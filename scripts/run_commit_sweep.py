#!/usr/bin/env python3
"""How many samples the joint fit sees, at each commit of a range.

WHY THIS EXISTS. On 2026-08-14 the record noted that rerunning the joint
light-shift construction under later code moved its campaign-only bound by
about a third, and called it a code-version instability. A sweep on
2026-08-20 found the cause, and the cause is not the code: the fit's POINT
COUNT changes at exactly one commit, 247783 to 247788 with the trace count
unchanged at 172. That commit renamed a vocabulary across the tree and
regenerated the committed ruler CSVs as a side effect, moving fitted rates in
their eleventh digit. A frequency axis shifted by 1e-11 moves a TRIM
BOUNDARY, and a trim is a comparison, so it is discrete: it crosses a sample
edge in a few traces and five samples enter.

WHY THE COUNT AND NOT THE FIT. The point count comes out of the LOADING PATH
before any fitting starts, so a commit costs seconds where a fit costs
three-quarters of an hour. The whole interval resolves in minutes. Localise
with the cheap observable, and spend the fit only at the boundary it finds.

WHAT THIS PRODUCER GUARDS. The numbers above were, when first written, typed
into `make_results_ledger.py` by hand, which is the same defect class the
sweep had just diagnosed: a number with no producer cannot fail when it stops
being true. This script is that producer, and `results/commit_sweep.csv` is
the file the ledger reads.

THE LOADERS WERE RENAMED TWICE inside the range this sweeps, and so were the
environment variables that point at the excluded-session trees, so both are
resolved by trying every name the range used. A commit that cannot find the
trees RETURNS EARLY AND LEAVES ITS COMMITTED CSV IN PLACE, printing "not on
this machine", so its run log is checked before its count is believed.

    python scripts/run_commit_sweep.py                  # the recorded range
    python scripts/run_commit_sweep.py --from A --to B  # any other range
"""

from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# The range the 2026-08-20 sweep resolved, kept as the default so the
# committed CSV reproduces without arguments (rule 19.75).
DEFAULT_FROM = "ac0dac3d~1"
DEFAULT_TO = "a55d6dd6"

# Both generations of the environment variables, and both of the loader
# function names, because the range renames each of them once.
TREE_VARS = ("RB5S6S_" + "PREHISTORY" + "_DIR", "RB5S6S_SESSION_20250704_DIR")
PILOT_VARS = ("RB5S6S_PILOT_DIR", "RB5S6S_SESSION_20250717_DIR")

_COUNTER = '''
import importlib.util
spec = importlib.util.spec_from_file_location("sj", "scripts/run_stark_joint.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
second = next(getattr(m, n) for n in
              ("load_session_20250704", "load_" + "rehearsal", "load_" + "prehistory")
              if hasattr(m, n))
third = next(getattr(m, n) for n in
             ("load_session_20250717", "load_pilot") if hasattr(m, n))
camp = m.load_campaign()
reh, _ = second()
_, rates = m.load_t_rates()
pil = third(rates["4192"][0])
traces = camp + reh + pil
print(sum(len(t["x"]) for t in traces), len(traces))
'''


def _tree_paths() -> tuple[Path, Path] | None:
    """The excluded-session trees, from whichever variable names are set."""
    pre = next((os.environ[v] for v in TREE_VARS if os.environ.get(v)), None)
    pil = next((os.environ[v] for v in PILOT_VARS if os.environ.get(v)), None)
    if not pre or not pil:
        return None
    p, q = Path(pre).expanduser(), Path(pil).expanduser()
    return (p, q) if p.is_dir() and q.is_dir() else None


