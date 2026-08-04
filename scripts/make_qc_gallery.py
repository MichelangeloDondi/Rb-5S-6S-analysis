#!/usr/bin/env python3
"""
The inspection gallery: every trace in the archive, drawn once, for the eye.

The tooth-indexing defect that motivated the validity ladder was found by
looking at a picture, not by reading a number. Nothing in the pipeline draws
the other 296 traces, so nothing in the pipeline would have found the same
defect anywhere else. This script closes that gap the cheap way: it renders all
297 manifest traces at one panel each, in five classes, with the model that was
fitted to them, the residual the trimmer read, the samples the trimmer cut, and
the marks the outlier rule left.

    python scripts/make_qc_gallery.py

Output, all of it under `private/qc_gallery/` and none of it tracked:

    index.html                          the way in
    <class>/<condition>/<trace>.png     one panel per trace
    contact_<class>_p<NN>.png           the same panels, thirty to a sheet

Panel filenames carry their provenance: `{source basename}__v{version}.png`,
the convention the predecessor repository used so that a picture found loose on
a disk still says which trace and which release produced it.

WHAT IS DRAWN. Radio frequency off traces get the shared optimum of the global
archive fit, with only the per-trace nuisances refit locally, through the same
code path the fit-quality figures use. Rulers get the validity ladder's own
comb fit with the tooth labels printed. The residual strip carries the residual
the TRIMMER saw, which is the model-free envelope residual for a line and the
comb residual for a ruler, so a shaded region can be read against the evidence
that produced it rather than against a different residual.

THREE DO-NOTS, each of them a decision rather than a preference.

1. Never route a panel through `make_figures._save()`. Anything under
   `figures/` is citable, carries a data fingerprint and is held to the figure
   register and the freshness guard. These panels are none of those things:
   they are 297 pictures of raw data drawn for one reader, and putting them in
   the citable tree would make every one of them a publication decision.

2. Never add this file to the figure-register targets in
   `tests/test_figure_register.py`. That guard exists so a rendered figure
   speaks physics rather than pipeline vocabulary. Audit imagery has the
   opposite job: it has to print `hard_flags`, `reindex_action`, `top3_ok` and
   the rest verbatim, because the reader is checking those very fields.

3. Never wire this into `scripts/ci_gate.sh`. The gallery is an audit that can
   trigger a recompute, not a gate that blocks one. It needs the raw archive,
   it takes minutes rather than seconds, and a red gate here would say nothing
   about whether the analysis is correct.

Reads: data_raw/MANIFEST.csv and the raw traces, results/qc_metrics.csv,
results/ruler_traces.csv, results/global_archive_fit.csv, results/ruler_blocks.csv.
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.linefit import adaptive_halfwidth, to_frequency  # noqa: E402
from rb5s6s.noise import condition_noise_model, signal_level, sigma_of_v  # noqa: E402
from rb5s6s.qc import hard_flags, ingest_flags, trace_metrics  # noqa: E402
from rb5s6s.ruler import (TEETH, comb_residual,  # noqa: E402
                          validated_comb_fit)
from rb5s6s.trim import envelope_residual  # noqa: E402


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
    fig.savefig(out_path(*parts))
    plt.close(fig)


def pipeline_version() -> str:
    """The release version the panels are stamped with, read from the one place
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

CLASS_BLURB = {
    "canonical": "radio frequency off lines that carry the physics",
    "ruler_p": "before and after comb brackets of the power session",
    "ruler_t": "per temperature combs of the temperature session",
    "quarantine": "the aborted first attempt, excluded session grain",
    "discarded": "curation discards, excluded trace by trace",
}

PEAK_COLOR = {"4121": "#0072B2", "4154": "#D55E00",
              "4192": "#009E73", "4207": "#E69F00"}

MARK_COLOR = {"outlier": "#b2182b", "quarantined": "#762a83",
              "advised": "#e08214", "excluded": "#4d4d4d"}

