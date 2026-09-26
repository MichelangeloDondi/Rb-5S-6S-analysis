"""The twin's clean line from the full-model line (owner order O59, W1): one path for the twin and the Monte Carlo.

WHY. The registry (`rb5s6s.model_registry`) holds the twin and the Monte Carlo apart by the terms one path carries and
the other does not (`PAIRING_BASELINE`) and by the terms both carry through different code (`IMPL_BASELINE`). The
full-model line, `bloch_full.full_line`, carries every term either path splits between them, so the twin's clean line
is drawn from it here and from nothing else; the noise layer is the twin's own (`forecast._traces_from_shape`), so a
trace differs from one of the layered generator's by the clean line alone.

WHAT IT COSTS, AND WHY THE CACHE. A full-model line is an atom-sampled optical-Bloch solve, minutes at the contract's
atom count, while a twin study needs a line per CONDITION and many noise realisations of each. So each condition's
line is computed once on a line grid and cached on disk, keyed by every parameter it depends on and by the digest of
the code it computes with, derived from the imports (`kernel_gate.import_closure`), so a code change is a cache miss
and never a stale line. The trace axis is then read off the line grid by a cubic spline, whose error is fourth order
in the step over the width (0.25 MHz against a core of about five), which the tests close against a direct solve; a
monotone cubic flattens a smooth peak and left 2.1e-3 of the peak there when this was written, five times the twin's
lowest noise rung.

    clean_line(grid, peak=..., P_W=..., T_C=..., w0_m=..., ...)   -> (peak-normalised line on `grid`, info)
    synthetic_traces(peak=..., P_W=..., T_C=..., w0_m=..., ...)   -> (freqs, volts), the twin's trace set

The cache directory is `RB5S6S_TWIN_LINE_CACHE`, else `~/.cache/rb5s6s/twin_lines`: lines are derived data, never a
record, and a clean checkout recomputes them.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
from typing import Dict, List, Optional, Tuple

import numpy as np

from . import constants as K
from . import kernel_gate as _KG

__all__ = ["clean_line", "synthetic_traces", "code_digest", "cache_dir", "LINE_STEP_MHZ"]

#: the line grid's step: the cubic spline that reads the trace axis off it is exact on the grid and its error between
#: nodes is fourth order in the step over the width, so 0.25 MHz against a core of about five is far below any noise
#: level the twin draws (the tests close it against a direct solve on a finer axis)
LINE_STEP_MHZ = 0.25
#: modules whose edits do not change a line: the gate and the registry judge a line, they do not compute it
_NOT_THE_LINE = frozenset({"kernel_gate", "model_registry"})


def cache_dir() -> pathlib.Path:
    d = os.environ.get("RB5S6S_TWIN_LINE_CACHE")
    return pathlib.Path(d) if d else pathlib.Path.home() / ".cache" / "rb5s6s" / "twin_lines"


def code_digest() -> str:
    """The digest of the code a full-model line computes with, derived from `bloch_full`'s imports."""
    return _KG.model_digest(files=_KG.import_closure(["bloch_full"], exclude=_NOT_THE_LINE)) or "no-code"


def _key(grid: np.ndarray, params: Dict) -> str:
    h = hashlib.sha256()
    h.update(code_digest().encode())
    h.update(np.ascontiguousarray(grid, dtype=float).tobytes())
    h.update(json.dumps(params, sort_keys=True, default=str).encode())
    return h.hexdigest()[:24]


