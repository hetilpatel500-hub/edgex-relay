"""VWAP chop then compression break.
Added 2026-10-04 by volume-vwap-analyst: WebSearch-free idea from the VWAP family (a session that keeps
crossing VWAP is balanced; when that balance compresses, the break out of it is the signal).
Parameters fixed BEFORE any P&L was seen: price closed on the other side of VWAP at least 4 times between
9:35 and the signal bar; the last 12 bars' range is at most 0.6 x the IB range; the signal bar closes
beyond that 12-bar range (high or low of the prior 12 bars) with a close on the breakout side of VWAP;
11:30 to 14:30; one signal per session. The lab tests it with and against.
"""


def vwap_chop_compression_break(s):
    b = s.bars
    ib = s.ib_hi - s.ib_lo
    if ib <= 0:
        return
    for i in range(13, len(b) - 1):
        m = b[i].m
        if m < 690:
            continue
        if m >= 870:
            return
        crosses = sum(1 for k in range(1, i) if (b[k].c - s.vwap[k]) * (b[k - 1].c - s.vwap[k - 1]) < 0)
        if crosses < 4:
            continue
        prev = b[i - 12:i]
        hi, lo = max(x.h for x in prev), min(x.l for x in prev)
        if hi - lo > 0.6 * ib:
            continue
        if b[i].c > hi and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if b[i].c < lo and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='vwap_chop_compression_break', name='VWAP chop, then compression break', family='volume',
         detect=vwap_chop_compression_break,
         rules="After at least four VWAP crosses since the open, when the last hour's range is no more than 60% "
               "of the initial balance, a 5-minute close beyond that hour's high (above VWAP) or low (below "
               "VWAP) between 11:30 and 14:30 leans with the break, once per session."),
]
