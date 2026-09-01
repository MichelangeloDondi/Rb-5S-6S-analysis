#!/usr/bin/env python3
"""Profile likelihood against an odd-cumulant likelihood, under model error.

THE QUESTION, AND WHY IT IS NOT SETTLED BY A THEOREM. Sufficiency says the
full-profile likelihood cannot be beaten by any statistic computed from the
same data, because a statistic is a function of the data and can only lose
information. That argument is sound and it is CONDITIONAL ON THE MODEL BEING
CORRECT. `results/fit_window_scan.csv` shows this model is not: the fitted
collisional width drifts with the fit window in 30 of 32 conditions over the wing-safe window range while the
chi-square stays flat, which is a tail the model does not carry. Under
misspecification the maximum-likelihood estimate converges to whatever
minimises the divergence from the wrong model, weighted by where the counts
are, and no theorem says that is the best estimate of an asymmetry.

So the comparison is empirical, and this is it. A twin injects a known S0,
then estimates it two ways:

  (A) the profile likelihood, fitting amplitude, collisional width, laser
      width, light shift and a per-trace centre;
  (B) a likelihood on the ODD cumulants kappa_3 and kappa_5 over two windows,
     which are blind to every symmetric kernel by parity and therefore to the
     laser width that A must fit.

WHAT IT MEASURES, AND WHAT IT DOES NOT. Bias and spread of each estimator with
and without a model error the fitter lacks, at two light shifts. It is ONE
defect shape, one drift scale, uniform sampling, no baseline and white noise,
so it is a statement about a mechanism and not a measurement of the archive.
The defect is deliberately ASYMMETRIC: a symmetric one cannot bias an
asymmetry much, which the producer records as its own control row.

    python scripts/run_estimator_duel.py    # about two minutes, seed-pinned
"""
from __future__ import annotations

import csv
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from _producer_lock import take_producer_lock                     # noqa: E402
from rb5s6s import config as C                                    # noqa: E402
from rb5s6s._compat import trapezoid as tz                        # noqa: E402
from rb5s6s.lineshape import model_profile                        # noqa: E402

OUT = C.RESULTS_DIR / "estimator_duel.csv"

GAMMA, SIGMA, TRANSIT = 0.55, 1.6, 1.8      # MHz, the campaign twin's own widths
SIGMA_HANDED_TO_B = 2.4                     # deliberately 50% wrong, to show parity
NU = np.linspace(-20, 20, 2001)
W1, W2 = 8.0, 16.0                          # the two moment windows, MHz
NTRACE = 25                                 # traces averaged into one realisation
DRIFT_MHZ = 0.30                            # per-realisation centre jitter
SAT_FRAC, SAT_OFFSET, SAT_GAMMA = 0.03, -4.0, 1.2   # the asymmetric defect
NREAL, NCOV = 120, 250
SEED = 9


def _prof(gamma, sigma, s0, centre):
    return np.interp(NU - centre, NU,
                     model_profile(NU, gamma_coll=gamma, sigma_laser_fwhm=sigma,
                                   transit_fwhm=TRANSIT, s0=s0))


def _truth(s0, centre, defect):
    y = _prof(GAMMA, SIGMA, s0, centre)
    if not defect:
        return y
    sat = np.interp(NU - centre - SAT_OFFSET, NU,
                    model_profile(NU, gamma_coll=SAT_GAMMA, sigma_laser_fwhm=SIGMA,
                                  transit_fwhm=TRANSIT, s0=s0))
    return (1 - SAT_FRAC) * y + SAT_FRAC * sat


