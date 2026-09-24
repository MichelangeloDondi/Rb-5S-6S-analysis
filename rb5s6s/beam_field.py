"""The drive beam's REAL field near the focus: a Gaussian of radius w_in, hard-clipped by the EOM's
bore, focused by the drive lens, and (for M2 > 1) an incoherent mode mixture -- propagated by the
paraxial Fresnel (Collins) diffraction integral into the whole focal REGION, not only the focal plane.

WHY THIS EXISTS (O45/O46, owner, 2026-09-22, re-sent verbatim: "the beam can't be approximated to a
perfect cylinder for waist too small and so divergence, for M^2 and for beam clipping"). The package
already computes the bore's effect AT the focal plane in closed form and by quadrature
(`lineshape.aperture_onaxis_factor`, `aperture_spread_factor`, `aperture_onaxis_factor_actual`,
`W0_CENTRAL_M`; the findings behind them are F104, F105, F108, F280, F281, F291 in
`private/cache/plan_2026-09-16/FINDINGS_NIGHT.md`). What is missing is the field AWAY from focus: an
atom's chord through the collected volume samples the beam at every z along its path, and F224/F281
measured that the local shift and the local transit width move TOGETHER as the beam diverges, which a
single on-axis factor at one w0 cannot carry. `rb5s6s/volume_line.py` (built alongside this module by
another agent) walks atom chords and needs, at each point, the local peak-intensity factor
u(b, z) = I(b, z) / I_peak_focus and a local radius w(z); its default beam is a plain
`GaussianBeam(w0_m, m2)`. `ClippedBeam` below answers the SAME two calls (`u`, `w`) for the REAL,
apertured beam, so a caller can swap one for the other without touching the chord machinery.

THE PHYSICS, RUNG 2 (a closed integral transform, not a Monte Carlo). A field u_in(rho) at a reference
plane propagates through any cascade of free space and thin lenses to a plane a distance such that the
whole system's paraxial ray matrix is (A, B, C, D) via the cylindrically symmetric Collins integral

    u_out(r) = (-i k / B) exp(i k L) exp(i k D r^2 / (2 B))
               int_0^a u_in(rho) exp(i k A rho^2 / (2 B)) J0(k rho r / B) rho drho,

exact for any paraxial scalar field, smooth or hard-edged (the hard aperture is simply where u_in is
truncated to zero, rho > a). Only |u_out|^2 is needed here, so the two prefactor phases drop out and
the reported intensity is (k/B)^2 times the squared modulus of the quadrature above -- one Hankel-type
transform per z, exactly generalising the package's own focal-plane quadrature
(`lineshape._actual_focus_quadrature`) to the whole axial window.

GEOMETRY ASSUMPTION, MATCHED TO THE EXISTING TABLE. For [free space d_ap][thin lens f][free space
s = f + z], composing the three ray matrices gives A(z) = -z/f (independent of d_ap) and
B(z) = f + z(1 - d_ap/f). At d_ap = 0 (the bore sitting AT the lens, no separate propagation modelled
between them) this is A(z) = -z/f, B(z) = f + z, and at z = 0 it reduces to A = 0, B = f: the PLAIN
Fourier-Bessel transform `lineshape._actual_focus_quadrature` already uses, with no z-dependence at
all (F281: "the focal map needs no bore-to-lens distance -- free propagation before the lens is a
quadratic phase" -- and indeed B(0) = f for ANY d_ap, since A(0) = 0 always: the back focal PLANE's own
intensity pattern is independent of where upstream of the lens the truncation sits). AWAY from focus
(z != 0) that is no longer true: B(z) depends on d_ap, because a bore some distance before the lens
imprints Fresnel ringing on the beam that only shows up off the focal plane (the "two apertures with
Fresnel propagation between them" F222 lists as unmodelled). `d_ap_m` is kept as an explicit
constructor argument, defaulting to 0.0 to match the existing table exactly; the input radius at the
lens and this distance are both open apparatus items (`docs/plan/12`, "beam radius at the focusing
lens"), so a caller who learns either fact later passes it here without changing the physics above.

M2 > 1: AN INCOHERENT MIXTURE OF AXISYMMETRIC LAGUERRE-GAUSS MODES LG(p, 0). The family represented is
beams whose excess divergence is purely RADIAL -- no orbital angular momentum, no azimuthal structure --
which is the natural minimal family compatible with a circularly symmetric aperture and a circularly
symmetric seed; it is not the most general M2 > 1 beam (one carrying azimuthal structure, l != 0 modes
or asymmetric Hermite-Gauss combinations, is a different and strictly larger family), but it is the one
this axisymmetric problem needs and the one a quadrature over a single radial coordinate can carry.
Each LG(p, 0), built on the same embedded fundamental radius w_in as the p = 0 mode, has its own
second-moment radius growing as W_p(z)^2 = (2p + 1) w_fund(z)^2 -- the standard M2 = 2p + 1 result for
this mode family, reproduced here by direct quadrature against the textbook value at p = 0..3 (this
module's own commit record). An incoherent (power-weighted, no interference) mixture of p = 0 (weight
1 - c) and one higher mode p1 (weight c) gives a composite second moment
W_mix(z)^2 = sum_p c_p (2p+1) w_fund(z)^2, which is EXACTLY of the single-M2 embedded-Gaussian form
W_mix(0)^2 [1 + (z lambda M2 / (pi W_mix(0)^2))^2] with M2 = sum_p c_p (2p+1) -- proved algebraically and
checked numerically to 1e-8 relative in this module's own development record, because W_mix(z)^2 is a
non-negative, w-symmetric-in-z, quadratic-in-z sum of terms that are each individually of that shape.
`_mode_weights_for_m2` picks the smallest p1 with 2 p1 + 1 >= M2 and solves c = (M2 - 1) / (2 p1) in
[0, 1], so the requested M2 is hit exactly at every z, clipped or not (clipping the mixture is then
"each mode clipped and propagated, summed in intensity", exactly as ordered).

WHICH RADIUS `w(z)` REPORTS, AND WHY. Two candidates exist and the record has burned one of them: F104
computed a second-moment ("D4-sigma"-style) radius for the clipped focal profile and RETRACTED it in
the same finding, because a hard aperture's rings put weight at large r, so an r^2-weighted moment
depends sensitively on where the radial grid is cut -- "impossible" values (M2 below one) came out of
that column. `w(z)` here is instead the 1/e^2 radius of the profile normalised to ITS OWN on-axis value
AT THAT z (never to the global peak), matching what a knife-edge or a beam profiler reads on the bench
and matching the convention `W0_CENTRAL_M` and `aperture_onaxis_factor_actual` already adopt for the
focal plane -- so `w(0.0)` reproduces the package's own "actual focus" exactly. The second-moment
radius is NOT abandoned -- it is exactly what makes the M2 algebra above exact -- but it is exposed
separately, `second_moment_radius_m`, with F104's caveat carried in its own docstring, and used in this
module's own tests only in the regime (no clipping) where the caveat does not apply.

RUNG. This module is rung 2 throughout: every quantity is a deterministic quadrature of a closed
paraxial integrand, convergence-checked against itself (the p = 0 transmitted power against its closed
form; three interior table nodes against a finer direct quadrature) rather than assumed. No Monte Carlo
here and no `kernel_gate` node: `ClippedBeam` is not imported by `rb5s6s/fullmodel.py` or by
`scripts/run_kernel_mc.py`, so it sits outside the validated-node population by construction
(`kernel_gate.model_population`) until a future wave wires it in and pays for that validation.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple, Union

import numpy as np
from scipy.interpolate import PchipInterpolator, RectBivariateSpline
from scipy.special import eval_genlaguerre, j0

from ._compat import trapezoid
from .constants import DRIVE_LENS_F_M, EOM_APERTURE_RADIUS_M, LAMBDA_LASER_M

__all__ = ["ClippedBeam", "mode_weights_for_m2", "axial_half_intensity_depth_m"]

ArrayLike = Union[float, np.ndarray]


def mode_weights_for_m2(m2: float) -> Tuple[Tuple[int, float], ...]:
    """The two-mode LG(p, 0) mixture (radial index p, power weight) hitting `m2` exactly.

    p = 0 (the plain Gaussian, M2 = 1) at weight 1 - c, and the smallest p1 >= 1 with
    2 p1 + 1 >= m2 at weight c = (m2 - 1) / (2 p1), so the composite's power-weighted M2,
    sum_p weight_p (2p + 1), equals `m2` to floating point. `m2 = 1.0` returns the pure mode
    alone (c = 0, no p1 term). See the module docstring for why this family (radial LG modes,
    no azimuthal structure) and why the mixture's second moment is exactly the requested M2 at
    every z, not only at the waist.
    """
    m2 = float(m2)
    if not math.isfinite(m2) or m2 < 1.0 - 1e-9:
        raise ValueError(f"mode_weights_for_m2: m2={m2!r} must be finite and >= 1")
    if abs(m2 - 1.0) <= 1e-12:
        return ((0, 1.0),)
    p1 = max(1, int(math.ceil((m2 - 1.0) / 2.0 - 1e-12)))
    c = (m2 - 1.0) / (2.0 * p1)
    c = min(max(c, 0.0), 1.0)
    return ((0, 1.0 - c), (p1, c))


def _ray_matrix_AB(z_m: ArrayLike, f_m: float, d_ap_m: float) -> Tuple[ArrayLike, ArrayLike]:
    """A(z), B(z) of the composed ray matrix [free d_ap][lens f][free f + z], the aperture plane to
    a point z from the paraxial focus (z > 0 beyond the lens). A(z) = -z/f is independent of d_ap
    (module docstring); B(z) = f + z(1 - d_ap/f) reduces to f + z at d_ap = 0 and to f at z = 0 for
    ANY d_ap, which is why the existing focal-plane table needs no bore-to-lens distance."""
    z = np.asarray(z_m, dtype=float)
    A = -z / f_m
    B = f_m + z * (1.0 - d_ap_m / f_m)
    return A, B


@dataclass
class ClippedBeam:
    """The real drive beam near the focus: a Gaussian (or, for m2 > 1, an incoherent LG(p,0) mixture
    built on the same embedded radius) of input radius `w_in_m` at the EOM bore, hard-clipped at
    `a_m`, focused by a lens of focal length `f_m`, tabulated on a radial x axial grid spanning
    several Rayleigh ranges of its own actual focus. See the module docstring for the geometry
    convention, the M2 mode family and which radius `w()` reports.

    Construction pays for a 2-D quadrature (build once); `u` and `w` are then table interpolations
    with their error bounded at construction (`_self_check`, raises rather than trusting an
    unchecked table, mirroring `lineshape._actual_onaxis_table`'s own discipline).
    """

    w_in_m: float
    a_m: float = EOM_APERTURE_RADIUS_M
    f_m: float = DRIVE_LENS_F_M
    lam_m: float = LAMBDA_LASER_M
    m2: float = 1.0
    d_ap_m: float = 0.0
    z_span_zr: float = 4.0
    n_z: int = 31
    n_xi: int = 140
    n_rho: int = 500
    xi_max: float = 6.0
    interp_tol: float = 5e-3

    #: samples per full cycle of the defocus phase kept at the tabulated window's worst (largest
    #: |z|) edge; not a dataclass field (no type annotation), just the oscillation-sampling floor
    #: `_min_n_rho_for_oscillation` enforces. Plain trapezoidal quadrature of an oscillatory
    #: integrand needs many points per cycle for per-mille accuracy: 24 left a residual few-per-
    #: mille error at a window edge of several zR (this module's own development record, found by
    #: comparing a fresh quadrature there against the standard focused-Gaussian closed form after
    #: ruling out xi- and z-resolution as the cause); 64 closed the remaining gap to this module's
    #: own 1e-3 target with margin (test (a)'s own achieved worst case is a few times 1e-4).
    _MIN_POINTS_PER_CYCLE = 64

    def __post_init__(self) -> None:
        if self.n_z % 2 == 0:
            self.n_z += 1  # force an exact z = 0 node (odd count, symmetric span)
        self._k = 2.0 * math.pi / self.lam_m
        self._modes = mode_weights_for_m2(self.m2)
        # THE APERTURE-PLANE GRID SPANS [0, a_m] PHYSICALLY, BUT IS SAMPLED OUT ONLY TO WHERE THE
        # INPUT HAS ANY WEIGHT LEFT: a hard cutoff at a_m always matters for the TRANSMITTED-POWER
        # bookkeeping, but sampling a uniform grid all the way to a_m when a_m is many w_in wide
        # starves the resolution of the part of the integrand that actually varies (the Gaussian
        # envelope times the oscillatory Bessel kernel). The highest-p mode's own natural radial
        # extent grows as sqrt(2p+1) w_in (module docstring), so the pad scales with it; six such
        # radii leaves exp(-2*6^2) = exp(-72) of the envelope beyond the cut, and the excluded tail
        # is capped at a_m regardless, so a genuinely narrow aperture is never widened by this.
        p_max = max(p for p, _ in self._modes)
        w_in_eff = self.w_in_m if math.isfinite(self.w_in_m) else self.a_m
        self._rho_hi = min(self.a_m, 6.0 * math.sqrt(2 * p_max + 1) * w_in_eff)
        self._rho = np.linspace(0.0, self._rho_hi, self.n_rho)
        self._amp_in = {p: self._mode_input_amplitude(p, self._rho) for p, _ in self._modes}
        self._p_transmitted = {p: self._transmitted_power(p) for p, _ in self._modes}
        self._check_p0_closed_form()

        # locate the natural axial scale from the on-axis profile at z = 0 first (no defocus phase
        # there, A(0) = 0, so this first probe is unaffected by the oscillation issue below), so the
        # axial window is sized to THIS beam's own actual focus and not to the unclipped free-focus
        # guess (F105: the two can differ by a factor of two near the bore's floor).
        w0_probe = self._w1e2_at_z(0.0, self._radial_grid(0.0))
        zR = math.pi * w0_probe ** 2 / self.lam_m
        #: OPTIONAL convenience attribute, not part of the two-method beam interface
        #: (`volume_line.GaussianBeam`'s own docstring): this beam's own probed Rayleigh range, for
        #: a caller wanting `collection_half_window_m(beam, z_ratio)`-style sizing. A clipped or
        #: mixed-mode beam has no single exact zR the way an unclipped m2=1 Gaussian does; this is
        #: the 1/e^2 reading at z=0 read back into the usual pi w^2/lambda, a reasonable convention
        #: and not a claim that w(z) is exactly hyperbolic in it.
        self.z_R_m = zR
        span = self.z_span_zr * zR
        self._z_nodes = np.linspace(-span, span, self.n_z)
        mid = self.n_z // 2
        # for an odd node count and a symmetric span, the middle node IS z = 0 exactly in real-
        # number arithmetic; float64 rounding inside np.linspace can still miss it by ~1 ULP, which
        # the assert below would otherwise trip on some (n_z, span) combinations and not others.
        # Snap it: this is not tabulation choice, it is guaranteeing an already-mathematically-true
        # value survives floating point, so `actual_focus_m`/`onaxis_per_watt` stay exact reads.
        assert abs(self._z_nodes[mid]) < 1e-6 * span, \
            f"z=0 landed {self._z_nodes[mid]:.3e} from the middle node, far more than float rounding"
        self._z_nodes[mid] = 0.0

        # THE DEFOCUS PHASE exp(i k A rho^2 / (2 B)) OSCILLATES FASTER THE FURTHER z SITS FROM
        # FOCUS (|A| grows with |z|), and a FIXED n_rho that resolves the in-focus integrand can
        # under-sample it badly at the window's edge: measured in this module's own development
        # record, a window edge carrying about 32 full cycles across the aperture grid with the
        # constructor's own default n_rho gave a percent-level error in `w(z)`, invisible until
        # checked against an independent doubled-resolution quadrature. `self.n_rho` is therefore a
        # FLOOR: it is raised (never lowered) so every z in the tabulated window keeps at least
        # `_MIN_POINTS_PER_CYCLE` samples per oscillation, and the aperture grid is rebuilt if it
        # was raised.
        z_worst = float(max(abs(self._z_nodes[0]), abs(self._z_nodes[-1])))
        n_rho_needed = self._min_n_rho_for_oscillation(z_worst)
        if n_rho_needed > self.n_rho:
            self.n_rho = n_rho_needed
            self._rho = np.linspace(0.0, self._rho_hi, self.n_rho)
            self._amp_in = {p: self._mode_input_amplitude(p, self._rho) for p, _ in self._modes}
            self._p_transmitted = {p: self._transmitted_power(p) for p, _ in self._modes}
            self._check_p0_closed_form()

        self._xi_nodes = np.linspace(0.0, self.xi_max, self.n_xi)
        I_table = np.empty((self.n_z, self.n_xi))
        w1e2 = np.empty(self.n_z)
        for i, z in enumerate(self._z_nodes):
            r_grid = self._xi_nodes * self._r_scale(z)
            row = self._mixture_intensity(z, r_grid)
            I_table[i, :] = row
            w1e2[i] = self._w1e2_from_profile(r_grid, row)
        self._I_table = I_table
        self._w1e2_of_z = w1e2
        self._i_peak = float(I_table[mid, 0])          # I(0, 0), an exact tabulated node
        # A BICUBIC SPLINE over both axes (2026-09-22). Bilinear interpolation was found, in this module's
        # own development record, to carry z-direction error above 1e-3 well inside the window, and the
        # tensor-product pchip that replaced it assumed I(r, z) single-peaked in xi, which a clipped
        # focus is not: its rings gave pchip's derivative estimates errors up to 7.9e-3 of peak at
        # random interior points (at z = -0.64 zR, xi = 1.19, a 2.46 mm input), above this table's own
        # 5e-3 bound, where the three fixed probes of `_self_check` never looked. The spline through
        # the same nodes stays within 6e-4 there. It can dip below zero beside a ring's zero and an
        # intensity cannot, so `u` floors it at 0.
        self._spline = RectBivariateSpline(self._z_nodes, self._xi_nodes, self._I_table, kx=3, ky=3, s=0)
        # w(z) is a SMOOTH, single-minimum curve (module docstring: w^2 is quadratic in z near a
        # stationary point at z=0), so a shape-preserving cubic (PCHIP) needs far fewer axial nodes
        # than the bilinear I(r,z) table for the same accuracy -- plain linear interpolation of
        # `w1e2_of_z` over a `z_span_zr` = 6-8 window was found, in this module's own development
        # record, to carry a few PER CENT error from the curve's own curvature, not from n_z being
        # small in absolute terms.
        self._w_interp = PchipInterpolator(self._z_nodes, self._w1e2_of_z)
        self._self_check()

    # ------------------------------------------------------------------ construction internals

    def _mode_input_amplitude(self, p: int, rho: np.ndarray) -> np.ndarray:
        """L_p(2 rho^2 / w_in^2) exp(-rho^2 / w_in^2), real, on the fixed aperture grid [0, a_m].
        `w_in_m = inf` gives the amplitude 1 identically (every mode degenerates to a uniformly
        illuminated aperture): the exact w_in -> infinity limit used by the floor test, not a
        special case in the physics."""
        if math.isfinite(self.w_in_m):
            x = 2.0 * rho ** 2 / self.w_in_m ** 2
            return eval_genlaguerre(p, 0, x) * np.exp(-(rho / self.w_in_m) ** 2)
        return np.ones_like(rho)          # L_p(0) = 1 for every p: uniform illumination, exactly

    def _transmitted_power(self, p: int) -> float:
        """Mode p's own transmitted power, int_0^a [amp_p(rho)]^2 2 pi rho drho. Closed form only
        at p = 0 (checked in `_check_p0_closed_form`); general p by quadrature on the same grid
        the field uses, which is what the field's own transmitted-power normalisation needs to be
        consistent with (a mismatched grid between the two was F280's own bug, corrected here by
        construction: both use `self._rho`)."""
        amp = self._amp_in[p]
        return float(trapezoid(amp ** 2 * 2.0 * math.pi * self._rho, self._rho))

    def _check_p0_closed_form(self) -> None:
        if not math.isfinite(self.w_in_m):
            return  # the uniform-illumination limit has no Gaussian closed form to check against
        exact = (math.pi * self.w_in_m ** 2 / 2.0) * (1.0 - math.exp(-2.0 * self.a_m ** 2 / self.w_in_m ** 2))
        got = self._p_transmitted[0]
        if exact <= 0 or abs(got / exact - 1.0) > 1e-3:
            raise ValueError(
                f"ClippedBeam: p=0 transmitted power {got:.6e} misses its closed form {exact:.6e} "
                f"by more than 1e-3 at w_in={self.w_in_m:.3e}; raise n_rho")

    def _kernel_and_AB(self, z: float, r_grid: np.ndarray) -> Tuple[float, float, np.ndarray]:
        A, B = _ray_matrix_AB(z, self.f_m, self.d_ap_m)
        A, B = float(A), float(B)
        if abs(B) < 1e-9:
            raise ValueError(f"ClippedBeam: |B(z={z:.4e})|={abs(B):.3e} is degenerate; narrow z_span_zr")
        arg = self._k * np.outer(r_grid, self._rho) / B
        return A, B, j0(arg)

    def _mixture_intensity(self, z: float, r_grid: np.ndarray) -> np.ndarray:
        """I_mix(r_grid, z), intensity per TOTAL recorded watt of the mixture: each mode's field is
        propagated by the same Collins-Hankel kernel, normalised to ITS OWN transmitted watt, then
        combined with the mode's power weight -- an incoherent (intensity, not amplitude) sum, since
        the modes of a real multimode beam carry no fixed relative phase."""
        A, B, kernel = self._kernel_and_AB(z, r_grid)
        out = np.zeros_like(r_grid)
        for p, weight in self._modes:
            if weight <= 0.0:
                continue
            phase = np.exp(1j * self._k * A * self._rho ** 2 / (2.0 * B))
            integrand = self._amp_in[p] * phase * self._rho
            field = trapezoid(integrand[None, :] * kernel, self._rho, axis=1)
            I_true = (self._k / B) ** 2 * np.abs(field) ** 2
            out += weight * I_true / self._p_transmitted[p]
        return out

    def _r_scale(self, z_m: ArrayLike) -> ArrayLike:
        """A generous, purely NUMERICAL (not physical) radial scale for the table at this z: the
        complex-beam-parameter (q) width of the UNCLIPPED Gaussian-optics reference beam (input
        radius capped at the aperture, `min(w_in, a_m)`, for the strongly clipped regime, where the
        aperture and not the input beam sets the radius), propagated through the SAME ray matrix A(z), B(z) as the field itself.

        NOT the simpler substitution "replace f by B(z) in the free-focus formula": that
        substitution is only the w=0 value of this q-based expression and was found, in this
        module's own development record, to UNDERESTIMATE the true unclipped w(z) by a factor
        growing to about 5-9x at z = 10 zR (it tracks the near-focus curvature but not the correct
        far-field divergence angle w_in/f). The q-parameter form used here is EXACT for the
        reference unclipped Gaussian at every z and every d_ap, including the regime where the
        input's own Rayleigh range is not much larger than f (checked against the standard
        w0 sqrt(1+(z/zR)^2) formula in the ordinary regime, agreeing to a percent or better out to
        z = 10 zR, and against neither approximation outside it). Vectorized in `z_m` (scalar or
        array) so the hot path, `u()`, never loops in Python over its query points."""
        w_eff = min(self.w_in_m, self.a_m) if math.isfinite(self.w_in_m) else self.a_m
        zR_in = math.pi * w_eff ** 2 / self.lam_m
        q_in = 1j * zR_in
        A, B = _ray_matrix_AB(z_m, self.f_m, self.d_ap_m)
        C = -1.0 / self.f_m
        D = 1.0 - self.d_ap_m / self.f_m
        q_out = (A * q_in + B) / (C * q_in + D)
        w2 = -self.lam_m / (math.pi * np.imag(1.0 / q_out))
        return np.sqrt(np.abs(w2))

    def _radial_grid(self, z: float) -> np.ndarray:
        return np.linspace(0.0, self.xi_max, self.n_xi) * float(self._r_scale(z))

    def _min_n_rho_for_oscillation(self, z_worst: float) -> int:
        """The aperture-grid point count needed to resolve TWO oscillatory factors at once at the
        tabulated window's worst-case |z|: the defocus phase exp(i k A rho^2 / (2B)) (quadratic in
        rho) AND the Bessel kernel J0(k r rho / B), which for large argument oscillates like a
        sinusoid of that argument (linear in rho, at the largest observation radius the table
        samples, `xi_max * r_scale(z_worst)`). Both are evaluated at their steepest point (rho =
        `self._rho_hi`) and their phase RATES added, a conservative (not tight) bound; the result
        keeps at least `_MIN_POINTS_PER_CYCLE` samples per cycle of the combined rate."""
        A, B = _ray_matrix_AB(z_worst, self.f_m, self.d_ap_m)
        A, B = float(A), float(B)
        r_max = self.xi_max * float(self._r_scale(z_worst))
        rate_defocus = self._k * abs(A) * self._rho_hi / abs(B)         # d/drho of the defocus phase at rho_hi
        rate_bessel = self._k * r_max / abs(B)                          # d/drho of the Bessel's own phase
        total_phase = (rate_defocus + rate_bessel) * self._rho_hi
        n_cycles = total_phase / (2.0 * math.pi)
        return int(math.ceil(self._MIN_POINTS_PER_CYCLE * max(n_cycles, 1.0))) + 50

    @staticmethod
    def _w1e2_from_profile(r_grid: np.ndarray, I_row: np.ndarray) -> float:
        i0 = float(I_row[0])
        target = i0 * math.exp(-2.0)
        below = np.nonzero(I_row <= target)[0]
        if not below.size or below[0] == 0:
            raise ValueError(
                "ClippedBeam: the tabulated radial grid does not reach the 1/e^2 crossing; "
                "widen xi_max")
        j = int(below[0])
        return float(np.interp(target, [I_row[j], I_row[j - 1]], [r_grid[j], r_grid[j - 1]]))

    def _w1e2_at_z(self, z: float, r_grid: np.ndarray) -> float:
        return self._w1e2_from_profile(r_grid, self._mixture_intensity(z, r_grid))

    def _self_check(self) -> None:
        """Interior (z, xi) probes against a fresh direct quadrature at that exact point, never
        against the table's own neighbours -- the same discipline as
        `lineshape._actual_onaxis_table` and `aperture_spread_factor`'s node caches. Raises rather
        than returning an interpolation whose error has not been measured. Three fixed probes and
        twenty-four seeded random ones: the fixed three alone passed a table whose interpolant missed
        by 7.9e-3 of peak between rings (2026-09-22), because none of them sat where it missed."""
        z_lo, z_hi = float(self._z_nodes[0]), float(self._z_nodes[-1])
        rng = np.random.default_rng(20260922)
        probes = [(0.3, 0.25), (0.5, 0.5), (0.7, 0.75)] + [tuple(p) for p in rng.uniform(0.0, 1.0, (24, 2))]
        for fz, fxi in probes:
            z = z_lo + fz * (z_hi - z_lo)
            xi = fxi * self.xi_max
            r = xi * self._r_scale(z)
            exact = float(self._mixture_intensity(z, np.array([r]))[0])
            got = max(float(np.ravel(self._spline.ev(z, xi))[0]), 0.0)
            scale = max(self._i_peak, 1e-300)
            err = abs(got - exact) / scale
            if err > self.interp_tol:
                raise ValueError(
                    f"ClippedBeam: interpolation missed its bound at z={z:.4e}, xi={xi:.3f} "
                    f"({got:.6e} against {exact:.6e}, err/peak={err:.2e} > {self.interp_tol:.2e}); "
                    f"raise n_z/n_xi or widen interp_tol")
        # the SAME discipline for the separate w(z) curve (PCHIP over z_nodes): three interior
        # probes against a fresh direct crossing-search, never against the curve's own neighbours.
        for fz in (0.3, 0.5, 0.7):
            z = z_lo + fz * (z_hi - z_lo)
            exact_w = self._w1e2_at_z(z, self._radial_grid(z))
            got_w = float(self._w_interp(z))
            err_w = abs(got_w - exact_w) / exact_w
            if err_w > self.interp_tol:
                raise ValueError(
                    f"ClippedBeam: w(z) interpolation missed its bound at z={z:.4e} "
                    f"({got_w:.6e} against {exact_w:.6e}, rel err={err_w:.2e} > {self.interp_tol:.2e}); "
                    f"raise n_z or widen interp_tol")

    # ---------------------------------------------------------------------------- bounds handling

    def _bounds_check_z(self, z: np.ndarray, clamp: bool) -> np.ndarray:
        lo, hi = float(self._z_nodes[0]), float(self._z_nodes[-1])
        bad = (z < lo) | (z > hi)
        if np.any(bad):
            if clamp:
                return np.clip(z, lo, hi)
            raise ValueError(
                f"ClippedBeam: z outside the tabulated window [{lo:.4e}, {hi:.4e}] m "
                f"(min/max asked {float(np.min(z)):.4e}/{float(np.max(z)):.4e}); pass clamp=True "
                f"or widen z_span_zr")
        return z

    def _to_table_coords(self, z: np.ndarray, b: np.ndarray, clamp: bool) -> Tuple[np.ndarray, np.ndarray]:
        z = self._bounds_check_z(z, clamp)
        r_scale = self._r_scale(z)          # vectorized: no per-point Python loop on the hot path
        xi = np.abs(b) / r_scale
        bad = xi > self.xi_max
        if np.any(bad):
            if clamp:
                xi = np.clip(xi, 0.0, self.xi_max)
            else:
                raise ValueError(
                    f"ClippedBeam: b outside the tabulated radial window at some z "
                    f"(max xi asked {float(np.max(xi)):.3f} > xi_max={self.xi_max}); pass "
                    f"clamp=True or widen xi_max")
        return z, xi

    # --------------------------------------------------------------------------------- public API

    def u(self, b_m: ArrayLike, z_m: ArrayLike, clamp: bool = False) -> ArrayLike:
        """I(b, z) / I_peak_focus, dimensionless, I_peak_focus = I(0, 0) exactly (a tabulated node,
        no interpolation on the normalisation itself). `b_m` is a radius (its sign is dropped);
        broadcasts like numpy. `clamp=True` clips an out-of-window query to the table's edge instead
        of raising -- for a prediction-band envelope, never for a fit (mirrors
        `lineshape.aperture_onaxis_factor_actual`'s own `clamp_floor`)."""
        b = np.asarray(b_m, dtype=float)
        z = np.asarray(z_m, dtype=float)
        bb, zz = np.broadcast_arrays(b, z)
        shape = bb.shape
        zc, xi = self._to_table_coords(zz.reshape(-1), bb.reshape(-1), clamp=clamp)
        val = np.maximum(self._spline.ev(zc, xi), 0.0).reshape(shape)
        out = val / self._i_peak
        return float(out) if shape == () else out

    def w(self, z_m: ArrayLike, clamp: bool = False) -> ArrayLike:
        """The 1/e^2 radius of the profile at z, normalised to ITS OWN on-axis value there (never
        to the global peak) -- see the module docstring for why this and not the second moment."""
        z = np.asarray(z_m, dtype=float)
        shape = z.shape
        zc = self._bounds_check_z(z.reshape(-1), clamp=clamp)
        out = self._w_interp(zc).reshape(shape)
        return float(out) if shape == () else out

    def actual_focus_m(self) -> float:
        """`w(0.0)`, an exact tabulated node (no interpolation): this beam's actual (same-reading)
        1/e^2 focal radius, the quantity `constants.W0_CENTRAL_M` names and
        `lineshape.aperture_onaxis_factor_actual` takes as its argument."""
        return float(self._w1e2_of_z[self.n_z // 2])

    def onaxis_per_watt(self) -> float:
        """I(0, 0) in the same "per recorded (transmitted) watt" convention as
        `lineshape.aperture_onaxis_factor_actual`: divide by a Gaussian's own 2/(pi w^2) at
        `actual_focus_m()` to read that factor back (this module's own test (b))."""
        return self._i_peak

    def second_moment_radius_m(self, z_m: float) -> float:
        """sqrt(2 <r^2>(z)), calibrated so a pure Gaussian (m2=1, no clipping) returns the SAME
        number as `w(z)` (verified: for I proportional to exp(-2 r^2/w^2), <r^2> = w^2/2). This is
        the radius the M2 algebra in the module docstring is written in terms of, and it is what
        makes an LG(p,0) mode's own second moment equal (2p+1) w_fund^2 exactly.

        F104's CAVEAT CARRIED FORWARD: under clipping, a hard aperture's focal rings put weight at
        large r, so this moment depends on where the quadrature is cut and was RETRACTED there for
        exactly that reason. This module's own tests use it only in the unclipped regime, where no
        such tail exists; a caller reading it under clipping is reading a grid-dependent number and
        should read `w(z)` instead unless the M2 algebra specifically is what is wanted.
        """
        z = float(z_m)
        r_grid = self._radial_grid(z)
        I_row = self._mixture_intensity(z, r_grid)
        num = trapezoid(I_row * r_grid ** 3, r_grid)
        den = trapezoid(I_row * r_grid, r_grid)
        return math.sqrt(2.0 * num / den)

    def on_axis_exact(self, z_m: ArrayLike) -> ArrayLike:
        """I(0, z) / I_peak_focus by a FRESH quadrature at each z (never the table), for validating
        the table itself or for a root-find (`axial_half_intensity_depth_m`) that should not
        compound the table's own interpolation error into its answer. Accepts a scalar or a 1-D
        array of z."""
        z = np.asarray(z_m, dtype=float)
        shape = z.shape
        zf = z.reshape(-1)
        out = np.array([self._mixture_intensity(float(zi), np.array([0.0]))[0] for zi in zf])
        out = (out / self._i_peak).reshape(shape)
        return float(out) if shape == () else out


def axial_half_intensity_depth_m(beam: ClippedBeam, n_scan: int = 400) -> float:
    """HALF the z-range over which the on-axis intensity I(0, z) stays at or above half of I(0, 0)
    -- i.e. the ONE-SIDED depth, averaged over both sides of the peak -- by `beam.on_axis_exact`
    (never the table): a coarse scan of `beam._z_nodes` for a bracket on each side of the peak
    (I(0, z) need not be exactly symmetric under clipping -- the aperture's own focal-shift physics
    can tilt it, and this function does not assume symmetry, though it reports one averaged number),
    then `scipy.optimize.brentq` on each side for the crossing.

    THE CONVENTION IS THE REFERENCE COMPUTATION'S, not the more obvious "full width": for an unclipped Gaussian
    of Rayleigh range zR, I(0, z) = I0 / (1 + (z/zR)^2) crosses one half exactly at z = zR, so the
    FULL width is 2 zR -- but the independent computation's own quoted reference number for a Gaussian at the
    owner's 42.4 um reading is 5.69 mm, which is zR itself (this module's own 2 pi w^2/lambda at
    that radius is 11.37 mm, exactly double), so their "depth" is the one-sided distance. Reproduces
    the independent computation's finding at the 2.46 mm input
    (`private/cache/plan_2026-09-16/FINDINGS_NIGHT.md` F281): this module's own number is read out
    and compared, not hard-coded -- a disagreement is a finding, not something to paper over
    (`private/cache/plan_2026-09-18/beam_field_report.md`)."""
    from scipy.optimize import brentq

    z_lo, z_hi = float(beam._z_nodes[0]), float(beam._z_nodes[-1])
    z_scan = np.linspace(z_lo, z_hi, n_scan)
    u_scan = beam.on_axis_exact(z_scan)
    i_peak = int(np.argmax(u_scan))

    def f(z: float) -> float:
        return float(beam.on_axis_exact(z)) - 0.5

    # left crossing: walk left from the peak until u drops below 0.5
    left = None
    for j in range(i_peak, 0, -1):
        if u_scan[j] >= 0.5 > u_scan[j - 1]:
            left = brentq(f, z_scan[j - 1], z_scan[j])
            break
    right = None
    for j in range(i_peak, len(z_scan) - 1):
        if u_scan[j] >= 0.5 > u_scan[j + 1]:
            right = brentq(f, z_scan[j], z_scan[j + 1])
            break
    if left is None or right is None:
        raise ValueError(
            "axial_half_intensity_depth_m: the half-intensity crossing was not bracketed inside "
            "the tabulated window; widen z_span_zr")
    return 0.5 * (right - left)


def shift_density(beam, half_window_m: float, x_grid: ArrayLike, n_photon: int = 2,
                  n_z: int = 161, n_r: int = 3001, r_cut_w: float = 8.0,
                  rate=None) -> np.ndarray:
    """The shift density over the COLLECTED VOLUME for any beam answering `u` and `w` (F368).

    `lineshape.local_ramp_density` is the transverse law of a GAUSSIAN, `n x^(n-1)`, and
    `lineshape.ramp_mixture` then mixes it axially through `S(zeta) = s0 / (1 + zeta^2)`, which is
    the Gaussian's on-axis law. Behind a hard bore neither holds: the transverse profile carries
    rings and the axial profile is flatter and NOT symmetric about the focal plane (its maximum sits
    off it). So this returns the density of the local shift fraction `u = I / I_peak` over the whole
    collected volume in ONE object, which `ramp_mixture` consumes at `z_ratio = 0` ("the local
    density itself") with no further axial mixing, because the axial mixing is already in here.

    The measure is the one the kernel Monte Carlo samples: `z` uniform over the collection window,
    the transverse plane on its area element `2 pi r dr` (the chord measure `db dl` integrates to it
    for a radially symmetric beam), and each element weighted by the `n_photon`-photon excitation
    rate `u ** n_photon`. Normalised to unit area on `x_grid`, exactly as `local_ramp_density` is,
    so the two are interchangeable at the same call site.

    `r_cut_w` is in units of the LOCAL radius and is deliberately wider than the Monte Carlo's own
    `B_CUT`: a Gaussian holds 2.3e-16 of the two-photon weight past three radii and the clipped
    field holds 2.4e-4, because its rings fall as a power and not as an exponential.
    """
    x = np.asarray(x_grid, float)
    z = (np.linspace(-half_window_m, half_window_m, int(n_z)) if half_window_m > 0
         else np.zeros(1))
    edges = np.concatenate([[0.0], 0.5 * (x[1:] + x[:-1]), [max(1.0, float(x[-1]))]])
    acc = np.zeros(x.size)
    for zi in z:
        w_loc = float(beam.w(zi, clamp=True))
        r = np.linspace(0.0, r_cut_w * w_loc, int(n_r))
        u = np.clip(np.asarray(beam.u(r, np.full_like(r, zi), clamp=True), float), 0.0, None)
        # `rate` is the SATURATED excitation rate when the caller has one, so saturation rides
        # with the beam rather than being a separate correction; u ** n_photon is its weak limit.
        wt = (np.asarray(rate(u), float) if rate is not None else u ** int(n_photon)) * r
        # trapezoidal mass per radial cell, deposited in the bin its own u falls in
        cell = 0.5 * (wt[1:] + wt[:-1]) * np.diff(r)
        idx = np.clip(np.searchsorted(edges, 0.5 * (u[1:] + u[:-1]), side="right") - 1, 0, x.size - 1)
        np.add.at(acc, idx, cell)
    width = np.gradient(x)
    dens = acc / np.where(width > 0, width, 1.0)
    area = float(np.trapezoid(dens, x))
    if not (area > 0):
        raise ValueError("shift_density: the beam deposited no weight; check half_window_m and the grid")
    return dens / area


def shift_moments(beam, half_window_m: float, n_photon: int = 2,
                  n_z: int = 401, n_r: int = 6001, r_cut_w: float = 8.0,
                  rate=None) -> dict:
    """The same object's mean, variance and third central moment BY DIRECT QUADRATURE, with no
    binning, so the density above can be checked against it (they agree to the grid's rounding).

    This is what the kernel gate's model side reads: `ramp_mixture_moments` exists to do this for a
    density that must first be built, and for a beam the quadrature is one step shorter and exact.
    """
    z = (np.linspace(-half_window_m, half_window_m, int(n_z)) if half_window_m > 0
         else np.zeros(1))
    n = s1 = 0.0
    rows = []
    for zi in z:
        w_loc = float(beam.w(zi, clamp=True))
        r = np.linspace(0.0, r_cut_w * w_loc, int(n_r))
        u = np.clip(np.asarray(beam.u(r, np.full_like(r, zi), clamp=True), float), 0.0, None)
        wt = (np.asarray(rate(u), float) if rate is not None else u ** int(n_photon)) * r
        rows.append((r, u, wt))
        n += float(np.trapezoid(wt, r)); s1 += float(np.trapezoid(wt * u, r))
    m = s1 / n
    var = k3 = 0.0
    for r, u, wt in rows:
        var += float(np.trapezoid(wt * (u - m) ** 2, r))
        k3 += float(np.trapezoid(wt * (u - m) ** 3, r))
    return {"mean": m, "var": var / n, "k3": k3 / n}


def effective_transit_radius(beam, half_window_m: float, rate=None, n_photon: int = 2,
                             n_z: int = 401) -> float:
    """The radius the TRANSIT kernel should be handed at each z, rate-weighted over the window.

    A chord's transit width goes as v / w(z), so the collected width is set by the rate-weighted mean
    of 1/w and the effective radius is `<weight> / <weight / w>`. The model's own
    `fullmodel.transit_collection_factor` computes exactly this for a beam that diverges as
    `w0 sqrt(1 + (z/z_R)^2)`, which the bore-clipped beam does NOT: its depth of focus is about 1.55
    times the Gaussian's of the same waist, so across the collection window it stays narrow while the
    model's beam opens up.

    This was derived as the cause of the transit reading's four per cent (F374, 2026-09-23)
    and predicted 1.0408 for the clipped-over-Gaussian width ratio at the record's focus, against
    1.0408 measured on eleven conditions of the corrected Monte Carlo. The chord KERNEL is not the
    problem -- evaluating the propagated field along a crossing against a Gaussian of the same local
    radius gives 0.9993 rate-weighted, a tenth of a per cent that changes sign across the window --
    so what is wrong is the `w` that kernel is handed, and this is the one substitution that fixes it.
    """
    z = (np.linspace(-half_window_m, half_window_m, int(n_z)) if half_window_m > 0
         else np.zeros(1))
    num = den = 0.0
    for zi in z:
        w_loc = float(beam.w(zi, clamp=True))
        u0 = float(np.asarray(beam.u(np.zeros(1), np.array([zi]), clamp=True), float)[0])
        wt = float(rate(np.array([u0]))[0]) if rate is not None else u0 ** int(n_photon)
        num += wt
        den += wt / w_loc
    return float(num / den)
