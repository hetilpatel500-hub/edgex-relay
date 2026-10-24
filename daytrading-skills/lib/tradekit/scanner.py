"""Chart scanner: run setup detectors across a universe of daily charts."""

from __future__ import annotations

import io
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd

from . import indicators as ind

UNIVERSE_DIR = Path(__file__).resolve().parent / "universes"
NASDAQ_LISTED = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
OTHER_LISTED = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

# share of a regular session's volume that has usually traded by each time (US equities, rough U-curve)
_VOLUME_CURVE = [(570, 0.0), (600, 0.18), (630, 0.27), (660, 0.34), (720, 0.45), (780, 0.54),
                 (840, 0.63), (900, 0.75), (930, 0.84), (960, 1.0)]


def session_volume_fraction(minute_of_day: int) -> float:
    xs, ys = zip(*_VOLUME_CURVE)
    return float(np.interp(minute_of_day, xs, ys))


# ---------------------------------------------------------------- universes

def builtin_universes() -> list[str]:
    return sorted(p.stem for p in UNIVERSE_DIR.glob("*.txt"))


def read_symbol_file(path: Path) -> list[str]:
    out = []
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out += [s.strip().upper() for s in line.replace(",", " ").split() if s.strip()]
    return list(dict.fromkeys(out))


def parse_nasdaq_directory(text: str, include_etfs: bool = False) -> list[str]:
    """Parse nasdaqlisted.txt / otherlisted.txt (pipe-delimited) into Yahoo-style tickers."""
    lines = [ln for ln in text.splitlines() if ln and not ln.startswith("File Creation Time")]
    if not lines:
        return []
    df = pd.read_csv(io.StringIO("\n".join(lines)), sep="|", dtype=str)
    sym_col = "Symbol" if "Symbol" in df.columns else "ACT Symbol"
    if "Test Issue" in df.columns:
        df = df[df["Test Issue"] == "N"]
    if not include_etfs and "ETF" in df.columns:
        df = df[df["ETF"] == "N"]
    name = df["Security Name"].fillna("")
    junk = name.str.contains(r"\b(?:Warrant|Rights?|Units?|Preferred|Notes? due|Depositary Shares? Representing)\b",
                             case=False, regex=True)
    df = df[~junk]
    syms = df[sym_col].dropna().str.strip()
    syms = syms[~syms.str.contains(r"[\$\^=]", regex=True)]
    return sorted(set(syms.str.replace(".", "-", regex=False)))


