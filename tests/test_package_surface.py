"""The installable surface: what a wheel promises, checked in-process.

WHY THIS EXISTS. rb5s6s is importable two ways, and they behave differently.
From a checkout, every path in config.py resolves two directories up and finds
the repository. From an INSTALLED WHEEL those same paths land inside
site-packages, where data_raw/ and results/ do not exist, so anything reading
committed data fails on a path the caller has never heard of.

The split the package promises is therefore: the names re-exported from
`rb5s6s` are PURE and work from a wheel, and a data-reading call fails with the
cause named rather than a site-packages path. A wheel build on 2026-08-10
confirmed the pure half on Python 3.14 in a clean venv outside the repository.
These are the in-process checks that keep it true, since a full wheel-install
test needs network and a build step that the fast suite cannot afford.

THE SIX DISK-READING MODULES SPLIT INTO TWO CONTRACTS, and the tests below
keep both. `ingest.load_manifest`, `rate_model.load_clock` and
`cavity_scan.load_scan` on its default path REQUIRE the repository and raise
`RepoDataMissing` naming the cause. `qc.outlier_files` and
`ruler.campaign_rate_relsyst` DEGRADE ON PURPOSE, returning an empty set and
0.0, which each says in its own docstring so that a checkout without a
quality or ruler run behaves as it did before.

Until 2026-08-15 `RepoDataMissing` had no call site outside `config` at all,
while three documents said otherwise, and the only test here exercised
`require_repo_data` in isolation, so nothing would have noticed.
"""
from __future__ import annotations

import importlib
import sys

import pytest

import rb5s6s


def test_the_exported_surface_is_stable_and_nonempty():
    """__all__ is the package's promise, so it should not shrink silently."""
    assert rb5s6s.__all__, "the namespace exports nothing"
    missing = [n for n in rb5s6s.__all__ if not hasattr(rb5s6s, n)]
    assert not missing, f"__all__ names something absent: {missing}"
    # the seam-map names docs/ADAPTING.md tells a reader to reach for
    for name in ("stark_ramp", "stark_shift_S0_mhz", "model_profile",
                 "delta_alpha", "two_photon_rabi_hz", "W0_MEASURED_M"):
        assert name in rb5s6s.__all__, f"{name} dropped from the public surface"


def test_every_exported_name_is_pure():
    """Nothing on the exported surface may need the repository.

    A wheel carries the package and NOT data_raw/ or results/, so an exported
    name that reads either is a promise the wheel cannot keep. This checks the
    property that makes the promise true: none of the modules the exports come
    from resolves a repository path at import time or on call.
    """
    import rb5s6s.config as cfg
    # the pure calls below must not touch these, so make them impossible to
    # satisfy and check the calls still work
    for fn, args in (
        (rb5s6s.stark_shift_S0_mhz, (0.225, 64e-6)),
        (rb5s6s.two_photon_rabi_hz, (0.225, 64e-6, 0.94)),
        (rb5s6s.delta_alpha, (993.4192,)),
        (rb5s6s.two_photon_matrix_element, (993.4192,)),
        (rb5s6s.alpha_5s, (993.4192,)),
        (rb5s6s.alpha_6s, (993.4192,)),
    ):
        val = fn(*args)
        assert val == val, f"{fn.__name__} returned NaN"  # NaN-safe finiteness
    assert hasattr(cfg, "require_repo_data")
    assert hasattr(cfg, "RepoDataMissing")


def test_require_repo_data_names_the_cause_when_the_tree_is_absent(tmp_path,
                                                                  monkeypatch):
    """The wheel failure mode, reproduced by pointing the paths at nothing.

    Verified for real on 2026-08-10 against an installed wheel in a clean venv:
    the message names the site-packages path it resolved to and says what to
    clone. This reproduces the same branch without a build.
    """
    import rb5s6s.config as cfg
    monkeypatch.setattr(cfg, "DATA_RAW_DIR", tmp_path / "nope_data_raw")
    monkeypatch.setattr(cfg, "RESULTS_DIR", tmp_path / "nope_results")
    for what in ("data_raw", "results"):
        with pytest.raises(cfg.RepoDataMissing) as exc:
            cfg.require_repo_data(what)
        msg = str(exc.value)
        assert what in msg, "the error should name which tree is missing"
        assert "clone" in msg.lower(), "the error should say how to fix it"


