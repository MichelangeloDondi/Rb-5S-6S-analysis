# Postscript to the M14 coverage preregistration: what the run returned

Run complete 2026-08-17, 15600 fits, 650 trials per cell, 24 cells, zero
failures. Output `private/run_logs/stark_coverage_2026-08-17T015322Z/`.
Read `stark_coverage_prereg.md` first: every endpoint below was named there
before the run, and none has been added or promoted since.

`provenance: NO_PRODUCER` - The run happened, 15600 fits over 24 cells with zero failures, and `run_stark_coverage.py` wrote its trials and summary into `private/run_logs/`, which is gitignored. **So a fresh clone cannot regenerate or check any of it**, which is the same shape as the block bootstrap. The producer exists and its output sink is the problem. **10 numeric claims on this page remain unaccounted for.** Declared after checking every three-significant-figure value on the page against `results/`, not by labelling.


The abandoned first run's directory exists and is empty, which is the evidence
for the amendment's claim that no output existed when it was stopped.

## The primary endpoint

Coverage of `kappa_ub95_profile` in the over-dispersed arm, target 0.95:

| $\kappa_{\rm true}$ (MHz/W) | $S_0$(225) implied | coverage | mcse |
|---|---|---|---|
| 0.00, the boundary the construction exists for | 0 | **1.0000** | 0 |
| 1.15, the joint C3f bound | 0.259 | **1.0000** | 0 |
| 2.81, the width-only C3d bound | 0.632 | **0.9954** | 0.0027 |
| 4.00 | 0.900 | 0.9692 | 0.0068 |
| 5.50 | 1.238 | **0.9354** | 0.0096 |
| 7.00 | 1.575 | **0.9338** | 0.0097 |
| 9.00 | 2.025 | **0.9400** | 0.0093 |

**Where the published bounds live, the construction over-covers.** At the
boundary and everywhere up to and including the width-only bound, coverage is
at or above 0.995. That is the boundary-mixture behaviour the preregistration
predicted: with the likelihood-ratio statistic an equal mixture of $\chi^2_0$
and $\chi^2_1$ at a railed parameter, a one-sided 2.706 threshold is
conservative rather than exact. The quoted 95% is therefore safe in the region
it is used, and the bound is looser than the data require.

**The preregistered falsification condition did trigger, and it is REPORTED
rather than reinterpreted.** The note said that coverage below 0.95 at any
ladder point means the quoted 95% is not 95%. At $\kappa_{\rm true} \ge 5.5$
coverage is 0.934 to 0.940, which is below 0.95 by six to seven Monte-Carlo
standard errors and is a real effect, not noise.

What that region is, stated so the reader can judge rather than take a verdict:
a kappa of 5.5 corresponds to an S0 at 225 mW of 1.24 MHz, which is four
times the ramp prediction of 0.35 and roughly twice the width-only bound the
record publishes. It is a part of parameter space this experiment already
excludes. **The literal condition is met and the practical consequence is
nil**, and separating those two is the owner's call rather than mine. Nothing
in the record was changed on this.

## The secondary that changes how the primary should be read

**The published bound sits at the 0.0th percentile of its own simulated
distribution.** At $\kappa_{\rm true} = 0$ with production-realistic noise, not
one of 650 simulated datasets produced a bound as tight as the archive's
2.8111 MHz/W. The median simulated bound is 5.61. In the nominal arm the
published bound sits at the 4.2nd percentile.

**The comparison must be like for like, and the first version of it was not.**
The real fit rails at the boundary. Comparing it against all 650 simulations,
railed and unrailed together, mixes two populations. Restricted to railed
simulations the published bound sits at the 0th percentile of 91 in the
over-dispersed arm, and at an unremarkable **12th percentile of 41** in the
nominal arm.

That split is the finding. **The real data behave like the nominal arm**, in
which their bound is ordinary, despite genuinely carrying a reduced chi-square
of 3.7. The likely mechanism is that the real over-dispersion is largely a
per-peak offset that the fit's own per-peak `sigma_laser` nuisances absorb,
while a uniform per-point inflation of sigma cannot be absorbed by anything and
so costs kappa information that the real data never lose. The over-dispersed
arm is therefore a pessimistic caricature rather than a model of this dataset.

**A wrong diagnosis, proposed and then refuted here, because the refutation is
the useful part.** The rail rate is 14 per cent where a naive argument expects
50, and the first reading of that was an optimiser failing to reach the
boundary, which would have made the whole over-coverage result an artefact. It
is testable: if the minimiser were failing, the unrailed fits would sit at
worse chi-square than the railed ones. Measured, they sit at better, 3.83
against 4.27 mean reduced chi-square. The unrailed fits found genuinely lower
minima, the optimiser is working, and the low rail rate is the zero-gradient
boundary `rb5s6s/stark.py` already describes: the width handle broadens as the
square of the shift, so the information at the boundary is zero and the minimum
is quartic-flat. The naive 50 per cent never applied.

**What this does and does not cost.** The direction of the primary result
survives, because over-covering at a boundary is a property of the threshold
and the mixture rather than of the noise scale. What is not calibrated by this
run is the size of the conservatism, so no factor of headroom should be quoted
from these numbers. A calibrated version would inject block-level scatter
rather than per-point inflation, and that is a separate study.

## The Wald comparison, measured rather than repeated

`rb5s6s/stark.py` says the Wald bound "carries no 95% coverage" at the
boundary. Measured, Wald also over-covers at $\kappa = 0$, at 1.0000 in both
arms, so the docstring's claim is about the mechanism, the sigma being a
finite-difference artifact where the Jacobian column vanishes, and not about a
coverage failure at that point. Where Wald is genuinely worse is the middle of
the ladder: in the nominal arm at $\kappa = 4.00$ it covers 0.9154 against the
profile's 0.9554, and at 2.81 it covers 0.9354 against 0.9892.

**The docstring's decision to quote the profile bound is supported by this
run**, and its stated reason is narrower than the evidence now available. That
is a wording question, not a numerical one, and it is left for the owner.

## What this does not license, added on the owner's caution

This study simulates one construction on one condition set, the 130 C
twenty-cell power grid, and says nothing about whether the three sessions the
joint bound pools describe the same kappa. The owner raised that on 2026-08-17:
the rehearsal and the campaign-morning pilot were early attempts exploited
afterwards, and they are not established as sharing the campaign's geometry.
Since kappa scales as one over the waist squared, a different focus makes it a
different parameter, which no per-session nuisance in that fit absorbs.

The committed `results/stark_joint.csv` shows part of the exposure and cannot
show the rest. Among rows that are the same construction, the pooled kappa bound
of 1.147 becomes 1.626 with peak 4192 dropped, which removes the entire pilot, so
a leave-one-peak-out alone moves it by a factor of 1.42.

**The spread cannot be widened using `kappa_ub95_camponly`.** Its value is the
campaign's chi-square read along the joint profile rather than an independent
campaign-only fit, and a row that is not a bound on the campaign alone cannot be
one end of a campaign-against-pool comparison. An earlier version of this
paragraph put it there and quoted a wider spread on the strength of it, which is
the naming defect this record now treats as a class rather than a slip. Nothing
in `results/` yet carries a campaign-alone refit, so the size of the session
exposure is not established by the committed record, and nothing in this coverage
study touches it.

## Standing

DIAGNOSTIC. Nothing entered `results/`, no committed number moved, and no
figure was made. The base fit printed at the top of the run reproduces the
committed `kappa_ub95_profile` of 2.8111 and `chi2_red` of 3.7047, so the
newer numpy in this environment did not move the quantity under test.
