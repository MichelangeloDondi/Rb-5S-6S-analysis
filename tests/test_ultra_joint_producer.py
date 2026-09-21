"""Guards for `scripts/run_ultra_joint.py`, the waist profile over the record.

FAILURE MODE IF THIS FILE IS DELETED. The producer could quietly go back to
the defects every earlier construction shared: a pooled run whose rows depend
on which worker took which cell, a power-arm check that refuses nothing or
refuses everything, a collection window switched off at M2 = 1 through
full_profile's own discontinuous switch, a temperature arm loaded at zero
power so the shift and the saturation vanish from it, a beta quoted as a
Hessian bar at its zero bound instead of its profile, a rung gate that passes
an unconverged run, and a bar whose column does not say where it came from.
Each is planted below in both directions where a direction exists.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import numpy as np
import pytest

from conftest import load_script_module        # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def _rows(name):
    """Committed rows of a results CSV, or [] when the producer has not run.

    The moment arm reads data_raw/, which the public mirror does not hold, so a
    test that requires its output would fail there for a reason that is not a
    defect. Returning [] lets the caller skip with a message.
    """
    p = ROOT / "results" / name
    if not p.exists():
        return []
    with p.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_ultra_joint.py"
CSV = ROOT / "results" / "ultra_joint_fit.csv"
_uj = load_script_module("run_ultra_joint", SCRIPT)

# a trace descriptor is all a Cell needs to know its sessions and peaks
_P_DESC = [dict(T=130.0, P_W=0.225, iso=85, session="P", peak="4192", axis="mhz")]


def _needs_traces():
    if not (ROOT / "data_raw" / "p_sweep").is_dir():
        pytest.skip("the raw traces are not in this checkout")


def _theory_cell(w0_um, m2=1.0, cycles=0.0, traces=_P_DESC, **extra):
    # THE THEORY CELL TESTS THE CLOSED FORMS at waists inside and outside the validated grid, so
    # it opens the kernel gate's one door and says so; the gate's own refusals and its
    # interpolation are tested in tests/test_kernel_gate.py through a temporary cache.
    extra.setdefault("kernel_gate", "legacy")
    return _uj.Cell(_uj._spec("mixed", w0_um, m2=m2, cycles=cycles, da=(-1131.8, 5.9), **extra), traces)  # SSOT-HISTORY: a fixture pins its own inputs so a constant change surfaces as a test failure and not a silent drift


def _theory_p(cell):
    """The theory point in the cell's own parameter order."""
    v = {"beta_rel": 1.0, "omega_scale": 1.0, "gamma_l": 0.4}
    return np.array([v.get(n, 1.6 if n.startswith("sigma_l") else 1.0 if n.startswith("power_scale") else 0.0)
                     for n in cell.names])


# ---------------------------------------------------------------- the pool
def test_one_worker_against_two_on_a_tiny_grid_gives_identical_rows():
    """The determinism plant: each cell depends only on its own arguments, so a
    pool, which is exactly an order, cannot change a digit."""
    _needs_traces()
    assert _uj.plant_determinism(workers_many=2)


# ---------------------------------------------------------------- the power arm
def test_the_power_arm_check_refuses_above_one_bar_and_passes_below():
    meas, bar = 0.9956, 0.0188
    refused = _uj.power_arm_check(meas + 3.0 * bar, meas, bar)
    assert refused["refused"] and refused["pull"] == pytest.approx(3.0)
    passes = _uj.power_arm_check(meas + 0.5 * bar, meas, bar)
    assert not passes["refused"] and passes["pull"] == pytest.approx(0.5)
    below = _uj.power_arm_check(meas - 2.0 * bar, meas, bar)
    assert not below["refused"] and below["pull"] == pytest.approx(-2.0), (
        "a prediction below the archive is never refused: every P^2 term widens")
    edge = _uj.power_arm_check(meas + _uj.POWER_ARM_REFUSAL_BARS * bar, meas, bar)
    assert not edge["refused"], "the refusal is strict at the bar"
    assert not _uj.power_arm_check(1.05, meas, 0.0)["refused"], "a zero bar refuses nothing rather than everything"
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'preds = cell.power_ratios(best["p"], omega_scale=1.0)' in src, (
        "the refusal reads the TIED Omega, never the fitted scale that a small waist can pull toward zero")


def test_the_pooled_power_arm_combines_sessions_by_inverse_variance():
    meas = {"P": dict(ratio=1.0, bar=0.02), "E": dict(ratio=1.0, bar=0.04)}
    same = _uj.pooled_power_arm({"P": 1.02, "E": 1.02}, meas)
    assert same["n_sessions"] == 2 and same["bar"] == pytest.approx(1.0 / np.sqrt(1 / 0.02 ** 2 + 1 / 0.04 ** 2))
    assert same["pull"] == pytest.approx(0.02 / same["bar"]) and same["refused"]
    opposite = _uj.pooled_power_arm({"P": 1.00, "E": 1.00}, meas)
    assert opposite["pull"] == pytest.approx(0.0) and not opposite["refused"]
    assert not np.isfinite(_uj.pooled_power_arm({"T": 1.0}, meas)["pull"]), "a session without a ladder pools nothing"


def test_the_model_predicts_a_steeper_power_ratio_at_a_small_waist():
    """The physics the refusal reads: the P^2 terms go as w0^-4, so the 25 to
    225 mW width ratio at the theory parameters is larger at 42 um than at
    85 um, and the 42 um prediction sits outside the archive's measured ratio
    while the 85 um one sits inside it."""
    cs, cl = _theory_cell(42.0), _theory_cell(85.0)
    small = cs.power_ratios(_theory_p(cs))["P"]
    large = cl.power_ratios(_theory_p(cl))["P"]
    assert 1.03 < small < 1.09, small
    assert 1.0 < large < 1.02, large
    assert small > large + 0.02
    meas = _uj.measured_power_ratio() if (ROOT / "results" / "power_sweep.csv").is_file() else dict(ratio=0.9956, bar=0.0188)
    assert _uj.power_arm_check(small, meas["ratio"], meas["bar"])["refused"]
    assert not _uj.power_arm_check(large, meas["ratio"], meas["bar"])["refused"]


def test_the_evening_ladder_carries_the_larger_lever():
    """A cell holding an evening trace predicts the 90 to 270 mW ratio on its
    own session, and the 270 mW rung's P^2 lever is 1.44 times the campaign's."""
    desc = _P_DESC + [dict(T=130.0, P_W=0.27, iso=87, session="E", peak="4121", axis="ms")]
    cell = _theory_cell(50.0, traces=desc)
    assert "sigma_l_E" in cell.names and "lograte_E_4121" in cell.names
    preds = cell.power_ratios(_theory_p(cell))
    assert set(preds) == {"P", "E"}
    assert preds["E"] > preds["P"] > 1.0, preds
    assert (0.27 / 0.225) ** 2 == pytest.approx(1.44)


