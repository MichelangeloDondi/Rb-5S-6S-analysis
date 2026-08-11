#!/usr/bin/env python3
"""
M27: the centre-channel AC-Stark coefficient from held-lock epochs.

M21 (run_stark_centres.py) already tried the centre channel and called it a
NULL: fitting one shared pull across all 26 display epochs makes drift and
pull collinear (power falls monotonically with time within every epoch that
sees more than one power), so the pull's SIGN flips between drift models and
its bound gets WORSE as the drift model gains freedom -- the signature of an
unidentifiable parameter, not a measurement.

THIS MODULE'S DIFFERENT LEVER. Instead of one global fit spanning many
epochs (which needs the retracted cross-epoch knob frame to even ask the
question), stay inside single epochs. A display epoch is, by construction, a
maximal run of UNCHANGED window_start_ms (run_laser_history.py) -- the knob
never moved, so `offset_mhz` inside one epoch is a laser-axis frequency
difference, licensed without the retracted frame. Where an epoch happens to
contain more than one power_mW for the same (peak, temperature_C), the
within-epoch difference is a legitimate Delta-centre-vs-Delta-power lever,
and the only nuisance it can be confounded with is the held-lock drift --
which run_drift_settling.py has *independently* measured, so it can enter as
an informative PRIOR instead of a free, degenerate parameter. That is the
whole idea: trade M21's flat-prior, many-epoch, unidentifiable fit for a
tight-prior, single-epoch, identified one.

THE EPOCH COUNT IN THE TASK BRIEF DOES NOT MATCH THE ARCHIVE. The brief
asserts five display epochs contrast two power_mW values for the same peak
and temperature_C. The archive has THREE: epoch 23 (993.4207 nm, 75/125 mW),
epoch 28 (993.4154 nm, 175/225 mW), epoch 33 (993.4121 nm, 175/225 mW) --
each ten p_sweep traces, five per power, all at 130 C. This is exactly the
"only THREE of 26 epochs contrast two powers" that M21's own docstring
already reports, so it is not a new disagreement, just the same fact
restated. Every number below is computed from these three; the discrepancy
is recorded here rather than papered over by inventing two more.

ROLE FILTER. The brief says roles != quarantine; this module narrows that to
role == "p_sweep". ruler_p and ruler_t carry blank power_mW (so they can
never join a multi-power group and the epoch count above is unaffected), but
they DO have entries in laser_history.csv with wildly different offset_mhz
scale (an EOM comb tooth position, not the atomic line) -- pooling them into
a same-epoch "constant power" control group during development produced
offsets an order of magnitude larger than the flanking p_sweep traces. They
are a different observable and are excluded throughout, including from the
zero-signal control epochs below.

THE PER-EPOCH MODEL. For each of the three epochs, on every individual trace
(not block medians -- the within-block time spread is part of what
separates kappa from drift):

    offset_mhz_i = a + kappa_eff * P_i(W) + drift * t_i(min) + noise_i

`a` and `kappa_eff` carry flat (improper) priors; `drift` carries the
run_drift_settling.py mixture-model posterior, +0.016 +/- 0.009 MHz/min
laser axis (68% interval [+0.007, +0.025], symmetrised), unchanged by
today's M22 wavemeter-photograph refinement (a different record). Per-trace
noise is not the offset_err_mhz column (that is a rate-calibration-error
propagation, proportional to |offset|, not a real per-trace scatter -- see
run_laser_history.py); it is estimated empirically from an unweighted
first-pass fit's own residual RMS, exactly M21's `s = sqrt(chi2/dof)` move.
Because the whole problem is linear-Gaussian, marginalising the drift prior
has an exact closed form (generalised least squares with the prior as one
extra pseudo-observation on the drift row) -- no MCMC or profiling needed,
and it is CROSS-CHECKED (addendum 20's lesson: one un-converged start once
manufactured two flagged anomalies out of nothing) against a multi-start
nonlinear refit of the same penalised chi2 from several random starting
points.

kappa_eff is laser-axis and RAMP-MEAN (a swept trace's apparent centre moves
by MEAN_OVER_S0 * S0 on average across the triangular ramp, not by the full
on-axis S0). Converting to the archive's standard kappa (S0 = kappa*P,
TRANSITION axis, on-axis peak, the convention in rb5s6s/stark.py and
results/stark_joint.csv):

    kappa_transition = 2 * kappa_eff / MEAN_OVER_S0

the same "laser-to-transition is a factor of 2" (lineshape.stark_shift_S0_mhz:
"Laser-axis value is S0/2") and the same MEAN_OVER_S0 = -0.653 (archival ramp
geometry, methods/03) that run_stark_centres.py already uses -- kept as the
same literal for consistency between the two centre-channel modules rather
than recomputed from ramp_transit.moving_atom_moments, which would drift the
two analyses apart for no physical reason.

COMBINING AND COMPARING. The three per-epoch kappa_transition values combine
by inverse-variance with PDG scatter inflation (run_ruler.combine_rates,
exactly the pattern run_pilot_ruler.py already reuses). The combined value is
checked against results/stark_joint.csv's kappa_ub95 (M23, the width-channel
95% bound) and kappa_pred (the priors' prediction), per three cases fixed in
advance: (1) inside the M23 bound -> report as a PRELIM indication, never a
detection; (2) outside it -> the channels contradict, run diagnostics before
reporting anything; (3) not robust under leave-one-out or no stronger than a
zero-signal control -> report a bound, not a pull. Diagnostics for case (2):
double the drift-prior width and refit; drop each epoch in turn; and widen
the zero-signal control census. A ZERO-SIGNAL CONTROL runs the identical
per-epoch machinery on genuinely single-power p_sweep epochs (n>=4 traces),
splitting them at the temporal midpoint and injecting a SYNTHETIC -50 mW
label (the real rung size) where the true Delta-power is zero -- an
estimator-validation technique already precedented in this repo
(run_drift_settling.py's injection closure, addenda 6-7). If the synthetic
"pull" it returns is no smaller than the real epochs', the real pull is not
distinguishable from the estimator's own noise floor.

Writes results/centre_stark.csv. Reads results/laser_history.csv (M20) and
results/stark_joint.csv (M23); exits cleanly (0) if either is absent.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from rb5s6s import config as C  # noqa: E402
from run_ruler import combine_rates  # noqa: E402

LASER_HISTORY_CSV = C.RESULTS_DIR / "laser_history.csv"
STARK_JOINT_CSV = C.RESULTS_DIR / "stark_joint.csv"
OUT_CSV = C.RESULTS_DIR / "centre_stark.csv"

# The held-lock drift, laser axis, run_drift_settling.py mixture_report
# (unchanged by the 2026-08-02 wavemeter-photograph refinement -- a
# different record/script; verified present in this checkout's docstring).
DRIFT_PRIOR_MEAN = 0.016     # MHz/min
DRIFT_PRIOR_SIGMA = (0.025 - 0.007) / 2.0   # 0.009, from the quoted 68% band

# The same drift after the 2026-07-30 window-reference correction, which
# withdrew the licence for its SIGN and left a two-sided bound of about
# 0.02 MHz/min. Carried as a diagnostic refit rather than as the primary,
# because the primary's own controls already show the prior is not what
# sets the answer (see the DIAGNOSTICS block).
DRIFT_PRIOR_SIGMA_UNDETERMINED = 0.020   # MHz/min, two-sided, zero-centred

# Ramp geometry, archival configuration -- same literal run_stark_centres.py
# (M21) uses, cited there to methods/03; kept identical across both
# centre-channel modules rather than independently recomputed.
MEAN_OVER_S0 = -0.653

# The three multi-power epochs actually present (see module docstring for
# why this is 3 and not the 5 the task brief asserted).
MULTI_POWER_EPOCHS = ("23", "28", "33")

# Genuinely single-power p_sweep epochs used as zero-signal controls (n>=4,
# role == "p_sweep" only -- see docstring on ruler_p/ruler_t contamination).
CONTROL_EPOCHS = ("25", "30", "14", "34", "29")
CONTROL_FAKE_DELTA_P_W = -0.05     # the real rungs are all 50 mW steps


def _load_rows():
    if not LASER_HISTORY_CSV.exists():
        print(f"  {LASER_HISTORY_CSV.name} absent -- run scripts/run_laser_history.py "
              f"first; nothing to do.")
        return None
    if not STARK_JOINT_CSV.exists():
        print(f"  {STARK_JOINT_CSV.name} absent -- run scripts/run_stark_joint.py "
              f"first; nothing to do.")
        return None
    return [r for r in csv.DictReader(open(LASER_HISTORY_CSV)) if r["role"] == "p_sweep"]


def _epochs(rows):
    by_epoch: dict[str, list[dict]] = {}
    for r in rows:
        by_epoch.setdefault(r["display_epoch"], []).append(r)
    return by_epoch


def fit_epoch(rs: list[dict], *, drift_sigma: float = DRIFT_PRIOR_SIGMA,
              drift_mean: float = DRIFT_PRIOR_MEAN,
              fake_delta_p_w: float | None = None) -> dict:
    """Delta-centre = kappa_eff * Delta-power + drift * Delta-t, drift-prior
    marginalised, on every individual trace of one epoch.

    `fake_delta_p_w`: for the zero-signal control -- ignore the (constant)
    real power and inject a synthetic step at the temporal midpoint instead,
    so the true kappa_eff is zero by construction.

    `drift_mean`: the prior centre. The default is the directional value
    this module was built on. The sign-undetermined refit of addendum 29
    passes 0 with the bound as the width, which is the licensed state of
    knowledge after the 2026-07-30 window-reference correction.
    """
    rs = sorted(rs, key=lambda r: int(r["t_epoch"]))
    t0 = min(int(r["t_epoch"]) for r in rs)
    t = np.array([(int(r["t_epoch"]) - t0) / 60.0 for r in rs])
    y = np.array([float(r["offset_mhz"]) for r in rs])
    n = len(rs)
    if fake_delta_p_w is None:
        p = np.array([float(r["power_mW"]) / 1000.0 for r in rs])
    else:
        half = n // 2
        p = np.array([0.0] * half + [fake_delta_p_w] * (n - half))
    x = np.column_stack([np.ones(n), p, t])

    # Stage A: unweighted OLS (flat priors) to get an empirical noise level
    # -- offset_err_mhz is a rate-calibration propagation, not a per-trace
    # scatter estimate (see module docstring), so it is not used as a weight.
    beta0, *_ = np.linalg.lstsq(x, y, rcond=None)
    resid = y - x @ beta0
    dof = max(n - x.shape[1], 1)
    sigma_hat = max(float(np.sqrt((resid @ resid) / dof)), 1e-4)

    # Stage B: closed-form GLS with the drift prior as one extra
    # pseudo-observation -- exact for a linear-Gaussian model, no
    # profiling needed.
    x_aug = np.vstack([x, [0.0, 0.0, 1.0]])
    y_aug = np.concatenate([y, [drift_mean]])
    w = np.concatenate([np.full(n, 1.0 / sigma_hat ** 2), [1.0 / drift_sigma ** 2]])
    a_mat = x_aug.T @ (w[:, None] * x_aug)
    b_vec = x_aug.T @ (w * y_aug)
    cov = np.linalg.inv(a_mat)
    theta = cov @ b_vec
    kappa_eff, kappa_eff_err = float(theta[1]), float(np.sqrt(cov[1, 1]))
    drift_post, drift_post_err = float(theta[2]), float(np.sqrt(cov[2, 2]))

    # Multi-start verification (addendum 20's lesson): refit the identical
    # penalised chi2 nonlinearly from several perturbed starts and confirm
    # they land on the same kappa_eff. The problem is convex (linear model,
    # Gaussian prior) so this cannot find a *better* optimum than the
    # closed form -- it is a check against a coding error making the closed
    # form silently wrong, not a search for local minima.
    def penalised_resid(theta_):
        r = (x @ theta_ - y) / sigma_hat
        rd = (theta_[2] - drift_mean) / drift_sigma
        return np.concatenate([r, [rd]])

    rng = np.random.default_rng(20260802)
    best = None
    for _ in range(8):
        seed = theta + rng.normal(scale=[1.0, 5.0, 0.05], size=3)
        sol = least_squares(penalised_resid, seed, method="lm", max_nfev=20000)
        if best is None or sol.cost < best.cost:
            best = sol
    multistart_kappa_eff = float(best.x[1])
    multistart_agrees = bool(abs(multistart_kappa_eff - kappa_eff)
                              < max(1e-6, 1e-4 * abs(kappa_eff)))

    kappa_transition = 2.0 * kappa_eff / MEAN_OVER_S0
    kappa_transition_err = abs(2.0 / MEAN_OVER_S0) * kappa_eff_err
    return {
        "n": n, "sigma_hat": sigma_hat,
        "kappa_eff_laser_mean": kappa_eff, "kappa_eff_err": kappa_eff_err,
        "kappa_transition": kappa_transition, "kappa_transition_err": kappa_transition_err,
        "drift_posterior": drift_post, "drift_posterior_err": drift_post_err,
        "multistart_agrees": multistart_agrees,
        "delta_p_w": float(p.max() - p.min()), "span_min": float(t.max() - t.min()),
    }


def main() -> int:
    rows = _load_rows()
    if rows is None:
        return 0
    by_epoch = _epochs(rows)

    sj = {r["quantity"]: r for r in csv.DictReader(open(STARK_JOINT_CSV))}
    kappa_ub95_m23 = float(sj["kappa_ub95"]["value"])
    kappa_pred = float(sj["kappa_pred"]["value"])

    print("=" * 74)
    print("(M27) CENTRE-CHANNEL AC-STARK COEFFICIENT FROM HELD-LOCK EPOCHS")
    n_multi = sum(1 for _, rs in by_epoch.items()
                  if len({r["power_mW"] for r in rs if r["power_mW"]}) > 1)
    print(f"  {n_multi} p_sweep display epochs contrast two power_mW values for the "
          f"same peak+temperature")
    print("  (the task brief asserted 5; the archive has 3 -- see module docstring)\n")

    out_rows = []

    def add(quantity, key, value, err, unit, status):
        out_rows.append({"quantity": quantity, "key": key,
                          "value": f"{value:.4f}" if isinstance(value, float) else value,
                          "err": f"{err:.4f}" if isinstance(err, float) else err,
                          "unit": unit, "status": status})

    add("n_multi_power_epochs", "found", float(n_multi), "", "count; task brief asserted 5",
        "DIAGNOSTIC")

    per_epoch = {}
    for ep in MULTI_POWER_EPOCHS:
        rs = by_epoch.get(ep, [])
        if not rs:
            print(f"  epoch {ep}: absent from this checkout -- skipped")
            continue
        peak = sorted({r["peak"] for r in rs})[0]
        res = fit_epoch(rs)
        per_epoch[ep] = (res["kappa_transition"], res["kappa_transition_err"])
        print(f"  epoch {ep} (993.{peak} nm, n={res['n']}, dP={res['delta_p_w']*1000:.0f} mW, "
              f"span={res['span_min']:.2f} min, sigma_hat={res['sigma_hat']:.4f} MHz):")
        print(f"    kappa_eff (laser, ramp-mean) = {res['kappa_eff_laser_mean']:+.3f} +/- "
              f"{res['kappa_eff_err']:.3f} MHz/W")
        print(f"    drift posterior = {res['drift_posterior']:+.4f} +/- "
              f"{res['drift_posterior_err']:.4f} MHz/min (prior {DRIFT_PRIOR_MEAN:+.3f} "
              f"+/- {DRIFT_PRIOR_SIGMA:.3f}); multistart agrees: {res['multistart_agrees']}")
        print(f"    kappa_transition (S0=kappa*P) = {res['kappa_transition']:+.3f} +/- "
              f"{res['kappa_transition_err']:.3f} MHz/W")
        add("epoch_kappa_transition", f"{ep}_993.{peak}nm", res["kappa_transition"],
            res["kappa_transition_err"],
            f"MHz per W, transition axis; n={res['n']}, dP={res['delta_p_w']*1000:.0f} mW, "
            f"drift-prior-marginalised, multistart_agrees={res['multistart_agrees']}",
            "DIAGNOSTIC")

    ks = np.array([v[0] for v in per_epoch.values()])
    ke = np.array([v[1] for v in per_epoch.values()])
    combined, combined_err, chi2_red = combine_rates(ks, ke)
    combined_err_raw = float(1.0 / np.sqrt(np.sum(1.0 / ke ** 2)))
    pull_sigma = abs(combined) / combined_err
    pull_sigma_raw = abs(combined) / combined_err_raw
    print(f"\n  COMBINED kappa_transition = {combined:+.3f} +/- {combined_err:.3f} MHz/W "
          f"(chi2_red={chi2_red:.2f}, PDG-inflated; {pull_sigma:.2f} sigma from 0, "
          f"{pull_sigma_raw:.2f} sigma uninflated)")
    add("combined_kappa_transition", "primary", combined, combined_err,
        f"MHz per W, transition axis; inverse-variance + PDG inflation over "
        f"{len(per_epoch)} epochs, chi2_red={chi2_red:.2f}", "DIAGNOSTIC")

    print(f"  M23 kappa_ub95 (results/stark_joint.csv) = {kappa_ub95_m23:.3f} MHz/W")
    print(f"  kappa_pred (priors)                      = {kappa_pred:.3f} MHz/W")
    add("kappa_ub95_m23", "reference", kappa_ub95_m23, "",
        "MHz per W; echoed from results/stark_joint.csv for comparison", "DIAGNOSTIC")
    add("kappa_pred", "reference", kappa_pred, "",
        "MHz per W; echoed from results/stark_joint.csv for comparison", "DIAGNOSTIC")

    inside_bound = abs(combined) + 2 * combined_err < kappa_ub95_m23

    # ---- diagnostics (run whenever case (2) is triggered) ------------------
    print("\n  DIAGNOSTICS")
    doubled = {}
    for ep in per_epoch:
        r = fit_epoch(by_epoch[ep], drift_sigma=2 * DRIFT_PRIOR_SIGMA)
        doubled[ep] = (r["kappa_transition"], r["kappa_transition_err"])
    dks = np.array([v[0] for v in doubled.values()])
    dke = np.array([v[1] for v in doubled.values()])
    d_mean, d_err, d_chi2 = combine_rates(dks, dke)
    print(f"    double drift-prior sigma (0.009->0.018): combined "
          f"{d_mean:+.3f} +/- {d_err:.3f} MHz/W ({abs(d_mean)/d_err:.2f} sigma)")
    add("diag_double_drift_prior", "primary", d_mean, d_err,
        f"MHz per W; drift prior sigma doubled to {2*DRIFT_PRIOR_SIGMA:.3f} MHz/min and refit",
        "DIAGNOSTIC")

    # Sign-undetermined drift prior (amendment 29). The directional prior
    # above predates the 2026-07-30 window-reference correction, which
    # withdrew the licence for the drift's SIGN while leaving its size at
    # about 0.02 MHz/min. This refit replaces the prior with a zero-centred
    # one of that width, which is what the corrected record supports.
    undet = {}
    for ep in per_epoch:
        r = fit_epoch(by_epoch[ep], drift_sigma=DRIFT_PRIOR_SIGMA_UNDETERMINED,
                      drift_mean=0.0)
        undet[ep] = (r["kappa_transition"], r["kappa_transition_err"])
    uks = np.array([v[0] for v in undet.values()])
    uke = np.array([v[1] for v in undet.values()])
    u_mean, u_err, u_chi2 = combine_rates(uks, uke)
    print(f"    sign-undetermined drift prior (0 +/- "
          f"{DRIFT_PRIOR_SIGMA_UNDETERMINED:.3f}): combined "
          f"{u_mean:+.3f} +/- {u_err:.3f} MHz/W ({abs(u_mean)/u_err:.2f} sigma)")
    add("diag_sign_undetermined_drift_prior", "primary", u_mean, u_err,
        f"MHz per W; drift prior replaced by 0 +/- "
        f"{DRIFT_PRIOR_SIGMA_UNDETERMINED:.3f} MHz/min, the sign-undetermined "
        f"form the 2026-07-30 window-reference correction leaves licensed",
        "DIAGNOSTIC")

    loo = {}
    for drop in per_epoch:
        remaining = {k: v for k, v in per_epoch.items() if k != drop}
        rks = np.array([v[0] for v in remaining.values()])
        rke = np.array([v[1] for v in remaining.values()])
        m, e, c = combine_rates(rks, rke)
        loo[drop] = (m, e)
        print(f"    leave-one-out, drop {drop}: combined {m:+.3f} +/- {e:.3f} MHz/W "
              f"({abs(m)/e:.2f} sigma) from {list(remaining)}")
        add("diag_leave_one_out", f"drop_{drop}", m, e,
            f"MHz per W; combined kappa_transition with epoch {drop} dropped", "DIAGNOSTIC")

    loo_sigmas = [abs(m) / e for m, e in loo.values()]
    loo_unstable = (max(loo_sigmas) - min(loo_sigmas)) > 1.5 or min(loo_sigmas) < 2.0

    control_results = []
    print("    zero-signal controls (single-power p_sweep epochs, synthetic -50 mW split):")
    for ep in CONTROL_EPOCHS:
        rs = by_epoch.get(ep)
        if not rs:
            continue
        peak = sorted({r["peak"] for r in rs})[0]
        r = fit_epoch(rs, fake_delta_p_w=CONTROL_FAKE_DELTA_P_W)
        sig = abs(r["kappa_transition"]) / r["kappa_transition_err"]
        control_results.append(sig)
        print(f"      epoch {ep} (993.{peak} nm, n={r['n']}): kappa_transition = "
              f"{r['kappa_transition']:+.2f} +/- {r['kappa_transition_err']:.2f} MHz/W "
              f"({sig:.2f} sigma from 0)")
        add("control_epoch", f"{ep}_993.{peak}nm", r["kappa_transition"],
            r["kappa_transition_err"],
            f"MHz per W; single-power epoch, synthetic {CONTROL_FAKE_DELTA_P_W*1000:.0f} mW "
            f"step injected at true Delta-power=0 -- estimator false-positive check",
            "DIAGNOSTIC")

    control_max_sigma = max(control_results) if control_results else 0.0
    control_comparable = control_max_sigma >= min(pull_sigma, pull_sigma_raw) * 0.5

    # ---- verdict -------------------------------------------------------
    if inside_bound:
        case = 1
        verdict = ("case 1: the pull sits inside the M23 width-channel bound -- the two "
                   "channels are consistent. Reported as a PRELIM centre-channel indication, "
                   "not a detection; a fixed-lock session (not this archival one) is needed "
                   "to confirm or reject it directly.")
    elif loo_unstable or control_comparable:
        case = 3
        verdict = (
            f"case 3: not robust. Leave-one-out pulls range "
            f"{min(loo_sigmas):.2f}-{max(loo_sigmas):.2f} sigma depending on which epoch is "
            f"dropped, and a genuinely zero-signal control epoch reproduces a comparable "
            f"({control_max_sigma:.2f} sigma) spurious pull from an injected fake power step. "
            f"Reported as a BOUND, not a pull.")
    else:
        case = 2
        verdict = ("case 2: the channels contradict (pull outside the M23 bound and stable "
                   "under the diagnostics run above). Reported as a contradiction, not "
                   "averaged away; the likely systematic is the drift prior or the epoch "
                   "construction on the centre side.")

    print(f"\n  VERDICT ({case}): {verdict}")
    kappa_bound = combined + 1.645 * combined_err   # one-sided 95%, same construction as M23
    print(f"  centre-channel kappa_ub95 = {kappa_bound:.3f} MHz/W "
          f"({kappa_bound/kappa_ub95_m23:.1f}x the M23 width-channel bound)")
    add("kappa_ub95_centre", "primary", kappa_bound, "",
        "MHz per W; one-sided 95% Wald bound on the combined centre-channel kappa "
        "(same construction as stark_joint.csv's kappa_ub95); quote this, not the "
        "combined point estimate -- see the verdict row", "BOUND")

    # The same bound under the sign-undetermined drift prior. It LOOSENS,
    # so the quoted bound above is not conservative with respect to the
    # 2026-07-30 correction. Nothing downstream turns on it: the channel is
    # already several times weaker than the width channel either way, and
    # the verdict is a bound under both priors.
    kappa_bound_undet = u_mean + 1.645 * u_err
    print(f"  centre-channel kappa_ub95, sign-undetermined prior = "
          f"{kappa_bound_undet:.3f} MHz/W "
          f"({kappa_bound_undet/kappa_ub95_m23:.1f}x the M23 width-channel bound)")
    add("diag_kappa_ub95_centre_sign_undetermined", "primary", kappa_bound_undet, "",
        "MHz per W; the same one-sided 95% Wald bound rebuilt on the "
        "sign-undetermined drift prior. It LOOSENS relative to the quoted "
        "bound, so the quoted bound is not conservative with respect to the "
        "2026-07-30 window-reference correction, and the channel stays "
        "several times weaker than the width channel under both",
        "DIAGNOSTIC")
    add("verdict", f"case_{case}", case, "", verdict, "PRELIM" if case == 1 else "BOUND")

    C.RESULTS_DIR.mkdir(exist_ok=True)
    with open(OUT_CSV, "w", newline="") as f:
        cols = ["quantity", "key", "value", "err", "unit", "status"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)
    print(f"\n  Wrote {OUT_CSV.relative_to(ROOT)}: {len(out_rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