def fetch_us_listed(include_etfs: bool = False, timeout: int = 30) -> list[str]:
    syms = []
    for url in (NASDAQ_LISTED, OTHER_LISTED):
        req = urllib.request.Request(url, headers={"User-Agent": "daytrading-skills/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https URL
            syms += parse_nasdaq_directory(resp.read().decode("utf-8", "replace"), include_etfs)
    return sorted(set(syms))


def resolve_universe(spec: str | None, tickers: list[str] | None = None) -> list[str]:
    if tickers:
        return tickers
    spec = spec or "liquid"
    p = Path(spec).expanduser()
    if p.exists():
        return read_symbol_file(p)
    if spec in ("us-all", "all"):
        return fetch_us_listed()
    if spec == "us-all-etfs":
        return fetch_us_listed(include_etfs=True)
    f = UNIVERSE_DIR / f"{spec}.txt"
    if f.exists():
        return read_symbol_file(f)
    raise ValueError(f"unknown universe {spec!r}: use a file path, us-all, or one of {builtin_universes()}")


# ---------------------------------------------------------------- features

@dataclass
class Filters:
    min_price: float = 2.0
    max_price: float | None = None
    min_dollar_volume: float = 5e6  # 20-day average
    min_atr_pct: float = 0.0


@dataclass
class Hit:
    symbol: str
    setup: str
    direction: str  # long / short / either
    score: float
    detail: str
    metrics: dict = field(default_factory=dict)


def features(df: pd.DataFrame, bench: pd.DataFrame | None = None, now: pd.Timestamp | None = None) -> dict | None:
    if len(df) < 30:
        return None
    c, h, lo, o, v = (df[k] for k in ("close", "high", "low", "open", "volume"))
    now = now or pd.Timestamp.now(tz=df.index.tz)
    last_day = df.index[-1].date()
    partial = last_day == now.date() and (now.hour * 60 + now.minute) < 960 and now.weekday() < 5
    frac = session_volume_fraction(now.hour * 60 + now.minute) if partial else 1.0
    prev_v = v.iloc[-21:-1]
    avg_vol = float(prev_v.mean()) if len(prev_v) else float("nan")
    rvol = float(v.iloc[-1] / max(1e-9, avg_vol * max(frac, 0.08)))
    a = ind.atr(df, 14)
    e9, e20, e50 = ind.ema(c, 9), ind.ema(c, 20), ind.ema(c, 50)
    bb = ind.bollinger(c, 20)
    width_rank = float(ind.percentile_rank(bb["width"], 120).iloc[-1]) if len(df) >= 40 else float("nan")
    rng = (h - lo)
    f = {
        "close": float(c.iloc[-1]), "open": float(o.iloc[-1]), "high": float(h.iloc[-1]), "low": float(lo.iloc[-1]),
        "prev_close": float(c.iloc[-2]), "prev_high": float(h.iloc[-2]), "prev_low": float(lo.iloc[-2]),
        "change": float(c.iloc[-1] / c.iloc[-2] - 1), "gap": float(o.iloc[-1] / c.iloc[-2] - 1),
        "volume": float(v.iloc[-1]), "avg_volume": avg_vol, "rvol": rvol, "partial_day": partial,
        "dollar_volume": float((c.iloc[-21:-1] * prev_v).mean()),
        "atr": float(a.iloc[-2]), "atr_pct": float(a.iloc[-2] / c.iloc[-2]),
        "hi20": float(h.iloc[-21:-1].max()), "lo20": float(lo.iloc[-21:-1].min()),
        "hi55": float(h.iloc[-56:-1].max()) if len(df) > 56 else float("nan"),
        "hi252": float(h.iloc[-253:-1].max()) if len(df) > 200 else float("nan"),
        "ema9": float(e9.iloc[-1]), "ema20": float(e20.iloc[-1]), "ema50": float(e50.iloc[-1]),
        "ema20_slope": float(e20.iloc[-1] / e20.iloc[-6] - 1),
        "bb_width_rank": width_rank,
        "nr7": bool(rng.iloc[-1] <= rng.iloc[-7:].min()),
        "inside": bool(h.iloc[-1] <= h.iloc[-2] and lo.iloc[-1] >= lo.iloc[-2]),
        "close_loc": float((c.iloc[-1] - lo.iloc[-1]) / max(1e-9, h.iloc[-1] - lo.iloc[-1])),
        "ret5": float(c.iloc[-1] / c.iloc[-6] - 1), "ret20": float(c.iloc[-1] / c.iloc[-21] - 1),
        "rsi2": float(ind.rsi(c, 2).iloc[-1]),
        "down_days": int((c.diff().iloc[-5:] < 0)[::-1].cumprod().sum()),
        "as_of": df.index[-1],
    }
    if bench is not None and len(bench) > 21:
        bc = bench["close"]
        f["rs20"] = f["ret20"] - float(bc.iloc[-1] / bc.iloc[-21] - 1)
        f["bench_above_ema20"] = bool(bc.iloc[-1] > ind.ema(bc, 20).iloc[-1])
    # flag: pole then flag
    if len(df) >= 15:
        pole = float(c.iloc[-5] / c.iloc[-12] - 1)
        flag_hi, flag_lo = float(h.iloc[-4:].max()), float(lo.iloc[-4:].min())
        f["pole"] = pole
        f["flag_depth"] = (flag_hi - flag_lo) / max(1e-9, float(c.iloc[-5]) - float(c.iloc[-12]))
        f["flag_vol_ratio"] = float(v.iloc[-4:].mean() / max(1e-9, v.iloc[-12:-4].mean()))
    return f


# ---------------------------------------------------------------- detectors

def _clip(x, lo=0.0, hi=100.0):
    return float(max(lo, min(hi, x)))


def detect(sym: str, f: dict, p: dict) -> list[Hit]:
    hits = []
    rv = f["rvol"]

    if abs(f["gap"]) >= p["gap_pct"] / 100 and rv >= p["gap_rvol"]:
        up = f["gap"] > 0
        held = (f["close"] >= f["open"]) if up else (f["close"] <= f["open"])
        score = _clip(40 + min(30, abs(f["gap"]) * 300) + min(15, rv * 3) + (8 if held else -8))
        hits.append(Hit(sym, "gap-up" if up else "gap-down", "long" if up else "short", score,
                        f"gapped {f['gap']:+.1%} on {rv:.1f}x volume, {'holding' if held else 'fading'} the gap"))

    if rv >= p["spike_rvol"] and abs(f["change"]) >= 0.02:
        hits.append(Hit(sym, "volume-spike", "long" if f["change"] > 0 else "short",
                        _clip(35 + min(30, rv * 5) + min(20, abs(f["change"]) * 200)),
                        f"{rv:.1f}x normal volume, {f['change']:+.1%} on the day"))

    if f["close"] > f["hi20"] and f["close_loc"] >= 0.6 and rv >= 1.2:
        bonus = (10 if not np.isnan(f["hi55"]) and f["close"] > f["hi55"] else 0) + \
                (15 if not np.isnan(f["hi252"]) and f["close"] > f["hi252"] else 0)
        label = "52-week high" if bonus >= 25 else "55-day high" if bonus >= 10 else "20-day high"
        hits.append(Hit(sym, "breakout", "long", _clip(45 + min(20, rv * 5) + bonus + f["close_loc"] * 10),
                        f"closed through the {label} on {rv:.1f}x volume"))

    if f["close"] < f["lo20"] and f["close_loc"] <= 0.4 and rv >= 1.2:
        hits.append(Hit(sym, "breakdown", "short", _clip(45 + min(20, rv * 5) + (1 - f["close_loc"]) * 10),
                        f"closed under the 20-day low on {rv:.1f}x volume"))

    if not np.isnan(f["bb_width_rank"]) and f["bb_width_rank"] <= 10 and (f["nr7"] or f["inside"]):
        trend = "long" if f["close"] > f["ema50"] else "short"
        hits.append(Hit(sym, "squeeze", trend, _clip(55 + (10 - f["bb_width_rank"]) * 2 + (5 if f["nr7"] else 0)),
                        f"tightest Bollinger width in {100 - f['bb_width_rank']:.0f}% of the last 120 days, "
                        f"{'NR7' if f['nr7'] else 'inside day'}: coiled for a move"))

    if "pole" in f and f["pole"] >= p["flag_pole"] / 100 and f["flag_depth"] <= 0.5 \
            and f["flag_vol_ratio"] < 1 and f["close"] > f["ema9"]:
        hits.append(Hit(sym, "bull-flag", "long",
                        _clip(50 + min(25, f["pole"] * 100) + (0.5 - f["flag_depth"]) * 30 + (1 - f["flag_vol_ratio"]) * 15),
                        f"{f['pole']:+.0%} pole, tight {f['flag_depth']:.0%}-deep flag on lighter volume"))

    if f["ema20"] > f["ema50"] and f["ema20_slope"] > 0 and f["low"] <= f["ema20"] * 1.005 \
            and f["close"] > f["ema20"] and f["close_loc"] >= 0.5:
        hits.append(Hit(sym, "ema-pullback", "long", _clip(50 + min(20, f["ema20_slope"] * 400) + f["close_loc"] * 10),
                        "uptrend pulled back to the 20 EMA and closed strong"))

    if f.get("rs20") is not None and f["rs20"] >= p["rs_pct"] / 100 and f["close"] > f["ema20"]:
        weak_tape = f.get("bench_above_ema20") is False
        hits.append(Hit(sym, "relative-strength", "long", _clip(45 + min(30, f["rs20"] * 100) + (10 if weak_tape else 0)),
                        f"{f['rs20']:+.1%} vs the benchmark over 20 days"
                        + (" while the market is under its 20 EMA" if weak_tape else "")))

    if f["rsi2"] < 10 and f["down_days"] >= 3 and f["close_loc"] >= 0.5 and f["close"] > f["ema50"]:
        hits.append(Hit(sym, "oversold-bounce", "long", _clip(45 + (10 - f["rsi2"]) * 2 + f["down_days"] * 3),
                        f"{f['down_days']} down days, RSI(2) {f['rsi2']:.0f}, closed in the top half of the range "
                        "above the 50 EMA"))
    for h in hits:
        h.metrics = {k: f[k] for k in ("close", "change", "gap", "rvol", "atr_pct", "dollar_volume")}
    return hits


SETUPS = ["gap-up", "gap-down", "volume-spike", "breakout", "breakdown", "squeeze", "bull-flag", "ema-pullback",
          "relative-strength", "oversold-bounce"]

DEFAULT_PARAMS = {"gap_pct": 3.0, "gap_rvol": 1.5, "spike_rvol": 2.5, "flag_pole": 15.0, "rs_pct": 8.0}


def scan(data: dict[str, pd.DataFrame], filters: Filters, setups: list[str] | None = None,
         bench: pd.DataFrame | None = None, params: dict | None = None, now=None) -> tuple[list[dict], dict]:
    params = {**DEFAULT_PARAMS, **(params or {})}
    stats = {"scanned": len(data), "passed_filters": 0, "too_short": 0}
    rows = []
    for sym, df in data.items():
        f = features(df, bench, now)
        if f is None:
            stats["too_short"] += 1
            continue
        if f["close"] < filters.min_price or (filters.max_price and f["close"] > filters.max_price):
            continue
        if not f["dollar_volume"] >= filters.min_dollar_volume or f["atr_pct"] < filters.min_atr_pct / 100:
            continue
        stats["passed_filters"] += 1
        hits = [h for h in detect(sym, f, params) if not setups or h.setup in setups]
        if not hits:
            continue
        hits.sort(key=lambda h: -h.score)
        confluence = len(hits)
        rows.append({
            "symbol": sym, "score": round(min(100.0, hits[0].score + 5 * (confluence - 1)), 1),
            "setups": [h.setup for h in hits], "direction": hits[0].direction,
            "why": "; ".join(h.detail for h in hits),
            **{k: round(f[k], 4) for k in ("close", "change", "gap", "rvol", "atr_pct")},
            "dollar_volume": round(f["dollar_volume"]), "partial_day": f["partial_day"], "as_of": f["as_of"],
        })
    rows.sort(key=lambda r: -r["score"])
    return rows, stats
