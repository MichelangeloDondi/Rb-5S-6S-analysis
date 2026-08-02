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

Nearest prior art: a spatially-varying AC-Stark shift producing an asymmetric lineshape from which alpha was extracted (standing wave, numerical Bloch). Bounds our novelty claim (we do NOT claim the asymmetry's existence) and supplies the fringe-averaged FM regime. Lineage: Wieman, Noecker, Masterson & Cooper, *PRL* **58**, 1738 (1987), the Cs 6S→7S parity-violation precedent.

**What it is.** Yb 6s² ¹S₀ → 5d6s ³D₁ (408 nm) — a one-photon forbidden Stark-induced transition, collimated atomic beam, intense standing wave in a power-buildup cavity. Numerical optical-Bloch lineshapes, integrated over trajectories, velocities and standing-wave phase. *(A "20–60 min each" computation time appeared here until 2026-07-30. No such figure is in the paper — searches for the numbers, for "takes", "runtime", "CPU" and "computation" all come up empty. It has been removed rather than re-sourced.)* They fit the measured asymmetric lineshapes and extract the ac-Stark parameter alpha = -0.312(34) Hz/(V/cm)^2 — so the asymmetry-as-observable idea exists in prior art; the novelty claim must be narrower than "first use of the asymmetry."

**Delineation (what is genuinely not in Stalnaker/Wieman):**

| Axis | Stalnaker 2006 | This work |
|---|---|---|
| Transition | 1-photon Stark-induced (signal proportional to I) | 2-photon (signal proportional to I^2) |
| Ensemble | collimated beam, velocity-selective | thermal vapor cell |
| Regime | fringe-resolved: FM index xi/Omega >~ 1, Bessel sidebands, sub-Doppler features | fringe-averaged: xi/Omega ~ 10^-3, atoms see the time-averaged envelope |
| Lineshape | numerical Bloch, per-condition | closed-form shift density f(s) proportional to \|s\| on [-S0,0] |
| Extraction | full-shape fit; needs beta, cavity field, velocity model, per-scan free center | closed-form ramp fit with a per-trace free center; the ramp SHIFT is absorbed by the free center, so S0 is read from the drift-invariant SHAPE ASYMMETRY (skew) |
| Saturation | saturating + hole-burning entangled with the asymmetry | unsaturated throughout (amplitude proportional to P^2 confirmed) |

The generic quasi-static law both regimes reduce to: signal weight proportional to I^n over a Gaussian envelope gives dA proportional to dI/I, hence f(s) proportional to \|s\|^(n-1) — uniform for their n=1, triangular for our n=2. The same dA proportional to dI/I holds for a thin evanescent shell, the geometry-independence bridge to the nanofibre extension.

**Gift #1 — their FM framework settles our <E^2> convention question.** Their Sec. IV/Fig. 6: an atom crossing standing-wave fringes sees frequency modulation of depth xi = (1/2)*alpha*epsilon0^2 at rate Omega/2pi = 2v/lambda. For us: lambda/2 ~ 0.50 um fringes, axial thermal speed ~280 m/s -> Omega/2pi ~ 0.56 GHz, xi = S0 <~ 1 MHz -> modulation index xi/Omega <~ 2e-3 -> pure carrier at the time-averaged intensity. So the shift is set by the fringe-averaged intensity I1+I2 = (1+rho)*I1 — no coherent x2 fringe enhancement. But the fringe-resolved tail is NOT benign: near-transverse atoms (small axial speed) sample the node/antinode arcsine, and because the fringe multiplies the shift (s -> s(1+x), x arcsine) it SUPPRESSES the ramp skew — kappa3 -> S0^3*(1/135 - f_res/10) at rho=1, a -13.5*f_res fractional leverage. Negligible at w0=50 um (~5-8% of an already-below-noise skew), ~25% at w0=16 um, and same-sign-additive to the beam-divergence correction (`rb5s6s/fringe_tail.py`).

## Audit against the PDF, 2026-07-30

Not a full pass, but the claims §5 of `LITERATURE.md` leans on were checked
directly, and they hold.

- **The concession is correct.** Their Eq. (45) does extract a polarizability
  from the fitted lineshapes:
  $\alpha_0^{ac}(^3D_1) + \alpha_2^{ac}(^3D_1) - \alpha_0^{ac}(^1S_0) = -0.312(34)$
  Hz/(V/cm)². Note it is a **combination** of scalar and tensor ac
  polarizabilities minus the ground-state scalar — structurally the same kind of
  differential this programme calls $\Delta\alpha$, not a single $\alpha$. Their
  Table IV gives the per-field-setting fits (all-data row: ac-Stark shift
  −0.3284(5), $\beta$ 2.237(2), $s$ 0.9730(3), $N = 45$), and Eq. (47) gives
  $|\beta| = 2.19(8)\times10^{-8}$ $e a_0$/(V/cm).
- **The FM framework is as this note describes it.** Eq. (37) is
  $\xi = \frac{1}{2}\alpha\varepsilon_0^2$ for the modulation *depth*, and
  Eq. (38) is $\Omega/2\pi = 2v_y/\lambda = 2\Delta\nu_D$ for its *rate*, with
  the factor of two arising "from the fact that the ac-Stark shift is quadratic
  so that the period of the shift is half that of the wave length". Their own
  experiment runs at a modulation depth of **0.28 to 7.4 MHz**. Fig. 6 shows the
  Bessel-sideband evolution at $\xi = 1\Omega$, $10\Omega$, $100\Omega$.
- **One nuance worth carrying, because it is a factor of two.** Their
  carrier-only criterion is stated as $\xi/2 \ll \Omega$, not $\xi \ll \Omega$.
  This programme quotes a modulation index $\xi/\Omega \lesssim 2\times10^{-3}$,
  which satisfies either form by three orders of magnitude, so nothing shipped
  changes — but a paper sentence should use their inequality, not a rounded
  version of it.
- **Every characterisation of Wieman that [wieman1987](wieman1987.md) sources
  from this paper's introduction is verbatim**, including "Spatial variation of
  the intense standing-wave light field leads to position- and
  velocity-dependent ac-Stark shifts. This results in asymmetric line shapes
  exhibiting sub-Doppler features" and "generalizes and extends the approach of
  Wieman et al." Confirmed also that this paper **never** characterises Wieman's
  calculation as numerical, which is why that word was struck from the Wieman
  note the same day.

**Still not done:** a claim-by-claim pass over the delineation table and the
"Gift #1" fringe-tail derivation. Those are this repository's own inferences
built on the paper rather than reports of it, so they need checking against
`rb5s6s/fringe_tail.py` as well as against the PDF.

