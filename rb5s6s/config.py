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
* Result-sensitivity to these knobs is reported (the systematics
  scans re-run the pipeline over knob ranges).
"""

import os
from pathlib import Path

# W0_PRIOR_M and transit_fwhm_from_w0 are used below; RHO_RETRO,
# RHO_RETRO_ERR and W0_BAND_M are deliberate RE-EXPORTS so the scripts, which
# already import config as C, can reach every prior through one namespace
# instead of importing constants separately.
from .constants import (  # noqa: F401
    RHO_RETRO, RHO_RETRO_ERR, W0_BAND_M, W0_PRIOR_M, transit_fwhm_from_w0)

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_DIR = REPO_ROOT / "data_raw"        # frozen dataset, committed to git
MANIFEST_CSV = DATA_RAW_DIR / "MANIFEST.csv" # one row per unique trace
RESULTS_DIR = REPO_ROOT / "results"          # all generated outputs; git-ignored

ARCHIVE_SOURCE_DIR = Path(os.environ.get(
    "RB5S6S_ARCHIVE_SOURCE_DIR", "~/rb-2025-archive/data")).expanduser()
"""Machine-specific location of the ORIGINAL 2025 archive (old repository).
Only needed to (re)run scripts/import_data.py on the machine that holds
that archive, and read from RB5S6S_ARCHIVE_SOURCE_DIR when that variable
is set. Everyone else: data_raw/ ships inside this repository, so you
never need this."""


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
"""Agilent/Keysight InfiniiVision export format: 2 header lines
('x-axis,N' / 'second,Volt'), then
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
InfiniiVision edge-dropout quirk costs at most ~4 rows; more means
truncation)."""

QC_MAX_INTERIOR_DROPOUTS = 5
"""Interior (non-edge) empty-voltage rows beyond this hard-flag the trace as
a dropout-riddled export (observed once: 4192nm_eom_070c3, ~950 interior)."""

QC_SMOOTH_W = 21
"""Boxcar width (samples; 10.5 ms) for peak/baseline QC metrics. Narrow enough
to keep a ~60 ms line intact, wide enough to kill sample noise."""

QC_STRUCT_SMOOTH_W = 41
"""Stronger boxcar (20.5 ms) for the bump-counting metric. Structure detection
on lightly-smoothed noise invents periodic peaks (2026-07-11 ledger) — count
bumps only after aggressive smoothing."""

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

SCOPE (from the closure tests): this catches SMALL background steps
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

# --- ruler fit VALIDITY (pre-registered in docs/notes/ruler_validity_and_trim_prereg.md) ---
RULER_FOLD_SEED = "proximity"
"""Which rule numbers the teeth of a comb fit: `amplitude` or `proximity`.

The comb phase scan fixes t0 modulo the tooth spacing. Which of the peaks it
found is then CALLED the carrier is the integer fold, and it is the whole of the
numbering. `proximity` answers it with the tooth nearest the acquisition window
centre, which is a fact about where the comb sits in the window rather than
about the comb, and it numbered 54 of the 104 campaign combs one slot out.
`amplitude` answers it from the sideband heights at the measured drive depth,
with the carrier left out because its height carries residual amplitude
modulation (amendment 6 section F3).

Landed 2026-08-06 as the adjudicated action RT12 of the frequency-calibration
red team, answering the question amendment 5 section E4 parked. `proximity` is
kept because the re-index ladder is calibrated on combs that are mislabelled to
begin with, and the only honest way to build one is to number it the old way."""

RULER_MOD_DEPTH_2BETA = 1.569
"""The drive depth, written as 2 beta and never as a bare depth in radians.

Measured in amendment 6 section F1 on the 41 combs whose numbering the verdict
passes cleanly and whose first-order pair stands above five times the fit
residual: median 2 beta = 1.569, standard deviation 0.058, range 1.449 to 1.730,
so one depth to four per cent. The fold seed reads it through the tooth height
law, J_k(2 beta) squared, and only through the SHAPE of the resulting pattern.
Nothing in the seed reads the depth's absolute value, which is why moving it
anywhere inside the measured band does not change a fold."""

RULER_TOP3_GATED = False
"""Whether the top-three amplitude verdict is allowed to ACT on the
calibration, or is only recorded.

False on landing, and the reason is in the open question at the end of the
pre-registration note. The rule fails 54 of the 104 fitted campaign rulers, it
fails CLEAN synthetic combs built from the repository's own Bessel amplitude
law once the modulation index 2*beta exceeds about 2.7 (where the second-order
sidebands legitimately outrank the first), and a parallel measurement finds it
passing an injected fold that costs 7.9% in rate. An instrument that fires on
half the population, on clean physics, and not on the defect it was written for
is not yet a gate. The whole ladder still runs and every outcome is written to
results/ruler_traces.csv as a diagnostic, so the population can be studied
without any of it touching a block, the campaign rate or the nonlinearity map.

