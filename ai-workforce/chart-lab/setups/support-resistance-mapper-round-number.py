"""Whole-dollar round-number level rejection on 5-minute bars.
Added 2026-09-28 by support-resistance-mapper: the research queue in
ai-workforce/chart-lab/README.md is exhausted for non-tape lines (every
other line already has a coded, backtested setup, confirmed against
PLAYBOOK.md and setups/ before treating it as exhausted; the "waiting for
tape" order-flow lines stay blocked, tape/ holds 0 sessions). This run used
WebSearch for a documented, untested technique squarely inside
support-resistance-mapper's own charter ("session levels: prior-day
high/low/close, pivots, round numbers") that isn't just another variant of
the pivot_bounce setup already coded this run: whole-dollar round-number
levels. Per https://www.luxalgo.com/library/concept/round-numbers/ and
https://atas.net/blog/the-magic-of-round-numbers/, whole (and half) dollar
marks act as support/resistance on equities because resting orders,
stop-losses and option strikes cluster there; a probe that fails to close
through is read as a bounce/rejection off the level, treated as a zone
rather than an exact line.
"""


def round_number_bounce(s):
    """The whole-dollar level nearest each bar's open. A bar that opens
    below that level, wicks up through it, but closes back below it leans
    down (rejection from above); a bar that opens above the level, wicks
    down through it, but closes back above it leans up (rejection from
    below). One signal per side per session, before 15:00."""
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
