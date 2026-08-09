# Per-paper notes

One Markdown file per reference, named for its citekey, 122 of them. Start at
[`../LITERATURE_INDEX.md`](../LITERATURE_INDEX.md), which lists every one with its status, routing and locus and
links each row to its note, or at [`../LITERATURE.md`](../LITERATURE.md), the prose ledger over the same set.

Each note opens with a frontmatter block of structured fields, then a free body. The field names are fixed only
in [`../../scripts/build_lit_index.py`](../../scripts/build_lit_index.py), so read that alongside
[`arora2012.md`](arora2012.md) and [`herold2012.md`](herold2012.md) before writing a new one. `status` records
what has been done to a paper. VERIFIED means the source itself was read here. REPORTED means it was not, so
the note rests on a second-hand record and nothing in it may be cited until that changes. `held` says only
that a copy is on disk, and a held paper nobody has read stays REPORTED.

A passage marked verbatim is quoted exactly as printed, and a note names the source of any number or record it
did not take from the paper.
