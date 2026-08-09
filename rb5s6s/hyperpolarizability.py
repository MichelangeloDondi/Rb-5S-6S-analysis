"""Trap-design corrections at the 5S-6S magic crossings: the
fourth-order (hyperpolarizability) differential shift, the vector
shift under imperfect polarization, and trap-photon scattering.

Who this is for. A trap design needs three numbers beyond the magic
wavelength itself: how fast the residual shift grows with depth, how
pure the polarization has to be, and how often the trapped atom
scatters trap photons. This module computes all three for every
polarizability crossing of the 5S-6S pair, including the
pole-adjacent crossings that magic_wavelengths() deliberately
excludes, so the exclusion is priced rather than asserted.

Method. Fourth-order Rayleigh-Schroedinger perturbation theory in
the Floquet (atom plus photon number) basis over the bound levels
5S-7S, 5P-8P, 4D and 5D, with the same line data, scalar prefactor
and tail-plus-core treatment as polarizability.py. The vector shift
is a direct sum over the line lists with explicit angular weights.
Scattering uses the decay rate of the admixed intermediate state:
complete for the downward 6S-5P channels (5P decays only to 5S,
which is in the lists), a lower bound for upward channels (the
partner's other decay paths are not in the lists).

Naming, since three words are in use for one coefficient. The
literature calls it the hyperpolarizability, which is why the file
carries that name. The documents call the quantity the fourth-order
differential shift, which is what it is. The code says `quartic`,
which is how it enters the field expansion. They are the same
number.

Grade. Everything here is CALCULATED and carries an envelope grade
of a factor of two, set by the P-D matrix elements and checked by
the anchors in tests/test_hyperpolarizability.py: the machinery
reproduces the exact two-level quartic to 1e-9, the linear shift
reproduces the module polarizabilities at every crossing, the
Einstein-A chain reproduces the D2 width and the measured 6S
lifetime, and the vector sum is polarization-trace invariant.
Higher even states and the two-photon continuum add corrections
estimated elsewhere to order of magnitude only (about a tenth of
the 1204 nm coefficient); they are not part of this module.

Run:  python -m rb5s6s.hyperpolarizability
"""
from __future__ import annotations

from fractions import Fraction as Fr
from math import factorial, sqrt

import numpy as np
from scipy.optimize import brentq

from .polarizability import (
    LINES_5S, LINES_6S, LINES_7S, TAIL_5S, TAIL_6S, CORE_5S, CORE_6S,
    E_6S_CM, E_7S_CM, CM_PER_HARTREE, alpha_5s, alpha_6s, delta_alpha,
)

HARTREE_HZ = 6.579683920502e15      # Hartree in Hz (CODATA)
ALPHA_FS = 1.0 / 137.035999084      # fine-structure constant (CODATA)
AU_RATE_HZ = 4.134137e16            # atomic unit of angular rate, rad/s
CM = CM_PER_HARTREE
_H, _TH, _FH = Fr(1, 2), Fr(3, 2), Fr(5, 2)

# ---------------------------------------------------------------- levels
# P energies come from the committed line lists (they are the same
# transition energies polarizability.py uses). D fine-structure
# energies above the 5S ground state are NIST ASD values
# (Sansonetti's Rb compilation), the one external input this module
# adds beyond the matrix-element tables below.
_PN = ["5P1/2", "5P3/2", "6P1/2", "6P3/2", "7P1/2", "7P3/2",
       "8P1/2", "8P3/2"]
LEVELS = {"5S": (0, _H, 0.0), "6S": (0, _H, E_6S_CM),
          "7S": (0, _H, E_7S_CM)}
for _nm, (_e, _d, _s) in zip(_PN, LINES_5S[:8]):
    LEVELS[_nm] = (1, _H if _nm.endswith("1/2") else _TH, _e)
LEVELS.update({
    "4D3/2": (2, _TH, 19355.203), "4D5/2": (2, _FH, 19355.649),
    "5D3/2": (2, _TH, 25700.536), "5D5/2": (2, _FH, 25703.498),
})

