#!/usr/bin/env python3
"""SPY combined strategies: setups + patterns + volume profile + order flow.
(owner, 2026-09-29: "combine strategies and patterns and market depth &
order flow analytics"). Analysis only: nothing here places, stages or
suggests orders.

WHAT CAN BE TESTED ON HISTORY
  * Volume profile: yes. Each session's profile is rebuilt from 5-minute
    bars (core.profile: each bar's volume spread over its range, 5 bps bins;
    POC and 70% value area), for the prior day and developing today.
  * Time & sales / order flow: only a proxy. Webull returns the last 1,000
    prints and the live book only, and footprint history isn't subscribed.
    The proxy is bar "delta": volume x (close - low - (high - close)) /
    (high - low), i.e. how much of each 5-minute bar's volume closed near its
    high vs its low. Real bid/ask delta can only be tested once tape/ holds
    30+ recorded sessions (the Chart Desk's live tape is recording it).
  * Level II depth: no. There is no book history to test. Forward only.

DATA  ../data_spy: SPY 5-minute RTH bars 2023-09-21 .. 2026-09-28 and daily
      bars 2002-11-25 .. 2026-09-25 (Webull get_stock_bars, read-only).

CANDIDATES (fixed before this run; each counts toward the luck correction on
top of the 34 setups spy_hunt.py graded)
  Daily (11 daily setups from the hunt vote: +1 per long signal, -1 per
  short signal on the same day; the net vote is the score)
    D1  net vote >= 1     D2  net vote >= 2     D3  net vote >= 3
    D4  "vetted" vote: only daily setups that were positive on BOTH train and
        validation in spy_hunt.py (never the test period), net vote >= 1
  Intraday (54 intraday setups from the hunt, pooled; each signal gets a
  confluence score 0-3 in its own direction d)
    vp    price on the d side of the prior day's POC AND today's developing POC
    flow  cumulative bar-delta proxy since the open has sign d AND the last
          6 bars' delta proxy has sign d
    ctx   yesterday's daily close on the d side of its 200-day average
    I0 any signal (reference)   I2 score >= 2   I3 score == 3
  Intraday per-layer check (reported, not graded): average R by score 0..3.

METHOD  Same as spy_hunt.py: 50/25/25 date split with identical cut dates;
side (with/fade), filter (daily: none/sma200) and exit picked on TRAIN only;
one position at a time (intraday: first qualifying signal of each session;
daily: nothing new until the open trade exits); 2 bps costs; matched random
baseline on TEST (same direction, same score/filter condition, same exit,
300 runs); same A+/A/B/C grades; Bonferroni K = 34 + 7.

usage: python3 combo.py        writes results.json and prints the table
"""
import json, math, os, random, sys, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'aplus_hunt'))
import hunt  # noqa: E402  (loads setups, extends filters and exits)
import core, lab  # noqa: E402

core.HERE = os.path.join(hunt.LAB, 'studies', 'data_spy')
core.UNIVERSE = ['SPY']
MIN_TRAIN = 40
PRIOR_K = 34
SPY_RES = os.path.join(HERE, '..', 'aplus_hunt', 'spy_results.json')


# ---- order-flow proxy and volume-profile features --------------------------
def bar_delta(b):
    rng = b.h - b.l
    return b.v * ((b.c - b.l) - (b.h - b.c)) / rng if rng > 0 else 0.0


def attach_flow(s):
    cum, out = 0.0, []
    for b in s.bars:
        cum += bar_delta(b)
        out.append(cum)
    s.cdelta = out


def features(s, i, d):
    b = s.bars
    c = b[i].c
    dev_poc = core.profile(b[:i + 1])[0]
    vp = s.prior is not None and d * (c - s.prior.poc) > 0 and d * (c - dev_poc) > 0
    last6 = s.cdelta[i] - (s.cdelta[i - 6] if i >= 6 else 0.0)
    flow = d * s.cdelta[i] > 0 and d * last6 > 0
    ctx = getattr(s, 'd200', None) == d
    return int(vp), int(flow), int(ctx)


def phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def pick(chosen_fn, conds, exits, c1):
    best = None
    for c in conds:
        for e in exits:
            tr = [x['R'][e] for x in chosen_fn(c, e) if x['day'] < c1]
            if len(tr) < MIN_TRAIN:
                continue
            a = sum(tr) / len(tr)
            if best is None or a > best[0]:
                best = (a, c, e)
    return best


