#!/usr/bin/env python3
"""Study: the "number one trade" claim -- double top / double bottom off key
highs and lows, confirmed by VWAP and the 200-day moving average.

Requested by the owner 2026-09-29 after a reel in which a coach calls this
the best trade and rejects RSI/MACD in favour of VWAP and the 200-day MA.
Analysis only: nothing here places, stages or suggests orders.

Every rule below was fixed BEFORE any result was looked at. Nothing is tuned.

Data (Webull get_stock_bars, read-only, saved as returned):
  5-minute RTH bars, 2025-10-01 .. 2026-09-28, SPY QQQ IWM DIA AAPL MSFT NVDA
  AMZN GOOGL META TSLA AMD (data/<SYM>_M5.csv.gz); daily bars 2021-12 ..
  2026-09-25 (data/<SYM>_D.csv.gz).

INTRADAY TEST (5-minute bars)
  Swing high/low: a bar whose high (low) beats the 2 bars on each side,
    known 2 bars later (no look-ahead).
  Key high (low): peak 1 is within 0.25 ATR of yesterday's high (low) or is
    the session's high (low) so far.
  Double top: a later swing high within 0.25 ATR of peak 1, at least 3 bars
    (15 minutes) after it, with nothing in between trading above the higher
    peak; the dip between them (the neckline) is at least 0.5 ATR deep.
  Trigger: the first 5-minute close below the neckline within 12 bars
    (1 hour) of the second peak being known, before 15:00 ET.
    Double bottom is the mirror image.
  The coach's confirmations:
    VWAP   short only if the trigger bar closes below session VWAP
           (long: above).
    200-DMA short only if yesterday's daily close was below its 200-day
           simple moving average (long: above), i.e. trade with the
           long-term trend.
  Trade: enter at the next bar's open; stop 0.1 ATR beyond the pattern's
    extreme (the higher top / lower bottom); target the textbook measured
    move (neckline minus the pattern height); anything open is closed at
    the last bar of the day. If one bar touches both stop and target, the
    stop counts. Costs: 2 bps round trip on ETFs, 3 bps on stocks.
  Result is in R (multiples of the money risked from entry to stop).

DAILY TEST (daily bars, 200-DMA only: VWAP is an intraday line)
  Swing highs/lows with 5 days each side; peak 1 is the highest high of the
  prior 60 days (key high); peak 2 within 0.5 daily ATR, 5-60 days later;
  neckline dip at least 1 ATR; trigger close through the neckline within
  20 days of peak 2 being known; 200-DMA confirmation as above; enter next
  open, stop 0.1 ATR beyond the extreme, measured-move target, 20-day max
  hold, gaps through the stop fill at the open.

CHECKS
  * Four versions side by side: pattern only, +VWAP, +200-DMA, +both
    (the coach's full rule).
  * Random baseline: every real trade is replayed 1,000 times at a random
    bar (before 15:00) of a random session of the same symbol, same
    direction, same stop and target distance in ATR. The p-value is the
    share of random runs whose average R is at least the real average.
  * Stability: first 70% of dates vs last 30%, each quarter, each symbol.

usage: python3 study.py            writes results.json and prints a summary
"""
import json, math, os, random, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, LAB)
import core  # noqa: E402

core.HERE = HERE          # read this study's own one-year data folder

TOL, DEPTH, MIN_GAP, WINDOW, BUF = 0.25, 0.5, 3, 12, 0.1
LAST_ENTRY_M = 900        # 15:00 ET


def daily_trend():
    """(sym, session date) -> +1 if yesterday closed above its 200-DMA, -1 below."""
    out = {}
    for sym in core.UNIVERSE:
        d = core.Daily(sym)
        prev = None
        for i, day in enumerate(d.day):
            if prev is not None and d.sma200[prev] is not None:
                out[(sym, day)] = 1 if d.c[prev] > d.sma200[prev] else -1
            prev = i
        # the session after the last stored daily bar
        last = len(d.day) - 1
        if d.sma200[last] is not None:
            out[(sym, 'after', d.day[last])] = 1 if d.c[last] > d.sma200[last] else -1
    return out


def trend_for(tr, sym, day):
    if (sym, day) in tr:
        return tr[(sym, day)]
    # sessions after the last daily bar (e.g. today's) use the last known close
    cands = [k for k in tr if len(k) == 3 and k[0] == sym and k[2] < day]
    return tr[max(cands, key=lambda k: k[2])] if cands else None