# S-P reduced matrix elements: magnitudes are the committed line
# lists. P-D magnitudes by family: the 5P-4D family is anchored on
# the measured 4D lifetimes, 7P-4D agrees with the all-order values
# to 5 percent, the 5P3/2-5D5/2 row is the Hamilton 2023
# measurement with its LS partners, and the 6P-4D, 6P-5D and 7P-5D
# families are the Safronova-Williams-Clark all-order values
# (PRA 69, 022509), cross-checked against a model-potential
# integration during the 2026-08-08 adversarial review.
_PD_MAG = {
    ("5P1/2", "4D3/2"): 8.02, ("5P3/2", "4D3/2"): 3.65,
    ("5P3/2", "4D5/2"): 10.90,
    ("5P1/2", "5D3/2"): 1.40, ("5P3/2", "5D3/2"): 0.60,
    ("5P3/2", "5D5/2"): 1.80,
    ("6P1/2", "4D3/2"): 4.717, ("6P3/2", "4D3/2"): 2.055,
    ("6P3/2", "4D5/2"): 6.184,
    ("6P1/2", "5D3/2"): 18.106, ("6P3/2", "5D3/2"): 8.160,
    ("6P3/2", "5D5/2"): 24.491,
    ("7P1/2", "4D3/2"): 1.00, ("7P3/2", "4D3/2"): 0.45,
    ("7P3/2", "4D5/2"): 1.35,
    ("7P1/2", "5D3/2"): 9.768, ("7P3/2", "5D3/2"): 4.242,
    ("7P3/2", "5D5/2"): 12.798,
}

# Radial signs, in the convention where every radial wavefunction is
# positive at large r. They matter at fourth order because closed
# loops through different intermediate states interfere, and the
# loop products are physical (they cannot be absorbed into state
# phases). Two independent integrations agree on every sign below
# and on all loop-invariant products: a Bates-Damgaard Coulomb
# approximation and a Marinescu-model-potential Numerov integration
# (both 2026-08-08). The published tables carry magnitudes only, so
# these signs are computed inputs, not literature values. The sign
# is a property of the radial pair and is the same for both
# fine-structure partners, so it is keyed by the nl pair.
_RADIAL_SIGN = {
    ("5S", "5P"): +1, ("5S", "6P"): -1, ("5S", "7P"): +1,
    ("5S", "8P"): -1,
    ("6S", "5P"): +1, ("6S", "6P"): +1, ("6S", "7P"): -1,
    ("6S", "8P"): +1,
    ("7S", "5P"): -1, ("7S", "6P"): +1, ("7S", "7P"): +1,
    ("7S", "8P"): -1,
    ("5P", "4D"): +1, ("5P", "5D"): +1,
    ("6P", "4D"): +1, ("6P", "5D"): +1,
    ("7P", "4D"): -1, ("7P", "5D"): +1,
    ("8P", "4D"): +1, ("8P", "5D"): -1,
}


def _pair_key(a: str, b: str):
    # every level label is one digit plus one letter, then the j tag
    return (a[:2], b[:2])


def _signed_rme():
    """The full signed reduced-matrix-element table."""
    out = {}
    for s, lines in (("5S", LINES_5S[:8]), ("6S", LINES_6S),
                     ("7S", LINES_7S)):
        for nm, (_e, d, _s) in zip(_PN, lines):
            out[(s, nm)] = _RADIAL_SIGN[_pair_key(s, nm)] * abs(d)
    for (a, b), d in _PD_MAG.items():
        out[(a, b)] = _RADIAL_SIGN[_pair_key(a, b)] * abs(d)
    return out


RME = _signed_rme()


# ------------------------------------------------- exact angular momentum
def _f(x):
    x = Fr(x)
    assert x.denominator == 1 and x >= 0
    return factorial(int(x))


