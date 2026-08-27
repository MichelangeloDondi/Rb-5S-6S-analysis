# The big picture

**The question.** What is this line, what did the 2025 measurement actually
establish, what does it still not determine, and what would a further session
convert?
**Takes.** Nothing.
**Gives.** The epistemic map of the experiment, quantity by quantity, and the
route into the chapters that argue each part of it.
**Skip if.** You want the numbers rather than the map, in which case
[RESULTS.md](RESULTS.md) is the ledger and [CLAIMS.md](CLAIMS.md) the register.
If you arrived holding one quantity and want its literature benchmark, its
constructions, its limiting mechanism and the recipes that would improve it,
that is [quantities/](quantities/README.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

This page is the information structure of one experiment. A Doppler-free
two-photon measurement of the rubidium 5S to 6S line at 993 nm, taken in 2025
under a lock that drifted, is analysed for what its lineshapes determine. The
tables below say which quantities that fixes, which it only bounds, which it
leaves undetermined and why, and what a designed session would change about
each. Everything quantitative traces to [RESULTS.md](RESULTS.md) and the files
it carries provenance for.

---

## Part I. What the 2025 measurement established

The headline is not a number. It is that the DATA constrain the light shift and
the collision rate without identifying either independently of the other
broadening mechanisms. The numbers follow from that, and each one carries the
construction it was measured under, because a bound quoted without its
construction reads as model-independent and none of these are.

| question | quantity | what is observed | what is inferred | parameter status | 2025 result | construction it depends on | what limits it |
|---|---|---|---|---|---|---|---|
| **Q-model-01** Does one lineshape model describe every condition? | the composite profile | 32 conditions of a temperature and power sweep | natural, transit, laser and collisional widths convolved | described | reduced chi-square 0.78 to 1.09, mean 0.89 | the accepted transit kernel and the waist of record | model |
| **Q-width-01** Can the collisional and laser widths be separated? | the width split | one total width per condition, to 0.0032 MHz | the split into its parts | **not identified** | the split direction is constrained only to 0.0588 MHz, a factor of eighteen worse, at a condition number of 345 | the joint fit over the shared-width structure | identifiability |
| **Q-beta-01** How fast do collisions broaden the line? | the collisional coefficient | widths across four densities | a rate per unit density | **bounded** | below 0.03 to 0.05 MHz per 1e12 per cubic centimetre, 95 per cent, per peak | the four-temperature construction, on a density scale from vapour-pressure curves | experimental, the density scale |
| **Q-s0-01** How large is the light shift at full power? | the light-shift amplitude | line shapes across a power ladder | the shift amplitude through the shape | **bounded** | below 0.26 MHz at 225 mW, against 0.36 MHz predicted | the joint three-session fit, conditional on the waist of record | experimental, the waist, and identifiability if the three pooled sessions do not share it, since the coefficient goes as one over the waist squared. See [chapter 8](big_picture/08_when-a-joint-fit-is-legitimate.md) |
| **Q-laser-01** How narrow was the laser? | the laser width | the total width and its trend | the laser part of it | **bounded** | below about 1.2 MHz on the laser axis, median 1.74 MHz across conditions | the same split as q-width-01, so conditional on it | identifiability |
| **Q-geom-01** What is the beam waist? | the waist | nothing on this bench | accepted from the apparatus lineage | **not measured here** | taken as 64 micrometres, band 62 to 68 | the lineage, and a transit-width consistency argument | experimental, and it is the largest open systematic |
| **Q-band-01** What is the excess outside the fit window? | the out-of-window residual | a real structured excess, 0.10 to 0.29 per cent of peak | a candidate mechanism, the lineshape rather than the atom | **unattributed, with a candidate** | survives per-trace cubic baselines, and tracks the model's own in-band profile height while vapour density is a null predictor | the production baseline and window | model, and see [the finding](notes/band_excess_is_model_form.md) |

**How to read the parameter status.** *Described* means the data are consistent
with the model and no parameter claim is being made. *Bounded* means one side
of the parameter is excluded and the other is not, under the stated
construction. *Not identified* means the data determine a combination of
parameters but not the parameters themselves, which is a stronger and more
useful statement than a wide error bar. The counts across the whole record are
122 bounds, 55 measured values, 21 nulls and 149 design envelopes, which is the
shape of a dataset taken under a drifting lock.

---

## Part ii. What remains undetermined, and why

Three things are undetermined for three different reasons, and the distinction
decides what a further measurement has to do.

**The width split is undetermined by degeneracy.** The collisional and laser
widths enter the profile almost interchangeably, so the fit determines the
total width fifty times better than it determines how the total divides. No
amount of the same data fixes this, because the information is not in the
lineshape at all. Only an independent measurement of one of the two, or a
lever that moves one without the other, can break it.

Both halves of that sentence are measured rather than argued. Varying the span
by a factor of five and the trace count by a factor of ten moves the
correlation between the two widths by 0.0075 and 0.0000
([`twin_span_sweep.csv`](../results/twin_span_sweep.csv)), which is no
movement, so no acquisition setting is the asymmetric lever. Measuring
one of them elsewhere buys the other a factor of one over the square root of
one minus the correlation squared, between 2.3 and 3.2 across the conditions
this record covers, and
[chapter 7](big_picture/07_limitations-and-identifiability.md) carries the
constructions, together with the second limitation hiding inside this one:
the fit assigns the laser a kernel shape, and the wrong shape biases the
collisional width rather than widening its error bar. What the record measures
about the laser's noise brackets the question from both sides, 0.62 MHz of
slow wander below half a hertz from the digitised wavemeter record and under
28 kHz at seven hertz from the comb clock, leaving exactly the band the width
integrates as the unmeasured middle.

**That shape is no longer unmeasured, as of 2026-08-20, and the answer came
from the line rather than from the laser.** The switch selecting it had been
wired through four modules and never thrown. Thrown, it moves the headline
coefficient by 45 to 67 per cent, which is nine to eighteen sigma on the
statistical error quoted beside it (`results/kernel_headline.csv`).

The per-condition figure first reported beside it, a median 45 per cent shift
in the collisional width, was WITHDRAWN on 2026-08-20 and is not a smaller
version of the same result. Under a Lorentzian laser kernel the collisional
and laser widths enter a single lineshape only through their sum, so at a
fixed condition the split between them is not identified at all: the fit
constrains the sum to two parts in ten thousand and leaves each part free.
The number that had been quoted was the position the optimiser happened to
stop at along that flat direction. What separates the two is density, which
the headline estimator varies and a single condition does not, which is why
the headline figure survives and the per-condition one never had a referent.
The correction is in `results/kernel_identifiability.csv`. That makes it the largest single
assumption the width channel rests on, larger than the width degeneracy above
it, and it means the quoted error bar omits a term about ten times its own
size. And the line does constrain the kernel, though not by the tally first
reported. **The pure-Lorentzian model is nested inside the Gaussian one**: let
the Gaussian width go to zero and what remains is exactly the Lorentzian arm,
since a zero-width Gaussian is a delta function and Lorentzian widths add. A
model that contains another cannot fit worse than it, so the Gaussian winning
at 32 conditions of 32 is arithmetic rather than evidence, and the sign test
built on that tally is withdrawn.

What the comparison does say is in the size of the improvement, read as the
nested likelihood ratio it is: a median $\Delta\chi^2$ of 232 for one extra
parameter sitting on its boundary, about fifteen sigma, over a range from 0.1
to 1303 across the conditions. **A purely Lorentzian laser contribution is
excluded at 26 of the 32 conditions at better than three sigma, 21 of them at
better than ten, and the line requires Gaussian-like content.** That
is a stronger statement than the tally made and it rests on a defensible test.
It also fixes what comes next: since one end-member contains the other, the two
were never alternatives to choose between, and the remaining work is a fitted
Lorentzian-equivalent width inside the containing model, which turns a
comparison of end-members into the error bar
([`run_laser_kernel.py`](../scripts/run_laser_kernel.py),
[the Voigt profile](wiki/voigt-profile.md)).

**That remaining work was done on 2026-08-21, and it stops one level short of
the sentence a reader will want.** Fitting the Lorentzian-equivalent width
inside the containing model at each peak, against the pinned-Gaussian arm,
gives a component present at every peak by $\Delta\chi^2$ of 176 to 961, with
peak-conditioned values of 0.315 to 0.449 MHz (`results/kernel_k3.csv`). The
same producer checks its own footing: the pinned arm reproduces the committed
collisional coefficient to seven parts in ten thousand, without which the
difference would be between producers rather than between kernels. Sized
against the statistical error on a matched footing, the kernel choice is
$R_\text{kernel} = 3.24$ times larger (`results/kernel_budget.csv`), so the
model form, not the noise, is what limits that coefficient now.

**The estimator was made to fail before it was believed.** Five hostile
synthetic worlds, 500 trials each, returned **0 false positives per world**,
including one world that varies only the numerical grid and so tests the
arithmetic rather than the physics (`results/kernel_worlds.csv`).

**And the record stops there deliberately.** Whether the four peaks share one
value is neither rejected nor established at $p = 0.097$, so their
inverse-variance mean is never written on its own. Attributing the component to
the laser is a separate claim that no measurement yet taken licenses, since the
one in-situ laser measurement samples a different band from the one a scanned
width integrates (`results/kernel_k5.csv`). And $R_\text{kernel}$ is a
sensitivity within the two forms tested, not over all model forms. A parameter
identified is not a common parameter identified is not an origin identified is
not a model class shown adequate, and this result sits at the first of those
four. [Chapter 7](big_picture/07_limitations-and-identifiability.md) carries it
with the figure.

**The atlas now qualifies, and it detects.** Stacking per-condition residuals
on a common axis and testing against a null that flips each condition's sign, a
common residual structure appears at the permutation floor in both arms, the
synthetic control built from the fitted model returns clean, and **the
detection survives the removal of any single condition**. The tested inference
family leaves **reproducible residual structure** that no member of it produces
(`results/kernel_k4.csv`).

**What that is and is not.** It is named unexplained reproducible residual
structure rather than model inadequacy, because a residual can come from the
physical model, the noise model, preprocessing or the instrument, and this test
separates none of them. **No mechanism is named.** **$R_\text{kernel}$ is
unchanged and remains a sensitivity within the class that was tested**, since
turning this structure into an admissible alternative model and computing its
effect on the collisional coefficient has not been done. And the domain is
stated: the structure is inside the fit window.

**Its relation to the excess outside the window has since been measured and is no longer
unresolved.** Regressing each condition's in-window amplitude on
the model's own profile height and on vapour density at once, weighted, height
wins at 9.4 sigma and density gives 1.3, with the two predictors correlated
only 0.49 and the height term surviving every leave-one-out above 8.5
(`results/kernel_k8.csv`). **The band excess outside the window gives +8.65 and
-0.75 on the same two predictors by the same method**, so both structures share
a predictor and both exclude density, and one common cause explains them better
than two unrelated ones. **The two band figures are the weaker pair**: they
come from [a note with no committed producer](notes/band_excess_is_model_form.md).
**A documented reconstruction (`results/band_excess.csv`) rebuilt
the construction from the same committed traces and did not reproduce them**:
the census matches exactly at 79 traces while the cubic-surviving amplitude
and the height significance come back far weaker. **A preregistered recovery
then identified the note's predictor** (the absolute in-band model height,
matching the note's 0.415 correlation to 0.001) **and proved no predictor
reaches the note's significance with the current amplitudes** (0.70 partial
correlation required, 0.39 available), so the discrepancy sits in the
amplitude vector itself. The density reading is construction-dependent in
the current tree, negative under the shape-only predictor and the marginal
positive under the recovered one, so the band's mechanism question is OPEN.
The K8 pair beside them is regenerated and graded on every run.

