# The nanofiber candidate: three instruments one apparatus provides

**Status.** DESIGN NOTE, written 2026-08-21. Every number here is produced by
[`run_onf_candidate.py`](../../scripts/run_onf_candidate.py) into
[`onf_candidate.csv`](../../results/onf_candidate.csv), where each row carries
its basis: a committed input of this repository, a cited outside number, an
assumed lab parameter waiting to be replaced, or arithmetic on those. Nothing
here is a measurement. The apparatus parameters this repository does not
know are marked in the CSV with the word REPLACE and listed at the end of
this note.

**What is already established on this platform, and what is not.** This note
was first written without its own literature, and the correction matters
enough to state at the top. The 5S to 6S transition has already been driven at
an optical nanofibre with cold atoms, in the lineage this record belongs to.
[Rajasree 2020](../lit/rajasree2020spin.md) drove it through the evanescent
field of a 400 nm fibre at 25 to 40 counts per millisecond, and established
the polarisation law for it, including that the guided mode's longitudinal
component leaves the circular configuration with a MINIMUM near 13 per cent in
theory and 25 per cent in practice rather than a null.
[Gokhroo 2022](../lit/gokhroo2022.md) observed a two-peak pushing profile near
the fibre on this exact line and did not model it: no fitted lineshape, and no
Casimir-Polder content anywhere in the paper. A prior-art audit recorded in
that literature note finds that no one has modelled it since.

So the open problem here is a QUANTITATIVE NEAR-SURFACE LINESHAPE, not a
standalone surface coefficient and not a feasibility demonstration. Signal
feasibility is settled by a published measurement on this platform. What this
note sizes is what such a measurement would additionally buy the vapour-cell
record, which is a different question and the one the campaign ranking needs
answered.

**The context that makes this worth sizing.** The width channel's intercept,
near 0.4 MHz, decomposes as laser + transit + residual, and the ladder that
attributes it needs an independent lever on each slot. Density separates the
collisional slope from the intercept and nothing more. The laser slot is the
identifying one, and the kernel window established that the cell data
constrain its shape only at one corner. The platform this note sizes is an
optical nanofibre with a two-colour evanescent trap, the configuration of the
published lineage above, operated with the trap dark where the spectroscopy
wants it. One apparatus provides three distinct instruments, sized below in
the order of what they remove from this record's uncertainty.

## A. Cold atoms, trap off: an independent laser-width instrument

MOT atoms drift through the evanescent field of the guided 993 nm mode. At
150 uK the transit contribution is about 0.14 MHz across the 210 to 390 nm
decay length, and at MOT density the collisional term is about 180 Hz, which
is nine orders below the cell's. What remains is

$$\Gamma_{\rm line} \approx \Gamma_{\rm nat} + \Gamma_{\rm laser} + 0.14\ \text{MHz}$$

with the natural width 3.49 MHz known from the committed lifetime. The laser
contribution, 1.5 to 1.9 MHz FWHM in the cell fits, is then a large and
resolvable fraction of a line whose every other component is known or
negligible. That is a direct measurement of the laser's width including its
Lorentzian content, the quantity the kernel window calls Gamma_L,equiv and
can only bound from cell data, because in the cell it is degenerate with the
collisional width at fixed condition and correlated at 0.82 to 0.98 with the
headline coefficient even across the density ladder.

Counter-propagating guided modes preserve the two-photon Doppler
cancellation, and the polarisation law governing the rate is
[Rajasree 2020](../lit/rajasree2020spin.md)'s: proportional to the squared
degree of linear polarisation, with the circular configuration suppressed to a
minimum rather than a null by the longitudinal field. Detectability is settled
there by measurement, at 25 to 40 counts per millisecond on this platform and
this line, so the ratios that follow are context for the light-shift budget
rather than the case for seeing the signal. The per-atom two-photon rate at
1 mW guided is about 870 times the 225 mW cell rate, because the mode area is
half a square micron. That
intensity carries the drive's own light shift with it: scaling the committed
cell value gives 10 MHz at 1 mW, so the spectroscopy setting is tens of
microwatts, where the shift is at the cell's own 0.3 to 0.5 MHz scale and the
per-atom rate still exceeds the cell's. About three atoms occupy the
evanescent shell on average at MOT density, which is the signal regime the
Rydberg-near-fiber detection already operates in.

