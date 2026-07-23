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
