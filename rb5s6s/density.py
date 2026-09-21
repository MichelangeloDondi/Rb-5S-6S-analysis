"""
Rb vapor number density vs temperature (module M4, support)
==========================================================

Number density N(T) of Rb vapor in a cell, from the saturated vapor pressure.
All our cell temperatures (70-130 C) are ABOVE the Rb melting point
(39.30 C = 312.45 K), so the LIQUID-phase correlation applies throughout.

Vapor pressure: THREE published laws, one central (owner ruling O42, 2026-09-21;
finding F259). The central law is Alcock, Itkin and Horrigan 1984 as the held
Steck (Rubidium D Line Data, revision 2.3.4, 8 August 2025) adopts it, liquid
phase, T in kelvin, P in torr, graded there "better than +-5% from 298-550 K":

    log10(P/torr) = 2.881 + 4.312 - 4040/T

(2.881 is log10 760: Alcock's own form is in atmospheres). Two model-form arms
are carried beside it and never averaged into it:

    nesmeyanov   log10(P/torr) = 15.88253 - 4529.635/T + 0.00058663*T - 2.99138*log10(T)
                 (Nesmeyanov 1963; Steck calls it older and probably less accurate;
                 the central law of this record until 2026-09-21)
    stull_sinke  log10(P/Pa) = 9.545 - 4132/T
                 (the CRC's second form; Killian 1926's curve as the spin-exchange
                 optical-pumping field prints it, 10.55 - 4132/T in dyn cm^-2, is the
                 same 4132 K law 1.2 per cent higher)

Across the record's 70 to 130 C, Nesmeyanov sits 24 to 17 per cent BELOW Alcock
and Stull-Sinke 9 per cent to 0.3 per cent below (`law_ratio` reproduces them;
`scripts/run_density_laws.py` writes them as rows).

Number density from the ideal gas law: N = P / (k_B T).

CAVEATS carried downstream (M4 error budget) -- PROPAGATED, not just named:
  * the density SCALE is uncertain by the spread between published laws, and
    that spread is now MEASURED, not guessed: N_SCALE_FRAC_SYST below is the
    largest |N_arm / N_central - 1| over the arms at the record's four cell
    temperatures (the Nesmeyanov arm at 70 C), replacing a typed 0.20 that
    sized the gap without naming its cause. Anything that scales as 1/N
    (beta_self and its bounds) inherits it: beta_true = beta_fit x
    N_assumed/N_true. ALCOCK_STATED_FRAC is the central law's own grade.
  * a hot vapor cell's density is set by the COLDEST spot on the glass, not
    the nominal set temperature. The archive gives a FIRST HANDLE on the
    offset (results report addendum 15): the line area scales as N, so
    dln(area)/dlnN(T_read) would be 1 for perfect readings; measured it is
    1.14 +/- 0.07 (sem over 4 peaks), consistent with 1 at ~2 sigma and
    preferring dT ~ 20 K at face value. That test cannot separate a cold spot
    from radiation trapping of the detected 795 nm fluorescence or from
    block-to-block amplitude wander, so 0-30 K stands. Its SIGN is known: a cold spot means N_true < N_assumed, i.e. the
    fitted beta UNDERSTATES the true beta -- the dangerous direction for an
    upper bound, and exactly why the (1 + f) inflation above is applied to
    the + side. Scale: dlnN/dT is ~7.6%/K at 70 C falling to ~5.5%/K at
    130 C on the central law (dlnN_dT_per_K below), so each kelvin of cold
    spot is ~5.5-7.6% of N. Because dlnN/dT itself varies across the sweep, a
    constant cold-spot offset also TILTS the N(T) lever arm by ~2.3%/K of
    offset -- a slope (not just scale) bias, second-order relative to the
    scale term and recorded here rather than propagated.
  * the beta_self fit leans on the SHAPE of N(T) (its ~48x rise across
    70->130 C on Alcock, ~52x on Nesmeyanov), which is robust to a pure scale
    error; the terms above bite the ABSOLUTE calibration of beta, not the
    existence of the bound.
"""

from __future__ import annotations

import numpy as np

# Physical constants (SI). ESTABLISHED; one home, constants.py (2026-09-12).
from .constants import K_B_J_PER_K
from .constants import TORR_PA as TORR_TO_PA   # one home: constants.py, 101325/760 exactly

RB_MELT_C = 39.30  # C; below this the SOLID correlation would be needed

# THE LAWS, liquid phase. ESTABLISHED, each read from its source as named in the docstring.
_ALCOCK = (2.881 + 4.312, 4040.0)                            # log10(P/torr) = a - b/T
_NESMEYANOV = (15.88253, 4529.635, 0.00058663, 2.99138)      # a - b/T + c*T - d*log10(T), torr
_STULL_SINKE = (9.545, 4132.0)                              # log10(P/Pa) = a - b/T

LAWS = ("alcock", "nesmeyanov", "stull_sinke")
DENSITY_LAW = "alcock"          # the central law (O42); the other two are model-form arms
ALCOCK_STATED_FRAC = 0.05       # Steck's grade of the central law over 298-550 K. ESTABLISHED
RECORD_CELL_TEMPS_C = (70.0, 90.0, 110.0, 130.0)   # the temperature arm of the design (the L)


