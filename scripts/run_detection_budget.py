#!/usr/bin/env python
"""M46: the detection budget. The archive's own photoelectron rate against the
chain the bench implies, and the waist exponent each collection geometry
realises.

WHAT THIS ANSWERS. The bench facts (owner, 2026-09-13): the 795 nm cascade
photons are collected by an f = 18 +- 1 mm lens at 50 +- 5 mm from a 3 x 12 mm
cathode of quantum efficiency 6 +- 1 per cent. Read as a channel, the absolute
fluorescence carries the waist through the two-photon rate, and the question
is WHICH power of the waist the archive's geometry realises, and how far the
measured rate sits from the prediction, so that the channel's reach is a
number and not a hope.

THE VOLUME INTEGRAL, derived rather than asserted. With
I(r, z) = (2P / pi w^2) exp(-2 r^2 / w^2) and w^2 = w0^2 (1 + z^2 / z_R^2),
the weak-drive two-photon rate is proportional to I^2, and

    int 2 pi r dr I^2 = P^2 / (pi w^2)                          (radial, exact)
    int_{-L/2}^{L/2} dz P^2 / (pi w0^2 (1 + z^2 / z_R^2))
        = (P^2 z_R / (pi w0^2)) 2 arctan(L / 2 z_R) = (P^2 / lambda) 2 arctan(x)

with x = L / (2 z_R) and z_R = pi w0^2 / lambda. The prefactor carries NO
waist: every waist dependence of the integrated weak-drive signal sits in
2 arctan(x), whose logarithmic slope in the waist is

    d ln(2 arctan x) / d ln w0 = -2 x / ((1 + x^2) arctan x)

(x goes as w0^-2), which runs from -2 where the collected length is short
against the Rayleigh range to 0 where the whole Rayleigh range sits inside
the window. The on-axis rate PER ATOM goes as I0^2, so as w0^-4. the mode
holds w0^2 L atoms, which is where two of the four powers go. Saturation
weakens the exponent further, so the predicted rate uses the strong-drive
integral of `platforms.events_per_s_profile` over the COLLECTED length, and
the saturated exponent is measured on it numerically beside the analytic
weak-drive one.

THE MEASURED RATE, from the noise law. `results/noise_model.csv` fits
sigma^2(V) = a^2 + b V per condition. Photoelectron shot noise through a
photomultiplier of gain G into a transimpedance R reads V = G e R n and
sigma^2 = (G e R)^2 F n 2B, with F the excess-noise factor and B the noise
bandwidth, so b = 2 G e R F B and the photoelectron rate per volt is
n / V = 2 F B / b, with neither G nor R needed. B is the boxcar's, 1 / (2 dt)
at the 0.5 ms stored spacing (docs/APPARATUS.md), 1 kHz. F is not on record
and enters as a named factor at 1 with its span stated. the noise module's
own statement that its absolute coefficients carry a method systematic of
1.5 to 2 is carried as a span on the measured rate.

WHAT IS OPEN and spanned rather than guessed: the lens's clear aperture
(three diameters spanned), the filter's transmission (at 1, its span
stated), the cathode's orientation (both), the excess-noise factor, the
retro ratio (0.7 to 1), the density law (two), and the D1 photons' own
trapping, whose optical depth over the standoff is computed and whose effect
on the collected fraction is not. Every one is a row.
"""
from __future__ import annotations

import csv
import dataclasses
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s.amplitudes import predicted_shares                     # noqa: E402
from rb5s6s.density import number_density_cm3                      # noqa: E402
from rb5s6s.detection import ir_branching_5p12                     # noqa: E402
from rb5s6s.platforms import PLATFORMS, events_per_s_profile, rayleigh_range_m   # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402

OUT = _CFG.RESULTS_DIR / "detection_budget.csv"
HEADER = ["quantity", "key", "value", "err", "unit", "note"]

