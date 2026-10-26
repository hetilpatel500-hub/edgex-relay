"""STARC band tag that closes back inside, 5-minute bars.
Added 2026-10-12 by volatility-analyst via WebSearch (Stoller Average Range Channel bands as described by LuxAlgo,
WealthCharts and OneOption: SMA plus/minus a multiple of ATR; a single tag that closes back inside the band argues for
rotation toward the centerline). Sources give no intraday rules, so parameters were fixed BEFORE any P&L was seen from
the common published form: SMA length 6, multiplier 2, ATR(14) of 5-minute bars (the session's carried ATR). A bar whose
high pierces the upper band but closes back below it leans short; the mirror leans long. Between 10:00 and 14:30 ET,
at most two signals per session, and the pierce must not be the second consecutive pierce bar (band-hugging runs are skipped).
"""

N, K = 6, 2.0


def starc_reversal(s):
    b = s.bars
    fired = 0
    prev_tag = 0
    for i in range(N, len(b) - 1):
        sma = sum(x.c for x in b[i - N + 1:i + 1]) / N
        up, dn = sma + K * s.atr[i], sma - K * s.atr[i]
        tag = 1 if b[i].h > up else -1 if b[i].l < dn else 0
        ok_time = 600 <= b[i].m <= 870
        if tag == 1 and b[i].c < up and prev_tag != 1 and ok_time and fired < 2:
            fired += 1
            yield i, -1
        elif tag == -1 and b[i].c > dn and prev_tag != -1 and ok_time and fired < 2:
            fired += 1
            yield i, 1
        prev_tag = tag


SETUPS = [
    dict(id='starc_band_reversal', name='STARC band tag closing back inside', family='volatility',
         detect=starc_reversal,
         rules="Bands sit 2 ATR above and below the 6-bar average close. A 5-minute bar that pokes through the upper "
               "band but closes back inside leans short (the mirror at the lower band leans long), between 10:00 and "
               "14:30, if the previous bar did not also tag that band. At most two signals per session; tested with "
               "and against."),
]
