---
citekey: schmidt2011b
type: article
authors:
  - Schmidt, O. A.
  - Schulze, C.
  - Flamm, D.
  - Brüning, R.
  - Kaiser, T.
  - Schröter, S.
  - Duparré, M.
title: 'Real-time determination of laser beam quality by modal decomposition'
journal: Opt. Express
volume: 19
number: 7
pages: 6741-6748
year: 2011
doi: 10.1364/OE.19.006741
arxiv: '1101.4610'
pdf: PDF_papers/Schmidt_2011_laser-beam-quality-M2-real-time-modal-decomposition.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:1101.4610v2 electronic reprint of the Optics Express article, posted with
    the publisher''s permission. Read in full on 2026-09-22. The citekey carries a b because
    schmidt2011 on this shelf is a different paper (van der Waals near a nanosphere).'
verified_date: 2026-09-22
summary: >
  M^2 as a sum over the modal content of a beam: expanded in Hermite-Gaussian modes, the second-moment
  width of an incoherent mode mixture is the fundamental waist times a weighted sum of (2m+1), so the
  ISO beam propagation ratio follows from the modal weights alone, checked against caustic
  measurements to within 13 per cent. The citable statement of the decomposition this record's M^2
  profiles are built on, and of the fact that a knife-edge width is not the ISO width on a
  non-Gaussian beam.
loci:
  - methods/03
section: method-anchors
---

# schmidt2011b

VERIFIED against the held reprint (scope in `verify_flags`).

## The decomposition

A beam from a resonator of rectangular symmetry is expanded in Hermite-Gaussian modes HG_mn of fundamental waist w0, with complex coefficients whose squared moduli are the relative powers of the modes (their Eqs. 1 and 2). Modes of different mode groups beat at different frequencies and average out over a camera exposure, so the recorded intensity is the sum of the mode groups' intensities (Eq. 6). The ISO 11146 beam propagation ratio is built from second-order moments of the intensity, and for Hermite-Gaussian content it reduces, verbatim, to this: "In other words, the ratio of the beam waist diameter to the one of the fundamental Gaussian beam determines the M 2 factor." The spatial second moment in x is w0^2/4 times the power-weighted sum of (2m+1) over the modes (Eq. 7), with a cross moment for rotated modes (Eq. 8), which together give M^2 from the modal weights (Eq. 11).

On what the fundamental mode means, verbatim: "Any deviation from the ideal diffraction-limited Gaussian beam profile can be attributed to the contribution of higher order modes, leading to M 2 > 1."

## The measurement

A computer-generated hologram used as a correlation filter reads the weights of the 21 modes with m+n up to 5 from one far-field image, on an end-pumped Nd:YAG laser at 1064 nm whose off-axis pumping excites HG_m0 modes. Against the ISO caustic method on seven mode mixtures the largest deviation is 13 per cent in M^2 along x and 5 per cent along y. Noise inflates the hologram's value at low M^2 and the truncation of the mode set at m+n = 5 deflates it at high M^2 (Section 3.2).

## The caution about widths

From the introduction, verbatim: "the existence of different archaic approaches like the variable aperture or moving knife-edge method, which are known to produce deviant results, has shown the need for a standardization of the definition." And, verbatim: "Siegman pointed out that the use of measurements not conform to the ISO standard will result in values for M 2 , which are not comparable to each other [1]."

## Use in this record

The plan's M^2 profiles for the light-shift distribution rest on this decomposition: a beam of M^2 above one is a mixture of higher modes whose intensity profile, and so the shape of the shift distribution, differs from the Gaussian's, which a rescaled waist does not reproduce. The paper supplies the width relation and the ISO definition. The mode weights of the 2025 beam are not known, and no number here stands for them.

It also bears on chapter 8's knife-edge session, which the thesis describes as returning w0 with no line-shape model. On a Gaussian that holds. On a clipped or multimode beam a knife-edge's clip-level width and the ISO second-moment width are different quantities, which is the paper's point about knife-edge methods, so the session's product is a profile to be read against the model's profile, not a single width to be inserted. The primary reference the paper cites for this is Siegman's 1998 tutorial, which this shelf does not hold.

Related on this shelf: `karman1998` and `lim2021` (the focal fields of truncated beams).
