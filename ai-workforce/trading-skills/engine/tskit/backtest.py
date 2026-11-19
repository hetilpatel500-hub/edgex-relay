"""Backtester: the Edgex chart lab's method, plus two luck checks.

Same rules for every setup, so results compare:
  * a signal is known at a bar's close; the simulated entry is the next
    bar's open; round-trip costs (2 bps ETFs, 3 bps stocks by default) come
    off every trade;
  * exits are ATR stops/targets (intraday: 5-minute ATR, flat by the close;
    daily: daily ATR with a holding limit); stop first if a bar touches both;
  * every setup is also tested faded (direction flipped);
  * dates are split once: the first 70% in-sample (IS), the last 30%
    out-of-sample (OOS). ONE filter, ONE exit and the side are chosen on IS
    only, then reported on OOS;
  * status: validated (IS avg >= 0.05R; OOS n >= 30, avg >= 0.05R, profit
    factor >= 1.1, t >= 1.5, at least half the symbols positive), promising
    (IS and OOS both positive), insufficient (< 30 OOS trades), rejected;
  * forward test: the first time a setup is validated or promising, its
    side, filter and exit are frozen with the last data date; every later
    day is a true forward test; retired at 30 forward trades averaging
    below -0.05R.
Added here:
  * luck check: how often random entries, with the same exit and the same
    number of trades, average at least as well as the setup did out of
    sample (a p-value against pure chance);
  * equity shuffle: the spread of drawdowns if the same OOS trades had come
    in a different order.
"""
import json, os, random, time
from . import data, session, sim, stats, setups as setups_mod, DISCLAIMER

FILTERS = {
    'none': lambda s, i, d: True,
    'vwap': lambda s, i, d: d * (s.bars[i].c - s.vwap[i]) > 0,
    'rvol': lambda s, i, d: (s.rvol[i] or 0) >= 1.3,
    'ppoc': lambda s, i, d: s.prior is not None and d * (s.bars[i].c - s.prior.poc) > 0,
    'trend': lambda s, i, d: s.trend[i] == d,
}
COMBOS = ['none', 'vwap', 'rvol', 'ppoc', 'trend', 'vwap+rvol', 'vwap+trend', 'rvol+trend', 'vwap+ppoc']
FILTERS_D = {
    'none': lambda r, i, d: True,
    'sma200': lambda r, i, d: r.sma200[i] is not None and d * (r.c[i] - r.sma200[i]) > 0,
}
COMBOS_D = ['none', 'sma200']
MIN_IS = 30
SIDES = [('with', 1), ('fade', -1)]


def passes(combo, table, *a):
    return all(table[f](*a) for f in combo.split('+'))


def signals_m5(setup, sess, cost):
    out = []
    for s in sess:
        for i, d in setups_mod.fires(setup, s):
            rs = {(sd, k): sim.trade(s, i, d * m, *v, cost) for sd, m in SIDES for k, v in sim.EXITS.items()}
            if None in rs.values():
                continue
            ok = [c for c in COMBOS if passes(c, FILTERS, s, i, d)]
            out.append((s.day, s.sym, rs, ok, d, i))
    return out


def signals_d(setup, ser, cost):
    out = []
    for i, d in setups_mod.fires(setup, ser):
        if i + 1 >= len(ser.c):
            continue
        rs = {(sd, k): sim.trade_d(ser, i, d * m, *v, cost) for sd, m in SIDES for k, v in sim.EXITS_D.items()}
        if None in rs.values():
            continue
        ok = [c for c in COMBOS_D if passes(c, FILTERS_D, ser, i, d)]
        out.append((ser.day[i], ser.sym, rs, ok, d, i))
    return out


def cutoff(dates):
    ds = sorted(set(dates))
    return ds[int(len(ds) * 0.7)]


def baseline(sess):
    """R of random entries (fixed seed) for each intraday exit."""
    rnd = random.Random(7)
    rs = {k: [] for k in sim.EXITS}
    for sym, v in sess.items():
        cost = session.cost_bps(sym)
        for s in v:
            for _ in range(5):
                i, d = rnd.randrange(6, 70), rnd.choice((1, -1))
                for k, e in sim.EXITS.items():
                    rs[k].append(sim.trade(s, i, d, *e, cost))
    return rs


