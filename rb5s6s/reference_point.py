"""The archive point: the widths of the 2025 line at its reference condition, DERIVED, never typed.

A twin, a coverage study or a forecast needs one representative line to generate: the collisional width,
the laser's Gaussian and the transit at the archive's reference condition (the p-sweep, 4154, 130 C, 225 mW).
Until 2026-09-22 about a dozen producers typed that point as literals (gamma 0.55 to 0.58, sigma 1.56 to 1.6,
transit 0.9575 MHz), which were the line's decomposition at a waist convention owner order O44 retired. The
convention moved, the fits moved with it, and the literals did not (F313): the twin went on generating the
retired waist's line while its own note said the truth was read from a committed condition.

So the point is read here, once: the collisional width and the laser width from the committed fit of the
reference condition (`results/linefit_conditions.csv`, regenerated with the fit whenever the model or the
waist moves), and the transit from `constants.transit_fwhm_from_w0` at the waist the record carries
(`config.W0_CENTRAL_M`). A producer that needs the archive's line imports `reference_point()`; nothing types it.

The fit is the record's decomposition at the calculated waist, and it is a BOUND like every absolute width
here: the waist is calculated and never profiled, and the laser width and the transit trade through it.
"""
from __future__ import annotations

import csv
from typing import Dict, Optional

from . import config as C
from . import constants as K

#: the reference condition, as `results/linefit_conditions.csv` keys it (role, peak, T in C, P in mW)
REFERENCE_CONDITION = ("p_sweep", "4154", "130", "225")


def _rabi_225mw_mhz() -> float:
    from .hyperpolarizability import two_photon_rabi_hz
    from .lineshape import aperture_onaxis_factor_actual
    return two_photon_rabi_hz(0.225, C.W0_CENTRAL_M, K.RHO_RETRO) * aperture_onaxis_factor_actual(C.W0_CENTRAL_M) / 1e6


def reference_point(results_dir: Optional[str] = None) -> Dict[str, float]:
    """The archive's line at its reference condition, in MHz FWHM on the transition axis.

    Returns `gamma_coll`, `sigma_laser` (the committed fit of `REFERENCE_CONDITION`), `transit_fwhm`
    (`constants.transit_fwhm_from_w0(config.W0_CENTRAL_M, 130 C)`), `s0_225mW` (the predicted shift at the
    reference power, `stark.kappa_pred_per_watt` at the waist the record carries, the bench's actual focus),
    `rabi_225mW` (the two-photon Rabi frequency there in MHz, with the SAME actual-focus factor, since both go
    as the on-axis intensity), plus `T_C`. Raises when the committed
    table has no row for the condition, rather than falling back to a number: a missing row is a record
    that moved, and a fallback is how the typed copies this module replaces were born.
    """
    from pathlib import Path
    path = Path(results_dir) / "linefit_conditions.csv" if results_dir else C.RESULTS_DIR / "linefit_conditions.csv"
    role, peak, T, P = REFERENCE_CONDITION
    with open(path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if (r["role"], r["peak"], r["T"], r["P"]) == (role, peak, T, P):
                from .stark import kappa_pred_per_watt
                return {"gamma_coll": float(r["gamma_coll"]), "sigma_laser": float(r["sigma_laser"]),
                        "transit_fwhm": float(K.transit_fwhm_from_w0(C.W0_CENTRAL_M, float(T))),
                        "s0_225mW": float(kappa_pred_per_watt(C.W0_CENTRAL_M, K.RHO_RETRO) * 0.225),
                        "rabi_225mW": float(_rabi_225mw_mhz()),
                        "T_C": float(T)}
    raise KeyError(f"{path} has no row for the archive condition {REFERENCE_CONDITION}; the archive point is "
                   f"read from the committed fit and has no typed fallback (F313)")
