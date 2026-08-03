"""
CANONICAL: one registry of headline numbers, checked against BOTH the code that
produces them and the docs that quote them.

Why this file exists. Every headline result is cited across many documents
(README, BIG_PICTURE, PAPER1_SKELETON, the methods chapters, the paper drafts).
When a re-analysis moves a number -- as the AC-Stark bound moved 3.1 -> 0.63 MHz
and the beta bound 0.07-0.15 -> 0.2-0.4 -- every one of those citations has to
follow, and a missed one is a silent contradiction a referee will find. This
test makes that failure loud and mechanical instead of a manual grep.

The registry is the SINGLE place a headline number's value lives for the docs.
Each entry pulls its true value from the committed results CSV or a constant
(the SSOT), formats it the way the docs write it, and lists the documents that
MUST cite it. Three checks then run:

  (A) value <-> source:  the formatted token equals the freshly-read CSV/constant
      value, so the registry itself can never drift from the data.
  (B) docs cite the RIGHT value:  in every listed doc, EVERY citation of the
      quantity (found by a phrasing-tolerant regex) states the canonical number.
      A stale value left behind anywhere fails here -- this is the check that
      would have caught the 3.1 lingering in eight files.
  (C) docs cite it AT ALL:  each listed doc contains at least one citation.

Plus a targeted tripwire (D) that forbids the specific superseded values from
reappearing in the front-door docs except where explicitly marked superseded.

To change a headline number after a re-run: update its `value` source if needed,
run the producers, and this test tells you exactly which docs still disagree.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"


# --------------------------------------------------------------------------- #
# SSOT readers                                                                 #
# --------------------------------------------------------------------------- #
def _cell(fname, quantity, key=None, col="value"):
    for r in csv.DictReader(open(RESULTS / fname)):
        if r["quantity"] == quantity and (key is None or r["key"] == key):
            return r[col]
    raise KeyError(f"{quantity}/{key} not in {fname}")


def _beta_bound_range():
    """min/max of the model-independent per-peak 95% bound (the headline
    variant), rounded to 2 dp. Since the 2026-08-02 promotion of the
    four-point (70/90/110/130 C, dof=2) construction to the sole headline,
    the bound is roughly an order of magnitude tighter than the superseded
    three-point '0.2-0.4' headline, so 1 dp (which rounded the new range to
    '0.0-0.0') is no longer enough resolution to say anything -- 2 dp gives
    the '0.03-0.05' headline."""
    vals = [float(r["bound95_nscale"]) for r in csv.DictReader(open(RESULTS / "beta_self_probe.csv"))
            if r.get("headline") == "yes"]
    return f"{min(vals):.2f}", f"{max(vals):.2f}"


def _const(name):
    from rb5s6s import constants as K
    return getattr(K, name)


# --------------------------------------------------------------------------- #
# Document normalization: collapse the LaTeX-vs-Unicode phrasing so ONE regex   #
# per quantity works across README (Unicode) and the paper docs ($LaTeX$).      #
# --------------------------------------------------------------------------- #
def _normalize(text: str) -> str:
    text = re.sub(r"```.*?```", "", text, flags=re.S)          # drop fenced code
    text = re.sub(r"\\text\{([^{}]*)\}", r"\1", text)          # \text{ mW} -> " mW"
    text = re.sub(r"\\mathrm\{([^{}]*)\}", r"\1", text)
    repl = {r"\lesssim": "≲", r"\Delta\alpha": "Δα", r"\beta": "β",
            r"\Gamma": "Γ", r"\mu": "µ", r"\approx": "≈", r"\sim": "~",
            r"\,": " ", r"\ ": " ", "{=}": "=", "{": "", "}": ""}
    for a, b in repl.items():
        text = text.replace(a, b)
    text = text.replace("$", "")
    text = text.replace("–", "-").replace("—", "-")   # en/em dash -> hyphen
    return re.sub(r"[ \t]+", " ", text)


def _read(rel: str) -> str:
    return _normalize((ROOT / rel).read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# THE REGISTRY.  Each entry:                                                    #
#   name    : human label                                                       #
#   value   : the canonical token(s) as written in docs (a str or a set)        #
#   check   : callable asserting `value` still equals the SSOT (CSV/constant)    #
#   find    : regex (post-normalization) capturing the number at each citation  #
#   docs    : files that MUST cite it (checked present AND correct)             #
# The capture group of `find` is compared, per occurrence, against `value`.     #
# --------------------------------------------------------------------------- #
def _beta_range_token():
    lo, hi = _beta_bound_range()
    return f"{lo}-{hi}"


# Registry scope: the RESULTS that a re-analysis can move -- the ones whose stale
# copies cause the silent contradictions this file exists to catch. Fixed textbook
# inputs (Gamma_nat from the 6S lifetime, Orson's computed 1093 a.u.) are NOT here:
# they are pinned at their definition by the physics tests, not by a re-run, so
# guarding their prose would add brittleness for no regression protection.
#   mode "all": every citation of the quantity must state a canonical token
#               (used where all mentions should agree -- the stale-value catch).
#   mode "any": at least one citation states a token (used where the value
#               legitimately co-occurs with others, e.g. "50 µm ... 32 µm excluded").
CANONICAL = [
    dict(
        # since M23 the headline is the joint two-session bound; M4e's 0.63
        # stays in stark_sweep.csv as the width-only bracket, and prose that
        # cites it avoids the S0(225)< pattern so this guard stays sharp
        name="AC-Stark bound S0(225mW), 95% profile",
        value=lambda: f"{float(_cell('stark_joint.csv', 'S0_225mW_ub95')):.2f}",
        find=re.compile(r"S(?:₀|_?0)\s*\(225[^)]*\)[^0-9]*[<≲]\s*([0-9.]+)\s*MHz"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md", "private/manuscripts/PAPER1_SKELETON.md",
              "docs/methods/03_the_ac_stark_ramp.md", "docs/methods/07_what_we_found.md",
              "docs/THEORY_NOTE.md", "private/manuscripts/paper1/drafts/VI-CD_power_stark.md",
              "results/README.md", "docs/CLAIMS.md"],
    ),
    dict(
        name="AC-Stark predicted S0(225mW)",
        value=lambda: f"{float(_cell('stark_sweep.csv', 'S0_225mW_pred')):.2f}",
        find=re.compile(r"pred[a-z.]*\s+([0-9.]+)"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md"],
    ),
    dict(
        # four-point headline (70/90/110/130 C, dof=2) since 2026-08-02;
        # was the three-point (70-110C, dof=1) '0.2-0.4' range before
        name="beta_self model-independent bound range (four-point headline, 95%)",
        value=_beta_range_token,
        find=re.compile(r"([0-9]\.[0-9]{1,2}-[0-9]\.[0-9]{1,2}) MHz per 10"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md", "private/manuscripts/PAPER1_SKELETON.md",
              "docs/CLAIMS.md"],
    ),
    dict(
        # COMPUTED since 2026-08-01, previously the literal "271". The bracket
        # is the computed polarizability scaled by how far the bound sits
        # below its own prediction, so it moves whenever EITHER the bound or
        # the priors move -- and the literal had already drifted ~4% (the
        # formula gives 261 at the values that produced it). A hand-typed
        # number here defeats the point of the registry.
        name="Delta-alpha archival bracket (was ~1200, before that ~5800)",
        value=lambda: str(int(round(
            _const("DELTA_ALPHA_AU")
            * float(_cell("stark_joint.csv", "S0_225mW_ub95", "primary"))
            / float(_cell("stark_sweep.csv", "S0_225mW_pred"))))),
        find=re.compile(r"Δα\s*[<≲]\s*~?\s*([0-9]+)\s*a\.u"),
        mode="all",
        docs=["docs/BIG_PICTURE.md", "private/manuscripts/PAPER1_SKELETON.md"],
    ),
    dict(
        name="beam waist w0 prior",
        value=lambda: f"{int(_const('W0_PRIOR_M') * 1e6)}",
        find=re.compile(r"w.?0\s*[≈=]\s*([0-9]+)\s*µm|([0-9]+)\s*µm\s*\(prior|~([0-9]+) µm;"),
        mode="any",
        docs=["README.md", "docs/BIG_PICTURE.md"],
    ),
    dict(
        # The M16 recompute -- distinct from Orson's fixed 1093 (which stays
        # unguarded as a textbook input, see the scope note above): -1145 is a
        # re-runnable result of run_polarizability.py and its stale copies
        # would contradict the ledger.
        name="M16 Delta-alpha(993) recompute",
        value=lambda: f"{abs(float(_cell('polarizability.csv', 'delta_alpha_993', 'model'))):.0f}",
        find=re.compile(r"[−-](1[0-9]{3})\s*a\.u"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md", "docs/RESULTS.md"],
    ),
    dict(
        name="M16 first 5S-6S magic wavelength (1204 nm crossing)",
        value=lambda: f"{float(_cell('polarizability.csv', 'magic_5s6s', '1204nm')):.1f}",
        find=re.compile(r"(120[0-9]\.[0-9])\s*/"),
        mode="all",
        docs=["README.md", "docs/RESULTS.md"],
    ),
]


def _tokens(entry):
    v = entry["value"]()
    return v if isinstance(v, set) else {v}


@pytest.mark.parametrize("entry", CANONICAL, ids=lambda e: e["name"])
def test_canonical_registry_entries_are_well_formed(entry):
    """(A) The registry token is DERIVED live from the CSV or constant, so this
    checks only that the derivation produced something usable -- non-empty and
    not a stringified NaN. It is not the value<->source tie and was renamed
    because its old name (`..._value_matches_source`) claimed to be
    (red-team, 2026-07-29).

    The real protection is the next test: corrupting
    results/stark_sweep.csv fails test_docs_cite_canonical_value, verified by
    planting 0.633 -> 999.999. Keep both -- this one catches a producer that
    silently emits NaN, which the citation check would then happily match
    against equally-NaN prose."""
    toks = _tokens(entry)
    assert toks and all(t and not t.startswith("nan") for t in toks), entry["name"]


@pytest.mark.parametrize("entry", CANONICAL, ids=lambda e: e["name"])
def test_docs_cite_canonical_value(entry):
    # (B)+(C): every listed doc cites the quantity at least once, and EVERY
    # citation states a canonical token (a stale value anywhere fails).
    toks = _tokens(entry)
    for doc in entry["docs"]:
        # Manuscript drafts (PAPER1_SKELETON.md, private/manuscripts/paper1/) were unpublished
        # 2026-07-23 and are untracked: present in a working checkout, absent in
        # CI. Skip what is not there rather than fail on the CI clone -- the same
        # trap results/qc_metrics.csv sprang.
        if not (ROOT / doc).exists():
            continue
        text = _read(doc)
        hits = [next(g for g in m.groups() if g) for m in entry["find"].finditer(text)]
        assert hits, f"{entry['name']}: no citation found in {doc} (moved or rephrased?)"
        if entry["mode"] == "all":
            bad = [h for h in hits if h not in toks]
            assert not bad, (f"{entry['name']}: {doc} cites {bad}, expected one of "
                             f"{sorted(toks)} -- stale value not updated after a re-run")
        else:  # "any": the canonical token co-occurs with others; require presence
            assert toks & set(hits), (f"{entry['name']}: {doc} cites {sorted(set(hits))}, "
                                      f"none is the canonical {sorted(toks)}")


# --------------------------------------------------------------------------- #
# (D) targeted tripwire: the specific SUPERSEDED values must not reappear in    #
# the front-door docs except on a line that explicitly marks them superseded.   #
# This guards the exact regression this file was written for.                   #
# --------------------------------------------------------------------------- #
SUPERSEDED = [
    ("3.1", re.compile(r"S(?:₀|_?0).{0,40}3\.1\b"), "AC-Stark bound (was the Wald 3.1 MHz)"),
    ("5800", re.compile(r"5800"), "Delta-alpha bracket (was ~5800 a.u.)"),
    ("0.07-0.15", re.compile(r"0\.07-0\.15|0\.07.{0,6}0\.15"), "beta bound (was 0.07-0.15)"),
    ("0.2-0.4", re.compile(r"0\.2-0\.4|0\.2.{0,6}0\.4"),
     "beta bound (was the three-point/dof=1 headline 0.2-0.4, superseded "
     "2026-08-02 by the four-point/dof=2 0.03-0.05 headline)"),
]
_ALLOW_SUPERSEDED = re.compile(r"supersed|earlier|Wald|was |before |old ", re.I)


@pytest.mark.parametrize("val,pat,label", SUPERSEDED, ids=lambda x: x if isinstance(x, str) else "")
def test_no_superseded_value_in_front_door(val, pat, label):
    for doc in ("README.md", "docs/BIG_PICTURE.md"):
        for ln in _read(doc).splitlines():
            if pat.search(ln) and not _ALLOW_SUPERSEDED.search(ln):
                pytest.fail(f"{doc}: superseded {label} reappears: {ln.strip()[:90]}")


# --------------------------------------------------------------------------
# CLASS GUARD: a quoted bound must be supported by the data it summarises.
# --------------------------------------------------------------------------
# Three instances of one defect were found on 2026-07-23, all the same shape:
# a round number quoted in prose or a figure title that the underlying CSV does
# not support.
#   * ruler linearity  "<0.4%"  -- well-sampled windows reach 0.4486%
#   * C3a linewidth    "<=2%"   -- observed spread is 3-8% (the 2% is the
#                                  ramp-law PREDICTION, not the observation)
#   * fig8 title claimed a bound while drawing an error bar twice its size
# The lesson is that a PREDICTION and an OBSERVATION must not be quoted in the
# same breath, and that boundary-hugging numbers need pinning to their source.
def test_c3a_spread_is_quoted_as_observed_not_as_the_prediction():
    import csv
    from collections import defaultdict
    rows = list(csv.DictReader(open(ROOT / "results" / "power_sweep.csv")))
    by = defaultdict(list)
    for r in rows:
        by[r["peak"]].append(float(r["fwhm"]))
    spread = [100 * (max(v) / min(v) - 1) for v in by.values()]
    lo, hi = min(spread), max(spread)
    assert 2.5 < lo and hi > 5.0, (
        f"the observed C3a FWHM spread is now {lo:.1f}-{hi:.1f}%; the docs quote "
        f"3-8% as OBSERVED and <=2% as the ramp-law PREDICTION. If the data "
        f"moved, requote both -- and keep them distinguishable.")
    for rel, txt in (("private/manuscripts/PAPER1_SKELETON.md", None), ("docs/RESULTS.md", None)):
        if not (ROOT / rel).exists():
            continue   # unpublished manuscript draft; absent in CI
        body = (ROOT / rel).read_text(encoding="utf-8")
        if "C3a" not in body:
            continue
        seg = body[body.index("C3a"):body.index("C3a") + 400]
        assert "3–8%" in seg or "3-8%" in seg, (
            f"{rel} states C3a without the observed 3-8% spread; quoting only "
            f"the <=2% prediction reads as a measurement it is not")


def test_delta_alpha_within_five_percent_is_actually_within_five_percent():
    """THEORY_NOTE/PLAN/methods03 say the recompute agrees with Orson 'within
    5%'. It is 4.76% -- true, but close enough to the boundary that a small
    change to either number would silently falsify three documents."""
    import csv
    rows = {r["quantity"]: r for r in
            csv.DictReader(open(ROOT / "results" / "polarizability.csv"))}
    recomputed = abs(float(rows["delta_alpha_993"]["value"]))
    orson = 1093.0
    frac = abs(recomputed - orson) / orson
    assert frac < 0.05, (
        f"the recompute now differs from Orson by {frac:.1%}, so 'within 5%' "
        f"in THEORY_NOTE §5, PLAN §3 and methods/03 is false")
    assert frac > 0.03, "agreement tightened; requote it nearer the truth"


def test_readme_diagram_labels_outcomes_by_their_actual_type():
    """Third instance of the result-type mislabel class (after fig8's bound and
    C3a's prediction-as-observation): the README pipeline diagram summarised
    'skew and amplitude laws -> nulls'. Neither is a null. The ramp asymmetry
    is an UPPER BOUND (RESULTS C3c: below the SNR floor, consistent with zero
    -- and STYLE.md says bounds stay bounds), and amplitude ~ P^2 is a
    CONFIRMED prediction -- the README's own results table says so three
    sections later. A reader who trusts the diagram would mis-state two of the
    archive's four headline outcomes."""
    txt = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "→ nulls]" not in txt, (
        "the README diagram again folds distinct outcome types into 'nulls'; "
        "label each branch by what it delivers (bound / null / confirmed law)")
    for token in ("ramp asymmetry<br/>upper bound",
                  "amplitude laws<br/>P² and density<br/>checks"):
        assert token in txt, f"README diagram lost its honest label: {token!r}"
    # every mermaid node label must be QUOTED and each rendered line short:
    # GitHub clipped two 53-character labels ("...P-squared and linear-in-N
    # checks", "guards: model ladder · identifiability · coverage") while every
    # label <=33 chars rendered. Quote + <br/> is the fix; keep it enforced.
    import re as _re
    blk = txt[txt.index("```mermaid"):]
    blk = blk[:blk.index("```", 3)]
    for lbl in _re.findall(r'\[([^\]]*)\]', blk):
        assert lbl.startswith('"') and lbl.endswith('"'), (
            f"unquoted mermaid label {lbl!r} — quote it, special characters "
            f"otherwise break parsing")
        for seg in lbl.strip('"').split("<br/>"):
            assert len(seg) <= 34, (
                f"mermaid label line {seg!r} is {len(seg)} chars; GitHub clips "
                f"long labels — break it with <br/>")


def _tracked_prose():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md", "*.py"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        import pytest as _pt
        _pt.skip("not a git checkout")
    return [p for p in out.stdout.split("\n")
            if p and not p.startswith(("tests/", "docs/lit/"))]


def test_no_stale_04_linearity_bound_even_latex_wrapped():
    """The 0.40->0.45 sweep matched ASCII '<0.4%' and missed '$<0.4$%' in
    methods/05 and methods/07 -- inline math split the number from its percent
    sign. This scan is LaTeX-aware.

    Extended 2026-08-01: the seven-tooth comb refit tightened the map again,
    0.45% -> 0.3%, so 0.45% is now ALSO a stale value the same regression
    could reintroduce -- caught with the same pattern rather than a second
    copy of this test."""
    import re
    pat = re.compile(r"(?:<|≲|\\lesssim)\s*\$?0\.(?:40?|45)\$?\s*\\?%")
    hits = []
    for rel in _tracked_prose():
        for i, line in enumerate(
                (ROOT / rel).read_text(encoding="utf-8",
                                       errors="replace").split("\n"), 1):
            if pat.search(line):
                hits.append(f"{rel}:{i}: {line.strip()[:90]}")
    assert not hits, (
        "the sweep-linearity bound is 0.3% (seven-tooth refit, 2026-08-01); "
        "a stale <0.4% or <0.45% survives, LaTeX-wrapped or not:\n  "
        + "\n  ".join(hits))


def test_c3_suite_is_not_wrapped_as_confirmed():
    """methods/07's own body says 'We say consistent with, not confirms' for
    C3b -- yet four summary surfaces wrapped the whole C3 suite as 'confirmed
    predictions'. The suite is a null (width) + a consistency check (P^2) + a
    bound (skew); no wrapper may flatten that back into one word."""
    banned = ("ramp-law predictions confirmed",
              "suite of confirmed predictions",
              "recast as *confirmed prediction*",
              "power laws are confirmed",
              "confirmed ramp power laws")
    hits = []
    for rel in _tracked_prose():
        txt = (ROOT / rel).read_text(encoding="utf-8", errors="replace")
        for b in banned:
            if b in txt:
                hits.append(f"{rel}: {b!r}")
    assert not hits, ("C3 wrapped as wholesale confirmation again:\n  "
                      + "\n  ".join(hits))


def test_sigma_laser_panel_numbers_match_the_csvs():
    """fig5's title said 'flat (~1.7' while its own plotted free-fit means are
    1.04-1.25, and methods/07 quoted tied values 2.1/2.2/1.6 against a
    committed global_fit.csv reading 1.48/1.63/1.06 -- both stale against the
    data under them. Pin quoted <-> computed."""
    import csv
    import numpy as np
    gf = {r["key"]: float(r["value"])
          for r in csv.DictReader(open(ROOT / "results" / "global_fit.csv"))
          if r["quantity"] == "sigma_laser"}
    assert [round(gf[k], 1) for k in ("70C", "90C", "110C")] == [2.1, 2.2, 1.5], (
        "tied sigma_laser(T) moved; requote methods/07 and this test together")
    rows = list(csv.DictReader(open(ROOT / "results" / "linefit_conditions.csv")))
    means = []
    for T in (70, 90, 110):
        v = [(float(r["sigma_laser"]), float(r["sigma_laser_err"]))
             for r in rows if r["role"] == "t_sweep" and int(float(r["T"])) == T]
        s = np.array([x[0] for x in v]); w = 1 / np.array([x[1] for x in v]) ** 2
        means.append(float(np.sum(w * s) / np.sum(w)))
    assert 1.4 <= min(means) and max(means) <= 1.8, (
        "free per-condition sigma_laser left the 1.4-1.8 band; requote fig5's "
        "title and methods/07")
    fig_src = (ROOT / "scripts" / "make_figures.py").read_text(encoding="utf-8")
    assert "flat (~1.6," in fig_src, "fig5 title no longer quotes ~1.6"
    m07 = (ROOT / "docs" / "methods" / "07_what_we_found.md").read_text(encoding="utf-8")
    assert "2.1/2.2/1.5" in m07 and "$1.5$–$1.75$" in m07


# --------------------------------------------------------------------------
# The power ladder ran DESCENDING (audit, 2026-07-23). Guard the correction.
# --------------------------------------------------------------------------
# The recovered timestamps proved 225 -> 25 mW on all four peaks; the repo had
# documented 25 -> 225 since 2026-07-11. P2 failed with exactly 4 adjacent
# inversions per peak -- identical across peaks, the signature of a reversed
# sequence rather than noisy memory. Anything reasserting the ascending order
# as the ACQUISITION order is stale.
_ASCENDING = re.compile(
    r"25\s*(?:->|→|,)\s*75\s*(?:->|→|,)\s*125\s*(?:->|→|,)\s*175\s*(?:->|→|,)\s*225")
_DESC_OK = re.compile(r"descend|reversed|ascending power|condition ladder|"
                      r"NOT AN ACQUISITION|by ASCENDING POWER", re.I)


def test_power_ladder_documented_descending():
    import subprocess
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md", "*.py"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        pytest.skip("not a git checkout")
    bad = []
    for rel in [p for p in out.stdout.split("\n") if p]:
        if rel.startswith(("docs/lit/", "tests/")):
            continue
        # the pre-registration is a frozen pre-data document: its P2 row quotes
        # the prediction as written, which is the point of a pre-registration
        if rel == "docs/PREREGISTRATION_timestamps.md":
            continue
        lines = (ROOT / rel).read_text(encoding="utf-8", errors="replace").split("\n")
        for i, line in enumerate(lines, 1):
            if not _ASCENDING.search(line):
                continue
            # SAME LINE only. A +/-4-line window was too permissive: it was
            # satisfied by the very correction note explaining the reversal,
            # so a planted ascending order passed. The exemption must ride on
            # the claim itself.
            if not _DESC_OK.search(line):
                bad.append(f"{rel}:{i}: {line.strip()[:100]}")
    assert not bad, (
        "the power ladder is documented ascending as an ACQUISITION order; the "
        "recovered timestamps prove it ran 225 -> 25 mW (see "
        "docs/PREREGISTRATION_RESULTS.md):\n  " + "\n  ".join(bad))


def test_block_seq_is_labelled_not_a_time_order():
    """block_seq maps 25mW->1 ... 225mW->5, i.e. BACKWARDS in acquisition time.
    The values stay (stable join key, manifest md5s computed over them), so the
    docstring must say so or a reader will treat block_seq as a sequence."""
    src = (ROOT / "scripts" / "import_data.py").read_text(encoding="utf-8")
    assert "NOT AN ACQUISITION ORDER" in src, (
        "import_data.py no longer warns that block_seq is not a time order")
    for consumer in ("rb5s6s/ingest.py", "scripts/run_intrablock_trend.py"):
        body = (ROOT / consumer).read_text(encoding="utf-8")
        assert "block_seq" not in body, (
            f"{consumer} now reads block_seq; if it orders by it, that order is "
            f"reversed in time for the power session")


def test_advertised_test_counts_match_the_real_suite():
    """The counts in README and methods.md drifted to 803/779 while the suite had
    grown past a thousand, and a reader who runs the command sees the mismatch
    immediately. Collect the real numbers instead of trusting the prose."""
    import re
    import subprocess
    import sys
    def collected(args):
        out = subprocess.run(
            [sys.executable, "-m", "pytest", "--collect-only", "-q", *args],
            cwd=ROOT, capture_output=True, text=True).stdout
        m = re.search(r"(\d+)(?:/\d+)? tests collected", out)
        return int(m.group(1)) if m else None
    # There is no single "real" count, which is why the first version of this
    # guard went red in CI at 869 against a locally-collected 1094. Several
    # tests parametrise over inputs a given checkout may not have -- the private
    # manuscript drafts most of all -- so the number depends on what is present.
    # The documented figure is the FULL working checkout's, so only that
    # checkout can be held to it. CI, which has neither the private drafts nor
    # (in the public mirror) the archive-only tests, is not the reference.
    import pytest as _p
    if not (ROOT / "private" / "manuscripts").is_dir():
        _p.skip("not a full working checkout: collected count is not comparable")
    total = collected([])
    slow = collected(["-m", "slow"])
    if total is None or slow is None:
        _p.skip("could not collect")
    txt = (ROOT / "docs" / "methods.md").read_text() + (ROOT / "README.md").read_text()
    # 5% tolerance: the point is to catch DRIFT (803 documented against 1092
    # real, a 26% gap that had gone unnoticed), not to force a docs edit with
    # every test added.
    stale = [n for n in re.findall(r"\b(\d{3,5})[- ]test", txt)
             if abs(int(n) - total) / total > 0.05]
    assert not stale, (
        f"documented test counts {stale} are more than 5% from the real {total} "
        f"({slow} slow). Update docs/methods.md and README.md.")


def test_peak_labels_are_not_presented_as_measured_wavelengths():
    """The 993.4xxx peak labels are identifiers, not measurements: they come
    from a wavemeter that was never calibrated, and what actually fixes which
    line is which is the hyperfine assignment. They appear 44 times across the
    docs as keys, which is fine and stays fine -- but a future sentence calling
    one a measured or absolute wavelength would be a real error, and the
    caveat currently lives in exactly one paragraph. Guard both ends: forbid
    the phrasing, and require the paragraph."""
    import re
    banned = re.compile(
        r"(measured|absolute|calibrated)\s+(vacuum\s+)?wavelengths?\s+"
        r"(of\s+)?993\.4|993\.4\d{3}\s*nm[^.\n]{0,30}\b(measured|absolute)\s+wavelength",
        re.I)
    offenders = []
    for rel in ["README.md"] + [f"docs/{p.name}" for p in (ROOT / "docs").glob("*.md")] \
            + [f"docs/methods/{p.name}" for p in (ROOT / "docs" / "methods").glob("*.md")]:
        f = ROOT / rel
        if not f.is_file():
            continue
        for m in banned.finditer(f.read_text(encoding="utf-8")):
            offenders.append(f"{rel}: {m.group(0)[:70]!r}")
    assert not offenders, (
        "a peak label is presented as a measured wavelength; the wavemeter was "
        "never calibrated:\n  " + "\n  ".join(offenders))

    defining = (ROOT / "docs" / "methods" / "01_the_measurement.md").read_text(encoding="utf-8")
    assert "uncalibrated" in defining.lower(), (
        "docs/methods/01 defines the peak labels but no longer says the "
        "wavemeter was uncalibrated -- the caveat has been dropped")
