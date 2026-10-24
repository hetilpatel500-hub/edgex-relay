"""Intraday entry signals with explicit triggers, stops and a quality score.

Every signal reports one of:
  triggered    fired on a recent bar and has not been invalidated
  armed        conditions are in place; the trigger price is where to act
  forming      not enough session yet (e.g. opening range still building)
  invalidated  fired earlier but price has since broken the stop or the idea
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd

from . import indicators as ind
from .session import Session, rth, split_days


@dataclass
class Signal:
    name: str
    side: str
    status: str
    trigger: float
    stop: float
    when: str | None = None
    quality: int = 50
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    description: str = ""

    @property
    def risk(self) -> float:
        return abs(self.trigger - self.stop)

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("trigger", "stop"):
            d[k] = round(d[k], 4)
        d["risk"] = round(self.risk, 4)
        return d


@dataclass
class Context:
    bars: pd.DataFrame  # today's regular-session bars with vwap/ema columns
    interval: int
    session: Session
    prior_close: float | None
    daily_atr: float | None
    slot_avg_volume: np.ndarray  # typical volume per slot on prior days
    cum_rvol: float  # today's volume so far vs typical by this time
    regime: str | None = None

    @property
    def last(self) -> pd.Series:
        return self.bars.iloc[-1]

    def slot(self, ts) -> int:
        return self.session.slot_of(ts, self.interval)

    def bar_rvol(self, i: int) -> float:
        ts = self.bars.index[i]
        k = self.slot(ts)
        typical = self.slot_avg_volume[k] if 0 <= k < len(self.slot_avg_volume) else np.nan
        if not typical or np.isnan(typical):
            return float("nan")
        return float(self.bars["volume"].iloc[i] / typical)


def build_context(intra: pd.DataFrame, session: Session, interval: int, daily: pd.DataFrame | None = None,
                  today=None, regime: str | None = None) -> Context:
    reg = rth(intra, session)
    if len(reg) == 0:
        raise ValueError("no regular-session bars in the data")
    today = today or reg.index[-1].date()
    reg = reg[reg.index.date <= today]
    closes = reg["close"]
    e9, e20 = ind.ema(closes, 9), ind.ema(closes, 20)
    day = reg[reg.index.date == today].copy()
    if len(day) == 0:
        raise ValueError(f"no regular-session bars for {today} yet")
    vw = ind.vwap(day)
    day = day.join(vw)
    day["ema9"], day["ema20"] = e9.loc[day.index], e20.loc[day.index]
    S = session.n_slots(interval)
    hist = {d: g for d, g in split_days(reg).items() if d < today}
    vol = np.full((max(1, len(hist)), S), np.nan)
    for r, (d, g) in enumerate(sorted(hist.items())[-20:]):
        k = ((g.index.hour * 60 + g.index.minute - session.start_min) // interval).to_numpy()
        ok = (k >= 0) & (k < S)
        vol[r, k[ok]] = g["volume"].to_numpy()[ok]
    with np.errstate(all="ignore"):
        slot_avg = np.nanmean(vol, axis=0) if len(hist) else np.full(S, np.nan)
    k_now = session.slot_of(day.index[-1], interval)
    typical_cum = np.nansum(slot_avg[: k_now + 1]) if len(hist) else np.nan
    cum_rvol = float(day["volume"].sum() / typical_cum) if typical_cum and not np.isnan(typical_cum) else float("nan")
    prior_close = None
    if hist:
        prior_close = float(sorted(hist.items())[-1][1]["close"].iloc[-1])
    if daily is not None and len(daily):
        done = daily[daily.index.date < today]
        if len(done):
            prior_close = float(done["close"].iloc[-1])
    daily_atr = None
    if daily is not None and len(daily[daily.index.date < today]) >= 5:
        daily_atr = float(ind.atr(daily[daily.index.date < today], 14).iloc[-1])
    return Context(day, interval, session, prior_close, daily_atr, slot_avg, cum_rvol, regime)


# ---------------------------------------------------------------- helpers

def _when(ctx: Context, i: int) -> str:
    return ctx.bars.index[i].strftime("%H:%M")


def _first_cross(series: pd.Series, level: float | pd.Series, direction: int, start: int = 0) -> int | None:
    v = series.to_numpy()
    lv = level.to_numpy() if isinstance(level, pd.Series) else np.full(len(v), level)
    for i in range(max(1, start), len(v)):
        if direction * (v[i] - lv[i]) > 0 and direction * (v[i - 1] - lv[i - 1]) <= 0:
            return i
    return None


def _tick(price: float) -> float:
    return 0.01 if price >= 1 else 0.0001


# ---------------------------------------------------------------- signals

def opening_range(ctx: Context, minutes: int = 15) -> list[Signal]:
    b = ctx.bars
    mins = np.asarray(ctx.session.minute_of(b.index))
    in_or = mins < minutes
    if in_or.all():
        hi, lo = float(b["high"].max()), float(b["low"].min())
        return [Signal(f"ORB{minutes}", side, "forming", px, stop, None, 0,
                       description=f"{minutes}-minute opening range still building ({hi:.2f}-{lo:.2f})")
                for side, px, stop in (("long", hi, lo), ("short", lo, hi))]
    orh, orl = float(b["high"][in_or].max()), float(b["low"][in_or].min())
    mid = (orh + orl) / 2
    wide = ctx.daily_atr and (orh - orl) > 0.5 * ctx.daily_atr
    out = []
    after = int(np.argmin(in_or))  # first bar after the range
    for side, level, d in (("long", orh, 1), ("short", orl, -1)):
        stop = mid if wide else (orl if d > 0 else orh)
        i = _first_cross(b["close"], level, d, start=after)
        desc = f"{minutes}-min opening range {orl:.2f}-{orh:.2f}" + (" (wide: stop at midpoint)" if wide else "")
        if i is None:
            out.append(Signal(f"ORB{minutes}", side, "armed", level + d * _tick(level), stop, None,
                              description=desc + f"; {'buy' if d > 0 else 'sell'} a close beyond {level:.2f}"))
            continue
        later = b["close"].iloc[i:]
        failed = (d * (later - mid) < 0).any() if not wide else (d * (later - stop) < 0).any()
        status = "invalidated" if failed else "triggered"
        out.append(Signal(f"ORB{minutes}", side, status, level, stop, _when(ctx, i),
                          description=desc + (f"; broke out at {_when(ctx, i)}" if not failed
                                              else f"; broke out at {_when(ctx, i)} then failed back into the range")))
        out[-1]._bar = i  # type: ignore[attr-defined]
    return out


def vwap_reclaim(ctx: Context, min_bars_away: int = 3, lookback: int = 4) -> list[Signal]:
    b = ctx.bars
    c, vw = b["close"].to_numpy(), b["vwap"].to_numpy()
    out = []
    for side, d in (("long", 1), ("short", -1)):
        name = "VWAP reclaim" if d > 0 else "VWAP rejection"
        above = d * (c - vw) > 0
        n = len(c)
        hit = None
        for i in range(max(min_bars_away, n - lookback), n):
            if above[i] and not above[i - min_bars_away : i].any():
                hit = i
                break
        if hit is not None:
            seg = b.iloc[max(0, hit - 8) : hit + 1]
            stop = float(seg["low"].min()) if d > 0 else float(seg["high"].max())
            still = above[hit:].all()
            out.append(Signal(name, side, "triggered" if still else "invalidated", float(vw[hit]), stop,
                              _when(ctx, hit),
                              description=f"closed back {'above' if d > 0 else 'below'} VWAP at {_when(ctx, hit)} "
                                          f"after {min_bars_away}+ bars on the other side"))
            out[-1]._bar = hit  # type: ignore[attr-defined]
        elif n >= min_bars_away and not above[-min_bars_away:].any():
            seg = b.iloc[-8:]
            stop = float(seg["low"].min()) if d > 0 else float(seg["high"].max())
            out.append(Signal(name, side, "armed", float(vw[-1]), stop, None,
                              description=f"price {'below' if d > 0 else 'above'} VWAP {float(vw[-1]):.2f}; "
                                          f"act on a close back {'above' if d > 0 else 'below'} it"))
    return out


def trend_pullback(ctx: Context) -> list[Signal]:
    b = ctx.bars
    if len(b) < 6:
        return []
    out = []
    last = b.iloc[-1]
    for side, d in (("long", 1), ("short", -1)):
        trend = d * (last["close"] - last["vwap"]) > 0 and d * (last["ema9"] - last["ema20"]) > 0
        if not trend:
            continue
        recent = b.iloc[-4:-1]
        touched = (d * (recent["low" if d > 0 else "high"] - recent["ema9"]) <= 0).any()
        held = (d * (recent["close"] - recent["ema20"]) >= 0).all()
        if not (touched and held):
            continue
        pb = b.iloc[-4:-1]
        trig = float(pb["high"].max()) if d > 0 else float(pb["low"].min())
        stop = float(pb["low"].min()) if d > 0 else float(pb["high"].max())
        fired = d * (last["close"] - trig) > 0
        out.append(Signal("Trend pullback", side, "triggered" if fired else "armed",
                          trig if fired else trig + d * _tick(trig), stop,
                          _when(ctx, len(b) - 1) if fired else None,
                          description=f"{'up' if d > 0 else 'down'}trend (VWAP + 9/20 EMA) pulled back to the 9 EMA; "
                                      f"{'broke' if fired else 'enter on a break of'} the pullback "
                                      f"{'high' if d > 0 else 'low'} {trig:.2f}"))
        if fired:
            out[-1]._bar = len(b) - 1  # type: ignore[attr-defined]
    return out


def range_break(ctx: Context, base_bars: int = 4) -> list[Signal]:
    """New high/low of day after a tight base under/over the extreme."""
    b = ctx.bars
    if len(b) < base_bars + 3:
        return []
    out = []
    for side, d, col in (("long", 1, "high"), ("short", -1, "low")):
        name = "HOD break" if d > 0 else "LOD break"
        prior = b.iloc[:-1]
        extreme = float(prior[col].max()) if d > 0 else float(prior[col].min())
        base = b.iloc[-1 - base_bars : -1]
        base_ext = float(base[col].max()) if d > 0 else float(base[col].min())
        base_opposite = float(base["low"].min()) if d > 0 else float(base["high"].max())
        near = abs(extreme - base_ext) <= 0.25 * max(1e-9, abs(extreme - base_opposite))
        tight = abs(extreme - base_opposite) <= (0.35 * ctx.daily_atr if ctx.daily_atr else abs(extreme) * 0.01)
        if not (near and tight):
            continue
        fired = d * (float(b["close"].iloc[-1]) - extreme) > 0
        out.append(Signal(name, side, "triggered" if fired else "armed",
                          extreme if fired else extreme + d * _tick(extreme), base_opposite,
                          _when(ctx, len(b) - 1) if fired else None,
                          description=f"{base_bars}-bar base tucked under the {'high' if d > 0 else 'low'} of day "
                                      f"{extreme:.2f}; {'broke it' if fired else 'trigger on a break'}"))
        if fired:
            out[-1]._bar = len(b) - 1  # type: ignore[attr-defined]
    return out


def red_to_green(ctx: Context) -> list[Signal]:
    if ctx.prior_close is None:
        return []
    b = ctx.bars
    pc = ctx.prior_close
    opened = float(b["open"].iloc[0])
    out = []
    for side, d in (("long", 1), ("short", -1)):
        name = "Red-to-green" if d > 0 else "Green-to-red"
        if d * (opened - pc) >= 0:
            continue  # need to open on the other side of yesterday's close
        i = _first_cross(b["close"], pc, d)
        seg = b.iloc[-6:]
        stop = float(seg["low"].min()) if d > 0 else float(seg["high"].max())
        if i is None:
            out.append(Signal(name, side, "armed", pc + d * _tick(pc), stop, None,
                              description=f"opened {'below' if d > 0 else 'above'} yesterday's close {pc:.2f}; "
                                          f"trigger on a move back through it"))
        else:
            ok = (d * (b["close"].iloc[i:] - pc) > 0).all()
            out.append(Signal(name, side, "triggered" if ok else "invalidated", pc, stop, _when(ctx, i),
                              description=f"crossed yesterday's close {pc:.2f} at {_when(ctx, i)}"))
            out[-1]._bar = i  # type: ignore[attr-defined]
    return out


# ---------------------------------------------------------------- scoring

def score(ctx: Context, sig: Signal) -> Signal:
    if sig.status == "forming":
        return sig
    q = 50
    d = 1 if sig.side == "long" else -1
    last = ctx.last
    i = getattr(sig, "_bar", len(ctx.bars) - 1)
    rv = ctx.bar_rvol(i)
    if not np.isnan(rv):
        if rv >= 1.5:
            q += 10; sig.reasons.append(f"trigger bar volume {rv:.1f}x normal for that time")
        elif rv < 0.8 and sig.status == "triggered":
            q -= 10; sig.warnings.append(f"trigger bar volume only {rv:.1f}x normal")
    if not np.isnan(ctx.cum_rvol):
        if ctx.cum_rvol >= 1.5:
            q += 10; sig.reasons.append(f"stock is in play: {ctx.cum_rvol:.1f}x usual volume so far")
        elif ctx.cum_rvol < 0.8:
            q -= 5; sig.warnings.append(f"light day: {ctx.cum_rvol:.1f}x usual volume")
    if "VWAP" not in sig.name:
        if d * (last["close"] - last["vwap"]) > 0:
            q += 10; sig.reasons.append("on the right side of VWAP")
        else:
            q -= 10; sig.warnings.append("fighting VWAP")
    if d * (last["ema9"] - last["ema20"]) > 0:
        q += 5; sig.reasons.append("9 EMA over 20 EMA in the trade's direction")
    if ctx.regime:
        reg = ctx.regime.lower()
        if (reg.startswith("trend-up") and d > 0) or (reg.startswith("trend-down") and d < 0):
            q += 10; sig.reasons.append(f"agrees with the {ctx.regime} market regime")
        elif (reg.startswith("trend-up") and d < 0) or (reg.startswith("trend-down") and d > 0):
            q -= 10; sig.warnings.append(f"against the {ctx.regime} market regime")
        elif "chop" in reg and sig.name.startswith(("ORB", "HOD", "LOD")):
            q -= 10; sig.warnings.append("breakouts fail more often in a choppy regime")
    if ctx.daily_atr:
        if sig.risk > 0.5 * ctx.daily_atr:
            q -= 10; sig.warnings.append(f"wide stop: {sig.risk / ctx.daily_atr:.2f} daily ATRs")
        elif sig.risk < 0.04 * ctx.daily_atr:
            q -= 5; sig.warnings.append("stop is inside normal noise; expect to get shaken out")
    band = last["upper2"] if d > 0 else last["lower2"]
    if d * (last["close"] - band) > 0:
        q -= 10; sig.warnings.append("extended beyond the 2σ VWAP band")
    t = ctx.bars.index[-1]
    m = t.hour * 60 + t.minute
    if m >= 15 * 60:
        q -= 10; sig.warnings.append("late in the session: less time for the move")
    elif 11 * 60 + 30 <= m < 13 * 60 + 30:
        q -= 5; sig.warnings.append("lunch hour: thinner volume, more fakeouts")
    if sig.status == "triggered":
        age = len(ctx.bars) - 1 - i
        if age > 3:
            q -= 10; sig.warnings.append(f"triggered {age} bars ago; chasing now is a worse entry")
        move = d * (float(last["close"]) - sig.trigger)
        if sig.risk > 0 and move > sig.risk:
            sig.warnings.append(f"already {move / sig.risk:.1f}R past the trigger")
    if sig.status == "invalidated":
        q = min(q, 20)
    sig.quality = int(max(0, min(100, q)))
    return sig


ALL = {
    "orb": opening_range,
    "vwap": vwap_reclaim,
    "pullback": trend_pullback,
    "range": range_break,
    "r2g": red_to_green,
}


def evaluate(ctx: Context, which: list[str] | None = None, orb_minutes: int = 15) -> list[Signal]:
    sigs: list[Signal] = []
    for key in which or list(ALL):
        fn = ALL[key]
        sigs += fn(ctx, orb_minutes) if key == "orb" else fn(ctx)
    sigs = [score(ctx, s) for s in sigs]
    rank = {"triggered": 0, "armed": 1, "forming": 2, "invalidated": 3}
    return sorted(sigs, key=lambda s: (rank[s.status], -s.quality))
