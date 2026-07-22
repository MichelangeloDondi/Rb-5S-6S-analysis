"""Docs <-> computation sync for the diverging-beam ramp-geometry moments.

The g1 sign-flip discussion (PLAN section 8.3 #4, methods/03, the
run_ramp_geometry docstring, config's Z_c envelope note) quotes specific
moment coefficients and the crossover location. A stale-number incident
(2026-07-22: PLAN still quoted "g1 +0.40, 10-40% modified" for the archival
geometry, a leftover of the superseded 32 um waist that contradicted both
methods/03 and the script output) motivated pinning every quoted value to
the function that produces it. If lineshape.stark_ramp_axial_moments or the
config geometry changes, these tests name the documents that must move with
it.
"""

from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import brentq

from rb5s6s.lineshape import stark_ramp_axial_moments

ROOT = Path(__file__).resolve().parents[1]

LAMBDA_M = 993.4e-9
ZC_PLACEHOLDER_M = 2.0e-3  # config.RAMP_COLLECTION_HALFLENGTH_MM_ENVELOPE[1]


def _z_ratio(w0_um: float) -> float:
    z_r = np.pi * (w0_um * 1e-6) ** 2 / LAMBDA_M
    return ZC_PLACEHOLDER_M / z_r


def _g1(z_ratio: float) -> float:
    return stark_ramp_axial_moments(1.0, z_ratio)["skew_standardized"]


def test_pure_triangle_benchmark():
    m = stark_ramp_axial_moments(1.0, 1e-6)
    assert m["mean"] == pytest.approx(-2.0 / 3.0, abs=2e-3)
    assert m["skew_standardized"] == pytest.approx(18**1.5 / 135, abs=2e-3)


def test_crossover_location_and_flip_condition():
    z_star = brentq(_g1, 0.8, 1.6, xtol=1e-4)
    assert z_star == pytest.approx(1.117, abs=0.01)
    # flip condition at the 16 um config, quoted as "~0.9 mm" in the docs
    z_r_16 = np.pi * (16e-6) ** 2 / LAMBDA_M
    assert z_star * z_r_16 * 1e3 == pytest.approx(0.90, abs=0.05)


# (doc file, tokens that must appear while the placeholder geometry stands)
DOC_TOKENS = [
    ("docs/PLAN.md", ["g1 +0.558", "Z_c/z_R ≈ 1.12", "r_PMT/M > 1.12 z_R"]),
    ("docs/methods/03_the_ac_stark_ramp.md",
     ["$+0.558$", "$-0.354$", "$+0.564$", "1.12"]),
    ("scripts/run_ramp_geometry.py", ["1.12", "r_PMT/M > ~0.9 mm"]),
    ("rb5s6s/config.py", ["1.12", "r_PMT/M"]),
    ("docs/THEORY_NOTE.md", ["$Z_c/z_R\\approx1.12$", "r_\\text{PMT}/M"]),
]


@pytest.mark.parametrize("relpath,tokens", DOC_TOKENS,
                         ids=[d for d, _ in DOC_TOKENS])
def test_docs_quote_current_coefficients(relpath, tokens):
    text = (ROOT / relpath).read_text(encoding="utf-8")
    missing = [t for t in tokens if t not in text]
    assert not missing, (
        f"{relpath} no longer quotes {missing}; if the geometry or the "
        f"moments code changed, update the document (and this registry) "
        f"together — see run_ramp_geometry.py."
    )


@pytest.mark.parametrize("w0_um,doc_g1", [(60.0, 0.564), (50.0, 0.558),
                                          (16.0, -0.354)])
def test_tabulated_g1_match_computation(w0_um, doc_g1):
    assert _g1(_z_ratio(w0_um)) == pytest.approx(doc_g1, abs=2e-3)
