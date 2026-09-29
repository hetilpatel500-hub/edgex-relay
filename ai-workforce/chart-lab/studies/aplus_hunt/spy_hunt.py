#!/usr/bin/env python3
"""A+ setup hunt on SPY only (owner, 2026-09-29: "everything back test only
on SPY"). Analysis only: nothing here places, stages or suggests orders.

DATA (Webull get_stock_bars, read-only, ../data_spy/data)
  SPY 5-minute RTH bars 2023-09-21 .. 2026-09-28 (about 3 years) and SPY
  daily bars 2002-11-25 .. 2026-09-25 (the 2008, 2020 and 2022 declines).

CANDIDATES
  The same 65 as hunt.py: every Chart Desk setup plus the 11 new ideas.

METHOD (fixed before this run; it builds in the checks that removed the
last round's paper A+ grades instead of adding them afterwards)
  * Dates split 50% TRAIN / 25% VALIDATE / 25% TEST. Side, filter and exit
    are chosen on TRAIN only. TEST is looked at once.
  * One position at a time: intraday, the first qualifying signal of each
    session only; daily, no new trade until the previous one has exited.
  * Same filters and exits as hunt.py (lab filters + d200 + am; lab exits;
    daily exits incl. 1- and 2-day holds). Costs 2 bps round trip.

GRADES (fixed before this run)
  A+  TRAIN n >= 40, avg >= +0.05R; VALIDATE n >= 30, avg >= +0.05R;
      TEST n >= 30, avg >= +0.10R, PF >= 1.3, t >= 2.0;
      TEST beats a random baseline with the SAME direction, the same filter
      state and the same exit (this removes SPY's upward drift) by >= 0.10R
      with p < 0.05 (share of 300 random runs doing as well);
      positive in at least 60% of calendar years that have 5+ trades;
      Bonferroni: one-sided TEST p x K < 0.05 (K = candidates graded).
  A   VALIDATE and TEST avg >= +0.05R, TEST t >= 1.5, PF >= 1.15, and TEST
      beats the matched random baseline.
  B   VALIDATE and TEST both positive.
  C   anything else.

usage: python3 spy_hunt.py      writes spy_results.json and prints the table
"""
import json, math, os, random, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hunt  # noqa: E402  (loads setups, extends filters and exits)
import core, lab  # noqa: E402

core.HERE = os.path.join(hunt.LAB, 'studies', 'data_spy')
core.UNIVERSE = ['SPY']
MIN_TRAIN = 40


def one_per_session(sigs):
    seen, out = set(), []
    for x in sorted(sigs, key=lambda x: x[0]):
        if x[0] in seen:
            continue
        seen.add(x[0]); out.append(x)
    return out


