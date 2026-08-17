# The analysis library

> The CONCEPTS these modules implement, one page each with a runnable
> example, are in [`docs/wiki/`](../docs/wiki/README.md). Start there for
> what a Voigt degeneracy or a profile likelihood is, and here for which
> function computes it.

The library computes and the scripts orchestrate. Every module in this package
takes arrays, blocks or tables and returns numbers, and none of them decides
where the data comes from or where a result goes. Those decisions belong to the
drivers in `scripts/`, which read the frozen dataset described in
[`data_raw/README.md`](../data_raw/README.md) and write the tables described in
[`results/README.md`](../results/README.md). The library names a directory in
one place only, the anchors at the top of `config.py`, and the few loaders that
default to them accept an explicit directory instead. The separation is what
makes the documentation traceable in a single direction: a number quoted in a
document is produced by a named function here, applied to that dataset, and
committed as a row in a CSV, which is what lets
`tests/test_docs_canonical.py` check the quoted values against the files that
produced them.

Two files are inputs rather than computation, and the split between them is a
rule. `constants.py` holds measured or cited values, the quantities nature or
the bench fixed, and every one of them carries a provenance tag recording
whether it is published, extracted from this archive by this pipeline, derived,
an order-of-magnitude envelope, or still open. `config.py` holds the choices
that move a number without changing the physics: fit windows, smoothing widths,
thresholds, random seeds, and the pre-registered trimmer and outlier
parameters. The test of where a value belongs is what moving it does. If
changing it changes what the code can conclude rather than how it gets there,
it belongs in `constants.py`. Nothing numeric is hard-coded outside those two
files.

Most modules below have a driver of their own in `scripts/`. The module map in
[`docs/methods.md`](../docs/methods.md) lays out the stage numbering that runs
through the code comments and the documentation, and marks the three modules
that produce no results table.

## Ingest, quality and the frequency axis

| module | what it computes | documented in |
|---|---|---|
| `ingest.py` | reads one oscilloscope CSV and the dataset manifest, validating the format rather than trusting it, and returns time in milliseconds with no frequency calibration applied | [The measurement](../docs/methods/01_the_measurement.md) |
| `qc.py` | per-trace quality metrics that fit no lineshape, and a symmetric comparison of the experimenter's curation against them, each trace against its same-condition siblings | [The measurement](../docs/methods/01_the_measurement.md), [DATA.md](../docs/DATA.md) |
| `noise.py` | the empirical noise law against signal level from second differences, and the residual correlation time that later fits inflate their errors by | [The statistics](../docs/methods/06_the_statistics.md) |
| `ruler.py` | the sweep rate from the EOM comb: autocorrelation initialisation, one simultaneous fit of the whole tooth grid, and the amplitude test of the tooth labelling | [From volts to a frequency axis](../docs/methods/05_the_frequency_ruler.md), [ruler validity and trimmer note](../docs/notes/ruler_validity_and_trim_prereg.md) |
| `rate_model.py` | the time-resolved sweep rate, one straight line per session and peak with scatter-based covariance, in place of a before-and-after bracket average | [ruler validity and trimmer note](../docs/notes/ruler_validity_and_trim_prereg.md) |
| `trim.py` | the residual-tail trimmer: where a triangular sweep re-crosses the line, a cumulative-sum onset turns the unmodelled copy into a sample mask, never into a quality flag | [ruler validity and trimmer note](../docs/notes/ruler_validity_and_trim_prereg.md), [From volts to a frequency axis](../docs/methods/05_the_frequency_ruler.md) |

## The lineshape and the fitting machinery

| module | what it computes | documented in |
|---|---|---|
| `lineshape.py` | the kernels and their convolution, on the transition axis: one Lorentzian carrying the natural and collisional widths, the two-sided-exponential transit cusp, the laser Gaussian, and the triangular AC-Stark ramp | [The lineshape](../docs/methods/02_the_lineshape.md), [The composite model](../docs/methods/04_the_composite_model.md) |
| `linefit.py` | the joint fit of one condition's repeats, sharing the shape while each trace keeps its own amplitude, centre and linear background, and returning the full covariance | [The lineshape](../docs/methods/02_the_lineshape.md), [The statistics](../docs/methods/06_the_statistics.md) |
| `density.py` | rubidium vapour number density against temperature from the liquid-phase vapour-pressure correlation, and the density-scale systematic that everything inversely proportional to it inherits | [The lineshape](../docs/methods/02_the_lineshape.md) |
| `beta.py` | the collisional self-broadening coefficient, fitting every temperature of one peak at once with the collisional width tied to the density law, so the density lever breaks the width degeneracy | [The statistics](../docs/methods/06_the_statistics.md), [What we found](../docs/methods/07_what_we_found.md) |
| `global_fit.py` | the hierarchical fit of all peaks and temperatures together, sharing the laser width per temperature and the collisional coefficient per isotope, which turns the isotope equality into something testable | [The statistics](../docs/methods/06_the_statistics.md) |
| `lever_crosscheck.py` | the packaged cross-check: the same fit across the model-form grid, returning one coefficient per isotope with separate statistical, model-form and beam-waist error bars, plus the leave-one-out scans and the density-anchor lever test | [What we found](../docs/methods/07_what_we_found.md) |
| `stark.py` | the AC-Stark coefficient from width against power at fixed temperature, one coefficient shared across the peaks while each floats its own power-independent core width | [The AC-Stark ramp](../docs/methods/03_the_ac_stark_ramp.md) |