Setting this True is a decision for the owner, and it changes numbers."""

RULER_TOP3_TIE_SIGMA = 1.0
"""Tie allowance for the top-three tooth-amplitude rule, in units of the fit's
own residual RMS. A required first-order tooth ranking FOURTH but within this
many residual RMS of the third-ranked height is recorded as a MARGINAL pass.
One residual RMS is the scale on which two heights are not distinguishable, so
this is the smallest defensible allowance; the pre-registration grants no
other. A marginal pass counts as a pass for the pipeline and as a failure for
figure eligibility."""

RULER_REINDEX_CHI2_TOL = 1e-3
"""How much a re-indexed comb fit may worsen chi2_red and still be accepted,
as a fraction of the failing fit's own chi2_red.

Not zero, and the reason is structural rather than a preference. Relabelling a
RIGID grid by whole slots is chi-squared DEGENERATE: the same seven free
heights describe the same peaks, and the only difference is which slots fall
outside the acquisition window. Measured on the closure synthetics, the correct
relabelling changes chi2_red by ~1e-4 relative, with the sign set by numerical
noise, so a strict-improvement test decides the right answer by coin flip and
quarantines clean combs. The tolerance must also stay tight enough to REJECT a
relabelling of a contaminated grid, which passes the amplitude rule while
keeping the contracted spacing that caused the failure. Measured on the folded
synthetics, that false rescue costs 4e-3 relative and the excision rung then
recovers the true spacing. 1e-3 separates the two by an order of magnitude on
each side."""

RULER_REINDEX_MAX_TRIALS = 5
"""Cap on refits per trace inside the re-index ladder: four comb-phase shifts
(j = -2, -1, +1, +2) plus one excision refit. The cap equals the full ladder,
so it forbids a wider search rather than truncating the ladder. A trace needing
more is quarantined with a recorded reason instead."""

# --- residual-tail trimmer (rb5s6s/trim.py, pre-registered in the same note,
# section 5 for the parameters and section 6 for the calibration) ---
TRIM_SMOOTH_W = 21
"""Boxcar width (samples) the trimmer smooths residuals with. ADOPTED from
QC_SMOOTH_W rather than tuned: the quality module already decided what width
keeps a ~60 ms line intact while killing sample noise, and a second answer to
the same question would be a knob with no owner."""

TRIM_CUSUM_DRIFT = 0.5
"""Allowance subtracted from each normalized residual sample before it
accumulates, in units of the smoothed residual's own sigma. 0.5 is the standard
allowance of a one-sided cumulative-sum detector: it is the half-shift the
detector is tuned to find, so a series with no shift drifts down and only a
sustained positive excursion climbs."""

TRIM_CUSUM_H = 8.0
"""Cumulative-sum threshold, in accumulated sample sigmas.

Set by the null calibration of the pre-registration's section 6: 10,000
synthetic traces carrying the fitted model plus noise and no tail, each run
through the full two-sided trim path at the campaign geometry (2000 samples, a
core guard leaving about 890 samples of scannable tail on each side, which is
the longest scan any stage performs and therefore the hardest case).

The calibration returned a degenerate answer to the question as pre-registered
and the resolution is recorded rather than hidden. TRIM_MIN_RUN alone already
holds the false-alarm rate below the 1-in-297 target at EVERY threshold on the
grid, down to 0.5, because a noise excursion that keeps accumulating for 40
samples is already rare. "The smallest threshold meeting the target" would
therefore have selected an arbitrarily small number. The threshold is instead
the smallest integer at which the calibration produced no false alarm AT ALL,
which is a strictly stronger criterion than the pre-registered one. The largest
null statistic seen across the 10,000 traces was 7.72.

Guarded by tests/test_trim.py under --runslow, which re-runs the calibration
and fails if this value stops clearing the null."""

TRIM_MIN_RUN = 40
"""Samples the cumulative sum must keep RISING after an onset before the
excursion counts as sustained. 40 samples is 20 ms at the campaign sampling
interval, below the narrowest feature the apparatus can produce, so nothing
physical is cut by a run shorter than this. It also sits above TRIM_SMOOTH_W,
which is what makes a point glitch undetectable as a tail whatever its height:
the smoother spreads a single sample over exactly TRIM_SMOOTH_W samples, so a
glitch can accumulate for at most that many."""

TRIM_CORE_GUARD_FWHM_MULT = 1.0
"""Fitted full widths on each side of the fitted structure that the trimmer may
never enter. One full width beyond the structure is inviolable, so the trimmer
cannot reach the line it is protecting even when that line is dim and its wings
are the only thing standing above noise."""

# --- group outlier rule (pre-registered in the same note, amendment 2 B4,
#     recalibrated against the null in amendment 3) ---
OUTLIER_ALPHA = 0.05
"""Two-sided significance of the group outlier test, before the Bonferroni
correction over the n members of the group and the m statistics tested on each.
Five per cent is the conventional level and no other was considered.

