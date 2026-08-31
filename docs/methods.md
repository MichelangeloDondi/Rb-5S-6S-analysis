# Rb 5S→6S two-photon lineshape analysis

Analysis of the rubidium $5S_{1/2}\to 6S_{1/2}$ two-photon transition at
993 nm (data taken at OIST in 2025, with a fixed-lock follow-up session proposed and not yet scheduled). This
document doubles as the **methods draft** for the paper: every broadening
mechanism and every statistical choice is derived rather than asserted, and
then tied to its implementation in the code. It is written to be read
top-to-bottom by someone new to the experiment. Nothing is
assumed beyond undergraduate quantum mechanics and statistics.

> **Status.** Every result in §5 is a bound or a null, and each names the
> measurement that would lift it. Nothing here is an absolute measurement,
> because the dominant systematic, the beam waist $w_0$, is still an open
> prior. That status is stated per result in §5 and attached to the data:
> every `results/*.csv` row carries a `status` column, the provenance tag the
> README describes. All four vapour-cell deliverables (C1 collisional
> broadening, C2 laser epoch, C3 power and ramp law, C3d the Stark-coefficient
> bound) are delivered at bound or null level. Prose results are in §5, the
> auto-generated single-source-of-truth table is
> [`docs/RESULTS.md`](RESULTS.md), the prior-art delineation and collision-rate
> calibration are in [`docs/LITERATURE.md`](LITERATURE.md), and what a
> fixed-lock session would lift is in §7.

### Notation and abbreviations (defined once, used throughout)

| symbol / term | meaning |
|---|---|
| $\nu$ | frequency. **Transition axis** = the two-photon sum frequency (see §0) |
| FWHM | full width at half maximum of a lineshape |
| $\Gamma_\text{nat}$ | natural FWHM of the transition |
| $\gamma_\text{coll}$ | collisional (pressure) broadening FWHM |
| $\sigma_\text{laser}$ | laser-jitter contribution to the FWHM |
| $N$ | rubidium vapour number density (atoms $\mathrm{cm}^{-3}$) |
| $\beta_\text{self}$ | collisional **self-broadening coefficient**, $\gamma_\text{coll}=\beta_\text{self}N$ |
| $w_0$ | laser beam waist (radius at which intensity falls to $1/e^2$) |
| $\rho$ | retro-reflection power ratio (returning/forward intensity at the atoms); $S_0\propto(1+\rho)$, so $\rho=1$ is a perfect retro. This bench assumes $0.94\pm0.04$ |
| $T$ | cell temperature (K unless °C stated) |
| EOM | electro-optic modulator (our frequency ruler) |
| PMT | photomultiplier tube (the detector) |
| SNR | signal-to-noise ratio |
| WLS | weighted least squares |
| MB | Maxwell–Boltzmann (speed distribution) |
| BIC | Bayesian information criterion (model-selection score) |

All width symbols above ($\Gamma_\text{nat}$, $\gamma_\text{coll}$,
$\sigma_\text{laser}$) are **FWHM**, for direct comparison with measured
linewidths. The one exception is $\sigma_\text{eff}$ in §2.6, which is a
**standard deviation** ($\sqrt{\kappa_2}$) because it sits in a cumulant
ratio, and it is flagged again where it appears.

### The label schemes: C-results, M-modules, and CI (not the same counter)

Three separate labels recur throughout the repo and are easy to conflate:

- **C1, C2, C3, C3d, the paper's *results*** (the deliverables), indexed in
  [`docs/RESULTS.md`](RESULTS.md). C1 is collisional self-broadening
  $\beta_\text{self}$, C2 the 2025 laser-epoch width $\sigma_\text{laser}$, and
  C3 the power sweep (ramp-law predictions), with C3d its AC-Stark coefficient
  bound $S_0$. Each is a **bound or null** in the 2025 dataset.
