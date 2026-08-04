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
codes being translated AWAY from), any string passed to _footer(...) (the
one licensed on-figure exception), and strings that leave through the console
or the exception channel (print(...) arguments and raise statements), which
are developer-facing and never drawn. Every string literal that survives that
exclusion is a candidate for being drawn on a figure, and none of them may
carry a banned token.
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
]

_BODY_NODES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _excluded_ids(tree: ast.AST) -> set[int]:
    """id()s of Constant/JoinedStr nodes that are exempt: docstrings, the
    STATUS_WORD lookup table, every argument of a _footer(...) or print(...)
    call, and every string inside a raise statement (console and exception
    text is developer-facing, never drawn on a figure)."""
    excluded: set[int] = set()

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
        # print(...), which goes to the console, not the canvas.
        if isinstance(node, ast.Call):
            fname = (node.func.id if isinstance(node.func, ast.Name)
                     else node.func.attr if isinstance(node.func, ast.Attribute) else None)
            if fname in ("_footer", "print"):
                for arg in list(node.args) + [kw.value for kw in node.keywords]:
                    for sub in ast.walk(arg):
                        excluded.add(id(sub))

        # raise SystemExit("...") and kin: exception text reaches the
        # terminal, never a rendered figure.
        if isinstance(node, ast.Raise):
            for sub in ast.walk(node):
                excluded.add(id(sub))

    return excluded


def _figure_facing_string_nodes(tree: ast.AST):
    excluded = _excluded_ids(tree)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in excluded):
            yield node


@pytest.mark.parametrize("target", TARGETS, ids=lambda p: p.name)
def test_figure_text_carries_no_pipeline_dialect(target):
    tree = ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    violations = []
    for node in _figure_facing_string_nodes(tree):
        for label, pat in BANNED_TOKENS:
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
