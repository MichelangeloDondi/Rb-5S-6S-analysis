"""The full-model Monte Carlo line: a per-atom FOUR-LEVEL optical-Bloch integration along
each atom's chord through a focused, retro-reflected beam.

WHY THIS EXISTS. Two incomplete models stand in the record. `rb5s6s.volume_line.joint_spectrum`
(the twin of record) carries each atom's CHIRPED crossing -- the light shift varies along the
trajectory -- but is weak-field: no saturation, no depletion, no F statistics, one homogeneous
width for every atom. `scripts/run_kernel_mc.py` carries saturation, the 5P cascade and the F
statistics, but an UNCHIRPED Gaussian pulse per atom (the light shift is frozen at the chord's
own peak, not followed along it). This module promotes the seed at
`private/cache/plan_2026-09-16/p18_saturated_node.py` (`bloch_line`, a closed two-level probe with
no cascade and a Gaussian chord) into a four-level, chirped, cascade-carrying line, generalising
its RK4-with-substepping recipe rather than restating it.

THE FOUR LEVELS, per atom, for the driven line: g (the ground hyperfine level the line starts
from), e (6S), p (5P, lumped over both fine-structure legs, weighted by their branching), d (the
OTHER ground hyperfine level, dark for this line -- the cascade's depletion target). 6S has no
allowed decay to 5S (`rb5s6s.cascade`'s own docstring), so e decays only into p; p decays into g
with probability b = 1 - BRANCHING_F[peak] and into d with probability 1 - b
(`rb5s6s.cascade.BRANCHING_F`). g and d are both part of the true 5S ground state and do not decay
on this timescale.

THE EQUATIONS, in the frame rotating at the two-photon drive. Only the g-e coherence is ever
driven (the drive is a scalar two-photon operator that cannot create p-anything or g-d coherence
from populations alone -- `rb5s6s.cascade`'s own "why populations and not a density matrix"
argument, carried one level down: nothing here builds a coherence the drive cannot create), so the
relevant state is six real numbers per atom per detuning: (u, v) the g-e coherence's quadratures
and (n_g, n_e, n_p, n_d) the four populations, generalising the seed's (U, V, W) with W = n_e - n_g
recovered in the seed's own closed two-level limit (n_g + n_e = 1):

    du/dt = -gamma_perp u - D(t) v
    dv/dt =  D(t) u - gamma_perp v - Om(t) (n_e - n_g)
    dn_e/dt =  (Om(t)/2) v - Gamma_e n_e
    dn_g/dt = -(Om(t)/2) v + b Gamma_p n_p
    dn_p/dt =  Gamma_e n_e - Gamma_p n_p
    dn_d/dt =  (1 - b) Gamma_p n_p

D(t) = 2 pi (delta_hz - sign S(t)), Om(t) = 2 pi Omega(t) (both angular, rad/s), gamma_perp =
Gamma_e/2 + pi * (sum of every extra FWHM contribution, Hz), Gamma_e = 2 pi GAMMA_NAT_HZ (6S
population decay), Gamma_p = 1/mean_5p_lifetime_s() (the branching-weighted lumped-5P population
decay, `rb5s6s.detection.mean_5p_lifetime_s`). `sign` is read once from `rb5s6s.lineshape.RAMP_SIDE`
and never restated (owner order O27). Initial condition: n_g(0) = (2F+1)/(2(2I+1)) (the line's own
thermal share, `rb5s6s.cascade.DRIVEN_F`), n_d(0) = 1 - n_g(0), n_e(0) = n_p(0) = u(0) = v(0) = 0.

THE DETECTED SIGNAL is the 5P decay's 795 nm (5P1/2) leg, `rb5s6s.detection.ir_branching_5p12()`
of every 5P decay (THEORY-ONLY, no measurement exists -- that module's own caveat, carried here
unchanged: this is the assumption named in the task, not a fact this module adds), integrated over
the atom's time in the beam and weighted by its crossing flux:

    signal(delta) = sum_atoms flux_i * Gamma_p * ir_branching_5p12() * integral n_p_i(t; delta) dt

THREE REPAIRS OF V6.1 (2026-09-25, the model's check against its own named fixes, F543), each a `**numerics` switch whose old value is kept
bit for bit as the comparison arm:

  THE CHORD. `chord="auto"` (the default) reads a clipped beam along each atom's TRUE chord,
  u(sqrt(b^2 + (w tau)^2), z), from the atom's own impact parameter and axial position
  (`sample_atoms(return_geometry=True)`), as `volume_line.joint_spectrum(chord="beam")` does; a
  `GaussianBeam` keeps the Gaussian chord, which is exact for it. `chord="gaussian"` forces the old
  shared envelope u_b exp(-2 tau^2) on every atom, the rank-one substitution F538 measured at 0.59 to
  0.77 of the alpha signal on the joint line.
  THE RETURNING BEAM AT EACH ATOM'S OWN z. `retro_axial="own_z"` (the default) reads the returning beam
  where the atom actually crosses; `"focal"` is the old reading at z = 0 with the impact parameter
  inverted from u_b, exact only in the focal plane while the collected window reaches 0.6 z_R.
  THE RETURNING BEAM IS THE FORWARD FIELD IMAGED. Lens 8 and its mirror image the forward focus back,
  displaced along the beam by `retro_focus_offset_m` (Delta = 2 delta + 2 z_R^2 (f - d)/f^2, positive toward the lens,
  the owner's lens-8 hypothesis as a term, registry `retro_focus_offset`). `retro_kind="imaged"` (the
  default) takes the returning intensity as the forward beam's own, clipped profile mirrored about
  Delta, u_ret(b, z) = u_fwd(b, Delta - z), AND its phase: the two wavefronts' curvatures no longer cancel off
  axis, so each chord at depth z carries the Doppler chirp k C(z) v x, C = z/(z^2 + z_R^2) + (Delta - z)/((Delta - z)^2
  + z_R^2), the embedded Gaussian's wavefront at the actual focus (F547; the bore's
  own diffraction on the phase is not carried). `retro_curvature="off"` keeps the intensity half alone, the study arm.
  ONE PART OF THE DISPLACED RETURN IS STILL OWED: the weak lens also changes the returning waist, by a few per cent at
  a returning focus one Rayleigh length away and more beyond it (first order in delta (d - f)/f^2, so larger for a
  mirror nearer the lens). `retro_kind="gaussian"` is the old Gaussian return of waist
  `retro_waist_ratio` w0, which an imaged return cannot have. And an atom dropped for its step count
  is budgeted: the dropped flux fraction above `dropped_flux_budget` (1e-3) is refused.

THE REGISTRY'S DOOR (O58). `full_line` names its `consumer` ("twin" or "mc") and refuses before its
first atom unless the terms it will execute, read off its knobs as registry ids
(`registry_terms`), are that path's registry model, or the call is a declared study whose `registry`
reason, six words or more, covers every term it drops or adds (`model_registry.preflight`).

EVERY TERM BELOW IS A KNOB IN `terms` (a dict of strengths; 0 means off unless stated otherwise),
and every term applied with a non-zero strength is named in the returned `executed` set. No
registry module is imported here; `executed` is a plain set for a future registry to read.

  1  chirp             the local light shift S(t) follows the local intensity along the chord
                        (on by default; off freezes each arm's shift at its average along that
                        atom's own chord against the drive's rate weight Om^2, which leaves the
                        weak-field centroid where the chirped line puts it, so the arm moves only
                        what the chirp moves; F547).
  2  saturation        the drive at its true local Rabi frequency Om(t) (on by default; off
                        rescales Om down by 1e2 and renormalises the returned line by 1e4, the
                        seed's own weak-field convention, so the two limits are comparable in
                        amplitude).
  3  cascade_F         the 5P branching into the dark level d (on by default; off sets b = 1, no
                        depletion, F-independent).
  4  retro_geometry    the forward and return beams as two separate fields (on by default; the
                        return beam's own waist ratio, transverse offset and the physical
                        constants are `retro_waist_ratio` and `retro_offset_w0`, keyword
                        arguments and not part of `terms`, defaults 1.0 and 0.0 -- a MATCHED
                        return beam, which is mathematically identical to the term being off, so
                        validation (a) turns it off only to skip the extra arithmetic). Local
                        Rabi frequency goes as sqrt(I_fwd(t) I_ret(t)), local light shift as their
                        sum (the k-sum-zero and the fringe-mean combinations of
                        `hyperpolarizability.two_photon_rabi_hz`'s own docstring, applied locally
                        rather than to one on-axis number).
  5  collisions_speed  each atom's own collisional width gamma_c(v) = beta_self N f(v) and red
                        shift -gamma_c(v) * SHIFT_OVER_HWHM / 2 (Lewis 1980's n = 6 law via
                        `vanderwaals.impact_prefactors()["shift_over_hwhm"]` = tan(pi/5), the
                        precise form of the task's stated ~1/2.75; off means one width for every
                        atom (the ensemble mean) and no shift.
  6  exchange_by_line  a per-line FACTOR on beta_self (default 1.0 for every line; the value,
                        not a switch, is the input -- passing 0.0 removes the collisional term
                        for that line entirely, which is the sense in which it is "off").
  7  laser             a Lorentzian part (`gamma_laser_l_mhz`) added into gamma_perp and a
                        Gaussian part (`sigma_laser_mhz`) convolved into the RETURNED line after
                        the ensemble sum, exactly as `volume_line.joint_spectrum` applies its
                        homogeneous widths (Wiener-Khinchin: a width common to every atom
                        commutes with the ensemble sum).
  8  foreign_gas       a constant Lorentzian `gamma_foreign_mhz` added into gamma_perp.
  9  retro_tilt        a residual first-order Doppler detuning k_drive * theta * v_x per atom,
                        `retro_tilt_theta_rad` the residual forward/return pointing angle;
                        v_x is drawn fresh (see the module's own caveat below).
 10  kerr_depletion    local intensity envelope multiplied by (1 - kerr_depletion_frac * u(t)):
                        EVEN in detuning (depends only on the local intensity itself).
 11  kerr_lens         an ODD-in-detuning addition to the local shift,
                        kerr_lens_frac * delta_mhz * u(t): a schematic dispersive placeholder
                        (the task names the required symmetry, not a closed form; see this
                        module's own report for what is NOT validated here).

DELTA-ALPHA ENTERS ONLY THROUGH THE LIGHT SHIFT (the thesis side's check of plan v6, 2026-09-25).
`delta_alpha_au` (a `**numerics` override of `constants.DELTA_ALPHA_AU`) multiplies ONLY the
shift-conversion constant `_CONV_S_MHZ_PER_WM2` below; the Rabi frequency, the saturation
parameter, the cascade rate table and every width in this module are driven from the INTENSITY
(`P_W`, `intensity_scale`, `w0_m`) directly, through `hyperpolarizability.two_photon_rabi_hz` and
the local-intensity envelopes, and never from the local shift as a proxy for it. This is the
opposite convention from `rb5s6s.stark.companion_gamma_mhz`, which DOES take the light shift `s0`
and multiplies by a fixed ratio (`COMPANIONS["ratio"]`, 1.2511) to stand in for the Rabi frequency
-- the shortcut this module's docstring was asked to confirm it does not take. `intensity_scale`
(default 1.0) is a separate knob, an overall multiplier on the intensity actually delivered at the
atoms, applied identically to the shift and the Rabi/saturation/cascade side, so a caller wanting
d(moment)/d(ln delta_alpha) at FIXED intensity varies `delta_alpha_au` alone, and a caller wanting
the intensity dependence at fixed delta_alpha varies `intensity_scale` alone.

THE PER-ATOM COLLISIONAL CORRELATION (`collisions_speed`) IS AN APPROXIMATION OF THE THESIS
SESSION'S OWN, STATED AS SUCH. The independent check at
`private/cache/plan_2026-09-25/s1_check/s1.py` (probe f9fa300d) correlates a radiator's transit
width with its collisional shift through the SAME atom's full 3D speed v and its angle to the beam
(v_perp = v sin(theta) sets the transit, f(v) the perturber-averaged v^0.6 sets the shift). This
module instead reuses `volume_line.sample_atoms`'s own transverse speed `v` (already drawn for the
transit) as the radiator speed in `f(v) = v**0.6 / <v**0.6>_population`, where the population
average is taken under `sample_atoms`'s OWN half-normal law for `v`, not the full 3D
Maxwell-Boltzmann speed s1.py integrates over. This reproduces a genuine, non-zero
transit-collisional correlation from the SAME per-atom variable rather than two independent draws,
but it is a coarser one-speed treatment than s1.py's (radiator speed, angle) pair, and the two are
compared, not reconciled, in this module's own tests and report.
"""
from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import numpy as np