def _odd_cumulants(y, W):
    """kappa_3 and kappa_5 about the trace's OWN centre. The cumulants are
    translation-invariant but the WINDOW is not, so the centre is estimated
    per trace and its jitter is a real cost of this estimator, not an
    idealisation away from one."""
    c = NU[int(np.argmax(np.convolve(y, np.ones(21) / 21, "same")))]
    m = np.abs(NU - c) <= W
    x, yy = NU[m] - c, np.clip(y[m], 0.0, None)
    area = tz(yy, x)
    if area <= 0:
        return np.nan, np.nan
    yy = yy / area
    m1 = tz(x * yy, x)
    mu = lambda k: tz((x - m1) ** k * yy, x)          # noqa: E731
    m2, m3, m5 = mu(2), mu(3), mu(5)
    return m3, m5 - 10 * m3 * m2


def _stats(y):
    a3, a5 = _odd_cumulants(y, W1)
    b3, _ = _odd_cumulants(y, W2)
    return np.array([a3, a5, b3])


def _fit_profile(data, noise, seed_s0):
    def r(q):
        return (q[0] * _prof(max(q[1], .05), max(q[2], .1), max(q[3], 0.), q[4])
                - data) / noise
    return least_squares(r, [1., GAMMA, SIGMA, seed_s0, 0.],
                         bounds=([.2, .05, .1, 0., -2.], [5., 3., 6., 12., 2.])).x[3]


def _fit_cumulants(data, chol, seed_s0, sigma_used):
    obs = _stats(data)
    if not np.all(np.isfinite(obs)):
        return np.nan
    def r(q):
        return chol @ (obs - _stats(_prof(max(q[0], .05), sigma_used,
                                          max(q[1], 0.), 0.)))
    return least_squares(r, [GAMMA, seed_s0],
                         bounds=([.05, 0.], [3., 12.])).x[1]


def _one(s0, defect, sigma_for_b):
    rng = np.random.default_rng(SEED)
    noise = 1e-3 * _truth(s0, 0., defect).max() / np.sqrt(NTRACE)
    draw = lambda: (_truth(s0, rng.normal(0, DRIFT_MHZ), defect)      # noqa: E731
                    + rng.normal(0, noise, NU.size))
    cov = np.cov(np.array([_stats(draw()) for _ in range(NCOV)]).T)
    chol = np.linalg.cholesky(np.linalg.inv(cov + 1e-18 * np.eye(3)))
    a = np.array([_fit_profile(draw(), noise, s0 * .7) for _ in range(NREAL)])
    b = np.array([_fit_cumulants(draw(), chol, s0 * .7, sigma_for_b)
                  for _ in range(NREAL)])
    return a[np.isfinite(a)], b[np.isfinite(b)]


