# Putting the three companions inside the model: specification of record

**Status: pre-registered 2026-08-10, before the code was written and before any
number came out of it.** Every prediction below is stated with its arithmetic so
the run can only confirm it or fail it.

**The question.** The fits of record quote the light-shift bounds with a stated
looseness, because three width-adding effects sit outside the forward model on
purpose. What happens when they go inside it?
**Takes.** [notes/two_photon_saturation_companion.md](two_photon_saturation_companion.md)
for the two companions and their measured sizes,
[methods/06_the_statistics.md](../methods/06_the_statistics.md) for the fitting
machinery, and [notes/full_archive_fit_prereg.md](full_archive_fit_prereg.md)
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
