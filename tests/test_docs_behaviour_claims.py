"""Prose claims about what a SCRIPT DOES, checked against what it does.

WHY THIS EXISTS. The tree is well guarded against stale NUMBERS: the canonical
registry in `test_docs_canonical.py` derives ~31 headline quantities live and
fails on any stale citation of them. It is not guarded at all against stale
BEHAVIOUR claims, and the protocol says so in its own words
(`private/RENDERING_PROTOCOL.md` section 19.2): "A guard keyed to data
freshness is silent on text freshness... Whenever a pass changes words rather
than numbers, name in advance what will detect a mistake. If the answer is
nothing, that is the finding."

The finding, 2026-08-15: `docs/methods/04_the_composite_model.md` described
`run_trapping_channels.py` and `run_blackbody_channels.py` as "both opt-in and
writing nothing". Both run unconditionally in `scripts/run_all.sh` and both
write a committed CSV. Two false statements in one clause, in a methods
chapter, past every existing guard, because no guard reads a sentence about a
script and compares it with the script.

WHAT THIS CHECKS. Two claim classes, both mechanically decidable:

  IS IT RUN?    prose saying a script is opt-in / not run / must be run by hand
                is checked against the invocation list in run_all.sh.
  DOES IT WRITE? prose saying a script writes nothing / produces no output is
                checked against whether the script writes into RESULTS_DIR.

WHAT THIS DELIBERATELY DOES NOT CHECK. Whether a script's description is a GOOD
one, whether the claimed physics is right, or any claim needing judgement. This
is a guard for the mechanically decidable subset, and the rest stays
ATTENTION-ONLY BY DESIGN, which the protocol treats as a permanent and
legitimate state rather than a deficiency.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DOCS = REPO / "docs"
SCRIPTS = REPO / "scripts"
RUN_ALL = SCRIPTS / "run_all.sh"

# how close a claim has to sit to a script's name to count as being about it.
# generous enough to span a wrapped sentence, tight enough that an unrelated
# clause two sentences away does not trip it.
WINDOW = 240

NOT_RUN_PHRASES = (
    "opt-in", "opt in", "not run by", "never run", "is not run",
    "run by hand", "run manually", "must be invoked", "not part of the pipeline",
    "not in the pipeline", "not called by",
)
NO_OUTPUT_PHRASES = (
    "writing nothing", "writes nothing", "writes no", "produces no output",
    "produces nothing", "no committed output", "writes no csv",
)


def _scripts_in_run_all() -> set[str]:
    """Stems the pipeline actually invokes. run_all.sh both loops over bare
    stems and calls `python scripts/<stem>.py` directly, so both forms count."""
    text = RUN_ALL.read_text(encoding="utf-8")
    stems = set(re.findall(r"scripts/(\w+)\.py", text))
    # the for-loop form lists bare stems across continued lines
    for block in re.findall(r"for\s+s\s+in\s+(.*?);\s*do", text, re.S):
        stems |= {w for w in re.findall(r"\b(run_\w+)\b", block)}
    return stems


# A WRITE idiom, not merely a mention of the results directory. The first
# version of this guard tested only for `RESULTS_DIR / "..."` and fired on two
# documents that were CORRECT: run_companion_refit.py and run_saturation_probe.py
# both name RESULTS_DIR only to READ (`open(..., newline="")`,
# `csv.DictReader(open(...))`). A guard's first firing is evidence to audit, not
# an instruction to obey, and obeying that one would have written a falsehood
# into two accurate notes.
_WRITE_IDIOM = re.compile(
    r"""open\([^)]*,\s*["']w["']          # open(..., "w")
      | \.to_csv\(                        # pandas
      | csv\.DictWriter\(
      | csv\.writer\(
      | \.write_text\(
    """, re.X)


def _writes_results(stem: str) -> bool:
    """Does this script WRITE into the results directory? It must both name
    RESULTS_DIR and contain a write idiom. Reading a committed CSV is not
    writing one."""
    p = SCRIPTS / f"{stem}.py"
    if not p.exists():
        return False
    src = p.read_text(encoding="utf-8")
    return bool(re.search(r"RESULTS_DIR", src)) and bool(_WRITE_IDIOM.search(src))


def _doc_files() -> list[Path]:
    # The walk stays directory-based because test_guard_fires_on_a_planted_claim
    # monkeypatches DOCS to a tmp tree. For the REAL tree it is then filtered
    # through git, which drops ignored local scaffolding (docs/reference_setup)
    # that a bare rglob would scan.
    walked = sorted(q for q in DOCS.rglob("*.md") if "lit/" not in str(q))
    if DOCS != REPO / "docs":
        return walked
    from _fileset import tracked_and_new
    ship = {str(REPO / r) for r in tracked_and_new("docs/*.md", "docs/**/*.md")}
    return [q for q in walked if str(q) in ship]


def _claims():
    """Yield (path, stem, phrase, kind) for every behavioural claim found."""
    run_set = _scripts_in_run_all()
    stems = [q.stem for q in SCRIPTS.glob("run_*.py")]
    for doc in _doc_files():
        text = doc.read_text(encoding="utf-8")
        low = text.lower()
        for stem in stems:
            for m in re.finditer(re.escape(stem), text):
                lo = max(0, m.start() - WINDOW)
                hi = min(len(text), m.end() + WINDOW)
                near = low[lo:hi]
                for ph in NOT_RUN_PHRASES:
                    if ph in near:
                        yield doc, stem, ph, "not_run", stem in run_set
                for ph in NO_OUTPUT_PHRASES:
                    if ph in near:
                        yield doc, stem, ph, "no_output", _writes_results(stem)


def test_prose_does_not_call_a_pipeline_script_opt_in():
    """A doc saying a script is opt-in, beside a script run_all.sh runs."""
    bad = []
    for doc, stem, ph, kind, reality in _claims():
        if kind == "not_run" and reality:
            bad.append(f"{doc.relative_to(REPO)}: says '{ph}' near {stem}, "
                       f"which scripts/run_all.sh invokes")
    assert not bad, (
        "Prose calls a script opt-in or not-run when the pipeline runs it:\n  "
        + "\n  ".join(sorted(set(bad)))
        + "\nFix the sentence, or if the pipeline changed, fix run_all.sh.")


def test_prose_does_not_say_a_writing_script_writes_nothing():
    """A doc saying a script writes nothing, beside a script that writes a CSV."""
    bad = []
    for doc, stem, ph, kind, reality in _claims():
        if kind == "no_output" and reality:
            bad.append(f"{doc.relative_to(REPO)}: says '{ph}' near {stem}, "
                       f"which writes into results/")
    assert not bad, (
        "Prose says a script writes nothing when it writes a committed CSV:\n  "
        + "\n  ".join(sorted(set(bad)))
        + "\nName the file it writes instead.")


def test_the_guard_can_actually_see_the_repository():
    """A guard that finds nothing because it is looking in the wrong place
    passes forever. Pin the inputs so an empty result means 'clean' and not
    'broken' (lesson 56: a guard skipped on the public mirror had never once
    run there, and drifted 19 per cent behind).
    """
    assert RUN_ALL.exists(), "run_all.sh not found: the not-run check is inert"
    run_set = _scripts_in_run_all()
    assert len(run_set) > 10, f"only {len(run_set)} scripts parsed from run_all.sh"
    assert "run_linefit" in run_set, "run_all.sh parse missed a known pipeline stem"
    assert len(_doc_files()) > 20, "docs sweep found almost nothing"
    # and at least one script really does write, or the writer check is inert
    assert any(_writes_results(q.stem) for q in SCRIPTS.glob("run_*.py")), \
        "no script detected as writing to results/: the writer check is inert"


@pytest.mark.parametrize("kind,phrase,stem", [
    ("not_run", "opt-in", "run_linefit"),
    ("no_output", "writes nothing", "run_linefit"),
])
def test_guard_fires_on_a_planted_claim(tmp_path, monkeypatch, kind, phrase, stem):
    """Both directions. A guard only ever seen to pass has not been tested, so
    put a deliberately false claim in a temporary docs tree and require the
    detector to find it."""
    fake_docs = tmp_path / "docs"
    fake_docs.mkdir()
    (fake_docs / "planted.md").write_text(
        f"The stage is handled by `scripts/{stem}.py`, which is {phrase} "
        f"and therefore of no concern here.\n", encoding="utf-8")
    monkeypatch.setattr(f"{__name__}.DOCS", fake_docs)
    hits = [c for c in _claims() if c[3] == kind]
    assert hits, f"planted '{phrase}' near {stem} was NOT detected"
