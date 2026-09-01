"""The gate's verdict sentinel, tested by exercising it rather than reading it.

WHY THIS EXISTS. Protocol rule 19.24 says to read the exit code of the gate
itself. On 2026-08-15 that rule was defeated three times in one evening by
callers of the form `./scripts/ci_gate.sh > log; echo "EXIT: $?"`, which
reports the echo's status, and once more by `check_invariants.py | tail -3`,
which reports tail's. Every one read green over a red run.

Audit 5 had already recorded the general finding: of the rules written that
week, the only ones that ran without their author were the MECHANISED ones. A
habit that has been broken four times is not a control. So `ci_gate.sh` now
writes its verdict where a later shell construct cannot reach it, and this
test pins the behaviour that makes that worth relying on.

The blocks are EXTRACTED FROM THE SCRIPT rather than restated here, so that
editing the script's mechanism breaks this test instead of silently leaving
it testing a copy that no longer exists. An earlier extraction anchored on
the FIRST exit trap and kept passing while the script grew a second one
that replaced it at runtime, so the extractor now refuses a script with more than
one exit trap after GATE_VERDICT= -- an extraction anchor that is not
unique is testing a copy by construction. The design under test: the trap
writes only FAIL over RUNNING, and PASS or PASS_MODULO has exactly one
author, the explicit write at the end of the script, reached only when
every stage completed.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

GATE = Path(__file__).resolve().parents[1] / "scripts" / "ci_gate.sh"


def _text() -> str:
    return GATE.read_text()


def _sentinel_block() -> str:
    """From GATE_ROOT= through the single verdict trap, asserted unique."""
    text = _text()
    start = text.index("GATE_ROOT=")
    after = text[text.index("GATE_VERDICT="):]
    traps = re.findall(r"^trap .*EXIT$", after, re.M)
    assert len(traps) == 1, (
        "ci_gate.sh must install exactly one EXIT trap after GATE_VERDICT= "
        f"(found {len(traps)}): a second trap silently replaces the first "
        "and orphans this extraction")
    end = after.index(traps[0]) + len(traps[0])
    return text[start:text.index("GATE_VERDICT=") + end] + "\n"


def _final_block() -> str:
    """The end-of-script verdict write, the only author of PASS."""
    text = _text()
    start = text.index("# The final verdict.")
    m = re.search(r"^fi$", text[start:], re.M)
    assert m, "the final verdict write lost its closing fi"
    return text[start:start + m.end()] + "\n"


def _run(cmd: str, tmp_path: Path, caller: str = "{probe}",
         with_final: bool = False, pmod: str = "") -> str:
    """Run the extracted block(s) around `cmd`; return the verdict line.

    `caller` models how a careless caller invokes the gate, e.g. piping it.
    """
    verdict = tmp_path / "verdict"
    probe = tmp_path / "probe.sh"
    body = ("set -euo pipefail\n"
            "GATE_LOCK=$(mktemp -d)\nGATE_PYLOG=$(mktemp)\n"
            # the harness exercises the verdict machinery; the targeted
            # floor is its own scenario below, so every other probe skips
            # it exactly the way a caller with a reason would
            "export CI_GATE_SKIP_TARGETED='sentinel harness'\n"
            + _sentinel_block()
            + (f'PMOD="{pmod}"\n' if with_final else "")
            + cmd + "\n"
            + (_final_block() if with_final else ""))
    probe.write_text(body)
    invocation = caller.format(probe=f"bash {probe}")
    subprocess.run(["bash", "-c", invocation], capture_output=True,
                   env={"CI_GATE_VERDICT_FILE": str(verdict),
                        "PATH": "/usr/bin:/bin"})
    if not verdict.exists():
        return "<absent>"
    return verdict.read_text().splitlines()[0].strip()


def test_the_extracted_blocks_are_the_real_ones():
    """If the script stops carrying the mechanism, fail loudly, not quietly."""
    block = _sentinel_block()
    assert "printf 'RUNNING" in block, "the pre-write is what makes a crash safe"
    assert "trap" in block and "EXIT" in block
    assert "RUNNING" in block and "FAIL" in block
    trap_line = re.search(r"^trap .*EXIT$", block, re.M).group(0)
    assert "PASS" not in trap_line, (
        "the trap must never write a pass-class verdict: PASS has exactly "
        "one author, the end-of-script block")
    final = _final_block()
    assert "PASS_MODULO" in final and "PASS 0" in final


def test_a_passing_run_records_pass(tmp_path):
    """Green suite, all stages done, no register entries invoked."""
    assert _run("true", tmp_path, with_final=True) == "PASS 0"


def test_a_pass_modulo_run_records_its_entries(tmp_path):
    """An excused suite that completes every stage lands PASS_MODULO."""
    assert _run("true", tmp_path, with_final=True, pmod="1") == "PASS_MODULO 1"


def test_a_downstream_failure_after_an_excused_suite_is_fail(tmp_path):
    """PASS_MODULO is provisional: a stage failing after it must FAIL."""
    assert _run("exit 3", tmp_path, with_final=True, pmod="1") == "FAIL 3"


def test_a_failing_run_records_the_real_status(tmp_path):
    assert _run("exit 3", tmp_path) == "FAIL 3"


def test_a_trailing_echo_cannot_mask_a_failure(tmp_path):
    """The 2026-08-15 defeat, three times in one evening."""
    assert _run("exit 3", tmp_path, caller="{probe} > /dev/null; echo done") == "FAIL 3"


def test_a_pipe_cannot_mask_a_failure(tmp_path):
    """The same trap in the other direction, `checker | tail`.

    This is the case worth having a test for: the shell genuinely reports 0
    here, so nothing at the call site could have caught it.
    """
    masked = subprocess.run(["bash", "-c", "(exit 7) | tail -1"])
    assert masked.returncode == 0, "if this ever fails, the shell changed, not us"
    assert _run("exit 7", tmp_path, caller="{probe} 2>&1 | tail -1") == "FAIL 7"


def test_an_interrupted_run_never_reads_as_a_pass(tmp_path):
    """A killed gate leaves RUNNING, which is the whole point of pre-writing."""
    assert _run("kill -9 $$", tmp_path) == "RUNNING"


def test_a_stale_verdict_cannot_be_read_as_this_run(tmp_path):
    """A previous run's PASS must not survive into a run that dies early."""
    verdict = tmp_path / "verdict"
    verdict.write_text("PASS 0\ntree abc\n")
    assert _run("kill -9 $$", tmp_path) == "RUNNING"


