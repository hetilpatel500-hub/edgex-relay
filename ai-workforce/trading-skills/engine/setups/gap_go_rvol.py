"""Gap-and-go on heavy early volume.

A gap session opens at least 0.25% away from yesterday's close. Early
relative volume is the average of the first three bars' rvol (9:30-9:45,
each bar's volume against its own 5-minute slot's 20-session average). With
early rvol >= 1.3 the setup leans WITH the gap direction, fired at 9:45.

Snapshot from the Edgex chart lab (12 US symbols, 2026-05-15 to 2026-10-23,
OOS from 2026-09-09): validated WITH the gap, vwap+rvol filter, 1 ATR stop
held to the close: 31 OOS trades, 35% win, +0.90R avg, PF 2.29, t 1.51.
Few trades; re-test on your own data before relying on it.
"""


def _early_rvol(s):
    vals = [s.rvol[k] for k in range(3)]
    if any(v is None for v in vals):
        return None
    return sum(vals) / 3


def _gap_dir(s):
    p = s.prior
    if p is None:
        return None
    g = s.open / p.close - 1
    if abs(g) < 0.0025:
        return None
    return 1 if g > 0 else -1


def gap_go_rvol(s):
    if len(s.bars) < 3:
        return
    d = _gap_dir(s)
    if d is None:
        return
    rv = _early_rvol(s)
    if rv is None or rv < 1.3:
        return
    yield 2, d


SETUPS = [
    dict(id='gap_go_rvol', name='Gap-and-go on heavy early volume', family='session/gaps', detect=gap_go_rvol,
         rules="A gap of 0.25%+ from yesterday's close with the first 15 minutes averaging 1.3x normal volume "
               "for those slots leans WITH the gap direction, fired at 9:45."),
]
