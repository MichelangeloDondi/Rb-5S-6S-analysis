"""GUARD kernel-mc PRODUCER: the Monte Carlo behind every node of the full model.

Owner, 2026-09-16 22:30: "make sure (with proper mechanisms, as always, to refuse to proceed
in case it's not correct what would be done!) that for each w_0 and M^2 (and in case also rho
and other parameters) you run the proper Monte Carlo simulation before using it in the full
model. Then check the full model (in particular the transit and the F statistics, which is
a nontrivial non-equilibrium complex system dynamics of atoms coming from the walls of the
cell and that are changing F state in the cascade of the relaxation with a certain probability
we have already computed, so they deplete the number of atoms in the ground state available
to be excited!)".

A NODE is (w0, M2, rho, T, P). For each node this samples the gas the beam sees in its steady
state: atoms uniform in the collected column (z over the collection half-window, the impact
parameter uniform out to three beam radii at that z, the line measure of an isotropic gas, with w(z) = w0 sqrt(1 + (z/z_R)^2)
and z_R = pi w0^2 / (M2 lambda)), transverse speeds from the two-dimensional Maxwellian, and
the crossing FLUX as the weight (the rate is flux times probability; `transit_mc` records the
2026-07-12 defect of omitting it). Every atom enters with the THERMAL hyperfine populations
(the wall relaxes F between crossings, and `docs/lit/jarrett1964.md` puts the gas-phase refill
as 180 times slower than a transit), and along its chord it sees u(t) = (w0/w)^2
exp(-2 (b^2 + v^2 t^2) / w^2): the local two-photon rate G(P u(t)) with the cascade's
saturation carried (`platforms.excitation_rate_per_atom`, tabulated once per node), the light
shift S0 u(t), and its driven-F population obeying dN/dt = -q G(t) N with q the cascade's
probability of ending in the other F (`cascade.BRANCHING_F`). The standing wave at rho enters
the shift's normalisation and the Doppler-free rate as constants; the fringe's survival is
`fullmodel.fringe_survival_mc`'s reading and not this one's.

The nine readings of `kernel_gate.READINGS`, each the Monte Carlo against what
`fullmodel.full_profile` USES at the node, so a FAIL is a statement about the model at that
node and not about the sampler:

  transit_fwhm_rel      the flux-weighted kernel's FWHM against `constants.transit_fwhm_from_w0`
                        at w0 (what `run_ultra_joint.Cell` passes as `transit_fwhm`)
  transit_shape_rel     the kernel's shape against the two-sided exponential AT ITS OWN FWHM
  ramp_mu2_rel, ramp_mu3_rel   the rate-weighted instantaneous-shift distribution's moments, at the
                        node's saturation, against the model's ramp: since 2026-09-18 (F133, PLAN v2
                        Phase 1) `lineshape.saturated_ramp_density` at the node's own power, waist,
                        temperature and rho, mixed axially by `lineshape.ramp_mixture` at the node's
                        z_ratio (`ramp_mixture_moments`), which is what `run_ultra_joint.Cell` fits
                        with; the weak-field Monte Carlo is recorded beside them so a failure names
                        the saturation and not the sampling; mu3 carries its grid movement
  amplitude_power_law_abs   d ln A / d ln P at the node, with saturation and depletion, against
                        the model's law P^2 x `cascade.amplitude_factor` at the on-axis cycles
  shares_abs            the four lines' shares (thermal population x each line's surviving
                        signal) against `amplitudes.predicted_shares` x the model's factor
  depleted_line_abs     the composed depleted line (the SURVIVAL-weighted kernel after the natural
                        Lorentzian, on the line with the largest branching) against the fit's own
                        form composed the same way, the cusp at the bare width times the fitted
                        ratio: peak-normalised. After the Lorentzian the slow atoms' missing core
                        is mostly an amplitude, so no kernel width is the right observable; the
                        FWHM ratio rides in the artefact as the core-flattening diagnostic
  joint_shape_abs,      C6b's own addition (the merge's item 5a, F290's gap): a random SUBSAMPLE of the
  joint_moment_sigma_abs  node's own atoms, run through volume_line.joint_spectrum's own per-atom recipe
                        (run_kernel_mc._joint_line), against volume_line.JointTable at the same
                        condition, weak field and natural width alone. shape is the largest absolute
                        difference of the two peak-normalised lines. moment_sigma is the worst of mu2,
                        mu3, mu4 at rb5s6s.windows.QUOTED, each in the record's own standard deviation
                        at a stated reference condition (JOINT_NOISE_COND). The transit and the ramp
                        above are validated SEPARATELY: this is their JOINT, which neither reading touches

The per-atom lineshape is kept Gaussian in frequency with the chord's own width (the weak
field's Fourier pair); depletion reweights atoms and does not reshape the pulse, which is the
approximation the artefact names. The artefact is `kernel_gate.record_node`'s, under the
current cache; `kernel_gate.require_node` refuses the model on any node without one.

Rung: 3 (simulation), checked against rung 1 in the two limits the sampler must reproduce:
with the collection window closed and the drive weak it returns the closed-form cusp
(`--self-test`, the Lehmann-class plant of `transit_fwhm_from_w0`).
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import csv
import dataclasses
import json
import math
import os
import sys
import time
import pathlib
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1"); os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s.config import RESULTS_DIR as _RESULTS_DIR  # noqa: E402  (F480: results where RB5S6S_RESULTS_DIR points)
from rb5s6s import constants as K                                   # noqa: E402
from rb5s6s import beam_field as BF                                 # noqa: E402
from rb5s6s import fullmodel as FM                                  # noqa: E402
from rb5s6s import kernel_gate                                      # noqa: E402
from rb5s6s import lineshape                                        # noqa: E402
from rb5s6s import model_registry as _MR                            # noqa: E402  (O58: a judge, not the model)
from rb5s6s._compat import trapezoid                                # noqa: E402
from rb5s6s.amplitudes import predicted_shares                      # noqa: E402
from rb5s6s.cascade import BRANCHING_F, amplitude_factor            # noqa: E402
from rb5s6s.moments import windowed_moments                       # noqa: E402
from rb5s6s.noise import load_noise_model, sigma_of_v                # noqa: E402
from rb5s6s.platforms import PLATFORMS, excitation_rate_per_atom    # noqa: E402
from rb5s6s.volume_line import JointTable                           # noqa: E402
from rb5s6s.volume_line import N_TAU as VL_N_TAU, TAU_EDGE as VL_TAU_EDGE   # noqa: E402
from rb5s6s.windows import QUOTED as JOINT_WINDOWS_MHZ               # noqa: E402

B_CUT = 3.0                   # impact parameters out to three beam radii
TAIL_FRACTION = 0.20          # the mixture proposal's uniform component (F372)
B_CUT_CLIPPED = 8.0           # a clipped beam's rings fall as a POWER: 2.4e-4 of the two-photon
                              # weight sits past three radii against 2.3e-16 for a Gaussian, and
                              # 3 -> 8 moves mu3 by 0.66 per cent. 8.0 is `shift_density`'s own
                              # cut, so the model and the Monte Carlo now truncate ALIKE
TAU_EDGE = 3.0                # the chord in units of w/v, the wings carried
N_TAU = 41                    # points along the chord; the grid movement halves it
# THE JOINT-LINE READING (C6b, the merge's 5a, owner orders O45/O46/O49, A148, A120). The kernel
# gate validates the transit kernel and the ramp SEPARATELY (F290). This reading validates their
# JOINT, the atom Monte Carlo's own shift-and-transit line against `volume_line.JointTable`, the
# fitter's new default (A148, scripts/run_ultra_joint.py).  # ladder-exempt: a prose mention, no import
#
# A HISTOGRAM WAS TRIED FIRST AND MEASURED WRONG (the brief's own instruction, "follow
# run_kernel_inhomogeneity.py's binned construction"): `w/v` (the per-atom transit time scale)
# is heavily right-skewed -- at this corner its median sits four orders of magnitude below its
# max, with 99.9999 per cent of the sampled flux weight inside the bottom one per cent of its own
# value range -- so a value-histogram over (shift, w/v), linear OR quantile, OR nested as
# `run_kernel_inhomogeneity.py`'s own (z, then s-within-z) grid is, left a max-abs-peak
# discrepancy against `volume_line.joint_spectrum` of 0.05 to 0.36 that did not converge with
# more cells (measured directly against `joint_spectrum` at this corner, s0=0: 0.357 at 140x72
# cells, 0.339 at 400x200, quantile bins 0.087 at 140x72 and 0.049 at 500x250, nested quantile
# bins 0.071 to 0.093 across three grids -- plateaus, not convergence, the signature of a biased
# estimator and not of Monte Carlo noise). `run_kernel_inhomogeneity.py`'s own histogram works
# because ITS cells carry a closed-form composite kernel (`model_profile`) evaluated exactly at
# each cell's own (s, transit). This reading's per-atom line is a genuine two-time correlation
# (`joint_spectrum`'s own FFT/autocorrelation, F294's own construction) that a cell's MEAN (u_b,
# w/v) does not linearly reproduce from its members'.
#
# THE FIX IS A RANDOM SUBSAMPLE of the node's own already-sampled atoms (`_sample`'s own draw,
# never a fresh one), run through `joint_spectrum`'s own per-atom recipe UNBINNED (`_joint_line`
# below is a verbatim copy of that recipe's inner loop, PLANTED against `joint_spectrum` itself at
# matching atoms and seed, `run_kernel_mc._self_test`): a subsample is UNBIASED by construction
# (it is what a smaller Monte Carlo IS), where the histogram was not, and it is fast (measured:
# 1.5 s at 8000 atoms) with a max-abs-peak noise floor of 0.002 to 0.011 against an independently
# seeded 200 000-atom reference across five subsample sizes 500 to 8000 -- ordinary Monte Carlo
# scatter, not a plateauing bias. `JOINT_N_PATH` is this subsample's own size.
#
# Windows are the joint vector's own quoted set (`rb5s6s.windows.QUOTED`), never a literal here, so
# the reading tracks what the MLE actually reads. The noise law is a FIXED, stated condition (the
# "p_sweep" role's own 4207 line at 130 C, 225 mW, this file's own reference line elsewhere,
# `amp_at`/`model_amp` above), not a free choice per node, so the "record sd" every reading is
# stated in is the same instrument every time.
JOINT_HALF_SPAN_MHZ = 40.0     # matches volume_line.HOMOG_MARGIN_MHZ: well past the widest QUOTED window
JOINT_N_FREQ = 4001
JOINT_N_PATH = 4000            # the reading's own atom count: the subsample AND the table's n_path
                                # (decoupled from n_atoms and measured, see the report)
JOINT_S0_GRID_N = 9            # the diagnostic JointTable's own S0 grid: measured to bring the bilinear
                                # interpolation error at the node's own S0 (the grid's midpoint) to 0.2 per
                                # cent of peak, against 2.8 for the 2-point grid a first version built
JOINT_SD_REPS = 8              # noisy replicas for the record-sd normalisation, seeded and stated
JOINT_NOISE_COND = dict(role="p_sweep", peak="4207", temperature_C=130.0, power_mW=225.0)
POWER_STEP = 0.05             # the central difference for d ln A / d ln P
GRID_W0_UM = tuple(range(34, 59, 2))                      # the 36-56 um scan grid with one node beyond each end, so a fine band at an edge truth has both bracketing nodes; the grid of the 16th ran from the retired band out to 92
GRID_CONDITIONS = tuple((130.0, p) for p in (25.0, 75.0, 125.0, 175.0, 225.0)) + \
                  tuple((t, 225.0) for t in (70.0, 90.0, 110.0)) + \
                  tuple((130.0, p) for p in (90.0, 180.0, 270.0))   # the L's eight conditions, and the LeCroy evening's three


def _rate_table(P_W: float, w0_m: float, T_C: float, rho: float, n: int = 240):
    """G(P_local) tabulated on a log grid of local powers, the saturation carried; below the
    grid the rate is quadratic (the weak field), which is the limit the table's foot sits in."""
    plat = dataclasses.replace(PLATFORMS["cell_130C"], w0_m=w0_m, temperature_k=T_C + 273.15)
    p = np.geomspace(P_W * 1e-5, P_W, n)
    g = np.array([excitation_rate_per_atom(float(x), plat, rho=rho) for x in p])
    return np.log(p), np.log(np.maximum(g, 1e-300))


