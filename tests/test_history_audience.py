"""Every history entry declares who it is for, and internal ones stay private.

WHY THIS EXISTS. The correction record WAS public and ported to the mirror,
so a PI assessing this work met it. Measured 2026-09-05, **4,305 of its 11,550
words, 37 per cent, are the correction history of our own machinery** --
provenance guards, documentation counts, status columns, producers disagreeing
in a fourth decimal. None of it changes a number either reader would quote, and
it feeds the one wrong reading the strategic record most wants removed: a
perfectionist who does not ship. The retraction record is an asset exactly
where it retracts something a reader could have believed, and a liability
everywhere else.

WHY IT IS NOT A PROSE CLASSIFIER. The obvious test -- does the entry state a
physical quantity with a unit -- was measured against the 76 existing entries
before any code was written: 7 false negatives and 18 false positives, a third
of the corpus misfiled. A guard built on it would have trained the eye to
ignore its own output, which this record has already learned once from the
quotation guard.

SO THE AUTHOR DECLARES, AND THE DECLARATION CANNOT BE SKIPPED. Every `## `
entry carries an audience marker on the line beneath it:

    <!-- audience: reader -->    a number or claim a reader could have quoted,
                                 relied on, or built a decision on
    <!-- audience: internal -->  the correction history of our own machinery

`reader` is the only value the public hub accepts. An `internal` entry belongs
in `private/`, and this test refuses it here. Entries predating the rule are
grandfathered BY NAME below, so the guard starts green and every NEW entry
must choose -- which is the whole mechanism: the judgement is not forbidden to
skip, it is impossible to skip.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HUB = ROOT / "private" / "history"   # private since 2026-09-05, owner decision
MARKER = re.compile(r"<!--\s*audience:\s*(reader|internal)\s*-->", re.I)

# The correction record is private since 2026-09-05 (owner decision), so a
# public clone has nothing to grade and must skip rather than fail.
pytestmark = pytest.mark.skipif(
    not HUB.is_dir(),
    reason="the correction record is private and absent from this clone")

# Entries written before the rule (2026-09-05). Grandfathered by heading so the
# guard starts green; NOT an exemption for anything new. Shrinking this list is
# how the hub is cleaned, and nothing may be added to it.
GRANDFATHERED = frozenset({
    'A checker was described in three documents and did not exist, 2026-08-28',
    'A governed row about ungoverned numbers, 2026-08-23',
    'A published regression had no producer, 2026-08-23',
    'A published sentence called a sensitivity an uncertainty, 2026-08-22',
    "A repair's own account of itself was wrong, 2026-08-28",
    'A results file said a finished instrument was deferred, 2026-08-23',
    'A results path was renamed away from a collision, 2026-08-22',
    'A summary drifted from the record it restated, 2026-08-28',
    'An exact degeneracy that the code broke, and the number that had no referent, 2026-08-20',
    'Counts in prose, and the day three of them were wrong at once, 2026-08-28',
    'Documentation counts, 2026-08-19',
    'Emphasis capitals in the corpus, 2026-08-24',
    'Seven of ten notes had no producer, 2026-08-23',
    'Sub-GHz EOM drive justification, 2026-08-19',
    "The 1.9 ms autocorrelation's mechanism, 2026-08-23",
    'The 2025 laser width bound, renamed 2026-08-24',
    'The 2026-08-15 band and design corrections',
    'The 2026-08-17 corrections',
    'The 2026-08-18 corrections',
    'The 2026-08-19 corrections',
    'The 60 µm working waist, retired 2026-08-15',
    "The 64 µm waist's provenance, 2026-08-24",
    'The acquisition-mode ceiling, 2026-08-24',
    'The amplitude power law was described rather than tested, 2026-08-18',
    "The band regression's density sign, 2026-08-24",
    'The band-excess significance pair, 2026-08-24',
    'The bit-depth argument, withdrawn 2026-08-24',
    'The cascade line table, 2026-08-19',
    "The case page's re-centring purchase factor, 2026-08-20",
    "The case page's two ungrounded numbers, 2026-08-23",
    'The case-page headline statement, 2026-08-24',
    'The class this chapter is an instance of',
    'The class-adequacy caveat, tested twice in one day, 2026-08-22',
    "The collisional-shift entry and Orson's own axis, 2026-08-27",
    'The comb tooth-weight model, 2026-08-19',
    "The cumulant producer's transit, from a literal to the record's value, 2026-09-04",
    "The digital twin's blackbody term, corrected 2026-08-24",
    'The drift-freedom factor of 48, retracted 2026-08-25',
    "The duel's injected shift labelled as the archive's, 2026-09-04",
    'The environment migration landed, 2026-08-23',
    'The headline beta_self shift under the laser-kernel switch, 2026-08-20',
    "The hot fibre's siblings, and the line budget's missing term, 2026-08-29",
    'The hot transit width was still the retired route, 2026-08-29',
    'The identifiability diagnostics moved under the arithmetic environment, 2026-08-22',
    'The in-window structure and the band excess share a predictor, 2026-08-23',
    'The mode was assumed and is now solved, 2026-08-27/28',
    'The modulation depth menu, 2026-08-19',
    'The note-provenance debt count, 2026-08-23',
    'The package exported a polarizability the record disagreed with, 2026-08-25',
    'The pair-route magnetic-channel rate, 2026-08-20',
    'The provenance debt partition, 2026-08-23',
    'The provenance guard reported a clean corpus it could not see, 2026-08-23',
    "The provenance instrument's self-reference, 2026-08-23",
    'The quantities pages disagreed with the record they index, 2026-08-26',
    'The release-note rules were not enforced as claimed, 2026-08-28',
    'The ruler-resolvability table, and the rows behind it, 2026-08-28',
    'The saturation companion factor, 2026-08-23',
    'The silica index at the working wavelength, 2026-08-28',
    "The skew-scaling producer's default draw count, 2026-08-20",
    'The transit kernel, and every claim about it retired in one day, 2026-08-28',
    "The tutorial's width-degeneracy claim, 2026-08-19",
    "The twin's four-decimal correlations, retired 2026-08-24",
    "The twin's span-sweep correlations, and the fibre wiki page, 2026-08-23",
    "The two-atom channel's headroom margin, 2026-08-20",
    'The v4.3 and v4.4 release pages, withdrawn 2026-08-26',
    "The vector light shift's sublevel spread, 2026-08-20",
    'The width-pinning factor, 2026-08-19',
    'The width-power concavity, 2026-08-18',
    "The windowed third cumulant's survival, quantified, 2026-08-31",
    'The withdrawn release notes were withdrawn for the physics, 2026-08-28',
    'Three pages described the kernel systematic as unquantified or still to be done, 2026-08-22',
    'Two producers disagreed about R_kernel in the fourth decimal, 2026-08-23',
    'Two results files were committed without their status column, 2026-08-23',
    'What a lever is worth, and it moved against the campaign',
})


def _entries():
    out = []
    if not HUB.is_dir():
        return out          # private/ is absent from a public clone
    for f in sorted(HUB.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        parts = re.split(r"^## ", text, flags=re.M)[1:]
        for part in parts:
            head = part.splitlines()[0].strip()
            body = "\n".join(part.splitlines()[1:4])
            out.append((f.name, head, body))
    return out


ENTRIES = _entries()


@pytest.mark.skipif(not (ROOT / "private" / "history").is_dir(),
                    reason="the correction record is private and absent here")
def test_the_hub_has_entries_to_grade():
    """A population that empties passes by grading nothing."""
    assert len(ENTRIES) > 20, (
        f"only {len(ENTRIES)} history entries found; the split that finds them "
        "has probably broken, and an empty population passes silently")


@pytest.mark.parametrize("fname,head,body", ENTRIES,
                         ids=[f"{f}::{h[:40]}" for f, h, _ in ENTRIES])
def test_every_entry_declares_its_audience(fname, head, body):
    if head in GRANDFATHERED:
        pytest.skip("predates the audience rule; grandfathered by name")
    m = MARKER.search(body)
    assert m, (
        f"{fname}: the entry '{head}' declares no audience. Add one of\n"
        "    <!-- audience: reader -->    a number or claim a reader could have quoted\n"
        "    <!-- audience: internal -->  the correction history of our own machinery\n"
        "on the line beneath the heading. The declaration is what lets a later "
        "judgement about disclosure separate the machinery mechanically, "
        "instead of re-reading the whole record.")
    assert m.group(1).lower() == "reader", (
        f"{fname}: the entry '{head}' declares itself internal, and this hub "
        "carries the reader-facing account. The machinery's own correction "
        "history belongs in the register, not here.")
