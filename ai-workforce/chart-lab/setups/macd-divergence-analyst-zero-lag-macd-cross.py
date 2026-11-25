"""Zero-Lag MACD (ZLEMA 12/26, signal EMA 9) signal-line cross with VWAP agreement, 5-minute bars.
Added 2026-10-14 by macd-divergence-analyst via WebSearch (ZLEMA by Ehlers and Way, TASC 2010: de-lagged input 2*close - close[lag],
lag=(N-1)/2, then an EMA; LuxAlgo and TradingView scripts describe a zero-lag MACD built from it, one public 5-minute strategy
combines it with Kijun-sen and Ease of Movement; none gives an out-of-sample result).
Rules fixed BEFORE any P&L was seen: fast 12, slow 26, signal 9 (plain EMA of the MACD line), series restarts each session,
signal on the close where the MACD line crosses its signal line (up = long, down = short) with the close on the same side
of VWAP, 10:30 to 14:30 ET (needs 26 bars to settle), at most 2 signals per side per session.
"""

FAST, SLOW, SIG = 12, 26, 9


def _zlema(x, n):
    lag = (n - 1) // 2
    k = 2.0 / (n + 1)
    out = []
    for i, v in enumerate(x):
        d = 2 * v - x[i - lag] if i >= lag else v
        out.append(d if not out else out[-1] + k * (d - out[-1]))
    return out


def zl_macd_cross(s):
    b = s.bars
    n = len(b)
    c = [x.c for x in b]
    f, sl = _zlema(c, FAST), _zlema(c, SLOW)
    m = [f[i] - sl[i] for i in range(n)]
    k = 2.0 / (SIG + 1)
    sg = []
    for v in m:
        sg.append(v if not sg else sg[-1] + k * (v - sg[-1]))
    cnt = {1: 0, -1: 0}
    for i in range(SLOW + 1, n):
        if b[i].m < 630 or b[i].m + 5 > 870:
            continue
        up = m[i] > sg[i] and m[i - 1] <= sg[i - 1]
        dn = m[i] < sg[i] and m[i - 1] >= sg[i - 1]
        if up and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='zl_macd_cross_vwap', name='Zero-Lag MACD (12/26/9) signal cross with VWAP', family='momentum',
         detect=zl_macd_cross,
         rules="MACD built from zero-lag EMAs (12 and 26, each fed 2*close minus the close half a period ago), "
               "restarted each session: the MACD line crossing above its 9-bar signal line with the close above VWAP "
               "leans long; crossing below with the close below VWAP leans short. 10:30 to 14:30 ET, at most two "
               "signals per side per session; tested with and against."),
]
