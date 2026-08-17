*Chapter 8 of 8 of [the big picture](../BIG_PICTURE.md)*

**The question.** A joint fit shares one parameter across many measurements. When
does that add information, and when does it only add freedom?
**Takes.** The constructions of [what the 2025 dataset
delivered](04_what-2025-delivered.md) and the degeneracies of [limitations and
identifiability](07_limitations-and-identifiability.md).
**Gives.** The two sharing decisions this record makes, one across spectral
peaks and one across measurement sessions, each with the evidence for it and the
boundary beyond which it is not established. Then six questions to ask of any
pooled fit.
**Skip if.** You want the bounds rather than their construction, in which case
[RESULTS.md](../RESULTS.md) is the ledger.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 1. What a joint fit assumes

Sharing a parameter across a set of measurements asserts that one physical
quantity produced all of them. Everything in this chapter follows from taking
that assertion literally and asking, for each shared parameter, whether the
quantity could have changed between the groups being pooled.

The general treatment of the machinery is [the wiki's joint-fit
page](../wiki/joint-fit.md). This chapter is about the two decisions this
dataset actually makes.

## 2. Across the four peaks

The four lines are hyperfine components of one transition recorded in one dwell.
The light shift and the saturation are blind to the hyperfine index, so one
coefficient across the four peaks is a physical statement rather than a
convenience. The collisional width is not shared: it carries a per-peak
coefficient under the prior built in [the beta_self
work](../notes/beta_self_pooling_prereg.md), whose framing is the template this
chapter follows, that the sharing level is decided by physics and the fit
statistics are reported as a check rather than as the licence.

**One peak difference is real, computable, and currently unspendable.** Hyperfine
pumping through the intermediate cascade does not preserve the hyperfine index,
and its branching product runs from 0.223 to 0.372 across the four lines, a
factor of 1.67. That is about 4 kHz of width against a single-block scatter of
88 kHz. So the peaks are known not to be identical, the size of the difference is
calculable, and it sits a factor of twenty below the noise that would reveal it.
A difference in that position is a reason to keep the term in the model and not
a reason to stop sharing.

**What the fit statistics say about sharing, including where they disagree with
themselves.** `results/sharing_bic.csv` compares a laser width shared per
temperature against one free per block. Corrected for the roughly threefold
spectral over-sampling, the criterion favours the shared model by 61.3, which is
decisive on the usual reading. Computed on raw sample counts it favours the free
model by 51.9. The two models fit almost identically, at reduced chi-square 0.857
against 0.854.

That pair of numbers is the most useful thing in this section. **The
model-selection verdict is set by the effective-sample convention used to account
for correlation, not by the physics**, which is a statement about the dataset's
information content rather than about whether the sharing is physically true. The
correction does two things at once, and naming both is what makes the flip
unsurprising: it rescales the chi-square as well as the sample count, so the
freer model's chi-square advantage shrinks roughly as the over-sampling factor
while the parameter penalty shrinks only logarithmically, and the verdict moves
toward the shared model. A
dataset whose verdict flips with the counting convention does not resolve shared
against independent, and the record's response is to keep the headline result
model-independent, which is why the width-slope bound rather than the
hierarchical fit carries the collisional claim.

## 3. Across the three sessions

The joint light-shift fit pools 100 campaign traces with 46 from the 4 July
rehearsal and 26 from the campaign-morning session of 17 July. It grants each
session its own laser width per peak, its own detector saturation, its own
milliseconds-to-megahertz rate for the rehearsal, and a rate scale bounded to ten
per cent for the campaign morning.

**What it shares is one coefficient.** The parameter hierarchy is tabulated for
the sibling full-dataset construction in [that fit's
preregistration](../notes/full_dataset_fit_prereg.md), and the coefficient is the
only row whose sharing column reads across everything, with no session
qualifier of any kind.

**A sharing that was wrong, kept on the record.** The first version of this fit
shared the laser width across sessions. The campaign widths then inflated to
about 4.4 MHz, which is far outside anything the campaign supports, so the second
version separated them per session. The failure was visible because it moved a
quantity with an independently known scale. That is the mechanism by which
over-sharing is normally caught, and it is worth stating that nothing forced the
discovery.

