"""
Intra-scan (within-scan) drift closure test for the drift-immune ramp method.

THEORY_NOTE §3 rests the whole method on a timescale separation: the 2025 lock
drifts at ~MHz/min, but a single ~1 s scan sees only a fraction of that, so the
per-trace free centre absorbs the shift and the ramp's shape asymmetry (the
skew, the light-shift observable) survives. The between-scan half is validated
elsewhere (it is why beta_self is a bound); the within-scan injection was argued
only by timescale separation. A hostile referee's objection is fair: MHz/min
drift *within* a scan is not a pure translation, and skew is exactly the ramp
observable, so an unmodelled within-scan skew would bias the light shift.

This test injects the drift and measures the resulting bias. A synthetic scan is
the composite line (rb5s6s.lineshape.model_profile) sampled on the nominal
frequency axis while the laser drifts across the 1 s sweep; the asymmetry is
recovered the way the pipeline recovers it -- a free-centre fit with floating
widths (linefit.fit_condition lets the drift live in the per-trace centre, and
the widths take up a symmetric stretch), reading the ramp coefficient s0
(THEORY_NOTE §3: the moments are read from the fitted function, not the raw
trace, so they stay finite and window-independent).

Result (this seed and geometry): the fitted asymmetry is biased by only a few
x 1e-3 at the archival within-scan drift -- about 1% of the SNR~130 statistical
error on s0 -- and the bias grows ~linearly with the drift rate, reaching
order-s0 only at tens of times the archival value, a rate the lock never
approached. The ~0.1 MHz within-scan claim is therefore backed by a measured
coverage number, not just timescale separation. If a future geometry surfaced a
real bias at the archival rate it would become a stated systematic in RESULTS.md
/ THEORY_NOTE §3; at the archival geometry it does not.
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.optimize import least_squares

from rb5s6s import config
from rb5s6s.constants import (
    DRIFT_RATE_LASER_HZ_PER_MIN, TRACE_DT_S, TRACE_N_POINTS)
from rb5s6s.lineshape import model_profile, ramp_moment_contributions

# Archival composite line (transition axis, MHz): natural + a modest collisional
# Lorentzian, a narrow laser kernel, the ~50 um transit cusp, and an archival-
# scale AC-Stark ramp (s0 = 0.6 MHz, as in test_fringe_tail).
_TRUE = dict(gamma_coll=0.3, sigma_laser_fwhm=0.2, transit_fwhm=1.2, s0=0.6)
_S0_TRUE = _TRUE["s0"]
_W_MHZ = 15.0                 # +-analysis / acquisition window (a few FWHM)
_N = TRACE_N_POINTS           # 2000 samples across the scan
_SNR = 130.0                  # THEORY_NOTE peak-SNR floor at <=225 mW

# Archival within-scan drift on the TRANSITION axis. The lock drifts on the
# LASER axis at DRIFT_RATE_LASER_HZ_PER_MIN; the two-photon resonance moves at
# twice that, and one scan lasts TRACE_N_POINTS * TRACE_DT_S = 1.000 s:
#   2 * 4 MHz/min * (1 s / 60 s) ~ 0.133 MHz  (~the §3 "<=0.1 MHz within-scan").
_SCAN_S = TRACE_N_POINTS * TRACE_DT_S
_DRIFT_ARCHIVAL_MHZ = 2.0 * (DRIFT_RATE_LASER_HZ_PER_MIN / 1e6) * (_SCAN_S / 60.0)


def _peak0() -> float:
    return float(model_profile(np.array([0.0]), **_TRUE)[0])


def _scan(lin_mhz, quad_mhz=0.0, direction=+1, noise=False, seed=0):
    """One synthetic scan. The laser frequency drifts across the sweep by
    lin_mhz (endpoint-to-endpoint linear) plus quad_mhz (an accelerating
    quadratic bow); the line recorded at nominal frequency nu is the true line
    at nu + drift(scan-time). direction=-1 reverses the sweep (the drift then
    correlates with frequency the other way)."""
    nu = np.linspace(-_W_MHZ, _W_MHZ, _N)
    u = np.linspace(0.0, 1.0, _N)                 # scan-time fraction (linear sweep)
    if direction < 0:
        u = u[::-1]
    delta = lin_mhz * u + quad_mhz * u * u
    y = model_profile(nu + delta, **_TRUE)
    if noise:
        rng = np.random.default_rng(config.RNG_SEED + seed)
        y = y + rng.normal(0.0, _peak0() / _SNR, _N)
    return nu, y


def _fit_s0(nu, y) -> float:
    """Recover the ramp asymmetry as the pipeline does: a free-centre fit with
    floating widths (A, centre, gamma_coll, transit_fwhm, s0, baseline). The
    narrow laser kernel is held at its independently-known value. Returns the
    fitted asymmetry coefficient s0."""
    def resid(p):
        amp, cen, gc, tf, s0, base = p
        prof = model_profile(nu - cen, gamma_coll=max(gc, 0.0),
                             sigma_laser_fwhm=_TRUE["sigma_laser_fwhm"],
                             transit_fwhm=max(tf, 1e-3), s0=max(s0, 1e-6))
        return amp * prof + base - y
    amp0 = y.max() / _peak0()
    sol = least_squares(
        resid, x0=[amp0, float(nu[np.argmax(y)]), 0.3, 1.2, 0.5, 0.0],
        bounds=([0.0, -5.0, 0.0, 0.1, 1e-3, -1.0],
                [np.inf, 5.0, 3.0, 5.0, 5.0, 1.0]), max_nfev=400)
    return float(sol.x[4])


def _bias(lin_mhz, quad_mhz=0.0, direction=+1) -> float:
    """Deterministic (noiseless) drift-induced bias on the fitted asymmetry."""
    return _fit_s0(*_scan(lin_mhz, quad_mhz, direction)) - _S0_TRUE


# --------------------------------------------------------------------------- #
# fast                                                                         #
# --------------------------------------------------------------------------- #
def test_clean_fit_recovers_injected_asymmetry():
    """Baseline closure: with no drift and no noise the free-centre fit returns
    the injected s0 to numerical precision, and the ramp moments it encodes
    (pull = -2/3 s0, kappa3 = s0^3/135; THEORY_NOTE §3) follow."""
    s0 = _fit_s0(*_scan(0.0))
    assert s0 == pytest.approx(_S0_TRUE, abs=1e-4), s0
    m = ramp_moment_contributions(s0)
    assert m["pull"] == pytest.approx(-2.0 / 3.0 * _S0_TRUE, rel=2e-3), m
    assert m["kappa3"] == pytest.approx(_S0_TRUE ** 3 / 135.0, rel=2e-3), m


def test_archival_linear_drift_leaves_asymmetry_unbiased():
    """The dominant archival drift is ~linear over 1 s. The centroid shifts (the
    pull the per-trace free centre absorbs) but the fitted asymmetry is unbiased:
    a linear sweep warp is a near-affine stretch the floating width takes up, not
    a spurious skew. Measured bias ~ -3e-3 on s0 = 0.6."""
    nu, y = _scan(_DRIFT_ARCHIVAL_MHZ)
    # the line centroid HAS moved (drift is active, not a no-op) ...
    centroid = float((nu * y).sum() / y.sum())
    assert abs(centroid) > 0.02, centroid
    # ... yet the recovered asymmetry is essentially unchanged
    assert abs(_fit_s0(nu, y) - _S0_TRUE) < 8e-3, _fit_s0(nu, y)


def test_bias_grows_with_drift_rate():
    """The asymmetry bias grows monotonically with the within-scan drift rate:
    negligible at the archival rate, order-s0 only at tens of times it."""
    b = {k: abs(_bias(k * _DRIFT_ARCHIVAL_MHZ)) for k in (1, 10, 30)}
    assert b[1] < b[10] < b[30], b
    assert b[1] < 8e-3, b            # archival: << s0
    assert b[30] > 0.05, b           # 30x stress: a material fraction of s0


def test_byte_reproducible_at_fixed_seed():
    a = _fit_s0(*_scan(_DRIFT_ARCHIVAL_MHZ, quad_mhz=_DRIFT_ARCHIVAL_MHZ,
                       noise=True, seed=3))
    b = _fit_s0(*_scan(_DRIFT_ARCHIVAL_MHZ, quad_mhz=_DRIFT_ARCHIVAL_MHZ,
                       noise=True, seed=3))
    assert a == b, (a, b)


# --------------------------------------------------------------------------- #
# slow (high-statistics coverage)                                             #
# --------------------------------------------------------------------------- #
@pytest.mark.slow
def test_archival_bias_is_within_the_noise_error():
    """Coverage number. The deterministic drift bias at the archival within-scan
    drift -- linear plus an equal accelerating quadratic bow (a conservative
    curvature) -- is a small fraction of the SNR~130 statistical error on the
    fitted asymmetry. So at the archival rate the asymmetry is 'unbiased within
    its error'. Measured: bias ~0.02-0.03, sigma_s0 ~0.3 => ratio ~0.1."""
    bias = abs(_bias(_DRIFT_ARCHIVAL_MHZ, quad_mhz=_DRIFT_ARCHIVAL_MHZ))
    draws = np.array([_fit_s0(*_scan(0.0, noise=True, seed=s)) for s in range(60)])
    sigma = float(draws.std(ddof=1))
    assert bias / sigma < 0.25, (bias, sigma)
    # the noise-only estimator is itself unbiased (weakly identified -> wide)
    assert draws.mean() == pytest.approx(_S0_TRUE, abs=0.15), draws.mean()


