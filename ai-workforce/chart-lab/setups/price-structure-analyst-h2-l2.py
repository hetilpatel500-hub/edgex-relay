"""Second-entry pullback (H2 / L2) in a trend, Al Brooks style price action.
Added 2026-09-29 by price-structure-analyst: the research queue's lines are all coded, so this
run used WebSearch for a documented untested idea (Brooks "high 2 / low 2": the second attempt
to resume the trend after a two-legged pullback). Parameters were fixed before any P&L was seen.
"""


def h2_l2(s):
    """Uptrend: close above VWAP, VWAP higher than 6 bars ago, and a new session high within
    the last 24 bars. After that high, the pullback must reach 0.5-2.5 ATR deep and never
    close below VWAP. Each bar whose high exceeds the prior bar's high, right after a bar that
    made a lower high, is one attempt (H1, H2). The bullish bar (close > open) that is the
    second attempt fires long. Downtrend mirrors (L2). One signal per direction per session,
    between bar 12 and 15:00 ET."""
    b = s.bars
    n = len(b)
    for d in (1, -1):
        hi_i = None
        cnt = 0
        done = False
        for i in range(12, n):
            if done or b[i].m >= 900:
                break
            atr = s.atr[i]
            if not atr:
                continue
            ext = [x.h for x in b[:i]] if d == 1 else [x.l for x in b[:i]]
            best = max(ext) if d == 1 else min(ext)
            # bar index of the session extreme so far
            ei = max(k for k in range(i) if (b[k].h if d == 1 else b[k].l) == best)
            trend = (b[i].c - s.vwap[i]) * d > 0 and (s.vwap[i] - s.vwap[i - 6]) * d > 0
            if not trend or i - ei > 24 or i - ei < 3:
                cnt = 0
                continue
            seg = b[ei + 1:i + 1]
            if d == 1:
                depth = b[ei].h - min(x.l for x in seg)
                broke = any(b[k].c < s.vwap[k] for k in range(ei + 1, i + 1))
            else:
                depth = max(x.h for x in seg) - b[ei].l
                broke = any(b[k].c > s.vwap[k] for k in range(ei + 1, i + 1))
            if broke or depth > 2.5 * atr:
                cnt = 0
                continue
            attempt = (b[i].h > b[i - 1].h and b[i - 1].h < b[i - 2].h) if d == 1 else \
                      (b[i].l < b[i - 1].l and b[i - 1].l > b[i - 2].l)
            if attempt and depth >= 0.5 * atr:
                cnt += 1
                if cnt == 2 and (b[i].c - b[i].o) * d > 0:
                    done = True
                    yield i, d


SETUPS = [
    dict(id='h2_l2_pullback', name='Second-entry pullback (H2 / L2)', family='price action', detect=h2_l2,
         rules="In an uptrend above a rising VWAP, after a new session high, wait for a pullback of 0.5-2.5 ATR that "
               "never closes under VWAP. The second bar that pokes above the prior bar's high (after a lower-high bar) and "
               "closes up is the H2 and leans long; the mirror below VWAP is the L2 and leans short, before 15:00."),
]
