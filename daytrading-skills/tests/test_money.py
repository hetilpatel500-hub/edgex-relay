from datetime import datetime

import pytest

from tradekit import journal as jr, risk as rk
from tradekit.sizing import contract_point_value, size_position


def test_size_by_risk():
    r = size_position(30_000, 187.5, 186.2, risk_pct=1, max_position_pct=None)
    assert r["units"] == 230 and r["binding_constraint"] == "risk budget"
    assert r["risk_total"] == pytest.approx(230 * 1.3)
    capped = size_position(30_000, 187.5, 186.2, risk_pct=1)  # default: no bigger than the account
    assert capped["units"] == 160 and capped["binding_constraint"] == "max position size"


def test_size_capped_by_account_and_buying_power():
    r = size_position(10_000, 100, 99.9, risk_pct=1)
    assert r["binding_constraint"] == "max position size" and r["units"] == 100
    r = size_position(10_000, 100, 99.9, risk_pct=1, max_position_pct=None, buying_power=40_000)
    assert r["units"] == 400


def test_futures_sizing_and_costs():
    r = size_position(10_000, 6012.25, 6006.75, risk_pct=1, point_value=5, commission_per_unit=0.62)
    assert r["units"] == int(100 // (5.5 * 5 + 1.24))
    assert contract_point_value("MESZ6") == 5 and contract_point_value("MES=F") == 5
    assert contract_point_value("CL") is None and contract_point_value("ES") is None  # stocks
    assert contract_point_value("/ES") == 50


def test_zero_units_warns():
    r = size_position(1_000, 100, 90, risk_pct=0.5)
    assert r["units"] == 0 and r["warnings"]


def _journal(tmp_path, trades):
    p = tmp_path / "j.csv"
    for t in trades:
        jr.add(p, **t)
    return p


def test_journal_pnl_r_and_stats(tmp_path):
    p = _journal(tmp_path, [
        dict(symbol="AAPL", side="long", entry=100, exit=102, shares=10, stop=99, setup="ORB",
             entry_time="2026-10-20 09:45", exit_time="2026-10-20 10:15", predicted_win=0.6),
        dict(symbol="TSLA", side="short", entry=200, exit=202, shares=5, stop=202, setup="VWAP",
             entry_time="2026-10-20 10:30", exit_time="2026-10-20 10:45", fees=1.0, predicted_win=0.4),
    ])
    df = jr.load(p)
    assert list(df["pnl"]) == [20.0, -11.0]
    assert df["r"].iloc[0] == pytest.approx(2.0)
    s = jr.stats(df)
    assert s["overall"]["trades"] == 2 and s["overall"]["win_rate"] == 0.5
    assert s["by_setup"]["ORB"]["total_pnl"] == 20.0


def test_journal_open_close(tmp_path):
    p = tmp_path / "j.csv"
    tid = jr.add(p, symbol="NVDA", side="long", entry=50, shares=100, stop=49, entry_time="2026-10-20 11:00")
    assert jr.load(p)["status"].iloc[0] == "open"
    jr.close(p, tid, 51.5, "2026-10-20 11:30")
    row = jr.load(p).iloc[0]
    assert row["status"] == "closed" and row["pnl"] == 150 and row["r"] == pytest.approx(1.5)
    with pytest.raises(ValueError):
        jr.close(p, tid, 52, "2026-10-20 12:00")


def test_risk_guard_blocks_after_daily_loss(tmp_path):
    p = _journal(tmp_path, [
        dict(symbol="A", side="long", entry=10, exit=9, shares=300, stop=9, entry_time="2026-10-20 09:40",
             exit_time="2026-10-20 09:50"),
        dict(symbol="B", side="long", entry=10, exit=9, shares=300, stop=9, entry_time="2026-10-20 10:00",
             exit_time="2026-10-20 10:10"),
    ])
    cfg = dict(rk.DEFAULTS, account_size=20_000, max_daily_loss_pct=3)
    st = rk.day_state(jr.load(p), datetime(2026, 10, 20).date())
    assert st.realized == -600 and st.consecutive_losses == 2
    res = rk.check(cfg, st, datetime(2026, 10, 20, 11, 0), entry=50, stop=49, shares=50)
    assert res["verdict"] == "BLOCKED"
    assert any("daily loss limit" in b for b in res["blocked"])


def test_risk_guard_cooldown_windows_and_clear(tmp_path):
    cfg = dict(rk.DEFAULTS, account_size=50_000, max_consecutive_losses=2, cooldown_minutes=30)
    p = _journal(tmp_path, [
        dict(symbol="A", side="long", entry=10, exit=9.9, shares=100, stop=9.9, entry_time="2026-10-20 09:40",
             exit_time="2026-10-20 09:50"),
        dict(symbol="B", side="long", entry=10, exit=9.9, shares=100, stop=9.9, entry_time="2026-10-20 10:00",
             exit_time="2026-10-20 10:10"),
    ])
    st = rk.day_state(jr.load(p), datetime(2026, 10, 20).date())
    blocked = rk.check(cfg, st, datetime(2026, 10, 20, 10, 20), entry=50, stop=49.5, shares=100, target=51)
    assert blocked["verdict"] == "BLOCKED" and any("cooldown" in b for b in blocked["blocked"])
    later = rk.check(cfg, st, datetime(2026, 10, 20, 11, 0), entry=50, stop=49.5, shares=100, target=51)
    assert later["verdict"] == "CAUTION"
    window = rk.check(cfg, rk.DayState(st.day), datetime(2026, 10, 20, 9, 31), entry=50, stop=49.5, shares=100)
    assert any("no-trade window" in b for b in window["blocked"])
    clear = rk.check(cfg, rk.DayState(st.day), datetime(2026, 10, 20, 10, 0), entry=50, stop=49.5, shares=100,
                     target=51.5, side="long")
    assert clear["verdict"] == "CLEAR" and clear["trade"]["max_units_allowed"] == 1000


def test_risk_guard_requires_stop_and_caps_size():
    cfg = dict(rk.DEFAULTS, account_size=10_000)
    st = rk.DayState(datetime(2026, 10, 20).date())
    assert rk.check(cfg, st, datetime(2026, 10, 20, 10), entry=50)["verdict"] == "BLOCKED"
    res = rk.check(cfg, st, datetime(2026, 10, 20, 10), entry=50, stop=49, shares=500)
    assert res["verdict"] == "BLOCKED" and res["trade"]["max_units_allowed"] == 100
