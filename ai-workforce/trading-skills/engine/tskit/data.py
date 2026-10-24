"""Bar store and loaders.

A store is a directory of gzip CSV files named SYMBOL_TF.csv.gz, where TF is
M5 (5-minute bars) or D (daily bars), with columns t,o,h,l,c,v. `t` is the
bar's start time in UTC, ISO 8601 (2026-10-23T19:55:00Z). Daily bars use
midnight New York time for their date. This is the same layout the Edgex
chart lab keeps, so its data directory works as a store as-is.

Loaders accept:
  * Webull get_stock_bars responses saved as JSON (one or many symbols),
  * any JSON list of bars with time/open/high/low/close/volume keys,
  * CSV with a header naming time (or date + time), open, high, low, close
    and volume columns, in any order and case.
1-minute bars are rolled up into 5-minute bars. Coarser intraday bars
(15m, 30m, 1h) are refused, because they cannot be turned into 5-minute bars.
Naive timestamps (no offset) are read as New York time.
"""
import csv, gzip, io, json, os, re, statistics as st
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

ET = ZoneInfo('America/New_York')
UTC = timezone.utc
FMT = '%Y-%m-%dT%H:%M:%SZ'

ALIASES = {
    't': ('t', 'time', 'timestamp', 'datetime', 'date_time', 'start', 'start_time', 'begins_at'),
    'o': ('o', 'open', 'open_price'),
    'h': ('h', 'high', 'high_price'),
    'l': ('l', 'low', 'low_price'),
    'c': ('c', 'close', 'close_price'),
    'v': ('v', 'volume', 'vol'),
}


def data_dir(arg=None):
    return arg or os.environ.get('TSKIT_DATA') or os.path.join(os.getcwd(), 'market-data')


def norm_time(x):
    """UTC ISO string from an ISO timestamp (any offset), a bare date
    (midnight New York), or epoch seconds/milliseconds."""
    if isinstance(x, (int, float)) or (isinstance(x, str) and re.fullmatch(r'\s*\d{10,13}\s*', x)):
        v = float(x)
        v = v / 1000 if v > 1e11 else v
        return datetime.fromtimestamp(v, UTC).strftime(FMT)
    s = str(x).strip()
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', s) or re.fullmatch(r'\d{4}/\d{2}/\d{2}', s):
        d = datetime.strptime(s.replace('/', '-'), '%Y-%m-%d').replace(tzinfo=ET)
        return d.astimezone(UTC).strftime(FMT)
    s = s.replace(' ', 'T', 1) if 'T' not in s else s
    s = re.sub(r'Z$', '+00:00', s)
    s = re.sub(r'([+-]\d{2})(\d{2})$', r'\1:\2', s)
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=ET)
    return d.astimezone(UTC).strftime(FMT)


def et(t):
    return datetime.fromisoformat(t.replace('Z', '+00:00')).astimezone(ET)


def path(d, sym, tf):
    return os.path.join(d, f'{sym.upper()}_{tf}.csv.gz')


def read(d, sym, tf):
    """[(t, o, h, l, c, v)] sorted by time; [] when the file is missing."""
    p = path(d, sym, tf)
    if not os.path.exists(p):
        return []
    with gzip.open(p, 'rt') as fh:
        return [(r['t'], float(r['o']), float(r['h']), float(r['l']), float(r['c']), float(r['v']))
                for r in csv.DictReader(fh)]


def write(d, sym, tf, rows):
    os.makedirs(d, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator='\n')
    w.writerow(['t', 'o', 'h', 'l', 'c', 'v'])
    for r in rows:
        w.writerow([r[0]] + [f'{x:.6f}'.rstrip('0').rstrip('.') for x in r[1:5]] + [f'{r[5]:.0f}'])
    with gzip.open(path(d, sym, tf), 'wt') as fh:
        fh.write(buf.getvalue())


def symbols(d, tf='M5'):
    if not os.path.isdir(d):
        return []
    return sorted(f[:-len(f'_{tf}.csv.gz')] for f in os.listdir(d) if f.endswith(f'_{tf}.csv.gz'))


def merge(old, new):
    m = {r[0]: r for r in old}
    m.update({r[0]: r for r in new})
    return [m[k] for k in sorted(m)]


# ---- parsing ---------------------------------------------------------------
def _num(x):
    return float(str(x).replace(',', ''))


def _bar(r):
    """Map one dict with any alias keys to (t, o, h, l, c, v)."""
    low = {str(k).strip().lower(): v for k, v in r.items()}
    out = {}
    if low.get('date') and low.get('time') and not re.search(r'\d{4}-\d{2}-\d{2}', str(low['time'])):
        out['t'] = f"{low['date']} {low['time']}"
    for k, names in ALIASES.items():
        if k in out:
            continue
        for n in names:
            if n in low and low[n] not in (None, ''):
                out[k] = low[n]
                break
    if 't' not in out and 'date' in low:
        out['t'] = f"{low['date']} {low['time']}" if low.get('time') else low['date']
    if any(k not in out for k in 'tohlc'):
        raise ValueError(f'bar is missing a column: needs time, open, high, low, close (got {sorted(low)})')
    return (norm_time(out['t']), _num(out['o']), _num(out['h']), _num(out['l']), _num(out['c']),
            _num(out.get('v', 0) or 0))


