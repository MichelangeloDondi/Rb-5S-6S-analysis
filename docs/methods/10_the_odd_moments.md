*Chapter 10 of the [methods](../methods.md)*

## 10. The odd moments of the shifted line, and what they can carry

**The question.** The odd cumulants of a shifted line are meant to be the
channel that reads the shift while the symmetric kernels drop out. Which orders
actually carry it here, and at what window?
**Takes.** The lineshape and AC-Stark chapters, and the composite the twin
builds.
**Gives.** A measured account of what the third, fifth and seventh orders do,
and a withdrawal: the convolution picture the argument rests on does not
describe this model.
**Skip if.** You only need the shift channel this record uses. That is the
third cumulant, and the AC-Stark chapter covers it. This chapter is about
whether the higher orders add anything, and its current answer is that the
question is not yet properly posed.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)

> **A withdrawal was posted here and is itself withdrawn, 2026-09-04. Section
> 12 has the account. The convolution assumption under this chapter was tested,
> appeared to fail at 35 per cent of peak, and the chapter was reframed on that.
> The test was wrong: this model's shift distribution lives on the negative
> interval and the search was over the positive one. Redone on the correct
> support the residual is one part in a thousand, which is rounding. The
> convolution holds, the ladder is the right prediction, and sections 1 to 10
> stand.**


**Its central question is OPEN, and this chapter says so rather than hiding it:
publishing the agreement without the disagreement is the failure this record
keeps finding in itself.**

## 1. The exact statement, untruncated

The composite is a convolution. An atom at intensity `I` is shifted by `s`, the
beam's spatial profile induces a shift distribution `f(s)` supported on
`[0, S_max]`, and each shifted class is broadened by a kernel `L` that is
symmetric about its own centre:

    P(nu) = (f * L)(nu)

**That equality is conditional.** Written as a volume integral, the line is
`f * L` exactly only when the kernel `L` is the same at every volume element,
and it is not: the transit width goes as the inverse local beam radius. What
makes the convolution usable is that the collected volume is short. Over the
axial window the collection optics set
([chapter 3](03_the_ac_stark_ramp.md), diverging-beam collection), the
signal-weighted transit width has an rms spread of
[0.97](../../results/prediction_band.csv "ref:prediction_band:collection_window:transit_kernel_rms_spread_pct")
per cent, so the statement below holds to that level and the residual is a
symmetric broadening to which the odd cumulants are blind at leading order.

**Cumulants add under convolution.** So for every order,

    k_n(P) = k_n(f) + k_n(L)

`L` is symmetric, so all its odd cumulants vanish, `k_3(L) = k_5(L) = k_7(L) = 0`.
Therefore **every odd cumulant of the line is a cumulant of the shift
distribution alone**, and the kernel drops out exactly. That is the whole
reason the odd moments are the shift channel.

`f` lives on `[0, S_max]`, so writing `f(s) = (1/S_max) g(s/S_max)` with `g`
fixed by the geometry gives, by the scaling of cumulants,

    k_n(f) = c_n * S_max^n,     c_n a pure number of the geometry

**So the untruncated ladder is exact: k_3 goes as the cube, k_5 as the fifth,
k_7 as the seventh.** Nothing about the kernel enters, and nothing about the
intensity except through `S_max`.

## 2. Why the record cannot use that statement directly

`L` contains a Lorentzian: the natural width always, the collisional width
usually. **A Lorentzian has no finite second or higher moment**, so `k_n(P)`
does not exist for any `n >= 2` and the equations above are formally empty.
Every moment this project computes is therefore a windowed moment, over a
finite range, and a window is not a convolution: **truncation destroys the
additivity the section above rests on.**

## 3. The measurement, and it contradicts the naive expectation

Self-centred windowed cumulants on the production path, log-derivative with
respect to the shift, five per cent central differences:

| kernel | half-window | k3 | k5 | k7 |
|---|---|---|---|---|
| archive | 8 | 2.999 | 3.000 | 3.004 |
| archive | 30 | 3.000 | 3.000 | 3.000 |
| reduced collisional | 8 | 2.999 | 3.001 | 3.007 |
| reduced collisional | 30 | 3.000 | 3.000 | 3.000 |

**All three orders return the cube, not the ladder.** The effect survives a
window nearly six times the line width and survives reducing the collisional
Lorentzian, which leaves the natural one.

## 4. The candidate explanation, and it is not yet demonstrated

