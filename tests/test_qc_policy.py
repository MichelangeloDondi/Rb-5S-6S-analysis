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
    """The drift analysis must never break a machine that lacks its inputs.
    With the committed data_recovered/CLOCK.csv the private backup is no
    longer needed -- but qc_metrics.csv is gitignored, so on such machines
    (CI) the script must exit 0 with a graceful message; where everything is
    present it must run the full report off the table alone.
    """
    import os
    import subprocess
    import sys
    from pathlib import Path

    env = dict(os.environ, RB5S6S_BACKUP_DIR=str(tmp_path / "nope"))
    out = subprocess.run(
        [sys.executable, "scripts/run_drift_settling.py"],
        capture_output=True, text=True, env=env, timeout=600)
    assert out.returncode == 0, out.stderr
    if Path("results/qc_metrics.csv").is_file():
        assert "MIXTURE REFINEMENT" in out.stdout, (
            "table + qc_metrics present but the full report did not run:\n"
            + out.stdout)
    else:
        assert "qc_metrics.csv not present" in out.stdout


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

    if not Path("results/qc_metrics.csv").is_file():
        pytest.skip("qc_metrics.csv not present (gitignored dump)")

    out = subprocess.run(
        [sys.executable, "scripts/run_drift_settling.py"],
        capture_output=True, text=True, timeout=300).stdout
    m = re.search(r"agree to \+([\d.]+) \+/- ([\d.]+) ms/min", out)
    assert m, out
    doc = Path("docs/PREREGISTRATION_RESULTS.md").read_text(encoding="utf-8")
    assert f"+0.{m.group(1).split('.')[1]}" in doc and m.group(2) in doc, (
        f"script says settled {m.group(1)} +/- {m.group(2)} ms/min; "
        "addendum 4 quotes something else")
    # the state-space stage owns the headline now: constant drift + its CI
    k = re.search(
        r"c = (\+\d+\.\d+) \[(\+\d+\.\d+), (\+\d+\.\d+)\] ms/min \(68%\)", out)
    assert k, "state-space stage printed no constant-drift line:\n" + out
    for val in k.groups():
        assert val in doc, (
            f"script's state-space drift {k.group(0)!r} not quoted in addendum 5 "
            f"(missing {val})")
    # and the centre-channel pull bound must match addendum 6
    p = re.search(r"S0\(225 mW\) < (\d+\.\d) MHz transition from CENTRES", out)
    assert p, "pull stage printed no centre-channel bound:\n" + out
    assert f"< {p.group(1)} MHz" in doc, (
        f"script's centre-channel bound {p.group(1)} MHz not quoted in addendum 6")


def test_rekick_fit_numbers_match_addendum_12():
    """Addendum 12 quotes B = 103 ms, tau = 97 min and an AIC ordering. Those
    are now computed by run_drift_settling.py's re-kick stage, so the doc must
    not drift from the code -- the same doc<->script lock the drift and pull
    numbers already carry.
    """
    import os
    import re
    import subprocess
    import sys
    from pathlib import Path

    import pytest

    if not Path("results/qc_metrics.csv").is_file():
        pytest.skip("qc_metrics.csv not present (gitignored dump)")

    out = subprocess.run([sys.executable, "scripts/run_drift_settling.py"],
                         capture_output=True, text=True, timeout=900).stdout
    m = re.search(r"B = (\d+) ms = ([\d.]+) MHz laser, tau = (\d+) min", out)
    assert m, "re-kick stage printed no fitted amplitude/tau:\n" + out
    doc = Path("docs/PREREGISTRATION_RESULTS.md").read_text(encoding="utf-8")
    B, tau = m.group(1), m.group(3)
    assert f"B = {B} " in doc, f"script fits B = {B} ms; addendum 12 quotes something else"
    assert f"τ = {tau} " in doc, f"script fits tau = {tau} min; addendum 12 quotes something else"

    # and the structural claim: the re-kick must beat both the session clock
    # and the per-epoch-level control, or the addendum's argument is void
    d = re.search(r"dAIC \+([\d.]+) over the session clock, \+([\d.]+) over", out)
    assert d, out
    assert float(d.group(1)) > 4 and float(d.group(2)) > 4, (
        "the re-kick no longer beats its comparators -- addendum 12's argument "
        f"rests on both margins: {d.group(0)}")

    # the second-timescale postscript: its bounds must match the script too,
    # and its central claim is that the campaign component fits to ZERO
    for tau, ub in (("3 h", "44"), ("6 h", "20"), ("flat", "10")):
        assert re.search(rf"tau = {tau}\s*: A < \s*{ub} ms", out), (
            f"second-timescale bound at tau={tau} is no longer {ub} ms:\n" + out)
        assert f"| {tau.replace(' h',' h')} | {ub} ms" in doc or f"{ub} ms" in doc, (
            f"addendum 12's postscript does not quote the {ub} ms bound")
    amp = re.search(r"amplitude fits to ([\d.]+) ms", out)
    assert amp and float(amp.group(1)) < 1.0, (
        "the campaign component no longer fits to zero -- the postscript's "
        f"'absent, not merely unwarranted' claim would need revisiting: {out}")
