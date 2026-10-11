"""Elder Force Index zero-line cross confirmed by VWAP side.
Added 2026-10-10 by volume-vwap-analyst via WebSearch (queue was fully coded). Alexander Elder's Force Index
(close change x volume) smoothed with a 13-period EMA is a documented volume-momentum read; the lab had no
Force Index setup (only MFI, CMF, CLV-delta). Parameters fixed BEFORE any P&L was seen: force per 5-minute bar =
(close - previous close) x volume (first bar uses its own open as previous close); EMA13 of force restarted each
session; signal at the close of the first bar between 10:00 and 14:30 ET where EMA13 crosses zero and the close is
on the same side of session VWAP as the cross; one per session; direction = sign of the cross.
"""


def force_index_zero_cross(s):
    b = s.bars
    a = 2 / 14
    ema = None
    prev_ema = None
    prev_c = b[0].o
    for i, x in enumerate(b):
        f = (x.c - prev_c) * x.v
        prev_c = x.c
        prev_ema = ema
        ema = f if ema is None else ema + a * (f - ema)
        if prev_ema is None or x.m < 600 or x.m > 870 or i + 1 >= len(b):
            continue
        d = 1 if (prev_ema <= 0 < ema) else (-1 if (prev_ema >= 0 > ema) else 0)
        if d and (x.c - s.vwap[i]) * d > 0:
            yield i, d
            return


SETUPS = [
    dict(id='force_index_zero_cross', name='Force Index (13) zero cross with VWAP', family='volume',
         detect=force_index_zero_cross,
         rules="Elder's Force Index (close change times volume, 13-bar EMA, restarted each session) crosses "
               "through zero between 10:00 and 14:30 while price closes on the same side of VWAP: up-cross above "
               "VWAP leans long, down-cross below VWAP leans short. One signal per session; tested with and against."),
]
