"""Market data loading.

Every loader returns a DataFrame indexed by tz-aware bar *start* timestamps (in
the market time zone) with float columns: open, high, low, close, volume.

Sources:
  csv       a file you (or Claude, via any connector) saved; works offline
  yfinance  free Yahoo data (pip install yfinance); 1m for ~30 days, 5m for 60
  alpaca    free IEX bars with an Alpaca account (ALPACA_API_KEY_ID/SECRET)
  relay     the edgex-relay service in this repo (RELAY_URL, RELAY_API_KEY)
  demo      synthetic bars for trying the skills; never use for real decisions
"""

from __future__ import annotations

import json
import math
import os
import urllib.parse
import urllib.request
import zlib
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_TZ = "America/New_York"
COLUMNS = ["open", "high", "low", "close", "volume"]
SOURCES = ["auto", "csv", "yfinance", "alpaca", "relay", "demo"]

_ALIASES = {
    "timestamp": ["timestamp", "datetime", "date", "time", "ts", "t", "bar_ts", "start", "ts_event"],
    "open": ["open", "o"],
    "high": ["high", "h"],
    "low": ["low", "l"],
    "close": ["close", "c", "last", "price", "adj close"],
    "volume": ["volume", "v", "vol"],
}


class DataError(RuntimeError):
    """Raised when bars cannot be loaded; the message says how to fix it."""


# ---------------------------------------------------------------- intervals

def interval_minutes(interval: str) -> int:
    """'1m' -> 1, '5m' -> 5, '1h' -> 60, '1d' -> 1440."""
    s = interval.strip().lower()
    for suffix, mult in (("min", 1), ("m", 1), ("h", 60), ("d", 1440)):
        if s.endswith(suffix):
            return int(float(s[: -len(suffix)]) * mult)
    raise ValueError(f"unrecognised interval {interval!r}; use e.g. 1m, 5m, 15m, 1h, 1d")


def infer_interval_minutes(df: pd.DataFrame) -> int:
    """Most common spacing between consecutive bars, in minutes."""
    if len(df) < 2:
        raise DataError("need at least two bars to infer the bar interval")
    diffs = pd.Series(df.index).diff().dropna().dt.total_seconds() / 60
    diffs = diffs[diffs > 0]
    return max(1, int(round(diffs.mode().iloc[0])))


# ---------------------------------------------------------------- normalising

def _epoch_to_datetime(values: pd.Series) -> pd.DatetimeIndex:
    v = values.astype("float64")
    peak = float(np.nanmax(np.abs(v)))
    unit = "ns" if peak > 1e17 else "us" if peak > 1e14 else "ms" if peak > 1e11 else "s"
    return pd.DatetimeIndex(pd.to_datetime(v, unit=unit, utc=True))


_OFFSET = r"(?:Z|[+-]\d{2}:?\d{2})$"


def parse_times(values, tz: str = DEFAULT_TZ) -> pd.Series:
    """Timestamps of any common shape to tz-aware market time.

    Strings with an offset (``Z``, ``-04:00``) are converted, so a file that
    spans a daylight-saving change still parses; naive strings are read as
    exchange-local time.
    """
    raw = pd.Series(values).reset_index(drop=True)
    if pd.api.types.is_datetime64_any_dtype(raw):
        ts = pd.to_datetime(raw)
        if ts.dt.tz is None:
            return ts.dt.tz_localize(tz, ambiguous="NaT", nonexistent="shift_forward")
        return ts.dt.tz_convert(tz)
    text = raw.astype("string").str.strip()
    aware = text.str.contains(_OFFSET, regex=True, na=False).to_numpy(dtype=bool)
    out = pd.Series(pd.NaT, index=raw.index, dtype=f"datetime64[ns, {tz}]")
    if aware.any():
        out[aware] = pd.to_datetime(text[aware], utc=True, format="mixed", errors="coerce").dt.tz_convert(tz)
    if (~aware).any():
        naive = pd.to_datetime(text[~aware], format="mixed", errors="coerce")
        out[~aware] = naive.dt.tz_localize(tz, ambiguous="NaT", nonexistent="shift_forward")
    return out


