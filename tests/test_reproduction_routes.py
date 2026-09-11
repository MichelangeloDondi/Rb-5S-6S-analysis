"""Every producer of a committed CSV has a named route, and the debt ratchets.

Escape E44 shipped `run_kernel_inhomogeneity.py` and its committed CSV routed by
neither `scripts/run_all.sh`'s stage loop nor `docs/REPRODUCING.md`, so the page
whose whole purpose is to route a stranger to every committed number routed them
to that one by no path at all. It RECURRED one wave later, and the rule file is
explicit about what a recurrence is owed: a mechanism that makes it impossible,
not a rule that forbids it.

The board that found the recurrence named two producers. **Counted, the class is
thirty-two**, which is the difference between repairing the name last found
missing and repairing the population. So the baseline below is a LIST and the
assertion is a subset one: a thirty-third unrouted producer cannot appear, and
routing one of the thirty-two fails the staleness test with the instruction to
reseed rather than passing quietly.

The population is read from `results/README.md`, which carries one row per
committed CSV naming the producer that writes it. That file is the repository's
own index and is guarded elsewhere; here it is the population, so this module
asserts the parse found a producer for EVERY tracked CSV before it asserts
anything about routes. A guard whose population silently shrinks was 42 per cent
of one board's findings, and this is the cheapest place to stop it.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

#: Producers of a committed CSV with no named route, measured 2026-09-11.
#: **This is a debt, not an allowance.** Each entry is a producer a stranger
#: cannot reach from either list; the runner holds them out for runtime, and the
#: reproduction page does not name them. Routing one means deleting its line
#: here with the reason in the commit message.
UNROUTED_BASELINE = frozenset({
    "make_twin_term_census",
    "run_band_excess",
    "run_centre_fisher",
    "run_cooperative_channel",
    "run_coverage_grid",
    "run_cumulant_window_check",
    "run_estimator_duel",
    "run_fit_window_scan",
    "run_kernel_budget",
    "run_kernel_headline",
    "run_kernel_identifiability",
    "run_kernel_k3",
    "run_kernel_k4",
    "run_kernel_k7",
    "run_kernel_k8",
    "run_kernel_worlds",
    "run_laser_kernel",
    "run_noise_floor_scaling",
    "run_onf_candidate",
    "run_orthogonal_levers",
    "run_prediction_band",
    "run_quantisation_check",
    "run_quantisation_crosscheck",
    "run_sweep_linearity",
    "run_three_channel_forecast",
    "run_twin_closed_loop",
    "run_twin_realism",
    "run_twin_span_sweep",
    "run_unregenerated_claims",
    "run_waist_ladder",
    "run_window_attribution",
    "run_zeeman_depletion",
})


def tracked_result_csvs(root: Path) -> list[str]:
    """The committed CSV file names under `results/`, from git and not a glob.

    A glob would count an uncommitted stray, which is the fourth of the rule
    file's five ways a file is ungraded while looking graded.
    """
    out = subprocess.run(["git", "-C", str(root), "ls-files", "results"],
                         capture_output=True, text=True, check=True).stdout
    return sorted({Path(p).name for p in out.split() if p.endswith(".csv")})


def producer_of_each_csv(root: Path) -> dict[str, str]:
    """CSV file name -> producer stem, read from `results/README.md`'s table.

    A row may name several CSVs, and a producer cell may carry arguments after
    the script name, so the parse takes the FIRST script named in the row's
    second cell and matches a CSV by its backticked name anywhere in the row.
    """
    rows = [line for line in (root / "results" / "README.md")
            .read_text(encoding="utf-8").splitlines() if line.startswith("|")]
    found: dict[str, str] = {}
    for name in tracked_result_csvs(root):
        for line in rows:
            if f"`{name}`" not in line:
                continue
            cells = line.split("|")
            if len(cells) < 3:
                continue
            m = re.search(r"`([A-Za-z0-9_]+)\.py", cells[2])
            if m:
                found[name] = m.group(1)
            break
    return found


def routed_names(root: Path) -> set[str]:
    """Producer stems a reader can reach: the runner's loop, or the page."""
    sh = (root / "scripts" / "run_all.sh").read_text(encoding="utf-8")
    loop = sh.split("for s in ", 1)[1].split("; do", 1)[0]
    names = set(re.findall(r"[A-Za-z0-9_]*run_[a-z0-9_]+", loop))
    page = (root / "docs" / "REPRODUCING.md").read_text(encoding="utf-8")
    names |= set(re.findall(r"`([A-Za-z0-9_]+)\.py`", page))
    return names


def unrouted(root: Path) -> set[str]:
    """Producers of a committed CSV that neither list names."""
    routed = routed_names(root)
    return {p for p in producer_of_each_csv(root).values() if p not in routed}


def test_the_population_covers_every_committed_csv():
    """The index names a producer for every tracked CSV, or this guard is blind.

    Its own first run found nine CSVs apparently unindexed, every one of them a
    parse artefact: rows naming several files at once, and one producer that is
    not a `run_` script. A confident negative is a claim about the normalisation
    until it survives this check.
    """
    csvs = tracked_result_csvs(ROOT)
    found = producer_of_each_csv(ROOT)
    assert csvs, "no committed results CSVs found; the population is empty"
    missing = sorted(set(csvs) - set(found))
    assert not missing, (
        f"{len(missing)} committed CSV(s) carry no producer in "
        f"results/README.md's table, so this guard cannot see them: {missing}")


def test_no_new_producer_of_a_committed_csv_is_unrouted():
    """A thirty-third unrouted producer fails here, which is E44's mechanism."""
    new = sorted(unrouted(ROOT) - UNROUTED_BASELINE)
    assert not new, (
        f"{len(new)} producer(s) of a committed CSV are reachable from neither "
        f"scripts/run_all.sh's stage loop nor docs/REPRODUCING.md: {new}. "
        "Name them in one of the two, or add them to UNROUTED_BASELINE with "
        "the reason in the commit message. Escape E44 is this defect twice.")


def test_the_route_debt_baseline_is_not_stale():
    """Routing one of the thirty-two must move the baseline, not pass quietly."""
    paid = sorted(UNROUTED_BASELINE - unrouted(ROOT))
    assert not paid, (
        f"{len(paid)} producer(s) gained a route and the baseline still lists "
        f"them: {paid}. Remove them from UNROUTED_BASELINE; a ratchet that is "
        "not reseeded stops measuring the debt it exists to shrink.")


@pytest.mark.parametrize("producer", sorted(UNROUTED_BASELINE))
def test_every_baselined_producer_still_exists(producer):
    """A deleted producer left in the baseline would hide a real regression."""
    candidates = list((ROOT / "scripts").glob(f"{producer}.py"))
    assert candidates, (
        f"{producer}.py is in UNROUTED_BASELINE and not in scripts/; a stale "
        "baseline entry masks the next unrouted producer that takes its place.")
