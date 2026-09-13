#!/usr/bin/env python3
"""The four peaks as a two-by-two design: isotope by hyperfine level, three
contrasts of the fitted widths per condition, each against its prediction.

WHY THIS EXISTS (owner, 2026-09-13: "exploit all the 4 peaks, each one with
its own isotope, its own relative abundance, its own F statistics, its own
saturation, its own m_F statistics"). Every condition of the archive was fitted
per peak (`results/linefit_conditions.csv`: 4121 and 4207 are 87Rb F = 1 and
2, 4154 and 4192 are 85Rb F = 2 and 3), and the four widths at one (T, P) form
a two-by-two table whose contrasts cancel what the peaks share and keep what
differs:

  isotope contrast   mean(85Rb) - mean(87Rb): the transit alone differs, by the
                     root of the mass ratio (85Rb wider by 1.17 per cent of the
                     transit). the van der Waals term is one C6 for both, the
                     laser and the Lorentzian floor are shared;
  F contrast, 87Rb   w(F=2) - w(F=1): the pumping companion differs by the
                     branching difference times the saturation width, the
                     higher-branching line (F=1, 0.372) the wider, so the
                     contrast is negative and grows as P^2. spin exchange
                     differs by an F-dependent coefficient and grows as N;
  F contrast, 85Rb   w(F=3) - w(F=2): the same with 0.248 against 0.348;
  interaction        the difference of the two F contrasts, which every term
                     shared by the isotopes cancels.

The predictions read the record's own terms: the transit at the adopted
waist (`constants.W0_MEASURED_M`, `transit_fwhm_from_w0`), the saturation
companion (`fullmodel.saturation_companion_mhz` at Omega tied to S0) and
`cascade.BRANCHING_F`. Where the record carries no coefficient (spin exchange,
hyperfine-changing collisions) the row says so and the contrast is reported
as a bound on that term. Every value carries the error the per-peak fits
carry, propagated. the pooled rows weight by inverse variance.

STATUS. The widths are the record's fits and the predictions are the record's
terms, so every row is DIAGNOSTIC: what the two-by-two says, not a new
measurement of a term.
"""
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s.cascade import BRANCHING_F, amplitude_factor           # noqa: E402
from rb5s6s.platforms import PLATFORMS, excitation_rate_per_atom   # noqa: E402
from rb5s6s._compat import trapezoid                              # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402

ISO = {p: K.PEAKS[p]["isotope"] for p in K.PEAKS}
F = {p: K.PEAKS[p]["F"] for p in K.PEAKS}
M87, M85 = K.M_RB87_KG, K.M_RB85_KG


def _rows():
    with (_CFG.RESULTS_DIR / "linefit_conditions.csv").open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)]


OMEGA_OVER_S0 = 1.2367     # the two-photon Rabi frequency over the light shift at this package's polarizability (fullmodel.py, hyperpolarizability.py)


def _transit_mhz(T_C: float) -> float:
    return float(K.transit_fwhm_from_w0(K.W0_MEASURED_M, T_C, isotope=87))


def _sat_width_mhz(P_W: float, peak: str) -> float:
    """The saturation-plus-pumping companion's width at this power for the
    adopted waist and THIS peak's branching, from the record's own terms."""
    from rb5s6s.fullmodel import saturation_companion_mhz
    from rb5s6s.lineshape import stark_shift_S0_mhz
    s0 = float(stark_shift_S0_mhz(P_W, K.W0_MEASURED_M))
    return float(saturation_companion_mhz(OMEGA_OVER_S0 * s0, peak=peak))


