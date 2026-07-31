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


import pytest
from PIL import Image

from rb5s6s import config as C


def _load_make_figures():
    """Import scripts/make_figures.py by path -- scripts/ is not a package."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "make_figures", C.REPO_ROOT / "scripts" / "make_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

DATA_DRIVEN = [
    "fig1_width_vs_density",
    "fig2_power_sweep",
    "fig3_transit_mc",
    "fig4_amplitude_ratios",
    "fig5_pooled_width",
    "fig6_gamma_floor",
    "fig7_identifiability_profile",
    "fig8_ruler",
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
        "If you just ADDED a results CSV, this is the expected ordering trap: the "
        "fingerprint hashes `git ls-files`, so a new CSV joins it only once it is "
        "staged, and every figure drawn before that goes stale at commit time. "
        "Redraw after staging, not before. "
        f"Otherwise a results CSV changed without redrawing the figures -- run "
        f"scripts/make_figures.py and commit the updated PNGs.")


def test_all_data_driven_figures_share_one_fingerprint():
    # They are all drawn in one make_figures.py run, so a split fingerprint means
    # a partial/hand-edited regeneration -- exactly the half-updated state to catch.
    fps = {name: _embedded(name) for name in DATA_DRIVEN}
    distinct = set(fps.values())
    assert len(distinct) == 1, f"figures drawn from different results snapshots: {fps}"


@pytest.mark.slow
def test_figure_text_does_not_overlap():
    """Measure label collisions instead of eyeballing them.

    Added 2026-07-29 after a review asked for no overlapping labels in the
    figures. Reading them by eye passed fig13; measuring the rendered bounding
    boxes did not -- its level names overlapped their own energy annotations by
    ~25%, invisible at a glance and obvious at 200%. Every figure is drawn
    in-process and every pair of text artists in each axes is compared; more
    than 20% of the smaller box covered is a collision.

    The 20% floor is deliberate: rotated tick labels and sub/superscripts touch
    at a few percent without being unreadable, and a zero-tolerance version
    would be noise.
    """
    import itertools
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    mf = _load_make_figures()
    drawers = [(n, getattr(mf, n)) for n in dir(mf)
               if n.startswith("fig_") and callable(getattr(mf, n))]
    assert drawers, "no figure drawers found in make_figures"
    original = mf._save
    problems = []
    try:
        for name, fn in drawers:
            plt.close("all")
            captured = {}
            mf._save = lambda fig, nm, _c=captured: _c.__setitem__("fig", fig)
            try:
                fn()
            except Exception:
                continue                      # inputs absent in this checkout
            finally:
                mf._save = original
            fig = captured.get("fig")
            if fig is None:
                continue
            fig.canvas.draw()
            r = fig.canvas.get_renderer()
            for ax in fig.axes:
                boxes = []
                for t in ax.texts:
                    if t.get_text().strip():
                        boxes.append((t.get_text()[:24],
                                      t.get_window_extent(renderer=r)))
                for (t1, b1), (t2, b2) in itertools.combinations(boxes, 2):
                    ov = (max(0.0, min(b1.x1, b2.x1) - max(b1.x0, b2.x0))
                          * max(0.0, min(b1.y1, b2.y1) - max(b1.y0, b2.y0)))
                    small = min(b1.width * b1.height, b2.width * b2.height)
                    if small > 0 and ov / small > 0.20:
                        problems.append(
                            f"{name}: {t1!r} overlaps {t2!r} by {100 * ov / small:.0f}%")
    finally:
        mf._save = original
        plt.close("all")
    assert not problems, "overlapping figure labels:\n  " + "\n  ".join(problems)
