"""Ehlers Inverse Fisher Transform of RSI, 5-minute bars.
Added 2026-10-14 by momentum-analyst (WebSearch 2026-10-14: Ehlers' template is RSI(5) minus 50, times 0.1,
smoothed by a 9-bar weighted MA, then y = (e^2x - 1)/(e^2x + 1); entries at the +/-0.5 crossings). Rules fixed
BEFORE any P&L was seen: RSI(5) Wilder on closes of the session (seeded from the session's first bars),
WMA(9) of 0.1*(RSI-50), transform; long when IFT crosses up through -0.5 from below, short when it crosses
down through +0.5, 10:00 to 14:30 ET, VWAP side agreeing with the signal direction not required (tested
with and against by the lab), at most two a session.
"""
import math


def ift_rsi(s):
    b = s.bars
    n = len(b)
    r = []
    ag = al = None
    for i in range(n):
        if i == 0:
            r.append(50.0); continue
        ch = b[i].c - b[i - 1].c
        g, l = max(ch, 0), max(-ch, 0)
        if i < 5:
            ag = (ag or 0) + g / 5; al = (al or 0) + l / 5
            r.append(50.0)
        else:
            ag = (ag * 4 + g) / 5; al = (al * 4 + l) / 5
            r.append(100.0 if al == 0 else 100 - 100 / (1 + ag / al))
    v = [0.1 * (x - 50) for x in r]
    ift = []
    for i in range(n):
        if i < 8:
            ift.append(0.0); continue
        w = sum((9 - k) * v[i - k] for k in range(9)) / 45.0
        e = math.exp(2 * w)
        ift.append((e - 1) / (e + 1))
    fired = 0
    for i in range(14, n):
        if b[i].m < 600 or b[i].m >= 870 or fired >= 2:
            continue
        if ift[i - 1] <= -0.5 < ift[i]:
            fired += 1; yield i, 1
        elif ift[i - 1] >= 0.5 > ift[i]:
            fired += 1; yield i, -1


SETUPS = [
    dict(id='ift_rsi_cross', name='Inverse Fisher RSI(5) crossing back through -0.5 / +0.5', family='momentum',
         detect=ift_rsi,
         rules="Ehlers' inverse Fisher transform of a smoothed 5-bar RSI (RSI-50, x0.1, 9-bar weighted average). "
               "Long when it crosses up through -0.5, short when it crosses down through +0.5, 10:00 to 14:30 ET, "
               "at most two a session. Tested with and against."),
]