def _law(law):
    law = DENSITY_LAW if law is None else str(law).lower()
    if law not in LAWS:
        raise ValueError(f"density law {law!r} is not one of {LAWS}")
    return law


def vapor_pressure_torr(T_C: np.ndarray, law: str | None = None) -> np.ndarray:
    """Saturated Rb vapor pressure (torr) vs temperature (deg C), liquid phase, on `law`
    (default the central law, DENSITY_LAW)."""
    T = np.asarray(T_C, float) + 273.15
    law = _law(law)
    if law == "alcock":
        a, b = _ALCOCK
        return 10.0 ** (a - b / T)
    if law == "nesmeyanov":
        a, b, c, d = _NESMEYANOV
        return 10.0 ** (a - b / T + c * T - d * np.log10(T))
    a, b = _STULL_SINKE
    return 10.0 ** (a - b / T) / TORR_TO_PA


def number_density_cm3(T_C: np.ndarray, law: str | None = None) -> np.ndarray:
    """Rb vapor number density (cm^-3) vs temperature (deg C), on `law`.

    Raises if any temperature is below the melting point (the liquid
    correlation would be extrapolated into the solid regime)."""
    T_C = np.asarray(T_C, float)
    if np.any(T_C < RB_MELT_C):
        raise ValueError(f"T below Rb melting point ({RB_MELT_C} C); "
                         "liquid vapor-pressure correlation invalid")
    T_K = T_C + 273.15
    P_pa = vapor_pressure_torr(T_C, law) * TORR_TO_PA
    N_m3 = P_pa / (K_B_J_PER_K * T_K)
    return N_m3 * 1e-6  # m^-3 -> cm^-3


def law_ratio(T_C, arm: str, central: str | None = None):
    """N_arm / N_central at T_C: the model-form displacement of the density scale."""
    return number_density_cm3(T_C, arm) / number_density_cm3(T_C, central)


def _arm_spread() -> float:
    """The largest |N_arm / N_central - 1| over the arms at the record's cell temperatures. CALCULATED."""
    arms = [a for a in LAWS if a != DENSITY_LAW]
    return float(max(abs(float(law_ratio(t, a)) - 1.0) for a in arms for t in RECORD_CELL_TEMPS_C))


# Density-SCALE fractional systematic, DERIVED from the laws (F259): the largest displacement an arm
# makes at the record's own temperatures. Consumers with a 1/N dependence (beta_self bounds) multiply
# their upper bounds by (1 + this). It replaced a typed 0.20 on 2026-09-21.
N_SCALE_FRAC_SYST = _arm_spread()


def dlnN_dT_per_K(T_C, law: str | None = None):
    """d ln N / dT (per kelvin) on `law`, analytic.

    ln N = ln P - ln(kB T) + const, so d lnN/dT = d lnP/dT - 1/T with
    d lnP/dT = ln10 * b/T^2 (Alcock, Stull-Sinke) or ln10 * (b/T^2 + c) - d/T
    (Nesmeyanov). Used to size the cold-spot systematic (~5.5-7.6%/K over
    70-130 C on the central law); see the module docstring."""
    T = np.asarray(T_C, float) + 273.15
    law = _law(law)
    if law == "nesmeyanov":
        _a, b, c, d = _NESMEYANOV
        return np.log(10.0) * (b / T ** 2 + c) - d / T - 1.0 / T
    b = _ALCOCK[1] if law == "alcock" else _STULL_SINKE[1]
    return np.log(10.0) * b / T ** 2 - 1.0 / T


# Convenience scale for beta_self fits: density in units of 1e12 cm^-3, so
# beta_self comes out as MHz per 1e12 cm^-3 (a human-sized number).
N_UNIT_CM3 = 1e12


def density_units(T_C, law: str | None = None):
    """N(T) in units of 1e12 cm^-3 (the fit's density variable), on `law`."""
    return number_density_cm3(T_C, law) / N_UNIT_CM3


def d1_optical_depth_per_cm(T_C, isotope, f_hf=0.5):
    """D1 (795 nm) resonant optical depth PER cm for the DETECTED cascade
    photon: tau/L = f_hf * abundance(isotope) * N(T) * sigma_D1. The emitted
    795 photon sits on the D1 line and is reabsorbed by ground-state atoms in
    the connected hyperfine level (fraction f_hf). Multiply by the cell path
    (few cm) for the full tau. ENVELOPE (sigma_D1 is an order-of-magnitude
    value); its ISOTOPE RATIO (85/87 = abundance ratio ~2.6) is robust and is
    what drives differential trapping between the peaks."""
    from .constants import SIGMA_D1_CM2, ABUNDANCE_RB85, ABUNDANCE_RB87
    if isotope not in (85, 87):
        raise ValueError(
            f"isotope={isotope} is neither 85 nor 87, and the natural "
            f"abundances this function carries are rubidium's. It used "
            f"to return the Rb-87 abundance for anything else, which is "
            f"a wrong number rather than a refusal.")
    ab = ABUNDANCE_RB85 if isotope == 85 else ABUNDANCE_RB87
    return f_hf * ab * number_density_cm3(T_C) * SIGMA_D1_CM2
