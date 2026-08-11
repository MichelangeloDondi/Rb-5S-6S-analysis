"""A ratchet on two punctuation marks the house style does not use.

Why a ratchet and not a ban. The style rule is that where a sentence wants an
em-dash or a semicolon, it should end and the next should begin. The corpus
began with 3063 of them across 112 files, so a hard ban would have failed on
the first run and been switched off on the second. A guard that cannot pass is
not a guard.

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
    """Drop code fences, tables and display maths: only running prose counts.

    THE $$ FIX (2026-08-10). This used to skip only lines that START with $$,
    which drops the delimiters of a display block and keeps everything between
    them. A multi-line equation therefore had its interior counted as prose,
    and LaTeX argument separators were counted as semicolons: the composite
    line in methods/02 contributed four that no rewrite could remove without
    breaking the mathematics. $$ now toggles a mode the way ``` does, and a
    line carrying an odd number of them flips it.
    """
    kept, in_fence, in_math = [], False, False
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        n_delim = line.count("$$")
        if n_delim:
            # a line with one $$ opens or closes; with two it is a whole
            # one-line display and is dropped either way
            if n_delim % 2:
                in_math = not in_math
            continue
        if in_fence or in_math or stripped.startswith("|"):
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
    # Added 2026-08-10, owner instruction, after measuring all of them against
    # the tree. EVERY phrase below was already at zero, which is why they can
    # be banned outright at no cost. The measurement is the point: of
    # forty-nine candidates tested, thirty-seven were already absent, five were
    # genuine filler and were removed in the same pass, and the rest turned out
    # to be technical usage and were KEPT. Those keepers are named in the
    # rendering protocol section 2.3 with the reason, because a word list that
    # bans "leverage" in a project with a density lever, or "underscore" in a
    # project whose filenames turn on one, would be worse than no list.
    "delve",
    "deep dive",
    "dive into",
    "shed light on",
    "sheds light on",
    "pave the way",
    "paves the way",
    "unleash",
    "harness the",
    "game-changer",
    "game changer",
    "showcase",
    "boasts",
    "seamless",
    "tapestry",
    "ever-evolving",
    "a testament to",
    "highlights the importance",
    "navigate the complexities",
    "at its core",
    "key takeaway",
    "empower",
    "meticulous",
    "utilize",
    "utilise",
    "myriad",
    "plethora",
    "when it comes to",
    "in conclusion",
    "to summarize",
    "to summarise",
    "double-edged sword",
    "in the realm of",
    "cutting-edge",
    "in today's",
    "pivotal",
])
def test_filler_openers_stay_absent(phrase):
    """Phrases that announce importance instead of demonstrating it.

    These are at zero. Unlike the punctuation above they can be banned
    outright, so they are, before they get a foothold.
    """
    # docs/lit/ holds one note per paper and quotes published titles and
    # abstracts VERBATIM, so a phrase there is the source's word and not this
    # project's. Two of the phrases added on 2026-08-10 turned up only there,
    # in a paper title and in an abstract, which is what surfaced the gap:
    # tests/test_repo_hygiene.py has skipped that directory for this reason
    # since it was written, and this guard never learned to.
    hits = [rel for rel in _tracked_markdown()
            if not rel.startswith("docs/lit/") and (ROOT / rel).exists()
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
