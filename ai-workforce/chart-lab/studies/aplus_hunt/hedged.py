#!/usr/bin/env python3
"""Round 3: does the dip beat the index? (drift-free check)

The daily dip-buying setups looked good, but buying on ANY day did about as
well over 2022-2026: the "edge" was mostly the market going up. This check
removes that drift: for each signal, the stock's return from the next open
to the close 10 trading days later MINUS SPY's return over the exact same
days (SPY itself is left out). Costs of 3 bps (stocks) / 2 bps (ETFs) come
off. One position at a time per symbol; the t-statistic is clustered by
entry date. A dip setup has a real, drift-free edge only if this excess
return is positive and significant, and beats the same calculation for
"any day".

usage: python3 hedged.py        writes hedged.json and prints a summary
"""
import json, math, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, LAB)
import core  # noqa: E402
import robust  # noqa: E402

core.HERE = os.path.join(LAB, 'studies', 'data_1y')
HOLD = 10
TEST_FROM = robust.TEST_FROM


def run(rule, need_sma=False):
    spy = core.Daily('SPY')
    spos = {d: k for k, d in enumerate(spy.day)}
    out = []
    for sym in core.UNIVERSE:
        if sym == 'SPY':
            continue
        D = core.Daily(sym)
        free = 0
        for i in range(200, len(D.c) - HOLD - 1):
            if i < free or not rule(D, i) or (need_sma and not robust.sma_ok(D, i)):
                continue
            a, b = D.day[i + 1], D.day[i + HOLD]
            if a not in spos or b not in spos:
                continue
            r_sym = D.c[i + HOLD] / D.o[i + 1] - 1
            r_spy = spy.c[spos[b]] / spy.o[spos[a]] - 1
            cost = core.COST_BPS[sym] / 1e4 + core.COST_BPS['SPY'] / 1e4
            out.append((D.day[i].isoformat(), sym, (r_sym - r_spy - cost) * 100))   # in %
            free = i + HOLD + 1
    return out


def summ(tr):
    xs = [t[2] for t in tr]
    if len(xs) < 3:
        return {'n': len(xs)}
    by = {}
    for d, _, x in tr:
        by.setdefault(d, []).append(x)
    days = [sum(v) / len(v) for v in by.values()]
    sd = st.pstdev(days)
    return {'n': len(xs), 'avg_excess_pct': round(sum(xs) / len(xs), 3),
            'beat_spy_rate': round(sum(1 for x in xs if x > 0) / len(xs), 3),
            'clustered_t': round(sum(days) / len(days) / sd * math.sqrt(len(days)), 2) if sd else None,
            'entry_days': len(days)}


def main():
    rules = {
        'n2_d_seven_day_low': (robust.lowest_close(7), False),
        'n2_d_bollinger_low': (robust.boll(20, 2.0), False),
        'n_d_three_down': (robust.three_down, True),
        'd_rsi2_pullback': (robust.rsi2, False),
        'reference_any_day': (lambda D, i: True, False),
    }
    out = {}
    for k, (f, sma) in rules.items():
        tr = run(f, sma)
        full, test = summ(tr), summ([t for t in tr if t[0] >= TEST_FROM])
        years = {}
        for t in tr:
            years.setdefault(t[0][:4], []).append(t)
        out[k] = {'full': full, 'test': test, 'by_year': {y: summ(v) for y, v in sorted(years.items())}}
        print(f'{k:22s} full {full}\n{"":22s} test {test}')
    json.dump(out, open(os.path.join(HERE, 'hedged.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
