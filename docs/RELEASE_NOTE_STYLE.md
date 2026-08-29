# Release note style

The rules a release body must satisfy before it is published, written
after every release note published on this project's two repositories
was read against one defect list and found to carry the same defects. The
mechanical half is enforced by `scripts/check_release_notes.py`. The
judgement half is enforced by the readers in the last section.

## The note's form

A release note must be readable, and checkable against the repository,
by a physicist in under a minute.

* **N1.** The first sentence after the title states the single most
  decision-relevant change. When no measured number changed, it says so.
* **N2.** The body stays at or under 300 words. The checker refuses above
  400. The repository documents everything else, and the note cites it.
* **N3.** Every number names its committed file in the same sentence. A
  value with no committed source does not appear. **This is the rule the
  withdrawn v4.3 and v4.4 notes broke, and the owner named their failure as
  the physics, not the register**: a waist no producer
  computes, a one-sided bound divided by a point prediction with the quotient
  called the disagreement, a null reported as a measured size. Its mechanical
  half is now in the checker, over quantities carrying a physical unit. Two
  halves stay with a person, because no script makes them: **a ratio says
  which of its terms is a limit and which a prediction**, and **a directional
  statement is scored against the constant the package carries**. A percentage names its
  denominator. A factor names both of its ends.
* **N4.** No internal shorthand. Pipeline and deliverable codes (the
  M, C, K and P series) appear only inside file paths. No nicknames for
  documents or constructions. A term a cold reader cannot resolve inside
  the note is either defined where it first appears or not used. Physics
  vocabulary that collides with the code pattern, such as the M1
  multipole label or the C3 dispersion coefficient, passes when one of
  the next few words names the physics (transition, coefficient,
  dispersion, multipole).
* **N5.** No sentence takes the record, the workflow, or the note itself
  as its subject. A correction is one sentence: old value, new value,
  cause, and where the change is disclosed.
* **N6.** An upper limit is written as "below X at 95 per cent" with its
  axis. A forecast is labelled a forecast. A decision is labelled a
  decision. A sensitivity is labelled a sensitivity.
* **N7.** Plain declarative register. No lists of three built for
  cadence. No headline aphorisms. No reversal constructions. No
  personified abstractions. No dramatic colon reveals.
* **N8.** The fixed template, and nothing outside it:
  1. title: `vX.Y:` then at most six plain words naming the change
  2. the first-line fact
  3. **Numbers that moved**, one line each, `old -> new (file, row)`
  4. **New**, what a reader can now use, one line each
  5. **Corrections**, per N5
  6. **Unchanged**, the standing headline bounds with values and files
* **N9.** The two repositories publish one identical body per version, so
  the body carries no count that differs between their trees. Any count
  it does carry is checked against the tagged tree before publishing.
* **N10.** A page reconstructed for an already-published tag states the
  frozen record in the template's Unchanged form and closes with one
  provenance line naming the `docs/HISTORY.md` disclosure. The
  reconstruction fact is that closing line, never the opening one.
* **N11. A note reports a change and names where it is recorded. It does not
  perform the inference in front of the reader.** It does not weigh evidence,
  explain how a finding was reached, or narrate a correction as a discovery
  with a discoverer and a moment of realisation. That belongs in
  `docs/RESULTS.md`, in `docs/history/`, or in the results row the note cites,
  and the note points at it in one clause.

  **This rule was missing, and it is one of two things the withdrawn pages
  broke. The other was the physics, and it was the larger half**, on the
  owner's reading. N3 carries the half a script can check. N5 forbids taking the record or the workflow as a sentence's
  subject, which is a constraint on grammar. The withdrawn notes passed that
  test sentence by sentence and failed as documents, because their genre was a
  results narrative rather than a ledger of deltas. A reading of the four
  withdrawn notes found that one carrying exactly those defects, while
  avoiding the banned phrases and staying under the ceiling, passes
  `scripts/check_release_notes.py` clean.

**What is mechanised, and most of this is not.** Of the rules above, the
checker enforces N2's word ceiling, N3's citation requirement over united
quantities, N4's shorthand codes and N7's phrase list, each in its narrowest
form. N1, N5, N6, N8, N9, N10 and N11 have no mechanism, so they are read by a person or they are
not read at all. **The
checker is wired into no gate.** The drill names it, so a release runs it by
procedure and not by memory. Stated
here instead of left to be discovered, because this document previously
implied the opposite.

## The checks before publishing

* The body passes `scripts/check_release_notes.py` before anyone reads
  it.
* The standing pre-release board gains two readers for a release: a
  voice reader, reading only for register against N7, and a cold
  reader, who receives the note alone with no repository access and must
  state what changed, quote the headline numbers, and resolve every
  term. Either reader can block. The cold reader exists because anyone who
  knows the repository resolves undefined terms without noticing them.
* A published body is edited in place only with a disclosure entry in
  `docs/HISTORY.md` naming what changed and why.