**What that does not say.** A residual normalised by the noise scales with the
signal under any fractional model error, so profile mismatch, a detector
nonlinearity and an amplitude-dependent baseline all predict this. **The
mechanism is not named.** What is excluded is a density-driven collisional
origin.

**On the two runs.** An earlier run of the same atlas on the same data was
declared void by its own preregistered check, which had invented a reproduction
threshold twenty times stricter than the one `verify_results_fresh.py` sets for
this repository and voided on a single condition already measured as
environment-sensitive. The criterion was not loosened afterwards: a second run
was preregistered with the repository's own standard plus a leave-one-out test,
and both runs stand in the record.

**The absolute frequency axis is undetermined by construction.** The lock
drifted and the wavemeter was photographed rather than logged, so every axis in
the archive is differential. Line shapes survive this and line positions do
not, which is why the analysis reads shapes.

**The waist is undetermined by absence.** It was never measured on this bench.
Every intensity-denominated quantity is conditional on it, which is why the
light-shift row above is a bound with a condition attached rather than a
measurement.

### The identifiability map

Which quantities each configuration determines. A cell says the status that
configuration would reach for that quantity, given the documented assumptions
and the projected machinery, and the hatch marks the ones that need the new
measurement rather than a reanalysis. Nothing in the added rows is a result.

