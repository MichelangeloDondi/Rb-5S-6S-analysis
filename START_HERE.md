# Start here

A working setup in five minutes, then a reading order that depends on why you
came. If the vocabulary is unfamiliar, open
[docs/GLOSSARY.md](docs/GLOSSARY.md) beside whatever you read. The main [README](README.md) is the full account and runs to about four
thousand words. This page is the front door.

## 1. Run it

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

Then the smallest thing that is actually the physics. This runs from the
installed package, needs no data from this repository, and the numbers it
prints are the ones the analysis is built on:

```python
import numpy as np, rb5s6s as r

nu = np.linspace(-20, 20, 4001)                      # MHz, laser axis
profile = r.model_profile(nu, gamma_coll=0.5,        # collisional FWHM, MHz
                          sigma_laser_fwhm=1.0,      # laser width, MHz
                          transit_fwhm=r.transit_fwhm_from_w0(
                              r.W0_MEASURED_M, 130.0),
                          s0=r.stark_shift_S0_mhz(0.225, r.W0_MEASURED_M))
print(profile.sum() * (nu[1] - nu[0]))               # 1.000017, normalised
```

The last digits are the finite window and the discrete sum, not the model.
Integrate over a wider axis and they go away.

Three API traps, stated once. `model_profile` takes the frequency axis and is
the one you want, while `composite_profile` takes widths and no axis.
`stark_shift_S0_mhz` needs the waist as well as the power.
`transit_fwhm_from_w0` takes metres where `transit_fwhm_at_T` takes MHz, and
confusing them now raises instead of returning a silently tiny number.
`rb5s6s/README.md` carries the rest.

That should end green in about two minutes, and it needs no data beyond what
this checkout carries. What `data_raw/` holds in the copy you are reading, and
how to obtain the original traces, is stated in
[data_raw/README.md](data_raw/README.md). If the fast suite passes, everything
below will work.

To regenerate the analysis rather than just check it:

```bash
bash scripts/run_all.sh
```

That runs the analysis stages in dependency order, then the figures, the
results ledger and the status column. The stages that read raw traces need the
traces, so which of them run at all depends on the copy you have, and
[data_raw/README.md](data_raw/README.md) states what this one carries.
**Where a stage runs, it reproduces its committed CSV within the tolerance
`scripts/verify_results_fresh.py` states**, which is the property the whole
repository is built to keep. The standard is a
stated tolerance rather than byte equality for a measured reason: the
committed digits hold across numpy 2.0 to 2.4, and outside that band four
files drift, in two quantity families this record already declines to read as
physics. [results/ENVIRONMENT_OF_RECORD.md](results/ENVIRONMENT_OF_RECORD.md)
gives the versions and the sizes. A difference the verifier rejects is a
finding. One it accepts is the arithmetic.

Two things are worth knowing before you wonder why something fails:

* `pytest -q --runslow` is the full battery and is what CI runs. Run it before
  pushing, not the fast subset, because several guards live only in it.
* Eight scripts read two data trees that are not in the repository. They exit
  0 naming the missing tree instead of failing, and the committed CSVs are the
  record for those stages, so nothing you need is missing. If you do have the
  trees, point `RB5S6S_SESSION_20250704_DIR` and `RB5S6S_SESSION_20250717_DIR`
  at them. The fallback path is not where they live.

## 2. Read it, depending on why you are here

