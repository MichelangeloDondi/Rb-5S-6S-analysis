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

The other three tests here hold the three do-nots the generator's own docstring
states, so that each of them is a check rather than a note: it never routes
through the citable figure saver, it is never added to the figure register's
targets, and it is never wired into the gate.
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
    """Do-not two. The register forbids pipeline vocabulary on a drawn figure.
    These panels exist to print exactly that vocabulary, verbatim, because the
    reader is checking those fields against the tables that hold them."""
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


def test_gallery_docstring_states_the_three_do_nots():
    """The three decisions are stated where the next reader of the file will
    find them, not only where the guard for them lives."""
    doc = ast.get_docstring(_tree()) or ""
    assert re.search(r"\bDO-NOTS\b", doc), "the do-nots are not stated in the docstring"
    for n, needle in ((1, "_save"), (2, "test_figure_register.py"), (3, "ci_gate.sh")):
        assert needle in doc, f"do-not {n} is not stated in the docstring"
