"""
Frequency-axis calibration from EOM ruler traces (module M2, core)
==================================================================

Each RF-on "ruler" trace holds up to seven two-photon comb teeth spaced
exactly 6.25 MHz apart on the laser axis (constants.TOOTH_SPACING_LASER_HZ,
RF-oscillator exact). Measuring the tooth spacing Δ in milliseconds
calibrates the sweep: rate = 6.25 MHz / Δ. This module implements the
staged per-trace protocol of docs/PLAN.md M2 (stages 1-2 and 6; the shape
ladder and free-center diagnostic extend it):

1. ROBUST INIT — never threshold peak-picking:
   * Δ from the autocorrelation of the baseline-subtracted smoothed trace,
     searched ONLY inside config.RULER_DELTA_RANGE_MS. Verified necessity:
     an unrestricted search lets comb periodicity lock onto multiples, and
     cold-block alignment locked 3/5 traces one tooth off (independent
     audit, 2026-07-11). Weak-carrier traces are handled for free — the
     autocorrelation uses all teeth at once.
   * comb phase t0 from a direct grid scan of the summed smoothed signal at
     the 7 predicted tooth positions. The scan folds t0 to the tooth nearest
     the WINDOW centre, which is proximity indexing and is exactly what the
     validity stage below exists to check.
2. CONSTRAINED SIMULTANEOUS FIT — one model for the whole trace: centers
   t0 + n*Δ (n = -3..+3), ONE shared Lorentzian tooth shape (all teeth are
   the same physical line excited via different photon pairs), free
   non-negative per-tooth heights, linear background. Simultaneous fitting
   is mandatory: at ~147 ms spacing and ~60 ms width, a strong tooth's wing
   under a weak neighbor is ~20% of the weak peak — single-tooth fits or
   maxima-reading pull centers by O(ms).
   Weights come from M1's noise law (rb5s6s.noise); parameter errors are
   inflated by sqrt(tau_int) for the measured wing-noise correlation and by
   sqrt(chi2_red) when the fit is imperfect (conservative).
2b. FIT VALIDITY (added 2026-08-04) — the rigid grid labels slots by
   proximity alone, so a retrace mirror can be fitted as a tooth. The
   top-three amplitude rule tests the labelling, a fixed-order ladder
   re-indexes what it can, and what it cannot is quarantined with a recorded
   reason. Pre-registered in docs/notes/ruler_validity_and_trim_prereg.md.
   This stage extends the plan rather than implementing one of its numbered
   stages.
3. BLOCK COMBINATION — inverse-variance mean of per-trace Δ with scatter
   inflation when the block chi2_red exceeds 1 (PDG-style conservative).

Everything here returns milliseconds; the conversion to MHz/ms happens at
the caller with the exact 6.25 MHz constant, so no frequency conventions
can leak in silently.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import numpy as np
from scipy.optimize import least_squares

from . import config as C
from .noise import signal_level, sigma_of_v
from .qc import boxcar
from .fitutil import cov_from_jac, feasible_p0


# ---------------------------------------------------------------------------
# stage 1 — robust initialization
# ---------------------------------------------------------------------------

def estimate_delta_acf(t_ms: np.ndarray, v: np.ndarray) -> Dict:
    """Tooth period from the autocorrelation, restricted to the physical
    search window. Returns {'delta_ms', 'score', 'fallback'}; on a weak
    autocorrelation (cold rulers) falls back to the campaign default and
    says so."""
    lev, _ = signal_level(v)
    x = boxcar(lev, 5)
    x = x - x.mean()
    n = len(x)
    acf = np.correlate(x, x, mode="full")[n - 1:]
    acf = acf / acf[0] if acf[0] > 0 else acf
    dt = t_ms[1] - t_ms[0]
    lo = int(C.RULER_DELTA_RANGE_MS[0] / dt)
    hi = min(int(C.RULER_DELTA_RANGE_MS[1] / dt), n - 1)
    seg = acf[lo:hi]
    if len(seg) == 0 or np.max(seg) < C.RULER_ACF_MIN_SCORE:
        return {"delta_ms": C.RULER_DELTA_FALLBACK_MS,
                "score": float(np.max(seg)) if len(seg) else 0.0, "fallback": True}
    return {"delta_ms": float((lo + int(np.argmax(seg))) * dt),
            "score": float(np.max(seg)), "fallback": False}


def estimate_t0(t_ms: np.ndarray, v: np.ndarray, delta_ms: float) -> float:
    """Comb phase by brute-force scan: t0 maximizing the summed smoothed
    signal at the predicted tooth positions (teeth outside the window
    simply do not contribute)."""
    lev, _ = signal_level(v)
    sm = boxcar(lev, C.QC_SMOOTH_W)
    best_t0, best_score = t_ms[0], -np.inf
    for t0 in np.arange(t_ms[0], t_ms[0] + delta_ms, 2.0):
        pos = t0 + delta_ms * np.array(TEETH)
        inside = (pos >= t_ms[0]) & (pos <= t_ms[-1])
        if not inside.any():
            continue
        score = float(np.sum(np.interp(pos[inside], t_ms, sm)))
        if score > best_score:
            best_score, best_t0 = score, float(t0)
    # fold t0 to the tooth nearest the window center for identifiability
    center = 0.5 * (t_ms[0] + t_ms[-1])
    k = round((center - best_t0) / delta_ms)
    return float(best_t0 + k * delta_ms)


# ---------------------------------------------------------------------------
# stage 2 — constrained simultaneous comb fit
# ---------------------------------------------------------------------------

N_TEETH = 7          # the comb runs to +/-3 orders. Fitting only +/-2 lets
TEETH = tuple(range(-(N_TEETH // 2), N_TEETH // 2 + 1))
"""Tooth orders fitted. RAISED 5 -> 7 on 2026-08-01 and it moves the rate.

