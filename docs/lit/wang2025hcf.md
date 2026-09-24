---
citekey: wang2025hcf
type: article
authors:
  - Wang, Rui
  - Li, Wei
  - Xia, Zhiwen
  - Deng, Hongchang
  - Zhang, Yao
  - Fu, Rongxin
  - Zhang, Shuailong
  - Euser, Tijmen G.
  - Yuan, Libo
  - Song, Ningfang
  - Jiang, Yi
  - Xie, Shangran
title: 'Optical trapping of mesoscale particles and atoms in hollow-core optical fibers: principle and applications'
journal: Light Sci. Appl.
volume: 14
pages: 146
year: 2025
doi: 10.1038/s41377-025-01801-5
arxiv: null
pdf: PDF_papers/Wang_2025_optical-trapping-mesoscale-particles-hollow-core-fibers-review.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/wang2025hcf.md  # one dropped sentence restored in the verbatim abstract quote; everything else confirmed clean. Extended 2026-09-22 to pp. 9-10 (the atom-loading efficiency and the magneto-optical-trap-to-core loading route), see private/cache/lit_intake_2026-09-22_audits/wang2025hcf_extension.md
author: agent
routing:
  - CITE
verify_flags:
  - 'CITEKEY NOTE: an unrelated paper, Wang, Cao, Yuan et al., "Multi-channel
    fluorescence spectroscopy of the Rb 5S1/2-7S1/2 transition ...",
    Spectrochim. Acta B 235, 107387 (2026), already holds the citekey
    `wang2025` in docs/lit/wang2025.md (a different first-name Wang, Sandan,
    on an unrelated 5S-7S spectroscopy topic). This note uses `wang2025hcf`
    (hollow-core fibre) to avoid the collision; rename on integration only if
    the maintainer prefers a different disambiguator.'
  - 'Page 1 of the held PDF (masthead, title, full author list and
    affiliations, the complete abstract, the Open Access/CC-BY-4.0 notice,
    and the opening paragraph of the introduction) read against the record on
    2026-09-21, downloaded directly from nature.com (gold open access, no
    paywall). The body survey of trapping mechanisms and applications
    (the bulk of the review) was unread as of 2026-09-21. Pages 9-10 of that
    body were read on 2026-09-22 (see the next entry). The rest (pp. 2-8,
    11-23) remains unread.'
  - 'Pages 9 and 10 of the held PDF read on 2026-09-22 (pdftotext -layout
    extraction, checked against 200 dpi rendered page images of both pages,
    text and image agreeing exactly, no dropped symbols found). Page 9
    carries the tail of the Doppler-velocimetry subsection (Fig. 6 and its
    caption, on particle propulsion, read but not drawn on here since it is
    about particles and not atoms), then the full atom-trapping-in-HCF
    subsection heading and its loading-efficiency paragraph, then the
    opening two sentences of the cold-atom-loading-procedure subsection.
    Page 10 carries Fig. 7 and its caption, the magneto-optical-trap-to-core
    loading paragraph in full, and the detection subsection up to its last
    sentence, which continues onto page 11 (not read). Pages 2-8 and 11-23
    remain unread.'
verified_date: 2026-09-22
summary: >
  Open-access review (Beijing Institute of Technology / Cambridge) of
  optical trapping of mesoscale particles and atom clouds inside hollow-core
  fibres: light-guiding mechanism, optical-gradient-force trapping in the
  hollow core, levitation/propulsion along the fibre axis, and applications,
  covering two decades of the field. The recent survey the search priority
  asked for of the guided-trap HCPCF literature. Pp. 9-10 add the review's
  own figure for the cold-atom loading efficiency into the core, 0.1 to 3
  per cent, set mainly by the geometric overlap of the atomic cloud with the
  trapping beam, and the standard loading route: a magneto-optical trap
  (MOT) turned off as an adiabatically ramped far-off-resonance trap forms a
  funnel-like dipole trap around the cloud, guiding the atoms into the core
  by the dipole force and gravity.
loci: []
section: prior-art
---

# wang2025hcf

VERIFIED for page 1 (masthead, title, authors, affiliations, abstract, licence
notice, opening introduction paragraph) and for pp. 9-10 (the atom-trapping
subsection: the loading efficiency into the core and the loading route).
REPORTED beyond that: the rest of the review's body, including the
mesoscale-particle trapping mechanisms (pp. 2-8) and the applications,
challenges and future-directions sections (pp. 11-23), remains unread.

**Citekey note**: the natural citekey `wang2025` is already held in this
repository's own `docs/lit/wang2025.md`, for Sandan Wang et al.'s unrelated
Rb 5S-7S multi-channel-fluorescence paper. This entry is filed as
`wang2025hcf` to keep the two apart. On integration into `docs/lit/`, keep
that name or pick a different disambiguator, but do not overwrite the
existing `wang2025`.

## What page 1 gives, verbatim

