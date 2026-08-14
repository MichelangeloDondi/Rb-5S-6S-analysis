# Reproducing the committed results

What runs from a clone, what needs the raw traces, and how the committed
numbers are held to the files that produce them. The short version is on the
front page under Reproduce. This is the detail behind it.

## What a clone can run

The dataset's manifest is committed, and the 297 raw traces are held
privately. Most of the battery does not need them: the certification suite
and the clock-dependent results run from a clone as they stand. **On the raw
traces** in the README says exactly where the boundary falls.

With the traces in place, `bash scripts/run_all.sh` executes every stage in
dependency order, then the figures, `docs/RESULTS.md`, and the CSV status
column. Each stage reads the previous stages' output in `results/`, and
re-running any stage reproduces its committed CSV within the tolerance
`scripts/verify_results_fresh.py` states.

That comparison is a stated tolerance rather than byte equality because the
arithmetic depends on the numerical environment. The committed digits were
produced under numpy 2.0.2 and hold across numpy 2.0 to 2.4. On the declared
floor of numpy 2.5 the two quoted bounds move in their last digit, 0.963 to
0.959 MHz/W and 0.217 to 0.216 MHz, while every quantity read as physics is
identical to the printed digit.
[`results/ENVIRONMENT_OF_RECORD.md`](../results/ENVIRONMENT_OF_RECORD.md)
gives the versions, the per-column sizes and the reasoning.

One committed number sits outside `run_all.sh`. The joint three-session
AC-Stark bound is a long profile-likelihood run with its own script,
`python scripts/run_stark_joint.py`, and it also needs the raw rehearsal and
pilot trees, which stay outside the repository.

## The clock-dependent results reproduce from a clone

The lock-drift measurement and its audit trail
([`PREREGISTRATION_RESULTS.md`](PREREGISTRATION_RESULTS.md) addenda 4 to 7)
need no raw traces: the acquisition clock is committed as
[`data_recovered/CLOCK.csv`](../data_recovered/CLOCK.csv), and

```bash
python scripts/run_drift_settling.py  # the drift analysis, off the committed clock
python scripts/run_laser_history.py   # laser frequency, within each display epoch
```

print the full report, because the per-trace QC metrics they read
(`results/qc_metrics.csv`) are committed. The complete timestamped raw backup
behind the clock is preserved verbatim with the traces, its sha256 recorded
in the audit report.

## How a quoted number is held to its source

The headline numbers are cited across many documents.
`tests/test_docs_canonical.py` holds each in a single registry, reads its true
value from the committed CSV, and checks that every document quotes *that*
value, so a re-analysis that moves a number cannot leave a stale copy behind.

The figures follow the same rule. `make_figures.py` stamps a fingerprint of
the results CSVs into each PNG, and `tests/test_figures_fresh.py` fails if a
committed figure was drawn from stale results. The check reads a hash in the
PNG, not pixels, so it is independent of the matplotlib version that drew the
figure.

Both exist because the alternative was found by experience: a number corrected
in one document and left standing in four others.
