"""The figure register guard: scripts/make_figures.py speaks two dialects.

Internally the pipeline uses module codes (M25, C3a), CSV-column names
(gamma_coll, sigma_laser), and provenance status tags (PRELIM, ARTIFACT) --
useful shorthand between people who already know this repo. None of that
belongs on a rendered figure: a physics reader with zero repo knowledge (the
"three-reader label test" -- would the senior reader follow it without friction, would a new
intern learn what the quantity IS, would an outside researcher with their own
transition understand it) must be able to read every title, suptitle, legend,
annotation and parameter box unaided. The ONE place pipeline vocabulary and
file paths are allowed is the footer (source files + regenerate command),
because that line exists for reproducibility, not readability -- see
scripts/make_figures.py's _footer() and the design contract it implements.

This is checked structurally rather than by re-grepping the files by hand: an
AST walk over every string literal in the figure-drawing scripts
(scripts/make_figures.py and scripts/make_fig0_spectrum.py), skipping only
docstrings (developer documentation, not rendered), comments (not part of the
AST at all), the STATUS_WORD translation table (its keys are necessarily the
codes being translated AWAY from), and strings that leave through the console
or the exception channel (print(...) arguments and raise statements), which
are developer-facing and never drawn. Every string literal that survives that
exclusion is a candidate for being drawn on a figure, and none of them may
carry a banned token.

Strings passed to _footer(...) are the partial exception. The footer may carry
file paths, module names and pipeline vocabulary, because that line exists for
reproducibility. It may not carry the banned punctuation: the footer is drawn
on the same canvas as everything else, so the em-dash, spaced-double-hyphen and
semicolon rules apply to it too.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / "scripts" / "make_figures.py",
           ROOT / "scripts" / "make_fig0_spectrum.py",
           # fig9's generator: it draws a tracked figure, so it is held to the
           # same register and the same footer rule as the other two. It was
           # structurally exempt from both until 2026-08-04.
           ROOT / "scripts" / "run_polarizability_ladder.py"]

# Kept as a module-level constant (not inline in the walker) so a future
# addition to the register rule extends this list instead of re-deriving it.
# Each entry: (name, compiled pattern). Case sensitivity matches the rule as
# stated: module codes and the status codes are matched as written (ALL-CAPS
# where the convention itself is ALL-CAPS); "CSV", "committed", "persisted"
# are the pipeline nouns a plain-physics reader would stumble on regardless
# of case.
BANNED_TOKENS = [
    ("module code (M<digits>)", re.compile(r"\bM\d+\b")),
    ("the token CSV", re.compile(r"\bCSV\b")),
    ("the word 'committed'", re.compile(r"\bcommitted\b", re.I)),
    ("the word 'persisted'", re.compile(r"\bpersisted\b", re.I)),
    ("ALL-CAPS status code", re.compile(
        r"\b(PRELIM|ARTIFACT|DIAGNOSTIC|CALIB|ENVELOPE|MEASURED|BOUND)\b")),
    ("em-dash", re.compile("—")),
    # A spaced double hyphen is the ASCII stand-in for the em-dash the register
    # bans, and it renders as broken typography on the PNGs (the 2026-08-03
    # audit found five figures carrying it). Unspaced "--" stays legal: it is
    # matplotlib's dashed-linestyle format string.
    ("double hyphen standing in for a dash", re.compile(r"\s--\s")),
    # The 2026-08-04 fig19 incident: a panel box cited results/ruler_traces.csv
    # by path, a title carried "dof=2, t=2.92", an axis label carried a
    # semicolon, and the word "headline" named a construction only this
    # repository calls that. All of it passed, because none of it was on this
    # list. File paths belong in the footer alone, statistics shorthand is
    # spelled out or dropped, and prose punctuation follows the same register
    # as the documents.
    # Directory-prefixed only: bare "name.csv" literals are how the module
    # BUILDS its Path objects, which the AST walk cannot tell from drawn text.
    # The leak this catches is the prefixed form ("results/ruler_traces.csv"),
    # which is what a reader-facing panel would quote.
    ("repository file path in figure text", re.compile(
        r"\b(results|data_raw|docs|scripts|private|tests)/", re.I)),
    ("the word 'headline'", re.compile(r"\bheadline\b", re.I)),
    ("t-quantile shorthand t(p,dof)", re.compile(r"\bt\(0\.\d+\s*,\s*\d+\)")),
    ("the shorthand 'dof'", re.compile(r"\bdof\b")),
    ("the abbreviation SNR", re.compile(r"\bSNR\b")),
    ("semicolon in figure prose", re.compile(r";\s")),
]

# The footer's exemption is about VOCABULARY: it is the one line licensed to
# carry file paths, module names and function names, because it exists for
# reproducibility. It was never meant to license typography. An em-dash, a
# spaced double hyphen and a semicolon render on the canvas wherever they sit,
# and the footer is on the canvas, so those three rules follow the footer in.
# Added 2026-08-05, after a pass removed semicolons from four footers and left
# them in three, with the guard structurally unable to see any of the seven.
TYPOGRAPHY_LABELS = {"em-dash", "double hyphen standing in for a dash",
                     "semicolon in figure prose"}
TYPOGRAPHY_TOKENS = [r for r in BANNED_TOKENS if r[0] in TYPOGRAPHY_LABELS]

_BODY_NODES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _excluded_ids(tree: ast.AST) -> tuple[set[int], set[int]]:
    """Two sets of Constant/JoinedStr node id()s.

    The first is fully exempt: docstrings, the STATUS_WORD lookup table, every
    argument of a print(...) call, and every string inside a raise statement
    (console and exception text is developer-facing, never drawn on a figure).

    The second is the _footer(...) arguments, which are exempt from the
    vocabulary rules only and are still held to TYPOGRAPHY_TOKENS."""
    excluded: set[int] = set()
    footer_only: set[int] = set()

    for node in ast.walk(tree):
        # docstrings: the first statement of a module/function/class body,
        # if it is a bare string expression.
        if isinstance(node, _BODY_NODES) and node.body:
            first = node.body[0]
            if (isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                excluded.add(id(first.value))

        # the STATUS_WORD dict itself: its keys are the very codes this test
        # bans, by construction (it exists to translate them away from figure
        # text), so the assignment's whole right-hand side is exempt.
        if (isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "STATUS_WORD" for t in node.targets)):
            for sub in ast.walk(node.value):
                excluded.add(id(sub))

        # any string literal handed to _footer(...) -- the one place file
        # paths and pipeline vocabulary are allowed on the figure -- or to
        # print(...), which goes to the console, not the canvas. The footer
        # keeps its vocabulary licence and loses its typography one.
        if isinstance(node, ast.Call):
            fname = (node.func.id if isinstance(node.func, ast.Name)
                     else node.func.attr if isinstance(node.func, ast.Attribute) else None)
            if fname in ("_footer", "print"):
                sink = excluded if fname == "print" else footer_only
                for arg in list(node.args) + [kw.value for kw in node.keywords]:
                    for sub in ast.walk(arg):
                        sink.add(id(sub))

        # raise SystemExit("...") and kin: exception text reaches the
        # terminal, never a rendered figure.
        if isinstance(node, ast.Raise):
            for sub in ast.walk(node):
                excluded.add(id(sub))

        # data-handling string literals that name fields rather than carry
        # prose: dict keys ({"dof": dof}), subscript indices (row["headline"])
        # and the first argument of a .get(...) lookup. Added 2026-08-04 when
        # the token list grew words that legitimately appear as column names.
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant):
                    excluded.add(id(k))
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
            excluded.add(id(node.slice))
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and node.args
                and isinstance(node.args[0], ast.Constant)):
            excluded.add(id(node.args[0]))

    return excluded, footer_only


def _figure_facing_string_nodes(tree: ast.AST):
    """Yields (node, rules): the token list each surviving string is held to."""
    excluded, footer_only = _excluded_ids(tree)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in excluded):
            yield node, (TYPOGRAPHY_TOKENS if id(node) in footer_only
                         else BANNED_TOKENS)


@pytest.mark.parametrize("target", TARGETS, ids=lambda p: p.name)
def test_figure_text_carries_no_pipeline_dialect(target):
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    violations = []
    for node, rules in _figure_facing_string_nodes(tree):
        for label, pat in rules:
            m = pat.search(node.value)
            if m:
                violations.append(
                    f"{target.name}:{node.lineno}: {label} ({m.group(0)!r}) in "
                    f"{node.value.strip()[:80]!r}")
    assert not violations, (
        "figure-facing text still speaks pipeline dialect -- move it to plain "
        "physics register, or into the _footer(...) call if it is genuinely "
        "provenance:\n  " + "\n  ".join(violations))


@pytest.mark.parametrize("target", TARGETS, ids=lambda p: p.name)
def test_every_figure_writing_function_carries_a_footer(target):
    """The footer rule had only half a guard: provenance had to go through
    _footer, but nothing checked that it was there at all, and fig0 and fig9
    shipped for months with no source line and no regenerate command. Any
    function that writes a figure must also call _footer."""
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    missing = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name in ("_save", "_footer"):      # the helpers themselves
            continue
        calls = {c.func.id if isinstance(c.func, ast.Name)
                 else c.func.attr if isinstance(c.func, ast.Attribute) else None
                 for c in ast.walk(node) if isinstance(c, ast.Call)}
        if ("_save" in calls or "savefig" in calls) and "_footer" not in calls:
            missing.append(f"{target.name}:{node.lineno}: {node.name}() writes a "
                           "figure without calling _footer(...)")
    assert not missing, (
        "a figure would ship with no source list and no regenerate command:\n  "
        + "\n  ".join(missing))


@pytest.mark.parametrize("target", TARGETS, ids=lambda p: p.name)
def test_footer_helper_is_the_only_provenance_route(target):
    """Guard against a second ad-hoc fig.text(...) provenance line reappearing
    beside _footer -- every regenerate-command line goes through one helper
    (the design contract's footer pattern), so there is exactly one place to
    check/update the wording."""
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    stray = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fname = (node.func.attr if isinstance(node.func, ast.Attribute) else
                  node.func.id if isinstance(node.func, ast.Name) else None)
        if fname != "text":
            continue
        # fig.text(...) calls outside of _footer's own body are only allowed
        # when they are not a "Source: ... Regenerate: ..." provenance line
        # (fig17 keeps one supplementary citation line beside its footer).
        text_args = [a.value for a in node.args if isinstance(a, ast.Constant)
                     and isinstance(a.value, str)]
        if any("Regenerate:" in t for t in text_args):
            stray.append(f"{target.name}:{node.lineno}: fig.text(...) carries a "
                         "regenerate line outside _footer(...)")
    assert not stray, "\n  ".join(stray)


# --------------------------------------------------------------------------
# An axis label is a quantity and a unit (protocol section 12.1)
# --------------------------------------------------------------------------
# The census of 2026-08-09 found 156 of 235 label strings carrying caption
# material: one x label read "beam waist (um). This has not been measured. The
# knife-edge scan is pending.", five residual axes read "residual, in units of
# the point error", and one suptitle ran to seven lines and argued its own
# conclusion. The rule had been written in the protocol for months and was not
# kept, which is why it is a test now. Titles are held to a longer limit than
# axis labels, because a title may name the conditions.
_AXIS_SETTERS = {"set_xlabel", "set_ylabel"}
_TITLE_SETTERS = {"set_title", "suptitle"}
_AXIS_MAX = 62
_TITLE_MAX = 110
# A sentence inside a label: a full stop or a semicolon followed by a space and
# a word. The lookbehind keeps a decimal out of it, which matters because an
# f-string flattens "993.{pk} nm" to "993. nm" and that is a wavelength, not a
# sentence. Found by this guard's own first run.
_LABEL_SENTENCE = re.compile(r"(?<!\d)[.;]\s+[A-Za-z]")
# Words that state a status, a judgement or an argument rather than a quantity.
_LABEL_PROSE = [
    r"\bnot been measured\b", r"\bis pending\b", r"\bin units of\b",
    r"\bremains open\b", r"\bmeasured directly\b", r"\bconservative\b",
    r"\bupper bounds?\b", r"\brather than\b", r"\bwhich is\b",
    r"\bso that\b", r"\bbecause\b",
]


def _label_calls(tree: ast.AST):
    """Yields (attr, literal, lineno) for every axis-label and title call."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        attr = node.func.attr
        if attr not in _AXIS_SETTERS | _TITLE_SETTERS:
            continue
        for arg in node.args[:1]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                yield attr, arg.value, arg.lineno
            elif isinstance(arg, ast.JoinedStr):
                lit = "".join(v.value for v in arg.values
                              if isinstance(v, ast.Constant)
                              and isinstance(v.value, str))
                yield attr, lit, arg.lineno


@pytest.mark.parametrize("target", TARGETS, ids=lambda p: p.name)
def test_axis_labels_are_a_quantity_and_a_unit(target):
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    bad = []
    for attr, lit, ln in _label_calls(tree):
        flat = " ".join(lit.split())
        limit = _AXIS_MAX if attr in _AXIS_SETTERS else _TITLE_MAX
        if len(flat) > limit:
            bad.append(f"{target.name}:{ln}: {attr} is {len(flat)} characters, "
                       f"over {limit}: {flat[:70]!r}. An axis label is a "
                       f"quantity and a unit. The rest belongs in the caption "
                       f"of the document that shows the figure.")
        if attr in _AXIS_SETTERS and _LABEL_SENTENCE.search(flat):
            bad.append(f"{target.name}:{ln}: {attr} contains a sentence: "
                       f"{flat[:70]!r}. Caveats go in the caption.")
        for pat in _LABEL_PROSE:
            if re.search(pat, flat, re.I):
                bad.append(f"{target.name}:{ln}: {attr} carries prose "
                           f"({pat}): {flat[:70]!r}")
    assert not bad, "figure labels carrying caption material:\n  " + "\n  ".join(bad)
