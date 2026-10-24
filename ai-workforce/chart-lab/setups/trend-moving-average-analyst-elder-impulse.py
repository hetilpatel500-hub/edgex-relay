"""Elder Impulse System turn, with VWAP side.
Added 2026-10-02 by trend-moving-average-analyst: Dr. Alexander Elder's Impulse
System (EMA13 slope + MACD(12,26,9) histogram slope colouring bars green / red /
blue; documented for 5-minute to 1-hour charts). Not yet in the lab. Rules fixed
before any P&L was seen.
"""


def _ema(x, n):
    k = 2 / (n + 1)
    out = [x[0]]
    for v in x[1:]:
        out.append(out[-1] + k * (v - out[-1]))
    return out


def elder_impulse(s):
    """Per bar: green = EMA13 and MACD histogram both higher than the prior bar;
    red = both lower; else blue. The first green bar after a non-green bar that
    closes above session VWAP leans long; the first red bar after a non-red bar
    that closes below VWAP leans short. 10:00 to 14:30 ET, at most 2 per side."""
    b = s.bars
    c = [y.c for y in b]
    e13 = _ema(c, 13)
    macd = [a - d for a, d in zip(_ema(c, 12), _ema(c, 26))]
    hist = [m - g for m, g in zip(macd, _ema(macd, 9))]
    col = [0] * len(b)
    for i in range(1, len(b)):
        if e13[i] > e13[i - 1] and hist[i] > hist[i - 1]:
            col[i] = 1
        elif e13[i] < e13[i - 1] and hist[i] < hist[i - 1]:
            col[i] = -1
    cnt = {1: 0, -1: 0}
    for i in range(27, len(b)):
        if b[i].m < 600 or b[i].m >= 870:
            continue
        if col[i] == 1 and col[i - 1] != 1 and c[i] > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif col[i] == -1 and col[i - 1] != -1 and c[i] < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='elder_impulse_turn', name='Elder Impulse turn with VWAP side', family='trend',
         detect=elder_impulse,
         rules="Elder Impulse System on 5-minute bars: a bar is green when the 13-bar EMA and the MACD "
               "(12,26,9) histogram both rose from the prior bar, red when both fell. The first green bar "
               "after a non-green one that closes above session VWAP leans long; the first red bar after "
               "a non-red one that closes below VWAP leans short. 10:00 to 14:30 ET, at most two signals "
               "per side per session."),
]
