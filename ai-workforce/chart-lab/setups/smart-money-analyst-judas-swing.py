"""ICT Judas swing at the New York cash open, on 5-minute bars.
Added 2026-10-01 by smart-money-analyst: the research queue is fully coded, so
this run used WebSearch (theinnercircletraders.com, tradingfinder.com,
innercircletrader.net) for an untested session-open idea. The false first move
away from the open that then closes back through the open price.
"""


def judas_swing(s):
    """Within the first 60 minutes, price trades at least 0.5 ATR beyond the
    session open on one side (the false move), then a 5-minute bar closes back
    through the open on the other side. Leans in the direction of that close
    (false move down, close back above the open = long). One signal per session."""
    b = s.bars
    o = s.open
    ext_dn = ext_up = False
    for i in range(1, len(b)):
        if b[i].m >= 630:  # 10:30 ET
            return
        atr = s.atr[i - 1] if i >= 1 else None
        if not atr:
            continue
        ext_dn = ext_dn or b[i - 1].l <= o - 0.5 * atr
        ext_up = ext_up or b[i - 1].h >= o + 0.5 * atr
        if ext_dn and not ext_up and b[i].c > o:
            yield i, 1
            return
        if ext_up and not ext_dn and b[i].c < o:
            yield i, -1
            return


SETUPS = [
    dict(id='judas_swing', name='Judas swing: false open move, close back through the open', family='smart money',
         detect=judas_swing,
         rules="In the first hour, price pushes at least 0.5 ATR to one side of the day's opening price and "
               "never the other way, then a 5-minute bar closes back through the open. A false move down that "
               "closes back above the open leans long; a false move up that closes back below leans short."),
]
