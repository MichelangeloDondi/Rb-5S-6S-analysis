---
citekey: bauche1988
type: article
authors:
  - Bauche, J.
  - Bauche-Arnoult, C.
  - Klapisch, M.
title: 'Transition arrays in the spectra of ionized atoms'
journal: Advances in Atomic and Molecular Physics
volume: 23
pages: 131--195
year: 1988
doi: 10.1016/S0065-2199(08)60107-4
arxiv: null
pdf: PDF_papers/Bauche_1988_transition-arrays-ionized-atoms-moments-review.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand2/audits/bauche1988.md  # partial-scope read checked against the PDF, 2026-09-22
author: agent
routing:
  - CITE
verify_flags:
  - 'Held and read for the sections named here only: pp. 131-135 (Introduction, Sect. I "Principles"
    and "Distribution Moments"), pp. 146-149 (Sect. III.B "Variance" and III.C "Skewness"), and
    pp. 189-190 (Sect. VIII.B.1.b, "Use of higher moments"), 8 of 65 pages. The DOI is read
    directly from the held PDF''s own embedded metadata (Title field:
    "doi:10.1016/S0065-2199(08)60107-4"), independently cross-checked against its ScienceDirect
    PII (S0065219908601074), which encodes the identical DOI. Sections II, IV-VII, and the rest of
    VIII-IX (pp. 137-145, 150-188, 191-192, the bulk of the review -- energy distributions of
    configuration states, spin-orbit-split arrays, comparisons with experiment, level emissivity,
    extension to more physical situations, level and line statistics) were not read and nothing
    below rests on them.'
  - 'Adversarial audit, 2026-09-22 (private/cache/lit_intake_2026-09-22_hand2/audits/bauche1988.md):
    a re-zoom of Table II (p. 148) caught this note''s first draft misreading one term of the
    variance polynomial (it had "8.998E-4(F^4)^2", a squared term; the page in fact prints a
    cross-product, "8.998E-4(F^2F^4)"). The specific numerical fragment was removed from the body
    rather than corrected term-by-term, since the remaining terms could not be transcribed with
    full confidence at the scan''s resolution either. Eq. (7)''s stated scope ("n = 1, 2" as
    printed) was also added; the note''s Use-in-this-record section had generalized it beyond what
    the equation itself claims.'
  - 'Scope extended 2026-09-22 for a thesis-writer attribution request: read pp. 189-190 also,
    Sect. VIII.B.1.b ("Use of higher moments," within VIII "Conclusion" > B "Application of the
    UTA Model" > 1 "Identification of Spectra"). This is the only passage read so far in which the
    review gives explicit practical advice on using moments beyond the skewness already covered in
    Sect. III; the advice is negative, for two stated reasons. Added to the note body as its own
    section and used to correct the Limits paragraph below, which previously read the review''s
    stance on this question as unknown.'
verified_date: 2026-09-22
summary: >
  Review of the exact theory and the approximate "unresolved transition array" (UTA) model for
  describing the thousands of lines in a highly-ionized atom's transition array through its
  intensity distribution's MOMENTS (mean energy, variance/width, skewness) rather than by
  resolving individual lines. Moments are computed exactly by a second-quantization sum rule over
  the atomic Hamiltonian (Eq. 7), and centered moments of the observed line profile add termwise
  under the convolution of the array's "stick spectrum" with an elementary (e.g. Doppler) lineshape
  (Eq. 5). Gives explicit variance and skewness formulas in terms of Slater-integral second moments
  (Eq. 34-40) and a worked numerical example (Table II, Fig. 4).
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# bauche1988

VERIFIED for the sections named in the verify_flags: pp. 131-135, 146-149, and 189-190 of this
65-page review, read directly against the held PDF.

## What it does

J. Bauche and C. Bauche-Arnoult (Laboratoire Aime Cotton, CNRS, Orsay) and M. Klapisch (Racah
Institute of Physics, Hebrew University of Jerusalem), "Transition Arrays in the Spectra of
Ionized Atoms," Advances in Atomic and Molecular Physics **23**, 131-195 (1988). The review's
subject, plainly stated: in highly-ionized-atom spectra (laser-produced plasmas, tokamaks) a
transition between two configurations with open d or f shells produces not one line but a
transition array of many thousands of unresolved lines, too numerous and too closely packed for
individual-line analysis. The review develops the statistics of that array as a spectroscopic
object, "characterized by their mean energy, spectral width, and other properties" (p. 134).

## The moment machinery (Sect. I, p. 134-135)

The observed intensity distribution of the whole array is a convolution (Eq. 2, p. 134):

    I(E) = P(E) * A(E),   A(E) = sum_ab N_a A_ab delta(E_ab - E)   (Eq. 3)

where A(E) is the array's exact "stick spectrum" (Einstein coefficients A_ab at each transition
energy E_ab) and P(E) is an elementary per-line profile (e.g. Doppler/Gaussian). The moments of a
distribution are defined the usual way (Eq. 4), mu_n[I] = integral I(E) E^n dE / integral I(E) dE,
and if P is Gaussian the centered moments of the convolution add termwise (Eq. 5):

    mu_n^c[I] = mu_n^c[P] + mu_n^c[A]

