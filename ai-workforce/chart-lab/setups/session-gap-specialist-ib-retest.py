"""Initial balance breakout, then retest of the broken IB edge.
Added 2026-09-30 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch for a documented, untested variant
(Dalton-style initial balance extension). ib_break tests the plain break and
orb_retest the 15-minute range; this waits for price to come back and hold the
60-minute IB edge before leaning with the break.
"""


def ib_retest(s):
    """A 5-minute close beyond the 9:30-10:30 initial balance (after 10:30, before 14:00)
    marks the break. The first later bar (within 12 bars) whose range touches the broken
    edge and that closes back outside it confirms the retest and leans with the break.
    A close back through the edge cancels it. One per session."""
    b = s.bars
    state = None
    for i in range(12, len(b)):
        if b[i].m >= 870:
            return
        if state is None:
            if b[i].m < 840:
                if b[i].c > s.ib_hi:
                    state = (1, s.ib_hi, i)
                elif b[i].c < s.ib_lo:
                    state = (-1, s.ib_lo, i)
            continue
        d, edge, k = state
        if i - k > 12:
            return
        if i == k:
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
    dict(id='ib_retest', name='Initial balance breakout retest', family='initial balance', detect=ib_retest,
         rules="A 5-minute close beyond the 9:30-10:30 initial balance (before 14:00) marks the break. The first "
               "bar within the next hour that trades back to the broken edge and closes outside it again "
               "confirms the retest; lean with the break. A close back inside the balance cancels it."),
]