def one_at_a_time_daily(sigs, D, hold):
    pos = {d: k for k, d in enumerate(D.day)}
    out, free = [], -1
    for x in sorted(sigs, key=lambda x: x[0]):
        k = pos[x[0]]
        if k < free:
            continue
        out.append(x); free = k + hold + 1
    return out


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def main():
    t0 = time.time()
    sess = {'SPY': core.sessions('SPY')}
    D = core.Daily('SPY')
    daily = {'SPY': D}
    hunt.attach_d200(sess, daily)
    m5_days = sorted(s.day for s in sess['SPY'])
    d_days = [d for d in D.day[200:]]
    c_m5 = (m5_days[int(len(m5_days) * .5)], m5_days[int(len(m5_days) * .75)])
    c_d = (d_days[int(len(d_days) * .5)], d_days[int(len(d_days) * .75)])
    rng = random.Random(11)
    rows, variants = [], 0
    for st in hunt.SETUPS:
        m5 = st['tf'] == 'M5'
        if m5:
            raw = lab.signals_m5(st, sess['SPY'])
        else:
            raw = [x for x in lab.signals_d(st, D) if x[0] >= D.day[200]]
        c1, c2 = c_m5 if m5 else c_d
        combos = lab.COMBOS if m5 else lab.COMBOS_D
        exits = [(sd, e) for sd, _ in lab.SIDES for e in (core.EXITS if m5 else core.EXITS_D)]
        variants += len(combos) * len(exits)
        best = None
        for c in combos:
            flt = [x for x in raw if c in x[3]]
            for e in exits:
                chosen = one_per_session(flt) if m5 else one_at_a_time_daily(flt, D, core.EXITS_D[e[1]][2])
                tr = [x[2][e] for x in chosen if x[0] < c1]
                if len(tr) < MIN_TRAIN:
                    continue
                a = sum(tr) / len(tr)
                if best is None or a > best[0]:
                    best = (a, c, e)
        r = {k: st.get(k) for k in ('id', 'name', 'family', 'rules', 'tf')}
        r['round'] = st.get('round', 1)
        r['signals'] = len(raw)
        if best is None:
            r.update(grade='C', note=f'fewer than {MIN_TRAIN} training trades for every variant'); rows.append(r); continue
        _, c, e = best
        flt = [x for x in raw if c in x[3]]
        chosen = one_per_session(flt) if m5 else one_at_a_time_daily(flt, D, core.EXITS_D[e[1]][2])
        TR = core.stats([x[2][e] for x in chosen if x[0] < c1])
        VA = core.stats([x[2][e] for x in chosen if c1 <= x[0] < c2])
        test = [x for x in chosen if x[0] >= c2]
        TE = core.stats([x[2][e] for x in test])
        years = {}
        for x in chosen:
            years.setdefault(str(x[0])[:4], []).append(x[2][e])
        yq = {y: v for y, v in years.items() if len(v) >= 5}
        ypos = sum(1 for v in yq.values() if sum(v) > 0)
        # matched random baseline on TEST: same direction, filter state and exit
        sgn = 1 if e[0] == 'with' else -1
        means = []
        if test:
            if m5:
                pool = [s for s in sess['SPY'] if s.day >= c2]
            else:
                pool = [k for k, dy in enumerate(D.day) if dy >= c2 and k + 11 < len(D.c)]
            for _ in range(300):
                rs = []
                for x in test:
                    d = x[4]
                    for _try in range(20):
                        if m5:
                            s = rng.choice(pool); i = rng.randrange(3, 66)
                            if lab.passes(c, lab.FILTERS, s, i, d):
                                v = core.trade(s, i, d * sgn, *core.EXITS[e[1]]); break
                        else:
                            k = rng.choice(pool)
                            if lab.passes(c, lab.FILTERS_D, D, k, d):
                                v = core.trade_d(D, k, d * sgn, *core.EXITS_D[e[1]]); break
                    else:
                        v = None
                    if v is not None:
                        rs.append(v)
                if rs:
                    means.append(sum(rs) / len(rs))
        mb = sum(means) / len(means) if means else None
        pm = sum(1 for m in means if m >= TE.get('avg_r', 0)) / len(means) if means else None
        r.update(side=e[0], filter=c, exit=e[1], train=TR, validate=VA, test=TE,
                 matched_baseline=round(mb, 3) if mb is not None else None,
                 edge_vs_matched=round(TE['avg_r'] - mb, 3) if mb is not None and TE.get('n') else None,
                 p_vs_matched=pm, years_positive=f'{ypos}/{len(yq)}', ypos=ypos, yn=len(yq),
                 by_year={y: round(sum(v) / len(v), 3) for y, v in sorted(years.items())},
                 test_trades=[[str(x[0]), round(x[2][e], 3)] for x in test])
        rows.append(r)
    K = sum(1 for r in rows if r.get('test', {}).get('n', 0) >= 30)
    for r in rows:
        if 'test' not in r:
            continue
        TR, VA, TE = r['train'], r['validate'], r['test']
        t = TE.get('t_stat') or 0
        p = 1 - phi(t) if TE.get('n', 0) >= 2 else 1.0
        padj = min(1.0, p * max(K, 1))
        r['p_bonferroni'] = round(padj, 5)
        r['edge_confidence'] = round(100 * (1 - padj))
        ok_n = TR.get('n', 0) >= MIN_TRAIN and VA.get('n', 0) >= 30 and TE.get('n', 0) >= 30
        beats = r['edge_vs_matched'] is not None and r['edge_vs_matched'] >= 0.10 and (r['p_vs_matched'] or 1) < 0.05
        if (ok_n and TR['avg_r'] >= 0.05 and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.10 and (TE['profit_factor'] or 0) >= 1.3
                and t >= 2.0 and beats and r['yn'] and r['ypos'] >= 0.6 * r['yn'] and padj < 0.05):
            g = 'A+'
        elif (ok_n and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.05 and t >= 1.5 and (TE['profit_factor'] or 0) >= 1.15
              and (r['edge_vs_matched'] or 0) > 0):
            g = 'A'
        elif VA.get('n', 0) and TE.get('n', 0) and VA['avg_r'] > 0 and TE['avg_r'] > 0:
            g = 'B'
        else:
            g = 'C'
        r['grade'] = g
    order = {'A+': 0, 'A': 1, 'B': 2, 'C': 3}
    rows.sort(key=lambda r: (order[r['grade']], -(r.get('test', {}).get('avg_r') or -9)))
    meta = {'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'source': 'Webull get_stock_bars (read-only), SPY only', 'symbol': 'SPY',
            'intraday': {'sessions': len(m5_days), 'first': str(m5_days[0]), 'last': str(m5_days[-1]),
                         'validate_from': str(c_m5[0]), 'test_from': str(c_m5[1])},
            'daily': {'first_used': str(D.day[200]), 'last': str(D.day[-1]), 'validate_from': str(c_d[0]), 'test_from': str(c_d[1])},
            'candidates': len(hunt.SETUPS), 'graded': K, 'variants_tried_total': variants,
            'grade_counts': {g: sum(1 for r in rows if r['grade'] == g) for g in order},
            'runtime_s': round(time.time() - t0, 1)}
    json.dump({'meta': meta, 'results': rows}, open(os.path.join(HERE, 'spy_results.json'), 'w'), indent=1, default=str)
    for r in rows:
        if 'test' in r:
            T = r['test']
            print(f"{r['grade']:2s} {r['id']:26s} {r['tf']:2s} [{r['side']}|{r['filter']}|{r['exit']}] TR {r['train']['n']:4d} {r['train']['avg_r']:+.3f} "
                  f"VA {r['validate'].get('n',0):4d} {r['validate'].get('avg_r',0):+.3f} TE {T.get('n',0):4d} {T.get('avg_r',0):+.3f} "
                  f"pf {T.get('profit_factor')} t {T.get('t_stat')} win {T.get('win_rate')} vsM {r['edge_vs_matched']} p {r['p_vs_matched']} yrs {r['years_positive']} conf {r['edge_confidence']}")
        else:
            print(f"{r['grade']:2s} {r['id']:26s} {r['note']}")
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()
