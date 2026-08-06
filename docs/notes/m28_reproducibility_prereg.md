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
are profile likelihoods whose hysteresis is the reason the seeded-twin
basin discipline exists, a subset has fewer points holding the chain in
place, and the subset variants run outside that discipline.

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
  checks is withdrawn until they run under the same seeded-twin basin
  discipline as the primary, and extending that discipline to the subset
  profiles becomes a pre-registered code change of its own.
* The primary fails to reproduce: stop. That is a finding about the whole
  fit, it supersedes both branches above, and it goes to the owner before
  anything else runs.

## 4. What is recorded

The run writes its usual table to a scratch path, never over the release's
`results/full_archive_fit.csv`. The comparison lands in this note as a dated
amendment with all three columns, run one, run two, and the fractional
moves, plus the gate values (census, chi-squared per point, basin gap,
direction indifference) for both runs side by side.

## 5. Cost and placement

About five hours on this machine, sequential with nothing. It launches after
the v3.4.0 push so that a failure cannot entangle the release, and its
outcome feeds the frequency-calibration red team's RT6 (block combination)
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