`k_5 = mu_5 - 10 mu_3 mu_2` is built so that the cross term cancels. Expanding
the convolution in the ramp's raw moments, `mu_5` carries a term proportional
to `m_3 * k_2`, which is order `S^3`, and the subtraction removes it exactly
only when the moments are taken over the whole line. **Windowed, the
cancellation is inexact, and the residue is order S^3 where the true `k_5` is
order S^5.** With `S` about 0.36 MHz against a 5.4 MHz line, `S^3` exceeds `S^5`
by four orders of magnitude, so the residue would dominate completely and
every odd order would report the cube.

That is consistent with everything measured. **It is not established.** A
direct numerical test on a hand-built Gaussian kernel returned catastrophic
cancellation in `k_5` and `k_7` rather than an answer, and is not reported here
as evidence in either direction.

## 5. What follows for the analysis, taking the measurement as it stands

* **The shift channel is one number, not three.** If all odd orders carry the
  same power, `k_5` and `k_7` add no independent shift information: they are
  the same asymmetry read through different truncation weights.
* **They do add information about the kernels.** Their nuisance sensitivities
  are measured non-parallel (collisional slopes -0.108, -0.001, +0.280 at a
  window of 8), so jointly they constrain the widths even while sharing a
  shift dependence.
* **The simple ratios are shift-free by construction** if the common power
  holds, and measured so to three or four decimals.

## 6. What is owed before this leaves draft

1. The residue argument of section 4 carried through analytically, to the
   order that predicts the coefficient and not merely the power.
2. A numerically sound test of the untruncated ladder, on a kernel whose
   moments exist, with the cancellation done in a way that keeps the
   answer above the rounding.
3. The same measurement at a campaign shift. **This was run on 2026-09-04 and
   it did not confirm section 4.** See section 7.

## 7. The decisive test was run, and the explanation did not survive it

Section 4 predicts that raising the shift toward and past the line width lets
the true fifth-order term emerge from under the third-order residue, so `k_5`'s
slope should migrate from three toward five. Measured, with the window widened
with the shift so truncation stays comparable:

| shift, MHz | shift / line width | window | k3 | k5 | k7 |
|---|---|---|---|---|---|
| 0.364 | 0.07 | 4.5 | 2.997 | 2.998 | 3.001 |
| 1.0 | 0.19 | 5.5 | 2.986 | 2.995 | 3.015 |
| 2.0 | 0.37 | 7.0 | 2.974 | 3.004 | 3.096 |
| 4.0 | 0.74 | 10.0 | 2.970 | 3.056 | 3.606 |
| 8.0 | 1.48 | 16.0 | 2.977 | 3.182 | -5.597 |
| 16.0 | 2.96 | 28.0 | 2.985 | 3.410 | 1.042 |

**`k_5` moves, but nowhere near far enough.** At a shift three times the line
width, where the ramp dominates the profile entirely and the ladder should be
plain, the slope has reached 3.41 against the five that section 4 predicts.
The drift is real and monotone, so something does migrate, but the residue
account as written does not explain a shift-independent cube that survives to
three line widths.

**And `k_7` is numerically unusable.** Its slope runs 3.0, 3.0, 3.1, 3.6,
then -5.6 and 1.0. The seventh-order combination is a difference of large
products and its answer falls under the rounding once the profile broadens. **The
seventh cumulant is therefore struck from the usable observables**, whatever
the theory says about it, until an estimator exists that computes it stably.

## 8. One of the two readings is refuted, on a kernel whose moments exist

Section 7 left two readings. The first, that the windowed cumulants are
dominated by the window edges at every shift so the cube would belong to the
truncation geometry and not to the ramp, is now refuted for a kernel with
finite moments.

The test builds two ramp distributions with the same third cumulant and a
deliberately different fifth, convolves each with a Gaussian, and windows the
result. If the windowed fifth cumulant carried nothing about the ramp it would
be the same for both.

Validated first, since an earlier hand-built attempt at this failed quietly:
a symmetric Gaussian alone returns a third cumulant of exactly zero and a
fifth of 3e-14, and a three-point ramp convolved with it returns 1.4880 and
-11.322 against true values of 1.4880 and -11.322. Convolution additivity is
recovered to full precision, so the machinery reports what it is asked.

Then, for two ramps differing in their true fifth cumulant by -0.0135:

| half-window | windowed k5, ramp A | ramp B | recovered |
|---|---|---|---|
| 4 | 0.0000 | -0.0013 | one tenth |
| 8 | 0.0000 | -0.0067 | one half |
| 16 | 0.0000 | -0.0135 | all of it |
| 40 | 0.0000 | -0.0135 | all of it |

