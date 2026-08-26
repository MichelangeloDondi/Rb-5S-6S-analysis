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

Held as arXiv v4 (quant-ph/0701167v4). The model's lack of a fitted width parameter and its predicted 57% increase in decay rate at the surface are both confirmed against the source, the second matching the paper's wording verbatim.

Work from Bonn (Meschede and Rauschenbeutel), the origin of the optical nanofibre cold-atom line and cited by patterson2018 as its reference [8].

## The system

A Cs magneto-optical trap (1/√e radius 0.6 mm, 125 µK) overlaps the waist of a tapered optical fibre (500 nm diameter, 5 mm waist length, 93% transmission), with a single HE₁₁ mode at 852 nm (Cs D2). A probe beam scanned ±24 MHz across 6²S₁∕₂ F=4 → 6²P₃∕₂ F=5 is launched through the fibre and its transmission recorded on an avalanche photodiode. Probe powers span femtowatts to 1 nW, with a probe laser linewidth of 1 MHz against the 5.2 MHz natural width. The MOT beams and field are switched off during the 10 ms spectroscopy window.

## The model

Their Eq. (1) is

$$A_P(\delta) = \frac{\hbar w}{P} \int \rho_{\delta,P}(r,z)  \Gamma\left(I_P(r), \gamma(r), \delta + \delta_{\rm vdW}(r)\right) {\rm d}V$$

The arguments of $\Gamma$ (intensity, decay rate, shift) are all functions of $r$. The decay rate is split (their Eq. 2) as $\gamma(r) = \gamma_{\rm free}(r) + \gamma_{\rm guid}(r) $, with $\gamma_{\rm free}(r)$ taken from [klimovducloy2004](klimovducloy2004.md) and

$$\gamma_{\rm guid}(r) \simeq 0.3 \gamma_0  I_P(r)/I_P(a)$$

where $a$ is the fibre radius and $0.3\gamma_0$ is the emission rate of an atom on the surface into the guided mode. The closed-form expression in klimovducloy2004 is quasistatic, valid only for $ka$ below $1/\varepsilon$ (0.473 for silica). This fibre's $ka = 1.844$ falls outside that range, so $\gamma_{\rm free}$ comes from the paper's full electrodynamic Section IV rather than its closed-form Eq. (29).

The van der Waals shift $\delta_{\rm vdW}(r)$ is the authors' own calculation: "We calculated the vdW shift, δvdW(r), for the D2 line of Cs near a 500 nm diameter dielectric cylinder [15]." Their [15] is `boustimi2002`, cited for the calculation method. The fibre here is silica, a dielectric, distinct from Boustimi's worked case of an argon atom near an aluminium wire. See [boustimi2017](boustimi2017.md) and [frawley2012](frawley2012.md).

The paper states: "On the surface of the fiber, Eq. (2) then predicts a 57% increase of the spontaneous emission rate of the Cs atoms, resulting in a broadening of the absorbance line shapes." The density $\rho_{\delta,P}(r,z)$ is a Gaussian cloud times a factor $f_{\delta,P}(r)$ from a 100,000-trajectory Monte Carlo calculation including the attractive van der Waals force and the saturating dipole force. The only fitting parameters in $A_P(\delta)$ are $n_0$ and an experimental frequency offset. The model carries no width parameter.

## The numbers

Measured linewidths approach 6.2 MHz for vanishing probe power, exceeding the natural Cs D2 linewidth (5.2 MHz) by almost 20%. The paper attributes the excess to two effects of comparable size: "This broadening can be explained by surface interactions, i.e., the vdW shift of the Cs D2 line and the modification of the spontaneous emission rate of the atoms near the fiber... Both effects have the same magnitude and only their combination yields the very good agreement between our model and the experimental data."

Above 100 pW, the measured lines are "considerably narrower than what would be expected in absence of dipole forces and surface interactions." At 1 nW, "this narrowing exceeds 40%." Blue and red detunings both reduce the integrated near-surface density. For red detuning, the acceleration toward the fibre is cancelled "almost perfectly" up to 100 nm by shorter time of flight and higher loss, beyond which the reducing effects dominate.

The extracted effective atom numbers are 107, 14, and 2 fully saturated atoms contributing at 1 nW, 52 pW, and 6 pW respectively. On resonance, "as little as two atoms on average, coupled to the evanescent field surrounding the fiber, already absorbed 20% of the total power transmitted through the fiber." The maximum atomic density is $4.4\times10^{10}$ cm⁻³, and the mean atom-surface distance of the probed atoms is power-tunable down to 248 nm.

## Use in this record

The comparison with [patterson2018](patterson2018.md) fixes the size of the unexplained residual in that paper's ONF linewidth budget. This model carries the decay rate $\gamma(r)$ inside the spatial integral and needs no residual term to match the data. Patterson's Eq. (10) instead passes $\Gamma_0$ in as a scalar, while using the same physical quantity, $\alpha(r) = \Gamma_{\rm 1D}(r)/\Gamma_0$ (their Eq. 3), only as a detection weight, and is left with about 2 MHz unexplained. Patterson's fibre (240 nm) is narrower than this one (500 nm), where guided-mode coupling is stronger, so the omitted term would be larger for Patterson's geometry. Patterson's fibre also falls outside klimovducloy2004's quasistatic regime (calculated $ka = 0.967$ against the 0.473 threshold), so the same guided-mode term is missing there too. Whether this model's structure would account for Patterson's residual has not been tested by refitting Patterson's data. The two measurements also differ in kind, one-photon absorption on cold atoms with a 1 MHz probe laser here, against a five-parameter fit to spectra taken with a desorption laser present in Patterson's case.
