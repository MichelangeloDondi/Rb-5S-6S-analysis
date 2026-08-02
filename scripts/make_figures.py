#!/usr/bin/env python3
"""
Publication figures from the committed results/ CSVs (paper draft).

Design choices (per the dataviz method, adapted to matplotlib science figures):
- the four peaks use a FIXED Okabe-Ito colorblind-safe order everywhere, so a
  colour means the same peak across every panel;
- one y-axis per panel (never dual-axis); recessive grid; error bars shown;
  legends present, units on every axis;
- every figure states in its title/annotation what is PRELIMINARY (w0-limited)
  vs robust, matching README section 5.

Writes PNGs to figures/. Run after the pipeline (reads results/*.csv).
"""

from __future__ import annotations

import csv
import datetime as dt_module
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import density_units  # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ, TRACE_N_POINTS, TRACE_DT_S  # noqa: E402

GNAT = GAMMA_NAT_HZ / 1e6
FIG = C.REPO_ROOT / "figures"
FIG.mkdir(exist_ok=True)
# Fingerprint of the results/ CSVs these figures are drawn from, stamped into
# each PNG's metadata so a stale figure (results changed, figure not redrawn)
# is caught by tests/test_figures_fresh.py without a fragile pixel compare.
_DATA_FP = C.results_fingerprint()


def _save(fig, name):
    """tight_layout + savefig with the data fingerprint embedded, then close."""
    fig.tight_layout()
    fig.savefig(FIG / name, metadata={"DataFingerprint": _DATA_FP})
    plt.close(fig)


# Okabe-Ito (colorblind-safe), fixed order for the four peaks
PEAK_COLOR = {"4121": "#0072B2", "4154": "#D55E00", "4192": "#009E73", "4207": "#E69F00"}
_ISO = {"4121": "$^{87}$Rb F1", "4154": "$^{85}$Rb F2",
        "4192": "$^{85}$Rb F3", "4207": "$^{87}$Rb F2"}
PEAK_LABEL = {k: f"993.{k} nm ({_ISO[k]})" for k in PEAK_COLOR}
plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True,
                     "grid.alpha": 0.25, "axes.axisbelow": True, "legend.frameon": False})


# Windows with fewer contributing traces than this cannot test the linearity
# bound -- their errors exceed it. Split point for fig8's right panel.
N_WELL_SAMPLED = 19


def _rows(name):
    return list(csv.DictReader(open(C.RESULTS_DIR / f"{name}.csv")))


def fig_width_vs_density():
    """C1: total line FWHM vs density per peak -- the non-monotonicity that
    makes beta_self a bound, not a measurement."""
    rows = _rows("linefit_conditions")
    fig, ax = plt.subplots(figsize=(6, 4.2))
    for peak in ("4121", "4154", "4192", "4207"):
        pts = []
        for r in rows:
            if r["peak"] != peak:
                continue
            T = 130.0 if r["role"] == "p_sweep" and r["P"] == "225" else (
                float(r["T"]) if r["role"] == "t_sweep" else None)
            if T is None or (r["role"] == "p_sweep" and r["P"] != "225"):
                continue
            pts.append((density_units(T), float(r["total_fwhm"]), float(r["total_fwhm_err"])))
        if not pts:
            continue
        pts.sort()
        N, W, We = zip(*pts)
        ax.errorbar(N, W, yerr=We, fmt="-o", color=PEAK_COLOR[peak], label=PEAK_LABEL[peak],
                    ms=5, lw=1.5, capsize=2)
    ax.axhline(GNAT, ls=":", color="0.4", lw=1)
    ax.annotate("natural width", (ax.get_xlim()[1], GNAT), va="bottom", ha="right",
                color="0.4", fontsize=8)
    ax.set_xscale("log")
    ax.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$, log)")
    ax.set_ylabel("total line FWHM  (MHz, transition axis)")
    ax.set_title("C1: width vs density — non-monotonic ⇒ $\\beta_\\mathrm{self}$ is bounded\n"
                 "(collisions must be monotonic; the wiggles are between-block laser drift)",
                 fontsize=9)
    ax.legend(fontsize=8, ncol=2)
    _save(fig, "fig1_width_vs_density.png")


def fig_power_sweep():
    """C3: FWHM shows no power trend; amplitude ~ P^2.

    The observed FWHM spread (3-8%) EXCEEDS the <=2% the ramp law predicts,
    so the title must not present the prediction as the observation -- it is
    between-block scatter, and no peak keeps a significant slope once that
    over-dispersion is absorbed (worst 1.7 sigma). Titling this "flat" read
    as a claim the plotted points do not support."""
    rows = _rows("power_sweep")
    by = defaultdict(list)
    for r in rows:
        by[r["peak"]].append((int(r["power_mW"]), float(r["fwhm"]), float(r["fwhm_err"]),
                              float(r["amp"]), float(r["amp_err"])))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 4.2))
    for peak in ("4121", "4154", "4192", "4207"):
        d = sorted(by[peak]); P = [x[0] for x in d]
        a1.errorbar(P, [x[1] for x in d], yerr=[x[2] for x in d], fmt="-o",
                    color=PEAK_COLOR[peak], label=PEAK_LABEL[peak], ms=4, lw=1.3, capsize=2)
        a2.errorbar(P, [x[3] for x in d], yerr=[x[4] for x in d], fmt="o",
                    color=PEAK_COLOR[peak], ms=4, capsize=2)
    a1.set_xlabel("power (mW)"); a1.set_ylabel("FWHM (MHz, transition)")
    a1.set_title("C3a: no power trend in the linewidth\n"
              "(observed 3–8% scatter; ramp predicts $\\leq$2%)", fontsize=9)
    a1.legend(fontsize=8)
    # amplitude log-log: a slope-2 (P^2) fit anchored to each peak's own data, so
    # the guide tracks the points instead of floating beside them
    a2.set_xscale("log"); a2.set_yscale("log")
    Pline = np.array([22.0, 250.0])
    for i, peak in enumerate(("4121", "4154", "4192", "4207")):
        d = sorted(by[peak])
        P = np.array([x[0] for x in d], float)
        A = np.array([x[3] for x in d], float)
        logk = np.mean(np.log10(A) - 2.0 * np.log10(P))  # least-squares slope-2 intercept
        a2.plot(Pline, 10 ** logk * Pline ** 2, "--", color=PEAK_COLOR[peak], lw=1.0,
                label=r"$\propto P^2$ fit" if i == 0 else None)
    a2.set_xlabel("power (mW)"); a2.set_ylabel("peak amplitude (V)")
    a2.set_title("C3b: amplitude $\\propto P^2$\n(two-photon rate law)", fontsize=9)
    a2.legend(fontsize=8)
    _save(fig, "fig2_power_sweep.png")


def fig_transit_mc():
    """M9: transit contribution vs w0 with the laser-narrow crossover."""
    rows = [r for r in _rows("transit_mc") if r["collection"] == "thin"]
    w0 = [float(r["w0_um"]) for r in rows]
    natx = [float(r["nat_conv_transit"]) for r in rows]
    natx_err = [float(r["nat_conv_transit_err"]) for r in rows]
    fig, ax = plt.subplots(figsize=(6, 4.2))
    ax.errorbar(w0, natx, yerr=natx_err, fmt="-o", color="#0072B2", ms=5, lw=1.6,
                capsize=2, label="natural ⊗ transit (MC)")
    ax.axhline(5.25, ls="--", color="#D55E00", lw=1.3, label="observed total ~5.2 MHz")
    ax.axhline(GNAT, ls=":", color="0.4", lw=1, label="natural alone")
    # shade the laser-narrow region (where nat⊗transit >= observed)
    ax.fill_between([min(w0), 20], GNAT, 6.0, color="#009E73", alpha=0.10)
    ax.annotate("laser NARROW\n(transit fills budget)", (16.5, 5.5), fontsize=8, color="#009E73")
    ax.annotate("laser ~1 MHz", (36, 4.2), fontsize=8, color="0.3")
    ax.set_xlabel(r"beam waist $w_0$ ($\mu$m)  — OPEN until knife-edge measurement")
    ax.set_ylabel("FWHM (MHz, transition)")
    ax.set_title("M9: transit ⊗ natural vs $w_0$ — the transit/laser degeneracy\n"
                 "crossover near $w_0\\approx18$–$20\\,\\mu$m sets narrow-vs-not", fontsize=9)
    ax.legend(fontsize=8, loc="center right")
    _save(fig, "fig3_transit_mc.png")


def fig_amplitude_ratios():
    """M10: within-isotope area ratios vs the parameter-free degeneracy law."""
    rows = _rows("amplitude_ratios")
    fig, ax = plt.subplots(figsize=(6, 4.2))
    styles = {"4207/4121": ("#E69F00", 5 / 3, "993.4207 / 993.4121 nm ($^{87}$Rb)"),
              "4192/4154": ("#009E73", 7 / 5, "993.4192 / 993.4154 nm ($^{85}$Rb)")}
    for key, (col, pred, lab) in styles.items():
        # err_total = stat (SEM) + between-block drift systematic, in quadrature
        # (the total bar; the stat-only column is a labelled diagnostic). See
        # run_amplitude_ratios.py and review finding 5, 2026-07-16.
        d = [(float(r["T"]), float(r["measured"]), float(r["err_total"]))
             for r in rows if r["ratio"] == key]
        d.sort()
        if not d:
            continue
        T, m, e = zip(*d)
        ax.errorbar(T, m, yerr=e, fmt="-o", color=col, ms=5, lw=1.3, capsize=2, label=lab)
        ax.axhline(pred, ls="--", color=col, lw=1)
    ax.annotate("predicted 5/3", (128, 5 / 3 + 0.03), fontsize=8, color="#E69F00", ha="right")
    ax.annotate("predicted 7/5", (128, 7 / 5 - 0.10), fontsize=8, color="#009E73", ha="right")
    ax.set_xlabel("temperature (°C)")
    ax.set_ylabel("area ratio")
    ax.set_title("M10: area ratios vs the scalar-operator degeneracy law\n"
                 "1–3% within-block, but 30–50% between-block drift ⇒ archive can't test it",
                 fontsize=9)
    ax.legend(fontsize=8)
    _save(fig, "fig4_amplitude_ratios.png")


