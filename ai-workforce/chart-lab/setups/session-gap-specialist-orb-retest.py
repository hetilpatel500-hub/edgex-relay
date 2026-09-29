"""Opening range breakout, then retest of the broken edge.
Added 2026-09-29 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch (LuxAlgo, tradersmastermind ORB
guides) for a documented, untested variant. orb15 already tests the plain
breakout; this waits for the retest that the guides say filters false breaks.
"""


def orb_retest(s):
    """A 5-minute close beyond the 9:30-9:45 range (before 10:30) marks the
    breakout. The first later bar (within 12 bars) whose range touches the
    broken edge and that closes back outside it, on the breakout side, confirms
    the retest and leans with the breakout. A close back through the far side
    of the edge (into the range by more than nothing) cancels it. One per side."""
    b = s.bars
    state = None   # (direction, edge, break bar)
    for i in range(3, len(b)):
        if b[i].m >= 690:
            return
        if state is None:
            if b[i].m < 630:
                if b[i].c > s.or_hi:
                    state = (1, s.or_hi, i)
                elif b[i].c < s.or_lo:
                    state = (-1, s.or_lo, i)
            continue
        d, edge, k = state
        if i == k or i - k > 12:
            if i - k > 12:
                return
            continue
        if d == 1:
            if b[i].c < edge:
                return
            if b[i].l <= edge and b[i].c > edge:
                yield i, 1
                return
        else:
            if b[i].c > edge:
                return
            if b[i].h >= edge and b[i].c < edge:
                yield i, -1
                return


SETUPS = [
    dict(id='orb_retest', name='Opening range breakout retest', family='opening range', detect=orb_retest,
         rules="A 5-minute close beyond the 9:30-9:45 range before 10:30 marks the break. The first bar within "
               "the next hour that trades back to the broken edge and closes outside it again confirms the "
               "retest; lean with the breakout. A close back inside the range cancels it."),
]
