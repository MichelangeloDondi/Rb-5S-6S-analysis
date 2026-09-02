#!/usr/bin/env python3
"""The power-versus-time sign test on the bidirectional rehearsal ladders.

Every 2025 campaign block ran its power ladder monotone in time, so any
width-versus-power statement from the campaign alone is degenerate with
clock time. The 2025-07-04 rehearsal ran two peaks' ladders ascending and
one descending (trigger stamps in the LeCroy headers), which separates
the two hypotheses by SIGN: a power effect keeps one slope sign across
both directions, a session drift flips the descending ladder's sign.
This producer regresses a model-independent width against power and
against clock time per (session, peak), and writes the signs, the
slopes, and a pooled two-model comparison.

Width metric: `rb5s6s.qc.contiguous_fwhm_ms` on the loader's own
window. The rehearsal window is scale-free (1.6 times the trace's own
width), so its truncation biases every width down by a common
shape-dependent factor; the pilot window is NOT scale-free — the
loader's adaptive halfwidth clips at an absolute 25 MHz, so the pilot
must be loaded at the real campaign bracket rate exactly as every
other caller loads it (a unit rate turns the clip into a window
narrower than the line, a saturating map an audit measured at
d(measured)/d(true) = 0.25). The absolute widths on either arm are
never the joint fit's fitted widths. Rehearsal widths convert ms to
MHz with the committed reh_rate CALIB rows; the pilot arrives in MHz
from its own axis, with the documented run ORDER as its time
coordinate (the Agilent files carry no trigger stamps).

Every row is a reanalysis of held sessions against a design question,
not a measurement of the atom, so the whole file is DIAGNOSTIC. Needs
the excluded 2025-07-04 and campaign-morning trees; without them it
prints what is missing and exits 0, like the other session producers.
Failure mode this guards against: reading the campaign's power axis as
physical when it could be elapsed time.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.pmfmt import pm_cells as _pm  # noqa: E402
from rb5s6s.qc import contiguous_fwhm_ms  # noqa: E402


def _ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(x)
    if n < 3 or np.ptp(x) == 0:
        return np.nan, np.nan, n
    A = np.vstack([np.ones(n), x]).T
    beta, res, *_ = np.linalg.lstsq(A, y, rcond=None)
    dof = n - 2
    s2 = (res[0] / dof) if (len(res) and dof > 0) else np.nan
    se = np.sqrt(s2 / np.sum((x - x.mean()) ** 2)) if np.isfinite(s2) else np.nan
    return float(beta[1]), float(se), n


def main() -> int:
    import run_stark_joint as rsj
    from run_beta_self import load_t_rates

    if not (rsj.SESSION_20250704 / "2025-07-04").is_dir():
        print("run_power_time_sign_test: the 2025-07-04 tree is absent "
              f"({rsj.SESSION_20250704}); set RB5S6S_SESSION_20250704_DIR. "
              "Nothing written.")
        return 0
    if not rsj.SESSION_20250717.is_dir():
        print("run_power_time_sign_test: the campaign-morning tree is absent "
              f"({rsj.SESSION_20250717.parent}); set "
              "RB5S6S_SESSION_20250717_DIR to that parent. Nothing written.")
        return 0

    reh_rate = {}
    with open(ROOT / "results" / "stark_joint.csv") as fh:
        for r in csv.DictReader(fh):
            if r["quantity"] == "reh_rate":
                reh_rate[r["key"]] = float(r["value"])

    reh, n_corrupt = rsj.load_session_20250704()
    t0 = min(tr["trig"] for tr in reh)
    rows = []
    for tr in reh:
        w_ms = contiguous_fwhm_ms(tr["x"], tr["v"])
        rows.append(dict(sess="reh", peak=tr["peak"], P_W=tr["P"],
                         t_min=(tr["trig"] - t0) / 60.0,
                         w=w_ms * reh_rate[tr["peak"]], unit="MHz"))
    _, prates = load_t_rates()
    pil = rsj.load_session_20250717(prates["4192"][0])
    # the documented ladder ran 210 -> 35 -> 70 -> 105; the order index is
    # CUMULATIVE over the blocks in that sequence (an audit measured that a
    # fixed per-block offset overlaps the 6/8/6/6 repeat counts and stops
    # being an order at all)
    ladder_seq = [0.210, 0.035, 0.070, 0.105]
    counts = {p: sum(1 for tr in pil if round(tr["P"], 3) == p)
              for p in ladder_seq}
    offset = {}
    run = 0
    for pw in ladder_seq:
        offset[pw] = run
        run += counts[pw]
    seen: dict[float, int] = {}
    for tr in pil:
        pw = round(tr["P"], 3)
        k = seen.get(pw, 0)
        seen[pw] = k + 1
        rows.append(dict(sess="pil", peak="4192", P_W=tr["P"],
                         t_min=float(offset[pw] + k),
                         w=contiguous_fwhm_ms(tr["x"], tr["v"]), unit="MHz"))

    out = [("n_traces", "reh", f"{len(reh)}", "", "count, loader accounting"),
           ("n_corrupt", "reh", f"{n_corrupt}", "",
            "count, parse or segmentation exits of the loader"),
           ("n_traces", "pil", f"{len(pil)}", "", "count")]
    for sess, peak in sorted({(r["sess"], r["peak"]) for r in rows}):
        g = [r for r in rows if r["sess"] == sess and r["peak"] == peak]
        P = [r["P_W"] for r in g]
        t = [r["t_min"] for r in g]
        y = [r["w"] for r in g]
        unit = g[0]["unit"]
        bP, seP, n = _ols(P, y)
        bt, set_, _ = _ols(t, y)
        cPt = (float(np.corrcoef(P, t)[0, 1])
               if np.ptp(P) > 0 and np.ptp(t) > 0 else np.nan)
        key = f"{sess}/{peak}"
        if np.isfinite(cPt):
            out.append(("corr_P_t", key, f"{cPt:.3f}", "",
                        "ladder direction, sign is the reading"))
        if np.isfinite(bP):
            vs, es = _pm(bP, seP)
            out.append(("slope_w_vs_P", key, vs, es,
                        (f"{unit} per W, the SIGN is the result"
                         if sess == "reh" else
                         f"{unit} per W. Weak and unresolved, the "
                         "recorded caveat of this file, beside three "
                         "positive rehearsal slopes")))
        if np.isfinite(bt):
            tunit = ("per min, trigger stamps" if sess == "reh"
                     else "per run-order step, no stamps on this arm")
            vt, et = _pm(bt, set_)
            out.append(("slope_w_vs_t", key, vt, et,
                        f"{unit} {tunit}"))

    mp = [r for r in rows if r["sess"] == "reh"]
    peaks = sorted({r["peak"] for r in mp
                    if len({q["P_W"] for q in mp if q["peak"] == r["peak"]}) > 1})
    mp = [r for r in mp if r["peak"] in peaks]
    y = np.array([r["w"] for r in mp])
    X0 = np.zeros((len(mp), len(peaks)))
    for i, r in enumerate(mp):
        X0[i, peaks.index(r["peak"])] = 1.0
    ssr = {}
    for name, xcol in (("power", [r["P_W"] for r in mp]),
                       ("time", [r["t_min"] for r in mp])):
        X = np.hstack([X0, np.array(xcol, float)[:, None]])
        beta, res, *_ = np.linalg.lstsq(X, y, rcond=None)
        ssr[name] = float(res[0]) if len(res) else float(np.sum((y - X @ beta) ** 2))
        out.append((f"pooled_slope_{name}", "reh", f"{beta[-1]:.4f}", "",
                    "MHz per W" if name == "power" else "MHz per min"))
    d_aic = len(mp) * (np.log(ssr["power"]) - np.log(ssr["time"]))
    out.append(("delta_aic_power_minus_time", "reh", f"{d_aic:.2f}", "",
                "negative prefers power. Per-peak intercepts, one common "
                "slope. This pooled row carries the discrimination, the "
                "per-peak descending slope alone does not resolve its sign"))

    dst = C.RESULTS_DIR / "power_time_sign_test.csv"
    with open(dst, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerows(out)
    print(f"wrote {dst} ({len(out)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
