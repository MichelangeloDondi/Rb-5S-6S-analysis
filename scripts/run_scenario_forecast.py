#!/usr/bin/env python3
"""Forecast each shipped scenario, spanning what the record leaves open.

For every preset under examples/scenarios/ this runs the public forecast
path (`forecast_precision`: synthetic traces through the production fitter,
Monte-Carlo, the fit's own reported errors) at each point of the waist
span's three-point grid, twice: once with the fitter matched to the
injected ramp and once with the ramp deliberately omitted from the fit, so
the cost of ignoring the one asymmetric term is a measured column and not a
belief. Every claim-class row carries an err: the forecast rows the
world-to-world spread of the reported error, the shift rows the derived
retro-ratio term, the mode rows the propagated diameter tolerance. The waist scales the transit width as 1/w0 and the 225 mW shift as
1/w0 squared from their committed 64 um values, which is geometry, not new
physics. The nanofibre preset adds rows from the solved HE11 mode: the
effective index, the intensity decay length, and the guided transit width
at the cold-atom temperature.

The lock-drift span rides along in the note, carried but not
modelled here: this producer is the scenario layer's end-to-end proof, and
the campaign case builds on it separately.

Runtime about four minutes, deterministic under fixed seeds. Output:
results/scenario_forecast.csv.
"""
from __future__ import annotations

import csv
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np

from rb5s6s import fibre  # noqa: E402
from rb5s6s.forecast import forecast_precision  # noqa: E402
from rb5s6s.noise import load_noise_model  # noqa: E402
from rb5s6s.scenario import load_scenario  # noqa: E402

# The record's committed line, the truth the forecast perturbs around.
GAMMA_COLL_MHZ = 0.55        # PRELIM medians, results/linefit_conditions
SIGMA_LASER_MHZ = 1.6
TRANSIT_FWHM_64UM_MHZ = 1.8  # at the 64 um lineage waist
S0_225MW_64UM_MHZ = 0.348    # results/stark_joint.csv S0_225mW_pred
NOISE_FRAC = 0.004           # the 2025 bright-rung dither regime
# The measured-law rows generate and weight in the bench's own volts: the
# acquisition layer's peak convention, 0.8 of a 1.0 V full scale. The flat
# rows keep amp = 1 normalised, which is what every committed forecast row
# used, so the delta column isolates the law and not a rescale.
AMP_LAW_V = 0.8
N_TRIALS = 6
LAMBDA_NM = 993.4            # the drive wavelength reaching the fibre solver

PRESETS = ("dataset_2025", "campaign_cell", "campaign_cell_onf")


def _two_sig(x: float) -> str:
    """LOGIC 8a.2: a Gaussian uncertainty carries two significant digits."""
    if x == 0.0 or not np.isfinite(x):
        return "0.0"
    from math import floor, log10
    d = 1 - int(floor(log10(abs(x))))
    return f"{round(x, d):.{max(d, 0)}f}"


