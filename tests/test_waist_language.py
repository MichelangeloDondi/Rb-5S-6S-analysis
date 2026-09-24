"""A retired CONCEPT, not only a retired phrase (the W1j round's reproducibility
finding, 2026-09-14): the results ledger's generator called the lineage waist
"measured" in six places the E76 phrase bank could not see, and the generated
docs/RESULTS.md contradicted itself. The owner's ruling of 2026-09-10 is that the
waist is a working convention; this guard reads every lowercase "measured" near a
waist token in the generator and allows each survivor by its own words."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "make_results_ledger.py"
WAIST = re.compile(r"waist|w_0|\bw0\b|W0_", re.I)
# a lowercase word, so the constant W0_CENTRAL_M (whose docstring says convention) is not a hit
MEASURED = re.compile(r"(?<![A-Za-z_])measured(?![A-Za-z_])")
ALLOWED = {
    "the peak this bound is measured on": "a bound measured on a peak is not a measured waist",
    "measured in situ in the next campaign": "the campaign that measures it, stated as future",
    "would survive to be measured at all": "a peak measured, beside a distance quoted in waists",
}


def _hits():
    flat = " ".join(GENERATOR.read_text(encoding="utf-8").split())
    out = []
    for m in MEASURED.finditer(flat):
        win = flat[max(0, m.start() - 90): m.end() + 90]
        if WAIST.search(win) and not any(a in win for a in ALLOWED):
            out.append(win)
    return out


def test_the_ledger_generator_never_calls_the_waist_measured():
    hits = _hits()
    assert not hits, ("the results ledger's generator calls the waist measured; the owner's ruling is that it is a convention "
                      "(E76). Reword, or allow the exact words in ALLOWED with a reason:\n  " + "\n  ".join(hits))


def test_the_guard_sees_a_planted_measurement_claim(tmp_path, monkeypatch):
    """The plant: a sentence of the retired shape inserted into a copy of the generator fires."""
    src = GENERATOR.read_text(encoding="utf-8") + "\n# the width at the measured waist\n"
    fake = tmp_path / "gen.py"; fake.write_text(src, encoding="utf-8")
    monkeypatch.setattr("tests.test_waist_language.GENERATOR", fake, raising=False)
    import tests.test_waist_language as me
    monkeypatch.setattr(me, "GENERATOR", fake)
    assert me._hits(), "the planted claim was not seen"
