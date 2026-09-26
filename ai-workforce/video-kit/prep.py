#!/usr/bin/env python3
"""Turn raw Webull bar responses into story.json: every number a video shows,
plus a first-draft script the writers can edit.

usage: prep.py RAW_SPY_M5.json RAW_DAILY.json OUT_story.json [--mag]

RAW files are the Webull get_stock_bars responses saved exactly as returned:
  spy_m5.json : symbols ["SPY"], category US_ETF, timespan M5,
                trading_sessions RTH, count 160
  daily.json  : symbols AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,SPY,QQQ,
                category US_STOCK, timespan D, count 10
Only the writers' fields under "script" and "captions" may be edited after
this runs. Numbers under "spy"/"mag"/"facts" must come from this script.
"""
import json, sys, statistics
from datetime import datetime, timedelta, timezone

MAG7 = ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA']
DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
LONG = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
MON3 = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def die(msg):
    print('PREP FAILED:', msg, file=sys.stderr)
    sys.exit(2)


def parse_t(s):
    s = s.replace('Z', '+00:00')
    if len(s) > 5 and s[-5] in '+-' and s[-3] != ':':
        s = s[:-2] + ':' + s[-2:]
    return datetime.fromisoformat(s)


def eastern(dt):
    """US Eastern time without tz data: EDT 2nd Sun Mar - 1st Sun Nov."""
    y = dt.year
    mar = datetime(y, 3, 8, 7, tzinfo=timezone.utc)
    mar += timedelta(days=(6 - mar.weekday()) % 7)
    nov = datetime(y, 11, 1, 6, tzinfo=timezone.utc)
    nov += timedelta(days=(6 - nov.weekday()) % 7)
    off = -4 if mar <= dt < nov else -5
    return dt + timedelta(hours=off)


def series(raw, sym):
    for blk in raw.get('result', []):
        if blk.get('symbol') == sym:
            return blk.get('result', [])
    die(f'{sym} missing from response')


def f(x):
    return float(x)


def pct(a, b):
    return (a / b - 1) * 100


def sg(v, d=2):
    return ('+' if v >= 0 else '−') + f'{abs(v):.{d}f}'


def hm(m):
    h, mm = divmod(m, 60)
    return f'{(h - 1) % 12 + 1}:{mm:02d}'


