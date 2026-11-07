"""Prior-close cross on a volume spike, on 5-minute bars.
Added 2026-09-29 by volume-vwap-analyst: the research queue is fully coded, so
this run used WebSearch (day-trading strategy guides describing "build a base
in the first hour, then cross the previous day's close on a volume spike").
Not covered by gap_fill (fade toward the close) or the IB/IVB setups.
"""


def prior_close_cross(s):
    """The first 12 bars (initial balance) stay entirely on one side of
    yesterday's close. The first later bar (before 14:00) that closes across
    yesterday's close with relative volume >= 1.5 leans in the direction of
    the cross: up through it long, down through it short. One signal a session."""
    p = s.prior
    if p is None:
        return
    b = s.bars
    if len(b) < 14:
        return
    pc = p.close
    below = all(x.h < pc for x in b[:12])
    above = all(x.l > pc for x in b[:12])
    if not (below or above):
        return
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        rv = s.rvol[i]
        if rv is None or rv < 1.5:
            continue
        if below and b[i].c > pc:
            yield i, 1
            return
        if above and b[i].c < pc:
            yield i, -1
            return


SETUPS = [
    dict(id='prior_close_cross', name='Prior-close cross on a volume spike', family='volume',
         detect=prior_close_cross,
         rules="The first hour (initial balance) trades entirely below (or above) yesterday's close. The first "
               "5-minute bar before 14:00 ET that closes through yesterday's close on 1.5x normal volume leans "
               "with the cross: long through it from below, short through it from above."),
]
