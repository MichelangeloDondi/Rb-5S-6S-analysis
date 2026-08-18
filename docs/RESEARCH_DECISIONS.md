# Research decisions

Why the analysis has the shape it has: which questions this dataset can answer,
which it cannot, and what was done about the gap. The methods pages say what the
pipeline computes, and this one says why it stops where it does.

**The question.** Why does the analysis stop where it stops?
**Takes.** Nothing.
**Gives.** One entry per decision, each pointing at the code or document that
carries it, and each stating the alternative that was rejected.
**Skip if.** You want what the pipeline computes rather than why it computes
that and not something else, which is [methods.md](methods.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

Every entry points at the code or document that carries the decision.

The dataset was taken with a **drifting, hand re-centred laser lock**, so
absolute line centres are unusable and only line *shapes* survive. Most of what
follows is downstream of that one fact.

The decisions at a glance, each argued in full in its numbered section:

| Question | Decision | Why |
|---|---|---|
| Can the width be split into collisional and laser parts? | The total width is the observable, and the split ships with its error and correlation | γ_coll and σ_laser are strongly correlated through the transit kernel (§1) |
| What heads the β_self result? | The model-independent width-slope bound. The global fit is a cross-check | model-form differences reach the coefficient's own scale (§2) |
| Does the dataset's fit carry an AC-Stark term? | No: the nested ladder declines it | the width channel supports a bound, not a component (§3) |
| Are core widths shared across conditions? | Both verdicts reported | the answer flips with how repeats are counted, so neither is asserted (§4) |
| The aborted power block? | Stays excluded | the cut predates the fits, so re-admitting it now would be post hoc (§5) |
| What happens to claims that fail? | They stay on the page, marked | the record of a withdrawal is part of the result (§6) |
| Where do the guards come from? | Each was added after a specific failure | a guard without an incident is decoration (§7) |
| What is left unmodelled? | Named mechanisms, each with the condition that would revive it | silence would read as completeness (§8) |
| The 130 °C density point? | Promoted from diagnostic to the headline four-point lever | same configuration as the temperature ladder, session receipts checked (§9) |
| The joint-refit choices (2026-08-03)? | Measured priors over seeded ones, per-session widths, no robustness row | each argued from the fits' own receipts (§10) |
| Can a cold-start profile be quoted? | Not without a seeded twin, and the minimum search variant runs first | a stuck primary printed a 283,000-unit artifact where the answer is indifference (§11) |
| Why pool the four lines into one slope? | Adopted by a preregistered probe, scored after the pooled number existed | its predictions held, one by a different mechanism than the note argued (§12) |
| Why does the ruler figure show six teeth, not seven? | The all-seven clause returned the empty set and was relaxed by amendment, in the open | two measured causes, recorded in the ruler specification (§12) |
| Why is the fixed-lock session proposed rather than run? | It is the next campaign, and this record's remit is the 2025 data | every descoped item names its fixed-lock revival condition (§12) |
| Where are the raw traces? | Held privately, with the manifest and every certifying check shipped | what runs here certifies the analysis, and what cannot is stated (§12) |
| Was the residual width collisional? | Treated as a residual floor, with the inelastic channel a recorded candidate | the evidence spans four documents, indexed in §12 |
| Is one light-shift coefficient across three sessions legitimate? | The pooled construction stays quoted, with the assumption recorded rather than asserted | the coefficient goes as one over the waist squared and no per-session waist was measured (§13) |

---

## 1. The total width is the observable, and the split carries its error and correlation

The composite line is a Lorentzian (natural + collisional, `gamma_coll`)
convolved with Gaussian-like components (laser width `sigma_laser`, transit).
A single-condition fit returns both, strongly anti-correlated at
`corr(sigma_laser, gamma_coll) ~ -0.9`, closure-measured at SNR ~ 130
([linefit.py:37](../rb5s6s/linefit.py#L37)):

> the TOTAL Voigt width (their combination) is robust and the individual split
> is not, so never quote a single-condition sigma_laser or gamma_coll as physics
> without its error and this correlation.

From `results/linefit_conditions.csv`, 20 conditions at one temperature (four
peaks × five powers), where the width was measured flat against power (C3a):

| quantity | range across the 20 | median error | largest error |
|---|---|---|---|
| total FWHM (the observable) | 5.28 – 5.71 MHz (8%) | 0.056 MHz (1.0%) | 0.17 MHz |
| `gamma_coll` (a component) | 0.249 – 0.695 MHz (2.8×) | 0.077 MHz | 0.33 MHz |
| `sigma_laser` (a component) | 0.216 – 2.056 MHz (9.5×) | 0.222 MHz | 1.11 MHz |

The extremes of both component ranges come from the 25 mW conditions, whose own
errors run three to five times the median. The largest `sigma_laser` error,
1.11 MHz, exceeds that column's median *value*. The wide ranges and the large
errors are one fact, not two.

![the degeneracy against the observable](../figures/fig10_degeneracy_vs_observable.png)

*Left: each condition's 1σ error ellipse from its own covariance, over contours
of constant total FWHM. The ellipses are elongated along the contours, two of
the twenty reaching unphysical negative widths, and the centres scatter in the
same direction, with a median correlation coefficient of −0.90 between the two
widths. Right: the quantity actually measured, the fitted total width, known to
1.0 per cent within a condition. No trend with laser power survives the scatter
between measurement blocks, which is several times larger than the plotted bars.
All twenty conditions are at 130 °C, so what the figure shows is that the total
is measured while its decomposition is not.*

**Decision: the estimator uses only the informative direction.** `beta_self`
rides on the *difference* in `gamma_coll` across temperature, the headline
bound uses the ×52.5 lever of the four-point 70/90/110/130 °C construction
(since 2026-08-02, where it was the ×16.2 lever of the 70 to 110 °C three-point
construction, see §9) and not on any absolute per-condition value
([linefit.py:40](../rb5s6s/linefit.py#L40)).

[M12](../rb5s6s/identifiability.py) maps the degeneracy: the χ² surface is
profiled over the (`gamma_coll`, `sigma_laser`) plane with every other parameter
re-minimised at each point ([fig7](../figures/fig7_identifiability_profile.png)),
giving

> the dataset constrains the TOTAL width well but the SPLIT poorly, so the
> individual coefficients are w0-conditional bounds, not measurements
> ([identifiability.py:37](../rb5s6s/identifiability.py#L37))

The local covariance is a quadratic approximation at the optimum and so
"cannot exclude a curved ('banana') valley or a second minimum"
([identifiability.py:27](../rb5s6s/identifiability.py#L27)), and the global map
tests whether the free fit is one of several near-degenerate optima
([run_identifiability.py:265](../scripts/run_identifiability.py#L265)).

### 1.1 Constraining the fit relocates the degeneracy

The natural response is to impose physics: tie `gamma_coll` to `beta * N(T)`,
with `N(T)` from Nesmeyanov's liquid-Rb vapour-pressure correlation as tabulated
by Steck ([density.py:9](../rb5s6s/density.py#L9)), share `sigma_laser`, and let
the constrained fit report smooth curves. That is
[M4b](../rb5s6s/global_fit.py).

The constrained fit then produces a `sigma_laser(T)` rising to 1.5–1.6 MHz at
70/90 °C and dropping to 1.06 at 110 °C, while the *free* per-condition value is
flat at 1.0–1.2. The rise is not a measured laser drift:

> that σ_laser(T) trend is the **β↔σ_laser degeneracy** under the density
> constraint, NOT a physical laser drift, so the trend is a model artifact,
> not a stale block ([RESULTS.md](RESULTS.md) M4c)

A smooth curve from a constrained fit is not better evidence than a scattered
one from a free fit. The same missing information has been redistributed into a
parameter where it resembles physics. `fig5`'s panel-B title names the
degeneracy on the plot itself
([make_figures.py:267](../scripts/make_figures.py#L267)), and §2 is why the
constrained fit is a cross-check.

---

## 2. The model-independent bound is the headline, and the global fit is a cross-check

Two estimates of `beta_self` exist: a model-independent width-versus-density
slope, and the hierarchical global fit, which is tighter. The tighter one is not
the headline.

> its beta is the best MODEL-BASED cross-check of the model-independent
> raw-width bound (M4), not a replacement for it
> ([global_fit.py:37](../rb5s6s/global_fit.py#L37))

M4's own producer says the same about its error bars, and gives the mechanism:

> the dataset's four-point lever BOUNDS beta_self (it does not measure it). The
> global-fit sigmas above are OVERCONFIDENT, since they assume one shared sigma_laser
> across blocks and so omit exactly this between-block drift.
> ([run_beta_self.py:396](../scripts/run_beta_self.py#L396))

Between-block width scatter (residuals ~0.06–0.16 MHz) is the dominant error:
laser drift over the cooling session is comparable to the collisional trend
itself.

The per-temperature `sigma_laser` sharing was originally justified by the four
peaks having been acquired close together in time. A recovered acquisition clock
measured the blocks **54–76 minutes apart** ([RESULTS.md](RESULTS.md)). The
sharing may still hold, and that justification does not.

## 3. The model ladder declines the AC-Stark parameter

The AC-Stark ramp is this programme's own proposed component. On the dataset
the ladder rejects it
([06_the_statistics.md](methods/06_the_statistics.md)):

> **A→B ≈ +1700** (transit decisively warranted), **B→C ≈ +435** … and **C→D
> ≈ −100**, so *the free AC-Stark parameter is decisively NOT warranted*

> A model-comparison that *declined* to add the AC-Stark term is the statement
> of "we do not claim to have measured it here."
> ([model_ladder.py:30](../rb5s6s/model_ladder.py#L30))

On synthetic data under a stable lock the same ladder decisively warrants an
injected Stark shift ([run_model_ladder.py:12](../scripts/run_model_ladder.py#L12)),
so the null is a property of the drifted dataset and not of the ladder's
sensitivity: the free per-scan centres, which the drifting lock forces, absorb
the ramp's pull.

## 4. The shared-versus-independent verdict flips with the sample counting

[M14](../rb5s6s/sharing_bic.py) scores shared against independent `sigma_laser`
by BIC. Counting the ~49k correlated samples as independent favours the free
model (ΔBIC ≈ −46), and the effective sample size favours the shared one
(ΔBIC ≈ +62). The effective-N version is the statistically correct one and is
the primary number. The sign flip bounds what the dataset can settle: it does
not robustly resolve shared against independent
([sharing_bic.py:37](../rb5s6s/sharing_bic.py#L37)).

A favourable score would not have meant much either:

> dBIC > 0 reads "the dataset cannot justify per-block freedom" (Occam on
> underpowered data), NOT "the sharing is confirmed"
> ([sharing_bic.py:36](../rb5s6s/sharing_bic.py#L36))

The in-sample check (M4c) returns χ²/dof of 0.19/0.58/0.33, all *below* one,
so the error bars are too large for the test to discriminate.
[RESULTS.md](RESULTS.md) records the sharing as "**untested**, not merely
unverifiable."

## 5. An aborted power block stays excluded

A first attempt at the 993.4154 nm 130 °C power sweep was aborted and redone in
full. Three reasons keep it out
([annotate_manifest_qc.py:62](../scripts/annotate_manifest_qc.py#L62)): it is
**redundant**, because the canonical sweep covers all five powers and the
partial retry only 25/125/225 mW. Its 225 mW set "carries a ~80x steeper
baseline slope (high-power drift, the likely abort cause)". And it was cut
before unblinding.

The lines are individually clean, matching the redo in height and width to
within 2%, and re-admitting them tightens the S0 bound while leaving `beta`
untouched:

> re-admitting previously-cut, drift-flagged data to improve a number is
> declined

Both bounds are recorded. (The specific pair quoted in that comment, 2.04 →
1.92 MHz, predates the switch to a profile-likelihood construction, and the current
dataset's bound is **0.63 MHz** at 225 mW, `results/stark_sweep.csv`. The
comment's numbers need refreshing, the decision does not.)

A pre-registered prediction was voided rather than scored when its corroborating
wavemeter photographs turned out to lie outside the campaign window
([PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md)), and the audit script
enforces the void on the integrity gate
([run_timestamp_audit.py:23](../scripts/run_timestamp_audit.py#L23)).

## 6. Withdrawn claims stay on the page

Six readings were withdrawn after publication in the pre-registration record.
Each withdrawal is recorded in place, next to the reading it replaces, with the
direction of the error ([PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md)).

Novelty claims have retreated twice. The prior-art assessment of Wall 2014 was
downgraded from "scooped" to "distinct" after the paper was read in full, and
the entry lists five specific distinctions: purely numerical treatment,
inference running the opposite direction, longitudinal rather than transverse
geometry, per-plane lines peaking at the maximum shift, and a regime where the
shift far exceeds the linewidth ([lit/wall2014.md](lit/wall2014.md)).

An earlier note claimed the transit Monte Carlo had two bugs and inferred
w0 ≈ 90 µm, and that inference is retracted in place
([notes/transit_width_resolved.md](notes/transit_width_resolved.md)).

## 7. Guards added after specific failures

Most of the suite's guards are regression guards for mistakes that were made:

- a freshness guard, because a physics fix moved `beta` from 0.056 to 0.036 and
  stale figures survived it, "found only by accident"
  ([test_figures_fresh.py:4](../tests/test_figures_fresh.py#L4)).
- a canonical-value guard, because one replaced number lingered "in eight
  files" ([test_docs_canonical.py:21](../tests/test_docs_canonical.py#L21)).
- that guard's ±4-line window was widened after a planted violation was
  "satisfied by the very correction note explaining the reversal"
  ([test_docs_canonical.py:428](../tests/test_docs_canonical.py#L428)).
- an asymptotic w0 → ∞ test, after an external adversarial review found it untested
  ([test_transit_mc.py:119](../tests/test_transit_mc.py#L119)).
- an SVG canonical-number guard, because the hand-authored bench schematic
  quoted a waist matching no value in the record and asserted the retro ratio
  at 1, invisible to both the figure guards and the markdown scan
  ([test_svg_canonical.py:1](../tests/test_svg_canonical.py#L1)).

[M19](../rb5s6s/ramp_transit.py) came from an objection in
[Camparo and Lambropoulos 1992](lit/camparo1992.md): a distribution of light
shifts skews a line only when sampled slowly compared with the atomic response.
Atoms in flight sweep their own shift within a transit time (~0.2 µs) only a few
times 1/Γ (~45 ns), and the ramp/transit factorisation had assumed the answer.
M19 propagates the weak-excitation amplitude along each trajectory with no
quasi-static step: the first two moments reproduce the static triangle to ~0.1%
across S₀/transit-FWHM = 0.09–7.6, and the result holds under the retro standing
wave and a thermal spread of speeds. **κ₃ is not resolved**, because the
ν³-weighted FFT noise floor swamps it, and κ₃ is the moment the asymmetry claim
rests on.

## 8. What is not modelled, and what would revive it

Eight load-bearing assumptions are listed as a numbered attack surface
([08_assumptions_and_outlook.md](methods/08_assumptions_and_outlook.md) §6), and
individual assumptions are also flagged at the point of use. The retro ratio
is assumed at ρ = 0.94 ± 0.04 rather than at the design value 1, and the transit
kernel's *shape* is "untested by the dataset and … a genuine attack
surface."

Descoped items carry the condition under which they return: the EOM modulation
index is dropped because the 2025 drive voltage was never recorded, and revives
in a fixed-lock session ([beta.py:8](../rb5s6s/beta.py#L8),
[PLAN.md](PLAN.md)). The waist w0 remains **OPEN**, and the config module warns
at the point of use, at "Do not quote a number built on this without the w0
caveat" ([config.py:286](../rb5s6s/config.py#L286)). Every absolute result is
conditional on it.

Two negative results: no Rb 6S self-broadening coefficient exists in the
literature after four independent search framings, and Russian-language coverage
could not be closed with the tools available, which is a limitation rather than
an absence
([lit/beterov1973.md](lit/beterov1973.md)).

## 9. The 130 °C point moves from a diagnostic to the headline (2026-08-02)

Through 2026-08-01 the `beta_self` headline used only the 70/90/110 °C
temperature sweep, three points at dof=1 with a ×16.2 density lever, and treated
the 130 °C power-sweep session's 225 mW block as an optional fourth lever
point, folded in only inside a separate, non-headline probe
(the fig19 trend audit, an internal working note). The
stated reason was that the 130 °C block looked like a different apparatus
configuration: a power sweep rather than a temperature sweep, calibrated off
before/after EOM ruler brackets rather than the T-session's own per-block
ruler.

**Decision: the 130 °C point is folded into the headline.** On firsthand
knowledge of the bench, the 130 °C power-sweep session ran
in the SAME optical/cell configuration as the 70/90/110 °C temperature sweep
with the same beam path, the same cell and the same detection chain. That
removes the
"different configuration" objection. What genuinely differs between the two
sessions is the acquisition epoch and the axis calibration, and the
calibration difference is already handled PER SESSION: `load_t_rates()`
derives the T-sweep rate from the T-session's own per-block ruler and the
P-sweep rate from the P-session's before/after bracket combination
independently, so combining the two onto one shared density axis carries no
unhandled calibration mismatch. There is no remaining reason to keep 130 °C
out of the headline, and no separate three-point construction is kept
alongside it, so it is one licensed construction and one bound per peak
([run_beta_self.py](../scripts/run_beta_self.py), module docstring).

The four-point construction (70/90/110/130 °C, dof=2, ×52.5 density lever)
tightens the per-peak 95% bound by roughly an order of magnitude, from
≲0.2–0.4 to ≲0.03–0.05 MHz per 10¹² cm⁻³, and the physics reading gets
stronger with it: `rb5s6s/lever_crosscheck.py` had already noted that folding
in the 130 °C anchor pulls the fitted slope down because `gamma_coll(T)`
barely grows across the full lever, which is a residual floor rather than
resolved collisions, and that is a cleaner demonstration with the full ×52.5 span
than with the ×16.2 one. What does NOT change: the bound still sits an order
of magnitude above the ~3.5 kHz expectation anchored on the measured 7S
self-broadening rate ([BIG_PICTURE.md](BIG_PICTURE.md) §1), so a same-session
150 to 170 °C extension remains worth doing, not to combine extreme lever
points at all (that objection is retired), but because a purpose-built
within-session lever removes the cross-epoch calibration step this fold-in
relies on, and reaches densities where a genuine collisional effect could
clear the block-noise floor ([PLAN.md](PLAN.md) §7).

## 10. Three decisions from the same joint-refit night (2026-08-03)

Recorded together because the fold-in reviews them as one commit.

**Decision: the four-point `beta_self` lever, already decided in §9, gets
the code that had not caught up to it.** The promotion of the
70/90/110/130 °C construction to the sole headline (dof=2, the ×52.5 lever,
the same-configuration fact and the instrument authority both recorded in
§9) was a documentation decision before it was a code one. `rb5s6s/beta.py`
and `rb5s6s/coverage.py` still ran the three-point, dof=1 machinery through
the night §9 was written. Both now compute dof=2 from the four-point lever
directly ([beta.py:114](../rb5s6s/beta.py#L114),
[coverage.py:42](../rb5s6s/coverage.py#L42)), so the coverage study that
certifies the bound's 95% claim tests the construction the headline
actually reports, not its retired three-point predecessor. No separate
construction is kept alongside it, matching §9's own statement of the
decision.

**Decision: the per-(session, peak) `sigma_laser` split takes a shrinkage
prior sized from the evidence that motivated it, not from convenience.** A
free-Gaussian-sigma probe on the brightest trace per peak
(the fig16 residual-asymmetry working note, "Seventh addition")
found the pooled-per-block `sigma_laser` too coarse at camp130: −85 kHz
(4121), −121 kHz (4154), −287 kHz (4192) and +97 kHz (4207). Their mean
absolute size, 147.5 kHz, rounded to the 150 kHz prior width that now pulls
every `sigma_sp` cell back toward its block's mean
([run_global_dataset_fit.py:211](../scripts/run_global_dataset_fit.py#L211)).
The joint refit reproduces the probe's own ordering at camp130 (−14, −36,
−57 and +107 kHz across the same four peaks), at the smaller amplitude the
prior was built to allow, which is the validation the probe alone could not
give itself: a number chosen from one free fit, checked against a second,
independent fit constrained by it.
[PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md) addendum 21's third
postscript carries the full comparison.

**Decision: the campaign-morning axis nuisance takes the measured prior in
place of the assumption box.** `pilot_rate_scale` used to float inside a
flat [0.9, 1.1] box and had drifted to 1.02–1.03 in earlier fits. M26's own
ruler day measures it directly, at 1.0022(12) from 27 rulers, and the refit
now uses a tight ±5σ box around that number, [0.9962, 1.0081], in its place
([run_global_dataset_fit.py:312](../scripts/run_global_dataset_fit.py#L312)).
The posterior comes out at 1.0081, indistinguishable at this precision from
that box's own upper edge. The measurement is doing the constraining now,
not an assumption, and the fit still wants a rate above what the
measurement allows. Whether that gap is the axis or absorbed width physics,
the question the module docstring poses, stays open.

---

## 11. A profile is only as good as its local minimum, so the minimum search now leads (2026-08-03)

The four-point joint refit's primary chain, started cold, parked in a false
minimum 283,000 chi-squared units above the solution every other chain in
the same run found, and its headline row and direction row were computed on
that stuck profile. The run's own campaign-only column moves by four units
of that 283,000 between the stuck solution and the true one, so the excess
sits outside the campaign data, consistent with the 4 July evening
session's free centres, the exact warm-up failure mode the fitter's own
docstring had documented from an earlier run, striking the primary variant
this time. Two structural
decisions follow.

**Decision: the wing variant runs first and seeds every other family.** A
cold start finds the true local minimum reliably only with the wing free, so the
chain order in [run_stark_joint.py](../scripts/run_stark_joint.py) now puts
the wing variant first and seeds the primary from its solution with the
wing entries stripped, in addition to the primary's own cold chains, with
the pointwise minimum kept. A seed can only improve a profile, so this
closes the failure mode for every family at once rather than patching the
variant it last struck.

**Decision: no cold-start profile is quoted without a seeded twin.** The
previous run's direction row compared a stuck profile against a converged
one and printed 283,135 where the physics answer, measured in the true
local minimum, is indifference. Any future variant added to the fit inherits the
same rule: its profile enters the CSV only after a seeded chain from the
best known local minimum has confirmed or improved its minimum.

The corrected rerun produces the CSV of record. The invalid run's numbers
never entered a document, and the incident's full account, including what
the corrected numbers turn out to be and whether the earlier three-point
primary needs the same correction, goes to the results report as addendum
24 when that run lands.

---

## 12. Decisions argued in their home documents

Five load-bearing judgement calls live where their evidence lives. An
external review found that a reader of the table above would not learn
they exist, which was true. This section is the missing index, and each
entry stays short because the argument is already written elsewhere.

**The pooled slope.** Whether the four lines share one self-broadening
slope was decided by a preregistered probe
([notes/beta_self_pooling_prereg.md](notes/beta_self_pooling_prereg.md)):
predictions stated before the pooled number existed, scored after it
did, all holding, one of them by a different mechanism than the note
had argued. The note's postscript carries both the adoption and the
surprise.

**The six-tooth ruler figure.** The figure's original eligibility
clause demanded all seven comb teeth standing and returned the empty
set. Amendment 4 of
[notes/ruler_validity_and_trim_prereg.md](notes/ruler_validity_and_trim_prereg.md)
records what the clause returned, the two measured causes, the options
put to the author, and the relaxation to six standing.

**The fixed-lock session.** Proposed, not run: [PLAN.md](PLAN.md) is
the full protocol, and §8 above shows the recurring pattern that a
descoped item names a fixed-lock condition as what would revive it.
The deferral is a scope decision of this record, not a gap in it.

**The raw traces.** Held privately, with the manifest and every
certifying check shipped. The repository [README](../README.md) section
on the raw traces and the manifest row of [DATA.md](DATA.md) state
exactly what reproduces without them and what cannot.

**The collision question.** Whether the fitted collisional width is
resolved collisions is answered across four documents, and this entry
exists so a reader finds all four:
[methods/06](methods/06_the_statistics.md) shows the near-flat trend
against the linear scaling a real binary-collision width requires,
[RESULTS.md](RESULTS.md) item C3g closes the collisional wing with the
density lever, the difference-potential note
([notes/vdw_difference_potential_and_4d_channel.md](notes/vdw_difference_potential_and_4d_channel.md))
records the open inelastic channel as a candidate mechanism rather
than a claim, and §8 above lists what staying unmodelled costs.

**The model-selection panel.** How much model the data may buy was
decided by BIC alone wherever it was decided at all, with no stated
reason against the alternatives. As of 2026-08-15 every complexity
comparison reports a panel of four criteria numerically (AIC, AICc,
BIC over raw $N$, BIC over the effective sample size), preregistered in
[notes/model_selection_prereg.md](notes/model_selection_prereg.md)
before any recomputation. The judgement call is in the treatment of
disagreement: a split panel is published as a fact about the data
(the ranking is convention-sensitive at this sample size) and never
broken by taste, and adopting a richer model on a split requires an
independent predeclared basis. The reasoning that makes this a real
choice here is the spread of $\ln N$ across the record's decision
sites, from 2.3 to 12.9, worked in
[methods/06](methods/06_the_statistics.md) §4.7a.

---

## 13. One coefficient is shared across three sessions, and the geometry that licenses it is untested (2026-08-17)

The joint light-shift fit pools 100 campaign traces with 46 from the 4 July
rehearsal and 26 from the campaign-morning session of 17 July, and shares one
coefficient across all three. Every other session difference in that fit has a
nuisance assigned to it: a laser width per session per peak, a detector
saturation per instrument, a fitted scan rate for the rehearsal, and a rate scale
bounded to ten per cent for the campaign morning.

**The decision is to keep the pooled construction as the quoted one, and to
record what it assumes rather than to assert that the assumption holds.**

The assumption is specific. The coefficient scales as one over the beam waist
squared, so a session recorded at a different focus has a different coefficient,
and none of the nuisances above is the waist. That the three sessions ran in
different CONFIGURATIONS is established from their own receipts. That they shared
a GEOMETRY is untested, because the archive holds no per-session waist
measurement.

Two committed diagnostics show the pooled surface behaving badly.
`results/stark_joint.csv` records the largest disagreement between the two scan
directions as 8.59 in chi-square, against the 2.706 at which the bound itself is
read, so the convergence error is about three times the quantity being measured.
And the rehearsal's 270 mW rung carries 1.44 times the campaign's largest
squared-shift lever while the pooled bound sits looser than its own campaign-rows
column, which is the opposite of what adding a longer lever to a measurement of
one quantity does.

**The rejected alternative was to promote a campaign-only construction on the
strength of those diagnostics.** It was rejected for now because a badly behaved
likelihood surface is a statement about the surface rather than proof that the
sessions saw different coefficients, because no campaign-alone refit is in
`results/`, and because replacing a published number with none is a loss. The
reasoning, the six questions it generalises to, and the boundary of the claim are
argued in
[big_picture/08](big_picture/08_when-a-joint-fit-is-legitimate.md).

The cross-peak half of the same question is settled differently and more
comfortably. Sharing across the four hyperfine components is a physical statement
because the light shift is blind to the hyperfine index, the one known peak
difference is calculable at about 4 kHz against an 88 kHz scatter, and the fit
statistics are reported as a check rather than as the licence, following the
template of [the pooled-slope
probe](notes/beta_self_pooling_prereg.md). Where those statistics are asked to
decide, they do not: §4 above records the same verdict flipping with the sample
counting.

---

## Status vocabulary

Statuses are attached by [a script](../scripts/annotate_results_status.py), so a
status cannot be strengthened without changing the producing code.

| status | meaning |
|---|---|
| `MEASURED` | a measurement with its error |
| `BOUND` | an upper/lower limit, conditional on the OPEN w0 and/or the model |
| `NULL` | a test performed that returned no effect |
| `PRELIM` | computed, not yet load-bearing |
| `ENVELOPE` | an order-of-magnitude scale, not a fitted value |
| `DIAGNOSTIC` | an internal check, not a physics claim |
| `ARTIFACT` | a feature identified as non-physical |

`beta_self`, `sigma_laser` and the AC-Stark `S0` are all **BOUND**.

## 14. The width concavity is withdrawn to provisional, 2026-08-18

**The decision.** A concave curvature of the linewidth against power, carried
since 2026-08-17 as a measured diagnostic, is reclassified as PROVISIONAL and
is not an established physical effect. The EOM thermal-lens channel, which was
inventoried as its candidate mechanism, is demoted with it.

**What forced it.** The curvature reaches 4.8 standard deviations only on
within-cell errors and falls to 1.4 under the between-block treatment this
record's own width channel already uses for the collisional slope. Neither
independent power ladder confirms it: the 2025-07-17 pilot's non-monotone
ladder gives the same sign at 1.2, and in the 2025-07-04 rehearsal a width
trend appears on the descending ladder while both ascending ladders show none,
which is order dependence rather than power dependence. Section C3a of the
results ledger had said from the beginning that the width's power variation is
block scatter, and that reading is now tested rather than asserted.

**The rejected alternative** was to keep the concavity as a measured
diagnostic with a caveat, on the ground that its sign agrees across sessions
and that the pilot test is underpowered. Rejected because a diagnostic that
has motivated a channel sweep, a component-resolved decomposition and a
mechanism hypothesis is not a caveated number in practice, whatever its label
says, and because the same evidence standard applied to the amplitude channel
in the same session let that finding through. Applying one standard to two
channels and reporting the different outcomes is the point.

**What does not change.** No committed number moves, because no published
bound rested on the concavity. The component-resolved sweep's own finding, that
the three width kernels are interchangeable in the power channel, is unaffected
since it is a statement about the model rather than about the concavity.

**What would settle it.** An interleaved power ladder, which removes the
power-time collinearity at the source. See
[the acquisition-settings chapter](plan/07_acquisition-settings.md).
