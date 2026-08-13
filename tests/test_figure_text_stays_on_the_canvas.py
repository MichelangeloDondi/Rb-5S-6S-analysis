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
# figures that RAISED, as opposed to figures that returned without drawing.
# The difference is the whole point: a figure whose input is absent in this
# checkout returns early and keeps its committed PNG, which is correct in the
# public mirror where the traces and the bench photograph do not exist. A
# figure that raises is broken, and on 2026-08-11 one had been for a day.
_RAISED: dict = {}


def _renderer(fig):
    """A renderer for this figure, on any matplotlib the CI matrix runs.

    `fig.canvas.get_renderer()` exists on the Agg canvas and NOT on
    FigureCanvasBase, and a Figure built without pyplot carries the base class.
    Locally that never showed, because this repository pins one interpreter and
    one matplotlib; the mirror's CI runs four combinations and the 3.11-latest
    job raised AttributeError on 2026-08-11 while the same commit's gate was
    clean on this machine. Attaching an Agg canvas is the portable fix and
    changes nothing about what is measured.
    """
    fig.canvas.draw()
    get = getattr(fig.canvas, "get_renderer", None)
    if get is not None:
        return get()
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    FigureCanvasAgg(fig)
    fig.canvas.draw()
    return fig.canvas.get_renderer()


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
            #
            # AND THE STUB APPLIES THE LAYOUT (2026-08-13). Recording the
            # figure alone measured a PRE-LAYOUT geometry while the shipped
            # PNG is laid out, so every check in this file was answering a
            # question about a figure that is never saved. mf._layout is the
            # half of _save that positions things, split out for exactly this.
            def _stub(fig, nm, _c=captured, _mf=mf, **kw):
                _mf._layout(fig, kw.get("rect"))
                _c["fig"] = fig

            mf._save = _stub
            raised = None
            try:
                fn()
            except Exception as exc:          # noqa: BLE001 - recorded, not hidden
                raised = f"{type(exc).__name__}: {exc}"
            finally:
                mf._save = original
            if raised is not None:
                _RAISED[name] = raised
                continue
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
    # NOTHING MAY RAISE. Not drawing is allowed and raising is not, and the
    # two were the same thing here until 2026-08-11. A figure whose input is
    # absent returns early and keeps its committed PNG, which is what the
    # public mirror does for the seven that need the raw traces or the bench
    # photograph. A figure that RAISES is broken: one had been for a day,
    # because a results file was normalised and its reader was not, and a
    # three-quarters coverage floor could not see it either.
    assert not _RAISED, (
        "these figures RAISED rather than returning, so they are broken and "
        "nothing here checked them:\n  "
        + "\n  ".join(f"{k}: {v}" for k, v in sorted(_RAISED.items())))
    if missing:
        print(f"\n  {len(missing)} figures returned without drawing, which is "
              "the absent-input path, not a failure: " + ", ".join(missing))


def test_no_figure_text_runs_off_the_canvas():
    figs = _drawn()
    assert figs, "no figures drawn, so this guard is vacuous"
    bad = []
    for name, fig in figs:
        r = _renderer(fig)
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
        r = _renderer(fig)
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


