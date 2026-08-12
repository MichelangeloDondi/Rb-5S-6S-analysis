# The environment the committed numbers were produced in

Every CSV in this directory was produced by the versions below. This file
exists because "the numbers reproduce" is not a property of the code alone, and
on 2026-08-12 that stopped being an abstract point: raising the tested Python
version pulled in numpy 2.5, which replaced the `np.convolve` implementation
this whole lineshape model is built on, and four of sixteen committed files
stopped matching a fresh run of their own producers.

## The versions of record

| | version |
|---|---|
| Python | 3.9.6 |
| numpy | 2.0.2 |
| scipy | 1.13.1 |
| pandas | 2.2.3 |
| matplotlib | 3.9.4 |

Recover it with:

```
python3.9 -m venv .venv-record
./.venv-record/bin/python -m pip install \
    "numpy==2.0.2" "scipy==1.13.1" "pandas==2.2.3" "matplotlib==3.9.4"
./.venv-record/bin/python -m pip install -e .        # ignore the requires-python warning
```

The editable install will complain that the package now declares
`requires-python >=3.12`. That is expected and it is the point of this file:
the SUPPORTED environment and the environment OF RECORD are different
statements, and only the second one reproduces the committed digits.

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

## When this file stops being necessary

The two environments converge on their own at the next full run of the heavy
producers. That run is already scheduled for a different reason: the archive
fit is gaining a parallel path over its kappa grid, and the acceptance test
for that path is a full run reproducing `global_archive_fit.csv` to the
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
