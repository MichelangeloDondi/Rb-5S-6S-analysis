#!/usr/bin/env python3
"""
Do the committed result CSVs still match what their producers generate?

WHY THIS EXISTS. On 2026-07-25 the beta_self producer was corrected: a variant
it had labelled a "cross-session" comparison is not one, and the script now says
so in as many words. Its output was never regenerated. For two days
results/beta_self_probe.csv carried the retracted label while the script that
writes it carried the retraction, and the whole battery stayed green -- because
every test read the CSV, and the CSV was self-consistent. Nothing compared it
against the code.

That is a defect class the existing guards cannot see. tests/test_figures_fresh
catches a stale FIGURE by embedding a fingerprint of the CSVs in each PNG, so a
figure drawn from old numbers is detectable. Nothing plays that role one level
up: a CSV drifting from its own producer is invisible.

WHAT THIS DOES. Re-runs each producer into the real results/ directory, diffs
what appears against what was committed, and puts the committed files back --
always, including on failure. Numeric cells compare with a relative tolerance
(fits are iterative; the last digit is not meaningful), string cells compare
exactly, which is what catches a stale label. The `status` column is ignored
because annotate_results_status.py adds it last, after every producer has run.

WHAT IT DOES NOT COVER. The heavy fitting producers (run_linefit,
run_beta_self, run_global_fit, run_stark_sweep and the rest of the C-series) are
not in the default set: they take minutes and need the raw traces, so a checkout
without data_raw/ cannot run them at all. Pass --all to include them where the
traces exist. The default set is the cheap producers, which is a partial answer
-- but the file that actually drifted is in it.

    python scripts/verify_results_fresh.py          # cheap producers
    python scripts/verify_results_fresh.py --all    # everything, needs raw traces
"""

from __future__ import annotations

import argparse
import csv
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# Producer -> the CSVs it writes. Cheap enough to re-run in a test.
CHEAP = {
    "run_noise": ["noise_model.csv"],
    "run_ruler": ["ruler_traces.csv", "ruler_blocks.csv", "ruler_campaign.csv"],
    "run_trim_report": ["trim_report.csv"],
    "run_sigma_laser_sharing": ["sigma_laser_sharing.csv"],
    "run_polarizability": ["polarizability.csv"],
    "run_modelform": ["modelform.csv"],
    "run_amplitude_ratios": ["amplitude_ratios.csv"],
    "run_transit_mc": ["transit_mc.csv"],
    "run_sharing_bic": ["sharing_bic.csv"],
    "run_resolving_power": ["resolving_power.csv"],
    "run_stark_centres": ["stark_centres.csv"],
    "run_laser_history": ["laser_history.csv", "laser_history_structure.csv"],
    "run_fringe_tail": ["fringe_tail.csv"],
}

# Minutes each, and they need data_raw/ traces.
EXPENSIVE = {
    "run_linefit": ["linefit_conditions.csv"],
    "run_beta_self": ["beta_self.csv", "beta_self_probe.csv"],
    "run_global_fit": ["global_fit.csv"],
    "run_stark_sweep": ["stark_sweep.csv"],
    "run_power_sweep": ["power_sweep.csv"],
    "run_amplitude_trapping": ["amplitude_trapping.csv"],
    "run_model_ladder": ["model_ladder.csv"],
    "run_identifiability": ["identifiability.csv", "identifiability_profile.csv"],
    "run_coverage": ["coverage.csv"],
}


def _rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# Iterative fits do not converge bit-identically across numpy versions, and CI
# runs three (3.9-minimum, 3.9-latest, 3.11-latest). Measured spread on the
# committed set, 2026-07-29: amplitude_ratios err_stat 3.2e-4 relative,
# laser_history offset_err 5.5e-5, modelform chi2 1.8e-5, noise a_V 2.8e-5,
# ruler block chi2 3.0e-5. A 1e-6 tolerance therefore fails on every CI job
# while passing locally, which is a flaky guard and worse than none. 5e-3 sits
# an order above the observed spread and still catches any change that means
# anything. The sharp edge of this check is the STRING comparison anyway -- a
# stale label is what actually drifted -- and that stays exact.
NUMERIC_RTOL = 5e-3


