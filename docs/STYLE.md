# Writing and repository conventions

House rules for this repository's documents and code comments. They exist so
that every page reads in one voice and states exactly as much certainty as the
data support. `tests/test_repo_hygiene.py` enforces the mechanical ones.

**The question.** How should a claim, a number or a figure in this repository
be written, so that a reader can tell what it licenses without opening the code
behind it?
**Takes.** Nothing. This page is the convention the rest of the repository is
written against.
**Gives.** The rules for claims and certainty, for retired and superseded
values, for register, for figures, and for which files are generated rather
than edited.
**Skip if.** You are reading for the physics or the results. This page governs
how they are stated, not what they say.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## Claims and certainty

- **A bound is reported as a bound.** Where the dataset constrains rather than
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
  committed CSVs, and prose quotes them rather than restating them
  independently.
  `tests/test_docs_canonical.py` and `tests/test_ramp_geometry_docs.py` fail if
  a document and its producing code disagree.
- **Name the construction whenever you quote a number.** Five committed
  constructions in this repository produce a quantity called "S0(225 mW)", and
  three of them also carry rows that are REPLACED diagnostics kept for
  continuity. A bare "the bound" is ambiguous, and on 2026-08-14 a reader of
  this repository (the author) quoted `stark_sweep.csv`'s replaced Wald row
  2.205 in place of its actual bound, `S0_225mW_ub95_profile` = 0.632, whose own
  note says "quote the profile row". Say which file, and check the `status`
  column before quoting the row.
- **A number cited from a paper carries the sentence that states it.** Quote
  the source's own words, with page, wherever a result depends on the value.
  A summary that is not anchored to a quote drifts toward what the writer
  expected: the waist provenance survived for weeks as a "measured 1/e^2
  diameter" claim with no quote behind it, correct as it happened, beside a
  claim of independent corroboration that was not.
- **Before calling two sources independent, ask who collected the data.** Two
  documents reporting one measurement are not two measurements. The thesis and
  the paper that both give this apparatus's beam diameter are the same dataset,
  which the thesis says in a footnote, and the record claimed corroboration
  until 2026-08-14.
- **A retired value is marked as retired at every site that still names it.**
  When a constant is re-pinned, the edit is not finished at the constant: grep
  the OLD value across the tree and decide per site whether it is history or a
  live claim. `tests/test_repo_hygiene.py` now fails on a retired beam waist
  quoted beside a live claim, and the same discipline applies to any re-pin.
- **A superseded number is REPLACED here and RECORDED in `HISTORY.md`.** That
  file is the one place in this repository licensed to print a value the
  record no longer believes. Every other document, this one included, states
  only what is live, and refers to a superseded value by LINKING to
  `HISTORY.md` rather than repeating the number. Where the number was COMPUTED
  at the old value, recompute rather than relabel, since a relabelled table is
  a new falsehood rather than a surviving one. Earned 2026-08-15, when a
  pre-measurement stand-in for the beam waist survived a re-pin in three
  forward-looking documents and outvoted the one page that was right, which
  produced a wrong edit to the front page. The version history remains the
  complete record, and `HISTORY.md` is the curated part a reader needs
  without running `git log`.
- **Two documents agreeing is not corroboration if they share an ancestor.**
  Date a claim before counting the sites that repeat it, and resolve prose
  against its SOURCE (a constant, a CSV, a measurement) rather than against
  other prose. A consistency sweep with no source in it converges the tree onto
  whichever value is most widely repeated.
- **Do not carry a discrepancy you cannot adjudicate.** If two sites disagree
  and the deciding evidence is not reachable, the honest move is to reach it,
  by running the thing that prints it or by asking whoever knows. Recording
  "these disagree" and moving on leaves both numbers live and the reader worse
  off than before the discrepancy was noticed.

- **A quantity carries its units and its convention where it is used**, not
  only where it is defined. `sigma_laser` is a FWHM and its module docstring
  says so, three hundred lines above every call site, and the name says
  otherwise. The trace axis loaded from disk is a time in milliseconds and
  becomes a frequency only after multiplication by the condition's own rate.
  Both are documented and both were misread in one afternoon, so state the
  convention beside the number rather than trusting a reader to have found the
  definition.

- **A reimplemented number is checked against the record BEFORE it is
  reported.** Rebuild the fitted width and compare it with the committed one,
  rebuild the reduced chi-squared and compare it with the committed one, and
  only then read whatever new thing the reimplementation was built to measure.
  The order carries the whole value: a plausible number that has already been
  seen will be explained rather than doubted. Three checks against committed
  values caught three separate defects on 2026-08-15 before any of them
  reached a sentence.

- **A number that will not move when its lever moves is a defect, not a
  measurement.** A fraction of an amplitude that stays the same across a
  hundredfold change in that amplitude is not measuring what its name says.
  This tell is sharper than implausibility and available earlier, so where a
  quantity should scale with power, density or amplitude, vary that thing and
  show that it does.

- **Whether an effect is additive or multiplicative is measurable, and the
  answer changes what the effect is.** Regress it against the amplitude it
  might be proportional to, with a free intercept, over the widest range the
  data hold. An instrument artifact gives an intercept and no slope, and a
  model-shape error gives the reverse. Applied to the residual outside the fit
  window, this retired a description that had stood since the effect was first
  seen.

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
agree between themselves, and a public repository is not the place to announce
them. Write "a new operator", "the group", "an external theory check".

## Generated files: edit the generator, not the output

