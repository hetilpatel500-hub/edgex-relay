"""Ehlers Even Better Sinewave (40/10) cycle-start/-end cross of -0.9 / +0.9, 5-minute session bars.
Added 2026-10-14 by trend-moving-average-analyst via WebSearch (TradingView community write-ups of Ehlers' "Cycle
Analytics for Traders": one-pole high-pass, Super Smoother, 3-bar average wave, normalised by the square root of its
recent power; the +/-0.9 crossings are a community convention, not Ehlers' own text). The lab has the Roofing Filter,
Decycler, Super Smoother and Cyber Cycle, but not the sinewave. Parameters fixed BEFORE any P&L was seen:
high-pass duration 40, Super Smoother period 10, wave = mean of the last 3 Super Smoother values, power = mean of their
squares, EBSW = wave / sqrt(power), everything restarted each session (first values seeded at 0).
Long at the close of the first bar between 10:00 and 14:30 ET where EBSW crosses up through -0.9 (previous bar <= -0.9);
short where it crosses down through +0.9 (previous bar >= +0.9). One per side per session.
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