def clean_line(grid, *, peak: str, P_W: float, T_C: float, w0_m: float, M2: float = 1.0,
               rho: float = K.RHO_RETRO, n_path: int = 4000, seed: int = 0,
               terms: Optional[Dict[str, float]] = None, intensity_scale: float = 1.0,
               registry: Optional[str] = None, use_cache: bool = True, **numerics) -> Tuple[np.ndarray, Dict]:
    """The full-model line on `grid` (MHz), normalised to a peak of 1, and what ran.

    Every argument is `bloch_full.full_line`'s own and reaches it unchanged, with `consumer="twin"`, so the registry's
    door grades the twin's terms before the first atom; `registry` is a study's reason, as there. The line is read
    from the cache when a line of the same grid, parameters and code is on disk."""
    from .bloch_full import full_line
    grid = np.asarray(grid, dtype=float)
    params = dict(peak=str(peak), P_W=float(P_W), T_C=float(T_C), w0_m=float(w0_m), M2=float(M2), rho=float(rho),
                  n_path=int(n_path), seed=int(seed), terms=dict(terms or {}), intensity_scale=float(intensity_scale),
                  registry=registry, numerics={k: numerics[k] for k in sorted(numerics)})
    key = _key(grid, params)
    f = cache_dir() / f"{key}.npz"
    if use_cache and f.is_file():
        with np.load(f, allow_pickle=False) as z:
            line = np.asarray(z["line"], float)
            info = json.loads(str(z["info"]))
        info["cache"] = "hit"
        return line, info
    signal, info = full_line(grid, peak=str(peak), P_W=float(P_W), T_C=float(T_C), w0_m=float(w0_m), M2=float(M2),
                             rho=float(rho), n_path=int(n_path), seed=int(seed), terms=terms,
                             intensity_scale=float(intensity_scale), consumer="twin", registry=registry, **numerics)
    signal = np.asarray(signal, float)
    top = float(np.max(signal))
    if not top > 0.0:
        raise ValueError("twin_bloch.clean_line: the full-model line vanished on this grid")
    line = signal / top
    info = {k: (sorted(v) if isinstance(v, (set, frozenset)) else v) for k, v in info.items() if k != "registry"}
    info = json.loads(json.dumps(info, default=str))
    info.update(code_digest=code_digest(), key=key)
    if use_cache:
        f.parent.mkdir(parents=True, exist_ok=True)
        tmp = f.with_suffix(".tmp.npz")
        np.savez(tmp, line=line, info=json.dumps(info))
        tmp.replace(f)
    info["cache"] = "miss"
    return line, info


def synthetic_traces(*, peak: str, P_W: float, T_C: float, w0_m: float, M2: float = 1.0,
                     rho: float = K.RHO_RETRO, span_mhz: float = 60.0, n_points: int = 2000,
                     centre_mhz: float = 0.0, n_traces: int = 5, noise: object = 0.004, amp: float = 1.0,
                     amp_spread: float = 0.05, offset: float = 0.010, offset_spread: float = 0.002,
                     halo_fraction: float = 0.0, tau_int: Optional[float] = None, residual_source=None,
                     rng: Optional[np.random.Generator] = None, n_path: int = 4000, seed: int = 0,
                     terms: Optional[Dict[str, float]] = None, intensity_scale: float = 1.0,
                     registry: Optional[str] = None, line_step_mhz: float = LINE_STEP_MHZ,
                     use_cache: bool = True, **numerics) -> Tuple[List[np.ndarray], List[np.ndarray]]:
    """The traces the instrument would record at this condition, drawn from the full-model line.

    The clean line is `clean_line` on a grid of `line_step_mhz` spanning the trace axis, read onto the `n_points`
    axis by a cubic spline; the noise, the amplitude and offset spreads, the halo, the correlation and the
    residual seam are the twin's one shared layer (`forecast._traces_from_shape`), exactly as for the layered
    generator. Returns (freqs, volts), one array per trace, in the form `linefit.fit_condition` accepts."""
    from scipy.interpolate import CubicSpline
    from .forecast import _traces_from_shape
    nu = np.linspace(-float(span_mhz), float(span_mhz), int(n_points))
    n_grid = int(round(2.0 * float(span_mhz) / float(line_step_mhz))) + 1
    grid = np.linspace(-float(span_mhz), float(span_mhz), n_grid)
    line, _info = clean_line(grid, peak=peak, P_W=P_W, T_C=T_C, w0_m=w0_m, M2=M2, rho=rho, n_path=n_path, seed=seed,
                             terms=terms, intensity_scale=intensity_scale, registry=registry, use_cache=use_cache,
                             **numerics)
    x = nu - float(centre_mhz)
    shape = np.where((x >= grid[0]) & (x <= grid[-1]), CubicSpline(grid, line)(np.clip(x, grid[0], grid[-1])), 0.0)
    shape = shape / float(np.max(shape))
    if rng is None:
        rng = np.random.default_rng(np.random.SeedSequence([int(seed), 2]))
    return _traces_from_shape(nu, shape, n_traces=n_traces, noise=noise, amp=amp, amp_spread=amp_spread,
                              offset=offset, offset_spread=offset_spread, halo_fraction=halo_fraction,
                              tau_int=tau_int, residual_source=residual_source, rng=rng)