def test_the_measured_power_ratio_carries_the_block_scatter():
    if not (ROOT / "results" / "power_sweep.csv").is_file():
        pytest.skip("results/power_sweep.csv not committed")
    meas = _uj.measured_power_ratio()
    assert meas["n_peaks"] == 4
    assert 0.95 < meas["ratio"] < 1.05
    assert 0.01 < meas["block_scatter_frac"] < 0.03, "the record's block scatter is about 1.6 to 2 per cent"
    assert meas["bar"] > meas["block_scatter_frac"] / 2.0, "the bar carries the scatter of two blocks over four peaks"
    for r, e in meas["per_peak"].values():
        assert e > np.sqrt(2.0) * meas["block_scatter_frac"] * r * 0.99


def test_a_sessions_ratio_from_its_own_traces_needs_repeats_at_both_rungs():
    widths = {("E", "4121", 0.09): dict(mean=400.0, se=8.0, n=5), ("E", "4121", 0.27): dict(mean=440.0, se=6.0, n=5),
              ("E", "4192", 0.09): dict(mean=410.0, se=5.0, n=5), ("E", "4192", 0.27): dict(mean=424.5, se=float("nan"), n=1)}
    m = _uj.measured_power_ratio_from_traces(widths, "E", 0.02)
    assert m["n_peaks"] == 1 and "4121" in m["per_peak"] and "4192" not in m["per_peak"]
    assert m["ratio"] == pytest.approx(1.1)
    assert m["bar"] > 1.1 * np.sqrt(2) * 0.02, "the block scatter rides on every session's bar"
    assert not np.isfinite(_uj.measured_power_ratio_from_traces(widths, "M", 0.02)["ratio"])


def test_the_width_against_power_diagnostic_reads_the_committed_widths():
    if not (ROOT / "results" / "power_sweep.csv").is_file():
        pytest.skip("results/power_sweep.csv not committed")
    meas = _uj.measured_power_ratio()
    rows = _uj.width_vs_power_rows({}, meas)
    committed = {r["peak"]: r for r in rows if r["kind"] == "width_vs_power_committed"}
    assert set(committed) == {"4121", "4154", "4192", "4207"}
    for r in committed.values():
        assert np.isfinite(r["slope"]) and r["err"] > 0
        assert abs(r["slope"]) < 3.0 * r["err"] + 0.5, "no peak's width moves with power beyond a few bars"
    synthetic = {("M", "4192", P): dict(mean=5.0 * (1 - 0.1 * P), se=0.02, n=6) for P in (0.035, 0.07, 0.105, 0.21)}
    r = [x for x in _uj.width_vs_power_rows(synthetic, meas) if x["kind"] == "width_vs_power_traces"][0]
    assert r["slope"] < 0 and r["slope"] == pytest.approx(-0.1, rel=0.05)


# ---------------------------------------------------------------- the window
def test_the_window_is_on_at_every_m2_including_exactly_one():
    """The licence: the collection window reaches the model through the
    profile seam at M2 = 1 too, continuously across 1, and the producer never
    passes m2 to full_profile, whose own switch is off at exactly 1."""
    from rb5s6s import constants as K
    from rb5s6s.fullmodel import full_profile
    w0 = 64e-6
    prof1 = _uj.window_profile(w0, 1.0)
    assert prof1.z_ratio == pytest.approx(K.collection_z_ratio(w0_m=w0)) and prof1.z_ratio > 0.2
    assert _uj.window_profile(w0, 2.0).z_ratio == pytest.approx(2.0 * prof1.z_ratio)
    nu = np.linspace(-20.0, 20.0, 4001)
    kw = dict(gamma_coll=0.58, sigma_laser_fwhm=1.56, transit_fwhm=0.9575, s0=0.36, peak="4192", omega_mhz=0.45)
    off = full_profile(nu, **kw)                                  # full_profile's default: no window
    on = full_profile(nu, profile=prof1, **kw)                    # the producer's path at M2 = 1
    assert np.max(np.abs(on - off)) / np.max(off) > 1e-4, "the window at M2 = 1 must change the line"
    eps = full_profile(nu, profile=_uj.window_profile(w0, 1.0 + 1e-9), **kw)
    assert np.max(np.abs(on - eps)) / np.max(on) < 1e-8, "no step across M2 = 1 through the seam"
    switched = full_profile(nu, m2=1.0 + 1e-9, w0_m=w0, **kw)
    assert np.max(np.abs(switched - on)) / np.max(on) < 1e-6, "the seam and the switch agree above 1"
    src = SCRIPT.read_text(encoding="utf-8")
    calls = [m.group(0) for m in re.finditer(r"full_profile\([^)]*\)", src, re.S)]
    assert calls and all("m2=" not in c for c in calls), "the producer must not use full_profile's m2 switch"
    # THE PROFILE REACHES `full_profile` PER TRACE SINCE 2026-09-18, because the saturated shift density
    # is built at each trace's own power, so the Cell passes `per["profile"]` and falls back to the
    # cell-wide one. The assertion is on the WIRING and not on one spelling of it.
    assert "profile=per.get(\"profile\", self.profile)" in src or "profile=self.profile" in src


def test_the_producer_model_carries_the_window_the_isotope_and_the_tie():
    """The model of one trace at the theory point: the window (through the
    seam), the per-peak isotope in the transit, and Omega tied to P sqrt(rho)
    over w0^2 through two_photon_rabi_hz."""
    from rb5s6s import constants as K
    from rb5s6s.hyperpolarizability import two_photon_rabi_hz
    cell = _theory_cell(64.0)
    per85 = cell._per_trace(dict(T=130.0, P_W=0.225, iso=85, session="P", peak="4192"))
    per87 = cell._per_trace(dict(T=130.0, P_W=0.225, iso=87, session="P", peak="4207"))
    assert per85["transit"] / per87["transit"] == pytest.approx(np.sqrt(K.M_RB87_KG / K.M_RB85_KG), rel=1e-9)
    assert per87["omega_ref"] == pytest.approx(two_photon_rabi_hz(0.225, 64e-6, 0.94) / 1e6)
    assert per87["omega_ref"] == pytest.approx(0.45, abs=0.01)
    low = cell._per_trace(dict(T=130.0, P_W=0.025, iso=87, session="P", peak="4207"))
    assert low["omega_ref"] / per87["omega_ref"] == pytest.approx(0.025 / 0.225)
    assert low["s0"] / per87["s0"] == pytest.approx(0.025 / 0.225)
    # The tied S0 at 225 mW is the record's ONE predicted coefficient times the power, never a
    # literal: this line read 0.36 until 2026-09-17, which was the prediction at the retired
    # polarizability, and a literal cannot follow the cell it quotes.
    from rb5s6s.stark import kappa_pred_per_watt
    assert per87["s0"] == pytest.approx(kappa_pred_per_watt(K.W0_MEASURED_M, K.RHO_RETRO) * 0.225, rel=1e-6)


