"""Five-minute opening range breakout confirmed by a volume spike.
Added 2026-09-30 by session-gap-specialist: the research queue's non-tape lines
are all coded, so this run used WebSearch (a public 5-Min ORB with Volume Spike
script, plus ORB/gap-and-go guides) for a documented, untested variant. orb15
tests the 15-minute range with no volume test; this uses the first 5-minute
bar's range and requires the breakout bar to trade heavy.
"""


def orb5_volume_spike(s):
    """The first 5-minute bar (9:30-9:35) sets the range. The first bar that
    closes beyond its high (or low) before 9:55, on relative volume of at least
    1.5x the average for that time slot, leans with the breakout. One per day.
    A close beyond the range without the volume test is skipped, not waited on."""
    b = s.bars
    hi, lo = b[0].h, b[0].l
    for i in range(1, min(5, len(b))):
        if b[i].c > hi or b[i].c < lo:
            r = s.rvol[i]
            if r is not None and r >= 1.5:
                yield i, (1 if b[i].c > hi else -1)
            return


SETUPS = [
    dict(id='orb5_volume_spike', name='5-minute opening range break on a volume spike', family='session',
         detect=orb5_volume_spike,
         rules="Wait for the first bar after 9:35 (before 9:55) that closes beyond the 9:30-9:35 high or low. "
               "If that bar's volume is at least 1.5x the usual for its time slot, lean with the breakout; "
               "otherwise skip the day."),
]
