#!/usr/bin/env python3
"""Trade journal: log trades and find out what actually makes you money.

Examples
  journal.py add --symbol AAPL --side long --entry 187.5 --exit 189.9 --shares 200 --stop 186.2 \\
                 --setup ORB --entry-time "2026-10-23 09:52" --exit-time "2026-10-23 10:40"
  journal.py open --symbol NVDA --side short --entry 131.2 --shares 100 --stop 132.0 --setup "VWAP rejection"
  journal.py close --id 3f9a1c2e --exit 129.8
  journal.py list --open
  journal.py stats --since 2026-09-01
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse

    import pandas as pd

    from tradekit import journal as jr
    from tradekit.report import emit_json, money, pct, table
    from tradekit.session import now_in

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--journal", help="CSV path (default ~/.daytrading-skills/journal.csv)")
    p.add_argument("--tz", default="America/New_York")
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def trade_args(sp, closed: bool):
        sp.add_argument("--symbol", required=True)
        sp.add_argument("--side", choices=["long", "short"], required=True)
        sp.add_argument("--entry", type=float, required=True)
        sp.add_argument("--shares", type=float, required=True)
        sp.add_argument("--stop", type=float, help="initial stop (needed for R multiples)")
        sp.add_argument("--target", type=float)
        sp.add_argument("--entry-time", help="YYYY-MM-DD HH:MM (default now)")
        if closed:
            sp.add_argument("--exit", type=float, required=True)
            sp.add_argument("--exit-time", help="default now")
        sp.add_argument("--fees", type=float, default=0.0)
        sp.add_argument("--point-value", type=float, default=1.0, help="futures: dollars per point")
        sp.add_argument("--setup", default="", help="e.g. ORB, VWAP reclaim, pullback")
        sp.add_argument("--tags", default="", help="comma list, e.g. a+,news,chased")
        sp.add_argument("--notes", default="")
        sp.add_argument("--predicted-win", type=float, help="time-machine 'made money' odds, 0-1")
        sp.add_argument("--predicted-r", type=float, help="time-machine average R")

    trade_args(sub.add_parser("add", help="log a finished trade"), closed=True)
    trade_args(sub.add_parser("open", help="log a trade you are in now"), closed=False)
    c = sub.add_parser("close", help="close an open trade")
    c.add_argument("--id", required=True)
    c.add_argument("--exit", type=float, required=True)
    c.add_argument("--exit-time")
    c.add_argument("--fees", type=float)
    c.add_argument("--notes")
    ls = sub.add_parser("list", help="show trades")
    ls.add_argument("--open", action="store_true")
    ls.add_argument("--last", type=int, default=20)
    st = sub.add_parser("stats", help="performance breakdown")
    st.add_argument("--since")
    st.add_argument("--setup")
    st.add_argument("--symbol")
    args = p.parse_args()

    path = Path(args.journal).expanduser() if args.journal else jr.default_path()
    now = now_in(args.tz).tz_localize(None).strftime("%Y-%m-%d %H:%M")

    if args.cmd in ("add", "open"):
        fields = dict(symbol=args.symbol.upper(), side=args.side, entry=args.entry, shares=args.shares,
                      stop=args.stop, target=args.target, entry_time=args.entry_time or now, fees=args.fees,
                      point_value=args.point_value, setup=args.setup, tags=args.tags, notes=args.notes,
                      predicted_win=args.predicted_win, predicted_r=args.predicted_r)
        if args.cmd == "add":
            fields.update(exit=args.exit, exit_time=args.exit_time or now)
        tid = jr.add(path, tz=args.tz, **fields)
        row = jr.load(path).set_index("id").loc[tid]
        msg = f"logged {tid}: {row['symbol']} {row['side']} {row['shares']:g} @ {row['entry']:g}"
        if args.cmd == "add":
            msg += f" → {row['exit']:g} = {money(row['pnl'])}"
            if pd.notna(row["r"]):
                msg += f" ({row['r']:+.2f}R)"
        print(msg)
        if args.stop is None:
            print("  tip: pass --stop next time so the journal can measure results in R")
        print(f"  journal: {path}")
        return 0

    if args.cmd == "close":
        jr.close(path, args.id, args.exit, args.exit_time or now, args.fees, args.notes, tz=args.tz)
        row = jr.load(path).set_index("id").loc[args.id]
        print(f"closed {args.id}: {row['symbol']} {money(row['pnl'])}"
              + (f" ({row['r']:+.2f}R)" if pd.notna(row["r"]) else ""))
        return 0

    df = jr.load(path)
    if args.cmd == "list":
        view = df[df["status"] == "open"] if args.open else df
        view = view.sort_values("entry_time").tail(args.last)
        if args.json:
            emit_json(view.to_dict(orient="records"))
            return 0
        if len(view) == 0:
            print(f"no {'open ' if args.open else ''}trades in {path}")
            return 0
        rows = [[r["id"], f"{r['entry_time']:%m-%d %H:%M}" if pd.notna(r["entry_time"]) else "", r["symbol"],
                 r["side"], f"{r['shares']:g}", f"{r['entry']:g}", "" if pd.isna(r["exit"]) else f"{r['exit']:g}",
                 "" if pd.isna(r["pnl"]) else money(r["pnl"]), "" if pd.isna(r["r"]) else f"{r['r']:+.2f}",
                 r["setup"]] for _, r in view.iterrows()]
        print(table(rows, ["id", "entered", "sym", "side", "size", "entry", "exit", "P&L", "R", "setup"],
                    "llllrrrrrl"))
        return 0

    s = jr.stats(df, args.since, args.setup, args.symbol)
    if args.json:
        emit_json(s)
        return 0
    o = s["overall"]
    if not o["trades"]:
        print(f"no closed trades yet in {path}")
        return 0
    print(f"JOURNAL STATS · {o['trades']} closed trades" + (f" since {args.since}" if args.since else ""))
    print(f"  Net P&L {money(o['total_pnl'])} · win rate {pct(o['win_rate'])} · avg win {money(o['avg_win'])} · "
          f"avg loss {money(o['avg_loss'])}")
    pf = f"{o['profit_factor']:.2f}" if o["profit_factor"] else "-"
    er = f"{o['expectancy_r']:+.2f}R" if o["expectancy_r"] is not None else "- (log stops to get R)"
    print(f"  Profit factor {pf} · expectancy {er} per trade · max drawdown {money(o['max_drawdown'])}")
    print(f"  Best {money(o['best'])} · worst {money(o['worst'])} · longest losing streak "
          f"{o['longest_loss_streak']}" + (f" · avg hold {o['avg_hold_min']:.0f} min" if o["avg_hold_min"] else ""))

    def section(title, data, limit=8):
        items = sorted(data.items(), key=lambda kv: -kv[1]["total_pnl"])[:limit]
        if not items:
            return
        print(f"\n{title}")
        rows = [[k, b["trades"], pct(b["win_rate"], 0), money(b["total_pnl"]),
                 f"{b['expectancy_r']:+.2f}R" if b.get("expectancy_r") is not None else "-"] for k, b in items]
        print(table(rows, ["", "trades", "win", "P&L", "avg R"], "lrrrr"))

    section("BY SETUP", s["by_setup"])
    section("BY HOUR OF ENTRY", {f"{int(k):02d}:00" if k != "-1" else "?": v for k, v in s["by_hour"].items()})
    section("BY SIDE", s["by_side"])
    section("BY TAG", s["by_tag"])
    if "calibration" in s:
        cal = s["calibration"]
        print(f"\nTIME MACHINE CALIBRATION · {cal['trades']} trades with predicted odds · Brier "
              f"{cal['brier']:.3f} (coin flip 0.250, lower is better)")
        for b, v in cal["bins"].items():
            print(f"  predicted {b}: said {v['predicted']:.0%}, actually won {v['actual']:.0%} ({v['trades']} trades)")
    if s.get("insights"):
        print("\nWHAT THE NUMBERS SAY")
        for t in s["insights"]:
            print(f"  - {t}")
    return 0


if __name__ == "__main__":
    run(main)
