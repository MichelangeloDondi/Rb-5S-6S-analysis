"""The kernel Monte Carlo's closed-form limit, which the gate runs and the floor does not (O59 F2, 2026-09-25).

`scripts/run_kernel_mc.limit_check` is the Lehmann-class plant of `transit_fwhm_from_w0`: with the collected window
closed and the drive weak the node sampler must return the closed-form cusp, its width to half a per cent. Its
tolerance is the sampler's own noise at 100 000 atoms, so it cannot be made cheaper without ceasing to be the check,
and it left the forty-second floor for the gate. FAILURE MODE IF THIS FILE IS DELETED: the limit runs nowhere, and a
sampler that drifted from its closed form would reach every kernel node unseen.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.slow
def test_the_node_sampler_meets_its_closed_form_limit():
    spec = importlib.util.spec_from_file_location("kmc_limit", ROOT / "scripts" / "run_kernel_mc.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.limit_check() == 0
