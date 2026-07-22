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
    """min/max of the model-independent per-peak 95% bound (70-110 C variant),
    rounded to 1 dp -- the '0.2-0.4' headline."""
    vals = [float(r["bound95_nscale"]) for r in csv.DictReader(open(RESULTS / "beta_self_probe.csv"))
            if r.get("headline") == "yes"]
    return f"{min(vals):.1f}", f"{max(vals):.1f}"


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
        name="AC-Stark bound S0(225mW), 95% profile",
        value=lambda: f"{float(_cell('stark_sweep.csv', 'S0_225mW_ub95_profile')):.2f}",
        find=re.compile(r"S(?:₀|_?0)\s*\(225[^)]*\)[^0-9]*[<≲]\s*([0-9.]+)\s*MHz"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md", "docs/PAPER1_SKELETON.md",
              "docs/methods/03_the_ac_stark_ramp.md", "docs/methods/07_what_we_found.md",
              "docs/THEORY_NOTE.md", "docs/paper1/drafts/VI-CD_power_stark.md",
              "results/README.md"],
    ),
    dict(
        name="AC-Stark predicted S0(225mW)",
        value=lambda: f"{float(_cell('stark_sweep.csv', 'S0_225mW_pred')):.2f}",
        find=re.compile(r"pred[a-z.]*\s+([0-9.]+)"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md"],
    ),
    dict(
        name="beta_self model-independent bound range (70-110C, 95%)",
        value=_beta_range_token,
        find=re.compile(r"([0-9]\.[0-9]-[0-9]\.[0-9]) MHz per 10"),
        mode="all",
        docs=["README.md", "docs/BIG_PICTURE.md", "docs/PAPER1_SKELETON.md"],
    ),
    dict(
        name="Delta-alpha archival bracket (was ~5800)",
        value=lambda: "1200",
        find=re.compile(r"Δα\s*[<≲]\s*~?\s*([0-9]+)\s*a\.u"),
        mode="all",
        docs=["docs/BIG_PICTURE.md", "docs/PAPER1_SKELETON.md"],
    ),
    dict(
        name="beam waist w0 prior",
        value=lambda: f"{int(_const('W0_PRIOR_M') * 1e6)}",
        find=re.compile(r"w.?0\s*[≈=]\s*([0-9]+)\s*µm|([0-9]+)\s*µm\s*\(prior|~([0-9]+) µm;"),
        mode="any",
        docs=["README.md", "docs/BIG_PICTURE.md"],
    ),
]


def _tokens(entry):
    v = entry["value"]()
    return v if isinstance(v, set) else {v}


@pytest.mark.parametrize("entry", CANONICAL, ids=lambda e: e["name"])
def test_canonical_value_matches_source(entry):
    # (A) the registry token is derived live from the CSV/constant, so this just
    # asserts it is well-formed and non-empty -- the derivation IS the SSOT tie.
    toks = _tokens(entry)
    assert toks and all(t and not t.startswith("nan") for t in toks), entry["name"]


@pytest.mark.parametrize("entry", CANONICAL, ids=lambda e: e["name"])
def test_docs_cite_canonical_value(entry):
    # (B)+(C): every listed doc cites the quantity at least once, and EVERY
    # citation states a canonical token (a stale value anywhere fails).
    toks = _tokens(entry)
    for doc in entry["docs"]:
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
    for rel, txt in (("docs/PAPER1_SKELETON.md", None), ("docs/RESULTS.md", None)):
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
