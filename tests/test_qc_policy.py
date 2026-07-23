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
