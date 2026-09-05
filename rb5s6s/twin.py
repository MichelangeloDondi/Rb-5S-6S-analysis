"""The digital twin: what an instrument would record, for either platform.

WHAT A TWIN OWES. `forecast.synthetic_traces` generates a line and
adds noise, which answers how well an estimator recovers a known truth. It
does not answer the question an acquisition design asks, which is what THIS
instrument at THESE settings would actually store. That needs the point
count the instrument allows, the vertical step its resolution mode gives,
the noise law of the real detector evaluated at each point's own level, the
sample correlation the chain imposes, and, for a four-peak trace, all four
lines on one vertical range at their measured splittings.

TWO PLATFORMS, AND THE BLACKBODY TERM IS WHERE THEY DIFFER MOST.

In the vapour cell the atoms sit inside a heated cell, so the radiation
field they see is the cell's own, and the blackbody shift is evaluated at
the cell temperature, 70 to 130 C.

**On the nanofibre it is not.** The atoms are laser-cooled to microkelvin
and held microns from a fibre that sits in a room-temperature laboratory,
so the radiation field is the room's and NOT the cloud's. Evaluating the
blackbody shift at the atomic temperature would put it at essentially zero
and would be wrong by the whole size of the term. The twin therefore fixes
the nanofibre's radiation temperature at 300 K, independent of the atom
temperature, and refuses to take an atom temperature as a radiation
temperature at all. A microkelvin cloud in a 300 K room carries the 300 K
shift.

WHAT THIS MODULE DELIBERATELY DOES NOT DO. It does not fit. It produces
traces in the form `fit_condition` accepts, so the analysis under test is
the real one, and a twin that carried its own estimator would be grading
its own homework.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np

from . import blackbody, constants as K, instruments as inst
from .noise import sigma_of_v

C_M_S = 299_792_458.0

# Room temperature for a laboratory nanofibre, in kelvin. Not a fitted or
# adjustable quantity in this twin: it is the environment the atoms radiate
# against, and the atom temperature has no bearing on it.
NANOFIBRE_RADIATION_K = 300.0


@dataclass
class Acquisition:
    """One instrument at one set of settings, as a session would write it."""

    instrument: str = "agilent_3054a"
    mode: Optional[str] = None            # None takes the instrument default
    n_points: Optional[int] = None        # None takes the instrument default
    span_mhz: float = 60.0                # half-width for a one-peak trace
    full_scale_v: float = 1.0             # the vertical window
    peak_fraction_of_scale: float = 0.8   # where the line peak sits in it
    n_traces: int = 5
    raw_per_point: int = 1                # boxcar block size, hires only
    tau_int_samples: float = 1.0          # measured sample correlation
    quantise: bool = True

    def resolved(self) -> Tuple[inst.Instrument, inst.ResolutionMode, int]:
        ins = inst.get(self.instrument)
        mode = ins.mode(self.mode)
        n = self.n_points or ins.default_points
        if n > ins.max_points:
            raise ValueError(
                f"{ins.model} stores at most {ins.max_points} points, asked {n}")
        return ins, mode, n

    def lsb_volts(self) -> float:
        ins, mode, _ = self.resolved()
        return ins.lsb_volts(self.full_scale_v, mode.name)


@dataclass
class Platform:
    """The physics the atoms bring, which differs between the two benches."""

    name: str
    radiation_temperature_k: float
    atom_temperature_k: Optional[float] = None
    transit_fwhm_mhz: float = 0.96
    gamma_coll_mhz: float = 0.0
    sigma_laser_mhz: float = 0.0
    gamma_l_mhz: float = 0.0
    note: str = ""

    def blackbody_shift_mhz(self) -> float:
        """The differential shift, at the RADIATION temperature, in MHz.

        The argument is the environment's temperature and never the cloud's.
        That is the whole distinction between the two platforms here.
        """
        return blackbody.shift_hz(self.radiation_temperature_k) / 1e6


def vapour_cell(t_c: float, **kw) -> Platform:
    """The heated cell: the atoms radiate against the cell they sit in."""
    return Platform(name="vapour_cell",
                    radiation_temperature_k=273.15 + t_c,
                    atom_temperature_k=273.15 + t_c,
                    note="radiation temperature IS the cell temperature",
                    **kw)


def nanofibre(atom_temperature_uk: float = 30.0, **kw) -> Platform:
    """The nanofibre: microkelvin atoms in a room-temperature laboratory.

    The atom temperature is carried because it sets the transit time through
    the guided mode, and it is NOT the radiation temperature. Passing it as
    one would zero a term that is the same size as it is in the cell.
    """
    return Platform(name="nanofibre",
                    radiation_temperature_k=NANOFIBRE_RADIATION_K,
                    atom_temperature_k=atom_temperature_uk * 1e-6,
                    note=("radiation temperature is the ROOM at 300 K, fixed, "
                          "while the atoms are at microkelvin. The two are "
                          "unrelated and the shift follows the room"),
                    **kw)


def line_positions_mhz() -> Dict[str, float]:
    """Transition-axis positions of the four peaks, from their wavelengths.

    Computed from `constants.PEAKS` rather than typed, referenced to the
    highest-frequency line, so a hand-copied splitting cannot enter. The four
    span about 5.2 GHz.
    """
    ref_nm = min(p["lambda_nm"] for p in K.PEAKS.values())
    return {k: 2.0 * (C_M_S / (v["lambda_nm"] * 1e-9)
                      - C_M_S / (ref_nm * 1e-9)) / 1e6
            for k, v in K.PEAKS.items()}


def _profile(nu: np.ndarray, centre: float, platform: Platform) -> np.ndarray:
    """The composite line, through the package's own profile machinery."""
    from .linefit import _shared_profile_grid
    g, prof = _shared_profile_grid(
        platform.gamma_coll_mhz, platform.sigma_laser_mhz,
        platform.transit_fwhm_mhz, 0.0, "gaussian", platform.gamma_l_mhz)
    pk = float(prof.max()) or 1.0
    return np.interp(nu - centre, g, prof, left=0.0, right=0.0) / pk


