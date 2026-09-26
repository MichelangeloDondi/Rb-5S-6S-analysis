"""A module renamed away leaves no route to its old name in the tracked tree (V7.1's board, 2026-09-26).

O61 stage A renamed `rb5s6s/cumulants.py` to `rb5s6s/moments.py` and moved every import, while five routes kept the old
name: `tests/test_docs_dotted_routes.py` resolves `rb5s6s.`-prefixed routes on the methods pages only, so a bare route on
a methods page and every route inside a `.py` docstring sat outside its population. This reads the whole tracked tree
outside the records for a route through a RETIRED module name; each retired name carries the module that replaced it,
and a later rename adds its row.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: a module renamed away -> the module that replaced it
RETIRED = {"cumulants": "moments"}

#: records keep the old names by design, and this file names them to plant the reader
EXCLUDED = ("docs/lit/", "docs/history/", "private/", "tests/test_retired_module_routes.py")


def _route(name: str) -> "re.Pattern":
    return re.compile(rf"(?<![A-Za-z_]){name}\.[a-z_][A-Za-z_0-9]*|rb5s6s/{name}\.py|rb5s6s\.{name}\b")


def retired_routes(texts) -> list:
    """(path, text) pairs -> 'path:line: text' for every route through a retired module outside the records."""
    out = []
    for rel, text in texts:
        if rel.startswith(EXCLUDED):
            continue
        for name in RETIRED:
            rx = _route(name)
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    out.append(f"{rel}:{i}: {line.strip()[:120]}")
    return out


def _tracked():
    listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.py", "*.md", "*.toml", "*.txt"],
                            capture_output=True, text=True, check=True).stdout.split()
    for rel in listed:
        try:
            yield rel, (ROOT / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue


def test_no_route_names_a_retired_module():
    hits = retired_routes(_tracked())
    assert not hits, ("routes through a retired module name; each becomes the module RETIRED names:\n"
                      + "\n".join(hits))


def test_the_reader_sees_every_spelling_and_spares_prose_and_records():
    hits = retired_routes([
        ("rb5s6s/a.py", '"""The baseline of `cumulants._centred_window_moments`."""'),
        ("docs/methods/b.md", "`cumulants.windowed_moments` coerces its orders"),
        ("scripts/c.py", "from rb5s6s.cumulants import windowed_moments"),
        ("docs/d.md", "see rb5s6s/cumulants.py"),
        ("docs/lit/e.md", "`cumulants.windowed_moments` in a held note"),
        ("rb5s6s/f.py", "through cumulants' additivity under convolution"),
        ("rb5s6s/g.py", "the higher cumulants. The next order"),
    ])
    assert [h.split(":")[0] for h in hits] == ["rb5s6s/a.py", "docs/methods/b.md", "scripts/c.py", "docs/d.md"], hits
