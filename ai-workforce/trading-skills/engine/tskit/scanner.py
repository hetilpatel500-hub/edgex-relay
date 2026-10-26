"""Chart scanner: run every setup over the latest session of each symbol.

Hits are ranked by the evidence behind each setup on YOUR data (from a
backtest results file, or a quick backtest run on the spot): validated
first, then promising, then the rest, and by out-of-sample t-stat inside
each group. A setup with no evidence is listed as untested, never as a
signal. For a tested setup the hit also shows whether today's bar meets
the setup's validated filter, which side (with or fade) tested best, and
the stop and target its validated exit implies.

`universe` turns saved ranking responses (top gainers/losers, most active)
into a watchlist worth fetching bars for, so the scanner can cover far
more than a fixed list: rank, filter, fetch bars, ingest, scan.
"""
from . import data, session, setups as setups_mod, backtest, sim, DISCLAIMER

ORDER = {'validated': 0, 'promising': 1, 'insufficient': 2, 'rejected': 3, 'retired': 4, 'untested': 5}


def universe(files, min_price=5.0, min_volume=1_000_000, max_symbols=40, exclude=()):
    """Watchlist from saved get_gainers_losers / get_most_active responses."""
    import json
    seen = {}
    for p in files:
        obj = json.load(open(p))
        rows = obj.get('data', obj) if isinstance(obj, dict) else obj
        for r in rows or []:
            sym = str(r.get('symbol', '')).upper()
            if not sym or not sym.replace('.', '').isalpha() or sym in exclude:
                continue
            try:
                px = float(r.get('price') or r.get('close') or 0)
                vol = float(r.get('volume') or 0)
                chg = float(r.get('change_ratio') or 0)
                rv = float(r.get('relative_volume_10d') or 0) or None
            except (TypeError, ValueError):
                continue
            if px < min_price or vol < min_volume:
                continue
            score = abs(chg) * (rv or 1.0)
            if sym not in seen or score > seen[sym]['score']:
                seen[sym] = {'symbol': sym, 'price': px, 'volume': vol, 'change_pct': round(chg * 100, 2),
                             'relative_volume_10d': rv, 'score': round(score, 4), 'source': p.split('/')[-1]}
    out = sorted(seen.values(), key=lambda x: -x['score'])[:max_symbols]
    return {'tool': 'universe', 'generated_at': data.now_utc(), 'filters': {'min_price': min_price,
            'min_volume': min_volume, 'max_symbols': max_symbols}, 'count': len(out), 'symbols': out,
            'next': 'Fetch 5-minute bars for these (get_stock_bars, up to 20 symbols per call), ingest, then scan.'}


def _evidence(results):
    if not results:
        return {}
    return {r['id']: r for r in results.get('results', [])}


def _hit(st_, ev, s, i, d, is_daily, bars_ago):
    r = ev.get(st_['id'])
    status = r['status'] if r else 'untested'
    hit = {'setup': st_['id'], 'name': st_['name'], 'family': st_.get('family'), 'tf': st_['tf'],
           'lean': 'up' if d == 1 else 'down', 'status': status, 'bars_ago': bars_ago}
    if is_daily:
        hit.update(day=str(s.day[i]), close=s.c[i], atr_daily=round(s.atr[i], 4))
        price, atr = s.c[i], s.atr[i]
    else:
        x = s.bars[i]
        hit.update(bar_et=session.clock(x.m), known_at_et=session.clock(x.m + 5), close=x.c, atr_5m=round(s.atr[i], 4),
                   vwap=round(s.vwap[i], 4))
        price, atr = x.c, s.atr[i]
    if r and r.get('side'):
        sgn = 1 if r['side'] == 'with' else -1
        trade = d * sgn
        table = backtest.FILTERS_D if is_daily else backtest.FILTERS
        try:
            met = backtest.passes(r['filter'], table, s, i, d)
        except (IndexError, TypeError):
            met = False
        hit.update(tested_variant=f"{r['side']} · {r['filter']} · {r['exit']}", filter_met=met,
                   trade_direction='long' if trade == 1 else 'short',
                   out_of_sample=r.get('out_of_sample'), luck_check_p=r.get('luck_check_p'),
                   forward=(r.get('forward') or {}).get('verdict'))
        ex = (sim.EXITS_D if is_daily else sim.EXITS).get(r['exit'])
        if ex:
            stop_m, tgt_m = ex[0], ex[1]
            hit['implied_stop'] = round(price - trade * stop_m * atr, 4)
            hit['implied_target'] = None if tgt_m is None else round(price + trade * tgt_m * atr, 4)
            hit['implied_exit_rule'] = r['exit'] + (' (daily ATR, max hold in days)' if is_daily else
                                                    ' (5-minute ATR; flat by the close)')
    return hit


