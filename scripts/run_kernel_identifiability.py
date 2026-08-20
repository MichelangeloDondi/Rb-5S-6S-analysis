#!/usr/bin/env python3
"""K0: WHAT THE ARCHIVE CAN AND CANNOT IDENTIFY ABOUT THE LASER KERNEL.

THE OBJECT. M38 measured what the `laser_kind` assumption COSTS: thrown from
Gaussian to Lorentzian it moves gamma_coll by a median 45 per cent. This
producer asks the prior question, which M38 did not: CAN the archive identify
the laser's contribution at all, or was the two-corner comparison reading a
degeneracy?

THE ANALYTIC ANSWER, FIRST, BECAUSE IT IS PROVABLE BY INSPECTION. All three
assembly sites (lineshape.py:184, lineshape.py:396, linefit.py:104) build

    homog = gamma_nat + gamma_coll          # a Lorentzian
    prof  = lorentzian(g, homog) (*) lk     # lk = the laser kernel

and the convolution of two Lorentzians of FWHM a and b is a Lorentzian of
FWHM a+b. So under laser_kind="lorentzian" THE PROFILE AT FIXED CONDITION
DEPENDS ON gamma_coll AND sigma_laser ONLY THROUGH THEIR SUM. That is an
exact null direction (1, -1)/sqrt(2) in the shared block, not an approximate
one, and it holds for every trace, every temperature and every power.

WHY THIS MATTERS FOR THE 32-OF-32 RESULT. The Lorentzian arm has one shape
parameter where the Gaussian arm has two. A comparison of a two-parameter fit
against a one-parameter fit that reports the two-parameter fit winning at
32 of 32 conditions is close to determined before any data is taken. The
32-of-32 is evidence about PARAMETER COUNT and is not evidence that the data
prefer a Gaussian laser.

WHAT IS MEASURED HERE, as corroboration of the analytic statement and as the
part that is NOT provable by inspection:

  1. FIXED-CONDITION JACOBIAN. Numerical columns d(profile)/d(gamma_coll) and
     d(profile)/d(sigma_laser) under each kernel. Their correlation and the
     singular values of the 2-column Jacobian. Under "lorentzian" the second
     singular value must be at machine-noise level; under "gaussian" it must
     not be. This is the SHOULD-FAIL CONTROL (rule 19.53): an instrument that
     reports degeneracy under both kernels would be measuring its own
     round-off, not the model.

  2. THE HIERARCHICAL FISHER MATRIX WITH THE INTERCEPT SLOTS FREE. The
     density ladder separates the collisional SLOPE from a density-independent
     INTERCEPT, and nothing more. The intercept is

         Gamma_intercept = Gamma_laser,L + Gamma_transit + Gamma_residual

     A Fisher matrix computed with Gamma_transit frozen reports health for a
     fit that is degenerate once it is freed, so this computes it with the
     intercept slots FREE and reports the smallest singular value AND ITS
     DIRECTION. The decision rule preregistered here: the real-data fit runs
     as a MEASUREMENT of the laser contribution only if that direction is not
     essentially parallel to the laser slot; otherwise it runs as a BOUND.

WHAT THIS PRODUCER DOES NOT DO. It does not fit real data and it does not
choose a kernel. It is the contract the K2 synthetics and the K3 inference are
checked against, and it is deliberately runnable in seconds so that the
contract exists before anything is fitted.

    python scripts/run_identifiability.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                       # noqa: E402
from rb5s6s._compat import trapezoid                 # noqa: E402
from rb5s6s.lineshape import (composite_profile, lorentzian,   # noqa: E402
                              gaussian, two_sided_exponential,
                              GAMMA_NAT_HZ)

OUT = C.RESULTS_DIR / "kernel_identifiability.csv"

# A representative canonical condition: the 4121 peak, 130 C, 225 mW row of
# results/laser_kernel.csv, whose fitted values are used as the expansion
# point so the Jacobian is evaluated where the fit actually lands.
NU = np.linspace(-8.0, 8.0, 801)          # MHz about line centre
GAMMA_COLL = 0.5848                        # MHz, gaussian arm, 4121/130/225
SIGMA_LASER = 1.5334                       # MHz FWHM, same row
TRANSIT = 0.35                             # MHz, transit_fwhm_at_T(130)
REL_STEP = 1e-4


def _profile(gamma_coll, sigma_laser, transit_fwhm, kind):
    """The SHIPPED composite, resampled onto the common grid NU.

    `composite_profile` returns its own self-sized grid, whose step is set by
    the narrowest kernel, so perturbing a width can move the grid as well as
    the profile. Interpolating onto one fixed grid removes that from the
    finite difference. What it cannot remove is the round-off the resampling
    itself adds, which is why the gaussian arm is carried as a should-fail
    control: if the instrument reported degeneracy under BOTH kernels it
    would be measuring its own noise floor rather than the model.
    """
    g, prof = composite_profile(gamma_coll, sigma_laser, transit_fwhm, kind)
    return np.interp(NU, g, prof)


def _column(kind, which, gc, sl, tr):
    """Central-difference derivative of the profile wrt one parameter."""
    base = {"gamma_coll": gc, "sigma_laser": sl, "transit_fwhm": tr}
    h = REL_STEP * max(base[which], 1e-3)
    up, dn = dict(base), dict(base)
    up[which] += h
    dn[which] -= h
    return (_profile(up["gamma_coll"], up["sigma_laser"], up["transit_fwhm"], kind)
            - _profile(dn["gamma_coll"], dn["sigma_laser"], dn["transit_fwhm"], kind)) / (2 * h)


def main() -> int:
    rows = []

    # --- 1. the fixed-condition two-parameter Jacobian, under both kernels ---
    for kind in ("gaussian", "lorentzian"):
        jg = _column(kind, "gamma_coll", GAMMA_COLL, SIGMA_LASER, TRANSIT)
        jl = _column(kind, "sigma_laser", GAMMA_COLL, SIGMA_LASER, TRANSIT)
        J = np.column_stack([jg, jl])
        corr = float(np.corrcoef(jg, jl)[0, 1])
        sv = np.linalg.svd(J, compute_uv=False)
        ratio = float(sv[1] / sv[0])
        # the null direction, as the right singular vector of the smallest sv
        v = np.linalg.svd(J, full_matrices=False)[2][-1]
        rows.append(dict(
            block="fixed_condition_jacobian", kind=kind,
            corr_gamma_sigma=f"{corr:.10f}",
            sv_ratio=f"{ratio:.3e}",
            null_dir_gamma=f"{v[0]:+.6f}", null_dir_sigma=f"{v[1]:+.6f}",
            note=(f"null direction weight on (gamma,sigma); "
                  f"1/sqrt(2)={1/np.sqrt(2):.4f} is the SUM degeneracy"),
            status="DIAGNOSTIC"))

    # --- 1b. THE DIRECT TEST, which has no finite-difference noise ---------
    # The SVD above divides by a step, so its floor is set by the resampling.
    # This asks the analytic question outright: move gamma_coll and sigma_laser
    # in OPPOSITE directions by the same amount, holding their SUM fixed. If
    # the profile depends on the sum alone the line must not move at all.
    # The control is the SAME-SIGN move, which changes the sum and must move
    # the line under BOTH kernels; it sets the scale the null move is read
    # against, so a small null residual cannot be mistaken for a dead
    # instrument (rule 19.53).
    D = 0.05  # MHz, ~9 per cent of gamma_coll: a large move, not a nudge
    for kind in ("gaussian", "lorentzian"):
        base = _profile(GAMMA_COLL, SIGMA_LASER, TRANSIT, kind)
        scale = float(np.max(np.abs(base)))
        opp = _profile(GAMMA_COLL + D, SIGMA_LASER - D, TRANSIT, kind)
        same = _profile(GAMMA_COLL + D, SIGMA_LASER + D, TRANSIT, kind)
        r_opp = float(np.max(np.abs(opp - base)) / scale)
        r_same = float(np.max(np.abs(same - base)) / scale)
        rows.append(dict(
            block="sum_invariance", kind=kind,
            corr_gamma_sigma="",
            sv_ratio=f"{r_opp / r_same:.3e}",
            null_dir_gamma=f"{r_opp:.3e}", null_dir_sigma=f"{r_same:.3e}",
            note=(f"sum-preserving move changes the line by {r_opp:.2e} of peak, "
                  f"against {r_same:.2e} for the sum-changing control"),
            status="DIAGNOSTIC"))

    # --- 1c. THE MIXED MODEL K3 WILL ACTUALLY FIT --------------------------
    # The two blocks above test the two pure CORNERS. K3 does not fit a corner:
    # it fits G+L, a Gaussian laser width AND a free Lorentzian-equivalent
    # laser contribution Gamma_L,equiv together. Whether THAT parameter is
    # identifiable alongside gamma_coll is the question the whole window turns
    # on, and it must be answered before any fitting code is written.
    #
    # The mixed profile is not in the shipped module, so it is built here from
    # the shipped primitives. A reimplementation is only worth its output if it
    # is shown to agree with the code it stands in for, so it is FIRST checked
    # in both limits: Gamma_L,equiv -> 0 must reproduce the shipped gaussian
    # arm, and sigma_G -> 0 must reproduce the shipped lorentzian arm. Those
    # two checks are written to the CSV, not merely run, because a validation
    # nobody can see is a validation nobody can dispute.
    def _mixed(gamma_coll, sigma_g, gamma_l, transit_fwhm):
        homog = GAMMA_NAT_HZ / 1e6 + max(gamma_coll, 0.0) + max(gamma_l, 0.0)
        # The shipped sites floor an absent width at 1e-6 and then take the
        # MINIMUM of the list to set the step. That is harmless when every
        # kernel is present and wrong when one is switched off, because the
        # 1e-6 placeholder becomes the minimum and drives the step to its
        # floor. Only widths that are actually present set the step here, so
        # the two constructions are compared on comparable grids rather than
        # on an artefact of which kernel was disabled.
        widths = [w for w in (homog, sigma_g, transit_fwhm) if w > 1e-3]
        span = 6.0 * (sum(widths) + max(widths)) + 5.0
        dnu = max(min(widths) / 12.0, 1e-3)
        n = int(np.ceil(span / dnu))
        g = np.arange(-n, n + 1) * dnu
        prof = lorentzian(g, homog)
        if sigma_g > 0:
            prof = np.convolve(prof, gaussian(g, sigma_g), "same") * dnu
        prof = np.convolve(prof, two_sided_exponential(g, transit_fwhm), "same") * dnu
        area = trapezoid(prof, g)
        return np.interp(NU, g, prof / (area if area > 0 else 1.0))

    for limit, kind, args in (
            ("gamma_L->0", "gaussian", (GAMMA_COLL, SIGMA_LASER, 0.0, TRANSIT)),
            ("sigma_G->0", "lorentzian", (GAMMA_COLL, 0.0, SIGMA_LASER, TRANSIT))):
        mine = _mixed(*args)
        theirs = _profile(GAMMA_COLL, SIGMA_LASER, TRANSIT, kind)
        dev = float(np.max(np.abs(mine - theirs)) / np.max(np.abs(theirs)))
        rows.append(dict(
            block="mixed_model_validation", kind=limit,
            corr_gamma_sigma="", sv_ratio=f"{dev:.3e}",
            null_dir_gamma="", null_dir_sigma="",
            note=(f"reimplementation vs shipped composite_profile in this limit; "
                  f"{'AGREES' if dev < 1e-3 else 'DISAGREES, do not read the next block'}"),
            status="DIAGNOSTIC"))

    # The four-parameter Jacobian of the mixed model. gamma_coll and
    # Gamma_L,equiv enter the SAME Lorentzian sum, so their two columns are
    # identical by construction and the pair is degenerate at fixed condition
    # NO MATTER what the Gaussian width does. What breaks it, if anything, is
    # the DENSITY LADDER: gamma_coll scales with density and Gamma_L,equiv does
    # not. That is a statement about the hierarchy, not about one condition, so
    # a fixed-condition matrix CANNOT answer it and this block reports what it
    # can: the degeneracy at fixed condition, which is the thing K3 must break.
    P = ("gamma_coll", "sigma_g", "gamma_l", "transit")
    base_vals = dict(gamma_coll=GAMMA_COLL, sigma_g=SIGMA_LASER,
                     gamma_l=0.10, transit=TRANSIT)
    cols = []
    for name in P:
        h = REL_STEP * max(base_vals[name], 1e-3)
        up, dn = dict(base_vals), dict(base_vals)
        up[name] += h
        dn[name] -= h
        cols.append((_mixed(up["gamma_coll"], up["sigma_g"], up["gamma_l"], up["transit"])
                     - _mixed(dn["gamma_coll"], dn["sigma_g"], dn["gamma_l"], dn["transit"])) / (2 * h))
    J = np.column_stack(cols)
    sv = np.linalg.svd(J, compute_uv=False)
    Vt = np.linalg.svd(J, full_matrices=False)[2]
    v = Vt[-1]
    rows.append(dict(
        block="mixed_model_jacobian", kind="G+L",
        corr_gamma_sigma=f"{float(np.corrcoef(cols[0], cols[2])[0, 1]):.10f}",
        sv_ratio=f"{float(sv[-1] / sv[0]):.3e}",
        null_dir_gamma=f"{v[0]:+.6f}", null_dir_sigma=f"{v[2]:+.6f}",
        note=("4 params (gamma_coll, sigma_G, Gamma_L_equiv, transit) at ONE "
              "condition; corr column is gamma_coll vs Gamma_L_equiv"),
        status="DIAGNOSTIC"))

    # --- 2. the hierarchical Fisher matrix, intercept slots FREE ------------
    # Three parameters: gamma_coll (which carries the density slope), the laser
    # width, and the transit width. Frozen transit is the construction that
    # reports false health, so it is reported BESIDE the free one as the
    # should-fail control for THIS block.
    for kind in ("gaussian", "lorentzian"):
        cols = {p: _column(kind, p, GAMMA_COLL, SIGMA_LASER, TRANSIT)
                for p in ("gamma_coll", "sigma_laser", "transit_fwhm")}
        for label, params in (("transit_frozen", ("gamma_coll", "sigma_laser")),
                              ("transit_free", ("gamma_coll", "sigma_laser", "transit_fwhm"))):
            J = np.column_stack([cols[p] for p in params])
            U, sv, Vt = np.linalg.svd(J, full_matrices=False)
            ratio = float(sv[-1] / sv[0])
            v = Vt[-1]
            # how much of the worst-determined direction lies in the laser slot
            i_laser = params.index("sigma_laser")
            i_gamma = params.index("gamma_coll")
            rows.append(dict(
                block=f"fisher_{label}", kind=kind,
                corr_gamma_sigma="",
                sv_ratio=f"{ratio:.3e}",
                null_dir_gamma=f"{v[i_gamma]:+.6f}", null_dir_sigma=f"{v[i_laser]:+.6f}",
                note=(f"n_params={len(params)}; "
                      f"laser weight in worst direction {abs(v[i_laser]):.4f}"),
                status="DIAGNOSTIC"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    for r in rows:
        print(f"{r['block']:<26} {r['kind']:<11} sv_ratio={r['sv_ratio']}  {r['note']}")
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
