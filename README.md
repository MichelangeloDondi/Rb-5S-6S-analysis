# Rb 5S→6S two-photon lineshape analysis

A physics-based forward-model analysis of the rubidium **5S₁/₂ → 6S₁/₂** two-photon
transition at **993 nm** — Doppler-free spectroscopy in a hot vapour cell. Data taken at OIST
in 2025; a fixed-lock follow-up session is specified in [`docs/PLAN.md`](docs/PLAN.md).

<p align="center">
  <img src="figures/fig0_spectrum.png" width="560" alt="A representative fitted line">
</p>

*One 993.4192 nm (⁸⁵Rb) line at 130 °C and 225 mW, with the composite fit and its
residuals. The total width is ≈ 5.2 MHz and the residuals sit at the noise floor
(reduced χ² ≈ 1.1) — this is the raw material everything below is built from.*

> **In one sentence:** from a 2025 dataset taken with a drifting laser lock, we
> extract what lives in the *shape* of the line — collisional
> broadening, laser width, the power-dependent light shift — as **bounds**,
> and lay out the fixed-lock measurements that turn each bound into a number.

**Where to go next:** the big picture (goals, prior art, what each future
measurement adds) → [`docs/BIG_PICTURE.md`](docs/BIG_PICTURE.md) ·
full derivations and statistics → [`docs/methods.md`](docs/methods.md) ·
results table (auto-generated) → [`docs/RESULTS.md`](docs/RESULTS.md) ·
measurement plan → [`docs/PLAN.md`](docs/PLAN.md) ·
prior work → [`docs/LITERATURE.md`](docs/LITERATURE.md).

---

## The experiment in one paragraph

A 993 nm beam is retro-reflected through a hot Rb cell. An atom absorbs one photon
from each direction and climbs 5S₁/₂ → 6S₁/₂; because the two photons come from
opposite directions, the first-order Doppler shift **cancels for every atom**,
collapsing the ~500 MHz thermal smear to a line a few MHz wide:

$$\nu\left(1 + \tfrac{v}{c}\right) + \nu\left(1 - \tfrac{v}{c}\right) = 2\nu$$

The 6S population is read out through the 795 nm fluorescence of the
6S → 5P₁/₂ → 5S cascade. Four hyperfine components are recorded across a
temperature sweep (70–110 °C) and a power sweep (25–225 mW at 130 °C) — 297 clean
traces in all.

## Why this dataset is unusual: shapes without centres

The 2025 data were taken with a **slowly drifting lock** (~MHz/min). That has one
consequence:

- absolute line **centres are lost** (drift moves them scan to scan), but
- line **shapes survive intact**.

So the archive delivers what lives in the *shape* of a line —
widths, power-law scalings, asymmetry — as **bounds and nulls**, while the absolute
shifts wait for a stable lock. Being honest about that split is the backbone of the
analysis, and it is why the results below are bounds rather than measurements.

A bound is a result, not a failed measurement: an upper bound excludes every
model that predicts more, and each bound here is the sensitivity target a
follow-up session has to beat — the fixed-lock plan is specified against these
numbers. The width data are already sensitive at the physical scale (the
AC-Stark bound sits just above its prediction), and the 95% constructions are
validated by injection-recovery
([methods §4.11](docs/methods/06_the_statistics.md)), not assumed.

The chain from raw trace to quoted bound — each stage a runnable script, each
output a committed CSV:

```mermaid
flowchart LR
    T[297 raw traces] --> N[measured noise law]
    T --> K[frequency ruler]
    N --> F[hierarchical lineshape fits]
    K --> F
    F --> W[widths and shapes vs T, P]
    W --> D[density lever → β_self bound]
    W --> P[power lever → S₀ bound]
    W --> S[skew and amplitude laws → nulls]
    G[guards: model ladder · identifiability · coverage] -.-> D
    G -.-> P
```

Every scan carries its own frequency ruler — an EOM comb that excites five
copies of the line, exactly 6.25 MHz apart on the laser axis — so the
frequency axis is self-calibrated per block even as the lock drifts, and the
ruler *rate* is a differential across identical lines, immune to the light
shift and to the lineshape asymmetry (methods §3):

<p align="center">
  <img src="figures/fig8_ruler.png" width="720" alt="A ruler trace with its five-tooth comb fit, and the empirical sweep-linearity map">
