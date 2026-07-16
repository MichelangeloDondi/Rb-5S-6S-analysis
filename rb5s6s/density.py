"""
Rb vapor number density vs temperature (module M4, support)
==========================================================

Number density N(T) of Rb vapor in a cell, from the saturated vapor pressure.
All our cell temperatures (70-130 C) are ABOVE the Rb melting point
(39.30 C = 312.45 K), so the LIQUID-phase correlation applies throughout.

Vapor pressure: Nesmeyanov's liquid-Rb correlation as tabulated by Steck
(Rubidium D Line Data), T in kelvin, P in torr:

    log10(P/torr) = 15.88253 - 4529.635/T + 0.00058663*T - 2.99138*log10(T)

Number density from the ideal gas law: N = P / (k_B T).

CAVEATS carried downstream (M4 error budget) — now PROPAGATED, not just named:
  * different vapor-pressure correlations disagree at the ~10-30% level; we
    quote the Steck/Nesmeyanov choice explicitly and adopt the midpoint of
    that spread, N_SCALE_FRAC_SYST = 0.20, as the density-SCALE systematic.
    Anything that scales as 1/N (beta_self and its bounds) inherits the same
    fractional error: beta_true = beta_fit x N_assumed/N_true, so a 20% N
    error moves every beta number 20%. Downstream consumers multiply their
    quoted upper bounds by (1 + N_SCALE_FRAC_SYST).
  * a hot vapor cell's density is set by the COLDEST spot on the glass, not
    the nominal set temperature. The offset dT is unpinned by the archive,
    but its SIGN is known: a cold spot means N_true < N_assumed, i.e. the
    fitted beta UNDERSTATES the true beta — the dangerous direction for an
    upper bound, and exactly why the (1 + f) inflation above is applied to
    the + side. Scale: dlnN/dT is ~7.8%/K at 70 C falling to ~5.6%/K at
    130 C (dlnN_dT_per_K below), so each kelvin of cold spot is ~6-8% of N.
    Because dlnN/dT itself varies across the sweep, a constant cold-spot
    offset also TILTS the N(T) lever arm by ~2.3%/K of offset — a slope
    (not just scale) bias, second-order relative to the 20% scale term and
    recorded here rather than propagated.
  * the beta_self fit leans on the SHAPE of N(T) (its ~50x rise across
    70->130 C), which is robust to a pure scale error; the terms above bite
    the ABSOLUTE calibration of beta, not the existence of the bound.
"""

from __future__ import annotations

import numpy as np

# Physical constants (SI). ESTABLISHED.
K_B_J_PER_K = 1.380649e-23
TORR_TO_PA = 133.322368

# Nesmeyanov liquid-Rb coefficients (Steck). ESTABLISHED.
_A, _B, _C, _D = 15.88253, 4529.635, 0.00058663, 2.99138
RB_MELT_C = 39.30  # C; below this the SOLID correlation would be needed


def vapor_pressure_torr(T_C: np.ndarray) -> np.ndarray:
    """Saturated Rb vapor pressure (torr) vs temperature (deg C), liquid phase."""
    T = np.asarray(T_C, float) + 273.15
    return 10.0 ** (_A - _B / T + _C * T - _D * np.log10(T))


def number_density_cm3(T_C: np.ndarray) -> np.ndarray:
    """Rb vapor number density (cm^-3) vs temperature (deg C).

    Raises if any temperature is below the melting point (the liquid
    correlation would be extrapolated into the solid regime)."""
    T_C = np.asarray(T_C, float)
    if np.any(T_C < RB_MELT_C):
        raise ValueError(f"T below Rb melting point ({RB_MELT_C} C); "
                         "liquid vapor-pressure correlation invalid")
    T_K = T_C + 273.15
    P_pa = vapor_pressure_torr(T_C) * TORR_TO_PA
    N_m3 = P_pa / (K_B_J_PER_K * T_K)
    return N_m3 * 1e-6  # m^-3 -> cm^-3


# Density-SCALE fractional systematic: midpoint of the ~10-30% spread between
# published vapor-pressure correlations (see module docstring). Consumers with
# a 1/N dependence (beta_self bounds) multiply their upper bounds by (1 + this).
N_SCALE_FRAC_SYST = 0.20


def dlnN_dT_per_K(T_C):
    """d ln N / dT (per kelvin) of the Nesmeyanov/Steck liquid correlation.

    Analytic: ln N = ln10 * (A - B/T + C*T - D*log10 T) - ln(kB T) + const, so
    d lnN/dT = ln10 * (B/T^2 + C) - D/T - 1/T. Used to size the cold-spot
    systematic (~6-8%/K over 70-130 C); see the module docstring."""
    T = np.asarray(T_C, float) + 273.15
    return np.log(10.0) * (_B / T ** 2 + _C) - _D / T - 1.0 / T


# Convenience scale for beta_self fits: density in units of 1e12 cm^-3, so
# beta_self comes out as MHz per 1e12 cm^-3 (a human-sized number).
N_UNIT_CM3 = 1e12


def density_units(T_C):
    """N(T) in units of 1e12 cm^-3 (the fit's density variable)."""
    return number_density_cm3(T_C) / N_UNIT_CM3


def d1_optical_depth_per_cm(T_C, isotope, f_hf=0.5):
    """D1 (795 nm) resonant optical depth PER cm for the DETECTED cascade
    photon: tau/L = f_hf * abundance(isotope) * N(T) * sigma_D1. The emitted
    795 photon sits on the D1 line and is reabsorbed by ground-state atoms in
    the connected hyperfine level (fraction f_hf). Multiply by the cell path
    (few cm) for the full tau. ENVELOPE (sigma_D1 is an order-of-magnitude
    value); its ISOTOPE RATIO (85/87 = abundance ratio ~2.6) is robust and is
    what drives differential trapping between the peaks."""
    from .constants import SIGMA_D1_CM2, ABUNDANCE_RB85, ABUNDANCE_RB87
    ab = ABUNDANCE_RB85 if isotope == 85 else ABUNDANCE_RB87
    return f_hf * ab * number_density_cm3(T_C) * SIGMA_D1_CM2