The 6th and 7th teeth are present (EXPERIMENTER), and truncating at five
biases the SPACING: the unmodelled +/-3 tails pull the outermost fitted
teeth outward, so Delta comes out too small and the rate too high. Measured
on 24 ruler traces across the four peaks, refitting the same data both ways:

    Delta(5 teeth) = 146.804 ms  ->  rate 0.042574 MHz/ms  (= the committed
                                     0.04257061, i.e. this reproduces M2)
    Delta(7 teeth) = 146.970 ms  ->  rate 0.042526 MHz/ms

a +0.113% one-directional bias on every frequency the repository quotes.
It is ~1 sigma of the quoted rate error and small beside the w0 systematic,
but it is a bias rather than scatter, so it is fixed rather than absorbed.
The same truncation railed gamma_coll at zero in the M25 comb fits, which is
how it was found."""


def _comb(t_ms, t0, delta, w, heights, b0, b1):
    out = b0 + b1 * (t_ms - t_ms[0])
    for n, h in zip(TEETH, heights):
        x = 2.0 * (t_ms - (t0 + n * delta)) / w
        out = out + h / (1.0 + x * x)
    return out


# A height "rails" when the optimizer parks it on its lower bound of zero. The
# tolerance is numerical, not a physics threshold: trace levels are volts of
# order 1e-3 to 1e-1, so 1e-9 is indistinguishable from the bound and far below
# any real tooth. Railing is REPORTED (n_railed) and is never itself the test.
_RAIL_ATOL = 1e-9

# Upper bound applied to a pinned height. scipy requires lo < hi strictly, so a
# pinned tooth is capped just above zero rather than at it.
_PIN_CAP = 1e-12


def fit_comb(t_ms: np.ndarray, v: np.ndarray, law: Optional[Dict] = None, *,
             t0_seed: Optional[float] = None,
             mask: Optional[np.ndarray] = None,
             pin_zero: Sequence[int] = ()) -> Dict:
    """Weighted constrained comb fit of one ruler trace.

    Returns delta_ms, delta_err_ms (tau_int- and chi2-inflated), t0_ms,
    width_ms, heights (7), chi2_red, fit_rms, resid_norm, n_fitted, init
    metadata. Raises RuntimeError if the optimizer fails — callers must not
    silently skip rulers.

    The three keyword arguments are the levers the validity ladder pulls
    (docs/notes/ruler_validity_and_trim_prereg.md §3). All three default to the
    behaviour this function had before they existed, so a plain
    `fit_comb(t, v, law)` call is byte-identical to the 2026-08-01 fit.

    t0_seed
        Comb phase to seed and to centre the phase bounds on, bypassing
        `estimate_t0`. Seeding at t0 + j*Delta relabels every tooth by j slots,
        which is how a mis-indexed comb is re-indexed.
    mask
        Boolean sample selector. Only masked-in samples enter the residual, so
        a region known to hold a retrace mirror can be excluded from the fit
        rather than fitted as signal.
    pin_zero
        Tooth orders whose height is capped at zero. Excising a slot's samples
        is not enough on its own: the freed height would otherwise absorb the
        wings of its neighbours and re-create the pull it was excised for.
    """
    init = estimate_delta_acf(t_ms, v)
    d0 = init["delta_ms"]
    t00 = estimate_t0(t_ms, v, d0) if t0_seed is None else float(t0_seed)

    sel = np.ones(len(v), dtype=bool) if mask is None else np.asarray(mask, dtype=bool)
    if sel.shape != np.shape(v):
        raise ValueError("mask must have the same shape as the trace")
    n_fitted = int(sel.sum())

    lev, base = signal_level(v)
    if law is not None:
        sig = sigma_of_v(np.maximum(lev, 0.0), law)
        tau = max(law.get("tau_int", 1.0), 1.0)
    else:  # flat weights fallback (closure tests may run law-free)
        sig = np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6))
        tau = 1.0

    sm = boxcar(lev, C.QC_SMOOTH_W)
    h0 = np.clip(np.interp(t00 + d0 * np.array(TEETH), t_ms, sm), 1e-4, None)

    h_hi = np.full(N_TEETH, np.inf)
    for k in pin_zero:
        i = TEETH.index(int(k))
        h_hi[i] = _PIN_CAP
        h0[i] = 0.0

    p0 = np.concatenate([[t00, d0, C.RULER_TOOTH_WIDTH_INIT_MS], h0, [base, 0.0]])
    lo = np.concatenate([[t00 - d0 / 2, C.RULER_DELTA_RANGE_MS[0], 15.0],
                         np.zeros(N_TEETH), [-np.inf, -np.inf]])
    hi = np.concatenate([[t00 + d0 / 2, C.RULER_DELTA_RANGE_MS[1], 120.0],
                         h_hi, [np.inf, np.inf]])

    def model(p):
        return _comb(t_ms, p[0], p[1], p[2], p[3:3 + N_TEETH], p[-2], p[-1])

    def resid(p):
        return ((v - model(p)) / sig)[sel]

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=20000)
    if not sol.success:
        raise RuntimeError(f"comb fit failed: {sol.message}")

    dof = max(n_fitted - len(p0), 1)
    chi2_red = float(2.0 * sol.cost / dof)
    # covariance from the whitened Jacobian (SVD, robust to parameter scale);
    # conservative double inflation
    cov = cov_from_jac(sol.jac)
    infl = np.sqrt(max(chi2_red, 1.0)) * np.sqrt(tau)
    raw = (v - model(sol.x))[sel]
    return {
        "delta_ms": float(sol.x[1]),
        "delta_err_ms": float(np.sqrt(max(cov[1, 1], 0.0)) * infl),
        "t0_ms": float(sol.x[0]),
        "width_ms": float(sol.x[2]),
        "heights": sol.x[3:3 + N_TEETH].tolist(),
        "b0": float(sol.x[-2]), "b1": float(sol.x[-1]),
        "chi2_red": chi2_red,
        # fit_rms is in SIGNAL units (the tooth heights' own units), which is
        # what the top-three tie tolerance and the figure eligibility rule
        # compare heights against. resid_norm is the whitened counterpart.
        "fit_rms": float(np.sqrt(np.mean(raw ** 2))) if n_fitted else float("nan"),
        "resid_norm": float(np.sqrt(2.0 * sol.cost / max(n_fitted, 1))),
        "n_fitted": n_fitted,
        "init_fallback": init["fallback"],
        "acf_score": init["score"],
    }


# ---------------------------------------------------------------------------
# stage 2b — fit VALIDITY: the top-three rule and the re-index ladder
# ---------------------------------------------------------------------------
# Pre-registered in docs/notes/ruler_validity_and_trim_prereg.md, 2026-08-04.
#
# Tooth INDEXING had no protection at all. Slot k is assigned by proximity to
# the window centre, so when the triangular sweep's apex falls inside the
# acquisition window, the retrace mirror of a real tooth can occupy an outer
# slot and be fitted as if it were a tooth. The mirror of an inner tooth lands
# at a SMALLER radius than the slot it occupies, so the rigid grid contracts to
# reach it: delta comes out low and the rate 6.25/delta comes out high. That is
# the same sign as the five-to-seven truncation bias, and it is invisible to
# every existing check.
#
# The remedy reads AMPLITUDE, which proximity indexing never consults.

QUARANTINE_REASONS = (
    "top_three_unrecoverable",   # the full ladder ran, the rule still fails
    "no_excision_candidate",     # rule fails, no outer slot qualifies as a mirror
    "refit_failed",              # the optimizer failed inside the ladder
)
"""Closed vocabulary. Adding a token is a change to the pre-registration first."""

_PHASE_SHIFTS = (-2, -1, 1, 2)
_REQUIRED = (-1, 1)   # the two first-order sidebands

# Free parameters of the constrained comb fit: t0, delta, width, seven heights,
# two background terms. Used only to turn n_fitted into the degrees of freedom
# the acceptance ceiling below is scaled by.
_N_PARAMS = 3 + N_TEETH + 2

REINDEX_CHI2_NSIGMA = 1.0
"""Ladder acceptance ceiling, in standard deviations of the fit's own reduced
chi-squared. AMENDED 2026-08-04. The amendment is in
docs/notes/ruler_validity_and_trim_prereg.md and states what changed and why.

