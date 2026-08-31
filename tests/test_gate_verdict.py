"""The gate's verdict decision, tested as the module it now is.

Reader-role: the resumed session, whose gates must tell it the truth.

The first implementation of this decision was shell inside ci_gate.sh; it
shipped dead under pipefail (the loop's last iteration killed the
assignment) and blind to ERROR lines, and neither defect was visible by
reading. The decision now lives in scripts/compute_gate_verdict.py, and
this file is its standing plant: verdict() in every direction, main()'s
own argument handling (the seam the shell actually calls), fixtures for
the register format's load-bearing rules, and the live register pinned as
an exact parse so a machine-line edit there fails here until both move
together.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "cgv", ROOT / "scripts" / "compute_gate_verdict.py")
cgv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cgv)

REGISTER_FIXTURE = """# register fixture

## 1. The worktree pair

signature-tests: tests/test_a.py::test_one tests/test_a.py::test_two
gate-excusable: yes

## 2. The freshness false-fail

signature-tests: tests/test_b.py::test_three
gate-excusable: yes

## 3. Never excusable

signature-tests: none
gate-excusable: no - always special-cause under a gate.

## 10. A double-digit entry

signature-tests: tests/test_c.py::test_ten
gate-excusable: yes
"""


def _with_register(tmp_path, text=REGISTER_FIXTURE):
    reg = tmp_path / "register.md"
    reg.write_text(text)
    old = cgv.REGISTER
    cgv.REGISTER = reg
    return old


def test_green_rc_is_pass(tmp_path):
    """rc 0 is PASS whatever the log says; the shell invokes the module
    unconditionally, so this branch is the live green path."""
    assert cgv.verdict(0, "anything") == "PASS"


def test_worktree_only_failure_is_pass_modulo(tmp_path):
    old = _with_register(tmp_path)
    try:
        log = "FAILED tests/test_a.py::test_one - assert nested"
        assert cgv.verdict(1, log) == "PASS_MODULO 1"
    finally:
        cgv.REGISTER = old


def test_two_entries_both_named(tmp_path):
    old = _with_register(tmp_path)
    try:
        log = ("FAILED tests/test_a.py::test_one - x\n"
               "FAILED tests/test_b.py::test_three - y")
        assert cgv.verdict(1, log) == "PASS_MODULO 1,2"
    finally:
        cgv.REGISTER = old


def test_entry_order_is_numeric_not_lexical(tmp_path):
    """Entry 10 must sort after 2, not between 1 and 2: the live register
    will reach double digits and a lexical sort would misreport which
    entries excused the run."""
    old = _with_register(tmp_path)
    try:
        log = ("FAILED tests/test_b.py::test_three - y\n"
               "FAILED tests/test_c.py::test_ten - z")
        assert cgv.verdict(1, log) == "PASS_MODULO 2,10"
    finally:
        cgv.REGISTER = old


def test_a_real_failure_beside_an_excusable_one_is_fail(tmp_path):
    old = _with_register(tmp_path)
    try:
        log = ("FAILED tests/test_a.py::test_one - x\n"
               "FAILED tests/test_real.py::test_defect - y")
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_error_lines_count_as_failures(tmp_path):
    """ERROR is a failure: the first version read only FAILED and would
    have excused fixture and teardown errors wholesale."""
    old = _with_register(tmp_path)
    try:
        log = "ERROR tests/test_real.py::test_defect - fixture died"
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_parametrized_ids_match_their_bare_signature(tmp_path):
    """One signature covers every parameterisation of its test, by the
    stated convention: the register names tests, not parameter points."""
    old = _with_register(tmp_path)
    try:
        log = "FAILED tests/test_a.py::test_one[docs/x.md] - y"
        assert cgv.verdict(1, log) == "PASS_MODULO 1"
    finally:
        cgv.REGISTER = old


def test_collection_crash_with_no_failure_lines_is_fail(tmp_path):
    old = _with_register(tmp_path)
    try:
        assert cgv.verdict(2, "INTERNALERROR> boom") == "FAIL"
    finally:
        cgv.REGISTER = old


def test_missing_register_excuses_nothing(tmp_path):
    old = cgv.REGISTER
    cgv.REGISTER = tmp_path / "absent.md"
    try:
        log = "FAILED tests/test_a.py::test_one - x"
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_no_signature_inheritance_between_entries(tmp_path):
    """An entry with no signature line of its own excuses nothing -- and
    must not inherit the previous entry's ids. The planted id belongs to
    entry 1, so a parser that leaks entry 1's signatures into entry 3
    reports two entries where one fired."""
    reg = REGISTER_FIXTURE.replace(
        "signature-tests: none\n", "")
    old = _with_register(tmp_path, reg)
    try:
        log = "FAILED tests/test_a.py::test_one - x"
        assert cgv.verdict(1, log) == "PASS_MODULO 1"
        log2 = "FAILED tests/test_unlisted.py::test_x - y"
        assert cgv.verdict(1, log2) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_gate_excusable_no_is_not_excusable(tmp_path):
    reg = REGISTER_FIXTURE.replace(
        "## 3. Never excusable\n\nsignature-tests: none",
        "## 3. Never excusable\n\nsignature-tests: tests/test_d.py::test_four")
    old = _with_register(tmp_path, reg)
    try:
        log = "FAILED tests/test_d.py::test_four - x"
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_gate_excusable_conditional_is_not_excusable(tmp_path):
    """conditional marks a human reading rule; the parser must treat it
    exactly like no, or a prose narrowing becomes an unconditional pass."""
    reg = REGISTER_FIXTURE.replace("gate-excusable: yes\n\n## 2.",
                                   "gate-excusable: conditional - human.\n\n## 2.")
    old = _with_register(tmp_path, reg)
    try:
        log = "FAILED tests/test_a.py::test_one - x"
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_a_bare_filename_signature_is_ignored(tmp_path):
    """A signature without :: could excuse a whole-file collection ERROR;
    the parser drops it, so the entry excuses nothing by that line."""
    reg = REGISTER_FIXTURE.replace(
        "signature-tests: tests/test_b.py::test_three",
        "signature-tests: tests/test_b.py")
    old = _with_register(tmp_path, reg)
    try:
        log = "ERROR tests/test_b.py - collection failed"
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_a_drift_line_vetoes_every_excuse(tmp_path):
    """A log containing 'drifted from' is special-cause whatever ids it
    carries: a committed CSV that stops matching its producer must never
    ride a register entry out of the gate."""
    old = _with_register(tmp_path)
    try:
        log = ("FAILED tests/test_a.py::test_one - "
               "results/x.csv drifted from run_x.py")
        assert cgv.verdict(1, log) == "FAIL"
    finally:
        cgv.REGISTER = old


def test_main_bad_arguments_print_fail_and_exit_zero(tmp_path):
    """The caller acts on the printed word; main() classifies malformed
    input as FAIL instead of dying, so a set -e shell survives it."""
    script = ROOT / "scripts" / "compute_gate_verdict.py"
    for args in (["x", "/dev/null"], ["1"], ["1", str(tmp_path / "no.log")]):
        r = subprocess.run([sys.executable, str(script), *args],
                           capture_output=True, text=True)
        assert r.returncode == 0, args
        assert r.stdout.strip() == "FAIL", args


@pytest.mark.skipif(not cgv.REGISTER.is_file(),
                    reason="private/COMMON_CAUSE_REGISTER.md is absent in "
                           "every clone but the working one; the fixture "
                           "tests above are the portable plant")
def test_the_live_register_parses_to_exactly_the_expected_map():
    """The live register's machine lines, pinned as an exact map: editing
    one there means updating this test in the same change, which is the
    register's own stated contract. Every signature id must also resolve
    to a real test, or a rename silently empties the excuse."""
    assert cgv.excusable_map() == {
        "1": {"tests/test_no_stale_duplicates.py::"
              "test_no_nested_checkout_below_the_root"},
    }
    for ids in cgv.excusable_map().values():
        for sig in ids:
            fname, test = sig.split("::", 1)
            path = ROOT / fname
            assert path.is_file(), sig
            assert f"def {test.split('[')[0]}(" in path.read_text(), sig


def test_a_qualified_yes_does_not_excuse(tmp_path):
    """`gate-excusable: yes, but only when ...` is a condition wearing a
    yes. The parser must read exact `yes` only, or prose qualifications
    silently widen the excusable set."""
    reg = tmp_path / "reg.md"
    reg.write_text(
        "## 1. q\n\n"
        "signature-tests: tests/test_x.py::test_y\n"
        "gate-excusable: yes, but only when the moon is full\n")
    old = cgv.REGISTER
    cgv.REGISTER = reg
    try:
        assert cgv.excusable_map() == {}
    finally:
        cgv.REGISTER = old


def test_the_freshness_arg_split_and_the_veto_share_their_phrase(tmp_path):
    """Two contracts that shipped unguarded. The registry key
    "run_saturation_probe --emit" must split into script and arguments
    (the joined form was unrunnable for the entry's whole life), and the
    producer's drift message must carry the exact substring the verdict
    module vetoes on - two copies of one English phrase, bound here so a
    reword on either side fails a test instead of silently disarming the
    veto."""
    import importlib.util as ilu
    spec = ilu.spec_from_file_location(
        "vrf", ROOT / "scripts" / "verify_results_fresh.py")
    vrf = ilu.module_from_spec(spec)
    spec.loader.exec_module(vrf)
    src = (ROOT / "scripts" / "verify_results_fresh.py").read_text()
    assert 'script.split()' in src, "the arg-split left the invocation path"
    assert cgv.DRIFT_VETO in src, (
        "the producer no longer prints the phrase the veto matches; "
        "reword both sides together or the veto is disarmed silently")
    name_and_args = "run_saturation_probe --emit".split()
    assert name_and_args[0] == "run_saturation_probe"
    assert name_and_args[1:] == ["--emit"]