SHORT_MARK = {"outlier": "group outlier", "quarantined": "quarantined",
              "advised": "quarantine advised"}
"""Contact sheet captions. `excluded` is deliberately absent: it is a property
of the class, the sheet title already carries it, and printing it on all thirty
cells would bury the marks that belong to one trace."""

TRIM_SHADE = "#d6604d"


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
    """The folder a trace lives in, which is also the group its noise law is
    built from. For every class this is the block the pipeline itself groups
    by, so a folder is a comparison a reader can make."""
    peak, T = row["peak"], int(float(row["temperature_C"]))
    if row["rf_on"] == "True":
        if row["bracket"]:
            return f"{peak}nm_{row['bracket']}_bracket"
        return f"{peak}nm_{T}C_comb"
    return f"{peak}nm_{T}C_{int(round(power_w(row) * 1e3))}mW"


def panel_name(row: dict, version: str) -> str:
    return f"{Path(row['file']).stem}__v{version}.png"


# ---------------------------------------------------------------------------
# the committed record each panel is annotated against
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
    so their curve is the shared optimum EVALUATED on them, which is stated on
    the panel.
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
                   "t": t, "v": v, "info": info, "kind": "line",
                   "law": law, "model_x": None, "model_y": None,
                   "fit_lo_ms": float("nan"), "fit_hi_ms": float("nan"),
                   "fit_note": "", "detector": envelope_residual(t, v),
                   "model_res_x": None, "model_res_y": None, "fit": None}
            pk = r["peak"]
            if pk not in prates:
                rec["fit_note"] = "no calibrated rate for this peak, data only"
                out.append(rec)
                continue
            rate = prates[pk][0]
            nu = to_frequency(t, rate)
            lev, base = signal_level(v)
            c0 = float(nu[int(np.argmax(lev))])
            sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
            m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
            block = f"camp{int(float(r['temperature_C']))}"
            if block not in ctx["sl_blocks"]:
                rec["fit_note"] = f"no shared laser width for {block}, data only"
                out.append(rec)
                continue
            fitrec = dict(sess="camp", peak=pk, T=float(r["temperature_C"]),
                          P=power_w(r), x=nu[m], v=v[m], sg=sg[m], c0=c0,
                          A0=float(lev.max()), b0=float(base), sl=block)
            try:
                fr = MF._fit_rec_nuisances(ctx, fitrec)
            except Exception as e:                       # a fit that will not run
                rec["fit_note"] = f"local nuisance refit failed: {e}"
                out.append(rec)
                continue
            rec["fit"] = fr
            rec["model_x"] = fr["xf"] / rate
            rec["model_y"] = fr["model_at"](fr["sol"].x, fr["xf"])
            rec["model_res_x"] = fr["x"] / rate
            rec["model_res_y"] = fr["v"] - fr["model_at"](fr["sol"].x, fr["x"])
            rec["fit_lo_ms"] = float(np.min(fr["x"]) / rate)
            rec["fit_hi_ms"] = float(np.max(fr["x"]) / rate)
            if key[0] != "canonical":
                rec["fit_note"] = ("outside the fitted population, the shared "
                                   "optimum is evaluated here, not fitted to it")
            out.append(rec)
    return out


