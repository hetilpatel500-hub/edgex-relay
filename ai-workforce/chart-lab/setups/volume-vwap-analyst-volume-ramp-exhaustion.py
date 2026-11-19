"""Volume-ramp exhaustion: three same-direction bars on rising volume that run away from VWAP.
Added 2026-10-19 by volume-vwap-analyst via the lab queue (WebSearch-free idea from volume-spread analysis:
a push that needs ever more volume per bar is being absorbed; distinct from climax_reversal, which reads one
bar, and from weis_wave_pullback, which reads a pullback after a thrust). Parameters fixed BEFORE any P&L was seen.
"""


def volume_ramp_exhaustion(s):
    """Three consecutive up (down) bars, each closing above (below) its open and above (below) the prior close,
    each with volume strictly above the bar before, the third closing in the top (bottom) 25% of its range,
    and the third's close more than 1.5 ATR(5-min) beyond session VWAP in that direction. Between 10:00 and
    14:30 ET. Direction is the push (the lab tests with and against); at most one signal per side per session."""
    b = s.bars
    seen = {1: False, -1: False}
    for i in range(3, len(b)):
        if b[i].m < 600 or b[i].m > 870:
            continue
        for d in (1, -1):
            if seen[d]:
                continue
            ok = True
            for j in (i - 2, i - 1, i):
                x = b[j]
                if (x.c - x.o) * d <= 0 or (x.c - b[j - 1].c) * d <= 0 or x.v <= b[j - 1].v:
                    ok = False
                    break
            if not ok:
                continue
            x = b[i]
            rng = x.h - x.l
            if rng <= 0:
                continue
            loc = (x.c - x.l) / rng if d == 1 else (x.h - x.c) / rng
            if loc < 0.75:
                continue
            if (x.c - s.vwap[i]) * d > 1.5 * s.atr[i]:
                seen[d] = True
                yield i, d


SETUPS = [
    dict(id='volume_ramp_exhaustion', name='Volume-ramp exhaustion beyond VWAP', family='volume',
         detect=volume_ramp_exhaustion,
         rules="Three bars in a row close in the same direction (each above its open and above the prior close) "
               "with volume rising on every bar, the third closing in the top (bottom) quarter of its range and "
               "more than 1.5 ATR beyond session VWAP, between 10:00 and 14:30 ET. One signal per side per "
               "session; signal is in the direction of the push, tested with and against."),
]
