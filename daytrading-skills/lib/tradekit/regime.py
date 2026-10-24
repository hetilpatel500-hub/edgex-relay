"""Market regime: is today a day to press breakouts, fade extremes, or sit on your hands?"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import indicators as ind

PLAYBOOKS = {
    "trend-up": {
        "size": 1.0,
        "favor": ["ORB long", "trend pullback long", "HOD break", "VWAP reclaim long"],
        "avoid": ["fading strength", "shorting new highs"],
        "notes": "buy pullbacks to VWAP / 9 EMA, let runners work, trail stops",
    },
    "trend-down": {
        "size": 0.75,
        "favor": ["ORB short", "VWAP rejection short", "LOD break", "trend pullback short"],
        "avoid": ["bottom fishing", "buying gap downs blindly"],
        "notes": "sell rips into VWAP; bounces are sharp, so take partials quickly",
    },
    "range": {
        "size": 0.75,
        "favor": ["VWAP reclaim/rejection", "fades at prior-day high/low", "red-to-green"],
        "avoid": ["chasing breakouts", "holding runners"],
        "notes": "take profits at the opposite side of the range; first targets only",
    },
    "volatile": {
        "size": 0.5,
        "favor": ["A+ setups only", "liquid names", "wider stops with smaller size"],
        "avoid": ["tight stops", "illiquid small caps", "overtrading"],
        "notes": "ranges are big in both directions: cut size so dollar risk stays fixed",
    },
}


def _trend_score(df: pd.DataFrame) -> dict:
    c = df["close"]
    e20, e50 = ind.ema(c, 20), ind.ema(c, 50)
    sma200 = c.rolling(200, min_periods=120).mean()
    score = 0
    score += 1 if c.iloc[-1] > e20.iloc[-1] else -1
    score += 1 if e20.iloc[-1] > e50.iloc[-1] else -1
    score += 1 if e20.iloc[-1] > e20.iloc[-6] else -1
    if not np.isnan(sma200.iloc[-1]):
        score += 1 if c.iloc[-1] > sma200.iloc[-1] else -1
    er = float(ind.efficiency_ratio(c, 10).iloc[-1])
    atr = ind.atr(df, 14)
    atr_pct = atr / c
    rank = float(ind.percentile_rank(atr_pct, 252).iloc[-1]) if len(df) > 60 else float("nan")
    return {
        "close": float(c.iloc[-1]), "ret5": float(c.iloc[-1] / c.iloc[-6] - 1),
        "ret20": float(c.iloc[-1] / c.iloc[-21] - 1), "vs_ema20": float(c.iloc[-1] / e20.iloc[-1] - 1),
        "trend_score": score, "efficiency_10d": er, "atr_pct": float(atr_pct.iloc[-1]),
        "atr_pct_rank_1y": rank,
    }


def classify(index_daily: dict[str, pd.DataFrame], vix: pd.DataFrame | None = None,
             breadth: float | None = None, intraday: pd.DataFrame | None = None) -> dict:
    """Combine index trend, volatility and breadth into one label plus a playbook."""
    per = {sym: _trend_score(df) for sym, df in index_daily.items() if len(df) >= 60}
    if not per:
        raise ValueError("need at least 60 daily bars for the index ETFs")
    trend = float(np.mean([v["trend_score"] for v in per.values()]))
    er = float(np.nanmean([v["efficiency_10d"] for v in per.values()]))
    vol_rank = float(np.nanmean([v["atr_pct_rank_1y"] for v in per.values()]))
    reasons = []
    vix_level = None
    if vix is not None and len(vix):
        vix_level = float(vix["close"].iloc[-1])
        reasons.append(f"VIX {vix_level:.1f}")

    volatile = (vix_level is not None and vix_level >= 28) or (not np.isnan(vol_rank) and vol_rank >= 85)
    if volatile:
        label = "volatile"
        reasons.append(f"index ATR in the {vol_rank:.0f}th percentile of the past year" if not np.isnan(vol_rank)
                       else "volatility is elevated")
    elif trend >= 2 and er >= 0.3:
        label = "trend-up"
    elif trend <= -2 and er >= 0.3:
        label = "trend-down"
    elif abs(trend) >= 3:
        label = "trend-up" if trend > 0 else "trend-down"
    else:
        label = "range"
    reasons.append(f"trend score {trend:+.1f} of ±4 (price vs 20/50 EMA, 20 EMA slope, 200-day)")
    reasons.append(f"10-day efficiency {er:.2f} (1 = straight line, under 0.3 = choppy)")
    if breadth is not None:
        reasons.append(f"{breadth:.0%} of the watch universe is above its 20 EMA")
        if label == "trend-up" and breadth < 0.4:
            reasons.append("narrow rally: index up on few names, so be pickier")
        if label == "trend-down" and breadth > 0.6:
            reasons.append("breadth is holding up better than the index")

    out = {"label": label, "reasons": reasons, "indexes": per, "vix": vix_level, "breadth": breadth,
           "playbook": PLAYBOOKS[label]}
    if intraday is not None and len(intraday) >= 3:
        out["today"] = intraday_read(intraday)
    return out


def intraday_read(day: pd.DataFrame) -> dict:
    """Early read on whether today is trending or rotating, from one index's intraday bars."""
    c = day["close"]
    vw = ind.vwap(day)["vwap"]
    above = float((c > vw).mean())
    er = float(abs(c.iloc[-1] - day["open"].iloc[0]) / max(1e-9, c.diff().abs().sum()))
    rng = float(day["high"].max() - day["low"].min())
    crosses = int(((c > vw).astype(int).diff().abs() > 0).sum())
    if er >= 0.35 and (above >= 0.8 or above <= 0.2):
        kind = "trend day so far"
    elif crosses >= 4:
        kind = "rotational / chop so far"
    else:
        kind = "undecided"
    return {"read": kind, "share_of_bars_above_vwap": above, "efficiency": er, "vwap_crosses": crosses,
            "range": rng, "last_vs_vwap": float(c.iloc[-1] / vw.iloc[-1] - 1)}


def breadth_above_ema20(data: dict[str, pd.DataFrame]) -> float | None:
    flags = [bool(df["close"].iloc[-1] > ind.ema(df["close"], 20).iloc[-1]) for df in data.values() if len(df) >= 25]
    return float(np.mean(flags)) if flags else None
