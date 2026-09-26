#!/usr/bin/env python3
"""The ultra-joint fit as a profile over the beam waist, on every RF-off trace
the record holds, built to the fit design of 2026-09-14 and its extension.

THE QUESTION IS NOT THE WAIST BUT WHICH TERM HAS THE WRONG FORM. Under the
model every earlier construction shared, the archive carries two waist channels
that disagree: the line shape puts the waist at 42 to 44 um and the power arm's
flatness of the width against P^2 puts it above 49 to 80 um. A genuinely
smaller beam brings its own w0^-4 saturation signature with it and the power
arm refuses that signature. So this producer fits BOTH arms under each
candidate laser-kernel form and reports, per form, the shape channel's minimum
or bound beside the power-arm check the same fit must satisfy, per session and
pooled.

THE ANSWER IS THE PARAMETER, SO IT IS SCANNED AND NEVER FITTED (A45, A52).
w0 runs over a grid, 40 to 90 um in steps of 2, and at every point everything
else is refit from two starts. A rail is then a bound read off the profile and
never a Hessian at a wall, which is what every earlier round quoted.

THE SESSIONS. P and T are the manifest's canonical RF-off traces, the 130 C
power sweep and the 70/90/110 C sweep at 225 mW (a blank manifest power is
that arm at 225 mW, docs/DATA.md, and reading it as zero switched the shift
and the saturation off for the whole arm in the pilots). `--all-sessions`
adds E, the 2025-07-04 LeCroy evening (46 usable traces, four peaks at
90/180/270 mW, internal 130 C, gain 1e6), and M, the 2025-07-17 campaign
morning (26 traces, 4192 at 35 to 210 mW), through run_stark_joint.py's own
loaders, read in place from the two trees named by RB5S6S_SESSION_20250704_DIR
and RB5S6S_SESSION_20250717_DIR, with its skip-when-absent behaviour: a
missing tree prints what is missing and exits 0. The evening's ms axis has no
ruler, so its rate per peak is a nuisance parameter seeded at the committed
fitted rates of results/stark_joint.csv and bounded to +-25 per cent; the
morning's axis is the campaign 4192 bracket rate times the measured pilot
scale of results/morning_ruler.csv. Neither session has a row in
results/noise_model.csv, so each condition's a^2 + bV law and tau_int are
fitted from its own wing samples with rb5s6s.noise.condition_noise_model, the
estimator the noise producer uses, and written as rows. `--with-excluded`
adds Q, the manifest's excluded 130 C 4154 attempt, as a diagnostic arm that
is never the headline.

WHAT IS FREE AT EACH GRID POINT, and what is pinned, and why:

  beta_self     profiled, one coefficient over every temperature, reported
                AGAINST the theory cell of results/beta_self_theory.csv (read, never typed)
                (vanderwaals.beta_self_anchored for the centre,
                beta_self_budget for the bar, which is the whole measured
                budget and not the anchor measurement's share of it) and
                never multiplied by it,
                and PROFILED at every waist: chi2 at beta fixed to zero, to
                theory, to five and to twenty times theory beside the free
                minimum, so the summary quotes a profile and never a Hessian
                bar at a rail (the first coarse run sat at its zero bound with
                a 0.039 kHz bar, which is the curvature of a wall).
  gamma_l       profiled and shared, in the mixed form only.
  sigma_laser   one per SESSION by default (P, T, E, M, Q), or ONE across
                every session under `--sigma-l shared`, so the temperature
                arm's density-dependent width cannot hide in the 130 C
                corner's own session width; beta's profile is read under each.
  Delta_alpha   PINNED at the record's deep value with its bar
                (results/polarizability_deep.csv) and propagated at its edges.
  rho           PINNED at 0.94 +- 0.04 and propagated the same way.
  Omega         TIED to the intensity through hyperpolarizability
                .two_photon_rabi_hz at every (P, w0, rho), times one scale
                under a 20 per cent Gaussian prior.
  power         `--power-scale` adds one multiplicative factor per session
                under a 10 per cent prior (the manifest's power_mW_inferred
                column is the record's own caution); Omega's scale is reported
                with and without it.
  M2            NOT fitted. Arms at 1, 1.5 and 2 with the axial collection
                window ALWAYS ON through the profile seam of
                lineshape.model_profile, never full_profile's own m2 switch,
                which is discontinuous at exactly 1.
  depletion     two arms, off and three mean cycles, through
                stark.companion_transit_mhz at the tied Omega's THEORY scale,
                a model form and not a parameter the fitted scale can switch
                off.
  pedestal      F465: fixed at the record's own quoted convention height (about 3e-3 of peak,
                fullmodel.FIT_TERMS), never fitted, since over these traces it is close enough to
                a constant offset to be degenerate with the per-trace baseline.
  retro tilt    F465: an unmeasured apparatus number. spec["retro_tilt_free"] fits it as one
                Cell-wide nuisance inside FIT_TERMS's own bound; otherwise fixed at the record's
                central value, FIT_TERMS's own start of zero. No production grid sets the flag.
  isotope       per peak (constants.PEAKS).
  centre        profiled per trace on a grid with parabolic refinements,
                re-profiled after every inner fit until it stops moving.
  amplitude,    solved linearly per trace, weighted by the condition's noise
  offset, slope law a^2 + bV with its dark floor.

ONE LIKELIHOOD BLOCK, the per-trace profile likelihood over every trace,
whitened per condition by its integrated correlation time (n / tau_int), so a
Delta chi2 of one is one sigma on the whitened statistic. No moment block, no
ruler block.

EVERY BAR NAMES ITS SOURCE IN ITS COLUMN: `_err_hessian` is a conditional
curvature with every other parameter pinned, `w0_err_parabola_um` is the
profile's parabola at Delta chi2 = 1, `start_spread_chi2` is the spread of the
starts, `beta_profile_*` is read off the fixed-beta chi2 rows, and
`width_slope_err_lsq_per_w` is a weighted linear fit's own error.

THE POWER-ARM CHECK IS A REFUSAL AND NOT A DIAGNOSTIC, PER SESSION AND POOLED.
At every grid point the model's own width ratio across each session's ladder
(P: 25 to 225 mW, E: 90 to 270, M: 35 to 210, Q: 25 to 225) at the TIED Omega
(scale one) with everything else fitted is compared with that session's
measured ratio, the P session's from results/power_sweep.csv and the others'
from the model-free contiguous half-maximum widths of their own traces, every
bar carrying the repeat scatter and the archive's block scatter, and a waist
whose predicted ratio exceeds the measured one by more than that bar is
refused. The pooled check combines the sessions by inverse variance. The
270 mW rung grows the P^2 lever by (270/225)^2 = 1.44.

RUNG GATES. Every run writes private/cache/ultra_joint_2026-09-14/gate_<run>.txt
in round_gate.py's form, a list of checks with their values ending in PASS or
REFUSE, and cells_<run>.json with every cell at full precision; `--arms-only
<cells.json>` runs the M2, depletion and propagation stage on a base grid a
previous run produced. The chained queue in QUEUE_LINE.txt starts each rung
only when the previous gate reads PASS.

PROVENANCE. Every row is DIAGNOSTIC: a discrimination between candidate
forms on one archive, conditional on the pinned terms named above, and not a
measurement of the waist. RUNG: the profile is rung 3, the ties are rung 1,
the whitening and the bound construction are rung 2.

FAILURE MODES. A depletion arm through companion_transit_mhz carries only the
lost-fraction form of the widening, about one per cent at the retired waist convention and six at 42,
not the velocity-resolved twelve per cent the twin's world builder carries. A
morning trace whose model-free width reads 2 MHz against its repeats' 5 is in
the fit under its condition's law and is named in the width rows. A caller
who passes m2 to full_profile instead of the closure gets the discontinuous
switch.

    RB5S6S_WORKERS=10 python scripts/run_ultra_joint.py --coarse --all-sessions --run-name coarse_all
    python scripts/run_ultra_joint.py --coarse --all-sessions --power-scale --no-stage2 --out <path>   # an arm run
    python scripts/run_ultra_joint.py --coarse --form mixed            # the canonical traces alone
    python scripts/run_ultra_joint.py --time-cells                     # 40 um, the retired convention, and 90 um
    python scripts/run_ultra_joint.py --plant                          # 1 worker vs 2
    python scripts/run_ultra_joint.py --separable                      # the named comparison arm, below

THE LINE IS THE JOINT LINE BY DEFAULT (C6b, owner orders O45/O46/O49, A148). Every Cell of the
production grid (the base matrix and the M2/depletion/propagation arms) reads its shift and its
transit together from the atom Monte Carlo's tabulated line (`rb5s6s.volume_line.JointTable`,
through `Cell.physics`'s own `volume_line` switch) instead of convolving them as two independent
kernels. `--separable` is the named comparison arm: it restores the transit-and-ramp convolution
(the saturated ramp density, the kernel gate's MC depletion factor) that was the only form before
this window. Each row's own `spec` column carries `ramp`, `depletion` and `volume_line` as they
were run, so an artefact says which line built it without a separate column. `Cell.__init__`'s own
defaults are UNCHANGED (ramp='saturated', depletion='mc', volume_line unset): they are what a bare
`Cell(_spec(...))` gets outside this file's own `main`, which is every test and helper that builds
one directly, and changing them there would make an unrelated unit test pay for an atom-sampled
Monte Carlo table build it never asked for. The flip lives where the production run is assembled,
`main`'s own `common` dict, exactly as `run_ultra_joint_closure.py`'s `--world`/`--fitter` and
`run_window_surface.py`'s `--world` flip their own defaults without touching the classes they call.
"""
from __future__ import annotations

import csv
import json
import math
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")   # one BLAS thread per pooled worker
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import re

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from rb5s6s import beam_field as BF                                 # noqa: E402
from rb5s6s import config as C                                     # noqa: E402
from rb5s6s import constants as K                                  # noqa: E402
from rb5s6s import stark                                           # noqa: E402
from rb5s6s.pmfmt import pm_cells                                  # noqa: E402
from rb5s6s.fullmodel import FIT_TERMS, collection_z_ratio_m2, convolution_licence, full_profile   # noqa: E402
from rb5s6s import kernel_gate                                                          # noqa: E402
from rb5s6s import noise                                                                # noqa: E402
from rb5s6s import windows as W                                                         # noqa: E402
from rb5s6s.hyperpolarizability import two_photon_rabi_hz          # noqa: E402
from rb5s6s.lineshape import (aperture_onaxis_factor_actual, local_ramp_density, ramp_mixture, saturated_ramp_density,   # noqa: E402
                              stark_shift_S0_mhz)
from rb5s6s.noise import condition_noise_model, sigma_of_v         # noqa: E402
from rb5s6s.qc import contiguous_fwhm_ms                           # noqa: E402
from rb5s6s.vanderwaals import beta_self_anchored, beta_self_budget                  # noqa: E402
from rb5s6s.workers import n_workers                               # noqa: E402
from run_density_laws import n_aih, n_nes, n_smi                          # noqa: E402

OUT = C.RESULTS_DIR / "ultra_joint_fit.csv"
GATE_DIR = ROOT / "private" / "cache" / "ultra_joint_2026-09-14"

# ------------------------------------------------------------ the saturation companion's ensemble scale
#: F324 (with addenda e and f) and A134: the Cell's saturation companion is evaluated at the ON-AXIS
#: two-photon Rabi frequency, but the ensemble of collected atoms never sees that frequency. The
#: steady-state average over the transverse and axial profile, times the crossing's own transient
#: share, leaves about half of it (0.49 to 0.51 across the bench's own range), the effective Rabi
#: fraction this table carries. Tabulated over the optical Bloch equations integrated along each
#: sampled atom's crossing (`private/cache/plan_2026-09-16/p18_sat_nodes.py`) at twelve (waist,
#: temperature) nodes, 225 mW, s0_scale 1.0, the trace's own kinetic temperature: three waists (41,
#: 42.38, 45 um) by four temperatures (70, 90, 110, 130 C). Interpolated bilinearly and REFUSED
#: outside that grid, because the table was never asked at any other node and this record does not
#: extrapolate a Monte Carlo it has not run.
#: TRACKED IN THE PACKAGE since 2026-09-25 (an audit that day: a tracked producer read it from private/cache/, so a clone,
#: the public mirror and every stranger re-running this producer lacked it). A byte copy of the harness's output;
#: the harness itself is still private, so a re-run of it is copied here by hand (owed: port it to scripts/).
SAT_FRACTION_TABLE_PATH = ROOT / "rb5s6s" / "data" / "sat_fraction_table.tsv"
_SAT_FRACTION_GRID_CACHE: dict = {}


def _sat_fraction_grid() -> tuple:
    """The twelve canonical nodes of `SAT_FRACTION_TABLE_PATH`, as (w0_um sorted, T_C sorted, the
    effective-Rabi-fraction grid), cached on the path so a run building many Cells pays the read
    once. Filters to the standard condition (225 mW, s0_scale 1.0, the row's own kinetic
    temperature, not the two _tk diagnostic rows displaced from it) -- the file also carries a
    125 mW row and an s0-off probe that are not part of the (waist, temperature) grid this reads."""
    cached = _SAT_FRACTION_GRID_CACHE.get(SAT_FRACTION_TABLE_PATH)
    if cached is not None:
        return cached
    with SAT_FRACTION_TABLE_PATH.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    keep = [r for r in rows if float(r["P_mW"]) == 225.0 and float(r["s0_scale"]) == 1.0
           and float(r["T_kin_C"]) == float(r["T_C"])]
    w0s = sorted({float(r["w0_um"]) for r in keep})
    Ts = sorted({float(r["T_C"]) for r in keep})
    if len(w0s) * len(Ts) != len(keep):
        raise ValueError(f"sat_fraction_table: {len(keep)} standard rows do not fill a "
                         f"{len(w0s)}x{len(Ts)} (w0, T) grid, so the table changed shape")
    grid = np.full((len(w0s), len(Ts)), np.nan)
    for r in keep:
        i, j = w0s.index(float(r["w0_um"])), Ts.index(float(r["T_C"]))
        grid[i, j] = float(r["effective_rabi_fraction"])
    if np.any(np.isnan(grid)):
        raise ValueError("sat_fraction_table: the standard grid has a hole")
    out = (np.array(w0s), np.array(Ts), grid)
    _SAT_FRACTION_GRID_CACHE[SAT_FRACTION_TABLE_PATH] = out
    return out


def bloch_fraction(w0_um: float, T_C: float, clamp: bool = False) -> float:
    """The saturation companion's ensemble-effective Rabi fraction at (w0_um, T_C), bilinearly
    interpolated over `_sat_fraction_grid`'s twelve nodes (F324, A134). RAISES outside the grid's
    own span (41 to 45 um, 70 to 130 C): a Cell built at a waist or a temperature the atom Monte
    Carlo has not been run at has no companion reading to carry, and extrapolating one would
    certify a scale nothing has checked. `clamp=True` (default False) holds the reading at the
    nearest edge instead, the same escape `aperture_onaxis_factor_actual`'s own `clamp_floor` gives
    for a beam this bench cannot make: a caller FITTING a real trace to a specific w0 must not pass
    it, and the theory-cell test fixture, which is explicitly built to probe closed forms at waists
    outside the validated grid, does."""
    w0s, Ts, grid = _sat_fraction_grid()
    if not (w0s[0] <= w0_um <= w0s[-1]) or not (Ts[0] <= T_C <= Ts[-1]):
        if clamp:
            w0_um = float(np.clip(w0_um, w0s[0], w0s[-1]))
            T_C = float(np.clip(T_C, Ts[0], Ts[-1]))
        else:
            raise ValueError(
                f"bloch_fraction: (w0={w0_um:g} um, T={T_C:g} C) is outside the twelve-node grid "
                f"({w0s[0]:g} to {w0s[-1]:g} um, {Ts[0]:g} to {Ts[-1]:g} C, "
                f"{SAT_FRACTION_TABLE_PATH.name}); no Monte Carlo has graded that node")
    i = int(np.clip(np.searchsorted(w0s, w0_um) - 1, 0, len(w0s) - 2))
    j = int(np.clip(np.searchsorted(Ts, T_C) - 1, 0, len(Ts) - 2))
    w0_lo, w0_hi = w0s[i], w0s[i + 1]
    T_lo, T_hi = Ts[j], Ts[j + 1]
    tw = 0.0 if w0_hi == w0_lo else (w0_um - w0_lo) / (w0_hi - w0_lo)
    tt = 0.0 if T_hi == T_lo else (T_C - T_lo) / (T_hi - T_lo)
    f00, f01 = grid[i, j], grid[i, j + 1]
    f10, f11 = grid[i + 1, j], grid[i + 1, j + 1]
    return float((1 - tw) * (1 - tt) * f00 + (1 - tw) * tt * f01 + tw * (1 - tt) * f10 + tw * tt * f11)

# ------------------------------------------------------------------ the design
# THE GRID STARTS AT THE BORE'S FLOOR (C6a, 2026-09-22, F291): the bench cannot focus tighter than about
# 40.9 um, so 41 um is the first grid point and the Cell REFUSES anything below it rather than reading it
# at the floor's factor with its own transit (an inconsistent beam). 41 sits between the 40 and 42 um nodes,
# inside the kernel gate's interpolation span; 42 to 56 um keep the 2 um step of 2026-09-18.
W0_GRID_UM = (41.0,) + tuple(float(w) for w in range(42, 57, 2))
W0_COARSE_UM = (42.0, 46.0, 52.0, 56.0)   # the coarse stage inside the reachable band and its margin (C6a)
FORMS = ("gaussian", "lorentzian", "mixed")
M2_ARMS = (1.0, 1.5, 2.0)
DEPLETION_ARMS = (0.0, 3.0)          # mean cycles through stark.companion_transit_mhz
OMEGA_PRIOR_FRAC = 0.20
POWER_PRIOR_FRAC = 0.10
RHO, RHO_ERR = K.RHO_RETRO, K.RHO_RETRO_ERR
TEMPS = (70.0, 90.0, 110.0, 130.0)
T_SWEEP_POWER_MW = 225.0             # the blank manifest power (docs/DATA.md)
DCHI2_ONE_SIGMA = 1.0
BETA_THEORY_DCHI2_MAX = 9.0      # dchi2 at the theory coefficient beyond 3 sigma one-sided: the form fails on beta (W1i finding)
SIGMA_L_MAX_MHZ = K.SIGMA_LASER_BOUND_2025_TRANSITION_MHZ   # 2.4 MHz on the TRANSITION axis, the axis of every sigma_l here (W1j finding F1: the per-photon 1.2 was read against a transition-axis width)
# THE ADMISSION IS ABSOLUTE AND IN TWO HALVES (W1m, A254, after three forms in three commits): the
# wing samples of a session read its NOISE LAW (chi2_red_wing against 1 +- sqrt(2/n_eff_wing)),
# the core samples read the MODEL (chi2_red_core against the same), and the gate names the word:
# WING-OFF when the wing is off either way (the session's noise law or the model's far wing: the
# 12 MHz moment window says which), MISFIT when the core costs too much, UNDER-COST when it
# costs too little (free nuisances). No pool, no reference containing the tested session.
SESSION_Z_MAX = 5.0                   # the refusal in sigma of sqrt(2/n_eff) per statistic
CORE_HALF_MHZ = 6.0                   # |nu - centre| inside this is the core, the 6 MHz window of the moment arm; outside is the wing
SESSION_VOTE_SHARE_MAX = 2.0          # a session's share of n_eff at most twice its share of the traces (W1j finding F4: the evening's tau_int at the white floor gave 46 traces half the vote)
RESOLVE_LEVELS = 4.0          # a crossing is read off the grid only within this many levels of rise per step
DCHI2_ONE_SIDED_95 = 2.71
POWER_ARM_REFUSAL_BARS = 1.0
BETA_PROFILE_REL = (0.0, 1.0, 5.0, 20.0)
MAX_OUTER = 4                        # centre re-profiles per start
CENTRE_TOL_MHZ = 0.02
CENTRE_FINE_MHZ = 0.15
_BETA = beta_self_anchored()
# THE BAR IS THE WHOLE BUDGET, not the anchor measurement's share of it.
# `beta6_err_khz` carries Zameroski's 10.08 per cent alone; a pull of a fitted
# coefficient against theory has to divide by the theory's own bar, which
# `beta_self_budget` measures at 10.64 per cent by displacing each input in
# turn. The difference is small here BECAUSE the anchor dominates, and that
# is a result of the budget rather than a reason not to read it.
BETA_THEORY_KHZ = float(_BETA["beta6_khz"])
BETA_THEORY_ERR_KHZ = float(beta_self_budget()["err_khz"])
#: beta_self's own budget, relative: beta_self_budget()['err_khz'] / BETA_THEORY_KHZ.
BETA_PRIOR_FRAC = float(beta_self_budget()["err_khz"]) / BETA_THEORY_KHZ
# THE PERMEATED GAS CARRIES ITS SEALED-CELL LAW (F245, owner order O41, 2026-09-21). A sealed cell holds a
# fixed AMOUNT of permeated gas, so its density is fixed and its Lorentzian width goes as n sigma v, T^+0.5
# for hard spheres and T^+0.3 with the van der Waals velocity dependence; the constant width it replaces is
# the p = 0 arm. `gamma_l` is the permeated width at the corner, GAMMA_L_T_REF_K, and each condition reads
# it through (T / T_ref)^p. Across 70 to 130 C that is 8.4 per cent at p = 0.5, a drift of the SAME sign as
# the self-broadening's, which is why a density slope fitted without it hands the gas's drift to beta_self.
GAMMA_L_EXP = 0.5
# F420 OWED A NEGATIVE ARM AND THIS RECORD WROTE PROSE INSTEAD UNTIL THE OWNER RE-SENT (2026-09-23).
# The velocity average is 5.0 per cent across 70 to 130 C at T^0.30 and 8.4 at T^0.50, and the
# PERMEATION CLOCK is Arrhenius at about 0.49 eV (`docs/lit/carle2023.md`), a factor of 11.8 over the
# same ladder: a cell equilibrated at room temperature sits above air's 3.98 mTorr once heated and
# SHEDS helium, which is the same size as the velocity average and the OPPOSITE sign. So the arms
# span both directions, and the exponent is a model-form ARM and never a derived constant.
# F427 then measured the term itself as UNDETECTED (gamma_l 0.0350 +- 0.0283 MHz, delta chi2 0.60
# against the 3.84 that one degree of freedom needs at 95 per cent), so these arms span a term the
# data does not resolve, and no surface quotes an exponent as though it had been measured.
GAMMA_L_EXP_ARMS = (-0.5, -0.3, 0.0, 0.3, 0.5)
GAMMA_L_T_REF_K = 403.15
#: Delta_alpha's, relative: the committed +-5.9 a.u. on -1131.8.
ALPHA_PRIOR_FRAC = abs(K.DELTA_ALPHA_ERR_AU / K.DELTA_ALPHA_AU)

LAWS = {"AIH": n_aih, "Nesmeyanov": n_nes, "SMI": n_smi}   # AIH central since O42 (F259); the others are arms
PROPAGATIONS = (("delta_alpha", +1), ("delta_alpha", -1), ("rho", +1), ("rho", -1), ("rho_floor", 0),
                ("law", "Nesmeyanov"), ("law", "SMI"))
SESSIONS = {"P": "the 130 C power sweep, canonical p_sweep",
            "T": "the 70/90/110 C sweep at 225 mW, canonical t_sweep",
            "E": "the 2025-07-04 LeCroy evening, 90/180/270 mW, internal 130 C, gain 1e6, ms axis with a fitted rate per peak",
            "M": "the 2025-07-17 campaign morning, 4192 at 35 to 210 mW, the campaign 4192 rate times the measured pilot scale",
            "Q": "the manifest's excluded 130 C 4154 attempt, a diagnostic arm and never the headline"}
SESSION_LADDER_W = {"P": (0.025, 0.225), "E": (0.09, 0.27), "M": (0.035, 0.21), "Q": (0.025, 0.225)}
# THE LASER WIDTH'S FLOOR IS THE BENCH'S, AND IT IS ALSO A COST. Three bench
# facts put the laser near 0.1 MHz on its own axis, 0.2 on the transition
# axis (docs/RESULTS.md C2), and model_profile sets its grid by the narrowest
# smooth kernel, so a Gaussian of 0.05 MHz FWHM under a 3.5 MHz Lorentzian
# costs thirty times the convolution for nothing the line can show: the first
# timing of the 40 um cell railed there and took 520 s where the retired waist convention took 15.
# The Omega scale and beta have no wall of their own so that the prior, or
# the profile, and not a bound is what the reader sees.
# THE EVENING RATE'S BOX IS WIDENED (2026-09-14): it sat on the old +-25 per cent wall
# in every admitted cell, and a wall no gate reads makes every bar conditional.
#: makes the log-determinant residual real: sum ln sigma^2 / tau over the L is about -0.92e6
#: (measured 2026-09-16 at 52 um); a constant moves no minimum.
LOGDET_OFFSET = 4.0e6
BOUNDS = {"beta_rel": (0.0, 40.0), "alpha_rel": (0.5, 1.5), "sigma_l": (0.2, 6.0), "omega_scale": (0.0, 3.0),
          "gamma_l": (0.0, 3.0), "lograte": (math.log(0.5), math.log(1.5)), "power_scale": (0.5, 1.5),
          "s0_scale": (0.2, 5.0), "w0_": (0.7, 1.4),
          # F465, F471: read from FIT_TERMS rather than restated, so a change to the record's
          # own bound moves this table without a second edit.
          "retro_tilt_rad": tuple(FIT_TERMS["retro_tilt_rad"][:2])}