from . import constants as K
from ._compat import trapezoid
from .beam_field import ClippedBeam
from .cascade import BRANCHING_F, DRIVEN_F
from .moments import windowed_moments  # noqa: F401  (re-exported for callers/tests)
from .density import number_density_cm3
from .detection import ir_branching_5p12, mean_5p_lifetime_s
from .hyperpolarizability import two_photon_matrix_element, two_photon_rabi_hz
from .lineshape import RAMP_SIDE, aperture_onaxis_factor_actual, gaussian as _gaussian_kernel, \
    stark_shift_S0_mhz
from .vanderwaals import beta_self_anchored, impact_prefactors
from .volume_line import GaussianBeam, sample_atoms
from . import model_registry as _MR

__all__ = ["full_line", "DEFAULT_TERMS", "TERM_NAMES", "registry_terms"]

# ---------------------------------------------------------------------------------------------
# term registry (a plain set of names; no registry module is imported)
# ---------------------------------------------------------------------------------------------
TERM_NAMES = (
    "chirp", "saturation", "cascade_F", "retro_geometry", "collisions_speed",
    "exchange_by_line", "laser", "foreign_gas", "retro_tilt", "kerr_depletion", "kerr_lens",
)

#: The "full model" defaults: the six mechanisms named as part of the core physics are ON, the
#: five extra nuisances (laser, foreign gas, retro tilt, the two Kerr placeholders) are OFF, so a
#: caller who wants the plain full model passes no `terms` at all. `exchange_by_line` is a FACTOR
#: (default 1.0), every other entry a strength in [0, whatever the physics needs].
DEFAULT_TERMS: Dict[str, float] = {
    "chirp": 1.0, "saturation": 1.0, "cascade_F": 1.0, "retro_geometry": 1.0,
    "collisions_speed": 1.0, "exchange_by_line": 1.0,
    "laser": 0.0, "foreign_gas": 0.0, "retro_tilt": 0.0,
    "kerr_depletion": 0.0, "kerr_lens": 0.0,
}

_G_ISO = {"87Rb": 8, "85Rb": 12}          # 2*(2I+1): ground-manifold sublevel counts
_SHIFT_OVER_HWHM = impact_prefactors()["shift_over_hwhm"]   # tan(pi/5), DERIVED (vanderwaals.py)

_F_TABLE_CACHE: Dict[Tuple[float, float], Tuple[np.ndarray, np.ndarray]] = {}


