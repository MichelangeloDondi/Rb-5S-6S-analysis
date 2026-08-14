#!/usr/bin/env python3
"""
M28: the cross-campaign full-dataset joint fit -- M23's construction, M25's data.

THE SPECIFICATION IS THE RECORD. This module was written against
docs/notes/full_dataset_fit_prereg.md, which was written first: the census, the
hierarchy, the priors, the QC gates and their thresholds, the kappa grid, the
seeding order and every acceptance criterion are fixed there, before any number
came out of the fit. Read that file before this one. Where the two disagree the
note is right and the code is a defect.

WHAT IT IS. M23 (run_stark_joint.py) profiles the AC-Stark coefficient kappa
with each peak's collisional width held under a Gaussian prior, and reads only
the POWER-sweep traces of three sessions. M25 (run_global_dataset_fit.py) reads
every canonical trace and frees beta_self alongside kappa, which buys a joint
(kappa, beta) region and spends the temperature ladder on a second free
coefficient in the same width budget. This module takes the third corner: the
FULL dataset, the collisional term under the repo's own FOUR-POINT measurement
as a prior, and one profiled coefficient.

    gamma_coll(peak, T) = beta_self(peak) * N(T)      beta_self per peak, prior
    transit(T)          = transit(110 C) * sqrt(T)    fixed form, rides on w0
    S0(P)               = kappa * P                   profiled on the grid

so the 59 campaign t_sweep traces anchor the CORE the power ladder is trying to
see past, while the four-point beta_self prior (70/90/110/130 C, dof 2, the
x52.5 density lever of RESEARCH_DECISIONS section 9) keeps the collisional term
tied to the dataset's own measurement instead of floating free.

THE HIERARCHY is campaign x session x peak. The campaign level carries no free
parameter today, because the dataset is one campaign. It exists as a key on
every trace and as the outer grouping of the sigma block so that a second
campaign folds in without restructuring the model. Below it: Vsat per
campaign-instrument (Agilent for campaign and campaign-morning, LeCroy for the
evening session), beta_self per peak under its prior, sigma_laser per
(session-block, peak) with a 150 kHz hierarchical shrinkage prior toward its
block's population mean, the evening-session scan rate per peak, the
campaign-morning rate scale under M26's measured box, and
four free parameters per trace. Every centre is free and NO centre is
interpreted, per M21.

THE RULERS ARE OUT. Addendum 22 derived the comb's tooth amplitudes and tested
the derivation against the measured ratios: the temperature-session rulers fit
reasonably, the power-session bracket rulers do not fit at all. Ruler traces are
therefore not licensed as lineshape data until an amplitude model exists that
closes on both populations. M25 admits them as seven-tooth combs and reports the
with-and-without gap as a stated systematic. This module does not reopen that.
When the amplitude model lands, the rulers join here as a fifth session with
their own sigma block, not as a variant of the existing four.

THE STARTING-POINT DISCIPLINE IS STRUCTURAL FROM BIRTH, not retrofitted after an
incident. RESEARCH_DECISIONS section 11 and methods 06 section 4.12: the wing
variant runs FIRST because a cold start finds the true local minimum reliably there,
every other family is seeded from a converged solution in addition to running
cold, the profile is the POINTWISE MINIMUM over chains (so a seed can only
improve a profile, never inflate one), and no cold-start profile is quoted
without a seeded twin. That last clause is why this module runs FIVE families
where M23 runs four: M23's own minimum search, the cold wing variant, is quoted
from cold chains alone, which is the one place its rule is not yet satisfied
here. The order is

    1. W-  wing free, evening-session direction -1, cold forward and backward
    2. P-  no wing, direction -1, cold pair PLUS a chain seeded from W-
    3. W-  twin, seeded from P- with the wing entries re-inserted
    4. P+  no wing, direction +1, cold pair PLUS a chain seeded from P-
    5. W+  wing free, direction +1, cold pair PLUS a chain seeded from W-

THE QC GATES ARE PRE-REGISTERED and evaluated whether they fire or not. At load:
a canonical RF-off trace carrying a hard QC flag is admitted only if the flag is
the second-structure class AND the structure lies outside the fit window, which
is checked mechanically by recomputing rb5s6s.qc.trace_metrics on the WINDOWED
data and requiring n_major <= 1. Today that examines three traces (4207 at
25 mW, repeats 2, 3 and 5) and admits all three, which confirms the curator's
own remedy ("mask at fit time") rather than taking it on trust. After the fit:
eight acceptance gates, thresholds fixed in the note, written to the CSV as
gate_* rows. A stop-class failure (census, a railed shared parameter, a missing
95% crossing) returns exit code 1 and the numbers do not enter a document.

REUSE. The evening-session and campaign-morning loaders, the measured
campaign-morning scale, the peak list,
the excluded paths, the profile-grid floor, the wing standoff and ub95 are
IMPORTED from run_stark_joint, which is untouched by this module. The campaign
loader is M25's, extended with the QC gate, the role tag and the manifest file
key that the gate needs. The chain, bidirectional-profile, strip_wing and
sparsity patterns follow M23's, re-cut for this layout.

RUNTIME: long, hours, single process. Run it in the background. The excluded
2025-07-04 and campaign-morning trees must be present; without them the module prints what
is missing and exits 0 (the build_clock_table pattern). Raw traces never enter
the repository.

    python scripts/run_full_dataset_fit.py            # the production run
    python scripts/run_full_dataset_fit.py --smoke    # every code path, minutes

Writes results/full_dataset_fit.csv and runs annotate_results_status.py. Reads
results/beta_self.csv (run M4 first), results/qc_metrics.csv (run M0 first),
results/morning_ruler.csv (M26) and the M2 bracket rates.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
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
from rb5s6s.lineshape import stark_shift_S0_mhz  # noqa: E402
from rb5s6s.linefit import (_shared_profile_grid, adaptive_halfwidth,  # noqa: E402
                            to_frequency, transit_fwhm_at_T)
from rb5s6s.noise import condition_noise_model, sigma_of_v, signal_level  # noqa: E402
from rb5s6s.qc import trace_metrics  # noqa: E402
from run_beta_self import load_t_rates  # noqa: E402
from run_stark_joint import (DNU_FLOOR, NU0_WING, PEAKS, SESSION_20250717,  # noqa: E402
                             SESSION_20250704, load_session_20250717, load_session_20250704,
                             measured_pilot_scale, ub95)

PK_IX = {p: i for i, p in enumerate(PEAKS)}
CAMPAIGN = "camp2025"
"""The dataset's single campaign. Every trace carries it so that a second
campaign folds into the same loaders, the same sigma blocks and the same CSV
without restructuring the model."""

# ---------------------------------------------------------------------------
# the parameter layout (see the note, section 3)
# ---------------------------------------------------------------------------
SL_BLOCKS = ["camp70", "camp90", "camp110", "camp130", "reh", "pil"]
SL_IX = {b: i for i, b in enumerate(SL_BLOCKS)}
I_KAPPA = 0
I_VSAT_AG = 1                 # Agilent: campaign + campaign-morning
I_VSAT_LC = 2                 # LeCroy: evening session
I_BETA = 3                    # 4, one per peak, under the four-point prior
I_SL = I_BETA + len(PEAKS)    # 6 block-level population means
I_REHRATE = I_SL + len(SL_BLOCKS)   # 4 evening-session scan rates (log)
I_PILSCALE = I_REHRATE + len(PEAKS)
NS = I_PILSCALE + 1           # 18; the per-(block, peak) sigma_sp block starts here
N_UNIT = 1e12

SIGMA_SP_PRIOR_MHZ = 0.15
"""Shrinkage prior width tying each per-(block, peak) sigma_sp to its block's
population mean. The mean absolute pull of the four free-Gaussian-sigma probes
at camp130 is 147.5 kHz, rounded to 150 kHz (RESEARCH_DECISIONS section 10). It
is the scale a real per-peak effect is expected to sit at, not a value tuned to
this fit's outcome."""

