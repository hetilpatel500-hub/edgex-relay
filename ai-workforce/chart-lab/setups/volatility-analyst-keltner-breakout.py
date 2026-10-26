"""Keltner Channel breakout on 5-minute bars.
Added 2026-09-28 by volatility-analyst: research queue in
ai-workforce/chart-lab/README.md is exhausted for non-tape lines (every
other line already has a coded, backtested setup -- README.md's checkboxes
were never ticked after that work, confirmed against PLAYBOOK.md and
setups/), and the "waiting for tape" order-flow lines stay blocked
(tape/ holds 0 sessions). This run used WebSearch for a documented,
untested technique for volatility-analyst's own family: the Keltner
Channel breakout, an ATR-banded channel distinct from the Bollinger
squeeze already tested (std-dev bands around an SMA) -- Keltner bands an
EMA with a multiple of ATR instead. Per
https://howtotrade.com/trading-strategies/keltner-channels/ and
https://www.quantifiedstrategies.com/keltner-bands-trading-strategies/,
the classic construction is EMA(20) as the midline with upper/lower bands
at midline +/- 2x ATR(14), and the breakout read is: a close beyond the
upper band, from inside the channel, confirms upward continuation (mirror
for the lower band).
"""


def _ema(closes, n):
    k = 2 / (n + 1)
    out, prev = [], None
    for c in closes:
        prev = c if prev is None else c * k + prev * (1 - k)
        out.append(prev)
    return out


def keltner_breakout(s):
    """Keltner Channel: EMA(20) of 5-minute closes as the midline, bands at
    midline +/- 2x the session's own ATR(14) (core.Session.atr). The first
    bar whose close breaks above the upper band, with the prior bar's close
    still inside the channel, leans long; the mirror break below the lower
    band leans short. One signal per side per session, before 15:00, after
    a 20-bar EMA warmup."""
    b = s.bars
    closes = [x.c for x in b]
    ema20 = _ema(closes, 20)
    fired_long = fired_short = False
    for i in range(20, len(b)):
        if b[i].m >= 900:
            break
        upper, lower = ema20[i] + 2 * s.atr[i], ema20[i] - 2 * s.atr[i]
        prev_upper, prev_lower = ema20[i - 1] + 2 * s.atr[i - 1], ema20[i - 1] - 2 * s.atr[i - 1]
        if not fired_long and b[i - 1].c <= prev_upper and b[i].c > upper:
            fired_long = True
            yield i, 1
        if not fired_short and b[i - 1].c >= prev_lower and b[i].c < lower:
            fired_short = True
            yield i, -1


SETUPS = [
    dict(id='keltner_breakout', name='Keltner Channel breakout', family='volatility',
         detect=keltner_breakout,
         rules="Keltner Channel: EMA(20) midline, bands at +/- 2x ATR(14). The first close above the upper "
               "band (from inside the channel) leans long; the first close below the lower band leans short. "
               "One signal per side per session, before 15:00, after a 20-bar warmup."),
]