def main():
    if len(sys.argv) < 4:
        die(__doc__)
    spy_raw = json.load(open(sys.argv[1]))
    day_raw = json.load(open(sys.argv[2]))
    want_mag = '--mag' in sys.argv

    # ---- SPY session ----
    bars = []
    for b in series(spy_raw, 'SPY'):
        if b.get('trading_session') not in ('RTH', '', None):
            continue
        et = eastern(parse_t(b['time']))
        bars.append(dict(date=et.date().isoformat(), m=et.hour * 60 + et.minute,
                         o=f(b['open']), h=f(b['high']), l=f(b['low']), c=f(b['close']),
                         v=int(float(b['volume'])), iso=b['time']))
    if not bars:
        die('no SPY bars')
    def complete(d):
        rs = sorted([b for b in bars if b['date'] == d], key=lambda b: b['m'])
        return (rs and rs[0]['m'] == 570 and rs[-1]['m'] in (955, 775)
                and all(y['m'] - x['m'] == 5 for x, y in zip(rs, rs[1:]))), rs
    done = [d for d in sorted({b['date'] for b in bars}) if complete(d)[0]]
    if not done:
        die('no complete regular session in the SPY bars (need 9:30-3:55 ET with no gaps; fetch count 160)')
    sess = done[-1]
    R = complete(sess)[1]
    newest = max(b['date'] for b in bars)
    if newest != sess:
        print(f'note: {newest} is still in progress; using the last complete session {sess}', file=sys.stderr)

    spyd = sorted(series(day_raw, 'SPY'), key=lambda b: b['time'])
    dd = [(eastern(parse_t(b['time']) + timedelta(hours=8)).date().isoformat(), b) for b in spyd]
    prior = [b for d, b in dd if d < sess]
    today = [b for d, b in dd if d == sess]
    if not prior:
        die('daily SPY bars do not include the prior session')
    prev = f(prior[-1]['close'])
    prev_date = [d for d, b in dd if d < sess][-1]
    if today and abs(f(today[0]['close']) - R[-1]['c']) > 0.05:
        print(f'note: daily close {today[0]["close"]} vs last 5m close {R[-1]["c"]}', file=sys.stderr)

    cv = cpv = 0
    for r in R:
        tp = (r['h'] + r['l'] + r['c']) / 3
        cpv += tp * r['v']; cv += r['v']; r['vw'] = round(cpv / cv, 3)
        r['t'] = hm(r['m'])
    N = len(R)
    o, c = R[0]['o'], R[-1]['c']
    hiI = max(range(N), key=lambda i: R[i]['h'])
    loI = min(range(N), key=lambda i: R[i]['l'])
    bigI = max(range(N), key=lambda i: abs(R[i]['c'] - R[i]['o']))
    medv = statistics.median(r['v'] for r in R)
    gap = pct(o, prev)
    sd = datetime.fromisoformat(sess)
    pd_ = datetime.fromisoformat(prev_date)
    dname, pname = LONG[sd.weekday()], LONG[pd_.weekday()]
    fillI = None
    if gap < 0:
        fillI = next((i for i, r in enumerate(R) if r['h'] >= prev), None)
    elif gap > 0:
        fillI = next((i for i, r in enumerate(R) if r['l'] <= prev), None)

    big = R[bigI]
    bigmv = big['c'] - big['o']
    marks = []
    gtxt = 'Gap down' if gap <= -0.15 else 'Gap up' if gap >= 0.15 else 'Flat open'
    marks.append(dict(i=0, p=o, label='OPEN', color='red' if gap < 0 else 'green' if gap > 0 else 'ink',
                      title=f'{gtxt} at the open',
                      body=f'Opened {o:.2f}, {sg(gap)}% vs {pname}\'s close of {prev:.2f}.'))
    marks.append(dict(i=loI, p=R[loI]['l'], label='LOW', color='red', title=f'Low of day · {R[loI]["t"]} ET',
                      body=f'{R[loI]["l"]:.2f}, {sg(pct(R[loI]["l"], prev))}% vs {pname}\'s close.'))
    fills = fillI == bigI
    marks.append(dict(i=bigI, p=big['h'] if bigmv >= 0 else big['l'], label='FILL' if fills else 'BIG', color='amber',
                      title=f'The {big["t"]} candle',
                      body=f'{"+" if bigmv >= 0 else "−"}${abs(bigmv):.2f} in five minutes on {big["v"]/1e6:.2f}M shares '
                           f'(~{round(big["v"]/medv)}× a typical bar).' + (' Its move filled the gap.' if fills else '')))
    marks.append(dict(i=hiI, p=R[hiI]['h'], label='HIGH', color='green', title=f'High of day · {R[hiI]["t"]} ET',
                      body=f'{R[hiI]["h"]:.2f}, {sg(pct(R[hiI]["h"], prev))}% vs {pname}\'s close.'))
    marks.append(dict(i=N - 1, p=c, label='CLOSE', color='ink', title='Close',
                      body=f'{c:.2f}. {sg(pct(c, o))}% from the open, {sg(pct(c, prev))}% on the day.'))
    # one mark per bar, in time order
    seen, mk = set(), []
    for m in sorted(marks, key=lambda m: (m['i'], ['OPEN', 'LOW', 'HIGH', 'FILL', 'BIG', 'CLOSE'].index(m['label']))):
        if m['i'] in seen and m['label'] not in ('CLOSE',):
            continue
        seen.add(m['i']); mk.append(m)

    day = pct(c, prev)
    line1 = (f'SPY gapped down {abs(gap):.2f}%.' if gap <= -0.15 else
             f'SPY gapped up {gap:.2f}%.' if gap >= 0.15 else 'SPY opened flat.')
    if fillI is not None:
        line2 = f'The gap filled at {R[fillI]["t"]}.'
    else:
        line2 = f'It closed {sg(pct(c, o))}% from the open.'
    spy = dict(
        session=sess, dayName=dname, prevName=pname, prev=prev,
        subtitle=f'{dname}, {MON3[sd.month-1]} {sd.day} · 5-minute candles',
        kicker=f'SPY · {dname.upper()} {MON3[sd.month-1].upper()} {sd.day}',
        prevLabel=f'{pname[:3].upper()} CLOSE {prev:.2f}',
        rows=[{k: r[k] for k in ('t', 'o', 'h', 'l', 'c', 'v', 'vw')} for r in R],
        hiI=hiI, loI=loI, bigI=bigI, fillI=fillI, medv=medv, marks=mk,
        stats=[['Open', f'{o:.2f}', 'ink'], ['Close', f'{c:.2f}', 'ink'],
               ['High', f'{R[hiI]["h"]:.2f}', 'green'], ['Low', f'{R[loI]["l"]:.2f}', 'red'],
               ['Open → close', sg(pct(c, o)) + '%', 'green' if c >= o else 'red'],
               [f'Day vs {pname[:3]}', sg(day) + '%', 'green' if day >= 0 else 'red'],
               ['Range', f'${R[hiI]["h"] - R[loI]["l"]:.2f}', 'ink'],
               ['Close vs VWAP', f'{"above" if c > R[-1]["vw"] else "below"} {R[-1]["vw"]:.2f}', 'ink']],
    )
    facts = [
        dict(claim=f'{pname} close', value=f'{prev:.2f}', source=f'daily SPY bar {prev_date}'),
        dict(claim='Open', value=f'{o:.2f}', source=f'5m bar {R[0]["iso"]} open'),
        dict(claim='Gap vs prior close', value=sg(gap) + '%', source='open / prior close - 1'),
        dict(claim='Low of day', value=f'{R[loI]["l"]:.2f} at {R[loI]["t"]} ET', source=f'5m bar {R[loI]["iso"]} low'),
        dict(claim='High of day', value=f'{R[hiI]["h"]:.2f} at {R[hiI]["t"]} ET', source=f'5m bar {R[hiI]["iso"]} high'),
        dict(claim='Biggest candle', value=f'{"+" if bigmv >= 0 else "−"}${abs(bigmv):.2f} on {big["v"]:,} shares at {big["t"]} ET',
             source=f'5m bar {big["iso"]} close - open, volume'),
        dict(claim='Volume multiple', value=f'~{round(big["v"]/medv)}x', source=f'volume / median 5m volume {medv:,.0f}'),
        dict(claim='Close', value=f'{c:.2f}', source=f'5m bar {R[-1]["iso"]} close'),
        dict(claim='Day change', value=sg(day) + '%', source='close / prior close - 1'),
        dict(claim='VWAP at close', value=f'{R[-1]["vw"]:.2f}', source='cumulative typical price x volume over the 5m bars'),
    ]
    if fillI is not None:
        facts.append(dict(claim='Gap filled', value=f'{R[fillI]["t"]} ET', source=f'first 5m bar reaching {prev:.2f}: {R[fillI]["iso"]}'))
    def ud(v):
        return ('up ' if v >= 0 else 'down ') + f'{abs(v):.2f}%'
    vo_marks = []
    for m in mk:
        r = R[m['i']]
        if m['label'] == 'OPEN':
            vo_marks.append(f'It opened at {o:.2f}.')
        elif m['label'] == 'LOW':
            vo_marks.append(f'The low came at {r["t"]}, at {r["l"]:.2f}.')
        elif m['label'] in ('BIG', 'FILL'):
            vo_marks.append(f'Then the {r["t"]} candle {"jumped" if bigmv >= 0 else "dropped"} ${abs(bigmv):.2f} in five minutes, '
                            f'on {round(big["v"]/medv)} times normal volume' + (', filling the gap.' if m['label'] == 'FILL' else '.'))
        elif m['label'] == 'HIGH':
            vo_marks.append(f'High of day at {r["t"]}: {r["h"]:.2f}.')
        elif m['label'] == 'CLOSE':
            vo_marks.append(f'It closed at {c:.2f}, {ud(day)} on the day.')
    story = dict(
        generated_at=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        spy=spy,
        script=dict(spy=dict(hook=dict(lines=[line1, line2], hl=[w for w in (line1 + ' ' + line2).split() if '%' in w or ':' in w]),
                             outro=dict(lines=[f'Close {c:.2f},', f'{sg(day)}% on the day.'], hl=[f'{sg(day)}%'],
                                        sub='Follow for the SPY tape every trading day.'),
                             vo=dict(hook=f'{line1} {line2}', marks=vo_marks,
                                     stats=f'Open to close: {ud(pct(c, o))}. The range was ${R[hiI]["h"] - R[loI]["l"]:.2f}.',
                                     outro='Follow for the SPY tape, every trading day.'))),
        captions=dict(spy=dict(
            title=f'SPY {dname} {MON3[sd.month-1]} {sd.day}: ' + line1.replace('SPY ', '').rstrip('.') + (', then filled it' if fillI is not None else ''),
            text=f'{line1} {line2} Low {R[loI]["l"]:.2f} at {R[loI]["t"]} ET, high {R[hiI]["h"]:.2f} at {R[hiI]["t"]} ET, '
                 f'close {c:.2f} ({sg(day)}% on the day).\n\nData: Webull 5-min bars. Educational only, not financial advice.\n'
                 '#SPY #stockmarket #daytrading #trading #investing #SP500')),
        facts=dict(spy=facts),
    )

    # ---- Mag 7 week ----
    if want_mag:
        wk_start = sd - timedelta(days=sd.weekday())  # Monday of the session's week
        closes, dates = {}, None
        for sym in MAG7 + ['SPY', 'QQQ']:
            s = sorted(series(day_raw, sym), key=lambda b: b['time'])
            ds = [(eastern(parse_t(b['time']) + timedelta(hours=8)).date(), f(b['close'])) for b in s]
            base = [x for x in ds if x[0] < wk_start.date()]
            wk = [x for x in ds if wk_start.date() <= x[0] <= sd.date()]
            if not base or not wk:
                die(f'{sym}: need the prior week\'s last close and this week\'s closes')
            seq = [base[-1]] + wk
            if dates is None:
                dates = [d for d, _ in seq]
            elif [d for d, _ in seq] != dates:
                die(f'{sym}: dates do not line up with the others')
            closes[sym] = [v for _, v in seq]
        if len(dates) < 3:
            die('fewer than two sessions this week; skip the Mag 7 video today')
        P = {k: [round(pct(v, cl[0]), 3) for v in cl] for k, cl in closes.items()}
        fin = {k: P[k][-1] for k in MAG7}
        lead = max(fin, key=fin.get); lag = min(fin, key=fin.get)
        daych = [pct(closes[lead][i], closes[lead][i - 1]) for i in range(1, len(dates))]
        bi = max(range(len(daych)), key=lambda i: daych[i])
        others = [fin[k] for k in MAG7 if k != lead]
        nd = len(dates) - 1
        labels = [f'{DAYS[d.weekday()]} {d.month}/{d.day}' for d in dates]
        span = f'{LONG[dates[0].weekday()][:3]} {dates[0].month}/{dates[0].day} close → {LONG[dates[-1].weekday()][:3]} {dates[-1].month}/{dates[-1].day} close'
        words = {2: 'two', 3: 'three', 4: 'four', 5: 'five'}
        story['mag'] = dict(names=MAG7, pct=P, closes=closes, days=labels, span=span,
                            lead=lead, lag=lag,
                            reveal=dict(name=lead, pct=sg(fin[lead], 1) + '%', frm=f'${closes[lead][0]:.2f}', to=f'${closes[lead][-1]:.2f}',
                                        rows=[[f'Best day: {LONG[dates[bi+1].weekday()]}', sg(daych[bi], 1) + '%', 'green' if daych[bi] >= 0 else 'red'],
                                              [f'Worst of the 7: {lag}', sg(fin[lag], 1) + '%', 'green' if fin[lag] >= 0 else 'red'],
                                              ['S&P 500 (SPY)', sg(P['SPY'][-1], 1) + '%', 'ink'],
                                              ['Nasdaq-100 (QQQ)', sg(P['QQQ'][-1], 1) + '%', 'ink']]))
        story['script']['mag'] = dict(
            hook=dict(kicker='MAGNIFICENT 7 · THIS WEEK',
                      lines=[f'One Mag 7 stock went', f'{sg(fin[lead],1)}% in {words.get(nd, str(nd))} days.'],
                      hl=[f'{sg(fin[lead],1)}%'], sub='Can you guess which?'),
            outro=dict(lines=['Who wins', 'next week?'], hl=['next'], sub='Follow for the weekly Mag 7 scoreboard.'),
            vo=dict(hook=f'One Mag 7 stock went {"up" if fin[lead] >= 0 else "down"} {abs(fin[lead]):.1f}% in {words.get(nd, str(nd))} days. Can you guess which?',
                    race=f'Here is the week, from {LONG[dates[0].weekday()]}\'s close.',
                    rev=f'It\'s {lead}. {"Up" if fin[lead] >= 0 else "Down"} {abs(fin[lead]):.1f}%, from {closes[lead][0]:.2f} to {closes[lead][-1]:.2f}. '
                        f'Its best day was {LONG[dates[bi+1].weekday()]}, {"up" if daych[bi] >= 0 else "down"} {abs(daych[bi]):.1f}%. '
                        f'The worst of the seven was {lag}, {"up" if fin[lag] >= 0 else "down"} {abs(fin[lag]):.1f}%.',
                    outro='Who wins next week? Follow for the weekly Mag 7 scoreboard.'))
        story['captions']['mag'] = dict(
            title=f'One Mag 7 stock went {sg(fin[lead],1)}% this week',
            text=f'{lead} {sg(fin[lead],1)}% ({closes[lead][0]:.2f} → {closes[lead][-1]:.2f}) while the other six moved between '
                 f'{sg(min(others),1)}% and {sg(max(others),1)}%. Did you guess it before the reveal?\n\n'
                 f'{span}. Data: Webull. Educational only, not financial advice.\n#{lead} #Magnificent7 #stocks #stockmarket #investing')
        story['facts']['mag'] = [dict(claim=f'{k} change', value=sg(P[k][-1], 2) + '%',
                                      source=f'{closes[k][0]:.2f} ({dates[0]}) → {closes[k][-1]:.2f} ({dates[-1]}) daily closes')
                                 for k in MAG7 + ['SPY', 'QQQ']] + [
            dict(claim=f'{lead} best day', value=sg(daych[bi], 2) + '%', source=f'{dates[bi]} → {dates[bi+1]} closes')]

    json.dump(story, open(sys.argv[3], 'w'), indent=1, ensure_ascii=False)
    print(f'story for session {sess} written to {sys.argv[3]}' + (' (with Mag 7)' if want_mag else ''))


if __name__ == '__main__':
    main()
