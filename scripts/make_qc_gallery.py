#!/usr/bin/env python3
"""
The inspection gallery: every trace in the archive, drawn once, for the eye.

The tooth-indexing defect that motivated the validity ladder was found by
looking at a picture, not by reading a number. Nothing in the pipeline draws the
other 296 traces, so nothing in the pipeline would have found the same defect
anywhere else. This script closes that gap.

    python scripts/make_qc_gallery.py

Output, all of it under `private/qc_gallery/` and none of it tracked:

    index.html                          the way in
    <class>/<condition>__v<version>.png one page per condition

THE UNIT OF PRESENTATION IS THE CONDITION. One page holds every repeat of one
condition, as rows, on ONE SHARED VERTICAL SCALE for the whole page. That scale
is the point: the job this gallery does is judging whether repeats agree, and a
page whose rows each auto-scale cannot answer it. Sixty one pages, where the
first version of this gallery drew 297 separate panels and 13 contact sheets. A
condition page already is the contact sheet for its condition.

Each page carries a header block placed in INCHES from the top, so it neither
stretches nor collides when a page gains a row: the observation in plain words,
then two labelled columns of small grey labels over large dark values. Each row
carries a left gutter with the repeat number and the file stem, the signal with
the drawn model, and the residual STANDARDIZED, every sample divided by the
error the fit weighted it with, under a shaded band of one point error. The raw
residual scatter in millivolts sits in the row's own stack of numbers, so
magnitude is not lost. The reason for standardizing is the one
`make_fig0_spectrum.py` states: the raw noise grows with signal level, so a raw
strip bulges at the line centre and reads as a model failure.

Comb pages add a tooth-order axis across the top of each signal row and a third
column of that trace's seven fitted tooth heights, drawn against the residual
scatter of its own fit.

THE TOOTH NUMBERING. Which combs carry a displaced grid is decided by the
AMPLITUDE TEST of amendment 5 section E5 of
`docs/notes/ruler_validity_and_trim_prereg.md`: a second-order tooth standing
taller than a first-order tooth, which no modulation depth below the crossing at
2 beta = 2.630 can produce. That test picks out 54 combs of the 104 fitted
rulers, two more than the labelling verdict marks, plus one comb of the aborted
session that has no calibration record at all.

Whether a proposed correction is ACCEPTED is decided by the RATIO TEST of
amendment 6 section F4: a correction is accepted when the corrected numbering
brings the second-to-first height ratio from unphysical or displaced INTO the
band the campaign measured, 0.159 to 0.249 of the first order, which is what
2 beta = 1.449 to 2 beta = 1.730 produces under the height law of section F1.
The CARRIER height plays no part in either test, in both directions: it carries
residual amplitude modulation, its measured ratio to the first order runs from
0.360 to 1.188, and it identifies nothing. Corrections that an earlier carrier
test failed for drawing a tall carrier are re-judged here on their ratios alone.

The ratio is compared to the band WITH ITS OWN ERROR, the scatter of each comb's
own fit residual carried through, which is the band the height bars are already
drawn against. That is not a tolerance bolted on: on the weakest combs of the
70 °C block the error reaches across the whole band, and the true statement
there is that the heights settle nothing, not that a correction is refused. The
three outcomes a flagged comb can reach are therefore corrected, refused and
undecided, and the page says which in a sentence.

Where a correction is accepted the page draws the corrected tooth order and
keeps the fitted one beside it, so the picture never hides the table. This is a
display correction and only that: the spacing and the drawn curve stay the comb
fit exactly as it stands, because a relabelling does not move the pitch.

WHO READS IT. Two external physicists with no knowledge of this repository, plus
the owner. The page body is therefore held to the same register as the citable
figures: spelled-out quantities with units, no column names, no status codes, no
internal vocabulary. Everything needed to trace a page back to the tables lives
in the grey footer line and in the index's per-trace fold-outs.

THREE DO-NOTS, each of them a decision rather than a preference.

1. Never route a page through `make_figures._save()`. Anything under `figures/`
   is citable, carries a data fingerprint and is held to the figure register and
   the freshness guard. These pages are none of those things, and putting them
   in the citable tree would make every one of them a publication decision.

2. Never add this file to the figure-register targets in
   `tests/test_figure_register.py`. The register's AST walk keys on `_footer()`,
   which this file has none of. The register rule is applied here in spirit, by
   hand, over every string that reaches a canvas, and held by this file's own
   guard in `tests/test_gallery_hygiene.py`.

3. Never wire this into `scripts/ci_gate.sh`. The gallery is an audit that can
   trigger a recompute, not a gate that blocks one. It needs the raw archive, it
   takes minutes rather than seconds, and a red gate here would say nothing
   about whether the analysis is correct.

Reads: data_raw/MANIFEST.csv and the raw traces, results/qc_metrics.csv,
results/ruler_traces.csv, results/global_archive_fit.csv.
"""

from __future__ import annotations

import csv
import html
import re
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from scipy.special import jv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.constants import TOOTH_SPACING_LASER_HZ  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.linefit import adaptive_halfwidth, to_frequency  # noqa: E402
from rb5s6s.noise import condition_noise_model, signal_level, sigma_of_v  # noqa: E402
from rb5s6s.qc import hard_flags, ingest_flags, trace_metrics  # noqa: E402
from rb5s6s.ruler import TEETH, _comb, validated_comb_fit  # noqa: E402


# ---------------------------------------------------------------------------
# where output is allowed to go, and nowhere else
# ---------------------------------------------------------------------------

GALLERY_DIR = C.REPO_ROOT / "private" / "qc_gallery"
"""The one writable root. `private/` is gitignored wholesale, by directory
rather than by filename glob, so nothing written here can become tracked by
being named something the ignore rules did not anticipate."""


def out_path(*parts: str) -> Path:
    """A path under :data:`GALLERY_DIR`, with the containing folder created.

    Every write in this script goes through here, and this function REFUSES a
    destination that resolves outside the gallery root. That refusal is the
    structural half of the guard in tests/test_gallery_hygiene.py: the static
    half checks that no other write path exists in the file, and this half
    checks that the one that does cannot be talked into escaping.
    """
    p = (GALLERY_DIR.joinpath(*parts)).resolve()
    root = GALLERY_DIR.resolve()
    if p != root and root not in p.parents:
        raise ValueError(f"refusing to write outside {root}: {p}")
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def save_png(fig, *parts: str) -> None:
    """The only place a figure reaches the disk. Every drawing routine ends
    here, so there is one destination expression in the file to check."""
    fig.savefig(out_path(*parts), dpi=110)
    plt.close(fig)


def pipeline_version() -> str:
    """The release version the pages are stamped with, read from the one place
    that carries it. Falls back to the package attribute if the field moves."""
    try:
        text = (C.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        m = re.search(r'^version = "([^"]+)"', text, re.M)
        if m:
            return m.group(1)
    except OSError:
        pass
    import rb5s6s
    return rb5s6s.__version__


# ---------------------------------------------------------------------------
# the five classes
# ---------------------------------------------------------------------------

CLASSES = ("canonical", "ruler_p", "ruler_t", "quarantine", "discarded")

CLASS_TITLE = {
    "canonical": "Lines",
    "ruler_p": "Calibration combs, power session",
    "ruler_t": "Calibration combs, temperature session",
    "quarantine": "The aborted first session",
    "discarded": "Curation discards",
}

CLASS_BLURB = {
    "canonical": "lines recorded with the modulation off, the measurements the "
                 "analysis is built on",
    "ruler_p": "the combs that open and close the power session",
    "ruler_t": "one comb per temperature of the temperature session",
    "quarantine": "traces of the aborted first attempt, excluded a whole session "
                  "at a time",
    "discarded": "traces removed one at a time during curation",
}

CLASS_TAG = {
    "canonical": "in the analysed set",
    "ruler_p": "power session",
    "ruler_t": "temperature session",
    "quarantine": "from the aborted first session",
    "discarded": "removed during curation",
}
"""The class, in words, on the title of every page. Four names collide across
classes, so a picture found on its own has to say which of the two traces that
share a name it is."""

SESSION_WORD = {"P": "power session", "T": "temperature session",
                "Q": "aborted first session"}

PEAK_COLOR = {"4121": "#0072B2", "4154": "#D55E00",
              "4192": "#009E73", "4207": "#E69F00"}

MARK_COLOR = {"outlier": "#c51b7d", "quarantined": "#54278f",
              "advised": "#9970ab", "excluded": "#4d4d4d"}
"""Note colours, drawn from a magenta to purple to grey family that shares no
member with the four wavelength colours above."""

TRIM_SHADE = "#d6604d"

INK = "#1a1a1a"
MUTED = "#5a5a5a"
FAINT = "#8a8a8a"
DATA = "#7a7a7a"
RULE = "#c9c9c9"
UNFIT = "#cfcfcf"
EDGE = "#b06a00"
FIRST_ORDER = "#2166ac"

MINUS = "−"

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.edgecolor": "#b0b0b0",
    "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
    "axes.labelsize": 8.5,
    "legend.frameon": False,
})


def _signed(k: int) -> str:
    """A tooth order with the typographic minus the numeric axes use, so the
    order printed above the trace and the order printed under the height bars
    are the same string and can be read against each other."""
    if k == 0:
        return "0"
    return f"+{k}" if k > 0 else f"{MINUS}{abs(k)}"


def _ms(x: float) -> str:
    """A time in milliseconds, with the same minus the axes print.

    Spelled out rather than done with `str.replace`, because the write guard in
    tests/test_gallery_hygiene.py counts every `replace` in this file as a
    possible write to disk and is right to.
    """
    s = f"{x:.0f}"
    return MINUS + s[1:] if s.startswith("-") else s


def _stem(path: str) -> str:
    """The file stem, which is what a reader looking for a raw trace types."""
    return Path(path).stem


# ---------------------------------------------------------------------------
# the modulation depth, and the two tests that use it
# ---------------------------------------------------------------------------

MOD_DEPTH_2BETA = 1.569
MOD_DEPTH_SD = 0.058
MOD_DEPTH_RANGE = (1.449, 1.730)
"""The drive depth, measured in amendment 6 section F1 of
`docs/notes/ruler_validity_and_trim_prereg.md` on the 41 combs whose recorded
numbering the verdict passes cleanly and whose first-order pair stands above
five times the fit residual. Written as 2 beta throughout and never as a bare
depth in radians, which a reviewer read as beta. Median 2 beta = 1.569,
standard deviation 0.058, range 2 beta = 1.449 to 2 beta = 1.730. The earlier
pooled 2 beta = 1.62 sits at the upper edge of it."""

