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
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = Path(__file__).with_name("_reference_coverage_baseline.json")

_STRIP = re.compile(
    r"```.*?```|`[^`]*`|\$\$.*?\$\$|\$[^$\n]*\$"
    r"|\[(?P<t>[^\]]+)\]\(\s*[^)\s]+\s+\"ref:[^\"]+\"\s*\)"  # referenced
    r"|\]\([^)]*\)|https?://\S+"
    r"|\b[\w/.-]+\.(?:md|csv|py|png|jpg|jpeg|json|sh|txt|pdf|yml|toml)\b"
    r"|^\s{4,}\S[^\n]*$",
    re.S | re.M)
_DECIMAL = re.compile(r"\b\d+\.\d+\b")


def _tracked_markdown() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files",
                          "docs/*.md", "README.md"],
                         capture_output=True, text=True)
    return out.stdout.split()


def _counts() -> dict[str, int]:
    # Re-seeded 2026-08-25 for ONE decimal: docs/ADAPTING.md's units
    # section illustrates the metres-for-nanometres trap with "microns
    # give 0.99". That is a pedagogical example of a WRONG input, not a
    # claim about the apparatus, so it has no source to reference and
    # referencing it would be false. Recorded here because a re-seed
    # without its reason is how a falling ratchet stops falling.
    #
    # Re-seeded again for the wiki figure captions, and the re-seed is
    # only recorded because the guard EARNED it. Seven pages gained one
    # decimal each, every one of them in a caption under a new figure.
    # Each was resolved to its source before the seed moved: 2.405 is the
    # first zero of J0; 993.4192 nm, 5.41 MHz, 11.86 bits, leverage 0.94
    # and the factor 3.2 all resolve to committed rows. The seventh did
    # NOT. A caption put the 6.25 MHz tooth spacing on the transition
    # axis, where the constant is Omega and not Omega/2, and reading the
    # page to fix it found the same error three lines above in prose. A
    # caption is a claim surface that gets less scrutiny than the prose
    # it sits under, which is the fig15 class exactly.
    #
    # Re-seeded a third time for the eight docs/history/ chapters, which are
    # new files rather than new claims: docs/HISTORY.md became a hub over a
    # directory and its entries moved out under it. The hub's count did not
    # fall, because the hub keeps a quantity index that restates each
    # entry's old and new value on purpose, so the same decimal is now
    # counted in two files. That duplication is the index's whole function
    # and it is also a place a value could drift, which is why it is
    # written down here rather than absorbed silently.
    #
    # Re-seeded a FOURTH time, and this note is retrospective: that re-seed
    # landed with no reason at all, the first in the file's history to do
    # so, and a board seat caught it. Recorded now because the
    # convention three paragraphs up is the whole reason the ratchet keeps
    # falling, and a re-seed that skips it is the failure the convention
    # exists to prevent. Most of that seed was a FALL and needed no defence:
    # seven wiki pages and two history files tightened as the register sweep
    # resolved their bare digits to rows. Three entries ROSE and are the
    # ones that owed a reason. docs/UNCERTAINTY.md 20 to 24 and
    # docs/history/01 34 to 36 were the collisional-shift entry and the
    # polarizability history entry, both hand arithmetic; the new
    # docs/notes/k8_radiation_trapping_adjudication.md at 12 is a page whose
    # own header says every number on it is read from a committed row, so
    # each of its twelve resolves to kernel_k8.csv or to RESULTS.md.
    #
    # Re-seeded a FIFTH time, downward, and this one is the answer to the
    # fourth. docs/UNCERTAINTY.md falls 24 to 21 because the collisional
    # block stopped printing digits: its figures now come from
    # results/collisional_shift_bound.csv. The differential, the ratio and the
    # expectation carry real inline `ref:` links; the four per-temperature
    # table cells are code-spans naming their row instead, and _STRIP excludes
    # both, by different branches. The distinction is written down because a
    # re-seed reason that names the wrong mechanism is how the next reader
    # learns the wrong lesson. Four of the digits it
    # used to print were wrong. That is the argument for the ratchet in one
    # sentence -- an unreferenced decimal is not a style problem, it is a
    # number nobody can check.
    #
    # Re-seeded a SIXTH time, upward, for the correction record alone.
    # docs/history/01 and its index row in docs/HISTORY.md gained a lineage
    # table with twelve was-and-now pairs, the night the collisional-shift
    # entry was re-read seat by seat. Counted, not estimated: a first draft of
    # this comment said eleven and a board seat counted the rows. A history table is the one place in
    # this repository a replaced number is licensed to appear, which is the
    # same argument the third re-seed made for the eight chapters, and the
    # figures in it are was-and-now pairs, so the replaced halves are
    # licensed here by definition and the live halves resolve to
    # results/collisional_shift_bound.csv, results/stark_joint.csv or the
    # cited paper, not all to one file as a first draft of this comment
    # claimed. The count rose again, 44 to 50, when a board found that one of
    # those twelve rows conflated two different comparisons under one heading
    # and that its correction was itself wrong: the repair had divided two
    # light shifts taken at DIFFERENT DRIVE POWERS, which credits this record
    # with the power ratio. Splitting the row and restating it on the
    # coefficient is what the six new figures are. Every other file that could
    # take a reference now does, including Orson's stated drive power, which
    # gained a row in its lit note rather than being printed four times.
    #
    # THE GUARD WAS BLIND, and the seventh re-seed is the repair rather than a
    # concession. `_STRIP`'s indented-code branch read `^\s{4,}\S.*$` under
    # re.S|re.M, so `.` matched newlines and `$` matched at every line end:
    # the greedy `.*` ran from a file's FIRST indented line to the end of the
    # file and deleted everything after it before `_DECIMAL` ever ran. A board
    # seat proved it on a three-line synthetic and then measured the damage:
    # 25 files were scored on a fraction of themselves, one of them on 7 per
    # cent. Fixing the branch to `[^\n]*` raises the corpus count 4,486 to
    # 6,451, and the 1,965 decimals that appear are not new claims -- they
    # were always there, and the guard whose docstring says it exists to catch
    # "exactly the class that produced the retracted band digits" could not
    # see them. The baseline is re-seeded at the true count so it can start
    # falling from a number that means something.
    #
    # Re-seeded an EIGHTH time, 2026-08-27, for one new teaching page, and
    # the count below was itself corrected by a board before it landed.
    # docs/wiki/reduced-chi-squared.md is the reduced-chi-squared explainer
    # and seeds at EIGHT, not nine as a first draft of this note said. The
    # eight, enumerated by running this module's own _STRIP and _DECIMAL over
    # the file rather than by eye: 0.45 and 0.045, the sqrt(2/nu) at ten and
    # at a thousand degrees of freedom; one of the two 1.5s, the value that
    # is a routine fluctuation at the first and eleven standard deviations at
    # the second; 0.78 and 1.09, the per-condition range, read off a COLUMN
    # of linefit_conditions.csv with no single row to point at; 0.75, the
    # joint fit's own total; and TWO further occurrences of 3.7, in the image
    # alt text and in an italic caption, which a ref: link cannot reach.
    # The textbook constants have nothing to reference, because a `results/`
    # row for them would be this page recomputing an identity and then citing
    # itself. The one 3.7 in body prose IS linked to results/stark_sweep.csv,
    # and linking it is what this wave's correction turned on: that 3.7
    # belongs to the summary width regression and NOT to the joint fit the
    # record's limit comes from, and this page asserted otherwise until a
    # board caught it. A first draft of this paragraph claimed all three 3.7s
    # were linked, on the page written to attribute that number correctly.
    # Re-seeded a NINTH time, 2026-08-27, in the same night as the eighth and
    # for the second board's corrections to the first board's repair. The
    # retraction of the light-shift exclusion was restructured after a seat
    # showed its leading reason did not support its conclusion: both readings
    # of the limit still placed the prediction above it, so the construction
    # spread was never the thing that falsified the exclusion. What does is
    # the subset dependence, and stating it costs the pair 1.626 against
    # 1.618, the drop-4192 bound against the predicted coefficient. Five
    # files rose. The additions are the evidence itself, and most of them
    # cannot take a `ref:` link for reasons worth recording rather than
    # working around: 1.104 and 1.115 are the producer's own decomposition of
    # the construction spread and live inside a `note` column, which the
    # resolver reads for a VALUE and not for prose; 0.223, 0.248, 0.348 and
    # 0.372 are the per-line pumping branching, committed in
    # `rb5s6s/stark.py` as source prose with no results row of their own; and
    # 2.4 to 2.5 is a square root taken here from two committed numbers, so a
    # row for it would be this page citing its own arithmetic. The ones that
    # DO have rows are linked. docs/methods/04 rose furthest because the
    # stale 1/3-to-2/3 branching bracket was replaced with the four committed
    # values, which is four numbers where there were two and is the whole
    # point of the fix.
    # Re-seeded a TENTH time, 2026-08-27, and the third re-seed of one night.
    # A THIRD board refuted the leading reason a SECOND board had installed.
    # The subset arm the second repair led on, drop-4192 at kappa < 1.626,
    # does not sit above the prediction at all: the prediction is an envelope
    # running 1.404 to 1.760 in kappa and 1.626 lands INSIDE it, so that
    # reason silently reverted to the point centre the next paragraph says is
    # not a calibrated centre. Its half-per-cent margin against the predicted point is also 4.6 times
    # smaller than the profile's own committed numerical scatter, and
    # RESULTS.md C3f reads the margin from the primary construction alone.
    # The replacement is the largest instability the record actually holds
    # and had never used: the pooled construction does not reproduce, its own
    # passes putting the bound at 1.007, 1.231 and 2.106 MHz per W. Those
    # three numbers, the envelope pair, and the 1.104/1.115 decomposition are
    # most of the rise here. They are the evidence, and the ones with rows
    # are linked. docs/plan/00 rose furthest because it also gained the
    # campaign-only 0.15 arm, whose omission had made the record's own subset
    # spread look narrower than it is.
    # Re-seeded an ELEVENTH time, 2026-08-27, and the last of that night. A
    # FOURTH board found that the retraction had OVERCORRECTED: only the
    # two-sigma calibration fails, while the exclusion at 95 per cent itself
    # stands, because the primary limit of 1.147 lies below every point of the
    # predicted envelope, 1.404 to 1.760 in kappa. Stating that correctly puts
    # the envelope pair and the posterior's 1.412 into docs/CLAIMS.md, which is
    # the whole of this rise. They are the evidence for the sentence and there
    # is no single row to link them to, the envelope being two rows and the
    # posterior limit being in kappa where the committed row is in a.u.
    # Re-seeded a TWELFTH time, 2026-08-27, for two decimals in one clause.
    # A board found C3f quoting the pre-adjudication 0.35 MHz and 1.3x inside
    # the same bullet that elsewhere uses the envelope built on 1145. The
    # clause now states both cells are pre-adjudication and gives the current
    # 0.364 and 1.4x, which is the two decimals. The stale cells stay because
    # regenerating them needs a five-hour refit on a tree this repository does
    # not hold, so the label beside them is what stands until it runs.
    # Re-seeded a THIRTEENTH time, 2026-08-27, and this one is the night's
    # actual result. A FIFTH board, the first run with the five canonical
    # seats the ledger requires, found that the retraction had been aimed at
    # a claim that was substantially TRUE: the retracted sentence's own
    # parenthetical defined its two-sigma as sqrt(Delta_chi2) under Wilks, a
    # DATA-side distance that never divides by the prediction's envelope, and
    # recomputed across that envelope it runs 4.1 to 5.7, i.e. 2.0 to 2.4
    # sigma. What the sentence lacked was two qualifications, and the second
    # had been sitting in committed rows all night: the lopo_dchi2_pred rows
    # read 8.75, 2.27, 1.12 and 0.61. (The binary count this comment used to
    # draw from them was withdrawn 2026-08-27: the arms are separate
    # likelihoods.) Those rows
    # fall below the 2.706 threshold at the predicted kappa and only dropping
    # 993.4121 nm leaves the prediction excluded. The record had read those
    # four as "all positive and similar" over a span of fourteen, and stated
    # the opposite conclusion. Those four numbers, the Delta_chi2 range and
    # the envelope pair are the whole of this rise, across seven files. They
    # are the evidence for the corrected sentence and there is no single row
    # to link a range to.
    # Re-seeded a FOURTEENTH time, 2026-08-27, and this is the last of that
    # night. A SIXTH board found the withdrawn claim was not only in the
    # prose: it was written into every lopo row by two producers, it was the
    # NAME of a green test asserting only positivity at a legacy checkpoint,
    # and it stood unmarked in results/README.md and in the preregistration.
    # It also found the referent: those rows are evaluated at the
    # PRE-ADJUDICATION kappa_pred of 1.545 and not at this record's own
    # 1.618, so the count of arms below threshold is provisional. Stating
    # that referent everywhere the four numbers appear is most of this rise,
    # and the numbers themselves, 8.75 / 2.27 / 1.12 / 0.61 and the 2.706
    # threshold, are the evidence. There is no single row to link a set of
    # four to.
    # Re-seeded a FIFTEENTH time, 2026-08-27, and this rise buys the night's
    # best result rather than another correction. A SEVENTH board found that
    # the leave-one-out fragility is a property of ONE construction. The
    # count this comment used to give was withdrawn 2026-08-27; the
    # three-session joint fit has arms straddling the 2.706
    # threshold, while the FULL-ARCHIVE fit is both stronger (Delta_chi2 6.5
    # to 10.5 across the envelope, 2.5 to 3.2 sigma, against 4.1 to 5.7 and
    # 2.0 to 2.4) and leave-one-out ROBUST, all four of its arms clearing at
    # 3.17 to 11.48. No surface said so, which put the record in breach of its
    # own standing rule to present the fullest model. Stating the comparison
    # everywhere the fragility appears is this rise: kappa < 0.944, the two
    # Delta_chi2 ranges, and the four arms. The same board caught a note this
    # wave had itself introduced, which copied the joint fit's finding into
    # the full-archive producer where zero of four sit below threshold.
    counts: dict[str, int] = {}
    for rel in _tracked_markdown():
        path = ROOT / rel
        if not path.exists() or rel.startswith("docs/lit/"):
            continue
        text = _STRIP.sub(" ", path.read_text(encoding="utf-8"))
        n = len(_DECIMAL.findall(text))
        if n:
            counts[rel] = n
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


if __name__ == "__main__":
    import sys
    if "--reseed" in sys.argv:
        BASELINE.write_text(json.dumps(_counts(), indent=1, sort_keys=True)
                            + "\n")
        print(f"reseeded {BASELINE.name} over {len(_counts())} files")