A reduced chi-squared on `dof` degrees of freedom has standard deviation
sqrt(2/dof), so a refit whose chi2_red rises by less than that is not
distinguishable from the first fit at the level of the fit's own noise. That is
the scale on which "did the relabelling worsen the fit" is answerable at all,
and 1.0 of it is the whole of it. On the campaign geometry, 2000 samples and
twelve parameters, sqrt(2/dof) is 0.032.

The original tolerance, C.RULER_REINDEX_CHI2_TOL = 1e-3 of chi2_red, is about
thirty times TIGHTER than that, so it rejected relabellings that no measurement
could call worse. It was calibrated on synthetics whose outer slots hold no
signal, where a one-slot relabel trades an empty slot for an empty slot and
costs nothing. Campaign combs populate all seven slots in a window that fits
6.8 of them, so a one-slot relabel always trades a populated slot, and it costs
something even when it is right.

Calibration of 1.0, on synthetics only. On 48 clean seven-tooth one-slot
mislabels the correct relabel costs at most 0.06 of a sqrt(2/dof), and on the
13 clean five-tooth closure combs at most 0.04. On the ladder's own fold
injector a relabel that satisfies the amplitude rule while keeping the
contracted spacing costs a median 2.4 and a maximum 8.1. One sigma sits a
factor of 16 above the clean cost and a factor of 2.4 below the fold cost. The
fold side is the tighter of the two, and the excision rung is the backstop
there: on the same injector excision improves chi2_red by 85 to 96 sigma.

