"""Daily Internal Bar Strength (IBS) extreme.
Added 2026-09-29 by momentum-analyst: the research queue's non-tape lines are
all coded, so this run used WebSearch (IBS = (close-low)/(high-low); below 0.2
oversold, above 0.8 overbought, per alvarezquanttrading.com and
quantifiedstrategies.com). Thresholds 0.2/0.8 are the documented ones and were
fixed before testing.
"""


def ibs_extreme(ser):
    for j in range(1, len(ser.c)):
        rng = ser.h[j] - ser.l[j]
        if rng <= 0:
            continue
        ibs = (ser.c[j] - ser.l[j]) / rng
        if ibs < 0.2:
            yield j, 1
        elif ibs > 0.8:
            yield j, -1


SETUPS = [
    dict(id='d_ibs_extreme', tf='D', name='Daily IBS extreme', family='mean reversion (daily)',
         detect=ibs_extreme,
         rules="A daily close in the bottom 20% of its own high-low range (IBS < 0.2) leans long into the next "
               "session; a close in the top 20% (IBS > 0.8) leans short."),
]
