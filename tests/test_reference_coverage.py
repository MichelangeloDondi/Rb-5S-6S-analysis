"""Unreferenced decimal claims per file fall and never rise.

The resolver in test_references.py checks the references that exist. This
ratchet is about the ones that do not: a decimal number in prose with no
inline reference is a claim the anti-staleness machinery cannot protect,
exactly the class that produced the retracted band digits and the four
public figures with no producer. It cannot be banned outright, because a
date, a version and a section number are numbers too, so it takes the
falling-baseline shape every debt here takes: seeded at the measured
counts, allowed down, never up.

THE MEASURE, stated so its blind region is on record: decimal tokens
(digits, a point, digits) in prose, after code spans, fenced blocks, math,
link targets, URLs and file paths are stripped, excluding tokens already
inside a reference link's text. Integers are not counted, which spares
dates and counts and misses integer-valued claims; a paraphrase carries no
token at all. Both misses are recorded in the design note rather than
discovered later.

2026-08-28, a SECOND re-seed the same day, and the first one was wrong in the
direction that matters. README.md was re-seeded UPWARD, 62 to 68, describing a
state of the file that no longer existed: the same commit cut the page from
6,101 words to 1,339 and its real count is 10. The seed was left 6.8 times
looser than the tree, which is 58 unreferenced decimals of silent headroom on
the one page a reader meets first.

A ratchet seeded above reality has stopped ratcheting. It is now seeded at the
measured counts, and `test_the_baseline_is_not_looser_than_reality` below makes
the failure impossible to repeat, which is the test both sibling ratchets
written the same night already carried and this one did not.

2026-08-28, a third time and a FALL, caught by the anti-slack test added six
hours earlier in this same file. The board of record found that methods/09
cited fibre_twin.csv at coverage values the transit-kernel correction in
this same wave had already replaced. Referencing the four of them properly, instead of
restating them, took the chapter below its seed and the new test refused the
slack. That is the guard doing on its first working day exactly what it was
written for.


RE-SEEDED 2026-08-29, and the reason each file moved. `docs/history/09` rose because a correction entry landed and a history table's `was` column names values with no live row to cite. `docs/big_picture/09` rose because the fibre payback gained the operating point it was quoted without, which is three derived numbers. `docs/notes/onf_candidate.md` rose by one, the spectroscopy power a board found stated ten times too high. `docs/big_picture/06` FELL, from a drafting narrative cut out of a reader table. RE-SEEDED AGAIN THE SAME DAY, after a release board found the CSV retracting a claim five prose surfaces still asserted: `docs/notes/onf_candidate.md` rose 47 to 48 when the atom-surface term was propagated into that page's budget equation. The two shift values it quotes carry `ref:` tags; the committed 3.49 MHz natural width beside them is stated rather than cited, and that is the decimal that moved.

RE-SEEDED 2026-09-12. `docs/RESULTS.md` fell 316 to 315 and `docs/THEORY_NOTE.md` 114 to 113: the deep polarizability derivation's value, its uncertainty, its 9P-and-above group and its static-tail pull are quoted on both pages as `ref:` tags to `results/polarizability_deep.csv`, and on RESULTS the bullet lives inside the generator so a regeneration keeps the tags.
RE-SEEDED AGAIN THE SAME NIGHT after the board's fix pass: `docs/plan/12_open-apparatus-items.md` 151 to 153 and `docs/wiki/identifiability.md` 111 to 113, the attenuator's cost stated as two factors, 1.9 and 1.3, which are the record's own ratio law from methods/03 at one half and which no cell carries.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# THE RE-SEED LOG LIVES HERE AND IT IS NOT THE PROJECT'S HISTORY.
# LANGUAGE 19.16a confines history to one file, and a reader was right
# that this preamble had grown into a second one: it reached 1,393 words of
# dated entries. A re-seed's REASON has to sit where the re-seed happens, or
# the ratchet stops being legible, so the recent reasons stay. The older ones
# are compressed to their outcome, and the full account of every move is the
# git history of _reference_coverage_baseline.json, which is the primary.
#
# Moves before 2026-08-29, in one line each: README re-seeded UPWARD once and
# left 6.8x looser than the tree, which is a ratchet that has stopped
# ratcheting and is why test_the_baseline_is_not_looser_than_reality exists;
# methods/09 entered at its full count as a new chapter; several chapters rose
# as corrections added figures no committed row holds; onf_candidate fell twice
# as typed values became citations. The ordinals in those entries reused
# TENTH and ELEVENTH for two dates each, which is why entries are dated now.

# Re-seeded 2026-08-29, after the final board. Two entries moved and both fell:
#   docs/history/09 30 -> 28, because the lever table's two hand-typed values
#   (30.6 where the CSV says 30.7, and 186 per cent where 1.851 is 185.1) now
#   carry ref: tags, so they leave the undeclared set and can no longer drift.
#   docs/methods/09 47 -> 45, because a dated correction narrative moved to a
#   citation of the history chapter, which is where LANGUAGE 19.16a puts it.
# Both are the ratchet's intended traffic: a typed value became a citation.
#
# Re-seeded 2026-08-29, late. Exactly one entry moved and it fell:
#   docs/history/09_the-guided-geometry.md 36 -> 30. Its new hot-transit entry
#   ran 318 words and H3 caps an entry at 150, so it was cut to the four facts
#   the rule names: the quantity, what it was, what it is now with its file,
#   and the cause in one clause. Six undeclared decimals left with the
#   reasoning. **The reasoning did not vanish**: the producer comment carries
#   why the two errors cancel, and the plan carries the lesson. That is H3's
#   own division of labour, and the fall is what obeying it looks like.
# Diffed entry by entry against the previous baseline before this was written.
#
# Re-seeded 2026-08-29, earlier the same day, and both moves are FALLS, which is
# the direction this ratchet exists to allow. Diffed against the previous
# baseline entry by entry before the reason was written, which is what the
# operational lesson below demands and what the sixth re-seed did not do:
#   docs/big_picture/06_next-nanofibre.md 24 -> 21. Its mode table carried
#   three effective indices and three decay lengths as bare numbers; the
#   three decimals now carry ref: tags into results/guided_mode_tables.csv,
#   so they leave the undeclared set. The integers were never in it.
#   docs/methods/09_the_guided_geometry.md 47 -> 46. One bare 0.156, ten
#   lines from its own tagged twin in the table below it, now carries the
#   tag as well.
# Exactly two entries moved and no entry rose. That matters more than usual
# here, because the run that found these falls also found that a guard's
# blind region is what a board cannot see: the tag is the only mechanism in
# this tree that catches a number which never matched its cell, so widening
# the tagged set is the counter, and this ratchet is how the widening is
# measured.
#
# Re-seeded 2026-08-29, first of the day, and THE ACCOUNT WRITTEN HERE FOR IT
# WAS WRONG. It said docs/history/09_the-guided-geometry.md rose 24 to 25
# "from the entry recording that the fused-silica index carried the 852 nm
# value". A seat re-ran this module's own strip-and-count over that file at
# the base, at the mode-solve commit and at HEAD, and got 25 at all three:
# FLAT, not a rise. The cited sentence is byte-identical across the range and
# contributes zero decimal tokens anyway, because its figures sit inside
# backticks and the strip pattern removes them.
#
# THE OPERATIONAL LESSON, and it is the reason this is written down rather
# than fixed silently: a blanket re-seed accepts every rise in one command,
# and the convention that a re-seed carries its dated reason does not say
# "the ones you noticed". Diff the baseline against HEAD after re-seeding
# and account for every entry that rose.

BASELINE = Path(__file__).with_name("_reference_coverage_baseline.json")

_STRIP = re.compile(
    r"```.*?```|`[^`]*`|\$\$.*?\$\$|\$[^$\n]*\$"
    r"|\[(?P<t>[^\]]+)\]\(\s*[^)\s]+\s+\"ref:[^\"]+\"\s*\)"  # referenced
    r"|\]\([^)]*\)|https?://\S+"
    r"|\b[\w/.-]+\.(?:md|csv|py|png|jpg|jpeg|json|sh|txt|pdf|yml|toml)\b"
    r"|^\s{4,}\S[^\n]*$",
    re.S | re.M)
_DECIMAL = re.compile(r"\b\d+\.\d+(?:[eE][+-]?\d+)?\b")
"""A decimal in prose, INCLUDING scientific notation.