def _rows_from_json(obj, symbol=None):
    """{symbol: [rows]} from a saved JSON response."""
    if isinstance(obj, dict) and isinstance(obj.get('result'), list) and obj['result'] and \
            isinstance(obj['result'][0], dict) and 'symbol' in obj['result'][0] and 'result' in obj['result'][0]:
        return {x['symbol'].upper(): [_bar(b) for b in x['result']] for x in obj['result']}
    if isinstance(obj, dict) and 'symbol' in obj and isinstance(obj.get('result') or obj.get('bars'), list):
        return {obj['symbol'].upper(): [_bar(b) for b in (obj.get('result') or obj.get('bars'))]}
    if isinstance(obj, dict) and isinstance(obj.get('data'), list):
        return _rows_from_json(obj['data'], symbol)
    if isinstance(obj, list):
        if obj and isinstance(obj[0], dict) and 'symbol' in obj[0] and 'result' in obj[0]:
            return _rows_from_json({'result': obj})
        if not symbol:
            raise ValueError('a plain list of bars needs --symbol')
        return {symbol.upper(): [_bar(b) for b in obj]}
    raise ValueError('unrecognised JSON layout for bars')


def _rows_from_csv(text, symbol):
    rd = csv.DictReader(io.StringIO(text))
    return {symbol.upper(): [_bar(r) for r in rd]}


def step_seconds(rows):
    ts = [datetime.strptime(r[0], FMT) for r in rows]
    gaps = [(b - a).total_seconds() for a, b in zip(ts, ts[1:]) if b > a]
    return st.median(gaps) if gaps else None


def to_m5(rows):
    """Roll 1-minute bars up into 5-minute bars aligned to :00, :05, ..."""
    out = {}
    for t, o, h, l, c, v in sorted(rows):
        d = datetime.strptime(t, FMT)
        k = d.replace(minute=d.minute - d.minute % 5, second=0).strftime(FMT)
        if k not in out:
            out[k] = [k, o, h, l, c, v]
        else:
            b = out[k]
            b[2], b[3], b[4], b[5] = max(b[2], h), min(b[3], l), c, b[5] + v
    return [tuple(out[k]) for k in sorted(out)]


def classify(rows):
    """('M5' | 'D', rows) with 1-minute bars rolled up; ValueError otherwise."""
    s = step_seconds(rows)
    if s is None:
        raise ValueError('need at least two bars to tell the timeframe')
    if s >= 20 * 3600:
        return 'D', rows
    if abs(s - 300) < 1:
        return 'M5', rows
    if abs(s - 60) < 1:
        return 'M5', to_m5(rows)
    raise ValueError(f'bars are {s/60:.0f} minutes apart; only 1-minute, 5-minute and daily bars are supported')


def load_file(p, symbol=None):
    """{symbol: {tf: rows}} from one saved file."""
    raw = open(p, 'rb').read()
    if p.endswith('.gz'):
        raw = gzip.decompress(raw)
    text = raw.decode('utf-8-sig')
    sym = symbol or re.split(r'[_.\-\s]', os.path.basename(p))[0]
    if text.lstrip()[:1] in '[{':
        bars = _rows_from_json(json.loads(text), symbol)
    else:
        bars = _rows_from_csv(text, sym)
    out = {}
    for s, rows in bars.items():
        if not rows:
            continue
        tf, rows = classify(sorted(set(rows)))
        out.setdefault(s, {})[tf] = rows
    return out


def ingest(files, d, symbol=None):
    """Merge saved bar files into the store. Returns a summary per file."""
    report = []
    for p in files:
        for sym, by_tf in load_file(p, symbol).items():
            for tf, rows in by_tf.items():
                old = read(d, sym, tf)
                new = merge(old, rows)
                write(d, sym, tf, new)
                report.append({'symbol': sym, 'tf': tf, 'before': len(old), 'after': len(new),
                               'first': new[0][0], 'last': new[-1][0], 'file': os.path.basename(p)})
    return report


def last_session_date(d, sym):
    rows = read(d, sym, 'M5')
    return et(rows[-1][0]).date() if rows else None


def now_utc():
    return datetime.now(UTC).strftime(FMT)


def parse_et_clock(day, hhmm):
    """Minutes after midnight ET from 'HH:MM'."""
    h, m = hhmm.split(':')
    return int(h) * 60 + int(m)


def utc_from_et(day, minutes):
    d = datetime(day.year, day.month, day.day, minutes // 60, minutes % 60, tzinfo=ET)
    return d.astimezone(UTC).strftime(FMT)


def add_days(day, n):
    return day + timedelta(days=n)
