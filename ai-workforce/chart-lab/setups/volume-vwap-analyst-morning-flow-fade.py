"""Morning move on weakening participation fades by 10:30.
Added 2026-10-06 by volume-vwap-analyst via WebSearch (Quantpedia, "Can Weakening Morning Order Flow
Predict SPY Reversals?": a morning move that loses participation tends to reverse). Bar volume stands in
for order flow because tape history is not deep enough yet. Distinct from volume_divergence_extreme (day
extreme, bar-to-bar) and heavy_volume_morning_trend (average rvol level, not its decay).
Parameters fixed BEFORE any P&L was seen: volume of 10:00-10:30 (bars 6-11) under 0.6x the volume of
9:30-10:00 (bars 0-5); the 10:25 bar close (bar 11) at least 0.5 ATR(5-min) from the session open;
signal at that close, one per session, fade the morning direction.
"""


def morning_flow_fade(s):
    b = s.bars
    if len(b) < 14:
        return
    v1 = sum(x.v for x in b[:6])
    v2 = sum(x.v for x in b[6:12])
    atr = s.atr[11]
    if not v1 or not atr or v2 >= 0.6 * v1:
        return
    d = b[11].c - s.open
    if d >= 0.5 * atr:
        yield 11, -1
    elif d <= -0.5 * atr:
        yield 11, 1


SETUPS = [
    dict(id='morning_flow_fade', name='Morning move on fading volume reverses', family='volume',
         detect=morning_flow_fade,
         rules="By 10:30 price is at least 0.5 ATR from the open, but the 10:00-10:30 half hour traded under 60% "
               "of the 9:30-10:00 volume: the push is losing participation, so the move leans back against the "
               "morning direction. One trade per session. Tested with and against."),
]