def count_at(commit: str, trees: tuple[Path, Path], python: str) -> tuple[int, int] | None:
    """Points and traces the joint construction loads at one commit.

    Returns None where the commit's own code cannot reach the trees, which is
    NOT a zero: it means that commit's answer is unknown rather than empty.
    """
    with tempfile.TemporaryDirectory(prefix="rb5s6s-sweep-") as tmp:
        wt = Path(tmp) / "wt"
        add = subprocess.run(["git", "-C", str(REPO), "worktree", "add",
                              "--detach", str(wt), commit],
                             capture_output=True, text=True)
        if add.returncode != 0:
            return None
        try:
            env = dict(os.environ)
            for v in TREE_VARS:
                env[v] = str(trees[0])
            for v in PILOT_VARS:
                env[v] = str(trees[1])
            env["PYTHONPATH"] = str(wt)
            env["OMP_NUM_THREADS"] = "1"
            out = subprocess.run([python, "-c", _COUNTER], cwd=wt, env=env,
                                 capture_output=True, text=True)
            tail = [l for l in out.stdout.strip().split("\n") if l.strip()]
            if not tail or "not on this machine" in out.stdout:
                return None
            parts = tail[-1].split()
            return (int(parts[0]), int(parts[1])) if len(parts) == 2 else None
        finally:
            subprocess.run(["git", "-C", str(REPO), "worktree", "remove",
                            "--force", str(wt)], capture_output=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from", dest="since", default=DEFAULT_FROM)
    ap.add_argument("--to", dest="until", default=DEFAULT_TO)
    ap.add_argument("--python", default=sys.executable)
    args = ap.parse_args()

    trees = _tree_paths()
    if trees is None:
        print("excluded-session tree(s) not on this machine -- the committed "
              "results/commit_sweep.csv is the record; nothing to do.")
        return 0

    rng = subprocess.run(["git", "-C", str(REPO), "rev-list", "--reverse",
                          f"{args.since}..{args.until}"],
                         capture_output=True, text=True)
    commits = [c for c in rng.stdout.split("\n") if c]
    if not commits:
        print(f"no commits in {args.since}..{args.until}")
        return 1

    rows = [["quantity", "key", "value", "err", "unit", "status"]]
    counts: list[tuple[str, int, int]] = []
    for c in commits:
        subj = subprocess.run(["git", "-C", str(REPO), "log", "--format=%h %s",
                               "-1", c], capture_output=True, text=True).stdout.strip()
        got = count_at(c, trees, args.python)
        short = subj.split()[0]
        if got is None:
            print(f"  {subj[:64]:66s} -> unresolved")
            rows.append(["fit_points", short, "", "", f"UNRESOLVED: this "
                         f"commit's code could not reach the trees. {subj}",
                         "DIAGNOSTIC"])
            continue
        pts, ntr = got
        counts.append((short, pts, ntr))
        print(f"  {subj[:64]:66s} -> {pts} points, {ntr} traces")
        rows.append(["fit_points", short, str(pts), "",
                     f"samples entering the joint light-shift fit. {subj}",
                     "DIAGNOSTIC"])
        rows.append(["fit_traces", short, str(ntr), "",
                     "traces entering the same fit", "DIAGNOSTIC"])

    # THE BOUNDARY IS COMPUTED, not asserted. Adjacent pairs are compared in
    # the order git returned them, and only resolved commits take part, so an
    # unresolved commit between two resolved ones widens the pair rather than
    # inventing a change.
    changes = [(a, b) for a, b in zip(counts, counts[1:]) if a[1] != b[1]]
    for (before, pb, _), (after, pa, _) in changes:
        rows.append(["fit_points_boundary", f"{before}->{after}",
                     str(pa - pb), "",
                     "samples gained across this adjacent pair, which is where "
                     "the input set changed", "DIAGNOSTIC"])
        print(f"\nBOUNDARY {before} -> {after}: {pa - pb:+d} samples")
    if not changes:
        print("\nno point-count change across the range")
    rows.append(["fit_points_boundaries", "count", str(len(changes)), "",
                 "adjacent pairs across which the loaded sample count changes",
                 "DIAGNOSTIC"])

    dst = REPO / "results" / "commit_sweep.csv"
    with open(dst, "w", newline="") as fh:
        csv.writer(fh).writerows(rows)
    print(f"wrote {dst.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