def _rate(logp_tab, logg_tab, p_local):
    lp = np.log(np.maximum(p_local, 1e-300))
    out = np.exp(np.interp(lp, logp_tab, logg_tab))
    low = lp < logp_tab[0]
    if np.any(low):
        out[low] = np.exp(logg_tab[0] + 2.0 * (lp[low] - logp_tab[0]))
    return out


#: THE BEAM IS AN OBJECT AND ITS FOCUS IS PRODUCED, NOT ASSUMED (F368, owner 2026-09-23). A node names
#: a waist; a waist on this bench is made by SOME input radius through the fixed 3 mm bore, so the beam
#: is found by inverting `ClippedBeam.actual_focus_m()` for that waist rather than by rescaling a
#: Gaussian. Below the bore's own floor no input produces the waist and above the clipping band the
#: input is far inside the bore, so both ends fall back to the diffracting Gaussian WITH A NOTE, which
#: rides in the artefact: a fallback nobody can read is a fallback nobody can weigh.
_BEAM_CACHE: dict = {}
#: the input radii the propagated field's own table accepts (measured 2026-09-23: 0.3 and 8 mm
#: is REFUSED by its interpolation bound, 0.5 to 14 mm are not), giving foci 94.90 to 40.90 um,
#: which reaches the Airy floor 0.4112 lambda f / a = 40.849 um that no input attains (the Thesis
#: Writer, 2026-09-23: the earlier 6 mm bracket stopped at 41.11 and threw 41.00 um nodes to the
#: Gaussian fallback, which is how a too-narrow bracket reads as a physical limit)
W_IN_LO_M, W_IN_HI_M = 0.50e-3, 14.0e-3


class _GaussianBeam:
    """The beam this file used to assume, as an object answering the same two calls."""

    def __init__(self, w0_m: float, m2: float):
        self.w0_m, self.m2 = float(w0_m), float(m2)
        self.z_R = math.pi * self.w0_m ** 2 / (self.m2 * K.LAMBDA_LASER_M)

    def w(self, z_m, clamp=False):
        return self.w0_m * np.sqrt(1.0 + (np.asarray(z_m, float) / self.z_R) ** 2)

    def u(self, r_m, z_m, clamp=False):
        w = self.w(z_m)
        return (self.w0_m / w) ** 2 * np.exp(-2.0 * np.asarray(r_m, float) ** 2 / w ** 2)


def _beam_for(w0_m: float, m2: float):
    """(beam, note) whose ACTUAL focus is `w0_m`, by bisection on the input radius."""
    key = (round(float(w0_m), 12), round(float(m2), 6))
    if key in _BEAM_CACHE:
        return _BEAM_CACHE[key]
    try:
        f_lo = float(BF.ClippedBeam(w_in_m=W_IN_LO_M, m2=m2).actual_focus_m())   # the widest focus
        f_hi = float(BF.ClippedBeam(w_in_m=W_IN_HI_M, m2=m2).actual_focus_m())   # the bore's floor
    except Exception as exc:                       # an M2 the field cannot carry
        out = (_GaussianBeam(w0_m, m2), f"gaussian: the propagated field refused this node ({exc})")
        _BEAM_CACHE[key] = out
        return out
    if not (f_hi <= w0_m <= f_lo):
        side = "below the bore's floor" if w0_m < f_hi else "wider than any clipped input produces"
        out = (_GaussianBeam(w0_m, m2),
               f"gaussian: {w0_m * 1e6:.2f} um is {side} ({f_hi * 1e6:.2f} to {f_lo * 1e6:.2f} um)")
        _BEAM_CACHE[key] = out
        return out
    lo, hi = W_IN_LO_M, W_IN_HI_M                  # focus DECREASES with input radius
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if float(BF.ClippedBeam(w_in_m=mid, m2=m2).actual_focus_m()) > w0_m:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    w_in = 0.5 * (lo + hi)
    beam = BF.ClippedBeam(w_in_m=w_in, m2=m2)
    out = (beam, f"clipped: w_in {w_in * 1e3:.4f} mm gives focus {beam.actual_focus_m() * 1e6:.3f} um")
    _BEAM_CACHE[key] = out
    return out


def _sample(rng, n, w0_m, m2, T_C, half_window_m, beam=None):
    sv = math.sqrt(K.K_B_J_PER_K * (T_C + 273.15) / K.M_RB87_KG)
    if beam is None:
        beam, _ = _beam_for(w0_m, m2)
    z0 = rng.uniform(-half_window_m, half_window_m, n) if half_window_m > 0 else np.zeros(n)
    w = np.asarray(beam.w(z0, clamp=True), float)
    # THE CHORDS OF A UNIFORM ISOTROPIC GAS ARE UNIFORM IN THE IMPACT PARAMETER (the line
    # measure db dphi), not in its area: `transit_mc` draws b uniform in area, which its only
    # validated output, the kernel's width, cannot see (the per-atom shape is blind to b) and
    # the ramp can: 4 per cent in mu2 and five-fold in mu3 (2026-09-16 night, F11).
    #
    # THE PROPOSAL IS A MIXTURE, AND THE PURE HALF-NORMAL IT REPLACES IS A GAUSSIAN-ONLY DEVICE
    # (F372, 2026-09-23). Drawing b from the half-normal e^{-4 b^2 / w^2} and restoring the
    # uniform measure with w e^{+4 b^2 / w^2} leaves FLAT weights only because the two-photon
    # rate carries e^{-4 b^2 / w^2} of its own and cancels it exactly. Behind a bore the rate
    # falls as a POWER, so that cancellation fails and the importance weight diverges: at three
    # radii it is e^{36}, about 4e15, against a rate that is no longer exponentially small, and
    # the estimator's variance is unbounded. So 20 per cent of the draws come from a UNIFORM
    # component over the same support, the weight is one over the MIXTURE density, and it is
    # bounded for any beam. In the Gaussian limit the answer is unchanged and only the variance
    # moves (the self-test plants both).
    r_max = (B_CUT if isinstance(beam, _GaussianBeam) else B_CUT_CLIPPED) * w
    sig_b = w / (2.0 * math.sqrt(2.0))
    # THE TAIL COMPONENT FIRES ONLY WHERE IT IS NEEDED. For a Gaussian the half-normal's weight
    # cancels the rate exactly and the proposal is already optimal, so adding a uniform arm only
    # wastes a fifth of the draws and widened the transit reading from under half a per cent to
    # 0.85. The Gaussian arm is therefore left EXACTLY as it was, which is also what keeps the
    # two-limit self-test a check on the closed form rather than on this change.
    # AND THE GAUSSIAN ARM DOES NOT EVEN DRAW THE MIXTURE'S SELECTOR, so its RANDOM STREAM is
    # bit-identical to the one this file used before the beam became an object. That is what
    # makes the two-limit self-test a plant on the change: the Gaussian node must return the
    # same numbers it always did, not merely numbers inside a tolerance.
    if isinstance(beam, _GaussianBeam):
        # THE GAUSSIAN ARM IS THE OLD CODE, LINE FOR LINE. Not merely the same stream: the same
        # WEIGHT. `1 / p_core` differs from `w e^{4 b^2 / w^2}` by the constant sqrt(pi/2)/(2 sqrt 2),
        # which normalises away inside this file and BROKE the bit-for-bit contract with
        # `volume_line.sample_atoms` that `test_sample_atoms_matches_scripts_run_kernel_mc` asserts.
        # The test caught it; a tolerance would not have.
        b = np.minimum(np.abs(rng.normal(0.0, 1.0, n)) * sig_b, r_max)
        imp_b = w * np.exp(4.0 * b ** 2 / w ** 2)
    else:
        pick = rng.random(n) < TAIL_FRACTION
        b = np.where(pick, rng.random(n) * r_max,
                     np.minimum(np.abs(rng.normal(0.0, 1.0, n)) * sig_b, r_max))
        p_core = math.sqrt(2.0 / math.pi) / sig_b * np.exp(-0.5 * (b / sig_b) ** 2)
        imp_b = 1.0 / ((1.0 - TAIL_FRACTION) * p_core + TAIL_FRACTION / r_max)
    # IMPORTANCE SAMPLING OF THE SPEED (2026-09-16 night). The kernel weights each chord by its
    # flux times its area over its width, which is one power of the speed BELOW the Rayleigh
    # density: sampled from the Maxwellian and weighted by 1/v, the weights' variance diverges
    # logarithmically and the width scattered by 2 per cent between seeds at 200k atoms (the
    # construction `transit_mc` also uses). The speed is drawn from the target density itself,
    # the half-normal e^{-v^2/2 sigma^2}, and the importance factor v rides in `flux_len`.
    v = np.maximum(np.abs(rng.normal(0.0, sv, n)), 1e-9 * sv)
    u_b = np.clip(np.asarray(beam.u(b, z0, clamp=True), float), 0.0, None)  # the chord's peak
    flux_len = v * imp_b * v                        # the crossing flux, the b-measure's factor, the speed's factor
    return w, v, u_b, flux_len, b, z0


