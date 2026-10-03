#!/usr/bin/env python3
"""Diagnostics for odte.py (run after it): D2 as calls and the plain daily call
/ put references at each volatility assumption, split into the same periods,
plus how far SPY moves before the owner's stop and target trigger.

usage: python3 diag.py      writes diag.json and prints a summary
"""
import json, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import odte  # noqa: E402
from odte import core, hunt  # noqa: E402


def summary(tr):
    s = odte.stats(tr)
    return {k: s.get(k) for k in ('n', 'win_rate', 'avg_r', 't_stat', 'avg_usd', 'total_usd', 'max_dd_usd', 'longest_losing_streak')}


def main():
    out = {}
    D = core.Daily('SPY')
    for vm in (1.0, 1.25, 1.5):
        odte.VOL_MULT = vm
        sess = core.sessions('SPY')
        odte.attach_vol(sess)
        sess = [s for s in sess if s.iv is not None]
        days = [s.day for s in sess]
        c1, c2 = days[int(len(days) * .5)], days[int(len(days) * .75)]
        by_day = {s.day: s for s in sess}
        votes = {}
        for stp in [x for x in hunt.SETUPS if x['tf'] == 'D']:
            for i, d in stp['detect'](D):
                votes.setdefault(i, {})[stp['id']] = d
        d2 = []
        for i, v in sorted(votes.items()):
            if sum(v.values()) >= 2 and i + 1 < len(D.day) and D.day[i + 1] in by_day:
                r = odte.sim(by_day[D.day[i + 1]], 1, 1)
                if r:
                    d2.append(dict(r, day=D.day[i + 1]))
        calls = [dict(r, day=s.day) for s in sess for r in [odte.sim(s, 1, 1)] if r]
        puts = [dict(r, day=s.day) for s in sess for r in [odte.sim(s, 1, -1)] if r]
        res = {}
        for name, tr in (('D2_calls', d2), ('call_every_day', calls), ('put_every_day', puts)):
            res[name] = {'full': summary(tr), 'train': summary([t for t in tr if t['day'] < c1]),
                         'validate': summary([t for t in tr if c1 <= t['day'] < c2]), 'test': summary([t for t in tr if t['day'] >= c2])}
        out[str(vm)] = res
        print(f'vol x{vm}')
        for k, v in res.items():
            print(f"  {k:15s} " + ' | '.join(f"{p} n {v[p]['n']} win {v[p]['win_rate']} ${v[p]['avg_usd']}/tr" for p in ('train', 'validate', 'test', 'full')))
    # how far SPY moves before the stop / target (vol x1.25, random entries 9:35-15:25)
    odte.VOL_MULT = 1.25
    sess = core.sessions('SPY'); odte.attach_vol(sess)
    sess = [s for s in sess if s.iv is not None]
    mv_stop, mv_tgt, t_stop = [], [], []
    for s in sess[-120:]:
        for j in range(1, 70, 6):
            for cp in (1, -1):
                r = odte.sim(s, j, cp)
                if not r:
                    continue
                S0 = s.bars[j].o
                # find the bar where it exited to measure the SPY move and minutes
                K = r['strike']; fill = r['premium']
                for k in range(j, len(s.bars)):
                    x = s.bars[k]; t_end = 960 - (x.m + 5)
                    lo = odte.bs(x.l if cp > 0 else x.h, K, t_end, s.iv, cp)
                    hi = odte.bs(x.h if cp > 0 else x.l, K, t_end, s.iv, cp)
                    if lo <= fill * (1 - odte.STOP_PCT):
                        mv_stop.append(abs((x.l if cp > 0 else x.h) - S0) / S0 * 100); t_stop.append(x.m + 5 - s.bars[j].m); break
                    if hi >= fill * odte.TGT_MULT:
                        mv_tgt.append(abs((x.h if cp > 0 else x.l) - S0) / S0 * 100); break
    out['move_to_trigger'] = {'median_spy_move_to_stop_pct': round(st.median(mv_stop), 3), 'median_minutes_to_stop': st.median(t_stop),
                              'median_spy_move_to_target_pct': round(st.median(mv_tgt), 3) if mv_tgt else None,
                              'samples_stop': len(mv_stop), 'samples_target': len(mv_tgt)}
    print(out['move_to_trigger'])
    json.dump(out, open(os.path.join(HERE, 'diag.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
