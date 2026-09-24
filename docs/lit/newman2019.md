---
citekey: newman2019
type: article
authors:
  - Newman, Z. L.
  - Maurice, V.
  - Drake, T. E.
  - Stone, J. R.
  - Briles, T. C.
  - Spencer, D. T.
  - Fredrick, C.
  - Li, Q.
  - Westly, D.
  - Ilic, B. R.
  - Shen, B.
  - Suh, M.-G.
  - Yang, K. Y.
  - Johnson, C.
  - Johnson, D. M. S.
  - Hollberg, L.
  - Vahala, K.
  - Srinivasan, K.
  - Diddams, S. A.
  - Kitching, J.
  - Papp, S. B.
  - Hummon, M. T.
title: 'Architecture for the photonic integration of an optical atomic clock'
journal: Optica
volume: 6
number: 5
pages: 680-685
year: 2019
doi: 10.1364/OPTICA.6.000680
arxiv: '1811.00616'
pdf: PDF_papers/Newman_2019_photonic-integration-optical-atomic-clock-Rb-two-photon.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/newman2019.md  # line-by-line against the held PDF, 2026-09-22: fixed a miscounted title diff ("one word" -> three), corrected a silicon-chip/laser mischaracterization, and corrected an unsupported arXiv-preprint provenance claim (file carries no arXiv watermark). Extended 2026-09-22 to pp. 6 and 9 (the light shift and collision shift Methods paragraph -- the intake brief named p. 8, which is the reference list, the paragraph is on p. 9), see private/cache/lit_intake_2026-09-22_audits/newman2019_extension.md
author: agent
routing: []
verify_flags:
  - 'Page 1 of the held PDF (title, full author list, affiliations, the
    complete abstract, and the opening of the Main Text through "an atomic
    vapor cell implemented on a silicon chip and a microresonator frequency
    comb (a microcomb) system for optical frequency division") read against
    the record on 2026-09-21. The preprint''s own title page reads
    "Photonic integration of an optical atomic clock", missing the leading
    "Architecture for the" (three words) that the Optica-published title
    carries: "Architecture for the photonic integration of an optical atomic
    clock"; the `title` field above follows the published version, per the
    journal reference.'
  - 'Pages 6 and 9 read on 2026-09-22 (pdftotext -layout extraction,
    single-column layout, corroborated against the 150 dpi rendered page
    image for both pages since these carry the load-bearing signed numbers).
    Page 6 (Fig. 4''s caption and the sentence introducing it) gives the
    overall clock frequency offset, delta-nu approximately -22.7 kHz
    (delta-nu/delta-nu_Rb approximately 5e-11), attributed to the light shift
    and the collision shift jointly, "(see Methods)". The intake brief for
    this pass named p. 8 for the quantitative light shift/collision shift
    paragraph. Page 8 is in fact the second page of the numbered reference list
    (refs 11-39, continuing from p. 7''s refs 1-10) and carries no Methods
    content. The paragraph itself is on p. 9, the first page of the
    "Methods" section ("1. Microfabricated vapor cell"), and is read and
    quoted from there. Pages 1-5, 7-8 and 10-11 are unread beyond what page 1
    already covers.'
  - 'A full-text search of the held file (2026-09-22, during the line-by-line
    audit) found no arXiv watermark anywhere in its 11 pages, unlike this
    repository''s other held arXiv preprints in the hydrogen-spectroscopy
    lineage; its "Distribution Statement ''A'' (Approved for Public Release,
    Distribution Unlimited)" header and "Foxit Reader PDF Printer" Producer
    metadata indicate this specific file is a NIST/DARPA public-release copy
    rather than an arXiv-fetched rendering, even though its title/author/
    abstract content matches arXiv:1811.00616. The frontmatter `arxiv` field
    records the citable identifier for the paper, not a verified property of
    this file.'
