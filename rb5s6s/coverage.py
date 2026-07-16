"""
Injection-recovery coverage of the collisional bound (M13)
==========================================================

The headline collisional result is an UPPER BOUND with a claimed 95% coverage,
built from a between-block scatter estimated on only one residual degree of
freedom (3 density points, 2 fit parameters) -- which is why the bound uses the
Student-t quantile t(0.95, 1) = 6.31 rather than the Gaussian 2 (methods 4.5,
beta.collisional_slope). A referee's fair question is: does that construction
actually cover the truth 95% of the time, or is it a plausible-looking formula?

This module answers it by simulation. For a grid of TRUE beta values it
generates many synthetic width-vs-density datasets with the archive's own
structure -- three temperatures, a between-block scatter that mimics the
drift-induced wander (the dominant error), plus the small within-block SEM --
runs the SHIPPED estimator `beta.collisional_slope` on each, and measures:

  * BIAS      : mean(beta_eff) - beta_true  (is the point estimate unbiased?)
  * COVERAGE  : fraction of trials with bound95_nscale >= beta_true
                (a valid 95% one-sided upper bound needs >= 0.95)
  * FALSE-POS : at beta_true = 0, the fraction the pre-registered rule would
                call a MEASUREMENT rather than a bound (should be small)

Because the scatter estimate has 1 DOF, the Gaussian-2 bound UNDER-covers and the
t-quantile bound is (conservatively) at or above nominal -- which is exactly the
correction this study is here to verify empirically rather than assert.
"""

from __future__ import annotations

from typing import Dict

import numpy as np

from .beta import collisional_slope
from .density import density_units

# the 3-point headline cooling sweep
_TEMPS = (70.0, 90.0, 110.0)
_N = np.array([density_units(t) for t in _TEMPS])
_W0 = 4.8            # MHz baseline width (natural (x) transit (x) laser, ~constant in N)
_SEM = 0.05         # within-block statistical error per condition (MHz)


def coverage_study(beta_true: float, *, block_sigma: float = 0.12,
                   n_trials: int = 2000, seed: int = 0) -> Dict:
    """Simulate the 3-point collisional bound at a known beta_true and return
    bias, 95% coverage, and (at beta_true = 0) the false-MEASUREMENT rate.

    block_sigma: 1-sigma of the between-block width scatter (the drift proxy,
    the dominant error in the real archive, ~0.06-0.16 MHz)."""
    rng = np.random.default_rng(seed)
    betas, covered, called_meas = [], 0, 0
    E = np.full(3, _SEM)
    for _ in range(n_trials):
        # true line + between-block scatter (common drift-like wander) + within-block noise
        W = _W0 + beta_true * _N \
            + rng.normal(0.0, block_sigma, 3) + rng.normal(0.0, _SEM, 3)
        r = collisional_slope(_N, W, E)
        betas.append(r["beta_eff"])
        if r["bound95_nscale"] >= beta_true:
            covered += 1
        if r["verdict"] == "MEASUREMENT":
            called_meas += 1
    betas = np.array(betas)
    return {
        "beta_true": beta_true, "n_trials": n_trials, "block_sigma": block_sigma,
        "bias": float(betas.mean() - beta_true),
        "scatter": float(betas.std(ddof=1)),
        "coverage": covered / n_trials,
        "false_measurement_rate": called_meas / n_trials,
    }
