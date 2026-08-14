"""
The 2025-06-12 cavity-scan reading (IMG_2508), computed from its digitisation.

Why this exists. APPARATUS.md section 6 reads the two channels of the
2025-06-12 oscilloscope photograph as the 5.00 s triangular cavity ramp
(channel 1) and the four 5S->6S hyperfine components crossed once per sweep
direction (channel 2). That reading rests on numbers -- mirror-pair
midpoints, spike integrals, their ratios against the ground-state population
law -- which until 2026-08-05 were quoted without a committed procedure
behind them. This module is the procedure: every number the apparatus notes
and the level-scheme figure quote from the digitised record is computed here,
from the committed CSV, under rules stated as module constants.

The record. `docs/apparatus/2025-06-12_cavity_scan_IMG_2508_digitised.csv`,
700 samples over one 5.00 s scan period (7.15 ms pitch), two channels in
scope divisions. It is a digitisation of a photographed display, and that
sets what the integrals can carry: the display compresses the tallest
spikes (the two 85Rb up-sweep peaks read equal heights to ~1% where the
populations put them 1.4 apart), the 87Rb F=1 crossings straddle the ramp
apex and span only three samples each, and the down-sweep amplitudes are
compressed outright (its 85Rb F=3/F=2 integral ratio reads ~0.65 against a
predicted 1.40). Ratios between the well-sampled up-sweep spikes survive;
per-spike weights do not.

The rules, all committed here as constants:

  * baseline = median of channel 2; a SPIKE is a maximal run of samples more
    than K_MAD median absolute deviations above it; each spike's integral is
    the trapezoid of (ch2 - baseline) over its run;
  * the ramp apex comes from an iterative straight-line fit to each ramp
    flank of channel 1, dropping points more than FLANK_K_MAD MADs of
    residual per pass (the digitisation carries cross-talk outliers); the
    apex is the flank-line intersection, with the raw argmax kept beside it;
  * spikes before the apex are the up-sweep, after it the down-sweep, and
    the k-th up spike pairs with the k-th-from-last down spike;
  * the hyperfine assignment takes the stated frequency direction (an
    up-sweep running from 87Rb F=2 to 87Rb F=1, APPARATUS.md sec. 6), i.e.
    up-sweep time order 4207, 4192, 4154, 4121 in the PEAKS labels.

The predicted strengths come from the M10 population law already in
`rb5s6s.amplitudes.predicted_shares`: abundance x (2F+1)/G_iso. Note the
G_iso normalisation -- against the un-normalised abundance x (2F+1) the
isotope-pair area ratio would be misread as 3.9 where the law predicts
exactly the abundance ratio 2.59, since the (2F+1) sum to G_iso within each
isotope.

Reproduce: `python -m rb5s6s.cavity_scan` prints the full table;
`python scripts/run_cavity_scan.py` writes `results/cavity_scan_integrals.csv`.
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from ._compat import trapezoid
from .amplitudes import predicted_shares
from . import config as C

SCAN_CSV = (C.REPO_ROOT / "docs" / "apparatus"
            / "2025-06-12_cavity_scan_IMG_2508_digitised.csv")

K_MAD = 5.0
"""Committed spike threshold: channel-2 median + K_MAD * MAD."""

K_MAD_BAND = (5.0, 6.0, 7.0, 8.0)
"""Thresholds over which the quoted rule-dependence band is taken. Below
5 MAD the runs pick up asymmetric shoulder samples and the 85Rb ratio
inflates (2.24 at 3 MAD); from 5 to 8 MAD the record keeps its eight runs
and the ratio moves only in the second digit."""

FLANK_EDGE_S = 0.3
FLANK_APEX_S = 0.25
"""Channel-1 samples fitted as ramp flanks: clear of the record's ends by
FLANK_EDGE_S and of the (argmax) apex by FLANK_APEX_S."""

FLANK_K_MAD = 4.0
FLANK_N_ITER = 6
"""Iterative flank fit: refit dropping points beyond FLANK_K_MAD MADs of
residual, at most FLANK_N_ITER passes (converges in fewer)."""

UP_SWEEP_ORDER = ("4207", "4192", "4154", "4121")
"""Hyperfine assignment of the four up-sweep spikes in time order, under the
stated frequency direction. PEAKS labels: 4207 = 87Rb F=2, 4192 = 85Rb F=3,
4154 = 85Rb F=2, 4121 = 87Rb F=1."""


@dataclass(frozen=True)
class Spike:
    """One maximal above-threshold run of channel 2."""
    t_start_s: float
    t_end_s: float
    n_samples: int
    t_centroid_s: float        # integral-weighted
    height_div: float          # peak excursion above the baseline
    integral_div_s: float      # trapezoid of (ch2 - baseline) over the run


@dataclass(frozen=True)
class ApexFit:
    """The channel-1 ramp apex, two ways."""
    t_apex_s: float            # flank-line intersection (the robust one)
    t_argmax_s: float          # raw sample argmax
    slope_up_div_s: float
    slope_down_div_s: float
    n_masked: int              # flank points dropped as cross-talk
    n_flank: int               # flank points offered to the fit


@dataclass(frozen=True)
class ScanReading:
    """Everything the docs and fig13 quote from the digitised record."""
    apex: ApexFit
    up: Dict[str, Spike]                 # peak label -> up-sweep spike
    down: Dict[str, Spike]
    pair_midpoint_s: Dict[str, float]    # mean of the paired centroids
    ratio_85_up: float                   # up-sweep 4192/4154 integrals
    ratio_85_up_band: Tuple[float, float]    # min/max over K_MAD_BAND
    ratio_85_down: float                 # the compression diagnostic
    iso_pair_up: float                   # up-sweep (85 pair)/(87 pair) areas
    iso_pair_up_band: Tuple[float, float]
    predicted: Dict[str, float]          # M10 population shares


def load_scan(path=SCAN_CSV):
    """The digitised record as (t_s, ch1_div, ch2_div) arrays.

    With the default path, raises `config.RepoDataMissing` when the
    repository is not beside the package. An explicit path is the caller's
    own and is opened as given.
    """
    if path is SCAN_CSV:
        C.require_repo_data("data_raw")
    t, ch1, ch2 = [], [], []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            t.append(float(row["t_s"]))
            ch1.append(float(row["ch1_div"]))
            ch2.append(float(row["ch2_div"]))
    return np.asarray(t), np.asarray(ch1), np.asarray(ch2)


def find_spikes(t, ch2, k_mad=K_MAD) -> List[Spike]:
    """Maximal runs of ch2 more than k_mad MADs above its median."""
    baseline = np.median(ch2)
    mad = np.median(np.abs(ch2 - baseline))
    above = ch2 > baseline + k_mad * mad
    spikes = []
    i = 0
    while i < len(above):
        if not above[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(above) and above[j + 1]:
            j += 1
        seg_t, seg_y = t[i:j + 1], ch2[i:j + 1] - baseline
        area = float(trapezoid(seg_y, seg_t)) if j > i else 0.0
        spikes.append(Spike(
            t_start_s=float(t[i]), t_end_s=float(t[j]), n_samples=j - i + 1,
            t_centroid_s=float(np.sum(seg_t * seg_y) / np.sum(seg_y)),
            height_div=float(seg_y.max()), integral_div_s=area))
        i = j + 1
    return spikes


def fit_apex(t, ch1) -> ApexFit:
    """The ramp apex from iterative straight-line fits to the two flanks."""
    def robust_line(tt, yy):
        keep = np.ones(len(tt), bool)
        for _ in range(FLANK_N_ITER):
            p = np.polyfit(tt[keep], yy[keep], 1)
            r = yy - np.polyval(p, tt)
            med = np.median(r[keep])
            s = np.median(np.abs(r[keep] - med))
            new = np.abs(r - med) < FLANK_K_MAD * max(s, 1e-9)
            if (new == keep).all():
                break
            keep = new
        return p, keep

    t_argmax = float(t[np.argmax(ch1)])
    up = (t > t[0] + FLANK_EDGE_S) & (t < t_argmax - FLANK_APEX_S)
    dn = (t > t_argmax + FLANK_APEX_S) & (t < t[-1] - FLANK_EDGE_S)
    p_up, k_up = robust_line(t[up], ch1[up])
    p_dn, k_dn = robust_line(t[dn], ch1[dn])
    return ApexFit(
        t_apex_s=float((p_dn[1] - p_up[1]) / (p_up[0] - p_dn[0])),
        t_argmax_s=t_argmax,
        slope_up_div_s=float(p_up[0]), slope_down_div_s=float(p_dn[0]),
        n_masked=int((~k_up).sum() + (~k_dn).sum()),
        n_flank=int(up.sum() + dn.sum()))


def _ratios(spikes: List[Spike], t_apex: float):
    """Assign the eight spikes and take the quoted ratios; None if the spike
    count is not the record's eight."""
    if len(spikes) != 8:
        return None
    up = [s for s in spikes if s.t_centroid_s < t_apex]
    down = [s for s in spikes if s.t_centroid_s >= t_apex]
    if len(up) != 4:
        return None
    up_by = dict(zip(UP_SWEEP_ORDER, up))
    down_by = dict(zip(UP_SWEEP_ORDER, down[::-1]))
    a_up = {k: up_by[k].integral_div_s for k in UP_SWEEP_ORDER}
    a_dn = {k: down_by[k].integral_div_s for k in UP_SWEEP_ORDER}
    return dict(
        up=up_by, down=down_by,
        ratio_85_up=a_up["4192"] / a_up["4154"],
        ratio_85_down=a_dn["4192"] / a_dn["4154"],
        iso_pair_up=(a_up["4192"] + a_up["4154"])
                    / (a_up["4207"] + a_up["4121"]))


