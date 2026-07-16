"""
Tunable analysis parameters and paths
=====================================

Everything in this file is a *choice* — a knob we are allowed to turn — as
opposed to :mod:`rb5s6s.constants`, which holds quantities fixed by nature or
the apparatus. Rules:

* Changing a value here must never change what the code *can* do, only how it
  does it. If moving a value changes the physics, it is in the wrong file.
* Every knob is documented: what it does, why the default, what breaks if you
  push it too far.
* Result-sensitivity to these knobs is itself a deliverable (the systematics
  scans re-run the pipeline over knob ranges).
"""

from pathlib import Path

from .constants import W0_PRIOR_M, transit_fwhm_from_w0

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = REPO_ROOT / "data_raw"        # frozen dataset, committed to git
MANIFEST_CSV = DATA_RAW_DIR / "MANIFEST.csv" # one row per unique trace
RESULTS_DIR = REPO_ROOT / "results"          # all generated outputs; git-ignored

ARCHIVE_SOURCE_DIR = Path(
    "/Users/michelangelodondi/Documents/GitHub/Rb-5S-to-6S-broadening/data"
)
"""Machine-specific location of the ORIGINAL 2025 archive (old repository).
Only needed to (re)run scripts/import_data.py on Michelangelo's machine.
Everyone else: data_raw/ ships inside this repository — you never need this."""


def results_fingerprint(results_dir=None):
    """A deterministic short hash over the git-TRACKED results CSVs — the
    committed inputs the figures are drawn from.

    `make_figures.py` embeds this in each figure's PNG metadata at draw time,
    and `tests/test_figures_fresh.py` checks the committed figures still carry
    the CURRENT fingerprint. So a stale figure (a CSV moved but the figure was
    not redrawn — the failure that once left fig1/3/5/6 showing an old beta)
    is caught mechanically, without a matplotlib-version-fragile pixel compare.

    Over the git-TRACKED CSVs specifically, for two reasons: (1) it covers every
    committed result, so it cannot miss a figure's input (a hand-listed input
    set can, and did); (2) it must exclude gitignored scratch dumps like
    `qc_metrics.csv` — those are present in a dev checkout but not in CI's, so
    hashing the raw directory gives a different value on each and the check
    fails spuriously. `git ls-files` is exactly the committed set CI sees."""
    import hashlib
    import subprocess
    d = Path(results_dir) if results_dir else RESULTS_DIR
    try:
        out = subprocess.run(["git", "-C", str(REPO_ROOT), "ls-files", "results/*.csv"],
                             capture_output=True, text=True, check=True).stdout
        rels = sorted(out.split())
    except Exception:                                   # no git (e.g. a tarball): best effort
        rels = sorted(str(p.relative_to(REPO_ROOT)) for p in d.glob("*.csv"))
    h = hashlib.sha256()
    for rel in rels:
        p = REPO_ROOT / rel
        if p.exists():
            h.update(rel.encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]

# --------------------------------------------------------------------------
# M0 — ingest & QC
# --------------------------------------------------------------------------
CSV_HEADER_LINES = 2
"""LeCroy export format: 2 header lines ('x-axis,2' / 'second,Volt'), then
time,volts rows. A parse failure on any file must raise, never skip silently."""

QC_BASELINE_LOW_FRACTION = 0.20
"""Fraction of the lowest-voltage samples used for the robust baseline
estimate in QC summaries (the physics fits use a fitted background instead,
so this only feeds QC metrics, not results)."""

TRACE_MIN_VALID_POINTS = 100
"""Loader floor: below this many valid samples a file is garbage and raises.
Between this and QC_MIN_VALID_POINTS the trace loads but QC hard-flags it."""

QC_MIN_VALID_POINTS = 1990
"""Traces with fewer valid samples than this are hard-flagged (the benign
LeCroy edge-dropout quirk costs at most ~4 rows; more means truncation)."""

QC_MAX_INTERIOR_DROPOUTS = 5
"""Interior (non-edge) empty-voltage rows beyond this hard-flag the trace as
a dropout-riddled export (observed once: 4192nm_eom_070c3, ~950 interior)."""

