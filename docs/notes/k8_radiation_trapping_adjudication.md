# The fourth candidate for K8's in-window structure, adjudicated on committed rows

**Status.** Adjudicated and excluded. No new computation.

`provenance: results/kernel_k8.csv` - this page computes nothing. Every
number on it is read from a committed row or from a published section named
beside it: the two z values and the predictor correlation from
[`results/kernel_k8.csv`](../../results/kernel_k8.csv), the density span and
the optical-depth range from [RESULTS.md](../RESULTS.md). The adjudication
is an argument over those rows, and if one of them moves this page is wrong
rather than merely stale.

## What prompted it

A sweep of the held literature proposed a mechanism the record was not
weighing. [araujo2021](../lit/araujo2021.md) models Levy-flight photon
transport, heavy-tailed with an exponent near one half, in He-broadened hot
rubidium, and [chevrollier2012](../lit/chevrollier2012.md) surveys radiation
trapping and Levy-flight statistics in atomic vapours. Anomalous transport
distorts a line in a way ordinary diffusive trapping does not, because the
escape probability becomes frequency dependent. The near-wing design weighs
three candidates for the in-window residual structure: profile mismatch,
detector and chain nonlinearity, and an amplitude-dependent baseline. This
would have been a fourth.

## Why it is excluded, and the exclusion was already on disk

K8 regressed the in-window residual structure on two predictors jointly
across 32 conditions
([`results/kernel_k8.csv`](../../results/kernel_k8.csv)):

| predictor | z | reading |
|---|---|---|
| the model's own profile height | 9.41 | the structure scales with signal amplitude |
| log10 vapour number density | 1.30 | it does not scale with density |

The two predictors correlate at 0.488, below the threshold preregistered
for separability, so the density null is a measurement rather than an
artefact of collinearity. Leave-one-out refits put the smallest height z at
8.53, so no single condition carries the result. The committed verdict is
`MULTIPLICATIVE_IN_SIGNAL_NOT_DENSITY`, with the mechanism recorded as not named.

**Trapping of any kind is governed by optical depth, and optical depth is
governed by density.** The reabsorber is a ground-state atom, which is what
[the composite-model chapter](../methods/04_the_composite_model.md) section
2.7 states in setting the mechanism up. The heavy tail changes how escape
scales with optical depth. It does not remove the dependence.

The lever is large enough for that null to bite. The density span across
the four temperatures is 52.5-fold ([RESULTS.md](../RESULTS.md)), and the
cell is optically thick on the D1 detection line over that span, with
tau per centimetre running about 1 to 160 (RESULTS.md, radiation trapping).
A mechanism whose strength tracks tau across a 160-fold range cannot
produce a density coefficient of 1.30 sigma while producing a height
coefficient of 9.41.

## What this does not settle

The three original candidates are untouched. K8's own note records why its
height coefficient is weak evidence about mechanism: a normalised residual
scales with signal under any fractional model, so 9.41 sigma on height
discriminates almost nothing by itself. **The exclusion here rests entirely
on the density null, not on the height coefficient.**

It also leaves the amplitude channel alone. Trapping is present in this
cell and the record measures it: amplitude against density gives log-log
slopes of 0.85 to 1.02 with no significant rollover, which is trapping
redistributing rather than destroying. That is a statement about
amplitudes. K8 is a statement about residual shape, and section 2.7's title
makes the distinction the record has always drawn.

## Consequence

The near-wing discriminator's assumption of three candidate mechanisms
stands, and it did not need a fourth arm. The two papers stay in the
corpus for the amplitude channel, where trapping is real and measured.
