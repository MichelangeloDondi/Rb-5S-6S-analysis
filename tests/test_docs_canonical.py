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

Plus a targeted tripwire (D) that forbids the specific replaced values from
reappearing in the front-door docs except where explicitly marked replaced.

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
def _vdw_ratio():
    from rb5s6s import vanderwaals as _v
    r = _v.beta_self_anchored()
    return r["dc6_ratio"]


def _vdw_beta7():
    from rb5s6s import vanderwaals as _v
    r = _v.beta_self_anchored()
    return r["beta7_predicted_khz"]


def _hyp_c1204():
    from rb5s6s import hyperpolarizability as _h
    return _h.quartic_coefficients()["1203.9"]


def _hyp_v1_khz():
    from rb5s6s import hyperpolarizability as _h
    return abs(_h.vector_coefficient(1203.886285673291)) / 1e3


def _coop(label, col="value"):
    """A row of results/cooperative_channel.csv, which is keyed on `label`
    inside a `block` rather than on quantity and key."""
    for r in csv.DictReader(open(RESULTS / "cooperative_channel.csv")):
        if r["label"] == label:
            return r[col]
    raise KeyError(label)


def _coop_leg_gain():
    """The RATE factor that carrying both 5P fine-structure legs buys over
    carrying 5P1/2 alone. Recomputed here from the committed line lists, so
    the docstrings that quote it are tied to the arithmetic and not to each
    other."""
    from rb5s6s import cooperative as _c
    from rb5s6s.polarizability import LINES_5S, E_6S_CM
    e1, d5 = LINES_5S[0][0], LINES_5S[0][1]
    one_leg = d5 * d5 / (2 * e1 - E_6S_CM)
    return (_c._sum_ratio_au_per_cm() / one_leg) ** 2


def _cell(fname, quantity, key=None, col="value"):
    for r in csv.DictReader(open(RESULTS / fname)):
        if r["quantity"] == quantity and (key is None or r["key"] == key):
            return r[col]
    raise KeyError(f"{quantity}/{key} not in {fname}")


def _cell_first(fname, col):
    """First data row of a WIDE one-row CSV (`ruler_campaign.csv` is one row of
    named columns, not the quantity/key/value long form `_cell` reads)."""
    for r in csv.DictReader(open(RESULTS / fname)):
        return r[col]
    raise KeyError(f"{fname} has no data rows")


def _beta_bound_range():
    """min/max of the model-independent per-peak 95% bound (the headline
    variant), rounded to 2 dp. Since the 2026-08-02 promotion of the
    four-point (70/90/110/130 C, dof=2) construction to the sole headline,
    the bound is roughly an order of magnitude tighter than the replaced
    three-point '0.2-0.4' headline, so 1 dp (which rounded the new range to
    '0.0-0.0') is no longer enough resolution to say anything -- 2 dp gives
    the '0.03-0.05' headline."""
    vals = [float(r["bound95_nscale"]) for r in csv.DictReader(open(RESULTS / "beta_self_probe.csv"))
            if r.get("headline") == "yes"]
    return f"{min(vals):.2f}", f"{max(vals):.2f}"


def _source_headroom(rung: str) -> float:
    """The source-class headroom row for one rung. Its key carries the rung and
    then the class name, so it is matched on the rung prefix rather than on the
    whole key: the class wording is prose that may be rewritten, and pinning a
    number to a sentence would make the pin the thing that breaks."""
    for r in csv.DictReader(open(RESULTS / "projections.csv")):
        if r["quantity"] == "proj_source_headroom" and r["key"].startswith(rung):
            return float(r["value"])
    raise KeyError(f"no proj_source_headroom row for {rung}")


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


def _rate_laser_tokens():
    """The campaign sweep rate as the docs write it. Three roundings of ONE
    value are canonical because three are in use and each is legitimate at its
    own precision: 5 dp with a parenthesised error (the ledger's own format),
    6 dp (the methods chapters and the literature table), and 7 dp (methods/05,
    which writes the replaced value and the current one side by side to the
    digit that separates them). Every rounding is derived from the CSV, so a
    stale value fails all three."""
    r = float(_cell_first("ruler_campaign.csv", "rate_laser"))
    return {f"{r:.5f}", f"{r:.6f}", f"{r:.7f}"}


