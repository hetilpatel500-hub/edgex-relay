"""Spring / upthrust at the IB extreme, on effort-vs-result.
Added 2026-09-27 by wyckoff-phase-analyst: next open line of the research
queue in ai-workforce/chart-lab/README.md ("Spring / upthrust at the IB
extreme"). `ib_sweep` in intraday.py already tests any wick-and-close-back
at the IB extreme (rejected); this setup is the Wyckoff-specific version of
that same event and only fires when the probe shows effort-vs-result
divergence: the probing bar trades on below-average volume for its slot (no
new supply/demand came in to extend the move) yet closes back with a
strong body in the opposite direction (the market absorbed it hard). A
plain sweep with average or heavy volume on the probe bar is not a spring
or an upthrust by this test and does not fire.
"""


def spring_upthrust(s):
    b = s.bars
    hi_done = lo_done = False
    for i in range(12, len(b)):
        if b[i].m >= 900:
            return
        rng = b[i].h - b[i].l
        if rng <= 0:
            continue
        r = s.rvol[i]
        if r is None or r >= 1.0:
            continue
        if not lo_done and b[i].l < s.ib_lo and b[i].c > s.ib_lo and b[i].c >= b[i].l + 0.5 * rng:
            lo_done = True; yield i, 1
        if not hi_done and b[i].h > s.ib_hi and b[i].c < s.ib_hi and b[i].c <= b[i].l + 0.5 * rng:
            hi_done = True; yield i, -1


SETUPS = [
    dict(id='spring_upthrust', name='Wyckoff spring / upthrust at the IB extreme', family='wyckoff',
         detect=spring_upthrust,
         rules="After the initial balance, a bar wicks beyond the IB low (high) and closes back inside on "
               "below-average volume for that time slot (low effort) while closing in the outer half of its "
               "own range against the wick (strong result): the effort-vs-result divergence marks a spring "
               "(lean long) or upthrust (lean short), before 15:00. One per side per session."),
]