</p>

## Results at a glance

Every absolute number is limited by a single systematic — the beam waist **w₀** —
so each is reported as a bound together with the fixed-lock session measurement that lifts it.

| Quantity | 2025 result | Type | Lifted by |
|---|---|---|---|
| Collisional self-broadening **β_self** | ≲ 0.2–0.4 MHz per 10¹² cm⁻³ (95% per peak) | bound | same-session 150–170 °C points |
| 2025 laser linewidth **σ_laser** | ≈ 0.8 MHz at the w₀ prior (0.4–1.1 over the open w₀) | bound | knife-edge w₀ |
| AC-Stark coefficient **S₀(225 mW)** | < 0.63 MHz (95%, profile likelihood; predicted 0.59) | bound | fixed lock + tighter focus |
| Power scaling | width flat; amplitude ∝ P² | confirmed prediction | — |
| Beam waist **w₀** | ≈ 50 µm (prior; direct waist ≈ 64 µm) | open | knife-edge measurement |

**β_self is a bound, not a measurement — and the data show why.** The fitted
collisional width barely grows with density (below), while a real binary-collision
width must grow *linearly*. So the fitted width is a residual floor, not resolved
collisions — and a naive fit that reports a "detection" here is reading a floor as
a signal. Demonstrating that the drifting lock *required* this care is
itself a result.

<p align="center">
  <img src="figures/fig6_gamma_floor.png" width="560" alt="The lever test: the collisional width is a floor">
</p>

**The power sweep bears out the ramp's power-law predictions.** At fixed
temperature only the AC-Stark shift varies with power, and both hold: the
linewidth stays flat (the shift broadens the line only as S₀², negligible here)
and the amplitude follows the two-photon rate law, ∝ P². These are *consistent
with* the light-shift model, not proof of it — a flat width is equally what zero
shift would give; the ramp's *distinctive* signature, the skew ∝ S₀³, is below
detection in the archive (a bound), which is why the coefficient itself waits
for a fixed-lock session. The S₀ bound and its prediction are independent by
construction: the bound uses only the width-vs-power data (no w₀ enters),
while the predicted 0.59 MHz is the computed polarizability at the beam
geometry's w₀ prior, with the retro ratio ρ=1 asserted (its in-situ measurement
is a fixed-lock-session task) — fixed before the fit and never an input to it. Their
proximity is a test passed, not a tuning.

<p align="center">
  <img src="figures/fig2_power_sweep.png" width="720" alt="Power sweep: width flat, amplitude proportional to P squared">
</p>

## The lineshape, mechanism by mechanism

The measured line is a convolution (⊗) of independent broadening mechanisms:

$$I(\nu) = A\left[ L_{\Gamma_\mathrm{nat}+\gamma_\mathrm{coll}} \otimes G_{\sigma_\mathrm{laser}} \otimes K_\mathrm{transit} \otimes R_{S_0} \right] + \text{background}$$

| Mechanism | Physical origin | Size (transition axis) | Shape |
|---|---|---|---|
| Natural width **Γ_nat** | finite 6S lifetime | 3.49 MHz (fixed, known) | Lorentzian |
| Collisional **γ_coll** | Rb–Rb collisions | ≲ 0.5 MHz | Lorentzian (adds to natural) |
| Laser **σ_laser** | laser frequency jitter | ≲ 1 MHz | Gaussian |
| Transit | finite time an atom spends in the beam | ~1.2 MHz at w₀ ≈ 50 µm | cusp kernel (Biraben–Cagnac / Lehmann) |
| AC-Stark **R(S₀)** | intensity-dependent light shift across the focus | ~0.6 MHz at 225 mW | triangular "ramp" |

The AC-Stark **ramp** is the analysis's novel core: because the beam is focused,
the light shift runs from zero at the dim edge to a maximum S₀ on the bright axis,
and for a two-photon (intensity-squared) signal that distribution is a closed-form
triangle. Its skew is a light-shift readout that survives a drifting lock — the
derivation is in [`docs/methods/03_the_ac_stark_ramp.md`](docs/methods/03_the_ac_stark_ramp.md) and
[`docs/THEORY_NOTE.md`](docs/THEORY_NOTE.md).

## The dominant systematic: the beam waist w₀

