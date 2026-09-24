"""
Closure tests for the hierarchical fit (rb5s6s/global_fit.py).

Before trusting a cross-peak/cross-temperature beta, the fit must recover
KNOWN per-isotope betas AND a KNOWN per-temperature sigma_laser drift from
campaign-like synthetics -- the whole point being that sharing sigma_laser
across the 4 peaks at each T pins sigma_laser(T) even when it drifts, so beta
is not contaminated by that drift.
"""

from __future__ import annotations

import numpy as np
import pytest

from rb5s6s import config as C
from rb5s6s.density import density_units
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency, transit_fwhm_at_T
from rb5s6s.global_fit import fit_global
from conftest import requires_raw_traces

RATE_T = 0.08514
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)
# two isotopes, two peaks each (like 87: 4207/4121; 85: 4192/4154)
PEAKS = [("4207", 87), ("4121", 87), ("4192", 85), ("4154", 85)]


def synth_blocks(beta_by_iso, sigma_by_T, transit_ref=0.9,
                 temps=(70.0, 90.0, 110.0), amp=1.0, noise_a=6e-3, seed=C.RNG_SEED):
    rng = np.random.default_rng(seed)
    blocks = []
    for peak, iso in PEAKS:
        for T in temps:
            N = density_units(T)
            gc = beta_by_iso[iso] * N
            sl = sigma_by_T[T]
            transit = transit_fwhm_at_T(T, transit_ref)
            freqs, volts = [], []
            for _ in range(5):
                c = rng.normal(0.0, 1.0)
                g = amp * (1.0 + rng.normal(0.0, 0.03))
                prof = model_profile(NU - c, gamma_coll=gc, sigma_laser_fwhm=sl,
                                     transit_fwhm=transit)
                v = g * prof / prof.max()
                sig = np.sqrt(noise_a ** 2 + 2e-5 * np.maximum(v, 0.0))
                volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
                freqs.append(NU.copy())
            blocks.append({"peak": peak, "isotope": iso, "T_C": T, "N_units": N,
                           "freqs": freqs, "volts": volts, "law": None})
    return blocks


@pytest.mark.slow
def test_recovers_per_isotope_beta_and_drifting_sigma():
    beta_true = {85: 0.05, 87: 0.02}           # isotopes genuinely differ
    sigma_true = {70.0: 1.0, 90.0: 1.4, 110.0: 0.9}  # NON-monotonic laser drift
    blocks = synth_blocks(beta_true, sigma_true)
    fit = fit_global(blocks, transit_ref_mhz=0.9)
    # per-isotope beta recovered and the two isotopes resolved as different
    for iso in (85, 87):
        assert abs(fit["beta_by_isotope"][iso] - beta_true[iso]) < \
            3 * fit["beta_err_by_isotope"][iso] + 0.02, fit["beta_by_isotope"]
    assert fit["beta_by_isotope"][85] > fit["beta_by_isotope"][87]
    # the sigma_laser(T) DRIFT is recovered, including its non-monotonicity
    sl = fit["sigma_laser_by_T"]
    for T in (70.0, 90.0, 110.0):
        assert abs(sl[T] - sigma_true[T]) < 0.25, sl
    assert sl[90.0] > sl[70.0] and sl[90.0] > sl[110.0]  # the injected bump


@pytest.mark.slow
def test_equal_isotopes_recovered_equal():
    beta_true = {85: 0.03, 87: 0.03}
    sigma_true = {70.0: 1.1, 90.0: 1.1, 110.0: 1.1}
    fit = fit_global(synth_blocks(beta_true, sigma_true, seed=3), transit_ref_mhz=0.9)
    b85, b87 = fit["beta_by_isotope"][85], fit["beta_by_isotope"][87]
    e = fit["beta_err_by_isotope"][85] + fit["beta_err_by_isotope"][87]
    assert abs(b85 - b87) < 3 * e + 0.02, (b85, b87)


@requires_raw_traces
def test_fit_global_runs_on_real_data():
    # DATA-VALIDATED smoke test: the headline fit must
    # RUN on the actual archive traces, not only on synthetics it generated.
    # Builds 2 peaks x 2 temperatures from data_raw at a fixed sane rate and
    # asserts convergence + a sane chi2_red. (Not a physics claim -- a
    # does-it-run-and-not-crash gate; the real rates come from M2 at pipeline
    # time.)
    import csv as _csv
    from rb5s6s.config import DATA_RAW_DIR, MANIFEST_CSV
    from rb5s6s.ingest import load_trace
    from rb5s6s.density import density_units
    from rb5s6s.constants import PEAKS
    rate_t = 0.08514  # transition axis, the M2 campaign value
    rows = list(_csv.DictReader(open(MANIFEST_CSV)))
    blocks = []
    for peak in ("4192", "4207"):          # one 85Rb, one 87Rb
        for T in ("90", "110"):
            recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "t_sweep"
                    and r["peak"] == peak and r["temperature_C"] == T][:4]
            if len(recs) < 3:
                continue
            fv = [load_trace(DATA_RAW_DIR / r["file"]) for r in recs]
            blocks.append({"peak": peak, "isotope": PEAKS[peak]["isotope"],
                           "T_C": float(T), "N_units": density_units(float(T)),
                           "freqs": [t * rate_t for t, _ in fv],
                           "volts": [v for _, v in fv], "law": None})
    assert len(blocks) >= 3
    fit = fit_global(blocks, transit_ref_mhz=0.9)          # must not raise
    assert 0.3 < fit["chi2_red"] < 5.0, fit["chi2_red"]    # sane fit on real data
    for iso in fit["beta_keys"]:
        assert np.isfinite(fit["beta_by_isotope"][iso])
        assert np.isfinite(fit["beta_err_by_isotope"][iso])


