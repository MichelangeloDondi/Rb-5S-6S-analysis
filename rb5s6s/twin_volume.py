"""The digital twin's WORLD on the joint per-path line (owner order O45/O46): synthetic traces
generated from the atom-sampled two-time line (`volume_line.joint_spectrum`) rather than from
the fitter's convolution form, so a fit against these traces cannot recover the truth merely by
being the same model that generated it (`rb5s6s.forecast`'s own charter line: "simulate the
experiment you have not built"; here, simulate it with the model the fitter is ALSO moving to,
so C6b's own moment reading is tested on a world it did not build).

THE WORLD MUST BE THE MONTE CARLO, NEVER THE FITTER'S TABLE (the task that ordered this file, in
those words): `synthetic_traces` below calls `volume_line.joint_spectrum` directly, at a high
atom count, never `volume_line.JointTable`. Using the table to generate what the table is later
used to fit would make every closure here circular -- the table's own interpolation error would
be invisible to any injection-recovery test built on it.

TRACE FORMAT: `synthetic_traces` returns `(freqs, volts)`, each a list of arrays one per trace,
matching `rb5s6s.forecast.synthetic_traces`'s own return convention exactly (`fit_condition`'s
input form) -- read that module's docstring for the charter this format serves. The INPUT
signature necessarily differs: the joint model has no separate `transit_fwhm`, `gamma_coll` or
independent `s0` the way three-independent-factor convolution does (that independence is exactly
what the joint line exists to drop, and F318 measured where it matters: the odd moments at middle
windows and high drive, under one archive sd, never the even ones), so this module takes a `beam` (see `volume_line.GaussianBeam`), `T_C`
and a `z_ratio`-derived collection window in its place, plus `S0_mhz` and `gamma_hom_mhz`
directly -- the same two quantities `volume_line.joint_spectrum` itself takes. `stark_s0_mhz`
below is the bridge from a physical (power, waist) condition to `S0_mhz`, through the CORRECTED,
actual-focus on-axis factor (F280/F291/F298), for a caller who has a power rather than an S0.

WHAT IS CARRIED from `forecast.synthetic_traces`: the per-trace amplitude/offset spread pattern
(`amp`, `amp_spread`, `offset`, `offset_spread`), the two `noise` modes (a float fraction of peak
for white i.i.d. noise, or a `rb5s6s.noise` law dict evaluated per point through `sigma_of_v`),
and the `centre_mhz` shift convention (the line is evaluated at `nu - centre_mhz`, so its own
peak lands at `nu = centre_mhz`). WHAT IS NOT: `tau_int`/`residual_source` (correlated or
archive-shaped noise) and `halo_fraction` (the trapped-light amplitude floor) are out of this
promotion's scope -- `noise` stays i.i.d. per point unless the caller layers correlation on
afterwards, and every trace here is the bare joint line's own amplitude and baseline.

THE WORLD LINE IS CACHED PER CONDITION AND SEED (the task's own instruction): recomputing the
atom-sampled Monte Carlo for every trace of a multi-trace call, or across repeated calls at an
identical design point, would be needless work the fitter-facing `JointTable` exists specifically
to avoid paying twice.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import numpy as np

from .constants import DELTA_ALPHA_AU, GAMMA_NAT_HZ, RHO_RETRO
from .lineshape import aperture_onaxis_factor_actual, stark_shift_S0_mhz
from .noise import sigma_of_v
from .volume_line import N_TAU, TAU_EDGE, GaussianBeam, collection_half_window_m, joint_spectrum

__all__ = ["stark_s0_mhz", "world_shape", "synthetic_traces"]


def stark_s0_mhz(power_w: float, w0_m: float, rho: float = RHO_RETRO,
                 delta_alpha_au: float = DELTA_ALPHA_AU, *, clamp_floor: bool = False) -> float:
    """On-axis, aperture-corrected AC-Stark S0 (MHz) at the ACTUAL (bore-limited, same-reading)
    focus `w0_m`: `stark_shift_S0_mhz(power_w, w0_m, rho, delta_alpha_au) *
    aperture_onaxis_factor_actual(w0_m, clamp_floor=clamp_floor)`.

    Mirrors `private/cache/plan_2026-09-16/p18_joint_line.py`'s own `s0_mhz`, but through the
    CORRECTED on-axis factor (F280/F291/F298) rather than the plain `aperture_onaxis_factor`:
    `w0_m` here is the SAME-READING actual focus (`constants.W0_CENTRAL_M`'s own convention,
    what a `volume_line.GaussianBeam(w0_m, ...)` is built from), and the plain
    `aperture_onaxis_factor` describes the wrong beam at that reading by about 20 per cent at the
    bore-limited waist (F280's own finding). A `w0_m` below this bore's floor (about 40.9 um at
    the default aperture) raises unless `clamp_floor=True`; see `aperture_onaxis_factor_actual`'s
    own docstring for both.
    """
    return (stark_shift_S0_mhz(float(power_w), float(w0_m), rho=float(rho),
                               delta_alpha_au=delta_alpha_au)
            * aperture_onaxis_factor_actual(float(w0_m), clamp_floor=clamp_floor))


_WORLD_CACHE: Dict[tuple, np.ndarray] = {}
_WORLD_CACHE_MAX = 64


def _world_line_cached(*, S0_mhz: float, gamma_hom_mhz: float, sigma_laser_mhz: float, beam,
                       T_C: float, half_window_m: float, n_path: int, seed: int,
                       delta_mhz: np.ndarray, n_tau: int, tau_edge: float) -> np.ndarray:
    """`volume_line.joint_spectrum`, cached per condition and seed: recomputed only when one of
    its own inputs moves, never once per trace and never twice for an identical design point
    (two forecast calls at the same condition and seed return the cached array). Keyed on scalar
    provenance rather than on the beam object's identity, so two value-equal beams built
    separately (e.g. across two calls) still hit the cache; `repr(beam)` is exact for
    `GaussianBeam` (its own `__repr__`) and merely conservative (never wrong, only a possible
    cache miss) for a beam whose `__repr__` is the default object one."""
    key = (round(float(S0_mhz), 12), round(float(gamma_hom_mhz), 12),
          round(float(sigma_laser_mhz), 12), repr(beam), round(float(T_C), 9),
          round(float(half_window_m), 15), int(n_path), int(seed),
          round(float(delta_mhz[0]), 9), round(float(delta_mhz[-1]), 9), int(delta_mhz.size),
          int(n_tau), round(float(tau_edge), 9))
    cached = _WORLD_CACHE.get(key)
    if cached is not None:
        return cached.copy()
    line = joint_spectrum(S0_mhz=S0_mhz, gamma_hom_mhz=gamma_hom_mhz, beam=beam, T_C=T_C,
                          half_window_m=half_window_m, n_path=n_path, seed=seed,
                          delta_mhz=delta_mhz, n_tau=n_tau, tau_edge=tau_edge,
                          sigma_laser_mhz=sigma_laser_mhz)
    if len(_WORLD_CACHE) > _WORLD_CACHE_MAX:
        _WORLD_CACHE.clear()
    _WORLD_CACHE[key] = line.copy()
    return line.copy()


def world_shape(*, beam, T_C: float, S0_mhz: float, gamma_hom_mhz: float,
                sigma_laser_mhz: float = 0.0, z_ratio: float = 0.6,
                span_mhz: float = 60.0, n_points: int = 2000,
                centre_mhz: float = 0.0, n_path: int = 20000, seed: int = 0,
                n_tau: int = N_TAU, tau_edge: float = TAU_EDGE,
                ) -> Tuple[np.ndarray, np.ndarray]:
    """The atom-sampled joint line's peak-normalised, noise-free shape (module docstring: THE
    WORLD MUST BE THE MONTE CARLO, NEVER THE FITTER'S TABLE) -- the piece `synthetic_traces`
    below layers its own per-trace amplitude/offset pattern onto, split out (C6b noise wave,
    2026-09-22) so a caller with its OWN noise layer (`forecast.synthetic_traces`'s shared
    `_traces_from_shape`, the SAME one the convolution branch uses) can reuse the cached
    Monte Carlo world line without a second, independent copy of the noise-adding code -- the
    defect that left `model="joint"` traces unable to carry correlated noise, a residual-seam
    draw or the halo fraction at all.

    `beam` (e.g. `volume_line.GaussianBeam(w0_m, m2)`) and `z_ratio` set the collection window
    (`volume_line.collection_half_window_m`). `S0_mhz` and `gamma_hom_mhz` are the same two
    quantities `joint_spectrum` itself takes (`stark_s0_mhz` above converts a physical power at
    this `beam`'s waist into `S0_mhz`, through the corrected on-axis factor, for a caller with
    a power instead of an S0). The world line is computed ONCE (cached, see
    `_world_line_cached`) and peak-normalised (`shape.max() == 1`). `centre_mhz` shifts the
    line: it is evaluated at `nu - centre_mhz`, so its own peak lands at `nu = centre_mhz`,
    matching `synthetic_traces` and `forecast.synthetic_traces` exactly.

    Returns (nu, shape): the frequency axis (MHz) and the peak-normalised world line.
    """
    nu = np.linspace(-float(span_mhz), float(span_mhz), int(n_points))
    half_window_m = collection_half_window_m(beam, z_ratio)
    world = _world_line_cached(S0_mhz=S0_mhz, gamma_hom_mhz=gamma_hom_mhz,
                               sigma_laser_mhz=sigma_laser_mhz, beam=beam, T_C=T_C,
                               half_window_m=half_window_m, n_path=n_path, seed=seed,
                               delta_mhz=nu - centre_mhz, n_tau=n_tau, tau_edge=tau_edge)
    peak = world.max()
    if peak <= 0.0:
        raise ValueError("twin_volume.world_shape: the joint line vanished on this axis: "
                         "widen span_mhz, or check n_path/T_C/beam")
    return nu, world / peak


def synthetic_traces(*, beam, T_C: float, S0_mhz: float, gamma_hom_mhz: float,
                     sigma_laser_mhz: float = 0.0, z_ratio: float = 0.6,
                     span_mhz: float = 60.0, n_points: int = 2000, n_traces: int = 5,
                     noise: object = 0.004, amp: float = 1.0, amp_spread: float = 0.05,
                     offset: float = 0.010, offset_spread: float = 0.002,
                     centre_mhz: float = 0.0, n_path: int = 20000, seed: int = 0,
                     n_tau: int = N_TAU, tau_edge: float = TAU_EDGE,
                     rng: Optional[np.random.Generator] = None,
                     registry: Optional[str] = None,
                     ) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """Generate the traces the real instrument would record, with the line computed by the
    atom-sampled joint Monte Carlo (`volume_line.joint_spectrum`) at `n_path` atoms -- the WORLD,
    never the fitter's `volume_line.JointTable` (module docstring). The shape comes from
    `world_shape` above (peak-normalised, cached). This function then gives it the same
    per-trace amplitude and offset spread `forecast.synthetic_traces` uses, so repeats differ the
    way real repeats do: `a = amp*(1+amp_spread*i)`, `base = offset+offset_spread*i`,
    `clean = a*shape + base`.

    `noise` is either a float, the i.i.d. per-point standard deviation as a FRACTION OF PEAK (the
    simple mode), or a noise-law dict as returned by `rb5s6s.noise.condition_noise_model` /
    `load_noise_model`, in which case each point's sigma comes from the law evaluated at that
    point's signal level through `sigma_of_v` -- exactly `forecast.synthetic_traces`'s own two
    modes, minus the correlated-noise and halo-fraction extensions that module also carries (see
    this module's own docstring for what is out of scope here: this function's OWN noise stays
    i.i.d., unchanged by the C6b noise wave. `forecast.synthetic_traces(model="joint")` is what
    gained the shared, fuller noise layer, by calling `world_shape` directly instead of this
    function).

    `registry` (O58) is the twin's declaration, read by `forecast.twin_preflight` before the world
    line is drawn: None for a run behind a result, or a study's reason of six words or more. The
    homogeneous width arrives lumped, so a width above the natural one is read as the collisional
    term the registry names; a caller whose width is something else declares a study.

    Returns (freqs, volts), each a list of `n_traces` arrays, in the form
    `rb5s6s.linefit.fit_condition` accepts (matching `forecast.synthetic_traces`'s own promise).
    """
    from .forecast import twin_preflight
    _ex = {"natural_width", "transit", "beam_quality_m2"}
    if not isinstance(beam, GaussianBeam):
        _ex.add("bore_clipping")
    if S0_mhz > 0.0:
        _ex |= {"ac_stark_ramp", "transit_chirp"}
    if z_ratio > 0.0:
        _ex.add("axial_collection_window")
    if sigma_laser_mhz > 0.0:
        _ex.add("laser_kernel")
    if gamma_hom_mhz > GAMMA_NAT_HZ / 1e6 + 1e-12:
        _ex.add("self_broadening_vdw")
    twin_preflight(_ex, registry, T_C=T_C)
    if rng is None:
        # never from entropy: the noise stream is derived from `seed`, spawned apart from the world
        # line's own sampling stream, so a trace set is reproducible from its arguments alone
        rng = np.random.default_rng(np.random.SeedSequence([int(seed), 1]))
    nu, shape = world_shape(beam=beam, T_C=T_C, S0_mhz=S0_mhz, gamma_hom_mhz=gamma_hom_mhz,
                            sigma_laser_mhz=sigma_laser_mhz, z_ratio=z_ratio, span_mhz=span_mhz,
                            n_points=n_points, centre_mhz=centre_mhz, n_path=n_path, seed=seed,
                            n_tau=n_tau, tau_edge=tau_edge)

    freqs: List[np.ndarray] = []
    volts: List[np.ndarray] = []
    for i in range(int(n_traces)):
        a = float(amp) * (1.0 + float(amp_spread) * i)
        base = float(offset) + float(offset_spread) * i
        clean = a * shape + base
        w_noise = rng.standard_normal(nu.size)
        if isinstance(noise, dict):
            sig = np.asarray([sigma_of_v(v, noise) for v in clean])
            v = clean + sig * w_noise
        else:
            v = clean + float(noise) * a * w_noise
        freqs.append(nu.copy())
        volts.append(v)
    return freqs, volts
