---
citekey: bunker1983
type: article
authors:
  - Bunker, Grant
title: 'Application of the ratio method of EXAFS analysis to disordered systems'
journal: Nuclear Instruments and Methods in Physics Research
volume: 207
pages: 437--444
year: 1983
doi: 10.1016/0167-5087(83)90655-5
arxiv: null
pdf: PDF_papers/Bunker_1983_EXAFS-ratio-method-cumulant-expansion.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand2/audits/bunker1983.md  # full 8-page read against the PDF, 2026-09-22; upgraded from the REPORTED stub
author: agent
routing:
  - CITE
verify_flags:
  - 'Upgraded 2026-09-22 from a REPORTED stub (docs/lit/bunker1983.md and
    private/cache/lit_intake_2026-09-21/notes/bunker1983.md, both resting on fornasini2015''s two
    citations of this paper and on unread search-engine summaries) after the owner obtained the
    PDF by hand. Held and read in full, all 8 pages (437-444). Every claim below is taken from the
    paper''s own text, with page and equation numbers; nothing below rests on fornasini2015 or a
    search summary any more. The general (non-centroid) cumulant-moment formula for C5 (p. 441)
    was cross-checked by substituting p1=0 and confirming it reduces exactly to the paper''s own
    centroid-referenced C5 on the same page; the printed C6 polynomial (also p. 441) was NOT
    transcribed into this note because one small-print term could not be read with confidence and
    did not match the well-known standard identity closely enough to assert either reading.'
verified_date: 2026-09-22
summary: >
  Introduces the EXAFS cumulant-expansion "ratio method": fitting the log-amplitude and phase of
  a disordered sample's EXAFS signal against a low-disorder reference of the same material as
  polynomials in k^2 (amplitude, even cumulants) and k (phase, odd cumulants), rather than by
  nonlinear least-squares over interatomic distances. Derives the cumulant-generating-function
  relation (Eq. 12), the explicit cumulant-from-shifted-moment recursion through fifth order
  (Eq. 14-15), and states that the cumulants of a convolution of distributions are simply the sums
  of the separate cumulants.
loci:
  - methods/06
  - methods/11
  - THEORY
section: method-anchors
---

# bunker1983

VERIFIED. Held and read in full: all 8 pages, 437-444. Upgraded from a REPORTED stub that rested
entirely on fornasini2015's two citations of this paper and on unread search-engine summaries.
Every claim below is checked directly against this paper's own text, with page and equation
references throughout.

## What it does

Grant Bunker (Dept. of Physics, University of Washington, Seattle), received 6 August 1982,
published in Nuclear Instruments and Methods **207**, 437-444 (1983). That is the journal name
exactly as printed in the paper's own running header. The Crossref-indexed and previously
recorded journal name, "...in Physics Research," is kept in the frontmatter since it was already
independently confirmed there and the two are the same serial either side of a mid-1980s title
change. The abstract states the paper's scope:

> "When moderate disorder is present, the cumulant expansion/ratio method approach to EXAFS data
> analysis offers an attractive alternative to nonlinear least-squares fitting of the data.
> Analysis by nonlinear fitting, moment expansion, and cumulant expansion are compared, and useful
> formulae are derived." (p. 437)

The Introduction (p. 437) also gives, ahead of any cumulant machinery, a quantitative bound on how
many independent parameters a filtered spectrum can support: naively varying six ligand distances
of a distorted shell one by one is unrealistic, because Fourier filtering with a k-window of width
ΔK and an r-window of width ΔR reduces the number of degrees of freedom in the data to
(2ΔKΔR)/π: "the number of K data points times the fraction of the total r space contained in the
pass band" (p. 437), a Shannon/sampling-type count of the independent data points the two window
widths jointly admit.