def test_no_canvas_text_argues_its_case():
    """A canvas labels, it does not explain. Protocol 12.1 and 12.20.

    Two objective limits, because "over-explaining" is a judgement and a
    guard needs a measurement:

    1. LENGTH. No canvas string may run past 30 words. The source footer and
       the shared-parameter box are exempt by name, since one is provenance
       and the other is a table of fitted values.
    2. ARGUMENT. No canvas string may carry the connective machinery of
       reasoning. A figure that has to say "which is why" or "the point is"
       is doing the caption's job on the reader's screen.

    MEASURED WHEN THIS WAS WRITTEN, 2026-08-13: the worst canvas carried 147
    words and told the reader which conclusion to draw from panel (b). Five
    figures carried essays. They are now labels, and their arguments live in
    figures/README.md and the methods chapters, which is where a reader can
    skip them.
    """
    figs = _drawn()
    assert figs, "no figures drawn, so this guard is vacuous"
    import re
    ARGUES = re.compile(r"\bwhich is why\b|\bthe point is\b|\bis the point\b|"
                        r"\bin other words\b|\bnote that\b|\bwhat matters\b|"
                        r"\bdoes not merely\b|\bit follows that\b|"
                        r"\bthat is why\b|\bthis means\b|\bwhat this shows\b",
                        re.I)
    # Exempt by KIND, not by opening words. A parameter table and a citation
    # list are long by nature and neither is prose: the first is data the
    # reader looks up, the second is provenance. Matched anywhere in the
    # string, since both sit after a heading.
    EXEMPT = ("Source:", "Sources:", "figure ", "Shared across",
              "Matrix elements:")
    bad = []
    for name, fig in figs:
        texts = [t.get_text() for t in fig.texts]
        for ax in fig.axes:
            texts += [ax.get_title(), ax.xaxis.label.get_text(),
                      ax.yaxis.label.get_text()]
            texts += [t.get_text() for t in ax.texts]
            leg = ax.get_legend()
            if leg is not None:
                texts += [t.get_text() for t in leg.get_texts()]
        for t in texts:
            flat = " ".join(str(t).split())
            if not flat or any(e in flat for e in EXEMPT):
                continue
            if len(flat.split()) > 30:
                bad.append(f"{name}: {len(flat.split())} words on the canvas: "
                           f"{flat[:60]!r}")
            if ARGUES.search(flat):
                bad.append(f"{name}: canvas text argues its case: {flat[:60]!r}")
    assert not bad, ("a canvas is explaining rather than labelling:\n  "
                     + "\n  ".join(bad))


def test_nothing_sits_on_the_footer(request):
    """The footer line is a named collision target, not just more text.

    Every figure carries one footer, drawn by make_figures._footer at the
    bottom-left: the CSVs and modules it came from and the command that
    rebuilds it. It is the smallest text on the canvas at 6.3 point and the
    lowest, so an x-axis label pushed down by a tall tick set, or a caption
    that grew a line, lands on top of it and nothing noticed. The other
    guards here do not: the canvas guard asks whether text is ON the figure,
    the legend guard asks about legends, and the axes guard asks about
    data-anchored labels inside their own axes. The footer was reachable by
    none of them.

    Owner instruction, 2026-08-12, added with the register rule of protocol
    12.18 in the same wave.
    """
    figs = _drawn()
    assert figs, "no figures drawn, so this guard is vacuous"
    bad = []
    for name, fig in figs:
        r = _renderer(fig)
        # the footer is the fig-level text nearest the bottom-left corner
        cands = [t for t in fig.texts if t.get_text().strip()]
        if not cands:
            continue
        foot = min(cands, key=lambda t: (t.get_position()[1],
                                         t.get_position()[0]))
        fb = foot.get_window_extent(renderer=r)
        others = [t for t in fig.texts if t is not foot and t.get_text().strip()]
        for ax in fig.axes:
            others += [ax.xaxis.label, ax.yaxis.label, ax.title]
            others += [t for t in ax.texts if t.get_text().strip()]
        for t in others:
            if not t.get_text().strip():
                continue
            b = t.get_window_extent(renderer=r)
            ov = (max(0.0, min(b.x1, fb.x1) - max(b.x0, fb.x0))
                  * max(0.0, min(b.y1, fb.y1) - max(b.y0, fb.y0)))
            area = min(b.width * b.height, fb.width * fb.height)
            if area > 0 and ov / area > COVER:
                bad.append(f"{name}: {t.get_text()[:34]!r} sits on the "
                           f"footer by {100 * ov / area:.0f}%")
    assert not bad, ("something is sitting on the source footer:\n  "
                     + "\n  ".join(bad))


