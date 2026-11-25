"""Market context: what the index ETFs and the rest of the store are doing.

For SPY, QQQ, IWM and DIA (whichever are in the store): change on the day,
side of VWAP, intraday structure trend, today's range against the daily
ATR, the daily trend (50- and 200-day averages) and where 20-day realised
volatility sits in its past year. Breadth comes from every symbol in the
store (how many are above VWAP and up on the day) and, if saved, from a
get_market_sectors response (advancers vs decliners, best and worst
sectors). The regime label is a plain summary of those facts.
"""
import json, math
from . import data, session, stats, DISCLAIMER

INDEXES = ('SPY', 'QQQ', 'IWM', 'DIA')


def _realised_vol(c, n=20):
    rets = [math.log(c[i] / c[i - 1]) for i in range(1, len(c))]
    out = []
    for i in range(n, len(rets) + 1):
        w = rets[i - n:i]
        m = sum(w) / n
        out.append(math.sqrt(sum((x - m) ** 2 for x in w) / (n - 1)) * math.sqrt(252))
    return out


def one(store, sym, date=None, time=None):
    rows = data.read(store, sym, 'M5')
    if not rows:
        return None
    s, full = session.live_session(rows, sym)
    if date:
        m = [x for x in full if str(x.day) == date]
        s = m[0] if m else None
    if s is None:
        return None
    i = len(s.bars) - 1
    if time:
        at = data.parse_et_clock(s.day, time)
        ks = [j for j, x in enumerate(s.bars) if x.m + 5 <= at]
        if not ks:
            return None
        i = ks[-1]
    c = s.bars[i].c
    out = {'symbol': sym, 'session': str(s.day), 'as_of_et': session.clock(s.bars[i].m + 5), 'last': c,
           'vs_vwap': 'above' if c > s.vwap[i] else 'below', 'vwap': round(s.vwap[i], 4),
           'trend_intraday': {1: 'up', -1: 'down', 0: 'none'}[s.trend[i]]}
    if s.prior is not None:
        out['change_pct'] = round((c / s.prior.close - 1) * 100, 2)
    rng = max(x.h for x in s.bars[:i + 1]) - min(x.l for x in s.bars[:i + 1])
    drows = data.read(store, sym, 'D')
    if drows:
        ser = session.Daily([r for r in drows if data.et(r[0]).date() < s.day], sym)
        if ser.c:
            out['range_vs_daily_atr'] = round(rng / ser.atr[-1], 2)
            if out.get('change_pct') is None:
                out['change_pct'] = round((c / ser.c[-1] - 1) * 100, 2)
            if ser.sma50[-1]:
                out['vs_50d'] = 'above' if c > ser.sma50[-1] else 'below'
            if ser.sma200[-1]:
                out['vs_200d'] = 'above' if c > ser.sma200[-1] else 'below'
            rv = _realised_vol(ser.c)
            if len(rv) > 30:
                cur = rv[-1]
                hist = rv[-252:]
                out['realised_vol_20d'] = round(cur * 100, 1)
                out['realised_vol_percentile_1y'] = round(sum(x <= cur for x in hist) / len(hist), 2)
    return out


def context(store, sectors=None, date=None, time=None):
    idx = [x for x in (one(store, s, date, time) for s in INDEXES) if x]
    breadth = {'symbols': 0, 'above_vwap': 0, 'up_on_day': 0}
    for sym in data.symbols(store, 'M5'):
        x = one(store, sym, date, time) if sym not in INDEXES else next((y for y in idx if y['symbol'] == sym), None)
        if not x:
            continue
        breadth['symbols'] += 1
        breadth['above_vwap'] += x['vs_vwap'] == 'above'
        breadth['up_on_day'] += (x.get('change_pct') or 0) > 0
    sec = None
    if sectors:
        sj = json.load(open(sectors)) if isinstance(sectors, str) else sectors
        rows = sj.get('data', sj) if isinstance(sj, dict) else sj
        adv = sum(int(r.get('advanced', 0)) for r in rows)
        dec = sum(int(r.get('declined', 0)) for r in rows)
        srt = sorted(rows, key=lambda r: float(r.get('change_ratio', 0)))
        sec = {'advancers': adv, 'decliners': dec, 'sectors': len(rows),
               'best': [(r['name'], round(float(r['change_ratio']) * 100, 2)) for r in srt[::-1][:3]],
               'worst': [(r['name'], round(float(r['change_ratio']) * 100, 2)) for r in srt[:3]]}
    score = 0
    for x in idx:
        if x['symbol'] in ('SPY', 'QQQ'):
            score += (1 if x['vs_vwap'] == 'above' else -1) + (1 if (x.get('change_pct') or 0) > 0 else -1) + \
                     {'up': 1, 'down': -1, 'none': 0}[x['trend_intraday']]
    label = 'trend up' if score >= 4 else 'trend down' if score <= -4 else 'mixed / range'
    spy = next((x for x in idx if x['symbol'] == 'SPY'), None)
    vol = None
    if spy and spy.get('realised_vol_percentile_1y') is not None:
        p = spy['realised_vol_percentile_1y']
        vol = 'high' if p >= 0.8 else 'low' if p <= 0.2 else 'normal'
    facts = []
    for x in idx:
        f = f"{x['symbol']} {x.get('change_pct', 0):+.2f}% on the day, {x['vs_vwap']} VWAP, intraday trend {x['trend_intraday']}"
        if x.get('vs_200d'):
            f += f", {x['vs_200d']} its 200-day average"
        facts.append(f)
    if breadth['symbols']:
        facts.append(f"{breadth['above_vwap']} of {breadth['symbols']} symbols in the store are above VWAP, "
                     f"{breadth['up_on_day']} are up on the day")
    if sec:
        facts.append(f"sectors: {sec['advancers']} advancing vs {sec['decliners']} declining stocks")
    as_of = next((x['as_of_et'] for x in idx), None)
    return {'tool': 'market-context', 'generated_at': data.now_utc(), 'regime': label, 'volatility': vol, 'as_of_et': as_of,
            'indexes': idx, 'breadth': breadth, 'sectors': sec, 'facts': facts, 'disclaimer': DISCLAIMER}


def render(r):
    L = [f"MARKET CONTEXT  regime: {r['regime']}" + (f", volatility {r['volatility']}" if r['volatility'] else '') +
         (f"  (as of {r['as_of_et']} ET)" if r.get('as_of_et') else ''), '']
    L += [f'- {f}' for f in r['facts']]
    for x in r['indexes']:
        if x.get('realised_vol_20d') is not None:
            L.append(f"- {x['symbol']} 20-day realised vol {x['realised_vol_20d']}% "
                     f"({x['realised_vol_percentile_1y']:.0%} percentile of the past year)")
    if r['sectors']:
        L.append('- best sectors: ' + ', '.join(f'{n} {v:+.2f}%' for n, v in r['sectors']['best']))
        L.append('- worst sectors: ' + ', '.join(f'{n} {v:+.2f}%' for n, v in r['sectors']['worst']))
    L += ['', r['disclaimer']]
    return '\n'.join(L)
