"""Gap that opens on thin volume tends to revert (unconfirmed gap).
Added 2026-10-06 by session-gap-specialist via WebSearch (documented SPY idea: overnight gaps typically revert
within the first 30 minutes; the open bar's volume tells whether anyone confirmed the gap). Distinct from
gap_first_bar_fail (waits for a price break of bar 1) and gap_fade_rvol (volume split on a different bar/slot).
Parameters fixed BEFORE any P&L was seen: gap = open vs prior close of at least 0.25%; first 5-minute bar's
relative volume below 0.8 and its close not beyond its open in the gap's direction by more than 0.2 ATR;
signal at the first bar's close (9:35), one per session, fade the gap.
"""


def thin_open_gap_revert(s):
    p = s.prior
    if p is None or not s.bars:
        return
    gap = s.open / p.close - 1
    if abs(gap) < 0.0025:
        return
    r = s.rvol[0]
    if r is None or r >= 0.8:
        return
    b0, atr = s.bars[0], s.atr[0]
    if not atr:
        return
    drift = (b0.c - b0.o) * (1 if gap > 0 else -1)
    if drift > 0.2 * atr:
        return
    yield 0, (-1 if gap > 0 else 1)


SETUPS = [
    dict(id='thin_open_gap_revert', name='Thin-volume opening gap reverts', family='gap', detect=thin_open_gap_revert,
         rules="The day opens at least 0.25% from yesterday's close, but the first 5-minute bar trades under 0.8x "
               "its usual volume and does not push on in the gap's direction (no more than 0.2 ATR). Nobody confirmed "
               "the gap, so the move leans back toward yesterday's close from the 9:35 bar, once per session. Tested with and against."),
]
