#!/usr/bin/env python3
"""Write a calibration report for the time machine on a bar store.

  python3 calibration_report.py --data STORE --out CALIBRATION.md

1. Clock-time mode on random entries (walk-forward: each test trade is
   predicted only from days before it).
2. Setup mode on every validated/promising intraday setup's out-of-sample
   signals (each predicted only from that setup's earlier signals).
Only aggregate statistics are written, never raw prices.
"""
import argparse, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tskit import backtest, timemachine as tm, data  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--points', type=int, default=600); ap.add_argument('--paths', type=int, default=300)
    a = ap.parse_args()
    res = backtest.run(a.data)
    days = tm.calibrate(a.data, points=a.points, paths=a.paths, seed=3)
    rows = []
    for r in res['results']:
        if r['tf'] != 'M5' or r['status'] not in ('validated', 'promising'):
            continue
        try:
            rows.append(tm.calibrate_setup(a.data, r['id'], res))
        except ValueError:
            continue
    n = sum(x['test_points'] for x in rows)
    pool_tm = sum(x['brier']['time_machine'] * x['test_points'] for x in rows) / n if n else None
    pool_cf = sum(x['brier']['coin_flip'] * x['test_points'] for x in rows) / n if n else None
    m = res['meta']['intraday']
    t = days['target_first']
    L = ['# Time machine calibration', '',
         f"Generated {data.now_utc()} by `engine/tools/calibration_report.py` on a store of "
         f"{len(res['meta']['symbols'])} symbols, {m['sessions']} sessions ({m['first']} to {m['last']}). "
         'Every test trade is predicted only from data before its date (walk-forward). Trade tested: '
         '1 ATR stop, 2R target, entry at a 5-minute close, flat by the close, costs included.', '',
         '## 1. Clock-time mode, random entries', '',
         f"- {days['test_points']} test trades, {days['paths_per_point']} paths each.",
         f"- Target first: predicted {t['predicted_avg']:.1%} on average, actual {t['actual_rate']:.1%} "
         f"(90% range {t['actual_90'][0]:.1%} to {t['actual_90'][1]:.1%}). Coin-flip baseline {t['coin_flip_predicted_avg']:.1%}.",
         f"- Brier score {days['brier']['time_machine']} vs {days['brier']['coin_flip']} for the coin flip "
         f"(skill {days['brier']['skill_vs_coin_flip']:+.3f}; above zero would mean better than the coin flip).",
         f"- Expected R: predicted {days['expected_r']['predicted_avg']:+.3f}, actual {days['expected_r']['actual_avg']:+.3f}.",
         '', 'Reading: on average the odds match reality, but trade by trade this mode is no better than the '
         'coin flip. It knows the time of day and volatility, not direction. Random entries have no edge to find.', '',
         '## 2. Setup mode, out-of-sample signals', '',
         '| Setup | Variant | Test signals | Predicted target first | Actual (90% range) | Coin flip | Brier: time machine / coin flip | Expected R: predicted / actual |',
         '|---|---|---|---|---|---|---|---|']
    for x in rows:
        tf = x['target_first']
        L.append(f"| {x['setup']} | {x['variant']} | {x['test_points']} | {tf['predicted_avg']:.1%} | "
                 f"{tf['actual_rate']:.1%} ({tf['actual_90'][0]:.0%}-{tf['actual_90'][1]:.0%}) | {tf['coin_flip_predicted_avg']:.1%} | "
                 f"{x['brier']['time_machine']} / {x['brier']['coin_flip']} | "
                 f"{x['expected_r']['predicted_avg']:+.2f} / {x['expected_r']['actual_avg']:+.2f} |")
    if n:
        better = sum(x['brier']['time_machine'] < x['brier']['coin_flip'] for x in rows)
        L += ['', f"Pooled over {n} test signals: Brier {pool_tm:.4f} vs {pool_cf:.4f} for the coin flip "
                  f"(skill {1 - pool_tm / pool_cf:+.3f}). Better than the coin flip on {better} of {len(rows)} setups."]
    L += ['', 'Reading: when a setup has a real edge, its own history moves the odds away from the coin flip in the '
              'right direction, but only modestly, and not for every setup. These setups were chosen because they passed '
              'testing on this same store, so their out-of-sample period is cleaner than their in-sample period, but the '
              'set itself is survivor-biased.', '',
          'Educational only. Not financial advice. Historical odds are not a forecast.', '']
    open(a.out, 'w').write('\n'.join(L))
    json.dump({'days_mode': days, 'setup_mode': rows}, open(os.path.splitext(a.out)[0] + '.json', 'w'), indent=1, default=str)
    print('\n'.join(L))


if __name__ == '__main__':
    main()
