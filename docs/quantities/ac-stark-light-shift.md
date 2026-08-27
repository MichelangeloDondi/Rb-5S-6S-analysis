# The AC-Stark light shift

*[quantities index](README.md) · headline parameter*

**The question.** What light shift can be separated from the other mechanisms
that share its power signature? The quantity is $\kappa$, relating the on-axis
shift to the drive power in MHz per watt, and $S_0 = \kappa P$, the shift at a
stated power, both on the transition axis.
**Takes.** The committed fits and their profile likelihoods. No new fitting.
**Gives.** The bound in every construction that produced one, the four reasons
it is a bound rather than a value, and three defined levels of improvement with
their bench recipes.
**Skip if.** The question is how the shift distorts a line, which is
[the AC-Stark shift](../wiki/ac-stark-shift.md), or whether the joint
constructions may be compared with each other, which is
[chapter 8](../big_picture/08_when-a-joint-fit-is-legitimate.md).

**Where it stands.** A bound, not a measurement, in every construction the
record carries, and the constructions span $\kappa \lt 0.944$ to
$\kappa \lt 2.811$ MHz/W depending on which data and which channel are used.
No single number is quotable without its construction, and whether the joint
three-session construction reproduces remains an open question, so
section 3's table with its status column is the citable object, not any one
row of it.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md) defines
> every term and symbol. The physics of the effect is
> [the AC-Stark shift](../wiki/ac-stark-shift.md), and the reason a bound is
> reported rather than a value is
> [identifiability](../wiki/identifiability.md).

## 1. What it is, and which observable carries it

The 993 nm drive shifts the 5S and 6S levels by different amounts, so the
two-photon resonance moves. Because the beam has a spatial intensity profile
and the transition is two-photon, atoms at different radii see different
shifts weighted by $I^2$, and the line does not simply translate. It acquires
a one-sided distortion whose shape is the intensity distribution mapped through
the differential polarizability. That mapping is the subject of
[methods chapter 3](../methods/03_the_ac_stark_ramp.md), and it is the reason
the shift is a lineshape feature rather than only a frequency offset.

Three observables in this archive contain information about $\kappa$, and they
are not equally sensitive. **The width** grows because the shift distribution
broadens the line. **The centre** moves because the distribution has a nonzero
mean. **The skew** appears because the distribution is one-sided. The record
uses the width, and the reason the width is the weakest of the three is the
subject of section 4.

The quantity to keep separate from $\kappa$ is the differential polarizability
$\Delta\alpha$, which is atomic and fixed, where $\kappa$ additionally carries
the geometry: the waist that sets the intensity and the retroreflection ratio
that sets the standing-wave contrast. A measurement of $\kappa$ is a
measurement of $\Delta\alpha$ only to the accuracy of that geometry, which is
section 4's second theme.

## 2. What the literature has achieved

Three classes of comparator, assembled from the repository's own
[literature notes](../LITERATURE_INDEX.md). Values appear exactly as
published, in the units their authors used, because the conventions differ and
converting them silently is how comparisons stop meaning anything.

**Direct comparators**, the same measurement on the same or a sister line.

| reference | value as published | system | why it is comparable |
|---|---|---|---|
| [Orson 2021](../lit/orson2021.md) | no shift resolved at 6 MHz spectral resolution, and computes $\alpha_{56} = -1093$ a.u. | Rb 5S-6S at 993 nm, this line | The only prior work on this transition, and its null is the standing prior result on this channel. Its computed differential polarizability is not the value this repository uses. In this record's sign convention that value is $+1093$, and an independent sum-over-states recompute gives $-1145$, the same quantity by the same definition, with the opposite sign and magnitudes agreeing to about five per cent. The record's own value became the package default by a decision on the theory, which is not a measurement, and the published one is kept named beside it as `DELTA_ALPHA_AU_ORSON2021`. Every committed bound is sign-immune; the fixed-lock pull direction is what would settle it. See [THEORY_NOTE](../THEORY_NOTE.md) |
| [Lee 2010](../lit/lee2010.md) | -7.25(45) Hz per mW per square millimetre, against theory $-6.58$ and a prior $-6.13(1.25)$ | Cs 6S-8S two-photon, hot cell | The closest published analogue: an nS to n'S alkali two-photon line with intensity and density scanned independently |
| [Fendel 2007](../lit/fendel2007.md) | $-0.21$ Hz per mW per square centimetre against average, not peak, intensity | Cs 6S-8S two-photon, comb-driven | The same experiment one element to the left. It engineered the spatial distribution away with an unfocused 0.72 mm waist, which is the effect measured here |

