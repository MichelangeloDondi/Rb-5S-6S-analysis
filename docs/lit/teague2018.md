---
citekey: teague2018
type: article
authors:
  - Teague, Richard
  - Foreman-Mackey, Daniel
title: 'A robust method to measure centroids of spectral lines'
journal: Res. Notes AAS
volume: 2
number: 3
pages: 173
year: 2018
doi: 10.3847/2515-5172/aae265
arxiv: '1809.10295'
pdf: PDF_papers/Teague_2018_robust-spectral-line-centroids.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/teague2018.md  # line-by-line against the held PDF, 2026-09-22: one wording fix so noise and asymmetry match the paper's own bias/affected distinction; Eqs. 6-7 confirmed on a rendered-page check
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1809.10295v1 (17 Sep 2018), read in full on 2026-09-22.
    Journal reference and DOI from Crossref the same day.'
verified_date: 2026-09-22
summary: >
  From radio and integral-field astronomy, where line centroids are mapped by the
  million: the intensity-weighted first moment is affected by noise and biased by line
  asymmetry, and the sigma-clipping used to tame the noise adds spurious features. A
  Gaussian fit is biased by asymmetry too, and the peak channel is limited by the
  resolution. A quadratic through the brightest pixel and its two neighbours gives a
  centroid robust to both, with a closed-form statistical error (Eq. 7). Code:
  bettermoments.
loci:
  - methods/06
section: method-anchors
---

# teague2018

VERIFIED. Held (arXiv v1). Read in full on 2026-09-22.

## What it does

A three-point quadratic around the brightest channel (Eqs. 1-4) gives the peak position x_max = x0 - (f+ - f-) / (2 (f+ + f- - 2 f0)) (Eq. 6), with a linearized statistical error (Eq. 7) for independent, homoskedastic noise. The authors warn that this covers statistics only and that systematic errors need their own treatment. On a simulated two-Gaussian asymmetric line, the first moment and a single-Gaussian fit are both pulled by the asymmetry, while the peak channel is unbiased but coarse (Fig. 1, top). On 13CO data of a protoplanetary disk at 330 m/s resolution, the quadratic gives 47 m/s statistical error, 15 per cent of a channel, where a 2-sigma-clipped first-moment map is dominated by noise (Fig. 1, bottom).

## Use in this record

- Outside atomic physics, the "first moment" of a spectral line is known to be fragile. Noise and asymmetry move it, and masking or clipping, a data-dependent window, adds artefacts. The field's answer is to change estimator. This record's answer is to keep the windowed moments and model their window dependence and bias with the twin. The paper is a citation for the problem being real and general.
- Mean and mode respond differently to asymmetry, and their difference is itself an odd shape statistic (Pearson's mode skewness). This record's centroid and a peak estimator together would carry an asymmetry signal the centroid alone cannot. That is an instance of the hybrid the programme proposes, canonical centroid plus a shape coordinate.

## Limits

- A research note: no systematic study of bias against S/N or line shape beyond the demonstration figure.
