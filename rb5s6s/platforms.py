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

  2. **The observable is not always fluorescence.** In a cell one collects 420
     nm photons against a dark background. In a fibre one usually measures the
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
    collection_eff: float = 0.162     # the cell's measured solid-angle fraction
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
#: 993.4 nm put 6S at 20133 cm^-1 and the 420 nm line puts 6P at 23714, so 6P
#: is 3581 cm^-1 ABOVE it. The record names the right cascade on three
#: surfaces, including `constants.TAU_5P12_S`'s own docstring, which this
#: module imports: 6S to 5P1/2 to 5S, collected at 795 nm.
#:
#: **AND 6P IS STILL REACHED, by blackbody EXCITATION rather than by decay**
#: (owner, 2026-09-11). `results/blackbody_channels.csv` measures the 6S to 6P
#: transfer at 44.30 per second at 130 C and calls it the largest blackbody
#: channel out of 6S. Against the 6S decay rate of 2.194e7 per second that is a
#: branch of **2.0 parts per million**, so the 420 nm photon is real and rare.
#: It is the branch and not the level ordering that keeps the leg out of a
#: cycle time: a route taken two millionths of the time cannot set one.
#:
#: The consequence is that the ceiling this constant sets **cannot bind**. At
#: 73.27 ns the cycle-limited rate is 1.365e7 per atom per second, above the
#: two-level steady state's own ceiling at every power, so `cascade_cap_binds`
#: is False everywhere and the capped and uncapped rates agree. The first
#: form's error was one-sided, a dead time too long lowering a rate, so every
#: affected row read conservative and no comparison against the archive's own
#: row could have caught it.
CASCADE_DEAD_TIME_S = C.TAU_6S_S + C.TAU_5P12_S


def cycle_limited_rate_per_s() -> float:
    """The most excitations one atom can complete per second."""
    return 1.0 / CASCADE_DEAD_TIME_S


def excitation_rate_per_atom(power_w: float, p: Platform,
                             rho: float = 0.94) -> float:
    """6S productions per atom per second.

    The two-level steady state gives `Gamma_pop rho_ee`, which tends to half
    the 6S decay rate under strong driving. **That limit is not reachable**,
    because a 6S atom does not return to 5S when it decays: it cascades
    through the 6P manifold or 5D and then 5P, and is unavailable for the whole
    journey. The cascade dead time caps the rate, and the cap BINDS at this
    record's tight-waist configurations, where the saturation parameter is of
    order ten and the uncapped form overstates the rate by about a factor of
    two. It does not bind at the archive's own waist, where the saturation
    parameter is 0.033 and the uncapped rate is thirty times below the cap.
    """
    uncapped = GAMMA_POP_PER_S * excited_fraction(power_w, p, rho)
    return float(min(uncapped, cycle_limited_rate_per_s()))


def signal_and_noise(power_w: float, p: Platform, integration_s: float,
                     rho: float = 0.94,
                     background_cps: float = 6000.0) -> Dict[str, float]:
    """Detected signal, its noise, and the resulting SNR, per detection mode.

    FLUORESCENCE. A 6S decay reaches the ground state through 5P, and the leg
    this bench collects is the 795 nm 5P1/2 to 5S photon (methods chapter 1,
    and the filters named in the apparatus page). The 420 nm line is 5S to 6P
    and lies ABOVE 6S, so it is not a 6S decay route; a 5D or 7S programme
    would collect it and this one does not.
    So the detected rate is the excitation rate times the branching,
    the collection solid angle and the quantum efficiency. The noise is the
    shot noise of signal plus background.

    ABSORPTION. Each excitation removes TWO probe photons. The observable is
    the fractional dip in transmitted power, and its noise is the shot noise of
    the FULL transmitted beam, so the SNR is the dip times the square root of
    the detected photon number. This is the mode that a fibre uses and it
    scales quite differently: the dip does not care how bright the probe is,
    while the shot noise improves as its square root.
    """
    n_at = atoms_in_probe(p)
    rate = excitation_rate_per_atom(power_w, p, rho)
    events_per_s = rate * n_at
    t_eff = integration_s * p.duty_cycle
    photon_energy = H_PLANCK_JS * C_M_PER_S / 993.4e-9
    flux = power_w / photon_energy                      # probe photons per second

    if p.detection == "fluorescence":
        det = events_per_s * p.collection_eff * p.detector_qe
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
        note="the tight-waist campaign proposal, outside three approximations"),
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
