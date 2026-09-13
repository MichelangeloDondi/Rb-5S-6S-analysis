"""A Numerov model-potential solver for Rb: bound radial functions at the
measured energies and energy-normalised continuum p waves, for the sums the
polarizability producers need (W1 M1.1, landed 2026-09-13 after the validation
in private/cache/ultra_joint_2026-09-12/model_potential_draft.py: the 6S E1
class reproduced at 0.980 +- 0.022, the 7S class at 0.998 +- 0.007, the 5s E2
4d anchor at 1.003 to 1.004 of S&S 2011; the 5s E1 ladder is NOT reproduced,
0.68, and this module is not used for 5s elements).

The potential is the Marinescu-Sadeghpour-Dalgarno (1994) parametric form,
    V_l(r) = -Z_l(r)/r - alpha_c/(2 r^4) (1 - exp(-(r/r_c)^6)),
    Z_l(r) = 1 + (Z-1) exp(-a1 r) - r (a3 + a4 r) exp(-a2 r),
and the radial functions are integrated INWARD at the experimental energies
(NIST levels through the record's quantum defects), on the sqrt(r) grid,
    r = x^2,  P(r) = sqrt(x) Q(x),  Q'' = [4 x^2 F(x^2) + 3/(4 x^2)] Q,
    F(r) = 2 (V + l(l+1)/(2 r^2) - E),
with Numerov on Q. Reduced matrix elements for an s state:
    |<s_1/2 || r^k C_k || l'=k, j'>|^2 = (2j'+1)/(2k+1) * R_k^2,
    R_k = int P_s r^k P_l' dr,
and the S&S 2011 multipole polarizability, their Eq. (7):
    alpha^{Ek}(5s) = 1/(2k+1) sum_n |<n l_j || r^k C_k || 5s>|^2 / (E_n - E_5s).

PARAMETERS ARE TYPED FROM MEMORY AND MARKED SO; the ARC data file is being
fetched to check them, and the validation is the gate either way.
"""
import math

import numpy as np

from ._compat import trapezoid
from .coulomb_approx import E_ION_CM, RYD_RB_CM
from .polarizability import CM_PER_HARTREE

Z = 37
ALPHA_C = 9.0760                                   # MSD 1994, memory
# l = 0, 1, 2, >=3: (a1, a2, a3, a4, r_c)  -- MSD 1994 Table I as carried by the ARC data file
# (alkali_atom_data.py, fetched 2026-09-12), every value identical to memory except a4[l=1] at the 6th digit
MSD = {0: (3.69628474, 1.64915255, -9.86069196, 0.19579987, 1.66242117),
       1: (4.44088978, 1.92828831, -16.79597770, -0.8163314, 1.50195124),   # a4: ARC data file reads -0.8163314, memory had -0.81633314 (4e-6 apart)
       2: (3.78717363, 1.57027864, -11.65588970, 0.52942835, 4.86851938),
       3: (2.39848933, 1.76810544, -12.07106780, 0.77256589, 4.79831327)}

def V(r, l):
    a1, a2, a3, a4, rc = MSD[min(l, 3)]
    zl = 1.0 + (Z - 1.0) * np.exp(-a1 * r) - r * (a3 + a4 * r) * np.exp(-a2 * r)
    return -zl / r - ALPHA_C / (2.0 * r ** 4) * (1.0 - np.exp(-(r / rc) ** 6))

X_MIN = 0.5   # inner limit r_min = 0.25 a0: the E2 4d anchor lands at 1.003-1.004 of S&S there against 1.07 at the ARC choice alpha_c^(1/3); the 5s E1 ladder does not move with it
def solve(E_h, l, x_max=None, dx=0.005, x_min=X_MIN):
    """Inward Numerov at energy E_h (Hartree, negative). Returns (r, P) normalised."""
    n_eff = 1.0 / math.sqrt(-2.0 * E_h)
    if x_max is None:
        x_max = math.sqrt(2.0 * n_eff * (n_eff + 15.0))
    x = np.arange(x_min, x_max, dx)[::-1]         # inward
    r = x ** 2
    F = 2.0 * (V(r, l) + l * (l + 1) / (2.0 * r ** 2) - E_h)
    G = 4.0 * r * F + 3.0 / (4.0 * r)              # 4 x^2 F + 3/(4 x^2)
    Q = np.zeros_like(x); Q[0] = 0.0; Q[1] = 1e-10
    h2 = dx * dx / 12.0
    for i in range(1, len(x) - 1):
        Q[i + 1] = (2.0 * Q[i] * (1.0 + 5.0 * h2 * G[i]) - Q[i - 1] * (1.0 - h2 * G[i - 1])) / (1.0 - h2 * G[i + 1])
        if abs(Q[i + 1]) > 1e250:                  # rescale, the inward solution grows
            Q[: i + 2] /= 1e250
    P = np.sqrt(x) * Q
    # cut the divergent inner part: stop where |P| starts to blow up inside the last node region
    r, P = r[::-1], P[::-1]
    norm = np.sqrt(trapezoid(P * P, r))
    return r, P / norm

def radial(Pa, ra, Pb, rb, k):
    r = ra if len(ra) >= len(rb) else rb
    Pa_i = np.interp(r, ra, Pa, left=0.0, right=0.0); Pb_i = np.interp(r, rb, Pb, left=0.0, right=0.0)
    return float(trapezoid(Pa_i * r ** k * Pb_i, r))

def energy_h(level_cm):
    return -(E_ION_CM - level_cm) / CM_PER_HARTREE

MU_P = 2.648                                   # the np quantum defect continued above threshold (Seaton): the j-average of 2.6549 and 2.6417
R_MAX_C = 600.0

