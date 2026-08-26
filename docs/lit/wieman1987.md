---
citekey: wieman1987
type: article
authors:
  - Wieman, C. E.
  - Noecker, M. C.
  - Masterson, B. P.
  - Cooper, J.
title: 'Asymmetric line shapes for weak transitions in strong standing-wave fields'
journal: Phys. Rev. Lett.
volume: 58
pages: 1738
year: 1987
doi: 10.1103/PhysRevLett.58.1738
arxiv: null
pdf: PDF_papers/wieman1987.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags: []
verified_date: '2026-08-02'
summary: >
  The foundational precedent for AC-Stark lineshape asymmetry: a weak transition
  (the forbidden 6S->7S M1 and Stark-induced line in Cs, from the JILA
  parity-violation programme) excited in an intense STANDING WAVE, whose spatial
  variation gives position- and velocity-dependent shifts and a Doppler-free,
  intensity-dependent distortion of the line, modelled with optical Bloch
  equations. Cited here as the work that owns "asymmetric lineshapes from a
  distributed AC-Stark shift" -- and, on the evidence available, as a
  ONE-PHOTON mechanism distinct from this programme's I-squared weighting.
loci:
  - THEORY
section: prior-art
---

# wieman1987

Verified against the full four-page article (Phys. Rev. Lett. 58, 1738-1741, 27 April 1987).

## The system and method

A very weak atomic transition, the forbidden 6S -> 7S magnetic-dipole and Stark-induced line in caesium studied in the JILA parity-violation experiment, is excited where an atomic beam crosses an intense standing-wave laser field. The resonance line shape shows an intensity-dependent distortion that is Doppler-free and independent of the excitation rate. The line shape is obtained by solving the optical Bloch equations for one atom, with the spatially varying AC-Stark shift entering as a phase proportional to $\varepsilon^2\cos[kz(t)]$, $z(t)=z_0+v_z t$, and averaging numerically over the initial standing-wave phase $z_0$ and the transverse velocity distribution. The field is taken as constant over the distance an atom moves in one lifetime, so the transverse intensity profile is not integrated. The calculated line shape agrees well with the measured one.

No shift probability distribution, moment, or cumulant is computed anywhere in the paper. The only asymmetry measure used is an operational ratio $D=d/h$, the wing-distortion amplitude over the undistorted peak height, compared against numerical output. The physical picture offered is a fast-atom/slow-atom distinction: atoms crossing many fringes per lifetime see the fringe-averaged field and give symmetric wings, while slow atoms sit at a near-frozen fringe and skew toward the local field maximum. The standing wave's spatial variation makes the shift position- and velocity-dependent, producing the asymmetry and its sub-Doppler features ([stalnaker2006](stalnaker2006.md)). The authors state that, to their knowledge, this is the first observation of this type of line-shape distortion (p. 1738).

## Use in this record

The transition studied is single-photon throughout, magnetic-dipole plus Stark-induced E1, so its $\varepsilon^2$ dependence is the ordinary quadratic AC-Stark shift, not a two-photon rate weighting ([delone1980](delone1980.md) treats the $I^k$ weighting for $k$-photon excitation generally). For a rate $\propto I^{n}$, the signal-weighted shift distribution is $f(s)\propto\vert s\vert ^{n-1}$ ([THEORY_NOTE](../THEORY_NOTE.md) §2). At $n=1$, the case of a Stark-induced forbidden line such as this one, that distribution is uniform with third cumulant $\kappa_3=0$, exactly zero skew, so a one-photon mechanism of this kind cannot produce the skewed closed-form distribution used elsewhere in this analysis (intrinsic skewness $g_1=+0.566$). That skew is attributed instead to $I^2$ weighting of a two-photon rate over a transverse Gaussian profile, with the standing wave shown not to shift the mean (M19). The measurement also differs by apparatus and treatment, using an atomic beam rather than a vapour cell, and a numerical Bloch calculation averaged over standing-wave phase and transverse velocity rather than a closed form with analytic cumulants. This paper treats the asymmetry as a distortion to be removed, as does its descendant [antypas2018](antypas2018.md) ("Lineshape-asymmetry elimination"). Here it is used as the measurement channel instead. No quantity from this paper enters the analysis directly. It stands as prior art for the general phenomenon, a spatially varying AC-Stark shift distorting a line asymmetrically, computed from first principles with no free parameters, which does not extend to the two-photon mechanism this analysis relies on.