![which quantities each configuration determines](../figures/fig33_identifiability_matrix.png)

---

## Part iii. What a further session would change

Each row is one ambiguity, the measurement that removes it, and the outcome
that measurement targets. The outcome column is a target and not a result, and
the failure column is what the record would say if the design did not work,
which is the part that makes the design testable rather than hopeful.

| ambiguity now | why the present data cannot resolve it | the new measurement | ambiguity removed | target outcome | validation basis | what would say it failed |
|---|---|---|---|---|---|---|
| the width split | two kernels exchange inside one profile | an independent laser-width measurement, the only lever acting on identifiability rather than noise | the width ridge | the collisional width becomes separately identifiable | the twin's measured span-and-count invariance and the pinning simulation, [chapter 5 of the plan](plan/05_width-collision-amplitude.md) and [identifiability](wiki/identifiability.md) | the pinned fit's residual scatter does not fall, which would place the limitation beyond the laser width |
| the absolute axis | no logged frequency reference | two same-isotope pairs inside one sweep, plus a logged wavemeter | absolute-frequency ambiguity | the axis becomes calibratable to the accuracy of the hyperfine constants | design simulation, [PLAN §10c](PLAN.md) | the two rulers disagree beyond the projected nonlinearity, which would mean the axis model is wrong rather than imprecise |
| the baseline | the pedestal is flat across the archive's window and a free baseline absorbs it | a span wide enough to curve the pedestal, with the pedestal fitted as a pedestal | baseline against signal | the baseline becomes measured rather than chosen | design simulation, tested by injection ([PLAN §10a](PLAN.md)) | the wide fit does not recover an injected pedestal, which would mean the span is still too narrow |
| the transit kernel | the waist is accepted and the cusp form is untested here | a beam profile measured on the day, plus one cold and dim condition | the geometry systematic | the transit model becomes directly testable | design simulation, [PLAN §10c](PLAN.md) | the model comparison stays inconclusive at the achieved precision |
| the light shift | one power cannot separate the shift from other broadening, and one trace has too little signal in the asymmetry | a randomised power ladder with more rungs and per-sweep normalisation | shift against broadening | measured rather than bounded | design projection, from the projections file | the per-sweep normalisation scatter exceeds the pull it is meant to resolve |
| the band excess | a model-form candidate and no mechanism, the pedestal excluded as its source, and the skew channel excluding every power-growing and density-keyed origin, leaving structure of fixed absolute size | polarisation isolation blocks, which separate line from pedestal in hardware | signal against contaminant | the anomaly becomes attributable | design simulation, [PLAN §10c](PLAN.md) | the isolated blocks show the same excess, which would move it from the optics into the detection chain |

