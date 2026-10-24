"""Developing POC first retest after an excursion.
Added 2026-10-05 by volume-vwap-analyst: POC family, a new idea (prior-day POC and the final session POC
are covered elsewhere; this uses the profile as it stood at each bar, no look-ahead). Asks whether the
first return to the developing point of control, after price travelled at least 1.5 ATR away from it,
is rejected (the POC acts as a support/resistance magnet that holds) or accepted.
Parameters fixed BEFORE any P&L was seen: profile built from bars 0..i-1 (5 bps buckets, core.profile);
10:30 to 14:30 ET; excursion = a close at least 1.5 ATR from the developing POC, at least 3 bars earlier;
touch = bar range reaches within 0.05 ATR of the POC; fires when the touch bar closes back on the
excursion side and in its direction; first touch only; one signal per session. The lab tests it with and against.
"""
import core


def developing_poc_retest(s):
    b = s.bars
    side = 0
    exc_i = None
    for i in range(7, len(b) - 1):
        a = s.atr[i]
        if not a:
            continue
        poc = core.profile(b[:i])[0]
        x = b[i]
        if poc is None:
            continue
        if x.m < 630 or x.m > 870:
            # keep tracking excursions before 10:30
            pass
        if side == 0:
            if x.c >= poc + 1.5 * a:
                side, exc_i = 1, i
            elif x.c <= poc - 1.5 * a:
                side, exc_i = -1, i
            continue
        if i - exc_i < 3:
            continue
        if side == 1:
            touch = x.l <= poc + 0.05 * a
            fire = x.c > poc and x.c > x.o
        else:
            touch = x.h >= poc - 0.05 * a
            fire = x.c < poc and x.c < x.o
        if not touch:
            continue
        if fire and 630 <= x.m <= 870:
            yield i, side
        break


SETUPS = [
    dict(id='developing_poc_retest', name='Developing POC first retest after a 1.5 ATR excursion',
         family='Volume profile', detect=developing_poc_retest,
         rules="Build the day's volume profile as it stands bar by bar. After price has closed at least 1.5 ATR "
               "away from the developing point of control, the first return to it (within 0.05 ATR) that closes "
               "back on the side price came from, in that direction, is the signal. 10:30 to 14:30, one a session."),
]