The ceiling is applied with C.RULER_REINDEX_CHI2_TOL as a floor, so this can
only ever widen the acceptance and never narrow it."""


def top_three_verdict(heights: Sequence[float], fit_rms: float) -> Dict:
    """PASS iff the k = -1 and k = +1 heights both rank third or better.

    The first-order sidebands are the brightest teeth a phase-modulated comb
    produces at this drive depth and they are symmetric by construction, so a
    peak that displaces either of them from the top three has taken a place
    physics says belongs to a real tooth.

    It deliberately does NOT require k = 0 to be tallest: the carrier was
    suppressed on purpose (half-wave plate tilted), so a carrier below its own
    neighbours is expected physics, not a fault.

    One tolerance, C.RULER_TOP3_TIE_SIGMA: a required tooth ranking fourth but
    within that many fit_rms of the third-ranked height is a MARGINAL pass.

    Returns top3_ok, marginal, rank_m1, rank_p1, n_railed, verdict.
    """
    h = np.asarray(heights, dtype=float)
    if h.size != N_TEETH:
        raise ValueError(f"expected {N_TEETH} heights, got {h.size}")
    idx = {k: i for i, k in enumerate(TEETH)}
    order = np.argsort(-h, kind="stable")
    rank = np.empty(h.size, dtype=int)
    rank[order] = np.arange(1, h.size + 1)
    ranks = {k: int(rank[idx[k]]) for k in _REQUIRED}
    third = float(np.sort(h)[::-1][2])

    tol = C.RULER_TOP3_TIE_SIGMA * float(fit_rms)
    ok, marginal = True, False
    for k in _REQUIRED:
        if ranks[k] <= 3:
            continue
        if ranks[k] == 4 and (third - h[idx[k]]) <= tol:
            marginal = True
        else:
            ok = False
    if not ok:
        marginal = False

    verdict = "PASS" if (ok and not marginal) else ("MARGINAL" if ok else "FAIL")
    return {"top3_ok": bool(ok), "marginal": bool(marginal),
            "rank_m1": ranks[-1], "rank_p1": ranks[1],
            "n_railed": int(np.sum(h <= _RAIL_ATOL)),
            "verdict": verdict}


def suspect_outer_slot(heights: Sequence[float]) -> Optional[int]:
    """The outer slot most likely to hold a retrace mirror: among |k| >= 2, the
    tallest whose height exceeds the weaker of the two first-order teeth.
    Returns None when no outer slot outranks a real sideband, in which case
    there is nothing an excision could remove."""
    h = np.asarray(heights, dtype=float)
    idx = {k: i for i, k in enumerate(TEETH)}
    floor = min(h[idx[-1]], h[idx[1]])
    cands = [k for k in TEETH if abs(k) >= 2 and h[idx[k]] > floor]
    return max(cands, key=lambda k: h[idx[k]]) if cands else None


def validated_comb_fit(t_ms: np.ndarray, v: np.ndarray, law: Optional[Dict] = None,
                       *, allow_trim: bool = False,
                       gated: Optional[bool] = None) -> Dict:
    """One ruler trace through the fixed-order validity ladder.

        1. fit
        2. trim (core-guarded)
        3. verdict
        4. comb-phase shifts, j = -2, -1, +1, +2
        5. excision of the suspect outer slot
        6. quarantine, with a reason from QUARANTINE_REASONS

    A refit is accepted only if it PASSES the verdict AND does not worsen
    chi2_red past a ceiling of REINDEX_CHI2_NSIGMA standard deviations of the
    fit's own reduced chi-squared. Both are required: a re-index that rescues
    the verdict while worsening the fit has moved the labelling to a different
    wrong answer, which is this ladder's most likely way to fail. The ceiling
    now governs the excision rung as well as the phase rung, so the destructive
    rung is not the loosest one; see REINDEX_CHI2_NSIGMA.

    A quarantined trace keeps every fitted quantity so that its removal can be
    audited. The caller is responsible for excluding it from the calibration.

    GATING. `gated` defaults to C.RULER_TOP3_GATED, which is False. Ungated, the
    ladder still runs in full and every outcome is returned, but the fit OF
    RECORD is the first fit, `quarantined` is False, and nothing the verdict
    decided touches the calibration. The ladder's own answer is returned
    alongside as `quarantine_advised`, `reindex_action` and `delta_advised_ms`,
    so the size of the effect is on the record without being applied. Gated,
    the ladder's fit is the fit of record and a failing trace is quarantined.
    The reason the default is off is in the constant's own note.

    Returns the fit dict of record plus the verdict fields and: top3_gated,
    reindex_action (none / phase_shift / excision), reindex_j, excised_k,
    n_refits, delta_advised_ms, quarantine_advised, quarantined,
    quarantine_reason, trimmed, trim_start_ms, trim_end_ms, trim_reason.
    RuntimeError from the FIRST fit propagates unchanged, so a trace that
    cannot be fitted at all still reaches the caller as it always did; only
    failures inside the ladder become a quarantine.
    """
    if gated is None:
        gated = bool(C.RULER_TOP3_GATED)
    rec = {"reindex_action": "none", "reindex_j": 0, "excised_k": "",
           "n_refits": 0, "quarantine_advised": False, "quarantine_reason": "",
           "trimmed": False, "trim_start_ms": float("nan"),
           "trim_end_ms": float("nan"), "trim_reason": ""}

    fit = fit_comb(t_ms, v, law)                                   # 1

    # 2. trim. TODO(Phase 2, rb5s6s/trim.py): with the residual-tail trimmer in
    # place this step rebuilds `mask` from cusum_onset/tail_trim under a core
    # guard of one fitted FWHM either side of the fitted comb span, refits once
    # through fit_comb(mask=...), and records trimmed/trim_start_ms/
    # trim_end_ms/trim_reason. Until then the step is a no-op in both branches
    # and the ladder below is unaffected, so the ordering lands now and the
    # trimmer slots into exactly one place later.
    if allow_trim:
        rec["trim_reason"] = "trimmer not implemented (see Phase 2)"

    first, first_verdict = fit, top_three_verdict(fit["heights"], fit["fit_rms"])
    verdict = first_verdict                                        # 3

    if not verdict["top3_ok"]:
        # One ceiling, applied to BOTH refit rungs. Scaled by the standard
        # deviation of a reduced chi-squared on this fit's own degrees of
        # freedom, with the original relative tolerance kept as a floor so the
        # amendment can only widen. See REINDEX_CHI2_NSIGMA.
        dof = max(fit["n_fitted"] - _N_PARAMS, 1)
        ceiling = fit["chi2_red"] + max(
            C.RULER_REINDEX_CHI2_TOL * fit["chi2_red"],
            REINDEX_CHI2_NSIGMA * float(np.sqrt(2.0 / dof)))
        best, phase_failures = None, 0
        for j in _PHASE_SHIFTS:                                    # 4
            if rec["n_refits"] >= C.RULER_REINDEX_MAX_TRIALS:
                break
            rec["n_refits"] += 1
            try:
                g = fit_comb(t_ms, v, law,
                             t0_seed=fit["t0_ms"] + j * fit["delta_ms"])
            except RuntimeError:
                phase_failures += 1
                continue
            gv = top_three_verdict(g["heights"], g["fit_rms"])
            if gv["top3_ok"] and g["chi2_red"] <= ceiling:
                if best is None or g["chi2_red"] < best[0]["chi2_red"]:
                    best = (g, gv, j)
        if best is not None:
            fit, verdict, rec["reindex_action"], rec["reindex_j"] = (
                best[0], best[1], "phase_shift", best[2])
        else:
            k = suspect_outer_slot(fit["heights"])                 # 5
            refit_failed = False
            if k is not None and rec["n_refits"] < C.RULER_REINDEX_MAX_TRIALS:
                rec["n_refits"] += 1
                centre = fit["t0_ms"] + k * fit["delta_ms"]
                mask = np.abs(t_ms - centre) > 0.5 * fit["delta_ms"]
                try:
                    g = fit_comb(t_ms, v, law, t0_seed=fit["t0_ms"],
                                 mask=mask, pin_zero=(k,))
                except RuntimeError:
                    refit_failed = True
                else:
                    gv = top_three_verdict(g["heights"], g["fit_rms"])
                    # The excision rung is the DESTRUCTIVE one: it deletes
                    # samples and pins a slot to zero. It was the only rung with
                    # no chi-squared condition on it, so a rejected relabelling
                    # fell through to a rung that could delete a real tooth and
                    # worsen the fit without anything noticing. It is now held to
                    # the same ceiling as the phase rung. On a genuine fold this
                    # costs nothing, because removing a mirror the model cannot
                    # describe improves chi2_red by tens of sigma.
                    if gv["top3_ok"] and g["chi2_red"] <= ceiling:
                        fit, verdict = g, gv
                        rec["reindex_action"], rec["excised_k"] = "excision", k
            if not verdict["top3_ok"]:                             # 6
                if refit_failed or (k is None and phase_failures == len(_PHASE_SHIFTS)):
                    reason = "refit_failed"
                elif k is None:
                    reason = "no_excision_candidate"
                else:
                    reason = "top_three_unrecoverable"
                rec["quarantine_advised"], rec["quarantine_reason"] = True, reason

    rec["delta_advised_ms"] = fit["delta_ms"]
    if gated:
        rec["quarantined"] = rec["quarantine_advised"]
    else:
        # ADVISORY ONLY: the ladder ran and its answer is recorded, but the fit
        # of record is the first fit and no trace is excluded. Nothing the
        # verdict decided reaches a block, the campaign rate or the map.
        fit, verdict, rec["quarantined"] = first, first_verdict, False
    rec["top3_gated"] = bool(gated)

    out = dict(fit)
    out.update(verdict)
    out.update(rec)
    return out


# ---------------------------------------------------------------------------
# stage 4 — free-center diagnostic (feeds the sweep-nonlinearity map)
# ---------------------------------------------------------------------------

def _comb_free(t_ms, centers, w, heights, b0, b1):
    out = b0 + b1 * (t_ms - t_ms[0])
    for c, h in zip(centers, heights):
        x = 2.0 * (t_ms - c) / w
        out = out + h / (1.0 + x * x)
    return out


def fit_comb_free_centers(t_ms: np.ndarray, v: np.ndarray, base_fit: Dict,
                          law: Optional[Dict] = None) -> Dict:
    """Refit with each tooth's CENTER free (shape width still shared), seeded
    from the constrained fit. Only teeth whose seeded center lies inside the
    window AND whose fitted height in `base_fit` is a real signal (> a small
    fraction of the max height) are freed — outer teeth that fell off the
    window or into the noise are dropped, not fit to noise.

    Returns per-tooth centers with errors and their n-indices. The
    center-vs-(t0+nΔ) residuals are the local departures from a linear sweep
    — pooled across all ruler traces (whose combs sit at different window
    positions from drift + recentering) they stitch the ν(t) nonlinearity
    map (plan M2 stage 4 / the recenter-enabled ensemble stitch)."""
    t0, d, w = base_fit["t0_ms"], base_fit["delta_ms"], base_fit["width_ms"]
    heights = np.array(base_fit["heights"])
    hmax = heights.max() if heights.size else 0.0
    ns, seeds, h0 = [], [], []
    for i, n in enumerate(TEETH):
        c = t0 + n * d
        if t_ms[0] <= c <= t_ms[-1] and heights[i] > C.RULER_FREE_MIN_HEIGHT_FRAC * hmax:
            ns.append(n); seeds.append(c); h0.append(max(heights[i], 1e-4))
    if len(ns) < 2:
        return {"n": [], "centers_ms": [], "center_err_ms": [], "width_ms": w}

    lev, base = signal_level(v)
    if law is not None:
        sig = sigma_of_v(np.maximum(lev, 0.0), law)
        tau = max(law.get("tau_int", 1.0), 1.0)
    else:
        sig = np.full_like(v, max(np.std(np.diff(v)) / np.sqrt(2.0), 1e-6)); tau = 1.0

    nt = len(ns)
    p0 = np.concatenate([seeds, [w], h0, [base_fit["b0"], base_fit["b1"]]])
    lo = np.concatenate([np.array(seeds) - d / 2, [15.0], np.zeros(nt), [-np.inf, -np.inf]])
    hi = np.concatenate([np.array(seeds) + d / 2, [120.0], np.full(nt, np.inf), [np.inf, np.inf]])

    def resid(p):
        return (v - _comb_free(t_ms, p[:nt], p[nt], p[nt + 1:2 * nt + 1],
                               p[2 * nt + 1], p[2 * nt + 2])) / sig

    p0 = feasible_p0(p0, lo, hi)  # project seed into bounds
    sol = least_squares(resid, p0, bounds=(lo, hi), max_nfev=20000)
    if not sol.success:
        raise RuntimeError(f"free-center fit failed: {sol.message}")
    dof = max(len(v) - len(p0), 1)
    chi2_red = float(2.0 * sol.cost / dof)
    cov = cov_from_jac(sol.jac)
    infl = np.sqrt(max(chi2_red, 1.0)) * np.sqrt(tau)
    return {
        "n": ns,
        "centers_ms": sol.x[:nt].tolist(),
        "center_err_ms": [float(np.sqrt(max(cov[i, i], 0.0)) * infl) for i in range(nt)],
        "width_ms": float(sol.x[nt]),
        "chi2_red": chi2_red,
    }


# ---------------------------------------------------------------------------
# stage 6 — block combination
# ---------------------------------------------------------------------------

def combine_block(fits: List[Dict]) -> Dict:
    """Inverse-variance mean of per-trace delta with PDG-style scatter
    inflation: if the block chi2_red > 1, the combined error is scaled by
    sqrt(chi2_red) so genuine trace-to-trace inconsistency widens the error
    instead of being averaged away."""
    d = np.array([f["delta_ms"] for f in fits])
    e = np.array([f["delta_err_ms"] for f in fits])
    w = 1.0 / np.maximum(e, 1e-9) ** 2
    mean = float(np.sum(w * d) / np.sum(w))
    err = float(1.0 / np.sqrt(np.sum(w)))
    chi2_red = float(np.sum(w * (d - mean) ** 2) / max(len(d) - 1, 1))
    if chi2_red > 1.0:
        err *= np.sqrt(chi2_red)
    return {"delta_ms": mean, "delta_err_ms": err,
            "block_chi2_red": chi2_red, "n": len(fits)}
