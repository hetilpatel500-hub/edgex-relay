"""Bull/bear flag after a 2-ATR impulse.
Added 2026-09-28 by pattern-specialist: next open line of the research queue
in ai-workforce/chart-lab/README.md ("Bull/bear flag after a 2-ATR
impulse"). A sharp impulse leg (net move over the last 4 bars >= 2x that
bar's ATR) is followed by a flag: up to 8 bars whose own range stays within
60% of the impulse bars' average range (the pause tightens) and that never
retrace more than 50% of the impulse. The first close beyond the flag's own
high (low), in the impulse's direction, confirms the breakout.
"""


def bull_bear_flag(s):
    b = s.bars
    n = len(b)
    W = 4
    fired = 0
    in_flag = False
    i = W
    while i < n:
        if b[i].m >= 900 or fired >= 2:
            break
        if not in_flag:
            atr = s.atr[i]
            if atr:
                move = b[i].c - b[i - W].o
                if abs(move) >= 2 * atr:
                    impulse = b[i - W:i + 1]
                    avg_rng = sum(x.h - x.l for x in impulse) / len(impulse)
                    if avg_rng > 0:
                        in_flag = True
                        impulse_d = 1 if move > 0 else -1
                        impulse_move, impulse_close = abs(move), b[i].c
                        flag_hi, flag_lo, flag_len = b[i].h, b[i].l, 0
            i += 1
            continue
        flag_len += 1
        x = b[i]
        if flag_len > 8 or x.m >= 900:
            in_flag = False
            continue
        if impulse_d == 1 and x.c > flag_hi:
            fired += 1; yield i, 1
            in_flag = False
            i += 1
            continue
        if impulse_d == -1 and x.c < flag_lo:
            fired += 1; yield i, -1
            in_flag = False
            i += 1
            continue
        if (x.h - x.l) > 0.6 * avg_rng:
            in_flag = False
            continue
        new_hi, new_lo = max(flag_hi, x.h), min(flag_lo, x.l)
        retr = (impulse_close - new_lo) if impulse_d == 1 else (new_hi - impulse_close)
        if retr > 0.5 * impulse_move:
            in_flag = False
            continue
        flag_hi, flag_lo = new_hi, new_lo
        i += 1


SETUPS = [
    dict(id='bull_bear_flag', name='Bull/bear flag after a 2-ATR impulse', family='pattern',
         detect=bull_bear_flag,
         rules="A net move over the last 4 bars of at least 2x that bar's ATR marks an impulse. The following "
               "bars form a flag as long as each one's own range stays within 60% of the impulse bars' average "
               "range and the pullback never exceeds 50% of the impulse, for up to 8 bars. The first close "
               "beyond the flag's own high (low) confirms the breakout in the impulse's direction."),
]