def read_scan(path=SCAN_CSV) -> ScanReading:
    """The full reading at the committed rules, with the K_MAD_BAND
    rule-dependence of the two quoted up-sweep ratios."""
    t, ch1, ch2 = load_scan(path)
    apex = fit_apex(t, ch1)
    main = _ratios(find_spikes(t, ch2, K_MAD), apex.t_apex_s)
    if main is None:
        raise ValueError(f"{path}: expected the record's eight spikes in "
                         f"4+4 about the apex at the {K_MAD} MAD rule")
    r85, riso = [], []
    for k in K_MAD_BAND:
        r = _ratios(find_spikes(t, ch2, k), apex.t_apex_s)
        if r is not None:
            r85.append(r["ratio_85_up"])
            riso.append(r["iso_pair_up"])
    return ScanReading(
        apex=apex, up=main["up"], down=main["down"],
        pair_midpoint_s={k: 0.5 * (main["up"][k].t_centroid_s
                                   + main["down"][k].t_centroid_s)
                         for k in UP_SWEEP_ORDER},
        ratio_85_up=main["ratio_85_up"],
        ratio_85_up_band=(min(r85), max(r85)),
        ratio_85_down=main["ratio_85_down"],
        iso_pair_up=main["iso_pair_up"],
        iso_pair_up_band=(min(riso), max(riso)),
        predicted=predicted_shares())


