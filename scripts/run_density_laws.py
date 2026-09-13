#!/usr/bin/env python3
"""The vapour-pressure laws the record could stand on, their spread across the
archive's temperatures, what each is supported by, and what the archive's own
temperature ladder says about them.

WHY THIS EXISTS (owner, 2026-09-13: "delve into the density law to understand
whether we can do better than 20 per cent"). `density.py` carries Nesmeyanov's
liquid correlation as Steck tabulates it and a typed 20 per cent as "the
midpoint of the 10 to 30 per cent spread between published correlations",
with none named. Three are named here with their forms:

  Nesmeyanov (Steck)   log10 P/torr = 15.88253 - 4529.635/T + 0.00058663 T - 2.99138 log10 T
  Alcock-Itkin-Horrigan (CRC)   log10 P/torr = 2.881 + 4.312 - 4040/T   (liquid. claimed better than 5 per cent)
  Stull-Sinke (CRC, second form)   log10 P/Pa = 9.545 - 4132/T

and what supports each: Siddons, Adams, Ge and Hughes 2008 (absolute D-line
absorption, room temperature to a few tens of degrees above, the Nesmeyanov
form in their appendix, "excellent agreement" of absolute absorption). Achar
et al. 2025 (single-pass absorption in MEMS cells at 293 to 353 K, densities
"follow the empirical relation closely" for Alcock et al., 2 per cent
systematic per point). Zameroski et al. 2014 (the self-broadening anchor's
pressure axis, the Alcock form). THE TWO LAWS DIFFER BY 15 TO 24 PER CENT OVER
70 TO 130 C AND EACH IS "SUPPORTED" AT A FEW PER CENT, which is consistent
only because a support is a comparison at a MEASURED temperature, and a
kelvin is 5.7 per cent of the density at 130 C: the laws' disagreement is a
thermometry offset of three to four kelvin between the experiments that
support them. So the literature bounds the law at about the 20 per cent
`density.py` types, and the row that matters is the archive's own: the
temperature ladder's collisional width, fitted with each law's shape.

WHAT THE ROWS ARE. `N_<law>` at each archive temperature. `ratio_<law>_over_Steck`;
`ratio_as_kelvin` (the offset that would reconcile the two laws at that
temperature). `support_<paper>` rows naming the range and the level. and the
`ladder_fit_<law>` rows: gamma_coll(T) from the t_sweep fitted as
beta N_law(T - dT) + floor, with dT free on [0, 30] K, reporting beta, dT,
floor and the fit's chi-squared, so the archive says which shape it prefers
and how much of a cold spot it needs under each. Every row is DIAGNOSTIC.
"""
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from rb5s6s import config as _CFG                                  # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s.density import number_density_cm3, dlnN_dT_per_K, N_SCALE_FRAC_SYST   # noqa: E402

TORR_PA = 101325.0 / 760.0
T_LADDER_C = (70.0, 90.0, 110.0, 130.0)


def n_aih(T_C):
    T = np.asarray(T_C, dtype=float) + 273.15
    p_torr = 10.0 ** (2.881 + 4.312 - 4040.0 / T)
    return p_torr * TORR_PA / (K.K_B_J_PER_K * T) * 1e-6


def n_smi(T_C):
    T = np.asarray(T_C, dtype=float) + 273.15
    p_pa = 10.0 ** (9.545 - 4132.0 / T)
    return p_pa / (K.K_B_J_PER_K * T) * 1e-6


LAWS = {"Steck": number_density_cm3, "AIH": n_aih, "SMI": n_smi}
SUPPORT = {
    "siddons2008": ("Nesmeyanov (Steck), their appendix A. absolute D-line absorption at room temperature and above", "absolute absorption in excellent agreement with theory at the measured temperature. no per cent on the density is stated"),
    "achar2025": ("Alcock-Itkin-Horrigan. single-pass absorption in MEMS cells, 293 to 353 K", "densities follow the relation closely over the range. 2.0 per cent systematic per point. no directional offset reported"),
    "zameroski2014": ("Alcock-Itkin-Horrigan. the self-broadening anchor's pressure axis at 393 K", "the anchor's rate per mTorr is on this law. converted with Steck's it is 22 per cent lower"),
    "alcock1984": ("the law's own claim", "better than 5 per cent for the practical equations"),
}