verified_date: 2026-09-22
summary: >
  NIST/Caltech/Draper compact optical-clock architecture: a semiconductor
  laser stabilized to the 778 nm two-photon 5S-5D transition in a
  microfabricated (silicon-chip) Rb vapor cell, divided by interlocked
  silicon-chip Kerr-microresonator combs to a 22 GHz electronic signal at
  1e-13 instability. The clock's -22.7 kHz frequency offset from the accepted
  transition frequency is attributed (Methods, p. 9) to a light shift of
  about -1.5 kHz/mW (about -23.4 kHz at the 15.6 mW clock laser power) and a
  collision shift of about +6 kHz from helium diffusion through the cell
  windows plus about -5 kHz from background gases, both consistent with a
  separate approximately 100 kHz collision-broadening measurement (their
  ref. 29, matching zameroski2014 on journal/volume/page/year though not on
  its printed author list). Direct predecessor
  of the already-held newman2021 (same NIST programme, different citekey/year)
  and sits beside martin2018, martin2019 and gerginov2018 in the two-photon
  Rb light-shift-systematics cluster the search priority asked for.
loci: []
section: prior-art
---

# newman2019

VERIFIED for page 1 (title, authors, affiliations, abstract, and the opening
lines of the Main Text), read on 2026-09-21, and for pages 6 and 9 (the clock
frequency offset and its Methods-section light-shift/collision-shift
breakdown), read on 2026-09-22 (see the What-pages-6-and-9-add section
below). REPORTED
beyond that: pages 2-5, 7-8 and 10-11 are unread.

## What page 1 gives, verbatim

"Laboratory optical atomic clocks achieve remarkable accuracy (now counted to
18 digits or more), opening possibilities to explore fundamental physics and
enable new measurements. However, their size and use of bulk components
prevent them from being more widely adopted in applications that require
precision timing. By leveraging silicon-chip photonics for integration and to
reduce component size and complexity, we demonstrate a compact optical-clock
architecture. Here a semiconductor laser is stabilized to an optical
transition in a microfabricated rubidium vapor cell, and a pair of interlocked
Kerr-microresonator frequency combs provide fully coherent optical division of
the clock laser to generate an electronic 22 GHz clock signal with a
fractional frequency instability of one part in 10^13. These results
demonstrate key concepts of how to use silicon-chip devices in future
portable and ultraprecise optical clocks."

## What pages 6 and 9 add, verbatim

Page 6, introducing Fig. 4 (optical clock performance), verbatim: "The
absolute frequency shift of our clock is Δν≈-22.7 kHz (Δν/ΔνRb≈5×10-11),
which is primarily due to the light shift and the collision shift (see
Methods). The mean values of the two measurements of the clock frequency
agree to within their standard error." Fig. 4a itself reports the two
measured means, mean = -22681±31 Hz (from the 22 GHz clock output) and
mean = -22685±33 Hz (from the beat note against the Er:fiber comb), which
the text's Δν≈-22.7 kHz rounds.
<!-- rendered-page: p. 6 -->

Page 9 (the "Methods" section, "1. Microfabricated vapor cell") gives the
quantitative breakdown the p. 6 sentence promises, verbatim: "We have
measured the absolute frequency of our clock to be ν ≈ 385284566347315 ± 30
Hz, which corresponds to a frequency shift from the accepted value of the
two-photon transition frequency of Δν≈-22.7 kHz (30) and is primarily due to
the light shift and the collision shift. We have measured the light shift to
be ≈-1.5 kHz/mW resulting in a ≈-23.4 kHz shift for the 15.6 mW of clock
laser power. We expect a ≈+6 kHz collision shift from helium diffusion and
attribute the remaining ≈-5 kHz to collision shifts from background gases.
Both the helium collision shift and the background gas collision shift are
consistent with our ≈100 kHz collision broadening measurement (29)."
Reference (29) is printed, on p. 8, as "N. D. Zameroski, G. D. Hager, C. J.
Erickson, J. H. Burke, J. Phys. B At. Mol. Opt. Phys. 47, 225205 (2014)".
This matches zameroski2014 on journal, volume, page and year exactly, though
zameroski2014's own held record lists its authors as Zameroski, Hager,
Rudolph, Erickson and Hostutler, without a "Burke" and with two fewer names
than newman2019 prints. The numeric identification (journal/volume/page/year)
is unambiguous. The author-list mismatch is newman2019's own reference-list
error, not re-verified against zameroski2014's PDF here.
<!-- rendered-page: p. 9 -->

