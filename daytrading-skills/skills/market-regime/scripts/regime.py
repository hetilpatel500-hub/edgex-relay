#!/usr/bin/env python3
"""Market regime: trending, ranging or volatile, and what that means for today's playbook.

Examples
  regime.py                         # SPY, QQQ, IWM + VIX
  regime.py --breadth               # add % of the liquid list above its 20 EMA (slower)
  regime.py --intraday              # add an early read on today's tape from SPY 5m bars
  regime.py --indexes SPY --json
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse

    from tradekit import regime as rg
    from tradekit.cli import parse_symbols
    from tradekit.data import DataError, fetch_yfinance_many, get_bars, resolve_source, synthetic_daily
    from tradekit.report import emit_json, pct, table, warn
    from tradekit.scanner import resolve_universe
    from tradekit.session import Session, rth

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--indexes", default="SPY,QQQ,IWM")
    p.add_argument("--vix", default="^VIX", help="volatility index ticker (Yahoo); 'none' to skip")
    p.add_argument("--breadth", action="store_true", help="measure breadth on the liquid universe")
    p.add_argument("--universe", default="liquid", help="universe for --breadth")
    p.add_argument("--intraday", action="store_true", help="read today's tape from the first index's 5m bars")
    p.add_argument("--source", choices=["auto", "csv", "yfinance", "alpaca", "demo"], default="auto")
    p.add_argument("--csv-dir", help="directory of <SYMBOL>.csv daily files")
    p.add_argument("--tz", default="America/New_York")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    src = resolve_source(args.source, None, args.csv_dir)
    idx = parse_symbols(args.indexes)

    def daily(sym):
        if src == "demo":
            return synthetic_daily(sym, 300, tz=args.tz)
        return get_bars(sym, src, "1d", 420, csv_dir=args.csv_dir, tz=args.tz)

    data = {s: daily(s) for s in idx}
    vix = None
    if args.vix.lower() != "none" and src in ("yfinance", "demo"):
        try:
            vix = daily(args.vix) if src == "yfinance" else None
        except DataError as exc:
            warn(f"VIX unavailable: {exc}")
    breadth = None
    if args.breadth:
        syms = resolve_universe(args.universe)
        if src == "yfinance":
            uni = fetch_yfinance_many(syms, days=90, tz=args.tz)
        elif src == "demo":
            uni = {s: synthetic_daily(s, 80, tz=args.tz) for s in syms}
        else:
            uni = {}
            for s in syms:
                try:
                    uni[s] = get_bars(s, src, "1d", 90, csv_dir=args.csv_dir, tz=args.tz)
                except DataError:
                    pass
        breadth = rg.breadth_above_ema20(uni)
    intraday = None
    if args.intraday:
        session = Session(tz=args.tz)
        bars = rth(get_bars(idx[0], src, "5m", 5, csv_dir=args.csv_dir, tz=args.tz), session)
        if len(bars):
            intraday = bars[bars.index.date == bars.index[-1].date()]

    res = rg.classify(data, vix, breadth, intraday)
    if args.json:
        emit_json(res)
        return 0
    pb = res["playbook"]
    print(f"MARKET REGIME · {res['label'].upper()} · suggested size {pb['size']:.0%} of normal")
    for r in res["reasons"]:
        print(f"  - {r}")
    rows = [[s, f"{v['close']:.2f}", pct(v["ret5"], 1, True), pct(v["ret20"], 1, True), pct(v["vs_ema20"], 1, True),
             f"{v['trend_score']:+d}", f"{v['efficiency_10d']:.2f}", pct(v["atr_pct"], 2)]
            for s, v in res["indexes"].items()]
    print()
    print(table(rows, ["index", "last", "5d", "20d", "vs 20EMA", "trend", "eff", "ATR%"], "lrrrrrrr"))
    if "today" in res:
        t = res["today"]
        print(f"\nTODAY ({idx[0]}): {t['read']} · {t['share_of_bars_above_vwap']:.0%} of bars above VWAP · "
              f"{t['vwap_crosses']} VWAP crosses · efficiency {t['efficiency']:.2f}")
    print(f"\nPLAYBOOK: {pb['notes']}")
    print(f"  favor: {', '.join(pb['favor'])}")
    print(f"  avoid: {', '.join(pb['avoid'])}")
    print(f"\nPass this to entry-signal with --regime {res['label']}")
    return 0


if __name__ == "__main__":
    run(main)