The physical setup (p. 437-438, Eqs. 1-3): the EXAFS signal chi(k) from a shell of N identical
atoms is an integral of a radial distribution rho_1(r) against a nonlinear phase 2kr+delta(k),
carried by a mean free path B(k). Section 1 defines the "effective" distribution
P(r,gamma) = [rho_1(r)/r^2] e^(-2 gamma r) (Eq. 2a), whose Fourier transform P-tilde(r-bar,gamma;k)
reproduces chi(k) up to the known B(k) (Eq. 3), and (Eq. 5a) expands P-tilde in shifted power
moments P_n of that effective distribution about a chosen origin r-bar.

## The moment expansion breaks down where the cumulant expansion does not

Section 3, "Relating the moment and cumulant expansions," is the paper's methodological core.
With d(gamma)/dk = 0, the log-amplitude and phase split into even and odd shifted moments
(Eq. 6-7). To low order, ln[A(k)/NB(k)] ~= ln P_0 (1 - 2k^2 p_2 + ...), with p_n = P_n/P_0. Its
central claim, verbatim:

> "In contrast with the power moments, which must describe the detailed shape of an approximately
> Gaussian" |P-tilde(k)| (the paper's own bars-and-tilde notation for the log-amplitude), "the
> cumulants converge rapidly because they measure the slowly varying deviations from a straight
> line. In fact, it is often sufficient to consider only the first four cumulants," C1 through C4
> (p. 440).

> "In a sense the higher-order cumulants measure the deviation of P(r) from a Gaussian function,
> whereas the shifted moments measure the deviation of P(r) from a delta function. The cumulant
> expansion is therefore a better-behaved expansion to which to fit experimental data than is the
> moment expansion." (p. 440)

