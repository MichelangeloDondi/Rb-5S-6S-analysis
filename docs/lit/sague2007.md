---
citekey: sague2007
type: article
authors:
  - Sagué, G.
  - Vetsch, E.
  - Alt, W.
  - Meschede, D.
  - Rauschenbeutel, A.
title: 'Cold Atom Physics Using Ultra-Thin Optical Fibers: Light-Induced Dipole Forces and Surface Interactions'
journal: Phys. Rev. Lett.
volume: 99
pages: 163602
year: 2007
doi: 10.1103/PhysRevLett.99.163602
arxiv: quant-ph/0701167
pdf: PDF_papers/Sague_2007_ONF-dipole-forces-vdW-surface-interactions-Cs.pdf
held: true
status: VERIFIED
routing:
  - CITE
  - FEED
verify_flags:
  - 'Held as arXiv v4 (quant-ph/0701167v4, stamped 4 February 2009 -- later than
    the 2007 publication, so v4 is a post-publication revision). The journal
    fields are the standard record for this DOI and were not re-checked against
    the published article.'
verified_date: 2026-07-30
summary: >
  The paper that DEFUSES the "unexplained ONF linewidth" premise, and in doing so
  supplies the mechanism for what is left of it. Cold Cs around a 500 nm optical
  nanofibre; measured linewidths approach 6.2 MHz as probe power vanishes,
  "almost 20%" above the 5.2 MHz natural width -- and they EXPLAIN it, as the
  van der Waals shift plus the modification of the spontaneous emission rate,
  which "have the same magnitude and only their combination yields the very good
  agreement". Decisively, their model carries a POSITION-DEPENDENT decay rate
  gamma(r) inside the spatial integral, predicting a 57% enhancement at the
  surface, and the fit has only TWO free parameters -- atom number and a
  frequency offset -- with no width parameter at all. Their 6.2 MHz is a model
  OUTPUT, not a residual. That is the exact structural contrast with
  patterson2018, which passes a scalar Gamma_0 and is left with 2 MHz it cannot
  explain.
loci:
  - P2
  - THEORY
section: oist-lineage
---

# sague2007

**Read from the held arXiv v4.** Bonn (Meschede/Rauschenbeutel), the origin of
the whole optical nanofibre cold-atom line, and the paper `patterson2018` cites
as its ref [8].

## What reading it settles

Two claims about this paper were sitting in this repository as **REPORTED**,
from an external literature pass, and both were doing real work: that its model
has no fitted width parameter, and that its decay rate reaches +57% at the
surface. **Both are confirmed from the source, and the second is verbatim.**

## The system

A Cs MOT (1/√e radius 0.6 mm, 125 µK) overlapped with the waist of a tapered
fibre — **500 nm diameter, 5 mm waist length, 93% transmission**, single
HE₁₁ mode at the 852 nm Cs D2 wavelength. A probe scanned ±24 MHz across
6²S₁∕₂ F=4 → 6²P₃∕₂ F=5 is launched *through* the fibre and its transmission
recorded on an APD. Probe powers span femtowatts to 1 nW; the probe laser
linewidth is 1 MHz against the 5.2 MHz natural width. MOT beams and field are off
during the 10 ms spectroscopy window.

## The model, which is the part that matters

Their Eq. (1) is

$$A_P(\delta) = \frac{\hbar w}{P} \int \rho_{\delta,P}(r,z)  \Gamma\left(I_P(r), \gamma(r), \delta + \delta_{\rm vdW}(r)\right) {\rm d}V$$

Read the arguments of $\Gamma$: the intensity, **the decay rate, and the shift
are all functions of $r$**. The decay rate is split (their Eq. 2) as
$\gamma(r) = \gamma_{\rm free}(r) + \gamma_{\rm guid}(r)$, with
$\gamma_{\rm free}(r)$ taken from [klimovducloy2004](klimovducloy2004.md) and

$$\gamma_{\rm guid}(r) \simeq 0.3 \gamma_0  I_P(r)/I_P(a)$$

where $a$ is the fibre radius and $0.3\gamma_0$ is the emission rate of an atom
*on* the surface into the guided mode.

The van der Waals shift $\delta_{\rm vdW}(r)$ is **their own calculation**, not a
number imported from elsewhere. Verbatim: "We calculated the vdW shift,
δvdW(r), for the D2 line of Cs near a 500 nm diameter dielectric cylinder [15]."
The emphasis is worth stating plainly rather than with markup inside the
quotation: it is *their* calculation, and the cylinder is *dielectric*.
Their [15] is `boustimi2002`, cited for the *method*. This
distinction was missed on the first pass through and matters (established
2026-07-31): the standing objection that Boustimi's worked case is an argon atom
near an *aluminium* wire, while this fibre is silica, does not land — nobody
imported a metallic number into a dielectric problem. What has to be reproduced
to redo this is a calculation, not a lookup. See
[boustimi2017](boustimi2017.md) and [frawley2012](frawley2012.md).

