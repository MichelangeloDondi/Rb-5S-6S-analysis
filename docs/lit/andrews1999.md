---
citekey: andrews1999
type: article
authors:
  - Andrews, Donald W. K.
title: 'Consistent Moment Selection Procedures for Generalized Method of Moments Estimation'
journal: Econometrica
volume: 67
number: 3
pages: 543-564
year: 1999
doi: 10.1111/1468-0262.00036
arxiv: null
pdf: PDF_papers/Andrews_1999_consistent-moment-selection-procedures-for-GMM.pdf
held: true
section: method-anchors
status: VERIFIED
verified_date: 2026-09-24
summary: 'Gives GMM analogues of BIC, AIC and HQIC for selecting which moment conditions to use, a rival to selecting coordinates by their twin-measured bias.'
audit: private/cache/lit_intake_2026-09-24_audits/finance_intake.md
routing:
  - CITE
  - FEED
verify_flags:
---

# Andrews 1999: a formal criterion for which moments to use, and it is a rival to this record's

**Why this record holds it.** The main aim selects coordinates by their twin-measured bias per
window (A100.2, A121). This paper selects moment conditions by a criterion with an explicit
penalty. The two rules are rivals, they can be run on the same data, and until now this record had
no account of the alternative it was not using.

## What it does

The paper's own sentence is "We introduce GMM analogues of the widely used BIC (Bayesian), AIC
(Akaike), and HQIC (Hannan-Quinn) model selection criteria". They are built on the
overidentification statistic, where a bonus
"term is subtracted from the J test statistic that rewards selection vectors that employ more
moment conditions". Minimising the criterion over selection vectors returns an estimate of which
moment conditions are the correct ones.

## How it differs from this record's rule, which is the useful part

**Their criterion asks whether a moment condition is true. This record's asks whether its bias is
known.** Those are different questions and the difference is the twin. A moment whose bias is large
but forecastable is admitted here and would be rejected there. A moment that is unbiased but
uninformative passes there and is dropped here for carrying no information (W1's leverage clause).

**So the honest position is that they are complementary and this record should run both.** The
J-statistic route needs no simulator and tests a hypothesis this record never tests, that the
model's moment conditions hold at all. That is a specification test the moment block currently
lacks, and it is available for the cost of computing one statistic.