KAPPA_PRED = stark_shift_S0_mhz(1.0, C.W0_MEASURED_M, rho=C.RHO_RETRO)
KAPPAS = tuple(sorted({0.0, 0.25, 0.5, 0.75, 1.0, round(KAPPA_PRED, 3),
                       1.5, 2.0, 2.62, 3.5, 5.0}))
KAPPAS_LOPO = tuple(sorted({0.0, 0.25, 1.0, round(KAPPA_PRED, 3), 2.0, 2.62}))
KAPPAS_SMOKE = tuple(sorted({0.0, round(KAPPA_PRED, 3), 5.0}))
KAPPAS_EXTENDED = tuple(sorted(set(KAPPAS) | {10.0, 20.0}))

# ---------------------------------------------------------------------------
# the acceptance gates (see the note, section 8). Fixed before the run.
# ---------------------------------------------------------------------------
GATE_N_TRACES = 231           # 100 p_sweep + 59 t_sweep + 46 evening-session + 26 campaign-morning
GATE_CHI2_LO, GATE_CHI2_HI = 0.3, 3.0
GATE_PRIOR_TENSION = 3.0
GATE_BASIN_GAP = 1000.0
GATE_DCHI2_DETECT = 9.0
RAIL_TOL = 1e-6

SMOKE_REPEATS = 1             # traces kept per condition group in a smoke run
SMOKE_DECIMATE = 3            # and one sample in this many kept from each trace


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def beta_priors() -> dict:
    """beta_self per peak from the repo's own FOUR-POINT lever.

    results/beta_self.csv carries the 70/90/110/130 C construction (dof 2, the
    x52.5 density lever) that RESEARCH_DECISIONS section 9 promoted to the sole
    headline and section 10 propagated into the code. M23 collapses the same
    file to a gamma_coll(130 C) prior because it has no temperature lever; this
    module has one, so the prior stays on the coefficient itself."""
    out = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "beta_self.csv")):
        out[r["peak"]] = (float(r["beta_self"]), float(r["beta_self_err"]))
    return out


def hard_flag_map() -> dict:
    """file -> hard_flags string from the M0 QC pass. Empty dict if absent."""
    path = C.RESULTS_DIR / "qc_metrics.csv"
    if not path.exists():
        return {}
    return {r["file"]: r["hard_flags"].strip()
            for r in csv.DictReader(open(path)) if r["hard_flags"].strip()}


def qc_admit(rec, t_ms, v, mask, flags):
    """Gate A1 of the note. Returns (admit, verdict_string).

    A canonical RF-off trace carrying a hard QC flag is admitted only if the
    flag is the second-structure class AND the second structure lies OUTSIDE
    the fit window. The window is where the fit actually looks, so the check is
    to recompute the same physics-blind structure metric on the WINDOWED data
    and require at most one major structure there. Any other hard-flag class
    excludes the trace outright. Nothing here knows what the physics fit will
    prefer, which is what keeps QC-based exclusion unbiased (M0)."""
    flag = flags.get(rec["file"], "")
    if not flag:
        return True, "clean"
    if "second structure" not in flag:
        return False, f"excluded, hard flag: {flag[:60]}"
    n_major = trace_metrics(t_ms[mask], v[mask])["n_major"]
    if n_major <= 1.5:
        return True, f"admitted, second structure outside the window (n_major={n_major:.0f})"
    return False, f"excluded, second structure INSIDE the window (n_major={n_major:.0f})"


