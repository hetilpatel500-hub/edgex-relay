"""RSI(14) divergence at the day's high/low.
Added by macd-divergence-analyst: momentum family, next open line of the
research queue in ai-workforce/chart-lab/README.md.
"""


def _rsi(closes, n=14):
    out, ag, al = [None] * len(closes), 0.0, 0.0
    for i in range(1, len(closes)):
        ch = closes[i] - closes[i - 1]
        g, l = max(ch, 0), max(-ch, 0)
        if i <= n:
            ag += g / n; al += l / n
            out[i] = None if i < n else (100 if al == 0 else 100 - 100 / (1 + ag / al))
        else:
            ag = (ag * (n - 1) + g) / n; al = (al * (n - 1) + l) / n
            out[i] = 100 if al == 0 else 100 - 100 / (1 + ag / al)
    return out


def rsi_divergence(s):
    """Track the session's developing high and low bar. The first time price
    sets a new session high while RSI(14) is lower than it was at the prior
    session-high bar (bearish divergence) leans short; the first time price
    sets a new session low while RSI is higher than at the prior session-low
    bar (bullish divergence) leans long. One signal per side per session."""
    b = s.bars
    rsi = _rsi([x.c for x in b])
    hi_i = lo_i = None
    fired_hi = fired_lo = False
    for i in range(14, len(b)):
        if b[i].m >= 900:
            break
        if rsi[i] is None:
            continue
        if hi_i is None or b[i].h > b[hi_i].h:
            if hi_i is not None and not fired_hi and rsi[i] < rsi[hi_i]:
                fired_hi = True
                yield i, -1
            hi_i = i
        if lo_i is None or b[i].l < b[lo_i].l:
            if lo_i is not None and not fired_lo and rsi[i] > rsi[lo_i]:
                fired_lo = True
                yield i, 1
            lo_i = i


SETUPS = [
    dict(id='rsi_divergence', name="RSI(14) divergence at the day's high/low", family='momentum',
         detect=rsi_divergence,
         rules="A new session high with RSI(14) lower than at the prior session-high bar (bearish divergence) "
               "leans short; a new session low with RSI higher than at the prior session-low bar (bullish "
               "divergence) leans long. One signal per side per session, before 15:00."),
]
