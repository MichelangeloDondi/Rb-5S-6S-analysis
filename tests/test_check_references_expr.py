"""Plants for the ref:expr: derived-reference form and --thesis-outbox (owner order O40).

WHY A SEPARATE FILE. tests/test_references.py already grades check_references.py against
THIS repository's own tracked corpus, which is exactly the tree these plants must never
touch: the working rules for this repository forbid running check_references.py --fix
against the real tree, so every plant here builds its own throwaway git repository under
pytest's tmp_path and points the loaded module's ROOT, RESULTS and LIT at it, the same
monkeypatch style test_references.py already uses for _csv_cell and _constant_value.

WHAT A SCRATCH REPOSITORY BUYS. _reference_population() discovers files through
`git -C ROOT ls-files`, not a directory walk, so a scratch tree needs `git init` and
`git add` for its documents to be seen at all. No commit is needed: ls-files reads the
index. results/*.csv is read straight off disk and never needs to be tracked.

Loaded by path, exactly like the existing ambiguous-coordinate and constant-reference
plants in tests/test_references.py, so the checker under test is always the one on disk
and never a cached, possibly stale, import.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_references.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_references_expr_plant", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _scratch_repo(tmp_path: Path) -> Path:
    """A throwaway git repository so git ls-files sees exactly what this test wrote."""
    repo = tmp_path / "repo"
    (repo / "results").mkdir(parents=True)
    (repo / "docs" / "lit").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def _tracked(repo: Path, relpath: str, text: str) -> Path:
    p = repo / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", relpath], check=True)
    return p


def _point_at(mod, repo: Path) -> None:
    mod.ROOT = repo
    mod.RESULTS = repo / "results"
    mod.LIT = repo / "docs" / "lit"


# ---------------------------------------------------------------------------------------
# 1. An expression site that agrees passes, and one that disagrees is a finding.
# ---------------------------------------------------------------------------------------

def test_an_agreeing_expression_site_is_not_a_finding(tmp_path, capsys):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)
    _tracked(repo, "results/x.csv", "quantity,key,value\nspeed,a,2\n")
    _tracked(repo, "p.md",
              'the sum is [7](../results/x.csv "ref:expr:{x:speed:a} + 5") today\n')

    rc = mod._report()
    out = capsys.readouterr().out

    assert rc == 0, out
    assert "1 references resolved, 0 findings" in out


def test_a_disagreeing_expression_site_is_a_finding(tmp_path, capsys):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)
    _tracked(repo, "results/x.csv", "quantity,key,value\nspeed,a,2\n")
    # x:speed:a + 5 is 7, and the page reads 9: stale by construction.
    _tracked(repo, "p.md",
              'the sum is [9](../results/x.csv "ref:expr:{x:speed:a} + 5") today\n')

    rc = mod._report()
    out = capsys.readouterr().out

    assert rc == 1, out
    assert "1 references resolved, 1 findings" in out
    assert "writes '9'" in out
    assert "evaluates to '7.0'" in out


# ---------------------------------------------------------------------------------------
# 2. --fix makes a disagreeing site agree, and a second --fix changes nothing.
# ---------------------------------------------------------------------------------------

def test_fix_rewrites_a_stale_expression_site_idempotently(tmp_path, capsys):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)
    _tracked(repo, "results/x.csv", "quantity,key,value\nspeed,a,2\n")
    doc = _tracked(repo, "p.md",
                    'the sum is [9](../results/x.csv "ref:expr:{x:speed:a} + 5") today\n')

    rc1 = mod._fix()
    out1 = capsys.readouterr().out
    after_first = doc.read_text(encoding="utf-8")

    assert rc1 == 0, out1
    assert "rewrote" in out1
    assert '[7](../results/x.csv "ref:expr:{x:speed:a} + 5")' in after_first
    # confirm the report now agrees, on the file --fix actually wrote
    assert mod._report() == 0
    capsys.readouterr()

    rc2 = mod._fix()
    out2 = capsys.readouterr().out
    after_second = doc.read_text(encoding="utf-8")

    assert rc2 == 0, out2
    assert "fix: 0 rewritten, 0 flagged for a human" in out2
    assert after_second == after_first, "a second --fix must be a no-op"


# ---------------------------------------------------------------------------------------
# 3. An expression naming a missing reference is an error, never a silent pass.
# ---------------------------------------------------------------------------------------

def test_an_unresolvable_reference_inside_an_expression_raises(tmp_path):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)

    with pytest.raises(mod.ExprError, match="unresolved reference"):
        mod._eval_expr("{nonexistent_stem:a:b} + 1")


def test_an_unresolvable_expression_site_is_a_report_finding_not_a_silent_pass(tmp_path, capsys):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)
    _tracked(repo, "p.md",
              'the sum is [1](../results/x.csv "ref:expr:{nonexistent_stem:a:b} + 1") today\n')

    rc = mod._report()
    out = capsys.readouterr().out

    assert rc == 1, out
    assert "EXPRESSION ERROR" in out
    assert "unresolved reference" in out


# ---------------------------------------------------------------------------------------
# 4. Eval-injection text in an expression is refused, never evaluated.
# ---------------------------------------------------------------------------------------

def test_eval_injection_text_in_an_expression_is_refused(tmp_path):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)
    _tracked(repo, "results/x.csv", "quantity,key,value\nspeed,a,2\n")

    # A bare call: no curly braces at all, so it reaches ast.parse directly.
    with pytest.raises(mod.ExprError):
        mod._eval_expr("__import__('os').system('true')")

    # A call MIXED with a reference that genuinely resolves: the whitelist must still
    # refuse the whole expression, not evaluate the resolvable half.
    with pytest.raises(mod.ExprError):
        mod._eval_expr("{x:speed:a} + __import__('os').system('true')")

    # A bare name: no operator, no call, still outside the whitelist.
    with pytest.raises(mod.ExprError):
        mod._eval_expr("os")

    # A string literal is a Constant but not a number.
    with pytest.raises(mod.ExprError):
        mod._eval_expr("{x:speed:a} + 'rm -rf /'")

    # None of the above may have executed: confirm _eval_expr never raised anything
    # OTHER than ExprError (a bare exec would surface as a different exception class
    # or, worse, as a silent success), and that a genuinely safe expression still works.
    assert mod._eval_expr("{x:speed:a} + 5") == 7.0


# ---------------------------------------------------------------------------------------
# 5. --graph lists an expression site as a dependent of every reference it reads.
# ---------------------------------------------------------------------------------------

def test_graph_lists_an_expression_site_as_a_dependent_of_what_it_reads(tmp_path):
    mod = _load()
    repo = _scratch_repo(tmp_path)
    _point_at(mod, repo)
    _tracked(repo, "results/x.csv", "quantity,key,value\nspeed,a,2\n")
    _tracked(repo, "p.md",
              'the sum is [7](../results/x.csv "ref:expr:{x:speed:a} + 5") today\n')

    out_path = mod._emit_graph()
    graph = json.loads(out_path.read_text(encoding="utf-8"))

    assert "x:speed:a" in graph, graph.keys()
    dependents = graph["x:speed:a"].get("expr_dependents", [])
    assert len(dependents) == 1, dependents
    assert dependents[0]["file"] == "p.md"
    assert dependents[0]["expr"] == "{x:speed:a} + 5"


# ---------------------------------------------------------------------------------------
# 6. --thesis-outbox: a row for a moved cell, none for an unmoved one, and read-only.
# ---------------------------------------------------------------------------------------

def test_thesis_outbox_writes_a_row_only_for_the_tag_that_moved(tmp_path):
    mod = _load()
    results = tmp_path / "results"
    results.mkdir()
    mod.RESULTS = results
    mod.LIT = tmp_path / "docs" / "lit"
    (results / "x.csv").write_text("quantity,key,value\nspeed,a,2\nspeed,b,9\n")

    chapter = tmp_path / "chapter.md"
    chapter.write_text(
        "# 7 The method\n\n"
        "The stale one reads "
        '[999](../results/x.csv "ref:x:speed:a") here.\n\n'
        "# 8 A later section\n\n"
        "The fresh one reads "
        '[9](../results/x.csv "ref:x:speed:b") here.\n',
        encoding="utf-8")
    outbox = tmp_path / "outbox.md"

    rc = mod._thesis_outbox(str(chapter), outbox_path=str(outbox))

    assert rc == 0
    assert outbox.exists()
    body = outbox.read_text(encoding="utf-8")
    assert "ref:x:speed:a" in body, body
    assert "999" in body and "2" in body
    assert "ref:x:speed:b" not in body, (
        "the unmoved tag must not appear in the outbox at all")
    assert "7 The method" in body, "the section column should name the nearest heading"


def test_thesis_outbox_writes_nothing_when_every_tag_agrees(tmp_path):
    mod = _load()
    results = tmp_path / "results"
    results.mkdir()
    mod.RESULTS = results
    mod.LIT = tmp_path / "docs" / "lit"
    (results / "x.csv").write_text("quantity,key,value\nspeed,a,2\n")

    chapter = tmp_path / "chapter.md"
    chapter.write_text(
        'the value is [2](../results/x.csv "ref:x:speed:a") exactly\n', encoding="utf-8")
    outbox = tmp_path / "outbox.md"

    rc = mod._thesis_outbox(str(chapter), outbox_path=str(outbox))

    assert rc == 0
    assert not outbox.exists(), "an unmoved chapter must never touch the outbox file"


def test_thesis_outbox_never_opens_the_chapter_file_for_writing(tmp_path):
    mod = _load()
    results = tmp_path / "results"
    results.mkdir()
    mod.RESULTS = results
    mod.LIT = tmp_path / "docs" / "lit"
    (results / "x.csv").write_text("quantity,key,value\nspeed,a,2\n")

    chapter = tmp_path / "chapter.md"
    chapter.write_text(
        'the stale one reads [999](../results/x.csv "ref:x:speed:a") here\n', encoding="utf-8")
    before = chapter.read_text(encoding="utf-8")
    outbox = tmp_path / "outbox.md"

    chapter.chmod(0o444)
    try:
        rc = mod._thesis_outbox(str(chapter), outbox_path=str(outbox))
        assert rc == 0
        assert outbox.exists()
    finally:
        chapter.chmod(0o644)

    after = chapter.read_text(encoding="utf-8")
    assert after == before, "the chapter file must be byte-identical: it was only read"


def test_thesis_outbox_on_a_missing_chapter_reads_nothing_and_writes_nothing(tmp_path):
    mod = _load()
    outbox = tmp_path / "outbox.md"

    rc = mod._thesis_outbox(str(tmp_path / "does_not_exist.md"), outbox_path=str(outbox))

    assert rc == 1
    assert not outbox.exists()
