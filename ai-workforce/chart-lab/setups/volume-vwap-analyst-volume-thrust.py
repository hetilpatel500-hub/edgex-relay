"""Volume thrust bar closing at its extreme, continuation.
Added 2026-09-29 by volume-vwap-analyst: WebSearch was not needed; this is the
continuation counterpart of `climax_reversal` (which fades heavy bars that
close against the move). A heavy, wide bar that breaks the session extreme
and closes near its own high (low) is read as aggressive participation with
no immediate absorption. Everything used is known at the bar's close.
"""


def volume_thrust(s):
    b = s.bars
    up_done = dn_done = False
    for i in range(12, len(b)):
        if b[i].m >= 870:
            return
        rng = b[i].h - b[i].l
        r, atr = s.rvol[i], s.atr[i]
        if rng <= 0 or r is None or r < 2.5 or not atr or rng < 1.5 * atr:
            continue
        prior_hi = max(x.h for x in b[:i])
        prior_lo = min(x.l for x in b[:i])
        if not up_done and b[i].h > prior_hi and b[i].c >= b[i].l + 0.8 * rng:
            up_done = True; yield i, 1
        elif not dn_done and b[i].l < prior_lo and b[i].c <= b[i].l + 0.2 * rng:
            dn_done = True; yield i, -1


SETUPS = [
    dict(id='volume_thrust', name='Volume thrust bar closing at its extreme', family='volume',
         detect=volume_thrust,
         rules="A bar with at least 2.5x its usual volume for that time slot and a range of at least 1.5 ATR "
               "that breaks the session high (low) and closes in the top (bottom) 20% of its range leans "
               "with the thrust, between 10:00 and 14:30. One per side per session."),
]
