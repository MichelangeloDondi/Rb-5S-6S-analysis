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

The seven readings of `kernel_gate.READINGS`, each the Monte Carlo against what
`fullmodel.full_profile` USES at the node, so a FAIL is a statement about the model at that
node and not about the sampler:

  transit_fwhm_rel      the flux-weighted kernel's FWHM against `constants.transit_fwhm_from_w0`
                        at w0 (what `run_ultra_joint.Cell` passes as `transit_fwhm`)
  transit_shape_rel     the kernel's shape against the two-sided exponential AT ITS OWN FWHM
  ramp_k2_rel, ramp_k3_rel   the rate-weighted instantaneous-shift distribution's cumulants, at the
                        node's saturation, against the model's ramp: since 2026-09-18 (F133, PLAN v2
                        Phase 1) `lineshape.saturated_ramp_density` at the node's own power, waist,
                        temperature and rho, mixed axially by `lineshape.ramp_mixture` at the node's
                        z_ratio (`ramp_mixture_moments`), which is what `run_ultra_joint.Cell` fits
                        with; the weak-field Monte Carlo is recorded beside them so a failure names
                        the saturation and not the sampling; k3 carries its grid movement
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
from rb5s6s._compat import trapezoid                                # noqa: E402
from rb5s6s.amplitudes import predicted_shares                      # noqa: E402
from rb5s6s.cascade import BRANCHING_F, amplitude_factor            # noqa: E402
from rb5s6s.platforms import PLATFORMS, excitation_rate_per_atom    # noqa: E402

B_CUT = 3.0                   # impact parameters out to three beam radii
TAIL_FRACTION = 0.20          # the mixture proposal's uniform component (F372)
B_CUT_CLIPPED = 8.0           # a clipped beam's rings fall as a POWER: 2.4e-4 of the two-photon
                              # weight sits past three radii against 2.3e-16 for a Gaussian, and
                              # 3 -> 8 moves mu3 by 0.66 per cent. 8.0 is `shift_density`'s own
                              # cut, so the model and the Monte Carlo now truncate ALIKE
TAU_EDGE = 3.0                # the chord in units of w/v, the wings carried
N_TAU = 41                    # points along the chord; the grid movement halves it
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
    # the ramp can: 4 per cent in k2 and five-fold in k3 (2026-09-16 night, F11).
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


def _cumulants(values, weights):
    wsum = weights.sum(); m = (weights * values).sum() / wsum
    d = values - m
    k2 = (weights * d ** 2).sum() / wsum; k3 = (weights * d ** 3).sum() / wsum
    return float(m), float(k2), float(k3)


def _ramp_reference(n=20001):
    s = np.linspace(0.0, 1.0, n); f = lineshape.stark_ramp(s, 1.0)
    return _cumulants(s, f)


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