with the note immediately following (p. 134): of the profile's own centered moments, only
mu_2^c[P] (the elementary profile's variance, the Doppler width squared of an isolated line)
is useful, because "it can usually be measured directly on the spectrum". That is, of the
elementary profile's own moments, only its variance carries information
the array analysis needs. The rest are known/measured separately or simply irrelevant to A(E)'s
extraction. The array's own moments (Eq. 6) are then the target:

    mu_n[A] = integral A(E) E^n dE / integral A(E) dE = sum_ab N_a A_ab E_ab^n / sum_ab N_a A_ab

Section I.B ("Distribution Moments," p. 135) fixes the vocabulary used throughout: the first
moment mu_1 is the distribution's mean value, the quantity sigma = [mu_2 - (mu_1)^2]^(1/2) is its
mean deviation, the moment mu_3 is used for the description of the asymmetry, and mu_4 for the
flattening (p. 135). A key methodological distinction the review draws explicitly and repeatedly:

> "It is important to note, at this point, that a clear distinction must be made between what we
> call the theory of transition arrays and the model of unresolved transition arrays (UTA). The
> former, which addresses the computation of various distribution moments like mu_n[A], is exact.
> ... The latter (UTA model) is an approximation which consists in assuming a specific analytical
> shape for I(E), such as Gaussian or skewed Gaussian, in which a few moments mu_n[I] -- in this
> case n<=3 -- are taken equal to mu_n[A], the others being neglected." (p. 135)

The moments themselves, for a single configuration C, are computed exactly via a sum rule over the
atomic Hamiltonian H (Eq. 7): mu_n(C) = sum_{m in C} <m|H|m>^n / g_C, with g_C the configuration's
total state count: moments obtained from the Hamiltonian's diagonal matrix elements directly,
with no need to diagonalize or resolve individual levels. As printed, Eq. (7) is stated for the
first two moments of a single configuration's own state-energy spread ("n = 1, 2"). The fuller
machinery for an n-th order moment of a full transition array between two configurations (what
Sect. III's variance and skewness formulas build) is the more elaborate, later apparatus, not a
direct n-fold extension of Eq. (7) itself.

## Variance and skewness of a transition array (Sect. III.B-C, p. 146-149)

The variance v(C-C') = mu_2 - (mu_1)^2 of an array's transition energies (Sect. III.B) splits, in
the strict central-field approximation, into an electrostatic part v_G and a spin-orbit part v_A
(Eq. 36-37), each a sum over the array's open subshells weighted by occupation-number factors
N_i(4l_i - N_i +- 1)/(4l_i +- 1) times "elementary variances" v_G(l^2 - ll') tabulated (in the
cited Bauche-Arnoult et al. 1979) as explicit polynomials in the Slater integrals. Table II
(p. 148) gives the worked numerical example for the d^(N+1) - d^N p array: a single bracketed
polynomial of about a dozen numerically-coefficented cross- and self-product terms in five Slater
integrals (F^2, F^4, F'^2, G^1, G^3), multiplied by N(9-N) and added to a separate three-term
spin-orbit piece in zeta_d and zeta_p (the footnote states F^k=F^k(d,d), F'^k=F^k(d,p),
G^k=G^k(d,p), with the printed numbers scaled by 1e-3). The individual numerical coefficients and
exactly which Slater-integral products they multiply are not reproduced here: on a careful
re-read at higher zoom this record's own first attempt at transcribing a short fragment of that
polynomial was caught misreading one term (a squared self-product where the page in fact shows a
cross-product), and the remaining terms could not be re-transcribed with full confidence at the
scan's resolution either. See the audit file. Section III.C defines the skewness via the
standardized third cumulant (Eq. 40):

    alpha_3 = mu_3^c / (mu_2^c)^(3/2),   with mu_2^c = v,   mu_3^c = mu_3 - 3 mu_2^c mu_1 - (mu_1)^3

and states that, unlike the variance, the triple-Slater-integral products entering mu_3^c can be
computed exactly only for some term types (those of degree <=3 in N), with an approximate
hydrogenic-radial-function method used for the rest (p. 149). Figure 4 (p. 149) is a worked
comparison for the 4d^8-4d^7f array of praseodymium XVI: the exact, line-by-line envelope against
(b) a one-moment Gaussian (mu_1, v) and (c) a three-moment skewed Gaussian (mu_1, v, mu_3). The
skewed-Gaussian visibly tracks the true asymmetric envelope far better than the plain Gaussian.

## Advice on higher moments (Sect. VIII.B.1.b, p. 189-190)

In its concluding chapter, under "B. Application of the UTA Model" > "1. Identification of
Spectra" > "b. Use of higher moments" (p. 189), the review first credits the skewness (mu_3, via
the skewed Gaussian already covered in Sect. III above) with two practical benefits over the
plain Gaussian, while denying it a third: introducing it "does not give a more realistic shape to
the arrays," but "it does yield better values for the energy of the transition peak," conditional
on already having a reliable way of estimating the configurations' energies, and causes "an
important reduction of the FWHM," which helps the normalization used to extract intensities and
"leaves less doubts on the presence or absence of satellites" (p. 189).

On going beyond the skewness, the review is explicit and negative: "it is not advisable to try
and obtain higher moments" (p. 189), for two stated reasons. First, "the formulas for these
become increasingly cumbersome" (p. 189). Second (p. 190): the populations of the levels are not
in general proportional to their statistical weights, and this must influence the array's true
shape at some point, while "computing these in complex spectra is not an easy task." The review
cites a level-by-level calculation for the Co-like Xe 3d^9-3d^84f array (Klapisch et al., 1987)
that finds overpopulated quasi-metastable levels making the array appear double-peaked even at a
laser-produced-plasma density of n_e = 10^20 cm^-3, and draws the conclusion: "attempting to
obtain shapes, without knowing how to account for the population repartition, is an illusion"
(p. 190).

## Use in this record

This is a full, independent atomic-physics precedent for treating a spectral line's shape through
its moments instead of by resolving its structure, in a completely different regime (a plasma's
many-thousand-line transition array, not this record's own single Doppler/transit-broadened
two-photon line):

- Eq. (7)'s exact sum rule, mu_n(C) = sum_m <m|H|m>^n / g_C, computes a spectral distribution's
  moments directly from the generating Hamiltonian, with no fitting step: the atomic-physics
  analogue of this record's own forward-model moments, which are likewise computable exactly from
  the model, not only estimated from finite synthetic or real traces.
- Eq. (5)'s statement that centered moments of a convolution add termwise, together with its own
  qualifier that "only mu_2^c[P] is useful," is a second, independent literature (alongside
  bunker1983's cumulant version of the same theorem) making the identical point this record
  already treats as a governing rule: a convolution is a condition, not a form. A convolution's moment
  bookkeeping is exact and simple exactly when the convolving kernel's own shape is either fixed,
  measured, or irrelevant beyond one low moment, and it breaks down, as this record's own kernel
  does at a tight waist, when the kernel depends on the variable being convolved over.
- The explicit theory/UTA-model distinction (p. 135), that moments are exact while a shape
  reconstruction from a truncated set of moments is an approximation whose quality depends on how
  many are kept, is precisely the question this record's own moment-and-cumulant programme (mu_2 through
  mu_12 and their ratios) asks of its own windowed line, and Fig. 4's worked example (one moment
  vs. three moments vs. the exact line) is a directly relevant, already-published illustration of
  how much shape information each additional moment order buys.

## Limits

Only the general moment/variance/skewness machinery, plus the review's own advice on higher
moments quoted above (Sect. VIII.B.1.b, p. 189-190), was read. The review's spin-orbit-split-array
formulas (Sect. II, unread), its dedicated UTA-vs-experiment comparison section (Sect. IV,
unread), and its level- and line-statistics section (Sect. VII, unread) may still carry further
material relevant to this record's higher-order programme (mu_4 and above) that this partial read
does not cover. But the one place this review states its own general advice on the question is
read above, and the advice is a caution against pursuing moments beyond the skewness, not an
endorsement.
