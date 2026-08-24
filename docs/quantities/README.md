# Quantities

One page per physical quantity this experiment tries to measure, constrain or
calibrate, written to answer a single question about that quantity rather than
to describe it.

**The question.** For one physical quantity: what is it, what has the field
already achieved, what does this dataset establish, why not more, and exactly
what would have to change at the bench to do better.
**Takes.** A quantity and a construction. Nothing else, and in particular no
new fitting: every number on these pages is read from a committed artefact.
**Gives.** A literature benchmark, the current result with its epistemic
class, the named limitation, three defined levels of improvement with their
bench recipes, the failure modes, and what remains impossible.
**Skip if.** The question is what a term means, which is
[the glossary](../GLOSSARY.md), or how a method works, which is
[the wiki](../wiki/README.md), or what the whole programme found, which is
[the synthesis](../BIG_PICTURE.md).

## What a dossier is, and what it is not

The rest of this repository is organised by theme, by method and by
re-centring. A reader who arrives holding a quantity, wanting to know where
this experiment stands on it and what a next campaign would buy, has had to
assemble that from five places. These pages are that assembly, and nothing
more.

A dossier is therefore a router with recipes attached. Where a treatment
already exists it is linked rather than repeated: the physics of an effect
belongs in [the wiki](../wiki/README.md), the derivation in
[the methods chapters](../methods.md), the block that would run a measurement
in [the plan](../PLAN.md), and the leverage ordering across the whole
programme in
[big picture chapter 5](../big_picture/05_next-vapour-cell.md). What is new
here is the per-quantity assembly, the benchmark against the literature, and
the recipes.

Not every quantity gets a page. Seven do, chosen by whether the quantity is
scientifically important, has a literature benchmark, has something nontrivial
said about it by this dataset, has a realistic experimental lever, would change
a decision if better measured, and contributes to one integrated campaign. A
quantity failing most of those is a section inside another dossier, which is
the difference between a quantity layer and one page per variable.

## The unit is a quantity and a construction

A number here is never quoted as belonging to a symbol alone. The AC-Stark
coefficient alone has seven committed constructions, from the full archive
through the pooled three-session fit to the width and centre channels taken
separately, and they differ by up to a factor of three with different
convergence states. Each dossier's results
section is therefore one row per construction, carrying the estimator, the data
subset, the status recorded in the committed artefact, and the epistemic class.

Where a construction is not settled, the dossier says so in place and does not
quote it as a value.

## The three levels

Every dossier defines three targets for a future measurement. They are levels
of scientific standing, not of decimal places.

**An improved bound** tightens the present constraint or removes a named
ambiguity. It need not produce a measurement. Turning an upper bound into a
tighter one, breaking one degeneracy, establishing a sign, or excluding a model
all qualify.

**A measurement** makes the quantity separately identifiable under a model that
has been tested and a calibration that has been supplied independently. The
distinction from the level above is identifiability, not precision: a small
error bar on a quantity that trades freely with another is not a measurement.

**A competitive measurement** reaches an uncertainty, a coverage and a
systematic control comparable with the literature benchmark in that dossier's
own second section. The benchmark is what makes the word mean anything, so a
level defined against this experiment's current state instead is not written.

Each level carries a recipe and a success criterion with six parts: precision,
identifiability, coverage, convergence, model validity and calibration. A
nominal precision reached while two models remain degenerate is not a success,
and the criterion says so before the measurement is taken rather than after.

Each level also states its minimum viable version, the smallest campaign that
would already be worth running, so that a programme can be entered rather than
committed to.

## What is not on these pages

Numbers typed by hand. Every value is read from a named committed artefact,
and where a target cannot yet be supported by a simulation or by the literature
it is marked as requiring a calculation rather than given a plausible figure.

Claims about who would find the result interesting. These pages describe the
experiment and the inference.

## The dossiers

| quantity | the question it answers | state |
|---|---|---|
| [the AC-Stark light shift](ac-stark-light-shift.md) | What light shift can be separated from the other mechanisms sharing its power signature? | written |
| [collisional self-broadening](self-broadening.md) | How much self-broadening does this experiment resolve independently of the laser width and the density scale? | written |
| the laser width | Can the laser contribution be calibrated independently rather than inferred from the line it broadens? | queued |
| the beam waist | Is the intensity and transit geometry independently known, or accepted? | queued |
| the frequency axis | Can the frequency scale be anchored physically rather than reconstructed differentially? | queued |
| the transit kernel | Is the cusp a measured shape or a pinned assumption? | queued |
| the band excess | Is the excess outside the fit window physical or instrumental? | queued |

The queued rows are listed because a reader is owed the shape of the layer
before it is complete, and because the two written pages are a format test.

## The campaign

The dossiers are deliberately per-quantity, and a campaign is not. One
measurement usually moves several quantities at once, and the waist is the
clearest case, entering the intensity that sets the light shift and the
transit width in the same stroke.
[The campaign page](campaign.md) carries that coupling, the leverage of each
re-centring across all the quantities, and the comparison between candidate
campaigns.
