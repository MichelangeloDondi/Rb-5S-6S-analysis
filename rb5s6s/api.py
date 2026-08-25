"""The supported entry point: a trace in, a linewidth out.

WHY THIS MODULE EXISTS. Until 2026-08-26 this package exported eighteen
names, every one a constant or a forward-model primitive, while the six
modules a stranger needs to fit their own data -- `linefit`, `ingest`,
`ruler`, `trim`, `qc`, `global_fit` -- were all present and none reachable
without reading the internal layout. The advertised front door,
`examples/your_line.ipynb`, never opened a file. So the package **exported
the physics it derived and hid the analysis it did**, which is the same
defect the repository has on its reading surface: what a reader needs is
present but not surfaced, and what the author found interesting is
foregrounded.

This module is the fix, and it is deliberately one function. Everything
under it already existed; nothing here is new physics.

WHAT IS DELIBERATELY NOT EXPORTED. `ruler`, `trim`, `qc` and `global_fit`
stay internal. They carry this campaign's own conventions -- the ruler's
per-session calibration rates, the trim's discrete sample boundaries, the
QC flags defined against this apparatus -- and surfacing them would invite a
stranger to apply them to data they do not describe. Exporting a name is a
promise of support, and the promise should cover only what someone else can
use correctly.

THE AXIS, because every width in this field is ambiguous by a factor of two.
Everything returned here is on the TRANSITION axis, which is twice the laser
axis for a two-photon transition. The field names say `_mhz` and this
docstring says which axis; that pairing is the record's own standing rule.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Sequence

import numpy as np

from .constants import GAMMA_NAT_HZ
from .linefit import fit_condition
from .lineshape import total_fwhm_mhz

__all__ = ["LinewidthResult", "fit_linewidth"]


@dataclass
class LinewidthResult:
    """A fitted linewidth and what it is made of, all on the transition axis.

    `fwhm_mhz` is the composite line's full width at half maximum, read off
    the fitted model profile rather than composed from a formula, because the
    composite is a convolution for which no closed form is exact.

    `fwhm_err_mhz` propagates the fitted component errors through that width
    by finite difference, including the fitted correlation between the
    collisional and laser terms. It is `nan` when the fit returned no usable
    covariance, and a `nan` here means the error is unknown, never zero.
    """

    fwhm_mhz: float
    fwhm_err_mhz: float
    components: Dict[str, float] = field(default_factory=dict)
    n_traces: int = 0
    chi2_red: float = float("nan")
    raw: Dict = field(default_factory=dict, repr=False)

    def __repr__(self) -> str:  # pragma: no cover - display only
        return (f"LinewidthResult(fwhm_mhz={self.fwhm_mhz:.4f} "
                f"+/- {self.fwhm_err_mhz:.4f}, transition axis, "
                f"n_traces={self.n_traces}, chi2_red={self.chi2_red:.3f})")


def _as_trace_lists(freqs, volts):
    """Accept one trace or many, and say so clearly when they do not match."""
    if np.ndim(freqs[0]) == 0:                      # a bare 1-D trace
        freqs, volts = [np.asarray(freqs, float)], [np.asarray(volts, float)]
    else:
        freqs = [np.asarray(f, float) for f in freqs]
        volts = [np.asarray(v, float) for v in volts]
    if len(freqs) != len(volts):
        raise ValueError(
            f"{len(freqs)} frequency arrays against {len(volts)} voltage "
            f"arrays. Pass one array each for a single trace, or two lists of "
            f"equal length for repeats of one condition.")
    for i, (f, v) in enumerate(zip(freqs, volts)):
        if f.shape != v.shape:
            raise ValueError(
                f"trace {i}: frequency axis has {f.shape} samples and the "
                f"voltage {v.shape}. They must match.")
        if f.size < 8:
            raise ValueError(
                f"trace {i}: {f.size} samples is too few to fit a lineshape.")
    return freqs, volts


def fit_linewidth(freqs: Sequence, volts: Sequence, *, T_C: float,
                  s0: float = 0.0, law: Optional[Dict] = None,
                  transit_fwhm: Optional[float] = None,
                  **fit_kw) -> LinewidthResult:
    """Fit one condition and return its linewidth, transition axis, MHz.

    `freqs` and `volts` are either one array each (a single trace) or two
    equal-length lists of arrays (repeats of ONE condition, fitted jointly
    with a shared width and per-trace centres and amplitudes). Frequencies are
    detunings in MHz on the transition axis; voltages are the raw detector
    signal, and the baseline is fitted rather than assumed.

    `T_C` is the cell temperature in Celsius, which sets the transit width
    unless `transit_fwhm` is given explicitly.

    `s0` is the depth of an axial AC-Stark ramp in MHz, zero by default. It is
    a MAGNITUDE: the sign convention lives in `constants.DELTA_ALPHA_AU` and
    is not this function's to reinterpret.

    Everything else is forwarded to `linefit.fit_condition`, which is what
    actually does the work and is exported beside this.

    >>> import numpy as np
    >>> from rb5s6s import fit_linewidth, lorentzian
    >>> nu = np.linspace(-30, 30, 400)
    >>> v = 0.6 * lorentzian(nu, 8.0) / lorentzian(np.array([0.0]), 8.0)[0]
    >>> r = fit_linewidth(nu, v, T_C=110.0)
    >>> 6.0 < r.fwhm_mhz < 11.0
    True
    """
    freqs, volts = _as_trace_lists(freqs, volts)
    # transit_fwhm is forwarded only when given, so fit_condition's own
    # default stands otherwise and this module holds no second default.
    kw = dict(fit_kw)
    if transit_fwhm is not None:
        kw["transit_fwhm"] = transit_fwhm
    raw = fit_condition(freqs, volts, T_C=T_C, law=law, s0=s0, **kw)

    gc = float(raw["gamma_coll"])
    sl = float(raw["sigma_laser"])
    tr = float(raw["transit_fwhm"])
    # A grid that clips the wings returns the grid's width, not the line's, so
    # it is sized from the fitted components rather than fixed.
    span = 12.0 * max(gc + sl + tr + s0, GAMMA_NAT_HZ / 1e6)
    nu = np.arange(-span, span, min(0.002, span / 20000.0))
    fwhm = total_fwhm_mhz(nu, gamma_coll=gc, sigma_laser_fwhm=sl,
                          transit_fwhm=tr, s0=s0)

    # Finite-difference propagation through the same construction, including
    # the fitted correlation. Analytic propagation is unavailable because the
    # width is read off a convolution rather than computed in closed form.
    err = float("nan")
    gce, sle = raw.get("gamma_coll_err"), raw.get("sigma_laser_err")
    if gce is not None and sle is not None and np.isfinite(gce) and np.isfinite(sle):
        h_g, h_s = max(1e-4, 1e-3 * max(gc, 1e-3)), max(1e-4, 1e-3 * max(sl, 1e-3))
        d_g = (total_fwhm_mhz(nu, gamma_coll=gc + h_g, sigma_laser_fwhm=sl,
                              transit_fwhm=tr, s0=s0) - fwhm) / h_g
        d_s = (total_fwhm_mhz(nu, gamma_coll=gc, sigma_laser_fwhm=sl + h_s,
                              transit_fwhm=tr, s0=s0) - fwhm) / h_s
        rho = float(raw.get("corr_laser_coll") or 0.0)
        var = (d_g * gce) ** 2 + (d_s * sle) ** 2 + 2.0 * rho * d_g * gce * d_s * sle
        err = float(np.sqrt(var)) if var > 0 else float("nan")

    return LinewidthResult(
        fwhm_mhz=fwhm, fwhm_err_mhz=err,
        components={"gamma_coll_mhz": gc, "sigma_laser_fwhm_mhz": sl,
                    "transit_fwhm_mhz": tr, "gamma_nat_mhz": GAMMA_NAT_HZ / 1e6,
                    "s0_mhz": float(s0)},
        n_traces=int(raw.get("n_traces", len(freqs))),
        chi2_red=float(raw.get("chi2_red", float("nan"))),
        raw=raw)
