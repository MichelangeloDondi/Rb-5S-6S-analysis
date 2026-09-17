#!/usr/bin/env python3
"""The far wing of every canonical condition: the one statistic that is not
the width again, read as a meter of the Lorentzian sum.

WHY THIS EXISTS. At one condition every shape statistic inside 12 MHz moves in
the same direction under the transit, the laser width and the Lorentzian
floor, so the whole even ladder over three windows is one number, the width.
The mean level over 15 to 40 MHz from the centre is the exception: a Gaussian
or a cusp of a few MHz is gone there, and the level is the Lorentzian sum's
alone, natural plus collisional plus whatever Lorentzian the laser carries.
Along the temperature arm at 225 mW that sum is gamma_nat + gamma_l + beta N(T),
so the far wing's slope against the number density is beta and its intercept
is the density-free floor, on a channel no window inside 12 MHz sees and one
that the transit-against-laser degeneracy of the core fits cannot reach.

WHAT IS MEASURED, per canonical RF-off trace of the two sweeps.

  1. The per-trace nuisances of the committed condition fit are re-solved at
     the committed shape (`results/linefit_conditions.csv`: gamma_coll and
     sigma_laser per condition, the transit at the adopted waist, no shift,
     a Gaussian laser), because the committed file carries the shared widths
     and NOT the per-trace centre, amplitude, offset and slope. The centre is
     seeded from the committed QC peak position (`results/qc_metrics.csv`)
     and refined by a scan with one parabolic step on the committed profile
     over the fit's own adaptive window, with the fit's own weights (the
     a^2 + bV law of `results/noise_model.csv` whitened by tau_int). The
     amplitude, offset and slope are then one weighted linear solve, with
     their covariance. Nothing about the shape is fitted here.
  2. The far-wing level is the mean of the trace minus that linear baseline
     over 15 <= |nu - centre| <= 40 MHz, both sides together, divided by the
     fitted peak height (the amplitude times the profile's maximum). Its bar
     is the noise law's variance over the window's samples, times tau_int for
     the correlation, plus the baseline's extrapolation error through the
     linear solve's covariance. The blue-minus-red asymmetry is reported
     beside it, because a dim trace's baseline wanders at the level the wing
     sits at and the asymmetry is what shows it.
  3. Per condition the traces are pooled by inverse variance. the block
     scatter over the repeats and the chi-squared of the pool are written in
     the note so a cell whose scatter exceeds its noise bar can be read as
     such.
  4. Beside each cell: the level the committed composite predicts over the
     same window (the model at the committed widths), the level a bare
     Lorentzian of gamma_nat + gamma_coll predicts, and the homogeneous width
     the measured level implies when the composite's Lorentzian is the only
     thing allowed to move. That width minus the committed gamma_nat +
     gamma_coll is the Lorentzian excess the far wing wants beyond the core
     fit, which is the far wing's own reading of gamma_l.
  5. The temperature arm at 225 mW (70, 90, 110 C from the t_sweep and the
     130 C corner from the p_sweep at 225 mW), per peak and pooled, fitted as
     a line in N(T) under each of the three vapour-pressure laws of
     `results/density_laws.csv`: the level's slope and intercept, and the
     implied homogeneous width's slope (beta, MHz per 1e12 cm^-3) and
     intercept (the floor, whose excess over gamma_nat is gamma_l's meter).

WHAT THE COMMITTED FITS COULD NOT SUPPLY. The per-trace centres and
amplitudes, which is why step 1 exists and why every row's note says the
nuisances were re-solved. A future commit of the per-trace fit parameters
replaces that step by a read.

FAILURE MODES. A window that reaches past the trace fills with the last
sample: a side whose 15 to 40 MHz span is not fully inside the trace is
refused for that trace, and the cell's note counts the refusals. A level read
against the QC baseline rather than the fitted linear baseline is wrong by the
Doppler pedestal and the detector's drift, which is why the baseline is the
fit's own. The bar carries the noise law and the baseline only: a slow
baseline structure at the wing's level is NOT in it, and the asymmetry column
and the pooled chi-squared are where it shows.

POOLING. The per-condition work is independent, so it runs under
`RB5S6S_WORKERS` workers (rb5s6s.workers.n_workers), the tasks submitted in
a fixed order and collected in that order. There is no random number in this
producer, so per-task seeding is moot and the CSV is byte-identical at every
worker count. The CSV is written once, at the end, only when every task
returned, so a failure anywhere leaves the committed file untouched.

STATUS. Every row is DIAGNOSTIC: the record's own traces read on a channel
the committed fits do not use, against the record's own widths.
"""
import csv
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from _producer_lock import take_producer_lock                      # noqa: E402
from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path    # noqa: E402
from rb5s6s.linefit import (_shared_profile_grid, adaptive_halfwidth,  # noqa: E402
                            to_frequency, transit_fwhm_at_T)
