"""Ross Hook: first correction after a 1-2-3 breakout.
Added 2026-09-30 by pattern-specialist via WebSearch (fortraders.org and
oxfordstrat.com Ross Hook write-ups of Joe Ross's rule: the Ross Hook is the first
bar that fails to extend after price breaks the 1-2-3 pattern's point 2). Parameters
(break of structure as the breakout, hook within 6 bars, 10:00-15:00, one per day)
were fixed before any P&L was seen.
"""


def ross_hook(s):
    """A break of structure (close beyond the last swing high/low) is the 1-2-3
    breakout. The first later bar within 6 bars that fails to make a new extreme
    beyond the bar before it (the hook) leans with the breakout. Between 10:00 and
    15:00, one per session."""
    b = s.bars
    for j in range(len(b)):
        ev = s.event[j]
        if ev not in ('bos_up', 'bos_dn') or b[j].m < 600:
            continue
        d = 1 if ev == 'bos_up' else -1
        for i in range(j + 1, min(j + 7, len(b))):
            if b[i].m >= 900:
                return
            hook = b[i].h <= b[i - 1].h if d == 1 else b[i].l >= b[i - 1].l
            if hook:
                yield i, d
                return
            if s.event[i] in ('choch_up', 'choch_dn'):
                break


SETUPS = [
    dict(id='ross_hook', name='Ross Hook after a 1-2-3 breakout', family='pattern', detect=ross_hook,
         rules="After a close beyond the last swing high (or low) that breaks the market structure, the first "
               "5-minute bar within the next six that fails to make a new high (or low) beyond the bar before it "
               "is the hook, and price leans with the breakout. Between 10:00 and 15:00, one per session."),
]
