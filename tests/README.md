# The test suite

Fifty-seven modules, a little over sixteen hundred collected cases, and most of
them are not unit tests. The suite exists to certify three different things at
once: that each analysis stage recovers an answer that was injected into
synthetic data before it is trusted on real data, that every committed CSV and
figure still matches the code that produced it, and that the published
documents still quote the numbers the code computes. The third group is why
this page is here. A failure there names a physics quantity but has a
bookkeeping cause, and the explanation of what the check is for lives in the
failing module's own docstring rather than anywhere a contributor would think
to look first.

## Closures on the physics

The pattern repeats across the analysis stages. Build synthetic traces from the
forward model with a known answer put in by hand, in the campaign's own format
and with campaign-like noise, run the shipped estimator over them, and require
the answer back within a stated tolerance. The demand runs in both directions.
On spectra built with a known AC-Stark shift the nested-model ladder must
decide the extra parameter is warranted, and on spectra built with no shift it
must stop before adding one. On data with no collisional broadening the
multi-temperature fit must report zero as consistent with zero.

The modules are `test_qc.py` (per-trace metrics and each injected defect
tripping the metric designed for it), `test_noise.py` (the noise law),
`test_ruler.py` (the comb machinery, including the cold dim combs and the
suppressed carriers), `test_linefit.py` (the joint condition fit),
`test_beta.py`, `test_global_fit.py` and `test_lever_crosscheck.py` (the
collisional fits, including the recovery of isotope-distinct injected values),
`test_stark.py`, `test_model_ladder.py`, `test_modelform.py` and
`test_sharing_bic.py` (model selection and model form),
`test_identifiability.py` with `test_identifiability_profile.py` (the width
degeneracy, required to be present and quantified),
`test_coverage.py` (whether the stated 95% bound actually covers the truth),
`test_trim.py` (what the residual-tail trimmer must cut and, held just as
tightly, what it must never cut), `test_intrascan_drift.py`,
`test_transit_mc.py`, `test_fringe_tail.py`, `test_ramp_transit.py`,
`test_resolving.py`, `test_amplitudes.py` and `test_rate_model.py`.

Alongside the closures sit invariants that hold without any data at all.
`test_lineshape.py` pins the kernels: each is area-normalized, each has the
FWHM it claims, and the composite convolution obeys its analytic limits, so a
Lorentzian convolved with a Gaussian is a Voigt and added Lorentzian widths
add. Elsewhere the invariants are structural, such as the requirement in
`test_lever_crosscheck.py` that the assembled error bar be at least as wide as
each single axis it combines.

The third mode is an anchor against a measured value the model does not use.

- `test_density.py` holds the vapour-density correlation to standard
  vapour-cell figures and to the roughly fiftyfold density rise across the
  70 to 130 °C sweep, which is the lever arm the collisional result rests on.
- `test_constants.py` reproduces the spacings between the four file-label
  wavelengths from the ground-state and 6S hyperfine intervals. That is the
  argument which locks the peak identification without the wide scans, and it
  fails if a label or a hyperfine constant is edited inconsistently.
- `test_polarizability.py` requires the measured 5S static polarizability, the
  measured 5S tune-out between the D lines and the published 6S static value
  before any magic wavelength may ship.
- `test_vanderwaals.py` checks the ground-state C6 against its literature
  value, which is what licenses the 5S plus 6S coefficient that has none.
- `test_hyperpolarizability.py` runs the Einstein-A chain into the measured D2
  width and the measured 6S lifetime, and pins the radial-sign table through a
  gauge-invariant loop product.
- `test_transit_mc.py` checks the bare transit FWHM against the closed form and
  against a published worked example.

## Freshness

Editing a producer without re-running it leaves the CSV, the documents pinned
to it and the figure drawn from it mutually consistent and all stale, with
nothing failing. Two modules close that.

`test_results_fresh.py` recomputes a committed results CSV from its committed
inputs, by the exact call the producer makes, and compares. `test_resolving.py`
carries the same check for its own stage.

