"""The inspection gallery is allowed to write in exactly one place.

`scripts/make_qc_gallery.py` renders 297 panels, 13 contact sheets and an index
from the raw archive. None of that is publishable: the panels are pictures of
raw traces, the index names quarantined and discarded files, and the whole set
is regenerated whenever anybody wants to look at it. It therefore lives under
`private/`, which this repository gitignores wholesale by DIRECTORY rather than
by filename glob, precisely so that nothing lands in the tracked tree by being
named something the ignore rules did not anticipate.

That decision is only worth as much as the guard on it, so the guard has two
halves. The static half walks the generator's syntax tree and checks that every
write it performs has `out_path(...)` as its destination. The runtime half calls
`out_path` and checks that it refuses a destination resolving outside the
gallery root, which is the case a static walk cannot see.

Seven tests in all, and the two halves above are the first of them. Three more
hold the three do-nots the generator's own docstring states, so that each of
them is a check rather than a note: it never routes through the citable figure
saver, it is never added to the figure register's targets, and it is never
wired into the gate.

The fifth holds the panel REGISTER. Two external reviews of a rendered set
found the same class of defect over and over: pipeline shorthand printed on a
picture drawn for a reader who has never seen this repository. The phrases they
named are banned here by name, so that removing them once removes them for good.

The sixth holds the gate on the most contested decision in this week's work,
that a panel corrects its tooth numbering on the amplitude evidence and never
on the labelling verdict string. The seventh reads the generator's own
docstring and checks that it still states the three do-nots.
"""

from __future__ import annotations

import ast
import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "make_qc_gallery.py"

# Every call that can put bytes on disk. A builtin `open` counts only when its
# mode says it writes, since the generator legitimately READS the manifest and
# the tables it annotates against.
WRITE_METHODS = {"savefig", "write_text", "write_bytes", "write", "writelines",
                 "mkdir", "touch", "rename", "replace", "unlink", "rmdir"}
WRITE_MODES = set("wax+")

# The one function allowed to build a destination, and the one allowed to
# create a folder while doing it.
GATEKEEPER = "out_path"


def _source() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def _tree() -> ast.AST:
    return ast.parse(_source())


def _enclosing_functions(tree: ast.AST) -> dict:
    """id(node) -> name of the function each node sits inside."""
    owner = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for node in ast.walk(fn):
                owner.setdefault(id(node), fn.name)
    return owner


def _is_gatekeeper(node) -> bool:
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == GATEKEEPER)


def _opens_for_writing(node: ast.Call) -> bool:
    """True for `open(path, 'w')` and its variants, false for a plain read."""
    if not (isinstance(node.func, ast.Name) and node.func.id == "open"):
        return False
    mode = node.args[1] if len(node.args) > 1 else next(
        (k.value for k in node.keywords if k.arg == "mode"), None)
    if mode is None:
        return False                                   # no mode given means read
    if not (isinstance(mode, ast.Constant) and isinstance(mode.value, str)):
        return True                                    # a computed mode is not readable here
    return bool(set(mode.value) & WRITE_MODES)


