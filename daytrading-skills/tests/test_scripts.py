"""Every skill script runs end to end on demo data or a CSV."""

import json
from datetime import date, timedelta

import numpy as np
import pandas as pd
import pytest
from conftest import make_day


def test_every_skill_has_a_script_and_frontmatter():
    from conftest import ROOT

    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert len(skills) == 11
    for s in skills:
        text = (s / "SKILL.md").read_text()
        assert text.startswith("---\nname: " + s.name + "\ndescription: ")
        assert "${CLAUDE_SKILL_DIR}/scripts/" in text
        for script in (s / "scripts").glob("*.py"):
            assert f"scripts/{script.name}" in text, f"{s.name} does not mention {script.name}"


@pytest.mark.parametrize("rel,args", [
    ("skills/time-machine/scripts/time_machine.py",
     ["--source", "demo", "--side", "long", "--stop-pct", "0.5", "--rr", "2", "--sims", "2000", "--seed", "1"]),
    ("skills/key-levels/scripts/levels.py", ["--source", "demo", "--symbol", "DEMO"]),
    ("skills/entry-signal/scripts/entry_signal.py", ["--source", "demo", "--symbol", "DEMO", "--interval", "5m"]),
    ("skills/exit-planner/scripts/exit_planner.py", ["--source", "demo", "--symbol", "DEMO", "--side", "short"]),
    ("skills/chart-scanner/scripts/scan.py", ["--source", "demo", "--tickers", "AAA,BBB,CCC,DDD", "--top", "3"]),
    ("skills/market-regime/scripts/regime.py", ["--source", "demo"]),
    ("skills/premarket-game-plan/scripts/premarket.py", ["--source", "demo", "--tickers", "AAA,BBB"]),
    ("skills/position-sizer/scripts/position_sizer.py", ["--account", "25000", "--entry", "50", "--stop", "49.5"]),
])
def test_scripts_run(run_script, tmp_path, rel, args):
    r = run_script(rel, *args, env={"DAYTRADING_HOME": str(tmp_path)})
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip()


def test_time_machine_json_and_html(run_script, tmp_path):
    html = tmp_path / "tm.html"
    r = run_script("skills/time-machine/scripts/time_machine.py", "--source", "demo", "--side", "short",
                   "--stop-pct", "0.4", "--target", "99,98", "--sims", "1000", "--seed", "2", "--json",
                   "--html", str(html), "--no-robustness")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    sim = out["simulation"]
    assert sim["paths"] == 1000
    total = sim["p_target"] + sim["p_stop"] + sim["p_partial_then_stop"] + sim["p_time_exit"]
    assert total == pytest.approx(1.0)
    assert html.read_text().startswith("<!doctype html>")


def test_time_machine_past_date_uses_no_future_data(run_script, tmp_path):
    rng = np.random.default_rng(11)
    frames = [make_day(date(2026, 9, 1) + timedelta(days=i), 100 + np.cumsum(rng.normal(0, 0.1, 78)))
              for i in range(30)]
    bars = pd.concat(frames)
    csv = tmp_path / "bars.csv"
    bars.to_csv(csv, index_label="timestamp")
    test_day = date(2026, 9, 21)
    entry = float(bars[bars.index.date == test_day]["close"].iloc[11])
    r = run_script("skills/time-machine/scripts/time_machine.py", "--csv", str(csv), "--symbol", "TEST",
                   "--side", "long", "--entry", str(entry), "--stop", str(entry - 0.4), "--rr", "2",
                   "--date", str(test_day), "--time", "10:30", "--sims", "500", "--json", "--no-robustness")
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout)
    assert out["history"]["days"] == 20  # only the sessions before the test day
    assert out["history"]["last"] == "2026-09-20"
    assert out["actual_outcome"] is not None


def test_exit_plan_feeds_time_machine(run_script, tmp_path):
    plan = tmp_path / "plan.json"
    r = run_script("skills/exit-planner/scripts/exit_planner.py", "--source", "demo", "--symbol", "DEMO",
                   "--side", "long", "--emit-plan", str(plan))
    assert r.returncode == 0, r.stderr
    r = run_script("skills/time-machine/scripts/time_machine.py", "--source", "demo", "--plan", str(plan),
                   "--sims", "500", "--no-robustness")
    assert r.returncode == 0, r.stderr
    assert "Hit every target" in r.stdout


def test_journal_and_risk_guard_cli(run_script, tmp_path):
    env = {"DAYTRADING_HOME": str(tmp_path)}
    j = "skills/trade-journal/scripts/journal.py"
    g = "skills/risk-guard/scripts/risk_guard.py"
    assert run_script(g, "init", "--account", "20000", env=env).returncode == 0
    r = run_script(j, "add", "--symbol", "AAPL", "--side", "long", "--entry", "100", "--exit", "101",
                   "--shares", "10", "--stop", "99", "--setup", "ORB", env=env)
    assert r.returncode == 0 and "+1.00R" in r.stdout
    r = run_script(j, "stats", env=env)
    assert r.returncode == 0 and "1 closed trades" in r.stdout
    r = run_script(g, "check", "--entry", "50", "--stop", "49", "--shares", "1000", "--time", "11:00", env=env)
    assert r.returncode == 1 and "BLOCKED" in r.stdout  # $1,000 risk > 1% of $20k


def test_missing_data_source_message(run_script, tmp_path):
    r = run_script("skills/key-levels/scripts/levels.py", "--symbol", "X", "--source", "csv",
                   "--csv", str(tmp_path / "nope.csv"))
    assert r.returncode == 2 and "CSV not found" in r.stderr
