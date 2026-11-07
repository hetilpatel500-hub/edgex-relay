"""Hull Moving Average (21) slope turn with VWAP agreement.
Added 2026-10-05 by trend-moving-average-analyst via WebSearch of published Hull MA
intraday usage (Alan Hull's HMA: WMA(2*WMA(n/2) - WMA(n), sqrt(n)); signal = slope turn).
Rules fixed BEFORE any P&L was seen: n = 21 on 5-minute closes within the session,
turn = HMA slope changes sign on a bar that closes on the same side of session VWAP,
09:30-14:30 entries, at most 2 signals per session.
"""
import math


def _wma(x, n):
    w = list(range(1, n + 1))
    d = sum(w)
    return [None if i < n - 1 else sum(x[i - n + 1 + k] * w[k] for k in range(n)) / d for i in range(len(x))]


def hull_turn(s):
    b = s.bars
    n = 21
    c = [x.c for x in b]
    h, f = n // 2, int(round(math.sqrt(n)))
    w1, w2 = _wma(c, h), _wma(c, n)
    raw = [None if w1[i] is None or w2[i] is None else 2 * w1[i] - w2[i] for i in range(len(c))]
    start = n - 1
    hull = [None] * len(c)
    seg = raw[start:]
    if len(seg) < f + 2:
        return
    sm = _wma(seg, f)
    for i, v in enumerate(sm):
        hull[start + i] = v
    fired = 0
    for i in range(start + f + 1, len(b)):
        if b[i].m >= 870 or fired >= 2:
            return
        a, p, q = hull[i], hull[i - 1], hull[i - 2]
        if a is None or p is None or q is None:
            continue
        if p < q and a > p and b[i].c > s.vwap[i]:
            fired += 1
            yield i, 1
        elif p > q and a < p and b[i].c < s.vwap[i]:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='hull_ma_turn_vwap', name='Hull MA(21) turn with VWAP agreement', family='trend', detect=hull_turn,
         rules="Hull moving average (21) of 5-minute closes turns up (slope flips from falling to rising) on a bar "
               "closing above session VWAP: lean long; turns down on a bar closing below VWAP: lean short. "
               "Starts after the first 21 bars have formed, until 14:30, at most 2 signals per session. "
               "Parameters fixed from the published Hull definition before testing. Tested with and against."),
]
