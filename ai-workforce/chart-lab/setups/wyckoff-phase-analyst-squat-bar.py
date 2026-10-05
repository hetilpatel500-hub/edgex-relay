"""Bill Williams squat bar after an extended leg, 5-minute bars.
Added 2026-10-04 by wyckoff-phase-analyst: the research queue held only tape items, so this run took a
documented technique (Williams' Market Facilitation Index: a "squat" bar has volume UP and range-per-volume
DOWN versus the previous bar, i.e. a fight where the market makes no headway). effort_no_result already
tests absorption at a session extreme; this tests the formal MFI squat after a 6-bar leg anywhere in the
session. Rules fixed BEFORE any P&L was seen: leg >= 1.5 ATR over the prior 6 bars, squat bar volume > prior
bar and range/volume < prior bar, rvol >= 1.5, trigger = a close beyond the squat bar's far side within 3 bars.
"""


def squat_bar_reversal(s):
    """After a leg of at least 1.5 ATR in 6 bars, a squat bar (volume above the previous bar, range per
    unit volume below it, relative volume >= 1.5) means the leg met opposition. A close back through the
    squat bar's far side within 3 bars leans against the leg. At most two signals a session, before 15:00."""
    b = s.bars
    fired = 0
    pend = []  # (dir, trigger, expires)
    for i in range(7, len(b)):
        if b[i].m >= 900 or fired >= 2:
            return
        for p in list(pend):
            d, lvl, exp = p
            if i > exp:
                pend.remove(p)
            elif (d == 1 and b[i].c > lvl) or (d == -1 and b[i].c < lvl):
                pend.remove(p)
                fired += 1
                yield i, d
                if fired >= 2:
                    return
        atr, rv = s.atr[i], s.rvol[i]
        if not atr or not rv or rv < 1.5:
            continue
        rng, prng = b[i].h - b[i].l, b[i - 1].h - b[i - 1].l
        if not b[i].v or not b[i - 1].v or rng <= 0 or prng <= 0:
            continue
        if not (b[i].v > b[i - 1].v and rng / b[i].v < prng / b[i - 1].v):
            continue
        leg = b[i - 1].c - b[i - 7].c
        if leg <= -1.5 * atr:
            pend.append((1, b[i].h, i + 3))
        elif leg >= 1.5 * atr:
            pend.append((-1, b[i].l, i + 3))


SETUPS = [
    dict(id='squat_bar_reversal', name='Williams squat bar after an extended leg', family='wyckoff',
         detect=squat_bar_reversal,
         rules="After a 6-bar leg of at least 1.5 ATR, a 5-minute bar with more volume than the one before "
               "it but less range per unit of volume (a Williams squat bar) and at least 1.5x its usual "
               "volume shows the leg meeting opposition. A close within 3 bars back through the squat bar's "
               "far side leans against the leg. Before 15:00."),
]
