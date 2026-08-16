# The wiki: one page per concept, method, effect or technique

This folder is the repository's general-knowledge layer. It abstracts the
reusable scientific concepts from the experiment without replacing the
experiment record, and it is the shared conceptual interface between the
methods chapters, a thesis and any future reusable package. Each page says
what a thing is, what problem it solves, where this repository uses it, what
can go wrong with it, and where to read more.

## How the pages connect

The clusters below are a chain, not a filing system. It runs from the light
the atoms sit in to the question of whether the answer was earned, and each
page is one link.

```mermaid
flowchart LR
    HF["hyperfine<br/>structure"] --> D["Doppler-free<br/>two-photon"]
    D --> V["Voigt profile"]
    S["AC-Stark shift"] --> V
    T["transit-time<br/>broadening"] --> V
    C["self-broadening"] --> V
    V --> W["weighted<br/>least squares"]
    W --> J["joint fit"]
    J --> I["information<br/>criteria"]
    I --> ID["identifiability"]
    ID --> PL["profile<br/>likelihood"]
    PL --> IR["injection<br/>recovery"]
    IR --> PR["preregistration"]
    E["EOM sidebands"] --> WM["wavemeter and<br/>the axis"]
    WM --> J
    SW["standing waves"] -.-> D
    BW["beam waist"] -.-> S
    BW -.-> T
    SAT["saturation"] -.-> S
    B["blackbody"] -.-> S
    K["third cumulant"] -.-> S
    A["Allan deviation"] -.-> WM
    BF["Bessel functions"] -.-> E
```

*Solid arrows carry the measurement: what the atoms are, what drives them,
what shapes the line, how it is weighted and fitted, and what decides whether
the fit determined anything. Dotted arrows are the supporting tools each step
needs. A reader who follows the solid path once has the whole argument of this
repository in order.*

## A. Experimental spectroscopy

*What is measured?* Read in order and the sequence is the measurement itself:
what the atoms are, how the line is driven, what shape it takes, and what
moves or widens it.

| page | type | in one line |
|---|---|---|
| [Hyperfine structure](hyperfine-structure.md) | concept | why one transition is four lines, and why a same-isotope pair is a frequency ruler |
| [Doppler-free two-photon spectroscopy](doppler-free-two-photon.md) | technique | why two counter-propagating photons cancel thermal motion, and what that costs in laser-noise sensitivity |
| [Standing waves](standing-waves.md) | physical effect | what a retro-reflected beam really makes, and how the fringes divide the signal from its pedestal |
| [The Voigt profile](voigt-profile.md) | concept | the Lorentzian-Gaussian convolution every real line becomes, and the width degeneracy it carries |
| [Transit-time broadening](transit-time-broadening.md) | physical effect | a finite crossing time broadens the line, and the thermal average makes a cusp, not a Gaussian |
| [The beam waist](the-beam-waist.md) | concept | the one number that turns a power into an intensity, and why every other quantity inherits it |
| [The AC-Stark shift](ac-stark-shift.md) | physical effect | the drive light moves the very levels it probes, and a focused beam turns one shift into a distribution |
| [Saturation](saturation.md) | physical effect | where the square law stops, and why a tighter focus leaves the safe regime faster than it gains signal |
| [Collisional self-broadening](self-broadening.md) | physical effect | collisions keep the line Lorentzian and grow its width linearly with density |

## B. Statistical inference

*How is it modelled, what is identifiable, and how do we know the inference is
valid?* The chain this repository actually runs, in order: weight the data by
what the noise actually does, fit jointly, choose the model honestly, ask what
the data determine, carry the uncertainty faithfully, prove the machinery on
known truth, and freeze the criterion before reading the answer.

| page | type | in one line |
|---|---|---|
| [Weighted least squares](weighted-least-squares.md) | method | weights from a measured noise law, not from the residuals |
| [The joint fit](joint-fit.md) | method | share what physics shares, free what drifts |
| [Information criteria](information-criteria.md) | method | when is a better fit worth its extra parameters |
| [Identifiability](identifiability.md) | method | when does the data actually determine the parameter we want |
| [The profile likelihood](profile-likelihood.md) | method | an interval that keeps its shape when nuisance parameters are degenerate |
| [Injection-recovery testing](injection-recovery.md) | method | no fitter touches real data before it recovers known truth from synthetic data |
| [Preregistration](preregistration.md) | method | the criterion, the null test and the ceiling test, frozen before any number is read |

## C. Robustness and influence