def fig_pooled_width():
    """fig5: the four ΔF=0 components share ONE
    width budget — β_85 = β_87 was TESTED equal in the joint fit, which is what
    LICENSES pooling (equality tested first, then pool; not the reverse). So the
    pooled width vs density is a clean trend where the individual components are
    statistics-limited and non-monotonic. Companion panel: the shared σ_laser(T)
    is NOT flat — the residual drift systematic, shown not hidden. This is
    PRECISION not accuracy: still a BOUND, because the common-mode time-drift
    survives pooling (only the fixed-lock session's opposite-order grid decontaminates)."""
    rows = _rows("linefit_conditions")

    def width(peak, T):
        role = "p_sweep" if T == 130 else "t_sweep"
        for r in rows:
            if (r["peak"] == peak and r["role"] == role and int(float(r["T"])) == T
                    and (r["P"] == "225" or role == "t_sweep")):
                return float(r["total_fwhm"])
        return None

    Ts = (70, 90, 110, 130)
    peaks = ("4121", "4154", "4192", "4207")
    N = [density_units(float(T)) for T in Ts]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.8, 4.3))
    # panel A: individual components (faint) + pooled mean (bold) vs density
    for peak in peaks:
        w = [width(peak, T) for T in Ts]
        a1.plot(N, w, "-o", color=PEAK_COLOR[peak], alpha=0.30, ms=3, lw=0.9)
    pooled = [np.mean([width(p, T) for p in peaks]) for T in Ts]
    perr = [np.std([width(p, T) for p in peaks], ddof=1) / 2.0 for T in Ts]
    a1.errorbar(N, pooled, yerr=perr, fmt="-o", color="k", ms=6, lw=2.0, capsize=3,
                label="pooled: 4-peak mean ± scatter/√4", zorder=5)
    # split-independent lever check (M4d): if the short-lever joint beta were a
    # real linear collision rate, the TOTAL width must grow by at least
    # 0.5346*beta*dN (minimum Voigt slope dW/dgamma_L >= 0.5346, sigma_laser
    # held flat -- and the measured widths already include some laser-width
    # growth, so the comparison is conservative). The pooled growth falls
    # short at the 130 C point -> beta is a lever-dependent BOUND.
    dfp = C.RESULTS_DIR / "lever_crosscheck.csv"
    if dfp.exists():
        dfr = list(csv.DictReader(open(dfp)))
        bhead = np.mean([float(r["value"]) for r in dfr
                         if r["quantity"] == "beta_crosscheck"])
        Nf = np.geomspace(N[0], N[-1], 200)
        a1.plot(Nf, pooled[0] + 0.5346 * bhead * (Nf - N[0]), "--", color="0.35",
                lw=1.4, label=(r"min. growth if $\beta$=%.3f were linear"
                               r" (Voigt slope $\geq$0.53)") % bhead)
    a1.set_xscale("log")
    a1.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$, log)")
    a1.set_ylabel("total line FWHM (MHz, transition)")
    a1.set_title("Pooled width vs density: individuals (faint) are\n"
                 "statistics-limited & non-monotonic; the pooled mean\n"
                 "rises cleanly (β₈₅, β₈₇ agree within ~1σ — consistent, not\n"
                 "discriminating) — still a BOUND",
                 fontsize=8)
    a1.legend(fontsize=8, loc="upper left")
    # panel B: σ_laser(T) is MODEL-DEPENDENT -> the "anomaly" is degeneracy, not drift
    gf = _rows("global_fit")
    sl = sorted((float(r["key"][:-1]), float(r["value"]), float(r["err"]))
                for r in gf if r["quantity"] == "sigma_laser")
    a2.errorbar([x[0] for x in sl], [x[1] for x in sl], yerr=[x[2] for x in sl],
                fmt="-o", color="#D55E00", ms=6, lw=1.6, capsize=3,
                label=r"global fit ($\beta\cdot N$-tied)")
    freeT, freeS = [], []
    for T in (70, 90, 110):
        v = [(float(r["sigma_laser"]), float(r["sigma_laser_err"])) for r in rows
             if r["role"] == "t_sweep" and int(float(r["T"])) == T]
        s = np.array([x[0] for x in v]); w = 1.0 / np.array([x[1] for x in v]) ** 2
        freeT.append(T); freeS.append(float(np.sum(w * s) / np.sum(w)))
    a2.plot(freeT, freeS, "-s", color="#0072B2", ms=6, lw=1.6,
            label="free per-condition (4 peaks agree)")
    a2.set_xlabel("temperature (°C)")
    a2.set_ylabel(r"$\sigma_\mathrm{laser}$ (MHz, transition)")
    a2.set_title("σ_laser(T) is MODEL-DEPENDENT: the free fit is flat (~1.6,\n"
                 "4 peaks agree, χ²<1 ⇒ in-sample check only, M4c); the tied drop is\n"
                 "the β↔σ_laser degeneracy, not a physical laser drift", fontsize=8)
    a2.legend(fontsize=7.5)
    _save(fig, "fig5_pooled_width.png")


def fig_gamma_floor():
    """The lever test (M4d, 2026-07-12): the fitted collisional width is a
    near-flat FLOOR — it rises only ~x1.5 while the density rises x52 — so the
    joint-fit beta cannot be a real linear collision rate: extrapolating either
    joint value from the 70 C anchor overshoots the measured 130 C width. That
    lever-dependence is WHY beta is quoted as a BOUND. Per-condition split shown
    (sigma_laser free), which is degenerate (corr ~ -0.85) — but the same story
    holds split-independently in fig5 panel A (total width vs the minimum
    growth line). Betas are READ from results/lever_crosscheck.csv, not typed."""
    rows = _rows("linefit_conditions")

    def gam(peak, T):
        role = "p_sweep" if T == 130 else "t_sweep"
        for r in rows:
            if (r["peak"] == peak and r["role"] == role and int(float(r["T"])) == T
                    and (r["P"] == "225" or role == "t_sweep")):
                return float(r["gamma_coll"]), float(r["gamma_coll_err"])
        return None

    Ts = (70, 90, 110, 130)
    peaks = tuple(PEAK_COLOR)
    N = np.array([density_units(float(T)) for T in Ts])
    fig, ax = plt.subplots(figsize=(6.6, 4.8))
    for peak in peaks:
        gv = [gam(peak, T) for T in Ts]
        ax.errorbar(N, [g[0] for g in gv], yerr=[g[1] for g in gv], fmt="-o",
                    color=PEAK_COLOR[peak], alpha=0.30, ms=3, lw=0.9,
                    label=PEAK_LABEL[peak])
    mean_g = np.array([np.mean([gam(p, T)[0] for p in peaks]) for T in Ts])
    scat = np.array([np.std([gam(p, T)[0] for p in peaks], ddof=1) / 2.0 for T in Ts])
    ax.errorbar(N, mean_g, yerr=scat, fmt="-o", color="k", ms=6, lw=2.0, capsize=3,
                label="4-peak mean ± scatter/√4", zorder=5)
    # joint-fit betas (from the committed CSV), extrapolated from the 70 C mean:
    # a REAL linear collision rate would follow these lines; the data do not.
    dfp = C.RESULTS_DIR / "lever_crosscheck.csv"
    if dfp.exists():
        dfr = list(csv.DictReader(open(dfp)))
        bhead = np.mean([float(r["value"]) for r in dfr
                         if r["quantity"] == "beta_crosscheck"])
        blever = np.mean([float(r["value"]) for r in dfr
                          if r["quantity"] == "beta_lever_probe_130"])
        Nf = np.geomspace(N[0], N[-1], 200)
        ax.plot(Nf, mean_g[0] + bhead * (Nf - N[0]), "--", color="#D55E00", lw=1.6,
                label=r"if $\beta$=%.3f (joint, x16 lever) were linear" % bhead)
        ax.plot(Nf, mean_g[0] + blever * (Nf - N[0]), ":", color="#0072B2", lw=1.8,
                label=r"if $\beta$=%.3f (joint, x53 lever) were linear" % blever)
        yend = mean_g[0] + bhead * (N[-1] - N[0])
        ax.annotate(r"$\rightarrow$ %.1f MHz at 130 °C" % yend, xy=(N[-1], 1.08),
                    ha="right", fontsize=8, color="#D55E00")
    ax.set_xscale("log")
    ax.set_ylim(0.0, 1.15)
    ax.set_xlabel(r"Rb density $N$  ($10^{12}\,\mathrm{cm^{-3}}$, log)")
    ax.set_ylabel(r"fitted $\gamma_\mathrm{coll}$ (MHz, transition)")
    rise = mean_g[-1] / mean_g[0]
    lever = N[-1] / N[0]
    ax.set_title("The lever test: fitted collisional width is a near-flat FLOOR\n"
                 + (r"($\gamma$ rises x%.1f while $N$ rises x%.0f)" % (rise, lever))
                 + " — a real binary-collision\nwidth is linear in N ⇒ β is a "
                 "lever-dependent BOUND (per-condition split;\n"
                 "split-independent check in fig5A)", fontsize=8)
    ax.legend(fontsize=7, loc="upper left", ncol=2)
    _save(fig, "fig6_gamma_floor.png")


