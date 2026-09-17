"""The 2025 waist is a convention, and no reader surface calls it measured.

`rb5s6s/constants.py` says it in the symbol's own docstring: w0 is NOT measured on this bench (a
lineage profile on another laser source, without this beam's 3 mm modulator aperture), and the owner
corrected the reading twice (2026-09-10, 2026-09-15). On 2026-09-17 thirty-six reader-facing lines still
called the 64 um waist "measured", and the owner named w0 among the stale values. The forms refused below
are the unambiguous ones: a measured 64 um, a measured w0 equal to 64, and a definite "the measured
waist" that a number is evaluated at. A campaign's future measurement ("the waist measured at several
powers", "a measured w0 would ...") is not refused, and neither is a preregistration or a history
record, which quote their own day.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STALE = [
    ("a measured 64 um", re.compile(r"measured\s+64\s*(?:µm|um|micron)", re.I)),
    ("a 64 um measured waist", re.compile(r"64\s*(?:µm|um)\s+measured\s+(?:beam\s+)?waist", re.I)),
    ("a measured w0 equal to 64", re.compile(r"measured\s+\$?w_?\{?0\}?\$?\s*=\s*64", re.I)),
    ("a number evaluated at the measured waist",
     re.compile(r"\b(?:at|using|rides|on)\s+the\s+(?:accepted\s+)?measured\s+(?:beam\s+)?waist\b", re.I)),
    ("the measured w0 band", re.compile(r"measured\s+w_?0\s+band", re.I)),
    # THE CODE SAID IT TOO (2026-09-17): a figure's annotation, a CSV note and nine docstrings called
    # the record's waist measured after every reader page had stopped, because the scan read only
    # markdown. "from the measured w0" and "transit(FIXED at the measured w0)" were the two spellings.
    ("the measured waist named as the record's",
     re.compile(r"\b(?:from|at|using|rides|on)\s+(?:the|its|this record's)\s+(?:accepted\s+)?measured\s+"
                r"(?:beam\s+)?(?:waist|\$?w_?\{?0\}?\$?)", re.I)),
]
EXEMPT_FILES = ("docs/PREREGISTRATION_RESULTS.md", "docs/notes/transit_width_resolved.md",
                "docs/lit/bruvelis2012.md")


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
                for name, pat in STALE:
                    if pat.search(para):
                        hits.append(f"{f}:{start + 1} [{name}] {para[:110]}")
                        break
                start = i + 1
    return hits


def _reader_surfaces():
    out = subprocess.run(["git", "ls-files", "README.md", "START_HERE.md", "docs", "results/README.md",
                          "rb5s6s", "scripts", "examples"],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith((".md", ".py")) and f not in EXEMPT_FILES and "prereg" not in f]


def test_the_scan_refuses_the_stale_forms_and_admits_a_campaign_measurement():
    planted = {
        "a.md": "below the predicted 0.35 MHz at the measured waist",
        "b.md": "At the dataset's\nmeasured 64 µm and 225 mW the law holds",
        "c.md": "Taken over the measured w0 band (62-68um)",
        "d.md": "the waist measured at several powers with the EOM thermalised",
        "e.md": "A measured $w_0$, by fixing transit, would turn this bound into a measurement.",
        "f.md": "below the predicted 0.35 MHz at the waist convention",
        "g.py": "the main analysis FIXES transit from the measured w0 and reports",
        "h.py": "B  + transit   A (x) transit(FIXED at the measured w0)",
        "i.py": "Per setting: the magnification, the measured waist, the retro ratio",
    }
    hits = stale_waist_lines(list(planted), lambda f: planted[f])
    assert sorted(h.split(":")[0] for h in hits) == ["a.md", "b.md", "c.md", "g.py", "h.py"], hits


def test_no_reader_surface_calls_the_2025_waist_measured():
    hits = stale_waist_lines(_reader_surfaces(), lambda f: (ROOT / f).read_text(encoding="utf-8", errors="ignore"))
    assert not hits, ("the 2025 waist is a convention (rb5s6s/constants.py, W0_MEASURED_M's docstring), "
                      "and these reader lines call it measured:\n  " + "\n  ".join(hits[:40]))
