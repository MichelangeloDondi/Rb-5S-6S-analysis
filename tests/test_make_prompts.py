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
    # the maker asks board_ledger which model a seat runs on rather than
    # deciding inline, so the fixture carries the real ledger: the inline copy
    # is how the helper and the emitted prompts disagreed for a whole round
    # without anything noticing (2026-09-08)
    _ledger = ROOT / "private" / "checks" / "board_ledger.py"
    if _ledger.is_file():
        (tmp_path / "private" / "checks" / "board_ledger.py").write_text(_ledger.read_text())
    for name in ("seat_brief.py", "reader_brief.py"):
        # stubs standing in for the brief emitters: each prints a marker the
        # positive test looks for, so an empty section cannot pass as a full one
        (tmp_path / "private" / "checks" / name).write_text(
            "import sys\nprint('STUB', sys.argv[0].rsplit('/', 1)[-1], *sys.argv[1:])\n")
    (tmp_path / "private" / "cache").mkdir()
    # a drafted message and the real coverage checker, so the branch that RUNS
    # a checker is exercised: the first form of this fixture carried neither,
    # so the only branch its test could reach was the one where a checker is
    # absent, and the running branch shipped a defect nobody's test could see
    # (the rules seat, 2026-09-08)
    (tmp_path / "private" / "cache" / "COMMIT_MSG_fixture.txt").write_text(
        "Subject line\n\nA body.\n\nReaches: a.md\n")
    _covers = ROOT / "private" / "checks" / "message_covers_staged.py"
    if _covers.is_file():
        (tmp_path / "private" / "checks" / "message_covers_staged.py").write_text(_covers.read_text())
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
        filed = (repo / "private" / "cache" / "boards"
                 / f"seat_reports_{tree[:12]}" / f"{seat}.PROMPT.md")
        assert filed.is_file() and filed.read_text().startswith(f"MODEL: {model}\n")


def test_it_refuses_a_brief_whose_commit_or_count_contradicts_git(tmp_path):
    """Two findings from one round, and both were typed by the convener.

    A wave brief named a prior commit the round did not read, and gave a file
    count that was not the delta. Eleven seats were briefed on both. The
    emitter already computes the prior pair and the staged count for the
    prompt, so a typed fact that disagrees with them is always the wrong one
    and the prompt refuses instead of printing it.
    """
    repo = _repo(tmp_path)
    tree = _tree(repo)
    _marker(repo, tree, ["physics", "rules", "concision"], opus=["rules"])
    brief = repo / "private" / "cache" / "WAVE_BRIEF.md"
    good = brief.read_text()

    # a real-looking sha that is not one of this round's prior commits
    brief.write_text(good + "\nPrior commit: deadbeef\n")
    r = _run(repo, "physics")
    assert r.returncode == 1, "a brief naming a foreign commit was emitted"
    assert "deadbeef" in r.stderr and "REFUSING" in r.stderr

    # AND A FILE COUNT THAT IS NOT THE STAGED DELTA. The count check is
    # conditional on something being staged, which is right: an on-head round
    # stages nothing and has no delta to contradict. So the fixture stages one
    # file before this half, and the marker is re-stamped because staging
    # moves the tree the board opened on.
    import subprocess
    (repo / "staged_for_the_count.txt").write_text("x\n")
    subprocess.run(["git", "add", "staged_for_the_count.txt"], cwd=repo, check=True)
    tree2 = _tree(repo)
    _marker(repo, tree2, ["physics", "rules", "concision"], opus=["rules"])
    brief.write_text(good + "\nThis wave moves 4321 files.\n")
    r = _run(repo, "physics")
    assert r.returncode == 1, "a brief with a wrong file count was emitted"
    assert "4321" in r.stderr and "staged set is 1" in r.stderr

    # the unmodified brief still emits, so the guard is not simply refusing
    brief.write_text(good)
    r = _run(repo, "physics")
    assert r.returncode == 0, r.stderr


def test_it_refuses_a_brief_carrying_the_retired_seat_model_wording(tmp_path):
    """Three surfaces described the retired catch-up form on 2026-09-08 while
    the ledger ran the convenings rule; a brief is what the seats are told."""
    repo = _repo(tmp_path)
    (repo / "private" / "cache" / "WAVE_BRIEF.md").write_text("# wave\na seat unpaid is written as rotation_miss\n")
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 1 and "retired" in r.stderr


def _prepare(repo, tmp_path, floor="0.001"):
    return subprocess.run([sys.executable, str(repo / "private/checks/make_prompts.py"), "--prepare-copy"],
                          capture_output=True, text=True, cwd=repo,
                          env=dict(os.environ, BOARD_COPY_ROOT=str(tmp_path / "copies"),
                                   BOARD_FREE_GB_FLOOR=floor))


def test_prepare_copy_asserts_the_tree_on_the_copy_and_on_the_recipe(tmp_path):
    """A git clone of the board copy carries HEAD and DROPS the staged change
    (four seats graded the prior commit's tree, 2026-09-08), so the recipe the
    prompt prints is a clone plus the staged diff, and the preparation runs
    that recipe on a probe and asserts its tree. The held papers are excluded:
    `git write-tree` reads the index, so an absent working file cannot move
    the tree the copy asserts."""
    repo = _repo(tmp_path)
    staged = repo / "staged_only.md"
    staged.write_text("a file a bare clone would drop\n")
    subprocess.run(["git", "add", "staged_only.md"], cwd=repo, check=True)
    (repo / "PDF_papers").mkdir()
    (repo / "PDF_papers" / "held.pdf").write_text("x" * 4096)
    tree = _tree(repo)
    _marker(repo, tree, ["physics"])
    r = _prepare(repo, tmp_path)
    assert r.returncode == 0, r.stderr
    copy = tmp_path / "copies" / f"board_{tree[:12]}"
    assert _tree(copy) == tree and "asserted" in r.stdout
    assert (copy / "staged_only.md").is_file(), "the recipe must carry the staged change"
    assert not (copy / "PDF_papers").exists(), "the held papers are not copied"
    assert not (tmp_path / "copies" / f"board_{tree[:12]}_probe").exists()
    assert "GB free after it" in r.stdout


