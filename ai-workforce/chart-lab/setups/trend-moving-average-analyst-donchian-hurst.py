"""Donchian 20-bar breakout gated by a Hurst exponent above 0.5, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (StockSharp "Donchian Hurst Exponent" strategy: 20-period
Donchian breakout, 100-period Hurst window, 0.5 threshold, 5-minute candles). A vendor listing with no verified
performance. The lab has donchian10_break and a daily Donchian but no persistence (Hurst) gate.
Parameters fixed BEFORE any P&L was seen: Hurst estimated by the aggregated-variance method on the last 100 5-minute log
returns (prior session's returns count; the overnight gap return is dropped): H = slope of log(std of k-bar summed
returns) on log(k) for k = 1, 2, 4, 8. Signal when a bar closes beyond the highest high / lowest low of the previous 20
bars while H > 0.5. From the 21st bar (11:05) to 14:55 ET, one signal per direction per session.
"""
import math


def _hurst(r):
    xs, ys = [], []
    for k in (1, 2, 4, 8):
        agg = [sum(r[j:j + k]) for j in range(0, len(r) - k + 1, k)]
        if len(agg) < 4:
            return None
        m = sum(agg) / len(agg)
        sd = math.sqrt(sum((a - m) ** 2 for a in agg) / (len(agg) - 1))
        if sd <= 0:
            return None
        xs.append(math.log(k)); ys.append(math.log(sd))
    mx, my = sum(xs) / 4, sum(ys) / 4
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def _rets(bars):
    return [math.log(bars[i].c / bars[i - 1].c) for i in range(1, len(bars)) if bars[i - 1].c > 0 and bars[i].c > 0]


def donchian_hurst(s):
    b = s.bars
    if s.prior is None:
        return
    prior_r = _rets(s.prior.bars)
    today_r = _rets(b)                       # today_r[i-1] is bar i's return
    done = set()
    for i in range(20, len(b)):
        if b[i].m >= 895:
            break
        hh = max(x.h for x in b[i - 20:i])
        ll = min(x.l for x in b[i - 20:i])
        d = 1 if b[i].c > hh else -1 if b[i].c < ll else 0
        if d == 0 or d in done:
            continue
        r = (prior_r + today_r[:i])[-100:]
        h = _hurst(r)
        if h is not None and h > 0.5:
            done.add(d)
            yield i, d


SETUPS = [
    dict(id='donchian_hurst', name='Donchian 20-bar breakout with Hurst > 0.5', family='trend',
         detect=donchian_hurst,
         rules="A 5-minute bar closing above the highest high (below the lowest low) of the previous 20 bars, only "
               "when the Hurst exponent of the last 100 five-minute returns (aggregated-variance estimate, prior "
               "session included) is above 0.5, i.e. returns have been trending rather than mean-reverting. "
               "11:05 to 14:55 ET, one signal per direction per session; tested with and against."),
]
