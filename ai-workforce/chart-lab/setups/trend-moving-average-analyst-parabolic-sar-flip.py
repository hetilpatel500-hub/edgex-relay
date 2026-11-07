"""Parabolic SAR flip on 5-minute bars.
Added 2026-10-02 by trend-moving-average-analyst: the research queue held only tape items, so this run took
the documented Parabolic SAR flip entry (WebSearch: cmcmarkets.com/en-gb/technical-analysis/parabolic-sar,
insights.exness.com parabolic-sar-strategy: SAR dot jumps below the candle = bullish turn, above = bearish).
Wilder's standard parameters (start 0.02, step 0.02, max 0.20) fixed BEFORE any P&L was seen. No SAR setup existed in the lab.
"""


def psar_flip(s):
    """SAR is run from the session open (first bar seeds the trend from bar 2's direction). When price crosses
    the SAR, the trend flips; that bar's close is the signal in the new direction. Signals from 10:00 to 14:55,
    at most one per direction per session, so a choppy day cannot fire repeatedly."""
    b = s.bars
    if len(b) < 3:
        return
    up = b[1].c >= b[0].c
    sar = b[0].l if up else b[0].h
    ep = b[1].h if up else b[1].l
    af = 0.02
    done = set()
    for i in range(1, len(b)):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, b[i - 1].l, b[i - 2].l if i >= 2 else b[i - 1].l)
            if b[i].l < sar:
                up, sar, ep, af = False, ep, b[i].l, 0.02
                d = -1
            else:
                d = 0
                if b[i].h > ep:
                    ep, af = b[i].h, min(af + 0.02, 0.20)
        else:
            sar = max(sar, b[i - 1].h, b[i - 2].h if i >= 2 else b[i - 1].h)
            if b[i].h > sar:
                up, sar, ep, af = True, ep, b[i].h, 0.02
                d = 1
            else:
                d = 0
                if b[i].l < ep:
                    ep, af = b[i].l, min(af + 0.02, 0.20)
        if d and b[i].m >= 600 and b[i].m < 895 and d not in done:
            done.add(d)
            yield i, d


SETUPS = [
    dict(id='psar_flip', name='Parabolic SAR flip (5-minute)', family='trend',
         detect=psar_flip,
         rules="Wilder's Parabolic SAR (start 0.02, step 0.02, max 0.20) runs on the session's 5-minute bars. "
               "When price trades through the SAR the trend flips and that bar's close leans the new way: "
               "long when it flips up, short when it flips down. From 10:00 to 14:55, at most one signal per "
               "direction per session. Parameters are Wilder's defaults, fixed before testing."),
]
