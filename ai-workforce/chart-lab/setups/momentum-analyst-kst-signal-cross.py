"""Know Sure Thing (KST) signal-line cross with VWAP agreement on 5-minute bars.
Added 2026-10-11 by momentum-analyst via WebSearch (Martin Pring's KST, 1992: weighted sum of four smoothed rates of
change, with a signal line; a cross of KST over its signal line is the primary signal. Sources note it works better on
daily/weekly charts and gives more false signals intraday; no intraday evidence is given). Untested adaptation.
Parameters fixed BEFORE any P&L was seen: the classic periods are too long for a 78-bar session, so they were scaled
down by 2: ROC 5/8/10/15, smoothed by SMA 5/5/5/8, weights 1/2/3/4, signal = SMA(5) of KST. Computed inside the
session only. Cross at a bar close between 11:30 and 14:30 ET, taken only when that close is on the same side of session
VWAP as the cross direction. One signal per session.
"""


def kst_cross(s):
    b = s.bars
    n = len(b)
    c = [x.c for x in b]
    spec = [(5, 5, 1), (8, 5, 2), (10, 5, 3), (15, 8, 4)]
    kst = [None] * n
    for i in range(n):
        tot, ok = 0.0, True
        for roc_n, sm_n, w in spec:
            lo = i - sm_n + 1
            if lo - roc_n < 0:
                ok = False
                break
            tot += w * sum((c[j] / c[j - roc_n] - 1) * 100 for j in range(lo, i + 1)) / sm_n
        kst[i] = tot if ok else None
    sig = [None] * n
    for i in range(n):
        if i >= 4 and all(kst[j] is not None for j in range(i - 4, i + 1)):
            sig[i] = sum(kst[i - 4:i + 1]) / 5
    for i in range(1, n - 1):
        if sig[i] is None or sig[i - 1] is None:
            continue
        m = b[i].m
        if m < 690 or m > 870:
            continue
        up = kst[i] > sig[i] and kst[i - 1] <= sig[i - 1]
        dn = kst[i] < sig[i] and kst[i - 1] >= sig[i - 1]
        if up and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if dn and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='kst_signal_cross', name='Know Sure Thing signal cross with VWAP', family='momentum',
         detect=kst_cross,
         rules="The Know Sure Thing adds up four smoothed rates of change (5, 8, 10 and 15 bars, longer ones "
               "weighted more) into one momentum line and compares it with its own 5-bar average. Between 11:30 "
               "and 14:30, the first time the line crosses above its average while price is above VWAP leans "
               "long; the first cross below while price is below VWAP leans short. One signal per session; "
               "tested with and against."),
]
