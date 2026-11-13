"""Opening range failure: a breakout of the first 15 minutes that is rejected.
Added 2026-09-29 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch (fortraders.com false-breakout guide,
daystoexpiry.com 0DTE reversal playbook, buildalpha.com ORB guide) for a
documented, untested idea. orb_retest cancels when price closes back inside the
range; this trades exactly that event. Distinct from ib_break_fail (60-minute
initial balance, 6+ bar window) and turtle_soup (prior-day extremes).
"""


def orb_failure(s):
    """A 5-minute close beyond the 9:30-9:45 range before 10:30 marks the break.
    If within the next 4 bars a bar closes back inside the range, that close is
    the signal, leaning back through the range (long after a failed break down,
    short after a failed break up). One signal per session."""
    b = s.bars
    state = None   # (break direction, break bar)
    for i in range(3, len(b)):
        if b[i].m >= 690:
            return
        if state is None:
            if b[i].m < 630:
                if b[i].c > s.or_hi:
                    state = (1, i)
                elif b[i].c < s.or_lo:
                    state = (-1, i)
            continue
        d, k = state
        if i - k > 4:
            return
        if d == 1 and b[i].c <= s.or_hi:
            yield i, -1
            return
        if d == -1 and b[i].c >= s.or_lo:
            yield i, 1
            return


SETUPS = [
    dict(id='orb_failure', name='Opening range failed breakout', family='opening range', detect=orb_failure,
         rules="A 5-minute close beyond the 9:30-9:45 range before 10:30 marks the break. If a close back inside "
               "the range follows within the next 4 bars, the failed break leans the other way (short after a failed "
               "break up, long after a failed break down). One trade per session."),
]