*Which observations is the answer resting on, and would it survive their
loss?* Wave 3, and the cluster the repository's own influence audit motivated.

| page | type | in one line |
|---|---|---|
| [Influence diagnostics](influence-diagnostics.md) | method | leverage, case deletion, and why outlying and influential are different words |
| [Robust fitting](robust-fitting.md) | method | losses that stop rewarding a far point, run beside the standard fit rather than in place of it |
| [Resampling](resampling.md) | method | the bootstrap and the jackknife, and when the structure of the data breaks them |
| [Heavy-tailed models](heavy-tailed-models.md) | concept | treating an outlier as evidence about the noise rather than as a point to remove |
| [Sensitivity analysis](sensitivity-analysis.md) | method | which input a projection actually depends on, locally and globally |

## D. Optical techniques

*How is the axis established, and what else does the apparatus impose?*

| page | type | in one line |
|---|---|---|
| [EOM sidebands](eom-sidebands.md) | technique | phase modulation stamps a radio-accurate frequency comb onto the light |
| [The wavemeter and the frequency axis](the-wavemeter-and-the-frequency-axis.md) | technique | where a frequency axis comes from, and how a nonlinear scan is calibrated rather than trusted |
| [Bessel functions](bessel-functions.md) | concept, supporting | the amplitudes every phase-modulation problem is written in |
| [Blackbody radiation](blackbody-radiation.md) | physical effect | the cell's own thermal glow, and how to tell when it matters |

## E. Mathematical descriptors

| page | type | in one line |
|---|---|---|
| [The third cumulant](third-cumulant.md) | concept | the number that isolates a lineshape's asymmetry from its width |
| [Allan deviation](allan-deviation.md) | concept, supporting | the statistic that separates noise types by how they average down |

Bessel functions and the Allan deviation are supporting topics, here because
the design of the next measurement session leans on them rather than because
the committed analysis does.

## What governs what

For experimental outcomes the order of authority is:
the committed data and `results/*.csv`, then [RESULTS.md](../RESULTS.md),
then the [methods chapters](../methods.md), then these pages, then the
front-door orientation. A wiki page can never override an authoritative
result. Dated preregistrations are prospective commitments and
[HISTORY.md](../HISTORY.md) is the historical record, and neither is edited
for navigation. For general theory the authority is the cited literature and
established mathematics: these pages explain, they are not sources, and a
claim is only as good as the reference it carries. The general section of a
page may stay valid across model revisions, and only its
repository-specific section is coupled to the current implementation.

## Waves so far

Wave 1 built the fifteen pages of clusters A, B, D and E. Wave 2 added
hyperfine structure, the wavemeter and the frequency axis, weighted least
squares, saturation, preregistration, the beam waist and standing waves. Wave
3 added cluster C, on robustness and influence, and it was written after the
repository ran the influence audit those pages describe rather than before, so
that the repository sections report work done rather than work imagined.

The next candidates, unordered and none committed: the density scale and the
vapour-pressure curve it comes from, photon counting against analog detection,
and the transit-time kernel's thermal average as a page of its own rather than
a section of the transit page.

## Conventions

Every page follows one template: What it is (general, a few hundred words, at
most two figures and only where a figure genuinely helps), What problem it
solves, Where this repository uses it (links into chapters, modules and
results, numbers read from the committed CSVs), What can go wrong (the
failure modes, distinguishing model failure, data insufficiency,
implementation failure and experimental limitation), Try it where the package
can demonstrate the idea in a few lines, and Further reading.

**The snippets run.** Every `python` block on these pages is executed by
`tests/test_wiki_snippets_run.py` in a clean subprocess with only the
repository on the path, and it must print something. A block that stops
working fails the suite rather than misleading a reader, and two of the first
six were written with a wrong signature and a wrong dictionary key, which is
why the guard exists. They use only the public API, so they are also a
working introduction to it. Pages
carry no external images. General claims carry references, and
repository-specific claims link to their source of truth.

**Status of the references.** A citation to `../lit/` points at a note in this
repository, which carries its own VERIFIED or REPORTED status. A citation to
anything else is a standard reference given for the reader's benefit and is
NOT held here or checked against its source, so it has the standing of
REPORTED in the same vocabulary. Textbook results on these pages are
verifiable by computation rather than by citation, and the numeric ones were
checked that way: the Bessel zeros, the two carrier nulls, the Voigt width
approximation against a numerical profile, the criterion crossing, the width
conversion factor and both blackbody peaks.
