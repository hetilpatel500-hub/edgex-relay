"""Opening range breakout confirmed by VWAP side and 5-minute RSI.
Added 2026-10-06 by session-gap-specialist: the queue is fully coded, so this
run used WebSearch (documented ORB variant: breakout of the 15-minute range
only when price is on the right side of the session VWAP and a momentum
oscillator agrees). Distinct from orb15 (no filter) and orb_vwap_slope (VWAP
slope, no RSI).
"""


def _rsi(closes, n):
    gain = loss = 0.0
    for k in range(1, n + 1):
        d = closes[k] - closes[k - 1]
        gain += max(d, 0); loss += max(-d, 0)
    gain /= n; loss /= n
    for k in range(n + 1, len(closes)):
        d = closes[k] - closes[k - 1]
        gain = (gain * (n - 1) + max(d, 0)) / n
        loss = (loss * (n - 1) + max(-d, 0)) / n
    if loss == 0:
        return 100.0
    return 100 - 100 / (1 + gain / loss)


def orb_vwap_rsi_confirm(s):
    """From 10:15 to 11:30, a 5-minute close beyond the 9:30-9:45 range that
    is also on the same side of session VWAP, with RSI(9) of the session's
    closes at 60 or above (long) or 40 or below (short). First qualifying bar
    only, one signal per session."""
    b = s.bars
    closes = [x.c for x in b]
    for i in range(9, len(b)):
        if b[i].m >= 690:
            return
        c = closes[i]
        up = c > s.or_hi and c > s.vwap[i]
        dn = c < s.or_lo and c < s.vwap[i]
        if not (up or dn):
            continue
        r = _rsi(closes[:i + 1], 9)
        if up and r >= 60:
            yield i, 1
            return
        if dn and r <= 40:
            yield i, -1
            return


SETUPS = [
    dict(id='orb_vwap_rsi_confirm', name='Opening range break with VWAP and RSI agreement', family='opening range',
         detect=orb_vwap_rsi_confirm,
         rules="From 10:15 to 11:30, a 5-minute close above the 9:30-9:45 range high, above session VWAP, with "
               "RSI(9) of the session's closes at 60 or more leans long; a close below the range low and VWAP "
               "with RSI(9) at 40 or less leans short. One trade per session."),
]
