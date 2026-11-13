"""Ehlers MESA Adaptive Moving Average (MAMA) cross of FAMA, 5-minute bars.
Added 2026-10-13 by trend-moving-average-analyst via WebSearch (John Ehlers, "MESA Adaptive Moving Averages", 2001;
published limits fast 0.5, slow 0.05; community signal: MAMA crossing FAMA sets the bias).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: Ehlers' published limits 0.5 / 0.05, Hilbert-transform
phase estimate built inside each session from its first close, cross must also have the close on the same side of VWAP,
10:30 to 14:30 ET, at most 2 signals per side per session. Everything is known at the signal bar's close.
"""
import math


def _hil(x, i, per):
    g = lambda k: x[i - k] if i - k >= 0 else 0.0
    return (0.0962 * g(0) + 0.5769 * g(2) - 0.5769 * g(4) - 0.0962 * g(6)) * (0.075 * per + 0.54)


def mama_fama(s):
    b = s.bars
    n = len(b)
    p = [x.c for x in b]
    sm = [0.0] * n; det = [0.0] * n; q1 = [0.0] * n; i1 = [0.0] * n
    i2 = [0.0] * n; q2 = [0.0] * n; re = [0.0] * n; im = [0.0] * n
    per = [0.0] * n; phase = [0.0] * n
    mama = [p[0]] * n; fama = [p[0]] * n
    fast, slow = 0.5, 0.05
    for i in range(n):
        if i < 6:
            sm[i] = p[i]
            continue
        sm[i] = (4 * p[i] + 3 * p[i - 1] + 2 * p[i - 2] + p[i - 3]) / 10
        pp = per[i - 1] or 6.0
        det[i] = _hil(sm, i, pp)
        q1[i] = _hil(det, i, pp)
        i1[i] = det[i - 3]
        ji = _hil(i1, i, pp)
        jq = _hil(q1, i, pp)
        i2[i] = 0.2 * (i1[i] - jq) + 0.8 * i2[i - 1]
        q2[i] = 0.2 * (q1[i] + ji) + 0.8 * q2[i - 1]
        r = i2[i] * i2[i - 1] + q2[i] * q2[i - 1]
        m = i2[i] * q2[i - 1] - q2[i] * i2[i - 1]
        re[i] = 0.2 * r + 0.8 * re[i - 1]
        im[i] = 0.2 * m + 0.8 * im[i - 1]
        pr = per[i - 1]
        if im[i] != 0 and re[i] != 0:
            pr = 360 / math.degrees(math.atan(im[i] / re[i]))
        if pr > 1.5 * per[i - 1] and per[i - 1]:
            pr = 1.5 * per[i - 1]
        if pr < 0.67 * per[i - 1]:
            pr = 0.67 * per[i - 1]
        pr = min(50.0, max(6.0, pr))
        per[i] = 0.2 * pr + 0.8 * per[i - 1]
        phase[i] = math.degrees(math.atan(q1[i] / i1[i])) if i1[i] != 0 else phase[i - 1]
        dp = max(1.0, phase[i - 1] - phase[i])
        al = min(fast, max(slow, fast / dp))
        mama[i] = al * p[i] + (1 - al) * mama[i - 1]
        fama[i] = 0.5 * al * mama[i] + (1 - 0.5 * al) * fama[i - 1]
    return mama, fama


def detect(s):
    b = s.bars
    mama, fama = mama_fama(s)
    cnt = {1: 0, -1: 0}
    for i in range(13, len(b)):
        if b[i].m < 630 or b[i].m >= 870:
            continue
        up = mama[i] > fama[i] and mama[i - 1] <= fama[i - 1]
        dn = mama[i] < fama[i] and mama[i - 1] >= fama[i - 1]
        if up and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='mama_fama_cross_vwap', name='Ehlers MAMA/FAMA cross with VWAP', family='trend', detect=detect,
         rules="Ehlers' MESA Adaptive Moving Average (limits 0.5 / 0.05) crossing above its follower FAMA with the 5-minute "
               "close above VWAP leans long; crossing below with the close below VWAP leans short. 10:30 to 14:30 ET, at most "
               "two signals per side per session; tested with and against."),
]
