"""Simulated exits on real bars.

Conventions (shared by the backtester, the time machine and the journal):
  * stops and targets are checked bar by bar; if one bar touches both, the
    stop counts (the conservative assumption on 5-minute bars);
  * a bar that opens beyond the stop fills at its open (a gap through the
    stop), and one that opens beyond the target fills at its open too;
  * anything still open is closed at the session's last bar close;
  * a round-trip cost in basis points comes off every trade.
"""

EXITS = {
    '1atr/1.5atr': (1.0, 1.5),
    '1atr/2atr': (1.0, 2.0),
    '1.5atr/3atr': (1.5, 3.0),
    '1atr/close': (1.0, None),
    '2atr/close': (2.0, None),
    '2atr/4atr': (2.0, 4.0),
    '3atr/close': (3.0, None),
}

EXITS_D = {
    '2atr/hold5': (2.0, None, 5),
    '2atr/hold10': (2.0, None, 10),
    '1.5atr/3atr/hold10': (1.5, 3.0, 10),
    '1atr/2atr/hold5': (1.0, 2.0, 5),
}


def trade(s, i, d, stop_m, tgt_m, cost_bps):
    """The lab's intraday trade: enter at the open of bar i+1 in direction d;
    stop and target are multiples of the 5-minute ATR at bar i (the target is
    measured from entry, in ATRs); flat at the close. Returns R after costs."""
    b = s.bars
    if i + 1 >= len(b):
        return None
    e = b[i + 1].o
    risk = stop_m * s.atr[i]
    if risk <= 0:
        return None
    stop = e - d * risk
    tgt = e + d * tgt_m * s.atr[i] if tgt_m else None
    x = b[-1].c
    for k in range(i + 1, len(b)):
        y = b[k]
        if (y.l <= stop) if d == 1 else (y.h >= stop):
            x = stop; break
        if tgt is not None and ((y.h >= tgt) if d == 1 else (y.l <= tgt)):
            x = tgt; break
    cost = cost_bps / 1e4 * e
    return ((x - e) * d - cost) / risk


def trade_d(ser, i, d, stop_m, tgt_m, hold, cost_bps):
    """The lab's daily trade: enter at the next day's open; stop/target in
    daily ATRs; exit at the close of the hold-th day. Gaps through the stop
    fill at the open."""
    if i + 1 >= len(ser.c):
        return None
    e = ser.o[i + 1]
    risk = stop_m * ser.atr[i]
    stop = e - d * risk
    tgt = e + d * tgt_m * ser.atr[i] if tgt_m else None
    last = min(i + hold, len(ser.c) - 1)
    x = ser.c[last]
    for k in range(i + 1, last + 1):
        if d == 1 and ser.l[k] <= stop:
            x = min(stop, ser.o[k]) if k > i + 1 else stop; break
        if d == -1 and ser.h[k] >= stop:
            x = max(stop, ser.o[k]) if k > i + 1 else stop; break
        if tgt is not None and ((ser.h[k] >= tgt) if d == 1 else (ser.l[k] <= tgt)):
            x = tgt; break
    cost = cost_bps / 1e4 * e
    return ((x - e) * d - cost) / risk


def replay(bars, start, e, d, stop, tgt):
    """Walk real bars from index `start` for a position entered at price e.
    Returns dict(outcome='target'|'stop'|'close', exit, k, mfe, mae) where k is
    the index of the exit bar and mfe/mae are in price units (>= 0)."""
    mfe = mae = 0.0
    for k in range(start, len(bars)):
        y = bars[k]
        if d == 1:
            if y.o <= stop:
                return dict(outcome='stop', exit=y.o, k=k, mfe=mfe, mae=max(mae, e - y.o))
            if tgt is not None and y.o >= tgt:
                return dict(outcome='target', exit=y.o, k=k, mfe=max(mfe, y.o - e), mae=mae)
            if y.l <= stop:
                return dict(outcome='stop', exit=stop, k=k, mfe=max(mfe, y.h - e), mae=max(mae, e - stop))
            if tgt is not None and y.h >= tgt:
                return dict(outcome='target', exit=tgt, k=k, mfe=max(mfe, tgt - e), mae=max(mae, e - y.l))
            mfe, mae = max(mfe, y.h - e), max(mae, e - y.l)
        else:
            if y.o >= stop:
                return dict(outcome='stop', exit=y.o, k=k, mfe=mfe, mae=max(mae, y.o - e))
            if tgt is not None and y.o <= tgt:
                return dict(outcome='target', exit=y.o, k=k, mfe=max(mfe, e - y.o), mae=mae)
            if y.h >= stop:
                return dict(outcome='stop', exit=stop, k=k, mfe=max(mfe, e - y.l), mae=max(mae, stop - e))
            if tgt is not None and y.l <= tgt:
                return dict(outcome='target', exit=tgt, k=k, mfe=max(mfe, e - tgt), mae=max(mae, y.h - e))
            mfe, mae = max(mfe, e - y.l), max(mae, y.h - e)
    if start >= len(bars):
        return dict(outcome='open', exit=e, k=start - 1, mfe=0.0, mae=0.0)
    return dict(outcome='close', exit=bars[-1].c, k=len(bars) - 1, mfe=mfe, mae=mae)


def r_multiple(e, x, d, risk, cost_bps):
    return ((x - e) * d - cost_bps / 1e4 * e) / risk