**On the surface, Eq. (2) predicts a 57% increase of the spontaneous emission
rate** — verbatim: "On the surface of the fiber, Eq. (2) then predicts a 57%
increase of the spontaneous emission rate of the Cs atoms, resulting in a
broadening of the absorbance line shapes."

The density $\rho_{\delta,P}(r,z)$ is a Gaussian cloud times a factor
$f_{\delta,P}(r)$ from a 100,000-trajectory Monte Carlo including the attractive
vdW force and the saturating dipole force.

## The two results this repository needs

**1. There is no fitted width parameter.** Verbatim: "$A_P(\delta)$ from Eq. (1)
can now be adjusted to the experimental line shapes, **the only fitting
parameters being $n_0$ and an experimental frequency offset**." Two free
parameters, neither of them a width. Their linewidth is therefore an *output* of
a model containing $\gamma(r)$ and $\delta_{\rm vdW}(r)$, not a fitted residual.

**2. The excess is explained, and by two effects of equal size.** Measured
linewidths "approach 6.2 MHz for vanishing powers. This result exceeds the
natural Cs D2 linewidth in free space by almost 20%." And then: "This broadening
can be explained by surface interactions, i.e., the vdW shift of the Cs D2 line
and the modification of the spontaneous emission rate of the atoms near the
fiber... **Both effects have the same magnitude and only their combination
yields the very good agreement between our model and the experimental data.**"

## What this does to the excess-linewidth question

**It removes Sagué from the unexplained column entirely** — a correction this
repository can now make from the source rather than on report. The count of ONF
experiments reporting an *unaccounted* excess is `patterson2018` plus the
newly-surfaced Liu *et al.* (2024/25), not three.

**And the contrast with Patterson is the whole finding.** Sagué put
$\gamma(r)$ **inside** the spatial integral and needed no residual.
[patterson2018](patterson2018.md)'s Eq. (10) passes $\Gamma_0$ in as a **scalar**
while using the same physical quantity — $\alpha(r) = \Gamma_{\rm 1D}(r)/\Gamma_0$,
their Eq. (3) — as a detection weight, and is left with 2 MHz it explicitly
cannot explain. Two experiments in the same geometry, eleven years apart: the one
that modelled the decay rate as position-dependent closed its budget, and the one
that did not has an unexplained residual of about the size that omission would
produce. That is no longer a hypothesis about a mechanism; it is a controlled
comparison already present in the literature. Patterson's fibre is 240 nm against
Sagué's 500 nm, where guided coupling is *stronger*, so the omitted term should
be larger there, not smaller.

**A caution against over-reading it.** Sagué is one-photon absorption on cold
atoms with a 1 MHz probe laser and 20% excess; Patterson fits a five-parameter
model to spectra taken with a desorption laser present. The two are not the same
measurement, and "Sagué's model structure would have absorbed Patterson's
residual" remains a **prediction to be tested by refitting**, not a demonstrated
result. What *is* now established is that the term is physically real and is
absent from Patterson's width.

**This sentence also said the term "is computable from
[klimovducloy2004](klimovducloy2004.md)"; that was too quick, and is corrected
here rather than dropped (2026-07-31).** That paper's closed form is
quasistatic, and its own Conclusion bounds the quasistatic regime at
$ka$ below $1/\varepsilon$ — 0.473 for silica, against $ka = 1.844$ for *this* fibre
and 0.967 for Patterson's (CALCULATED). Computable it is, but from that paper's
full electrodynamic Section IV, not from its Eq. (29). Sagué's own
$\gamma = \gamma_{\rm free} + \gamma_{\rm guid}$ split is the tell: a separate
guided-mode term is exactly what this regime demands.

## Two smaller things worth keeping

- **The dipole-force narrowing runs the other way and is large.** Above 100 pW
  the measured lines are "considerably narrower than what would be expected in
  absence of dipole forces and surface interactions"; at 1 nW "this narrowing
  exceeds 40%". Blue and red detunings both *reduce* the integrated near-surface
  density — for red detuning the acceleration toward the fibre is cancelled
  "almost perfectly" up to 100 nm by shorter time of flight and higher loss, and
  beyond that the reducing effects dominate. Any ONF lineshape model that omits
  light-induced dipole forces gets the *power* dependence wrong in the opposite
  direction from the surface terms.
- **The sensitivity is extraordinary and worth quoting in a proposal.** They
  extract effective atom numbers of **107, 14 and 2** fully-saturated atoms
  contributing at 1 nW, 52 pW and 6 pW; on resonance "as little as two atoms on
  average, coupled to the evanescent field surrounding the fiber, already
  absorbed 20% of the total power transmitted through the fiber". Maximum atomic
  density $4.4\times10^{10}$ cm⁻³; the mean atom-surface distance of the probed
  atoms is power-tunable down to **248 nm**.