def run_node(w0_um, m2, rho, T_C, P_mW, *, n_atoms=None, half_window_m=None,
             cycles_model=0.0, seed=0, n_tau=N_TAU, depletion_form="mc",
             beam_kind="clipped", mc_deviations=None):
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
    w, v, u_b, flux_len, b_imp, z_imp = _sample(rng, n_atoms, w0_m, m2, T_C,
                                                half_window_m, beam=beam)
    _bk = dict(beam=beam, b=b_imp, z0=z_imp)
    tab = _rate_table(P_W, w0_m, T_C, rho)
    ref_bare = K.transit_fwhm_from_w0(w0_m, T_C, isotope=87)
    # THE TRANSIT REFERENCE GAINS THE BEAM'S OWN AXIAL WIDTH (F374, 2026-09-23).
    # `transit_collection_factor` computes the rate-weighted mean of 1/w(z) for a beam that diverges as
    # w0 sqrt(1 + (z/z_R)^2); the bore-clipped beam does NOT, its depth of focus being about 1.55 times
    # that, so across the window it stays narrow while the model's beam opens up. The correction enters
    # as a RATIO of `effective_transit_radius` on the two beams and never as a replacement, because that
    # function carries its own 0.37 per cent offset against the closed form and a ratio of like for like
    # cancels it exactly. For a Gaussian beam the ratio is identically one, so this line is unchanged in
    # the limit -- the same standard the sampler's own change was held to.
    _rate_w = (lambda uu: _rate(*tab, P_W * uu))
    if zr > 0 and not isinstance(beam, _GaussianBeam):
        beam_transit_corr = (BF.effective_transit_radius(_GaussianBeam(w0_m, m2), half_window_m, rate=_rate_w)
                             / BF.effective_transit_radius(beam, half_window_m, rate=_rate_w))
    else:
        beam_transit_corr = 1.0
    ref_fwhm = ref_bare * ((FM.transit_collection_factor(w0_m, m2) * beam_transit_corr) if zr > 0 else 1.0)
    nu = np.linspace(0.0, 6.0 * ref_fwhm, 721)
    # --- the transit kernel, no depletion: the time-integrated rate weights each chord
    G, N1, dt, u = _chord(P_W, u_b, w, v, tab, n_tau, **_bk)
    sig0 = (G * dt).sum(axis=1) * flux_len
    L0 = _kernel(nu, sig0, w, v); fwhm_mc = _fwhm(nu, L0)
    cusp = lineshape.two_sided_exponential(nu, fwhm_mc); cusp = cusp / cusp[0]
    sel = nu <= 3.0 * fwhm_mc
    shape_dev = float(np.max(np.abs(L0[sel] - cusp[sel])))      # encoded below as 1 + dev against 1
    # --- the ramp: the rate-weighted instantaneous shift, saturated and weak-field, k3's grid movement
    Gw, _, _, _ = _chord(P_W, u_b, w, v, tab, n_tau, weak=True, **_bk)
    shift = +u                                                          # BLUE-sided (O27), units of S0
    wt_sat = (G * dt) * flux_len[:, None]; wt_weak = (Gw * dt) * flux_len[:, None]
    m_s, k2_s, k3_s = _cumulants(shift, wt_sat); m_w, k2_w, k3_w = _cumulants(shift, wt_weak)
    Gh, _, dth, uh = _chord(P_W, u_b, w, v, tab, (n_tau - 1) // 2 + 1, **_bk)
    # THE SAME SIDE AS THE FULL GRID, and it was not (2026-09-18). When the ramp's side was flipped
    # to blue (O27) line 210 above became `shift = +u` and this halved-grid twin kept `-uh`. k3 is
    # ODD, so the convergence check has been differencing k3 against MINUS ITSELF ever since, and
    # `grid_movement` read |2 k3| / |k3_ref| ~ 1.9 at every node instead of the movement. Measured on
    # w38.0_m1.00_r0.940_T130_P75: reported 1.92288 against |2 k3|/|k3_ref| = 1.92477, agreeing to
    # 0.1 per cent, so the true movement was the residue, 0.0019. k2 is EVEN and was immune, which is
    # why its own movement read 6e-6 and nothing looked odd. Nothing caught it because `judge` tested
    # that the field was PRESENT and never what it said.
    shift_h = +uh                                                       # BLUE-sided (O27), as above
    _, k2_h, k3_h = _cumulants(shift_h, (Gh * dth) * flux_len[:, None])
    # THE MODEL'S RAMP IS THE SATURATED DENSITY IN THE AXIAL MIXTURE (F133, 2026-09-18). Until this
    # day the reference was the weak-field law (`stark_ramp_axial_moments`), and every node with
    # P/w0^2 over 0.078 mW/um^2 failed k3 by 8 to 15 per cent (F131, F132): the Monte Carlo's chord
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
    m_ref, k2_ref, k3_ref = mm["mean"], mm["var"], mm["k3"]
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
    # the widths and cumulants are ratios in which the weight is flat, this one cell was not.
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
    readings = {
        "transit_fwhm_rel": {"mc": fwhm_mc, "model": ref_fwhm},
        "transit_shape_rel": {"mc": 1.0 + shape_dev, "model": 1.0},
        "ramp_k2_rel": {"mc": k2_s, "model": k2_ref, "weak_field_mc": k2_w},
        "ramp_k3_rel": {"mc": k3_s, "model": k3_ref, "weak_field_mc": k3_w,
                        "grid_movement": abs(k3_s - k3_h) / abs(k3_ref)},
        "amplitude_power_law_abs": {"mc": expo_mc, "model": expo_model},
        "shares_abs": {"mc": shares_dev, "model": 0.0},
        "depleted_line_abs": {"mc": dep_line_misfit, "model": 0.0, "line": worst_q,
                              "note": "the composed depleted line against the fit's form (the cusp at the bare width times the fitted ratio) composed the same way, peak-normalised"},
    }
    detail = {
        "node": dict(w0_um=w0_um, m2=m2, rho=rho, T_C=T_C, P_mW=P_mW), "n_atoms": n_atoms, "n_tau": n_tau,
        "half_window_m": half_window_m, "cycles_model": cycles_model, "seed": seed, "depletion_form": depletion_form,
        "beam_kind": beam_kind, "beam_note": beam_note, "beam_transit_corr": beam_transit_corr,
        "ramp_model_gaussian": {"mean": mm_gauss["mean"], "var": mm_gauss["var"], "k3": mm_gauss["k3"]},
        "beam_cost_rel": {k: (float(mm[k] / mm_gauss[k] - 1.0) if mm_gauss[k] else float("nan"))
                          for k in ("mean", "var", "k3")},
        "cycles_on_axis": cycles_axis, "cycles_mean_over_chords": cycles_mean,
        "ramp_mean": {"mc": m_s, "weak_field_mc": m_w, "model": m_ref},
        "ramp_k2_grid_movement": abs(k2_s - k2_h) / abs(k2_ref),
        "surviving_signal_fraction": per_line, "depleted_fwhm_mhz": dep, "bare_fwhm_mhz": fwhm_mc,
        "depleted_width_convergence": {p: {"n_tau": dep[p], "halved": model_dep[p]} for p in th} if depletion_form == "mc" else {},
        "shares_shift_abs": shares_shift, "shares_thermal": th,
        "depletion_widening_rel": dep_fit, "depletion_fwhm_rel": dep_rel, "closed_form_bare_mhz": ref_bare, "z_ratio": zr,
        "depletion_note": "depletion_widening_rel is what a cusp FIT reads after the natural Lorentzian (the factor the fit carries); depletion_fwhm_rel is the surviving kernel's FWHM over the bare one, the core-flattening diagnostic",
        "shares_mc": mc_sh, "shares_model": md_sh,
        "approximation": "per-atom Gaussian pulse of the chord's own width; depletion reweights atoms and does not reshape the pulse",
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


def _self_test() -> int:
    """The two limits: window closed and drive weak, the sampler returns the closed-form cusp."""
    # the contract is loaded HERE as run_node loads it: `_MC` is run_node's local, and the first form of
    # this plant named it at module scope, so it raised NameError and graded nothing (F476)
    _MC = _load_contract()
    _bare = _parser().parse_args([]).n_atoms
    if _MC is not None and _bare not in (None, _MC.kernel_contract()["n_atoms"]):
        print(f"run_kernel_mc: self-test FAIL -- a bare command line asks for {_bare} atoms against the "
              f"contract's {_MC.kernel_contract()['n_atoms']}, so every default node run is refused")
        return 1
    # THE CONTRACT BINDS THIS CALL TOO, AND THE DEVIATION IS DECLARED (F476, 2026-09-24): since F447 put
    # `guard_kernel_node` in `run_node`, this limit check raised ContractBreach on its atom count and its
    # beam, and nothing ran it, because the floor discovers plants under private/checks only.
    r, d = run_node(44.0, 1.0, 0.94, 130.0, 25.0, n_atoms=100_000, half_window_m=0.0,
                    beam_kind="gaussian",   # a CLOSED-FORM check, so the closed form's beam   # the window CLOSED: the transverse limit
                    mc_deviations={"n_atoms": "a closed-form limit check, not a validated node, needs fewer atoms",
                                   "beam_kind": "the closed form being checked is the Gaussian beam's own cusp"})
    dev = abs(r["transit_fwhm_rel"]["mc"] - r["transit_fwhm_rel"]["model"]) / r["transit_fwhm_rel"]["model"]
    print(f"  closed window, 25 mW: FWHM mc {r['transit_fwhm_rel']['mc']:.4f} against the closed form "
          f"{r['transit_fwhm_rel']['model']:.4f} ({dev:.2%}); shape {r['transit_shape_rel']['mc']:.3g}; "
          f"ramp k2 {r['ramp_k2_rel']['mc']:.4f} / {r['ramp_k2_rel']['model']:.4f}, "
          f"k3 {r['ramp_k3_rel']['mc']:.5f} / {r['ramp_k3_rel']['model']:.5f}")
    ok = dev < 0.005 and r["transit_shape_rel"]["mc"] - 1.0 < 0.01 and abs(r["ramp_k2_rel"]["weak_field_mc"] / r["ramp_k2_rel"]["model"] - 1) < 0.01
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
              seed=a.seed, depletion_form=a.depletion_form)
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
              f"shape {r['transit_shape_rel']['mc']:.3g}  k2 {r['ramp_k2_rel']['mc']:.4f}/{r['ramp_k2_rel']['model']:.4f}  "
              f"k3 {r['ramp_k3_rel']['mc']:.5f}/{r['ramp_k3_rel']['model']:.5f} (grid {r['ramp_k3_rel']['grid_movement']:.2g})  "
              f"expo {r['amplitude_power_law_abs']['mc']:.3f}/{r['amplitude_power_law_abs']['model']:.3f}  "
              f"shares {r['shares_abs']['mc']:.4f}  line misfit {r['depleted_line_abs']['mc']:.1e} "
              f"({r['depleted_line_abs']['line']})  cycles axis {d['cycles_on_axis']:.4f} mean {d['cycles_mean_over_chords']:.4f}  {d['seconds']:.0f} s",
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
