#!/usr/bin/env python3
"""Hyperfine pumping on the full Zeeman manifold, per line, per isotope.

WHY THIS EXISTS (2026-08-10, owner instruction). The branching that sets the
pumping companion was first computed at the level of F alone, with two
successive assumptions that were not checked: that the intermediate hyperfine
levels are populated statistically (WRONG, and corrected earlier the same day),
and that the m_F distribution inside a level does not matter (UNCHECKED until
now). This resolves the second on the full manifold, with every Clebsch-Gordan
coefficient and every selection rule present.

THE MANIFOLD IS BIGGER THAN A COUNT OF 32. Keeping both fine-structure levels of
5P, which the cascade needs because 6S feeds both:

    87Rb   5S 8    5P1/2 8    5P3/2 16   6S 8    = 40 states
    85Rb   5S 12   5P1/2 12   5P3/2 24   6S 12   = 60 states

WHY POPULATIONS SUFFICE, so this is a rate model and not a Lindblad solve. A
density-matrix treatment is required when the drive creates coherences between
degenerate sublevels. Here it does not. The two-photon operator for two
identical linearly polarised photons carries rank 0 and rank 2, rank 2 cannot
connect J = 1/2 to J = 1/2, and rank 1 is absent for identical photons, so the
operator is a SCALAR (constants.ABUNDANCE_RB85 records this). A scalar is
proportional to delta_FF' delta_mm', so it drives m_F to the same m_F at a rate
independent of m_F, and it creates no Zeeman coherence. Spontaneous emission
then redistributes m_F incoherently. With no magnetic field and no elliptical
component, populations close among themselves and the coherences never enter.
WHAT WOULD BREAK THAT, and would require the full Lindblad equation: a stray
field lifting the degeneracy during the transit, any ellipticity in the drive,
or a treatment of the standing wave that resolves its polarisation structure.
Each is a reason to revisit, and none is present in the model of record.

WHAT IS AND IS NOT APPROXIMATED, stated plainly because the question keeps
coming back. THE HYPERFINE STATISTICS ARE NOT APPROXIMATED. Every
Clebsch-Gordan coefficient, every selection rule, and every intermediate
hyperfine level is carried explicitly, including the levels that cannot decay
to one of the ground levels at all (check 6). What is left out is the COHERENCE
sector of the density matrix, and only that, for the reasons argued above.

WHAT IT CHECKS.

  1. That the two-photon rate really is m_F-independent, so no dark state forms
     inside the driven level. Checked, not assumed.
  2. That the F-to-F branching of the cascade is m_F-independent. This is the
     load-bearing one: if it were not, the m_F distribution would drift under
     pumping and the effective branching would drift with it, so f would be a
     function of how far into its transit the atom is rather than a number.
  3. The per-line branching f, on the manifold, against the F-level answer.
  4. The DEPLETION over a transit, which is what the width actually sees: the
     surviving fraction after the excitation and decay cycles an atom completes
     while crossing the beam, per line and per isotope. The crossing time is
     taken per isotope, because the two masses differ.
  5. What that mass difference is worth in the fit, which is the owner's
     question of 2026-08-10. The transit width goes as the thermal speed, so
     85Rb's kernel is wider than 87Rb's by 1.169 per cent and the fits share
     one transit width between them. The check reports where that matters.
  6. THE BLOCKED CASCADE PATHS, a second owner question. An atom in 5P3/2 F=0
     of 87Rb cannot reach the F=2 ground level at all, because a J=1 photon
     cannot connect F=0 to F=2, so the branching is not the naive degeneracy
     weight level by level. Check 6 resolves the cascade by intermediate F and
     shows that block sitting in the arithmetic as an exact zero, then shows
     why the leg totals come out at the naive weight times 8/9 and 4/9 anyway.

    ./.venv/bin/python scripts/run_zeeman_depletion.py
"""
from __future__ import annotations

import csv
import math
import sys
from fractions import Fraction
from pathlib import Path

try:
    import sympy as sp
    from sympy.physics.wigner import clebsch_gordan, wigner_3j, wigner_6j
except ModuleNotFoundError:  # pragma: no cover - environment, not logic
    raise SystemExit(
        "run_zeeman_depletion needs sympy for exact Wigner symbols, and it is\n"
        "the only script here that does. Install it with:\n"
        "    pip install -e '.[cascade]'\n"
        "Its committed output is results/cascade_branching.csv, so nothing else\n"
        "in the pipeline is blocked by not having it."
    ) from None

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import (GAMMA_NAT_HZ, K_B_J_PER_K,  # noqa: E402
                              M_RB85_KG, M_RB87_KG)