## Model comparison, identifiability and the observables

| module | what it computes | documented in |
|---|---|---|
| `modelform.py` | the smooth Gaussian against the cusped transit exponential, and both against a form that carries each, scored by information criterion at equal parameter count | [The statistics](../docs/methods/06_the_statistics.md), [What we found](../docs/methods/07_what_we_found.md) |
| `model_ladder.py` | the nested ladder that asks which kernels the data demand, from a bare Voigt up to a free AC-Stark ramp, one physical mechanism per rung | [The statistics](../docs/methods/06_the_statistics.md) |
| `identifiability.py` | the correlation structure and condition number of the three-width block, and the two-dimensional profile likelihood that tests whether that local covariance can be trusted | [The statistics](../docs/methods/06_the_statistics.md) |
| `coverage.py` | injection and recovery of the bound construction on synthetic data with the archive's own structure, returning bias, coverage, and the false-positive rate at zero effect | [The statistics](../docs/methods/06_the_statistics.md) |
| `sharing_bic.py` | whether the data can pay for a free laser width per block, scored on the effective sample size that correlated samples allow rather than the raw point count | [The statistics](../docs/methods/06_the_statistics.md) |
| `resolving.py` | for each observable, how far it moves across the sweep divided by how much it scatters when nothing physical changes, and a permutation null under the assumption that block scatter is independent | [results/README.md](../results/README.md) |
| `amplitudes.py` | line areas and the degeneracy law, relative strengths set by abundance and ground-state population alone, using the integrated area rather than the peak height so the width cannot leak in | [The composite model](../docs/methods/04_the_composite_model.md) |

## The physics models

| module | what it computes | documented in |
|---|---|---|
| `transit_mc.py` | the transit lineshape from first principles, over the three-dimensional velocity distribution, the beam growing along the collection column, and the crossing-flux weight that makes the cusp finite | [The lineshape](../docs/methods/02_the_lineshape.md), [transit width note](../docs/notes/transit_width_resolved.md) |
| `ramp_transit.py` | whether atomic motion washes the ramp out, by change of variables: a flux-weighted moving ensemble samples the same distribution of shifts as the static one it replaces | [THEORY_NOTE.md](../docs/THEORY_NOTE.md) |
| `fringe_tail.py` | the standing-wave fringe tail of the ramp, the slow axial atoms that sit at one frozen fringe phase for a whole excitation window, and the suppression of the ramp skew that follows | [THEORY_NOTE.md](../docs/THEORY_NOTE.md) |
| `polarizability.py` | dynamic scalar polarizabilities of the two states by sum over states, the differential at the drive wavelength, the tune-out and static anchors it is checked against, and the magic crossings | [The AC-Stark ramp](../docs/methods/03_the_ac_stark_ramp.md), [THEORY_NOTE.md](../docs/THEORY_NOTE.md) |
| `hyperpolarizability.py` | the three trap-design numbers at each magic crossing, beyond the crossing wavelength itself: the fourth-order differential shift, the vector shift under imperfect polarization, and trap-photon scattering | [BIG_PICTURE.md](../docs/BIG_PICTURE.md), [CLAIMS.md](../docs/CLAIMS.md) |
| `vanderwaals.py` | the van der Waals coefficient for the two-state asymptote, from the same matrix elements continued to imaginary frequency, and the self-broadening coefficient the impact result then implies | [The lineshape](../docs/methods/02_the_lineshape.md), [difference-potential note](../docs/notes/vdw_difference_potential_and_4d_channel.md) |

## Inputs and shared utilities

| module | what it computes | documented in |
|---|---|---|
| `constants.py` | every physics and apparatus quantity, each with its provenance tag, on the transition axis unless the name says otherwise, including the closed-form transit width against beam waist | [The measurement](../docs/methods/01_the_measurement.md), [conventions](../docs/methods.md) |
| `config.py` | the analysis choices, grouped by the stage that reads them, with the reason for each default written next to it, and the directory anchors the drivers resolve their paths from | [conventions](../docs/methods.md) |
| `fitutil.py` | projection of a seed into the feasible box before a bounded least-squares call, and parameter covariance from the Jacobian by singular value decomposition rather than by forming the normal matrix | [The statistics](../docs/methods/06_the_statistics.md) |
| `_compat.py` | one numpy name resolved at import time, so the trapezoid rule works on the oldest version the manifest promises | [conventions](../docs/methods.md) |
| `__init__.py` | the package version, and the pointer to the methods document whose stage numbering the module names follow | [conventions](../docs/methods.md) |

Reading order for someone new to the code: the measurement chapter next to
`ingest.py` and `qc.py`, then the lineshape chapter next to `lineshape.py`, then
the statistics chapter next to `linefit.py` and `beta.py`. The synthetic
closure tests in `tests/` are the second half of that reading, since each one
states the answer it injects before it checks what the module recovers.
