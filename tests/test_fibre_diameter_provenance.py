"""A producer may not read a guided quantity solved at another diameter.

WHY THIS FILE EXISTS, AND IT IS THE SIXTH INSTANCE OF ONE CLASS.

`results/onf_candidate.csv` is solved on a **400 nm** fibre. Two other
producers, `run_campaign_twin_forecast` and `run_onf_lever_ranking`, declare
**370 nm** and read rows out of that file. Every guided quantity -- the
effective index, the decay length, both mode areas, the intensity at the
atom, the transit band -- is a function of the diameter, so a row carried
across that boundary is a number from the wrong fibre wearing the right name.

It happened. `run_campaign_twin_forecast` read the 400 nm transit band into
its 370 nm arm and committed `lorentzian_excess_truth = 0.08668` where its
own fibre gives **0.06694**, an error of 29.5 per cent in a committed row.
`run_onf_lever_ranking` carried the 400 nm light-shift area the same way.

**NO EXISTING GUARD COULD FIRE ON EITHER.** `verify_results_fresh` re-runs
each producer and compares it against itself, so a producer that consistently
reads the wrong file is consistently green. The reference checker resolves
that a row EXISTS, never that it was solved at the geometry naming it. The
suite has no notion of which fibre a number came from.

WHAT THIS CHECKS, and it is deliberately narrow.

For every `scripts/run_*.py` that declares a fibre diameter, every quantity
name it mentions that also appears in ANOTHER fibre producer's committed CSV
must be diameter-INDEPENDENT. Cell and MOT quantities cross freely; guided
ones do not. The diameter-dependent set is named by prefix below rather than
inferred, because inferring it is what the failing code already did.

WHAT IT DOES NOT CHECK. It cannot see a number retyped into prose, or a
guided quantity computed inline instead of read. Those are the reference
checker's population and the producer-note guard's, and this one says so
rather than implying a coverage it lacks.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"

#: Substrings marking a quantity as a function of the fibre diameter. A row
#: whose name contains any of these is solved on one specific fibre.
GUIDED_MARKERS = (
    "neff", "decay", "mode_area", "stark_area", "effective_area",
    "intensity_onf", "intensity_at_", "s0_onf", "transit_onf",
    "guided_", "evanescent", "flux_fraction", "stark_fraction",
    "atoms_in_", "teeth_per_transit_onf", "two_photon_rate_onf",
)

#: How a producer states the fibre it solves.
_DIAMETER = re.compile(
    r"^(?:DIAMETER_NM|PROFILE_DIAMETER_NM|ONF_DIAMETER_NM)\s*=\s*([0-9.]+)",
    re.M,
)
_RADIUS = re.compile(r"^FIBER_RADIUS_NM\s*=\s*([0-9.]+)", re.M)


def _is_guided(quantity: str) -> bool:
    q = quantity.lower()
    return any(m in q for m in GUIDED_MARKERS)


def _declared_diameters(text: str) -> set[float]:
    """Every fibre diameter in nm a producer states, radii doubled."""
    out = {float(v) for v in _DIAMETER.findall(text)}
    out |= {2.0 * float(v) for v in _RADIUS.findall(text)}
    return out


def _fibre_producers() -> dict[str, tuple[set[float], str]]:
    """Producers that solve a guided mode, by stem -> (diameters, source)."""
    found = {}
    for path in sorted(SCRIPTS.glob("run_*.py")):
        text = path.read_text()
        if "solve_he11" not in text and "HE11Field" not in text:
            continue
        diameters = _declared_diameters(text)
        if diameters:
            found[path.stem] = (diameters, text)
    return found


def _committed_quantities(stem: str) -> dict[str, str]:
    """The quantity column of the CSV a producer writes, if it is committed."""
    csv_path = RESULTS / f"{stem.removeprefix('run_')}.csv"
    if not csv_path.exists():
        return {}
    with csv_path.open() as handle:
        return {
            row["quantity"]: row.get("value", "")
            for row in csv.DictReader(handle)
            if row.get("quantity")
        }


def test_the_population_is_not_empty():
    """A guard whose population is empty reports a zero that means nothing.

    This project has shipped exactly that twice, so the population is
    asserted before the property is.
    """
    producers = _fibre_producers()
    assert len(producers) >= 3, (
        f"expected at least three fibre producers, found {sorted(producers)}; "
        "either the detection pattern broke or the producers were renamed, "
        "and in both cases the check below is measuring nothing")
    diameters = {d for ds, _ in producers.values() for d in ds}
    assert len(diameters) >= 2, (
        f"every fibre producer declares the same diameter {diameters}, so no "
        "cross-diameter read is possible and this guard cannot fire")


def test_some_committed_quantity_is_recognised_as_guided():
    """The marker list actually matches the record's own naming."""
    guided = [
        q
        for stem in _fibre_producers()
        for q in _committed_quantities(stem)
        if _is_guided(q)
    ]
    assert len(guided) >= 5, (
        f"GUIDED_MARKERS matched only {guided} across every fibre CSV, so a "
        "cross-diameter read would pass unseen")


@pytest.mark.parametrize("stem", sorted(_fibre_producers()))
def test_no_producer_reads_a_guided_row_from_another_diameter(stem):
    """The property this file exists for."""
    producers = _fibre_producers()
    mine, text = producers[stem]

    offences = []
    for other, (theirs, _) in producers.items():
        if other == stem or theirs == mine:
            continue
        for quantity, value in _committed_quantities(other).items():
            if _is_guided(quantity) and f'"{quantity}"' in text:
                offences.append(
                    f"{quantity} = {value}, solved at {sorted(theirs)} nm in "
                    f"results/{other.removeprefix('run_')}.csv")

    assert not offences, (
        f"scripts/{stem}.py declares a fibre of {sorted(mine)} nm and names "
        f"{len(offences)} guided quantity/quantities solved on a different "
        "fibre:\n  " + "\n  ".join(offences) + "\n"
        "A guided quantity is a function of the diameter. Solve it on this "
        "producer's own fibre with rb5s6s.fibre, or read it from a producer "
        "that declares the same diameter.")
