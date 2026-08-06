"""
Closure tests for the global beta_self fit (rb5s6s/beta.py).

The gate for the headline collisional-broadening result: before any real
beta_self is believed, the global multi-temperature fit must recover a KNOWN
injected beta_self from campaign-like synthetic data, demonstrate that it
does so where a single-condition fit could not (degeneracy broken by the
density lever arm), and report zero collisional broadening as consistent
with zero.

The second half of the module guards the POOLED width slope of
scripts/run_beta_self.py, pre-registered in
docs/notes/beta_self_pooling_prereg.md: the collapse of the pooled
generalized-least-squares fit onto the four condition means, the closed-form
REML that separates the condition-common from the per-line scatter, and the
shape of the rows the construction adds to results/beta_self_probe.csv.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
import pytest

from rb5s6s import config as C
from rb5s6s.constants import GAMMA_NAT_HZ
from rb5s6s.density import density_units, N_SCALE_FRAC_SYST
from rb5s6s.lineshape import model_profile
from rb5s6s.linefit import to_frequency, transit_fwhm_at_T, fit_condition
from rb5s6s.beta import fit_beta_self, collisional_slope

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import run_beta_self as RBS  # noqa: E402

GNAT = GAMMA_NAT_HZ / 1e6
RATE_T = 0.08514
T_MS = np.arange(2000) * 0.5 - 500.0
NU = to_frequency(T_MS, RATE_T)


def synth_peak(beta_self, sigma_laser, transit_ref=0.9, temps=(70.0, 90.0, 110.0),
               amp=1.0, drift=1.0, noise_a=5e-3, ntr=5, seed=C.RNG_SEED):
    """One peak's worth of synthetic conditions at several temperatures, with
    gamma_coll(T) = beta_self * N(T) (density units), shared sigma_laser."""
    rng = np.random.default_rng(seed)
    conds = []
    for T in temps:
        N = density_units(T)
        gc = beta_self * N
        transit = transit_fwhm_at_T(T, transit_ref)
        freqs, volts = [], []
        for _ in range(ntr):
            c = rng.normal(0.0, drift)
            g = amp * (1.0 + rng.normal(0.0, 0.03))
            prof = model_profile(NU - c, gamma_coll=gc, sigma_laser_fwhm=sigma_laser,
                                 transit_fwhm=transit)
            v = g * prof / prof.max()
            sig = np.sqrt(noise_a ** 2 + 2e-5 * np.maximum(v, 0.0))
            volts.append(v + rng.normal(0.0, 1.0, len(v)) * sig)
            freqs.append(NU.copy())
        conds.append({"T_C": T, "N_units": N, "freqs": freqs, "volts": volts, "law": None})
    return conds


def test_recovers_injected_beta():
    beta_true = 0.15  # MHz per 1e12 cm^-3
    conds = synth_peak(beta_self=beta_true, sigma_laser=1.2)
    fit = fit_beta_self(conds, transit_ref_mhz=0.9)
    assert abs(fit["beta_self"] - beta_true) < 3 * fit["beta_self_err"] + 0.02, fit
    assert abs(fit["sigma_laser"] - 1.2) < 0.25, fit


def test_zero_beta_recovered_near_zero():
    conds = synth_peak(beta_self=0.0, sigma_laser=1.2)
    fit = fit_beta_self(conds, transit_ref_mhz=0.9)
    # consistent with zero within ~3 sigma (bounded below at 0)
    assert fit["beta_self"] < 3 * fit["beta_self_err"] + 0.03, fit


def test_global_beats_single_condition_degeneracy():
    # At a SINGLE temperature the laser/coll split is degenerate and gamma_coll
    # is poorly determined; the GLOBAL fit across 3 T pins beta_self far
    # better. Compare the implied gamma_coll error at 110 C.
    beta_true = 0.20
    conds = synth_peak(beta_self=beta_true, sigma_laser=1.5, noise_a=8e-3)
    single = fit_condition(conds[2]["freqs"], conds[2]["volts"], T_C=110.0,
                           transit_fwhm=transit_fwhm_at_T(110.0, 0.9))
    glob = fit_beta_self(conds, transit_ref_mhz=0.9)
    # global gamma_coll error at 110 C = beta_err * N(110)
    N110 = density_units(110.0)
    glob_gc_err = glob["beta_self_err"] * N110
    assert glob_gc_err < single["gamma_coll_err"], (glob_gc_err, single["gamma_coll_err"])
    assert abs(glob["beta_self"] - beta_true) < 3 * glob["beta_self_err"] + 0.03


@pytest.mark.slow
def test_unbiased_across_seeds():
    beta_true = 0.15
    vals, errs = [], []
    for s in range(1, 8):
        fit = fit_beta_self(synth_peak(beta_self=beta_true, sigma_laser=1.2, seed=s),
                            transit_ref_mhz=0.9)
        vals.append(fit["beta_self"]); errs.append(fit["beta_self_err"])
    mean, sem = np.mean(vals), np.std(vals) / np.sqrt(len(vals))
    assert abs(mean - beta_true) < 3 * sem + 0.02, (mean, sem, vals)


def test_collisional_slope_clean_monotonic_is_measurement():
    # Widths rising cleanly with density, tiny within-block errors and small
    # residual => a MEASUREMENT-quality slope.
    N = np.array([density_units(t) for t in (70.0, 90.0, 110.0)])
    beta = 0.05
    W = 5.0 + beta * N          # perfectly on the line
    E = np.array([0.01, 0.01, 0.01])
    res = collisional_slope(N, W, E)
    assert res["monotonic"] and res["verdict"] == "MEASUREMENT"
    assert abs(res["beta_eff"] - beta) < 0.01
    assert res["resid_rms"] < 0.02


def test_collisional_slope_nonmonotonic_is_bound():
    # A non-monotonic width sequence (higher density -> narrower somewhere)
    # cannot be pure collisional broadening: large residual, BOUND verdict,
    # and the between-block systematic must dwarf the formal error.
    N = np.array([density_units(t) for t in (70.0, 90.0, 110.0)])
    W = np.array([5.11, 4.87, 5.28])  # the real 4207 pattern
    E = np.array([0.07, 0.03, 0.02])
    res = collisional_slope(N, W, E)
    assert not res["monotonic"] and res["verdict"] == "BOUND"
    assert res["syst_err"] > 2 * res["formal_err"]  # systematic dominates


def test_collisional_slope_bound_coverage_construction():
    # The 95% bound must honour the scatter's own degrees of freedom (Student-t,
    # NOT the asymptotic 2) and carry the density-scale systematic on top.
    from scipy.stats import t as student_t
    from rb5s6s.density import N_SCALE_FRAC_SYST

    # 3 points -> dof = 1 -> t95 = 6.31; 4 points -> dof = 2 -> t95 = 2.92
    N3 = np.array([density_units(t) for t in (70.0, 90.0, 110.0)])
    r3 = collisional_slope(N3, np.array([5.11, 4.87, 5.28]),
                           np.array([0.07, 0.03, 0.02]))
    assert r3["dof"] == 1
    assert abs(r3["t95"] - student_t.ppf(0.95, 1)) < 1e-9      # 6.314
    assert abs(r3["bound95"] - (abs(r3["beta_eff"]) + r3["t95"] * r3["syst_err"])) < 1e-12

    N4 = np.array([density_units(t) for t in (70.0, 90.0, 110.0, 130.0)])
    r4 = collisional_slope(N4, np.array([5.11, 4.87, 5.28, 5.35]),
                           np.array([0.07, 0.03, 0.02, 0.03]))
    assert r4["dof"] == 2
    assert abs(r4["t95"] - student_t.ppf(0.95, 2)) < 1e-9      # 2.920

    # the N-scale inflation rides on the + side of the bound
    for r in (r3, r4):
        assert r["n_frac_syst"] == N_SCALE_FRAC_SYST
        assert abs(r["bound95_nscale"] - r["bound95"] * (1 + N_SCALE_FRAC_SYST)) < 1e-12
        assert r["bound95_nscale"] > r["bound95"]


# ---------------------------------------------------------------------------
# The pooled width slope (docs/notes/beta_self_pooling_prereg.md)
# ---------------------------------------------------------------------------
POOL_N = np.array([density_units(t) for t in RBS.POOL_CONDITIONS_C])
PROBE_CSV = Path(C.RESULTS_DIR) / "beta_self_probe.csv"


def synth_pool_table(beta_true=0.012, floors=(4.82, 5.01, 5.14, 5.30),
                     s_c=0.07, s_ind=0.13, within=0.05, seed=7):
    """A balanced four-by-four width table with a KNOWN shared slope.

    Built the way the pre-registration describes the data: one floor per line,
    one shared slope, one condition-common departure drawn once per condition
    and applied to every line, and one per-line departure per point."""
    rng = np.random.default_rng(seed)
    common = rng.normal(0.0, s_c, len(POOL_N))
    W = np.array([f + beta_true * POOL_N + common
                  + rng.normal(0.0, s_ind, len(POOL_N)) for f in floors])
    return POOL_N, W, np.full(W.shape, within)


def explicit_gls_slope(N, W, s_c2, s_ind2):
    """Slope and slope error from a GLS written out on all sixteen points.

    Per-line floors and a shared slope in the design matrix, the two-component
    covariance built in full rather than collapsed. This is the reference the
    collapse identity is checked against, and it shares no code with it."""
    n_line, n_cond = W.shape
    y = W.reshape(-1)
    Z = np.zeros((n_line * n_cond, n_cond))
    X = np.zeros((n_line * n_cond, n_line + 1))
    for i in range(n_line):
        for p in range(n_cond):
            k = i * n_cond + p
            Z[k, p] = 1.0
            X[k, i] = 1.0
            X[k, n_line] = N[p]
    inv = np.linalg.inv(s_ind2 * np.eye(n_line * n_cond) + s_c2 * (Z @ Z.T))
    cov_b = np.linalg.inv(X.T @ inv @ X)
    b = cov_b @ X.T @ inv @ y
    return float(b[-1]), float(np.sqrt(cov_b[-1, -1]))


def test_pooled_gls_collapses_onto_the_condition_means():
    """The identity the pre-registration's estimator rests on (section 2).

    On the balanced design the pooled GLS slope IS the floor-plus-slope fit of
    the four condition-mean widths, and its variance IS V/S_NN with
    V = s_c^2 + s_ind^2/n_line. The slope half of that holds for ANY pair of
    variance components, which is the strong form: the estimator does not
    depend on the separation at all, only its error does."""
    N, W, E = synth_pool_table()
    pooled = RBS.pooled_width_slope(N, W, E)

    b_gls, se_gls = explicit_gls_slope(N, W, pooled["s_c2"], pooled["s_ind2"])
    assert abs(b_gls - pooled["beta_eff"]) < 1e-13, (b_gls, pooled["beta_eff"])
    assert abs(se_gls - pooled["syst_err"]) < 1e-13, (se_gls, pooled["syst_err"])

    # any components at all, including the s_c = 0 corner
    for s_c2, s_ind2 in ((0.0, 0.02), (0.005, 0.018), (0.05, 1e-4)):
        b2, se2 = explicit_gls_slope(N, W, s_c2, s_ind2)
        assert abs(b2 - pooled["beta_eff"]) < 1e-13
        assert abs(se2 - np.sqrt((s_c2 + s_ind2 / W.shape[0]) / pooled["S_NN"])) < 1e-13

    # and the same identity read the other way: the equal-weight per-line
    # slopes average to the pooled slope exactly
    assert abs(float(np.mean(pooled["slopes_line"])) - pooled["beta_eff"]) < 1e-15

    # known truth, recovered inside the error the construction quotes
    assert abs(pooled["beta_eff"] - 0.012) < 3 * pooled["syst_err"], pooled["beta_eff"]
    assert pooled["verdict"] == "BOUND"


def test_pooled_reml_matches_a_numerical_restricted_likelihood():
    """The closed-form REML is the balanced-design solution, not an ansatz.

    Checked against a direct numerical maximization of the restricted
    likelihood with the covariance written out in full, from several starts."""
    from scipy.optimize import minimize

    N, W, E = synth_pool_table(seed=11)
    pooled = RBS.pooled_width_slope(N, W, E)

    n_line, n_cond = W.shape
    y = W.reshape(-1)
    Z = np.zeros((n_line * n_cond, n_cond))
    X = np.zeros((n_line * n_cond, n_line + 1))
    for i in range(n_line):
        for p in range(n_cond):
            k = i * n_cond + p
            Z[k, p] = 1.0
            X[k, i] = 1.0
            X[k, n_line] = N[p]

    def m2_log_lr(theta):
        s_c2, s_ind2 = np.exp(theta)
        cov_y = s_ind2 * np.eye(n_line * n_cond) + s_c2 * (Z @ Z.T)
        inv = np.linalg.inv(cov_y)
        A = X.T @ inv @ X
        r = y - X @ np.linalg.solve(A, X.T @ inv @ y)
        return (np.linalg.slogdet(cov_y)[1] + np.linalg.slogdet(A)[1]
                + float(r @ inv @ r))

    best = min((minimize(m2_log_lr, [a, b], method="Nelder-Mead",
                         options=dict(xatol=1e-12, fatol=1e-12, maxiter=20000))
                for a in (-8.0, -5.0, -2.0) for b in (-8.0, -5.0, -2.0)),
               key=lambda r: r.fun)
    s_c2, s_ind2 = np.exp(best.x)
    assert abs(s_c2 - pooled["s_c2"]) < 1e-5 * pooled["s_c2"], (s_c2, pooled["s_c2"])
    assert abs(s_ind2 - pooled["s_ind2"]) < 1e-5 * pooled["s_ind2"]
    assert abs(s_c2 + s_ind2 / n_line - pooled["V"]) < 1e-5 * pooled["V"]
    # the interior solution puts every degree of freedom of V in the
    # condition-mean mean square, which is the four means constraining a line
    assert not pooled["reml_at_bound"]
    assert abs(pooled["dof"] - (n_cond - 2)) < 1e-12


def test_pooled_anchor_share_is_the_computed_leverage():
    """The 70 C narrowing's share is arithmetic on the fit, not a typed number.

    A table exactly on its own line has nothing to attribute. Depressing the
    coldest condition on every line by a known amount then moves the pooled
    slope by lever*delta, and the reported share is that change over the
    slope."""
    N = POOL_N
    W = np.array([f + 0.012 * N for f in (4.82, 5.01, 5.14, 5.30)])
    pooled = RBS.pooled_width_slope(N, W)
    flat = RBS.anchor_narrowing_share(pooled, N, RBS.POOL_CONDITIONS_C)
    assert abs(flat["share"]) < 1e-12
    assert flat["anchor_C"] == 70.0

    delta = 0.10                       # MHz of narrowing at the cold anchor
    W2 = W.copy()
    W2[:, 0] -= delta
    p2 = RBS.pooled_width_slope(N, W2)
    a2 = RBS.anchor_narrowing_share(p2, N, RBS.POOL_CONDITIONS_C)
    assert a2["share"] > 0                       # narrowing STEEPENS the slope
    assert a2["n_lines_low"] == W.shape[0]
    # the anchor sits low but by less than the injection, because the refitted
    # line follows it part of the way down
    assert 0.0 < a2["shortfall_mhz"] < delta

    # closure: the reported share is the fractional slope change of a real
    # refit with the anchor mean lifted onto the line, not a restatement of
    # the leverage formula
    lifted = W2.copy()
    lifted[:, 0] -= float(p2["resid_cond"][0])
    p3 = RBS.pooled_width_slope(N, lifted)
    assert abs(p3["beta_eff"] - a2["slope_without"]) < 1e-12
    assert abs(a2["share"]
               - (p2["beta_eff"] - p3["beta_eff"]) / p2["beta_eff"]) < 1e-12

    # and it is the conservative reading of the injection: attributing only the
    # measured departure from the line credits less to the narrowing than
    # assuming the whole known delta, because the fit absorbs the rest
    assert a2["share"] < -float(p2["lever"][0]) * delta / p2["beta_eff"]


def test_pooled_isotope_split_error_drops_the_common_mode():
    """The split's error is the per-line component alone (note section 1).

    Adding an arbitrary condition-common offset to every line changes both
    group slopes together and must leave the split and its error untouched."""
    N, W, E = synth_pool_table(seed=3)
    groups = [87, 85, 85, 87]
    pooled = RBS.pooled_width_slope(N, W, E)
    split = RBS.pooled_group_split(N, W, groups, pooled["s_ind2"])
    shifted = W + np.array([0.3, -0.2, 0.5, -0.4])[None, :]
    split2 = RBS.pooled_group_split(N, shifted, groups, pooled["s_ind2"])
    assert abs(split2["diff"] - split["diff"]) < 1e-13
    assert abs(split2["se"] - split["se"]) < 1e-15
    assert split["label"] == "87 minus 85"
    # the closed form the docstring quotes
    expect = np.sqrt(pooled["s_ind2"] * (1 / 2 + 1 / 2) / pooled["S_NN"])
    assert abs(split["se"] - expect) < 1e-15


def _probe_rows():
    if not PROBE_CSV.exists():
        pytest.skip("results/beta_self_probe.csv not in this checkout")
    return list(csv.DictReader(open(PROBE_CSV)))


def test_pooled_bound_reproduces_on_the_committed_table():
    """Every pooled number in the committed table rebuilds from the others.

    The bound is |slope| + t(0.95, dof_eff) * sqrt(V/S_NN) with
    V = s_c^2 + s_ind^2/4, then the density-scale inflation. S_NN comes from
    the density model rather than from the file, so this is a real recompute of
    the quoted bound and not a restatement of it."""
    from scipy.stats import t as student_t

    rows = {r["peak"]: r for r in _probe_rows()}
    if "pooled_slope" not in rows:
        pytest.skip("pooled rows absent (run scripts/run_beta_self.py)")
    head = rows["pooled_slope"]
    s_c = float(rows["pooled_s_c"]["beta_eff"])
    s_ind = float(rows["pooled_s_ind"]["beta_eff"])
    n_line = 4

    V = s_c ** 2 + s_ind ** 2 / n_line
    assert abs(np.sqrt(V) - float(head["resid_rms"])) < 1e-12

    S_NN = float(np.sum((POOL_N - POOL_N.mean()) ** 2))
    se = np.sqrt(V / S_NN)
    assert abs(se - float(head["syst_err"])) < 1e-12

    dof = float(head["dof"])
    t95 = float(student_t.ppf(0.95, dof))
    assert abs(t95 - float(head["t95"])) < 1e-12
    bound = abs(float(head["beta_eff"])) + t95 * se
    assert abs(bound - float(head["bound95"])) < 1e-12
    assert abs(float(head["n_frac_syst"]) - N_SCALE_FRAC_SYST) < 1e-12
    assert abs(bound * (1 + N_SCALE_FRAC_SYST)
               - float(head["bound95_nscale"])) < 1e-12

    # the common-mode fraction and its profile range
    f = s_c ** 2 / (s_c ** 2 + s_ind ** 2)
    assert abs(f - float(rows["pooled_f_common"]["beta_eff"])) < 1e-12
    assert (float(rows["pooled_f_common_lo"]["beta_eff"]) <= f
            <= float(rows["pooled_f_common_hi"]["beta_eff"]))

    # the gain the pre-registration's prediction 3 is stated on
    worst = max(float(r["bound95_nscale"]) for r in _probe_rows()
                if r.get("headline") == "yes")
    gain = worst / float(head["bound95_nscale"])
    assert abs(gain - float(rows["pooled_gain_vs_worst_perline"]["beta_eff"])) < 1e-9

    # the per-line component must SUBSUME the within-block error, never sit
    # below it: a table quieter than its own error bars would mean the
    # decomposition is not describing the data
    assert s_ind > float(rows["pooled_rms_within"]["beta_eff"])


def test_pooled_rows_do_not_disturb_the_per_line_table():
    """Schema guard on the rows the pooling adds.

    The file is one table with one header, the four per-line rows stay first
    and stay the only headline rows (every consumer selects on that: the
    ledger, fig19's quoted bound, tests/test_coverage.py and
    tests/test_docs_canonical.py), and every added row is prefixed so it cannot
    be mistaken for a peak."""
    rows = _probe_rows()
    if not any(r["peak"].startswith("pooled_") for r in rows):
        pytest.skip("pooled rows absent (run scripts/run_beta_self.py)")

    fields = list(rows[0].keys())
    assert None not in fields and all(None not in r.values() for r in rows), \
        "a row carries more fields than the header: the table has split in two"
    assert fields[:3] == ["peak", "variant", "headline"]

    headline = [r for r in rows if r["headline"] == "yes"]
    assert [r["peak"] for r in headline] == list(RBS.PEAKS)
    assert [r["peak"] for r in rows[:4]] == list(RBS.PEAKS)
    assert all(r["peak"].startswith("pooled_") for r in rows[4:])
    assert all(r["status"] == "BOUND" for r in rows)

    names = {r["peak"] for r in rows[4:]}
    assert names == {
        "pooled_slope", "pooled_s_c", "pooled_s_ind", "pooled_rms_within",
        "pooled_f_common", "pooled_f_common_lo", "pooled_f_common_hi",
        "pooled_gain_vs_worst_perline", "pooled_share_70C",
        "pooled_isotope_split", "pooled_perline_chi2"}, names
    assert all(r["beta_eff"] != "" for r in rows[4:]), \
        "every pooled row carries its value in beta_eff"

    head = next(r for r in rows if r["peak"] == "pooled_slope")
    assert head["verdict"] == "BOUND"          # frozen by note section 3
    assert all(head[k] != "" for k in
               ("beta_eff", "formal_err", "syst_err", "resid_rms", "snr", "dof",
                "t95", "bound95", "n_frac_syst", "bound95_nscale", "monotonic"))


@pytest.mark.slow
def test_with_130C_extends_lever_arm():
    # Adding the 130 C (highest-density) point should tighten beta_self.
    beta_true = 0.15
    three = fit_beta_self(synth_peak(beta_self=beta_true, sigma_laser=1.2,
                                     temps=(70.0, 90.0, 110.0)), transit_ref_mhz=0.9)
    four = fit_beta_self(synth_peak(beta_self=beta_true, sigma_laser=1.2,
                                    temps=(70.0, 90.0, 110.0, 130.0)), transit_ref_mhz=0.9)
    assert four["beta_self_err"] < three["beta_self_err"], (four, three)
