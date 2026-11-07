"""Ehlers Reflex (20) re-entry from +/-2, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (Ehlers 2020 Reflex: SuperSmoother(20) of closes compared with a
straight line across the lookback, normalised by its own RMS so +/-2 marks an extreme; sources call it a cycle-timing tool and
give no intraday rule or backtest; Trendflex is the trend sibling and is not tested here).
Rules fixed BEFORE any P&L was seen: Ehlers' published formulas, N=20, RMS smoothing 0.04, series restarts each session,
signal on the close where Reflex moves back inside the band after the previous bar was beyond it (below -2 = long, above +2 = short),
10:30 to 14:30 ET (needs 20 bars to settle), at most 2 signals per side per session.
"""
import math

N = 20


def reflex_reentry(s):
    b = s.bars
    n = len(b)
    a1 = math.exp(-1.414 * math.pi / N)
    c2 = 2 * a1 * math.cos(1.414 * math.pi / N)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    f = [b[0].c, b[1].c if n > 1 else b[0].c] + [0.0] * max(n - 2, 0)
    for i in range(2, n):
        f[i] = c1 * (b[i].c + b[i - 1].c) / 2 + c2 * f[i - 1] + c3 * f[i - 2]
    ms = 0.0
    rf = [0.0] * n
    for i in range(N, n):
        slope = (f[i - N] - f[i]) / N
        tot = sum(f[i] + k * slope - f[i - k] for k in range(1, N + 1)) / N
        ms = 0.04 * tot * tot + 0.96 * ms
        rf[i] = tot / math.sqrt(ms) if ms > 0 else 0.0
    cnt = {1: 0, -1: 0}
    for i in range(N + 1, n):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        if rf[i - 1] < -2 <= rf[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif rf[i - 1] > 2 >= rf[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='reflex_reentry', name='Ehlers Reflex (20) re-entry from +/-2', family='trend',
         detect=reflex_reentry,
         rules="Ehlers' Reflex oscillator (20-bar SuperSmoother compared with a straight line over the lookback, "
               "normalised by its RMS, restarted each session): a close where Reflex comes back above -2 leans long; "
               "coming back below +2 leans short. 10:30 to 14:30 ET, at most two signals per side per session; "
               "tested with and against."),
]
