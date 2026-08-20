"""Rule 19.7 as extended 2026-08-20: a difference is read in units of the
quantity's own error, not as a percentage.

WHY THIS EXISTS. `scripts/verify_results_fresh.py` compared committed CSVs
against fresh producer runs by RELATIVE difference alone, and on 2026-08-20 it
reported drifts up to 13 per cent that were 0.081 sigma. The error columns
were in the same rows, unused. These tests pin the fix, and the last of them
is the ceiling test: a move that genuinely matters still fails.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "_vrf", ROOT / "scripts" / "verify_results_fresh.py")
vrf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vrf)


def test_both_error_column_conventions_are_read():
    """results/ uses `value` beside `err`, and `<name>` beside `<name>_err`."""
    assert vrf._paired_error({"value": "1.0", "err": "0.25"}, "value") == 0.25
    assert vrf._paired_error(
        {"gamma_coll": "0.78", "gamma_coll_err": "0.23"}, "gamma_coll") == 0.23


def test_a_missing_or_useless_error_falls_back_to_the_relative_tolerance():
    assert vrf._paired_error({"value": "1.0"}, "value") is None
    assert vrf._paired_error({"value": "1.0", "err": "0"}, "value") is None
    assert vrf._paired_error({"value": "1.0", "err": ""}, "value") is None


def test_a_move_inside_its_own_error_reproduces():
    """The 2026-08-20 false alarm. Thirteen per cent on a parameter whose
    error is more than three times its value is 0.04 sigma, and the record
    already publishes that parameter as unresolved."""
    committed = [{"quantity": "sigma_laser", "sigma_laser": "0.4052",
                  "sigma_laser_err": "1.427"}]
    fresh = [{"quantity": "sigma_laser", "sigma_laser": "0.3531",
              "sigma_laser_err": "1.427"}]
    assert vrf._differs(committed, fresh, csv_name="x.csv") is None


def test_the_message_states_the_sigma_before_the_percentage():
    """A percentage is reported only ALONGSIDE the sigma, never instead."""
    committed = [{"quantity": "q", "value": "1.000", "err": "0.010"}]
    fresh = [{"quantity": "q", "value": "1.100", "err": "0.010"}]
    msg = vrf._differs(committed, fresh, csv_name="x.csv")
    assert msg is not None
    assert "sigma of its own error" in msg
    assert "relative" in msg


def test_a_move_that_matters_still_fails():
    """The ceiling test. A well-conditioned number moving by ten of its own
    errors must not be acquitted by the new path."""
    committed = [{"quantity": "q", "value": "1.000", "err": "0.010"}]
    fresh = [{"quantity": "q", "value": "1.100", "err": "0.010"}]
    assert vrf._differs(committed, fresh, csv_name="x.csv") is not None


def test_a_column_with_no_error_keeps_the_old_behaviour():
    """Nothing is loosened where the producer emits no uncertainty."""
    committed = [{"quantity": "q", "value": "1.000"}]
    fresh = [{"quantity": "q", "value": "1.100"}]
    assert vrf._differs(committed, fresh, csv_name="x.csv") is not None


def test_the_tolerance_is_tight_enough_to_be_worth_having():
    assert vrf.SIGMA_TOL <= 0.5
