"""Morning extreme retest failure (double top / bottom of the day).
Added 2026-09-30 by pattern-specialist: classic double-top/bottom idea, but
anchored to the session's own morning extreme rather than a prior-day level.
Rules fixed before any P&L was seen; everything is known at the signal bar's
close (the running high/low is built bar by bar, no look-ahead).
"""


def morning_extreme_retest(s):
    b = s.bars
    hi_i = lo_i = 0
    done = set()
    for i in range(1, len(b)):
        if b[i].h > b[hi_i].h:
            hi_i = i
        if b[i].l < b[lo_i].l:
            lo_i = i
        if b[i].m < 720 or b[i].m >= 900:
            continue
        a = s.atr[i]
        # morning high set before 11:00, pulled back >=1.5 ATR, now retested without a new high
        if 1 not in done and b[hi_i].m < 660 and b[i].h < b[hi_i].h:
            dip = b[hi_i].h - min(x.l for x in b[hi_i:i + 1])
            if dip >= 1.5 * a and b[i].h >= b[hi_i].h - 0.15 * a and b[i].c <= b[hi_i].h - 0.3 * a:
                done.add(1)
                yield i, -1
        if -1 not in done and b[lo_i].m < 660 and b[i].l > b[lo_i].l:
            rip = max(x.h for x in b[lo_i:i + 1]) - b[lo_i].l
            if rip >= 1.5 * a and b[i].l <= b[lo_i].l + 0.15 * a and b[i].c >= b[lo_i].l + 0.3 * a:
                done.add(-1)
                yield i, 1


SETUPS = [
    dict(id='morning_extreme_retest', name="Morning high/low retest that fails", family='pattern',
         detect=morning_extreme_retest,
         rules="The day's high (or low) is set before 11:00 and price moves at least 1.5 ATR away. Between 12:00 "
               "and 15:00 a bar comes within 0.15 ATR of that extreme without breaking it and closes at least "
               "0.3 ATR back from it. Tested with and against the rejection; one signal per side per session."),
]
