"""Ehlers Even Better Sinewave (40/10) cross of -0.9 / +0.9 (5-minute bars).

From community write-ups of John Ehlers' "Cycle Analytics for Traders":
one-pole high-pass (40), Super Smoother (10), a 3-bar average wave
normalised by the square root of its recent power. The +/-0.9 crossings are
a community convention, not Ehlers' own text. Everything restarts each
session. Long at the first close between 10:00 and 14:30 ET where the value
crosses up through -0.9; short where it crosses down through +0.9; one per
side per session.

Snapshot from the Edgex chart lab (12 US symbols, 2026-05-15 to 2026-10-23,
OOS from 2026-09-09): validated when FADED, rvol+trend filter, 1.5 ATR stop
/ 3 ATR target: 50 OOS trades, 50% win, +0.32R avg, PF 1.70, t 1.72.
Re-test on your own data before relying on it.
"""
import math


def ebsw_cross(s):
    b = s.bars
    n = len(b)
    alpha1 = (1 - math.sin(2 * math.pi / 40)) / math.cos(2 * math.pi / 40)
    a1 = math.exp(-1.414 * math.pi / 10)
    c2 = 2 * a1 * math.cos(1.414 * math.pi / 10)
    c3 = -a1 * a1
    c1 = 1 - c2 - c3
    hp = [0.0] * n
    ss = [0.0] * n
    e = [0.0] * n
    for i in range(1, n):
        hp[i] = 0.5 * (1 + alpha1) * (b[i].c - b[i - 1].c) + alpha1 * hp[i - 1]
        h2 = hp[i - 1] if i >= 1 else 0.0
        ss[i] = c1 * (hp[i] + h2) / 2 + c2 * ss[i - 1] + (c3 * ss[i - 2] if i >= 2 else 0.0)
        if i >= 3:
            w = (ss[i] + ss[i - 1] + ss[i - 2]) / 3
            pw = (ss[i] ** 2 + ss[i - 1] ** 2 + ss[i - 2] ** 2) / 3
            e[i] = w / math.sqrt(pw) if pw > 0 else 0.0
    done = {1: False, -1: False}
    for i in range(5, n):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        if not done[1] and e[i] > -0.9 >= e[i - 1]:
            done[1] = True; yield i, 1
        elif not done[-1] and e[i] < 0.9 <= e[i - 1]:
            done[-1] = True; yield i, -1


SETUPS = [
    dict(id='ebsw_cross', name='Ehlers Even Better Sinewave (40/10) cross of -0.9 / +0.9', family='trend',
         detect=ebsw_cross,
         rules="Ehlers' Even Better Sinewave (high-pass 40, Super Smoother 10, 3-bar wave normalised by its power) "
               "crosses up through -0.9 (cycle start, leans long) or down through +0.9 (cycle end, leans short) on "
               "5-minute closes between 10:00 and 14:30. One signal per side per session; tested with and against."),
]