def pivots(b, k, hi=True):
    if k < 2 or k + 2 >= len(b):
        return False
    if hi:
        return all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2))
    return all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2))


def patterns(s):
    """Yield dicts for every double top (d=-1) / bottom (d=+1) trigger in a session."""
    b, p = s.bars, s.prior
    n = len(b)
    for d in (-1, 1):
        top = d == -1
        ext = (lambda x: x.h) if top else (lambda x: x.l)
        better = (lambda a, c: a > c) if top else (lambda a, c: a < c)
        peaks = []                      # (k, value) of qualified key-level first peaks
        fired = False
        for i in range(4, n):
            if fired or b[i].m >= LAST_ENTRY_M:
                break
            k = i - 2                   # pivot at k is known at bar i
            if not pivots(b, k, hi=top):
                continue
            atr = s.atr[k]
            if not atr:
                continue
            v = ext(b[k])
            # is it a second peak for any earlier key-level first peak?
            for (k1, v1) in peaks:
                if k - k1 < MIN_GAP or abs(v - v1) > TOL * atr:
                    continue
                mid = b[k1 + 1:k]
                if not mid:
                    continue
                edge = max(v, v1) if top else min(v, v1)
                if any(better(ext(x), edge) for x in mid):
                    continue
                neck = min(x.l for x in mid) if top else max(x.h for x in mid)
                inner = min(v, v1) if top else max(v, v1)
                if abs(inner - neck) < DEPTH * atr:
                    continue
                # look for the trigger close through the neckline
                for j in range(i, min(i + WINDOW + 1, n)):
                    if b[j].m >= LAST_ENTRY_M:
                        break
                    if any(better(ext(b[q]), edge) for q in range(k + 1, j + 1)):
                        break           # pattern broken: new extreme before the trigger
                    if (b[j].c < neck) if top else (b[j].c > neck):
                        yield dict(i=j, d=d, edge=edge, neck=neck, k1=k1, k2=k)
                        fired = True
                        break
                if fired:
                    break
            if fired:
                break
            # key-level test for this pivot as a potential first peak
            so_far = b[:k + 1]
            day_ext = max(x.h for x in so_far) if top else min(x.l for x in so_far)
            key = (v == day_ext)
            if p is not None:
                key = key or abs(v - (p.hi if top else p.lo)) <= TOL * atr
            if key:
                peaks.append((k, v))


def simulate(s, i, d, stop, tgt):
    """Enter next bar open; return (R, stop_dist) or None."""
    b = s.bars
    if i + 1 >= len(b):
        return None
    e = b[i + 1].o
    risk = (e - stop) * d
    if risk <= 0:
        return None
    x = b[-1].c
    for k in range(i + 1, len(b)):
        y = b[k]
        if (y.l <= stop) if d == 1 else (y.h >= stop):
            x = stop; break
        if tgt is not None and ((y.h >= tgt) if d == 1 else (y.l <= tgt)):
            x = tgt; break
    cost = core.COST_BPS[s.sym] / 1e4 * e
    return ((x - e) * d - cost) / risk, risk


def intraday():
    tr = daily_trend()
    trades = []
    sess_by_sym = {}
    for sym in core.UNIVERSE:
        ss = core.sessions(sym)
        sess_by_sym[sym] = ss
        for s in ss:
            for pt in patterns(s):
                i, d = pt['i'], pt['d']
                atr = s.atr[i]
                stop = pt['edge'] - d * BUF * atr
                height = abs(pt['edge'] - pt['neck'])
                tgt = pt['neck'] + d * height
                r = simulate(s, i, d, stop, tgt)
                if r is None:
                    continue
                R, risk = r
                e = s.bars[i + 1].o
                vw_ok = (s.bars[i].c > s.vwap[i]) if d == 1 else (s.bars[i].c < s.vwap[i])
                t = trend_for(tr, sym, s.day)
                ma_ok = t is not None and t == d
                trades.append(dict(sym=sym, day=s.day.isoformat(), t=f'{s.bars[i].m // 60:02d}:{s.bars[i].m % 60:02d}',
                                   d=d, R=round(R, 4), vwap_ok=vw_ok, ma200_ok=ma_ok, ma200_known=t is not None,
                                   entry=e, stop=round(stop, 4), target=round(tgt, 4),
                                   stop_atr=risk / atr, tgt_atr=abs(tgt - e) / atr))
    return trades, sess_by_sym


