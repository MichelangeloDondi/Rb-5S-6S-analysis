#!/usr/bin/env python3
"""The three terms that rise together along the temperature arm: the Rb self-broadening signal, the transit's drift and
the permeated gas's drift, sized from the record's own cells and callables.

WHY THIS EXISTS. F244 and F245 (2026-09-21) sized them from the same callables and retracted the claim that beta_self is read
through a density slope the beam does not enter: across the arm the transit's own sqrt(T)/w0 drift is as large as the whole
self-broadening signal and carries its sign, and a sealed cell's permeated gas adds to both. Those sizes sat in a findings
ledger and in no results file, so nothing could cite them (asked 2026-09-22), and two of their
inputs have moved since: the central density law is Alcock's (owner order O42), and the Lorentzian-equivalent width at the
calculated waist is the kernel chain's own. This producer writes the three terms and their ratios as cells.

WHAT EACH ROW READS, never a typed value:
* the arm's end points from `density.RECORD_CELL_TEMPS_C`, the densities from `density.number_density_cm3` on the central law,
* beta_self from `results/beta_self_theory.csv` (`beta_self_6s`, `anchored`), held at its 403.15 K anchor across the arm as
  F244 held it (the density at the cold end is about two per cent of the hot end's, so beta's own temperature law barely enters),
* the transit FWHM from `constants.transit_fwhm_from_w0` at the waist band's edges (`constants.W0_BAND_M`) and the central
  waist (`constants.W0_CENTRAL_M`),
* the permeated gas's reference width from `results/kernel_k3.csv`'s inverse-variance mean of the per-peak Lorentzian-
  EQUIVALENT widths (`all`, `k2p5_gamma_l_weighted_mean`), which also holds any Lorentzian laser content, so the permeated
  drift it gives is an UPPER size. Its fractional change across the arm is thermodynamics alone: a sealed cell holds a fixed
  amount on the arm's timescale of hours, so the width goes as n sigma v with n fixed, T^+0.5 for a hard sphere and T^+0.3 once
  the van der Waals rate coefficient's own velocity law is carried, and only a cell held at fixed pressure gives T^-0.5 (F245).

Output: results/ladder_terms.csv. Every row DIAGNOSTIC. Seconds.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s.pmfmt import pm_cells  # noqa: E402
from rb5s6s import config as C  # noqa: E402
from rb5s6s import constants as K  # noqa: E402
from rb5s6s import density  # noqa: E402

KELVIN = 273.15
#: The permeated gas's temperature exponents: name -> (exponent, reading).
PERMEATED_LAWS = {
    "fixed_density_hard_sphere": (0.5, "a sealed cell on the arm's timescale, width n sigma v with n fixed"),
    "fixed_density_vdw": (0.3, "the same with the van der Waals rate coefficient's own velocity law carried"),
    "fixed_pressure": (-0.5, "a cell held at fixed pressure, n = P/kT, the branch that does NOT apply to a sealed cell"),
}


def _row(path: Path, first: str, second: str, cols=("value", "err")) -> tuple:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.reader(fh))
    head, body = rows[0], rows[1:]
    hit = [r for r in body if r[0] == first and r[1] == second]
    if len(hit) != 1:
        raise SystemExit(f"{path.name}: {len(hit)} rows for ({first}, {second}), need exactly one")
    r = dict(zip(head, hit[0]))
    return tuple(float(r[c]) if r.get(c, "") not in ("", None) else float("nan") for c in cols)


def gamma_l_reference() -> tuple[float, float]:
    """The kernel chain's mean Lorentzian-equivalent width and its standard error, the mean re-derived from its members."""
    path = Path(C.RESULTS_DIR) / "kernel_k3.csv"
    (mean,) = _row(path, "all", "k2p5_gamma_l_weighted_mean", cols=("value",))
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    vals = {r["scope"]: float(r["value"]) for r in rows if r["quantity"] == "gamma_l_equiv"}
    errs = {r["scope"]: float(r["value"]) for r in rows if r["quantity"] == "gamma_l_equiv_err"}
    w = np.array([1.0 / errs[k] ** 2 for k in vals])
    x = np.array([vals[k] for k in vals])
    members = float(np.sum(w * x) / np.sum(w))
    if abs(members - mean) > 1e-4:
        raise SystemExit(f"kernel_k3.csv's mean row {mean} left its members {members:.6f}: the chain is stale against itself")
    return mean, float(1.0 / np.sqrt(np.sum(w)))


