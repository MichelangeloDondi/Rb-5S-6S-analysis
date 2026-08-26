#!/usr/bin/env python3
"""
M23: the joint Stark fit -- every lineshape from every session, one kappa.

THE QUESTION. The AC-Stark programme had three channels and two of them are
dead: the centres are unidentifiable (M21 -- power descends with time inside
every display epoch, so drift and pull are one regression column), and the
third cumulant is ~150x below this dataset's noise at the predicted S0. What
remained was the width-and-shape channel, which M4e used through 20 summary
FWHM numbers. This module uses everything instead: a joint maximum-likelihood
fit of the FULL PROFILES of all canonical power-sweep traces, with a single
shared kappa (S0 = kappa * P, transition axis), per-peak physical widths, and
every trace keeping a free centre -- so laser drift and re-locks are profiled
out exactly rather than modelled.

THE SECOND SESSION. The 2025-07-04 LeCroy 4 July evening session (results
report addendum 9; excluded tree) joins the fit: 46 usable traces of 50
(three are 0xff-corrupted, one has no line), at 90/180/270 mW -- the 270 mW
rung carries 1.44x the campaign's maximum S0^2 lever. Its ladders were run in
ALTERNATING directions (4192 descending, 4207 and 4121 ascending, each ladder
complete inside 6-13 min), which is exactly the design M21 demanded and the
campaign lacked. Two facts blunt what the evening session can say on its own: the
LeCroy auto-triggered, so the triangle phase is random per trace and absolute
positions carry no frequency (repeat centres jump ~0.45 s within 84 s, which
would be 4 MHz/min as drift -- impossible); and its scan is ~4x slower than
the campaign's, so its ms->MHz rate must be fitted per peak, anchored only by
the physical widths it shares with the campaign. The direction of its
frequency axis is a discrete hypothesis and the corrected likelihood is
INDIFFERENT to it (the CSV row quotes the delta); v1 of this fit had decided
it at delta chi2 = 318 under a mis-weighted likelihood, which was wrong.

WHAT THE FIT CONTAINS, and what died on the way in (each kept a CSV row or a
docstring sentence because the wrong version ran first):

  * Per-session noise via the M1 law (condition_noise_model on each 5-repeat
    block, both sessions). v1 gave the evening session a constant per-trace sigma;
    its pull widths then grew 1.0 -> 3.5 with power, which was the noise
    model, not physics.
  * Per-session sigma_laser (different days, no shared laser width) and per
    peak. v1 shared it across sessions and the campaign pull widths exploded
    to 4.4 at 225 mW; v2's flat 0.44-0.69 is what unmasked everything else.
  * gamma_coll per peak under a Gaussian prior from the record's own chain,
    beta_self x N(130 C) (0.55/0.46/0.56/1.01 +/- 0.23/0.23/0.12/0.19 MHz).
    Without the prior the evening session's rate-width degeneracy rails gamma_coll
    at zero, which contradicts the repo's own beta_self measurement.
  * A detector saturation nuisance Vsat per session. Both sessions fit
    essentially LINEAR (tens to hundreds of volts against ~1 V signals) --
    the instrument is vindicated, the row is the receipt.
  * A causal detector tail tau_det was tried and is DEAD: the 2D
    (kappa, tau) profile pays +33 at tau = 2.5 ms and +2200 at 10 ms. The
    campaign's power-dependent residual skew is not a detector time constant.
  * A red-side WING nuisance (standoff 2 MHz, scale 2-60 MHz, amplitude
    free): the one residual structure left is a same-physical-side wing
    excess in BOTH sessions (campaign skew +0.33 falling with P; evening session
    -0.28 under its flipped axis -- the same side of the line). The wing row
    reports how the kappa bound moves when that structure is absorbed; the
    wedge and the wing both live on the red side, so this is the fit's
    hardest robustness test, not a formality.

THE THIRD SESSION (added 2026-08-01, the module's v2). THE CAMPAIGN-MORNING
SESSION OF 17 JULY 2025, directory SESSION_20250717 (this docstring said
2025-07-18 until 2026-08-17 while naming the 20250717 directory in the same
sentence; GLOSSARY.md and DATA.md both say 17 July and are the canonical
naming): 26 traces on peak 4192 alone, powers 35/70/105/210 mW at the
campaign's internal ~130 C (addendum 17 established it ran hot), on the
Agilent in campaign trace format, ~20 minutes after the ruler's final
commissioning. Its axis borrows the campaign 4192 bracket rate through a
rate-scale nuisance bounded to +/-10% -- licensed by the raw widths: the
campaign-morning 210 mW line is 60.8 +/- 0.4 ms against the campaign 225 mW line's
62.6 +/- 0.3, ratio 0.971, which equal rates and near-equal physics
predict. Its ladder ran 210 -> 35 -> 70 -> 105, non-monotone in time --
the ordering M21 asked for -- but its CENTRES still stay out of the fit:
the recorded window starts step with the power changes, in the same
direction and at the same scale as the expected pull (-478 ms at 210 mW,
-464 at 35, -468 at 70/105), which is M21's response-versus-relabel
ambiguity in miniature. Shape and width only, like everything else here.
THE PIEZO-RAMP CHANNEL of the 2025-07-03 EOM traces, and what
it settles (an earlier version of this note dismissed it as a near-DC
monitor; prior notes said piezo ramp, and the data agree).
The signal channel's two equal peaks are the SAME line crossed twice near
a sweep turnaround, and the ramp channel proves it: at the two crossings
it reads equal to 0.04-0.12 mV on a 13 mV in-window sweep, forty times
tighter than a monotone ramp would allow. That validated axis then gets a
calibration from a ~2% satellite sitting at a CONSTANT ramp-voltage offset
from the line (+2.29 and +2.48 mV in the two traces that show it): read as
the 12.5 MHz EOM tooth it gives 5.24 MHz/mV, under which the line's
0.98 +/- 0.03 mV width is 5.1 MHz at 80 C -- on the physical budget --
while the 25 MHz reading gives an unphysical 10.3. The EOM-day scan rate
at the crossings is therefore MEASURED: 4.5 mV/s x 5.24 = 0.024 MHz/ms
(transition). That is 2.2x the evening session's width-fitted 0.0107, so the
07-03 and 07-04 scan configurations genuinely differ and no rate
transfers: the evening session's anchor stays width-tied as a measured
conclusion, not an assumption. No usable in-trace ruler exists for the
evening session itself.

THE PRIORS MOVED AT v3.0.0 (2026-08-01), which is why the numbers in this
docstring's history differ from the CSV. w0 went 50 -> 64 um (accepted from
the Nieddu/Rajasree lineage measurement on the same laser model, lens and
geometry) and the retro ratio went from an asserted 1 to an assumed
0.94 +/- 0.04. The predicted coefficient therefore moved 2.62 -> 1.55 MHz/W
and is now COMPUTED from the constants (KAPPA_PRED) rather than typed into
the grid; 2.62 is kept as a legacy checkpoint so older profiles stay
comparable. The bound itself also moves a little, because the transit width
that enters this fit's lineshape rides on w0.

SIGMA GRANULARITY, verified 2026-08-02 against the measured-prior re-run's
requirement. `build()`/`make_resid()` already carry sigma_laser per PEAK,
separately for the campaign+morning session (`p[7+k]`, indices 7-10) and the
evening session (`p[11+k]`, indices 11-14) -- 8 parameters, no coarser
pooling above the peak axis to shrink from. The morning traces reuse the
campaign's peak-4192 slot rather than getting a dedicated one, which is not
a pooling gap: the morning session only ever touches peak 4192, so there is nothing
else its own slot could resolve, and sharing it with the campaign's
best-measured peak is a data-availability choice, not an averaging-away of
# term-of-art: the private reviews directory is a filesystem path
distinct physics. private/reviews/digest/fig16_residual_asymmetry.md
("Seventh addition", Granularity recommendation) reads this same code and
reaches the same conclusion: "M23's peak-resolved choice is closer to what
T=130 supports" and names it the baseline the M25 re-run should match. No
change made here; M25 (`run_global_dataset_fit.py`, `_m25_norulers.py`) is
the one that needed the upgrade, since it pools sigma_laser across all four
peaks per campaign temperature block -- see its own docstring's SIGMA
GRANULARITY UPGRADE section for the hierarchical-shrinkage fix applied
there. No transit-tail or periodic term is added to this module either;
both were tested elsewhere in the same digest and excluded (wrong sign /
too small, and unsupported for a different module respectively).

CONVERGENCE DISCIPLINE, learned twice: scipy's free fits on this problem
land thousands of chi2 above their own profiles. Nothing from a free fit is
quoted; every number comes from warm-chained BIDIRECTIONAL kappa profiles
(left-to-right, then right-to-left from the far seed, pointwise minimum) at
ftol = xtol = 1e-12.

RUNTIME: ~5 h single process (three sessions, 172 traces) (the profile builder runs at dnu_floor = 2e-2,
see _shared_profile_grid -- equivalence tested). The excluded 2025-07-04
tree must be present for the evening-session arm; without it this module prints
what is missing and exits 0, and the committed CSV remains the record
(build_clock_table pattern). Raw traces never enter the repository.
RB5S6S_SESSION_20250704_DIR and RB5S6S_SESSION_20250717_DIR are needed only to re-run this
script against those private working copies, and the committed CSVs are what
the repository ships.

Writes results/stark_joint.csv. Reads results/beta_self.csv (run M4 first)
and the M2 bracket rates.
"""

