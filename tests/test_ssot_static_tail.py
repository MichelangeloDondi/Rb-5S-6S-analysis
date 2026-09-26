"""The static-tail differential polarizability stands in the history folder and nowhere else.

Owner, 2026-09-17: the retired value may stand in the history folder alone, "not just labelled, neither in
prose, nor in comments nor in docstrings". This test grades the tracked tree, which is what the public
mirror carries; `private/checks/retired_values.py` grades the rest of the repository with the same digests.
It holds DIGESTS of the value's canonical forms and never the value: a tripwire that spells the number it
refuses would be one more copy of it, so its plants build the value by arithmetic.
"""
import hashlib
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
#: SHA-256 of the magnitude's integer rounding and of its one-decimal rounding.
RETIRED_DIGESTS = {"a5bef651c8e3fd6cc63c43cd6bc1341af97d78af828f152c0f40d5a06570bd34", "fa676a7ec9fbd2c947465708e9f754d05e7b00694a911514ddb3e3f6d0b94f80"}
TOKEN = re.compile(r"(?<![\w.])[-\u2212]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?(?![\w.]*\d)(?!\w)")
BINARY = (".png", ".pdf", ".jpg", ".jpeg", ".npz", ".npy", ".gz", ".ico", ".zip", ".xlsx")


def _forms(tok):
    try:
        x = abs(float(tok.replace("\u2212", "-")))
    except (ValueError, OverflowError):
        return set()
    if not (x == x) or x > 1e15:
        return set()
    return {f"{round(x):d}", f"{round(x, 1):.1f}"}


_POLARIZABILITY_ROW = re.compile(r"delta.?alpha|polari[sz]|\\balpha_|a\\.u\\.|\\bau\\b|\\u0394\\u03b1", re.I)


def _text_cells(line):
    """A CSV row with its numeric cells blanked: a computed cell is data of its own quantity, a note is prose."""
    import csv
    try:
        cells = next(csv.reader([line]))
    except (csv.Error, StopIteration):
        return line
    keep = []
    for c in cells:
        try:
            float(c.replace("\u2212", "-"))
        except ValueError:
            keep.append(c)
    if _POLARIZABILITY_ROW.search(" ".join(keep)):
        return line                       # a row about the polarizability reads whole, its numbers included
    return " | ".join(keep)


#: THE REFERENCE GRAPH'S POSITION FIELDS ARE NOT VALUES, the same predicate as the private guard's `_GRAPH_POSITION`
#: (private/checks/retired_values.py, 2026-09-25), restated because a mirror has no private/ to import from. The
#: mirror's suite on V7.0's port failed on a quoting site whose line NUMBER shared the retired value's digits.
_GRAPH_POSITION = re.compile(r'^\s*"line":\s*\d+,?\s*$')


def _hits(files, reader, digests=None):
    digests = RETIRED_DIGESTS if digests is None else digests
    out = []
    for f in files:
        try:
            text = reader(f)
        except (OSError, UnicodeDecodeError):
            continue
        graph = f.endswith("reference_graph.json")
        for i, line in enumerate(text.splitlines(), 1):
            if graph and _GRAPH_POSITION.match(line):
                continue
            line = _text_cells(line) if f.endswith(".csv") else line
            if any(hashlib.sha256(form.encode()).hexdigest() in digests
                   for m in TOKEN.finditer(line) for form in _forms(m.group(0))):
                out.append(f"{f}:{i}")
    return out


def test_the_static_tail_polarizability_is_nowhere_but_the_history_record():
    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split()
    files = [f for f in files if not f.endswith(BINARY) and not f.startswith("data_raw/")]
    hits = _hits(files, lambda f: (ROOT / f).read_text(encoding="utf-8", errors="ignore"))
    assert not hits, ("the static-tail Delta-alpha is back in the tracked tree; the value of record is "
                      "results/polarizability_deep.csv and the static one lives in private/history/ alone:\n  "
                      + "\n  ".join(hits[:30]))


def test_the_tripwire_catches_every_form_and_no_float_that_contains_the_digits():
    v = 1100 + 45
    # THE FIXTURE BUILDS THE ONE-DECIMAL FORM FROM THE VALUE, never from a second literal:
    # typed separately it read 11446/10 and its digest went into the register (2026-09-17).
    w = float(v)
    planted = {"a.md": f"gives **-{v} a.u.** (band -1150 to -1139)",
               "b.py": f"OURS_STATIC = -{w:.1f}",
               "c.csv": f"delta_alpha_module,at_drive,-{w:.1f},,a.u.",
               "d.md": f"replacing the earlier \u2212{v} a.u.",
               "e.csv": f"0,0.012,agilent_3054a,hires,16,false,5,2,-4.73{v}e+00,6.009e-01",
               "f.csv": f"1.005332269251{v},2000,120.83",
               "g.md": "the dynamic sum, -1131.8 a.u.",
               "h.md": f"a count of {v} lines",
               "i.csv": f"wide_dchi2,5|15,{v}.4,delta chi2 (raw),DIAGNOSTIC"}
    hits = _hits(list(planted), lambda f: planted[f])
    assert sorted(h.split(":")[0] for h in hits) == ["a.md", "b.py", "c.csv", "d.md", "h.md"], hits


def test_a_graph_position_is_not_a_value_and_a_quoted_value_still_is():
    """Both ways, on a stand-in digest (no test prints the retired value): a graph line that is only a line number equal
    to the digits passes, and the same digits quoted as a value in the graph are still a hit."""
    fake = {hashlib.sha256(form.encode()).hexdigest() for form in _forms("12345")}
    graph = '{\n "k": {\n  "file": "x.md",\n  "line": 12345,\n  "writes": "12345"\n }\n}\n'
    hits = _hits(["docs/reference_graph.json"], lambda f: graph, digests=fake)
    assert hits == ["docs/reference_graph.json:5"], hits