CROSSING_2BETA = 2.630
"""Where the second-order and first-order Bessel weights cross. Below it a
second-order tooth taller than a first-order tooth is impossible, which is what
makes the amplitude test of section E5 safe. The crossing is the same under
either reading of the height law, since both are monotone in J_2 over J_1."""

CARRIER_RATIO_RANGE = (0.360, 1.188)
"""What the carrier-to-first-order ratio actually does across the same 41 combs.
Pure phase modulation predicts 0.696 at the measured depth. The spread is
residual amplitude modulation at the carrier, so the carrier height is evidence
of nothing and is kept out of both tests."""


def _second_to_first(two_beta: float) -> float:
    """The second-to-first tooth HEIGHT ratio a phase modulation at 2 beta
    produces.

    The teeth are two-photon signals. The comb-amplitude derivation of
    `docs/methods/05_the_frequency_ruler.md` gives the tooth at k an amplitude
    of J_k(2 beta), by Neumann's addition theorem over every sideband pair, and
    the height drawn here is the modulus squared of it. So the ratio is the
    SQUARE of the Bessel weights, taken at 2 beta and not at half of it. An
    earlier version of this function did neither, and the two errors nearly
    cancelled, which is what kept it out of sight. Amendment 6 section F1 sets
    the law out and states what the archive can and cannot say about it.
    """
    return float(jv(2, two_beta) ** 2 / jv(1, two_beta) ** 2)


RATIO_BAND = (_second_to_first(MOD_DEPTH_RANGE[0]),
              _second_to_first(MOD_DEPTH_RANGE[1]))
RATIO_CROSSING = _second_to_first(CROSSING_2BETA)


DEPTH_SENTENCE = (
    f"The phase modulation runs at one depth across the campaign, 2β = "
    f"{MOD_DEPTH_2BETA:.3f} with a standard deviation of {MOD_DEPTH_SD:.3f}, which "
    f"is four per cent, and at any depth below 2β = {CROSSING_2BETA:.2f} a second "
    "order tooth taller than a first order tooth is impossible, which is the one "
    "thing that identifies a displaced numbering.")

CARRIER_SENTENCE = (
    "The carrier is left out of that ordering because its height carries residual "
    f"amplitude modulation and runs from {CARRIER_RATIO_RANGE[0]:.3f} to "
    f"{CARRIER_RATIO_RANGE[1]:.3f} of the first order across the campaign, so a "
    "carrier taller or shorter than the teeth beside it identifies nothing.")

GATE_SENTENCE = (
    f"Across the depths that campaign spans, 2β = {MOD_DEPTH_RANGE[0]:.3f} to "
    f"2β = {MOD_DEPTH_RANGE[1]:.3f}, the second order teeth stand between "
    f"{RATIO_BAND[0]:.3f} and {RATIO_BAND[1]:.3f} of the first order, and a tooth "
    "numbering is redrawn here only where a whole slot brings that ratio into those "
    "bounds, judged against the error the fit's own scatter puts on it.")

BAR_KEY_SENTENCE = (
    "In the height bars of each row the two first order teeth are blue, the shaded "
    "band rising from zero is the scatter of that row's own fit residual, printed "
    "beside it, and a tooth that does not clear that band is drawn hollow, so how "
    "many of the seven teeth the fit can actually see is read off the picture.")

GREY_TICK_SENTENCE = (
    "A tooth order printed in grey above a trace marks a tooth centre the recorded "
    "sweep never reached, so its height comes from the shoulder the fit could see "
    "and not from a tooth drawn in full.")

RELABEL_COLOR = {"recorded": "#1a4f7a", "amplitudes": "#00695c",
                 "none": "#4d4d4d"}
"""The tooth-numbering note is not an exclusion, so it does not share the mark
palette. Its three colours separate a correction whose offset the record already
carries from one read off this page's own heights, and both from a displaced
numbering that no offset repairs."""


# ---------------------------------------------------------------------------
# plain language for the closed vocabularies the tables carry. Every entry is a
# token that appears in a committed column and a sentence a physicist who has
# never seen this repository can act on.
# ---------------------------------------------------------------------------

TRIM_WORD = {
    "sustained positive residual, upper tail":
        "cut from the late end of the sweep, where the residual stayed positive",
    "sustained positive residual, lower tail":
        "cut from the early end of the sweep, where the residual stayed positive",
    "refused, trim would reach into the guarded half":
        "nothing cut, a cut would have reached into the fitted structure",
    "not applicable, multi-peak trace":
        "nothing cut, the search for a drifting tail is not run on a trace with "
        "several peaks",
    "": "nothing cut, nothing refused",
}

OUTLIER_WORD = {
    "spacing_outlier": "its tooth spacing sits far from the rest of its group",
}

CARRIER_WORD = {
    "top_three_unrecoverable":
        "shifting the tooth grid by whole slots and removing the suspect outer "
        "tooth both failed to bring the two first order teeth among the three "
        "tallest without worsening the fit",
    "refit_failed": "the comb fit would not converge when the labelling was retried",
    "no_excision_candidate": "no outer tooth stands high enough to explain the pattern",
}

DISCARD_WORD = (
    ("duplicate-name save", "the second save of one recording, superseded by the "
                            "copy that was kept"),
    ("dimmer than its repeat", "about a quarter dimmer than the repeats taken "
                               "beside it"),
    ("supernumerary", "one repeat more than the written plan allowed for this "
                      "condition, and excluded by that plan before the analysis ran"),
    ("indistinguishable from kept", "indistinguishable from the repeats kept beside "
                                    "it, and excluded by the written plan before the "
                                    "analysis ran"),
)


def trace_class(row: dict) -> str:
    if row["flag"] == "discarded":
        return "discarded"
    if row["flag"] == "quarantined":
        return "quarantine"
    if row["role"] in ("ruler_p", "ruler_t"):
        return row["role"]
    return "canonical"


def power_w(row: dict) -> float:
    """Power in watts. A blank cell is a temperature sweep trace, taken at the
    dwell's 225 mW exactly as the archive fit takes it."""
    return int(row["power_mW"]) / 1e3 if row["power_mW"] else 0.225


def condition(row: dict) -> str:
    """The group a trace is drawn with, which is also the group its noise law is
    built from. For every class this is the block the pipeline itself groups by,
    so a page is a comparison a reader can make."""
    peak, T = row["peak"], int(float(row["temperature_C"]))
    if row["rf_on"] == "True":
        if row["bracket"]:
            return f"{peak}nm_{row['bracket']}_bracket"
        return f"{peak}nm_{T}C_comb"
    return f"{peak}nm_{T}C_{int(round(power_w(row) * 1e3))}mW"


def page_name(cls: str, cond: str, version: str) -> str:
    return f"{cond}__v{version}.png"


# ---------------------------------------------------------------------------
# the committed record each page is annotated against
# ---------------------------------------------------------------------------

def _table(name: str) -> dict:
    path = C.RESULTS_DIR / name
    if not path.exists():
        print(f"  ({name} absent, its annotations will be blank)")
        return {}
    with open(path, newline="") as f:
        return {r["file"]: r for r in csv.DictReader(f)}


def _truthy(x) -> bool:
    """The tables write booleans three ways: a float from the quality pass, a
    Python bool from the ruler pass, an int from the outlier columns."""
    s = str(x).strip().lower()
    if s in {"true", "yes"}:
        return True
    try:
        return float(s) != 0.0
    except ValueError:
        return False


def _num(x, default=float("nan")) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# per trace analysis: one record per manifest row, ready to draw
# ---------------------------------------------------------------------------

def line_records(rows, ctx, prates):
    """Radio frequency off traces, built the way the global archive fit builds
    them so that the drawn curve is the shared optimum and not a local one.

    One noise law per condition, from that condition's own traces, then the
    adaptive fit window, then the local nuisance refit of the figure gallery's
    code path. Traces outside the canonical population never entered that fit,
    so their curve is the shared optimum EVALUATED on them, which the page says
    once.

    The model is evaluated across the WHOLE recorded sweep and the samples the
    fit was not asked about are drawn paler, because a page that draws a model
    across samples it was never fitted to makes a sound fit look like a failing
    one. That is how the rising retrace tail on three of the five 993.4207 nm
    repeats at 130 °C and 25 mW was first misread.
    """
    import make_figures as MF

    groups = defaultdict(list)
    for r in rows:
        groups[(trace_class(r), condition(r))].append(r)

    out = []
    for key in sorted(groups):
        recs = groups[key]
        loaded = [load_trace(trace_path(r), with_info=True) for r in recs]
        law = condition_noise_model([v for _, v, _ in loaded])
        tau = max(law.get("tau_int", 1.0), 1.0)
        for r, (t, v, info) in zip(recs, loaded):
            rec = {"file": r["file"], "row": r, "cls": key[0], "cond": key[1],
                   "t": t, "v": v, "info": info, "kind": "line", "law": law,
                   "nu": None, "model": None, "resid": None, "used": None,
                   "centre": float("nan"), "halfwidth": float("nan"), "win": None,
                   "rate": float("nan"), "fit": None, "fit_note": ""}
            pk = r["peak"]
            if pk not in prates:
                rec["fit_note"] = ("no calibrated sweep rate is on record for this "
                                   "line, so the trace is drawn without a model")
                out.append(rec)
                continue
            rate = prates[pk][0]
            nu = to_frequency(t, rate)
            lev, base = signal_level(v)
            c0 = float(nu[int(np.argmax(lev))])
            sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
            hw = adaptive_halfwidth(nu, v)
            m = np.abs(nu - c0) <= hw
            block = f"camp{int(float(r['temperature_C']))}"
            if block not in ctx["sl_blocks"]:
                rec["fit_note"] = ("the archive fit carries no laser line width at "
                                   "this temperature, so the trace is drawn without "
                                   "a model")
                out.append(rec)
                continue
            fitrec = dict(sess="camp", peak=pk, T=float(r["temperature_C"]),
                          P=power_w(r), x=nu[m], v=v[m], sg=sg[m], c0=c0,
                          A0=float(lev.max()), b0=float(base), sl=block)
            try:
                fr = MF._fit_rec_nuisances(ctx, fitrec)
            except Exception:                            # a fit that will not run
                rec["fit_note"] = ("the local match of height, centre and background "
                                   "did not converge, so the trace is drawn without "
                                   "a model")
                out.append(rec)
                continue
            rec["fit"] = fr
            rec["rate"] = rate
            rec["nu"] = nu
            rec["centre"] = float(fr["cc"])
            rec["halfwidth"] = float(hw)
            # the window edges are kept as they were SET, on the seed centre, so
            # the dashed rules land on the samples the mask actually cut and not
            # half a linewidth away from them
            rec["win"] = (c0 - hw, c0 + hw)
            rec["used"] = m
            rec["model"] = fr["model_at"](fr["sol"].x, nu)
            rec["raw_resid"] = v - rec["model"]
            rec["resid"] = rec["raw_resid"] / sg
            out.append(rec)
    return out