def test_prepare_copy_sweeps_stale_copies_and_refuses_a_full_volume(tmp_path):
    """Eleven seats each keeping a copy of the tree ran a 228 GB volume to
    zero bytes free on 2026-09-08 and killed a round outright: every seat lost
    git, the shared findings file and its own shell, and about thirty copies
    from earlier rounds were still there because nothing had ever swept one.
    The preparation sweeps first and reads the free space after."""
    repo = _repo(tmp_path)
    tree = _tree(repo)
    _marker(repo, tree, ["physics"])
    copies = tmp_path / "copies"
    copies.mkdir()
    (copies / "board_deadbeef0000").mkdir()
    (copies / "seat_physics_999").mkdir()
    r = _prepare(repo, tmp_path)
    assert r.returncode == 0, r.stderr
    assert not (copies / "board_deadbeef0000").exists()
    assert not (copies / "seat_physics_999").exists()
    assert "swept 2 stale" in r.stdout

    # the negative, through the same path: a floor no volume can clear
    r2 = _prepare(repo, tmp_path, floor="1000000")
    assert r2.returncode == 1 and "REFUSING" in r2.stderr
    assert "under the 1000000 GB floor" in r2.stderr


def test_it_refuses_when_a_brief_script_fails(tmp_path):
    """A brief emitter that dies must not leave an empty section behind a
    zero exit: three seats of 2026-09-08 showed the maker shipping blank
    standing briefs from a fixture without the emitters."""
    repo = _repo(tmp_path)
    (repo / "private" / "checks" / "seat_brief.py").write_text("import sys\nsys.exit(3)\n")
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 1 and "seat_brief.py" in r.stderr and "failed" in r.stderr


def test_the_prompt_names_the_rulebook_and_does_not_carry_it(tmp_path):
    """Emitting the reader brief's index and a rule family's body verbatim put
    935 KB into eleven prompts on 2026-09-08, 600 KB of it the same index
    eleven times, and each seat re-read its whole prompt on every turn. The
    repository's rule file already said a brief names the rules and does not
    reproduce them. The prompt carries the file list and the commands; the
    reader runs one when a finding needs a rule."""
    repo = _repo(tmp_path)
    tree = _tree(repo)
    _marker(repo, tree, ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 0, r.stderr
    out = r.stdout
    assert "reader_brief.py --rules" in out, "the prompt must name the command"
    # 30 KB binds: a prompt measured 23.5 KB after the classes catalogue went
    # behind its own command too, from 30 KB after the first pass and 87 KB
    # before it. A ceiling above every real value grades nothing.
    assert len(out) < 30_000, f"the prompt is {len(out)} bytes; it carries a body it should name"


def test_the_prompt_carries_the_convener_s_own_checks(tmp_path):
    """Six seats independently ran the message checker on 2026-09-08 and filed
    the same omission. The convener runs the cheap checks once and the prompt
    carries their output, so reproducing one is spending budget against
    instruction. A checker that is absent is skipped with a line; only one
    that runs and dies refuses the prompt."""
    repo = _repo(tmp_path)
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 0, r.stderr
    assert "CHECKS THE CONVENER ALREADY RAN" in r.stdout
    # the RUNNING branch: the fixture carries the checker and a message, so its
    # verdict is in the prompt; and the absent branch still reports itself, for
    # check_references.py which the fixture does not carry
    assert "message covers the staged set" in r.stdout or "does not cover" in r.stdout
    assert "(absent here, so it was not run)" in r.stdout


def test_the_prompt_states_a_budget(tmp_path):
    """A reader that spent 200 thousand tokens and returned one finding is the
    long tail this figure exists to shorten; it is a cost and not a goal."""
    repo = _repo(tmp_path)
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert "YOUR BUDGET" in r.stdout and "not a target" in r.stdout


def test_an_on_head_board_names_its_real_prior_commits_and_checks_the_right_mode(tmp_path):
    """A round convened on a landed commit has nothing staged and HEAD IS the
    change being read, so counting back from HEAD names that commit itself as
    one of its own two predecessors, and the coverage checker's
    staged mode compares against an empty index. Both shipped in eleven
    prompts on 2026-09-08: the auto-generated half contradicted the
    hand-written half about which commits carry the two-commit read, and a
    false failure was pasted under the line telling each reader that a named
    defect is already known. One question answers both."""
    repo = _repo(tmp_path)
    for n in ("one", "two"):
        (repo / f"{n}.md").write_text(n + "\n")
        subprocess.run(["git", "add", f"{n}.md"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", f"commit {n}"], cwd=repo, check=True,
                       env=dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                                GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t"))
    head, prev = subprocess.run(["git", "log", "-2", "--format=%h"], cwd=repo,
                                capture_output=True, text=True).stdout.split()
    _marker(repo, _tree(repo), ["physics"])
    r = _run(repo, "physics")
    assert r.returncode == 0, r.stderr
    assert prev in r.stdout, "the prior pair must start one commit back from HEAD"
    assert head not in r.stdout.split("BINDING")[0], (
        "the head commit must not be named as one of its own predecessors")
