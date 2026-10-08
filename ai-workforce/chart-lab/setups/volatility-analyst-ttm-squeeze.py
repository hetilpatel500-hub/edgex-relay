"""TTM Squeeze fire on 5-minute bars.
Added 2026-10-05 by volatility-analyst via WebSearch: John Carter's TTM Squeeze
(https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ttm-squeeze,
https://www.luxalgo.com/library/concept/ttm-squeeze.md). Distinct from bb_squeeze_expansion (band-width rank) and
keltner_breakout (close outside channel): the squeeze is Bollinger(20,2) fully inside Keltner(20 EMA, 1.5 x ATR20).
Rules fixed BEFORE any P&L was seen: standard parameters, squeeze must have lasted >= 6 bars, fire = first bar the bands
leave the channel, direction = sign of momentum (close minus the mean of the 20-bar high/low midpoint and SMA20).
"""


def _ttm(s):
    b = s.bars
    n = len(b)
    w = 20
    if n < w + 8:
        return
    closes = [x.c for x in b]
    ema, k = [], 2 / (w + 1)
    for c in closes:
        ema.append(c if not ema else c * k + ema[-1] * (1 - k))
    tr = [b[0].h - b[0].l] + [max(b[i].h - b[i].l, abs(b[i].h - b[i - 1].c), abs(b[i].l - b[i - 1].c)) for i in range(1, n)]
    on, mom = [False] * n, [None] * n
    for i in range(w - 1, n):
        seg = closes[i - w + 1:i + 1]
        m = sum(seg) / w
        sd = (sum((c - m) ** 2 for c in seg) / w) ** 0.5
        atr = sum(tr[i - w + 1:i + 1]) / w
        on[i] = (m + 2 * sd < ema[i] + 1.5 * atr) and (m - 2 * sd > ema[i] - 1.5 * atr)
        mid = ((max(x.h for x in b[i - w + 1:i + 1]) + min(x.l for x in b[i - w + 1:i + 1])) / 2 + m) / 2
        mom[i] = closes[i] - mid
    run = 0
    fired = 0
    for i in range(w - 1, n):
        if b[i].m >= 900 or fired >= 2:
            break
        if on[i]:
            run += 1
            continue
        if run >= 6 and mom[i]:
            fired += 1
            yield i, 1 if mom[i] > 0 else -1
        run = 0


def ttm_squeeze_fire(s):
    yield from _ttm(s)


SETUPS = [
    dict(id='ttm_squeeze_fire', name='TTM Squeeze fire', family='volatility', detect=ttm_squeeze_fire,
         rules="Bollinger(20,2) bands sit entirely inside Keltner(20 EMA, 1.5 x ATR20) for at least 6 five-minute bars. "
               "On the first bar they leave the channel, lean the way the momentum reading points (close vs the "
               "midpoint of the 20-bar range and SMA20), before 15:00. Tested with and against."),
]