Each chain is argued in full, with its evidence, in
[limitations and identifiability](big_picture/07_limitations-and-identifiability.md).

---

## Part IV. The projections, quantitatively

![the 2025 limits beside the precision a designed session projects](../figures/fig32_achieved_vs_achievable.png)

*The two panels put what the archive supports on the same axis as what a
designed session projects. A projected precision is drawn as a length in the
panel's own unit rather than as an interval around an assumed centre, because
it is the size of a future error bar and not a claim about where the answer
falls. Panel A puts the four per-peak limits an order of magnitude above the
rate the van der Waals anchor predicts, while the projected precisions sit an
order of magnitude below it, which is what a detection at 9.7 sigma for an
interleaved session and 3.0 at the archive's own noise level means. Panel B
carries a genuine tension rather than a gap: the primary bound on the light
shift sits below the predicted value, and the robustness fit that drops one
peak does not, so the ordering is subset-dependent. Both bounds are drawn for
that reason. The exclusion holds on the full fit, its strength is a range
and not a single two-sigma, and on the three-session construction it does not
survive leaving one peak out: one arm clearly excludes, two clearly do not, and
the fourth sits inside the profile's own scatter of the threshold, so no count
of arms is quotable. RESULTS.md C3f carries all three statements.*

a projection is not a result. The values drawn above are envelope calculations
attached to specific session designs, and they are reported so the cost of a
session can be weighed against what it would buy. The design simulations behind
the acquisition settings are argued in [PLAN.md](PLAN.md) sections 10a to 10c
and are cited there rather than restated here.

---

## Part V. Where to read further

