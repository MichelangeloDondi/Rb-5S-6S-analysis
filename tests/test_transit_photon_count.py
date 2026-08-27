"""The transit kernel's exponent carries the TWO-photon count, checked numerically.

WHY THIS EXISTS. On 2026-08-26 an outside reading of `rb5s6s/transit_mc.py`
concluded that the per-atom lineshape

    P_atom(nu) ∝ exp(-(2 pi nu)^2 w^2 / (4 v^2))

used the ONE-photon envelope while its `I_pk^2` prefactor used the
two-photon rate, and that the transit width was therefore a factor sqrt(2)
narrow, 0.96 MHz where it should read 1.35 at 130 C. The claim was specific,
it named the committed constant, and it was WRONG. It was also entirely
reasonable to make, which is why this file exists.

THE ERROR, because naming it is what stops it recurring. The two-photon
AMPLITUDE is the transform of the coupling, a(Delta) = FT[Omega_2(t)] with
Omega_2 proportional to intensity, and that transform is
exp(-Delta^2 w^2 / 8 v^2). That is the number the reading quoted. But the
OBSERVABLE is a probability, P = |a|^2, and squaring returns
exp(-Delta^2 w^2 / 4 v^2), which is what the module has. A forgotten square,
not a missing geometry factor.

The direction seals it. The one-photon case, amplitude proportional to the
FIELD, gives |FT(E)|^2 = exp(-Delta^2 w^2 / 2 v^2), which is NARROWER than
the module's exponent. So the module is already the two-photon result and is
broader, because I^2 confines excitation toward the beam centre and shortens
the crossing. A reading that the module used the one-photon envelope
predicts a width in the wrong direction.

WHY A TEST AND NOT A COMMENT. The module's docstring already said
"two-photon", and the reading still landed the other way, because the
docstring says "amplitude" a few lines above an expression that is a
probability. A comment is read by the same eye that misread the docstring.
The Lehmann NNO validation cannot close it either: that is a single-beam
Doppler-broadened problem, so it constrains the functional form, the flux
weighting and the constants, and a two-photon geometry factor is outside
its reach. This test is in the geometry's reach, and it is the thing to
cite when the question is asked again.
"""
from __future__ import annotations

import numpy as np


def _power_spectrum_exponent_coefficient(envelope, t, dt, w=1.0, v=1.0):
    """Fit C in |FT(envelope)|^2 ∝ exp(-(2 pi f)^2 w^2 / (C v^2))."""
    amp = np.fft.fftshift(np.fft.fft(envelope)) * dt
    freq = np.fft.fftshift(np.fft.fftfreq(len(envelope), dt))
    power = np.abs(amp) ** 2
    power = power / power.max()
    keep = (power > 1e-6) & (freq != 0)
    coeff = -((2 * np.pi * freq[keep]) ** 2 * w**2) / (v**2 * np.log(power[keep]))
    return float(np.median(coeff))


def _grid():
    t = np.linspace(-40.0, 40.0, 1 << 18)
    return t, float(t[1] - t[0])


def test_the_two_photon_lineshape_is_the_modules_exponent():
    """|FT(I)|^2 -> exp(-(2 pi nu)^2 w^2 / 4 v^2), which transit_mc.py has."""
    t, dt = _grid()
    intensity = np.exp(-2.0 * t**2)          # I ∝ exp(-2 r^2 / w^2), w = v = 1
    c = _power_spectrum_exponent_coefficient(intensity, t, dt)
    assert abs(c - 4.0) < 0.02, (
        f"the two-photon per-atom lineshape returns 1/{c:.3f} where the "
        f"module's exponent is 1/4. If this moved, transit_mc.py's PHYSICS "
        f"paragraph and constants.transit_fwhm_from_w0 disagree with the "
        f"transform they claim.")


def test_the_one_photon_lineshape_is_narrower_not_wider():
    """The direction check that refutes the one-photon-envelope reading."""
    t, dt = _grid()
    field = np.exp(-1.0 * t**2)              # E ∝ sqrt(I)
    c_one = _power_spectrum_exponent_coefficient(field, t, dt)
    assert abs(c_one - 2.0) < 0.02, f"one-photon coefficient {c_one:.3f}, expected 2"
    # a smaller coefficient is a faster fall-off, so a NARROWER line
    assert c_one < 4.0, (
        "the one-photon lineshape must be narrower than the two-photon one. "
        "A reading that the module uses the one-photon envelope predicts a "
        "WIDER correct answer, which is the wrong direction.")


def test_the_amplitude_spectrum_is_not_the_lineshape():
    """The exact step the 2026-08-26 reading skipped, pinned as its own case."""
    t, dt = _grid()
    intensity = np.exp(-2.0 * t**2)
    amp = np.fft.fftshift(np.fft.fft(intensity)) * dt
    freq = np.fft.fftshift(np.fft.fftfreq(len(intensity), dt))
    a = np.abs(amp) / np.abs(amp).max()
    keep = (a > 1e-6) & (freq != 0)
    c_amp = float(np.median(-((2 * np.pi * freq[keep]) ** 2) / np.log(a[keep])))
    assert abs(c_amp - 8.0) < 0.05, f"amplitude coefficient {c_amp:.3f}, expected 8"
    # and squaring it is exactly the observable
    c_power = _power_spectrum_exponent_coefficient(intensity, t, dt)
    assert abs(c_amp / c_power - 2.0) < 0.02, (
        "the amplitude spectrum is exp(-D^2 w^2 / 8 v^2) and the observable "
        "is its square, exp(-D^2 w^2 / 4 v^2). Quoting the first as the "
        "lineshape is a factor sqrt(2) in the transit width.")