# F465: full_profile's pedestal_height_frac and retro_tilt_rad were passed by neither the world nor
# the Cell (the module docstring's own term table called both "dropped: degenerate with the
# per-trace baseline and with the session's laser width on these traces"), so a fit and a twin
# generated from it both carried a term the fitter's own gate certifies with the term absent.
# PEDESTAL_HEIGHT_FRAC is the record's own quoted convention (FIT_TERMS's start, about 3e-3): a
# FIXED input, always passed, never fitted, since results/twin_term_census.csv's own doppler_pedestal
# row states why fitting it here buys nothing -- over these traces' sub-100 MHz span the 931 MHz
# pedestal is a near-constant offset, degenerate with the per-trace linear baseline `Cell.linear`
# already floats.
PEDESTAL_HEIGHT_FRAC = FIT_TERMS["pedestal_height_frac"][2]
# The retro tilt is an unmeasured apparatus number (docs/plan/12_open-apparatus-items.md, "Tilt of
# the retro-reflection": every row there states a tilt nobody measured, "no forecast rests on it",
# "nothing in RESULTS/ carries it"). `spec["retro_tilt_free"]` fits it as one Cell-wide nuisance,
# box-bounded by the record's own FIT_TERMS bound and start (off by default, so every existing
# Cell is unaffected); when it is not free the Cell still passes RETRO_TILT_START, FIT_TERMS's own
# start and the record's central value, to full_profile, since no measurement assigns it a nonzero
# one. Either way the term is wired into the call full_profile receives rather than silently absent.
RETRO_TILT_START = FIT_TERMS["retro_tilt_rad"][2]
# THE OWNER'S SECOND ANGLE (2026-09-17 00:30: "explore also the w_0 free and S_0 free combinations"):
# `spec["s0_free"]` frees the light shift per condition (`s0_scale_<condition>`, no prior), and
# `spec["w0_free"]` lets the three waist meters float about the scanned waist (`w0_transit_rel`,
# `w0_shift_rel`, `w0_sat_rel`, the transit going as the inverse, the shift and the saturation's
# Rabi frequency as the inverse square, per the exponent table), so their disagreement, term by
# term, is a statement about the term list. Tied is the default and the primary matrix's form.
START_SIGMA_L = {"gaussian": (1.4, 1.0), "lorentzian": (0.8, 0.4), "mixed": (1.3, 0.9)}
#: The volume line's table settings (C6b item 2), each overridable through `spec["volume_line"]`: the atoms and
#: seed of the Monte Carlo, the S0 step and the margin above the highest shift the Cell can reach, the detuning
#: step and its margin beyond the widest trace, the reach used when a trace's axis is in time (the evening), and
#: where the tables are stored.
#: "beam" DEFAULTS TO "clipped" (C6c), NOT "gaussian": the model of record is the bore-clipped focus
#: (the owner's standing rule that the twin runs the full model, the bore included; F465/F471 landed
#: the plain Cell's own side of it, `self._clipped_beam`). The production run's own default flip
#: (`main`'s `common.update(..., volume_line=True)` below) passes no dict at all, so it reads this
#: default outright, and `Cell._table`'s `VolumeWorld._bind` already tracks whichever beam a
#: volume-line Cell's own table carries (`cell.volume["beam"]`), so a Cell built here and the world
#: that closes against it move to the clipped beam TOGETHER rather than drifting onto two different
#: ones. "gaussian" stays a supported, explicit value (`run_ultra_joint_closure.py`'s
#: `RB5S6S_CLOSURE_FITTER="volume:..."` names it opposite "volume-clipped" for exactly that
#: comparison) for a caller that wants the free-space approximation on purpose.
VOLUME_DEFAULTS = {"n_path": 8000, "seed": 20260922, "s0_step_mhz": 0.05, "s0_margin": 0.1, "delta_step_mhz": 0.05,
                   "delta_margin_mhz": 5.0, "reach_mhz": 40.0, "beam": "clipped",
                   "cache_dir": os.environ.get("RB5S6S_VOLUME_TABLE_DIR", str(ROOT / "private" / "cache" / "volume_tables"))}
START_OTHER = ((1.0, 1.0, 0.3), (4.0, 0.8, 0.05))      # beta_rel, omega_scale, gamma_l per start
DIFF_STEP = 3e-3
#: Half-window at load, MHz on the transition axis. The model puts the line below
#: 1e-3 of peak beyond 33.3 MHz and the retrace mirror sits at 38 to 50 MHz, so this
#: keeps every wing sample the noise-law statistic reads (|nu| > CORE_HALF_MHZ = 6)
#: and drops the mirror band entirely. Wider than `linefit.adaptive_halfwidth`'s
#: 25 MHz cap on purpose: that cap is sized for a single-line FIT, and this producer
#: needs the wing to grade a session's noise law.
RETRACE_CUT_MHZ = 33.0
MAX_NFEV = 160  # doubled again 2026-09-16: `alpha_rel` added a dimension and the
# gate's own convergence check went red, the free minimum sitting up to 1171 chi2
# ABOVE the lowest fixed-beta refit. A free fit scoring above its own profile has
# not found the minimum, and every beta and waist read off such a cell is an
# optimiser artefact.
EVENING_RATE_SEED = 5.9 / 470.0      # run_stark_joint's r0, MHz per ms, when no committed rate exists
# A TRACE THAT ENDS AT ITS OWN PEAK IS HALF A LINE. One morning file holds 976
# finite samples of 2000 (the header-variant NaN rows the loader masks) and
# its window stops within a per cent of the peak, so its model-free width
# reads 2 MHz against its repeats' 5 and a profiled centre on it is a guess.
# It is dropped with its reason written as a row, never silently.
TRUNCATED_EDGE_FRAC = 0.02


def deep_delta_alpha() -> tuple[float, float]:
    """The record's deep differential polarizability with its bar, from the
    committed derivation and never from the package constant."""
    path = C.RESULTS_DIR / "polarizability_deep.csv"
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["quantity"] == "delta_alpha" and r["key"] == "at_drive":
                return float(r["value"]), float(r["err"])
    raise SystemExit(f"{path}: no delta_alpha at_drive row, so the shift cannot be pinned")


def evening_rate_seeds() -> dict:
    """The committed fitted evening rates per peak (results/stark_joint.csv
    reh_rate rows), MHz per ms, or run_stark_joint's own seed where absent."""
    out = {}
    path = C.RESULTS_DIR / "stark_joint.csv"
    if path.is_file():
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("quantity") == "reh_rate":
                    out[r["key"]] = float(r["value"])
    return out


def morning_pilot_scale() -> tuple[float, float]:
    """The measured pilot rate scale of results/morning_ruler.csv, or one
    with no bar when the file is absent."""
    path = C.RESULTS_DIR / "morning_ruler.csv"
    if path.is_file():
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("quantity") == "pilot_rate_scale_measured":
                    return float(r["value"]), float(r["err"])
    return 1.0, float("nan")


# ------------------------------------------------------------------ the archive
def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return float("nan")


def noise_law_for(rows, role, peak, T, P_mW):
    """The committed noise law and correlation time of one condition. The
    t_sweep rows carry a blank power, so the match is on the keys the row has
    and then on the nearest by temperature and power."""
    def dist(x, y):
        d = abs(x - y)
        return d if np.isfinite(d) else float("inf")
    exact = [r for r in rows if r["role"] == role and r["peak"] == peak
             and _f(r["temperature_C"]) == T and (_f(r["power_mW"]) == P_mW or r["power_mW"] == "")]
    pool = exact or [r for r in rows if r["peak"] == peak and _f(r["temperature_C"]) == T] \
        or [r for r in rows if r["peak"] == peak] or rows
    r = min(pool, key=lambda r: (dist(_f(r["temperature_C"]), T), dist(_f(r["power_mW"]), P_mW)))
    c = _f(r["c"])
    return dict(a=_f(r["a_V"]), b=_f(r["b_V"]), c=c if np.isfinite(c) else 0.0, lev_max=float("inf"),
                tau_int=_f(r["tau_int"]), source="results/noise_model.csv",
                # THE KEY COMES FROM THE CALLER'S OWN CONDITION, NOT FROM THE ROW (F186, 2026-09-19).
                # `_tau_key_of_row` needs the row's power and the t_sweep rows carry a BLANK one, as this
                # function's own docstring says, so it returned None for all twelve temperature-arm
                # conditions, `effective_tau` took its documented fallback, and those twelve whitened by the
                # RAW segment time: 14.080 against a post-fit 0.950 at 4154 110 C. The relative weights of
                # the conditions therefore moved, which moves the estimates and not only the bars, and the
                # arm that was down-weighted is the one that separates the transit from the laser width.
                # The caller holds peak, T and P_mW; the row is the fallback and no longer the source.
                tau_eff=noise.effective_tau({"tau_int": _f(r["tau_int"])}, tau_resid_table(),
                                            _tau_key(peak, T, float(P_mW) / 1e3) if P_mW is not None
                                            and np.isfinite(_f(P_mW)) else _tau_key_of_row(r)))


def _law_from_traces(volts):
    law = condition_noise_model(list(volts))
    tau = float(law.get("tau_int", 1.0))
    return dict(a=float(law["a"]), b=float(law["b"]), c=float(law.get("c", 0.0)), lev_max=float("inf"),
                tau_int=tau if np.isfinite(tau) else 1.0, source="condition_noise_model on the session's own traces",
                n_traces=int(law.get("n_traces", len(volts))), rho1=float(law.get("rho1", float("nan"))))


def _rates():
    rates = {}
    with (C.RESULTS_DIR / "linefit_conditions.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            v = _f(r.get("rate_t"))
            if np.isfinite(v):
                rates[(r["peak"], r["T"], r["P"])] = v
    return rates


def design(traces_per_condition: int | None = None, with_excluded: bool = False) -> list[dict]:
    """The canonical RF-off traces with their rate, session, isotope, noise law
    and correlation time; with the manifest's excluded 130 C RF-off traces as
    session Q when asked. `traces_per_condition` limits the repeats per
    (peak, T, P), first by filename, for the plants."""
    rates = _rates()
    with (C.RESULTS_DIR / "noise_model.csv").open(encoding="utf-8") as fh:
        laws = list(csv.DictReader(fh))
    roles = ("p_sweep", "t_sweep") + (("excluded",) if with_excluded else ())
    with (C.DATA_RAW_DIR / "MANIFEST.csv").open(encoding="utf-8") as fh:
        man = sorted((r for r in csv.DictReader(fh)
                      if r["role"] in roles and r["rf_on"] == "False"
                      and (r["flag"] == "canonical" or r["role"] == "excluded")),
                     key=lambda r: r["file"])
    rows, seen = [], {}
    for r in man:
        T = float(r["temperature_C"])
        if T not in TEMPS:
            continue
        p_mw = _f(r["power_mW"])
        if not np.isfinite(p_mw):
            p_mw = T_SWEEP_POWER_MW
        key = (r["role"], r["peak"], r["temperature_C"], r["power_mW"])
        if traces_per_condition is not None and seen.get(key, 0) >= traces_per_condition:
            continue
        seen[key] = seen.get(key, 0) + 1
        rate = rates.get((r["peak"], r["temperature_C"], r["power_mW"]))
        if rate is None:
            cand = [v for (p_, T_, _), v in rates.items() if p_ == r["peak"] and T_ == r["temperature_C"]]
            if not cand:
                raise SystemExit(f"no sweep rate for {r['file']} in results/linefit_conditions.csv")
            rate = float(np.mean(cand))
        sess = "Q" if r["role"] == "excluded" else r["session"]
        law = None if sess == "Q" else noise_law_for(laws, r["role"], r["peak"], T, p_mw)
        rows.append(dict(file=r["file"], role=r["role"], peak=r["peak"], T=T, P_W=p_mw * 1e-3,
                         rate=rate, session=sess, iso=int(K.PEAKS[r["peak"]]["isotope"]),
                         law=law, tau=max(float(law.get("tau_eff", law["tau_int"])), 1.0) if law else float("nan")))
    return rows


def session_trees() -> dict:
    """Where the two excluded sessions live and whether they are present, by
    run_stark_joint.py's own paths and patterns."""
    import glob
    import run_stark_joint as sj
    return {"E": (sj.SESSION_20250704, bool(glob.glob(str(sj.SESSION_20250704 / "2025-07-04" / "C2L=*.csv")))),
            "M": (sj.SESSION_20250717, bool(glob.glob(str(sj.SESSION_20250717 / "*mw*.csv"))))}


_TRACES: dict = {}
#: The sessions outside the manifest, loaded ONCE in the parent through
#: run_stark_joint.py's loaders and handed to every worker by the pool's
#: initializer. Ten workers each running the evening loader at once is what
#: broke the first rung-0 pool: fifty large files through genfromtxt in ten
#: processes beside a gate, and one process was terminated. The workers now
#: read only the manifest's own traces.
_SESSION_TRACES: list = []


def _init_worker(session_traces):
    global _SESSION_TRACES
    _SESSION_TRACES = list(session_traces)


# ---------------------------------------------------------------- moment arm
#: The moment arm's windows and orders (owner orders O12, O13, O17).  BOTH
#: PARITIES and orders 2 to 7, because the owner's specification opens with the
#: ODD ones and their ratios and the arm that ran on 2026-09-15 carried orders
#: [2, 4] at five windows, p = 10, which is a ladder with nothing to disagree
#: about.  The windows sit inside the +-42.5 MHz sweep with room, and 12 is the
#: widest that does not reach the off-centre-sweep mirror band.
#: Two-sided 95 per cent t-factors by degrees of freedom, for the bar on a mean
#: of a handful of repeats. A condition carries about five, so the Gaussian 1.96
#: understates the interval by a third and the number has to come from the t.
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447,
        7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}

# THE WINDOWS, MEASURED AT THE ARCHIVE'S NOISE before they were chosen (PLAN v3 D9, 2026-09-19). Per-trace
# signal-to-noise of each order against the window, at the archive's own law: the odd orders read <= 1.0 at
# EVERY window and are dead; k4 reads 0.3 at 8 MHz (its zero crossing) and k6 reads 7.8 at 21 (its collapse);
# the even-order sum ranks 3 > 2 > 5 > 1 > 13 > 8 > 0.5 > 21. The quoted set is log-spaced at 2.0/2.5/2.6,
# spans thirteenfold so four windows are not four readings of one thing (the covariance below is DIAGONAL
# by construction, so span is what makes a fourth window worth having), and avoids both poisoned cells.
# THE TWIN'S SNR IS OPTIMISTIC BY A8's OWN EXCESS (the C2 physics chair, 2026-09-19): the archive's repeats
# scatter 4.06x the twin's at 3.25 MHz, 2.95 at 6 and 1.82 at 12, so the per-trace table divided by those
# factors reads k4 about 11, 15, 13, 29 and k6 about 7, 9, 5, 17 at 1, 2, 5, 13 MHz -- six of twelve even cells
# under 15, and the wide end relatively stronger, not weaker. The set stands on its span and its avoidance
# of the two deaths; no cell is claimed above a threshold the archive's own scatter does not support. The diagnostic set holds the SNR peak (3) and the two deaths (8, 21), computed
# and written with admitted=False so a reader can SEE where each channel dies and never quotes it there.
# Both sets are on the window surface's grid, so the twin's bias is subtractable at every one. The set this
# replaces, (2, 8, 13) of 2026-09-18, sat on k4's zero; (3.25, 6, 12) before it intersected the surface nowhere.
MOMENT_WINDOWS = W.QUOTED
DIAGNOSTIC_WINDOWS = W.DIAGNOSTIC
#: THE FLOOR IS DERIVED FROM THE ARM'S OWN PRECISION, never tuned to pass a rung (2026-09-19, the moments
#: ladder's fourth stage-0 run). With the fit exact the arm still reproduces a statistic only to an ABSOLUTE
#: error of about epsilon times its dimensional scale mu2^(n/2): measured on mu7/mu5@2, a ratio whose numerator
#: sits at 1.3e-4 of its scale, the relative error was 3.6e-3, so epsilon is about 4.7e-7. The noiseless
#: rung's tolerance is 1e-3 relative (`ladder_gate.NOISELESS_TOL`), so a statistic whose normalised size is
#: under epsilon / 1e-3 = 5e-4 cannot meet it for arithmetic reasons whatever the physics, and is refused as
#: BELOW THE ARM'S PRECISION with that number in its reason. F144's k7@13 read 6.6e-7, three decades under
#: this; the median live row reads 4.1e-4 relative error and is untouched. EPSILON IS ONE POINT, measured on
#: k7, and the grid-movement error spans 2.3e-8 to 2.9e-4 across orders 3 to 7 and windows 1 to 21 (the C2
#: physics chair): k6's margin under this floor is 1.7x, not k7's three decades. Every odd order on this archive
#: sits under the floor at every quoted window, which agrees with the SNR measurement of 02:20 (odd orders
#: <= 1.0 at every window): the odd block is a test of the model's zero, and the floor is what says so.
CUMULANT_FLOOR_REL = 5e-4
MOMENT_ORDERS = (2, 3, 4, 5, 6, 7)


def _moment_stats(nu, y, windows=MOMENT_WINDOWS, orders=MOMENT_ORDERS):
    """Windowed moments of one trace, keyed `mu<order>@<window>`.

    `baseline=None` ON PURPOSE, and it is the repair of a measured bias rather
    than a convenience.  `windowed_moments` defaults to a WINGS baseline, and
    on this sweep the line itself contributes 0.878 per cent of peak at the
    +-20 to 28 MHz strips, which biases mu2 by -7.6 per cent and mu3 by -20.9 at
    the 12 MHz window -- and the sweep cannot be widened, because the model puts
    the line below 1e-3 only beyond 33.3 MHz while the off-centre-sweep mirror
    occupies the outer tenth from about 38.  A strip baseline is not available
    on this dataset.  The caller therefore removes the FITTED offset and slope
    first, which is what the profile fit already estimates, and hands this
    function a trace whose baseline is a fitted parameter and not a strip.
    """
    # MOMENTS ARE THE VECTOR (O33, A72, and O49 which retired the k5/mu3 diagnostic this function
    # used to emit beside them). One quadrature per (window, trace), and nothing here converts it
    # to a cumulant any more: where a conditioning read is still wanted, it is the moments' own,
    # the replica spread over the mean that `moment_arm`'s SEM and SNR already carry, never a
    # second, cumulant-valued basis whose keys would stop corresponding to the model's.
    from rb5s6s.moments import windowed_moments
    out = {}
    top = max(orders)
    for w in windows:
        mu, _ = windowed_moments(nu, y, w, orders=tuple(range(1, top + 1)), baseline=None)
        for n in orders:
            out[f"mu{n}@{w:g}"] = float(mu[n])
    return out


def _finish(t):
    t["ones"] = np.ones_like(t["x"])
    t["n"] = int(t["x"].size)
    return t


def load_sessions(sessions) -> tuple[list[dict], list[dict]]:
    """Sessions E and M read in place through run_stark_joint.py's loaders,
    their noise laws fitted per condition from their own traces. Returns the
    finished trace dicts and the traces dropped with their reasons."""
    out, dropped = [], []
    if not ("E" in sessions or "M" in sessions):
        return out, dropped
    import run_stark_joint as sj
    from run_beta_self import load_t_rates
    if "E" in sessions:
        reh, _ = sj.load_session_20250704()
        groups: dict = {}
        for t in reh:
            d = dict(file=f"E/{t['peak']}/{int(round(t['P'] * 1e3))}mW/{len(groups.get((t['peak'], t['P']), []))}",
                     role="evening", peak=t["peak"], T=130.0, P_W=float(t["P"]), rate=float("nan"),
                     session="E", iso=int(K.PEAKS[t["peak"]]["isotope"]), law=None, tau=float("nan"),
                     x=np.asarray(t["x"], float) - float(t["c0"]), v=np.asarray(t["v"], float), axis="ms")
            groups.setdefault((t["peak"], t["P"]), []).append(_finish(d))
        for grp in groups.values():
            law = _law_from_traces([t["v"] for t in grp])
            for t in grp:
                t["law"], t["tau"] = law, noise.effective_tau(law, tau_resid_table(), _tau_key(t["peak"], t["T"], t["P_W"]))
            out.extend(grp)
    if "M" in sessions:
        _, prates = load_t_rates()
        scale, _ = morning_pilot_scale()
        pil = sj.load_session_20250717(prates["4192"][0])
        groups = {}
        for t in pil:
            x = np.asarray(t["x"], float)
            ipk = int(np.argmax(np.asarray(t["v"], float)))
            if min(ipk, x.size - 1 - ipk) < TRUNCATED_EDGE_FRAC * x.size:
                dropped.append(dict(session="M", peak="4192", P_W=float(t["P"]), n=int(x.size),
                                    reason=f"the window ends {min(ipk, x.size - 1 - ipk)} samples from the peak "
                                           f"of {x.size}: a line truncated at its maximum"))
                continue
            d = dict(file=f"M/4192/{int(round(t['P'] * 1e3))}mW/{len(groups.get(t['P'], []))}", role="morning",
                     peak="4192", T=130.0, P_W=float(t["P"]), rate=prates["4192"][0] * scale, session="M",
                     iso=int(K.PEAKS["4192"]["isotope"]), law=None, tau=float("nan"),
                     x=(x - float(t["c0"])) * scale, v=np.asarray(t["v"], float), axis="mhz")
            groups.setdefault(t["P"], []).append(_finish(d))
        for grp in groups.values():
            law = _law_from_traces([t["v"] for t in grp])
            for t in grp:
                t["law"], t["tau"] = law, noise.effective_tau(law, tau_resid_table(), _tau_key(t["peak"], t["T"], t["P_W"]))
            out.extend(grp)
        for d in dropped:
            print(f"  dropped one {d['session']} trace at {d['P_W'] * 1e3:g} mW: {d['reason']}", flush=True)
    return out, dropped


def _load(spec: dict) -> list[dict]:
    """The traces of one design, loaded once per process and keyed on the
    design so two designs in one worker cannot alias: the manifest's traces
    from disk, and the sessions outside the manifest from what the parent
    loaded and handed over."""
    key = json.dumps(dict(files=[r["file"] for r in spec["rows"]], sessions=spec["sessions"]), sort_keys=True)
    if key in _TRACES:
        return _TRACES[key]
    # THIS ROUTE IS DEBT AND IS NAMED AS SUCH. The producer calls
    # `ladder_gate.real_traces` at the top, which the TEXT scan reads as routed file-wide,
    # and then loads its traces here with `ingest.load_trace`, which it does not cover.
    # The runtime refusal added 2026-09-16 caught that the first time the suite ran, which
    # is the whole reason the rule moved from a regex to the loader: one sanctioned call
    # does not sanction a second route in the same file. Routing this line was TRIED and
    # reverted the same hour -- the gate then refuses the producer outright, because the
    # closure's own noiseless rung reads FAIL at a 0.70 per cent recovery with NO NOISE
    # against a tolerance of 0.1, so the committed CSV would stop being reproducible and
    # the gate would stay red on a defect that is real and is not this line's. The entry
    # in `ladder_gate.PREDATES_THE_GATE` carries that reason and the paydown is exactly
    # one thing: make the noiseless closure recover its injected waist.
    from rb5s6s.ingest import load_trace
    out = []
    q_groups: dict = {}
    for r in spec["rows"]:
        t_ms, v = load_trace(C.DATA_RAW_DIR / r["file"])
        nu = (np.asarray(t_ms, float) - float(np.mean(t_ms))) * r["rate"]
        v = np.asarray(v, float)
        # THE OFF-CENTRE-SWEEP MIRROR IS CUT HERE, as every other fitter in this
        # package already cuts it. The triangular sweep's down-ramp re-crosses the
        # line and leaves a mirror about 40 MHz out; docs/DATA.md names the eight
        # canonical RF-off traces that carry one, almost all in 4207, at up to 79
        # per cent of peak, and records that not excluding it took those fits from
        # a reduced chi-squared of 6.7 to 1.0. `linefit.adaptive_halfwidth` and
        # `rb5s6s.beta` obey the rule and THIS PRODUCER DID NOT, which put the
        # whole of the power session's far-wing excess (+142 sigma, of which five
        # 4207 traces carry 100.5 per cent) into a likelihood that read it as
        # physics. Diagnosed 2026-09-16 from the whitened residuals binned by
        # detuning; the account is register entry A264.
        keep = np.abs(nu) <= RETRACE_CUT_MHZ
        nu, v = nu[keep], v[keep]
        t = dict(r, x=nu, v=v, axis="mhz")
        out.append(_finish(t))
        if r["session"] == "Q":
            q_groups.setdefault((r["peak"], r["P_W"]), []).append(t)
    for grp in q_groups.values():
        law = _law_from_traces([t["v"] for t in grp])
        for t in grp:
            t["law"], t["tau"] = law, noise.effective_tau(law, tau_resid_table(), _tau_key(t["peak"], t["T"], t["P_W"]))
    have = {t["session"] for t in _SESSION_TRACES}
    missing = [s for s in spec["sessions"] if s in ("E", "M") and s not in have]
    if missing:
        raise RuntimeError(f"sessions {missing} were asked for but not handed to this process: load_sessions() "
                           f"runs in the parent and run_cells passes its traces to the pool")
    out.extend(t for t in _SESSION_TRACES if t["session"] in spec["sessions"])
    _TRACES[key] = out
    return out


