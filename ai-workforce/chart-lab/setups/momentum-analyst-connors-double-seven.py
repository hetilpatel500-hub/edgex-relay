"""Connors Double 7 entry on daily bars.
Added 2026-10-04 by momentum-analyst: the research queue held only tape items, so this run took the documented
Larry Connors / Cesar Alvarez "Double 7" rule found by WebSearch (quantifiedstrategies.substack.com, strategyquant.com):
close above the 200-day average and at or below the lowest close of the last 7 bars, buy weakness in an uptrend.
Rules were fixed BEFORE any P&L was seen: 7 bars, SMA200, mirrored for shorts. The published exit (highest close of
7 bars) is not available in the lab, so the entry is judged with the lab's standard exits. Distinct from
d_rsi2_pullback (RSI threshold, not a rolling closing low) and streak_exhaustion (intraday).
"""


def connors_double_seven(ser):
    """Close above SMA200 and at or below the lowest close of the last 7 days (including today) leans long;
    close below SMA200 and at or above the highest close of the last 7 days leans short."""
    for i in range(200, len(ser.c)):
        m = ser.sma200[i]
        if m is None:
            continue
        w = ser.c[i - 6:i + 1]
        if ser.c[i] > m and ser.c[i] <= min(w):
            yield i, 1
        elif ser.c[i] < m and ser.c[i] >= max(w):
            yield i, -1


SETUPS = [
    dict(id='d_connors_double_seven', tf='D', name='Connors Double 7 (7-day closing low in an uptrend)',
         family='mean reversion (daily)', detect=connors_double_seven,
         rules="Close above the 200-day average and at or below the lowest close of the last 7 days leans long "
               "at the next open (mirrored below the 200-day average at a 7-day closing high). Tested with and "
               "against, with the lab's standard exits rather than the published highest-close exit."),
]
