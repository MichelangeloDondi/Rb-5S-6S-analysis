"""The shape of the front path, ratcheted: walls only shrink.

The reader-surface budget bounds VOLUME; a file can hold its budget and
be one paragraph. These axes bound SHAPE, measured the way the
attention-geometry review measured them (paragraphs split on blank
lines and on bare `>` quote-separators; code fences skipped): the
longest unbroken paragraph, and the words a reader crosses before the
first structural anchor (heading, table, list, or figure) after the
title block.

POPULATION: the files in the tuple below — the front-path pages a
five-minute reader meets, chosen by hand at introduction and extended
on review findings (the tuple is the count; prose stopped carrying
one after a review caught it stale). It overlaps the
reader-surface budget's population without equalling it (the budget bounds
volume on its own set; this bounds shape on this one). docs/methods/ is excluded BY RULE: a derivation is long because
it derives, and the review that priced these thresholds names that
exclusion as load-bearing. Baselines seed at today's measured values
and may only FALL; paying a wall down re-records with --reseed and a
--reason, which the shared history book refuses to go without.

Also here: the skim-rail debt counter -- tracked docs over 1,500 words
carrying no four-part header block (the house rail; a TOC requirement
was priced and REFUSED: zero exist and hand indexes rot). Seeded at
today's count, only falls.

Plant, verified at introduction: doubling one population file's worst
paragraph in a tmp copy fails its axis; splitting it passes.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_prose_shape_baseline.json")
BOOK = Path(__file__).with_name("_ratchet_history.md")

POPULATION = (
    "README.md", "START_HERE.md", "docs/BIG_PICTURE.md",
    "docs/RESULTS.md", "docs/CLAIMS.md", "docs/PLAN.md",
    "docs/UNCERTAINTY.md", "docs/big_picture/01_why-this-line.md",
    "docs/APPARATUS.md", "docs/DATA.md",
    # joined 2026-09-01 on a review finding: both are budget files a
    # five-minute reader meets, and both were unguarded while the first
    # docstring claimed the budget set was covered
    "docs/GLOSSARY.md", "docs/plan/00_the-case.md",
)
RAIL_MIN_WORDS = 1500
RAIL_EXCLUDE = ("docs/methods/", "docs/lit/", "docs/notes/",
                "docs/history/", "docs/apparatus/")
RAIL_BLOCK = "**Skip if.**"


def _paragraphs(text: str):
    out, cur, fence = [], [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        bare_quote = line.strip() == ">"
        if not line.strip() or bare_quote:
            if cur:
                out.append(" ".join(cur)); cur = []
        else:
            cur.append(line)
    if cur:
        out.append(" ".join(cur))
    return out


def _shape(text: str) -> dict:
    paras = _paragraphs(text)
    longest = max((len(p.split()) for p in paras), default=0)
    words_before, seen_title = 0, False
    anchor = re.compile(r"^(#{1,6} |\||[-*] |\d+\. |!\[|> )")
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if not seen_title and s.startswith("# "):
            seen_title = True
            continue
        if seen_title and anchor.match(s):
            break
        if seen_title:
            words_before += len(s.split())
    return {"longest_para": longest, "to_first_anchor": words_before}


def _counts() -> dict:
    return {rel: _shape((ROOT / rel).read_text(encoding="utf-8"))
            for rel in POPULATION if (ROOT / rel).is_file()}


def _rail_debt() -> list[str]:
    tracked = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*.md"],
        capture_output=True, text=True).stdout.split()
    out = []
    for rel in tracked:
        if any(rel.startswith(x) for x in RAIL_EXCLUDE):
            continue
        text = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        if len(text.split()) >= RAIL_MIN_WORDS and RAIL_BLOCK not in text:
            out.append(rel)
    return sorted(out)


def test_walls_only_shrink():
    base = json.loads(BASELINE.read_text())
    worse = []
    for rel, now in _counts().items():
        was = base["files"].get(rel)
        if was is None:
            worse.append(f"{rel}: NEW to the population, reseed with a reason")
            continue
        for axis in ("longest_para", "to_first_anchor"):
            if now[axis] > was[axis]:
                worse.append(f"{rel}: {axis} {was[axis]} -> {now[axis]}")
    assert not worse, (
        "the front path gained wall where it had less. Break the "
        "paragraph or lead with the anchor; a deliberate rise re-records "
        "with --reseed --reason:\n  " + "\n  ".join(worse))


def test_rail_debt_only_falls():
    base = json.loads(BASELINE.read_text())
    debt = _rail_debt()
    assert len(debt) <= base["rail_debt"], (
        f"files over {RAIL_MIN_WORDS} words without the header-block rail "
        f"rose {base['rail_debt']} -> {len(debt)}. Give the new one its "
        "block, or reseed with a reason:\n  " + "\n  ".join(debt))


def test_the_plant_fires_through_the_real_measurer(tmp_path):
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    paras = _paragraphs(text)
    worst = max(paras, key=lambda p: len(p.split()))
    doubled = text.replace(worst.split(" ", 1)[0],
                           worst + " " + worst.split(" ", 1)[0], 1)
    assert _shape(doubled)["longest_para"] > _shape(text)["longest_para"]


def test_the_history_book_rows_are_well_formed():
    rows = [ln for ln in BOOK.read_text().splitlines()
            if ln.startswith("| 20")]
    for ln in rows:
        assert len([c for c in ln.split("|") if c.strip()]) == 4, ln


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        i = sys.argv.index("--reason") if "--reason" in sys.argv else -1
        if i < 0 or i + 1 >= len(sys.argv):
            raise SystemExit("reseed refuses without --reason \"...\" "
                             "(the history book records it)")
        reason = sys.argv[i + 1]
        new = {"files": _counts(), "rail_debt": len(_rail_debt())}
        BASELINE.write_text(json.dumps(new, indent=1, sort_keys=True) + "\n")
        from datetime import date
        with BOOK.open("a") as fh:
            fh.write(f"| {date.today()} | prose_shape | reseed | "
                     f"{reason.replace(chr(124), chr(47))} |\n")
        print(f"reseeded over {len(new['files'])} files, "
              f"rail debt {new['rail_debt']}")