"Hollow-core fiber (HCF) is a special optical waveguide type that can guide
light in the air or liquid core surrounded by properly designed cladding
structures. The guiding modes of the fiber can generate sufficient optical
gradient forces to balance the gravity of the particles or confine the atom
clouds, forming a stable optical trap in the hollow core. The levitated
objects can be propelled over the fiber length along the beam axis through an
imbalance of the optical scattering forces or by forming an optical lattice
by the counter-propagating beams. The ability to overcome the diffraction of
the laser beam in HCF can significantly increase the range of the optical
manipulation compared with standard free-space optical tweezers, opening up
vast ranges of applications that require long-distance optical control. Since
the first demonstration of optical trapping in HCF, hollow-core-fiber-based
optical trap (HCF-OT) has become an essential branch of optical tweezer that
draws intense research interests. Fast progress on the fundamental principle
and applied aspects of HCF-OT has been visible over the past two decades. In
recent years, significant milestones in reducing the propagation loss of HCF
have been achieved, making HCF an attractive topic in the field of optics and
photonics. This further promotes the research and applications of HCF-OT.
This review starts from the mechanism of light guidance of HCF,
mainly focusing on the issues related to the optical trap in the hollow core.
The basic principles and key features of HCF-OT, from optical levitation to
manipulation and the detection of macroscopic particles and atoms, are
summarized in detail. The key applications of HCF-OT, the challenges and
future directions of the technique are also discussed."

Published under CC BY 4.0 (page 1 licence notice, verbatim in part): "This
article is licensed under a Creative Commons Attribution 4.0 International
License, which permits use, sharing, adaptation, distribution and reproduction
in any medium or format, as long as you give appropriate credit to the
original author(s) and the source."

## What pp. 9-10 give, verbatim

Page 9 opens the "Atom trapping in HCFs" subsection by explaining that a
relatively high-power Gaussian trapping beam is typically used for a large
potential depth, that the atoms move in an axisymmetric circular potential
trap, and that their initial velocity sorts their motion into three
trajectory types in the trap (quasi-linear, quasi-circular, or elliptical
precession, simulated in Fig. 7c). It then gives the loading efficiency,
verbatim: "Typically, the loading efficiency is in the range of 0.1% – 3%,
depending mainly on the geometric overlapping between the atomic cloud and
the trapping beam." The paper attaches its own refs 128-130 to that
sentence, resolved below.
<!-- rendered-page: p. 9 -->

Pages 9-10 then give the loading route, under the heading "Loading of cold
atoms into HCF". Atoms are first laser-cooled in a magneto-optical trap
with a final temperature of several micro-Kelvin, and a cloud several
millimeters across is trapped in front of the fibre end face (Fig. 7a).
From there, verbatim: "Then, the MOT is turned off, and a far-off-resonance
trapping beam is adiabatically turned on, forming a funnel-like dipole
trap. The atoms are loaded into the FORT by superimposing the atomic cloud
with the trap volume. The optically trapped atoms are guided towards the
core of the HCF due to both the dipole force and gravity. The radial
temperature of the trapped atoms is usually a fraction of the potential
depth of the dipole trap. Once guided inside the core, the atoms move
freely in the axial direction while remaining confined in the radial
direction, preventing collision with the inner core wall."
<!-- rendered-page: p. 10 -->

Figure 7a sketches the same route in four panels: preparing the cold
cloud, loading it into the trap, its free fall, and its guiding into the
fibre, with the untrapped fraction of the cloud falling away beside the
guided one.

## Use in this record

This is the recent review of the guided-atom-in-HCPCF field the search
priority asked for (item 4), and it surveys the trapping-mechanism side that
okaba2014, bajcsy2011 and epple2014 (all newly held above) instantiate
individually. It is dated after the 2026-08-05 Lan-group digest
(`private/reviews/LAN_GROUP_DIGEST.md`) and after `wang2022`/`wang2020`, so it
is the freshest available map of where the field's trapping techniques stand.
Its focus is squarely on the mechanical (trapping/levitation/propulsion)
side, not the internal-state light-shift-distribution side this record's
own programme addresses, so it complements, not duplicates, the Lan-group
digest's own framing.

Its own reference list was unread as of 2026-09-21. As of 2026-09-22, the
three references the paper attaches to the p. 9 loading-efficiency sentence
are resolved from its own reference list (p. 22 of 23). Ref 128 is Hilton,
A. P. et al., High-efficiency cold-atom transport into a waveguide trap,
Phys. Rev. Appl. 10, 044034 (2018), held here as hilton2018. Ref 129 is
Peters, T., Yatsenko, L. P. and Halfmann, T., Loading and spatially
resolved characterization of a cold atomic ensemble inside a hollow-core
fiber, Phys. Rev. A 103, 063302 (2021), not held here. Ref 130 is Bajcsy,
M. et al., Laser-cooled atoms inside a hollow-core photonic-crystal fiber,
Phys. Rev. A 83, 063830 (2011), held here as bajcsy2011. The rest of the
reference list remains unread and is still the natural next place to look
for still-more-recent HCPCF light-shift work.

For chapter 4's capture comparison: the p. 9 loading-efficiency figure, 0.1
to 3 per cent, is a review-level restatement of the numbers hilton2018
(about 3 per cent, a 45-micron-core kagome fibre over 10 cm) and wang2020's
own table (0.19 per cent simulated, 3.2 per cent and 3 per cent measured)
already give that chapter, and two of its own three references for the
figure are those same two papers. The comparison gains a corroborating
review-level source here, not a new number: the chapter's own
loading-efficiency figures should still cite hilton2018 and wang2020
directly, with wang2025hcf as the survey-level pointer to the same result.
