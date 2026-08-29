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
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# THE RE-SEED LOG LIVES HERE AND IT IS NOT THE PROJECT'S HISTORY.
# LANGUAGE 19.16a confines history to one file, and a board seat was right
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
    # so, and it was caught. Recorded now because the
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
    # this comment said eleven and the rows were counted. A history table is the one place in
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
    #
    # Re-seeded a SIXTEENTH time, 2026-08-27, and this one carries a
    # correction of its own. The baseline moved 62 to 65 earlier the same night with
    # NO paragraph here at all, which is the one thing this convention exists
    # to prevent, and it was caught. The re-seed was also wrong: the
    # true count was 72, so an under-seeded baseline sat in the index looking
    # deliberate.
    #
    # What the rise actually buys, now that the file has been cut from 6612
    # words back to its budget. README gained a nanofibre block whose numbers
    # are the first two-arm campaign forecast this record has run through the
    # twin: the collisional-against-Gaussian correlation at -0.941 and -0.913
    # on the cell against -0.941 on the fibre, the collisional width falling
    # from 0.19-0.93 MHz to 178 Hz at MOT density, and about 69 minutes per
    # trace to match the cell's per-trace precision at 25 to 40 counts per ms.
    # Each is computed by scripts/run_campaign_twin_forecast.py into
    # results/campaign_twin_forecast.csv, which the same block names one line
    # above them, so they are traceable by file even where the inline ref
    # syntax does not reach a table cell. The paid-for subtraction is real:
    # three duplicated retellings, two paragraph-in-cell table rows, a
    # 343-word caption and a stale nav claim came out to fit them.
    #
    # Re-seeded a SEVENTEENTH time, 2026-08-27, same wave and same night as
    # the sixteenth, and this one is three decimals for a physics repair. The
    # mode solve replaced the assumed neff_band in results/onf_candidate.csv
    # and moved twenty of its rows, so docs/big_picture/06_next-nanofibre.md
    # and docs/wiki/guided-atoms-and-nanofibres.md now carry the solved
    # effective mode area of 1.98 um^2 in place of an assumed 0.50, the
    # computed transit band 105 to 141 kHz in place of a hardcoded 98 to 181,
    # and the intensity decay length beside the amplitude one because the
    # producer had been returning one while labelled the other. Each replaces
    # a WRONG number with a right one and each is a row of the CSV those
    # sections name. The rise is three and the physics it corrects was a
    # factor of four in every guided intensity.
    #
    # Re-seeded a TENTH time, 2026-08-28, and it moves in BOTH directions,
    # which is why it is recorded rather than waved through. THREE FILES FELL
    # and that is the point of the wave: a board found correction narration
    # sitting outside docs/HISTORY.md on the two chapters written to carry
    # this work to a hiring reader and to the group whose fibre it is, which
    # is the register STYLE.md bans and which reads as advocacy. Cutting it
    # took docs/big_picture/06 from 22 to 20, docs/big_picture/09 from 12 to
    # 11, and docs/wiki/guided-atoms-and-nanofibres.md from 9 to 5, because
    # the narrated numbers were retired values that no `results/` row holds
    # and none could be referenced.
    #
    # THREE FILES ROSE and the reason is the other half of the same repair.
    # docs/HISTORY.md gained seven, which is where those retired values went:
    # this file is the one surface licensed to print a value the record no
    # longer believes, and a retired number is unreferenceable BY DEFINITION,
    # since the row that would hold it is the row that was replaced.
    # docs/methods/09 gained two, 1.554 and 1.811, the two levers inside the
    # transit kernel factor: a seat showed the 0.6436 is the envelope's
    # two-sidedness and not the squared-magnitude rule, so the chapter now
    # names sidedness and weighting as separate assumptions and states both
    # sizes. docs/notes/onf_candidate.md gained one from the same correction.
    #
    # Re-seeded an ELEVENTH time, 2026-08-28, for the ninth board round, and it
    # moves in both directions again. THREE FELL. docs/HISTORY.md 161 to 158,
    # because the guided-geometry section was rewritten against HEAD: three of
    # its six rows retired values that were never committed, which is
    # intra-wave churn and not history, and the row for a CSV absent from HEAD
    # entirely was deleted. docs/big_picture/06 20 to 17 and docs/methods/09 45
    # to 43, because the additivity correction replaced a narrated sequence of
    # retired precisions with one statement of the mechanism.
    #
    # ONE ROSE. docs/notes/onf_candidate.md gained two, the fraction 0.04 to
    # 0.09 and the exponent 0.98, which are the size and the temperature
    # scaling of the transit kernel's second-order entry into the width.
    # NEITHER CAN TAKE A `ref:` LINK, because neither is a committed row: they
    # are properties of the kernel measured by convolution, and no producer
    # emits them. That is a real gap, it is the reason this file's count rose,
    # and it is named here instead of worked around.
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
