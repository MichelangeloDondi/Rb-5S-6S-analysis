"""
M19 -- does atomic motion wash out the AC-Stark ramp?

The composite model (rb5s6s.lineshape.model_profile) treats the ramp and the
transit lineshape as two independent factors that convolve. Read literally,
that looks like it cannot be right, because the two describe the SAME atom
crossing the SAME beam:

  * `stark_ramp` derives its triangular weight by assuming each atom sits at
    one intensity and therefore carries one fixed shift s = -k I -- a
    QUASI-STATIC picture with the atom nailed in place;
  * `transit_mc` derives its width from the atom MOVING through the beam, and
    puts every atom's line at nu = 0, with no shift in it at all.

An atom crossing the waist sees its own light shift sweep from ~0 up to its
on-axis maximum and back down within the transit time. Camparo and
Lambropoulos (JOSA B 9, 2163 (1992)) is the reason to take this seriously: for
a two-photon transition in a fluctuating field they show the lineshape depends
on whether the field varies slowly or quickly compared with the atomic
response -- slow (adiabatic) fluctuations give an asymmetric line, fast ones
average away to a symmetric line at the mean shift. Their variation is in
time and ours is in space, but an atom in flight converts one into the other,
and in this cell the two timescales are comparable. At the MEASURED 64 um
waist (constants.W0_MEASURED_M; this line said ~50 um until 2026-08-10, from
the estimate the lineage measurement replaced) an atom takes w0/v ~ 260 ns to
cross one waist radius, or 520 ns for the full beam diameter, against a natural
response time of 1/(2 pi Gamma_FWHM) = 45.6 ns. The transverse speed here is
the 2D Maxwell-Boltzmann mean, sigma_v sqrt(pi/2) = 246 m/s at 130 C.
That is not a comfortable separation, and "the asymmetry survives motion" is
therefore an assumption, not an obvious truth.

THE RESULT: it survives exactly, and the factorization is legitimate.

The reason is a change of variables, not a cancellation. Write the atom's
transverse position as its impact parameter b and its displacement along the
flight direction v*t. Those two coordinates ARE the transverse plane, and
db d(vt) IS the area element. A uniform-density ensemble weighted by crossing
flux therefore samples exactly the uniform 2D spatial measure that the static
derivation integrates over. Since the two-photon signal weights by I^2 in both
pictures, and the shift is the same function of I in both, the I^2-weighted
DISTRIBUTION OF SHIFTS sampled by the moving ensemble is identical, moment for
moment, to the one sampled by the static ensemble. Motion re-labels which atom
contributes which shift; it does not change the distribution over shifts.

What that argument does not cover is non-adiabaticity: it assumes the atom's
spectrum reflects the shifts it samples, which is the quasi-static limit
Camparo warns about. So the claim is checked WITHOUT that assumption here, by
propagating the weak-excitation amplitude

    A(nu) = integral Omega_2ph(t) exp(i[2 pi nu t - phi(t)]) dt,
    phi(t) = 2 pi integral^t delta(t') dt',   Omega_2ph ~ I(t),  delta = -S0 I(t),

for each trajectory and summing |A|^2 over impact parameters. No quasi-static
step is taken: the phase is integrated along the path. The first two moments
come out at the static triangle's values to ~0.1% across S0/transit_FWHM from
0.09 to 7.6 -- i.e. from far inside the non-adiabatic regime to far inside the
adiabatic one (see tests/test_ramp_transit.py).

The invariance of the FIRST moment is stronger than a numerical coincidence:
the mean of a power spectrum is the coupling-weighted mean instantaneous
frequency for any modulation, adiabatic or not. The second moment matching is
the substantive check, and it is what licenses the convolution.

WHAT ELSE THE REAL GEOMETRY THROWS AT IT. The beam is retro-reflected, so it
is a standing wave with lambda/2 fringes; the atoms carry a Maxwell-Boltzmann
velocity distribution; and the shift is inhomogeneous in three dimensions, not
one. Each is checked below, and the pull survives all three:

  * STANDING WAVE. The fringe modulates the SHIFT (which follows the total
    |E+ + E-|^2 over the full lambda/2 period) but NOT the coupling (the
    Doppler-free rate takes one photon from each beam, so it goes as I+ * I-
    and is z-uniform). Both limits give the triangle: fringes swept fast by an
    axial atom (~113 per transit at the experiment's ~0.56 GHz against a ~5 MHz
    transit rate), and the frozen fringe of a near-transverse atom sampled over
    the node-antinode arcsine. That is an independent confirmation of the
    fringe-immunity of the mean asserted in `constants` and quantified in M15 --
    which bounds the fringe's effect on the SKEW, a different and non-null
    question this module does not address.
  * MAXWELL-BOLTZMANN. Only the ratio S0/(v/w) enters, so the sweep over
    S0/transit_FWHM below IS a sweep over transverse speed spanning ~80x, which
    brackets the thermal distribution. Every speed class shares one mean and one
    ramp variance and differs only in transit width, so any mixture inherits
    both; verified directly against a flux-weighted Maxwell-Boltzmann sample.

SCOPE. Transverse crossing of a slice of constant w; the axial (z_ratio)
beam-divergence weighting is `lineshape.stark_ramp_axial` and the fringe's
suppression of the third cumulant is `fringe_tail` (M15) -- neither is
re-derived here. Third and higher cumulants are NOT resolved by this simulation -- the
numerical noise floor of the FFT, weighted by nu^3, swamps kappa_3 -- so the
change-of-variables argument is the only support for the odd cumulants above
the first, and it carries the quasi-static assumption. kappa_3 is the moment the asymmetry claim rests on.
"""

from __future__ import annotations

import numpy as np

