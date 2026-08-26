---
citekey: stalnaker2006
type: article
authors:
  - Stalnaker, J. E.
  - Budker, D.
  - Freedman, S. J.
  - Guzman, J. S.
  - Rochester, S. M.
  - Yashchuk, V. V.
title: 'Dynamic Stark effect and forbidden-transition spectral lineshapes'
journal: Phys. Rev. A
volume: 73
number: 4
pages: 043416
year: 2006
doi: 10.1103/PhysRevA.73.043416
arxiv: physics/0512111
pdf: PDF_papers/Stalnaker_2006_dynamic-Stark-forbidden-transition-asymmetric-lineshapes.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: null
summary: >
  Nearest prior art: a spatially-varying AC-Stark shift producing an
  asymmetric lineshape from which alpha was extracted (standing wave,
  numerical Bloch).
loci:
  - P1
  - THEORY
  - constants
  - methods/03
section: prior-art
---

# stalnaker2006

Held. Eq. (45), Eqs. (37)-(38), and Table IV were verified against the PDF, as was the wording drawn from this paper's introduction into [wieman1987](wieman1987.md). The delineation table and the fringe-suppression derivation below have not been checked against the PDF.

## The system

Yb $6s^2 ^1S_0 \to 5d6s ^3D_1$ (408 nm), a one-photon forbidden Stark-induced transition studied with a collimated atomic beam crossing an intense standing wave in a power-buildup cavity. Numerical optical-Bloch lineshapes, integrated over trajectories, velocities, and standing-wave phase, are fit to the measured asymmetric lineshapes to extract the ac-Stark parameter. Lineage: Wieman, Noecker, Masterson, and Cooper, *Phys. Rev. Lett.* **58**, 1738 (1987), the Cs $6S \to 7S$ parity-violation precedent.

## The numbers

Eq. (45) gives $\alpha_0^{ac}(^3D_1) + \alpha_2^{ac}(^3D_1) - \alpha_0^{ac}(^1S_0) = -0.312(34)$ Hz/(V/cm) $^2$, a combination of scalar and tensor ac polarizabilities minus the ground-state scalar, not a single polarizability. Table IV (all-data row) gives ac-Stark shift $-0.3284(5) $, $\beta = 2.237(2) $, $s = 0.9730(3) $, $N = 45$. Eq. (47) gives $\vert \beta\vert  = 2.19(8)\times10^{-8} e a_0$/(V/cm). The experiment runs at a modulation depth of 0.28 to 7.4 MHz, from Eq. (37), $\xi = \tfrac12\alpha\varepsilon_0^2$, and Eq. (38), $\Omega/2\pi = 2v_y/\lambda = 2\Delta\nu_D$, with the factor of two arising because the ac-Stark shift is quadratic, so the shift's period is half the light's wavelength. The paper's carrier-only criterion is $\xi/2 \ll \Omega$, not $\xi \ll \Omega$.

## Delineation from the 5S-6S two-photon case

| Axis | Stalnaker 2006 | 5S-6S two-photon |
|---|---|---|
| Transition | 1-photon Stark-induced (signal proportional to $I$) | 2-photon (signal proportional to $I^2$) |
| Ensemble | collimated beam, velocity-selective | thermal vapor cell |
| Regime | fringe-resolved: FM index $\xi/\Omega \gtrsim 1$, Bessel sidebands, sub-Doppler features | fringe-averaged: $\xi/\Omega \sim 10^{-3}$, atoms see the time-averaged envelope |
| Lineshape | numerical Bloch, per-condition | closed-form shift density $f(s) \propto \vert s\vert $ on $[-S_0,0]$ |
| Extraction | full-shape fit, needing $\beta$, cavity field, velocity model, per-scan free center | closed-form ramp fit with a per-trace free center, which absorbs the ramp shift, so $S_0$ is read from the drift-invariant shape asymmetry (skew) |
| Saturation | saturating, with hole-burning entangled with the asymmetry | unsaturated throughout (amplitude proportional to $P^2$ confirmed) |

Both regimes reduce to the same quasi-static law: signal weight proportional to $I^n$ over a Gaussian envelope gives $dA \propto dI/I$, hence $f(s) \propto \vert s\vert ^{n-1}$, uniform for Stalnaker's $n=1$ and triangular for the two-photon case's $n=2$. The same $dA \propto dI/I$ relation holds for a thin evanescent shell, extending the argument to the nanofibre geometry.

## The fringe-modulation regime

Section IV and Fig. 6 give the fringe-modulation framework used here. An atom crossing standing-wave fringes sees frequency modulation of depth $\xi = \tfrac12\alpha\varepsilon_0^2$ at rate $\Omega/2\pi = 2v/\lambda$. For a fringe spacing $\lambda/2 \approx 0.50 \mu\text{m}$ and axial thermal speed $\approx 280$ m/s, $\Omega/2\pi \approx 0.56$ GHz and $\xi = S_0 \lesssim 1$ MHz, giving a modulation index $\xi/\Omega \lesssim 2\times10^{-3}$: a pure carrier at the fringe-averaged intensity $I_1+I_2=(1+\rho)I_1$, with no coherent fringe enhancement of the shift. Near-transverse atoms, with small axial speed, instead sample the node-antinode arcsine distribution, which suppresses the ramp skew: $\kappa_3 \to S_0^3(1/135 - f_{res}/10)$ at $\rho=1$, a $-13.5 f_{res}$ fractional leverage. As a fraction of the intrinsic $+0.566$ triangle skew, this is small at $w_0=64 \mu\text{m}$ (7-14% of an already-below-noise skew) and reaches 26-28% at $w_0=16 \mu\text{m}$, additive in sign to the beam-divergence correction.

## Use in this record

The asymmetric-lineshape method used in this record's two-photon analysis is bounded in novelty by this paper. A spatially-varying ac-Stark shift producing an asymmetric lineshape, from which a polarizability parameter is extracted, is established prior art, generalizing Wieman (1987). What differs is the transition order (two-photon vs. one-photon), the ensemble (vapor cell vs. beam), the regime (fringe-averaged vs. fringe-resolved), and the extraction method (closed-form skew fit vs. full numerical-Bloch fit).
