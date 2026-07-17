"""
Fringe-tail Monte-Carlo of the standing-wave AC-Stark ramp (module M14)
=======================================================================

The 5S->6S retro-excitation is a focused STANDING wave. The Doppler-free drive
is the counter-propagating cross term E_f E_b, whose phase e^{ikz} e^{-ikz} = 1
is z-UNIFORM: the lambda/2 fringes do NOT gate excitation and do NOT enter the
transit time. They live only in the AC-Stark SHIFT, through the local intensity

    I(z, r) = I_f(r) [ 1 + rho + 2 sqrt(rho) cos(2 k z) ],

which modulates the instantaneous light shift an atom feels while it is being
excited. constants.DELTA_ALPHA_AU pins the on-axis, fast-fringe-averaged peak
shift S0 = Delta_alpha I_eff / (2 eps0 c h) with I_eff = (1+rho) 2P/(pi w0^2)
the standing-wave MEAN; the archival ramp uses S0 and its symmetric transverse
wedge (lineshape.stark_ramp, mean pull -(2/3) S0, third cumulant +S0^3/135).

This module quantifies the ONE piece that mean picture drops: a slow-v_z tail.
An atom whose axial speed is small crosses the fringes slowly, sits near a
frozen fringe phase for the whole coherent excitation window, and therefore
samples the node-antinode intensity rather than its mean. The shift then
modulates MULTIPLICATIVELY, s = s_wedge (1 + x) with x = contrast cos(theta0) F,
contrast = 2 sqrt(rho)/(1+rho) and F the trajectory-averaged fringe survival.
The modulation is symmetric (E[x] = 0, so the MEAN pull is preserved) but the
PRODUCT s(1+x) inherits a cross-term in its third moment,

    mu3(s(1+x)) = mu3(s_wedge) + 3 Var(x) (E[s^3] - <s> E[s^2]),

so the ramp's own skew is SUPPRESSED, not inflated -- the arcsine fringe kills
its own skew but not the product's. The effect is a same-sign (negative) rider
on the beam-DIVERGENCE axial averaging the pipeline already models
(lineshape.stark_ramp_axial); at the small (16 um, config S) waist the two must be fit
jointly, which is why their coefficients are wanted as reproducible facts.

PHYSICS OF ONE ATOM. Beam axis z, transverse plane (x, y); Gaussian beam of
waist w0, constant over the ~0.1-0.2 us transit (axial travel << Rayleigh
range). Straight-line crossing at closest-approach impact parameter b, so
r(t)^2 = b^2 + v_perp^2 t^2 with v_perp = sqrt(vx^2 + vy^2); axial position
z(t) = z0 + vz t with (vx, vy, vz) drawn from the full 3D Maxwell-Boltzmann
distribution and the entry fringe phase theta0 = 2 k z0 uniform on [0, 2 pi).
The forward envelope is I_f = exp(-2 r^2/w0^2); the two-photon excitation RATE
(z-uniform, per the cross-term argument) is proportional to I_f^2, and the
instantaneous shift is S0 I_f (1 + rho + 2 sqrt(rho) cos(2 k z))/(1+rho).

The excitation-rate-weighted trajectory average of the shift over the coherence
window is, for the Gaussian crossing, closed-form. In the transverse
crossing-time variable the rate weight is exp(-4 tau^2) (from I_f^2) and the
shift-times-rate weight is exp(-6 tau^2) (from I_f^3); an optional coherence
window of 1/e time tau_c multiplies both by a common Gaussian, adding
1/(2 tau_c^2) to each quadratic coefficient. Writing

    a_num = 6 v_perp^2/w0^2 + 1/(2 tau_c^2),
    a_den = 4 v_perp^2/w0^2 + 1/(2 tau_c^2),

the per-atom effective (centroid) shift is

    s_eff = S0 u0 sqrt(a_den/a_num) [ 1 + contrast cos(theta0) F ],
    u0    = exp(-2 b^2/w0^2),   F = exp(-k^2 vz^2 / a_num).

sqrt(a_den/a_num) is the transit path-averaging of the envelope (sqrt(2/3) in
the transit-limited limit tau_c -> inf); F is the fringe survival: F -> 0 for a
fast axial crosser (many fringes averaged, the mean picture), F -> 1 for a slow
one (a resolved, frozen fringe). Each atom is weighted by its crossing flux
times integrated rate, which reduces to W ∝ u0^2 (v_perp cancels between the
flux and the Gaussian crossing time), exactly the transit_mc convention.

COHERENCE WINDOW. tau_c is the ONE open modelling choice. The coherent
excitation amplitude lives at most one 6S lifetime (tau_6S ~ 46 ns), but the
beam crossing may be shorter or longer: at the archival 50 um waist the transit
is ~0.2 us (transit-limited, tau_c -> inf is the right cap), at the small
16 um waist it is ~65 ns, comparable to tau_6S, so the two bracket the fringe
survival. fringe_tail_mc SWEEPS tau_c between the transit-limited case and
tau_6S to report that bracket. The fringe-survival moments are
temperature-independent (F depends only on vz/v_perp, whose distribution is set
by the Maxwell-Boltzmann isotropy, not by T); T enters only the axial-speed
threshold of the coherence-window fraction, through the transit time.

ESTIMATOR NOTE. The standardized skewness is a third-moment ratio and converges
slowly: a single 3e5-atom draw carries ~0.015 of skew noise, so a committable
number pools several independent blocks (n_blocks) and reports the pooled value
with the block-to-block standard error. The third CUMULANT change is far
better behaved -- the noisy wedge third moment cancels in the difference, so it
reproduces the exact cross-term identity above to a fraction of a percent and is
the primary reported leverage. Everything is deterministic at a fixed base seed.
"""

