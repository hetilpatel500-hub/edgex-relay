"""New candidate setups for the A+ hunt (2026-09-29). Each one is a published
or widely documented idea, written by the Chart Desk agent that owns its
family, and fixed before any result was seen. Same contract as setups/*.py:
dict(id, name, family, rules, detect[, tf='D']); detect yields (bar index, +1/-1).
"""


def intraday_momentum(s):
    """momentum-analyst. Gao, Han, Li & Zhou (2018), "Market intraday momentum",
    Journal of Financial Economics: the first half-hour return (yesterday's
    close to 10:00) predicts the last half-hour return."""
    b, p = s.bars, s.prior
    if p is None or len(b) < 73:
        return
    i = next((k for k, x in enumerate(b) if x.m == 925), None)    # 15:25 bar, known at 15:30
    first = b[5].c - p.close                                       # 10:00 close vs yesterday
    if i is not None and first != 0:
        yield i, (1 if first > 0 else -1)


def orb30(s):
    """session-gap-specialist. 30-minute opening range breakout: the first
    5-minute close outside the 9:30-10:00 range, before 12:00, one per day."""
    b = s.bars
    hi, lo = max(x.h for x in b[:6]), min(x.l for x in b[:6])
    for i in range(6, len(b)):
        if b[i].m >= 720:
            return
        if b[i].c > hi:
            yield i, 1; return
        if b[i].c < lo:
            yield i, -1; return


def vwap_first_pullback(s):
    """volume-vwap-analyst. After a strong open (10:00 close at least 0.5 ATR
    beyond VWAP), the first pullback that touches VWAP and closes back on the
    trend side, before 13:00."""
    b = s.bars
    k = 5
    if not s.atr[k]:
        return
    gap = b[k].c - s.vwap[k]
    if abs(gap) < 0.5 * s.atr[k]:
        return
    d = 1 if gap > 0 else -1
    for i in range(k + 1, len(b)):
        if b[i].m >= 780:
            return
        touched = (b[i].l <= s.vwap[i]) if d == 1 else (b[i].h >= s.vwap[i])
        if touched:
            if (b[i].c > s.vwap[i]) if d == 1 else (b[i].c < s.vwap[i]):
                yield i, d
            return


def late_trend(s):
    """trend-moving-average-analyst. Trend-day continuation: at 15:00, price
    on the VWAP side of the move and at least 0.5 ATR beyond the open."""
    b = s.bars
    i = next((k for k, x in enumerate(b) if x.m == 895), None)     # 14:55 bar, known at 15:00
    if i is None or not s.atr[i]:
        return
    mv = b[i].c - s.open
    if abs(mv) >= 0.5 * s.atr[i] and (b[i].c - s.vwap[i]) * mv > 0:
        yield i, (1 if mv > 0 else -1)


def d_ibs(ser):
    """volatility-analyst. Internal bar strength (close position in the day's
    range): IBS below 0.2 leans long, above 0.8 leans short."""
    for i in range(1, len(ser.c)):
        rng = ser.h[i] - ser.l[i]
        if rng <= 0:
            continue
        ibs = (ser.c[i] - ser.l[i]) / rng
        if ibs < 0.2:
            yield i, 1
        elif ibs > 0.8:
            yield i, -1


def d_turnaround_tuesday(ser):
    """strategy-playbook-analyst. A down Monday (close below Friday's close)
    leans long from Tuesday's open."""
    for i in range(1, len(ser.c)):
        if ser.day[i].weekday() == 0 and ser.c[i] < ser.c[i - 1]:
            yield i, 1


def d_three_down(ser):
    """momentum-analyst. Three lower closes in a row lean long (short-term
    mean reversion, as popularised by Connors)."""
    for i in range(3, len(ser.c)):
        if ser.c[i] < ser.c[i - 1] < ser.c[i - 2] < ser.c[i - 3]:
            yield i, 1


