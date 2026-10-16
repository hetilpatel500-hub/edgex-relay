"""Elder Ray pullback with the 13-EMA trend (Bear Power buy / Bull Power sell setup).
Added 2026-10-10 by trend-moving-average-analyst via WebSearch (queue was fully coded). Alexander Elder's Elder Ray:
Bull Power = high - EMA13, Bear Power = low - EMA13; trade only with the EMA's slope, buy when Bear Power is negative
but rising, sell when Bull Power is positive but falling. Published rules are for daily bars; no intraday version was
found, so this is a plain 5-minute transfer. Parameters fixed BEFORE any P&L was seen: EMA13 of closes restarted each
session; signal at the close of the first bar between 10:00 and 14:30 ET where the EMA is up over the last 6 bars,
Bear Power < 0 and higher than the previous bar's, and the bar closes up (mirror for shorts); one per session.
"""


def elder_ray_pullback(s):
    b = s.bars
    a = 2 / 14
    ema = []
    for x in b:
        ema.append(x.c if not ema else ema[-1] + a * (x.c - ema[-1]))
    for i in range(7, len(b) - 1):
        x = b[i]
        if x.m < 600 or x.m > 870:
            continue
        if ema[i] > ema[i - 6]:
            bear, bear_p = x.l - ema[i], b[i - 1].l - ema[i - 1]
            if bear < 0 and bear > bear_p and x.c > x.o:
                yield i, 1
                return
        elif ema[i] < ema[i - 6]:
            bull, bull_p = x.h - ema[i], b[i - 1].h - ema[i - 1]
            if bull > 0 and bull < bull_p and x.c < x.o:
                yield i, -1
                return


SETUPS = [
    dict(id='elder_ray_pullback', name='Elder Ray pullback with EMA13 trend', family='trend',
         detect=elder_ray_pullback,
         rules="Elder Ray on 5-minute bars (EMA13 of closes, restarted each session). Between 10:00 and 14:30, if the EMA "
               "has risen over the last 6 bars, Bear Power (low minus EMA) is negative but higher than the bar before and "
               "the bar closes up: long. Mirror: EMA falling, Bull Power (high minus EMA) positive but lower than the bar "
               "before and the bar closes down: short. One signal per session; tested with and against."),
]
