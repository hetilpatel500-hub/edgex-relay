"""Ehlers band-pass filter crossing its RMS line, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (John Ehlers' band-pass / super bandpass filter trading rules
as quoted on prorealcode.com: long when the filter crosses above its RMS line, short when it crosses below the negative RMS
line; the forum user reports using it as stop-and-reverse on a 5-minute index chart, anecdotal only).
Parameters fixed BEFORE any P&L was seen: period 20, bandwidth 0.3 (Ehlers' textbook defaults), filter built inside the
session from its first close, RMS over the trailing 30 filter values (needs at least 20), signals 10:30 to 14:30 ET, at most
2 signals per side per session. No VWAP condition (the quoted rule has none).
"""
import math


def bandpass_rms_cross(s):
    b = s.bars
    n = len(b)
    per, bw = 20.0, 0.3
    beta = math.cos(2 * math.pi / per)
    gamma = 1.0 / math.cos(2 * math.pi * bw / per)
    alpha = gamma - math.sqrt(gamma * gamma - 1.0)
    bp = [0.0] * n
    for i in range(2, n):
        bp[i] = (0.5 * (1 - alpha) * (b[i].c - b[i - 2].c)
                 + beta * (1 + alpha) * bp[i - 1] - alpha * bp[i - 2])
    rms = [None] * n
    for i in range(n):
        w = bp[max(0, i - 29):i + 1]
        if len(w) >= 20:
            rms[i] = math.sqrt(sum(x * x for x in w) / len(w))
    cnt = {1: 0, -1: 0}
    for i in range(3, n):
        if b[i].m < 630 or b[i].m >= 870 or rms[i] is None or rms[i - 1] is None:
            continue
        up = bp[i] > rms[i] and bp[i - 1] <= rms[i - 1]
        dn = bp[i] < -rms[i] and bp[i - 1] >= -rms[i - 1]
        if up and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='ehlers_bandpass_rms', name='Ehlers band-pass (20, 0.3) cross of its RMS line', family='trend',
         detect=bandpass_rms_cross,
         rules="Ehlers band-pass filter (period 20, bandwidth 0.3) of the 5-minute closes, built from the session's first bar. "
               "When it crosses above its trailing RMS line (30 values) the setup leans long; when it crosses below the "
               "negative RMS line it leans short. 10:30 to 14:30 ET, at most two signals per side per session; "
               "tested with and against."),
]
