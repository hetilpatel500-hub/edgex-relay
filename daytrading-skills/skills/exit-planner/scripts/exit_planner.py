#!/usr/bin/env python3
"""Exit planner: stop, profit targets, scale-outs, trailing and time stops for one trade.

Examples
  exit_planner.py --symbol AAPL --side long --entry 187.50
  exit_planner.py --symbol AAPL --side long --entry 187.50 --stop 186.20 --style thirds
  exit_planner.py --symbol TSLA --side short --style single --first-r 2.5 --emit-plan plan.json
  (then: time_machine.py --plan plan.json)
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse
    import json

    from tradekit import exits, indicators as ind, levels as lv
    from tradekit.data import add_data_args, bars_from_args, daily_for
    from tradekit.report import emit_json, money, table
    from tradekit.session import Session, rth

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", required=True)
    p.add_argument("--side", choices=["long", "short"], required=True)
    p.add_argument("--entry", type=float, help="entry price (default: last trade)")
    p.add_argument("--stop", type=float, help="your stop; omitted = pick one from structure/volatility")
    p.add_argument("--style", choices=list(exits.STYLES), default="scale",
                   help="scale: 50%% at T1, 25%% at T2, 25%% runner · thirds · single · runner")
    p.add_argument("--first-r", type=float, help="R multiple for the first (or only) target")
    p.add_argument("--trail-r", type=float, default=1.0, help="runner trailing distance in R (default 1)")
    p.add_argument("--time-stop", type=int, default=45, help="minutes to reach +0.5R before bailing (0 = off)")
    p.add_argument("--flat-by", default="15:55")
    p.add_argument("--shares", type=float, help="show dollar amounts for this size")
    p.add_argument("--session", default="09:30-16:00")
    p.add_argument("--emit-plan", help="write a time-machine plan JSON here")
    p.add_argument("--json", action="store_true")
    add_data_args(p, interval="5m", days=30)
    args = p.parse_args()

    sym = args.symbol.upper()
    session = Session.parse(args.session, args.tz)
    intra = bars_from_args(args, sym, prepost=True)
    daily = daily_for(args, sym, intra, session)
    today = intra.index[-1].date()
    levels, ctx = lv.collect(intra, daily, session, today)
    entry = args.entry or ctx["last"]
    reg = rth(intra, session)
    day = reg[reg.index.date == today]
    bar_atr = float(ind.atr(reg, 14).iloc[-1]) if len(reg) > 14 else None
    plan = exits.plan_exits(
        args.side, entry, args.stop, levels, ctx.get("daily_atr"), bar_atr,
        float(day["high"].max()) if len(day) else None, float(day["low"].min()) if len(day) else None,
        style=args.style, first_r=args.first_r, trail_r=args.trail_r,
        time_stop_minutes=args.time_stop or None, flat_by=args.flat_by,
    )
    d = plan.to_dict()
    d["symbol"] = sym

    if args.emit_plan:
        tm = {"symbol": sym, "side": plan.side, "entry": round(plan.entry, 4), "stop": round(plan.stop, 4),
              "targets": [{"price": round(t["price"], 4), "fraction": t["fraction"]} for t in plan.targets],
              "breakeven_after": plan.breakeven_after or 0, "trail_r": plan.trail_r, "flat_by": plan.flat_by,
              "session": args.session}
        if args.shares:
            tm["shares"] = args.shares
        out = Path(args.emit_plan).expanduser()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(tm, indent=2) + "\n")

    if args.json:
        emit_json(d)
        return 0

    risk = plan.risk
    print(f"EXIT PLAN · {sym} {plan.side} @ {plan.entry:.2f}"
          + (f" · daily ATR {ctx['daily_atr']:.2f}" if ctx.get("daily_atr") else ""))
    print(f"\nSTOP {plan.stop:.2f} ({plan.stop_reason}) · risk {risk:.2f}/share"
          + (f" = {money(risk * args.shares)}" if args.shares else ""))
    alts = [c for c in plan.stop_options if abs(c["price"] - plan.stop) > 1e-3]
    if alts:
        print("  other stops considered: " + "; ".join(f"{c['price']:.2f} ({c['reason']})" for c in alts))
    rows = []
    for i, t in enumerate(plan.targets, 1):
        pnl = abs(t["price"] - plan.entry) * t["fraction"] * args.shares if args.shares else None
        rows.append([f"T{i}", f"{t['price']:.2f}", f"+{t['r']:.2f}R", f"{t['fraction']:.0%}",
                     money(pnl) if pnl else "", t["reason"] + (" (stretch)" if t.get("stretch") else "")])
    runner = 1 - sum(t["fraction"] for t in plan.targets)
    if runner > 1e-6:
        rows.append(["runner", "trail", f"{plan.trail_r:g}R trail", f"{runner:.0%}", "", "after T1, until flat-by"])
    print("\nTARGETS")
    print(table(rows, ["leg", "price", "reward", "size", "$", "why"], "lrrrrl"))
    print("\nMANAGEMENT RULES")
    if plan.breakeven_after:
        print(f"  1. When T{plan.breakeven_after} fills, move the stop to breakeven ({plan.entry:.2f}).")
    else:
        print("  1. Leave the stop where it is until the target or the flat-by time.")
    if plan.time_stop_minutes:
        print(f"  2. Time stop: not at +0.5R ({plan.entry + (1 if plan.side == 'long' else -1) * 0.5 * risk:.2f}) "
              f"within {plan.time_stop_minutes} minutes → get out; the idea did not work.")
    print(f"  3. Flat by {plan.flat_by}: no day trade becomes an overnight hold.")
    print("  4. Never widen the stop once the trade is on.")
    if plan.notes:
        print("\nNOTES")
        for n in plan.notes:
            print(f"  - {n}")
    if args.emit_plan:
        print(f"\nPlan saved for the time machine: {Path(args.emit_plan).expanduser().resolve()}")
    return 0


if __name__ == "__main__":
    run(main)
