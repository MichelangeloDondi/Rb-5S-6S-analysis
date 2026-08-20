# The nanofiber candidate: three instruments one apparatus provides

**Status.** DESIGN NOTE, written 2026-08-21. Every number here is produced by
[`run_onf_candidate.py`](../../scripts/run_onf_candidate.py) into
[`onf_candidate.csv`](../../results/onf_candidate.csv), where each row carries
its basis: a committed input of this repository, a cited outside number, an
assumed lab parameter waiting to be replaced, or arithmetic on those. Nothing
here is a measurement. The lab facts this repository does not know are marked
in the CSV with the word REPLACE and listed at the end of this note.

**The context that makes this worth sizing.** The width channel's intercept,
near 0.4 MHz, decomposes as laser + transit + residual, and the ladder that
attributes it needs an independent lever on each slot. Density separates the
collisional slope from the intercept and nothing more. The laser slot is the
identifying one, and the kernel window established that the cell data
constrain its shape only at one corner. The lab holds an optical nanofiber
with a two-colour standing-wave trap, built for Rydberg-atom work, usable
with the trap dark. One apparatus provides three distinct instruments, sized
below in the order of what they remove from this record's uncertainty.

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
cancellation. The per-atom two-photon rate at 1 mW guided is about 870 times
the 225 mW cell rate, because the mode area is half a square micron. That
intensity carries the drive's own light shift with it: scaling the committed
cell value gives 10 MHz at 1 mW, so the spectroscopy setting is tens of
microwatts, where the shift is at the cell's own 0.3 to 0.5 MHz scale and the
per-atom rate still exceeds the cell's. About three atoms occupy the
evanescent shell on average at MOT density, which is the signal regime the
Rydberg-near-fiber detection already operates in.

## B. The atom-surface tail: a C3 for the 6S state

Evanescent excitation samples atoms 50 to 300 nm from silica. The 6S state is
far more polarizable than the ground state, so the differential van der Waals
shift red-shifts the line by an amount set by distance: 1.7 to 4.2 MHz at
100 nm and 13 to 34 MHz at 50 nm, against a cold line a few MHz wide. The
near-surface atoms therefore form a resolved red tail whose shape is a
measurement of the 6S versus silica C3, a coefficient with no published
measurement that we know of, obtained with the mild lasers of this programme
on exactly the atom-surface machinery the Rydberg-near-fiber work needs at
higher n. The C3 ratio band in the CSV brackets the expectation and is the
first thing a Casimir-Polder sum should replace.

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

## Lab facts to replace before this enters the ranking

* The fiber diameter, hence the guided-mode index at 993 nm and the decay
  length. The CSV carries 1.08 to 1.25 as a band.
* The effective mode area at the surface, carried as 0.5 square microns.
* The species and temperature of the MOT, carried as Rb at 150 uK.
* Transmission of the existing pigtails at 993 nm.
* A Casimir-Polder sum for C3 of the 6S state, replacing the 3 to 6 band.
* The residual DC Stark from adsorbates on the fiber surface, which shifts
  the 6S state and is both a systematic here and a diagnostic the Rydberg
  work wants measured.

The cited outside number is the ground-state coefficient against fused
silica, C3 of about 5.6e-49 J m cubed, from the surface-interaction
literature for Rb on glass. Everything else is either committed in this
repository or labelled as an assumption in the CSV.
