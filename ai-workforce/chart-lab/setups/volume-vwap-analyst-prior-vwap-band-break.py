"""Prior-day VWAP band break on above-average volume.
Added 2026-10-15 by volume-vwap-analyst, from a WebSearch of a TradingView "value area breakout"
script that treats the prior day's VWAP +/- 1 standard deviation as value. Parameters fixed BEFORE any
P&L was seen: the band is yesterday's final session VWAP +/- 1 volume-weighted stdev; the signal is the
first bar between 10:00 and 14:30 that closes beyond a band while the previous bar closed inside it,
with relative volume (same time slot, 20-session average) at least 1.2. One signal per session. The lab
tests it with and against ("against" = failed-breakout fade).
"""


def prior_vwap_band_break(s):
    p = s.prior
    if p is None or not p.vwap or not p.vsd[-1]:
        return
    mid, sd = p.vwap[-1], p.vsd[-1]
    hi, lo = mid + sd, mid - sd
    b = s.bars
    for i in range(1, len(b) - 1):
        if b[i].m < 600 or b[i].m + 5 > 870:
            continue
        r = s.rvol[i]
        if r is None or r < 1.2:
            continue
        if b[i].c > hi and b[i - 1].c <= hi:
            yield i, 1
            return
        if b[i].c < lo and b[i - 1].c >= lo:
            yield i, -1
            return


SETUPS = [
    dict(id='prior_vwap_band_break', name="Break of yesterday's VWAP +/-1 stdev band on volume", family='volume profile',
         detect=prior_vwap_band_break,
         rules="Yesterday's session VWAP plus and minus one volume-weighted standard deviation is treated as "
               "value. The first bar between 10:00 and 14:30 that closes outside the band (previous bar "
               "inside) on at least 1.2x its usual volume for that time of day leans in the break direction. "
               "Once per session, tested with and against."),
]