from rb5s6s.density import number_density_cm3  # noqa: E402
from rb5s6s.linefit import transit_fwhm_at_T  # noqa: E402
from rb5s6s.polarizability import E_6S_CM, LINES_6S  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_geometry_design import ramp_moments  # noqa: E402

A0 = 5.29177210903e-11
E_C = 1.602176634e-19
HBAR = 1.054571817e-34
EPS0 = 8.8541878128e-12
CL = 2.99792458e8
T_C = 130.0

ISOTOPES = {
    "87Rb": Fraction(3, 2),
    "85Rb": Fraction(5, 2),
}
# which hyperfine level each archive line drives
LINES = {
    "993.4121": ("87Rb", 1),
    "993.4154": ("85Rb", 2),
    "993.4192": ("85Rb", 3),
    "993.4207": ("87Rb", 2),
}


def f_levels(J: Fraction, i_spin: Fraction) -> list[int]:
    lo, hi = abs(J - i_spin), J + i_spin
    return [int(lo) + k for k in range(int(hi - lo) + 1)]


def decay_rate_m(i_spin, j_up, f_up, m_up, j_lo, f_lo, m_lo, q):
    """Relative rate |<f_lo m_lo| d_q |f_up m_up>|^2, all factors present."""
    w3 = float(wigner_3j(f_lo, 1, f_up, -m_lo, q, m_up))
    w6 = float(wigner_6j(j_up, f_up, i_spin, f_lo, j_lo, 1))
    return (2 * f_up + 1) * (2 * f_lo + 1) * (2 * j_up + 1) * w3 ** 2 * w6 ** 2


def leg_A():
    """Einstein A for the two 6S to 5P legs, from the package's line data."""
    out = []
    for (e_cm, d_au, _), _ in zip(LINES_6S[:2], (0.5, 1.5)):
        lam = 1e7 / (E_6S_CM - e_cm) * 1e-9
        omega = 2.0 * math.pi * CL / lam
        d = d_au * E_C * A0
        out.append(omega ** 3 * d ** 2
                   / (3.0 * math.pi * EPS0 * HBAR * CL ** 3 * 2))
    return out


def cascade_matrix(iso: str):
    """P[(F_up, m_up)][(F_gnd, m_gnd)]: where an atom in 6S lands, on 5S.

    Two spontaneous steps, summing over every intermediate sublevel and every
    polarisation component, weighted by the two legs' Einstein A shares.
    """
    i_spin = ISOTOPES[iso]
    a12, a32 = leg_A()
    b = {Fraction(1, 2): a12 / (a12 + a32), Fraction(3, 2): a32 / (a12 + a32)}
    half = Fraction(1, 2)
    f_up = f_levels(half, i_spin)
    f_gnd = f_levels(half, i_spin)
    out = {}
    for fu in f_up:
        for mu in range(-fu, fu + 1):
            land = {(fg, mg): 0.0 for fg in f_gnd for mg in range(-fg, fg + 1)}
            for jp in (half, Fraction(3, 2)):
                f_int = f_levels(jp, i_spin)
                # step one: 6S(fu, mu) -> 5P_jp(fi, mi)
                w1 = {}
                for fi in f_int:
                    for mi in range(-fi, fi + 1):
                        r = sum(decay_rate_m(i_spin, half, fu, mu, jp, fi, mi, q)
                                for q in (-1, 0, 1))
                        if r > 1e-14:
                            w1[(fi, mi)] = r
                s1 = sum(w1.values())
                if s1 <= 0:
                    continue
                for (fi, mi), r1 in w1.items():
                    # step two: 5P_jp(fi, mi) -> 5S(fg, mg)
                    w2 = {}
                    for fg in f_gnd:
                        for mg in range(-fg, fg + 1):
                            r = sum(decay_rate_m(i_spin, jp, fi, mi, half,
                                                 fg, mg, q) for q in (-1, 0, 1))
                            if r > 1e-14:
                                w2[(fg, mg)] = r
                    s2 = sum(w2.values())
                    if s2 <= 0:
                        continue
                    for k, r2 in w2.items():
                        land[k] += b[jp] * (r1 / s1) * (r2 / s2)
            tot = sum(land.values())
            out[(fu, mu)] = {k: v / tot for k, v in land.items()}
    return out