def evaluate(setup, sigs, cut, base_avg, base_pool):
    m5 = setup['tf'] == 'M5'
    combos = COMBOS if m5 else COMBOS_D
    exits = [(sd, e) for sd, _ in SIDES for e in (sim.EXITS if m5 else sim.EXITS_D)]
    best = None
    for c in combos:
        for e in exits:
            rs = [x[2][e] for x in sigs if x[0] < cut and c in x[3]]
            if len(rs) < MIN_IS:
                continue
            avg = sum(rs) / len(rs)
            if best is None or avg > best[0]:
                best = (avg, c, e)
    res = {'variants_tried': len(combos) * len(exits), 'signals_total': len(sigs)}
    if best is None:
        res.update(status='insufficient', note=f'fewer than {MIN_IS} in-sample signals for every variant')
        return res
    _, c, e = best
    side, ex = e
    chosen = sorted([x for x in sigs if c in x[3]], key=lambda x: x[0])
    is_r = [x[2][e] for x in chosen if x[0] < cut]
    oos_r = [x[2][e] for x in chosen if x[0] >= cut]
    per_sym = {}
    for x in chosen:
        per_sym.setdefault(x[1], []).append(x[2][e])
    sym_pos = sum(1 for v in per_sym.values() if sum(v) > 0)
    sgn = 1 if side == 'with' else -1
    longs = [x[2][e] for x in chosen if x[4] * sgn == 1]
    shorts = [x[2][e] for x in chosen if x[4] * sgn == -1]
    IS, OOS = stats.stats(is_r), stats.stats(oos_r)
    if OOS['n'] < 30:
        status = 'insufficient'
    elif (IS['avg_r'] >= 0.05 and OOS['avg_r'] >= 0.05 and (OOS['profit_factor'] or 0) >= 1.1
          and (OOS['t_stat'] or 0) >= 1.5 and sym_pos >= len(per_sym) / 2):
        status = 'validated'
    elif IS['avg_r'] > 0 and OOS['avg_r'] > 0:
        status = 'promising'
    else:
        status = 'rejected'
    res.update(status=status, side=side, filter=c, exit=ex, random_baseline_r=base_avg.get(ex),
               edge_vs_random_oos=round(OOS['avg_r'] - base_avg[ex], 3) if OOS.get('n') and ex in base_avg else None,
               in_sample=IS, out_of_sample=OOS,
               longs=stats.stats(longs), shorts=stats.stats(shorts),
               symbols_positive=f'{sym_pos}/{len(per_sym)}',
               by_symbol={k: round(sum(v), 2) for k, v in sorted(per_sym.items())})
    if OOS.get('n'):
        if ex in base_pool:
            res['luck_check_p'] = stats.luck_check(OOS['avg_r'], OOS['n'], base_pool[ex])
        res['equity_shuffle_oos'] = stats.equity_mc(oos_r)
    return res


def forward(sigs, fz):
    side, ex = fz['side'], fz['exit']
    rs = [x[2][(side, ex)] for x in sorted(sigs, key=lambda x: x[0])
          if str(x[0]) > fz['frozen_at'] and fz['filter'] in x[3]]
    f = stats.stats(rs)
    if f['n'] >= 30 and f['avg_r'] < -0.05:
        f['verdict'] = 'retired'
    elif f['n'] < 20:
        f['verdict'] = 'tracking'
    else:
        f['verdict'] = 'holding' if f['avg_r'] > 0 else 'fading'
    return f


