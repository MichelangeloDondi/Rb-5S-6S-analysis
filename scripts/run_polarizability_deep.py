#!/usr/bin/env python3
"""The differential polarizability at the drive, re-derived to 12P and beyond,
with the quadrupole and magnetic-dipole channels bounded and every
uncertainty propagated (M41).

WHAT `polarizability.py` LEFT OUT, measured before this was written. The
993.42 nm drive sits BETWEEN two 6S resonances, 6S-8P at 1030 nm and 6S-9P at
924 nm, so each 6S-nP term is enhanced over its static size by
dE^2/(dE^2 - w^2): -13.5 for 8P, +7.3 for 9P, +4.2 for 10P, +3.4 for 11P,
+3.0 for 12P, converging to +2.23 at the ionisation limit. The module carried
every term above 8P as ONE static number, +3.4 a.u., so at the drive it
understated that group by the enhancement. And the static value it rested on
constrains the group far more loosely than its +-3.4 said: Safronova &
Safronova 2011 Table VI puts the whole 6s "Other" contribution at 49(1) a.u.,
and after the tabulated 7P, 8P and the core that leaves 4.0 +- 1.3 for
everything from 9P up. The 9P-12P elements themselves are in no held table.

THE ROUTE. `rb5s6s.coulomb_approx` computes every ns-n'p element the record
holds and reports the ratio held/computed per channel: the outer channels this
sum needs come back at 0.94 to 1.03 (6s-7p, 6s-8p, 7s-7p, 7s-8p), the compact
5s ladder at 0.4 to 0.8 and is therefore never computed here but read from its
tables. The 6s-nP elements for n >= 9 are the computed values times a
calibration factor c read from the held 6s-8p pair, the class nearest the
tail (its mean held/computed), with the step from the 6s-7p pair as its
spread, which the producer computes and writes (0.949 +- 0.041) rather than
types, and the STATIC sum they give is checked against the 4.0 +- 1.3 the
paper's own table leaves for them, which is the one independent test of the
calibration in the literature. The tail is summed explicitly to n = 40 and the
continuum bounded by the same n*^-3 law at the limiting enhancement.

THE MULTIPOLE CHANNELS. E2: the ns-nd quadrupole polarizability enters the
light shift with the field gradient, (k a0)^2 = 1.1e-7 relative to E1 per unit
polarizability ratio. it is BOUNDED here, not computed, by scaling the
paper's measured 5s quadrupole polarizability to 6s, because the Coulomb
approximation is invalid for 4d (a model-potential computation is the next
wave's). M1: the magnetic-dipole operator connects 6s only within its own
hyperfine manifold non-relativistically, and the wave's magnetic field enters
as B0 = E0/c, so the STATIC ratio to E1 is alpha_M / (alpha_E c^2) ~ 5e-6 with
the Rb85 6S interval 3A = 717 MHz (constants. the smaller interval and so the
larger bound). at the drive the magnetic polarizability is smaller still by
(dE_hf / omega)^2. Both are stated with their size, neither reaches the second
significant digit of the uncertainty, and that is the result: they are
bounded, not neglected.

THE UNCERTAINTY. A Monte Carlo over every input at its quoted sigma, run three
times: with the fine-structure pairs of each nP drawn independently, drawn
fully correlated (the same all-order calculation produces both members of a
pair, so their errors are not independent), and with every element of a state
moved together, the envelope of an unknown correlation. The largest of the
three is quoted. Two significant digits throughout.

Writes results/polarizability_deep.csv.
"""
from __future__ import annotations
import csv
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C                                          # noqa: E402
from rb5s6s.pmfmt import pm_cells                                       # noqa: E402
from rb5s6s.constants import A_6S_RB85_HZ                             # noqa: E402
from rb5s6s.polarizability import (LINES_5S, LINES_6S, E_6S_CM, CM_PER_HARTREE,   # noqa: E402
                                   CORE_5S, CORE_5S_SIG, TAIL_5S, TAIL_5S_SIG,
                                   alpha_5s, delta_alpha)
from rb5s6s.coulomb_approx import (reduced_e1_s_to_p, n_star,   # noqa: E402
                                   E_ION_CM, RYD_RB_CM, calibrate)
