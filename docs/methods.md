# Rb 5S→6S two-photon lineshape analysis

Analysis of the rubidium $5S_{1/2}\to 6S_{1/2}$ two-photon transition at
993 nm (data taken at OIST in 2025, follow-up planned a fixed-lock session 2026). This
document doubles as the **methods draft** for the paper: every broadening
mechanism and every statistical choice is derived from first principles and
then tied to its implementation in the code. It is written to be read
top-to-bottom by someone new to the experiment. Nothing is
assumed beyond undergraduate quantum mechanics and statistics.

> **Status (2026-07-12):** the **archival data is exhausted** — every quantity
> it can yield has been extracted, and each is a documented **bound or null with
> a named a fixed-lock session measurement that lifts it**; nothing here is an absolute
> measurement, because the dominant systematic (the beam waist $w_0$) is still an
> OPEN prior. That status is stated per-result in §5 **and now machine-attached**:
> every `results/*.csv` row carries a `status` column (BOUND/NULL/MEASURED/…), so
> a number never reads as more certain than it is. Modules M0→M10
> plus the lever-crosscheck (M4d) and Stark-sweep (M4e) analyses, **113 tests**
> passing on numpy 1.24 *and* 2.0;
> all Paper-1 deliverables (C1 collisional broadening, C2 laser epoch, C3
> power/ramp-law, C3d Stark-coefficient bound) delivered at bound/null level. A
> manuscript scaffold with drafted sections is in
> [`docs/PAPER1_SKELETON.md`](PAPER1_SKELETON.md). Prose results in §5; the auto-generated
> single-source-of-truth table is [`docs/RESULTS.md`](RESULTS.md); the
> prior-art delineation and collision-rate calibration are in
> [`docs/LITERATURE.md`](LITERATURE.md); what a fixed-lock session lifts is in §7.

### Notation and abbreviations (defined once, used throughout)

| symbol / term | meaning |
|---|---|
| $\nu$ | frequency; **transition axis** = the two-photon sum frequency (see §0) |
| FWHM | full width at half maximum of a lineshape |
| $\Gamma_\text{nat}$ | natural FWHM of the transition |
| $\gamma_\text{coll}$ | collisional (pressure) broadening FWHM |
| $\sigma_\text{laser}$ | laser-jitter contribution to the FWHM |
| $N$ | rubidium vapour number density (atoms cm$^{-3}$) |
| $\beta_\text{self}$ | collisional **self-broadening coefficient**, $\gamma_\text{coll}=\beta_\text{self}N$ |
| $w_0$ | laser beam waist (radius at which intensity falls to $1/e^2$) |
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
ratio — flagged again where it appears.

---

## 0. The frequency-axis convention (read this first)

Two photons are absorbed, so the resonance depends on the **sum** of their
frequencies. We therefore quote all physics on the **transition axis**,

$$\nu_\text{transition} = \nu_1 + \nu_2 = 2\nu_\text{laser}$$

which is exactly twice the laser frequency the atom sees. Anything expressed
per-photon (on the "laser axis") carries a `_LASER` suffix in the code. The
factor of two is a recurring trap (it appears again for the laser linewidth in
§2.3 and the ruler in §3), so we state it once and never mix silently. The
natural width, for example, is $\Gamma_\text{nat}=3.4926$ MHz on the transition
axis and would read $1.746$ MHz on the laser axis.

---

## The chapters

Each chapter adds one piece of the analysis to the one before it and is
self-contained: read them in order, and each assumes only the chapters before
it. The frequency-axis convention above (§0) is assumed by all of them.

| # | chapter | what it adds |
|---|---|---|
| **1** | [The measurement](methods/01_the_measurement.md) | the apparatus, the cascade we detect, and why two counter-propagating photons cancel the Doppler width |
| **2** | [The lineshape, kernel by kernel](methods/02_the_lineshape.md) | natural, collisional, laser and transit-time broadening — each derived, and why the transit kernel is a cusp rather than a Gaussian |
| **3** | [The AC-Stark ramp](methods/03_the_ac_stark_ramp.md) | the analysis's novel core: a focused beam makes the light shift a *distribution*, closed-form and triangular for a two-photon rate, with a drift-immune skew |
| **4** | [The composite model](methods/04_the_composite_model.md) | the assembled profile in code — and radiation trapping, the mechanism that moves amplitudes but not shapes |
| **5** | [From volts to a frequency axis](methods/05_the_frequency_ruler.md) | the EOM sideband ruler that calibrates every scan |
| **6** | [The statistics](methods/06_the_statistics.md) | measured weights, hierarchical sharing, the σ_laser↔γ_coll degeneracy, and the pre-registered measurement-vs-bound rule |
| **7** | [What we found](methods/07_what_we_found.md) | the 2025 archive's results: the bounds, the nulls, and the confirmed predictions |
| **8** | [Assumptions, and where this can go](methods/08_assumptions_and_outlook.md) | the load-bearing assumptions to challenge, and what a fixed-lock session would lift |