def _correlate(x: np.ndarray, tau_int: float,
               rng: np.random.Generator) -> np.ndarray:
    """Impose a measured integrated autocorrelation on a white sequence.

    A first-order recursion whose lag-one coefficient gives the requested
    tau_int, rescaled to preserve the marginal variance. The record measures
    tau_int between 1.3 and 19.8 samples, which is why a twin that generates
    white noise overstates the independent information of every trace.
    """
    if tau_int <= 1.0:
        return x
    rho = (tau_int - 1.0) / (tau_int + 1.0)
    out = np.empty_like(x)
    out[0] = x[0]
    for i in range(1, x.size):
        out[i] = rho * out[i - 1] + x[i]
    return out * np.sqrt(1.0 - rho ** 2)


def acquire(platform: Platform, acq: Acquisition, *,
            detection_channel=None, halo_fraction: float = 0.0,
            kind: str = "one_peak",
            peak: str = "4154",
            amp_v: Optional[float] = None,
            noise_law: Optional[dict] = None,
            noise_frac: float = 0.004,
            baseline_v: float = 0.01,
            amp_spread: float = 0.05,
            centre_jitter_mhz: float = 0.0,
            drift_mhz_per_trace: float = 0.0,
            rng: Optional[np.random.Generator] = None,
            ) -> Tuple[List[np.ndarray], List[np.ndarray], Dict]:
    """Produce the traces this instrument would store, in fitter form.

    ``detection_channel`` is None by default, which leaves the four peaks at
    equal shares and every existing output byte-identical. Passed a
    ``detection.DetectionChannel`` it applies the scalar-operator population
    law, abundance times (2F+1)/G_iso, and ``halo_fraction`` adds the
    trapped-light re-excitation the caller reads from
    ``results/trapping_channels.csv`` for its temperature.

    ``kind`` is "one_peak", the quantitative ladder's trace, or "four_peak",
    all four lines on ONE vertical range in a single acquisition, which is
    the trace kind that carries its own frequency ruler and its own
    brightness comparison.

    Returns (freqs, volts, meta), where meta records what the instrument did:
    the point count, the vertical step, the mode and its mechanism, and the
    blackbody shift with the temperature it was evaluated at, so a reader can
    check the platform distinction rather than trust it.
    """
    if rng is None:
        rng = np.random.default_rng()
    ins, mode, n_points = acq.resolved()
    pos = line_positions_mhz()

    peak_v = amp_v if amp_v is not None else (
        acq.peak_fraction_of_scale * acq.full_scale_v - baseline_v)
    bbr_mhz = platform.blackbody_shift_mhz()

    if kind == "one_peak":
        nu = np.linspace(-acq.span_mhz, acq.span_mhz, n_points)
        centres = {peak: 0.0}
        shares = {peak: 1.0}
    elif kind == "four_peak":
        lo, hi = min(pos.values()) - acq.span_mhz, max(pos.values()) + acq.span_mhz
        nu = np.linspace(lo, hi, n_points)
        centres = dict(pos)
        if detection_channel is None:
            # equal shares unless the caller supplies its own brightness model:
            # the twin must not invent a branching ratio it does not have
            shares = {k: 1.0 for k in pos}
        else:
            # THE DETECTION CHANNEL, wired 2026-09-05 (register A56, A57).
            #
            # NOT exp(-tau). The first draft of this wiring attenuated each peak
            # by its own optical depth and would have generated BLANK traces:
            # tau runs 2.3 at 70 C to 319 at 130 C over 2 cm, and exp(-319) is
            # zero. Two reasons that model is wrong here, and the record already
            # carried both. At tau >> 1 the photon is RE-EMITTED rather than
            # lost, so trapping is transport and not Beer-Lambert. And inside the
            # driven volume the medium is INVERTED, 4.81 and 5.26 to one
            # (results/trapping_channels.csv), because 5P empties in 27 ns while
            # the drive refills 6S, so there is no reabsorption where the signal
            # is made at all.
            #
            # What survives is a 5P HALO fed by trapped D-line photons, which
            # re-excites at a fraction of the primary two-photon rate: 0 at
            # 70 C, 0.0027 at 90 C, 0.080 at 110 C, and 1.07 +- 0.58 per cent at
            # 130 C. The CALLER supplies that fraction from the committed cells,
            # so the number keeps its provenance and this module does not read
            # results/.
            from . import amplitudes as _amp
            base = _amp.predicted_shares()
            shares = {k: base[k] * (1.0 + halo_fraction) for k in pos}
    else:
        raise ValueError(f"kind must be one_peak or four_peak, got {kind!r}")

    freqs, volts = [], []
    for i in range(acq.n_traces):
        drift = drift_mhz_per_trace * i
        jitter = centre_jitter_mhz * rng.standard_normal() if centre_jitter_mhz else 0.0
        amp = peak_v * (1.0 + amp_spread * rng.standard_normal())
        v = np.full(nu.size, baseline_v, dtype=float)
        for key, c0 in centres.items():
            # the blackbody term shifts the LINE, at the radiation
            # temperature of this platform and never at the atoms'
            c = c0 - bbr_mhz + drift + jitter
            v = v + amp * shares[key] * _profile(nu, c, platform)
        if noise_law is not None:
            sig = sigma_of_v(np.clip(v - baseline_v, 0.0, None), noise_law)
        else:
            sig = noise_frac * peak_v * np.sqrt(
                np.clip(v, 0.0, None) / max(peak_v, 1e-12))
        white = rng.standard_normal(nu.size)
        v = v + sig * _correlate(white, acq.tau_int_samples, rng)
        v = inst.apply_resolution_mode(v, mode, raw_per_point=acq.raw_per_point)
        if acq.quantise:
            v = inst.quantise(v, acq.lsb_volts())
        freqs.append(nu.copy())
        volts.append(v)

    meta = {
        "instrument": ins.model,
        "mode": mode.name,
        "mode_kind": mode.kind,
        "correlates_neighbours": mode.correlates_neighbours,
        "n_points": n_points,
        "lsb_volts": acq.lsb_volts(),
        "peak_over_lsb": peak_v / acq.lsb_volts() if acq.lsb_volts() else float("inf"),
        "kind": kind,
        "platform": platform.name,
        "radiation_temperature_k": platform.radiation_temperature_k,
        "atom_temperature_k": platform.atom_temperature_k,
        "blackbody_shift_mhz": bbr_mhz,
        "tau_int_samples": acq.tau_int_samples,
    }
    return freqs, volts, meta
