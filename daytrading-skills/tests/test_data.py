import json

import pandas as pd
import pytest

from tradekit import data as dt


def test_normalize_aliases_and_naive_times():
    raw = pd.DataFrame({"Date": ["2026-10-20 09:30", "2026-10-20 09:31"], "O": [1, 2], "H": [2, 3],
                        "L": [0.5, 1.5], "C": [1.5, 2.5], "Vol": [100, 200]})
    df = dt.normalize(raw)
    assert list(df.columns) == dt.COLUMNS
    assert str(df.index.tz) == dt.DEFAULT_TZ
    assert df.index[0].hour == 9 and df.index[0].minute == 30


@pytest.mark.parametrize("scale", [1, 1_000, 1_000_000_000])
def test_normalize_epoch_units(scale):
    t0 = 1_760_967_000  # 2025-10-20 13:30 UTC
    raw = pd.DataFrame({"t": [t0 * scale, (t0 + 60) * scale], "o": [1, 1], "h": [1, 1], "l": [1, 1], "c": [1, 1]})
    df = dt.normalize(raw)
    assert df.index[0].tz_convert("UTC").hour == 13
    assert (df["volume"] == 0).all()


def test_normalize_repairs_high_low_and_dedupes():
    raw = pd.DataFrame({"timestamp": ["2026-10-20T13:30:00Z"] * 2 + ["2026-10-20T13:31:00Z"],
                        "open": [10, 10, 10], "high": [9, 9, 9], "low": [11, 11, 11], "close": [10.5, 10.6, 10.2]})
    df = dt.normalize(raw)
    assert len(df) == 2
    assert (df["high"] >= df[["open", "close"]].max(axis=1)).all()
    assert (df["low"] <= df[["open", "close"]].min(axis=1)).all()
    assert df["close"].iloc[0] == 10.6  # last duplicate wins


def test_load_csv_and_json(tmp_path):
    p = tmp_path / "bars.csv"
    p.write_text("time,open,high,low,close,volume\n2026-10-20 09:30,1,2,0.5,1.5,10\n")
    assert len(dt.load_csv(p)) == 1
    j = tmp_path / "bars.json"
    j.write_text(json.dumps({"bars": [{"ts": "2026-10-20T13:30:00+00:00", "open": 1, "high": 2, "low": 1,
                                       "close": 2, "volume": 5}]}))
    assert dt.load_csv(j)["close"].iloc[0] == 2


def test_resample_and_interval():
    idx = pd.date_range("2026-10-20 09:30", periods=10, freq="1min", tz=dt.DEFAULT_TZ)
    df = pd.DataFrame({"open": range(10), "high": range(1, 11), "low": range(10), "close": range(10),
                       "volume": [1] * 10}, index=idx).astype(float)
    assert dt.infer_interval_minutes(df) == 1
    r = dt.resample(df, 5)
    assert len(r) == 2 and r["volume"].iloc[0] == 5 and r["high"].iloc[0] == 5 and r["open"].iloc[1] == 5
    assert dt.interval_minutes("15m") == 15 and dt.interval_minutes("1h") == 60 and dt.interval_minutes("1d") == 1440


def test_relay_fetch_reverses_newest_first(monkeypatch):
    monkeypatch.setenv("RELAY_URL", "https://relay.example")
    monkeypatch.setenv("RELAY_API_KEY", "k")
    seen = {}

    def fake(url, headers):
        seen["url"], seen["headers"] = url, headers
        return {"bars": [{"ts": "2026-10-20T13:31:00+00:00", "open": 2, "high": 2, "low": 2, "close": 2, "volume": 1},
                         {"ts": "2026-10-20T13:30:00+00:00", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]}

    df = dt.fetch_relay("MESZ6", http=fake)
    assert seen["headers"] == {"X-API-Key": "k"} and "symbol=MESZ6" in seen["url"]
    assert list(df["close"]) == [1.0, 2.0]


def test_alpaca_paginates(monkeypatch):
    monkeypatch.setenv("ALPACA_API_KEY_ID", "id")
    monkeypatch.setenv("ALPACA_API_SECRET_KEY", "secret")
    pages = iter([
        {"bars": [{"t": "2026-10-20T13:30:00Z", "o": 1, "h": 1, "l": 1, "c": 1, "v": 1}], "next_page_token": "x"},
        {"bars": [{"t": "2026-10-20T13:35:00Z", "o": 2, "h": 2, "l": 2, "c": 2, "v": 2}], "next_page_token": None},
    ])
    urls = []

    def fake(url, headers):
        urls.append(url)
        assert headers["APCA-API-KEY-ID"] == "id"
        return next(pages)

    df = dt.fetch_alpaca("AAPL", "5m", 5, http=fake)
    assert len(df) == 2 and "timeframe=5Min" in urls[0] and "page_token=x" in urls[1]


def test_auto_source_without_anything_explains(monkeypatch):
    monkeypatch.delenv("ALPACA_API_KEY_ID", raising=False)
    monkeypatch.setattr(dt, "_yf", lambda: (_ for _ in ()).throw(dt.DataError("no yf")))
    with pytest.raises(dt.DataError, match="--csv"):
        dt.resolve_source("auto")


def test_synthetic_is_deterministic_and_distinct():
    a = dt.synthetic_daily("AAA", 50)
    b = dt.synthetic_daily("AAA", 50)
    c = dt.synthetic_daily("AAB", 50)
    assert a.equals(b) and not a["close"].equals(c["close"])


class _FakeTicker:
    calls = []

    def __init__(self, sym):
        self.sym = sym

    def history(self, start, end, interval, prepost, auto_adjust, actions):
        _FakeTicker.calls.append((interval, start, end))
        idx = pd.date_range(pd.Timestamp(start).tz_convert("America/New_York"), periods=3, freq="5min",
                            name="Datetime")
        return pd.DataFrame({"Open": [1.0, 2, 3], "High": [1.5, 2.5, 3.5], "Low": [0.5, 1.5, 2.5],
                             "Close": [1.2, 2.2, 3.2], "Volume": [10, 20, 30]}, index=idx)


class _FakeYF:
    Ticker = _FakeTicker

    @staticmethod
    def download(batch, **kw):
        idx = pd.date_range("2026-10-01", periods=5, freq="B", tz="America/New_York", name="Date")
        cols = pd.MultiIndex.from_product([batch, ["Open", "High", "Low", "Close", "Volume"]])
        return pd.DataFrame(1.0, index=idx, columns=cols)


def test_yfinance_shapes(monkeypatch):
    monkeypatch.setattr(dt, "_yf", lambda: _FakeYF)
    _FakeTicker.calls.clear()
    df = dt.fetch_yfinance("AAPL", "1m", 20)
    assert len(_FakeTicker.calls) >= 3  # 1m history is fetched in <=7-day chunks
    assert list(df.columns) == dt.COLUMNS and df.index.tz is not None
    many = dt.fetch_yfinance_many(["AAA", "BBB"], days=10)
    assert set(many) == {"AAA", "BBB"} and len(many["AAA"]) == 5