# ------------------------------------------------------------------ the model
def window_profile(w0_m: float, m2: float, power_w: float = None, T_C: float = None, rho: float = None,
                   density=None):
    """The axial collection window as a `profile` closure for model_profile,
    ON at every M2 including exactly 1, memoised on the grid it is asked for.
    The z_ratio is on the closure for the tests.

    THE LOCAL DENSITY IS SATURATED WHEN THE POWER IS GIVEN (F133, PLAN v2 Phase 1, 2026-09-18):
    with `power_w`, `T_C` and `rho` the transverse law is `lineshape.saturated_ramp_density` at
    the trace's own conditions, which is what the kernel gate's nodes are now judged against
    (`run_kernel_mc.py`); without them it is the weak-field triangle, the pre-2026-09-18 form,
    kept for the comparison arm and for callers that carry no power. The Cell builds one per
    trace (`_per_trace`), memoised on its own grid."""
    zr = collection_z_ratio_m2(float(w0_m), float(m2))
    if density is not None:                       # a WORLD's own local density (the mismatch worlds, K5a)
        xg, gx = (np.asarray(density[0], float), np.asarray(density[1], float))
    else:
        xg = np.linspace(0.0, 1.0, 4001)
        if power_w is None:
            gx = local_ramp_density(xg)
        else:
            gx = saturated_ramp_density(xg, float(power_w), float(w0_m), float(T_C), float(rho))
    memo: dict = {}

    def prof(g, s0):
        key = (round(float(s0), 12), int(g.shape[0]), round(float(g[0]), 9), round(float(g[1] - g[0]), 12))
        if key not in memo:
            if len(memo) > 4096:
                memo.clear()
            memo[key] = ramp_mixture(g, s0, zr, xg, gx)
        return memo[key]
    prof.z_ratio = zr
    return prof


def depleted_transit(transit_mhz: float, omega_mhz: float, peak: str, cycles: float) -> float:
    """The transit after pumping depletion through stark.companion_transit_mhz
    at the TIED Omega: the package function multiplies its shift argument by
    its own ratio, so the argument is Omega over that ratio and the Rabi
    frequency it uses is exactly the tied one."""
    if cycles <= 0.0:
        return float(transit_mhz)
    ratio = 1.2511
    stark.COMPANIONS = {"ratio": ratio, "deplete": True, "cycles": float(cycles)}
    try:
        return float(stark.companion_transit_mhz(float(transit_mhz), float(omega_mhz) / ratio, peak))
    finally:
        stark.COMPANIONS = None


_TAU_RESID = None


def tau_resid_table() -> dict:
    """The post-fit residuals' integrated correlation time per condition (F36), the rows
    `tau_resid` of `results/residual_resampling.csv` keyed `<peak>_<T>C_<P>mW`, read once; an
    absent table (the interim before the resampler's regeneration) leaves every producer on the
    raw-segment `tau_int` with `noise.effective_tau`'s printed reason."""
    global _TAU_RESID
    if _TAU_RESID is None:
        _TAU_RESID = {}
        try:
            import csv as _csv
            from rb5s6s import config as _cfg
            with open(os.path.join(str(_cfg.RESULTS_DIR), "residual_resampling.csv"), newline="") as fh:
                for r in _csv.DictReader(fh):
                    if r.get("quantity") == "tau_resid":
                        try:
                            _TAU_RESID[r["key"]] = float(r["value"])
                        except (TypeError, ValueError):
                            pass
        except OSError:
            pass
    return _TAU_RESID


def _tau_key(peak, T, P_W) -> str:
    return f"{peak}_{float(T):.0f}C_{1e3 * float(P_W):.0f}mW"


def _tau_key_of_row(r) -> str:
    """The residual-time key of a noise-model row; None for a pooled row without a condition."""
    try:
        return f"{r['peak']}_{float(r['temperature_C']):.0f}C_{float(r['power_mW']):.0f}mW"
    except (KeyError, TypeError, ValueError):
        return None


