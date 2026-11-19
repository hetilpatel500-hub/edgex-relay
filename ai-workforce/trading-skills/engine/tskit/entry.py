"""Entry watch: is the trigger in, and does the rest of the picture agree?

Two ways to say what you are waiting for:
  * a setup: `setup=ID` — the trigger is that setup firing on one of the
    last two closed bars, in your direction once its tested side (with or
    fade) is applied, with its validated filter met;
  * a level: `level=PRICE, trigger=break|reclaim|bounce`
      break    the last close is beyond the level and no earlier close today was
      reclaim  an earlier close today was on the wrong side; the last close is back
      bounce   the last bar tagged the level (within 0.1 ATR) and closed at
               least 0.1 ATR away on your side
Then a checklist: VWAP side, volume, structure trend, the market (SPY vs
its VWAP), the trade tape and order book if saved, time left in the
session, the stop's distance, and any event risk from the event calendar.

States: INVALID (price is already through your stop), WAIT (no trigger),
CAUTION (trigger in, but something disagrees), READY (trigger in and
nothing disagrees). READY means the conditions you asked for are present,
not that the trade will work.
"""
import json
from . import data, session, setups as setups_mod, backtest, tape as tape_mod, DISCLAIMER


def _chk(name, ok, detail, required=False):
    return {'check': name, 'result': 'pass' if ok is True else 'fail' if ok is False else 'n/a',
            'detail': detail, 'required': required}