def continuum(eps, l=1, mu=MU_P):
    """INWARD Numerov at eps > 0 from the Coulomb asymptote, the phase fixed by
    the quantum defect (Seaton's theorem: delta_l = pi mu_l at threshold), so the
    p wave is the analytic continuation of the bound np series and its threshold
    density joins the discrete law by construction. Energy-normalised: the
    asymptotic amplitude is sqrt(2/(pi k)). The first cut integrated OUTWARD from
    r = 0.25 with a zero there, which imposes a phase the pseudopotential cannot
    set, and read a threshold density ten times the discrete law (2026-09-13)."""
    x = np.arange(X_MIN, math.sqrt(R_MAX_C), 0.005)[::-1]; r = x ** 2
    F = 2.0 * (V(r, l) + l * (l + 1) / (2.0 * r ** 2) - eps)
    G = 4.0 * r * F + 3.0 / (4.0 * r)
    # THE SEED IS THE WKB COULOMB WAVE, NOT THE r -> infinity FORM: the asymptotic
    # phase k r - eta ln(2 k r) + sigma_l needs k r >> 1/k^2 (thirty thousand a0 at
    # eps = 5e-4), and seeding with it at 600 a0 read a threshold density thirty
    # times the discrete law. In the Coulomb zone the energy-normalised regular
    # solution is sqrt(2/pi) p^-1/2 sin(Phi), Phi = int_{r_0}^{r} p_C dr + pi/4 from
    # the Langer-corrected inner turning point; the physical wave adds pi mu.
    lam2 = (l + 0.5) ** 2
    def p_c(rr):
        return np.sqrt(np.maximum(2.0 * (eps + 1.0 / rr) - lam2 / rr ** 2, 0.0))
    r0 = (-1.0 + math.sqrt(1.0 + 2.0 * eps * lam2)) / (2.0 * eps) if eps > 0 else lam2 / 2.0   # inner turning point of the Coulomb + Langer potential
    rq = np.linspace(r0, R_MAX_C, 200001)
    pq = p_c(rq)
    phi_max = float(trapezoid(pq, rq)) + math.pi / 4.0
    def P_asym(rr):
        phi = phi_max - float(trapezoid(pq[rq >= rr], rq[rq >= rr]))
        return math.sqrt(2.0 / math.pi) / math.sqrt(float(p_c(np.array([rr]))[0])) * math.sin(phi + math.pi * mu)
    Q = np.zeros_like(x)
    Q[0] = P_asym(r[0]) / np.sqrt(x[0]); Q[1] = P_asym(r[1]) / np.sqrt(x[1])
    h2 = 0.005 * 0.005 / 12.0
    for i in range(1, len(x) - 1):
        Q[i + 1] = (2.0 * Q[i] * (1.0 + 5.0 * h2 * G[i]) - Q[i - 1] * (1.0 - h2 * G[i - 1])) / (1.0 - h2 * G[i + 1])
    P = np.sqrt(x) * Q
    return r[::-1], P[::-1]



def np_level_cm(n: int, j: float) -> tuple[float, float]:
    """The Rb np level (cm^-1) and its effective quantum number from the series'
    quantum defects, delta(n) = d0 + d2/(n - d0)^2 (Lorenzen and Niemax; NIST-consistent)."""
    d0, d2 = (2.6548849, 0.2900) if j == 0.5 else (2.6416737, 0.2950)
    ns = n - d0 - d2 / (n - d0) ** 2
    return E_ION_CM - RYD_RB_CM / ns ** 2, ns


def continuum_polarizability(level_cm: float, omega_cm: float, eps_max: float = 6.0) -> dict:
    """The s -> eps p continuum's oscillator strength and polarizability
    (static and at omega_cm) for the s state at level_cm, with the threshold
    join against the discrete law and the bound f-sum as checks. Atomic units
    for the polarizabilities; the bar is the caller's (see the deep producer)."""
    Es = energy_h(level_cm)
    rs, Ps = solve(Es, 0)
    w = omega_cm / CM_PER_HARTREE
    f_sum = 0.0; f_thr = []
    for n in range(5, 61):
        for j, wj in ((0.5, 1.0 / 3.0), (1.5, 2.0 / 3.0)):
            lev, ns = np_level_cm(n, j)
            rp, Pp = solve(energy_h(lev), 1)
            R = radial(Ps, rs, Pp, rp, 1)
            f = (2.0 / 3.0) * (energy_h(lev) - Es) * R * R * wj
            f_sum += f
            if n >= 45:
                f_thr.append(f * ns ** 3 / wj)
    eps = np.concatenate([np.linspace(5e-4, 0.02, 40), np.geomspace(0.021, eps_max, 90)])
    dfde = np.empty_like(eps); a_stat = np.empty_like(eps); a_dyn = np.empty_like(eps)
    for i, e in enumerate(eps):
        rc, Pc = continuum(e, 1)
        R = radial(Ps, rs, Pc, rc, 1)
        dE = e - Es
        dfde[i] = (2.0 / 3.0) * dE * R * R
        a_stat[i] = (2.0 / 3.0) * R * R / dE
        a_dyn[i] = (2.0 / 3.0) * R * R * dE / (dE * dE - w * w)
    return {"f_bound": f_sum, "f_continuum": float(trapezoid(dfde, eps)),
            "threshold_density_continuum": float(dfde[0]), "threshold_density_discrete": float(np.mean(f_thr)),
            "alpha_static": float(trapezoid(a_stat, eps)), "alpha_at_omega": float(trapezoid(a_dyn, eps))}