def test_gallery_writes_only_under_private():
    """No write in the generator has a destination the gallery root does not own.

    Static half: every writing call's destination, which is the receiver for a
    method like `path.write_text(...)` and the first argument for one like
    `fig.savefig(path)`, has to be an `out_path(...)` call. Runtime half:
    `out_path` refuses to resolve outside the gallery root, so the single
    licensed destination cannot be talked into leaving it.
    """
    tree = _tree()
    owner = _enclosing_functions(tree)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Attribute) and node.func.attr in WRITE_METHODS:
            name = node.func.attr
            receiver, first = node.func.value, (node.args[0] if node.args else None)
        elif _opens_for_writing(node):
            name = "open for writing"
            receiver, first = None, (node.args[0] if node.args else None)
        else:
            continue
        # the gatekeeper creates the folder it is about to hand back, which is
        # the one write that cannot itself go through the gatekeeper
        if owner.get(id(node)) == GATEKEEPER:
            continue
        if _is_gatekeeper(receiver) or _is_gatekeeper(first):
            continue
        offenders.append(f"line {node.lineno}: {name}(...) with no {GATEKEEPER}(...) "
                         "destination")
    assert not offenders, (
        f"{GENERATOR.name} writes outside the one licensed destination:\n  "
        + "\n  ".join(offenders))

    spec = importlib.util.spec_from_file_location("make_qc_gallery", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    assert mod.GALLERY_DIR == ROOT / "private" / "qc_gallery", (
        f"the gallery root moved to {mod.GALLERY_DIR}")
    for escape in (("..", "figures", "stolen.png"),
                   ("..", "..", "results", "stolen.csv"),
                   ("subdir", "..", "..", "escaped.png")):
        with pytest.raises(ValueError):
            mod.out_path(*escape)

    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert any(line.strip() in {"/private/", "private/"} for line in ignore), (
        "private/ is no longer ignored wholesale, so the gallery would become "
        "publishable output")


def test_gallery_never_routes_through_the_citable_saver():
    """Do-not one. `figures/` is the citable tree: everything in it carries a
    data fingerprint, answers to the figure register and is held fresh against
    the results. Audit imagery belongs to none of that, so the generator must
    not reach the figure saver, by import or by attribute."""
    tree = _tree()
    offenders = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").endswith("make_figures"):
            names = [a.name for a in node.names if a.name.startswith("_save")]
            if names:
                offenders.append(f"line {node.lineno}: imports {names} from the figure script")
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Attribute) and fn.attr == "_save":
                offenders.append(f"line {node.lineno}: calls a figure saver")
            if isinstance(fn, ast.Name) and fn.id == "_save":
                offenders.append(f"line {node.lineno}: calls a figure saver")
    assert not offenders, "\n  ".join(offenders)


def test_gallery_is_not_a_figure_register_target():
    """Do-not two. The exemption is structural rather than editorial. The
    register's own tests key on `_footer(...)`, the provenance helper every
    citable figure calls and this generator has none of, so listing it as a
    target would fail on the missing helper rather than on any wording. The
    panels are held to their own register instead, by
    `test_no_pipeline_shorthand_reaches_a_panel` below, which bans the same
    shorthand on a drawn string."""
    from test_figure_register import TARGETS
    assert GENERATOR not in TARGETS, (
        "the gallery was added to the figure register targets, which would "
        "forbid the field names its panels exist to show")


def test_gallery_is_not_wired_into_the_gate():
    """Do-not three. The gallery is an audit that can trigger a recompute, not
    a gate that blocks one. It needs the raw archive, which a fresh clone does
    not have, and it takes minutes rather than seconds."""
    offenders = []
    for rel in ("scripts/ci_gate.sh", "scripts/run_all.sh",
                ".github/workflows/tests.yml"):
        path = ROOT / rel
        if path.exists() and "make_qc_gallery" in path.read_text(encoding="utf-8"):
            offenders.append(rel)
    assert not offenders, f"the gallery is wired into {offenders}"


# Shorthand two external reviewers found on the rendered panels and could not
# read. Each one is a phrase the pipeline uses among its own tests and tables and
# that means nothing to a physicist meeting the archive for the first time.
BANNED_ON_A_PANEL = (
    "the tail test",
    "the fit of record",
    "marked, still inside",
    "outside its group",
    "the record removed or marked",
    "the ones that carry the physics",
)


def _prose_strings(tree: ast.AST) -> list:
    """Every string literal in the generator except the ones addressed to
    whoever edits it next, which are the docstrings and the bare string
    expressions used to document a constant."""
    exempt = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if not isinstance(body, list):
            continue
        for i, stmt in enumerate(body):
            first = i == 0 and isinstance(node, (ast.Module, ast.ClassDef,
                                                 ast.FunctionDef,
                                                 ast.AsyncFunctionDef))
            follows_assign = i > 0 and isinstance(body[i - 1],
                                                  (ast.Assign, ast.AnnAssign))
            if (first or follows_assign) and isinstance(stmt, ast.Expr) \
                    and isinstance(stmt.value, ast.Constant) \
                    and isinstance(stmt.value.value, str):
                exempt.add(id(stmt.value))
    return [(n.lineno, n.value) for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in exempt]