**Physical analogues**, the same mechanism in a different system.
[Stalnaker 2006](../lit/stalnaker2006.md) extracted a polarizability from an
asymmetric line produced by a spatially varying AC-Stark shift in a Yb standing
wave, quoting $-0.312(34)$ Hz per (V/cm) squared, and is the nearest prior art for the
method rather than for the number, since it is one-photon and therefore weights
the intensity linearly rather than quadratically.
[Slepkov 2010](../lit/slepkov2010.md) is the same atom with the same mechanism
in a guided mode. [Wall 2014](../lit/wall2014.md) shows the converging-beam
version of the same distortion in He.

**Scale references.** [Quirk 2024](../lit/quirk2024.md) measured the Cs
6S-7S differential static polarizability to four significant figures, 5807
a0 cubed, which is the validation target for the analogous Rb 5S-6S quantity,
though it is DC where this is AC.

**The counterpoint worth stating, because it defines the gap this experiment
sits in.** [Yudin 2020](../lit/yudin2020.md),
[Li 2024](../lit/li2024b.md) and [Gerginov 2018](../lit/gerginov2018.md) all
treat the light shift as one scalar to be suppressed, and the words
distribution, waist and inhomogeneous appear nowhere in the last of them. The
distinction is not that those works are wrong. It is that a programme
suppressing a shift and a programme reading a distribution from it need
different things from the apparatus, and the second has almost no measured
precedent on an alkali nS to n'S line.

## 3. What this dataset establishes

Every row is one construction. They are not alternative renderings of one
number, and quoting one where another applies is the error this layer exists to
prevent.

