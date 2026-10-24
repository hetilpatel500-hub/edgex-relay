from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from conftest import make_day

from tradekit import exits, levels as lv, signals as sg
from tradekit.data import to_daily


def test_floor_pivots():
    piv = {x.kind: x.price for x in lv.floor_pivots(110, 100, 105)}
    assert piv["P"] == pytest.approx(105)
    assert piv["R1"] == pytest.approx(110) and piv["S1"] == pytest.approx(100)
    assert piv["R2"] == pytest.approx(115) and piv["S2"] == pytest.approx(95)


def test_volume_profile_finds_heavy_price():
    idx = pd.date_range("2026-10-20 09:30", periods=40, freq="5min", tz="America/New_York")
    px = np.r_[np.full(30, 50.0), np.linspace(51, 55, 10)]
    df = pd.DataFrame({"open": px, "high": px + 0.05, "low": px - 0.05, "close": px, "volume": 1000.0}, index=idx)
    vp = lv.volume_profile(df)
    assert vp["poc"] == pytest.approx(50.0, abs=0.2)
    assert vp["val"] <= 50.0 <= vp["vah"]


def test_merge_does_not_chain_far_levels():
    levels = [lv.Level(100 + 0.2 * i, "X", "x", 2) for i in range(10)]
    merged = lv.merge(levels, tol=0.25)
    assert len(merged) >= 4
    assert max(m.price for m in merged) >= 101.6  # the top of the chain survives as its own level


def test_prior_day_skips_partial_today():
    days = [make_day(date(2026, 10, 19), [100, 102, 101]), make_day(date(2026, 10, 20), [105, 106, 104])]
    daily = to_daily(pd.concat(days))
    got = {x.kind: x.price for x in lv.prior_day(daily, date(2026, 10, 20))}
    assert got["PDC"] == 101 and got["PDH"] == pytest.approx(102.05)


def _history(n_days=10, base=100.0):
    rng = np.random.default_rng(4)
    frames = []
    for i in range(n_days):
        d = date(2026, 10, 1) + timedelta(days=i)
        frames.append(make_day(d, base + np.cumsum(rng.normal(0, 0.05, 78)), volume=1000.0))
    return frames


def test_orb_breakout_triggers(session):
    hist = _history()
    # today: tight 15-minute range 100-100.3, then a strong breakout on heavy volume
    closes = [100.1, 100.2, 100.15] + list(np.linspace(100.5, 101.5, 9))
    today = make_day(date(2026, 10, 20), closes, spread=0.05)
    today["volume"] = [1000] * 3 + [5000] * 9
    df = pd.concat(hist + [today])
    ctx = sg.build_context(df, session, 5, to_daily(df))
    sigs = {(s.name, s.side): s for s in sg.evaluate(ctx, ["orb"], 15)}
    long_ = sigs[("ORB15", "long")]
    assert long_.status == "triggered"
    assert long_.trigger == pytest.approx(max(today["high"].iloc[:3]))
    assert long_.stop < long_.trigger
    assert any("volume" in r for r in long_.reasons)


def test_vwap_reclaim_armed_then_triggered(session):
    hist = _history()
    below = list(np.linspace(100, 99, 8))
    today = make_day(date(2026, 10, 20), below)
    df = pd.concat(hist + [today])
    ctx = sg.build_context(df, session, 5, to_daily(df))
    longs = [s for s in sg.vwap_reclaim(ctx) if s.side == "long"]
    assert longs and longs[0].status == "armed"
    today2 = make_day(date(2026, 10, 20), below + [99.6, 100.4])
    df2 = pd.concat(hist + [today2])
    ctx2 = sg.build_context(df2, session, 5, to_daily(df2))
    longs2 = [s for s in sg.vwap_reclaim(ctx2) if s.side == "long"]
    assert longs2 and longs2[0].status == "triggered"


def test_exit_plan_targets_snap_to_levels():
    levels = [lv.Level(101.5, "PDH", "prior day high", 4), lv.Level(99.2, "PDL", "prior day low", 4)]
    plan = exits.plan_exits("long", 100.0, None, levels, daily_atr=4.0, bar_atr=0.3)
    assert plan.stop == pytest.approx(99.2 - 0.2)  # just under PDL by 0.05 ATR
    assert plan.targets[0]["price"] < 101.5 and "prior day high" in plan.targets[0]["reason"]
    assert plan.targets[0]["r"] >= 1.0
    assert plan.breakeven_after == 1
    with pytest.raises(ValueError):
        exits.plan_exits("long", 100.0, 101.0)


def test_exit_plan_single_style_uses_2r():
    plan = exits.plan_exits("short", 50.0, 50.5, [], style="single")
    assert len(plan.targets) == 1 and plan.targets[0]["price"] == pytest.approx(49.0)
    assert plan.trail_r is None
