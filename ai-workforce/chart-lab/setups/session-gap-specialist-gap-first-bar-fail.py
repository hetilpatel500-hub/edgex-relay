"""Gap with first-bar failure (opening-bar break against the gap).
Added 2026-10-05 by session-gap-specialist via WebSearch (opening-bar reversal pattern as taught for gap days:
"gap up, then price trades below the first 5-minute bar's low" and the mirror). Distinct from oops_reversal
(needs a gap beyond the prior high/low and a return to the prior close) and gap_fade_rvol (volume-split fade from
the open): this one waits for the first bar's own extreme to break. Rules fixed BEFORE any P&L was seen:
gap = open vs prior close of at least 0.25%; first 5-minute close beyond the first bar's opposite extreme
(gap up: close below bar-1 low; gap down: close above bar-1 high) between 09:40 and 11:00; one signal per session.
"""


def gap_first_bar_fail(s):
    p = s.prior
    if p is None or not s.bars:
        return
    gap = s.open / p.close - 1
    if abs(gap) < 0.0025:
        return
    b0 = s.bars[0]
    for i, x in enumerate(s.bars):
        if i == 0:
            continue
        if x.m > 660:
            return
        if x.m < 580:
            continue
        if gap > 0 and x.c < b0.l:
            yield i, -1
            return
        if gap < 0 and x.c > b0.h:
            yield i, 1
            return


SETUPS = [
    dict(id='gap_first_bar_fail', name='Gap with first-bar failure', family='gap', detect=gap_first_bar_fail,
         rules="The day opens at least 0.25% away from yesterday's close. If it gapped up and a 5-minute bar closes "
               "below the first bar's low (gapped down: closes above its high) between 09:40 and 11:00, the gap is "
               "failing and the move leans against it, once per session. Tested with and against."),
]
