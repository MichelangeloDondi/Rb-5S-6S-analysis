---
citekey: kaplan2003
type: inproceedings
authors:
  - Kaplan, Ariel
  - Andersen, Mikkel Fredslund
  - Davidson, Nir
title: 'Suppression of inhomogeneous broadening in rf spectroscopy of optically trapped atoms'
journal: 2003 European Quantum Electronics Conference (EQEC 2003)
volume: null
pages: '300'
year: 2003
doi: 10.1109/EQEC.2003.1314157
arxiv: null
pdf: PDF_papers/Kaplan_2003_inhomogeneous-broadening-suppression-rf-spectroscopy-trapped-atoms.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_hand2/audits/kaplan2003.md  # full 1-page read against the PDF, and identity checked against the task's own guess, 2026-09-22
author: agent
routing:
  - CITE
verify_flags:
  - 'IDENTITY CORRECTION: the intake brief guessed this PDF was "Kaplan, Andersen and Davidson
    2002, PRA 66, 045401." It is not. The held PDF''s own metadata (Subject field) and its printed
    text identify it as a ONE-PAGE digest for the 2003 European Quantum Electronics Conference
    (EQEC 2003, IEEE Cat No.03TH8665), p. 300, DOI 10.1109/EQEC.2003.1314157 -- a condensed
    conference report BY THE SAME AUTHORS that explicitly cites the PRA paper as its own
    reference [1] ("A. Kaplan, M.F. Andersen, and N. Davidson, Phys. Rev. A 66, 045401 (2002)").
    The PRA paper itself is not held under this intake and is not this note''s subject; the
    citekey and every number below are taken only from the one page actually held.'
  - 'Held and read in full (the paper is one page). A companion note already in this record,
    kaplan2005 (a longer 2005 review by two of the same three authors plus Grunzweig), reports a
    shift of "-756 Hz" for what reads as a similar 3 ms trapped-atom Rabi measurement; THIS paper''s
    own text gives "~550Hz" for its analogous shift. The two figures are not reconciled here --
    they are kept attributed to their own separate sources and neither is used as a stand-in for
    the other.'
verified_date: 2026-09-22
summary: >
  One-page EQEC 2003 conference digest of Kaplan, Andersen and Davidson, Phys. Rev. A 66, 045401
  (2002): a far-off-resonance optical trap (FORT) imposes a differential AC-Stark shift on the two
  ground-state hyperfine levels, inhomogeneously broadening an rf/microwave hyperfine-splitting
  measurement of the trapped ensemble; a second, weak beam tuned midway between the hyperfine
  levels, mode-matched into the same trap, cancels the shift for every trapped atom at once
  (intensity ratio ~ (Delta_HF/2delta)^2), narrowing a 3 ms Rabi line from ~320 Hz rms back toward
  the ~110 Hz free-atom Fourier limit, and to nearly Fourier-limited with a 50 ms pulse.
loci:
  - THEORY
  - methods/09
section: prior-art
---

# kaplan2003

VERIFIED. Held and read in full: the paper is a single page. See the identity-correction
verify_flag above: this is the EQEC 2003 conference digest, not the PRA 66, 045401 (2002) paper
the intake brief guessed at.

## What it does, in the paper's own words

> "We demonstrate a method for reducing the inhomogeneous broadening in the spectroscopic
measurement of the hyperfine splitting of the ground state of optically trapped atoms."

This reduction is achieved, in substance, by the addition of a very weak light field (the paper's
own compensating beam [1]), whose frequency is tuned between the two hyperfine levels. The total
shift is obtained by adding the shifts from the trap and the compensating beam, and a complete
cancellation of the inhomogeneous broadening occurs for an intensity ratio of
~(Delta_HF/2delta)^2, paraphrased from here on since this scan's OCR is corrupted on both the
word `field` (reads `tield`) and the formula itself (reads `- (AHF/2&)*`, a heavy garbling of the
same Δ_HF/2δ ratio squared).