def comb_records(rows):
    """Rulers, through the validity ladder, one noise law per block.

    The law is built from the block members the ladder itself would keep, which
    is what `run_ruler.py` does: a dropout riddled export is not allowed to set
    the noise scale its siblings are measured against. It is still DRAWN, with
    the reason it enters nothing printed on its page, because a trace nobody ever
    looks at is a trace nobody can check.
    """
    groups = defaultdict(list)
    for r in rows:
        groups[(trace_class(r), condition(r))].append(r)

    out = []
    for key in sorted(groups):
        recs = groups[key]
        loaded = [load_trace(trace_path(r), with_info=True) for r in recs]
        keep = []
        for r, (t, v, info) in zip(recs, loaded):
            flags = hard_flags(trace_metrics(t, v, rf_on=True), rf_on=True) \
                + ingest_flags(info)
            broken = [f for f in flags
                      if "dropout" in f or "no comb" in f or "truncated" in f]
            keep.append(not broken)
        usable = [v for (_, v, _), k in zip(loaded, keep) if k]
        law = condition_noise_model(usable if len(usable) >= 2
                                    else [v for _, v, _ in loaded])
        for r, (t, v, info), ok in zip(recs, loaded, keep):
            rec = {"file": r["file"], "row": r, "cls": key[0], "cond": key[1],
                   "t": t, "v": v, "info": info, "kind": "comb", "law": law,
                   "nu": None, "model": None, "resid": None, "used": None,
                   "centre": float("nan"), "halfwidth": float("nan"), "win": None,
                   "rate": float("nan"), "fit": None, "fit_note": ""}
            if not ok:
                rec["fit_note"] = ("this export is broken as a comb and left the "
                                   "frequency calibration before any fit ran")
            try:
                f = validated_comb_fit(t, v, law)
            except RuntimeError:
                rec["fit_note"] = (rec["fit_note"] + ", and " if rec["fit_note"]
                                   else "") + "the comb fit did not converge on it"
                out.append(rec)
                continue
            rec["fit"] = f
            rec["model"] = _comb(t, f["t0_ms"], f["delta_ms"], f["width_ms"],
                                 np.asarray(f["heights"]), f["b0"], f["b1"])
            lev, _ = signal_level(v)
            sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6)
            rec["raw_resid"] = v - rec["model"]
            rec["resid"] = rec["raw_resid"] / sg
            rec["used"] = np.ones(len(v), dtype=bool)
            if key[0] == "quarantine":
                rec["fit_note"] = (rec["fit_note"] + ", and " if rec["fit_note"]
                                   else "") + ("the seven tooth fit drawn beside each "
                                               "of these traces was made to that trace "
                                               "alone, and the spacing it returns "
                                               "enters no frequency calibration")
            out.append(rec)
    return out


# ---------------------------------------------------------------------------
# the tooth numbering the page draws
# ---------------------------------------------------------------------------

def _height_map(heights) -> dict:
    return {k: float(h) for k, h in zip(TEETH, heights)}


def displaced_grid(heights) -> bool:
    """True when the tooth heights say the numbering is shifted off the comb.

    The one criterion, from amendment 5 section E5 of the preregistration: below
    the crossing the expected height ordering puts both first-order teeth above
    both second-order teeth, so a SECOND-order tooth standing taller than a
    FIRST-order tooth is impossible on a correctly numbered comb. The carrier is
    not part of the test in either direction, which is the half that was being
    got wrong: it carries residual amplitude modulation and can stand above or
    below its own first-order pair on a perfectly good comb.

    Applied to the persisted heights this fires on 54 combs of the 104 fitted
    rulers, two more than the labelling verdict marks.
    """
    h = _height_map(heights)
    return max(h[-2], h[2]) > min(h[-1], h[1])


def forbidden_pair(heights):
    """The tallest second-order tooth and the shortest first-order tooth, in the
    numbering the fit produced, so a page can print the evidence it acted on."""
    h = _height_map(heights)
    second = max((-2, 2), key=lambda k: h[k])
    first = min((-1, 1), key=lambda k: h[k])
    return second, h[second], first, h[first]


def second_to_first_ratio(heights, shift: int = 0, fit_rms: float = 0.0):
    """The mean of the two second-order teeth over the mean of the two first-order
    teeth, under a numbering shifted by `shift` slots, with its error.

    None when the shift moves one of the four teeth outside the seven the fit
    holds, because a ratio built from three teeth and a guess is not the quantity
    amendment 6 measured. With seven teeth this restricts the test to shifts of
    one slot, which is every offset the calibration record carries.

    The error is the one the page already draws. Each tooth height is given the
    scatter of its own fit residual, the shaded band under the height bars, so a
    pair mean carries that scatter over the square root of two and the ratio
    carries the two relative errors in quadrature. It is a conservative error,
    since a height is fitted from many samples rather than read off one, and it
    is deliberately the conservative one: on the weakest combs of the 70 °C block
    it is large enough to swallow the whole band, which is the true statement
    that those heights settle nothing.
    """
    h = _height_map(heights)
    need = (shift - 2, shift - 1, shift + 1, shift + 2)
    if not all(k in h for k in need):
        return None, None
    first = 0.5 * (h[shift - 1] + h[shift + 1])
    second = 0.5 * (h[shift - 2] + h[shift + 2])
    if first <= 0.0 or second <= 0.0:
        return None, None
    r = second / first
    sig = fit_rms / np.sqrt(2.0)
    err = r * float(np.hypot(sig / second, sig / first))
    return r, err


def ratio_agrees(ratio, err) -> bool:
    """Whether a second-to-first ratio is consistent with the measured band,
    which is the question the correction gate asks and the only one it asks."""
    if ratio is None:
        return False
    e = 0.0 if err is None else err
    return (ratio + e) >= RATIO_BAND[0] and (ratio - e) <= RATIO_BAND[1]


def ratio_state(ratio, err=None) -> str:
    """Where a second-to-first ratio sits against the measured band. These five
    words are the vocabulary of the correction gate and of nothing else."""
    if ratio is None:
        return "unavailable"
    e = 0.0 if err is None else err
    if ratio_agrees(ratio, e):
        return "inside"
    if ratio - e > RATIO_CROSSING:
        return "unphysical"
    if ratio > RATIO_BAND[1]:
        return "above"
    return "below"


def derive_tooth_shift(heights, fit_rms: float = 0.0):
    """The slot offset the tooth heights themselves imply, or None.

    Used only where the calibration record carries no offset. The criterion is
    the RATIO TEST and nothing else: try each whole-slot shift the seven teeth
    can carry, and take the one whose second-to-first ratio agrees with the
    measured band. Ties go to the ratio nearest the middle of the band. None
    means no shift repairs the ratio, which the page says rather than guesses.

    The carrier plays no part. An earlier version chose the shift that put a
    suppressed tooth between the two tallest, which fails on the ten combs of the
    campaign whose carrier stands above its own first-order pair.
    """
    mid = 0.5 * (RATIO_BAND[0] + RATIO_BAND[1])
    best = None
    for s in (-1, 1):
        r, e = second_to_first_ratio(heights, s, fit_rms)
        if not ratio_agrees(r, e):
            continue
        if best is None or abs(r - mid) < best[0]:
            best = (abs(r - mid), s)
    return None if best is None else best[1]


def _pct(a: str, b: str) -> str:
    """How closely two teeth match, in per cent, computed from the ROUNDED
    strings the page prints beside it. Every percentage on a page has to be
    reproducible from the numbers next to it, and a percentage computed from
    full precision and printed beside three decimal places is not.
    """
    x, y = float(a), float(b)
    if x + y <= 0:
        return ""
    return f"{200.0 * abs(x - y) / (x + y):.0f}"


