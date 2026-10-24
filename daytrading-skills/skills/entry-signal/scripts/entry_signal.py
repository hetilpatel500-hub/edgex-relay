#!/usr/bin/env python3
"""Entry signal: check (or keep watching) a stock for an entry trigger.

Examples
  entry_signal.py --symbol AMD                       # one check on 1m bars
  entry_signal.py --symbol AMD --side long --only orb,vwap
  entry_signal.py --symbol AMD --watch 60 --until 11:30   # re-check every 60s, print new triggers
  entry_signal.py --symbol MESZ6 --source relay --watch 30
Alerts only: this script never places orders.
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse
    import time as _time

    from tradekit import signals as sg
    from tradekit.data import add_data_args, bars_from_args, daily_for, infer_interval_minutes
    from tradekit.report import emit_json, table
    from tradekit.session import Session, now_in, parse_hhmm

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", choices=["long", "short"], help="only show this direction")
    p.add_argument("--only", help=f"comma list of signal families: {','.join(sg.ALL)}")
    p.add_argument("--orb", type=int, default=15, help="opening-range minutes (default 15)")
    p.add_argument("--regime", help="market regime label from the market-regime skill, e.g. trend-up")
    p.add_argument("--min-quality", type=int, default=0)
    p.add_argument("--session", default="09:30-16:00")
    p.add_argument("--watch", type=int, metavar="SECONDS", help="poll every N seconds and print new triggers")
    p.add_argument("--until", help="stop watching at HH:MM exchange time (default: session close)")
    p.add_argument("--json", action="store_true")
    add_data_args(p, interval="1m", days=7)
    args = p.parse_args()

    sym = args.symbol.upper()
    session = Session.parse(args.session, args.tz)
    which = [w.strip() for w in args.only.split(",")] if args.only else None
    if which:
        bad = [w for w in which if w not in sg.ALL]
        if bad:
            raise ValueError(f"unknown signal family {bad}; choose from {list(sg.ALL)}")

    daily_cache = {}

    def check():
        intra = bars_from_args(args, sym)
        interval = infer_interval_minutes(intra)
        if "d" not in daily_cache:
            daily_cache["d"] = daily_for(args, sym, intra, session)
        ctx = sg.build_context(intra, session, interval, daily_cache["d"], regime=args.regime)
        sigs = [s for s in sg.evaluate(ctx, which, args.orb)
                if (not args.side or s.side == args.side) and s.quality >= args.min_quality]
        return ctx, sigs

    def show(ctx, sigs):
        last = ctx.last
        print(f"ENTRY SIGNALS · {sym} · {last.name:%Y-%m-%d %H:%M} · last {last['close']:.2f} · "
              f"VWAP {last['vwap']:.2f} · day volume {ctx.cum_rvol:.1f}x usual")
        rows = []
        for s in sigs:
            rows.append([s.status.upper(), s.side, s.name, f"{s.trigger:.2f}", f"{s.stop:.2f}",
                         f"{s.risk:.2f}", s.when or "", s.quality])
        if rows:
            print(table(rows, ["status", "side", "signal", "trigger", "stop", "risk", "at", "quality"], "lllrrrlr"))
        else:
            print("No setups match right now.")
        best = next((s for s in sigs if s.status in ("triggered", "armed") and s.quality >= 50), None)
        for s in sigs:
            if s.status in ("triggered", "armed"):
                print(f"\n• {s.name} {s.side} [{s.status}, quality {s.quality}] {s.description}")
                for r in s.reasons:
                    print(f"    + {r}")
                for w in s.warnings:
                    print(f"    - {w}")
        if best:
            print(f"\nBest candidate: {best.name} {best.side} — trigger {best.trigger:.2f}, stop {best.stop:.2f} "
                  f"(risk {best.risk:.2f}/share). Size it with position-sizer and stress it with time-machine.")

    if not args.watch:
        ctx, sigs = check()
        if args.json:
            emit_json({"symbol": sym, "as_of": ctx.last.name, "last": float(ctx.last["close"]),
                       "vwap": float(ctx.last["vwap"]), "day_rvol": ctx.cum_rvol,
                       "signals": [s.to_dict() for s in sigs]})
        else:
            show(ctx, sigs)
        return 0

    until = parse_hhmm(args.until) if args.until else session.end
    seen = set()
    print(f"watching {sym} every {args.watch}s until {until:%H:%M} (Ctrl-C to stop)", flush=True)
    while True:
        try:
            ctx, sigs = check()
        except Exception as exc:  # keep watching through transient data errors
            print(f"[{now_in(args.tz):%H:%M:%S}] data error: {exc}", flush=True)
        else:
            for s in sigs:
                key = (s.name, s.side, s.status, s.when)
                if s.status == "triggered" and key not in seen:
                    seen.add(key)
                    print(f"[{now_in(args.tz):%H:%M:%S}] TRIGGER {sym} {s.name} {s.side} @ {s.trigger:.2f} "
                          f"stop {s.stop:.2f} risk {s.risk:.2f} quality {s.quality} — {s.description}", flush=True)
        if now_in(args.tz).time() >= until:
            print("watch window over", flush=True)
            return 0
        _time.sleep(args.watch)


if __name__ == "__main__":
    run(main)
