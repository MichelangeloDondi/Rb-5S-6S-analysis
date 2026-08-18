"""Every quantity dossier is linked from its index, and every link has a page.

The wiki has this guard for the same reason and the reasoning transfers
unchanged: an index is written when a directory is tidied and not when a file
is added, so it drifts one page at a time and nothing says so.
`test_docs_links` checks that a link RESOLVES, which is the other direction.

The cluster carries one rule the wiki does not, and it is the one worth a
guard of its own. A dossier states a bound or a value, and a bound stated
without the construction that produced it is the defect this whole cluster was
built to prevent, five bounds in this project having shared one name. So the
results table of every dossier is required to carry a construction column and
a status column, checked here rather than trusted to review.

Counts are printed on every run rather than only on failure, because a guard
that finds its subject by pattern has to show what it found.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUANT = ROOT / "docs" / "quantities"
INDEX = QUANT / "README.md"
# campaign.md is a synthesis page rather than a dossier, so the per-dossier
# content rules below do not apply to it.
NOT_A_DOSSIER = {"README.md", "campaign.md"}


def _pages():
    return {p.name for p in QUANT.glob("*.md") if p.name != "README.md"}


def _dossiers():
    return {p for p in QUANT.glob("*.md") if p.name not in NOT_A_DOSSIER}


def _linked(text):
    return set(re.findall(r"\]\((?!\.\./|https?:)([A-Za-z0-9_-]+\.md)\)", text))


def test_every_dossier_is_linked_from_the_index(capsys):
    pages = _pages()
    linked = _linked(INDEX.read_text(encoding="utf-8"))
    with capsys.disabled():
        print(f"\n  quantities index: {len(pages)} pages on disk, "
              f"{len(linked)} linked from README.md")
    missing = sorted(pages - linked)
    assert not missing, (
        "these pages exist under docs/quantities/ and nothing in its "
        "README.md links to them, so a reader arriving at the index cannot "
        "find them:\n  " + "\n  ".join(missing))


def test_every_index_entry_has_a_page():
    dangling = sorted(_linked(INDEX.read_text(encoding="utf-8")) - _pages())
    assert not dangling, (
        "docs/quantities/README.md links to these pages and they do not "
        "exist:\n  " + "\n  ".join(dangling))


def test_every_dossier_states_its_question_and_routes_to_the_glossary():
    """The four-field header and a glossary link, on every dossier.

    `test_docs_structure` requires these only above its word threshold. A
    dossier is defined by opening with the question it answers, whatever its
    length, so the cluster asks for them unconditionally.
    """
    bad = []
    for p in sorted(_dossiers()):
        head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:60])
        for field in ("**The question.**", "**Takes.**", "**Gives.**",
                      "**Skip if.**"):
            if field not in head:
                bad.append(f"{p.name}: header is missing {field}")
        if "GLOSSARY.md" not in p.read_text(encoding="utf-8"):
            bad.append(f"{p.name}: no link to the glossary")
    assert not bad, "\n  ".join([""] + bad)


def test_every_dossier_names_constructions_and_statuses(capsys):
    """A dossier's results table carries a construction and a status column.

    This is the cluster's reason for existing, mechanised. On 2026-08-17 three
    separate errors in one day had the identical shape, a number checked
    against a different construction wearing the same name, and `S0` alone
    spans five constructions differing by up to a factor of two. A results
    table without a construction column reintroduces exactly that.
    """
    bad = []
    for p in sorted(_dossiers()):
        text = p.read_text(encoding="utf-8")
        if "| construction |" not in text:
            bad.append(f"{p.name}: no results table with a construction column")
        if "| status |" not in text:
            bad.append(f"{p.name}: no results table with a status column")
    with capsys.disabled():
        print(f"  quantities: {len(_dossiers())} dossiers checked for "
              f"construction and status columns")
    assert not bad, "\n  ".join([""] + bad)


def test_every_dossier_defines_the_three_levels():
    """The level names are fixed, and 'tier' is not one of them.

    The three levels are an improved bound, a measurement, and a competitive
    measurement, and 'competitive' is defined against that dossier's own
    literature benchmark rather than against this experiment's current state.
    Fixed names are what makes the levels comparable across dossiers.
    """
    bad = []
    for p in sorted(_dossiers()):
        text = p.read_text(encoding="utf-8").lower()
        for level in ("an improved bound", "a measurement",
                      "a competitive measurement"):
            if f"### {level}" not in text:
                bad.append(f"{p.name}: no section headed {level!r}")
        if re.search(r"\btiers?\b", text):
            bad.append(f"{p.name}: uses 'tier' for a measurement level")
    assert not bad, "\n  ".join([""] + bad)


# ---------------------------------------------------------------------------
# The numbers on a dossier come from a committed cell, checked here
# ---------------------------------------------------------------------------

def _cell(csv_name, quantity, key=None, col="value"):
    """One cell of a committed results CSV, by quantity and optional key."""
    import csv as _csv
    with open(ROOT / "results" / csv_name, encoding="utf-8") as fh:
        for row in _csv.DictReader(fh):
            first = next(iter(row.values()))
            if first != quantity:
                continue
            if key is not None and list(row.values())[1] != key:
                continue
            return float(row[col] if col in row else list(row.values())[2])
    raise AssertionError(f"{csv_name}: no row for {quantity!r}/{key!r}")


# (dossier, the number as the page writes it, how to derive it)
QUOTED = [
    ("ac-stark-light-shift.md", "0.944",
     lambda: _cell("full_dataset_fit.csv", "kappa_ub95", "primary")),
    ("ac-stark-light-shift.md", "1.147",
     lambda: _cell("stark_joint.csv", "kappa_ub95", "primary")),
    ("ac-stark-light-shift.md", "0.258",
     lambda: _cell("stark_joint.csv", "S0_225mW_ub95", "primary")),
    ("ac-stark-light-shift.md", "1.066",
     lambda: _cell("stark_joint.csv", "kappa_ub95_wing", "robustness")),
    ("ac-stark-light-shift.md", "1.626",
     lambda: _cell("stark_joint.csv", "kappa_ub95_drop4192", "robustness")),
    ("ac-stark-light-shift.md", "1.545",
     lambda: _cell("stark_joint.csv", "kappa_pred", "prediction")),
    ("ac-stark-light-shift.md", "0.348",
     lambda: _cell("stark_joint.csv", "S0_225mW_pred", "prediction")),
    ("self-broadening.md", "0.0249",
     lambda: _cell("beta_self_probe.csv", "pooled_slope", col="bound95")),
]


def test_every_quoted_number_matches_its_committed_cell(capsys):
    """A dossier quotes a bound, so the bound is checked against its source.

    `test_docs_canonical` does this for the headline numbers through a regex
    registry keyed on phrasing. These pages quote one number per CONSTRUCTION,
    several of which share a phrase and differ only by which fit produced them,
    so they are checked by value against the named cell instead. Rewriting a
    dossier's physics to satisfy a registry regex would be the wrong direction.
    """
    bad = []
    for page, written, derive in QUOTED:
        text = (QUANT / page).read_text(encoding="utf-8")
        got = derive()
        # Compare at the precision the page actually writes. A dossier quotes
        # three or four significant figures and the cell carries fifteen, so a
        # fixed relative tolerance either rejects correct rounding or accepts
        # a wrong digit, depending on the magnitude.
        places = len(written.split(".")[1]) if "." in written else 0
        if written != f"{got:.{places}f}":
            bad.append(f"{page}: writes {written}, the CSV cell rounds to "
                       f"{got:.{places}f} (raw {got})")
        elif written not in text:
            bad.append(f"{page}: no longer states {written}, which its source "
                       f"cell still holds")
    with capsys.disabled():
        print(f"  quantities: {len(QUOTED)} quoted numbers re-derived from "
              f"their committed cells")
    assert not bad, "\n  ".join([""] + bad)