def normalize(df: pd.DataFrame, tz: str = DEFAULT_TZ) -> pd.DataFrame:
    """Coerce any reasonable OHLCV table into the tradekit shape.

    Naive timestamps are read as exchange-local time (``tz``); aware ones are
    converted. Epoch numbers in s/ms/us/ns are detected automatically.
    """
    if df is None or len(df) == 0:
        raise DataError("no bars returned")
    df = df.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    picked = {}
    for want, options in _ALIASES.items():
        for opt in options:
            if opt in df.columns:
                picked[want] = opt
                break

    if picked.get("timestamp") == "date" and "time" in df.columns:
        raw = df["date"].astype(str) + " " + df["time"].astype(str)  # separate Date and Time columns
    elif "timestamp" in picked:
        raw = df[picked["timestamp"]]
    else:
        raw = pd.Series(df.index, index=df.index)
    if pd.api.types.is_numeric_dtype(raw):
        idx = _epoch_to_datetime(raw).tz_convert(tz)
    else:
        idx = pd.DatetimeIndex(parse_times(raw, tz))

    missing = [c for c in ("open", "high", "low", "close") if c not in picked]
    if missing == ["open", "high", "low"] and "close" in picked:
        # close-only data: treat each bar as flat
        for c in ("open", "high", "low"):
            picked[c] = picked["close"]
    elif missing:
        raise DataError(f"missing columns {missing}; found {list(df.columns)}")

    out = pd.DataFrame(
        {c: pd.to_numeric(df[picked[c]].to_numpy(), errors="coerce") for c in ("open", "high", "low", "close")},
        index=idx,
    )
    out["volume"] = (
        pd.to_numeric(df[picked["volume"]].to_numpy(), errors="coerce") if "volume" in picked else 0.0
    )
    out = out[~out.index.isna()]
    out = out.dropna(subset=["open", "high", "low", "close"])
    out["volume"] = out["volume"].fillna(0.0)
    # repair bars whose high/low do not contain open/close
    out["high"] = out[["open", "high", "low", "close"]].max(axis=1)
    out["low"] = out[["open", "high", "low", "close"]].min(axis=1)
    out = out[~out.index.duplicated(keep="last")].sort_index()
    out.index.name = "timestamp"
    return out.astype("float64")


def resample(df: pd.DataFrame, minutes: int, session_start_min: int = 9 * 60 + 30) -> pd.DataFrame:
    """Aggregate to a coarser bar size with bins lined up on the session open (09:30 by default)."""
    rule = f"{minutes}min" if minutes < 1440 else "1D"
    offset = pd.Timedelta(minutes=session_start_min % minutes) if minutes < 1440 else pd.Timedelta(0)
    agg = df.resample(rule, label="left", closed="left", origin="start_day", offset=offset).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
    )
    return agg.dropna(subset=["close"])


