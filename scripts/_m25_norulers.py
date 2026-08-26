#!/usr/bin/env python3
"""
M25: the global dataset fit -- every canonical trace, one likelihood.

WHY THIS EXISTS. M23 fits the POWER lever (S0 = kappa*P) across three
sessions and takes each peak's collisional width from a Gaussian prior built
on results/beta_self.csv. That prior was itself fitted under a transit prior,
so the AC-Stark bound inherits an assumption from the collisional fit, which
inherited one from the waist. M4e/M4b/M4d have the mirror problem: they fit
beta_self while holding the Stark term at a fixed prediction. The two
coefficients are estimated separately even though they are constrained by
overlapping data and are correlated through the SAME nuisance -- the width
budget shared between transit, laser and collisions.

This module removes that split. One likelihood, every canonical trace, both
coefficients free:

    gamma_coll(T) = beta_self * N(T)         the collisional term
    S0(P)         = kappa * P                the AC-Stark term
    transit(T)    = transit(T_ref) * sqrt(T/T_ref)   fixed form, rides on w0
    sigma_laser   free per (session, temperature block)

WHAT THE DATASET ACTUALLY OFFERS, and why the two levers separate. The
campaign ran a POWER ladder at fixed 130 C (5 powers, 4 peaks) and a
TEMPERATURE ladder at fixed 225 mW (70/90/110 C, 4 peaks). Those are
orthogonal in exactly the right way:

  * along the T ladder the power is CONSTANT, so the Stark contribution is
    constant too, and every width change is collisional (x53 in density)
    plus transit (sqrt(T), a fixed form). That ladder measures the CORE.
  * along the P ladder the temperature is constant, so the collisional and
    transit terms are constant, and the width change is Stark alone.

Fitting them jointly is therefore not merely "more data": it is the only
construction in which the core-width nuisance that limits the Stark bound is
itself measured rather than assumed, and in which the covariance between
beta_self and kappa is propagated instead of ignored.

THE RULER COMBS, and a measurement mistake worth recording. The 61
canonical ruler_t traces carry the EOM comb: up to seven replicas of the
same physical line at 12.5 MHz transition-axis spacing, which is free
lineshape statistics at exactly the three cooling temperatures where the
density lever wants them. Their tooth SPACINGS calibrated the frequency axis (M2);
their tooth SHAPES had never fed a width fit until now.

Two facts about the comb, both RECOLLECTION and both
confirmed against the traces. The carrier is DELIBERATELY SUPPRESSED (the half-wave
plate was tilted), and the comb is uniform. Measured on 993.4121/4192/4207
at 110 C over the five INNER slots, k = -2..+2, which is all the 2026-07-11
reading resolved: 12.49 +/- 1.10, 12.25 +/- 0.29 and 12.37 +/- 0.58 MHz
spacing, with relative amplitudes [0.24, 1.00, 0.69, 0.93, 0.21] -- the
centre tooth sitting BELOW both of its neighbours, which is the suppression,
with symmetric +/-1 and +/-2 sidebands either side of it. The comb runs to
+/-3, and the fit was widened to all seven slots on 2026-08-01 when the
truncation was found to bias the spacing (rb5s6s/ruler.py, TEETH).

An intermediate version of this module disabled the rulers on the strength
of a comb map that showed extra teeth at ~4 MHz offsets, read as a
triangular-sweep retrace folding a mirrored comb into the window. That was
wrong: the peak finder used a 3% threshold on unsmoothed data and was
picking up noise between the real teeth. At a 20% threshold the comb is
clean and uniform (RECOLLECTION). The lesson is in the record
because the wrong reading was one step from being shipped.

HOW MANY TEETH, and why it matters more than it sounds. The comb runs to
+/-3 orders: the 6th and 7th teeth are present (RECOLLECTION), and
truncating the model at five RAILS gamma_coll AT ZERO. Fitting the same
110 C ruler blocks both ways:

    peak    5 teeth (win +/-38)      7 teeth (win +/-44)
    4121    gamma_coll 0.000         gamma_coll 0.398
    4192    gamma_coll 0.000         gamma_coll 0.575
    4207    gamma_coll 0.000         gamma_coll 0.722

with chi2_red flat or better (4192: 0.256 -> 0.199). The mechanism is
plain: teeth at +/-37.5 MHz sit right at a +/-38 MHz window edge, so their
unmodelled tails leak in and the only way the model can absorb them is to
narrow its core. A railed parameter carries no information and biases
everything sharing its budget, which is why this was worth chasing rather
than accepting.

The fit therefore uses SEVEN free tooth amplitudes per trace -- free rather
than Bessel-locked, so the carrier suppression and the known AM
contamination both live in the amplitudes and stay out of the widths -- and
one shared lineshape. ruler_p stays out: its power setting was never
recorded.

THE RULERS ARE NOT ALLOWED TO SET beta_self SILENTLY. Even unrailed, the
RF-on blocks prefer a collisional width (0.4-0.7 MHz at 110 C) well above
what the RF-off campaign implies there (~0.17 MHz at the fitted beta), so
modulated and unmodulated excitation do not agree about the core. Whatever
the cause -- EOM phase noise, a different saturation regime, velocity-class
selection -- it is unexplained, so this module reports the fit WITH and
WITHOUT the rulers and treats the gap as a stated systematic rather than
averaging it away. The rulers earn their place for the Stark channel, where
they add lineshape statistics at fixed power and temperature.

THE 59 t_sweep TRACES ARE NEW TO THE STARK ANALYSIS. They have always been in
the collisional fits (M4, M4b, M4d) and in M24's wing check, but no
Stark-channel module had ever read them, because a single-power ladder cannot
constrain a power law on its own. In a joint fit it does not need to: it
anchors the core the power ladder is trying to see past.

SESSIONS. Campaign p_sweep (100) + campaign t_sweep (59) + the 2025-07-04
LeCroy evening session (46) + the 2025-07-18 campaign-morning session (26) =
231 traces. The evening session keeps its per-peak fitted rate and the
campaign-morning session its bounded rate scale, exactly as M23 established;
neither contributes centres.

WHAT THIS MODULE DOES NOT CLAIM. It is still bounded by the same open beam
waist: transit rides on w0, so beta_self and kappa remain w0-conditional and
PRELIMINARY. What changes is that they are now conditional on ONE assumption
instead of a chain of three.

ARM B of the two-arm M25 design: this copy runs with USE_RULERS = False, so
the ruler combs contribute no lineshape information and beta_self is set by
the RF-off traces alone. The gap between this arm and the rulers-on arm in
run_global_dataset_fit.py is reported as a stated systematic rather than
resolved, because the two disagree on the collisional core and the dataset
cannot say which is right.

SIGMA GRANULARITY UPGRADE (2026-08-02), the measured-prior re-run's second
change, applied identically to both M25 arms. Until now sigma_laser was
pooled per SL_BLOCKS entry only (one value per campaign temperature, plus
one each for the evening-session and campaign-morning sessions, 6 total),
which POOLS ALL
FOUR PEAKS inside every block. Free-Gaussian-sigma probes on the single
# term-of-art: the docstring cites a private reviews directory path
brightest trace per peak at 225 mW/130 C (private/reviews/digest/
fig16_residual_asymmetry.md, "Seventh addition") found that pooling too
coarse there: peak-level deviations of -287 kHz (4192, dchi2 21.5, 4.6
sigma) and -121 kHz (4154, dchi2 9.1, 3.0 sigma), with 4121 and 4207
consistent with zero (-85 +/- 256, +97 +/- 199 kHz). The digest's own
recommendation (same section, "Recommendation") is to resolve sigma_laser
per (session-block, peak) -- matching the granularity M23 already uses --
but with a HIERARCHICAL SHRINKAGE PRIOR rather than a flat parameter-count
expansion, because a flat per-(peak, temperature) grid is not affordable at
the campaign's low-temperature blocks (single-trace sigma errors already
reach 0.5-2.3 MHz at 70/90 C, per the same digest section).

Implementation: the SL_BLOCKS parameters (indices I_SL..I_SL+5) are KEPT
UNCHANGED as session/block-level population means sigma_s. A new block of
sigma_sp parameters is appended at index NS, one per (SL_BLOCKS entry, peak)
combination actually realized in the loaded traces -- 21 in the full
dataset (4 campaign temperatures x 4 peaks = 16, evening session 4 peaks,
campaign-morning 1 peak, since the campaign-morning session only ever
touches 4192). Each trace's lineshape
uses its own sigma_sp directly (not the pooled sigma_s); a soft Gaussian
prior residual (sigma_sp - sigma_s) / SIGMA_SP_PRIOR_MHZ is added for every
sp parameter, tying it back to its block's mean. The prior width, 150 kHz,
is the mean absolute pull from the four probe numbers above:
mean(|-85|, |-121|, |-287|, |97|) = 147.5 kHz, rounded. This is not a hard
constraint: at camp130 (the only block with a resolved peak-level pull) the
data can pay the ~4-9 dchi2 cost of a 150 kHz-scale deviation and win far
more in likelihood, exactly as the free-sigma probe found; at camp70/camp90
(errors of 0.5-2.3 MHz per trace) the prior chi2 cost of any comparable
deviation swamps the handful of noisy points that would otherwise drive it,
so those cells are shrunk back toward the pooled mean automatically. This is
partial pooling, not a flat 6 -> 27 parameter-count increase: the EFFECTIVE
number of free sigmas is set by how much SNR each cell actually has, which
is the property the digest asked for and a hard per-(peak,T) split cannot
provide. Two alternative parents of the same residual excess were tested
elsewhere in the same digest and excluded, so neither is implemented here:
a transit-tail term (MC-vs-analytic-kernel test, wrong sign and 2-3 orders
of magnitude too small) and a periodic term (tested for a different module,
M22, and found unsupported). New CSV rows carry quantity "sigma_laser_sp",
key f"{block}_{peak}" (e.g. "camp130_4192"); the existing "sigma_laser" rows
are unchanged and still report the pooled sigma_s means.

Writes results/global_dataset_fit_norulers.csv, NOT the rulers-on arm's
global_dataset_fit.csv. Needs the excluded 2025-07-04 and
campaign-morning trees; without them it prints what is missing and exits 0.
Runtime: long (many hours). Run it in the background.
"""

