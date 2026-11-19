"""Yesterday's peak-volume bar: first-touch hold of its high or low.
Added 2026-10-07 by volume-vwap-analyst, from a WebSearch run (TradingView
"HVC + levels" / LuxAlgo "Intraday Volume Swings": the high/low of the
highest-volume candle is projected forward as a support/resistance zone).
Distinct from prior_hvn_secondary and prior_lvn_rejection, which read the
price-binned profile; this reads the single heaviest 5-minute bar.
Parameters fixed BEFORE any P&L was seen: the heaviest 5-minute bar of the
prior session defines [L, H]; ignore it if H-L < 0.3 ATR. Between 09:45 and
13:55 ET, the first bar that comes from above (previous bar's low > H) and
trades down to H or lower but closes back above H signals long; from below
(previous bar's high < L), a bar that trades up to L or higher but closes
below L signals short. A close through the level on the wrong side first
cancels the day. One per session.
"""


def prior_peak_bar_hold(s):
    p = s.prior
    if p is None:
        return
    k = max(range(len(p.bars)), key=lambda j: p.bars[j].v)
    H, L = p.bars[k].h, p.bars[k].l
    b = s.bars
    for i in range(3, len(b)):
        if b[i].m >= 835:
            return
        if H - L < 0.3 * s.atr[i]:
            return
        if b[i].m < 585:
            continue
        if b[i - 1].l > H and b[i].l <= H:
            if b[i].c > H:
                yield i, 1
            return
        if b[i - 1].h < L and b[i].h >= L:
            if b[i].c < L:
                yield i, -1
            return


SETUPS = [
    dict(id='prior_peak_bar_hold', name="Yesterday's peak-volume bar: first-touch hold", family='volume profile',
         detect=prior_peak_bar_hold,
         rules="Take yesterday's single highest-volume 5-minute bar. Between 09:45 and 13:55 ET, the first time "
               "price comes down from above and dips to the bar's high but closes back above it, it leans long; "
               "the first time it comes up from below to the bar's low and closes back under, it leans short. "
               "Skipped when the bar is narrower than 0.3 ATR. One signal per session; tested with and against."),
]