| # | chapter | what it adds |
|---|---|---|
| 1 | [Why this line](big_picture/01_why-this-line.md) | what makes 5S to 6S worth the work, and the trap and clock physics that depends on it |
| 2 | [The method and its limits](big_picture/02_the-method-and-its-limits.md) | the drift-immune method itself, the shape channels it reads, and the size the coefficients should have |
| 3 | [Goals and prior art](big_picture/03_goals-and-prior-art.md) | what is already published on this line, and the gap this work fills |
| 4 | [What the 2025 dataset delivered](big_picture/04_what-2025-delivered.md) | the results of Part I in full, with their derivations linked |
| 5 | [The next vapour-cell session](big_picture/05_next-vapour-cell.md) | the cell measurements ranked by leverage, with costs |
| 6 | [The next nanofibre session](big_picture/06_next-nanofibre.md) | what a guided-atom platform adds that a cell structurally cannot |
| 7 | [Limitations and identifiability](big_picture/07_limitations-and-identifiability.md) | the six chains of Part iii, argued from the diagnostics |
| 8 | [When a joint fit is legitimate](big_picture/08_when-a-joint-fit-is-legitimate.md) | the two sharing decisions this record makes, across peaks and across sessions, and six questions to ask of any pooled fit |
| 9 | [The two campaign cases](big_picture/09_the-campaign-cases.md) | what another campaign adds in total, cell-only against cell-plus-fibre, in the physics, the record, and the laboratory's own instruments |

**The platform lane, for a reader with no fibre.** The fibre thread of this
repository is [chapter 6](big_picture/06_next-nanofibre.md), the second
scenario of [chapter 9](big_picture/09_the-campaign-cases.md),
[the sized candidate](notes/onf_candidate.md), and one wiki page,
[guided atoms and nanofibres](wiki/guided-atoms-and-nanofibres.md), which
carries its own skip line and is the only page there that is not
platform-neutral. Everything else, the method, the results, the plan and the
rest of the wiki, is platform-neutral, so a vapour-cell reader, or one
adapting the pipeline to a different transition
([ADAPTING.md](ADAPTING.md)), skips those four surfaces whole and loses
nothing on their path.

For the derivations, [methods.md](methods.md) owns every one. For the general
concepts, the [wiki](wiki/README.md) explains each technique on its own page.
For the proposed session, [PLAN.md](PLAN.md) is the measurement plan.

### What each piece buys

```
  2025 dataset (done)          model + bounds + method, w0-conditional
        │
        ├── beam-profile w0 ───────► every intensity-denominated bound
        │                            sharpens (no new physics run)
        │
        ├── absorption channel ────► the density scale the collisional
        │   for N(T)                 bound rides on becomes measured
        │
        ├── hot points 150-170 C, ─► beta_self would be measured
        │   peaks interleaved
        │
        ├── fixed-lock cell session ► the pull comes alive, so the
        │         │                   polarizability and the self-shift
        │         │                   would be measured (if run)
        │         │
        │         ├── ramp monitor ► a time axis independent of the scope
        │         │   on a spare     knob, which is what the centre
        │         │   scope channel  channel lost
        │         │
        │         ├── small waist ──► shape-based readout demonstrated vs the pull
        │         │
        │         └── O-band diode at 1297.5 nm ► the 6S-7P matrix element by a
        │                                         differential null, plus the
        │                                         asymmetry sign-flip test
        │
        └── nanofibre session ──────► pushing-dip model + surface shift,
                                      read against the cell reference
```

*Each arrow is independently valuable, and nothing below the 2025 dataset is
required for the 2025 dataset's own results to stand.* [The next vapour-cell
session](big_picture/05_next-vapour-cell.md) ranks four of these arrows by
leverage and quantifies three acquisition changes on the same points. Two
arrows sit outside that ranking on purpose: the ramp monitor is an instrument
repair rather than new physics, which is why [PLAN.md](PLAN.md) §3 puts it at
the top of its own order, and the O-band diode is ranked against the other
candidate lines in
[FUTURE_TRANSITIONS_titsapph.md](FUTURE_TRANSITIONS_titsapph.md) §4.1 instead.
The nanofibre arrow is [chapter 6](big_picture/06_next-nanofibre.md).

![the loop from raw traces through the model to the bounds and back to the limitations](../figures/fig20_method_loop.png)

*How the parts of this page connect. The bounds and the limitations are not two
lists but one loop: what the apparatus could not do sets which observable
survives, the surviving observable sets which model can be fitted, and the
fit's own failures name the next measurement. That is why Part iii exists, and
why it reads downward from the dataset rather than upward from a result.*
