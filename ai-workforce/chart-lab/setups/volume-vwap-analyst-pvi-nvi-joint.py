"""Positive and Negative Volume Index agreeing (both above / both below their EMA20), with VWAP side, on 5-minute bars.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (luxalgo.com Positive Volume Index and Negative Volume Index
library pages: 'both above their averages is the most bullish classic configuration, both below the most bearish').
The sources are daily-bar write-ups, so this intraday adaptation was fixed BEFORE any P&L was seen. Each index starts
at 1000 per session; PVI moves by the bar's % price change only on bars whose volume exceeds the previous bar's,
NVI only on bars whose volume is below it; each is compared with its own EMA20. Signal at the close of the first bar
between 11:00 and 14:30 ET where the joint state flips into 'both above' (long) or 'both below' (short) and the close
is on the same side of session VWAP; one per session.
"""


def pvi_nvi_joint(s):
    b = s.bars
    pvi = nvi = 1000.0
    ep = en = None
    prev = 0
    for i, x in enumerate(b):
        if i > 0:
            p = b[i - 1]
            if p.c:
                r = x.c / p.c
                if x.v > p.v:
                    pvi *= r
                elif x.v < p.v:
                    nvi *= r
        ep = pvi if ep is None else ep + (2 / 21) * (pvi - ep)
        en = nvi if en is None else en + (2 / 21) * (nvi - en)
        st = 1 if (pvi > ep and nvi > en) else (-1 if (pvi < ep and nvi < en) else 0)
        was, prev = prev, st
        if i < 21 or x.m < 660 or x.m > 870 or i + 1 >= len(b):
            continue
        if st and st != was and (x.c - s.vwap[i]) * st > 0:
            yield i, st
            return


SETUPS = [
    dict(id='pvi_nvi_joint', name='Positive + Negative Volume Index agreement with VWAP', family='volume',
         detect=pvi_nvi_joint,
         rules="Two volume-split price indexes are built from the session's 5-minute bars: PVI moves with price only on "
               "bars with more volume than the bar before (the crowd), NVI only on bars with less (the quiet money). "
               "When both move above their own 20-bar averages between 11:00 and 14:30 while price closes above VWAP, "
               "it leans long; both below with price under VWAP leans short. One signal per session; tested with and "
               "against."),
]
