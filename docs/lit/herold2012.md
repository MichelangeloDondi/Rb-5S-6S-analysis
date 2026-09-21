---
citekey: herold2012
type: article
authors:
  - Herold, C. D.
  - Vaidya, V. D.
  - Li, X.
  - Rolston, S. L.
  - Porto, J. V.
  - Safronova, M. S.
title: 'Precision Measurement of Transition Matrix Elements via Light Shift Cancellation'
journal: Phys. Rev. Lett.
volume: 109
number: 24
pages: 243003
year: 2012
doi: 10.1103/PhysRevLett.109.243003
arxiv: '1208.4291'
pdf: PDF_papers/Herold_2012_5s-6p-matrix-elements-light-shift-cancellation.pdf
held: true
status: VERIFIED
audit: ../../../PhD-Thesis/private/lit_audits_2026-09-21/herold2012.md  # every claim checks against the held PDF, 2026-09-21. rb5s6s/polarizability.py carries 0.3236(9), matching the paper's abstract, its Table I ("our results") and its text. The paper's own Table II (supplemental, the per-term polarizability breakdown) prints a different 0.3235(11) for the same matrix element (T0aq)
routing:
  - FEED
verify_flags:
  - 'Record confirmed on 2026-08-05 from the publisher listing and two
    independent indexes, not from the paper. Nobody here has read it. The two
    matrix elements below are quoted from the module docstring of
    rb5s6s/polarizability.py, which is the source of record in this repository
    until the PDF is held.'
  - 'Pages 1 and 2 of the held PDF (the arXiv:1208.4291v1 preprint, 21 Aug
    2012, with the published PRL typeset version not separately held) read
    against the record on 2026-09-20. The preprint abstract gives 0.3236(9)
    ea0 for the 5s-6p1/2 matrix element, one unit in the last digit above the
    0.3235(9) the rb5s6s/polarizability.py docstring quotes. The 5s-6p3/2
    value, 0.5230(8) ea0, matches exactly. Status stays REPORTED: only the
    introduction and the start of the experimental section (through the
    polarization-cancellation procedure) have been read, not the fit or the
    uncertainty budget that produced the final two numbers.'
  - 'Supersedes the reading above on the 0.3235/0.3236 gap, not the REPORTED
    status: `rb5s6s/polarizability.py` was corrected to 0.3236(9) after
    2026-09-20 (T0aq), and the held PDF''s page 4 confirms the code now
    matches the paper''s own abstract, main text and results table exactly,
    with no residual one-digit gap: the main text reads "The matrix elements
    are d6p1/2 = 0.3236(9)", and Table I''s own-results row, separately,
    reads the same 0.3236(9). Reading
    further, page 6, Table II of the Supplemental Material, the per-term
    polarizability breakdown at the two magic-zero wavelengths, finds a
    third, separate printing of the same 6p1/2 matrix element, one unit
    lower in the last digit than the abstract/text/Table I value and with a
    wider stated uncertainty: 0.3235(11) against the abstract''s 0.3236(9).
    The paper prints both. This record''s code matches the
    abstract/text/Table I reading, not Table II''s. Still REPORTED: the fit
    and uncertainty-budget sections (pages 2-4) were read for this
    reconciliation but not line by line for their own sake, and the
    Supplemental Material beyond Tables II and III is unread.'
verified_date: 2026-09-21
summary: >
  Source of the 5S to 6P reduced dipole matrix elements
  rb5s6s/polarizability.py uses, 0.3236(9) and 0.5230(8) ea0 for 5s-6p1/2 and
  5s-6p3/2. Measured by locating the magic zeros of the light shift near 421 and
  423 nm, where the shift vanishes and the ratio of the contributing matrix
  elements is fixed by that condition alone. The 6P group is one of the two
  large opposing terms in the 993 nm polarizability difference, so its
  uncertainty propagates directly into Delta alpha and into every magic
  wavelength M16 reports.
loci:
  - constants
  - M16
  - THEORY
section: method-anchors
---

# herold2012

REPORTED. Held (the arXiv:1208.4291v1 preprint). Pages 1-2 read against the
record on 2026-09-20. The fit and uncertainty budget in the later pages are
not yet read, so status stays REPORTED, not VERIFIED.

## The method

The atomic ground-state light shift passes through zero near 421 nm and
423 nm ("magic-zero" wavelengths, distinct from the magic wavelengths used
in clocks, where two states share a shift instead of one vanishing). At
each such zero the ratio of the two contributing matrix elements is fixed by
the wavelength alone, turning a matrix-element measurement into a wavelength
measurement, with no need to calibrate the absolute light intensity.

The measurement applies a sequence of up to 15 standing-wave (optical
lattice) pulses to a small 87Rb Bose-Einstein condensate, so the diffracted
population builds up coherently as the pulse count squared. The diffracted
fraction after 40 ms time of flight gives the light shift. The lattice light
is tunable between 419 and 424 nm, calibrated to 50 fm (90 MHz) against known
5s-6p transition frequencies, with a beam waist of about 110 µm. To remove a
systematic shift of the zero crossing from a small (about 1%) window-induced
ellipticity in the otherwise linear polarization, the light shift is
measured for two orthogonal linear input polarizations and averaged, which
cancels the vector light-shift contribution.

## The numbers

The `rb5s6s/polarizability.py` docstring quotes 0.3236(9) ea0 (5s-6p1/2) and
0.5230(8) ea0 (5s-6p3/2) as the reduced dipole matrix elements for 5S to 6P.
The held preprint prints the 5s-6p1/2 value in three places, and they agree
with each other and with the code: the abstract ("we find 0.3236(9) ea0"),
the main text ("The matrix elements are d6p1/2 = 0.3236(9)"), and the row
of Table I labelled with the paper's own results, which also reads
0.3236(9). The 5s-6p3/2 value, 0.5230(8) ea0, matches
exactly in all three places too. The preprint's Supplemental Material,
Table II, the per-term breakdown of the polarizability at the two
magic-zero wavelengths, prints a different value for the same 5s-6p1/2
element, on its own row labelled 6p1/2: 0.3235(11), one unit lower in the
last digit and with a wider uncertainty (11 against the abstract's 9). The
code matches the abstract, text and Table I. It does not match Table II.

## Use in this record

`rb5s6s/polarizability.py` builds the 5S and 6S dynamic polarizabilities
from a sum over states. The 5S-6P group is one of the two large opposing
terms setting the 993 nm polarizability difference, so its uncertainty
propagates directly into every magic wavelength computed for that
transition.
