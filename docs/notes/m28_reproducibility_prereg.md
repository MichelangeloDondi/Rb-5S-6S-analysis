# The full-archive fit re-run on identical inputs: specification before code

Status: pre-registered 2026-08-05, before the run. This note is committed
with the v3.4.0 release and the run launches after it, so the inputs are the
release's own committed tables and the record shows the rule before the
outcome.

`provenance: NO_PRODUCER` - Reported at medium confidence by the audit that found it. The outcome numbers were not traced to any committed row, and the next reader should treat this declaration as the current best account rather than as settled. **5 numeric claims on this page remain unaccounted for.** Recorded by an audit that read every numeric claim on this page against `results/` and `scripts/`. See `docs/HISTORY.md`.


## 1. The observation that forces the question

Between the 2026-08-04 committed run and the 2026-08-05 recompute of the
full-archive joint fit, the primary Stark bound moved by 0.1 per cent and
the wing and drop-one variants by under 1 per cent, while the two subset
robustness variants moved by a quarter and a third, both loosening:

| variant | committed | recomputed |
|---|---|---|
| campaign rows only | 0.639 | 0.864 |
| power-ladder rows only | 0.696 | 0.874 |

The input change between those runs was the recalibrated ruler table, whose
campaign rate moved by 0.0007 per cent, three orders too small to explain a
third of a bound. Two explanations remain and they cannot be told apart
from the existing record.

The first is that the subsets genuinely respond to the calibration in a way
the full archive does not. The second is optimizer chain variation: these
are profile likelihoods whose hysteresis is the reason no cold-start profile
is quoted without a twin seeded from the best known local minimum, a subset has fewer
points holding the chain in place, and the subset variants run without such a
seed.

## 2. The test

One further run of `scripts/run_full_archive_fit.py`, complete and
unmodified, on inputs bit-identical to the v3.4.0 release commit. No code
change, no seed change, no configuration change. Identical inputs remove
the first explanation by construction, so whatever moves is the chain.

## 3. Decision rule, fixed here

A quantity reproduces if its second value lies within 3 per cent of its
first. The threshold sits far below the observed 26 and 35 per cent moves
and far above the sub-0.1-per-cent numerical scatter of the primary bound
across the existing runs.

* Both subset variants reproduce, and the primary reproduces: the
  2026-08-04 to 2026-08-05 movement was input-driven after all, the subset
  variants keep their point values, and the release documentation gains one
  sentence recording the check.
* Either subset variant fails to reproduce: chain variation is established
  on identical inputs. The subset variants are then quoted as the spread of
  the available runs rather than as points, their description as robustness
  checks is withdrawn until they run with the same seeded twin as the
  primary, and extending that seeding rule to the subset profiles becomes a
  pre-registered code change of its own.
* The primary fails to reproduce: stop. That is a finding about the whole
  fit, it replaces both branches above, and nothing else runs until it is
  settled.

## 4. What is recorded

The run writes its usual table to a scratch path, never over the release's
`results/full_archive_fit.csv`. The comparison lands in this note as a dated
amendment with all three columns, run one, run two, and the fractional
moves, plus the gate values (census, chi-squared per point, local minimum gap,
direction indifference) for both runs side by side.

## 5. Cost and placement

About five hours on this machine, sequential with nothing. It launches after
the v3.4.0 push so that a failure cannot entangle the release, and its
outcome feeds the frequency-calibration audit's RT6 (block combination)
and the M28 documentation, not the release itself.

## Postscript, 2026-08-06: adjudicated, branch one

