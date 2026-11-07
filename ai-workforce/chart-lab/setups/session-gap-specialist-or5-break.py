"""Opening 5-minute bar breakout (OR5).
Added 2026-10-02 by session-gap-specialist: the research queue's open lines were already covered by earlier
runs, so this run took the documented opening-bar breakout (the 5-minute opening range is the shortest of the
standard 5/15/30-minute opening ranges; the lab only had the 15-minute orb15 and the 30-minute variants).
Rules fixed BEFORE any P&L was seen: first 5-minute bar, close beyond it, before 10:30, first signal only.
"""


def or5_break(s):
    """The first 5-minute bar's high and low set the range. The first later bar that closes beyond one side
    (bars 2 to 12, before 10:30) leans that way; one signal per session."""
    b = s.bars
    hi, lo = b[0].h, b[0].l
    for i in range(1, len(b)):
        if b[i].m >= 630:
            return
        if b[i].c > hi:
            yield i, 1
            return
        if b[i].c < lo:
            yield i, -1
            return


SETUPS = [
    dict(id='or5_break', name='Opening 5-minute bar breakout', family='opening range',
         detect=or5_break,
         rules="The first 5-minute bar of the session (09:30-09:35) sets the range. The first later bar that "
               "closes above its high leans long, or below its low leans short, before 10:30; one signal per "
               "session. Tested with and against, like every setup."),
]
