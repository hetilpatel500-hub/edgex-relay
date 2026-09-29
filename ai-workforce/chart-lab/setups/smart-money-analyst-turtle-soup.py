"""Turtle Soup: false break of the prior 20-bar extreme on 5-minute bars.
Added 2026-09-28 by smart-money-analyst: the research queue's non-tape lines
are all coded, so this run used WebSearch (luxalgo.com, turtletrader.com,
alchemymarkets.com) for a documented, untested liquidity-raid technique from
Connors and Raschke's Street Smarts (1995). Distinct from pd_sweep and
ib_sweep, which sweep fixed session levels; this sweeps a rolling 20-bar
extreme.
"""


def turtle_soup(s):
    """A bar whose low undercuts the lowest low of the prior 20 bars, where
    that prior low is at least 4 bars old, yet closes back above it, leans
    long; the mirror at the highest high of the prior 20 bars leans short.
    One signal per side per session, from 11:10 to 14:30."""
    b = s.bars
    fired = set()
    for i in range(20, len(b)):
        if b[i].m >= 870:
            break
        win = b[i - 20:i]
        lo = min(x.l for x in win)
        hi = max(x.h for x in win)
        lo_age = i - (i - 20 + min(range(20), key=lambda k: win[k].l))
        hi_age = i - (i - 20 + max(range(20), key=lambda k: win[k].h))
        x = b[i]
        if 1 not in fired and x.l < lo and x.c > lo and lo_age >= 4:
            fired.add(1)
            yield i, 1
        elif -1 not in fired and x.h > hi and x.c < hi and hi_age >= 4:
            fired.add(-1)
            yield i, -1


SETUPS = [
    dict(id='turtle_soup', name='Turtle Soup: false break of the prior 20-bar extreme', family='smart-money',
         detect=turtle_soup,
         rules="A 5-minute bar that breaks below the lowest low of the prior 20 bars (that low at least 4 bars "
               "old) but closes back above it leans long; a break above the highest high of the prior 20 bars "
               "that closes back below leans short. One signal per side per session, 11:10 to 14:30."),
]
