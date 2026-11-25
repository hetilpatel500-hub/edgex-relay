"""McGinley Dynamic (10) close-cross with VWAP agreement, 5-minute bars.
Added 2026-10-12 by trend-moving-average-analyst via WebSearch (McGinley Dynamic: MD = MD1 + (P - MD1) / (N * (P / MD1)^4);
sources describe a close crossing the line as the signal and name N = 10 for intraday charts; confirmation is advised).
Not yet in the lab. Parameters fixed BEFORE any P&L was seen: N = 10, seeded with the session's first close (built inside
the session), signal when the close crosses the line and sits on the same side of VWAP, 10:30 to 14:30 ET,
at most 2 signals per side per session.
"""


def mcginley_cross(s):
    b = s.bars
    n = 10
    md = [b[0].c]
    for i in range(1, len(b)):
        p, m1 = b[i].c, md[-1]
        md.append(m1 + (p - m1) / (n * (p / m1) ** 4))
    cnt = {1: 0, -1: 0}
    for i in range(1, len(b)):
        if b[i].m < 630 or b[i].m >= 870:
            continue
        up = b[i].c > md[i] and b[i - 1].c <= md[i - 1]
        dn = b[i].c < md[i] and b[i - 1].c >= md[i - 1]
        if up and b[i].c > s.vwap[i] and cnt[1] < 2:
            cnt[1] += 1; yield i, 1
        elif dn and b[i].c < s.vwap[i] and cnt[-1] < 2:
            cnt[-1] += 1; yield i, -1


SETUPS = [
    dict(id='mcginley10_cross_vwap', name='McGinley Dynamic (10) cross with VWAP', family='trend',
         detect=mcginley_cross,
         rules="McGinley Dynamic line (10, seeded at the session's first close): a 5-minute close crossing above it "
               "with the close above VWAP leans long; crossing below it with the close below VWAP leans short. "
               "10:30 to 14:30 ET, at most two signals per side per session; tested with and against."),
]
