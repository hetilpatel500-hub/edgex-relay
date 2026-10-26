"""First pullback into the 9/20 EMA "bone zone" after the opening drive.
Added 2026-09-29 by price-structure-analyst: the queue's non-tape lines are all
coded, so this run used WebSearch (bullsonwallstreet.com first-pullback guide)
for a documented, untested idea. ema9_20_pullback tests any pullback in a
trending session; this is only the FIRST pullback in the first hour, after a
drive that made a new session extreme.
"""


def _ema(xs, n):
    k, out, e = 2 / (n + 1), [], None
    for x in xs:
        e = x if e is None else x * k + e * (1 - k)
        out.append(e)
    return out


def first_pullback(s):
    """Drive: by 10:00 a bar closes at a new session high (low) with the 9 EMA
    above (below) the 20 EMA of closes. First pullback: the first later bar
    (before 10:45) whose range touches the 9 EMA but whose low (high) holds
    above (below) the 20 EMA, and which closes back above (below) the 9 EMA in
    the drive direction. Lean with the drive. A close through the 20 EMA against
    the drive cancels it. One signal per session."""
    b = s.bars
    c = [x.c for x in b]
    e9, e20 = _ema(c, 9), _ema(c, 20)
    d = 0
    for i in range(3, len(b)):
        m = b[i].m
        if m >= 645:
            return
        if d == 0:
            if m < 600:
                hi = max(x.h for x in b[:i]); lo = min(x.l for x in b[:i])
                if b[i].c > hi and e9[i] > e20[i]:
                    d = 1
                elif b[i].c < lo and e9[i] < e20[i]:
                    d = -1
            continue
        if d == 1:
            if b[i].c < e20[i]:
                return
            if b[i].l <= e9[i] and b[i].l > e20[i] and b[i].c > e9[i]:
                yield i, 1
                return
        else:
            if b[i].c > e20[i]:
                return
            if b[i].h >= e9[i] and b[i].h < e20[i] and b[i].c < e9[i]:
                yield i, -1
                return


SETUPS = [
    dict(id='first_pullback', name='First pullback to the 9/20 EMA after the opening drive',
         family='price structure', detect=first_pullback,
         rules="By 10:00 a 5-minute bar closes at a new session high (low) with the 9 EMA above (below) the "
               "20 EMA. The first bar before 10:45 that dips to the 9 EMA without touching the 20 EMA and "
               "closes back beyond the 9 EMA is the first pullback; lean with the drive. A close through the "
               "20 EMA cancels it."),
]
