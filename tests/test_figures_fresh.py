"""
Figure freshness: a committed figure must be drawn from the CURRENT results.

The failure this guards against actually happened once here: a physics fix moved
beta from 0.056 to 0.036 in the results CSVs, but fig1/3/5/6 were not redrawn and
kept showing the old value -- found only by accident. A pixel comparison would
catch it, but committed matplotlib PNGs are not reproducible across matplotlib
versions (this repo's CI runs three), so a pixel diff would flake.

Instead `make_figures.py` stamps a fingerprint of the results/ CSVs into each
figure's PNG metadata at draw time (config.results_fingerprint). This test reads
that stamp back and checks it still matches the current results. It is therefore
matplotlib-version-independent: it compares a hash in a text chunk, never pixels.
A stale figure fails with a clear instruction to re-run make_figures.py.

fig0_spectrum is intentionally exempt: it is a representative raw-trace
illustration (frozen data_raw + fit), not an artifact of the mutable results/.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from rb5s6s import config as C

DATA_DRIVEN = [
    "fig1_width_vs_density",
    "fig2_power_sweep",
    "fig3_transit_mc",
    "fig4_amplitude_ratios",
    "fig5_pooled_width",
    "fig6_gamma_floor",
    "fig7_identifiability_profile",
]


def _embedded(name: str):
    p = C.REPO_ROOT / "figures" / f"{name}.png"
    if not p.exists():
        pytest.skip(f"{name}.png not present (run scripts/make_figures.py)")
    return Image.open(p).text.get("DataFingerprint")


@pytest.mark.parametrize("name", DATA_DRIVEN)
def test_figure_drawn_from_current_results(name):
    embedded = _embedded(name)
    current = C.results_fingerprint()
    assert embedded is not None, (
        f"{name}.png carries no DataFingerprint -- redraw it with scripts/make_figures.py")
    assert embedded == current, (
        f"{name}.png is STALE: drawn from results {embedded}, current is {current}. "
        f"A results CSV changed without redrawing the figures -- run "
        f"scripts/make_figures.py and commit the updated PNGs.")


def test_all_data_driven_figures_share_one_fingerprint():
    # They are all drawn in one make_figures.py run, so a split fingerprint means
    # a partial/hand-edited regeneration -- exactly the half-updated state to catch.
    fps = {name: _embedded(name) for name in DATA_DRIVEN}
    distinct = set(fps.values())
    assert len(distinct) == 1, f"figures drawn from different results snapshots: {fps}"
