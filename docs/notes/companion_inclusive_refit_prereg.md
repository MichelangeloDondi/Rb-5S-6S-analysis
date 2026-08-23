# Putting the three companions inside the model: specification of record

**Status: pre-registered 2026-08-10, before the code was written and before any
number came out of it.** Every prediction below is stated with its arithmetic so
the run can only confirm it or fail it.

`provenance: NO_PRODUCER` - Lines 1 to 181 preregister. The postscript reports what `run_companion_refit.py` returned, and that script contains exactly one `open()` call, a READ, with every output a `print()`. The note says so itself: "prints its results and persists none of them". It is also absent from `run_all.sh`. Two prereg-side factors (2.8 and 2.21) come from `run_saturation_probe.py`, which since 2026-08-23 persists its C3d half into `results/saturation_companion.csv` and deliberately persists no joint figure, since that fit needs trees outside this repository. **15 numeric claims on this page remain unaccounted for.** Recorded 2026-08-23 by an audit that read every numeric claim on this page against `results/` and `scripts/`. See `docs/HISTORY.md`.


**The question.** The fits of record quote the light-shift bounds with a stated
looseness, because three width-adding effects sit outside the forward model on
purpose. What happens when they go inside it?
**Takes.** [notes/two_photon_saturation_companion.md](two_photon_saturation_companion.md)
for the two companions and their measured sizes,
[methods/06_the_statistics.md](../methods/06_the_statistics.md) for the fitting
machinery, and [notes/full_archive_fit_prereg.md](full_dataset_fit_prereg.md)
for the trace census this reuses unchanged.
**Gives.** The model change, the construction that could separate the pumping
term from the other two, five numbered predictions, and the stop conditions.
**Skip if.** You want the result rather than the contract it was run under.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

Producers when it runs: `scripts/run_stark_sweep.py` (the five-trace and
twenty-trace fits behind fig21 and fig22), `scripts/run_stark_joint.py` (C3f),
`scripts/run_global_archive_fit.py` and `scripts/_m25_norulers.py` (M25, both
arms). No new script. The change is a model option, off by default, so the
committed numbers are reproducible from the same tree that produces the new
ones.

## 1. Why this is not a bug fix

Nothing below corrects an error. The three effects are absent from the fitted
model by a decision that is recorded in the results ledger and in the outbound
correspondence: injecting them means adopting a two-level homogeneous
saturation law driven by a two-photon Rabi frequency, which is standard practice
and is not derived for this level structure. The bounds are therefore quoted as
they stand with the looseness and its measured size attached.

Putting the companions inside the model retires that framing, and that is the
cost. It buys a bound that is not loose, conditional on a saturation law this
record has not derived. **Which of those two is the better thing to publish is
an owner decision and this note does not take it.** What this note fixes is
what the run would have to show for the question to be worth putting.

## 2. What enters the model, and how

Three terms, all of which broaden the Doppler-free core without moving its
centre.

**Saturation.** The extra homogeneous width
$\Gamma(\sqrt{1+s}-1)$ with $s=2\Omega^2/\Gamma^2$, exactly the function already
committed as `saturation_increment_mhz` in `scripts/run_saturation_probe.py`.
It carries the conversion from the shift to the Rabi frequency, which is the one
number in the chain the record gives as a band (1.24 to 1.30) rather than a
value, so **every prediction below is stated at both ends of that band.**

**Hyperfine pumping.** An atom that decays mid-transit cascades through 5P,
whose decay does not preserve $F$, and can land in the ground level that is not
being driven. The width this adds is $f$ times the saturation width exactly,
with everything else cancelling, and $f$ is the cascade branching into the
undriven level. It is **per line** and fixed, not free:

| line | isotope, driven $F$ | $f$ |
|---|---|---|
| 993.4121 nm | $^{87}\text{Rb}$, $F=1$ | 0.3725 |
| 993.4154 nm | $^{85}\text{Rb}$, $F=2$ | 0.3476 |
| 993.4192 nm | $^{85}\text{Rb}$, $F=3$ | 0.2483 |
| 993.4207 nm | $^{87}\text{Rb}$, $F=2$ | 0.2235 |

These come from the full Zeeman manifold with every Clebsch-Gordan coefficient
present (`scripts/run_zeeman_depletion.py`), which also verified that the
branching is $m_F$-independent to $3\times10^{-16}$, so $f$ is a number and not
a function of how far into its transit an atom is.

**Depletion.** The same pumping shortens the interaction time, 2.02 to 3.34 per
cent per crossing at the signal-weighted rate, per line and now per isotope. It
multiplies the transit kernel rather than adding a Lorentzian, because it is a
loss of interaction time and not a loss of coherence.

