"""News watch: group headlines into stories and confirm them.

Inputs are saved get_stock_news / search_news responses and, optionally, a
JSON list of web search results ({title, url, outlet?, date}). Headlines
about the same event are grouped by word overlap; a story counts as
CONFIRMED only when at least two independent outlets carry it inside the
window (default 14 days). Several items from one outlet are one source.

For each story it also measures how far the stock has moved since the
story first appeared (from the 5-minute bars in the store), so you can
see whether the news is already in the price. Catalyst tags come from
keywords in the headline; they are labels, not judgements.
"""
import json, re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from . import data, session, DISCLAIMER

STOP = set('the a an and or of to in on for with at by from as is are be its it this that will after over new into '
           'than more says say said could can may why what how stock stocks shares share inc corp co ltd'.split())
TAGS = {
    'earnings': r'earnings|eps|revenue|quarter|results|guidance|outlook|forecast',
    'analyst': r'upgrade|downgrade|price target|rating|analyst|initiat',
    'deal': r'acqui|merger|buyout|deal|stake|partnership|partner',
    'legal/regulatory': r'lawsuit|sue|sec |probe|investigation|antitrust|regulator|fine|ban|export control|tariff',
    'product': r'launch|unveil|release|product|chip|model|platform',
    'management': r'ceo|cfo|resign|appoint|steps down|executive',
    'macro': r'fed|inflation|cpi|jobs|rates|treasury|oil|recession',
}


def _words(t):
    return {w for w in re.findall(r'[a-z0-9$%]+', t.lower()) if len(w) > 2 and w not in STOP}


def _outlet(item):
    o = item.get('source') or item.get('outlet')
    if o:
        return str(o).strip().lower()
    host = urlparse(item.get('url', '')).netloc.lower()
    return host[4:] if host.startswith('www.') else host


def normalise(webull=(), web=None, symbol=None, aliases=()):
    items = []
    for p in webull:
        obj = json.load(open(p))
        rows = obj.get('data', obj) if isinstance(obj, dict) else obj
        for r in rows or []:
            items.append({'title': r.get('title', '').strip(), 'summary': r.get('summary'), 'url': r.get('url'),
                          'outlet': _outlet(r), 'time': data.norm_time(r['publish_time']) if r.get('publish_time') else None,
                          'related': r.get('related_symbols') or [], 'sentiment': r.get('sentiment'), 'via': 'webull'})
    if web:
        rows = json.load(open(web)) if isinstance(web, str) else web
        for r in rows:
            items.append({'title': r.get('title', '').strip(), 'summary': r.get('snippet') or r.get('summary'),
                          'url': r.get('url'), 'outlet': _outlet(r),
                          'time': data.norm_time(r['date']) if r.get('date') else None,
                          'related': [], 'sentiment': None, 'via': 'web'})
    names = [n for n in ([symbol] if symbol else []) + list(aliases or []) if n]
    for x in items:
        text = f"{x['title']} {x.get('summary') or ''}"
        x['mentions'] = bool(symbol and symbol.upper() in x['related']) or any(
            re.search(rf'\b{re.escape(n)}\b', text, re.I) for n in names)
    return [x for x in items if x['title']]


def cluster(items, min_overlap=0.5, min_shared=3):
    """Group headlines: two headlines are the same story when they share at
    least `min_shared` words and that is at least half of the shorter one."""
    groups = []
    for x in sorted(items, key=lambda x: x['time'] or ''):
        w = _words(x['title'])
        best, bi = 0.0, None
        for gi, g in enumerate(groups):
            shared = len(w & g['words'])
            ov = shared / max(1, min(len(w), len(g['words'])))
            if shared >= min_shared and ov > best:
                best, bi = ov, gi
        if bi is not None and best >= min_overlap:
            groups[bi]['items'].append(x); groups[bi]['words'] |= w
        else:
            groups.append({'items': [x], 'words': set(w)})
    return groups


def _move_since(store, symbol, t):
    if not store or not symbol or not t:
        return None
    rows = data.read(store, symbol, 'M5')
    if not rows:
        return None
    after = [r for r in rows if r[0] >= t]
    if not after:
        return None
    ref = after[0][1]
    last = rows[-1][4]
    return {'from_bar_utc': after[0][0], 'price_then': ref, 'price_now': last,
            'move_pct': round((last / ref - 1) * 100, 2)}


def news(symbol=None, webull=(), web=None, days=14, store=None, now=None, aliases=()):
    now = now or datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=days)).strftime(data.FMT)
    items = [x for x in normalise(webull, web, symbol, aliases) if not x['time'] or x['time'] >= cutoff]
    stories = []
    for g in cluster(items):
        its = g['items']
        outlets = sorted({x['outlet'] for x in its if x['outlet']})
        first = min((x['time'] for x in its if x['time']), default=None)
        title = its[0]['title']
        tags = [k for k, rx in TAGS.items() if any(re.search(rx, x['title'].lower()) for x in its)]
        sents = {}
        for x in its:
            if x.get('sentiment'):
                sents[x['sentiment'].lower()] = sents.get(x['sentiment'].lower(), 0) + 1
        st_ = {'headline': title, 'first_seen_utc': first, 'outlets': outlets, 'items': len(its),
               'mentions_symbol': any(x['mentions'] for x in its),
               'confirmed': len(outlets) >= 2, 'tags': tags, 'feed_sentiment': sents or None,
               'links': [x['url'] for x in its if x.get('url')][:4]}
        mv = _move_since(store, symbol.upper() if symbol else None, first)
        if mv:
            st_['price_since_first_seen'] = mv
        stories.append(st_)
    conf = [s for s in stories if s['confirmed']]
    conf.sort(key=lambda s: s['first_seen_utc'] or '', reverse=True)
    unconf = sorted([s for s in stories if not s['confirmed']], key=lambda s: s['first_seen_utc'] or '', reverse=True)
    return {'tool': 'news-watch', 'generated_at': data.now_utc(), 'symbol': symbol.upper() if symbol else None,
            'window_days': days, 'items': len(items), 'stories': len(stories),
            'confirmed': conf, 'unconfirmed': unconf[:15],
            'note': 'Confirmed = carried by 2+ independent outlets in the window. Unconfirmed stories may be true, '
                    'but they are one outlet\'s report; check before acting on them. Headlines are not reasons for a move '
                    'unless a source says so.',
            'disclaimer': DISCLAIMER}


def render(r):
    L = [f"NEWS WATCH  {r['symbol'] or 'all'}: {r['stories']} stories from {r['items']} items, last {r['window_days']} days", '']
    L.append(f"confirmed by 2+ outlets ({len(r['confirmed'])}):")
    for s in r['confirmed'][:12]:
        mv = s.get('price_since_first_seen')
        L.append(f"  {s['first_seen_utc']}  {s['headline'][:110]}  [{', '.join(s['outlets'])}]"
                 + (f"  {r['symbol']} {mv['move_pct']:+.2f}% since" if mv else '') + (f"  tags: {', '.join(s['tags'])}" if s['tags'] else ''))
    L.append(f"\nsingle-source ({len(r['unconfirmed'])} most recent):")
    for s in r['unconfirmed'][:8]:
        L.append(f"  {s['first_seen_utc']}  {s['headline'][:110]}  [{', '.join(s['outlets'])}]")
    L += ['', r['note'], r['disclaimer']]
    return '\n'.join(L)