def w3j(j1, j2, j3, m1, m2, m3):
    """Wigner 3j, exact rational arithmetic."""
    j1, j2, j3, m1, m2, m3 = map(Fr, (j1, j2, j3, m1, m2, m3))
    if m1 + m2 + m3 != 0:
        return 0.0
    if not (j1 + j2 >= j3 and j2 + j3 >= j1 and j3 + j1 >= j2):
        return 0.0
    for j, m in ((j1, m1), (j2, m2), (j3, m3)):
        if abs(m) > j or (j - m).denominator != 1:
            return 0.0
    pre = Fr(_f(j1 + j2 - j3) * _f(j1 - j2 + j3) * _f(-j1 + j2 + j3),
             _f(j1 + j2 + j3 + 1))
    pre *= (_f(j1 - m1) * _f(j1 + m1) * _f(j2 - m2) * _f(j2 + m2)
            * _f(j3 - m3) * _f(j3 + m3))
    s = 0.0
    kmin = max(0, int(j2 - j3 - m1), int(j1 - j3 + m2))
    kmax = min(int(j1 + j2 - j3), int(j1 - m1), int(j2 + m2))
    for k in range(kmin, kmax + 1):
        s += (-1) ** k / (factorial(k) * _f(j1 + j2 - j3 - k)
                          * _f(j1 - m1 - k) * _f(j2 + m2 - k)
                          * _f(j3 - j2 + m1 + k) * _f(j3 - j1 - m2 + k))
    return (-1) ** int(j1 - j2 - m3) * sqrt(float(pre)) * s


def _cg(j1, m1, j2, m2, J, M):
    return (-1) ** int(Fr(j1) - Fr(j2) + Fr(M)) * sqrt(float(2 * Fr(J) + 1)) \
        * w3j(j1, j2, J, m1, m2, -Fr(M))


def _cos_theta(lp, l, ml):
    if lp == l + 1:
        return sqrt(((l + 1) ** 2 - ml * ml) / ((2 * l + 1) * (2 * l + 3)))
    if lp == l - 1:
        return sqrt((l * l - ml * ml) / ((2 * l - 1) * (2 * l + 1)))
    return 0.0


def _z_ls(lp, jp, l, j, m=Fr(1, 2)):
    """LS-coupled angular factor of the m = 1/2 z matrix element with
    a unit positive radial integral, so all relative angular signs
    inside a radial block are correct by construction."""
    tot = 0.0
    for ms in (Fr(-1, 2), Fr(1, 2)):
        ml = m - ms
        if abs(ml) > l or abs(ml) > lp:
            continue
        tot += (_cg(l, ml, Fr(1, 2), ms, j, m)
                * _cg(lp, ml, Fr(1, 2), ms, jp, m)
                * _cos_theta(lp, l, float(ml)))
    return tot


def _zmat(drop=()):
    """Signed m = 1/2 z matrix elements between all levels: angular
    sign from the LS construction, radial sign carried by RME."""
    z = {}
    for (a, b), d in RME.items():
        if a in drop or b in drop:
            continue
        la, ja, _ = LEVELS[a]
        lb, jb, _ = LEVELS[b]
        mag = abs(d) * abs(w3j(jb, 1, ja, -_H, 0, _H))
        s = _z_ls(lb, jb, la, ja)
        sgn = (1.0 if s >= 0 else -1.0) * (1.0 if d >= 0 else -1.0)
        z[(a, b)] = z[(b, a)] = sgn * mag
    return z


