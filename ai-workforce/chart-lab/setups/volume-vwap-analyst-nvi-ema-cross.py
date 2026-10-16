"""Negative Volume Index (Fosback) cross of its EMA, confirmed by VWAP side, on 5-minute session bars.
Added 2026-10-11 by volume-vwap-analyst via WebSearch (luxalgo.com Negative Volume Index, supermoney.com NVI
encyclopedia; both daily-bar sources, so this is an untested intraday adaptation and parameters were fixed before
any P&L was seen). NVI starts at 1000 each session and changes by the bar's % price change only on bars whose
volume is below the previous bar's volume (the 'smart money trades quietly' premise); signal = EMA20 of NVI.
Signal at the close of the first bar between 11:00 and 14:30 ET where NVI crosses its EMA and the close is on the
same side of session VWAP; one per session.
"""


def nvi_ema_cross(s):
    b = s.bars
    nvi = 1000.0
    ema = None
    prev_diff = None
    for i, x in enumerate(b):
        if i > 0:
            p = b[i - 1]
            if x.v < p.v and p.c:
                nvi *= x.c / p.c
        ema = nvi if ema is None else ema + (2 / 21) * (nvi - ema)
        diff = nvi - ema
        pd, prev_diff = prev_diff, diff
        if pd is None or i < 21 or x.m < 660 or x.m > 870 or i + 1 >= len(b):
            continue
        d = 1 if (pd <= 0 < diff) else (-1 if (pd >= 0 > diff) else 0)
        if d and (x.c - s.vwap[i]) * d > 0:
            yield i, d
            return


SETUPS = [
    dict(id='nvi_ema_cross', name='Negative Volume Index EMA cross with VWAP', family='volume',
         detect=nvi_ema_cross,
         rules="A Negative Volume Index built from the session's 5-minute bars (it moves with price only on bars "
               "whose volume is lower than the bar before) crosses above or below its 20-bar average between "
               "11:00 and 14:30 while price closes on the same side of VWAP: up-cross above VWAP leans long, "
               "down-cross below VWAP leans short. One signal per session; tested with and against."),
]
