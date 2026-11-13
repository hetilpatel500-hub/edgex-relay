"""Hikkake: inside-bar false breakout (Daniel Chesler, Active Trader, April 2004).
Added 2026-09-30 by pattern-specialist via WebSearch (hikkake / inside-day
false-breakout guides). Parameters (inside bar 10:00-14:30, false break then
snap-back close within 3 bars, one per day) were fixed before any P&L was seen.
"""


def hikkake(s):
    """A 5-minute inside bar (high below and low above the previous bar) between
    10:00 and 14:30. If a later bar trades below the inside bar's low and, within
    3 bars of the inside bar, a bar closes back above the inside bar's high, lean
    long on that close (mirror for a false break up). One per day."""
    b = s.bars
    for i in range(1, len(b)):
        m = b[i].m
        if m < 600 or m + 5 > 870:
            continue
        if not (b[i].h < b[i - 1].h and b[i].l > b[i - 1].l):
            continue
        hi, lo = b[i].h, b[i].l
        broke_dn = broke_up = False
        for j in range(i + 1, min(i + 4, len(b))):
            if b[j].m + 5 > 900:
                break
            if broke_dn and not broke_up and b[j].c > hi:
                yield j, 1
                return
            if broke_up and not broke_dn and b[j].c < lo:
                yield j, -1
                return
            if b[j].l < lo:
                broke_dn = True
            if b[j].h > hi:
                broke_up = True
            if broke_up and broke_dn:
                break


SETUPS = [
    dict(id='hikkake', name='Hikkake: inside-bar false breakout', family='pattern',
         detect=hikkake,
         rules="Between 10:00 and 14:30, a 5-minute inside bar. If price breaks below its low and, within 3 bars, "
               "a bar closes back above its high, the trap leans long (mirror for a false break up). One per day."),
]
