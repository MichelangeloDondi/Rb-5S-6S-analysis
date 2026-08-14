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
    # 1 / (2 pi * 45.57 ns) = 3492537.7 Hz = 3.4925 MHz on the transition
    # axis. This asserted 3.4926e6 until 2026-08-15, a rounding of the
    # fourth decimal in the wrong direction, and the 2e-4 tolerance was
    # loose enough to pass anyway, so the guard was pinning a value the
    # code never produced. Tightened tenfold so it pins the real one.
    assert math.isclose(K.GAMMA_NAT_HZ, 3.4925e6, rel_tol=2e-5)


def test_tooth_spacing_axis_convention():
    # The EOM drive is the ABSOLUTE SCALE of the frequency ruler: every width
    # and shift in this analysis is measured in teeth, so a wrong Omega scales
    # the whole result set linearly. Pin the value, not only its bookkeeping --
    # both assertions below read Omega from the module under test, so a
    # 12.5 -> 125 MHz typo satisfied them and the entire suite stayed green.
    # The number is the EOM-02-12.5-V drive.
    assert K.OMEGA_EOM_HZ == 12.5e6
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


def test_the_unshifted_term_energy_really_is_the_hyperfine_centroid():
    """The (2F+1)-weighted hyperfine shifts must sum to zero.

    Added 2026-08-09 because the wavemeter-offset statement had ASSUMED that
    the NIST term energy is a centroid rather than checked it. If the weighted
    shifts did not cancel, every per-component prediction below would carry a
    hidden offset.
    """
    from rb5s6s.constants import (A_6S_RB85_HZ, A_6S_RB87_HZ,
                                  HFS_GROUND_RB85_HZ, HFS_GROUND_RB87_HZ,
                                  hyperfine_shift_hz)
    for I2, A6, split in ((3, A_6S_RB87_HZ, HFS_GROUND_RB87_HZ),
                          (5, A_6S_RB85_HZ, HFS_GROUND_RB85_HZ)):
        A5 = split / (I2 / 2.0 + 0.5)
        for A in (A5, A6):
            lo, hi = (I2 - 1) // 2, (I2 + 1) // 2
            s = sum((2 * F + 1) * hyperfine_shift_hz(A, I2, F) for F in (lo, hi))
            assert abs(s) < 1.0, f"I2={I2} A={A}: weighted shifts sum to {s} Hz"


def test_the_label_offsets_are_one_common_mode_wavemeter_error():
    """Each label against the component it names, not against the centroid.

    The four offsets must agree to well inside the labels' own quantisation,
    which is what shows them to be one calibration error rather than four
    independent mistakes. Pinned so a change to a label or a hyperfine constant
    cannot quietly turn a calibration statement into a physics statement.
    """
    from rb5s6s.constants import PEAKS, C_M_PER_S, label_offset_mhz
    offs = [label_offset_mhz(k) for k in sorted(PEAKS)]
    mean = sum(offs) / len(offs)
    spread = max(offs) - min(offs)
    # the labels carry four decimal places in nm; that step is ~61 MHz here
    lam = 993.4192e-9
    quantum_mhz = 2.0 * C_M_PER_S * 1e-13 / lam**2 / 1e6
    assert spread < quantum_mhz, (
        f"spread {spread:.1f} MHz exceeds the label quantisation "
        f"{quantum_mhz:.1f} MHz, so the offsets are not common-mode")
    assert 250.0 < mean < 340.0, f"mean label offset {mean:.1f} MHz moved"
    # and the isotope-centroid choice must be a pure common-mode shift
    alt = [label_offset_mhz(k, centroid_isotope=87) for k in sorted(PEAKS)]
    assert abs((max(alt) - min(alt)) - spread) < 0.1
    assert abs((sum(alt) / len(alt) - mean) - 99.189) < 0.01
