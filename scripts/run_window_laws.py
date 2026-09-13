#!/usr/bin/env python3
"""How each term of the composite line and each nuisance enters the
self-centred windowed cumulants AS A FUNCTION OF THE WINDOW, and what the even
window ladder measures once the nuisances are projected out.

THE QUESTION THIS ANSWERS (owner, 2026-09-13): the truncated window is not a
fixed statistic but a scan axis, and every term has a signature law in it. A
nuisance whose law is steeper than the physics' is removed by the scan. a term
whose law equals another's is one term with it. This producer measures the
laws on the package's own profile at the archive point, projects the one
nuisance that survives the wing baseline and the self-centring (the tilt) out
of the even ladder, and reports the per-trace information the ladder then
carries on the three width terms under four noise forms, with the covariance
of the 36 statistics taken from realisations and never assumed diagonal.

WHAT THE ROWS ARE. `law_<term>` rows: the log-log slope of |d k_n| over W in
4 to 20 MHz, one per order, err from the fit. `kept_<term>` rows: the fraction
of the term's noise-weighted sensitivity over the W grid that survives
projecting the tilt out, per even order. `sigma_ln_<param>` rows: the per-trace
sigma from the joint Fisher of k2, k4, k6 at twelve windows with the tilt free,
per noise form, err from a bootstrap of the realisation set. `bias_k<n>` rows:
the estimator's own noise-induced bias in units of its per-trace sd at 6 and
12 MHz, per noise form, err the standard error over realisations.

THE NOISE FORMS. White. AR(1) at the law's first lag rho1. AR(1) at the
coefficient the law's integrated time implies (the twin's `_correlate` form,
which overstates the first lag, as `run_moment_admission.py` records). and
white plus a slow wander carrying 30 per cent of the variance, the form the
law's tail (a blocking statistic still rising at L = 64) points at.

STATUS. Every row is a twin measurement at one parameter point on the
package's own profile, so every row is DIAGNOSTIC. the pooled archive figure
with the measured spectrum per condition is Phase 1's, not this file's.
"""
import csv
import os
import sys
from pathlib import Path

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s.cumulants import windowed_cumulants                    # noqa: E402
from rb5s6s.fullmodel import full_profile                          # noqa: E402
from rb5s6s.noise import load_noise_model                          # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402

POINT = dict(gamma_coll=0.55, sigma_laser_fwhm=1.6, transit_fwhm=0.9575,
             gamma_l=0.40, s0=0.364, peak="4192")
NU = np.linspace(-45.0, 45.0, 3601)
W = np.array([1.5, 2.0, 2.5, 3.25, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0])
ORDERS = (2, 3, 4, 5, 6, 7)
EVEN = (2, 4, 6)
NOISE_FRAC = 0.004
N_REAL = int(os.environ.get("N_REAL", "400"))
N_BOOT = 24
EPS = 0.02
ROLE = "p_sweep"
SEED = 20260913


def _prof(**kw):
    p = dict(POINT); p.update(kw)
    y = full_profile(NU, **p)
    return y / y.max()


def _cums(y, orders=ORDERS):
    out = {}
    for w in W:
        k, _ = windowed_cumulants(NU, y, w, orders=orders, baseline="wings")
        for n in orders:
            out[(n, w)] = k[n]
    return out


def _vec(c, n):
    return np.array([c[(n, w)] for w in W])


def _stat_even(y):
    c = _cums(y, EVEN)
    return np.concatenate([_vec(c, n) for n in EVEN])


def _ar1(rng, a):
    e = rng.standard_normal(NU.size)
    f = np.empty_like(e); f[0] = e[0]
    for i in range(1, e.size):
        f[i] = a * f[i - 1] + np.sqrt(1 - a * a) * e[i]
    return f * NOISE_FRAC


def _forms(rho1, tau_int):
    a_tau = (tau_int - 1.0) / (tau_int + 1.0)

    def white(rng):
        return rng.standard_normal(NU.size) * NOISE_FRAC

    def ar_rho(rng):
        return _ar1(rng, rho1)

    def ar_tau(rng):
        return _ar1(rng, a_tau)

    def wander(rng):
        w = _ar1(rng, rho1)
        rw = np.cumsum(rng.standard_normal(NU.size))
        rw -= np.polyval(np.polyfit(NU, rw, 1), NU)
        rw *= np.sqrt(0.3) * NOISE_FRAC / rw.std()
        return np.sqrt(0.7) * w + rw
    return {"white": white, "ar1_rho1": ar_rho, "ar1_tau_int": ar_tau, "white_plus_wander": wander}


def _slope(d):
    m = W >= 4.0
    if not np.all(d[m] > 0):
        return np.nan, np.nan
    x, yv = np.log(W[m]), np.log(d[m])
    A = np.vstack([x, np.ones_like(x)]).T
    coef, res, *_ = np.linalg.lstsq(A, yv, rcond=None)
    dof = max(len(x) - 2, 1)
    s2 = (res[0] / dof) if len(res) else float(np.sum((yv - A @ coef) ** 2) / dof)
    cov = s2 * np.linalg.inv(A.T @ A)
    return float(coef[0]), float(np.sqrt(cov[0, 0]))