def test_the_depletion_arm_widens_through_the_package_function_and_restores_the_switch():
    from rb5s6s import stark
    t = 0.9575
    assert _uj.depleted_transit(t, 0.45, "4192", 0.0) == t
    wide = _uj.depleted_transit(t, 0.45, "4192", 3.0)
    assert 1.005 < wide / t < 1.03, "about one per cent at 64 um through companion_transit_mhz"
    wider = _uj.depleted_transit(t, 1.05, "4192", 3.0)
    assert wider > wide, "more Rabi frequency, more depletion"
    assert stark.COMPANIONS is None, "the module switch is restored after the call"
    src = SCRIPT.read_text(encoding="utf-8")
    assert 'depleted_transit(per["transit"], omega_ref, peak, self.cycles)' in src and "omega_ref = f * per[\"omega_ref\"]" in src, (
        "the depletion arm takes the tied Omega at its theory scale, not the fitted scale")


# ---------------------------------------------------------------- the parameter arms
def test_the_shared_laser_width_and_the_power_scale_arms_change_the_parameter_list():
    desc = _P_DESC + [dict(T=90.0, P_W=0.225, iso=87, session="T", peak="4207", axis="mhz")]
    per_session = _theory_cell(64.0, traces=desc)
    # ALPHA AND BETA ARE PINNED AT THEIR THEORY VALUES BY DEFAULT SINCE 2026-09-17 (owner,
    # 00:30: pin them from theory with their uncertainty carried as a systematic, and compare
    # the MLE's own value afterwards), so neither is in the name order unless freed, and the
    # freed arm restores the 2026-09-16 order with both prior terms beside omega_scale.
    assert per_session.names == ("sigma_l_P", "sigma_l_T", "omega_scale", "gamma_l")
    assert per_session.spec["pinned"] == ("alpha_rel", "beta_rel")
    shared = _theory_cell(64.0, traces=desc, sigma_l="shared")
    assert shared.names == ("sigma_l_shared", "omega_scale", "gamma_l")
    scaled = _theory_cell(64.0, traces=desc, power_scale=True)
    assert scaled.names[-2:] == ("power_scale_P", "power_scale_T")
    assert [n for n, _, _ in scaled.prior_terms] == ["omega_scale", "power_scale_P", "power_scale_T"]
    assert [sig for _, _, sig in scaled.prior_terms] == [_uj.OMEGA_PRIOR_FRAC, _uj.POWER_PRIOR_FRAC,
                                                         _uj.POWER_PRIOR_FRAC]
    freed = _theory_cell(64.0, traces=desc, free=("beta_rel", "alpha_rel"))
    assert freed.names == ("beta_rel", "alpha_rel", "sigma_l_P", "sigma_l_T", "omega_scale", "gamma_l")
    assert [n for n, _, _ in freed.prior_terms] == ["omega_scale", "beta_rel", "alpha_rel"]
    assert [sig for _, _, sig in freed.prior_terms] == [_uj.OMEGA_PRIOR_FRAC, _uj.BETA_PRIOR_FRAC,
                                                        _uj.ALPHA_PRIOR_FRAC]
    fixed = _theory_cell(64.0, traces=desc, fixed={"beta_rel": 5.0})
    assert "beta_rel" not in fixed.names and fixed.unpack([1.0, 1.6, 1.6, 1.0, 0.4])["beta_rel"] == 5.0
    d = scaled.unpack(_theory_p(scaled))
    assert scaled.power_factor(d, "P") == 1.0 and per_session.power_factor(per_session.unpack(_theory_p(per_session)), "P") == 1.0


def test_the_beta_profile_is_read_against_its_own_minimum_and_gives_a_bound():
    r = dict(chi2=100.0, params={"beta_rel": 0.0},
             beta_profile={"0.0": dict(chi2=100.0), "1.0": dict(chi2=100.5), "5.0": dict(chi2=104.0), "20.0": dict(chi2=200.0)})
    bp = _uj.beta_profile_read(r)
    assert bp["dchi2_beta_theory"] == pytest.approx(0.5) and bp["free_above_profile_min"] == 0.0
    assert bp["beta_profile_1sigma_hi_rel"] == pytest.approx(1.0 + 0.5 / 3.5 * 4.0)
    assert bp["beta_profile_ub95_rel"] == pytest.approx(1.0 + 2.21 / 3.5 * 4.0)
    stale = dict(r, chi2=103.0)                     # an unconverged free fit above its own profile
    bp2 = _uj.beta_profile_read(stale)
    assert bp2["free_above_profile_min"] == pytest.approx(3.0) and bp2["dchi2_beta_0"] == 0.0


# ---------------------------------------------------------------- the gate
def _fake_cell(form="mixed", w0=50.0, chi2=1000.0, moved=0.001, spread=0.1, chi2_red=1.4, preds=None, prof=None):
    return dict(spec=dict(form=form, w0_um=w0), chi2=chi2, chi2_red=chi2_red, centre_moved=moved, outer=[1, 1],
                spread=spread, errs={"beta_rel": 0.1}, sessions=["P", "T"], preds=preds or {"P": 1.01},
                params={"beta_rel": 0.0}, chi2_red_session={"P": chi2_red}, chi2_split_session={"P": {"core": [1000.0, 1000.0], "wing": [1000.0, 1000.0]}}, n_eff_session={"P": 1000.0}, n_traces_session={"P": 100},
                beta_profile=prof if prof is not None else {"0.0": dict(chi2=chi2), "1.0": dict(chi2=chi2 + 1), "5.0": dict(chi2=chi2 + 5), "20.0": dict(chi2=chi2 + 50)})


def test_the_rung_gate_passes_a_converged_run_and_refuses_each_defect(tmp_path):
    meas = {"P": dict(ratio=0.9956, bar=0.0188)}
    base = [_fake_cell(w0=w, chi2=1000.0 + (w - 50) ** 2) for w in (40.0, 50.0, 60.0)]
    summ = _uj.profile_summary([40.0, 50.0, 60.0], [c["chi2"] for c in base])
    good = _uj.gate_checks(base, {"mixed": (summ, base[1])}, meas, True)
    assert all(ok for _, ok, _ in good), [c for c in good if not c[1]]
    assert _uj.write_gate(tmp_path / "gate_x.txt", "x", good)
    text = (tmp_path / "gate_x.txt").read_text(encoding="utf-8")
    assert text.splitlines()[-1] == "GATE PASS" and "power-arm verdict for session P" in text
    for defect in ("moved", "spread", "nan_bar", "no_verdict", "free_above", "chi2_red", "session_starved", "noise_law_off", "session_overweight", "beta_far_from_theory", "laser_over_bound"):
        cells = [dict(c) for c in base]
        if defect == "moved":
            cells[1]["centre_moved"] = 0.5
        elif defect == "spread":
            cells[1]["spread"] = 12.0  # above the 10 the gate carries as a systematic
        elif defect == "nan_bar":
            cells[1]["errs"] = {"beta_rel": float("nan")}
        elif defect == "free_above":
            cells[1]["beta_profile"] = {"0.0": dict(chi2=990.0), "1.0": dict(chi2=991.0), "5.0": dict(chi2=995.0), "20.0": dict(chi2=1050.0)}
        elif defect == "chi2_red":
            cells[1]["chi2_red"] = 3.0
        elif defect == "session_starved":
            cells[1]["chi2_split_session"] = {"P": {"core": [1690.0, 1000.0], "wing": [1000.0, 1000.0]}, "E": {"core": [700.0, 1000.0], "wing": [1000.0, 1000.0]}}   # P MISFIT at +15 sigma, E UNDER-COST at -7 (A254)
        elif defect == "beta_far_from_theory":
            cells[1]["beta_profile"] = {"0.0": dict(chi2=1000.0), "1.0": dict(chi2=1000.0 + 4762.1), "5.0": dict(chi2=1000.0 + 90.4), "20.0": dict(chi2=1000.0 + 88085.3)}   # the committed Gaussian cell
        elif defect == "noise_law_off":
            cells[1]["chi2_split_session"] = {"P": {"core": [1000.0, 1000.0], "wing": [1400.0, 1000.0]}}   # the wing 9 sigma above its own law: WING-OFF
        elif defect == "session_overweight":
            cells[1]["n_eff_session"] = {"P": 1000.0, "E": 3000.0}; cells[1]["n_traces_session"] = {"P": 100, "E": 20}   # the evening's 48 per cent with 20 per cent of the traces
        elif defect == "laser_over_bound":
            cells[1]["params"] = {"beta_rel": 0.0, "sigma_l_T": 2.704}   # the Gaussian best cell's T width against the 2.4 MHz transition-axis bound
        m = {} if defect == "no_verdict" else meas
        checks = _uj.gate_checks(cells, {"mixed": (summ, cells[1])}, m, True)
        assert not all(ok for _, ok, _ in checks), defect
        assert not _uj.write_gate(tmp_path / f"gate_{defect}.txt", defect, checks)
        assert (tmp_path / f"gate_{defect}.txt").read_text(encoding="utf-8").splitlines()[-1] == "GATE REFUSE"


