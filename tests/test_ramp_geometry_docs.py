"""Docs <-> computation sync for the diverging-beam ramp-geometry moments.

The g1 sign-flip discussion (PLAN section 8.3 #4, methods/03, the
run_ramp_geometry docstring, config's Z_c envelope note) quotes specific
moment coefficients and the crossover location. A stale-number incident
(2026-07-22: PLAN still quoted "g1 +0.40, 10-40% modified" for the archival
geometry, a leftover of the superseded 32 um waist that contradicted both
methods/03 and the script output) motivated pinning every quoted value to
the function that produces it. If lineshape.stark_ramp_axial_moments or the
config geometry changes, these tests name the documents that must move with
it.
"""

import re
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy.optimize import brentq

from rb5s6s.lineshape import stark_ramp_axial_moments

ROOT = Path(__file__).resolve().parents[1]

LAMBDA_M = 993.4e-9
ZC_PLACEHOLDER_M = 2.0e-3  # config.RAMP_COLLECTION_HALFLENGTH_MM_ENVELOPE[1]


def _z_ratio(w0_um: float) -> float:
    z_r = np.pi * (w0_um * 1e-6) ** 2 / LAMBDA_M
    return ZC_PLACEHOLDER_M / z_r


def _g1(z_ratio: float) -> float:
    return stark_ramp_axial_moments(1.0, z_ratio)["skew_standardized"]


def test_pure_triangle_benchmark():
    m = stark_ramp_axial_moments(1.0, 1e-6)
    assert m["mean"] == pytest.approx(-2.0 / 3.0, abs=2e-3)
    assert m["skew_standardized"] == pytest.approx(18**1.5 / 135, abs=2e-3)


def test_crossover_location_and_flip_condition():
    z_star = brentq(_g1, 0.8, 1.6, xtol=1e-4)
    assert z_star == pytest.approx(1.117, abs=0.01)
    # flip condition at the 16 um config, quoted as "~0.9 mm" in the docs
    z_r_16 = np.pi * (16e-6) ** 2 / LAMBDA_M
    assert z_star * z_r_16 * 1e3 == pytest.approx(0.90, abs=0.05)


# (doc file, tokens that must appear while the placeholder geometry stands)
DOC_TOKENS = [
    ("docs/PLAN.md", ["g1 +0.558", "Z_c/z_R ≈ 1.12", "r_PMT/M > 1.12 z_R",
                      "3 × 12 mm", "two-lens relay"]),
    ("docs/methods/03_the_ac_stark_ramp.md",
     ["$+0.558$", "$-0.354$", "$+0.564$", "1.12"]),
    ("scripts/run_ramp_geometry.py", ["1.12", "r_PMT/M > ~0.9 mm"]),
    ("rb5s6s/config.py", ["1.12", "L_par/(2M)", "R636-10", "3 x 12 mm"]),
    ("docs/THEORY_NOTE.md", ["$Z_c/z_R\\approx1.12$", "L_\\parallel/2M"]),
]


@pytest.mark.parametrize("relpath,tokens", DOC_TOKENS,
                         ids=[d for d, _ in DOC_TOKENS])
def test_docs_quote_current_coefficients(relpath, tokens):
    text = (ROOT / relpath).read_text(encoding="utf-8")
    missing = [t for t in tokens if t not in text]
    assert not missing, (
        f"{relpath} no longer quotes {missing}; if the geometry or the "
        f"moments code changed, update the document (and this registry) "
        f"together — see run_ramp_geometry.py."
    )


@pytest.mark.parametrize("w0_um,doc_g1", [(60.0, 0.564), (50.0, 0.558),
                                          (16.0, -0.354)])
def test_tabulated_g1_match_computation(w0_um, doc_g1):
    assert _g1(_z_ratio(w0_um)) == pytest.approx(doc_g1, abs=2e-3)


# Every document that mentions the small-waist skew gain must NOT quote the
# naive x64 (S_0^3) scaling: the axial average changes the third cumulant's
# magnitude and, past the crossover, its sign. PLAN itself retracts x64 as
# "wrong in sign", yet four documents still carried it (found 2026-07-22).
_X64 = re.compile(r"(×64|x64|64\\times|64\s*×)")
_RETRACTED = re.compile(r"naive|supersed|wrong in sign|not by the", re.I)

# Every document that carries the claim -- INCLUDING the generated ledger and
# the generator it comes from. The first version of this list watched only the
# hand-written docs, and the three files it omitted (docs/RESULTS.md, its
# generator, and FUTURE_TRANSITIONS) were exactly the three that still carried
# the superseded x64 a commit later.
SKEW_DOCS = ["docs/BIG_PICTURE.md", "docs/PAPER1_SKELETON.md",
             "docs/THEORY_NOTE.md", "docs/PLAN.md",
             "docs/methods/03_the_ac_stark_ramp.md",
             "docs/methods/08_assumptions_and_outlook.md",
             "docs/RESULTS.md", "scripts/make_results_ledger.py",
             "docs/FUTURE_TRANSITIONS_titsapph.md"]


