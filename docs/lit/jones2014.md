---
citekey: jones2014
type: article
authors:
  - Jones, D. E.
  - Franson, J. D.
  - Pittman, T. B.
title: 'Saturation of atomic transitions using subwavelength diameter tapered optical fibers in rubidium vapor'
journal: J. Opt. Soc. Am. B
volume: 31
number: 8
pages: 1997-2001
year: 2014
doi: 10.1364/JOSAB.31.001997
arxiv: '1403.7141'
pdf: PDF_papers/Jones_2014_Rb-saturation-tapered-subwavelength-fibre-vapour.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'Held copy is the arXiv:1403.7141v2 preprint (1 Aug 2014); journal, volume, first page and DOI are
    Crossref''s record, checked 2026-09-22, and the page range is arXiv''s journal reference. Read in
    full on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  A tapered fibre of about 320 nm diameter in warm Rb vapour saturates the D2 line at tens of
  nanowatts: the transit of a few nanoseconds through the evanescent mode is too short for hyperfine
  pumping, the Doppler dips carry more Lorentzian weight from transit and fibre collisions, and the
  transmission against power fits a homogeneous saturation law with P_sat of 61 nW where the free-space
  cell needs the inhomogeneous form. The warm-vapour reference for how an evanescent mode reshapes a
  line through transit and saturation, which the nanofibre arm's warm-atom case meets.
loci:
  - methods/09
section: deep-search
---

# jones2014

VERIFIED against the held preprint (scope in `verify_flags`).

## The system

A tapered optical fibre pulled by the flame-brush technique, near the 320 nm diameter the authors give as optimal for 780 nm, guides an HE11 mode of about 1 um^2 cross-section over about 1 cm in a warm Rb vapour, in a vacuum system with a heating unit that limits Rb build-up on the fibre (their Figs. 1 and 2). A free-space vapour cell on the same laser is the comparison.

## What it finds

On the line shape, the tapered-fibre dips are better fitted with stronger Lorentzian contributions, which the authors attribute to transit-time broadening in the small mode and to collisions with the fibre. On pumping, verbatim: "In contrast, the average transit time through the ∼1 µm size beam in the TOF system is on the order of a few ns, meaning the atoms have left the mode before significant hyperfine pumping occurs." All four hyperfine dips saturate at about the same power in the fibre, while in the cell the pumped ones saturate first (Fig. 5). Fitting transmission against power with a Beer-Lambert law whose absorption falls as a power r of one plus P over P_sat, the fibre data follow r = 1 over the whole range and give P_sat of 61 +- 3 nW (51 +- 5 nW at the best-fit r of 0.88), whereas the cell follows r = 1/2 only at low power (Fig. 6). The authors caution, verbatim: "This is consistent with the idea of increased homogeneous line broadening due to transit time effects and collisions with the TOF; however, care should be taken not to over-interpret this fit as an accurate model of the physical processes responsible for the saturation behavior." The measured P_sat agrees in order of magnitude with a rough estimate of about 100 nW from the nominal saturation intensity, the mode area and the measured widths.

## Use in this record

The thesis's nanofibre arm compares cold atoms with warm atoms crossing the evanescent field in 0.1 to 0.4 GHz, and its line model carries transit, saturation and depletion. This is the warm-vapour measurement of what that regime does to a one-photon line: transit and fibre collisions make it more Lorentzian, pumping has no time to act, and saturation sets in at nanowatts with a homogeneous law. For the two-photon 5S to 6S line, whose rate goes as the square of the intensity, the saturation powers do not transfer, but the ordering of the mechanisms does, and the authors' own warning against reading a good empirical fit as physics is the discipline the joint model applies to its terms.

Related on this shelf: `hendrickson2010` (Rb two-photon absorption on a tapered nanofibre at low power, from the same group), `gokhroo2022` (Rb line shapes in high intensity near a nanofibre), `patterson2018` (the van der Waals asymmetry of Rb lines at a nanofibre).