def load_campaign_full(smoke=False):
    """Campaign p_sweep AND t_sweep, each tagged with its temperature, through
    the pre-registered QC gates.

    M25's load_campaign_all, plus three things this module needs: the gate A1
    admission check, the manifest `file` key the gate reports against, and the
    `role` tag that separates the power ladder from the temperature ladder in
    the partial chi-squared columns. The noise law is conditioned on the
    ADMITTED traces of each group, since those are the ones entering the fit."""
    rows = load_manifest()
    _, prates = load_t_rates()
    flags = hard_flag_map()
    out, examined, dropped = [], [], []
    groups = defaultdict(list)
    for r in rows:
        if r["flag"] != "canonical" or r["rf_on"] == "True":
            continue
        if r["role"] == "p_sweep":
            groups[(r["peak"], 130.0, int(r["power_mW"]) / 1e3, "p_sweep")].append(r)
        elif r["role"] == "t_sweep":
            groups[(r["peak"], float(r["temperature_C"]), 0.225, "t_sweep")].append(r)
    for (pk, T, P, role), recs in sorted(groups.items()):
        rate, _ = prates[pk]
        kept = []
        for r in recs:
            t, v = load_trace(trace_path(r))
            nu = to_frequency(t, rate)
            lev, base = signal_level(v)
            c0 = float(nu[int(np.argmax(lev))])
            m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
            admit, verdict = qc_admit(r, t, v, m, flags)
            if verdict != "clean":
                examined.append((r["file"], verdict))
            if not admit:
                continue
            kept.append((r, v, nu, lev, base, c0, m))
        if len(kept) < 3:                      # gate A2: the M1 law needs a group
            dropped.append((pk, T, P, len(kept)))
            continue
        law = condition_noise_model([k[1] for k in kept])
        tau = max(law.get("tau_int", 1.0), 1.0)
        for r, v, nu, lev, base, c0, m in (kept[:SMOKE_REPEATS] if smoke else kept):
            sg = np.maximum(sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
            out.append(dict(campaign=CAMPAIGN, sess="camp", role=role, peak=pk,
                            T=T, P=P, x=nu[m], v=v[m], sg=sg[m], c0=c0,
                            A0=float(lev.max()), b0=float(base),
                            sl=f"camp{int(T)}", file=r["file"]))
    return out, examined, dropped


def thin(traces, key):
    """Keep SMOKE_REPEATS traces per condition group. Smoke runs only: the
    noise law is already conditioned on the full group, so this thins what the
    fit sees without touching how it is weighted."""
    seen = defaultdict(int)
    out = []
    for t in traces:
        k = key(t)
        seen[k] += 1
        if seen[k] <= SMOKE_REPEATS:
            out.append(t)
    return out


def decimate(traces, k=SMOKE_DECIMATE):
    """Keep one sample in k from every trace. Smoke runs only. It changes the
    arrays the same code path walks and nothing else, which is what makes a
    smoke run cheap without letting it exercise a different fitter."""
    out = []
    for t in traces:
        d = dict(t)
        d["x"], d["v"], d["sg"] = t["x"][::k], t["v"][::k], t["sg"][::k]
        out.append(d)
    return out


# ---------------------------------------------------------------------------
# the model
# ---------------------------------------------------------------------------

def sp_keys_for(traces):
    """Realized (session block, peak) cells, sorted for a deterministic
    ordering that build(), make_resid() and sparsity() each recompute from the
    same trace list rather than threading an extra argument everywhere."""
    return sorted({(t["sl"], t["peak"]) for t in traces})


def shared_names(sp_keys, wing):
    """Human-readable names for the shared block, used by the railing gate."""
    names = ["kappa", "Vsat_agilent", "Vsat_lecroy"]
    names += [f"beta_self_{pk}" for pk in PEAKS]
    names += [f"sigma_laser_s_{b}" for b in SL_BLOCKS]
    names += [f"reh_rate_{pk}" for pk in PEAKS]
    names += ["pilot_rate_scale"]
    names += [f"sigma_laser_sp_{b}_{pk}" for b, pk in sp_keys]
    if wing:
        names += ["wing_fraction", "wing_scale"]
    return names


def build(traces, priors, wing):
    sp_keys = sp_keys_for(traces)
    n_sp = len(sp_keys)
    n_shared = NS + n_sp + (2 if wing else 0)
    p0 = np.zeros(n_shared + 4 * len(traces))
    lo = np.full_like(p0, -np.inf)
    hi = np.full_like(p0, np.inf)
    p0[I_KAPPA] = 0.0; lo[I_KAPPA] = 0.0; hi[I_KAPPA] = 60.0
    for j in (I_VSAT_AG, I_VSAT_LC):
        p0[j] = 5.0; lo[j] = -1.0; hi[j] = 6.0
    r0 = np.log(5.9 / 470.0)
    for k, pk in enumerate(PEAKS):
        p0[I_BETA + k] = priors[pk][0]; lo[I_BETA + k] = 0.0; hi[I_BETA + k] = 5.0
        j = I_REHRATE + k
        p0[j] = r0; lo[j] = r0 - np.log(4); hi[j] = r0 + np.log(4)
    for b in SL_BLOCKS:
        j = I_SL + SL_IX[b]
        p0[j] = 1.2; lo[j] = 0.05; hi[j] = 50.0
    _mps = measured_pilot_scale()
    if _mps is not None:
        _m, _e = _mps
        p0[I_PILSCALE] = np.log(_m)
        lo[I_PILSCALE] = np.log(_m - 5 * _e); hi[I_PILSCALE] = np.log(_m + 5 * _e)
    else:
        p0[I_PILSCALE] = 0.0
        lo[I_PILSCALE] = np.log(0.9); hi[I_PILSCALE] = np.log(1.1)
    for i in range(n_sp):
        j = NS + i
        p0[j] = 1.2; lo[j] = 0.05; hi[j] = 50.0
    if wing:
        j = NS + n_sp
        p0[j] = 0.005; lo[j] = 0.0; hi[j] = 0.5
        p0[j + 1] = np.log(6.0); lo[j + 1] = np.log(2.0); hi[j + 1] = np.log(60.0)
    for i, t in enumerate(traces):
        j = n_shared + 4 * i
        p0[j:j + 4] = [t["A0"], t["c0"], t["b0"], 0.0]
        lo[j] = 0.0
        span = 1200.0 if t["sess"] == "reh" else 8.0
        lo[j + 1] = t["c0"] - span; hi[j + 1] = t["c0"] + span
    return p0, lo, hi


def make_resid(traces, priors, direction, wing):
    sp_keys = sp_keys_for(traces)
    sp_ix = {k: i for i, k in enumerate(sp_keys)}
    n_sp = len(sp_keys)
    n_shared = NS + n_sp + (2 if wing else 0)
    i_wing = NS + n_sp
    dens = {T: float(number_density_cm3(np.array([T]))[0]) / N_UNIT
            for T in sorted({t["T"] for t in traces})}
    transits = {T: transit_fwhm_at_T(T, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
                for T in dens}

    def resid(p, kappa=None):
        kap = p[I_KAPPA] if kappa is None else kappa
        f_w = p[i_wing] if wing else 0.0
        w_w = np.exp(p[i_wing + 1]) if wing else 1.0
        cache = {}
        out = []
        for i, t in enumerate(traces):
            k = PK_IX[t["peak"]]
            T = t["T"]
            gc = p[I_BETA + k] * dens[T]
            sl = p[NS + sp_ix[(t["sl"], t["peak"])]]
            s0 = kap * t["P"]
            sess = t["sess"]
            key = (sess == "reh", round(gc, 7), round(sl, 7),
                   round(transits[T], 7), round(s0, 8),
                   round(f_w, 7), round(w_w, 5))
            if key not in cache:
                g, prof = _shared_profile_grid(gc, sl, transits[T], s0,
                                               "gaussian", dnu_floor=DNU_FLOOR)
                if f_w > 0:
                    msk = g < -NU0_WING
                    prof = prof.copy()
                    prof[msk] += (f_w * prof.max()
                                  * np.exp(-(np.abs(g[msk]) - NU0_WING) / w_w))
                if sess == "reh" and direction < 0:
                    prof = prof[::-1]
                cache[key] = (g, prof)
            g, prof = cache[key]
            A, cc, b0, b1 = p[n_shared + 4 * i: n_shared + 4 * i + 4]
            if sess == "reh":
                rate = np.exp(p[I_REHRATE + k])
                lin = A * np.interp(rate * (t["x"] - cc), g, prof, left=0., right=0.)
                Vs = np.exp(p[I_VSAT_LC])
            elif sess == "pil":
                scale = np.exp(p[I_PILSCALE])
                lin = A * np.interp(scale * t["x"] - cc, g, prof, left=0., right=0.)
                Vs = np.exp(p[I_VSAT_AG])
            else:
                lin = A * np.interp(t["x"] - cc, g, prof, left=0., right=0.)
                Vs = np.exp(p[I_VSAT_AG])
            mdl = Vs * (1.0 - np.exp(-lin / Vs)) + b0 + b1 * t["x"]
            out.append((t["v"] - mdl) / t["sg"])
        # the four-point beta_self prior, one row per peak
        out.append(np.array([(p[I_BETA + k] - priors[pk][0]) / priors[pk][1]
                             for k, pk in enumerate(PEAKS)]))
        # hierarchical shrinkage: each sigma_sp toward its block's mean
        out.append(np.array([(p[NS + i] - p[I_SL + SL_IX[blk]]) / SIGMA_SP_PRIOR_MHZ
                             for (blk, _pk), i in sp_ix.items()]))
        return np.concatenate(out)
    return resid


def sparsity(traces, wing):
    sp_keys = sp_keys_for(traces)
    sp_ix = {k: i for i, k in enumerate(sp_keys)}
    n_sp = len(sp_keys)
    n_shared = NS + n_sp + (2 if wing else 0)
    i_wing = NS + n_sp
    n_rows = sum(len(t["x"]) for t in traces)
    S = lil_matrix((n_rows, n_shared + 4 * len(traces)), dtype=int)
    r0 = 0
    for i, t in enumerate(traces):
        n = len(t["x"]); k = PK_IX[t["peak"]]
        S[r0:r0 + n, I_KAPPA] = 1
        S[r0:r0 + n, I_BETA + k] = 1
        S[r0:r0 + n, NS + sp_ix[(t["sl"], t["peak"])]] = 1
        if wing:
            S[r0:r0 + n, i_wing] = 1; S[r0:r0 + n, i_wing + 1] = 1
        if t["sess"] == "reh":
            S[r0:r0 + n, I_VSAT_LC] = 1
            S[r0:r0 + n, I_REHRATE + k] = 1
        else:
            S[r0:r0 + n, I_VSAT_AG] = 1
            if t["sess"] == "pil":
                S[r0:r0 + n, I_PILSCALE] = 1
        S[r0:r0 + n, n_shared + 4 * i: n_shared + 4 * i + 4] = 1
        r0 += n
    pri = lil_matrix((len(PEAKS) + n_sp, S.shape[1]), dtype=int)
    for k in range(len(PEAKS)):
        pri[k, I_BETA + k] = 1
    for (blk, _pk), i in sp_ix.items():
        pri[len(PEAKS) + i, I_SL + SL_IX[blk]] = 1
        pri[len(PEAKS) + i, NS + i] = 1
    return vstack([S.tocsr(), pri.tocsr()]).tocsr()


# ---------------------------------------------------------------------------
# chains and profiles
# ---------------------------------------------------------------------------

def strip_wing(q, n_sp):
    """A wing-family solution vector, re-cut for the no-wing layout.

    The two shared wing entries sit at q indices NS-1+n_sp and NS+n_sp (q
    excludes kappa). Everything else transplants one to one, which is what
    makes seeding the primary from the minimum search legitimate."""
    return np.delete(q, [NS - 1 + n_sp, NS + n_sp])


def insert_wing(q, n_sp, f_w=0.005, log_w=np.log(6.0)):
    """The inverse: a no-wing solution re-cut for the wing layout, with the
    wing entries at their own seed values. Used for the minimum search's seeded
    twin, so that no cold-start profile is quoted without one."""
    return np.insert(q, NS - 1 + n_sp, [f_w, log_w])


def chain(resid, Sf, lo, hi, q0, kappas, ncamp, npld, tag, nfev=1500):
    """One warm-started sweep across the kappa grid. Logs in M23's line style.

    Returns kappa -> (chi2 total, chi2 campaign rows, chi2 power-ladder rows,
    parameter vector). The two partial sums answer whether the bound leans on
    the evening session's soft rate anchor and whether the temperature ladder that is
    new to this fit is doing the work."""
    res, q = {}, q0.copy()
    for kap in kappas:
        t0 = time.time()
        fn = lambda z: resid(np.concatenate([[0.0], z]), kappa=kap)  # noqa: E731
        s = least_squares(fn, q, bounds=(lo[1:], hi[1:]), jac_sparsity=Sf,
                          max_nfev=nfev, x_scale="jac", ftol=1e-12, xtol=1e-12)
        q = s.x.copy()
        r = fn(q)
        res[kap] = (float(np.sum(r * r)), float(np.sum(r[:ncamp] ** 2)),
                    float(np.sum(r[:npld] ** 2)), q.copy())
        print(f"    [{tag}] kappa={kap:5.2f}  chi2={np.sum(r * r):11.2f}"
              f"  ({time.time() - t0:4.0f}s, nfev={s.nfev})", flush=True)
    return res


def bidi_profile(traces, priors, direction, wing, tag, seeds=(),
                 kappas=KAPPAS, nfev=1500, cold=True):
    """Bidirectional profile plus any seeded chains, pointwise minimum kept.

    `seeds` are converged parameter vectors from other families, already
    re-cut for this layout. A seeded chain runs IN ADDITION to the cold pair,
    so a seed can only improve the profile. `cold=False` runs the seeded
    chains alone, which is how the minimum search gets its twin without paying
    for a second cold pair.

    Returns (profile array [kappa, total, campaign, power-ladder], kappa at the
    minimum, the parameter vector there, the cold-minus-seeded gap)."""
    p0, lo, hi = build(traces, priors, wing)
    resid = make_resid(traces, priors, direction, wing)
    Sf = sparsity(traces, wing)[:, 1:]
    ncamp = sum(len(t["x"]) for t in traces if t["sess"] == "camp")
    npld = sum(len(t["x"]) for t in traces
               if t["sess"] == "camp" and t["role"] == "p_sweep")
    cold_chains, seed_chains = [], []
    if cold:
        fwd = chain(resid, Sf, lo, hi, p0[1:], kappas, ncamp, npld, tag + ">", nfev)
        bwd = chain(resid, Sf, lo, hi, fwd[kappas[-1]][3], kappas[::-1],
                    ncamp, npld, tag + "<", nfev)
        cold_chains = [fwd, bwd]
    for n, seed in enumerate(seeds):
        seed_chains.append(chain(resid, Sf, lo, hi, seed, kappas, ncamp, npld,
                                 f"{tag}s{n}" if len(seeds) > 1 else tag + "s",
                                 nfev))
    chains = cold_chains + seed_chains
    prof, best, gap = [], (np.inf, None, None), -np.inf
    for kap in kappas:
        pick = min((c[kap] for c in chains), key=lambda r: r[0])
        prof.append((kap, pick[0], pick[1], pick[2]))
        if pick[0] < best[0]:
            best = (pick[0], kap, pick[3])
        if cold_chains and seed_chains:
            gap = max(gap, (min(c[kap][0] for c in cold_chains)
                            - min(c[kap][0] for c in seed_chains)))
    return np.array(prof), best[1], best[2], (gap if np.isfinite(gap) else float("nan"))


# ---------------------------------------------------------------------------
# the gates
# ---------------------------------------------------------------------------

RAIL_PHYSICS = ("beta_self_", "sigma_laser_", "reh_rate_")
"""Railing here is a stop: these carry the widths, and a railed parameter
carries no information while biasing everything sharing its budget, which is
the lesson the five-tooth ruler truncation taught M25."""


def railed_shared(q, lo, hi, names):
    """Shared parameters sitting on a bound, as (name, value, edge) triples.
    `q` excludes kappa, so the name list is offset by one."""
    out = []
    for j in range(len(names) - 1):
        val, a, b = q[j], lo[j + 1], hi[j + 1]
        scale = max(abs(a), abs(b), 1.0)
        if abs(val - a) <= RAIL_TOL * scale:
            out.append((names[j + 1], float(val), "lo"))
        elif abs(val - b) <= RAIL_TOL * scale:
            out.append((names[j + 1], float(val), "hi"))
    return out


def split_railings(railed):
    """Three classes, per the note's amendment 1.

    A saturation parameter at the TOP of its box is the EXPECTED outcome and
    not a defect: it says the detector ran linear, which is exactly what M23
    reports from the same box (Vsat_camp 402.8 V against a 403.4 V ceiling).
    A physics parameter on either edge is a stop. Everything else, which today
    means the campaign-morning axis scale against M26's measured box, is reported and
    flagged, because that gap is a live open question rather than a fault."""
    expected, stop, flagged = [], [], []
    for name, val, edge in railed:
        if name.startswith("Vsat") and edge == "hi":
            expected.append((name, val, edge))
        elif name.startswith(RAIL_PHYSICS):
            stop.append((name, val, edge))
        else:
            flagged.append((name, val, edge))
    return expected, stop, flagged


def _rail_str(items):
    return (", ".join(f"{n}={v:.6g} at its {e} bound" for n, v, e in items)
            if items else "none")


def gate_rows(*, n_traces, n_points, chi2_min, railed, tensions, ub, basin_gap,
              dir_delta, dchi2_0, smoke):
    """The eight acceptance gates of the note, section 8. Each returns a row
    whether it fires or not, and each carries its own threshold in the unit
    column so the CSV states what it was checked against."""
    rows = []

    def add(name, value, ok, threshold, stop, note):
        verdict = "SMOKE" if smoke and stop and not ok else ("PASS" if ok else "FAIL")
        rows.append((name, verdict, value, threshold, stop, note))

    add("gate_B1_census", n_traces, n_traces == GATE_N_TRACES,
        f"exactly {GATE_N_TRACES}", True,
        "trace count entering the fit; a silent loader change is what this catches")
    chi2p = chi2_min / max(n_points, 1)
    add("gate_B2_chi2_per_point", chi2p, GATE_CHI2_LO <= chi2p <= GATE_CHI2_HI,
        f"[{GATE_CHI2_LO}, {GATE_CHI2_HI}]", False,
        "chi2 at the profile minimum per fitted point")
    add("gate_B3_railed_physics", len(railed), not railed, "zero", True,
        "beta_self, sigma_laser or evening-session-rate parameters on a bound: "
        + _rail_str(railed))
    worst = max(tensions.values()) if tensions else 0.0
    add("gate_B4_prior_tension", worst, worst < GATE_PRIOR_TENSION,
        f"< {GATE_PRIOR_TENSION} sigma", False,
        "largest |posterior - prior| / prior error over the four peaks")
    add("gate_B5_ub95_in_grid", ub, np.isfinite(ub), "finite", True,
        "the 95% crossing must exist inside the kappa grid, not beyond it")
    add("gate_B6_basin_gap", basin_gap, not (basin_gap > GATE_BASIN_GAP),
        f"<= {GATE_BASIN_GAP}", False,
        "best cold chain minus best seeded chain; the pointwise minimum keeps "
        "the profile safe either way, so this is a flag and not a stop")
    add("gate_B7_direction_delta", dir_delta, dir_delta < GATE_BASIN_GAP,
        f"< {GATE_BASIN_GAP}", False,
        "max |chi2 difference| between evening-session axis directions; thousands "
        "means a parked chain, not a physical preference")
    add("gate_B8_dchi2_kappa0", dchi2_0, dchi2_0 < GATE_DCHI2_DETECT,
        f"< {GATE_DCHI2_DETECT}", False,
        "above this the profile prefers a positive shift at better than "
        "3 sigma, which is a detection claim and needs a decision")
    return rows


# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("--smoke", action="store_true",
                    help="one trace per condition group, one sample in three "
                         "from each, a three-point kappa grid and short "
                         "chains: exercises every code path in minutes, and "
                         "quotes nothing")
    ap.add_argument("--no-lopo", action="store_true",
                    help="skip the leave-one-peak-out family")
    args = ap.parse_args(argv)
    smoke = args.smoke

    if not (SESSION_20250704.is_dir() and SESSION_20250717.is_dir()):
        print(f"excluded tree(s) not on this machine "
              f"({SESSION_20250704}, {SESSION_20250717}) -- the committed "
              f"results/full_dataset_fit.csv is the record; nothing to do.")
        return 0

    kappas = KAPPAS_SMOKE if smoke else KAPPAS
    kappas_lopo = KAPPAS_SMOKE if smoke else KAPPAS_LOPO
    nfev = 120 if smoke else 1500
    nfev_lopo = 80 if smoke else 900

    priors = beta_priors()
    camp, qc_examined, qc_dropped = load_campaign_full(smoke=smoke)
    reh, n_corrupt = load_session_20250704()
    _, prates = load_t_rates()
    pil = load_session_20250717(prates["4192"][0])
    for t in reh:
        t.update(campaign=CAMPAIGN, T=130.0, sl="reh", role="p_sweep_reh", file="")
    for t in pil:
        t.update(campaign=CAMPAIGN, T=130.0, sl="pil", role="p_sweep_pil", file="")
    if smoke:
        reh = decimate(thin(reh, lambda t: (t["peak"], t["P"])))
        pil = decimate(thin(pil, lambda t: (t["peak"], t["P"])))
        camp = decimate(camp)
    camp_p = [t for t in camp if t["role"] == "p_sweep"]
    camp_t = [t for t in camp if t["role"] == "t_sweep"]
    traces = camp_p + camp_t + reh + pil       # ORDER MATTERS: partial chi2 sums
    npts = sum(len(t["x"]) for t in traces)
    sp_keys = sp_keys_for(traces)
    n_sp = len(sp_keys)
    p0_shape, _, _ = build(traces, priors, False)

    print(f"(M28){' SMOKE' if smoke else ''} CROSS-CAMPAIGN FULL-DATASET JOINT "
          f"FIT: {len(camp_p)} campaign p_sweep + {len(camp_t)} campaign "
          f"t_sweep + {len(reh)} evening-session ({n_corrupt} files unusable) + "
          f"{len(pil)} campaign-morning traces, {npts} points, {len(p0_shape)} parameters, "
          f"{n_sp} sigma cells")
    for f, verdict in qc_examined:
        print(f"  QC gate A1: {f}: {verdict}")
    for pk, T, P, n in qc_dropped:
        print(f"  QC gate A2: dropped group peak {pk} T={T} P={P} ({n} admitted)")
    if not qc_examined:
        print("  QC gate A1: no canonical RF-off trace carries a hard flag.")

    t0 = time.time()
    print("  wing robustness (dir -1, cold; the minimum search):")
    prof_c, kmin_c, q_c, _ = bidi_profile(traces, priors, -1, True, "C-",
                                          kappas=kappas, nfev=nfev)
    print("  primary profile (four-point priors, evening-session dir -1, seeded from C-):")
    prof_a, kmin_a, q_a, gap_a = bidi_profile(
        traces, priors, -1, False, "A-", seeds=(strip_wing(q_c, n_sp),),
        kappas=kappas, nfev=nfev)
    print("  wing minimum search's seeded twin (from A-; no cold profile is quoted alone):")
    prof_c2, kmin_c2, q_c2, _ = bidi_profile(
        traces, priors, -1, True, "C-t", seeds=(insert_wing(q_a, n_sp),),
        kappas=kappas, nfev=nfev, cold=False)
    gap_c = float(np.max(prof_c[:, 1] - prof_c2[:, 1]))
    if prof_c2[:, 1].min() < prof_c[:, 1].min():   # the twin found a better local minimum
        kmin_c, q_c = kmin_c2, q_c2
    prof_c = np.column_stack([prof_c[:, 0],
                              np.minimum(prof_c[:, 1:], prof_c2[:, 1:])])
    print("  direction check (dir +1, seeded from the dir -1 solution):")
    prof_b, kmin_b, _q_b, gap_b = bidi_profile(
        traces, priors, +1, False, "A+", seeds=(q_a,), kappas=kappas, nfev=nfev)
    print("  wing robustness (dir +1, seeded from C-):")
    prof_d, kmin_d, _q_d, gap_d = bidi_profile(
        traces, priors, +1, True, "C+", seeds=(q_c,), kappas=kappas, nfev=nfev)

    ka, kc = ub95(prof_a), ub95(prof_c)
    ka_camp = ub95(prof_a, col=2)
    ka_pld = ub95(prof_a, col=3)
    dchi2_a = float(prof_a[0, 1] - prof_a[:, 1].min())
    dir_delta = float(np.abs(prof_a[:, 1] - prof_b[:, 1]).max())
    basin_gap = float(np.nanmax([g for g in (gap_a, gap_b, gap_d, gap_c)
                                 if np.isfinite(g)] or [np.nan]))

    # leave-one-peak-out at the primary settings, seeded from the primary
    # solution. Peak 4192 gets the full grid because dropping it removes the
    # ENTIRE campaign-morning session, so that subset deserves a real profile bound.
    lopo, lopo_prof = {}, {}
    if not args.no_lopo:
        for drop in PEAKS:
            keep = [i for i, t in enumerate(traces) if t["peak"] != drop]
            sub = [traces[i] for i in keep]
            sub_keys = sp_keys_for(sub)
            n_sp_sub = len(sub_keys)
            p0s, los, his = build(sub, priors, False)
            qs = p0s[1:].copy()
            qs[:NS - 1] = q_a[:NS - 1]
            full_ix = {k: i for i, k in enumerate(sp_keys)}
            for i, k in enumerate(sub_keys):    # the surviving sigma cells
                qs[NS - 1 + i] = q_a[NS - 1 + full_ix[k]]
            for j, i in enumerate(keep):
                a, b = NS - 1 + n_sp_sub + 4 * j, NS - 1 + n_sp + 4 * i
                qs[a:a + 4] = q_a[b:b + 4]
            rs = make_resid(sub, priors, -1, False)
            Sfs = sparsity(sub, False)[:, 1:]
            ncs = sum(len(t["x"]) for t in sub if t["sess"] == "camp")
            nps = sum(len(t["x"]) for t in sub
                      if t["sess"] == "camp" and t["role"] == "p_sweep")
            grid = kappas if drop == "4192" else kappas_lopo
            res = chain(rs, Sfs, los, his, qs, grid, ncs, nps, f"L{drop}",
                        nfev_lopo)
            cs = {k: v[0] for k, v in res.items()}
            mn = min(cs.values())
            lopo[drop] = {k: cs[k] - mn for k in cs}
            lopo_prof[drop] = np.array([[k, cs[k], cs[k], cs[k]] for k in sorted(cs)])
            print(f"  LOPO {drop}: "
                  + "  ".join(f"k={k}:{lopo[drop][k]:+.2f}" for k in sorted(cs)))
    ka_d4192 = ub95(lopo_prof["4192"]) if "4192" in lopo_prof else float("nan")

    # ---- the gates -----------------------------------------------------
    names = shared_names(sp_keys, False)
    _, lo_a, hi_a = build(traces, priors, False)
    rail_expected, rail_stop, rail_flagged = split_railings(
        railed_shared(q_a, lo_a, hi_a, names))
    tensions = {pk: abs(q_a[I_BETA + k - 1] - priors[pk][0]) / priors[pk][1]
                for k, pk in enumerate(PEAKS)}
    gates = gate_rows(n_traces=len(traces), n_points=npts,
                      chi2_min=float(prof_a[:, 1].min()), railed=rail_stop,
                      tensions=tensions, ub=ka, basin_gap=basin_gap,
                      dir_delta=dir_delta, dchi2_0=dchi2_a, smoke=smoke)

    print(f"\n  primary: min kappa = {kmin_a}, dchi2(kappa=0) = {dchi2_a:.2f}")
    print(f"  **95% UB kappa < {ka:.3f} MHz/W -> S0(225 mW) < {ka * 0.225:.3f} MHz**")
    print(f"  campaign-only UB: kappa < {ka_camp:.3f} -> S0(225) < {ka_camp * 0.225:.3f}")
    print(f"  power-ladder-only UB: kappa < {ka_pld:.3f}")
    print(f"  wing-marginalized: min {kmin_c}, UB kappa < {kc:.3f}")
    print(f"  direction indifference: max |dchi2| between dirs = {dir_delta:.2f}")
    print(f"  local minimum gap (cold minus seeded, worst family) = {basin_gap:.2f}")
    for pk in PEAKS:
        print(f"  beta_self {pk}: post {q_a[I_BETA + PK_IX[pk] - 1]:.5f} vs prior "
              f"{priors[pk][0]:.5f}+/-{priors[pk][1]:.5f} "
              f"({tensions[pk]:.2f} sigma)")
    print(f"  railed, expected (a saturation ceiling means a linear detector): "
          f"{_rail_str(rail_expected)}")
    print(f"  railed, flagged nuisances: {_rail_str(rail_flagged)}")
    for name, verdict, value, threshold, stop, note in gates:
        print(f"  [{verdict}] {name} = {value:.4g} (want {threshold})"
              + ("  <-- STOP CLASS" if stop and verdict == "FAIL" else ""))
    print(f"  ({(time.time() - t0) / 60:.0f} min)")

    # ---- the CSV -------------------------------------------------------
    path = C.RESULTS_DIR / "full_dataset_fit.csv"
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerow(["kappa_min", "primary", f"{kmin_a:.2f}", "",
                    "MHz per W; profile minimum, four-point priors, dir -1; "
                    "NOT a detection (see dchi2_kappa0)"])
        w.writerow(["dchi2_kappa0", "primary", f"{dchi2_a:.2f}", "",
                    "chi2(kappa=0) - chi2(min); the strength of the kappa>0 "
                    "preference"])
        w.writerow(["kappa_ub95", "primary", f"{ka:.3f}", "",
                    "MHz per W; 95% one-sided profile-likelihood bound over "
                    "the FULL dataset (negative kappa is flat by construction: "
                    "the ramp model only broadens red)"])
        w.writerow(["S0_225mW_ub95", "primary", f"{ka * 0.225:.3f}", "",
                    "MHz, transition axis; full-dataset bound at the "
                    "campaign's maximum power"])
        w.writerow(["S0_270mW_ub95", "primary", f"{ka * 0.270:.3f}", "",
                    "MHz; at the evening session's maximum power"])
        w.writerow(["kappa_pred", "prediction", f"{KAPPA_PRED:.3f}", "",
                    f"MHz per W; the PREDICTED coefficient at the current "
                    f"priors (w0 = {C.W0_MEASURED_M * 1e6:.0f} um, rho = "
                    f"{C.RHO_RETRO}), computed from constants"])
        w.writerow(["S0_225mW_pred", "prediction", f"{KAPPA_PRED * 0.225:.3f}", "",
                    "MHz, transition axis; the prediction at 225 mW"])
        w.writerow(["kappa_ub95_camponly", "robustness", f"{ka_camp:.3f}", "",
                    "MHz per W; campaign rows of the same profile (power AND "
                    "temperature ladders), so the bound does not lean on the "
                    "evening session's soft rate anchor"])
        w.writerow(["kappa_ub95_pladder", "robustness", f"{ka_pld:.3f}", "",
                    "MHz per W; campaign POWER-ladder rows only -- the M23 "
                    "trace set inside this fit, so the difference from the "
                    "primary is what the temperature ladder adds"])
        w.writerow(["kappa_min_wing", "robustness", f"{kmin_c:.2f}", "",
                    "MHz per W; minimum with the red-wing nuisance free"])
        w.writerow(["kappa_ub95_wing", "robustness", f"{kc:.3f}", "",
                    "MHz per W; bound with the wing marginalized -- quote "
                    "alongside the primary, the gap IS the wing systematic"])
        w.writerow(["direction_dchi2_max", "robustness", f"{dir_delta:.2f}", "",
                    "max |chi2 difference| between evening-session axis directions "
                    "across the profile; small = indifferent"])
        w.writerow(["basin_gap_max", "robustness", f"{basin_gap:.2f}", "",
                    "chi2; worst (best cold chain - best seeded chain) over "
                    "the families that have both. Large = a cold chain parked, "
                    "and the pointwise minimum already discarded it"])
        if np.isfinite(ka_d4192):
            w.writerow(["kappa_ub95_drop4192", "robustness", f"{ka_d4192:.3f}", "",
                        "MHz per W; 95% bound with peak 4192 dropped, which "
                        "removes the ENTIRE campaign-morning session -- the most "
                        "conservative subset"])
            w.writerow(["S0_225mW_ub95_drop4192", "robustness",
                        f"{ka_d4192 * 0.225:.3f}", "",
                        "MHz; the drop-4192 bound at 225 mW"])
        for pk in PEAKS:
            if pk in lopo:
                w.writerow(["lopo_dchi2_pred", pk,
                            f"{lopo[pk][round(KAPPA_PRED, 3)]:+.2f}", "",
                            "chi2(kappa_pred) - min with this peak dropped; "
                            "all positive and similar = no single peak drives it"])
                if 2.62 in lopo[pk]:
                    w.writerow(["lopo_dchi2_262", pk, f"{lopo[pk][2.62]:+.2f}", "",
                                "chi2(kappa=2.62) - min with this peak dropped"])
        n130 = float(number_density_cm3(np.array([130.0]))[0]) / N_UNIT
        for k, pk in enumerate(PEAKS):
            w.writerow(["beta_self_post", pk, f"{q_a[I_BETA + k - 1]:.5f}",
                        f"{tensions[pk]:.2f}",
                        f"MHz per 1e12 cm^-3; posterior under the four-point "
                        f"prior {priors[pk][0]:.5f}+/-{priors[pk][1]:.5f} "
                        f"(err column: the tension in prior sigmas)"])
            w.writerow(["gamma_coll_post_130C", pk,
                        f"{q_a[I_BETA + k - 1] * n130:.3f}", "",
                        "MHz; the same posterior expressed as a collisional "
                        "width at 130 C, comparable with M23's row"])
            w.writerow(["reh_rate", pk, f"{np.exp(q_a[I_REHRATE + k - 1]):.5f}", "",
                        "MHz per ms, transition; fitted evening-session scan rate"])
        for b in SL_BLOCKS:
            w.writerow(["sigma_laser_s", b, f"{q_a[I_SL + SL_IX[b] - 1]:.3f}", "",
                        "MHz, transition axis; session-block population mean"])
        for i, (blk, pk) in enumerate(sp_keys):
            val = q_a[NS + i - 1]
            w.writerow(["sigma_laser_sp", f"{blk}_{pk}", f"{val:.3f}",
                        f"{val - q_a[I_SL + SL_IX[blk] - 1]:+.3f}",
                        f"MHz, transition axis; per-(block, peak) sigma_laser "
                        f"under a {SIGMA_SP_PRIOR_MHZ * 1e3:.0f} kHz shrinkage "
                        f"prior toward the {blk} mean (err column: the "
                        f"deviation from it)"])
        w.writerow(["Vsat_agilent", "nuisance", f"{np.exp(q_a[I_VSAT_AG - 1]):.1f}", "",
                    "V; detector saturation, campaign and campaign-morning -- large = linear"])
        w.writerow(["Vsat_lecroy", "nuisance", f"{np.exp(q_a[I_VSAT_LC - 1]):.1f}", "",
                    "V; detector saturation, evening session"])
        _box = ("box = measured M26 value +/- 5 sigma"
                if measured_pilot_scale() else "bounded [0.9, 1.1]")
        w.writerow(["pilot_rate_scale", "nuisance",
                    f"{np.exp(q_a[I_PILSCALE - 1]):.4f}", "",
                    "campaign-morning axis = campaign 4192 bracket rate x this factor, "
                    + _box])
        w.writerow(["n_traces", "camp_p/camp_t/reh/pil",
                    f"{len(camp_p)}/{len(camp_t)}/{len(reh)}/{len(pil)}", "",
                    f"{npts} points; canonical p_sweep / canonical t_sweep / "
                    f"usable evening session ({n_corrupt} files corrupt or lineless) "
                    f"/ campaign-morning sweep. Rulers excluded (addendum 22)"])
        w.writerow(["qc_gate_a1_examined", "count", f"{len(qc_examined)}", "",
                    "canonical RF-off traces carrying a hard QC flag, each "
                    "re-checked on its own fit window: "
                    + ("; ".join(f"{f}: {v}" for f, v in qc_examined)
                       if qc_examined else "none")])
        w.writerow(["qc_gate_a2_dropped", "count", f"{len(qc_dropped)}", "",
                    "condition groups dropped for fewer than 3 admitted "
                    "repeats"])
        w.writerow(["railed_expected", "nuisance", f"{len(rail_expected)}", "",
                    "shared parameters railed where railing is the EXPECTED "
                    "answer rather than a fault (a saturation ceiling means "
                    "the detector ran linear): " + _rail_str(rail_expected)])
        w.writerow(["railed_flagged", "nuisance", f"{len(rail_flagged)}", "",
                    "shared nuisances railed, reported and not stopped: "
                    + _rail_str(rail_flagged)])
        for name, verdict, value, threshold, stop, note in gates:
            w.writerow([name, verdict, f"{value:.6g}", threshold,
                        ("STOP CLASS. " if stop else "") + note])
        for kap, c2, cc, cp in prof_a:
            w.writerow(["profile_point", f"{kap:.2f}", f"{c2:.2f}", f"{cc:.2f}",
                        "chi2 total (value) and campaign-only (err column), "
                        "primary settings"])
        for kap, c2, cc, cp in prof_a:
            w.writerow(["profile_point_pladder", f"{kap:.2f}", f"{cp:.2f}", "",
                        "chi2 of the campaign power-ladder rows alone at the "
                        "same primary settings"])
    print(f"\n  Wrote {path.relative_to(REPO)}.")

    r = subprocess.run([sys.executable, str(REPO / "scripts" /
                                            "annotate_results_status.py")],
                       capture_output=True, text=True)
    print("  " + (r.stdout.strip().splitlines() or ["annotator produced no output"])[-1])
    if r.returncode != 0:
        print(r.stderr.strip())
        return 1

    stops = [g for g in gates if g[4] and g[1] == "FAIL"]
    if stops:
        print("\n  STOP: " + ", ".join(g[0] for g in stops)
              + ". The numbers do not enter a document until this is ruled on.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