def baseline(trades, sess_by_sym, reps=1000, seed=7):
    """Average R of random entries matched to each real trade."""
    rng = random.Random(seed)
    pools = {}
    for sym, ss in sess_by_sym.items():
        pools[sym] = [(s, i) for s in ss for i in range(3, len(s.bars) - 1) if s.bars[i].m < LAST_ENTRY_M and s.atr[i]]
    means = []
    for _ in range(reps):
        rs = []
        for t in trades:
            s, i = rng.choice(pools[t['sym']])
            d = t['d']
            e = s.bars[i + 1].o
            atr = s.atr[i]
            stop = e - d * t['stop_atr'] * atr
            tgt = e + d * t['tgt_atr'] * atr
            r = simulate(s, i, d, stop, tgt)
            if r:
                rs.append(r[0])
        means.append(sum(rs) / len(rs) if rs else 0)
    return means


def daily_test():
    tr_out = []
    for sym in core.UNIVERSE:
        D = core.Daily(sym)
        n = len(D.c)
        for d in (-1, 1):
            top = d == -1
            ext = D.h if top else D.l
            last_fire = -1
            for i in range(10, n):
                k2 = i - 5
                if k2 < 5 or k2 <= last_fire:
                    continue
                if not all((ext[k2] > ext[j]) if top else (ext[k2] < ext[j]) for j in range(k2 - 5, k2 + 6) if j != k2):
                    continue
                atr = D.atr[k2]
                for k1 in range(max(5, k2 - 60), k2 - 4):
                    lo, hi = max(0, k1 - 60), k1
                    if hi - lo < 60:
                        continue
                    key = ext[k1] >= max(D.h[lo:hi]) if top else ext[k1] <= min(D.l[lo:hi])
                    if not key:
                        continue
                    if not all((ext[k1] > ext[j]) if top else (ext[k1] < ext[j]) for j in range(k1 - 5, k1 + 6) if j != k1):
                        continue
                    if abs(ext[k2] - ext[k1]) > 0.5 * atr:
                        continue
                    edge = max(ext[k1], ext[k2]) if top else min(ext[k1], ext[k2])
                    mid = range(k1 + 1, k2)
                    if any((ext[j] > edge) if top else (ext[j] < edge) for j in mid):
                        continue
                    neck = min(D.l[j] for j in mid) if top else max(D.h[j] for j in mid)
                    inner = min(ext[k1], ext[k2]) if top else max(ext[k1], ext[k2])
                    if abs(inner - neck) < 1.0 * atr:
                        continue
                    for j in range(i, min(i + 21, n - 1)):
                        if any((ext[q] > edge) if top else (ext[q] < edge) for q in range(k2 + 1, j + 1)):
                            break
                        if (D.c[j] < neck) if top else (D.c[j] > neck):
                            e = D.o[j + 1]
                            stop = edge - d * 0.1 * D.atr[j]
                            risk = (e - stop) * d
                            if risk <= 0:
                                break
                            tgt = neck + d * abs(edge - neck)
                            last = min(j + 20, n - 1)
                            x = D.c[last]
                            for q in range(j + 1, last + 1):
                                if d == 1 and D.l[q] <= stop:
                                    x = min(stop, D.o[q]) if q > j + 1 else stop; break
                                if d == -1 and D.h[q] >= stop:
                                    x = max(stop, D.o[q]) if q > j + 1 else stop; break
                                if (D.h[q] >= tgt) if d == 1 else (D.l[q] <= tgt):
                                    x = tgt; break
                            cost = core.COST_BPS[sym] / 1e4 * e
                            R = ((x - e) * d - cost) / risk
                            ma = D.sma200[j]
                            ma_ok = ma is not None and ((D.c[j] > ma) if d == 1 else (D.c[j] < ma))
                            tr_out.append(dict(sym=sym, day=D.day[j].isoformat(), d=d, R=round(R, 4),
                                               ma200_ok=ma_ok, ma200_known=ma is not None))
                            last_fire = j
                            break
                    break
    return tr_out


def split_stats(rows, dates_sorted):
    cut = dates_sorted[int(len(dates_sorted) * 0.7)]
    first = [r['R'] for r in rows if r['day'] < cut]
    last = [r['R'] for r in rows if r['day'] >= cut]
    return {'cut': cut, 'first_70pct': core.stats(first), 'last_30pct': core.stats(last)}