def _perturber_averaged_f_table(T_K: float, m_kg: float, n_v: int = 48, n_mu: int = 32,
                                vmax_sigma: float = 8.0, n_grid: int = 96
                                ) -> Tuple[np.ndarray, np.ndarray]:
    """(v_grid, F) for the collisional width's speed factor: F(v) = <v_rel^0.6>(v) /
    <v_rel^0.6>_ensemble, the RADIATOR's full 3D speed `v` perturber-averaged over an isotropic
    Maxwellian at the same T (Lewis 1980's n=6 law feeds on the RELATIVE speed, not the radiator's
    own), reproducing `private/cache/plan_2026-09-25/s1_check/s1.py`'s own `velocity_grid`
    construction (probe f9fa300d) via the same 2D Gauss-Legendre quadrature over the perturber's
    own (speed, angle-to-radiator), cached per (T_K, m_kg) since it does not depend on P_W, w0_m
    or the detuning grid.

    FIXED HERE (2026-09-25, the thesis side's S1 check): the module's first version used
    `v**0.6` of the RADIATOR's own speed alone as this factor, silently treating the relative
    speed as if the perturber had no independent thermal motion. Averaging over an isotropic
    perturber SMOOTHS the v-dependence sharply (measured: this repository's own construction had
    46.6 per cent population spread against s1.py's 12.41 per cent, a factor of 3.75), and a third
    moment goes as spread^3, so 3.75^3 = 52.7 against the measured 53.4-to-56.1 factor the S1
    check found -- the whole discrepancy, to within a few per cent, was this one omission.
    """
    key = (round(float(T_K), 6), round(float(m_kg), 20))
    cached = _F_TABLE_CACHE.get(key)
    if cached is not None:
        return cached
    sigma = math.sqrt(K.K_B_J_PER_K * T_K / m_kg)
    vmax = vmax_sigma * sigma
    v_grid = np.linspace(1e-6 * sigma, vmax, n_grid)
    v2n, v2w = np.polynomial.legendre.leggauss(n_v)
    v2n = 0.5 * vmax * (v2n + 1.0)
    v2w = 0.5 * vmax * v2w
    mun, muw = np.polynomial.legendre.leggauss(n_mu)
    p_v2 = (4.0 * np.pi * v2n ** 2 * (2.0 * np.pi * sigma ** 2) ** -1.5
           * np.exp(-v2n ** 2 / (2.0 * sigma ** 2)))
    V1 = v_grid[:, None, None]
    V2 = v2n[None, :, None]
    MU = mun[None, None, :]
    rel2 = np.clip(V1 ** 2 + V2 ** 2 - 2.0 * V1 * V2 * MU, 0.0, None)
    vrel_pow = rel2 ** 0.3                                   # (v_rel^2)^0.3 = v_rel^0.6
    inner = np.sum(vrel_pow * (muw[None, None, :] / 2.0), axis=2)     # integrate perturber angle
    F_raw = np.sum(inner * (v2w * p_v2)[None, :], axis=1)             # integrate perturber speed
    # normalise to the RADIATOR's own density-weighted (Maxwell, not flux) ensemble average, the
    # convention `vanderwaals.speed_average_factor`/`beta_self_anchored` already calibrate beta_self
    # in (s1.py's own point (c): population sums are density-weighted, never flux-weighted)
    p_v1 = (4.0 * np.pi * v_grid ** 2 * (2.0 * np.pi * sigma ** 2) ** -1.5
           * np.exp(-v_grid ** 2 / (2.0 * sigma ** 2)))
    dv = np.gradient(v_grid)
    ens_avg = float(np.sum(F_raw * p_v1 * dv) / np.sum(p_v1 * dv))
    F = F_raw / ens_avg
    _F_TABLE_CACHE[key] = (v_grid, F)
    return v_grid, F

#: One arm's on-axis intensity per recorded watt, and the light-shift conversion constant, both
#: independent of `delta_alpha_au` except where the constant itself is named -- see the module
#: docstring's "delta-alpha enters only through the light shift".
from .hyperpolarizability import ATOMIC_FIELD_V_PER_M as _ATOMIC_FIELD_V_PER_M  # noqa: E402  (one home for the constant)


def _conv_s_mhz_per_wm2(delta_alpha_au: float) -> float:
    return (abs(float(delta_alpha_au)) * K.ATOMIC_POLARIZABILITY_SI
            / (2.0 * K.EPS0_F_PER_M * K.C_M_PER_S * K.H_PLANCK_JS) / 1e6)


# ---------------------------------------------------------------------------------------------
# beam construction: the real, bore-clipped beam by default (F417's rule), a plain Gaussian for
# validation against volume_line.joint_spectrum, which knows no bore.
# ---------------------------------------------------------------------------------------------
_W_IN_LO_M, _W_IN_HI_M = 0.50e-3, 14.0e-3


class _ClampedClippedBeam:
    """`ClippedBeam` with every call clamped, because `volume_line.sample_atoms` calls `beam.w`
    and `beam.u` with no `clamp` keyword at all (F418's own repair in `p18_beam.py`, reproduced
    here rather than imported, so this module depends only on `rb5s6s.*`)."""

    def __init__(self, inner: ClippedBeam):
        self._b = inner

    def w(self, z_m, clamp=False):
        return self._b.w(z_m, clamp=True)

    def u(self, r_m, z_m, clamp=False):
        return np.clip(np.asarray(self._b.u(r_m, z_m, clamp=True), float), 0.0, None)

    def __getattr__(self, name):
        return getattr(self._b, name)


def _beam_for_actual_focus(w0_m: float, m2: float) -> Tuple[object, str]:
    """(beam, note): a `ClippedBeam` whose actual focus is `w0_m`, by bisection on the input
    radius through the fixed EOM bore (the same recipe as `scripts/run_kernel_mc.py::_beam_for`
    and `private/cache/plan_2026-09-16/p18_beam.py`, reproduced rather than cross-imported so this
    module has no dependency outside `rb5s6s`). Falls back to a plain `GaussianBeam` WITH A NOTE
    when `w0_m` sits below this bore's diffraction floor or above what any clipped input makes."""
    try:
        f_lo = float(ClippedBeam(w_in_m=_W_IN_LO_M, m2=m2).actual_focus_m())
        f_hi = float(ClippedBeam(w_in_m=_W_IN_HI_M, m2=m2).actual_focus_m())
    except Exception as exc:  # an M2 the propagated field cannot carry
        # gaussian-limit: the propagated field refused this node, stated in the note
        return GaussianBeam(w0_m, m2), f"gaussian: the propagated field refused this node ({exc})"
    if not (f_hi <= w0_m <= f_lo):
        side = "below the bore's floor" if w0_m < f_hi else "wider than any clipped input produces"
        # gaussian-limit: a waist below the bore's floor, stated in the returned note
        return (GaussianBeam(w0_m, m2),
                f"gaussian: {w0_m * 1e6:.2f} um is {side} ({f_hi * 1e6:.2f} to {f_lo * 1e6:.2f} um)")
    lo, hi = _W_IN_LO_M, _W_IN_HI_M
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if float(ClippedBeam(w_in_m=mid, m2=m2).actual_focus_m()) > w0_m:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-9:
            break
    w_in = 0.5 * (lo + hi)
    beam = ClippedBeam(w_in_m=w_in, m2=m2)
    return beam, f"clipped: w_in {w_in * 1e3:.4f} mm gives focus {beam.actual_focus_m() * 1e6:.3f} um"


def _make_beam(w0_m: float, m2: float, window_beam: str) -> Tuple[object, float, str]:
    """(beam, aperture_on_axis_factor, note). `aperture_on_axis_factor` is
    `lineshape.aperture_onaxis_factor_actual` for a clipped beam (F280's correction: the real
    on-axis intensity per watt at a given ACTUAL focus is below an ideal Gaussian's), 1.0 for a
    plain Gaussian, which has no such correction."""
    if window_beam == "gaussian":
        # gaussian-limit: the caller asked for the ideal beam, validation against joint_spectrum
        return GaussianBeam(w0_m, m2), 1.0, "gaussian: asked for explicitly"
    if window_beam != "clipped":
        raise ValueError(f"window_beam={window_beam!r} is neither 'clipped' nor 'gaussian'")
    beam, note = _beam_for_actual_focus(w0_m, m2)
    if isinstance(beam, GaussianBeam):
        return beam, 1.0, note
    ap = float(aperture_onaxis_factor_actual(w0_m, clamp_floor=True))
    return _ClampedClippedBeam(beam), ap, note


