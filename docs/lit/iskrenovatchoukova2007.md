---
citekey: iskrenovatchoukova2007
type: article
authors:
  - Iskrenova-Tchoukova, E.
  - Safronova, M. S.
  - Safronova, U. I.
title: 'High-precision study of Cs polarizabilities'
journal: J. Comput. Methods Sci. Eng.
volume: null
pages: null
year: 2007
doi: null
arxiv: '0705.4425'
pdf: PDF_papers/IskrenovaTchoukova_2007_Cs-polarizabilities-all-order.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Held as arXiv v1 (0705.4425, 30 May 2007). No journal-ref is carried by the
    arXiv record and none was found; the journal field above is UNCONFIRMED and
    must be established before formal citation. Cite the arXiv identifier until
    then.'
  - 'All polarizabilities in the paper''s tables are in units of 10^3 a0^3. The
    values quoted in this note have been multiplied out to a0^3 to match the
    convention of quirk2024 and rb5s6s/polarizability.py. Check the exponent
    before reusing any number from the PDF directly.'
verified_date: 2026-07-30
summary: >
  First-principles relativistic all-order (linearized coupled-cluster
  single-double) static dipole polarizabilities for Cs Ns (N=6-12), Npj (N=6-10)
  and Ndj (N=5-10), with evaluated uncertainties and a comparison table against
  every available experiment. The numbers this programme needs are
  alpha(6s) = 398.4(7), alpha(7s) = 6238(41) and alpha(8s) = 38270(280) a0^3.
  The 7s value agrees with quirk2024's MEASURED 6207.9(2.4) within the theory
  bar (0.7 sigma), a validation target for the repository's sum-over-states
  machinery. NOTE the complication in the body: their own Expt. column carries
  6238(6) from the older Bennett Stark-shift lineage, which quirk2024 replaces
  and disagrees with at about 4.6 sigma, so the target is a ~0.5% BAND, not a
  four-figure number. Also carries the 8s-6pj matrix elements that
  sieradzan2004 measured and the alpha(8s) that sets the scale of lee2010's
  measured 6S-8S light shift.
loci:
  - M16
  - THEORY
section: method-anchors
---

# iskrenovatchoukova2007

Held as arXiv v1 (0705.4425). Tables I and VIII verified against the PDF.

## The system

Relativistic all-order calculation of Cs polarizabilities and matrix
elements, by the same author group and method as the Rb calculations in
[safronova2004](safronova2004.md).

## The method

Linearized coupled-cluster single-double (SD) all-order method: single and
double excitations of the Dirac-Fock wavefunction summed to all orders, with
partial triples included in the harder cases, over a B-spline basis of
$N_B = 70$ functions per partial wave up to $l_{\max} = 6$ (the paper notes
that $N_B = 50$ is not sufficient for the highly excited states). Theoretical
uncertainties are assigned from the difference between ab initio and scaled
matrix elements, a procedure the paper states is not derived from comparison
with experiment. Several of the matrix elements used as input are themselves
experimental values substituted for theoretical ones, so the resulting
theory-versus-experiment comparison in Table VIII is only partly independent
of experiment.

## The numbers

Scalar static polarizabilities of the Cs $Ns$ sequence, converted from the
paper's tabulated units of $10^3 a_0^3$ (Table VIII):

| state | this work ($a_0^3$) | experiment ($a_0^3$) |
|---|---|---|
| 6s | 398.4 ± 0.7 | 401.0 ± 0.4 |
| 7s | 6238 ± 41 | 6238 ± 6 |
| 8s | 38270 ± 280 | 38060 ± 250 |
| 9s | 153700 ± 1000 | — |
| 10s | 478000 ± 3000 | 479000 ± 1000 |
| 11s | 1246000 ± 8000 | 1246000 ± 1000 |

Table I gives the 8s-6p matrix elements
$\langle 8s \Vert r \Vert 6p_{1/2}\rangle = 17.78(7)$ and
$\langle 8s \Vert r \Vert 6p_{3/2}\rangle = 24.56(10)\ ea_0$ (all-order SD
scaled), a ratio of 1.381, measured relative to each other by Sieradzan,
Havey and Safronova (sieradzan2004).

## Validity

These are static polarizabilities. The paper's own Table VIII experimental
entry for 7s, $6238 \pm 6$, is footnoted as derived from the Bennett et al.
(1999) 7s-6s Stark-shift measurement combined with the Amini and Gould
ground-state result, a lineage later revised by the dc Stark measurement in
[quirk2024](quirk2024.md), which gives $\alpha_{7s} = 6207.9(2.4) $, about 4.6
sigma from the Bennett-lineage value on the combined uncertainty. A static
polarizability does not by itself constrain an ac cancellation between
opposing state groups at a specific wavelength.

## Use in this record

`rb5s6s/polarizability.py` computes a Rb 5S-6S static differential
$\alpha_{6S} - \alpha_{5S} = 5167.0 - 318.3 = 4848.7$ a.u. by the same
sum-over-states construction, $\sum \vert \langle \beta \Vert r \Vert v\rangle\vert ^2$
over energy denominators, that this paper uses for Cs. The Cs 6s-7s
differential from this paper's theory, $6238 - 398.4 = 5840~a_0^3$, agrees
with the measured value in [quirk2024](quirk2024.md),
$6207.9 - 401.1 = 5807~a_0^3$, to 0.57%. The $\alpha_{7s}$ values individually
differ by 30, 0.7 sigma of the theory uncertainty and 0.5% in absolute terms.
Because the comparison above is only partly independent (see Validity), it
bounds the sign and magnitude of the sum-over-states method at the percent
level rather than providing an independent cross-check.
$\alpha_{8s} = 38270(280)~a_0^3$ gives a static Cs 6s-8s differential of
about $37900~a_0^3$, about 7.8 times the Rb 5S-6S value above
($37872/4848.7$), which sets the scale of the 6S-8S light shift measured in
[lee2010](lee2010.md) at 822 nm.