def check(store, symbol, side, setup=None, level=None, trigger='break', stop=None, results=None, setup_dirs=None,
          ticks=None, book=None, flow=None, events=None, min_rvol=1.2, late_minutes=30, date=None, time=None):
    symbol = symbol.upper()
    d = {'long': 1, 'buy': 1, 'short': -1, 'sell': -1}[side.lower()]
    rows = data.read(store, symbol, 'M5')
    if not rows:
        raise ValueError(f'no 5-minute bars for {symbol}')
    s, full = session.live_session(rows, symbol)
    if date:
        m = [x for x in full if str(x.day) == date]
        s = m[0] if m else s
    if s is None:
        raise ValueError(f'{symbol}: no session with a 9:30 bar')
    i = len(s.bars) - 1
    if time:
        m = data.parse_et_clock(s.day, time)
        ks = [j for j, b in enumerate(s.bars) if b.m + 5 <= m]
        if not ks:
            raise ValueError(f'no 5-minute bar completed by {time} ET')
        i = ks[-1]
    x = s.bars[i]
    A = s.atr[i]
    c = x.c
    checks = []
    trig = False
    if setup:
        stp = setups_mod.load(setup_dirs, store, {setup})
        if not stp:
            raise ValueError(f'unknown setup {setup}')
        ev = next((r for r in (results or {}).get('results', []) if r.get('id') == setup), None)
        sgn = -1 if ev and ev.get('side') == 'fade' else 1
        filt = ev.get('filter') if ev and ev.get('side') else 'none'
        hits = [(j, dd) for j, dd in setups_mod.fires(stp[0], s) if i - 1 <= j <= i]
        good = [(j, dd) for j, dd in hits if dd * sgn == d]
        met = [(j, dd) for j, dd in good if filt == 'none' or backtest.passes(filt, backtest.FILTERS, s, j, dd)]
        trig = bool(met)
        detail = (f"{setup} fired at {session.clock(s.bars[met[-1][0]].m + 5)} ET" if met else
                  f"{setup} fired but not in your direction or without its filter ({filt})" if hits else
                  f"{setup} has not fired on the last two bars")
        checks.append(_chk('trigger', trig, detail, True))
        if ev:
            checks.append(_chk('setup evidence', ev['status'] in ('validated', 'promising'),
                               f"status {ev['status']} on this data ({ev.get('side')} · {ev.get('filter')} · {ev.get('exit')})"))
        else:
            checks.append(_chk('setup evidence', None, 'no backtest results given; run the backtester'))
    elif level is not None:
        level = float(level)
        closes = [b.c for b in s.bars[:i + 1]]
        on = lambda v: (v - level) * d > 0
        if trigger == 'break':
            trig = on(c) and not any(on(v) for v in closes[:-1])
            detail = f"close {c} {'beyond' if on(c) else 'not beyond'} {level}; " + \
                     ('first close beyond today' if trig else 'an earlier close was already beyond' if on(c) else '')
        elif trigger == 'reclaim':
            trig = on(c) and any((v - level) * d < 0 for v in closes[:-1])
            detail = f"close {c} back {'on your side of' if on(c) else 'still on the wrong side of'} {level}"
        elif trigger == 'bounce':
            tag = (x.l <= level + 0.1 * A) if d == 1 else (x.h >= level - 0.1 * A)
            away = (c - level) * d >= 0.1 * A
            trig = tag and away
            detail = f"bar {'tagged' if tag else 'did not tag'} {level} and closed {abs(c - level) / A:.2f} ATR away"
        else:
            raise ValueError('trigger must be break, reclaim or bounce')
        checks.append(_chk('trigger', trig, detail.strip('; '), True))
    else:
        trig = True
        checks.append(_chk('trigger', None, 'no setup or level given: checklist only', False))

    checks.append(_chk('vwap side', (c - s.vwap[i]) * d > 0, f"close {c} vs VWAP {round(s.vwap[i], 4)}"))
    rv = s.rvol[i]
    checks.append(_chk('volume', None if rv is None else rv >= min_rvol,
                       'no volume history yet' if rv is None else f"last bar {rv:.2f}x normal (want {min_rvol}x)"))
    checks.append(_chk('structure trend', None if s.trend[i] == 0 else s.trend[i] == d,
                       {1: 'up', -1: 'down', 0: 'none yet'}[s.trend[i]]))
    if symbol != 'SPY' and data.read(store, 'SPY', 'M5'):
        sp, _ = session.live_session(data.read(store, 'SPY', 'M5'), 'SPY')
        if sp is not None and sp.day == s.day:
            j = min(len(sp.bars) - 1, i)
            checks.append(_chk('market (SPY vs VWAP)', (sp.bars[j].c - sp.vwap[j]) * d > 0,
                               f"SPY {sp.bars[j].c} vs VWAP {round(sp.vwap[j], 2)}"))
    flow = tape_mod.read_all(ticks, book, flow, c)
    if flow.get('tape'):
        t = flow['tape']
        checks.append(_chk('trade tape', t['delta_pct'] * d > 0.02 if abs(t['delta_pct']) > 0.02 else None,
                           f"buy {t['buy_volume']:,} vs sell {t['sell_volume']:,} ({t['delta_pct']:+.1%})"))
    if flow.get('book') and flow['book'].get('available'):
        b = flow['book']
        checks.append(_chk('order book', None if abs(b['imbalance_top10']) < 0.2 else b['imbalance_top10'] * d > 0,
                           f"top-10 imbalance {b['imbalance_top10']:+.2f}, spread {b['spread']}"))
    left = session.CLOSE - (x.m + 5)
    checks.append(_chk('time left', left > late_minutes, f'{left} minutes to the close'))
    status = None
    if stop is not None:
        stop = float(stop)
        dist = (c - stop) * d
        if dist <= 0:
            status = 'INVALID'
            checks.append(_chk('stop', False, f'price {c} is already through the stop {stop}', True))
        else:
            checks.append(_chk('stop distance', 0.5 <= dist / A <= 3.0, f'{dist / A:.2f} ATR (want 0.5 to 3)'))
    if events:
        ej = json.load(open(events)) if isinstance(events, str) else events
        flags = [f for f in ej.get('flags', []) if f.get('symbol') in (symbol, None, '*')]
        checks.append(_chk('event risk', not flags, '; '.join(f['flag'] for f in flags) or 'nothing flagged'))
    against = [k for k in checks if k['result'] == 'fail' and not k['required']]
    if status is None:
        status = 'WAIT' if not trig else ('CAUTION' if against else 'READY')
    return {'tool': 'entry-watch', 'generated_at': data.now_utc(), 'symbol': symbol, 'side': 'long' if d == 1 else 'short',
            'session': str(s.day), 'as_of_et': session.clock(x.m + 5), 'price': c, 'atr_5m': round(A, 4),
            'status': status, 'checks': checks,
            'note': 'READY means the conditions you asked for are present, not that the trade will work.',
            'disclaimer': DISCLAIMER}


def render(r):
    mark = {'pass': '+', 'fail': 'x', 'n/a': '.'}
    L = [f"ENTRY WATCH  {r['symbol']} {r['side']} at {r['as_of_et']} ET ({r['session']}), price {r['price']}: {r['status']}", '']
    for c in r['checks']:
        L.append(f"  [{mark[c['result']]}] {c['check']:22s} {c['detail']}")
    L += ['', r['note'], r['disclaimer']]
    return '\n'.join(L)
