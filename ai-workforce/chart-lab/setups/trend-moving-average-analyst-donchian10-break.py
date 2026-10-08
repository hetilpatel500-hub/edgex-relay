"""Intraday Donchian (10-bar) channel breakout.
Added 2026-10-02 by trend-moving-average-analyst: the research queue held only tape items, so this run took
the documented intraday Donchian idea (WebSearch: trendspider.com/learning-center/donchian-channel-trading-strategies,
luxalgo.com Donchian breakout: period 10-20 on 5-minute charts, close beyond the channel). The lab only had the daily
d_donchian20. Period 10 (50 minutes) fixed BEFORE any P&L was seen.
"""


def donchian10_break(s):
    """A 5-minute bar that closes above the highest high of the previous 10 bars leans long; below the lowest
    low of the previous 10 bars leans short. Signals from the 11th bar (10:20) to 14:55, at most one per
    direction per session."""
    b = s.bars
    n = 10
    done = set()
    for i in range(n, len(b)):
        if b[i].m >= 895:
            break
        hh = max(x.h for x in b[i - n:i])
        ll = min(x.l for x in b[i - n:i])
        if b[i].c > hh and 1 not in done:
            done.add(1)
            yield i, 1
        elif b[i].c < ll and -1 not in done:
            done.add(-1)
            yield i, -1


SETUPS = [
    dict(id='donchian10_break', name='Intraday Donchian 10-bar channel breakout', family='trend',
         detect=donchian10_break,
         rules="A 5-minute bar closing above the highest high of the previous 10 bars (50 minutes) leans long; "
               "closing below the lowest low of the previous 10 bars leans short. From 10:20 to 14:55, at most "
               "one signal per direction per session. Period fixed from published intraday defaults before testing."),
]