| you are | start with |
|---|---|
| here for ten minutes | [docs/plan/00_the-case.md](docs/plan/00_the-case.md), the whole record compressed: the three bounds with their constructions, what stays unidentified, the measurement that breaks each, and what this record refuted in its own claims |
| new to two-photon spectroscopy | [docs/GLOSSARY.md](docs/GLOSSARY.md), which explains the measurement in six sentences and then defines every term and symbol the rest of the repository uses |
| here for the physics result | [docs/BIG_PICTURE.md](docs/BIG_PICTURE.md), then [docs/RESULTS.md](docs/RESULTS.md). Section 1.3a is the plain-language account of why the light shift is hard to measure here, and the shortest route to why the headline numbers are bounds |
| checking a specific number | [docs/RESULTS.md](docs/RESULTS.md), which reads every headline from its producing CSV, then [docs/UNCERTAINTY.md](docs/UNCERTAINTY.md) for what its error bar means |
| refereeing the claims | [docs/CLAIMS.md](docs/CLAIMS.md) for what is and is not claimed, then [docs/PREREGISTRATION_RESULTS.md](docs/PREREGISTRATION_RESULTS.md) for what was predicted before it ran, including what failed |
| meeting a technique | [docs/wiki/](docs/wiki/README.md), one page per concept, method and technique: what it is, what problem it solves, where this repository uses it, and how it fails. Most carry a worked example that runs |
| asking what model was fitted | [docs/methods/04](docs/methods/04_the_composite_model.md): the composite profile term by term, and what is left out of it. [docs/methods/09](docs/methods/09_the_guided_geometry.md) is the same model in a guided geometry |
| here for the lineshape theory | [docs/THEORY_NOTE.md](docs/THEORY_NOTE.md) |
| going to work on the code | section 3 below |
| pointing this at a different transition | [docs/ADAPTING.md](docs/ADAPTING.md), which names every seam, and `examples/your_line.ipynb`. Its three radiation tests and branching-fraction recipe decide whether the machinery applies to your line before any fitting does |
| here for five minutes, to see how the analysis is done | `examples/campaign_twin.py`. It builds this campaign in software with the whole forward model and the instrument's quantisation, fits it back with the production analysis, and says whether the design recovers what was put in |
| deciding whether a new campaign is worth running | [docs/big_picture/09](docs/big_picture/09_the-campaign-cases.md), cell-only beside cell-plus-fibre, with what each leaves behind for the group whose apparatus it is |
| not interested in nanofibres | the fibre thread is named in [docs/BIG_PICTURE.md](docs/BIG_PICTURE.md). Skip those surfaces and lose nothing |
| designing the next campaign, or wondering what happens next | [docs/PLAN.md](docs/PLAN.md), twelve chapters including the open apparatus items, with `scripts/run_campaign_conditions.py` projecting this dataset's effects onto a chosen waist, power and temperature |
| looking for the apparatus | [docs/APPARATUS.md](docs/APPARATUS.md), every fact tagged with its provenance |

[docs/README.md](docs/README.md) is the index over all of it.

## 3. If you are going to work on the code

The layout, in one sentence each. `rb5s6s/` is the library, one module per
analysis stage, pure physics with no disk access except in six named modules.
`scripts/run_*.py` are the drivers, mostly one per stage, writing into
`results/`. [`tests/`](tests/README.md) holds the closure tests, and each one states the answer it
injects before checking what the module recovers, which makes them the second
half of the documentation.

**Reading order for the code**, merged from `rb5s6s/README.md`: the
[measurement chapter](docs/methods/01_the_measurement.md) next to `ingest.py`
and `qc.py`, then the [lineshape chapter](docs/methods/02_the_lineshape.md)
next to `lineshape.py`, then the statistics chapter next to `linefit.py` and
`beta.py`. Read each module's test alongside it.

Two conventions that will otherwise cost you an afternoon:

* **Every frequency is on the two-photon transition axis** unless the name ends
  in `_LASER`. The laser axis is exactly half. Never mix them silently.
* **Nothing numeric is hard-coded outside `constants.py` and `config.py`.**
  Physics quantities live in the first, tunable analysis choices in the second,
  and each carries a provenance tag saying where it came from and how much it
  can be trusted.

Before you commit: `pytest -q --runslow` and `ruff check`. If you changed
anything that writes a `results/*.csv`, also run
`scripts/annotate_results_status.py` and redraw the figures once, because the
figures carry a fingerprint of the results they were drawn from and go stale
when a CSV changes.

## 4. What this is, in three sentences

A from-scratch reanalysis of a 2025 two-photon spectroscopy campaign on the
rubidium 5S to 6S transition, driven at 993.4 nm in a hot vapour cell. The
headline results are **bounds rather than measurements**, because the laser
lock drifted and the beam waist is not re-measured by this dataset, and the
repository is organised around making that conditionality visible rather than
around hiding it. Where a claim was tested and refused, the refusal is in the
record next to the claim.
