# Collisional self-broadening

*[quantities index](README.md) · headline parameter*

**The question.** How much self-broadening does this experiment resolve
independently of the laser width and of the density scale? The quantity is
$\beta_{\rm self}$, the coefficient relating the collisional Lorentzian width
to the rubidium number density, in MHz per 1e12 per cubic centimetre, so that
$\gamma_{\rm coll} = \beta_{\rm self} N$.
**Takes.** The committed width fits across four temperatures. No new fitting.
**Gives.** The bound in each construction, the reason the fitted collisional
width is a floor rather than a resolved effect, the position of that bound
against the measured rungs above and below this line, and three levels of
improvement with their recipes.
**Skip if.** The question is the physics of the broadening mechanism, which is
[self-broadening](../wiki/self-broadening.md), or how the width channel is
shared with the light shift, which is
[the AC-Stark dossier](ac-stark-light-shift.md).

**Where it stands.** A bound. The pooled four-temperature construction gives
$\beta_{\rm self} \lt 0.0249$ MHz per 1e12 per cubic centimetre, and the reason it is a
bound is measured rather than assumed: across a factor of 52.5 in density the
fitted collisional width rises only by a factor of 1.5.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md) defines
> every term and symbol used anywhere in this repository.

## 1. What it is, and which observable carries it

Rubidium atoms collide with rubidium atoms, each collision interrupts the
radiating phase, and the line acquires a Lorentzian width proportional to the
perturber density. That proportionality is the impact-theory result of
[Baranger 1958](../lit/baranger1958.md), valid when collisions are weak and well
separated, and it is what makes a single coefficient meaningful:
$\gamma_{\rm coll} = \beta_{\rm self} N$, linear in $N$.

The observable is the line width against temperature, since temperature sets
the density through the vapour pressure curve. That is the whole lever, and it
has a consequence worth stating at the top: the collisional width shares the
width channel with the laser width, the transit width and the natural width,
and this experiment cannot separate them by shape. It separates them by how
they respond to temperature, which is why the four-temperature ladder is the
construction of record.

The quantity to keep separate from $\beta_{\rm self}$ is $\gamma_{\rm coll}$
itself. The first is a coefficient, atomic and transferable. The second is a
fitted width at one condition, and it can be nonzero for reasons that have
nothing to do with collisions, which is exactly what this dataset finds.

## 2. What the literature has achieved

Rubidium self-broadening has been measured on the neighbouring rungs of the
same ladder but not on this one. Values appear exactly as published, in the
authors' own units, because the conventions differ and one of them is not
stated at all.

**Direct comparators**, self-broadening of an nS state in rubidium by
rubidium.

| reference | value as published | state | convention |
|---|---|---|---|
| [Zameroski 2014](../lit/zameroski2014.md) | $129 \pm 11$ kHz/mTorr | 85Rb 5S to 7S, cascade fluorescence | FWHM, stated |
| [Cao 2025](../lit/cao2025.md) | $40 \pm 0.54$ kHz/mTorr | 85Rb 5S to 5D 3/2, cascade fluorescence | FWHM, stated |
| [Wang 2025](../lit/wang2025.md) | $0.32 \pm 0.01$ MHz/mTorr | 85Rb 5S to 7S, five-channel fluorescence | **Not stated** |

Zameroski 2014 is the closest, being the only measured self-broadening rate for
an nS state in rubidium, and it converts to about $5.39 \pm 0.46$ kHz per
1e12 per cubic centimetre in this repository's units. **The 6S entry between the 5D
and 7S rungs is the missing one, and it is the entry this experiment addresses.**

Two convention warnings travel with that table and are not incidental. Wang
2025 states no FWHM or HWHM convention anywhere, so any comparison with it
carries a factor-of-two ambiguity, and its own note flags this. And Cao 2025
infers density from temperature rather than measuring it, which is the same
systematic this experiment carries.