# --------------------------------------------------- fourth-order machinery
def _rspt4(g: str, lam_nm: float, u_mhz: float = 1.0, nmax: int = 3):
    """(E2, E4) in Hz for level g at trap depth u_mhz (in units of
    h times 1 MHz, which is 48 uK), exact fourth-order perturbation
    theory in the Floquet basis. Tail and core enter as one far
    fictitious channel per S state so the linear shift reproduces
    the full module polarizability.

    PRECONDITION, and it is not optional: lam_nm must stay away from a
    TWO-PHOTON resonance between the two S states. The Floquet basis
    contains |partner, n-2>, whose energy denominator is the two-photon
    detuning, so E4 carries a pole wherever 2*h*nu equals a real S-to-S
    interval. For 5S-6S that pole sits at 993.4181 nm, which is the
    wavelength this experiment actually drives.

    What that costs, measured 2026-08-09, and the demonstration is
    better than the diagnosis. Fed one of the campaign's peak labels,
    _rspt4 returns a differential E4 of order 100 Hz, of which 99.995 per
    cent is the single |6S, n-2> term. It is not a hyperpolarizability:
    it is the second-order two-photon level repulsion, |M|^2 / D with
    |M| of order 2e5 Hz. Three checks pin that. nmax=1 drops the
    delta-n = 2 sector and leaves -5.2e-4 Hz, while nmax=2 through 5
    agree identically. Dropping the partner S state leaves -3.4e-3 Hz.
    A wavelength scan holds E4 times D constant and flips its sign
    through the resonance.

    THE DENOMINATOR IS NOT EVEN A PHYSICAL DETUNING, which is what makes
    the number unusable rather than merely large. The peak labels are
    fitted hyperfine positions, so the drive sits ON the component it
    addresses; D is the offset between twice a label and E_6S_CM, which
    is the NIST hyperfine-CENTROID term. So D is a bookkeeping residue,
    part genuine hyperfine offset from the centroid and part a
    common-mode calibration offset shared by all four labels, and E4
    accordingly swings from -27.75 to +152.73 Hz and CHANGES SIGN across
    the four measured lines. A physical shift does not do that.

    The genuine non-resonant differential fourth-order shift at 993 nm
    is of order 1e-3 Hz (the two pole removals bracket it between 5e-4
    and 5e-3, sign negative, under the module's own factor-of-two
    envelope). That is about 5e7 below the second-order differential
    shift at the same field and eight orders below the archive's
    light-shift bound, so a third photon contributes nothing measurable
    through this channel.

    No committed result is affected, which is why this is a precondition
    and not a correction. The nearest of the six crossings the module is
    evaluated at, 1029.7 nm, sits 354 cm^-1 clear of the pole, and the
    farthest is 2601 cm^-1 clear. tests/test_hyperpolarizability.py pins
    both the clearance and the pole's structure."""
    z = _zmat()
    om = 1e7 / lam_nm
    a_m = 0.5 * (alpha_5s(lam_nm) + alpha_6s(lam_nm))
    u_ha = u_mhz * 1e6 / HARTREE_HZ
    e0 = sqrt(4.0 * u_ha / abs(a_m))

    labs = list(LEVELS)
    en = {k: LEVELS[k][2] for k in labs}
    for s, a_ex in (("5S", TAIL_5S + CORE_5S), ("6S", TAIL_6S + CORE_6S),
                    ("7S", 9.4)):
        lab = "FAR_" + s
        de_cm = 5e5
        d2 = 3.0 * a_ex * (de_cm / CM)
        labs.append(lab)
        en[lab] = en[s] + de_cm
        z[(s, lab)] = z[(lab, s)] = sqrt(d2 / 6.0)

    basis = [(l, n) for l in labs for n in range(-nmax, nmax + 1)]
    idx = {b: i for i, b in enumerate(basis)}
    nb = len(basis)
    energies = np.array([(en[l] + n * om) / CM for l, n in basis])
    e_g = en[g] / CM
    v_mat = np.zeros((nb, nb))
    for (a, b), val in z.items():
        if a not in en or b not in en:
            continue
        for n in range(-nmax, nmax + 1):
            for dn in (-1, 1):
                if -nmax <= n + dn <= nmax:
                    v_mat[idx[(a, n)], idx[(b, n + dn)]] += -0.5 * e0 * val
    i0 = idx[(g, 0)]
    denom = e_g - energies
    ok = np.ones(nb, bool)
    ok[i0] = False
    green = np.where(ok, 1.0 / np.where(ok, denom, 1.0), 0.0)
    v = v_mat[i0].copy()
    v[i0] = 0.0
    e2 = float(np.sum(v * v * green))
    vp = v_mat.copy()
    vp[i0, :] = 0.0
    vp[:, i0] = 0.0
    x = v * green
    # macOS Accelerate raises spurious floating-point flags inside
    # matmul on benign input, so the flags are silenced for the
    # product and finiteness is asserted explicitly instead.
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        e4 = float(x @ vp @ np.diag(green) @ vp @ x) \
            - e2 * float(np.sum(v * v * green * green))
    assert np.isfinite(e2) and np.isfinite(e4)
    return e2 * HARTREE_HZ, e4 * HARTREE_HZ


