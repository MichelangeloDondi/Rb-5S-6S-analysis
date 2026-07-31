---
citekey: leonard2015
type: article
authors:
  - Leonard, R. H.
  - Fallon, A. J.
  - Sackett, C. A.
  - Safronova, M. S.
title: 'High precision measurement of the 87Rb D-line tune-out wavelength'
journal: Phys. Rev. A
volume: 92
pages: 052501
year: 2015
doi: 10.1103/PhysRevA.92.052501
arxiv: '1507.07898'
pdf: PDF_papers/Leonard_2015_Rb87-D-line-tune-out-wavelength.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'THE 2017 ERRATUM IS NOW HELD AND READ -- see leonard2017, whose PDF is
    PDF_papers/Leonard_2017_ERRATUM_Rb87-D-line-tune-out-wavelength.pdf (it was
    held under the bare APS filename PhysRevA.95.059901.pdf and renamed
    2026-07-31). It SUPERSEDES this paper''s headline. The
    tune-out becomes 790.032326(32) nm, the ratio R = 1.99217(3), and theory
    790.0315(7). Quote the ERRATUM values, not this paper''s. The erratum is not
    on arXiv -- the arXiv record (1507.07898) is pre-erratum through v3 -- which
    is why this stood unverified until the PDF was obtained.'
  - 'This paper reports FIVE different wavelengths and they are easy to confuse:
    the headline 790.032388(32) (abstract; the constrained fit, given as
    790.032388(29) in the text), the unconstrained fit 790.032439(35), a raw
    regression intercept 790.03232, and theory 790.0312(7) and 790.02568.
    Quote the headline unless a specific fit is meant.'
verified_date: 2026-07-31
summary: >
  The source of three things rb5s6s/polarizability.py depends on, and it had no
  note until 2026-07-31 despite that. (1) The 5S scalar tune-out validation
  anchor -- measured with a BEC interferometer to fifty times better than
  previous work, and reported here as 790.032388(32) nm but CORRECTED BY THE
  2017 ERRATUM TO 790.032326(32), which is the value the repo now uses.
  (2) TAIL_5S = 0.097, which is Leonard's Table II
  (n>12) tails, 0.022(22) for P_1/2 plus 0.075(75) for P_3/2 -- both verified
  against the held PDF. (3) CORE_5S = 8.709(93), their "Core + vc" row, also
  verified. Also gives the matrix-element ratio |<5P3/2||d||5S1/2> /
  <5P1/2||d||5S1/2>|^2 = 1.99221(3) -- ALSO SUPERSEDED, the erratum making it
  1.99217(3) -- a 100-fold improvement on previous experiment, and the 5P-12P
  energies the module uses. A further erratum result worth keeping: the
  apparent conflict with Lamporesi et al.'s 790.018(2) nm is not a discrepancy
  but a different ground state (theirs F=1); carried to F=1 this measurement
  gives 790.017496(32) against a 790.0167(7) theory, and they agree.
loci:
  - M16
  - THEORY
  - constants
section: method-anchors
---

# leonard2015

**Read (relevant sections) 2026-07-31** from the held arXiv PDF (1507.07898),
fetched after an audit found the repository had been citing a tune-out value
that appears in no published source.

## Why this note exists

`rb5s6s/polarizability.py` has depended on this paper since M16 — for the
validation anchor, for two numerical constants, and for the 5P–12P energies —
without a note. That gap is the reason a wrong tune-out value survived: there
was nowhere for the correct one to be checked against.

## What the module takes from it, all verified against the held PDF

| module constant | Leonard source | verified |
|---|---|---|
| tune-out anchor | 790.032388(32) nm (abstract; constrained fit) — **superseded**; the module's anchor is the erratum's 790.032326(32), see [leonard2017](leonard2017.md) | yes, and the erratum value verified against its own held PDF |
| `TAIL_5S = 0.097` | Table II, (n>12)P₁∕₂ **0.022(22)** + (n>12)P₃∕₂ **0.075(75)** | yes, sums exactly |
| `CORE_5S = 8.709`, σ 0.093 | Table II, "Core + vc" **8.709(93)** | yes |
| 9P–12P energies | Table II | yes |

The `±100%` uncertainty the module puts on the tail is Leonard's own: both tail
entries carry an uncertainty equal to their value.

## The value that was wrong, and what it should have been

Until 2026-07-31 the repository cited **790.03235(3)**. That number appears
nowhere in this paper. Searching the full text turns up five wavelengths —
790.032388(32), 790.032439(35), 790.03232, 790.0312(7), 790.02568 — and it is
none of them, nor a rounding of any. Its origin is unknown.

**Nothing downstream turns on the correction.** The computed tune-out is
790.0339 nm, so the agreement is 1.51 pm against the 2015 value and 1.55 pm
against the wrong one — the claim was, and remains, "≈2 pm". The correction is
a provenance fix, not a physics one.

## The erratum, now HELD and VERIFIED

**Superseded 2026-07-31.** This section used to say the erratum was REPORTED
from an external literature pass, "has not been verified here", and "should be
obtained". It has been: see [leonard2017](leonard2017.md), held and read from
the APS PDF. Everything the external pass reported was right —
**790.032326(32)** and R = 1.99217(3), from a ground-state Zeeman shift omitted
from $\omega'$ — and the erratum adds a corrected theory value, 790.0315(7) nm,
plus the resolution of the apparent Lamporesi conflict (an $F=1$ versus $F=2$
difference, not a discrepancy).

The 0.062 pm shift is twenty-five times smaller than the model's ~1.6 pm
agreement, so it changes no conclusion; what changed is that the repo's anchor
is now quoted from a document it holds. **`TAIL_5S` and `CORE_5S` remain
assumed-untouched, not checked**: they come from this paper's theoretical
decomposition table rather than from the measured tune-out, and the erratum
corrects the measurement analysis, so it should not reach them — but the erratum
does not say so explicitly and the table was not re-derived.
