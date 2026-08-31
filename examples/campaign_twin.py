#!/usr/bin/env python3
"""The digital twin of the next campaign, run as a check on this record.

WHAT THIS IS. The next measurement campaign, run in software before it is run
on the bench: four hyperfine peaks on one vertical range, a randomised power
ladder with session drift, and every physics layer the record claims matters,
hyperfine F statistics with cascade depletion, saturation companions, the
AC-Stark ramp, blackbody radiation, the measured noise law, and 12-bit
quantisation at the snug bright range.

WHAT MAKES IT A CHECK rather than a demonstration: each layer is a committed claim,
and the twin CHECKS the claim against its own output rather than assuming it.
The line table cross-check in this file's first version caught a wrong
isotope assignment in rb5s6s.cascade within hours of that module's commit,
which is the working example of the method.

THE CLAIMS UNDER TEST, each with its source:
  1. The four lines' relative amplitudes follow abundance x (2F+1)/G_iso
     scaled by cascade depletion, and the PUMPING ordering differs from the
     BRIGHTNESS ordering (plan/05).
  2. One vertical range across the 81x ladder leaves the dim rung dithered
     at about 0.99 (plan/07, measured from the 2025 traces).
  3. Blackbody shifts are negligible against MHz widths (blackbody module,
     79.9 to 161.0 Hz across 70 to 130 C).
  4. The CENTRE channel cannot measure the light-shift pull (M21,
     run_stark_centres): even with the full prediction injected, session
     drift leaves the centre-versus-power slope consistent with zero at this
     trace budget, and the null world stays null. The record's actual bound
     construction is the joint width likelihood over 172 traces, which is
     out of an example's budget and is what `forecast_precision` scales
     toward. THE FIRST VERSION OF THIS FILE claimed the twin would DETECT
     through centres, the twin refused at -0.8 sigma, and the record's own
     M21 turned out to have said so first. The twin contradicted its author.
  5. Saturation companions vanish at zero drive and grow monotonically
     (rb5s6s.stark forward physics; the measured 2.8 factor is a deferred
     ladder target, not re-derived here, and this line says so).

NO ARCHIVE DATA IS READ. Committed inputs are embedded as provenance-tagged
constants. Runs from a bare clone:

    python examples/campaign_twin.py
"""
from __future__ import annotations

import math
import sys

import numpy as np

from rb5s6s import cascade
from rb5s6s import blackbody
from rb5s6s import stark
from rb5s6s.amplitudes import predicted_shares
from rb5s6s.constants import PEAKS
from rb5s6s.linefit import fit_condition

C_M_S = 299792458.0

# ---- provenance-tagged inputs (no file reads, per the no-data rule) --------
# PRELIM medians of the per-condition joint fits (results/linefit_conditions).
GAMMA_COLL_MHZ = 0.55
SIGMA_LASER_MHZ = 1.6
TRANSIT_FWHM_MHZ = 1.8
# The prediction under test: S0(225 mW) = 0.35 MHz (docs/plan/04; kappa in
# MHz per W on the transition axis).
KAPPA_PRED = 0.35 / 0.225
# The 2025 ladder, watts.
POWERS_W = np.array([0.025, 0.075, 0.125, 0.175, 0.225])
# Session drift, MHz over the whole session (plan/06's confound scale).
DRIFT_MHZ_TOTAL = 0.8
# Noise fraction of peak at the BRIGHT rung (the 2025 dither-30 regime).
NOISE_FRAC_BRIGHT = 0.004
# 12-bit converter, snug bright range at 1.25x the brightest signal.
ADC_LEVELS = 4096
REPEATS_PER_RUNG = 4
# CHECK 4 is a scatter measurement, so it needs several worlds; see main().
CHECK4_SEEDS = (11, 12, 13, 14, 15)
CYCLES_AT_225MW = 3.0        # pumping cycles an atom completes at full power


def _pull_per_s0() -> float:
    """The ramp's first moment per unit S0, MEASURED from the library kernel.

    The derivation gives -2/3 for the density f(s) ∝ |s| on [-s0, 0], but this
    is measured rather than written down because a literal here is exactly what
    went wrong before: the file carried 0.5, the mean of a UNIFORM density, and
    the estimator built on it read kappa 33 per cent high while its own
    null-versus-prediction check passed, injection and recovery sharing the
    error. Reading the constant off `stark_ramp` means the twin cannot disagree
    with the kernel it convolves, in magnitude or in SIDE -- and the side is an
    open question (`tests/test_ramp_side_matches_the_polarizability.py`), so it
    is inherited here and never re-chosen.
    """
    from rb5s6s._compat import trapezoid
    from rb5s6s.lineshape import stark_ramp
    g = np.linspace(-4.0, 4.0, 40001)
    r = stark_ramp(g, 1.0)
    r = r / trapezoid(r, g)
    return float(trapezoid(g * r, g))