SETUPS = [
    dict(id='n_intraday_momentum', name='Intraday momentum: first half hour predicts the last', family='momentum',
         detect=intraday_momentum, file='studies/aplus_hunt/new_setups.py',
         rules='At 15:30 ET, lean in the direction of the move from yesterday\'s close to 10:00 ET.'),
    dict(id='n_orb30', name='30-minute opening range breakout', family='breakout',
         detect=orb30, file='studies/aplus_hunt/new_setups.py',
         rules='First 5-minute close outside the 9:30-10:00 range, before 12:00; one per day.'),
    dict(id='n_vwap_first_pullback', name='First VWAP pullback after a strong open', family='vwap',
         detect=vwap_first_pullback, file='studies/aplus_hunt/new_setups.py',
         rules='10:00 close at least 0.5 ATR beyond VWAP; the first bar that touches VWAP and closes back on '
               'the trend side, before 13:00.'),
    dict(id='n_late_trend', name='Late-day trend continuation', family='trend',
         detect=late_trend, file='studies/aplus_hunt/new_setups.py',
         rules='At 15:00, price at least 0.5 ATR beyond the open and on the same side of VWAP: lean with it.'),
    dict(id='n_d_ibs', tf='D', name='Internal bar strength reversal (daily)', family='mean reversion (daily)',
         detect=d_ibs, file='studies/aplus_hunt/new_setups.py',
         rules='Close in the bottom 20% of the day\'s range: long next open; top 20%: short.'),
    dict(id='n_d_turnaround_tuesday', tf='D', name='Turnaround Tuesday (daily)', family='calendar (daily)',
         detect=d_turnaround_tuesday, file='studies/aplus_hunt/new_setups.py',
         rules='Monday closes below Friday: long at Tuesday\'s open.'),
    dict(id='n_d_three_down', tf='D', name='Three lower closes (daily)', family='mean reversion (daily)',
         detect=d_three_down, file='studies/aplus_hunt/new_setups.py',
         rules='Three consecutive lower closes: long next open.'),
]


# ---- Round 2 (2026-09-29): new documented ideas, added after round 1. They
# count toward the Bonferroni correction together with every round-1 idea.

def d_bollinger_low(ser):
    """volatility-analyst. Close below the lower 20-day Bollinger band (2 sd):
    lean long for a snap-back."""
    import statistics as st
    for i in range(20, len(ser.c)):
        w = ser.c[i - 19:i + 1]
        m, sd = sum(w) / 20, st.pstdev(w)
        if sd > 0 and ser.c[i] < m - 2 * sd:
            yield i, 1


def d_seven_day_low(ser):
    """momentum-analyst. Close at a 7-day closing low ("double 7s", Connors &
    Alvarez): lean long."""
    for i in range(7, len(ser.c)):
        if ser.c[i] <= min(ser.c[i - 6:i + 1]):
            yield i, 1


def d_turn_of_month(ser):
    """strategy-playbook-analyst. Turn-of-the-month effect (Lakonishok & Smidt
    1988; McConnell & Xu 2008): long from the last trading day's close into the
    first days of the new month."""
    for i in range(len(ser.c) - 1):
        if ser.day[i + 1].month != ser.day[i].month:
            yield i, 1


def d_gap_down_reversal(ser):
    """session-gap-specialist. A day that opens below the prior day's low and
    closes back above its open: lean long."""
    for i in range(1, len(ser.c)):
        if ser.o[i] < ser.l[i - 1] and ser.c[i] > ser.o[i]:
            yield i, 1


ROUND2 = [
    dict(id='n2_d_bollinger_low', tf='D', name='Close below the lower Bollinger band (daily)', family='mean reversion (daily)',
         detect=d_bollinger_low, file='studies/aplus_hunt/new_setups.py',
         rules='Close below the 20-day mean minus 2 standard deviations: long next open.'),
    dict(id='n2_d_seven_day_low', tf='D', name='7-day closing low (daily)', family='mean reversion (daily)',
         detect=d_seven_day_low, file='studies/aplus_hunt/new_setups.py',
         rules='Close at the lowest close of the last 7 days: long next open.'),
    dict(id='n2_d_turn_of_month', tf='D', name='Turn of the month (daily)', family='calendar (daily)',
         detect=d_turn_of_month, file='studies/aplus_hunt/new_setups.py',
         rules='At the last trading day of the month: long from the next open.'),
    dict(id='n2_d_gap_down_reversal', tf='D', name='Gap-down reversal day (daily)', family='gap (daily)',
         detect=d_gap_down_reversal, file='studies/aplus_hunt/new_setups.py',
         rules='Open below yesterday\'s low and close above the open: long next open.'),
]
