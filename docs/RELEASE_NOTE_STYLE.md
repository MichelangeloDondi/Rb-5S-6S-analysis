# Release note style

The rules a release body must satisfy before it is published, written
after an adversarial review of every release note published on this
project's two repositories found the same defects in each one. The
mechanical half is enforced by `scripts/check_release_notes.py`. The
judgement half is enforced by the review seats in the last section.

## The note's form

A release note must be readable, and checkable against the repository,
by a physicist in under a minute.

* **N1.** The first sentence after the title states the single most
  decision-relevant change. When no measured number changed, it says so.
* **N2.** The body stays at or under 300 words. The checker refuses above
  400. The repository documents everything else, and the note cites it.
* **N3.** Every number names its committed file in the same sentence. A
  value with no committed source does not appear. A percentage names its
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

## The review

* The body passes `scripts/check_release_notes.py` before anyone reads
  it.
* The standing pre-release review adds two seats for a release: a voice
  seat, which reads only for register against N7, and a cold-reader
  seat, which receives the note alone with no repository access and must
  state what changed, quote the headline numbers, and resolve every
  term. Either seat can block. The cold-reader seat exists because
  reviewers who know the repository resolve undefined terms without
  noticing them.
* A published body is edited in place only with a disclosure entry in
  `docs/HISTORY.md` naming what changed and why.
