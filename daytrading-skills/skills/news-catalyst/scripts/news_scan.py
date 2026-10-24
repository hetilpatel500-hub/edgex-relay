#!/usr/bin/env python3
"""News catalyst scan: pull fresh headlines for tickers, classify the catalyst, rank by impact.

Examples
  news_scan.py --tickers NVDA,AMD,SMCI
  news_scan.py --tickers-file watchlist.txt --hours 12 --wires
  news_scan.py --wires-only --hours 2              # every ticker mentioned on the press wires
  news_scan.py --input headlines.json              # rank headlines gathered some other way
Sources: Yahoo Finance RSS, SEC EDGAR 8-K filings, GlobeNewswire and PR Newswire.
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse
    from concurrent.futures import ThreadPoolExecutor

    from tradekit import news as nw
    from tradekit.cli import parse_symbols
    from tradekit.report import emit_json, warn
    from tradekit.scanner import read_symbol_file

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tickers", help="comma list")
    p.add_argument("--tickers-file", help="file of tickers (e.g. the scanner's output list)")
    p.add_argument("--hours", type=float, default=24, help="look-back window (default 24)")
    p.add_argument("--wires", action="store_true", help="also scan press-release wires for these tickers")
    p.add_argument("--wires-only", action="store_true", help="only the wires, any ticker")
    p.add_argument("--no-sec", action="store_true", help="skip SEC EDGAR")
    p.add_argument("--input", help="JSON list of {ticker,title,published,source,link} to classify")
    p.add_argument("--min-score", type=float, default=0)
    p.add_argument("--per-ticker", type=int, default=5)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    tickers = parse_symbols(args.tickers)
    if args.tickers_file:
        tickers += [t for t in read_symbol_file(Path(args.tickers_file).expanduser()) if t not in tickers]
    if not (tickers or args.wires_only or args.input):
        raise ValueError("pass --tickers, --tickers-file, --wires-only or --input")

    items, errors = [], []
    if args.input:
        items += nw.load_items(args.input)
    if tickers and not args.wires_only:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for got, errs in pool.map(lambda t: nw.fetch_ticker(t, sec=not args.no_sec), tickers):
                items += got
                errors += errs
    if args.wires or args.wires_only:
        got, errs = nw.fetch_wires(None if args.wires_only else tickers)
        items += got
        errors += errs

    ranked = [i for i in nw.rank(items, args.hours) if i.score >= args.min_score]
    if errors:
        warn(f"{len(errors)} feed requests failed (first: {errors[0]})")
        if not ranked:
            warn("no feed was reachable: fall back to a web search for each ticker's news")

    if args.json:
        emit_json({"window_hours": args.hours, "errors": errors, "items": [i.to_dict() for i in ranked]})
        return 0

    by_ticker = {}
    for it in ranked:
        by_ticker.setdefault(it.ticker or "?", []).append(it)
    order = sorted(by_ticker, key=lambda t: -by_ticker[t][0].score)
    print(f"NEWS CATALYSTS · last {args.hours:g}h · {len(ranked)} unique headlines across {len(order)} tickers")
    if not ranked:
        print("Nothing found in the window.")
        return 0
    arrow = {1: "▲", -1: "▼", 0: "•"}
    for t in order:
        top = by_ticker[t][0]
        print(f"\n{t}  top catalyst: {top.catalyst} {arrow[top.direction]} (score {top.score:.0f})")
        for it in by_ticker[t][: args.per_ticker]:
            dup = f" (+{it.duplicates} similar)" if it.duplicates else ""
            print(f"  {nw.ago(it.age_hours):>4} {arrow[it.direction]} [{it.catalyst}] {it.title}{dup}")
            print(f"       {it.source}{' · ' + it.link if it.link else ''}")
    unclear = [t for t in order if by_ticker[t][0].direction == 0 and by_ticker[t][0].impact >= 3]
    if unclear:
        print(f"\nRead the source before trading: direction unclear for {', '.join(unclear)}")
    return 0


if __name__ == "__main__":
    run(main)
