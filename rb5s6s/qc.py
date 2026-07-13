"""
Per-trace objective quality metrics and the curation audit (module M0, part 2)
==============================================================================

PURPOSE
-------
Two jobs, both *physics-blind* (no lineshape model is fitted here — QC must
never know what answer the physics fits will later prefer, or QC-based
exclusion stops being unbiased):

1. Compute, for every trace in the manifest, a set of objective quality
   metrics (baseline, noise, glitches, steps, clipping, peak location and
   crude extent, comb periodicity).
2. Audit the experimenter's curation SYMMETRICALLY (user request,
   2026-07-11): the discarded traces must look bad by these metrics, and the
   canonical traces must look good — each trace is compared against its
   same-condition siblings. Disagreements in either direction are reported;
   the pre-registered policy (canonical in / discarded out of headline fits)
   only changes for *canonical* traces that fail hard QC — that is the
   "QC-based, never result-based" exclusion the plan allows.

DESIGN NOTES
------------
* Smoothing is plain boxcar (documented widths in config). We learned the
  hard way (2026-07-11 ledger) that raw peak-picking on band-limited noise
  invents structure — every structural metric therefore works on strongly
  smoothed data, and no metric here is used for physics.
* The noise model proper is module M1. QC runs BEFORE M1, so the
  signal-dependent noise scale used by the glitch detector is a documented
  provisional guess (config.QC_PROVISIONAL_NOISE_GAIN, motivated by the old
  pipeline's residuals: ~x5 noise growth from wing to peak). M1 replaces it;
  QC verdicts are re-checked afterwards (one iteration, per plan M1).
* The comb-periodicity score doubles as an RF-state check: an "RF-off" trace
  showing strong ~147 ms autocorrelation periodicity would mean sidebands
  leaked into a line trace (label error) — nobody has verified this
  assumption before; now every trace is checked.
"""

from __future__ import annotations

from typing import Dict, List

import numpy as np
from scipy.signal import medfilt

from . import config as C


# ---------------------------------------------------------------------------
# building blocks
# ---------------------------------------------------------------------------

def boxcar(v: np.ndarray, w: int) -> np.ndarray:
    """Centered boxcar smoothing; ~w/2 samples at each edge are edge-biased,
    which is acceptable for QC because the peak never sits at the very edge
    (and if it does, the edge-margin metric flags the trace anyway)."""
    if w <= 1:
        return v.astype(float)
    return np.convolve(v, np.ones(w) / w, mode="same")


def robust_sigma_from_diff(x: np.ndarray) -> float:
    """Noise sigma from first differences, immune to slow background:
    std(diff)/sqrt(2), using MAD*1.4826 instead of std for outlier immunity."""
    d = np.diff(x)
    return 1.4826 * np.median(np.abs(d - np.median(d))) / np.sqrt(2.0)


def contiguous_fwhm_ms(t_ms: np.ndarray, v: np.ndarray, smooth_w: int = 21) -> float:
    """Model-independent FWHM (ms) from the smoothed, baseline-subtracted line,
    measured on the CONTIGUOUS above-half region CONTAINING THE PEAK.

    Shared helper (2026-07-11) so the union-of-regions bug the M0 audit caught
    cannot recur: taking the span of ALL above-half samples swallows a sweep
    retrace re-crossing the line near the window edge (4207 nm 25 mW: 5.4 ->
    "29" MHz). Always the peak's own contiguous half-max region."""
    sm = boxcar(v, smooth_w)
    sm = sm - np.median(np.sort(sm)[: max(1, int(C.QC_BASELINE_LOW_FRACTION * len(sm)))])
    ipk = int(np.argmax(sm))
    half = 0.5 * sm[ipk]
    lo = ipk
    while lo > 0 and sm[lo - 1] >= half:
        lo -= 1
    hi = ipk
    while hi < len(sm) - 1 and sm[hi + 1] >= half:
        hi += 1
    return float(t_ms[hi] - t_ms[lo])