def summarize(name, rules, chosen, e, c1, c2, base_means):
    TR = core.stats([x['R'][e] for x in chosen if x['day'] < c1])
    VA = core.stats([x['R'][e] for x in chosen if c1 <= x['day'] < c2])
    test = [x for x in chosen if x['day'] >= c2]
    TE = core.stats([x['R'][e] for x in test])
    years = {}
    for x in chosen:
        years.setdefault(str(x['day'])[:4], []).append(x['R'][e])
    yq = {y: v for y, v in years.items() if len(v) >= 5}
    mb = sum(base_means) / len(base_means) if base_means else None
    pm = sum(1 for m in base_means if m >= TE.get('avg_r', 0)) / len(base_means) if base_means else None
    return dict(id=name, rules=rules, side=e[0], exit=e[1], train=TR, validate=VA, test=TE,
                matched_baseline=round(mb, 3) if mb is not None else None,
                edge_vs_matched=round(TE['avg_r'] - mb, 3) if mb is not None and TE.get('n') else None,
                p_vs_matched=pm, ypos=sum(1 for v in yq.values() if sum(v) > 0), yn=len(yq),
                by_year={y: round(sum(v) / len(v), 3) for y, v in sorted(years.items())},
                test_trades=[[str(x['day']), round(x['R'][e], 3)] for x in test])


def grade(r, K):
    TR, VA, TE = r['train'], r['validate'], r['test']
    t = TE.get('t_stat') or 0
    p = 1 - phi(t) if TE.get('n', 0) >= 2 else 1.0
    padj = min(1.0, p * K)
    r['p_bonferroni'] = round(padj, 5)
    r['years_positive'] = f"{r['ypos']}/{r['yn']}"
    ok_n = TR.get('n', 0) >= MIN_TRAIN and VA.get('n', 0) >= 30 and TE.get('n', 0) >= 30
    beats = r['edge_vs_matched'] is not None and r['edge_vs_matched'] >= 0.10 and (r['p_vs_matched'] or 1) < 0.05
    if (ok_n and TR['avg_r'] >= 0.05 and VA['avg_r'] >= 0.05 and TE['avg_r'] >= 0.10 and (TE['profit_factor'] or 0) >= 1.3
            and t >= 2.0 and beats and r['yn'] and r['ypos'] >= 0.6 * r['yn'] and padj < 0.05):
        return 'A+'
    if (ok_n and VA.get('avg_r', -1) >= 0.05 and TE.get('avg_r', -1) >= 0.05 and t >= 1.5
            and (TE.get('profit_factor') or 0) >= 1.15 and (r['edge_vs_matched'] or 0) > 0):
        return 'A'
    if VA.get('n', 0) and TE.get('n', 0) and VA['avg_r'] > 0 and TE['avg_r'] > 0:
        return 'B'
    return 'C'


