"""Order flow from saved read-only responses: trades, the order book and
daily money flow (Webull get_stock_tick / get_stock_quotes /
get_stock_capital_flow). Webull's own footprint feed needs a paid
subscription, so the footprint here is rebuilt from the trade tape."""
import json, statistics as st
from datetime import datetime, timezone


def _load(p):
    obj = json.load(open(p))
    return obj


def footprint(ticks, step):
    rows, big, cum = {}, [], 0
    sizes = [int(float(t['volume'])) for t in ticks]
    cut = max(5000, sorted(sizes)[int(len(sizes) * 0.99)] if sizes else 5000)
    for t in sorted(ticks, key=lambda t: int(t['time'])):
        p, v, sd = float(t['price']), int(float(t['volume'])), t.get('side')
        k = round(round(p / step) * step, 4)
        r = rows.setdefault(k, {'buy': 0, 'sell': 0, 'neutral': 0})
        if sd == 'B':
            r['buy'] += v; cum += v
        elif sd == 'S':
            r['sell'] += v; cum -= v
        else:
            r['neutral'] += v
        if v >= cut:
            big.append({'time': datetime.fromtimestamp(int(t['time']) / 1000, timezone.utc).strftime('%H:%M:%SZ'),
                        'price': p, 'size': v, 'side': {'B': 'buy', 'S': 'sell'}.get(sd, 'neutral')})
    tot_b = sum(r['buy'] for r in rows.values())
    tot_s = sum(r['sell'] for r in rows.values())
    t0, t1 = (min(int(t['time']) for t in ticks), max(int(t['time']) for t in ticks)) if ticks else (0, 0)
    poc = max(rows, key=lambda k: sum(rows[k].values())) if rows else None
    return {
        'window_utc': [datetime.fromtimestamp(t0 / 1000, timezone.utc).strftime('%H:%M:%SZ'),
                       datetime.fromtimestamp(t1 / 1000, timezone.utc).strftime('%H:%M:%SZ')] if ticks else None,
        'trades': len(ticks), 'buy_volume': tot_b, 'sell_volume': tot_s, 'delta': tot_b - tot_s,
        'delta_pct': round((tot_b - tot_s) / max(tot_b + tot_s, 1), 3), 'tape_poc': poc,
        'big_prints': big[-10:], 'big_print_threshold_shares': cut,
        'big_buy': sum(b['size'] for b in big if b['side'] == 'buy'),
        'big_sell': sum(b['size'] for b in big if b['side'] == 'sell'),
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
    near_b = sum(s for _, s in bids[:10]); near_a = sum(s for _, s in asks[:10])
    walls = [{'side': sd, 'price': p, 'size': s} for sd, xs in (('bid', bids), ('ask', asks)) for p, s in xs[:20]
             if s >= 3 * med]
    return {'available': True, 'levels': max(len(bids), len(asks)),
            'best_bid': bids[0][0] if bids else None, 'best_ask': asks[0][0] if asks else None,
            'spread': round(asks[0][0] - bids[0][0], 4) if bids and asks else None,
            'imbalance_top10': round((near_b - near_a) / max(near_b + near_a, 1), 3),
            'walls_near': walls[:8]}


def money_flow(rows):
    out = []
    for r in rows:
        out.append({'date': r['date'],
                    'large_net': round(float(r['large_in']) - float(r['large_out'])),
                    'medium_net': round(float(r['medium_in']) - float(r['medium_out'])),
                    'small_net': round(float(r['small_in']) - float(r['small_out']))})
    return out


def read_all(ticks=None, book_file=None, flow=None, price=None):
    out = {}
    if ticks:
        tj = _load(ticks)
        tl = tj.get('result', []) if isinstance(tj, dict) else tj
        ref = price or (float(tl[-1]['price']) if tl else 1.0)
        step = max(0.01, round(ref * 0.0002, 2))
        out['tape'] = footprint(tl, step)
    if book_file:
        out['book'] = book(_load(book_file))
    if flow:
        fj = _load(flow)
        out['money_flow'] = money_flow(fj if isinstance(fj, list) else fj.get('data', []))
    return out
