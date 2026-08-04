"""A ratchet on the prose tics that make writing read as machine-drafted.

Why a ratchet and not a ban. The house style forbids em-dashes and semicolons
in prose: where a sentence wants one, it should end and the next should begin.
But the repository has 3063 of them across 112 files, accumulated over months
of AI-assisted drafting, and a hard ban would fail on day one and be disabled
by day two. A guard that cannot pass is not a guard.

So this records a per-file budget and fails only when a file gets WORSE. Every
cleanup pass lowers a number and locks the gain in. The budget can only fall,
never rise, which is the whole point: it makes the repository monotonically
more readable without demanding one enormous rewrite first.

Lowering the numbers is the work, not a chore to be automated around. Run
`python tests/test_prose_style_ratchet.py --relax` after a genuine cleanup to
re-record the improved counts. Raising a budget by hand means admitting that a
file got worse, which should feel like what it is.

Scope. Tracked Markdown only. Generated files are excluded because their prose
lives in the generator, so editing the output is pointless; fix the generator
and the output follows. Code fences, tables and display maths are stripped
before counting, because a semicolon in a code sample is not a style problem.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).parent / "_style_baseline.json"

# Generated: their prose lives in the generators, not in the output.
#
# docs/RESULTS.md left this set on 2026-08-04. Being exempt meant the guard
# could not see the ledger at all, and the ledger is the second link on the
# README's first screen. Its generator now writes prose without either mark,
# so the file is held to the same budget as every hand-written document. The
# other two stay exempt until their generators get the same pass.
GENERATED = {
    "docs/LITERATURE_INDEX.md",
    "PDF_papers/README.md",
}


def _tracked_markdown() -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return sorted(f for f in out if f not in GENERATED)


def _prose(text: str) -> str:
    """Drop code fences, tables and display maths: only running prose counts."""
    kept, in_fence = [], False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("|") or stripped.startswith("$$"):
            continue
        kept.append(line)
    return "\n".join(kept)


def _count(path: Path) -> int:
    prose = _prose(path.read_text(encoding="utf-8"))
    return prose.count("—") + prose.count(";")


def _current() -> dict[str, int]:
    counts = {}
    for rel in _tracked_markdown():
        p = ROOT / rel
        if not p.exists():          # staged deletion
            continue
        n = _count(p)
        if n:
            counts[rel] = n
    return counts


def test_no_file_gains_splice_punctuation():
    """Em-dash and semicolon counts may fall or hold, never rise."""
    baseline = json.loads(BASELINE.read_text())
    current = _current()

    worse = []
    for rel, now in sorted(current.items()):
        was = baseline.get(rel)
        if was is None:
            worse.append(f"{rel}: NEW file with {now} (write it without them, "
                         f"or add it to the baseline with --relax)")
        elif now > was:
            worse.append(f"{rel}: {was} -> {now} (+{now - was})")

    assert not worse, (
        "prose style regressed. The house rule is no em-dashes and no "
        "semicolons in prose: end the sentence instead.\n  "
        + "\n  ".join(worse)
        + "\n\nIf a cleanup pass genuinely lowered other files, re-record with:"
          "\n  python tests/test_prose_style_ratchet.py --relax")


def test_the_baseline_itself_only_ever_shrinks():
    """The recorded budget must not drift above what the files actually need.

    Without this, --relax could be run on a dirty tree and silently bless a
    regression. Here the baseline is required to be tight: no entry may sit
    above its file's real count.
    """
    baseline = json.loads(BASELINE.read_text())
    current = _current()
    slack = {rel: (was, current.get(rel, 0))
             for rel, was in baseline.items() if was > current.get(rel, 0)}
    assert not slack, (
        "the baseline is looser than reality, which leaves room for silent "
        "regressions. Re-record it:\n  "
        + "\n  ".join(f"{r}: budget {w}, actual {c}" for r, (w, c) in sorted(slack.items()))
        + "\n  python tests/test_prose_style_ratchet.py --relax")


@pytest.mark.parametrize("phrase", [
    "it is worth noting",
    "it should be noted",
    "crucially,",
    "importantly,",
    "needless to say",
    "at the end of the day",
])
def test_filler_openers_stay_absent(phrase):
    """Phrases that announce importance instead of demonstrating it.

    These are at zero. Unlike the punctuation above they can be banned
    outright, so they are, before they get a foothold.
    """
    hits = [rel for rel in _tracked_markdown()
            if (ROOT / rel).exists()
            and phrase in (ROOT / rel).read_text(encoding="utf-8").lower()]
    assert not hits, f"{phrase!r} appears in: {', '.join(hits)}"


if __name__ == "__main__":  # `python tests/test_prose_style_ratchet.py --relax`
    import sys
    if "--relax" in sys.argv:
        cur = _current()
        old = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
        BASELINE.write_text(json.dumps(cur, indent=1, sort_keys=True) + "\n")
        before, after = sum(old.values()), sum(cur.values())
        print(f"baseline re-recorded: {before} -> {after} ({after - before:+d})")
    else:
        print(f"total splice punctuation in prose: {sum(_current().values())}")