def wing_mask(v: np.ndarray) -> np.ndarray:
    """Boolean mask of 'wing' samples (far from any signal): smoothed value
    below QC_WING_FRACTION of the smoothed peak-above-baseline."""
    sm = boxcar(v, C.QC_SMOOTH_W)
    base = np.median(np.sort(sm)[: max(1, int(C.QC_BASELINE_LOW_FRACTION * len(sm)))])
    height = sm.max() - base
    return (sm - base) < C.QC_WING_FRACTION * height


def signal_free_segments(sm_minus_base: np.ndarray, sigma_w: float,
                         min_len: int = 120):
    """Contiguous index runs where the smoothed signal is < QC_STEP_WING_NSIGMA
    wing sigmas above baseline — strictly signal-free ground.

    This is the ONLY territory where slow-structure statistics (steps, LF
    power) are meaningful without a physics model: the 10% wing mask still
    contains the line's smooth tail, whose curvature masquerades as
    low-frequency noise (lesson learned twice — first by the step detector's
    closure test, then by 120 spurious lf_ratio flags on bright real traces)."""
    strict = sm_minus_base < C.QC_STEP_WING_NSIGMA * sigma_w
    idx = np.where(strict)[0]
    if len(idx) == 0:
        return []
    breaks = np.where(np.diff(idx) > 5)[0]
    return [seg for seg in np.split(idx, breaks + 1) if len(seg) >= min_len]


# ---------------------------------------------------------------------------
# per-trace metrics
# ---------------------------------------------------------------------------