**Physical analogues.** [Rahaman 2022](../lit/rahaman2022.md) measured Cs 6S to
7D 3/2 self-broadening at 99(6) kHz/mTorr, about 4.18 kHz per $10^{12}$
per cubic centimetre, in a convention identical to the one used here, and did so with an
absolute frequency axis. [Weller 2011](../lit/weller2011.md) measured the Rb D1
resonant self-broadening at 69 kHz per 1e12 per cubic centimetre, which is a ceiling
rather than an estimate: a resonant dipole channel exists there and does not
exist for an S-to-S transition, so the S-to-S coefficient must be far smaller.
[Sautenkov 2026](../lit/sautenkov2026.md) is the resonance-broadened case this
line definitionally is not.

**Theory.** [Lewis 1980](../lit/lewis1980.md) supplies the van der Waals
cross-section formula and the Lindholm-Foley prefactor that
[`rb5s6s/vanderwaals.py`](../../rb5s6s/vanderwaals.py) specialises,
and [Bala 2026](../lit/bala2026.md) supports the expectation that the two
isotopes share a coefficient, the reduced-mass difference being about one per
cent.

## 3. What this dataset establishes

| construction | value | status | source |
|---|---|---|---|
| Four-temperature width slope, pooled, dof 2 | $\lt 0.0249$ MHz per 1e12 per cubic centimetre | BOUND | [`beta_self_probe.csv`](../../results/beta_self_probe.csv) |
| Four-temperature width slope, per peak | $\lt 0.0239$ to $\lt 0.0411$ | BOUND | `beta_self_probe.csv` |
| Model-independent per-peak central values | 0.0131 to 0.0181 | PRELIM | [`beta_self.csv`](../../results/beta_self.csv) |
| Hierarchical joint fit, cooling sweep | $0.0534 \pm 0.0043$ (85Rb) | BOUND | [`global_fit.csv`](../../results/global_fit.csv) |
| Same fit with the 130 C anchor folded in | 0.0198 (85Rb), 0.0219 (87Rb) | BOUND | [`lever_crosscheck.csv`](../../results/lever_crosscheck.csv) |
| $\kappa$ and $\beta_{\rm self}$ both free | 0.0183, interval 0.0177 to 0.0187 | PRELIM | [`global_dataset_fit.csv`](../../results/global_dataset_fit.csv) |

**The measurement that turns the value into a bound.** The fitted collisional
width across the temperature ladder is 0.404, 0.390, 0.444 and 0.594 MHz at 70,
90, 110 and 130 C, against densities of 0.56, 2.45, 9.10 and 29.43 in units of
1e12 per cubic centimetre. That is a factor of 1.47 in width across a factor of 52.5
in density. A genuine collisional width would rise linearly. **A width that
rises by 1.5 while the density rises by 52 is a floor with a small collisional
component on top, not a resolved collision rate**, so the quantity the data
support is an upper limit and that is what the record reports.

**The hierarchical construction is a cross-check and is not settled.** Its
central value of 0.0534 moves to 0.0198 and 0.0219 when the 130 C anchor
extends the density lever from 16 to 52. A cross-check estimator that moves by
a factor of 2.6 when one condition is added is reporting its own model
dependence, which is precisely why the model-independent slope is the headline
and this is not.

## 4. Why the experiment cannot do better

**Experimental: the density is inferred, not measured.** Density comes from the
cell temperature through a vapour-pressure curve, so every value above inherits
a scale uncertainty that no amount of spectroscopy removes. The committed
numbers carry it explicitly as a separate systematic column, and it is the
reason a `bound95_nscale` variant exists beside every `bound95`.

**Experimental: the temperature lever is short and one-ended.** Four
temperatures spanning a factor of 52 in density sounds generous and is not,
because the width response is 1.5 over that span. Most of the density lever
buys almost no width.

**Model form, and as of 2026-08-21 the binding one.** The laser kernel was
treated as a choice between a Gaussian and a Lorentzian. Freeing both
components at once, which the shipped model can now do, is preferred at every
peak by a nested likelihood ratio, and it moves $\beta_\text{self}$ by 42 to
66 per cent. The uncertainty this contributes,
$U_\text{kernel} = 0.004530$ MHz per density unit, exceeds the statistical
error $U_\text{statistical} = 0.001398$ by a factor
$R_\text{kernel} = 3.24$ (`results/kernel_k3.csv`).