def test_the_verdict_carries_the_tree_it_graded(tmp_path):
    """The second line binds the verdict to a tree, so the board ledger can
    refuse a green written for a different tree (19.24)."""
    verdict = tmp_path / "verdict"
    probe = tmp_path / "probe.sh"
    probe.write_text("set -euo pipefail\nGATE_LOCK=$(mktemp -d)\n"
                     "GATE_PYLOG=$(mktemp)\n"
                     "export CI_GATE_SKIP_TARGETED='sentinel harness'\n"
                     + _sentinel_block()
                     + 'PMOD=""\n' + _final_block())
    subprocess.run(["bash", str(probe)], capture_output=True,
                   env={"CI_GATE_VERDICT_FILE": str(verdict),
                        "PATH": "/usr/bin:/bin"})
    lines = verdict.read_text().splitlines()
    assert len(lines) >= 2 and lines[1].startswith("tree "), (
        "a verdict without its tree line cannot be bound to what it graded")


def test_a_green_suite_with_an_unusable_verdict_module_still_fails(tmp_path):
    """The fail-open this arm carried: rc 0 plus a crashed
    compute_gate_verdict made the catch-all exit 0, skipping every
    downstream stage with a green shell status. The arm must never exit
    0; this probe feeds it exactly that input."""
    text = GATE.read_text()
    assert text.count('GV=$(') == 1, "anchor not unique; extraction unsafe"
    start = text.index('GV=$(')
    end = text.index("esac", start) + 4
    block = text[start:end]
    probe = tmp_path / "probe.sh"
    probe.write_text("set -euo pipefail\nPYRC=0\nPY=/no/such/python\n"
                     "GATE_PYLOG=/dev/null\n" + block + "\necho REACHED_DOWNSTREAM\n")
    r = subprocess.run(["bash", str(probe)], capture_output=True, text=True,
                       env={"PATH": "/usr/bin:/bin"})
    assert r.returncode != 0, "a green suite with no verdict module exited 0"
    assert "REACHED_DOWNSTREAM" not in r.stdout


