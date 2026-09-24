---
citekey: mackinnon1998
type: article
authors:
  - MacKinnon, J. G.
  - Smith, A. A.
title: 'Approximate bias correction in econometrics'
journal: J. Econometrics
volume: 85
number: 2
pages: 205-230
year: 1998
doi: 10.1016/S0304-4076(97)00099-7
arxiv: null
pdf: PDF_papers/MacKinnon_1998_approximate-bias-correction-econometrics.pdf
held: true
status: VERIFIED
author: agent
audit: private/cache/lit_intake_2026-09-22_audits/mackinnon1998.md  # line-by-line against the held PDF, 2026-09-22: no factual defects found on a full read (Sections 1-7 plus references); one precision edit to a scare-quoted phrase that could be misread as attributing this record's own terminology to the paper
routing:
  - CITE
verify_flags:
  - 'The held PDF is the authors'' final revision (May 1997), from the first author''s Queen''s University page; the journal typesetting is not held, so the note cites the preprint''s equation numbers. Read in full on 2026-09-22, Sections 1 to 7. Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  How to subtract a simulated bias, and what it costs. The bias of an estimator is a
  function of the true parameter, b(theta). Subtracting it evaluated at the estimate (the
  bootstrap-style constant correction, CBC) leaves a bias of -b' times the original and
  scales the variance by (1 - b')^2. Solving theta = theta_hat - b(theta) instead (the
  nonlinear correction, NBC, or its linear approximation LBC) removes the bias to
  O(1/n^2) and scales the variance by 1/(1 + b')^2. So the slope of the bias function
  decides whether correction helps: it can raise the mean squared error when the slope
  is negative and the variance is large next to the bias. An AR(1) and a logit model
  illustrate both outcomes. The authors conclude that correcting mechanically, without
  knowing the bias function's shape, is not a good idea, and that the corrected
  estimate's variance must always be recomputed.
loci:
  - P1
  - methods/06
section: method-anchors
---

# mackinnon1998

VERIFIED. Held (authors' final revision). Read in full on 2026-09-22.

## What it does

Section 1 defines the bias function b(theta, n) = E(theta_hat) - theta_0 and notes that for a root-n consistent, asymptotically normal estimator it is O(1/n). Section 2 treats flat and linear bias functions. The constant-bias-correcting estimator is theta_tilde = theta_hat - b_hat = 2 theta_hat - theta_bar, with theta_bar the mean of estimates from N samples simulated at theta_hat (Eqs. 3-4), which is the bootstrap's bias correction. If b(theta) = alpha + b' theta, its bias is -b' times the original bias (Eq. 9) and its variance (1 - b')^2 times the original (Eq. 11). The linear-bias-correcting estimator solves theta = theta_hat - b(theta), is unbiased for a linear bias function, and has variance 1/(1 + b')^2 times the original (Eqs. 6-7, 10, 12). Either can have a larger mean squared error than the uncorrected estimator (Eqs. 13-14): correction works well when the bias function slopes upward, or when the variance is small next to the bias. With N = 1000 simulations the simulated bias carries a standard error of about 0.032 times that of theta_hat.

Section 3 allows a nonlinear bias function. The nonlinear-bias-correcting estimator solves theta = theta_hat - b(theta) by a damped fixed-point iteration (Eqs. 15-16). It is the inverse of the mean function theta + b(theta), as Andrews' median-unbiased estimator inverts the median function. LBC and NBC agree through O_p(1/n) and are biased at O(1/n^2) by an amount proportional to the bias function's curvature (Eqs. 18, 20-23). CBC's O(1/n^2) bias has an extra slope term (Eq. 24). Section 4 gives the vector forms, CBC with covariance (I - B')V(I - B')' and LBC with (I + B')^-1 V (I + B')^-1' (Eqs. 26-29), where the variance can rise for some parameters and fall for others. Section 5's AR(1) study finds that the corrections remove most of the bias, yet ordinary least squares has the lower RMSE for rho between about -0.9 and 0.5 because the bias function slopes downward there. Section 6's logit study, with an upward-sloping bias function, finds correction works well in both bias and RMSE.

## Use in this record

- The main aim uses the twin to compute biases and factor them out, and this paper distinguishes three ways to do that, each with a different cost. A twin bias evaluated at the fitted point and subtracted is CBC: it leaves -b' of the bias and rescales the spread by (1 - b'). A twin iterated until the truth minus its own bias reproduces the data's estimate is NBC, removing the bias to second order with spread rescaled by 1/(1 + b'). The record should say which it does.
- The slope b' is a number every twin-corrected result needs beside its correction. The twin's grids of truths (the waist, the sigma_L worlds, the noise ladder's levels) already sample the bias function at several points, so its slope is available without new runs.
- A corrected estimate's bar is not the uncorrected bar. The record's rule that a bias is printed only with its coverage and standard error extends here to the corrected value's own variance, Eqs. (22), (25) or (29).
- Correction can raise the mean squared error where the bias function slopes downward and the variance is large next to the bias, which is the regime of the high orders at the archive's noise. Whether to correct is then a per-coordinate decision, consistent with choosing coordinates by their twin bias.
- gourieroux2000 proves the NBC form is indirect inference with the finite-sample binding function. barlow1993 is the complementary case of bias from noisy templates.

## Limits

- Scalar and small-vector parameters, i.i.d. or AR(1) data, and bias functions smooth enough to be estimated by simulation. It does not treat confidence intervals, misspecification of the simulator, or a bias function sampled only at a few grid points.