**Not entering: the isotope transit split.** It is available as
`transit_fwhm_at_T(..., isotope=)` and stays off, for the reason measured in
[methods 2.5](../methods/02_the_lineshape.md): against density it is 0.41 per
cent of one sigma on $\beta_{85}-\beta_{87}$, so switching it on would produce a
diff with no physics in it. Prediction 5 makes that falsifiable rather than
assumed.

## 3. The construction that could separate the pumping term

This is the reason the refit is interesting rather than mechanical. All three
terms grow as $P^2$ and all three grow as $w_0^{-4}$, so **no sweep this
apparatus can run separates them through a continuous knob.** The saturation and
the ramp are also identical on all four hyperfine lines, because the two-photon
operator here is scalar and the coupling is $F$-independent. The pumping is not.

So the separating construction is a joint fit over the four peaks with the four
$f$ above held **fixed** and one free scale $A$ multiplying them, where $A=1$ is
the computed companion and $A=0$ is its absence. Each line keeps its own free
core width, which absorbs any constant per-line offset, so what $A$ is read from
is the difference in the *power dependence* between lines. The lever is
$f_\text{max}-f_\text{min}=0.149$ of the saturation width, which is 3.06 kHz at
225 mW and at the committed $S_0$ bound of 0.217 MHz.

## 4. The five predictions

**Prediction 1, and it is the one that matters: $A$ will not be measured, and
the bound on it will be loose by a factor between 20 and 100.** The arithmetic
is a least-squares power calculation on the actual design, four lines by five
powers, with the four core widths free and one shared quadratic absorbing
everything common. Taking the single-block width scatter of 0.088 MHz as the
error on each width point gives $\sigma_A=42$, and taking the scatter reduced by
the five repeats in each block gives $\sigma_A=19$. So the archive would detect
its own computed companion at **0.02 to 0.05 sigma**, and a fit that rails at
zero returns $A\lt 31$ to $A\lt 69$ at 95 per cent one-sided.

That is a prediction of failure, and it is stated because the failure is
informative: it says the per-line lever is real, is the only separation this
method admits without a fixed lock, and is **twenty to forty times too small for
this dataset**. A session with the block scatter under control is what spends
it, and the factor above says how much control is needed.

**Prediction 2: the shared bounds tighten by the factors the probe already
measured, and by no more.** The width-only construction moves from 0.6325 to
about 0.23 MHz, a factor 2.8, and the joint C3f construction by 2.21. The refit
must reproduce those to within the ratio band, because it is the same law
applied inside the fit rather than around it. **A tightening much larger than
2.8 would mean the depletion term is doing more than the interaction-time
argument allows, and is a stop condition, not a result.**

**Prediction 3: adding the per-line term will not be preferred by BIC.** With
$A$ contributing 0.02 to 0.05 sigma, $\Delta\chi^2$ from freeing it is below 1
and the BIC penalty for one parameter over 100 width points is 4.6. So the
model comparison should prefer the four-line-shared form. If BIC prefers the
per-line model, something other than pumping is per-line, and the candidates are
already named in the record: differential radiation trapping, which is
monotonic in density and isotope-ordered, and the amplitude-ratio degeneracy
breaking of M7 and M10.

**Prediction 4: $\beta_\text{self}$ moves by less than its own interval.** The
companions are $P^2$ terms and $\beta$ is read from a density lever at fixed
power, so the two are orthogonal by construction. A $\beta$ shift larger than
its 95 per cent interval would mean the companions are stealing density-lever
width, which they have no mechanism to do.

**Prediction 5: switching the isotope transit split on moves
$\beta_{85}-\beta_{87}$ by less than 0.05 of its own sigma.** The computed value
is 0.41 per cent of one sigma. This is stated separately because it is the one
prediction that can be checked cheaply, by running the split arm alone, and
because it is the falsifiable form of the claim that the shared transit width
costs nothing.

## 5. Stop conditions

The run stops and reports rather than continuing if any of these fire.

1. The unpatched arm fails to reproduce the committed numbers exactly. That is
   the check that the option is genuinely off by default, and it is run first.
2. Prediction 2 fails upward, meaning a shared-bound tightening beyond about 3.
3. Any bound moves in the **loosening** direction. The companions add width at
   nonzero power and remove none, so a light-shift bound derived from width can
   only tighten. A loosening bound is a sign error.
4. The profile for $A$ is not smooth enough for the interval construction of
   [addendum 30](../PREREGISTRATION_RESULTS.md), which interpolates in
   $\sqrt{\Delta\chi^2}$ and refines until the interval spans four grid steps.

## 6. What is not run, and what would change that