def test_the_verdict_file_is_ignored_by_git():
    """It is run state. A tracked one would differ per machine and per run."""
    root = GATE.parents[1]
    assert ".ci_gate_verdict" in (root / ".gitignore").read_text()
    out = subprocess.run(["git", "-C", str(root), "check-ignore", ".ci_gate_verdict"],
                         capture_output=True, text=True)
    if out.returncode == 128:
        pytest.skip("not a git checkout")
    assert out.returncode == 0, ".ci_gate_verdict is not actually ignored"


def _dirty_digest_fn() -> str:
    """The gate_dirty_digest function, extracted and asserted unique."""
    text = _text()
    assert text.count("gate_dirty_digest() {") == 1, "anchor not unique"
    start = text.index("gate_dirty_digest() {")
    end = text.index("\n}", start) + 2
    return text[start:end]


def _git_env(repo: Path) -> dict:
    return {"PATH": "/usr/bin:/bin", "HOME": str(repo),
            "GIT_AUTHOR_NAME": "s", "GIT_AUTHOR_EMAIL": "s@x.invalid",
            "GIT_COMMITTER_NAME": "s", "GIT_COMMITTER_EMAIL": "s@x.invalid"}


def _digest_in(repo: Path) -> str:
    out = subprocess.run(
        ["bash", "-c", _dirty_digest_fn() + "\ngate_dirty_digest"],
        capture_output=True, text=True, cwd=repo, env=_git_env(repo))
    assert out.returncode == 0, out.stderr
    return out.stdout.strip()


def test_the_chimera_digest_sees_what_its_comment_claims(tmp_path):
    """The plant for the dirty-tree digest, matched one-to-one to the
    comment in scripts/ci_gate.sh, direction by direction: an unstaged
    content edit; a SECOND edit to an already-dirty file (the hole a
    name-list digest had); staging a modified tracked file leaving the
    digest alone (the stated blind spot the verdict's tree line covers
    downstream); a hand edit under results/ (not special-cased); an
    untracked arrival; an edit INSIDE an untracked file staying
    invisible (the stated name-only limit, asserted so it stays
    stated); an untracked departure; and a NEW file staged mid-gate
    failing honestly. Eight directions. Nine assertions, one of them a consistency check that recreation restores the digest."""
    repo = tmp_path / "r"; repo.mkdir()
    env = _git_env(repo)
    run = lambda *a: subprocess.run(["git", *a], cwd=repo, env=env,
                                    capture_output=True, text=True)
    run("init", "-q")
    (repo / "f.txt").write_text("one\n")
    (repo / "results").mkdir()
    (repo / "results" / "x.csv").write_text("a,b\n1,2\n")
    run("add", "-A"); run("commit", "-q", "-m", "base")
    d0 = _digest_in(repo)
    (repo / "f.txt").write_text("two\n")
    d1 = _digest_in(repo)
    assert d1 != d0, "an unstaged edit is invisible"
    (repo / "f.txt").write_text("three\n")
    d2 = _digest_in(repo)
    assert d2 != d1, "a second edit to an already-dirty file is invisible"
    # the stated blind spot, exactly as the comment scopes it: staging a
    # MODIFIED tracked file leaves git diff HEAD unchanged, so the digest
    # must not move -- the ledger's tree binding is that case's cover.
    run("add", "f.txt")
    d2s = _digest_in(repo)
    assert d2s == d2, (
        "staging a modified tracked file moved the digest; the comment's "
        "split between this sentinel and the ledger's tree binding no "
        "longer matches the code")
    (repo / "results" / "x.csv").write_text("a,b\n1,999\n")
    d3 = _digest_in(repo)
    assert d3 != d2s, "a hand edit under results/ is invisible"
    (repo / "new.txt").write_text("n\n")
    d4 = _digest_in(repo)
    assert d4 != d3, "an untracked arrival is invisible"
    # the name-only limit, in both of its directions: content inside an
    # untracked file does not move the digest, its departure does.
    (repo / "new.txt").write_text("rewritten\n")
    d4e = _digest_in(repo)
    assert d4e == d4, (
        "an edit inside an untracked file moved the digest; the comment's "
        "name-only claim for untracked files no longer matches the code")
    (repo / "new.txt").unlink()
    d4g = _digest_in(repo)
    assert d4g != d4e, "an untracked departure went unseen"
    (repo / "new.txt").write_text("n\n")
    assert _digest_in(repo) == d4, "recreation did not restore the digest"
    # a NEW file staged mid-gate moves both halves of the digest, and
    # this assertion pins that FAIL so a future change cannot quietly
    # excuse it.
    run("add", "new.txt")
    d5 = _digest_in(repo)
    assert d5 != d4, "staging a new file mid-gate went unseen"