def results_rows(reading: ScanReading = None) -> List[List[str]]:
    """The rows run_cavity_scan.py commits to results/cavity_scan_integrals.csv,
    in the long (quantity, key, value, unit) house format. One function so the
    freshness test in tests/test_cavity_scan.py diffs exactly what the
    producer writes."""
    r = reading or read_scan()
    rows = [["quantity", "key", "value", "unit"]]
    for sweep, spikes in (("up", r.up), ("down", r.down)):
        for k in UP_SWEEP_ORDER:
            s = spikes[k]
            rows += [
                ["integral", f"{k}_{sweep}", f"{s.integral_div_s:.5f}", "div_s"],
                ["height", f"{k}_{sweep}", f"{s.height_div:.3f}", "div"],
                ["t_centroid", f"{k}_{sweep}", f"{s.t_centroid_s:.4f}", "s"],
                ["n_samples", f"{k}_{sweep}", str(s.n_samples), "count"],
            ]
    for k in UP_SWEEP_ORDER:
        rows.append(["pair_midpoint", k, f"{r.pair_midpoint_s[k]:.4f}", "s"])
    rows += [
        ["apex_flank_fit", "ch1", f"{r.apex.t_apex_s:.4f}", "s"],
        ["apex_argmax", "ch1", f"{r.apex.t_argmax_s:.4f}", "s"],
        ["flank_points_masked", "ch1",
         f"{r.apex.n_masked}_of_{r.apex.n_flank}", "count"],
        ["ratio_85_up", "4192/4154", f"{r.ratio_85_up:.3f}", "ratio"],
        ["ratio_85_up_min", f"{min(K_MAD_BAND):g}-{max(K_MAD_BAND):g}_mad",
         f"{r.ratio_85_up_band[0]:.3f}", "ratio"],
        ["ratio_85_up_max", f"{min(K_MAD_BAND):g}-{max(K_MAD_BAND):g}_mad",
         f"{r.ratio_85_up_band[1]:.3f}", "ratio"],
        ["ratio_85_down", "4192/4154", f"{r.ratio_85_down:.3f}", "ratio"],
        ["iso_pair_up", "85/87", f"{r.iso_pair_up:.3f}", "ratio"],
        ["iso_pair_up_min", f"{min(K_MAD_BAND):g}-{max(K_MAD_BAND):g}_mad",
         f"{r.iso_pair_up_band[0]:.3f}", "ratio"],
        ["iso_pair_up_max", f"{min(K_MAD_BAND):g}-{max(K_MAD_BAND):g}_mad",
         f"{r.iso_pair_up_band[1]:.3f}", "ratio"],
        ["predicted_ratio_85", "7/5", f"{7 / 5:.3f}", "ratio"],
        ["predicted_iso_pair", "abundance",
         f"{(r.predicted['4192'] + r.predicted['4154']) / (r.predicted['4207'] + r.predicted['4121']):.3f}",
         "ratio"],
    ]
    return rows