**So the answer to "why can the experiment not do better" has changed.** It is
no longer the density lever or the statistics. **More repetitions of the
current construction do not improve this coefficient**, because the kernel
systematic is three times larger than the thing more data would shrink. What
improves it is an independent constraint on the laser kernel, and
`results/kernel_k7.csv` ranks the routes. Note also what the kernel result does
not settle: a non-Gaussian homogeneous component is present, and attributing it
to the laser is a separate arrow that no measurement yet taken carries.

**Statistical: the width degeneracy.** The collisional width and the laser
width both broaden the same line, and the sensitivity matrix at one condition
has a condition number of 345. Simulated on a bright synthetic condition
with signal-dependent noise (`scripts/run_width_pinning.py`), freeing both
recovers the collisional width with a scatter of 0.0073 MHz where fixing the
laser width recovers it with 0.0022 MHz, a ratio of $3.18 \pm 0.20$ across
nine seeds. That ratio is one condition's value of $1/\sqrt{1-\rho^2}$, which
runs from 2.29 at the record's median correlation to 2.97 at the simulated
condition's own $-0.9417$. **An independent laser-width diagnostic is worth more to this
quantity than any improvement to the fitting**, and the computation with its
construction is discussed in
[identifiability](../wiki/identifiability.md).

**Model: what the floor actually is.** The 0.4 MHz that does not scale with
density is unattributed. It could be residual laser width, transit, or
lineshape misfit, and the record does not resolve which. Until it is
attributed, the collisional coefficient is being read as the slope of a line
whose intercept is not understood.

## 5. Three levels of improvement

### An improved bound

**What it delivers.** A tighter upper limit, by extending the density lever
upward and by pinning the floor, without yet resolving a collision rate.

**Recipe.** Temperatures to 150 and 170 C in the same session as the existing
ladder, which raises the density lever by roughly another factor of five, with
an absorption channel on the same cell so that density is MEASURED rather than
inferred. Same powers, same detection, additional thermocouple readout for the
gradient. This is [plan chapter 5](../plan/05_width-collision-amplitude.md).

**Success criterion.** Precision: the bound tightened by the factor the
extended lever supports, now computed at the committed coverage construction:
a factor 3.5 at 150 C and 10 at 170 C on the median null bound, under
assumptions stated as optimistic in
[the projection note](../notes/extended_lever_and_skew_projection.md).
Identifiability: unchanged at this level. Coverage: the existing profile
construction. Convergence: single-condition fits, not at issue. Model validity:
the width against density checked for linearity across the extended span rather
than assumed. Calibration: the absorption channel supplies the density scale,
which is the point of the level.

**Minimum viable version.** Two additional temperatures with the absorption
channel, in one session, alongside the existing four. Six points test linearity
where four constrain a slope.

**Kill criterion.** If blackbody-driven population redistribution or thermal
gradients broaden the line at 150 and 170 C, the added points are not measuring
collisions and the lever is not extendable in this cell. That is a real
possibility and it is why the two points come with the gradient readout.

### A measurement

**What it delivers.** A resolved collision rate rather than a limit, requiring
that the width be shown to rise linearly with density above the floor.

**Recipe.** The extended temperature ladder above, plus an independent
laser-width calibration so that the largest competing width is externally
known rather than jointly fitted. The laser width is measured by a delayed
self-heterodyne or cavity-referenced diagnostic outside the cell.

**Success criterion.** Precision: the collisional width resolved at better than
three standard deviations at the highest density. Identifiability: the
sigma-gamma ridge broken by external calibration, the factor of 1.7 computed in
section 4 realised. Coverage: injection and recovery at the measured noise law.
Convergence: not at issue for per-condition fits. Model validity: the floor
attributed, so that the intercept of the width-against-density line has a name.
Calibration: density measured by absorption, laser width measured externally.