The refit is not started while the two M25 arms are writing
`results/global_archive_fit.csv` and `results/global_archive_fit_norulers.csv`.

It is also not started before this note is committed, which is the point of
writing it.

## 7. What would falsify the whole framing

A per-line width difference in the power dependence, larger than the 3 kHz the
pumping predicts and ordered the way the four $f$ are ordered. That would mean
the pumping companion is much larger than the cascade branching says, which
would in turn mean the scalar-operator argument that puts 6S in a single
hyperfine level is wrong. The same argument is what makes the saturation term
$F$-independent, so it would not be a local repair.

---

## Postscript, 2026-08-11: what the run returned

**Everything above this line is the note as preregistered on 2026-08-10 and is
unchanged.** This section was added after the run and is the only part of the
file written with a result in hand. Producer:
`scripts/run_companion_refit.py`, which prints its results and persists none of them.

Read this first, because it reframes the rest of the postscript. **The central
prediction was not testable in the form it was written, and the reason it was
not is a better answer than the one the note asked for.** The scale $A$ is not
loosely determined by this dataset. It is unidentifiable in principle, for a
structural reason the preregistration did not anticipate and its stop-condition
list did not cover.

### Stop condition 1 passed, and it was checked first

The committed $S_0(225)$ bound is 0.632 MHz and the run with the option present
and off returns 0.632 MHz, a difference of zero at the precision the file
stores. The stronger form also holds: `scripts/run_stark_sweep.py` reproduces
the whole committed CSV byte for byte on the tree that carries the option. So
the option is inert by default, which is what every number below depends on.

One correction to a first version of the check, recorded because it is the kind
of error that reads as a result. It compared at a tolerance of $10^{-6}$ against
a value the CSV stores to three decimals, and stopped on 0.632 against 0.63250.
That was the file's formatting and not the model.

### Prediction 1: the archive cannot see the companion at all

The construction the note specifies is a joint fit over the four lines with the
four $f$ fixed and one free scale $A$. Run as written, with $\kappa$ free
alongside $A$, the fit drives $\kappa$ to zero and $\chi^2$ comes back identical
to four decimals from $A=2$ to $A=100$. That is not a loose profile. It is an
escape, and the mechanism is exact: $A$ enters only through
$A\times\text{sat}(S_0)$ with $S_0=\kappa P$, so at $\kappa=0$ the companion
vanishes identically and $A$ multiplies nothing.

Profiling the surface rather than cutting it makes the situation plain. Each
model is minimised over $\kappa$ on a 25-point grid with three starts each. The
null for a question about the pumping scale is **saturation only**, not
production, because $A$ scales the pumping term alone:

| model | $\hat\kappa$ (MHz/W) | $\chi^2$ | at $\kappa=0$ | $\Delta\chi^2$ vs the null |
|---|---|---|---|---|
| production, no companions | 0.4505 | 54.5737 | 55.5712 | −0.9974, better |
| **saturation only, the null** | 0.0000 | 55.5712 | 55.5712 | 0 |
| saturation + pumping, $A=0.5$ | 0.0000 | 55.5712 | 55.5712 | 0.0000 |
| saturation + pumping, $A=1$ | 0.0000 | 55.5712 | 55.5712 | 0.0000 |
| saturation + pumping, $A=2$ | 0.0000 | 55.5712 | 55.5712 | 0.0000 |
| saturation + pumping, $A=4$ | 0.0000 | 55.5712 | 55.5712 | 0.0000 |
| saturation + pumping, $A=8$ | 0.0000 | 55.5712 | 55.5712 | 0.0000 |
| saturation + pumping, $A=16$ | 0.0000 | 55.5712 | 55.5712 | 0.0000 |

$\Delta\chi^2$ is **exactly zero at every scale from 0.5 to 16**, not merely
equal to four decimals, because every one of those fits sets $\hat\kappa=0$ and
thereby switches the companion it is supposed to be measuring back off. There is
no bound on $A$ to quote and no profile to interpolate one from.

The fourth column is an exact self-check rather than a result. Both companions
are proportional to $S_0=\kappa P$, so at $\kappa=0$ they must vanish and every
row must return the production $\chi^2$. Every row does.

The first row is a separate fact and it is worth not confusing with the others.
Production, with no companion of either kind, fits 0.9974 better than the null,
which is the archive preferring no **saturation** term at 1.00 sigma. That says
nothing about the pumping scale, which is what the last six rows are for.

