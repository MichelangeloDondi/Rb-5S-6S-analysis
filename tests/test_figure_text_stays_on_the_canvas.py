"""Text that runs off the figure, and text a legend sits on top of.

Written 2026-08-10, after a day of drawing found ten defects by eye that
tests/test_figures_fresh.py::test_figure_text_does_not_overlap cannot see. That
guard compares text artists against each other WITHIN an axes, which is the
right check and covers only one of the ways a label goes wrong. The two it
misses, and which cost the most rounds:

  * text whose box extends past the FIGURE, so the reader gets "2.19e+07 s" and
    the exponent is simply gone. Three figures did this on their first render.
  * text a LEGEND covers. A legend is not in ax.texts, so both of figure 28's
    legends could sit squarely on a value label and nothing said so.

Both checks are geometric and neither needs a human to look, which is the point:
looking is for the things that cannot be measured.
"""


from test_figures_fresh import _load_make_figures

TOL_PX = 1.0          # a hair of antialiasing is not an overflow
COVER = 0.20          # same floor the sibling overlap guard uses


_CACHE = None


def _drawn():
    """Every figure drawn in-process, once, as [(name, fig)].

    Cached because drawing the whole set takes about four minutes and both
    checks below need all of it. Drawing it twice was the first version and
    doubled the gate's cost for nothing.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    _CACHE = list(_draw_all())
    return _CACHE


def _draw_all():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    mf = _load_make_figures()
    original = mf._save
    try:
        for name in sorted(n for n in dir(mf) if n.startswith("fig_")):
            fn = getattr(mf, name)
            if not callable(fn):
                continue
            plt.close("all")
            captured = {}
            # **kw, because _save takes rect= and a two-argument stub raises
            # TypeError, which the except below then swallows. Thirteen of the
            # twenty-eight figures pass rect, so the first version of this
            # guard silently skipped half the repository and reported a pass.
            mf._save = lambda fig, nm, _c=captured, **kw: _c.__setitem__("fig", fig)
            try:
                fn()
            except Exception:
                continue                      # inputs absent in this checkout
            finally:
                mf._save = original
            fig = captured.get("fig")
            if fig is not None:
                fig.canvas.draw()
                yield name, fig
    finally:
        mf._save = original
        plt.close("all")


def test_the_guard_sees_most_of_the_repository():
    """A skipped figure is a figure nothing checks, and the skip is silent.

    Both checks here catch every exception from a drawer, because a checkout
    without the outside data trees genuinely cannot draw some figures. That
    same clause hid a TypeError in the stub for a while. This asserts a floor
    on coverage so the failure cannot be silent again.
    """
    import ast
    src = ast.parse((__import__("pathlib").Path(__file__).resolve().parents[1]
                     / "scripts" / "make_figures.py").read_text())
    savers = {fn.name for fn in ast.walk(src)
              if isinstance(fn, ast.FunctionDef)
              for c in ast.walk(fn)
              if isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
              and c.func.id == "_save"}
    drawn = {n for n, _f in _drawn()}
    missing = sorted(savers - drawn)
    # EVERY figure, not a fraction. A three-quarters floor was the first
    # version and it let a single broken figure through: make_figures.py
    # raised on one of them for a day, because a results file had been
    # normalised and its reader had not, and 27 of 28 clears 75 per cent
    # comfortably. If a checkout genuinely cannot draw one, name it here with
    # the reason rather than widening the floor.
    assert not missing, (
        f"{len(missing)} of {len(savers)} figures did not draw, so nothing "
        "here checked them. Run scripts/make_figures.py to see why:\n  "
        + "\n  ".join(missing))


def test_no_figure_text_runs_off_the_canvas():
    figs = _drawn()
    assert figs, "no figures drawn, so this guard is vacuous"
    bad = []
    for name, fig in figs:
        r = fig.canvas.get_renderer()
        w, h = fig.canvas.get_width_height()
        for ax in list(fig.axes) + [fig]:
            for t in getattr(ax, "texts", []):
                if not t.get_text().strip():
                    continue
                b = t.get_window_extent(renderer=r)
                if (b.x0 < -TOL_PX or b.y0 < -TOL_PX
                        or b.x1 > w + TOL_PX or b.y1 > h + TOL_PX):
                    bad.append(f"{name}: {t.get_text()[:34]!r} extends past the "
                               f"canvas ({b.x0:.0f},{b.y0:.0f})-"
                               f"({b.x1:.0f},{b.y1:.0f}) on {w}x{h}")
    assert not bad, "figure text off the canvas:\n  " + "\n  ".join(bad)


def test_no_legend_sits_on_a_label():
    figs = _drawn()
    assert figs, "no figures drawn, so this guard is vacuous"
    bad = []
    for name, fig in figs:
        r = fig.canvas.get_renderer()
        for ax in fig.axes:
            leg = ax.get_legend()
            if leg is None:
                continue
            lb = leg.get_window_extent(renderer=r)
            for t in ax.texts:
                if not t.get_text().strip():
                    continue
                b = t.get_window_extent(renderer=r)
                ov = (max(0.0, min(b.x1, lb.x1) - max(b.x0, lb.x0))
                      * max(0.0, min(b.y1, lb.y1) - max(b.y0, lb.y0)))
                area = b.width * b.height
                if area > 0 and ov / area > COVER:
                    bad.append(f"{name}: the legend covers "
                               f"{t.get_text()[:34]!r} by {100*ov/area:.0f}%")
    assert not bad, "a legend is sitting on a label:\n  " + "\n  ".join(bad)
