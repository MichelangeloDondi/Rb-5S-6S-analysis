"""
Is the per-T sigma_laser sharing statistically warranted? A BIC comparison (M14)
================================================================================

The hierarchical beta (global_fit, M4b) shares one sigma_laser(T) across the four
peaks at each temperature (Model A, "per_T"); the conservative alternative frees
sigma_laser per (peak, T) block (Model B, "per_block"). The choice is not cosmetic
-- sharing pins sigma_laser lower at high density and reassigns width to
collisions, raising the hierarchical beta -- so a referee fairly asks: how much
EVIDENCE does the archive carry for the sharing, beyond "chi2_red < 1 is
compatible with it" (M4c)?

Both models are fit with the SAME machinery (global_fit); the only difference is
the sigma_laser grouping -- 3 params (one per T) for per_T vs 12 (one per peak-T
block) for per_block, so Model B has 9 more free parameters. per_T is a nested
restriction of per_block, so chi2(per_block) <= chi2(per_T) always, and

    BIC = chi2 + k*ln(N)                          (lower is better)
    dBIC = BIC(per_block) - BIC(per_T) ;  dBIC > 0 favours per_T (shared)
    Kass-Raftery: |dBIC| < 2 negligible, 2-6 positive, 6-10 strong, >10 decisive.

THE CORRELATED-SAMPLE TRAP (why this needs care). Each trace is a smooth line
sampled at ~2000 highly-correlated points, so the ~49k raw samples are NOT 49k
independent observations. Using raw N over-counts BOTH the chi2 improvement and
the ln(N) penalty, and on this archive it flips the verdict: with raw N the per-
block fit's tiny chi2 gain (the archive's noise model whitens by sqrt(tau_int),
tau ~ 3.5) is inflated ~tau-fold and per_block "wins" (dBIC ~ -46); with the
matching EFFECTIVE sample size N_eff = N/tau and the whitened chi2, per_T wins
(dBIC ~ +62). The effective-N BIC is the statistically correct one -- you cannot
treat correlated samples as independent -- so it is the primary number here; the
raw-N value is reported only as the cautionary diagnostic it is. (This module
returns both; `dBIC` is the effective one, `dBIC_raw` the naive one.)

WHAT THIS DOES AND DOES NOT SETTLE. Even the effective-N dBIC scores PARSIMONY --
whether the data can pay for 9 extra parameters -- not the PHYSICS of sharing.
Four peaks that co-drifted between unlogged acquisitions would look shared too
(M4c), and no in-sample score can recover the timing. So dBIC > 0 reads "the
archive cannot justify per-block freedom" (Occam on underpowered data), NOT "the
sharing is confirmed". That the sign even flips with the sample counting is itself
the headline: the archive does not robustly resolve shared-vs-independent,
exactly as M4c frames it. The headline result stays the model-INDEPENDENT
width-slope bound (C1); this only turns the M4c consistency check into a number.

The closure test (tests/test_sharing_bic.py) uses clean synthetics (tau = 1, so
effective == raw): the score must favour per_T when the four peaks genuinely share
one sigma_laser and per_block when they carry grossly different ones -- i.e. it
detects real sharing structure when the data have the power the archive lacks.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np

from .global_fit import fit_global


def _verdict(dbic: float) -> str:
    a = abs(dbic)
    return ("negligible" if a < 2 else "positive" if a < 6
            else "strong" if a < 10 else "decisive")


def sharing_bic(blocks: List[Dict], *, transit_ref_mhz: float,
                transit_kind: str = "exp", T_ref_C: float = 110.0) -> Dict:
    """Compare Model A (sigma_laser per_T) with Model B (per_block) by BIC,
    fitting BOTH with global_fit, using the correlation-corrected effective
    sample size as primary and the raw-sample count as a diagnostic.

    Returns each model's counts and both BICs, plus
      dBIC     = BIC_eff(per_block) - BIC_eff(per_T)   (PRIMARY; >0 favours per_T)
      dBIC_raw = the naive raw-N version (over-counts correlated samples)
    and `robust` = whether the two agree in sign.
    """
    models = {}
    for sharing in ("per_T", "per_block"):
        r = fit_global(blocks, sigma_sharing=sharing, transit_ref_mhz=transit_ref_mhz,
                       transit_kind=transit_kind, T_ref_C=T_ref_C)
        k = int(r["nparams"])
        n_raw, n_eff = int(r["ndata"]), float(r["ndata_eff"])
        chi2_raw = float(r["chi2_red"]) * max(n_raw - k, 1)
        chi2_eff = float(r["chi2_whitened"])
        models[sharing] = {
            "k": k, "n_raw": n_raw, "n_eff": n_eff,
            "chi2_raw": chi2_raw, "chi2_eff": chi2_eff,
            "bic_raw": chi2_raw + k * np.log(n_raw),
            "bic_eff": chi2_eff + k * np.log(n_eff),
            "chi2_red": float(r["chi2_red"]), "n_sigma_params": len(r["sig_keys"]),
        }
    dbic_eff = models["per_block"]["bic_eff"] - models["per_T"]["bic_eff"]
    dbic_raw = models["per_block"]["bic_raw"] - models["per_T"]["bic_raw"]
    return {
        "models": models,
        "dBIC": float(dbic_eff), "dBIC_raw": float(dbic_raw),
        "verdict": _verdict(dbic_eff),
        "favours": "per_T (shared)" if dbic_eff > 0 else "per_block (independent)",
        "tau_mean": float(models["per_T"]["n_raw"] / models["per_T"]["n_eff"]),
        "delta_k": models["per_block"]["k"] - models["per_T"]["k"],
        "robust": bool((dbic_eff > 0) == (dbic_raw > 0)),
    }