**The difference no nuisance absorbs.** The light-shift coefficient scales as one
over the beam waist squared. A session recorded at a different focus therefore
has a different coefficient, and no per-session laser width, saturation or rate
scale can absorb that, because none of them is the waist. Every other
session-to-session difference in this fit has a nuisance assigned to it. This one
does not, by construction.

**The boundary of the claim, stated exactly.** That the sessions ran in different
configurations is ESTABLISHED: the rehearsal's scan rate is fitted from its own
widths rather than transferred, the 4 July configuration does not share the
campaign's rate, and one session ran at a different cell temperature. That the
sessions had different GEOMETRY is UNTESTED. The archive carries no per-session
waist measurement, so the question is open on apparatus knowledge rather than
settled either way.

## 4. The signature of a pool that is not measuring one parameter

Two committed diagnostics say the pooled construction is not behaving like a fit
to one quantity.

**The profile passes disagree about the bound itself, by a factor of two.** The
numbers come from two runs and the provenance matters, so it is stated. The
committed bound, 1.147 MHz per W, is the 2026-08-03 production run's
pointwise-minimum construction over cold and seeded chains, interpolated between
its 1.00 and 1.50 grid points. A diagnostic re-run of the same construction on
2026-08-17 scanned the profile in both directions and from a seeded start, and
taken separately its passes put the bound at 1.007, 1.231 and 2.106 MHz per W. So
the passes span a factor of 2.1, and even the re-run's best-converged seeded pass
sits seven per cent from the committed value. The campaign-only refit from the
same day behaves oppositely: its passes agree to three decimals, at 1.024, 1.025
and 1.026. The constructions and profiles are published in [the campaign-only
profile note](../notes/campaign_only_stark_profile.md) so these sentences rest on
evidence a reader can see.

Two different gap statistics exist and only one of them carries this claim.
Within the diagnostic re-run, the chi-square gap between the ascending and
descending passes varies by up to 56 along the profile, and a gap that varies is
exactly what moves a bound, which is why those passes land answers a factor of
two apart. The committed run separately records `direction_dchi2_max` as 8.59,
the largest pointwise gap between its two direction variants, each of which is
already a pointwise minimum over several chains. **Neither raw gap establishes
anything by itself**, because each profile is normalised to its OWN minimum
before the threshold is applied, so a constant offset between passes moves no
bound at all. The quantity that matters is the spread of the ANSWERS, and that is
the factor of 2.1 above.

**The noise scales and the signal, in one place.** The loosening this section
interprets, the pooled 1.147 against the campaign-only 1.025, is twelve per cent.
The pooled construction's pass spread is a factor of 2.1, its best-pass-to-
committed movement is seven per cent, and its profile carries a local
non-monotonicity of 0.24 in chi-square, rising to 4.60 at 1.50 and falling to
4.36 at 1.54. **A twelve per cent difference read from a construction that
reproduces itself to no better than a factor of two across passes is not a
resolved comparison.** What the numbers support is that the pooled and campaign-only
bounds cannot currently be compared at the size of their difference, and the
comparison becomes meaningful only after the pooled construction passes a
profile-reproducibility test, independent starts agreeing on the Delta
chi-square curve and not merely on the fitted point.

A profile-likelihood interval means what it says only when the surface is the
same surface whichever way it is traversed.

**A longer lever loosens the bound.** The rehearsal contributes a 270 mW rung,
which carries 1.44 times the campaign's largest squared-shift lever. Adding data
that extend the lever should tighten a bound. The record instead shows the pooled
bound sitting looser than its own campaign-rows column, and the sibling
full-dataset fit shows the same shape when the temperature ladder is added rather
than the power ladder. Both observations were previously logged without
interpretation, in [the preregistration
record](../PREREGISTRATION_RESULTS.md) and in [the full-dataset
preregistration](../notes/full_dataset_fit_prereg.md).

