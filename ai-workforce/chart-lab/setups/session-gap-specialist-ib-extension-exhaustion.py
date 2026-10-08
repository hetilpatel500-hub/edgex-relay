"""IB 1x extension exhaustion.
Added 2026-10-03 by session-gap-specialist: after the initial balance, the
documented 1x / 2x IB-range extensions are used as mechanical targets (LuxAlgo
initial-balance library, NexusFi initial-balance article). Not yet in the lab:
ib_break trades the first break, ib_break_fail the failed first break. This tests
the other end: price has already travelled one full IB range beyond the IB and
fails to hold it.
"""


def ib_ext_exhaust(s):
    """After the first hour, a bar that trades at least 1x the IB range beyond the IB high
    (low) but closes back below (above) that 1x line leans short (long). Before 15:00, one
    signal per side per session."""
    b = s.bars
    rng = s.ib_hi - s.ib_lo
    if rng <= 0:
        return
    up_line, dn_line = s.ib_hi + rng, s.ib_lo - rng
    done = set()
    for i in range(12, len(b)):
        if b[i].m >= 900:
            return
        if 1 not in done and b[i].h >= up_line and b[i].c < up_line:
            done.add(1)
            yield i, -1
        elif -1 not in done and b[i].l <= dn_line and b[i].c > dn_line:
            done.add(-1)
            yield i, 1


SETUPS = [
    dict(id='ib_ext_exhaust', name='IB 1x extension exhaustion', family='session', detect=ib_ext_exhaust,
         rules="Once price has travelled a full initial-balance range beyond the IB high (low) and a "
               "5-minute bar closes back under (over) that 1x line, lean back toward the IB. After the "
               "first hour, before 15:00, one per side per session."),
]