from __future__ import annotations

import csv
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.sparse import lil_matrix, vstack

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

from rb5s6s import config as C  # noqa: E402
from rb5s6s.density import number_density_cm3  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.linefit import (_shared_profile_grid, adaptive_halfwidth,  # noqa: E402
                            to_frequency, transit_fwhm_at_T)
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402
from rb5s6s.noise import condition_noise_model, sigma_of_v, signal_level  # noqa: E402
from run_beta_self import load_t_rates  # noqa: E402
from run_stark_joint import PEAKS, SESSION_20250717, SESSION_20250704, load_session_20250717, load_session_20250704  # noqa: E402

PK_IX = {p: i for i, p in enumerate(PEAKS)}
DNU_FLOOR = 2e-2
KAPPA_PRED = stark_shift_S0_mhz(1.0, C.W0_MEASURED_M, rho=C.RHO_RETRO)
KAPPAS = tuple(sorted({0.0, 0.25, 0.5, 0.75, 1.0, round(KAPPA_PRED, 3),
                       2.0, 2.62, 3.5, 5.0}))

# sigma_laser blocks: campaign gets one per temperature (the M4b hierarchical
# choice, whose per-T sharing across peaks M4c found untested but not
# contradicted); the two other sessions get one each. These remain the
# session/block-level POPULATION MEANS sigma_s; see SIGMA GRANULARITY UPGRADE
# in the module docstring for the per-(block, peak) sigma_sp layer appended
# at index NS.
SL_BLOCKS = ["camp70", "camp90", "camp110", "camp130", "reh", "pil"]
SL_IX = {b: i for i, b in enumerate(SL_BLOCKS)}
NS = 2 + len(SL_BLOCKS) + 2 + len(PEAKS) + 1   # kappa,beta + sl + Vsat*2 + rates + campaign-morning
I_KAPPA, I_BETA = 0, 1
I_SL = 2
I_VSAT_AG = I_SL + len(SL_BLOCKS)          # Agilent (campaign + campaign-morning)
I_VSAT_LC = I_VSAT_AG + 1                  # LeCroy (evening session)
I_REHRATE = I_VSAT_LC + 1
I_PILSCALE = I_REHRATE + len(PEAKS)