def tooth_correction(rec, rl):
    """Whether the drawn tooth numbering differs from the fitted one, and why.

    Two gates, and they answer different questions. WHICH combs carry a displaced
    grid is `displaced_grid` above, the amplitude test of amendment 5 section E5.
    Whether a proposed correction is ACCEPTED is the RATIO TEST of amendment 6
    section F4: the corrected numbering has to bring the second-to-first height
    ratio from unphysical or displaced into the band the campaign measured. The
    carrier height enters neither, because it carries residual amplitude
    modulation and identifies nothing.

    Display only. The offset is preferred from the calibration record, which
    already holds the trial that rescued the labelling, and is otherwise read off
    the heights on this page. Neither route touches the spacing or the curve: a
    relabelling leaves the pitch where it was, so the comb fit is drawn exactly
    as it stands and only the numbers over the teeth move.
    """
    f = rec["fit"]
    if f is None:
        return None
    if not displaced_grid(f["heights"]):
        return None

    h = _height_map(f["heights"])
    rms = float(f["fit_rms"])
    r0, e0 = second_to_first_ratio(f["heights"], 0, rms)
    s0 = ratio_state(r0, e0)

    shift, source = 0, "none"
    for src in (rl, f):
        if src and str(src.get("reindex_action", "")) == "phase_shift":
            j = int(_num(src.get("reindex_j"), 0.0))
            if j:
                shift, source = j, "recorded"
                break
    if not shift:
        j = derive_tooth_shift(f["heights"], rms)
        if j:
            shift, source = j, "amplitudes"

    r1, e1 = (second_to_first_ratio(f["heights"], shift, rms) if shift else (None, None))
    accepted = bool(shift) and s0 != "inside" and ratio_agrees(r1, e1)

    ks, hs, kf, hf = forbidden_pair(f["heights"])
    said = (f"As the comb fit numbers the teeth, the second order tooth {_signed(ks)} "
            f"stands at {hs:.3f} V above the first order tooth {_signed(kf)} at "
            f"{hf:.3f} V, which no depth below 2β = {CROSSING_2BETA:.2f} produces.")
    if r0 is not None:
        said += (f" Its second to first height ratio is {r0:.3f} ± {e0:.3f}, against "
                 f"the measured {RATIO_BAND[0]:.3f} to {RATIO_BAND[1]:.3f}.")

    if s0 == "inside":
        # the error on the ratio reaches the band, so these heights decide nothing.
        # Every comb this catches is in the coldest block, where the teeth stand
        # barely above the fit residual.
        why = ("That error reaches the band, so these tooth heights are too small "
               "against the scatter of their own fit to settle the numbering, and "
               "the numbering drawn is the one the comb fit produced.")
        if shift:
            why += (f" The calibration record carries an offset of {_slots(shift)} "
                    "for this trace, which the heights here neither confirm nor "
                    "refuse.")
        return {"shift": 0, "source": "none", "state": s0, "outcome": "undecided",
                "ratio_before": r0, "lines": [said + " " + why]}

    if not accepted:
        why = ("No whole number of slots brings that ratio into the band, so the "
               "numbering drawn is the one the comb fit itself produced.")
        if shift and r1 is not None:
            why = (f"Counted {_slots(shift)} across the ratio is {r1:.3f} ± {e1:.3f}, "
                   "which still does not reach the band, so the correction is refused "
                   "and the numbering drawn is the one the comb fit produced.")
        return {"shift": 0, "source": "none", "state": s0, "outcome": "refused",
                "ratio_before": r0, "lines": [said + " " + why]}

    ha, hb = f"{h[shift - 1]:.3f}", f"{h[shift + 1]:.3f}"
    match = _pct(ha, hb)
    ev = (f"Counted {_slots(shift)} across, that ratio becomes {r1:.3f} ± {e1:.3f}, "
          f"which reaches the band, with a first order pair of {ha} and {hb} V")
    ev += f" matching to {match} per cent." if match else "."
    said = (f"Tooth numbering corrected by {_slots(shift)}. " + said + " " + ev
            + f" The comb fit gave the true carrier the name {_signed(shift)}.")
    if source == "recorded":
        prov = ("This is the offset the calibration record already carries for this "
                "trace. ")
    else:
        prov = ("The calibration record carries no offset for this trace, so this one "
                "is read off the tooth heights drawn beside it. The automatic repair "
                "had to refit the trace within a fixed cost before it would accept a "
                "new labelling, and a change of names on a drawing does not. ")
    prov += ("The tooth spacing and the drawn curve are the comb fit exactly as it "
             "stands, because renaming the teeth does not move their pitch.")
    return {"shift": shift, "source": source, "state": s0, "outcome": "corrected",
            "ratio_before": r0, "ratio_after": r1, "lines": [said, prov]}


def _slots(shift: int) -> str:
    return "one slot" if abs(shift) == 1 else f"{abs(shift)} slots"


# ---------------------------------------------------------------------------
# annotation: what the page says about each trace
# ---------------------------------------------------------------------------

def _condition_title(rec) -> str:
    """The observation a page is of, in the words a physicist would use to ask
    for it, with the class on it.

    Four names are used twice in the archive, once for a trace that was kept and
    once for a trace that was removed, so a title without the class names two
    different pictures. On a bracket comb the class is folded into the bracket,
    because "closing the session, power session" says the session twice.
    """
    row = rec["row"]
    T = int(float(row["temperature_C"]))
    tag = CLASS_TAG[rec["cls"]]
    if rec["kind"] == "comb":
        head = f"993.{row['peak']} nm calibration comb at {T} °C"
        if row["bracket"] and rec["cls"] in ("ruler_p", "ruler_t"):
            opening = row["bracket"] == "before"
            return head + (", opening the " if opening else ", closing the ") + tag
        if row["bracket"]:
            head += (", opening bracket" if row["bracket"] == "before"
                     else ", closing bracket")
    else:
        head = (f"993.{row['peak']} nm at {T} °C and "
                f"{int(round(power_w(row) * 1e3))} mW")
    return f"{head}, {tag}"


def _repeat_word(rec, i: int) -> str:
    idx = rec["row"]["repeat_idx"]
    return f"repeat {idx}" if idx else f"repeat {i + 1}"


def _split_flags(text: str) -> list:
    """The quality pass's note field, one note per entry.

    The separator is a semicolon, but a note also carries its own evidence in
    parentheses and that evidence can contain a semicolon of its own. Splitting
    on every semicolon tore one note in half and printed the tail of it as a note
    the page could not translate, which is the pipeline's raw text on a reader's
    picture.
    """
    parts, depth, cur = [], 0, []
    for ch in text or "":
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)
        if ch == ";" and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def _quality_notes(text: str) -> list:
    """The quality pass's own notes, in plain sentences, minus the redundant.

    A low signal to noise is already a number in the row's own stack, so its note
    is dropped rather than repeated. Anything this function does not recognise is
    reported as unrecognised, because silently dropping a note the record left
    would be the page hiding the table.
    """
    out = []
    for part in _split_flags(text):
        low = part.lower()
        if low.startswith("low-snr"):
            continue
        if "second structure" in low:
            out.append("a second structure sits in this trace, most likely the sweep "
                       "retrace crossing the line")
        elif "no comb" in low:
            out.append("no comb structure was found in this trace")
        elif "truncated" in low or "short/" in low:
            out.append("the export is short, so the sweep window is incomplete")
        elif "dropout" in low:
            out.append("the export drops samples")
        else:
            out.append("the quality pass left a note on this trace that this page "
                       "does not translate")
    return out


def _discard_reason(row) -> str:
    text = (row.get("qc_reason") or "").lower()
    for needle, word in DISCARD_WORD:
        if needle in text:
            return word
    return ""


def archive_census(manifest) -> dict:
    """How many traces the archive holds at each condition and how many of them
    the analysis keeps.

    Every number a page prints about curation is counted here from the manifest
    rather than typed into a sentence, so a curation note cannot drift away from
    the archive it describes.
    """
    by_cond = defaultdict(Counter)
    for r in manifest:
        by_cond[(r["session"], condition(r))][trace_class(r)] += 1
    return {"by_condition": by_cond,
            "by_class": Counter(trace_class(r) for r in manifest)}


def _curation_sentence(rec, census) -> str:
    """Who removed this trace, on what criterion, and out of how many."""
    why = _discard_reason(rec["row"])
    counts = census["by_condition"].get((rec["row"]["session"], rec["cond"]), Counter())
    n_all = sum(counts.values())
    n_gone = counts["discarded"] + counts["quarantine"]
    said = "The curator removed this trace from the analysis by hand before any fit ran"
    said += f", because it is {why}." if why else "."
    if n_all:
        said += (f" Of the {n_all} traces recorded at this wavelength, temperature and "
                 f"power, {n_all - n_gone} were kept and {n_gone} removed.")
    said += " The recording itself is still in the archive, and it is drawn here."
    return said


def annotate(rec, qc_rows, ruler_rows, census):
    """Attach the trim record, the exclusion marks and everything drawn as text."""
    row, f = rec["row"], rec["fit"]
    qc = qc_rows.get(rec["file"], {})
    rl = ruler_rows.get(rec["file"], {})
    is_comb = rec["kind"] == "comb"

    # The AUTHORITATIVE trim record. A ruler's lives in the ruler table and the
    # quality table deliberately reports it as not applicable there, so exactly
    # one record is read per trace and two records can never disagree on a page.
    src = rl if (is_comb and rl) else qc
    rec["trimmed"] = _truthy(src.get("trimmed"))
    rec["keep_lo"] = _num(src.get("trim_start_ms"))
    rec["keep_hi"] = _num(src.get("trim_end_ms"))
    rec["trim_reason"] = src.get("trim_reason", "")
    rec["trim_source"] = ("the ruler ladder" if src is rl and rl
                          else "the quality pass" if src else "no record")
    rec["has_ruler_row"] = bool(rl)
    rec["snr"] = _num(qc.get("snr"))

    rec["outlier"] = _truthy(qc.get("outlier")) or _truthy(rl.get("outlier"))
    rec["outlier_reason"] = (rl.get("outlier_reason") or qc.get("outlier_reason") or "")
    rec["quarantined"] = _truthy(rl.get("quarantined"))
    rec["quarantine_advised"] = _truthy(rl.get("quarantine_advised"))
    rec["quarantine_reason"] = rl.get("quarantine_reason", "")

    marks = []
    if rec["outlier"]:
        marks.append(("outlier", "Left out of its group average: "
                      + (OUTLIER_WORD.get(rec["outlier_reason"])
                         or rec["outlier_reason"] or "no reason recorded") + "."))
    if rec["quarantined"]:
        marks.append(("quarantined", "Out of the frequency calibration: "
                      + (CARRIER_WORD.get(rec["quarantine_reason"])
                         or rec["quarantine_reason"] or "no reason recorded") + "."))
    elif rec["quarantine_advised"]:
        marks.append(("advised", "Marked for removal from the frequency calibration "
                      "and still inside it: "
                      + (CARRIER_WORD.get(rec["quarantine_reason"])
                         or rec["quarantine_reason"] or "no reason recorded") + "."))
    if rec["cls"] == "discarded":
        marks.append(("excluded", _curation_sentence(rec, census)))
    if rec["fit_note"]:
        marks.append(("excluded", rec["fit_note"][0].upper() + rec["fit_note"][1:] + "."))
    rec["marks"] = marks

    # A curve is FITTED HERE when it was fitted to this trace. A comb fit always
    # is. A line drawn outside the canonical population is the shared archive
    # model with three nuisances matched to it, which is a different thing and is
    # said once on the page rather than three times.
    rec["fitted_here"] = f is not None and (is_comb or rec["cls"] == "canonical")
    rec["tooth"] = tooth_correction(rec, rl) if is_comb else None

    notes = list(marks)
    if rec["trimmed"]:
        said = ("Samples "
                + (TRIM_WORD.get(rec["trim_reason"]) or rec["trim_reason"])
                + f", keeping {_ms(rec['keep_lo'])} to {_ms(rec['keep_hi'])} ms.")
        # On a line the two guards act in a fixed order and the window gets there
        # first, so saying only that samples were cut invites the reading that the
        # line fit saw them and threw them out. It usually never saw them.
        if (not is_comb) and rec["used"] is not None:
            cut = (rec["t"] < rec["keep_lo"]) | (rec["t"] > rec["keep_hi"])
            both = int(np.count_nonzero(cut & rec["used"]))
            if both == 0:
                said += (" All of them lie outside the window the line fit was asked "
                         "about, so the line fit never saw them.")
            else:
                said += (f" {both} of them lie inside the window the line fit was "
                         "asked about.")
        notes.append(("trim", said))
    for note in _quality_notes(qc.get("hard_flags", "")):
        notes.append(("excluded", note[0].upper() + note[1:] + "."))
    rec["notes"] = notes

    # Every internal code the page dropped, kept recoverable in one place: the
    # index, one fold-out per trace. The page foot carries the source, the tables
    # and the regenerate command only.
    codes = [f"class={rec['cls']}", f"condition={rec['cond']}",
             f"role={row['role']}", f"flag={row['flag']}",
             f"session={row['session']}", f"rf_on={row['rf_on']}",
             f"bracket={row['bracket'] or '-'}", f"repeat_idx={row['repeat_idx']}"]
    for key in ("snr", "height_v", "fwhm_ms", "peak_pos_ms", "edge_margin_ms",
                "z_spike", "z_step", "lf_ratio", "comb_score", "outlier",
                "outlier_reason", "hard_flags"):
        if key in qc:
            codes.append(f"{key}={qc[key] or '-'}")
    codes.append(f"trim_source={rec['trim_source']} trimmed={rec['trimmed']} "
                 f"trim_reason={rec['trim_reason'] or '-'}")
    if is_comb and f is not None:
        codes.append(
            f"delta_ms={f['delta_ms']:.6f} delta_err_ms={f['delta_err_ms']:.6f} "
            f"width_ms={f['width_ms']:.3f} chi2_red={f['chi2_red']:.4f} "
            f"fit_rms={f['fit_rms']:.5f} n_fitted={f['n_fitted']} "
            f"t0_ms={f['t0_ms']:.4f} verdict={f['verdict']} "
            f"top3_ok={f['top3_ok']} rank_m1={f['rank_m1']} rank_p1={f['rank_p1']} "
            f"n_railed={f['n_railed']} reindex_action={f['reindex_action']} "
            f"reindex_j={f['reindex_j']} excised_k={f['excised_k'] or '-'} "
            f"n_refits={f['n_refits']} top3_gated={f['top3_gated']}")
        codes.append("heights=" + " ".join(f"h_{k:+d}={hh:.4f}"
                                           for k, hh in zip(TEETH, f["heights"])))
        r0, e0 = second_to_first_ratio(f["heights"], 0, float(f["fit_rms"]))
        codes.append(f"second_to_first={r0 if r0 is None else round(r0, 5)} "
                     f"+-{e0 if e0 is None else round(e0, 5)} "
                     f"ratio_state={ratio_state(r0, e0)} "
                     f"ratio_band={RATIO_BAND[0]:.5f}..{RATIO_BAND[1]:.5f}")
    if rl:
        codes.append(
            f"recorded delta_ms={_num(rl.get('delta_ms')):.6f} "
            f"rate_MHzms={_num(rl.get('rate_MHzms')):.6f} "
            f"verdict={rl.get('verdict', '-')} "
            f"reindex_action={rl.get('reindex_action', '-')} "
            f"reindex_j={rl.get('reindex_j', '-')} "
            f"delta_advised_ms={_num(rl.get('delta_advised_ms')):.6f} "
            f"quarantine_advised={rl.get('quarantine_advised', '-')} "
            f"quarantine_reason={rl.get('quarantine_reason') or '-'}")
    if rec["tooth"]:
        codes.append(f"drawn_tooth_shift={rec['tooth']['shift']:+d} "
                     f"shift_source={rec['tooth']['source']}")
    if (not is_comb) and f is not None:
        codes.append(
            f"gamma_coll={f['gc']:.4f} sigma_laser={f['sl']:.4f} "
            f"transit={f['transit']:.4f} stark_scale={f['s0']:.4f} "
            f"centre_MHz={f['cc']:.4f}+-{f['cc_err']:.4f} amplitude={f['A']:.5f} "
            f"chi2_red={f['chi2_red']:.4f} dof={f['dof']} fwhm_MHz={f['fwhm']:.4f} "
            f"halfwidth_MHz={rec['halfwidth']:.3f}")
    rec["codes"] = codes
    return rec


