#!/usr/bin/env python3
"""A+ setup hunt (owner request 2026-09-29: "make strategies using our agents
that are back tested heavily and give a high probability score which counts
as an A+ setup").

Analysis only: nothing here places, stages or suggests orders.

CANDIDATES
  Every Chart Desk setup in ../../setups/*.py (written by the 20 Chart Desk
  agents over the past week) plus the new documented ideas in new_setups.py.

DATA (Webull get_stock_bars, read-only)
  5-minute RTH bars 2025-10-01 .. 2026-09-28 for 12 symbols (../data_1y/data),
  daily bars 2021-12 .. 2026-09-25.

METHOD (fixed before any result was seen)
  Dates are split three ways:
    TRAIN     first 50% of dates: each candidate's side (with/fade), filter
              and exit are chosen here and nowhere else.
    VALIDATE  next 25%: the chosen variant must hold up.
    TEST      last 25%: the final exam, looked at once per candidate.
  Intraday filters: the lab's nine (none, vwap, rvol, ppoc, trend and pairs)
  plus the daily 200-day MA trend (d200) and "before 11:00" (am) and their
  pairs with vwap/trend/rvol. Intraday exits: the lab's 7 ATR exits.
  Daily filters: none, sma200. Daily exits: the lab's 4 plus 1-day and
  2-day holds (short-term mean-reversion ideas need them).
  Costs: 2 bps ETFs, 3 bps stocks, every trade. Random-entry baselines per
  exit, computed on the same data.

GRADES (fixed before any result was seen)
  A+  TRAIN n >= 40 and avg >= +0.05R;
      VALIDATE n >= 30 and avg >= +0.05R;
      TEST n >= 30, avg >= +0.10R, profit factor >= 1.3, t >= 2.0;
      TEST avg beats the random baseline for its exit by >= 0.10R;
      positive in at least 60% of the symbols it traded (VALIDATE+TEST);
      and still significant after correcting for every candidate that
      reached the final exam (Bonferroni: one-sided p x K < 0.05).
  A   VALIDATE and TEST avg >= +0.05R, TEST t >= 1.5 and PF >= 1.15.
  B   VALIDATE and TEST both positive.
  C   anything else (or too few trades).
  "Edge confidence" = 100 x (1 - Bonferroni-adjusted p) on the TEST period:
  how unlikely the final-exam result would be if the setup had no edge,
  after allowing for how many setups were tried. It is not a win rate.

usage: python3 hunt.py            writes results.json and prints the table
"""
import glob, importlib.util, json, math, os, random, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, LAB)
import core, lab  # noqa: E402

SETUPS = lab.load_setups()                         # lab setups, loaded from the lab's own folder
spec = importlib.util.spec_from_file_location('new_setups', os.path.join(HERE, 'new_setups.py'))
ns = importlib.util.module_from_spec(spec); spec.loader.exec_module(ns)
for rnd, lst in ((1, ns.SETUPS), (2, getattr(ns, 'ROUND2', []))):
    for s in lst:
        s = dict(s); s.setdefault('tf', 'M5'); s['round'] = rnd; SETUPS.append(s)

core.HERE = os.path.join(LAB, 'studies', 'data_1y')   # read the one-year data

lab.FILTERS.update({
    'd200': lambda s, i, d: getattr(s, 'd200', None) == d,
    'am': lambda s, i, d: s.bars[i].m < 660,
})
lab.COMBOS = lab.COMBOS + ['d200', 'vwap+d200', 'trend+d200', 'rvol+d200', 'am', 'vwap+am', 'd200+am']
core.EXITS_D = dict(core.EXITS_D, **{'2atr/hold1': (2.0, None, 1), '2atr/hold2': (2.0, None, 2)})
MIN_TRAIN = 40


def attach_d200(sess, daily):
    for sym, ss in sess.items():
        D = daily[sym]
        pos = {d: k for k, d in enumerate(D.day)}
        for s in ss:
            prev = max((k for d, k in pos.items() if d < s.day), default=None) if s.day not in pos else pos[s.day] - 1
            if prev is not None and prev >= 0 and D.sma200[prev] is not None:
                s.d200 = 1 if D.c[prev] > D.sma200[prev] else -1


def daily_baseline(daily):
    rnd = random.Random(7)
    rs = {k: [] for k in core.EXITS_D}
    for D in daily.values():
        n = len(D.c)
        for _ in range(400):
            i, d = rnd.randrange(200, n - 25), rnd.choice((1, -1))
            for k, e in core.EXITS_D.items():
                r = core.trade_d(D, i, d, *e)
                if r is not None:
                    rs[k].append(r)
    return {k: round(sum(v) / len(v), 3) for k, v in rs.items()}


