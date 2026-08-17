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

That pair of numbers is the most useful thing in this section. **The archive does
not resolve shared against independent**, and the direction of the answer is set
by a bookkeeping convention rather than by the data. The record's response is to
keep the headline result model-independent, which is why the width-slope bound
rather than the hierarchical fit carries the collisional claim.

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
profile is scanned in both directions and re-run from a seeded start, as a
convergence check. Taken separately, the pooled fit's passes put the bound at
1.007, 1.231 and 2.106 MHz per W. The campaign-only refit's passes agree to three
decimals, at 1.024, 1.025 and 1.026.

That is the statement worth making, and it is worth being careful about which
number carries it. `results/stark_joint.csv` also records
`direction_dchi2_max` as 8.59, the largest pointwise chi-square gap between the
two direction variants, against the 2.706 at which the bound is read. **That
comparison alone would not establish anything**, because each profile is
normalised to its OWN minimum before the threshold is applied, so a gap that is a
constant offset moves no bound at all. Only the part of the gap that VARIES along
the profile can. Here it does vary, by 56 in chi-square across the range, which
is why the passes land on different bounds. A large gap is a prompt to check the
bounds, not a result by itself.

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
as the evidence allows.** A longer lever that loosens a bound means the pool is
not ADDING INFORMATION about the shared parameter. That much follows: the pooled
dataset contains the campaign, so it cannot know less about a genuinely shared
quantity.

It does NOT follow that the groups disagree about the quantity, and separating the
candidates is the work. There are three, and they are distinguishable.

  * **A genuine preference for a nonzero value** in the added group, which would
    move the profile minimum and legitimately raise an upper bound. **Checked and
    ruled out here.** Both constructions put the minimum at the same place, 0.25
    MHz per W, and neither prefers a nonzero value at any strength worth quoting.
    A loosening produced by a preference requires the minimum to move, and it does
    not move.
  * **Added nuisance freedom** absorbing structure the shared parameter was
    reading. The extra sessions bring their own detector saturation, scan rates
    and rate scale, and those are constrained by data in the pool while sitting
    inert in a campaign-only fit. This is a real cost of pooling and is NOT
    heterogeneity.
  * **Imperfect convergence**, which is what the evidence in this case points at.
    The pooled profile is shallower than the campaign-only profile through the
    whole region that sets the bound, and it is locally non-monotonic, rising to
    4.60 at 1.50 and falling to 4.36 at 1.54. Together with passes that disagree
    about the answer by a factor of two, that is a statement about the optimiser
    and the surface.

So the diagnostic is a prompt and not a verdict. **What it establishes is that the
pooled number should not be read as the better-constrained one merely because it
uses more data.** Whether the sessions shared a geometry stays open, on apparatus
grounds, and section 3 says why no nuisance in the fit could settle it.

**What this does not establish, and the distinction matters.** A poorly behaved
likelihood surface is a statement about the surface. It is not proof that the
sessions saw different coefficients. Leave-one-peak-out is similarly asymmetric
rather than damning: removing peak 4121 costs 8.75 in chi-square against the
prediction while the other three cost 1.12, 2.27 and 0.61, so one peak carries
most of the constraint, which is a concentration of leverage and not a
contradiction.

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

Question 6 is the one most often skipped. For this dataset the answer is that the
composite width is about two thirds a fixed natural width, and the light-shift
term moves it by a few kilohertz at the bound, while the same term moves the line
centre by a hundred and fifty kilohertz against an eighty-eight kilohertz
scatter. The width is the insensitive moment because the shift distribution is
one-sided, so the moment has to be matched to the symmetry of the perturbation.
[The identifiability page](../wiki/identifiability.md) carries the general form.

## 6. What the record does about all of this

**A converged construction is not automatically the better-supported one, and
this dataset makes the point sharply.** The campaign alone is the construction
whose profile passes agree, and it is also the construction most exposed to the
one systematic that competes with the light shift. Granting the fit a free
red-side wing, which is an alternative explanation of the same structure the light
shift is read from, tightens the campaign-alone bound by a factor of about seven
while tightening the pooled bound by about seven per cent. The campaign's
red-side structure is almost entirely absorbable by that wing, so the campaign by
itself can barely distinguish a light shift from an instrumental wing, and the
extra sessions contribute structure the wing cannot absorb.

Two desirable properties therefore point in opposite directions here. Adjudicating
on either one alone would pick a different answer, which is the reason this chapter
argues for a checklist rather than for a construction.

The pooled bound stays the quoted construction, S₀(225 mW) below 0.26 MHz,
because it is the one that has been run, checked and published, and because
withdrawing it on the strength of a diagnostic would replace a documented number
with none. The two open items are recorded rather than resolved: a campaign-alone
refit is not in `results/`, and no per-session waist measurement exists. Both
appear in [the plan](../PLAN.md) as work, and the second is the reason
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
