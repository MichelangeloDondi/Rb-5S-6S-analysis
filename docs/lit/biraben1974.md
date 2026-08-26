---
citekey: biraben1974
type: article
authors:
  - Biraben, F.
  - Cagnac, B.
  - Grynberg, G.
title: 'Experimental Evidence of Two-Photon Transition without Doppler Broadening'
journal: Phys. Rev. Lett.
volume: 32
pages: 643
year: 1974
doi: 10.1103/PhysRevLett.32.643
arxiv: null
pdf: PDF_papers/Biraben_1974_first-doppler-free-two-photon-Na.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: '2026-08-03'
summary: >
  The founding experimental demonstration of Doppler-free two-photon
  spectroscopy: the 3S-5S transition in sodium vapour, driven by a
  retro-reflected dye laser, shows two narrow hyperfine-resolved peaks that
  survive only when the atom is forced to take one photon from each of the
  two counter-propagating beams (opposite circular polarisations eliminate
  the residual Doppler pedestal entirely). Confirms the 1970/1973 theoretical
  prediction. Contains the Doppler-cancellation algebra our methods/01
  rederives, but no transit-time lineshape, no fitted width, and no moments
  -- that is biraben1979, five years later.
loci:
  - P1
  - methods/01
section: method-anchors
---

# biraben1974

Held. Verified in full (four-page PRL, 32, 643-645, 25 March 1974, received 28 January 1974).

This is the founding paper of the two-photon Doppler-free technique this repository's measurement rests on. It shares its pages with an independent companion demonstration, [M. D. Levenson and N. Bloembergen, "Observation of Two-Photon Absorption without Doppler Broadening on the 3S-5S Transition in Sodium Vapor," ibid. 645](https://doi.org/10.1103/PhysRevLett.32.645), printed immediately after it in the same issue.

## Abstract

"Experiments on the 3S-5S two-photon transition in sodium give evidence that Doppler broadening is eliminated if the atom absorbs two photons propagating in opposite directions. The proof is given by the comparison of the two-photon absorption line shape in traveling and standing waves."

## The experiment

The 3S to 5S two-photon transition in sodium vapour (cell at about 220 C) is driven with a flashlamp-pumped rhodamine-6G dye laser at 6022.3 Å, multimode (three or four longitudinal modes, about 240 MHz apart, calibrated by a Michelson interferometer), retro-reflected by a mirror to form a standing wave. The 5S population is read out via fluorescence at 6154/6160 Å (decay to 3P1/2, 3P3/2), with the signal Q integrated over a 300 ns pulse and plotted as Q/P² against laser frequency, since the two-photon rate scales as the square of the laser power P.

Three configurations are compared. A single travelling wave, no mirror, gives a broad Doppler-spread pedestal about 2000 MHz wide, weak, plotted at 10x expansion. A standing wave with linear polarisation gives two narrow hyperfine-resolved peaks (the allowed ΔF=0 transitions, F=1 to F'=1 and F=2 to F'=2) on a much weaker residual Doppler pedestal, from atoms absorbing both photons out of the same travelling wave. A standing wave with the two counter-propagating waves given opposite circular polarisations (σ+/σ-), via quarter-wave plates, forbids absorbing two photons from the same wave under the ΔmF=0 selection rule, so every absorbing atom takes one photon from each direction and the Doppler pedestal vanishes completely, leaving signal only at the two narrow peaks. Removing the mirror in this third configuration kills the signal outright. The progression across the three configurations is the paper's proof that the narrow Doppler-free feature is specific to forcing one photon from each direction, not an artefact of the standing wave generally.

## The numbers

Sodium 3S ground-state hyperfine splitting, 1771 MHz (known). 5S hyperfine splitting, not previously measured, estimated at about 155 MHz from the Fermi-Segre formula, giving a predicted 1616 MHz separation between the F=1 to F'=1 and F=2 to F'=2 two-photon lines and hence an expected ~800 MHz separation between the two observed peaks (the two-photon frequency axis is half the transition energy). No quantitative linewidth or fitted hyperfine value is reported: "the present uncertainty in the laser frequency prevents us from giving any significance to the experimental widths of the peaks, or assigning a precise value to the hyperfine structure of the 5S level." The paper states this falls short of "the ultimate precision inherent in this method."

## Theoretical lineage

The prediction confirmed here is from Cagnac, Grynberg and Biraben, J. Phys. (Paris) 34, 845 (1973), and, behind that, Vasilenko, Chebotaev and Shishaev, Pis'ma Zh. Eksp. Teor. Fiz. 12, 161 (1970) [JETP Lett. 12, 113 (1970)]. This paper is the first experimental test of that prediction, not its origin.

## Use in this record

This repository's [methods/01](../methods/01_the_measurement.md), driving the Rb 5S1/2 to 6S1/2 two-photon transition Doppler-free by retro-reflecting a 993 nm beam onto itself, rederives the same cancellation condition independently: an atom absorbing one photon from each counter-propagating direction sees ν(1+v/c) + ν(1−v/c) = 2ν, the velocity term cancelling to first order for every atom. This matches this paper's Eq. (1), ħω_e − ħω_g = ħω(1 − v_x/c) + ħω(1 + v_x/c) = 2ħω, restated here for a different beam geometry. The founding-history role in this repository's other documents is carried by [biraben2019](biraben2019.md), a later retrospective review; `docs/BIG_PICTURE.md` and `docs/THEORY_NOTE.md` attribute the transit lineshape itself to [biraben1979](biraben1979.md), a different, later paper.

This 1974 paper establishes the Doppler-cancellation algebra and the experimental proof, via the polarisation-selection control, that forcing one photon from each counter-propagating direction, not merely illuminating with a standing wave, is what removes the Doppler pedestal. It contains no transit-time lineshape, cusp, Lorentzian-convolved-with-exponential kernel, moments, AC-Stark or standing-wave intensity-weighting discussion, second-order Doppler estimate, or rubidium data (the measured transition is sodium 3S-5S at 6022.3 Å). Those belong to [biraben1979](biraben1979.md) for the transit kernel and [biraben2019](biraben2019.md) for the retrospective synthesis.