The identical-input rerun completed 07:12 after a 5.1 hour run. Every
tracked quantity reproduces to the printed digit: the primary kappa
bound 0.9440 to 0.9440, campaign-only 0.8640 to 0.8640, power-ladder
0.8740 to 0.8740, wing-marginalized 0.9590 to 0.9590, drop-4192 1.4210
to 1.4210, and S0(225 mW) 0.2120 to 0.2120, every move 0.00 per cent
against the 3 per cent threshold. Branch one holds: the movement of the
subset variants between the 2026-08-04 and 2026-08-05 recomputes was
input-driven, the recalibration genuinely changed what those subsets
constrain, and it was not chain variance. The subset variants keep
their committed point values and the robustness framing stands. The
seeded-twin discipline gap on the variants, recorded in section 1,
loses its urgency by this result but stays open as written.

## Second postscript, 2026-08-14: the code-path axis this test could not see

The 2026-08-06 result above stands. With the code held fixed at the v3.4.0
release, the fit reproduces every tracked quantity to the printed digit, so
the movement between the 2026-08-04 and 2026-08-05 recomputes was not chain
variance at fixed code.

A second rerun on 2026-08-14 varied the other thing. It executed commit
`b17609c7`, 272 files and about 21,500 insertions later than the release,
while every data input the fit reads stayed byte-identical (`beta_self.csv`,
`qc_metrics.csv` and `ruler_traces.csv` unchanged, and the single changed
`MANIFEST.csv` line is one word inside a QC-reason string on a discarded,
non-canonical row).

All three primary bounds reproduced to the printed digit: `kappa_ub95` 0.944,
`S0_225mW_ub95` 0.212, `S0_270mW_ub95` 0.255. The two single-session subsets
moved by about a third and both tightened: campaign-only 0.864 to 0.557 and
power-ladder 0.874 to 0.617. `basin_gap_max` went from 0.82 to 57.29, still
inside gate B6's threshold of 1000.

A precision this NOTE owes its own section 1. That section says the subset
variants "run without such a seed", which reads as though they are separately
run cold profiles. They are not. `run_full_archive_fit.py` computes them as
`ub95(prof_a, col=2)` and `ub95(prof_a, col=3)`, partial-chi-squared columns of
the same seeded profile the primary bound is read from at `col=1`. So the
seeding and the pointwise-minimum discipline protect the total, and what has
no protection of its own is the split of that total between sessions. Section
1's instinct was right and its mechanism was loose.

Identical data, changed code, the total exact, the split between sessions
moved by a third. A changed constant or a changed model would have moved the
primary too. What moves only the poorly conditioned quantities is the
optimizer path.

> **Third postscript, 2026-08-20: the premise above was wrong and this
> paragraph's conclusion goes with it.** A commit sweep across the range,
> holding one environment, found the joint construction's point count
> changing at exactly one commit, 247783 to 247788 with the trace count
> unchanged at 172. That commit renamed a vocabulary across the tree and
> regenerated the committed ruler CSVs as a side effect, moving fitted ruler
> rates in their eleventh digit, and a frequency axis shifted by that much
> moves a discrete trim boundary across a sample edge so that five samples
> enter. So the data were not identical: byte-identical described the raw
> traces and not the fit's inputs, and this note's own check looked at the
> files it expected to move rather than at the count of what the fit loads.
>
> The code, meanwhile, is bit-stable across the whole range: six commits
> spanning nine days return the same chi-square to the last printed digit at
> a common grid point. "Changed code" is the half of the premise that fails
> hardest.
>
> What survives is the conditioning argument, and it survives intact. A
> perturbation this small moving only the poorly conditioned quantities is
> exactly what the paragraph above says, and it is now the candidate
> amplifier rather than the cause. How much of the reported third five
> samples account for is being measured. See `docs/RESULTS.md` C3f.

So section 1's seeded-twin discipline gap, which the first postscript said had
lost its urgency, has its urgency back, and on a second axis: the variants are
sensitive not only to their own inputs but to the path the optimizer takes to
them. The remedy is unchanged and is now better motivated, which is to seed the
subset variants the way the primary is seeded. Until that is done the subset
spread is a robustness range of about 30 per cent resolution rather than a set
of separately quotable limits, and `docs/RESULTS.md` C3f says so.

No committed CSV is rewritten and no primary bound moves.
