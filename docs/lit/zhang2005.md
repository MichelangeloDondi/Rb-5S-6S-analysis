---
citekey: zhang2005
type: article
authors:
  - Zhang, Lan
  - Mykland, Per A.
  - Ait-Sahalia, Yacine
title: 'A Tale of Two Time Scales: Determining Integrated Volatility with Noisy High-Frequency Data'
journal: Journal of the American Statistical Association
volume: 100
number: 472
pages: 1394-1411
year: 2005
doi: 10.1198/016214505000000169
arxiv: null
pdf: PDF_papers/Zhang_2005_tale-of-two-time-scales-integrated-volatility-noisy-data.pdf
held: true
section: method-anchors
status: VERIFIED
verified_date: 2026-09-24
summary: 'Removes a sampling-induced bias by evaluating one estimator at two scales and subtracting, which fixes a divergence analytically where this record forecasts it with a twin.'
audit: private/cache/lit_intake_2026-09-24_audits/finance_intake.md
routing:
  - CITE
  - FEED
verify_flags:
  - the held copy is the September 2004 draft, not the JASA version of record. The volume, number and pages in this frontmatter are the published article's and were not read off the held file
---

# Zhang, Mykland and Ait-Sahalia 2005: a bias cancelled by combining two scales

**Why this record holds it.** It is the cleanest published instance of cancelling an estimator's
leading bias by evaluating the same estimator at two values of a sampling parameter and taking a
linear combination. This record sweeps a truncation window and forecasts the bias with a twin. This
paper removes the analogous bias analytically, with no simulator at all.

## What it does

High-frequency returns carry microstructure noise, and the realised-volatility estimator built from
all the data is dominated by it. The paper is explicit that its remedy is not a choice of sampling
rate: the two-scales estimator "works for any size of the noise".

The estimator is a difference between a subsampled-average estimator and a scaled full-grid one,
formed "by combining estimators obtained over the two time scales", with a small-sample adjustment
given separately.

## What transfers

**This record already has the exponent the trick needs.** The window programme's own derivation
(A39, A72) gives the large-window form of an even moment as its converged part plus a divergence
going as `W` to the power `n-1`. Two windows therefore fix that term exactly: with
`lambda = (W1/W2)^(n-1)`, the combination `[mu_n(W1) - lambda mu_n(W2)] / (1 - lambda)` cancels the
leading divergence and returns the converged part, with no twin in the loop.

**The normalisation is load-bearing.** Without the `1/(1 - lambda)` the combination returns
`mu_n_inf` times `(1 - lambda)` rather than `mu_n_inf`. On the fourth order at 8 and 13 MHz against
an assumed converged value of 2.5, the raw combination reads 1.9174, the normalised one reads
2.5000, and the uncorrected `mu_4(W1)` reads 65.6467 (probe:6944826a). Zhang and his co-authors
carry the same shape: a scaled subtraction followed by a small-sample adjustment factor. That is this paper's device on this record's axis, and
it is computable on the twin immediately, which is how it should be checked before it is believed.

**What it would buy, stated before it is run so the result can disappoint it.** A two-window
combination that removes the leading truncation term would make the wide windows usable where the
divergence currently forces a choice between truncation bias and admitted noise. What it cannot do
is remove a bias that is geometric rather than a property of the window, which is what the pairing
of shift and transit produces here, so the honest expectation is that it helps the even orders at
wide windows and does nothing for the odd channel.
