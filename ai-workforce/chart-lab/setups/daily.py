"""Seed daily setups. detect(ser) yields (i, d) known at the close of day i."""


def donchian20(ser):
    for i in range(20, len(ser.c)):
        if ser.c[i] > max(ser.h[i - 20:i]):
            yield i, 1
        elif ser.c[i] < min(ser.l[i - 20:i]):
            yield i, -1


def rsi2_pullback(ser):
    for i in range(200, len(ser.c)):
        m, r = ser.sma200[i], ser.rsi2[i]
        if m is None or r is None:
            continue
        if ser.c[i] > m and r < 10:
            yield i, 1
        elif ser.c[i] < m and r > 90:
            yield i, -1


def nr7_break(ser):
    rng = [h - l for h, l in zip(ser.h, ser.l)]
    for j in range(8, len(ser.c)):
        k = j - 1
        if rng[k] == min(rng[k - 6:k + 1]):
            if ser.c[j] > ser.h[k]:
                yield j, 1
            elif ser.c[j] < ser.l[k]:
                yield j, -1


def inside_day_break(ser):
    for j in range(2, len(ser.c)):
        k = j - 1
        if ser.h[k] < ser.h[k - 1] and ser.l[k] > ser.l[k - 1]:
            if ser.c[j] > ser.h[k - 1]:
                yield j, 1
            elif ser.c[j] < ser.l[k - 1]:
                yield j, -1


SETUPS = [
    dict(id='d_donchian20', tf='D', name='20-day breakout', family='trend (daily)', detect=donchian20,
         rules='Daily close above the prior 20-day high (below the 20-day low).'),
    dict(id='d_rsi2_pullback', tf='D', name='RSI(2) pullback in trend', family='mean reversion (daily)', detect=rsi2_pullback,
         rules='Above the 200-day average with RSI(2) under 10 (or below it with RSI(2) over 90).'),
    dict(id='d_nr7_break', tf='D', name='NR7 breakout', family='volatility (daily)', detect=nr7_break,
         rules="Day after the narrowest range of the last 7 days closes beyond that day's range."),
    dict(id='d_inside_day_break', tf='D', name='Inside-day breakout', family='volatility (daily)', detect=inside_day_break,
         rules="Close beyond the mother bar's range the day after an inside day."),
]
