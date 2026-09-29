#!/usr/bin/env python3
"""Robustness checks for the hunt's A+ and A daily setups (run after hunt.py).

These checks can only make a result look worse, never better, and none of
them changes a grade upward:
  1. One position at a time per symbol (signals while a trade is open are
     skipped), so overlapping trades can't inflate the count.
  2. Clustered by entry date: all trades entered on the same day are averaged
     into one number before the t-statistic, because 12 correlated symbols
     buying on the same day are not 12 independent bets.
  3. Parameter neighbours (e.g. 5- and 10-day lows, 1.5 and 2.5 sd bands):
     an edge that exists at only one exact setting is probably luck.
  4. Every daily exit, same entries.
  5. Year by year and per symbol.
All numbers are on the full period used by the hunt (2022-09-30 to
2026-09-25) and on its TEST window (from 2025-09-29) separately.

usage: python3 robust.py        writes robust.json and prints a summary
"""
import json, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, LAB)
import core  # noqa: E402

core.HERE = os.path.join(LAB, 'studies', 'data_1y')
EXITS = dict(core.EXITS_D, **{'2atr/hold1': (2.0, None, 1), '2atr/hold2': (2.0, None, 2)})
TEST_FROM = '2025-09-29'


def lowest_close(n):
    def f(D, i):
        return i >= n and D.c[i] <= min(D.c[i - n + 1:i + 1])
    return f


def boll(win, k):
    def f(D, i):
        if i < win:
            return False
        w = D.c[i - win + 1:i + 1]
        m, sd = sum(w) / win, st.pstdev(w)
        return sd > 0 and D.c[i] < m - k * sd
    return f


def three_down(D, i):
    return i >= 3 and D.c[i] < D.c[i - 1] < D.c[i - 2] < D.c[i - 3]


def rsi2(D, i):
    return D.rsi2[i] is not None and D.rsi2[i] < 10 and D.sma200[i] is not None and D.c[i] > D.sma200[i]


def sma_ok(D, i):
    return D.sma200[i] is not None and D.c[i] > D.sma200[i]


def run(rule, exit_name, need_sma=False, overlap=True):
    stop, tgt, hold = EXITS[exit_name]
    trades = []
    for sym in core.UNIVERSE:
        D = core.Daily(sym)
        free = 0
        for i in range(200, len(D.c) - 1):
            if not rule(D, i) or (need_sma and not sma_ok(D, i)):
                continue
            if not overlap and i < free:
                continue
            r = core.trade_d(D, i, 1, stop, tgt, hold)
            if r is None:
                continue
            trades.append((D.day[i].isoformat(), sym, r))
            free = i + hold + 1
    return trades


def clustered_t(trades):
    by = {}
    for d, _, r in trades:
        by.setdefault(d, []).append(r)
    xs = [sum(v) / len(v) for v in by.values()]
    if len(xs) < 3:
        return None, len(xs)
    sd = st.pstdev(xs)
    return (round(sum(xs) / len(xs) / sd * math.sqrt(len(xs)), 2) if sd else None), len(xs)


def summary(trades):
    rs = [t[2] for t in trades]
    s = core.stats(rs)
    s['clustered_t'], s['entry_days'] = clustered_t(trades)
    return s


def block(trades):
    test = [t for t in trades if t[0] >= TEST_FROM]
    years = {}
    for t in trades:
        years.setdefault(t[0][:4], []).append(t[2])
    syms = {}
    for t in test:
        syms.setdefault(t[1], []).append(t[2])
    return {'full': summary(trades), 'test': summary(test),
            'by_year': {y: core.stats(v) for y, v in sorted(years.items())},
            'test_by_symbol': {k: round(sum(v) / len(v), 3) for k, v in sorted(syms.items())}}


def main():
    out = {}
    cands = {
        'n2_d_seven_day_low': dict(rule=lowest_close(7), exit='2atr/hold10', sma=False,
                                   neighbours={f'{n}-day low': lowest_close(n) for n in (5, 6, 8, 10)}),
        'n2_d_bollinger_low': dict(rule=boll(20, 2.0), exit='2atr/hold10', sma=False,
                                   neighbours={'20d 1.5sd': boll(20, 1.5), '20d 2.5sd': boll(20, 2.5),
                                               '10d 2sd': boll(10, 2.0), '30d 2sd': boll(30, 2.0)}),
        'n_d_three_down': dict(rule=three_down, exit='2atr/hold10', sma=True, neighbours={}),
        'd_rsi2_pullback': dict(rule=rsi2, exit='2atr/hold10', sma=False, neighbours={}),
    }
    for cid, c in cands.items():
        res = {'as_graded_overlapping': block(run(c['rule'], c['exit'], c['sma'])),
               'one_position_per_symbol': block(run(c['rule'], c['exit'], c['sma'], overlap=False))}
        res['exits_one_position'] = {e: summary([t for t in run(c['rule'], e, c['sma'], overlap=False) if t[0] >= TEST_FROM])
                                     for e in EXITS}
        res['neighbours_one_position_test'] = {k: summary([t for t in run(f, c['exit'], c['sma'], overlap=False) if t[0] >= TEST_FROM])
                                               for k, f in c['neighbours'].items()}
        out[cid] = res
        o = res['one_position_per_symbol']
        print(f"\n== {cid}")
        print('  graded (overlapping) test:', res['as_graded_overlapping']['test'])
        print('  one position/symbol  test:', o['test'])
        print('  one position/symbol  full:', o['full'])
        print('  by year:', {y: (v['n'], v['avg_r']) for y, v in o['by_year'].items()})
        print('  exits (test):', {e: (v['n'], v.get('avg_r'), v.get('clustered_t')) for e, v in res['exits_one_position'].items()})
        print('  neighbours (test):', {k: (v['n'], v.get('avg_r'), v.get('clustered_t')) for k, v in res['neighbours_one_position_test'].items()})
        print('  test by symbol:', o['test_by_symbol'])
    # market drift reference: buy every day, same exit, one position per symbol
    drift = block(run(lambda D, i: True, '2atr/hold10', overlap=False))
    out['reference_buy_any_day'] = drift
    print('\n== reference: buy any day (one position/symbol), 2atr/hold10 test:', drift['test'], 'full:', drift['full'])
    json.dump(out, open(os.path.join(HERE, 'robust.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
