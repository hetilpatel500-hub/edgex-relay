"""Stochastic(14,3,3) %K/%D crossover out of overbought/oversold.
Added 2026-09-28 by momentum-analyst: research queue in
ai-workforce/chart-lab/README.md was exhausted (all non-tape lines already
had setups; tape/ still holds 0 sessions, so the order-flow lines stay
blocked). momentum-analyst's own family (RSI / Stochastic) had no setup yet
-- RSI divergence was coded earlier by macd-divergence-analyst -- so this
run used WebSearch for a documented, untested momentum technique: the
classic slow Stochastic Oscillator, settings 14/3/3, per
https://www.daytrading.com/stochastic-oscillator and
https://admiralmarkets.com/education/articles/forex-indicators/stochastic-oscillator
-- %K crossing above %D while both are below 20 (oversold) is a buy signal;
%K crossing below %D while both are above 80 (overbought) is a sell signal.
"""


def _sma(x, n):
    out = [None] * len(x)
    for i in range(len(x)):
        w = x[max(0, i - n + 1):i + 1]
        if len(w) < n or None in w:
            continue
        out[i] = sum(w) / n
    return out


def _stochastic(highs, lows, closes, n=14, smooth_k=3, smooth_d=3):
    fast_k = [None] * len(closes)
    for i in range(len(closes)):
        if i < n - 1:
            continue
        hh = max(highs[i - n + 1:i + 1])
        ll = min(lows[i - n + 1:i + 1])
        fast_k[i] = 50.0 if hh == ll else 100 * (closes[i] - ll) / (hh - ll)
    slow_k = _sma(fast_k, smooth_k)
    d = _sma(slow_k, smooth_d)
    return slow_k, d


def stochastic_crossover(s):
    """Slow Stochastic(14,3,3) on the session's own 5-minute bars (%K = 3-bar
    SMA of the 14-bar fast %K, %D = 3-bar SMA of %K). The first %K/%D
    crossover with %K rising above %D while both sit below 20 leans long
    (out of oversold); the first crossover with %K falling below %D while
    both sit above 80 leans short (out of overbought). One signal per side
    per session, before 15:00."""
    b = s.bars
    k, d = _stochastic([x.h for x in b], [x.l for x in b], [x.c for x in b])
    fired_long = fired_short = False
    for i in range(1, len(b)):
        if b[i].m >= 900:
            break
        if None in (k[i], d[i], k[i - 1], d[i - 1]):
            continue
        if not fired_long and k[i - 1] <= d[i - 1] and k[i] > d[i] and k[i] < 20 and d[i] < 20:
            fired_long = True
            yield i, 1
        if not fired_short and k[i - 1] >= d[i - 1] and k[i] < d[i] and k[i] > 80 and d[i] > 80:
            fired_short = True
            yield i, -1


SETUPS = [
    dict(id='stochastic_crossover', name="Stochastic(14,3,3) crossover from overbought/oversold", family='momentum',
         detect=stochastic_crossover,
         rules="Slow Stochastic(14,3,3) on 5-minute bars. %K crossing above %D while both are below 20 "
               "(oversold) leans long; %K crossing below %D while both are above 80 (overbought) leans "
               "short. One signal per side per session, before 15:00."),
]
