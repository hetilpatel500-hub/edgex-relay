"""Quiet lunch-hour drift away from VWAP reverts into the afternoon.
Added 2026-10-06 by volume-vwap-analyst via WebSearch (VWAP mean-reversion write-ups: a deviation from VWAP
on thin participation is noise rather than conviction, so it tends to pull back). Distinct from
vwap_2sd_fading_volume (bar-level 2 sigma pierce) and vwap_cross_range_fade (IB fakeouts).
Parameters fixed BEFORE any P&L was seen: lunch = bars with start 11:30 to 13:25 ET (24 bars); average rvol of
the lunch bars under 0.8; the 13:25 bar close at least 1.0 ATR(5-min) from session VWAP; signal at that close,
one per session, lean back toward VWAP.
"""


def lunch_drift_vwap_revert(s):
    b = s.bars
    idx = [i for i, x in enumerate(b) if 690 <= x.m <= 805]
    if len(idx) < 24:
        return
    r = [s.rvol[i] for i in idx if s.rvol[i]]
    if len(r) < 24 or sum(r) / len(r) >= 0.8:
        return
    i = idx[-1]
    atr = s.atr[i]
    if not atr or i + 1 >= len(b):
        return
    dev = b[i].c - s.vwap[i]
    if dev >= atr:
        yield i, -1
    elif dev <= -atr:
        yield i, 1


SETUPS = [
    dict(id='lunch_drift_vwap_revert', name='Quiet lunch drift away from VWAP reverts', family='vwap',
         detect=lunch_drift_vwap_revert,
         rules="If the 11:30-13:30 lunch hours trade at under 80% of their usual volume and price at 13:30 sits at "
               "least 1 ATR away from VWAP, the drift lacks participation, so lean back toward VWAP. One trade "
               "per session. Tested with and against."),
]