**Minimum viable version.** The existing four temperatures plus one external
laser-width measurement. That alone tests whether the ridge is what limits the
current bound, before any new thermal work is committed.

**Kill criterion.** If the externally measured laser width does not collapse the
ridge, the limitation was never the degeneracy, and the plan's own claim that it
was must be withdrawn rather than restated.

### A competitive measurement

**What it delivers.** The 6S rung of the rubidium self-broadening ladder at a
precision comparable with the rungs above and below it, which means about eight
per cent, the precision [Zameroski 2014](../lit/zameroski2014.md) reached on 7S.

**Recipe.** The measurement level above, plus the stated FWHM convention, plus
both isotopes measured in the same session so that the isotope expectation of
[Bala 2026](../lit/bala2026.md) is tested rather than assumed, plus enough
repeats at each condition that the block scatter rather than the fit error sets
the uncertainty.

**Success criterion.** Precision: comparable with the 8 per cent of the 7S
entry. Identifiability: as above. Coverage: verified. Convergence: verified.
Model validity: linearity across the full density span demonstrated, not
assumed from impact theory. Calibration: an absolute density scale, which is
the part that separates a competitive measurement from a good one, since two of
the three published comparators infer density from temperature exactly as this
experiment currently does.

**Minimum viable version.** There is none. A competitive measurement is the
full construction, and saying otherwise would be the kind of claim this page
exists to avoid.

**What is calculation required.** The uncertainty reachable with the extended
lever and an external laser width together. The lever alone is computed in
[the projection note](../notes/extended_lever_and_skew_projection.md), and the
combined configuration is not.

## 6. What goes wrong as sensitivity improves

| knob | what it buys | what it costs |
|---|---|---|
| higher temperature | density, and the whole lever | blackbody redistribution, thermal gradients across the cell, a changing pedestal, and a vapour-pressure curve extrapolated further from where it is trusted |
| more power | signal | saturation and the light shift, which broaden the same width channel with a different power law but the same sign |
| more repeats | block scatter as the square root | drift within the block |
| an absorption channel | a measured density, which is the single largest gain | optical access, an additional alignment, and a new systematic in the absorption path itself |

The knob that matters most here is not on the list of things that raise
sensitivity. It is the external laser-width measurement, which raises nothing
and instead removes a competitor, and that asymmetry is the general lesson of
[identifiability](../wiki/identifiability.md).

## 7. What each level would make answerable

**Improved bound.** Whether the 0.4 MHz floor is collisional at all, which the
extended lever answers by whether the width finally begins to track density.

**Measurement.** The 6S entry in the rubidium ladder, which currently has 5D
and 7S measured and 6S missing, and with it a test of the van der Waals route
that predicts it.

**Competitive measurement.** Whether the impact-theory scaling holds across the
alkali nS series, which needs three rungs at comparable precision and currently
has two. The technique, a temperature ladder with a measured density scale and
an externally calibrated laser width, transfers to any thermal-cell line.

## 8. What remains impossible

**Not measurable with this architecture.** An absolute density scale better
than the absorption channel supports. Every published comparator except
Rahaman 2022 has the same limit, which is why the field's numbers are hard to
compare and why the convention warnings in section 2 matter more than they look.

**Not separable in principle here.** The floor's composition, if the floor is a
lineshape misfit rather than a physical width. A misfit that mimics a
Lorentzian at every temperature is indistinguishable from a
temperature-independent collision channel in this observable, and only a better
profile, not more data, separates them. That is the same conclusion the band
excess reaches from the residual side.

**Not yet measured, which is different.** The isotope difference. It is
expected to be about one per cent and neither the current data nor any planned
level resolves it, but nothing in the architecture forbids it.

## See also

- [The AC-Stark light shift](ac-stark-light-shift.md), which shares the width
  channel with this quantity
- [The campaign](campaign.md), for the session that serves both
- [Self-broadening](../wiki/self-broadening.md) for the physics
- [Identifiability](../wiki/identifiability.md) for the ridge and what breaking
  it is worth
- [Plan chapter 5](../plan/05_width-collision-amplitude.md) for the blocks
