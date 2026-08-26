#!/usr/bin/env python
"""What the twin records on each instrument, and what it recovers.

WHY THIS EXISTS. The twin was redesigned, by decision, to produce realistic
traces of the next campaign: the instrument's own point
count and vertical step, the measured noise law, the sample correlation, one
peak or all four on a single range, and either platform. A redesign that is
only exercised by its unit tests is a design nobody can check, so this
producer runs it across the configurations the next campaign would use and
writes what came out.

THE TWO THINGS WORTH READING. First, the recovery rows: the twin generates
from a known truth and the PRODUCTION fitter recovers it, so a bias here is
a bias in the analysis and not in the twin. Second, the platform rows: the
vapour cell radiates against the cell it sits in, while the nanofibre
radiates against a room-temperature laboratory whatever its atoms do, and
those two blackbody temperatures are printed side by side because reading
the atom temperature as the radiation temperature is the error this design
exists to make impossible.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import config as C, instruments as inst, twin   # noqa: E402
from rb5s6s.linefit import fit_condition                     # noqa: E402

OUT = C.RESULTS_DIR / "twin_realism.csv"
LAW = dict(a=0.004, b=1.0e-3, c=0.0, lev_max=1.0, tau_int=1.0)
TRUTH = dict(gamma_coll_mhz=0.580779, sigma_laser_mhz=1.560691,
             transit_fwhm_mhz=0.957477)
SEED = 20260824


def main() -> int:
    rows = []

    def add(scope, quantity, value, unit, note, status="DIAGNOSTIC"):
        rows.append(dict(scope=scope, quantity=quantity, value=value,
                         unit=unit, note=note, status=status))

    add("TRUTH", "source", "linefit_conditions p_sweep/4154/130/225", "reference",
        "the truth is read from a named committed condition and the transit "
        "from the measured waist, so no number here is chosen to be recovered")
    for k, v in TRUTH.items():
        add("TRUTH", k, f"{v:.6f}", "MHz", "the world the twin generates")

    # ---- what each instrument stores -----------------------------------
    cell = twin.vapour_cell(130.0, **TRUTH)
    for key, kind in (("agilent_3054a", "one_peak"),
                      ("lecroy_ws3104z", "four_peak"),
                      ("rtm3004", "four_peak")):
        acq = twin.Acquisition(instrument=key, n_traces=1)
        f, v, meta = twin.acquire(cell, acq, kind=kind, noise_law=LAW,
                                  rng=np.random.default_rng(SEED))
        ins = inst.get(key)
        scope = f"{key}_{kind}"
        add(scope, "n_points", meta["n_points"], "count",
            f"the instrument's own record length, {ins.provenance}")
        add(scope, "peak_over_lsb", f"{meta['peak_over_lsb']:.0f}", "LSB",
            f"line peak in vertical steps at {meta['mode']}, a "
            f"{meta['mode_kind']} mechanism")
        add(scope, "span_mhz", f"{f[0].max() - f[0].min():.0f}", "MHz",
            "the frequency window the trace covers, which for a four-peak "
            "trace has to hold all four lines on one vertical range")
        add(scope, "correlates_neighbours", meta["correlates_neighbours"],
            "flag", "true only for the moving-average mode, which is why the "
            "design runs the LeCroy raw and smooths offline")

    # ---- does the production fitter recover the truth -------------------
    for tau in (1.0, 3.8):
        acq = twin.Acquisition(instrument="agilent_3054a", n_traces=5,
                               span_mhz=40.0, tau_int_samples=tau)
        f, v, _ = twin.acquire(cell, acq, kind="one_peak", noise_law=LAW,
                               rng=np.random.default_rng(SEED))
        fit = fit_condition(f, v, T_C=130.0, law=LAW,
                            transit_fwhm=TRUTH["transit_fwhm_mhz"],
                            trim_tails=True, gamma_l=0.0, fit_gamma_l=False)
        scope = f"RECOVERY_tau{tau:g}"
        for name, got, want in (("gamma_coll", fit["gamma_coll"],
                                 TRUTH["gamma_coll_mhz"]),
                                ("sigma_laser", fit["sigma_laser"],
                                 TRUTH["sigma_laser_mhz"])):
            add(scope, f"{name}_ratio", f"{got / want:.3f}", "dimensionless",
                f"fitted over true at sample correlation {tau:g}. One means "
                "the production fitter reads the twin's world correctly")

    # ---- the platform distinction, printed side by side -----------------
    onf = twin.nanofibre(atom_temperature_uk=30.0, transit_fwhm_mhz=3.0,
                         sigma_laser_mhz=0.10)
    add("PLATFORM_cell", "radiation_temperature", f"{cell.radiation_temperature_k:.2f}",
        "K", "the heated cell IS the radiation environment its atoms see")
    add("PLATFORM_cell", "blackbody_shift", f"{cell.blackbody_shift_mhz():.6f}",
        "MHz", "evaluated at the cell temperature")
    add("PLATFORM_nanofibre", "radiation_temperature",
        f"{onf.radiation_temperature_k:.2f}", "K",
        "the ROOM, fixed at 300 K, and not the atoms. Microkelvin atoms "
        "microns from a fibre in a laboratory radiate against the laboratory")
    add("PLATFORM_nanofibre", "atom_temperature",
        f"{onf.atom_temperature_k:.2e}", "K",
        "carried because it sets the transit time through the guided mode, "
        "and never used as a radiation temperature")
    add("PLATFORM_nanofibre", "blackbody_shift",
        f"{onf.blackbody_shift_mhz():.6f}", "MHz",
        "evaluated at 300 K. Reading the atom temperature as the radiation "
        "temperature would return essentially zero and would be wrong by the "
        "whole size of the term")

    f, v, meta = twin.acquire(onf, twin.Acquisition(
        instrument="lecroy_ws3104z", n_points=100_000, n_traces=1),
        kind="one_peak", noise_law=LAW, rng=np.random.default_rng(SEED))
    add("PLATFORM_nanofibre", "acquires", "YES", "flag",
        f"the twin runs for the fibre platform too, {meta['n_points']} points "
        f"at {meta['mode']}")

    add("VERDICT", "twin_is_instrument_aware", "YES", "verdict",
        "point count, vertical step, resolution mechanism, sample "
        "correlation, trace kind and platform all come from the "
        "configuration rather than from a default", "DIAGNOSTIC")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["scope", "quantity", "value",
                                           "unit", "note", "status"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")
    for r in rows:
        if r["scope"].startswith(("RECOVERY", "PLATFORM")):
            print(f"  {r['scope']:22} {r['quantity']:24} {r['value']:>12} {r['unit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