def trace_metrics(t_ms: np.ndarray, v: np.ndarray) -> Dict[str, float]:
    """All QC metrics for one trace. Returns a flat dict of floats.

    Metric glossary (units):
      baseline_v        robust baseline level [V]
      base_slope_vps    linear baseline slope fitted on wings [V/s]
      sigma_wing_v      wing noise sigma [V]
      height_v          smoothed peak height above baseline [V]
      snr               height_v / sigma_wing_v
      peak_pos_ms       smoothed peak position [ms]
      fwhm_ms           crude smoothed half-max extent [ms] (QC only, never physics)
      edge_margin_ms    distance of the nearer half-max edge from the window end;
                        small => the line is cut by the window
      n_major           count of strongly-smoothed local maxima above
                        QC_MAJOR_PEAK_FRAC of the peak (RF-off should give 1)
      z_spike           worst point-glitch significance vs provisional noise
      z_step            worst wing-level step significance between wing chunks
      clip_run          longest run of samples pinned at the global max (ADC
                        clipping shows as a flat top => long run)
      comb_score        autocorrelation peak in the tooth-lag window (0..1);
                        high => a ~140-150 ms comb is present in the trace
      comb_period_ms    lag of that autocorrelation peak [ms]
    """
    m: Dict[str, float] = {}
    n = len(v)
    sm = boxcar(v, C.QC_SMOOTH_W)

    # --- baseline & wings ---
    base = np.median(np.sort(sm)[: max(1, int(C.QC_BASELINE_LOW_FRACTION * n))])
    wings = wing_mask(v)
    m["baseline_v"] = float(base)
    if wings.sum() > 50:
        # slope in V/s on the wings (drifting PMT background / stray light)
        p = np.polyfit(t_ms[wings] * 1e-3, v[wings], 1)
        m["base_slope_vps"] = float(p[0])
        m["sigma_wing_v"] = float(robust_sigma_from_diff(v[wings]))
    else:  # pathological trace: signal everywhere
        m["base_slope_vps"] = np.nan
        m["sigma_wing_v"] = float(robust_sigma_from_diff(v))

    # --- peak (on smoothed trace) ---
    height = sm.max() - base
    ipk = int(np.argmax(sm))
    m["height_v"] = float(height)
    m["snr"] = float(height / m["sigma_wing_v"]) if m["sigma_wing_v"] > 0 else np.inf
    m["peak_pos_ms"] = float(t_ms[ipk])
    # FWHM and edge margin use the CONTIGUOUS above-half region containing
    # the maximum — never the union of disjoint regions. (independent
    # verification caught the union inflating a healthy 60 ms line to
    # "532 ms" when the triangular sweep's RETRACE re-crossed the line near
    # the window edge, 4207nm 25 mW block.)
    mask = sm - base >= 0.5 * height
    lo = ipk
    while lo > 0 and mask[lo - 1]:
        lo -= 1
    hi = ipk
    while hi < n - 1 and mask[hi + 1]:
        hi += 1
    m["fwhm_ms"] = float(t_ms[hi] - t_ms[lo])
    m["edge_margin_ms"] = float(min(t_ms[lo] - t_ms[0], t_ms[-1] - t_ms[hi]))
    # count of DISJOINT above-half regions: a second one on an RF-off trace
    # is typically the sweep retrace re-crossing the same line (real signal
    # to be masked at fit time, not trace damage)
    m["n_half_regions"] = float(np.sum(mask[1:] & ~mask[:-1]) + (1 if mask[0] else 0))

    # --- structure: how many major bumps? (hysteresis, not local maxima) ---
    # Counting local maxima on a smoothed dome counts noise ripples as peaks
    # (caught by the closure tests — same trap as the 2026-07-11 find_peaks
    # ledger entry). Hysteresis instead: a new bump is counted when the
    # strongly-smoothed trace rises above QC_MAJOR_PEAK_FRAC of the peak,
    # and the counter re-arms only after falling below QC_MAJOR_VALLEY_FRAC
    # — ripples on a single dome can never re-arm it.
    sms = boxcar(v, C.QC_STRUCT_SMOOTH_W) - base
    hi = C.QC_MAJOR_PEAK_FRAC * sms.max()
    lo = C.QC_MAJOR_VALLEY_FRAC * sms.max()
    n_major, armed = 0, True
    for x in sms:
        if armed and x >= hi:
            n_major, armed = n_major + 1, False
        elif not armed and x < lo:
            armed = True
    m["n_major"] = float(n_major)

    # --- point glitches vs provisional signal-dependent noise ---
    resid = v - medfilt(v, kernel_size=5)
    sig_local = m["sigma_wing_v"] * (
        1.0 + C.QC_PROVISIONAL_NOISE_GAIN * np.clip((sm - base) / height if height > 0 else 0.0, 0, 1)
    )
    with np.errstate(divide="ignore", invalid="ignore"):
        m["z_spike"] = float(np.nanmax(np.abs(resid) / sig_local))

    # --- background level steps (light-level jumps, electronics) ---
    # Run ONLY on strictly signal-free ground (< NSIGMA wing sigmas above
    # baseline): the far tail of a bright Lorentzian is smooth SIGNAL, and
    # chunk-median differences there measure tail slope, not steps (bug
    # caught by the closure tests). Each contiguous signal-free segment is
    # linearly detrended (removes residual smooth slope; a sharp step
    # survives at ~half amplitude) and scanned for adjacent-chunk jumps.
    k = C.QC_STEP_CHUNK_SAMPLES
    se = 1.2533 * m["sigma_wing_v"] * np.sqrt(2.0 / k)
    z_step = np.nan
    for seg in signal_free_segments(sm - base, m["sigma_wing_v"], min_len=3 * k):
        r = v[seg] - np.polyval(np.polyfit(np.arange(len(seg)), v[seg], 1),
                                np.arange(len(seg)))
        nchunk = len(seg) // k
        meds = np.array([np.median(r[i * k:(i + 1) * k]) for i in range(nchunk)])
        z = np.max(np.abs(np.diff(meds))) / se if nchunk >= 2 else np.nan
        if np.isnan(z_step) or (np.isfinite(z) and z > z_step):
            z_step = float(z)
    m["z_step"] = z_step

    # --- low-frequency content the diff-based sigma cannot see ---
    # (QC-design critic, 2026-07-11: 50/100 Hz pickup, slow oscillation and
    # PMT drift barely move sample-to-sample differences, so sigma_wing_v
    # alone under-reports them.) Two dedicated metrics:
    #   lf_ratio   — direct (per-segment linearly detrended) sd over the
    #                diff-based sd on STRICTLY signal-free segments; ~1 for
    #                white noise, grows with LF power. Strict segments are
    #                mandatory: the line tail's curvature inside the loose
    #                10% mask fakes lf_ratio ~1.5-1.7 on bright traces.
    #   slope_frac — |baseline slope| x window as a fraction of line height.
    segs = signal_free_segments(sm - base, m["sigma_wing_v"])
    if segs:
        pooled = []
        for seg in segs:
            r = v[seg].astype(float)
            r = r - np.polyval(np.polyfit(np.arange(len(r)), r, 1), np.arange(len(r)))
            pooled.append(r)
        pooled = np.concatenate(pooled)
        direct = 1.4826 * np.median(np.abs(pooled - np.median(pooled)))
        diffsd = 1.4826 * np.median(np.abs(np.diff(pooled))) / np.sqrt(2.0)
        m["lf_ratio"] = float(direct / max(diffsd, 1e-12))
    else:
        m["lf_ratio"] = np.nan
    span_s = (t_ms[-1] - t_ms[0]) * 1e-3
    m["slope_frac"] = float(abs(m["base_slope_vps"]) * span_s / height) \
        if height > 0 and np.isfinite(m["base_slope_vps"]) else np.nan

    # --- ADC clipping: flat run at the global maximum ---
    at_max = np.isclose(v, v.max(), atol=1e-12) | (v >= v.max())
    runs, run = [], 0
    for flag in at_max:
        run = run + 1 if flag else 0
        runs.append(run)
    m["clip_run"] = float(max(runs))

    # --- comb periodicity (RF-state check + ruler sanity) ---
    x = boxcar(v, 5) - base
    x = x - x.mean()
    acf = np.correlate(x, x, mode="full")[n - 1 :]
    acf = acf / acf[0] if acf[0] > 0 else acf
    dt = t_ms[1] - t_ms[0]
    lo, hi = int(C.QC_COMB_LAG_MS[0] / dt), int(C.QC_COMB_LAG_MS[1] / dt)
    hi = min(hi, n - 1)
    seg = acf[lo:hi]
    m["comb_score"] = float(seg.max()) if len(seg) else np.nan
    m["comb_period_ms"] = float((lo + int(np.argmax(seg))) * dt) if len(seg) else np.nan

    return m