# ---------------------------------------------------------------------------
# the page: header, rows, footer
# ---------------------------------------------------------------------------

def _wrap_width(width_in: float) -> int:
    """Characters to a line of note, from the width of the page it is set on.
    The notes used to be wrapped to a fixed 118 in a column wide enough for
    about 160, which cost a quarter of the lines for nothing."""
    return int(0.88 * width_in * 72.0 / 4.8)


NOTE_PT = 8.4
NOTE_LINE_IN = NOTE_PT * 1.34 / 72.0
NOTE_GAP_IN = 0.058
"""Blank space between one note and the next. Without it the note stack was set
solid at exactly one line height per line, so a three line note about one repeat
and a one line note about the next ran together as a single paragraph."""
FOOT_PT = 7.2
FOOT_LINE_IN = FOOT_PT * 1.34 / 72.0


def _note_blocks(page, width_in: float) -> list:
    """Every note of a page, already wrapped, in drawing order. Used by the
    drawing routine and by the height calculation, so the space reserved for the
    notes and the space they take cannot disagree."""
    return [(kind, textwrap.wrap(msg, _wrap_width(width_in)) or [""])
            for kind, msg in page["notes"]]


def _notes_inches(page, width_in: float) -> float:
    blocks = _note_blocks(page, width_in)
    if not blocks:
        return 0.0
    return (sum(len(b) for _, b in blocks) * NOTE_LINE_IN
            + (len(blocks) - 1) * NOTE_GAP_IN)


def _stat_block(fig, x, y, items, label_size=7.4, value_size=11.5, dy_in=0.62):
    """A column of label-over-value pairs: the number large, its name small and
    quiet above it. Spacing in inches so it does not stretch with the page."""
    H = fig.get_figheight()
    for i, (label, value) in enumerate(items):
        yy = y - i * dy_in / H
        fig.text(x, yy, label, fontsize=label_size, color=FAINT, ha="left", va="top")
        fig.text(x, yy - 0.163 / H, value, fontsize=value_size, color=INK,
                 ha="left", va="top", fontweight="medium")


def _draw_header(fig, page) -> None:
    """Title, subtitle, rule and the two labelled columns, all positioned in
    INCHES from the top so the block does not stretch or collide when the page
    grows a row."""
    H, W = fig.get_figheight(), fig.get_figwidth()

    def y(inches):
        return 1.0 - inches / H

    fig.text(0.055, y(0.42), page["title"], fontsize=15.5, color=INK, ha="left",
             va="top", fontweight="semibold")
    fig.text(0.055, y(0.74), page["subtitle"], fontsize=9.6, color=MUTED, ha="left",
             va="top")
    fig.add_artist(plt.Line2D([0.055, 0.955], [y(1.04), y(1.04)],
                              transform=fig.transFigure, color=RULE, lw=0.8))
    right_x = 0.055 + 4.55 / W
    fig.text(0.055, y(1.26), "what was measured", fontsize=7.8, color=MUTED,
             ha="left", va="top", fontweight="semibold")
    fig.text(right_x, y(1.26), page["right_label"], fontsize=7.8, color=MUTED,
             ha="left", va="top", fontweight="semibold")
    _stat_block(fig, 0.055, y(1.52), page["left_items"])
    _stat_block(fig, right_x, y(1.52), page["right_items"])

    yy = y(STATS_IN)
    for kind, wrapped in _note_blocks(page, W):
        fig.text(0.055, yy, "\n".join(wrapped), fontsize=NOTE_PT, va="top", ha="left",
                 color=NOTE_COLOR.get(kind, "0.38"), linespacing=1.34)
        yy -= (NOTE_LINE_IN * len(wrapped) + NOTE_GAP_IN) / H


NOTE_COLOR = dict(MARK_COLOR, trim=TRIM_SHADE, plain="0.38", **RELABEL_COLOR)
"""Which colour a note under the header is set in. A removal the record left
takes the mark palette, a tooth-numbering note takes its own, and the sentences
true of every comb rather than of this one are grey."""

STATS_IN = 3.42
"""Where the notes start, in inches from the top of the page: below the title,
the rule and a three deep stack of labelled values."""


TAIL_IN = {"comb": 0.62, "line": 0.34}
"""What is reserved below the last note, before the first row's axes begin. A
comb row carries a tooth-order axis ACROSS ITS TOP, whose tick labels and axis
title stand about a third of an inch above the frame, so a comb page needs
nearly twice the tail a line page does. At the single 0.34 the comb pages spent
their tooth-order title on top of the last page note."""


def header_inches(page, width_in: float) -> float:
    tail = TAIL_IN.get(page["kind"], 0.34)
    if not page["notes"]:
        return 3.05 + tail          # nothing to say, so no empty band to say it in
    return STATS_IN + _notes_inches(page, width_in) + tail


def _footer(fig, lines) -> None:
    fig.text(0.055, 0.22 / fig.get_figheight(), "\n".join(lines), fontsize=FOOT_PT,
             color=FAINT, ha="left", va="bottom", linespacing=1.34)


def _footer_lines(page, version: str, width_in: float) -> list:
    body = " ".join(page["footer"])
    tail = (f"Source data_raw, model {page['module']}, annotated against "
            f"{page['tables']}. Redraw with python scripts/make_qc_gallery.py. "
            f"rb5s6s v{version}, inspection gallery, not a citable figure.")
    return (textwrap.wrap(body, _wrap_width(width_in) + 18)
            + textwrap.wrap(tail, _wrap_width(width_in) + 18))


def trim_spans(rec) -> list:
    """The stretches of sweep the search for a drifting residual tail cut, in
    MILLISECONDS, which is the unit the record keeps them in."""
    if not rec["trimmed"]:
        return []
    t = rec["t"]
    lo, hi = rec["keep_lo"], rec["keep_hi"]
    spans = []
    if np.isfinite(lo) and lo > t[0]:
        spans.append((float(t[0]), float(lo)))
    if np.isfinite(hi) and hi < t[-1]:
        spans.append((float(hi), float(t[-1])))
    return spans


def _shade_trim(ax, rec, to_x) -> None:
    """Shade those stretches on an axis, THROUGH the page's own horizontal
    coordinate. A page that reads in detuning and a record that reads in
    milliseconds are two different axes, and shading one with the other put the
    band the width of the page away from the samples it described."""
    for a, b in trim_spans(rec):
        ax.axvspan(to_x(a), to_x(b), color=TRIM_SHADE, alpha=0.20, lw=0, zorder=0)


def standing_teeth(fit) -> int:
    """How many of the seven fitted teeth stand above the scatter of the fit's own
    residual. It is the number the six-standing question turns on, and it is
    reproducible from the seven heights and the one scatter the page prints."""
    return int(sum(1 for h in fit["heights"] if float(h) > float(fit["fit_rms"])))