THE EXPONENT FORM JOINED 2026-09-06, and its absence was a real hole. A
word boundary does not exist between the `9` and the `e` of `2.9e7`, both
being word characters, so the old pattern matched nothing at all in
`2.9e7`, `8.1e6` or `3.5e8`. A check found `docs/plan/12` gaining two
headline ceiling figures in that form while its unreferenced-decimal count
did not move: the ratchet reported compliance because it could not see
them. The docstring recorded a blind region and exponent notation was not
in it, which is how the gap survived a reading of this file.
"""


def _tracked_markdown() -> list[str]:
    # THE REGISTRIES ARE CLAIM SURFACES TOO. results/README.md and
    # scripts/README.md carry a row per file with the file's headline numbers,
    # and both sat outside this population until a stale value survived a fix
    # pass there on 2026-09-07; the count ratchet licenses no growth of untagged
    # decimals, and a stale value is caught only by a tag.
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files",
                          "docs/*.md", "README.md", "results/README.md", "scripts/README.md"],
                         capture_output=True, text=True)
    return out.stdout.split()


def _counts() -> dict[str, int]:
    # Re-seeded 2026-09-01, wave F's prose unit, instrument output pasted
    # Re-seeded 2026-09-01 again in the same unit, instrument output pasted:
    #   docs/methods/07_what_we_found.md: 77 -> 70
    #   docs/plan/07_acquisition-settings.md: 228 -> 227
    # THE FIRST ACCOUNT OF THIS MOVEMENT WAS FALSE IN BOTH CLAUSES (the
    # class's eighth instance, caught by a reading): it said "tightening"
    # and "merged a duplicate". Measured, the fall is seven values
    # entering the methods chapter's own math-mode convention, whose
    # spans this counter strips BY DESIGN. One further wrap in the
    # plan had
    # no such convention and was undone the same day. No duplicate ever
    # existed.
    # Re-seeded 2026-09-01 once more for that undoing, instrument output
    # pasted:
    #   docs/plan/07_acquisition-settings.md: 227 -> 228
    # The bare value re-entered the counted set (the
    # first draft of the clause above composed the pair as 228 -> 228
    # and was corrected from the instrument's print before staging).
    # (this date first said 09-02, composed from the operator clock while
    # the instrument row says 09-01 -- the class's seventh instance, and
    # the guard below now reads the book so a composed DATE cannot ship
    # again):
    #   docs/methods/07_what_we_found.md: 67 -> 77
    #   docs/plan/07_acquisition-settings.md: 227 -> 228
    # The rises are the sign test's producer values quoted beside their
    # power_time_sign_test.csv links (the documented rise class); each
    # decimal resolves to a row of that CSV.
    # Re-seeded 2026-09-01, prose-ratchet v2, instrument output pasted:
    #   docs/BIG_PICTURE.md: 34 -> 24
    # The duplicated 45-line identifiability block in the hub became a
    # four-line pointer into chapter 7, and the ten counted references
    # inside it now stand once, in the chapter. A fall by deletion of a
    # duplicate, nothing relaxed.
    # Re-seeded 2026-09-01, the sobol wave, terminal movement:
    #   docs/plan/07_acquisition-settings.md: 245 -> 233
    # as the board's anchor findings landed -- the table's ten error
    # values, the floor exponent's pair, the interaction pair and the
    # section-6 totals gained inline references: twelve unreferenced
    # decimal claims left the page. A fall, nothing relaxed. (This entry
    # was first written one round late FROM MEMORY, said 246 -> 245 -> 233
    # with thirteen and eleven, and was corrected by the final round --
    # the class's sixth instance; the reseed-log guard that ends it by
    # instrument is queued to wave F.) Re-seeded again 2026-09-01 in the same fix pass, movement
    # pasted from the instrument:
    #   docs/plan/07_acquisition-settings.md: 233 -> 230
    # the correction clause's transient decimals (B5) removed. A fall.
    # Re-seeded once more 2026-09-01 (the 19.16a repair of the same
    # clause), movement pasted from the instrument:
    #   docs/plan/07_acquisition-settings.md: 230 -> 227
    # the retired hand-typed digits left the clause. A fall. (This
    # line first said 228, written in the same command as the reseed,
    # BEFORE its output existed -- the fifth recurrence of the class,
    # caught by reading the instrument after. The rule that survives:
    # the note is written in a separate step after the output prints,
    # never alongside the command that produces it.)
    # Re-seeded 2026-08-31 across the board-2 fix wave. Measured against
    # HEAD, every moved key (the two blocks this replaces described the
    # movement from intention and got both the direction and the
    # contributors wrong, which a reading caught by computing exactly
    # this list):
    #   docs/history/02_the-lineshape-and-its-kernel.md: 36 -> 38
    #   docs/methods.md: 3 -> 4
    #   docs/methods/03_the_ac_stark_ramp.md: 35 -> 37
    #   docs/methods/06_the_statistics.md: 64 -> 80
    #   docs/wiki/third-cumulant.md: 4 -> 8
    # Every risen count is a dated decimal of the cumulant episode or a
    # section cross-reference matching the token pattern; each resolves to a
    # row of cumulant_window_check.csv, fit_window_scan.csv or
    # estimator_duel.csv, or to a section anchor.
    #
    # Re-seeded again later the same day; movement pasted from the tool:
    #   docs/UNCERTAINTY.md: 30 -> 31
    #   docs/methods/03_the_ac_stark_ramp.md: 36 -> 35
    #   docs/wiki/third-cumulant.md: 11 -> 12
    # The two rises are converged producer values quoted beside their CSV
    # links in the same edits; the fall is the de-spliced remark in 03.
    #
    counts: dict[str, int] = {}
    for rel in _tracked_markdown():
        path = ROOT / rel
        if not path.exists() or rel.startswith("docs/lit/"):
            continue
        text = _STRIP.sub(" ", path.read_text(encoding="utf-8"))
        n = len(_DECIMAL.findall(text))
        counts[rel] = n                  # a zero is recorded, as every counter does since 2026-09-08
    return counts


def test_unreferenced_decimals_only_fall():
    current = _counts()
    baseline = json.loads(BASELINE.read_text())
    grew = {k: (baseline.get(k, 0), v) for k, v in current.items()
            if v > baseline.get(k, 0)}
    assert not grew, (
        "files gained unreferenced decimal claims. Either add an inline "
        "reference to the source (the design note has the syntax) or, "
        "after confirming the additions are legitimate, re-seed with "
        "python tests/test_reference_coverage.py --reseed:\n  "
        + "\n  ".join(f"{k}: {a} -> {b}" for k, (a, b) in sorted(grew.items())))


def _print_movement(old: dict, new: dict) -> None:
    """Emit the measured per-key movement of a baseline write and say whether
    anything moved; a key on one side only prints ADDED or REMOVED (the
    prose-style twin carries the same contract)."""
    moved = []
    for k in sorted(set(old) | set(new)):
        if old.get(k) == new.get(k):
            continue
        a = "ADDED" if k not in old else old[k]
        b = "REMOVED" if k not in new else new[k]
        moved.append(f"  {k}: {a} -> {b}")
    print("movement (paste this into the dated note):")
    print("\n".join(moved) if moved else "  (no key moved)")


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        _ri = sys.argv.index("--reason") if "--reason" in sys.argv else -1
        if _ri < 0 or _ri + 1 >= len(sys.argv):
            raise SystemExit("reseed refuses without --reason (the "
                             "ratchet history book records it)")
        new = _counts()
        _old_total = sum(json.loads(BASELINE.read_text()).values()) \
            if BASELINE.exists() else 0
        _old_map = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
        old = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}
        if _old_map == new:
            print("  (no key moved, no row written)")
            raise SystemExit(0)
        # THE BASELINE IS WRITTEN BY `record`, after its refusals (E43).
        # A write that dies still leaves no row, which is what the comment here
        # used to defend; what it missed is that a REFUSAL is not a dying write.
        from _ratchet_book import record as _record
        _record("reference_coverage",
                f"reseed {_old_total} -> {sum(new.values())}",
                _old_map, new, sys.argv[_ri + 1],
                commit=lambda: BASELINE.write_text(
                    json.dumps(new, indent=1, sort_keys=True) + "\n"))
        print(f"reseeded {BASELINE.name} over {len(new)} files")
        _print_movement(old, new)


def test_the_baseline_is_not_looser_than_reality():
    """A seed above the real count is headroom, and headroom is not a ratchet.

    Its two siblings, the reader-surface budget and the uncertainty gap, have
    carried this check since they were written. This one did not, and on
    2026-08-28 it let README.md sit at a seed of 68 against a real count of 10
    after the page was cut by four fifths. The guard reported green over the
    whole of that gap.
    """
    seeded = json.loads(BASELINE.read_text())
    now = _counts()
    slack = {f: (seeded[f], now[f]) for f in now
             if f in seeded and now[f] < seeded[f]}
    assert not slack, (
        "the baseline is looser than the tree for "
        f"{len(slack)} file(s), so the ratchet has stopped falling: "
        + ", ".join(f"{f} seeded {a} actual {b}" for f, (a, b) in
                    sorted(slack.items())[:6])
        + ".\n  Re-seed with python tests/test_reference_coverage.py --reseed "
          "and say in the docstring why each fell.")


def test_reseed_notes_match_the_book():
    """Every dated reseed note in this module's own account has a book row.

    The composed-note class shipped eight times through this docstring:
    a date or a number or an account written beside instrument output
    rather than derived from it. This guard covers the DATE face only.
    FALSE-PASS DIRECTION, stated first: with no reference_coverage rows
    in the book the epoch floor grandfathers everything and the guard
    passes on an empty population. The instrument writes tests/_ratchet_history.md
    itself, so the book is the ground truth this note is graded
    against: each "Re-seeded <date>" line here must name a date on
    which the book holds a reference_coverage row. The seventh
    instance (a tomorrow-date composed from the operator clock) is the
    plant this guard was verified against at introduction.
    """
    import re
    here = Path(__file__).read_text(encoding="utf-8")
    noted = set(re.findall(r"Re-seeded (\d{4}-\d{2}-\d{2})", here))
    book = Path(__file__).with_name("_ratchet_history.md").read_text(
        encoding="utf-8")
    booked = {m.group(1) for m in re.finditer(
        r"^\| (\d{4}-\d{2}-\d{2}) \| reference_coverage \|", book,
        re.M)}
    # notes older than the book itself predate the instrument's ledger
    # (the book began 2026-09-01) and are grandfathered: the guard grades
    # only dates the instrument could have written
    epoch = min(booked) if booked else "9999-99-99"
    orphans = sorted(d for d in noted - booked if d >= epoch)
    assert not orphans, (
        "reseed notes dated with no matching book row (a composed date "
        "beside pasted numbers is this class's signature): "
        + ", ".join(orphans))

