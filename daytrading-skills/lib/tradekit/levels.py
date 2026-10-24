"""Support and resistance levels day traders actually watch."""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import indicators as ind
from .session import Session, premarket, rth, split_days


@dataclass
class Level:
    price: float
    kind: str  # short code, e.g. PDH, VWAP, POC, R1, SWING
    label: str  # human description
    strength: int = 1  # 1 (minor) .. 5 (major)
    tags: list[str] = field(default_factory=list)


def _today_and_prior(daily: pd.DataFrame, today) -> tuple[pd.DataFrame, pd.DataFrame | None]:
    """Split daily bars into completed sessions and today's (possibly partial) bar."""
    if len(daily) and daily.index[-1].date() == today:
        return daily.iloc[:-1], daily.iloc[-1:]
    return daily, None


def prior_day(daily: pd.DataFrame, today) -> list[Level]:
    done, _ = _today_and_prior(daily, today)
    if len(done) == 0:
        return []
    d = done.iloc[-1]
    when = done.index[-1].strftime("%b %d")
    return [
        Level(float(d["high"]), "PDH", f"prior day high ({when})", 4),
        Level(float(d["low"]), "PDL", f"prior day low ({when})", 4),
        Level(float(d["close"]), "PDC", f"prior day close ({when})", 3),
    ]


def floor_pivots(high: float, low: float, close: float) -> list[Level]:
    p = (high + low + close) / 3
    r1, s1 = 2 * p - low, 2 * p - high
    r2, s2 = p + (high - low), p - (high - low)
    r3, s3 = high + 2 * (p - low), low - 2 * (high - p)
    return [
        Level(p, "P", "floor pivot", 2), Level(r1, "R1", "pivot R1", 2), Level(s1, "S1", "pivot S1", 2),
        Level(r2, "R2", "pivot R2", 1), Level(s2, "S2", "pivot S2", 1),
        Level(r3, "R3", "pivot R3", 1), Level(s3, "S3", "pivot S3", 1),
    ]


def multi_day(daily: pd.DataFrame, today) -> list[Level]:
    done, _ = _today_and_prior(daily, today)
    out = []
    if len(done) >= 20:
        w = done.iloc[-20:]
        out += [Level(float(w["high"].max()), "20DH", "20-day high", 3),
                Level(float(w["low"].min()), "20DL", "20-day low", 3)]
    if len(done) >= 240:
        w = done.iloc[-252:]
        out += [Level(float(w["high"].max()), "52WH", "52-week high", 5),
                Level(float(w["low"].min()), "52WL", "52-week low", 5)]
    if len(done) >= 6:
        weeks = done.groupby(done.index.tz_localize(None).to_period("W"))
        keys = list(weeks.groups.keys())
        cur = pd.Timestamp(today).to_period("W")
        prev = [k for k in keys if k < cur]
        if prev:
            g = weeks.get_group(prev[-1])
            out += [Level(float(g["high"].max()), "PWH", "prior week high", 3),
                    Level(float(g["low"].min()), "PWL", "prior week low", 3)]
    return out


def intraday(intra: pd.DataFrame, session: Session, today, orb_minutes: int = 15) -> list[Level]:
    out = []
    day = intra[intra.index.date == today]
    pre = premarket(day, session)
    if len(pre):
        out += [Level(float(pre["high"].max()), "PMH", "premarket high", 4),
                Level(float(pre["low"].min()), "PML", "premarket low", 4)]
    reg = rth(day, session)
    if len(reg):
        vw = ind.vwap(reg).iloc[-1]
        out.append(Level(float(vw["vwap"]), "VWAP", "session VWAP", 4))
        out += [Level(float(vw["upper2"]), "VWAP+2", "VWAP +2σ band", 2),
                Level(float(vw["lower2"]), "VWAP-2", "VWAP -2σ band", 2)]
        mins = session.minute_of(reg.index)
        orb = reg[np.asarray(mins) < orb_minutes]
        if len(orb) and len(reg) > len(orb):
            out += [Level(float(orb["high"].max()), "ORH", f"{orb_minutes}-min opening range high", 3),
                    Level(float(orb["low"].min()), "ORL", f"{orb_minutes}-min opening range low", 3)]
        out += [Level(float(reg["high"].max()), "HOD", "high of day", 3),
                Level(float(reg["low"].min()), "LOD", "low of day", 3)]
    return out


