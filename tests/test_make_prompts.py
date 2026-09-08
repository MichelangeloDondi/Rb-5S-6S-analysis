"""The seat prompt maker refuses what the 2026-09-07 boards suffered from.

The seats of one round read briefs emitted before the board opened, whose
two halves named different trees, and some then ran a producer against the
canonical checkout. `private/checks/make_prompts.py` emits a seat's prompt
only from an open board's marker, only for a seat that board convenes, and
only while the staged tree is the one the board opened on; its first line is
the model the spawner passes. Each refusal is planted here on a copy under a
temporary directory, so the canonical checkout's marker is never touched.

SKIPPED WHERE `private/` IS ABSENT, which is every clone but this one.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "private" / "checks" / "make_prompts.py"

pytestmark = pytest.mark.skipif(
    not SRC.is_file(),
    reason="private/checks/make_prompts.py is absent, as it is in every "
           "clone but the archive")


def _repo(tmp_path: Path) -> Path:
    """A throwaway git repository carrying only the prompt maker."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    ident = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                 GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-q", "--allow-empty",
                    "-m", "seed"], check=True, env=ident)
    (tmp_path / "private" / "checks").mkdir(parents=True)
    (tmp_path / "private" / "checks" / "make_prompts.py").write_text(SRC.read_text())
    for name in ("seat_brief.py", "reader_brief.py"):
        # stubs standing in for the brief emitters: each prints a marker the
        # positive test looks for, so an empty section cannot pass as a full one
        (tmp_path / "private" / "checks" / name).write_text(
            "import sys\nprint('STUB', sys.argv[0].rsplit('/', 1)[-1], *sys.argv[1:])\n")
    (tmp_path / "private" / "cache").mkdir()
    # the severities block quotes LOGIC 0c.17; the maker checks the quote at emission
    (tmp_path / "private" / "LOGIC_PROTOCOL.md").write_text(
        "### 0c.17\n* SEVERITIES. CRITICAL: a published number or claim is wrong, or a\n"
        "  committed guard is red — a falsehood would ship. SEVERE: a claim stands\n"
        "  without its licensed support, or a guard hole could pass a falsehood.\n"
        "  MODERATE: a consistency or register defect with no wrong claim. MINOR:\n"
        "  wording and style. A seat's verdict is its worst finding's severity, or\n"
        "  CONFIRM.\n")
    (tmp_path / "private" / "cache" / "WAVE_BRIEF.md").write_text("# wave\n")
    return tmp_path


def _run(repo: Path, seat: str):
    return subprocess.run([sys.executable, str(repo / "private/checks/make_prompts.py"), seat],
                          capture_output=True, text=True, cwd=repo)


def _tree(repo: Path) -> str:
    return subprocess.run(["git", "write-tree"], capture_output=True, text=True,
                          cwd=repo).stdout.strip()


def _marker(repo: Path, tree: str, seats, opus=()):
    (repo / "private" / ".board_running").write_text(json.dumps(
        {"tree": tree, "seats": list(seats), "opus": list(opus)}))


def test_it_refuses_without_an_open_board(tmp_path):
    r = _run(_repo(tmp_path), "physics")
    assert r.returncode == 1 and "no open board" in r.stderr


def test_it_refuses_a_seat_the_board_does_not_convene(tmp_path):
    repo = _repo(tmp_path)
    _marker(repo, _tree(repo), ["rules", "strategy"])
    r = _run(repo, "physics")
    assert r.returncode == 1 and "does not convene" in r.stderr


def test_it_refuses_when_the_staged_tree_moved_since_begin(tmp_path):
    repo = _repo(tmp_path)
    _marker(repo, "0" * 40, ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 1 and "moved since --begin" in r.stderr


def test_it_emits_the_model_first_and_files_the_prompt(tmp_path):
    repo = _repo(tmp_path)
    tree = _tree(repo)
    _marker(repo, tree, ["physics", "rules", "concision"], opus=["rules"])
    for seat, model in (("physics", "fable"), ("rules", "opus"), ("concision", "sonnet")):
        r = _run(repo, seat)
        assert r.returncode == 0, r.stderr
        assert r.stdout.splitlines()[0] == f"MODEL: {model}"
        assert tree in r.stdout and "NEVER run pytest" in r.stdout
        assert f"STUB seat_brief.py --seat {seat}" in r.stdout and "STUB reader_brief.py" in r.stdout
        filed = repo / "private" / "cache" / f"seat_reports_{tree[:12]}" / f"{seat}.PROMPT.md"
        assert filed.is_file() and filed.read_text().startswith(f"MODEL: {model}\n")


def test_it_refuses_a_brief_carrying_the_retired_seat_model_wording(tmp_path):
    """Three surfaces described the retired catch-up form on 2026-09-08 while
    the ledger ran the convenings rule; a brief is what the seats are told."""
    repo = _repo(tmp_path)
    (repo / "private" / "cache" / "WAVE_BRIEF.md").write_text("# wave\na seat unpaid is written as rotation_miss\n")
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 1 and "retired" in r.stderr


def test_prepare_copy_asserts_the_tree_on_the_copy_and_on_the_recipe(tmp_path):
    """A git clone of the board copy carried HEAD and dropped the staged
    change (four seats, 2026-09-08); the preparation now asserts the copy's
    write-tree and exercises the cp -a recipe the prompt prints."""
    repo = _repo(tmp_path)
    tree = _tree(repo)
    _marker(repo, tree, ["physics"])
    r = subprocess.run([sys.executable, str(repo / "private/checks/make_prompts.py"), "--prepare-copy"],
                       capture_output=True, text=True, cwd=repo,
                       env=dict(os.environ, BOARD_COPY_ROOT=str(tmp_path / "copies")))
    assert r.returncode == 0, r.stderr
    copy = tmp_path / "copies" / f"board_{tree[:12]}"
    assert _tree(copy) == tree and "asserted" in r.stdout
    assert not (tmp_path / "copies" / f"board_{tree[:12]}_probe").exists()


def test_it_refuses_when_a_brief_script_fails(tmp_path):
    """A brief emitter that dies must not leave an empty section behind a
    zero exit: three seats of 2026-09-08 showed the maker shipping blank
    standing briefs from a fixture without the emitters."""
    repo = _repo(tmp_path)
    (repo / "private" / "checks" / "seat_brief.py").write_text("import sys\nsys.exit(3)\n")
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 1 and "seat_brief.py" in r.stderr and "failed" in r.stderr