def fig_identifiability_profile():
    """The global profile-likelihood map behind M12 (methods §4.10): chi2
    minimised over transit + all per-trace nuisances at each (gamma_coll,
    sigma_laser) point, on the bright 993.4192 nm 130 C / 225 mW condition.
    LEFT: the wide map — the topology of the width degeneracy (log10 dchi2)
    with the joint-68/95% contours. RIGHT: the zoom about the minimum, profile
    contours against the LOCAL covariance ellipse (dashed): in the Gaussian
    limit the two coincide, so their agreement is the trust test for every
    covariance-based statement; the valley-floor points trace the degeneracy
    direction. All values read from results/identifiability_profile.csv."""
    fp = C.RESULTS_DIR / "identifiability_profile.csv"
    if not fp.exists():
        print("  (identifiability_profile.csv absent -- skipping fig7)")
        return
    rows = list(csv.DictReader(open(fp)))

    def axis(name):
        vals = {int(r["key"]): float(r["value"]) for r in rows if r["quantity"] == name}
        return np.array([vals[i] for i in sorted(vals)])

    def surf(name, nsl, ngc):
        Z = np.empty((nsl, ngc))
        for r in rows:
            if r["quantity"] == name:
                i, j = r["key"].split("|")
                Z[int(i), int(j)] = float(r["value"])
        return Z

    cov = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "cov"}
    fit = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "fit"}
    M = np.array([[cov["gc_gc"], cov["gc_sl"]], [cov["gc_sl"], cov["sl_sl"]]])
    from rb5s6s.identifiability import valley_floor

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 4.4))
    for k, (nm, ax) in enumerate(zip(("wide", "zoom"), axes)):
        gc = axis(f"{nm}_gc"); sl = axis(f"{nm}_sl")
        D = surf(f"{nm}_dchi2", len(sl), len(gc))
        T = surf(f"{nm}_transit", len(sl), len(gc))
        pc = ax.contourf(gc, sl, np.log10(np.maximum(D, 0.05)), levels=18,
                         cmap="viridis")
        ax.contour(gc, sl, D, levels=[2.30, 5.99], colors=["w", "w"],
                   linestyles=["-", "--"], linewidths=1.2)
        # the transit -> 0 wall: beyond it the profiled transit is pinned at its
        # bound and the Gaussian ellipse correspondence does not apply
        if (T < 0.02).any() and not (T < 0.02).all():
            ax.contour(gc, sl, T, levels=[0.02], colors="gray",
                       linestyles=":", linewidths=1.4)
            ax.plot([], [], ":", color="gray", label=r"transit$\to$0 wall (pinned beyond)")
        ax.plot(fit["gamma_coll"], fit["sigma_laser"], "*", color="w", ms=11,
                mec="k", mew=0.6, label="free fit (all widths free)", zorder=5)
        i_m, j_m = np.unravel_index(int(np.argmin(D)), D.shape)
        ax.plot(gc[j_m], sl[i_m], "o", color="#D55E00", ms=6, mec="w", mew=0.6,
                label="profile minimum", zorder=5)
        # same floor definition as the shipped banana metric (within=5.99 on the
        # zoom); the wide panel uses a looser cut purely to trace the topology
        fl = valley_floor(gc, sl, D, within=(5.99 if nm == "zoom" else 25.0))
        ax.plot(fl["floor_gc"], fl["floor_sl"], ".", color="#E69F00", ms=4,
                label="profile valley floor")
        if nm == "zoom":
            evals, evecs = np.linalg.eigh(M)
            th = np.linspace(0, 2 * np.pi, 200)
            for c, ls in ((2.30, "-"), (5.99, "--")):
                e = (np.sqrt(c * evals[0]) * np.outer(np.cos(th), evecs[:, 0])
                     + np.sqrt(c * evals[1]) * np.outer(np.sin(th), evecs[:, 1]))
                ax.plot(fit["gamma_coll"] + e[:, 0], fit["sigma_laser"] + e[:, 1],
                        ls, color="k", lw=1.1,
                        label=("local covariance ellipse (68/95%)" if c == 2.30 else None))
            ax.set_title("zoom: profile contours (white)\nvs the local covariance ellipse (black)",
                         fontsize=9)
        else:
            ax.set_title("wide: the width-degeneracy topology\n"
                         r"(joint 68/95% contours in white; log$_{10}\Delta\chi^2$ fill)",
                         fontsize=9)
        ax.set_xlabel(r"$\gamma_\mathrm{coll}$ (MHz, transition)")
        if k == 0:
            ax.set_ylabel(r"$\sigma_\mathrm{laser}$ FWHM (MHz, transition)")
        cb = fig.colorbar(pc, ax=ax, shrink=0.9)
        cb.set_label(r"log$_{10}\,\Delta\chi^2$", fontsize=8)
        ax.legend(fontsize=7, loc="upper right")
    fig.suptitle("Profile likelihood of the width split (993.4192 nm, 130 °C / 225 mW; "
                 "transit + nuisances re-minimised per point)", fontsize=9)
    _save(fig, "fig7_identifiability_profile.png")


