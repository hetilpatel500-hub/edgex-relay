"""Trade journal: plans, outcomes, and whether the odds came true.

An append-only JSON-lines file (default ./trade-journal.jsonl, or
$TSKIT_JOURNAL). Each plan can carry the time machine's odds at the time
it was made. Outcomes come from you (`close`, with your real fill) or, for
paper trades, from the bars (`settle` replays the rest of the session
against the plan's stop and target, with costs). `report` then checks the
journal's own track record: win rate and R by setup, and calibration of the
recorded odds against what actually happened.
"""
import json, os
from datetime import datetime
from . import data, session, sim, stats, DISCLAIMER


def path(p=None):
    return p or os.environ.get('TSKIT_JOURNAL') or os.path.join(os.getcwd(), 'trade-journal.jsonl')


def _read(p):
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p) if l.strip()]


def _append(p, ev):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    with open(p, 'a') as fh:
        fh.write(json.dumps(ev) + '\n')


def records(p):
    recs = {}
    for ev in _read(p):
        if ev['type'] == 'plan':
            recs[ev['id']] = dict(ev, status='open')
        elif ev['id'] in recs:
            recs[ev['id']].update({k: v for k, v in ev.items() if k not in ('type', 'id')})
            recs[ev['id']]['status'] = 'closed'
    return list(recs.values())


def plan(p, symbol, side, entry, stop, target=None, setup=None, date=None, time=None, tm=None, note=None,
         mode='paper', shares=None):
    symbol = symbol.upper()
    d = 1 if side.lower() in ('long', 'buy') else -1
    entry, stop = float(entry), float(stop)
    if (entry - stop) * d <= 0:
        raise ValueError('stop must be on the losing side of the entry')
    date = date or datetime.now(data.ET).strftime('%Y-%m-%d')
    n = sum(1 for r in records(p) if r['date'] == date and r['symbol'] == symbol) + 1
    ev = {'type': 'plan', 'id': f'{date}-{symbol}-{n}', 'created_at': data.now_utc(), 'mode': mode,
          'symbol': symbol, 'side': 'long' if d == 1 else 'short', 'entry': entry, 'stop': stop,
          'target': None if target is None else float(target), 'setup': setup, 'date': date, 'time_et': time,
          'shares': shares, 'note': note}
    if tm:
        ev['odds_at_plan'] = {'target_first': tm['odds']['target_first'], 'stop_first': tm['odds']['stop_first'],
                              'expected_r': tm.get('expected_r'),
                              'coin_flip_target_first': tm['coin_flip_baseline']['odds']['target_first'],
                              'mode': tm.get('mode'), 'stop_used': tm.get('stop'), 'target_used': tm.get('target')}
    _append(p, ev)
    return ev


def close(p, rid, exit_price, exit_time=None, note=None):
    recs = {r['id']: r for r in records(p)}
    if rid not in recs:
        raise ValueError(f'no plan {rid}')
    r = recs[rid]
    d = 1 if r['side'] == 'long' else -1
    x = float(exit_price)
    R = (x - r['entry']) * d / abs(r['entry'] - r['stop'])
    ev = {'type': 'close', 'id': rid, 'closed_at': data.now_utc(), 'exit': x, 'exit_time_et': exit_time,
          'r': round(R, 3), 'outcome': 'target' if r['target'] is not None and (x - r['target']) * d >= 0 else
          'stop' if (x - r['stop']) * d <= 0 else 'other', 'how': 'manual', 'close_note': note}
    _append(p, ev)
    return ev