_BRACKETS = {
    "1203.9": (1195.0, 1210.0), "1287.9": (1281.0, 1291.5),
    "1339.6": (1332.0, 1348.0), "1297.5": (1296.6, 1298.05),
    "1029.7": (1028.75, 1030.55), "1031.9": (1030.80, 1033.00),
}


def crossings():
    """All six polarizability crossings, as (name, wavelength_nm).
    The three long-wavelength entries are the published magic list.
    The other three hug poles and exist here so the design
    comparison can price them: 1297.5 nm sits 0.7 nm from the
    6S-7P1/2 line and the two near 1030 nm hug the 8P doublet."""
    return [
        ("1203.9", brentq(delta_alpha, 1195.0, 1210.0, xtol=1e-9)),
        ("1287.9", brentq(delta_alpha, 1281.0, 1291.5, xtol=1e-9)),
        ("1339.6", brentq(delta_alpha, 1332.0, 1348.0, xtol=1e-9)),
        ("1297.5", brentq(delta_alpha, 1296.6, 1298.05, xtol=1e-9)),
        ("1029.7", brentq(delta_alpha, 1028.75, 1030.55, xtol=1e-9)),
        ("1031.9", brentq(delta_alpha, 1030.80, 1033.00, xtol=1e-9)),
    ]


def quartic_coefficients():
    """{crossing name: C} with C in Hz per (U/h in MHz) squared: the
    residual differential shift is C times the squared trap depth.
    Bound levels through 5D; higher even states add roughly another
    tenth at 1203.9 nm (order of magnitude, estimated outside this
    module)."""
    out = {}
    for name, lam in crossings():
        q5 = _rspt4("5S", lam)[1]
        q6 = _rspt4("6S", lam)[1]
        out[name] = q6 - q5
    return out


# ------------------------------------------------------------ vector shift
def vector_coefficient(lam_nm: float):
    """Differential vector shift for the stretched m = +1/2 pair, in
    Hz per (U/h in MHz) per unit circularity of the trap light. The
    second-order shift of a J = 1/2 state is exactly linear in the
    circularity, so this one number fixes the whole ellipticity
    budget: shift = coefficient times depth times circularity, and
    the m = -1/2 pair sees the opposite sign (an unpolarized
    ensemble sees a splitting, not a shift)."""
    j_list = [_H, _TH] * 4
    om = (1e7 / lam_nm) / CM
    a_m = 0.5 * (alpha_5s(lam_nm) + alpha_6s(lam_nm))
    e0 = sqrt(4.0 * (1e6 / HARTREE_HZ) / abs(a_m))

    def e2(lines, upper_cm, m, circ):
        tot = 0.0
        for (e, d, _s), jp in zip(lines, j_list):
            de = (e - upper_cm) / CM
            if circ:
                w_abs = d * w3j(jp, 1, _H, -(m + 1), 1, m)
                w_em = d * w3j(jp, 1, _H, -(m - 1), -1, m)
            else:
                w_abs = w_em = d * w3j(jp, 1, _H, -m, 0, m)
            tot += (e0 / 2) ** 2 * (w_abs ** 2 / (om - de)
                                    - w_em ** 2 / (om + de))
        return tot * HARTREE_HZ

    d5 = e2(LINES_5S[:8], 0.0, _H, True) - e2(LINES_5S[:8], 0.0, _H, False)
    d6 = e2(LINES_6S, E_6S_CM, _H, True) - e2(LINES_6S, E_6S_CM, _H, False)
    return d6 - d5


# -------------------------------------------------------------- scattering
def einstein_a(de_ha: float, d_rme: float, j_upper_2: int):
    """Einstein A in atomic angular-rate units for the decay of the
    upper state, degeneracy of the EMITTER."""
    return (4.0 / 3.0) * ALPHA_FS ** 3 * abs(de_ha) ** 3 * d_rme * d_rme \
        / (j_upper_2 + 1.0)


