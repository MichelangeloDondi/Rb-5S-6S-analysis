# Collisional self-broadening

*[quantities index](README.md) · headline parameter*

How much self-broadening does this experiment resolve independently of the laser width and of the density scale? The quantity is $\beta_{\rm self}$, the coefficient relating the collisional Lorentzian width to the rubidium number density, in MHz per 1e12 per cubic centimetre, so that $\gamma_{\rm coll} = \beta_{\rm self} N$. This page builds on the committed width fits across four temperatures. No new fitting. It sets out the bound in each construction, the reason the fitted collisional width is a floor rather than a resolved effect, the position of that bound against the measured rungs above and below this line, and three levels of improvement with their recipes. Not covered here: the question is the physics of the broadening mechanism, which is [self-broadening](../wiki/self-broadening.md), or how the width channel is shared with the light shift, which is [the AC-Stark dossier](ac-stark-light-shift.md).
**Where it stands.** A bound.

The pooled four-temperature construction gives
$\beta_{\rm self} \lt$ [0.026](../../results/beta_self_probe.csv "ref:beta_self_probe:pooled_slope::bound95_nscale") MHz per 1e12 per cubic centimetre, which is the
figure the rest of the record quotes, and the reason it is a
bound is measured rather than assumed: across a factor of 48.1 (Alcock) in density the
fitted collisional width rises only by a factor of 1.5. Without the
vapour-pressure scale systematic the same construction gives [0.0205](../../results/beta_self_probe.csv "ref:beta_self_probe:pooled_slope::bound95"), and
section 4 says why that column is not the one to quote.

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## 1. Definition and observable

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

## 2. Prior achievements in the literature

Rubidium self-broadening has been measured on the neighbouring rungs of the
same ladder but not on this one. Values appear exactly as published, in the
authors' own units, because the conventions differ and one of them is not
stated at all.

Direct comparators, self-broadening of an nS state in rubidium by
rubidium.

| reference | value as published | state | convention |
|---|---|---|---|
| [Zameroski 2014](../lit/zameroski2014.md) | $129 \pm 13$ kHz/mTorr | 85Rb 5S to 7S, cascade fluorescence | FWHM, stated |
| [Cao 2025](../lit/cao2025.md) | $40 \pm 0.54$ kHz/mTorr | 85Rb 5S to 5D 3/2, cascade fluorescence | FWHM, stated |
| [Wang 2025](../lit/wang2025.md) | $0.32 \pm 0.01$ MHz/mTorr | 85Rb 5S to 7S, five-channel fluorescence | **Not stated** |

