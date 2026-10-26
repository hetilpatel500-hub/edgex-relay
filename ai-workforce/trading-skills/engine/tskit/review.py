"""Daily review: what happened today, measured, not narrated.

  1. the market (market-context for the day);
  2. the scanner's hits of the day, replayed to the close with each tested
     setup's own exit: did they work? (from scanner JSON files saved during
     the day);
  3. the journal: plans made today and their outcomes (paper plans are
     settled on the bars first);
  4. setups whose status or forward-test verdict changed since the previous
     backtest results file;
  5. the journal's running odds check.
"""
import json
from . import data, session, sim, context as ctx_mod, journal as jr, DISCLAIMER


def _latest_day(store):
    days = [data.last_session_date(store, s) for s in data.symbols(store, 'M5')]
    days = [d for d in days if d]
    return str(max(days)) if days else None


def settle_hits(store, scans, date):
    out = []
    for p in scans:
        sj = json.load(open(p))
        for h in sj.get('hits', []):
            if h.get('tf') != 'M5' or h.get('implied_stop') is None or not h.get('known_at_et'):
                continue
            rows = data.read(store, h['symbol'], 'M5')
            today, full = session.live_session(rows, h['symbol'])
            s = next((x for x in full if str(x.day) == date), None)
            if s is None:
                continue
            m = data.parse_et_clock(s.day, h['known_at_et'])
            ks = [i for i, x in enumerate(s.bars) if x.m + 5 == m]
            if not ks:
                continue
            k = ks[0]
            d = 1 if h['trade_direction'] == 'long' else -1
            e = s.bars[k + 1].o if k + 1 < len(s.bars) else s.bars[k].c
            res = sim.replay(s.bars, k + 1, e, d, h['implied_stop'], h.get('implied_target'))
            risk = abs(e - h['implied_stop'])
            key = (h['symbol'], h['setup'], h['known_at_et'])
            if risk <= 0 or key in {(x['symbol'], x['setup'], x['time_et']) for x in out}:
                continue
            out.append({'symbol': h['symbol'], 'setup': h['setup'], 'status': h['status'], 'time_et': h['known_at_et'],
                        'direction': h['trade_direction'], 'filter_met': h.get('filter_met'), 'outcome': res['outcome'],
                        'r': round(sim.r_multiple(e, res['exit'], d, risk, session.cost_bps(h['symbol'])), 3)})
    return out


def changes(results, previous):
    if not results or not previous:
        return []
    a = {r['id']: r for r in previous.get('results', [])}
    out = []
    for r in results.get('results', []):
        p = a.get(r['id'])
        if p is None:
            out.append({'setup': r['id'], 'change': f"new, {r['status']}"}); continue
        if p['status'] != r['status']:
            out.append({'setup': r['id'], 'change': f"{p['status']} -> {r['status']}"})
        fa, fb = (p.get('forward') or {}).get('verdict'), (r.get('forward') or {}).get('verdict')
        if fb and fa != fb:
            out.append({'setup': r['id'], 'change': f"forward test {fa or 'none'} -> {fb}"})
    return out


def review(store, date=None, journal=None, scans=(), results=None, previous=None, sectors=None):
    date = date or _latest_day(store)
    ctx = ctx_mod.context(store, sectors=sectors, date=date)
    hits = settle_hits(store, scans, date) if scans else []
    jnl = None
    if journal:
        st_ = jr.settle(journal, store)
        recs = [r for r in jr.records(journal) if r['date'] == date]
        jnl = {'settled_now': len(st_['settled']), 'today': recs, 'report': jr.report(journal)}
    tested = [h for h in hits if h['status'] in ('validated', 'promising') and h['filter_met']]
    return {'tool': 'daily-review', 'generated_at': data.now_utc(), 'date': date, 'market': ctx,
            'scanner_hits_replayed': hits,
            'tested_hits_summary': {'n': len(tested), 'avg_r': round(sum(h['r'] for h in tested) / len(tested), 3) if tested else None,
                                    'wins': sum(h['r'] > 0 for h in tested)},
            'journal': jnl, 'setup_changes': changes(results, previous), 'disclaimer': DISCLAIMER}


def render(r):
    L = [f"# Daily review {r['date']}", '', f"## Market: {r['market']['regime']}"]
    L += [f"- {f}" for f in r['market']['facts']]
    L += ['', '## Scanner hits, replayed to the close']
    if r['scanner_hits_replayed']:
        for h in r['scanner_hits_replayed']:
            L.append(f"- {h['time_et']} {h['symbol']} {h['setup']} ({h['status']}{'' if h['filter_met'] else ', filter not met'}) "
                     f"{h['direction']}: {h['outcome']}, {h['r']:+.2f}R")
        t = r['tested_hits_summary']
        if t['n']:
            L.append(f"- tested hits with the filter met: {t['n']}, {t['wins']} winners, {t['avg_r']:+.2f}R average")
    else:
        L.append('- no saved scanner output for this day')
    if r['journal']:
        L += ['', '## Journal']
        for x in r['journal']['today']:
            L.append(f"- {x['id']} {x['side']} {x['symbol']} at {x['entry']}: " +
                     (f"{x.get('outcome')} {x.get('r', 0):+.2f}R" if x['status'] == 'closed' else 'open'))
        rep = r['journal']['report']
        if rep['overall'].get('n'):
            o = rep['overall']
            L.append(f"- running: {o['n']} trades, {o['win_rate'] * 100:.0f}% win, {o['avg_r']:+.2f}R avg")
        if rep.get('odds_check'):
            c = rep['odds_check']
            L.append(f"- odds check: predicted {c['predicted_target_first_avg']:.0%} target-first, actual "
                     f"{c['actual_target_first_rate']:.0%} over {c['trades']} trades")
    if r['setup_changes']:
        L += ['', '## Setup changes'] + [f"- {c['setup']}: {c['change']}" for c in r['setup_changes']]
    L += ['', r['disclaimer']]
    return '\n'.join(L)