The same page 9, one paragraph earlier (describing the cell's construction),
already splits a broadening budget this way, verbatim: "Helium diffusion
through the glass windows as the cell ages accounts for ≈75 kHz of
broadening and ≈25 kHz of broadening is due to unwanted gases that arise
during the cell bonding and filling process." 75+25 = 100, matching the
≈100 kHz collision-broadening measurement cited to zameroski2014 two
sentences later. Read together, the two paragraphs give one consistent
picture, a ≈100 kHz collision-broadening budget split 75/25 between helium
and background gases, and a separate ≈+6/-5 kHz collision-shift split
attributed to the same two sources, and not two different 100 kHz figures.
<!-- rendered-page: p. 9 -->

The ≈100 kHz figure above must not be conflated with a different,
unread-here number on p. 4: a Lorentzian fit to the clock transition's
fluorescence lineshape there gives a total linewidth of ≈1 MHz built from
330 kHz natural linewidth + ≈475 kHz laser linewidth + ≈100 kHz transit-time
broadening + ≈125 kHz "collisional broadening from background gases in the
cell" (p. 4, seen in passing while locating the Methods section, not one of
this pass's assigned pages). That ≈125 kHz is an observed-linewidth budget
component. The ≈100 kHz on p. 9 is a separate "collision broadening
measurement" cited to zameroski2014 and used only to cross-check the sign
and rough size of the ±6/-5 kHz collision-shift split above.

## Use in this record

Named by the search priority as "Newman et al. 2019", distinct from the
already-held newman2021 (results/`docs/lit/newman2021.md`), a later paper from
the same NIST programme. This 2019 paper is the architecture precursor: the
Rb vapor cell and the 778 nm two-photon transition (5S-5D, this record's
neighbouring two-photon Rb line, not this record's own 5S-6S/993 nm) are the
same physical system whose light-shift systematics martin2018, martin2019 and
gerginov2018 (all already held) treat directly. Filed as `prior-art` rather
than the `landscape-24-26` bucket its 2021 successor uses, since 2019 sits
chronologically and thematically closer to the older architecture/systematics
precedents (gerginov2018) than to the recent-landscape cluster.

For the permeation paragraph: p. 9's own attribution of the ≈+6 kHz and ≈-5
kHz collision shifts to, respectively, helium diffusing through the cell's
anodically bonded glass windows as it ages and background gases entering
during the bonding and filling process (p. 9, quoted above) is a directly
named, quantified instance of exactly the gas-permeation-into-a-sealed-cell
effect this record's own permeation paragraph is about, on a small
(3x3x1.5 mm chambers) microfabricated Rb cell and not this record's own
glass cell. The sign (helium diffusing in, raising the shift) and the order
of magnitude (kHz-scale on a 778 nm two-photon transition) are the
transferable facts, not the absolute rate, which depends on this specific
cell's glass thickness and bonding process (p. 9's own "10x10x3 mm silicon
frame sandwiched between two 700 um-thick aluminosilicate glass pieces").

For chapter 8's first canonical row: the light shift, ≈-1.5 kHz/mW (about
-23.4 kHz at 15.6 mW of 778 nm clock laser power), and the collision-shift
split, ≈+6 kHz (helium) and ≈-5 kHz (background gases), against a
≈100 kHz collision-broadening cross-check (their ref. 29, zameroski2014 on
its numeric fields), are a complete, self-consistent, page-cited light-shift/
collision-shift measurement on a two-photon Rb transition (778 nm, 5S-5D)
adjacent to this record's own 5S-6S line, and are offered as the first
canonical row of a comparison table: a coefficient in kHz/mW for the light
shift, a signed kHz collision shift attributed to a named gas species, and a
kHz collision-broadening cross-check, each with the cell/power conditions it
was measured at, matching the shape martin2018, martin2019 and gerginov2018
would need to fill in as further rows.