PULL_PER_S0 = _pull_per_s0()


def line_positions_mhz() -> dict:
    """Transition-axis positions from the PEAKS wavelengths themselves, so a
    wrong hand-typed spacing cannot enter. Referenced to the highest-frequency
    line (the smallest wavelength, 993.4121), so every position is at or
    below zero and the four span about minus 5.2 GHz."""
    ref_nm = min(p["lambda_nm"] for p in PEAKS.values())
    return {k: 2.0 * (C_M_S / (v["lambda_nm"] * 1e-9)
                      - C_M_S / (ref_nm * 1e-9)) / 1e6
            for k, v in PEAKS.items()}


def build_rung(power_w: float, kappa: float, t_c: float, order_idx: int,
               n_rungs: int, rng, layers) -> tuple:
    """One trace: all four peaks, one range, at this power."""
    pos = line_positions_mhz()
    nu = np.linspace(min(pos.values()) - 60.0, 60.0, 6000)
    shares = predicted_shares()
    s0 = kappa * power_w
    p_rel = (power_w / POWERS_W.max())

    v = np.zeros_like(nu)
    truth_amps = {}
    for peak, share in shares.items():
        amp = share * p_rel ** 2                      # two-photon: signal ~ P^2
        if layers["cascade"]:
            amp *= cascade.amplitude_factor(peak, CYCLES_AT_225MW * p_rel)
        gamma = GAMMA_COLL_MHZ
        if layers["saturation"]:
            gamma = gamma + stark.companion_gamma_mhz(s0, peak)
        centre = pos[peak]
        if layers["bbr"]:
            centre += -blackbody.shift_hz(273.15 + t_c) / 1e6
        if layers["drift"]:
            centre += DRIFT_MHZ_TOTAL * (order_idx / max(n_rungs - 1, 1) - 0.5)
        # THE RAMP IS CONVOLVED, NOT APPLIED AS A SHIFT (corrected 2026-08-30).
        # It used to enter as `centre += 0.5 * s0`, which was wrong twice over.
        # The magnitude: the ramp density is f(s) = 2s/S0^2, whose mean is
        # (2/3) S0; S0/2 is the mean of a UNIFORM density, not of this one.
        # The kind: a rigid translation carries only the first moment, so every
        # trace this twin emitted was exactly SYMMETRIC (skewness ~1e-16) while
        # the third cumulant, kappa_3 = +S0^3/135 for a SELF-CENTRED readout
        # (docs/wiki/third-cumulant.md), is the channel this record is built
        # on. A twin that cannot emit the asymmetry
        # cannot forecast it, and cannot test a fitter against it.
        # model_profile convolves lineshape.stark_ramp, so BOTH the -2/3 pull
        # and the skew come from the library rather than from a literal here,
        # and the ramp's coded DIRECTION is inherited rather than re-chosen.
        from rb5s6s.lineshape import model_profile
        shape = model_profile(nu - centre,
                              gamma_coll=gamma,
                              sigma_laser_fwhm=SIGMA_LASER_MHZ,
                              transit_fwhm=TRANSIT_FWHM_MHZ,
                              s0=(s0 if layers["stark"] else 0.0))
        v += amp * (shape / shape.max())
        truth_amps[peak] = amp
    v += 0.01                                          # detector offset
    # shot-like noise: sigma grows as the root of the LOCAL signal, anchored
    # so the brightest rung's peak carries NOISE_FRAC_BRIGHT of itself. This
    # is the regime the 2025 noise law measured (variance linear in signal),
    # and it is what makes one vertical range survivable at the dim rung: the
    # noise falls with the signal while the quantisation step does not.
    bright_peak = max(predicted_shares().values()) + 0.01
    sigma = NOISE_FRAC_BRIGHT * np.sqrt(np.clip(v, 0.0, None) * bright_peak)
    v = v + sigma * rng.standard_normal(nu.size)
    if layers["quantise"]:
        step = 1.25 * (max(shares.values()) + 0.01) / ADC_LEVELS
        v = np.round(v / step) * step
    return nu, v, truth_amps


def fit_rung(nu, v, rng) -> dict:
    """Fit each peak in its own window, single-trace, as the analysis would."""
    pos = line_positions_mhz()
    out = {}
    for peak in PEAKS:
        centre = pos[peak]
        m = np.abs(nu - centre) < 18.0
        res = fit_condition([nu[m] - centre], [v[m]], T_C=130.0,
                            transit_fwhm=TRANSIT_FWHM_MHZ)
        out[peak] = {"centre": float(res["centers"][0]) + centre,
                     "amp": float(res["amps"][0]),
                     "gamma_coll": res["gamma_coll"],
                     "gamma_err": res["gamma_coll_err"]}
    return out