def swings(df: pd.DataFrame, tol: float, left: int = 3, right: int = 3, max_levels: int = 8) -> list[Level]:
    """Cluster pivot highs/lows that sit within ``tol`` of each other; more touches = stronger."""
    h, lo = df["high"].to_numpy(), df["low"].to_numpy()
    pts = []
    for i in range(left, len(df) - right):
        if h[i] == h[i - left : i + right + 1].max():
            pts.append(h[i])
        if lo[i] == lo[i - left : i + right + 1].min():
            pts.append(lo[i])
    if not pts:
        return []
    pts.sort()
    clusters = [[pts[0]]]
    for p in pts[1:]:
        if p - clusters[-1][-1] <= tol:
            clusters[-1].append(p)
        else:
            clusters.append([p])
    clusters.sort(key=len, reverse=True)
    out = []
    for c in clusters[:max_levels]:
        if len(c) < 2:
            continue
        out.append(Level(float(np.mean(c)), "SWING", f"swing zone ({len(c)} touches)", min(5, 1 + len(c) // 2)))
    return out


def volume_profile(df: pd.DataFrame, bins: int = 60, value_area: float = 0.70) -> dict | None:
    if len(df) < 10 or df["volume"].sum() <= 0:
        return None
    lo, hi = float(df["low"].min()), float(df["high"].max())
    if hi <= lo:
        return None
    edges = np.linspace(lo, hi, bins + 1)
    mids = (edges[:-1] + edges[1:]) / 2
    hist = np.zeros(bins)
    # spread each bar's volume evenly across the price bins it traded through
    for l_, h_, v in zip(df["low"].to_numpy(), df["high"].to_numpy(), df["volume"].to_numpy()):
        a = max(0, np.searchsorted(edges, l_, side="right") - 1)
        b = min(bins - 1, np.searchsorted(edges, h_, side="right") - 1)
        hist[a : b + 1] += v / (b - a + 1)
    poc = int(hist.argmax())
    total, inside = hist.sum(), hist[poc]
    i = j = poc
    while inside < value_area * total and (i > 0 or j < bins - 1):
        left = hist[i - 1] if i > 0 else -1
        right = hist[j + 1] if j < bins - 1 else -1
        if right >= left:
            j += 1
            inside += hist[j]
        else:
            i -= 1
            inside += hist[i]
    return {"poc": float(mids[poc]), "vah": float(edges[j + 1]), "val": float(edges[i])}


def round_numbers(price: float, atr: float | None) -> list[Level]:
    step = 10 ** math.floor(math.log10(max(price, 0.01)))
    if atr and atr < step / 2:
        step /= 2 if atr > step / 10 else 10
    step = max(step, 0.5)
    base = math.floor(price / step) * step
    return [Level(base, "ROUND", "round number", 1), Level(base + step, "ROUND", "round number", 1)]


def collect(intra: pd.DataFrame | None, daily: pd.DataFrame | None, session: Session, today,
            orb_minutes: int = 15, profile_days: int = 5) -> tuple[list[Level], dict]:
    """Every level type we know, plus context numbers (ATR, last price)."""
    levels: list[Level] = []
    ctx: dict = {}
    if daily is not None and len(daily):
        done, _ = _today_and_prior(daily, today)
        levels += prior_day(daily, today)
        levels += multi_day(daily, today)
        if len(done):
            d = done.iloc[-1]
            levels += floor_pivots(float(d["high"]), float(d["low"]), float(d["close"]))
            ctx["daily_atr"] = float(ind.atr(done, 14).iloc[-1])
            ctx["prior_close"] = float(d["close"])
        ctx["last"] = float(daily["close"].iloc[-1])
    if intra is not None and len(intra):
        levels += intraday(intra, session, today, orb_minutes)
        ctx["last"] = float(intra["close"].iloc[-1])
        ctx["last_time"] = intra.index[-1]
        reg = rth(intra, session)
        days = sorted(split_days(reg))
        recent = reg[np.isin(reg.index.date, days[-profile_days:])] if days else reg
        vp = volume_profile(recent)
        if vp:
            n = min(profile_days, len(days))
            levels += [Level(vp["poc"], "POC", f"{n}-day volume point of control", 4),
                       Level(vp["vah"], "VAH", f"{n}-day value area high", 3),
                       Level(vp["val"], "VAL", f"{n}-day value area low", 3)]
        tol = 0.15 * ctx.get("daily_atr", float(ind.atr(reg, 14).iloc[-1]) * 6) if len(reg) else 0
        if len(recent) > 10 and tol > 0:
            levels += swings(recent, tol)
    if "last" in ctx:
        levels += round_numbers(ctx["last"], ctx.get("daily_atr"))
    return levels, ctx


def merge(levels: list[Level], tol: float) -> list[Level]:
    """Fold levels within ``tol`` of each other into one, keeping the strongest label first."""
    clusters: list[list[Level]] = []
    for lv in sorted(levels, key=lambda x: x.price):
        # anchor on the cluster's lowest price so a chain of close levels cannot snowball
        if clusters and lv.price - clusters[-1][0].price <= tol:
            clusters[-1].append(lv)
        else:
            clusters.append([lv])
    out = []
    for c in clusters:
        c = sorted(c, key=lambda x: -x.strength)
        top = c[0]
        bonus = sum(max(1, x.strength // 2) for x in c[1:])
        tags = [x.kind for x in c[1:] if x.kind != top.kind]
        out.append(Level(top.price, top.kind, top.label, min(5, top.strength + bonus), list(dict.fromkeys(tags))))
    return out


def ladder(levels: list[Level], price: float, atr: float | None, above: int = 6, below: int = 6) -> dict:
    tol = (atr or price * 0.02) * 0.08
    merged = merge(levels, tol)
    res = [lv for lv in merged if lv.price > price][:above]
    sup = [lv for lv in merged if lv.price <= price][::-1][:below]
    return {"resistance": res, "support": sup}


def nearest(levels: list[Level], price: float, direction: int, min_dist: float = 0.0,
            min_strength: int = 1) -> Level | None:
    """First level beyond ``price`` in ``direction`` (+1 up, -1 down) at least ``min_dist`` away."""
    cand = [lv for lv in levels if direction * (lv.price - price) > min_dist and lv.strength >= min_strength]
    if not cand:
        return None
    return min(cand, key=lambda lv: direction * (lv.price - price))
