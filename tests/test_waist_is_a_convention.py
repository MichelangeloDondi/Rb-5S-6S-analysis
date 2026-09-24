"""The 2025 waist is a convention, and no reader surface calls it measured.

`rb5s6s/constants.py` says it in the symbol's own docstring: w0 is NOT measured on this bench (a
lineage profile on another laser source, without this beam's 3 mm modulator aperture), and the owner
corrected the reading twice (2026-09-10, 2026-09-15). On 2026-09-17 thirty-six reader-facing lines still
called the retired waist convention "measured", and the owner named w0 among the stale values. The forms refused below
are the unambiguous ones: a measured waist called out by NUMBER, a measured w0 set equal to one, and a definite "the measured
waist" that a number is evaluated at. A campaign's future measurement ("the waist measured at several
powers", "a measured w0 would ...") is not refused, and neither is a preregistration or a history
record, which quote their own day.

RE-PINNED 2026-09-22 (O44): the first three patterns below used to name the retired convention's own
number literally. No waist of any size has ever been independently measured on this bench (the
knife-edge scan is still owed), so a claim of a MEASURED waist is false whichever number it names, and
the patterns now match any number rather than only the retired one. Matching any number collides with
a THIRD PARTY's own measured beam, quoted correctly elsewhere in this record (Nieddu's and Rajasree's
profiler readings, docs/lit/nieddu2019.md and docs/lit/rajasree2020thesis.md) -- a different apparatus
and a different quantity, so a paragraph naming one of them is not refused.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STALE = [
    ("a measured waist named by a number and its unit",
     re.compile(r"measured\s+\d+(?:\.\d+)?\s*(?:µm|um|micron)", re.I)),
    ("a number and unit before 'measured waist'",
     re.compile(r"\d+(?:\.\d+)?\s*(?:µm|um)\s+measured\s+(?:beam\s+)?waist", re.I)),
    ("a measured w0 equal to a number",
     re.compile(r"measured\s+\$?w_?\{?0\}?\$?\s*=\s*\d+(?:\.\d+)?", re.I)),
    ("a number evaluated at the measured waist",
     re.compile(r"\b(?:at|using|rides|on)\s+the\s+(?:accepted\s+)?measured\s+(?:beam\s+)?waist\b", re.I)),
    ("the measured w0 band", re.compile(r"measured\s+w_?0\s+band", re.I)),
    # THE CODE SAID IT TOO (2026-09-17): a figure's annotation, a CSV note and nine docstrings called
    # the record's waist measured after every reader page had stopped, because the scan read only
    # markdown. "from the measured w0" and "transit(FIXED at the measured w0)" were the two spellings.
    ("the measured waist named as the record's",
     re.compile(r"\b(?:from|at|using|rides|on)\s+(?:the|its|this record's)\s+(?:accepted\s+)?measured\s+"
                r"(?:beam\s+)?(?:waist|\$?w_?\{?0\}?\$?)", re.I)),
    # THE ADJECTIVE MOVED AND THE SCAN DID NOT (2026-09-18). "at the COMMITTED measured waist" and
    # "the measured waist makes" both name this record's own number and neither matches the line
    # above: the first because only "accepted" was allowed between the article and the word, the
    # second because it needs no preposition at all. The population had holes to match -- `tests/`
    # was not in it. A possessive or a determiner naming THIS record's waist is the form to catch;
    # a FUTURE campaign's measurement is admitted by the exemptions and by the plant below.
    ("the record's own waist called measured, with an adjective between",
     re.compile(r"\b(?:from|at|using|rides|on)\s+the\s+(?:committed|adopted|accepted|current|record's)\s+"
                r"measured\s+(?:beam\s+)?(?:waist|\$?w_?\{?0\}?\$?)", re.I)),
    ("the committed measured waist as a noun phrase",
     re.compile(r"\bthe\s+committed\s+measured\s+(?:beam\s+)?(?:waist|\$?w_?\{?0\}?\$?)", re.I)),
]
EXEMPT_FILES = ("docs/PREREGISTRATION_RESULTS.md", "docs/notes/transit_width_resolved.md",
                "docs/lit/bruvelis2012.md",
                # A WAIST-LANGUAGE GUARD MUST QUOTE THE FORMS IT CATCHES, and adding `tests/` to the
                # population on 2026-09-18 made both of them their own first offenders. This is the
                # same self-match that made an expensive-producer check find its own shell in `ps`.
                "tests/test_waist_is_a_convention.py", "tests/test_waist_language.py")

# RE-PINNED 2026-09-22 (O44): matching ANY number (above) collided with "directly measured 128 µm"
# and "a MEASURED 128 um beam diameter" -- Nieddu's and Rajasree's own profiler readings of a
# DIFFERENT apparatus, quoted correctly across docs/APPARATUS.md, docs/LITERATURE.md,
# docs/LITERATURE_INDEX.md and the rajasree thesis note itself, none of which claim anything about
# THIS bench. `private/checks/retired_values.py`'s own role patterns carry the identical allowlist
# for the identical reason (its `_ROLE_ALLOWLIST_FILES` comment). A paragraph naming either
# researcher is about their beam, not this record's, so it is not refused.
_THIRD_PARTY_WAIST = re.compile(r"nieddu|rajasree", re.I)


def stale_waist_lines(files, reader):
    hits = []
    for f in files:
        try:
            text = reader(f)
        except OSError:
            continue
        # a sentence may wrap, so the scan reads each paragraph joined, and names its first line
        lines = text.splitlines()
        start = 0
        for i in range(len(lines) + 1):
            if i == len(lines) or not lines[i].strip():
                para = " ".join(l.strip() for l in lines[start:i])
                if not _THIRD_PARTY_WAIST.search(para):
                    for name, pat in STALE:
                        if pat.search(para):
                            hits.append(f"{f}:{start + 1} [{name}] {para[:110]}")
                            break
                start = i + 1
    return hits


def _reader_surfaces():
    # `tests/` JOINS THE POPULATION (2026-09-18): a test's own comment called the record's waist
    # measured while every reader page had stopped, which is the same defect one layer down.
    out = subprocess.run(["git", "ls-files", "README.md", "START_HERE.md", "docs", "results/README.md",
                          "rb5s6s", "scripts", "examples", "tests"],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith((".md", ".py")) and f not in EXEMPT_FILES and "prereg" not in f]


def test_the_scan_refuses_the_stale_forms_and_admits_a_campaign_measurement():
    planted = {
        "a.md": "below the predicted 0.35 MHz at the measured waist",
        "b.md": "At the dataset's\nmeasured 50 µm and 225 mW the law holds",
        "c.md": "Taken over the measured w0 band (40-45um)",
        "d.md": "the waist measured at several powers with the EOM thermalised",
        "e.md": "A measured $w_0$, by fixing transit, would turn this bound into a measurement.",
        "f.md": "below the predicted 0.35 MHz at the waist convention",
        "g.py": "the main analysis FIXES transit from the measured w0 and reports",
        "h.py": "B  + transit   A (x) transit(FIXED at the measured w0)",
        "i.py": "Per setting: the magnification, the measured waist, the retro ratio",
        # PLANT for the third-party escape (2026-09-22): the same shape as b.md's positive, so the
        # escape is shown doing real work and not merely admitting a line the pattern never fired on.
        "j.md": "Rajasree 2020 measured 128 um beam diameter on their own bench",
    }
    hits = stale_waist_lines(list(planted), lambda f: planted[f])
    assert sorted(h.split(":")[0] for h in hits) == ["a.md", "b.md", "c.md", "g.py", "h.py"], hits
    # the escape is not a no-op: strip the researcher's name and the same sentence is refused
    assert stale_waist_lines(["k.md"], lambda f: "measured 128 um beam diameter on their own bench")


def test_no_reader_surface_calls_the_2025_waist_measured():
    hits = stale_waist_lines(_reader_surfaces(), lambda f: (ROOT / f).read_text(encoding="utf-8", errors="ignore"))
    assert not hits, ("the 2025 waist is a convention (rb5s6s/constants.py, W0_CENTRAL_M's docstring), "
                      "and these reader lines call it measured:\n  " + "\n  ".join(hits[:40]))
