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

Runtime about fifty seconds sequential and twenty at four workers,
measured 2026-09-02, deterministic under fixed seeds at any count. Output:
results/scenario_forecast.csv.
"""
from __future__ import annotations

import csv
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# _producer_lock lives in scripts/, which Python puts on sys.path only
# when a script is run DIRECTLY. A test that loads this module by path
# gets no such favour, and three sibling test files do exactly that - two
# of them failed at collection and a third swallowed the ImportError in a
# bare except and reported a pass. Making the import self-sufficient is
# cheaper than remembering.
sys.path.insert(0, str(Path(__file__).resolve().parent))  # _producer_lock lives here
from _producer_lock import take_producer_lock     # noqa: E402

import numpy as np

from rb5s6s import fibre  # noqa: E402
from rb5s6s import constants as C  # noqa: E402
from rb5s6s.constants import transit_fwhm_from_w0  # noqa: E402
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402
from rb5s6s.forecast import forecast_precision  # noqa: E402
from rb5s6s.workers import n_workers  # noqa: E402
from rb5s6s.noise import load_noise_model  # noqa: E402
from rb5s6s.scenario import load_scenario  # noqa: E402

# The record's committed line, the truth the forecast perturbs around.
GAMMA_COLL_MHZ = 0.55        # PRELIM medians, results/linefit_conditions
SIGMA_LASER_MHZ = 1.6
# SOURCED, not written down (2026-09-04). The
# transit stood at 1.8 MHz, the retired 32 um figure relabelled, 88 per cent
# above what this file's own 130 C and the record's 64 um waist give. The shift
# stood at the retired polarizability. Neither was reachable by the sweep that
# closed the transit class, because its pattern could not match an identifier
# carrying digits.
TRANSIT_FWHM_64UM_MHZ = transit_fwhm_from_w0(C.W0_MEASURED_M, T_C=130.0)
S0_225MW_64UM_MHZ = stark_shift_S0_mhz(0.225, C.W0_MEASURED_M, rho=C.RHO_RETRO)
NOISE_FRAC = 0.004           # the 2025 bright-rung dither regime
GAGE_SEEDS = 5               # G3's verdict is a median over seeds, see below
GAGE_TRIALS = 24             # where all eight measured seeds cleared the gate
# The measured-law rows generate and weight in the bench's own volts: the
# acquisition layer's peak convention, 0.8 of a 1.0 V full scale. The flat
# rows keep amp = 1 normalised, which is what every committed forecast row
# used, so the delta column isolates the law and not a rescale.
AMP_LAW_V = 0.8
N_TRIALS = 6
LAMBDA_NM = 993.4            # the drive wavelength reaching the fibre solver

PRESETS = ("dataset_2025", "campaign_cell", "campaign_cell_onf")


def _two_sig(x: float) -> str:
    """LANGUAGE 8a.2 through the shared seam; the local form this replaces
    carried the decade-carry defect the audit measured at 0.0999."""
    from rb5s6s.pmfmt import fmt_err
    out = fmt_err(abs(x))
    return out if out else "0.0"


# --------------------------------------------------------------------
# the Monte-Carlo phase, factored so it can run in a worker
# --------------------------------------------------------------------


def _fp_triple(args):
    """The three forecasts one (preset, waist) task runs: the ramp
    matched, the ramp omitted, and the committed noise law. All three
    take the task's own derived seed, so this function's output depends
    on nothing but its arguments - which is what lets it run in any
    process in any order."""
    truth, design, law_noise, amp_law, seed, n_trials = args
    matched = forecast_precision(truth, design, n_trials=n_trials,
                                 seed=seed, scalings=False,
                                 return_trials=True)
    omitted = forecast_precision(truth, {**design, "fit_s0": 0.0},
                                 n_trials=n_trials, seed=seed,
                                 scalings=False, return_trials=True)
    lawful = forecast_precision(
        truth, {**design, "noise": law_noise, "amp": amp_law},
        n_trials=n_trials, seed=seed, scalings=False, return_trials=True)
    return matched, omitted, lawful


def _assemble_forecasts(tasks, res):
    """Pair each task's key with its own result.

    ONE LINE, EXTRACTED ON PURPOSE. It was inline in `main()`, where no
    test could reach it, and the cost of that was demonstrated on
    2026-09-02 by injection: rotating `res` by one position before the
    zip writes a CSV with the right row count, no error, and every
    value on the wrong row - one preset's number landing on another
    preset's waist. Every test in the determinism file passed, because
    they all call `_fp_triple` directly and none of them touches this.

    `pool.map` preserves order, so the pairing is positional and
    correct. That is a property to PIN, not to trust: it is the single
    assumption standing between a pooled producer and a silently
    mislabelled result table.
    """
    if len(tasks) != len(res):
        raise RuntimeError(
            f"{len(tasks)} tasks against {len(res)} results: the pooled "
            "map dropped or duplicated one, and pairing them positionally "
            "would mislabel every row after the gap")
    return {key: r for (key, _, _, _), r in zip(tasks, res)}


def _init_fp_worker():
    """One BLAS thread per worker: the forecasts are many small solves,
    so nested threading costs more than it buys and oversubscription is
    the failure mode a pooled gate would feel first."""
    import os as _os
    for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        _os.environ.setdefault(v, "1")


def main() -> int:
    # A pooled producer is the one that most needs this: it holds most
    # of the machine for its whole run, so a second copy started because
    # the first "looked stuck" is both likelier and more damaging. The
    # the sequential producers took the lock and the three pooled ones
    # did not, which is exactly backwards. NO COUNT HERE: this comment
    # said "nineteen" where the tree held seventeen, wrong the hour it
    # was written, and a comment cannot derive what it asserts.
    take_producer_lock("run_scenario_forecast")
    law = load_noise_model(ROOT / "results" / "noise_model.csv",
                           role="p_sweep", pool="median")
    # PHASE ONE: every (preset, waist) task with the seed it will use.
    # The seed is the producer's own crc32 of the task identity, so the
    # jobs are independent of each other and of the order they run in.
    # Byte-identity across worker counts follows from that and is
    # MEASURED, not argued, exactly as rb5s6s.workers states: 0, 3 and 8
    # workers each reproduced the committed CSV on 2026-09-02.
    _tasks = []
    _built = {}
    for name in PRESETS:
        sc = load_scenario(ROOT / "examples" / "scenarios" / f"{name}.toml")
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
            _tasks.append(((name, w0), truth, design, seed))
            _built[(name, w0)] = (truth, seed)

    # PHASE TWO: run them. pool.map preserves order, so the results line
    # up with the tasks whatever the worker count, including zero.
    _jobs = [(tr, de, law, AMP_LAW_V, sd, N_TRIALS)
             for _, tr, de, sd in _tasks]
    _nw = n_workers()
    if _nw > 0:
        import multiprocessing as _mp
        with _mp.get_context("spawn").Pool(
                min(_nw, len(_jobs)), initializer=_init_fp_worker) as _pool:
            # a deadline, for the reason the sibling producer states:
            # a spawn child that cannot import its function's module
            # leaves the parent blocked in `map` forever, and a gate
            # then reports nothing at all instead of a failure
            _res = _pool.map_async(_fp_triple, _jobs).get(600)
    else:
        _res = [_fp_triple(j) for j in _jobs]
    _fp = _assemble_forecasts(_tasks, _res)

    # PHASE THREE: the rows, exactly as before, reading the forecasts
    # instead of computing them.
    rows = []
    for name in PRESETS:
        sc = load_scenario(ROOT / "examples" / "scenarios" / f"{name}.toml")
        drift_note = (f"lock {sc.lock}, drift span "
                      f"[{sc.lock_drift_mhz_per_min.low}, "
                      f"{sc.lock_drift_mhz_per_min.high}] MHz/min carried, "
                      "not modelled here")
        for w0 in sc.waist_um.grid(3):
            # read back what phase one built rather than rebuilding it:
            # two independent reconstructions of the same truth cannot be
            # kept in step by anything, and the rows below quote these
            # values while the Monte Carlo consumed phase one's copy
            truth, seed = _built[(name, w0)]
            matched, omitted, lawful = _fp[(name, w0)]
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
                         f"the record's {S0_225MW_64UM_MHZ:.3f} MHz at 64 um scaled by "
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
    # THE VERDICT IS A MEDIAN OVER SEEDS, AND THAT IS THE 2026-09-04 REPAIR.
    # One seed at N_TRIALS was inside its own noise. Measured over eight seeds
    # at six trials the movement runs +7.6 to +106.4 per cent, standard
    # deviation 34.5 against a threshold of 10, and it passes on seven of the
    # eight. The committed seed happened to be the eighth once the transit was
    # sourced, and read -7 per cent: a knob that IS wired, reported unwired.
    # At twenty-four trials the spread is 26.0 and all eight seeds pass. So the
    # gage takes the median of GAGE_SEEDS draws at GAGE_TRIALS, which is what
    # makes its verdict a property of the wiring rather than of the seed. The
    # gage's own history already carried one misreading of this statistic, put
    # down at the time to the wrong rung.
    moves = []
    for gi in range(GAGE_SEEDS):
        seed_g = zlib.crc32(f"gage:G3:{gi}".encode()) % (2 ** 31)
        base_g = forecast_precision(tg, {**dg, "noise": law}, n_trials=GAGE_TRIALS,
                                    seed=seed_g, scalings=False)
        law2 = dict(law); law2["a"] = 2.0 * law["a"]
        dbl_g = forecast_precision(tg, {**dg, "noise": law2}, n_trials=GAGE_TRIALS,
                                   seed=seed_g, scalings=False)
        moves.append(100.0 * (dbl_g["gamma_coll_err"] / base_g["gamma_coll_err"] - 1.0))
    moved = float(np.median(moves))
    rows.append(["gage", "G3", "law_floor_doubling_moves_error",
                 str(moved > 10.0), f"{np.std(moves, ddof=1):.0f}", "",
                 f"doubling the law's floor moves the dim-rung campaign error "
                 f"by {moved:+.0f} per cent, the median of {GAGE_SEEDS} seeds at "
                 f"{GAGE_TRIALS} trials with the err column carrying their spread, "
                 "required past +10 per the preregistration: a law knob that "
                 "moves nothing is not wired", "DIAGNOSTIC"])
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