# The bench facts, each with its source. The image distance's one-sigma is the
# owner's 2026-09-13 figure (5 mm); constants.COLLECTION_IMAGE_DIST_ERR_M still
# carries the 10 mm of 2026-09-04 and is not moved here, because the prediction
# band's committed cells rest on it (docs/plan/12 carries the discrepancy).
F_M, F_ERR_M = K.COLLECTION_LENS_F_M, K.COLLECTION_LENS_F_ERR_M
S_IMG_M, S_IMG_ERR_M = K.COLLECTION_IMAGE_DIST_M, 5e-3
QE, QE_ERR = 0.06, 0.01                     # owner, 2026-09-13: 8 per cent cathode, 6 +- 1 in the chain
CATHODE_M = {"along12": K.PMT_CATHODE_ALONG_BEAM_M,      # the 12 mm dimension along the beam, the record's reading
             "along3": 3e-3}                             # the 3 mm dimension along the beam, the owner's 2026-09-12 "portrait"   # datasheet TPMS1016E, 3 x 12 mm
APERTURES_MM = (6.0, 12.7, 25.4)            # the lens's clear aperture is not on record: spanned
DT_STORED_S = 0.5e-3                        # docs/APPARATUS.md, the stored spacing of the boxcar
B_HZ = 1.0 / (2.0 * DT_STORED_S)
RHO = 0.94                                  # the record's retro ratio; the span 0.7 to 1 is a row
T_C, P_W = 130.0, 0.225
W0_GRID_UM = (64.0, 40.0, 25.0, 16.0)
N_DRAWS = 4000


def aih_density_cm3(T_C: float) -> float:
    """Alcock, Itkin and Horrigan's liquid-rubidium law, log10 P/torr = 2.881 + 4.312 - 4040/T,
    as the density laws producer carries it, so the two producers agree by construction."""
    T = T_C + 273.15
    p_pa = 10 ** (2.881 + 4.312 - 4040.0 / T) * K.TORR_PA
    return p_pa / (K.K_B_J_PER_K * T) * 1e-6


def geometry(f_m: float, s_img_m: float, cathode_m: float, w0_m: float):
    """Object distance, magnification, collected length and its Rayleigh ratio."""
    s_obj = 1.0 / (1.0 / f_m - 1.0 / s_img_m)
    mag = s_img_m / s_obj
    L = cathode_m / mag
    z_r = rayleigh_range_m(w0_m)
    return s_obj, mag, L, z_r, L / (2.0 * z_r)


def weak_drive_exponent(x: float) -> float:
    """d ln(2 arctan x) / d ln w0 with x proportional to w0^-2: -2 x / ((1 + x^2) arctan x)."""
    return -2.0 * x / ((1.0 + x * x) * math.atan(x))


def solid_angle_fraction(aperture_m: float, s_obj_m: float) -> float:
    """Omega / 4 pi of a circular aperture of that diameter at the object distance."""
    theta = math.atan(0.5 * aperture_m / s_obj_m)
    return 0.5 * (1.0 - math.cos(theta))


def events_collected(P_w: float, w0_m: float, L_m: float, n_cm3: float, rho: float = RHO) -> float:
    """Excitations per second inside the collected length, saturation carried."""
    base = PLATFORMS["cell_130C"]
    plat = dataclasses.replace(base, w0_m=w0_m, length_m=L_m, density_cm3=n_cm3)
    return events_per_s_profile(P_w, plat, rho=rho)


def saturated_exponent(P_w: float, w0_m: float, cathode_m: float, n_cm3: float) -> float:
    """d ln(events) / d ln w0 on the strong-drive integral, by a central difference."""
    def ev(w):
        _, _, L, _, _ = geometry(F_M, S_IMG_M, cathode_m, w)
        return events_collected(P_w, w, L, n_cm3)
    h = 0.01
    return (math.log(ev(w0_m * (1 + h))) - math.log(ev(w0_m * (1 - h)))) / (math.log(1 + h) - math.log(1 - h))


