"""The platform-lane promise in BIG_PICTURE.md is checkable, so it is checked.

WHAT THE PROMISE IS. `docs/BIG_PICTURE.md` tells a reader with no fibre
interest that the fibre thread of this repository is exactly three surfaces,
and that "everything else, the method, the results, the plan and the wiki, is
platform-neutral", so they may skip those three "and lose nothing on their
path". That is not a decoration. It is a load-bearing claim about what a
reader can skip, and it is the kind of claim that decays silently: one number
quoted from a fibre result in a platform-neutral chapter breaks it, and
nothing else in the tree would notice.

WHAT THIS GUARD DOES NOT DO, and why. A keyword sweep for "fibre" across
docs/ matches fifty-four files, nearly all of them legitimately: literature
notes on nanofibre papers, the bibliography, and the apparatus chapter
describing a bench that really did have a nanofibre in it. A guard that fired
on those would be measuring vocabulary, not the promise, and would be turned
off within a week. The promise is about the reader's PATH, not about which
words occur.

WHAT IT DOES INSTEAD. It checks the dependency the promise actually forbids:
no platform-neutral surface may cite a result that only the fibre layer
produces. That is the mechanism by which skipping a lane surface would start
costing a reader something, and it is also the exact path by which a
SIMULATION-BACKED fibre result would be promoted into the record's measured
claims -- the failure the epistemic classes exist to prevent.

THE GUARD READS THE PROMISE IT ENFORCES. The lane is parsed out of
BIG_PICTURE.md rather than restated here, so the two cannot drift apart. If
the fibre thread ever grows a fourth surface, the paragraph is where it is
declared and this guard follows it automatically. If the paragraph disappears,
the guard fails loudly rather than passing over an empty set.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# A results CSV only the fibre layer produces. Derived from the producers that
# describe a guided platform, and asserted non-empty below so a rename cannot
# empty it silently.
FIBRE_ONLY_RESULTS = ("fibre_twin.csv", "onf_candidate.csv")

# Index and catalogue files list every surface by design; a one-line row naming
# a fibre note is the catalogue doing its job, not a dependency on it.
INDEX_FILES = {"README.md", "RESULTS.md"}


def _lane_surfaces():
    """The fibre thread, parsed from the promise itself.

    The paragraph names its surfaces BEFORE the words "Everything else"; the
    link that follows them points at ADAPTING.md and names a kind of reader,
    not a lane surface, so the split is on that phrase rather than on the
    paragraph.
    """
    text = (DOCS / "BIG_PICTURE.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*The platform lane[^*]*\*\*(.*?)Everything else", text, re.S)
    assert m, ("the platform-lane promise is gone from docs/BIG_PICTURE.md. "
               "Either restore it or delete this guard deliberately -- do not "
               "leave a guard standing over a claim nobody makes any more.")
    return {link for link in re.findall(r"\]\(([^)]+)\)", m.group(1))
            if link.endswith(".md")}


def test_the_promise_names_a_nonempty_lane():
    lane = _lane_surfaces()
    assert lane, "the platform-lane paragraph names no surfaces"
    for rel in lane:
        assert (DOCS / rel).exists(), f"the promise names a missing surface: {rel}"


def test_the_fibre_only_results_exist():
    """Otherwise the guard below passes over an empty set."""
    missing = [n for n in FIBRE_ONLY_RESULTS
               if not (ROOT / "results" / n).exists()]
    assert not missing, (
        f"fibre-only results named here are absent from results/: {missing}. "
        "A rename must update this list, or the lane guard checks nothing.")


def _citing_files():
    hits = {}
    for path in sorted(DOCS.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found = [n for n in FIBRE_ONLY_RESULTS if n in text]
        if found:
            hits[str(path.relative_to(DOCS))] = found
    return hits


def test_no_platform_neutral_surface_cites_a_fibre_only_result():
    lane = _lane_surfaces()
    bad = []
    for rel, names in _citing_files().items():
        if rel in lane or Path(rel).name in INDEX_FILES:
            continue
        bad.append(f"{rel}: {', '.join(names)}")
    assert not bad, (
        "these platform-neutral surfaces cite a result only the fibre layer "
        "produces, which breaks the promise in docs/BIG_PICTURE.md that a "
        "reader with no fibre can skip the fibre thread and lose nothing:\n  "
        + "\n  ".join(bad)
        + "\n\nEither move the claim into the fibre thread, or widen the "
          "platform-lane paragraph to name the surface -- and mean it.")


def test_the_lane_guard_fires_when_a_violation_is_planted(tmp_path):
    """A guard that has never fired cannot be told from one that cannot."""
    lane = _lane_surfaces()
    planted = "docs/methods/02_the_lineshape.md"
    assert planted not in lane, "the ceiling test needs a platform-neutral file"

    def check(rel, text):
        if rel in lane or Path(rel).name in INDEX_FILES:
            return False
        return any(n in text for n in FIBRE_ONLY_RESULTS)

    assert check(planted, "the coverage in `results/fibre_twin.csv` shows"), (
        "the planted citation was not detected")
    assert not check(next(iter(lane)), "results/fibre_twin.csv"), (
        "a lane surface must be allowed to cite its own results")
