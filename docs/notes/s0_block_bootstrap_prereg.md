# Preregistration: the block bootstrap of the power-lever profile limit

Status: pre-registered 2026-08-07, before any bootstrap number was
computed. The construction below is frozen together with the script
that implements it (`scripts/run_s0_block_bootstrap.py`), in the same
commit.

`provenance: NO_PRODUCER` - The producer's own docstring says it writes "one row per resample to private/run_logs/, nothing into results/", DIAGNOSTIC until this postscript adjudicated. **The postscript adjudicated and nothing was promoted.** So the outcome numbers (0.262 MHz, the factor 2.4, 41.6 per cent railed, the 0.634 median with its range) reproduce from retained raw rows in a gitignored log and have no committed home. **The factor 2.4 also reached `docs/RESULTS.md` as a literal in the ledger generator**, which is now stated there. **6 numeric claims on this page remain unaccounted for.** Recorded by an audit that read every numeric claim on this page against `results/` and `scripts/`. See `docs/HISTORY.md`.


## What this answers, and what it can break

The ledger's C-item on the power-lever bound states its own gap: the
profile threshold `2.706 x max(chi2_red, 1)` carries the block-to-block
over-dispersion into the bound "conservatively, though as one global
factor", and "a block bootstrap of the profile limit would be the
sharper construction, and it is not run on the archive". This note runs
it. The run can FALSIFY the committed wording: if the bootstrap bound
comes out above the committed profile bound, then the global-factor
treatment was not conservative and the word falls, by addendum, at
three sites (the `rb5s6s/stark.py` docstring, the `run_stark_sweep`
console text, the ledger sentence).

## The construction, fixed

Data: the committed 20-cell grid (4 peaks x 5 powers) from
`results/power_sweep.csv`, exactly as `run_stark_sweep` reads it.
Model and fitter: `rb5s6s.stark.fit_stark_sweep`, unchanged.

Resampling: STRATIFIED BY PEAK. Each resample draws, for every peak
independently, five cells with replacement from that peak's five power
cells. Stratification keeps every per-peak nuisance identified in
every resample. B = 1000 resamples, seed 20260807, both frozen here.

Estimators, two, with distinct roles:

1. PRIMARY, the percentile bound: for each resample, the fitted
   `kappa_hat` (the minimizer, profile machinery off). The bootstrap
   bound is the 95th percentile of the `kappa_hat` distribution,
   quoted as S0(225 mW) = 0.225 x kappa. Rail-safe by construction
   (resamples railing at kappa = 0 enter the distribution as zeros).
2. SECONDARY, diagnostic only: for each of the first B2 = 200
   resamples, the RAW profile bound at threshold 2.706 UNSCALED (the
   resampling now carries the dispersion the global factor stood in
   for). Reported as the median and interquartile range of the bound
   distribution. Not the headline under this preregistration.

Comparison target: the committed `S0_225_ub95_profile` read from
`results/stark_sweep.csv` at run time. No number is hand-typed.

Output: `private/run_logs/s0_block_bootstrap.csv` (one row per
resample) plus a printed summary. DIAGNOSTIC standing until the
postscript adjudicates. Nothing enters `results/` or any document
before the predictions are scored.

## Predictions, scored before anything is written

- P1 (direction): the primary bootstrap bound lies AT OR BELOW the
  committed profile bound. This is what "conservative" predicts.
- P2 (the falsifier): if the primary bound EXCEEDS the committed
  bound, the conservatism wording is wrong at the three sites named
  above and is corrected by a dated addendum. A bound that survives
  on a wrong mechanism is not kept on it.
- P3 (structure): at least half of the resamples rail at
  kappa_hat = 0, consistent with the committed null (best fit at the
  rail, width handle ~S0^2 with zero gradient there).

## Stop conditions

- More than 10 per cent of resamples fail to converge: stop, nothing
  quoted, diagnose the fitter under resampling before any rerun.
- A pilot of B = 20 projecting more than 12 hours of runtime: B2 may
  be reduced (secondary only) and the reduction recorded here by
  amendment. The primary B = 1000 does not shrink.

## What is NOT claimed

The bootstrap does not replace the committed bound in this
preregistration. Whether it becomes a companion number, a replacing
construction, or a recorded diagnostic is the postscript's decision,
taken against P1-P3 with the numbers on the table.

## Postscript, 2026-08-07: run complete, predictions scored

Run integrity: 1000 of 1000 resamples converged, zero failures (stop
condition 10 per cent, did not fire), 23.8 minutes, seed as frozen.

- P1 HOLDS. The primary percentile bound is S0(225 mW) = 0.262 MHz
  at the 95th percentile of the resampled minimizers, against the
  committed profile bound of 0.632 MHz. The committed construction is
  conservative relative to the empirical percentile bound, by a
  factor of 2.4.
- P2 DOES NOT FIRE. The conservatism wording stands unchanged at its
  three sites.
- P3 FAILS, and is recorded as failed. 41.6 per cent of resamples
  rail at kappa = 0 against the predicted at-least-half. The
  committed fit rails, but under block resampling the minimizer
  leaves the rail in a majority of resamples: the rail is a feature
  of the point estimate, not of the resampling distribution's bulk.
- The secondary diagnostic is the run's sharpest result: the median
  raw-profile bound under resampling (unscaled 2.706 threshold) is
  0.634 MHz with interquartile range 0.607 to 0.723, and the
  committed over-dispersion-scaled bound is 0.632. The global factor
  lands where the empirical block-level dispersion puts the median,
  so the committed construction is not only conservative against the
  percentile estimator but calibrated at the median of the sharper
  one it stood in for.

Disposition, per the preregistration's own scope clause: the
bootstrap is RECORDED AS A DIAGNOSTIC. The committed bound stays the
quoted construction, now carrying the validation this run supplies.
The numerical proximity of the percentile bound (0.262) to the joint
three-session headline bound (0.26) is a coincidence of scale
between different constructions on different data, recorded without
interpretation. Output of record:
private/run_logs/s0_block_bootstrap.csv, 1000 rows.