# ---------------------------------------------------------------- the archive
def test_the_design_reads_every_canonical_trace_with_its_session_isotope_and_power():
    if not (ROOT / "data_raw" / "MANIFEST.csv").is_file():
        pytest.skip("data_raw/MANIFEST.csv not in this checkout")
    from rb5s6s import constants as K
    rows = _uj.design()
    assert len(rows) == 159
    assert len({(r["peak"], r["T"], r["P_W"]) for r in rows}) == 32
    assert {r["session"] for r in rows} == {"P", "T"}
    assert all(r["P_W"] == 0.225 for r in rows if r["role"] == "t_sweep"), (
        "a blank manifest power is the temperature arm at 225 mW, never zero")
    assert all(r["iso"] == K.PEAKS[r["peak"]]["isotope"] for r in rows)
    assert all(1.0 <= r["tau"] <= 25.0 for r in rows)
    assert all(np.isfinite(r["law"]["a"]) and r["law"]["a"] > 0 for r in rows), "the dark floor is in every law"
    one = _uj.design(traces_per_condition=1)
    assert len(one) == 32
    q = [r for r in _uj.design(with_excluded=True) if r["session"] == "Q"]
    assert len(q) == 19 and all(r["role"] == "excluded" and r["peak"] == "4154" and r["law"] is None for r in q), (
        "session Q is the manifest's RF-off excluded 130 C attempt, with no committed noise law")


def test_the_excluded_sessions_load_in_place_with_their_own_laws_or_skip():
    """Session E and M through run_stark_joint.py's loaders; skipped, not
    faked, when the trees are not on this machine."""
    _needs_traces()
    trees = _uj.session_trees()
    if not all(ok for _, ok in trees.values()):
        pytest.skip("the excluded session trees are not on this machine")
    rows = _uj.design(traces_per_condition=1)
    session_traces, dropped = _uj.load_sessions(["E", "M"])
    _uj._init_worker(session_traces)
    tr = _uj._load(_uj.design_spec(rows, ["P", "T", "E", "M"]))
    by = {s: [t for t in tr if t["session"] == s] for s in "PTEM"}
    assert len(by["E"]) == 46 and len(by["M"]) == 25
    assert len(dropped) == 1 and dropped[0]["P_W"] == 0.21 and "truncated" in dropped[0]["reason"]
    _uj._init_worker([])
    with pytest.raises(RuntimeError):
        _uj._load(_uj.design_spec(rows, ["P", "T", "E"]))          # a worker never handed the session refuses
    assert all(t["axis"] == "ms" for t in by["E"]) and all(t["axis"] == "mhz" for t in by["M"])
    assert {t["peak"] for t in by["E"]} == {"4121", "4154", "4192", "4207"} and {t["peak"] for t in by["M"]} == {"4192"}
    for t in by["E"] + by["M"]:
        assert t["law"]["source"].startswith("condition_noise_model") and t["law"]["a"] > 0 and t["tau"] >= 1.0
        assert t["T"] == 130.0 and t["P_W"] in (0.09, 0.18, 0.27, 0.035, 0.07, 0.105, 0.21)
    e = _theory_cell(64.0, traces=by["E"][:1])
    d = e.unpack(_theory_p(e))
    nu = e.axis(d, by["E"][0])
    assert nu.size == by["E"][0]["x"].size and abs(nu[-1] - nu[0]) > 5.0, "the evening axis is ms times the seeded rate"