class Cell:
    """One (form, M2 arm, depletion arm, propagation arm, w0, fixed terms)
    with its traces. The free parameter list is built from the traces the
    cell holds: a laser width per session (or one shared), a rate per evening
    peak, a power factor per session when asked, minus whatever `fixed` pins."""

    def __init__(self, spec: dict, traces: list[dict]):
        self.spec = spec
        self.form = spec["form"]
        self.kind = "lorentzian" if self.form == "lorentzian" else "gaussian"
        self.w0 = spec["w0_um"] * 1e-6
        self.m2, self.cycles = float(spec["m2"]), float(spec["cycles"])
        # THE DEPLETION FORM AND THE KERNEL GATE (owner, 2026-09-16 22:30; F12, F15). "mc": the
        # transit carries the kernel Monte Carlo's own depletion factor at the trace's node,
        # read through `kernel_gate.depletion_factor`, which REFUSES a node without a passing
        # artefact; "none" and "companion" are the legacy forms, kept for the comparison and
        # still gated. `kernel_gate="legacy"` is the one door, for reproducing a committed CSV
        # that predates the gate, and it is printed once per Cell.
        self.depletion = str(spec.get("depletion", "mc"))
        self.gamma_l_exp = float(spec.get("gamma_l_exp", GAMMA_L_EXP))
        self.kernel_gate = str(spec.get("kernel_gate", "require"))
        # THE READING SET (D1 of PLAN v2, 2026-09-18). This Cell fits one free amplitude, offset and
        # slope per trace (`linear`), so it never reads the amplitude's local power law and the gate is
        # asked for `kernel_gate.WAIST_READINGS`; `spec["readings"] = "all"` asks for every reading, for
        # an analysis that ties amplitudes across powers. Nothing here loosens a tolerance.
        self.readings = None if str(spec.get("readings", "waist")) == "all" else kernel_gate.WAIST_READINGS
        # THE RAMP'S LOCAL DENSITY (F133, PLAN v2 Phase 1): "saturated" builds the transverse law from
        # the trace's own power through `lineshape.saturated_ramp_density`, which is what the kernel
        # nodes are judged against; "weak" is the triangle, the pre-2026-09-18 form, the comparison arm.
        self.ramp = str(spec.get("ramp", "saturated"))
        if self.kernel_gate == "legacy" and not spec.get("_legacy_said"):
            print("  Cell: kernel gate LEGACY, no node validated (reproduction of a pre-gate CSV only)", flush=True)
            spec["_legacy_said"] = True
        da, da_err = spec["delta_alpha"], spec["delta_alpha_err"]
        self.delta_alpha, self.rho, law = da, RHO, "AIH"
        prop = spec.get("propagation")
        if prop is not None:
            what, val = prop
            if what == "delta_alpha":
                self.delta_alpha = da + val * da_err
            elif what == "rho":
                self.rho = RHO + val * RHO_ERR        # the owner's 0.94 +- 0.04
            elif what == "rho_floor":
                self.rho = 0.80                       # "very surprised in case it is below 0.8"
            elif what == "law":
                law = val
        self.law_name = law
        # F280: self.w0 IS the actual (same-reading) focus, the one the transit above already
        # reads, so the on-axis factor is the ACTUAL-convention one and not the free-focus
        # `aperture_onaxis_factor`. Cached once here rather than inside `_per_trace` (F280's own
        # closing line: a node validated on the wrong S0 certifies the wrong model), because that
        # method runs once per trace at this Cell's one fixed w0 -- a hundred-plus identical calls
        # to a table lookup cost nothing, but the table's own first build should happen once, not
        # be paid down the trace list.
        # NO CLAMP (C6a, 2026-09-22, replacing the clamp of 2026-09-21): a Cell below the bore's floor
        # (about 40.89 um) would carry the floor's on-axis factor beside its OWN narrower transit, a
        # beam this bench cannot make. The grids start at the floor instead (W0_GRID_UM above, the
        # closure's GRID_UM and GRID_NOISELESS), so a Cell below it is a defect and refuses.
        # `spec["aperture_clamp_floor"]` (a DIAGNOSTIC, never a production fit): below the floor the on-axis factor
        # is held at the floor's, so a Gaussian-beam fitter can be walked where a world it cannot describe pushes it
        # (C6b D3, the clipped focus), and the size of that push is read instead of a rail at the floor.
        # m2=self.m2 (C6c): this Cell's own clipped beam (`self._clipped_beam`, built below with the
        # same m2) is what a `VolumeWorld` reads its on-axis factor from, and an M2 > 1 beam focuses
        # less tightly than a diffraction-limited one through the same bore, so leaving this at the
        # implicit M2=1 default disagreed with that beam by 0.42 per cent at m2=1.3 while agreeing
        # to rel=1e-12 at m2=1.0 (tests/test_volume_world.py's own two-m2 sweep found it).
        self.aperture_onaxis = aperture_onaxis_factor_actual(
            self.w0, clamp_floor=bool(spec.get("aperture_clamp_floor", False)), m2=self.m2)
        # THE BORE-CLIPPED BEAM, BUILT ONCE (F471, plan item V5.19a): _per_trace's transit reads
        # it through beam_field.clipped_transit_fwhm_mhz instead of the free-space
        # transit_collection_factor alone, closing the 3.3 to 4.6 per cent narrow reading F471
        # measured against the kernel Monte Carlo at M2 = 1. A waist this bore and lens cannot
        # produce (BF.ClippedBeam.at_focus raises for one) falls back to None, which leaves the
        # correction at one and reproduces the old free-space-only number exactly -- the same
        # fallback scripts/run_kernel_mc.py's own _beam_for already takes for the same reason.
        try:
            self._clipped_beam = BF.ClippedBeam.at_focus(self.w0, m2=self.m2)
        except ValueError:
            self._clipped_beam = None
        self.profile = window_profile(self.w0, self.m2)
        self.z_ratio = self.profile.z_ratio
        self.traces = traces
        self.beta_theory_mhz = BETA_THEORY_KHZ * 1e-3
        self.sessions = sorted({t["session"] for t in traces}, key=list(SESSIONS).index)
        self.shared_sigma = spec.get("sigma_l", "session") == "shared"
        # THE LOG-DETERMINANT (2026-09-16). `linear` sets sigma from the FITTED level, so the
        # objective's weights depend on the parameters and the sum of squares alone is not a
        # likelihood: -2 ln L = sum r^2/sigma^2 + sum ln sigma^2 (the rule file: "an objective whose
        # weights depend on its own parameters is not a likelihood until its log-determinant is
        # carried"). Measured at the fixed truth across the noiseless grid, the term moves by
        # 358 per micron near 52 um, nine times the archive-rung rail. With `logdet` on, the term
        # rides as ONE extra residual sqrt(sum ln sigma^2 / tau + LOGDET_OFFSET), whose square adds
        # the term to the sum of squares up to a constant that moves no minimum; `chi2_parts`
        # returns the three blocks so a closure judges a rung on the DATA block alone.
        self.logdet = bool(spec.get("logdet", False))
        # THE WHITENING FOLLOWS THE NOISE THAT IS THERE (2026-09-16, F7): a closure rung at scale s
        # injects s times the law, so its objective whitens at s times the law too, or every bar
        # below the archive's rung is too small by s and a log-determinant at the wrong scale
        # rewards whatever shrinks sigma (42.2 um for an injected 52 at zero noise). Real data and
        # the archive rung sit at 1.0; the noiseless rung passes 1.0 for its data term and carries
        # no log-determinant, which is undefined at zero noise.
        self.noise_scale = float(spec.get("noise_scale", 1.0))
        self.power_scale = bool(spec.get("power_scale", False))
        self.evening_peaks = sorted({t["peak"] for t in traces if t["session"] == "E"})
        self.rate_seed = {pk: spec.get("rate_seeds", {}).get(pk, EVENING_RATE_SEED) for pk in self.evening_peaks}
        names = ["beta_rel", "alpha_rel"]
        names += ["sigma_l_shared"] if self.shared_sigma else [f"sigma_l_{s}" for s in self.sessions]
        names += ["omega_scale"]
        if self.form == "mixed":
            names.append("gamma_l")
        # F465: the retro tilt as a fitted nuisance, opt-in and off by default so every existing
        # Cell is unaffected; when it is not free, physics() still passes RETRO_TILT_START (see
        # unpack()) rather than leaving the term out of the full_profile call altogether.
        if spec.get("retro_tilt_free"):
            names.append("retro_tilt_rad")
        self.conditions = sorted({self._condition_key(t) for t in traces})
        if spec.get("s0_free"):
            names += [f"s0_scale_{c}" for c in self.conditions]
        if spec.get("w0_free"):
            names += ["w0_transit_rel", "w0_shift_rel", "w0_sat_rel"]
        names += [f"lograte_E_{pk}" for pk in self.evening_peaks]
        if self.power_scale:
            names += [f"power_scale_{s}" for s in self.sessions]
        self.fixed = dict(spec.get("fixed", {}))
        self.names = tuple(n for n in names if n not in self.fixed)
        self.all_names = tuple(names)
        # THE VOLUME LINE (C6b item 2, owner orders O45 and O46): `spec["volume_line"]` (a dict of the table's
        # settings, or True for the defaults) makes the line the atom Monte Carlo's joint line of shift and
        # transit, tabulated at this Cell's waist per temperature and isotope (`volume_line.JointTable`), in
        # place of the transit and ramp convolution. The table is weak-field and undepleted, so a Cell that
        # carries the saturated ramp or the transit's depletion, or floats separate waist meters that one
        # table cannot separate, is refused rather than silently half-converted.
        vol = spec.get("volume_line")
        self.volume = None
        if vol:
            bad = [why for cond, why in ((self.ramp != "weak", "ramp='saturated'"),
                                         (self.depletion != "none", f"depletion={self.depletion!r}"),
                                         (bool(spec.get("w0_free")), "w0_free"))
                   if cond]
            if bad:
                raise ValueError("volume_line: the joint table is weak-field and holds one beam, so it cannot carry "
                                 + ", ".join(bad) + "; build the Cell with ramp='weak' and depletion='none'")
            v = dict(VOLUME_DEFAULTS, **(vol if isinstance(vol, dict) else {}))
            self.volume = v
            self._tables: dict = {}
            from rb5s6s.volume_line import GaussianBeam, collection_half_window_m
            # gaussian-limit: the collection window's axial extent read from the free-space Rayleigh range; the bore's axial width is the registry's owed collection-window-in-fitter
            self._half_window_m = collection_half_window_m(GaussianBeam(self.w0, self.m2), self.z_ratio)
        self.per = [self._per_trace(t) for t in traces]
        # ALPHA AND BETA ENTER UNDER THEIR OWN THEORY UNCERTAINTIES, not pinned and
        # not free (owner, 2026-09-16: "you have to do it with alpha jointly at the
        # same time, considering their uncertainty in the MLE ultra-joint"). Pinning
        # is infinitely stiff and makes the quantity do the model's work for it;
        # free is unpenalised and lets beta run from 0 to 5x theory, which is what
        # every committed grid row shows. A prior with the record's own bar is the
        # construction between them, and it makes the owner's iteration unnecessary:
        # the posterior reports how far the archive pulls against theory instead of
        # the convener deciding by pinning.
        self.prior_terms = [t for t in [("omega_scale", 1.0, OMEGA_PRIOR_FRAC),
                                        ("beta_rel", 1.0, BETA_PRIOR_FRAC),
                                        ("alpha_rel", 1.0, ALPHA_PRIOR_FRAC)] + [
            (f"power_scale_{s}", 1.0, POWER_PRIOR_FRAC) for s in self.sessions if self.power_scale]
                            # a PINNED parameter carries no prior term (owner, 2026-09-17 00:30): its
                            # theory uncertainty is a systematic band read by displacing the pin, never a
                            # pull on the objective, and a term evaluated at a fixed value is a constant
                            if t[0] not in self.fixed]

    # -- parameters -------------------------------------------------------
    @staticmethod
    def _condition_key(t) -> str:
        return f"{t['session']}_{t['peak']}_{1e3 * t['P_W']:.0f}mW_{t['T']:.0f}C"

    def bounds(self, name):
        for k in ("beta_rel", "alpha_rel", "sigma_l", "omega_scale", "gamma_l", "lograte", "power_scale",
                  "s0_scale", "w0_", "retro_tilt_rad"):
            if name.startswith(k):
                return BOUNDS[k]
        raise KeyError(name)

    def starts(self):
        """Two starts spanning the model: the second at a large beta, a low
        Omega scale and a small gamma_l."""
        out = []
        for i in range(2):
            p = []
            for n in self.names:
                if n == "beta_rel":
                    p.append(START_OTHER[i][0])
                elif n == "alpha_rel":
                    # BOTH STARTS AT THEORY. The prior is 0.52 per cent wide, so a
                    # start away from 1.0 explores nothing the penalty allows and
                    # only costs evaluations; the two starts differ where the
                    # likelihood is actually multimodal, which is beta and sigma_l.
                    p.append(1.0)
                elif n.startswith("sigma_l"):
                    p.append(START_SIGMA_L[self.form][i])
                elif n == "omega_scale":
                    p.append(START_OTHER[i][1])
                elif n == "gamma_l":
                    p.append(START_OTHER[i][2])
                elif n.startswith("lograte_E_"):
                    p.append(0.0)
                elif n.startswith("power_scale_"):
                    p.append(1.0)
                elif n.startswith("s0_scale_") or n.startswith("w0_"):
                    p.append(1.0)
                elif n == "retro_tilt_rad":
                    p.append(RETRO_TILT_START)
            out.append(tuple(p))
        return out

    def unpack(self, p) -> dict:
        d = dict(zip(self.names, p))
        d.update(self.fixed)
        d.setdefault("gamma_l", 0.0)
        d.setdefault("alpha_rel", 1.0)
        # F465: the record's central value (FIT_TERMS's own start, 0.0: no reading assigns the
        # retro tilt a nonzero one) when spec["retro_tilt_free"] did not make it a free name.
        d.setdefault("retro_tilt_rad", RETRO_TILT_START)
        return d

    def _per_trace(self, t):
        # THE COLLECTED COLUMN'S WINDOW FACTOR (F12): the kernel the detector sees is the
        # signal-weighted mixture over the column, narrower than the closed form at the waist by
        # <w^-3>/<w^-2> (small at the retired waist convention); the ramp carried this mixture and the transit did not.
        # THE BEAM'S OWN AXIAL WIDTH (F374, F471, plan item V5.19a): w0 over its effective transit
        # radius, weighted as the chord signal is, through the one function
        # scripts/run_kernel_mc.py's own gate reference calls too. `rate=None` (the default) keeps
        # this on the same unsaturated two-photon slice law transit_collection_factor already used
        # alone; the Cell has no ready route to the Monte Carlo's own saturated chord rate, and the
        # gap that leaves against it is measured rather than closed silently.
        bare = BF.clipped_transit_fwhm_mhz(self.w0, self.m2, t["T"], isotope=t["iso"], beam=self._clipped_beam)
        if self.kernel_gate == "legacy":
            dep = 1.0
        else:
            dep = kernel_gate.depletion_factor(self.w0 * 1e6, t["peak"], self.m2, self.rho, float(t["T"]), t["P_W"] * 1e3,
                                               readings=self.readings)
            if self.depletion != "mc":
                dep = 1.0                          # the node is still required; the factor is the form's
        # A WORLD'S OWN INGREDIENTS (PLAN v2 Phase 5a, the mismatch worlds): `spec["world_density"]`
        # is a (x_grid, g_x) local density that replaces the model's, `spec["transit_scale"]` multiplies
        # the bare transit; both default to nothing and exist so a TWIN can be generated from a
        # world the fit's model is not (the clipped focus), never for fitting real traces.
        wd = self.spec.get("world_density")
        prof = (window_profile(self.w0, self.m2, density=wd) if wd is not None
                else window_profile(self.w0, self.m2, t["P_W"], float(t["T"]), self.rho) if self.ramp == "saturated"
                else self.profile)
        bare = bare * float(self.spec.get("transit_scale", 1.0))
        return dict(transit=bare, dep=dep, cond=self._condition_key(t), profile=prof,
                    # F280: the meter reads behind the cell, so the recorded watt buys the clipped
                    # focus's on-axis intensity AT THE SAME READING self.w0 already is (the ACTUAL
                    # focus, cached once in __init__ as self.aperture_onaxis -- not the free-focus
                    # convention this line called until 2026-09-21, which read S0 about 20 per
                    # cent low at the bore-limited central value)
                    s0=stark_shift_S0_mhz(t["P_W"], self.w0, rho=self.rho, delta_alpha_au=self.delta_alpha)
                       * self.aperture_onaxis,
                    # F324/A134 (C6b): the reference Rabi frequency the saturation companion is
                    # evaluated at becomes the ENSEMBLE-EFFECTIVE one, not the on-axis one the fitter
                    # used to carry. two_photon_rabi_hz(self.w0) is the UNCLIPPED focus's Rabi
                    # frequency (F324 addendum e). The bore's on-axis factor (self.aperture_onaxis,
                    # already cached above at this Cell's one w0, the same actual-reading convention
                    # F280 gives the shift) reads it down to the clipped beam's on-axis value, a
                    # linear correction because the two-photon Rabi frequency is itself linear in
                    # intensity. `bloch_fraction` then reads the steady-state-times-transient share
                    # the collected ensemble actually carries off `sat_fraction_table.tsv`. The prior
                    # `omega_scale = 1 +- 0.20` keeps its meaning around THIS reference (F324's own
                    # point: at omega_scale 1 evaluated on the old on-axis reference, the fitter's
                    # saturation overshot the Bloch line by 3 to 13 archive sd).
                    omega_ref=(two_photon_rabi_hz(t["P_W"], self.w0, self.rho) / 1e6
                              * self.aperture_onaxis * bloch_fraction(
                                  self.w0 * 1e6, float(t["T"]),
                                  clamp=bool(self.spec.get("bloch_fraction_clamp", False)))),
                    n12=float(LAWS[self.law_name](np.array([t["T"]]))[0]) / 1e12,
                    sess=t["session"], peak=t["peak"], axis=t.get("axis", "mhz"),
                    T_K=float(t["T"]) + 273.15, T_C=float(t["T"]), iso=int(t["iso"]))

    def sigma_l_of(self, d, sess):
        return d["sigma_l_shared"] if self.shared_sigma else d[f"sigma_l_{sess}"]

    def power_factor(self, d, sess):
        return d.get(f"power_scale_{sess}", 1.0) if self.power_scale else 1.0

    def axis(self, d, t):
        """The trace's frequency axis under the current parameters."""
        if t.get("axis", "mhz") == "ms":
            return t["x"] * (self.rate_seed[t["peak"]] * math.exp(d[f"lograte_E_{t['peak']}"]))
        return t["x"]

    def _table(self, per):
        """The joint table this trace reads: one per temperature and isotope, at this Cell's waist, its S0 axis
        covering every shift the Cell's free parameters can reach at those conditions, and its detuning axis
        every trace's. Built once and stored (`JointTable.cached`), so the Cells of one waist share it."""
        from rb5s6s.volume_line import JointTable
        key = (per["T_C"], per["iso"])
        tab = self._tables.get(key)
        if tab is not None:
            return tab
        v = self.volume
        mine = [q for q in self.per if (q["T_C"], q["iso"]) == key]
        reach = max(float(np.max(np.abs(t["x"]))) for t in self.traces) if all(
            t.get("axis", "mhz") == "mhz" for t in self.traces) else float(v["reach_mhz"])
        grow = ((BOUNDS["alpha_rel"][1] if "alpha_rel" in self.names else float(self.fixed.get("alpha_rel", 1.0)))
                * (BOUNDS["power_scale"][1] if self.power_scale else 1.0)
                * (BOUNDS["s0_scale"][1] if any(n.startswith("s0_scale") for n in self.names) else 1.0))
        s0_hi = grow * max(q["s0"] for q in mine) * (1.0 + float(v["s0_margin"]))
        step = float(v["s0_step_mhz"])
        S0 = np.arange(0.0, s0_hi + step, step)
        half = int(np.ceil((reach + float(v["delta_margin_mhz"])) / float(v["delta_step_mhz"])))
        delta = np.linspace(-half * float(v["delta_step_mhz"]), half * float(v["delta_step_mhz"]), 2 * half + 1)
        factory, tag = None, ""
        if v["beam"] == "clipped":           # the bench's bore-clipped focus, built to read this Cell's waist (D3)
            from rb5s6s.beam_field import ClippedBeam
            factory, tag = (lambda w0_m: ClippedBeam.at_focus(float(w0_m), m2=self.m2)), f"clipped:m2={self.m2}"
        elif v["beam"] != "gaussian":
            raise ValueError(f"volume_line beam {v['beam']!r}: 'gaussian' or 'clipped'")
        tab = JointTable.cached(v["cache_dir"], tag=tag, S0_grid=S0, w0_grid=np.array([self.w0]), delta_mhz=delta,
                                m2=self.m2, T_C=float(per["T_C"]), n_path=int(v["n_path"]), seed=int(v["seed"]),
                                half_window_m=float(self._half_window_m), isotope=int(per["iso"]),
                                beam_factory=factory)
        self._tables[key] = tab
        return tab

    def physics(self, d, per, peak, sess) -> dict:
        """The line's physical inputs for one trace at the parameters `d`, as `full_profile`'s own
        keywords. The ONE place this Cell maps its parameters onto physics (C6b, 2026-09-22): `model`
        passes them to `full_profile`, and a twin world that draws the same trace from the atom
        Monte Carlo (`run_ultra_joint_closure.VolumeWorld`) reads the same numbers here, so the two
        cannot drift apart through a second copy of this arithmetic."""
        f = self.power_factor(d, sess)
        omega_ref = f * per["omega_ref"]
        omega = d["omega_scale"] * omega_ref * d.get("w0_sat_rel", 1.0) ** -2
        # THE DEPLETION ARM IS A MODEL FORM AND NOT A FIT PARAMETER: it takes
        # the tied Omega at its theory scale, so a fit that pulls the
        # saturation scale toward zero cannot switch the arm off as well.
        transit = (depleted_transit(per["transit"], omega_ref, peak, self.cycles) if self.depletion == "companion"
                   else per["transit"] * per["dep"]) / d.get("w0_transit_rel", 1.0)
        out = dict(gamma_coll=d["beta_rel"] * self.beta_theory_mhz * per["n12"],
                   sigma_laser_fwhm=self.sigma_l_of(d, sess), transit_fwhm=transit,
                   s0=f * d["alpha_rel"] * per["s0"] * d.get(f"s0_scale_{per['cond']}", 1.0) * d.get("w0_shift_rel", 1.0) ** -2,
                   gamma_l=d["gamma_l"] * (per["T_K"] / GAMMA_L_T_REF_K) ** self.gamma_l_exp,
                   laser_kind=self.kind, peak=peak,
                   omega_mhz=omega, profile=per.get("profile", self.profile),
                   # F465: neither term was passed before this change (the module docstring's own
                   # term table called both "dropped"); the pedestal is the record's fixed
                   # convention height, the tilt is d["retro_tilt_rad"] (unpack()'s own default or
                   # the fitted value when spec["retro_tilt_free"] is set).
                   pedestal_height_frac=PEDESTAL_HEIGHT_FRAC, retro_tilt_rad=d["retro_tilt_rad"])
        if self.volume is not None:
            # the table carries the transit and the ramp together, so neither is passed beside it
            del out["profile"]
            out.update(transit_fwhm=None, volume_table=self._table(per), w0_m=self.w0, m2=self.m2,
                       T_C=float(per["T_C"]), isotope=int(per["iso"]))
        return out

    def model(self, nu, d, per, peak, sess):
        return full_profile(nu, **self.physics(d, per, peak, sess))

    def linear(self, t, nu, m):
        """Amplitude, offset and slope by weighted least squares under the
        condition's law at the fitted level. Returns (chi2 whitened, residuals
        whitened)."""
        A = np.column_stack([m, t["ones"], nu])
        c0, *_ = np.linalg.lstsq(A, t["v"], rcond=None)
        level = np.clip(c0[0] * m, 0.0, None)
        s = np.asarray(sigma_of_v(level, t["law"]), float) * self.noise_scale
        cf, *_ = np.linalg.lstsq(A / s[:, None], t["v"] / s, rcond=None)
        r = (t["v"] - A @ cf) / s / math.sqrt(t["tau"])
        return float(r @ r), r

    def logdet_of(self, t, nu, m) -> float:
        """sum ln sigma^2 over the trace's samples, each counted 1/tau, at the level `linear` uses."""
        A = np.column_stack([m, t["ones"], nu])
        c0, *_ = np.linalg.lstsq(A, t["v"], rcond=None)
        s = np.asarray(sigma_of_v(np.clip(c0[0] * m, 0.0, None), t["law"]), float) * self.noise_scale
        return float(np.sum(np.log(s * s))) / float(t["tau"])

    def chi2_parts(self, p, centres) -> dict:
        """The objective split into its blocks: data (whitened residual sum), prior, logdet."""
        d = self.unpack(p)
        data = ld = 0.0
        for i, t in enumerate(self.traces):
            nu = self.axis(d, t)
            m = self.model(nu - centres[i], d, self.per[i], t["peak"], t["session"])
            data += self.linear(t, nu, m)[0]
            ld += self.logdet_of(t, nu, m)
        prior = float(sum(((d[n] - mu) / sig) ** 2 for n, mu, sig in self.prior_terms if n in d))
        return {"data": data, "prior": prior, "logdet": ld, "logdet_on": self.logdet}

    def chi2_at(self, i, p, c):
        t, per = self.traces[i], self.per[i]
        d = self.unpack(p)
        nu = self.axis(d, t)
        m = self.model(nu - c, d, per, t["peak"], t["session"])
        return self.linear(t, nu, m)[0]

    def moment_arm(self, p, centres):
        """Windowed cumulants 2 to 7 per CONDITION, data against this fit's own
        prediction, with the covariance built from the repeats (owner O12).

        WHAT IT COMPARES, and the distinction is the reason the arm exists. A
        windowed cumulant is a SUMMARY STATISTIC matched against its own forward
        prediction, never an estimator of an untruncated ramp cumulant: the
        windowed fifth of a Lorentzian-cored line diverges as the window widens
        and that is a property of the window. So every row here is
        (data - model) at the SAME window, and nothing is extrapolated.

        THE COVARIANCE IS DIAGONAL AND SAYS SO. A condition carries five
        repeats, so a p x p covariance over 18 statistics is singular by
        construction and any interval through its pseudo-inverse is an artefact.
        What five repeats CAN estimate is a per-statistic spread, with about
        four degrees of freedom, so the bar on the mean carries a t-factor and
        the row states it. Pooling across conditions is the caller's job and is
        not done here, because the statistics are not exchangeable across
        temperature.

        ADMISSION IS BY THE REPLICA DISTRIBUTION AND NEVER BY SIGNAL-TO-NOISE
        (O17). A cross-rung ratio enters only where its denominator keeps one
        sign across the repeats: a denominator that crosses zero makes the ratio
        Cauchy-like, with no population mean for a pull to be computed against.
        Everything else enters, whatever its size.
        """
        d = self.unpack(p)
        conds: dict = {}
        for i, t in enumerate(self.traces):
            conds.setdefault((t["session"], t["peak"], round(float(t["P_W"]) * 1e3),
                              round(float(t["T"]))), []).append(i)
        out = []
        for key, idx in sorted(conds.items()):
            sess, peak, p_mw, t_c = key
            per_trace, per_model = [], []
            for i in idx:
                t, per = self.traces[i], self.per[i]
                nu = self.axis(d, t)
                m = self.model(nu - centres[i], d, per, t["peak"], t["session"])
                # THE BASELINE IS FITTED, NOT STRIPPED, and the amplitude with
                # it: the same three-column solve the likelihood already does,
                # so the statistic is taken on the trace this fit actually
                # describes rather than on one a wing strip has biased.
                A = np.column_stack([m, t["ones"], nu])
                c0, *_ = np.linalg.lstsq(A, t["v"], rcond=None)
                s_v = np.asarray(sigma_of_v(np.clip(c0[0] * m, 0.0, None), t["law"]), float)
                cf, *_ = np.linalg.lstsq(A / s_v[:, None], t["v"] / s_v, rcond=None)
                if not (cf[0] > 0):
                    continue
                y = (t["v"] - cf[1] * t["ones"] - cf[2] * nu) / cf[0]
                per_trace.append(_moment_stats(nu - centres[i], y, windows=MOMENT_WINDOWS + DIAGNOSTIC_WINDOWS))
                # THE MODEL IS AVERAGED OVER THE REPEATS TOO. Each repeat has its
                # own centre and its own grid, so the model's windowed cumulant
                # differs across them; taking the first and discarding four put
                # that difference into every one of the condition's statistics as
                # a COMMON OFFSET -- the block-systematic signature, manufactured
                # inside the producer that went looking for it.
                per_model.append(_moment_stats(nu - centres[i], m, windows=MOMENT_WINDOWS + DIAGNOSTIC_WINDOWS))
            if len(per_model) < 1 or len(per_trace) < 2:
                continue
            pred = {k: float(np.mean([pm[k] for pm in per_model])) for k in per_model[0]}
            n_rep = len(per_trace)
            tfac = _T95.get(n_rep - 1, 2.0)
            # THE TWIN'S BIAS, SUBTRACTED ONCE AND WRITTEN BESIDE THE RESULT (PLAN v2 Phase 2, the
            # main aim's "using the twin to compute and factor out biases"). `spec["twin_bias"]` is a
            # `rb5s6s.twin_bias.TwinBias` over the window surface at THIS fit's noise level; a cell the
            # surface lacks RAISES here, in the producer, and is never read as zero.
            tb = self.spec.get("twin_bias")
            case = f"{sess}_{peak}_{p_mw}mW_{t_c}C"
            for k in sorted(pred):
                vals = np.array([r[k] for r in per_trace], float)
                if not np.all(np.isfinite(vals)):
                    continue
                # THE NUMERICAL FLOOR (F144, 2026-09-19): a moment of order n is a small difference of large
                # numbers to the n-th power, and mu7@13 read 6.6e-07 of its own dimensional scale mu2^(n/2) with
                # the fit exact -- both sides reporting the fit's residual, not the line. A row whose model
                # sits under the floor is REFUSED with the reason, never admitted as a measurement. A window
                # in DIAGNOSTIC_WINDOWS is refused as a measurement whatever its floor, with its reason.
                _ord, _win = (re.match(r"mu(\d+)@(.+)$", k).groups()
                               if re.match(r"mu\d+@", k) and "/" not in k else (None, None))
                if _ord is not None:
                    # A HARD LOOKUP ON THE EMITTER'S OWN KEY (2026-09-21, F264): `.get("k2@W", 0.0)` read
                    # zero on every row since the mu rename, so `_scale` was 0, `_rel` inf, and EVERY
                    # moment was refused on the floor with no error raised. mu2 is k2 identically.
                    _n = int(_ord); _mu2 = abs(float(pred[f"mu2@{_win}"]))
                    _scale = _mu2 ** (_n / 2.0) if _mu2 > 0 else 0.0
                    _rel = abs(pred[k]) / _scale if _scale > 0 else float("inf")
                    _why = None
                    if float(_win) in DIAGNOSTIC_WINDOWS:
                        _why = (f"a DIAGNOSTIC window: {_win} MHz shows where the channel dies (the SNR peak at 3, "
                                f"k4's zero at 8, k6's collapse at 21) and is never quoted as a measurement")
                    elif _n > 2 and _rel < CUMULANT_FLOOR_REL:
                        _why = (f"the model's {k} is {_rel:.2g} of its own scale mu2^{_n / 2:g}, under the floor "
                                f"{CUMULANT_FLOOR_REL:g} = the arm's precision over the noiseless tolerance: "
                                f"below what the arithmetic can resolve, not a channel")
                    if _why:
                        _mu = float(vals.mean())
                        out.append(dict(session=sess, peak=peak, p_mw=p_mw, t_c=t_c, statistic=k, n_rep=n_rep,
                                        data=_mu, sem=float(vals.std(ddof=1)) / math.sqrt(n_rep), t95=tfac,
                                        model=pred[k], pull=float("nan"), twin_bias=0.0, twin_bias_se=0.0,
                                        admitted=False, why=_why))
                        continue
                mu, sd = float(vals.mean()), float(vals.std(ddof=1))
                sem = sd / math.sqrt(n_rep)
                b, b_se = (tb.bias(case, k, float(self.noise_scale)) if tb is not None else (0.0, 0.0))
                mu_c, sem_c = mu - b, math.sqrt(sem * sem + b_se * b_se)
                pull = (mu_c - pred[k]) / sem_c if sem_c > 0 else float("nan")
                out.append(dict(session=sess, peak=peak, p_mw=p_mw, t_c=t_c,
                                statistic=k, n_rep=n_rep, data=mu_c, sem=sem_c,
                                t95=tfac, model=pred[k], pull=pull,
                                twin_bias=b, twin_bias_se=b_se,
                                admitted=True, why=""))
            # CROSS-RUNG RATIOS, admitted on having a population moment
            # THE PLAIN ROWS' OWN VERDICTS, so a ratio never admits a member the floor refused: the moments
            # ladder's stage 0 read 0.284 on k7/k5@13 with k7@13 itself refused, because this loop had its
            # own admission and consulted nobody (2026-09-19, the second half of F144's repair). The
            # diagnostic windows are walked too, and refused as diagnostics through their members.
            _refused_plain = {r_["statistic"]: r_["why"] for r_ in out
                              if r_["session"] == sess and r_["peak"] == peak and r_["p_mw"] == p_mw
                              and r_["t_c"] == t_c and not r_["admitted"] and "/" not in r_["statistic"]}
            for w in MOMENT_WINDOWS + DIAGNOSTIC_WINDOWS:
                for lo in MOMENT_ORDERS:
                    hi = lo + 2
                    if hi not in MOMENT_ORDERS:
                        continue
                    _member = next((k_ for k_ in (f"mu{hi}@{w:g}", f"mu{lo}@{w:g}") if k_ in _refused_plain), None)
                    if _member is not None:
                        out.append(dict(session=sess, peak=peak, p_mw=p_mw, t_c=t_c,
                                        statistic=f"mu{hi}/mu{lo}@{w:g}", n_rep=n_rep, data=float("nan"),
                                        sem=float("nan"), t95=tfac, model=float("nan"), pull=float("nan"),
                                        admitted=False,
                                        why=f"its member {_member} is refused: {_refused_plain[_member]}"))
                        continue
                    den = np.array([r[f"mu{lo}@{w:g}"] for r in per_trace], float)
                    num = np.array([r[f"mu{hi}@{w:g}"] for r in per_trace], float)
                    flips = min(int((den > 0).sum()), int((den < 0).sum()))
                    name = f"mu{hi}/mu{lo}@{w:g}"
                    # THE MODEL'S KEY IS THE EMITTER'S (2026-09-21, K-C's first cell raised KeyError 'k2@1'):
                    # the prediction is keyed `mu` since O33 and this admission still asked for `k`, the
                    # half-switched likelihood A72 warned of. The exact-zero test stays T0ad's (E71).
                    if flips > 0 or pred[f"mu{lo}@{w:g}"] == 0.0:
                        out.append(dict(session=sess, peak=peak, p_mw=p_mw, t_c=t_c,
                                        statistic=name, n_rep=n_rep, data=float("nan"),
                                        sem=float("nan"), t95=tfac, model=float("nan"),
                                        pull=float("nan"), admitted=False,
                                        why=f"the denominator changes sign in {flips} of "
                                            f"{n_rep} repeats, so the ratio has no "
                                            f"population moment"))
                        continue
                    # AN ADJACENT ODD-ODD RATIO IS MINUS TEN mu2 PLUS A REMAINDER,
                    # and the remainder is the only part that is about the
                    # asymmetry: kappa5/mu3 = mu5/mu3 - 10 mu2 exactly, so
                    # a fit reading mu5/mu3 beside mu2 reads mu2 twice. The row
                    # carries the mu2 term so a reader can subtract it rather
                    # than discover the identity later.
                    rat = num / den
                    mu, sd = float(rat.mean()), float(rat.std(ddof=1))
                    sem = sd / math.sqrt(n_rep)
                    # THE MODEL SIDE THROUGH THE DATA SIDE'S FUNCTIONAL (F144's second half): the data is
                    # the MEAN OF PER-REPEAT RATIOS, so the model is too, not the ratio of the means --
                    # two different functionals that disagree by a Jensen gap of about 4e-4 at zero noise.
                    _pm_per = [pm_[f"mu{hi}@{w:g}"] / pm_[f"mu{lo}@{w:g}"] for pm_ in per_model
                               if pm_[f"mu{lo}@{w:g}"] != 0.0]
                    pm = float(np.mean(_pm_per)) if _pm_per else pred[f"mu{hi}@{w:g}"] / pred[f"mu{lo}@{w:g}"]
                    mu2_term = -10.0 * pred[f"mu2@{w:g}"] if lo % 2 else None   # mu2 = kappa2 exactly
                    out.append(dict(session=sess, peak=peak, p_mw=p_mw, t_c=t_c,
                                    statistic=name, n_rep=n_rep, data=mu, sem=sem,
                                    t95=tfac, model=pm,
                                    pull=(mu - pm) / sem if sem > 0 else float("nan"),
                                    admitted=True,
                                    why=("" if mu2_term is None else
                                         f"an odd-odd adjacent ratio: -10*mu2 = {mu2_term:.4g} "
                                         f"of this is mu2 and not the asymmetry")))
        return out

    @staticmethod
    def _parabola(x, y):
        j = int(np.argmin(y))
        if 0 < j < len(x) - 1:
            den = y[j - 1] - 2.0 * y[j] + y[j + 1]
            if den > 0:
                v = x[j] + 0.5 * (y[j - 1] - y[j + 1]) / den * (x[j + 1] - x[j])
                return float(np.clip(v, x[j - 1], x[j + 1]))
        return float(x[j])

    def centre(self, i, p, c_prev=None):
        """The profiled centre of one trace: a coarse scan over +-5 MHz on the
        first call, a medium step, then a fine three-node parabola about the
        previous centre, re-centred while its vertex sits on an edge node."""
        c = c_prev
        if c is None:
            grid = np.linspace(-5.0, 5.0, 11)
            c = self._parabola(grid, [self.chi2_at(i, p, g) for g in grid])
            mid = c + np.array([-0.5, 0.0, 0.5])
            c = self._parabola(mid, [self.chi2_at(i, p, g) for g in mid])
        for _ in range(3):
            fine = c + np.array([-CENTRE_FINE_MHZ, 0.0, CENTRE_FINE_MHZ])
            vals = [self.chi2_at(i, p, g) for g in fine]
            c2 = self._parabola(fine, vals)
            if abs(c2 - c) < 0.999 * CENTRE_FINE_MHZ:
                break
            c = c2
        f2 = self.chi2_at(i, p, c2)
        if f2 > min(vals):
            c2, f2 = float(fine[int(np.argmin(vals))]), float(min(vals))
        return c2, f2

    def residuals(self, p, centres):
        d = self.unpack(p)
        parts = []
        for i, t in enumerate(self.traces):
            nu = self.axis(d, t)
            m = self.model(nu - centres[i], d, self.per[i], t["peak"], t["session"])
            parts.append(self.linear(t, nu, m)[1])
        # A PROFILE LIKELIHOOD CARRIES THE SAME OBJECTIVE AT EVERY POINT, and this
        # line read `if n in self.names`, which DROPS a parameter's prior the moment
        # that parameter is PINNED. The beta profile pins beta_rel, so every profile
        # point was scored without the beta prior while the free fit paid it, and the
        # two chi2 were not the same statistic. The gap is exactly the penalty:
        # ((beta-1)/0.1064)^2 is 88 at beta 0, 1413 at 5x, and the gate's
        # "the free fit is the beta profile's minimum" read 1171.58 in the gaussian
        # arm, 88.27 in the lorentzian and 53.78 in the mixed -- diagnosed for two
        # runs as an optimiser that had not converged, and answered once by doubling
        # MAX_NFEV, which changed the number not at all.
        # THE FALSE-PASS DIRECTION: the dropped term only ever made a pinned point
        # look BETTER than the free minimum, so it biased the profile DOWNWARD away
        # from theory -- widening the beta interval and pulling its centre.
        # `unpack` merges `self.fixed` into `d`, so `n in d` is the free AND the
        # pinned set; a term for a parameter this cell does not carry at all (a
        # per-session power scale when power_scale is off) is still skipped.
        parts.append(np.array([(d[n] - mu) / sig for n, mu, sig in self.prior_terms if n in d]))
        if self.logdet:
            ld = sum(self.logdet_of(t, self.axis(d, t),
                                    self.model(self.axis(d, t) - centres[i], d, self.per[i], t["peak"], t["session"]))
                     for i, t in enumerate(self.traces))
            if ld + LOGDET_OFFSET <= 0.0:
                raise ValueError(f"logdet: sum ln sigma^2 = {ld:.0f} is below -LOGDET_OFFSET; raise the offset")
            parts.append(np.array([math.sqrt(ld + LOGDET_OFFSET)]))
        return np.concatenate(parts)

    def chi2(self, p, centres):
        r = self.residuals(p, centres)
        return float(r @ r)

    def chi2_by_session(self, p, centres) -> dict:
        """chi2_red per session at p: the whitened residual sum of each session's
        traces over that session's effective samples minus its per-trace nuisances.
        A SESSION'S NOISE LAW SETS ITS VOTE (2026-09-14): chi2_red read 1.11 with the
        evening session and 1.36 without it over the same P, T, M traces, so the
        evening rows cost nothing and their nuisances were free to absorb the kernel;
        a session outside the admitted band has no vote and the gate says so."""
        d = self.unpack(p); acc = {}
        for i, t in enumerate(self.traces):
            nu = self.axis(d, t)
            m = self.model(nu - centres[i], d, self.per[i], t["peak"], t["session"])
            r = self.linear(t, nu, m)[1]
            a = acc.setdefault(t["session"], [0.0, 0.0, 0])
            a[0] += float(r @ r); a[1] += t["n"] / t["tau"]; a[2] += 1
        return {s: c / max(n_eff - 4.0 * n, 1.0) for s, (c, n_eff, n) in acc.items()}

    def chi2_split_by_session(self, p, centres) -> dict:
        """Per session, the whitened residual sum and the effective samples of the CORE
        (|nu - centre| <= CORE_HALF_MHZ) and of the WING, separately.

        **"THE WING READS THE NOISE LAW, NO LINE THERE TO MISFIT" IS RETRACTED**
        (2026-09-15). On one P trace the per-sample line exceeds
        the whitened noise wherever gamma^2/(gamma^2 + Delta^2) > sqrt(tau)/(A/s),
        which is out to 35 MHz of an 85 MHz sweep, so the wing holds the
        Lorentzian tail and not the noise alone: 3.1 per cent of the whitened
        model power sits beyond 6 MHz, 8.7e4 units against the wing statistic's
        per-trace resolution of 36, so a 1 per cent RMS tail misfit is 2.4 sigma
        over 100 traces and 7.7 per cent is what the cached P split's wing excess
        actually is. What DOES hold is one-sided: a NEGATIVE wing z can only be
        the noise law, because a misfit ADDS residual power and four nuisances
        per trace cannot remove 44 per cent of it. The word therefore splits by
        sign, and the core reads the noise law too -- the evening's core swings
        from +28.5 to -20 across kernel forms at fixed data. Returns
        {session: {"core": [chi2, n_eff], "wing": [chi2, n_eff]}}; each half's chi2_red is
        chi2 / n_eff, the per-trace nuisances being charged to the core."""
        d = self.unpack(p); acc: dict = {}
        for i, t in enumerate(self.traces):
            nu = self.axis(d, t)
            m = self.model(nu - centres[i], d, self.per[i], t["peak"], t["session"])
            r = self.linear(t, nu, m)[1]
            core = np.abs(nu - centres[i]) <= CORE_HALF_MHZ
            a = acc.setdefault(t["session"], {"core": [0.0, 0.0], "wing": [0.0, 0.0]})
            a["core"][0] += float(r[core] @ r[core]); a["core"][1] += float(np.sum(core)) / t["tau"] - 4.0
            a["wing"][0] += float(r[~core] @ r[~core]); a["wing"][1] += float(np.sum(~core)) / t["tau"]
        return acc

    def fit(self, p0, max_nfev=MAX_NFEV):
        """One start: inner bounded least squares with the centres held, outer
        re-profile of the centres until they stop moving."""
        from scipy.optimize import least_squares
        lo = np.array([self.bounds(n)[0] for n in self.names])
        hi = np.array([self.bounds(n)[1] for n in self.names])
        p = np.clip(np.asarray(p0, float), lo, hi)
        centres = np.array([self.centre(i, p)[0] for i in range(len(self.traces))])
        nfev, moved, outer = 0, float("nan"), 0
        for outer in range(1, MAX_OUTER + 1):
            res = least_squares(lambda q: self.residuals(q, centres), p, bounds=(lo, hi),
                                method="trf", diff_step=DIFF_STEP, x_scale="jac",
                                max_nfev=max_nfev, xtol=1e-6, ftol=1e-6, gtol=1e-8)
            p = np.clip(res.x, lo, hi)
            nfev += int(res.nfev) * (1 + len(p))
            new = np.array([self.centre(i, p, centres[i])[0] for i in range(len(self.traces))])
            moved = float(np.max(np.abs(new - centres)))
            centres = new
            if moved < CENTRE_TOL_MHZ:
                break
        return dict(p=p, centres=centres, chi2=self.chi2(p, centres), nfev=nfev, outer=outer,
                    centre_moved=moved)

    def conditional_bars(self, p, centres):
        """One sigma per parameter with every other parameter pinned, from the
        curvature of the whitened chi2: sigma = sqrt(2 / d2chi2). A HESSIAN
        bar, one-sided at a bound, and the column that carries it says so."""
        f0 = self.chi2(p, centres)
        out = []
        for j, name in enumerate(self.names):
            h = 0.05 * max(abs(p[j]), 0.2)
            lo, hi = self.bounds(name)
            pp, pm = p.copy(), p.copy()
            pp[j] = min(p[j] + h, hi)
            pm[j] = max(p[j] - h, lo)
            step = 0.5 * (pp[j] - pm[j])
            fp, fm = self.chi2(pp, centres), self.chi2(pm, centres)
            curv = (fp - 2.0 * f0 + fm) / step ** 2 if step > 0 else float("nan")
            out.append(math.sqrt(2.0 / curv) if np.isfinite(curv) and curv > 0 else float("nan"))
        return out

    def power_ratios(self, p, omega_scale=None) -> dict:
        """Per session, the model's own width ratio across that session's
        ladder at 130 C, mean over the session's peaks, everything
        power-independent held at the fitted values, the session's power
        factor applied where fitted."""
        d = self.unpack(p)
        if omega_scale is not None:
            d = dict(d, omega_scale=omega_scale)
        nu = np.arange(-30.0, 30.0, 0.01)
        out = {}
        for sess in self.sessions:
            if sess not in SESSION_LADDER_W:
                continue
            peaks = sorted({t["peak"] for t in self.traces if t["session"] == sess})
            ratios = []
            for peak in peaks:
                widths = []
                for P in SESSION_LADDER_W[sess]:
                    per = self._per_trace(dict(T=130.0, P_W=P, iso=int(K.PEAKS[peak]["isotope"]), session=sess, peak=peak))
                    widths.append(_fwhm(nu, self.model(nu, d, per, peak, sess)))
                ratios.append(widths[1] / widths[0])
            out[sess] = float(np.mean(ratios))
        return out


