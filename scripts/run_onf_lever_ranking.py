#!/usr/bin/env python
"""Which nanofibre knob buys the most, ranked by information per hour.

WHY THIS EXISTS. The owner's five ONF knobs are recorded as apparatus
capability and the campaign case lists them, but nothing said which to spend
beam time on first. That is not a question for the owner. It is a question for
the twin, and he said so.

THE RANKING METRIC is the campaign case's own stated ordering principle:
information per unit of time, hardware change and new systematic exposure.
Time is the one this file can compute, because the twin already gives a fibre
trace's cost in minutes.

METHOD. Each lever is a linear design over its rungs. For a lever with design
matrix A and per-rung uncertainty sigma, the parameter covariance is
(A^T A / sigma^2)^-1, so the recovered precision follows from the rung
placement alone. That is a Fisher forecast and not a fit, which is the right
tool: the question is what a design CAN identify, before anyone builds it.

WHAT IS MEASURED AND WHAT IS ESTIMATED, kept separate on purpose.
  - The per-rung WIDTH uncertainty is MEASURED, by Monte Carlo, and read from
    results/campaign_twin_forecast.csv.
  - The per-rung CENTRE uncertainty is a Cramer-Rao ESTIMATE, sigma_nu =
    Gamma / (2 * SNR_total), because the committed fitter reports width
    channels only. It is labelled ENVELOPE wherever it propagates.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

from rb5s6s.fibre import HE11Field, solve_he11, transit_fwhm

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

DIAMETER_NM = 370.0            # raj2026's fibre
TRAP_DISTANCE_NM = 400.0       # the trap distance the lock_requirement rows use
PROBE_NM = 993.4181            # the literature line
N_POINTS = 2000
NOISE_FRAC = 0.02              # the 2.8 min/trace setting, the affordable one
MIN_PER_TRACE = 2.78           # from campaign_twin_forecast at that noise
GAMMA_NAT_MHZ = 3.4925
# THE LOCK IS NO LONGER DRIFTING. The cavity lock was repaired 2026-08-16 and
# the owner states it holds. 0.04 MHz/min is the 2025 ARCHIVE's rate and is
# carried here only as the historical reference point, because a first version
# of this file applied it to a 2026 campaign and got a design conclusion that
# inverts once the lock is fixed. No committed row gives the repaired lock's
# residual, so it is SPANNED rather than guessed.
LOCK_DRIFT_2025_MHZ_PER_MIN = 0.04
LOCK_DRIFT_SPAN = (0.04, 0.01, 0.004, 0.001, 0.0)


def _committed(stem: str, quantity: str, **where: str) -> str:
    """Read one committed cell. Nothing in this file retypes a producer's value.

    Added 2026-08-28 after a hardcoded 2.7 was found standing against a
    committed 8.8 in the row it claimed to be.

    `where` NARROWS BY ANY OTHER COLUMN, and it exists because a quantity name
    is not always unique. `transit_additivity.csv` carries the same quantity
    once per kernel branch, and a reader that took the first match would have
    silently used the single-velocity number where the flux branch was meant --
    which is a smaller version of the very defect that produced that file.
    """
    with open(RESULTS / f"{stem}.csv", newline="", encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["quantity"] == quantity
                and all(r.get(k) == v for k, v in where.items())]
    if not rows:
        raise KeyError(f"no {quantity} row in results/{stem}.csv matching {where}")
    if len(rows) > 1:
        raise KeyError(
            f"{len(rows)} rows in results/{stem}.csv match {quantity} {where}. "
            "Narrow it: an ambiguous read is how a producer picks up the wrong "
            "branch without anything noticing.")
    return rows[0]["value"]


def _twin() -> dict:
    out = {}
    with open(RESULTS / "campaign_twin_forecast.csv", newline="",
              encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[(r["arm"], r["quantity"], r["basis"])] = r["value"]
    return out


def _fisher_sigma(design: np.ndarray, sigma_per_rung) -> np.ndarray:
    """One-sigma on each parameter of a linear design, per the Fisher inverse.

    `sigma_per_rung` may be a scalar OR a per-rung array. It was scalar-only
    until 2026-08-28, and that is correct exactly while the lock drift
    dominates, because drift is power-independent. **The lock was repaired, so
    it does not dominate any more**, and in the photon-limited regime the
    centre precision of a two-photon line goes as 1/P: the rate goes as P^2,
    counts go as P^2, and the centre error goes as one over the square root of
    counts. Over the 20x power span this lever uses, that is a factor of 20
    between the noisiest and quietest rung, and the noisiest rungs are the ones
    that determine the INTERCEPT, which is the surface shift.
    """
    sig = np.atleast_1d(np.asarray(sigma_per_rung, dtype=float))
    if sig.size == 1:
        sig = np.full(design.shape[0], float(sig[0]))
    fisher = design.T @ np.diag(1.0 / sig ** 2) @ design
    return np.sqrt(np.diag(np.linalg.inv(fisher)))


from _producer_lock import take_producer_lock     # noqa: E402


def main() -> None:
    take_producer_lock("run_onf_lever_ranking")
    twin = _twin()
    mode = solve_he11(DIAMETER_NM, PROBE_NM)
    _fld = HE11Field(DIAMETER_NM, PROBE_NM)
    lam_int_nm = mode.intensity_decay_nm

    sigma_width = float(twin[("onf", "lorentzian_excess_0.02_err", "noise 0.02")])

    # Centre precision. THE PHOTON-LIMITED TERM IS NOT THE BINDING ONE and a
    # first version of this file used it alone, landing 520 times better than
    # the record's own committed per-trace centre precision. The lock drifts,
    # which is the entire reason this record reads shapes and not centres, and
    # a trace that takes minutes accumulates that drift.
    gamma_tot = GAMMA_NAT_MHZ + 0.12          # natural plus the fibre excess
    snr_total = (1.0 / NOISE_FRAC) * math.sqrt(N_POINTS)
    sigma_photon = gamma_tot / (2.0 * snr_total)
    sigma_drift = LOCK_DRIFT_2025_MHZ_PER_MIN * MIN_PER_TRACE
    sigma_centre = math.hypot(sigma_photon, sigma_drift)

    rows = []

    def add(lever, quantity, value, unit, basis, note, status):
        rows.append(dict(lever=lever, quantity=quantity, value=value,
                         unit=unit, basis=basis, note=note, status=status))

    add("_inputs", "sigma_width_per_rung", round(sigma_width, 5), "MHz",
        "campaign_twin_forecast, noise 0.02",
        "MEASURED by Monte Carlo through the committed fitter", "ENVELOPE")
    add("_inputs", "sigma_centre_photon", round(sigma_photon, 5), "MHz",
        f"Cramer-Rao, Gamma/(2 SNR) at {N_POINTS} points and noise "
        f"{NOISE_FRAC}",
        "the photon-limited floor, and NOT the binding term", "ENVELOPE")
    add("_inputs", "sigma_centre_drift", round(sigma_drift, 5), "MHz",
        f"{LOCK_DRIFT_2025_MHZ_PER_MIN} MHz per min over a {MIN_PER_TRACE} min trace",
        "the 2025 ARCHIVE rate, kept as the historical reference. It dominates "
        f"the photon floor by {sigma_drift / sigma_photon:.0f}x, and the lock "
        "was repaired 2026-08-16, so the rows below at this rate are the "
        "pessimistic end and not the campaign's expectation",
        "ENVELOPE")
    add("_inputs", "sigma_centre_per_rung", round(sigma_centre, 5), "MHz",
        "the two in quadrature",
        "ESTIMATED. The committed fitter reports width channels only, so every "
        "centre-channel row below inherits this",
        "ENVELOPE")

    # --- L1: molasses temperature ladder, separating transit from a floor ---
    #
    # THE ADDED WIDTH IS READ FROM ITS PRODUCER, NOT FITTED HERE. This design
    # carried a hand-fitted second-order coefficient until 2026-08-28, and it
    # was wrong: the coefficient was fitted by convolving a SINGLE squared
    # Lorentzian at the ENSEMBLE's FWHM, when the ensemble is a MIXTURE whose
    # curvature at the origin -- the thing the added width depends on -- is
    # different. A board physics seat caught it and the row was out by about a
    # factor of two.
    #
    # That quantity had by then been wrong three times in one day, all three
    # because it was a literal with no producer. LOGIC 0d.2 says the third
    # breach buys a MECHANISM, so `run_transit_additivity.py` computes it and
    # this file consumes the committed row. The kernel enters at SECOND order,
    # so the response goes as T and not as sqrt(T), and the design column is
    # built from the producer's own per-temperature widths rather than from a
    # power law asserted here.
    temps_uk = [10.0, 20.0, 50.0, 100.0, 170.0]
    t_ref = 170.0
    def _added_khz(t_uk):
        return float(_committed("transit_additivity",
                                f"added_width_{t_uk:.0f}uK",
                                branch="ensemble_flux"))

    a_ref = _added_khz(t_ref) / 1e3                      # MHz
    design = np.array([[1.0, _added_khz(t) / _added_khz(t_ref)] for t in temps_uk])
    sig = _fisher_sigma(design, sigma_width)
    add("temperature_ladder", "sigma_transit_frac",
        round(sig[1] / a_ref, 4), "fraction",
        f"{len(temps_uk)} rungs, {min(temps_uk):.0f} to {max(temps_uk):.0f} uK",
        f"the width the ladder can actually read at {t_ref:.0f} uK is "
        f"{_added_khz(t_ref):.1f} kHz on the flux branch, not the "
        f"{transit_fwhm(t_ref * 1e-6, lam_int_nm * 1e-9).fwhm_hz / 1e3:.0f} kHz "
        "of the kernel itself, because the kernel enters at SECOND order. Read "
        "from results/transit_additivity.csv, which spans the kernel branches. "
        f"This row uses the flux branch and the span is "
        f"{_committed('transit_additivity', 'added_width_170uK_band', branch='spanned')} kHz. It "
        "remains the only lever that moves the transit term against a "
        "temperature-independent floor, and this row is what that costs",
        "ENVELOPE")
    add("temperature_ladder", "hours", round(len(temps_uk) * MIN_PER_TRACE / 60.0, 2),
        "hours", f"{len(temps_uk)} rungs at {MIN_PER_TRACE} min per trace",
        "one trace per rung", "ENVELOPE")

    # --- L2: power sweep, separating the light shift from the surface shift -
    powers_mw = [0.05, 0.1, 0.2, 0.5, 1.0]
    design = np.array([[1.0, p] for p in powers_mw])
    # PER-RUNG noise. The photon term scales as 1/P and the drift term does
    # not, so the quadrature sum is power-dependent and the lever is reported
    # across the lock span rather than at the 2025 rate alone.
    p_ref = max(powers_mw)
    sigma_rung = np.array([math.hypot(sigma_photon * (p_ref / p), sigma_drift)
                           for p in powers_mw])
    sig = _fisher_sigma(design, sigma_rung)
    # READ, NOT RETYPED. This was hardcoded as 2.7 while the committed
    # S0_onf_1mW row said 8.8, so the reported fractional precision on kappa
    # was wrong by 3.3x -- and wrong in the pessimistic direction, which is
    # why no reader would have queried it. The literal was the value from
    # before the mode solve replaced the assumed area.
    # AT THE ATOM, ON THIS LEVER'S OWN FIBRE, and it was neither.
    #
    # The denominator read `S0_onf_1mW_at_400nm` from onf_candidate.csv, which
    # `run_onf_candidate.py` computes on a 400 nm fibre. This file sets
    # DIAMETER_NM = 370 and derives its mode, its profile and its whole
    # distance-scan design from that. Two fibres, one ratio, which is the
    # class this record keeps catching.
    #
    # So the shift is rebuilt here from cell quantities, which are
    # fibre-independent, through THIS fibre's own mode area and stark
    # fraction. The cell rows are committed and read, never retyped.
    s0_cell = float(_committed("onf_candidate", "S0_cell_225mW"))
    i_cell = float(_committed("onf_candidate", "intensity_cell_eff"))
    # THE STARK AREA, NOT THE POWER-BUDGET ONE. This line divided guided
    # power by `effective_area_m2`, the axial-flux area, to obtain a LIGHT
    # SHIFT. `fibre.stark_area_m2` says in terms which is which, the row's own
    # note below says a light shift scales with |E|^2 and not with the axial
    # flux, and `run_onf_candidate.py` made exactly this correction earlier in
    # the same wave.
    #
    # THE REPAIR LANDED IN ONE PRODUCER AND NOT ITS SIBLING, which is the
    # night's most repeated shape: a class fixed at one instance. The two areas
    # differ by S_z/(0.5 c eps0 <|E|^2>) = 0.77731 on this 370 nm fibre, so
    # six
    # committed rows were low by that factor and the span they feed is quoted
    # on two reader surfaces. The error ran pessimistic, which is why nothing
    # queried it.
    #
    # AND THE NUMBER IN THIS COMMENT WAS ITSELF STALE UNTIL 2026-08-29. It
    # read 0.776, the value under the retired silica index, inside the
    # paragraph explaining that a class gets fixed at one instance. The
    # paragraph was right and it was an instance of what it describes.
    a_eff_m2 = _fld.stark_area_m2()
    i_onf_1mw = 1e-3 / a_eff_m2
    stark_frac = _fld.stark_fraction_at(TRAP_DISTANCE_NM * 1e-9)
    s0_1mw = s0_cell * (i_onf_1mw / i_cell) * stark_frac
    add("_inputs", "S0_onf_1mW_at_trap_this_fibre", f"{s0_1mw:.3f}", "MHz",
        f"cell shift scaled through the {DIAMETER_NM:.0f} nm STARK area and "
        f"|E|^2 at {TRAP_DISTANCE_NM:.0f} nm",
        "computed on THIS file's fibre. It previously read a row computed on "
        "a 400 nm fibre while every other quantity here is 370 nm, and the "
        "at-400nm stark fraction differs between the two by about 30 per "
        "cent. A light shift scales with |E|^2 and not with the axial flux",
        "ENVELOPE")
    # Shared by the distance scan and by the lock-span comparison below, so
    # both are defined once here rather than in whichever block runs first.
    s0_surface = s0_1mw / stark_frac          # the same fibre, at the glass
    c3_ref = 0.5 * (0.026 + 0.066) * TRAP_DISTANCE_NM**3
    add("power_sweep", "sigma_kappa_frac", round(sig[1] / s0_1mw, 4), "fraction",
        f"{len(powers_mw)} rungs, {min(powers_mw)} to {max(powers_mw)} mW",
        "S0 goes as P and the surface shift does not, so the slope is the "
        "light shift and the INTERCEPT is the atom-surface shift. No model of "
        "the surface is needed. Computed at the 2025 archive's drifting lock, "
        "which is the pessimistic end, and the `lock_span_*` rows carry the "
        "same lever across the drift span. "
        "NO EARLIER VALUE IS NARRATED HERE ON PURPOSE: this note carried a "
        "three-step history whose terminal figure was stale within hours, "
        "twice, because a note that restates a number is a second copy of it. "
        "The correction record is in docs/HISTORY.md, which is generated",
        "ENVELOPE")
    add("power_sweep", "sigma_surface_shift", round(sig[0], 5), "MHz",
        "the intercept of the same fit",
        "this IS the Casimir-Polder measurement, and it is what the ONF group "
        "cannot get from a Rydberg probe that makes the charge it reads",
        "ENVELOPE")
    add("power_sweep", "hours",
        round(len(powers_mw) * MIN_PER_TRACE / 60.0, 2), "hours",
        f"{len(powers_mw)} rungs at {MIN_PER_TRACE} min per trace",
        "one trace per rung", "ENVELOPE")

    # --- Does the ORDER survive the lock span? MEASURED, not asserted. -----
    #
    # The record said "the order is robust to the lock and only the margin
    # moves". That was true of the numbers it was written against. It is FALSE
    # of the corrected ones: once kappa is read at the atom rather than at the
    # glass, the two best levers sit at 0.14 and 0.16, close enough that the
    # ordering turns over inside the span -- and it turns over in the
    # low-drift regime, which is where the REPAIRED lock puts us.
    # COMPARE LIKE WITH LIKE. The first version set a Fisher sigma in MHz
    # against a dimensionless sigma(kappa)/S0, so the crossover it reported
    # was between two different kinds of number and the falsification built on
    # it does not stand. Both are fractional precisions on their own parameter
    # here, which is the only comparison that means anything.
    _flip = None
    _trap = [_fld.stark_fraction_at(x * 1e-9) for x in (200., 300., 400., 500., 600.)]
    _Ad = np.array([[-x * s0_surface * g, -1.0 / x**3, g]
                    for x, g in zip((200., 300., 400., 500., 600.), _trap)])
    for _dr in LOCK_DRIFT_SPAN:
        _sd = _dr * MIN_PER_TRACE
        _sp = [math.hypot(sigma_photon * (max(powers_mw) / q), _sd)
               for q in powers_mw]
        _k = _fisher_sigma(np.array([[1.0, q] for q in powers_mw]), _sp)[1] / s0_1mw
        _sdd = [math.hypot(sigma_photon * (_trap[0] / g), _sd) for g in _trap]
        _c3 = _fisher_sigma(_Ad, _sdd)[1] / c3_ref
        if _flip is None and _c3 < _k:
            _flip = _dr
    add("lock_requirement", "lever_order_flips_below", 
        "never" if _flip is None else f"{_flip}", "MHz per min",
        "the drift at which C3 overtakes kappa, both as fractional precision "
        "on their own parameter",
        "This row compared an MHz against a dimensionless ratio until "
        "2026-08-28 and the crossover it reported was between two different "
        "kinds of number. Both sides are now fractions of their own "
        "parameter. Read the value: `never` means the order holds across the "
        "whole span and the record's original claim stands",
        "ENVELOPE")

    # --- L3: distance scan via the trap-colour ratio ------------------------
    dists_nm = [200.0, 300.0, 400.0, 500.0, 600.0]
    # Two parameters: the mode length Lambda through d(ln I)/d(1/Lambda) = -d,
    # and the differential C3 through d^-3.
    #
    # THE SENSITIVITY IS WEIGHTED BY THE INTENSITY AT THAT DISTANCE, and it
    # was not. The first version used a bare `d / lam_int_nm` column, which
    # gives the 600 nm rung MORE leverage on the decay length than the 200 nm
    # rung -- where in fact the light shift it is read from has fallen to a
    # fifth by then, so that rung carries almost no signal. An unweighted
    # design overstates what a distance scan buys and does it worst at exactly
    # the rungs that cost the most trap settling time.
    #
    # The light-shift term is S0*I(d)/I(a), so d(shift)/d(1/Lambda) goes as
    # -d * I(d)/I(a). The profile is the VALIDATED field solution, not an
    # exponential: q*a = 0.23 here and the asymptotic form is unavailable.
    # THE DESIGN CARRIES THE SHIFT, so the recovered sigmas have units.
    #
    # The first version's columns were dimensionless while sigma_per_rung is
    # in MHz, so `_fisher_sigma` returned MHz on both parameters and both were
    # labelled `fraction`. That also invalidated the lever-order comparison,
    # which was setting an MHz against a dimensionless ratio.
    #
    # The observable at rung d is the centre shift in MHz:
    #     shift(d) = S0_surface * g(d)  -  C3 / d^3
    # with g the |E|^2 profile, so the derivative columns are
    #     d(shift)/d(1/Lambda) = -d * S0_surface * g(d)      MHz per (1/nm)
    #     d(shift)/d(C3)       = -1 / d^3                     MHz per (MHz nm^3)
    _prof = [_fld.stark_fraction_at(d * 1e-9) for d in dists_nm]
    # THREE PARAMETERS, NOT TWO. The design treated s0_surface as exactly
    # known until 2026-08-28, and it is not: it is what the power sweep
    # measures, and this same file reports it to 15 per cent at the 2025 lock.
    # A distance scan cannot know its own drive amplitude a priori, and
    # amplitude against decay length is the classic degeneracy of a five-rung
    # near-exponential scan.
    #
    # Fixing it made the lever look 1.7 to 2.3 times better than it is, in the
    # flattering direction. The third column is d(shift)/d(S0) = g(d).
    design = np.array([[-d * s0_surface * g, -1.0 / d**3, g]
                       for d, g in zip(dists_nm, _prof)])
    # AND the per-rung noise falls with the signal for the same reason as the
    # power sweep: the two-photon rate goes as I^2, so the photon-limited
    # centre error goes as 1/I. The far rungs are penalised twice, once in the
    # design and once in the noise, and that is the physics rather than a
    # pessimism -- an atom 600 nm out sees a fifth of the surface intensity.
    sigma_rung_d = np.array([math.hypot(sigma_photon * (_prof[0] / g), sigma_drift)
                             for g in _prof])
    sig = _fisher_sigma(design, sigma_rung_d)
    # sig[0] is in 1/nm, so the FRACTION on Lambda is sig[0]*Lambda.
    # sig[1] is in MHz nm^3; express it against the committed CP shift at the
    # trap distance, C3 = shift * d^3, so the fraction is sig[1]/(shift*d^3).
    lam_frac = sig[0] * lam_int_nm
    c3_frac = sig[1] / c3_ref
    add("distance_scan", "sigma_lambda_frac", round(lam_frac, 4), "fraction",
        f"{len(dists_nm)} rungs, {min(dists_nm):.0f} to {max(dists_nm):.0f} nm",
        f"the mode length {lam_int_nm:.0f} nm inverts to the fibre diameter, "
        "which no held paper states a tolerance for. This lever DOES deliver "
        "it. The design must be weighted by the intensity present at each "
        "rung, must carry the shift so the fitted observable is a frequency "
        "and not a bare ratio, and must marginalise over the drive's own "
        "surface shift, which the scan cannot know a priori. "
        "NO EARLIER VALUE IS NARRATED HERE ON PURPOSE: this note carried the "
        "figure's own history and its terminal value went stale twice in one "
        "day, because a note that restates a number is a second copy of it",
        "ENVELOPE")
    add("distance_scan", "sigma_C3_frac", round(c3_frac, 4), "fraction",
        "the d^-3 column of the same design",
        "the committed C3 ratio spans 3 to 6 and no integration time closes "
        "it. This lever narrows it, and it is the WEAKER of the two "
        "parameters the scan carries rather than the stronger, because the "
        "light-shift column is large and the d^-3 column is not. NO RATIO IS "
        "NARRATED HERE: a note that restates a comparison between two rows of "
        "this file is a second copy of it, and the one that stood here said "
        "four where the rows give 6.5",
        "ENVELOPE")
    # What the decay-length precision means for the DIAMETER, which is the
    # quantity the campaign actually wants and the one the record kept
    # claiming this lever delivers.
    _h = 5.0
    _dLdd = (solve_he11(DIAMETER_NM + _h, PROBE_NM).intensity_decay_nm
             - solve_he11(DIAMETER_NM - _h, PROBE_NM).intensity_decay_nm) / (2 * _h)
    add("distance_scan", "sigma_diameter_nm",
        round(lam_frac * lam_int_nm / abs(_dLdd), 1), "nm",
        "sigma_lambda_frac carried through dLambda/dd",
        "the quantity the campaign wants, and this row has moved four times "
        "in one day. It is now MARGINALISED over the drive's own surface "
        "shift, which the scan cannot know a priori and which the power sweep "
        "measures: amplitude against decay length is the classic degeneracy "
        "of a five-rung near-exponential scan, and fixing the amplitude made "
        "the lever look about twice as good as it is. Quoted at the 2025 "
        "drifting lock, which is the pessimistic end. The `lock_span_*` rows "
        "carry it down to under a nanometre at the photon floor. A joint fit "
        "with the power sweep would narrow it, but that prior is NOT "
        "independent, since converting sigma_kappa to the surface divides by "
        "a stark fraction that depends on the diameter being fitted. SEM and "
        "the 480 nm mode-cutoff diagnostic stay as "
        "independent cross-checks",
        "ENVELOPE")
    # THE LEVERS ACROSS THE LOCK SPAN, which is what chapter 12 requires and
    # what the point rows above do not do.
    #
    # Every row above is computed at sigma_drift = 0.04 MHz/min, the 2025
    # ARCHIVE's drifting lock, and the photon floor is 0.00081 MHz against a
    # drift term of 0.111, a factor of 138. So every lever figure in this file
    # is very nearly proportional to a drift rate the record says no longer
    # applies: the lock was repaired 2026-08-16 and its residual is unmeasured.
    #
    # Quoting the 2025 value alone reports the PESSIMISTIC end of the span as
    # though it were the answer, which is the failure chapter 12 was written
    # this same wave to prevent. The point rows are kept as the historical
    # reference and these span rows are what a campaign forecast should quote.
    for _dr in LOCK_DRIFT_SPAN:
        _sd = _dr * MIN_PER_TRACE
        _sp = [math.hypot(sigma_photon * (max(powers_mw) / q), _sd)
               for q in powers_mw]
        _kf = _fisher_sigma(np.array([[1.0, q] for q in powers_mw]), _sp)[1] / s0_1mw
        _sdd = [math.hypot(sigma_photon * (_prof[0] / g), _sd) for g in _prof]
        _sg = _fisher_sigma(design, _sdd)
        _lam = _sg[0] * lam_int_nm
        add(f"lock_span_{_dr}", "sigma_diameter_nm",
            round(_lam * lam_int_nm / abs(_dLdd), 2), "nm",
            f"the distance scan at {_dr} MHz per minute of residual drift",
            "the 2025 archive rate is the first entry and the photon floor the "
            "last. The repaired lock's residual is unmeasured, so the campaign "
            "sits somewhere inside this span and not at either end",
            "ENVELOPE")
        add(f"lock_span_{_dr}", "sigma_kappa_frac",
            round(_kf, 4), "fraction",
            f"the power sweep at {_dr} MHz per minute of residual drift",
            "same span, same reason. Read the lever ranking across it rather "
            "than at the 2025 point",
            "ENVELOPE")

    add("distance_scan", "hours",
        round(len(dists_nm) * MIN_PER_TRACE / 60.0, 2), "hours",
        f"{len(dists_nm)} rungs at {MIN_PER_TRACE} min per trace",
        "one trace per rung, and the trap must settle between rungs, which is "
        "NOT costed here", "ENVELOPE")

    # --- what lock stability the surface measurement needs -----------------
    # The intercept factor is the Fisher ratio sigma_surface/sigma_centre for
    # the power design above, so this asks the same question at each lock.
    intercept_factor = _fisher_sigma(np.array([[1.0, p] for p in powers_mw]),
                                     1.0)[0]
    CP_400 = (0.026, 0.066)      # committed cp_shift scaled to the trap distance
    for drift in LOCK_DRIFT_SPAN:
        sc = math.hypot(sigma_photon, drift * MIN_PER_TRACE)
        s_surf = intercept_factor * sc
        # THE LEVER KEY CARRIES THE DRIFT RATE, so each of the five rows is
        # separately citable. They shared one key until 2026-08-28, which made
        # four of the five structurally unreachable by a `ref:` link: the
        # reference machinery resolves (file, key, quantity), so five rows
        # under one key resolve to the first and a page quoting any other one
        # fails its own reference check. The rows are different quantities --
        # the same significance at five different lock rates -- and a key that
        # cannot tell them apart is a key that hides four of them.
        add(f"lock_requirement_{drift * 1e3:.0f}kHz",
            # NAMED `_band` BECAUSE IT IS ONE. The value is an interval
            # spanning the committed C3 ratio of 3 to 6, not a central value
            # with a Gaussian error, and 8a.1 is satisfied by the quantity
            # stating its own nature rather than by attaching a sigma to a
            # systematic span. `_band` is one of the sibling suffixes the
            # uncertainty guard already recognises.
            "surface_shift_significance_at_400nm_band",
            f"{CP_400[0] / s_surf:.0f} to {CP_400[1] / s_surf:.0f}", "sigma",
            f"lock at {drift * 1e3:.0f} kHz per min",
            "Casimir-Polder at the trap distance raj2026 already runs, over "
            "the recovered surface-shift uncertainty. Below about 4 kHz per "
            "min the measurement is available WITHOUT moving atoms closer to "
            "the glass, which is the gentler configuration for the fibre",
            "ENVELOPE")

    out = RESULTS / "onf_lever_ranking.csv"
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["lever", "quantity", "value", "unit",
                                           "basis", "note", "status"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")
    for r in rows:
        print(f"  {r['lever']:<20} {r['quantity']:<24} {str(r['value']):>10} "
              f"{r['unit']}")


if __name__ == "__main__":
    main()