# ---------------------------------------------------------------------------
# hard QC flags (pre-registered; thresholds documented in config)
# ---------------------------------------------------------------------------

def hard_flags(m: Dict[str, float], rf_on: bool) -> List[str]:
    """Threshold-based failures for one trace. Empty list = pass.

    These are the ONLY criteria that may exclude a canonical trace from
    headline fits (plan: QC-based, never result-based). Sibling-comparison
    *outliers* (see audit) are reported but do not auto-exclude — they go to
    the experimenter, who is the instrument for apparatus context.
    """
    flags = []
    if m["clip_run"] >= C.QC_CLIP_RUN_MAX:
        flags.append(f"clipped (run {int(m['clip_run'])} at max)")
    if not np.isnan(m["edge_margin_ms"]) and m["edge_margin_ms"] < C.QC_EDGE_MARGIN_MS:
        flags.append(f"peak cut by window (margin {m['edge_margin_ms']:.0f} ms)")
    if m["z_spike"] > C.QC_SPIKE_Z:
        flags.append(f"point glitch (z={m['z_spike']:.1f})")
    if (not rf_on) and not np.isnan(m["z_step"]) and m["z_step"] > C.QC_STEP_Z:
        # RF-off only: on rulers the weak n=+-2 teeth sit INSIDE the
        # "signal-free" mask (their ~20 mV height is comparable to 3 wing
        # sigmas), so chunk-median jumps there measure tooth structure, not
        # background steps (blind spot found in the first real-data audit).
        # Ruler background integrity is checked model-aware in M2 instead.
        flags.append(f"wing level step (z={m['z_step']:.1f})")
    if m["snr"] < C.QC_MIN_SNR:
        if rf_on:
            # Rulers are NEVER excluded on SNR: cold rulers at SNR 2-6 are
            # handled by M2's pooled / bright-tooth path by design. The flag
            # only routes them there. (QC-design critic: a uniform SNR floor
            # must not exist where SNR tracks the physics lever arm.)
            flags.append(f"low-SNR ruler ({m['snr']:.1f}) — M2 pooled path, not excluded")
        else:
            # For RF-off lines SNR tracks vapor density — the beta_self lever
            # arm — so this flag is REVIEW-ONLY and any exclusion decision
            # must document why it is not density-correlated selection.
            flags.append(f"SNR {m['snr']:.1f} < {C.QC_MIN_SNR} (review-only: "
                         "SNR tracks the density lever arm)")
    if not np.isnan(m.get("lf_ratio", np.nan)) and m["lf_ratio"] > C.QC_LF_RATIO_MAX:
        flags.append(f"low-frequency wing power (lf_ratio {m['lf_ratio']:.2f})")
    if (not rf_on) and not np.isnan(m.get("slope_frac", np.nan)) \
            and m["slope_frac"] > C.QC_SLOPE_FRAC_MAX:
        # RF-off only: on weak rulers a few mV of ordinary PMT drift is
        # unavoidably a large fraction of a small tooth, and M2's per-trace
        # fitted background absorbs it — flagging there is pure noise.
        flags.append(f"strong baseline slope ({100*m['slope_frac']:.1f}% of height over window)")
    if (not rf_on) and m["n_major"] > 1.5:
        # Verified cause in this archive (4207nm 25 mW block): the triangular
        # sweep's retrace re-crossing the SAME line near the window edge —
        # i.e. real signal, handled by masking at fit time (M3), not by
        # discarding the trace. Flag surfaces it for the mask bookkeeping.
        flags.append(
            f"second structure in RF-off trace (n={int(m['n_major'])}; "
            "likely sweep-retrace crossing — mask at fit time)")
    if (not rf_on) and m["comb_score"] > C.QC_COMB_SCORE_RFOFF_MAX:
        flags.append(f"comb periodicity in RF-off trace (score {m['comb_score']:.2f})")
    if rf_on and m["comb_score"] < C.QC_COMB_SCORE_RFON_MIN:
        flags.append(f"no comb in RF-on ruler (score {m['comb_score']:.2f})")
    return flags


