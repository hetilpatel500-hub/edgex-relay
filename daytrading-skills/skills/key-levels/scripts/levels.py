#!/usr/bin/env python3
"""Key levels: the support/resistance ladder around the current price.

Examples
  levels.py --symbol NVDA
  levels.py --symbol SPY --orb 5 --json
  levels.py --symbol MESZ6 --source relay --session 09:30-16:00
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse

    from tradekit import levels as lv
    from tradekit.data import add_data_args, bars_from_args, daily_for
    from tradekit.report import emit_json, table
    from tradekit.session import Session

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", required=True)
    p.add_argument("--price", type=float, help="reference price (default: last trade)")
    p.add_argument("--orb", type=int, default=15, help="opening-range minutes (default 15)")
    p.add_argument("--profile-days", type=int, default=5, help="sessions in the volume profile (default 5)")
    p.add_argument("--count", type=int, default=6, help="levels to show on each side")
    p.add_argument("--session", default="09:30-16:00")
    p.add_argument("--json", action="store_true")
    add_data_args(p, interval="5m", days=30)
    args = p.parse_args()

    sym = args.symbol.upper()
    session = Session.parse(args.session, args.tz)
    intra = bars_from_args(args, sym, prepost=True)
    daily = daily_for(args, sym, intra, session)
    today = intra.index[-1].date()
    levels, ctx = lv.collect(intra, daily, session, today, args.orb, args.profile_days)
    price = args.price or ctx["last"]
    atr = ctx.get("daily_atr")
    lad = lv.ladder(levels, price, atr, args.count, args.count)

    def row(level):
        dist = level.price - price
        return [f"{level.price:.2f}", f"{dist / price:+.2%}", f"{dist / atr:+.2f}" if atr else "-",
                "★" * level.strength, level.label + (f"  (+{', '.join(level.tags)})" if level.tags else "")]

    if args.json:
        conv = lambda L: [dict(price=x.price, kind=x.kind, label=x.label, strength=x.strength,  # noqa: E731
                               confluence=x.tags, distance_pct=(x.price - price) / price) for x in L]
        emit_json({"symbol": sym, "price": price, "as_of": ctx.get("last_time"), "daily_atr": atr,
                   "resistance": conv(lad["resistance"]), "support": conv(lad["support"])})
        return 0

    print(f"KEY LEVELS · {sym} · last {price:.2f} as of {ctx.get('last_time')}"
          + (f" · daily ATR {atr:.2f} ({atr / price:.1%})" if atr else ""))
    print()
    print("RESISTANCE (nearest last)")
    print(table([row(x) for x in lad["resistance"][::-1]], ["price", "away", "ATRs", "str", "level"], "rrrll"))
    print(f"\n  ── {price:.2f} last ──\n")
    print("SUPPORT (nearest first)")
    print(table([row(x) for x in lad["support"]], ["price", "away", "ATRs", "str", "level"], "rrrll"))
    r = lad["resistance"][0] if lad["resistance"] else None
    s = lad["support"][0] if lad["support"] else None
    if r and s:
        print(f"\nRoom to move: {r.price - price:+.2f} to {r.kind} overhead, {s.price - price:+.2f} to {s.kind} below "
              f"(reward:risk {abs(r.price - price) / max(1e-9, abs(price - s.price)):.1f} long from here)")
    return 0


if __name__ == "__main__":
    run(main)
