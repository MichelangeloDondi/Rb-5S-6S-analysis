# The environment the committed numbers were produced in

Every CSV in this directory was produced by the versions below. This file
exists because "the numbers reproduce" is not a property of the code alone, and
on 2026-08-12 that stopped being an abstract point: raising the tested Python
version pulled in numpy 2.5, which replaced the `np.convolve` implementation
this whole lineshape model is built on, and four of sixteen committed files
stopped matching a fresh run of their own producers.

**That is now the history of this file rather than its present tense.** The
migration onto numpy 2.5 was measured, held for two days on a preregistered
backstop, and landed on 2026-08-23. What it moved, cell by cell, is in
[the history](../docs/HISTORY.md#the-environment-migration-landed-2026-08-23):
56 of 58 committed result files reproduced across the change, and the two that
moved are the archive's known ill-conditioned direction.

## The versions of record, since 2026-08-23

| | version |
|---|---|
| Python | 3.14.6 |
| numpy | 2.5.2 |
| scipy | 1.18.0 |
| pandas | 3.0.5 |
| blas | Apple Accelerate |
| platform | macOS 26.6.2, arm64 |

**The environment is recorded item by item on purpose.** "The environment"
is too broad to be a controlled variable, and the migration was run as a
controlled re-centring with these rows as the only thing allowed to differ.

## The previous environment of record, until 2026-08-23

| | version |
|---|---|
| Python | 3.9.6 |
| numpy | 2.0.2 |
| scipy | 1.13.1 |
| pandas | 2.2.3 |
| matplotlib | 3.9.4 |

Recover it with the recipe below when reproducing a pre-2026-08-23 commit.
The `--no-deps` warning under it is load-bearing in either direction.

Recover it with:

```
python3.9 -m venv .venv-record       # 3.10-3.12 also host numpy 2.0.2
./.venv-record/bin/python -m pip install \
    "numpy==2.0.2" "scipy==1.13.1" "pandas==2.2.3" "matplotlib==3.9.4"
./.venv-record/bin/python -m pip install -e . --no-deps
./.venv-record/bin/python -c "import numpy, scipy; print(numpy.__version__, scipy.__version__)"
```

**`--no-deps` is load-bearing and the last line is not optional.** Until
2026-08-20 this recipe ended `pip install -e .` with a note to ignore the
`requires-python` warning. That was wrong, and wrong in the one way that
destroys the thing it is building: an editable install is a dependency
resolution, not a path fixup. It reads the `numpy>=2.5` floor this package
declares and enforces it, so the fourth line silently upgraded the 2.0.2
pinned on the second line. The note told the reader to expect a complaint
about the Python version while the damage happened quietly beside it, in a
directory named for the record. Measured on 2026-08-20, both arms run:

| last line | numpy after | `import rb5s6s` |
|---|---|---|
| `pip install -e .` | **2.0.2 -> 2.5.2** | works |
| `pip install -e . --no-deps` | 2.0.2 held | works |

The package still imports either way, so nothing announces the failure. Hence
the printed versions: an environment is a MEASURED quantity, not a configured
one, and its name is not evidence about its contents. If pythonpath suits you
better it is safer still, because it never lets pip near the environment.

The editable install will also complain that the package declares
`requires-python >=3.12`. That complaint is expected, and it is the point of
this file: the supported environment and the environment of record are
different statements, and only the second one reproduces the committed
digits.

## What reproduces, and how widely

The committed digits reproduce on **numpy 2.0 through 2.4**. They drift on both
sides of that band, which was measured rather than assumed: five files differ
under numpy 1.26.4 and four under 2.5.2.

The drift is not scattered. Of 2421 columns that moved at all under numpy 2.5,
exactly six moved by more than 2 per cent, and they belong to two families that
this record already declines to quote as physics:

* `full_gauss` and `full_exp` in `modelform.csv`, the Gaussian and exponential
  widths of the three-component model form. They are fitted against a total
  width that constrains only their combination, which is the degeneracy
  [`RESEARCH_DECISIONS.md`](../docs/RESEARCH_DECISIONS.md) section 1 refuses to
  read as physics and
  [fig10](../figures/fig10_degeneracy_vs_observable.png) exists to draw.
  Observed spread 1.3e-1.
* `dBIC_voigt_minus_lehmann`, a difference of two BICs of order 1e4, where
  cancellation multiplies a 1e-15 perturbation by 1e4. Observed 1.4e-1. The
  conclusion is unchanged at either value: |dBIC| < 2 means no preference
  between the two model forms.

Their well-conditioned siblings, the total width and `chi2_full`, move by under
5e-3 in the same runs. **The arithmetic is unstable exactly where the physics
was already declared unidentifiable, and stable everywhere a number is
quoted.**

## How the guard treats this

`scripts/verify_results_fresh.py` compares at 2e-2 by default, with named
per-column tolerances for the two families above and a zero test taken
relative to each column's own median magnitude rather than an absolute
constant. The reasoning, including the two mistakes that produced it, is in
that file's header and in
[`docs/UNCERTAINTY.md`](../docs/UNCERTAINTY.md) section 4b.

## The convergence run was performed on 2026-08-21, and its result

The full heavy-producer rerun this file anticipates was executed on 2026-08-21
under Python 3.14.6 / numpy 2.5.2, about forty minutes of wall clock, and
compared against the committed digits.

**Two of fifty-one committed CSVs drift, as measured on 2026-08-21.**
Forty-nine reproduce. The denominator is 58 at the landing on 2026-08-23,
because seven committed results were added between the two dates. The
numerator did not move, and it is the same two files.

| file | column | committed | fresh |
|---|---|---|---|
| `linefit_conditions.csv` | `corr`, row 21 | -0.70340 | -0.66265 |
| `identifiability.csv` | `unit`, row 10 | "predicts 0.080" | "predicts 0.110" |

Both belong to the families this file already names as ill-conditioned: a
correlation coefficient, and a ratio of covariance elements taken along a flat
valley. Neither is a quantity this record reads as physics.

**The migration was held at that point, and it landed on 2026-08-23.** The
preregistered threshold was that the migration lands unless a number a public
document quotes moves beyond its stated tolerance. The second drift was such a
number: `docs/methods/06_the_statistics.md` quoted the covariance prediction as
+0.080 in running prose. The hold stood until the owner authorised the
migration, and the paragraph above records the versions the committed digits
are made under now.

**This paragraph described the hold in the present tense for two days after it
was written**, and it survived four propagation sweeps in the window that
landed the migration, because a sweep that greps `docs/` does not read a file
in `results/`. It is corrected here for the same reason
`results/kernel_budget.csv` was: a statement a reader could act on has no
business going stale wherever it lives.

Two findings came out of the run that outlast the decision:

* The 0.080 was living inside a `unit` prose string rather than in a value
  column, so the freshness comparator was checking it as text rather than at a
  numeric tolerance. **It now has its own row**, `ridge_slope_covariance_pred`,
  added when the migration landed.
* The published agreement between the profile map's ridge slope and that
  covariance prediction is a consistency check rather than a precision test,
  because only one of the two numbers is robust. The statistics chapter says so
  and names which one.

## When this file stops being necessary

The two environments converge on their own at the next full run of the heavy
producers. That run is already scheduled for a different reason: the archive
fit is gaining a parallel path over its kappa grid, and the acceptance test
for that path is a full run reproducing `global_dataset_fit.csv` to the
printed digit. It will execute on the supported floor, so if it reproduces
within the tolerances the guard states, its output is committed and the
environment of record becomes the floor. Nothing needs migrating separately.

Until then the versions above are a fact about how the committed files were
produced, and this file records it rather than leaving a reader to discover
it from a diff.

## What this file is not

It is not a claim that the analysis requires these versions. The code runs, and
the suite passes, on the declared floor (Python 3.12, numpy 2.5, scipy 1.16)
and on Python 3.14 with the current stack. What is specific to the versions
above is the reproduction of the committed digits to the precision the CSVs
store.
