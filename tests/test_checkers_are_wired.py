"""Every checker in this tree is called by something, or says why it is not.

WHY THIS EXISTS. On 2026-08-26 a commit landed whose best content was a
docstring recording that `scripts/annotate_results_status.py` had a
deliberate `KeyError` designed to fail closed on an unmapped results file,
and that it had FIRED FOR NOBODY, because nothing ever called it -- while
`bash scripts/run_all.sh`, the entry point a community adopter runs on their
own data and the first thing a successor runs, had been dying on the first
unmapped file for two days with every gate green over it.

Twenty-five lines away, the same commit added `private/checks/board_ledger.py`
and a new row in `private/checks/enforcement_report.py`. Nothing called
either. `ci_gate.sh` named neither, no hook named them, no test named them,
and `enforcement_report.py` -- the only caller `board_ledger` had -- was
itself called by nothing, so the whole chain was dead. Running the new
verifier by hand returned `0 of 1 commit(s) carry a recorded board verdict`
against its own enabling commit.

THE CLASS: a guard that nothing calls is not a guard, and the commit that
diagnosed the class instantiated it twice in its own diff. That is what a
guard for the class has to catch, so this file generalises the fix from one
script to every checker in the tree.

WHY AN ALLOWLIST RATHER THAN A RULE THAT EVERYTHING RUNS. Some checkers
genuinely cannot run per-commit, and the defensible ones say why. The outbound
carrier checks read untracked application drafts, so there is no committed
input for a gate to hold still and check. `anchor_drafts.py` takes a batch
file for one fan-out. `check_release_notes.py` checks a release body pasted
into a web form, which is by construction not a tracked file. Each of those
carries its reason here, at least twelve words of it, on the pattern
`scripts/verify_results_fresh.py`'s own `UNCOVERED` registry already uses:
a label is not a reason, and a reason is what a later reader needs in order
to disagree.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# BLIND REGION, stated because this guard's own motivation is a script that
# fired for nobody: the globs below are name-shaped, so a validator whose name
# does not start with check_ or verify_ and does not sit in private/checks/ is
# outside this guard's population entirely. scripts/annotate_results_status.py
# is exactly such a script and this guard does not see it.
#
# AND THE POPULATION IS A FILESYSTEM GLOB WHILE THE COMMIT TEAM READS A DIFF.
# `private/` became its own git repository on 2026-08-29, so the archive's
# history cannot see a file appear under private/checks/ at all: a checker
# added there is invisible to `git diff`, to `git ls-files`, and therefore to
# every seat reading a staged diff. This guard is the ONLY thing that notices,
# and it notices at collection time, not when a seat reads a diff. So the
# obligation sits here rather than in a seat's brief: adding a checker under
# private/checks/ means adding it to a caller or to NOT_WIRED in the SAME
# edit, because no seat downstream can be shown that it exists.
# Earned on 2026-08-29, when backup_governance.py was created and committed
# in a batch that edited this very dict to add its sibling, and the suite went
# red at HEAD for want of the entry below.
#
# checker path (relative to the repo root) -> why it is not wired
NOT_WIRED = {
    "private/check_carriers.py":
        "checks the outbound blocks of untracked application and outreach "
        "drafts before a send, so there is no committed input a per-commit "
        "gate could run it against",
    "private/check_freshness.py":
        "checks an outbound letter or brief against the live state of the "
        "record at the moment of sending, and the letter is never a tracked "
        "file, so there is nothing for the gate to hold still",
    "private/check_invariants.py":
        "cross-checks the untracked application drafts against each other, "
        "and which drafts are in flight changes between sessions, so its "
        "input set is not a property of any commit",
    "private/checks/reader_brief.py":
        "TRANSPORT, not a guard: it carries the rule text verbatim and each "
        "source's hash to a reader who did not do the work, and it decides "
        "nothing. There is no property for a gate to assert, because a brief "
        "cannot pass or fail -- what it produces is an input to a human "
        "judgement, and wiring it into the suite would be asserting that the "
        "reader read it, which no test can see. It is invoked by the convener "
        "when briefing the enforcement reader, per LOGIC 0b.2, and its own "
        "docstring says that if it ever returns a conclusion it has become "
        "the checker-of-the-checker the ceiling rule refuses",
    "private/checks/check_prose_numbers.py":
        "grades an UNTRACKED prose file -- the thesis chapter, the application "
        "drafts -- against the committed results CSVs, and which of those "
        "exists changes between sessions, so there is no committed input a "
        "per-commit gate could hold still. It also cannot pass or fail on its "
        "own: a hit can be coincidental and only the MISS list carries signal, "
        "so what it produces is an input to a human reading rather than an "
        "assertion. Wiring it would mean asserting that someone read the list",
    "private/checks/anchor_drafts.py":
        "a one-shot batch tool that takes a drafts file for one subagent "
        "fan-out and compares each drafted body against the file it claims "
        "to replace; a clean checkout has no such batch to feed it",
    "private/checks/protocol_changes.py":
        "counts content-hash changes to the untracked protocol files across "
        "sessions, so its ledger is machine state rather than tree state and "
        "a hermetic checkout would make its count meaningless",
    "private/checks/governance_msa.py":
        "measures the board's own discrimination from the ledger and is read "
        "at audits, not at commits: its output is a judgement about whether "
        "the seats are worth their cost, which no gate should act on "
        "automatically. Wiring it would make a governance metric into a "
        "commit blocker, which is the Goodhart move this record refuses",
    "private/checks/backup_governance.py":
        "an operator-run backup, not a gate step: it writes a bundle and an "
        "archive to iCloud, which is a side effect on a path outside both "
        "repositories, and a gate that wrote to the operator's cloud storage "
        "on every commit would be doing something no commit asked for. Its "
        "own --check mode reports the artefacts' ages and is what an audit "
        "runs. THE FALSE PASS THIS LEAVES OPEN: nothing fails when the backup "
        "goes stale, so an age reported in a session nobody read is the same "
        "as no backup at all",
}
# scripts/check_release_notes.py left NOT_WIRED on 2026-08-28:
# tests/test_release_note_checker.py now exercises it against planted bodies
# in both directions, so the recorded reason (nothing can reach it) went
# false the day the release drill gained step D5 and the plant became a test.
# THE FALSE PASS THIS DOES NOT CLOSE: the test feeds it synthetic bodies, so
# a defective REAL note still ships if nobody runs the drill's D5 step --
# wiring here proves the checker works, not that a release used it.

# Places a checker may be called from. A checker named in any of these is
# wired; run_all.sh counts because a producer that dies takes the pipeline
# with it, which is exactly how the annotator's failure was found.
CALLER_GLOBS = ("scripts/ci_gate.sh", "scripts/run_all.sh",
                "tests/*.py", ".github/workflows/*.yml",
                ".github/workflows/*.yaml")

# A deliberate frozen snapshot of a past mirror state, not a tool anyone
# runs; tests/test_no_shadowed_script_names.py documents it as such.
EXCLUDED_DIRS = ("private/mirror_stash_",)


def _checkers() -> list[str]:
    found = []
    for pat in ("private/checks/*.py", "private/check_*.py",
                "scripts/check_*.py", "scripts/verify_*.py"):
        for p in sorted(ROOT.glob(pat)):
            rel = p.relative_to(ROOT).as_posix()
            if p.name == "__init__.py" or rel.startswith(EXCLUDED_DIRS):
                continue
            found.append(rel)
    return found


# A NAME IS NOT A CALL, AND A LINE IS NOT A STATEMENT. This guard shipped
# two drafts with two defects, both of them classes this repository already
# names. The first matched the filename anywhere in a caller file, so the six
# entries in NOT_WIRED above -- named in this very dict -- were reported as
# wired, by this file, about itself. The second matched only lines carrying
# an invocation token, and missed `scripts/check_references.py`, which
# tests/test_references.py genuinely calls with the path on a DIFFERENT LINE
# from the `subprocess` that runs it. That is the wrapped-phrase class: a
# guard that reads one line at a time cannot see a statement that spans two.
#
# So: strip the prose, keep the code, and match against the whole of it.
# Comments and docstrings are where a filename gets MENTIONED; string
# literals and shell words are where it gets RUN.
def _code_text(p: Path) -> str:
    if p.suffix == ".py":
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="ignore"))
        except (SyntaxError, OSError):
            return ""
        docs = set()
        for node in ast.walk(tree):
            if not isinstance(node, (ast.Module, ast.FunctionDef,
                                     ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            body = getattr(node, "body", None)
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                docs.add(id(body[0].value))
        return "\n".join(
            n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in docs)
    try:
        text = p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    return "\n".join(ln for ln in text.splitlines()
                     if not ln.lstrip().startswith("#"))


def _caller_sources() -> list[tuple[Path, str]]:
    here = Path(__file__).resolve()
    paths = []
    for pat in CALLER_GLOBS:
        paths.extend(sorted(ROOT.glob(pat)))
    hooks = ROOT / ".git" / "hooks"
    if hooks.is_dir():
        paths.extend(p for p in sorted(hooks.iterdir())
                     if p.is_file() and not p.name.endswith(".sample"))
    out = []
    for p in paths:
        if p.resolve() == here:
            continue
        try:
            raw = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        out.append((p, _code_text(p), raw))
    return out


# A python file that never runs a subprocess is not calling a checker, it is
# talking about one. Shell and workflow files run things by naming them.
#
# THE RUNNER IS LOOKED UP IN THE RAW SOURCE AND THE NAME IN THE STRIPPED
# CODE, and they are different texts on purpose. `subprocess` is an
# IDENTIFIER, which does not survive a strip that keeps only string literals;
# the checker's filename is a string literal, which is exactly what that
# strip keeps. A first draft looked for both in the stripped text and
# reported `scripts/check_references.py` unwired while
# tests/test_references.py was running it.
_RUNNERS = ("subprocess", "runpy", "importlib", "os.system")


def _is_called(rel: str, sources) -> bool:
    name = Path(rel).name
    for p, code, raw in sources:
        if name not in code and rel not in code:
            continue
        if p.suffix == ".py" and not any(r in raw for r in _RUNNERS):
            continue
        return True
    return False


def test_every_checker_is_called_by_something_or_says_why_not():
    sources = _caller_sources()
    orphans = []
    for rel in _checkers():
        if _is_called(rel, sources) or rel in NOT_WIRED:
            continue
        orphans.append(rel)
    assert not orphans, (
        "these checkers are called by nothing -- not the gate, not a hook, "
        "not a test, not run_all.sh, not a workflow. A guard that nothing "
        "calls is not a guard; it is a file that looks like one. Wire it, "
        "or add it to NOT_WIRED above with a reason a later reader could "
        "disagree with:\n  " + "\n  ".join(orphans))


def test_the_allowlist_names_real_files_and_gives_real_reasons():
    """A stale allowlist is how this guard would quietly stop measuring."""
    bad = []
    for rel, reason in NOT_WIRED.items():
        if not (ROOT / rel).is_file():
            # private/ is absent in every clone but the archive, and its
            # entries are correctly invisible there rather than wrong.
            if rel.startswith("private/") and not (ROOT / "private").is_dir():
                continue
            bad.append(f"{rel}: no such file")
        elif len(reason.split()) < 12:
            bad.append(f"{rel}: reason is {len(reason.split())} words, "
                       f"which is a label and not a reason")
    assert not bad, "\n  ".join(bad)


def test_the_allowlist_does_not_excuse_a_checker_that_is_wired():
    """If a listed checker gets wired, the excuse must go, or it misleads."""
    sources = _caller_sources()
    stale = [rel for rel in NOT_WIRED
             if (ROOT / rel).is_file() and _is_called(rel, sources)]
    assert not stale, (
        "these are in NOT_WIRED but something now calls them, so the "
        "recorded reason is false and a reader would trust it:\n  "
        + "\n  ".join(stale))


def test_the_two_that_earned_this_file_are_wired():
    """The regression test proper: these are why the file exists."""
    if not (ROOT / "private" / "checks").is_dir():
        return  # not the archive; nothing to assert
    # NAMED IN THE GATE SPECIFICALLY, not merely somewhere a subprocess runs.
    # A ceiling test caught this: with board_ledger.py removed from
    # ci_gate.sh, this assertion still passed, because tests/test_board_ledger.py
    # imports the module and so counted as a caller. That is a fair reading of
    # "wired" in general and the wrong reading here -- a unit test exercising
    # a checker's functions is not the gate refusing a push over it.
    gate = (ROOT / "scripts" / "ci_gate.sh").read_text(encoding="utf-8")
    for name in ("board_ledger.py", "enforcement_report.py",
                 "protocol_citations.py"):
        assert name in gate, (
            f"{name} is not called by anything again. This file exists "
            f"because it was shipped unwired once, in the same commit that "
            f"diagnosed unwired guards as a failure class.")
