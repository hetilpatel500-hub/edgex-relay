"""VWAP band walk: price riding outside the +1 SD (or -1 SD) VWAP band.
Added 2026-10-04 by volume-vwap-analyst: WebSearch-free idea from the VWAP-bands family. vwap_1sd_hold
tests the first PULLBACK to the band; this tests the walk itself (persistence), with no pullback.
Parameters fixed BEFORE any P&L was seen: four consecutive 5-minute closes beyond the 1 SD band on the
same side, VWAP itself sloping the same way over the last 6 bars, 10:00 to 14:30, the signal is the
close of the 4th bar, one signal per side per session. The lab tests it with and against.
"""


def vwap_band_walk(s):
    b = s.bars
    done = set()
    for i in range(9, len(b) - 1):
        m = b[i].m
        if m < 600:
            continue
        if m >= 870:
            return
        for d in (1, -1):
            if d in done:
                continue
            if not all(s.vsd[k] and d * (b[k].c - (s.vwap[k] + d * s.vsd[k])) > 0 for k in range(i - 3, i + 1)):
                continue
            if d * (s.vwap[i] - s.vwap[i - 6]) <= 0:
                continue
            done.add(d)
            yield i, d


SETUPS = [
    dict(id='vwap_band_walk', name='VWAP 1 SD band walk (four closes outside)', family='volume',
         detect=vwap_band_walk,
         rules="Four 5-minute closes in a row beyond the +1 SD VWAP band (or below -1 SD), with VWAP sloping "
               "the same way over the last half hour, lean with the walk at the fourth close, 10:00-14:30, "
               "once per side per session."),
]
