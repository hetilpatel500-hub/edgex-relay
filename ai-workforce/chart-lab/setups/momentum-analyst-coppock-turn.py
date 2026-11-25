"""Coppock curve turn from below/above zero, 5-minute bars.
Added 2026-10-12 by momentum-analyst via WebSearch (Edwin Coppock, Barron's 1962; Coppock = weighted moving average of
the sum of two rates of change; the classic buy signal is the curve turning up while below zero). The sources describe
monthly use; this is an untested intraday adaptation. Parameters fixed BEFORE any P&L was seen: the standard 14 and 11
rates of change and a 10-bar weighted moving average, all in 5-minute bars within the session. Long at the close of the
first bar between 10:30 and 14:30 ET where Coppock is below zero and has risen for the second bar in a row after a
non-rise (turn up); mirror short (above zero, turns down). No VWAP filter. One signal per session. The curve needs 24
bars of history, so signals can only appear from about 11:30 ET.
"""


def coppock_turn(s):
    b = s.bars
    n = len(b)
    roc = [None] * n
    for i in range(14, n):
        roc[i] = 100 * (b[i].c / b[i - 14].c - 1) + 100 * (b[i].c / b[i - 11].c - 1)
    cop = [None] * n
    for i in range(23, n):
        w = roc[i - 9:i + 1]
        cop[i] = sum((k + 1) * v for k, v in enumerate(w)) / 55
    for i in range(26, n - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        a, p, q = cop[i], cop[i - 1], cop[i - 2]
        if a < 0 and a > p and p <= q:
            yield i, 1
            return
        if a > 0 and a < p and p >= q:
            yield i, -1
            return


SETUPS = [
    dict(id='coppock_turn', name='Coppock curve turn against zero', family='momentum',
         detect=coppock_turn,
         rules="Coppock is a weighted average of two rates of change (14 and 11 bars). Between 10:30 and 14:30, "
               "when it is below zero and turns up it leans long; when above zero and it turns down it leans short. "
               "Needs about two hours of session history. One signal per session; tested with and against."),
]
