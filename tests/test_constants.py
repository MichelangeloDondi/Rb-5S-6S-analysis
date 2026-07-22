"""
Tests of the physical constants and of the peak-identification cross-check.

The second test encodes, permanently, the argument that locked the peak
identification WITHOUT the 3 GHz wide scans: the spacings between the four
file-label wavelengths must reproduce (Delta_HFS_ground - Delta_HFS_6S)/2
on the laser axis for each isotope (S->S two-photon, Delta F = 0 lines).
If someone ever edits a label or a hyperfine constant inconsistently, this
fails.
"""

import math

import pytest

from rb5s6s import constants as K


def _label_gap_laser_hz(label_a: str, label_b: str) -> float:
    """Laser-frequency gap implied by two file-label wavelengths (vacuum nm)."""
    la = K.PEAKS[label_a]["lambda_nm"] * 1e-9
    lb = K.PEAKS[label_b]["lambda_nm"] * 1e-9
    lmid = 0.5 * (la + lb)
    return abs(la - lb) * K.C_M_PER_S / lmid**2


def test_natural_width_value():
    # 1 / (2 pi * 45.57 ns) = 3.4926 MHz on the transition axis.
    assert math.isclose(K.GAMMA_NAT_HZ, 3.4926e6, rel_tol=2e-4)


def test_tooth_spacing_axis_convention():
    # Adjacent two-photon comb teeth: Omega/2 on the laser axis, Omega on the
    # transition axis. The factor-2 bookkeeping must never drift.
    assert K.TOOTH_SPACING_LASER_HZ == K.OMEGA_EOM_HZ / 2.0
    assert K.TOOTH_SPACING_TRANSITION_HZ == 2.0 * K.TOOTH_SPACING_LASER_HZ


def test_peak_identification_87rb():
    # 87Rb F=2->2 (4207) vs F=1->1 (4121):
    # transition gap = HFS_ground(87) - 2*A_6S(87); laser gap = half of that.
    predicted = (K.HFS_GROUND_RB87_HZ - 2.0 * K.A_6S_RB87_HZ) / 2.0
    measured = _label_gap_laser_hz("4207", "4121")
    assert abs(measured / predicted - 1.0) < 0.01  # passes at ~0.1%


def test_peak_identification_85rb():
    # 85Rb F=3->3 (4192) vs F=2->2 (4154): 6S splitting is 3*A (I=5/2).
    predicted = (K.HFS_GROUND_RB85_HZ - 3.0 * K.A_6S_RB85_HZ) / 2.0
    measured = _label_gap_laser_hz("4192", "4154")
    assert abs(measured / predicted - 1.0) < 0.01  # passes at ~0.4%


def test_peak_label_full_form():
    from rb5s6s.constants import peak_label
    assert peak_label("4192") == "993.4192 nm"
    assert peak_label("4192", isotope=True) == "993.4192 nm (85Rb)"
    assert peak_label("4207", isotope=True, line=True) == "993.4207 nm (87Rb F=2->2)"


def test_no_direct_trapezoid_outside_compat():
    # Recurrence guard: np.trapezoid is numpy 2.0+, so any direct use breaks
    # the declared numpy>=1.24 floor (it regressed into modelform.py after the
    # first fix, then into tests/scripts after that -- caught only by the
    # minimum-versions CI job, 2026-07-12). The shim in rb5s6s/_compat.py is
    # the ONLY place allowed to touch np.trapezoid / np.trapz, and this guard
    # now scans the package, the scripts AND the tests so it cannot slip past
    # again in a file the minimum job runs.
    import re
    from pathlib import Path
    call = re.compile(r"np\.(trapezoid|trapz)\s*\(")  # a CALL, not a doc mention
    root = Path(__file__).resolve().parents[1]
    offenders = []
    for sub in ("rb5s6s", "scripts", "tests"):
        for py in (root / sub).glob("*.py"):
            if py.name in ("_compat.py", "test_constants.py"):  # shim + this guard
                continue
            if call.search(py.read_text()):
                offenders.append(f"{sub}/{py.name}")
    assert not offenders, f"direct numpy trapezoid CALL outside _compat: {offenders}"


# --------------------------------------------------------------------------
# The drift envelope is in tension with the measured intra-block scatter.
# --------------------------------------------------------------------------
# The reference was NOT moved within a 5-repeat block (experimenter-confirmed
# 2026-07-22), so the ~0.08 MHz intra-block position scatter is drift
# accumulated over the block, not a re-centring artifact. For 5 evenly spaced
# traces under linear drift the scatter is rate x T x 0.354, so the 4 MHz/min
# envelope implies a block spanning ~3.4 s -- less than the 5 x 1.000 s of
# acquisition the block must contain. docs/PREREGISTRATION_timestamps.md 7
# pre-registers the resulting prediction (D0: the measured rate lands BELOW
# the envelope). This test pins the arithmetic behind that prediction so the
# envelope and the scatter cannot drift apart unnoticed.
INTRA_BLOCK_SCATTER_MHZ = 0.08   # MEASURED-HERE, DATA.md section 2
SPACING_FACTOR = 0.35355339      # std of [0, .25, .5, .75, 1]


def test_drift_envelope_is_in_tension_with_intra_block_scatter():
    import statistics
    assert statistics.pstdev([0, .25, .5, .75, 1.0]) == \
        pytest.approx(SPACING_FACTOR, abs=1e-6)
    rate_mhz_per_s = K.DRIFT_RATE_LASER_HZ_PER_MIN / 1e6 / 60.0
    implied_block_s = INTRA_BLOCK_SCATTER_MHZ / (rate_mhz_per_s * SPACING_FACTOR)
    assert implied_block_s == pytest.approx(3.4, abs=0.15)
    # the block must physically contain 5 acquisitions of TRACE_DT_S x N points
    floor_s = 5 * K.TRACE_N_POINTS * K.TRACE_DT_S
    assert floor_s == pytest.approx(5.0, abs=1e-9)
    assert implied_block_s < floor_s, (
        "the tension this test documents has gone away -- if the envelope or "
        "the scatter changed, docs/PREREGISTRATION_timestamps.md 7 (prediction "
        "D0) must be revisited, and it may no longer be pre-data")


@pytest.mark.parametrize("block_s,lo,hi", [(10, 1.2, 1.5), (60, 0.20, 0.25)])
def test_preregistered_drift_rate_band(block_s, lo, hi):
    """The 0.2-1.4 MHz/min band quoted in the pre-registration for 10-60 s
    blocks. Pinned so the quoted band matches the arithmetic that produced it."""
    rate = INTRA_BLOCK_SCATTER_MHZ / (block_s * SPACING_FACTOR) * 60
    assert lo <= rate <= hi
    assert rate < K.DRIFT_RATE_LASER_HZ_PER_MIN / 1e6