_GAMMA_5P = {}
for _j2, (_e5p, _d5p, _s5p) in zip((1, 3), LINES_5S[:2]):
    _GAMMA_5P[_e5p] = einstein_a(_e5p / CM, _d5p, _j2)


def scattering_rates(lam_nm: float):
    """(rate_5S, rate_6S) trap-photon scattering in events per second
    at a depth of h times 1 MHz (48 uK), scaling linearly with depth.
    Per channel the rate is the admixed intermediate state's decay
    rate times the squared admixture. Downward 6S-5P channels use
    the complete 5P decay rate (5P decays only to 5S, which the
    lists contain, and the chain reproduces the D2 width and the
    measured 6S lifetime in the tests). Upward channels use the
    partial width into the tracked state, so those contributions are
    LOWER bounds: at the two 1030 nm crossings, where upward 8P
    channels dominate, the complete rates are several times larger."""
    om = (1e7 / lam_nm) / CM
    a_m = 0.5 * (alpha_5s(lam_nm) + alpha_6s(lam_nm))
    e0sq = 4.0 * (1e6 / HARTREE_HZ) / abs(a_m)
    j_list = [1, 3] * 4
    out = []
    for lines, upper in ((LINES_5S[:8], 0.0), (LINES_6S, E_6S_CM)):
        total = 0.0
        for (e, d, _s), j2 in zip(lines, j_list):
            de = (e - upper) / CM
            delta = om - abs(de)
            if de < 0.0:
                g_au = None
                for k, v in _GAMMA_5P.items():
                    if abs(k - (e)) < 0.5:
                        g_au = v
                assert g_au is not None
            else:
                g_au = einstein_a(de, d, j2)
            om2 = e0sq * d * d / 6.0
            total += g_au * om2 / (4.0 * delta ** 2)
        out.append(total * AU_RATE_HZ)
    return tuple(out)


# ------------------------------------------------------ the inverse use
# A crossing can be read backwards. Its POSITION is fixed by the
# matrix elements that build the two polarizabilities, so measuring
# where it sits constrains them. That is the logic of the published
# tune-out and magic-wavelength measurements (Herold 2012 on the Rb
# 5s-6p elements, Hamilton 2023 on the 5P-5D element from the 5S-5D
# magic wavelength, which is the row this module keeps in preference
# to all-order theory). The two functions below say which crossing
# constrains which element, and how well.

def steepness(lam_nm: float, h: float = 1e-4):
    """d(alpha_6S - alpha_5S)/d(lambda) in atomic units per picometre.

    This is the lever arm. It sets how precisely a crossing can be
    LOCATED IN WAVELENGTH from a measured shift, and it cancels out of
    what the crossing then measures (see lever_table). It runs
    opposite to what makes
    a crossing a good trap: a flat crossing is insensitive to the
    trap laser's wavelength, which is why it traps well and locates
    badly."""
    return (delta_alpha(lam_nm + h) - delta_alpha(lam_nm - h)) \
        / (2.0 * h) * 1e-3


def position_sensitivity(name: str, lam_nm: float, bracket, frac: float = 0.01):
    """How far the crossing moves when one reduced matrix element is
    scaled by `frac`, in picometres, for the eight lines up through
    8P of each state (the eight higher lines the 5S list carries are
    left out). Returns a list of (shift_pm, state, line_label),
    largest in magnitude first.

    ONE AT A TIME, which is a sensitivity and not an error budget: a
    real inversion needs the joint covariance of the element set, and
    the leading entry here names the element a measurement would
    speak to rather than delivering its uncertainty."""
    import rb5s6s.polarizability as _p
    keep5, keep6 = _p.LINES_5S, _p.LINES_6S
    lam0 = brentq(delta_alpha, *bracket, xtol=1e-11)
    out = []
    try:
        for state, src in (("5S", keep5), ("6S", keep6)):
            for i in range(min(8, len(src))):
                rows = [list(r) for r in src]
                rows[i][1] *= 1.0 + frac
                new = tuple(tuple(r) for r in rows)
                if state == "5S":
                    _p.LINES_5S = new
                else:
                    _p.LINES_6S = new
                try:
                    lam1 = brentq(delta_alpha, *bracket, xtol=1e-11)
                    out.append(((lam1 - lam0) * 1e3, state, _PN[i]))
                except ValueError:
                    pass
                _p.LINES_5S, _p.LINES_6S = keep5, keep6
    finally:
        _p.LINES_5S, _p.LINES_6S = keep5, keep6
    out.sort(key=lambda r: -abs(r[0]))
    return out