from __future__ import annotations

from math import erf, pi, sqrt
from typing import Dict, Optional

import numpy as np

from . import config as C
from .constants import K_B_J_PER_K, LAMBDA_LASER_M, M_RB87_KG

_K_WAVE = 2.0 * pi / LAMBDA_LASER_M          # laser wavenumber (rad/m)


def _sigma_v1d(T_C: float, mass_kg: float = M_RB87_KG) -> float:
    """1D Maxwell-Boltzmann speed scale sqrt(k T / m) (m/s)."""
    return float(sqrt(K_B_J_PER_K * (T_C + 273.15) / mass_kg))


def _power_sums(s: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted power sums [sum w, sum w s, sum w s^2, sum w s^3] for pooling."""
    return np.array([w.sum(), (w * s).sum(), (w * s * s).sum(),
                     (w * s ** 3).sum()])


def _moments_from_sums(p: np.ndarray) -> tuple:
    """Mean, variance, third central moment and standardized skew from pooled
    weighted power sums (the pooling is exact -- equivalent to one large draw)."""
    m1 = p[1] / p[0]
    m2 = p[2] / p[0]
    m3 = p[3] / p[0]
    var = m2 - m1 ** 2
    mu3 = m3 - 3.0 * m1 * m2 + 2.0 * m1 ** 3
    skew = mu3 / var ** 1.5 if var > 0 else 0.0
    return float(m1), float(var), float(mu3), float(skew)


def _one_block(w0_m: float, s0_mhz: float, rho: float, T_C: float,
               inv2tau: float, contrast: float, n_atoms: int,
               b_cut: float, rng: np.random.Generator) -> Dict:
    """Sample one independent block and return its pooled power sums (fringe and
    no-fringe), fringe-resolved weight, fringe-variance weight, and total weight,
    plus the block's own skew change for a Monte-Carlo error estimate."""
    sv = _sigma_v1d(T_C)
    vx = rng.normal(0.0, sv, n_atoms)
    vy = rng.normal(0.0, sv, n_atoms)
    vz = rng.normal(0.0, sv, n_atoms)
    v_perp = np.maximum(np.hypot(vx, vy), 1e-6)

    b = b_cut * w0_m * np.sqrt(rng.uniform(0.0, 1.0, n_atoms))
    u0 = np.exp(-2.0 * b ** 2 / w0_m ** 2)
    theta0 = rng.uniform(0.0, 2.0 * pi, n_atoms)

    a_num = 6.0 * v_perp ** 2 / w0_m ** 2 + inv2tau
    a_den = 4.0 * v_perp ** 2 / w0_m ** 2 + inv2tau
    kappa_path = np.sqrt(a_den / a_num)
    F = np.exp(-_K_WAVE ** 2 * vz ** 2 / a_num)

    s_env = -s0_mhz * u0 * kappa_path                   # symmetric transverse wedge
    s_signed = s_env * (1.0 + contrast * np.cos(theta0) * F)
    W = u0 ** 2                                         # flux x integrated rate

    p_f = _power_sums(s_signed, W)
    p_n = _power_sums(s_env, W)
    _, _, _, skew_f = _moments_from_sums(p_f)
    _, _, _, skew_n = _moments_from_sums(p_n)
    return {
        "p_f": p_f, "p_n": p_n,
        "w_tot": float(W.sum()),
        "w_resolved": float(W[F > 0.5].sum()),
        "w_fvar": float((W * 0.5 * (contrast * F) ** 2).sum()),
        "w_kappa": float((W * kappa_path).sum()),
        "block_d_skew": skew_f - skew_n,
        "sigma_v": sv,
    }


def fringe_tail_mc(*, w0_m: float, s0_mhz: float, rho: float = 1.0,
                   T_C: float = 130.0, coherence_s: Optional[float] = None,
                   n_atoms: int = 300_000, n_blocks: int = 1, b_cut: float = 3.0,
                   seed: int = None) -> Dict:
    """Sample the 3D-MB + fringe-phase ensemble and return the fringe tail's
    imprint on the signal-weighted effective-shift distribution.

    w0_m       : beam waist (m).
    s0_mhz     : on-axis fast-averaged peak red shift S0 (MHz, transition axis).
    rho        : retro power ratio (1.0 = perfect retro).
    coherence_s: 1/e coherence window (s); None = transit-limited (tau_c -> inf).
    n_blocks   : independent blocks pooled to tame the third-moment noise (the
                 pooling is exact; block spread gives the reported MC error).
    T_C        : cell temperature (C); sets only the axial-speed threshold of
                 the coherence-window fraction (the fringe-survival moments are
                 T-independent).

    Returns a dict, on the signed shift s in [-S0, 0] (red = negative):
      mean_over_s0, mean_nofringe_over_s0: signal-weighted centroid pull / S0
                                          with and without the fringe (equal to
                                          ~2e-3: the symmetric fringe preserves
                                          the mean, since E[1+x]=1);
      kappa_path                        : transit envelope path factor
                                          (sqrt(2/3) ~ 0.816, transit-limited);
      kappa3, kappa3_nofringe, d_kappa3 : third cumulant (MHz^3) with/without
                                          the fringe and its change (the primary,
                                          well-converged leverage);
      skew, skew_nofringe, d_skew       : standardized skewness and its change;
      d_skew_mc_err                     : block-to-block standard error on d_skew;
      var, var_nofringe, excess_var_frac: variance and the fringe fraction of it;
      f_res_var                         : signal-weighted fringe modulation
                                          variance Var(x) (the leverage f_res/2);
      frac_resolved                     : signal-weighted fraction with F > 0.5;
      window_frac                       : coherence-window axial-speed estimate
                                          P(|vz| < (lambda/2)/T_window).
    """
    rng = np.random.default_rng(C.RNG_SEED if seed is None else seed)
    inv2tau = 0.0 if coherence_s is None else 1.0 / (2.0 * coherence_s ** 2)
    contrast = 2.0 * sqrt(rho) / (1.0 + rho)

    p_f = np.zeros(4)
    p_n = np.zeros(4)
    w_tot = w_res = w_fvar = w_kappa = 0.0
    block_dskew = []
    sv = _sigma_v1d(T_C)
    for _ in range(n_blocks):
        blk = _one_block(w0_m, s0_mhz, rho, T_C, inv2tau, contrast,
                         n_atoms, b_cut, rng)
        p_f += blk["p_f"]
        p_n += blk["p_n"]
        w_tot += blk["w_tot"]
        w_res += blk["w_resolved"]
        w_fvar += blk["w_fvar"]
        w_kappa += blk["w_kappa"]
        block_dskew.append(blk["block_d_skew"])

    mean, var, mu3, skew = _moments_from_sums(p_f)
    mean_n, var_n, mu3_n, skew_n = _moments_from_sums(p_n)
    bd = np.array(block_dskew)
    d_skew_mc_err = float(bd.std(ddof=1) / sqrt(n_blocks)) if n_blocks > 1 else 0.0

    vbar = sqrt(pi / 2.0) * sv
    t_window = w0_m / vbar if coherence_s is None else coherence_s
    vz_thr = (LAMBDA_LASER_M / 2.0) / t_window
    window_frac = float(erf(vz_thr / (sqrt(2.0) * sv)))

    return {
        "w0_um": w0_m * 1e6, "s0_mhz": s0_mhz, "rho": rho, "T_C": T_C,
        "coherence_ns": (np.inf if coherence_s is None else coherence_s * 1e9),
        "sigma_v": sv, "t_window_ns": t_window * 1e9, "vz_thr": vz_thr,
        "n_atoms": n_atoms, "n_blocks": n_blocks,
        "mean_over_s0": mean / s0_mhz, "mean_nofringe_over_s0": mean_n / s0_mhz,
        "kappa_path": w_kappa / w_tot,
        "var": var, "var_nofringe": var_n,
        "excess_var_frac": (var - var_n) / var if var > 0 else 0.0,
        "f_res_var": w_fvar / w_tot,
        "kappa3": mu3, "kappa3_nofringe": mu3_n, "d_kappa3": mu3 - mu3_n,
        "skew": skew, "skew_nofringe": skew_n, "d_skew": skew - skew_n,
        "d_skew_mc_err": d_skew_mc_err,
        "frac_resolved": w_res / w_tot,
        "window_frac": window_frac,
    }