**The interpretation, which is the one step this chapter adds, stated as narrowly
as the evidence allows.** Two objects have to be kept apart. The INFORMATION the
data carry about a shared parameter is a property of the data under a correctly
specified common model, and adding informative data cannot reduce it: the pooled
dataset contains the campaign, so it cannot know less about a genuinely shared
quantity. The REPORTED INTERVAL is a different object. It is the output of a
particular model, nuisance structure and optimiser, and it is the thing observed
to loosen. So a longer lever that loosens the bound does not say the added data
destroyed information, which is impossible. It says the enlarged CONSTRUCTION
changed the reported inference, and the question becomes which part of the
construction did it. A further consequence follows and is the defensible
headline: **the two bounds profile different parameter spaces, so they are not
comparable as constraints on one quantity**, and no ordering between them should
be read as one construction knowing more than the other.

It does NOT follow that the groups disagree about the quantity, and separating
the candidates is the work. There are four.

  * **A genuine preference for a nonzero value** in the added group, which would
    move the profile minimum and legitimately raise an upper bound. **The
    available test has no power to decide this, and its one discriminating row
    leans toward the preference rather than against it.** Both minima sit on the
    same grid point at 0.25 MHz per W, but the grid is spaced 0.25, far coarser
    than the shift a mild preference from lower-weight groups would produce. At
    zero coefficient the pooled profile sits 0.12 above its minimum while the
    campaign-only profile sits at 0.00, which is a displacement of the pooled
    curve toward positive values, the signature the preregistration predicted
    with "mildly prefer a positive shift and drag the profile's rise", and the
    drag half of that prediction is confirmed by the profile table directly. The
    0.12 is below the 0.24 optimiser noise floor demonstrated on the same curve,
    so it is a lean and not a finding.
  * **Added nuisance freedom** absorbing structure the shared parameter was
    reading. The extra sessions bring their own detector saturation, scan rates
    and rate scale, and those are constrained by data in the pool while sitting
    inert in a campaign-only fit. This is a real cost of pooling and is NOT
    heterogeneity.
  * **A group-dependent error model.** If the construction weighted groups by
    their own misfit, adding a group that fits less well would flatten every
    profile arithmetically, with no heterogeneity involved. Checked for this
    fit: the producer applies no per-block error inflation, so the specific
    mechanism is absent here, and the class belongs on the list because the test
    that catches it, holding the error model fixed while the groups change, is
    cheap wherever it applies.
  * **Imperfect convergence**, which most of the evidence points at. The pooled
    profile is shallower than the campaign-only profile through the whole region
    that sets the bound, it is locally non-monotonic at the 0.24 level, and its
    passes disagree about the answer by a factor of two. That is a statement
    about the optimiser and the surface.

So the diagnostic is a prompt and not a verdict. **What it establishes is that
the pooled number should not be read as the better-constrained one merely because
it uses more data.** Whether the sessions shared a geometry stays open, on
apparatus grounds, and section 3 says why no nuisance in the fit could settle it.

One of this chapter's own checklist questions applies to these numbers and gets
its answer here rather than being deflected. Question 3 asks whether leaving one
group out moves the answer more than the systematic being claimed, and it does:
dropping peak 4192, which removes the entire campaign-morning session, moves the
bound by a factor of 1.42, and the chi-square cost of removing peak 4121 from
the fit at the predicted coefficient is 8.75 against 1.12, 2.27 and 0.61 for the
other three, so the constraint is substantially owned by one peak and one
subset. That is why the record publishes the leave-one-out rows and treats their
spread as the dominant reported sensitivity of this construction.

**What this does not establish, and the distinction matters.** A poorly behaved
likelihood surface is a statement about the surface. It is not proof that the
sessions saw different coefficients, and concentrated ownership is not proof of a
contradiction between the peaks. What the ownership numbers above DO establish is
answered where question 3 is applied, not waved past.

## 5. Six questions to ask of any pooled fit

Each is answerable from artefacts this pipeline already writes.

1. **Do the profile passes agree about the ANSWER?** Scan the profiled parameter
   in both directions and from a seeded start, then derive the interval
   SEPARATELY from each pass and compare those. Do not compare the passes'
   chi-square values, because each profile is normalised to its own minimum, so a
   constant offset between two passes changes no interval while a gap that varies
   along the profile changes it a great deal. The quantity that matters is the
   spread of the answers, not the spread of the curves.
2. **Does a longer lever tighten the bound?** If extending the lever loosens it,
   stop and find out why before quoting either number.
