"""Exit planner: try many stop/target pairs through the time machine.

For one entry it tests a grid of stops (in 5-minute ATRs) against targets
(in R, plus "hold to the close"), and stops/targets placed at the session's
own levels (VWAP, the protected swing, the opening range and initial
balance, yesterday's high/low/close, the day's extremes so far). Every pair
runs on the same history (past days at this clock time, or a setup's past
signals with --setup), next to its coin-flip baseline.

The grid's expected results are smoothed over neighbouring cells before
ranking, so one lucky cell can't win on noise alone. If no plan has a
positive expected result after costs, it says so instead of picking the
least-bad one.
"""
from . import data, session, timemachine as tm, DISCLAIMER

STOPS_ATR = (0.5, 0.75, 1.0, 1.5, 2.0)
TARGETS_R = (1.0, 1.5, 2.0, 3.0, None)


def _levels(s, k, e, d, A):
    b = s.bars[:k + 1]
    lv = {'vwap': s.vwap[k], 'vwap+1sd': s.vwap[k] + s.vsd[k], 'vwap-1sd': s.vwap[k] - s.vsd[k],
          'vwap+2sd': s.vwap[k] + 2 * s.vsd[k], 'vwap-2sd': s.vwap[k] - 2 * s.vsd[k],
          'day_high': max(x.h for x in b), 'day_low': min(x.l for x in b),
          'or_high': s.or_hi if k >= 2 else None, 'or_low': s.or_lo if k >= 2 else None,
          'ib_high': s.ib_hi if k >= 11 else None, 'ib_low': s.ib_lo if k >= 11 else None,
          'protected_swing': s.prot[k]}
    if s.prior is not None:
        lv.update(prior_high=s.prior.hi, prior_low=s.prior.lo, prior_close=s.prior.close)
    stops, tgts = [], []
    for name, p in lv.items():
        if p is None:
            continue
        dist = (e - p) * d          # > 0: level is on the stop side
        if 0.3 * A <= dist <= 4 * A:
            stops.append((f'beyond {name}', p - d * 0.1 * A))
        if -dist >= 0.5 * A:
            tgts.append((f'at {name}', p))
    return stops, tgts


