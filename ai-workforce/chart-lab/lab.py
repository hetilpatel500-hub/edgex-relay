#!/usr/bin/env python3
"""Chart Desk lab: backtest every setup in setups/*.py on the Webull bars in data/.

usage: python3 lab.py [--only ID[,ID...]]

Method (the same for every setup, so results compare):
  * A signal is known at a bar's close; the simulated entry is the next bar's
    open. Round-trip costs (2 bps ETFs, 3 bps stocks) come off every trade.
  * Exits are ATR stops/targets (intraday: 5-minute ATR, flat by the close;
    daily: daily ATR with a holding limit). If a bar touches stop and target,
    the stop counts.
  * Every setup is also tested faded (direction flipped). "with" or "fade" is
    chosen on IS like the filter and exit.
  * Dates are split once: the first 70% of dates are in-sample (IS), the last
    30% out-of-sample (OOS). For each setup the lab picks ONE filter and ONE
    exit using IS results only, then reports that single choice on OOS.
  * Status:
      validated     IS avg >= 0.05R and OOS n >= 30, avg >= 0.05R, profit factor
                    >= 1.1, t >= 1.5, and at least half the symbols positive
      promising     IS and OOS both positive, but short of "validated"
      insufficient  fewer than 30 OOS trades
      rejected      anything else
  * Forward test: the first time a setup is validated or promising, its
    side, filter and exit are frozen in frozen.json with the last data date.
    Every day of data after that is a true forward test of that exact
    variant (no re-tuning). A frozen setup is retired when its forward
    results reach 30 trades with an average below -0.05R.
  * The number of variants tried is recorded: the more combinations tested,
    the more likely a good-looking result is luck.

Writes out/results.json and PLAYBOOK.md. Analysis only: nothing here trades.
"""
import glob, importlib.util, json, os, sys, time
from datetime import datetime, timezone
import core

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


def load_setups():
    out = []
    for f in sorted(glob.glob(os.path.join(core.HERE, 'setups', '*.py'))):
        spec = importlib.util.spec_from_file_location(os.path.basename(f)[:-3], f)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        for s in getattr(m, 'SETUPS', []):
            s = dict(s); s.setdefault('tf', 'M5'); s['file'] = os.path.relpath(f, core.HERE)
            out.append(s)
    return out


def passes(combo, table, *a):
    return all(table[f](*a) for f in combo.split('+'))


def signals_m5(setup, sess):
    """[(date, sym, {(side, exit): R}, [filters passed], d)] for one symbol.
    Filters are judged in the setup's own direction d."""
    out = []
    for s in sess:
        for i, d in setup['detect'](s):
            rs = {(sd, k): core.trade(s, i, d * m, *v) for sd, m in SIDES for k, v in core.EXITS.items()}
            if None in rs.values():
                continue
            ok = [c for c in COMBOS if passes(c, FILTERS, s, i, d)]
            out.append((s.day, s.sym, rs, ok, d))
    return out


def signals_d(setup, ser):
    out = []
    for i, d in setup['detect'](ser):
        if i + 1 >= len(ser.c):
            continue
        rs = {(sd, k): core.trade_d(ser, i, d * m, *v) for sd, m in SIDES for k, v in core.EXITS_D.items()}
        if None in rs.values():
            continue
        ok = [c for c in COMBOS_D if passes(c, FILTERS_D, ser, i, d)]
        out.append((ser.day[i], ser.sym, rs, ok, d))
    return out


def evaluate(setup, sigs, cut):
    combos = COMBOS if setup['tf'] == 'M5' else COMBOS_D
    exits = [(sd, e) for sd, _ in SIDES for e in (core.EXITS if setup['tf'] == 'M5' else core.EXITS_D)]
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
    IS, OOS = core.stats(is_r), core.stats(oos_r)
    if OOS['n'] < 30:
        status = 'insufficient'
    elif (IS['avg_r'] >= 0.05 and OOS['avg_r'] >= 0.05 and (OOS['profit_factor'] or 0) >= 1.1
          and (OOS['t_stat'] or 0) >= 1.5 and sym_pos >= len(per_sym) / 2):
        status = 'validated'
    elif IS['avg_r'] > 0 and OOS['avg_r'] > 0:
        status = 'promising'
    else:
        status = 'rejected'
    res.update(status=status, side=side, filter=c, exit=ex, random_baseline_r=BASE.get(ex),
               edge_vs_random_oos=round(OOS['avg_r'] - BASE[ex], 3) if OOS.get('n') and ex in BASE else None,
               in_sample=IS, out_of_sample=OOS,
               longs=core.stats(longs), shorts=core.stats(shorts),
               symbols_positive=f'{sym_pos}/{len(per_sym)}',
               by_symbol={k: round(sum(v), 2) for k, v in sorted(per_sym.items())})
    return res


