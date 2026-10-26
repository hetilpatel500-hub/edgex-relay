#!/usr/bin/env python3
"""Robustness for D2 (two or more daily setups agree), run after combo.py.
Checked after grading; can only make it look worse, never raises a grade:
every exit x filter on the same votes, longs vs shorts, vote threshold
neighbours, year by year, and the same exit on any day (SPY's drift).

usage: python3 robust.py      writes robust.json and prints a summary
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import combo  # noqa: E402  (sets SPY data and loads the hunt setups)
from combo import core, lab, hunt  # noqa: E402

TEST_FROM = json.load(open(os.path.join(HERE, 'results.json')))['meta']['daily']['test_from']


def run(D, votes, k, exit_name, flt, side=None):
    stop, tgt, hold = core.EXITS_D[exit_name]
    out, free = [], -1
    for i in sorted(votes):
        net = sum(votes[i].values()) if votes[i] else 0
        if k == 0:
            d = 1
        elif abs(net) >= k:
            d = 1 if net > 0 else -1
        else:
            continue
        if (side and d != side) or i < free or not lab.passes(flt, lab.FILTERS_D, D, i, d):
            continue
        r = core.trade_d(D, i, d, stop, tgt, hold)
        if r is None:
            continue
        out.append((D.day[i].isoformat(), d, r)); free = i + hold + 1
    return out


def s(tr):
    return core.stats([x[2] for x in tr])


def main():
    D = core.Daily('SPY')
    votes = {i: {} for i in range(200, len(D.c) - 1)}
    for st in [x for x in hunt.SETUPS if x['tf'] == 'D']:
        for i, d in st['detect'](D):
            if i in votes:
                votes[i][st['id']] = d
    out = {'test_from': TEST_FROM, 'grid': {}, 'sides': {}, 'thresholds': {}, 'by_year': {}}
    for flt in lab.COMBOS_D:
        for e in core.EXITS_D:
            a, ref = run(D, votes, 2, e, flt), run(D, votes, 0, e, flt)
            out['grid'][f'{flt}|{e}'] = {'full': s(a), 'test': s([x for x in a if x[0] >= TEST_FROM]),
                                         'any_day_full': s(ref), 'any_day_test': s([x for x in ref if x[0] >= TEST_FROM])}
    for sd, lab_ in ((1, 'long'), (-1, 'short')):
        a = run(D, votes, 2, '1.5atr/3atr/hold10', 'none', sd)
        out['sides'][lab_] = {'full': s(a), 'test': s([x for x in a if x[0] >= TEST_FROM])}
    for k in (1, 2, 3, 4):
        a = run(D, votes, k, '1.5atr/3atr/hold10', 'none')
        out['thresholds'][str(k)] = {'full': s(a), 'test': s([x for x in a if x[0] >= TEST_FROM])}
    a = run(D, votes, 2, '1.5atr/3atr/hold10', 'none')
    ys = {}
    for x in a:
        ys.setdefault(x[0][:4], []).append(x[2])
    out['by_year'] = {y: core.stats(v) for y, v in sorted(ys.items())}
    json.dump(out, open(os.path.join(HERE, 'robust.json'), 'w'), indent=1)
    f = lambda z: (z['n'], z.get('avg_r'), z.get('t_stat'))
    for k, v in out['grid'].items():
        print(f"{k:28s} full {f(v['full'])} test {f(v['test'])} | any day full {f(v['any_day_full'])} test {f(v['any_day_test'])}")
    print('sides', {k: (f(v['full']), f(v['test'])) for k, v in out['sides'].items()})
    print('thresholds', {k: (f(v['full']), f(v['test'])) for k, v in out['thresholds'].items()})
    print('years', {y: (v['n'], v['avg_r']) for y, v in out['by_year'].items()})


if __name__ == '__main__':
    main()