| File | Generator |
|---|---|
| `docs/RESULTS.md` | `scripts/make_results_ledger.py` |
| `docs/LITERATURE_INDEX.md` (+ a local, untracked `PDF_papers/README.md`) | `scripts/build_lit_index.py` |
| `docs/references.bib` | `scripts/build_lit_index.py` |
| `figures/*.png` | `scripts/make_figures.py` |
| `figures/fig0_spectrum.png` | `scripts/make_fig0_spectrum.py` |
| `docs/apparatus/program_timeline.png` | `scripts/make_timeline_figure.py` |
| `docs/wiki/figures/*.png` | `scripts/make_wiki_figures.py` |

Editing these directly is lost on the next run, and the freshness tests fail.

**Redraw with the generator you edited, by name, and then LOOK at the output.**
`scripts/run_all.sh` calls `make_fig0_spectrum`, `make_figures` and
`make_results_ledger`. It does NOT call `make_timeline_figure`, so a text edit
to that generator leaves a stale published PNG that every test passes over: the
figure-freshness guard hashes the RESULTS CSVs and asks whether a figure was
drawn from stale RESULTS, and a wording change moves no result. On 2026-08-14 a
panel title kept a retired word through a full sweep, two gates and two
commits, and was caught only by opening the image. Before relying on a runner,
check which generators it actually calls.

**A guard keyed to data freshness says nothing about text freshness.** Whenever
a pass changes words rather than numbers, name what will detect it.

**Editing a SOURCE regenerates its artifacts too.** The table above reads in
one direction, generator to output, and the trap runs the other way: the
literature notes under `docs/lit/` are hand-written SOURCES from which
`build_lit_index.py` generates `docs/LITERATURE_INDEX.md`, `docs/references.bib`
and a local `PDF_papers/README.md`. Editing one note therefore makes three
tracked files stale, and the gate is where that surfaces. After editing any
file, ask what is generated FROM it, not only what generates it.

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
- **No thin-space macros** (`\,` and its siblings) in Markdown maths. GitHub's
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
- **Compute every drawn number at draw time, from the function that produces
  it.** Never copy it from the document the figure illustrates. When a figure
  recomputed a companion width it came out at 28.2 kHz against the note's 25.4,
  and the difference was a collection half-length the note had never stated. The
  recomputation did not disagree with the note. It found the missing parameter.
- **Where a figure and a document give the same quantity, one of them is the
  authority and says so.** Two numbers of one name in two places is the defect,
  whether or not they currently agree.
- **Choose the form that is honest at both ends.** Three broadenings that all
  grow as the square of the power are drawn as three bars at one power, not as
  three curves, because at low power the smallest falls under the resolution of
  the frequency grid it is computed on and the curve would be drawing its own
  rounding. Where the obvious form was rejected, the reason goes in the
  generator's docstring, or the next pass restores it.
- **Look at the rendered image at every iteration, not once at the end.** Of
  four figures drawn on 2026-08-10, three had a defect visible only in the
  pixels: a legend over a curve, a clipped panel title, a caption past the right
  margin. All three passed every automated check first.
- **A figure embedded in no document is a defect at both ends**, the document
  reading as an unbroken wall and the figure as decoration.
  `figures/README.md` names, for each figure, the document it supports. If it
  can name one, the figure belongs in it.

## Document structure

Long documents are the main thing that makes this repository hard to enter, and
the fixes are cheap and were repeatedly not applied, so they are rules now
rather than habits. `tests/test_docs_structure.py` checks the first two.

**Any document over 2500 words opens with the four-line reader header.** The
methods chapters set the pattern and it is the most useful thing here for
somebody arriving without context:

```
**The question.** What this document answers, as a question.
**Takes.** What a reader should have read first, or "Nothing".
**Gives.** What they leave with.
**Skip if.** When not to read it. Say this honestly, including when the
answer is that a shorter document already covers it.
```

**Any document over 2500 words carries the glossary pointer**, as a blockquote
near the top, because a reader who lands in the middle of the repository from a
search result has no front door.

**A document over about 4000 words should show something before it argues.**
A figure in the first screen is worth more than a better paragraph, and there
are usually one already drawn: `figures/README.md` names, for every figure, the
document it supports. A figure embedded nowhere is a defect at both ends, the
document reading as an unbroken wall and the figure as decoration.

**Every embedded figure carries a caption in italics under it**, saying what
the reader should take from it rather than restating the axis labels. The
caption is the document's, not the figure's: on-canvas text stays to what the
axes cannot say (see Figures, above).

## One sentence, two copies

This project lives in two repositories with the same documents and different
contents: one carries the 297 raw traces, the published one carries the
manifest alone. So a sentence can be true where it is written and false where
it is read, and the guards cannot tell, because both copies pass their own
tests.

A published sentence must be true in EVERY copy it appears in. Where a fact
genuinely differs between copies, there are two honest resolutions and no
third:

- Say what depends on the copy and point at the one file that states it,
  `data_raw/README.md`. `START_HERE.md` takes this route, because
  `sync_public.sh` resolves a divergent file to the public version on
  conflict, and putting the front door on the hand-carry list would be a
  standing liability for one sentence.
- Or let the file diverge deliberately and be true locally in each tree, each
  copy acknowledging the other. `data_raw/README.md` is the worked example
  and is the reason the first route has somewhere to point.

A REPLACEMENT EARNS THE SAME TEST. On 2026-08-14 a batch of sentences of this
kind was corrected, and the first replacement written for `START_HERE.md`
said the fast suite needs no data because the tests that matter are synthetic.
True in the published copy. False in the one with the traces, where the
manifest re-hash is gated by trace presence alone and runs inside the
two-minute suite. Ask in which copy a replacement is true before writing it,
not after.

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