def render_results_csv() -> str:
    """The committed CSV, byte for byte."""
    buf = io.StringIO()
    csv.writer(buf, lineterminator="\n").writerows(results_rows())
    return buf.getvalue()


def main():
    r = read_scan()
    names = {"4207": "87Rb F=2", "4192": "85Rb F=3",
             "4154": "85Rb F=2", "4121": "87Rb F=1"}
    print(f"apex: flank fit {r.apex.t_apex_s:.4f} s (argmax "
          f"{r.apex.t_argmax_s:.3f} s), masking {r.apex.n_masked} of "
          f"{r.apex.n_flank} flank points")
    print(f"{'component':10s} {'up-A':>8s} {'down-A':>8s} {'mid':>6s} "
          f"{'pred share':>10s}")
    for k in UP_SWEEP_ORDER:
        print(f"{names[k]:10s} {r.up[k].integral_div_s:8.5f} "
              f"{r.down[k].integral_div_s:8.5f} {r.pair_midpoint_s[k]:6.3f} "
              f"{r.predicted[k]:10.3f}")
    print(f"up 85 F=3/F=2: {r.ratio_85_up:.3f} "
          f"({r.ratio_85_up_band[0]:.3f}-{r.ratio_85_up_band[1]:.3f} over "
          f"{min(K_MAD_BAND):g}-{max(K_MAD_BAND):g} MAD; predicted 1.400); "
          f"down-sweep reads {r.ratio_85_down:.3f}")
    p_iso = ((r.predicted["4192"] + r.predicted["4154"])
             / (r.predicted["4207"] + r.predicted["4121"]))
    print(f"up 85/87 pair areas: {r.iso_pair_up:.2f} "
          f"({r.iso_pair_up_band[0]:.2f}-{r.iso_pair_up_band[1]:.2f}; "
          f"predicted {p_iso:.2f})")


if __name__ == "__main__":
    main()