QC_SMOOTH_W = 21
"""Boxcar width (samples; 10.5 ms) for peak/baseline QC metrics. Narrow enough
to keep a ~60 ms line intact, wide enough to kill sample noise."""

QC_STRUCT_SMOOTH_W = 41
"""Stronger boxcar (20.5 ms) for the bump-counting metric. Lesson learned
(2026-07-11 ledger): structure detection on lightly-smoothed noise invents
periodic peaks — count bumps only after aggressive smoothing."""

QC_WING_FRACTION = 0.10
"""Samples whose smoothed signal is below this fraction of the peak height
count as 'wings' (baseline/noise territory)."""

QC_MAJOR_PEAK_FRAC = 0.50
"""A bump counts as 'major' when the strongly-smoothed trace rises above this
fraction of the peak (hysteresis high threshold)."""

QC_MAJOR_VALLEY_FRAC = 0.25
"""The bump counter re-arms only after the trace falls below this fraction
(hysteresis low threshold). Noise ripples on one dome never dip this far, so
they cannot double-count — the failure mode the closure tests caught."""

QC_PROVISIONAL_NOISE_GAIN = 5.0
"""PROVISIONAL signal-dependent noise scale for the glitch detector only:
sigma(V) ~ sigma_wing * (1 + gain * V/height). Motivated by the old
pipeline's residuals (~x5 wing-to-peak growth). Module M1 replaces this with
the measured noise(V); QC verdicts are then re-checked (one iteration)."""

QC_SPIKE_Z = 10.0
"""Point-glitch threshold (in provisional sigma units). Deliberately loose
until M1's real noise model tightens it — QC must not over-reject."""

QC_STEP_WING_NSIGMA = 3.0
"""Step detection runs ONLY where the smoothed signal is below this many wing
sigmas above baseline (strictly signal-free ground). Lesson from the closure
tests: a Lorentzian tail is smooth *signal* far above noise over half the
window, and a step detector that treats it as baseline reads the tail slope
as a step (z~37 on a clean trace). Under the line itself, background steps
are indistinguishable from lineshape without a physics model — those are
caught later by fit residuals (M3), not by M0."""

QC_STEP_CHUNK_SAMPLES = 40
QC_STEP_Z = 7.0
"""Contiguous signal-free wing segments are linearly detrended, then chunked
(QC_STEP_CHUNK_SAMPLES each); a level step shows as an adjacent-chunk median
jump above QC_STEP_Z times its standard error.

HONEST SCOPE (from the closure tests): this catches SMALL background steps
(below ~3 wing sigmas — larger ones classify as signal and leave the mask),
so it is most effective on dim traces where 3 sigma is a meaningful fraction
of the line. Large steps under a bright line are indistinguishable from
lineshape without a physics model and are caught by M3's fit residuals
instead. Threshold 7.0: synthetic clean-trace null max-|z| is 2-3.9, but
REAL traces reach ~4.7-5.4 from pure noise (correlated samples + no
look-elsewhere correction in this statistic — established by independent
verification of the first audit, which refuted a z=5.4 flag on
4154nm_025mw3 via BIC model comparison). 7.0 clears the real-data null;
the proper renormalized statistic belongs to M1. Also note: slow shared
baseline bows exist block-wide (e.g. ~0.5 mV in the whole 4207nm 70C
block), which per-trace step statistics cannot and should not flag —
low-order baseline terms in the M3 fits absorb them."""

QC_CLIP_RUN_MAX = 4
"""Consecutive samples pinned at the global max that count as ADC clipping
(a noisy unclipped peak pins 1-2 samples; a flat top pins many)."""

QC_EDGE_MARGIN_MS = 25.0
"""Minimum distance of the half-max edge from the window end; below this the
line is considered cut by the acquisition window."""

QC_MIN_SNR = 8.0
"""SNR reporting floor. NOT an unconditional exclusion (QC-design critic,
2026-07-11): for RF-on rulers the flag only routes the trace to M2's pooled
/ bright-tooth path; for RF-off lines it is review-only, because line SNR
tracks vapor density — the very lever arm beta_self regresses on — and an
automatic floor there would be result-correlated selection in disguise."""