The transit width and the laser width both depend on the beam waist, and the
archive cannot separate them — a tighter waist means more transit broadening and
less room for laser width, and vice versa. The observed ≈ 5.2 MHz line is
reproduced anywhere from w₀ ≈ 20 µm (laser width → 0) up to ≈ 65 µm (laser ~1.1 MHz).
Only a direct beam-profile ("knife-edge") measurement collapses this — which is
why every absolute number above is w₀-conditional, and why it is the first thing
a fixed-lock session fixes. What each assumption moves, quantity by quantity, is
tabulated live from the result CSVs in [`docs/RESULTS.md`](docs/RESULTS.md)
("Sensitivity at a glance").

<p align="center">
  <img src="figures/fig3_transit_mc.png" width="560" alt="Line width versus beam waist: the transit/laser degeneracy">
</p>

## What a follow-up session would add

- **A fixed-lock session.** A stable lock returns the absolute centres, and a
  knife-edge measures w₀ — turning the bounds above into the first measured 5S–6S
  AC-Stark and collisional self-shift coefficients. With power capped at 225 mW,
  the intensity axis comes from the waist instead (a telescope gives two working
  waists spanning a ×16 intensity range), and a same-session 150–170 °C extension
  gives β_self a real density lever. The knife-edge alone is worth a visit: it needs
  only the beam, and it retroactively sharpens this archive. Full specification:
  [`docs/PLAN.md`](docs/PLAN.md) §8.
- **Optical nanofibre (Paper 2).** The same ramp law tested in the evanescent field
  at a fibre surface, where an atom–surface potential and the "pushing dip"
  (Gokhroo et al., 2022) ride on the lineshape.

## Reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                 # fast test suite (~35 s)
pytest -q --runslow       # full suite incl. high-statistics closure tests (what CI runs)
```

The 2025 dataset is already in `data_raw/`, so the pipeline runs directly. Each
stage reads the previous stages' output in `results/`:

```bash
bash scripts/run_all.sh   # every stage in dependency order, then the figures,
                          # docs/RESULTS.md, and the CSV status column
```

Re-running any stage reproduces its committed CSV in `results/` byte-for-byte.

The headline numbers (the AC-Stark and collisional bounds, the beam-waist prior)
are cited across many documents. `tests/test_docs_canonical.py` holds each in a
single registry, reads its true value from the committed CSV, and checks that
every document quotes *that* value — so a re-analysis that moves a number can
never leave a stale copy behind unnoticed. To change a headline number: re-run
its producer, then run the suite; it names any document still out of step.

The **figures** carry the same discipline: `make_figures.py` stamps a fingerprint
of the results CSVs into each PNG's metadata, and `tests/test_figures_fresh.py`
fails if a committed figure was drawn from stale results (the fix is to re-run
`make_figures.py`). The check reads a hash in the PNG, not pixels, so it is
independent of the matplotlib version that drew the figure.

## Repository map

```
rb5s6s/     the library: ingest, quality control, noise model, frequency ruler,
            lineshape + fitting, density, collisional/global/AC-Stark fits,
            transit Monte-Carlo, amplitude analyses, shared utilities
scripts/    one runnable per analysis stage, plus make_figures / make_results_ledger
data_raw/   the frozen 2025 dataset (297 unique traces) + MANIFEST.csv
results/    committed output CSVs (the documented run)
figures/    publication figures produced by make_figures.py
tests/      full test battery; CI runs it on the minimum and latest numpy
docs/       methods.md (index) + methods/ (8 ordered chapters: the full
            derivations) · PLAN.md (measurement plan) ·
            RESULTS.md (auto-generated results table) · DATA.md (data provenance) ·
            THEORY_NOTE.md (AC-Stark ramp theory) · LITERATURE.md (prior work) ·
            PAPER1_SKELETON.md (manuscript outline)
```

## Conventions

- **Transition-frequency axis everywhere** — the two-photon sum frequency, i.e.
  twice the laser frequency. Per-photon quantities carry a `_LASER` suffix in code.
- **Every number carries a provenance tag** (measured here / calculated /
  established / open) so nothing reads as more certain than it is; the same tags
  drive the machine-readable `status` column on every results CSV.
- **Physics constants and analysis choices are separated** (`constants.py` vs
  `config.py`); repeat counts come from `MANIFEST.csv`, never from filenames;
  data quality cuts are decided before fitting, never from the results.
