# Adapting this pipeline

This page is for a reader with their own transition, their own cell or fibre,
and their own detector, deciding whether this machinery is worth pointing at
them. It names every seam: what to change, where it lives, what getting it
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
| the apparatus | [`rb5s6s/config.py`](../rb5s6s/config.py) | waists, powers, temperatures, file layouts, directory roots. No physics | the peak light shift quoted at the wrong intensity, since it goes as the inverse square of the waist | [`tests/test_ramp_geometry_docs.py`](../tests/test_ramp_geometry_docs.py), which recomputes the geometry tables the documents print |
| the light geometry | [`rb5s6s/lineshape.py`](../rb5s6s/lineshape.py) | the composite line model and the shift-distribution machinery. The deep seam, below | a symmetric fit to an asymmetric line, with the shift absorbed into a width | [`tests/test_lineshape.py`](../tests/test_lineshape.py) |
| the detection noise | [`rb5s6s/noise.py`](../rb5s6s/noise.py) | the noise law measured from the traces themselves, used as fit weights everywhere | error bars wrong by a factor, and a model comparison that then picks its model with confidence | [`tests/test_noise.py`](../tests/test_noise.py) |
| the frequency axis | [`rb5s6s/ruler.py`](../rb5s6s/ruler.py) and [`rb5s6s/trim.py`](../rb5s6s/trim.py) | the sideband-ruler calibration, its validity layer, and the residual-tail trimmer | one scale error on every width and every shift at once | [`tests/test_ruler.py`](../tests/test_ruler.py), [`tests/test_trim.py`](../tests/test_trim.py) |
| which traces are allowed in | [`rb5s6s/qc.py`](../rb5s6s/qc.py) and the manifest | hard flags, the group outlier rule, the exclusion register of [`DATA.md`](DATA.md) | a census that quietly empties itself | [`tests/test_qc_policy.py`](../tests/test_qc_policy.py), which forbids a hard flag from reading a quantity the physics fits |

Three of those rows need more than a row. They are the next three sections.

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
  answer by coin flip and quarantines clean combs.
  `RULER_REINDEX_CHI2_TOL` is the tolerance separating a correct relabelling
  from the false rescue of a contaminated grid, set on synthetics with known
  answers. What the ladder cannot fix is quarantined with a recorded reason
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
gap by drawing every trace in the archive once. The unit of presentation is
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
this archive.

## What transfers with no edits at all

The statistical machinery holds nothing about rubidium: the noise-law
fitting, the identifiability and coverage studies, the model comparison
ladder, the profile-likelihood bound constructions, and the repository
guards (the canonical-value test, the figure fingerprint, the results status
tags). [`methods/06_the_statistics.md`](methods/06_the_statistics.md)
derives each one.

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