from rb5s6s.model_potential import continuum_polarizability   # noqa: E402
from rb5s6s.constants import DELTA_ALPHA_AU, DELTA_ALPHA_AU_ORSON2021           # noqa: E402

OUT = C.RESULTS_DIR / "polarizability_deep.csv"
LAM_DRIVE_NM = 2e7 / E_6S_CM                      # the two-photon line, NIST 6S level
W_HA = (1e7 / LAM_DRIVE_NM) / CM_PER_HARTREE
CORE_6S_SS, CORE_6S_SS_SIG = 9.076, 0.5           # S&S 2011 core; the 0.5 is Safronova 2004's spread
OTHER_6S_STATIC, OTHER_6S_STATIC_SIG = 49.0, 1.0  # S&S 2011 Table VI, 6s "Other"
N_MAX = 40
SEED = 20260912


def enh(de_cm):
    de = de_cm / CM_PER_HARTREE
    return de * de / (de * de - W_HA * W_HA)


def term(de_cm, d):
    """One line's contribution to a J=1/2 scalar polarizability at the drive, a.u."""
    de = de_cm / CM_PER_HARTREE
    return (1.0 / 6.0) * 2.0 * de * d * d / (de * de - W_HA * W_HA)


def term_static(de_cm, d):
    de = de_cm / CM_PER_HARTREE
    return (1.0 / 6.0) * 2.0 * d * d / de


def quantum_defects():
    """delta for np1/2 and np3/2 from the held 5p-12p term energies, and the
    scatter of the fit, which is the energy uncertainty of every level built
    from it."""
    e12 = [e for e, _, _ in LINES_5S][0::2]; e32 = [e for e, _, _ in LINES_5S][1::2]
    out = {}
    for j, es in ((0.5, e12), (1.5, e32)):
        ns = np.arange(5, 5 + len(es))
        d = ns - np.array([n_star(e) for e in es])
        # the defect drifts slowly with n (Ritz); a linear fit in 1/n*^2 over n>=7
        m = ns >= 7
        A = np.column_stack([np.ones(m.sum()), 1.0 / (ns[m] - d[m]) ** 2])
        coef, *_ = np.linalg.lstsq(A, d[m], rcond=None)
        resid = d[m] - A @ coef
        out[j] = (coef, float(np.std(resid, ddof=1)))
    return out


def np_energy(n, j, qd):
    coef, _ = qd[j]
    d = coef[0]
    for _ in range(5):                       # Ritz iteration
        d = coef[0] + coef[1] / (n - d) ** 2
    return E_ION_CM - RYD_RB_CM / (n - d) ** 2


