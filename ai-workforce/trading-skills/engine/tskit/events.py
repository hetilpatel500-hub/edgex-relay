"""Event calendar: earnings and economic releases that can move a stock.

Earnings come from saved get_stock_earnings_calendar responses (one per
symbol; the response does not name the symbol, so pass SYMBOL=FILE).
Economic releases come from saved get_macroeconomic_calendar responses.
Flags:
  * earnings within N days (default 5) — and a stronger flag the day of and
    the day before, when the report can gap the stock overnight; the feed
    does not say whether a report is before the open or after the close;
  * high-impact releases today (inflation, jobs, GDP, retail sales, ISM,
    Fed decisions and the Fed chair) with their New York time — moves often
    spike in the minutes around them;
  * Fed speakers today (lower impact).
"""
import json, re
from datetime import datetime, timedelta
from . import data, DISCLAIMER

HIGH = re.compile(r'\b(CPI|PPI|PCE|core pce|nonfarm|non-farm|payrolls|employment situation|unemployment rate|'
                  r'GDP|retail sales|ISM|JOLTS|FOMC|fed funds|interest rate decision|rate decision|powell|fed chair|'
                  r'consumer price|producer price|initial jobless)\b', re.I)


def _date(s):
    return datetime.strptime(s[:10], '%Y-%m-%d').date()


def earnings(sym, rows, today, days):
    rows = rows.get('data', rows) if isinstance(rows, dict) else rows
    past = [r for r in rows if r.get('eps_actual') not in (None, '')]
    up = sorted([r for r in rows if r.get('eps_actual') in (None, '') and r.get('expected_publish_date')
                 and _date(r['expected_publish_date']) >= today], key=lambda r: r['expected_publish_date'])
    out = {'symbol': sym, 'next': None, 'last': None}
    flags = []
    if up:
        n = up[0]
        dd = (_date(n['expected_publish_date']) - today).days
        out['next'] = {'date': n['expected_publish_date'], 'days_until': dd,
                       'fiscal': f"FY{n.get('fiscal_year')} Q{n.get('fiscal_period')}",
                       'eps_estimate': n.get('eps_est'), 'revenue_estimate': n.get('rev_est')}
        if dd <= 1:
            flags.append({'symbol': sym, 'severity': 'high',
                          'flag': f"{sym} reports earnings {'today' if dd == 0 else 'tomorrow'} ({n['expected_publish_date']}); "
                                  "the stock can gap; the feed does not say before the open or after the close"})
        elif dd <= days:
            flags.append({'symbol': sym, 'severity': 'medium',
                          'flag': f"{sym} reports earnings in {dd} days ({n['expected_publish_date']})"})
    if past:
        p = sorted(past, key=lambda r: r['expected_publish_date'])[-1]
        try:
            surprise = (float(p['eps_actual']) / float(p['eps_est']) - 1) * 100 if float(p['eps_est']) else None
        except (TypeError, ValueError):
            surprise = None
        out['last'] = {'date': p['expected_publish_date'], 'eps_actual': p.get('eps_actual'), 'eps_estimate': p.get('eps_est'),
                       'eps_surprise_pct': None if surprise is None else round(surprise, 1)}
    return out, flags


def macro(rows, today, days):
    rows = rows.get('data', rows) if isinstance(rows, dict) else rows
    todays, upcoming, flags = [], [], []
    for r in rows:
        if not r.get('publish_time') and not r.get('publish_date'):
            continue
        t = data.et(data.norm_time(r['publish_time'])) if r.get('publish_time') else None
        day = t.date() if t else _date(r['publish_date'])
        imp = 'high' if HIGH.search(r.get('event_name', '')) else ('fed' if r.get('is_fed_related') else 'low')
        item = {'date': str(day), 'time_et': t.strftime('%H:%M') if t else None, 'event': r.get('event_name', '').strip(),
                'impact': imp, 'forecast': r.get('forecast_value'), 'prior': r.get('prior_value')}
        if day == today:
            todays.append(item)
            if imp == 'high':
                flags.append({'symbol': '*', 'severity': 'high',
                              'flag': f"{item['event']} at {item['time_et']} ET today: prices often jump in the minutes around it"})
            elif imp == 'fed':
                flags.append({'symbol': '*', 'severity': 'low', 'flag': f"Fed speaker at {item['time_et']} ET today"})
        elif today < day <= today + timedelta(days=days) and imp in ('high', 'fed'):
            upcoming.append(item)
    key = lambda x: (x['date'], x['time_et'] or '')
    return sorted(todays, key=key), sorted(upcoming, key=key), flags


def calendar(earnings_files=None, macro_files=None, today=None, days=5):
    """earnings_files: {SYMBOL: path}; macro_files: [path]."""
    today = today or datetime.now(data.ET).date()
    if isinstance(today, str):
        today = _date(today)
    ern, flags = [], []
    for sym, p in (earnings_files or {}).items():
        e, f = earnings(sym.upper(), json.load(open(p)), today, days)
        ern.append(e); flags += f
    mt, mu = [], []
    for p in macro_files or []:
        a, b, f = macro(json.load(open(p)), today, days)
        mt += a; mu += b; flags += f
    order = {'high': 0, 'medium': 1, 'low': 2}
    flags.sort(key=lambda f: order[f['severity']])
    return {'tool': 'event-calendar', 'generated_at': data.now_utc(), 'today': str(today), 'window_days': days,
            'flags': flags, 'earnings': ern, 'macro_today': mt, 'macro_upcoming': mu, 'disclaimer': DISCLAIMER}


def render(r):
    L = [f"EVENT CALENDAR  {r['today']} (next {r['window_days']} days)", '']
    L += [f"[{f['severity']}] {f['flag']}" for f in r['flags']] or ['No flags.']
    if r['macro_today']:
        L += ['', 'today (ET):'] + [f"  {m['time_et']}  {m['event']}  ({m['impact']}; forecast {m['forecast'] or '-'}, prior {m['prior'] or '-'})"
                                    for m in r['macro_today'] if m['impact'] != 'low']
    if r['macro_upcoming']:
        L += ['', 'coming up:'] + [f"  {m['date']} {m['time_et']}  {m['event']} ({m['impact']})" for m in r['macro_upcoming'][:12]]
    for e in r['earnings']:
        n, p = e['next'], e['last']
        s = f"{e['symbol']}: next earnings {n['date']} ({n['days_until']} days, EPS est {n['eps_estimate']})" if n else \
            f"{e['symbol']}: no upcoming date in the feed"
        if p and p.get('eps_surprise_pct') is not None:
            s += f"; last report {p['date']} EPS {p['eps_actual']} vs {p['eps_estimate']} ({p['eps_surprise_pct']:+.1f}%)"
        L.append(s)
    L += ['', r['disclaimer']]
    return '\n'.join(L)
