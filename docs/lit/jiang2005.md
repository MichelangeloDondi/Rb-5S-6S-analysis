---
citekey: jiang2005
type: article
authors:
  - Jiang, George J.
  - Tian, Yisong S.
title: 'The Model-Free Implied Volatility and Its Information Content'
journal: The Review of Financial Studies
volume: 18
number: 4
pages: 1305-1342
year: 2005
doi: 10.1093/rfs/hhi027
arxiv: null
pdf: PDF_papers/Jiang_2005_model-free-implied-volatility-and-its-information-content.pdf
held: true
section: method-anchors
status: VERIFIED
verified_date: 2026-09-24
summary: 'Separates the truncation error of a finite integration range from the discretisation error of a finite grid and bounds each, distinguishing a tight model-based bound from a looser model-free one.'
audit: private/cache/lit_intake_2026-09-24_audits/finance_intake.md
routing:
  - CITE
  - FEED
verify_flags:
---

# Jiang and Tian 2005: truncation error and discretisation error, separated and bounded

**Why this record holds it.** It is the only source found that treats a moment computed over a
finite range of a truncation variable by decomposing the error into a truncation half and a
discretisation half, and bounds each. That is this record's own window-bias-against-numerical-floor
distinction, which was obtained here by simulation (the halved-grid refusal, F218) and there by
derivation.

## What it does

The model-free implied volatility is an integral of option prices over the whole strike axis.
Markets supply a finite strike range and a finite grid, so the implementation has two errors, and
the paper treats them in two subsections of its own section 1.2.

**Truncation (section 1.2.1).** Proposition 2 gives upper bounds on the right and left truncation
errors beyond the available range. Their character is the transferable part: the paper states that
"the truncation errors are related to the local variations in the tails" of the distribution.
Two bound families are derived, and the paper is explicit that the tighter one is not assumption
free: "Although these upper bounds are shown subsequently to be quite tight, they are not model
free. We also derive model-free upper bounds for truncation errors in the Appendix."

**Discretisation (section 1.2.2).** The same integral evaluated by the trapezoidal rule over a
finite grid carries its own error, treated separately and never folded into the first.

**The two criteria, both in units of the distribution's own standard deviation.** For truncation:
"In general, the truncation error is negligible if the truncation points are more than two SDs
from Fo." For the grid, the paper reports that discretisation errors are negligible below about
0.35 SD of spacing, equivalently more than about twenty intervals.

**Asymmetry with skew.** For a left-skewed distribution the left truncation error dominates, and
the paper states the consequence directly: "With a fatter left tail, a larger range of strike
prices is needed on the left of Fo if we wish to have identical truncation errors from both sides."

## What transfers, and what does not

**The structure transfers and the criterion does not, for a reason that is this record's own
subject.** Both of their thresholds are counted in standard deviations of the distribution being
integrated. This record's line has a Lorentzian wing, so its untruncated even moments do not exist
(A26, F218): there is no standard deviation to count two of. A rule of thumb stated in SDs is
therefore unavailable here, and the reason it is unavailable is exactly what makes the window a
designed axis rather than a nuisance.

**What does transfer is the model-free bound.** This record's entire bias treatment is
model-based: the twin computes the bias because the twin knows the truth. A model-free upper bound
is a different object, and it is the check on the twin that this record does not have. Deriving
one for a windowed central moment under a bounded wing weight is a defined piece of work.

**And the asymmetry is unexplored here.** This record's window is a symmetric rect, plus or minus
W, while its line is skewed by the AC-Stark ramp. Their result says a symmetric truncation of a
skewed density gives unequal errors on the two sides. An asymmetric window matched to the line's
own skew is a lever this record has never considered.