## B. The near-surface lineshape, and the surface potential it reads

Evanescent excitation samples atoms 50 to 300 nm from silica, where the
atom-surface potential shifts 5S and 6S differently and pulls the line red by
an amount set by distance. In the near-field Casimir-Polder form the
differential shift is 1.7 to 4.2 MHz at 100 nm and 13 to 34 MHz at 50 nm,
against a cold line a few MHz wide, so the near-surface atoms make a resolved
red tail rather than a perturbation.

**The potential has two components and this note's first version had one.**
[Pennetta 2026](../lit/pennetta2026.md) measures, on this exact class of
platform, Casimir-Polder attraction PLUS an electrostatic term from surface
charges on the silica. The second is device- and time-dependent, so it is
calibrated per run and carried as a systematic rather than as a universal
constant. That also relocates a caveat this note had misplaced: adsorbate
fields are not an external nuisance to be listed separately, they are part of
the potential being measured. And the near-field C3 over z cubed form crosses
to a retarded C4 over z to the fourth at larger distance, a crossover
[Ton 2026](../lit/ton2026.md) measures directly while reading a kilohertz
Casimir-Polder shift out of a spectroscopic lineshape. That paper is the
template for the estimator here: the surface shift is read as a DISTRIBUTION
over the atoms' distance from the surface, by the same moment machinery that
reads the light-shift distribution, so one method handles both
inhomogeneities.

Read that way the measurement is the quantitative completion of
[Gokhroo 2022](../lit/gokhroo2022.md)'s observed pushing profile, and a C3 for
the 6S state against silica is an output of the fitted model rather than the
goal. A feasibility bound travels with it:
[Piotrowski 2026](../lit/piotrowski2026.md) shows probe scattering heats
nanophotonic-trapped atoms, so near-field probing is inherently transient and
the powers quoted here bound an integration window rather than a steady state.

## C. Hot vapor: the transit kernel where it is the whole line

Thermal atoms cross the evanescent field in about a nanosecond, so the
transit width scales from 0.96 MHz in the cell to roughly 230 MHz at the
fiber, from a small component of the line to essentially all of it. The
transit kernel, whose Gaussian versus cusp choice carries 18 to 23 per cent
of model form on the collisional coefficient and cannot be resolved inside
the cell line, becomes the measured object. Two honest caveats. The
evanescent intensity profile is exponential rather than Gaussian, so this
tests the transit machinery on a second geometry rather than re-testing the
cusp itself. And hot rubidium degrades nanofiber transmission by adsorption,
and a degraded fiber is a loss to the Rydberg programme, so this
instrument ranks last and belongs on a sacrificial fiber if it runs at all.

## The free rider: the Stark geometry seam

`model_profile` takes a pluggable closure over `stark_from_intensity_profile`
with its own sampled intensities and volume measure. That seam was designed
for a geometry change and has never had one. The evanescent gradient is the
second geometry, and at 1 mW guided the light shift is the dominant feature
of the line by design, so the same apparatus that is a hazard for instrument
A is a calibrated Stark-model test at full power. No new code is required.

## The joint Fisher forecast: what the prior is worth, computed

The design case is now arithmetic rather than prose.
`run_kernel_identifiability.py` carries a joint cell plus ONF Fisher block
(the `joint_cell_onf` rows of
[`kernel_identifiability.csv`](../../results/kernel_identifiability.csv))
built on the record's own estimator structure: four temperatures, the density
ladder, per-condition nuisances projected out, conditions weighted by signal,
and the fit window taken from the estimator's own `adaptive_halfwidth` rule
rather than chosen. That last point was a correction. A first version
inherited a narrow fixed window from an adjacent code block, an adversarial
verification pass showed the truncation moved the headline ratio by 27 per
cent while the validation gate passed at either window, and the fix removes
the window as a free parameter. The block still validates itself before it
forecasts: run in the record's own two-parameter form it gives a correlation
of minus 0.912 against the committed minus 0.82 to minus 0.89, close enough
to license the forecast and flagged in its own output row either way.

Four numbers carry the case.

