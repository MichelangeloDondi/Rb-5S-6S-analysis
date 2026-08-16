"""The selector contract: what each file-list helper is FOR, pinned by example.

WHY THIS FILE EXISTS. On 2026-08-15 the tracked-only blind spot was repaired
by routing nine test modules through one helper, and the repair silently
WIDENED six of them, because a bare git pathspec is not shell globbing: in
`git ls-files docs/*.md` the `*` crosses slashes and matches 169 files, where
the `Path.glob` it replaced matched the 22 at the top level. Every affected
test still passed, because a guard that reads MORE files finds no fewer
offences. The failure surfaced two modules away, in a citation check whose
domain had grown by 139 files.

So the tests below pin the DOMAIN of each selector rather than its output on
today's tree: an included example, an excluded example, and a
depth-sensitive case that distinguishes recursive from top-level. A future
rewrite that changes the semantics fails here, at the selector, instead of
somewhere downstream.

Rule 19.18 states the general form (an array's units and DOMAIN are part of
its contract). A path selector's domain is exactly that, and this file is its
machine check.
"""
from __future__ import annotations

import subprocess

import pytest

from _fileset import ROOT, about_to_be_tracked, tracked, tracked_and_new


# --------------------------------------------------------------- the contract
# selector spec: (pathspecs, recursive?, one path it MUST include,
#                 one it MUST exclude)
CONTRACTS = [
    pytest.param(("docs/*.md",), True,
                 "docs/methods/01_the_measurement.md", "README.md",
                 id="bare-pathspec-is-recursive"),
    pytest.param((":(glob)docs/*.md",), False,
                 "docs/BIG_PICTURE.md", "docs/methods/01_the_measurement.md",
                 id="glob-magic-is-top-level"),
    pytest.param((":(glob)docs/methods/*.md",), False,
                 "docs/methods/01_the_measurement.md", "docs/BIG_PICTURE.md",
                 id="glob-magic-scopes-to-one-directory"),
    pytest.param(("*.md",), True,
                 "docs/lit/nieddu2019.md", "rb5s6s/linefit.py",
                 id="extension-pathspec-spans-the-tree"),
]


@pytest.mark.parametrize("specs,recursive,must_include,must_exclude", CONTRACTS)
def test_selector_domain(specs, recursive, must_include, must_exclude):
    got = set(tracked_and_new(*specs))
    assert must_include in got, (
        f"{specs} lost {must_include}. The selector's domain narrowed.")
    assert must_exclude not in got, (
        f"{specs} gained {must_exclude}. The selector's domain widened, which "
        f"is the 2026-08-15 defect: a guard reading more files still passes.")
    # Nesting is judged against the SELECTOR'S OWN directory prefix, not a
    # hardcoded one: "docs/methods/*.md" is top-level for its prefix even
    # though its paths are nested under docs/.
    spec = specs[0].replace(":(glob)", "")
    prefix = spec.rsplit("/", 1)[0] + "/" if "/" in spec else ""
    under = [p[len(prefix):] for p in got if p.startswith(prefix)]
    nested = any("/" in p for p in under)
    if recursive:
        assert nested, f"{specs} is meant to reach into subdirectories and did not"
    else:
        assert not nested, f"{specs} is meant to be top-level and recursed"


def test_bare_and_glob_pathspecs_actually_differ():
    """The distinction this whole file exists for, asserted directly.

    If these ever agree, either git changed or the helper stopped passing
    pathspecs through, and every contract above becomes vacuous.
    """
    bare = set(tracked_and_new("docs/*.md"))
    globbed = set(tracked_and_new(":(glob)docs/*.md"))
    assert globbed < bare, "':(glob)' no longer restricts to one directory"
    assert len(bare) > 3 * len(globbed), (
        "the recursive/top-level gap collapsed, so the contract tests below "
        "would no longer catch a widening")


def test_tracked_and_new_is_the_union_and_excludes_ignored(tmp_path):
    """New-and-not-ignored comes in; ignored stays out. Both halves matter."""
    probe = ROOT / "docs" / "_contract_probe.md"
    ignored = ROOT / "private" / "_contract_probe.md"
    assert not probe.exists()
    try:
        probe.write_text("probe\n", encoding="utf-8")
        got = tracked_and_new("docs/*.md")
        assert "docs/_contract_probe.md" in got, (
            "an untracked, unignored document is invisible, which is the hole "
            "that let 0caf19a5 ship a semicolon through a green gate")
        assert "docs/_contract_probe.md" not in tracked("docs/*.md")
        assert "docs/_contract_probe.md" in about_to_be_tracked("docs/*.md")
    finally:
        probe.unlink(missing_ok=True)

    if (ROOT / "private").is_dir():
        wrote = False
        try:
            if not ignored.exists():
                ignored.write_text("probe\n", encoding="utf-8"); wrote = True
            assert not any(p.startswith("private/")
                           for p in tracked_and_new("*.md")), (
                "gitignored content reached a guard, which is the opposite "
                "defect the rglob-plus-denylist selectors used to have")
        finally:
            if wrote:
                ignored.unlink(missing_ok=True)


def test_helpers_degrade_quietly_outside_a_checkout(monkeypatch):
    """Outside git the helpers return empty rather than raising, so a guard
    skips instead of erroring. Pinned because several callers branch on it."""
    def boom(*a, **k):
        class R:
            returncode = 128
            stdout = ""
        return R()
    monkeypatch.setattr(subprocess, "run", boom)
    assert tracked("*.md") == []
    assert about_to_be_tracked("*.md") == []
    assert tracked_and_new("*.md") == []
