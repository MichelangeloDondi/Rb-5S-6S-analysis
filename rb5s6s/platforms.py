"""Where the atoms are, and how the signal leaves: the platform layer.

WHY THIS MODULE EXISTS (2026-09-10). `forecast.build_world_trace` takes every
width and rate as an explicit argument, which is right, and it means nothing in
the package says what those arguments ARE for a magneto-optical trap, a
molasses, or a hollow-core fibre. Every cold or guided number in the record has
so far been an extrapolation of a warm-cell world builder. This module supplies
the parameters and, more importantly, the two things a warm cell never forced
anyone to separate:

  1. **The interaction length is not the Rayleigh range in a guided mode.** A
     free Gaussian beam concentrates a two-photon rate (which goes as the
     intensity SQUARED) within about one Rayleigh range of its focus, so the
     effective length is `min(z_R, cell, cloud)`. A guided mode does not
     diverge, so its effective length is the FIBRE, centimetres against a
     millimetre. That single fact is why hollow-core spectroscopy works at all
     and it is worth more than any other term here.

  2. **The observable is not always fluorescence.** In a cell one collects the
     795 nm D1 leg of the 6S to 5P to 5S cascade against a dark background --
     NOT 420 nm, which this paragraph said until 2026-09-11 and which is 5S to
     6P, a level ABOVE 6S and no decay route out of it (the same mistake as
     escapes E46 and E47, surviving here because those swept the docs and this
     module's own head was outside their population). In a fibre one usually measures the
     TRANSMITTED probe, so the signal is a small dip in a large number and the
     noise is the shot noise of the full beam rather than of the signal. The
     two detection modes have different scalings in atom number and in power,
     and comparing platforms without saying which one is meant is meaningless.

FAILURE MODES THIS MODULE WILL NOT PROTECT YOU FROM. The densities and
temperatures of the trapped platforms are DESIGN FIGURES, not measurements of
any apparatus in this record, and they are tagged ENVELOPE wherever they reach
a CSV. Nothing here models loading, trap lifetime, or the radial heating that
`Rb87-clock-EIT-infiber-cooling` names as its own open chapter. The absorption
arm assumes a shot-noise-limited detector and no technical intensity noise,
which is the optimistic end and is stated as such: a real transmission
measurement is usually limited by laser intensity noise long before shot noise,
and that is the first thing to add.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np

from . import constants as C
from .hyperpolarizability import two_photon_rabi_hz
from .detection import ir_branching_5p12, mean_5p_lifetime_s
from ._compat import trapezoid  # the seam, never the numpy name

H_PLANCK_JS = 6.62607015e-34
C_M_PER_S = 2.99792458e8
KB_J_PER_K = 1.380649e-23

#: Population decay rate of 6S, in 1/s. Gamma_nat is a FWHM in Hz, so the
#: population rate is 2 pi times it. tau = 45.57 ns inverts to the same number.
GAMMA_POP_PER_S = 2.0 * np.pi * C.GAMMA_NAT_HZ


@dataclass(frozen=True)
class Platform:
    """One place to put atoms, with the detection chain that reads them.

    `length_m` is the PHYSICAL extent available (cell, cloud diameter, or fibre
    length). The effective interaction length is computed, never stored, since
    it depends on the waist through the Rayleigh range for every free-space
    platform.
    """

    name: str
    kind: str                 # cell | mot | molasses | hcpcf | onf
    temperature_k: float
    density_cm3: float
    w0_m: float
    length_m: float
    duty_cycle: float
    detection: str            # fluorescence | absorption
    guided: bool
    # NOT A SOLID ANGLE, which this line called it until 2026-09-11.
    # `results/prediction_band.csv` derives 0.162 as `2 arctan(z_ratio) / pi`,
    # the fraction of the emitted fluorescence inside the COLLECTION WINDOW the
    # cathode and the lens define, at the archive's waist. So the detected rate
    # carries an axial window and NO solid angle: the record has never measured
    # one, which `docs/plan/12` now carries as an open item. Two consequences
    # are stated rather than buried: the absolute fluorescence rows are upper
    # bounds by whatever that solid angle is, and the fraction is computed on
    # the ramp's axial weight rather than on the saturated rate's, so applying
    # it to the profile integral is an approximation of its own. It rides
    # unchanged on the trapped and guided rows, where the window is not what
    # limits the collection at all.
    collection_eff: float = 0.162
    detector_qe: float = 0.15
    note: str = ""


def rayleigh_range_m(w0_m: float, lam_m: float = 993.4e-9) -> float:
    """z_R of a free Gaussian beam. Meaningless for a guided mode, which is
    why `effective_length_m` branches on `guided` before calling this."""
    return np.pi * w0_m ** 2 / lam_m


def effective_length_m(p: Platform) -> float:
    """The length that actually contributes to a two-photon rate.

    Free space: the rate goes as I^2, so it falls to a quarter one Rayleigh
    range from the focus and the sample is truncated by whichever of the
    Rayleigh range, the cell and the cloud is shortest. Guided: the mode does
    not diverge, so the fibre length is the answer and z_R never enters.
    """
    if p.guided:
        return p.length_m
    return float(min(rayleigh_range_m(p.w0_m), p.length_m))


def probe_volume_m3(p: Platform) -> float:
    """pi w0^2 times the effective length. The same convention as the record's
    other volume estimates, so the numbers compare."""
    return float(np.pi * p.w0_m ** 2 * effective_length_m(p))


def atoms_in_probe(p: Platform) -> float:
    return float(p.density_cm3 * 1e6 * probe_volume_m3(p))


def excited_fraction(power_w: float, p: Platform, rho: float = 0.94) -> float:
    """Steady-state 6S population on resonance, saturation included.

    rho_ee = s/2 / (1 + s) with s = 2 (Omega/Gamma)^2, which tends to one half
    and NOT to one. The weak-field form Omega^2/Gamma^2 is wrong by more than a
    factor of two wherever this record's tight-waist configurations sit: the
    saturation parameter there is of order ten.
    """
    omega_hz = two_photon_rabi_hz(power_w, p.w0_m, rho)
    s = 2.0 * (omega_hz / C.GAMMA_NAT_HZ) ** 2
    return float(0.5 * s / (1.0 + s))


#: Time an atom spends OUT of 5S after one excitation, before it can be driven
#: again: the 6S lifetime plus the 5P lifetime. **An ATOMIC cycle time, not a
#: detector dead time** (owner, 2026-09-11): this bench's photomultiplier is
#: read in analogue current and has no per-event dead time at all, so the only
#: thing that keeps an atom from being re-driven is the atom itself. The name
#: is kept for continuity and the docstring is the authority.
#:
#: **CORRECTED 2026-09-11, and the first form was not a mis-estimate but the
#: wrong LEVEL.** It read `TAU_6S_S + 120.7e-9 + TAU_5P12_S` with a docstring
#: naming a leg "through 6P", and 6P does not lie below 6S: two photons at
#: 993.4 nm put 6S at 20133 cm^-1, and 6P1/2 sits at 23715 cm^-1, so 6P is
#: **3582 cm^-1 ABOVE** it. **The 23714 written here until 2026-09-11 was a
#: mistyped 23715.081, which is the 421.7 nm line and not the 420 nm one**: the
#: 420 nm line is 6P3/2 at 23792.6, which is 3660 above 6S. Both orderings give
#: the same conclusion and the record should still say which line it means. The record names the right cascade on three
#: surfaces, including `constants.TAU_5P12_S`'s own docstring, which this
#: module imports: 6S to 5P1/2 to 5S, collected at 795 nm.
#:
#: **AND 6P IS STILL REACHED, by blackbody EXCITATION rather than by decay**
#: (owner, 2026-09-11). `results/blackbody_channels.csv` measures the 6S to 6P
#: transfer at 44.30 per second at 130 C and calls it the largest blackbody
#: channel out of 6S. Against the 6S decay rate of 2.194e7 per second that is a
#: branch of **2.0 parts per million**, so the blue photon is real and rare.
#: It is the branch and not the level ordering that keeps the leg out of a
#: cycle time: a route taken two millionths of the time cannot set one.
#:
#: **AND THE CONSTANT IS NOT A CEILING AT ALL**, which is the correction of
#: 2026-09-11 and the second one this constant has needed. Its reciprocal,
#: 1.365e7 per atom per second, is the cycle rate of an atom re-excited the
#: instant it returns, and no drive achieves it; the model took a MINIMUM
#: against it, which never selected, so `cascade_cap_binds` read False on every
#: row while the index sold the column pair as "with and without the cascade
#: dead-time ceiling". What the cascade actually does is renormalise the
#: saturation parameter, `s -> 1.293 s`, and its strong-drive ceiling is
#: `1 / (2 tau_6S + <tau_5P>)` = 8.483e6, twenty-three per cent BELOW the
#: two-level one rather than twenty-four above. So a cascade properly modelled
#: LOWERS every rate. See `cascade_saturation_factor` and
#: `cascade_ceiling_per_s`; this constant survives only as the time an atom is
#: away, which is what its name says and all it is good for.
#:
#: **AND THE 5P LIFETIME IN IT IS THE BRANCHING-WEIGHTED ONE** (2026-09-11).
#: Both the factor and the ceiling first used `TAU_5P12_S` for
#: every decay, and the record's own branching sends two decays in three
#: through 5P3/2 at 26.24 ns. `detection.mean_5p_lifetime_s` is 26.74 ns, which
#: moved the factor from 1.3039, the ceiling from 8.415e6 and this dead time
#: from 73.3 ns to 72.3.
CASCADE_DEAD_TIME_S = C.TAU_6S_S + mean_5p_lifetime_s()


def cascade_saturation_factor() -> float:
    """How much the cascade multiplies the saturation parameter, `1 + t5/2t6`.

    **THE CASCADE IS A RENORMALISATION AND NOT A CAP** (2026-09-11, escape E50
    re-opened). Solve the three-level steady state rather than capping a
    two-level one: the ground-to-excited coherence decays at half the 6S rate
    and the 5P level does not touch it, so with `e -> p` at the 6S rate and
    `p -> g` at the 5P rate the excited population is

        rho_ee = (s/2) / (1 + s (1 + tau_5P / 2 tau_6S))

    which is the two-level form with `s` scaled by this factor. It reduces to
    the two-level expression as `tau_5P -> 0` and to the weak-field limit as
    `s -> 0`, and it takes no minimum of anything.

    With two intermediate levels and branches `b_i` the steady state carries
    `sum b_i tau_i` in place of one lifetime, which is what
    `detection.mean_5p_lifetime_s` returns; the account of why that replaced a
    single lifetime is on `CASCADE_DEAD_TIME_S` and is not repeated here.
    """
    return float(1.0 + mean_5p_lifetime_s() / (2.0 * C.TAU_6S_S))


def cascade_ceiling_per_s() -> float:
    """The strong-drive ceiling of the three-level steady state.

    `Gamma_pop / 2` divided by the saturation factor, which is
    `1 / (2 tau_6S + tau_5P)`. **It lies BELOW the two-level ceiling**, by 23
    per cent on this bench's constants, where the retired `1/(tau_6S+tau_5P)`
    sat 24 per cent ABOVE it. That sign is the whole of the correction: a
    cascade properly modelled lowers every rate, and the retired form lowered
    none.
    """
    return float(1.0 / (2.0 * C.TAU_6S_S + mean_5p_lifetime_s()))


def cycle_limited_rate_per_s() -> float:
    """The most excitations one atom can complete per second."""
    return 1.0 / CASCADE_DEAD_TIME_S


def excitation_rate_per_atom(power_w: float, p: Platform,
                             rho: float = 0.94) -> float:
    """6S productions per atom per second.

    The two-level steady state gives `Gamma_pop rho_ee`, which tends to half
    the 6S decay rate under strong driving. **That limit is not reachable**,
    because a 6S atom does not return to 5S when it decays: it goes to 5P and
    the 5P lifetime follows, so the atom is unavailable for the whole journey.
    The cascade is a RENORMALISATION of the saturation and not a cap: with the
    intermediate level carried, the steady state is
    `rho_ee = (s/2) / (1 + s (1 + tau_5P / 2 tau_6S))` and its strong-drive
    ceiling is `1 / (2 tau_6S + tau_5P)`, which lies BELOW the two-level
    `Gamma_pop / 2`. `cascade_saturation_factor` and `cascade_ceiling_per_s`
    are those two quantities and the test pins both limits from constants.

    **THIS PARAGRAPH DESCRIBED A `min` AND A CEILING THAT NEITHER EXIST**
    (escape E50, and on 2026-09-11 the retired half was found still standing
    after the first repair). It said the ceiling is
    `CASCADE_DEAD_TIME_S`, that it sits ABOVE the two-level ceiling so a `min`
    never selects it, and it named, as the assertion behind all of that, a
    test the cascade commit had deleted along with the `min` itself. It also routed the
    cascade "through the 6P manifold or 5D and then 5P": both legs are
    impossible, 6P lying 3582 wavenumbers ABOVE 6S and 5D above it too at 25700
    wavenumbers, so that leg is closed at every multipole order and not only at
    E1. A docstring naming a deleted test is invisible to every guard here,
    because the population those guards read is `tests/`.

    **AND THE RATE IS ON AXIS.** `two_photon_rabi_hz` uses the on-axis
    intensity `2P / (pi w0^2)`, so this is the rate at the centre of the mode.
    Where the drive saturates the profile average is NOT this number times a
    volume: the wings are unsaturated and carry most of the events. The
    profile integral is `events_per_s`'s business and is computed there.
    """
    omega_hz = two_photon_rabi_hz(power_w, p.w0_m, rho)
    s = 2.0 * (omega_hz / C.GAMMA_NAT_HZ) ** 2
    rho_ee = 0.5 * s / (1.0 + s * cascade_saturation_factor())
    return float(GAMMA_POP_PER_S * rho_ee)


def events_per_s_profile(power_w: float, p: Platform, rho: float = 0.94,
                         cascade: bool = True) -> float:
    """Excitations per second in the whole mode, integrated over its profile.

    **THE ON-AXIS RATE TIMES A CYLINDER IS NOT THIS NUMBER WHERE THE DRIVE
    SATURATES** (2026-09-11). `two_photon_rabi_hz` takes the
    on-axis intensity `2P / (pi w0^2)`, so `excitation_rate_per_atom` is the
    rate at the centre of the mode; multiplying it by every atom in
    `pi w0^2 L_eff` assumes the rate is flat across the beam. It is not: the
    saturated centre is where the rate stops growing and the unsaturated wings
    are where the events are.

    **AND THE FACTOR OF FIVE AT THE TIGHT ROW IS NOT THAT MECHANISM**
    (2026-09-11). Decomposed by axis, the radial saturation integral alone,
    over the SAME axial window the conventional volume uses, moves that row to
    0.69 -- the other direction. The five is the removal of the `min(z_R, L)`
    truncation: the conventional volume counts 0.81 mm of a 50 mm cell there,
    and the quadrature counts all of it. Three surfaces attributed the five to
    the wings, and a reader who reproduced the radial integral would have got
    0.69 and concluded the module was broken.

    The integral is analytic in the radial coordinate. With `u = exp(-4r^2/w^2)`
    the two-photon saturation parameter is `s = s_ax (w0/w)^4 u`, and

        int 2 pi r dr (s/2) / (1 + f s) = (pi w^2 / 8f) ln(1 + f s_ax (w0/w)^4)

    exactly, with `f` the cascade's saturation factor. The axial integral is a
    quadrature over the PHYSICAL sample length, which is what replaces the
    `min(z_R, L)` truncation the conventional volume uses: the truncation is
    the approximation this integral exists to remove.

    Weak drive reduces it to a quarter of the conventional number for a guided
    mode, since a Gaussian's `I^2` integral is `pi w0^2 / 4` of the on-axis
    value over an area `pi w0^2`. In free space the ratio is
    `z_R atan(L / 2 z_R) / (2 L_eff)`: where the Rayleigh range truncates that
    is `atan(L / 2 z_R) / 2`, and where the CLOUD is the shorter of the two it
    is not, which the trapped rows are and which the shorter form this
    docstring first carried got wrong by a factor of 1.6 on them (2026-09-11).
    """
    omega_hz = two_photon_rabi_hz(power_w, p.w0_m, rho)
    s_ax = 2.0 * (omega_hz / C.GAMMA_NAT_HZ) ** 2
    f = cascade_saturation_factor() if cascade else 1.0
    n_per_m3 = p.density_cm3 * 1e6
    if p.guided:
        radial = np.pi * p.w0_m ** 2 / (8.0 * f) * np.log1p(f * s_ax)
        return float(n_per_m3 * GAMMA_POP_PER_S * radial * p.length_m)
    z_r = rayleigh_range_m(p.w0_m)
    half = 0.5 * p.length_m
    z = np.linspace(-half, half, 4001)
    w2 = p.w0_m ** 2 * (1.0 + (z / z_r) ** 2)
    radial = np.pi * w2 / (8.0 * f) * np.log1p(f * s_ax * (p.w0_m ** 2 / w2) ** 2)
    return float(n_per_m3 * GAMMA_POP_PER_S * trapezoid(radial, z))


def events_per_s_on_axis(power_w: float, p: Platform, rho: float = 0.94) -> float:
    """The retired convention: the on-axis rate times the conventional volume.

    Kept as a column so the move from one to the other is legible in the
    committed table rather than being a silent change of a number, and so the
    ratio of the two is reportable per row.
    """
    return float(excitation_rate_per_atom(power_w, p, rho) * atoms_in_probe(p))


def signal_and_noise(power_w: float, p: Platform, integration_s: float,
                     rho: float = 0.94,
                     background_cps: float = 6000.0) -> Dict[str, float]:
    """Detected signal, its noise, and the resulting SNR, per detection mode.

    FLUORESCENCE. A 6S decay reaches the ground state through 5P, and the leg
    this bench collects is the 795 nm 5P1/2 to 5S photon (methods chapter 1,
    and the filters named in the apparatus page). The 420 nm line is 5S to 6P
    and lies ABOVE 6S, so it is not a 6S decay route; a 5D or 7S programme
    would collect it and this one does not.
    So the detected rate is the PROFILE-INTEGRATED excitation rate times the
    branching, the collection solid angle and the quantum efficiency. The noise
    is the shot noise of signal plus background. Both of those first two
    factors were wrong here until 2026-09-11: the rate was the on-axis one
    times a cylinder of atoms, and the branching was named and never applied.

    ABSORPTION. Each excitation removes TWO probe photons. The observable is
    the fractional dip in transmitted power, and its noise is the shot noise of
    the FULL transmitted beam, so the SNR is the dip times the square root of
    the detected photon number. This is the mode that a fibre uses and it
    scales quite differently: the dip does not care how bright the probe is,
    while the shot noise improves as its square root.
    """
    events_per_s = events_per_s_profile(power_w, p, rho)
    t_eff = integration_s * p.duty_cycle
    photon_energy = H_PLANCK_JS * C_M_PER_S / 993.4e-9
    flux = power_w / photon_energy                      # probe photons per second

    if p.detection == "fluorescence":
        # THE BRANCHING, which this line asserted and did not apply until
        # 2026-09-11. This bench passes 795 nm alone, and only 34.09 per cent
        # of 6S decays take the 5P1/2 leg that ends on it; the other two thirds
        # go through 5P3/2 and out at 780. Omitting it made every fluorescence
        # SNR high by 1/sqrt(0.341) = 1.71 where signal shot noise dominates,
        # which it does at every row here.
        det = (events_per_s * ir_branching_5p12()
               * p.collection_eff * p.detector_qe)
        sig = det * t_eff
        noise = np.sqrt(max(sig + background_cps * t_eff, 1e-30))
        return {"events_per_s": events_per_s, "detected": sig,
                "noise": noise, "snr": sig / noise if noise > 0 else 0.0,
                "absorbed_fraction": np.nan}

    if p.detection == "absorption":
        absorbed_fraction = 2.0 * events_per_s / flux
        detected_photons = flux * p.detector_qe * t_eff
        noise_frac = 1.0 / np.sqrt(max(detected_photons, 1e-30))
        return {"events_per_s": events_per_s, "detected": detected_photons,
                "noise": noise_frac, "snr": absorbed_fraction / noise_frac,
                "absorbed_fraction": absorbed_fraction}

    raise ValueError(f"unknown detection mode {p.detection!r}")


def transit_fwhm_mhz(p: Platform) -> float:
    """The transit width this platform's temperature and waist imply.

    `constants.transit_fwhm_from_w0` takes CELSIUS, which has cost this record
    one wrong table already, so the conversion happens here and once.
    """
    return float(C.transit_fwhm_from_w0(p.w0_m, p.temperature_k - 273.15))


#: The standard set. Densities and temperatures for the trapped platforms are
#: DESIGN FIGURES; the cell's are this record's own measured conditions.
PLATFORMS: Dict[str, Platform] = {
    "cell_130C": Platform(
        "cell_130C", "cell", 403.15, 2.94e13, 64e-6, 0.05, 1.0,
        "fluorescence", False,
        note="the 2025 archive's own conditions, the only measured row here"),
    "cell_130C_tight": Platform(
        "cell_130C_tight", "cell", 403.15, 2.94e13, 16e-6, 0.05, 1.0,
        "fluorescence", False,
        note="the tight-waist campaign proposal, outside the approximations this model rests on"),
    "mot": Platform(
        "mot", "mot", 150e-6, 3e10, 16e-6, 5e-4, 0.01,
        "fluorescence", False,
        note="cloud-limited length. The duty cycle is load against probe window"),
    "molasses": Platform(
        "molasses", "molasses", 20e-6, 1e10, 16e-6, 5e-4, 0.005,
        "fluorescence", False,
        note="colder and thinner than the MOT, and a shorter window"),
    "hcpcf_warm": Platform(
        "hcpcf_warm", "hcpcf", 403.15, 2.94e13, 19e-6, 0.10, 1.0,
        "absorption", True,
        note="vapour-filled kagome mode. The length is the fibre and not z_R"),
    "hcpcf_cold": Platform(
        "hcpcf_cold", "hcpcf", 150e-6, 1e10, 19e-6, 0.01, 0.01,
        "absorption", True,
        note="atoms loaded into the guided mode. Length is the loaded column"),
    # THE NANOFIBRE ROW IS THE CRUDEST HERE AND IS MARKED SO. The atoms sit
    # OUTSIDE the glass in the evanescent tail, so `w0_m` below is an effective
    # mode radius standing in for a field that decays over a few hundred
    # nanometres, and the density is an areal shell recast as a volume. The
    # quantitative treatment is in `rb5s6s.fibre`, which solves HE11 and has
    # `evanescent_intensity`; this row exists so the platform table is not
    # silent about the geometry, not to evaluate it.
    "onf": Platform(
        "onf", "onf", 150e-6, 1e9, 0.4e-6, 0.005, 0.01,
        "absorption", True,
        note="ORDER OF MAGNITUDE ONLY. Atoms sit in the evanescent tail "
             "outside the glass. Use rb5s6s.fibre for anything quantitative"),
}