def _chord(P_W, u_b, w, v, tab, n_tau, q=0.0, weak=False, beam=None, b=None, z0=None):
    """Along the chord: the rate G(t), the population N(t), the time step. Arrays (atoms, tau)."""
    tau = np.linspace(-TAU_EDGE, TAU_EDGE, n_tau)
    if beam is None or b is None:
        u = u_b[:, None] * np.exp(-2.0 * tau[None, :] ** 2)
    else:
        # THE ATOM TRAVERSES THE REAL PROFILE. At chord time t its radius is
        # sqrt(b^2 + (v t)^2), and tau = v t / w, so r = sqrt(b^2 + (w tau)^2) with no
        # speed in it. For a Gaussian this is identically u_b exp(-2 tau^2), which is the
        # line above, so the branch is exact in the limit and not an approximation of it.
        r = np.sqrt(b[:, None] ** 2 + (w[:, None] * tau[None, :]) ** 2)
        zz = np.broadcast_to(z0[:, None], r.shape)
        u = np.clip(np.asarray(beam.u(r, zz, clamp=True), float), 0.0, None)
    if weak:
        g0 = _rate(*tab, np.array([P_W * 1e-3]))[0] / (P_W * 1e-3) ** 2   # the weak-field coefficient
        G = g0 * (P_W * u) ** 2
    else:
        G = _rate(*tab, P_W * u)
    dt = (w / v)[:, None] * (tau[1] - tau[0])
    if q > 0.0:
        cum = np.cumsum(0.5 * (G[:, 1:] + G[:, :-1]) * dt, axis=1)
        N = np.exp(-q * np.concatenate([np.zeros((G.shape[0], 1)), cum], axis=1))
    else:
        N = np.ones_like(G)
    return G, N, dt, u


def _kernel(nu_mhz, weights, w, v):
    """The ensemble's lineshape: each chord's AREA (its excitations per unit time) times its
    unit-area Gaussian, whose peak goes as w/v. Weighting the unit-peak Gaussian by the area
    instead is one power of the speed and read the cusp 1.8x too wide (the self-test's plant)."""
    weights = weights * w / v
    kcoef = w ** 2 / (4.0 * v ** 2)
    f = np.asarray(nu_mhz, float) * 1e6
    L = np.array([np.sum(weights * np.exp(-(2.0 * math.pi) ** 2 * x * x * kcoef)) for x in f])
    return L / L[0]


def _fwhm(nu, L):
    i = int(np.argmax(L < 0.5))
    x0, x1, y0, y1 = nu[i - 1], nu[i], L[i - 1], L[i]
    return 2.0 * (x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0))


def _moments(values, weights):
    wsum = weights.sum(); m = (weights * values).sum() / wsum
    d = values - m
    mu2 = (weights * d ** 2).sum() / wsum; mu3 = (weights * d ** 3).sum() / wsum
    return float(m), float(mu2), float(mu3)


def _ramp_reference(n=20001):
    s = np.linspace(0.0, 1.0, n); f = lineshape.stark_ramp(s, 1.0)
    return _moments(s, f)


def _cycles_axis(tab, P_W: float, w0_m: float, T_C: float) -> float:
    """The on-axis cycles per crossing at power P_W: the chord's time-integrated rate at the node's
    own saturation (`_rate_table` at that power), over the thermal crossing time. F134's known half:
    the cycles come from the SATURATED rate, so the depletion's law departs from P^2 as the rate does."""
    tau = np.linspace(-TAU_EDGE, TAU_EDGE, 4001)
    return float(trapezoid(_rate(*tab, P_W * np.exp(-2.0 * tau ** 2)), tau)
                 * w0_m / math.sqrt(math.pi * K.K_B_J_PER_K * (T_C + 273.15) / (2.0 * K.M_RB87_KG)))


def _load_contract():
    """The Monte Carlo contract, or None where `private/` is absent (the public mirror, a stranger's clone).

    The contract lives in the governance tree and binds every node run HERE; a checkout without it runs
    the sampler at the numerics its caller names, and says so, instead of dying on a missing file
    (2026-09-24)."""
    path = ROOT / "private" / "checks" / "mc_contract.py"
    if not path.is_file():
        return None
    import importlib.util as _ilu
    _s = _ilu.spec_from_file_location("mc_contract", path)
    _m = _ilu.module_from_spec(_s); _s.loader.exec_module(_m)
    return _m


def _joint_line(nu_mhz, s0_mhz, gamma_hom_mhz, w, v, u_b, flux_len, *,
                sign=None, n_tau=VL_N_TAU, tau_edge=VL_TAU_EDGE):
    """The joint per-path line at a RANDOM SUBSAMPLE of the atoms passed in (the node's own
    `_sample`), run through `volume_line.joint_spectrum`'s own per-atom recipe UNBINNED --
    verbatim (`run_kernel_mc._self_test` plants the two byte-identical on the same atoms and
    seed). Each atom carries its own accumulated light-shift phase (`sign * s0_mhz * u_b`, `u_b`
    the chord's own peak intensity factor) and its own two-time correlation
    (`f = u_b * exp(-2 tau^2) * exp(i phi)`, `n_tau`/`tau_edge` `volume_line`'s own, for the same
    grid resolution `JointTable` samples at): the two are the SAME atom's, so the pairing a
    convolution discards is carried into the sum.

    WHY A SUBSAMPLE AND NOT A HISTOGRAM, though the brief asked to follow
    `run_kernel_inhomogeneity.py`'s binned construction: tried first, and measured wrong (see the
    module-level comment beside `JOINT_N_PATH` for the numbers). `run_kernel_inhomogeneity.py`'s
    cells carry a CLOSED-FORM kernel evaluated exactly at each cell's own (shift, transit), while
    this line is a two-time correlation whose per-atom output is not linear in the atom's own
    (u_b, w/v), so a cell's mean does not reproduce its members' sum, and `w/v`'s own heavy tail
    (99.9999 per cent of the sampled flux inside the bottom one per cent of its value range at
    this corner) left every histogram tried -- linear, quantile, nested by (z, then
    shift-within-z) as `run_kernel_inhomogeneity.py`'s own grid is -- PLATEAUED at 0.05 to 0.36 of
    peak against `joint_spectrum` without converging. A random subsample is UNBIASED by construction (a
    smaller Monte Carlo IS one), measured against an independently seeded 200 000-atom reference at
    0.002 to 0.011 of peak across five sizes 500 to 8000 -- ordinary scatter, not a plateau -- and
    fast (1.5 s at 8000 atoms). `n_path` (below, `run_node`'s own keyword) sizes the subsample.

    `gamma_hom_mhz` is applied ONCE, after the atoms are summed, matching how
    `volume_line.JointTable.profile` applies its own homogeneous width after the ensemble (F317):
    the two lines are built in the same order, so this comparison is not confounded by the wing
    defect F317 found and repaired in the per-atom route.

    Returns the line peak-normalised to 1 (`transit_shape_rel`'s own convention, "over the peak").
    """
    sign = lineshape.RAMP_SIDE if sign is None else float(sign)
    nu_mhz = np.asarray(nu_mhz, dtype=float)
    tau = np.linspace(-tau_edge, tau_edge, n_tau)
    dtau = tau[1] - tau[0]
    genv = np.exp(-2.0 * tau ** 2)
    cs = np.cumsum(genv)
    n2 = 1 << int(np.ceil(np.log2(2 * n_tau - 1)) + 1)
    spec = np.zeros_like(nu_mhz)
    for i in range(w.shape[0]):
        dt = (w[i] / v[i]) * dtau
        phi = sign * 2.0 * math.pi * float(s0_mhz) * 1e6 * u_b[i] * cs * dt
        f = u_b[i] * genv * np.exp(1j * phi)
        Fa = np.fft.fft(f, n2)
        C = np.fft.ifft(np.abs(Fa) ** 2)
        Cd = np.concatenate([C[n2 - (n_tau - 1):], C[:n_tau]]) * dt       # linear autocorr, lags -(n_tau-1)..n_tau-1
        buf = np.zeros(n2, dtype=complex)
        buf[:n_tau] = Cd[n_tau - 1:]                 # lags 0 .. n_tau-1
        buf[n2 - (n_tau - 1):] = Cd[:n_tau - 1]       # lags -(n_tau-1) .. -1
        S = np.fft.fft(buf) * dt
        freq_hz = np.fft.fftfreq(n2, d=dt)
        order = np.argsort(freq_hz)
        spec += flux_len[i] * np.interp(nu_mhz, freq_hz[order] / 1e6, np.real(S[order]), left=0.0, right=0.0)
    if gamma_hom_mhz > 0.0:
        dnu = float(nu_mhz[1] - nu_mhz[0])
        spec = np.convolve(spec, lineshape.lorentzian(nu_mhz, float(gamma_hom_mhz)), mode="same") * dnu
    peak = float(spec.max())
    return spec / peak if peak > 0.0 else spec


