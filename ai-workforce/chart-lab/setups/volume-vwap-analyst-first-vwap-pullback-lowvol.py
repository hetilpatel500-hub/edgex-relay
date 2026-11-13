"""First low-volume pullback to VWAP after a 30-minute one-sided run.
Added 2026-10-07 by volume-vwap-analyst from the "first pullback to VWAP in a trending stock" write-up found via
WebSearch (daytradingtoolkit.com). Distinct from vwap_bounce (wick + drift test), vwap_second_touch and
volume_dryup_pullback (never touches VWAP).
Parameters fixed BEFORE any P&L was seen: at least 6 consecutive closes on one side of VWAP, then the first bar
whose close is within 0.1% of VWAP or whose range touches it (before that, no touch since the run began); the
average volume of the pullback bars (from the run's last extreme) is below the average volume of the run bars;
signal bar closes back on the trend side with a candle in the trend direction (close > open for longs).
Window 10:00-14:30; one signal per side per session.
"""


def first_vwap_pullback_lowvol(s):
    b = s.bars
    done = set()
    run_start, side = None, 0
    for i in range(len(b)):
        if b[i].m >= 870:
            break
        c, w = b[i].c, s.vwap[i]
        sd = 1 if c > w else (-1 if c < w else 0)
        if run_start is not None and side != 0:
            touched = (b[i].l <= w <= b[i].h) or abs(c - w) <= 0.001 * w
            if touched and i - run_start >= 6 and b[i].m >= 600 and side not in done:
                ext = max(range(run_start, i), key=lambda k: b[k].h) if side == 1 else \
                    min(range(run_start, i), key=lambda k: b[k].l)
                run_v = [b[k].v for k in range(run_start, ext + 1)]
                pb_v = [b[k].v for k in range(ext + 1, i + 1)]
                trend_candle = (c > b[i].o and c > w) if side == 1 else (c < b[i].o and c < w)
                if run_v and pb_v and sum(pb_v) / len(pb_v) < sum(run_v) / len(run_v) and trend_candle:
                    done.add(side)
                    yield i, side
                run_start, side = None, 0
                if sd:
                    run_start, side = i, sd
                continue
            if touched:
                run_start, side = (i, sd) if sd else (None, 0)
                continue
        if sd != side:
            run_start, side = (i, sd) if sd else (None, 0)
        elif run_start is None and sd:
            run_start, side = i, sd


SETUPS = [
    dict(id='first_vwap_pullback_lowvol', name='First low-volume pullback to VWAP', family='vwap',
         detect=first_vwap_pullback_lowvol,
         rules="After at least six 5-minute closes on one side of VWAP, the first bar to touch VWAP (or close within "
               "0.1% of it) on lighter average volume than the run, closing back on the trend side in a trend-direction "
               "candle, leans with the run. 10:00 to 14:30, one per side per session; tested with and against."),
]