from rb5s6s.lineshape import lorentzian                            # noqa: E402
from rb5s6s.noise import load_noise_model, sigma_of_v, signal_level  # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402
from rb5s6s.workers import n_workers                               # noqa: E402

GNAT = K.GAMMA_NAT_HZ / 1e6
WING_LO_MHZ = 15.0
WING_HI_MHZ = 40.0
PEAKS = ("4121", "4154", "4192", "4207")
LAWS = ("Steck", "AIH", "SMI")
P_BLANK_MW = 225.0        # the manifest's blank power on the t_sweep is the maximum power
CENTRE_SCAN_MHZ = 1.5     # half-span of the centre scan about the QC seed
CENTRE_STEP_MHZ = 0.05
UNIT = "1e-3 of peak"     # the level's natural decade, so the cells stay in the plain band


def _read(name):
    with (_CFG.RESULTS_DIR / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def conditions():
    """The committed per-condition fits keyed (role, peak, T, P), P as a float."""
    out = {}
    for r in _read("linefit_conditions.csv"):
        if not r.get("T"):
            continue
        P = float(r["P"]) if r.get("P") else P_BLANK_MW
        out[(r["role"], r["peak"], float(r["T"]), P)] = {
            "rate": float(r["rate_t"]), "gamma_coll": float(r["gamma_coll"]),
            "gamma_coll_err": float(r["gamma_coll_err"]),
            "sigma_laser": float(r["sigma_laser"]),
            "sigma_laser_err": float(r["sigma_laser_err"])}
    return out


def canonical_traces():
    """Canonical RF-off manifest rows of the two sweeps, keyed like conditions()."""
    out = {}
    for r in load_manifest():
        if r["flag"] != "canonical" or r["rf_on"] != "False" or r["role"] not in ("p_sweep", "t_sweep"):
            continue
        P = float(r["power_mW"]) if r["power_mW"] else P_BLANK_MW
        out.setdefault((r["role"], r["peak"], float(r["temperature_C"]), P), []).append(r)
    for v in out.values():
        v.sort(key=lambda r: int(r["repeat_idx"]))
    return out


def qc_peak_positions():
    return {r["file"]: float(r["peak_pos_ms"]) for r in _read("qc_metrics.csv")}


def density_by_law():
    """N(T) in 1e12 cm^-3 per law, from the committed density file."""
    out = {law: {} for law in LAWS}
    for r in _read("density_laws.csv"):
        q = r["quantity"]
        if q.startswith("N_") and q[2:] in LAWS and r["key"].startswith("T"):
            out[q[2:]][float(r["key"][1:])] = float(r["value"]) / 1e12
    return out


def wing_mask(d, side):
    """Samples on one side (-1 red, +1 blue) or both (0) of the far window."""
    a = np.abs(d)
    inside = (a >= WING_LO_MHZ) & (a <= WING_HI_MHZ)
    if side == 0:
        return inside
    return inside & (np.sign(d) == side)


TRACE_STEP_MHZ = 0.0425   # the traces' own sample step on the transition axis
MODEL_D = np.arange(-1000, 1000) * TRACE_STEP_MHZ


def model_level(g, prof, side=0):
    """The far-wing level of an area-normalised profile relative to its peak,
    read on the traces' own sample step. The window's edge falls a fraction
    of a step differently on a different grid, and a sample at 15 MHz carries
    four times the window's mean, so a level read on the profile's internal
    grid differs from one read on the trace's by a few parts in a thousand:
    the model is resampled so the comparison carries none of that."""
    y = np.interp(MODEL_D, g, prof, left=0.0, right=0.0)
    m = wing_mask(MODEL_D, side)
    return float(np.mean(y[m]) / prof.max())


def solve_trace(nu, v, law, tau, g, prof, c_seed):
    """Re-solve the committed fit's per-trace nuisances at the committed shape.

    Returns the centre, (A, b0, b1), their covariance, the unwhitened sigma
    per sample and the profile's maximum. The window is the fit's own
    adaptive half-width about the seed, as `linefit.fit_condition` takes it.
    """
    lev, _base = signal_level(v)
    sig = sigma_of_v(np.maximum(lev, 0.0), law)
    hw = min(adaptive_halfwidth(nu, v), _CFG.FIT_HALFWIDTH_MAX_MHZ)
    m = np.abs(nu - c_seed) <= hw
    nu_w, v_w, w = nu[m], v[m], 1.0 / (sig[m] * np.sqrt(tau))

    def solve(c):
        X = np.column_stack([np.interp(nu_w - c, g, prof, left=0.0, right=0.0),
                             np.ones_like(nu_w), nu_w])
        Xw, yw = X * w[:, None], v_w * w
        beta, *_ = np.linalg.lstsq(Xw, yw, rcond=None)
        chi2 = float(np.sum((yw - Xw @ beta) ** 2))
        return beta, chi2, Xw

    cs = c_seed + np.arange(-CENTRE_SCAN_MHZ, CENTRE_SCAN_MHZ + 0.5 * CENTRE_STEP_MHZ, CENTRE_STEP_MHZ)
    chi = np.array([solve(c)[1] for c in cs])
    i = int(np.argmin(chi))
    c = cs[i]
    if 0 < i < cs.size - 1:
        y0, y1, y2 = chi[i - 1], chi[i], chi[i + 1]
        den = y0 - 2.0 * y1 + y2
        if den > 0:
            c = cs[i] + 0.5 * CENTRE_STEP_MHZ * (y0 - y2) / den
    beta, chi2, Xw = solve(c)
    cov = np.linalg.inv(Xw.T @ Xw)
    # chi2 on the UNSCALED sigma, as `linefit.fit_condition` reports it: the
    # whitening by tau sits in the weights, so the raw figure is tau times the
    # whitened one
    return float(c), beta, cov, sig, tau * chi2 / max(nu_w.size - 3, 1)


def wing_level(nu, v, sig, tau, c, beta, cov, pmax, side):
    """(level, variance, n) over one side or both, relative to the fitted peak."""
    d = nu - c
    m = wing_mask(d, side)
    n = int(m.sum())
    if n == 0:
        return float("nan"), float("nan"), 0
    A, b0, b1 = beta
    height = A * pmax
    resid = v[m] - b0 - b1 * nu[m]
    level = float(np.mean(resid) / height)
    var_noise = float(np.sum(sig[m] ** 2)) / n ** 2 * tau
    J = np.array([-level / A, -1.0 / height, -float(np.mean(nu[m])) / height])
    var_base = float(J @ cov @ J)
    return level, var_noise + var_base, n


def gamma_hom_table(gc, sl, transit):
    """The composite's far-wing level as a function of its homogeneous width,
    the laser and transit kernels held at the committed values. Monotone, so
    it inverts by interpolation. Returned in the level's decade (1e-3)."""
    # the table starts AT the natural width: the profile builder clamps a
    # negative collisional width at zero, so below gamma_nat the level is
    # flat and the inversion would be undefined there
    hom = GNAT + np.arange(0.0, 12.51, 0.25)
    lev = []
    for h in hom:
        g, prof = _shared_profile_grid(h - GNAT, sl, transit, 0.0, "gaussian", 0.0)
        lev.append(1e3 * model_level(g, prof))
    lev = np.array(lev)
    if not np.all(np.diff(lev) > 0):
        raise SystemExit("run_far_wing_level: the far-wing level is not monotone in the "
                         "homogeneous width, so it cannot be inverted. refuse rather than publish")
    return hom, lev


def invert_gamma_hom(level, err, table):
    hom, lev = table
    if not (lev[0] <= level <= lev[-1]):
        return float("nan"), float("nan")
    h = float(np.interp(level, lev, hom))
    slope = float(np.interp(level, lev, np.gradient(lev, hom)))
    return h, err / slope


def condition_task(key, fit, recs, seeds):
    """Everything one condition needs, in one worker."""
    role, peak, T, P = key
    law = load_noise_model(_CFG.RESULTS_DIR / "noise_model.csv", role=role, peak=peak,
                           temperature_C=T, power_mW=(P if role == "p_sweep" else None))
    tau = max(law.get("tau_eff", law["tau_int"]), 1.0)   # F36
    transit = transit_fwhm_at_T(T, _CFG.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    g, prof = _shared_profile_grid(fit["gamma_coll"], fit["sigma_laser"], transit, 0.0, "gaussian", 0.0)
    pmax = float(prof.max())
    levels, variances, asym, asym_var, refused, chi2s = [], [], [], [], 0, []
    span_ok = 0
    for r in recs:
        t, v = load_trace(trace_path(r))
        nu = to_frequency(t, fit["rate"])
        c, beta, cov, sig, chi2_red = solve_trace(nu, v, law, tau, g, prof, seeds[r["file"]] * fit["rate"])
        d = nu - c
        if d.min() > -WING_HI_MHZ or d.max() < WING_HI_MHZ:
            refused += 1
            continue
        span_ok += 1
        lv, var, _n = wing_level(nu, v, sig, tau, c, beta, cov, pmax, 0)
        lb, vb, _ = wing_level(nu, v, sig, tau, c, beta, cov, pmax, +1)
        lr, vr, _ = wing_level(nu, v, sig, tau, c, beta, cov, pmax, -1)
        levels.append(lv)
        variances.append(var)
        asym.append(lb - lr)
        asym_var.append(vb + vr)
        chi2s.append(chi2_red)
    out = {"key": key, "n": span_ok, "refused": refused, "tau": tau,
           "pred_composite": 1e3 * model_level(g, prof),
           "pred_lorentz": 1e3 * model_level(g, lorentzian(g, GNAT + fit["gamma_coll"])),
           "gamma_hom_committed": GNAT + fit["gamma_coll"],
           "core_chi2_red": float(np.mean(chi2s)) if chi2s else float("nan")}
    if not levels:
        out.update(level=float("nan"), err=float("nan"), scatter=float("nan"), chi2=float("nan"),
                   asym=float("nan"), asym_err=float("nan"), gamma_hom=float("nan"), gamma_hom_err=float("nan"))
        return out
    lv = 1e3 * np.array(levels)
    var = 1e6 * np.array(variances)
    wgt = 1.0 / var
    mean = float(np.sum(wgt * lv) / np.sum(wgt))
    err = float(1.0 / np.sqrt(np.sum(wgt)))
    chi2 = float(np.sum(wgt * (lv - mean) ** 2))
    scatter = float(np.std(lv, ddof=1) / np.sqrt(lv.size)) if lv.size > 1 else float("nan")
    av = 1e3 * np.array(asym)
    avv = 1e6 * np.array(asym_var)
    aw = 1.0 / avv
    a_mean = float(np.sum(aw * av) / np.sum(aw))
    a_err = float(1.0 / np.sqrt(np.sum(aw)))
    table = gamma_hom_table(fit["gamma_coll"], fit["sigma_laser"], transit)
    gh, gh_err = invert_gamma_hom(mean, err, table)
    out.update(level=mean, err=err, scatter=scatter, chi2=chi2, asym=a_mean, asym_err=a_err,
               gamma_hom=gh, gamma_hom_err=gh_err)
    return out


def _run_task(args):
    return condition_task(*args)


def weighted_line(x, y, e):
    """Weighted least squares of y = a + b x. Returns (a, b, ea, eb, chi2, dof)."""
    x, y, e = (np.asarray(v, float) for v in (x, y, e))
    w = 1.0 / e ** 2
    X = np.column_stack([np.ones_like(x), x])
    Xw = X * np.sqrt(w)[:, None]
    cov = np.linalg.inv(Xw.T @ Xw)
    beta = cov @ (Xw.T @ (y * np.sqrt(w)))
    chi2 = float(np.sum(w * (y - X @ beta) ** 2))
    return float(beta[0]), float(beta[1]), float(np.sqrt(cov[0, 0])), float(np.sqrt(cov[1, 1])), chi2, x.size - 2


def shared_slope_line(groups):
    """One slope shared across groups, an intercept per group. groups: list of
    (x, y, e) arrays. Returns (slope, slope_err, intercepts, chi2, dof)."""
    xs, ys, es, idx = [], [], [], []
    for gi, (x, y, e) in enumerate(groups):
        xs += list(x)
        ys += list(y)
        es += list(e)
        idx += [gi] * len(x)
    x, y, e, idx = np.array(xs), np.array(ys), np.array(es), np.array(idx)
    ng = len(groups)
    X = np.zeros((x.size, ng + 1))
    X[np.arange(x.size), idx] = 1.0
    X[:, ng] = x
    w = np.sqrt(1.0 / e ** 2)
    Xw = X * w[:, None]
    cov = np.linalg.inv(Xw.T @ Xw)
    beta = cov @ (Xw.T @ (y * w))
    chi2 = float(np.sum((w * (y - X @ beta)) ** 2))
    return float(beta[ng]), float(np.sqrt(cov[ng, ng])), beta[:ng], chi2, x.size - ng - 1


def key_label(key):
    role, peak, T, P = key
    return f"{peak}_T{T:g}_P{P:g}"


def main() -> int:
    take_producer_lock("far_wing_level")
    fits = conditions()
    traces = canonical_traces()
    seeds = qc_peak_positions()
    keys = sorted(k for k in fits if k in traces)
    missing = sorted(set(traces) - set(fits))
    if missing:
        raise SystemExit(f"run_far_wing_level: conditions with traces and no committed fit: {missing}")
    tasks = [(k, fits[k], traces[k], {r["file"]: seeds[r["file"]] for r in traces[k]}) for k in keys]
    nw = n_workers()
    if nw > 0:
        with ProcessPoolExecutor(max_workers=nw) as pool:
            futures = [pool.submit(_run_task, t) for t in tasks]
            results = [f.result() for f in futures]        # collected in submission order
    else:
        results = [_run_task(t) for t in tasks]
    by_key = {r["key"]: r for r in results}

    out = [["quantity", "key", "value", "err", "unit", "note", "status"]]
    out.append(["window", "definition", f"{WING_LO_MHZ:g} to {WING_HI_MHZ:g}", "", "MHz from the centre",
                "both sides together, relative to the fitted peak height (amplitude times the committed profile's maximum), the per-trace linear baseline of the committed fit removed. the per-trace centre, amplitude, offset and slope are NOT in the committed fit file and were re-solved at the committed shape (centre from the committed QC peak position, one scan with a parabolic step, then a weighted linear solve). the bar is the noise law a^2 + bV over the window's samples times tau_int, plus the baseline's extrapolation error from the linear solve's covariance", "DIAGNOSTIC"])
    for k in keys:
        r = by_key[k]
        lab = key_label(k)
        v, e = pm_cells(r["level"], r["err"])
        pull = (r["level"] - r["pred_composite"]) / r["err"] if np.isfinite(r["err"]) else float("nan")
        out.append(["far_wing_level", lab, v, e, UNIT,
                    f"{r['n']} traces pooled by inverse variance, {r['refused']} refused for a window past the trace. block scatter over the repeats {r['scatter']:.3f}, chi2 of the pool {r['chi2']:.1f} for {max(r['n'] - 1, 0)} dof, tau_int {r['tau']:.2f}. the committed composite predicts {r['pred_composite']:.3f} and a bare Lorentzian of gamma_nat + gamma_coll predicts {r['pred_lorentz']:.3f}. pull against the composite {pull:+.1f}. core chi2_red of the re-solved nuisances {r['core_chi2_red']:.2f}",
                    "DIAGNOSTIC"])
        va, ea = pm_cells(r["asym"], r["asym_err"])
        out.append(["far_wing_asymmetry", lab, va, ea, UNIT,
                    "blue side minus red side of the same window. a symmetric line gives zero, so a value beyond its bar is the baseline's structure or a tilt the linear baseline did not take, and the level row above inherits it", "DIAGNOSTIC"])
        out.append(["far_wing_pred_composite", lab, f"{r['pred_composite']:.4f}", "", UNIT,
                    f"the committed composite (gamma_coll {fits[k]['gamma_coll']:.4f}, sigma_laser {fits[k]['sigma_laser']:.4f} MHz, transit at the adopted waist, no shift) over the same window", "DIAGNOSTIC"])
        out.append(["far_wing_pred_lorentzian", lab, f"{r['pred_lorentz']:.4f}", "", UNIT,
                    f"a bare Lorentzian of FWHM gamma_nat + gamma_coll = {r['gamma_hom_committed']:.4f} MHz over the same window: what the far wing is when the Gaussian and the cusp are gone", "DIAGNOSTIC"])
        if np.isfinite(r["gamma_hom"]):
            vg, eg = pm_cells(r["gamma_hom"], r["gamma_hom_err"])
            vx, ex = pm_cells(r["gamma_hom"] - r["gamma_hom_committed"], r["gamma_hom_err"])
            why = ""
        else:
            vg = eg = vx = ex = ""
            why = " NOT INVERTED: the measured level sits outside the table, below what the natural width alone gives or above its top, so no homogeneous width reproduces it."
        out.append(["far_wing_gamma_hom", lab, vg, eg, "MHz",
                    f"the homogeneous FWHM the measured level implies when the composite's Lorentzian alone moves, the laser and transit kernels held at the committed values. the committed gamma_nat + gamma_coll is {r['gamma_hom_committed']:.4f}.{why}", "DIAGNOSTIC"])
        out.append(["far_wing_gamma_excess", lab, vx, ex, "MHz",
                    "far_wing_gamma_hom minus the committed gamma_nat + gamma_coll: the Lorentzian width the far wing wants beyond the core fit, which is the far wing's reading of gamma_l at this condition", "DIAGNOSTIC"])

    # the temperature arm at the maximum power: the three t_sweep points and the corner
    dens = density_by_law()
    arm = {}
    for k in keys:
        role, peak, T, P = k
        if P != P_BLANK_MW:
            continue
        if role == "t_sweep" or (role == "p_sweep" and T == 130.0):
            arm.setdefault(peak, {})[T] = by_key[k]
    for law in LAWS:
        groups_level, groups_gamma = [], []
        for peak in PEAKS:
            cells = arm.get(peak, {})
            Ts = sorted(cells)
            if len(Ts) < 3:
                continue
            Ts_l = [T for T in Ts if np.isfinite(cells[T]["level"]) and np.isfinite(cells[T]["err"])]
            Ts_g = [T for T in Ts if np.isfinite(cells[T]["gamma_hom"]) and np.isfinite(cells[T]["gamma_hom_err"])]
            if len(Ts_l) < 3 or len(Ts_g) < 3:
                out.append(["far_wing_level_slope", f"{law}_{peak}", "", "", f"{UNIT} per 1e12 cm^-3",
                            f"not fitted: {len(Ts_l)} level cells and {len(Ts_g)} invertible cells, three needed", "DIAGNOSTIC"])
                continue
            N = [dens[law][T] for T in Ts_l]
            lv = [cells[T]["level"] for T in Ts_l]
            le = [cells[T]["err"] for T in Ts_l]
            groups_level.append((N, lv, le))
            a, b, ea, eb, chi2, dof = weighted_line(N, lv, le)
            vb, ebb = pm_cells(b, eb)
            va, eaa = pm_cells(a, ea)
            tlist = "/".join(f"{T:g}" for T in Ts_l)
            out.append(["far_wing_level_slope", f"{law}_{peak}", vb, ebb, f"{UNIT} per 1e12 cm^-3",
                        f"the level against N(T) under the {law} law at 225 mW, temperatures {tlist} C. chi2 {chi2:.1f} for {dof} dof", "DIAGNOSTIC"])
            out.append(["far_wing_level_intercept", f"{law}_{peak}", va, eaa, UNIT,
                        f"the same line's density-free level under the {law} law", "DIAGNOSTIC"])
            N = [dens[law][T] for T in Ts_g]
            gh = [cells[T]["gamma_hom"] for T in Ts_g]
            ge = [cells[T]["gamma_hom_err"] for T in Ts_g]
            groups_gamma.append((N, gh, ge))
            tlist = "/".join(f"{T:g}" for T in Ts_g)
            a, b, ea, eb, chi2, dof = weighted_line(N, gh, ge)
            vb, ebb = pm_cells(b, eb)
            va, eaa = pm_cells(a, ea)
            vf, ef = pm_cells(a - GNAT, ea)
            out.append(["far_wing_beta", f"{law}_{peak}", vb, ebb, "MHz per 1e12 cm^-3",
                        f"the far wing's homogeneous width against N(T) under the {law} law, temperatures {tlist} C: beta on the wing channel. chi2 {chi2:.1f} for {dof} dof", "DIAGNOSTIC"])
            out.append(["far_wing_gamma0", f"{law}_{peak}", va, eaa, "MHz",
                        f"the same line's density-free homogeneous width under the {law} law", "DIAGNOSTIC"])
            out.append(["far_wing_floor", f"{law}_{peak}", vf, ef, "MHz",
                        f"far_wing_gamma0 minus gamma_nat ({GNAT:.4f} MHz): the Lorentzian floor the far wing reads, which is gamma_l's meter", "DIAGNOSTIC"])
        if len(groups_gamma) < 2:
            continue
        for name, groups, unit_slope, unit_int in (("level", groups_level, f"{UNIT} per 1e12 cm^-3", UNIT),
                                                   ("gamma", groups_gamma, "MHz per 1e12 cm^-3", "MHz")):
            b, eb, ints, chi2, dof = shared_slope_line(groups)
            vb, ebb = pm_cells(b, eb)
            qn = "far_wing_level_slope" if name == "level" else "far_wing_beta"
            out.append([qn, f"{law}_pooled", vb, ebb, unit_slope,
                        f"one slope shared across the {len(groups)} peaks with an intercept per peak, {law} law. chi2 {chi2:.1f} for {dof} dof. per-peak intercepts " + ", ".join(f"{x:.4f}" for x in ints), "DIAGNOSTIC"])
            x = np.concatenate([g[0] for g in groups])
            y = np.concatenate([g[1] for g in groups])
            e = np.concatenate([g[2] for g in groups])
            a, b, ea, eb, chi2, dof = weighted_line(x, y, e)
            vb, ebb = pm_cells(b, eb)
            va, eaa = pm_cells(a, ea)
            out.append([qn, f"{law}_pooled_shared", vb, ebb, unit_slope,
                        f"one slope and one intercept across every peak and temperature, {law} law. chi2 {chi2:.1f} for {dof} dof", "DIAGNOSTIC"])
            qi = "far_wing_level_intercept" if name == "level" else "far_wing_gamma0"
            out.append([qi, f"{law}_pooled_shared", va, eaa, unit_int,
                        f"the fully shared line's intercept, {law} law", "DIAGNOSTIC"])
            if name == "gamma":
                vf, ef = pm_cells(a - GNAT, ea)
                out.append(["far_wing_floor", f"{law}_pooled_shared", vf, ef, "MHz",
                            "the fully shared line's intercept minus gamma_nat: the pooled Lorentzian floor on the wing channel", "DIAGNOSTIC"])
    n_tr = sum(r["n"] for r in results)
    n_ref = sum(r["refused"] for r in results)
    out.append(["traces", "used", str(n_tr), "", "", f"canonical RF-off traces whose window sat inside the trace on both sides. {n_ref} refused", "DIAGNOSTIC"])
    out_path = _CFG.RESULTS_DIR / "far_wing_level.csv"
    tmp = out_path.with_name(out_path.name + ".writing")
    with tmp.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(out)
    tmp.replace(out_path)
    print(f"wrote {out_path} ({len(out) - 1} rows, {n_tr} traces, {n_ref} refused, workers {nw})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
