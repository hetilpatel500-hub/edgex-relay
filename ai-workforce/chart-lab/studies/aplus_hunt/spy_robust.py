#!/usr/bin/env python3
"""Robustness for the SPY hunt's top daily setups (run after spy_hunt.py).

Checks that can only make a result look worse: every daily exit on the same
entries; with and without the 200-day filter; and the same exit on EVERY day
and on every Tuesday (the drift reference: if buying any day does as well,
the "setup" is just SPY going up). One position at a time, 2 bps costs,
TEST window = spy_hunt.py's daily TEST (from its spy_results.json).

usage: python3 spy_robust.py    writes spy_robust.json and prints a summary
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hunt  # noqa: E402
import core  # noqa: E402
import robust  # noqa: E402

core.HERE = os.path.join(hunt.LAB, 'studies', 'data_spy')
META = json.load(open(os.path.join(HERE, 'spy_results.json')))['meta']
TEST_FROM = META['daily']['test_from']


def run(D, rule, exit_name, sma):
    stop, tgt, hold = robust.EXITS[exit_name]
    out, free = [], 0
    for i in range(200, len(D.c) - 1):
        if i < free or not rule(D, i) or (sma and not robust.sma_ok(D, i)):
            continue
        r = core.trade_d(D, i, 1, stop, tgt, hold)
        if r is None:
            continue
        out.append((D.day[i].isoformat(), r))
        free = i + hold + 1
    return out


def st(tr):
    return core.stats([r for _, r in tr])


def main():
    D = core.Daily('SPY')
    rules = {
        'n_d_turnaround_tuesday': lambda D, i: D.day[i].weekday() == 0 and D.c[i] < D.c[i - 1],
        'n2_d_turn_of_month': lambda D, i: i + 1 < len(D.day) and D.day[i + 1].month != D.day[i].month,
        'n2_d_seven_day_low': robust.lowest_close(7),
        'n2_d_gap_down_reversal': lambda D, i: D.o[i] < D.l[i - 1] and D.c[i] > D.o[i],
        'reference_any_monday': lambda D, i: D.day[i].weekday() == 0,
        'reference_any_day': lambda D, i: True,
    }
    out = {'test_from': TEST_FROM}
    for k, f in rules.items():
        res = {}
        for sma in (True, False):
            for e in robust.EXITS:
                tr = run(D, f, e, sma)
                res[f"{'sma200' if sma else 'none'}|{e}"] = {'full': st(tr), 'test': st([t for t in tr if t[0] >= TEST_FROM])}
        out[k] = res
        print(f'\n== {k}')
        for v, x in res.items():
            print(f"  {v:22s} full n {x['full']['n']:4d} {x['full'].get('avg_r', 0):+.3f} t {x['full'].get('t_stat')}"
                  f" | test n {x['test']['n']:3d} {x['test'].get('avg_r', 0):+.3f} t {x['test'].get('t_stat')}")
    json.dump(out, open(os.path.join(HERE, 'spy_robust.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