**The windowed fifth cumulant does carry the ramp's own fifth cumulant**, in
full at a wide window and with a survival factor at a narrow one, exactly as
the third cumulant does and as this record's survival ratios already describe.
It is an observable of the ramp, not an artefact of the edges.

**Which leaves the Lorentzian as the remaining suspect.** The clean test above
uses a Gaussian, whose moments exist. The composite this record fits contains
a Lorentzian from the natural width and usually another from collisions, whose
moments do not exist at any order above the first, so its truncated
contribution is a function of the window and not a property of the line.
That is the difference between the case where the ladder is recovered and the
case where every order returns the cube, and it is where item 1 of section 6
should now be aimed.

## 9. The Lorentzian is confirmed, and the fifth cumulant is struck with the seventh

Section 8 named the Lorentzian as the remaining suspect. The same two-ramp
test, with the kernel changed and nothing else, confirms it. The figure is the
fraction of the ramps' true difference in the fifth cumulant that the windowed
estimator returns:

| kernel | half-window 8 | 16 | 40 |
|---|---|---|---|
| Gaussian | 216% | **100.0%** | **100.0%** |
| Lorentzian | 570% | 1858% | 5946% |

With a Gaussian the estimator converges on the ramp's own fifth cumulant and
returns it exactly once the window is wide enough to contain the line. With a
Lorentzian it does not converge at all. The recovered fraction grows with the
window without bound, which is the signature of the divergent moment: what the
window takes from the tail grows faster than the ramp's contribution, so at
every practical window the number is a measurement of the kernel's truncated
tail and of the window, not of the ramp.

**So the fifth cumulant is struck from the usable observables for this line,
and it goes for the same reason as the seventh.** A Lorentzian sits in every
profile this record fits, from the natural width if from nothing else. Section
4c of the plan proposed that three odd orders span the two width nuisances
while sharing a shift dependence. **That architecture does not survive this
table.** What survives is the third cumulant alone, whose truncated
contribution is bounded and already carried in this record's survival ratios,
and whose window dependence is measured instead of divergent.

**The moment-family programme does not survive in the form it was proposed.**
The shift channel is one observable, not three, and the ratios that were to
pin the kernels without touching the shift are built from orders that do not
survive the kernel this experiment has. The separation of the widths has to
come from somewhere else, and the trace axes of section 4c, power above all,
are where it now has to come from.

## 10. Where the ladder is recoverable, and why this transition never reaches it

A factorial on the twin settles what the earlier sections left. The ramp's own
cumulants were validated first and scale as designed, powers of 3.000 and
5.000 to three decimals. The table is the power the windowed estimator reports
for each cumulant, against the fraction of the kernel that is Lorentzian:

| Lorentzian fraction | window 4 | 8 | 16 |
|---|---|---|---|
| 0.00 | 2.96 / 2.98 | 2.97 / 3.07 | 3.00 / **4.91** |
| 0.15 | 2.95 / 2.97 | 2.98 / 3.06 | 3.00 / 3.05 |
| 0.35 | 2.93 / 2.96 | 2.99 / 3.03 | 3.00 / 3.02 |
| 0.60 | 2.92 / 2.95 | 2.99 / 3.01 | 3.00 / 3.01 |
| 1.00 | 2.93 / 2.94 | 2.99 / 3.00 | 3.00 / 3.01 |

(each cell is the third cumulant's power and then the fifth's.)

**One cell of fifteen recovers the fifth power, and it is the one with no
Lorentzian at all and the widest window.** A Lorentzian fraction of 0.15 is
already enough to return the fifth cumulant to the third power. The third
cumulant's own power is stable at 3.00 everywhere, which is what makes it the
usable channel.

**This transition cannot reach that cell, and the reason is a constant.** The
natural width of the upper state is 3.493 MHz and is Lorentzian. The Gaussian
widths of the archive's line, the laser at 1.6 and the transit at 0.958 in
quadrature, come to 1.865 MHz. So the archive sits at a Lorentzian fraction of
**0.68**, and with the collisional term driven to zero the floor is still
**0.65**. Reaching 0.15 would need Gaussian widths near 20 MHz, which is not a
line anyone would fit.

**So the fifth cumulant is not a channel this experiment can open, at any
power, temperature, lock or window.** It is not a question of noise or of
statistics. The negative result is structural and it is permanent for this
transition, and stating it saves the campaign from designing toward an
observable that does not exist here.

**What the two datasets can therefore deliver.** The 2025 archive and the new
campaign both have exactly one moment channel, the third cumulant. Where the
campaign gains is not in new observables but in the two levers already
measured: the shift itself, where the traces a given precision needs fall as
its inverse fourth power, and an external width measurement, which the profile
likelihood turns into a factor of ten. Neither is a moment-family argument.

