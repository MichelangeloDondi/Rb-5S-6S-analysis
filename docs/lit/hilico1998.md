---
citekey: hilico1998
type: article
authors:
  - Hilico, L.
  - Felder, R.
  - Touahri, D.
  - Acef, O.
  - Clairon, A.
  - Biraben, F.
title: 'Metrological features of the rubidium two-photon standards of the BNM-LPTF and Kastler Brossel Laboratories'
journal: Eur. Phys. J. Appl. Phys.
volume: 4
pages: 219--225
year: 1998
doi: 10.1051/epjap:1998263
arxiv: null
pdf: PDF_papers/Hilico_1998_Rb-two-photon-frequency-standard-metrology.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand2/audits/hilico1998.md  # full 7-page read against the PDF, 2026-09-22
author: agent
routing:
  - CITE
verify_flags:
  - 'Held and read in full, all 7 pages (219-225), 2026-09-22. DOI confirmed via CrossRef
    (api.crossref.org/works/10.1051/epjap:1998263): title, authors, journal, volume and pages all
    match the held PDF exactly. This is a DIFFERENT transition (5S1/2 to 5D5/2 two-photon, 778 nm)
    from this record''s own 5S-6S line at 993 nm; it is held as a metrology and systematics-budget
    anchor for Doppler-free two-photon Rb spectroscopy generally, not as a source of any constant
    this record''s code uses.'
verified_date: 2026-09-22
summary: >
  Three independent grating-diode-laser optical frequency standards locked to the Doppler-free
  5S1/2(F=3)-5D5/2(F=5) two-photon transition of 85Rb at 778 nm (385 THz), operated over three
  years. Reports a full systematic error budget (Table 2: light shift 5300 Hz typical with <140 Hz
  uncertainty, collisions 500 Hz, second-order Doppler -230 Hz, blackbody radiation -210 Hz) and a
  short-term stability of 3e-13 tau^-1/2 up to 1000 s, limited by the fluorescence-detection
  signal-to-noise ratio, with day-to-day reproducibility of order 5e-13.
loci:
  - P1
  - methods/06
section: method-anchors
---

# hilico1998

VERIFIED. Held and read in full, all 7 pages (219-225).

## What it does

L. Hilico, R. Felder, D. Touahri, O. Acef, A. Clairon and F. Biraben (Laboratoire Kastler
Brossel / BNM-LPTF, Paris) built and cross-compared three diode-laser optical frequency standards
(L1, L2, and a third, KB, connected to the other two by a 3 km fibre link, the same fibre later
characterized in debeauvoir1998) locked to the F=3 to F=5 component of the 5S1/2-5D5/2 two-photon
transition of rubidium 85 at 778 nm, inside a build-up cavity (finesse ~50, waist 420 um) with
counter-propagating Doppler-free excitation and 420 nm fluorescence (via the 6P-5S cascade)
monitored by a photomultiplier (Sect. 2, Fig. 1, p. 219-220).

## The systematic effects (Sect. 3)

The dominant and best-characterized effect is the AC Stark (light shift), proportional to
optical power and "of the order of -10 kHz in our conditions" (p. 220), that is in total at their
standard operating conditions of 24 and 26 mW of intracavity power, about -0.4 kHz per mW (Table 1). It
is removed by measuring the beat frequency between two systems as a
function of intracavity power and linearly extrapolating to zero power (Fig. 2, Table 1). Collision
shifts with the cell's own residual gas are inferred, not directly attributed to Rb-Rb collisions
alone, from extrapolating measured 5S-nD shifts to n*=3.7: "we have no information about the
collision shifts due to other impurities and consequently about their sign" (p. 222). Table 1 (p. 221)
lists the light-shift slope against each laser's intracavity power on six dates from October 1995 to
December 1997: from -392.3 to -468.6 Hz/mW against L1 and from -366.5 to -432.5 Hz/mW against L2,
against a calculated -422.2 Hz/mW for both. The text's own reading is that "the slope of the light
shift fluctuates by ± 3 % with time" (p. 221). The six L1 values span about ±9 per cent about their
mean, wider than that statement. It places the cause in the power measurement, not in the atoms: "This
may be due to a modification of the transmission of the output mirrors of the optical cavities which
get dirty with time" (p. 221), or to a varying detection efficiency of the transmitted beam through
misalignment. On the mean, the same page reads: "The mean value of the slopes is very close to the value that
can be predicted from the beam geometry and the strength of the transition" (p. 221, their ref. [17]).
Table 2, the paper's error budget, transcribed exactly:

