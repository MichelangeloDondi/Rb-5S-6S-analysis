---
citekey: biraben1979
type: article
authors:
  - Biraben, F.
  - Bassini, M.
  - Cagnac, B.
title: 'Line-shapes in Doppler-free two-photon spectroscopy: the effect of finite transit time'
journal: J. Phys. (Paris)
volume: 40
number: 5
pages: 445--455
year: 1979
doi: 10.1051/jphys:01979004005044500
arxiv: null
pdf: PDF_papers/Biraben_1979_finite-transit-time-two-photon-lineshape.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: '2026-08-03'
summary: >
  Origin of our transit kernel: Eq. (46) derives the finite-transit
  Doppler-free two-photon line as exactly a Lorentzian (width Gamma_e/2)
  convolved with a two-sided exponential (width delta*ln2, the central
  cusp), delta = <v_r>/w0. Confirmed by full read: our kernel restates
  Eq. (46) verbatim, and does not over-attribute the M9 Monte Carlo
  extension to this paper.
loci:
  - M3
  - M9
  - methods/02
section: transit-time
---

# biraben1979

**VERIFIED, 2026-08-03**, read in full from the open-access HAL deposit
jpa-00209125 (J. Physique 40 (5), 445-455, 1979, DOI
10.1051/jphys:01979004005044500; received 8 December 1978, accepted 24
January 1979).

**Abstract, verbatim.** "A general formalism is developed with the aim of
calculating the line-shapes in two-photon absorption for the case of non
monochromatic fields. This formalism is applied to the problem of the finite
transit time of the atoms through the Laser beam; and it permits a precise
expression to be obtained for the line-shape (convolution of a Lorentzian
curve and a double-exponential curve). The comparison is made using
experimental profiles."

**What it does, section by section.** Section 1 recaps the monochromatic
two-photon absorption rate already published in Cagnac-Grynberg-Biraben
1973 (their ref. [10]), setting up the two-photon operator and the
Doppler-cancellation result (companion theory to `biraben1974`'s
demonstration). Section 2 builds a general formalism for NON-monochromatic
fields: for a field E(t) with Fourier support confined to a finite interval
[T1, T2], the absorbed energy is expressed through A(Omega), the Fourier
transform of E(t)^2 (Eq. 36), the two-photon analogue of the one-photon
correlation-function result. This machinery is deliberately general, so it
also covers a mode-locked-laser interference example (Eqs. ~39-40) and,
in the Appendix, collisional effects.

Section 3, "Application. The effect of finite transit time," specializes
that formalism to an atom crossing a focused Gaussian TEM00 beam waist,
observed over a length L explicitly assumed small compared with the
Rayleigh length z_R (citing Kogelnik and Li 1966, and Siegman 1971, for the
Gaussian-beam formalism), with radial velocity v_r and impact parameter p.
For one trajectory the result is stated plainly: "For a given velocity, the
absorption curve is a Voigt profile, convolution of a Lorentzian and a
Gaussian curves." That Voigt is then averaged over the Maxwell-Boltzmann
radial-velocity distribution f(v_r) and over p, giving Eq. (46), the
paper's central result:

"The absorption profile as a function of omega_L is the convolution of a
Lorentzian curve of width Gamma_e/2 with a double exponential curve of
width delta*log2 at half maximum,"

with delta = <v_r>/w0 (the reciprocal mean transit time) and the text
noting the result "is in agreement with that calculated by Borde [11] in
the case of a three-level system." The paper ties the cusp explicitly to
slow atoms: "the particular sharp-point shape of the broadening is due to
slow atoms, which stay a long time in the beam and contribute much to the
absorption but very little to the broadening." It also flags, and
dismisses by citing Biraben's unpublished 1977 thesis [20], the same
low-v_r divergence concern our own M9 Monte Carlo independently
re-discovered: "the calculation is not valid for atoms of very low radial
velocity v_r... Nevertheless, it can be shown that the corresponding
correction is negligible." In the opposite, long-transit limit (delta much
less than Gamma_e) the double exponential collapses to a delta function
and Eq. (46) reduces to the pure-Lorentzian Eq. (48) -- the no-transit
sanity limit.

