"""RSI(14) of the session VWAP line, re-entry from 30/70, 5-minute session bars.
Added 2026-10-14 by momentum-analyst via WebSearch (public TradingView "RSI of VWAP" scripts, no published results):
RSI is computed on the running session VWAP instead of price, so it measures how fast the volume-weighted average is
drifting. The lab has VWAP side/slope setups and RSI on price, not RSI on VWAP. Parameters fixed BEFORE any P&L was
seen: Wilder RSI period 14 on the VWAP series, restarted each session (first value at bar 14), levels 30 / 70.
Long at the close of the first bar between 10:15 and 14:30 ET where RSI(VWAP) crosses back up through 30 (prior bar
<= 30, this bar > 30); short where it crosses back down through 70 (prior >= 70, this < 70). One per side per session.
"""


def rsi_of_vwap_reentry(s):
    v = s.vwap
    b = s.bars
    n = len(b)
    if n < 16:
        return
    gains = [max(v[i] - v[i - 1], 0) for i in range(1, n)]
    losses = [max(v[i - 1] - v[i], 0) for i in range(1, n)]
    rsi = [None] * n
    ag = sum(gains[:14]) / 14
    al = sum(losses[:14]) / 14
    rsi[14] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    for i in range(15, n):
        ag = (ag * 13 + gains[i - 1]) / 14
        al = (al * 13 + losses[i - 1]) / 14
        rsi[i] = 100.0 if al == 0 else 100 - 100 / (1 + ag / al)
    done = {1: False, -1: False}
    for i in range(15, n):
        if b[i].m < 615 or b[i].m + 5 > 870:
            continue
        if not done[1] and rsi[i - 1] <= 30 < rsi[i]:
            done[1] = True; yield i, 1
        elif not done[-1] and rsi[i - 1] >= 70 > rsi[i]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='rsi_of_vwap_reentry', name='RSI(14) of VWAP re-entry from 30/70', family='momentum',
         detect=rsi_of_vwap_reentry,
         rules="Wilder RSI(14) computed on the running session VWAP (not price). When it crosses back up through 30 "
               "the setup leans long; when it crosses back down through 70 it leans short, between 10:15 and 14:30. "
               "One signal per side per session; tested with and against."),
]
