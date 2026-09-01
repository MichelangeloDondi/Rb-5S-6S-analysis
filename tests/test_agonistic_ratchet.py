"""The agonistic register's soft tier, ratcheted per file: counts only fall.

The hard tier (war, victory, battle, fought; defeat/game/won in markdown)
is a zero-population ban in test_repo_hygiene. This half covers the words
with a real live population — win, lose, waste, play, defeat in code — where
a ban would demand a hundred rewordings in one wave and a bare count would
drift back up. So each file's count is a frozen ceiling: the waves that
touch a file pay its debt down, and a rise anywhere fails that file by
name. EXCLUDED AS PHYSICS TERMS OF ART, priced at introduction: loss/losses
(optical, transmission, insertion loss) and beat/beats/beaten (heterodyne
beat notes) — a ratchet that counts the physics vocabulary would punish
writing about the apparatus.

Reseeding (a deliberate rise, or a population change) runs this file with
--reseed --reason "..."; the reason lands as a dated row in the shared
ratchet history book, which refuses to go without one.

Plant, verified at introduction: appending one 'wins' to a counted file's
text in memory raises its count through the real measurer.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_agonistic_baseline.json")
BOOK = Path(__file__).with_name("_ratchet_history.md")

WORDS = re.compile(
    r"\b(?:win|wins|winning|winners?|lose|loses|losing|"
    r"waste|wasted|wasteful|wasting|plays?|played|playing|"
    r"defeat(?:s|ed|ing)?)\b", re.I)

SKIP = ("docs/lit/",)
SKIP_EXACT = {"docs/STYLE.md", "tests/test_repo_hygiene.py",
              "tests/test_agonistic_ratchet.py",
              "tests/test_board_ledger.py"}


def _counts() -> dict[str, int]:
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.md", "*.py"],
        capture_output=True, text=True).stdout.split()
    out = {}
    for rel in tracked:
        if rel.startswith(SKIP) or rel in SKIP_EXACT:
            continue
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        n = len(WORDS.findall(text))
        if n:
            out[rel] = n
    return out


def test_agonistic_counts_only_fall():
    base = json.loads(BASELINE.read_text())["files"]
    worse = []
    for rel, n in _counts().items():
        was = base.get(rel, 0)
        if n > was:
            worse.append(f"{rel}: {was} -> {n}")
    assert not worse, (
        "the agonistic count rose where it was frozen. Reword (prevails, "
        "governs, is taken, misses nothing, drop lock, cost), or reseed "
        "with a reason the history book records:\n  " + "\n  ".join(worse))


def test_the_plant_fires_through_the_real_measurer():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert len(WORDS.findall(text + " wins")) == len(WORDS.findall(text)) + 1


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        i = sys.argv.index("--reason") if "--reason" in sys.argv else -1
        if i < 0 or i + 1 >= len(sys.argv):
            raise SystemExit('reseed refuses without --reason "..." '
                             "(the history book records it)")
        reason = sys.argv[i + 1]
        new = {"files": _counts()}
        BASELINE.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
        from datetime import date
        with BOOK.open("a") as fh:
            fh.write(f"| {date.today()} | agonistic | reseed | "
                     f"{reason.replace(chr(124), chr(47))} |\n")
        print(f"reseeded over {len(new['files'])} files, "
              f"total {sum(new['files'].values())}")