QC_LF_RATIO_MAX = 1.5
"""Flag when the direct (detrended) wing sd exceeds the diff-based wing sd
by this factor: white noise gives ~1; 50/100 Hz pickup, oscillations and
drift raise it (they are nearly invisible to sample-to-sample differences —
critic finding). Calibrated on synthetics in the closure tests."""

QC_SLOPE_FRAC_MAX = 0.05
"""Flag when |baseline slope| x window exceeds this fraction of the line
height — measured-then-ignored drift was a critic finding; a linear fit
background absorbs small slopes, but 5%+ deserves eyes."""

QC_SIBLING_MAD_FLOOR_FRAC = 0.02
"""Floor on the sibling MAD as a fraction of the median metric value (see
qc.sibling_zscores). Chosen so that a |z|>=5 sibling outlier implies >=10%
relative deviation — beyond the campaign's ordinary 2-4% shot-to-shot
amplitude repeatability."""

QC_COMB_LAG_MS = (110.0, 190.0)
"""Autocorrelation lag window (ms) where the two-photon comb periodicity
(~147 ms tooth spacing) must appear for RF-on rulers."""

QC_COMB_SCORE_RFON_MIN = 0.15
"""RF-on ruler must show at least this autocorrelation peak in the comb-lag
window (else: no usable comb)."""

QC_COMB_SCORE_RFOFF_MAX = 0.35
"""An RF-off trace showing MORE comb periodicity than this is suspicious
(possible RF-state label error). Not 0: a single line still autocorrelates a
little at long lags through its wings."""

# --------------------------------------------------------------------------
# M1 — noise model
# --------------------------------------------------------------------------
NOISE_NBINS = 10
"""Signal-level quantile bins for the sigma(V) curve. Quantile binning makes
the wing-dominated low bins huge (precise floor) and leaves a few small
peak-region bins (they carry the b/c terms; the law fit weights by n)."""

NOISE_MIN_BIN_SAMPLES = 40
"""Bins with fewer second-diff samples than this are dropped (their MAD
sigma estimate is too unstable to constrain the law)."""

NOISE_BIC_MARGIN = 6.0
"""The quadratic (multiplicative-noise) term c*V^2 enters only when it
improves BIC by at least this margin — 'strong evidence' on the Kass-Raftery
scale; below that the 2-parameter shot-noise law wins by parsimony."""

NOISE_MAX_LAG = 50
NOISE_ACF_TRUNC = 0.05
"""Wing-ACF integration for tau_int stops at NOISE_MAX_LAG samples or when
the autocorrelation drops below NOISE_ACF_TRUNC (standard truncated
estimator; prevents summing pure noise tails)."""

# --------------------------------------------------------------------------
# M2 — frequency-axis (ruler) fits
# --------------------------------------------------------------------------
RULER_DELTA_RANGE_MS = (130.0, 165.0)
"""Physical search window for the comb tooth spacing. Campaign quick-look:
147 ± 4 ms across 22 blocks; the window is wide enough for real drifts and
narrow enough to forbid period-multiple lock-in (< half a tooth off) — the
failure the independent audit demonstrated on cold-block alignment."""

RULER_DELTA_FALLBACK_MS = 147.0
"""Init fallback when a trace's autocorrelation is too weak to seed the
spacing (cold rulers). Only the INIT falls back; the fit still determines
delta freely inside RULER_DELTA_RANGE_MS, and the fit result records
init_fallback=True so M2's combination can audit fallback usage."""

RULER_ACF_MIN_SCORE = 0.10
"""Minimum autocorrelation peak in the search window to trust the ACF init."""

RULER_TOOTH_WIDTH_INIT_MS = 55.0
"""Initial shared tooth width (the teeth ARE the spectral line: ~50-65 ms
at campaign conditions). Fit bounds 15-120 ms."""

