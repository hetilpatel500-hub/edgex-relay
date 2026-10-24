#!/usr/bin/env python3
"""Chart scanner: sweep hundreds or thousands of daily charts for trade setups.

Examples
  scan.py                                   # bundled liquid list (~200 names)
  scan.py --universe us-all --top 40        # every US-listed common stock (~6,000)
  scan.py --tickers AAPL,TSLA,NVDA --setups breakout,bull-flag
  scan.py --universe my_watchlist.txt --min-dollar-volume 20e6 --json > scan.json
  scan.py --source demo                     # fake data, to see the output
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse

    from tradekit import scanner as sc
    from tradekit.cli import parse_symbols
    from tradekit.data import DataError, fetch_yfinance_many, get_bars, resolve_source, synthetic_daily
    from tradekit.report import emit_json, pct, table, warn

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--universe", default="liquid",
                   help=f"file of tickers, 'us-all', or a bundled list: {', '.join(sc.builtin_universes())}")
    p.add_argument("--tickers", help="comma list instead of a universe")
    p.add_argument("--setups", help=f"only these: {','.join(sc.SETUPS)}")
    p.add_argument("--direction", choices=["long", "short"])
    p.add_argument("--benchmark", default="SPY", help="for relative strength (default SPY)")
    p.add_argument("--min-price", type=float, default=2.0)
    p.add_argument("--max-price", type=float)
    p.add_argument("--min-dollar-volume", type=float, default=5e6, help="20-day average $ volume (default 5e6)")
    p.add_argument("--min-atr-pct", type=float, default=0.0, help="minimum daily ATR as %% of price")
    p.add_argument("--gap-pct", type=float, default=3.0)
    p.add_argument("--top", type=int, default=25)
    p.add_argument("--source", choices=["auto", "csv", "yfinance", "alpaca", "demo"], default="auto")
    p.add_argument("--csv-dir", help="directory of <SYMBOL>.csv daily files")
    p.add_argument("--tz", default="America/New_York")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    symbols = sc.resolve_universe(args.universe, parse_symbols(args.tickers))
    setups = [s.strip() for s in args.setups.split(",")] if args.setups else None
    if setups:
        bad = [s for s in setups if s not in sc.SETUPS]
        if bad:
            raise ValueError(f"unknown setups {bad}; choose from {sc.SETUPS}")
    src = resolve_source(args.source, None, args.csv_dir)
    bench_sym = args.benchmark.upper()

    def progress(i, n):
        print(f"  fetched {i}/{n}…", file=sys.stderr, flush=True)

    data = {}
    if src == "yfinance":
        print(f"downloading daily bars for {len(symbols)} tickers…", file=sys.stderr, flush=True)
        data = fetch_yfinance_many(list(dict.fromkeys(symbols + [bench_sym])), days=420, tz=args.tz,
                                   progress=progress)
    elif src == "demo":
        data = {s: synthetic_daily(s, 300, tz=args.tz) for s in symbols + [bench_sym]}
    else:
        failed = 0
        for i, s in enumerate(dict.fromkeys(symbols + [bench_sym])):
            try:
                data[s] = get_bars(s, src, "1d", 420, csv_dir=args.csv_dir, tz=args.tz)
            except DataError:
                failed += 1
            if i and i % 100 == 0:
                progress(i, len(symbols))
        if failed:
            warn(f"{failed} tickers had no data")
    bench = data.pop(bench_sym, None) if bench_sym not in symbols else data.get(bench_sym)
    if not data:
        raise DataError("no daily bars came back for any ticker")

    filters = sc.Filters(args.min_price, args.max_price, args.min_dollar_volume, args.min_atr_pct)
    rows, stats = sc.scan(data, filters, setups, bench, {"gap_pct": args.gap_pct})
    if args.direction:
        rows = [r for r in rows if r["direction"] in (args.direction, "either")]
    rows = rows[: args.top]

    if args.json:
        emit_json({"universe": args.universe if not args.tickers else "custom", "source": src, **stats,
                   "results": rows})
        return 0
    as_of = max(df.index[-1] for df in data.values())
    partial = any(r["partial_day"] for r in rows)
    print(f"CHART SCAN · {stats['scanned']} charts · {stats['passed_filters']} passed liquidity/price filters · "
          f"{len(rows)} shown · data through {as_of:%Y-%m-%d}" + (" (today is still trading)" if partial else ""))
    if not rows:
        print("No setups found with these filters.")
        return 0
    out = [[r["symbol"], f"{r['score']:.0f}", r["direction"], f"{r['close']:.2f}", pct(r["change"], 1, True),
            f"{r['rvol']:.1f}x", pct(r["atr_pct"], 1), ", ".join(r["setups"])] for r in rows]
    print(table(out, ["sym", "score", "dir", "last", "chg", "rvol", "ATR%", "setups"], "lrlrrrrl"))
    print()
    for r in rows[: min(10, len(rows))]:
        print(f"• {r['symbol']}: {r['why']}")
    if partial:
        print("\nnote: today's volume is projected to the full session with a typical intraday volume curve")
    return 0


if __name__ == "__main__":
    run(main)