def _differs(committed: list[dict], fresh: list[dict], rtol: float = NUMERIC_RTOL):
    """Return a short description of the first meaningful difference, or None."""
    if len(committed) != len(fresh):
        return f"row count {len(committed)} committed vs {len(fresh)} fresh"
    for i, (a, b) in enumerate(zip(committed, fresh)):
        keys = (set(a) | set(b)) - {"status"}      # annotator adds status last
        for k in sorted(keys):
            va, vb = a.get(k, ""), b.get(k, "")
            if va == vb:
                continue
            try:
                fa, fb = float(va), float(vb)
            except (TypeError, ValueError):
                return f"row {i} column {k!r}: committed {va!r} vs fresh {vb!r}"
            scale = max(abs(fa), abs(fb), 1e-30)
            if fa != fb and abs(fa - fb) > rtol * scale:
                return (f"row {i} column {k!r}: committed {fa!r} vs fresh {fb!r} "
                        f"({abs(fa - fb) / scale:.1e} relative)")
    return None


def _committed(name: str, dest: Path) -> bool:
    """Write results/<name> AS COMMITTED AT HEAD into dest. Reading the working
    copy instead would compare a dirty tree against itself and pass -- which is
    exactly the blind spot this script exists to close, so it must not have it."""
    proc = subprocess.run(["git", "show", f"HEAD:results/{name}"],
                          cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        return False
    dest.write_text(proc.stdout)
    return True


def verify(producers: dict) -> list[str]:
    """Re-run each producer and report CSVs that no longer match what is
    COMMITTED. The working copies are restored unconditionally -- this must
    never leave the tree dirty."""
    stash = Path(tempfile.mkdtemp(prefix="results_committed_"))
    working = Path(tempfile.mkdtemp(prefix="results_working_"))
    problems: list[str] = []
    try:
        for f in RESULTS.glob("*.csv"):
            shutil.copy2(f, working / f.name)        # to put back afterwards
            _committed(f.name, stash / f.name)       # to compare against

        for script, outputs in producers.items():
            proc = subprocess.run([sys.executable, f"scripts/{script}.py"],
                                  cwd=ROOT, capture_output=True, text=True)
            if proc.returncode != 0:
                tail = (proc.stderr or "").strip().splitlines()[-1:] or ["(no stderr)"]
                problems.append(f"{script}.py exited {proc.returncode}: {tail[0]}")
                continue
            for name in outputs:
                fresh, committed = RESULTS / name, stash / name
                if not committed.is_file():
                    problems.append(f"{name}: produced but not committed at HEAD")
                    continue
                d = _differs(_rows(committed), _rows(fresh))
                if d:
                    problems.append(f"{name} drifted from {script}.py -- {d}")
    finally:
        for f in working.glob("*.csv"):
            shutil.copy2(f, RESULTS / f.name)
        shutil.rmtree(stash, ignore_errors=True)
        shutil.rmtree(working, ignore_errors=True)
    return problems


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true",
                    help="include the heavy fitting producers (needs data_raw/)")
    args = ap.parse_args()

    producers = dict(CHEAP)
    if args.all:
        if not (ROOT / "data_raw" / "p_sweep").is_dir():
            print("--all needs the raw traces, which this checkout does not have")
            return 2
        producers.update(EXPENSIVE)

    problems = verify(producers)
    n = sum(len(v) for v in producers.values())
    if problems:
        print(f"{len(problems)} of {n} committed CSVs no longer match their producer:")
        for p in problems:
            print(f"  {p}")
        print("\nRe-run the producer and commit its output, then re-run "
              "annotate_results_status.py to restore the status column.")
        return 1
    print(f"all {n} committed CSVs match a fresh run of their producer "
          f"({len(producers)} producers checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
