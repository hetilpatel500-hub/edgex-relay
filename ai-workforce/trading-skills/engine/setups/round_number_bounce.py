"""Whole-dollar round-number rejection (5-minute bars).

Whole-dollar levels act as support/resistance on equities because resting
orders, stop-losses and option strikes cluster there
(https://www.luxalgo.com/library/concept/round-numbers/). A bar that opens
below the nearest whole dollar, wicks up through it and closes back below
leans down; a bar that opens above, wicks down through it and closes back
above leans up. One signal per side per session, before 15:00.

Snapshot from the Edgex chart lab (12 US symbols, 2026-05-15 to 2026-10-23,
OOS from 2026-09-09): validated WITH the lean, vwap+rvol filter, 1 ATR stop
held to the close: 107 OOS trades, 33% win, +0.41R avg, PF 1.54, t 1.50;
forward test since freezing: 58 trades, +0.23R avg ("holding").
Re-test on your own data before relying on it.
"""


def round_number_bounce(s):
    b = s.bars
    fired_up = fired_dn = False
    for i in range(len(b)):
        if b[i].m >= 900:
            break
        x = b[i]
        lvl = round(x.o)
        if not fired_dn and x.o < lvl and x.h >= lvl and x.c < lvl:
            fired_dn = True
            yield i, -1
        if not fired_up and x.o > lvl and x.l <= lvl and x.c > lvl:
            fired_up = True
            yield i, 1


SETUPS = [
    dict(id='round_number_bounce', name='Whole-dollar round-number rejection', family='support/resistance',
         detect=round_number_bounce,
         rules="The whole-dollar level nearest a bar's open. A bar that opens below it, wicks through it, "
               "and closes back below leans down; a bar that opens above it, wicks through it, and closes "
               "back above leans up. One signal per side per session, before 15:00."),
]
