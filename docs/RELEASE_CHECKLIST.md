# Release checklist

The framework is a RELEASE CANDIDATE and the release act is the owner's. This
page is what that act requires, assembled so it can be worked through rather
than reconstructed. Nothing here has been performed.

## What "release" would change

The repository already installs, imports without data, and runs its examples
from a bare clone. Releasing changes one thing only: it invites people who
have never seen this experiment to use the framework on their own data. Every
item below exists to make that invitation honest.

## Before the release

**1. Decide what the version means.** The package is at 4.1 and the framework
and the rubidium result move independently, which the README states. A release
should say which of the two the number tracks. The current answer is the
framework, and it is worth saying so in `pyproject.toml`'s description rather
than leaving it inferred.

**2. Retire or keep the release-candidate paragraph.** README carries "no
independent scientist has installed this and applied it to a dataset that is
not ours, so this is a release candidate rather than a community release."
That sentence is TRUE and it is the most useful sentence in the file for
anyone deciding whether to adopt the framework. Releasing does not make it
false. Keep it, and add the date of the first outside application when there
is one.

**3. Refresh `CITATION.cff`.** Version, date, and the author list. The DOI, if
one is minted, goes here and in the README badge.

**4. Confirm the two entry points still run from a clean environment.** In a
fresh virtual environment, from a clone with `data_raw/` absent:

```
pip install -e ".[dev]"
python examples/synthetic_recovery.py
python examples/full_model_tour.py
pytest -q
```

The first two must complete without touching `results/` or `data_raw/`. The
suite will skip the data-dependent tests and must not fail.

**5. Build the distribution and install it somewhere else.**

```
python -m build
pip install dist/rb5s6s-<version>-py3-none-any.whl
python -c "import rb5s6s; print(rb5s6s.__version__)"
```

Installing the wheel rather than the source tree is the only check that
catches a package that depends on files the wheel does not carry.

**6. Decide about the optional extra.** `cascade` pulls sympy for the exact
manifold computation. The committed coefficient table means a plain install
has the physics without it, so the extra is genuinely optional, and the
release notes should say that rather than leaving it to be discovered.

**7. State what the framework does NOT do.** It does not download data, does
not fit anything it has not been given a model for, and its noise-law
coefficients and quality-control thresholds are calibrated to one apparatus.
`docs/ADAPTING.md` is the seam map and should be linked from the release
notes, because the first real question anyone adopting this asks is which
numbers they have to replace.

## The 4.2 release, verified 2026-08-20

Both repositories were pushed, tagged v4.2 at their heads, and given release
objects titled "v4.2: the digital twin", confirmed non-draft by the GitHub
CLI, with the mirror's tag commit equal to its branch head. Both pre-push
gates returned exactly one failure, the release-integrity guard itself
reporting that the declared 4.2 had no published release yet, which is that
guard's designed transient during any release and went green with the act.
The first release attempt was ABORTED by the automation's own check when the
port was found to have overwritten the mirror's push-trigger workflow with
the archive's dispatch-only one, a by-design divergence now excluded in
`scripts/port_to_mirror.sh` both ways.

## What the release does not need

A tutorial, a documentation site, and a paper are all reasonable things to
want and none is a precondition. The bus test is the criterion: a stranger
who installs the package can define a transition, simulate a line, fit it,
compare models and read an identifiability report inside five minutes, and
that path is `synthetic_recovery.py` followed by `full_model_tour.py`.

## After the release

Record the first outside application when it happens, in HISTORY, with what
broke. That is the only evidence that would let the release-candidate sentence
be retired, and it is worth waiting for rather than asserting.

---

## Verification run, 2026-08-19

Every mechanical item below was executed rather than asserted. The
judgement items are marked and remain open.

**READ THIS SECTION AS DATED RATHER THAN AS CURRENT.** Every check below was
measured against a public checkout that predates `rb5s6s/cascade.py`,
`rb5s6s/blackbody.py`, `rb5s6s/model_compare.py`, `rb5s6s/forecast.py`,
`docs/TUTORIAL.md` and the two example scripts that exercise them. A PASS
recorded on a tree is a statement about that tree. The whole section is
therefore re-run after the port and before the tag, and the re-run must reach
the four new modules and both new entry points, not only the eighteen names
the first run checked.

### The clean-environment check, run against the genuine public checkout

The first attempt at this was flawed and is recorded because the flaw is easy
to repeat: a clone of the ARCHIVE had its whole `data_raw/` removed, including
the two TRACKED files every real clone carries, `MANIFEST.csv` and
`README.md`. The suite then errored during collection, which looked like a
packaging defect and was a defect in the test.

Repeated against a fresh clone of the public mirror, which ships exactly those
two files and no traces, in a clean Python 3.12 environment:

  * `pip install -e ".[dev]"` completes.
  * `examples/synthetic_recovery.py` returns PASS, every parameter recovered
    within 3 of its own standard error, with no repository data present.
  * The full suite returns **2429 passed, 52 skipped, 1 xfailed, none
    failed**. It DEGRADES BY SKIPPING rather than erroring, which is what
    START_HERE promises and what the flawed first attempt appeared to deny.

### The wheel

`python -m build --wheel` produces a 200 KB wheel. Installed into a THIRD
environment, which is the only check that catches a package depending on
files the wheel does not carry, `rb5s6s.__version__` resolves and all 18
public API names import.

THE OUTSTANDING ITEM WAS RE-RUN on 2026-08-19 against the committed tree at
the fourteen-commit batch head. `python -m build --wheel` from a fresh local
clone produces `rb5s6s-4.1-py3-none-any.whl`. Installed into a THIRD
environment, a clean Python 3.14 venv holding nothing else: the version
resolves, all four expert modules import (cascade, blackbody, model_compare,
forecast), all 18 public API names resolve, `comb_tooth_weights` returns the
committed weights, and BOTH new entry points run from the installed package
in a bare directory outside any repository, `tutorial_forecast.py` and
`campaign_twin.py` each ending in their VERDICT: PASS line. The mirror-side
clean-environment suite run is repeated after the port, which is the one
check that has to wait for the port by construction.

### What is still a judgement and not a check

**What the version number tracks.** The package is at 4.1 while the README
states plainly that the framework and the rubidium result move independently.
A release should say which of the two the number follows. Nothing here can
decide that.

**`CITATION.cff`** carries version 4.1 dated 2026-08-18 and needs whatever
the version decision implies.

### On the release-candidate sentence

It stays. "No independent scientist has installed this and applied it to a
dataset that is not ours" remains true, and a release does not make it false.
It is the most useful sentence in the README for anyone deciding whether to
adopt the framework, and the date of the first outside application is what
would retire it.