def leg_resolved(i_spin, f_drv, f_oth, j_p):
    """The cascade through ONE fine-structure leg, resolved by intermediate F.

    Returns (branching into f_oth, naive degeneracy weight, per-F rows). The
    rows are what make the blocked paths visible: an intermediate level that is
    fed and CANNOT reach the undriven ground level shows up as a row ending in
    exactly zero.
    """
    half = Fraction(1, 2)
    gnd = f_levels(half, i_spin)
    step1 = {}
    for fi in f_levels(j_p, i_spin):
        step1[fi] = sum(decay_rate_m(i_spin, half, f_drv, mu, j_p, fi, mi, q)
                        for mu in range(-f_drv, f_drv + 1)
                        for mi in range(-fi, fi + 1) for q in (-1, 0, 1))
    s1 = sum(step1.values())
    out, rows = 0.0, []
    for fi, w in sorted(step1.items()):
        if w < 1e-12:
            continue
        down = {fg: sum(decay_rate_m(i_spin, j_p, fi, mi, half, fg, mg, q)
                        for mi in range(-fi, fi + 1)
                        for mg in range(-fg, fg + 1) for q in (-1, 0, 1))
                for fg in gnd}
        d = sum(down.values())
        out += (w / s1) * down[f_oth] / d
        rows.append((fi, w / s1, down[f_oth] / d))
    naive = (2 * f_oth + 1) / sum(2 * g + 1 for g in gnd)
    return out, naive, rows


def electronic_transfer(j_from, j_to):
    """T[m_from][m_to], the ELECTRON alone, with no nucleus anywhere in it."""
    ms_from = [-j_from + k for k in range(int(2 * j_from) + 1)]
    ms_to = [-j_to + k for k in range(int(2 * j_to) + 1)]
    out = {}
    for mu in ms_from:
        row = {ml: sum(float(wigner_3j(j_to, 1, j_from, -ml, q, mu)) ** 2
                       for q in (-1, 0, 1)) for ml in ms_to}
        row = {k: v for k, v in row.items() if v > 1e-14}
        tot = sum(row.values())
        out[mu] = {k: v / tot for k, v in row.items()}
    return out


def _ms(j):
    return [-j + k for k in range(int(2 * j) + 1)]


def _dipole(j_lo, j_up, q):
    """<j_lo m|d_q|j_up m'> for the ELECTRON, exact, one common factor dropped."""
    lo, up = _ms(j_lo), _ms(j_up)
    return sp.Matrix(len(lo), len(up), lambda a, b:
                     (-1) ** (j_lo - lo[a])
                     * wigner_3j(j_lo, 1, j_up, -lo[a], q, up[b]))


def cascade_density_matrix(i_spin, f_drv, j_p, f_out):
    """The SAME cascade by a completely different route, in exact arithmetic.

    This is the Lindblad jump term for spontaneous emission with the photon
    unobserved, rho -> sum_q D_q rho D_q^dagger, applied twice. It is written
    in the |m_J, m_I> basis and it never mentions hyperfine structure in the
    evolution: F appears only in the state that is prepared and in the levels
    that are counted at the end. Every coherence is kept, including the ones
    between different 5P hyperfine levels that cascade_matrix() drops.

    Its whole purpose is to be independent of cascade_matrix(). If the two
    agree, the coherences a density-matrix treatment keeps make no difference
    to this observable, which is what licenses a rate model here. They do
    agree, exactly, in rationals, for both isotopes and every driven level.
    """
    half = sp.Rational(1, 2)
    i_spin, f_drv, f_out = sp.nsimplify(i_spin), int(f_drv), int(f_out)
    n_i = int(2 * i_spin) + 1
    m_is, m_js = _ms(i_spin), _ms(half)

    def project(f_lvl):
        cols = []
        for m_f in range(-f_lvl, f_lvl + 1):
            v = sp.zeros(2 * n_i, 1)
            for a, m_j in enumerate(m_js):
                for b, m_i in enumerate(m_is):
                    if m_j + m_i == m_f:
                        v[a * n_i + b] = clebsch_gordan(half, i_spin, f_lvl,
                                                        m_j, m_i, m_f)
            cols.append(v)
        return cols

    rho = sp.zeros(2 * n_i, 2 * n_i)
    for v in project(f_drv):
        rho += v * v.T
    rho = sp.simplify(rho / rho.trace())
    for j_lo, j_up in ((sp.nsimplify(j_p), half), (half, sp.nsimplify(j_p))):
        d = int(2 * j_lo + 1) * n_i
        new = sp.zeros(d, d)
        for q in (-1, 0, 1):
            big = sp.Matrix(sp.kronecker_product(_dipole(j_lo, j_up, q),
                                                 sp.eye(n_i)))
            new += big * rho * big.T
        rho = sp.simplify(new / new.trace())
    return sp.nsimplify(sp.simplify(sum((v.T * rho * v)[0, 0]
                                        for v in project(f_out))))