N_UNIT = 1e12

SIGMA_SP_PRIOR_MHZ = 0.15
"""Hierarchical shrinkage prior width for the per-(session-block, peak)
sigma_sp deviations from their block's sigma_s mean (see the module
docstring, SIGMA GRANULARITY UPGRADE). Set to the mean absolute pull
observed in the free-Gaussian-sigma probe (fig16_residual_asymmetry.md,
Seventh addition): mean(|-85|, |-121|, |-287|, |+97|) kHz = 147.5 kHz,
rounded to 150 kHz -- the scale a real per-peak effect is expected to sit
at, not a value tuned to this fit's own outcome."""


def sp_keys_for(traces):
    """Realized (sigma_laser block, peak) pairs, sorted for a deterministic
    parameter ordering shared by build(), make_resid() and sparsity() (all
    three recompute this from the same `traces` list rather than threading
    an extra argument through every call site, including profile2d and
    w0_scan)."""
    return sorted({(t["sl"], t["peak"]) for t in traces})


def load_campaign_all():
    """Campaign p_sweep AND t_sweep, each tagged with its temperature."""
    rows = load_manifest()
    _, prates = load_t_rates()
    out = []
    groups = defaultdict(list)
    for r in rows:
        if r["flag"] != "canonical" or r["rf_on"] == "True":
            continue
        if r["role"] == "p_sweep":
            groups[(r["peak"], 130.0, int(r["power_mW"]) / 1e3)].append(r)
        elif r["role"] == "t_sweep":
            groups[(r["peak"], float(r["temperature_C"]), 0.225)].append(r)
    for (pk, T, P), recs in sorted(groups.items()):
        if len(recs) < 3:
            continue
        rate, _ = prates[pk]
        volts = [load_trace(trace_path(r))[1] for r in recs]
        law = condition_noise_model(volts)
        tau = max(law.get("tau_int", 1.0), 1.0)
        for r in recs:
            t, v = load_trace(trace_path(r))
            nu = to_frequency(t, rate)
            lev, base = signal_level(v)
            c0 = float(nu[int(np.argmax(lev))])
            sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
            m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
            out.append(dict(sess="camp", peak=pk, T=T, P=P, x=nu[m], v=v[m],
                            sg=sg[m], c0=c0, A0=float(lev.max()), b0=float(base),
                            sl=f"camp{int(T)}"))
    return out


USE_RULERS = False        # 5 uniform teeth, carrier suppressed: see docstring
TOOTH_MHZ = 12.5          # transition-axis comb spacing (constants: OMEGA)
N_TEETH = 7               # carrier +/-1 +/-2 +/-3: the 6th and 7th
                          # teeth are present and truncating them
                          # RAILS gamma_coll at zero (see docstring)
