"""Bollinger squeeze -> expansion on 5-minute bars.
Added 2026-09-27 by volatility-analyst: volatility family, next open line of
the research queue in ai-workforce/chart-lab/README.md.
"""


def bb_squeeze_expansion(s):
    """Bollinger(20,2) on 5-minute closes. A squeeze bar is the one whose band
    width (4 stdev / SMA20) is the lowest of the last 20 bars: the tightest
    compression seen recently. The signal fires on the first of the next 6
    bars whose close breaks back outside that squeeze bar's own bands,
    leaning with the direction of the expansion."""
    b = s.bars
    closes = [x.c for x in b]
    n = len(b)
    window = 20
    if n < 2 * window:
        return
    sma, std = [None] * n, [None] * n
    for i in range(window - 1, n):
        seg = closes[i - window + 1:i + 1]
        m = sum(seg) / window
        var = sum((c - m) ** 2 for c in seg) / window
        sma[i], std[i] = m, var ** 0.5
    bw = [None] * n
    for i in range(window - 1, n):
        bw[i] = (4 * std[i]) / sma[i] if sma[i] else None
    fired = 0
    for i in range(2 * window - 2, n):
        if b[i].m >= 900 or fired >= 2:
            break
        if bw[i] is None or bw[i] != min(bw[i - window + 1:i + 1]):
            continue
        upper_i, lower_i = sma[i] + 2 * std[i], sma[i] - 2 * std[i]
        for j in range(i + 1, min(i + 7, n)):
            if b[j].c > upper_i:
                fired += 1; yield j, 1; break
            if b[j].c < lower_i:
                fired += 1; yield j, -1; break


SETUPS = [
    dict(id='bb_squeeze_expansion', name='Bollinger squeeze then expansion', family='volatility',
         detect=bb_squeeze_expansion,
         rules="Bollinger(20,2) band width at its 20-bar low marks a squeeze; the first of the next 6 bars "
               "whose close breaks back outside that bar's own bands leans with the breakout, before 15:00."),
]
