---
citekey: kolachevsky2006
type: article
authors:
  - Kolachevsky, N.
  - Haas, M.
  - Jentschura, U. D.
  - Herrmann, M.
  - Fendel, P.
  - Fischer, M.
  - Holzwarth, R.
  - Udem, Th.
  - Keitel, C. H.
  - Hänsch, T. W.
title: 'Photoionization broadening of the 1S-2S transition in a beam of atomic hydrogen'
journal: Phys. Rev. A
volume: 74
number: 5
pages: 052504
year: 2006
doi: 10.1103/PhysRevA.74.052504
arxiv: 'quant-ph/0609114'
pdf: PDF_papers/Kolachevsky_2006_photoionization-broadening-hydrogen-1S-2S-line-shape.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/kolachevsky2006.md  # line-by-line against the held PDF, 2026-09-22: frontmatter cross-checked against the Crossref record; one correction to an Eq. 4 attribution and a scope trim in verify_flags, all other claims confirmed
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is arXiv:quant-ph/0609114v1 (15 Sep 2006). The journal reference is
    from the Crossref and OSTI records found while searching for Haas et al. 2006, for
    which this preprint had been wrongly offered as the arXiv posting. The published
    version was not compared, but the frontmatter fields (authors, title, journal,
    volume, issue, pages, year, doi) were independently confirmed against the Crossref
    record for the DOI. Sections I to IV B read on 2026-09-22.'
verified_date: 2026-09-22
summary: >
  The canonical full-model precedent for a light-shifted two-photon line: a Monte
  Carlo of 10 000 hydrogen atoms on random trajectories through the Gaussian mode
  (w0 = 283 um), each integrating two-photon Bloch equations with a time-dependent
  detuning (ac Stark shift and second-order Doppler along its own path) and an
  intensity-dependent ionization loss. The simulated lines are fitted exactly as the
  data are, and the slopes of line shift and width against power agree with
  experiment to 15 and 18 per cent, validating the ac Stark coefficient. Terms are
  switched off one at a time, and the paper states that they do not add.
loci:
  - THEORY
  - methods/03
  - methods/04
section: prior-art
---

# kolachevsky2006

VERIFIED. Held (arXiv v1). Sections I to IV B read on 2026-09-22.

## What it does

A 243 nm standing wave in an enhancement cavity (waist 283 um on the incoupler, diverging along the axis) excites a 5 K hydrogen beam. Time-of-flight detection selects atoms slower than a cut-off, v_max = 15 cm / delay, and the analysis uses the 1210 us delay, where v_max is about 120 m/s (Section II). Each simulated atom gets a random entry and exit point on the two diaphragms and a speed from the beam's v^3 Maxwellian. Along its straight path it sees a time-dependent intensity I(t) and integrates two-photon Bloch equations (Eq. 2) with a time-dependent detuning (Eq. 3): the second-order Doppler term, the real part of the dynamic Stark shift (beta_ac = 1.66982e-4 Hz per W/m^2), and an ionization rate proportional to I(t) (beta_ioni = 1.20208e-4 Hz per W/m^2). The standing wave's modulation, near 10 GHz for a 1 m/s atom, is averaged out (Section III).

Two program switches, gamma_i = 0 and beta_ac = 0, let the authors separate ionization, the inhomogeneous ac Stark shift and power broadening (Fig. 4). The Fig. 4 caption states that the contributions cannot be added in any simple algebraic way. Ionization preferentially removes the slow atoms, which would have given the strongest and narrowest lines. That replaces the empirical slow-atom depletion (Zacharias effect) of the earlier line-shape model (Sections III and IV B).

## The numbers

- Experiment, from 12 days of Lorentzian fits against circulating power: the shift slope k_shift is 1.61(6) Hz/mW and the width slope k_broad is 2.25(11) Hz/mW. The day-to-day scatter has a reduced chi-squared near 3, which the paper partly assigns to errors on the power axis (Section IV A).
- The simulation matches k_shift within about 15 per cent and k_broad within about 18 per cent, which the paper reads as an experimental check of the calculated beta_ac to 15 per cent (Sections IV A and IV B).
- The simulated width at zero power, 550(5) Hz, is time-of-flight broadening alone. Against the observed 775(20) Hz it returns a laser width of 56(5) Hz at 486 nm, consistent with an independent 60 Hz beat-note value (Section IV B). The factor of 4 in Eq. (5) converts from 486 nm to 121 nm.
- The mean second-order Doppler shift at this delay is -20(1) Hz, against -200 Hz at v_max, because the detected velocity distribution is weighted by (1 - v/v_max) (Eq. 4), with a further correction from ionization's preferential loss of slow atoms.
- Adding +/-5 per cent white intensity noise to I(t) changes the result by less than the Monte Carlo spread. The spread between three independent 10 000-atom ensembles is a few per cent.

## Use in this record

- The canonical comparator the red team asks for: a trajectory-level forward model of a light-shifted two-photon line, with the shift changing along each path, fitted to the data through the same estimator the experiment uses. It is this record's twin in all but name. The precedent it sets is to validate a polarizability-type coefficient (beta_ac) against the data through the model, to 15 per cent, which is the move this record's Delta alpha comparison makes.
- Its estimator is the canonical one: the Lorentzian centre and width against power, with the model supplying the slopes. This record's addition is the shape channel, moments beyond the width, which this paper does not use. It says only that the simulated profile is fitted "exactly like" the data.
- Methodological match: the terms are switched off one at a time to attribute effects, and the paper says outright that they do not add. That is the non-additivity this record measures as the failure of the convolution form.
- Two further parallels: the laser width is inferred from the line, as this record bounds the residual laser width, and a loss process (ionization here, depletion there) reshapes the velocity distribution of the atoms that reach the signal.

## Limits

- The agreement is on slopes at the 15 to 18 per cent level. The line shape itself is not tested beyond its Lorentzian centre and width.
- The Monte Carlo spread, a few per cent, is estimated from three ensembles.