def run(store, setup_dirs=None, only=None, symbols=None, frozen_path=None, out_path=None, freeze=True):
    t0 = time.time()
    syms = session.ordered(symbols or data.symbols(store, 'M5'))
    stps = setups_mod.load(setup_dirs, store, set(only) if only else None)
    sess = {s: session.sessions(data.read(store, s, 'M5'), s) for s in syms}
    sess = {s: v for s, v in sess.items() if v}
    daily = {s: session.Daily(data.read(store, s, 'D'), s) for s in syms if s in data.symbols(store, 'D')}
    if not sess:
        raise ValueError(f'no full 5-minute sessions in {store}')
    pool = baseline(sess)
    base_avg = {k: round(sum(v) / len(v), 3) for k, v in pool.items()}
    cut_m5 = cutoff([x.day for v in sess.values() for x in v])
    cut_d = cutoff([d for v in daily.values() for d in v.day]) if daily else None
    frozen = json.load(open(frozen_path)) if frozen_path and os.path.exists(frozen_path) else {}
    last_day = {'M5': str(max(x.day for v in sess.values() for x in v)),
                'D': str(max(max(v.day) for v in daily.values())) if daily else None}
    results = []
    for st_ in stps:
        if st_['tf'] == 'M5':
            sigs = [x for sym, v in sess.items() for x in signals_m5(st_, v, session.cost_bps(sym))]
            r = evaluate(st_, sigs, cut_m5, base_avg, pool)
        else:
            if not daily:
                continue
            sigs = [x for sym, ser in daily.items() for x in signals_d(st_, ser, session.cost_bps(sym))]
            r = evaluate(st_, sigs, cut_d, {}, {})
        r.update({k: st_.get(k) for k in ('id', 'name', 'family', 'rules', 'tf', 'file')})
        fz = frozen.get(st_['id'])
        if fz is None and freeze and frozen_path and r['status'] in ('validated', 'promising'):
            fz = frozen[st_['id']] = {'side': r['side'], 'filter': r['filter'], 'exit': r['exit'], 'tf': st_['tf'],
                                      'frozen_at': last_day[st_['tf']], 'status_at_freeze': r['status'],
                                      'oos_at_freeze': r['out_of_sample']}
        if fz:
            r['frozen'] = fz
            r['forward'] = forward(sigs, fz)
            if r['forward']['verdict'] == 'retired':
                r['status'] = 'retired'
        results.append(r)
    days = sorted({x.day for v in sess.values() for x in v})
    meta = {
        'generated_at': data.now_utc(), 'store': os.path.abspath(store), 'symbols': sorted(sess),
        'intraday': {'sessions': len(days), 'first': str(days[0]), 'last': str(days[-1]), 'oos_from': str(cut_m5)},
        'daily': ({'first': str(min(min(v.day) for v in daily.values())), 'last': last_day['D'], 'oos_from': str(cut_d)}
                  if daily else None),
        'random_entry_baseline_r': base_avg,
        'variants_tried_total': sum(r['variants_tried'] for r in results),
        'runtime_s': round(time.time() - t0, 1),
        'disclaimer': DISCLAIMER,
    }
    if frozen_path and freeze:
        json.dump(frozen, open(frozen_path, 'w'), indent=1, default=str)
    out = {'meta': meta, 'results': results}
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        json.dump(out, open(out_path, 'w'), indent=1, default=str)
    return out


def fmt(s):
    if not s or not s.get('n'):
        return '0 trades'
    return f"{s['n']} trades, {s['win_rate']*100:.0f}% win, {s['avg_r']:+.2f}R avg, PF {s['profit_factor']}, t {s['t_stat']}"


def render(out):
    m = out['meta']
    order = {'validated': 0, 'promising': 1, 'insufficient': 2, 'rejected': 3, 'retired': 4}
    L = [f"BACKTEST  {m['intraday']['sessions']} sessions {m['intraday']['first']} to {m['intraday']['last']} "
         f"(out-of-sample from {m['intraday']['oos_from']}), {len(m['symbols'])} symbols, "
         f"{m['variants_tried_total']} variants tried", '',
         'Random entries: ' + ', '.join(f'{k} {v:+.2f}R' for k, v in m['random_entry_baseline_r'].items()), '']
    for r in sorted(out['results'], key=lambda r: (order[r['status']], -(r.get('out_of_sample', {}).get('avg_r') or -9))):
        if 'in_sample' not in r:
            L.append(f"{r['status']:12s} {r['id']}: {r.get('note', '')}")
            continue
        line = (f"{r['status']:12s} {r['id']}  [{r['side']} | {r['filter']} | {r['exit']}]  "
                f"IS: {fmt(r['in_sample'])}  OOS: {fmt(r['out_of_sample'])}  symbols+ {r['symbols_positive']}")
        if r.get('luck_check_p') is not None:
            line += f"  luck p={r['luck_check_p']}"
        if r.get('forward'):
            line += f"  forward: {fmt(r['forward'])} ({r['forward']['verdict']})"
        L.append(line)
    L += ['', 'luck p = share of random-entry samples (same exit, same trade count) that did at least as well '
              'out of sample. Under 0.05 means luck rarely looks this good; it is still not a guarantee.',
          'The more variants tried, the more likely the best one is luck.', '', m['disclaimer']]
    return '\n'.join(L)
