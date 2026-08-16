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

Two names are easy to confuse and worth stating once. `model_profile` takes
the frequency axis and keyword arguments, and is the one you want.
`composite_profile` builds the kernel from its widths and does NOT take an
axis. And `stark_shift_S0_mhz` needs the waist as well as the power, because
the light shift depends on both. A third pair sits one level down:
`transit_fwhm_from_w0` takes a waist in metres, while `linefit`'s
`transit_fwhm_at_T` scales an existing width in MHz. Passing a waist to the
second used to return a number four orders of magnitude small without
complaining, and now raises.

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
committed digits were produced under numpy 2.0.2 and hold across numpy 2.0 to
2.4, and outside that band four files drift, in the two quantity families this
record already declines to read as physics.
[results/ENVIRONMENT_OF_RECORD.md](results/ENVIRONMENT_OF_RECORD.md) gives the
versions, the measured sizes and the reasoning. So a difference the verifier
rejects is a finding. A difference it accepts is the arithmetic.

Two things are worth knowing before you wonder why something fails:

* `pytest -q --runslow` is the full battery and is what CI runs. Run it before
  pushing, not the fast subset, because several guards live only in it.
* Eight scripts read two data trees that are not in the repository, the
  4 July evening session and the campaign-morning session. Five name the trees
  themselves and three reach them by importing `run_stark_joint`'s loaders.
  They exit 0 with a message naming the missing tree rather than failing, and
  the committed CSVs are the record for those stages, so nothing you need is
  missing. If you do have the trees, point `RB5S6S_SESSION_20250704_DIR` and
  `RB5S6S_SESSION_20250717_DIR` at them rather than relying on the fallback path, which
  is not where they live.

## 2. Read it, depending on why you are here

| you are | start with |
|---|---|
| new to two-photon spectroscopy | [docs/GLOSSARY.md](docs/GLOSSARY.md), which explains the measurement in six sentences and then defines every term and symbol the rest of the repository uses |
| here for the physics result | [docs/BIG_PICTURE.md](docs/BIG_PICTURE.md), then [docs/RESULTS.md](docs/RESULTS.md). Section 1.3a of the first is the plain-language account of why the light shift is hard to measure here, and it is the shortest route to why the headline numbers are bounds |
| checking a specific number | [docs/RESULTS.md](docs/RESULTS.md), which reads every headline from its producing CSV, then [docs/UNCERTAINTY.md](docs/UNCERTAINTY.md) for what its error bar means |
| refereeing the claims | [docs/CLAIMS.md](docs/CLAIMS.md) for what is and is not claimed, then [docs/PREREGISTRATION_RESULTS.md](docs/PREREGISTRATION_RESULTS.md) for what was predicted before it was run, including what failed |
| meeting a technique for the first time | [docs/wiki/](docs/wiki/README.md), one page per concept, method, effect and technique: what it is, what problem it solves, where this repository uses it, and how it fails. Every page carries a worked example that runs |
| here for the lineshape theory | [docs/THEORY_NOTE.md](docs/THEORY_NOTE.md) |
| going to work on the code | section 3 below |
| pointing this at a different transition | [docs/ADAPTING.md](docs/ADAPTING.md), which names every seam, and `examples/your_line.ipynb`. Start with its three radiation tests and its branching-fraction recipe, since those decide whether the machinery applies to your line at all before any of the fitting does |
| designing the next campaign | `scripts/run_campaign_conditions.py`, which projects every effect this dataset measured onto a waist, a power, a temperature and a choice of transition, then [docs/PLAN.md](docs/PLAN.md) section 6 for the light-shift programme and [docs/FUTURE_TRANSITIONS_titsapph.md](docs/FUTURE_TRANSITIONS_titsapph.md) section 2 for the menu |
| looking for the apparatus | [docs/APPARATUS.md](docs/APPARATUS.md), every fact tagged with its provenance |
| wondering what happens next | [docs/PLAN.md](docs/PLAN.md) |

[docs/README.md](docs/README.md) is the index over all of it.

## 3. If you are going to work on the code

The layout, in one sentence each. `rb5s6s/` is the library, one module per
analysis stage, pure physics with no disk access except in six named modules.
`scripts/run_*.py` are the drivers, mostly one per stage, writing into
`results/`. `tests/` holds the closure tests, and each one states the answer it
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
