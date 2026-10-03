"""Opening-range (30 min) measured-move extension exhausted, fade the close back inside.
Added 2026-10-02 by session-gap-specialist: the research queue held only tape items, so this run took the
documented opening-range technique (WebSearch: forextester ORB guide, tradingsmartedge ORB setups) whose
profit target is the range height projected from the breakout, and tested what happens when price reaches
that projection and fails to hold it. The lab tested the ORB entries (orb15, orb_retest, orb_failure) but not
the measured-move target as an exhaustion level. Rules fixed BEFORE any P&L was seen.
"""


def or30_mm_fade(s):
    """OR30 = high/low of the first six 5-minute bars. After 10:00 and before 13:00, the first bar that trades
    at least one OR30 height beyond the OR30 high and closes back below that projection leans short; the mirror
    below the OR30 low leans long. OR30 height must be at least 1.5 ATR. One signal per side per session."""
    b = s.bars
    if len(b) < 20:
        return
    hi, lo = max(x.h for x in b[:6]), min(x.l for x in b[:6])
    h = hi - lo
    done = set()
    for i in range(6, len(b)):
        if b[i].m >= 780:
            break
        if not s.atr[i] or h < 1.5 * s.atr[i]:
            continue
        if -1 not in done and b[i].h >= hi + h and b[i].c < hi + h:
            done.add(-1)
            yield i, -1
        elif 1 not in done and b[i].l <= lo - h and b[i].c > lo - h:
            done.add(1)
            yield i, 1


SETUPS = [
    dict(id='or30_mm_fade', name='OR30 measured-move extension exhausted, fade', family='session',
         detect=or30_mm_fade,
         rules="Take the first 30 minutes' high and low. After 10:00 and before 13:00, a 5-minute bar that trades "
               "one full opening-range height beyond the range edge but closes back inside that projection leans "
               "the other way (the measured move was reached and rejected). The range must be at least 1.5 ATR "
               "tall. One signal per side per session."),
]
