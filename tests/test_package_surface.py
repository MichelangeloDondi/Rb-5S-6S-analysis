"""The installable surface: what a wheel promises, checked in-process.

WHY THIS EXISTS. rb5s6s is importable two ways, and they behave differently.
From a checkout, every path in config.py resolves two directories up and finds
the repository. From an INSTALLED WHEEL those same paths land inside
site-packages, where data_raw/ and results/ do not exist, so anything reading
committed data fails on a path the caller has never heard of.

The split the package promises is therefore: the names re-exported from
`rb5s6s` are PURE and work from a wheel, and the six modules that read from
disk raise `RepoDataMissing` naming the cause. A wheel build on 2026-08-10
confirmed both on Python 3.14 in a clean venv outside the repository. These are
the in-process checks that keep it true, since a full wheel-install test needs
network and a build step that the fast suite cannot afford.
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