def settle(p, store):
    """Replay open paper plans on the bars; record the ones whose session is complete."""
    done, pending = [], []
    for r in records(p):
        if r['status'] != 'open' or r.get('mode') == 'real' or not r.get('time_et'):
            continue
        rows = data.read(store, r['symbol'], 'M5')
        if not rows:
            pending.append({'id': r['id'], 'why': 'no bars in the store'}); continue
        today, full = session.live_session(rows, r['symbol'])
        s = next((x for x in full if str(x.day) == r['date']), None)
        partial = False
        if s is None and today is not None and str(today.day) == r['date']:
            s, partial = today, today.partial
        if s is None:
            pending.append({'id': r['id'], 'why': f"no session for {r['date']} in the store"}); continue
        m = data.parse_et_clock(s.day, r['time_et'])
        ks = [i for i, x in enumerate(s.bars) if x.m + 5 <= m]
        if not ks:
            pending.append({'id': r['id'], 'why': 'entry time is before the first bar closed'}); continue
        d = 1 if r['side'] == 'long' else -1
        res = sim.replay(s.bars, ks[-1] + 1, r['entry'], d, r['stop'], r['target'])
        risk = abs(r['entry'] - r['stop'])
        R = sim.r_multiple(r['entry'], res['exit'], d, risk, session.cost_bps(r['symbol']))
        if partial and res['outcome'] in ('close', 'open'):
            pending.append({'id': r['id'], 'why': 'session still open', 'so_far_r': round(R, 3)}); continue
        ev = {'type': 'settle', 'id': r['id'], 'closed_at': data.now_utc(), 'exit': round(res['exit'], 4),
              'exit_time_et': session.clock(s.bars[res['k']].m + 5), 'outcome': res['outcome'], 'r': round(R, 3),
              'how': 'replayed on bars (paper)'}
        _append(p, ev)
        done.append(ev)
    return {'tool': 'trade-journal', 'action': 'settle', 'settled': done, 'pending': pending}


def report(p, since=None):
    recs = [r for r in records(p) if not since or r['date'] >= since]
    closed = [r for r in recs if r['status'] == 'closed' and r.get('r') is not None]
    rs = [r['r'] for r in sorted(closed, key=lambda r: (r['date'], r.get('time_et') or ''))]
    by = {}
    for r in closed:
        by.setdefault(r.get('setup') or 'manual', []).append(r['r'])
    cal = [r for r in closed if r.get('odds_at_plan') and r.get('outcome') in ('target', 'stop', 'close', 'other')
           and r['odds_at_plan'].get('stop_used') == r['stop'] and r['odds_at_plan'].get('target_used') == r['target']]
    calib = None
    if cal:
        pred = [r['odds_at_plan']['target_first'] for r in cal]
        base = [r['odds_at_plan']['coin_flip_target_first'] for r in cal]
        out = [1 if r['outcome'] == 'target' else 0 for r in cal]
        calib = {'trades': len(cal), 'predicted_target_first_avg': round(sum(pred) / len(pred), 3),
                 'actual_target_first_rate': round(sum(out) / len(out), 3),
                 'actual_90': [round(x, 3) for x in stats.wilson(sum(out), len(out))],
                 'brier_time_machine': round(stats.brier(pred, out), 4), 'brier_coin_flip': round(stats.brier(base, out), 4),
                 'reliability': stats.reliability(pred, out)}
    return {'tool': 'trade-journal', 'action': 'report', 'file': p, 'plans': len(recs),
            'open': sum(r['status'] == 'open' for r in recs), 'closed': len(closed),
            'overall': stats.stats(rs), 'by_setup': {k: stats.stats(v) for k, v in sorted(by.items())},
            'odds_check': calib, 'disclaimer': DISCLAIMER}


def render(r):
    if r.get('action') == 'settle':
        L = [f"JOURNAL SETTLE  {len(r['settled'])} settled, {len(r['pending'])} pending"]
        L += [f"  {e['id']}: {e['outcome']} at {e['exit']} ({e['exit_time_et']} ET), {e['r']:+.2f}R" for e in r['settled']]
        L += [f"  {e['id']}: pending ({e['why']})" for e in r['pending']]
        return '\n'.join(L)
    o = r['overall']
    L = [f"JOURNAL  {r['plans']} plans, {r['open']} open, {r['closed']} closed"]
    if o.get('n'):
        L.append(f"overall: {o['n']} trades, {o['win_rate'] * 100:.0f}% win, {o['avg_r']:+.2f}R avg, {o['total_r']:+.2f}R total, "
                 f"max drawdown {o['max_drawdown_r']}R")
        for k, v in r['by_setup'].items():
            L.append(f"  {k}: {v['n']} trades, {v['win_rate'] * 100:.0f}% win, {v['avg_r']:+.2f}R avg")
    c = r['odds_check']
    if c:
        L.append(f"odds check on {c['trades']} trades: predicted target-first {c['predicted_target_first_avg']:.0%}, "
                 f"actual {c['actual_target_first_rate']:.0%} (90% {c['actual_90'][0]:.0%}-{c['actual_90'][1]:.0%}); "
                 f"Brier {c['brier_time_machine']} vs coin flip {c['brier_coin_flip']} (lower is better)")
    L += ['', r['disclaimer']]
    return '\n'.join(L)
