"""Larry Williams smash-day reversal, intraday version on 5-minute bars.
Added 2026-10-14 by pattern-specialist via WebSearch (oxfordstrat.com smash day backtest series, roboforex.com and
mql5.com articles on Williams' smash day): the setup bar closes beyond the previous bar's extreme and the entry is a
break of the smash bar's far side. Published definitions leave the bar count open; the rules below were fixed BEFORE any
P&L was seen and are not tuned: 5-minute bar, smash bar range at least 1.0 ATR, close beyond the prior bar's extreme and
beyond the close 12 bars earlier (a one-hour flush), reversal confirmed within 3 bars.
"""


def smash_reversal(s):
    """A bar closes below the previous bar's low, below the close 12 bars earlier, with a range of at least 1 ATR (the
    smash). Within the next 3 bars a bar closes above the smash bar's high: long at that close. Mirror for shorts.
    10:30-15:00 ET, one signal per side per session."""
    b = s.bars
    done = {1: False, -1: False}
    pend = None  # (direction, smash index, level)
    for i in range(13, len(b)):
        if b[i].m < 630 or b[i].m >= 900:
            continue
        if pend:
            d, k, lvl = pend
            if i - k > 3:
                pend = None
            elif (d == 1 and b[i].c > lvl) or (d == -1 and b[i].c < lvl):
                pend = None
                if not done[d]:
                    done[d] = True
                    yield i, d
                continue
        atr = s.atr[i - 1]
        if not atr or b[i].h - b[i].l < atr:
            continue
        if b[i].c < b[i - 1].l and b[i].c < b[i - 12].c:
            pend = (1, i, b[i].h)
        elif b[i].c > b[i - 1].h and b[i].c > b[i - 12].c:
            pend = (-1, i, b[i].l)


SETUPS = [
    dict(id='smash_day_reversal', name='Williams smash-bar reversal (5-minute)', family='pattern',
         detect=smash_reversal,
         rules="A 5-minute bar of at least 1 ATR closes below the previous bar's low and below the close one hour "
               "earlier (a smash). If within three bars a bar closes back above the smash bar's high, that close leans "
               "long; mirror for a smash up. 10:30-15:00, one per side per session; tested with and against."),
]