def fig_ruler():
    """The built-in frequency ruler (M2, methods §3): a representative EOM
    ruler trace with its constrained seven-tooth comb fit — the same physical
    line excited via up to seven sideband pairs, teeth exactly 6.25 MHz apart
    on the laser axis (outer teeth weak: they need higher-order pairs; note
    the k=0 TOOTH is fed by (s+,s-) pairs as well as (c,c), so it can stand
    tall even with the optical carrier AM-suppressed -- the tooth pattern
    varies block to block with the 2025 HWP setting; methods section 3).
    RIGHT: the free-centres nonlinearity map (results/ruler_nlmap.csv) — the
    empirical bound (~0.3% per position) on scan nonlinearity AND any
    tooth-dependent pull (differential Stark, asymmetric-wing overlap), the
    ruler's common-mode-rejection check. Trace choice is deterministic: the
    first canonical rf-on ruler of the brightest 130 °C block."""
    from rb5s6s.ingest import load_manifest, load_trace, trace_path
    from rb5s6s.ruler import fit_comb, _comb, TEETH

    rows = sorted((r for r in load_manifest()
                   if r["role"].startswith("ruler") and r["flag"] == "canonical"
                   and r["rf_on"] == "True"),
                  key=lambda r: (r["peak"] != "4154", r["temperature_C"] != "130",
                                 r["peak"], r["temperature_C"], trace_path(r)))
    if not rows:
        print("  (no ruler trace found -- skipping fig8)")
        return
    t, v = load_trace(trace_path(rows[0]))
    fit = fit_comb(t, v)

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.8, 3.9),
                                  gridspec_kw={"width_ratios": [2.1, 1.0]})
    ax.plot(t, v, ".", ms=1.6, color="0.55", label="ruler trace (raw)")
    tf = np.linspace(t[0], t[-1], 3000)
    ax.plot(tf, _comb(tf, fit["t0_ms"], fit["delta_ms"], fit["width_ms"],
                      fit["heights"], fit["b0"], fit["b1"]),
            "-", color="#0072B2", lw=1.4,
            label=f"constrained {len(TEETH)}-tooth comb fit")
    ymax = max(fit["heights"]) + fit["b0"]
    ax.set_ylim(top=ymax * 1.22)
    for n in TEETH:
        tc = fit["t0_ms"] + n * fit["delta_ms"]
        ax.axvline(tc, color="#D55E00", lw=0.7, alpha=0.5)
        ax.annotate(f"$k={n}$", xy=(tc, ymax * 1.08), ha="center", fontsize=8,
                    color="#D55E00")
    ax.set_xlabel("scan time (ms)")
    ax.set_ylabel("fluorescence (V)")
    ax.set_title(f"the scan carries its own calibration: {len(TEETH)} copies of the same\n"
                 "line, 6.25 MHz apart on the laser axis, via EOM sideband pairs",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower left", framealpha=1.0, frameon=True)

    nl = _rows("ruler_nlmap")
    pos = np.array([float(r["pos_ms"]) for r in nl])
    rr = np.array([float(r["rate_rel"]) for r in nl])
    er = np.array([float(r["rate_rel_err"]) for r in nl])
    n_win = np.array([int(r["n"]) for r in nl])
    # Edge windows have few contributing traces, so their errors (~1/sqrt(n))
    # are LARGER THAN THE BOUND ITSELF -- the rightmost spans +/-0.74% against a
    # 0.3% band. Scaling marker area with n was not enough: a reader still
    # reads the long bar as an anomaly, or as contradicting the panel title.
    # So the two populations are now drawn differently and the title says which
    # one sets the bound. (The long bar is NOT anomalous: at n=5 it sits 0.9
    # sigma from the 1/sqrt(n) law, and its CENTRAL value, +0.24%, is inside
    # the band. Only its precision is poor.)
    well = n_win >= N_WELL_SAMPLED
    sizes = 12 + 38 * (n_win / n_win.max())
    for m, ec, alpha, z in ((well, "#009E73", 1.0, 2), (~well, "#8FBFB0", 0.9, 1)):
        ax2.errorbar(pos[m], rr[m], yerr=er[m], fmt="none", ecolor=ec,
                     elinewidth=1, capsize=2, alpha=alpha, zorder=z)
    ax2.scatter(pos[well], rr[well], s=sizes[well], color="#009E73",
                edgecolor="none", zorder=3,
                label=f"$n\\geq{N_WELL_SAMPLED}$ (sets the bound)")
    ax2.scatter(pos[~well], rr[~well], s=sizes[~well], facecolor="white",
                edgecolor="#009E73", linewidth=1.0, zorder=3,
                label=f"$n<{N_WELL_SAMPLED}$ (edge; error $>$ bound)")
    ax2.axhline(1.0, color="k", lw=0.8)
    ax2.axhspan(0.9955, 1.0045, color="#009E73", alpha=0.10)
    ax2.set_xlabel("window position (ms)")
    ax2.set_ylabel("local rate / block rate")
    ax2.set_title("sweep linearity + any tooth-dependent pull:\n"
                  r"$\lesssim$0.3% from the well-sampled windows", fontsize=9)
    # One cue, not two: the legend already carries the n split, and the old
    # free-floating "marker area ~ n" note collided with it.
    ax2.legend(fontsize=6, loc="lower left", framealpha=1.0, frameon=True)
    _save(fig, "fig8_ruler.png")


def fig_degeneracy_vs_observable():
    """Why the per-condition Lorentzian/Gaussian split is never quoted as
    physics (docs/RESEARCH_DECISIONS.md 1). LEFT: the 20 power-sweep conditions
    at 130 C in the (gamma_coll, sigma_laser) plane, each with its 1-sigma
    error ellipse from the fit's own covariance, over contours of constant
    TOTAL FWHM. The ellipses are elongated along the contours and the condition
    centres scatter along the same direction -- the split moves freely in the
    direction the observable does not constrain. RIGHT: the same conditions'
    total FWHM against power, the quantity actually measured: flat (no power
    broadening, C3a) and determined to ~1%. All values read from
    results/linefit_conditions.csv; contours from the shipped model."""
    fp = C.RESULTS_DIR / "linefit_conditions.csv"
    if not fp.exists():
        print("  (linefit_conditions.csv absent -- skipping fig10)")
        return
    rows = [r for r in csv.DictReader(open(fp)) if r["role"] == "p_sweep"]
    if not rows:
        print("  (no p_sweep rows -- skipping fig10)")
        return
    from rb5s6s.stark import _fwhm_of
    from rb5s6s.linefit import transit_fwhm_at_T

    g = np.array([float(r["gamma_coll"]) for r in rows])
    ge = np.array([float(r["gamma_coll_err"]) for r in rows])
    sl = np.array([float(r["sigma_laser"]) for r in rows])
    sle = np.array([float(r["sigma_laser_err"]) for r in rows])
    corr = np.array([float(r["corr"]) for r in rows])
    tw = np.array([float(r["total_fwhm"]) for r in rows])
    twe = np.array([float(r["total_fwhm_err"]) for r in rows])
    P = np.array([float(r["P"]) for r in rows])
    peaks = [r["peak"] for r in rows]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.2, 4.5))

    # --- LEFT: the degeneracy plane -------------------------------------
    transit = transit_fwhm_at_T(130.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
    gg = np.linspace(max(g.min() - 0.15, 0.0), g.max() + 0.15, 46)
    ss = np.linspace(max(sl.min() - 0.2, 0.0), sl.max() + 0.2, 46)
    nu = np.arange(-40.0, 40.0, 0.01)
    W = np.array([[_fwhm_of(a, b, transit, 0.0, nu) for a in gg] for b in ss])
    cs = ax1.contour(gg, ss, W, levels=8, colors="0.55", linewidths=0.8)
    ax1.clabel(cs, inline=True, fontsize=6, fmt="%.2f")

    th = np.linspace(0, 2 * np.pi, 120)
    for i, pk in enumerate(peaks):
        c = PEAK_COLOR.get(pk, "0.4")
        cov = np.array([[ge[i] ** 2, corr[i] * ge[i] * sle[i]],
                        [corr[i] * ge[i] * sle[i], sle[i] ** 2]])
        vals, vecs = np.linalg.eigh(cov)
        pts = vecs @ (np.sqrt(np.maximum(vals, 0))[:, None] * np.array([np.cos(th), np.sin(th)]))
        ax1.plot(g[i] + pts[0], sl[i] + pts[1], color=c, lw=0.8, alpha=0.55)
        ax1.plot(g[i], sl[i], "o", color=c, ms=3.5, zorder=3)
    for pk, c in PEAK_COLOR.items():
        if pk in peaks:
            ax1.plot([], [], "o-", color=c, ms=3.5, lw=0.8, label=f"993.{pk} nm")
    ax1.set_xlabel(r"$\gamma_\mathrm{coll}$  (MHz, Lorentzian component)")
    ax1.set_ylabel(r"$\sigma_\mathrm{laser}$  (MHz, Gaussian component)")
    ax1.axhline(0.0, color="0.3", lw=0.8, ls=":")
    ax1.text(gg[-1], 0.02, "unphysical below", fontsize=6, color="0.3",
             ha="right", va="bottom")
    ax1.set_ylim(min(-0.25, ss[0]), ss[-1])
    ax1.set_title("the split: free along the contour\n"
                  f"median corr = {np.median(corr):+.2f}; several 1$\\sigma$ "
                  "ellipses reach unphysical widths", fontsize=9)
    ax1.legend(fontsize=7, framealpha=1.0, frameon=True)
    ax1.grid(alpha=0.25, lw=0.5)

    # --- RIGHT: the observable ------------------------------------------
    for pk in PEAK_COLOR:
        m = [i for i, p in enumerate(peaks) if p == pk]
        if not m:
            continue
        o = np.argsort(P[m])
        ax2.errorbar(P[m][o], tw[m][o], yerr=twe[m][o], marker="o", ms=4,
                     lw=1.0, capsize=2, color=PEAK_COLOR[pk], label=f"993.{pk} nm")
    ax2.set_xlabel("laser power (mW)")
    ax2.set_ylabel("total FWHM  (MHz, transition axis)")
    ax2.set_title("the observable: no power broadening, determined to "
                  f"{100 * np.median(twe) / np.median(tw):.1f}%", fontsize=9)
    ax2.legend(fontsize=7, framealpha=1.0, frameon=True)
    ax2.grid(alpha=0.25, lw=0.5)

    fig.suptitle("One temperature, 20 conditions: the total width is measured; "
                 "its decomposition is not", fontsize=10)
    _save(fig, "fig10_degeneracy_vs_observable.png")


_RUN_GAP_S = 120      # traces this far apart or less are one acquisition run
_KICK_MHZ = 8.0       # step size that separates a hand re-centring from drift


def fig_laser_history():
    """M20: the laser frequency history, reconstructed PIECEWISE.

    Rebuilt 2026-07-29 after the retraction. The earlier version plotted
    session-referenced offsets as one continuous record and titled itself with a
    65 MHz peak-to-peak excursion; that excursion was the scope's horizontal
    knob (window-start travel x rate = 64.54 MHz against the 64.97 quoted), and
    an offset means nothing across a change of that setting. So the record is
    drawn in DISPLAY EPOCHS -- runs of unchanged window_start_ms -- with a
    visible break at every setting change, because across a break the offset is
    unknown rather than zero.

    Three panels. Left: the two sessions, one connected segment per (epoch,
    line), breaks left empty. Middle: the one long knob-untouched stretch, which
    is a genuine drift measurement. Right: the within-epoch step distribution,
    whose heavy tail is the CAVITY reference being recentred -- a real frequency
    step, unlike a knob move.
    """
    fp = C.RESULTS_DIR / "laser_history.csv"
    if not fp.exists():
        print("  (laser_history.csv absent -- skipping fig11)")
        return
    rows = list(csv.DictReader(open(fp)))
    if not rows or "display_epoch" not in rows[0]:
        print("  (laser_history.csv predates display_epoch -- re-run "
              "run_laser_history.py; skipping fig11)")
        return
    for r in rows:
        r["_t"] = int(r["t_epoch"])
        r["_o"] = float(r["offset_mhz"])
        r["_e"] = int(r["display_epoch"])
    rows.sort(key=lambda r: r["_t"])
    days = sorted({r["session_day"] for r in rows})

    fig, axes = plt.subplots(1, 3, figsize=(15.0, 4.5))

    # ---- panel 1: piecewise record, both sessions side by side --------------
    ax = axes[0]
    xoff, ticks = 0.0, []
    for d in days:
        rs = [r for r in rows if r["session_day"] == d]
        t0 = rs[0]["_t"]
        day_segs = defaultdict(list)
        for r in rs:
            day_segs[(r["_e"], r["peak"])].append(r)
        for (_, pk), g in sorted(day_segs.items()):
            if len(g) < 2:
                continue
            x = [xoff + (r["_t"] - t0) / 3600.0 for r in g]
            ax.plot(x, [r["_o"] for r in g], "-o", ms=2.6, lw=0.9,
                    color=PEAK_COLOR.get(pk, "0.6"), alpha=0.9)
        span = (rs[-1]["_t"] - t0) / 3600.0
        ticks.append((xoff + span / 2, dt_module.datetime.fromtimestamp(t0)
                      .strftime("%m-%d")))
        xoff += span + 0.6
    ax.axhline(0.0, color="0.5", lw=0.8, ls=":")
    ax.set_xticks([t for t, _ in ticks])
    ax.set_xticklabels([lab for _, lab in ticks])
    ax.set_xlabel("session (hours run left to right within each)")
    ax.set_ylabel("offset within its display epoch (MHz, laser axis)")
    n_ep = len({r["_e"] for r in rows})
    ax.set_title(f"{len(rows)} traces in {n_ep} display epochs — each segment is\n"
                 "referenced to itself; gaps are knob moves, offset unknown across them",
                 fontsize=8.5)
    ax.grid(alpha=0.25, lw=0.5)
    h = [plt.Line2D([], [], color=c, lw=2, label=f"993.{k} nm")
         for k, c in PEAK_COLOR.items()]
    ax.legend(handles=h, fontsize=7, frameon=True, framealpha=0.95, ncol=2,
              loc="lower left")

    # ---- panel 2: the QUIETEST well-sampled segment -------------------------
    # NOT the longest: the longest (75 min) is two bursts 75 min apart with
    # ~13 MHz of internal scatter, so a line through it measures a cavity
    # re-centring between the clusters, not a drift rate. Drawing it is what
    # exposed that. No epoch in the archive gives a long intervention-free
    # stretch, so the archive does NOT measure a drift rate; what it does
    # measure is how still the laser sat when nobody touched it.
    ax = axes[1]
    segs = defaultdict(list)
    for r in rows:
        segs[(r["_e"], r["peak"])].append(r)
    cand = []
    for key, g in sorted(segs.items()):
        if len(g) < 6:
            continue
        g = sorted(g, key=lambda r: r["_t"])
        dur = (g[-1]["_t"] - g[0]["_t"]) / 60.0
        yy = [r["_o"] for r in g]
        if dur > 0:
            cand.append((max(yy) - min(yy), key, g, dur))
    if cand:
        cand.sort()
        pp, (_, pk), g, dur = cand[0]
        x = (np.array([r["_t"] for r in g], float) - g[0]["_t"]) / 60.0
        y = [r["_o"] for r in g]
        ax.plot(x, y, "-o", ms=5, lw=1.0,
                color=PEAK_COLOR.get(pk, "0.6"))
        ax.axhline(0.0, color="0.5", lw=0.8, ls=":")
        pad = max(0.15, 0.35 * pp)
        ax.set_ylim(min(y) - pad, max(y) + pad)
        ax.set_xlabel("minutes into the epoch")
        ax.set_ylabel("offset (MHz, laser axis)")
        ax.set_title(f"the quietest well-sampled epoch: 993.{pk} nm,\n"
                     f"{len(g)} traces over {dur:.1f} min held to "
                     f"{pp:.2f} MHz peak-to-peak", fontsize=8.5)
        ax.grid(alpha=0.25, lw=0.5)

    # ---- panel 3: within-epoch steps, the cavity re-centrings --------------
    ax = axes[2]
    steps = []
    by = defaultdict(list)
    for r in rows:
        by[(r["_e"], r["peak"])].append(r)
    for g in by.values():
        g.sort(key=lambda r: r["_t"])
        steps += [abs(b["_o"] - a["_o"]) for a, b in zip(g, g[1:])
                  if 0 < b["_t"] - a["_t"] < 120]
    if steps:
        s = np.array(steps)
        ax.hist(s, bins=np.linspace(0, max(16.0, s.max()), 33),
                color="#0072B2", alpha=0.85)
        med = float(np.median(s))
        ax.axvline(med, color="0.15", lw=1.4, ls="--")
        ax.set_yscale("log")
        ax.set_xlabel("|step| between consecutive traces, same epoch (MHz)")
        ax.set_ylabel("count (log)")
        ax.set_title(f"median {med:.2f} MHz with a tail to {s.max():.1f} MHz —\n"
                     "quiet drift, punctuated by cavity re-centrings", fontsize=8.5)
        ax.grid(alpha=0.25, lw=0.5, which="both")

    fig.suptitle("No wavemeter log survives: what the traces can and cannot say about "
                 "the laser's frequency", fontsize=10.5)
    _save(fig, "fig11_laser_history.png")


def fig_ramp_construction():
    """How a Gaussian beam becomes a triangular shift distribution (THEORY_NOTE
    section 2, methods chapter 3). The derivation is four lines of change-of-
    variables and the result is the observable the whole analysis rests on, so
    it is worth seeing rather than integrating mentally. Every curve comes from
    rb5s6s.lineshape -- no data, no fitted parameters."""
    from rb5s6s.lineshape import stark_ramp, model_profile
    fig, ax = plt.subplots(1, 4, figsize=(13.6, 3.5))
    S0 = 1.0

    # (a) the beam, and the shift it imposes
    r = np.linspace(0, 2.2, 400)
    u = np.exp(-2 * r ** 2)
    ax[0].plot(r, u, color="#0072B2", lw=1.8)
    ax[0].fill_between(r, 0, u, color="#0072B2", alpha=0.12)
    for rr, lab, dx, dy in ((0.0, "axis: $s=-S_0$", 10, -12),
                            (1.18, "edge: $s\\to 0$", 10, 6)):
        ax[0].plot([rr], [np.exp(-2 * rr ** 2)], "o", color="#D55E00", ms=6)
        ax[0].annotate(lab, (rr, np.exp(-2 * rr ** 2)), fontsize=7,
                       textcoords="offset points", xytext=(dx, dy))
    ax[0].set_ylim(-0.03, 1.12)
    ax[0].set_xlabel("radius  $r/w$")
    ax[0].set_ylabel("$u = I/I_0$")
    ax[0].set_title("(a) the beam sets the shift\n$s = -S_0\\,u$", fontsize=9)

    # (b) the two competing weights
    uu = np.linspace(0.02, 1.0, 300)
    # all three normalised to their value on axis (u = 1) so they are comparable
    ax[1].semilogy(uu, 1 / uu, color="0.45", lw=1.6,
                   label=r"atoms per $\mathrm{d}u$: $1/u$")
    ax[1].semilogy(uu, uu ** 2, color="#009E73", lw=1.8,
                   label=r"signal each gives: $u^2$")
    ax[1].semilogy(uu, uu, color="#D55E00", lw=2.2, ls="--",
                   label=r"product: $u$")
    ax[1].set_xlabel("$u = I/I_0$")
    ax[1].set_ylabel("weight, relative to on-axis")
    ax[1].set_title("(b) many dim atoms, few bright\nones -- but $I^2$ wins",
                    fontsize=9)
    ax[1].legend(fontsize=7, framealpha=1.0, frameon=True)

    # (c) the triangle itself
    nu = np.arange(-1.6, 0.4, 0.002)
    ax[2].plot(nu, stark_ramp(nu, S0), color="#D55E00", lw=1.9)
    ax[2].axvline(-2 / 3 * S0, color="0.35", lw=1.0, ls=":")
    ax[2].annotate("mean $-\\frac{2}{3}S_0$", (-2 / 3 * S0, 2.28), fontsize=7,
                   ha="center", color="0.3")
    ax[2].set_ylim(0, 2.55)
    ax[2].set_xlabel("shift  $s/S_0$")
    ax[2].set_ylabel("density  $f(s)$")
    ax[2].set_title(r"(c) a triangle: $f(s)\propto|s|$" "\n"
                    r"skew $g_1=+0.566$, from $I^2$ alone", fontsize=9)

    # (d) what it does to the line
    g = np.arange(-14, 14, 0.01)
    sym = model_profile(g, gamma_coll=0.45, sigma_laser_fwhm=1.1,
                        transit_fwhm=1.9, s0=0.0)
    ramped = model_profile(g, gamma_coll=0.45, sigma_laser_fwhm=1.1,
                           transit_fwhm=1.9, s0=3.0)
    ax[3].plot(g, sym / sym.max(), color="0.5", lw=1.4, label="$S_0=0$")
    ax[3].plot(g, ramped / ramped.max(), color="#D55E00", lw=1.9,
               label="$S_0=3$ MHz")
    ax[3].set_xlabel("detuning (MHz)")
    ax[3].set_ylabel("normalised signal")
    ax[3].set_title("(d) the line it produces\n(exaggerated $S_0$ to show it)",
                    fontsize=9)
    ax[3].legend(fontsize=7, framealpha=1.0, frameon=True)

    for a in ax:
        a.grid(alpha=0.22, lw=0.5)
    fig.suptitle("The AC-Stark ramp: a focused beam gives a distribution of "
                 "light shifts, not one shift", fontsize=10)
    _save(fig, "fig12_ramp_construction.png")


def fig_level_scheme():
    """What transition is driven and what is detected. Vertical positions are
    TO SCALE in term energy: 5P_1/2 at 12579 cm^-1 and 6S_1/2 at 20133 cm^-1
    above the ground state, with the 993 nm virtual level at exactly half the
    two-photon energy -- which is why it falls BELOW the real 5P_1/2, not above.
    Every number is from rb5s6s.constants and polarizability; the hyperfine
    assignments are methods chapter 1."""
    from rb5s6s.polarizability import E_6S_CM
    E_5P_CM = 1.0e7 / 794.979          # 5P_1/2 term energy, NIST
    E_VIRT_CM = 1.0e7 / (C.LAMBDA_LASER_M * 1e9) if False else 1.0e7 / 993.4

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11.0, 5.0),
                                 gridspec_kw={"width_ratios": [1.15, 1]})

    y5s, yv, y5p, y6s = 0.0, E_VIRT_CM, E_5P_CM, E_6S_CM
    for y, lab in ((y5s, r"$5S_{1/2}$"), (y5p, r"$5P_{1/2}$"), (y6s, r"$6S_{1/2}$")):
        ax.hlines(y, 0.10, 0.72, color="0.15", lw=2.4)
        ax.text(0.745, y + 620, lab, va="bottom", fontsize=10)
        ax.text(0.745, y - 620, f"{y:,.0f}" + r" cm$^{-1}$", va="top",
                fontsize=6.5, color="0.5")
    ax.hlines(yv, 0.16, 0.46, color="0.55", lw=1.3, ls=(0, (4, 3)))
    ax.text(0.16, yv - 1150, "virtual level, half the two-photon energy",
            fontsize=6.8, color="0.45", va="center")

    # the two 993 nm photons, one per beam direction
    for x in (0.26, 0.40):
        ax.annotate("", (x, yv), (x, y5s),
                    arrowprops=dict(arrowstyle="-|>", color="#0072B2", lw=1.9))
        ax.annotate("", (x, y6s), (x, yv),
                    arrowprops=dict(arrowstyle="-|>", color="#0072B2", lw=1.9))
    ax.text(0.115, y6s * 0.80, "2 x 993 nm,\none photon from\neach beam\n(Doppler-free)",
            fontsize=7.5, color="#0072B2", va="top")

    # the cascade that is detected
    ax.annotate("", (0.60, y5p), (0.60, y6s),
                arrowprops=dict(arrowstyle="-|>", color="#009E73", lw=1.9))
    ax.text(0.615, 0.5 * (y5p + y6s), "1367 nm", fontsize=7.5, color="#009E73",
            va="center")
    ax.annotate("", (0.60, y5s), (0.60, y5p),
                arrowprops=dict(arrowstyle="-|>", color="#D55E00", lw=2.6))
    ax.text(0.615, 0.5 * y5p, "795 nm\ndetected", fontsize=8.5, color="#D55E00",
            va="center", fontweight="bold")

    ax.set_xlim(0.02, 0.92)
    ax.set_ylim(-1800, y6s * 1.10)
    ax.set_ylabel(r"term energy above $5S_{1/2}$ (cm$^{-1}$)", fontsize=8)
    ax.tick_params(labelsize=7)
    ax.spines[["top", "right", "bottom"]].set_visible(False)
    ax.set_xticks([])
    ax.set_title(f"to scale; natural width {GNAT:.2f} MHz", fontsize=9)

    # --- the four measured lines ---------------------------------------
    lines = [("4121", 993.4121, r"$^{87}$Rb", r"$F{=}1\!\to\!1$"),
             ("4154", 993.4154, r"$^{85}$Rb", r"$F{=}2\!\to\!2$"),
             ("4192", 993.4192, r"$^{85}$Rb", r"$F{=}3\!\to\!3$"),
             ("4207", 993.4207, r"$^{87}$Rb", r"$F{=}2\!\to\!2$")]
    for pk, lam, iso, hf in lines:
        c = PEAK_COLOR[pk]
        bx.vlines(lam, 0.32, 0.78, color=c, lw=2.6)
        bx.text(lam, 0.82, f"993.{pk}", rotation=90, fontsize=7.5,
                color=c, ha="center", va="bottom")
        bx.text(lam, 0.275, iso, fontsize=7.5, color=c, ha="center", va="top")
        bx.text(lam, 0.205, hf, fontsize=7, color=c, ha="center", va="top")
    bx.set_xlim(993.4108, 993.4220)
    bx.set_ylim(0.0, 1.30)
    bx.ticklabel_format(useOffset=False, style="plain", axis="x")
    bx.set_xticks([993.412, 993.415, 993.418, 993.421])
    bx.set_xticklabels(["993.4120", "993.4150", "993.4180", "993.4210"],
                       fontsize=8)
    bx.set_yticks([])
    bx.set_xlabel("wavemeter reading (nm, uncalibrated)")
    bx.set_title("the four hyperfine components measured", fontsize=9)
    bx.text(0.5, 0.04, "readings identify the lines, not absolute wavelengths",
            transform=bx.transAxes, ha="center", fontsize=7, color="0.35")
    bx.grid(alpha=0.20, lw=0.5, axis="x")

    fig.suptitle(r"Rb $5S_{1/2}\to 6S_{1/2}$: a degenerate two-photon transition, "
                 "read out on the 795 nm cascade", fontsize=10)
    _save(fig, "fig13_level_scheme.png")