def main() -> int:
    qd = quantum_defects()
    rows = []
    def add(q, key, v, e, unit, note, status="DIAGNOSTIC"):
        """A row. A value carrying an uncertainty is written through
        rb5s6s.pmfmt.pm_cells, so the uncertainty has two significant digits
        and the value the decimals to match (protocol 8a.2). an errless value
        arrives pre-formatted. Statuses are the annotator's controlled
        vocabulary: DIAGNOSTIC for the intermediate sums and elements, CALIB
        for the calibration and its literature anchors, ENVELOPE for the
        Monte Carlo spread and the value it bounds, BOUND for the multipole
        channels."""
        if e not in ("", None):
            v, e = pm_cells(float(v), float(e))
        rows.append(dict(quantity=q, key=key, value=v, err=e, unit=unit, note=note, status=status))

    # ---- 1. the calibration factor for the outer 6s-nP class
    cal = {lab: r for lab, val, sig, comp, r, src in calibrate()}
    c8 = np.mean([cal["6s-8p1/2"], cal["6s-8p3/2"]]); c7 = np.mean([cal["6s-7p1/2"], cal["6s-7p3/2"]])
    # the factor is READ from the calibration table, never typed: the 6s-8p
    # pair is the class nearest the tail and sets the value, the step from
    # the 6s-7p pair sets the spread (this was a typed literal until
    # 2026-09-12, with four of the twenty non-5s ratios inside its band)
    C_FAC, C_SIG = float(c8), float(abs(c7 - c8))
    add("calibration_6s_7p", "held/computed", f"{c7:.3f}", "", "ratio",
        "Coulomb approximation against the portal's 6s-7p pair. the class the 9P+ elements belong to", "CALIB")
    add("calibration_6s_8p", "held/computed", f"{c8:.3f}", "", "ratio",
        f"against the 6s-8p pair. the factor applied to 9P and above is this pair's mean, {c8:.3f}, with the step from the 7p pair, {abs(c7 - c8):.3f}, as its spread", "CALIB")
    add("calibration_factor", "applied", C_FAC, C_SIG, "ratio",
        "held over computed on the 6s-8p pair, the class nearest the tail. the spread is the step from the 6s-7p pair, the trend. applied to every computed 6s-nP element with n >= 9", "CALIB")

    # ---- 2. the 6s-nP elements for n = 9..N_MAX, and their static and dynamic sums
    hi_lines = []
    for n in range(9, N_MAX + 1):
        for j in (0.5, 1.5):
            e = np_energy(n, j, qd)
            d = C_FAC * reduced_e1_s_to_p(E_6S_CM, e, j)
            hi_lines.append((n, j, e, d))
    stat_hi = sum(term_static(e - E_6S_CM, d) for n, j, e, d in hi_lines)
    dyn_hi = sum(term(e - E_6S_CM, d) for n, j, e, d in hi_lines)
    # continuum and n > N_MAX: the n*^-3 tail of the last decade at the limiting enhancement
    last = [t for t in hi_lines if t[0] > N_MAX - 10]
    stat_last = sum(term_static(e - E_6S_CM, d) for n, j, e, d in last)
    # sum_{n>N} n^-3 ~ 1/(2 N^2). the last ten n contribute ~ (1/(2(N-10)^2) - 1/(2N^2))
    geom = (1.0 / (2 * N_MAX ** 2)) / (1.0 / (2 * (N_MAX - 10) ** 2) - 1.0 / (2 * N_MAX ** 2))
    stat_cont = stat_last * geom
    dyn_cont = stat_cont * enh(E_ION_CM - E_6S_CM)
    for n in (9, 10, 11, 12):
        for j in (0.5, 1.5):
            e, d = [(e, d) for nn, jj, e, d in hi_lines if nn == n and jj == j][0]
            add(f"rme_6s_{n}p{'1/2' if j == 0.5 else '3/2'}", "computed", d, d * C_SIG / C_FAC, "a.u.",
                f"Coulomb approximation times the calibration factor. level at {e:.1f} cm^-1 from the fitted quantum defect, "
                f"enhancement {enh(e - E_6S_CM):.2f} at the drive")
    add("static_6s_9p_and_above", "computed", stat_hi + stat_cont, (stat_hi + stat_cont) * 2 * C_SIG / C_FAC, "a.u.",
        f"explicit to {N_MAX}P plus the n*^-3 remainder above it, {stat_cont:.2f}, which is the DISCRETE Rydberg tail. the positive-energy continuum is its own row below")
    # the paper's own residual for the same group
    stat_7p8p = sum(term_static(e - E_6S_CM, d) for e, d, _ in LINES_6S[4:])
    other_resid = OTHER_6S_STATIC - stat_7p8p - CORE_6S_SS
    other_resid_sig = np.hypot(OTHER_6S_STATIC_SIG, np.hypot(
        2 * 0.0182 * term_static(LINES_6S[4][0] - E_6S_CM, LINES_6S[4][1]),
        2 * 0.0162 * term_static(LINES_6S[5][0] - E_6S_CM, LINES_6S[5][1])))
    add("static_6s_9p_and_above", "SS2011_residual", other_resid, other_resid_sig, "a.u.",
        f"the paper's sixth table, its 'Other' row, {OTHER_6S_STATIC}({OTHER_6S_STATIC_SIG:.0f}) minus the tabulated 7P and 8P ({stat_7p8p:.2f}) and the core ({CORE_6S_SS}). "
        "the one literature test of the calibration", "CALIB")
    # ---- 2b. THE CONTINUUM, computed and not bounded (E64, 2026-09-13). The
    # model potential's energy-normalised p waves (Seaton-continued from the np
    # series) give the 6s -> eps p share directly; the SS2011 residual minus the
    # calibrated discrete tail is kept beside it as the model-form cross-check,
    # and the difference between the two is the row's model-form term.
    E_ION_6S_CM = E_ION_CM - E_6S_CM          # the 6s threshold above 6S
    W_DRIVE_CM = 1e7 / LAM_DRIVE_NM           # the drive, half the 6S term energy
    tail_disc = stat_hi + stat_cont
    tail_disc_sig = tail_disc * 2 * C_SIG / C_FAC
    cont_resid_static = other_resid - tail_disc
    cont_resid_static_sig = float(np.hypot(other_resid_sig, tail_disc_sig))
    e_thr = (E_ION_6S_CM ** 2) / (E_ION_6S_CM ** 2 - W_DRIVE_CM ** 2)
    mpc = continuum_polarizability(E_6S_CM, W_DRIVE_CM)
    cont_dyn = mpc["alpha_at_omega"]
    join = mpc["threshold_density_continuum"] / mpc["threshold_density_discrete"]
    trk = mpc["f_bound"] + mpc["f_continuum"]
    own_frac = float(np.sqrt((1.0 - join) ** 2 + (trk - 1.0) ** 2 + (2 * 0.022) ** 2))   # the threshold join, the TRK excess, the 6S E1 class scatter on R^2
    resid_dyn_mid = cont_resid_static * (1.0 + e_thr) / 2.0
    cont_dyn_sig = float(np.hypot(cont_dyn * own_frac, abs(cont_dyn - resid_dyn_mid)))
    add("continuum_6s", "model_potential_static", f"{mpc['alpha_static']:.2f}", "", "a.u.",
        f"the 6s -> eps p continuum from rb5s6s.model_potential (energy-normalised p waves continued from the np series by the quantum defect). threshold join against the discrete law f_n n*^3: {join:.2f}. valence TRK sum {trk:.3f}")
    add("continuum_6s", "at_drive", cont_dyn, cont_dyn_sig, "a.u.",
        f"the same at the drive (enhancement {cont_dyn / mpc['alpha_static']:.2f}. the threshold's is {e_thr:.2f}). sigma is {own_frac:.0%} of the value (join, TRK, class scatter) in quadrature with the difference to the residual construction below")
    add("continuum_6s", "SS2011_residual_construction", cont_resid_static, cont_resid_static_sig, "a.u.",
        "the paper's 'Other' residual minus the calibrated discrete tail at the static limit: SS2011 groups the discrete np with n <= 26 and its discrete representation of the continuum (pp. 8-9) in one row, so the difference is the continuum's static share. the model-form cross-check of the row above")
    add("continuum_enhancement_at_threshold", "computed", f"{e_thr:.2f}", "", "", f"dE = {E_ION_6S_CM:.0f} cm^-1 above 6S at the drive's {W_DRIVE_CM:.0f} cm^-1")
    pull = ((stat_hi + stat_cont) - other_resid) / np.hypot((stat_hi + stat_cont) * 2 * C_SIG / C_FAC, other_resid_sig)
    add("static_tail_pull", "computed_vs_SS2011", f"{pull:+.2f}", "", "sigma",
        "the computed static tail against the paper's residual. a pull inside one says the calibration holds where it is used")
    add("dynamic_6s_9p_and_above", "at_drive", dyn_hi + dyn_cont, (dyn_hi + dyn_cont) * 2 * C_SIG / C_FAC, "a.u.",
        f"the same group at {LAM_DRIVE_NM:.4f} nm. the module carried +3.4 static for it")

    # ---- 3. the full 6S and 5S sums at the drive, term by term
    a6_expl = sum(term(e - E_6S_CM, d) for e, d, _ in LINES_6S)
    a6 = a6_expl + CORE_6S_SS + dyn_hi + dyn_cont + cont_dyn
    a5 = alpha_5s(LAM_DRIVE_NM)
    d_alpha = a6 - a5
    add("alpha_6s_explicit_5p_8p", "at_drive", f"{a6_expl:.2f}", "", "a.u.", "the four tabulated pairs at the drive")
    add("alpha_6s", "at_drive", f"{a6:.1f}", "", "a.u.", "explicit + core + the computed 9P-and-above group + the continuum row")
    add("alpha_5s", "at_drive", f"{a5:.1f}", "", "a.u.", "polarizability.alpha_5s: the D lines, 6P, 7P-12P tabulated, tail and core (Leonard 2015)")
    add("delta_alpha_module", "at_drive", f"{delta_alpha(LAM_DRIVE_NM):.1f}", "", "a.u.", "polarizability.delta_alpha, the value constants.DELTA_ALPHA_AU carries")

    # ---- 4. multipole channels, BOUNDED by derivation, not computed by a method
    # that fails where the term lives. The 6s quadrupole polarizability is
    # dominated by 6s-4d, 777 cm^-1 BELOW 6s, and the Coulomb approximation
    # is invalid for 4d (n* = 2.77 < l + 1 = 3: it returned <4d|r^2|4d> = 0.01
    # against the hydrogenic 81). So the term is bounded from the paper's own
    # 5s quadrupole polarizability, 6525(37) a0^5 (S&S 2011 Table V), scaled to
    # 6s by the radial moment and the denominator: <r^2> grows as n*^4, so
    # |<6s||r^2 C2||4d>|^2 is about (2.845/1.805)^4 = 6.2 times the 5s one, and
    # the 6s-4d denominator (777 cm^-1) is 25 times smaller than 5s-4d (19356),
    # for a bound of about 6525 x 6.2 x 25 = 1.0e6 a0^5 in magnitude. The E2
    # light shift carries the field gradient, (k a0)^2 = 1.12e-7 at 993 nm, so
    # E2/E1 = 1.0e6 x 1.12e-7 / 1133 = 1e-4, below the second digit of the
    # sigma. The order-of-magnitude scaling is stated as such and the row is a
    # BOUND. M1: the operator connects 6s only inside its own manifold
    # non-relativistically. with the wave's B0 = E0/c the ratio to E1 is
    # mu_B^2 / (h x 3.4 GHz) / (|Delta_alpha| c^2) = 1e-6.
    k_au = 2 * np.pi * 0.0529177 / LAM_DRIVE_NM
    a_e2_5s, a_e2_5s_sig = 6525.0, 37.0
    scale_r2 = (n_star(E_6S_CM) / n_star(0.0)) ** 4
    scale_de = 19356.0 / 777.0
    a_e2_6s_bound = a_e2_5s * scale_r2 * scale_de
    e2_rel = a_e2_6s_bound * k_au ** 2 / abs(d_alpha)
    add("alpha_E2_5s", "SS2011", a_e2_5s, a_e2_5s_sig, "a0^5",
        "the ground-state quadrupole polarizability, the paper's fifth table. The anchor the 6s bound is scaled from", "CALIB")
    add("alpha_E2_6s_bound", "scaled", f"{a_e2_6s_bound:.1e}", "", "a0^5",
        f"order of magnitude: 5s value times (n*_6s/n*_5s)^4 = {scale_r2:.1f} for the radial moment and 19356/777 = {scale_de:.0f} "
        "for the 6s-4d denominator. the Coulomb approximation cannot compute 4d and is not used", "BOUND")
    add("E2_over_E1_shift", "at_drive", f"{e2_rel:.0e}", "", "ratio",
        f"the quadrupole light shift relative to the dipole one: alpha_E2 (k a0)^2 / |Delta_alpha| with (k a0)^2 = {k_au**2:.2e}. "
        "below the second significant digit of the uncertainty, so bounded and not carried", "BOUND")
    alpha_fs = 1 / 137.035999
    hf_hz = 3.0 * A_6S_RB85_HZ                      # the Rb85 6S interval, 717 MHz: the smaller of the two isotopes', so the larger bound
    m1_rel = (alpha_fs / 2) ** 2 / (hf_hz / 6.5797e15) / abs(d_alpha) / 137.035999 ** 2
    add("M1_over_E1_shift", "at_drive", f"{m1_rel:.0e}", "", "ratio",
        "mu_B^2 over the Rb85 6s hyperfine interval 3A = 717 MHz in the wave's magnetic field B0 = E0/c: alpha_M/(alpha_E c^2), a STATIC bound. at the drive the magnetic polarizability is smaller by (dE_hf/omega)^2", "BOUND")

    # ---- 5. the Monte Carlo, independent and fully-correlated fine-structure pairs
    rng = np.random.default_rng(SEED)
    def draw(correlated, n=20000):
        """correlated: False (independent), True (fine-structure pairs), "all" (one z for every element of a state)."""
        out = np.empty(n)
        for k in range(n):
            a6k = 0.0
            zg6, zg5 = rng.normal(), rng.normal()
            for i in range(0, len(LINES_6S), 2):
                z1 = zg6 if correlated == "all" else rng.normal()
                z2 = z1 if correlated else rng.normal()
                (e1, d1, s1), (e2, d2, s2) = LINES_6S[i], LINES_6S[i + 1]
                a6k += term(e1 - E_6S_CM, d1 + s1 * z1) + term(e2 - E_6S_CM, d2 + s2 * z2)
            cfac = C_FAC + C_SIG * rng.normal()
            a6k += (dyn_hi + dyn_cont) * (cfac / C_FAC) ** 2
            a6k += CORE_6S_SS + CORE_6S_SS_SIG * rng.normal()
            a6k += cont_dyn + cont_dyn_sig * rng.normal()
            # the 5S side: every element at its sigma, pairs treated the same way
            sc = []
            for i in range(0, len(LINES_5S), 2):
                z1 = zg5 if correlated == "all" else rng.normal()
                z2 = z1 if correlated else rng.normal()
                sc += [LINES_5S[i][1] + LINES_5S[i][2] * z1, LINES_5S[i + 1][1] + LINES_5S[i + 1][2] * z2]
            a5k = alpha_5s(LAM_DRIVE_NM, scale=sc, tail=TAIL_5S + TAIL_5S_SIG * rng.normal(),
                           core=CORE_5S + CORE_5S_SIG * rng.normal())
            out[k] = a6k - a5k
        return out
    mc_i, mc_c, mc_a = draw(False), draw(True), draw("all")
    si, sc_, sa = float(np.std(mc_i, ddof=1)), float(np.std(mc_c, ddof=1)), float(np.std(mc_a, ddof=1))
    sig = max(si, sc_, sa)
    add("delta_alpha_sigma_independent", "MC", f"{si:.1f}", "", "a.u.", "every element drawn independently", "ENVELOPE")
    add("delta_alpha_sigma_pairs", "MC", f"{sc_:.1f}", "", "a.u.", "fine-structure pairs drawn fully correlated", "ENVELOPE")
    add("delta_alpha_sigma_all", "MC", f"{sa:.1f}", "", "a.u.",
        "every element of a state moved together, the envelope of an unknown correlation. the largest of the three is quoted", "ENVELOPE")
    add("delta_alpha", "at_drive", d_alpha, sig, "a.u.",
        f"alpha_6s - alpha_5s at {LAM_DRIVE_NM:.4f} nm with the 9P-and-above group summed dynamically and the continuum carried as its own term. "
        f"the package constant {DELTA_ALPHA_AU:.0f} differs by {d_alpha - DELTA_ALPHA_AU:+.0f}. Orson 2021 carries {DELTA_ALPHA_AU_ORSON2021:.0f} in magnitude", "ENVELOPE")
    add("delta_alpha_shift_from_module", "at_drive", f"{d_alpha - delta_alpha(LAM_DRIVE_NM):+.1f}", "", "a.u.",
        "against the module's own value (delta_alpha_module above). the whole move is the 9P-and-above group read dynamically instead of statically. the constant -1145.0 sits 0.4 further")
    add("delta_alpha_vs_orson", "at_drive", f"{(abs(d_alpha) - abs(DELTA_ALPHA_AU_ORSON2021)) / sig:+.1f}", "", "sigma",
        "magnitude against Orson 2021's, over this derivation's sigma alone (Orson's own uncertainty is not carried by the record)")

    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["quantity", "key", "value", "err", "unit", "note", "status"], lineterminator="\n")
        w.writeheader(); w.writerows(rows)
    for r in rows:
        print(f"  {r['quantity']:32s} {r['key']:18s} {r['value']:>10s} {('+- ' + r['err']) if r['err'] else '':>10s} {r['unit']}")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
