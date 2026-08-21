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
from rb5s6s.lineshape import (composite_profile)

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
    # THE MIXED PROFILE IS NOW SHIPPED (2026-08-21). This block used to carry a
    # local reimplementation, because composite_profile could not express a
    # Gaussian and a Lorentzian laser component at once. It can: `gamma_l` was
    # threaded through all six fit sites, and the shipped model was checked
    # against the reimplementation it replaces at both corners and three
    # interior points, agreeing to 0.000e+00 at every one. The local copy is
    # therefore deleted rather than kept in step, per the standing rule that a
    # second copy of an artefact outside the module's own tests is wrong in the
    # one way nothing catches. The two limit checks below still run and are
    # still written to the CSV: a validation nobody can see is a validation
    # nobody can dispute, and they now check the SHIPPED model.
    def _mixed(gamma_coll, sigma_g, gamma_l, transit_fwhm):
        """The SHIPPED mixed kernel, on this block's common axis."""
        g, prof = composite_profile(gamma_coll, sigma_g, transit_fwhm,
                                    "gaussian", gamma_l=gamma_l)
        return np.interp(NU, g, prof)

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

    # --- 3. THE JOINT CELL+ONF FISHER BLOCK (design forecast) --------------
    # What an independent laser-width measurement at the lab's nanofiber
    # would do to the beta_self inference, computed BEFORE any hardware moves.
    # The construction mirrors the record's own estimator: one peak, its four
    # temperatures, a shared Gaussian laser width sigma_G, the collisional
    # term beta*N(T) riding the density ladder, transit FIXED per condition as
    # fit_beta_self does, per-condition nuisances (amplitude, centre, two
    # baseline terms) PROJECTED OUT of the physics columns, and each
    # condition's block SCALED BY ITS SIGNAL AMPLITUDE, taken proportional to
    # N(T): the two-photon signal per atom is fixed at fixed power, so the
    # number of emitting atoms sets the scale and the information leans on
    # the hot bright conditions, as the real fit's signal scaling implies.
    # This neglects cascade-photon reabsorption at the hot end
    # (density.d1_optical_depth_per_cm), which would soften the hot weights;
    # the choice is validated only empirically, by the gate below.
    #
    # THE VALIDATION ROW COMES FIRST and it gates everything after it: the
    # forecast machinery is run in the record's own TWO-parameter form
    # (beta, sigma_G, the gaussian arm of kernel_headline.csv) and its
    # correlation must land near the committed -0.82 to -0.89. A first
    # version of this block failed its own gate at +0.06, for two reasons now
    # built in as requirements: the committed correlation belongs to the
    # 2-parameter model, not the 3-parameter one, and equal condition weights
    # misstate where the fit's information lives.
    #
    # THE ONF ENTERS AS A PRIOR on the laser parameters, because that is how
    # it would enter fit_beta_self. Prior widths are quoted RELATIVE to the
    # cell-alone uncertainty of the pinned parameter, so no absolute noise
    # scale is claimed. All rows are DERIVED EXPECTATIONS in the vocabulary
    # of results/onf_candidate.csv, and the laser-transfer validity condition
    # travels with them: the fiber path adds phase noise, so a fiber-side
    # laser width speaks for the cell only under the simultaneous
    # differential configuration described in the "shared-path condition"
    # section of docs/notes/onf_candidate.md, or under a measured bound on
    # fiber-added noise. Neither exists yet; both are named there as the
    # design requirement.
    from rb5s6s.density import density_units
    from rb5s6s.linefit import transit_fwhm_at_T

    BETA = 0.0156                 # MHz per 1e12 cm^-3, committed 4121 beta_self
    SIGMA_G = 1.88                # MHz FWHM, committed 4121 sigma_laser
    GAMMA_L0 = 0.10               # MHz, expansion point for the Lorentzian content
    TRANSIT_REF = 0.9334247073098216   # C.TRANSIT_FWHM_PLACEHOLDER_MHZ
    TEMPS_C = (70.0, 90.0, 110.0, 130.0)

    def _mixed_cond(beta, sigma_g, gamma_l, T_C, nu):
        gc = beta * float(density_units(T_C)) + gamma_l
        g, prof = composite_profile(gc, sigma_g,
                                    transit_fwhm_at_T(T_C, TRANSIT_REF),
                                    "gaussian")
        return np.interp(nu, g, prof)

    def _cond_window(T_C):
        """The window the RECORD'S OWN estimator would use for this line.

        A first version of this block inherited the +-8 MHz grid of the
        fixed-condition sections above. An adversarial verification pass
        showed that window is less than half of what `adaptive_halfwidth`
        assigns to these lines (3.5 x FWHM, clipped to [9, 25] MHz, which
        lands at 17.5 to 19 MHz here), that the truncation moved the
        cost-of-freeing-Gamma_L figure by 27 per cent, and that the
        validation gate below passes at EITHER window and so cannot
        arbitrate. The window is therefore computed from the estimator's
        own rule rather than chosen, which removes it as a free parameter.
        """
        g, prof = composite_profile(
            BETA * float(density_units(T_C)) + GAMMA_L0, SIGMA_G,
            transit_fwhm_at_T(T_C, TRANSIT_REF), "gaussian")
        half = prof / prof.max() - 0.5
        n2 = len(g) // 2
        fwhm = g[n2:][np.argmin(np.abs(half[n2:]))] - g[:n2][np.argmin(np.abs(half[:n2]))]
        hw = float(np.clip(C.FIT_HALFWIDTH_FWHM_MULT * fwhm,
                           C.FIT_HALFWIDTH_MIN_MHZ, C.FIT_HALFWIDTH_MAX_MHZ))
        return np.linspace(-hw, hw, 1201)

    def _cond_block(T_C, params):
        """Projected, amplitude-weighted physics columns for one condition."""
        nu = _cond_window(T_C)
        base = dict(beta=BETA, sigma_g=SIGMA_G, gamma_l=GAMMA_L0)
        cols = []
        for name in params:
            h = REL_STEP * max(base[name], 1e-3)
            up, dn = dict(base), dict(base)
            up[name] += h
            dn[name] -= h
            cols.append((_mixed_cond(up["beta"], up["sigma_g"], up["gamma_l"], T_C, nu)
                         - _mixed_cond(dn["beta"], dn["sigma_g"], dn["gamma_l"], T_C, nu)) / (2 * h))
        prof = _mixed_cond(BETA, SIGMA_G, GAMMA_L0, T_C, nu)
        nuis = np.column_stack([prof, np.gradient(prof, nu),
                                np.ones_like(nu), nu])
        Q, _ = np.linalg.qr(nuis)
        amp = float(density_units(T_C))          # signal weight, ~ atom number
        return np.column_stack([amp * (c - Q @ (Q.T @ c)) for c in cols])

    def _fisher(params):
        J = np.vstack([_cond_block(T, params) for T in TEMPS_C])
        return np.linalg.inv(J.T @ J)

    def _corr(Cm, i, j):
        return float(Cm[i, j] / np.sqrt(Cm[i, i] * Cm[j, j]))

    # -- validation against the committed estimator (2 params, gaussian arm) --
    C2 = _fisher(("beta", "sigma_g"))
    corr2 = _corr(C2, 0, 1)
    ok = -0.97 <= corr2 <= -0.74     # the committed band plus modelling slack
    rows.append(dict(
        block="joint_cell_onf", kind="validation_cell_alone",
        corr_gamma_sigma=f"{corr2:+.4f}", sv_ratio="1.000",
        null_dir_gamma="", null_dir_sigma="",
        note=(f"the forecast machinery in the record's own 2-parameter form: "
              f"corr(beta, sigma_G) = {corr2:+.3f} against the committed "
              f"-0.82 to -0.89 (kernel_headline.csv, gaussian arm): "
              f"{'CREDIBLE, the rows below may be read' if ok else 'OUT OF BAND, do not read the rows below'}"),
        status="DIAGNOSTIC"))

    # -- the K3 model (3 params) and the prior scan ---------------------------
    C3m = _fisher(("beta", "sigma_g", "gamma_l"))
    sig_beta3 = float(np.sqrt(C3m[0, 0]))
    sig_beta2 = float(np.sqrt(C2[0, 0]))
    rows.append(dict(
        block="joint_cell_onf", kind="cost_of_freeing_gamma_L",
        corr_gamma_sigma=f"{_corr(C3m, 0, 2):+.4f}",
        sv_ratio=f"{sig_beta3 / sig_beta2:.3f}",
        null_dir_gamma=f"{_corr(C3m, 0, 1):+.4f}", null_dir_sigma="",
        note=("freeing Gamma_L inflates sigma(beta) by this factor over the "
              "2-parameter fit: what K3 pays for honesty about the "
              "kernel, and the quantity an ONF prior buys back"),
        status="DIAGNOSTIC"))

    for rel_w in (1.0, 0.5, 0.2, 0.1):
        for label, idx in (("GL", (2,)), ("GL_and_sigmaG", (2, 1))):
            F = np.linalg.inv(C3m).copy()
            for k in idx:
                w = rel_w * float(np.sqrt(C3m[k, k]))
                F[k, k] += 1.0 / w ** 2
            Cp = np.linalg.inv(F)
            rows.append(dict(
                block="joint_cell_onf", kind=f"prior_{label}_rel{rel_w:g}",
                corr_gamma_sigma=f"{_corr(Cp, 0, 2):+.4f}",
                sv_ratio=f"{float(np.sqrt(Cp[0, 0])) / sig_beta3:.3f}",
                null_dir_gamma=f"{float(np.sqrt(Cp[0, 0])) / sig_beta2:.3f}",
                null_dir_sigma="",
                note=(f"ONF prior at {rel_w:g} x the cell-alone width on "
                      f"{'Gamma_L alone' if label == 'GL' else 'both laser parameters'}: "
                      f"sigma(beta) at this fraction of the FREE-Gamma_L fit "
                      f"(sv_ratio) and of the 2-parameter fit (null_dir_gamma)"),
                status="DIAGNOSTIC"))

    # the true asymptote of the Gamma_L-alone route, not a sampled point
    F = np.linalg.inv(C3m).copy()
    F[2, 2] += 1.0 / (1e-6 * float(np.sqrt(C3m[2, 2]))) ** 2
    Cp = np.linalg.inv(F)
    rows.append(dict(
        block="joint_cell_onf", kind="floor_GL_alone",
        corr_gamma_sigma="",
        sv_ratio=f"{float(np.sqrt(Cp[0, 0])) / sig_beta3:.3f}",
        null_dir_gamma="", null_dir_sigma="",
        note=("the exact asymptote of a Gamma_L-only prior: however precise, "
              "sigma(beta) cannot fall below this fraction of the free fit "
              "while sigma_G stays free"),
        status="DIAGNOSTIC"))

    # ABSOLUTE anchoring: relative prior widths hide that the cell-alone
    # Gamma_L determination is itself weak, so a prior quoted as a modest
    # fraction of it is a demanding absolute measurement. Anchor the scale by
    # matching the 2-parameter forecast error on beta to the committed
    # beta_err of the same construction, then state the prior targets in MHz.
    with (C.RESULTS_DIR / "kernel_headline.csv").open() as fh:
        hrow = next(r for r in csv.DictReader(fh) if r["peak"] == "4121")
    anchor = float(hrow["beta_err_gaussian"]) / float(np.sqrt(C2[0, 0]))
    sig_gl_mhz = float(np.sqrt(C3m[2, 2])) * anchor
    sig_sg_mhz = float(np.sqrt(C3m[1, 1])) * anchor
    rows.append(dict(
        block="joint_cell_onf", kind="absolute_anchor",
        corr_gamma_sigma="",
        sv_ratio=f"{sig_gl_mhz:.3f}",
        null_dir_gamma=f"{sig_sg_mhz:.3f}", null_dir_sigma="",
        note=("cell-alone sigma(Gamma_L) and sigma(sigma_G) in MHz, anchored "
              "by matching the 2-parameter forecast to the committed "
              "beta_err_gaussian of the 4121 peak: the 0.2x prior row "
              f"therefore asks the ONF for {0.2 * sig_gl_mhz:.2f} MHz on "
              f"Gamma_L and {0.2 * sig_sg_mhz:.2f} MHz on sigma_G, which is "
              "the absolute precision target the instrument must meet"),
        status="DIAGNOSTIC"))

    F = np.linalg.inv(C3m).copy()
    for k in (1, 2):
        F[k, k] += 1.0 / (1e-6 * float(np.sqrt(C3m[k, k]))) ** 2
    Cp = np.linalg.inv(F)
    rows.append(dict(
        block="joint_cell_onf", kind="ceiling_laser_pinned",
        corr_gamma_sigma="",
        sv_ratio=f"{float(np.sqrt(Cp[0, 0])) / sig_beta3:.3f}",
        null_dir_gamma=f"{float(np.sqrt(Cp[0, 0])) / sig_beta2:.3f}",
        null_dir_sigma="",
        note=("both laser parameters pinned exactly: the ceiling of the "
              "prior route, relative to the free-Gamma_L fit (sv_ratio) and "
              "to the 2-parameter fit (null_dir_gamma)"),
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
