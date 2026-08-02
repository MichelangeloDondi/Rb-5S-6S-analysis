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

This is checked structurally rather than by re-grepping the file by hand: an
AST walk over every string literal in scripts/make_figures.py, skipping only
docstrings (developer documentation, not rendered), comments (not part of the
AST at all), the STATUS_WORD translation table (its keys are necessarily the
codes being translated AWAY from), and any string passed to _footer(...)
(the one licensed exception). Every string literal that survives that
exclusion is a candidate for being drawn on a figure, and none of them may
carry a banned token.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "make_figures.py"

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
        r"\b(PRELIM|ARTIFACT|DIAGNOSTIC|CALIB|ENVELOPE|MEASURED)\b")),
    ("em-dash", re.compile("—")),
]

_BODY_NODES = (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def _excluded_ids(tree: ast.AST) -> set[int]:
    """id()s of Constant/JoinedStr nodes that are exempt: docstrings, the
    STATUS_WORD lookup table, and every argument of a _footer(...) call."""
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
        # paths and pipeline vocabulary are allowed.
        if isinstance(node, ast.Call):
            fname = (node.func.id if isinstance(node.func, ast.Name)
                     else node.func.attr if isinstance(node.func, ast.Attribute) else None)
            if fname == "_footer":
                for arg in list(node.args) + [kw.value for kw in node.keywords]:
                    for sub in ast.walk(arg):
                        excluded.add(id(sub))

    return excluded


def _figure_facing_string_nodes(tree: ast.AST):
    excluded = _excluded_ids(tree)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and id(node) not in excluded):
            yield node


def test_figure_text_carries_no_pipeline_dialect():
    tree = ast.parse(TARGET.read_text(encoding="utf-8"), filename=str(TARGET))
    violations = []
    for node in _figure_facing_string_nodes(tree):
        for label, pat in BANNED_TOKENS:
            m = pat.search(node.value)
            if m:
                violations.append(
                    f"{TARGET.name}:{node.lineno}: {label} ({m.group(0)!r}) in "
                    f"{node.value.strip()[:80]!r}")
    assert not violations, (
        "figure-facing text still speaks pipeline dialect -- move it to plain "
        "physics register, or into the _footer(...) call if it is genuinely "
        "provenance:\n  " + "\n  ".join(violations))


def test_footer_helper_is_the_only_provenance_route():
    """Guard against a second ad-hoc fig.text(...) provenance line reappearing
    beside _footer -- every regenerate-command line goes through one helper
    (the design contract's footer pattern), so there is exactly one place to
    check/update the wording."""
    tree = ast.parse(TARGET.read_text(encoding="utf-8"), filename=str(TARGET))
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
            stray.append(f"{TARGET.name}:{node.lineno}: fig.text(...) carries a "
                         "regenerate line outside _footer(...)")
    assert not stray, "\n  ".join(stray)
