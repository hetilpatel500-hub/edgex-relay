"""Single prints and poor high/low from yesterday's volume profile, revisited today.
Added 2026-09-28 by volume-vwap-analyst: next open line of the research queue in
ai-workforce/chart-lab/README.md ("Single prints / poor high or low from
yesterday's profile revisited").

- A single print is a price bin (same bps bucketing as core.profile) that
  yesterday's session touched with only one 5-minute bar: a fast, thin
  passage with little resting volume. Today's first bar that trades into the
  widest such zone and closes back out the side it came in from leans WITH
  that close (a thin spot gets filled through quickly rather than holding).
- A poor high/low is when yesterday's own session extreme bin (the one
  holding the session high or low) was touched by more than one bar: the
  auction didn't reject it cleanly, so the level is unfinished business.
  A clean extreme (touched by exactly one bar) is left untested by this
  setup. Today's first close beyond a poor high/low leans WITH the break,
  before 15:00.
"""
import statistics as st


def _bins(bars, bps=5.0):
    px = st.median(x.c for x in bars)
    step = px * bps / 1e4
    touches = {}
    for x in bars:
        lo, hi = int(x.l // step), int(x.h // step)
        for k in range(lo, hi + 1):
            touches[k] = touches.get(k, 0) + 1
    return touches, step


def _single_print_zone(bars):
    """Price of the widest run of bins yesterday touched exactly once."""
    touches, step = _bins(bars)
    if not touches:
        return None
    best_run = run = []
    for k in sorted(touches):
        if touches[k] == 1:
            run = run + [k] if run and k == run[-1] + 1 else [k]
        else:
            run = []
        if len(run) > len(best_run):
            best_run = run
    if not best_run:
        return None
    mid_bin = (best_run[0] + best_run[-1]) / 2
    return (mid_bin + 0.5) * step


def _poor_extreme(bars):
    touches, step = _bins(bars)
    hi_bin = int(max(x.h for x in bars) // step)
    lo_bin = int(min(x.l for x in bars) // step)
    return touches.get(hi_bin, 0) > 1, touches.get(lo_bin, 0) > 1


def single_print_fill(s):
    p = s.prior
    if p is None:
        return
    level = _single_print_zone(p.bars)
    if level is None:
        return
    b = s.bars
    for i in range(len(b)):
        if b[i].m >= 900:
            return
        if b[i].l <= level <= b[i].h:
            if b[i].c > level:
                yield i, 1
            elif b[i].c < level:
                yield i, -1
            return


def poor_high_low_break(s):
    p = s.prior
    if p is None:
        return
    poor_hi, poor_lo = _poor_extreme(p.bars)
    if not poor_hi and not poor_lo:
        return
    b = s.bars
    fired_hi = fired_lo = False
    for i in range(len(b)):
        if b[i].m >= 900:
            return
        if poor_hi and not fired_hi and b[i].c > p.hi:
            fired_hi = True
            yield i, 1
        if poor_lo and not fired_lo and b[i].c < p.lo:
            fired_lo = True
            yield i, -1


SETUPS = [
    dict(id='single_print_fill', name="Fill through yesterday's single-print zone", family='volume profile',
         detect=single_print_fill,
         rules="Yesterday's widest price bin touched by only one 5-minute bar (a thin, fast passage) is the "
               "single-print zone. The first bar today that trades into it and closes back out the side it "
               "entered from leans WITH that close (continuation through the thin spot), before 15:00."),
    dict(id='poor_high_low_break', name="Break of yesterday's poor high/low", family='volume profile',
         detect=poor_high_low_break,
         rules="If yesterday's session high (low) bin was touched by more than one 5-minute bar, the auction "
               "didn't reject it cleanly (a poor high/low, unfinished business). The first close today beyond "
               "that poor high (low) leans WITH the break, before 15:00. A clean (single-touch) high/low is "
               "left untested by this setup."),
]