def fig_wavemeter_reconstruction():
    """The wavemeter record, its model, and the same quantity from our traces (M22).

    The result is the settled floor on unmodelled laser motion. The relaxation
    time constants are not constrained by this record and are not shown as
    though they were.
    """
    import collections
    import csv

    import matplotlib.image as mpimg
    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_wavemeter_reconstruction import reconstruct, PHOTO
    r = reconstruct()
    t, f, band = r["t"], r["f"], r["band"]
    tf, mu, sg = r["t_fit"], r["mu"], r["sigma"]

    fig = plt.figure(figsize=(7.6, 8.4))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.35, 2.0, 1.5], hspace=0.34)

    ax0 = fig.add_subplot(gs[0])
    ax0.imshow(mpimg.imread(str(PHOTO)))
    ax0.set_axis_off()
    ax0.set_title("(a) as photographed: 2025-06-11, a preliminary session five "
                  "weeks before the campaign", fontsize=8.5)

    ax1 = fig.add_subplot(gs[1])
    ax1.fill_between(t, f - band/2, f + band/2, color="#0072B2", alpha=0.15, lw=0,
                     label=f"scan band, {r['band_mhz']:.0f} MHz")
    ax1.plot(t, f, color="#0072B2", lw=0.7, label="digitised band centre")
    ax1.plot(tf, mu, color="#D55E00", lw=1.8,
             label=f"{r['n_kicks']} re-locks, each relaxing back")
    for k, tk in enumerate(r["kick_times"]):
        ax1.axvline(tk, color="#D55E00", lw=0.8, ls=":", alpha=0.55)
    ax1.set_ylabel("frequency  (MHz)")
    ax1.legend(loc="lower right", fontsize=7.5, frameon=True, framealpha=0.9)
    ax1.set_title("(b) the record is re-locks and relaxation, not drift", fontsize=8.5)

    ax2 = fig.add_subplot(gs[2])
    ax2.fill_between(tf, -sg, sg, color="#D55E00", alpha=0.18, lw=0,
                     label=f"fitted noise, settling to {r['sigma_inf']:.2f} MHz")
    ax2.plot(tf, f[::3] - mu, color="#666666", lw=0.6, label="residual")
    rows = [x for x in csv.DictReader(open(C.REPO_ROOT / "results" / "laser_history.csv"))
            if x["flag"] == "canonical" and x["offset_mhz"] not in ("", "nan")]
    ep = collections.defaultdict(list)
    for x in rows:
        ep[x["display_epoch"]].append((int(x["t_epoch"]), float(x["offset_mhz"])))
    best = sorted(max(ep.values(), key=lambda v: max(a for a, _ in v) - min(a for a, _ in v)))
    tt = np.array([(a - best[0][0]) / 60 for a, _ in best])
    oo = np.array([b for _, b in best]); oo -= oo.mean()
    # markers only: the archive samples in bursts, not continuously
    ax2.plot(tt, oo, "o", color="#009E73", ms=5,
             label=f"our traces, same quantity, sd {oo.std():.1f} MHz")
    ax2.axhline(0, color="k", lw=0.5)
    ax2.set_xlabel("time  (min)")
    ax2.set_ylabel("frequency  (MHz)")
    ax2.legend(loc="upper right", fontsize=7.5, frameon=True, framealpha=0.9)
    ax2.set_ylim(-9, 12)          # the first seconds spike off-scale; the
                                  # settled region is the point of this panel
    ax2.set_title("(c) what is left: the noise settles, and the floor is what "
                  "a measurement must beat  (axis clipped)", fontsize=8.5)
    _save(fig, "fig14_wavemeter_reconstruction.png")