Amendment 2 read this level off a t quantile. Amendment 3 keeps the level and
reads the threshold off the null instead, because the statistic is not a t. It
is now the target the calibration below hits, not a construction."""

OUTLIER_THRESHOLDS = {
    "group": {
        (4, 1): 6.909, (5, 1): 7.926, (6, 1): 5.530, (7, 1): 5.854, (8, 1): 4.915,
        (4, 2): 9.902, (5, 2): 11.411, (6, 2): 7.163, (7, 2): 7.611, (8, 2): 6.072,
    },
    "sibling": {
        (4, 1): 61.520, (5, 1): 13.847, (6, 1): 13.004, (7, 1): 8.252, (8, 1): 8.102,
        (4, 2): 122.507, (5, 2): 19.884, (6, 2): 18.771, (7, 2): 10.677, (8, 2): 10.506,
    },
}
"""Deviation above which the most deviant of n group members is removed, keyed
by the scaling the deviation carries, then by the group size n and the number of
statistics m tested on each member.

Each entry is the 95th percentile of the group's largest deviation over
2,000,000 groups of independent standard Gaussians, so the per-group
false-alarm rate is five per cent by construction rather than by assumption.
Monte Carlo error on each entry is 0.005 to 0.03 outside the two n=4 sibling
cells. Amendment 3 of docs/notes/ruler_validity_and_trim_prereg.md records the
calibration and the values these replace.

The two scalings are two different statistics and they need two different
nulls.

`group` is the deviation :func:`rb5s6s.qc.group_outlier` computes: the median
and the scaled median absolute deviation are taken over the whole group,
including the member being tested. Population A, the ruler spacings.

`sibling` is the deviation :func:`rb5s6s.qc.sibling_zscores` computes: each
member is centred and scaled by the OTHER n-1 members. Population B, the line
heights and widths. Dropping the member from its own scale gives the statistic
much heavier tails, so the same nominal level needs a threshold roughly twice
as high, and at n=4 the scale is a three-point median absolute deviation and
the tail is heavy enough that no useful threshold exists. Those two cells are
carried at the value the null returns rather than being capped, which leaves
the rule inert at n=4 for population B. Whether to test groups of four on a
sibling scaling at all is a policy question amendment 3 puts to the owner.

The null omits the QC_SIBLING_MAD_FLOOR_FRAC floor, which can only shrink a
deviation, so the calibrated thresholds cannot fire more often than five per
cent on real groups.

Guarded by tests/test_trim.py, which re-runs the calibration under --runslow
and fails if these values stop returning five per cent."""

OUTLIER_MIN_GROUP = 4
"""Smallest group the outlier rule will test. With three members the median
absolute deviation is a single number, so a rule built on it reports the
arithmetic of three points rather than a property of the group."""

OUTLIER_MAD_FLOOR_FRAC = 1e-3
"""Floor on the scaled median absolute deviation of the ruler spacing, as a
fraction of the group median, so a group that happens to agree closely cannot
divide by nearly zero and manufacture an outlier.

Set by what the fit can resolve rather than by any campaign number: the rigid
grid places six spacings across a window sampled every 0.5 ms, so the spacing
is resolved to at best 0.5/6 = 0.083 ms, which is 5.7e-4 of a 147 ms spacing.
One part in a thousand sits just above that, so a real fit can never reach the
floor, while a one per cent disagreement is still ten scale units wide."""

# --------------------------------------------------------------------------
# M3 — lineshape fit
# --------------------------------------------------------------------------
# --- RF-off fit window (ADAPTIVE) ---
# The fit window around each line EXCLUDES the off-center-sweep MIRROR crossing
# — when the triangular sweep is not centered on the transition, the down-ramp
# re-crosses the line ~40 MHz away (fold near 432 ms in the 4207 blocks;
# 4207@25mW has a 79%-of-peak mirror in 4/5 traces). A single-line fit over the
# full 1 s window treats that mirror as unmodelled signal and biases
# baseline/width (whole-dataset scan 2026-07-11, flagged during curation: 8 RF-off traces,
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
(64 um) => ~0.93 MHz. This rides on w0, which is an ADOPTED prior until the
fixed-lock session
knife-edge, so every M3 absolute width that uses this is PRELIMINARY; the
degeneracy-robust total width and its T-trend are the trustworthy shakedown
outputs. Do not quote a number built on this without the w0 caveat.

History: was a hand-set 0.9 (tied to the OLD buggy transit MC, which was ~2x
too narrow); re-derived 2026-07-12 when the MC flux bug was fixed and w0
re-centred 32 -> 50 um; re-derived again 2026-08-01 (v3.0.0) when w0 moved
50 -> 64 um on the adopted lineage measurement, narrowing this to ~0.93 MHz.
See constants.W0_PRIOR_M."""