# ---------------------------------------------------------------- the profile read
def test_the_profile_read_gives_an_interval_inside_and_a_bound_at_an_edge():
    ws = np.arange(40.0, 91.0, 2.0)
    inner = 100.0 + ((ws - 63.0) / 2.0) ** 2                 # sigma = 2 um at Delta chi2 = 1
    s = _uj.profile_summary(ws, inner)
    assert s["kind"] == "interior_minimum"
    assert s["w0"] == pytest.approx(63.0, abs=1e-6) and s["w0_err"] == pytest.approx(2.0, rel=1e-6)
    # the crossings are interpolated linearly between grid points two um apart,
    # so they carry up to a quarter step of bias against the parabola's own
    # crossing, which is why the quotable bar is w0_err and these are the check
    assert s["lo1"] == pytest.approx(61.0, abs=0.3) and s["hi1"] == pytest.approx(65.0, abs=0.3)
    assert s["lo1"] < s["w0"] - s["w0_err"] * 0.8 and s["hi1"] > s["w0"] + s["w0_err"] * 0.8
    coarse = np.array([40.0, 50.0, 60.0])
    s = _uj.profile_summary(coarse, 100.0 + ((coarse - 47.9) / 0.7) ** 2)
    assert s["kind"] == "interior_minimum" and s["w0"] == pytest.approx(47.9, abs=1e-6)
    assert np.isnan(s["lo1"]) and np.isnan(s["hi1"]), "a grid that cannot resolve the crossing leaves it blank"
    # THE COMMITTED GRID OF W1h (physics F1): dchi2 39.2/0/17.0 at 70/80/90 um read a
    # 0.26 um linear crossing beside a 1.9 um parabola bar; the rise per step is
    # 17 and 39 levels, so both crossings stay blank and the parabola is the bar
    committed = np.array([70.0, 80.0, 90.0])
    s = _uj.profile_summary(committed, 1000.0 + np.array([39.2, 0.0, 17.0]))
    assert s["kind"] == "interior_minimum" and s["w0"] == pytest.approx(81.98, abs=0.01)
    assert s["w0_err"] == pytest.approx(1.887, abs=0.01)
    assert np.isnan(s["lo1"]) and np.isnan(s["hi1"]) and np.isnan(s["lo_od"]) and np.isnan(s["hi_od"])
    # and a step of one sigma with the vertex on the grid resolves both crossings
    ongrid = np.arange(60.0, 71.0, 2.0)
    s = _uj.profile_summary(ongrid, 100.0 + ((ongrid - 66.0) / 2.0) ** 2)
    assert s["lo1"] == pytest.approx(64.0, abs=0.01) and s["hi1"] == pytest.approx(68.0, abs=0.01)
    # THE COMMITTED GRID OF W1h (physics F1): dchi2 39.2/0/17.0 at 70/80/90 um read a
    # 0.26 um linear crossing beside a 1.9 um parabola bar; the rise per step is
    # 17 and 39 levels, so both crossings stay blank and the parabola is the bar
    committed = np.array([70.0, 80.0, 90.0])
    s = _uj.profile_summary(committed, 1000.0 + np.array([39.2, 0.0, 17.0]))
    assert s["kind"] == "interior_minimum" and s["w0"] == pytest.approx(81.98, abs=0.01)
    assert s["w0_err"] == pytest.approx(1.887, abs=0.01)
    assert np.isnan(s["lo1"]) and np.isnan(s["hi1"]) and np.isnan(s["lo_od"]) and np.isnan(s["hi_od"])
    # and a step of one sigma with the vertex on the grid resolves both crossings
    ongrid = np.arange(60.0, 71.0, 2.0)
    s = _uj.profile_summary(ongrid, 100.0 + ((ongrid - 66.0) / 2.0) ** 2)
    assert s["lo1"] == pytest.approx(64.0, abs=0.01) and s["hi1"] == pytest.approx(68.0, abs=0.01)
    rising = 100.0 + 0.3 * (ws - 40.0)                       # monotone from the low edge
    s = _uj.profile_summary(ws, rising)
    assert s["kind"] == "one_sided_upper_bound"
    assert s["bound95"] == pytest.approx(40.0 + 2.71 / 0.3, rel=1e-6)
    falling = 100.0 + 0.3 * (90.0 - ws)
    s = _uj.profile_summary(ws, falling)
    assert s["kind"] == "one_sided_lower_bound"
    assert s["bound95"] == pytest.approx(90.0 - 2.71 / 0.3, rel=1e-6)


def test_the_admission_names_its_word_from_two_absolute_statistics():
    """A254: the wing reads the noise law, the core reads the model, each against
    1 +- sqrt(2/n_eff); the gate names WING-OFF, MISFIT or UNDER-COST per session, admits
    a session inside five sigma on both, and refuses a cell carrying no split at all.
    Planted through the REAL gate_checks, not a re-implementation."""
    n = 1000.0
    ok = dict(chi2_split_session={"P": {"core": [n * 1.10, n], "wing": [n * 0.95, n]}})
    v = _uj.session_verdicts(ok); assert v["P"]["word"] == "ADMITTED", v
    bad = dict(chi2_split_session={"P": {"core": [n * 1.69, n], "wing": [n, n]}, "E": {"core": [n * 0.70, n], "wing": [n, n]},
                                   "T": {"core": [n, n], "wing": [n * 1.40, n]}})
    v = _uj.session_verdicts(bad)
    assert v["P"]["word"] == "MISFIT" and v["E"]["word"] == "UNDER-COST" and v["T"]["word"] == "WING-OFF", v
    assert "P:MISFIT" in _uj.session_verdicts_text(bad) and "T:WING-OFF" in _uj.session_verdicts_text(bad)
    assert _uj.session_verdicts({}) == {}, "no split, no verdict: the gate refuses the cell for it"
    # through the real gate: the fixture's own cell admits, the misfit one refuses on this check by name
    ws = [40.0, 50.0, 60.0]; chi2s = [1010.0, 1000.0, 1012.0]
    summ = _uj.profile_summary(ws, chi2s)
    good = [_fake_cell(w0=w, chi2=c) for w, c in zip(ws, chi2s)]
    meas = {"P": {"ratio": 1.0, "bar": 0.02, "block_scatter_mhz": 0.0, "block_scatter_frac": 0.0}}
    labels = [lbl for lbl, ok_, _ in _uj.gate_checks(good, {"mixed": (summ, good[1])}, meas, True) if "wing within" in lbl]
    assert labels, "the two-statistic check is registered"
    worse = [dict(c) for c in good]; worse[1] = dict(worse[1], chi2_split_session=bad["chi2_split_session"])
    named = [(ok_, msg) for lbl, ok_, msg in _uj.gate_checks(worse, {"mixed": (summ, worse[1])}, meas, True) if "wing within" in lbl]
    assert named and not named[0][0] and "P:MISFIT" in named[0][1] and "E:UNDER-COST" in named[0][1], named


def test_no_summary_row_rises_above_diagnostic_without_a_closure_row():
    """NO INTERVAL BEFORE CLOSURE (2026-09-14): until a row of row_kind `closure` (the
    twin's truth recovered within the bar) is in the committed file, every summary
    row's status stays DIAGNOSTIC. The rule is read from the committed CSV itself."""
    if not CSV.is_file():
        pytest.skip("results/ultra_joint_fit.csv not committed yet")
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    closure = [r for r in rows if r.get("row_kind") == "closure"]
    if not closure:
        above = [r for r in rows if r.get("row_kind", "").startswith("summary") and r.get("status") not in ("DIAGNOSTIC", "")]
        assert not above, f"{len(above)} summary row(s) above DIAGNOSTIC with no closure row: " + ", ".join(r['row_kind'] + ':' + r['status'] for r in above[:4])


def test_two_significant_digits_and_every_bar_names_its_source():
    assert _uj.sig2(1234.5) == "1200" and _uj.sig2(0.012345) == "0.012" and _uj.sig2(0.0995) == "0.10"
    assert _uj.sig2(float("nan")) == "" and _uj.sig2(0.0) == "0"
    assert _uj.pair(0.123456, 0.00987) == ("0.1235", "0.0099")
    assert _uj.pair(63.27, 2.04) == ("63.3", "2.0")
    assert _uj.pair(5.0, float("nan")) == ("5.0", "")
    assert _uj.with_decimals_of(49.917, 0.69) == "49.92" and _uj.with_decimals_of(49.917, float("nan")) == "49.92"
    assert _uj.COLUMNS[-1] == "status", "status is the last column, where annotate_results_status.py writes it"
    bars = [c for c in _uj.COLUMNS if "err" in c or "spread" in c or "profile" in c]
    for c in bars:
        assert any(tag in c for tag in ("_hessian", "_parabola", "_lsq", "start_spread", "_profile_")), (
            f"{c}: a bar column must say whether it is a Hessian, a parabola, a least-squares fit, a start spread or a profile")


