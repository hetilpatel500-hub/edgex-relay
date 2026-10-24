"""One test per bug found in review, so they stay fixed."""

from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from conftest import make_day

from tradekit import data as dt, journal as jr, montecarlo as mc, risk as rk, signals as sg
from tradekit.session import Session


def test_csv_spanning_dst_loads(tmp_path):
    # offsets change from -04:00 to -05:00 on 2025-11-02
    bars = pd.concat([make_day(date(2025, 10, 30) + timedelta(days=i), [100, 101]) for i in range(6)])
    p = tmp_path / "bars.csv"
    dt.save_csv(bars, p)
    back = dt.load_csv(p)
    assert len(back) == len(bars)
    assert back.index[0].hour == 9 and back.index[-1].hour == 9  # still 09:30 local on both sides


def test_journal_accepts_offset_and_naive_times(tmp_path):
    p = tmp_path / "j.csv"
    jr.add(p, symbol="A", side="long", entry=10, exit=11, shares=1, stop=9,
           entry_time="2026-10-23 10:00", exit_time="2026-10-23 10:30")
    jr.add(p, symbol="B", side="long", entry=10, exit=11, shares=1, stop=9,
           entry_time="2026-10-23T14:40Z", exit_time="2026-10-23T11:00:00-04:00")
    df = jr.load(p)
    assert list(df["entry_time"].dt.strftime("%H:%M")) == ["10:00", "10:40"]
    assert df["hold_min"].iloc[1] == 20


def test_long_with_stop_above_entry_is_blocked_without_target():
    st = rk.DayState(date(2026, 10, 20))
    res = rk.check(dict(rk.DEFAULTS), st, datetime(2026, 10, 20, 10), entry=50, stop=51, shares=100, side="long")
    assert res["verdict"] == "BLOCKED"


def test_max_size_respects_open_risk_cap():
    cfg = dict(rk.DEFAULTS, account_size=12_500, max_total_open_risk_pct=3.0)  # cap 375
    st = rk.DayState(date(2026, 10, 20), open_risk=300.0, open_positions=1)
    res = rk.check(cfg, st, datetime(2026, 10, 20, 10), entry=50, stop=49.5, shares=1)
    allowed = res["trade"]["max_units_allowed"]
    assert allowed == 150  # (375 cap - 300 open) / 0.5, tighter than the 125/0.5 = 250 per-trade limit
    again = rk.check(cfg, st, datetime(2026, 10, 20, 10), entry=50, stop=49.5, shares=allowed)
    assert not any("open risk" in b for b in again["blocked"])


def _ctx(today_df, prior_close=100.0):
    hist = make_day(date(2026, 10, 19), np.full(78, prior_close))
    df = pd.concat([hist, today_df])
    return sg.build_context(df, Session(), 5)


def test_red_to_green_stop_sits_below_trigger():
    closes = [99.0, 99.5, 100.4, 101.5, 102.5, 103, 104, 105, 106, 107]
    ctx = _ctx(make_day(date(2026, 10, 20), closes, opens=[98.8] + closes[:-1]))
    sig = next(s for s in sg.red_to_green(ctx) if s.side == "long")
    assert sig.status == "triggered" and sig.when == "09:40"
    assert sig.stop < sig.trigger == 100.0


def test_red_to_green_on_first_bar():
    ctx = _ctx(make_day(date(2026, 10, 20), [101.0, 101.5, 102.0], opens=[99.0, 101.0, 101.5]))
    sig = next(s for s in sg.red_to_green(ctx) if s.side == "long")
    assert sig.status == "triggered" and sig.when == "09:30" and sig.stop < 100


def test_separate_date_and_time_columns():
    raw = pd.DataFrame({"Date": ["2026-10-20"] * 3, "Time": ["09:30", "09:35", "09:40"],
                        "Open": [1, 2, 3], "High": [1, 2, 3], "Low": [1, 2, 3], "Close": [1, 2, 3]})
    df = dt.normalize(raw)
    assert len(df) == 3 and df.index[-1].minute == 40


def test_hourly_resample_keeps_the_open():
    day = make_day(date(2026, 10, 20), np.linspace(100, 101, 78))
    hourly = dt.resample(day, 60)
    assert hourly.index[0].strftime("%H:%M") == "09:30"
    assert hourly["open"].iloc[0] == day["open"].iloc[0]
    assert hourly["volume"].sum() == day["volume"].sum()


def test_excursions_stop_at_the_exit():
    # up bar touching the stop first: price went to 102.5 only after the trade was stopped
    closes = np.r_[100.0, 101.5, np.full(76, 101.5)]
    bars = make_day(date(2026, 10, 20), closes, opens=np.r_[100, 100, np.full(76, 101.5)],
                    highs=np.r_[100, 102.5, np.full(76, 101.55)], lows=np.r_[100, 98.9, np.full(76, 101.45)])
    bank = mc.build_bank(pd.concat([bars] * 1), Session(), 5)
    plan = mc.TradePlan("long", 100, 99, [mc.Target(103, 1.0)])
    res = mc.simulate(bank, plan, 1, 77, n_sims=20, seed=0)
    assert (res.outcome == mc.STOP).all()
    assert res.mfe.max() == pytest.approx(0.0)
    assert mc.summarize(res)["p_full_loss_after_1r_open_profit"] == 0


def test_integer_prices_do_not_truncate_trailing_stop():
    closes = np.r_[np.linspace(100.0, 102, 10), np.linspace(101.9, 101.6, 10), np.full(58, 101.0)]
    bank = mc.build_bank(make_day(date(2026, 10, 20), closes, spread=0.01), Session(), 5)
    plan = mc.TradePlan("long", 100, 99, [], trail_r=0.25, slippage=0)
    res = mc.simulate(bank, plan, 0, 77, n_sims=5, seed=0)
    assert (res.outcome == mc.STOP).all()
    assert res.pnl == pytest.approx(np.full(5, 1.76), abs=0.02)  # trailed at ~101.76, not 101