def main() -> int:
    law = load_noise_model(ROOT / "results" / "noise_model.csv",
                           role="p_sweep", pool="median")
    rows = []
    for name in PRESETS:
        sc = load_scenario(ROOT / "examples" / "scenarios" / f"{name}.toml")
        drift_note = (f"lock {sc.lock}, drift span "
                      f"[{sc.lock_drift_mhz_per_min.low}, "
                      f"{sc.lock_drift_mhz_per_min.high}] MHz/min carried, "
                      "not modelled here")
        for w0 in sc.waist_um.grid(3):
            scale = 64.0 / w0
            truth = {"gamma_coll": GAMMA_COLL_MHZ,
                     "sigma_laser": SIGMA_LASER_MHZ,
                     "transit_fwhm": TRANSIT_FWHM_64UM_MHZ * scale,
                     "s0": S0_225MW_64UM_MHZ * scale ** 2}
            design = {"noise": NOISE_FRAC, "n_traces": 5, "n_points": 2000,
                      "T_C": 130.0}
            # zlib.crc32, not hash(): string hashing is per-process
            # randomised and a seed that moves would fail freshness forever
            seed = zlib.crc32(f"{name}:{w0:.3f}".encode()) % (2 ** 31)
            matched = forecast_precision(truth, design, n_trials=N_TRIALS,
                                         seed=seed, scalings=False,
                                         return_trials=True)
            omitted = forecast_precision(truth, {**design, "fit_s0": 0.0},
                                         n_trials=N_TRIALS, seed=seed,
                                         scalings=False, return_trials=True)
            m_spread = float(np.std(matched["gamma_coll_err_trials"], ddof=1))
            o_spread = float(np.std(omitted["gamma_coll_err_trials"], ddof=1))
            # The retro-ratio term alone moves the shift: the ramp samples
            # the fringe-averaged intensity, <E^2> going as 1 + rho^2, so
            # d ln S0 = 2 rho d rho / (1 + rho^2). Derived, not simulated.
            s0_err = truth["s0"] * 2.0 * sc.retro_ratio \
                * sc.retro_ratio_err / (1.0 + sc.retro_ratio ** 2)
            rows.append([name, f"w0_{w0:g}um", "gamma_coll_err_matched",
                         f"{matched['gamma_coll_err']:.4f}",
                         _two_sig(m_spread), "MHz",
                         f"median fitted error over {N_TRIALS} trials, ramp "
                         f"matched. s0 {truth['s0']:.3f} MHz, transit "
                         f"{truth['transit_fwhm']:.2f} MHz at this waist. "
                         + drift_note, "ENVELOPE"])
            rows.append([name, f"w0_{w0:g}um", "gamma_coll_err_ramp_omitted",
                         f"{omitted['gamma_coll_err']:.4f}",
                         _two_sig(o_spread), "MHz",
                         "same worlds, fitter refuses the ramp. The gap "
                         "against the matched row is the measured cost of "
                         "ignoring the asymmetric term at this focus, and "
                         "the mismatched fitter's reported error can also "
                         "under-state itself", "ENVELOPE"])
            lawful = forecast_precision(
                truth, {**design, "noise": law, "amp": AMP_LAW_V},
                n_trials=N_TRIALS, seed=seed, scalings=False,
                return_trials=True)
            l_spread = float(np.std(lawful["gamma_coll_err_trials"], ddof=1))
            delta_pct = 100.0 * (lawful["gamma_coll_err"]
                                 / matched["gamma_coll_err"] - 1.0)
            rows.append([name, f"w0_{w0:g}um", "gamma_coll_err_measured_law",
                         f"{lawful['gamma_coll_err']:.4f}",
                         _two_sig(l_spread), "MHz",
                         "same worlds under the committed noise law "
                         "(noise_model.csv p_sweep median, volts, amp 0.8 V "
                         f"per the acquisition convention): {delta_pct:+.0f} "
                         "per cent against the flat row, which is leg 3's "
                         "committed delta", "ENVELOPE"])
            rows.append([name, f"w0_{w0:g}um", "s0_225mW",
                         f"{truth['s0']:.4f}", _two_sig(s0_err), "MHz",
                         "the committed 0.348 MHz at 64 um scaled by "
                         "(64/w0)^2, geometry only", "CALIB"])
        if sc.fibre is not None:
            mode = fibre.solve_he11(sc.fibre.diameter_nm, LAMBDA_NM)
            lo = fibre.solve_he11(
                sc.fibre.diameter_nm - sc.fibre.diameter_tolerance_nm,
                LAMBDA_NM)
            hi = fibre.solve_he11(
                sc.fibre.diameter_nm + sc.fibre.diameter_tolerance_nm,
                LAMBDA_NM)
            rows.append([name, "fibre", "neff", f"{mode.neff:.4f}",
                         _two_sig(abs(hi.neff - lo.neff) / 2.0), "",
                         "solved HE11 effective index at the drive "
                         "wavelength, rb5s6s.fibre", "CALIB"])
            rows.append([name, "fibre", "intensity_decay",
                         f"{mode.intensity_decay_nm:.1f}",
                         _two_sig(abs(hi.intensity_decay_nm
                                      - lo.intensity_decay_nm) / 2.0), "nm",
                         "the evanescent intensity 1/e length, 1/(2q)",
                         "CALIB"])
            tr = fibre.transit_fwhm(sc.fibre.atom_temperature_k,
                                    mode.intensity_decay_nm * 1e-9)
            tr_lo = fibre.transit_fwhm(sc.fibre.atom_temperature_k,
                                       hi.intensity_decay_nm * 1e-9)
            tr_hi = fibre.transit_fwhm(sc.fibre.atom_temperature_k,
                                       lo.intensity_decay_nm * 1e-9)
            rows.append([name, "fibre", "guided_transit_fwhm",
                         f"{tr.fwhm_hz / 1e6:.4f}",
                         _two_sig(abs(tr_hi.fwhm_hz - tr_lo.fwhm_hz)
                                  / 2e6), "MHz",
                         f"cold atoms at {sc.fibre.atom_temperature_k:g} K "
                         "crossing the evanescent decay length, ensemble "
                         "flux kernel, rb5s6s.fibre.transit_fwhm", "CALIB"])
    # G3, the wired-knob gage: doubling the law's floor must move the dim
    # forecast visibly, or the law knob reaches nothing. One configuration,
    # committed beside the physics rows.
    sc16 = load_scenario(ROOT / "examples" / "scenarios" / "campaign_cell.toml")
    w0g = sc16.waist_um.grid(3)[1]
    sg = 64.0 / w0g
    tg = {"gamma_coll": GAMMA_COLL_MHZ, "sigma_laser": SIGMA_LASER_MHZ,
          "transit_fwhm": TRANSIT_FWHM_64UM_MHZ * sg,
          "s0": S0_225MW_64UM_MHZ * sg ** 2}
    # THE GAGE RUNS AT THE DIM RUNG, the regime the preregistration names:
    # at the bright amplitude the shot term b times level buries the floor
    # thirty-seven-fold and the first version of this gage read minus five
    # per cent there, a wrong-regime test, not an unwired knob. At the dim
    # rung's two-photon amplitude the floor dominates and the knob shows.
    amp_dim = AMP_LAW_V * (0.025 / 0.225) ** 2
    dg = {"n_traces": 5, "n_points": 2000, "T_C": 130.0, "amp": amp_dim}
    seed_g = zlib.crc32(b"gage:G3") % (2 ** 31)
    base_g = forecast_precision(tg, {**dg, "noise": law}, n_trials=N_TRIALS,
                                seed=seed_g, scalings=False)
    law2 = dict(law); law2["a"] = 2.0 * law["a"]
    dbl_g = forecast_precision(tg, {**dg, "noise": law2}, n_trials=N_TRIALS,
                               seed=seed_g, scalings=False)
    moved = 100.0 * (dbl_g["gamma_coll_err"] / base_g["gamma_coll_err"] - 1.0)
    rows.append(["gage", "G3", "law_floor_doubling_moves_error",
                 str(moved > 10.0), "", "",
                 f"doubling the law's floor moves the dim-rung campaign error "
                 f"by {moved:+.0f} per cent, required past +10 per the "
                 "preregistration: a law knob that moves nothing is not "
                 "wired", "DIAGNOSTIC"])
    out = ROOT / "results" / "scenario_forecast.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "key", "quantity", "value", "err", "unit",
                    "note", "status"])
        w.writerows(rows)
    print(f"wrote {out.relative_to(ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
