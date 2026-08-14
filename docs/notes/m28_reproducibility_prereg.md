# The full-archive fit re-run on identical inputs: specification before code

Status: pre-registered 2026-08-05, before the run. This note is committed
with the v3.4.0 release and the run launches after it, so the inputs are the
release's own committed tables and the record shows the rule before the
outcome.

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
outcome feeds the frequency-calibration review's RT6 (block combination)
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

A PRECISION THIS NOTE OWES ITS OWN SECTION 1. That section says the subset
variants "run without such a seed", which reads as though they are separately
run cold profiles. They are not. `run_full_archive_fit.py` computes them as
`ub95(prof_a, col=2)` and `ub95(prof_a, col=3)`, partial-chi-squared columns of
the SAME seeded profile the primary bound is read from at `col=1`. So the
seeding and the pointwise-minimum discipline protect the TOTAL, and what has
no protection of its own is the SPLIT of that total between sessions. Section
1's instinct was right and its mechanism was loose.

Identical data, changed code, primaries exact, unseeded subsets moved by a
third. A changed constant or a changed model would have moved the primary too.
What moves only the poorly conditioned quantities is the optimizer path.

So section 1's seeded-twin discipline gap, which the first postscript said had
lost its urgency, HAS ITS URGENCY BACK, and on a second axis: the variants are
sensitive not only to their own inputs but to the path the optimizer takes to
them. The remedy is unchanged and is now better motivated, which is to seed the
subset variants the way the primary is seeded. Until that is done the subset
spread is a robustness range of about 30 per cent resolution rather than a set
of separately quotable limits, and `docs/RESULTS.md` C3f says so.

No committed CSV is rewritten and no primary bound moves.