@pytest.mark.parametrize("relpath", SKEW_DOCS, ids=SKEW_DOCS)
def test_no_unretracted_x64_skew_claim(relpath):
    bad = []
    for i, line in enumerate((ROOT / relpath).read_text(encoding="utf-8")
                             .split("\n"), 1):
        if _X64.search(line) and not _RETRACTED.search(line):
            bad.append(f"{relpath}:{i}: {line.strip()[:90]}")
    assert not bad, (
        "naive x64 small-waist skew scaling quoted without its retraction "
        "(the axial average changes magnitude AND sign — PLAN 8.3 #4):\n  "
        + "\n  ".join(bad)
    )


@pytest.mark.parametrize("relpath", SKEW_DOCS, ids=SKEW_DOCS)
def test_sign_flip_claims_carry_the_condition(relpath):
    """Any document asserting the g1 sign flip must say, somewhere, that it
    depends on the (unmeasured) collection geometry."""
    txt = (ROOT / relpath).read_text(encoding="utf-8")
    asserts_flip = re.search(r"sign[- ]flip|flips? sign|skewness sign", txt, re.I)
    if not asserts_flip:
        pytest.skip("document does not assert the flip")
    carries = re.search(
        r"conditional|contingent|unmeasured|1\.12|collection geometry|r_?PMT|"
        r"field of view", txt, re.I)
    assert carries, (
        f"{relpath} asserts the g1 sign flip but never states that it is "
        f"conditional on the unmeasured collection geometry (PLAN 8.3 #4)."
    )


def test_results_ledger_is_fresh():
    """docs/RESULTS.md is generated; nothing checked that it still matches its
    generator. It drifted: a wording fix landed in make_results_ledger.py while
    the committed ledger kept the old text, so the stale claim stayed visible.
    tests/test_results_fresh.py covers the CSVs, not this document."""
    import subprocess
    committed = (ROOT / "docs" / "RESULTS.md").read_text(encoding="utf-8")
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "make_results_ledger.py")],
        capture_output=True, text=True, cwd=str(ROOT))
    assert out.returncode == 0, f"generator failed:\n{out.stderr[-800:]}"
    regenerated = (ROOT / "docs" / "RESULTS.md").read_text(encoding="utf-8")
    if regenerated != committed:
        (ROOT / "docs" / "RESULTS.md").write_text(committed, encoding="utf-8")
        pytest.fail("docs/RESULTS.md is stale against "
                    "scripts/make_results_ledger.py -- re-run the generator "
                    "and commit the result.")


# The registry above is a PRESENCE check: it verifies the correct tokens appear
# somewhere in each file. That can never catch a WRONG instruction sitting a few
# lines away -- which is exactly what happened. run_ramp_geometry.py passed its
# token check while line 78 still printed "measure u, v, PMT diameter" to stdout
# on every run, one commit after the docstring above it was corrected. Z_c takes
# the cathode's HALF-extent ALONG the beam image; the R636-10 cathode is a
# 3 x 12 mm rectangle, so "diameter" is both the wrong shape and off by 2x.
_BAD_EXTENT = re.compile(
    r"(?:PMT|photocathode|cathode|active)\s+(?:active\s+)?diameter|"
    r"diameter\s+of\s+the\s+(?:PMT|photocathode|cathode)", re.I)


def test_no_document_asks_for_a_pmt_diameter():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md", "*.py"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    hits = []
    for rel in [p for p in out.stdout.split("\n") if p]:
        if rel == "tests/test_ramp_geometry_docs.py":
            continue
        try:
            txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(txt.split("\n"), 1):
            if _BAD_EXTENT.search(line):
                hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (
        "a document asks the reader to measure a PMT/cathode DIAMETER; Z_c = "
        "L_par/(2M) takes the active extent ALONG the beam image, and the "
        "R636-10 cathode is a 3 x 12 mm rectangle (rotation alone changes Z_c "
        "by x4). Following this literally is wrong by up to x8:\n  "
        + "\n  ".join(hits))


# The collection path's own facts. The two-lens relay prescription (PLAN 8.3 #4)
# was written specifying an "800 nm shortpass" in the collimated segment -- that
# is NIEDDU's detection (LITERATURE.md, correctly attributed there), not this
# apparatus, which uses a ~50 dB 795 nm PASSBAND stack (DATA.md). Describing our
# own stack as a shortpass would send someone to the bench with the wrong part,
# so the attribution has to hold: an unattributed short-pass is the error.
_SHORTPASS = re.compile(r"short-?pass", re.I)
_ATTRIB = re.compile(r"nieddu|their |lit/|2019|ONF|nanofib", re.I)


def test_shortpass_only_ever_attributed_to_others():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md", "*.py"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    hits = []
    for rel in [p for p in out.stdout.split("\n") if p]:
        if rel.startswith("docs/lit/") or rel == "tests/test_ramp_geometry_docs.py":
            continue
        try:
            lines = (ROOT / rel).read_text(encoding="utf-8",
                                           errors="replace").split("\n")
        except OSError:
            continue
        for i, line in enumerate(lines):
            if not _SHORTPASS.search(line):
                continue
            # attribution may sit on the wrapped line before or after
            ctx = " ".join(lines[max(0, i - 1):i + 2])
            if not _ATTRIB.search(ctx):
                hits.append(f"{rel}:{i + 1}: {line.strip()[:90]}")
    assert not hits, (
        "a short-pass is described without attribution; THIS apparatus detects "
        "through a ~50 dB 795 nm PASSBAND stack (DATA.md) -- the 800 nm "
        "short-pass belongs to Nieddu's ONF setup:\n  " + "\n  ".join(hits))