The reason is one the note should have seen in advance and did not. **This
archive does not measure $\kappa$, it bounds it from above**, and $\hat\kappa=0$
sits inside the allowed region. A coefficient multiplying a term whose own
amplitude is consistent with zero cannot be measured at any precision. The
preregistration's power calculation evaluated the per-line lever "at 225 mW and
at the committed $S_0$ bound of 0.217 MHz", which is to say at the bound,
treating $\kappa$ as though it were known to sit there. It is not known to sit
there, and that is the whole difference between $\sigma_A=19$ to 42 and no
$\sigma_A$ at all.

Holding $\kappa$ at the value the polarizability predicts, 1.5447 MHz/W, does
produce a profile: $A\lt 0.3$ at 95 per cent one-sided, with the computed companion
at $A=1$ disfavoured at 2.881 sigma. That number is real and it is conditional,
and the condition is not satisfied. At $A=0$ the same fit prefers
$\hat\kappa=0.4505$, so pinning at 1.5447 costs 3.51 units of $\chi^2$ before any
companion is added. **A bound conditional on a value the data disfavours is not
a bound on the physics**, and it is recorded here as the second reading of one
surface rather than as a competing result.

So prediction 1's conclusion survives and is understated. The note predicted the
archive would see its own companion at 0.02 to 0.05 sigma and return
$A\lt 31$ to 69. It sees it at nothing and returns no bound.

### Prediction 2: the stop condition fired, and the threshold was mis-specified

| ratio | $S_0(225)$ ub95 | tightening |
|---|---|---|
| 1.2367 | 0.2106 | 3.00 |
| 1.2951 | 0.2041 | 3.10 |

Stop condition 2 calls a tightening beyond about 3 a stop rather than a result,
so as worded it fired on both ends of the ratio band. The run stopped and
reported, nothing was written, and no committed bound moved.

The threshold itself is the defect. The 2.8 was measured for **saturation
alone**, by `scripts/run_saturation_probe.py`. This run carries saturation
**and** hyperfine pumping, which multiplies the homogeneous companion by
$1+f$ with $f$ between 0.223 and 0.372, so between 22 and 37 per cent more
width by construction. A tightening above 2.8 is therefore expected here and the
stop condition as written cannot distinguish that from the failure it was meant
to catch. The right threshold would have been stated against the two-companion
width, and it was not, because the note reused a one-companion number without
saying which model it belonged to.

This is a defect in the preregistration's wording, not a finding about the
physics, and it is recorded as one. It is also the reason the fired stop
condition was reported rather than acted on.

### Prediction 3: confirmed, by the widest possible margin

Freeing $A$ buys $\Delta\chi^2=0$, so no information criterion of any kind can
prefer the per-line model. The prediction is confirmed and the mechanism is
stronger than the one predicted: not a small $\Delta\chi^2$ against a penalty,
but no $\Delta\chi^2$ at all. Note the shape of this. $A$ has no
maximum-likelihood value here, because the likelihood is flat along its axis
rather than peaked at zero, and a parameter that cannot be estimated also cannot
be paid for.

One arithmetic slip in the prediction as written. It states the BIC penalty as
"one parameter over 100 width points is 4.6", while the design it specifies and
this run uses is four lines by five powers, which is 20 points and a penalty of
3.0. The conclusion is unaffected.

### Predictions 4 and 5 were not scored by this run

Prediction 4 concerns $\beta_\text{self}$, which is read from a density lever
that the twenty-point stark sweep does not contain. Scoring it needs
`scripts/run_global_archive_fit.py` with the option on, which is a run of about
ten hours and has not been made. **It is open, not passed.**

Prediction 5 was computed independently on 2026-08-10 by
`scripts/run_zeeman_depletion.py` check 5, before this run and by a separate
route: switching the isotope transit split on moves $\beta_{85}-\beta_{87}$ by
0.41 per cent of one sigma against a predicted ceiling of 5 per cent. It holds,
and it holds on that calculation rather than on this one.

### What the stop-condition list was missing

The four stop conditions cover the option leaking into production, the shared
bound moving too far, a bound moving the wrong way, and a profile too rough for
the interval construction. **None of them covers the case that actually
occurred**, which is a parameter that is not merely poorly constrained but
structurally unidentifiable, so that the fit returns a profile-shaped object
carrying no information. The symptom in this instance was distinctive and easy
to check: $\chi^2$ identical to four decimals across a factor of fifty in the
parameter. A future preregistration of this shape should carry a fifth stop
condition testing for it, and the test is one line, since an unidentifiable
parameter leaves $\chi^2$ flat along its own axis.

The general form is worth stating plainly, because it is not specific to this
fit. **A term that enters the model only as a multiple of another term must be
identified jointly with it, and if the multiplying term is itself only bounded,
the product is the only thing the data constrains.** The record already says
this about the three same-signature broadeners in the two continuous knobs. It
turns out to apply to the per-line construction that was supposed to escape it.