3. **Does leaving one group out move the answer more than the systematic being
   claimed?** If so, the answer belongs to that group rather than to the pool.
4. **Does the shared parameter have a known group dependence that no nuisance
   can absorb?** List the nuisances, then list the ways the groups differ, and
   look for a difference with no nuisance opposite it.
5. **Are the nuisances that absorb group differences measured or fitted from the
   same channel as the answer?** A rate fitted from widths couples straight into
   a width-channel result, so it is not an independent absorber.
6. **Is the shared parameter's channel the one carrying the information?** Build
   the component budget and compute how much of the observable the parameter
   actually moves. A parameter can sit in a channel and carry almost none of it,
   in which case constraining that channel buys nothing.

Question 6 is the one most often skipped. For this dataset: the fixed natural
Lorentzian width is 3.49 MHz, from the 6S lifetime known to four parts in a
thousand, against an observed composite width near 5.4 MHz, a linear ratio of
about 0.65. That is a ratio of two defined widths and not an additive share,
since the width of a convolution does not decompose additively, and its meaning
here is only that most of the observed width is a constant no lever moves. The
leverage comparison is then per observable: the light-shift term moves the
composite width by about 4 kHz at the bound, against a per-block width scatter
of 88 kHz, while the same term pulls the line centre by about 150 kHz, nearly
forty times its width effect. The width is the insensitive moment because the
shift distribution is one-sided, so the moment has to be matched to the symmetry
of the perturbation. **And the sensitive moment is not available to this
archive**, which the comparison would otherwise leave as an obvious question:
the laser lock drifted, absolute centres are lost, and reading widths instead of
centres is the founding premise of the drift-immune method. The comparison
therefore says what a fixed-lock session buys, which is why the plan carries
one.
[The identifiability page](../wiki/identifiability.md) carries the general form.

## 6. What the record does about all of this

**A converged construction is not automatically the better-supported one, and
this dataset makes the point sharply.** The campaign alone is the construction
whose profile passes agree, and it is also the construction whose reported upper
limit is by far the more sensitive to the one alternative model that competes
with the light shift. The perturbation is controlled, since the only change is
whether the fit carries a free red-side wing, an alternative explanation of the
same structure the light shift is read from. Granting it moves the campaign-alone
upper limit by a factor of about 7.3 and the pooled upper limit by a factor of
about 1.07, stated that way because the two movements are the same kind of ratio
and should read as one. That is a statement about the reported limits under two
stated constructions, not a measured systematic error, and it is a REASSIGNMENT
rather than a tightening: the wing's thirteen units of chi-square say real
red-side structure exists, and the fit reassigns that structure from the light
shift to the wing without any current test adjudicating which explanation is
true. If the structure is instrumental the conditional bound applies,
and if it is physical then absorbing it biases the coefficient low, so the
tighter number is not a prize. What the comparison establishes is that the
campaign by itself can barely distinguish a light shift from an instrumental
wing, while the extra sessions contribute structure the wing cannot absorb.

Two desirable properties therefore point in opposite directions here. Adjudicating
on either one alone would pick a different answer, which is the reason this chapter
argues for a checklist rather than for a construction.

The pooled bound stays the quoted construction, S₀(225 mW) below 0.26 MHz,
because it is the one that has been run and published, with its convergence under
review in section 4, and because withdrawing it on the strength of a diagnostic
would replace a documented number with none. The two open items are recorded rather than resolved: the
campaign-alone refit is documented as a diagnostic in [its own
note](../notes/campaign_only_stark_profile.md) and is not in `results/`, and no
per-session waist measurement exists. Both appear in [the plan](../PLAN.md) as
work, and the second is the reason
[chapter 7](07_limitations-and-identifiability.md) calls the waist the largest
open systematic.

## See also

  * [The wiki on joint fitting](../wiki/joint-fit.md), for the machinery in
    general rather than this dataset's two decisions.
  * [The wiki on identifiability](../wiki/identifiability.md), for what sharing
    can and cannot repair.
  * [Limitations and identifiability](07_limitations-and-identifiability.md), for
    the six chains from a limitation to the measurement that removes it.
  * [RESEARCH_DECISIONS.md](../RESEARCH_DECISIONS.md), for the decision record
    rather than the argument.