BASE = {}


def baseline(sess):
    """Average R of random entries (fixed seed) for each intraday exit: what
    trading costs alone do. A setup is only interesting if it beats this."""
    import random
    rnd = random.Random(7)
    rs = {k: [] for k in core.EXITS}
    for v in sess.values():
        for s in v:
            for _ in range(5):
                i, d = rnd.randrange(6, 70), rnd.choice((1, -1))
                for k, e in core.EXITS.items():
                    rs[k].append(core.trade(s, i, d, *e))
    BASE.update({k: round(sum(v) / len(v), 3) for k, v in rs.items()})


FROZEN_PATH = os.path.join(core.HERE, 'frozen.json')


def forward(sigs, fz):
    side, ex = fz['side'], fz['exit']
    rs = [x[2][(side, ex)] for x in sorted(sigs, key=lambda x: x[0])
          if str(x[0]) > fz['frozen_at'] and fz['filter'] in x[3]]
    f = core.stats(rs)
    if f['n'] >= 30 and f['avg_r'] < -0.05:
        f['verdict'] = 'retired'
    elif f['n'] < 20:
        f['verdict'] = 'tracking'
    else:
        f['verdict'] = 'holding' if f['avg_r'] > 0 else 'fading'
    return f


def cutoff(dates):
    ds = sorted(set(dates))
    return ds[int(len(ds) * 0.7)]


def main():
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    setups = [s for s in load_setups() if not only or s['id'] in only]
    t0 = time.time()
    sess = {s: core.sessions(s) for s in core.UNIVERSE}
    daily = {s: core.Daily(s) for s in core.UNIVERSE}
    baseline(sess)
    cut_m5 = cutoff([x.day for v in sess.values() for x in v])
    cut_d = cutoff([d for v in daily.values() for d in v.day])
    frozen = json.load(open(FROZEN_PATH)) if os.path.exists(FROZEN_PATH) else {}
    last_day = {'M5': str(max(x.day for v in sess.values() for x in v)), 'D': str(max(daily['SPY'].day))}
    results = []
    for st in setups:
        if st['tf'] == 'M5':
            sigs = [x for sym in core.UNIVERSE for x in signals_m5(st, sess[sym])]
            r = evaluate(st, sigs, cut_m5)
        else:
            sigs = [x for sym in core.UNIVERSE for x in signals_d(st, daily[sym])]
            r = evaluate(st, sigs, cut_d)
        r.update({k: st[k] for k in ('id', 'name', 'family', 'rules', 'tf', 'file')})
        fz = frozen.get(st['id'])
        if fz is None and r['status'] in ('validated', 'promising') and not only:
            fz = frozen[st['id']] = {'side': r['side'], 'filter': r['filter'], 'exit': r['exit'], 'tf': st['tf'],
                                     'frozen_at': last_day[st['tf']], 'status_at_freeze': r['status'],
                                     'oos_at_freeze': r['out_of_sample']}
        if fz:
            r['frozen'] = fz
            r['forward'] = forward(sigs, fz)
            if r['forward']['verdict'] == 'retired':
                r['status'] = 'retired'
        results.append(r)
        print(f"{st['id']:24s} {r['status']:12s} "
              + (f"IS {r['in_sample']['n']:4d} {r['in_sample']['avg_r']:+.3f}R  OOS {r['out_of_sample']['n']:4d} "
                 f"{r['out_of_sample'].get('avg_r', 0):+.3f}R pf {r['out_of_sample'].get('profit_factor')} "
                 f"t {r['out_of_sample'].get('t_stat')}  [{r['side']} | {r['filter']} | {r['exit']}] syms {r['symbols_positive']}"
                 if 'in_sample' in r else r.get('note', '')))
    m5_days = sorted({x.day for v in sess.values() for x in v})
    meta = {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'source': 'Webull get_stock_bars (read-only), stored in chart-lab/data',
        'universe': core.UNIVERSE,
        'intraday': {'sessions': len(m5_days), 'first': str(m5_days[0]), 'last': str(m5_days[-1]),
                     'oos_from': str(cut_m5)},
        'daily': {'first': str(min(daily['SPY'].day)), 'last': str(max(daily['SPY'].day)), 'oos_from': str(cut_d)},
        'costs_bps_round_trip': {'ETFs': 2, 'stocks': 3},
        'random_entry_baseline_r': BASE,
        'variants_tried_total': sum(r['variants_tried'] for r in results),
        'runtime_s': round(time.time() - t0, 1),
    }
    os.makedirs(os.path.join(core.HERE, 'out'), exist_ok=True)
    if only:
        print(json.dumps(meta, indent=1)); return
    json.dump(frozen, open(FROZEN_PATH, 'w'), indent=1, default=str)
    json.dump({'meta': meta, 'results': results}, open(os.path.join(core.HERE, 'out', 'results.json'), 'w'), indent=1, default=str)
    write_playbook(meta, results)
    print(json.dumps(meta, indent=1))


