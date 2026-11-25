"""Ehlers Laguerre RSI re-entry from the 0.15 / 0.85 zones, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (Ehlers' Laguerre RSI as documented by FXCodeBase, MQL5 forum and
WH SelfInvest: gamma 0.55-0.85, buy when the line crosses up through 0.15, sell when it crosses down through 0.85.
The sources are platform docs and forum posts with no intraday backtest). Untested intraday adaptation.
Parameters fixed BEFORE any P&L was seen: gamma = 0.7 (middle of the quoted range), price = close, seeded at the first
bar of the session; long at the close of the first bar between 10:30 and 14:30 ET where the line crosses up through
0.15 (mirror: down through 0.85 for short). No VWAP or candle filter. One signal per session.
"""


def laguerre_rsi(s):
    b = s.bars
    g = 0.7
    l0 = l1 = l2 = l3 = None
    lr = []
    for x in b:
        p = x.c
        if l0 is None:
            l0 = l1 = l2 = l3 = p
        n0 = (1 - g) * p + g * l0
        n1 = -g * n0 + l0 + g * l1
        n2 = -g * n1 + l1 + g * l2
        n3 = -g * n2 + l2 + g * l3
        l0, l1, l2, l3 = n0, n1, n2, n3
        cu = cd = 0.0
        for a, c in ((l0, l1), (l1, l2), (l2, l3)):
            if a >= c:
                cu += a - c
            else:
                cd += c - a
        lr.append(cu / (cu + cd) if cu + cd else 0.5)
    for i in range(10, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        if lr[i - 1] <= 0.15 < lr[i]:
            yield i, 1
            return
        if lr[i - 1] >= 0.85 > lr[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='laguerre_rsi_reentry', name='Laguerre RSI re-entry from 0.15 / 0.85', family='momentum',
         detect=laguerre_rsi,
         rules="Ehlers' Laguerre RSI is a heavily smoothed RSI that runs 0 to 1. Between 10:30 and 14:30 the first "
               "cross back up through 0.15 leans long and the first cross back down through 0.85 leans short. One "
               "signal per session; tested with and against."),
]