def _thermal_share(peak: str) -> Tuple[float, int]:
    """(f_g, isotope): the driven ground level's thermal population share (2F+1)/(2(2I+1)),
    `cascade.DRIVEN_F`'s own (isotope, F), and the isotope as an int for `sample_atoms`."""
    iso_s, F = DRIVEN_F[peak]
    iso = int(iso_s[:2])
    return (2 * F + 1) / _G_ISO[iso_s], iso


def _frozen_means(env_f, env_r, tt):
    """Each arm's envelope frozen for `chirp` off: its average along the chord against the drive's rate weight.

    The two-photon drive goes as Om ~ sqrt(I_f I_r) with the returning beam and as I_f without it, so the
    excitation's weight along a chord is Om^2 ~ e_f e_r, or e_f^2. The weak-field line's centroid is the
    Om^2-weighted mean of the instantaneous shift, so freezing each arm at <e>_{Om^2} keeps that centroid and
    leaves the chirp's own reach, the higher moments. The uniform average over [-tau_edge, tau_edge] this replaces
    scaled as 1/tau_edge and read 0.157 of u_b S0 at tau_edge 4 against the centroid's 0.8165 on a Gaussian chord
    (F547, 2026-09-25). Returns (mean_f, mean_r), each (nb, 1) or (1, 1), mean_r None
    without a returning beam."""
    # AN ATOM THE DRIVE NEVER REACHES HAS NO WEIGHT, AND ITS FROZEN SHIFT IS ZERO (V7.1, 2026-09-26): the weight's
    # integral vanishes for an atom outside the returning beam, 0/0 read NaN there, and one NaN atom made every
    # chirp-off line of V7.2's budget NaN at every detuning. Such an atom carries no drive, so the value is immaterial.
    def _ratio(num, den):
        out = np.zeros_like(num)
        return np.divide(num, den, out=out, where=den > 0.0)

    ef = np.atleast_2d(np.asarray(env_f, float))
    if env_r is None:
        wgt = ef * ef
        return _ratio(trapezoid(ef * wgt, tt, axis=-1), trapezoid(wgt, tt, axis=-1))[:, None], None
    er = np.atleast_2d(np.asarray(env_r, float))
    wgt = ef * er
    den = trapezoid(wgt, tt, axis=-1)
    return (_ratio(trapezoid(ef * wgt, tt, axis=-1), den)[:, None],
            _ratio(trapezoid(er * wgt, tt, axis=-1), den)[:, None])


def registry_terms(t: Dict[str, float], *, clipped: bool, half_window_m: float, s0_mhz: float,
                   retro_kind: str, retro_axial: str, retro_waist_ratio: float, retro_offset_w0: float,
                   sigma_laser_mhz: float, gamma_laser_l_mhz: float, gamma_foreign_mhz: float,
                   retro_tilt_theta_rad: float, kerr_depletion_frac: float, kerr_lens_frac: float) -> set:
    """The registry term ids (`rb5s6s.model_registry`) a configured `full_line` WILL execute, read off its
    knobs before any atom is drawn. A term applied at a trivial value (M2 = 1, Delta = 0) still counts,
    because the construction applies it; a switch at zero strength does not."""
    on = {k: abs(float(v)) > 0.0 for k, v in t.items()}
    ex = {"natural_width", "transit", "beam_quality_m2"}
    if half_window_m > 0.0:
        ex.add("axial_collection_window")
    if s0_mhz > 0.0:
        ex.add("ac_stark_ramp")
        if on["chirp"]:
            ex.add("transit_chirp")
    if clipped:
        ex.add("bore_clipping")
    if on["saturation"]:
        ex |= {"saturation", "companion_pull_reduction"}
    if on["cascade_F"]:
        ex |= {"depletion_cascade", "hyperfine_pumping"}
    if on["collisions_speed"]:
        ex |= {"self_broadening_vdw", "speed_dependent_collisional_width", "speed_dependent_collisional_shift",
               "collisional_shift"}
    elif on["exchange_by_line"]:
        ex.add("self_broadening_vdw")
    if on["laser"] and (sigma_laser_mhz > 0.0 or gamma_laser_l_mhz > 0.0):
        ex.add("laser_kernel")
    if on["foreign_gas"] and gamma_foreign_mhz > 0.0:
        ex.add("foreign_gas")
    if on["retro_tilt"] and retro_tilt_theta_rad != 0.0:
        ex.add("retro_tilt")
    if on["kerr_depletion"] and kerr_depletion_frac > 0.0:
        ex.add("two_photon_absorption")
    if on["kerr_lens"] and kerr_lens_frac != 0.0:
        ex.add("kerr_lens")
    if on["retro_geometry"]:
        if retro_kind == "gaussian" and retro_waist_ratio != 1.0:
            ex.add("retro_mismatch")
        if retro_offset_w0 != 0.0:
            ex.add("retro_offset")
        if retro_axial == "own_z":
            ex.add("retro_focus_offset")
    return ex


