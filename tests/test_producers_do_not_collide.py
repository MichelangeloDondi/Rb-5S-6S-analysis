"""Every committed result CSV has exactly ONE producer.

WHY THIS EXISTS. On 2026-08-20 a new producer was written as
`scripts/run_identifiability.py`, writing `results/identifiability.csv`. Both
names were already taken, by M12, and the new file silently replaced a
committed producer and its committed CSV. Nothing objected.

The registration guards DID fire, but about the new file being unregistered,
which is a symptom of the collision rather than the collision itself. Had the
new producer inherited the old one's registration they would have stayed
silent while an older measurement vanished from the tree with every index
still reading correctly. What actually caught it was noticing the old entry
while reading an index by eye. That is not a mechanism. This is.

WHERE IT LOOKS. `scripts/verify_results_fresh.py` already carries the
authoritative producer-to-output map, because the freshness check has to know
which script regenerates which file. Reading the collision out of that map is
better than re-deriving it from the source, since a static scan of
`RESULTS_DIR / "x.csv"` cannot tell a write from a read: measured on this
tree, that scan reports seventeen "collisions", all of them scripts that
merely READ a table someone else produces.
"""
import re
from pathlib import Path

FRESH = Path(__file__).resolve().parents[1] / "scripts/verify_results_fresh.py"
BLOCK = re.compile(r"^(CHEAP|EXPENSIVE)\s*=\s*\{(.*?)^\}", re.M | re.S)
ENTRY = re.compile(r'["\'](run_[\w]+)["\']\s*:\s*\[(.*?)\]', re.S)
NAME = re.compile(r'["\']([\w.\-]+\.csv)["\']')


def _map():
    text = FRESH.read_text()
    owners = {}
    for _, body in BLOCK.findall(text):
        for producer, csvs in ENTRY.findall(body):
            for csv in NAME.findall(csvs):
                owners.setdefault(csv, []).append(producer)
    return owners


def test_no_result_csv_has_two_producers():
    owners = _map()
    clashes = {c: w for c, w in owners.items() if len(set(w)) > 1}
    assert not clashes, (
        "these result CSVs are claimed by more than one producer, so one "
        "silently overwrites the other:\n  "
        + "\n  ".join(f"{c}: {', '.join(sorted(set(w)))}" for c, w in sorted(clashes.items())))


def test_the_scan_finds_the_whole_map():
    """Should-fail control (19.53): a regex that stopped matching would make
    the test above pass by looking at nothing."""
    owners = _map()
    assert len(owners) >= 30, (
        f"parsed only {len(owners)} CSV entries out of the freshness map, so "
        f"the collision test above is not covering the tree")
    assert "laser_kernel.csv" in owners and "beta_self.csv" in owners, (
        "known entries are missing from the parse, so the regex has drifted "
        "from the file it reads")
