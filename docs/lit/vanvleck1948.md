---
citekey: vanvleck1948
type: article
authors:
  - Van Vleck, J. H.
title: 'The Dipolar Broadening of Magnetic Resonance Lines in Crystals'
journal: Physical Review
volume: 74
number: 9
pages: 1168--1183
year: 1948
doi: 10.1103/PhysRev.74.1168
arxiv: null
pdf: PDF_papers/VanVleck_1948_dipolar-broadening-magnetic-resonance-lines.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-21/audits/vanvleck1948.md  # bibliographic fields checked against the APS journal page, 2026-09-22; exact match; no claim of having read the paper found
author: agent
routing:
  - CITE
verify_flags:
  - 'Held and read 2026-09-23 (the owner placed the PDF). Pages 1168, 1178-1183 read directly.
    The earlier flag on this note said in plain words that no page had been read, and a claim was
    nonetheless written into the strategic document from it. That is recorded as F404, and it is
    why this note now carries what the paper says instead of what search engines say.'
  - 'Read at the PDF. The shape indicator is the ratio of root-mean-fourth to root-mean-square
    frequency deviation, Dnu_4/Dnu_2 with Dnu_n = ((Dnu^n)_av)^(1/n), which is (mu4/mu2^2)^(1/4).
    Page 1179 tabulates it for three shapes: rectangular 1.158, triangular 1.245, Gaussian 1.316,
    whose fourth powers are 1.7982, 2.4026 and 2.9993. Page 1182 gives the Gaussian case in the
    moment form directly, "the Gaussian value 3[(Dnu^2)_av]^2". Observed 1.24 against his theory
    1.25 for CaF2 in the 100 direction (Pake and Purcell).'
  - 'Absent from the paper, checked because an earlier draft asserted it: any treatment of
    truncating Lorentzian wings. The difficulty he names is an experimental uncertainty in the
    integration that yields the moment (p. 1180) and one spurious wing from a misaligned
    microcrystal. His lines are near-Gaussian dipolar crystal lines, and the Lorentzian-wing
    liquid case is Bloembergen, Pound and Purcell, which he engages in section VI and hedges on the next page, his own theory being an adiabatic one (p. 1183).'
verified_date: 2026-09-23
summary: >
  The paper usually credited with the method-of-moments treatment of a magnetic-resonance
  absorption line: rather than compute the full lineshape (intractable in general), Van Vleck used
  the invariance of the quantum-mechanical diagonal sum (trace) to derive the second MOMENT of the
  line directly from the dipolar Hamiltonian, without ever solving for the lineshape itself -- the
  origin of what NMR/EPR spectroscopy still calls the "Van Vleck second moment." The paper the task
  named for the method of moments for line shapes; PR 74, 1168 confirmed as the correct
  reference. Held and read 2026-09-23, pages 1168 and 1178 to 1183.
loci:
  - methods/06
  - THEORY
section: method-anchors
---

# vanvleck1948

## What is reported about it

Phys. Rev. **74**, 1168-1183 (1948), DOI 10.1103/PhysRev.74.1168, "The Dipolar Broadening of
Magnetic Resonance Lines in Crystals." A search-engine summary describes the paper's approach as
follows: "the width of absorption lines arising from magnetic moments in crystals... are caused
primarily by magnetic dipole interactions. While determining the precise shape of the absorption
line is difficult theoretically, Van Vleck used the invariance of the diagonal sum in quantum
mechanics to calculate the second moment of the frequency deviation and the root-mean-square line
breadth. The calculated line breadth agreed excellently with observations by Pake and Purcell on
the magnetic absorption of the F nucleus in CaF2" (paraphrased/summarized from search results, not
a direct quotation of the paper).

The general method this paper is credited with establishing (computing a spectral moment
directly from the underlying Hamiltonian/interaction, as a sum rule, without first solving for or
even assuming a functional form of the lineshape) is what NMR and EPR spectroscopy still call the
method of moments, and the paper's own second moment is still taught as the "Van Vleck second
moment."

## Use in this record

The task asked for this paper specifically as the method of moments for line shapes, and the
title, journal and page (PR 74, 1168) match exactly what was specified. This record confirms the
citation is correct and not a misremembered reference. Held as the earliest and most-cited root of
the practice of reading a lineshape through its moments rather than its full functional form, predating this
record's own two-photon-lineshape moment programme by 78 years, in a different branch of physics
(nuclear/electron magnetic resonance in solids, driven by dipole-dipole coupling, not a
laser-driven two-photon transition in a vapour). The specific technique (computing a moment as a
trace/sum rule directly from a known Hamiltonian, with no window or truncation in play) is not
this record's own situation (this record's moments are windowed and simulation-calibrated, not
closed-form sum rules of a known interaction), so the precedent is historical and terminological
(establishing that reading the line through its moments has an eighty-year pedigree), not a
technique this record's own producers could adopt directly.