from __future__ import annotations

import csv
import datetime
import glob
import os
import re
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
from run_beta_self import load_t_rates  # noqa: E402

SESSION_20250704 = Path(os.environ.get(
    "RB5S6S_SESSION_20250704_DIR", "~/rb-2025-sessions/prehistory")).expanduser()
PEAKS = ("4121", "4154", "4192", "4207")
PK_IX = {p: i for i, p in enumerate(PEAKS)}
TRANSIT = transit_fwhm_at_T(130.0, C.TRANSIT_FWHM_PLACEHOLDER_MHZ)
DNU_FLOOR = 2e-2          # see _shared_profile_grid's docstring
NU0_WING = 2.0            # MHz standoff of the wing nuisance
KAPPA_PRED = stark_shift_S0_mhz(1.0, C.W0_MEASURED_M, rho=C.RHO_RETRO)
"""The predicted coefficient, COMPUTED from the constants rather than typed.
It moved 2.62 -> 1.55 MHz/W at v3.0.0 when the priors became w0 = 64 um and
rho = 0.94; the grid below keeps 2.62 as a legacy checkpoint so the older
profiles stay comparable."""
KAPPAS = tuple(sorted({0.0, 0.25, 0.5, 0.75, 1.0, round(KAPPA_PRED, 3),
                       1.5, 2.0, 2.62, 3.5, 5.0}))