`test_figures_fresh.py` reads a fingerprint of the results CSVs that
`scripts/make_figures.py` stamps into each figure's PNG metadata at draw time
and requires it to match the current results. It compares a hash held in a text
chunk and never pixels, because committed matplotlib output is not reproducible
across the matplotlib versions CI runs. The raw-trace illustration is exempt,
being drawn from the frozen archive rather than from `results/`.

## The committed record, and the dataset

Some producers cannot run from a clone, because they read raw material that is
held privately and take tens of minutes or hours. Their tests hold the
committed CSV to its own construction instead of re-deriving the number:
internal consistency, the exclusions the construction declares, and the
premises the argument rests on. `test_stark_joint.py`, `test_morning_ruler.py`,
`test_centre_stark.py`, `test_stark_centres.py`, `test_wing_check.py`,
`test_laser_history.py` and `test_wavemeter_reconstruction.py` work this way.

The dataset itself is certified separately. `test_manifest.py` requires every
trace present and byte-identical against `data_raw/MANIFEST.csv` and correctly
role-classified, `test_manifest_qc.py` that every excluded trace carries its
recorded reason, `test_qc_policy.py` the exclusion policy rather than any one
threshold, and `test_recovered_layer.py` the contract of the backup-recovered
layer. `test_results_status.py` requires every committed row to carry the
provenance word described in [../results/README.md](../results/README.md), so a
plot script that never opens the ledger cannot read a bound as a measurement.

Where the raw traces are absent from a checkout these skip rather than fail,
through `requires_raw_traces` in [conftest.py](conftest.py). Everything that
certifies the analysis itself runs regardless.

## Guards on the documents

These read the published files and fail on a contradiction. None of them
computes physics.