| Physical effect | Frequency shift | Uncertainty (1 sigma) |
|---|---|---|
| Light shift | 5300 Hz (typical) | < 140 Hz |
| Collisions | not given | 500 Hz |
| Modulation | not given | < 300 Hz |
| Electronic offsets | not given | < 60 Hz |
| Second order Doppler effect | -230 Hz | < 5 Hz* |
| Black body radiation | -210 Hz | < 5 Hz* |
| Magnetic field | 0 Hz | < 1 Hz |
| Adjacent transitions | not given | < 10 mHz |

(*: assuming a 5 degC uncertainty on the temperature.) The blackbody shift is evaluated at 300 K
from separately reported shifts of the 5S1/2 (-2.8 Hz) and 5D5/2 (-181.4 Hz) levels, assumed to
scale as T^4 (p. 222).

## Stability (Sect. 4)

The short-term stability is shown to be set by the fluorescence signal-to-noise ratio: the
frequency-locked laser translates fluorescence amplitude noise into laser frequency noise through
the servo loop, quantitatively reproduced from the measured fluorescence noise spectral density
(shot-noise-consistent gain-times-excess-noise-factor GF ~ 1-1.7e6). The measured relative Allan
deviation of the L1-L2 beat is:

The relative stability varies as 3e-13 tau^-1/2, shorthand here for the source's own spelled-out
coefficient-and-exponent form, "for integration times up to
1000 s in agreement with the value predicted from the fluorescence noise analysis." (p. 224)

with a random-walk-like sqrt(tau) increase beyond 1000 s attributed to uncharacterized longer-term
drifts (aging cavity mirrors, lock-in offsets). The day-to-day reproducibility, from repeated
extrapolated L1-L2 differences over more than a year (Table 1), is "better than 200 Hz that is"
5e-13 (the source's own spelled-out "5 x 10^-13") "in relative value." (p. 225).

## Conclusion (Sect. 5, p. 225), quoted

> "We have shown that the collisions with foreign gas are responsible for the rather poor
> reproducibility. This effect will be suppressed using evacuated cells and the relative
> reproducibility should become better than 10^-13."

and the headline performance statement: "we are able to synthesize an optical frequency in the
385 THz range with a repeatability better than 200 Hz for each system, and a reproducibility of
the order of 1000 Hz, that is better than" 3e-12 (the source's own spelled-out "3 x 10^-12") "in
relative value." (p. 225).

## Use in this record

This is a metrology-grade, fully budgeted two-photon Doppler-free Rb frequency standard from the
same instrumental family as this record's own 5S-6S apparatus (grating-tuned diode laser, build-up
cavity, fluorescence detection, AC-Stark-dominated systematics), on a different line (778 nm,
5S-5D5/2) and at a different precision regime (a locked clock-grade standard instead of a
lineshape-fitting campaign). Its use here is as an external, independently-published anchor for
how a mature two-photon Rb standard partitions and quotes its systematic budget:

- Table 2 is a worked example of exactly the systematic-error factoring this record's own main aim
  calls for ("caring about systematic errors... using the twin to compute and factor out biases"):
  a dominant, well-characterized term (light shift, 5300 Hz typical but bounded to under 140 Hz
  uncertainty because its power-dependence is measured and extrapolated away) sitting alongside a
  much smaller but less controlled term (collisions, no reported central value, only a
  500 Hz uncertainty band), the same asymmetry between a modeled/removable systematic and an
  unmodeled/bounded one that this record's own AC-Stark-ramp-as-signal versus collision-shift
  budgeting must draw.
- That the light shift is this standard's largest systematic yet is handled by deliberate
  power-dependence extrapolation, instead of simply operating at low power, is a published
  precedent for this record's own stance (the light shift is modelled as a term and never capped) of treating
  the AC-Stark shift distribution as a per-configuration-characterized quantity instead of a
  systematic to be minimized by brute-force low power.
- The stability analysis's method, deriving the expected Allan deviation from an independently
  measured noise source (fluorescence shot noise) and checking the prediction against the observed
  tau^-1/2 law before trusting the number, is the same close-the-loop-before-reading-the-fit
  discipline this record enforces for its waist estimator.

## Limits

Nothing in this paper's own numbers (778 nm line, cavity-enhanced detection, three-system
comparison) is used as an input to this record's model or code. It is read here as prior art and a
systematics-methodology anchor only. Sections 1-3 and the conclusion were read closely. Table 1's
six dated rows are transcribed above. Fig. 3-5 were read for their stated conclusions, not independently
re-analyzed from the plotted data.