- **M0 … M38, the analysis *modules* (pipeline stages)**, one `rb5s6s/*.py`
  file and one `scripts/run_*.py` driver each, where the fitting core has
  lettered sub-stages (M4b–M4e). The C-results are the *what*, the M-modules the *how*:

  |  |  |  |  |
  |---|---|---|---|
  | M0 ingest + QC | M1 noise law | M2 frequency ruler | M3 lineshape + fit |
  | M4 density + $\beta$ | M4b global fit | M4c $\sigma_\text{laser}$ sharing | M4d lever check |
  | M4e Stark sweep | M5 laser epoch | M6 power sweep | M7 amplitude trapping |
  | M8 model-form | M9 transit MC | M10 amplitude ratios | M11 model ladder (BIC) |
  | M12 identifiability | M13 coverage study | M14 $\sigma$-sharing BIC | M15 fringe tail |
  | M16 polarizabilities | M17 resolving power | M18 van der Waals $C_6$ | M19 ramp vs motion |
  | M20 laser history (piecewise) | M21 centre channel (null) | M22 wavemeter reconstruction | M23 joint three-session Stark |
  | M24 wing check (null) | M25 global dataset fit (both coefficients free) | M26 pilot ruler (the pilot day's own rate) | M27 centre-channel Stark |
  | M28 full dataset in one likelihood | M29 trap-design corrections at the magic crossings | M30 cavity-scan photograph, integrated |  |
  | M31 cascade populations and ground-F depletion | M32 blackbody as a campaign temperature boundary | M33 model comparison as an evidence vector | M34 the digital twin: forecast a design before building it |
  | M35 the detection channel: which decay branch is collected, and its trapping | M36 polarisation: what ellipticity and a beam mismatch open | M37 the two-atom channel: what a pair accepts that one atom must refuse | M38 the fibre twin's forward model: a transit kernel entering at second order, contributing a few per cent of its own width and growing as T not sqrt(T), so a temperature ladder reads it weakly |

- **CI, Continuous Integration** (*not* C1): the GitHub Actions workflow that
  runs the full `pytest` battery on every push, on the minimum *and* latest
  numpy. It is software infrastructure rather than a physics result, and the
  resemblance to "C1" is a coincidence worth naming.

---

## 0. The frequency-axis convention (read this first)

Two photons are absorbed, so the resonance depends on the **sum** of their
frequencies. We therefore quote all physics on the **transition axis**,

$$\nu_\text{transition} = \nu_1 + \nu_2 = 2\nu_\text{laser}$$

which is exactly twice the laser frequency the atom sees. Anything expressed
per-photon (on the "laser axis") carries a `_LASER` suffix in the code. The
factor of two is a recurring trap (it appears again for the laser linewidth in
§2.3 and the ruler in §3), so we state it once and never mix silently. The
natural width, for example, is $\Gamma_\text{nat}=3.4925$ MHz on the transition
axis and would read $1.746$ MHz on the laser axis.

---

## The chapters

The chapters are the experiment: what was done here, in what order, and what
the numbers came out as. The general theory behind each technique lives once,
in the [wiki](wiki/README.md), and a chapter links to it where a term it uses
first does real work.

Each chapter adds one piece of the analysis to the one before it and is
self-contained: read them in order, and each assumes only the chapters before
it. The frequency-axis convention above (§0) is assumed by all of them.

| # | chapter | what it adds |
|---|---|---|
| **1** | [The measurement](methods/01_the_measurement.md) | the apparatus, the cascade we detect, and why two counter-propagating photons cancel the Doppler width |
| **2** | [The lineshape, kernel by kernel](methods/02_the_lineshape.md) | natural, collisional, laser and transit-time broadening, each derived, and why the transit kernel is a cusp rather than a Gaussian |
| **3** | [The AC-Stark ramp](methods/03_the_ac_stark_ramp.md) | the analysis's novel core: a focused beam makes the light shift a *distribution*, closed-form and triangular for a two-photon rate, with a self-centred drift-immune skew |
| **4** | [The composite model](methods/04_the_composite_model.md) | the assembled profile in code, and radiation trapping, the mechanism that moves amplitudes but not shapes |
| **5** | [From volts to a frequency axis](methods/05_the_frequency_ruler.md) | the EOM sideband ruler that calibrates every scan |
| **6** | [The statistics](methods/06_the_statistics.md) | measured weights, hierarchical sharing, the σ_laser↔γ_coll degeneracy, the pre-registered measurement-vs-bound rule, and the fit-against-moments comparison the twin measured (§4.14) |
| **7** | [What we found](methods/07_what_we_found.md) | the 2025 dataset's results: the bounds, the nulls, and the consistency checks |
| **8** | [Assumptions, and where this can go](methods/08_assumptions_and_outlook.md) | the load-bearing assumptions to challenge, and what a fixed-lock session would lift |
| **9** | [The guided geometry](methods/09_the_guided_geometry.md) | the same four terms derived in an evanescent field: the guided mode solved from the fibre diameter and validated against its own boundary conditions, transit turning near-Lorentzian, the atom-surface potential, and which knobs separate them |

For the project's goals, the prior art, and what each future measurement would
add, see [BIG_PICTURE.md](BIG_PICTURE.md).

## 8. Conventions, repository map, reproduction

**Conventions (non-negotiable):** transition-frequency axis everywhere (laser
$=\tfrac12$, `_LASER` suffix) · a provenance tag on every number
(`ESTABLISHED` / `MEASURED-HERE` / `CALCULATED` / `ENVELOPE` / `OPEN` /
`DESCOPED`) · validation on synthetic data before real data · independent cross-checks of headline results,
including the strongest kind, an independent physical channel checking the
primary fit rather than a re-fit or bootstrap: the collisional-wing null is
closed by a density lever and a power lever agreeing (C3g), and the sweep rate
is cross-checked against unrelated calibrations in the ruler chapter (§3). The
same design carries over to the beam waist: PLAN §4.2 gives it two instruments
with different failure modes, and a measurement would either reproduce the
fitted transit width or falsify the transit-laser decomposition ·
physics constants vs analysis choices split across `constants.py` / `config.py`
· count repeats from `MANIFEST.csv`, never filenames · excluded and outlier
rejection pre-registered and QC-based, never result-based.

```
rb5s6s/   api(the supported entry point: a trace in, a linewidth out)
          constants config ingest(M0) qc(M0) noise(M1) ruler(M2)
          rate_model(M2b: the time-resolved sweep rate)
          trim(M2c: the residual-tail trimmer, shared by M0, M2 and M3)
          lineshape(M3) linefit(M3) density(M4) beta(M4) global_fit(M4b)
          lever_crosscheck(M4d) stark(M4e) modelform(M8) transit_mc(M9)
          amplitudes(M10) model_ladder(M11) identifiability(M12) coverage(M13)
          sharing_bic(M14) fringe_tail(M15) polarizability(M16) resolving(M17)
          vanderwaals(M18) ramp_transit(M19) hyperpolarizability(M29)
          cavity_scan(M30: the 2025-06-12 cavity-scan photograph, integrated)
          cascade(M31: hyperfine populations under repeated excitation, and the
                  ground-F depletion that separates transition strength from
                  observed amplitude)
          blackbody(M32: thermal radiation as a campaign boundary, delivering
                    T_max(target precision) rather than a single ceiling)
          model_compare(M33: model comparison as an evidence vector, with the
                        interpretation layer deliberately separate)
          forecast(M34: the digital twin, synthesise traces for an experiment
                   that does not exist yet, fit them back, and read the
                   achievable precision from the fit's own covariance)
          scenario(M34c: a campaign session as a loadable file. Every
                   field carries its provenance or refuses to load, open
                   apparatus items enter as spans, and an acquisition the
                   named scope cannot realise is rejected citing the manual's
                   own limit)
          instruments(M34a: the oscilloscopes as objects, record length,
                      effective depth per resolution mode, and whether that
                      mode correlates neighbouring samples, every number from
                      a manufacturer manual and None where none is printed)
          twin(M34b: the twin as an acquisition. An instrument at settings, a
               one-peak or four-peak trace, the measured noise law and sample
               correlation, and the platform that decides the radiation
               temperature: the heated cell radiates against itself while the
               nanofibre radiates against a 300 K room whatever its
               microkelvin atoms do)
          detection(M35: which decay branch the apparatus collects, and the
                    radiation trapping that follows from it, so the detected
                    wavelength is a configuration rather than a constant)
          polarisation(M36: what an imperfect polarisation opens. Ellipticity
                       gives a vector light shift of a few kHz that spreads
                       the line. A forward-to-retro mismatch was thought to
                       open Delta m_F = +-1 and is RETRACTED, because the
                       two-photon operator is symmetric in the two beams for
                       photons drawn from one laser, so rank 1 is absent. The
                       isotope g_F-squared comparison is now a ceiling on
                       whatever g_F-scaling term remains)
          cooperative(M37: the two-atom channel that lifts the single-atom
                      rank-2 closure. A pair accepts one unit each, putting a
                      satellite at the Delta m_F = +-2 position, at 1.5e-10
                      of the single-atom rate)
          fibre(M38: the fibre twin's forward model, PROSPECTIVE. The
                transit kernel is a Maxwell-averaged SQUARED Lorentzian,
                FWHM f*vbar/(pi*Lambda) with f spanned 0.24 to 0.44. Its
                time function is quadratic at the origin, not linear, so it
                enters the width at second order and contributes a fraction
                of its own FWHM, not all of it, growing as T**0.98 and not
                as sqrt(T). The band, and the line it was computed
                against, are in the guided-geometry chapter. A leaf module:
                it imports core and core never imports it)
          fitutil _compat
          (M18, M19, M29, M31, M32, M33, M34, M35, M36 and M37 are library-and-test only: they have
           no CSV product, so grepping results/ for them finds nothing -- see
           their test files, and for M34 also examples/campaign_twin.py)
scripts/  import_data (+ annotate_manifest_qc: qc_reason provenance)
          → run_qc → run_noise → run_ruler → run_linefit → run_trim_report
          → run_beta_self(C1) · run_global_fit(M4b) · run_lever_crosscheck(M4d)
          · run_laser_epoch(C2,M5) · run_power_sweep(C3,M6) · run_stark_sweep(C3d,M4e) · run_amplitude_trapping(M7) · run_modelform(M8) · run_transit_mc(M9) · run_amplitude_ratios(M10) · run_sigma_laser_sharing(M4c) · run_model_ladder(M11) · run_identifiability(M12) · run_coverage(M13) · run_sharing_bic(M14) · run_fringe_tail(M15) · run_polarizability(M16) · run_resolving_power(M17) · run_laser_history(M20, laser frequency within each display epoch) · run_stark_centres(M21, the centre channel cannot measure the pull) · run_wavemeter_reconstruction(M22, digitises the 2025-06-11 wavemeter photograph) · run_stark_joint(M23, the joint three-session profile-likelihood Stark bound) · run_wing_check(M24, the residual asymmetry is not a collisional wing) · run_global_dataset_fit(M25, every canonical trace in one likelihood, both coefficients free) · run_morning_ruler(M26, the pilot day's own rate from its 27 recovered rulers) · run_centre_stark(M27, the centre-channel AC-Stark coefficient from the held-lock epochs) · run_full_dataset_fit(M28, M23's construction over M25's data: the full dataset in one likelihood) · run_ramp_geometry(§2.6/PLAN §6 predictions) · run_cavity_scan(M30, integrates the 2025-06-12 cavity-scan digitisation) · annotate_results_status(status column, after every producer and before every reader) · make_figures · make_results_ledger
          Two more write no CSV and are run by hand, so a published number
          can be re-derived rather than taken: run_saturation_probe (the
          light-shift bounds re-profiled with the saturation companion in
          the model, four stages, the last needing the outside trees) and
          run_geometry_design (the running-wave and waist designs, whose
          weak-field branch reproduces lineshape.stark_ramp_axial_moments)
data_raw/ MANIFEST.csv, and the 297 traces where the copy carries them
tests/    3185-test battery (3143 fast ~5 min + 42 `slow` high-statistics
          closure tests via --runslow, incl. the M4d synthetic-β and M4e
          synthetic-κ closures, the MANIFEST qc_reason guards, and the
          docs-consistency gates: canonical numbers, links+anchors, math
          rendering, figure freshness, images, recovered-layer contract);
          CI runs the full set on numpy-minimum AND latest
docs/     PLAN.md (fixed-lock proposal + protocol) · DATA.md (dataset provenance) · RESULTS.md (auto-generated ledger)
          · THEORY_NOTE.md (ramp theory, written for a theorist reader) · LITERATURE.md (prior-art ledger)
          · APPARATUS.md (hardware of record, with photographs + schematic)
          · PREREGISTRATION_timestamps.md + PREREGISTRATION_RESULTS.md (the
          timestamp audit: frozen predictions, results, addenda 1–21)
data_recovered/  the backup-recovered layer: the acquisition clock
          (CLOCK.csv), backup-only discards, degradation lineage
results/  committed CSVs (the documented run) + results/README.md
figures/  paper figures from make_figures.py (C1 width-vs-density, C3 power
          sweep, M9 transit degeneracy, M10 area ratios, C1 pooled-width money
          figure + σ_laser(T) anomaly companion, M4d γ-floor lever test, fig15 drift story)
```

The first six scripts form the pipeline (each reads the previous ones'
`results/`), and the rest are the physics analyses keyed to the deliverables.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && pytest -q          # 3143 fast tests (~5 min)
pytest -q --runslow                           # full 3185 incl. slow closures (what CI runs)
# reproduce every committed CSV, figure, and docs/RESULTS.md from data_raw/
# (already in git; import_data.py only re-imports from the original tree):
bash scripts/run_all.sh
```

`run_all.sh` runs every stage in dependency order, then
`annotate_results_status` (which appends the machine-readable `status`
provenance column), then `make_figures` and `make_results_ledger`, both of
which read that column. Where the raw
traces are present it regenerates every committed `results/*.csv`, the figures
and the ledger within the tolerance `scripts/verify_results_fresh.py` states.
`data_raw/README.md` states what the copy you are reading carries.

Raw-data source and history: the 2025 dataset comes from the earlier
`Rb-5S-to-6S-broadening` project. This repository is a clean reimplementation, and
`docs/DATA.md` documents the provenance and every change made here.