def _fwhm(nu, y):
    ypk = float(np.max(y))
    above = np.where(y >= 0.5 * ypk)[0]
    if above.size == 0:
        return float("nan")
    lo, hi = int(above[0]), int(above[-1])

    def cross(i, j):
        y1, y2 = y[i], y[j]
        return nu[i] + (0.5 * ypk - y1) / (y2 - y1) * (nu[j] - nu[i]) if y2 != y1 else nu[i]
    left = cross(lo - 1, lo) if lo > 0 else nu[lo]
    right = cross(hi, hi + 1) if hi < len(nu) - 1 else nu[hi]
    return float(right - left)


# ------------------------------------------------------------------ the archive's power arm
def measured_power_ratio(path=None) -> dict:
    """The archive's 25 to 225 mW width ratio at 130 C from the committed
    per-power widths, the four peaks combined by inverse variance, each peak's
    variance carrying its two fit errors and the block-to-block width scatter
    of the file (the pooled within-peak scatter of the five powers about their
    mean, which is what a power-independent width leaves)."""
    path = Path(path) if path else C.RESULTS_DIR / "power_sweep.csv"
    by = {}
    with path.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            by.setdefault(r["peak"], {})[float(r["power_mW"])] = (float(r["fwhm"]), float(r["fwhm_err"]))
    dev, n_dof, means = [], 0, []
    for peak, d in by.items():
        w = np.array([d[p][0] for p in sorted(d)])
        dev.extend((w - w.mean()).tolist())
        n_dof += len(w) - 1
        means.append(w.mean())
    s_block = math.sqrt(sum(x * x for x in dev) / n_dof)
    s_frac = s_block / float(np.mean(means))
    num = den = 0.0
    per = {}
    for peak, d in by.items():
        f25, e25 = d[min(d)]
        f225, e225 = d[max(d)]
        r = f225 / f25
        var = r * r * ((e25 / f25) ** 2 + (e225 / f225) ** 2 + 2.0 * s_frac ** 2)
        per[peak] = (r, math.sqrt(var))
        num += r / var
        den += 1.0 / var
    return dict(ratio=num / den, bar=1.0 / math.sqrt(den), block_scatter_mhz=s_block,
                block_scatter_frac=s_frac, per_peak=per, n_peaks=len(by), source="results/power_sweep.csv")


def trace_widths(traces) -> dict:
    """The model-free contiguous half-maximum width of every trace on its own
    axis, grouped by (session, peak, power): mean, standard error over the
    repeats and the count."""
    groups: dict = {}
    for t in traces:
        groups.setdefault((t["session"], t["peak"], t["P_W"]), []).append(contiguous_fwhm_ms(t["x"], t["v"]))
    out = {}
    for k, ws in groups.items():
        w = np.asarray(ws, float)
        se = float(np.std(w, ddof=1) / math.sqrt(w.size)) if w.size > 1 else float("nan")
        out[k] = dict(mean=float(w.mean()), se=se, n=int(w.size), widths=[float(x) for x in w])
    return out


def measured_power_ratio_from_traces(widths: dict, sess: str, block_frac: float) -> dict:
    """A session's ladder ratio, top rung over bottom rung, per peak from the
    model-free widths of its own traces, combined by inverse variance; each
    peak's bar carries the repeats' standard errors and the archive's block
    scatter for both rungs. Axis-free, so the evening's ms widths serve."""
    lo_w, hi_w = SESSION_LADDER_W[sess]
    num = den = 0.0
    per = {}
    for (s, peak, P), g in widths.items():
        if s != sess or P != lo_w:
            continue
        top = widths.get((sess, peak, hi_w))
        if top is None or not np.isfinite(g["se"]) or not np.isfinite(top["se"]):
            continue
        r = top["mean"] / g["mean"]
        var = r * r * ((g["se"] / g["mean"]) ** 2 + (top["se"] / top["mean"]) ** 2 + 2.0 * block_frac ** 2)
        per[peak] = (r, math.sqrt(var))
        num += r / var
        den += 1.0 / var
    if den == 0.0:
        return dict(ratio=float("nan"), bar=float("nan"), per_peak=per, n_peaks=0,
                    source="no peak with repeats at both rungs")
    return dict(ratio=num / den, bar=1.0 / math.sqrt(den), per_peak=per, n_peaks=len(per),
                source="contiguous half-maximum widths of the session's own traces")


def power_arm_check(predicted: float, measured: float, bar: float) -> dict:
    """The refusal: the predicted ratio may not exceed the measured one by more
    than POWER_ARM_REFUSAL_BARS of its bar. The pull is signed so a prediction
    BELOW the archive is visible too and is never refused, since every P^2
    term in the model widens."""
    pull = (predicted - measured) / bar if bar > 0 else float("nan")
    return dict(pull=pull, refused=bool(np.isfinite(pull) and pull > POWER_ARM_REFUSAL_BARS))


def pooled_power_arm(preds: dict, meas: dict) -> dict:
    """The sessions' (predicted minus measured) combined by inverse variance."""
    num = den = 0.0
    for sess, pred in preds.items():
        m = meas.get(sess)
        if m is None or not np.isfinite(m["bar"]) or m["bar"] <= 0 or not np.isfinite(pred):
            continue
        num += (pred - m["ratio"]) / m["bar"] ** 2
        den += 1.0 / m["bar"] ** 2
    if den == 0.0:
        return dict(pull=float("nan"), refused=False, bar=float("nan"), n_sessions=0)
    pull = (num / den) * math.sqrt(den)
    return dict(pull=pull, refused=bool(pull > POWER_ARM_REFUSAL_BARS), bar=1.0 / math.sqrt(den),
                n_sessions=sum(1 for s in preds if s in meas))


def width_vs_power_rows(widths: dict, meas_committed: dict) -> list[dict]:
    """The diagnostic the Omega reading must be read against: the width
    against power per session and peak, from the committed per-power model-free
    half-maximum widths for P and from the traces' own for every session, as a weighted
    linear slope of ln(width) in per watt with its least-squares bar and the
    sign of the slope."""
    out = []

    def slope(P, w, e):
        P, w, e = np.asarray(P, float), np.asarray(w, float), np.asarray(e, float)
        ok = np.isfinite(e) & (e > 0)
        if ok.sum() < 3:
            return float("nan"), float("nan")
        y, s = np.log(w[ok]), e[ok] / w[ok]
        A = np.column_stack([np.ones(ok.sum()), P[ok]]) / s[:, None]
        cov = np.linalg.inv(A.T @ A)
        coef = cov @ (A.T @ (y / s))
        return float(coef[1]), float(math.sqrt(cov[1, 1]))
    path = C.RESULTS_DIR / "power_sweep.csv"
    if path.is_file():
        by: dict = {}
        with path.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                by.setdefault(r["peak"], []).append((float(r["power_mW"]) * 1e-3, float(r["fwhm"]), float(r["fwhm_err"])))
        for peak, rows in sorted(by.items()):
            P, w, e = zip(*sorted(rows))
            e = [math.hypot(x, meas_committed["block_scatter_frac"] * y) for x, y in zip(e, w)]
            s, se = slope(P, w, e)
            out.append(dict(kind="width_vs_power_committed", sess="P", peak=peak, slope=s, err=se,
                            # power_sweep.csv's fwhm is qc.contiguous_fwhm_ms, a MODEL-FREE half-maximum width, not a
                            # fit (F511, 2026-09-25); the block scatter is estimated about each line's mean, so it
                            # absorbs any real trend and this slope's bar bounds a narrowing rather than testing one.
                            source="results/power_sweep.csv model-free half-maximum widths (qc.contiguous_fwhm_ms), the block scatter added in quadrature"))
    keys = sorted({(s, pk) for (s, pk, _) in widths}, key=lambda k: (list(SESSIONS).index(k[0]), k[1]))
    for sess, peak in keys:
        pts = sorted((P, g["mean"], g["se"]) for (s, pk, P), g in widths.items() if s == sess and pk == peak)
        if len(pts) < 3:
            continue
        P, w, e = zip(*pts)
        s, se = slope(P, w, e)
        out.append(dict(kind="width_vs_power_traces", sess=sess, peak=peak, slope=s, err=se,
                        source="model-free contiguous half-maximum widths of the traces, repeats' standard errors"))
    return out


# ------------------------------------------------------------------ one cell
def _n_by_session(traces) -> tuple[dict, dict]:
    """Effective samples and trace counts per session, the vote's own bookkeeping."""
    ne, nt = {}, {}
    for t in traces:
        ne[t["session"]] = ne.get(t["session"], 0.0) + t["n"] / t["tau"]
        nt[t["session"]] = nt.get(t["session"], 0) + 1
    return ne, nt


def _diag_task(job):
    """Per-session chi2_red and effective samples for a SAVED cell fitted before
    they were carried: the cell rebuilt from its spec, the parameters read back,
    the centres re-profiled at them. No fit, so the cell's numbers do not move."""
    idx, rec, design_spec = job
    traces = _load(design_spec)
    cell = Cell(rec["spec"], traces)
    p = np.array([float(rec["params"][n]) for n in cell.names], float)
    centres = np.array([cell.centre(i, p)[0] for i in range(len(traces))])
    ne, nt = _n_by_session(traces)
    return dict(idx=idx, chi2_red_session=cell.chi2_by_session(p, centres), chi2_split_session=cell.chi2_split_by_session(p, centres),
                n_eff_session=ne, n_traces_session=nt)


def fill_session_diagnostics(base, design_spec, workers: int, session_traces=()) -> int:
    """Fill the per-session diagnostics into every saved cell that lacks them
    (W1j findings F3 to F5: the committed cells were fitted before the checks
    existed and the gate refused them for it). Returns the count filled."""
    todo = [(i, r, design_spec) for i, r in enumerate(base) if not r.get("chi2_red_session") or not r.get("n_eff_session") or not r.get("chi2_split_session")]
    if not todo:
        return 0
    print(f"  per-session diagnostics for {len(todo)} saved cell(s) that were fitted before they were carried", flush=True)
    out = {}
    if workers <= 0:
        _init_worker(session_traces)
        for j in todo:
            r = _diag_task(j); out[r["idx"]] = r
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(list(session_traces),)) as ex:
            for fu in as_completed([ex.submit(_diag_task, j) for j in todo]):
                r = fu.result(); out[r["idx"]] = r
    for i, r in out.items():
        base[i]["chi2_red_session"], base[i]["n_eff_session"], base[i]["n_traces_session"] = r["chi2_red_session"], r["n_eff_session"], r["n_traces_session"]
        base[i]["chi2_split_session"] = r["chi2_split_session"]
    return len(todo)


def _cell_task(job):
    """One grid point: everything refit from every start, the conditional
    bars, the beta profile and the power-arm checks at the best start.
    Depends on nothing but its own arguments, which is what makes the pool an
    order and not a result."""
    idx, spec, design_spec = job
    traces = _load(design_spec)
    cell = Cell(spec, traces)
    t0 = time.time()
    max_nfev = spec.get("max_nfev", MAX_NFEV)
    starts = spec.get("starts") or cell.starts()
    fits = [cell.fit(p0, max_nfev=max_nfev) for p0 in starts]
    best = min(fits, key=lambda f: f["chi2"])
    spread = max(f["chi2"] for f in fits) - min(f["chi2"] for f in fits)
    bars = cell.conditional_bars(best["p"], best["centres"])
    n_eff = sum(t["n"] / t["tau"] for t in traces)
    dof = n_eff - len(cell.names) - 4 * len(traces)
    p = {k: float(v) for k, v in cell.unpack(best["p"]).items()}
    e = {k: float(v) for k, v in zip(cell.names, bars)}
    # THE BETA PROFILE: chi2 with beta pinned at each of the named values and
    # everything else refit, warm from the free minimum, one start each.
    beta_profile = {}
    if "beta_rel" in cell.names and spec.get("beta_profile", True):
        for br in BETA_PROFILE_REL:
            cb = Cell(dict(spec, fixed={**cell.fixed, "beta_rel": br}), traces)
            warm = [p[n] for n in cb.names]
            fb = cb.fit(warm, max_nfev=max_nfev)
            beta_profile[br] = dict(chi2=fb["chi2"], params={k: float(v) for k, v in cb.unpack(fb["p"]).items()})
    # A FREE FIT SEEDED FROM THE PROFILE'S BEST POINT (2026-09-14): rung 0 was
    # refused twice because a fixed-beta refit sat below the free minimum, which
    # is an optimiser that stopped and not a physics statement. The best profile
    # point is a start the free fit must match or beat, so the free minimum can
    # never sit above its own profile.
    # AND THE RESEED REPEATS UNTIL IT STOPS PAYING (2026-09-16). One pass was not
    # enough once the parameter set gained a dimension: the profile's best point is
    # a start, and a start can itself stop on its budget, leaving the free minimum
    # above the profile again. Three passes at most, and it exits the moment a pass
    # buys less than the convergence check's own tolerance.
    for _ in range(3):
        if not beta_profile:
            break
        _br = min(beta_profile, key=lambda k: beta_profile[k]["chi2"])
        if beta_profile[_br]["chi2"] >= best["chi2"] - 1e-6:
            break
        _seed = dict(beta_profile[_br]["params"]); _seed["beta_rel"] = float(_br)
        _f3 = cell.fit([_seed.get(n, p[n]) for n in cell.names], max_nfev=max_nfev)
        fits.append(_f3)
        if _f3["chi2"] >= best["chi2"] - 1e-6:
            break
        best = _f3
        bars = cell.conditional_bars(best["p"], best["centres"])
        p = {k: float(v) for k, v in cell.unpack(best["p"]).items()}
        e = {k: float(v) for k, v in zip(cell.names, bars)}
    # THE SPREAD IS READ OVER THE ENDPOINTS AFTER A POLISH from each start's own
    # end, so a start that stopped on its budget is not read as a second minimum.
    spread = max(f["chi2"] for f in fits) - min(f["chi2"] for f in fits)
    # THE REFUSAL READS THE TIED OMEGA, never the fitted scale: a fit that
    # pays for a small waist by pulling the scale toward zero has used the
    # escape valve the tie exists to close, so the check is made at the theory
    # coefficient with everything else at the fitted values, and the fitted
    # scale's own prediction is written beside it as the diagnostic.
    preds = cell.power_ratios(best["p"], omega_scale=1.0)
    preds_fitted = cell.power_ratios(best["p"])
    chi2_red_session = cell.chi2_by_session(best["p"], best["centres"])
    lic = convolution_licence(cell.w0, cell.m2)
    ref = cell._per_trace(dict(T=130.0, P_W=0.225, iso=87, session="P", peak="4207"))
    return dict(idx=idx, spec={k: v for k, v in spec.items() if k != "starts"},
                chi2=best["chi2"], chi2_red=best["chi2"] / dof, n_eff=n_eff, n_traces=len(traces),
                names=list(cell.names), params=p, errs=e, spread=spread, nfev=sum(f["nfev"] for f in fits),
                outer=[f["outer"] for f in fits], centre_moved=best["centre_moved"],
                s0_225=ref["s0"], omega_225=p["omega_scale"] * ref["omega_ref"],
                transit_130=ref["transit"], transit_130_depleted=depleted_transit(
                    ref["transit"], ref["omega_ref"], "4192", cell.cycles),
                z_ratio=cell.z_ratio, licensed=lic["licensed"], w0_edge_um=lic["w0_min_m"] * 1e6,
                preds=preds, preds_fitted=preds_fitted, seconds=time.time() - t0,
                chi2_red_session=chi2_red_session, chi2_split_session=cell.chi2_split_by_session(best["p"], best["centres"]),
                n_eff_session=_n_by_session(traces)[0], n_traces_session=_n_by_session(traces)[1],
                delta_alpha=cell.delta_alpha, rho=cell.rho, law=cell.law_name, sessions=cell.sessions,
                beta_profile={str(k): v for k, v in beta_profile.items()},
                at_bound=at_bound_of(cell.names, best["p"], bars),
                p_vector=[float(x) for x in best["p"]])


def _spec(form, w0, m2=1.0, cycles=0.0, propagation=None, starts=None, da=None, **extra):
    # ALPHA AND BETA PINNED AT THEORY BY DEFAULT (owner, 2026-09-17 00:30: "pin alpha and beta_self
    # from theory ... to compare only after the theoretical value with what would come from the
    # MLE"), replacing the 2026-09-16 prior form for the PRIMARY matrix: `fixed` carries both at
    # their theory scale unless the caller frees one (`free=("alpha_rel",)`), which is the
    # comparison arm and is recorded as such in `pinned`. Their uncertainties ride as systematics
    # through `propagation` (delta_alpha and rho at one sigma, beta through a fixed beta_rel).
    free = tuple(extra.pop("free", ()))
    pinned = {n: 1.0 for n in ("beta_rel", "alpha_rel") if n not in free}
    extra["fixed"] = {**pinned, **extra.get("fixed", {})}
    extra["pinned"] = tuple(sorted(pinned))
    da = da if da is not None else deep_delta_alpha()
    return dict(form=form, w0_um=float(w0), m2=float(m2), cycles=float(cycles), propagation=propagation,
                starts=(None if starts is None else tuple(tuple(s) for s in starts)),
                delta_alpha=da[0], delta_alpha_err=da[1], **extra)


def _cost_key(spec):
    """Longest first: the small-waist end rails the laser widths at their
    floor and pays for a fine grid, the arms are warm-started."""
    return (spec["w0_um"], 0 if spec.get("starts") is None else 1, FORMS.index(spec["form"]))


def run_cells(specs, design_spec, workers: int, label: str = "", session_traces=()) -> list[dict]:
    """Every spec through `_cell_task`, in the pool when workers > 0,
    collected by index so the result is the same at every worker count. The
    sessions outside the manifest travel to each worker once, through the
    pool's initializer."""
    jobs = sorted(((i, s, design_spec) for i, s in enumerate(specs)), key=lambda j: _cost_key(j[1]))
    out = {}
    t0 = time.time()
    if workers <= 0:
        _init_worker(session_traces)
        for j in jobs:
            r = _cell_task(j)
            out[r["idx"]] = r
            _progress(r, len(out), len(jobs), t0, label)
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker, initargs=(list(session_traces),)) as ex:
            futs = [ex.submit(_cell_task, j) for j in jobs]
            for fu in as_completed(futs):
                r = fu.result()
                out[r["idx"]] = r
                _progress(r, len(out), len(jobs), t0, label)
    return [out[i] for i in range(len(specs))]


def _progress(r, done, total, t0, label):
    s = r["spec"]
    arm = f"m2={s['m2']:g} cyc={s['cycles']:g}" + (f" prop={s['propagation']}" if s.get("propagation") else "")
    pr = " ".join(f"{k}={v:.4f}" for k, v in r["preds"].items())
    print(f"  [{label}{done}/{total}] {s['form']:<10} w0={s['w0_um']:5.1f} {arm}: chi2={r['chi2']:.1f} "
          f"chi2_red={r['chi2_red']:.3f} beta_rel={r['params']['beta_rel']:.2f} om={r['params']['omega_scale']:.2f} "
          f"ratio {pr} ({r['nfev']} evals, {r['seconds']:.0f} s) [{time.time() - t0:.0f} s]", flush=True)


# ------------------------------------------------------------------ the profile read
def profile_summary(ws, chi2s, chi2_red=1.0) -> dict:
    """The minimum or the bound read off chi2(w0) on the grid it was computed
    on. Interior: the parabola's vertex and sigma at Delta chi2 = 1, the
    crossings at 1 and at chi2_red, and the one-sided crossings at 2.71. At an
    edge: the one-sided bound at 2.71 against that edge."""
    ws, chi2s = np.asarray(ws, float), np.asarray(chi2s, float)
    order = np.argsort(ws)
    ws, chi2s = ws[order], chi2s[order]
    j = int(np.argmin(chi2s))
    cmin = float(chi2s[j])
    out = dict(w0=float(ws[j]), chi2_min=cmin, kind="", w0_err=float("nan"), lo1=float("nan"), hi1=float("nan"),
               lo_od=float("nan"), hi_od=float("nan"), bound95=float("nan"), curvature=float("nan"))

    def cross(level, direction):
        """The first waist from the minimum, in `direction`, at which chi2
        rises past `level` above `out["chi2_min"]`, by linear interpolation
        between grid points, read against the PARABOLA's minimum once one is
        fitted, and blank where the grid point itself already sits above the
        level, which is what a coarse grid does."""
        # AGAINST THE GRID MINIMUM (2026-09-14): read against the parabola's vertex,
        # the grid point itself sat 1.04 above the reference and every crossing went
        # blank, then the overdispersed level crossed 0.07 above it into a 0.05 um
        # interval: a zero-width interval from a moved reference, a wrong committed cell.
        ref = cmin
        # UNRESOLVED STAYS BLANK: a linear crossing on a step where chi2 rises
        # by r levels sits at step/r from the grid point while a parabola puts
        # it at step/sqrt(r), so past RESOLVE_LEVELS the interpolation is off
        # by a factor two or more (the committed 39/0/17 grid read 0.26 um
        # beside a 1.9 um parabola bar) and the parabola's sigma is the bar.
        nb = j + 1 if direction > 0 else j - 1
        if 0 <= nb < len(ws) and chi2s[nb] - ref > RESOLVE_LEVELS * level:
            return float("nan")
        idx = range(j, len(ws)) if direction > 0 else range(j, -1, -1)
        prev = None
        for i in idx:
            if prev is None and chi2s[i] - ref >= level:
                return float("nan")
            if prev is not None and chi2s[i] - ref >= level:
                a, b = prev, i
                fa, fb = chi2s[a] - ref, chi2s[b] - ref
                return float(ws[a] + (level - fa) / (fb - fa) * (ws[b] - ws[a]))
            prev = i
        return float("nan")

    # A FLAT NEIGHBOUR IS AN EDGE, NOT A MINIMUM (2026-09-14): the mixed form's
    # "interior minimum" was a parabola through dchi2 0 at 80 and 0.34 at 90, the
    # last grid point, and its sigma excluded a point the profile held inside one.
    # ... and only when that flat neighbour is the LAST point on its side, with
    # nothing beyond it to confirm the rise; a resolved interior minimum with a
    # sigma near the grid step also has neighbours under one and is not an edge.
    flat_hi = 0 < j < len(ws) - 1 and j + 1 == len(ws) - 1 and chi2s[j + 1] - cmin < DCHI2_ONE_SIGMA
    flat_lo = 0 < j < len(ws) - 1 and j - 1 == 0 and chi2s[j - 1] - cmin < DCHI2_ONE_SIGMA
    if flat_hi and not flat_lo:
        out["kind"] = "one_sided_lower_bound"; out["bound95"] = cross(DCHI2_ONE_SIDED_95, -1)
        if not np.isfinite(out["bound95"]):
            # THE GRID CELL IS NOT THE BOUND (W1i finding): the crossing sits between the
            # cell and its neighbour, unresolved on this step; both estimates ride in the kind.
            _k = (chi2s[j - 1] - cmin) / (ws[j] - ws[j - 1]) ** 2
            out["kind"] = "one_sided_lower_bound_unresolved"
            out["bound95_linear"] = float(ws[j] - (ws[j] - ws[j - 1]) * DCHI2_ONE_SIDED_95 / max(chi2s[j - 1] - cmin, 1e-12))
            out["bound95_parabola"] = float(ws[j] - math.sqrt(DCHI2_ONE_SIDED_95 / _k)) if _k > 0 else float("nan")
    elif flat_lo and not flat_hi:
        out["kind"] = "one_sided_upper_bound"; out["bound95"] = cross(DCHI2_ONE_SIDED_95, +1)
    elif flat_lo and flat_hi:
        out["kind"] = "unresolved_on_this_grid"
    elif 0 < j < len(ws) - 1:
        den = chi2s[j - 1] - 2.0 * chi2s[j] + chi2s[j + 1]
        h = 0.5 * (ws[j + 1] - ws[j - 1])
        if den > 0:
            out["w0"] = float(ws[j] + 0.5 * (chi2s[j - 1] - chi2s[j + 1]) / den * h)
            curv = den / h ** 2
            out["curvature"] = float(curv)
            out["w0_err"] = math.sqrt(2.0 * DCHI2_ONE_SIGMA / curv)
            out["chi2_min"] = float(chi2s[j] - 0.125 * (chi2s[j - 1] - chi2s[j + 1]) ** 2 / den)
        out["kind"] = "interior_minimum"
        out["lo1"], out["hi1"] = cross(DCHI2_ONE_SIGMA, -1), cross(DCHI2_ONE_SIGMA, +1)
        od = max(float(chi2_red), 1.0) * DCHI2_ONE_SIGMA
        out["lo_od"], out["hi_od"] = cross(od, -1), cross(od, +1)
    elif j == 0:
        out["kind"] = "one_sided_upper_bound"
        out["bound95"] = cross(DCHI2_ONE_SIDED_95, +1)
    else:
        out["kind"] = "one_sided_lower_bound"
        out["bound95"] = cross(DCHI2_ONE_SIDED_95, -1)
        if not np.isfinite(out["bound95"]) and j >= 1:
            # THE PROFILE IS STILL FALLING AT THE GRID EDGE (W1j finding F2): the fine_all
            # gaussian and mixed minima sit on the last point with rises of 31 and 28 per
            # step against the resolve threshold of 10.8, so the crossing is unresolved and
            # the minimum is off the grid; the kind says so and both estimates ride beside
            # the rise, and the gate reads an unresolved edge as no bound at all.
            _k = (chi2s[j - 1] - cmin) / (ws[j] - ws[j - 1]) ** 2
            out["kind"] = "one_sided_lower_bound_unresolved"
            out["edge_rise_levels"] = float((chi2s[j - 1] - cmin) / DCHI2_ONE_SIDED_95)
            out["bound95_linear"] = float(ws[j] - (ws[j] - ws[j - 1]) * DCHI2_ONE_SIDED_95 / max(chi2s[j - 1] - cmin, 1e-12))
            out["bound95_parabola"] = float(ws[j] - math.sqrt(DCHI2_ONE_SIDED_95 / _k)) if _k > 0 else float("nan")
    return out


