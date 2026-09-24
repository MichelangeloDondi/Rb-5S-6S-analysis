---
citekey: belland1982
type: article
authors:
  - Belland, P.
  - Crenn, J. P.
title: 'Changes in the characteristics of a Gaussian beam weakly diffracted by a circular aperture'
journal: Appl. Opt.
volume: 21
number: 3
pages: 522-527
year: 1982
doi: 10.1364/AO.21.000522
arxiv: null
pdf: PDF_papers/Belland_1982_Gaussian-beam-diffracted-circular-aperture.pdf
held: true
status: VERIFIED
audit: private/cache/lit_intake_2026-09-22_audits/belland1982.md  # line-by-line against the held PDF (scanned, equation-dense); every cited equation number confirmed exact against page images, one Dickson-attribution scope tightened
author: agent
routing:
  - CITE
verify_flags:
  - 'The held PDF is the published article (Optica Publishing Group), downloaded by the owner by hand. Read in full on 2026-09-22, Sections I to V. The text layer is a scan with an advertisement set into the conclusion column, so nothing from the conclusion is quoted. Journal record from Crossref, which lists the first page only; the last page, 527, is read from the held PDF.'
  - 'The paper states its criteria in the 1/e INTENSITY radius r = w/sqrt(2), not the 1/e^2 radius w this record uses. The conversions in the body are the reviewer''s arithmetic.'
verified_date: 2026-09-22
summary: >
  Closed forms for the far field of a Gaussian beam weakly clipped by a circular
  aperture, which stays close to a Gaussian with changed parameters. With the waist in
  the aperture plane and a relative power loss u = dP/P, the equivalent waist shrinks by
  1 - sqrt(u), the divergence grows by 1/(1 - sqrt(u)) and the fictitious waist
  intensity by about 1/(1 - 2 sqrt(u)). A waist away from the aperture adds a factor
  cos(ka^2/2R0), so the change vanishes at discrete aperture radii. The regimes, in the
  1/e intensity radius r0 at the aperture: diffraction negligible for a/r0 > 3; a
  weakly modified Gaussian for 1.6 < a/r0 < 3; below 1.6 the profile is no longer
  Gaussian and the formulas fail. A 1 per cent power loss already changes the
  divergence by about 10 per cent, so a small loss does not mean an unchanged beam.
loci:
  - constants
  - methods/02
  - methods/03
section: method-anchors
---

# belland1982

VERIFIED. Held (published version, scanned text). Read in full on 2026-09-22.

## What it does

Section II defines the beam by its intensity profile with r the 1/e intensity radius, r = w/sqrt(2) for the 1/e field radius w (Eq. 1). The power transmitted through an aperture of radius a is 1 - exp(-a^2/r0^2) of the incident power (Eqs. 9-10), so the loss stays under 1 per cent for a/r0 above 2.2. Section III puts the waist in the aperture plane and takes the far-field profile from Fresnel diffraction as a Bessel series (Eqs. 11, 14, after Schell and Tyras). Two methods fit an equivalent Gaussian to it: three common points of the profile (Eqs. 16-27), or its on-axis intensity and its power (Eqs. 30-36). To first order both give the same result. The equivalent waist is r0' = r0 (1 - sqrt(u)) with u = dP/P (Eq. 37). The divergence half-angle is larger by 1/(1 - sqrt(u)) (Eq. 38). The fictitious waist intensity is higher by about 1/(1 - 2 sqrt(u)) (Eq. 39). Figures 3 and 4 show the effect beginning near a/r0 = 3 and the simple forms adequate down to about 1.6.

Section IV moves the waist a distance l from the aperture and uses Dickson's on-axis far-field formula (Eq. 44). The first-order changes then carry cos(ka^2/2R0), with R0 the wavefront radius at the aperture (Eqs. 51-53). Diffraction drops out to first order at the discrete radii where that cosine vanishes (Eqs. 54-55) and is largest where it is plus or minus one (Eqs. 56-57). With the reduced parameter p = l lambda/rm^2 the ratios oscillate more as the waist moves away (Figs. 5-6, Eqs. 62-63). The conclusion states the three regimes in the summary and the 1 per cent loss, 10 per cent divergence case.

## Use in this record

- The published source of the record's closed form. At equal incident power the clipped beam's on-axis far-field intensity is [1 - exp(-a^2/2r0^2)]^2 times the unclipped one (Eqs. 30-31. Eq. 30 is also derivable from Dickson 1970, as the paper notes). In the record's 1/e^2 radius w that is (1 - e^{-a^2/w^2})^2. Divided by the transmission of Eq. (9), 1 - e^{-2a^2/w^2}, it is `lineshape.aperture_onaxis_factor` exactly. The on-axis amplitude integrates the truncated Gaussian directly, so this part holds at any clipping in the far field. The validity limit below concerns the profile, not the peak.
- The same two exact quantities, peak and power, define the paper's second equivalent Gaussian (Eq. 35). Read in the focal plane its 1/e^2 radius is w_eq = w_free sqrt(1 - u)/(1 - sqrt(u)), with w_free = lambda f/(pi w_in) and u = e^{-2a^2/w_in^2}. The reviewer's arithmetic then gives `lineshape.aperture_onaxis_factor_actual` = (w_act/w_eq)^2, since the record's closed form (1 - e^{-x})^2/(1 - e^{-2x}) (w_act/w_free)^2 reduces to it. It reproduces the record's 0.890 for a 2.46 mm input, (42.42/44.97)^2, and its 0.997 at the 0.80 mm node. Only the 1/e^2 reading w_act needs the Hankel transform.
- The regime check for the modulator's bore. With the bore radius a = 1.5 mm (`constants.EOM_APERTURE_RADIUS_M`), the weakly clipped regime a/r0 > 1.6 needs an input 1/e^2 radius below about 1.33 mm, and negligible diffraction (a/r0 > 3) below about 0.71 mm. The input radii of 1.4 to 4.0 mm examined in the docstring of `constants.W0_CENTRAL_M` give a/r0 from 1.52 down to 0.53, all below 1.6. Across that range the clipped focus is not a Gaussian and no equivalent-Gaussian width describes it. That supports reading the bore-limited focus from its own diffraction (`docs/methods/02`, section 2.5).
- The warning that a small power loss is not a small change. At 1 per cent loss the divergence, and so the focused spot, already moves by about 10 per cent through sqrt(u). A transmission measured near one does not show that the focus is the unclipped one.
- The width definition matters. The paper matches its equivalent Gaussian on three points or on peak and power, while the record's actual waist is the radius where the focal intensity first falls to 1/e^2 of its on-axis value. On a clipped focus the two differ, and a second-moment width differs again (schmidt2011b). karman1998 follows the same focus into the strongly clipped regime, and lim2021 measures its axial lengthening.

## Limits

- Scalar, paraxial and far-field, with the aperture centred on the beam. It covers the weak-clipping regime only and gives no intensity distribution beyond the equivalent Gaussian's parameters. It has no treatment of the rings or of the axial structure of the focus, and nothing on M^2.
