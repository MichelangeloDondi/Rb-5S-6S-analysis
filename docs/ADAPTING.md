# Adapting this pipeline

**The question.** You have your own transition, your own cell or fibre, and your
own detector. Which parts of this machinery transfer, which need editing, and
what does getting each one wrong do to your answer?
**Takes.** Nothing. This page is a door, not a chapter.
**Gives.** Every seam named, with the file it lives in, the failure it causes,
and the test that catches it. Then the three radiation fields, the branching
fraction, and the two-mass correction, each as a test you can run on your own
numbers before writing code.
**Skip if.** You only want this repository's own results, which are in
[RESULTS.md](RESULTS.md) and [CLAIMS.md](CLAIMS.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

> **Want the concept rather than the seam?** [`docs/wiki/`](wiki/README.md)
> carries one page per concept, method and effect, each with a worked
> example that runs. Its router has a route for adapting this code to
> another line, and nineteen of its pages record where this project got
> that concept wrong first.

This page names every seam: what to change, where it lives, what getting it
wrong does to the answer, and the check that catches it.

The fastest way in: [examples/your_line.ipynb](../examples/your_line.ipynb)
takes a dictionary of your transition's numbers and shows your composite
line, the light-shift distribution your light geometry implies (focused
beam, nanofibre evanescent field, hollow-core mode, or your own sampled
profile), and the observable line with the shift folded in. GitHub renders
it with the plots embedded.

The analysis is a library (`rb5s6s/`, installable with `pip install -e .`)
driven by thin scripts (`scripts/run_*.py`). It was built for one campaign
on one transition, but its parts separate along clean seams, and this page
names them for anyone pointing the machinery at a different line, a
different species, or a different light geometry. The test battery
(`pytest --runslow`, see CI) pins the behaviour of every part named below,
so an adaptation that breaks an assumption fails loudly rather than
silently.

## The seam map

| you want to change | you touch | what lives there | a wrong change looks like | the check |
|---|---|---|---|---|
| the transition or species | [`rb5s6s/constants.py`](../rb5s6s/constants.py) | line frequencies, hyperfine constants, natural width from the upper-state lifetime, polarizability inputs. Every value carries a provenance tag and a source | fits that converge on widths meaning something else. Nothing downstream re-derives a constant | [`tests/test_constants.py`](../tests/test_constants.py), which holds the peak identification and the two frequency axes apart |
| the vapour and its density | [`rb5s6s/density.py`](../rb5s6s/density.py) | the vapour-pressure chain N(T) and its stated systematics | a clean multiplier on every collisional coefficient, with no fit residual to show it | [`tests/test_density.py`](../tests/test_density.py). A molecular beam or a buffer-gas cell replaces the file outright, and nothing else reads the vapour law |
| the apparatus | [`rb5s6s/config.py`](../rb5s6s/config.py) for file layouts, directory roots, fit windows and QC thresholds. [`rb5s6s/constants.py`](../rb5s6s/constants.py) for the beam itself, since `W0_MEASURED_M`, `W0_BAND_M`, `RHO_RETRO` and `RHO_RETRO_ERR` are measured quantities with provenance tags and live there. `config.py` re-exports those four by name, so a script importing them from either module gets the same value, and only `constants.py` is the place to change one | the peak light shift quoted at the wrong intensity, since it goes as the inverse square of the waist | [`tests/test_ramp_geometry_docs.py`](../tests/test_ramp_geometry_docs.py), which recomputes the geometry tables the documents print |
| the light geometry | [`rb5s6s/lineshape.py`](../rb5s6s/lineshape.py) | the composite line model and the shift-distribution machinery. The deep seam, below | a symmetric fit to an asymmetric line, with the shift absorbed into a width | [`tests/test_lineshape.py`](../tests/test_lineshape.py) |
| the detection noise | [`rb5s6s/noise.py`](../rb5s6s/noise.py) | the noise law measured from the traces themselves, used as fit weights everywhere | error bars wrong by a factor, and a model comparison that then picks its model with confidence | [`tests/test_noise.py`](../tests/test_noise.py) |
| the frequency axis | [`rb5s6s/ruler.py`](../rb5s6s/ruler.py) and [`rb5s6s/trim.py`](../rb5s6s/trim.py) | the sideband-ruler calibration, its validity layer, and the residual-tail trimmer | one scale error on every width and every shift at once | [`tests/test_ruler.py`](../tests/test_ruler.py), [`tests/test_trim.py`](../tests/test_trim.py) |
| which traces are allowed in | [`rb5s6s/qc.py`](../rb5s6s/qc.py) and the manifest | hard flags, the group outlier rule, the exclusion register of [`DATA.md`](DATA.md) | a census that quietly empties itself | [`tests/test_qc_policy.py`](../tests/test_qc_policy.py), which forbids a hard flag from reading a quantity the physics fits |

Three of those rows need more than a row. They are the next three sections.

One gap in the seam is worth naming rather than leaving to be found.
`fit_stark_sweep`, the stage that turns measured widths against power into the
width-channel AC-Stark bound, is not on the geometry seam. Its `profile`
argument is a boolean switch and not the geometry callable of the same name
that `model_profile` and `fit_condition` accept, and its `_fwhm_of` helper has
no override point. Pointing that stage at another geometry means editing it
rather than passing it something, and the shared parameter name hides that
from anyone reading the signature alone.

The gap is wider than that one function. `run_stark_joint`, the stage behind
the joint three-session bound the front page quotes, names its geometry with
the literal string `"gaussian"` rather than taking a callable. So neither
production inference stage sits on the seam: one takes a boolean that shares
its name, the other takes a string. The seam is real and tested where this
section describes it, and the two stages that turn measured data into
committed bounds sit beside it rather than on it.

## The deep seam: the light-shift distribution

The pipeline's central object is the map from an intensity distribution to
a lineshape. Three facts build it. The shift is proportional to intensity,
the detected signal goes as intensity to the n-th power, and every position
carries its geometry's volume weight. Those three turn one number, the peak
shift, into a whole density of shifts, and each environment gives its own.

`lineshape.stark_from_intensity_profile` is that map with nothing assumed
about the geometry. Pass sampled intensities on any parameterization of your
environment, together with the volume weight of each sample (r dr for a
cylindrical evanescent shell, uniform for a one-dimensional scan), and it
returns the density on your detuning grid. A focused Gaussian beam gives the
closed form this campaign used, `lineshape.stark_ramp`, a triangular density
at n = 2. The general function reproduces that triangle exactly, which is a
test and not a claim
(`test_general_profile_reproduces_focused_beam_triangle`).

The exponent n is the power of intensity the detected signal carries, so a
one-photon line uses n = 1 and gets a flat density, and a detection channel
with a different power scaling changes that exponent and nothing else.

Geometries the notebook already computes:

- a focused Gaussian beam across its transverse plane,
- a nanofibre evanescent field, exponential in the distance out from the surface,
- a hollow-core fibre mode, Bessel-like across the core.

The step from intensity to shift, dA ∝ dI/I, does not know
which geometry produced I. It holds for a thin evanescent shell as it holds
for a focused beam, which is why a guided-mode system can reuse the
extraction and not only the pictures. What changes between geometries is the
volume weight and the support of the density, and both are arguments to the
same function. The relation itself is not new. [`LITERATURE.md`](LITERATURE.md)
section 5 traces it to a 1980 review, whose Eq. (5.3) the closed form used
here reduces to exactly once the geometric measure is substituted. What this
repository adds is the evaluation for a fixed geometry and the consequences
that follow. If you reuse the construction, reuse that scoping with it.

`ramp_moment_contributions` and the machinery above it, the cumulant chain,
the joint fits and the identifiability tools, consume whatever density the
seam returns.

The fit path takes the geometry as an argument. `model_profile` and
`fit_condition` accept `profile`, a callable that builds the shift density
on the model's internal grid, defaulting to `stark_ramp`, the focused-beam
triangle every committed fit used. An adapted geometry passes a closure
over `stark_from_intensity_profile` with its own sampled intensities and
volume measure, and the joint fit runs unchanged. Cell 7 of
`examples/your_line.ipynb` does exactly that for the three geometries
above, and `test_model_profile_default_profile_is_stark_ramp_bitwise`
guards that omitting the argument reproduces the ramp path bit for bit.

A worked adaptation to a guided mode already exists:
[`notes/guided_mode_two_photon_design.md`](notes/guided_mode_two_photon_design.md)
takes the same measurement into a hollow-core fibre, states which of the
four line-shaping mechanisms stop being true there, and quotes the module
call behind every number so a reader can recompute it.

## The frequency axis, and the layer that decides whether to believe it

Every width and every shift here is quoted on an axis a sideband ruler
builds. [`rb5s6s/ruler.py`](../rb5s6s/ruler.py) fits each ruler trace as one
rigid comb, all teeth sharing one shape and one spacing, and converts the
fitted spacing into a sweep rate against the RF oscillator's exact tooth
spacing. Any calibrated axis can replace it. What has to survive the
replacement is the interface, which is that each block carries a rate and an
error, and the error reaches the fits.

The layer above the fit is the part worth porting, because a comb fit can
converge confidently on the wrong answer. The rigid grid labels its slots by
proximity to the window centre, so a retrace mirror can be fitted as a tooth
and the spacing comes out contracted. Four mechanisms guard that, all
pre-registered in
[`notes/ruler_validity_and_trim_prereg.md`](notes/ruler_validity_and_trim_prereg.md):

- **A labelling test.** The modulation depth is one constant for a campaign,
  so below the first crossing of the two Bessel weights a second-order tooth
  cannot stand taller than a first-order one for any reason internal to the
  modulation. Where the fitted heights say otherwise, the labelling is
  suspect. The `RULER_TOP3_*` constants in `config.py` carry the tie
  allowance and the switch deciding whether the verdict acts on the
  calibration or is only recorded. On this campaign it is recorded and not
  acting, and the constant's own docstring says why: the rule fires on half
  the fitted population, and it fires on clean synthetics built from the
  repository's own Bessel amplitude law whenever the modulation index sits
  above that crossing, where a second-order tooth legitimately outranks a
  first-order one. That makes it a diagnostic rather than a gate.
- **A re-index ladder.** Relabelling a rigid grid by whole slots is nearly
  degenerate in chi-squared, so a strict-improvement test decides the right
  answer by coin flip and excludes clean combs.
  `RULER_REINDEX_CHI2_TOL` is the tolerance separating a correct relabelling
  from the false rescue of a contaminated grid, set on synthetics with known
  answers. What the ladder cannot fix is excluded with a recorded reason
  rather than passed through.
- **A residual-tail trimmer.** [`rb5s6s/trim.py`](../rb5s6s/trim.py) cuts
  unmodelled mirror signal out of the fit sample with a one-sided cumulative
  sum, refuses any cut that would reach a guarded core around the line, and
  never writes a quality flag. Sustained means lasting rather than large,
  which is why one tall spike cannot trigger it.
- **A group outlier rule.** `qc.group_outlier` removes at most one member of
  a group of repeats, refuses groups too small for a scale estimate, and
  reads its thresholds from a table keyed by group size and by which scaling
  the deviation carries.

Port the shape of that layer rather than its numbers. Every threshold above
was calibrated against nulls or synthetics with a known answer, and a
threshold carried across to a different comb, a different sweep or a
different sampling rate is a number with no calibration behind it. The
recalibration is [`tests/test_trim.py`](../tests/test_trim.py) under
`--runslow`, which re-runs the null and fails if the tabulated thresholds
stop returning their nominal false-alarm rate.

## The noise law

Fits here are weighted by a noise law measured from the traces rather than
assumed. [`rb5s6s/noise.py`](../rb5s6s/noise.py) takes local noise from
second differences, which cancel a linear signal trend exactly and so
survive the steep flank of a bright line, bins them by local signal level,
and fits the variance law with a floor term and a shot-like term, adding a
multiplicative term only where the model comparison insists. Wing
autocorrelation supplies the correlation time, and parameter errors are
inflated by its square root.

Two properties of that construction have to travel with it. Second
differences high-pass the noise, so they underestimate correlated noise, and
the fitted law is rescaled so its floor matches the sigma measured directly
in the wings. And the law is fitted per condition, because both coefficients
move with condition.

Guessing the law instead is cheap and looks harmless, because it barely
moves a fitted centre. It moves every error bar and every model-selection
verdict, and the ladder choosing how many components a line needs reads
chi-squared. Refit it for your detector.

## What the fit layer assumes

`linefit.fit_condition` fits repeats of one condition jointly: shared
physical widths, per-trace centre, amplitude, and linear background. It
assumes nothing about which atom produced the line. It does assume the
symmetric kernels (Lorentzian, Gaussian, two-sided-exponential transit)
convolved with one asymmetric mechanism. If your system has a second
asymmetric mechanism, add it in `lineshape.py` and extend the model-form
study ([`scripts/run_modelform.py`](../scripts/run_modelform.py)) so the
data get to vote on it.

## The instrument to port first

The tooth-labelling defect the section above guards against was found by
looking at a picture rather than by reading a number, and no fitting stage
draws the traces it does not fit.
[`scripts/make_qc_gallery.py`](../scripts/make_qc_gallery.py) closes that
gap by drawing every trace in the dataset once. The unit of presentation is
the condition: one page per condition, every repeat of it as a row, on one
shared vertical scale for the whole page. Each row carries the signal with
the drawn model, the fitted window marked at both edges, and a residual
standardised by the error the fit weighted each sample with. The shared
scale is the point, because the question a page answers is whether repeats
agree, and rows that each auto-scale cannot answer it.

That layout is worth copying before any of the physics, since it is where a
new system's first surprises arrive as pictures instead of as numbers. It
gates nothing, carries no data fingerprint, and its output is untracked
under `private/qc_gallery/`, rebuilt from the repository alone.
[`DATA.md`](DATA.md) section 4 describes it as the inspection instrument for
this dataset.

## Three radiation fields, and the tests that say whether yours matter

Any hot cell has three, and this repository checked all three only after being
asked about them one at a time. Each has a one-line test you can run on your own
transition before writing any code.

**The light you detect, trapped.** Compute the optical depth over the shortest
path out, $\tau = n\sigma L$, using the distance from your excitation region to
the nearest exit rather than the cell's radius, which is the correction this
record had to make. Below $\tau\approx1$ ignore it. Above it, trapping rescales
your amplitude and leaves your lineshape alone, because the escape probability
is the same at every point of a frequency scan. It stops being harmless when it
differs *between* your lines, which happens as soon as two lines overlap the
ground-state absorption differently.

**The other colours of your own cascade.** If your upper state decays through an
intermediate, those legs are radiating too, and the reflex that they are
negligible because they are infrared is wrong: at 1324 and 1367 nm here they
absorb as strongly per lower-state atom as the detected 795 nm line does. What
saves you is population, not wavelength. The test is an inversion check: if your
drive refills the upper state faster than the intermediate empties, those legs
are inverted where the atoms are and cannot pump anything back up.
`scripts/run_trapping_channels.py` is the worked version.

**The cell's own thermal glow.** One number decides it, and it decides it
brutally. Compare $h\nu/kT$ for each transition of your cascade against the
blackbody peak, which for photon number sits near 9.1 µm at 400 K. Here every line is between 0.79
and 2.8 µm, so $h\nu/kT$ runs 26 to 45, the occupation numbers are $10^{-12}$ to
$10^{-20}$, and thermal light does nothing at all. **This is the test that
flips** if your levels are higher: a transition with a 10 µm neighbour has an
occupation number of order 1 and lives in a different regime. Watch the smallest
gap out of your upper state, not the one you drive.
`scripts/run_blackbody_channels.py` is the worked version, and it also computes
the blackbody AC-Stark shift, which is hundreds of hertz here rather than the
~1 Hz a ground state alone would give, because the excited state's own
resonances sit inside the thermal band.

## Getting the branching fraction for your cascade

If your upper state can decay into a ground level you are not driving, atoms
leave your line mid-transit and your effective interaction time shortens. The
fraction that does is one number per line, and **the naive answer is wrong**.

The naive answer is the degeneracy weight of the undriven level,
$(2F'+1)/\sum_F(2F+1)$. This repository used it, published it, and corrected it:
it is too large, here by a factor 0.596. The correction is a closed form and
costs nothing to evaluate:

$$f = \frac{2F'+1}{\sum_F (2F+1)} \times \sum_J b_J \cdot 2(1-p_J)$$

where $b_J$ is the branching into each fine-structure leg and $p_J$ is the
probability that the electron's $m_J$ survives the two-step cascade through that
leg. For $S\to P\to S$ it is $5/9$ through $J=1/2$ and $7/9$ through $J=3/2$,
giving $8/9$ and $4/9$. No nuclear spin appears in the derivation, so the same
two fractions serve any isotope and any driven level, which is worth checking
rather than trusting: `scripts/run_zeeman_depletion.py` verifies it on the full
Zeeman manifold and again as an exact-rational density matrix.

Two traps this record fell into and you can skip. **The intermediate levels that
cannot reach your undriven ground state at all** are real and are not a
correction you may drop: a $J=1$ photon cannot change $F$ by two, so some
populated intermediate levels return the atom to where it started. They cancel
against the enhanced paths exactly, but only once you sum them all. And **the
per-line spread is the only thing in the width budget that differs between your
lines**, so it is the one handle that can separate pumping from saturation and
from the light shift without a stable frequency reference. Whether you can spend
it is arithmetic: here the spread is 3 kHz, at the light shift this dataset can
actually bound, against an 88 kHz block scatter, so
the answer was no by a factor of twenty to forty.

## Two masses in one cell

If your species has two abundant isotopes, or you run an isotopologue mixture,
they do not share a transit width: it goes as the thermal speed, so it goes as
$1/\sqrt{m}$. Here that is 1.169 per cent, worth 11.4 kHz.
`linefit.transit_fwhm_at_T(..., isotope=)` shows the shape of the fix, and its
default is deliberately the shared behaviour, because against a density lever
the split is almost all a constant offset that a free per-line core width
absorbs. What reached the collisional coefficient here was 0.41 per cent of one
standard error. Where it does not hide is any observable that resolves the
Doppler pedestal, where the same fraction is megahertz and separable.

## The platform axis, for a reader with no nanofibre

The pipeline is platform-neutral and the fibre material is deliberately
separable. If you are adapting this record to another transition, 5S to 6D
say, on a vapour cell and nothing else, the fibre thread is three surfaces
and you can skip them whole: [big-picture chapter 6](big_picture/06_next-nanofibre.md),
the second scenario of [chapter 9](big_picture/09_the-campaign-cases.md),
and [the sized fibre candidate](notes/onf_candidate.md). Nothing in the
method chapters, the results, the fit layer or the seam map below depends on
them.

What is actually platform-specific is narrower than it looks. The geometry
enters the model in exactly one seam, the intensity profile closure of
`model_profile` (the deep seam above), and the transit kernel's reference
width. A cell with a focused beam, a guided evanescent field and a hollow
core are three closures over the same machinery, and the fibre files above
are one worked instance, not a dependency.

## What transfers with no edits at all

The statistical machinery holds nothing about rubidium: the noise-law
fitting, the identifiability and coverage studies, the model comparison
ladder, the profile-likelihood bound constructions, and the repository
guards (the canonical-value test, the figure fingerprint, the results status
tags). [`methods/06_the_statistics.md`](methods/06_the_statistics.md)
derives each one.

## The eighteen names you can import

`import rb5s6s` gives an eighteen-name public surface, and it is deliberately
small: every name on it is **pure**, meaning it computes and does not read the
repository, so it works from an installed wheel with no data alongside it. That
is checked by [`tests/test_package_surface.py`](../tests/test_package_surface.py),
which also checks that importing the physics does not drag in a module that
reads from disk.

```python
from rb5s6s import (
    # the lineshape and the light-shift distribution
    model_profile, composite_profile, stark_ramp, stark_ramp_axial_moments,
    stark_shift_S0_mhz,
    # the atomic inputs, recomputed rather than tabulated
    delta_alpha, alpha_5s, alpha_6s, two_photon_matrix_element,
    two_photon_rabi_hz,
    # the constants a caller most often needs to override
    W0_MEASURED_M, RHO_RETRO, GAMMA_NAT_HZ, TAU_6S_S, LAMBDA_LASER_M,
    DELTA_ALPHA_AU, transit_fwhm_from_w0, __version__,
)
```

Everything else is reached through its module. Six modules read from disk
(`config`, `ingest`, `qc`, `rate_model`, `ruler`, `cavity_scan`), and from an
installed wheel their paths resolve inside site-packages, where the
directories are not. Those six split into two contracts, and the split is
deliberate.

The ones that require the repository raise `config.RepoDataMissing` naming
what needs cloning, rather than resolving a path into site-packages and
failing somewhere stranger later: `ingest.load_manifest`,
`rate_model.load_clock`, `cavity_scan.load_scan` on its default path, and
`config.require_repo_data` itself.

The ones that degrade raise nothing: `qc.outlier_files` returns an empty set
and `ruler.campaign_rate_relsyst` returns 0.0 when their tables are absent,
so a checkout without a quality or a ruler run behaves exactly as it did
before. Each says so where it is defined.

## Two worked examples

**The whole loop.** [`scripts/run_stark_joint.py`](../scripts/run_stark_joint.py)
is the template for a multi-session joint fit: sessions with different
instruments and different frequency axes, tied by shared physics, with every
nuisance either fitted or bounded and every robustness check written into
the results CSV. Reading it top to bottom is the fastest way to see how the
parts compose.

**The smallest adaptation, one new beam on an existing cell.** Section 5.1
of [`FUTURE_TRANSITIONS_titsapph.md`](FUTURE_TRANSITIONS_titsapph.md) runs a
proposal through these same seams. One auxiliary beam in the telecom O band
would be pointed at the existing cell and its wavelength scanned across a
zero crossing of the differential polarizability, with the shift it induces
read off the lineshape rather than off an absolute frequency reference. The
constants file would gain the perturber's polarizability inputs and the
config file its power and waist. The shift density, the noise law, the
frequency axis and the fit layer would not move at all, which is what makes
it the cheapest adaptation in this document. None of it has been run, and
the section is written as a proposal.

## The cascade seam, added 2026-08-19

`rb5s6s/cascade.py` carries the ground-level population dynamics under
repeated excitation: how much of the driven hyperfine level survives an
atom's transit, and therefore how far an observed amplitude sits below the
transition strength that would predict it.

**What is general.** The dynamics. `surviving_fraction` is geometric decay
under a per-cycle loss with an optional repumping term, and holds for any
two-level ground manifold driven out of one level and returned to the other.
`CascadePopulations` and `amplitude_factor` are the same arithmetic in a
form callers can use.

**What is this transition's.** The four numbers in `BRANCHING_F` and the
line-to-isotope map in `DRIVEN_F`. Both are rubidium 5S-6S. For another
species or another line, replace the table.

**Where the numbers come from, and the seam that matters.** The branching is
the committed output of `scripts/run_zeeman_depletion.py`, which carries
every Clebsch-Gordan coefficient on the full Zeeman manifold and needs sympy
from the `cascade` extra. `branching_from_manifold` recomputes it exactly
where sympy is present and raises rather than falling back, so a caller
asking for the exact computation never receives the table by accident. A
plain install gets the physics from the table without the dependency.

**The guard.** `tests/test_cascade_invariants.py`, which checks population
conservation, non-negativity, the zero-cycle and zero-excitation identities,
monotone depletion, the unrepumped and repumped steady states, the
isotope-to-line assignment, and that the transit average lies between the
endpoints it averages. Those checks need no sympy, because they test the
dynamics rather than the table.

**A duplication this seam removed.** `rb5s6s/stark.py` carried its own
literal copy of the four branching values and its own literal natural width.
Both now come from their source, so a change to either cannot leave that file
behind. Reproduced exactly on collapse: the width is byte-identical and three
of four branchings are unchanged, with 4121 gaining precision from 0.372478
to 0.372478177, a relative move of 5e-7.

## The blackbody seam, added 2026-08-19

`rb5s6s/blackbody.py` answers a design question rather than reporting a
number: above which temperature does thermal radiation enter the systematic
budget, at a given target precision.

**What is general.** `Transition`, `occupation`, `einstein_a` and
`stimulated_rate` know nothing about rubidium. `t_max` is a solver over any
shift model.

**What is this transition's.** `RB_5S6S_SHIFT_HZ`, the four committed
differential-shift values, and the exponent fitted to them. Another species is
another preset.

**The seam that matters, and the one deliberately not crossed.** The
differential shift is a principal value through the 6S-6P poles, and
`scripts/run_blackbody_channels.py` records three earlier attempts that were
each wrong in an instructive way. Reimplementing that integral in the library
would create a second source of truth for a delicate number, so the committed
values are carried and interpolated instead, exactly at the four points and
flagged as extrapolation outside them.

**The guard.** `tests/test_blackbody_boundary.py`, which checks that the
interpolation reproduces every committed point exactly, that occupation sits
on the Wien tail for this cascade, that Einstein A scales as the cube of
frequency, that the ceiling family moves the right way with the target, and
that correcting the shift raises the ceiling.

## The model-comparison seam, added 2026-08-19

`rb5s6s/model_compare.py` computes an evidence vector.
`interpret_model_comparison` judges it. They are separate functions on
purpose, and the invariant is tested: no single statistic in the output can
return a preference.

**What is general.** All of it. Nothing in this module knows about rubidium.

**What is campaign-specific.** Nothing, except that the effective-sample-size
convention it enforces is this repository's, described in
`rb5s6s/sharing_bic.py` and not a theorem.

**The trap this seam closes.** The effective BIC needs the whitened
chi-square against the effective count, both terms. A raw chi-square against a
reduced penalty inflates the fit's gain by roughly the correlation time while
lowering its parameter cost, and on this archive that reverses a verdict. The
module refuses the half-treatment rather than computing it.

**Status.** Uncalibrated, stated in the docstring and in the output, until a
bootstrap coverage run measures the selection statistic on this noise
structure.

**The guard.** `tests/test_model_compare.py`, including the no-verdict
invariant and the refusal of the half-treatment.

## The forecast seam, added 2026-08-19: the digital twin

`rb5s6s/forecast.py` runs the package backwards. Every other seam takes data
and returns parameters. This one takes parameters and returns data, then fits
that data back and reports what an experiment would achieve. An apparatus that
does not exist yet is therefore a thing that can be measured.

**What is general.** All of it. `synthetic_traces` builds traces from any line
model this package can evaluate, with noise either as a fraction of peak or
through a MEASURED noise law evaluated by `rb5s6s.noise.sigma_of_v`, so a
characterised detector simulates under its own law rather than under a
convenient one. `forecast_precision` is a Monte-Carlo over
`synthetic_traces` into `fit_condition` at a chosen design, returning median
parameter uncertainties, the scalings measured by re-running the study at
scaled designs rather than by asserting exponents, and the ceilings the model
layer supplies. `external_constraint_gain(rho)` returns $\sqrt{1-\rho^2}$,
the fraction of its uncertainty a parameter keeps once its correlated partner
is measured independently. `comb_tooth_weights` returns the two-photon comb
tooth weights in the zero-delay limit and cell-averaged beyond it, where the
retro delay maps to a position-dependent effective modulation depth, with
the identity tested against the explicit pathway sum. Its reciprocal is the factor bought, and it depends
on the correlation alone, so it is a property of the design rather than of the
sample size.

**What is campaign-specific.** Nothing in the module. `examples/campaign_twin.py`
is the campaign-specific instance, and it embeds every committed input it needs
as a provenance-tagged constant rather than reading `results/`, so it runs from
a clone with no data present.

**The trap this seam closes.** A design study that reports what more data buys
will always report an improvement, because more data always shrinks an error
bar. It will not tell you that the pair you care about stays degenerate. Run
`width_identifiability` or read `corr_laser_coll` alongside every forecast: on
this line the two widths correlate at about -0.92, and that number does not
move with span or with repeat count. More data fixes noise and never fixes
identifiability, and the twin is where the difference becomes visible in
minutes.

**Status.** Validation class iii, design: sensitivity checks with stated
limits. A forecast holds for its stated truth, design and noise model and for
nothing else, which is why every returned mapping carries an `assumptions`
entry.

**The guard.** `tests/test_forecast.py`, including the no-repository-data rule
and a reduced end-to-end run of the campaign twin.
