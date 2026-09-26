#!/usr/bin/env python3
"""Live read of one symbol from saved Webull responses. Analysis only.

usage: live.py SYMBOL [--ticks FILE] [--book FILE] [--flow FILE]

Levels come from data/<SYMBOL>_M5.csv.gz (run ingest.py on today's bars
first; today's unfinished session is included). Order flow comes from saved
responses of the read-only tools:
  --ticks  get_stock_tick (up to 1000 trades; side B = buyer lifted the ask,
           S = seller hit the bid, anything else counted as neutral)
  --book   get_stock_quotes (level 2 bids/asks, depth up to 50)
  --flow   get_stock_capital_flow (daily large/medium/small money in and out;
           stocks only)

Prints one JSON object: levels (VWAP, bands, IB, opening range, initial volume
bar, today's developing POC/VAH/VAL, yesterday's POC/VAH/VAL/high/low,
structure trend and protected level), where price sits against each level,
the footprint built from the ticks (buy/sell volume per price, delta,
stacked imbalances), big prints, the order book (imbalance, walls) and any
playbook setup that fired today. Webull's own footprint feed needs a paid
subscription, so the footprint here is rebuilt from the tick tape.
"""
import json, os, statistics as st, sys
from datetime import datetime, timezone
import core
import lab


def arg(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None


def today_session(sym):
    """core.sessions() keeps only full days; rebuild with today's partial
    session appended so live levels are current."""
    full = core.sessions(sym)
    days = {}
    for t, o, h, l, c, v in core.read(sym, 'M5'):
        d = core.et(t); m = d.hour * 60 + d.minute
        if core.OPEN <= m < core.CLOSE:
            days.setdefault(d.date(), []).append(core.Bar(m, o, h, l, c, v))
    last = max(days)
    if full and full[-1].day == last:
        return full[-1], full
    b = days[last]
    if b[0].m != core.OPEN or len(b) < 1:
        return None, full
    slot_hist = {}
    for s in full[-20:]:
        for k, x in enumerate(s.bars):
            slot_hist.setdefault(k, []).append(x.v)
    s = core.Session(sym, last, b)
    prev = full[-1] if full else None
    s.prior = prev
    atr_state = []
    if prev:
        for x in prev.bars[-14:]:
            atr_state.append(x.h - x.l)
    if len(b) < 3:
        s.bars = b + [b[-1]] * (3 - len(b))   # pad so the opening range exists
    s.build(slot_hist, prev.close if prev else None, atr_state)
    s.bars = b
    return s, full


def footprint(ticks, step):
    rows, big, cum, path = {}, [], 0, []
    sizes = [int(float(t['volume'])) for t in ticks]
    cut = max(5000, sorted(sizes)[int(len(sizes) * 0.99)] if sizes else 5000)
    for t in sorted(ticks, key=lambda t: int(t['time'])):
        p, v, sd = float(t['price']), int(float(t['volume'])), t.get('side')
        k = round(p / step) * step
        r = rows.setdefault(round(k, 4), {'buy': 0, 'sell': 0, 'neutral': 0})
        if sd == 'B':
            r['buy'] += v; cum += v
        elif sd == 'S':
            r['sell'] += v; cum -= v
        else:
            r['neutral'] += v
        path.append(cum)
        if v >= cut:
            big.append({'time': datetime.fromtimestamp(int(t['time']) / 1000, timezone.utc).strftime('%H:%M:%SZ'),
                        'price': p, 'size': v, 'side': {'B': 'buy', 'S': 'sell'}.get(sd, 'neutral'),
                        'notional': round(p * v)})
    prices = sorted(rows)
    imb = []
    for a, b in zip(prices, prices[1:]):       # diagonal: buys at b vs sells at a
        if rows[b]['buy'] >= 3 * max(rows[a]['sell'], 1) and rows[b]['buy'] > 0:
            imb.append({'price': b, 'side': 'buy', 'ratio': round(rows[b]['buy'] / max(rows[a]['sell'], 1), 1)})
        if rows[a]['sell'] >= 3 * max(rows[b]['buy'], 1) and rows[a]['sell'] > 0:
            imb.append({'price': a, 'side': 'sell', 'ratio': round(rows[a]['sell'] / max(rows[b]['buy'], 1), 1)})
    stacked = []
    for sd in ('buy', 'sell'):
        run = []
        for x in [i for i in imb if i['side'] == sd]:
            if run and round(x['price'] - run[-1]['price'], 4) > step * 1.01:
                if len(run) >= 3: stacked.append({'side': sd, 'from': run[0]['price'], 'to': run[-1]['price']})
                run = []
            run.append(x)
        if len(run) >= 3: stacked.append({'side': sd, 'from': run[0]['price'], 'to': run[-1]['price']})
    tot_b = sum(r['buy'] for r in rows.values()); tot_s = sum(r['sell'] for r in rows.values())
    t0, t1 = (min(int(t['time']) for t in ticks), max(int(t['time']) for t in ticks)) if ticks else (0, 0)
    return {
        'window': [datetime.fromtimestamp(t0 / 1000, timezone.utc).strftime('%H:%M:%SZ'),
                   datetime.fromtimestamp(t1 / 1000, timezone.utc).strftime('%H:%M:%SZ')] if ticks else None,
        'trades': len(ticks), 'bucket': step,
        'buy_volume': tot_b, 'sell_volume': tot_s, 'delta': tot_b - tot_s,
        'delta_pct': round((tot_b - tot_s) / max(tot_b + tot_s, 1), 3),
        'rows': [{'price': p, **rows[p], 'delta': rows[p]['buy'] - rows[p]['sell']} for p in reversed(prices)],
        'imbalances': imb[-12:], 'stacked_imbalances': stacked,
        'big_prints': big[-15:], 'big_print_threshold_shares': cut,
    }


def book(q):
    def lv(xs):
        out = []
        for x in xs or []:
            if isinstance(x, dict):
                p = x.get('price'); s = x.get('size', x.get('volume', x.get('quantity')))
            else:
                p, s = x[0], x[1]
            if p is not None and s is not None:
                out.append((float(p), float(s)))
        return out
    bids, asks = lv(q.get('bids')), lv(q.get('asks'))
    if not bids and not asks:
        return {'available': False, 'note': 'empty book (market closed, or no level 2 permission)'}
    allsz = [s for _, s in bids + asks]
    med = st.median(allsz)
    walls = [{'side': sd, 'price': p, 'size': s} for sd, xs in (('bid', bids), ('ask', asks)) for p, s in xs if s >= 3 * med]
    bsum, asum = sum(s for _, s in bids), sum(s for _, s in asks)
    return {'available': True, 'levels': max(len(bids), len(asks)),
            'best_bid': bids[0] if bids else None, 'best_ask': asks[0] if asks else None,
            'bid_size': bsum, 'ask_size': asum, 'imbalance': round((bsum - asum) / max(bsum + asum, 1), 3),
            'walls': walls, 'bids': bids, 'asks': asks}


def fired_today(s):
    out = []
    frozen = json.load(open(lab.FROZEN_PATH)) if os.path.exists(lab.FROZEN_PATH) else {}
    for stp in lab.load_setups():
        if stp['tf'] != 'M5' or stp['id'] not in frozen:
            continue
        fz = frozen[stp['id']]
        for i, d in stp['detect'](s):
            if not lab.passes(fz['filter'], lab.FILTERS, s, i, d):
                continue
            lean = d if fz['side'] == 'with' else -d
            out.append({'setup': stp['id'], 'name': stp['name'], 'bar_et': f"{s.bars[i].m // 60}:{s.bars[i].m % 60:02d}",
                        'lean': 'up' if lean == 1 else 'down', 'variant': f"{fz['side']} · {fz['filter']} · {fz['exit']}"})
    return out


def main():
    sym = sys.argv[1]
    s, full = today_session(sym)
    if s is None:
        print(json.dumps({'symbol': sym, 'error': 'no session for the latest day in data/'})); return
    i = len(s.bars) - 1
    c = s.bars[-1].c
    poc, vah, val = core.profile(s.bars)
    p = s.prior
    rel = lambda lvl: None if lvl is None else ('above' if c > lvl else 'below' if c < lvl else 'at')
    lv = {
        'last': c, 'as_of_et': f"{s.bars[-1].m // 60}:{s.bars[-1].m % 60:02d}", 'session': str(s.day), 'bars': len(s.bars),
        'vwap': round(s.vwap[i], 4), 'vwap_upper_1sd': round(s.vwap[i] + s.vsd[i], 4), 'vwap_lower_1sd': round(s.vwap[i] - s.vsd[i], 4),
        'vwap_upper_2sd': round(s.vwap[i] + 2 * s.vsd[i], 4), 'vwap_lower_2sd': round(s.vwap[i] - 2 * s.vsd[i], 4),
        'opening_range': [s.or_lo, s.or_hi], 'initial_balance': [s.ib_lo, s.ib_hi], 'ib_complete': len(s.bars) >= 12,
        'initial_volume_bar': {'bar_et': f"{s.bars[s.ivb_i].m // 60}:{s.bars[s.ivb_i].m % 60:02d}", 'low': s.ivb_lo, 'high': s.ivb_hi},
        'developing_poc': round(poc, 4), 'developing_vah': round(vah, 4), 'developing_val': round(val, 4),
        'prior': None if p is None else {'high': p.hi, 'low': p.lo, 'close': p.close,
                                         'poc': round(p.poc, 4), 'vah': round(p.vah, 4), 'val': round(p.val, 4)},
        'structure': {'trend': {1: 'up', -1: 'down', 0: 'none'}[s.trend[i]], 'protected_level': s.prot[i],
                      'last_event': next(((f"{s.bars[k].m // 60}:{s.bars[k].m % 60:02d}", s.event[k]) for k in range(i, -1, -1) if s.event[k]), None)},
        'rvol_last_bar': None if s.rvol[i] is None else round(s.rvol[i], 2), 'atr_5m': round(s.atr[i], 4),
    }
    lv['position'] = {k: rel(v) for k, v in {'vwap': lv['vwap'], 'ib_high': s.ib_hi, 'ib_low': s.ib_lo,
                                            'developing_poc': poc, 'prior_poc': p.poc if p else None,
                                            'prior_vah': p.vah if p else None, 'prior_val': p.val if p else None,
                                            'prior_high': p.hi if p else None, 'prior_low': p.lo if p else None}.items()}
    out = {'symbol': sym, 'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'levels': lv,
           'playbook_signals_today': fired_today(s)}
    if arg('--ticks'):
        tj = json.load(open(arg('--ticks')))
        step = max(0.01, round(c * 0.0002, 2))
        out['footprint'] = footprint(tj.get('result', []) if isinstance(tj, dict) else tj, step)
    if arg('--book'):
        out['book'] = book(json.load(open(arg('--book'))))
    if arg('--flow'):
        fl = json.load(open(arg('--flow')))
        out['money_flow'] = [{'date': r['date'],
                              'large_net': round(float(r['large_in']) - float(r['large_out'])),
                              'medium_net': round(float(r['medium_in']) - float(r['medium_out'])),
                              'small_net': round(float(r['small_in']) - float(r['small_out']))} for r in fl]
    if '--db' in sys.argv:
        d = os.path.join(core.HERE, 'out', 'db', 'chart_live')
        os.makedirs(d, exist_ok=True)
        doc = json.loads(json.dumps(out, default=str))
        if doc.get('footprint'):
            doc['footprint']['rows'] = doc['footprint']['rows'][:40]
        if doc.get('book'):
            doc['book'].pop('bids', None); doc['book'].pop('asks', None)
        json.dump(doc, open(os.path.join(d, f'{sym}.json'), 'w'))
        fp, bk, lv = out.get('footprint') or {}, out.get('book') or {}, out['levels']
        row = {'symbol': sym, 'at': out['generated_at'], 'session': lv['session'], 'as_of_et': lv['as_of_et'], 'last': lv['last'],
               'vwap': lv['vwap'], 'poc': lv['developing_poc'], 'vah': lv['developing_vah'], 'val': lv['developing_val'],
               'trend': lv['structure']['trend'], 'protected': lv['structure']['protected_level'],
               'tick_window': fp.get('window'), 'trades': fp.get('trades'), 'buy': fp.get('buy_volume'), 'sell': fp.get('sell_volume'),
               'delta': fp.get('delta'), 'stacked': fp.get('stacked_imbalances'), 'big_prints': len(fp.get('big_prints') or []),
               'big_buy': sum(b['size'] for b in fp.get('big_prints') or [] if b['side'] == 'buy'),
               'big_sell': sum(b['size'] for b in fp.get('big_prints') or [] if b['side'] == 'sell'),
               'book_available': bk.get('available'), 'book_imbalance': bk.get('imbalance'),
               'walls': [[w['side'], w['price'], w['size']] for w in (bk.get('walls') or [])][:8],
               'large_money_net_today': (out.get('money_flow') or [{}])[-1].get('large_net')}
        with open(os.path.join(core.HERE, 'out', 'tape_rows.jsonl'), 'a') as fh:
            fh.write(json.dumps(row) + '\n')
        print(json.dumps(row))
        return
    print(json.dumps(out, default=str))


if __name__ == '__main__':
    main()