KAPPAS_LOPO = tuple(sorted({0.0, 0.25, 1.0, round(KAPPA_PRED, 3), 2.0, 2.62}))
NS = 20                   # kappa, 2 Vsat, 4 gc, 8 sl, 4 evening-session rates, 1 campaign-morning rate-scale
SESSION_20250717 = Path(os.environ.get(
    "RB5S6S_SESSION_20250717_DIR", "~/rb-2025-sessions/pilot")).expanduser() / "4192nm91c650ma"


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------

def gc_priors() -> dict:
    """gamma_coll(130 C) per peak from the repo's own beta_self x N chain."""
    n130 = float(number_density_cm3(np.array([130.0]))[0]) / 1e12
    out = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "beta_self.csv")):
        out[r["peak"]] = (float(r["beta_self"]) * n130,
                          float(r["beta_self_err"]) * n130)
    return out


def load_campaign():
    rows = load_manifest()
    _, prates = load_t_rates()
    out = []
    for peak in PEAKS:
        rate, _ = prates[peak]
        byP = defaultdict(list)
        for r in rows:
            if (r["flag"] == "canonical" and r["role"] == "p_sweep"
                    and r["peak"] == peak):
                byP[r["power_mW"]].append(r)
        for P, recs in sorted(byP.items(), key=lambda kv: int(kv[0])):
            if len(recs) < 3:
                continue
            volts = [load_trace(trace_path(r))[1] for r in recs]
            law = condition_noise_model(volts)
            tau = max(law.get("tau_int", 1.0), 1.0)
            for r in recs:
                t, v = load_trace(trace_path(r))
                nu = to_frequency(t, rate)
                lev, base = signal_level(v)
                c0 = float(nu[int(np.argmax(lev))])
                sg = sigma_of_v(np.maximum(lev, 0.0), law) * np.sqrt(tau)
                m = np.abs(nu - c0) <= adaptive_halfwidth(nu, v)
                out.append(dict(sess="camp", peak=peak, P=int(P) / 1e3,
                                x=nu[m], v=v[m], sg=sg[m],
                                c0=c0, A0=float(lev.max()), b0=float(base)))
    return out