def beta_profile_read(r) -> dict:
    """The beta profile of one cell: dchi2 at each fixed value above the free
    minimum, and the first crossings at Delta chi2 = 1 and 2.71 above the
    free minimum interpolated linearly in beta between the profile points,
    labelled as read off the profile."""
    prof = r.get("beta_profile") or {}
    ref = min([r["chi2"]] + [v["chi2"] for v in prof.values()])
    pts = sorted([(float(k), v["chi2"] - ref) for k, v in prof.items()] + [(r["params"]["beta_rel"], r["chi2"] - ref)])
    out = {f"dchi2_beta_{k}": float("nan") for k in ("0", "theory", "5x", "20x")}
    tag = {0.0: "0", 1.0: "theory", 5.0: "5x", 20.0: "20x"}
    for k, v in prof.items():
        out[f"dchi2_beta_{tag[float(k)]}"] = v["chi2"] - ref
    out["free_above_profile_min"] = r["chi2"] - ref

    def crossing(level):
        b0 = min(pts, key=lambda q: q[1])[0]
        above = [(b, d) for b, d in pts if b >= b0]
        prev = None
        for b, d in above:
            if prev is not None and d >= level:
                pb, pd = prev
                return float(pb + (level - pd) / (d - pd) * (b - pb)) if d > pd else float(b)
            prev = (b, d)
        return float("nan")
    out["beta_profile_1sigma_hi_rel"] = crossing(DCHI2_ONE_SIGMA)
    out["beta_profile_ub95_rel"] = crossing(DCHI2_ONE_SIDED_95)
    return out


# ------------------------------------------------------------------ the CSV
def sig2(x) -> str:
    """Two significant digits, never scientific notation below 1e6."""
    if x is None or not np.isfinite(x):
        return ""
    if x == 0:
        return "0"
    d = 1 - int(math.floor(math.log10(abs(x))))
    v = round(float(x), d)
    if v != 0 and 1 - int(math.floor(math.log10(abs(v)))) < d:
        d -= 1
    return f"{v:.{max(d, 0)}f}"


def with_decimals_of(v, e, default=2) -> str:
    """A waist crossing or shift written to the decimals of the bar beside it
    (or `default` decimals without one), so a crossing at 49.9 um does not
    round onto the grid point at 50."""
    if v is None or not np.isfinite(v):
        return ""
    es = sig2(e) if (e is not None and np.isfinite(e) and e > 0) else ""
    d = len(es.split(".")[1]) if "." in es else default
    return f"{v:.{d}f}"


def pair(v, e) -> tuple[str, str]:
    """A value and its bar: the bar to two significant digits, the value to the
    bar's decimals (protocol 8a.2). Without a finite bar the value alone at two
    significant digits."""
    if e is None or not np.isfinite(e) or e <= 0:
        return sig2(v), ""
    es = sig2(e)
    d = len(es.split(".")[1]) if "." in es else 0
    return (f"{v:.{d}f}" if np.isfinite(v) else ""), es


PARAM_COLUMNS = (["beta_rel", "sigma_l_shared"] + [f"sigma_l_{s}" for s in SESSIONS] + ["omega_scale", "gamma_l"]
                 + [f"lograte_E_{pk}" for pk in sorted(K.PEAKS)] + [f"power_scale_{s}" for s in SESSIONS])
COLUMNS = (["row_kind", "sessions", "sigma_l_arm", "power_scale_arm", "form", "m2", "depletion_cycles", "propagation",
            "peak", "w0_um", "w0_err_parabola_um", "bound_kind", "w0_bound95_um", "w0_lo_um", "w0_hi_um",
            "w0_lo_overdispersed_um", "w0_hi_overdispersed_um", "w0_shift_um",
            "chi2", "dchi2", "chi2_red", "n_eff", "n_traces", "start_spread_chi2", "chi2_red_by_session", "session_verdicts", "nfev"]
           + [c for n in PARAM_COLUMNS for c in (n, f"{n}_err_hessian")]
           + ["beta_khz_per_1e12", "beta_err_khz_hessian", "beta_pull_vs_theory_hessian", "beta_fixed_rel",
              "dchi2_beta_0", "dchi2_beta_theory", "dchi2_beta_5x", "dchi2_beta_20x",
              "beta_profile_1sigma_hi_khz", "beta_profile_ub95_khz", "omega_scale_pull",
              "s0_225_mhz", "omega_225_mhz", "transit_130_mhz", "transit_130_depleted_mhz",
              "z_ratio", "licensed", "w0_licence_edge_um",
              "power_ratio_pred", "power_ratio_pred_fitted_omega", "power_ratio_meas", "power_ratio_bar",
              "power_arm_pull", "power_arm_refused", "power_arm_pooled_pull", "power_arm_pooled_refused",
              "power_lo_w", "power_hi_w", "width_slope_per_w", "width_slope_err_lsq_per_w", "width_slope_sign",
              "noise_a_v", "noise_b_v", "noise_tau_int", "at_bound", "seconds", "note", "status"])
# status LAST, as annotate_results_status.py writes it


def _row(kind, r, meas, dchi2=float("nan"), **extra):
    s = r["spec"]
    p, e = r["params"], r["errs"]
    prop = s.get("propagation")
    beta_khz, beta_err = p["beta_rel"] * BETA_THEORY_KHZ, e.get("beta_rel", float("nan")) * BETA_THEORY_KHZ
    pr = r["preds"].get("P", float("nan"))
    check = power_arm_check(pr, meas["P"]["ratio"], meas["P"]["bar"]) if "P" in meas else dict(pull=float("nan"), refused=False)
    pooled = pooled_power_arm(r["preds"], meas)
    bp = beta_profile_read(r)
    row = dict.fromkeys(COLUMNS, "")
    row.update(row_kind=kind, sessions="".join(r["sessions"]), sigma_l_arm=s.get("sigma_l", "session"),
               power_scale_arm=str(bool(s.get("power_scale", False))), form=s["form"], m2=f"{s['m2']:g}",
               depletion_cycles=f"{s['cycles']:g}",
               propagation=("" if prop is None else f"{prop[0]}{prop[1]:+d}sigma" if prop[0] != "law" else f"law={prop[1]}"),
               w0_um=sig2(s["w0_um"]), chi2=sig2(r["chi2"]), dchi2=sig2(dchi2), chi2_red=sig2(r["chi2_red"]),
               n_eff=sig2(r["n_eff"]), n_traces=str(r["n_traces"]), start_spread_chi2=sig2(r["spread"]),
               chi2_red_by_session=" ".join(f"{s}:{v:.3f}" for s, v in sorted(r.get("chi2_red_session", {}).items())),
               session_verdicts=session_verdicts_text(r),
               nfev=str(r["nfev"]),
               beta_khz_per_1e12=pair(beta_khz, beta_err)[0], beta_err_khz_hessian=pair(beta_khz, beta_err)[1],
               beta_pull_vs_theory_hessian=sig2((beta_khz - BETA_THEORY_KHZ) / math.hypot(beta_err, BETA_THEORY_ERR_KHZ))
               if np.isfinite(beta_err) else "",
               beta_fixed_rel=("" if "beta_rel" not in s.get("fixed", {}) else sig2(s["fixed"]["beta_rel"])),
               dchi2_beta_0=sig2(bp["dchi2_beta_0"]), dchi2_beta_theory=sig2(bp["dchi2_beta_theory"]),
               dchi2_beta_5x=sig2(bp["dchi2_beta_5x"]), dchi2_beta_20x=sig2(bp["dchi2_beta_20x"]),
               beta_profile_1sigma_hi_khz=sig2(bp["beta_profile_1sigma_hi_rel"] * BETA_THEORY_KHZ),
               beta_profile_ub95_khz=sig2(bp["beta_profile_ub95_rel"] * BETA_THEORY_KHZ),
               omega_scale_pull=sig2((p["omega_scale"] - 1.0) / OMEGA_PRIOR_FRAC),
               s0_225_mhz=sig2(r["s0_225"]), omega_225_mhz=sig2(r["omega_225"]), transit_130_mhz=sig2(r["transit_130"]),
               transit_130_depleted_mhz=sig2(r["transit_130_depleted"]), z_ratio=sig2(r["z_ratio"]),
               licensed=str(bool(r["licensed"])), w0_licence_edge_um=sig2(r["w0_edge_um"]),
               power_ratio_pred=(f"{pr:.4f}" if np.isfinite(pr) else ""),
               power_ratio_pred_fitted_omega=(f"{r['preds_fitted'].get('P', float('nan')):.4f}" if "P" in r["preds_fitted"] else ""),
               power_ratio_meas=(f"{meas['P']['ratio']:.4f}" if "P" in meas else ""),
               power_ratio_bar=(f"{meas['P']['bar']:.4f}" if "P" in meas else ""),
               power_arm_pull=sig2(check["pull"]), power_arm_refused=str(check["refused"]),
               power_arm_pooled_pull=sig2(pooled["pull"]), power_arm_pooled_refused=str(pooled["refused"]),
               at_bound=" ".join(r["at_bound"]), seconds=sig2(r["seconds"]), status="DIAGNOSTIC")
    for n in PARAM_COLUMNS:
        if n in p and (not r["names"] or n in r["names"] or n in s.get("fixed", {})):
            v, ev = pair(p[n], e.get(n, float("nan")))
            row[n], row[f"{n}_err_hessian"] = v, ev
    if s["form"] != "mixed":
        row["gamma_l"], row["gamma_l_err_hessian"] = "0", ""
    row.update({k: v for k, v in extra.items() if k in row})
    return row


def _note_grid(r, meas):
    s = r["spec"]
    pr = r["preds"].get("P", float("nan"))
    check = power_arm_check(pr, meas["P"]["ratio"], meas["P"]["bar"]) if "P" in meas else dict(pull=float("nan"), refused=False)
    pooled = pooled_power_arm(r["preds"], meas)
    return (f"the whitened profile likelihood over {r['n_traces']} traces of sessions {''.join(r['sessions'])} at this "
            f"waist with beta_self, the laser widths ({s.get('sigma_l', 'session')}), the Omega scale (prior 1 +- "
            f"{OMEGA_PRIOR_FRAC:g}){', a power factor per session (prior 1 +- 0.1)' if s.get('power_scale') else ''}"
            f"{', a rate per evening peak' if 'E' in r['sessions'] else ''} refit from 2 starts, "
            f"gamma_l {'free and shared' if s['form'] == 'mixed' else 'pinned at zero'}, "
            f"Delta_alpha pinned at {r['delta_alpha']:.1f} a.u. and rho at {r['rho']:.2f}, the density law {r['law']}, "
            f"the collection window on at z_ratio {r['z_ratio']:.3f} (M2 {s['m2']:g}), depletion at {s['cycles']:g} cycles "
            f"through companion_transit_mhz (transit at 130 C {r['transit_130']:.4f} to {r['transit_130_depleted']:.4f} MHz). "
            f"the _err_hessian bars are conditional, every other parameter pinned{', at a bound: ' + ' '.join(r['at_bound']) if r['at_bound'] else ''}. "
            f"the dchi2_beta columns are the beta profile, chi2 with beta pinned at 0, theory, 5x and 20x theory and "
            f"everything else refit, above the free minimum. the power-arm check reads the model's width ratio across each "
            f"session's ladder at the TIED Omega (scale 1) with everything else fitted: P against the archive's "
            f"{meas['P']['ratio']:.4f} +- {meas['P']['bar']:.4f}, {'refused' if check['refused'] else 'passes'} at pull "
            f"{check['pull']:+.2f}, pooled over {pooled['n_sessions']} sessions {'refused' if pooled['refused'] else 'passes'} "
            f"at pull {pooled['pull']:+.2f}. centres profiled per trace and re-profiled after each inner fit, outer passes "
            f"{r['outer']}, last centre move {r['centre_moved']:.3f} MHz")


def summary_rows(base, arms, props, meas, widths, laws_rows, grid_ws, forms_run, dropped=()) -> tuple[list[dict], dict]:
    """The rows in canonical order: the base grid per form, the arms, the
    propagation cells, then the summaries per form, the per-session power
    arm, the width diagnostic and the fitted noise laws."""
    rows = []
    summaries = {}
    for form in FORMS:
        cells = [r for r in base if r["spec"]["form"] == form]
        if not cells:
            continue
        ws = [r["spec"]["w0_um"] for r in cells]
        c2 = [r["chi2"] for r in cells]
        best = cells[int(np.argmin(c2))]
        summ = profile_summary(ws, c2, chi2_red=best["chi2_red"])
        summaries[form] = (summ, best)
        cmin = min(c2)
        for r in sorted(cells, key=lambda r: r["spec"]["w0_um"]):
            rows.append(_row("grid", r, meas, dchi2=r["chi2"] - cmin, note=_note_grid(r, meas)))
            for br, v in sorted(r.get("beta_profile", {}).items(), key=lambda kv: float(kv[0])):
                om0 = r["params"]["omega_scale"]
                rb = dict(r, spec=dict(r["spec"], fixed={**r["spec"].get("fixed", {}), "beta_rel": float(br)}),
                          chi2=v["chi2"], params=v["params"], errs={}, names=[], at_bound=[], beta_profile={},
                          preds={}, preds_fitted={},
                          omega_225=(v["params"]["omega_scale"] * r["omega_225"] / om0 if om0 > 0 else float("nan")))
                rows.append(_row("beta_profile", rb, meas, dchi2=v["chi2"] - r["chi2"],
                                 note=f"beta_self pinned at {float(br):g} times theory ({float(br) * BETA_THEORY_KHZ:.2f} kHz per "
                                      f"1e12 cm^-3) with everything else refit warm from the free minimum at this waist: dchi2 is "
                                      f"against the free minimum, and the dchi2_beta columns of the grid row read every point "
                                      f"against the lowest of the free and the fixed fits. the summary reads the profile these "
                                      f"rows make and never a Hessian bar at a rail"))
    base_at = {(r["spec"]["form"], r["spec"]["w0_um"]): r for r in base}
    for r in sorted(arms, key=lambda r: (FORMS.index(r["spec"]["form"]), r["spec"]["m2"], r["spec"]["cycles"], r["spec"]["w0_um"])):
        b = base_at.get((r["spec"]["form"], r["spec"]["w0_um"]))
        d = r["chi2"] - b["chi2"] if b else float("nan")
        rows.append(_row("arm", r, meas, dchi2=d,
                         note=_note_grid(r, meas) + ". dchi2 is against the base arm (M2 1, no depletion) at the same waist"
                         + (", warm-started from it" if b else "")))
    for r in sorted(props, key=lambda r: (FORMS.index(r["spec"]["form"]), str(r["spec"]["propagation"]), r["spec"]["w0_um"])):
        b = base_at.get((r["spec"]["form"], r["spec"]["w0_um"]))
        d = r["chi2"] - b["chi2"] if b else float("nan")
        rows.append(_row("propagation", r, meas, dchi2=d,
                         note=_note_grid(r, meas) + ". dchi2 is against the base cell at the same waist, and the "
                         "summary_propagation row reads the shift of the minimum"))
    for form, (summ, best) in summaries.items():
        kind = summ["kind"]
        w_v, w_e = pair(summ["w0"], summ["w0_err"])
        note = (f"the profile over {len([r for r in base if r['spec']['form'] == form])} waists from {min(grid_ws):g} to "
                f"{max(grid_ws):g} um on sessions {''.join(best['sessions'])}: {kind.replace('_', ' ')}. ")
        if kind == "interior_minimum":
            note += (f"w0_err_parabola_um is sqrt(2/curvature) at Delta chi2 = {DCHI2_ONE_SIGMA:g} on the whitened chi2 from "
                     f"the parabola through the best grid cell and its neighbours, the lo/hi columns the crossings at Delta "
                     f"chi2 = {DCHI2_ONE_SIGMA:g} and at chi2_red = {best['chi2_red']:.3f} above the parabola's minimum, "
                     f"interpolated between grid points and blank where the grid does not resolve them. ")
        else:
            if summ["kind"].endswith("_unresolved"):
                note += (f"the Delta chi2 = {DCHI2_ONE_SIDED_95:g} crossing sits between the best cell and its neighbour, unresolved on this step: "
                         f"{summ.get('bound95_linear', float('nan')):.1f} um by linear interpolation, {summ.get('bound95_parabola', float('nan')):.1f} um by a parabola through the neighbour, and the cell is not the bound. ")
            else:
                note += (f"the bound is the Delta chi2 = {DCHI2_ONE_SIDED_95:g} crossing against the grid's edge, which at "
                         f"M2 1 is also the convolution licence edge 40 um sqrt(M2). ")
        note += ("the parameters and the power-arm checks are those of the best grid cell. the frequency axis carries "
                 "a common 0.5 per cent scale (linefit_conditions rate_relerr), so no bar on w0 below 0.5 per cent is a bar. "
                 "the model-form spread across the forms is the bar between the summary rows")
        dec = summ["w0_err"]
        rows.append(_row("summary_minimum", best, meas, dchi2=0.0, w0_um=w_v, w0_err_parabola_um=w_e, bound_kind=kind,
                         w0_bound95_um=with_decimals_of(summ["bound95"], dec), w0_lo_um=with_decimals_of(summ["lo1"], dec),
                         w0_hi_um=with_decimals_of(summ["hi1"], dec),
                         w0_lo_overdispersed_um=with_decimals_of(summ["lo_od"], dec),
                         w0_hi_overdispersed_um=with_decimals_of(summ["hi_od"], dec),
                         chi2=sig2(summ["chi2_min"]), note=note))
        bp = beta_profile_read(best)
        rows.append(_row("summary_beta_profile", best, meas, dchi2=0.0, w0_um=w_v, w0_err_parabola_um=w_e, bound_kind=kind,
                         note=(f"beta_self at the profile's best cell read off its PROFILE against the theory prior "
                               f"{BETA_THEORY_KHZ:.2f} +- {BETA_THEORY_ERR_KHZ:.2f} kHz per 1e12 cm^-3 (vanderwaals"
                               f".beta_self_anchored, Zameroski's 7S rate scaled, on the Steck density law): the free minimum "
                               f"at {best['params']['beta_rel']:.3f} times theory, and dchi2 with beta pinned at 0, theory, 5x "
                               f"and 20x theory of {bp['dchi2_beta_0']:.1f}, {bp['dchi2_beta_theory']:.1f}, "
                               f"{bp['dchi2_beta_5x']:.1f} and {bp['dchi2_beta_20x']:.1f}. beta_profile_1sigma_hi_khz and "
                               f"beta_profile_ub95_khz are the Delta chi2 = 1 and 2.71 crossings interpolated in beta between "
                               f"those points. the Hessian bar beside it is the curvature of a wall where beta sits at zero "
                               f"and is not the number to quote. the prior is reported against and never multiplied into the "
                               f"likelihood")))
        for sess in best["sessions"]:
            if sess not in best["preds"]:
                continue
            m = meas.get(sess)
            if m is None:
                continue
            ck = power_arm_check(best["preds"][sess], m["ratio"], m["bar"])
            lo_w, hi_w = SESSION_LADDER_W[sess]
            per = ", ".join(f"{pk} {v[0]:.4f} +- {v[1]:.4f}" for pk, v in sorted(m.get("per_peak", {}).items()))
            rows.append(_row("power_arm_session", best, meas, dchi2=0.0, sessions=sess, w0_um=w_v,
                             power_ratio_pred=f"{best['preds'][sess]:.4f}",
                             power_ratio_pred_fitted_omega=f"{best['preds_fitted'][sess]:.4f}",
                             power_ratio_meas=f"{m['ratio']:.4f}", power_ratio_bar=f"{m['bar']:.4f}",
                             power_arm_pull=sig2(ck["pull"]), power_arm_refused=str(ck["refused"]),
                             power_lo_w=f"{lo_w:g}", power_hi_w=f"{hi_w:g}",
                             note=(f"session {sess}, {SESSIONS[sess]}: the model's {hi_w * 1e3:g} over {lo_w * 1e3:g} mW width "
                                   f"ratio at the tied Omega (scale 1) with everything else at the best cell's values against the "
                                   f"session's measured ratio ({m['source']}, per peak {per}), refused above "
                                   f"{POWER_ARM_REFUSAL_BARS:g} bar. the P^2 lever of this ladder against the campaign's is "
                                   f"{(hi_w / 0.225) ** 2:.2f}")))
        pooled = pooled_power_arm(best["preds"], meas)
        rows.append(_row("power_arm_pooled", best, meas, dchi2=0.0, w0_um=w_v,
                         power_arm_pull=sig2(pooled["pull"]), power_arm_refused=str(pooled["refused"]),
                         power_ratio_bar=(f"{pooled['bar']:.4f}" if np.isfinite(pooled["bar"]) else ""),
                         note=(f"the sessions' (predicted minus measured) width ratios combined by inverse variance over "
                               f"{pooled['n_sessions']} sessions at the best cell, refused above {POWER_ARM_REFUSAL_BARS:g} "
                               f"bar of the pooled bar")))
        arm_cells = [r for r in arms if r["spec"]["form"] == form]
        for (m2, cyc) in sorted({(r["spec"]["m2"], r["spec"]["cycles"]) for r in arm_cells}):
            sub = sorted((r for r in arm_cells if r["spec"]["m2"] == m2 and r["spec"]["cycles"] == cyc), key=lambda r: r["spec"]["w0_um"])
            at_min = min(sub, key=lambda r: abs(r["spec"]["w0_um"] - best["spec"]["w0_um"]))
            b = base_at[(form, at_min["spec"]["w0_um"])]
            parts = []
            for r in sub:
                bb = base_at.get((form, r["spec"]["w0_um"]))
                parts.append(f"{r['spec']['w0_um']:g} um {r['chi2'] - bb['chi2']:+.1f}" if bb else f"{r['spec']['w0_um']:g} um n/a")
            rows.append(_row("summary_arm", at_min, meas, dchi2=at_min["chi2"] - b["chi2"],
                             note=(f"the M2 {m2:g}, depletion {cyc:g} cycles arm at the base profile's best waist: dchi2 against "
                                   f"the base arm there, and across the waists it was run at: {', '.join(parts)}. "
                                   f"the licence edge for this M2 is {40.0 * math.sqrt(m2):.1f} um and the row's z_ratio is the arm's. "
                                   f"a negative dchi2 is the arm fitting the archive better than the base form at that waist")))
        prop_cells = [r for r in props if r["spec"]["form"] == form]
        base_ws = sorted({r["spec"]["w0_um"] for r in prop_cells})
        if base_ws:
            base_sub = profile_summary(base_ws, [base_at[(form, w)]["chi2"] for w in base_ws])
        for prop in PROPAGATIONS:
            sub = sorted((r for r in prop_cells if tuple(r["spec"]["propagation"]) == prop), key=lambda r: r["spec"]["w0_um"])
            if not sub:
                continue
            ps = profile_summary([r["spec"]["w0_um"] for r in sub], [r["chi2"] for r in sub])
            shift = (ps["w0"] - base_sub["w0"]) if (ps["kind"] == "interior_minimum" and base_sub["kind"] == "interior_minimum") else float("nan")
            at_min = min(sub, key=lambda r: abs(r["spec"]["w0_um"] - best["spec"]["w0_um"]))
            b = base_at[(form, at_min["spec"]["w0_um"])]
            rows.append(_row("summary_propagation", at_min, meas, dchi2=at_min["chi2"] - b["chi2"],
                             w0_shift_um=with_decimals_of(shift, base_sub["w0_err"]),
                             note=(f"the {prop[0]} {prop[1]:+d} sigma edge" if prop[0] != "law" else f"the {prop[1]} density law")
                             + f" refit at {', '.join(f'{w:g}' for w in base_ws)} um: w0_shift_um is the move of the three-point "
                             f"parabola's vertex against the base cells' own three-point vertex ({base_sub['w0']:.2f} um, "
                             f"{base_sub['kind'].replace('_', ' ')}), blank when either is at an edge. dchi2 is against the base cell "
                             f"nearest the best waist. the shift is the propagated bar for this pinned term"))
    for w in widths:
        row = dict.fromkeys(COLUMNS, "")
        v, ev = pair(w["slope"], w["err"])
        row.update(row_kind=w["kind"], sessions=w["sess"], peak=w["peak"], width_slope_per_w=v, width_slope_err_lsq_per_w=ev,
                   width_slope_sign=("" if not np.isfinite(w["slope"]) else "+" if w["slope"] > 0 else "-"),
                   status="DIAGNOSTIC",
                   note=(f"d ln(width) / dP in per watt from {w['source']}, a weighted straight line through the ladder's "
                         f"rungs with its least-squares bar. read before any reading of the Omega scale: a width that falls "
                         f"with power is what pulls the saturation scale below its prior"))
        rows.append(row)
    for d in dropped:
        row = dict.fromkeys(COLUMNS, "")
        row.update(row_kind="dropped_trace", sessions=d["session"], peak=d["peak"], power_lo_w=f"{d['P_W']:g}",
                   n_traces=str(d["n"]), status="DIAGNOSTIC", note=d["reason"] + ". power_lo_w is the trace's power in watts")
        rows.append(row)
    for lr in laws_rows:
        row = dict.fromkeys(COLUMNS, "")
        row.update(row_kind="noise_law", sessions=lr["sess"], peak=lr["peak"], power_lo_w=f"{lr['P_W']:g}",
                   noise_a_v=sig2(lr["a"]), noise_b_v=sig2(lr["b"]), noise_tau_int=sig2(lr["tau_int"]),
                   n_traces=str(lr["n"]), status="DIAGNOSTIC",
                   note=("sigma^2 = a^2 + bV fitted from this condition's own wing samples with rb5s6s.noise"
                         ".condition_noise_model, the estimator results/noise_model.csv was produced with, and its "
                         "integrated correlation time, because that file carries no row for this session. power_lo_w "
                         "is the condition's power in watts"))
        rows.append(row)
    return rows, summaries