TEETH = tuple(range(-(N_TEETH // 2), N_TEETH // 2 + 1))
RULER_HALFWIN_MHZ = 44.0  # 3*12.5 + ~1.3 linewidths of margin


def load_rulers_t():
    """The 61 canonical ruler_t traces as five-tooth COMBS. Their tooth
    spacings calibrated the frequency axis (M2); their tooth SHAPES -- five
    replicas of the same physical line per trace, at exactly known
    +/-12.5 MHz transition-axis offsets -- have never fed a width fit.
    Each trace contributes one shared lineshape and five free tooth
    amplitudes (free, NOT Bessel-locked: the known AM contamination lives
    in the amplitudes and stays out of the widths). Power is taken as the
    dwell's 225 mW; it is not recorded in the manifest, and the Stark term
    at the bound is < 5% of the linewidth, so a wrong assumption cannot
    move the core widths these traces are here to pin. ruler_p (44 traces)
    stays OUT: its power is unrecorded and it brackets a ladder whose
    setting changed underneath it."""
    rows = load_manifest()
    _, prates = load_t_rates()
    out = []
    groups = defaultdict(list)
    for r in rows:
        if r["flag"] == "canonical" and r["role"] == "ruler_t":
            groups[(r["peak"], float(r["temperature_C"]))].append(r)
    for (pk, T), recs in sorted(groups.items()):
        rate, _ = prates[pk]
        volts = [load_trace(trace_path(r))[1] for r in recs]
        law = condition_noise_model(volts)
        tau = max(law.get("tau_int", 1.0), 1.0)
        for r in recs:
            t, v = load_trace(trace_path(r))
            nu = to_frequency(t, rate)
            lev, base = signal_level(v)
            c0 = float(nu[int(np.argmax(lev))])
            sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
            m = np.abs(nu - c0) <= RULER_HALFWIN_MHZ
            out.append(dict(sess="ruler", peak=pk, T=T, P=0.225, x=nu[m],
                            v=v[m], sg=sg[m], c0=c0, A0=float(lev.max()),
                            b0=float(base), sl=f"camp{int(T)}"))
    return out




def measured_pilot_scale():
    """The M26 measured pilot_rate_scale, if the committed CSV carries it.

    Returns (mean, err) or None. When present, the campaign-morning axis
    scale becomes a tight box around the MEASURED value instead of the
    [0.9, 1.1] assumption box: the campaign-morning session's own 27 rulers
    beat a fitted nuisance. The 2026-08-02
    fits put the fitted scale at 1.023-1.029 while the rulers measure
    1.0022(12); imposing the measurement is the experiment that decides
    whether that gap was the axis or absorbed width physics."""
    import csv as _csv
    path = C.RESULTS_DIR.parent / "results" / "morning_ruler.csv"
    if not path.exists():
        return None
    for r in _csv.DictReader(open(path)):
        if r["quantity"] == "pilot_rate_scale_measured":
            return float(r["value"]), float(r["err"])
    return None


def build(traces):
    sp_keys = sp_keys_for(traces)
    n_sp = len(sp_keys)
    p0 = np.zeros(NS + n_sp + (N_TEETH + 3) * len(traces))
    lo = np.full_like(p0, -np.inf)
    hi = np.full_like(p0, np.inf)
    p0[I_KAPPA] = 0.0; lo[I_KAPPA] = 0.0; hi[I_KAPPA] = 60.0
    p0[I_BETA] = 0.03; lo[I_BETA] = 0.0; hi[I_BETA] = 5.0
    for b in SL_BLOCKS:
        i = I_SL + SL_IX[b]
        p0[i] = 1.2; lo[i] = 0.05; hi[i] = 50.0
    for i in (I_VSAT_AG, I_VSAT_LC):
        p0[i] = 5.0; lo[i] = -1.0; hi[i] = 6.0
    r0 = np.log(5.9 / 470.0)
    for k in range(len(PEAKS)):
        i = I_REHRATE + k
        p0[i] = r0; lo[i] = r0 - np.log(4); hi[i] = r0 + np.log(4)
    p0[I_PILSCALE] = 0.0
    _mps = measured_pilot_scale()
    if _mps is not None:
        _m, _e = _mps
        p0[I_PILSCALE] = np.log(_m)
        lo[I_PILSCALE] = np.log(_m - 5 * _e); hi[I_PILSCALE] = np.log(_m + 5 * _e)
    else:
        lo[I_PILSCALE] = np.log(0.9); hi[I_PILSCALE] = np.log(1.1)
    # per-(session-block, peak) sigma_sp: seeded at the same value as the
    # pooled sigma_s blocks, tied to them by the shrinkage prior in resid().
    for i, (blk, pk) in enumerate(sp_keys):
        idx = NS + i
        p0[idx] = 1.2; lo[idx] = 0.05; hi[idx] = 50.0
    j = NS + n_sp
    offsets = []
    for t in traces:
        offsets.append(j)
        if t["sess"] == "ruler":
            # 5 tooth amplitudes, then centre, b0, b1
            # measured pattern at 110 C: [-2,-1,0,+1,+2] ~ .22/.97/.69/.93/.21
            # of the strongest tooth, i.e. the CARRIER (slot 0) suppressed
            # below its own neighbours. Seed that shape; the amplitudes are
            # free, so the fit refines it per trace.
            p0[j:j + N_TEETH] = 0.5 * t["A0"]
            lo[j:j + N_TEETH] = 0.0
            p0[j + N_TEETH] = t["c0"]
            lo[j + N_TEETH] = t["c0"] - 8.0
            hi[j + N_TEETH] = t["c0"] + 8.0
            p0[j + N_TEETH + 1] = t["b0"]; p0[j + N_TEETH + 2] = 0.0
            j += N_TEETH + 3
        else:
            p0[j:j + 4] = [t["A0"], t["c0"], t["b0"], 0.0]
            lo[j] = 0.0
            span = 8.0 if t["sess"] != "reh" else 1200.0
            lo[j + 1] = t["c0"] - span; hi[j + 1] = t["c0"] + span
            j += 4
    return p0[:j], lo[:j], hi[:j], offsets


def make_resid(traces, offsets, direction=-1, transit_ref=None):
    dens = {T: float(number_density_cm3(np.array([T]))[0]) / N_UNIT
            for T in sorted({t["T"] for t in traces})}
    sp_keys = sp_keys_for(traces)
    sp_ix = {k: i for i, k in enumerate(sp_keys)}

    def resid(p, kappa=None):
        kap = p[I_KAPPA] if kappa is None else kappa
        beta = p[I_BETA]
        cache = {}
        out = []
        for i, t in enumerate(traces):
            T = t["T"]
            gc = beta * dens[T]                       # the collisional model
            sl = p[NS + sp_ix[(t["sl"], t["peak"])]]
            transit = transit_fwhm_at_T(
                T, C.TRANSIT_FWHM_PLACEHOLDER_MHZ
                if transit_ref is None else transit_ref)
            s0 = kap * t["P"]
            key = (t["sess"] == "reh", round(gc, 7), round(sl, 7),
                   round(transit, 7), round(s0, 8))
            if key not in cache:
                g, prof = _shared_profile_grid(gc, sl, transit, s0, "gaussian",
                                               dnu_floor=DNU_FLOOR)
                if t["sess"] == "reh" and direction < 0:
                    prof = prof[::-1]
                cache[key] = (g, prof)
            g, prof = cache[key]
            j = offsets[i]
            if t["sess"] == "ruler":
                amps = p[j:j + N_TEETH]
                cc = p[j + N_TEETH]
                b0, b1 = p[j + N_TEETH + 1], p[j + N_TEETH + 2]
                lin = np.zeros_like(t["x"])
                for kk, ak in zip(TEETH, amps):
                    lin = lin + ak * np.interp(t["x"] - cc - kk * TOOTH_MHZ,
                                               g, prof, left=0., right=0.)
                Vs = np.exp(p[I_VSAT_AG])
                mdl = Vs * (1.0 - np.exp(-lin / Vs)) + b0 + b1 * t["x"]
                out.append((t["v"] - mdl) / t["sg"])
                continue
            A, cc, b0, b1 = p[j: j + 4]
            if t["sess"] == "reh":
                rate = np.exp(p[I_REHRATE + PK_IX[t["peak"]]])
                lin = A * np.interp(rate * (t["x"] - cc), g, prof, left=0., right=0.)
                Vs = np.exp(p[I_VSAT_LC])
            elif t["sess"] == "pil":
                lin = A * np.interp(np.exp(p[I_PILSCALE]) * t["x"] - cc, g, prof,
                                    left=0., right=0.)
                Vs = np.exp(p[I_VSAT_AG])
            else:
                lin = A * np.interp(t["x"] - cc, g, prof, left=0., right=0.)
                Vs = np.exp(p[I_VSAT_AG])
            mdl = Vs * (1.0 - np.exp(-lin / Vs)) + b0 + b1 * t["x"]
            out.append((t["v"] - mdl) / t["sg"])
        # hierarchical shrinkage: each sigma_sp is pulled toward its block's
        # sigma_s mean by a Gaussian prior of width SIGMA_SP_PRIOR_MHZ (see
        # SIGMA GRANULARITY UPGRADE in the module docstring).
        out.append(np.array([
            (p[NS + i] - p[I_SL + SL_IX[blk]]) / SIGMA_SP_PRIOR_MHZ
            for (blk, pk), i in sp_ix.items()
        ]))
        return np.concatenate(out)
    return resid


def sparsity(traces, offsets, nparams):
    sp_keys = sp_keys_for(traces)
    sp_ix = {k: i for i, k in enumerate(sp_keys)}
    n_rows = sum(len(t["x"]) for t in traces)
    S = lil_matrix((n_rows, nparams), dtype=int)
    r0 = 0
    for i, t in enumerate(traces):
        n = len(t["x"])
        S[r0:r0 + n, I_KAPPA] = 1
        S[r0:r0 + n, I_BETA] = 1
        S[r0:r0 + n, NS + sp_ix[(t["sl"], t["peak"])]] = 1
        if t["sess"] == "reh":
            S[r0:r0 + n, I_VSAT_LC] = 1
            S[r0:r0 + n, I_REHRATE + PK_IX[t["peak"]]] = 1
        else:
            S[r0:r0 + n, I_VSAT_AG] = 1
            if t["sess"] == "pil":
                S[r0:r0 + n, I_PILSCALE] = 1
        width = N_TEETH + 3 if t["sess"] == "ruler" else 4
        S[r0:r0 + n, offsets[i]:offsets[i] + width] = 1
        r0 += n
    pri = lil_matrix((len(sp_keys), nparams), dtype=int)
    for (blk, pk), i in sp_ix.items():
        pri[i, I_SL + SL_IX[blk]] = 1
        pri[i, NS + i] = 1
    return vstack([S.tocsr(), pri.tocsr()]).tocsr()


def chain(resid, Sf, lo, hi, q0, kappas, tag, nfev=2500):
    res, q = {}, q0.copy()
    for kap in kappas:
        t0 = time.time()
        fn = lambda z: resid(np.concatenate([[0.0], z]), kappa=kap)  # noqa: E731
        s = least_squares(fn, q, bounds=(lo[1:], hi[1:]), jac_sparsity=Sf,
                          max_nfev=nfev, x_scale="jac", ftol=1e-12, xtol=1e-12)
        q = s.x.copy()
        r = fn(q)
        res[kap] = (float(np.sum(r * r)), q.copy())
        print(f"    [{tag}] kappa={kap:5.2f} chi2={np.sum(r*r):12.2f} "
              f"beta={q[I_BETA - 1]:.4f} {time.time()-t0:4.0f}s nfev={s.nfev}",
              flush=True)
    return res


def _crossings(x, c, thresh):
    """Both edges of a profile interval, INTERPOLATED to the threshold crossing.

    WHY THIS EXISTS (2026-08-10). This file is ARM B of the two-arm M25 design,
    a deliberate second copy of run_global_dataset_fit.py rather than a shared
    import, so a fix to the primary copy does not reach it automatically. The
    primary copy's beta interval used to be reported as the set of GRID POINTS
    under the threshold, min(bl) to max(bl) on a grid of step 0.01, and where
    exactly one grid point qualified both edges landed on it: a committed
    95 per cent interval of ZERO WIDTH, narrower than the grid that produced it.
    This copy carries the identical construction and the identical defect, and
    is fixed the same way: interpolate both edges to the threshold crossing, the
    way ub95() two functions below already does for kappa.

    AND THE SAME SECOND CORRECTION (addendum 30). Linear interpolation of chi2
    is wrong in a known direction, because a profile is quadratic about its
    minimum and a straight line reaches the threshold far too early. On the
    primary arm that understated the interval by a factor of 14. Interpolate in
    sqrt(chi2 - chi2_min), which is the locally linear variable, exactly as the
    primary copy now does. The duplication is the point of the two-arm design
    and also its cost: this is the second time one defect has needed two fixes.
    """
    x = np.asarray(x, float)
    c = np.asarray(c, float) - float(np.min(c))
    i = int(np.argmin(c))
    root = np.sqrt(np.maximum(c, 0.0))
    root_t = float(np.sqrt(thresh))

    def edge(idxs, fallback):
        prev = i
        for j in idxs:
            if c[j] > thresh:
                return float(np.interp(root_t, [root[prev], root[j]],
                                       [x[prev], x[j]]))
            prev = j
        return float(fallback)

    lo = edge(range(i - 1, -1, -1), x[0])
    hi = edge(range(i + 1, len(x)), x[-1])
    return lo, hi


def ub95(k, c):
    c = np.asarray(c) - np.min(c)
    k = np.asarray(k)
    i = int(np.argmin(c))
    above = np.where((k > k[i]) & (c > 2.706))[0]
    if not len(above):
        return float("nan")
    j = above[0]
    return float(np.interp(2.706, [c[j - 1], c[j]], [k[j - 1], k[j]]))


def profile2d(resid, Sf, lo, hi, q0, kappas, betas, tag="2D"):
    """chi2 on a (kappa, beta) grid, warm-started along each row. Gives the
    JOINT confidence region instead of a bound on one coefficient with the
    other profiled away silently."""
    out = {}
    for kap in kappas:
        q = q0.copy()
        for b in betas:
            def fn(z, _k=kap, _b=b):
                z = z.copy()
                z[I_BETA - 1] = _b
                return resid(np.concatenate([[0.0], z]), kappa=_k)
            # beta is overwritten inside fn, so its slot is INERT: leave its
            # bounds alone (pinning lo==hi is a scipy ValueError, the v2 crash)
            s = least_squares(fn, q, bounds=(lo[1:], hi[1:]), jac_sparsity=Sf,
                              max_nfev=800, x_scale="jac", ftol=1e-11, xtol=1e-11)
            q = s.x.copy()
            r = fn(q)
            out[(kap, b)] = float(np.sum(r * r))
        print(f"    [{tag}] kappa={kap:5.2f} done", flush=True)
    return out


def w0_scan(traces, offsets, w0s, kappas):
    """kappa and beta as functions of the ASSUMED waist. The dataset cannot
    pin w0 (transit and sigma_laser are degenerate), so the statement of
    record is not one bound but the bound's dependence on the assumption."""
    rows = []
    for w0 in w0s:
        tr_ref = C.transit_fwhm_from_w0(w0, 110.0)
        resid = make_resid(traces, offsets, transit_ref=tr_ref)
        p0, lo, hi, _ = build(traces)
        Sf = sparsity(traces, offsets, len(p0))[:, 1:]
        res = chain(resid, Sf, lo, hi, p0[1:], kappas, f"w{w0*1e6:.0f}",
                    nfev=1200)
        ks = np.array(kappas)
        cs = np.array([res[k][0] for k in kappas])
        kmin = float(ks[int(np.argmin(cs))])
        rows.append((w0, tr_ref, ub95(ks, cs), kmin,
                     float(res[kmin][1][I_BETA - 1])))
        print(f"  w0={w0*1e6:.0f}um transit={tr_ref:.3f}: "
              f"kappa<{rows[-1][2]:.3f} beta={rows[-1][4]:.4f}", flush=True)
    return rows


def main() -> int:
    if not (SESSION_20250704.is_dir() and SESSION_20250717.is_dir()):
        print(f"excluded trees absent ({SESSION_20250704}, {SESSION_20250717}) -- the "
              f"committed results/global_dataset_fit_norulers.csv is the record.")
        return 0
    camp = load_campaign_all()
    reh, n_corrupt = load_session_20250704()
    _, prates = load_t_rates()
    pil = load_session_20250717(prates["4192"][0])
    rul = load_rulers_t() if USE_RULERS else []
    for t in reh:
        t["T"] = 130.0; t["sl"] = "reh"
    for t in pil:
        t["T"] = 130.0; t["sl"] = "pil"
    traces = camp + reh + pil + rul
    npts = sum(len(t["x"]) for t in traces)
    nT = sum(1 for t in camp if t["T"] != 130.0)
    print(f"(M25) GLOBAL DATASET FIT: {len(traces)} traces "
          f"({len(camp)-nT} campaign p_sweep + {nT} campaign t_sweep + "
          f"{len(reh)} evening-session + {len(pil)} campaign-morning + {len(rul)} ruler "
          f"combs = ~{len(rul)*N_TEETH} tooth replicas), {npts} points")

    p0, lo, hi, offsets = build(traces)
    print(f"  {len(p0)} parameters")
    resid = make_resid(traces, offsets)
    Sf = sparsity(traces, offsets, len(p0))[:, 1:]
    t0 = time.time()
    print("  kappa profile, forward:")
    fwd = chain(resid, Sf, lo, hi, p0[1:], KAPPAS, "F")
    print("  kappa profile, backward:")
    bwd = chain(resid, Sf, lo, hi, fwd[KAPPAS[-1]][1], KAPPAS[::-1], "B")
    prof = {k: min(fwd[k][0], bwd[k][0]) for k in KAPPAS}
    kmin = min(prof, key=prof.get)
    best_q = fwd[kmin][1] if fwd[kmin][0] <= bwd[kmin][0] else bwd[kmin][1]
    ks = np.array(KAPPAS); cs = np.array([prof[k] for k in KAPPAS])
    ka = ub95(ks, cs)
    beta_fit = best_q[I_BETA - 1]

    # ---- the joint (kappa, beta) confidence region -------------------
    betas = tuple(round(b, 4) for b in np.linspace(0.005, 0.075, 8))
    print("\n  joint (kappa, beta) region:")
    g2 = profile2d(resid, Sf, lo, hi, best_q, KAPPAS, betas)
    c2min = min(g2.values())
    # 1-parameter and 2-parameter thresholds
    beta_prof = {b: min(g2[(k, b)] for k in KAPPAS) for b in betas}
    bmin = min(beta_prof, key=beta_prof.get)
    b_lo95, b_hi95 = _crossings(sorted(beta_prof),
                                [beta_prof[b] for b in sorted(beta_prof)], 3.841)

    # ---- resolve that interval instead of asserting it (addendum 30) ------
    # Identical to the primary arm's loop, and here for the same reason: a
    # 0.01-step grid cannot resolve an interval about 0.001 wide, so the
    # reported minimum is whichever grid point sat lowest. Refine about the
    # running minimum until the interval spans MIN_SPAN_STEPS of the grid that
    # resolves it, the criterion tests/test_interval_sanity.py applies.
    MIN_SPAN_STEPS, MAX_ROUNDS = 4.0, 4
    step = float(betas[1] - betas[0])
    for rnd in range(1, MAX_ROUNDS + 1):
        if (b_hi95 - b_lo95) >= MIN_SPAN_STEPS * step:
            break
        step /= 8.0
        centre = min(beta_prof, key=beta_prof.get)
        fresh = tuple(sorted({round(centre + j * step, 6)
                              for j in range(-6, 7)} - set(beta_prof)))
        fresh = tuple(b for b in fresh if b > 0)
        if not fresh:
            break
        print(f"    refine round {rnd}: {len(fresh)} betas at step {step:.5f} "
              f"about {centre:.4f}", flush=True)
        g2.update(profile2d(resid, Sf, lo, hi, best_q, KAPPAS, fresh,
                            tag=f"2D-r{rnd}"))
        for b in fresh:
            beta_prof[b] = min(g2[(k, b)] for k in KAPPAS)
        bs_sorted = sorted(beta_prof)
        b_lo95, b_hi95 = _crossings(bs_sorted,
                                    [beta_prof[b] for b in bs_sorted], 3.841)
    beta_grid_step = step
    c2min = min(g2.values())
    beta_prof = {b: min(g2[(k, b)] for k in KAPPAS) for b in sorted(beta_prof)}
    bmin = min(beta_prof, key=beta_prof.get)
    print(f"    beta_self profile minimum {bmin:.4f}, "
          f"95% (1-par, dchi2<3.84) range [{b_lo95:.4f}, {b_hi95:.4f}] "
          f"at grid step {beta_grid_step:.5f}")

    # ---- how the answer depends on the assumed waist ------------------
    print("\n  w0 dependence (the conditionality, mapped):")
    # DELIBERATELY WIDER THAN constants.W0_BAND_M, and left literal for that
    # reason (noted 2026-08-10, when the band narrowed to 62-68 um and a
    # different hard-coded band in run_global_fit.py turned out to be two
    # generations stale). This is a SENSITIVITY scan: its job is to show how
    # the answer moves outside the band as well as inside it, so tying it to
    # the band would destroy what it is for. The band sits inside this range.
    w0rows = w0_scan(traces, offsets, (56e-6, 60e-6, 64e-6, 68e-6, 72e-6),
                     KAPPAS)

    print(f"\n  min kappa = {kmin}, dchi2(0) = {prof[0.0]-min(cs):.2f}")
    print(f"  **95% UB kappa < {ka:.3f} MHz/W -> S0(225) < {ka*0.225:.3f} MHz**")
    print(f"  beta_self (joint, at the profile minimum) = {beta_fit:.4f} "
          f"MHz per 1e12 cm^-3")
    print(f"  ({(time.time()-t0)/3600:.1f} h)")

    with open(C.RESULTS_DIR / "global_dataset_fit_norulers.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerow(["kappa_ub95", "primary", f"{ka:.3f}", "",
                    "MHz per W; 95% one-sided profile-likelihood bound on the "
                    "AC-Stark coefficient, beta_self free (not a prior)"])
        w.writerow(["S0_225mW_ub95", "primary", f"{ka*0.225:.3f}", "",
                    "MHz, transition axis, at the campaign's maximum power"])
        w.writerow(["kappa_min", "primary", f"{kmin:.3f}", "",
                    "MHz per W; profile minimum -- NOT a detection unless "
                    "dchi2_kappa0 is large"])
        w.writerow(["dchi2_kappa0", "primary", f"{prof[0.0]-min(cs):.2f}", "",
                    "chi2(kappa=0) - chi2(min)"])
        w.writerow(["kappa_pred", "prediction", f"{KAPPA_PRED:.3f}", "",
                    f"MHz per W at w0={C.W0_MEASURED_M*1e6:.0f} um, "
                    f"rho={C.RHO_RETRO}"])
        w.writerow(["beta_self_joint", "primary", f"{beta_fit:.4f}", "",
                    "MHz per 1e12 cm^-3; fitted JOINTLY with kappa over the "
                    "x53 density lever -- no Stark prior, no transit-derived "
                    "beta prior, the two coefficients' covariance propagated"])
        for b in SL_BLOCKS:
            w.writerow(["sigma_laser", b, f"{best_q[I_SL + SL_IX[b] - 1]:.3f}", "",
                        "MHz, transition axis; free per session/temperature block"])
        sp_keys = sp_keys_for(traces)
        sp_ix = {k: i for i, k in enumerate(sp_keys)}
        for (blk, pk), i in sp_ix.items():
            sp_val = best_q[NS + i - 1]
            dev = sp_val - best_q[I_SL + SL_IX[blk] - 1]
            w.writerow(["sigma_laser_sp", f"{blk}_{pk}", f"{sp_val:.3f}", f"{dev:+.3f}",
                        f"MHz, transition axis; per-(session,peak) sigma_laser, "
                        f"hierarchical shrinkage prior width "
                        f"{SIGMA_SP_PRIOR_MHZ*1e3:.0f} kHz toward the {blk} pooled "
                        f"mean (err column: deviation from that mean)"])
        for k, pk in enumerate(PEAKS):
            w.writerow(["reh_rate", pk, f"{np.exp(best_q[I_REHRATE + k - 1]):.5f}",
                        "", "MHz per ms, transition; fitted evening-session scan rate"])
        w.writerow(["pilot_rate_scale", "nuisance",
                    f"{np.exp(best_q[I_PILSCALE - 1]):.4f}", "",
                    "campaign-morning axis = campaign 4192 rate x this, bounded [0.9,1.1]"])
        w.writerow(["n_traces", "camp_p/camp_t/reh/pil/ruler",
                    f"{len(camp)-nT}/{nT}/{len(reh)}/{len(pil)}/{len(rul)}", "",
                    f"{npts} points total ({n_corrupt} evening-session files "
                    f"unusable); rulers enter as five-tooth combs with free "
                    f"tooth amplitudes"])
        for k in KAPPAS:
            w.writerow(["profile_point", f"{k:.3f}", f"{prof[k]:.2f}", "",
                        "chi2 at this kappa, beta and all nuisances re-minimized"])
        w.writerow(["beta_self_min", "joint_region", f"{bmin:.5f}", "",
                    "MHz per 1e12 cm^-3; beta at the 2D profile minimum, on the "
                    f"refined grid of step {beta_grid_step:.5f}"])
        w.writerow(["beta_self_lo95", "joint_region", f"{b_lo95:.5f}", "",
                    "MHz per 1e12 cm^-3; 1-parameter 95% (dchi2 < 3.841), "
                    "kappa profiled out at each beta, edges interpolated in "
                    "sqrt(dchi2) on a grid refined until the interval spans it"])
        w.writerow(["beta_self_hi95", "joint_region", f"{b_hi95:.5f}", "",
                    "MHz per 1e12 cm^-3; upper edge of the same interval"])
        w.writerow(["beta_grid_step", "joint_region", f"{beta_grid_step:.5f}", "",
                    "MHz per 1e12 cm^-3; the spacing the interval above was "
                    "resolved on, refined down from 0.01000 by the loop of "
                    "addendum 30 -- quote it whenever the interval is quoted"])
        for (kk, bb), cc in sorted(g2.items()):
            if bb not in betas:
                continue
            w.writerow(["joint_chi2", f"k{kk:.3f}_b{bb:.4f}",
                        f"{cc - c2min:+.3f}", "",
                        "dchi2 above the joint minimum on the (kappa, beta) "
                        "grid -- the confidence REGION, not two separate bounds"])
        for bb in sorted(beta_prof):
            w.writerow(["beta_profile", f"{bb:.5f}",
                        f"{beta_prof[bb] - min(beta_prof.values()):+.3f}", "",
                        "dchi2 above the beta profile minimum, kappa profiled "
                        "out on the kappa grid -- the curve the 95% interval "
                        "is read off, coarse and refined points together"])
        for w0, tr_ref, kub, kmn, bfit in w0rows:
            w.writerow(["w0_scan", f"{w0*1e6:.0f}um",
                        f"{kub:.3f}", f"{bfit:.4f}",
                        f"value=95% kappa bound, err=beta_self, at transit_ref "
                        f"{tr_ref:.3f} MHz -- how both coefficients depend on "
                        f"the ASSUMED waist, which the dataset cannot pin"])
    print("\n  Wrote results/global_dataset_fit_norulers.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