def _t_sweep():
    """The temperature ladder is the L's vertical arm AND its corner: the
    t_sweep rows (70, 90, 110 C at the maximum power) plus the p_sweep rows at
    the maximum power (130 C), which the manifest marks `serves_t130` (owner,
    2026-09-13: "the 130C 225 mW has to be considered in both sweeps")."""
    rows = []
    with (_CFG.RESULTS_DIR / "linefit_conditions.csv").open(encoding="utf-8") as fh:
        all_rows = [r for r in csv.DictReader(fh) if r.get("T") and r.get("gamma_coll") and r.get("gamma_coll_err")]
    # The t_sweep rows carry a BLANK power, which the manifest defines as the maximum power
    # (docs/DATA.md), so the selection never asks them for one.
    p_max = max(float(r["P"]) for r in all_rows if r.get("P"))
    for r in all_rows:
        if r.get("role") == "t_sweep" or (r.get("role") == "p_sweep" and r.get("P") and abs(float(r["P"]) - p_max) < 1e-9):
            rows.append((float(r["T"]), float(r["gamma_coll"]), float(r["gamma_coll_err"]), r["peak"]))
    return rows


def _fit_ladder(law, rows):
    """gamma = beta * N_law(T - dT) + floor, dT scanned on [0, 30] K, beta and
    floor linear at each dT. returns the best (beta, dT, floor, chi2, n)."""
    T = np.array([r[0] for r in rows]); g = np.array([r[1] for r in rows]); e = np.array([r[2] for r in rows])
    best = None
    for dT in np.linspace(0.0, 30.0, 301):
        N = law(T - dT) / 1e12
        A = np.vstack([N, np.ones_like(N)]).T / e[:, None]
        coef, *_ = np.linalg.lstsq(A, g / e, rcond=None)
        chi2 = float(np.sum((A @ coef - g / e) ** 2))
        if best is None or chi2 < best[3]:
            best = (float(coef[0]), float(dT), float(coef[1]), chi2, len(g))
    return best