def main() -> int:
    take_producer_lock("run_estimator_duel")
    rows, bias = [], {}
    for s0 in (3.0, 0.35):
        for defect in (False, True):
            a, b = _one(s0, defect, SIGMA_HANDED_TO_B)
            tag = f"S0_{s0:g}_{'defect' if defect else 'clean'}"
            for name, v in (("profile_mle", a), ("odd_cumulants", b)):
                bi = float(v.mean() - s0)
                bias[(name, s0, defect)] = bi
                rows.append([f"bias_{name}", tag, f"{bi:+.4f}", f"{v.std():.4f}",
                             f"MHz. RMSE {np.hypot(bi, v.std()):.4f}. "
                             f"{'an ASYMMETRIC defect the fitter lacks' if defect else 'model correct'}, "
                             f"injected S0 {s0:g} MHz, err column is the spread"])
        for name in ("profile_mle", "odd_cumulants"):
            shift = abs(bias[(name, s0, True)] - bias[(name, s0, False)])
            rows.append([f"defect_sensitivity_{name}", f"S0_{s0:g}", f"{shift:.4f}",
                         "", "MHz. How far the bias MOVES when the defect appears. "
                             "This, not the bias itself, is what robustness means"])
    # The control: B is handed a 50%-wrong laser width, to show parity holds.
    _, b_ok = _one(3.0, True, SIGMA)
    rows.append(["bias_odd_cumulants_correct_sigma", "S0_3_defect",
                 f"{float(b_ok.mean() - 3.0):+.4f}", f"{b_ok.std():.4f}",
                 f"MHz. Same as bias_odd_cumulants but with the TRUE laser width "
                 f"{SIGMA} rather than {SIGMA_HANDED_TO_B}. The gap is what the "
                 f"laser width costs the cumulant route, and it is small because "
                 f"a symmetric kernel contributes nothing to a SELF-CENTRED "
                 f"odd moment (the Lorentzian to the truncation fraction "
                 f"docs/wiki/third-cumulant.md quantifies)"])
    # The sigma-blindness of the self-centred kappa_3, with its centring
    # NAMED because the same number under a lab-frame window is two orders
    # larger (audit finding, 2026-08-31): windows ride the profile's own
    # mean, the translation-invariant centring the fit licenses.
    def _k3_centred(sigma):
        # MEAN-centred by fixed point on a fine local grid, with the
        # earlier centrings emitted as rows below so every retracted
        # number stays reproducible: mean-centred 110.3, lab-frame 3.3,
        # mode-on-trace-grid 175.2 (all per cent, this sweep, the rows'
        # own values). The first version used the mode and shipped an
        # irreproducible figure; mode and mean differ by O(S0), and that
        # offset leaks kappa_1 into kappa_3. The trio shares a four-pass
        # fixed point on a 40001-point grid, stated here because a sister
        # producer's four-pass mean-pull was construction-sensitive at the
        # 0.1 per cent scale.
        fine = np.linspace(-20.0, 20.0, 40001)
        y = np.interp(fine, NU, _prof(GAMMA, sigma, 3.0, 0.0))
        c = 0.0
        for _ in range(4):                      # fixed point: c -> windowed mean
            w = np.abs(fine - c) <= W1
            x, yy = fine[w] - c, np.clip(y[w], 0, None)
            yy = yy / tz(yy, x)
            c = c + tz(x * yy, x)
        w = np.abs(fine - c) <= W1
        x, yy = fine[w] - c, np.clip(y[w], 0, None)
        yy = yy / tz(yy, x); m1 = tz(x * yy, x)
        return tz((x - m1) ** 3 * yy, x)
    k3a, k3b = _k3_centred(SIGMA), _k3_centred(SIGMA * 4)
    rows.append(["kappa3_sigma_blindness_pct", "S0_3",
                 f"{100 * abs(k3b / k3a - 1):.1f}", "",
                 f"per cent change of the self-centred windowed kappa_3, window "
                 f"+/-{W1:g} MHz about its own mean (the centre iterated until "
                 f"it equals the windowed mean), laser width {SIGMA} to "
                 f"{SIGMA*4} MHz. Earlier centrings in the two rows below"])

    def _k3_at(centre_mode, sigma):
        fine = np.linspace(-20.0, 20.0, 40001)
        y = np.interp(fine, NU, _prof(GAMMA, sigma, 3.0, 0.0))
        if centre_mode == "lab":
            c = 0.0
        else:                                   # the first version's mode
            c = NU[int(np.argmax(np.convolve(_prof(GAMMA, sigma, 3.0, 0.0),
                                             np.ones(201) / 201, "same")))]
        w = np.abs(fine - c) <= W1
        x, yy = fine[w] - c, np.clip(y[w], 0, None)
        yy = yy / tz(yy, x); m1 = tz(x * yy, x)
        return tz((x - m1) ** 3 * yy, x)
    for mode, name in (("lab", "labframe"), ("mode", "modecentred")):
        a, b = _k3_at(mode, SIGMA), _k3_at(mode, SIGMA * 4)
        rows.append([f"kappa3_sigma_blindness_{name}_pct", "S0_3",
                     f"{100 * abs(b / a - 1):.1f}", "",
                     f"the same sweep under the earlier "
                     f"{'window pinned at the laboratory zero' if mode == 'lab' else 'smoothed-mode centring on the trace grid'}, "
                     f"kept so the retracted variants stay reproducible"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for k, v in sorted(bias.items()):
        print(f"  {k[0]:>14} S0={k[1]:<5} defect={str(k[2]):<5} bias {v:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