def lever_table(shift_precision_hz: float = 92e3,
                khz_per_pm_at_ref: float = 3.6,
                ref_steepness: float = 11.27):
    """What each crossing would measure, given a shift precision.

    The conversion is anchored on the worked case in
    FUTURE_TRANSITIONS section 5.1: at the campaign intensity a
    picometre of wavelength at the 1297.5 nm root is 3.6 kHz of
    induced differential shift, and that root runs at 11.27 atomic
    units per picometre. Both scale with the same intensity, so the
    kHz per picometre at any other crossing follows from its own
    steepness, and the localisation is the shift precision divided by
    that. Dividing the localisation by the position sensitivity gives
    the fractional precision on the element the crossing speaks to.
    Steepness cancels in that division, since the localisation and the
    sensitivity both scale as one over it. What is left is the
    differential polarizability measured to 288 atomic units at this
    shift precision, divided by the element's response in the same
    units, so wavelength is the unit the measurement is expressed in
    and not a term in it.

    THE OTHER FACTOR, and it decides everything. A precision is
    worth nothing on its own. What matters is the precision against
    what is ALREADY known about that element, and the line lists
    carry their own quoted uncertainties, so the comparison is
    available here rather than in someone's judgement. The `gain`
    field is the quoted fractional uncertainty divided by what the
    crossing would deliver: above one the measurement improves on
    the present state, below one it does not.

    Yields dicts with the crossing, its steepness, the localisation
    in picometres, the leading element, the fractional precision on
    it, the currently quoted uncertainty and the gain."""
    rows = []
    for name, lam in crossings():
        b = _BRACKETS[name]
        s = steepness(lam)
        khz_per_pm = khz_per_pm_at_ref * abs(s) / ref_steepness
        loc_pm = (shift_precision_hz / 1e3) / khz_per_pm
        sens = position_sensitivity(name, lam, b)
        lead_pm, lead_state, lead_line = sens[0]
        prec = loc_pm / abs(lead_pm) * 0.01
        src = LINES_5S if lead_state == "5S" else LINES_6S
        i = _PN.index(lead_line)
        e_l, d_l, sig_l = src[i]
        known = sig_l / d_l
        rows.append(dict(
            crossing=name, lam_nm=lam, steepness_au_per_pm=s,
            localisation_pm=loc_pm, element=f"{lead_state}-{lead_line}",
            frac_precision=prec, known_frac=known, gain=known / prec))
    return rows


if __name__ == "__main__":
    cs = quartic_coefficients()
    print("crossing   lambda_nm   C(Hz/MHz^2)   V1(Hz/MHz/S3)   "
          "Gamma_sc 5S,6S (/s at h x 1 MHz)")
    for name, lam in crossings():
        v1 = vector_coefficient(lam)
        r5, r6 = scattering_rates(lam)
        print(f"{name:>8s}  {lam:10.4f}  {cs[name]:+11.4f}  {v1:+13.0f}  "
              f"{r5:7.3f} {r6:9.3f}")

    print("\nRead backwards: what each crossing would measure, at the "
          "projected shift precision")
    print(f"{'crossing':>9s} {'a.u./pm':>9s} {'locate/pm':>10s} "
          f"{'element':>12s} {'would give':>11s} {'known':>8s} {'gain':>6s}")
    for r in lever_table():
        print(f"{r['crossing']:>9s} {r['steepness_au_per_pm']:+9.3f} "
              f"{r['localisation_pm']:10.0f} {r['element']:>12s} "
              f"{r['frac_precision']*100:10.1f}% {r['known_frac']*100:7.2f}% "
              f"{r['gain']:6.2f}")
