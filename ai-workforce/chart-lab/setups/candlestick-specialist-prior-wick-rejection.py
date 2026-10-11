"""Yesterday's wick zone: first-touch rejection of the prior day's body edge.
Added 2026-10-07 by candlestick-specialist via the lab queue, from a WebSearch run (TradingView "wick rejected"
day-statistics definition: a day opens inside yesterday's range, trades up into yesterday's upper wick, never
reaches yesterday's high and closes back under the top of the body). The source is an indicator definition, not a
tested rule. Distinct from prior_range_tag and pd_acceptance, which read the prior high/low, not the body edge.
Parameters fixed BEFORE any P&L was seen: prior day's body is [B, T] = [min, max] of its first open and its close.
Only used when today opens inside the prior [low, high]. The upper wick zone is [T, prior high], the lower wick
zone [prior low, B]; a zone counts only if at least 0.5 ATR tall. Between 09:45 and 14:00 ET, the first bar
that comes from below (previous high < T) and reaches T or higher without trading at the prior high, then closes
back below T, signals short; the mirror at B (previous low > B, reaches B, stays above the prior low, closes
back above B) signals long. Touching the prior high/low first cancels that side. One per side per session.
"""


def prior_wick_rejection(s):
    p = s.prior
    if p is None:
        return
    b = s.bars
    ph, pl = p.hi, p.lo
    if not (pl < s.open < ph):
        return
    T, B = max(p.bars[0].o, p.close), min(p.bars[0].o, p.close)
    done_up = done_dn = False
    for i in range(1, len(b)):
        if b[i].m >= 840:
            return
        if b[i].h >= ph:
            done_up = True
        if b[i].l <= pl:
            done_dn = True
        if b[i].m < 585:
            continue
        a = s.atr[i]
        if not done_up and ph - T >= 0.5 * a and b[i - 1].h < T <= b[i].h and b[i].c < T:
            done_up = True
            yield i, -1
        elif not done_dn and B - pl >= 0.5 * a and b[i - 1].l > B >= b[i].l and b[i].c > B:
            done_dn = True
            yield i, 1
        if done_up and done_dn:
            return


SETUPS = [
    dict(id='prior_wick_rejection', name="Yesterday's wick zone: body-edge rejection", family='candlestick',
         detect=prior_wick_rejection,
         rules="On a day that opens inside yesterday's range, the first time price rises into yesterday's upper "
               "wick (reaches the top of yesterday's candle body without trading at yesterday's high) and closes "
               "back under that body edge it leans short; the mirror at the bottom of the body leans long. "
               "Wick zones under 0.5 ATR are skipped; 09:45-14:00 ET; one signal per side per session; "
               "tested with and against."),
]