def comb_records(rows):
    """Rulers, through the validity ladder, one noise law per block.

    The law is built from the block members the ladder itself would keep, which
    is what `run_ruler.py` does: a dropout riddled export is not allowed to set
    the noise scale its siblings are measured against. It is still DRAWN, with
    the reason it enters nothing printed on its panel, because a trace nobody
    ever looks at is a trace nobody can check.
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
                   "t": t, "v": v, "info": info, "kind": "comb",
                   "law": law, "model_x": None, "model_y": None,
                   "fit_lo_ms": float("nan"), "fit_hi_ms": float("nan"),
                   "fit_note": "", "detector": None,
                   "model_res_x": None, "model_res_y": None, "fit": None}
            if not ok:
                rec["fit_note"] = ("broken as a ruler, excluded from the "
                                   "calibration before any fit ran")
            try:
                f = validated_comb_fit(t, v, law)
            except RuntimeError as e:
                rec["fit_note"] = (rec["fit_note"] + " " if rec["fit_note"] else "") \
                    + f"comb fit failed: {e}"
                rec["detector"] = envelope_residual(t, v)
                out.append(rec)
                continue
            rec["fit"] = f
            grid = np.linspace(t[0], t[-1], 4000)
            from rb5s6s.ruler import _comb
            rec["model_x"] = grid
            rec["model_y"] = _comb(grid, f["t0_ms"], f["delta_ms"], f["width_ms"],
                                   np.asarray(f["heights"]), f["b0"], f["b1"])
            rec["detector"] = comb_residual(t, v, f)
            rec["fit_lo_ms"], rec["fit_hi_ms"] = float(t[0]), float(t[-1])
            if key[0] == "quarantine":
                rec["fit_note"] = ("comb of the aborted attempt, quarantined "
                                   "session grain, enters nothing")
            out.append(rec)
    return out


# ---------------------------------------------------------------------------
# annotation: the committed marks a panel has to show
# ---------------------------------------------------------------------------

def annotate(rec, qc_rows, ruler_rows):
    """Attach the trim record, the outlier mark and the header text."""
    row, f = rec["row"], rec["fit"]
    qc = qc_rows.get(rec["file"], {})
    rl = ruler_rows.get(rec["file"], {})
    is_comb = rec["kind"] == "comb"

    # The AUTHORITATIVE trim record. A ruler's lives in the ruler table and the
    # quality table deliberately reports it as not applicable there, so exactly
    # one record is read per trace and two records can never disagree on a panel.
    src = rl if (is_comb and rl) else qc
    rec["trimmed"] = _truthy(src.get("trimmed"))
    rec["keep_lo"] = _num(src.get("trim_start_ms"))
    rec["keep_hi"] = _num(src.get("trim_end_ms"))
    rec["trim_reason"] = src.get("trim_reason", "")
    rec["trim_source"] = ("the ruler ladder" if src is rl and rl
                          else "the quality pass" if src else "no record")

    rec["outlier"] = _truthy(qc.get("outlier")) or _truthy(rl.get("outlier"))
    rec["outlier_reason"] = (rl.get("outlier_reason") or qc.get("outlier_reason") or "")
    rec["quarantined"] = _truthy(rl.get("quarantined"))
    rec["quarantine_advised"] = _truthy(rl.get("quarantine_advised"))
    rec["quarantine_reason"] = rl.get("quarantine_reason", "")

    marks = []
    if rec["outlier"]:
        marks.append(("outlier", f"group outlier: {rec['outlier_reason'] or 'removed'}"))
    if rec["quarantined"]:
        marks.append(("quarantined", f"quarantined: {rec['quarantine_reason']}"))
    elif rec["quarantine_advised"]:
        marks.append(("advised", "quarantine advised, the verdict is not acting yet: "
                      + rec["quarantine_reason"]))
    if rec["cls"] in ("quarantine", "discarded"):
        marks.append(("excluded", f"{rec['cls']}: enters no headline fit"))
    if rec["fit_note"]:
        marks.append(("excluded", rec["fit_note"]))
    rec["marks"] = marks

    head = [f"{rec['file']}    [{rec['cls']} / {rec['cond']}]",
            f"role {row['role']}  peak 993.{row['peak']} nm  "
            f"T {row['temperature_C']} C  "
            f"power {row['power_mW'] + ' mW' if row['power_mW'] else 'the dwell'}  "
            f"rf_on {row['rf_on']}  bracket {row['bracket'] or '-'}  "
            f"repeat {row['repeat_idx']}  flag {row['flag']}"]
    if qc:
        head.append(
            f"quality: snr {_num(qc.get('snr')):.1f}  height {_num(qc.get('height_v')):.4f} V  "
            f"fwhm {_num(qc.get('fwhm_ms')):.1f} ms  peak at {_num(qc.get('peak_pos_ms')):.0f} ms  "
            f"edge margin {_num(qc.get('edge_margin_ms')):.0f} ms  "
            f"z_spike {_num(qc.get('z_spike')):.1f}  z_step {_num(qc.get('z_step')):.1f}  "
            f"lf_ratio {_num(qc.get('lf_ratio')):.2f}  comb_score {_num(qc.get('comb_score')):.2f}")
        head.append("hard_flags: " + (qc.get("hard_flags") or "none"))
    if is_comb and f is not None:
        head.append(
            f"comb: delta {f['delta_ms']:.3f} +- {f['delta_err_ms']:.3f} ms  "
            f"width {f['width_ms']:.1f} ms  chi2_red {f['chi2_red']:.2f}  "
            f"fit_rms {f['fit_rms']:.4f} V  n_fitted {f['n_fitted']}")
        head.append(
            f"verdict {f['verdict']}  rank(k=-1) {f['rank_m1']}  rank(k=+1) {f['rank_p1']}  "
            f"n_railed {f['n_railed']}  reindex_action {f['reindex_action']}  "
            f"j {f['reindex_j']}  excised_k {f['excised_k'] or '-'}  n_refits {f['n_refits']}")
        if rl:
            head.append(
                f"the recorded run: delta {_num(rl.get('delta_ms')):.3f} ms  "
                f"rate {_num(rl.get('rate_MHzms')):.6f} MHz/ms  "
                f"verdict {rl.get('verdict', '-')}  "
                f"advised delta {_num(rl.get('delta_advised_ms')):.3f} ms")
    if (not is_comb) and f is not None:
        head.append(
            f"shared optimum: gamma_coll {f['gc']:.2f} MHz  sigma_laser {f['sl']:.2f} MHz  "
            f"transit {f['transit']:.2f} MHz  stark scale {f['s0']:.2f} MHz")
        head.append(
            f"local nuisances: centre {f['cc']:.2f} +- {f['cc_err']:.2f} MHz  "
            f"height {f['A']:.4f}  chi2_red {f['chi2_red']:.2f}  "
            f"model fwhm {f['fwhm']:.2f} MHz")
    head.append(
        f"trim ({rec['trim_source']}): "
        + (f"keeps {rec['keep_lo']:.0f} to {rec['keep_hi']:.0f} ms, {rec['trim_reason']}"
           if rec["trimmed"] else (rec["trim_reason"] or "nothing cut, nothing refused")))
    rec["header"] = head
    return rec


# ---------------------------------------------------------------------------
# drawing
# ---------------------------------------------------------------------------

def _shade_trim(ax, rec):
    """Shade what the trimmer removed and print why, on whichever axis."""
    if not rec["trimmed"]:
        return
    t = rec["t"]
    lo, hi = rec["keep_lo"], rec["keep_hi"]
    if np.isfinite(lo) and lo > t[0]:
        ax.axvspan(t[0], lo, color=TRIM_SHADE, alpha=0.20, lw=0, zorder=0)
    if np.isfinite(hi) and hi < t[-1]:
        ax.axvspan(hi, t[-1], color=TRIM_SHADE, alpha=0.20, lw=0, zorder=0)


def _mark_axes(ax, rec):
    """A coloured frame is how a marked trace is found while scrolling."""
    if not rec["marks"]:
        return
    colour = MARK_COLOR[rec["marks"][0][0]]
    for s in ax.spines.values():
        s.set_color(colour)
        s.set_linewidth(1.8)


def draw_panel(rec, version: str, *dest: str) -> None:
    peak = rec["row"]["peak"]
    colour = PEAK_COLOR.get(peak, "#444444")
    is_comb = rec["kind"] == "comb"

    fig = plt.figure(figsize=(10.0, 7.4), dpi=100)

    # The header is as tall as the record makes it and the marks sit under it,
    # so the axes are given whatever is left rather than a fixed fraction that
    # a two-line hard_flags entry would print through.
    head_lines = [w for line in rec["header"]
                  for w in (textwrap.wrap(line, 132, subsequent_indent="        ")
                            or [""])]
    mark_lines = [(kind, textwrap.wrap(msg, 148) or [""]) for kind, msg in rec["marks"]]
    line_h = 7.0 * 1.20 / 72.0 / 7.4          # size in points, leading, inches
    mark_h = 7.4 * 1.30 / 72.0 / 7.4
    head_bottom = 0.988 - len(head_lines) * line_h - 0.012
    marks_bottom = head_bottom - sum(len(w) for _, w in mark_lines) * mark_h
    # a comb panel carries a tooth-order axis ABOVE its main axis, so it needs
    # the clearance the marks would otherwise print into
    top = min(0.80, marks_bottom - (0.050 if is_comb else 0.012))

    nrows = 3 if is_comb else 2
    ratios = [3.0, 1.1, 1.2] if is_comb else [3.0, 1.25]
    gs = fig.add_gridspec(nrows, 1, height_ratios=ratios,
                          hspace=0.46 if is_comb else 0.30,
                          top=max(top, 0.60), bottom=0.105 if is_comb else 0.085,
                          left=0.085, right=0.975)
    ax = fig.add_subplot(gs[0])
    axr = fig.add_subplot(gs[1], sharex=ax)

    t, v = rec["t"], rec["v"]
    ax.plot(t, v, ".", ms=1.6, color="0.55", alpha=0.65, label="trace")
    if rec["model_y"] is not None:
        ax.plot(rec["model_x"], rec["model_y"], "-", color=colour, lw=1.5,
                label="comb fit of record" if is_comb else "shared optimum, nuisances refit")
    if (not is_comb) and np.isfinite(rec["fit_lo_ms"]):
        for e in (rec["fit_lo_ms"], rec["fit_hi_ms"]):
            ax.axvline(e, color=colour, lw=0.8, ls=(0, (5, 4)), alpha=0.7)
        ax.plot([], [], color=colour, lw=0.8, ls=(0, (5, 4)),
                label="edges of the fitted window")
    inside = []
    if is_comb and rec["fit"] is not None:
        f = rec["fit"]
        inside = [(k, f["t0_ms"] + k * f["delta_ms"]) for k in TEETH
                  if t[0] <= f["t0_ms"] + k * f["delta_ms"] <= t[-1]]
        for _, c in inside:
            ax.axvline(c, color="0.35", lw=0.7, ls=":", alpha=0.8)
    _shade_trim(ax, rec)
    ax.set_ylabel("signal (V)", fontsize=9)
    ax.tick_params(labelbottom=False, labelsize=8)
    ax.legend(fontsize=7, loc="upper left", frameon=True, framealpha=0.85)
    _mark_axes(ax, rec)
    if inside:
        # the tooth labels ride on their own axis across the top, where no
        # legend, no data and no shaded band can land on top of them
        axk = ax.twiny()
        axk.set_xlim(ax.get_xlim())
        axk.set_xticks([c for _, c in inside])
        axk.set_xticklabels([f"{k:+d}" if k else "0" for k, _ in inside], fontsize=7.5)
        axk.set_xlabel("tooth order k, at the fitted comb positions", fontsize=8,
                       labelpad=2)
        axk.tick_params(length=2.5)
        axk.grid(False)

    det = rec["detector"]
    label = ("comb residual, what the trimmer read" if is_comb
             else "envelope residual, what the trimmer read")
    if det is not None:
        axr.plot(t, det, "-", lw=0.6, color="0.45", label=label)
    if rec["model_res_y"] is not None:
        axr.plot(rec["model_res_x"], rec["model_res_y"], ".", ms=1.5,
                 color=colour, alpha=0.6, label="trace minus the drawn model")
    axr.axhline(0.0, color="k", lw=0.7)
    _shade_trim(axr, rec)
    axr.set_ylabel("residual (V)", fontsize=8)
    axr.tick_params(labelsize=8)
    axr.legend(fontsize=6.5, loc="upper left", frameon=True, framealpha=0.85, ncol=2)
    if rec["trimmed"]:
        axr.text(0.995, 0.04, f"shaded, cut from the fit: {rec['trim_reason']}",
                 transform=axr.transAxes, fontsize=7, ha="right", va="bottom",
                 color=TRIM_SHADE)
    _mark_axes(axr, rec)

    if is_comb:
        axh = fig.add_subplot(gs[2])
        f = rec["fit"]
        if f is not None:
            h = np.asarray(f["heights"], dtype=float)
            cols = ["#2166ac" if abs(k) == 1 else "0.62" for k in TEETH]
            axh.bar(list(TEETH), h, color=cols, width=0.62)
            axh.axhline(f["fit_rms"], color=TRIM_SHADE, lw=1.0, ls="--",
                        label=f"fit_rms {f['fit_rms']:.4f} V")
            for k, hk in zip(TEETH, h):
                axh.text(k, hk, f"{hk:.3f}", fontsize=6, ha="center", va="bottom",
                         color="0.3")
            axh.set_ylim(top=max(float(h.max()), f["fit_rms"]) * 1.22 or 1.0)
            axh.legend(fontsize=6.5, loc="best", frameon=False)
        axh.set_xticks(list(TEETH))
        # the verdict goes UNDER the bars: a tall comb fills every corner of
        # this panel, and which corner it fills depends on the trace
        verdict_line = ("" if f is None else
                        f"\nverdict {f['verdict']}    ladder {f['reindex_action']}"
                        f"    n_railed {f['n_railed']}")
        axh.set_xlabel("the seven fitted tooth heights by order k, the two blue "
                       "bars being the pair the top three rule tests"
                       + verdict_line, fontsize=8)
        axh.set_ylabel("height (V)", fontsize=8)
        axh.tick_params(labelsize=7.5)
    axr.tick_params(labelbottom=True)
    axr.set_xlabel("acquisition time (ms)", fontsize=9)

    fig.text(0.012, 0.988, "\n".join(head_lines), fontsize=7.0, family="monospace",
             va="top", ha="left", color="0.15")
    y = head_bottom
    for kind, wrapped in mark_lines:
        fig.text(0.012, y, "\n".join(wrapped), fontsize=7.4, va="top",
                 ha="left", color=MARK_COLOR[kind], fontweight="bold")
        y -= mark_h * len(wrapped)
    fig.text(0.988, 0.006,
             f"rb5s6s v{version} inspection gallery, not a citable figure   "
             f"regenerate: python scripts/make_qc_gallery.py",
             fontsize=6.2, ha="right", va="bottom", color="0.45")
    save_png(fig, *dest)


CONTACT_ROWS, CONTACT_COLS = 6, 5
CONTACT_PER_SHEET = CONTACT_ROWS * CONTACT_COLS


def draw_contact_sheet(cls, page, recs, version: str, npages: int, *dest: str) -> None:
    """One sheet of thirty panels, each a nested main and residual cell.

    The nested subgridspec layout is the one the twenty condition figure uses:
    an outer cell per trace, split into a tall data cell and a short residual
    cell, so a whole class can be scanned for the shape that does not belong.
    """
    fig = plt.figure(figsize=(15.0, 19.0), dpi=100)
    gs = fig.add_gridspec(1, 1, left=0.035, right=0.985, top=0.935, bottom=0.030)
    inner = gs[0, 0].subgridspec(CONTACT_ROWS, CONTACT_COLS, hspace=0.42, wspace=0.14)
    for i in range(CONTACT_PER_SHEET):
        r, c = divmod(i, CONTACT_COLS)
        cell = inner[r, c].subgridspec(2, 1, height_ratios=[3.0, 1.1], hspace=0.06)
        ax = fig.add_subplot(cell[0])
        axr = fig.add_subplot(cell[1], sharex=ax)
        for a in (ax, axr):
            a.set_xticks([]); a.set_yticks([])
            for s in a.spines.values():
                s.set_color("0.85")
        if i >= len(recs):
            ax.set_axis_off(); axr.set_axis_off()
            continue
        rec = recs[i]
        colour = PEAK_COLOR.get(rec["row"]["peak"], "#444444")
        t, v = rec["t"], rec["v"]
        ax.plot(t[::3], v[::3], ".", ms=0.9, color="0.55", alpha=0.6)
        if rec["model_y"] is not None:
            ax.plot(rec["model_x"], rec["model_y"], "-", color=colour, lw=0.9)
        if rec["detector"] is not None:
            axr.plot(t[::3], rec["detector"][::3], "-", lw=0.5, color="0.45")
        axr.axhline(0.0, color="k", lw=0.5)
        _shade_trim(ax, rec)
        _shade_trim(axr, rec)
        _mark_axes(ax, rec)
        _mark_axes(axr, rec)
        tag = Path(rec["file"]).stem
        # only the PER TRACE marks go on a sheet: a class-wide note would print
        # identically on all thirty cells and say nothing the title does not
        note = ", ".join(SHORT_MARK[k] for k, _ in rec["marks"] if k in SHORT_MARK)
        ax.set_title(tag + (f"\n{note}" if note else ""), fontsize=6.2,
                     color=MARK_COLOR[rec["marks"][0][0]] if rec["marks"] else "0.25",
                     pad=2)

    fig.suptitle(f"{cls}: {CLASS_BLURB[cls]}   sheet {page} of {npages}   "
                 f"{len(recs)} of the class on this sheet", fontsize=12, y=0.972)
    fig.text(0.035, 0.950,
             "a coloured frame marks a trace the record removed or flagged, a "
             "shaded band marks samples the trimmer cut, the lower strip is the "
             "residual the trimmer read",
             fontsize=8.5, color="0.35", ha="left")
    fig.text(0.985, 0.006, f"rb5s6s v{version} inspection gallery, not a citable figure",
             fontsize=6.5, ha="right", color="0.45")
    save_png(fig, *dest)


# ---------------------------------------------------------------------------
# index
# ---------------------------------------------------------------------------

def write_index(records, sheets, version: str) -> Path:
    e = html.escape
    by_class = defaultdict(lambda: defaultdict(list))
    for rec in records:
        by_class[rec["cls"]][rec["cond"]].append(rec)

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
             ".mark{font-weight:600}", ".outlier{color:#b2182b}",
             ".quarantined{color:#762a83}", ".advised{color:#e08214}",
             ".excluded{color:#4d4d4d}", ".trim{color:#d6604d}",
             "code{background:#f4f4f4;padding:.1rem .3rem;border-radius:3px}",
             "</style>",
             f"<h1>Inspection gallery, {len(records)} traces, v{e(version)}</h1>",
             "<p>One panel per trace in the archive manifest, drawn from the raw "
             "trace and annotated against the tables of record. Shaded bands are "
             "samples the residual tail trimmer cut. Coloured frames and coloured "
             "notes are marks the record left: a group outlier, a quarantine, a "
             "quarantine the ladder advised without acting on, or a class that "
             "enters no headline fit.</p>",
             "<p>This is an audit, not a citable figure set. Nothing here is "
             "tracked, nothing here carries a data fingerprint, and nothing here "
             "gates anything. Regenerate with "
             "<code>python scripts/make_qc_gallery.py</code>.</p>"]

    counts = Counter(rec["cls"] for rec in records)
    parts.append("<h2>The five classes</h2><table><tr><th>class</th><th>what it is"
                 "</th><th>traces</th><th>trimmed</th><th>marked</th></tr>")
    for cls in CLASSES:
        rs = [r for r in records if r["cls"] == cls]
        parts.append(f"<tr><td><a href='#{e(cls)}'>{e(cls)}</a></td>"
                     f"<td>{e(CLASS_BLURB[cls])}</td><td>{counts[cls]}</td>"
                     f"<td>{sum(1 for r in rs if r['trimmed'])}</td>"
                     f"<td>{sum(1 for r in rs if r['marks'])}</td></tr>")
    parts.append("</table>")

    for cls in CLASSES:
        conds = by_class.get(cls, {})
        if not conds:
            continue
        parts.append(f"<h2 id='{e(cls)}'>{e(cls)}: {e(CLASS_BLURB[cls])}</h2>")
        for name in sorted(sheets.get(cls, [])):
            parts.append(f"<p><img src='{e(name)}' alt='{e(name)}'></p>")
        for cond in sorted(conds):
            parts.append(f"<h3>{e(cond)}</h3><table>"
                         "<tr><th>trace</th><th>panel</th><th>trim</th>"
                         "<th>marks</th></tr>")
            for rec in sorted(conds[cond], key=lambda r: r["file"]):
                rel = f"{cls}/{cond}/{panel_name(rec['row'], version)}"
                trim = (f"<span class='trim'>{e(rec['trim_reason'])}, keeps "
                        f"{rec['keep_lo']:.0f} to {rec['keep_hi']:.0f} ms</span>"
                        if rec["trimmed"] else e(rec["trim_reason"] or ""))
                marks = " ".join(
                    f"<span class='mark {k}'>{e(m)}</span><br>" for k, m in rec["marks"])
                parts.append(f"<tr><td>{e(rec['file'])}</td>"
                             f"<td><a href='{e(rel)}'>panel</a></td>"
                             f"<td>{trim}</td><td>{marks}</td></tr>")
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
    records = line_records(lines, ctx, prates) + comb_records(combs)
    records = [annotate(rec, qc_rows, ruler_rows) for rec in records]
    records.sort(key=lambda r: (CLASSES.index(r["cls"]), r["cond"], r["file"]))

    for rec in records:
        draw_panel(rec, version, rec["cls"], rec["cond"],
                   panel_name(rec["row"], version))
    print(f"  rendered {len(records)} panels")

    sheets = defaultdict(list)
    for cls in CLASSES:
        rs = [r for r in records if r["cls"] == cls]
        npages = max(1, -(-len(rs) // CONTACT_PER_SHEET))
        for page in range(npages):
            chunk = rs[page * CONTACT_PER_SHEET:(page + 1) * CONTACT_PER_SHEET]
            name = f"contact_{cls}_p{page + 1:02d}.png"
            draw_contact_sheet(cls, page + 1, chunk, version, npages, name)
            sheets[cls].append(name)
    print(f"  rendered {sum(len(v) for v in sheets.values())} contact sheets")

    index = write_index(records, sheets, version)
    print(f"  wrote {index}")

    print("\ncensus by class")
    for cls in CLASSES:
        rs = [r for r in records if r["cls"] == cls]
        drawn_model = sum(1 for r in rs if r["model_y"] is not None)
        print(f"  {cls:>11s}: {len(rs):>3d} traces, {drawn_model} with a model, "
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

    # A recomputation that disagrees with the table it annotates would make
    # every ruler panel a picture of a different fit, so the disagreement is
    # counted rather than assumed away.
    drift = []
    for rec in records:
        rl = ruler_rows.get(rec["file"])
        if rec["kind"] != "comb" or rec["fit"] is None or not rl:
            continue
        d = abs(rec["fit"]["delta_ms"] - _num(rl["delta_ms"]))
        if d > 1e-6:
            drift.append((rec["file"], d))
    print(f"\n{len(drift)} of {len(ruler_rows)} recorded combs redraw at a "
          f"different spacing than the table")
    for name, d in drift[:10]:
        print(f"  {name}: {d:.6f} ms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
