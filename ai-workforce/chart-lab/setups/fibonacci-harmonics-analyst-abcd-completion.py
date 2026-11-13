"""AB=CD harmonic completion on 5-minute bars.
Added 2026-10-06 by fibonacci-harmonics-analyst via the queue's fibonacci/harmonics family (the classic
AB=CD pattern, H.M. Gartley / Scott Carney; not yet tested here, distinct from fib618_opening_drive and abc_pullback).
Parameters fixed BEFORE any P&L was seen: swing pivots are 2-bar fractals confirmed two bars later (same as
core structure); A->B leg at least 1.0 ATR(5-min); B->C retraces 0.382-0.786 of AB; point D = C -/+ AB
(equal legs). Signal at the close of the first bar whose range reaches D, leaning against the CD leg, before
15:00, one per side per session. No look-ahead: only pivots confirmed by the signal bar are used.
"""


def abcd(s):
    b = s.bars
    n = len(b)
    piv = []                       # confirmed pivots: (bar, price, 'H'|'L')
    fired = {1: False, -1: False}
    for i in range(4, n):
        if b[i].m >= 900:
            return
        k = i - 2
        if k >= 2:
            if all(b[k].h > b[j].h for j in (k - 2, k - 1, k + 1, k + 2)):
                piv.append((k, b[k].h, 'H'))
            if all(b[k].l < b[j].l for j in (k - 2, k - 1, k + 1, k + 2)):
                piv.append((k, b[k].l, 'L'))
        piv.sort()
        if len(piv) < 3:
            continue
        atr = s.atr[i]
        if not atr:
            continue
        (ka, a, ta), (kb, bb, tb), (kc, c, tc) = piv[-3:]
        if not (ta == tc and ta != tb):
            continue
        ab = abs(a - bb)
        if ab < atr:
            continue
        bc = abs(c - bb)
        if not (0.382 * ab <= bc <= 0.786 * ab):
            continue
        if ta == 'H':              # bullish: A high, B low, C lower high, D = C - AB
            if c >= a:
                continue
            d_px = c - ab
            if not fired[1] and b[i].l <= d_px and min(x.l for x in b[kc + 1:i]) > d_px if i - 1 >= kc + 1 else False:
                fired[1] = True
                yield i, 1
        else:                      # bearish: A low, B high, C higher low, D = C + AB
            if c <= a:
                continue
            d_px = c + ab
            if not fired[-1] and b[i].h >= d_px and max(x.h for x in b[kc + 1:i]) < d_px if i - 1 >= kc + 1 else False:
                fired[-1] = True
                yield i, -1


SETUPS = [
    dict(id='abcd_completion', name='AB=CD harmonic completion', family='fibonacci',
         detect=abcd,
         rules="After a swing leg AB of at least 1 ATR and a 38.2-78.6% retracement BC, price travelling an "
               "equal leg CD to point D completes the AB=CD pattern: leans against the CD leg (long at a "
               "completed down CD, short at a completed up CD), at the close of the bar that first reaches D, "
               "before 15:00."),
]
