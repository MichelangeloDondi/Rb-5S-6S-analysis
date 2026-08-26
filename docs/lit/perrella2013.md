---
citekey: perrella2013
type: article
authors:
  - Perrella, C.
  - Light, P. S.
  - Anstie, J. D.
  - Stace, T. M.
  - Benabid, F.
  - Luiten, A. N.
title: 'High-resolution two-photon spectroscopy of rubidium within a confined geometry'
journal: Phys. Rev. A
volume: 87
pages: 013818
year: 2013
doi: 10.1103/PhysRevA.87.013818
arxiv: null
pdf: PDF_papers/theses/Perrella_2013_PhD-thesis_nonlinear-spectroscopy-Rb-hollow-core-fibres.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'HELD VIA THE THESIS, NOT THE ARTICLE. The APS paper is paywalled and has no
    arXiv preprint (checked 2026-07-30). What is held is the first author''s
    open-access UWA PhD thesis, "Non-Linear Spectroscopy of Rubidium in
    Hollow-Core Fibres" (Feb 2013, 235 pp, supervisors Luiten and Light), which
    REPRINTS this paper in full including its abstract, setup and figures.
    Quotations below are from that reprint. Page and figure numbers are the
    article''s own.'
  - 'The two questions this note previously carried as OPEN are now SETTLED from
    that reprint, and both had been guessed correctly in one case and wrongly in
    the other -- see the body. Excitation: TWO-COLOUR, 780 + 776 nm. Fibre:
    kagome HC-PCF, 45 um CORE DIAMETER, 40 cm, at 90 C.'
verified_date: 2026-07-31
summary: >
  Two-photon spectroscopy of THERMAL Rb vapour in a hollow-core fibre
  (Adelaide/Luiten with Benabid), 5S1/2 -> 5D5/2, linewidths as narrow as
  10 MHz, >90% nonlinear absorption, absorption sustained to 9 GHz of
  intermediate-state detuning. Held via the first author's
  open-access PhD thesis, which reprints the paper. TWO CORRECTIONS TO THIS
  NOTE followed: the excitation is TWO-COLOUR (780 + 776 nm, an ECDL and a
  Ti:sapphire), as the 9 GHz detuning scale had suggested; and the fibre is a
  kagome HC-PCF of 45 um CORE DIAMETER at 90 C, so the mode radius is ~15 um
  and transit accounts for only 3-4 MHz of the 10 MHz -- NOT the few-micron,
  transit-limited mode this note previously inferred by reading the geometry
  backwards out of the linewidth. The thesis points at coupling to higher-order
  transverse modes, caused by the curved large-core fibre, for the remainder.
loci:
  - M9
  - P2
section: oist-lineage
---

# perrella2013

Held via the first author's open-access PhD thesis (University of Western Australia, 235 pp), which reprints the article in full. The journal article itself is paywalled with no arXiv preprint. Bibliographic details are from Crossref, and the abstract below is from the publisher listing. Page and figure numbers cited are the article's own, as reprinted in the thesis.

## The system

Two-photon spectroscopy of a thermal Rb vapor confined to the hollow core of a photonic-crystal fiber (Adelaide/Luiten group, with Benabid), driving the 5S1/2 -> 5D5/2 transition with two-colour excitation at 780 nm (an ECDL) and 776 nm (a Ti:sapphire laser). The fibre is a kagome hollow-core photonic-crystal fibre (HC-PCF) of 45 um core diameter, 40 cm long, held at 90 C.

Abstract, verbatim: "We present two-photon spectroscopy of a thermal rubidium vapor confined to the hollow core of a photonic-crystal fiber. Linewidths as narrow as 10 MHz were observed on the 5S1/2->5D5/2 transition enabling the hyperfine splitting of the excited state to be resolved. Very strong nonlinear absorption (>90%) was observed, with substantial absorption maintained over large detunings (9 GHz) from an intermediate state. These attributes make this system ideal for many frequency metrology and quantum optics applications."

## The numbers

Linewidths as narrow as 10 MHz were observed, resolving the 5D5/2 hyperfine splitting. Nonlinear absorption exceeded 90%, sustained over an intermediate-state detuning of up to 9 GHz. Pressure broadening is estimated at about 12 kHz, negligible against the observed width.

## Validity

Saha (2010) demonstrated degenerate two-photon Rb spectroscopy at 778 nm in a 6 um-core photonic band-gap fibre, with 1% absorption at 1 mW. This work extends the platform to near-complete absorption and hyperfine-resolved linewidths, in a much larger core and with two-colour rather than degenerate excitation. Where slepkov2010 models the AC-Stark shift through a Gaussian-core guided mode, this paper measures the resulting lineshape directly. The reported 10 MHz linewidth is not decomposed into a full budget: the thesis attributes the width beyond transit and pressure broadening to coupling into higher-order transverse optical modes, caused by the fibre being curved between the vacuum chambers combined with its large core diameter, without quantifying that contribution.

## Use in this record

Applying this repository's own transit-broadening formula to the fibre's stated geometry at 90 C (a mode radius of 14.6-15.8 um, the 0.65a-0.70a convention for a 45 um core) attributes 3.69-3.98 MHz of the reported 10 MHz total to transit time, leaving roughly 6 MHz as the unquantified mode-coupling contribution.
