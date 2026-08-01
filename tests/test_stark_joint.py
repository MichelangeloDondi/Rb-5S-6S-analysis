"""M23 joint two-session Stark fit: the committed record and its premises.

The module itself needs the quarantine prehistory tree and ~1 h, so these
tests check (1) the committed results CSV is internally consistent, (2) the
dnu_floor coarsening the module relies on is harmless, (3) the module
degrades gracefully without the quarantine, and (4) the gamma_coll prior it
uses reproduces the archive's own beta_self x N chain.
"""

import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.linefit import _shared_profile_grid  # noqa: E402

CSV = C.RESULTS_DIR / "stark_joint.csv"


def rows():
    return list(csv.DictReader(open(CSV)))


def val(quantity, key):
    for r in rows():
        if r["quantity"] == quantity and r["key"] == key:
            return float(r["value"])
    raise KeyError((quantity, key))


# ---------------------------------------------------------------------------
# the committed record
# ---------------------------------------------------------------------------

def test_csv_exists_and_has_headline():
    assert CSV.exists(), "run scripts/run_stark_joint.py (needs quarantine)"
    ub = val("kappa_ub95", "primary")
    assert 0.0 < ub < 60.0
    assert abs(val("S0_225mW_ub95", "primary") - ub * 0.225) < 1e-3
    assert abs(val("S0_270mW_ub95", "primary") - ub * 0.270) < 1e-3


def test_bound_tighter_than_m4e():
    """The whole point of M23: the full-profile fit must beat the 20-number
    width fit, else the module has no reason to exist."""
    m4e = None
    p = C.RESULTS_DIR / "stark_sweep.csv"
    for r in csv.DictReader(open(p)):
        if r["quantity"] == "S0_225mW_ub95_profile":
            m4e = float(r["value"])
    assert m4e is not None
    assert val("S0_225mW_ub95", "primary") < m4e


def test_no_detection_claim():
    """kappa_min's preference over kappa=0 must stay below detection
    strength; if a future rerun pushes it past 9 (3 sigma), the NULL
    framing of every doc that cites this file is wrong and must change."""
    assert val("dchi2_kappa0", "primary") < 9.0


def test_campaign_only_reproduces_bound():
    """The robustness claim made in RESULTS: the campaign rows alone give
    nearly the same bound, so nothing leans on the rehearsal's fitted
    scan rates."""
    joint = val("kappa_ub95", "primary")
    camp = val("kappa_ub95_camponly", "robustness")
    assert abs(camp - joint) < 0.5 * joint


def test_direction_indifference():
    assert val("direction_dchi2_max", "robustness") < 10.0


def test_lopo_no_single_peak_drives():
    """Every leave-one-peak-out fit must still disfavour kappa=2.62."""
    for pk in ("4121", "4154", "4192", "4207"):
        assert val("lopo_dchi2_262", pk) > 0.0


def test_saturation_fitted_linear():
    """The detector-linearity receipt: both Vsat >> the ~1 V signals."""
    assert val("Vsat_camp", "nuisance") > 10.0
    assert val("Vsat_reh", "nuisance") > 10.0


def test_rehearsal_rates_sane():
    """~4x slower than the campaign's ~0.0426 MHz/ms, consistent across
    peaks (same generator setting; the spread is the anchor's softness)."""
    r = [val("reh_rate", pk) for pk in ("4121", "4154", "4192", "4207")]
    assert all(0.005 < x < 0.02 for x in r)
    assert max(r) / min(r) < 1.25


def test_gc_posterior_within_prior():
    """The posterior must not rail at zero (the failure the prior exists
    to prevent) nor wander far above its prior."""
    import re
    for r in rows():
        if r["quantity"] == "gamma_coll_post":
            post = float(r["value"])
            m = re.search(r"prior ([\d.]+)\+/-([\d.]+)", r["unit"])
            mu, sig = float(m.group(1)), float(m.group(2))
            assert post > 0.05, "gamma_coll railed at zero despite the prior"
            assert abs(post - mu) < 4 * sig


# ---------------------------------------------------------------------------
# the premises
# ---------------------------------------------------------------------------

def test_dnu_floor_equivalence():
    """M23 runs the profile builder at dnu_floor=2e-2. Against the 1e-3
    default the profile must agree to well under the campaign's per-point
    noise (5e-3 of peak at SNR 193) even at the nastiest corner the
    optimizer visits (sigma_laser at its 0.05 bound, s0 on)."""
    for gc, sl, s0 in ((0.5, 1.0, 0.0), (6.0, 2.0, 0.6), (4.0, 0.05, 1.5)):
        g1, p1 = _shared_profile_grid(gc, sl, 3.0, s0, "gaussian")
        g2, p2 = _shared_profile_grid(gc, sl, 3.0, s0, "gaussian",
                                      dnu_floor=2e-2)
        d = np.abs(np.interp(g1, g2, p2) - p1).max() / p1.max()
        assert d < 5e-5, (gc, sl, s0, d)


def test_graceful_without_quarantine(tmp_path, monkeypatch):
    """Without the prehistory tree the module must exit 0 and change
    nothing (the committed CSV is the record)."""
    import run_stark_joint as M
    monkeypatch.setattr(M, "PREHISTORY", tmp_path / "absent")
    assert M.main() == 0


def test_gc_prior_matches_beta_self_chain():
    import run_stark_joint as M
    from rb5s6s.density import number_density_cm3
    pri = M.gc_priors()
    n130 = float(number_density_cm3(np.array([130.0]))[0]) / 1e12
    for r in csv.DictReader(open(C.RESULTS_DIR / "beta_self.csv")):
        mu, sig = pri[r["peak"]]
        assert abs(mu - float(r["beta_self"]) * n130) < 1e-9
        assert abs(sig - float(r["beta_self_err"]) * n130) < 1e-9
