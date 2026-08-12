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
import re
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
# RECALIBRATED 2026-08-11. The 2026-07-29 spreads above were measured across
# numpy versions that all shared ONE np.convolve implementation. numpy 2.5
# replaced it (measured on this machine: 10x faster on the 9000-point
# convolution this whole lineshape model is built from), and a different
# algorithm rounds differently. Re-measured across numpy 1.26.4, 2.0.2 (the
# environment the committed CSVs were produced in) and 2.5.2, the largest
# well-conditioned drift is 1.2e-2. 5e-3 no longer covers that.
#
# 2e-2 is chosen against what the guard is FOR. Its own note says a real change
# to rb5s6s.stark moves these by tens of percent, so 2e-2 keeps a factor of 5
# to 50 of margin against a change that means something, while sitting above
# arithmetic that means nothing. The STRING skeleton comparison stays exact,
# which is where this check's real sharpness lives.
NUMERIC_RTOL = 2e-2

# One column cannot hold any fixed tolerance, and it is worth naming rather
# than hiding in the default: dBIC is a DIFFERENCE of two BICs of order 1e4, so
# cancellation multiplies a 1e-15 input perturbation by ~1e4. Observed 1.4e-1
# across the three numpy versions. The conclusion it carries does not move:
# |dBIC| < 2 is "no preference between Voigt and Lehmann" and it reads 0.38 to
# 0.44 everywhere.
# Measured on 2026-08-11 by re-running all 16 producers under numpy 2.5.2 and
# recording EVERY differing column rather than the first (_differs returns on
# the first, which is right for a guard and useless for calibrating one). Of
# 2421 columns that moved at all, exactly SIX moved by more than 2e-2, and they
# belong to only two families. Both are quantities this record already declines
# to quote, which is the reassuring part: the arithmetic is unstable precisely
# where the physics was already declared unidentifiable.
_COLUMN_RTOL = {
    # THE DEGENERATE SPLIT. full_gauss and full_exp are the Gaussian and
    # exponential widths of the three-component "full" model form, fitted
    # against a total width that constrains only their combination. This is
    # the degeneracy docs/RESEARCH_DECISIONS.md 1 refuses to quote as physics
    # and fig10 exists to draw: the split moves freely along the direction the
    # observable does not see, so a different rounding of the same convolution
    # lands it somewhere else on the same contour. Observed 1.3e-1; the total
    # width and chi2_full, which ARE well conditioned, move by under 5e-3 in
    # the same runs and keep the default.
    "full_gauss": 0.25,
    "full_exp": 0.25,
    # CATASTROPHIC CANCELLATION. dBIC is a difference of two BICs of order 1e4,
    # so a 1e-15 perturbation of the profile is multiplied by ~1e4. Observed
    # 1.4e-1 across numpy 1.26.4, 2.0.2 and 2.5.2. The conclusion it carries
    # does not move: |dBIC| < 2 is "no preference between Voigt and Lehmann",
    # and it reads between 0.38 and 0.93 everywhere.
    "dBIC_voigt_minus_lehmann": 0.30,
}

# WHETHER A CELL IS ZERO IS A QUESTION ABOUT ITS COLUMN, not about an absolute
# constant. ruler_traces h_m2 runs from 7.7e-37 to 0.31 with a median of 4e-3,
# and 8.7 per cent of its rows sit below 1e-10: those are comb teeth that are
# ABSENT, railed to zero by the fit, whose remaining digits are optimizer noise
# and carry no information. Comparing two of those relatively is meaningless.
#
# A global floor cannot express that. Set it low (1e-20) and absent teeth still
# read as disagreements; set it high (1e-10) and the blackbody channel rates,
# which are genuinely of order 1e-12 per second, get silently declared zero.
# So the floor is RELATIVE TO THE COLUMN'S OWN SCALE: a cell smaller than this
# fraction of its column's median magnitude is not a small measurement, it is
# a zero.
ZERO_FRACTION_OF_COLUMN = 1e-6


def _column_scales(rows: list[dict]) -> dict:
    """Median absolute value per numeric column, for the zero test above."""
    import statistics
    out = {}
    for k in (rows[0] if rows else {}):
        vals = []
        for r in rows:
            try:
                f = abs(float(r.get(k, "")))
            except (TypeError, ValueError):
                continue
            if f > 0.0:
                vals.append(f)
        if vals:
            out[k] = statistics.median(vals)
    return out


def _same_but_for_numbers(a: str, b: str, rtol: float) -> bool:
    """True when two strings differ only in embedded numbers, within rtol.

    The skeleton (everything that is not a number) must match EXACTLY, so a
    renamed field or a changed formula still fails. Only the numbers are
    allowed to drift, and only by the same tolerance a numeric column gets.
    """
    num = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
    if num.sub("#", a) != num.sub("#", b):
        return False
    na, nb = num.findall(a), num.findall(b)
    if len(na) != len(nb):
        return False
    for x, y in zip(na, nb):
        fx, fy = float(x), float(y)
        if fx == fy:
            continue
        if abs(fx - fy) > rtol * max(abs(fx), abs(fy), 1e-300):
            return False
    return True


def _differs(committed: list[dict], fresh: list[dict], rtol: float = NUMERIC_RTOL):
    """Return a short description of the first meaningful difference, or None."""
    if len(committed) != len(fresh):
        return f"row count {len(committed)} committed vs {len(fresh)} fresh"
    scales = _column_scales(committed)
    for i, (a, b) in enumerate(zip(committed, fresh)):
        keys = (set(a) | set(b)) - {"status"}      # annotator adds status last
        for k in sorted(keys):
            va, vb = a.get(k, ""), b.get(k, "")
            if va == vb:
                continue
            col_rtol = _COLUMN_RTOL.get(k, rtol)
            try:
                fa, fb = float(va), float(vb)
            except (TypeError, ValueError):
                # A NUMBER INSIDE A STRING is still a number. sharing_bic's
                # "unit" column embeds its own effective sample size, as
                # "...k=241, N_eff=13853", so an N_eff that moved by 2 in
                # 13853 failed an EXACT string comparison and read as a stale
                # label. Compare the words exactly and the embedded numbers
                # numerically, which keeps the sharp edge this check relies on
                # (a changed label still fails) without pretending a count is
                # text. The proper fix is for that producer to write N_eff as
                # its own numeric column; until then this stops a schema
                # defect from masquerading as a reproducibility failure.
                if _same_but_for_numbers(va, vb, col_rtol):
                    continue
                return f"row {i} column {k!r}: committed {va!r} vs fresh {vb!r}"
            zero = scales.get(k, 0.0) * ZERO_FRACTION_OF_COLUMN
            if abs(fa) <= zero and abs(fb) <= zero:
                continue                      # both zero, for this column
            scale = max(abs(fa), abs(fb))
            if scale == 0.0:
                continue
            if fa != fb and abs(fa - fb) > col_rtol * scale:
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