def write_csv(path, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    _refuse_ragged_rows(path)


def _refuse_ragged_rows(path) -> None:
    with open(path, newline="", encoding="utf-8") as fh:
        rows_ = list(csv.reader(fh))
    if any(len(r_) != len(rows_[0]) for r_ in rows_[1:]):
        raise SystemExit(f"run_ultra_joint: a row's length differs from the header's {len(rows_[0])}")


# ------------------------------------------------------------------ the gate
def session_verdicts(rec) -> dict:
    """Per session, the two z's and the word, with the wing's sign carried.

    THE WORDS. WING-LAW when the wing's chi2_red sits more than SESSION_Z_MAX
    sigma BELOW one, which only the noise law can produce; WING-OFF when it sits
    that far ABOVE, which is the noise law OR the model's far wing and the
    statistic cannot separate them; MISFIT when the core's sits above;
    UNDER-COST when the core's sits below; ADMITTED otherwise. The old single
    WING-OFF covered both signs and read as one diagnosis.

    **AND EVERY z HERE IS A LOWER BOUND.** `linear` divides by sqrt(tau), so
    E[chi2] = n/tau and Var[chi2] = 2 n tau2 / tau^2 with tau2 = sum_k rho_k^2,
    giving sd(chi2_red) = sqrt(2 tau2 / n). This divides by sqrt(2/n_eff) =
    sqrt(2 tau / n) instead, and tau2 <= tau, so the divisor is too LARGE and
    every z too small -- the false-pass direction. `results/noise_model.csv`
    carries tau_int and rho1 and not the rho series, so tau2 cannot be computed
    from it: the measured factor is 1.5 to 3 (tau2/tau about 0.4 at tau 2.4 and
    near 0.1 at 20, a long weak tail rather than an exponential). The bound is
    reported beside the value so a reader cannot take the z for the z.
    """
    out = {}
    for s, halves in (rec.get("chi2_split_session") or {}).items():
        zs = {}
        for half in ("core", "wing"):
            c, n = halves[half]
            zs[half] = (c / max(n, 1.0) - 1.0) / math.sqrt(2.0 / max(n, 1.0))
        word = ("WING-LAW" if zs["wing"] < -SESSION_Z_MAX
                else "WING-OFF" if zs["wing"] > SESSION_Z_MAX
                else "MISFIT" if zs["core"] > SESSION_Z_MAX
                else "UNDER-COST" if zs["core"] < -SESSION_Z_MAX else "ADMITTED")
        out[s] = dict(z_core=zs["core"], z_wing=zs["wing"], word=word,
                      z_is_lower_bound=True, z_inflation_range=(1.5, 3.0))
    return out


def session_verdicts_text(rec) -> str:
    v = session_verdicts(rec)
    return " ".join(f"{s}:{d['word']}(core {d['z_core']:+.0f}, wing {d['z_wing']:+.0f})" for s, d in sorted(v.items()))


def gate_checks(base, summaries, meas, coarse: bool) -> list[tuple[str, bool, str]]:
    """The rung gate in round_gate.py's form: every check with its value. A
    run that fails any check does not earn the next rung."""
    checks = []

    def chk(name, ok, detail):
        checks.append((name, bool(ok), detail))
    chk("every base cell's centres settled", all(r["centre_moved"] < CENTRE_TOL_MHZ for r in base),
        f"max last centre move {max(r['centre_moved'] for r in base):.3f} MHz over {len(base)} cells, tolerance {CENTRE_TOL_MHZ}")
    sp = max(r["spread"] for r in base)
    # A START SPREAD BETWEEN 2 AND 10 IS A SYSTEMATIC, NOT A REFUSAL (2026-09-14):
    # three runs gave identical minima with a spread of 3.5 to 3.7, which the
    # rows carry in start_spread_chi2 beside every cell; above 10 the minimum is
    # not one minimum and the rung is refused.
    chk("start spread below 10 in whitened chi2 at every base cell (2 to 10 is carried as the start systematic)", sp < 10.0, f"max spread {sp:.2f}")
    bad = [n for r in base for n, v in r["errs"].items() if not np.isfinite(v)]
    chk("every Hessian bar finite", not bad, f"non-finite: {sorted(set(bad))}" if bad else "all finite")
    for form, (summ, best) in summaries.items():
        chk(f"{form}: a shape minimum or bound found", summ["kind"] in ("interior_minimum", "one_sided_upper_bound", "one_sided_lower_bound"),
            f"{summ['kind']} at w0 = {summ['w0']:.2f} um" + (f" +- {summ['w0_err']:.2f} (parabola)" if np.isfinite(summ["w0_err"]) else "")
            + (f", bound95 {summ['bound95']:.2f}" if np.isfinite(summ["bound95"]) else ""))
        for sess in best["sessions"]:
            if sess in SESSION_LADDER_W:
                m = meas.get(sess)
                ok = sess in best["preds"] and m is not None and np.isfinite(m["bar"])
                ck = power_arm_check(best["preds"][sess], m["ratio"], m["bar"]) if ok else dict(pull=float("nan"), refused=False)
                chk(f"{form}: power-arm verdict for session {sess} recorded", ok and np.isfinite(ck["pull"]),
                    (f"pred {best['preds'][sess]:.4f} vs meas {m['ratio']:.4f} +- {m['bar']:.4f}, pull {ck['pull']:+.2f}, "
                     f"{'REFUSED' if ck['refused'] else 'passes'}") if ok else "no measured ratio for this session")
        pooled = pooled_power_arm(best["preds"], meas)
        chk(f"{form}: pooled power-arm verdict recorded", np.isfinite(pooled["pull"]),
            f"pooled pull {pooled['pull']:+.2f} over {pooled['n_sessions']} sessions, {'REFUSED' if pooled['refused'] else 'passes'}")
        bp = beta_profile_read(best)
        chk(f"{form}: beta profile present at the best cell", all(np.isfinite(bp[f"dchi2_beta_{k}"]) for k in ("0", "theory", "5x", "20x")),
            f"dchi2 at beta 0/theory/5x/20x: {bp['dchi2_beta_0']:.1f}/{bp['dchi2_beta_theory']:.1f}/{bp['dchi2_beta_5x']:.1f}/{bp['dchi2_beta_20x']:.1f}, "
            f"free minimum {best['params']['beta_rel']:.3f} x theory")
        chk(f"{form}: chi2_red inside [0.8, 2.0] at the best cell", 0.8 <= best["chi2_red"] <= 2.0, f"chi2_red {best['chi2_red']:.3f}")
        # THE WALL STOOD IN FOR TWO CHECKS (W1i finding): the Gaussian's beta at 5.8 x theory
        # was the mixed form's gamma_l divided by n(130 C) to 0.3 per cent, and its per-session
        # laser widths sat above the record's bound; a form whose profile puts the theory
        # coefficient past 3 sigma has failed on beta, and a session whose laser width has
        # taken the transit has failed on sigma_L, each refused in words.
        _bt = beta_profile_read(best).get("dchi2_beta_theory", float("nan"))
        chk(f"{form}: the theory coefficient inside the beta profile's 3 sigma at the best cell", np.isfinite(_bt) and _bt <= BETA_THEORY_DCHI2_MAX,
            f"dchi2 at theory {_bt:.1f} against {BETA_THEORY_DCHI2_MAX:g}")
        _sl = {k: v for k, v in best["params"].items() if k.startswith("sigma_l") and np.isfinite(v)}
        _over = {k: v for k, v in _sl.items() if v > SIGMA_L_MAX_MHZ}
        chk(f"{form}: every laser width under the record's {SIGMA_L_MAX_MHZ:g} MHz transition-axis bound at the best cell", not _over,
            "all under" if not _over else "over: " + ", ".join(f"{k} {v:.2f}" for k, v in sorted(_over.items())))
        # A SESSION'S NOISE LAW SETS ITS VOTE (2026-09-14): a session whose rows cost
        # nothing has free nuisances, and one whose rows cost too much is misfit;
        # either refuses the cell and names the session.
        # ABSOLUTE, IN TWO HALVES (W1m, A254): the wing against the noise law, the core against the
        # model, each 1 +- sqrt(2/n_eff) per session; the word names which failed.
        _v = session_verdicts(best)
        _bad = {s: d for s, d in _v.items() if d["word"] != "ADMITTED"}
        chk(f"{form}: every session's wing within {SESSION_Z_MAX:g} sigma of its noise law and its core within {SESSION_Z_MAX:g} sigma of the model at the best cell", bool(_v) and not _bad,
            "no per-session split in this cell" if not _v else ("all admitted: " if not _bad else "") + session_verdicts_text(best))
        # A SESSION'S VOTE IS ITS EFFECTIVE SAMPLE (W1j finding F4): the evening session held 48 per
        # cent of n_eff with 20 per cent of the traces because its tau_int sat at the white floor, and
        # no other session calibrates that whitening.
        _ne, _nt = best.get("n_eff_session") or {}, best.get("n_traces_session") or {}
        _te, _tt = (sum(_ne.values()) or 1.0), (sum(_nt.values()) or 1.0)
        _heavy = {s for s in _ne if _nt.get(s) and (_ne[s] / _te) / (_nt[s] / _tt) > SESSION_VOTE_SHARE_MAX}
        chk(f"{form}: no session's share of n_eff exceeds {SESSION_VOTE_SHARE_MAX:g} times its share of the traces", bool(_ne) and not _heavy,
            "no per-session n_eff in this cell" if not _ne else ("shares: " + ", ".join(
                f"{s} {100 * _ne[s] / _te:.0f}% of n_eff with {100 * _nt.get(s, 0) / _tt:.0f}% of traces" + (" REFUSED" if s in _heavy else "") for s in sorted(_ne))))
        chk(f"{form}: no parameter at a wall in the best cell", not best.get("at_bound"), "none" if not best.get("at_bound") else "at a bound: " + " ".join(best["at_bound"]))
        worst = max((beta_profile_read(r)["free_above_profile_min"] for r in base if r["spec"]["form"] == form), default=0.0)
        chk(f"{form}: the free fit is the beta profile's minimum at every waist", worst <= DCHI2_ONE_SIGMA,
            f"the free minimum sits at most {worst:.2f} above the lowest fixed-beta refit (a converged free fit sits at 0)")
    return checks


def _append_gate_row(csv_path, row) -> None:
    """Append the gate row to the CSV just written, in its own column order."""
    import csv as _csv
    with Path(csv_path).open("a", newline="", encoding="utf-8") as fh:
        _csv.writer(fh).writerow([row.get(c, "") for c in COLUMNS])


def write_gate(path, run_name, checks) -> bool:
    ok = all(c[1] for c in checks)
    lines = [f"RUNG GATE {run_name}: {'PASS -- the next rung is earned' if ok else 'REFUSE -- re-run at the same budget'}"]
    lines += [f"  [{'ok' if good else 'FAIL'}] {name}: {detail}" for name, good, detail in checks]
    lines.append(f"GATE {'PASS' if ok else 'REFUSE'}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines), flush=True)
    return ok


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, (np.floating, np.integer)):
        return float(x)
    if isinstance(x, np.ndarray):
        return [float(v) for v in x]
    if isinstance(x, float) and not np.isfinite(x):
        return None
    return x


def bounds_for(name):
    """The box of a parameter by its name, the rule Cell.bounds uses, for a cell read back
    without a Cell."""
    for k in ("beta_rel", "alpha_rel", "sigma_l", "omega_scale", "gamma_l", "lograte", "power_scale"):
        if name.startswith(k):
            return BOUNDS[k]
    raise KeyError(name)


def at_bound_of(names, values, bars):
    """The at-bound rule, one function for the fit and for a cell read back."""
    return [n for n, v, b in zip(names, values, bars)
            if min(abs(v - bounds_for(n)[0]), abs(v - bounds_for(n)[1]))
            <= max(0.5 * (b if np.isfinite(b) else 0.0), 0.02 * max(abs(v), 0.05))]


STALE_WALLS: list = []


def _from_json(r):
    r = dict(r)
    # A STORED WALL IS THE BOX OF ITS FIT TIME (W1i, 2026-09-14): nine committed
    # cells named lograte_E_4154 at ln 0.75 as a wall after the box had moved to ln 0.5, and
    # the gate refused on a flag the committed code could not regenerate. The flag is
    # recomputed against the live box; a disagreement is collected and the caller refuses
    # unless --accept-stale-walls <reason> is given, in which case the live reading stands.
    if "p_vector" in r and "names" in r and "errs" in r:
        live = at_bound_of(r["names"], r["p_vector"], [float("nan") if r["errs"].get(n) is None else float(r["errs"][n]) for n in r["names"]])
        if sorted(live) != sorted(r.get("at_bound", [])):
            STALE_WALLS.append((r["spec"].get("form"), r["spec"].get("w0_um"), list(r.get("at_bound", [])), live))
            r["at_bound_stored"] = list(r.get("at_bound", [])); r["at_bound"] = live
    if r["spec"].get("propagation") is not None:
        r["spec"]["propagation"] = tuple(r["spec"]["propagation"])
    r["errs"] = {k: (float("nan") if v is None else v) for k, v in r["errs"].items()}
    return r


# ------------------------------------------------------------------ the stages
def stage2_specs(base, grid_ws, coarse: bool, da, common) -> tuple[list[dict], list[dict]]:
    """The M2 and depletion arms at the best waist and the two grid edges (the
    best waist alone on the coarse grid), and the propagation arms at the best
    waist and its two neighbours, each warm-started from the base cell at the
    same waist, without the beta profile."""
    arms, props = [], []
    grid_ws = sorted(grid_ws)
    for form in FORMS:
        cells = [r for r in base if r["spec"]["form"] == form]
        if not cells:
            continue
        best = min(cells, key=lambda r: r["chi2"])
        w_best = best["spec"]["w0_um"]
        warm = {r["spec"]["w0_um"]: [r["p_vector"]] for r in cells}
        arm_ws = [w_best] if coarse else sorted({grid_ws[0], w_best, grid_ws[-1]})
        for m2 in M2_ARMS:
            for cyc in DEPLETION_ARMS:
                if m2 == 1.0 and cyc == 0.0:
                    continue
                for w in arm_ws:
                    arms.append(_spec(form, w, m2=m2, cycles=cyc, starts=warm[w], da=da, beta_profile=False, **common))
        j = grid_ws.index(w_best)
        lo, hi = max(j - 1, 0), min(j + 1, len(grid_ws) - 1)
        if hi - lo < 2:
            lo, hi = (0, min(2, len(grid_ws) - 1)) if j == 0 else (max(len(grid_ws) - 3, 0), len(grid_ws) - 1)
        for prop in PROPAGATIONS:
            for w in grid_ws[lo:hi + 1]:
                props.append(_spec(form, w, propagation=prop, starts=warm[w], da=da, beta_profile=False, **common))
    return arms, props


def base_specs(forms, grid_ws, da, common, starts=None, max_nfev=None, beta_profile=True):
    extra = dict(common)
    if max_nfev is not None:
        extra["max_nfev"] = max_nfev
    return [_spec(f, w, starts=starts, da=da, beta_profile=beta_profile, **extra) for f in forms for w in grid_ws]


def design_spec(rows, sessions):
    return dict(rows=rows, sessions=list(sessions))


def plant_determinism(workers_many: int = 2) -> bool:
    """One worker against many on a tiny problem: one canonical trace per
    condition, two waists, one start, two inner evaluations, no beta profile.
    The rows must be identical in every digit, since each cell depends only
    on its own arguments."""
    rows = design(traces_per_condition=1)
    dspec = design_spec(rows, ("P", "T"))
    da = deep_delta_alpha()
    specs = base_specs(("mixed",), (41.0, 90.0), da, {}, starts=(START_SIGMA_L["mixed"][:1] * 2 + (START_OTHER[0][1], START_OTHER[0][2]),),
                       # the start follows the PINNED default's name order (sigma_l per session, omega, gamma_l)
                       max_nfev=2, beta_profile=False)
    for s in specs:
        # the plant measures the pool's ORDER, not a node of the model: the 41 um probe sits
        # below the validated span, so it opens the gate's one door and says so in the row.
        # MOVED from 40.0 (O44/F280, 2026-09-21): the actual-focus on-axis factor now refuses
        # below this bore's own geometric floor (about 40.89 um, F280), and 40 um sits under it
        # -- a probe below the FLOOR is not "below the validated span", it describes no beam this
        # bench can make at all, which is a different edge than this plant means to exercise.
        s["kernel_gate"] = "legacy"
        # F324/A134 (C6b): this plant measures the pool's ORDER, never a physical value, and the
        # 90 um probe sits outside bloch_fraction's twelve-node grid (41 to 45 um); clamp rather
        # than let an unrelated refusal stand in for the determinism check this function is.
        s["bloch_fraction_clamp"] = True
    seq = run_cells(specs, dspec, 0, label="seq ")
    par = run_cells(specs, dspec, workers_many, label=f"pool{workers_many} ")
    strip = lambda rs: [{k: v for k, v in r.items() if k != "seconds"} for r in rs]   # noqa: E731
    return repr(strip(seq)) == repr(strip(par))



def _moment_arm_twin(w0_um: float, out_name: str) -> int:
    """THE MOMENT VECTOR ON THE TWIN, at every level whose rung is recorded PASS, and a REFUSED row for
    every level that is not (owner, 2026-09-19 02:40; PLAN v3 D11).

    The archive arm above is gated on `ladder_gate.real_traces("ultra_joint_moments")`, which nothing in
    the tree could climb until 2026-09-19 (F142) and which fails at its noiseless rung on k7@13 (F144)
    until the floor in `moment_arm` admits the vector. This arm reads NO real trace: the traces are
    injected through the closure's own route at the band's waist, so it is ladder-exempt in the same sense
    `_synthetic_source` is -- it is what the ladder is climbed ON. What it may WRITE is gated all the same:
    a level whose rung is not PASS gets one row that says so, with the recorded reason, and no moment is
    quoted above the last level that passed, which is the form in which the order's archive half can be delivered.
    """
    import importlib.util as _iu
    from rb5s6s import ladder_gate as _lg
    _s = _iu.spec_from_file_location("closure_for_twin_arm", ROOT / "scripts" / "run_ultra_joint_closure.py")
    CL = _iu.module_from_spec(_s); _s.loader.exec_module(CL)      # ladder-exempt: the injection's own route
    CL._W["real"] = CL._synthetic_source()
    cell_t, ptr = CL._truth(float(w0_um), True)
    out = [["case", "quantity", "value", "err", "unit", "basis", "note", "status"]]
    profile = _lg.PROFILES[_lg.profile_of("ultra_joint_moments")]
    for rung in profile:
        level = float(_lg.NOISE_SCALE[rung])
        art = _lg.ladder_dir("ultra_joint_moments") / f"{rung}.json"
        verdict, reasons = "ABSENT", ["no artefact: the rung has not been run"]
        if art.is_file():
            _d = json.loads(art.read_text()); verdict, reasons = _d.get("verdict", "?"), _d.get("reasons", [])
        if verdict != "PASS":
            out.append([f"twin@x{level:g}", "REFUSED", "", "", "", f"rung {rung} reads {verdict}",
                        " -- ".join(str(r).replace(";", ",") for r in reasons)[:400] or "no reason recorded", "ARTIFACT"])
            print(f"  twin x{level:g}: REFUSED ({rung} {verdict})", flush=True)
            continue
        syn, lv, sh = CL.inject(cell_t, ptr, CL.SEED, noise_scale=level)
        spec = dict(_spec("mixed", float(w0_um), beta_profile=False), noise_scale=(level if level > 0 else 1.0),
                    logdet=bool(level > 0))
        cell = Cell(spec, syn)
        fits = [cell.fit(list(p0), max_nfev=spec.get("max_nfev", MAX_NFEV)) for p0 in cell.starts()]
        best = min(fits, key=lambda f: f["chi2"])
        for r in cell.moment_arm(best["p"], best["centres"]):
            case = f"twin@x{level:g}_{r['session']}_{r['peak']}_{r['p_mw']}mW_{r['t_c']}C"
            if not r["admitted"]:
                out.append([case, r["statistic"], "", "", "", "refused by the arm's own admission", r["why"].replace(";", ","), "ARTIFACT"])
                continue
            out.append([case, r["statistic"], *pm_cells(r["data"], r["sem"] * r["t95"]),
                        "MHz^n" if "/" not in r["statistic"] else "dimensionless",
                        f"{r['n_rep']} twin repeats at x{level:g} of the law, rung {rung} PASS, the bar on the mean "
                        f"at the two-sided 95 per cent t-factor {r['t95']:g}",
                        f"this fit predicts {r['model']:.6g} at the same window, so the pull is {r['pull']:+.2f}. "
                        f"The statistic is compared against its own forward prediction and is not an estimator "
                        f"of an untruncated cumulant", "DIAGNOSTIC"])
        print(f"  twin x{level:g}: {sum(1 for o in out if o[0].startswith(f'twin@x{level:g}_'))} rows", flush=True)
    dest = os.path.join(str(C.RESULTS_DIR), out_name)
    # LIST ROWS, LIKE THE ARCHIVE ARM: `write_csv` is the fit's dict-row writer over COLUMNS, and calling it
    # here on 2026-09-19 wrote the fit's header into the moments file (restored from HEAD the same minute).
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(out)
    print(f"  wrote {dest}: {len(out) - 1} rows", flush=True)
    return 0

def moment_arm_run(w0_um: float = 42.0, out_name: str = "ultra_joint_moments.csv", twin: bool = False) -> int:
    """The moment arm at one waist: fit, then read orders 2 to 7 per condition.

    Owner orders O12, O13 and O17 in one arm. What it writes, per condition and
    statistic: the repeats' mean, the bar on that mean with its t-factor, this
    fit's own forward prediction of the same windowed statistic, and the pull.
    Then the cross-rung ratios, admitted on having a population moment and never
    on their size; then mu3 against power, which is a waist channel because the
    transit is the only term carrying an odd power of the waist; then a REFUSAL
    row per session.

    WHAT A READER MUST NOT TAKE FROM IT. The pulls are conditional on every
    parameter this cell pinned, the waist above all, and the arm is run at one
    waist rather than profiled over the grid. It says whether the model
    DESCRIBES the higher moments at that waist; it does not measure the waist.
    """
    rows = design()
    dspec = design_spec(rows, ("P", "T"))
    if twin:
        return _moment_arm_twin(w0_um, out_name)
    traces = _load(dspec)
    print(f"  loaded {len(traces)} traces", flush=True)
    spec = _spec("mixed", w0_um, da=deep_delta_alpha(), beta_profile=False)
    cell = Cell(spec, traces)
    starts = spec.get("starts") or cell.starts()
    fits = [cell.fit(p0, max_nfev=spec.get("max_nfev", MAX_NFEV)) for p0 in starts]
    best = min(fits, key=lambda f: f["chi2"])
    print(f"  fitted at w0={w0_um:g} um, chi2 {best['chi2']:.1f}", flush=True)
    arm = cell.moment_arm(best["p"], best["centres"])

    out = [["case", "quantity", "value", "err", "unit", "basis", "note", "status"]]
    for r in arm:
        case = f"{r['session']}_{r['peak']}_{r['p_mw']}mW_{r['t_c']}C"
        if not r["admitted"]:
            out.append([case, r["statistic"], "", "", "", "admitted on having a "
                        "population moment, never on signal-to-noise (O17)",
                        r["why"], "ARTIFACT"])
            continue
        out.append([case, r["statistic"], *pm_cells(r["data"], r["sem"] * r["t95"]),
                    "MHz^n" if "/" not in r["statistic"] else "dimensionless",
                    f"{r['n_rep']} repeats, the bar on the mean at the two-sided "
                    f"95 per cent t-factor {r['t95']:g}",
                    f"this fit predicts {r['model']:.6g} at the same window, so the "
                    f"pull is {r['pull']:+.2f}. The statistic is compared against its "
                    f"own forward prediction and is not an estimator of an "
                    f"untruncated moment", "DIAGNOSTIC"])

    # ---- mu3 AGAINST POWER, the waist channel ----------------------------
    # The transit is the only term with an odd power of the waist, and mu3 is the
    # ramp's own first-order signal, so the slope of mu3 against P at fixed
    # temperature is a waist statement in a way no even order is.
    lanes: dict = {}
    for r in arm:
        if r["admitted"] and r["statistic"] == "mu3@6":
            lanes.setdefault((r["session"], r["peak"], r["t_c"]), []).append(r)
    for key, rs in sorted(lanes.items()):
        if len(rs) < 3:
            continue
        P = np.array([r["p_mw"] for r in rs], float)
        y = np.array([r["data"] for r in rs], float)
        w = np.array([r["sem"] for r in rs], float)
        # WEIGHTED, because the comment above says so and until 2026-09-15 the
        # line below did not: np.polyfit is unweighted while the bar under it is
        # the weighted-fit variance, and the per-rung sems span a factor seven,
        # so the four published z's were wrong by a median 2.2 and one lane
        # changed SIGN between the two estimators. A producer's prose naming an
        # estimator its own code does not compute.
        _W = np.diag(1.0 / w ** 2)
        _A = np.vstack([np.ones_like(P), P]).T
        sd = float(np.linalg.solve(_A.T @ _W @ _A, _A.T @ _W @ y)[1])
        sm = np.polyfit(P, [r["model"] for r in rs], 1)[0]
        # THE SLOPE CARRIES ITS OWN BAR OR IT IS NOT A CHANNEL. Weighted
        # least squares on the rungs' own repeat bars, so a lane whose
        # "slope" is the scatter of a mu3 consistent with zero says so
        # instead of reading as a measurement.
        V = np.sum(1.0 / w ** 2) * np.sum(P ** 2 / w ** 2) - np.sum(P / w ** 2) ** 2
        sd_err = math.sqrt(np.sum(1.0 / w ** 2) / V) if V > 0 else float("nan")
        z = (sd - sm) / sd_err if sd_err > 0 else float("nan")
        out.append([f"mu3_vs_P_{key[0]}_{key[1]}_{key[2]}C", "slope_data_minus_model",
                    *pm_cells(sd - sm, sd_err), "MHz^3 per mW",
                    f"{len(rs)} power rungs at one temperature, the bar from the "
                    f"rungs' own repeat spreads",
                    f"data slope {sd:.4g} against this fit's {sm:.4g}, a difference of "
                    f"{z:+.1f} of its own bar. The transit is the only term carrying an "
                    f"odd power of the waist, so a slope mismatch here is a waist "
                    f"statement and an even order's is not -- BUT read the four peaks "
                    f"together before reading any one of them: they share the physics, "
                    f"so slopes that disagree in SIGN across them are scatter and not a "
                    f"channel, whatever each one's own bar says",
                    "DIAGNOSTIC"])

    # ---- THE REFUSAL ARM -------------------------------------------------
    # Per session, because a session's noise law and its model are graded
    # separately everywhere else in this producer and a pooled number hides
    # which one failed.
    verdicts = {}
    for sess in sorted({r["session"] for r in arm}):
        pulls = [r["pull"] for r in arm
                 if r["session"] == sess and r["admitted"] and np.isfinite(r["pull"])]
        if not pulls:
            continue
        # THE REFUSAL IS AN EXCEEDANCE COUNT AND NOT A CHI-SQUARED, and the
        # reason is the same one that governs which ratios are admitted above.
        # A bar built from n repeats makes the pull a t-statistic with
        # nu = n - 1 degrees of freedom. Its square has expectation
        # nu/(nu - 2), which is 2 and not 1 at the five repeats a condition
        # carries, and its VARIANCE is 2 nu^2 (nu - 1) / ((nu - 2)^2 (nu - 4)),
        # which does not exist at nu = 4 at all. So a mean of squares here has
        # no sd to quote a sigma against, and the first form of this arm quoted
        # one: "+194.6 sigma" on a statistic with no second moment. What IS
        # well defined at any dof is how often |t| clears its own two-sided 95
        # per cent point, which is 5 per cent under a correct model whatever nu
        # is, and that is what is counted.
        n = len(pulls)
        nu = max(int(round(np.median([r["n_rep"] for r in arm
                                      if r["session"] == sess]))) - 1, 1)
        # THE POPULATION THE TEST CAN SEE. A statistic whose model prediction sits
        # below its own bar cannot fail: its pull is (data - ~0)/sem, a test of
        # whether the DATA's cumulant is zero, with the model contributing
        # nothing. Every odd-order statistic here is in that state. Harmless in a
        # likelihood, where C^-1 down-weights it; in a pass/fail RATE it is a
        # guaranteed near-pass that dilutes the numerator, so the admission rule
        # that serves the covariance cannot serve this arm.
        live = [r for r in arm if r["session"] == sess and r["admitted"]
                and np.isfinite(r["pull"]) and r["sem"] > 0
                and abs(r["model"]) / r["sem"] >= 3.0]
        # AND A BAR IS AVAILABLE. The eighteen-plus statistics of a condition come
        # from the same traces, which is what a CLUSTER-ROBUST bar is for: cluster
        # on condition and the fraction carries its own sd without any
        # independence assumption. "No p-value can be quoted" was wrong.
        t95v = _T95.get(nu, 2.0)
        over = int(sum(1 for v in pulls if abs(v) > t95v))
        frac = over / n
        chi2 = float(np.mean(np.square(pulls)))
        expect = nu / (nu - 2.0) if nu > 2 else float("nan")
        by_cond = {}
        for r in arm:
            if r["session"] == sess and r["admitted"] and np.isfinite(r["pull"]):
                by_cond.setdefault((r["peak"], r["p_mw"], r["t_c"]), []).append(
                    abs(r["pull"]) > t95v)
        cl = np.array([np.mean(v) for v in by_cond.values()]) if by_cond else np.array([frac])
        cl_sd = float(np.std(cl, ddof=1) / math.sqrt(cl.size)) if cl.size > 1 else float("nan")
        z_cl = (frac - 0.05) / cl_sd if cl_sd and np.isfinite(cl_sd) and cl_sd > 0 else float("nan")
        live_frac = (sum(1 for r in live if abs(r["pull"]) > t95v) / len(live)) if live else float("nan")
        verdicts[sess] = (frac, n, over, chi2, expect, live_frac, len(live), z_cl, cl.size)
        out.append([f"moment_refusal_{sess}", "exceedance_fraction", f"{frac:.4g}", "",
                    "fraction", f"{over} of {n} admitted statistics clear their own "
                    f"two-sided 95 per cent t-point ({t95v:g} at {nu} dof), "
                    f"at w0={w0_um:g} um",
                    f"expectation 0.05 under a correct model at ANY number of repeats. "
                    f"Over the {len(live)} statistics whose own model prediction clears "
                    f"three times their bar -- the only ones this test can fail -- it is "
                    f"{live_frac:.3f}, and the rest are dead channels that can only "
                    f"near-pass. Clustered on the {cl.size} conditions, the fraction "
                    f"carries sd {cl_sd:.4f}, so it sits {z_cl:+.1f} sigma from 0.05. " +
                    ("REFUSED: the model does not describe this session's higher moments "
                     "at this waist" if frac > 0.25 else
                     "not refused at a quarter") +
                    ". The sigma above is CLUSTER-ROBUST on condition and needs no "
                    "independence assumption between the statistics of one condition, "
                    "which is what the sentence retracted here -- that no p-value could "
                    "be quoted -- had mistaken for an obstacle.",
                    "DIAGNOSTIC"])
        out.append([f"moment_refusal_{sess}", "mean_square_pull", f"{chi2:.4g}", "",
                    "dimensionless", f"{n} admitted statistics at w0={w0_um:g} um",
                    f"a DIAGNOSTIC and not a test. Its expectation is nu/(nu-2) = "
                    f"{expect:.3g} at {nu} degrees of freedom and NOT one, and its "
                    f"variance does not exist below five degrees of freedom, so no sigma "
                    f"may be taken from it. The exceedance row above is the test",
                    "DIAGNOSTIC"])

    dest = os.path.join(str(C.RESULTS_DIR), out_name)
    with open(dest, "w", newline="", encoding="utf-8") as fh:
        csv.writer(fh).writerows(out)
    print(f"wrote {dest} with {len(out) - 1} rows", flush=True)
    for sess, (frac, n, over, chi2, expect, lf, nl, zc, nc) in sorted(verdicts.items()):
        print(f"  {sess}: {over} of {n} beyond their own 95 per cent point "
              f"({100 * frac:.0f} per cent against an expected 5); over the {nl} with "
              f"model power it is {100 * lf:.0f} per cent; clustered on {nc} conditions "
              f"that is {zc:+.1f} sigma -- {'REFUSED' if frac > 0.25 else 'not refused'}",
              flush=True)
    return 0


def time_cells(workers_for_queue: int = 10) -> dict:
    """One mixed-form cell at each end of the grid and in the middle, timed on
    this process, and the queue line the numbers imply."""
    rows = design()
    dspec = design_spec(rows, ("P", "T"))
    t0 = time.time()
    _load(dspec)
    t_load = time.time() - t0
    print(f"  loaded {len(rows)} traces in {t_load:.1f} s", flush=True)
    da = deep_delta_alpha()
    out = {}
    for w in (41.0, 56.0, 90.0):   # C6a: the grid's two ends and a far node, the worst cells timed
        r = _cell_task((0, _spec("mixed", w, da=da, beta_profile=False), dspec))
        out[w] = r
        print(f"  cell mixed w0={w:g} um: {r['seconds']:.0f} s, {r['nfev']} evaluations over 2 starts, outer passes "
              f"{r['outer']}, chi2 {r['chi2']:.1f}, chi2_red {r['chi2_red']:.3f}, beta_rel {r['params']['beta_rel']:.2f}, "
              f"gamma_l {r['params']['gamma_l']:.3f}, sigma_l T/P {r['params']['sigma_l_T']:.2f}/{r['params']['sigma_l_P']:.2f}, "
              f"omega scale {r['params']['omega_scale']:.2f}, power ratio {r['preds']['P']:.4f}", flush=True)
    t_cell = float(np.mean([r["seconds"] for r in out.values()]))
    w_worst = max(out, key=lambda w: out[w]["seconds"])
    t_worst = out[w_worst]["seconds"]
    n_core = len(W0_GRID_UM) * len(FORMS)
    n_arms = len(FORMS) * (len(M2_ARMS) * len(DEPLETION_ARMS) - 1) * 3
    n_props = len(FORMS) * len(PROPAGATIONS) * 3
    serial = n_core * 3.0 * t_cell + (n_arms + n_props) * 0.5 * t_cell
    eff = {1: 1.0, 4: 3.0, 6: 4.5, 8: 5.0, 10: 5.5}
    speed = eff.get(min(workers_for_queue, 10), 5.0)
    wall = serial / speed
    line = (f"RB5S6S_WORKERS={workers_for_queue} .venv/bin/python scripts/run_ultra_joint.py    "
            f"# {n_core} base cells at {t_cell:.0f} s each without the beta profile (worst {t_worst:.0f} s at {w_worst:g} um), "
            f"about three times that with it, then {n_arms} arm and {n_props} propagation cells warm-started at about half "
            f"a bare cell: {serial / 3600:.1f} h serial, about {wall / 3600:.1f} h wall at a measured pool speed-up of {speed:g}; "
            f"traces load in {t_load:.0f} s per worker")
    out["queue_line"] = line
    out["t_cell"] = t_cell
    print("  " + line, flush=True)
    return out


def main() -> int:
    known = {"--coarse", "--time-cells", "--plant", "--no-stage2", "--all-sessions", "--with-excluded", "--power-scale", "--accept-stale-walls", "--moment-arm", "--moment-twin", "--separable"}
    valued = {"--form": None, "--sigma-l": "session", "--run-name": None, "--arms-only": None, "--out": None, "--drop-session": "", "--accept-stale-walls": None, "--moment-w0": None, "--gamma-l-exp": None, "--m2-arms": None}
    args = sys.argv[1:]
    for key in list(valued):
        if key in args:
            i = args.index(key)
            valued[key] = args[i + 1]
            args = args[:i] + args[i + 2:]
    form = valued["--form"]
    if form is not None and form not in FORMS:
        raise SystemExit(f"--form must be one of {FORMS}")
    if valued["--sigma-l"] not in ("session", "shared"):
        raise SystemExit("--sigma-l must be session or shared")
    bad = [a for a in args if a.startswith("-") and a not in known]
    if bad:
        raise SystemExit(f"unknown flag(s) {bad}: the flags are {sorted(known | set(valued))}")
    import rb5s6s
    print(f"  package: {os.path.realpath(rb5s6s.__file__)}", flush=True)
    if not (C.DATA_RAW_DIR / "p_sweep").is_dir():
        print(f"  {C.DATA_RAW_DIR / 'p_sweep'} is absent: this producer reads the raw traces and cannot run here. "
              f"The committed results/ultra_joint_fit.csv stands as the record", flush=True)
        # A PLANT THAT DID NOT RUN SAYS SO AND EXITS 3, never 0 (2026-09-14):
        # on the mirror, where data_raw/ is absent by design, --plant read as a pass.
        if "--plant" in sys.argv or "--time-cells" in sys.argv:
            print("PLANT NOT RUN: the raw traces are absent", flush=True); return 3
        return 0
    if "--moment-twin" in args:
        # THE TWIN ARM READS NO REAL TRACE and is therefore not behind `real_traces`; what it may WRITE is
        # gated per level inside `_moment_arm_twin` (PLAN v3 D11).
        return moment_arm_run(float(valued.get("--moment-w0") or 42.0), twin=True)
    if "--moment-arm" in args:
        # THE MOMENT ARM READS THE ARCHIVE AND IS GATED ON ITS OWN LADDER (2026-09-16): before this
        # line it returned ahead of the real_traces call below and read the archive ungated.
        # "ultra_joint_moments" is registered on the MOMENTS profile, seven noise levels in order,
        # so the arm runs on real traces only after the twin has climbed them.
        from rb5s6s import ladder_gate
        ladder_gate.real_traces("ultra_joint_moments", __file__)
        return moment_arm_run(float(valued.get("--moment-w0") or 42.0))
    if "--time-cells" in args:
        time_cells()
        return 0
    if "--plant" in args:
        ok = plant_determinism()
        print(f"  determinism plant, 1 worker against 2 on two cells: {'IDENTICAL' if ok else 'DIFFERENT'}", flush=True)
        return 0 if ok else 1
    sessions = ["P", "T"]
    if "--all-sessions" in args:
        trees = session_trees()
        missing = [f"{s}: {p} ({'empty' if p.is_dir() else 'absent'})" for s, (p, ok) in trees.items() if not ok]
        if missing:
            print("  --all-sessions: the excluded session tree(s) are not on this machine, so nothing runs: "
                  + "; ".join(missing) + ". Point RB5S6S_SESSION_20250704_DIR and RB5S6S_SESSION_20250717_DIR at the "
                  "trees (run_stark_joint.py's own paths); the committed CSV stands as the record", flush=True)
            return 0
        sessions += ["E", "M"]
    if "--with-excluded" in args:
        sessions.append("Q")
    # A SESSION WITHOUT A RULER ABSORBS THE KERNEL MISMATCH (2026-09-14, the fine grid):
    # the evening rate and laser width went to opposite walls under the Gaussian and
    # the Lorentzian kernel, so the design is also read with that session dropped.
    _drop = set(valued["--drop-session"])
    if _drop - set(sessions):
        print(f"  REFUSED: --drop-session names {sorted(_drop - set(sessions))}, not among the sessions {sessions}", flush=True)
        return 2
    sessions = [s for s in sessions if s not in _drop]
    from _producer_lock import producer_lock
    with producer_lock("run_ultra_joint"):
        # THE NOISE LADDER BINDS HERE (owner, 2026-09-15, restated twice on 2026-09-16):
        # "all analysis have to be done first on noiseless synthetic traces, then on
        # increasingly noisy synthetic traces up to the archive noise levels and only
        # after that to the real ones." This producer is the analysis that rule is most
        # about, and until now it read data_raw/ with no ladder anywhere in its path.
        #
        # `real_traces` RAISES until the noiseless, low and archive rungs of
        # `ultra_joint_waist` are recorded and all read PASS. Its rungs are written by
        # scripts/run_ultra_joint_closure.py, which injects through THIS module's own
        # forward model, so the two share one ladder as `ladder_gate`'s docstring
        # intends -- "analysis_id is a name, not a path".
        #
        # CONSEQUENCE, SAID PLAINLY: while the closure fails, this producer does not
        # run, and results/ultra_joint_fit.csv cannot be regenerated. That is the rule
        # working rather than an obstacle to route around, and the pressure it creates
        # is to repair the closure -- which is where the science is anyway.
        #
        # `--plant` and `--time-cells` are exempt and named: the first is a determinism
        # check that fits two cells and asserts one worker equals many, the second times
        # cells without reading a result. Neither draws a conclusion about the atom, and
        # a gate that blocks its own plant cannot be tested.
        if not ({"--plant", "--time-cells"} & set(args)):
            from rb5s6s import ladder_gate
            ladder_gate.real_traces("ultra_joint_waist", __file__)
        workers = n_workers()
        coarse = "--coarse" in args
        grid_ws = W0_COARSE_UM if coarse else W0_GRID_UM
        forms = (form,) if form else FORMS
        run_name = valued["--run-name"] or (f"{'coarse' if coarse else 'fine'}_{''.join(sessions)}"
                                            f"_{'-'.join(forms)}_{valued['--sigma-l']}{'_pscale' if '--power-scale' in args else ''}"
                                            f"{'_separable' if '--separable' in args else ''}")
        rows = design(with_excluded="Q" in sessions)
        dspec = design_spec(rows, sessions)
        common = dict(sigma_l=valued["--sigma-l"], power_scale="--power-scale" in args, rate_seeds=evening_rate_seeds())
        # THE JOINT LINE IS THE DEFAULT (C6b, A148, this file's own docstring above): every Cell of
        # the production grid reads the atom Monte Carlo's tabulated joint line unless --separable
        # asks for the named comparison arm, which is the transit-and-ramp convolution this file
        # built before this window (the saturated ramp density and the kernel gate's MC depletion
        # factor). `ramp`/`depletion` here are the ONLY values `volume_line` accepts beside it
        # (Cell.__init__'s own refusal), so the three travel together.
        if "--separable" not in args:
            common.update(ramp="weak", depletion="none", volume_line=True)
        if valued["--gamma-l-exp"] is not None:        # an ARM of the permeation law (GAMMA_L_EXP_ARMS); the default is F245's 0.5
            common["gamma_l_exp"] = float(valued["--gamma-l-exp"])
        if valued["--m2-arms"] is not None:            # M2 PROFILED ON THE DATA'S OWN REASON (O41): coarse arms first,
            global M2_ARMS                             # then a finer grid between two whose chi-squared differs
            M2_ARMS = tuple(float(x) for x in valued["--m2-arms"].split(","))
            if min(M2_ARMS) < 1.0:
                raise SystemExit(f"--m2-arms {M2_ARMS}: a beam quality factor is at least 1")
        session_traces, dropped = load_sessions(sessions)
        _init_worker(session_traces)
        traces = _load(dspec)
        widths = trace_widths(traces)
        meas = {"P": measured_power_ratio()}
        for sess in ("E", "M", "Q"):
            if sess in sessions:
                meas[sess] = measured_power_ratio_from_traces(widths, sess, meas["P"]["block_scatter_frac"])
        laws_rows = []
        seen = set()
        for t in traces:
            if t["session"] in ("E", "M", "Q") and (t["session"], t["peak"], t["P_W"]) not in seen:
                seen.add((t["session"], t["peak"], t["P_W"]))
                laws_rows.append(dict(sess=t["session"], peak=t["peak"], P_W=t["P_W"], a=t["law"]["a"], b=t["law"]["b"],
                                      tau_int=t["law"]["tau_int"], n=t["law"].get("n_traces", 0)))
        da = deep_delta_alpha()
        counts = {s: sum(1 for t in traces if t["session"] == s) for s in sessions}
        print(f"  run {run_name}: {len(traces)} traces {counts}, {len(grid_ws)} waists x {len(forms)} forms, "
              f"sigma_l {valued['--sigma-l']}, power scale {'--power-scale' in args}, {workers} workers. measured ladder ratios: "
              + "; ".join(f"{s} {m['ratio']:.4f} +- {m['bar']:.4f}" for s, m in meas.items())
              + f" (block scatter {meas['P']['block_scatter_mhz']:.3f} MHz, {100 * meas['P']['block_scatter_frac']:.2f} per cent). "
              f"Delta_alpha {da[0]:.1f} +- {da[1]:.1f} a.u.", flush=True)
        t0 = time.time()
        if valued["--arms-only"]:
            saved = json.loads(Path(valued["--arms-only"]).read_text(encoding="utf-8"))
            base = [_from_json(r) for r in saved["base"]]
            grid_ws = sorted({r["spec"]["w0_um"] for r in base})
            coarse = len(grid_ws) <= len(W0_COARSE_UM)
            print(f"  base grid of {len(base)} cells read from {valued['--arms-only']}", flush=True)
            if "--no-stage2" in args:
                # A RESUMMARIZE: the saved cells rewritten through the current summary code
                _arms0 = [_from_json(r) for r in saved.get("arms", [])]; _props0 = [_from_json(r) for r in saved.get("props", [])]
        else:
            base = run_cells(base_specs(forms, grid_ws, da, common), dspec, workers, label="base ", session_traces=session_traces)
        arms, props = (list(_arms0), list(_props0)) if valued["--arms-only"] and "--no-stage2" in args else ([], [])
        if STALE_WALLS and "--accept-stale-walls" not in args:
            print("  REFUSED: " + str(len(STALE_WALLS)) + " saved cell(s) carry a wall the live box does not: "
                  + "; ".join(f"{f} {w:g} um stored {s} live {l}" for f, w, s, l in STALE_WALLS[:6])
                  + ". Refit them, or pass --accept-stale-walls <reason> to read them against the live box.", flush=True)
            return 3
        if STALE_WALLS:
            print(f"  {len(STALE_WALLS)} saved cell(s) read against the live box (--accept-stale-walls): " + args[args.index("--accept-stale-walls") + 1], flush=True)
        if valued["--arms-only"]:
            fill_session_diagnostics(base, dspec, workers, session_traces)
        if "--no-stage2" not in args:
            arm_specs, prop_specs = stage2_specs(base, grid_ws, coarse, da, common)
            both = run_cells(arm_specs + prop_specs, dspec, workers, label="stage2 ", session_traces=session_traces)
            arms, props = both[:len(arm_specs)], both[len(arm_specs):]
        wrows = width_vs_power_rows(widths, meas["P"])
        rows_out, summaries = summary_rows(base, arms, props, meas, wrows, laws_rows, grid_ws, forms, dropped)
        out_path = Path(valued["--out"]) if valued["--out"] else OUT
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_csv(out_path, rows_out)
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        (GATE_DIR / f"cells_{run_name}.json").write_text(
            json.dumps(_jsonable(dict(run=run_name, sessions=sessions, base=base, arms=arms, props=props)), indent=0),
            encoding="utf-8")
        print(f"  wrote {out_path} ({len(rows_out)} rows) and {GATE_DIR / f'cells_{run_name}.json'} in "
              f"{(time.time() - t0) / 60:.1f} min", flush=True)
        for row in rows_out:
            if row["row_kind"] == "summary_minimum":
                print(f"  {row['form']:<10} {row['bound_kind']:<24} w0 {row['w0_um']} +- {row['w0_err_parabola_um']} um "
                      f"(bound95 {row['w0_bound95_um']}), chi2_red {row['chi2_red']}, beta free {row['beta_khz_per_1e12']} "
                      f"kHz/1e12, profile ub95 {row['beta_profile_ub95_khz']} kHz/1e12, omega scale {row['omega_scale']} "
                      f"(pull {row['omega_scale_pull']}), power arm P pull {row['power_arm_pull']} refused "
                      f"{row['power_arm_refused']}, pooled pull {row['power_arm_pooled_pull']} refused "
                      f"{row['power_arm_pooled_refused']}", flush=True)
        _checks = gate_checks(base, summaries, meas, coarse)
        write_gate(GATE_DIR / f"gate_{run_name}.txt", run_name, _checks)
        # THE VERDICT IS IN THE FILE IT JUDGES (W1i, two findings): a cache gate file was overwritten
        # by a copy from the clone and no committed artefact carried the refusal.
        _failed = [n for n, ok, _ in _checks if not ok]
        _grow = {c: "" for c in COLUMNS}; _grow.update(row_kind="gate", sessions="".join(sessions), form="all",
                     note=("GATE REFUSE: " + ", ".join(_failed) if _failed else "GATE PASS: every check of gate_" + run_name + ".txt holds"), status="DIAGNOSTIC")
        _append_gate_row(out_path, _grow)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
