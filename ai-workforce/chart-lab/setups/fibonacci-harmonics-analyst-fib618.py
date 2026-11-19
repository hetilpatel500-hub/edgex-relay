"""61.8% retracement of the opening drive holding.
Added by fibonacci-harmonics-analyst: fibonacci family, next open line of the
research queue in ai-workforce/chart-lab/README.md.
"""


def fib618_opening_drive(s):
    """The opening drive is the session's directional push over the first 30
    minutes (bars 0-5): up if the 6th bar closes above the session open, down
    if below. The drive's extreme is the highest high (lowest low) of those
    six bars. The 61.8% retracement level measures back from that extreme
    toward the open. The first later bar that trades to that level and
    closes back in the drive's original direction confirms the retracement
    held; lean with the drive."""
    b = s.bars
    if len(b) < 7:
        return
    o = s.open
    seg = b[:6]
    if b[5].c > o:
        d = 1
        extreme = max(x.h for x in seg)
        lvl = extreme - 0.618 * (extreme - o)
    elif b[5].c < o:
        d = -1
        extreme = min(x.l for x in seg)
        lvl = extreme + 0.618 * (o - extreme)
    else:
        return
    fired = 0
    for i in range(6, len(b)):
        if b[i].m >= 900 or fired >= 2:
            break
        if d == 1 and b[i].l <= lvl and b[i].c > lvl:
            fired += 1
            yield i, 1
        elif d == -1 and b[i].h >= lvl and b[i].c < lvl:
            fired += 1
            yield i, -1


SETUPS = [
    dict(id='fib618_opening_drive', name='61.8% retracement of the opening drive holds', family='fibonacci',
         detect=fib618_opening_drive,
         rules="The first 30 minutes' directional push (open to its own extreme) defines the opening drive. "
               "The first bar that trades to the 61.8% retracement of that drive (measured back from the "
               "extreme toward the open) and closes back in the drive's direction confirms the level held, "
               "before 15:00."),
]