* Freeing the Lorentzian laser content, which is what an honest K3 fit must
  do, inflates the coefficient's statistical error by a factor 1.71. That is
  what kernel honesty costs with cell data alone.
* An ONF measurement of BOTH laser shape components at one fifth of the
  cell's own precision on them brings the error to 0.36 of the free fit,
  buying back the whole inflation and more, on data already taken.
* A measurement of the Lorentzian content ALONE has an exact floor at 0.585
  of the free fit however precise it is, because the free Gaussian width
  stays correlated with the coefficient. The design consequence decides the
  instrument: the ONF must measure the laser's shape, both components, which
  is exactly what the cold trap-off mode does and a single wing measurement
  would not.
* The relative language hides an absolute demand, so the block anchors it:
  matching the forecast to the committed beta error puts the cell's own
  determination of each laser parameter near 0.06 MHz, and the one-fifth
  prior above therefore asks the ONF for roughly 12 kHz on each component.
  Useful gains begin already at the 0.06 MHz level, which costs the ONF
  little, and the factor-three gains need the 12 kHz level, which is a real
  demand on a line a few MHz wide and belongs in the instrument's error
  budget from the start.

The ceiling with both components pinned exactly is 0.24 of the free fit.
Multiplied by the 1.71 inflation this is 0.41 of the TWO-parameter fit,
which equals the square root of one minus the validation correlation
squared, so the forecast agrees with the covariance algebra it must reduce
to. The shared-path condition below applies to every row.

## The shared-path condition the laser transfer stands on

Every use of an ONF laser measurement as a prior on the cell inference
assumes the laser at the fiber is the laser at the cell. Fiber transport
adds acoustic and thermal phase noise, so that assumption is a design
requirement, not a fact, and it is met in one of two ways. Either the drive
is split and both instruments run SIMULTANEOUSLY, cell and fiber recording
the same laser at the same moments, so the cell's own drift machinery
becomes the live reference and everything the fiber path adds shows up as a
cell-versus-fiber difference. Or the fiber-added noise is measured once,
bounded, and carried as a term in the transfer. The simultaneous
configuration is the stronger of the two and costs a beamsplitter. Nothing
in this repository yet measures either, which is why the forecast rows are
expectations and the transfer condition is named here rather than assumed
away.

## What this candidate does not buy

A better collisional coefficient. There is no density ladder in a MOT and no
controlled density near a hot surface, so the cell campaign keeps the
beta_self measurement. The candidate feeds the two intercept slots the cell
cannot separate and opens one new coefficient. With the two-colour trap ON
the trap light shifts the 6S state strongly and inhomogeneously, so
spectroscopy wants the trap dark or strobed, which is why the trap-free mode
leads this note.

## Apparatus parameters to replace before this enters the ranking

* The fiber diameter, hence the guided-mode index at 993 nm and the decay
  length. The CSV carries 1.08 to 1.25 as a band.
* The effective mode area at the surface, carried as 0.5 square microns.
* The species and temperature of the MOT, carried as Rb at 150 uK.
* Transmission of the existing pigtails at 993 nm.
* A Casimir-Polder sum for C3 of the 6S state, replacing the 3 to 6 band.
* A per-run calibration of the electrostatic surface-charge term, which
  [Pennetta 2026](../lit/pennetta2026.md) shows is a component of the
  potential rather than an external nuisance.
* Which fibre. The cold-atom 5S-6S measurement of
  [Rajasree 2020](../lit/rajasree2020spin.md) used a 400 nm nanofibre and the
  estimates here follow it. Nanofibres in this platform class span roughly
  400 to 650 nm, and the decay length, and with it the transit and surface
  rows, scale with the diameter, so the estimates are re-run for the actual
  fibre before any of them is quoted.

The cited outside numbers are the ground-state coefficient against fused
silica, C3 of about 5.6e-49 J m cubed from the surface-interaction literature
for Rb on glass, and the platform results carried in this repository's own
literature notes for [Rajasree 2020](../lit/rajasree2020spin.md),
[Gokhroo 2022](../lit/gokhroo2022.md),
[Pennetta 2026](../lit/pennetta2026.md), [Ton 2026](../lit/ton2026.md) and
[Piotrowski 2026](../lit/piotrowski2026.md). Everything else is either
committed in this repository or labelled as an assumption in the CSV.
