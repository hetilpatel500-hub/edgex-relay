"""Ehlers Fisher Transform extreme crossover.
Added 2026-10-02 by momentum-analyst: the research queue's non-tape lines are
all coded, so this run used WebSearch (Trading Technologies, quantifiedstrategies.com,
howtotrade.com Fisher Transform guides: 9-period default, Fisher line crossing its
one-bar-lagged trigger from beyond +/-1.5) for a documented, untested idea.
Rules fixed before any P&L was seen.
"""
import math


def fisher_extreme_cross(s):
    """Fisher Transform on 9 five-minute bars of (high+low)/2, built inside the
    session: x = 0.33*2*((p-low9)/(high9-low9)-0.5) + 0.67*x_prev clamped to
    +/-0.999; fisher = 0.5*ln((1+x)/(1-x)) + 0.5*fisher_prev; trigger = fisher
    one bar earlier. Fisher crossing up through the trigger while the trigger is
    below -1.5 leans long; crossing down while the trigger is above +1.5 leans
    short. 10:15 to 14:30 ET, at most 2 signals per side per session."""
    b = s.bars
    n = 9
    x = f = 0.0
    fish = []
    for i in range(len(b)):
        if i < n - 1:
            fish.append(None)
            continue
        w = b[i - n + 1:i + 1]
        hi, lo = max(y.h for y in w), min(y.l for y in w)
        p = (b[i].h + b[i].l) / 2
        raw = 0.66 * ((p - lo) / (hi - lo) - 0.5) if hi > lo else 0.0
        x = max(-0.999, min(0.999, raw + 0.67 * x))
        f = 0.5 * math.log((1 + x) / (1 - x)) + 0.5 * f
        fish.append(f)
    cnt = {1: 0, -1: 0}
    for i in range(n, len(b)):
        if b[i].m < 615 or b[i].m >= 870:
            continue
        f1, f0 = fish[i], fish[i - 1]
        if f0 is None:
            continue
        if f1 > f0 and fish[i - 1] <= (fish[i - 2] if fish[i - 2] is not None else f0) and f0 < -1.5 and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif f1 < f0 and fish[i - 1] >= (fish[i - 2] if fish[i - 2] is not None else f0) and f0 > 1.5 and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='fisher_extreme_cross', name='Fisher Transform extreme crossover', family='momentum',
         detect=fisher_extreme_cross,
         rules="Ehlers Fisher Transform (9 five-minute bars): when the Fisher line turns up through its "
               "one-bar-lagged trigger while below -1.5, it leans long; turning down through the trigger "
               "while above +1.5, it leans short. From 10:15 to 14:30 ET, at most two signals per side per session."),
]
