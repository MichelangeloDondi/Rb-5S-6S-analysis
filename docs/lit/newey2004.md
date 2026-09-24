---
citekey: newey2004
type: article
authors:
  - Newey, W. K.
  - Smith, R. J.
title: 'Higher order properties of GMM and generalized empirical likelihood estimators'
journal: Econometrica
volume: 72
number: 1
pages: 219-255
year: 2004
doi: 10.1111/j.1468-0262.2004.00482.x
arxiv: null
pdf: PDF_papers/Newey_2004_higher-order-GMM-GEL-bias.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/newey2004.md  # line-by-line against the held PDF, 2026-09-22: every cited theorem number (2.1, 4.1, 4.2, 4.3, 4.5, 4.6, 5.1, 6.1, 6.2) and the conclusion's Monte Carlo claim confirmed exactly; no correction needed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (Econometric Society), downloaded by the owner by hand. Read on 2026-09-22: Sections 1, 2, 4, 5 (the construction), 6 and 7 in full; Section 3 (the stochastic expansion) and the Appendix proofs skimmed, so the note relies on the theorems as stated and not on their proofs. Journal record from Crossref.'
verified_date: 2026-09-22
summary: >
  The second-order bias of moment estimators, split term by term. GMM's bias is the sum
  of four terms: the bias of the optimal linear combination of the moments, and three
  terms from estimating the Jacobian, the moments' second-moment matrix Omega and the
  preliminary estimator. Empirical likelihood (EL) keeps only the first, so its bias
  does not grow with the number of moment conditions while GMM's often does. For
  minimum distance, the moment fit of a model's predicted moments, the only excess
  over EL is the weight matrix's term, which vanishes when the third moments of the
  moment functions do. In a worked example the GMM bias in units of its standard error
  grows as the square root of the number of overidentifying restrictions. Analytic bias
  corrections are given, and bias-corrected EL is higher-order efficient among bias-
  corrected GMM and GEL estimators.
loci:
  - P1
  - methods/06
section: method-anchors
---

# newey2004

VERIFIED for the sections read (see the flag). Held (published version).

## What it does

Section 2 sets up m moment conditions E[g(z, beta0)] = 0 for p parameters and shows that empirical likelihood, exponential tilting, the continuous-updating estimator (CUE) and the Cressie-Read family are all generalized empirical likelihood (GEL) estimators. It shows the CUE is GEL with a quadratic rho (Theorem 2.1). Section 4 gives the O(1/n) bias. For two-step GMM it is B_I + B_G + B_Omega + B_W (Theorem 4.1). B_I is the bias of the estimator using the optimal linear combination G' Omega^-1 g. B_G comes from estimating the Jacobian and is zero when the Jacobian is constant. B_Omega comes from estimating Omega and is zero when the third moments of g are zero. B_W comes from the preliminary estimator and is zero when its weight is proportional to Omega. B_G and B_Omega vanish under exact identification, m = p. For GEL, B_G and B_W drop out (Theorem 4.2), and for EL the bias is B_I alone (Corollary 4.3).

For conditional moment restrictions, and under a sign condition on the model's skewness terms, the bias of GMM grows linearly with the number of overidentifying restrictions while EL's stays bounded (Theorem 4.5). In the homoskedastic linear case this recovers the Nagar bias of two-stage least squares. Section 4.2 treats minimum distance, g = r(z) - h(beta). There GMM and the CUE share one bias, EL's plus a term in E[g g' P g], and EL's bias is zero when h is linear and does not grow with the number of restrictions (Theorem 4.6). The example of a common mean fitted to m independent skewed components gives an EL bias of zero and a GMM bias that, divided by its standard error, grows as the square root of m. Section 5 builds analytic bias corrections from the same ingredients as the variance estimate (Theorem 5.1). Section 6 shows that bias-corrected EL is third-order efficient relative to the other bias-corrected estimators (Theorem 6.1), while without the corrections the ranking can reverse with the tails of the errors (Theorem 6.2). The conclusion cites Monte Carlo studies consistent with these results and recommends GEL, EL in particular for minimum distance, where the weight matrix's bias can be serious.

## Use in this record

- The record's moment fit is a minimum-distance problem: the trace's windowed moments r are matched to the model's h(beta). Theorem 4.6 splits its first-order bias into a curvature part (zero when the model moments are linear in the parameters) and a weight part (the correlation of an estimated weight with the moments it weights). The twin measures the sum. The theorem says which part scales with the number of moments, so the twin's bias can be read against it, not only subtracted.
- The weight part comes from estimating the weight from the same data, so it is absent when the weight is independent of the data. The record's covariance from twin replicas is that case, with the replica count as the price (hartlap2007, sellentin2016), as altonji1996 argues for the same bias. If the replicas are regenerated at a preliminary fit to the data, the weight depends on the data again, and a term of the B_W form appears through the covariance's dependence on the parameters. It vanishes when that preliminary fit is itself efficient.
- The weight term is driven by the third moments of the moment functions. A raw windowed moment is linear in the trace, so with Gaussian noise its third moments vanish and so does the term. The ratios and normalised cumulants the programme favours are nonlinear in the trace and skewed, and for them the term returns and can grow with the number of overidentifying coordinates. That supports the rule of choosing coordinates by their twin bias per window instead of accumulating them, and it bears on the programme's reach toward mu_12.
- Empirical likelihood, or the CUE, is a named alternative to a Gaussian moment likelihood whose bias does not grow with the number of moments. It is the estimator-level partner of frazier2024's misspecification results for synthetic likelihood.

## Limits

- First-order asymptotics in 1/n for i.i.d. observations and a fixed number of moments (the growing-m results are cited from Donald, Imbens and Newey 2002, not proved here). It gives formulas, not a finite-sample guarantee at the record's replica counts, and it does not treat a moment's window or its noise floor.
