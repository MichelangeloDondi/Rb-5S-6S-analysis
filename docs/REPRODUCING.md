# Reproducing the committed results

What runs from a clone, what needs data that is not in it, and how the
committed numbers are held to the files that produce them. The short version
is on the front page under Reproduce. This is the detail behind it.

## The runner, and the twenty scripts outside it

`bash scripts/run_all.sh` executes 29 analysis stages in dependency order,
then the figures, `docs/RESULTS.md`, and the CSV status column. Re-running any
stage reproduces its committed CSV in `results/` within the tolerance
`scripts/verify_results_fresh.py` states.

That comparison is a stated tolerance rather than byte equality because the
arithmetic depends on the numerical environment. The committed digits were
produced under numpy 2.0.2 and hold across numpy 2.0 to 2.4. A full rerun on
the declared numpy 2.5 floor moved two of the global dataset fit's preliminary
values in their last digit, 0.963 to 0.959 MHz/W and 0.217 to 0.216 MHz, while
the collisional coefficient and the predicted light shift stayed identical to
the printed digit.
[`results/ENVIRONMENT_OF_RECORD.md`](../results/ENVIRONMENT_OF_RECORD.md)
gives the versions, the per-column sizes and the reasoning.

One measured incident calibrates how seriously to take that dependence. On
2026-08-18 the freshness comparison ran in three environments on the same
tree: under the pinned floor dependencies every committed CSV matched its
producer, under a local numpy 2.5.2 and scipy 1.18.0 every CSV matched again,
and on a hosted runner resolving the newest releases two cells drifted, a
chi-square by 5.4 per cent and the model-form probe's `full_exp` by 62 per
cent, the latter beyond even its own widened per-column tolerance. The record
was unchanged in all three runs. The lesson for a reproducer is that
`full_exp` is the tree's most environment-fragile quantity, that a mismatch
under moving dependencies is a property of the environment until the pinned
comparison disagrees, and that the pinned comparison is the one that speaks
for the record.

The runner's stages write 35 of the 63 committed CSVs. The other twenty each
have their own script, held out for one of two reasons.

### Six need trees that stay outside the repository

These do not run from a clone: `run_stark_joint.py` (`stark_joint.csv`, the
joint three-session AC-Stark bound, a long profile-likelihood run that also
reads the raw 4 July and campaign-morning trees), `run_full_dataset_fit.py`
(`full_dataset_fit.csv`, the same construction over the full dataset),
`run_global_dataset_fit.py` (`global_dataset_fit.csv`), `_m25_norulers.py`
(`global_dataset_fit_norulers.csv`) and `run_morning_ruler.py`
(`morning_ruler.csv`). The sixth is `run_commit_sweep.py`
(`commit_sweep.csv`), which counts the samples the joint fit loads at each
commit of a historical range, so it needs the excluded-session trees AND a
git worktree per commit.

Three of those five reach the trees indirectly, importing `run_stark_joint`'s
`load_session_20250704` and `load_session_20250717` rather than reading the environment
variables themselves, which is worth knowing if you are grepping for what
depends on them. Three further scripts outside this thirteen also need the trees
and write no CSV: `build_clock_table.py`, `run_epoch_checks.py`, and
`run_saturation_probe.py` in its opt-in `--joint` stage.

Point `RB5S6S_SESSION_20250704_DIR` and `RB5S6S_SESSION_20250717_DIR` at the trees if you have
them. The fallback path the scripts fall back to is not where they live.

### Seven run from a clone, held out for runtime or as diagnostics

`run_wing_check.py` (`wing_check.csv`, about 6 minutes over the raw traces),
`run_wavemeter_reconstruction.py` (`wavemeter_reconstruction.csv`, digitised
from a tracked photograph), `run_laser_history.py` (`laser_history.csv` and
`laser_history_structure.csv`), `run_stark_centres.py` (`stark_centres.csv`),
`run_centre_stark.py` (`centre_stark.csv`), `run_cavity_scan.py`
(`cavity_scan_integrals.csv`) and `run_tooth_scatter.py`
(`ruler_tooth_scatter.csv`, about a minute refitting every RF-on comb with
free tooth centres, held out because nothing downstream reads its bound).
Three of them read only committed files (the
cavity-scan one integrates the tracked digitisation
`docs/apparatus/2025-06-12_cavity_scan_IMG_2508_digitised.csv`).

Four of the thirteen are still checked without being in the runner:
`tests/test_results_fresh.py` re-runs `run_laser_history.py` and
`run_stark_centres.py` and diffs what they produce against what is committed,
and `tests/test_cavity_scan.py` does the same for `run_cavity_scan.py`.

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
behind the clock is preserved verbatim as the release asset
`raw-backup-2026-07-24` (sha256 in its notes).

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
