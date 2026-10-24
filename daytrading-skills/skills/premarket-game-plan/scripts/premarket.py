#!/usr/bin/env python3
"""Premarket game plan: rank today's gappers and write if-then plans around their levels.

Examples
  premarket.py --tickers NVDA,TSLA,PLTR,SMCI
  premarket.py --from-scan scan.json --news news.json      # chain the scanner and news skills
  premarket.py --tickers-file watchlist.txt --top 8 --json
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def main():
    import argparse
    import json

    import numpy as np

    from tradekit import indicators as ind, levels as lv
    from tradekit.cli import parse_symbols
    from tradekit.data import DataError, add_data_args, bars_from_args, daily_for
    from tradekit.report import emit_json, pct, table, warn
    from tradekit.scanner import read_symbol_file
    from tradekit.session import Session, premarket as pm_bars, rth, split_days

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--tickers")
    p.add_argument("--tickers-file")
    p.add_argument("--from-scan", help="JSON written by chart-scanner --json")
    p.add_argument("--news", help="JSON written by news-catalyst --json")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--session", default="09:30-16:00")
    p.add_argument("--json", action="store_true")
    add_data_args(p, interval="5m", days=30, single=False)
    args = p.parse_args()

    tickers = parse_symbols(args.tickers)
    if args.tickers_file:
        tickers += read_symbol_file(Path(args.tickers_file).expanduser())
    if args.from_scan:
        tickers += [r["symbol"] for r in json.loads(Path(args.from_scan).expanduser().read_text())["results"]]
    tickers = list(dict.fromkeys(tickers))
    if not tickers:
        raise ValueError("pass --tickers, --tickers-file or --from-scan")
    news = {}
    if args.news:
        for it in json.loads(Path(args.news).expanduser().read_text())["items"]:
            news.setdefault(it["ticker"], it)  # items are already sorted best-first
    session = Session.parse(args.session, args.tz)

    rows, plans = [], []
    for sym in tickers:
        try:
            intra = bars_from_args(args, sym, prepost=True)
        except DataError as exc:
            warn(f"{sym}: {exc}")
            continue
        daily = daily_for(args, sym, intra, session)
        today = intra.index[-1].date()
        done = daily[daily.index.date < today]
        if len(done) < 15:
            warn(f"{sym}: not enough daily history")
            continue
        prior = done.iloc[-1]
        atr = float(ind.atr(done, 14).iloc[-1])
        day = intra[intra.index.date == today]
        pre = pm_bars(day, session)
        reg = rth(day, session)
        last = float(day["close"].iloc[-1])
        gap = last / float(prior["close"]) - 1
        pm_vol = float(pre["volume"].sum())
        # premarket volume vs the same window on prior days
        hist_pm = []
        cutoff = pre.index[-1].time() if len(pre) else None
        for d, g in split_days(pm_bars(intra, session)).items():
            if d < today and cutoff is not None:
                hist_pm.append(float(g[g.index.time <= cutoff]["volume"].sum()))
        pm_rvol = pm_vol / np.mean(hist_pm) if hist_pm and np.mean(hist_pm) > 0 else float("nan")
        levels, ctx = lv.collect(intra, daily, session, today)
        lad = lv.ladder(levels, last, atr, 2, 2)
        cat = news.get(sym)
        score = min(40, abs(gap) * float(prior["close"]) / atr * 20) \
            + (min(30, pm_rvol * 6) if not np.isnan(pm_rvol) else 0) \
            + ((20 if cat["impact"] >= 4 else 10 if cat["impact"] >= 3 else 0) if cat else 0)
        pmh = float(pre["high"].max()) if len(pre) else None
        pml = float(pre["low"].min()) if len(pre) else None
        row = {
            "symbol": sym, "score": round(score, 1), "last": last, "prior_close": float(prior["close"]),
            "gap": gap, "gap_atr": gap * float(prior["close"]) / atr, "pm_volume": pm_vol, "pm_rvol": pm_rvol,
            "pmh": pmh, "pml": pml, "pdh": float(prior["high"]), "pdl": float(prior["low"]), "daily_atr": atr,
            "market_open": len(reg) > 0, "catalyst": cat["catalyst"] if cat else None,
            "headline": cat["title"] if cat else None,
            "resistance": [(x.price, x.label) for x in lad["resistance"]],
            "support": [(x.price, x.label) for x in lad["support"]],
        }
        trig_long, trig_short = pmh or row["pdh"], pml or row["pdl"]
        merged = lv.merge(levels, 0.05 * atr)

        def target(trig, d):
            nxt = lv.nearest(merged, trig, d, min_dist=0.15 * atr, min_strength=2)
            if nxt and abs(nxt.price - trig) <= atr:
                return nxt.price, nxt.label
            far = f"; next level {nxt.label} {nxt.price:.2f} is over an ATR away" if nxt else ""
            return trig + d * 0.5 * atr, "half a daily ATR" + far

        row["long_trigger"], row["short_trigger"] = trig_long, trig_short
        row["long_target"], row["short_target"] = target(trig_long, 1), target(trig_short, -1)
        rows.append(row)

    rows.sort(key=lambda r: -r["score"])
    rows = rows[: args.top]
    for r in rows:
        r["tier"] = "A" if r["score"] >= 55 else "B" if r["score"] >= 35 else "C"
        up = r["gap"] >= 0
        lt, st_ = r["long_trigger"], r["short_trigger"]
        r["plan"] = [
            f"Long over {lt:.2f} ({'premarket high' if r['pmh'] else 'prior day high'}), stop under "
            f"{max(st_, lt - 0.35 * r['daily_atr']):.2f}, first target {r['long_target'][0]:.2f} "
            f"({r['long_target'][1]})",
            f"Short under {st_:.2f} ({'premarket low' if r['pml'] else 'prior day low'}), stop over "
            f"{min(lt, st_ + 0.35 * r['daily_atr']):.2f}, first target {r['short_target'][0]:.2f} "
            f"({r['short_target'][1]})",
            f"{'Gap-fill' if up else 'Gap-fill rally'} target if it fades: prior close {r['prior_close']:.2f}",
        ]
        if abs(r["gap_atr"]) > 1.5:
            r["plan"].append("gap is more than 1.5 daily ATRs: expect a wide, fast open; wait for the opening range")

    if args.json:
        emit_json({"tickers": len(tickers), "results": rows})
        return 0
    if not rows:
        print("No tickers with usable data.")
        return 0
    print(f"PREMARKET GAME PLAN · {len(rows)} of {len(tickers)} tickers ranked"
          + (" · market already open" if rows[0]["market_open"] else ""))
    out = [[r["tier"], r["symbol"], f"{r['last']:.2f}", pct(r["gap"], 1, True), f"{r['gap_atr']:+.1f}",
            f"{r['pm_rvol']:.1f}x" if not np.isnan(r["pm_rvol"]) else "-",
            f"{r['pmh']:.2f}" if r["pmh"] else "-", f"{r['pml']:.2f}" if r["pml"] else "-",
            r["catalyst"] or ""] for r in rows]
    print(table(out, ["tier", "sym", "last", "gap", "ATRs", "PM vol", "PMH", "PML", "catalyst"], "llrrrrrrl"))
    for r in rows:
        if r["tier"] == "C":
            continue
        print(f"\n{r['tier']} · {r['symbol']} {pct(r['gap'], 1, True)}"
              + (f" — {r['headline']}" if r["headline"] else ""))
        for line in r["plan"]:
            print(f"   • {line}")
    print("\nTier A = in play (big gap for its ATR, heavy premarket volume, real catalyst). "
          "Tier C rows are listed but not planned.")
    return 0


if __name__ == "__main__":
    run(main)