def _row_values(rec, is_comb) -> list:
    """The numbers in a row's own stack, each named and united."""
    f = rec["fit"]
    vals = []
    if is_comb and f is not None:
        vals.append(("tooth spacing", f"{f['delta_ms']:.2f} ± {f['delta_err_ms']:.2f} ms"))
        vals.append(("sweep rate, laser axis",
                     f"{TOOTH_SPACING_LASER_HZ / 1e6 / f['delta_ms']:.5f} MHz/ms"))
        vals.append(("residual scatter", f"{1000 * f['fit_rms']:.2f} mV"))
        vals.append(("teeth above that scatter",
                     f"{standing_teeth(f)} of {len(TEETH)}"))
        vals.append(("reduced chi-squared", f"{f['chi2_red']:.2f}"))
    elif f is not None:
        used = rec["used"]
        # the height of the curve the page actually draws, not the fit's
        # unsaturated amplitude: at 25 mW those two differ by a factor of seven,
        # and printing the second beside a peak that reaches the first reads as
        # the page contradicting its own picture
        peak = f["Vs"] * (1.0 - np.exp(-f["lin_peak"] / f["Vs"]))
        vals.append(("height of the drawn line", f"{peak:.4f} V"))
        vals.append(("width at half maximum", f"{f['fwhm']:.2f} MHz"))
        vals.append(("residual scatter",
                     f"{1000 * float(np.std(rec['raw_resid'][used])):.2f} mV"))
        if rec["fitted_here"]:
            vals.append(("reduced chi-squared", f"{f['chi2_red']:.2f}"))
    else:
        if np.isfinite(rec["snr"]):
            vals.append(("signal to noise", f"{rec['snr']:.0f}"))
        vals.append(("model", "not drawn"))
    return vals


def draw_page(page, version: str, dest_dir: str, dest_name: str) -> None:
    """One condition, every repeat as a row, one shared vertical scale."""
    recs = page["recs"]
    is_comb = page["kind"] == "comb"
    n = len(recs)

    W = 13.7 if is_comb else 11.7
    row_in = 2.35 if is_comb else 1.95
    head_in = header_inches(page, W)
    foot_in = 0.92 + FOOT_LINE_IN * len(_footer_lines(page, version, W))
    H = row_in * n + head_in + foot_in

    fig = plt.figure(figsize=(W, H))
    ncols = 3 if is_comb else 2
    ratios = [2.00, 1.05, 1.05] if is_comb else [2.05, 1.15]
    gs = GridSpec(n, ncols, figure=fig, left=0.150, right=0.812,
                  top=1.0 - head_in / H, bottom=foot_in / H,
                  hspace=0.62 if is_comb else 0.30,
                  width_ratios=ratios, wspace=0.30 if is_comb else 0.20)

    _draw_header(fig, page)

    # One horizontal axis for the whole page. A line page reads in detuning from
    # each trace's own centre, which is the comparison the page is for, but only
    # if every row has a centre to measure from: one row in time and the rest in
    # frequency under a single axis label would be a lie about the page.
    detuning = (not is_comb) and all(r["model"] is not None for r in recs)
    xlabel = ("detuning from this trace's own line centre (MHz)" if detuning
              else "time through the sweep (ms)")

    # ---- the one vertical scale for the whole page, on both columns ----
    drawn = [r for r in recs if r["model"] is not None]
    sig_lo = min(float(np.min(r["v"])) for r in recs)
    sig_hi = max(float(np.max(r["v"])) for r in recs)
    pad = 0.07 * (sig_hi - sig_lo) if sig_hi > sig_lo else 1.0
    # the residual scale is set on the FITTED samples: letting the excluded tail
    # set it would squash the residual the fit is actually judged on
    res_hi = 1.2
    for r in drawn:
        u = r["used"]
        if np.any(u):
            res_hi = max(res_hi, float(np.max(np.abs(r["resid"][u]))))
    bar_hi = 0.0
    for r in drawn:
        if is_comb and r["fit"] is not None:
            bar_hi = max(bar_hi, float(np.max(r["fit"]["heights"])),
                         float(r["fit"]["fit_rms"]))

    # ---- and the one horizontal scale, for the same reason ----
    def row_x(rec):
        if detuning:
            return rec["nu"] - rec["centre"]
        return rec["t"]

    x_lo = min(float(np.min(row_x(r))) for r in recs)
    x_hi = max(float(np.max(row_x(r))) for r in recs)
    if is_comb:
        for r in drawn:
            if r["fit"] is not None:
                f = r["fit"]
                edge = 0.35 * f["delta_ms"]
                x_lo = min(x_lo, f["t0_ms"] + min(TEETH) * f["delta_ms"] - edge)
                x_hi = max(x_hi, f["t0_ms"] + max(TEETH) * f["delta_ms"] + edge)
    x_pad = 0.02 * (x_hi - x_lo)

    for i, rec in enumerate(recs):
        f = rec["fit"]
        shift = rec["tooth"]["shift"] if rec.get("tooth") else 0
        t, v = rec["t"], rec["v"]
        ax = fig.add_subplot(gs[i, 0])
        axr = fig.add_subplot(gs[i, 1])

        x = row_x(rec)

        def to_x(ms, rec=rec):
            """A time in the record's milliseconds, in this page's horizontal
            coordinate, so a band read off the record lands on the samples it
            belongs to."""
            if not detuning:
                return ms
            return float(to_frequency(np.asarray([ms]), rec["rate"])[0]) - rec["centre"]

        used = rec["used"] if rec["used"] is not None else np.ones(len(v), dtype=bool)
        ax.plot(x[~used], v[~used], ".", ms=1.0, color=UNFIT, rasterized=True)
        ax.plot(x[used], v[used], ".", ms=1.1, color=DATA, rasterized=True)
        if rec["model"] is not None:
            ax.plot(x[used], rec["model"][used], "-", color=page["curve"], lw=1.4)
            axr.plot(x[~used], rec["resid"][~used], ".", ms=0.9, color=UNFIT,
                     rasterized=True)
            axr.plot(x[used], rec["resid"][used], ".", ms=1.0, color=DATA,
                     rasterized=True)
        if rec["win"] is not None and not np.all(used) and detuning:
            for e in rec["win"]:
                ax.axvline(e - rec["centre"], color=EDGE, lw=0.9, ls=(0, (4, 3)))
                axr.axvline(e - rec["centre"], color=EDGE, lw=0.9, ls=(0, (4, 3)))
        axr.axhline(0.0, color=page["curve"], lw=0.9)
        # a shaded band of one point error rather than dashed rules, so the eye
        # reads "inside the noise" as an area and not as a threshold to cross
        axr.axhspan(-1.0, 1.0, color="0.5", alpha=0.15, lw=0, zorder=0)
        _shade_trim(ax, rec, to_x)
        _shade_trim(axr, rec, to_x)
        ax.set_xlim(x_lo - x_pad, x_hi + x_pad)
        axr.set_xlim(x_lo - x_pad, x_hi + x_pad)
        ax.set_ylim(sig_lo - pad, sig_hi + pad)
        axr.set_ylim(-1.10 * res_hi, 1.10 * res_hi)
        ax.set_ylabel("signal (V)")
        axr.set_ylabel("residual, in units\nof the point error")
        if i == n - 1:
            ax.set_xlabel(xlabel)
            axr.set_xlabel(xlabel)
        else:
            ax.set_xticklabels([])
            axr.set_xticklabels([])

        # ---- the tooth order, on its own axis across the top of the row ----
        if is_comb and f is not None:
            centres = [(k, f["t0_ms"] + k * f["delta_ms"]) for k in TEETH]
            for _, c in centres:
                ax.axvline(c, color="0.35", lw=0.6, ls=":", alpha=0.7, zorder=0)
            axk = ax.twiny()
            axk.set_xlim(ax.get_xlim())
            axk.set_xticks([c for _, c in centres])
            axk.set_xticklabels([_signed(k - shift) for k, _ in centres], fontsize=8.0)
            # The corrected numbering never hides the fitted one, and the
            # sentence that says so rides on the axis title rather than floating
            # above it. As a separate line at 1.30 of the axes height it stood
            # higher than the header reserved room for, and on every page whose
            # first row carries a correction it printed through the last page
            # note.
            axk.set_xlabel(
                ("tooth order, corrected: the comb fit numbers each tooth "
                 f"{_signed(shift)} from this" if shift else "tooth order"),
                fontsize=8.5, labelpad=2)
            axk.tick_params(length=2.5)
            axk.grid(False)
            for label, (_, c) in zip(axk.get_xticklabels(), centres):
                if not (t[0] <= c <= t[-1]):
                    label.set_color("0.62")

        # ---- the tooth heights, against this fit's own residual scatter ----
        if is_comb:
            axh = fig.add_subplot(gs[i, 2])
            if f is not None:
                order = [k - shift for k in TEETH]
                h = np.asarray(f["heights"], dtype=float)
                rms = float(f["fit_rms"])
                # the scatter is a BAND from zero and NOT a rule across the bars:
                # as a rule it struck the height labels through wherever a tooth
                # happened to stand near it. A tooth that does not clear the band
                # is drawn hollow as well, because on the strongest combs the band
                # is two per cent of the axis and whether the outermost tooth
                # stands above it is the whole question a reader comes here with.
                for k, hk in zip(order, h):
                    face = FIRST_ORDER if abs(k) == 1 else "0.62"
                    stands = hk > rms
                    axh.bar([k], [hk], width=0.62,
                            color=face if stands else "white",
                            edgecolor=face, linewidth=0.9 if stands else 1.1,
                            hatch=None if stands else "///")
                axh.axhspan(0.0, rms, color=TRIM_SHADE, alpha=0.22, lw=0, zorder=0)
                top = max(bar_hi, float(h.max())) * 1.30
                axh.set_ylim(0.0, top if top > 0 else 1.0)
                for k, hk in zip(order, h):
                    axh.text(k, hk + 0.018 * top, f"{hk:.3f}", fontsize=6.4,
                             ha="center", va="bottom", rotation=90,
                             color="0.28" if hk > rms else TRIM_SHADE)
                # The caption for this column is a page note, not a row label. Set
                # under every row it ran the width of the column and printed
                # through the numbers stacked to its right, and it says the same
                # thing five times over: what varies row to row is the scatter and
                # the count, and both of those are in the row's own stack.
                axh.set_xlabel("tooth height (V) by "
                               + ("corrected order" if shift else "order"),
                               fontsize=8.0)
            else:
                axh.set_xlabel("no comb fit converged on this trace", fontsize=8.0)
            axh.set_xticks([k - shift for k in TEETH])
            axh.set_xticklabels([_signed(k - shift) for k in TEETH], fontsize=7.5)
            axh.tick_params(labelsize=7.5)

        # ---- the gutter, and the row's own numbers ----
        pos = ax.get_position()
        fig.text(0.020, pos.y1 - 0.002, _repeat_word(rec, i), fontsize=9.4, color=INK,
                 ha="left", va="top", fontweight="semibold")
        # THE CLASS IS PART OF THE ROW LABEL. Four file stems sit in two classes
        # at once, each with the same repeat number in both, so "repeat 4" over
        # "4154nm_070c4" names the analysed trace on one page and the curation
        # copy on another. The class in words settles which, the way it already
        # settles which of two pages of the same name a reader is looking at.
        gy = 0.20
        ident = [ln for part in (_stem(rec["row"]["file"]),
                                 CLASS_TAG.get(rec["cls"], rec["cls"]))
                 for ln in (textwrap.wrap(part, 26) or [""])]
        fig.text(0.020, pos.y1 - gy / H, "\n".join(ident), fontsize=6.6,
                 color=FAINT, ha="left", va="top", linespacing=1.3)
        gy += 0.123 * len(ident) + 0.058
        if rec["marks"]:
            fig.text(0.020, pos.y1 - gy / H,
                     "\n".join(textwrap.wrap(page["gutter_word"][i], 22)),
                     fontsize=6.6, color=MARK_COLOR[rec["marks"][0][0]], ha="left",
                     va="top", linespacing=1.3)
        _stat_block(fig, 0.826, pos.y1 - 0.002, _row_values(rec, is_comb),
                    label_size=6.6, value_size=8.8, dy_in=0.40)

    _footer(fig, _footer_lines(page, version, W))
    save_png(fig, dest_dir, dest_name)