def test_the_governance_layer_refusal_fires(tmp_path):
    """The plant for the refuse-not-skip block: a checkout that cannot
    reach an existing governance layer must FAIL, not skip four stages."""
    text = _text()
    anchor = 'if [ -d "$GATE_ROOT/private/checks" ]'
    assert text.count(anchor) == 1, "anchor not unique"
    start = text.index(anchor)
    end = text.index("fi", start) + 2
    block = text[start:end]
    root = tmp_path / "main"; (root / "private" / "checks").mkdir(parents=True)
    elsewhere = tmp_path / "elsewhere"; elsewhere.mkdir()
    probe = tmp_path / "p.sh"
    probe.write_text(f'GATE_ROOT="{root}"\n' + block + "\necho SKIPPED_PAST\n")
    r = subprocess.run(["bash", str(probe)], capture_output=True, text=True,
                       cwd=elsewhere, env={"PATH": "/usr/bin:/bin"})
    assert r.returncode == 1, "the unreachable-layer case did not refuse"
    assert "SKIPPED_PAST" not in r.stdout
    reachable = tmp_path / "main2"
    (reachable / "private" / "checks").mkdir(parents=True)
    (reachable / "private" / "checks" / "protocol_citations.py").write_text("")
    probe.write_text(f'GATE_ROOT="{reachable}"\n' + block + "\necho OK\n")
    r2 = subprocess.run(["bash", str(probe)], capture_output=True, text=True,
                        cwd=reachable, env={"PATH": "/usr/bin:/bin"})
    assert r2.returncode == 0 and "OK" in r2.stdout


def test_the_common_dir_resolution_finds_the_main_checkout(tmp_path):
    """The plant for GATE_ROOT: from a linked worktree the verdict must
    anchor to the MAIN checkout's root, or two callers read two
    different verdict files (the --show-toplevel regression)."""
    text = _text()
    assert text.count('GATE_COMMON="$(') == 1, "anchor not unique"
    start = text.index('GATE_COMMON="$(')
    end = text.index('GATE_VERDICT=', start)
    block = text[start:end] + 'echo "$GATE_ROOT"\n'
    repo = tmp_path / "main"; repo.mkdir()
    env = _git_env(repo)
    run = lambda *a: subprocess.run(["git", *a], cwd=repo, env=env,
                                    capture_output=True, text=True)
    run("init", "-q")
    (repo / "f.txt").write_text("x\n")
    run("add", "-A"); run("commit", "-q", "-m", "base")
    wt = tmp_path / "wt"
    run("worktree", "add", "-q", str(wt))
    for cwd in (repo, wt):
        r = subprocess.run(["bash", "-c", block], capture_output=True,
                           text=True, cwd=cwd, env=env)
        got = Path(r.stdout.strip()).resolve()
        assert got == repo.resolve(), (
            f"from {cwd.name} the root resolved to {got}, not the main "
            "checkout, so two callers would read different verdict files")


def test_a_missing_targeted_stamp_refuses_before_any_verdict(tmp_path):
    """The targeted floor (workflow v2): no stamp, no gate, no verdict.

    The refusal must land BEFORE the RUNNING write, so a refused gate
    leaves whatever verdict a real run last recorded; a refusal that
    wrote RUNNING would turn every stamp mismatch into a fake
    interrupted-gate record. Run the extracted block in a bare
    directory with no .targeted_ok and no skip reason: it must exit 4
    and create nothing.
    """
    verdict = tmp_path / "verdict"
    probe = tmp_path / "probe.sh"
    probe.write_text("set -euo pipefail\n"
                     "GATE_LOCK=$(mktemp -d)\nGATE_PYLOG=$(mktemp)\n"
                     + _sentinel_block()
                     + "echo unreachable\n")
    done = subprocess.run(
        ["bash", str(probe)], cwd=tmp_path, capture_output=True, text=True,
        env={"PATH": "/usr/bin:/bin", "CI_GATE_VERDICT_FILE": str(verdict)})
    assert done.returncode == 4, (done.returncode, done.stdout, done.stderr)
    assert "unreachable" not in done.stdout
    assert not verdict.exists(), "a refused gate must not touch the verdict"

