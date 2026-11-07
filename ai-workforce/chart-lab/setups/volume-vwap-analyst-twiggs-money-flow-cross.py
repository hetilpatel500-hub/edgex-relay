"""Twiggs Money Flow +/-0.05 threshold cross with VWAP agreement.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (luxalgo.com Twiggs Money Flow page: +/-0.05 thresholds to
filter zero-line whipsaws; motivewave.com Twiggs Money Flow study; Colin Twiggs' definition). Distinct from
cmf_zero_cross_vwap: Twiggs uses true range high/low including the prior close (so gaps count) and a smoothed
ratio. Rules fixed BEFORE any P&L was seen: TRH = max(high, prev close), TRL = min(low, prev close),
AD = (2C - TRL - TRH)/(TRH - TRL) x volume; TMF = EMA(AD)/EMA(volume) with a 12-bar span (one hour; Twiggs'
21 days adapted to a session, not tuned). Session starts at the first bar. Signal when TMF crosses above +0.05
(below -0.05) while the bar closes above (below) VWAP; after bar 12, before 15:00 ET, at most two a session.
"""


def twiggs_money_flow_cross(s):
    b = s.bars
    k = 2 / 13
    ead = ev = None
    prev = None
    fired = 0
    for i, x in enumerate(b):
        pc = b[i - 1].c if i > 0 else x.o
        trh, trl = max(x.h, pc), min(x.l, pc)
        r = trh - trl
        ad = (2 * x.c - trl - trh) / r * x.v if r > 0 else 0.0
        ead = ad if ead is None else ead + (ad - ead) * k
        ev = x.v if ev is None else ev + (x.v - ev) * k
        tmf = ead / ev if ev else 0.0
        if i >= 12 and prev is not None and x.m < 900 and fired < 2 and i + 1 < len(b):
            if prev <= 0.05 < tmf and x.c > s.vwap[i]:
                fired += 1
                yield i, 1
            elif prev >= -0.05 > tmf and x.c < s.vwap[i]:
                fired += 1
                yield i, -1
        prev = tmf


SETUPS = [
    dict(id='twiggs_money_flow_cross', name='Twiggs Money Flow +/-0.05 cross + VWAP', family='volume',
         detect=twiggs_money_flow_cross,
         rules="Twiggs Money Flow (smoothed ratio of gap-aware accumulation/distribution volume to volume, 12-bar "
               "span) crossing above +0.05 while price closes above VWAP leans long; crossing below -0.05 while price "
               "closes below VWAP leans short. After the first 12 bars, before 15:00 ET, at most two a session; "
               "tested with and against."),
]
