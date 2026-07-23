# Writing and repository conventions

House rules for this repository's documents and code comments. They exist so
that every page reads in one voice and states exactly as much certainty as the
data support. `tests/test_repo_hygiene.py` enforces the mechanical ones.

## Claims and certainty

- **A bound is reported as a bound.** Where the archive constrains rather than
  measures, say so in the sentence that gives the number, not in a footnote.
  Every headline value carries a provenance tag (MEASURED-HERE / CALCULATED /
  ESTABLISHED / ENVELOPE / OPEN / DESCOPED).
- **Proposed work is written as proposed.** No session, campaign, or paper in
  this repository is scheduled or agreed. Use "a proposed session", "would
  measure", "if run" — never "the session will" or a present-tense outcome
  ("converts the bounds into measurements"). A reader must never be able to
  mistake a plan for a commitment.
- **Conditional predictions name their condition.** If a result depends on an
  unmeasured parameter, the sentence that states the result states the
  dependency and the threshold — see the g1 sign-flip discussion in PLAN §8.3
  #4, which is conditional on a collection geometry that has not been measured.
- **Numbers live in one place.** Headline values are generated from the
  committed CSVs; prose quotes them, never restates them independently.
  `tests/test_docs_canonical.py` and `tests/test_ramp_geometry_docs.py` fail if
  a document and its producing code disagree.

## Register

Plain declarative prose. State the finding and stop.

Avoid the self-assessing register — sentences that comment on the work's own
virtue rather than reporting a result. In particular avoid "X is itself a
result", "not a hedge but the point", "the honest headline", "a test passed,
not a tuning". They read as advocacy, and a reader who has to be told a result
is honest starts wondering why.

Precise technical contrasts are different and are welcome: "an upper bound,
not a detection" and "a model fit, not a moment computation" draw real
distinctions and should stay.

## People

Name people in **citation context only** — cite via `docs/lit/<citekey>.md`.

Do not assign colleagues roles in published documents ("X must be able to take
over", "ask X", "lead on the fibre side"). Roles are for the people involved to
agree between themselves; a public repository is not the place to announce
them. Write "a new operator", "the group", "an external theory check".

## Generated files — edit the generator, not the output

| File | Generator |
|---|---|
| `docs/RESULTS.md` | `scripts/make_results_ledger.py` |
| `docs/LITERATURE_INDEX.md` (+ a local, untracked `PDF_papers/README.md`) | `scripts/build_lit_index.py` |
| `docs/references.bib` | `scripts/build_lit_index.py` |

Editing these directly is lost on the next run, and the freshness tests fail.

## Markdown and maths

- **Unicode in prose and in YAML frontmatter** — ⁸⁷Rb, 5S₁/₂, µm, →, —.
  GitHub renders `$…$` inline maths inconsistently and shows it raw inside
  frontmatter tables, so LaTeX belongs only in display maths (`$$…$$`) and in
  bibliographic fields.
- **LaTeX stays in bibliographic fields.** `title:` and `pages:` in
  `docs/lit/*.md` keep publisher/BibTeX form (`{Rb}`, `$6S_{1/2}$`,
  `855--865`) because they feed `references.bib`. Author names use Unicode
  accents (Síle, Bordé, Wcisło) — safe for modern LaTeX and correct on the page.
- **No thin-space macros** (`\,`, `\;`, `\!`) in Markdown maths — GitHub's
  renderer eats the backslash. `tests/test_docs_math_render.py` catches these.
- **Quote arXiv IDs** in YAML (`arxiv: '2201.06000'`), or a trailing zero is
  lost to float parsing.

## Private material

Correspondence and personal documents (CV, letters, briefs, reviewer notes)
live in the working tree but are never committed. `.gitignore` carries generic
patterns for them, and `tests/test_repo_hygiene.py` fails if a matching path
ever becomes tracked. Do not rely on `.git/info/exclude` — it is local to one
clone and does not survive a fresh checkout elsewhere.

## Commits

Explain why the change was needed, not only what moved. Where a fix corrects
an earlier error, say what was wrong. No generated-by or co-authored-by
trailers. Run the full suite (`pytest -q --runslow`) before pushing.
