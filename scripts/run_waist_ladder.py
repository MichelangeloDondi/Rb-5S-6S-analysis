#!/usr/bin/env python3
"""The waist ladder: every term's dependence on a known magnification.

WHY THIS PRODUCER EXISTS. The campaign's second lever is an adjustable
beam expander that scales the waist at fixed
power and fixed retro ratio. Its whole value is that the terms of the forward
model carry DIFFERENT powers of the knob, so a fit across settings measures the
reference waist rather than assuming it. Those powers are quoted in
`docs/methods/03_the_ac_stark_ramp.md`, and a quoted exponent with no producer
is exactly what this record calls an asserted number. This file computes each
term from the package function that owns it and fits the exponent back, so the
table is re-derivable and a drift in any of those functions fails the guard.

WHAT IT IS NOT. It is not a forecast: no noise, no traces, no estimator. It is
the analytic ladder, the second rung of the record's own order, and what a
measurement of it costs is measured elsewhere.

Columns per rung: the magnification, the waist, the transit FWHM, the peak
light shift, the two-photon Rabi frequency, the axial collection ratio, the
ramp's own second and third cumulant against the pure ramp at that ratio, the
relative excitation cycles of one crossing, the relative rate per atom, the
relative collected signal and the relative peak height. Then one row per term
carrying the fitted exponent across the ladder and the exponent the derivation
predicts, which is what a reader checks.

THE COLLECTED SIGNAL IS A CLOSED FORM and it is the row that surprised the
record: with the transverse integral of I^2 equal to P^2/(pi w(z)^2) and the
axial half-window L fixed by the detector,

    S(w0) = (2 P^2 / lambda) * arctan(L / zR),   zR = pi w0^2 / lambda,

so tightening the beam buys far less than 1/w0^2, and the peak height, the
line having broadened as 1/w0, still less.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from rb5s6s import config as C_cfg
from rb5s6s import constants as C
from rb5s6s.hyperpolarizability import two_photon_rabi_hz
from rb5s6s.lineshape import ramp_moment_contributions
from rb5s6s.stark import stark_shift_S0_mhz

W0_REF_M = C.W0_MEASURED_M          # the record's prior waist, the ladder's anchor
POWER_W = 0.225                     # the campaign's top rung
T_C = 130.0
RHO = 0.94
MAGNIFICATIONS = (1.0, 0.625, 0.390625, 0.25)   # 64, 40, 25, 16 um at the anchor
GAMMA_COLL = 0.55        # the producers' own 130 C collisional width, MHz
SIGMA_LASER = 2.07       # the session range's upper end, MHz FWHM

# The anchors the relative columns are normalised against, from the same
# package functions that make the columns, so the ladder carries no power
# of the magnification typed by hand.
RABI_ANCHOR_HZ = two_photon_rabi_hz(POWER_W, W0_REF_M, RHO)
TRANSIT_ANCHOR_MHZ = C.transit_fwhm_from_w0(W0_REF_M, T_C)

PREDICTED = {"transit_fwhm_mhz": -1.0, "s0_mhz": -2.0, "rabi_hz": -2.0,
             "z_ratio": -2.0, "cycles_rel": -3.0, "rate_rel": -4.0}



def _k3_axial(z_ratio: float, n_photon: int, n_grid: int = 600_001) -> float:
    """Third cumulant of the axially windowed ramp at photon order n, in units
    of the on-axis shift cubed.

    Emitted so the one-photon comparison below is a computed cell and not a
    remembered fact. At `z_ratio` zero it returns 0 for n = 1 and +1/135 for
    n = 2, which are the closed forms `docs/methods/03` derives."""
    import numpy as np
    from rb5s6s._compat import trapezoid
    from rb5s6s.lineshape import stark_ramp_axial
    nu = np.linspace(-1.0000001, 0.0, n_grid)
    f = stark_ramp_axial(nu, 1.0, z_ratio, n_photon=n_photon)
    a = trapezoid(f, nu)
    if not a:
        return float("nan")
    f = f / a
    m = trapezoid(nu * f, nu)
    return float(trapezoid((nu - m) ** 3 * f, nu))


def _one_over_two(z_ratio: float) -> float:
    """|kappa3| of a one-photon ramp over a two-photon one at the same window."""
    a, b = abs(_k3_axial(z_ratio, 1)), abs(_k3_axial(z_ratio, 2))
    return a / b if b else float("nan")


def _line_fwhm(w0_m: float) -> float:
    """The COMPOSITE line's full width at this waist, in MHz.

    Not the transit. The transit is about a fifth of the line at the record's
    own conditions, and at tight waists the light shift's own ramp is the
    largest contributor, so dividing the collected signal by the transit
    overstates how fast the line spreads and inverts the peak-height reading.
    A first draft of this producer did exactly that, and the reading was
    refuted at the artefact.
    """
    from rb5s6s.lineshape import model_profile
    nu = np.linspace(-80.0, 80.0, 80001)
    y = model_profile(nu, gamma_coll=GAMMA_COLL, sigma_laser_fwhm=SIGMA_LASER,
                      transit_fwhm=C.transit_fwhm_from_w0(w0_m, T_C),
                      s0=stark_shift_S0_mhz(POWER_W, w0_m, RHO), resolve_shift=True)
    half = y.max() / 2.0
    i = np.where(y >= half)[0]
    return float(nu[i[-1]] - nu[i[0]])


def _rows() -> list[dict]:
    out = []
    for m in MAGNIFICATIONS:
        w0 = W0_REF_M * m
        z_ratio = C.collection_z_ratio(w0_m=w0)
        ramp = ramp_moment_contributions(stark_shift_S0_mhz(POWER_W, w0, RHO), z_ratio=z_ratio)
        pure = ramp_moment_contributions(stark_shift_S0_mhz(POWER_W, w0, RHO), z_ratio=0.0)
        out.append(dict(
            magnification=m,
            w0_um=w0 * 1e6,
            transit_fwhm_mhz=C.transit_fwhm_from_w0(w0, T_C),
            s0_mhz=stark_shift_S0_mhz(POWER_W, w0, RHO),
            rabi_hz=two_photon_rabi_hz(POWER_W, w0, RHO),
            z_ratio=z_ratio,
            k2_over_pure=(ramp["excess_var"] / pure["excess_var"]) if pure["excess_var"] else float("nan"),
            k3_over_pure=(ramp.get("kappa3", float("nan")) / pure["kappa3"]) if pure.get("kappa3") else float("nan"),
            # THE ONE-PHOTON NULL IS A THIN-WINDOW STATEMENT (owner, 2026-09-09).
            # The transverse law is uniform at n = 1 and a uniform density is
            # symmetric about its own mean, so its third cumulant vanishes. The
            # OBSERVED density is the axial mixture of uniforms with different
            # upper limits, which is not uniform and not symmetric. It is
            # recovered only as z_ratio goes to zero, which is a wide waist and
            # a large collection magnification.
            k3_one_photon_over_two=_one_over_two(z_ratio),
            rate_rel=(two_photon_rabi_hz(POWER_W, w0, RHO) / RABI_ANCHOR_HZ) ** 2,
            cycles_rel=((two_photon_rabi_hz(POWER_W, w0, RHO) / RABI_ANCHOR_HZ) ** 2
                        * TRANSIT_ANCHOR_MHZ / C.transit_fwhm_from_w0(w0, T_C)),
            signal_rel=math.atan(z_ratio),
            line_fwhm_mhz=_line_fwhm(w0),
            peak_rel=math.atan(z_ratio) / _line_fwhm(w0),
        ))
    # THE REFERENCE IS CAPTURED BEFORE THE LOOP. Taking it as out[0] and
    # dividing in place made the first row its own divisor, so every later row
    # was divided by one and the column read as the bare arctangent. Caught on
    # the dry run because the signal came back non-monotone in a way the
    # closed form forbids.
    s_ref, p_ref = out[0]["signal_rel"], out[0]["peak_rel"]
    for r in out:
        r["signal_rel"] /= s_ref
        r["peak_rel"] /= p_ref
    return out


def _exponents(rows: list[dict]) -> list[dict]:
    lm = np.log(np.array([r["magnification"] for r in rows]))
    out = []
    for term, want in PREDICTED.items():
        y = np.log(np.array([abs(r[term]) for r in rows]))
        slope = float(np.polyfit(lm, y, 1)[0])
        out.append(dict(term=term, fitted_exponent=slope, predicted_exponent=want,
                        agrees=abs(slope - want) < 1e-6))
    return out


def peak_height_optimum() -> tuple[float, float, float]:
    """The magnification that maximises the peak height, and its waist.

    The collected signal goes as arctan(L/zR) and the peak height is that over
    the COMPOSITE line width, which is not the transit: at tight waists the
    light shift's own ramp dominates the width and is what turns the peak
    height over. Scanned rather than solved, because the answer is the
    parameter (the record's own rule).
    """
    grid = np.linspace(0.10, 1.5, 141)
    val = np.array([math.atan(C.collection_z_ratio(w0_m=W0_REF_M * m))
                    / _line_fwhm(W0_REF_M * m) for m in grid])
    i = int(np.argmax(val))
    return (float(grid[i]), float(W0_REF_M * grid[i] * 1e6),
            float(C.collection_z_ratio(w0_m=W0_REF_M * grid[i])))


def main(out_path: Path | None = None) -> Path:
    rows = _rows()
    exps = _exponents(rows)
    m_opt, w_opt, z_opt = peak_height_optimum()
    dest = out_path or (Path(C_cfg.RESULTS_DIR) / "waist_ladder.csv")
    note = ("the analytic waist ladder at fixed power and retro ratio, each term from the package function "
            "that owns it. signal_rel is the closed form (2 P^2 / lambda) arctan(L / zR) normalised to the "
            "anchor, and peak_rel divides it by the COMPOSITE line width, which is what a peak height "
            "is measured against and is not the transit alone. "
            "k2_over_pure and k3_over_pure are the ramp's cumulants through the axial collection window "
            "against the pure ramp, and the third reverses sign where the window passes about one Rayleigh "
            "range. The exponent rows fit d ln term / d ln magnification across the ladder and compare it "
            "against the derivation of docs/methods/03. k3_one_photon_over_two is the same "
            "window applied to a one-photon ramp against the two-photon one: the one-photon "
            "null holds only as the window shrinks, since the transverse law is uniform at "
            "each slice and the axial mixture of uniforms with different upper limits is not.")
    with dest.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["row_kind", "magnification", "w0_um", "transit_fwhm_mhz", "s0_mhz", "rabi_hz",
                    "z_ratio", "k2_over_pure", "k3_over_pure", "k3_one_photon_over_two",
                    "cycles_rel", "rate_rel",
                    "signal_rel", "line_fwhm_mhz", "peak_rel", "term", "fitted_exponent",
                    "predicted_exponent", "status", "note"])
        for r in rows:
            w.writerow(["rung", f"{r['magnification']:.6f}", f"{r['w0_um']:.3f}",
                        f"{r['transit_fwhm_mhz']:.6f}", f"{r['s0_mhz']:.6f}", f"{r['rabi_hz']:.3f}",
                        f"{r['z_ratio']:.6f}", f"{r['k2_over_pure']:.6f}", f"{r['k3_over_pure']:.6f}",
                        f"{r['k3_one_photon_over_two']:.6f}",
                        f"{r['cycles_rel']:.6f}", f"{r['rate_rel']:.6f}", f"{r['signal_rel']:.6f}",
                        f"{r['line_fwhm_mhz']:.4f}", f"{r['peak_rel']:.6f}", "", "", "", "DIAGNOSTIC", note])
        for e in exps:
            w.writerow(["exponent", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                        e["term"], f"{e['fitted_exponent']:.6f}", f"{e['predicted_exponent']:.1f}", "DIAGNOSTIC", note])
        w.writerow(["peak_optimum", f"{m_opt:.6f}", f"{w_opt:.3f}", "", "", "",
                    f"{z_opt:.6f}", "", "", "", "", "", "", "", "",
                    "peak_height_max", "", "", "DIAGNOSTIC", note])
    return dest


if __name__ == "__main__":
    import sys
    p = main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(f"wrote {p}")
    for line in p.read_text().splitlines()[:2]:
        print("  " + line[:150])