def plan(store, symbol, side, entry=None, date=None, time=None, pool='all', condition='none', paths=2000,
         seed=7, cost=None, levels=True, setup=None, setup_side=None, setup_filter=None, setup_dirs=None, results=None):
    symbol = symbol.upper()
    d = {'long': 1, 'buy': 1, 'short': -1, 'sell': -1}[side.lower()]
    today, k, full = tm.locate(store, symbol, date, time)
    A = today.atr[k]
    e = float(entry) if entry is not None else today.bars[k].c
    syms = tm._pool_syms(store, symbol, pool)
    lib = []
    for s in syms:
        ss = full if s == symbol else session.sessions(data.read(store, s, 'M5'), s)
        lib += [x for x in ss if x.day < today.day]
    cb = session.cost_bps(symbol, cost)
    if setup:
        sigs, sside, sfilt = tm.setup_signals(store, setup, today.day, syms, setup_side, setup_filter, setup_dirs, results)
        if len(sigs) < 10:
            raise ValueError(f'{setup} has only {len(sigs)} past signals in the store; too few to replay')
        memory = {'setup': setup, 'setup_side': sside, 'setup_filter': sfilt, 'signals': len(sigs)}
    else:
        prep = tm.prepare(lib, today, k, d, condition)
        memory = {'past_days': len(prep.pool), 'conditioning': condition}

    def one(stop, tgt, label_s, label_t):
        risk = (e - stop) * d
        if setup:
            x = tm.run_setup(sigs, k, e, d, stop, tgt, A, 0, seed, cb)
            er, eb = x['expected_r'], x['coin_flip_baseline']['expected_r']
            pt, ps = x['odds']['target_first'], x['odds']['stop_first']
        else:
            m = tm.simulate(prep.pool, k, e, d, stop, tgt, A, paths, tm.BLOCK, seed, False, cb)
            b = tm.simulate(prep.pool, k, e, d, stop, tgt, A, paths, tm.BLOCK, seed + 1, True, cb)
            er, eb = sum(m['rs']) / paths, sum(b['rs']) / paths
            pt, ps = m['cnt']['target'] / paths, m['cnt']['stop'] / paths
        return {'stop': round(stop, 4), 'stop_rule': label_s, 'stop_atr': round(risk / A, 2),
                'target': None if tgt is None else round(tgt, 4), 'target_rule': label_t,
                'target_r': None if tgt is None else round(abs(tgt - e) / risk, 2),
                'target_first': round(pt, 3), 'stop_first': round(ps, 3),
                'expected_r': round(er, 3), 'coin_flip_expected_r': round(eb, 3), 'edge_r': round(er - eb, 3)}

    grid = {}
    for sa in STOPS_ATR:
        stop = e - d * sa * A
        for tr in TARGETS_R:
            tgt = None if tr is None else e + d * tr * sa * A
            grid[(sa, tr)] = one(stop, tgt, f'{sa} ATR', 'hold to close' if tr is None else f'{tr}R')
    si, ti = list(STOPS_ATR), list(TARGETS_R)
    for (sa, tr), cell in grid.items():
        a, b = si.index(sa), ti.index(tr)
        nb = [grid[(si[x], ti[y])]['expected_r'] for x in (a - 1, a, a + 1) for y in (b - 1, b, b + 1)
              if 0 <= x < len(si) and 0 <= y < len(ti)]
        cell['smoothed_expected_r'] = round(sum(nb) / len(nb), 3)
    lvl = []
    if levels:
        ls, lt = _levels(today, k, e, d, A)
        for name, stop in ls:
            for tname, tgt in lt + [('2R', None), ('hold to close', None)]:
                risk = (e - stop) * d
                t = e + d * 2 * risk if tname == '2R' else tgt
                if t is not None and abs(t - e) / risk < 0.5:
                    continue
                c = one(stop, t, name, tname)
                c['smoothed_expected_r'] = c['expected_r']
                lvl.append(c)
    cands = list(grid.values()) + lvl
    ranked = sorted(cands, key=lambda c: -c['smoothed_expected_r'])
    best = ranked[0]
    positive = [c for c in ranked if c['smoothed_expected_r'] > 0 and c['expected_r'] > 0]
    bs, bt = best['stop'], best['target']
    if setup:
        rng = tm.run_setup(sigs, k, e, d, bs, bt, A, 2000, seed, cb)['expected_r_range_90']
    else:
        rng = tm.run(prep, e, d, bs, bt, A, paths=1000, seed=seed, boot=30, boot_paths=300, cost_bps=cb)['expected_r_range_90']
    best['expected_r_range_90'] = rng
    rep = {
        'tool': 'exit-planner', 'generated_at': data.now_utc(), 'symbol': symbol,
        'side': 'long' if d == 1 else 'short', 'session': str(today.day),
        'entry_time_et': session.clock(today.bars[k].m + 5), 'entry': round(e, 4), 'atr_5m': round(A, 4),
        'memory': memory, 'paths_per_plan': None if setup else paths, 'plans_tested': len(cands),
        'grid_expected_r': {f'{sa} ATR stop': {('close' if tr is None else f'{tr}R'): grid[(sa, tr)]['expected_r']
                                               for tr in TARGETS_R} for sa in STOPS_ATR},
        'top_plans': ranked[:5],
        'verdict': ('positive' if positive else 'no_positive_plan'),
        'summary': (f"Best by smoothed expected result: stop {best['stop']} ({best['stop_rule']}), target "
                    f"{best['target'] if best['target'] is not None else 'hold to close'} ({best['target_rule']}): "
                    f"{best['expected_r']:+.2f}R expected (90% range {rng[0]:+.2f} to {rng[1]:+.2f}) vs "
                    f"{best['coin_flip_expected_r']:+.2f}R for a coin flip. It is the best of {len(cands)} plans "
                    f"tried on the same history, so expect less in the future."
                    if positive else
                    f"None of the {len(cands)} exit plans has a positive expected result after costs in this history. "
                    "The history says this entry has no edge as it stands; the exit choice only trades win rate for "
                    "payoff."),
        'disclaimer': DISCLAIMER,
    }
    return rep


def render(r):
    m = r['memory']
    mem = (f"{m['signals']} past signals of {m['setup']}" if 'setup' in m else
           f"{r['paths_per_plan']} paths each on {m['past_days']} past days")
    L = [f"EXIT PLANNER  {r['symbol']} {r['side']} at {r['entry']} ({r['entry_time_et']} ET, {r['session']}), "
         f"{r['plans_tested']} plans, {mem}", '',
         'expected R by stop (rows) and target (columns):']
    cols = list(next(iter(r['grid_expected_r'].values())).keys())
    L.append(f"{'':>14}" + ''.join(f'{c:>8}' for c in cols))
    for row, v in r['grid_expected_r'].items():
        L.append(f'{row:>14}' + ''.join(f'{v[c]:>+8.2f}' for c in cols))
    L += ['', 'top plans:']
    for c in r['top_plans']:
        L.append(f"  stop {c['stop']} ({c['stop_rule']}, {c['stop_atr']} ATR)  target "
                 f"{c['target'] if c['target'] is not None else 'close'} ({c['target_rule']})  "
                 f"target first {c['target_first'] * 100:.0f}%  stop first {c['stop_first'] * 100:.0f}%  "
                 f"expected {c['expected_r']:+.2f}R  (coin flip {c['coin_flip_expected_r']:+.2f}R)")
    L += ['', r['summary'], '', r['disclaimer']]
    return '\n'.join(L)