RULER_FREE_MIN_HEIGHT_FRAC = 0.15
"""In the free-center diagnostic, a tooth is freed only if its constrained
height exceeds this fraction of the block's tallest tooth — keeps the
nonlinearity map from fitting phantom outer teeth to noise."""

RULER_NLMAP_NBINS = 12
"""Window-position bins for the pooled sweep-nonlinearity map ν(t)."""

# --------------------------------------------------------------------------
# M3 — lineshape fit
# --------------------------------------------------------------------------
# --- RF-off fit window (ADAPTIVE) ---
# The fit window around each line EXCLUDES the off-center-sweep MIRROR crossing
# — when the triangular sweep is not centered on the transition, the down-ramp
# re-crosses the line ~40 MHz away (fold near 432 ms in the 4207 blocks;
# 4207@25mW has a 79%-of-peak mirror in 4/5 traces). A single-line fit over the
# full 1 s window treats that mirror as unmodelled signal and biases
# baseline/width (whole-dataset scan 2026-07-11, user-flagged: 8 RF-off traces,
# almost all 4207). The half-width now SCALES with each trace's own measured
# FWHM rather than a fixed value, so it keeps ~the same number of Lorentzian
# wings whether the line is narrow (cold/dim) or collisionally broadened —
# cutting too tight would clip the fat wings where gamma_coll lives and bias it.
FIT_HALFWIDTH_FWHM_MULT = 3.5
"""Fit half-width = this multiple of the trace's measured FWHM. 3.5 FWHM keeps
the Lorentzian wings to ~1%."""

FIT_HALFWIDTH_MIN_MHZ = 9.0
"""Floor on the fit half-width (transition axis) — a dim/noisy FWHM estimate
must not shrink the window below a few core widths."""

FIT_HALFWIDTH_MAX_MHZ = 25.0
"""Cap on the fit half-width (transition axis): must stay well below the
~40 MHz mirror separation so the window always excludes it, even if a
condition is anomalously broad."""

TRANSIT_FWHM_PLACEHOLDER_MHZ = transit_fwhm_from_w0(W0_PRIOR_M, 110.0)
"""Central transit FWHM at 110 C (transition axis, bare kernel), scaled sqrt(T)
elsewhere. DERIVED from the corrected transit<->w0 physics
(constants.transit_fwhm_from_w0, Lehmann-validated) at the W0_PRIOR central
(50 um) => ~1.20 MHz. This rides on w0, which is OPEN until the fixed-lock session
knife-edge, so every M3 absolute width that uses this is PRELIMINARY; the
degeneracy-robust total width and its T-trend are the trustworthy shakedown
outputs. Do not quote a number built on this without the w0 caveat.

History: was a hand-set 0.9 (tied to the OLD buggy transit MC, which was ~2x
too narrow); re-derived 2026-07-12 when the MC flux bug was fixed and w0
re-centred 32 -> 50 um. See constants.W0_PRIOR_M."""

RAMP_GEOMETRY_CONFIGS_UM = {
    "L (60 um, Oct)": 60.0,
    "M (50 um, archival)": 50.0,
    "S (16 um, Oct)": 16.0,
}
"""Beam-waist configurations for the ramp-geometry predictions (PLAN §8.1;
run_ramp_geometry.py). M is the 2025 archival prior (re-centred 32 -> 50 um
2026-07-12, see constants.W0_PRIOR_M); L and S are target for a fixed-lock sessions, all
pending knife-edge measurement (OPEN)."""

RAMP_COLLECTION_HALFLENGTH_MM_ENVELOPE = (1.0, 2.0, 4.0)
"""Envelope of the fluorescence-collection axial half-length Z_c: the f=18 mm
lens + PMT geometry collects light from 'many mm' of the beam (user,
2026-07-11 session), value unmeasured. OPEN until the fixed-lock session
collection-profile measurement; every ramp-geometry moment coefficient
(including the g1 sign-flip location) depends on it, hence an envelope,
never a single number."""

# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------
RNG_SEED = 20260711
"""Single seed for every stochastic step (synthetic data, Monte Carlo error
propagation). Change only deliberately; closure tests pin coverage at this
seed and at least two others."""
