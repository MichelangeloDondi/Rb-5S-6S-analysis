"""Every condition whitens by ITS OWN post-fit residual time, and this refuses a silent fallback.

WHY THIS EXISTS (F186, 2026-09-19). Twelve of the thirty-two conditions were whitened by the raw-segment
correlation time instead of their own post-fit one: 14.080 against a post-fit 0.950 at peak 4154 and 110 C.
The cause was one line. `noise_law_for` built its lookup key with `_tau_key_of_row`, which needs the row's
power, and the t_sweep rows carry a BLANK power, as that function's own docstring says. The key came back
None, `effective_tau` took its documented fallback, and every temperature-arm condition kept the raw time.

WHY IT MATTERS MORE THAN A WRONG NUMBER. The weight of a condition goes as one over its time, so the
twelve were down-weighted by between 1.7 and 14.8 relative to the rest. That moves the ESTIMATES and not
only the bars, and the twelve are the whole temperature arm, which is the axis that separates the transit
width from the laser width. The arm's share of the total information was 16.3 per cent and is 37.1.

WHY NOTHING CAUGHT IT. `effective_tau` prints its reason once per process and returns a documented
fallback, which is correct behaviour for a law built for a condition outside the record. Nothing asserted
that a condition INSIDE the record never takes that branch. A fallback with no guard over the population
that must never reach it is a silent default, and this is that guard.

THE FALSE-PASS DIRECTION, stated first: green means every committed condition's law carries the post-fit
time. It does not mean that time is right -- the Sokal estimate and its floor are graded elsewhere -- nor
that any other producer whitens the same way.
"""
from __future__ import annotations

import csv
from pathlib import Path

from conftest import load_script_module        # noqa: E402

from rb5s6s import config as C

ROOT = Path(__file__).resolve().parents[1]


def _rows():
    with (C.RESULTS_DIR / "noise_model.csv").open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _uj():
    return load_script_module("run_ultra_joint", ROOT / "scripts" / "run_ultra_joint.py")


def test_every_committed_condition_whitens_by_its_own_post_fit_time():
    """The exact defect of F186, at the real call path and not at a helper."""
    uj = _uj()
    rows, table = _rows(), uj.tau_resid_table()
    assert table, "no post-fit residual times at all: this test would pass vacuously"
    offenders = []
    for r in rows:
        T = float(r["temperature_C"])
        # the t_sweep rows carry a blank power and ARE the case that broke; 225 mW is their condition
        P_mW = 225.0 if r["power_mW"] == "" else float(r["power_mW"])
        key = uj._tau_key(r["peak"], T, P_mW / 1e3)
        if key not in table:
            continue                              # outside the post-fit population: the fallback is right
        want = max(float(table[key]), 1.0)
        got = float(uj.noise_law_for(rows, r["role"], r["peak"], T, P_mW)["tau_eff"])
        if abs(got - want) > 1e-9:
            offenders.append(f"{key} (role {r['role']}): whitens by {got:.4f}, its post-fit time is {want:.4f}")
    assert not offenders, (
        "conditions inside the post-fit population took the raw-time fallback, which re-weights them "
        "against the rest and moves the estimates (F186):\n  " + "\n  ".join(offenders))


def test_the_blank_power_rows_are_really_in_the_population_this_guards():
    """The check on the check: if the t_sweep rows ever stop being blank, the guard above still passes
    while no longer exercising the case it was written for, and it would say nothing about it."""
    rows = _rows()
    blank = [r for r in rows if r["power_mW"] == ""]
    assert blank, ("no row carries a blank power any more, so the guard above no longer exercises F186's "
                   "own case; re-read it before trusting it")
    uj = _uj()
    assert all(uj._tau_key_of_row(r) is None for r in blank), (
        "a blank-power row now yields a key from the ROW, so `_tau_key_of_row` has changed and the "
        "caller-side key this guard checks may no longer be the thing under test")


def test_a_broken_key_is_caught(monkeypatch):
    """PLANTED BOTH WAYS. With the key builder returning None, as it did for twelve conditions, the
    first test must FAIL; this asserts the guard has the discrimination it claims."""
    uj = _uj()
    rows, table = _rows(), uj.tau_resid_table()
    monkeypatch.setattr(uj, "_tau_key", lambda *a, **k: None)
    fell_back = []
    for r in rows:
        T = float(r["temperature_C"])
        P_mW = 225.0 if r["power_mW"] == "" else float(r["power_mW"])
        law = uj.noise_law_for(rows, r["role"], r["peak"], T, P_mW)
        key = f"{r['peak']}_{T:.0f}C_{P_mW:.0f}mW"
        if key in table and abs(float(law["tau_eff"]) - max(float(table[key]), 1.0)) > 1e-9:
            fell_back.append(key)
    assert fell_back, ("with the key builder broken NOTHING fell back to the raw time, so the guard above "
                       "cannot see the defect it was written for and is a no-op")