Zameroski 2014 is the closest, being the only measured self-broadening rate for
an nS state in rubidium, and it converts to about [5.62](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_7s:measured") $\pm$ 0.45 kHz per
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

## 3. Results established by this dataset
| construction | value | status | source |
|---|---|---|---|
| Four-temperature width slope, pooled, dof 2 | $\lt$ [0.026](../../results/beta_self_probe.csv "ref:beta_self_probe:pooled_slope::bound95_nscale") MHz per 1e12 per cubic centimetre, the headline; [0.0205](../../results/beta_self_probe.csv "ref:beta_self_probe:pooled_slope::bound95") before the density-scale systematic | BOUND | [`beta_self_probe.csv`](../../results/beta_self_probe.csv) |
| Four-temperature width slope, per peak | $\lt 0.0246$ to $\lt 0.0423$ | BOUND | `beta_self_probe.csv` |
| Model-independent per-peak central values | 0.0043 to 0.0069 | PRELIM | [`beta_self.csv`](../../results/beta_self.csv) |
| Hierarchical joint fit, cooling sweep | [0.0086](../../results/global_fit.csv "ref:global_fit:beta_self:85Rb") $\pm$ [0.0026](../../results/global_fit.csv "ref:global_fit:beta_self:85Rb:err") (85Rb) | BOUND | [`global_fit.csv`](../../results/global_fit.csv) |
| Same fit with the 130 C anchor folded in | [0.0058](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_lever_probe_130:85Rb") (85Rb), [0.0076](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_lever_probe_130:87Rb") (87Rb) | BOUND | [`lever_crosscheck.csv`](../../results/lever_crosscheck.csv) |
| $\kappa$ and $\beta_{\rm self}$ both free | 0.0043, interval 0.0041 to 0.0046 | PRELIM | [`global_dataset_fit.csv`](../../results/global_dataset_fit.csv) |

**The measurement that turns the value into a bound.** The fitted collisional
width across the temperature ladder is 0.075, 0.057, 0.088 and 0.223 MHz at 70,
90, 110 and 130 C, against densities of 0.74, 3.11, 11.23 and 35.59 (Alcock) in units of
1e12 per cubic centimetre. That is a factor of [2.99](../../results/lever_crosscheck.csv "ref:lever_crosscheck:gamma_rise_factor:70to130") in width across a factor of 48.1
in density. A genuine collisional width would rise linearly. **A width that
rises by 3 while the density rises by 48 is a floor with a small collisional
component on top, not a resolved collision rate**, so the quantity the data
support is an upper limit and that is what the record reports.

The hierarchical construction is a cross-check and is not settled. Its
central values of 0.0086 and 0.0093 move to 0.0058 and 0.0076 when the 130 C anchor
extends the density lever from 15 to 48 (Alcock), a third and a fifth lower, and
dropping the 110 C condition moves the first by
[0.0382](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_loo_temp:85Rb"), more than four times its value.
A cross-check estimator that moves this much when one condition is added or removed is
reporting its own model dependence, which is precisely why the model-independent
slope is the headline and this is not.

## 4. Limits of the present experiment

Experimental: the density is inferred, not measured. Density comes from the
cell temperature through a vapour-pressure curve, so every value above inherits
a scale uncertainty that no amount of spectroscopy removes. The committed
numbers carry it explicitly as a separate systematic column, and it is the
reason a `bound95_nscale` variant exists beside every `bound95`.

Experimental: the temperature lever is short and one-ended. Four
temperatures spanning a factor of 48 in density sounds generous and is not,
because the width response is 3 over that span. Most of the density lever
buys almost no width.

**Model form, quantified 2026-08-21.** The laser kernel was
treated as a choice between a Gaussian and a Lorentzian. Freeing both
components at once, which the shipped model can now do, is preferred at three
of the four peaks by a nested likelihood ratio, and it moves $\beta_\text{self}$ by 5 to
48 per cent. The uncertainty this contributes,
$U_\text{kernel} = 0.000709$ MHz per density unit, sits below the statistical
error $U_\text{statistical} =$ [0.001165](../../results/kernel_k3.csv "ref:kernel_k3:all:U_statistical"), a factor
$R_\text{kernel} = 0.61$ (`results/kernel_k3.csv`).

And the hierarchical arm had not carried it until 2026-09-11. The paragraph
above is a per-peak result, from `kernel_k3.csv`, which fits the extra component
free in each peak. The hierarchical fit that `docs/RESULTS.md` heads its table
with publishes a model-form bar built from a grid of transit form and sharing
only, and holds the component at zero. Set instead to the weighted mean that
same file fits, 0.078 MHz, the hierarchical coefficient reads
[0.0019](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_grid_exp_per_T_gamma_l0.078:85Rb") against
[0.0086](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_grid_exp_per_T:85Rb"), a move of
[0.0067](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_kernel:85Rb"), at the same reduced $\chi^2$
of 0.851, so at the calculated waist the width fit prefers neither end of the
axis. `beta_err_kernel` carries the axis in that file, beside `beta_err_transit`
and `beta_err_sharing`, and outside `beta_err_modelform`, whose definition over
three cells is left where a reader found it.

At this waist the transit's form is
the larger axis by far: the Voigt transit reads
[0.0548](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_grid_gaussian_per_T:85Rb") where the Lehmann
cusp reads 0.0086, a `beta_err_transit` of
[0.0462](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_transit:85Rb"), about seven times the
kernel axis and eighteen times the statistical error.

And the reason the kernel axis moves the coefficient is the shape of the fit,
not a wide bar on a good number. The homogeneous width is
$\Gamma_\text{nat} + \beta N + \gamma_l$. Holding $\gamma_l$ at zero forces the
density line through the origin against a floor this same file reports:
`gamma_coll_mean_vs_T` reads
[0.075](../../results/lever_crosscheck.csv "ref:lever_crosscheck:gamma_coll_mean_vs_T:70C") MHz at the lowest
density, where $\beta N$ at the fitted coefficient would be about 0.006. A line
through the origin fitted to a floor $c$ has slope offset by
$c \sum wN / \sum wN^2$, so the fitted coefficient is *linear* in $\gamma_l$,
and the two committed points put that slope at $-0.086$ per MHz on the cooling
ladder.

Three things follow. The floor and the fitted component are the same
quantity by two constructions, 0.075 MHz from the lowest-density width against
the 0.078 the kernel chain fits. The lever dependence that makes this
coefficient a BOUND, the width rising only
[2.99](../../results/lever_crosscheck.csv "ref:lever_crosscheck:gamma_rise_factor:70to130")-fold across a 48.1-fold density span,
is that floor forced through the origin, so modelling it removes the lever
dependence instead of explaining it. And the van der Waals prediction is crossed
inside the span the kernel chain fits: on the straight line through the two
committed points it falls near $\gamma_l = 0.06$ MHz.

**What it leaves open, and the first draft of this section got it backwards.**
That draft said that if the extra width were atomic the coefficient would be
smaller. **Attribution does not enter**: a density-independent width lowers the
fitted slope whatever its origin, and the kernel chain defines this component as
density-independent. What attribution decides is whether the floor is a property
of the apparatus or of the vapour, which is the K5 transfer triangle's question
and is not settled here. The central value is left where a reader found it for
that reason and for no other.

Owed before any of this is quoted further. The per-peak coefficients at the
fitted component have no committed producer: they exist in this repository's
private correction record and in a replay beside it, not in `results/`. The
hierarchical one is the committed row `beta_grid_exp_per_T_gamma_l0.078`. The
van der Waals prediction of [3.50](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_6s:anchored")([0.37](../../results/beta_self_theory.csv "ref:beta_self_theory:beta_self_6s:anchored:err")) kHz lies between the
two committed grid points, and locating its crossing needs a third grid point
and not a line drawn through two.

So the answer to "why can the experiment not do better" has changed. It is
no longer the density lever or the statistics. **More repetitions of the
current construction do not improve this coefficient**, because its model-form
systematic, the transit's form above all, is about eighteen times the
statistical error that more data would shrink, and the kernel axis alone is two
and a half times it. What improves it is an independent constraint on the
transit and laser kernels, and
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

Model: what the floor actually is. The 0.4 MHz that does not scale with
density is unattributed. It could be residual laser width, transit, or
lineshape misfit, and the record does not resolve which. Until it is
attributed, the collisional coefficient is being read as the slope of a line
whose intercept is not understood.

Model: the temperature arm moves three terms together. Across the arm's 70 to
130 C the self-broadening signal is [122.0](../../results/ladder_terms.csv "ref:ladder_terms:signal:rb_self_broadening") kHz on the central density law,
while the transit's own drift over the same arm is [105.4](../../results/ladder_terms.csv "ref:ladder_terms:transit_drift:band_high_45.00um_rb87") to
[118.6](../../results/ladder_terms.csv "ref:ladder_terms:transit_drift:band_low_40.00um_rb87") kHz across the 40 to 45 um band, [0.86](../../results/ladder_terms.csv "ref:ladder_terms:transit_over_signal:band_high_45.00um_rb87") to
[0.97](../../results/ladder_terms.csv "ref:ladder_terms:transit_over_signal:band_low_40.00um_rb87") of the signal and with its sign, because the transit width
rises as the square root of the temperature.

A sealed cell's permeated gas adds at
most [6.6](../../results/ladder_terms.csv "ref:ladder_terms:permeated_drift:fixed_density_hard_sphere") kHz more with the same sign: on the arm's timescale of
hours the cell holds a fixed amount, so that width rises with temperature too.
A slope of total width against density would return about [1.97](../../results/ladder_terms.csv "ref:ladder_terms:naive_slope_factor:central_fixed_density_hard_sphere") times
beta_self. The record does not read beta_self from such a slope: it fits the
composite model, in which the transit is a term with its own temperature law,
so the result is conditional on that term and through it on the waist. The
separation needs a lever with a different temperature exponent: power, waist,
or a platform without the transit (`results/ladder_terms.csv`).

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

## 6. Failure modes at higher sensitivity
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

## 7. Questions answerable at each level

**Improved bound.** Whether the 0.4 MHz floor is collisional at all, which the
extended lever answers by whether the width finally begins to track density.

**Measurement.** The 6S entry in the rubidium ladder, which currently has 5D
and 7S measured and 6S missing, and with it a test of the van der Waals route
that predicts it.

**Competitive measurement.** Whether the impact-theory scaling holds across the
alkali nS series, which needs three rungs at comparable precision and currently
has two. The technique, a temperature ladder with a measured density scale and
an externally calibrated laser width, transfers to any thermal-cell line.

## 8. Questions out of reach

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

Not yet measured, which is different. The isotope difference. It is
expected to be about one per cent and neither the current data nor any planned
level resolves it, but nothing in the architecture forbids it.

## Related pages
- [The AC-Stark light shift](ac-stark-light-shift.md), which shares the width
  channel with this quantity
- [The campaign](campaign.md), for the session that serves both
- [Self-broadening](../wiki/self-broadening.md) for the physics
- [Identifiability](../wiki/identifiability.md) for the ridge and what breaking
  it is worth
- [Plan chapter 5](../plan/05_width-collision-amplitude.md) for the blocks