Figure 1(a) shows the trapping beam's shift of the two hyperfine ground levels as a function of
radial position (dashed), the compensating beam's opposite-sign shift (dotted), and their sum
(full line) becoming flat, equal for both hyperfine levels at every point in the trap.

## The experiment and its numbers

FORT: 50 mW, detuned 5 nm below resonance, a 50 um 1/e^2 radius, trap depth U0 = 200 E_rec (E_rec the
recoil energy). A second, weak laser locked near the middle of the ground-state hyperfine
splitting is mode-matched into the same single-mode fibre as the FORT beam. About 1e5 atoms are
loaded at ~10 uK. Rabi spectroscopy drives the magnetically-insensitive |F=2,mF=0> to |F=3,mF=0>
transition with a 3 ms pi pulse (Fig. 1(b)):

- Free (untrapped) atoms: no measurable broadening, rms width Fourier-limited to ~110 Hz.
- Trapped atoms, FORT only: peak shifted by ~550Hz, and the line broadened to ~320Hz rms.
- Trapped atoms with the compensating beam added: the shift and broadening are nearly cancelled.
- With a longer, 50 ms pulse: "a nearly Fourier limited width (thus showing a nearly 50-fold
  narrowing), at the expense of a larger spontaneous photon scattering and hence a smaller
  signal."

The paper closes: "With the suppression of inhomogeneous broadening, the atomic coherence time is
next limited by the much smaller spontaneous scattering time," and frames the compensating beam as
a general tool "to study the interesting interplay between dynamics and coherence in systems with
a rich phase-space, for example in atom-optics billiards[2]." References: [1] the PRA 66, 045401
(2002) full paper, and [2] PRL 87, 274101 (2001) and a PRL then "in press" (quant-ph/0208052).

## Use in this record

The physical mechanism (a trap's differential light shift on two internal levels producing an
Inhomogeneous distribution of shifts across the trapped ensemble, which shows up as both a mean
shift and a broadening of a subsequently measured transition) is structurally the same object
this record studies in its own AC-Stark ramp: a spatially/temporally varying light shift smeared
over an ensemble of atoms (here, over the trap volume at fixed time, and there, over the transit chord
and the scan ramp) turns into a shift-plus-broadening of the measured line, describable by the
first two moments of the underlying shift distribution.

- Fig. 1(b)'s pair of numbers (a shift of the line centre and a broadening of its width, both
  produced by the same inhomogeneous-shift mechanism and both nulled together by tuning one
  compensating parameter) is a clean, independent illustration of reading the first two moments
  of a shift distribution off a measured spectrum, the same object this record's own moment ladder
  extends to higher orders instead of cancelling.
- Where Kaplan et al. engineer a suppression of the inhomogeneous broadening (a second beam that
  nulls the shift distribution's contribution to the line), this record's stated programme takes
  the opposite stance for its own AC-Stark shift: read the shift distribution's moments as signal
  instead of removing them. The two are complementary readings of the same underlying physics,
  and Kaplan et al.'s suppression scheme is itself evidence for how large and how structured such a
  light-shift-driven inhomogeneous broadening can be in a real optical-trap geometry.
- The validity condition implicit in their stationary picture (the compensating beam must be
  mode-matched well enough, and the pulse short enough, that atomic motion during the pulse does
  not change the local trap depth seen) is the same class of quasi-static condition this record
  states for its own ramp (S0^2 much larger than the transit kernel's variance term). kaplan2005's
  fuller review (already in this record, see its own note) states this condition explicitly as its
  Eq. (34), and is the more appropriate citation for the condition itself.

## Limits

This one-page digest gives no error bars, no explicit functional form for the compensating-beam
cancellation beyond the leading-order intensity ratio, and no numeric value for the width reached
at 50 ms (only "nearly Fourier limited... nearly 50-fold narrowing"). The fuller numbers (the
25 ms/13 Hz point, the specific -756 Hz shift, the four-geometry comparison) live in the PRA and
review papers this digest cites, not in the page held here. See kaplan2005's own note for those,
attributed to that source and not to this one.
