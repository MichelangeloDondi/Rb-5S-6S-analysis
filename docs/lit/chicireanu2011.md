---
citekey: chicireanu2011
type: article
authors:
  - Chicireanu, R.
  - Nelson, K. D.
  - Olmschenk, S.
  - Lundblad, N.
  - Derevianko, A.
  - Porto, J. V.
title: 'Differential light-shift cancellation in a magnetic-field-insensitive transition of 87Rb'
journal: Phys. Rev. Lett.
volume: 106
number: 6
pages: 063002
year: 2011
doi: 10.1103/PhysRevLett.106.063002
arxiv: '1010.1520'
pdf: PDF_papers/Chicireanu_2011_differential-light-shift-cancellation-Rb87-lattice.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/chicireanu2011.md  # line-by-line against the held PDF, 2026-09-22: one overclaim corrected (the paper's own refs. 1-5 show it is not the "origin" of scalar-versus-vector compensation, only of the simultaneous combination with field-insensitivity); every number confirmed exactly
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:1010.1520v1 (7 Oct 2010). Journal reference and DOI from
    Crossref, 2026-09-22. Pages 1 to 3 (theory, setup, Figs. 1-3) read on 2026-09-22;
    the closing discussion on page 4 was not read.'
verified_date: 2026-09-22
summary: >
  Up to 95(2) per cent of the differential light shift of the two-photon hyperfine
  transition |1,-1> to |2,+1> of 87Rb in an optical lattice is cancelled, while the
  transition stays field-insensitive at the magic 0.3228917 mT. The vector light shift,
  which couples only to the electron spin, is set against the scalar one using circular
  polarization on selected lattice sites. A demonstration cited by the host group's
  xin2019 and leong2020 for the scalar-versus-vector compensation used on hollow-core-fibre
  clock states -- though this paper's own references show the vector-shift technique itself
  predates it, and credit the proposal to combine it with field-insensitivity to Derevianko
  (2010).
loci:
  - methods/09
section: lan-platforms
---

# chicireanu2011

VERIFIED for pages 1 to 3. Held (arXiv v1). Read on 2026-09-22.

## What it does

For alkali ground-state hyperfine transitions the scalar differential shift has no magic zero, so with linear light it cannot be cancelled. The vector shift acts as an effective magnetic field and couples only to the electronic moment, while the Zeeman interaction also carries the nuclear moment. At the magic field B_m, where the differential Zeeman shift of |F=1, m_F=-1> to |F'=2, m_F'=+1> vanishes, the differential vector shift therefore survives and can be tuned against the scalar one. The paper estimates for 87Rb that the two are of the same order (Eq. 1 and the text after it). The experiment loads a Bose-Einstein condensate into a 3D lattice in the Mott regime with single occupancy. It keeps atoms only on the lattice sites with adjustable circular polarization and measures the transition frequency against intensity by detuned Ramsey spectroscopy, comparing with the |1,0> to |2,0> clock transition as reference.

## The numbers

- Up to 95(2) per cent of the differential light shift cancelled (abstract, Fig. 2).
- The ratio of intensity sensitivities between the two transitions reaches a minimum of 4.5 per cent at 806 nm, a "nearly magic" behaviour against the lattice wavelength (Fig. 3).
- The projected circularity is estimated at A of about 0.99. Reversing B increases the sensitivity, because scalar and vector then add.

## Use in this record

- For the application: an experimental demonstration of the polarization-and-field compensation that the host group cites for hollow-core-fibre clock states (xin2019, leong2020). This paper's own references (1-4) credit the vector-shift DLS-compensation technique itself to earlier work, and its ref. 5 (Derevianko 2010) to the theoretical proposal for combining it with field-insensitivity, which this paper realizes experimentally, making it a precedent for the combination, not the origin of scalar-versus-vector compensation as such. It also proves that full cancellation needs a second parameter, which is what xin2019's impossibility statement for a single wavelength leaves out.
- For this record's magic-condition gain: polarization and field join wavelength as knobs on the differential shift. A magic condition read from the sign change of the odd moments, as the record proposes, would have the same knob set to scan.

## Limits

- A lattice experiment with single occupancy. The compensation holds only on the sites with the right circularity and is optimized by minimizing the intensity dependence, not by a model fit.