Section 4 tests Eq. (46) against experiment: the 3S to 4D5/2 line in sodium
at 5787.3 Angstrom, recorded with two focusing lenses (f = 25 cm, w0 ~ 25
micron, giving a visibly non-Lorentzian, sharp-cusped, fast-decaying-wing
trace) and f = 50 cm, w0 ~ 50 micron (narrower, closer to Lorentzian). Using
the known ratio delta_4 = 2*delta_5 between the two configurations, the
width difference between the traces is solved for delta_5, and the result
agrees with the transit-time estimate from w0 and the RMS radial velocity.
The final width budget for the narrower trace: natural linewidth Gamma_e/4pi
= 1.6 MHz (Lorentzian FWHM) plus about 1 MHz more from "residual frequency
jitter of the laser" and "collisional broadening... due to the presence of
impurities in the experimental cell." The Appendix separately shows the
two-photon lineshape is insensitive to velocity-changing collisions (A(Omega)
depends on E(t)^2 at one instant, not a two-time correlation), so collisions
only enter as an ordinary phase-interruption Lorentzian term, a mechanism
distinct from transit broadening.

**Where the Voigt comes from, and why it is easy to mis-cite this paper.**
Biraben *does* contain a Voigt, and it is not the final result. The Voigt
above is the **per-velocity-class** profile; the double-exponential appears
only *after* averaging over the Maxwell-Boltzmann radial velocities in
Eq. (46). Anyone quoting the intermediate step will report this paper as
giving a Voigt -- which is exactly the error `bruvelis2012` carried in this
repository until 2026-07-30.

## Bridges to this repository -- kernel-fidelity verdict

Our `methods/02_the_lineshape.md` S2.5 states that Biraben, Bassini and
Cagnac "derived the finite-transit Doppler-free two-photon line as exactly
a Lorentzian convolved with a two-sided exponential," giving
K_transit(nu) ~ exp(-|nu|/b), FWHM = 2b*ln2. That is a faithful, essentially
verbatim restatement of Eq. (46) -- "convolution of a Lorentzian curve of
width Gamma_e/2 with a double exponential curve of width delta*log2 at half
maximum" -- not a paraphrase drift.
<!-- not-from-pdf: the first quotation in this paragraph is our own
methods/02 text, not the paper's. The second is the paper's Eq. (46)
sentence, but this PDF's text layer renders the typeset Greek as Latin
lookalikes (Gamma_e as "Te", delta as "à", omega_L as "wL"), so
test_lit_quotes_are_verbatim.py cannot match it against extracted text.
It is checked by eye against the rendered page. --> Our K_transit is precisely the paper's
double-exponential factor, with the natural Lorentzian (Gamma_e/2, i.e.
Gamma_nat in our notation) factored out and handled separately in the
convolution chain, matching how the paper itself separates the two.

The paper's Eq. (46) is exact only for its own idealized geometry: a single
w0 evaluated at the waist, L << z_R, no explicit I^2 (saturation) weighting,
no explicit collection-solid-angle weighting, and the crossing-flux
divergence at v_r -> 0 dismissed by citation to an unpublished thesis
rather than derived in this paper. Module M9 (the 3D Maxwell-Boltzmann
Monte Carlo with full w(z), I^2 weighting and the collection profile) is
correctly framed in our docs as an *extension* beyond Eq. (46)'s
idealization, not as something Eq. (46) itself already contains -- and it
is not misattributed to this paper. **Verdict: faithful, not an
uncredited extension.** The analytic core our methods chapter attributes to
Biraben-Bassini-Cagnac is exactly Eq. (46); everything M9 adds beyond that
idealization is correctly kept off this paper's account.

**On focused beams and wavefront curvature.** The paper's transit-time
derivation is restricted, by explicit assumption, to atoms observed "in the
vicinity of the waist... over a length L which is small compared to the
Rayleigh length z_R," citing Kogelnik and Li and Siegman for the
underlying Gaussian-beam formalism. That is a domain restriction, not a
compensation mechanism -- the paper only ever treats the locally flat
wavefront at the waist and never analyzes trajectories away from it. No
form of "wavefront curvature," "phase curvature," or an exact-compensation
result between curvature-induced broadening and off-axis transit time
appears anywhere in the text; no such mechanism is derived, hinted at, or
needed for Eq. (46). So this 1979 paper does **not** already contain the
seed of the PRA 86, 012501 (2012) curvature-compensation claim -- that
paper's regime, atoms sampling the beam away from the waist where
wavefront curvature matters, is explicitly outside what Biraben 1979
considers by its own L << z_R assumption.

Why this matters for the paper: it upgrades the transit model from "assumed
shape" to "literature-standard analytic form," and it means the M8
Voigt-vs-Lehmann BIC test is Gaussian-core (Voigt) vs the BBC-1979 cusp -- a
test between two published forms, not against a made-up one. Our M9
Monte-Carlo then refines the BBC idealization for our exact 3D-Maxwell-
Boltzmann + w(z) + I^2 + collection conditions (finding the real kernel
slightly MORE cusped, excess kurtosis ~4.6).
