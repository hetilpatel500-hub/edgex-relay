"""Vectorised indicators. All take/return pandas objects aligned to the input."""

from __future__ import annotations

import numpy as np
import pandas as pd


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=1).mean()


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev = df["close"].shift(1)
    tr = pd.concat([df["high"] - df["low"], (df["high"] - prev).abs(), (df["low"] - prev).abs()], axis=1)
    return tr.max(axis=1)


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Wilder's average true range."""
    return true_range(df).ewm(alpha=1 / n, adjust=False, min_periods=1).mean()


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    return (100 - 100 / (1 + rs)).fillna(100.0).where(dn.notna())


def vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Session-anchored VWAP (resets each calendar day) with 1 and 2 sigma bands."""
    tp = (df["high"] + df["low"] + df["close"]) / 3
    vol = df["volume"].where(df["volume"] > 0, 1.0)
    key = df.index.date
    cum_v = vol.groupby(key).cumsum()
    cum_pv = (tp * vol).groupby(key).cumsum()
    cum_p2v = (tp * tp * vol).groupby(key).cumsum()
    vw = cum_pv / cum_v
    sd = np.sqrt((cum_p2v / cum_v - vw * vw).clip(lower=0))
    return pd.DataFrame(
        {"vwap": vw, "upper1": vw + sd, "lower1": vw - sd, "upper2": vw + 2 * sd, "lower2": vw - 2 * sd},
        index=df.index,
    )


def bollinger(s: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    mid = sma(s, n)
    sd = s.rolling(n, min_periods=n).std(ddof=0)
    return pd.DataFrame({"mid": mid, "upper": mid + k * sd, "lower": mid - k * sd,
                         "width": (2 * k * sd) / mid}, index=s.index)


def efficiency_ratio(s: pd.Series, n: int = 10) -> pd.Series:
    """Kaufman efficiency ratio: 1 = straight-line trend, 0 = pure chop."""
    change = (s - s.shift(n)).abs()
    path = s.diff().abs().rolling(n, min_periods=n).sum()
    return change / path.replace(0, np.nan)


def percentile_rank(s: pd.Series, window: int) -> pd.Series:
    """Where the latest value sits in its trailing window, 0-100."""
    return s.rolling(window, min_periods=max(5, window // 4)).apply(
        lambda w: (w[:-1] < w[-1]).mean() * 100 if len(w) > 1 else np.nan, raw=True
    )


def log_returns(s: pd.Series) -> pd.Series:
    return np.log(s / s.shift(1))
