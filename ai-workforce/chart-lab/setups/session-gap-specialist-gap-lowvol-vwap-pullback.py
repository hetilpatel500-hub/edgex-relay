"""Heavy-volume gap, then a quiet first pullback to VWAP that holds.
Added 2026-10-05 by session-gap-specialist via WebSearch (the "low volume pullback" write-up:
a stock gaps on high volume, pulls back to VWAP on low volume, then continues). Parameters fixed
BEFORE any P&L was seen: gap of at least 0.5% versus yesterday's close, average relative volume
of the first six 5-minute bars at least 1.5, first bar from 09:55 on whose range touches VWAP
while closing back on the gap's side with volume below the average of the first six bars, all
earlier closes since 09:55 on the gap's side, before 14:00, one per session. The lab tests it
with and against.
"""


def gap_lowvol_vwap_pullback(s):
    p = s.prior
    b = s.bars
    if p is None or len(b) < 8:
        return
    gap = s.open / p.close - 1
    if abs(gap) < 0.005:
        return
    rv = [x for x in s.rvol[:6] if x is not None]
    if len(rv) < 6 or sum(rv) / 6 < 1.5:
        return
    d = 1 if gap > 0 else -1
    avgv = sum(x.v for x in b[:6]) / 6
    for i in range(6, len(b)):
        if b[i].m >= 840:
            return
        touch = b[i].l <= s.vwap[i] if d == 1 else b[i].h >= s.vwap[i]
        side = d * (b[i].c - s.vwap[i]) > 0
        if touch and side and b[i].v < avgv:
            yield i, d
            return
        if not side:
            return


SETUPS = [
    dict(id='gap_lowvol_vwap_pullback', name='Heavy-volume gap, quiet first pullback to VWAP holds', family='session',
         detect=gap_lowvol_vwap_pullback,
         rules="Open gaps at least 0.5% from yesterday's close on heavy opening volume (first six bars average "
               "relative volume 1.5 or more). The first bar from 9:55 that dips to VWAP on volume below the "
               "opening bars' average and closes back on the gap's side leans with the gap; if a close ever "
               "lands on the wrong side of VWAP first, no signal. Before 14:00, once per session."),
]
