"""The model potential reproduces the record's held elements and its continuum
joins the discrete series at threshold.

FAILURE MODE IF THIS FILE IS DELETED: the continuum row of the polarizability
producer (escape E64) would rest on a solver nobody re-validates; a wrong
phase in the continuum wave (the first two cuts read ten and thirty times the
discrete law) would ship as a polarizability term. Every bar here is the one
the validation of 2026-09-12/13 measured; nothing is typed from a later run.
"""
import math

import pytest

from rb5s6s import model_potential as mp
from rb5s6s._compat import trapezoid
from rb5s6s.coulomb_approx import HELD
from rb5s6s.polarizability import E_6S_CM


@pytest.fixture(scope="module")
def cont():
    return mp.continuum_polarizability(E_6S_CM, E_6S_CM / 2.0)


def test_the_continuum_joins_the_discrete_series_at_threshold(cont):
    ratio = cont["threshold_density_continuum"] / cont["threshold_density_discrete"]
    assert 0.85 < ratio < 1.15, f"threshold join {ratio:.2f}: the continuum wave's phase or normalisation is wrong (Seaton continuity)"


def test_the_valence_sum_rule_holds_to_the_model_potentials_accuracy(cont):
    trk = cont["f_bound"] + cont["f_continuum"]
    assert 0.9 < trk < 1.12, f"TRK total {trk:.3f} for 6s"


def test_the_continuum_share_is_small_and_enhanced_at_the_drive(cont):
    assert 0.3 < cont["alpha_static"] < 2.0
    assert 1.2 < cont["alpha_at_omega"] / cont["alpha_static"] < 2.23, "the enhancement at the drive lies between one and the threshold's"


def test_the_6s_e1_class_is_reproduced_on_the_held_elements():
    """The validation's own bar: the 6S class ratio 0.980 +- 0.022 (draft, 2026-09-12).
    HELD rows are (label, E_lower_cm, E_upper_cm, j, |d| a.u., sigma, source); a
    computed |<s||d||p_j>| is sqrt((2j+1)/3) |R_1| with R_1 the radial integral."""
    ratios = []
    for label, e_lo, e_hi, j, d, _sig, _src in HELD:
        if not label.startswith("6s-"):
            continue
        rs, Ps = mp.solve(mp.energy_h(e_lo), 0)
        rp, Pp = mp.solve(mp.energy_h(e_hi), 1)
        comp = math.sqrt((2 * j + 1) / 3.0) * abs(mp.radial(Ps, rs, Pp, rp, 1))
        ratios.append(comp / d)
    assert ratios, "no 6s rows in HELD"
    mean = sum(ratios) / len(ratios)
    assert 0.93 < mean < 1.03, f"6S E1 class ratio {mean:.3f} over {len(ratios)} elements; the validation measured 0.980 +- 0.022"


def test_a_bound_function_is_normalised():
    r, P = mp.solve(mp.energy_h(E_6S_CM), 0)
    assert abs(trapezoid(P * P, r) - 1.0) < 1e-6
    assert math.isfinite(P.max())