# Static-triangle benchmarks the moving ensemble must reproduce (n_photon = 2,
# pure transverse). Derived in lineshape.stark_ramp / stark_ramp_axial_moments.
TRIANGLE_MEAN_OVER_S0 = -2.0 / 3.0
TRIANGLE_EXCESS_VAR_OVER_MEAN_SQ = 0.125


def moving_atom_moments(s0: float, *, n_b: int = 501, n_t: int = 60001,
                        t_max: float = 10.0, b_max: float = 3.2,
                        nu_window: float | None = None,
                        fringe_per_transit: float = 0.0,
                        frozen_fringe_phases: int = 0,
                        speeds: "np.ndarray | None" = None) -> dict:
    """First two moments of the line from atoms CROSSING the beam, with the
    light shift integrated along each trajectory.

    Units are the beam's own: waist w = 1, transverse speed v = 1, so `s0` (the
    on-axis maximum shift) is measured against the transit scale v/w, and the
    pure-transit FWHM is ~0.53 in these units. Returns the mean in units of s0
    and the EXCESS variance (transit contribution subtracted) in units of the
    mean squared -- the two quantities `ramp_moment_contributions` predicts.

    `fringe_per_transit` adds the RETRO standing wave: the atom's axial motion
    carries it through lambda/2 fringes, modulating its shift by 2 cos^2 at a
    rate set by v_z. 0 is the frozen-fringe limit (a near-transverse atom parked
    at one point of the node-antinode pattern, sampled over the arcsine); the
    experiment's fast-axial atoms sit near ~113 (2 v_z/lambda ~ 0.56 GHz against
    a ~4 MHz transit rate at the adopted w0 = 64 um). Both limits preserve the mean, which
    is the fringe-immunity that `constants` asserts and M15 quantifies.

    `speeds` supplies a distribution of transverse speeds to mix over -- pass a
    Maxwell-Boltzmann sample for the real ensemble. Mixing is cheap to justify
    but is checked anyway: every speed class shares the same mean and the same
    ramp variance, differing only in transit width, so the mixture inherits
    both. (Note the sweep in the tests over s0/transit_FWHM IS a sweep over
    transverse speed, since only that ratio enters.)

    `nu_window` bounds the moment integration. It is not cosmetic: the FFT's
    ~1e-16 noise floor, weighted by nu^2 out to the Nyquist frequency, is
    comparable to the signal's own second moment, so an unwindowed variance is
    dominated by numerical noise (observed: 0.238 instead of 0.125). The
    default tracks the line's actual support.
    """
    t = np.linspace(-t_max, t_max, n_t)
    dt = t[1] - t[0]
    nu = np.fft.fftshift(np.fft.fftfreq(n_t, dt))
    bs = np.linspace(0.0, b_max, n_b)

    vs = np.array([1.0]) if speeds is None else np.asarray(speeds, float)
    # frozen fringe: a static multiplier 2 cos^2(phi), phi uniform over the
    # standing-wave period -- the arcsine sampling of M15's fringe-RESOLVED tail
    phis = (np.array([0.0]) if frozen_fringe_phases <= 0 else
            (np.arange(frozen_fringe_phases) + 0.5) * np.pi / frozen_fringe_phases)

    def spectrum(shift: float) -> np.ndarray:
        """The fringe enters the SHIFT but not the COUPLING, and getting that
        backwards is the easy mistake (it was made once here, and showed up as a
        5/3 inflation of the frozen-fringe pull). The Doppler-free two-photon
        rate takes one photon from each counter-propagating beam, so it goes as
        I+ * I- and carries NO z-modulation; the ac-Stark shift goes as the
        total |E+ + E-|^2 and is modulated over the full lambda/2 period. So
        `couple` is the bare envelope while `shift_env` carries the fringe."""
        tot = np.zeros(n_t)
        for v in vs:
            for phi in phis:
                for b in bs:
                    couple = np.exp(-2.0 * (b * b + (v * t) ** 2))
                    shift_env = couple
                    if frozen_fringe_phases > 0:
                        # atom parked at one fringe phase (small v_z): a static
                        # multiplier of unit mean over the arcsine
                        shift_env = shift_env * 2.0 * np.cos(phi) ** 2
                    if fringe_per_transit > 0.0:
                        # atom sweeping through fringes at the axial crossing
                        # rate: unit-mean modulation of the shift only
                        shift_env = shift_env * 2.0 * np.cos(
                            np.pi * fringe_per_transit * v * t) ** 2
                    phase = 2.0 * np.pi * np.cumsum(-shift * shift_env) * dt
                    amp = np.fft.fftshift(
                        np.fft.fft(couple * np.exp(-1j * phase))) * dt
                    tot += np.abs(amp) ** 2
        return tot

    win = 4.0 + 3.0 * abs(s0) if nu_window is None else nu_window
    keep = np.abs(nu) < win

    def moments(tot: np.ndarray) -> tuple[float, float]:
        p = tot[keep] / tot[keep].sum()
        x = nu[keep]
        m1 = float((x * p).sum())
        return m1, float(((x - m1) ** 2 * p).sum())

    _, var_transit = moments(spectrum(0.0))
    m1, var = moments(spectrum(s0))
    # the simulation's nu axis runs opposite to the physical detuning (numpy's
    # forward FFT carries exp(-2 pi i nu t) against the exp(+i 2 pi nu t) of the
    # amplitude above), so the physical red shift is -m1
    mean_over_s0 = -m1 / s0
    return {"mean_over_s0": mean_over_s0,
            "excess_var": var - var_transit,
            "excess_var_over_mean_sq": (var - var_transit) / (m1 * m1),
            "transit_fwhm": 2.3548 * np.sqrt(var_transit)}