def ingest_flags(info: Dict[str, int]) -> List[str]:
    """Hard flags derived from the loader's dropout bookkeeping (see
    :func:`rb5s6s.ingest.load_trace`): truncated or dropout-riddled exports
    are excluded from headline fits like any other hard-QC failure."""
    flags = []
    if info["n_valid"] < C.QC_MIN_VALID_POINTS:
        flags.append(f"short/truncated export ({info['n_valid']} valid samples)")
    if info["empty_interior"] > C.QC_MAX_INTERIOR_DROPOUTS:
        flags.append(f"dropout-riddled export ({info['empty_interior']} interior empty rows)")
    return flags


def sibling_zscores(value: float, sib_values: np.ndarray) -> float:
    """Robust z of a value against its same-condition siblings (median/MAD).
    With 4-5 siblings this is indicative, not decisive — audit output only.

    The MAD is floored at QC_SIBLING_MAD_FLOOR_FRAC of |median|: with a
    handful of siblings the raw MAD can quantize to ~0 (identical rounded
    noise metrics), which exploded z to 1e14 in the first real-data audit.
    The floor also gives |z|>=5 a physical meaning: at a 2% floor, 5 sigma
    implies at least a 10% relative deviation — safely beyond the known
    2-4% shot-to-shot amplitude repeatability of the campaign."""
    med = np.median(sib_values)
    mad = 1.4826 * np.median(np.abs(sib_values - med))
    scale = max(mad, C.QC_SIBLING_MAD_FLOOR_FRAC * abs(med), 1e-12)
    return float((value - med) / scale)