def fmt(s):
    if not s or not s.get('n'):
        return '0 trades'
    return f"{s['n']} trades, {s['win_rate']*100:.0f}% win, {s['avg_r']:+.2f}R avg, PF {s['profit_factor']}, t {s['t_stat']}"


def write_playbook(meta, results):
    order = {'validated': 0, 'promising': 1, 'insufficient': 2, 'rejected': 3, 'retired': 4}
    L = ['# Chart Desk playbook (generated by lab.py, do not edit by hand)', '',
         f"Generated {meta['generated_at']} from Webull bars. Intraday: {meta['intraday']['sessions']} sessions, "
         f"{meta['intraday']['first']} to {meta['intraday']['last']}, out-of-sample from {meta['intraday']['oos_from']}. "
         f"Daily: {meta['daily']['first']} to {meta['daily']['last']}, out-of-sample from {meta['daily']['oos_from']}. "
         f"Costs: 2 bps (ETFs) / 3 bps (stocks) round trip. Variants tried in total: {meta['variants_tried_total']}.", '',
         'Past results are not a promise about the future. These are research notes for the desk\'s commentary; '
         'Edgex never places trades and nothing here is advice to buy or sell.', '',
         'Random entries lose about the cost of trading: ' + ', '.join(f'{k} {v:+.2f}R' for k, v in meta['random_entry_baseline_r'].items())
         + ' (intraday). A setup has to beat that, not just zero, to be worth anything.', '',
         '| Status | Setup | Side · filter · exit | In-sample | Out-of-sample | Symbols + |', '|---|---|---|---|---|---|']
    for r in sorted(results, key=lambda r: (order[r['status']], -(r.get('out_of_sample', {}).get('avg_r') or -9))):
        if 'in_sample' not in r:
            L.append(f"| {r['status']} | {r['name']} ({r['id']}) | - | {r.get('note','')} | - | - |")
            continue
        L.append(f"| {r['status']} | {r['name']} ({r['id']}) | {r['side']} · {r['filter']} · {r['exit']} | {fmt(r['in_sample'])} | "
                 f"{fmt(r['out_of_sample'])} | {r['symbols_positive']} |")
    fz = [r for r in results if r.get('frozen')]
    if fz:
        L += ['', '## Forward test (frozen variants, no re-tuning after the freeze date)', '',
              '| Setup | Frozen | Variant | Forward since freeze | Verdict |', '|---|---|---|---|---|']
        for r in fz:
            f = r['frozen']
            L.append(f"| {r['id']} | {f['frozen_at']} | {f['side']} · {f['filter']} · {f['exit']} | {fmt(r['forward'])} | {r['forward']['verdict']} |")
    L += ['', '## Rules', '']
    for r in results:
        L.append(f"- **{r['id']}** ({r['family']}, {r['tf']}): {r['rules']}")
    L += ['', 'Filters: vwap = on the trade side of VWAP; rvol = 1.3x normal volume for the time of day; '
          "ppoc = beyond yesterday's POC in the trade direction; trend = the structure trend agrees; "
          'sma200 = daily close on the trade side of the 200-day average.', '']
    open(os.path.join(core.HERE, 'PLAYBOOK.md'), 'w').write('\n'.join(L))


if __name__ == '__main__':
    main()