For the project's goals, the prior art, and what each future measurement would
add, see [BIG_PICTURE.md](BIG_PICTURE.md).

## 8. Conventions, repository map, reproduction

**Conventions (non-negotiable):** transition-frequency axis everywhere (laser
$=\tfrac12$, `_LASER` suffix) · a provenance tag on every number
(`ESTABLISHED` / `MEASURED-HERE` / `CALCULATED` / `ENVELOPE` / `OPEN` /
`DESCOPED`) · validation on synthetic data before real data · independent cross-checks of headline results ·
physics constants vs analysis choices split across `constants.py` / `config.py`
· count repeats from `MANIFEST.csv`, never filenames · quarantine and outlier
rejection pre-registered and QC-based, never result-based.

```
rb5s6s/   constants config ingest(M0) qc(M0) noise(M1) ruler(M2)
          lineshape(M3) linefit(M3) density(M4) beta(M4) global_fit(M4b)
          lever_crosscheck(M4d) stark(M4e) modelform(M8) transit_mc(M9)
          amplitudes(M10) fitutil _compat
scripts/  import_data (+ annotate_manifest_qc: qc_reason provenance)
          → run_qc → run_noise → run_ruler → run_linefit
          → run_beta_self(C1) · run_global_fit(M4b) · run_lever_crosscheck(M4d)
          · run_laser_epoch(C2,M5) · run_power_sweep(C3,M6) · run_stark_sweep(C3d,M4e) · run_amplitude_trapping(M7) · run_modelform(M8) · run_transit_mc(M9) · run_amplitude_ratios(M10) · run_sigma_laser_sharing(M4c) · run_ramp_geometry(§2.6/PLAN §8.3 predictions) · make_figures · make_results_ledger · annotate_results_status(status column, runs LAST)
data_raw/ frozen 2025 dataset (297 unique traces) + MANIFEST.csv
tests/    113-test battery (104 fast ~22 s + 9 `slow` high-statistics
          closure tests via --runslow, incl. the M4d synthetic-β and M4e
          synthetic-κ closures and the MANIFEST qc_reason guards);
          CI runs the full set on numpy-minimum AND latest
docs/     PLAN.md (plan of record) · DATA.md (archive provenance) · RESULTS.md (auto-generated ledger)
          · THEORY_NOTE.md (ramp theory, written for a theorist reader) · LITERATURE.md (prior-art ledger)
          · PAPER1_SKELETON.md (manuscript scaffold)
results/  committed CSVs (the documented run) + results/README.md
figures/  paper figures from make_figures.py (C1 width-vs-density, C3 power
          sweep, M9 transit degeneracy, M10 area ratios, C1 pooled-width money
          figure + σ_laser(T) anomaly companion, M4d γ-floor lever test)
```

The first five scripts form the pipeline (each reads the previous ones'
`results/`); the rest are the physics analyses keyed to the deliverables.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && pytest -q          # 104 fast tests (~22 s)
pytest -q --runslow                           # full 113 incl. slow closures (what CI runs)
# reproduce the pipeline + the headline results (data_raw/ is already in git,
# so import_data.py is NOT needed — it only re-imports from the old archive):
for s in run_qc run_noise run_ruler run_linefit \
         run_beta_self run_global_fit run_lever_crosscheck run_laser_epoch \
         run_power_sweep run_stark_sweep run_amplitude_trapping run_modelform; do
    python scripts/$s.py          # run_lever_crosscheck is the slow one (~5 min)
done
```

That loop is the headline subset; the remaining analyses named in the tree above
(`run_sigma_laser_sharing`, `run_transit_mc`, `run_amplitude_ratios`,
`run_ramp_geometry`), then `make_figures`, `make_results_ledger`, and
`annotate_results_status` (which appends the machine-readable `status` provenance
column to every `results/*.csv` and must run last, after every producer),
regenerate
the rest of `results/`, the figures, and the ledger — the complete set that
reproduces every committed CSV byte-for-byte.

Raw-data source and history: the 2025 dataset comes from the earlier
`Rb-5S-to-6S-broadening` project; this repository is a clean reimplementation, and
`docs/DATA.md` documents the provenance and every change made here.