def _cycles_per_crossing(P_W: float, w0_m: float, T_C: float = 130.0) -> float:
    """Excitation cycles an atom completes on a central chord of the beam.

    THE SECOND FACE OF THE F-DEPENDENT TERM (owner, 2026-09-13): F is not
    conserved in the cascade, so under continuous excitation the driven level
    is depleted per crossing (cascade.amplitude_factor) and the deviation of
    the four amplitudes from the thermal law abundance x (2F+1)/G is the same
    pumping term the width contrasts read, with BRANCHING_F as its coefficient.
    Its size is set by the cycles per crossing: the on-axis rate of the record
    (platforms.excitation_rate_per_atom, the cascade's saturation carried)
    integrated along a chord through the centre at the mean transverse speed.

    THE CHORD INTEGRAL CARRIES THE SATURATION AND THE CLOSED FORM DID NOT
    (corrected 2026-09-13). `excitation_rate_per_atom` is the ON-AXIS
    rate and its own docstring says the profile average is not that number
    times a volume, because the wings are unsaturated. The first version here
    multiplied that saturated on-axis rate by the WEAK-DRIVE profile integral
    int exp(-4 v^2 t^2 / w0^2) dt = sqrt(pi) w0 / (2 v), which under-counts
    wherever the drive saturates: measured, by 1.32 at 25 microns and 1.77 at
    16 at 225 mW, and the committed row FELL from 25 to 16 microns where the
    physics rises. What runs now is the integral of the saturated rate itself,
    the local drive scaled as P exp(-2 v^2 t^2 / w0^2) so that the saturation
    parameter s, which goes as P^2, carries the I^2 profile and the cascade
    denominator is evaluated at each point. It reduces to the closed form in
    the weak-drive limit, which is the plant, and it goes as P^2 / w0^3 only
    there: at a tight waist the exponent is softer because the core saturates.
    Off-centre chords accumulate fewer, so this is the largest chord's count
    and an upper bound on the transit average. The campaign twin's
    CYCLES_AT_225MW of 3.0 is not derived from this and the master plan
    carries the reconciliation as owed.

    The quadrature states its regime and self-checks by halving: a cell whose
    answer moves by more than a part in a million on the halved grid raises
    rather than publishing an unconverged number.
    """
    import dataclasses
    plat = dataclasses.replace(PLATFORMS["cell_130C"], w0_m=w0_m, temperature_k=T_C + 273.15)
    v_mean_2d = np.sqrt(np.pi * K.K_B_J_PER_K * (T_C + 273.15) / (2.0 * K.M_RB87_KG))
    t_edge = 3.0 * w0_m / v_mean_2d          # three waists of chord, the wings carried
    t_grid = np.linspace(-t_edge, t_edge, 4001)
    local_w = P_W * np.exp(-2.0 * (v_mean_2d * t_grid) ** 2 / w0_m ** 2)
    rate = np.array([excitation_rate_per_atom(float(p), plat, rho=0.94)
                     for p in local_w])
    fine = float(trapezoid(rate, t_grid))
    half = float(trapezoid(rate[::2], t_grid[::2]))   # the SAME grid, every other point
    if abs(fine - half) > 1e-6 * abs(fine):
        raise SystemExit(
            f"run_four_peak_contrasts: the chord quadrature is unconverged at "
            f"P = {P_W} W, w0 = {w0_m} m ({fine:.6g} against {half:.6g} on the "
            "halved grid). Refuse the cell rather than publish it.")
    return fine