def _record_sd_of_moments(nu_mhz, clean, law, orders, windows, *, n_rep=JOINT_SD_REPS, seed=0):
    """The record's own replica scatter of each windowed central moment: `n_rep` noisy draws of
    `clean` at the condition's own measured noise law (`load_noise_model`'s convention,
    `sigma_of_v` evaluated at the clean line's own level with peak amplitude 1.0, matching
    `twin_volume.synthetic_traces`'s own default amplitude convention), the sample standard
    deviation of `windowed_moments` across the draws. This is the unit F318's own readings are
    stated in ("record sd"). It is MEASURED here, from the noise law a real condition carries,
    never assumed."""
    rng = np.random.default_rng(seed)
    clean = np.asarray(clean, dtype=float)
    reps = {o: {w: [] for w in windows} for o in orders}
    for _ in range(int(n_rep)):
        sigma = np.asarray(sigma_of_v(np.clip(clean, 0.0, None), law), dtype=float)
        noisy = clean + sigma * rng.standard_normal(clean.shape)
        for wdw in windows:
            vals, _info = windowed_moments(nu_mhz, noisy, wdw, orders=orders, baseline=None)
            for o in orders:
                reps[o][wdw].append(vals[o])
    return {(o, wdw): float(np.std(np.asarray(reps[o][wdw]), ddof=1)) for o in orders for wdw in windows}


#: the registry terms this Monte Carlo applies by construction, whatever its knobs: the saturated chord rate with
#: the cascade's pumping and depletion, the four lines' shares, the ramp and its reduced mean pull, the transit at
#: the beam's own M2, the natural width. The bore and the collected window depend on what the node BUILT.
MC_STRUCTURAL_TERMS = ("ac_stark_ramp", "beam_quality_m2", "companion_pull_reduction", "depletion_cascade",
                       "hyperfine_pumping", "hyperfine_shares", "natural_width", "saturation", "transit")


def registry_preflight(*, beam_note: str, half_window_m: float, P_mW: float, T_C: float,
                       mc_deviations=None) -> dict:
    """O58: the node refuses BEFORE its first atom unless the terms it will execute are the registry's
    Monte Carlo at the node's regime, read off the beam it BUILT and the window it will sample (F457: a
    contract graded against the request is not a contract). A term it drops or adds is a declared study,
    and its reason is the deviation the caller already gave under the knob that drops it (`beam_kind` for
    the bore, `half_window_m` for the collected window) or under the term's own id."""
    dev = dict(mc_deviations or {})
    executes = set(MC_STRUCTURAL_TERMS)
    if not str(beam_note).startswith("gaussian"):
        executes.add("bore_clipping")
    if float(half_window_m) > 0.0:
        executes.add("axial_collection_window")
    regime = "2025" if (float(P_mW) <= 270.0 + 1e-9 and float(T_C) <= 130.0 + 1e-9) else "campaign"
    carried = set(_MR.carried_term_ids("mc", regime))
    knob = {"bore_clipping": "beam_kind", "axial_collection_window": "half_window_m"}
    gaps = {t: dev.get(knob.get(t, t), dev.get(t, "")) for t in sorted(carried - executes)}
    extras = {t: dev.get(t, "") for t in sorted(executes - carried)}
    return _MR.preflight("mc", regime, executes, scope="study" if (gaps or extras) else "result",
                         gaps=gaps, extras=extras)


