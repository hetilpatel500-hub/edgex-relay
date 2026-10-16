"""IB breakout only when the first hour carried an outsized share of yesterday's volume.
Added 2026-10-06 by volume-vwap-analyst via WebSearch (volume-profile / initial-balance write-ups: an IB built
on heavy participation signals conviction, a light one is easily faded). Distinct from ib_break (no volume
filter), orb5_volume_spike (single bar) and heavy_volume_morning_trend (rvol vs 20-day slot average).
Parameters fixed BEFORE any P&L was seen: IB volume (bars 0-11) at least 25% of the previous session's total
volume; first 5-minute close beyond the IB between 10:30 and 14:00 ET; one signal per session.
"""


def ib_volume_share_break(s):
    p = s.prior
    if p is None or len(s.bars) < 14:
        return
    pv = sum(x.v for x in p.bars)
    if not pv or sum(x.v for x in s.bars[:12]) < 0.25 * pv:
        return
    b = s.bars
    for i in range(12, len(b)):
        if b[i].m >= 840:
            return
        if b[i].c > s.ib_hi:
            yield i, 1; return
        if b[i].c < s.ib_lo:
            yield i, -1; return


SETUPS = [
    dict(id='ib_volume_share_break', name='IB breakout on heavy first-hour volume share', family='volume profile',
         detect=ib_volume_share_break,
         rules="If the first hour's volume was at least 25% of yesterday's full-day volume, the first 5-minute "
               "close beyond the initial balance (first hour) before 14:00 leans in the break direction. "
               "Tested with and against; one signal per session."),
]