def by(rows, key):
    out = {}
    for r in rows:
        out.setdefault(key(r), []).append(r['R'])
    return {k: core.stats(v) for k, v in sorted(out.items())}


def main():
    trades, sess = intraday()
    all_days = sorted({s.day.isoformat() for ss in sess.values() for s in ss})
    versions = {
        'pattern_only': lambda t: True,
        'plus_vwap': lambda t: t['vwap_ok'],
        'plus_200dma': lambda t: t['ma200_ok'],
        'coach_full_rule': lambda t: t['vwap_ok'] and t['ma200_ok'],
    }
    res = {'data': {'intraday_sessions': len(all_days), 'first': all_days[0], 'last': all_days[-1],
                    'symbols': core.UNIVERSE, 'source': 'Webull get_stock_bars (read-only), 5-minute RTH bars'},
           'intraday': {}, 'daily': {}}
    for name, f in versions.items():
        rows = [t for t in trades if f(t)]
        st = core.stats([t['R'] for t in rows])
        base = baseline(rows, sess) if rows else []
        mean = st.get('avg_r', 0)
        p = sum(1 for m in base if m >= mean) / len(base) if base else None
        res['intraday'][name] = {
            'all': st,
            'longs': core.stats([t['R'] for t in rows if t['d'] == 1]),
            'shorts': core.stats([t['R'] for t in rows if t['d'] == -1]),
            'random_baseline_avg_r': round(sum(base) / len(base), 3) if base else None,
            'random_baseline_p95': round(sorted(base)[int(len(base) * 0.95)], 3) if base else None,
            'p_value_vs_random': p,
            'split': split_stats(rows, all_days),
            'by_quarter': by(rows, lambda t: f"{t['day'][:4]}-Q{(int(t['day'][5:7]) - 1) // 3 + 1}"),
            'by_symbol': by(rows, lambda t: t['sym']),
            'symbols_positive': sum(1 for v in by(rows, lambda t: t['sym']).values() if v.get('avg_r', 0) > 0),
        }
    # Exit sensitivity (added AFTER the main result was seen, so it is reported
    # only as a robustness check, never as the headline): same entries and
    # the same structural stop, other exits.
    idx = {}
    for sym, ss in sess.items():
        for s in ss:
            idx[(sym, s.day.isoformat())] = s
    res['exit_sensitivity_post_hoc'] = {}
    for name in ('pattern_only', 'coach_full_rule'):
        rows = [t for t in trades if versions[name](t)]
        out = {}
        for label, mult in (('target_1R', 1.0), ('target_2R', 2.0), ('target_3R', 3.0), ('hold_to_close', None)):
            rs = []
            for t in rows:
                s = idx[(t['sym'], t['day'])]
                i = next(k for k, b in enumerate(s.bars) if f'{b.m // 60:02d}:{b.m % 60:02d}' == t['t'])
                risk = (t['entry'] - t['stop']) * t['d']
                tgt = t['entry'] + t['d'] * mult * risk if mult else None
                r = simulate(s, i, t['d'], t['stop'], tgt)
                if r:
                    rs.append(r[0])
            out[label] = core.stats(rs)
        res['exit_sensitivity_post_hoc'][name] = out
    res['intraday_trades'] = trades
    dt = daily_test()
    ddays = sorted({t['day'] for t in dt})
    for name, f in {'pattern_only': lambda t: True, 'plus_200dma': lambda t: t['ma200_ok']}.items():
        rows = [t for t in dt if f(t)]
        res['daily'][name] = {'all': core.stats([t['R'] for t in rows]),
                              'longs': core.stats([t['R'] for t in rows if t['d'] == 1]),
                              'shorts': core.stats([t['R'] for t in rows if t['d'] == -1]),
                              'split': split_stats(rows, ddays) if ddays else None,
                              'by_symbol': by(rows, lambda t: t['sym'])}
    res['daily_trades'] = dt
    json.dump(res, open(os.path.join(HERE, 'results.json'), 'w'), indent=1, default=str)
    for name, v in res['intraday'].items():
        print('INTRADAY', name, v['all'], 'baseline', v['random_baseline_avg_r'], 'p', v['p_value_vs_random'],
              'sym+', v['symbols_positive'])
        print('   split', v['split']['first_70pct'], '|', v['split']['last_30pct'])
    for name, v in res['daily'].items():
        print('DAILY', name, v['all'])


if __name__ == '__main__':
    main()
