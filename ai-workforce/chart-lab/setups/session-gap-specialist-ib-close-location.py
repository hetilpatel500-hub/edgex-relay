"""Initial balance closes at its extreme (one-time-framing hour).
Added 2026-10-01 by session-gap-specialist: the research queue's non-tape lines
are coded, so this run chose a Market Profile idea not yet tested: a first
hour that finishes in the outer fifth of its own range shows one side in
control (a "one-time-framing" opening hour), and the lean is that the move
continues. Distinct from ib_break (needs a break of the IB) and
prior_close_location (reads yesterday's range).
"""


def ib_close_location(s):
    """At the close of bar 11 (10:30), if the close sits in the top 20% of the
    IB range lean long; in the bottom 20%, lean short. One signal per session."""
    b = s.bars
    if len(b) < 13:
        return
    rng = s.ib_hi - s.ib_lo
    if rng <= 0:
        return
    loc = (b[11].c - s.ib_lo) / rng
    if loc >= 0.8:
        yield 11, 1
    elif loc <= 0.2:
        yield 11, -1


SETUPS = [
    dict(id='ib_close_location', name='Initial balance closes at its extreme', family='initial balance',
         detect=ib_close_location,
         rules="If the first hour (9:30-10:30) closes in the top 20% of its own range lean long; in the bottom "
               "20% lean short. Signal at the 10:30 close, one per session."),
]
