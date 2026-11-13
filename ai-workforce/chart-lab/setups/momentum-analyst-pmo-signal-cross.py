"""DecisionPoint Price Momentum Oscillator (PMO) signal cross with VWAP agreement, 5-minute bars.
Added 2026-10-13 by momentum-analyst via WebSearch (Carl Swenlin's PMO: 1-bar rate of change smoothed twice with a
custom EMA whose factor is 2/length, times 10; signal line = EMA of the PMO; a cross of the PMO over its signal line is
the buy/sell trigger per StockCharts/DecisionPoint and TradingView's help page. The search results did not restate the
35/20 lengths; they are the commonly published daily defaults, and no intraday evidence was found).
Parameters fixed BEFORE any P&L was seen: ROC = 100 * (close / prior close - 1), PMO = EMA(2/20) of 10 * EMA(2/35) of ROC,
signal = standard EMA(10) of the PMO, computed within the session from its second bar. Long at the close of the first bar
between 10:30 and 14:30 ET where the PMO crosses above its signal while PMO < 0 and the close is above session VWAP
(mirror for short with PMO > 0 and close below VWAP). One signal per session.
"""


def _ema_k(x, k):
    out, e = [], None
    for v in x:
        e = v if e is None else e + k * (v - e)
        out.append(e)
    return out


def pmo_signal_cross(s):
    b = s.bars
    roc = [0.0] + [100.0 * (b[i].c / b[i - 1].c - 1) if b[i - 1].c else 0.0 for i in range(1, len(b))]
    sm1 = [10 * v for v in _ema_k(roc, 2 / 35)]
    pmo = _ema_k(sm1, 2 / 20)
    sig = _ema_k(pmo, 2 / 11)
    for i in range(30, len(b) - 1):
        if b[i].m < 630 or b[i].m > 870:
            continue
        up = pmo[i] > sig[i] and pmo[i - 1] <= sig[i - 1]
        dn = pmo[i] < sig[i] and pmo[i - 1] >= sig[i - 1]
        if up and pmo[i] < 0 and b[i].c > s.vwap[i]:
            yield i, 1
            return
        if dn and pmo[i] > 0 and b[i].c < s.vwap[i]:
            yield i, -1
            return


SETUPS = [
    dict(id='pmo_signal_cross', name='Price Momentum Oscillator (35/20/10) signal cross with VWAP', family='momentum',
         detect=pmo_signal_cross,
         rules="Swenlin's Price Momentum Oscillator is a rate of change smoothed twice. Between 10:30 and 14:30, when "
               "it crosses above its 10-bar signal line while still below zero and price closes above VWAP, it leans "
               "long; the mirror (cross down while above zero, price under VWAP) leans short. One signal per "
               "session; tested with and against."),
]
