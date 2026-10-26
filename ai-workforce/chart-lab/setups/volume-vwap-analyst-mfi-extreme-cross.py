"""Money Flow Index (14) leaving an extreme while price is stretched from VWAP.
Added 2026-10-02 by volume-vwap-analyst: the research queue's open lines were already covered, so this run took
the Money Flow Index (volume-weighted RSI, Quong and Soudack), which the lab had not tested. The existing RSI and
volume-divergence setups ignore the volume weighting of money flow itself.
Rules fixed BEFORE any P&L was seen: MFI over 14 bars inside the session only, thresholds 20/80, price beyond
VWAP by 1 session stdev on the stretched side, 10:45-14:30, one signal per side per session.
"""


def mfi_extreme_cross(s):
    b = s.bars
    tp = [(x.h + x.l + x.c) / 3 for x in b]
    up_done = dn_done = False
    prev = None
    for i in range(14, len(b)):
        if b[i].m >= 870:
            return
        pos = neg = 0.0
        for k in range(i - 13, i + 1):
            f = tp[k] * b[k].v
            if tp[k] > tp[k - 1]:
                pos += f
            elif tp[k] < tp[k - 1]:
                neg += f
        mfi = 100.0 if neg == 0 and pos > 0 else (50.0 if neg == 0 else 100 - 100 / (1 + pos / neg))
        if prev is not None and b[i].m >= 645:
            sd = s.vsd[i]
            if not up_done and prev < 20 <= mfi and sd and b[i].c <= s.vwap[i] - sd:
                up_done = True; yield i, 1
            elif not dn_done and prev > 80 >= mfi and sd and b[i].c >= s.vwap[i] + sd:
                dn_done = True; yield i, -1
        prev = mfi


SETUPS = [
    dict(id='mfi_extreme_cross', name='Money Flow Index leaving an extreme, stretched from VWAP', family='volume',
         detect=mfi_extreme_cross,
         rules="The 14-bar Money Flow Index (typical price x volume, up-bars versus down-bars) climbs back above 20 "
               "while price closes at least 1 volume-weighted standard deviation below VWAP (leans long), or falls "
               "back below 80 while price closes at least 1 above VWAP (leans short), between 10:45 and 14:30. "
               "One per side per session. Tested with and against, like every setup."),
]
