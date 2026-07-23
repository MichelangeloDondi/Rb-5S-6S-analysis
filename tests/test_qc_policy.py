"""Guards on the exclusion policy itself, not on any one threshold."""


def test_no_hard_flag_reads_a_quantity_the_physics_fits():
    """The plan's exclusion rule is "QC-based, never result-based" (rb5s6s/qc.py).

    That holds structurally only while the flag criteria stay disjoint from the
    observables the fits report. hard_flags() reads its metrics dict `m`, so the
    rule is testable: no `m[...]` lookup inside hard_flags may name a width, a
    centre or an amplitude. A future flag keyed on `fwhm_ms` would silently
    convert curation into a result-based cut -- the exact thing the plan forbids.
    """
    import inspect, re
    from rb5s6s import qc

    src = inspect.getsource(qc.hard_flags)
    read = set(re.findall(r'm\[["\']([a-z0-9_]+)["\']\]', src))
    read |= set(re.findall(r'm\.get\(\s*["\']([a-z0-9_]+)["\']', src))
    assert read, "no metric lookups found -- the regex has gone stale, not the code"

    FITTED = ("fwhm", "width", "gamma", "sigma", "centre", "center",
              "height", "amp", "area", "beta")
    offenders = sorted(k for k in read if any(f in k for f in FITTED))
    assert not offenders, (
        "hard_flags() keys an exclusion on a quantity the physics fits: "
        f"{offenders}. Exclusions must stay QC-based (clipping, glitches, "
        "baseline, SNR, comb) -- never result-based."
    )


def test_audit_report_warns_when_it_names_a_colliding_filename():
    """The audit reasons about backup copies whose names ALSO exist in data_raw/
    holding different traces -- 9 of the 19 do. A reader who resolves a cited
    name against data_raw/ gets a different trace and different numbers, and
    reads it as an error in the report. So: if the report names any CSV that
    also exists in data_raw/, it must carry the collision warning.
    """
    import re
    from pathlib import Path

    report = Path("docs/PREREGISTRATION_RESULTS.md")
    text = report.read_text(encoding="utf-8")
    named = set(re.findall(r"`([0-9]{4}nm_[0-9a-z_]+\.csv)`", text))
    in_repo = {p.name for p in Path("data_raw").rglob("*.csv")}
    colliding = sorted(named & in_repo)
    if not colliding:
        return
    assert "collision, not a contradiction" in text, (
        f"{report} names {len(colliding)} file(s) that also exist in data_raw/ "
        f"with different content ({colliding[:3]}...) but has lost the warning "
        "that cited names refer to the backup copies, identified by hash."
    )


def test_drift_settling_script_degrades_cleanly_without_the_backup(tmp_path):
    """The drift-rate recovery needs the timestamp backup, which never ships.
    Without it the script must exit 0 with the no-clock message -- CI has no
    backup, so anything else breaks the build for machines that lack a clock.
    """
    import os
    import subprocess
    import sys

    env = dict(os.environ, RB5S6S_BACKUP_DIR=str(tmp_path / "nope"))
    out = subprocess.run(
        [sys.executable, "scripts/run_drift_settling.py"],
        capture_output=True, text=True, env=env, timeout=120)
    assert out.returncode == 0, out.stderr
    assert "no timestamp backup" in out.stdout


def test_drift_settling_numbers_match_the_addendum():
    """Addendum 4 quotes +0.55 +/- 0.17 ms/min settled and a dAIC ~ +21 for the
    exponential. If the backup is present, re-run the estimator and hold the
    report to its own script -- the doc must not drift from the code.
    """
    import os
    import re
    import subprocess
    import sys
    from pathlib import Path

    import pytest

    backup = Path(os.environ.get(
        "RB5S6S_BACKUP_DIR",
        os.path.expanduser("~/Documents/RawDataBackUp_QUARANTINE_2026-07-23")))
    if not backup.is_dir():
        pytest.skip("timestamp backup not on this machine")

    out = subprocess.run(
        [sys.executable, "scripts/run_drift_settling.py"],
        capture_output=True, text=True, timeout=300).stdout
    m = re.search(r"agree to \+([\d.]+) \+/- ([\d.]+) ms/min", out)
    assert m, out
    doc = Path("docs/PREREGISTRATION_RESULTS.md").read_text(encoding="utf-8")
    assert f"+0.{m.group(1).split('.')[1]}" in doc and m.group(2) in doc, (
        f"script says settled {m.group(1)} +/- {m.group(2)} ms/min; "
        "addendum 4 quotes something else")