def _amplitude_face():
    """Rows for the amplitude face: the predicted deviation of each isotope's
    within-isotope ratio from the thermal law, per rung at the record's waist
    and along the campaign's waist ladder, and the measured deviation from the
    canonical RF-off peak heights at 130 C with its statistical error, the
    record's between-block systematic on the ratio quoted beside it."""
    import statistics as st
    from collections import defaultdict
    rows = []
    pairs = {"87Rb": ("4207", "4121", 5.0 / 3.0), "85Rb": ("4192", "4154", 7.0 / 5.0)}
    powers = (0.025, 0.075, 0.125, 0.175, 0.225)
    for P in powers:
        cyc = _cycles_per_crossing(P, K.W0_MEASURED_M)
        rows.append(["cycles_per_crossing_axis", f"P{P*1e3:g}_w64", f"{cyc:.4f}", "", "",
                     "excitation cycles on a central chord at 130 C: the saturated rate integrated along the chord, the local drive scaled as P exp(-2 v^2 t^2 / w0^2). P^2 / w0^3 in the weak-drive limit only, the core saturating at a tight waist", ""])
        for iso, (hi, lo, thermal) in pairs.items():
            dev = np.log(amplitude_factor(hi, cyc) / amplitude_factor(lo, cyc))
            rows.append(["amplitude_face_predicted", f"{iso}_P{P*1e3:g}_w64", f"{dev:.5f}", "", "ln",
                         f"predicted ln({hi}/{lo}) minus ln({thermal:.3f}): the higher-branching line ({lo}, BRANCHING_F {BRANCHING_F[lo]:.3f}) is depleted more, so the ratio sits ABOVE the thermal law by this much", ""])
    for w_um in (40.0, 25.0, 16.0):
        cyc = _cycles_per_crossing(0.225, w_um * 1e-6)
        rows.append(["cycles_per_crossing_axis", f"P225_w{w_um:g}", f"{cyc:.3f}", "", "", "the same at the campaign's waists, 225 mW", ""])
        for iso, (hi, lo, thermal) in pairs.items():
            dev = np.log(amplitude_factor(hi, cyc) / amplitude_factor(lo, cyc))
            rows.append(["amplitude_face_predicted", f"{iso}_P225_w{w_um:g}", f"{dev:.4f}", "", "ln", "the campaign's reach on this face at that waist", ""])
    heights = defaultdict(list)
    with (_CFG.RESULTS_DIR / "qc_metrics.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["role"] == "p_sweep" and r["flag"] == "canonical" and r["rf_on"] == "False":
                heights[(r["peak"], float(r["power_mW"]))].append(float(r["height_v"]))
    syst = {}
    with (_CFG.RESULTS_DIR / "amplitude_ratios.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["T"] == "130":
                syst[r["ratio"]] = float(r["syst_between_block"]) / float(r["predicted"])
    for P in powers:
        for iso, (hi, lo, thermal) in pairs.items():
            a, b = heights.get((hi, P * 1e3)), heights.get((lo, P * 1e3))
            if not a or not b:
                continue
            la, lb = np.log(a), np.log(b)
            dev = float(np.mean(la) - np.mean(lb) - np.log(thermal))
            err = float(np.hypot(st.stdev(la) / np.sqrt(len(la)), st.stdev(lb) / np.sqrt(len(lb))))
            v, es = pm_cells(dev, err)
            sy = syst.get(f"{hi}/{lo}", float("nan"))
            rows.append(["amplitude_face_measured", f"{iso}_P{P*1e3:g}", v, es, "ln",
                         f"ln of the median-free mean of the canonical RF-off peak heights, {hi} over {lo}, minus the thermal law, at 130 C. the statistical error only, and amplitude_ratios.csv's between-block systematic on this ratio is {sy:.2f} in the log, which is the bar on the archive", ""])
    return rows


def main() -> int:
    rows = _rows()
    out = [["quantity", "key", "value", "err", "unit", "note", "status"]]
    by_cond: dict = {}
    for r in rows:
        if not (r.get("T") and r.get("total_fwhm") and r.get("total_fwhm_err")):
            continue                                   # summary rows carry no condition
        # A t_sweep row carries a BLANK power: the manifest's convention for the maximum
        # power (225 mW), which is what makes the design an L with a shared corner.
        by_cond.setdefault((r["role"], float(r["T"]), float(r["P"]) if r.get("P") else None), {})[r["peak"]] = r
    p_blank = max(P for (_, _, P) in by_cond if P is not None)
    by_cond = {(role, T, P if P is not None else p_blank): v for (role, T, P), v in by_cond.items()}
    pooled = {"isotope": [], "F87": [], "F85": [], "interaction": []}
    pooled_pred = {"isotope": [], "F87": [], "F85": [], "interaction": []}
    # THE L'S TWO ARMS, POOLED SEPARATELY: the power arm (every p_sweep condition at 130 C)
    # and the temperature arm (the t_sweep rows plus the 130 C corner at the maximum power)
    p_max = max(P for (_, _, P) in by_cond)
    arm_of = lambda role, T, P: ("power_arm" if role == "p_sweep" else "temperature_arm") if not (role == "p_sweep" and abs(P - p_max) < 1e-9) else "both_arms"
    pooled_arm = {a: {k: [] for k in pooled} for a in ("power_arm", "temperature_arm")}
    for (role, T, P), peaks in sorted(by_cond.items()):
        if set(peaks) != {"4121", "4154", "4192", "4207"}:
            continue
        w = {p: float(peaks[p]["total_fwhm"]) for p in peaks}
        e = {p: float(peaks[p]["total_fwhm_err"]) for p in peaks}
        c_iso = (w["4154"] + w["4192"]) / 2 - (w["4121"] + w["4207"]) / 2
        e_iso = 0.5 * np.sqrt(sum(e[p] ** 2 for p in peaks))
        c_f87, e_f87 = w["4207"] - w["4121"], np.hypot(e["4207"], e["4121"])
        c_f85, e_f85 = w["4192"] - w["4154"], np.hypot(e["4192"], e["4154"])
        c_int, e_int = c_f87 - c_f85, np.hypot(e_f87, e_f85)
        tr = _transit_mhz(T)
        # the transit goes as the thermal speed, 1/sqrt(m): the lighter 85Rb is faster and wider
        p_iso = tr * (np.sqrt(M87 / M85) - 1.0)
        P_W = P / 1000.0 if P > 5 else P
        comp = {pk: _sat_width_mhz(P_W, pk) for pk in peaks}   # the companion per peak carries that peak's branching
        p_f87 = comp["4207"] - comp["4121"]
        p_f85 = comp["4192"] - comp["4154"]
        p_int = p_f87 - p_f85
        key = f"{role}_T{T:g}_P{P:g}"
        for name, c, ee, pr in (("isotope", c_iso, e_iso, p_iso), ("F87", c_f87, e_f87, p_f87), ("F85", c_f85, e_f85, p_f85), ("interaction", c_int, e_int, p_int)):
            v, es = pm_cells(c, ee)
            pv = "" if not np.isfinite(pr) else f"{pr:.4f}"
            pull = "" if not np.isfinite(pr) else f"{(c - pr) / ee:+.2f}"
            out.append([f"contrast_{name}", key, v, es, "MHz", f"measured width contrast. predicted {pv or 'not carried'} from the record's terms. pull {pull or 'n/a'}", ""])
            pooled[name].append((c, ee)); pooled_pred[name].append(pr)
            arm = arm_of(role, T, P)
            for a in (("power_arm", "temperature_arm") if arm == "both_arms" else (arm,)):
                pooled_arm[a][name].append((c, ee))
    for name, vals in pooled.items():
        c = np.array([v for v, _ in vals]); s = np.array([e for _, e in vals])
        wgt = 1 / s ** 2
        m = float(np.sum(wgt * c) / np.sum(wgt)); em = float(1 / np.sqrt(np.sum(wgt)))
        chi2 = float(np.sum(wgt * (c - m) ** 2)); n = len(c)
        pr = np.array(pooled_pred[name], dtype=float)
        pr_m = float(np.nanmean(pr)) if np.isfinite(pr).any() else float("nan")
        v, es = pm_cells(m, em)
        out.append([f"contrast_{name}", "pooled", v, es, "MHz",
                    f"inverse-variance pool over {n} conditions. chi2 of the pool {chi2:.1f} for {n - 1} dof (a chi2 far above it says the contrast depends on the condition, which is the P^2 or N signature). predicted mean {'' if not np.isfinite(pr_m) else f'{pr_m:.4f}'}", ""])
    for a, sets in pooled_arm.items():
        for name, vals in sets.items():
            if not vals:
                continue
            c = np.array([v for v, _ in vals]); sg = np.array([e for _, e in vals]); wgt = 1 / sg ** 2
            m = float(np.sum(wgt * c) / np.sum(wgt)); em = float(1 / np.sqrt(np.sum(wgt))); chi2 = float(np.sum(wgt * (c - m) ** 2))
            v, es = pm_cells(m, em)
            out.append([f"contrast_{name}", f"pooled_{a}", v, es, "MHz",
                        f"inverse-variance pool over the {a.replace('_', ' ')} of the L ({len(c)} conditions, the 130 C corner at the maximum power in both arms). chi2 {chi2:.1f} for {len(c) - 1} dof", ""])
    out.extend(_amplitude_face())
    out.append(["predicted_isotope_contrast", "law", f"{np.sqrt(M87 / M85) - 1:.5f}", "", "", "85Rb transit over 87Rb transit minus one, the root of the mass ratio", ""])
    out.append(["branching_difference", "87Rb_F2_minus_F1", f"{BRANCHING_F['4207'] - BRANCHING_F['4121']:.4f}", "", "", "cascade.BRANCHING_F", ""])
    out.append(["branching_difference", "85Rb_F3_minus_F2", f"{BRANCHING_F['4192'] - BRANCHING_F['4154']:.4f}", "", "", "cascade.BRANCHING_F", ""])
    out_path = _CFG.RESULTS_DIR / "four_peak_contrasts.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(out)
    print(f"wrote {out_path} ({len(out) - 1} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
