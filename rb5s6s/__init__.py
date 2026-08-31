"""
rb5s6s: from-scratch analysis of the OIST Rb 5S1/2 to 6S1/2 two-photon campaigns.

Pipeline modules follow docs/methods.md (M0 ingest through M30). Physics constants
live in :mod:`rb5s6s.constants`, tunable choices in :mod:`rb5s6s.config`. Nothing
numeric is hard-coded anywhere else.

WHAT THIS NAMESPACE RE-EXPORTS, and why only this much. docs/ADAPTING.md's seam map
names the places another transition or another apparatus would touch, and the names
below are the ones on those seams: the shift-distribution machinery and the composite
line model (the deep seam), the polarizability chain that predicts the shift, and the
two-photon coupling. They are re-exported so `from rb5s6s import stark_ramp` works
without the reader having to learn the module layout first.

Everything re-exported here is PURE: it touches no file and needs no data tree, so it
works from an installed wheel. The modules that do read data (config, ingest, qc,
rate_model, ruler, cavity_scan) are deliberately NOT re-exported, because reaching them from an
installed package without the repository beside it fails in a way worth failing
loudly (see :func:`rb5s6s.config.require_repo_data`).
"""

__version__ = "4.5"

from .constants import (                                    # noqa: F401
    DELTA_ALPHA_AU,
    GAMMA_NAT_HZ,
    LAMBDA_LASER_M,
    RHO_RETRO,
    TAU_6S_S,
    W0_MEASURED_M,
    transit_fwhm_from_w0,
)
from .hyperpolarizability import (                          # noqa: F401
    two_photon_matrix_element,
    two_photon_rabi_hz,
)
from .lineshape import (                                    # noqa: F401
    composite_profile,
    model_profile,
    stark_ramp,
    stark_ramp_axial_moments,
    stark_shift_S0_mhz,
    total_fwhm_mhz,
    voigt_fwhm,
)
# THE ANALYSIS PATH. Everything above derives the
# physics; until this line the package shipped no supported way to fit a
# measured trace, though `linefit` had done exactly that for the whole
# campaign. `api.fit_linewidth` is the one-call entry and `linefit` and
# `ingest` are the modules under it. `ruler`, `trim`, `qc` and `global_fit`
# stay unexported on purpose: they carry this campaign's own conventions and
# exporting a name is a promise it can be used correctly on other data.
from . import ingest, linefit                               # noqa: F401
from .api import LinewidthResult, fit_linewidth             # noqa: F401
from .linefit import fit_condition                          # noqa: F401
from .polarizability import (                               # noqa: F401
    alpha_5s,
    alpha_6s,
    delta_alpha,
)

__all__ = [
    "__version__",
    # constants and the geometry that follows from them
    "DELTA_ALPHA_AU", "GAMMA_NAT_HZ", "LAMBDA_LASER_M", "RHO_RETRO",
    "TAU_6S_S", "W0_MEASURED_M", "transit_fwhm_from_w0",
    # the deep seam: the shift distribution and the line model
    "stark_ramp", "stark_ramp_axial_moments", "stark_shift_S0_mhz",
    "composite_profile", "model_profile",
    # what predicts the shift, and what couples to the light
    "alpha_5s", "alpha_6s", "delta_alpha",
    "two_photon_matrix_element", "two_photon_rabi_hz",
    # the analysis path: a measured trace in, a linewidth out
    "fit_linewidth", "LinewidthResult", "fit_condition",
    "total_fwhm_mhz", "voigt_fwhm",
    "linefit", "ingest",
    # THE GUIDED GEOMETRY IS DELIBERATELY NOT RE-EXPORTED HERE, and a reading
    # was right that it is hard to reach and wrong about the remedy.
    # `rb5s6s.fibre` is the PROSPECTIVE layer, and
    # tests/test_module_boundaries.py forbids a core module importing it:
    # the published analysis must not depend on unbuilt hardware. Hoisting
    # it into this namespace was tried on 2026-08-28 and that guard refused
    # it within one suite run.
    #
    # It is reachable, and the route is `from rb5s6s.fibre import solve_he11`.
    # What was actually missing is that no page said so, which is a
    # documentation fix and not an API one.
]
