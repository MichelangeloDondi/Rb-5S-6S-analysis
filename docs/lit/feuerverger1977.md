---
citekey: feuerverger1977
type: article
authors:
  - Feuerverger, Andrey
  - Mureika, Roman A.
title: 'The empirical characteristic function and its applications'
journal: Ann. Stat.
volume: 5
number: 1
pages: 88-97
year: 1977
doi: 10.1214/aos/1176343742
arxiv: null
pdf: PDF_papers/Feuerverger_1977_empirical-characteristic-function.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/feuerverger1977.md  # line-by-line against the held PDF via page images (no text layer), 2026-09-22: two precision corrections (a U-statistic attribution, a theorem-citation scope)
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (a scanned JSTOR copy distributed through
    Project Euclid, open access). It has no text layer, so pages 88-94 were read as page
    images on 2026-09-22; pages 95-97 were not read. The DOI is the Project Euclid one
    in the download URL.'
verified_date: 2026-09-22
summary: >
  The statistics of the empirical characteristic function c_n(t) = (1/n) sum
  exp(i t X_j). It converges uniformly almost surely on bounded t intervals
  (Theorem 2.1), and on intervals growing like (n/log n)^(1/2) under a mild
  condition (Theorem 2.6). sqrt(n)(c_n - c) tends to a complex Gaussian process
  (Theorem 3.1) whose covariance is fixed by c itself, E Y(t1)Y(t2) = c(t1+t2) -
  c(t1)c(t2). The imaginary part of c_n carries the asymmetry: the statistic
  integral of [Im c_n(t)]^2 dG(t) tests symmetry, with a stated asymptotic
  distribution (Section 4).
loci:
  - methods/11
section: method-anchors
---

# feuerverger1977

VERIFIED for pages 88-94. Held (published version, scanned). Read on 2026-09-22.

## What it says

Section 2 proves uniform almost-sure convergence of the empirical characteristic function on any bounded interval of t (Theorem 2.1), on the whole line for purely discrete distributions (Theorem 2.2), and on intervals growing like (n / log n)^(1/2) when the singular part's characteristic function vanishes at the extremities (Theorem 2.6). A mean-convergence result is Theorem 2.7. Section 3 treats Y_n(t) = sqrt(n)(c_n(t) - c(t)) as a random process: its covariance is c(t1 + t2) - c(t1) c(t2), with the covariances of real and imaginary parts written out, and it converges weakly to the corresponding complex Gaussian process on every finite interval (Theorem 3.1). Section 4 uses the fact that a characteristic function is real exactly when the distribution is symmetric. The statistic T_n = integral of [Im c_n(t)]^2 dG(t), with G a symmetric weight, is asymptotically normal under asymmetry, its fluctuation reducing to a Hoeffding U-statistic (Theorem 4.1), and a weighted sum of chi-squared variables under symmetry (Theorems 4.2-4.3, through a Karhunen-Loeve expansion). The paper notes that for data recorded on a grid of step Delta, frequencies beyond about 1/Delta are neither estimable nor relevant.

## Use in this record

- The conjugate-domain statistics of the programme. The odd cumulants of a line live in the imaginary part of its characteristic function, and a weighted integral of that part, with a weight G, is a symmetry statistic with known sampling behaviour. The rule file's statement that a frequency window acts as a sinc convolution of the characteristic function is the other side of the same picture. This paper gives the sampling covariance on that side in closed form, E Y(t1)Y(t2) = c(t1 + t2) - c(t1) c(t2).
- A reminder of the resolution limit a finite grid puts on the conjugate variable, which is the statement behind the record's small-window limit.

## Limits

- The theory is for independent, identically distributed samples X_j. A spectral line recorded with additive noise is not such a sample: its Fourier transform is a time-domain signal with its own noise law. The connection here is structural, not a direct application of the theorems.
