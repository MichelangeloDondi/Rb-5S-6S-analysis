"""Every `rb5s6s.<module>.<name>` a methods page names as a route resolves in the package.

WHY THIS EXISTS (the audit of 2026-09-25). Owner order O49 retired the cumulant functions from
rb5s6s/moments.py in code and in tests, and four methods pages went on telling a reader to call
them, one of them under its own "Route to re-derive" heading, which is the third of the four things
every model term carries. Nothing read a dotted path in prose against the live package, so a route
could name a function that no longer existed for days and every check stayed green. This reads the
backticked `rb5s6s.x.y` paths of docs/methods/, the pages that carry the routes, and imports each.

A path that names a module resolves by importing it; a path that names an attribute resolves by
walking getattr from the deepest importable module. A retired name a page keeps as history is
written without the `rb5s6s.` prefix, which is how the pages already mark one.
"""
import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted((ROOT / "docs" / "methods").glob("*.md"))
DOTTED = re.compile(r"`(rb5s6s(?:\.[A-Za-z_][A-Za-z0-9_]*)+)(?:\([^`]*\))?`")


def _resolves(path: str) -> bool:
    parts = path.split(".")
    for i in range(len(parts), 0, -1):
        try:
            obj = importlib.import_module(".".join(parts[:i]))
        except ImportError:
            continue
        for attr in parts[i:]:
            if not hasattr(obj, attr):
                return False
            obj = getattr(obj, attr)
        return True
    return False


def _citations():
    out = []
    for page in PAGES:
        for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            for m in DOTTED.finditer(line):
                out.append((f"{page.relative_to(ROOT).as_posix()}:{n}", m.group(1)))
    return out


def test_the_methods_pages_name_package_routes():
    """A guard over an empty population passes for the wrong reason."""
    assert _citations(), ("no backticked rb5s6s dotted path found in docs/methods/, so this guard "
                          "checks nothing: the fence syntax changed, or the pattern needs updating")


def test_every_dotted_route_resolves():
    bad = [f"{where}: {path}" for where, path in _citations() if not _resolves(path)]
    assert not bad, ("these methods pages name a package route that does not exist, so a reader "
                     "following it gets an ImportError or an AttributeError:\n  " + "\n  ".join(bad))


def test_the_resolver_discriminates():
    """The plant, both ways, through the real resolver: a live function resolves, the retired
    cumulant function and a misspelt module do not."""
    assert _resolves("rb5s6s.moments.windowed_moments")
    assert _resolves("rb5s6s.lineshape")
    assert not _resolves("rb5s6s.moments.windowed_cumulants")
    assert not _resolves("rb5s6s.cumulantz.windowed_moments")
