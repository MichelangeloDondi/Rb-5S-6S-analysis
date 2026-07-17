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
    """C3: FWHM flat vs power; amplitude ~ P^2."""
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
    a1.set_title("C3a: linewidth flat vs power\n(ramp law predicts $\\leq$2% inflation)", fontsize=9)
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
        # (the honest bar; the stat-only column is a labelled diagnostic). See
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
    """The 'money figure': the four ΔF=0 components share ONE
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
                 "rises cleanly (β₈₅=β₈₇ tested ⇒ pooling licensed) — still a BOUND",
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
    a2.set_title("σ_laser(T) is MODEL-DEPENDENT: the free fit is flat (~1.7,\n"
                 "4 peaks agree ⇒ sharing validated, M4c); the tied fit's drop is\n"
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
    laser axis (outer teeth weak: they need second-order sideband pairs; the
    carrier-suppression trick applies on other blocks). RIGHT: the
    free-centres nonlinearity map (results/ruler_nlmap.csv) — the empirical
    bound (~0.3% per position) on scan nonlinearity AND any tooth-dependent
    pull (differential Stark, asymmetric-wing overlap), the ruler's
    common-mode-rejection receipt. Trace choice is deterministic: the first
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
    for n in range(-2, 3):
        tc = fit["t0_ms"] + n * fit["delta_ms"]
        ax.axvline(tc, color="#D55E00", lw=0.7, alpha=0.5)
        ax.annotate(f"$k={n}$", xy=(tc, ymax * 1.04), ha="center", fontsize=8,
                    color="#D55E00")
    ax.annotate("6.25 MHz per tooth (laser axis)\n= the frequency ruler",
                xy=(fit["t0_ms"] + 0.5 * fit["delta_ms"], ymax * 0.55),
                ha="center", fontsize=8)
    ax.set_xlabel("scan time (ms)")
    ax.set_ylabel("fluorescence (V)")
    ax.set_title("the scan carries its own calibration: five copies of the\n"
                 "same line via EOM sideband pairs", fontsize=9)
    ax.legend(fontsize=7, loc="upper right")

    nl = _rows("ruler_nlmap")
    pos = np.array([float(r["pos_ms"]) for r in nl])
    rr = np.array([float(r["rate_rel"]) for r in nl])
    er = np.array([float(r["rate_rel_err"]) for r in nl])
    ax2.errorbar(pos, rr, yerr=er, fmt="o", ms=3.5, color="#009E73", lw=1)
    ax2.axhline(1.0, color="k", lw=0.8)
    ax2.axhspan(0.996, 1.004, color="#009E73", alpha=0.10)
    ax2.set_xlabel("window position (ms)")
    ax2.set_ylabel("local rate / block rate")
    ax2.set_title("sweep linearity + any tooth-dependent\npull, bounded "
                  r"empirically ($\lesssim$0.4%)", fontsize=9)
    _save(fig, "fig8_ruler.png")


def main() -> int:
    fig_width_vs_density()
    fig_power_sweep()
    fig_transit_mc()
    fig_amplitude_ratios()
    fig_pooled_width()
    fig_gamma_floor()
    fig_identifiability_profile()
    fig_ruler()
    print(f"wrote figures to {FIG}/")
    for p in sorted(FIG.glob("*.png")):
        print(f"  {p.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