def load_session_20250704():
    """Reduce the LeCroy evening session in place: header TrigTime, 50 ms boxcar
    segmentation, window +/-1.6 FWHM, 0.5 ms sampling. Never writes."""
    files = sorted(glob.glob(str(SESSION_20250704 / "2025-07-04" / "C2L=*.csv")))
    out, n_corrupt = [], 0
    raw_traces = {}
    for f in files:
        m = re.search(r"993\.(\d{4})nm.*P=(\d+)mW_n(\d+)", f)
        try:
            head = open(f, "rb").read(400).decode("utf-8")
            tm = re.search(r"#1,(\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2})", head)
            trig = datetime.datetime.strptime(
                tm.group(1), "%d-%b-%Y %H:%M:%S").timestamp()
            d = np.genfromtxt(f, delimiter=",", skip_header=5)
        except Exception:
            n_corrupt += 1
            continue
        t, v = d[:, 0], d[:, 1]
        k = 5001
        sm = np.convolve(v, np.ones(k) / k, "same")
        base = np.median(np.sort(sm)[:len(sm) // 5])
        pk = sm.max()
        above = sm > base + 0.5 * (pk - base)
        edges = np.flatnonzero(np.diff(above.astype(int)))
        segs = [(edges[i], edges[i + 1]) for i in range(0, len(edges) - 1, 2)
                if t[edges[i + 1]] - t[edges[i]] > 0.05]
        if not segs:
            n_corrupt += 1
            continue
        a, b = max(segs, key=lambda s: s[1] - s[0])
        w = t[b] - t[a]
        cmid = (t[a] + t[b]) / 2
        msk = (t > cmid - 1.6 * w) & (t < cmid + 1.6 * w)
        td, vd = t[msk][::50] * 1e3, v[msk][::50]        # ms, 0.5 ms sampling
        out.append(dict(sess="reh", peak=m.group(1), P=int(m.group(2)) / 1e3,
                        x=td, v=vd, sg=None, trig=trig,
                        c0=float(cmid * 1e3), A0=float(pk - base), b0=0.0))
        raw_traces.setdefault((m.group(1), m.group(2)), []).append(out[-1])
    for grp in raw_traces.values():
        law = condition_noise_model([t["v"] for t in grp])
        tau = max(law.get("tau_int", 1.0), 1.0)
        for t in grp:
            lev = t["v"] - np.median(np.sort(t["v"])[:max(len(t["v"]) // 5, 8)])
            t["sg"] = sigma_of_v(np.maximum(lev, 0.0), law) * np.sqrt(tau)
    return out, n_corrupt


def load_session_20250717(rate_4192):
    """The 2025-07-18 campaign-morning session: 26 traces, peak 4192 only, powers
    35/70/105/210 mW at the campaign's internal ~130 C (addendum 17), on the
    Agilent in campaign format, ~20 min after the ruler's final
    commissioning. Its frequency axis is the campaign 4192 bracket rate
    times a free scale bounded to +/-10% (the raw 210 mW width matches the
    campaign 225 mW width to 2.9%, so the scale is a nuisance, not a leap).
    Its ladder ran 210 -> 35 -> 70 -> 105, non-monotone in time -- but its
    centres stay OUT of the fit: the recorded window starts move with the
    power steps in the same direction and size as the expected pull, which
    is exactly M21's response-versus-relabel ambiguity. Shape and width
    only, like every other trace here. NaN rows in the raw files (the
    header-variant quirk) are masked."""
    files = sorted(glob.glob(str(SESSION_20250717 / "*mw*.csv")))
    out = []
    bycond = {}
    for f in files:
        m = re.search(r"(\d{3})mw(\d+)\.csv", f)
        d = np.genfromtxt(f, delimiter=",", skip_header=2)
        msk = np.isfinite(d[:, 0]) & np.isfinite(d[:, 1])
        t_ms, v = d[msk, 0] * 1e3, d[msk, 1]
        nu = t_ms * rate_4192
        lev, base = signal_level(v)
        c0 = float(nu[int(np.argmax(lev))])
        hw = adaptive_halfwidth(nu, v)
        w = np.abs(nu - c0) <= hw
        out.append(dict(sess="pil", peak="4192", P=int(m.group(1)) / 1e3,
                        x=nu[w], v=v[w], sg=None,
                        c0=c0, A0=float(lev.max()), b0=float(base)))
        bycond.setdefault(m.group(1), []).append(out[-1])
    for grp in bycond.values():
        law = condition_noise_model([t["v"] for t in grp])
        tau = max(law.get("tau_int", 1.0), 1.0)
        for t in grp:
            lev = t["v"] - np.median(np.sort(t["v"])[:max(len(t["v"]) // 5, 8)])
            t["sg"] = np.maximum(
                sigma_of_v(np.maximum(lev, 0.0), law), 1e-6) * np.sqrt(tau)
    return out


# ---------------------------------------------------------------------------
# the model
# ---------------------------------------------------------------------------

def build(traces, priors, wing):
    r0 = np.log(5.9 / 470.0)
    ns_tot = NS + (2 if wing else 0)
    p0 = np.zeros(ns_tot + 4 * len(traces))
    lo = np.full_like(p0, -np.inf)
    hi = np.full_like(p0, np.inf)
    p0[0] = 0.0; lo[0] = 0.0; hi[0] = 60.0
    for j in (1, 2):
        p0[j] = 5.0; lo[j] = -1.0; hi[j] = 6.0
    for k, pk in enumerate(PEAKS):
        p0[3 + k] = priors[pk][0]; lo[3 + k] = 0.0; hi[3 + k] = 50.0
        p0[7 + k] = 1.0; lo[7 + k] = 0.05; hi[7 + k] = 50.0
        p0[11 + k] = 1.0; lo[11 + k] = 0.05; hi[11 + k] = 50.0
        p0[15 + k] = r0; lo[15 + k] = r0 - np.log(4); hi[15 + k] = r0 + np.log(4)
    _mps = measured_pilot_scale()
    if _mps is not None:
        _m, _e = _mps
        p0[19] = np.log(_m)
        lo[19] = np.log(_m - 5 * _e); hi[19] = np.log(_m + 5 * _e)
    else:
        p0[19] = 0.0; lo[19] = np.log(0.9); hi[19] = np.log(1.1)   # campaign-morning rate scale
    if wing:
        p0[NS] = 0.005; lo[NS] = 0.0; hi[NS] = 0.5
        p0[NS + 1] = np.log(6.0); lo[NS + 1] = np.log(2.0); hi[NS + 1] = np.log(60.0)
    for i, t in enumerate(traces):
        j = ns_tot + 4 * i
        p0[j:j + 4] = [t["A0"], t["c0"], t["b0"], 0.0]
        lo[j] = 0.0
        span = 8.0 if t["sess"] == "camp" else 1200.0
        lo[j + 1] = t["c0"] - span; hi[j + 1] = t["c0"] + span
    return p0, lo, hi


def make_resid(traces, priors, direction, wing):
    ns_tot = NS + (2 if wing else 0)

    def resid(p, kappa=None):
        kap = p[0] if kappa is None else kappa
        f_w = p[NS] if wing else 0.0
        w_w = np.exp(p[NS + 1]) if wing else 1.0
        cache = {}
        out = []
        for i, t in enumerate(traces):
            k = PK_IX[t["peak"]]
            gc = p[3 + k]
            s0 = kap * t["P"]
            sess = t["sess"]
            sl = p[11 + k] if sess == "reh" else p[7 + k]
            key = (sess == "reh", k, round(sl, 7), round(gc, 7), round(s0, 8),
                   round(f_w, 7), round(w_w, 5))
            if key not in cache:
                g, prof = _shared_profile_grid(gc, sl, TRANSIT, s0, "gaussian",
                                               dnu_floor=DNU_FLOOR)
                if f_w > 0:
                    msk = g < -NU0_WING
                    prof = prof.copy()
                    prof[msk] += (f_w * prof.max()
                                  * np.exp(-(np.abs(g[msk]) - NU0_WING) / w_w))
                if sess == "reh" and direction < 0:
                    prof = prof[::-1]
                cache[key] = (g, prof)
            g, prof = cache[key]
            A, cc, b0, b1 = p[ns_tot + 4 * i: ns_tot + 4 * i + 4]
            if sess == "camp":
                lin = A * np.interp(t["x"] - cc, g, prof, left=0., right=0.)
                Vs = np.exp(p[1])
            elif sess == "pil":
                scale = np.exp(p[19])
                lin = A * np.interp(scale * t["x"] - cc, g, prof, left=0., right=0.)
                Vs = np.exp(p[1])
            else:
                rate = np.exp(p[15 + k])
                lin = A * np.interp(rate * (t["x"] - cc), g, prof, left=0., right=0.)
                Vs = np.exp(p[2])
            mdl = Vs * (1.0 - np.exp(-lin / Vs)) + b0 + b1 * t["x"]
            out.append((t["v"] - mdl) / t["sg"])
        out.append(np.array([(p[3 + k] - priors[pk][0]) / priors[pk][1]
                             for k, pk in enumerate(PEAKS)]))
        return np.concatenate(out)
    return resid


def sparsity(traces, wing):
    ns_tot = NS + (2 if wing else 0)
    n_rows = sum(len(t["x"]) for t in traces)
    S = lil_matrix((n_rows, ns_tot + 4 * len(traces)), dtype=int)
    r0 = 0
    for i, t in enumerate(traces):
        n = len(t["x"]); k = PK_IX[t["peak"]]
        S[r0:r0 + n, 0] = 1
        S[r0:r0 + n, 3 + k] = 1
        if wing:
            S[r0:r0 + n, NS] = 1; S[r0:r0 + n, NS + 1] = 1
        if t["sess"] == "camp":
            S[r0:r0 + n, 1] = 1; S[r0:r0 + n, 7 + k] = 1
        elif t["sess"] == "pil":
            S[r0:r0 + n, 1] = 1; S[r0:r0 + n, 7 + k] = 1; S[r0:r0 + n, 19] = 1
        else:
            S[r0:r0 + n, 2] = 1; S[r0:r0 + n, 11 + k] = 1; S[r0:r0 + n, 15 + k] = 1
        S[r0:r0 + n, ns_tot + 4 * i: ns_tot + 4 * i + 4] = 1
        r0 += n
    pri = lil_matrix((4, S.shape[1]), dtype=int)
    for k in range(4):
        pri[k, 3 + k] = 1
    return vstack([S.tocsr(), pri.tocsr()]).tocsr()


# ---------------------------------------------------------------------------
# profiles
# ---------------------------------------------------------------------------

def chain(resid, Sf, lo, hi, q0, kappas, ncamp, tag, nfev=1500):
    res, q = {}, q0.copy()
    for kap in kappas:
        fn = lambda z: resid(np.concatenate([[0.0], z]), kappa=kap)
        s = least_squares(fn, q, bounds=(lo[1:], hi[1:]), jac_sparsity=Sf,
                          max_nfev=nfev, x_scale="jac", ftol=1e-12, xtol=1e-12)
        q = s.x.copy()
        r = fn(q)
        res[kap] = (float(np.sum(r * r)), float(np.sum(r[:ncamp] ** 2)), q.copy())
        print(f"    [{tag}] kappa={kap:5.2f}  chi2={np.sum(r * r):11.2f}", flush=True)
    return res




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
    path = REPO / "results" / "morning_ruler.csv"
    if not path.exists():
        return None
    for r in _csv.DictReader(open(path)):
        if r["quantity"] == "pilot_rate_scale_measured":
            return float(r["value"]), float(r["err"])
    return None


def bidi_profile(traces, priors, direction, wing, tag, seed=None):
    """seed (2026-08-02): a converged parameter vector from another variant.

    The direction check flips only the evening-session x axis, but a cold start on
    the flipped axis can park the 46 evening-session centres in the wrong local minimum and
    stay there for the WHOLE chain, forward and backward: the 2026-08-02 run
    left the dir +1 priors variant 17,779 chi2 above the dir -1 primary at
    every kappa, while the wing variant of the same direction found the true
    local minimum (chi2 189,580) -- so the gap was warm-up, not physics. Seeding each
    direction variant from its converged opposite-direction twin removes the
    failure mode; the seeded chain is run IN ADDITION to the cold one and the
    pointwise minimum is kept, so a seed can only improve the profile."""
    p0, lo, hi = build(traces, priors, wing)
    resid = make_resid(traces, priors, direction, wing)
    Sf = sparsity(traces, wing)[:, 1:]
    ncamp = sum(len(t["x"]) for t in traces if t["sess"] == "camp")
    fwd = chain(resid, Sf, lo, hi, p0[1:], KAPPAS, ncamp, tag + ">")
    bwd = chain(resid, Sf, lo, hi, fwd[KAPPAS[-1]][2], KAPPAS[::-1], ncamp, tag + "<")
    chains = [fwd, bwd]
    if seed is not None:
        chains.append(chain(resid, Sf, lo, hi, seed, KAPPAS, ncamp, tag + "s"))
    prof, best = [], (np.inf, None, None)
    for kap in KAPPAS:
        pick = min((c[kap] for c in chains), key=lambda r: r[0])
        prof.append((kap, pick[0], pick[1]))
        if pick[0] < best[0]:
            best = (pick[0], kap, pick[2])
    return np.array(prof), best[1], best[2]


def ub95(arr, col=1):
    k, c = arr[:, 0], arr[:, col] - arr[:, col].min()
    i = int(np.argmin(arr[:, col]))
    above = np.where((k > k[i]) & (c > 2.706))[0]
    if not len(above):
        return float("nan")
    j = above[0]
    return float(np.interp(2.706, [c[j - 1], c[j]], [k[j - 1], k[j]]))


# ---------------------------------------------------------------------------

def strip_wing(q):
    """A wing-family solution vector, re-cut for the no-wing layout.

    The two shared wing entries sit at q indices NS-1 and NS (q excludes
    kappa). Everything else -- session widths, per-peak physics, rates,
    per-trace blocks -- transplants one to one."""
    return np.delete(q, [NS - 1, NS])


CAMPONLY = "--camponly" in sys.argv
"""Fit the MAIN CAMPAIGN ALONE, opt-in, writing nothing into results/.

WHY THIS EXISTS. The owner asked on 2026-08-17 whether the two pre-campaign
sessions are safe to pool, since they were early attempts exploited afterwards.
The record could not answer: `kappa_ub95_camponly` reads the campaign's chi2
along the JOINT profile, with nuisances fitted on all three sessions, so it is
not the campaign-alone bound its name suggests.

WHAT IT CHANGES. One thing. The residual is built from campaign traces only.
The parameter vector is UNCHANGED, so the dropped sessions' nuisances stay in it
and sit at their seeds, contributing nothing. That is safe here because ub95()
uses an UNSCALED 2.706 threshold, so no chi2_red bookkeeping enters the bound,
and it is informative: a vector that converges while carrying those parameters
proves the parameter COUNT is not what breaks the pooled fit.

WHAT IT MAY NOT DO. Write results/stark_joint.csv. The committed file is the
pooled record and this variant is a different construction, so the write is
guarded below rather than left to discipline.
"""


# The two session trees and the pattern each must actually match. A
# directory that EXISTS and is EMPTY is what a half-finished copy or a failed
# sync leaves behind, and it passes an is_dir() check while contributing zero
# traces to a fit that would then run for hours and write a headline bound
# from one session instead of three. The directory test below was already
# right about absence; this pair makes it right about emptiness too.
_REQUIRED_SESSIONS = (
    ("RB5S6S_SESSION_20250704_DIR", SESSION_20250704,
     SESSION_20250704 / "2025-07-04" / "C2L=*.csv"),
    ("RB5S6S_SESSION_20250717_DIR", SESSION_20250717,
     SESSION_20250717 / "*mw*.csv"),
)


def main() -> int:
    if not (SESSION_20250704.is_dir() and SESSION_20250717.is_dir()):
        print(f"excluded tree(s) not on this machine "
              f"({SESSION_20250704}, {SESSION_20250717}) -- the committed "
              f"results/stark_joint.csv is the record; nothing to do.")
        return 0
    for env_var, root, pattern in _REQUIRED_SESSIONS:
        if not glob.glob(str(pattern)):
            print(f"REFUSING TO RUN: {root} exists but holds no file matching "
                  f"{pattern.name}. This fit reads three sessions and would "
                  f"otherwise proceed on the two it can see, writing a "
                  f"headline bound built from less data than the committed "
                  f"one. Point {env_var} at the real tree, or leave the "
                  f"committed results/stark_joint.csv as the record.")
            return 1
    priors = gc_priors()
    camp = load_campaign()
    reh, n_corrupt = load_session_20250704()
    _, prates = load_t_rates()
    pil = load_session_20250717(prates["4192"][0])
    traces = camp if CAMPONLY else camp + reh + pil
    if CAMPONLY:
        print(f"  --camponly: {len(reh)} evening and {len(pil)} "
              f"campaign-morning traces LOADED and EXCLUDED. Every number "
              f"below is campaign-only and NOTHING is written to results/.")
    npts = sum(len(t["x"]) for t in traces)
    if CAMPONLY:
        print(f"(M23) CAMPAIGN-ONLY STARK FIT: {len(traces)} campaign traces "
              f"fitted, {npts} points. The {len(reh)} evening "
              f"({n_corrupt} unusable) and {len(pil)} campaign-morning traces "
              f"were loaded and are NOT in the residual.")
    else:
        print(f"(M23) JOINT THREE-SESSION STARK FIT: {len(camp)} campaign + "
              f"{len(reh)} evening-session ({n_corrupt} files unusable) + "
              f"{len(pil)} campaign-morning traces, {npts} points")

    # Chain order (2026-08-03): the wing variant goes FIRST because a cold
    # start finds the true local minimum reliably there, and every other family is
    # seeded from its solution (in addition to its own cold chains; the
    # pointwise minimum keeps whichever wins). The 2026-08-03 four-point run
    # demonstrated the warm-up failure mode striking the PRIMARY variant:
    # its cold chains parked 283k above the local minimum every seeded and wing
    # chain found, and the direction row then compared a stuck profile
    # against a converged one. Seeding the primary from the wing solution
    # (wing entries stripped) closes that mode for every family at once.
    t0 = time.time()
    print("  wing robustness (dir -1, cold; the minimum search):")
    prof_c, kmin_c, q_c = bidi_profile(traces, priors, -1, True, "C-")
    print("  primary profile (priors, evening-session dir -1, seeded from C-):")
    prof_a, kmin_a, q_a = bidi_profile(traces, priors, -1, False, "A-",
                                       seed=strip_wing(q_c))
    print("  direction check (dir +1, seeded from the dir -1 solution):")
    prof_b, kmin_b, _ = bidi_profile(traces, priors, +1, False, "A+", seed=q_a)
    print("  wing robustness (dir +1, seeded):")
    prof_d, kmin_d, _ = bidi_profile(traces, priors, +1, True, "C+", seed=q_c)

    ka, kc = ub95(prof_a), ub95(prof_c)
    ka_camp = ub95(prof_a, col=2)
    dchi2_a = float(prof_a[0, 1] - prof_a[:, 1].min())
    dir_delta = float(np.abs(prof_a[:, 1] - prof_b[:, 1]).max())

    # LOPO at the primary settings, seeded from the full solution. Peak 4192
    # gets the FULL kappa grid rather than the short one, because dropping it
    # removes the entire campaign-morning session -- so that subset deserves a real
    # profile bound, which the ledger used to hand-type as "0.34".
    lopo, lopo_prof = {}, {}
    for drop in PEAKS:
        keep = [i for i, t in enumerate(traces) if t["peak"] != drop]
        sub = [traces[i] for i in keep]
        p0s, los, his = build(sub, priors, False)
        qs = p0s[1:].copy()
        qs[:NS - 1] = q_a[:NS - 1]
        for j, i in enumerate(keep):
            qs[NS - 1 + 4 * j: NS - 1 + 4 * j + 4] = q_a[NS - 1 + 4 * i: NS - 1 + 4 * i + 4]
        rs = make_resid(sub, priors, -1, False)
        Sfs = sparsity(sub, False)[:, 1:]
        ncs = sum(len(t["x"]) for t in sub if t["sess"] == "camp")
        grid = KAPPAS if drop == "4192" else KAPPAS_LOPO
        res = chain(rs, Sfs, los, his, qs, grid, ncs, f"L{drop}", nfev=900)
        cs = {k: v[0] for k, v in res.items()}
        mn = min(cs.values())
        lopo[drop] = {k: cs[k] - mn for k in cs}
        lopo_prof[drop] = np.array([[k, cs[k], cs[k]] for k in sorted(cs)])
        print(f"  LOPO {drop}: "
              + "  ".join(f"k={k}:{lopo[drop][k]:+.2f}" for k in sorted(cs)))

    ka_d4192 = ub95(lopo_prof["4192"])

    print(f"\n  primary: min kappa = {kmin_a}, dchi2(kappa=0) = {dchi2_a:.2f}")
    print(f"  **95% UB kappa < {ka:.2f} MHz/W -> S0(225 mW) < {ka*0.225:.3f} MHz**")
    print(f"  campaign-only UB: kappa < {ka_camp:.2f} -> S0(225) < {ka_camp*0.225:.3f}")
    print(f"  wing-marginalized: min {kmin_c}, UB kappa < {kc:.2f}"
          f" -> S0(225) < {kc*0.225:.3f}")
    print(f"  direction indifference: max |dchi2| between dirs = {dir_delta:.2f}")
    print(f"  ({(time.time()-t0)/60:.0f} min)")

    _out = (C.RESULTS_DIR / "stark_joint.csv" if not CAMPONLY else
            Path(__file__).resolve().parents[1] / "private" / "run_logs"
            / "stark_camponly.csv")
    if CAMPONLY:
        _out.parent.mkdir(parents=True, exist_ok=True)
    assert not (CAMPONLY and _out.name == "stark_joint.csv"), \
        "--camponly must never write the pooled record"
    with open(_out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["quantity", "key", "value", "err", "unit"])
        w.writerow(["kappa_min", "primary", f"{kmin_a:.2f}", "",
                    "MHz per W; profile minimum, priors, dir -1; NOT a "
                    "detection (see dchi2_kappa0)"])
        w.writerow(["dchi2_kappa0", "primary", f"{dchi2_a:.2f}", "",
                    "chi2(kappa=0) - chi2(min); the strength of the kappa>0 "
                    "preference"])
        w.writerow(["kappa_ub95", "primary", f"{ka:.3f}", "",
                    "MHz per W; 95% one-sided profile-likelihood bound -- "
                    "THE quoted construction (negative kappa is flat by "
                    "construction: the ramp model only broadens red)"])
        w.writerow(["S0_225mW_ub95", "primary", f"{ka*0.225:.3f}", "",
                    "MHz, transition axis; joint three-session bound at the "                    "campaign's maximum power"])
        w.writerow(["S0_270mW_ub95", "primary", f"{ka*0.270:.3f}", "",
                    "MHz; at the evening session's maximum power"])
        w.writerow(["kappa_pred", "prediction", f"{KAPPA_PRED:.3f}", "",
                    f"MHz per W; the PREDICTED coefficient at the current "
                    f"priors (w0 = {C.W0_MEASURED_M*1e6:.0f} um, rho = "
                    f"{C.RHO_RETRO}), computed from constants -- what the "
                    f"bound is compared against"])
        w.writerow(["S0_225mW_pred", "prediction",
                    f"{KAPPA_PRED * 0.225:.3f}", "",
                    "MHz, transition axis; the prediction at 225 mW"])
        w.writerow(["kappa_ub95_drop4192", "robustness", f"{ka_d4192:.3f}", "",
                    "MHz per W; 95% bound with peak 4192 dropped, which "
                    "removes the ENTIRE campaign-morning session -- the most "
                    "conservative subset"])
        w.writerow(["S0_225mW_ub95_drop4192", "robustness",
                    f"{ka_d4192 * 0.225:.3f}", "",
                    "MHz; the drop-4192 bound at 225 mW"])
        w.writerow(["kappa_ub95_camponly", "robustness", f"{ka_camp:.3f}", "",
                    "MHz per W; campaign rows of the same profile -- the "
                    "bound does not lean on the evening session's soft rate anchor"])
        w.writerow(["kappa_min_wing", "robustness", f"{kmin_c:.2f}", "",
                    "MHz per W; minimum with the red-wing nuisance free"])
        w.writerow(["kappa_ub95_wing", "robustness", f"{kc:.3f}", "",
                    "MHz per W; bound with the wing marginalized -- quote "
                    "alongside the primary, the gap IS the wing systematic"])
        w.writerow(["direction_dchi2_max", "robustness", f"{dir_delta:.2f}", "",
                    "max |chi2 difference| between evening-session axis directions "
                    "across the profile; small = indifferent"])
        for pk in PEAKS:
            w.writerow(["lopo_dchi2_pred", pk,
                        f"{lopo[pk][round(KAPPA_PRED, 3)]:+.2f}", "",
                        "chi2(kappa_pred) - min with this peak dropped; all "
                        "positive and similar = no single peak drives it"])
            w.writerow(["lopo_dchi2_262", pk, f"{lopo[pk][2.62]:+.2f}", "",
                        "chi2(kappa=2.62)-min with this peak dropped; all "
                        "positive and similar = no single peak drives it"])
        for k, pk in enumerate(PEAKS):
            w.writerow(["gamma_coll_post", pk, f"{q_a[2 + k]:.3f}", "",
                        f"MHz; posterior under the beta_self prior "
                        f"{priors[pk][0]:.3f}+/-{priors[pk][1]:.3f}"])
            w.writerow(["reh_rate", pk, f"{np.exp(q_a[14 + k]):.5f}", "",
                        "MHz per ms, transition; fitted evening-session scan rate"])
        w.writerow(["Vsat_camp", "nuisance", f"{np.exp(q_a[0]):.1f}", "",
                    "V; detector saturation, campaign -- large = linear"])
        w.writerow(["Vsat_reh", "nuisance", f"{np.exp(q_a[1]):.1f}", "",
                    "V; detector saturation, evening session"])
        w.writerow(["n_traces", "camp/reh/pil", f"{len(camp)}/{len(reh)}/{len(pil)}", "",
                    f"canonical p_sweep / usable evening session ({n_corrupt} files "
                    f"corrupt or lineless) / campaign-morning sweep"])
        _box = ("box = measured M26 value +/- 5 sigma"
                if measured_pilot_scale() else "bounded [0.9, 1.1]")
        w.writerow(["pilot_rate_scale", "nuisance", f"{np.exp(q_a[18]):.4f}", "",
                    "campaign-morning axis = campaign 4192 bracket rate x this factor, "
                    + _box + "; the raw 210 vs 225 mW width ratio "
                    "0.971 justified the tight band"])
        for kap, c2, cc in prof_a:
            w.writerow(["profile_point", f"{kap:.2f}", f"{c2:.2f}", f"{cc:.2f}",
                        "chi2 total (value) and campaign-only (err column), "
                        "primary settings"])
    print(f"\n  Wrote {_out}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
