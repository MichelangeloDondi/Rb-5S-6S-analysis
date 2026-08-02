---
citekey: bennett1999
type: article
authors:
  - Bennett, S. C.
  - Roberts, J. L.
  - Wieman, C. E.
title: 'Measurement of the dc Stark shift of the 6S→7S transition in atomic cesium'
journal: Phys. Rev. A
volume: 59
number: 1
pages: R16--R18
year: 1999
doi: 10.1103/PhysRevA.59.R16
arxiv: null
pdf: PDF_papers/Bennett_1999_Cs-6s-7s-dc-Stark-shift.pdf
held: true
status: VERIFIED
routing: []
verify_flags:
  - 'Rapid Communication, three pages (R16-R18). DOI built from the printed
    volume/issue/starting page, not itself printed on the PDF. VERIFY at
    submission.'
verified_date: 2026-08-03
summary: >
  Measures the dc Stark shift slope of the Cs 6S to 7S transition,
  k = 0.7262(8) Hz (V/cm)^-2, agreeing with ab initio theory to 0.3% and
  removing what was then the largest experiment-theory gap in low-lying Cs
  structure. Later revised about 0.5% low by quirk2024. The Cs 6S-7S
  differential polarizability this k encodes is the electronic sibling of
  the Rb 5S-6S quantity behind this repository's DELTA_ALPHA_AU, but the
  measurement is DC while the repository's is AC at 993 nm, so it is a
  methodological precedent, not a numeric cross-check.
loci:
  - THEORY
section: prior-art
---

# bennett1999

Read in full from the held PDF, 2026-08-03.

## Verbatim abstract

> "We have measured the dc Stark shift of the 6S→7S transition in atomic
> cesium using laser spectroscopy. The result of our experiment is
> 0.7262(8) Hz (V/cm)^-2. This value disagrees with a previous experiment
> but is within 0.3% of the value predicted by ab initio calculations.
> This measurement removes the largest outstanding disagreement between
> experiment and ab initio theory of low-lying states in atomic cesium."

## What it does

A JILA/NIST group drives the normally forbidden Cs 6S(F=3) to 7S(F=3)
transition with 540 nm dye-laser light inside a static electric field
between two molybdenum plates 0.48994(25) cm apart. The dc field mixes
opposite-parity states and opens a Stark-induced electric-dipole channel
between the two S states. The line is scanned at a fixed low field
(1 kV/cm) and at six higher fields (5 to 10 kV/cm). The frequency
difference between the two line centers, Delta_nu_Stark, follows

    nu_Stark = (alpha_7S - alpha_6S) / (4 pi) * E^2 = k * E^2

in atomic units (their Eq. 2), so k is the differential dc scalar
polarizability of the pair, expressed directly in Hz (V/cm)^-2. Ten
alternating scans per field pair give line centers reproducible to
0.02 MHz, and the full set is fit against a cubic-in-time baseline to
remove reference-cavity drift. The stated motivation is atomic parity
nonconservation (PNC): interpreting the Boulder Cs PNC measurement
(Wood et al., Science 275, 1759, 1997) against the Standard Model needs
the same 6S-7S Stark matrix element, and the earlier 1983 value carried a
2% gap against ab initio theory, the largest such disagreement in Cs at
the time.

## The measured numbers

- **Headline result**: k = **0.7262(8) Hz (V/cm)^-2**, a total fractional
  uncertainty of 0.11%, built from three contributions added in
  quadrature: 0.1% from the field-plate separation, 0.04% from the
  determination of Delta_nu_Stark, and 0.01% from the applied-voltage
  measurement.
- **Disagrees with the earlier measurement**: Watts, Gilbert and Wieman
  (Phys. Rev. A 27, 2769, 1983) reported 0.7103(24) Hz (V/cm)^-2, about
  2.2% lower and more than 6 sigma away on the combined bar. The authors
  could not resolve the discrepancy, noting the original analyst had
  died and his working records were gone.
- **Agrees with ab initio theory to 0.3% or better**: Dzuba, Flambaum and
  Sushkov (1989) predicted 0.7237 Hz (V/cm)^-2 (0.35% low of this
  measurement), and Blundell, Sapirstein and Johnson (1992) predicted
  0.7257 Hz (V/cm)^-2 (0.07% low).
