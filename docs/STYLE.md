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
  measure", "if run". Never "the session will" or a present-tense outcome
  ("converts the bounds into measurements"). A reader must never be able to
  mistake a plan for a commitment.
- **Conditional predictions name their condition.** If a result depends on an
  unmeasured parameter, the sentence that states the result states the
  dependency and the threshold. See the g1 sign-flip discussion in PLAN §6
  #4, which is conditional on a collection geometry that has not been measured.
- **Numbers live in one place.** Headline values are generated from the
  committed CSVs; prose quotes them, never restates them independently.
  `tests/test_docs_canonical.py` and `tests/test_ramp_geometry_docs.py` fail if
  a document and its producing code disagree.

## Register

Plain declarative prose. State the finding and stop.

Avoid the self-assessing register, meaning sentences that comment on the work's own
virtue rather than reporting a result. In particular avoid "X is itself a
result", "not a hedge but the point", "the honest headline", "a test passed,
not a tuning". They read as advocacy, and a reader who has to be told a result
is honest starts wondering why.

Precise technical contrasts are different and are welcome: "an upper bound,
not a detection" and "a model fit, not a moment computation" draw real
distinctions and should stay.

## People

Name people in **citation context only**, citing via `docs/lit/<citekey>.md`.

Do not assign colleagues roles in published documents ("X must be able to take
over", "ask X", "lead on the fibre side"). Roles are for the people involved to
agree between themselves; a public repository is not the place to announce
them. Write "a new operator", "the group", "an external theory check".

## Generated files: edit the generator, not the output

| File | Generator |
|---|---|
| `docs/RESULTS.md` | `scripts/make_results_ledger.py` |
| `docs/LITERATURE_INDEX.md` (+ a local, untracked `PDF_papers/README.md`) | `scripts/build_lit_index.py` |
| `docs/references.bib` | `scripts/build_lit_index.py` |

Editing these directly is lost on the next run, and the freshness tests fail.

## Markdown and maths

- **Unicode in prose and in YAML frontmatter.** ⁸⁷Rb, 5S₁/₂, µm, →, ±, ×, ≈,
  ⁻³. Not the em-dash, which this guide forbids below and which
  `tests/test_prose_style_ratchet.py` holds to a falling budget.
- **Why inline LaTeX is the exception and not the rule, measured rather than
  asserted.** GitHub opens an inline `$…$` span only when the opening delimiter
  follows a line start, whitespace, `(` or `**`, and closes it only when the
  next character is not a letter or a digit. So ` $w_0$ ` renders and
  `cm$^{-3}$`, `2.92$\times$syst` and `$\pm$0.0043` are left on the page as
  raw source. The rule is undocumented by GitHub and was established by
  rendering probe documents through its own markdown endpoint on 2026-08-09,
  which found 203 such spans in this repository. A second cause is independent:
  `<` or `>` inside mathematics is escaped to an HTML entity before the maths is
  read, so it can never render. Both are enforced by
  `tests/test_docs_math_render.py`. Prefer Unicode for a single symbol, which is
  what `docs/CLAIMS.md` does throughout, and keep LaTeX for display maths and
  bibliographic fields.
- **A quotation is never altered to satisfy a rendering rule.** Where a quoted
  symbol cannot render, the platform loses rather than the quote. The maths
  guard exempts the span whose delimiter touches the quotation mark on a
  verbatim line, and nothing else on that line.
- **matplotlib mathtext is not markdown.** Inside a figure label `$10^{12}$cm$^{-3}$`
  is correct and renders. The adjacency rule above is a GitHub rule and applies
  to documents only. Applying it to a label would break every unit on every axis.
- **LaTeX stays in bibliographic fields.** `title:` and `pages:` in
  `docs/lit/*.md` keep publisher/BibTeX form (`{Rb}`, `$6S_{1/2}$`,
  `855--865`) because they feed `references.bib`. Author names use Unicode
  accents (Síle, Bordé, Wcisło), which modern LaTeX takes and which are
  correct on the page.
- **No thin-space macros** (`\,`, `\;`, `\!`) in Markdown maths. GitHub's
  renderer eats the backslash. `tests/test_docs_math_render.py` catches these.
- **Quote arXiv IDs** in YAML (`arxiv: '2201.06000'`), or a trailing zero is
  lost to float parsing.

## Figures

- **An axis label is a quantity and a unit.** Not a sentence, not a caveat, not
  a status and not an argument. One x label read "beam waist (µm). This has not
  been measured. The knife-edge scan is pending." and five residual axes read
  "residual, in units of the point error". A census on 2026-08-09 found 156 of
  235 label strings defective in that way.
- **Every frequency axis says which frequency it carries**, the laser one or
  the two-photon one, in those words. Every width axis says FWHM. Every density
  axis uses one form of the unit.
- **A title states what is plotted**, not what it proves. The conclusion belongs
  in the caption.
- **The caveat moves to the caption of the document that references the figure**,
  and it must actually arrive there. Deleting it from the canvas without placing
  it loses information the reader needs.
- **A caption asserts only what its panels draw.** The first caption written for
  the pooled-width figure described a different analysis, and reading the image
  is what caught it.
- **The provenance footer is a contract, not prose.** It may carry file paths and
  pipeline vocabulary because it exists for reproducibility.
  `tests/test_figure_register.py` documents this and polices everything else
  drawn on the canvas.
- **Redraw only where `results/` is clean.** The figure fingerprint reads the
  working tree, so drawing while another session holds uncommitted CSVs stamps
  its numbers into a published PNG. Use a detached worktree at HEAD and confirm
  the fingerprint matches the tree you are publishing from.

## Private material

Correspondence and personal documents (CV, letters, briefs, reviewer notes)
live in the working tree but are never committed. `.gitignore` carries generic
patterns for them, and `tests/test_repo_hygiene.py` fails if a matching path
ever becomes tracked. Do not rely on `.git/info/exclude`, which is local to one
clone and does not survive a fresh checkout elsewhere.

## Commits

Explain why the change was needed, not only what moved. Where a fix corrects
an earlier error, say what was wrong. No generated-by or co-authored-by
trailers. Run the full suite (`pytest -q --runslow`) before pushing.
