"""Initial balance broken on both sides (neutral-day flip).
Added 2026-10-01 by session-gap-specialist, from a WebSearch run (luxalgo.com
Day-type Taxonomy; quant-radar.com Day Structure Types): a session that
extends beyond both ends of the initial balance is a Market Profile neutral
day, where the first break was a failed trend attempt. Rules and thresholds
were fixed before any P&L was seen; everything is known at the signal bar's
close. Distinct from ib_break (first break) and ib_break_fail (close back
inside), which do not require the opposite side to break.
"""


def ib_both_sides_flip(s):
    """After 10:30 and before 14:30, a 5-minute close beyond one side of the 9:30-10:30
    initial balance is the first break. The first later bar that closes beyond the
    opposite side (within 24 bars of the first break) is the flip: signal in the flip's
    direction (the move away from the first break). One per session."""
    b = s.bars
    first = None
    for i in range(12, len(b)):
        if b[i].m >= 870:
            return
        if first is None:
            if b[i].c > s.ib_hi:
                first = (1, i)
            elif b[i].c < s.ib_lo:
                first = (-1, i)
            continue
        d, k = first
        if i - k > 24:
            return
        if d == 1 and b[i].c < s.ib_lo:
            yield i, -1
            return
        if d == -1 and b[i].c > s.ib_hi:
            yield i, 1
            return


SETUPS = [
    dict(id='ib_both_sides_flip', name='Initial balance broken on both sides (neutral-day flip)',
         family='initial balance', detect=ib_both_sides_flip,
         rules="After 10:30, a 5-minute close beyond one end of the 9:30-10:30 initial balance is the first break. "
               "If a later bar within two hours closes beyond the opposite end, the first break failed and the "
               "day is a neutral day; the signal is the direction of that second break. Tested with it and "
               "against it (fade). One per session, before 14:30."),
]