def fig_drift_story():
    """The drift problem, what the archive extracted despite it, and what a
    fixed lock buys (fig15). Three panels.

    (a) The problem, photographed: the 2025-06-11 wavemeter record, digitised
        by M22 -- re-lock kicks and relaxations on a drifting cavity lock.
        Not campaign data; the campaign saved no wavemeter log at all, which
        is the point of panel (b).
    (b) The campaign, reconstructed from its own traces (M20): line offsets
        within each scope-knob epoch. Absolute frequency is unknowable across
        epoch boundaries (the knob moved 58 times), so each segment floats;
        within a segment the excursion is ~1 MHz and the held-lock drift is
        +0.016 [0.007, 0.025] MHz/min (state-space fit on the recovered
        clock, audit addendum 5; band shown).
    (c) The consequence ladder: what each drift regime licenses, with the
        archive's extracted bounds and the fixed-lock conversions annotated.
        The fixed-lock benchmark is Ayachitula 2024 on this same transition:
        < 0.5 kHz over 50 min.
    """
    import csv as _csv

    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    from run_wavemeter_reconstruction import reconstruct
    r = reconstruct()
    t, f, band = r["t"], r["f"], r["band"]
    tf, mu = r["t_fit"], r["mu"]

    # campaign side: within-epoch offsets from the committed laser history
    rows = [x for x in _csv.DictReader(open(C.RESULTS_DIR / "laser_history.csv"))
            if x["flag"] == "canonical" and x["offset_mhz"]]
    t0 = min(float(x["t_epoch"]) for x in rows)

    # Each row IS a recorded trace: a 2000-point, fixed-duration Agilent scan
    # (module M0/ingest.py), so its clock time carries a real scan span, not
    # just a fitted centre. duration x the trace's own session rate
    # (results/ruler_blocks.csv, before/after brackets averaged for the P
    # sessions) is that span; falls back to the campaign-wide rate only if a
    # (session, peak, T) combination is somehow absent from ruler_blocks.
    trace_duration_ms = TRACE_N_POINTS * TRACE_DT_S * 1e3   # 1000 ms, fixed format
    rate_sum, rate_n = defaultdict(float), defaultdict(int)
    for rb in _csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        key = (rb["session"], rb["peak"], rb["T"])
        rate_sum[key] += float(rb["rate"])
        rate_n[key] += 1
    rate_by_key = {k: rate_sum[k] / rate_n[k] for k in rate_sum}
    campaign_rate = float(next(iter(
        _csv.DictReader(open(C.RESULTS_DIR / "ruler_campaign.csv"))))["rate_laser"])

    def _span_mhz(x):
        session = "P" if x["role"] in ("p_sweep", "ruler_p") else "T"
        rate = rate_by_key.get((session, x["peak"], x["temperature_C"]), campaign_rate)
        return trace_duration_ms * rate

    by_ep = {}
    for x in rows:
        by_ep.setdefault(int(x["display_epoch"]), []).append(
            ((float(x["t_epoch"]) - t0) / 3600.0, float(x["offset_mhz"]), _span_mhz(x)))

    # the extracted-vs-gain numbers, read from the committed CSVs
    s0 = float(next(x["value"] for x in _csv.DictReader(open(C.RESULTS_DIR / "stark_joint.csv"))
                    if x["quantity"] == "S0_225mW_ub95"))
    bvals = [float(x["bound95_nscale"]) for x in _csv.DictReader(open(C.RESULTS_DIR / "beta_self_probe.csv"))
             if x.get("headline") == "yes"]
    sl = float(next(x["value_MHz"].lstrip("<") for x in _csv.DictReader(open(C.RESULTS_DIR / "laser_epoch.csv"))
                    if x["quantity"] == "sigma_laser_bound"))

    fig = plt.figure(figsize=(8.6, 9.2))
    gs = fig.add_gridspec(3, 1, height_ratios=[1.6, 1.6, 1.15], hspace=0.42)

    # (a) the photographed record, digitised
    ax = fig.add_subplot(gs[0])
    ax.fill_between(t, f - band / 2, f + band / 2, color="#0072B2", alpha=0.25,
                    lw=0, label="scan band (the sweep, not noise)")
    ax.plot(t, f, color="#0072B2", lw=0.9, label="band centre = laser frequency")
    mclip = tf > 0.4     # the pre-first-kick baseline is a fit artifact
    ax.plot(tf[mclip], mu[mclip], color="#D55E00", lw=1.6, ls="--",
            label="M22 model: re-lock kicks + relaxations")
    for tk in r["kick_times"]:
        ax.axvline(tk, color="0.55", lw=0.7, alpha=0.6)
    ax.set_xlabel("time (min)")
    ax.set_ylabel("laser detuning (MHz)")
    ax.set_title("(a) the problem, photographed: wavemeter record, 2025-06-11 "
                 "preliminary session (no log survives from the campaign itself)",
                 fontsize=9)
    ax.legend(fontsize=7, loc="lower right", framealpha=1.0, frameon=True)

    # (b) the campaign, reconstructed from its own traces
    ax = fig.add_subplot(gs[1])
    drift = 0.016   # MHz/min, laser; audit addendum 5 (state-space, recovered clock)
    dlo, dhi = 0.007, 0.025
    first = True
    first_band = True
    for ep, pts in sorted(by_ep.items()):
        if len(pts) < 2:
            continue
        pts.sort()
        th = [p[0] for p in pts]
        off = [p[1] for p in pts]
        span = [p[2] for p in pts]
        # texture, not decoration: each segment is one recorded trace's own
        # piezo scan ramp (duration x that session's ruler rate), centred on
        # its fitted centre -- the like-for-like counterpart of panel (a)'s
        # photographed scan band, drawn low-alpha so the smooth centre
        # line/points (plotted next, on top) stay legible.
        lbl = None
        if first_band:
            lbl = f"each trace's own scan ramp (~{span[0]:.0f} MHz)"
        ax.vlines(th, [o - s / 2 for o, s in zip(off, span)],
                  [o + s / 2 for o, s in zip(off, span)],
                  color="#009E73", lw=0.7, alpha=0.10, zorder=1, label=lbl)
        first_band = False
        ax.plot(th, off, "-", color="#009E73", lw=0.8, alpha=0.85, zorder=2)
        ax.plot(th, off, ".", color="#009E73", ms=2.5, zorder=3,
                label="line offset within one knob epoch" if first else None)
        first = False
    # A slope INDICATOR over 3 h, not a fit across the record: the absolute
    # trend across epochs is exactly what the knob moves make unknowable.
    ts0, y0 = 9.0, -9.5
    tind = np.linspace(ts0, ts0 + 3.0, 20)
    ax.plot(tind, y0 + (tind - ts0) * 60 * drift, color="#D55E00", lw=1.8,
            ls="--", label="held-lock drift, slope only: +0.016 MHz/min")
    ax.fill_between(tind, y0 + (tind - ts0) * 60 * dlo,
                    y0 + (tind - ts0) * 60 * dhi,
                    color="#D55E00", alpha=0.25, lw=0)
    ax.annotate("what the held lock does in 3 h", xy=(ts0 + 1.5, y0 + 3.2),
                ha="center", fontsize=7.5, color="#D55E00")
    ax.set_xlabel("time into campaign (h)")
    ax.set_ylabel("offset (MHz, laser)")
    ax.set_title("(b) the campaign, reconstructed from its own traces (M20): "
                 "segments float (58 knob moves re-zero the axis); shapes survive",
                 fontsize=9)
    ax.legend(fontsize=7, loc="upper right", framealpha=1.0, frameon=True)

    # (c) the consequence ladder
    ax = fig.add_subplot(gs[2])
    regimes = [
        (4.0, "planning envelope (2025)", "everything below is usable"),
        (drift, "2025 held lock, measured", "shapes only: bounds\n"
         f"$S_0<{s0:.2f}$ MHz, $\\beta$ {min(bvals):.1f}-{max(bvals):.1f}, "
         f"$\\sigma_\\mathrm{{laser}}<{sl:.1f}$ MHz"),
        (1e-5, "fixed lock, demonstrated on this line\n(Ayachitula 2024: <0.5 kHz / 50 min)",
         "centres usable: measure the pull ($\\propto S_0$),\n"
         "the self-shift, and $\\beta$ at 3-12$\\sigma$"),
    ]
    ys = [2, 1, 0]
    for y, (rate, left, right) in zip(ys, regimes):
        ax.plot([rate], [y], "o", ms=9, color="#0072B2")
        ax.annotate(left, xy=(rate, y), xytext=(0, 12), textcoords="offset points",
                    ha="center", fontsize=7.5)
        ax.annotate(right.replace("\\n", "\n"), xy=(rate, y), xytext=(0, -13),
                    textcoords="offset points", ha="center", va="top", fontsize=7.5)
    ax.set_xscale("log")
    ax.set_xlim(3e-6, 30)
    ax.set_ylim(-1.4, 3.1)
    ax.set_yticks([])
    ax.set_xlabel("laser drift rate (MHz/min, laser axis)")
    ax.set_title("(c) what each regime licenses: the archive's bounds, and the "
                 "session's conversions", fontsize=9)
    ax.grid(axis="y", visible=False)
    _save(fig, "fig15_drift_story.png")