| construction | $\kappa$ bound | $S_0$ at 225 mW | status | source |
|---|---|---|---|---|
| Full archive, power and temperature ladders | $\lt$ [0.944](../../results/full_dataset_fit.csv "ref:full_dataset_fit:kappa_ub95:primary") MHz/W | $\lt 0.212$ MHz | BOUND | [`full_dataset_fit.csv`](../../results/full_dataset_fit.csv) |
| Joint three-session profile, the quoted construction | $\lt$ [1.147](../../results/stark_joint.csv "ref:stark_joint:kappa_ub95:primary") MHz/W | $\lt$ [0.258](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_ub95:primary") MHz | BOUND | [`stark_joint.csv`](../../results/stark_joint.csv) |
| Joint, with the red-side wing marginalised | $\lt$ [1.066](../../results/stark_joint.csv "ref:stark_joint:kappa_ub95_wing:robustness") MHz/W | | BOUND, conditional | `stark_joint.csv` |
| Joint, dropping the 4192 peak and with it the whole pilot session | $\lt$ [1.626](../../results/stark_joint.csv "ref:stark_joint:kappa_ub95_drop4192:robustness") MHz/W | $\lt 0.366$ MHz | BOUND | `stark_joint.csv` |
| $\kappa$ and $\beta_{\rm self}$ both free, no prior | $\lt 0.963$ MHz/W | $\lt 0.217$ MHz | PRELIM | [`global_dataset_fit.csv`](../../results/global_dataset_fit.csv) |
| Width channel alone | $\lt 2.811$ MHz/W | $\lt 0.632$ MHz | BOUND | [`stark_sweep.csv`](../../results/stark_sweep.csv) |
| Centre channel alone | $\lt 8.653$ MHz/W | | BOUND | [`centre_stark.csv`](../../results/centre_stark.csv) |

**The prediction, for comparison rather than as a result.** $\kappa$ is
predicted at [1.545](../../results/stark_joint.csv "ref:stark_joint:kappa_pred:prediction") MHz/W, giving $S_0 =$ [0.348](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_pred:prediction") MHz at 225 mW, a waist of 64 µm and a retro ratio of 0.94. Those two cells
were computed under the earlier $|\Delta\alpha| = 1093$ default and have not
been regenerated since this record pinned its own 1145, which raises them by
the ratio 1145/1093, about 4.8 per cent.
 The file `results/stark_sweep.csv` carries the
current shift, 0.364 MHz. The coefficient 1.618 MHz/W is that divided by the
225 mW drive and has no committed row of its own, and its producer is the cheap one. The bounds therefore sit below the prediction,
which is the interesting feature of the table and is discussed in section 4.

**Two things the table does not say, stated here so that it cannot be read as
saying them.** No construction reports a detection: the joint profile's minimum
sits at $\kappa = 0.25$ MHz/W with $\Delta\chi^2 = 0.12$ at $\kappa = 0$, which
is no preference at all. And the pooled three-session construction is **not
currently reproducible**: its passes span a factor of 2.1 and a second local
optimum roughly 21,000 in $\chi^2$ above the best has been confirmed, so the
pooled and campaign-only bounds cannot be compared at the size of their
difference. That is worked out in
[big picture chapter 8](../big_picture/08_when-a-joint-fit-is-legitimate.md),
which is the page to read before quoting any of these numbers against each
other.

### The retired significance, and the two supports that did not hold

Every bound in the primary constructions sits below the prediction, and until
2026-08-27 this record called that an exclusion at 95 per cent, at roughly
the two-sigma level. **On the primary three-session fit both halves hold**,
and what the sentence lacked is two qualifications instead of a correction.
The record spent one night discovering that, offering five wider retractions
and withdrawing all five. They are listed at the end of this section.

**What stands.** The 95 per cent one-sided limit on the full three-session
fit, $\kappa \lt 1.147$ MHz/W, lies below every point of the predicted
envelope, which runs 1.404 to 1.760 over the stated waist and retro band. So
the prediction is excluded at 95 per cent at every geometry in that band.

**Qualification one: the strength is a range and not a number.**
$\Delta\chi^2$ runs 4.1 at the envelope's lower vertex to 5.7 at its upper,
2.0 to 2.4 $\sigma$ under Wilks, and the same profile read as a posterior
puts the computed 1145 a.u. in the upper 3 per cent, about 1.8 $\sigma$. A
single calibrated two-sigma is what the record withdraws, not the existence
of a significance. The envelope's own half-width is a two-vertex scan and
must never be used as the denominator of one.

**Qualification two, and it is the larger: on this construction the exclusion
does not survive leaving one peak out.** At the predicted $\kappa$ the committed
`lopo_dchi2_pred` rows read 8.75, 2.27, 1.12 and 0.61 for 993.4121, 993.4192,
993.4154 and 993.4207 nm against a 2.706 threshold. **No count of arms is
quoted here.** Each arm is a fit with one peak removed against its own
minimum, so the arms do not share the full profile's derivative. Carrying them to 1.618 needs no curvature model. Each arm's own committed pair, at 1.545 and at 2.62, brackets it between its value at 1.545 and that value plus its own secant slope across the gap, giving 4121 in [8.75, 10.05], 4192 in [2.27, 2.77], 4154 in [1.12, 1.35] and 4207 in [0.61, 0.86]. So 4121 clears at both ends, 4154 and 4207 fail at both ends, and 4192 straddles the threshold and is not callable. The rows are
evaluated at the pre-adjudication predicted $\kappa$ of 1.545 and not at
this record's own 1.618, which is why the bracket above is quoted instead of
a count. The record used to
read those four as "all positive and similar" over a span of fourteen. Note
too that drop-4192 is called the most conservative subset only because
`run_stark_joint` gives that one drop a fine $\kappa$ grid, so it is the only
arm whose bound can be read off at all.

**An observation that looks like a third reason and is not.** The drop-4192
arm of the table above, $\kappa \lt 1.626$, lands inside the predicted
envelope and not below it. It cannot carry the retraction: its margin
against the predicted point is half a per cent, several times smaller than
the profile's own committed numerical scatter, and `RESULTS.md` C3f reads
this margin from the primary construction alone and calls the subset columns
a robustness range and not separately quotable limits. An earlier draft of
this section led on it, which is the third leading reason this retraction has
had to withdraw.

**A caveat that runs the other way**, recorded because it is easy to
over-read in this record's favour. The limit bounds the sum of three channels
sharing the $P^2$ signature, of which the ramp is about a sixth. But the
width grows as $S_0^2$, so a bound on $\kappa$ scales as the square root of
that budget: the companions make the limit about 2.4 to 2.5 times
conservative, not six. The record's own measured saturation-only tightening
of the joint bound is of the same size, but it is classified
NEEDS_EXTERNAL_TREE in `results/saturation_companion.csv` and is not
committed as a digit, so it corroborates the scale and not the value. Which of the three channels is
smallest varies by line: the pumping term is below the ramp on 993.4207 and
993.4192 nm and above it on the other two. **The branching fractions 0.223 to
0.372 are not commensurate with the ramp's ~1/6 share of the P-squared budget
and this page put them on one line as though they were**, which a reader who
checks concludes is false. The per-line statement is the checkable form and is
carried in `docs/methods/04_the_composite_model.md`.

**Five wider retractions were offered in one night and all five were
withdrawn. They are named so that none is revived.**

1. **The reduced chi-square of about 3.7.** It is `stark_sweep.csv`'s, a
   property of C3d's width-only summary regression. The quoted limit is
   C3f's, whose `ub95()` reads a plain 2.706 and whose own total sits below
   one. This record had caught the same misattribution on 2026-08-04.
2. **The coverage study's zeroth percentile.** Its subject is the same C3d
   bound, and the reading was already withdrawn in-record as a like-for-like
   error mixing railed and unrailed simulations. Restricted properly it is a
   12th percentile of 41. Entries 1 and 2 are one category error made twice.
3. **The 837-to-1038 construction spread.** Real and correctly computed, and
   the two limits differ by
   [1.231](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:limit:construction_spread")
   at fixed geometry on both sides, about 23 per cent, and the tail
   probabilities they imply differ by a factor of two, 0.0324 against 0.0165,
   so neither is a third-digit effect and an earlier draft of this entry
   called them one. **The figure is the committed like-for-like row and not
   1038/837.** That ratio of 1.24 divides a geometry-marginalised percentile
   by a central-geometry crossing, mixing the construction change with a
   marginalisation. That is the not-like-for-like class the producer was
   rewritten to remove, reintroduced here by hand. It does not bear on whether an exclusion
   exists, since both readings put the computed value above the limit. It does
   bear on the whole-envelope statement, and that caveat is stated in
   Qualification one above instead of here.
4. **The pass-to-pass spread of a factor of two.** Two different diagnostics
   of near-identical size sit behind it, the 2026-08-17 three-pass warm chain
   and the five cold multi-starts, and the 2026-08-19 correction records the
   second as a display-normalisation artefact. Citing one factor for both is
   the two-instruments-one-sentence class.
5. **The drop-4192 arm.** Its bound lands inside the envelope and not above
   it, its margin is several times smaller than the profile's own numerical
   scatter, and `RESULTS.md` C3f reads the margin from the primary alone.

**What survives all of this is the tension itself.** The computed 1145 a.u.
sits in the upper
[0.0324](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:comparison:posterior_prob_above_computed_here")
of the posterior and Orson's 1093 in the upper
[0.0404](../../results/delta_alpha_posterior.csv "ref:delta_alpha_posterior:comparison:posterior_prob_above_orson2021"),
under the posterior, and 0.017 and 0.016 under the crossing. Those two sit
closer together than this profile's own numerical noise floor, so no ordering
between them may be read. Neither pair is quotable
to three digits, and the data prefer a smaller shift than the calculation
predicts under both. This record simply does not claim a calibrated
confidence level for that preference.

## 4. Why the experiment cannot do better

Four limitations, of three different kinds, and only one of them is about
noise.

**Statistical: the estimator sits where its own gradient vanishes.** The width
grows as the square of $S_0$, so at the best fit, which rails at $\kappa = 0$, the
derivative of the observable with respect to the parameter is zero. A
linearised error bar evaluated there is a finite-difference artefact carrying
no coverage, which is why every bound above is a profile-likelihood bound and
not a Wald bound. That correction is recorded in
[`rb5s6s/stark.py`](../../rb5s6s/stark.py) and its coverage was checked by
simulation.

**The wrong moment is being used, by a factor of forty.** At the bound the
light-shift term moves the composite width by about 4 kHz, against a per-block
width scatter of 88 kHz. The same term pulls the line centre by about 150 kHz.
The centre is the sensitive moment because a one-sided perturbation moves a
line's position far more than its width, and a symmetric summary of an
antisymmetric perturbation is insensitive by construction. The centre channel
is nevertheless the weakest bound in the table, because the laser lock drifted
during the campaign and absolute centres are lost. **The experiment measured
the insensitive moment well and the sensitive moment not at all.**

**Model: the geometry is accepted rather than measured.** The waist of 64 µm,
with an accepted band of 62 to 68 µm, comes from one profiler measurement on
the predecessor laser of this apparatus lineage, not on the campaign's own
beam, and no error bar on the campaign's own waist exists to be quoted. The
retro ratio of 0.94 is an assumption. Both enter the prediction, and the bound itself moves with the
assumed waist, from 1.050 to 1.191 MHz/W across 56 to 72 µm. This is the
largest open systematic in the whole programme, and it is
[big picture chapter 5](../big_picture/05_next-vapour-cell.md)'s first item.

**Model: mechanisms sharing the power signature are omitted.** Atomic
saturation and hyperfine pumping both widen the line with the same power
dependence as the ramp, and both are left out of the production model. Their
effect is measured rather than argued: including a saturation companion
tightens the joint bound by a factor of 2.21. The committed bound is therefore
loose by a known amount, and no committed number moves on it because the
companion rests on a two-level saturation law that is standard practice rather
than a derivation for this level structure.

## 5. Three levels of improvement

Every level names the plan block that runs it, so that the recipe and the
programme cannot drift apart. The
[Needs, Shots, Go-no-go, Empty and Record](../plan/04_intensity-and-light-shift.md)
fields stay in the plan.

### An improved bound

**What it delivers.** Removal of the geometry systematic and of the convergence
ambiguity, tightening the existing bound and making it reproducible, without
producing a measurement.

**Recipe.** Measure the beam waist on the day, at several powers, with the EOM
in the beam and thermalised at each, and measure the retro ratio against power
in the same session. Repeat the existing power ladder in randomised order.
Nothing else changes: same cell, same temperatures, same detection.

**Success criterion, all six parts.** Precision: the waist known to better than
2 µm, which holds the bound's geometry sensitivity below the 13 per cent it
currently spans. Identifiability: unchanged, this level does not break a
degeneracy. Coverage: the profile construction already over-covers where the
bounds live and this is unaffected. Convergence: independent starts on the
pooled surface agree, which is the open question and is the reason the
randomised ladder matters. Model validity: residuals unchanged from the current
fit. Calibration: the waist becomes a measurement rather than an accepted prior.

**Minimum viable version.** One session, one beam profile at three powers with
the EOM thermalised. That alone converts the largest systematic from accepted to
measured, and it is an afternoon.

**Kill criterion.** If the measured waist at several powers is not stable to
within the band the transit kernel assumes, the pooling across sessions that
every joint construction relies on is not licensed, and the joint bounds are
withdrawn rather than tightened.

### A measurement

**What it delivers.** A value for $\kappa$ with an uncertainty, rather than an
upper limit, by moving from the insensitive moment to the sensitive one.

**Recipe.** A fixed cavity lock, so that absolute line centres survive across
the power ladder, then a randomised power ladder at fixed temperature with the
centre recorded against power. The lever is the 150 kHz centre pull against an
88 kHz block scatter, so the measurement is a regression of centre on power
rather than of width on power. This is
[plan chapter 9](../plan/09_the-fixed-lock.md) and
[chapter 10](../plan/10_the-fixed-lock-instrument.md), and the lock is now
available rather than proposed.

**Success criterion.** Precision: a centre pull resolved at better than three
standard deviations, which the 40-to-1 moment ratio makes reachable where the
width channel is not. Identifiability: the light shift separated from
saturation and pumping, which move the width but not the centre, so this level
breaks the degeneracy that the width channel cannot. Coverage: verified by
injection and recovery at the achieved noise. Convergence: independent starts
agree, tested rather than assumed. Model validity: the drift model checked
against a zero-signal control epoch, since a control epoch has already been
shown to reproduce a comparable spurious pull. Calibration: the frequency axis
anchored, and the waist measured as in the level above.

**Minimum viable version.** One fixed-lock session with three powers and a
control epoch. Three points determine a slope and the control decides whether
the slope is drift.

**Kill criterion.** If the zero-signal control epoch reproduces the pull, the
centre channel is measuring lock drift and the result is a bound again. This
has happened once already, at 2.69 standard deviations, which is why the
control is in the recipe rather than in the discussion.

### A competitive measurement

**What it delivers.** An uncertainty comparable with the direct comparators of
section 2, which means a few per cent on the differential polarizability, and
the first reading of the intensity distribution from the lineshape on an
alkali nS to n'S line.

**Recipe.** A tighter focus, near 16 µm, which raises the predicted $S_0$ to
5.56 MHz and clears the measured skew threshold of about 2.5 MHz by design.
The skew channel then carries signal for the first time, and the skew is the
observable that maps the distribution rather than only its mean. With the fixed
lock and the measured waist already in place, all three moments contribute.

**Success criterion.** Precision: comparable with Lee 2010's six per cent on a
sister line. Identifiability: three moments constraining two parameters, which
is over-determined rather than degenerate. Coverage: injection and recovery at
the achieved noise. Convergence: multi-start agreement, a requirement rather
than an observation. Model validity: the skew's predicted shape tested against
the measured one, which is the actual scientific content. Calibration: waist,
retro ratio and axis all measured in-session.

**Minimum viable version.** A single tight-focus condition at maximum power
alongside one loose-focus reference, to demonstrate the skew appears where the
threshold says it should. That is a discrimination test, not yet a measurement,
and it is cheap.

**What is calculation required.** The achievable uncertainty at 16 µm. The
threshold margin, 5.56 MHz predicted against the measured 2.5 MHz turn-on, is
computed, and
[the projection note](../notes/extended_lever_and_skew_projection.md) states
why the precision beyond it needs a full lineshape simulation at the
tight-focus geometry rather than an extrapolation, so no number is given
here.

## 6. What goes wrong as sensitivity improves

| knob | what it buys | what it costs |
|---|---|---|
| more power | signal, and $S_0$ linearly | saturation and hyperfine pumping, which share the ramp's power law exactly and are omitted from the model, so the bound loosens as they grow |
| tighter waist | $S_0$ quadratically, and the skew channel | transit broadening, a faster-varying envelope along the cell, alignment sensitivity, and a geometry that must be characterised to the same accuracy it is being used at |
| higher temperature | density and signal | collisional broadening in the same width channel, blackbody, and thermal gradients |
| wider scan | wings and baseline discrimination | sweep nonlinearity and hysteresis, both measured and both worse at the leading edge |
| more repeats | the block scatter falls as the square root | drift within the block, which the randomised ladder exists to break |

The pattern worth naming: **every knob that raises $S_0$ also raises something
that imitates it.** That is why the levels above buy identifiability through
the centre and skew channels rather than buying precision through power.

## 7. What each level would make answerable

**Improved bound.** Whether the geometry, rather than the statistics, is what
stands between this archive and a measurement. It converts the programme's
largest open systematic into a measured quantity.

**Measurement.** Whether the differential polarizability at 993 nm agrees with
the computed value, which no experiment has yet tested on this line, and
whether Orson 2021's null is a null or a resolution limit.

**Competitive measurement.** Whether an intensity distribution can be read from
a two-photon lineshape at all. The technique generalises to any two-photon
transition in a focused beam, which is the methodological payoff, and it
inverts the standard practice of engineering the distribution away.

## 8. What remains impossible

**Not measurable with this architecture.** The differential polarizability
cannot be extracted to better than the geometry is known, so $\Delta\alpha$
from this apparatus is limited by beam characterisation and not by
spectroscopy. A percent-level $\Delta\alpha$ needs an intensity calibration
this cell geometry does not support.

**Not separable in principle here.** Atomic saturation, hyperfine pumping and
the ramp are degenerate in both of the width channel's continuous knobs, power
and waist, so no sweep in either separates them. Only the centroid, which they
do not move, and the line index, which distinguishes them by hyperfine
branching, can. The centroid route is the measurement level above. The line
index route gives 4 kHz against an 88 kHz scatter and is real but unspendable
in this archive.

**Not yet measured, which is different.** The convergence of the pooled
surface. That is a computational question with a known answer route, and it is
open rather than closed.

## See also

- [Collisional self-broadening](self-broadening.md), the other headline
  quantity, which shares the width channel with this one
- [The campaign](campaign.md), for how one session serves both
- [The AC-Stark shift](../wiki/ac-stark-shift.md) for the physics
- [Identifiability](../wiki/identifiability.md) for why a bound rather than a
  value
- [Plan chapter 4](../plan/04_intensity-and-light-shift.md) for the blocks that
  run these recipes