def cuts(dates):
    ds = sorted(set(dates))
    return ds[int(len(ds) * 0.5)], ds[int(len(ds) * 0.75)]


def phi(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def pick(st, sigs, c1):
    combos = lab.COMBOS if st['tf'] == 'M5' else lab.COMBOS_D
    exits = [(sd, e) for sd, _ in lab.SIDES for e in (core.EXITS if st['tf'] == 'M5' else core.EXITS_D)]
    best = None
    for c in combos:
        for e in exits:
            rs = [x[2][e] for x in sigs if x[0] < c1 and c in x[3]]
            if len(rs) < MIN_TRAIN:
                continue
            a = sum(rs) / len(rs)
            if best is None or a > best[0]:
                best = (a, c, e)
    return best, len(combos) * len(exits)


def main():
    t0 = time.time()
    sess = {s: core.sessions(s) for s in core.UNIVERSE}
    daily = {s: core.Daily(s) for s in core.UNIVERSE}
    attach_d200(sess, daily)
    lab.baseline(sess)
    base_m5, base_d = dict(lab.BASE), daily_baseline(daily)
    c_m5 = cuts([x.day for v in sess.values() for x in v])
    c_d = cuts([d for v in daily.values() for d in v.day if d >= v.day[200]])
    rows, variants = [], 0
    for st in SETUPS:
        m5 = st['tf'] == 'M5'
        if m5:
            sigs = [x for sym in core.UNIVERSE for x in lab.signals_m5(st, sess[sym])]
        else:
            sigs = [x for sym in core.UNIVERSE for x in lab.signals_d(st, daily[sym]) if x[0] >= daily[sym].day[200]]
        c1, c2 = c_m5 if m5 else c_d
        best, nv = pick(st, sigs, c1)
        variants += nv
        r = {k: st.get(k) for k in ('id', 'name', 'family', 'rules', 'tf', 'file')}
        r['round'] = st.get('round', 1)
        r['variants_tried'] = nv
        r['signals'] = len(sigs)
        if best is None:
            r.update(grade='C', note=f'fewer than {MIN_TRAIN} training trades for every variant')
            rows.append(r); continue
        _, c, e = best
        ch = sorted([x for x in sigs if c in x[3]], key=lambda x: x[0])
        tr = [x[2][e] for x in ch if x[0] < c1]
        va = [x[2][e] for x in ch if c1 <= x[0] < c2]
        te = [x[2][e] for x in ch if x[0] >= c2]
        per = {}
        for x in ch:
            if x[0] >= c1:
                per.setdefault(x[1], []).append(x[2][e])
        sym_pos = sum(1 for v in per.values() if sum(v) > 0)
        base = (base_m5 if m5 else base_d).get(e[1])
        TR, VA, TE = core.stats(tr), core.stats(va), core.stats(te)
        r.update(side=e[0], filter=c, exit=e[1], train=TR, validate=VA, test=TE, random_baseline_r=base,
                 test_edge_vs_random=round(TE['avg_r'] - base, 3) if TE.get('n') and base is not None else None,
                 symbols_positive=f'{sym_pos}/{len(per)}', sym_pos=sym_pos, sym_n=len(per),
                 by_symbol={k: round(sum(v), 2) for k, v in sorted(per.items())})
        rows.append(r)
    K = sum(1 for r in rows if 'test' in r and r['test'].get('n', 0) >= 30)
    for r in rows:
        if 'test' not in r:
            continue
        TR, VA, TE = r['train'], r['validate'], r['test']
        t = TE.get('t_stat') or 0
        p = 1 - phi(t) if TE.get('n', 0) >= 2 else 1.0
        padj = min(1.0, p * max(K, 1))
        r['p_one_sided'] = round(p, 5)
        r['p_bonferroni'] = round(padj, 5)
        r['edge_confidence'] = round(100 * (1 - padj))
        ok_n = TR.get('n', 0) >= MIN_TRAIN and VA.get('n', 0) >= 30 and TE.get('n', 0) >= 30
        if (ok_n and TR['avg_r'] >= 0.05 and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.10
                and (TE['profit_factor'] or 0) >= 1.3 and t >= 2.0
                and (r['test_edge_vs_random'] or 0) >= 0.10 and r['sym_pos'] >= 0.6 * r['sym_n'] and padj < 0.05):
            g = 'A+'
        elif ok_n and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.05 and t >= 1.5 and (TE['profit_factor'] or 0) >= 1.15:
            g = 'A'
        elif VA.get('n', 0) and TE.get('n', 0) and VA['avg_r'] > 0 and TE['avg_r'] > 0:
            g = 'B'
        else:
            g = 'C'
        r['grade'] = g
    # Stricter check added in round 2 (it can only make a result look worse):
    # random entries with the SAME direction mix, the same filter state and
    # the same exit, in the TEST period only. For long-only daily ideas this
    # removes the market's own drift.
    rnd = random.Random(11)
    for r in rows:
        if r.get('grade') not in ('A+', 'A', 'B'):
            continue
        st = next(x for x in SETUPS if x['id'] == r['id'])
        m5 = st['tf'] == 'M5'
        sd_mult = 1 if r['side'] == 'with' else -1
        c1, c2 = c_m5 if m5 else c_d
        if m5:
            sigs = [x for sym in core.UNIVERSE for x in lab.signals_m5(st, sess[sym])]
        else:
            sigs = [x for sym in core.UNIVERSE for x in lab.signals_d(st, daily[sym])]
        test_sigs = [x for x in sigs if x[0] >= c2 and r['filter'] in x[3]]
        means = []
        for _ in range(300):
            rs = []
            for (day, sym, _rs, _ok, d) in test_sigs:
                dd = d * sd_mult
                if m5:
                    ss = [s for s in sess[sym] if s.day >= c2]
                    s = rnd.choice(ss)
                    i = rnd.randrange(3, 66)
                    if not lab.passes(r['filter'], lab.FILTERS, s, i, d):
                        continue
                    v = core.trade(s, i, dd, *core.EXITS[r['exit']])
                else:
                    D = daily[sym]
                    idx = [k for k, dy in enumerate(D.day) if dy >= c2 and k + 11 < len(D.c)]
                    k = rnd.choice(idx)
                    if not lab.passes(r['filter'], lab.FILTERS_D, D, k, d):
                        continue
                    v = core.trade_d(D, k, dd, *core.EXITS_D[r['exit']])
                if v is not None:
                    rs.append(v)
            if rs:
                means.append(sum(rs) / len(rs))
        if means:
            m = sum(means) / len(means)
            r['matched_baseline_test_r'] = round(m, 3)
            r['test_edge_vs_matched'] = round(r['test']['avg_r'] - m, 3)
            r['p_vs_matched'] = round(sum(1 for x in means if x >= r['test']['avg_r']) / len(means), 3)
    order = {'A+': 0, 'A': 1, 'B': 2, 'C': 3}
    rows.sort(key=lambda r: (order[r['grade']], -(r.get('test', {}).get('avg_r') or -9)))
    meta = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'Webull get_stock_bars (read-only)',
        'universe': core.UNIVERSE,
        'intraday': {'sessions': len({x.day for v in sess.values() for x in v}),
                     'first': str(min(x.day for v in sess.values() for x in v)),
                     'last': str(max(x.day for v in sess.values() for x in v)),
                     'validate_from': str(c_m5[0]), 'test_from': str(c_m5[1])},
        'daily': {'first_used': str(daily['SPY'].day[200]), 'last': str(daily['SPY'].day[-1]),
                  'validate_from': str(c_d[0]), 'test_from': str(c_d[1])},
        'candidates': len(SETUPS), 'reached_final_exam': K, 'variants_tried_total': variants,
        'random_baseline_r': {'intraday': base_m5, 'daily': base_d},
        'grade_counts': {g: sum(1 for r in rows if r['grade'] == g) for g in order},
        'runtime_s': round(time.time() - t0, 1),
    }
    json.dump({'meta': meta, 'results': rows}, open(os.path.join(HERE, 'results.json'), 'w'), indent=1, default=str)
    for r in rows:
        if 'test' in r:
            T = r['test']
            print(f"{r['grade']:2s} {r['id']:26s} [{r['side']}|{r['filter']}|{r['exit']}] "
                  f"TR {r['train']['n']:4d} {r['train']['avg_r']:+.3f} VA {r['validate'].get('n',0):4d} {r['validate'].get('avg_r',0):+.3f} "
                  f"TE {T.get('n',0):4d} {T.get('avg_r',0):+.3f} pf {T.get('profit_factor')} t {T.get('t_stat')} "
                  f"win {T.get('win_rate')} syms {r['symbols_positive']} conf {r['edge_confidence']} R{r['round']} "
                  + (f"vs-matched {r['test_edge_vs_matched']:+.3f} p {r['p_vs_matched']}" if 'test_edge_vs_matched' in r else ''))
        else:
            print(f"{r['grade']:2s} {r['id']:26s} {r['note']}")
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()