def scan(store, symbols=None, setup_dirs=None, results=None, lookback=3, lookback_days=1, date=None):
    syms = session.ordered(symbols or data.symbols(store, 'M5'))
    stps = setups_mod.load(setup_dirs, store)
    if results is None:
        results = backtest.run(store, setup_dirs, symbols=syms)
    ev = _evidence(results)
    hits, sessions_seen = [], {}
    for sym in syms:
        rows = data.read(store, sym, 'M5')
        if not rows:
            continue
        today, full = session.live_session(rows, sym)
        if date:
            m = [s for s in full if str(s.day) == date]
            today = m[0] if m else None
        if today is None:
            continue
        sessions_seen[sym] = {'session': str(today.day), 'last_bar_et': session.clock(today.bars[-1].m),
                              'partial': today.partial}
        n = len(today.bars)
        for st_ in stps:
            if st_['tf'] != 'M5':
                continue
            for i, d in setups_mod.fires(st_, today, lookback):
                hits.append({'symbol': sym, **_hit(st_, ev, today, i, d, False, n - 1 - i)})
        drows = data.read(store, sym, 'D')
        if drows:
            ser = session.Daily(drows, sym)
            for st_ in stps:
                if st_['tf'] != 'D':
                    continue
                for i, d in setups_mod.fires(st_, ser, lookback_days):
                    hits.append({'symbol': sym, **_hit(st_, ev, ser, i, d, True, len(ser.c) - 1 - i)})
    key = lambda h: (ORDER.get(h['status'], 9), not h.get('filter_met', False),
                     -((h.get('out_of_sample') or {}).get('t_stat') or 0), h['bars_ago'])
    hits.sort(key=key)
    return {'tool': 'chart-scanner', 'generated_at': data.now_utc(), 'store': store, 'symbols_scanned': len(sessions_seen),
            'setups': len(stps), 'lookback_bars': lookback, 'sessions': sessions_seen, 'hits': hits,
            'evidence_from': (results.get('meta') or {}).get('generated_at'),
            'note': 'A hit is a pattern that printed, not a recommendation. Only setups marked validated or '
                    'promising on your own data have any evidence behind them, and only when the filter is met.',
            'disclaimer': DISCLAIMER}


def render(r):
    L = [f"SCANNER  {r['symbols_scanned']} symbols, {r['setups']} setups, last {r['lookback_bars']} bars "
         f"(evidence from backtest {r['evidence_from']})", '']
    if not r['hits']:
        L.append('No setup fired in the window.')
    for h in r['hits']:
        when = h.get('known_at_et') or h.get('day')
        line = f"{h['status']:11s} {h['symbol']:6s} {h['setup']:26s} {h['lean']:4s} at {when} close {h['close']}"
        if h.get('tested_variant'):
            o = h.get('out_of_sample') or {}
            line += (f"  -> {h['trade_direction']} ({h['tested_variant']}; filter {'met' if h['filter_met'] else 'NOT met'}); "
                     f"OOS {o.get('n')} trades {o.get('avg_r', 0):+.2f}R")
            if h.get('implied_stop') is not None:
                line += f"; stop {h['implied_stop']}" + (f" target {h['implied_target']}" if h.get('implied_target') else ' hold')
        L.append(line)
    L += ['', r['note'], r['disclaimer']]
    return '\n'.join(L)