def main() -> int:
    t_lo, t_hi = min(density.RECORD_CELL_TEMPS_C), max(density.RECORD_CELL_TEMPS_C)
    n_lo, n_hi = (float(v) for v in density.number_density_cm3(np.array([t_lo, t_hi])))
    beta, beta_err = _row(Path(C.RESULTS_DIR) / "beta_self_theory.csv", "beta_self_6s", "anchored")
    signal = beta * (n_hi - n_lo) / 1e12            # kHz, beta in kHz per 1e12 cm^-3
    signal_err = beta_err * (n_hi - n_lo) / 1e12
    law = density.DENSITY_LAW
    arm = f"{t_lo:g} to {t_hi:g} C"
    rows = [
        ("density", f"n_{t_lo:g}C", n_lo, "", "cm^-3", f"number_density_cm3 on the central law ({law})"),
        ("density", f"n_{t_hi:g}C", n_hi, "", "cm^-3", f"number_density_cm3 on the central law ({law})"),
        ("density", "lever", n_hi / n_lo, "", "ratio", f"the arm's density lever on {law}"),
        ("input", "beta_self_anchor", beta, beta_err, "kHz per 1e12 cm^-3 at 403.15 K",
         "beta_self_theory.csv beta_self_6s anchored, held at its anchor across the arm"),
        ("signal", "rb_self_broadening", signal, signal_err, "kHz",
         f"beta_self times the density change across {arm}: what a slope of width against density is meant to read"),
    ]
    waists = [("band_low", K.W0_BAND_M[0]), ("central", K.W0_CENTRAL_M), ("band_high", K.W0_BAND_M[1])]
    transit_central = None
    for label, w0 in waists:
        for iso in (87, 85):
            d = 1e3 * (K.transit_fwhm_from_w0(w0, t_hi, isotope=iso) - K.transit_fwhm_from_w0(w0, t_lo, isotope=iso))
            key = f"{label}_{w0 * 1e6:.2f}um_rb{iso}"
            rows.append(("transit_drift", key, d, "", "kHz",
                         f"transit_fwhm_from_w0 at {w0 * 1e6:.2f} um, {arm}: it rises as sqrt(T) with the signal's sign"))
            rows.append(("transit_over_signal", key, d / signal, d / signal * signal_err / signal, "ratio",
                         "the transit drift over the whole self-broadening signal, its error the anchor's alone"))
            if label == "central" and iso == 87:
                transit_central = d
    g_ref, g_err = gamma_l_reference()
    rows.append(("input", "gamma_l_equiv_reference", g_ref, g_err, "MHz",
                 "kernel_k3.csv's inverse-variance mean of the per-peak Lorentzian-equivalent widths: an UPPER size for "
                 "the permeated gas, which it holds together with any Lorentzian laser content"))
    ratio_t = (t_hi + KELVIN) / (t_lo + KELVIN)
    perm = {}
    for name, (n, reading) in PERMEATED_LAWS.items():
        f = ratio_t ** n - 1.0
        d = 1e3 * g_ref * f
        perm[name] = d
        rows.append(("permeated_factor", name, f, "", "fraction", f"T^{n:+g} across {arm}: {reading}"))
        rows.append(("permeated_drift", name, d, 1e3 * g_err * abs(f), "kHz",
                     "the reference width times the fraction: an upper size"))
        rows.append(("permeated_over_signal", name, d / signal, "", "ratio", "the permeated drift over the whole signal"))
    for name in ("fixed_density_hard_sphere", "fixed_density_vdw"):
        total = (signal + transit_central + perm[name]) / signal
        rows.append(("naive_slope_factor", f"central_{name}", total, "", "ratio",
                     "what a slope of total width against density returns over beta_self at the central waist, Rb 87: "
                     "all three terms rise together along the arm, so no cancellation is available and the separation "
                     "needs a lever with a different exponent (power, waist, or a platform without the transit)"))
    out = Path(C.RESULTS_DIR) / "ladder_terms.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit", "note", "status"])
        for q, k, v, e, u, note in rows:
            # two significant digits on an error and the value to its decimals (LANGUAGE 8a.2), through the one
            # formatter every producer uses; a row without an error keeps its six significant figures
            vs, es = (f"{v:.6g}", "") if e == "" else pm_cells(v, e)
            w.writerow([q, k, vs, es, u, note, "DIAGNOSTIC"])
    print(f"signal {signal:.1f} +- {signal_err:.1f} kHz, transit at the central waist {transit_central:+.1f} kHz, "
          f"permeated upper size {perm['fixed_density_hard_sphere']:+.1f} (T^+0.5), {perm['fixed_density_vdw']:+.1f} (T^+0.3) kHz")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