def _rate_transition_token():
    return f"{2 * float(_cell_first('ruler_campaign.csv', 'rate_laser')):.6f}"


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
        # "below" joined `<` and `≲` on 2026-08-09. The math-render sweep
        # rewrote `$S_0(225\ \text{mW})<0.26$` as `... $ below 0.26`, because
        # a `<` inside a math span is entity-escaped before MathJax sees it
        # and the whole span renders as raw source. The relation had moved out
        # of the maths into the prose in README and methods/03, where this
        # regex could no longer see it, and methods/03 failed the presence
        # check with the correct value on the page. Same value pinned, one
        # more spelling of the relation. Note for the width-only 0.63: the
        # prose that cites it must now avoid "S0(225 mW) below" as well as
        # "S0(225 mW) <", or it will be read as a citation of this bound.
        find=re.compile(r"S(?:₀|_?0)\s*\(225[^)]*\)[^0-9]*(?:[<≲]|below)\s*"
                        r"([0-9.]+)\s*MHz"),
        mode="all",
        # docs/PLAN.md joined 2026-08-05: it quotes the bound twice in its
        # referee-risk section and was in no docs= list at all, which is the
        # gap that let its permutation p go stale at the retired 0.11.
        docs=["README.md", "docs/big_picture/04_what-2025-delivered.md", "private/manuscripts/PAPER1_SKELETON.md",
              "docs/methods/03_the_ac_stark_ramp.md", "docs/methods/07_what_we_found.md",
              "docs/THEORY_NOTE.md", "private/manuscripts/paper1/drafts/VI-CD_power_stark.md",
              "results/README.md", "docs/CLAIMS.md", "docs/plan/01_aim-and-failure-modes.md",
              # 08 joined 2026-08-17. It argues what the pooled construction
              # assumes, so it is the one chapter that must never drift from the
              # bound that construction produces.
              "docs/big_picture/08_when-a-joint-fit-is-legitimate.md"],
    ),
    dict(
        # The find regex must look like an S0 VALUE, not merely like the word
        # "predicted" followed by a number. The old `pred[a-z.]*\s+([0-9.]+)`
        # matched README's fig13 caption ("against the predicted 7/5 = 1.40"),
        # captured the "7" of the degeneracy ratio and failed the entry on a
        # sentence that has nothing to do with the light shift. Requiring the
        # capture to be a decimal followed by "MHz", within a short window of
        # the word, keeps every real citation ("the predicted 0.35 MHz") and
        # drops the parameter-free area ratios, which carry no unit.
        name="AC-Stark predicted S0(225mW)",
        value=lambda: f"{float(_cell('stark_sweep.csv', 'S0_225mW_pred')):.2f}",
        find=re.compile(r"pred[a-z.]*[^0-9]{0,24}?([0-9]+\.[0-9]+)\s*MHz"),
        mode="all",
        docs=["README.md", "docs/big_picture/04_what-2025-delivered.md"],
    ),
    dict(
        # four-point headline (70/90/110/130 C, dof=2) since 2026-08-02;
        # was the three-point (70-110C, dof=1) '0.2-0.4' range before
        name="beta_self model-independent bound range (four-point headline, 95%)",
        value=_beta_range_token,
        find=re.compile(r"([0-9]\.[0-9]{1,2}-[0-9]\.[0-9]{1,2})\s+MHz\s+per\s+10"),
        mode="all",
        docs=["README.md", "docs/big_picture/04_what-2025-delivered.md", "private/manuscripts/PAPER1_SKELETON.md",
              "docs/CLAIMS.md", "docs/plan/05_width-collision-amplitude.md"],
    ),
    dict(
        # COMPUTED since 2026-08-01, previously the literal "271". The bracket
        # is the computed polarizability scaled by how far the bound sits
        # below its own prediction, so it moves whenever EITHER the bound or
        # the priors move -- and the literal had already drifted ~4% (the
        # formula gives 261 at the values that produced it). A hand-typed
        # number here defeats the point of the registry.
        name="Delta-alpha record bracket (was ~1200, before that ~5800)",
        value=lambda: str(int(round(
            _const("DELTA_ALPHA_AU")
            * float(_cell("stark_joint.csv", "S0_225mW_ub95", "primary"))
            / float(_cell("stark_sweep.csv", "S0_225mW_pred"))))),
        find=re.compile(r"Δα\s*[<≲]\s*~?\s*([0-9]+)\s*a\.u"),
        mode="all",
        docs=["docs/big_picture/04_what-2025-delivered.md", "private/manuscripts/PAPER1_SKELETON.md"],
    ),
    dict(
        # ADDED 2026-08-10, when the band moved from 60-70 to 62-68 um on the
        # experimenter's instruction and turned up hand-typed in five documents plus a
        # SECOND, different, two-generations-stale literal band inside
        # run_global_fit.py. Every reader of constants.W0_BAND_M moved by
        # itself. Nothing that had typed the numbers did, which is what this
        # entry now prevents.
        name="beam waist band, low edge",
        value=lambda: f"{int(_const('W0_BAND_M')[0] * 1e6)}",
        # one capture per entry, because the registry compares a single number
        # and the four documents write the band three different ways: an
        # en-dash, a hyphen, and the word "to".
        find=re.compile(r"([0-9]{2})\s*(?:to|[-–])\s*[0-9]{2}\s*µm\s*band"
                        r"|band\s+([0-9]{2})\s*(?:to|[-–])\s*[0-9]{2}\s*µm"
                        r"|working band is\s+([0-9]{2})[-–][0-9]{2}\s*µm"),
        mode="all",
        docs=["docs/big_picture/04_what-2025-delivered.md", "docs/plan/03_optics-protocol.md",
              "docs/methods/02_the_lineshape.md",
              "docs/methods/08_assumptions_and_outlook.md"],
    ),
    dict(
        name="beam waist band, high edge",
        value=lambda: f"{int(_const('W0_BAND_M')[1] * 1e6)}",
        find=re.compile(r"[0-9]{2}\s*(?:to|[-–])\s*([0-9]{2})\s*µm\s*band"
                        r"|band\s+[0-9]{2}\s*(?:to|[-–])\s*([0-9]{2})\s*µm"
                        r"|working band is\s+[0-9]{2}[-–]([0-9]{2})\s*µm"),
        mode="all",
        docs=["docs/big_picture/04_what-2025-delivered.md", "docs/plan/03_optics-protocol.md",
              "docs/methods/02_the_lineshape.md",
              "docs/methods/08_assumptions_and_outlook.md"],
    ),
    dict(
        name="beam waist w0",
        value=lambda: f"{int(_const('W0_MEASURED_M') * 1e6)}",
        find=re.compile(r"w.?0\s*[≈=]\s*([0-9]+)\s*µm|([0-9]+)\s*µm\s*(?:\((?:prior|measured)|,\s*measured)|~([0-9]+)\s+µm;"),
        mode="any",
        # docs/PLAN.md joined 2026-08-05 through the "(prior" alternate: its
        # configuration table writes the waist as "w₀" with a subscript zero,
        # which the first alternate cannot see.
        docs=["README.md", "docs/big_picture/04_what-2025-delivered.md", "docs/plan/03_optics-protocol.md"],
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
        docs=["README.md", "docs/big_picture/03_goals-and-prior-art.md",
              "docs/big_picture/04_what-2025-delivered.md", "docs/RESULTS.md"],
    ),
    dict(
        # The frequency axis every MHz-denominated number in the repository is
        # denominated in. It is hand-typed in eight files today, and the ruler
        # re-validation of docs/notes/ruler_validity_and_trim_prereg.md is
        # expected to move it, so the citations are mechanized BEFORE the move
        # rather than chased afterwards.
        # The regex demands 5 or more decimals immediately in front of MHz/ms,
        # which is what separates a citation of this number from the rounded
        # "~0.043 MHz/ms" and "0.0426" that appear legitimately elsewhere.
        name="M2 campaign sweep rate, laser axis",
        value=_rate_laser_tokens,
        find=re.compile(r"([0-9]\.[0-9]{4,7})\s*(?:\([0-9]+\)|±\s*[0-9.]+)?\s*MHz/ms"),
        mode="all",
        docs=["docs/DATA.md", "docs/RESULTS.md", "docs/LITERATURE.md",
              "docs/methods/05_the_frequency_ruler.md",
              "docs/methods/07_what_we_found.md",
              "scripts/run_laser_history.py"],
    ),
    dict(
        # Twice the laser-axis rate, written out once so that the factor-2
        # bookkeeping cannot drift away from its own source.
        name="M2 campaign sweep rate, transition axis",
        value=_rate_transition_token,
        find=re.compile(r"transition\s+axis\s+([0-9]\.[0-9]{4,7})"),
        mode="all",
        docs=["docs/DATA.md"],
    ),
    dict(
        # The three projections the decision-maker table and the claims ledger
        # both quote. They are not results, but they are quoted in two places
        # each and every one of them rides on the campaign sweep rate, so a
        # recalibration moves them and a stale copy would read as a promise the
        # arithmetic no longer supports. Same registry, same mechanism.
        name="projected S0(225 mW) uncertainty, one fixed-lock morning",
        value=lambda: f"{float(_cell('projections.csv', 'proj_pull_S0_sigma', '24 per day, 1 day')):.2f}",
        find=re.compile(r"([0-9.]+)\s*MHz\s+on\s+S(?:₀|_?0)\(225"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md",
              "docs/plan/04_intensity-and-light-shift.md"],
    ),
    dict(
        name="projected beta_self detection significance, five interleaved blocks",
        value=lambda: f"{float(_cell('projections.csv', 'proj_beta_self_detection_sigma', 'interleaved, 20 K cold-spot lag')):.0f}",
        find=re.compile(r"resolved\s+at\s+about\s+([0-9]+)\s+sigma"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="7S precision needed to separate the two published rates at 5 sigma",
        value=lambda: f"{float(_cell('projections.csv', 'proj_7s_precision_needed', 'Wang read as FWHM')):.0f}",
        # \s+ throughout: the docs wrap, so a hard space in the pattern would
        # miss a citation that happens to straddle a line break
        find=re.compile(r"five\s+sigma\s+needs\s+([0-9]+)\s+kHz\s+per\s+mTorr"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        # The per-rung light-shift ceilings and the two readings that hang off
        # them. Same reason as the block above: each is quoted in the claims
        # ledger and in the transitions map, and each rides on the dataset's
        # measured line width and on a differential polarizability, so a
        # recompute of either moves all three and a stale copy would read as a
        # drive power the physics does not allow.
        name="993 nm light-shift ceiling at the dataset geometry",
        value=lambda: f"{float(_cell('projections.csv', 'proj_light_shift_ceiling', '993 nm, 5S to 6S')):.0f}",
        # \s+ throughout: the docs wrap, so a hard space would miss a
        # citation that happens to straddle a line break
        find=re.compile(r"993\s+nm\s+ceiling\s+of\s+([0-9]+)\s+mW"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="760 nm light-shift ceiling at the dataset geometry",
        value=lambda: f"{float(_cell('projections.csv', 'proj_light_shift_ceiling', '760 nm, 5S to 7S')):.0f}",
        find=re.compile(r"760\s+nm\s+ceiling\s+of\s+([0-9]+)\s+mW"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="778 nm light-shift ceiling at the dataset geometry",
        value=lambda: f"{float(_cell('projections.csv', 'proj_light_shift_ceiling', '778 nm, 5S to 5D5/2')):.0f}",
        find=re.compile(r"778\s+nm\s+ceiling\s+of\s+([0-9]+)\s+mW"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="7S adjudication margin at the 760 nm ceiling",
        value=lambda: f"{float(_cell('projections.csv', 'proj_7s_margin_at_ceiling', 'Wang read as FWHM')):.1f}",
        find=re.compile(r"adjudication\s+keeps\s+a\s+ceiling\s+margin\s+of\s+([0-9.]+)"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="778 nm factor-two test margin at the 778 nm ceiling",
        value=lambda: f"{float(_cell('projections.csv', 'proj_778_margin_at_ceiling', 'factor-two convention error at 3 sigma')):.2f}",
        find=re.compile(r"factor-two\s+test\s+drops\s+to\s+a\s+ceiling\s+margin\s+of\s+([0-9.]+)"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="778 nm source-class headroom over its ceiling",
        value=lambda: f"{_source_headroom('778 nm, 5S to 5D5/2'):.1f}",
        find=re.compile(r"([0-9.]+)\s+times\s+the\s+778\s+nm\s+ceiling"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        # The wide-scan pedestal add-on. Quoted in the ledger and in the
        # transitions map, and every figure rides on the dataset's own measured
        # signal to noise, so a re-run of the QC layer moves all three.
        name="Doppler pedestal width at the design temperature",
        value=lambda: f"{float(_cell('projections.csv', 'input_pedestal_width', '130 C, 85Rb')):.0f}",
        find=re.compile(r"([0-9]+)\s+MHz\s+wide\s+on\s+the\s+transition\s+axis"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="pedestal thermometry stacking time, four-pedestal comb",
        value=lambda: f"{float(_cell('projections.csv', 'proj_pedestal_thermometry_hours', 'to match the density scale, four-pedestal comb')):.1f}",
        find=re.compile(r"pins\s+the\s+temperature\s+in\s+about\s+([0-9.]+)\s+hours"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="pedestal retro-ratio stacking time, four-pedestal comb",
        value=lambda: f"{float(_cell('projections.csv', 'proj_pedestal_rho_hours', 'to match the adopted prior, four-pedestal comb')):.1f}",
        find=re.compile(r"reaches\s+the\s+adopted\s+retro\s+ratio\s+in\s+about\s+([0-9.]+)\s+hours"),
        mode="all",
        docs=["docs/CLAIMS.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="M16 first 5S-6S magic wavelength (1204 nm crossing)",
        value=lambda: f"{float(_cell('polarizability.csv', 'magic_5s6s', '1204nm')):.1f}",
        find=re.compile(r"(120[0-9]\.[0-9])\s*/"),
        mode="all",
        # BIG_PICTURE added 2026-08-05: its 1.2 section cites the crossing in
        # four places that were hand-typed and unpinned until this line.
        docs=["README.md", "docs/RESULTS.md", "docs/big_picture/01_why-this-line.md"],
    ),
    # --- Trace-census counts, read live from the manifest. Added
    # 2026-08-07 after the "39 committed CSVs" incident (actual 42, a
    # fifteen-second catch for any reader): hand-typed counts are the
    # silently-rotting class, so the ones the front door states are
    # pinned to data_raw/MANIFEST.csv here.
    dict(
        name="trace census: 297 total",
        value=lambda: str(sum(1 for _ in csv.DictReader(open(ROOT / "data_raw/MANIFEST.csv")))),
        find=re.compile(r"\b(297)\b(?=[^.]{0,40}traces)"),
        mode="all",
        docs=["README.md", "docs/DATA.md"],
    ),
    dict(
        name="trace census: canonical line traces",
        value=lambda: str(sum(1 for r in csv.DictReader(open(ROOT / "data_raw/MANIFEST.csv"))
                              if r["role"] in ("p_sweep", "t_sweep") and r["flag"] == "canonical")),
        find=re.compile(r"\b(159)\b(?=[^.]{0,30}(?:composite-)?line)"),
        mode="all",
        docs=["README.md"],
    ),
    dict(
        name="trace census: ruler traces",
        value=lambda: str(sum(1 for r in csv.DictReader(open(ROOT / "data_raw/MANIFEST.csv"))
                              if r["role"].startswith("ruler"))),
        find=re.compile(r"\b(105)\b(?=[^.]{0,40}(?:frequency-)?ruler)"),
        mode="all",
        docs=["README.md"],
    ),
    dict(
        name="trace census: excluded files",
        value=lambda: str(sum(1 for r in csv.DictReader(open(ROOT / "data_raw/MANIFEST.csv"))
                              if r["flag"] != "canonical")),
        find=re.compile(r"\b(33)\b(?=\s*(?:files|excluded|are\b))"),
        mode="all",
        docs=["README.md", "docs/DATA.md"],
    ),
    # --- The van der Waals anchor numbers, computed live from the
    # module. Added 2026-08-08 after the difference-form correction of
    # 2026-08-05 was found unpropagated in BIG_PICTURE (the pair ratio
    # 0.347 and its 3.5/4.5/17% satellites survived there for three
    # days) and its scale factor survived mislabeled in
    # FUTURE_TRANSITIONS. The adjudication note kept a hand-written
    # list of sites to update, and that list missed both. These entries
    # read the numbers from the code, so the next adjudication
    # propagates by test failure rather than by memory.
    dict(
        name="vdW anchor: the delta-C6 ratio (difference form)",
        value=lambda: f"{_vdw_ratio():.4f}",
        find=re.compile(r"ratio\s+(0\.3[0-9]{3})\s+(?:enters|to\s+the)"),
        mode="all",
        # The adjudication note is deliberately absent: its
        # before/after table legitimately shows the retired 0.3473.
        docs=["docs/big_picture/02_the-method-and-its-limits.md", "docs/FUTURE_TRANSITIONS_titsapph.md"],
    ),
    dict(
        name="vdW anchor: the predicted 7S rate",
        value=lambda: f"{_vdw_beta7():.2f}",
        find=re.compile(r"\b(4\.[0-9]{2})\s+kHz\s+per\s+10"),
        mode="all",
        # The note is absent here too: it carries the number only in
        # its before/after table, next to the retired 4.50.
        docs=["docs/big_picture/02_the-method-and-its-limits.md"],
    ),
    # ---- trap-design coefficients (2026-08-08): the quartic and
    # vector numbers are computed live by rb5s6s/hyperpolarizability
    # and quoted in BIG_PICTURE and CLAIMS. Same pattern as the vdW
    # anchors: the registry reads the code so a module change
    # propagates by test failure rather than by memory.
    # find regexes use \s+ between words: the docs hard-wrap, and a
    # literal-space pattern misses a citation that spans a line break
    # (the same wrap that once false-alarmed the carrier checker).
    dict(
        name="hyperpolarizability: quartic coefficient at the 1204 crossing",
        value=lambda: f"{_hyp_c1204():+.2f}",
        find=re.compile(r"([+-][0-9]\.[0-9]{2})\s+Hz\s+per\s+megahertz\s+"
                        r"squared"),
        mode="all",
        docs=["docs/big_picture/01_why-this-line.md", "docs/CLAIMS.md"],
    ),
    dict(
        # ADDED 2026-08-20, and the first registry entry ever pointed at a
        # PYTHON file. The window log named "nothing checks that a docstring's
        # numbers match what its own code produces" as the strongest candidate
        # for the next guard. The registry could always do it, since _read
        # takes any path, and this is that guard: three surfaces and one
        # producer, and a re-run that moves the number fails all three.
        name="cooperative: pair channel at 130 C, as a fraction of the line",
        value=lambda: f"{float(_coop('rate ratio at 130 C')) * 1e9:.1f}",
        find=re.compile(r"([0-9]\.[0-9])(?:e-9|\\times10\^\{?-9\}?)"),
        mode="all",
        docs=["rb5s6s/cooperative.py", "docs/wiki/magnetic-sublevels.md"],
    ),
    dict(
        # ADDED 2026-08-20. This p-value was quoted on three pages and in the
        # generated ledger, and moved from 0.010 to 0.011 when the producer's
        # default was corrected to the number its own docstring calls stable.
        # Four surfaces, one producer, now tied together.
        name="skew scaling: p against the fixed-amplitude hypothesis",
        value=lambda: f"{float(_cell('skew_scaling.csv', 'skew_hypothesis_p_fixed_amplitude', 'one-sided')):.3f}",
        find=re.compile(r"p = (0\.0[0-9]{2})\b"),
        # "any", not "all": these pages carry OTHER p-values legitimately, so
        # the requirement is that the canonical one is present, not that every
        # p on the page equals it.
        mode="any",
        docs=["docs/wiki/injection-recovery.md", "docs/wiki/third-cumulant.md",
              "docs/big_picture/07_limitations-and-identifiability.md"],
    ),
    dict(
        # The factor that carrying both fine-structure legs buys. It appears in
        # a module docstring and a wiki page and is computed in neither, which
        # is the exact shape of the defect this entry exists to prevent.
        name="cooperative: rate gain from carrying both 5P legs",
        value=lambda: f"{_coop_leg_gain():.2f}",
        find=re.compile(r"the rate by\s+([0-9]\.[0-9]{2})"),
        mode="all",
        docs=["rb5s6s/cooperative.py", "docs/wiki/magnetic-sublevels.md"],
    ),
    dict(
        # ADDED 2026-08-20. This number was quoted for weeks against the 95
        # per cent UPPER BOUND on the scalar shift rather than the calibrated
        # PREDICTION, which understated it by a third, and nothing checked it
        # against its own producer. Now two documents and one CSV must agree.
        name="polarisation: vector m_F spread at 225 mW, fully circular",
        value=lambda: f"{float(_cell('polarisation_bound.csv', 'vector_spread_at_225mW_pred')) * 1e3:.1f}",
        find=re.compile(r"(?:the spread is|sublevels by)\s+([0-9]\.[0-9])\s+kHz"),
        mode="all",
        docs=["docs/wiki/magnetic-sublevels.md",
              "docs/big_picture/02_the-method-and-its-limits.md"],
    ),
    dict(
        name="polarisation: 95 per cent limit on any g_F-squared broadening",
        value=lambda: f"{float(_cell('polarisation_bound.csv', 'dmf1_broadening_ub95')) * 1e3:.0f}",
        find=re.compile(r"([0-9]{2})\s+kHz,?\s+at\s+95\s+per\s+cent"),
        mode="all",
        docs=["docs/RESULTS.md"],
    ),
    dict(
        name="hyperpolarizability: vector-shift coefficient at 1204",
        value=lambda: f"{_hyp_v1_khz():.0f}",
        find=re.compile(r"([0-9]{3})\s+kHz\s+per\s+megahertz\s+of\s+depth"
                        r"\s+per\s+unit\s+circularity"),
        mode="all",
        docs=["docs/big_picture/01_why-this-line.md", "docs/CLAIMS.md"],
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
    (adversarial review, 2026-07-29).

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
# (D) targeted tripwire: the specific REPLACED values must not reappear in    #
# the front-door docs except on a line that explicitly marks them replaced.   #
# This guards the exact regression this file was written for.                   #
# --------------------------------------------------------------------------- #
REPLACED = [
    ("3.1", re.compile(r"S(?:₀|_?0).{0,40}3\.1\b"), "AC-Stark bound (was the Wald 3.1 MHz)"),
    ("5800", re.compile(r"5800"), "Delta-alpha bracket (was ~5800 a.u.)"),
    ("0.07-0.15", re.compile(r"0\.07-0\.15|0\.07.{0,6}0\.15"), "beta bound (was 0.07-0.15)"),
    ("0.2-0.4", re.compile(r"0\.2-0\.4|0\.2.{0,6}0\.4"),
     "beta bound (was the three-point/dof=1 headline 0.2-0.4, replaced "
     "2026-08-02 by the four-point/dof=2 0.03-0.05 headline)"),
]
_ALLOW_SUPERSEDED = re.compile(
    r"supersed|replaced|earlier|Wald|was |before |old |first version|"
    r"no longer|used to|reported ", re.I)

# THE SAME TRIPWIRE, POINTED AT CODE. Added 2026-08-20 after a number was
# corrected in a module docstring and a wiki page and left standing in the
# producer that writes the CSV both of them cite. The front-door list above
# scans two markdown files; a retired number hides just as well in a
# docstring, and the window log named that class as the next guard to build.
#
# A general check was MEASURED first and rejected: extracting every number
# from five producers' docstrings and asking whether each appears in that
# producer's own CSV flagged 16, of which one was a real staleness and the
# rest are thresholds and hypothesis values that correctly never appear in an
# output. A tripwire on values known to be retired has no such false floor.
REPLACED_IN_CODE = [
    # NOT LISTED, and the reason is the useful part: the retired pair-channel
    # value 1.5e-10 is ALSO the live single-atom hyperfine sum, so a tripwire
    # on the bare number cannot tell the two apart and fires on correct prose.
    # A tripwire is only available where the retired value is unique.
    ("nine or ten orders",
     re.compile(r"(?:nine|ten) orders"),
     "headroom claim: was nine in one paragraph and ten in another, neither "
     "sourced, retired 2026-08-20 for six orders against wing_check.csv",
     ("rb5s6s/cooperative.py", "scripts/run_cooperative_channel.py",
      "docs/wiki/magnetic-sublevels.md")),
]


@pytest.mark.parametrize("val,pat,label,files", REPLACED_IN_CODE,
                         ids=lambda x: x if isinstance(x, str) else "")
def test_no_superseded_value_in_the_code_that_carries_it(val, pat, label, files):
    """A retired number must not survive in a docstring or a producer.

    Ceiling-tested on the way in: planting 1.5e-10 back into
    scripts/run_cooperative_channel.py fails this, which is how the real
    instance was found.
    """
    for doc in files:
        if not (ROOT / doc).exists():
            continue
        for i, ln in enumerate(_read(doc).splitlines(), 1):
            if pat.search(ln) and not _ALLOW_SUPERSEDED.search(ln):
                pytest.fail(f"{doc}:{i}: retired {label} reappears: "
                            f"{ln.strip()[:90]}")


@pytest.mark.parametrize("val,pat,label", REPLACED, ids=lambda x: x if isinstance(x, str) else "")
def test_no_superseded_value_in_front_door(val, pat, label):
    for doc in ("README.md", "docs/BIG_PICTURE.md"):
        for ln in _read(doc).splitlines():
            if pat.search(ln) and not _ALLOW_SUPERSEDED.search(ln):
                pytest.fail(f"{doc}: replaced {label} reappears: {ln.strip()[:90]}")


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
    record's four headline outcomes."""
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
    from _fileset import tracked_and_new
    class _O:
        pass
    out = _O()
    out.stdout = "\n".join(tracked_and_new("*.md", "*.py"))
    if not out.stdout:
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
    # The panel used to carry a typed "~1.6". It now formats the same
    # inverse-variance mean this test recomputes, so the pin is on the
    # construction rather than on a literal a recompute could strand.
    assert "% (float(np.mean(freeS)), T_dip)" in fig_src, (
        "fig5's right-hand title no longer reads its flat free-fit value from "
        "the plotted means; a typed number there can go stale silently")
    m07 = (ROOT / "docs" / "methods" / "07_what_we_found.md").read_text(encoding="utf-8")
    # The band was written `$1.5$–$1.75$`. The math-render sweep (2026-08-09)
    # rewrote it as plain `1.5–1.75`, because GitHub opens an inline span only
    # where the `$` follows a line start, whitespace, `(` or `*`, so the `$`
    # after the en-dash never opened one and the range reached the page as raw
    # source. Same two numbers pinned, one less punctuation between them.
    assert "2.1/2.2/1.5" in m07


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
    from _fileset import tracked_and_new
    _shipping = tracked_and_new("*.md", "*.py")
    if not _shipping:
        pytest.skip("not a git checkout")
    bad = []
    for rel in _shipping:
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


def test_the_advertised_counts_agree_with_each_other():
    """Sites that must agree exactly are compared to EACH OTHER, not to truth.

    The guard below compares every advertised count to the real one under a 5
    per cent tolerance, INDEPENDENTLY per site. That is a drift detector and
    not a consistency checker, and the difference showed on 2026-08-16:
    docs/methods.md carried 2148 and 2093 three lines apart, both within
    tolerance of the truth at the time, so nothing failed while the page
    contradicted itself. The stale one had survived two separate repairs of
    the very same class, because each repair fixed the sites its author had
    already read.

    A percentage tolerance is right for the comparison against the suite,
    which grows a test at a time. It is wrong for two sentences on one page
    that describe the same number, and those have to be equal.
    """
    import re as _re

    text = (ROOT / "docs" / "methods.md").read_text(encoding="utf-8")
    # Every number on a line that runs pytest, plus the battery line, all of
    # which describe the same suite from different angles.
    full = set(_re.findall(r"(\d{3,5})-test battery", text))
    full |= set(_re.findall(r"--runslow\s*#\s*full\s+(\d{3,5})", text))
    fast = set(_re.findall(r"battery \((\d{3,5}) fast", text))
    fast |= set(_re.findall(r"pytest -q\s+#\s*(\d{3,5}) fast", text))

    bad = []
    if len(full) > 1:
        bad.append(f"the full-suite count is given as {sorted(full)}")
    if len(fast) > 1:
        bad.append(f"the fast-suite count is given as {sorted(fast)}")
    assert not bad, (
        "docs/methods.md contradicts itself about the size of its own test "
        "suite:\n  " + "\n  ".join(bad)
        + "\nThese describe one quantity each and must be equal, which a "
          "percentage tolerance against the real count cannot enforce.")


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
    # (in the public mirror) the record-only tests, is not the reference.
    import pytest as _p
    # This compares THIS checkout's documented number against THIS checkout's
    # collected count, so there is nothing cross-checkout about it and no
    # reason to skip on the mirror. It used to skip whenever
    # private/manuscripts was absent, which is always true in the public
    # copy, so the number a reader actually sees was the one number never
    # checked: on 2026-08-13 the mirror advertised 1570 against a real 1872.
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
    # A count does not have to sit beside the word "test" to mislead a reader.
    # The runnable block in methods.md carried "# 1160 fast tests" and "full
    # 1293 incl. slow closures" until 2026-08-14, by which time both had
    # drifted by a factor of 1.8, and neither matched the pattern above: one
    # puts an adjective between the number and the noun, the other names no
    # noun at all. Any number on a line that runs pytest is advertising what
    # that command prints, so check those lines whatever words surround them.
    # Matching on proximity instead was tried and rejected: it flags the 560
    # in an image width whose alt text happens to say "test".
    stale += [n for line in txt.splitlines() if "pytest" in line
              for n in re.findall(r"\b(\d{3,5})\b", line)
              if abs(int(n) - total) / total > 0.05]
    assert not stale, (
        f"documented test counts {sorted(set(stale))} are more than 5% from the "
        f"real {total} ({slow} slow). Update docs/methods.md and README.md.")


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


def test_pipeline_bookkeeping_counts_match_the_tree():
    """Stage and CSV counts quoted in the front-door documents, derived live.

    These are class (b) bookkeeping numbers rather than physics, so they get a
    guard instead of a registry row, but they go stale exactly as fast: the
    2026-08-15 sweep found README and REPRODUCING both quoting 25 stages and
    43 CSVs against a tree with 27 and 46. Nothing had ever checked them.
    """
    import re
    sh = (ROOT / "scripts" / "run_all.sh").read_text(encoding="utf-8")
    loop = re.search(r"for\s+s\s+in\s+(.*?);\s*do", sh, re.S)
    stages = len(set(re.findall(r"\b(run_\w+)\b", loop.group(1)))) if loop else 0
    n_csv = len(list((ROOT / "results").glob("*.csv")))
    assert stages > 10 and n_csv > 10, (
        f"the counter itself is broken (stages={stages}, csvs={n_csv}), so an "
        "empty result would mean 'no check ran' rather than 'clean'")

    bad = []
    for rel in ("README.md", "docs/REPRODUCING.md"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        for m in re.finditer(r"(\d+)\s+analysis stages", text):
            if int(m.group(1)) != stages:
                bad.append(f"{rel}: says {m.group(1)} analysis stages, "
                           f"run_all.sh loops over {stages}")
        for m in re.finditer(r"of the (\d+) committed CSVs", text):
            if int(m.group(1)) != n_csv:
                bad.append(f"{rel}: says {m.group(1)} committed CSVs, "
                           f"results/ holds {n_csv}")
    assert not bad, "pipeline bookkeeping has gone stale:\n  " + "\n  ".join(bad)


def test_identifiability_prose_matches_its_csv():
    """The §4.10 identifiability paragraph, checked against the row it describes.

    A whole paragraph sat frozen at pre-2026-08-02 values while the CSV moved
    under it: condition number 480 against 390, worst-constrained sigma 0.07
    against 0.062, ridge slope and its predicted counterpart both stale. Every
    number in it is derivable, so none of it needs to be typed twice.
    """
    import csv as _csv
    vals = {}
    with open(ROOT / "results" / "identifiability.csv", encoding="utf-8") as fh:
        for r in _csv.DictReader(fh):
            try:
                vals[(r["quantity"], r["key"])] = float(r["value"])
            except (ValueError, KeyError):
                pass
    text = (ROOT / "docs" / "methods" / "06_the_statistics.md").read_text(encoding="utf-8")
    checks = [
        ("condition number", vals[("condition_number", "width_block")], r"covariance\* is \$\\approx(\d+)\$", 0),
        ("branch gap", vals[("branch_gap", "local")], r"\\Delta\\chi\^2\\approx(\d+)\$ preference", 0),
        ("ridge slope", vals[("ridge_slope", "zoom_profile")], r"ridge slope \(\+([\d.]+)\)", 3),
    ]
    bad = []
    for name, want, pat, places in checks:
        m = re.search(pat, text)
        if m is None:
            bad.append(f"{name}: the prose pattern no longer matches, so this "
                       "guard has stopped guarding")
            continue
        got = float(m.group(1))
        if round(got, places) != round(want, places):
            bad.append(f"{name}: prose says {got}, identifiability.csv says {want}")
    assert not bad, "methods 4.10 has drifted from its CSV:\n  " + "\n  ".join(bad)


# A prose count OF A TABLE IN ANOTHER FILE goes stale silently: the table grows,
# the sentence does not, and no reader of either file is looking at both. Three
# claims about the same table disagreed with it and with each other, the section
# heading saying eight and constants.py saying six against a table of ten, and
# the wrong ones had outlived several sweeps that read the documents, because
# reading one file cannot catch it (2026-08-16, lesson 124).
def test_the_advertised_wavemeter_record_count_matches_its_table():
    """Both prose counts of the drift-record table equal the table's rows.

    The table is found by walking forward from the section 6 heading, not by
    matching its column header, because APPARATUS.md has more than one table
    whose header names a lock state and an earlier version of this guard
    silently counted the wrong one. If the section or either claim disappears
    the test SKIPS loudly rather than passing, since a count guard that quietly
    stops finding its subject is worse than no guard.
    """
    import pytest as _p

    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
             "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15}

    lines = (ROOT / "docs" / "APPARATUS.md").read_text().splitlines()
    heads = [i for i, l in enumerate(lines)
             if l.startswith("## 6. Laser drift")]
    if not heads:
        _p.skip("the APPARATUS.md laser-drift section was not found, so this "
                "guard cannot see what it is meant to check")
    rows = 0
    for i in range(heads[0], len(lines)):
        if lines[i].startswith("|---"):
            j = i + 1
            while j < len(lines) and lines[j].startswith("|"):
                rows += 1
                j += 1
            break
    if not rows:
        _p.skip("no table follows the laser-drift heading")

    claims = []
    m = re.search(r"## 6\. Laser drift: (\w+) wavemeter records", lines[heads[0]])
    if m:
        claims.append(("docs/APPARATUS.md heading", m.group(1)))
    src = (ROOT / "rb5s6s" / "constants.py").read_text()
    for c in re.findall(r"\b(\w+) wavemeter records are tabulated", src):
        claims.append(("rb5s6s/constants.py", c))
    if not claims:
        _p.skip("neither site advertises a wavemeter record count any more")

    bad = []
    for where, c in claims:
        n = words.get(c.lower())
        if n is None:
            try:
                n = int(c)
            except ValueError:
                bad.append(f"{where}: unparsable count {c!r}")
                continue
        if n != rows:
            bad.append(f"{where} says {c} ({n}), the table has {rows}")
    assert not bad, ("an advertised wavemeter record count disagrees with the "
                     "table in docs/APPARATUS.md section 6:\n  "
                     + "\n  ".join(bad))