GUTTER_WORD = {"outlier": "out of its group average",
               "quarantined": "out of the calibration",
               "advised": "marked for removal",
               "excluded": "enters no fit"}


def build_page(cls, cond, recs, census, version):
    """Everything the page draws, decided once, before any axis exists."""
    recs = sorted(recs, key=lambda r: r["file"])
    head = recs[0]
    is_comb = head["kind"] == "comb"
    row = head["row"]
    n = len(recs)
    fits = [r["fit"] for r in recs if r["fit"] is not None]

    left = [("spectral line", f"993.{row['peak']} nm"),
            ("cell temperature", f"{int(float(row['temperature_C']))} °C")]
    if is_comb:
        left.append(("phase modulation depth",
                     f"2β = {MOD_DEPTH_2BETA:.3f} radians"))
    else:
        left.append(("optical power", f"{int(round(power_w(row) * 1e3))} mW"))

    corrected = [r for r in recs if r.get("tooth") and r["tooth"]["shift"]]
    if is_comb:
        right_label = "what the comb fits found"
        if fits:
            d = float(np.mean([f["delta_ms"] for f in fits]))
            right = [("tooth spacing, mean of the repeats", f"{d:.2f} ms"),
                     ("sweep rate on the laser axis, mean",
                      f"{TOOTH_SPACING_LASER_HZ / 1e6 / d:.5f} MHz/ms"),
                     ("repeats with a corrected numbering", f"{len(corrected)} of {n}")]
        else:
            right = [("comb fit", "none converged on this page")]
    elif head["cls"] == "canonical":
        right_label = "what the shared fit found"
        right = ([("collisional width", f"{fits[0]['gc']:.2f} MHz"),
                  ("laser line width", f"{fits[0]['sl']:.2f} MHz"),
                  ("transit broadening", f"{fits[0]['transit']:.2f} MHz")]
                 if fits else [("shared fit", "no model available here")])
    else:
        right_label = "what the archive model gives here"
        right = ([("collisional width", f"{fits[0]['gc']:.2f} MHz"),
                  ("laser line width", f"{fits[0]['sl']:.2f} MHz"),
                  ("transit broadening", f"{fits[0]['transit']:.2f} MHz")]
                 if fits else [("archive model", "not available here")])

    title = _condition_title(head)
    where = SESSION_WORD.get(row["session"], "session not recorded")
    plural = "repeat of one condition" if n == 1 else "repeats of one condition"
    # the session goes in the subtitle only when the title has not already said
    # it, or the page reads "temperature session" twice in two lines
    subtitle = (f"{n} {plural}" if (row["bracket"] or where in title)
                else f"{where}, {n} {plural}")

    notes = []
    if cls == "quarantine":
        notes.append(("excluded", "Every trace on this page belongs to the aborted "
                      "first session, which is set aside whole: all "
                      f"{census['by_class']['quarantine']} of its traces enter no "
                      "fit."))
    if (not is_comb) and any(r["fit"] is not None and not r["fitted_here"]
                             for r in recs):
        notes.append(("excluded", "The curve drawn on each row is the shared archive "
                      "line model with only its height, centre and background matched "
                      "to that trace, so no goodness of fit is quoted for it."))
    # A note every repeat carries is a note about the page. Printed once per row
    # it filled six lines with one sentence five times and buried the notes that
    # belonged to a single trace.
    shared = [nt for nt in recs[0]["notes"]
              if n > 1 and all(nt in r["notes"] for r in recs[1:])]
    for kind, msg in shared:
        notes.append((kind, msg))
    for i, rec in enumerate(recs):
        for kind, msg in rec["notes"]:
            if (kind, msg) in shared:
                continue
            notes.append((kind, f"{_repeat_word(rec, i).capitalize()}. {msg}"))
        if rec.get("tooth"):
            src = rec["tooth"]["source"]
            for j, line in enumerate(rec["tooth"]["lines"]):
                head_word = f"{_repeat_word(rec, i).capitalize()}. " if j == 0 else ""
                notes.append((src if src != "none" else "none", head_word + line))
    if is_comb:
        notes.append(("plain", BAR_KEY_SENTENCE))
        notes.append(("plain", DEPTH_SENTENCE))
        notes.append(("plain", CARRIER_SENTENCE))
        if any(r.get("tooth") for r in recs):
            notes.append(("plain", GATE_SENTENCE))
        notes.append(("plain", GREY_TICK_SENTENCE))

    footer = ["Every repeat of one condition, on one shared vertical scale, so two "
              "rows that differ cannot look alike."]
    if is_comb:
        footer.append("Each residual is standardized: every sample divided by the "
                      "error the comb fit weighted it with, under a shaded band of "
                      "one point error. Adjacent teeth are "
                      f"{TOOTH_SPACING_LASER_HZ / 1e6:.2f} MHz apart on the laser "
                      "frequency axis, which is what turns a spacing into a sweep "
                      "rate.")
    else:
        footer.append("Each residual is standardized: every sample divided by the "
                      "error the fit weighted it with, under a shaded band of one "
                      "point error, because the raw noise grows with signal level and "
                      "a raw strip bulges at the line centre for that reason alone. "
                      "Dashed lines mark the edges of the window the fit was asked "
                      "about, set from each trace's own width, and the paler points "
                      "outside it are recorded but not fitted, which is where the "
                      "sweep retrace re-crosses the line.")
    if any(r["trimmed"] for r in recs):
        footer.append("A shaded vertical band marks the stretch of sweep the search "
                      "for a drifting residual tail cut.")

    tables = "results/qc_metrics.csv"
    if any(r["has_ruler_row"] for r in recs):
        tables += " and results/ruler_traces.csv"

    return {"cls": cls, "cond": cond, "kind": head["kind"], "recs": recs,
            "title": title, "subtitle": subtitle,
            "left_items": left, "right_items": right, "right_label": right_label,
            "notes": notes, "footer": footer, "tables": tables,
            "module": "rb5s6s.ruler" if is_comb else "rb5s6s.linefit",
            "curve": PEAK_COLOR.get(row["peak"], "#444444"),
            "gutter_word": [GUTTER_WORD.get(r["marks"][0][0], "") if r["marks"] else ""
                            for r in recs],
            "name": page_name(cls, cond, version)}


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

