"""On-balance volume divergence at a new session extreme.
Added 2026-10-10 by volume-vwap-analyst via WebSearch (queue was fully coded; sources: StockSharp OBV Divergence
strategy for 5-minute candles, luxalgo.com OBV Divergence concept, crosstrade.io OBV guide). The lab had no OBV
setup. Nothing tuned: OBV restarts each session (close up = +volume, close down = -volume); a new session low whose
OBV is higher than OBV at the previous session low (at least 6 bars earlier) is bullish divergence, mirrored for
highs. Fires on the first such bar between 10:30 and 14:30 ET that also closes in the direction of the reversal
(up bar for a low, down bar for a high), as the sources advise waiting for price confirmation; one per session.
"""


def obv_divergence_extreme(s):
    b = s.bars
    obv = [0.0]
    for i in range(1, len(b)):
        sg = 1 if b[i].c > b[i - 1].c else (-1 if b[i].c < b[i - 1].c else 0)
        obv.append(obv[-1] + sg * b[i].v)
    lo_i = hi_i = 0
    for i in range(1, len(b) - 1):
        new_lo = b[i].l < b[lo_i].l
        new_hi = b[i].h > b[hi_i].h
        d = 0
        if 600 <= b[i].m <= 870:
            if new_lo and i - lo_i >= 6 and obv[i] > obv[lo_i] and b[i].c > b[i].o:
                d = 1
            elif new_hi and i - hi_i >= 6 and obv[i] < obv[hi_i] and b[i].c < b[i].o:
                d = -1
        if new_lo:
            lo_i = i
        if new_hi:
            hi_i = i
        if d:
            yield i, d
            return


SETUPS = [
    dict(id='obv_divergence_extreme', name='OBV divergence at a new session extreme', family='volume',
         detect=obv_divergence_extreme,
         rules="A new session low whose on-balance volume (restarted each session) is higher than at the previous "
               "session low, 6+ bars earlier, and that closes as an up bar leans long; a new session high with lower "
               "OBV than at the previous high that closes as a down bar leans short. 10:30-14:30 ET, one signal per "
               "session; tested with and against."),
]
