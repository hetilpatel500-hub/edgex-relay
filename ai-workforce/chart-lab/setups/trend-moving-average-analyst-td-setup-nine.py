"""TD Sequential setup 9 (perfected) on 5-minute bars.
Added 2026-09-29 by trend-moving-average-analyst: the queue's non-tape lines are
all coded, so this run used WebSearch (Tom DeMark, "Applying TD Sequential to
intraday charts", Futures, April 1997; TrendSpider and TradingMan guides) for a
documented, untested exhaustion count.
"""


def td_setup_nine(s):
    """Buy setup: nine consecutive closes each below the close four bars
    earlier, counted inside one session (the count resets at the open and on any
    break). Perfected when the low of bar 8 or 9 is at or below the lows of bars
    6 and 7 (DeMark's rule). The signal is bar 9's close, before 15:00, leaning
    long; the sell setup (nine closes above the close four bars earlier, high of
    bar 8 or 9 at or above the highs of bars 6 and 7) leans short. One signal
    per direction per session."""
    b = s.bars
    up = dn = 0
    done = set()
    for i in range(4, len(b)):
        if b[i].m >= 900:
            return
        dn = dn + 1 if b[i].c < b[i - 4].c else 0
        up = up + 1 if b[i].c > b[i - 4].c else 0
        if dn == 9 and 1 not in done:
            lows = [x.l for x in b[i - 8:i + 1]]  # bars 1..9
            if min(lows[7], lows[8]) <= min(lows[5], lows[6]):
                done.add(1)
                yield i, 1
        if up == 9 and -1 not in done:
            highs = [x.h for x in b[i - 8:i + 1]]
            if max(highs[7], highs[8]) >= max(highs[5], highs[6]):
                done.add(-1)
                yield i, -1


SETUPS = [
    dict(id='td_setup_nine', name='TD Sequential setup 9 (perfected)', family='trend',
         detect=td_setup_nine,
         rules="Nine consecutive 5-minute closes each below (above) the close four bars earlier inside one "
               "session, with bar 8 or 9 making a lower low (higher high) than bars 6 and 7, leans long "
               "(short) at bar 9's close before 15:00 as an exhaustion signal."),
]