# ---- daily ensembles --------------------------------------------------------
def daily_part(D, rng):
    days = D.day[200:]
    c1, c2 = days[int(len(days) * .5)], days[int(len(days) * .75)]
    dsetups = [s for s in hunt.SETUPS if s['tf'] == 'D']
    prior = {r['id']: r for r in json.load(open(SPY_RES))['results']}
    vetted = [s['id'] for s in dsetups if prior.get(s['id'], {}).get('train', {}).get('avg_r', -1) > 0
              and prior.get(s['id'], {}).get('validate', {}).get('avg_r', -1) > 0]
    votes = {}                       # index -> {setup id: d}
    pos = {d: k for k, d in enumerate(D.day)}
    for st in dsetups:
        for i, d in st['detect'](D):
            if i >= 200 and i + 1 < len(D.c):
                votes.setdefault(i, {})[st['id']] = d
    cands = {
        'D1': ('Daily vote >= 1: at least one more daily setup says long than short (or vice versa).', None, 1),
        'D2': ('Daily vote >= 2: two or more daily setups agree on the same day.', None, 2),
        'D3': ('Daily vote >= 3: three or more daily setups agree on the same day.', None, 3),
        'D4': ('Vetted vote >= 1: only setups positive in train and validation (' + ', '.join(vetted) + ').', vetted, 1),
    }
    exits = [(sd, e) for sd, _ in lab.SIDES for e in core.EXITS_D]
    rows = []
    for cid, (rules, only, k) in cands.items():
        sigs = []
        for i, v in sorted(votes.items()):
            net = sum(d for sid, d in v.items() if only is None or sid in only)
            if abs(net) >= k:
                d = 1 if net > 0 else -1
                sigs.append(dict(i=i, day=D.day[i], d=d, members=sorted(s for s in v if only is None or s in only),
                                 ok={c for c in lab.COMBOS_D if lab.passes(c, lab.FILTERS_D, D, i, d)}))
        cache = {}

        def chosen(c, e, sigs=sigs, cache=cache):
            key = (c, e)
            if key not in cache:
                out, free = [], -1
                for x in sigs:
                    if c not in x['ok'] or x['i'] < free:
                        continue
                    m = 1 if e[0] == 'with' else -1
                    r = core.trade_d(D, x['i'], x['d'] * m, *core.EXITS_D[e[1]])
                    if r is None:
                        continue
                    out.append(dict(x, R={e: r})); free = x['i'] + core.EXITS_D[e[1]][2] + 1
                cache[key] = out
            return cache[key]
        best = pick(chosen, lab.COMBOS_D, exits, c1)
        if best is None:
            rows.append(dict(id=cid, rules=rules, tf='D', grade='C', note='too few training trades')); continue
        _, c, e = best
        ch = chosen(c, e)
        test = [x for x in ch if x['day'] >= c2]
        pool = [k for k, dy in enumerate(D.day) if dy >= c2 and k + 11 < len(D.c)]
        means = []
        sgn = 1 if e[0] == 'with' else -1
        for _ in range(300):
            rs = []
            for x in test:
                for _t in range(20):
                    k2 = rng.choice(pool)
                    if lab.passes(c, lab.FILTERS_D, D, k2, x['d']):
                        v = core.trade_d(D, k2, x['d'] * sgn, *core.EXITS_D[e[1]])
                        if v is not None:
                            rs.append(v)
                        break
            if rs:
                means.append(sum(rs) / len(rs))
        r = summarize(cid, rules, ch, e, c1, c2, means)
        r.update(tf='D', filter=c, signals=len(sigs))
        r['member_counts'] = {}
        for x in ch:
            for m in x['members']:
                r['member_counts'][m] = r['member_counts'].get(m, 0) + 1
        rows.append(r)
    return rows, {'validate_from': str(c1), 'test_from': str(c2), 'vetted': vetted}


# ---- intraday confluence ----------------------------------------------------
def intraday_part(sess, rng):
    days = sorted(s.day for s in sess)
    c1, c2 = days[int(len(days) * .5)], days[int(len(days) * .75)]
    msetups = [s for s in hunt.SETUPS if s['tf'] == 'M5']
    per_sess = {}
    for st in msetups:
        for s in sess:
            for i, d in st['detect'](s):
                per_sess.setdefault(s.day, []).append((i, d, st['id']))
    by_day = {s.day: s for s in sess}
    sigs = []
    for day, lst in per_sess.items():
        s = by_day[day]
        seen = {}
        for i, d, sid in sorted(lst):
            seen.setdefault((i, d), []).append(sid)
        for (i, d), ids in sorted(seen.items()):
            if (i, -d) in seen:
                continue              # setups disagree on the same bar: skip
            rs = {(sd, k): core.trade(s, i, d * m, *v) for sd, m in lab.SIDES for k, v in core.EXITS.items()}
            if None in rs.values():
                continue
            vp, flow, ctx = features(s, i, d)
            sigs.append(dict(day=day, i=i, d=d, ids=ids, R=rs, vp=vp, flow=flow, ctx=ctx, score=vp + flow + ctx))
    sigs.sort(key=lambda x: (x['day'], x['i']))
    exits = [(sd, e) for sd, _ in lab.SIDES for e in core.EXITS]
    # layer check: every signal (not one per session), 'with' side, each exit
    layers = {}
    for e in core.EXITS:
        row = {}
        for sc in range(4):
            sub = [x for x in sigs if x['score'] == sc]
            row[str(sc)] = {p: core.stats([x['R'][('with', e)] for x in sub if f(x['day'])])
                            for p, f in (('train', lambda d: d < c1), ('validate', lambda d: c1 <= d < c2), ('test', lambda d: d >= c2))}
        layers[e] = row
    single = {}
    for name in ('vp', 'flow', 'ctx'):
        single[name] = {str(v): {p: core.stats([x['R'][('with', '1atr/close')] for x in sigs if x[name] == v and f(x['day'])])
                                 for p, f in (('train', lambda d: d < c1), ('validate', lambda d: c1 <= d < c2), ('test', lambda d: d >= c2))}
                        for v in (0, 1)}
    cands = {
        'I0': ('Any intraday setup, first signal of the session (reference, no confluence).', lambda x: True, 0),
        'I2': ('Any intraday setup whose signal has 2 of 3 confluences (volume profile, order-flow proxy, daily 200-day trend).',
               lambda x: x['score'] >= 2, 2),
        'I3': ('Any intraday setup whose signal has all 3 confluences.', lambda x: x['score'] == 3, 3),
    }
    rows = []
    for cid, (rules, cond, need) in cands.items():
        base = [x for x in sigs if cond(x)]
        first, seen = [], set()
        for x in base:
            if x['day'] in seen:
                continue
            seen.add(x['day']); first.append(x)
        best = pick(lambda c, e: first, ['none'], exits, c1)
        if best is None:
            rows.append(dict(id=cid, rules=rules, tf='M5', grade='C', note='too few training trades')); continue
        _, c, e = best
        test = [x for x in first if x['day'] >= c2]
        pool = [s for s in sess if s.day >= c2]
        sgn = 1 if e[0] == 'with' else -1
        means = []
        for _ in range(300):
            rs = []
            for x in test:
                for _t in range(30):
                    s = rng.choice(pool); i = rng.randrange(6, 66)
                    if sum(features(s, i, x['d'])) >= need:
                        v = core.trade(s, i, x['d'] * sgn, *core.EXITS[e[1]])
                        if v is not None:
                            rs.append(v)
                        break
            if rs:
                means.append(sum(rs) / len(rs))
        r = summarize(cid, rules, first, e, c1, c2, means)
        r.update(tf='M5', filter='none', signals=len(base))
        rows.append(r)
    return rows, layers, single, {'validate_from': str(c1), 'test_from': str(c2), 'signals': len(sigs)}


