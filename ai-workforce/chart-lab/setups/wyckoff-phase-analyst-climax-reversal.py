"""Selling / buying climax reversal on effort-vs-result.
Added 2026-09-29 by wyckoff-phase-analyst: new idea from the Wyckoff
playbook (climactic volume at a session extreme that closes back against the
move). Unlike `spring_upthrust` (low-effort probe at the IB extreme), this
fires on HIGH effort: a very heavy, very wide bar that makes a new session
low (high) but closes in the opposite half of its range, i.e. the market
absorbed the flush. Everything used is known at the bar's close.
"""


def climax_reversal(s):
    b = s.bars
    up_done = dn_done = False
    for i in range(6, len(b)):
        if b[i].m >= 900:
            return
        rng = b[i].h - b[i].l
        r, atr = s.rvol[i], s.atr[i]
        if rng <= 0 or r is None or r < 3.0 or not atr or rng < 2.0 * atr:
            continue
        prior_lo = min(x.l for x in b[:i])
        prior_hi = max(x.h for x in b[:i])
        if not up_done and b[i].l < prior_lo and b[i].c >= b[i].l + 0.6 * rng:
            up_done = True; yield i, 1
        elif not dn_done and b[i].h > prior_hi and b[i].c <= b[i].l + 0.4 * rng:
            dn_done = True; yield i, -1


SETUPS = [
    dict(id='climax_reversal', name='Volume climax reversal at a session extreme', family='wyckoff',
         detect=climax_reversal,
         rules="A bar with at least 3x its usual volume for that time slot and a range of at least 2 ATR "
               "that makes a new session low (high) but closes in the top (bottom) 40% of its range is a "
               "selling (buying) climax: lean long (short) on the reversal, before 15:00. One per side per "
               "session."),
]