# ---- the three guards of 2026-09-21 (F250, F252, F253), planted both ways -------------------

_BETA = {85: 0.05, 87: 0.02}
_SIGMA = {90.0: 1.4}


def test_a_density_outside_the_vapour_band_is_refused_with_its_units():
    """F250: a harness passed Kelvin to a callee that takes Celsius and handed fit_global
    N_units = 55468 (0.56 is right at 70 C); the first residual built 1.3 million grid points and
    hung for 7h50m. The refusal names the units; the same blocks with a physical density fit."""
    blocks = synth_blocks(_BETA, _SIGMA, temps=(90.0,))
    # EVERY block carries the wrong density, which is F250's own shape (the harness's density
    # helper was wrong for all of them); a single bad block trips the older per-temperature
    # consistency refusal first, which is correct and is not this plant's subject
    bad = [dict(b, N_units=55468.3) for b in blocks]
    with pytest.raises(ValueError, match=r"N_units=5\.547e\+04.*units defect"):
        fit_global(bad, transit_ref_mhz=0.9)
    fit = fit_global(blocks, transit_ref_mhz=0.9)          # the positive: the band admits the record's cells
    assert fit["chi2_red"] < 5.0 and not fit["worse_than_start"]


def test_a_warm_start_of_the_shared_prefix_is_honoured_and_its_shape_checked():
    """F253: a profile by continuation needs a start it can hand over; the shared prefix is the
    caller's, the per-trace seeds stay data-derived, and a wrong length is refused by name."""
    blocks = synth_blocks(_BETA, _SIGMA, temps=(90.0,))
    cold = fit_global(blocks, transit_ref_mhz=0.9)
    shared = list(cold["sigma_laser"]) + [cold["beta_by_isotope"][iso] for iso in cold["beta_keys"]]
    warm = fit_global(blocks, transit_ref_mhz=0.9, p0_shared=shared)
    assert abs(warm["chi2_red"] - cold["chi2_red"]) < 1e-6      # the same minimum, reached from it
    assert warm["cost_at_start"] >= warm["cost"] - 1e-9 and not warm["worse_than_start"]
    with pytest.raises(ValueError, match="shared prefix"):
        fit_global(blocks, transit_ref_mhz=0.9, p0_shared=shared[:-1])


def test_the_start_cost_and_the_budget_are_carried():
    """F252: a minimiser that ends above its own start is named, never returned silently. The
    True branch's live instance is the T0l harness (0.19 MHz at chi2 4.30 against 0.98 at the
    truth); it is not constructible here without a fake solver, so this plant asserts the
    reading's arithmetic on a converged fit and that the budget reaches the solver."""
    blocks = synth_blocks(_BETA, _SIGMA, temps=(90.0,))
    fit = fit_global(blocks, transit_ref_mhz=0.9)
    assert {"cost_at_start", "cost", "worse_than_start"} <= fit.keys()
    assert fit["cost"] <= fit["cost_at_start"] and fit["worse_than_start"] is False
    assert abs(fit["cost"] - 0.5 * fit["chi2_whitened"]) < 1e-6   # one definition, stated twice
    with pytest.raises(RuntimeError, match="global fit failed"):
        fit_global(blocks, transit_ref_mhz=0.9, max_nfev=1)       # a budget of one cannot converge


def test_a_solver_that_ends_worse_than_its_start_or_not_stationary_is_named(monkeypatch):
    """The True branches (F252, F258), manufactured with a fake solver rather than left to a docstring:
    the C3 advancement and twin seats both found them unplanted. The fake returns the start itself
    with a cost above the start's and a large optimality; both flags must read True and neither
    may raise. The False branch is the converged fit the tests above already exercise."""
    import numpy as np
    from rb5s6s import global_fit as G
    blocks = synth_blocks(_BETA, _SIGMA, temps=(90.0,))

    class _Sol:
        def __init__(self, x, cost):
            self.x = x; self.cost = cost; self.success = True; self.message = "fake"
            self.fun = np.zeros(1); self.jac = np.eye(len(x)); self.optimality = 5.4e4; self.nfev = 25

    real = G.least_squares

    def fake(fun, x0, **kw):
        r = real(fun, x0, **kw)                       # the real answer, then a worse cost reported
        return _Sol(r.x, 1e12)                     # above ANY start's cost, whatever the seed

    monkeypatch.setattr(G, "least_squares", fake)
    fit = G.fit_global(blocks, transit_ref_mhz=0.9)
    assert fit["worse_than_start"] is True and fit["not_stationary"] is True
    assert fit["nfev"] == 25 and fit["optimality"] == 5.4e4