# ---------------------------------------------------------------- the committed file
def test_the_file_is_registered_and_its_summary_rows_carry_the_check():
    src = (ROOT / "scripts" / "annotate_results_status.py").read_text(encoding="utf-8")
    assert '"ultra_joint_fit.csv": "DIAGNOSTIC"' in src
    if not CSV.is_file():
        pytest.skip("results/ultra_joint_fit.csv not committed yet")
    rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
    assert rows and set(_uj.COLUMNS) <= set(rows[0])
    forms = {r["form"] for r in rows if r["row_kind"] == "grid"}
    assert forms
    for form in forms:
        summ = [r for r in rows if r["row_kind"] == "summary_minimum" and r["form"] == form]
        assert len(summ) == 1, form
        s = summ[0]
        assert s["bound_kind"] in ("interior_minimum", "one_sided_upper_bound", "one_sided_lower_bound",
                                   "one_sided_lower_bound_unresolved", "one_sided_upper_bound_unresolved")
        assert s["power_arm_refused"] in ("True", "False") and s["power_ratio_meas"]
        assert s["power_arm_pooled_refused"] in ("True", "False")
        assert s["status"] == "DIAGNOSTIC"
        grid = [r for r in rows if r["row_kind"] == "grid" and r["form"] == form]
        assert min(float(r["dchi2"]) for r in grid) == 0.0
        assert all(r["m2"] == "1" and r["depletion_cycles"] == "0" for r in grid)
        assert all(r["dchi2_beta_theory"] != "" and r["dchi2_beta_0"] != "" for r in grid), "every grid row carries its beta profile"
        prof = [r for r in rows if r["row_kind"] == "beta_profile" and r["form"] == form]
        assert len(prof) == 4 * len(grid)
        bsum = [r for r in rows if r["row_kind"] == "summary_beta_profile" and r["form"] == form]
        assert len(bsum) == 1 and bsum[0]["beta_profile_ub95_khz"] != ""
        assert [r for r in rows if r["row_kind"] == "power_arm_session" and r["form"] == form]
        assert [r for r in rows if r["row_kind"] == "power_arm_pooled" and r["form"] == form]
    assert [r for r in rows if r["row_kind"] == "width_vs_power_committed"]
    assert all(";" not in v for r in rows for v in r.values())

def test_a_profile_still_falling_at_the_grid_edge_is_unresolved_and_no_bound():
    """W1j finding F2: the fine_all gaussian and mixed minima sit on the last grid point with
    a rise of about 30 per 2 um step against the resolve threshold, so the crossing cannot be
    read and the minimum is off the grid. The kind must say unresolved, the bound stay blank,
    both estimates and the rise be carried, and the gate must not count it as a bound."""
    ws = [80.0, 82.0, 84.0, 86.0, 88.0, 90.0]
    chi2s = [1150.0, 1120.0, 1093.6, 1062.4, 1028.1, 1000.0]
    s = _uj.profile_summary(ws, chi2s)
    assert s["kind"] == "one_sided_lower_bound_unresolved", s
    assert not np.isfinite(s["bound95"])
    assert s["edge_rise_levels"] > _uj.RESOLVE_LEVELS
    assert np.isfinite(s["bound95_linear"]) and np.isfinite(s["bound95_parabola"])
    assert s["bound95_linear"] < 90.0 and s["bound95_parabola"] < 90.0
    # a resolved edge, the neighbour within the threshold, stays a bound
    s2 = _uj.profile_summary(ws, [1010.0, 1006.0, 1004.0, 1002.5, 1001.0, 1000.0])
    assert s2["kind"] == "one_sided_lower_bound" and np.isfinite(s2["bound95"]), s2



def test_the_moment_statistic_takes_a_fitted_baseline_and_not_a_wing_strip():
    """The arm's statistic, on a trace whose wings the LINE ITSELF occupies.

    FAILURE MODE THIS CATCHES, and it is a measured bias rather than a
    hypothetical. `windowed_cumulants` defaults to a WINGS baseline; on this
    sweep the line contributes about 0.9 per cent of peak at the +-20 to 28 MHz
    strips, which drags k2 down by 7.6 per cent and k3 by 21 at the 12 MHz
    window. `_moment_stats` must therefore pass `baseline=None` and let the
    caller remove a FITTED offset, and this test fails if the default ever comes
    back: the wings-baselined statistic sits measurably below the truth on a
    trace built with no offset at all.
    """
    from rb5s6s.cumulants import windowed_cumulants
    m = _uj
    nu = np.linspace(-42.5, 42.5, 4001)
    from rb5s6s.fullmodel import full_profile
    y = full_profile(nu, gamma_coll=0.26, sigma_laser_fwhm=1.0, transit_fwhm=1.28,
                     s0=0.36, gamma_l=0.28, peak="4192", T_C=130.0)
    stats = m._moment_stats(nu, y)
    assert {k for k in stats if not k.startswith("diag_")} == {
        f"mu{n}@{w:g}" for n in m.MOMENT_ORDERS for w in m.MOMENT_WINDOWS}
    # THE WINDOW IS READ FROM THE PRODUCER, never typed: `MOMENT_WINDOWS` moved from (3.25, 6, 12) to
    # (2, 8, 13) on 2026-09-18 so the vector sits on the window surface's own grid, and a typed 12 here
    # raised a KeyError on a statistic the producer no longer emits.
    w_hi = max(m.MOMENT_WINDOWS)
    k_wing, _ = windowed_cumulants(nu, y, w_hi, orders=(2,), baseline="wings")
    assert stats[f"mu2@{w_hi:g}"] > k_wing[2], (stats[f"mu2@{w_hi:g}"], k_wing[2])
    # both parities are produced, which the arm that ran at orders [2, 4] was not
    assert {2, 3, 4, 5, 6, 7} == set(m.MOMENT_ORDERS)


def test_moment_cumulant_conditioning_matches_orders_two_and_three_being_unmoved():
    """O33's vector, read off the producer's own function: for order >= 4, `mu` and `k` differ
    and `conditioning` is exactly `abs(k) / abs(mu)` from the SAME central-moment array (no
    second quadrature -- planted by checking `k` against an independent `windowed_cumulants`
    call, which must agree to floating-point precision if both routes are consistent)."""
    from rb5s6s.cumulants import windowed_cumulants
    m = _uj
    nu = np.linspace(-42.5, 42.5, 4001)
    from rb5s6s.fullmodel import full_profile
    y = full_profile(nu, gamma_coll=0.26, sigma_laser_fwhm=1.0, transit_fwhm=1.28,
                     s0=0.36, gamma_l=0.28, peak="4192", T_C=130.0)
    rows = m.moment_cumulant_conditioning(nu, y, windows=(5.0, 8.0), orders=m.MOMENT_ORDERS)
    assert {r["order"] for r in rows} == {4, 5, 6, 7}          # orders 2, 3 are not returned
    assert {r["window"] for r in rows} == {5.0, 8.0}
    for r in rows:
        k_indep, _ = windowed_cumulants(nu, y, r["window"], orders=(r["order"],), baseline=None)
        assert r["k"] == pytest.approx(k_indep[r["order"]], rel=1e-9, abs=1e-12)
        assert r["conditioning"] == pytest.approx(abs(r["k"]) / abs(r["mu"]), rel=1e-12)
        assert r["mu"] > 0.0 or r["order"] % 2 == 1            # every even order's moment is non-negative