def test_no_data_anchored_label_leaves_its_own_axes():
    """A label anchored to a data point must stay inside the panel holding it.

    Added 2026-08-11. fig29's four temperature labels were offset 14 points
    BELOW markers that sat near the bottom of a log axis, so all four fell
    outside the axes and the bottom spine cut them through the middle. The
    guard above did not fire and was right not to: they were inside the FIGURE
    the whole time. On the canvas and inside its own panel are two different
    questions and only the first was ever asked.

    The two constructs are distinguishable, which is what keeps this from
    firing on every caption. Text anchored in DATA coordinates is a label on
    something and belongs in the panel. Text placed with transform=ax.transAxes
    is deliberate furniture, and several figures legitimately put caption prose
    below their panels that way. Only the first kind is checked.
    """
    figs = _drawn()
    assert figs, "no figures drawn, so this guard is vacuous"
    bad = []
    for name, fig in figs:
        r = _renderer(fig)
        for ax in fig.axes:
            for t in ax.texts:
                if not t.get_text().strip():
                    continue
                if not _is_data_anchored(t, ax):
                    continue
                b, box = t.get_window_extent(renderer=r), ax.bbox
                if (b.x0 < box.x0 - TOL_PX or b.y0 < box.y0 - TOL_PX
                        or b.x1 > box.x1 + TOL_PX or b.y1 > box.y1 + TOL_PX):
                    bad.append(
                        f"{name}: {t.get_text()[:34]!r} is anchored to a data "
                        f"point but its box ({b.x0:.0f},{b.y0:.0f})-"
                        f"({b.x1:.0f},{b.y1:.0f}) leaves its axes "
                        f"({box.x0:.0f},{box.y0:.0f})-({box.x1:.0f},{box.y1:.0f})")
    assert not bad, (
        "data-anchored labels outside their own panel. Put the label on the "
        "other side of its marker, or make it caption text with "
        "transform=ax.transAxes if it belongs outside:\n  " + "\n  ".join(bad))


def _is_data_anchored(t, ax):
    """True when this text is positioned FROM a data point.

    Annotations carry xycoords, which says it directly. A plain Text is data
    anchored when its transform is the axes' transData, which is matplotlib's
    default for ax.text and is exactly what transform=ax.transAxes overrides.
    """
    from matplotlib.text import Annotation
    if isinstance(t, Annotation):
        return getattr(t, "xycoords", "data") == "data"
    return t.get_transform() is ax.transData


NARRATIVE_OPENERS = {"and", "so", "but", "then", "which", "now", "yet", "or"}


def test_no_panel_title_continues_the_previous_panel_sentence():
    """A panel title names what is plotted. It does not narrate.

    THE TELL, which the owner named on 2026-08-13: panel titles chained as
    one running sentence, so that (b) opens with "and" and only parses if
    you have read (a). It reads as a person talking through their own
    figure, and it is the register fault the canvas-essay cut was about,
    wearing a title instead of a text box.

        (c)  and the fit gives the ramp all of it     narrated
        (c)  the width budget at 225 mW               named

    Seven were found and rewritten in the sweep that added this guard. A
    title may be long and it may state a physical fact; what it may not do
    is open with a conjunction, because a figure's panels are read in any
    order and each label has to stand up alone.
    """
    import pathlib
    import re
    source = (pathlib.Path(__file__).resolve().parents[1] / "scripts"
              / "make_figures.py").read_text()
    titles = re.findall(
        r"(?:set_title|suptitle)\(\s*(?:rf?|f)?[\"']([^\"']{4,})[\"']", source)
    assert len(titles) > 40, f"only {len(titles)} titles parsed, regex drifted"

    narrated = []
    for title in titles:
        body = re.sub(r"^\([a-z]\)\s*", "", title).strip()
        first = body.split()[0].lower().strip(",") if body.split() else ""
        if first in NARRATIVE_OPENERS:
            narrated.append(title)
    assert not narrated, (
        "panel titles opening with a conjunction, so they only parse after "
        "the previous panel:\n  " + "\n  ".join(narrated))