RAMP_GEOMETRY_CONFIGS_UM = {
    "L (60 um, config)": 60.0,
    # the archival entry tracks the prior, so it can never drift from it
    f"M ({W0_PRIOR_M * 1e6:.0f} um, archival)": W0_PRIOR_M * 1e6,
    "S (16 um, config)": 16.0,
}
"""Beam-waist configurations for the ramp-geometry predictions (PLAN §4;
run_ramp_geometry.py). M is the 2025 archival prior (re-centred 32 -> 50 um
2026-07-12, see constants.W0_PRIOR_M); L and S are target for a fixed-lock sessions, all
pending knife-edge measurement (OPEN)."""

RAMP_COLLECTION_HALFLENGTH_MM_ENVELOPE = (1.0, 2.0, 4.0)
"""Envelope of the fluorescence-collection axial half-length Z_c: the 2025
single f=18 mm lens + PMT geometry collects light from 'many mm' of the beam
(recollection, 2026-07-11 session), value unmeasured. Z_c is not a free
parameter: for a lens imaging the beam onto the detector it is the axial
field of view L_par/(2M), M = v/u with 1/u + 1/v = 1/f, where L_par is the
detector's active extent ALONG the beam image. The PMT of record is the
side-on Hamamatsu R636-10 (datasheet TPMS1016E; experimenter-confirmed
2026-07-23), whose cathode is a 3 x 12 mm rectangle -- rotation alone is a x4
lever on Z_c, and the cathode was LANDSCAPE through the 2025 campaign
(experimenter-confirmed 2026-07-23), so L_par = 12 mm and Z_c = 6/M mm.

Two of the three inputs are now fixed and the third is estimated: M = 2.5-3
for the bare f18 (experimenter, 2026-07-29 -- an ESTIMATE, u and v unmeasured),
giving Z_c = 2.0-2.4 mm. This envelope is DELIBERATELY NOT narrowed to it. An
estimate is not a measurement, and every ramp-geometry moment coefficient --
including whether the g1 sign flip at config S occurs at all (crossover
Z_c/z_R ~ 1.12) -- depends on Z_c, so the published coefficients stay bracketed
until u and v are read off a ruler. What the estimate does buy is that it lands
on the envelope's middle entry, so the 2 mm figures quoted throughout are the
ones the geometry actually supports. A proposed session replaces the bare f18
with a two-lens relay plus an image-plane slit, which makes Z_c settable
hardware and directly measurable (PLAN §6 #4)."""

RAMP_PMT_CATHODE_MM = (3.0, 12.0)
"""R636-10 photocathode rectangle (short, long axis), datasheet TPMS1016E.

CONFIRMED for this apparatus (experimenter, 2026-07-23): the module visible
in the in-campaign photograph, a Thorlabs PXT1/M, HOUSES the R636-10. So the
3 x 12 mm rectangle stands and the install decision built on it is live. Note
the tube sits in a commercial housing, so orientation is set by rotating the
MODULE, not the bare tube -- check the housing's mounting before assuming
either orientation is equally convenient.
(The attribution was originally taken from Nieddu 2019, the NANOFIBRE
experiment, and happened to be right; it was flagged as unverified on
2026-07-23 and confirmed the same day.)

Which axis lies along the beam image is the install decision: L_par = 12 mm
('landscape') or 3 mm ('portrait'), a x4 lever on Z_c. The 2025 archive was
taken in LANDSCAPE (experimenter-confirmed 2026-07-23), which is also the
recommendation for a future session (PLAN §6 #4) -- portrait puts Z_c below the 0.90 mm flip
threshold at every plausible M and forfeits the sign-flip test, while its
one advantage (less axial averaging) is recovered by closing the slit."""

RAMP_RELAY_MAGNIFICATION_ENVELOPE = (1.9, 2.8)
"""M = f2/f1 for the proposed two-lens relay, f1 = 18 mm and f2 = 35-50 mm
(PLAN §6 #4). Sets Z_c = L_par/(2M) when the cathode is the limiting
aperture, or (slit half-width)/M when the image-plane slit is."""

# --------------------------------------------------------------------------
# Reproducibility
# --------------------------------------------------------------------------
RNG_SEED = 20260711
"""Single seed for every stochastic step (synthetic data, Monte Carlo error
propagation). Change only deliberately; closure tests pin coverage at this
seed and at least two others."""
