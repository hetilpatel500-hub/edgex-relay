"""Bill Williams Market Facilitation Index "green" bar as trend continuation, 5-minute bars.
Added 2026-10-13 by volatility-analyst (WebSearch 2026-10-13: Williams' MFI = range / volume; a green bar has
MFI UP and volume UP versus the previous bar, read as new participants joining the move). squat_bar_reversal
already tests the opposite state (volume up, MFI down). Rules fixed BEFORE any P&L was seen: green bar as
defined, body >= 60% of range, relative volume >= 1.2, close beyond the prior 6 bars' highest high (lowest low),
10:00 to 14:30 ET, direction = the bar's direction, signal on that bar's close, at most two a session.
"""


def williams_green_bar(s):
    b = s.bars
    fired = 0
    for i in range(7, len(b)):
        if b[i].m < 600 or b[i].m >= 870 or fired >= 2:
            continue
        rng, prng = b[i].h - b[i].l, b[i - 1].h - b[i - 1].l
        rv = s.rvol[i]
        if rng <= 0 or prng <= 0 or not b[i].v or not b[i - 1].v or not rv or rv < 1.2:
            continue
        if not (b[i].v > b[i - 1].v and rng / b[i].v > prng / b[i - 1].v):
            continue
        if abs(b[i].c - b[i].o) < 0.6 * rng:
            continue
        if b[i].c > b[i].o and b[i].c > max(x.h for x in b[i - 6:i]):
            fired += 1; yield i, 1
        elif b[i].c < b[i].o and b[i].c < min(x.l for x in b[i - 6:i]):
            fired += 1; yield i, -1


SETUPS = [
    dict(id='williams_green_bar', name='Williams MFI green bar breaking the 6-bar range', family='volatility',
         detect=williams_green_bar,
         rules="A 5-minute bar where volume and range-per-volume (Williams' Market Facilitation Index) both rise "
               "versus the previous bar, body at least 60% of range, relative volume at least 1.2, closing beyond "
               "the prior six bars' high (or low), 10:00 to 14:30 ET, at most two a session. Leans with the bar. "
               "Tested with and against."),
]
