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

__version__ = "4.0"

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
)
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
]
