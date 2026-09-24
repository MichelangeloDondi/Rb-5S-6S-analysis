"""The stark joint fit's families survive a checkpoint unchanged (plan v5.1 RT46, 2026-09-22).

`scripts/run_stark_joint.py` is about five hours in one process, so it runs under the wave rule one family
per wave: each family is saved to a state directory and the next seeds from the file. That is only the same
computation if the saved state is EXACTLY what the in-process run holds, and if no family is asked to seed
from one that has not run yet. Both are checked here without the session trees the fit itself needs.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_stark_joint.py"


def _load():
    spec = importlib.util.spec_from_file_location("_stark_joint_families", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_every_family_seeds_only_from_families_that_run_before_it():
    sj = _load()
    for i, fam in enumerate(sj.FAMILIES):
        for need in sj._NEEDS[fam]:
            assert sj.FAMILIES.index(need) < i, (fam, need)
    assert set(sj._NEEDS) == set(sj.FAMILIES)


def test_a_profile_family_round_trips_through_its_checkpoint_exactly(tmp_path):
    sj = _load()
    rng = np.random.default_rng(7)
    prof = np.column_stack([np.array(sj.KAPPAS), rng.normal(1e5, 10.0, len(sj.KAPPAS)),
                            rng.normal(5e4, 5.0, len(sj.KAPPAS))])
    res = (prof, 0.25, rng.normal(size=4 * 172 + sj.NS - 1))
    sj._save_family(tmp_path, "A-", res)
    back = sj._load_family(tmp_path, "A-")
    assert np.array_equal(back[0], res[0]) and back[1] == res[1] and np.array_equal(back[2], res[2])
    assert sj.ub95(back[0]) == sj.ub95(res[0]) or np.isnan(sj.ub95(res[0]))


def test_the_leave_one_out_family_rebuilds_the_dictionaries_the_fit_reads(tmp_path):
    """`lopo` is rebuilt from `lopo_prof` on load, so it must equal what `lopo_fits` builds directly,
    including the key the CSV reads at the predicted coefficient."""
    sj = _load()
    rng = np.random.default_rng(11)
    lopo, lopo_prof = {}, {}
    for pk in sj.PEAKS:
        grid = sj.KAPPAS if pk == "4192" else sj.KAPPAS_LOPO
        cs = {k: float(v) for k, v in zip(grid, rng.normal(2e5, 20.0, len(grid)))}
        mn = min(cs.values())
        lopo[pk] = {k: cs[k] - mn for k in cs}
        lopo_prof[pk] = np.array([[k, cs[k], cs[k]] for k in sorted(cs)])
    sj._save_family(tmp_path, "LOPO", (lopo, lopo_prof))
    lopo2, prof2 = sj._load_family(tmp_path, "LOPO")
    for pk in sj.PEAKS:
        assert np.array_equal(prof2[pk], lopo_prof[pk])
        assert lopo2[pk] == lopo[pk]
        assert lopo2[pk][round(sj.KAPPA_PRED, 3)] == lopo[pk][round(sj.KAPPA_PRED, 3)]