def measured_rates():
    """Per p_sweep condition: the median peak height of its canonical RF-off traces, the
    noise law's b, and the photoelectron rate per volt 2 F B / b at F = 1."""
    heights = defaultdict(list)
    with (_CFG.RESULTS_DIR / "qc_metrics.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["role"] == "p_sweep" and r["flag"] == "canonical" and r["rf_on"] == "False":
                heights[(r["peak"], float(r["power_mW"]))].append(float(r["height_v"]))
    b_of = {}
    with (_CFG.RESULTS_DIR / "noise_model.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["role"] == "p_sweep":
                b_of[(r["peak"], float(r["power_mW"]))] = float(r["b_V"])
    out = {}
    for key, hs in heights.items():
        if key in b_of:
            h = float(np.median(hs)); b = b_of[key]
            out[key] = (h, float(np.std(hs, ddof=1) / math.sqrt(len(hs))), b, 2.0 * B_HZ / b)
    return out


def main() -> None:
    rng = np.random.default_rng(20260913)
    rows = []
    add = rows.append
    share = predicted_shares()
    n_steck = number_density_cm3(T_C)
    n_aih = aih_density_cm3(T_C)
    branching = ir_branching_5p12()
    w0 = K.W0_MEASURED_M

    # 1. the geometry and the exponents, at the record's waist and along the campaign's ladder
    for orient, cath in CATHODE_M.items():
        s_obj, mag, L, z_r, x = geometry(F_M, S_IMG_M, cath, w0)
        add(["object_distance", orient, f"{s_obj*1e3:.2f}", "", "mm", "1/(1/f - 1/s'), thin lens, the detector in focus"])
        add(["magnification", orient, f"{mag:.3f}", "", "", "s'/s"])
        add(["collected_length", orient, f"{L*1e3:.2f}", "", "mm", "the cathode's dimension along the beam over the magnification"])
        add(["collected_fraction", orient, f"{2*math.atan(x)/math.pi:.3f}", "", "", "2 arctan(L / 2 z_R) / pi, the ramp's axial weight inside the window. the record's prediction_band cell is the 12 mm reading"])
        for w_um in W0_GRID_UM:
            wm = w_um * 1e-6
            _, _, Lw, z_rw, xw = geometry(F_M, S_IMG_M, cath, wm)
            add(["x_L_over_2zR", f"{orient}_w{w_um:g}um", f"{xw:.3f}", "", "", f"L / 2 z_R at that waist, z_R {z_rw*1e3:.2f} mm"])
            add(["exponent_weak_drive", f"{orient}_w{w_um:g}um", f"{weak_drive_exponent(xw):.3f}", "", "",
                 "d ln(integrated I^2) / d ln w0 = -2 x / ((1 + x^2) arctan x): -2 at short windows, 0 once the Rayleigh range sits inside"])
            add(["exponent_saturated", f"{orient}_w{w_um:g}um", f"{saturated_exponent(P_W, wm, cath, n_steck * share['4192']):.3f}", "", "",
                 "the same slope on the strong-drive integral at 225 mW (events_per_s_profile over the collected length), the cascade's saturation carried"])
    add(["exponent_on_axis_per_atom", "all", "-4.000", "", "", "the on-axis rate per atom goes as I0^2. the volume integral gives two of those powers to the atom count w0^2 L"])
    e12 = weak_drive_exponent(geometry(F_M, S_IMG_M, CATHODE_M["along12"], w0)[4])
    add(["waist_from_a_15pct_budget", "along12", f"{0.15/abs(e12)*100:.1f}", "", "per cent",
         "sigma(ln w0) = 0.15 / |exponent| at the record's orientation: what a 15 per cent absolute budget would constrain the waist to, once the chain is calibrated"])

    # 2. the chain's factors, each a row with its status
    add(["branching_795nm", "chain", f"{branching:.4f}", "", "", "the 6S decays that take the 5P1/2 leg, rb5s6s.detection.ir_branching_5p12"])
    add(["quantum_efficiency", "chain", f"{QE:.3f}", f"{QE_ERR:.3f}", "", "owner, 2026-09-13: 6 +- 1 per cent in the chain at 795 nm (8 per cent cathode)"])
    add(["filter_transmission", "chain", "1.00", "", "", "OPEN: not on record. docs/plan/12 spans 0.5 to 1, and the predicted rate below is at 1"])
    add(["retro_ratio", "chain", f"{RHO:.2f}", "", "", "the two-photon rate goes as 4 rho (the k-sum-zero coupling). the physical span 0.7 to 1 moves the prediction by 0.7 to 1.06 of the row"])
    add(["noise_bandwidth", "chain", f"{B_HZ:.0f}", "", "Hz", "1 / (2 dt) at the 0.5 ms stored spacing of the boxcar"])
    add(["excess_noise_factor", "chain", "1.00", "", "", "OPEN: the photomultiplier's excess-noise factor is not on record. the measured rate scales with it, and 1.2 to 1.5 is the usual span"])
    add(["density_Steck_130C", "chain", f"{n_steck:.3e}", "", "cm^-3", "rb5s6s.density.number_density_cm3 at the set point"])
    add(["density_AIH_130C", "chain", f"{n_aih:.3e}", "", "cm^-3", "Alcock-Itkin-Horrigan at the set point, as run_density_laws carries it"])
    for a_mm in APERTURES_MM:
        s_obj = geometry(F_M, S_IMG_M, CATHODE_M["along12"], w0)[0]
        add(["solid_angle_fraction", f"D{a_mm:g}mm", f"{solid_angle_fraction(a_mm*1e-3, s_obj):.4f}", "", "",
             "Omega / 4 pi of that clear aperture at the object distance. the aperture is an open item and these three span it"])

    # 2b. the transimpedance the bench states (1e6 V/A, 2026-09-13) turns the noise law's
    # shot term into the photomultiplier's gain and the peak volts into anode currents.
    # The photoelectron rate itself is unchanged by it, n = V / (R G e) = 2 F B V / b, so
    # the gain is a check on the tube and not a second route to the rate.
    R_TRANSIMPEDANCE = 1e6
    with (_CFG.RESULTS_DIR / "noise_model.csv").open(encoding="utf-8") as fh:
        _rows = [r for r in csv.DictReader(fh) if r["role"] == "p_sweep"]
    b_med = float(np.median([float(r["b_V"]) for r in _rows]))
    a_med = float(np.median([float(r["a_V"]) for r in _rows]))
    gain_f = b_med / (2.0 * K.E_CHARGE_C * R_TRANSIMPEDANCE * B_HZ)
    add(["transimpedance", "chain", f"{R_TRANSIMPEDANCE:.0e}", "", "V per A", "the current-to-voltage stage, stated on the bench on 2026-09-13"])
    add(["pmt_gain_times_excess_noise", "chain", f"{gain_f:.2e}", "", "", "G F = b / (2 e R B) from the noise law's shot term at the median b of the p_sweep conditions. A bench check of the tube at its high voltage, which is not on record"])
    n_dark = a_med ** 2 / ((gain_f * K.E_CHARGE_C * R_TRANSIMPEDANCE) ** 2 * 2.0 * B_HZ)
    add(["floor_as_dark_equivalent_rate", "chain", f"{n_dark:.2e}", "", "per s times F", "the noise law's floor a read as photoelectron shot noise of a dark current, a^2 F / ((G e R)^2 2 B) at F = 1. The Johnson noise of the transimpedance over B is a thousandth of a, so the floor is the tube's dark current or the digitiser, not the resistor"])
    add(["floor_as_dark_anode_current", "chain", f"{gain_f * K.E_CHARGE_C * n_dark * 1e9:.1f}", "", "nA", "the same floor as an anode dark current, G e n_dark, independent of F"])

    # 3. the measured photoelectron rate, per p_sweep condition
    meas = measured_rates()
    for (peak, P_mW), (h, h_se, b, per_volt) in sorted(meas.items()):
        n_pe = h * per_volt * 1e-6
        v, es = pm_cells(n_pe, n_pe * math.hypot(h_se / h, 0.10))
        add(["measured_pe_rate", f"{peak}_P{P_mW:g}", v, es, "1e6 per s",
             f"peak height {h:.3f} V (median of the condition's canonical RF-off traces) times 2 F B / b at F = 1, b = {b*1e3:.3f} mV from noise_model.csv. the err carries the height's standard error and the noise coefficients' 10 per cent spread across conditions, and the module's stated 1.5 to 2 method systematic is a further span"])

    # 4. the predicted rate at the 4192 peak, 225 mW, 130 C, with f, s' and QE drawn
    key_meas = ("4192", 225.0)
    n_meas = meas[key_meas][0] * meas[key_meas][3]
    add(["measured_pe_rate_reference", "4192_P225", f"{n_meas:.3e}", "", "per s", "the row the predictions below are read against"])
    add(["anode_current_peak", "4192_P225", f"{meas[key_meas][0] / R_TRANSIMPEDANCE * 1e6:.2f}", "", "uA", "the peak volts over the transimpedance, well inside a side-on tube's linear range"])
    draws_f = rng.normal(F_M, F_ERR_M, N_DRAWS)
    draws_s = rng.normal(S_IMG_M, S_IMG_ERR_M, N_DRAWS)
    draws_qe = rng.normal(QE, QE_ERR, N_DRAWS)
    for law, n_cm3 in (("Steck", n_steck), ("AIH", n_aih)):
        for orient, cath in CATHODE_M.items():
            for a_mm in APERTURES_MM:
                pred = np.empty(N_DRAWS)
                for i in range(N_DRAWS):
                    s_obj, mag, L, _, _ = geometry(draws_f[i], draws_s[i], cath, w0)
                    ev = events_collected(P_W, w0, L, n_cm3 * share["4192"])
                    pred[i] = ev * branching * solid_angle_fraction(a_mm * 1e-3, s_obj) * draws_qe[i]
                med = float(np.median(pred)); lo, hi = np.percentile(pred, [16, 84])
                v, es = pm_cells(math.log10(med), 0.5 * (math.log10(hi) - math.log10(lo)))
                gap = math.log10(med / n_meas)
                gv, ges = pm_cells(gap, math.hypot(0.5 * (math.log10(hi) - math.log10(lo)), 0.2))
                add(["predicted_pe_rate_log10", f"{law}_{orient}_D{a_mm:g}mm", v, es, "log10 per s",
                     f"excitations in the collected length at 4192 (share {share['4192']:.3f} of the atoms), 225 mW, 130 C, saturation carried, times the branching, the aperture's solid angle, the QE. f, s' and QE drawn {N_DRAWS} times, err the 16 to 84 half-spread. filter at 1, rho {RHO}"])
                add(["gap_log10_predicted_over_measured", f"{law}_{orient}_D{a_mm:g}mm", gv, ges, "",
                     "log10 of the prediction over the measured 4192, 225 mW rate. the err adds the measured side's 1.5 to 2 method span (0.2 in the log) to the drawn spread. the D1 trapping, the filter and the excess-noise factor are the named terms outside it"])

    # 5. the D1 photons' own trapping over the standoff
    for law, n_cm3 in (("Steck", n_steck), ("AIH", n_aih)):
        od_per_mm = K.SIGMA_D1_CM2 * n_cm3 * share["4192"] * 0.1
        add(["D1_optical_depth_per_mm", law, f"{od_per_mm:.2f}", "", "per mm",
             "sigma_D1 (constants.SIGMA_D1_CM2, an envelope) times the absorbing share of the atoms (the level the 795 nm photon lands on) times the density. the path from the beam to the window is not on record, so this is per millimetre"])
    add(["D1_trapping_effect_on_collection", "open", "", "", "", "OPEN: a re-emitted photon leaves the cell from elsewhere and the collected fraction of a trapped emission is not the beam's. unpriced here and named in docs/plan/12"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh); w.writerow(HEADER); w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
