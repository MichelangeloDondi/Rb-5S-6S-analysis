---
citekey: buchmueller2006
type: article
authors:
  - Buchmüller, O. L.
  - Flächer, H. U.
title: 'Fit to Moments of Inclusive B to Xc l nu and B to Xs gamma Decay Distributions using Heavy Quark Expansions in the Kinetic Scheme'
journal: Physical Review D
volume: 73
pages: '073008'
year: 2006
doi: 10.1103/PhysRevD.73.073008
arxiv: 'hep-ph/0507253'
pdf: PDF_papers/Buchmueller_2006_B-to-Xc-lepton-nu-moment-fit-lower-energy-cut-HQE.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/buchmueller2006.md  # line-by-line against the held PDF, 2026-09-22; two corrections applied -- a substituted symbol (Gamma_SL misquoted as tau in two places: the frontmatter summary and the Values table) and a moment-definition equation misattributed to this paper's p.2 that is actually alberti2014's
author: agent
routing:
  - CITE
verify_flags:
  - 'Pages 1-3 of the held PDF (arXiv:hep-ph/0507253v3, 4 Jun 2006) read directly on 2026-09-21:
    title, abstract, Section I (Introduction), Section II (Heavy Quark Expansions in the Kinetic
    Scheme) through Eq. 1-2 (the semileptonic width and its |Vcb| ratio transformation) and the
    start of Section III.A (experimental input, Table I). The fit procedure, results, and
    cross-checks (Sections III.B onward, pages 4-13) were NOT read. CORRECTED 2026-09-22 (audit):
    this bullet previously called eq. 1-2 "the moment definition" -- they are not; see the audit
    file.'
verified_date: 2026-09-21
summary: >
  A global fit of central moments of three different inclusive B-decay distributions (hadronic
  mass, lepton energy, photon energy), each measured at SEVERAL different lower-energy cuts
  E_cut by five experiments, to a shared set of Heavy Quark Expansion parameters (quark masses,
  matrix elements), extracting |Vcb| = (41.96 +/- 0.23_exp +/- 0.35_HQE +/- 0.59_GammaSL)e-3. The
  paper the task names directly for "moment fits against a lower energy cut".
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# buchmueller2006

VERIFIED for pages 1-3 (title through the start of the experimental-input section and Table I).
The fit machinery and the numerical cross-checks (Sections III.B-V) were not read.

## Values

| field | value | where in the paper |
|---|---|---|
| journal reference | Phys. Rev. D **73**, 073008 (2006) | Crossref lookup, 2026-09-21, exact title match |
| affiliations | CERN, Royal Holloway, University of London | p. 1 |
| headline result | \|Vcb\| = (41.96 +/- 0.23_exp +/- 0.35_HQE +/- 0.59_GammaSL) x 10^-3, m_b = 4.590 +/- 0.025_exp +/- 0.030_HQE GeV | abstract, p. 1 |
| moments as functions of the shared parameter set | <M_X^n> -> <M_X^n>(m_b,m_c,mu_pi^2,mu_G^2,rho_D^3,rho_LS^3,alpha_s). <E_l^n> -> <E_l^n>(m_b,m_c,mu_pi^2,mu_G^2,rho_D^3,rho_LS^3,alpha_s). <E_gamma^n> -> <E_gamma^n>(mu_pi^2,mu_G^2,rho_D^3,rho_LS^3,alpha_s) | p. 2, the three unnumbered display lines after "Relations similar to Eq. 2 have been calculated for inclusive observables..." |
| experimental inputs | five collaborations (BABAR, Belle, CDF, CLEO, DELPHI) supplying hadron-mass, lepton-energy and photon-energy moments at up to 16 different E_cut values, with published correlation matrices | p. 3, Table I |

## What it says, in its own terms

Abstract (verbatim, p. 1): "We present a fit to measured moments of inclusive distributions in
B" [to Xc l-bar-nu and to Xs gamma] "decays to extract values for the CKM matrix element
\|Vcb\|, the b- and c- quark masses, and higher order parameters that appear in the Heavy Quark
Expansion. The fit is carried out using theoretical calculations in the kinetic scheme and
includes moment measurements of the BABAR, Belle, CDF, CLEO and DELPHI collaborations for which
correlation matrices have been published."

The moments are explicitly central moments computed with a lower cut on an observable (the lepton
momentum or the photon energy) that differs measurement to measurement, and the paper's own text
states the reason for combining many cuts instead of one: "it is important to use as many moment
measurements as possible in order to overconstrain the extraction of the heavy quark parameters
and to establish the validity of the expansions" (p. 3). Every moment's THEORY prediction is
written as an explicit function of the same shared parameter set (quark masses and four HQE
matrix elements), so that "since every moment calculation has a different dependence on the heavy
quark parameters a simultaneous fit allows for the extraction of all these parameters" (p. 3).
Section III.A (p. 3, Table I) tabulates exactly which moment order n, which observable, and which
E_cut value each of the five experiments contributes. Some cut settings are deliberately excluded
"as correlation matrices are only available for the statistical errors" (p. 3): a measurement is
dropped from a joint fit when its correlation structure with the others is not known, not merely
when its own value looks uncertain.

## Use in this record

This is the concrete particle-physics precedent the task named directly, and it maps onto this
record's own programme almost coordinate for coordinate: a moment of a measured distribution
(there, hadron mass / lepton energy / photon energy in a semileptonic or radiative B decay, and
here, the two-photon lineshape) is not a single number but a family of numbers indexed by a window
setting (there, the lower energy cut E_cut, and here, the truncated frequency window W), each with its
own theory prediction as a function of a shared physical parameter set, combined into one global
Fit that uses the moments' different sensitivities to the shared parameters to overconstrain them.
The explicit design rule is this: include a cut/window setting only when its correlation with the others
is known, never average it in blind. It is the same discipline this record's own OWNER_ORDERS and
ladder gate enforce by refusing a moment at a window where its own denominator distribution
misbehaves. The physics (heavy-quark expansion of a weak-decay spectrum vs. a light-shift-
broadened atomic line) is unrelated. The shared structure is many windowed moments of several
distributions, combined in one global joint fit for shared parameters, with correlation-aware
inclusion of each cut setting.