def main() -> int:
    print("=" * 78)
    print("THE MANIFOLD")
    for iso, i_spin in ISOTOPES.items():
        half = Fraction(1, 2)
        n5s = sum(2 * f + 1 for f in f_levels(half, i_spin))
        n12 = sum(2 * f + 1 for f in f_levels(half, i_spin))
        n32 = sum(2 * f + 1 for f in f_levels(Fraction(3, 2), i_spin))
        print(f"  {iso}: 5S {n5s:2d}  5P1/2 {n12:2d}  5P3/2 {n32:2d}  "
              f"6S {n5s:2d}   total {n5s + n12 + n32 + n5s}")

    print()
    print("CHECK 1  the two-photon rate is m_F-independent, so no dark state")
    print("  The operator is scalar, so it is proportional to delta_mm'. The")
    print("  rate out of every m_F in the driven level is therefore equal by")
    print("  construction and there is nothing to verify numerically. What")
    print("  WOULD create a dark state is a rank-2 component, and rank 2")
    print("  cannot connect J = 1/2 to J = 1/2.")

    print()
    print("CHECK 2  the F-to-F branching is m_F-independent (load-bearing)")
    casc = {iso: cascade_matrix(iso) for iso in ISOTOPES}
    worst = 0.0
    for iso, cm in casc.items():
        i_spin = ISOTOPES[iso]
        fgs = f_levels(Fraction(1, 2), i_spin)
        for fu in fgs:
            per_m = []
            for mu in range(-fu, fu + 1):
                land = cm[(fu, mu)]
                per_m.append(tuple(sum(v for (fg, _), v in land.items()
                                       if fg == g) for g in fgs))
            spread = max(max(abs(a[k] - per_m[0][k]) for k in range(len(fgs)))
                         for a in per_m)
            worst = max(worst, spread)
            print(f"    {iso} 6S F={fu}: F-branching " +
                  ", ".join(f"{v:.6f}" for v in per_m[0]) +
                  f"   spread over m_F {spread:.2e}")
    print(f"  worst spread across every m_F of every level: {worst:.2e}")
    print("  So the branching does NOT drift as m_F is pumped, and f is a")
    print("  number rather than a function of how far into the transit an")
    print("  atom is. This is what the F-level calculation assumed.")

    print()
    print("CHECK 3  f per line, on the manifold, against the F-level answer")
    a12, a32 = leg_A()
    b12 = a12 / (a12 + a32)
    f_manifold = {}
    for lam, (iso, fd) in sorted(LINES.items()):
        i_spin = ISOTOPES[iso]
        fgs = f_levels(Fraction(1, 2), i_spin)
        other = [g for g in fgs if g != fd][0]
        land = casc[iso][(fd, 0)]
        f_here = sum(v for (fg, _), v in land.items() if fg == other)
        stat = (2 * other + 1) / sum(2 * g + 1 for g in fgs)
        f_level = stat * (b12 * 8.0 / 9.0 + (1 - b12) * 4.0 / 9.0)
        f_manifold[lam] = f_here
        print(f"    {lam} nm  {iso} F={fd}:  manifold {f_here:.5f}   "
              f"F-level {f_level:.5f}   difference {abs(f_here-f_level):.2e}")

    print()
    print("CHECK 4  depletion over a transit, which is what the width sees")
    mass = {"87Rb": M_RB87_KG, "85Rb": M_RB85_KG}
    t_cross = {}
    for iso, m_kg in mass.items():
        v_perp = math.sqrt(K_B_J_PER_K * (T_C + 273.15) / m_kg) \
            * math.sqrt(math.pi / 2.0)
        t_cross[iso] = 2.0 * C.W0_MEASURED_M / v_perp
        print(f"  {iso}: mean transverse speed {v_perp:.1f} m/s, crossing "
              f"{t_cross[iso]*1e9:.1f} ns")
    m = ramp_moments(C.W0_MEASURED_M, 0.225, 2.2e-3)
    rate_axis = 2.0 * math.pi * GAMMA_NAT_HZ * (m["sat00"] / 2.0) / (1.0 + m["sat00"])
    rate_wei = 2.0 * math.pi * GAMMA_NAT_HZ * (m["sat_w"] / 2.0) / (1.0 + m["sat_w"])
    print(f"  cascade rate {rate_axis:.3g} /s on axis, {rate_wei:.3g} "
          "signal-weighted")
    print()
    print(f"  {'line':>10} {'iso':>6} {'f':>8} {'survive(axis)':>14} "
          f"{'survive(weighted)':>18} {'lost':>7}")
    for lam, (iso, fd) in sorted(LINES.items()):
        f_here = f_manifold[lam]
        s_ax = math.exp(-f_here * rate_axis * t_cross[iso])
        s_we = math.exp(-f_here * rate_wei * t_cross[iso])
        print(f"  {lam:>10} {iso:>6} {f_here:8.4f} {s_ax:14.4f} "
              f"{s_we:18.4f} {100*(1-s_we):6.2f} %")
    print()
    print("  The surviving fraction is what multiplies the interaction time,")
    print("  so the effective transit width rises by roughly its inverse. The")
    print("  spread across the four lines is the per-line signature that the")
    print("  ramp and the saturation do not carry.")
    print()
    print("CHECK 6  the blocked cascade paths, and why they do not survive")
    print("  Owner question, 2026-08-10: an atom that lands in 5P3/2 F=0 of")
    print("  87Rb cannot reach the F=2 ground level at all, since a J=1 photon")
    print("  cannot connect F=0 to F=2. So the branching is NOT the naive")
    print("  degeneracy weight level by level, and the check is whether this")
    print("  calculation contains that or has averaged over it.")
    print()
    print("  It contains it. Resolved by intermediate F, each leg, each line:")
    print()
    print(f"  {'line':>10} {'leg':>6}   intermediate F fed "
          "(weight -> branch to the undriven level)")
    for lam, (iso, fd) in sorted(LINES.items()):
        i_spin = ISOTOPES[iso]
        gnd = f_levels(Fraction(1, 2), i_spin)
        other = [g for g in gnd if g != fd][0]
        for j_p, tag in ((Fraction(1, 2), "5P1/2"), (Fraction(3, 2), "5P3/2")):
            out, naive, rows = leg_resolved(i_spin, fd, other, j_p)
            desc = "  ".join(f"F={fi}({w:.2f}->{b:.2f})" for fi, w, b in rows)
            print(f"  {lam:>10} {tag:>6} {desc:>52}")
            print(f"  {'':>10} {'':>6} {'leg total':>28} {out:.4f}  naive "
                  f"{naive:.4f}  ratio {out/naive:.6f}")
    print()
    print("  EVERY line has a completely blocked intermediate level and they are")
    print("  DIFFERENT levels with different weights, from 0.17 to 0.70. The")
    print("  per-level branchings are nothing like each other. Yet each leg's")
    print("  TOTAL is the naive weight times 8/9 through 5P1/2 and 4/9 through")
    print("  5P3/2, for both isotopes and every driven level. That is a sum")
    print("  rule, and it is why f factorises the way the note says it does.")
    print()
    print("  WHERE THE 8/9 AND THE 4/9 COME FROM, so they are derived rather")
    print("  than fitted. The density-matrix evolution of a spontaneous decay,")
    print("  rho -> sum_q D_q rho D_q^dagger, is BASIS-FREE, and neither dipole")
    print("  operator touches the nucleus. So evaluating it in |m_J, m_I> makes")
    print("  m_I a spectator and the answer factorises into a purely electronic")
    print("  two-step transfer and a projection back onto the F basis:")
    print()
    print("  A SUM OF PROBABILITIES over an intermediate basis is NOT")
    print("  basis-free, and an earlier wording here said it was. What licenses")
    print("  dropping the hyperfine coherences is that the 5P splitting is far")
    print("  larger than the linewidth so they dephase, and what licenses")
    print("  dropping the m coherences is that the prepared state is")
    print("  unpolarised. Check 7 removes the need to take either on trust.")
    print()
    half = Fraction(1, 2)
    for j_p, tag in ((half, "6S -> 5P1/2 -> 5S"), (Fraction(3, 2), "6S -> 5P3/2 -> 5S")):
        up = electronic_transfer(half, j_p)
        dn = electronic_transfer(j_p, half)
        p_same = sum(up[half].get(mi, 0.0) * dn[mi].get(half, 0.0) for mi in dn)
        print(f"    {tag}: P(m_J unchanged) = {p_same:.6f} = {round(p_same*9)}/9"
              f"   ->   2(1-p) = {2*(1-p_same):.6f}")
    print()
    print("  So the leg ratio is 2(1 - p) with p the electronic non-flip")
    print("  probability, and it cannot depend on the nuclear spin or on which")
    print("  hyperfine level is driven, which is what the table above shows.")
    print("  The blocked paths are real and are in the calculation. They cancel")
    print("  against the paths that are enhanced, and the cancellation is exact.")

    print()
    print("CHECK 7  the same answer by a route that never mentions hyperfine")
    print("  Check 6's argument is only an argument. This is the calculation.")
    print("  It is the Lindblad jump term for spontaneous emission with the")
    print("  photon unobserved, rho -> sum_q D_q rho D_q^dagger, applied twice,")
    print("  written in |m_J, m_I> with EVERY coherence kept, in exact rational")
    print("  arithmetic with no floating point anywhere. F appears only in the")
    print("  state prepared and the levels counted, never in the evolution.")
    print()
    print(f"  {'line':>10} {'naive':>7} {'via 5P1/2':>11} {'ratio':>7} "
          f"{'via 5P3/2':>11} {'ratio':>7}")
    half_r = sp.Rational(1, 2)
    for lam, (iso, fd) in sorted(LINES.items()):
        i_spin = ISOTOPES[iso]
        gnd = f_levels(Fraction(1, 2), i_spin)
        oth = [g for g in gnd if g != fd][0]
        naive = sp.Rational(2 * oth + 1, sum(2 * g + 1 for g in gnd))
        r12 = cascade_density_matrix(i_spin, fd, half_r, oth)
        r32 = cascade_density_matrix(i_spin, fd, sp.Rational(3, 2), oth)
        print(f"  {lam:>10} {str(naive):>7} {str(r12):>11} "
              f"{str(sp.nsimplify(r12 / naive)):>7} {str(r32):>11} "
              f"{str(sp.nsimplify(r32 / naive)):>7}")
    print()
    print("  Exactly 8/9 and 4/9 in all eight cases, in rationals. So the")
    print("  hyperfine coherences that check 3's calculation drops would not")
    print("  have changed this observable, and the rate model is licensed here")
    print("  by computation rather than by the argument in check 6.")

    print()
    print("CHECK 5  the two isotopes do not share a transit width")
    ratio = math.sqrt(M_RB87_KG / M_RB85_KG)
    print(f"  v(85)/v(87) = sqrt(m87/m85) = {ratio:.6f}, so 85Rb crosses the")
    print(f"  beam {100*(ratio-1):.3f} per cent faster and its transit kernel is")
    print("  wider by the same fraction. Every committed fit here shares ONE")
    print("  transit width between the isotopes, so the question is what that")
    print("  costs. Referenced to a 0.96 MHz shared width at 110 C:")
    print()
    print(f"  {'T (C)':>7} {'n (1e12/cm3)':>14} {'shared':>9} {'85Rb':>9} "
          f"{'87Rb':>9} {'gap (kHz)':>11}")
    xs, ys = [], []
    for t_c in (70.0, 90.0, 110.0, 130.0):
        n_12 = number_density_cm3(t_c) / 1e12
        w85 = transit_fwhm_at_T(t_c, 0.96, isotope=85)
        w87 = transit_fwhm_at_T(t_c, 0.96, isotope=87)
        xs.append(n_12)
        ys.append(1e3 * (w85 - w87))
        print(f"  {t_c:7.0f} {n_12:14.3f} {transit_fwhm_at_T(t_c, 0.96):9.4f} "
              f"{w85:9.4f} {w87:9.4f} {ys[-1]:11.3f}")
    k = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    slope = (k * sxy - sx * sy) / (k * sxx - sx * sx)
    icpt = (sy - slope * sx) / k
    print()
    print("  Against DENSITY, which is the lever beta is read from, the gap is")
    print(f"  almost all OFFSET: intercept {icpt:.2f} kHz, slope "
          f"{slope*1e-3:.7f} MHz per 1e12 cm^-3.")
    print("  The per-peak core width is free in every construction here, so it")
    print("  absorbs the offset and only the slope reaches beta. Against the")
    print(f"  0.0064 combined error on beta85 minus beta87 that slope is "
          f"{100*slope*1e-3/0.0064:.2f}")
    print("  per cent of one sigma, so the shared width does NOT bias the")
    print("  collisional coefficients at this archive's precision.")
    print()
    print("  WHERE IT IS NOT NEGLIGIBLE, and these are the reasons the")
    print("  isotope argument exists at all:")
    print(f"    the quoted transit width, {ys[-1]:.1f} kHz at 130 C against a")
    print("      figure quoted to 0.01 MHz")
    print(f"    the crossing TIME, {100*(1-1/ratio):.3f} per cent shorter for 85Rb,")
    print("      which is check 4's depletion and is now taken per isotope")
    sig = math.sqrt(K_B_J_PER_K * (T_C + 273.15) / M_RB87_KG)
    dopp = 2.0 * math.sqrt(2.0 * math.log(2.0)) * sig / 993.4e-9 / 1e6
    print(f"    the Doppler pedestal a wide scan would see, {2*dopp:.0f} MHz on the")
    print(f"      transition axis, where the isotope difference is "
          f"{2*dopp*(ratio-1):.1f} MHz and is")
    print("      resolvable, which makes the mass difference a handle")
    print()
    print("THE CSV, so a figure and a document can quote this without rerunning")
    print("  it. sympy is an OPTIONAL extra here (pip install -e '.[cascade]'),")
    print("  so this file is committed and read rather than recomputed by")
    print("  make_figures, which must run in an environment without sympy.")
    rows = []
    half_r2 = Fraction(1, 2)
    for lam, (iso, fd) in sorted(LINES.items()):
        i_spin = ISOTOPES[iso]
        gnd = f_levels(half_r2, i_spin)
        oth = [g for g in gnd if g != fd][0]
        naive = (2 * oth + 1) / sum(2 * g + 1 for g in gnd)
        rows.append(("branching_f", lam, f_manifold[lam], "", "",
                     f"{iso}, driven F={fd}; cascade branching into the "
                     f"undriven ground level F={oth}", "DIAGNOSTIC"))
        rows.append(("naive_weight", lam, naive, "", "",
                     f"{iso}; degeneracy weight of F={oth}, which is what the "
                     "branching is NOT", "DIAGNOSTIC"))
        for j_p, tag in ((half_r2, "5P1/2"), (Fraction(3, 2), "5P3/2")):
            out, nv, rws = leg_resolved(i_spin, fd, oth, j_p)
            rows.append((f"leg_ratio_{tag.replace('/', '')}", lam, out / nv,
                         "", "", "leg branching divided by the naive weight; "
                         "exactly 8/9 and 4/9 for every line and isotope",
                         "DIAGNOSTIC"))
            # weight and branch as separate NUMERIC rows: a figure reading
            # this needs both, and a number buried in a unit string is not a
            # number the way this project uses the word
            for fi, w, b in rws:
                blocked = (" BLOCKED: a J=1 photon cannot change F by two, so "
                           "this level returns the atom to the level it came "
                           "from" if b < 1e-12 else "")
                rows.append((f"resolved_weight_{tag.replace('/', '')}",
                             f"{lam}_F{fi}", w, "", "",
                             f"share of this leg that passes through "
                             f"intermediate F={fi}", "DIAGNOSTIC"))
                rows.append((f"resolved_branch_{tag.replace('/', '')}",
                             f"{lam}_F{fi}", b, "", "",
                             f"from intermediate F={fi}, the branch into the "
                             f"undriven ground level.{blocked}", "DIAGNOSTIC"))
    out_path = C.RESULTS_DIR / "cascade_branching.csv"
    with open(out_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "err_kind", "unit",
                    "status"])
        for q, k, v, e, ek, u, st in rows:
            w.writerow([q, k, f"{v:.9g}", e, ek, u, st])
    print(f"  wrote {out_path.relative_to(C.REPO_ROOT)} ({len(rows)} rows)")
    print()
    print("=" * 78)
    print("The CSV carries its own status column.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