def to_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Collapse intraday bars to one bar per calendar date (market tz)."""
    g = df.groupby(df.index.date)
    out = pd.DataFrame(
        {
            "open": g["open"].first(),
            "high": g["high"].max(),
            "low": g["low"].min(),
            "close": g["close"].last(),
            "volume": g["volume"].sum(),
        }
    )
    out.index = pd.DatetimeIndex(pd.to_datetime(out.index)).tz_localize(df.index.tz)
    out.index.name = "timestamp"
    return out


# ---------------------------------------------------------------- csv

def load_csv(path: str | os.PathLike, tz: str = DEFAULT_TZ) -> pd.DataFrame:
    p = Path(path).expanduser()
    if not p.exists():
        raise DataError(f"CSV not found: {p}")
    if p.suffix.lower() in (".json", ".jsonl"):
        text = p.read_text()
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = [json.loads(line) for line in text.splitlines() if line.strip()]
        if isinstance(payload, dict):
            payload = payload.get("bars") or payload.get("data") or payload.get("candles") or []
        return normalize(pd.DataFrame(payload), tz)
    return normalize(pd.read_csv(p), tz)


def save_csv(df: pd.DataFrame, path: str | os.PathLike) -> Path:
    p = Path(path).expanduser()
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index_label="timestamp")
    return p


# ---------------------------------------------------------------- yfinance

def _yf():
    try:
        import yfinance as yf  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise DataError(
            "yfinance is not installed. Run: pip install yfinance  "
            "(or pass --csv with your own bars, or set ALPACA_API_KEY_ID/ALPACA_API_SECRET_KEY)"
        ) from exc
    return yf


# Yahoo's look-back limits per bar size (calendar days)
_YF_LIMITS = {1: 29, 2: 59, 5: 59, 15: 59, 30: 59, 60: 729, 90: 59}


def fetch_yfinance(symbol: str, interval: str = "5m", days: int = 60, prepost: bool = False,
                   tz: str = DEFAULT_TZ) -> pd.DataFrame:
    yf = _yf()
    mins = interval_minutes(interval)
    end = datetime.now(timezone.utc) + timedelta(days=1)
    if mins < 1440:
        limit = _YF_LIMITS.get(mins, 59)
        days = min(days, limit)
    start = end - timedelta(days=days + 1)
    ticker = yf.Ticker(symbol)
    frames = []
    if mins == 1:
        # Yahoo serves at most ~8 days of 1m bars per request
        cursor = start
        while cursor < end:
            stop = min(cursor + timedelta(days=7), end)
            part = ticker.history(start=cursor, end=stop, interval="1m", prepost=prepost,
                                  auto_adjust=True, actions=False)
            if len(part):
                frames.append(part)
            cursor = stop
    else:
        yf_interval = {60: "60m", 1440: "1d"}.get(mins, f"{mins}m")
        frames.append(ticker.history(start=start, end=end, interval=yf_interval, prepost=prepost,
                                     auto_adjust=True, actions=False))
    frames = [f for f in frames if f is not None and len(f)]
    if not frames:
        raise DataError(f"Yahoo returned no {interval} bars for {symbol}. Check the ticker, "
                        "or that the network allows query1.finance.yahoo.com.")
    return normalize(pd.concat(frames), tz)


def fetch_yfinance_many(symbols: list[str], days: int = 400, tz: str = DEFAULT_TZ,
                        chunk: int = 150, progress=None) -> dict[str, pd.DataFrame]:
    """Daily bars for many tickers in batched requests (used by the scanner)."""
    yf = _yf()
    out: dict[str, pd.DataFrame] = {}
    start = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    for i in range(0, len(symbols), chunk):
        batch = symbols[i : i + chunk]
        if progress:
            progress(i, len(symbols))
        raw = yf.download(batch, start=start, interval="1d", group_by="ticker", auto_adjust=True,
                          threads=True, progress=False)
        if raw is None or len(raw) == 0:
            continue
        for sym in batch:
            try:
                sub = raw[sym] if isinstance(raw.columns, pd.MultiIndex) else raw
            except KeyError:
                continue
            sub = sub.dropna(how="all")
            if len(sub) == 0:
                continue
            try:
                out[sym] = normalize(sub, tz)
            except DataError:
                continue
    return out


# ---------------------------------------------------------------- alpaca

def _http_json(url: str, headers: dict | None = None, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "daytrading-skills/0.1", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 - fixed https URLs
        return json.loads(resp.read().decode("utf-8"))


def alpaca_configured() -> bool:
    return bool(os.environ.get("ALPACA_API_KEY_ID") and os.environ.get("ALPACA_API_SECRET_KEY"))


def fetch_alpaca(symbol: str, interval: str = "5m", days: int = 60, tz: str = DEFAULT_TZ,
                 http=_http_json) -> pd.DataFrame:
    if not alpaca_configured():
        raise DataError("set ALPACA_API_KEY_ID and ALPACA_API_SECRET_KEY to use --source alpaca")
    mins = interval_minutes(interval)
    timeframe = "1Day" if mins >= 1440 else f"{mins // 60}Hour" if mins % 60 == 0 else f"{mins}Min"
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days + 1)
    params = {
        "timeframe": timeframe,
        "start": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit": 10000,
        "adjustment": "split",
        "feed": os.environ.get("ALPACA_FEED", "iex"),
    }
    headers = {
        "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY_ID"],
        "APCA-API-SECRET-KEY": os.environ["ALPACA_API_SECRET_KEY"],
    }
    base = f"https://data.alpaca.markets/v2/stocks/{urllib.parse.quote(symbol)}/bars"
    rows, token = [], None
    for _ in range(500):
        q = dict(params, **({"page_token": token} if token else {}))
        payload = http(f"{base}?{urllib.parse.urlencode(q)}", headers)
        rows.extend(payload.get("bars") or [])
        token = payload.get("next_page_token")
        if not token:
            break
    if not rows:
        raise DataError(f"Alpaca returned no {interval} bars for {symbol}")
    return normalize(pd.DataFrame(rows), tz)


# ---------------------------------------------------------------- edgex relay

def fetch_relay(symbol: str | None = None, limit: int = 500, tz: str = DEFAULT_TZ,
                http=_http_json) -> pd.DataFrame:
    """1-minute bars from the edgex-relay /candles endpoint (newest-first JSON)."""
    url = os.environ.get("RELAY_URL")
    key = os.environ.get("RELAY_API_KEY")
    if not url or not key:
        raise DataError("set RELAY_URL (e.g. https://your-relay.up.railway.app) and RELAY_API_KEY")
    q = {"limit": limit}
    if symbol:
        q["symbol"] = symbol
    payload = http(f"{url.rstrip('/')}/candles?{urllib.parse.urlencode(q)}", {"X-API-Key": key})
    bars = payload.get("bars") or []
    if not bars:
        raise DataError(f"relay has no buffered bars for {symbol or 'its default symbol'} yet")
    return normalize(pd.DataFrame(bars), tz)


# ---------------------------------------------------------------- synthetic

def _business_days(n: int, end: date) -> list[date]:
    days, d = [], end
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d -= timedelta(days=1)
    return sorted(days)


def synthetic_intraday(symbol: str = "DEMO", days: int = 60, interval: int = 5, seed: int = 7,
                       price: float = 100.0, daily_vol: float = 0.022, tz: str = DEFAULT_TZ,
                       end: date | None = None, today_until: time | None = None,
                       premarket: bool = False) -> pd.DataFrame:
    """Plausible fake intraday bars: U-shaped volatility, fat tails, volume smile.

    ``today_until`` adds a partial session on ``end`` (default today) up to that
    time, which is how the demos fake "the market is open right now".
    """
    rng = np.random.default_rng([seed, zlib.crc32(symbol.encode())])
    end = end or datetime.now().date()
    hist_days = _business_days(days + 1, end)
    if hist_days[-1] == end:
        hist_days = hist_days[:-1]
    hist_days = hist_days[-days:]
    sessions = [(d, time(16, 0)) for d in hist_days]
    if today_until is not None:
        sessions.append((end, today_until))

    rows = []
    px = price
    for d, until in sessions:
        day_scale = float(np.exp(rng.normal(0, 0.35)))
        start_min = 7 * 60 if premarket else 9 * 60 + 30
        stop_min = until.hour * 60 + until.minute
        px *= float(np.exp(rng.normal(0, daily_vol * 0.25)))  # overnight gap
        m = start_min
        while m < stop_min:
            rth = m >= 9 * 60 + 30
            pos = (m - 570) / 390 if rth else 0.0
            u_shape = 0.6 + 1.6 * (pos - 0.5) ** 2 * 4 / 2 if rth else 0.35
            bar_sigma = daily_vol * day_scale * math.sqrt(interval / 390) * u_shape
            sub = rng.standard_t(4, size=5) * bar_sigma / math.sqrt(5 * 2)
            path = px * np.exp(np.cumsum(sub))
            o = px
            c = float(path[-1])
            hi = float(max(o, path.max()))
            lo = float(min(o, path.min()))
            vol = float(rng.lognormal(math.log(40_000 * interval * (u_shape ** 2) * (1 if rth else 0.08)), 0.4))
            ts = pd.Timestamp(datetime.combine(d, time(m // 60, m % 60))).tz_localize(tz)
            rows.append((ts, o, hi, lo, c, vol))
            px = c
            m += interval
    df = pd.DataFrame(rows, columns=["timestamp", *COLUMNS]).set_index("timestamp")
    return df


def synthetic_daily(symbol: str = "DEMO", days: int = 400, seed: int = 7, price: float | None = None,
                    tz: str = DEFAULT_TZ, end: date | None = None) -> pd.DataFrame:
    rng = np.random.default_rng([seed, zlib.crc32(symbol.encode())])
    end = end or datetime.now().date()
    dates = _business_days(days, end)
    px = price or float(rng.uniform(8, 400))
    vol = float(rng.uniform(0.012, 0.04))
    base_volume = float(rng.lognormal(math.log(3e6), 1.0))
    drift = float(rng.normal(0.0004, 0.001))
    rows = []
    sigma = vol
    for d in dates:
        sigma = max(0.005, 0.9 * sigma + 0.1 * vol * float(np.exp(rng.normal(0, 0.5))))
        gap = float(rng.normal(0, sigma * 0.3))
        o = px * math.exp(gap)
        r = float(rng.standard_t(4)) * sigma / math.sqrt(2) + drift
        c = o * math.exp(r)
        hi = max(o, c) * math.exp(abs(float(rng.normal(0, sigma * 0.5))))
        lo = min(o, c) * math.exp(-abs(float(rng.normal(0, sigma * 0.5))))
        v = base_volume * float(np.exp(rng.normal(0, 0.35))) * (1 + 8 * abs(r))
        rows.append((pd.Timestamp(d).tz_localize(tz), o, hi, lo, c, v))
        px = c
    return pd.DataFrame(rows, columns=["timestamp", *COLUMNS]).set_index("timestamp")


# ---------------------------------------------------------------- dispatcher

def add_data_args(parser, interval: str = "5m", days: int = 60, single: bool = True) -> None:
    g = parser.add_argument_group("market data")
    g.add_argument("--source", choices=SOURCES, default="auto",
                   help="where bars come from (auto: --csv, then Alpaca keys, then yfinance)")
    if single:
        g.add_argument("--csv", help="CSV/JSON of OHLCV bars (any common column names)")
    g.add_argument("--csv-dir", help="directory of <SYMBOL>.csv files")
    g.add_argument("--interval", default=interval, help=f"bar size (default {interval})")
    g.add_argument("--days", type=int, default=days, help=f"calendar days of history (default {days})")
    g.add_argument("--tz", default=DEFAULT_TZ, help="exchange time zone")
    g.add_argument("--save-data", help="also write the bars that were used to this CSV path")


def resolve_source(source: str, csv_path: str | None = None, csv_dir: str | None = None) -> str:
    if source != "auto":
        return source
    if csv_path or csv_dir:
        return "csv"
    if alpaca_configured():
        return "alpaca"
    try:
        _yf()
        return "yfinance"
    except DataError:
        pass
    raise DataError(
        "no market data source available. Options: pass --csv bars.csv (export from your broker, "
        "or have Claude save bars from a market-data connector), set ALPACA_API_KEY_ID + "
        "ALPACA_API_SECRET_KEY, pip install yfinance, or use --source demo to try the skill on fake data."
    )


def get_bars(symbol: str, source: str = "auto", interval: str = "5m", days: int = 60,
             csv: str | None = None, csv_dir: str | None = None, tz: str = DEFAULT_TZ,
             prepost: bool = False, demo_today_until: time | None = None) -> pd.DataFrame:
    src = resolve_source(source, csv, csv_dir)
    mins = interval_minutes(interval)
    if src == "csv":
        path = csv or (Path(csv_dir) / f"{symbol}.csv" if csv_dir else None)
        if path is None:
            raise DataError("--source csv needs --csv FILE or --csv-dir DIR")
        df = load_csv(path, tz)
    elif src == "yfinance":
        df = fetch_yfinance(symbol, interval, days, prepost=prepost, tz=tz)
    elif src == "alpaca":
        df = fetch_alpaca(symbol, interval, days, tz=tz)
    elif src == "relay":
        df = fetch_relay(symbol, tz=tz)
    elif src == "demo":
        if mins >= 1440:
            df = synthetic_daily(symbol, days=max(30, int(days * 252 / 365)), tz=tz)
        else:
            df = synthetic_intraday(symbol, days=max(2, int(days * 5 / 7)), interval=mins, tz=tz,
                                    today_until=demo_today_until or time(11, 0), premarket=prepost)
    else:  # pragma: no cover - argparse restricts choices
        raise DataError(f"unknown source {src}")
    if src in ("csv", "relay") and mins < 1440:
        native = infer_interval_minutes(df)
        if native < mins:
            df = resample(df, mins)
    if src == "csv" and mins >= 1440 and infer_interval_minutes(df) < 1440:
        df = to_daily(df)
    df.attrs["source"] = src
    df.attrs["symbol"] = symbol
    return df


def daily_for(args, symbol: str, intraday: pd.DataFrame | None = None, session=None,
              days: int = 400) -> pd.DataFrame:
    """Daily bars to go with intraday ones.

    CSV, relay and demo intraday data is rolled up (regular session only) so the
    two always agree; yfinance and Alpaca fetch real daily history.
    """
    src = resolve_source(args.source, getattr(args, "csv", None), getattr(args, "csv_dir", None))
    if src in ("csv", "relay", "demo") and intraday is not None:
        from .session import rth  # noqa: PLC0415

        part = rth(intraday, session) if session is not None else intraday
        return to_daily(part if len(part) else intraday)
    return get_bars(symbol, source=src, interval="1d", days=days, tz=args.tz)


def bars_from_args(args, symbol: str, interval: str | None = None, days: int | None = None,
                   prepost: bool = False, demo_today_until: time | None = None) -> pd.DataFrame:
    df = get_bars(
        symbol,
        source=args.source,
        interval=interval or args.interval,
        days=days or args.days,
        csv=getattr(args, "csv", None),
        csv_dir=getattr(args, "csv_dir", None),
        tz=args.tz,
        prepost=prepost,
        demo_today_until=demo_today_until,
    )
    if getattr(args, "save_data", None):
        save_csv(df, args.save_data)
    return df