- **A byproduct, not the target**: at the low laser power used to avoid
  saturation there is still a residual ac Stark shift of 0.21 MHz, held
  constant across a given scan set by stabilizing the intracavity power
  to 1 part in 10^5 rather than removed.
- **Fit quality**: the E^2 fit to Delta_nu_Stark(E) has reduced
  chi-squared 0.9882, a 61% probability of arising from a random draw of
  the stated errors.
- **No standalone alpha_6S or alpha_7S in this paper.** Bennett, Roberts
  and Wieman report only the slope k. A separate ground-state
  polarizability (Amini and Gould) has to be combined with k to produce
  individual state polarizabilities, which is how the later value
  alpha_7S = 6238(6) a0^3 quoted by
  [iskrenovatchoukova2007](iskrenovatchoukova2007.md) is derived, and
  which [quirk2024](quirk2024.md) revises about 0.5% down (their
  independent k = 0.72246(29) Hz (V/cm)^-2 gives alpha_7S = 6207.9(2.4)
  a0^3), a difference the two measurements' own quoted uncertainties do
  not cover.

## Bridges to the Rb 5S-6S programme

**The structural sibling.** Cesium's 6S-7S pair is the alkali nS to
(n+1)S sibling of this programme's Rb 5S-6S pair. Both are S-to-S
transitions that couple only through intervening P states in a
sum-over-states expansion, and in both atoms the differential scalar
polarizability of that pair, Delta_alpha = alpha_(n+1)S minus alpha_nS,
is the quantity theory and experiment are asked to agree on. This
repository's `constants.py` pins **DELTA_ALPHA_AU = 1093.0 a.u.**,
defined as alpha(6S) minus alpha(5S) for Rb at 993 nm, sourced from
[orson2021](orson2021.md). Bennett's k encodes the equivalent Cs
quantity, alpha(7S) minus alpha(6S), at zero frequency.

**Why the two measurements are not interchangeable.** Bennett applies a
static field between plates and reads a Stark-induced, normally
forbidden E1 transition, so k is a genuinely dc polarizability
difference with no frequency dependence to account for. This
repository's DELTA_ALPHA_AU is an ac differential polarizability
evaluated at one laser wavelength, 993 nm, where the sign is set by a
cancellation between an upward 6S-6P group and a downward 6S-5P cascade
(THEORY_NOTE.md section 5.0.1). No applied dc field appears anywhere in
the Rb programme. The archival bound there is read from lineshape
distortions at a fixed lock point, an ac shape-only bound, not from a
Delta_nu versus E^2 scan of the kind Bennett runs.

**Does it offer a scaling cross-check on the Delta_alpha chain? Not a
numeric one.** Different atom, different principal quantum number, and
dc against 993 nm mean k = 0.7262(8) Hz (V/cm)^-2 cannot be rescaled
into a Rb 993 nm prediction by any simple ratio. What it offers instead
is the role [quirk2024](quirk2024.md) and
[iskrenovatchoukova2007](iskrenovatchoukova2007.md) already carry in
this literature store: the Cs 6S-7S differential polarizability, now
known from three independent routes (this original measurement, Quirk's
later 0.04%-precision remeasurement, and Iskrenova-Tchoukova's
all-order calculation), is the closest available test in the published
literature of whether a sum-over-states calculation on an alkali nS to
(n+1)S pair gets the sign and the size right. That test already runs
through the two lit notes named above, where a properly signed
sum-over-states calculation reproduces the measured Cs differential to
a percent or better. The Rb sign question this repository carries
(Orson's implied alpha(6S) minus alpha(5S) = +1093 against this
repository's own recompute of -1145) is instead decided internally, by
the 6S radiative lifetime the two signs imply: Orson's sign needs a 6S
lifetime of 9.9 ns, 210 sigma from the measured 45.57(17) ns
([gomez2005](gomez2005.md)), while this repository's own sign gives
45.42 ns, 0.9 sigma from the same measurement (THEORY_NOTE.md section
5.0.2). Bennett's Cs number has no lever on that comparison, because it
carries no information about which Rb term dominates at 993 nm.

**Verdict.** Prior art and a methodological precedent for reading a
Delta_alpha off an nS to (n+1)S pair, and the historical origin of the
value later works cite before Quirk's remeasurement. Not a numeric
scaling cross-check on DELTA_ALPHA_AU, because the field (dc versus ac),
the wavelength, and the atom all differ.