def main():
    t0 = time.time()
    rng = random.Random(23)
    D = core.Daily('SPY')
    sess = core.sessions('SPY')
    hunt.attach_d200({'SPY': sess}, {'SPY': D})
    for s in sess:
        attach_flow(s)
    drows, dmeta = daily_part(D, rng)
    irows, layers, single, imeta = intraday_part(sess, rng)
    rows = drows + irows
    K = PRIOR_K + len(rows)
    for r in rows:
        if 'test' in r:
            r['grade'] = grade(r, K)
    meta = {'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'source': 'Webull get_stock_bars (read-only), SPY only', 'daily': dmeta, 'intraday': imeta,
            'bonferroni_k': K, 'runtime_s': round(time.time() - t0, 1),
            'not_testable': {'level2_depth': 'no book history available; live snapshots only',
                             'time_and_sales': 'last 1,000 prints only; footprint history not subscribed; bar-delta proxy used',
                             'tape_sessions_recorded': len(os.listdir(os.path.join(hunt.LAB, 'tape')))}}
    json.dump({'meta': meta, 'results': rows, 'intraday_layers': layers, 'intraday_single_layer': single},
              open(os.path.join(HERE, 'results.json'), 'w'), indent=1, default=str)
    for r in rows:
        if 'test' not in r:
            print(r['id'], r['note']); continue
        T = r['test']
        print(f"{r['grade']:2s} {r['id']} {r['tf']} [{r['side']}|{r.get('filter')}|{r['exit']}] sig {r['signals']} "
              f"TR {r['train']['n']} {r['train']['avg_r']:+.3f} VA {r['validate'].get('n', 0)} {r['validate'].get('avg_r', 0):+.3f} "
              f"TE {T.get('n', 0)} {T.get('avg_r', 0):+.3f} pf {T.get('profit_factor')} t {T.get('t_stat')} win {T.get('win_rate')} "
              f"base {r['matched_baseline']} vsM {r['edge_vs_matched']} p {r['p_vs_matched']} yrs {r['years_positive']} padj {r['p_bonferroni']}")
    print('\nintraday avg R by confluence score (with side, every signal):')
    for e, row in layers.items():
        print(' ', e, {sc: (v['train'].get('n'), v['train'].get('avg_r'), v['validate'].get('avg_r'), v['test'].get('n'), v['test'].get('avg_r')) for sc, v in row.items()})
    print('single layers (1atr/close):', json.dumps({k: {v: {p: (s.get('n'), s.get('avg_r')) for p, s in d.items()} for v, d in vv.items()} for k, vv in single.items()}))
    print(json.dumps(meta, indent=1))


if __name__ == '__main__':
    main()
