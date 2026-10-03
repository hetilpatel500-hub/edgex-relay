"""Gap-and-go vs gap-fade, split by early relative volume.
Added 2026-09-28 by session-gap-specialist: next open line of the research
queue in ai-workforce/chart-lab/README.md ("Gap-and-go vs gap-fade split by
relative volume"). `gap_fill` in intraday.py already tests fading a gap once
price shows early movement back toward yesterday's close; this pair tests a
different, purely volume-based hypothesis instead of a price-confirmation
one: does the crowd showing up (or not) in the first 15 minutes decide
whether a gap keeps going or gives it back?

A gap session is one where the open sits at least 0.25% away from
yesterday's close (same threshold as gap_fill, not loosened). Early
relative volume is the average of the first three bars' `rvol` (9:30-9:45,
each bar's volume vs. its own 5-minute slot's 20-session average).

  gap_go_rvol    early rvol >= 1.3 (heavy participation): leans WITH the gap
                 direction, fired once at the close of bar index 2 (9:45).
  gap_fade_rvol  early rvol < 1.0 (light participation, no conviction):
                 leans AGAINST the gap direction (toward yesterday's close),
                 fired at the same bar.
Sessions with rvol in between (1.0-1.3) or with fewer than 20 prior sessions
of volume history for a slot (rvol is None) fire neither setup.
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
    d = _gap_dir(s)
    if d is None:
        return
    rv = _early_rvol(s)
    if rv is None or rv < 1.3:
        return
    yield 2, d


def gap_fade_rvol(s):
    d = _gap_dir(s)
    if d is None:
        return
    rv = _early_rvol(s)
    if rv is None or rv >= 1.0:
        return
    yield 2, -d


SETUPS = [
    dict(id='gap_go_rvol', name='Gap-and-go on heavy early volume', family='session/gaps', detect=gap_go_rvol,
         rules="A gap of 0.25%+ from yesterday's close with the first 15 minutes averaging 1.3x normal volume "
               "for those slots leans WITH the gap direction, fired at 9:45."),
    dict(id='gap_fade_rvol', name='Gap fade on light early volume', family='session/gaps', detect=gap_fade_rvol,
         rules="A gap of 0.25%+ from yesterday's close with the first 15 minutes averaging under 1x normal "
               "volume for those slots (no conviction) leans AGAINST the gap direction, fired at 9:45."),
]