def write_index(pages, version: str) -> Path:
    e = html.escape
    records = [r for p in pages for r in p["recs"]]
    parts = ["<!doctype html>", "<meta charset='utf-8'>",
             f"<title>rb5s6s inspection gallery v{e(version)}</title>",
             "<style>",
             "body{font:14px/1.5 -apple-system,Segoe UI,Helvetica,Arial,sans-serif;",
             "margin:2rem auto;max-width:64rem;padding:0 1rem;color:#1b1b1b}",
             "h1{font-size:1.6rem}h2{margin-top:2.4rem;border-bottom:1px solid #ddd}",
             "h3{margin:1.4rem 0 .4rem;font-size:1rem;color:#333}",
             "table{border-collapse:collapse;width:100%;font-size:12.5px}",
             "td,th{border-bottom:1px solid #eee;padding:.28rem .4rem;text-align:left;",
             "vertical-align:top}", "img{max-width:100%;border:1px solid #ddd}",
             ".mark{font-weight:600}",
             *(f".{k}{{color:{v}}}" for k, v in MARK_COLOR.items()),
             f".trim{{color:{TRIM_SHADE}}}",
             "code{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px}",
             "details{margin:.2rem 0}summary{cursor:pointer;color:#555}",
             "pre{white-space:pre-wrap;font-size:11px;color:#444;margin:.3rem 0 0}",
             "</style>",
             f"<h1>Inspection gallery, {len(pages)} conditions, "
             f"{len(records)} traces, v{e(version)}</h1>",
             "<p>One page per condition, every repeat of it as a row, on one shared "
             "vertical scale. Each row carries the signal with the drawn model and "
             "the residual standardized by the error the fit weighted each sample "
             "with, under a shaded band of one point error. Shaded vertical bands are "
             "samples cut by the search for a drifting residual tail. Coloured notes "
             "under the header are removals the record left: a trace left out of its "
             "group average, a comb out of the frequency calibration, a comb marked "
             "for removal and still inside it, or a class that enters no fit.</p>",
             "<p>The tooth numbering on a comb page is corrected wherever the heights "
             f"say it is displaced and a whole slot repairs it. {e(DEPTH_SENTENCE)} "
             f"{e(CARRIER_SENTENCE)} A correction is accepted only when it brings the "
             "second to first height ratio into the measured band of "
             f"{RATIO_BAND[0]:.3f} to {RATIO_BAND[1]:.3f}, within the error that the "
             "scatter of the comb's own fit puts on that ratio, and the numbering the "
             "comb fit produced is kept on the page beside the corrected one. The "
             "fitted spacing and the drawn curve are untouched.</p>",
             "<p>This is an audit, not a citable figure set. Nothing here is tracked, "
             "nothing here carries a data fingerprint, and nothing here gates "
             "anything. Regenerate with "
             "<code>python scripts/make_qc_gallery.py</code>.</p>"]

    parts.append("<h2>The five classes</h2><table><tr><th>class</th><th>what it is"
                 "</th><th>pages</th><th>traces</th><th>samples cut</th>"
                 "<th>marked</th></tr>")
    for cls in CLASSES:
        ps = [p for p in pages if p["cls"] == cls]
        rs = [r for p in ps for r in p["recs"]]
        parts.append(f"<tr><td><a href='#{e(cls)}'>{e(CLASS_TITLE[cls])}</a></td>"
                     f"<td>{e(CLASS_BLURB[cls])}</td><td>{len(ps)}</td>"
                     f"<td>{len(rs)}</td>"
                     f"<td>{sum(1 for r in rs if r['trimmed'])}</td>"
                     f"<td>{sum(1 for r in rs if r['marks'])}</td></tr>")
    parts.append("</table>")

    for cls in CLASSES:
        ps = [p for p in pages if p["cls"] == cls]
        if not ps:
            continue
        parts.append(f"<h2 id='{e(cls)}'>{e(CLASS_TITLE[cls])}: "
                     f"{e(CLASS_BLURB[cls])}</h2>")
        for page in ps:
            rel = f"{cls}/{page['name']}"
            parts.append(f"<h3>{e(page['title'])}</h3>"
                         f"<p><a href='{e(rel)}'>{e(page['subtitle'])}</a></p>"
                         f"<p><img src='{e(rel)}' alt='{e(page['title'])}'></p>"
                         "<table><tr><th>trace</th><th>samples cut</th>"
                         "<th>tooth numbering</th><th>marks</th></tr>")
            for rec in page["recs"]:
                word = TRIM_WORD.get(rec["trim_reason"], rec["trim_reason"])
                trim = (f"<span class='trim'>{e(word)}, keeping "
                        f"{_ms(rec['keep_lo'])} to {_ms(rec['keep_hi'])} ms</span>"
                        if rec["trimmed"] else e(word))
                tooth = ""
                if rec.get("tooth"):
                    s, src = rec["tooth"]["shift"], rec["tooth"]["source"]
                    tooth = {"undecided": "displaced, and the heights are too small "
                                          "against this fit's scatter to settle it",
                             "refused": "displaced, and no whole slot brings the ratio "
                                        "into the band"}.get(rec["tooth"]["outcome"], "")
                    if s:
                        tooth = (f"drawn {_signed(s)} slots from the comb fit, "
                                 + ("offset from the record" if src == "recorded"
                                    else "offset read off the heights"))
                marks = " ".join(f"<span class='mark {k}'>{e(m)}</span><br>"
                                 for k, m in rec["marks"])
                # the fields the page dropped, one fold-out per trace. This is the
                # one place in the gallery that speaks the pipeline's own dialect,
                # and it is the reason the page foot no longer has to.
                codes = ("<details><summary>recorded fields</summary><pre>"
                         + e("\n".join(rec["codes"])) + "</pre></details>")
                parts.append(f"<tr><td>{e(rec['file'])}{codes}</td>"
                             f"<td>{trim}</td><td>{e(tooth)}</td><td>{marks}</td></tr>")
            parts.append("</table>")

    out_path("index.html").write_text("\n".join(parts), encoding="utf-8")
    return GALLERY_DIR / "index.html"


# ---------------------------------------------------------------------------

def main() -> int:
    version = pipeline_version()
    manifest = load_manifest()
    print(f"inspection gallery v{version}: {len(manifest)} manifest traces "
          f"-> {GALLERY_DIR}")

    if not (C.DATA_RAW_DIR / "MANIFEST.csv").exists():
        print("  (no manifest in this checkout, nothing to draw)")
        return 1
    missing = [r["file"] for r in manifest if not trace_path(r).exists()]
    if missing:
        print(f"  ({len(missing)} raw traces absent, for example {missing[0]})")
        return 1

    import make_figures as MF
    from run_beta_self import load_t_rates
    ctx = MF._gallery_context()
    if ctx is None:
        print("  (no shared optimum available, lines will be drawn without a model)")
        ctx = {"sl_blocks": {}}
    _, prates = load_t_rates()

    qc_rows, ruler_rows = _table("qc_metrics.csv"), _table("ruler_traces.csv")

    lines = [r for r in manifest if r["rf_on"] != "True"]
    combs = [r for r in manifest if r["rf_on"] == "True"]
    print(f"  fitting {len(lines)} lines and {len(combs)} combs ...")
    census = archive_census(manifest)
    records = line_records(lines, ctx, prates) + comb_records(combs)
    records = [annotate(rec, qc_rows, ruler_rows, census) for rec in records]

    groups = defaultdict(list)
    for rec in records:
        groups[(rec["cls"], rec["cond"])].append(rec)
    pages = [build_page(cls, cond, groups[(cls, cond)], census, version)
             for cls, cond in sorted(groups,
                                     key=lambda k: (CLASSES.index(k[0]), k[1]))]
    for page in pages:
        draw_page(page, version, page["cls"], page["name"])
    print(f"  rendered {len(pages)} condition pages")

    index = write_index(pages, version)
    print(f"  wrote {index}")

    print("\ncensus by class")
    for cls in CLASSES:
        ps = [p for p in pages if p["cls"] == cls]
        rs = [r for p in ps for r in p["recs"]]
        print(f"  {cls:>11s}: {len(ps):>2d} pages, {len(rs):>3d} traces, "
              f"{sum(1 for r in rs if r['model'] is not None)} with a model, "
              f"{sum(1 for r in rs if r['trimmed'])} trimmed, "
              f"{sum(1 for r in rs if r['marks'])} marked")
    print("\nmarks")
    for kind, n in sorted(Counter(k for r in records for k, _ in r["marks"]).items()):
        print(f"  {kind:>12s}: {n}")
    print("\ncomb verdicts")
    for verdict, n in sorted(Counter(
            r["fit"]["verdict"] for r in records
            if r["kind"] == "comb" and r["fit"] is not None).items()):
        print(f"  {verdict:>12s}: {n}")
    print("\ntrim reasons")
    for reason, n in sorted(Counter(r["trim_reason"] for r in records).items()):
        print(f"  {n:>4d}  {reason or 'nothing cut, nothing refused'}")
    # the distinction amendment 7 asks the pages to keep: a cut recorded against a
    # line is almost always outside the window the line fit was ever asked about
    cut_lines = [r for r in records
                 if r["kind"] == "line" and r["trimmed"] and r["used"] is not None]
    seen = [r for r in cut_lines
            if np.any(((r["t"] < r["keep_lo"]) | (r["t"] > r["keep_hi"])) & r["used"])]
    print(f"  of the {len(cut_lines)} line traces with a cut on record, the line fit "
          f"had seen the cut samples on {len(seen)}")

    # the two gates, counted separately, because they answer different questions
    combs_fitted = [r for r in records if r["kind"] == "comb" and r["fit"] is not None]
    flagged = [r for r in combs_fitted if r.get("tooth")]
    accepted = [r for r in flagged if r["tooth"]["shift"]]
    print(f"\nthe amplitude test: {len(flagged)} of {len(combs_fitted)} fitted combs "
          "show a second order tooth taller than a first order tooth")
    for cls, n in sorted(Counter(r["cls"] for r in flagged).items()):
        print(f"    {n:>4d}  {cls}")
    print(f"\nthe ratio test, measured band {RATIO_BAND[0]:.3f} to "
          f"{RATIO_BAND[1]:.3f} of the first order:")
    for word, n in sorted(Counter(r["tooth"]["outcome"] for r in flagged).items()):
        print(f"    {n:>4d}  {word}")
    for src, n in sorted(Counter(r["tooth"]["source"] for r in accepted).items()):
        print(f"    {n:>4d}  offset from "
              f"{'the calibration record' if src == 'recorded' else 'the tooth heights'}")
    for off, n in sorted(Counter(r["tooth"]["shift"] for r in accepted).items()):
        print(f"    {n:>4d}  at {off:+d} slots")
    # the same rule applied to the combs the amplitude test does NOT flag: if it
    # rejected those, it would be measuring something other than the numbering
    clean = [r for r in combs_fitted if not r.get("tooth")]
    agree = sum(1 for r in clean
                if ratio_agrees(*second_to_first_ratio(r["fit"]["heights"], 0,
                                                       float(r["fit"]["fit_rms"]))))
    print(f"  control: {agree} of the {len(clean)} combs the amplitude test does not "
          "flag carry a ratio that agrees with the band")
    # the recorded-branch combs the earlier carrier test failed are re-judged here
    rec_branch = [r for r in flagged
                  if str(ruler_rows.get(r["file"], {}).get("reindex_action", ""))
                  == "phase_shift"]
    tall = [r for r in rec_branch if r["tooth"]["shift"]
            and _height_map(r["fit"]["heights"])[r["tooth"]["shift"]]
            > max(_height_map(r["fit"]["heights"])[r["tooth"]["shift"] - 1],
                  _height_map(r["fit"]["heights"])[r["tooth"]["shift"] + 1])]
    print(f"  {len(rec_branch)} of the flagged combs carry a recorded offset, and "
          f"{len(tall)} of those draw a carrier taller than its own first order pair, "
          "which the ratio test does not hold against them")
    # what the labelling verdict says about the same combs is a check, not the gate
    for verdict, n in sorted(Counter(
            (ruler_rows.get(r["file"], {}).get("verdict") or "no recorded verdict")
            for r in flagged).items()):
        print(f"    {n:>4d}  recorded as {verdict}")

    # A recomputation that disagrees with the table it annotates would make every
    # ruler page a picture of a different fit, so the disagreement is counted
    # rather than assumed away.
    drift = []
    for rec in records:
        rl = ruler_rows.get(rec["file"])
        if rec["kind"] != "comb" or rec["fit"] is None or not rl:
            continue
        d = abs(rec["fit"]["delta_ms"] - _num(rl["delta_ms"]))
        if d > 1e-6:
            drift.append((rec["file"], d))
    print(f"\n{len(drift)} of {len(ruler_rows)} recorded combs redraw at a different "
          "spacing than the table")
    for name, d in drift[:10]:
        print(f"  {name}: {d:.6f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