and, immediately before that, the Gaussian special case used to motivate it: "if P(r) is a
Gaussian function of" (r minus its centroid r-bar), "all cumulants higher than the second vanish,
whereas the power moments do not (for example," C4 = 0 = p4 - 3p2^2) (p. 440). Figure 1 (p. 440)
is a worked failure mode: fitting ln|P-tilde(k)| vs k^2 as a straight line over a k^2 range of
16-64 Angstrom^-2, for a distribution with true sigma^2 = 0.0054 Angstrom^2, recovers an apparent
`sigma^2` = 0.0070 Angstrom^2, about 30% high from curvature the higher cumulants would absorb,
which the text calls "an easy mistake to make in a routine analysis" (p. 440).

## The cumulant machinery (Appendix A, p. 441-442)

Cumulants are defined by the standard generating function (Eq. 11, citing Kubo 1962, for any
normalized distribution of a variable x):

    <e^(xi x)> = exp[ sum_{n=0}^inf xi^n C_n / n! ],  n >= 0,  with C_0 = 0 when normalized.

Eq. (12) is the gamma-dependent form for P(r,gamma). Amplitude carries only even cumulants and
phase only odd ones (Eq. 13a-b). Eq. (14)-(15) give the explicit cumulant-from-shifted-power-moment
recursion. At a general origin r-bar (Eq. 14 and the unlabeled lines following it, p. 441):

    C1 = p1
    C2 = p2 - p1^2
    C3 = p3 - 3 p2 p1 + 2 p1^3
    C4 = p4 - 4 p3 p1 - 3 p2^2 + 12 p2 p1^2 - 6 p1^4
    C5 = p5 - 5 p1 p4 + 20 p1^2 p3 - 60 p1^3 p2 - 10 p2 p3 + 30 p1 p2^2 + 24 p1^5

and, choosing r-bar as the centroid of the effective distribution so that p1 = 0, these reduce
(Eq. 15) to:

    C0 = ln P0,   C1 = 0,   C2 = p2,   C3 = p3,   C4 = p4 - 3 p2^2,   C5 = p5 - 10 p3 p2

(the paper continues the same pattern through a sixth-order term at the centroid, not transcribed
here per the verify_flags note above). Substituting p1=0 into the general C4 and C5 formulas
reproduces the centroid C4 and C5 exactly, which is a useful internal consistency check on the
transcription. Table 1 (p. 442) tabulates the cumulants of three simple `effective` distributions:
a Gaussian has only C_2 = sigma^2 nonzero, with every C_n (n>2) exactly zero. A one-sided
(`skewed`) exponential has C_n(n>1) = (n-1)!/alpha^n, all positive. A sum of N delta functions at
r_n = R + Delta_n has C_2 = (1/N) sum(Delta_n^2) and C_4 = (1/N) sum(Delta_n^4) -
(3/N^2) sum(Delta_n^2) sum(Delta_n'^2), which the table's own footnote flags as negative for N<=3.

The property this record leans on hardest: "the cumulants of the distribution which results from
the convolution of other distributions are simply the sums of the cumulants of the separate
distributions" (p. 441-442): for P(r) = P^(1) * P^(2), C_n = C_n^(1) + C_n^(2) at every order,
used immediately afterward to note that convolving the table's Gaussian and exponential entries
can reproduce "any amount of skewing or broadening."

## Section 4, Summary (p. 440), and the appendices

The paper's own two-point summary of its recommended approach:

> "(a) Instead of fitting the EXAFS chi(k) data with a multiplicity of correlated parameters,
> adopt a statistical viewpoint and describe the various distances in the shell by a probability
> distribution... The idea is to reduce the dimension of the parameter space by changing variables
> (from r_i, atomic distances) to C_n (cumulants). This is a model-independent method..."
>
> "(b) Separate the filtered EXAFS data into amplitude and phase functions and plot them as in the
> ratio method. This decouples the even and odd cumulants... The cumulant description is more
> appropriate and better conditioned than the power moment description, and is the one used
> implicitly in the ratio method in any event." (p. 440)

Appendix B (p. 442-443) treats a k-dependent mean free path as a perturbation added on top of the
gamma_0-referenced cumulant expansion. Appendix C (p. 443) extends the ratio method to a shell
containing two atom types, and states explicitly where it fails: "If phi_1 - phi_2 approaches pi
... the analysis becomes difficult in all but the simplest cases" (p. 443), where a nonlinear fit
to the amplitude's minimum position is needed instead.

## Use in this record

This is the closest methodological precedent this search has found for the record's own
programme of reading a physical distribution's higher moments and cumulants directly off a
measured spectral signal, order by order, instead of fitting a handful of shape parameters.

- The paper's central claim (that cumulants `converge rapidly` and are `better conditioned` than
  power moments for a nearly-but-not-quite-Gaussian distribution) is the same argument this
  record makes for climbing a windowed-cumulant ladder instead of fitting raw high-order moments
  of the AC-Stark-broadened line. Eq. (14)-(15)'s cumulant-from-moment recursion (C1-C5, checked
  for internal consistency above) is an independent literature cross-check for this record's own
  moment-to-cumulant conversion in `rb5s6s/cumulants.py`, arrived at in an unrelated spectroscopy.
- The stated convolution rule (cumulants of a convolution sum termwise) is the textbook property
  this record's own convolution-condition discussion (that a convolution is a condition,
  not a form) depends on wherever it is invoked, and Bunker's Fig. 1 is a worked example of the
  failure mode when a cumulant-bearing curvature is mis-read as a single low-order moment by
  fitting over too narrow a domain, structurally the same risk as extracting a third cumulant
  from too coarse a window or too narrow a noise ladder rung.
- Table 1's delta-function-sum entry (C_4 negative for N<=3 and cumulants beyond second order are, in
  the paper's own words, "not in general positive definite") is a caution worth carrying before
  reading a negative higher moment or cumulant as necessarily a specific physical mechanism, not
  a small-N or model artefact of the sampling.

## Limits

The ratio method as derived here assumes a single coordination shell (or, with Appendix C, at
most two atom types within one shell) and a k-independent or slowly k-dependent mean free path.
The "model independence" claimed is model independence in the shape of the distance distribution,
not independence from the ratio method's own structural assumptions (one shell, a reference
standard similar enough to the unknown). Its cumulant machinery is one-dimensional, over a scalar
EXAFS wavenumber k. This record's own windowing and moment machinery is over a scan
frequency/time axis, a structurally similar but physically distinct convolution problem.