def run_node(w0_um, m2, rho, T_C, P_mW, *, n_atoms=None, half_window_m=None,
             cycles_model=0.0, seed=0, n_tau=N_TAU, depletion_form="mc",
             beam_kind="clipped", mc_deviations=None, joint_n_path=JOINT_N_PATH, stop_after=""):
    """THE MONTE CARLO IS CALLED AT ONE SET OF NUMERICS OR THE RUN IS THROWN AWAY (O56, the owner,
    nine times). Until 2026-09-24 this file referenced `mc_contract` ZERO times: the twin's LINE was
    guarded by `twin_callers` and the KERNEL MONTE CARLO, which is what the order names, was under
    no contract at all. The node population was already MIXED, 130 artefacts at 100 000 atoms and
    123 at 400 000, while `depleted_line_abs` is sampler noise A188 puts at 0.00234 and 0.00089 for
    those two counts against a tolerance of 0.002 -- so a node could fail a reading on its atom
    count alone and nothing said so. `n_atoms` now defaults to the contract's value instead of a
    literal, and a departure needs a reason of six words through `mc_deviations`.

    The node's COORDINATES (`w0_um`, `m2`, `rho`, `T_C`, `P_mW`) are swept by design and are not in
    the contract. Its NUMERICS are, because the gate grades every node against one set of
    tolerances."""
    _MC = _load_contract()
    if n_atoms is None:
        if _MC is None:
            raise SystemExit("run_kernel_mc: no atom count given and no contract in this checkout "
                             "(private/checks/mc_contract.py is absent, as in the public mirror); pass n_atoms")
        n_atoms = _MC.kernel_contract()["n_atoms"]
    if _MC is not None:
        _MC.guard_kernel_node(n_atoms=n_atoms, seed=seed, depletion_form=depletion_form,
                              beam_kind=beam_kind, deviations=mc_deviations)
    t0 = time.time()
    w0_m, P_W = w0_um * 1e-6, P_mW * 1e-3
    z_R = math.pi * w0_m ** 2 / (float(m2) * K.LAMBDA_LASER_M)
    if half_window_m is None:                     # the record's own collected column, L = z_ratio z_R
        half_window_m = FM.collection_z_ratio_m2(w0_m, m2) * z_R
    zr = half_window_m / z_R
    rng = np.random.default_rng(seed)
    if beam_kind == "gaussian":
        beam, beam_note = _GaussianBeam(w0_m, m2), "gaussian: asked for by the caller"
    else:
        beam, beam_note = _beam_for(w0_m, m2)
        # THE CONTRACT GRADED THE REQUEST AND THE RUN USED A DIFFERENT BEAM (2026-09-24, F457).
        # `_beam_for` falls back to a diffracting Gaussian whenever the asked-for waist is below the
        # bore's reachable floor. `guard_kernel_node` sees beam_kind="clipped" because that is what the
        # CALLER asked for, matches it against the contract's 'clipped', and passes -- so four nodes ran
        # with no bore in the Monte Carlo at all and three of them recorded PASS at the contract's atom
        # count, indistinguishable in the population from a validated node. A contract satisfied by an
        # INTENTION is not a contract. The produced beam is graded here, where it exists, and before the
        # sampler spends anything. An explicit `--beam gaussian` is untouched: that is a declared choice.
        if beam_note.startswith("gaussian") and not (mc_deviations or {}).get("beam_kind"):
            raise _MC.ContractBreach(
                f"mc-contract kernel: beam_kind='clipped' was asked for and this node produced "
                f"{beam_note!r}. The bore is absent from this Monte Carlo, so every reading it "
                f"returns is about a beam the apparatus cannot make (F382, A192). Ask for the "
                f"Gaussian explicitly, declare the deviation, or choose a reachable waist.")
    registry_block = registry_preflight(beam_note=beam_note, half_window_m=half_window_m, P_mW=P_mW, T_C=T_C,
                                        mc_deviations=mc_deviations)
    if stop_after == "preflight":
        # a plant of the refusals at construction and at the door reads this far and no further (O59 F2): the beam is
        # built and graded, the registry has admitted it, and not one atom has been sampled
        return None, {"beam_note": beam_note, "registry": registry_block}
    w, v, u_b, flux_len, b_imp, z_imp = _sample(rng, n_atoms, w0_m, m2, T_C,
                                                half_window_m, beam=beam)
    _bk = dict(beam=beam, b=b_imp, z0=z_imp)
    tab = _rate_table(P_W, w0_m, T_C, rho)
    ref_bare = K.transit_fwhm_from_w0(w0_m, T_C, isotope=87)
    # THE TRANSIT REFERENCE GAINS THE BEAM'S OWN AXIAL WIDTH (F374, 2026-09-23), THROUGH THE ONE
    # FUNCTION scripts/run_ultra_joint.py's Cell now calls too (F471, plan item V5.19a).  # ladder-exempt: prose
    # `beam_field.clipped_transit_fwhm_mhz` carries the ratio of `effective_transit_radius` on the
    # free-space beam over this node's own, weighted by the same saturated chord rate below, so a
    # validated node certifies the transit the fitter actually runs. `z_ratio` and `half_window_m`
    # are passed through exactly as already computed here, so this node's reading is unchanged to
    # the bit; passing beam=None whenever `beam` is already this file's own `_GaussianBeam` (asked
    # for directly, or the fallback `_beam_for` returns) keeps the ratio at one without spending an
    # `effective_transit_radius` call that would only reproduce it.
    _rate_w = (lambda uu: _rate(*tab, P_W * uu))
    _ref_beam = beam if not isinstance(beam, _GaussianBeam) else None
    ref_fwhm = BF.clipped_transit_fwhm_mhz(
        w0_m, m2, T_C, isotope=87, z_ratio=zr, half_window_m=half_window_m, rate=_rate_w,
        beam=_ref_beam)
    # beam_transit_corr is the artefact's own detail field (read by kernel_gate and by this
    # session's own private/tmp/b_terms_notes/transit_gap_report.py, among others), computed the
    # same way clipped_transit_fwhm_mhz computes its internal correction rather than backed out of
    # ref_fwhm by division, which left a 1-ULP difference against the pre-existing value at some
    # nodes (floating-point division is not the exact inverse of the multiplication that built it).
    if zr > 0 and _ref_beam is not None:
        beam_transit_corr = (BF.effective_transit_radius(_GaussianBeam(w0_m, m2), half_window_m, rate=_rate_w)
                             / BF.effective_transit_radius(_ref_beam, half_window_m, rate=_rate_w))
    else:
        beam_transit_corr = 1.0
    nu = np.linspace(0.0, 6.0 * ref_fwhm, 721)
    # --- the transit kernel, no depletion: the time-integrated rate weights each chord
    G, N1, dt, u = _chord(P_W, u_b, w, v, tab, n_tau, **_bk)
    sig0 = (G * dt).sum(axis=1) * flux_len
    L0 = _kernel(nu, sig0, w, v); fwhm_mc = _fwhm(nu, L0)
    cusp = lineshape.two_sided_exponential(nu, fwhm_mc); cusp = cusp / cusp[0]
    sel = nu <= 3.0 * fwhm_mc
    shape_dev = float(np.max(np.abs(L0[sel] - cusp[sel])))      # encoded below as 1 + dev against 1
    # --- the ramp: the rate-weighted instantaneous shift, saturated and weak-field, mu3's grid movement
    Gw, _, _, _ = _chord(P_W, u_b, w, v, tab, n_tau, weak=True, **_bk)
    shift = +u                                                          # BLUE-sided (O27), units of S0
    wt_sat = (G * dt) * flux_len[:, None]; wt_weak = (Gw * dt) * flux_len[:, None]
    m_s, mu2_s, mu3_s = _moments(shift, wt_sat); m_w, mu2_w, mu3_w = _moments(shift, wt_weak)
    Gh, _, dth, uh = _chord(P_W, u_b, w, v, tab, (n_tau - 1) // 2 + 1, **_bk)
    # THE SAME SIDE AS THE FULL GRID, and it was not (2026-09-18). When the ramp's side was flipped
    # to blue (O27) line 210 above became `shift = +u` and this halved-grid twin kept `-uh`. mu3 is
    # ODD, so the convergence check has been differencing mu3 against MINUS ITSELF ever since, and
    # `grid_movement` read |2 mu3| / |mu3_ref| ~ 1.9 at every node instead of the movement. Measured on
    # w38.0_m1.00_r0.940_T130_P75: reported 1.92288 against |2 mu3|/|mu3_ref| = 1.92477, agreeing to
    # 0.1 per cent, so the true movement was the residue, 0.0019. mu2 is EVEN and was immune, which is
    # why its own movement read 6e-6 and nothing looked odd. Nothing caught it because `judge` tested
    # that the field was PRESENT and never what it said.
    shift_h = +uh                                                       # BLUE-sided (O27), as above
    _, mu2_h, mu3_h = _moments(shift_h, (Gh * dth) * flux_len[:, None])
    # THE MODEL'S RAMP IS THE SATURATED DENSITY IN THE AXIAL MIXTURE (F133, 2026-09-18). Until this
    # day the reference was the weak-field law (`stark_ramp_axial_moments`), and every node with
    # P/w0^2 over 0.078 mW/um^2 failed mu3 by 8 to 15 per cent (F131, F132): the Monte Carlo's chord
    # saturates and the reference did not. The density is the Cell's own (`window_profile` with the
    # trace's power), so a PASS here certifies the model the fit uses. The sign convention follows
    # `shift = +u` above: the reference mean is POSITIVE (blue) as the Monte Carlo's is; the old
    # `-abs(mean)` in the detail was a leftover of the red-sided kernel.
    # THE MODEL SIDE READS THE SAME BEAM AND THE SAME SATURATED RATE (F368). The Gaussian route
    # below is kept and reported beside it, because the DIFFERENCE between them is the cost of
    # the beam the fitter still assumes, and a number nobody prints is a number nobody can act on.
    _xg = np.linspace(0.0, 1.0, 4001)
    _gx = lineshape.saturated_ramp_density(_xg, P_W, w0_m, T_C, rho)
    mm_gauss = lineshape.ramp_mixture_moments(1.0, zr, _xg, _gx, n_photon=2)
    mm = BF.shift_moments(beam, half_window_m, rate=lambda uu: _rate(*tab, P_W * uu))
    m_ref, mu2_ref, mu3_ref = mm["mean"], mm["var"], mm["mu3"]
    # --- depletion per line: the surviving signal, the surviving kernel's width, the shares
    per_line, dep = {}, {}
    for peak, q in BRANCHING_F.items():
        Gq, Nq, dtq, _ = _chord(P_W, u_b, w, v, tab, n_tau, q=q, **_bk)
        sig = (Gq * Nq * dtq).sum(axis=1) * flux_len
        per_line[peak] = float(sig.sum() / sig0.sum())                   # surviving fraction of the signal
        dep[peak] = _fwhm(nu, _kernel(nu, sig, w, v))
    cycles_axis = _cycles_axis(tab, P_W, w0_m, T_C)
    # THE FLUX-WEIGHTED MEAN BY QUADRATURE (2026-09-17, the physics chair): as a sample mean it
    # carried the b-weight e^{4b^2/w^2}, whose mean over a finite half-normal draw is set by the
    # largest draw and scattered 7 per cent between seeds while every ratio scattered under 0.3;
    # the widths and moments are ratios in which the weight is flat, this one cell was not.
    _bq = np.linspace(0.0, B_CUT * w0_m, 241); _vq = np.linspace(1e-3, 4.5, 121) * math.sqrt(K.K_B_J_PER_K * (T_C + 273.15) / K.M_RB87_KG)
    _tau = np.linspace(-TAU_EDGE, TAU_EDGE, 401)
    _cyc_b = np.array([trapezoid(_rate(*tab, P_W * math.exp(-2.0 * bb ** 2 / w0_m ** 2) * np.exp(-2.0 * _tau ** 2)), _tau) for bb in _bq])   # per unit (w/v)
    _sv = math.sqrt(K.K_B_J_PER_K * (T_C + 273.15) / K.M_RB87_KG)
    _fv = _vq * np.exp(-_vq ** 2 / (2.0 * _sv ** 2))                      # the 2D Maxwellian
    _flux = _vq * _fv                                                    # the crossing flux
    _cyc_v = w0_m / _vq                                                  # the chord time factor per unit tau
    cycles_mean = float((trapezoid(_cyc_b, _bq) * trapezoid(_flux * _cyc_v, _vq)) / (trapezoid(np.ones_like(_bq), _bq) * trapezoid(_flux, _vq)))
    # --- the amplitude's local power law: Monte Carlo (saturation + depletion, line 4207) against the model's law
    def amp_at(scale, q):
        tab_s = _rate_table(P_W * scale, w0_m, T_C, rho)
        Gs, Ns, dts, _ = _chord(P_W * scale, u_b, w, v, tab_s, n_tau, q=q, **_bk)
        return float(((Gs * Ns * dts).sum(axis=1) * flux_len).sum())
    q4 = BRANCHING_F["4207"]
    a_hi, a_lo = amp_at(1.0 + POWER_STEP, q4), amp_at(1.0 - POWER_STEP, q4)
    expo_mc = math.log(a_hi / a_lo) / math.log((1.0 + POWER_STEP) / (1.0 - POWER_STEP))
    def model_amp(scale):
        # THE RECORD'S OWN RATE OVER THE TRANSVERSE PLANE (rung 2): the measure is du/u for
        # u = I/I0, so A(P) = int_0^1 G(P u) du/u with the saturation `excitation_rate_per_atom`
        # carries, times the cascade's per-crossing factor at the on-axis cycles; the weak field
        # gives P^2 exactly. What the Monte Carlo adds is the chord: the velocity-resolved
        # depletion and the finite crossing, which is the reading's content.
        tab_s = _rate_table(P_W * scale, w0_m, T_C, rho)
        lu = np.linspace(math.log(1e-4), 0.0, 2001); uu = np.exp(lu)
        a_plane = float(trapezoid(_rate(*tab_s, P_W * scale * uu), lu))          # du/u = d(ln u)
        # F134's known half (2026-09-18): the cycles at the scaled power come from the SATURATED rate,
        # not from `cycles_axis * scale**2`, the weak-field law that was here. Measured on the band
        # before the change: 21 of 39 nodes inside 0.02 with this repair, the worst at 0.0502; the
        # other half, the velocity-resolved depletion along the chord, is not a one-line term and is
        # why the waist analyses read the gate on `kernel_gate.WAIST_READINGS` (D1).
        c = _cycles_axis(tab_s, P_W * scale, w0_m, T_C)
        return a_plane * amplitude_factor("4207", c)
    expo_model = math.log(model_amp(1.0 + POWER_STEP) / model_amp(1.0 - POWER_STEP)) / math.log((1.0 + POWER_STEP) / (1.0 - POWER_STEP))
    # --- the shares
    th = predicted_shares()
    mc_sh = {p: th[p] * per_line[p] for p in th}; z = sum(mc_sh.values()); mc_sh = {p: x / z for p, x in mc_sh.items()}
    md_sh = {p: th[p] * amplitude_factor(p, cycles_axis) for p in th}; z = sum(md_sh.values()); md_sh = {p: x / z for p, x in md_sh.items()}
    shares_dev = max(abs(mc_sh[p] - md_sh[p]) for p in th)
    shares_shift = max(abs(mc_sh[p] - th[p]) for p in th)          # thermal to depleted: the physical move
    # --- the model's transit at its declared depletion arm
    from scripts.run_ultra_joint import depleted_transit                # noqa: E402  (the Cell's own form)
    om = 1.2511 * K.stark_shift_s0_mhz(P_W, w0_m, rho) if hasattr(K, "stark_shift_s0_mhz") else 0.0
    dep_rel = {p: dep[p] / fwhm_mc - 1.0 for p in th}          # the FWHM's widening: a diagnostic, not what a fit reads
    # WHAT A TRANSIT FIT READS (2026-09-17 06:50, a question from the chapter's side and an
    # independent sub-micron check): depletion removes the slowest atoms, which are the cusp's core, and leaves
    # the wings, so a cusp fitted to the surviving kernel reads far less than the FWHM says: at the
    # corner the FWHM widens by 0.051 and the fitted cusp, after the natural Lorentzian, by 0.005.
    # The fit carries the FITTED ratio; a cusp widened by the FWHM ratio misses the depleted line
    # nine times worse than the bare cusp does.
    from scipy.optimize import minimize_scalar
    nus = np.concatenate([-nu[:0:-1], nu]); dnu = nus[1] - nus[0]
    gam = K.GAMMA_NAT_HZ / 1e6
    lor = (gam / 2) / math.pi / (nus ** 2 + (gam / 2) ** 2); lor /= trapezoid(lor, nus)
    def _sym(Lp):
        a = np.concatenate([Lp[:0:-1], Lp]); return a / trapezoid(a, nus)
    def _line(a):
        c = np.convolve(a, lor, mode="same") * dnu; return c / trapezoid(c, nus)
    def _cusp(fw):
        c = lineshape.two_sided_exponential(nus, fw); return c / trapezoid(c, nus)
    def _fit(target):
        return float(minimize_scalar(lambda x: float(np.sum((_line(_cusp(x)) - target) ** 2)),
                                     bounds=(0.5 * fwhm_mc, 2.0 * fwhm_mc), method="bounded").x)
    fit_bare = _fit(_line(_sym(L0)))
    dep_fit = {}
    for p in th:
        Gq, Nq, dtq, _ = _chord(P_W, u_b, w, v, tab, n_tau, q=BRANCHING_F[p], **_bk)
        Lq = _kernel(nu, (Gq * Nq * dtq).sum(axis=1) * flux_len, w, v)
        dep_fit[p] = _fit(_line(_sym(Lq))) / fit_bare - 1.0
    if depletion_form == "mc":
        # THE FIT CARRIES THIS NODE'S OWN FACTOR (F15), so the reading certifies the number's
        # convergence: the surviving kernel's width on the chord grid against the halved grid,
        # on the line with the largest depletion; the interpolation between nodes is the gate's
        # own plant (`kernel_gate --self-test`), and the factor's smoothness is in the artefact.
        model_dep = {}
        for p in th:
            Gq, Nq, dtq, _ = _chord(P_W, u_b, w, v, tab, (n_tau - 1) // 2 + 1, q=BRANCHING_F[p], **_bk)
            model_dep[p] = _fwhm(nu, _kernel(nu, (Gq * Nq * dtq).sum(axis=1) * flux_len, w, v))
    else:
        model_dep = {p: depleted_transit(ref_fwhm, om, p, cycles_model) for p in th}
        # THE DEPLETION READING ON THE FIT'S OBSERVABLE (the physics chair, 2026-09-17): after the
    # natural Lorentzian a core narrower than it is mostly an amplitude, so no kernel width is the
    # right observable. The composed depleted line (worst line) against the fit's own form, the
    # cusp at the bare width times the fitted ratio, composed the same way: peak-normalised misfit.
    worst_q = max(th, key=lambda p: dep_fit[p])
    Gq, Nq, dtq, _ = _chord(P_W, u_b, w, v, tab, n_tau, q=BRANCHING_F[worst_q], **_bk)
    Lq_line = _line(_sym(_kernel(nu, (Gq * Nq * dtq).sum(axis=1) * flux_len, w, v)))
    fit_line = _line(_cusp(fwhm_mc * (1.0 + dep_fit[worst_q])))
    dep_line_misfit = float(np.max(np.abs(fit_line - Lq_line)) / np.max(Lq_line))
    # --- THE JOINT LINE (C6b, the merge's 5a): the node's own sample against volume_line.JointTable,
    # the shape and the windowed moments mu2, mu3, mu4 at the joint vector's own windows, in the
    # record's own standard deviation at the node's stated reference condition (JOINT_NOISE_COND).
    # Weak field, no session term, by construction: a node carries no gamma_coll/sigma_laser axis,
    # so both lines below are built with the natural width alone, exactly matching how
    # transit_fwhm_rel/transit_shape_rel above compare bare kernels.
    s0_mhz = lineshape.stark_shift_S0_mhz(P_W, w0_m, rho)
    gamma_hom_ref_mhz = K.GAMMA_NAT_HZ / 1e6
    nu_joint = np.linspace(-JOINT_HALF_SPAN_MHZ, JOINT_HALF_SPAN_MHZ, JOINT_N_FREQ)
    # A RANDOM SUBSAMPLE of the node's own atoms, never a fresh draw (`_joint_line`'s own docstring
    # states why a subsample and not a histogram): a seed derived from this node's own, so the
    # subsample is reproducible and distinct from every other draw this node makes.
    n_sub = min(int(joint_n_path), w.shape[0])
    sub = np.random.default_rng(seed + 11).choice(w.shape[0], size=n_sub, replace=False)
    L_mc_joint = _joint_line(nu_joint, s0_mhz, gamma_hom_ref_mhz, w[sub], v[sub], u_b[sub], flux_len[sub])
    # One waist node (the Cell's own convention, JointTable's "one waist node is a table at one
    # waist"), an S0 axis bracketing the node's own shift so the fitter's OWN bilinear
    # interpolation is exercised, not a synthetic exact-node comparison -- but FINE ENOUGH that
    # the interpolation is not itself what the reading measures. A first version used a 2-point
    # grid [0, 2 s0_mhz] read at its own midpoint and measured a 2.8 per cent interpolation error
    # there against `joint_spectrum` called directly at that S0 (this corner, gamma_hom the
    # natural width): most of what the reading first reported as "the joint pairing". Nine points
    # over the same span reads 0.2 per cent, matching the atom count's own Monte Carlo floor
    # (JOINT_S0_GRID_N below, the margin behind the gate's tolerance states this number).
    s0_hi = max(2.0 * s0_mhz, 1e-6)
    joint_table = JointTable.build(S0_grid=np.linspace(0.0, s0_hi, JOINT_S0_GRID_N), w0_grid=np.array([w0_m]),
                                   delta_mhz=nu_joint, m2=m2, T_C=T_C, n_path=int(joint_n_path),
                                   seed=seed, half_window_m=half_window_m)
    L_table_joint = joint_table.profile(nu_joint, s0_mhz=s0_mhz, w0_m=w0_m,
                                        gamma_hom_mhz=gamma_hom_ref_mhz, sigma_laser_mhz=0.0)
    L_table_peak = float(L_table_joint.max())
    L_table_norm = L_table_joint / L_table_peak if L_table_peak > 0.0 else L_table_joint
    joint_shape_dev = float(np.max(np.abs(L_mc_joint - L_table_norm)))
    joint_orders = (2, 3, 4)
    mu_mc = {wdw: windowed_moments(nu_joint, L_mc_joint, wdw, orders=joint_orders, baseline=None)[0]
             for wdw in JOINT_WINDOWS_MHZ}
    mu_tab = {wdw: windowed_moments(nu_joint, L_table_norm, wdw, orders=joint_orders, baseline=None)[0]
              for wdw in JOINT_WINDOWS_MHZ}
    joint_law = load_noise_model(Path(os.environ.get("RB5S6S_RESULTS_DIR", str(_RESULTS_DIR))) / "noise_model.csv",
                                 **JOINT_NOISE_COND)
    joint_sd = _record_sd_of_moments(nu_joint, L_table_norm, joint_law, joint_orders, JOINT_WINDOWS_MHZ,
                                      seed=seed + 7)
    joint_dev_sigma = {(o, wdw): abs(mu_mc[wdw][o] - mu_tab[wdw][o]) / joint_sd[(o, wdw)]
                       for wdw in JOINT_WINDOWS_MHZ for o in joint_orders}
    joint_moment_sigma = float(max(joint_dev_sigma.values()))
    joint_worst = max(joint_dev_sigma, key=joint_dev_sigma.get)
    readings = {
        "transit_fwhm_rel": {"mc": fwhm_mc, "model": ref_fwhm},
        "transit_shape_rel": {"mc": 1.0 + shape_dev, "model": 1.0},
        "ramp_mu2_rel": {"mc": mu2_s, "model": mu2_ref, "weak_field_mc": mu2_w},
        "ramp_mu3_rel": {"mc": mu3_s, "model": mu3_ref, "weak_field_mc": mu3_w,
                        "grid_movement": abs(mu3_s - mu3_h) / abs(mu3_ref)},
        "amplitude_power_law_abs": {"mc": expo_mc, "model": expo_model},
        "shares_abs": {"mc": shares_dev, "model": 0.0},
        "joint_shape_abs": {"mc": joint_shape_dev, "model": 0.0,
                            "note": "a random subsample of the node's own atoms, run through joint_spectrum's own "
                                    "per-atom recipe, against volume_line.JointTable: the largest absolute "
                                    "difference of the two peak-normalised lines"},
        "joint_moment_sigma_abs": {"mc": joint_moment_sigma, "model": 0.0,
                                   "worst_at": f"mu{joint_worst[0]}@{joint_worst[1]:g}",
                                   "note": "the worst of |mu2,mu3,mu4 (the atom subsample) - mu2,mu3,mu4 (JointTable)| "
                                           "over rb5s6s.windows.QUOTED, each in the record's own sd at "
                                           f"{JOINT_NOISE_COND}"},
        "depleted_line_abs": {"mc": dep_line_misfit, "model": 0.0, "line": worst_q,
                              "note": "the composed depleted line against the fit's form (the cusp at the bare width times the fitted ratio) composed the same way, peak-normalised"},
    }
    detail = {
        "node": dict(w0_um=w0_um, m2=m2, rho=rho, T_C=T_C, P_mW=P_mW), "n_atoms": n_atoms, "n_tau": n_tau,
        "half_window_m": half_window_m, "cycles_model": cycles_model, "seed": seed, "depletion_form": depletion_form,
        "registry": registry_block,
        "beam_kind": beam_kind, "beam_note": beam_note, "beam_transit_corr": beam_transit_corr,
        "ramp_model_gaussian": {"mean": mm_gauss["mean"], "var": mm_gauss["var"], "mu3": mm_gauss["mu3"]},
        "beam_cost_rel": {k: (float(mm[k] / mm_gauss[k] - 1.0) if mm_gauss[k] else float("nan"))
                          for k in ("mean", "var", "mu3")},
        "cycles_on_axis": cycles_axis, "cycles_mean_over_chords": cycles_mean,
        "ramp_mean": {"mc": m_s, "weak_field_mc": m_w, "model": m_ref},
        "ramp_mu2_grid_movement": abs(mu2_s - mu2_h) / abs(mu2_ref),
        "surviving_signal_fraction": per_line, "depleted_fwhm_mhz": dep, "bare_fwhm_mhz": fwhm_mc,
        "depleted_width_convergence": {p: {"n_tau": dep[p], "halved": model_dep[p]} for p in th} if depletion_form == "mc" else {},
        "shares_shift_abs": shares_shift, "shares_thermal": th,
        "depletion_widening_rel": dep_fit, "depletion_fwhm_rel": dep_rel, "closed_form_bare_mhz": ref_bare, "z_ratio": zr,
        "depletion_note": "depletion_widening_rel is what a cusp FIT reads after the natural Lorentzian (the factor the fit carries); depletion_fwhm_rel is the surviving kernel's FWHM over the bare one, the core-flattening diagnostic",
        "shares_mc": mc_sh, "shares_model": md_sh,
        "approximation": "per-atom Gaussian pulse of the chord's own width; depletion reweights atoms and does not reshape the pulse",
        "joint_line_detail": {
            "s0_mhz": s0_mhz, "gamma_hom_mhz": gamma_hom_ref_mhz, "windows_mhz": list(JOINT_WINDOWS_MHZ),
            "orders": list(joint_orders), "n_path": int(joint_n_path), "n_sub": int(n_sub),
            "table_s0_grid": [0.0, s0_hi], "noise_condition": JOINT_NOISE_COND,
            "moment_dev_sigma": {f"mu{o}@{wdw:g}": joint_dev_sigma[(o, wdw)]
                                 for wdw in JOINT_WINDOWS_MHZ for o in joint_orders},
            "record_sd": {f"mu{o}@{wdw:g}": joint_sd[(o, wdw)] for wdw in JOINT_WINDOWS_MHZ for o in joint_orders},
            "note": "a random subsample of the node's own atoms' shift-and-transit pairing against "
                    "volume_line.JointTable, weak field, natural width only, no session term: what F290 named "
                    "as the kernel gate's own gap (the transit and the ramp validated separately, never their "
                    "joint). n_sub of n_atoms is the subsample actually drawn (n_path clipped to n_atoms)",
        },
        "seconds": time.time() - t0,
    }
    return readings, detail


def _task(args):
    (w0, m2, rho, T, P), kw = args
    r, d = run_node(w0, m2, rho, T, P, **kw)
    key = kernel_gate.node_key(w0, m2, rho, T, P)
    art = kernel_gate.record_node(key, r, detail=d)
    return key, json.loads(art.read_text())["verdict"], r, d


def _collect(rho: float) -> int:
    """The committed table: every reading of every validated node at one retro ratio, with the
    per-line depletion widening and the cycle counts, read from the artefacts under the current
    cache (or `RB5S6S_KERNEL_MC_DIR`). Reproduction on another machine is the grid first
    (`--grid`, minutes on eight workers) and then this; the producer is in the expensive set."""
    d = kernel_gate.mc_dir()
    rows, prov = [], set()
    for f in sorted(d.glob("*.json")):
        row = json.loads(f.read_text())
        node = row["detail"]["node"]
        if abs(float(node["rho"]) - rho) > 1e-9 or float(node["m2"]) != 1.0:
            continue
        key = row["key"]; v = row["verdict"]
        # PROVENANCE RIDES WITH EVERY ROW (2026-09-17): the artefact directory accumulates runs, and
        # a table that cannot say which model digest, atom count and seed a row came from cannot
        # announce a mixed population. One digest, one count and one seed per table, or refused.
        sha, n_at, seed, when = row.get("model_sha"), row["detail"].get("n_atoms"), row["detail"].get("seed"), row.get("when")
        prov.add((sha, n_at, seed))
        tail = [sha, n_at, seed, when]
        for name, val in row["readings"].items():
            rows.append([key, name, f"{val['mc']:.6g}", f"{val['model']:.6g}", "", v, "the Monte Carlo against the form the fit uses at this node", ""] + tail)
        for line, x in row["detail"]["depletion_widening_rel"].items():
            rows.append([key, f"depletion_widening_rel_{line}", f"{x:.6g}", "", "", v, "what a transit fit reads from the surviving kernel after the natural Lorentzian, over the bare one: the factor the fit carries", ""] + tail)
        for line, x in row["detail"].get("depletion_fwhm_rel", {}).items():
            rows.append([key, f"depletion_fwhm_rel_{line}", f"{x:.6g}", "", "", v, "the surviving transit kernel's FWHM over the bare collected kernel's, the core-flattening diagnostic", ""] + tail)
        rows.append([key, "shares_shift_abs", f"{row['detail'].get('shares_shift_abs', float('nan')):.6g}", "", "", v, "the largest move of a line's share from the thermal law to the depleted one: the physical shift", ""] + tail)
        rows.append([key, "cycles_on_axis", f"{row['detail']['cycles_on_axis']:.6g}", "", "", v, "excitation cycles on the central chord at the mean transverse speed", ""] + tail)
        rows.append([key, "cycles_mean_over_chords", f"{row['detail']['cycles_mean_over_chords']:.6g}", "", "", v, "the flux-weighted mean over every chord", ""] + tail)
    if len(prov) != 1:
        raise SystemExit(f"run_kernel_mc --collect: the artefacts at rho {rho} come from {len(prov)} (model digest, atoms, seed) populations {sorted(map(str, prov))}: re-run the grid so the table is one population")
    out = Path(os.environ.get("RB5S6S_RESULTS_DIR", str(_RESULTS_DIR))) / "kernel_mc.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["node", "quantity", "mc", "model", "unit", "verdict", "note", "status", "model_sha", "n_atoms", "seed", "written"]); w.writerows(rows)
    print(f"  wrote {out} ({len(rows)} rows from {len(rows) and len({r[0] for r in rows})} nodes at rho {rho})")
    return 0


def limit_check() -> int:
    """The two limits: window closed and drive weak, the sampler returns the closed-form cusp.

    ITS COST IS ITS PHYSICS, SO THE GATE RUNS IT (O59 F2, 2026-09-25): the tolerance below is the sampler's own
    noise at 100 000 atoms, so fewer atoms would stop it being the check, and inside the forty-second floor it was
    the one plant that could not be made cheaper. `tests/test_kernel_mc_limit.py` runs it under `--runslow`."""
    # THE CONTRACT BINDS THIS CALL TOO, AND THE DEVIATION IS DECLARED (F476, 2026-09-24): since F447 put
    # `guard_kernel_node` in `run_node`, this limit check raised ContractBreach on its atom count and its
    # beam, and nothing ran it, because the floor discovers plants under private/checks only.
    r, d = run_node(44.0, 1.0, 0.94, 130.0, 25.0, n_atoms=100_000, half_window_m=0.0,
                    beam_kind="gaussian",   # a CLOSED-FORM check, so the closed form's beam   # the window CLOSED: the transverse limit
                    mc_deviations={"n_atoms": "a closed-form limit check, not a validated node, needs fewer atoms",
                                   "beam_kind": "the closed form being checked is the Gaussian beam's own cusp",
                                   "half_window_m": "the closed form is the focal plane's transverse limit alone"})
    dev = abs(r["transit_fwhm_rel"]["mc"] - r["transit_fwhm_rel"]["model"]) / r["transit_fwhm_rel"]["model"]
    print(f"  closed window, 25 mW: FWHM mc {r['transit_fwhm_rel']['mc']:.4f} against the closed form "
          f"{r['transit_fwhm_rel']['model']:.4f} ({dev:.2%}); shape {r['transit_shape_rel']['mc']:.3g}; "
          f"ramp mu2 {r['ramp_mu2_rel']['mc']:.4f} / {r['ramp_mu2_rel']['model']:.4f}, "
          f"mu3 {r['ramp_mu3_rel']['mc']:.5f} / {r['ramp_mu3_rel']['model']:.5f}")
    ok = dev < 0.005 and r["transit_shape_rel"]["mc"] - 1.0 < 0.01 and abs(r["ramp_mu2_rel"]["weak_field_mc"] / r["ramp_mu2_rel"]["model"] - 1) < 0.01
    print("run_kernel_mc: limit check", "OK" if ok else "FAIL")
    return 0 if ok else 1


def _self_test() -> int:
    """The fast half, the floor's: the bare command line against the contract, and the joint-line identity."""
    # the contract is loaded HERE as run_node loads it: `_MC` is run_node's local, and the first form of
    # this plant named it at module scope, so it raised NameError and graded nothing (F476)
    _MC = _load_contract()
    _bare = _parser().parse_args([]).n_atoms
    if _MC is not None and _bare not in (None, _MC.kernel_contract()["n_atoms"]):
        print(f"run_kernel_mc: self-test FAIL -- a bare command line asks for {_bare} atoms against the "
              f"contract's {_MC.kernel_contract()['n_atoms']}, so every default node run is refused")
        return 1
    ok = True
    # THE JOINT-LINE PLANT (C6b, the merge's 5a): `_joint_line` claims to be `volume_line.joint_spectrum`'s
    # own per-atom recipe verbatim, run on the SAME sampler. Both halves of that claim are checked here,
    # against the real call path (not a helper), on atoms this test draws itself. FALSE-PASS DIRECTION: a
    # `_joint_line` that quietly drifted from `joint_spectrum` (a wrong constant, a dropped factor) would
    # read here as a mismatch and fail this test before it ever reached a node's readings.
    from rb5s6s.volume_line import GaussianBeam, joint_spectrum, sample_atoms
    # gaussian-limit: the joint-line plant compares two samplers on one ideal beam, a test of the sampler and not of the physics
    beam = GaussianBeam(44.0e-6, 1.0)
    aw, av, au, af = sample_atoms(np.random.default_rng(3), 500, beam, 130.0, 0.0)
    # `_sample` also returns each atom's impact parameter and axial position (the fold of 2026-09-25), which
    # `sample_atoms` does not, so the comparison reads its first four
    # the SAME beam on both sides: with no beam `_sample` builds the clipped beam whose focus is 44 um
    # (`_beam_for`), and a comparison of two samplers on two beams tests nothing about the samplers
    bw, bv, bu, bf, *_ = _sample(np.random.default_rng(3), 500, 44.0e-6, 1.0, 130.0, 0.0, beam=_GaussianBeam(44.0e-6, 1.0))
    same_atoms = np.allclose(aw, bw) and np.allclose(av, bv) and np.allclose(au, bu) and np.allclose(af, bf)
    nu_plant = np.linspace(-20.0, 20.0, 801)
    ref = joint_spectrum(S0_mhz=0.3, gamma_hom_mhz=0.0, beam=beam, T_C=130.0, half_window_m=0.0,
                         n_path=500, seed=3, delta_mhz=nu_plant)
    ref_n = ref / ref.max()
    mine = _joint_line(nu_plant, 0.3, 0.0, bw, bv, bu, bf)
    joint_ok = bool(same_atoms and np.allclose(mine, ref_n, atol=1e-10))
    print(f"  joint line plant: _sample matches volume_line.sample_atoms {same_atoms}, "
          f"_joint_line matches joint_spectrum (unbinned, same atoms and seed) {joint_ok}, "
          f"max abs diff {float(np.max(np.abs(mine - ref_n))):.2e}")
    ok = ok and joint_ok
    print("run_kernel_mc: self-test", "OK" if ok else "FAIL")
    return 0 if ok else 1


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--w0", type=float, default=round(K.W0_CENTRAL_M * 1e6, 2)); ap.add_argument("--m2", type=float, default=1.0)
    # SLICING, so a long node list runs in WAVES (owner order O50). This file is NOT in
    # `kernel_gate.model_population()` -- checked, 20 modules, none of them this script -- so these
    # arguments cost no digest move and re-open no node.
    ap.add_argument("--from", dest="slice_from", type=int, help="first node index of this wave")
    ap.add_argument("--n", dest="slice_n", type=int, help="how many nodes this wave runs")
    ap.add_argument("--dump", help="a file written when the wave ends, so the runner can resume")
    ap.add_argument("--beam", choices=("clipped", "gaussian"), default="clipped",
                    help="the drive beam at the chord; `gaussian` is the comparison arm (F368)")
    ap.add_argument("--rho", type=float, default=0.94); ap.add_argument("--T", type=float, default=130.0)
    ap.add_argument("--P", type=float, default=225.0)
    ap.add_argument("--grid", action="store_true", help="the treatment matrix's grid: GRID_W0_UM x the L's eight conditions")
    # THE DEFAULT IS THE CONTRACT'S, NOT A LITERAL (2026-09-24). This read `default=100_000` while
    # `run_node` defaulted to the contract's 400 000, so every node started from a bare command line was
    # REFUSED by `mc_contract.guard_kernel_node` -- the contract working, the default contradicting it.
    # None lets `run_node` read `kernel_contract()["n_atoms"]`, so the two can no longer disagree.
    ap.add_argument("--n-atoms", type=int, default=None); ap.add_argument("--cycles-model", type=float, default=0.0)
    ap.add_argument("--joint-n-path", type=int, default=JOINT_N_PATH,
                    help="atoms in the joint-line reading's own subsample AND its JointTable build, decoupled "
                         "from --n-atoms (the reading's own cost, C6b's merge item 5a)")
    ap.add_argument("--depletion-form", default="mc", choices=("mc", "none", "companion"),
                    help="the fit's form the reading is judged against: mc (the node's own factor, judged on convergence), none, companion")
    ap.add_argument("--rhos", default=None, help="a comma list of retro ratios for --grid (default the single --rho)")
    ap.add_argument("--window-mm", type=float, default=None, help="the collected half-window; default the record's own, z_ratio x z_R")
    ap.add_argument("--workers", type=int, default=1); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--nodes", default=None,
                    help="a text file of nodes to run, one 'w0_um m2 rho T_C P_mW' per line (# comments), for the "
                         "pooled re-run of every recorded node after a model edit (PLAN v2 Phase 1 step 5)")
    ap.add_argument("--out", default=None, help="a CSV of the readings per node (cache class)")
    ap.add_argument("--collect", action="store_true",
                    help="write results/kernel_mc.csv from the artefacts on disk at the record's retro ratio (no Monte Carlo is run): the committed readings")
    return ap


def main(argv=None) -> int:
    a = _parser().parse_args(argv)
    if a.self_test:
        return _self_test()
    if a.collect:
        return _collect(a.rho)
    kw = dict(n_atoms=a.n_atoms, beam_kind=a.beam, half_window_m=(None if a.window_mm is None else a.window_mm * 1e-3), cycles_model=a.cycles_model,
              seed=a.seed, depletion_form=a.depletion_form, joint_n_path=a.joint_n_path)
    rhos = [float(x) for x in a.rhos.split(",")] if a.rhos else [a.rho]
    if a.nodes:
        nodes = []
        for ln in open(a.nodes):
            if ln.strip() and not ln.lstrip().startswith("#"):
                w, m2, r, T, P = (float(x) for x in ln.split()[:5])
                nodes.append((w, m2, r, T, P))
        if a.slice_from is not None:
            nodes = nodes[a.slice_from:a.slice_from + (a.slice_n or len(nodes))]
            print(f"wave: nodes[{a.slice_from}:{a.slice_from + (a.slice_n or 0)}] = {len(nodes)} node(s)",
                  flush=True)
    else:
        nodes = ([(float(w), a.m2, r, T, P) for r in rhos for w in GRID_W0_UM for (T, P) in GRID_CONDITIONS] if a.grid
                 else [(a.w0, a.m2, a.rho, a.T, a.P)])
    jobs = [(n, kw) for n in nodes]
    # SUBMIT AND PRINT AS EACH NODE LANDS (the rule file: a progress line is not an instrument, and
    # `map` yields in task order): a grid stopped at minute thirteen had printed nothing and lost
    # every node, because the summary waited for the whole pool.
    rows, res = [], []
    def _emit(key, verdict, r, d):
        print(f"  {key}: {verdict}  transit {r['transit_fwhm_rel']['mc']:.4f}/{r['transit_fwhm_rel']['model']:.4f}  "
              f"shape {r['transit_shape_rel']['mc']:.3g}  mu2 {r['ramp_mu2_rel']['mc']:.4f}/{r['ramp_mu2_rel']['model']:.4f}  "
              f"mu3 {r['ramp_mu3_rel']['mc']:.5f}/{r['ramp_mu3_rel']['model']:.5f} (grid {r['ramp_mu3_rel']['grid_movement']:.2g})  "
              f"expo {r['amplitude_power_law_abs']['mc']:.3f}/{r['amplitude_power_law_abs']['model']:.3f}  "
              f"shares {r['shares_abs']['mc']:.4f}  line misfit {r['depleted_line_abs']['mc']:.1e} "
              f"({r['depleted_line_abs']['line']})  joint shape {r['joint_shape_abs']['mc']:.2e}  "
              f"joint moment {r['joint_moment_sigma_abs']['mc']:.3f} sd ({r['joint_moment_sigma_abs']['worst_at']})  "
              f"cycles axis {d['cycles_on_axis']:.4f} mean {d['cycles_mean_over_chords']:.4f}  {d['seconds']:.0f} s",
              flush=True)
        for name, val in r.items():
            rows.append([key, name, val["mc"], val["model"], verdict])
    if a.workers > 1 and len(jobs) > 1:
        with cf.ProcessPoolExecutor(max_workers=a.workers) as ex:
            futs = [ex.submit(_task, j) for j in jobs]
            for fut in cf.as_completed(futs):
                out = fut.result(); res.append(out); _emit(*out)
    else:
        for j in jobs:
            out = _task(j); res.append(out); _emit(*out)
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        with open(a.out, "w", newline="") as f:
            wr = csv.writer(f); wr.writerow(["node", "reading", "mc", "model", "verdict"]); wr.writerows(rows)
        print(f"  wrote {a.out} ({len(rows)} rows)")
    if a.dump:                       # the wave's own marker, so the runner can resume (O50)
        pathlib.Path(a.dump).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(a.dump).write_text(json.dumps(
            {"from": a.slice_from, "n": a.slice_n, "nodes": len(jobs)}, indent=1))
        print(f"  wave dump -> {a.dump}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