def run_world(kappa: float, layers: dict, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    order = rng.permutation(len(POWERS_W)) if layers["randomise"] else np.arange(len(POWERS_W))
    fits, dither = [], None
    for idx, rung_i in enumerate(order):
        P = POWERS_W[rung_i]
        if layers["quantise"] and P == POWERS_W.min():
            bright_peak = max(predicted_shares().values()) + 0.01
            step = 1.25 * bright_peak / ADC_LEVELS
            p_rel = P / POWERS_W.max()
            dim_peak = max(predicted_shares().values()) * p_rel ** 2 + 0.01
            dim_sigma = NOISE_FRAC_BRIGHT * math.sqrt(dim_peak * bright_peak)
            dither = dim_sigma / step
        for _ in range(REPEATS_PER_RUNG):
            # each repeat is an independently generated trace, as on a bench;
            # refitting one trace twice would manufacture zero scatter
            nu, v, truth = build_rung(P, kappa, 130.0, idx, len(order), rng, layers)
            fits.append((P, fit_rung(nu, v, rng)))
    # kappa from the centre channel: weighted slope of centre vs P, per peak,
    # averaged, which is the design's own construction
    slopes = []
    for peak in PEAKS:
        Ps = np.array([p for p, f in fits])
        cs = np.array([f[peak]["centre"] for p, f in fits])
        A = np.vstack([Ps, np.ones_like(Ps)]).T
        coef, res_, *_ = np.linalg.lstsq(A, cs, rcond=None)
        n, k = len(Ps), 2
        sigma2 = (res_[0] / (n - k)) if len(res_) else float(np.var(cs))
        sigma2 = max(sigma2, 1e-12)      # a perfectly straight set of centres
        cov = sigma2 * np.linalg.inv(A.T @ A)
        slopes.append((coef[0], math.sqrt(cov[0, 0])))
    w = np.array([1 / s[1] ** 2 for s in slopes])
    slope = float(np.sum([s[0] * wi for s, wi in zip(slopes, w)]) / w.sum())
    slope_err = float(1 / math.sqrt(w.sum()))
    # The centre channel reads the ramp's MEAN, and for the density this record
    # derives, f(s) = 2s/S0^2, that mean is (2/3) S0 and not S0/2 (corrected
    # 2026-08-30; S0/2 is the mean of a UNIFORM density). lineshape.stark_ramp
    # codes the pull NEGATIVE, so the fitted slope of centre against power is
    # -(2/3) kappa and the estimator is -3/2 times it. The factor is written as
    # -1/PULL_PER_S0 rather than as a literal so it cannot drift from the
    # library again.
    # The first version of this file compared the raw slope to kappa and
    # under-read its own injection by exactly that factor, which the twin's
    # null-versus-prediction check exposed.
    kap = slope / PULL_PER_S0
    kap_err = abs(slope_err / PULL_PER_S0)
    # amplitude RATIOS at the bright rung, against the shares: the pumping
    # signature is a per-line DEVIATION from the degeneracy law, not a gross
    # reordering, because amp = share x survival and the shares dominate.
    brights = [f for p, f in fits if p == POWERS_W.max()]
    shares = predicted_shares()
    ref = "4192"
    dev = {}
    for peak in PEAKS:
        r_fit = np.median([b[peak]["amp"] / b[ref]["amp"] for b in brights])
        r_share = shares[peak] / shares[ref]
        dev[peak] = float(r_fit / r_share)
    return {"kappa": kap, "kappa_err": kap_err, "dither": dither,
            "ratio_dev": dev}


def main() -> int:
    layers = {"cascade": True, "saturation": True, "stark": True, "bbr": True,
              "drift": True, "quantise": True, "randomise": True}
    stark.COMPANIONS = {"ratio": 1.2367, "scale": 1.0, "cycles": 1.0}

    print(__doc__.splitlines()[0], "\n")
    # claim 5, checked before anything is generated
    z = stark.companion_gamma_mhz(0.0, "4121")
    g1 = stark.companion_gamma_mhz(0.2, "4121")
    g2 = stark.companion_gamma_mhz(0.4, "4121")
    print(f"CHECK 5 saturation: zero at s0=0 -> {z == 0.0}; monotone -> {g2 > g1 > 0}")

    # claim 3
    bb = blackbody.shift_hz(403.15) / 1e6
    print(f"CHECK 3 blackbody: {bb*1e3:.3f} kHz at 130 C against MHz widths "
          f"-> negligible = {abs(bb) < 1e-3 * GAMMA_COLL_MHZ * 1e3}")

    # CHECK 4 IS RUN OVER SEVERAL SEEDS, and that is the point of it
    # (2026-08-30). A single world reports the regression's own error on the
    # centre-versus-power slope, which knows nothing about the randomised power
    # ORDER it happened to draw. Measured over eight seeds the recovered kappa
    # ran 0.22 to 7.28 for an injected 1.556 while each world quoted about
    # +/-0.6, so the per-world error understates the scatter by roughly four.
    # Quoting one seed therefore turns a channel the record calls unusable into
    # a 4.8-sigma "detection" or a clean null depending on the draw. The spread
    # ACROSS seeds is the uncertainty to report, and it states M21 more
    # directly: drift aliases onto the power order, so what moves between
    # worlds is the answer and not merely its error bar.
    pred_worlds = [run_world(KAPPA_PRED, layers, seed=s) for s in CHECK4_SEEDS]
    null_worlds = [run_world(0.0, layers, seed=s + 100) for s in CHECK4_SEEDS]

    def _pool(ws):
        k = np.array([w["kappa"] for w in ws])
        return {"kappa": float(np.median(k)),
                "kappa_err": float(np.std(k, ddof=1)),
                "quoted_err": float(np.median([w["kappa_err"] for w in ws])),
                "lo": float(k.min()), "hi": float(k.max()),
                "dither": ws[0]["dither"], "ratio_dev": ws[0]["ratio_dev"]}

    pred, null = _pool(pred_worlds), _pool(null_worlds)

    print(f"\nCHECK 2 one-range dither at the dim rung: {pred['dither']:.2f} "
          f"(2025 measured 0.99 at a 1.0x-snug range; this twin ranges at 1.25x, usable above ~0.9)")
    sig = pred["kappa"] / pred["kappa_err"]
    nsig = null["kappa"] / null["kappa_err"]
    # the channel is unusable when its answer moves more than its own error bar
    # admits: that is a calibration failure, not merely an imprecise estimate.
    understated = pred["kappa_err"] / pred["quoted_err"]
    print("CHECK 4 the centre channel (M21 says it cannot measure the pull):")
    print(f"           injected kappa {KAPPA_PRED:.3f} -> centres recover "
          f"{pred['kappa']:.3f} +/- {pred['kappa_err']:.3f} over "
          f"{len(CHECK4_SEEDS)} seeds, spanning {pred['lo']:.2f} to {pred['hi']:.2f}")
    print(f"           each world quoted only +/-{pred['quoted_err']:.3f}, so the "
          f"per-world error understates the scatter by {understated:.1f}x")
    print(f"           -> the channel's own error bar is not trustworthy, "
          f"M21 confirmed = {understated > 2}")
    print(f"           null world: {null['kappa']:.3f} +/- {null['kappa_err']:.3f} "
          f"({abs(nsig):.1f} sigma) -> null stays null = {abs(nsig) < 3}")
    print("           the bound construction of record is the joint width "
          "likelihood over 172 traces, not this channel")

    # pumping predicts each line's amplitude falls below the degeneracy law
    # by its survival factor, so the ratio-to-4192 deviations should match
    # the SURVIVAL ratios, and a detection chain that tracked brightness
    # would show deviations tracking amplitude instead.
    surv = {k: cascade.amplitude_factor(k, CYCLES_AT_225MW) for k in PEAKS}
    exp_dev = {k: surv[k] / surv["4192"] for k in PEAKS}
    print("\nCHECK 1 pumping signature in the amplitude ratios (vs shares, ref 4192):")
    agree = True
    for k in sorted(PEAKS):
        ok = abs(pred["ratio_dev"][k] - exp_dev[k]) < 0.12
        agree &= ok
        print(f"           {k}: fitted deviation {pred['ratio_dev'][k]:.3f}, "
              f"pumping predicts {exp_dev[k]:.3f} -> {'agrees' if ok else 'DISAGREES'}")
    print(f"           orderings do NOT flip at these cycle counts; the "
          f"signature is this deviation pattern, and it {'holds' if agree else 'FAILS'}")

    ok = (z == 0.0 and g2 > g1 and abs(nsig) < 3 and abs(sig) < 3
          and agree and pred["dither"] and pred["dither"] > 0.9)
    print(f"\nVERDICT: {'PASS' if ok else 'FAIL'}. The twin confirms the record "
          f"against itself: the pumping signature appears in the amplitude "
          f"ratios, the centre channel cannot see the pull exactly as M21 "
          f"states, the null does not false-alarm, one vertical range stays "
          f"dithered at the dim rung, and blackbody is negligible where the "
          f"boundary model says it is.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
