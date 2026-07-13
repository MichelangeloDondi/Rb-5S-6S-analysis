"""
Peak areas and the degeneracy law (module M10)
=============================================

PHYSICS. For two-photon S->S excitation with two IDENTICAL photons, the
effective two-photon operator contains only tensor ranks K=0 and K=2, and K=2
cannot connect J=1/2 to J=1/2 (triangle rule K <= J+J' = 1). The operator is
therefore PURELY SCALAR: Delta F=0, Delta mF=0, and -- crucially -- the same
per-atom rate for every F and every m_F. The relative line STRENGTH (area) is
then pure initial-state population,

    S(peak)  proportional to  abundance(iso) * (2F+1) / G_iso ,

with G_87 = 8 and G_85 = 12 ground sublevels. Everything else (two-photon
matrix element, 6S->5P_1/2 branching, 795 nm collection) is common to the four
peaks at the level of isotope shifts / hyperfine anisotropies, i.e. <<1%.
Predictions: 4207/4121 = 5/3, 4192/4154 = 7/5 (degeneracy only; abundance and
all detection factors cancel), 4192/4207 = 2.42 (tests abundance too).
Temperature dependence of the measured/predicted ratio is a DIFFERENTIAL
radiation-trapping / D1-reabsorption probe (the emitted 795 nm hyperfine lines
overlap the two isotopes' ground D1 absorption differently).

MEASUREMENT. The right amplitude observable is the AREA (integral) of the
line, not the peak height: height = area/width x shape factor, so it
confounds amplitude with the width, which varies across peaks/blocks (laser
drift). The area is width-independent. We integrate the baseline-subtracted
trace over the adaptive window (which also excludes the off-center-sweep
mirror), on the frequency axis, so the result is in V*MHz and directly
comparable across peaks fitted with different sweep rates.

CAVEAT. Cross-peak ratios inherit BETWEEN-BLOCK power/alignment drift (each
peak is its own block, hours apart) -- expect a few-% systematic on top of the
2-4% within-block gain scatter.
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np

from .constants import PEAKS, ABUNDANCE_RB85, ABUNDANCE_RB87
from .linefit import adaptive_halfwidth
from .qc import boxcar
from . import config as C


def predicted_shares() -> Dict[str, float]:
    """Predicted relative areas (normalized to sum 1) from the scalar-operator
    population law: abundance x (2F+1)/G_iso."""
    G = {87: 8.0, 85: 12.0}
    ab = {87: ABUNDANCE_RB87, 85: ABUNDANCE_RB85}
    raw = {}
    for label, info in PEAKS.items():
        iso, F = info["isotope"], info["F"]
        raw[label] = ab[iso] * (2 * F + 1) / G[iso]
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()}


def peak_area(freqs: np.ndarray, volts: np.ndarray) -> float:
    """Model-independent TRUNCATED line area (V*MHz): integrate the
    baseline-subtracted trace over the adaptive window around the peak. The
    linear baseline is estimated from the window's outer 15% edges.

    Truncation is deliberate and documented: ~9% of a Lorentzian-cored line
    lies outside +-3.5 FWHM (plus a little wing eaten by the edge baseline),
    so peak_area UNDERCOUNTS the total area by a stable 5-15%. That bias
    CANCELS in ratios of similar-width lines -- the intended use -- and is
    verified by the closure tests (same-area/different-width ratio stays ~1
    while heights differ by >30%)."""
    sm = boxcar(volts, C.QC_SMOOTH_W)
    c0 = float(freqs[int(np.argmax(sm))])
    hw = adaptive_halfwidth(freqs, volts)
    m = np.abs(freqs - c0) <= hw
    f, v = freqs[m], volts[m]
    edge = np.abs(f - c0) >= 0.85 * hw
    if edge.sum() >= 10:
        p = np.polyfit(f[edge], v[edge], 1)
        v = v - np.polyval(p, f)
    from ._compat import trapezoid
    return float(trapezoid(v, f))
