#!/usr/bin/env python3
"""Time Machine: simulate the rest of the trading day 10,000 times for one trade.

Examples
  time_machine.py --symbol AAPL --side long --entry 187.50 --stop 186.20 --target 190.10
  time_machine.py --symbol TSLA --side short --stop 251.4 --target 246,243 --split 50,50 --time 10:15
  time_machine.py --plan plan.json --html odds.html
  time_machine.py --source demo --symbol DEMO --side long --stop-pct 0.5 --rr 2   # fake data, try it out
"""

import sys
from pathlib import Path

_skill = Path(__file__).resolve().parents[1]  # engine is vendored in packaged skills, shared in the plugin
sys.path.insert(0, str(_skill / "lib" if (_skill / "lib").is_dir() else _skill.parents[1] / "lib"))

from tradekit.cli import run  # noqa: E402


def build_parser():
    import argparse

    from tradekit.data import add_data_args

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--symbol", help="ticker (used to fetch data and label the report)")
    p.add_argument("--plan", help="JSON trade plan, e.g. from the exit-planner skill")
    p.add_argument("--side", choices=["long", "short"])
    p.add_argument("--entry", type=float, help="fill price (default: last price at the entry time)")
    p.add_argument("--stop", type=float, help="stop-loss price")
    p.add_argument("--stop-pct", type=float, help="stop distance as a %% of price when --stop is not known, e.g. 0.5")
    p.add_argument("--target", help="target price(s), comma separated for scale-outs")
    p.add_argument("--split", help="percent sold at each target, e.g. 50,50 or 50,25 (rest = runner)")
    p.add_argument("--rr", type=float, help="put a single target at this reward:risk multiple instead")
    p.add_argument("--breakeven-after", type=int, help="move stop to entry after target N fills "
                   "(default 1 when there are several targets; 0 = never)")
    p.add_argument("--trail-r", type=float, help="trailing stop distance in R (starts after the first target)")
    p.add_argument("--slippage", type=float, default=None, help="price lost on stop/market exits (default 1 tick ~0.01)")
    p.add_argument("--shares", type=float, help="position size, to show dollar results")
    p.add_argument("--point-value", type=float, default=1.0, help="dollars per point per unit (futures: MES=5, ES=50)")
    p.add_argument("--date", help="session date YYYY-MM-DD (default: today)")
    p.add_argument("--time", help="entry time HH:MM exchange time (default: now / the latest bar)")
    p.add_argument("--flat-by", help="time exit HH:MM (default: session close)")
    p.add_argument("--session", default="09:30-16:00", help="regular session, exchange time")
    p.add_argument("--sims", type=int, default=10_000, help="number of simulated days (default 10000)")
    p.add_argument("--block", type=float, default=30, help="average bootstrap block length in minutes (default 30)")
    p.add_argument("--vol-scale", default="auto", help="'auto' (match today's volatility), 'none', or a multiplier")
    p.add_argument("--demean", action="store_true", help="remove the historical intraday drift")
    p.add_argument("--ambiguous", choices=["ohlc", "worst"], default="ohlc",
                   help="when one bar touches stop and target: OHLC path heuristic or worst case")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--no-robustness", action="store_true", help="skip the stress-test reruns")
    p.add_argument("--json", action="store_true", help="print machine-readable results")
    p.add_argument("--html", help="write a self-contained HTML report with charts to this path")
    add_data_args(p, interval="5m", days=60)
    return p


def load_plan(args):
    import json

    if not args.plan:
        return {}
    plan = json.loads(Path(args.plan).expanduser().read_text())
    return plan.get("plan", plan)