| module | what it holds |
|---|---|
| `test_docs_canonical.py` | One registry of headline numbers. Each entry reads its true value from the producing CSV or constant, formats it the way the documents write it, and lists the documents that must cite it. A stale value left anywhere fails here. |
| `test_svg_canonical.py` | The same discipline for numbers drawn on hand-authored SVGs under `docs/`, which no other check can see. |
| `test_docs_links.py` | Every internal link and image path resolves, every `#anchor` matches a real heading in the target, and the run commands in fenced blocks name real scripts. Bare section pointers into the three long planning documents resolve too. |
| `test_docs_images.py` | Every referenced image exists, every published photograph is referenced somewhere, and none carries EXIF metadata. |
| `test_docs_math_render.py` | Every math span survives GitHub's markdown-to-MathJax pipeline. A backslash before an ascii punctuation character is eaten before MathJax sees the content, which is invisible in a local editor. |
| `test_figure_register.py` | An ast walk over the figure-drawing scripts, requiring that no module code, CSV column name or provenance tag reaches a rendered title, legend, annotation or parameter box. The footer is the one place file paths belong. |
| `test_lit_consistency.py` | `docs/lit/<citekey>.md` is the one place a paper's facts live, and `docs/references.bib` with `docs/LITERATURE_INDEX.md` are generated from it. Citekey resolution, frontmatter schema and holdings all have to agree. |
| `test_lit_quotes_are_verbatim.py` | Where a note asserts a quotation is verbatim, it is checked character by character against the source PDF. Scope is opt-in, because these notes also quote this repository's own voice. |
| `test_result_attribution.py` | A sentence describing one result's property must not attach to a different result's number. Whitespace is collapsed first, since the wording wraps across line breaks. |
| `test_ramp_geometry_docs.py` | The ramp-geometry moment coefficients and the crossover location quoted in prose equal what the function computes, and a failure names the documents that must move. |
| `test_repo_hygiene.py` | What must never enter the public history, plus the house conventions. Every check reads `git ls-files`, so local working files are never scanned. |
| `test_docs_structure.py` | Every `docs/` file over 2500 words opens with the four-line reader header and points at the glossary. A check on shape rather than wording, so it cannot be satisfied by a formula, and it fails if its own exemption list ever leaves it matching nothing. |
| `test_interval_sanity.py` | A committed interval must have positive width, must be wider than the grid its producer recorded resolving it on, and must contain its own point estimate. Written after a 95 per cent interval shipped with zero width, and it then refused the interpolated interval that replaced it, which was still 14 times too narrow. |
| `test_package_surface.py` | The wheel's promise, checked in process: the exported names are all pure, importing the physics does not drag in a module that reads from disk, and the data modules raise an error naming what needs cloning rather than resolving a path into site-packages. |
| `test_gallery_hygiene.py` | The inspection generator writes only under `private/`, checked both by a walk of its syntax tree and at runtime. |
| `_provenance_budgets.json` (in `test_note_provenance_ratchet.py`) | Two falling budgets on the provenance debt plus a hard one on the class that matters. `notes_no_producer` and `orphan_claims_total` may fall and never rise, and `orphans_on_reader_facing_surfaces` is the release-blocker class: an ungoverned number quoted on a page a reader acts on. A third test refuses a budget recorded above the current count, since that would let the debt grow back unnoticed. All three ceiling-tested by planting. |
| `test_no_shadowed_script_names.py` | No tracked executable outside `scripts/` may wear a committed script's basename. Written after a scratchpad `port_to_mirror.sh` shadowed the committed one, copied `.github/`, and disabled the public repository's CI trigger for the second time in three days. The name is the expensive part: an outside reviewer read the committed tool, found it correct, and cleared the port. Its blind region is stated in the file, and it is large. |
| `test_note_provenance_ratchet.py` | A per-file budget of numeric claims in `docs/notes/` that declare nothing about what regenerates them. Written after a published regression table was found to have no producer, no `results/` row and therefore no freshness check, six days after its own commit message said "Nothing in `results/` moved". A note escapes by declaring `provenance:` as a `results/` file, DESIGN, PREREG, INDEX, or NO_PRODUCER with a reason. NO_PRODUCER is not an exemption: it is the sentence a reader needs and cannot otherwise get. |
| `test_prose_style_ratchet.py` | A per-file budget for em-dashes and semicolons in prose that may fall and never rise, and a short list of filler openers held at zero. A brand-new Markdown file has no budget, so it must carry none of either. |
| `test_version_surface.py` | The three files carrying the version string agree, and a version that has been released carries its tag. |
| `test_ci_triggers.py` | This checkout's workflow runs the full battery on every push. A checkout identifies itself by whether the raw traces are present. |

The writing conventions these enforce are stated in
[../docs/STYLE.md](../docs/STYLE.md).

## The slow battery

A handful of closures carry the statistical weight of the whole suite. They
need large trace counts and large Monte Carlo samples before their answer stops
moving, and they dominate the wall clock. Those are marked `slow` and
skipped by default, so the inner loop stays short, and CI always runs them.
Every module keeps at least one fast case, so no code path goes completely
unexercised locally. The marker and the `--runslow` option are defined in
[conftest.py](conftest.py).

## Running it

```bash
pytest -q                 # the fast suite
pytest -q --runslow       # everything, which is what CI runs
bash scripts/ci_gate.sh   # ruff, then the full battery, before a push
```

[../scripts/ci_gate.sh](../scripts/ci_gate.sh) runs the lint job and the full
battery in the order the workflow runs them, so a push can only turn red for a
reason the local machine could not have seen.

## Adding a guard

A guard's docstring records the specific breakage it exists to prevent, in
enough detail that someone meeting the failure later can tell whether the check
is still earning its place and what the alternative to it was. That is why the
docstrings in this directory are long, and writing one is part of adding a
check rather than a courtesy afterwards.

A new guard is then verified by planting the defect it describes, watching the
check fail, and restoring the file. Without that step nothing establishes that
the check can fail at all, and a check that cannot fail reads as coverage while
providing none. Where the planted defect is cheap to express, some modules keep
it permanently as a parametrised case asserting that the check still rejects
it.

For the documents these guards read, start at
[../docs/README.md](../docs/README.md). For the pipeline they certify, start at
the [top-level README](../README.md).
