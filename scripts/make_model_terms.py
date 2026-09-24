#!/usr/bin/env python3
"""
The model-terms registry, rendered: results/model_terms.csv and docs/methods/model_terms.md
=============================================================================================

Both are GENERATED from `rb5s6s/model_registry.py`, never hand-edited: the module is the single
source, this script is its two renderings, and `tests/test_model_registry.py` asserts both stay
byte-identical to what the module would produce right now.

Run:

    python scripts/make_model_terms.py

Then (registry convention, this producer runs before it):

    python scripts/annotate_results_status.py
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import model_registry as MR  # noqa: E402

DOC_PATH = ROOT / "docs" / "methods" / "model_terms.md"

#: the doc page's own column order: the six statuses and the three impl sites, never the whole
#: sixteen-column CSV, which is the file to read for physics/param_keys/anchors/evidence.
_DOC_COLUMNS = (
    ("term_id", "term"),
    ("status_fitter_2025", "fitter 2025"),
    ("status_fitter_campaign", "fitter campaign"),
    ("status_twin_2025", "twin 2025"),
    ("status_twin_campaign", "twin campaign"),
    ("status_mc_2025", "mc 2025"),
    ("status_mc_campaign", "mc campaign"),
    ("impl_fitter", "impl (fitter)"),
    ("impl_twin", "impl (twin)"),
    ("impl_mc", "impl (mc)"),
)


def csv_text() -> str:
    """`results/model_terms.csv`'s exact bytes, as a string, so the freshness test can compare
    without touching the filesystem."""
    import io
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=MR.CSV_COLUMNS)
    writer.writeheader()
    writer.writerows(MR.to_csv_rows())
    return buf.getvalue()


def _escape(cell: str) -> str:
    """A markdown table cell may not carry a bare pipe or a line break."""
    return str(cell).replace("|", "\\|").replace("\n", " ")


def doc_text() -> str:
    """`docs/methods/model_terms.md`'s exact text, as a string."""
    digest = MR.registry_digest()
    lines = [
        "# The model-terms registry",
        "",
        "Generated from `rb5s6s/model_registry.py` by `scripts/make_model_terms.py`. Do not edit "
        "this page by hand: `tests/test_model_registry.py` refuses a committed copy that "
        "disagrees with the module.",
        "",
        "One row per physical term of the forward model, naming which of the three computation "
        "paths carries it: the fitter (`rb5s6s/fullmodel.py`'s `full_profile` and the ultra-joint `Cell` "
        "of `scripts/run_ultra_joint.py`, `rb5s6s/beta.py`'s `fit_beta_self`, "  # ladder-exempt: a prose mention
        "`rb5s6s/linefit.py`'s `fit_condition`), the joint twin of record "
        "(`rb5s6s/volume_line.py` through `rb5s6s/twin_volume.py`), and the kernel Monte Carlo "
        "(`scripts/run_kernel_mc.py`), at the archive's own 2025 conditions and at "
        "the proposed campaign's. A status of `carried` names its own code site in the `impl` "
        "column beside it. `owed`, `neglected`, `absorbed` and `n/a` are read in full in "
        "`rb5s6s/model_registry.py`'s own module docstring, and the six-status detail, the "
        "physics, the parameter names, the thesis anchor and the evidence for every row live in "
        f"`results/model_terms.csv`, not repeated here. Registry digest (the joint twin's own "
        f"2025 carried set): `{digest}`.",
        "",
        "| " + " | ".join(h for _, h in _DOC_COLUMNS) + " |",
        "|" + "|".join(["---"] * len(_DOC_COLUMNS)) + "|",
    ]
    for row in MR.REGISTRY:
        cells = [_escape(getattr(row, attr)) for attr, _ in _DOC_COLUMNS]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    out = Path(C.RESULTS_DIR) / "model_terms.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(csv_text())
    print(f"  wrote {out} ({len(MR.REGISTRY)} terms)")

    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(doc_text())
    print(f"  wrote {DOC_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