def test_no_pipeline_shorthand_reaches_a_panel():
    """The panel register, held as a check rather than as a habit.

    A panel is read by a prospective supervisor and by a funder, neither of whom
    has seen this repository, so nothing on one may depend on knowing what a
    test, a table or a status code is called here.
    """
    offenders = []
    for lineno, text in _prose_strings(_tree()):
        low = text.lower()
        for phrase in BANNED_ON_A_PANEL:
            if phrase in low:
                offenders.append(f"line {lineno}: {phrase!r} in a drawn string")
    assert not offenders, (
        "pipeline shorthand reaches a reader's picture:\n  " + "\n  ".join(offenders))


def test_the_tooth_correction_is_gated_on_the_amplitudes():
    """Two gates, and neither of them is the labelling verdict.

    WHICH combs carry a displaced grid is the amplitude test of amendment 5
    section E5: a second-order tooth cannot stand above a first-order tooth at
    any depth below 2 beta = 2.63, where the Bessel weights cross, and the
    measured depth stays well below it. The verdict is wrong for that job in
    both directions. It misses two combs recorded as marginal passes that carry
    a plainly displaced grid, and by ranking the carrier at all it invites a
    reader to treat a height that identifies nothing as a defect, since the
    carrier carries the residual amplitude modulation.

    WHETHER a correction is accepted is the ratio test of amendment 6 section
    F4: the corrected numbering has to bring the second-to-first height ratio
    into the band the campaign measured. The carrier is out of that one too, in
    both directions: a comb with a tall carrier and a good ratio is accepted,
    and a comb with a textbook carrier and a bad ratio is not.
    """
    spec = importlib.util.spec_from_file_location("make_qc_gallery", GENERATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # heights run from k = -3 to k = +3. A textbook comb below the crossing.
    good = [0.001, 0.005, 0.026, 0.016, 0.026, 0.005, 0.001]
    assert not mod.displaced_grid(good), (
        "a comb whose carrier sits below its own first-order pair was called "
        "displaced, which is the misreading the pages exist to prevent")

    # the same comb, read one slot across: a second-order tooth now outranks a
    # first-order one, which any depth below the crossing forbids
    shifted = [0.005, 0.026, 0.016, 0.026, 0.005, 0.001, 0.0002]
    assert mod.displaced_grid(shifted)
    assert mod.derive_tooth_shift(shifted) == -1

    # the ratio test. The band is the Bessel ratio across the measured depths,
    # and it has to bracket the ratio the textbook comb above actually shows.
    lo, hi = mod.RATIO_BAND
    assert 0.0 < lo < hi < 1.0
    r, _ = mod.second_to_first_ratio(shifted, -1)
    assert lo <= r <= hi, "the corrected numbering left the measured band"
    r0, _ = mod.second_to_first_ratio(shifted, 0)
    assert r0 > mod.RATIO_CROSSING, (
        "the numbering the fit produced has to be unphysical for there to be "
        "anything to correct")

    # the carrier plays no part in either direction. Raising the carrier alone,
    # which residual amplitude modulation does, must change no verdict.
    tall = list(good)
    tall[3] = 0.040
    assert not mod.displaced_grid(tall)
    assert mod.second_to_first_ratio(tall, 0) == mod.second_to_first_ratio(good, 0)

    # and a ratio whose error reaches the band settles nothing, which is a
    # different outcome from a ratio that misses it and is measured well
    assert mod.ratio_agrees(hi + 0.05, 0.20)
    assert not mod.ratio_agrees(hi + 0.05, 0.001)

    src = _source()
    assert "displaced_grid(f[\"heights\"])" in src, (
        "the tooth correction no longer reads the amplitude test")
    assert 'verdict") or ""' not in src, (
        "the tooth correction is gated on the labelling verdict again")


def test_gallery_docstring_states_the_three_do_nots():
    """The three decisions are stated where the next reader of the file will
    find them, not only where the guard for them lives."""
    doc = ast.get_docstring(_tree()) or ""
    assert re.search(r"\bDO-NOTS\b", doc), "the do-nots are not stated in the docstring"
    for n, needle in ((1, "_save"), (2, "test_figure_register.py"), (3, "ci_gate.sh")):
        assert needle in doc, f"do-not {n} is not stated in the docstring"