def main():
    import math

    import numpy as np
    import pandas as pd

    from tradekit import montecarlo as mc
    from tradekit.data import infer_interval_minutes, interval_minutes, resample
    from tradekit.report import bar, dots, emit_json, money, time_machine_html
    from tradekit.session import Session, at, now_in, parse_hhmm
    from tradekit.session import rth as rth_bars

    args = build_parser().parse_args()
    plan_file = load_plan(args)
    symbol = (args.symbol or plan_file.get("symbol") or ("DEMO" if args.source == "demo" else None))
    if not symbol and not args.csv:
        raise ValueError("pass --symbol (or --csv with your bars)")
    symbol = (symbol or Path(args.csv).stem).upper()
    side = args.side or plan_file.get("side")
    if side not in ("long", "short"):
        raise ValueError("pass --side long or --side short")
    session = Session.parse(args.session or plan_file.get("session"), args.tz)
    interval = interval_minutes(args.interval)

    from tradekit.data import bars_from_args

    demo_until = parse_hhmm(args.time) if args.source == "demo" and args.time else None
    bars = bars_from_args(args, symbol, demo_today_until=demo_until)
    native = infer_interval_minutes(bars)
    if native < interval:
        bars = resample(bars, interval, session.start_min)
    elif native > interval:
        interval = native

    now = now_in(args.tz)
    session_date = pd.Timestamp(args.date).date() if args.date else now.date()
    if args.source == "demo" and not args.date:
        session_date = bars.index[-1].date()
    day_bars = bars[bars.index.date == session_date]
    if args.time or plan_file.get("time"):
        entry_t = parse_hhmm(args.time or plan_file["time"])
    elif len(day_bars):
        last = day_bars.index[-1] + pd.Timedelta(minutes=interval)
        entry_t = last.time()
    else:
        raise ValueError(f"no bars for {session_date} yet (market closed?). Pass --time HH:MM to simulate "
                         "an entry at that time, and --date to pick the session.")
    entry_ts = at(session_date, entry_t, args.tz)
    minute = session.minute_of(entry_ts)
    if not 0 <= minute < session.minutes:
        raise ValueError(f"entry time {entry_t:%H:%M} is outside the {session.label()} session")

    # only bars that had finished by the entry time: a 10:02 entry cannot know the 10:00 bar's close
    before = day_bars[day_bars.index + pd.Timedelta(minutes=interval) <= entry_ts]
    entry = args.entry or plan_file.get("entry")
    if entry is None:
        if len(before) == 0:
            raise ValueError("no price before the entry time to use as the fill; pass --entry")
        entry = float(before["close"].iloc[-1])
    entry = float(entry)

    stop = args.stop if args.stop is not None else plan_file.get("stop")
    if stop is None and args.stop_pct:
        stop = entry * (1 - args.stop_pct / 100) if side == "long" else entry * (1 + args.stop_pct / 100)
    if stop is None:
        raise ValueError("pass --stop PRICE (or --stop-pct PERCENT)")
    stop = float(stop)
    risk = abs(entry - stop)
    sign = 1 if side == "long" else -1

    targets = []
    if args.target:
        prices = [float(x) for x in args.target.split(",") if x.strip()]
        if args.split:
            fracs = [float(x) / 100 for x in args.split.split(",")]
            if len(fracs) != len(prices):
                raise ValueError("--split needs one percentage per target")
        else:
            fracs = [1 / len(prices)] * len(prices)
        targets = [mc.Target(p, f) for p, f in zip(prices, fracs)]
    elif args.rr:
        targets = [mc.Target(entry + sign * args.rr * risk, 1.0)]
    elif plan_file.get("targets"):
        targets = [mc.Target(float(t["price"]), float(t.get("fraction", 1 / len(plan_file["targets"]))))
                   for t in plan_file["targets"]]

    be = args.breakeven_after if args.breakeven_after is not None else plan_file.get("breakeven_after")
    if be is None:
        be = 1 if len(targets) > 1 else 0
    slippage = args.slippage if args.slippage is not None else plan_file.get("slippage", 0.01)
    plan = mc.TradePlan(side, entry, stop, targets, breakeven_after=(be - 1) if be else None,
                        trail_r=args.trail_r or plan_file.get("trail_r"), slippage=float(slippage))

    flat_by = parse_hhmm(args.flat_by or plan_file.get("flat_by") or session.end.strftime("%H:%M"))
    start_slot = math.ceil(minute / interval)
    end_slot = session.minute_of(at(session_date, flat_by, args.tz)) // interval - 1
    end_slot = min(end_slot, session.n_slots(interval) - 1)
    if end_slot < start_slot:
        raise ValueError("no full bars left between the entry time and the flat-by time")

    bank_all = mc.build_bank(bars, session, interval)
    hist = bank_all.select(np.array([d < session_date for d in bank_all.days]))
    if hist.n_days < 5:
        raise ValueError(f"only {hist.n_days} prior sessions in the data; fetch more history (--days)")
    today_bars = bars[bars.index.date == session_date]
    today = mc.build_bank(today_bars, session, interval, min_coverage=0) if len(rth_bars(today_bars, session)) else None

    notes = []
    if args.vol_scale == "auto":
        vol_scale, vol_note = mc.auto_vol_scale(hist, today, minute // interval)
    elif args.vol_scale == "none":
        vol_scale, vol_note = 1.0, "volatility left at its historical level (--vol-scale none)"
    else:
        vol_scale = float(args.vol_scale)
        vol_note = f"volatility multiplied by {vol_scale:g} by request"

    block_bars = max(1.0, args.block / interval)
    common = dict(start_slot=start_slot, end_slot=end_slot, block_bars=block_bars, ambiguous=args.ambiguous)
    res = mc.simulate(hist, plan, n_sims=args.sims, vol_scale=vol_scale, demean=args.demean, seed=args.seed,
                      **common)
    summary = mc.summarize(res)
    replay = mc.summarize(mc.simulate(hist, plan, mode="replay", vol_scale=vol_scale, demean=args.demean,
                                      record_fan=False, **common))

    robustness = []
    if not args.no_robustness:
        variants = [
            ("drift removed" if not args.demean else "drift kept", dict(demean=not args.demean)),
            ("volatility +25%", dict(vol_scale=vol_scale * 1.25)),
            ("volatility -25%", dict(vol_scale=vol_scale * 0.75)),
        ]
        if args.ambiguous == "ohlc":
            variants.append(("worst-case fills", dict(ambiguous="worst")))
        for label, override in variants:
            kw = dict(common, vol_scale=vol_scale, demean=args.demean)
            kw.update(override)
            r = mc.summarize(mc.simulate(hist, plan, n_sims=min(args.sims, 5000), seed=args.seed,
                                         record_fan=False, **kw))
            robustness.append((label, r))

    actual = None
    if today is not None and today.valid[0, start_slot:end_slot + 1].mean() >= 0.8:
        actual = mc.summarize(mc.simulate(today, plan, mode="replay", vol_scale=1.0, record_fan=False, **common))

    # ---------------------------------------------------------------- notes
    notes.append(vol_note)
    drift = float(hist.rc[:, start_slot:end_slot + 1].sum(axis=1).mean())
    if abs(drift) > 0.15 * float(np.sqrt((hist.rc[:, start_slot:end_slot + 1] ** 2).sum(axis=1).mean())):
        notes.append(f"the history drifted {drift:+.2%} on average over this time window; "
                     f"compare with the 'drift removed' row before trusting a directional edge")
    if hist.n_days < 20:
        notes.append(f"only {hist.n_days} historical sessions: the odds rest on few distinct days; get more "
                     "history (Alpaca or a CSV) before leaning on them")
    if summary["ambiguous_bar_share"] > 0.05:
        notes.append(f"{summary['ambiguous_bar_share']:.0%} of paths had a bar touching stop and target together; "
                     f"the stop is tight for {interval}m bars, so rerun with 1m data or check the worst-case row")
    if risk / entry < 0.0015:
        notes.append("the stop is under 0.15% away: spread and slippage dominate a stop this tight")
    notes.append(f"Monte Carlo error is about ±{summary['p_profit_ci95']:.1%}; the real uncertainty is "
                 f"whether the next session behaves like these {hist.n_days} did")
    notes.append("this is a statistical what-if built from past bars, not a prediction or financial advice")

    units = args.shares or plan_file.get("shares")
    pv = args.point_value
    to_usd = (lambda x: x * units * pv) if units else None

    if args.json:
        emit_json({
            "symbol": symbol, "session_date": session_date, "entry_time": entry_t.strftime("%H:%M"),
            "flat_by": flat_by.strftime("%H:%M"), "interval_min": interval, "source": bars.attrs.get("source"),
            "history": {"days": hist.n_days, "first": hist.days[0], "last": hist.days[-1]},
            "plan": {"side": plan.side, "entry": plan.entry, "stop": plan.stop, "risk": plan.risk,
                     "targets": [{"price": t.price, "fraction": t.fraction, "r": plan.r_of(t.price)}
                                 for t in plan.targets],
                     "breakeven_after": be or None, "trail_r": plan.trail_r, "slippage": plan.slippage},
            "vol_scale": vol_scale, "demean": args.demean, "ambiguous": args.ambiguous,
            "simulation": {k: v for k, v in summary.items() if k not in ("fan",)},
            "exact_replay": {k: v for k, v in replay.items() if not k.startswith("curve") and k != "histogram"},
            "robustness": {label: {k: r[k] for k in ("p_target", "p_stop", "p_profit", "expected_r")}
                           for label, r in robustness},
            "actual_outcome": None if actual is None else {
                "outcome": "target" if actual["p_target"] else "stop" if actual["p_stop"] else
                "partial_then_stop" if actual["p_partial_then_stop"] else "time_exit",
                "r": actual["expected_r"]},
            "notes": notes,
        })
    else:
        between = summary["p_time_exit"] + summary["p_partial_then_stop"]
        print(f"TIME MACHINE · {symbol} {plan.side} @ {plan.entry:.2f} · {session_date} {entry_t:%H:%M} → "
              f"{flat_by:%H:%M} · {res.n:,} simulated rest-of-days")
        print(f"Plan: {plan.describe()}")
        print(f"History: {hist.n_days} sessions of {interval}m bars ({hist.days[0]} → {hist.days[-1]}, "
              f"source {bars.attrs.get('source')}), {res.steps} bars simulated, avg block {args.block:g} min, "
              f"vol ×{vol_scale:.2f}{', drift removed' if args.demean else ''}")
        print()
        print("OUTCOMES")
        rows = [("Hit target" if len(plan.targets) <= 1 else "Hit every target", summary["p_target"]),
                ("Hit stop", summary["p_stop"]),
                ("Ended in between", between)]
        for label, v in rows:
            print(f"  {dots(label)}{v:6.1%}  {bar(v)}")
        if summary["p_partial_then_stop"]:
            print(f"     {dots('T1 hit, then stopped', 23)}{summary['p_partial_then_stop']:6.1%}")
        print(f"     {dots('held to close, green', 23)}{summary['p_time_exit_green']:6.1%}")
        print(f"     {dots('held to close, red', 23)}{summary['p_time_exit_red']:6.1%}")
        print(f"  {dots('Made money overall')}{summary['p_profit']:6.1%}  {bar(summary['p_profit'])}")
        if len(plan.targets) > 1:
            for i, p in enumerate(summary["p_each_target"], 1):
                print(f"  {dots(f'Reached T{i}')}{p:6.1%}")
        print()
        print("EXPECTANCY")
        er = summary["expected_r"]
        line = f"  Average result {er:+.2f}R ({er * plan.risk:+.2f}/share)"
        if to_usd:
            line += f" = {money(to_usd(er * plan.risk))} on {units:g} units"
        print(line)
        pc = summary["r_percentiles"]
        print(f"  Range of results: 5% {pc['p5']:+.2f}R · 25% {pc['p25']:+.2f}R · median {pc['p50']:+.2f}R · "
              f"75% {pc['p75']:+.2f}R · 95% {pc['p95']:+.2f}R")
        if len(plan.targets) == 1 and summary.get("breakeven_win_rate_if_all_or_nothing"):
            print(f"  This reward:risk needs a {summary['breakeven_win_rate_if_all_or_nothing']:.1%} hit rate "
                  f"to break even; the simulation hit the target {summary['p_target']:.1%} of the time")
        if summary["median_minutes_to_target"]:
            print(f"  Typical time to target: {summary['median_minutes_to_target']:.0f} min", end="")
            if summary["median_minutes_to_stop"]:
                print(f" · to stop: {summary['median_minutes_to_stop']:.0f} min", end="")
            print()
        if summary["median_mae_of_winners_r"] is not None:
            print(f"  Winners typically sat through {summary['median_mae_of_winners_r']:+.2f}R of heat first")
        if summary["p_full_loss_after_1r_open_profit"] > 0.03:
            print(f"  {summary['p_full_loss_after_1r_open_profit']:.1%} of paths were up 1R or more and still "
                  "took a full loss: consider partials, a breakeven stop or a trail")
        print()
        print("DISTRIBUTION OF RESULTS (R)")
        centers, share = summary["histogram"]["centers"], summary["histogram"]["share"]
        peak = max(share) or 1
        for c, sh in zip(centers, share):
            if sh >= 0.0005:
                print(f"  ≈{c:+5.1f}R  {sh:6.1%}  {bar(sh / peak, 28)}")
        print()
        print(f"EXACT REPLAY · each of the {replay['paths']} eligible past sessions once, no reshuffling")
        print(f"  {mc.headline(replay)}")
        if robustness:
            print()
            print("ROBUSTNESS · same trade, different assumptions")
            for label, r in robustness:
                print(f"  {dots(label, 20)}{mc.headline(r)}")
        if actual is not None:
            print()
            got = ("target" if actual["p_target"] else "stop" if actual["p_stop"] else
                   "partial, then stop" if actual["p_partial_then_stop"] else "held to the close")
            print(f"WHAT ACTUALLY HAPPENED on {session_date}: {got}, {actual['expected_r']:+.2f}R")
        print()
        print("NOTES")
        for n in notes:
            print(f"  - {n}")

    if args.html:
        levels = {"Stop": plan.stop, "Entry": plan.entry}
        for i, t in enumerate(plan.targets, 1):
            levels[f"T{i}"] = t.price
        page = time_machine_html(
            f"Time Machine · {symbol} {plan.side}",
            f"{session_date} entry {entry_t:%H:%M} · {res.n:,} simulated rest-of-days from {hist.n_days} "
            f"historical sessions of {interval}m bars",
            summary, [plan.describe(), f"Flat by {flat_by:%H:%M}", f"Vol scale ×{vol_scale:.2f}"],
            levels, notes,
        )
        out = Path(args.html).expanduser()
        out.write_text(page)
        print(f"\nHTML report: {out.resolve()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    run(main)