**So the question is more open than section 4 left it, not less.** Two
readings remain and this chapter does not choose between them: the windowed
cumulants may be dominated by the window edges at every shift, in which case
the cube is a property of the truncation geometry and not of the ramp. Or the
convergence toward the ladder may be genuine but far slower than a leading-order
argument suggests. Distinguishing them needs the coefficient, not the power,
and that is the analytic work item 1 above already names.

## 11. The assumption under all of it, tested at last, and it does not hold

Sections 1 to 10 rest on one thing: that the line is a fixed kernel convolved
with a distribution of shifts. Cumulants add only under convolution, and the
kernel drops out of the odd orders only because it is symmetric and enters that
way. Nothing in this chapter tested it.

**The test.** Take the model at zero shift as the kernel, and ask whether any
non-negative weight on the shift interval reproduces the model at a shift of
2 MHz. This is a non-negative least squares problem with eighty-one shift
classes, and it is exactly the question of whether the ramp is a convolution.

**The result.** The best non-negative weight leaves a residual of 35 per cent
of the peak. A convolution would leave rounding. The confound was checked: with
the shift resolved on the grid the internal step is set by the narrowest kernel
at both shifts here, so the two profiles are computed at the same resolution
and the residual is not a resolution artefact. The first moment does move as
minus two thirds of the shift, matching the record's own derivation, so the
model is not wrong. It is doing something the convolution picture does not
describe.

**What follows.**

* The ladder of 3, 5, 7 is a property of a convolution with a scaling shift
  distribution. It is not a prediction about this model until the model is
  shown to be that, and it is not.
* So the measured cube at every order is not necessarily a defect of the
  estimator, of the window, or of the Lorentzian. It may be what this model
  correctly produces, in which case sections 4, 7, 9 and 10 are answering a
  question that was not posed.
* **The higher-moment programme is reopened.** Section 10 closed it on a
  comparison between a measured power and a predicted one. The prediction does
  not apply, so the closure does not stand.

**What has to happen before this chapter says anything else.** Read what the
model actually does with the shift, from its own source and its own
derivation in `docs/methods/03`, and restate the expected orders for the
construction it actually uses. Only then is a measured power comparable to anything. The
sections above are kept, with this note at the head, because the measurements
in them are sound and only their framing is in question.

## 12. The convolution assumption, tested wrongly and then correctly

Section 11 reported that no non-negative weight on the shift interval
reproduces the shifted profile, leaving 35 per cent of the peak as residual,
and the chapter was reframed around that. **The test was wrong and this section
replaces it.**

`stark_ramp` puts its density on `[-s0, 0]`, red shifts, because the shift is
to lower frequency. The search was over `[0, +s0]`. It asked whether a sum of
rightward shifts reproduces a profile built from leftward ones, and the answer
to that is correctly no. The measured first moment was already negative, and
that should have been read as a contradiction of the test rather than a
property of the model.

**Redone on the support the model actually uses:**

| shift | residual, wrong support | residual, correct support | recovered mean | expected |
|---|---|---|---|---|
| 1.0 | 1.7e-1 | **1.1e-3** | -0.6667 | -0.6667 |
| 2.0 | 3.5e-1 | **1.1e-3** | -1.3333 | -1.3333 |
| 4.0 | 6.5e-1 | **1.1e-3** | -2.6667 | -2.6667 |

One part in a thousand of the peak is rounding. **The composite is a
convolution of a fixed kernel with a shift distribution**, the recovered mean
is exactly the two thirds of the shift the AC-Stark chapter derives, and the
recovered distribution's own third cumulant runs 0.00732, 0.05940 and 0.47439
at those three shifts, ratios of 8.11 and 7.99 against the 8 that a cube
demands. The ramp scales as designed.

**So sections 1 to 10 stand.** The ladder of three, five and seven is the right
prediction for this model, the measured cube at every windowed order is a real
property of the windowed estimator, and the higher-moment programme is closed
again.

**With one correction that is independent of all this.** Section 10 argued the
closure by placing the archive at a Lorentzian fraction of 0.68 against a
threshold near 0.15. Those two numbers came from different definitions, a
synthetic kernel weight and a linear sum of full widths, and are not
commensurable. The closure rests instead on the regrounded scan: on the
production model, with the window set as a multiple of each line's own width,
the fifth cumulant's local power is 3.00 in every cell tested, including a
Gaussian-dominated line of 42 MHz at ten times its own width. That comparison
is in the right units and it is the one to cite.