def main() -> int:
    out = [["quantity", "key", "value", "err", "unit", "note", "status"]]
    for T in T_LADDER_C:
        ns = {name: float(f(T)) for name, f in LAWS.items()}
        for name, n in ns.items():
            out.append([f"N_{name}", f"T{T:g}", f"{n:.4e}", "", "cm^-3", "number density from the named law at the set point", ""])
        for name in ("AIH", "SMI"):
            r = ns[name] / ns["Steck"]
            dk = float(np.log(r) / dlnN_dT_per_K(T))
            out.append([f"ratio_{name}_over_Steck", f"T{T:g}", f"{r:.4f}", "", "", "the two laws' ratio at this temperature", ""])
            out.append([f"ratio_as_kelvin_{name}", f"T{T:g}", f"{dk:.2f}", "", "K", "the temperature offset at which Steck's law gives the other's density (ln ratio over d ln N/dT). the laws' disagreement is a thermometry offset of this size between the experiments supporting each", ""])
        out.append(["dlnN_dT", f"T{T:g}", f"{100 * float(dlnN_dT_per_K(T)):.2f}", "", "per cent per K", "the density's sensitivity to the temperature at this set point", ""])
    out.append(["typed_spread", "density_py", f"{100 * N_SCALE_FRAC_SYST:.0f}", "", "per cent", "N_SCALE_FRAC_SYST as density.py carries it", ""])
    for key, (law, level) in SUPPORT.items():
        out.append([f"support_{key}", "law", law, "", "", level, ""])
    rows = _t_sweep()
    if rows:
        BETA_THEORY = 0.00338     # MHz per 1e12 cm^-3, vanderwaals.beta_self_anchored at 403 K (the record's anchor; the 393 K correction is 2.6 per cent)
        for name, f in LAWS.items():
            # the trade-off, made explicit: beta at dT fixed at 0 and at 10 K, and dT with beta pinned at theory
            T = np.array([r[0] for r in rows]); g = np.array([r[1] for r in rows]); e = np.array([r[2] for r in rows])
            for dT_fix in (0.0, 10.0):
                N = f(T - dT_fix) / 1e12
                A = np.vstack([N, np.ones_like(N)]).T / e[:, None]
                coef, *_ = np.linalg.lstsq(A, g / e, rcond=None)
                chi2f = float(np.sum((A @ coef - g / e) ** 2))
                out.append([f"ladder_fit_{name}", f"beta_at_dT{dT_fix:g}", f"{coef[0]:.4f}", "", "MHz per 1e12 cm^-3",
                            f"beta with the cold spot fixed at {dT_fix:g} K and the floor free ({coef[1]:.3f} MHz). chi2 {chi2f:.2f} for {len(g) - 2} dof. theory {BETA_THEORY} per 1e12, so this reads {coef[0] / BETA_THEORY:.0f} times theory, the Lorentzian-sum degeneracy the record names (lever_crosscheck.csv)", ""])
            # THE PROFILE IS READ, NOT ASSUMED (corrected 2026-09-13). The
            # first version of this row called dT "unconstrained" and credited
            # "three temperatures". Both are wrong: the ladder is the L design's
            # FOUR temperatures, and the pinned chi2 profile RISES monotonically
            # from dT = 0 to the scan's edge, so the minimum sits on the dT = 0
            # rail. A flat profile is unconstrained; a monotone one is railed,
            # and the two readings differ in what they license.
            best_p, prof = None, []
            for dT in np.linspace(0.0, 30.0, 301):
                N = f(T - dT) / 1e12
                floor = float(np.sum((g - BETA_THEORY * N) / e ** 2) / np.sum(1 / e ** 2))
                chi2p = float(np.sum(((BETA_THEORY * N + floor - g) / e) ** 2))
                prof.append(chi2p)
                if best_p is None or chi2p < best_p[1]:
                    best_p = (dT, chi2p, floor)
            rising = all(b >= a for a, b in zip(prof, prof[1:]))
            _, _, _, chi2_free, n_free = _fit_ladder(f, rows)
            dchi2 = best_p[1] - chi2_free
            shape = ("rises monotonically to the scan's 30 K edge"
                     if rising else "is not monotone across the scan")
            out.append([f"ladder_fit_{name}", "dT_with_beta_pinned", f"{best_p[0]:.1f}", "", "K",
                        f"the cold spot with beta pinned at theory and the floor free ({best_p[2]:.3f} MHz). chi2 {best_p[1]:.1f} for {len(g) - 1} dof, and the profile {shape} (chi2 {prof[0]:.1f} at dT = 0 against {prof[-1]:.1f} at 30 K), so the pinned model sits on the dT = 0 rail rather than being unconstrained in dT. Over the L design's {len(set(T.tolist()))} temperatures, {len(g)} rows", ""])
            out.append([f"ladder_fit_{name}", "pinned_vs_free_dchi2", f"{dchi2:.2f}", "", "",
                        f"the pinned-beta fit's chi2 minus the free fit's ({best_p[1]:.2f} against {chi2_free:.2f}), for the two parameters the free fit adds. The theory value is disfavoured by this much rather than neither refused nor confirmed", ""])
        for name, f in LAWS.items():
            beta, dT, floor, chi2, n = _fit_ladder(f, rows)
            out.append([f"ladder_fit_{name}", "beta", f"{beta:.4f}", "", "MHz per 1e12 cm^-3", f"gamma_coll(T) of the t_sweep ({n} rows) fitted as beta N(T - dT) + floor with dT on [0, 30] K. chi2 {chi2:.1f} for {n - 3} dof", ""])
            out.append([f"ladder_fit_{name}", "dT", f"{dT:.1f}", "", "K", "the cold-spot offset the fit prefers under this law (30 is the scan's edge)", ""])
            out.append([f"ladder_fit_{name}", "floor", f"{floor:.4f}", "", "MHz", "the density-independent floor the fit prefers", ""])
            out.append([f"ladder_fit_{name}", "chi2", f"{chi2:.2f}", "", "", f"for {n - 3} degrees of freedom", ""])
    out_path = _CFG.RESULTS_DIR / "density_laws.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(out)
    print(f"wrote {out_path} ({len(out) - 1} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
