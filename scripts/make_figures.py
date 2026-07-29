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
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import density_units  # noqa: E402
from rb5s6s.constants import GAMMA_NAT_HZ  # noqa: E402

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
    a2.set_title("σ_laser(T) is MODEL-DEPENDENT: the free fit is flat (~1.1,\n"
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
    ruler trace with its constrained five-tooth comb fit — the same physical
    line excited via five sideband pairs, teeth exactly 6.25 MHz apart on the
    laser axis (outer teeth weak: they need second-order pairs; note the k=0
    TOOTH is fed by (s+,s-) pairs as well as (c,c), so it can stand tall even
    with the optical carrier AM-suppressed -- the tooth pattern varies block
    to block with the 2025 HWP setting; methods section 3). RIGHT: the
    free-centres nonlinearity map (results/ruler_nlmap.csv) — the empirical
    bound (~0.3% per position) on scan nonlinearity AND any tooth-dependent
    pull (differential Stark, asymmetric-wing overlap), the ruler's
    common-mode-rejection check. Trace choice is deterministic: the first
    canonical rf-on ruler of the brightest 130 °C block."""
    from rb5s6s.ingest import load_manifest, load_trace, trace_path
    from rb5s6s.ruler import fit_comb, _comb

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
            "-", color="#0072B2", lw=1.4, label="constrained 5-tooth comb fit")
    ymax = max(fit["heights"]) + fit["b0"]
    ax.set_ylim(top=ymax * 1.22)
    for n in range(-2, 3):
        tc = fit["t0_ms"] + n * fit["delta_ms"]
        ax.axvline(tc, color="#D55E00", lw=0.7, alpha=0.5)
        ax.annotate(f"$k={n}$", xy=(tc, ymax * 1.08), ha="center", fontsize=8,
                    color="#D55E00")
    ax.set_xlabel("scan time (ms)")
    ax.set_ylabel("fluorescence (V)")
    ax.set_title("the scan carries its own calibration: five copies of the same\n"
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
    # 0.45% band. Scaling marker area with n was not enough: a reader still
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
                  r"$\lesssim$0.45% from the well-sampled windows", fontsize=9)
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


def fig_laser_history():
    """The laser's frequency history, reconstructed from the atoms and the
    recovered file timestamps alone (M20, scripts/run_laser_history.py). No
    wavemeter log survives the 2025 campaign; the fitted peak position IS the
    laser's offset within the sweep, and the EOM ruler converts it to MHz. One
    panel per acquisition day, hours since that day's first trace. This is a
    PREDICTION of what a wavemeter log would show -- if one is ever recovered,
    it can be compared point by point, testing the ruler calibration, the
    mtime-as-acquisition-time assumption and the peak extraction at once."""
    fp = C.RESULTS_DIR / "laser_history.csv"
    if not fp.exists():
        print("  (laser_history.csv absent -- skipping fig11)")
        return
    rows = list(csv.DictReader(open(fp)))
    if not rows:
        return
    days = sorted({r["session_day"] for r in rows})
    sf_fp = C.RESULTS_DIR / "laser_history_structure.csv"
    sf = list(csv.DictReader(open(sf_fp))) if sf_fp.exists() else []
    ncol = len(days) + (1 if sf else 0)
    fig, axes = plt.subplots(1, ncol, figsize=(4.8 * ncol, 4.3), squeeze=False)
    for ax, d in zip(axes[0], days):
        rs = sorted((r for r in rows if r["session_day"] == d),
                    key=lambda r: int(r["t_epoch"]))
        t0 = int(rs[0]["t_epoch"])
        for pk in PEAK_COLOR:
            sel = [r for r in rs if r["peak"] == pk]
            if not sel:
                continue
            ax.plot([(int(r["t_epoch"]) - t0) / 3600 for r in sel],
                    [float(r["offset_mhz"]) for r in sel],
                    "o", ms=3.2, alpha=0.8, color=PEAK_COLOR[pk],
                    label=f"993.{pk} nm")
        other = [r for r in rs if r["peak"] not in PEAK_COLOR]
        if other:
            ax.plot([(int(r["t_epoch"]) - t0) / 3600 for r in other],
                    [float(r["offset_mhz"]) for r in other],
                    "o", ms=2.6, alpha=0.5, color="0.55", label="other/QC")
        ax.axhline(0.0, color="0.4", lw=0.8, ls=":")
        ax.set_xlabel("hours since first trace of the day")
        ax.set_ylabel("reconstructed laser offset (MHz, laser axis)")
        import datetime as _dt
        ax.set_title(_dt.datetime.fromtimestamp(t0).strftime("%Y-%m-%d")
                     + f"  ({len(rs)} traces)", fontsize=9)
        ax.legend(fontsize=7, framealpha=1.0, frameon=True)
        ax.grid(alpha=0.25, lw=0.5)
    if sf:
        ax = axes[0][-1]
        lag = [0.5 * (float(b["lag_lo_s"]) + min(float(b["lag_hi_s"]), 7200.0))
               for b in sf]
        rms = [float(b["rms_mhz"]) for b in sf]
        ax.semilogx(lag, rms, "o-", color="#0072B2", ms=5, lw=1.4)
        for x, y, b in zip(lag, rms, sf):
            ax.annotate(f"n={b['n_pairs']}", (x, y), fontsize=6,
                        textcoords="offset points", xytext=(0, -12), ha="center")
        ax.axhline(rms[0], color="0.5", lw=0.8, ls=":")
        ax.text(lag[0], rms[0] * 1.04, "flat here = scatter, not history",
                fontsize=6.5, color="0.35")
        ax.set_xlabel("time between two traces of the SAME line (s)")
        ax.set_ylabel("RMS disagreement (MHz)")
        ax.set_title(f"the test: {rms[-1] / rms[0]:.1f}× rise, so it is real\n"
                     "correlation time a few minutes", fontsize=9)
        ax.grid(alpha=0.25, lw=0.5, which="both")
    off = [float(r["offset_mhz"]) for r in rows]
    fig.suptitle("No wavemeter log survives: the laser's drift and hand re-centrings, "
                 f"rebuilt from the lines themselves ({max(off) - min(off):.0f} MHz "
                 "peak-to-peak)", fontsize=10)
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
    print(f"wrote figures to {FIG}/")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