def test_the_grouped_jacobian_returns_scipys_own_fit_bitwise_and_costs_nine_evaluations(monkeypatch):
    """F301 (2026-09-22): the column-grouped Jacobian is a cost repair and not a model change, so the fit
    it returns must be scipy's own dense-differencing fit to the last bit, and it must actually group.
    Both ways: the default and `_jac='2-point'` agree bitwise on every returned number, and one grouped
    Jacobian evaluates the residuals nshared + 4 + 1 times (the +1 is its own f0) where the dense
    one evaluates them once per parameter."""
    from rb5s6s import global_fit as G
    blocks = synth_blocks(_BETA, {90.0: 1.4, 110.0: 1.1}, temps=(90.0, 110.0))
    a = fit_global(blocks, transit_ref_mhz=0.9, _jac="2-point")
    b = fit_global(blocks, transit_ref_mhz=0.9)
    for key in ("sigma_laser", "sigma_laser_err", "beta_by_isotope", "beta_err_by_isotope",
                "chi2_red", "cost", "nfev"):
        assert a[key] == b[key], key
    # the grouping is real: count the residual calls one grouped Jacobian makes
    calls = {"n": 0}

    def counted(x):
        calls["n"] += 1
        return np.zeros(8)
    nshared, lens = 3, [2, 3, 3]
    jac = G._grouped_jacobian(counted, np.zeros(nshared + 12), np.full(nshared + 12, np.inf), nshared, lens)
    J = jac(np.ones(nshared + 12))
    assert J.shape == (8, nshared + 12) and J.flags["F_CONTIGUOUS"]
    assert calls["n"] == nshared + 4 + 1, calls["n"]


def test_the_permeated_gas_switch_is_byte_identical_when_off_and_shared_when_on():
    """`fit_gamma_l` plumbed into the joint fit (F426), planted BOTH ways.

    Failure mode it guards: `linefit.fit_condition` has carried `fit_gamma_l` since 2026-08-21 while
    `fit_global` took only a FIXED `gamma_l`, so every committed joint number pins the permeated gas
    at exactly zero with no way to test the assumption. The switch must (a) leave the default path
    bitwise unchanged, so no committed cell moves under it, and (b) add exactly ONE shared parameter
    when thrown, because a permeated gas is one gas in one cell and never one number per block.
    """
    blocks = synth_blocks({85: 0.012, 87: 0.012}, {70.0: 1.4, 90.0: 1.4, 110.0: 1.4}, seed=11)

    off_a = fit_global(blocks, transit_ref_mhz=0.9)
    off_b = fit_global(blocks, transit_ref_mhz=0.9, fit_gamma_l=False)
    assert off_a["beta_by_isotope"] == off_b["beta_by_isotope"], "the default path moved"
    assert off_a["chi2_whitened"] == off_b["chi2_whitened"], "the default path moved"
    assert off_a["gamma_l_fitted"] is False and off_a["gamma_l"] == 0.0
    assert np.isnan(off_a["gamma_l_err"]), "a pinned gas must not report an error bar"

    on = fit_global(blocks, transit_ref_mhz=0.9, fit_gamma_l=True)
    assert on["gamma_l_fitted"] is True
    assert on["nparams"] == off_a["nparams"] + 1, "the gas is ONE shared parameter, not one per block"
    assert on["gamma_l"] >= 0.0 and np.isfinite(on["gamma_l_err"])
    # freeing a parameter cannot raise the whitened cost at the minimum
    assert on["chi2_whitened"] <= off_a["chi2_whitened"] * (1.0 + 1e-6)


def test_p0_shared_names_the_gas_when_the_gas_is_free():
    """The warm-start contract must count the new slot, or a continuation profile silently
    misaligns the shared prefix (A11's own failure mode one parameter over)."""
    blocks = synth_blocks({85: 0.012, 87: 0.012}, {70.0: 1.4, 90.0: 1.4, 110.0: 1.4}, seed=12)
    off = fit_global(blocks, transit_ref_mhz=0.9)
    n_off = len(off["sigma_laser"]) + len(off["beta_by_isotope"])
    with pytest.raises(ValueError, match="gamma_l"):
        fit_global(blocks, transit_ref_mhz=0.9, fit_gamma_l=True,
                   p0_shared=np.ones(n_off))          # one short: the gas's slot is missing
