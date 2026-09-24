"""The non-convolving joint per-path line: the atom sampler, the beam interface, the two-time
correlation spectrum, and its fast tabulated form.

WHY (owner order O45, 2026-09-21, re-sent as O46, 2026-09-22: "the model and the twin has to
deal with the non convolving model directly ... in particular the TWIN"). The fitted line today
(`lineshape.model_profile`) is a CONVOLUTION of a light-shift profile with one transit kernel
and a Lorentzian, three independent factors. Across the collected volume an atom's light shift
and its transit width are correlated -- both are set by where it crosses the diverging beam, so
a convolution throws that pairing away before it averages. `results/kernel_inhomogeneity.csv`
measures the cost: the third cumulant wrong by about a factor of two at the bench's 42.38 um
waist (`constants.W0_CENTRAL_M`). Three findings of 2026-09-16/21
(`private/cache/plan_2026-09-16/FINDINGS_NIGHT.md`) built and measured the replacement:

  F290 -- the kernel gate's own Monte Carlo agreement is EVEN by construction (no light shift in
          it), so it never tests the joint where the convolution actually fails.
  F293 -- the joint per-path two-time line (dephasing carried per atom, atom-sampled over the
          diverging beam) disagrees with the convolution exactly where the programme reads: the
          EVEN orders at wide windows (mu4 at 13 MHz over 1 archive-sd at 62 per cent of the 32
          nodes tested), while the odd orders stay under the noise. RE-READ by F318 (2026-09-22):
          that joint arm carried the Lorentzian inside each atom's own transform, whose wing
          error (F317, below at `joint_spectrum`) made the disagreement. At F293's own pre-wave
          node (42 um, 130 C, 225 mW) the line built in the order below agrees with the
          convolution within 0.24 archive sd at every window from 2 to 21 MHz, where F293's arm
          read +3.6 sd on mu4 at 13 MHz. The other 31 nodes are re-read by the same harness.
  F294 -- the joint line separates EXACTLY (Wiener-Khinchin + the convolution theorem) into a
          coherent (dephasing-free) table convolved with the homogeneous Lorentzian and the
          laser Gaussian AFTER interpolation, so a fast, tabulated form is both affordable and
          faster per evaluation than the convolution it replaces (0.145 ms against 1.666 ms for
          `p18_joint_line.convolution_line`, the fitter's own construction, at the prototype's
          own settings).

This module is those two prototypes -- `private/cache/plan_2026-09-16/p18_joint_line.py`
(`joint_spectrum`) and `p18_joint_table.py` (the table, `fast_model_eval`) -- PROMOTED into the
package, per the task that ordered this file: their own formulae are ported verbatim where the
physics is concerned (the two-time correlation's FFT recipe, the atom sampler), generalised only
at the ONE seam the promotion needs: a `Beam` interface (see `GaussianBeam`) in place of a
hardcoded Gaussian divergence, so `rb5s6s/beam_field.py`'s bore-clipped propagated beam (built
separately, to the SAME interface) can serve every function here unchanged.

WEAK FIELD ONLY, throughout. `joint_spectrum` is the coherent-amplitude, two-time-correlation
(first-order, linear-response) line: a(t) = u_b(t) g(t) exp(i phi(t)), phi the light shift's
accumulated phase. A saturated, depleting atom needs an optical-Bloch population carried along
the same trajectory -- a different, several-times-more-expensive calculation -- which is why the
prototypes' own measurement of the regime (dephasing-times-chord-time of order unity, but
shift-times-chord-time only 0.03-0.31 rad across the L's 32-node band) reads the weak-field
line as a reasonable first cut and DEFERS the saturated arm; so does this module. See
`private/cache/plan_2026-09-18/volume_line_report.md` for what is deferred and why.

THE RAMP'S SIDE is read once, from `lineshape.RAMP_SIDE`, and never restated (owner order O27):
every function below that needs the sign of the AC-Stark chirp takes it as a `sign=RAMP_SIDE`
default rather than a literal.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Callable, Optional, Tuple

import numpy as np
from scipy.signal import fftconvolve

from ._compat import trapezoid
from .constants import K_B_J_PER_K, LAMBDA_LASER_M, M_RB85_KG, M_RB87_KG
from .lineshape import RAMP_SIDE, gaussian, lorentzian

__all__ = [
    "GaussianBeam", "collection_half_window_m", "sample_atoms", "joint_spectrum", "JointTable",
    "B_CUT", "TAU_EDGE", "N_TAU",
]

#: Impact parameters sampled out to this many beam radii. PORTED from
#: `scripts/run_kernel_mc.py`'s own `B_CUT = 3.0` (same physical meaning, same value).
B_CUT = 3.0
TAIL_FRACTION = 0.20          # the mixture proposal's uniform component (F372)
B_CUT_CLIPPED = 8.0           # a clipped beam's rings fall as a POWER, so three radii
                              # truncate 2.4e-4 of the two-photon weight against 2.3e-16
                              # for a Gaussian; 8.0 matches `beam_field.shift_density`

#: The per-atom chord's half-span and point count, in the dimensionless units `genv = exp(-2
#: tau^2)` sets (tau = 0 at the chord's own centre). THESE ARE `p18_joint_line.py`'s OWN CHOICES,
#: not `run_kernel_mc.py`'s: that module's `_chord` uses the same dimensionless chord variable
#: for the saturated RATE integral alone, at TAU_EDGE=3.0/N_TAU=41 (module docstring there); the
#: two-time correlation this module builds needs more range and resolution for its own FFT/
#: interpolation floor to stay small (measured in `p18_joint_line.py`'s own convergence check,
#: `private/cache/plan_2026-09-18/joint_line_readme.md`: doubling N_TAU moves mu12 at the widest
#: window by 3.3 per cent, the ceiling on the highest, tail-sensitive cells).
TAU_EDGE = 6.0
N_TAU = 301

#: THE HOMOGENEOUS WIDTHS ARE APPLIED AFTER THE ENSEMBLE SUM, on an internal grid symmetric about zero
#: with this step (MHz) and reaching this far beyond the widest detuning asked for (F317, 2026-09-22).
#: The margin must hold the coherent line's own reach, so a Lorentzian evaluated at every offset an
#: output point needs is exact: the transit line is a few MHz wide at the waists of this record and its
#: wings are negligible long before 40 MHz.
HOMOG_STEP_MHZ = 0.01
HOMOG_MARGIN_MHZ = 40.0


class GaussianBeam:
    """The default beam: a diverging Gaussian TEM00, M2 carried through the Rayleigh range.

        w(z)    = w0 * sqrt(1 + (z/z_R)^2),          z_R = pi * w0^2 / (M2 * lambda)
        u(b, z) = (w0 / w(z))^2 * exp(-2 b^2 / w(z)^2)

    `u` is the on-axis-referenced peak intensity factor I/I_peak_focus a chord at impact
    parameter b and axial position z sees at its own closest approach -- exactly
    `scripts/run_kernel_mc.py`'s own `_sample`'s `u_b` ("the chord's peak, on-axis focus = 1"),
    ported here as a method so a different beam can return the same quantity its own way.

    THE BEAM INTERFACE, stated once because `rb5s6s/beam_field.py` (a bore-clipped, propagated
    beam, built separately) implements it too: a beam is any object exposing

        w(z_m)      -> the local 1/e^2 field radius (m) at axial position z_m, array-safe
        u(b_m, z_m) -> the local peak intensity factor I/I_peak_focus at impact parameter b_m
                       and axial position z_m, array-safe, broadcasting b_m against z_m

    `sample_atoms` and `joint_spectrum` below call ONLY these two methods on a `beam` argument,
    so a beam that carries the EOM bore's diffraction and the actual (same-reading) on-axis
    factor (`lineshape.aperture_onaxis_factor_actual`) drops in unchanged; this class does not
    model the bore at all and is the interface's plain reference implementation.

    `z_R_m` is this class's OWN convenience attribute, not part of the two-method interface
    above: a caller turning a dimensionless collection ratio z_ratio = Z/z_R
    (`fullmodel.collection_z_ratio_m2`'s own convention) into a physical half-window reads it
    from here (`collection_half_window_m`, below). A beam without one well-defined Rayleigh
    range needs its own convention for that conversion.
    """

    def __init__(self, w0_m: float, m2: float = 1.0, lambda_m: float = LAMBDA_LASER_M):
        if not (float(w0_m) > 0.0):
            raise ValueError(f"GaussianBeam: w0_m must be positive, got {w0_m!r}")
        if not (float(m2) >= 1.0):
            # M^2 >= 1 is physics, not a fit bound (fullmodel.collection_z_ratio_m2's own guard,
            # F... : no real beam is better than diffraction-limited).
            raise ValueError(
                f"GaussianBeam: m2={m2!r} is below the diffraction limit; M^2 = 1 IS the ideal "
                "beam and no real beam is better than one.")
        self.w0_m = float(w0_m)
        self.m2 = float(m2)
        self.lambda_m = float(lambda_m)
        self.z_R_m = math.pi * self.w0_m ** 2 / (self.m2 * self.lambda_m)

    def w(self, z_m):
        z_m = np.asarray(z_m, dtype=float)
        return self.w0_m * np.sqrt(1.0 + (z_m / self.z_R_m) ** 2)

    def u(self, b_m, z_m):
        w = self.w(z_m)
        b_m = np.asarray(b_m, dtype=float)
        return (self.w0_m / w) ** 2 * np.exp(-2.0 * b_m ** 2 / w ** 2)

    def __repr__(self) -> str:
        return f"GaussianBeam(w0_m={self.w0_m!r}, m2={self.m2!r}, lambda_m={self.lambda_m!r})"


def collection_half_window_m(beam: "GaussianBeam", z_ratio: float) -> float:
    """`z_ratio * beam.z_R_m`: the collected column's physical half-length, z_ratio the
    dimensionless collection ratio Z/z_R (`fullmodel.collection_z_ratio_m2`'s own convention,
    not reimported here so this module stays independent of the fitter's collection-optics
    constants -- the caller supplies z_ratio). Defined only for a beam exposing `z_R_m`
    (`GaussianBeam`'s own convenience attribute, not part of the two-method beam interface);
    a beam without one raises rather than guessing."""
    if not hasattr(beam, "z_R_m"):
        raise AttributeError(
            "collection_half_window_m needs a beam exposing z_R_m (GaussianBeam's own "
            f"convenience attribute); {type(beam).__name__} has none, so pass half_window_m "
            "directly instead")
    return float(z_ratio) * float(beam.z_R_m)


def sample_atoms(rng: np.random.Generator, n: int, beam, T_C: float, half_window_m: float, *,
                 isotope: int = 87, b_cut: float = B_CUT,
                 ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """The flux-weighted, axially-sampled atom ensemble a focused two-photon beam sees in
    steady state.

    PORTED from `scripts/run_kernel_mc.py`'s `_sample` (the guard kernel-mc producer, owner
    order 2026-09-16 22:30), generalised over a `beam` object (see `GaussianBeam` and its
    docstring's "THE BEAM INTERFACE") in place of the hardcoded Gaussian divergence
    `w = w0 sqrt(1+(z/z_R)^2)`, so the identical sampling recipe serves any beam implementing
    `.w(z_m)` and `.u(b_m, z_m)` -- in particular a future bore-clipped propagated beam
    (`rb5s6s/beam_field.py`). At `beam = GaussianBeam(w0_m, m2)` this reproduces `_sample`'s own
    numbers exactly: identical RNG draw order (z, then b, then v) and identical arithmetic.

    z is uniform over the collected column [-half_window_m, half_window_m] (every atom at z=0
    when half_window_m <= 0, a point-beam degenerate case); the local beam radius is
    `beam.w(z)`. The impact parameter b is drawn from the WEAK FIELD's own half-normal weight
    exp(-4 b^2 / w^2) rather than uniformly in area -- a uniform draw leaves five atoms in six
    with negligible weight, `_sample`'s own 2026-09-16 finding (F11) -- cut at `b_cut` beam
    radii; the importance factor `w * exp(4 b^2 / w^2)` restores the chords-are-uniform-in-
    impact-parameter measure of an isotropic gas. The transverse speed v is drawn from its own
    target half-normal density (not the Maxwellian directly, the same importance-sampling
    repair), the flux's own extra power of v folded into `flux_len`. `beam.u(b, z)` is the
    chord's own peak intensity factor (I / I_peak_at_focus), exactly what `_sample` calls `u_b`.

    Returns (w, v, u_b, flux_len), each shape (n,): the local beam radius (m), the transverse
    speed (m/s), the peak intensity factor, and the (unnormalised) crossing-flux weight.
    """
    n = int(n)
    m = M_RB87_KG if int(isotope) == 87 else M_RB85_KG
    sv = math.sqrt(K_B_J_PER_K * (float(T_C) + 273.15) / m)
    z0 = rng.uniform(-half_window_m, half_window_m, n) if half_window_m > 0 else np.zeros(n)
    w = np.asarray(beam.w(z0), dtype=float)
    # THE PROPOSAL IS A MIXTURE FOR ANY BEAM THAT IS NOT A GAUSSIAN (F372/F376, 2026-09-23). The
    # half-normal `e^{-4 b^2 / w^2}` with the restoring factor `w e^{+4 b^2 / w^2}` leaves FLAT
    # weights only because the two-photon rate carries `e^{-4 b^2 / w^2}` of its own and cancels it
    # EXACTLY. Behind a bore the rate falls as a POWER, the cancellation fails, and at three radii
    # the weight is `e^{36}`, about 4e15, against a rate that is no longer exponentially small: the
    # estimator's variance is UNBOUNDED. This sampler already accepted any beam and still carried
    # the Gaussian-only device, so every clipped-beam world built on it -- `joint_spectrum`,
    # `JointTable`, the twin's own `VolumeWorld` -- was drawing from a proposal that does not cover
    # its target. A uniform component fixes it and the weight is one over the MIXTURE density.
    #
    # A GAUSSIAN BEAM DOES NOT EVEN DRAW THE SELECTOR, so its random stream stays bit-identical to
    # the one this function had before and `test_sample_atoms_matches_scripts_run_kernel_mc` is a
    # plant on the change rather than a tolerance around it.
    gaussian = isinstance(beam, GaussianBeam)
    cut = float(b_cut) if gaussian else max(float(b_cut), B_CUT_CLIPPED)
    r_max = cut * w
    sig_b = w / (2.0 * math.sqrt(2.0))
    if gaussian:
        b = np.minimum(np.abs(rng.normal(0.0, 1.0, n)) * sig_b, r_max)
        imp_b = w * np.exp(4.0 * b ** 2 / w ** 2)
    else:
        pick = rng.random(n) < TAIL_FRACTION
        b = np.where(pick, rng.random(n) * r_max,
                     np.minimum(np.abs(rng.normal(0.0, 1.0, n)) * sig_b, r_max))
        p_core = math.sqrt(2.0 / math.pi) / sig_b * np.exp(-0.5 * (b / sig_b) ** 2)
        imp_b = 1.0 / ((1.0 - TAIL_FRACTION) * p_core + TAIL_FRACTION / r_max)
    v = np.maximum(np.abs(rng.normal(0.0, sv, n)), 1e-9 * sv)
    u_b = np.asarray(beam.u(b, z0), dtype=float)
    flux_len = v * imp_b * v
    return w, v, u_b, flux_len


def joint_spectrum(*, S0_mhz: float, gamma_hom_mhz: float, beam, T_C: float,
                   half_window_m: float, n_path: int, seed: int, delta_mhz: np.ndarray,
                   n_tau: int = N_TAU, tau_edge: float = TAU_EDGE,
                   sigma_laser_mhz: float = 0.0, sign: float = RAMP_SIDE,
                   isotope: int = 87, homog_step_mhz: float = HOMOG_STEP_MHZ,
                   homog_margin_mhz: float = HOMOG_MARGIN_MHZ) -> np.ndarray:
    """The joint per-path line: the two-time correlation with dephasing, atom-sampled over an
    axially divergent beam. PORTED verbatim (the FFT/correlation recipe unchanged) from
    `private/cache/plan_2026-09-16/p18_joint_line.py`'s `joint_spectrum`, merged with that
    file's `joint_spectrum_with_laser` extension (`p18_joint_table.py`) as one optional Gaussian
    decay factor that is an exact no-op at `sigma_laser_mhz=0` (see below) -- the module docstring
    above cites F290/F293/F294, the findings that measured why this replaces a convolution and
    that it separates exactly into a table (this line at `gamma_hom_mhz=0`) convolved afterwards.

    THE HOMOGENEOUS WIDTHS ARE APPLIED ONCE, AFTER THE ENSEMBLE SUM (F317, 2026-09-22). The atoms
    give the COHERENT line (no dephasing, no laser); when `gamma_hom_mhz` or `sigma_laser_mhz` is
    non-zero that line is computed on an internal grid symmetric about zero (`homog_step_mhz`,
    reaching `homog_margin_mhz` beyond the widest detuning asked for), convolved there with the
    Lorentzian and then the laser's Gaussian, and interpolated onto `delta_mhz`. Wiener-Khinchin
    and the convolution theorem make this EXACTLY the line with the decay carried inside every
    atom's correlation (F294), because the decay is common to every atom. What the order decides
    is the numerics. Carried inside each atom's own transform, as this function did until
    2026-09-22, the Lorentzian is sampled on that atom's own band, +-1/(2 dt), which ends near 15
    MHz for the slow atoms: their wings were cut beyond it and folded back inside it, one bin more
    on one side than the other. Measured at the archive's corner with no light shift, over +-30
    MHz: a third moment of -0.072 MHz^3 where the line is symmetric and the value is zero, and a
    variance 4 per cent above the transit-kernel convolution's, both stable from 4 000 to 64 000
    atoms. It was the "separability floor" of 0.86 to 1.5 per cent of peak the earlier tests
    calibrated to, and it carried F293's wide-window disagreement with the convolution (F318).

    PER ATOM (own w, v, u_b, flux weight, all `sample_atoms`'s own draws): on the shared
    dimensionless chord grid tau in [-tau_edge, tau_edge], the coherent excitation amplitude

        a(t) = u_b * exp(-2 tau^2) * exp(i phi(t)),
        phi(t) = sign * 2 pi S0_mhz*1e6 * u_b * cumsum(exp(-2 tau^2)) * dt,   dt = (w/v) dtau,

    (`sign` read from `lineshape.RAMP_SIDE` by default, never restated). Its two-time
    correlation C(tau) = a (correlate) a, via a circular-autocorrelation-via-FFT trick
    (`ifft(|fft(a, n2)|^2)`, zero-padded, trimmed to the LINEAR correlation window), is the
    atom's coherent spectrum's transform. The Lorentzian of FWHM `gamma_hom_mhz` and the
    Gaussian of FWHM `sigma_laser_mhz` (`lineshape.lorentzian` and `lineshape.gaussian`, both in
    their FWHM convention) are applied to the sum, as the paragraph above says; at zero width
    each is skipped, a true no-op and not a small-width approximation.

    THE FREQUENCY EVALUATION IS AN FFT-THEN-INTERPOLATE, not a direct matmul onto `delta_mhz`:
    every atom has its own dt = (w/v)*dtau (w differs per atom once z is sampled), so no single
    shared frequency-domain operator exists across atoms; a second FFT gives each atom's own
    spectrum on ITS OWN natural (dt-set) frequency axis in O(n2 log n2), and `np.interp` onto the
    shared `delta_mhz` grid is O(n_delta) -- both cheap (measured 190x faster than the direct
    matmul in the prototype this was ported from). The cost is that a spectral feature narrower
    than an atom's own frequency spacing 1/(n2*dt) is smeared by the interpolation; doubling
    `n_tau` (halving each atom's own dt, doubling its frequency resolution) and reporting the
    movement is the record's convention for this floor (see this module's tests).

    Returns `spec`, UNNORMALISED (units of MHz^-1 x atoms' flux weight) -- the caller normalises
    (an overall constant factor does not move a windowed CENTRAL moment,
    `rb5s6s.cumulants.windowed_moments`, at all).
    """
    delta_mhz = np.asarray(delta_mhz, dtype=float)
    gamma_hom_mhz, sigma_laser_mhz = float(gamma_hom_mhz), float(sigma_laser_mhz)
    if gamma_hom_mhz > 0.0 or sigma_laser_mhz > 0.0:
        step = float(homog_step_mhz)
        half = int(np.ceil((float(np.max(np.abs(delta_mhz))) + float(homog_margin_mhz)) / step))
        grid = np.linspace(-half * step, half * step, 2 * half + 1)       # symmetric: the kernels centre
        line = joint_spectrum(S0_mhz=S0_mhz, gamma_hom_mhz=0.0, beam=beam, T_C=T_C,
                              half_window_m=half_window_m, n_path=n_path, seed=seed, delta_mhz=grid,
                              n_tau=n_tau, tau_edge=tau_edge, sigma_laser_mhz=0.0, sign=sign,
                              isotope=isotope)
        dnu = grid[1] - grid[0]
        if gamma_hom_mhz > 0.0:
            line = fftconvolve(line, lorentzian(grid, gamma_hom_mhz), mode="same") * dnu
        if sigma_laser_mhz > 0.0:
            line = fftconvolve(line, gaussian(grid, sigma_laser_mhz), mode="same") * dnu
        return np.interp(delta_mhz, grid, line, left=0.0, right=0.0)
    rng = np.random.default_rng(seed)
    w, v, u_b, flux_len = sample_atoms(rng, int(n_path), beam, T_C, half_window_m, isotope=isotope)

    tau = np.linspace(-tau_edge, tau_edge, n_tau)
    dtau = tau[1] - tau[0]
    genv = np.exp(-2.0 * tau ** 2)
    cs = np.cumsum(genv)
    n2 = 1 << int(np.ceil(np.log2(2 * n_tau - 1)) + 1)

    spec = np.zeros_like(delta_mhz)
    for i in range(w.shape[0]):
        dt = (w[i] / v[i]) * dtau
        phi = sign * 2.0 * math.pi * float(S0_mhz) * 1e6 * u_b[i] * cs * dt
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
        spec += flux_len[i] * np.interp(delta_mhz, freq_hz[order] / 1e6, np.real(S[order]), left=0.0, right=0.0)
    return spec


class JointTable:
    """The fast form of `joint_spectrum`: a table of the COHERENT (gamma_hom=0, no laser) line
    M_coh over a (S0, w0) grid at one fixed (M2, T_C), convolved with the homogeneous Lorentzian
    and the laser Gaussian AT EVALUATION TIME rather than baked in.

    LICENSED BY F294's separability measurement: multiplying the per-atom correlation by
    exp(-gamma_hom |tau|) (and, if present, the laser's Gaussian decay), the SAME gamma_hom and
    sigma_laser for every atom, commutes with the ensemble sum (Wiener-Khinchin + the
    convolution theorem), so the line with the widths carried inside every atom's correlation
    EQUALS the coherent line convolved with Lorentzian(g) then Gaussian(s). `joint_spectrum` itself
    applies the widths in that order since F317 (2026-09-22), so this table and a direct call agree
    to floating point at a table node. The 0.86 per cent of peak the prototype read as the
    construction's "discretisation floor" was the per-atom route's wing error (F317), not a floor of
    the physics or of this table. WEAK
    FIELD ONLY: a saturated atom's dephasing becomes intensity-dependent (power broadening), so
    gamma_hom would no longer be common to every atom and this separability would not hold; the
    saturated arm is out of scope here (module docstring).

    `profile(nu_mhz, s0_mhz, w0_m, gamma_hom_mhz, sigma_laser_mhz)` MATCHES
    `lineshape.model_profile`'s own axis and normalisation convention: `gamma_hom_mhz` and
    `sigma_laser_mhz` are BOTH FWHM (never sigma -- `lineshape.gaussian`'s own convention,
    `model_profile`'s `sigma_laser_fwhm` despite its name), the internal table grid is
    interpolated and convolved on `self.delta_mhz`, then `np.interp`-resampled onto the
    CALLER's `nu_mhz` with zero outside the table's own span (`left=0.0, right=0.0`, exactly
    `model_profile`'s own `np.interp(nu, g, prof, left=0.0, right=0.0)`), and area-normalised by
    `trapezoid` OVER `nu_mhz` ITSELF (not over the internal grid) -- so, exactly as in
    `model_profile`, a `nu_mhz` that does not cover the table's full span returns a profile whose
    area over the GIVEN axis is 1, not over the whole line.
    """

    def __init__(self, *, S0_grid: np.ndarray, w0_grid: np.ndarray, table: np.ndarray,
                delta_mhz: np.ndarray, m2: float, T_C: float, n_path: int, seed: int,
                z_ratio: float):
        self.S0_grid = np.asarray(S0_grid, dtype=float)
        self.w0_grid = np.asarray(w0_grid, dtype=float)
        self.table = np.asarray(table, dtype=float)
        self.delta_mhz = np.asarray(delta_mhz, dtype=float)
        if self.table.shape != (self.S0_grid.size, self.w0_grid.size, self.delta_mhz.size):
            raise ValueError(
                f"JointTable: table shape {self.table.shape} does not match "
                f"(n_S0={self.S0_grid.size}, n_w0={self.w0_grid.size}, "
                f"n_delta={self.delta_mhz.size})")
        if self.S0_grid.size < 2 or self.w0_grid.size < 2:
            raise ValueError("JointTable: both S0_grid and w0_grid need at least two points "
                             "for bilinear interpolation")
        if not (np.all(np.diff(self.S0_grid) > 0) and np.all(np.diff(self.w0_grid) > 0)):
            raise ValueError("JointTable: S0_grid and w0_grid must both ascend strictly")
        self.m2 = float(m2)
        self.T_C = float(T_C)
        self.n_path = int(n_path)
        self.seed = int(seed)
        self.z_ratio = float(z_ratio)

    @classmethod
    def build(cls, *, S0_grid: np.ndarray, w0_grid: np.ndarray, delta_mhz: np.ndarray,
             m2: float, T_C: float, n_path: int, seed: int = 0, z_ratio: float = 0.6,
             n_tau: int = N_TAU, tau_edge: float = TAU_EDGE,
             beam_factory: Optional[Callable[[float], object]] = None,
             isotope: int = 87) -> "JointTable":
        """Build M_coh(delta; S0, w0) for one condition (fixed M2, T_C): `joint_spectrum` at
        `gamma_hom_mhz=0, sigma_laser_mhz=0` (the coherent line) on every (S0, w0) grid node, ONE
        FIXED seed for the whole table (not one per node): S0 does not enter the atom sampler at
        all (only w0, m2, T_C do -- `sample_atoms`), so a shared seed makes the table a smooth,
        common-random-numbers-coupled function of (S0, w0) rather than adding fresh Monte Carlo
        roughness at every node, which is what keeps bilinear interpolation between nodes
        accurate at a modest grid (F294's own reading: interpolation error is measured
        n_path-independent for exactly this reason).

        `beam_factory(w0_m) -> beam` builds the beam for each w0 grid point (default
        `GaussianBeam(w0_m, m2)`); overriding it can point the table at a different beam
        implementing the same interface (`GaussianBeam`'s docstring), but `z_ratio` must then
        make sense for that beam's own geometry -- `collection_half_window_m` needs `z_R_m`.
        """
        S0_grid = np.asarray(S0_grid, dtype=float)
        w0_grid = np.asarray(w0_grid, dtype=float)
        delta_mhz = np.asarray(delta_mhz, dtype=float)
        if beam_factory is None:
            beam_factory = lambda w0_m: GaussianBeam(float(w0_m), float(m2))  # noqa: E731
        table = np.empty((S0_grid.size, w0_grid.size, delta_mhz.size), dtype=float)
        for j, w0v in enumerate(w0_grid):
            beam = beam_factory(float(w0v))
            half_window_m = collection_half_window_m(beam, z_ratio)
            for i, s0v in enumerate(S0_grid):
                table[i, j] = joint_spectrum(
                    S0_mhz=float(s0v), gamma_hom_mhz=0.0, beam=beam, T_C=T_C,
                    half_window_m=half_window_m, n_path=n_path, seed=seed, delta_mhz=delta_mhz,
                    n_tau=n_tau, tau_edge=tau_edge, sigma_laser_mhz=0.0, isotope=isotope)
        return cls(S0_grid=S0_grid, w0_grid=w0_grid, table=table, delta_mhz=delta_mhz, m2=m2,
                  T_C=T_C, n_path=n_path, seed=seed, z_ratio=z_ratio)

    def _bilinear(self, s0q: float, w0q: float) -> np.ndarray:
        """Bilinear interpolation of the tabulated M_coh curve in (S0, w0); out-of-range queries
        clip to the nearest edge CELL (not edge VALUE extrapolation beyond it -- the same
        behaviour `np.searchsorted` plus a clipped cell index gives the prototype this is ported
        from, `p18_joint_table.bilinear_curve`)."""
        S0g, w0g, table = self.S0_grid, self.w0_grid, self.table
        n_s0, n_w0 = S0g.size, w0g.size
        i = int(np.clip(np.searchsorted(S0g, s0q) - 1, 0, n_s0 - 2))
        j = int(np.clip(np.searchsorted(w0g, w0q) - 1, 0, n_w0 - 2))
        ts = (s0q - S0g[i]) / (S0g[i + 1] - S0g[i])
        tw = (w0q - w0g[j]) / (w0g[j + 1] - w0g[j])
        c00, c10, c01, c11 = table[i, j], table[i + 1, j], table[i, j + 1], table[i + 1, j + 1]
        return (1 - ts) * (1 - tw) * c00 + ts * (1 - tw) * c10 + (1 - ts) * tw * c01 + ts * tw * c11

    def profile(self, nu_mhz: np.ndarray, s0_mhz: float, w0_m: float, gamma_hom_mhz: float,
               sigma_laser_mhz: float = 0.0) -> np.ndarray:
        """The fast model evaluation: interpolate M_coh, then convolve with the homogeneous
        Lorentzian and the laser Gaussian by FFT (both applied AFTER interpolation, in
        frequency space, never baked into the table -- this class's own docstring names the
        separability finding that licenses the order). Matches `lineshape.model_profile`'s axis
        and normalisation convention; see this class's docstring for exactly what and why."""
        nu_mhz = np.asarray(nu_mhz, dtype=float)
        m_coh = self._bilinear(float(s0_mhz), float(w0_m))
        dnu = self.delta_mhz[1] - self.delta_mhz[0]
        spec = m_coh
        gamma_hom_mhz = float(gamma_hom_mhz)
        sigma_laser_mhz = float(sigma_laser_mhz)
        if gamma_hom_mhz > 0.0:
            spec = fftconvolve(spec, lorentzian(self.delta_mhz, gamma_hom_mhz), mode="same") * dnu
        if sigma_laser_mhz > 0.0:
            spec = fftconvolve(spec, gaussian(self.delta_mhz, sigma_laser_mhz), mode="same") * dnu
        prof = np.interp(nu_mhz, self.delta_mhz, spec, left=0.0, right=0.0)
        area = trapezoid(prof, nu_mhz)
        return prof / area if area > 0 else prof

    def save(self, path) -> None:
        """Save as a single `.npz` (compressed): the grids, the table, the internal frequency
        axis, and the scalar provenance (`m2`, `T_C`, `n_path`, `seed`, `z_ratio`). A table built
        with a non-default `beam_factory` does not record that choice -- the caller's own
        bookkeeping, outside this class, same as any lookup table's build recipe."""
        np.savez_compressed(Path(path), S0_grid=self.S0_grid, w0_grid=self.w0_grid,
                            table=self.table, delta_mhz=self.delta_mhz, m2=self.m2, T_C=self.T_C,
                            n_path=self.n_path, seed=self.seed, z_ratio=self.z_ratio)

    @classmethod
    def load(cls, path) -> "JointTable":
        """The inverse of `save`."""
        with np.load(Path(path)) as d:
            return cls(S0_grid=d["S0_grid"], w0_grid=d["w0_grid"], table=d["table"],
                      delta_mhz=d["delta_mhz"], m2=float(d["m2"]), T_C=float(d["T_C"]),
                      n_path=int(d["n_path"]), seed=int(d["seed"]), z_ratio=float(d["z_ratio"]))
