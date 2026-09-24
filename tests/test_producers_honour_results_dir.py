"""Every producer reads and writes its tables where `RB5S6S_RESULTS_DIR` points.

WHY THIS EXISTS (F480, 2026-09-24). `scripts/verify_results_fresh.py` re-runs a producer into a PRIVATE
directory by setting `RB5S6S_RESULTS_DIR`, and `rb5s6s.config.RESULTS_DIR` honours it. Thirteen producers
built the path by hand as `ROOT / "results"` instead, so a re-run "into a private directory" read the live
tables and, for six of them, WROTE the live tree: a re-obtain chain rewrote `results/twin_closed_loop.csv`
in the checkout while its private copy stayed the seed, which reads exactly like a perfect reproduction.
Most of the thirteen sit in the verifier's EXPENSIVE set, which no gate runs, so nothing had seen it.

The shape refused is a path expression `<ROOT-like name> / "results"` in a producer's CODE, found with
`ast` so a comment or a docstring naming the directory is not a hit.
"""
from __future__ import annotations

import ast
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
_ROOT_NAMES = {"ROOT", "REPO_ROOT", "HERE", "BASE"}


def hard_coded_results(src: str) -> list[int]:
    """Line numbers of `<ROOT-like> / "results"` in the code of `src`."""
    out = []
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
                and isinstance(node.right, ast.Constant) and node.right.value == "results"):
            left = node.left
            name = left.id if isinstance(left, ast.Name) else left.attr if isinstance(left, ast.Attribute) else None
            if name in _ROOT_NAMES:
                out.append(node.lineno)
    return out


def test_the_guard_sees_the_shape_and_nothing_else():
    """The plant, both ways: the hand-built path is seen at any depth of a path chain and through an
    attribute; the configured directory, a comment and a string are not."""
    assert hard_coded_results('out = ROOT / "results" / "x.csv"\n') == [1]
    assert hard_coded_results('RESULTS = C.REPO_ROOT / "results"\n') == [1]
    assert hard_coded_results('out = _RESULTS_DIR / "x.csv"\n') == []
    assert hard_coded_results('# ROOT / "results" in a comment\nx = "ROOT / results"\n') == []


def test_no_producer_hard_codes_the_results_directory():
    bad = [f"{p.name}:{ln}" for p in sorted((ROOT / "scripts").glob("run_*.py"))
           for ln in hard_coded_results(p.read_text(encoding="utf-8"))]
    assert not bad, ("these producers build the results path by hand, so a re-run under "
                     "RB5S6S_RESULTS_DIR reads or writes the LIVE tree: " + ", ".join(bad)
                     + ". Use rb5s6s.config.RESULTS_DIR.")


def test_a_private_rerun_writes_its_ladder_rungs_beside_its_tables(monkeypatch, tmp_path):
    """F482: a re-run under a private RB5S6S_RESULTS_DIR overwrote the LIVE ladder rung of window_surface,
    the gate's own evidence. Its rungs now go beside its tables; the live tree's run, and a caller naming
    its own cache, write where they always did."""
    from rb5s6s import ladder_gate as lg
    monkeypatch.setenv("RB5S6S_RESULTS_DIR", str(tmp_path))
    assert lg.record_dir("window_surface") == tmp_path / ".ladder_private" / "window_surface"
    assert lg.record_dir("window_surface", cache=tmp_path / "c") == tmp_path / "c" / ".ladder" / "window_surface"
    monkeypatch.setenv("RB5S6S_RESULTS_DIR", str(lg.ROOT / "results"))
    assert lg.record_dir("window_surface") == lg.ladder_dir("window_surface")
    monkeypatch.delenv("RB5S6S_RESULTS_DIR")
    assert lg.record_dir("window_surface") == lg.ladder_dir("window_surface")
