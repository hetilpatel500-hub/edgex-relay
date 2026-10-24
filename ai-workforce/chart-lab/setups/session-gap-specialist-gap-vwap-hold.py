"""Gap that holds its side of VWAP through the second half hour.
Added 2026-10-04 by session-gap-specialist via WebSearch (VWAP-as-institutional-benchmark
write-ups: a gap that VWAP supports is "accepted"). gap_go_rvol splits gaps by volume; this
splits them by VWAP acceptance. Parameters fixed BEFORE any P&L was seen: gap of at least 0.3%
versus yesterday's close, every 5-minute close from 10:00 to 10:30 on the gap's side of VWAP,
signal at the 10:30 close, one per session. The lab tests it with and against.
"""


def gap_vwap_hold(s):
    p = s.prior
    b = s.bars
    if p is None or len(b) < 12 or b[11].m != 625:
        return
    gap = s.open / p.close - 1
    if abs(gap) < 0.003:
        return
    d = 1 if gap > 0 else -1
    if all(d * (b[k].c - s.vwap[k]) > 0 for k in range(6, 12)):
        yield 11, d


SETUPS = [
    dict(id='gap_vwap_hold', name='Gap accepted: held its side of VWAP 10:00-10:30', family='session',
         detect=gap_vwap_hold,
         rules="Open gaps at least 0.3% from yesterday's close and every 5-minute close from 10:00 to "
               "10:30 stays on the gap's side of VWAP: lean with the gap at the 10:30 close, once per session."),
]