def fig_fit_gallery():
    """M25 fit-quality gallery: data, model overlay and residuals, per peak.

    Picks the single highest-SNR campaign trace per peak (the 225 mW, 130 C
    p_sweep condition, the brightest combination of power and temperature the
    campaign ran, per fig2's P^2 amplitude law, taking the largest-amplitude
    repeat of the five) and overlays the M25 global archive model at the
    COMMITTED shared optimum read from results/global_archive_fit.csv:
    kappa_min, beta_self_joint, sigma_laser (per session/T block) and the
    transit reference. This does not re-run the global fit.

    Per-trace nuisances the global fit solves separately for every trace
    (amplitude, centre, background level and slope) are recomputed here by a
    local least-squares fit with the shared parameters held fixed. The
    saturation scale Vsat is also a per-session shared M25 parameter, but its
    fitted value is not written to the committed CSV, so it is refit as a
    local nuisance here too, which is noted on the figure.

    At the committed profile minimum kappa_min = 0.0 MHz/W, so the AC-Stark
    ramp width is exactly zero in the drawn model for every trace here. That
    is a property of the committed optimum, not a choice made for this
    figure.
    """
    fp = C.RESULTS_DIR / "global_archive_fit.csv"
    if not fp.exists():
        print("  (global_archive_fit.csv absent -- skipping fig16)")
        return
    if not (C.DATA_RAW_DIR / "MANIFEST.csv").exists():
        print("  (data_raw/MANIFEST.csv absent -- skipping fig16)")
        return

    rows = _rows("global_archive_fit")

    def val(q, k="primary"):
        return float(next(r["value"] for r in rows if r["quantity"] == q and r["key"] == k))

    status = next(r["status"] for r in rows if r["quantity"] == "beta_self_joint")
    kappa = val("kappa_min")
    beta = val("beta_self_joint")
    sl_blocks = {r["key"]: float(r["value"]) for r in rows if r["quantity"] == "sigma_laser"}

    sys.path.insert(0, str(C.REPO_ROOT / "scripts"))
    try:
        from run_global_archive_fit import DNU_FLOOR, load_campaign_all
        from rb5s6s.linefit import _shared_profile_grid, transit_fwhm_at_T
        traces = load_campaign_all()
    except Exception as e:  # missing/changed raw archive: degrade like fig7/10/11
        print(f"  (could not load campaign traces for fig16: {e} -- skipping)")
        return

    # brightest campaign condition per peak: 225 mW at 130 C is both the
    # highest power AND the highest temperature the campaign ran, so it is
    # the single brightest condition available (fig2: amplitude ~ P^2).
    # Within its five repeats, take the largest peak-amplitude one.
    reps = {}
    for t in traces:
        if t["T"] == 130.0 and abs(t["P"] - 0.225) < 1e-9:
            cur = reps.get(t["peak"])
            if cur is None or t["A0"] > cur["A0"]:
                reps[t["peak"]] = t
    peaks = ("4121", "4154", "4192", "4207")
    if not all(pk in reps for pk in peaks):
        print("  (missing a 225 mW / 130 C campaign trace for some peak, skipping fig16)")
        return

    fig = plt.figure(figsize=(13.5, 9.8))
    outer = fig.add_gridspec(2, 2, hspace=0.34, wspace=0.24, top=0.83, bottom=0.06,
                             left=0.06, right=0.98)
    slot = {"4121": (0, 0), "4154": (0, 1), "4192": (1, 0), "4207": (1, 1)}

    for peak in peaks:
        t = reps[peak]
        r0, c0 = slot[peak]
        inner = outer[r0, c0].subgridspec(2, 1, height_ratios=[3.0, 1.1], hspace=0.08)
        ax_main = fig.add_subplot(inner[0])
        ax_res = fig.add_subplot(inner[1], sharex=ax_main)

        T, P = t["T"], t["P"]
        gc = beta * float(density_units(T))
        sl = sl_blocks[t["sl"]]
        transit = transit_fwhm_at_T(T, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
        s0 = kappa * P
        g, prof = _shared_profile_grid(gc, sl, transit, s0, "gaussian", dnu_floor=DNU_FLOOR)
        x, v, sg = t["x"], t["v"], t["sg"]

        def model_at(p, xx, g=g, prof=prof):
            A, cc, b0, b1, logVs = p
            lin = A * np.interp(xx - cc, g, prof, left=0.0, right=0.0)
            Vs = np.exp(logVs)
            return Vs * (1.0 - np.exp(-lin / Vs)) + b0 + b1 * xx

        def resid(p, x=x, v=v, sg=sg):
            return (v - model_at(p, x)) / sg

        p0 = [t["A0"], t["c0"], t["b0"], 0.0, 5.0]
        lo = [0.0, t["c0"] - 8.0, -np.inf, -np.inf, -1.0]
        hi = [np.inf, t["c0"] + 8.0, np.inf, np.inf, 6.0]
        sol = least_squares(resid, p0, bounds=(lo, hi), x_scale="jac", ftol=1e-13, xtol=1e-13)
        A, cc, b0, b1, logVs = sol.x
        Vs = np.exp(logVs)
        n_local = 5
        chi2 = float(np.sum(resid(sol.x) ** 2))
        dof = max(len(x) - n_local, 1)
        chi2_red = chi2 / dof

        # FWHM measured off the drawn model curve (background subtracted),
        # by linear interpolation across the half-maximum crossings.
        xf = np.linspace(x.min(), x.max(), 4000)
        lin_f = A * np.interp(xf - cc, g, prof, left=0.0, right=0.0)
        line_f = Vs * (1.0 - np.exp(-lin_f / Vs))
        half = line_f.max() / 2.0
        idx = np.where(line_f >= half)[0]
        if len(idx) >= 2:
            il, ir = int(idx[0]), int(idx[-1])

            def cross(i0, i1):
                x0, x1, y0, y1 = xf[i0], xf[i1], line_f[i0], line_f[i1]
                return x0 + (half - y0) * (x1 - x0) / (y1 - y0)
            xl = cross(il - 1, il) if il > 0 else xf[il]
            xr = cross(ir, ir + 1) if ir < len(xf) - 1 else xf[ir]
            fwhm = xr - xl
        else:
            fwhm = float("nan")

        # ---- main panel: data + model, centred on the fitted line centre ----
        xd = x - cc
        ax_main.plot(xd, v, ".", ms=2.2, color="0.4", alpha=0.5, label="data")
        ax_main.plot(xf - cc, model_at(sol.x, xf), "-", color=PEAK_COLOR[peak], lw=1.7,
                     label="M25 global model")
        ax_main.set_ylabel("signal (V)")
        ax_main.set_title(f"{PEAK_LABEL[peak]}, 225 mW / 130 °C p_sweep, "
                           f"brightest repeat\nFWHM {fwhm:.3f} MHz, "
                           r"$\chi^2_\nu$" + f" = {chi2_red:.2f} (n={len(x)})",
                           fontsize=8.5)
        ax_main.legend(fontsize=7, loc="upper right", frameon=True, framealpha=0.9)
        ax_main.tick_params(labelbottom=False)

        # ---- residual panel ----
        res_v = v - model_at(sol.x, x)
        ax_res.plot(xd, res_v, ".", ms=2.0, color=PEAK_COLOR[peak], alpha=0.6)
        ax_res.axhline(0.0, color="k", lw=0.7)
        rmax = float(np.max(np.abs(res_v))) * 1.15 if len(res_v) else 1.0
        ax_res.set_ylim(-rmax, rmax)
        ax_res.set_xlabel("detuning from fitted centre (MHz, transition axis)")
        ax_res.set_ylabel("resid (V)", fontsize=8)

    fig.suptitle(
        "Fit-quality gallery: the M25 global archive model at its committed shared "
        f"optimum (status {status}) against one representative trace per peak\n"
        "Shared kappa, beta_self, sigma_laser and transit are frozen at the M25 "
        "committed values (kappa_min = 0, so no Stark ramp is drawn).\n"
        "Per-trace amplitude, centre, background and the saturation scale (not "
        "persisted in the committed CSV) are refit locally. No re-run.\n"
        "Residuals: the antisymmetric near-centre structure falls as "
        "amplitude$^{-0.5}$ on both the power and temperature axes (shot noise, "
        "the C3g residual-skew scaling, not a lineshape asymmetry).\n"
        "A small symmetric centre excess on the brightest traces (up to 1.4% of "
        "peak on 4192, below the noise inflation) remains unattributed and does "
        "not move any committed number.",
        fontsize=9.0, y=0.995)
    _save(fig, "fig16_fit_gallery.png")


def fig_magic_wavelengths():
    """The 5S-6S magic wavelengths (M16): where the light shift lands the
    same on both clock states.

    GENERIC LAW FIRST: a magic wavelength is a wavelength where the
    differential AC-Stark shift between two states vanishes. A trap held
    there shifts both states equally, so it does not move the transition
    between them -- the trick behind every optical-lattice clock (e.g. Sr
    at 813 nm). THE INSTANCE here: for Rb 5S1/2 and 6S1/2 (the 993 nm line)
    that happens near 1204, 1288 and 1340 nm, from an independent
    sum-over-states recompute (rb5s6s.polarizability, M16) on published
    matrix elements -- Volz & Schmoranzer 1996, Herold et al. 2012, the
    Safronova-group portal, Leonard et al. 2015; full sourcing is in that
    module's docstring. Both states are J=1/2, so under linear polarization
    the scalar term is EXACT (the tensor polarizability vanishes
    identically by the triangle rule), not an approximation resting on the
    vector/tensor terms being small.

    TOP panel: Delta_alpha = alpha_6S - alpha_5S and its three zero
    crossings, each marked with its committed 16-84% Monte Carlo band
    (results/polarizability.csv). BOTTOM panel: alpha_5S and alpha_6S
    separately, on the same axis, so the crossings are visibly just where
    a nearly-flat curve (alpha_5S, far from its own D-line poles here)
    meets a curve threaded between nearby 6S->nP resonances (alpha_6S).
    Points within a mask of a 6S->nP pole are dropped (NaN) so the
    crossings stay readable; the poles are the physics, not a plotting
    artifact.

    Status: ENVELOPE (unpublished to the depth searched 2026-07-17,
    scalar-only). The vector term near the 6S-5P lines needs its own
    treatment before any trap design -- see rb5s6s/polarizability.py.
    """
    import re

    from rb5s6s import polarizability as P

    rows = _rows("polarizability")
    magic_rows = sorted((r for r in rows if r["quantity"] == "magic_5s6s"),
                        key=lambda r: float(r["value"]))
    if not magic_rows:
        print("  (no magic_5s6s rows in polarizability.csv -- skipping fig17)")
        return
    status = magic_rows[0]["status"]
    crossings = []
    for r in magic_rows:
        lam = float(r["value"])
        m = re.search(r"16-84% band ([\d.]+)\.\.([\d.]+) nm", r["unit"])
        lo, hi = (float(m.group(1)), float(m.group(2))) if m else (lam, lam)
        crossings.append((lam, lo, hi))

    lo_nm, hi_nm = 1050.0, 1420.0
    CLIP = 2500.0                                  # a.u.; masks the 6S->nP poles
    g = np.linspace(lo_nm, hi_nm, 4000)
    a5 = np.array([P.alpha_5s(x) for x in g])
    a6 = np.array([P.alpha_6s(x) for x in g])
    da = a6 - a5
    a6_m = np.where(np.abs(a6) > CLIP, np.nan, a6)
    da_m = np.where(np.abs(da) > CLIP, np.nan, da)

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(9.6, 7.8), sharex=True,
        gridspec_kw={"height_ratios": [1.15, 1.0], "hspace": 0.08})

    # ---- top: the differential and its zero crossings ----
    ax_top.axhline(0, color="0.55", lw=0.9)
    ax_top.plot(g, da_m, color="#0072B2", lw=1.7)
    for i, (lam, clo, chi) in enumerate(crossings):
        ax_top.axvline(lam, color="#D55E00", ls="--", lw=1.1)
        ax_top.annotate(
            f"{lam:.2f} nm\n[{clo:.2f}, {chi:.2f}]",
            (lam, 0.0), xytext=(0, 34 if i % 2 == 0 else -46),
            textcoords="offset points", ha="center", fontsize=7.6,
            color="#D55E00",
            bbox=dict(boxstyle="round,pad=0.15", facecolor="white",
                     edgecolor="none", alpha=0.85),
            arrowprops=dict(arrowstyle="-", color="#D55E00", lw=0.7, alpha=0.6))
    ax_top.text(
        lo_nm + (hi_nm - lo_nm) * 0.02, CLIP * 0.88,
        "at each crossing a trap pulls 5S and 6S equally --\n"
        "the 993 nm clock transition does not move",
        fontsize=7.6, color="0.3", ha="left", va="top")
    ax_top.set_ylabel(r"$\Delta\alpha=\alpha_{6S}-\alpha_{5S}$  (a.u.)")
    ax_top.set_ylim(-CLIP * 1.05, CLIP * 1.05)
    ax_top.set_title(
        "Magic wavelengths: the zero crossings of the differential scalar "
        "polarizability", fontsize=9.5)

    # ---- bottom: the two states separately -- the resonance structure ----
    ax_bot.axhline(0, color="0.7", lw=0.7)
    ax_bot.plot(g, a5, color="#009E73", lw=1.7,
                label=r"$\alpha_{5S}$ (smooth: far from its own D-line poles)")
    ax_bot.plot(g, a6_m, color="#E69F00", lw=1.5,
                label=r"$\alpha_{6S}$ (poles: nearby 6S$\to n$P resonances)")
    for lam, _, _ in crossings:
        ax_bot.axvline(lam, color="#D55E00", ls=":", lw=1.0)
    ax_bot.set_ylim(-CLIP * 1.05, CLIP * 1.05)
    ax_bot.set_xlabel("wavelength (nm)")
    ax_bot.set_ylabel(r"$\alpha$  (a.u.)")
    ax_bot.legend(fontsize=7.5, loc="lower left", framealpha=1.0, frameon=True)

    fig.suptitle(
        "A magic wavelength is where the differential light shift between two states vanishes:\n"
        "a trap there shifts both equally, so the transition it holds atoms for does not move.\n"
        r"Instance: Rb 5S$_{1/2}$-6S$_{1/2}$ (993 nm) -- scalar-only, EXACT for $J=1/2$ under "
        f"linear polarization. Status: {status}.",
        fontsize=9.0, y=0.995)

    fig.text(
        0.01, 0.018,
        "Source: results/polarizability.csv (magic_5s6s rows) + rb5s6s/polarizability.py "
        "(alpha_5s, alpha_6s). Regenerate: python scripts/run_polarizability.py && "
        "python scripts/make_figures.py.",
        fontsize=6.6, color="0.35")
    fig.text(
        0.01, 0.002,
        "Matrix elements: Volz & Schmoranzer 1996, Herold et al. 2012, the Safronova-group "
        "portal, Leonard et al. 2015 (full sourcing in rb5s6s/polarizability.py); unpublished "
        "to the depth searched 2026-07-17.",
        fontsize=6.6, color="0.35")

    _save(fig, "fig17_magic_wavelengths.png")


def main() -> int:
    fig_width_vs_density()
    fig_power_sweep()
    fig_transit_mc()
    fig_amplitude_ratios()
    fig_pooled_width()
    fig_gamma_floor()
    fig_identifiability_profile()
    fig_ruler()
    fig_degeneracy_vs_observable()
    fig_laser_history()
    fig_ramp_construction()
    fig_level_scheme()
    fig_wavemeter_reconstruction()
    fig_drift_story()
    fig_fit_gallery()
    fig_magic_wavelengths()
    print(f"wrote figures to {FIG}/")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
