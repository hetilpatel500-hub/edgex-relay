"""MACD histogram flip with VWAP agreement.
Added by macd-divergence-analyst: macd family, next open line of the
research queue in ai-workforce/chart-lab/README.md.
"""


def _ema(closes, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for c in closes:
        prev = c if prev is None else c * k + prev * (1 - k)
        out.append(prev)
    return out


def macd_vwap_flip(s):
    """MACD(12,26,9) on 5-minute closes: macd line = EMA12 - EMA26, signal =
    EMA9 of the macd line, histogram = macd - signal. The first bar where the
    histogram flips from negative to positive while price closes above VWAP
    leans long (momentum and location agree); the mirror flip to negative
    with price below VWAP leans short. One signal per side per session."""
    b = s.bars
    closes = [x.c for x in b]
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    macd_line = [a - c for a, c in zip(ema12, ema26)]
    signal = _ema(macd_line, 9)
    hist = [m - g for m, g in zip(macd_line, signal)]
    warmup = 35
    fired = 0
    for i in range(max(warmup, 1), len(b)):
        if b[i].m >= 900 or fired >= 3:
            break
        if hist[i - 1] <= 0 and hist[i] > 0 and b[i].c > s.vwap[i]:
            fired += 1
            yield i, 1
        elif hist[i - 1] >= 0 and hist[i] < 0 and b[i].c < s.vwap[i]:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='macd_vwap_flip', name='MACD histogram flip with VWAP agreement', family='macd',
         detect=macd_vwap_flip,
         rules="MACD(12,26,9) histogram flips from negative to positive with price closing above VWAP leans "
               "long; the mirror flip to negative with price below VWAP leans short. One signal per side per "
               "session, before 15:00, after a 35-bar warmup."),
]