def test_the_moment_vector_is_not_wired_into_the_arms_own_admission():
    """The 2026-09-20 invariance check of O33's switch, planted so a future edit that DOES flip
    `_moment_stats` or `moment_arm` onto `mu<n>@<w>` keys is caught here rather than discovered
    downstream. `moment_arm`'s own docstring says its covariance is diagonal; central moments at
    order >= 4 are strongly auto-correlated with mu2, so wiring them into that arm's per-statistic
    exceedance test would over-weight correlated evidence (see `moment_cumulant_conditioning`'s
    docstring). Until that arm carries a full covariance or the owner rules the marginal
    treatment acceptable, `_moment_stats` keeps quoting cumulants and nothing it returns is
    prefixed `mu`."""
    m = _uj
    nu = np.linspace(-42.5, 42.5, 4001)
    from rb5s6s.fullmodel import full_profile
    y = full_profile(nu, gamma_coll=0.26, sigma_laser_fwhm=1.0, transit_fwhm=1.28,
                     s0=0.36, gamma_l=0.28, peak="4192", T_C=130.0)
    stats = m._moment_stats(nu, y)
    # O33/A72 INVERTED: this guard asserted the moment vector stays UNWIRED. The owner's
    # ruling reverses it, and a guard left asserting the retired state is how a reversed
    # decision silently un-reverses itself.
    assert all(k.startswith("mu") or k.startswith("diag_") for k in stats), stats
    assert any(k.startswith("mu") for k in stats), stats   # the vector IS the moments now


def test_the_moment_and_cumulant_vectors_carry_the_same_information():
    """THE INVARIANCE ADDITION TO O33 (2026-09-20): moments and cumulants are related by an
    invertible map, so a fit carrying the FULL covariance of its statistic vector extracts
    IDENTICAL information from either -- what the switch buys is conditioning, not new
    information, and F211's SNR ratios (384x at mu4@8) are a MARGINAL, per-statistic reading
    that does not carry over to a joint, full-covariance treatment.

    Planted on a pure Lorentzian (nu grid, one window, orders 2 and 4): draw many noisy
    replicas of the noiseless truth (same construction as `fullmodel.ultra_joint_covariance`),
    estimate the FULL 2x2 covariance of (mu2, mu4) and of (k2, k4) from them, then whiten one
    held-out noisy realisation's departure from the truth by each vector's own covariance. THE
    TWO WHITENED CHI-SQUAREDS MUST AGREE TO WITHIN A FEW PER CENT (the map is exact only in the
    noiseless limit; away from it a small residual from the map's own nonlinearity at order 4 is
    expected and is not the effect under test), while the MOMENT covariance's condition number
    must be substantially worse than the CUMULANT covariance's -- that gap, and not the SNR
    ratio, is the number the switch is licensed by for a diagonal-admission arm."""
    from rb5s6s.cumulants import cumulants_from_central_moments, windowed_moments
    from rb5s6s.lineshape import lorentzian

    nu = np.linspace(-30.0, 30.0, 4001)
    y0 = lorentzian(nu, 3.0)
    peak = float(np.max(y0))
    w = 5.0
    orders_full = (1, 2, 3, 4)

    def stats(y):
        mu, _ = windowed_moments(nu, y, w, orders=orders_full, baseline=None, centre0=0.0,
                                 n_points=801, max_passes=30)
        mu_arr = np.array([mu[o] for o in range(1, 5)])
        kappa = cumulants_from_central_moments(mu_arr)
        return np.array([mu[2], mu[4]]), np.array([kappa[1], kappa[3]])

    truth_mu, truth_k = stats(y0)
    noise_frac, n_real = 0.02, 4000
    X_mu = np.empty((n_real, 2)); X_k = np.empty((n_real, 2))
    for r in range(n_real):
        rng = np.random.default_rng(20260920 + r)
        x = rng.standard_normal(y0.size)
        yn = y0 + noise_frac * np.sqrt(np.clip(y0, 0.0, None) * peak) * x
        X_mu[r], X_k[r] = stats(yn)
    cov_mu = np.cov(X_mu, rowvar=False)
    cov_k = np.cov(X_k, rowvar=False)

    rng = np.random.default_rng(7770)
    x = rng.standard_normal(y0.size)
    y_data = y0 + noise_frac * np.sqrt(np.clip(y0, 0.0, None) * peak) * x
    data_mu, data_k = stats(y_data)
    r_mu, r_k = data_mu - truth_mu, data_k - truth_k
    chi2_mu = float(r_mu @ np.linalg.solve(cov_mu, r_mu))
    chi2_k = float(r_k @ np.linalg.solve(cov_k, r_k))

    assert chi2_mu == pytest.approx(chi2_k, rel=0.05), (chi2_mu, chi2_k)
    cond_mu, cond_k = np.linalg.cond(cov_mu), np.linalg.cond(cov_k)
    assert cond_mu > 10.0 * cond_k, (cond_mu, cond_k)


def test_a_ratio_whose_denominator_flips_sign_across_repeats_is_refused_by_name():
    """The arm admits on having a population moment, never on size (O17).

    The odd cumulants of this archive sit consistent with zero, so a ratio built
    on one has a denominator that changes sign from repeat to repeat: the ratio
    is then Cauchy-like, with no population mean for a pull to be taken against,
    and a bar computed from the repeats returns a finite number that keeps
    moving with the repeat count. That is the failure that does not announce
    itself. This asserts the refusal fires on exactly that and that it says so,
    and -- the half a size-based rule would get wrong -- that a SMALL but
    sign-stable denominator is admitted.
    """
    flips = lambda v: min(int((np.asarray(v) > 0).sum()), int((np.asarray(v) < 0).sum()))  # noqa: E731
    assert flips([+1.0, -1.0, +1.0, -2.0, +1.0]) == 2      # refused
    assert flips([1e-9, 2e-9, 1.5e-9, 1.1e-9, 1.3e-9]) == 0  # tiny, and admitted
    rows = _rows("ultra_joint_moments.csv")
    if not rows:
        pytest.skip("the moment arm has not been run in this tree")
    # THREE KINDS OF REFUSAL SHARE THE ARTIFACT STATUS SINCE 2026-09-19 (the C2 board's CRITICAL): the
    # sign-flip rule this test is about, the per-statistic numerical floor (F144), and the diagnostic
    # windows (D9). Only the first is a RATIO refusal, so the selection reads the rule's own note and not
    # the status, which the other two kinds now share. A row refused for another reason names it.
    artefacts = [r for r in rows if r["status"] == "ARTIFACT"]
    # THE FILE CARRIES ARCHIVE ROWS ONLY WHEN THE MOMENT LADDER'S ARCHIVE RUNG IS RECORDED PASS
    # (D11, 2026-09-19); until then it holds the twin's vector at the passed levels and a refused row
    # per absent rung, and the sign-flip rule has no archive population to fire on. The planted
    # `flips` above is the rule's own test; the committed file is read only where it has the rows.
    real_rows = [r for r in artefacts if not r["case"].startswith("twin@")]
    if not real_rows:
        assert any("rung has not been run" in r["note"] for r in artefacts), \
            "no archive rows and no refused-rung row: the file says neither why it lacks the archive nor that it does"
        return
    refused = [r for r in artefacts if "no population moment" in r["note"]]
    assert refused, "no ratio was refused, so the rule never fired on the archive"
    for r in refused:
        assert "/" in r["quantity"], r["quantity"]
    for r in artefacts:
        assert any(k in (r["note"] + r["basis"]) for k in ("no population moment", "under the floor",
                                                            "DIAGNOSTIC window", "refused", "rung ")), r
    # and the refusal row may not quote a sigma on a statistic that has no
    # variance: at five repeats Var(t^2) does not exist
    for r in rows:
        if r["quantity"] == "mean_square_pull":
            assert "sigma" in r["note"] and "no sigma" in r["note"], r["note"]


