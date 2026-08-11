"""Every committed figure must be drawn by `make_figures.main()`.

Written 2026-08-10 after three figures spent a day as committed PNGs with no
live producer: their draw functions existed, were correct, and were never called
from main(), so `scripts/make_figures.py` did not reproduce them and neither did
`run_all.sh`. Nothing failed, because the freshness guard only tracks the
figures drawn from results CSVs, and these three are module-computed.

The failure mode is specific and worth naming: a figure written in one session
and drawn by hand looks finished, and the gap only shows up in a clean clone.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "make_figures.py"


def _tree():
    return ast.parse(SRC.read_text(encoding="utf-8"))


def _savers(tree):
    """{png name or literal prefix: enclosing function} for every _save call.

    A name built with an f-string, as the four per-peak fits are
    (`fig18_single_{peak}.png`), contributes its literal PREFIX, and a
    committed PNG starting with that prefix counts as produced. Resolving it
    exactly would mean executing the module.
    """
    out = {}
    for fn in [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]:
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "_save" and len(node.args) >= 2):
                continue
            arg = node.args[1]
            if isinstance(arg, ast.Constant):
                out[arg.value] = fn.name
            elif isinstance(arg, ast.JoinedStr) and arg.values:
                head = arg.values[0]
                if isinstance(head, ast.Constant) and head.value:
                    out[head.value] = fn.name
    return out


def _called_by_main(tree):
    main = next(n for n in ast.walk(tree)
                if isinstance(n, ast.FunctionDef) and n.name == "main")
    return {n.func.id for n in ast.walk(main)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def test_every_drawn_figure_is_reachable_from_main():
    tree = _tree()
    savers, called = _savers(tree), _called_by_main(tree)
    assert savers, "found no _save calls at all, so this guard is vacuous"
    orphans = sorted(f"{png} (drawn by {fn})"
                     for png, fn in savers.items() if fn not in called)
    assert not orphans, (
        "these figures are saved by a function main() never calls, so "
        "make_figures.py does not reproduce them:\n  " + "\n  ".join(orphans))


def test_every_committed_png_has_a_producer():
    savers = _savers(_tree())
    committed = {p.name for p in (ROOT / "figures").glob("*.png")}
    # Two figures are drawn by their own scripts rather than by make_figures,
    # and the methods map records both: fig0 by make_fig0_spectrum.py and fig9
    # by run_polarizability_ladder.py, which owns the polarizability ladder it
    # also computes.
    committed -= {"fig0_spectrum.png", "fig9_polarizability_ladder.png"}
    missing = sorted(png for png in committed
                     if not any(png == k or png.startswith(k) for k in savers))
    assert not missing, (
        "these PNGs are committed with no _save call in make_figures.py:\n  "
        + "\n  ".join(missing))