# ---------------------------------------------------------------------------------------------
# the public entry point
# ---------------------------------------------------------------------------------------------
def full_line(delta_mhz, *, peak: str, P_W: float, T_C: float, w0_m: float, M2: float = 1.0,
             rho: float = 0.94, n_path: int = 4000, seed: int = 0,
             terms: Optional[Dict[str, float]] = None, window_beam: str = "clipped",
             intensity_scale: float = 1.0, consumer: Optional[str] = None,
             registry: Optional[str] = None, **numerics):
    """The flux-weighted detected 795 nm signal per detuning, plus a dict of what ran.

    Required: `peak` (one of `constants.PEAKS`, e.g. "4192"), `P_W` (forward-arm recorded power,
    W), `T_C` (cell temperature, C), `w0_m` (actual focal 1/e^2 radius, m -- NOT an input radius).
    `M2 >= 1`, `rho` the retro power ratio, `n_path` the atom count, `seed` the RNG seed.
    `terms` overrides `DEFAULT_TERMS` by name (unknown keys raise). `window_beam` selects the
    forward beam's own construction: "clipped" (default, F417's rule) or "gaussian" (validation
    (a) against `volume_line.joint_spectrum`, which has no bore). `intensity_scale` multiplies the
    intensity actually delivered at the atoms, independent of `delta_alpha_au` (module docstring).

    `**numerics` (all optional): `n_tau` (301), `tau_edge` (4.0), `batch` (256), `max_sub` (40),
    `delta_alpha_au` (`constants.DELTA_ALPHA_AU`), `sigma_laser_mhz` (0.0, Gaussian, post-sum),
    `gamma_laser_l_mhz` (0.0, Lorentzian, in gamma_perp), `gamma_foreign_mhz` (0.0),
    `retro_waist_ratio` (1.0), `retro_offset_w0` (0.0), `retro_tilt_theta_rad` (0.0),
    `kerr_depletion_frac` (0.0), `kerr_lens_frac` (0.0), `isotope` (overrides the peak's own),
    and V6.1's `chord` ("auto"), `retro_kind` ("imaged"), `retro_axial` ("own_z"),
    `retro_focus_offset_m` (0.0), `retro_curvature` ("on") and `dropped_flux_budget` (1e-3), module docstring.

    `consumer` ("twin" or "mc", required) and `registry` (None, or a study's reason of six words or more)
    are the registry's door (module docstring): nothing is drawn before it admits.

    Returns `(signal, info)`. `signal` has one entry per `delta_mhz`, unnormalised (an overall
    constant does not move a windowed central moment). `info` carries `executed` (the set of terms
    applied at non-zero strength), `dropped_flux_frac`, `beam_note`, `n_atoms_used`, `S0_ref_mhz`,
    `Om0_ref_hz`, `gamma_perp_floor_mhz`, and the resolved numerics.
    """
    t = dict(DEFAULT_TERMS)
    if terms:
        unknown = set(terms) - set(TERM_NAMES)
        if unknown:
            raise ValueError(f"full_line: terms has unknown keys {sorted(unknown)}")
        t.update({k: float(v) for k, v in terms.items()})

    n_tau = int(numerics.get("n_tau", 301))
    # SPEED (thesis side, 2026-09-25): the RK4 total step count is `rate_bound * 2*tau_edge *
    # (w/v)`, independent of n_tau (a coarser outer tau grid gets a proportionally larger n_sub,
    # so the product is fixed) -- measured by profiling, not assumed. `rate_bound` is dominated by
    # the WIDEST |detuning| asked for (2.6x the next-largest term at the 2025 corner), which the
    # physics needs; `tau_edge` is a pure NUMERICAL truncation of the chord's own Gaussian envelope
    # exp(-2 tau^2), negligible at tau_edge=4 (1.3e-14 of the tau=0 value, far below floating-point
    # noise) where the previous default of 6 (2.3e-31) bought accuracy nobody could measure. This
    # is a `WAVE_CAP_S`-safe reduction in unused range, not a physics change: tests (a), (b), (c),
    # (e) are re-run against it, and their published numbers move only within their own reported
    # tolerance.
    tau_edge = float(numerics.get("tau_edge", 4.0))
    batch = int(numerics.get("batch", 256))
    max_sub = int(numerics.get("max_sub", 40))
    delta_alpha_au = float(numerics.get("delta_alpha_au", K.DELTA_ALPHA_AU))
    sigma_laser_mhz = float(numerics.get("sigma_laser_mhz", 0.0))
    gamma_laser_l_mhz = float(numerics.get("gamma_laser_l_mhz", 0.0))
    gamma_foreign_mhz = float(numerics.get("gamma_foreign_mhz", 0.0))
    retro_waist_ratio = float(numerics.get("retro_waist_ratio", 1.0))
    retro_offset_w0 = float(numerics.get("retro_offset_w0", 0.0))
    retro_tilt_theta_rad = float(numerics.get("retro_tilt_theta_rad", 0.0))
    kerr_depletion_frac = float(numerics.get("kerr_depletion_frac", 0.0))
    kerr_lens_frac = float(numerics.get("kerr_lens_frac", 0.0))
    chord = str(numerics.get("chord", "auto"))
    retro_kind = str(numerics.get("retro_kind", "imaged"))
    retro_axial = str(numerics.get("retro_axial", "own_z"))
    retro_focus_offset_m = float(numerics.get("retro_focus_offset_m", 0.0))
    retro_curvature = str(numerics.get("retro_curvature", "on"))
    if retro_curvature not in ("on", "off"):
        raise ValueError(f"full_line: retro_curvature is 'on' or 'off', not {retro_curvature!r}")
    dropped_flux_budget = float(numerics.get("dropped_flux_budget", 1e-3))
    if chord not in ("auto", "gaussian", "beam"):
        raise ValueError(f"full_line: chord={chord!r} is not 'auto', 'gaussian' or 'beam'")
    if retro_kind not in ("imaged", "gaussian"):
        raise ValueError(f"full_line: retro_kind={retro_kind!r} is not 'imaged' or 'gaussian'")
    if retro_axial not in ("own_z", "focal"):
        raise ValueError(f"full_line: retro_axial={retro_axial!r} is not 'own_z' or 'focal'")
    if retro_kind == "imaged" and retro_waist_ratio != 1.0:
        raise ValueError("full_line: an imaged return carries the forward beam's own size, so a "
                         f"retro_waist_ratio of {retro_waist_ratio} needs retro_kind='gaussian'")
    if retro_axial == "focal" and (retro_kind != "gaussian" or retro_focus_offset_m != 0.0):
        raise ValueError("full_line: retro_axial='focal' is the old Gaussian return read at z = 0, which "
                         "has no displaced focus: it needs retro_kind='gaussian' and retro_focus_offset_m=0")
    if consumer not in ("twin", "mc"):
        raise ValueError("full_line: name the consumer, 'twin' or 'mc', so the registry can grade the "
                         "terms this line will execute before its first atom (O58)")
    # DIRECT OVERRIDES, for a validation harness that must inject a REFERENCE's own parameters
    # rather than recomputing them (so a test isolates the OBE machinery from a formula
    # difference elsewhere): None means "use this module's own physics", as documented per name.
    s0_ref_mhz_override = numerics.get("s0_ref_mhz_override")
    om0_ref_hz_override = numerics.get("om0_ref_hz_override")
    gamma_p_hz_override = numerics.get("gamma_p_hz_override")
    gamma_extra_mhz_override = numerics.get("gamma_extra_mhz_override")

    delta_mhz = np.asarray(delta_mhz, dtype=float)
    n_delta = delta_mhz.size
    P_eff = float(P_W) * float(intensity_scale)

    f_g_thermal, iso_from_peak = _thermal_share(peak)
    isotope = int(numerics.get("isotope", iso_from_peak))

    beam, ap_factor, beam_note = _make_beam(float(w0_m), float(M2), window_beam)

    lam_nm = K.PEAKS[peak]["lambda_nm"]
    S0_ref_mhz = (stark_shift_S0_mhz(P_eff, w0_m, rho, delta_alpha_au=delta_alpha_au) * ap_factor
                 if s0_ref_mhz_override is None else float(s0_ref_mhz_override))
    Om0_ref_hz = (two_photon_rabi_hz(P_eff, w0_m, rho, lam_nm=lam_nm) * ap_factor
                 if om0_ref_hz_override is None else float(om0_ref_hz_override))
    I_arm0_wm2 = ap_factor * 2.0 * P_eff / (math.pi * float(w0_m) ** 2)
    conv_s = _conv_s_mhz_per_wm2(delta_alpha_au)
    T_matrix_au = two_photon_matrix_element(lam_nm=lam_nm)
    HARTREE_HZ = K.HARTREE_J / K.H_PLANCK_JS

    executed: set = set()

    def _on(name: str) -> bool:
        return abs(t[name]) > 0.0

    # -------------------------------------------------------------- population sample (once)
    rng = np.random.default_rng(seed)
    if "half_window_m" in numerics:
        half_window_m = float(numerics["half_window_m"])
    else:
        # the same axial COLLECTION window every other producer in this record uses
        # (`fullmodel.collection_z_ratio_m2` at the beam's own M2, `volume_line.collection_half_window_m`),
        # so this is atoms as the apparatus actually collects them and not the focal plane alone.
        # `numerics["half_window_m"] = 0.0` recovers the focal-plane-only comparison validation (a)
        # needs against `volume_line.joint_spectrum` called the same way.
        from .fullmodel import collection_z_ratio_m2
        from .volume_line import collection_half_window_m as _coll_half_window_m
        half_window_m = _coll_half_window_m(beam, collection_z_ratio_m2(w0_m, M2))
    clipped = not isinstance(beam, GaussianBeam)
    chord_mode = ("beam" if clipped else "gaussian") if chord == "auto" else chord
    executes = registry_terms(
        t, clipped=clipped, half_window_m=half_window_m, s0_mhz=float(S0_ref_mhz), retro_kind=retro_kind,
        retro_axial=retro_axial, retro_waist_ratio=retro_waist_ratio, retro_offset_w0=retro_offset_w0,
        sigma_laser_mhz=sigma_laser_mhz, gamma_laser_l_mhz=gamma_laser_l_mhz, gamma_foreign_mhz=gamma_foreign_mhz,
        retro_tilt_theta_rad=retro_tilt_theta_rad, kerr_depletion_frac=kerr_depletion_frac,
        kerr_lens_frac=kerr_lens_frac)
    regime = "2025" if (float(P_W) <= 0.270 + 1e-9 and float(T_C) <= 130.0 + 1e-9) else "campaign"
    if registry is None:
        registry_block = _MR.preflight(consumer, regime, executes)
    else:
        _carried = set(_MR.carried_term_ids(consumer, regime))
        registry_block = _MR.preflight(consumer, regime, executes, scope="study",
                                       gaps={x: str(registry) for x in _carried - executes},
                                       extras={x: str(registry) for x in executes - _carried})
    # the draws are the same with the geometry returned (`sample_atoms`' own docstring), so the first four
    # arrays are bit for bit the old ones and the legacy arms reproduce the old lines
    w_arr, v_arr, u_b, flux, b_arr, z_arr = sample_atoms(rng, int(n_path), beam, T_C, half_window_m,
                                                         isotope=isotope, return_geometry=True)
    n = w_arr.size

    if _on("collisions_speed") or _on("exchange_by_line"):
        n_cm3 = float(number_density_cm3(T_C))
        beta_mean_khz = beta_self_anchored(T_C + 273.15, n_cm3=1e12)["beta6_khz"]
        beta_mean_khz *= t["exchange_by_line"]
        gamma_self_mean_mhz = beta_mean_khz * 1e-3 * (n_cm3 / 1e12)
    else:
        gamma_self_mean_mhz = 0.0

    if gamma_extra_mhz_override is not None:
        # a validation harness's own homogeneous width, injected whole (the seed's own
        # `gamma_perp_extra_mhz`, which carries no associated real-detuning shift at all).
        gamma_c_mhz = np.full(n, float(gamma_extra_mhz_override))
        shift_c_mhz = np.zeros(n)
    elif _on("collisions_speed"):
        # THE RADIATOR'S OWN TRANSVERSE SPEED IS NOT THE RELATIVE SPEED (fixed 2026-09-25, module
        # docstring's own account): the perturber carries its own independent thermal motion, so
        # `_perturber_averaged_f_table` supplies the perturber-averaged <v_rel^0.6>(v_full)/
        # <...>_ensemble the radiator's own FULL 3D speed implies.
        #
        # `v_arr` IS ALREADY THE FULL 2D TRANSVERSE SPEED, NOT ONE CARTESIAN COMPONENT (corrected
        # again, same day: `sample_atoms`'s own docstring, "the transverse speed v is drawn from
        # its own target half-normal density ... the flux's own extra power of v folded into
        # flux_len" -- the DRAWN proposal is half-normal, but `flux_len = v * imp_b * v` packs TWO
        # powers of v: one is the crossing flux itself, the other is the importance repair from
        # the half-normal PROPOSAL to `v`'s own TRUE (density-weighted) target, which is Rayleigh,
        # exactly the 2D transverse-speed-magnitude law. So only ONE fresh, independent component
        # (the axial v_z) is needed to reach the radiator's full 3D speed, not two -- drawing two
        # double-counted a dimension `v_arr` already carries.
        m_kg = K.M_RB87_KG if isotope == 87 else K.M_RB85_KG
        sv_full = math.sqrt(K.K_B_J_PER_K * (float(T_C) + 273.15) / m_kg)
        vz = rng.normal(0.0, sv_full, n)
        v_full = np.sqrt(v_arr ** 2 + vz ** 2)
        v_grid, F_tab = _perturber_averaged_f_table(float(T_C) + 273.15, m_kg)
        f_of_v = np.interp(v_full, v_grid, F_tab)
        gamma_c_mhz = gamma_self_mean_mhz * t["collisions_speed"] * f_of_v
        shift_c_mhz = -gamma_c_mhz * _SHIFT_OVER_HWHM / 2.0
    else:
        gamma_c_mhz = np.full(n, gamma_self_mean_mhz)
        shift_c_mhz = np.zeros(n)

    if _on("retro_tilt"):
        sv = math.sqrt(K.K_B_J_PER_K * (float(T_C) + 273.15)
                       / (K.M_RB87_KG if isotope == 87 else K.M_RB85_KG))
        v_x = rng.normal(0.0, sv, n)
        k_drive = 2.0 * math.pi / K.LAMBDA_LASER_M
        tilt_mhz = (k_drive * retro_tilt_theta_rad * v_x) / (2.0 * math.pi) / 1e6
    else:
        tilt_mhz = np.zeros(n)

    extra_homog_mhz = (gamma_c_mhz + gamma_laser_l_mhz * t["laser"]
                       + gamma_foreign_mhz * t["foreign_gas"])
    gamma_perp_floor_mhz = float(np.min(extra_homog_mhz)) if n else 0.0

    # ---------------------------------------------------- the retro-geometry return-beam factors
    do_retro = _on("retro_geometry")
    ret_own_z = do_retro and retro_axial == "own_z"
    if ret_own_z:
        # V6.1: the returning beam read where each atom crosses. An imaged return is the forward beam's own
        # profile mirrored about the returning focus, u_ret(b, z) = u_fwd(b, Delta - z); a Gaussian return
        # of its own waist is symmetric about Delta. The transverse offset keeps the old scalar reading,
        # the offset taken along the atom's own impact parameter.
        # gaussian-limit: the declared Gaussian return of its own waist, the old model kept as an arm
        ret_beam = beam if retro_kind == "imaged" else GaussianBeam(float(w0_m) * retro_waist_ratio, float(M2))
        b_ret_arr = np.abs(b_arr - retro_offset_w0 * float(w0_m))
        z_ret_arr = (retro_focus_offset_m - z_arr) if retro_kind == "imaged" else (z_arr - retro_focus_offset_m)
        u_b_ret = None
        ratio_w = None
        executed.add("retro_geometry")
    elif do_retro:
        # gaussian-limit: the legacy focal return, kept bit for bit as the comparison arm
        ret_beam = GaussianBeam(float(w0_m) * retro_waist_ratio, float(M2))
        # `sample_atoms` does not return each atom's own z0, only w(z0) (as `w_arr`, already
        # exactly the FORWARD beam's local radius at the atom's true axial position) and u_b (the
        # forward beam's own closest-approach factor there); the impact parameter b is INVERTED
        # from u_b assuming a locally Gaussian forward profile at that z:
        # u_b = exp(-2 b^2 / w_fwd(z)^2) => b = w_fwd(z)/sqrt(2) sqrt(-ln u_b). Exact for
        # `window_beam="gaussian"`; an approximation (the profile's core, not its rings) for the
        # clipped beam. The ALWAYS-Gaussian return beam (module docstring) is then read AT z = 0
        # rather than at the atom's own z (which sample_atoms does not expose), a second
        # approximation that is exact whenever the collection window is small against the return
        # beam's own Rayleigh range, as it is at every waist and z_ratio this record uses.
        w_z0 = w_arr
        z0 = np.zeros(n)
        with np.errstate(divide="ignore", invalid="ignore"):
            b_est = np.where(u_b > 0.0, w_z0 / math.sqrt(2.0)
                             * np.sqrt(np.maximum(-np.log(np.clip(u_b, 1e-300, 1.0)), 0.0)), 0.0)
        b_ret = np.abs(b_est - retro_offset_w0 * float(w0_m))
        u_b_ret = np.asarray(ret_beam.u(b_ret, z0), float)
        w_ret_z0 = np.asarray(ret_beam.w(z0), float)
        ratio_w = w_z0 / np.maximum(w_ret_z0, 1e-300)
        executed.add("retro_geometry")
    else:
        u_b_ret = None
        ratio_w = None

    # THE RETURNING FOCUS'S PHASE HALF (F547): the Doppler chirp along each chord, rad/s per unit tau, zero for a
    # return focused on the forward focus and for every arm that is not the imaged return read at the atom's own z
    curv_arr = np.zeros(n)
    if ret_own_z and retro_kind == "imaged" and retro_focus_offset_m != 0.0 and retro_curvature == "on":
        z_R_fwd = math.pi * float(w0_m) ** 2 / (float(M2) * K.LAMBDA_LASER_M)
        c_z = z_arr / (z_arr ** 2 + z_R_fwd ** 2) + z_ret_arr / (z_ret_arr ** 2 + z_R_fwd ** 2)
        curv_arr = (2.0 * math.pi / K.LAMBDA_LASER_M) * v_arr * w_arr * c_z
        executed.add("retro_curvature")

    def _along(bm, bb, zz):
        """A beam read along chords, (nb, ntt): the clipped table through `u_fast` (zero past its reach,
        never the edge value a clamp would repeat along a chord), a Gaussian through `u`."""
        f = getattr(bm, "u_fast", None) or bm.u
        return np.asarray(f(bb, np.broadcast_to(zz, bb.shape)), float)

    if _on("chirp"):
        executed.add("chirp")
    if _on("saturation"):
        executed.add("saturation")
    b_survival = 1.0
    if _on("cascade_F"):
        b_survival = 1.0 - BRANCHING_F[peak]
        executed.add("cascade_F")
    if _on("exchange_by_line"):
        executed.add("exchange_by_line")
    if _on("collisions_speed"):
        executed.add("collisions_speed")
    if _on("laser"):
        executed.add("laser")
    if _on("foreign_gas"):
        executed.add("foreign_gas")
    if _on("retro_tilt"):
        executed.add("retro_tilt")
    if _on("kerr_depletion"):
        executed.add("kerr_depletion")
    if _on("kerr_lens"):
        executed.add("kerr_lens")

    sat_scale = 1.0 if _on("saturation") else 1e-2
    sat_renorm = 1.0 if _on("saturation") else 1e4

    Gamma_e = 2.0 * math.pi * K.GAMMA_NAT_HZ            # 6S population decay, 1/s
    Gamma_p = (1.0 / mean_5p_lifetime_s() if gamma_p_hz_override is None
              else float(gamma_p_hz_override))          # lumped 5P population decay, 1/s
    ir_branch = ir_branching_5p12()

    tau = np.linspace(-tau_edge, tau_edge, n_tau)
    dtau = tau[1] - tau[0]
    d_ang = 2.0 * math.pi * delta_mhz * 1e6             # (n_delta,) rad/s


    order = np.argsort(w_arr / np.maximum(v_arr, 1e-30))  # slowest chords (largest w/v) last
    step_all = (w_arr / v_arr) * dtau
    (w_s, _v_s, u_b_s, flux_s, step_s, gamma_c_s, shift_c_s, tilt_s) = (
        w_arr[order], v_arr[order], u_b[order], flux[order], step_all[order],
        gamma_c_mhz[order] if np.ndim(gamma_c_mhz) else np.full(n, gamma_c_mhz),
        shift_c_mhz[order], tilt_mhz[order])
    b_s, z_s = b_arr[order], z_arr[order]
    curv_s = curv_arr[order]
    if ret_own_z:
        b_ret_s, z_ret_s = b_ret_arr[order], z_ret_arr[order]
    elif do_retro:
        u_b_ret_s, ratio_w_s = u_b_ret[order], ratio_w[order]

    rate_bound = max(
        float(np.max(np.abs(d_ang))) if n_delta else 0.0,
        2.0 * math.pi * float(np.max(np.abs(S0_ref_mhz))) * 1e6,   # a frozen shift turns the phase too
        2.0 * math.pi * abs(Om0_ref_hz) * sat_scale,
        Gamma_e, Gamma_p,
        float(np.max(np.abs(curv_arr))) * tau_edge if n else 0.0,   # the curvature chirp's reach at the chord's end
    )
    keep = rate_bound * step_s / max_sub <= 0.5
    dropped_flux_frac = float(flux_s[~keep].sum() / max(flux_s.sum(), 1e-300))
    if dropped_flux_frac > dropped_flux_budget:
        raise ValueError(
            f"full_line: {dropped_flux_frac:.2e} of the flux would be dropped for its step count, over the "
            f"{dropped_flux_budget:.0e} budget. The slowest crossings are the tails of both the transit and the "
            f"ramp, so raise max_sub (now {max_sub}) or declare a larger dropped_flux_budget with its reason")
    idx_keep = np.nonzero(keep)[0]

    out = np.zeros(n_delta)
    n_used = 0
    for a in range(0, idx_keep.size, batch):
        sl = idx_keep[a:a + batch]
        nb = sl.size
        n_used += nb
        n_sub = max(1, int(math.ceil(rate_bound * float(step_s[sl].max()) / 0.5)))
        dt = (step_s[sl] / n_sub)[:, None]                      # (nb, 1) s per RK sub-step
        ub = u_b_s[sl][:, None]
        g_extra_mhz = (gamma_c_s[sl][:, None] + gamma_laser_l_mhz * t["laser"]
                      + gamma_foreign_mhz * t["foreign_gas"])
        gamma_perp = Gamma_e / 2.0 + math.pi * g_extra_mhz * 1e6     # (nb, 1) rad/s
        shift_dc_mhz = shift_c_s[sl][:, None] + tilt_s[sl][:, None]  # (nb, 1) real MHz offset
        curv_b = curv_s[sl][:, None]                                 # (nb, 1) rad/s per unit tau
        D_dc = 2.0 * math.pi * shift_dc_mhz * 1e6

        tt = np.linspace(-tau_edge, tau_edge, (n_tau - 1) * n_sub + 1)
        genv = np.exp(-2.0 * tt ** 2)
        # each arm's local intensity factor along the chord is base * env: the Gaussian chord keeps the old
        # shared envelope and per-atom peak (bit for bit), the true chord reads the beam at every step
        if chord_mode == "gaussian":
            base_f, env_f = ub, genv
        else:
            x_along = w_s[sl][:, None] * tt[None, :]
            env_f = _along(beam, np.sqrt(b_s[sl][:, None] ** 2 + x_along ** 2), z_s[sl][:, None])
            base_f = 1.0
        if ret_own_z:
            x_along = w_s[sl][:, None] * tt[None, :]
            env_r = _along(ret_beam, np.sqrt(b_ret_s[sl][:, None] ** 2 + x_along ** 2), z_ret_s[sl][:, None])
            base_r = 1.0
        elif do_retro:
            rw = ratio_w_s[sl][:, None]
            env_r = np.exp(-2.0 * (tt[None, :] * rw) ** 2)     # (nb, ntt)
            base_r = u_b_ret_s[sl][:, None]
        else:
            env_r = base_r = None
        mean_f, mean_r = (None, None) if _on("chirp") else _frozen_means(env_f, env_r, tt)

        U = np.zeros((nb, n_delta)); V = np.zeros_like(U)
        Ng = np.full((nb, n_delta), f_g_thermal)
        Ne = np.zeros_like(U); Np = np.zeros_like(U)
        Nd = np.full((nb, n_delta), 1.0 - f_g_thermal)
        Np_int = np.zeros_like(U)

        def _local_S_Om(e_fwd, e_ret):
            """(S_mhz (nb,n_delta or nb,1), Om_hz (nb,1)) at one substep.

            TWO envelope roles, not one (F-numbered corrections are for the CODE check, this one
            is for the docstring the task itself states): `e_fwd`/`e_ret` are the TRUE, always
            time-varying local envelope and drive Om (saturation reads the real local intensity
            regardless of `chirp`); the SHIFT alone is frozen at the chord's own drive-weighted
            average when `chirp` is off (`_frozen_means`), which is the one thing that term
            names. Conflating the two would make `chirp=0` also freeze the drive, which is not
            what "off means the shift frozen at its chord average" says.
            """
            e_fwd_s = e_fwd if _on("chirp") else mean_f
            e_ret_s = e_ret if _on("chirp") else mean_r
            if do_retro:
                u_fwd_t, u_ret_t = base_f * e_fwd, base_r * e_ret
                u_fwd_s, u_ret_s = base_f * e_fwd_s, base_r * e_ret_s
                if _on("kerr_depletion"):
                    corr_t = 1.0 - kerr_depletion_frac * (u_fwd_t + u_ret_t)
                    corr_s = 1.0 - kerr_depletion_frac * (u_fwd_s + u_ret_s)
                    u_fwd_t, u_ret_t = u_fwd_t * corr_t, u_ret_t * corr_t
                    u_fwd_s, u_ret_s = u_fwd_s * corr_s, u_ret_s * corr_s
                I_fwd, I_ret = I_arm0_wm2 * u_fwd_t, (rho * I_arm0_wm2) * u_ret_t
                I_fwd_s, I_ret_s = I_arm0_wm2 * u_fwd_s, (rho * I_arm0_wm2) * u_ret_s
                # rho is the intensity ratio AT THE ATOMS (RHO_RETRO's own docstring), i.e. the
                # ratio of the two beams' ON-AXIS PEAK intensities, whatever their waists: the
                # return beam's own shape (u_ret_t, normalised to ITS OWN peak) carries the waist
                # difference and rho alone sets the peak-to-peak ratio.
                S_mhz = RAMP_SIDE * conv_s * (I_fwd_s + I_ret_s)
                e0sq_au = (4.0 * np.sqrt(np.maximum(I_fwd * I_ret, 0.0)) / (K.EPS0_F_PER_M * K.C_M_PER_S)
                          / _ATOMIC_FIELD_V_PER_M ** 2)
                M_hz = (e0sq_au / 4.0) * T_matrix_au * HARTREE_HZ
                # THE SATURATION KNOB ACTS HERE TOO (the moment budget of 2026-09-25): this branch built the Rabi
                # frequency from the two arms' intensities without `sat_scale`, while `sat_renorm` still scaled the
                # output by 1e4, so `saturation=0` with the retro geometry on changed nothing but the normalisation
                # and every weak-field line of the budget ran saturated.
                Om_hz = 2.0 * M_hz * sat_scale
            else:
                u_t, u_s = base_f * e_fwd, base_f * e_fwd_s
                if _on("kerr_depletion"):
                    u_t = u_t * (1.0 - kerr_depletion_frac * u_t)
                    u_s = u_s * (1.0 - kerr_depletion_frac * u_s)
                S_mhz = RAMP_SIDE * S0_ref_mhz * u_s
                Om_hz = Om0_ref_hz * sat_scale * u_t
            return S_mhz, Om_hz

        def rhs(Uc, Vc, Ngc, Nec, Npc, Ndc, e_fwd, e_ret, tau_c=0.0):
            S_mhz, Om_hz = _local_S_Om(e_fwd, e_ret)
            if _on("kerr_lens"):
                S_mhz = S_mhz + kerr_lens_frac * delta_mhz[None, :] * (base_f * e_fwd)
            # FIXED 2026-09-25 (the thesis side's sign check): D_dc (the collisional shift plus
            # the retro-tilt Doppler term, `shift_dc_mhz`) must enter with the SAME sign as S_mhz,
            # because both are detuning offsets on the one resonance condition D=0 <=>
            # delta_mhz = S_mhz + shift_dc_mhz (module docstring's D(t) = 2 pi (delta_hz - sign
            # S(t)), generalised to every shift the atom carries, not just the light shift). The
            # `+ D_dc` this replaces put the collisional (RED, i.e. negative) shift on the BLUE
            # side of resonance -- confirmed by probe:9a79b0ec, whose collisions_speed-only line
            # self-centred at +0.0452 MHz against a theoretical shift_mean_mhz of -0.0452 MHz. The
            # planted guard (test_bloch_full.py, test_guard_collisional_shift_lands_on_red_side)
            # fails on the old `+ D_dc` and passes on this line.
            D = d_ang[None, :] - 2.0 * math.pi * S_mhz * 1e6 - D_dc - curv_b * tau_c
            Om = 2.0 * math.pi * Om_hz
            dU = -gamma_perp * Uc - D * Vc
            dV = D * Uc - gamma_perp * Vc - Om * (Nec - Ngc)
            dNe = 0.5 * Om * Vc - Gamma_e * Nec
            dNg = -0.5 * Om * Vc + b_survival * Gamma_p * Npc
            dNp = Gamma_e * Nec - Gamma_p * Npc
            dNd = (1.0 - b_survival) * Gamma_p * Npc
            return dU, dV, dNg, dNe, dNp, dNd

        for k in range(tt.size - 1):
            if chord_mode == "gaussian":
                e0f, e1f = float(env_f[k]), float(env_f[k + 1])
            else:
                e0f, e1f = env_f[:, k:k + 1], env_f[:, k + 1:k + 2]
            emf = 0.5 * (e0f + e1f)
            if do_retro:
                e0r, e1r = env_r[:, k:k + 1], env_r[:, k + 1:k + 2]
                emr = 0.5 * (e0r + e1r)
            else:
                e0r = e1r = emr = None
            t0c, t1c = float(tt[k]), float(tt[k + 1])
            tmc = 0.5 * (t0c + t1c)
            k1 = rhs(U, V, Ng, Ne, Np, Nd, e0f, e0r, t0c)
            k2 = rhs(U + 0.5 * dt * k1[0], V + 0.5 * dt * k1[1], Ng + 0.5 * dt * k1[2],
                    Ne + 0.5 * dt * k1[3], Np + 0.5 * dt * k1[4], Nd + 0.5 * dt * k1[5], emf, emr, tmc)
            k3 = rhs(U + 0.5 * dt * k2[0], V + 0.5 * dt * k2[1], Ng + 0.5 * dt * k2[2],
                    Ne + 0.5 * dt * k2[3], Np + 0.5 * dt * k2[4], Nd + 0.5 * dt * k2[5], emf, emr, tmc)
            k4 = rhs(U + dt * k3[0], V + dt * k3[1], Ng + dt * k3[2],
                    Ne + dt * k3[3], Np + dt * k3[4], Nd + dt * k3[5], e1f, e1r, t1c)
            Np_new = Np + dt / 6.0 * (k1[4] + 2 * k2[4] + 2 * k3[4] + k4[4])
            U = U + dt / 6.0 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            V = V + dt / 6.0 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            Ng = Ng + dt / 6.0 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
            Ne = Ne + dt / 6.0 * (k1[3] + 2 * k2[3] + 2 * k3[3] + k4[3])
            Nd = Nd + dt / 6.0 * (k1[5] + 2 * k2[5] + 2 * k3[5] + k4[5])
            Np_int += 0.5 * (Np + Np_new) * dt
            Np = Np_new

        detected = Gamma_p * ir_branch * sat_renorm * Np_int
        out += np.sum(flux_s[sl][:, None] * detected, axis=0)

    if sigma_laser_mhz > 0.0 and _on("laser"):
        dnu = float(delta_mhz[1] - delta_mhz[0]) if n_delta > 1 else 1.0
        from scipy.signal import fftconvolve
        out = fftconvolve(out, _gaussian_kernel(delta_mhz - float(np.mean(delta_mhz)),
                                                sigma_laser_mhz), mode="same") * dnu

    info = dict(
        executed=executed, dropped_flux_frac=dropped_flux_frac, beam_note=beam_note,
        n_atoms_used=int(n_used), n_atoms_kept=int(idx_keep.size), n_atoms_total=int(n),
        S0_ref_mhz=float(S0_ref_mhz), Om0_ref_hz=float(Om0_ref_hz),
        aperture_factor=float(ap_factor), gamma_perp_floor_mhz=float(gamma_perp_floor_mhz),
        b_survival=float(b_survival), f_g_thermal=float(f_g_thermal), isotope=int(isotope),
        rate_bound_rad_s=float(rate_bound), gamma_self_mean_mhz=float(gamma_self_mean_mhz),
        terms=dict(t), numerics=dict(n_tau=n_tau, tau_edge=tau_edge, batch=batch, max_sub=max_sub,
                                     delta_alpha_au=delta_alpha_au, intensity_scale=intensity_scale,
                                     chord=chord_mode, retro_kind=retro_kind, retro_axial=retro_axial,
                                     retro_focus_offset_m=retro_focus_offset_m,
                                     dropped_flux_budget=dropped_flux_budget),
        registry=registry_block,
    )
    return out, info
