"""The chapter chains are coherent: every forward edge has its back edge.

The footer guard of the same wave checks position; the strategy seat of
round two found every walk defect to be one of coherence (a hub link seven
siblings lack, a hyphen for a middot, a back edge skipping a chapter). The
plan and big-picture footers name their neighbours by file, so the chain is
reconstructed from the footers themselves: chapter k's next is k+1 by number,
its previous is k-1, the first chapter's back link is the hub, the last's
forward link is the hub, and the separator is one middot.
"""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
NUM = re.compile(r"^(\d\d)_")


def _chapters(directory):
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", f"{directory}/*.md"], capture_output=True, text=True, check=True).stdout.split()
    return sorted(out)


def _footer(rel):
    lines = (ROOT / rel).read_text(encoding="utf-8").rstrip("\n").split("\n")
    return lines[-1]


def _links(rel):
    return [t for _, t in LINK.findall(_footer(rel))]


@pytest.mark.parametrize("directory,hub", [("docs/plan", "../PLAN.md"), ("docs/big_picture", "../BIG_PICTURE.md")])
def test_the_chapter_chain_is_coherent(directory, hub):
    chapters = _chapters(directory)
    assert len(chapters) > 5
    names = [Path(c).name for c in chapters]
    bad = []
    for i, rel in enumerate(chapters):
        links = _links(rel)
        want = []
        if i > 0:
            want.append(names[i - 1])
        if i < len(chapters) - 1:
            want.append(names[i + 1])
        neighbours = [l for l in links if l in names]
        if neighbours != want:
            bad.append(f"{rel}: footer neighbours {neighbours} where the chain wants {want}")
        if " - " in _footer(rel) or "··" in _footer(rel):
            bad.append(f"{rel}: the footer's separator is not one middot")
    assert not bad, "\n  ".join(bad)


def test_the_guard_reads_a_planted_break(tmp_path, monkeypatch):
    d = tmp_path / "docs" / "plan"; d.mkdir(parents=True)
    for k, nxt in ((1, 2), (2, 3), (3, None)):
        prev = f"0{k-1}_x.md" if k > 1 else "../PLAN.md"
        nxt_l = f"0{nxt}_x.md" if nxt else "../PLAN.md"
        (d / f"0{k}_x.md").write_text(f"# c{k}\n\ntext\n\n---\n\n*[p]({prev}) · [n]({nxt_l})*\n")
    (d / "02_x.md").write_text("# c2\n\ntext\n\n---\n\n*[p](../PLAN.md) · [n](03_x.md)*\n")   # the back edge skips chapter 1
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: type("R", (), {"stdout": "docs/plan/01_x.md docs/plan/02_x.md docs/plan/03_x.md"})())
    monkeypatch.setattr("test_navigation_chain_is_coherent.ROOT", tmp_path, raising=False)
    import test_navigation_chain_is_coherent as m
    m.ROOT = tmp_path
    with pytest.raises(AssertionError, match="02_x.md"):
        m.test_the_chapter_chain_is_coherent("docs/plan", "../PLAN.md")
