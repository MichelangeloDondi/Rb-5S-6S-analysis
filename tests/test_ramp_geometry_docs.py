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
                      "3 × 12 mm", "two-lens relay", "LANDSCAPE",
                      "+0.402", "−0.421"]),
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
# ...and the same claim survives WITHOUT the literal x64, as "the small waist
# makes the propto S_0^3 skew a detection" (found in PAPER1_SKELETON and
# methods/03 after the x64 sweep was declared complete). Flag an S_0^3 that is
# sold as a measurability gain unless the axial average is named nearby.
_NAIVE_GAIN = re.compile(
    r"S_?0?[\^_]?3.{0,80}(?:detect|measurab|measurement)|"
    r"(?:detect|measurab)\w*.{0,80}S_?0?[\^_]?3", re.I | re.S)
_AXIAL = re.compile(r"axial|sign|1\.12|cumulant|not by the", re.I)

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


@pytest.mark.parametrize("relpath", SKEW_DOCS, ids=SKEW_DOCS)
def test_no_naive_s0cubed_measurability_claim(relpath):
    """The x64 sweep keyed on the literal number and so missed the same claim
    written as "the small waist makes the propto S_0^3 skew a detection".

    Scoped to the SENTENCE, not to a proximity window: the first version of this
    check allowed +/-300 characters of context, which every one of these
    documents satisfies -- they all discuss the axial average somewhere. A naive
    sentence sitting directly beside its own retraction passed. The qualifier
    has to be in the claim's own sentence (or the next), where a reader lifting
    the sentence will carry it away too."""
    txt = " ".join((ROOT / relpath).read_text(encoding="utf-8").split())
    sents = re.split(r"(?<=[.;])\s+", txt)
    bad = []
    for i, sent in enumerate(sents):
        if not _NAIVE_GAIN.search(sent):
            continue
        scope = sent + " " + (sents[i + 1] if i + 1 < len(sents) else "")
        if not _AXIAL.search(scope):
            bad.append(sent.strip()[:130])
    assert not bad, (
        "S_0^3 sold as the small-waist measurability gain, with no mention of "
        "the axial average that changes its magnitude and sign in the same "
        "sentence:\n  " + "\n  ".join(bad))


# --------------------------------------------------------------------------
# The install decision (PLAN 8.3 #4): cathode orientation and the slit scan.
# Both tables are printed by run_ramp_geometry.py and quoted in PLAN; pin them
# so the recommendation cannot drift from the arithmetic behind it.
# --------------------------------------------------------------------------
# (L_par mm, M, Z_c mm, g1 at 60 um, g1 at 16 um)
ORIENTATION_ROWS = [
    (12.0, 1.9, 3.16, +0.555, -0.421),
    (12.0, 2.8, 2.14, +0.563, -0.367),
    (3.0, 1.9, 0.79, +0.566, +0.103),
    (3.0, 2.8, 0.54, +0.566, +0.367),
]


@pytest.mark.parametrize("l_par,mag,zc_mm,g1_l,g1_s", ORIENTATION_ROWS)
def test_orientation_table_matches_computation(l_par, mag, zc_mm, g1_l, g1_s):
    # g1 from the EXACT geometry, not from the table's rounded Z_c column: at
    # the tightest row the two differ by 0.004 mm, which is enough to move g1
    # past the tolerance (g1 is steepest exactly where portrait sits).
    z_c = l_par / (2 * mag) * 1e-3
    assert z_c * 1e3 == pytest.approx(zc_mm, abs=5e-3), "table Z_c mis-rounded"
    assert _g1(z_c / (np.pi * (60e-6) ** 2 / LAMBDA_M)) == \
        pytest.approx(g1_l, abs=2e-3)
    assert _g1(z_c / (np.pi * (16e-6) ** 2 / LAMBDA_M)) == \
        pytest.approx(g1_s, abs=2e-3)


def test_portrait_really_forfeits_the_flip():
    """The recommendation rests on this: portrait is below the crossover at
    BOTH ends of the magnification envelope, so it is not a weaker test but no
    test. If the envelope or the crossover moves, the advice must be
    re-argued."""
    z_r16 = np.pi * (16e-6) ** 2 / LAMBDA_M
    for mag in (1.9, 2.8):
        assert _g1(3.0 / (2 * mag) * 1e-3 / z_r16) > 0, "portrait would flip"
        assert _g1(12.0 / (2 * mag) * 1e-3 / z_r16) < 0, "landscape would not"


# (Z_c mm, g1 at 60 um, g1 at 16 um, collected fraction at 16 um)
SLIT_ROWS = [(0.5, +0.566, +0.402, 0.35), (1.0, +0.566, -0.071, 0.57),
             (2.0, +0.564, -0.354, 0.76), (3.0, +0.557, -0.416, 0.83)]


@pytest.mark.parametrize("zc_mm,g1_l,g1_s,frac", SLIT_ROWS)
def test_slit_scan_table_matches_computation(zc_mm, g1_l, g1_s, frac):
    z_r16 = np.pi * (16e-6) ** 2 / LAMBDA_M
    assert _g1(zc_mm * 1e-3 / (np.pi * (60e-6) ** 2 / LAMBDA_M)) == \
        pytest.approx(g1_l, abs=2e-3)
    assert _g1(zc_mm * 1e-3 / z_r16) == pytest.approx(g1_s, abs=2e-3)
    # two-photon rate per unit length ~ 1/(1+(z/z_R)^2), so the collected
    # fraction within +-Z_c is 2 arctan(Z_c/z_R)/pi -- NOT the I^2 form: the
    # transverse integral of I^2 already supplies one power of w(z)^-2.
    assert 2 * np.arctan(zc_mm * 1e-3 / z_r16) / np.pi == \
        pytest.approx(frac, abs=5e-3)


def test_slit_scan_actually_crosses_zero_within_its_range():
    """The scan is worth doing only if the predicted g1 changes SIGN inside the
    slit range PLAN sends the experimenter to (0.5-3 mm at 16 um)."""
    z_r16 = np.pi * (16e-6) ** 2 / LAMBDA_M
    assert _g1(0.5e-3 / z_r16) > 0 and _g1(3.0e-3 / z_r16) < 0
    crossing = brentq(lambda zc: _g1(zc / z_r16), 0.5e-3, 3.0e-3, xtol=1e-9)
    assert crossing * 1e3 == pytest.approx(0.90, abs=0.02)