@pytest.mark.slow
def test_bias_is_scan_direction_dependent_at_stress():
    """THEORY_NOTE §3: within-scan drift smears the line in a scan-direction-
    dependent way. Negligibly so at the archival rate, but at a stress rate the
    two sweep directions leave a measurably different residual asymmetry -- the
    fingerprint that this is a genuine within-scan (not between-scan) effect."""
    stress = 30.0 * _DRIFT_ARCHIVAL_MHZ
    fwd = _bias(0.0, quad_mhz=stress, direction=+1)
    rev = _bias(0.0, quad_mhz=stress, direction=-1)
    assert abs(fwd - rev) > 0.02, (fwd, rev)
    # at the archival rate the direction split is negligible
    a_fwd = _bias(0.0, quad_mhz=_DRIFT_ARCHIVAL_MHZ, direction=+1)
    a_rev = _bias(0.0, quad_mhz=_DRIFT_ARCHIVAL_MHZ, direction=-1)
    assert abs(a_fwd - a_rev) < 8e-3, (a_fwd, a_rev)


# --------------------------------------------------------------------------
# Intra-BLOCK (between repeats) position variation: jitter, not drift.
# --------------------------------------------------------------------------
# Distinct from the intra-SCAN drift above. The experimenter confirmed nothing
# was moved within a 5-repeat block, so repeat positions are comparable and
# repeat_idx is their time order. If the 0.08 MHz scatter were accumulated
# drift it would trend with that index; it does not. This matters because
# docs/PREREGISTRATION_timestamps.md derived a block DURATION by dividing that
# scatter by a drift rate, which is only valid if it is drift.
def test_intra_block_scatter_is_jitter_not_drift():
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "scripts"))
    from run_intrablock_trend import blocks, JUMP_MS
    from scipy import stats

    R = blocks()
    clean = R[R["std"] < JUMP_MS]
    assert len(clean) >= 20, "too few scatter-like blocks to conclude anything"
    # DATA.md section 2 quotes 1.8 ms; confirm the ledger against the data
    assert clean["std"].median() == pytest.approx(1.8, abs=0.5)
    null = 1.0 / (clean.n - 1)
    _, p = stats.ttest_1samp(clean.r2 - null, 0.0)
    assert p > 0.05, (
        "intra-block positions now show a monotonic trend with repeat index, "
        "i.e. the scatter IS accumulating drift. PREREGISTRATION D4 was voided "
        "on the opposite finding and must be reinstated and re-argued."
    )


def test_ruler_blocks_stay_excluded_from_that_test():
    """Pooling the RF-on ruler blocks in inflates the apparent intra-block
    scatter ~7x (peak_pos_ms locks onto different comb teeth there, so it
    measures tooth identification, not the laser). That error was made once."""
    import pandas as pd
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    d = pd.read_csv(root / "results" / "qc_metrics.csv")
    d = d[d.flag == "canonical"]
    rf_on = d[d.rf_on].groupby(
        ["role", "peak", "temperature_C"], dropna=False).peak_pos_ms.std()
    assert rf_on.median() > 50, (
        "ruler-block position scatter is no longer large; if peak_pos_ms now "
        "tracks a consistent tooth, run_intrablock_trend.py may include them"
    )
