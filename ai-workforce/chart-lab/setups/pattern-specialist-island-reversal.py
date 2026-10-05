"""Island reversal (daily).
Added 2026-10-05 by pattern-specialist: the research queue was fully ticked, so this run took the documented
island reversal (en.wikipedia.org/wiki/Island_reversal: a gap in one direction, a short cluster of bars, then a gap
back the other way, leaving the cluster isolated). Rules fixed BEFORE any P&L was seen: island of 1 to 5 bars, both
gaps measured high-vs-low (true price gaps, no minimum size), no volume filter, signal on the close of the bar that
gaps back.
"""


def island_reversal(ser):
    n = len(ser.c)
    for k in range(6, n):
        for width in range(1, 6):
            a = k - width              # first island bar
            if a < 1:
                break
            island = range(a, k)
            if ser.l[a] > ser.h[a - 1] and ser.h[k] < ser.l[k - 1] and all(ser.l[x] > ser.h[a - 1] for x in island):
                yield k, -1            # island top: gap up, cluster, gap down
                break
            if ser.h[a] < ser.l[a - 1] and ser.l[k] > ser.h[k - 1] and all(ser.h[x] < ser.l[a - 1] for x in island):
                yield k, 1             # island bottom: gap down, cluster, gap up
                break


SETUPS = [
    dict(id='d_island_reversal', tf='D', name='Island reversal (daily)', family='pattern (daily)',
         detect=island_reversal,
         rules="Price gaps up (the day's low is above the prior day's high), trades in a cluster of 1 to 5 sessions "
               "that never fills that gap, then gaps back down (the day's high is below the prior day's low): an "
               "island top, leaning short on that close. The mirror image after a gap down is an island bottom, "
               "leaning long."),
]