def test_the_pure_modules_import_without_the_data_modules():
    """Importing the physics from a wheel must not drag in a disk-reading module.

    Checked by importing the pure modules into a fresh module namespace with
    the data-reading ones evicted, which fails loudly if one of them is a
    hidden import-time dependency.
    """
    data_modules = ["rb5s6s.ingest", "rb5s6s.qc", "rb5s6s.rate_model",
                    "rb5s6s.ruler", "rb5s6s.cavity_scan"]
    saved = {m: sys.modules.pop(m, None) for m in data_modules}
    try:
        for m in ("rb5s6s.lineshape", "rb5s6s.polarizability",
                  "rb5s6s.hyperpolarizability", "rb5s6s.constants"):
            sys.modules.pop(m, None)
            importlib.import_module(m)
        still_absent = [m for m in data_modules if m not in sys.modules]
        assert still_absent == data_modules, (
            "importing the pure surface pulled in a data-reading module: "
            f"{[m for m in data_modules if m in sys.modules]}")
    finally:
        for m, mod in saved.items():
            if mod is not None:
                sys.modules[m] = mod


def test_the_required_data_loaders_name_the_cause(tmp_path, monkeypatch):
    """The three loaders that genuinely need the repository say so when it is absent.

    Added 2026-08-15. Until then `RepoDataMissing` had no call site outside
    `config` itself, so `ingest.load_manifest` and `rate_model.load_clock`
    raised a bare FileNotFoundError naming a path inside site-packages, which
    is the outcome that error class was written to prevent. The claim that
    they did otherwise sat in three documents and in this file's own
    docstring, and the only test for it exercised `require_repo_data` alone,
    so nothing would have noticed.

    NOT COVERED HERE ON PURPOSE: `qc.outlier_files` and
    `ruler.campaign_rate_relsyst` return an empty set and 0.0 when their
    tables are absent. That is a deliberate contract stated in each of their
    own docstrings, so a checkout without a quality or ruler run behaves as
    it did before, and turning it into a raise would break it.
    """
    import rb5s6s.config as cfg
    import rb5s6s.ingest as ingest
    import rb5s6s.rate_model as rate_model
    import rb5s6s.cavity_scan as cavity_scan

    monkeypatch.setattr(cfg, "DATA_RAW_DIR", tmp_path / "nope_data_raw")
    monkeypatch.setattr(cfg, "RESULTS_DIR", tmp_path / "nope_results")

    for label, call in (
        ("ingest.load_manifest", ingest.load_manifest),
        ("rate_model.load_clock", rate_model.load_clock),
        ("cavity_scan.load_scan", cavity_scan.load_scan),
        # science_times is here because the first version of this test was not
        # exercising it, and that is exactly where the hole survived: it
        # resolves the default root itself before calling load_clock, so
        # load_clock's guard could not fire through it. Test the entry point
        # callers use, not only the helper underneath it.
        ("rate_model.science_times", lambda: rate_model.science_times("p_sweep")),
    ):
        with pytest.raises(cfg.RepoDataMissing) as exc:
            call()
        msg = str(exc.value)
        assert "data_raw" in msg, f"{label} did not name which tree is missing"
        assert "clone" in msg.lower(), f"{label} did not say how to fix it"


def test_the_graceful_loaders_stay_graceful(tmp_path, monkeypatch):
    """The two that degrade on purpose must keep degrading.

    The counterpart to the test above, and the reason this pair exists rather
    than one sweeping rule: wiring the guard into these two would silently
    change what a partial checkout does, which is the opposite of the
    stability their docstrings promise.
    """
    import rb5s6s.config as cfg
    import rb5s6s.qc as qc
    import rb5s6s.ruler as ruler

    # Called with NO argument on purpose. The first version of this test
    # patched RESULTS_DIR and then passed an explicit results_dir anyway, and
    # both functions consult the module default only when the argument is
    # None, so the patch was inert and the branch under test was the wrong
    # one. The default path is the one a wheel install takes.
    #
    # Only the ruler assertion discriminates. This tree has no outlier files,
    # so `outlier_files()` returns an empty set with or without the patch and
    # that line proves only that it does not raise. `campaign_rate_relsyst()`
    # returns 0.0029 here and 0.0 under the patch, so it is the one that would
    # go red if the default stopped being consulted.
    monkeypatch.setattr(cfg, "RESULTS_DIR", tmp_path / "nope_results")
    assert qc.outlier_files() == set()
    assert ruler.campaign_rate_relsyst() == 0.0