def main() -> int:
    out_path = _CFG.RESULTS_DIR / "window_laws.csv"
    law = load_noise_model(str(_CFG.RESULTS_DIR / "noise_model.csv"), role=ROLE, pool="median")
    rho1, tau_int = float(law["rho1"]), float(law["tau_int"])
    rng = np.random.default_rng(SEED)
    y0 = _prof(); c0 = _cums(y0)
    terms = {
        "transit": _cums(_prof(transit_fwhm=POINT["transit_fwhm"] * (1 + EPS))),
        "lorentzian_sum": _cums(_prof(gamma_l=POINT["gamma_l"] * (1 + EPS))),
        "gaussian_laser": _cums(_prof(sigma_laser_fwhm=POINT["sigma_laser_fwhm"] * (1 + EPS))),
        "lorentzian_laser_form": _cums(_prof(laser_kind="lorentzian")),
        "tilt": _cums(y0 + 0.0005 * NU),
        "offset_after_wings": _cums(y0 + 0.005),
        "centre_shift": _cums(np.interp(NU, NU + 0.1, y0)),
    }
    rows = [["quantity", "window_mhz", "value", "err", "note", "status"]]
    for name, c in terms.items():
        for n in ORDERS:
            sl, se = _slope(np.abs(_vec(c, n) - _vec(c0, n)))
            v_cell, e_cell = ("", "") if np.isnan(sl) else pm_cells(sl, se)
            rows.append([f"law_{name}_k{n}", "4-20", v_cell, e_cell,
                         "log-log slope of |d k_n| over the window. blank when the signature is below the grid's resolution (removed by the wing baseline or the self-centring)", ""])
    # per-trace white sd for the weights
    forms = _forms(rho1, tau_int)
    real = {f: np.array([_stat_even(y0 + gen(rng)) for _ in range(N_REAL)]) for f, gen in forms.items()}
    s_white = real["white"].std(axis=0) + 1e-15
    nv = len(W)
    for i, n in enumerate(EVEN):
        sl = slice(i * nv, (i + 1) * nv)
        s = s_white[sl]
        t = (_vec(terms["tilt"], n) - _vec(c0, n)) / s
        Q = t / np.sqrt(t @ t)
        for name in ("transit", "lorentzian_sum", "gaussian_laser"):
            v = (_vec(terms[name], n) - _vec(c0, n)) / s
            res = v - Q * (Q @ v)
            rows.append([f"kept_{name}_k{n}", "1.5-20", f"{float(res @ res / (v @ v)):.2f}", "",
                         "fraction of the term's noise-weighted sensitivity over the twelve windows surviving the tilt's projection", ""])
    # joint Fisher with the tilt free, per noise form, bootstrap error
    s0 = _stat_even(y0)
    J = np.array([(_stat_even(_prof(transit_fwhm=POINT["transit_fwhm"] * (1 + EPS))) - s0) / EPS,
                  (_stat_even(_prof(gamma_l=POINT["gamma_l"] * (1 + EPS))) - s0) / EPS,
                  (_stat_even(_prof(sigma_laser_fwhm=POINT["sigma_laser_fwhm"] * (1 + EPS))) - s0) / EPS,
                  (_stat_even(y0 + 0.0001 * NU) - s0)]).T
    names = ("transit", "lorentzian_sum", "gaussian_laser")

    def sig_from(R):
        C = np.cov(R.T); C = 0.95 * C + 0.05 * np.diag(np.diag(C))
        F = J.T @ np.linalg.pinv(C) @ J
        cov = np.linalg.pinv(F)
        return np.sqrt(np.diag(cov))[:3], cov[0, 1] / np.sqrt(cov[0, 0] * cov[1, 1])
    for f, R in real.items():
        sig, corr = sig_from(R)
        boots = np.array([sig_from(R[rng.integers(0, N_REAL, N_REAL)])[0] for _ in range(N_BOOT)])
        for j, name in enumerate(names):
            rows.append([f"sigma_ln_{name}_{f}", "1.5-20", *pm_cells(float(sig[j]), float(boots[:, j].std())),
                         f"per-trace sigma on ln {name} from k2, k4, k6 at twelve windows with the tilt free and the empirical covariance of {N_REAL} realisations, shrunk 5 per cent to its diagonal. err from {N_BOOT} bootstrap resamples", ""])
        rows.append([f"corr_transit_lorentzian_{f}", "1.5-20", f"{corr:.2f}", "", "correlation of the transit and the Lorentzian sum in the joint covariance", ""])
        # the estimator's own bias at 6 and 12 MHz per order, from the same realisations
        for n_i, n in enumerate(EVEN):
            for wsel in (6.0, 12.0):
                k = n_i * nv + int(np.argmin(np.abs(W - wsel)))
                col = R[:, k]
                sd = col.std(); b = (col.mean() - s0[k]) / sd
                rows.append([f"bias_k{n}_{f}", f"{wsel:g}", *pm_cells(float(b), 1 / np.sqrt(N_REAL)),
                             "noise-induced bias of the self-centred windowed cumulant in units of its own per-trace sd", ""])
        for n_i, n in enumerate(EVEN):
            k6 = n_i * nv + int(np.argmin(np.abs(W - 6.0)))
            rows.append([f"sd_ratio_k{n}_{f}", "6", f"{R[:, k6].std() / real['white'][:, k6].std():.2f}", "",
                         "per-trace sd relative to the white form at 6 MHz", ""])
    rows.append(["noise_law_rho1", "", f"{rho1:.3f}", "", f"first-lag correlation of the {ROLE} law, pooled median", ""])
    rows.append(["noise_law_tau_int", "", f"{tau_int:.2f}", "", "integrated correlation time of the same law. the ar1_tau_int form uses (tau-1)/(tau+1)", ""])
    rows.append(["n_realisations", "", str(N_REAL), "", "per noise form", ""])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(rows)
    print(f"wrote {out_path} ({len(rows) - 1} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