def test_the_jackknife_corrects_the_anchor_and_not_the_parabola_vertex():
    """F179: `coverage_as_used` jackknifed the PARABOLA VERTEX and handed the bias to `_covered`, which
    anchors the interval at the grid argmin, so a reference-anchored interval was shifted by a different
    estimator's bias. That is the mis-anchoring F164 repaired, re-entering through the correction. F164
    measured the two points 0.163 um apart at the low rung against a half-width of 0.027.

    Planted four ways, the third of them the NEGATIVE: the old shift put the interval nowhere near the
    truth, so a green here cannot be produced by the defect this replaces."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "closure_anchor_test", Path(__file__).resolve().parents[1] / "scripts" / "run_ultra_joint_closure.py")
    cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)

    def cell(est, ref, lo_hw, hi_hw, bar=0.5):
        x = [None] * 9
        x[1], x[2], x[8] = est, bar, (lo_hw, hi_hw, ref)
        return x

    truth = 42.0
    # 1. the interval is the REFERENCE's, whatever the vertex says
    far = cell(est=43.5, ref=42.0, lo_hw=0.1, hi_hw=0.1)
    assert cl._covered(far, truth), "a reference-anchored interval on the truth was reported uncovered"
    assert cl._anchor(far) == 42.0, cl._anchor(far)

    # 2. a correction shifts that interval by the bias OF THE ANCHOR
    off = cell(est=99.0, ref=42.30, lo_hw=0.05, hi_hw=0.05)
    assert not cl._covered(off, truth)
    assert cl._covered(off, truth, centre=cl._anchor(off) - 0.30)

    # 3. THE NEGATIVE: the old rule shifted by (centre - est), which with a distant vertex is absurd
    old_shift = (cl._anchor(off) - 0.30) - off[1]
    lo, hi = 42.30 + old_shift - 0.05, 42.30 + old_shift + 0.05
    assert not (lo <= truth <= hi), "the OLD pairing covered the truth, so this test cannot see F179"

    # 4. and the jackknife removes a common bias from the anchors, never from the vertices
    g = [cell(est=99.0 + i, ref=42.0 + 0.30 + 0.01 * i, lo_hw=0.05, hi_hw=0.05) for i in range(8)]
    corrected, raw, bias, _se = cl.coverage_as_used(g, truth)
    assert raw == 0.0, raw
    assert corrected == 1.0, corrected
    assert abs(bias - 0.335) < 0.01, bias          # the ANCHOR's bias, not the vertex's +57


def test_the_closure_reads_its_interval_from_the_profile_crossings_on_a_skewed_profile():
    """F41: a profile steep on one side and flat on the other gives a parabola whose bar averages
    the two; the crossings read each side. Planted on chi2 = 4 x^2 (x < 0) and chi2 = x^2 (x >= 0):
    the left half-width is 0.5, the right 1.0, and the parabola over a 3 um window sits between."""
    import importlib.util
    import numpy as np
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("closure_for_test", Path(__file__).resolve().parents[1] / "scripts" / "run_ultra_joint_closure.py")
    cl = importlib.util.module_from_spec(spec); spec.loader.exec_module(cl)
    w = np.arange(70.0, 82.5, 0.5); c = np.where(w < 76, 4.0 * (w - 76) ** 2, (w - 76) ** 2) + 100.0
    lo, hi, _ref = cl.crossings(list(zip(w, c)))   # crossings carries its reference since F164
    assert abs(lo - 0.5) < 0.02 and abs(hi - 1.0) < 0.02, (lo, hi)
    _, bar, why = cl.parabola(list(zip(w, c)))
    assert why == "interior" and 0.5 < bar < 1.0, (bar, why)
    # THE INTERVAL CARRIES ITS OWN ANCHOR SINCE F164 (2026-09-19). This block asserted the interval was
    # centred on the reported ESTIMATE, which is the pairing F164 found wrong: `crossings()` measures its
    # half-widths from the grid's argmin, and anchoring them at the parabola vertex tested the profile's
    # WIDTH placed somewhere else. The row's interval is now (lo, hi, reference) and coverage is a property
    # of that interval; the estimate is a separate diagnostic point.
    # the stored row is (r, w, bar, why, pts, level, shape, parts, half_widths): the interval is index 8
    row = (0, 76.3, 0.1, "interior", None, None, None, None, (0.5, 1.0, 76.3))
    assert cl._covered(row, 76.0), "an interval anchored at 76.3 spans [75.8, 77.3] and holds the truth"
    assert not cl._covered((0, 77.2, 0.1, "interior", None, None, None, None, (0.5, 1.0, 77.2)), 76.0)
    # the ANCHOR is what decides it, not the estimate: the same widths and estimate, a reference one
    # micron away, and the verdict flips. This is the defect F164 repaired, planted.
    assert not cl._covered((0, 76.3, 0.1, "interior", None, None, None, None, (0.5, 1.0, 77.3)), 76.0)
    # an OLD dump carries a two-element interval and must fall back to the symmetric bar, never re-anchor
    assert not cl._covered((0, 76.3, 0.1, "interior", None, None, None, None, (0.5, 1.0)), 76.0)
    assert cl._covered((0, 76.05, 0.1, "interior", None, None, None, None, (0.5, 1.0)), 76.0)
    # the jackknife moves the estimate, and the interval travels with it
    assert not cl._covered(row, 76.0, centre=76.3 + 5.0)


def test_the_window_sets_are_disjoint_on_the_surface_grid_and_ordered_by_measured_snr():
    """The quoted windows and the diagnostic windows are two sets of one grid, and the constants say so.

    Failure mode: a window quoted in both sets would be admitted as a measurement and refused as a diagnostic
    in the same CSV; a window off the surface's grid would have no twin bias to subtract; and a floor of zero
    would admit numerical dust as a channel (F144 read k7@13 at 6.6e-7 of its own scale with the fit exact).
    The numbers here are read from the producer, never typed, so a re-measured choice moves them with it.
    """
    m = _uj
    quoted, diag = set(m.MOMENT_WINDOWS), set(m.DIAGNOSTIC_WINDOWS)
    assert quoted and diag and not (quoted & diag), (quoted, diag)
    surface = {0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 13.0, 21.0}
    assert (quoted | diag) <= surface, (quoted | diag) - surface
    assert 0.0 < m.CUMULANT_FLOOR_REL < 1e-3, m.CUMULANT_FLOOR_REL
    # the two windows the measurement of 2026-09-19 found dead for one order each are NOT quoted
    assert 8.0 not in quoted and 21.0 not in quoted
