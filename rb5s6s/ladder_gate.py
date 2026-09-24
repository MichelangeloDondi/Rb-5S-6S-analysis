"""GUARD noise-ladder: the real traces are reachable only after the synthetic ladder has passed.

Owner, 2026-09-15: "Make sure to make a mechanism for which every analysis is at first performed
in synthetic traces without noise, then with ones with low noise level, then in ones with archive
noise level, and only as last step in the real traces after all this validation."

A rule saying that is a rule that gets skipped the first time a real trace is one line away, so it
is a refusal instead. An analysis declares an id; its three rungs write artefacts; `real_traces`
raises until all three exist, are newer than the analysis's own file, and read PASS.

    from rb5s6s import ladder_gate
    ladder_gate.record("moment_mle", "noiseless", passed=True, detail={...})   # rung by rung
    rows = ladder_gate.real_traces("moment_mle", __file__)                     # raises unless 3/3

The rungs, and what each has to show before it writes PASS:

  noiseless  the estimator recovers the injected truth with no noise at all. A failure here is
             an arithmetic or a convention error and nothing further is worth running.
  low        at 0.3 times the archive's own noise law, the truth is recovered with coverage
             inside [nominal - 0.10, nominal + 0.10] in BOTH directions; over-coverage is an
             inflated bar and is as much a failure as under-coverage; and the coverage is a
             statement only at the realisation count where two binomial standard errors fit
             inside the band (88 at 0.68), UNRESOLVED below it (F32.3).
  archive    the same at 1.0 times the law, per condition, with the twin's bias subtracted and
             its spread validated against the five repeats.

`analysis_id` is a name, not a path, so two harnesses sharing an estimator share one ladder.
"""
from __future__ import annotations

import contextlib
import json
import pathlib
import time
from typing import Any, Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
#: THE PRODUCERS THAT PREDATE THE GATE, and this is the ONE list.
#: It lived in `private/checks/noise_ladder_gate.py` until 2026-09-16, where the static scan
#: could read it and the RUNTIME could not -- so the refusal in `ingest.load_trace` below had
#: nothing to consult and a second copy would have been two lists free to drift. It is here,
#: the scanner imports it, and `ingest` enforces it.
#: A NEW HARNESS CANNOT BE BORN WITH A DIRECT ROUTE: a caller not on this list, not under
#: `tests/`, and not inside a `ladder_gate.real_traces` call is REFUSED by the loader itself.
#: The list may only SHRINK. Paying one down means routing it through `real_traces` and
#: deleting its line.
PREDATES_THE_GATE = {
    "run_ultra_joint.py": ("analysis", "routed at the top through real_traces and NOT in its own `_load`, which the text scan cannot see and the loader can. Routing `_load` is blocked on the closure's noiseless rung, which reads FAIL at a 0.70 per cent recovery with no noise against a 0.1 tolerance; that rung is the paydown"),
    "_m25_norulers.py": ("instrument", "a manifest slice helper for the M25 set; selects rows and fits nothing"),
    "annotate_manifest_qc.py": ("instrument", "writes the manifest's own QC columns; curation, not analysis"),
    "make_fig0_spectrum.py": ("instrument", "renders one survey spectrum; a picture and not a parameter"),
    "make_figures.py": ("instrument", "draws every committed figure from the traces and the CSVs; it renders and estimates nothing"),
    "make_qc_gallery.py": ("instrument", "the QC contact sheet; it looks at traces and concludes nothing about the atom"),
    "run_amplitude_ratios.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_amplitude_trapping.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_band_excess.py": ("instrument", "a band-excess QC statistic over the raw traces; no parameter of the atom is estimated"),
    "run_beta_self.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_commit_sweep.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_cross_arm_ratios.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_digitiser_scale.py": ("instrument", "reads the vertical step out of the traces; an instrument fact"),
    "run_drift_settling.py": ("instrument", "the lock's settling from the timestamps; an apparatus fact"),
    "run_epoch_checks.py": ("instrument", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_far_wing_level.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_fit_window_scan.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_full_dataset_fit.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_global_dataset_fit.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_global_fit.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_identifiability.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_kernel_k4.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_kernel_k8.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_laser_kernel.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_lever_crosscheck.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_linefit.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_model_ladder.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_modelform.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_moment_admission.py": ("instrument", "reads data_raw/MANIFEST.csv for a trace COUNT and calls no loader; its measurement is on the twin's own world, so it already obeys the rule"),
    "run_morning_ruler.py": ("instrument", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_power_sweep.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_power_time_sign_test.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_qc.py": ("instrument", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_quantisation_check.py": ("instrument", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_ruler.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_saturation_probe.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_stark_joint.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
    "run_timestamp_audit.py": ("instrument", "reads acquisition times; touches no lineshape"),
    "run_tooth_scatter.py": ("analysis", "ladder CLIMBED and corrected (A280): at archive noise it under-recovers the injected excursion by about 17 per cent, coverage 1.00 at every rung, so the bound holds; the noiseless point estimate is 9 per cent off against a 1e-3 tolerance, which is what still keeps it unrouted"),
    "run_twin_completeness.py": ("instrument", "grades the TWIN against the archive and estimates no parameter of the atom; the ladder's archive rung depends on this measurement, so gating it on the ladder is circular"),
    "run_wing_check.py": ("analysis", "a committed producer predating the gate; reads the archive through the package's own ingest and was invisible to this scan until the import spelling was widened"),
}

RUNGS = ("noiseless", "low", "archive")
NOISE_SCALE = {"noiseless": 0.0, "low": 0.3, "archive": 1.0}
# THE MOMENTS CLIMB SEVEN LEVELS (owner, 2026-09-16: "0%-1%-3%-10%-30%-100%, maybe also 300% ...
# a mechanism to prevent you to use the twin with a certain noise level before it has been
# validated properly on the lower noise level; the high orders and their ratios are so sensible
# to noise"). A PROFILE names an analysis's rung list; `record()`'s predecessor rule then refuses a
# level whose lower level is absent or failing, whatever the profile, and `real_traces` needs the
# chain through the archive's own law. The waist keeps the three-rung default; the moment
# statistics, their ratios, the treatment matrix and the window surface are registered `moments`.
# The 300 per cent rung is the single-trace case and sits ABOVE the archive: it is recorded after
# real traces are admitted and never gates them.
PROFILES = {
    # THE WAIST PROFILE GAINS AN OPTIONAL 3.0 RUNG (PLAN v3 D10, 2026-09-19). Its measured scatter at
    # 0.3x is 0.065 um and at 1.0x about 0.2, two orders inside the +-8 um stopping bar, so the three
    # required rungs sit deep inside the regime where the waist information survives and never find
    # the edge -- and the edge is the campaign lever. A rung at three times the law brackets both the
    # real archive level (A8: the repeats scatter 1.8 to 4.1 times the twin's) and the start of the
    # death curve. It is NOT in REQUIRED: real traces open on the three, and this one is read after.
    "default": RUNGS,
    "moments": ("noiseless", "n01", "n03", "n10", "low", "archive", "n300"),
    "waist": RUNGS + ("n300",),
    # THE OWNER'S OWN GRID FOR THE BIAS SURFACE (O34, A37), and it departs from `moments` twice, both
    # deliberately. It starts at 0.1 PER CENT, a decade below this ladder's previous floor, because the
    # bias the surface reports is the replica mean minus the noiseless value at the same window and its
    # growth law is what says whether the bias is the estimator's or the model's -- a law read from
    # three decades is a law, read from one it is a slope. And it carries NO 3.0 rung: the surface is a
    # bias table, not a death curve, and a level above the archive's own never gates a real trace.
    "moment_window_bias": ("noiseless", "n001", "n003", "n01", "n03", "n10", "low", "archive"),
}
NOISE_SCALE.update({"n01": 0.01, "n03": 0.03, "n10": 0.1, "n300": 3.0, "n001": 0.001, "n003": 0.003})
REAL_GATE_RUNG = "archive"     # the rung real traces wait for, in every profile
# COARSE FIRST, REFINE ON A REASON (owner, 2026-09-17 02:40: "maybe I was too extreme to ask to run
# all cases 1-3-10-30-100-300 per cent ... think which order of computations would allow us to
# skip some of them"). A profile's REQUIRED rungs are the ones every climb must record; the
# others are REFINEMENTS, recorded only when the required ones give a reason (a pass at 10 per
# cent and a fail at the archive's own level asks for 30; a fail at 10 asks for 1 and 3). The
# order rule survives in two halves: a rung is climbable only when every required rung below it
# reads PASS, and the nearest recorded rung below it does not read FAIL.
REQUIRED = {
    "default": RUNGS,
    "waist": RUNGS,                     # real traces open on the three; the 3.0 rung is read after, never required
    "moments": ("noiseless", "n10", "archive"),
    # COARSE FIRST on the owner's grid: 0 -> 0.01 -> 0.1 -> 1.0 are required and the three between
    # them (0.001, 0.003, 0.03, 0.3) are refinements a pass-then-fail asks for, which is the same
    # discipline the `moments` profile already runs on.
    "moment_window_bias": ("noiseless", "n01", "n10", "archive"),
}
ANALYSIS_PROFILE = {
    "ultra_joint_waist": "waist",       # the three required rungs plus the optional 3.0 (PLAN v3 D10)
    "moment_mle": "moments", "ultra_joint_moments": "moments", "ultra_joint_treatments": "moments",
    "twin_windows": "moments", "window_surface": "moments", "odd_channel": "moments",
    "plant_moments": "moments",   # the self-test's own id
    "moment_window_bias": "moment_window_bias",   # O34's bias surface over window and noise
    "plant_window_bias": "moment_window_bias",    # its plant's own id
}


def profile_of(analysis_id: str) -> str:
    """The profile of an analysis id. A suffixed id, `<base>@<world or session>`, climbs its OWN ladder
    (its records sit under its own directory) on its base's profile: the plan's per-session ids (`@E`,
    `@M`, Phase 6) and the twin worlds of C6b (`@volume`, `@volume-clipped`) are the same analysis on a
    different world, so a rung passed on one world licenses nothing on another and the rungs they climb
    are the same rungs. Until 2026-09-22 a suffixed id fell to the default profile's three rungs."""
    return ANALYSIS_PROFILE.get(analysis_id.split("@", 1)[0], "default")


def rungs_of(analysis_id: str) -> tuple:
    return PROFILES[profile_of(analysis_id)]


def gating_rungs(analysis_id: str) -> tuple:
    """The rungs real traces wait for: the profile's REQUIRED chain up to and including the archive."""
    r = REQUIRED[profile_of(analysis_id)]
    return r[: r.index(REAL_GATE_RUNG) + 1]


# ---------------------------------------------------------------------------------------------
# The verdict is COMPUTED from the evidence and is NEVER passed in.  Until 2026-09-15 `record`
# took `passed: bool` from the caller, so this gate refused a MISSING rung and could not refuse a
# FALSE one: any harness could write PASS with an empty detail.  The repair removes the parameter
# outright, so a caller that still tries to hand a verdict in fails with a TypeError rather than
# being quietly believed.  `_judge` below is the only thing that can write PASS.
# ---------------------------------------------------------------------------------------------

NOISELESS_TOL = 1e-3          # a noiseless recovery is arithmetic: it closes or it does not
COVER_TOL = 0.10              # two-sided: over-coverage is an inflated bar, as bad as under
LEVEL_TOL = 1.30              # a rung's injected noise against the record's own: a FACTOR check
SPECTRUM_TOL = 1.60           # and its SHAPE: a rung at the right level may still be the wrong noise
CHI2_BAND = (0.8, 1.3)        # the gage's own band
MIN_REALISATIONS = 8          # the fewest realisations a coverage can be read on (halves of four)
RESOLVE_SE = 2.0              # a coverage is RESOLVED when this many binomial standard errors fit inside COVER_TOL


def coverage_resolved_n(nominal: float = 0.68, tol: float = COVER_TOL, k: float = RESOLVE_SE) -> int:
    """The fewest realisations at which a coverage inside the band is a statement: k standard
    errors of a binomial proportion at `nominal` fit inside `tol`, n >= k^2 nominal (1 - nominal) / tol^2,
    88 at 0.68 and 0.10 (F32.3: at eight the standard error is 0.15 and a PASS tests
    nothing; about 20 at a nominal 0.95)."""
    import math
    return int(math.ceil(k * k * nominal * (1.0 - nominal) / (tol * tol) - 1e-9))   # 19.000000000000004 is nineteen


def _need(detail, key, reasons):
    if key not in detail:
        reasons.append(f"the detail carries no {key!r}, which this rung is judged on")
        return None
    return detail[key]


def _judge(rung: str, detail: Dict[str, Any]) -> tuple:
    """(verdict, reasons).  PASS only when the evidence for THIS rung is present and inside band."""
    reasons: List[str] = []
    if rung == "noiseless":
        e = _need(detail, "max_abs_rel_error", reasons)
        if e is not None and float(e) > NOISELESS_TOL:
            reasons.append(f"noiseless recovery is off by {float(e):.3g}, over {NOISELESS_TOL:g}: "
                           "a noiseless failure is an arithmetic or convention error")
        n = _need(detail, "n_truths", reasons)
        if n is not None and int(n) < 1:
            reasons.append("no injected truth was tested")
    else:
        nominal = float(detail.get("nominal", 0.68))
        # A COVERAGE AT FEWER THAN EIGHT REALISATIONS IS NOT A STATEMENT (a reading of
        # 2026-09-17): at one realisation it can only read 0 or 1, and the closure had fed six.
        # The floor lives here, in the shared judge, and not in each producer's own hand.
        nr = _need(detail, "n_realisations", reasons)
        if nr is not None and int(nr) < MIN_REALISATIONS:
            reasons.append(f"{int(nr)} realisation(s) is under the floor of {MIN_REALISATIONS}: a coverage read on "
                           "fewer cannot be inside or outside any band")
        # THE COVERAGE JUDGED IS THE ESTIMATOR AS USED (owner, 2026-09-19 02:40; plan D6, A16): a harness
        # that subtracts the twin's bias downstream records the jackknife-corrected coverage here and
        # carries the raw one as `coverage_raw`, which this verdict reads for nothing and keeps on the
        # artefact so the raw number is never lost. A harness that does not correct records its raw
        # coverage as `coverage` and no `coverage_raw`; both forms are legal and the artefact says which.
        c = _need(detail, "coverage", reasons)
        # A COVERAGE INSIDE THE BAND AT TOO FEW REALISATIONS IS UNRESOLVED, NOT PASSED (F32.3): the
        # binomial standard error at eight is 0.15 against a band of 0.10, so an eight-realisation
        # 0.75 is compatible with 0.45 and with 1.0. The count decides, before the value is read.
        if nr is not None and int(nr) >= MIN_REALISATIONS and int(nr) < coverage_resolved_n(nominal):
            se = (nominal * (1.0 - nominal) / int(nr)) ** 0.5
            reasons.append(f"coverage UNRESOLVED at {int(nr)} realisations: {RESOLVE_SE:g} binomial standard errors "
                           f"({RESOLVE_SE * se:.2f}) exceed the {COVER_TOL:g} band. {coverage_resolved_n(nominal)} realisations resolve it")
        if c is not None and not (nominal - COVER_TOL <= float(c) <= nominal + COVER_TOL):
            reasons.append(
                f"coverage {float(c):.3f} is outside [{nominal - COVER_TOL:.2f}, {nominal + COVER_TOL:.2f}] "
                "(TWO-SIDED: over-coverage is an inflated bar and fails as hard as under-coverage)")
        x = _need(detail, "chi2_red", reasons)
        if x is not None and not (CHI2_BAND[0] <= float(x) <= CHI2_BAND[1]):
            reasons.append(f"chi2_red {float(x):.3f} is outside {CHI2_BAND}")
        # INAPPLICABLE IS NOT SATISFIED, and this key is where that bites.  The
        # 2026-09-15 rungs recorded `odd_sign_agreement: PASS` beside `orders = [2, 4]`
        # -- a check with nothing to disagree about -- which is the `passed` parameter's
        # own defect one level down.  A waist closure estimates a LOCATION and tests no
        # odd order at all, so a caller with nothing to report must SAY so rather than
        # write True, and saying so costs a reason that lands in the artefact.
        o = _need(detail, "odd_sign_agreement", reasons)
        if isinstance(o, str) and o.strip().lower() in ("n/a", "not applicable", "inapplicable"):
            why = str(detail.get("odd_sign_reason", "")).strip()
            if not why:
                reasons.append("odd_sign_agreement is declared inapplicable with no "
                               "`odd_sign_reason`: an inapplicable check states why, or it is "
                               "a pass nobody earned")
        elif o is not None and not bool(o):
            reasons.append("the odd orders disagree in sign with the twin's prediction")
        # THE RUNG'S LEVEL, NOT ONLY ITS ARITHMETIC (A280, 2026-09-16). Three harnesses
        # read this gate's `NOISE_SCALE` as a fraction of PEAK when it is a multiplier of
        # THE ARCHIVE'S OWN LAW, and injected sigma = 100 per cent of peak at the archive
        # rung where the real traces sit at a median signal-to-noise of 29.3. The noiseless
        # rung cannot catch that -- at scale zero there is nothing to scale -- so an exact
        # noiseless recovery had certified a ladder whose every noisy rung was 29x wrong.
        # A caller therefore states the ratio of the sigma it INJECTED to the sigma the
        # RECORD holds for that condition, at this rung's scale; 1.0 is correct and the
        # band is deliberately wide, because this catches a factor and not a per cent.
        lv = _need(detail, "injected_over_record", reasons)
        if lv is not None:
            try:
                lvf = float(lv)
            except (TypeError, ValueError):
                reasons.append(f"injected_over_record is not a number: {lv!r}")
            else:
                if not (1.0 / LEVEL_TOL <= lvf <= LEVEL_TOL):
                    reasons.append(
                        f"the injected noise is {lvf:.3g} times what the record holds for this "
                        f"rung, outside [{1/LEVEL_TOL:.2f}, {LEVEL_TOL:.2f}]: a rung at the wrong "
                        f"LEVEL measures a different instrument, and the noiseless rung cannot see it")
        # AND THE LEVEL IS NOT THE NOISE. `injected_over_record` compares root-mean-square
        # sigmas, so it reads exactly 1.000 for any rung whose amplitude is right --
        # including one whose noise has entirely the wrong SPECTRUM. Measured 2026-09-16:
        # the closure injects independent samples at `sigma_of_v`, which is correct on this
        # archive, and the level check reads 1.000 whether the samples are independent or
        # driven through an AR(1) at any coefficient whatever. A rung is "at the archive's
        # noise" only when it matches the record in level AND in shape, and the owner's
        # standing rule -- synthetic traces raised to the archive's own noise before any
        # real one is read -- is a rule about the noise and not about its amplitude.
        #
        # LIKE WITH LIKE, AND THAT IS THE WHOLE DESIGN. The record's `tau_int` is measured
        # by `noise.wing_correlation` on a trace that CARRIES THE LINE, and 2026-09-16
        # measured that the line's own wing curvature is what that number holds: an analytic
        # line over provably independent noise reads tau 2.31 against the archive's 2.57,
        # and removing a quadratic instead of a straight line takes the archive to 1.000.
        # So the ratio demanded here is between two readings of the SAME instrument on the
        # SAME kind of trace, never between a rung's noise and a number the record measured
        # some other way. A rung that reproduced the archive's *noise* while lacking its
        # line would read low and be refused, correctly: it is not the archive's trace.
        sp = _need(detail, "injected_tau_over_record", reasons)
        if sp is not None:
            try:
                spf = float(sp)
            except (TypeError, ValueError):
                reasons.append(f"injected_tau_over_record is not a number: {sp!r}")
            else:
                if not (1.0 / SPECTRUM_TOL <= spf <= SPECTRUM_TOL):
                    reasons.append(
                        f"the injected noise has {spf:.3g} times the record's correlation time "
                        f"for this rung, outside [{1/SPECTRUM_TOL:.2f}, {SPECTRUM_TOL:.2f}]: a rung "
                        f"at the right LEVEL with the wrong SHAPE is not at the archive's noise, "
                        f"and `injected_over_record` reads 1.000 throughout")
        b = _need(detail, "blame", reasons)
        if b is not None and not str(b).strip():
            reasons.append("the blame verdict is empty: say what the twin reproduces and what it does not")
        # THE BIAS IS TESTED BESIDE THE CORRECTED COVERAGE (the C2 physics chair, 2026-09-19): a coverage
        # judged on the jackknife-corrected estimate has mean exactly the truth for a bias of ANY size, so
        # it tests the bar against the scatter and carries no accuracy at all -- a 2 um bias passed it in
        # simulation. A harness that records `coverage_raw` has corrected, and must then also record the
        # bias with its jackknife SE; the rung refuses when the bias exceeds the median bar, which is the
        # estimator's own claimed uncertainty failing to cover its own systematic. A harness that has not
        # corrected records no `coverage_raw` and its raw coverage already carries the bias.
        if "coverage_raw" in detail:
            bb, bse, mb = detail.get("bias"), detail.get("bias_se"), detail.get("median_bar")
            if bb is None or bse is None or mb is None:
                reasons.append("a corrected coverage was recorded without `bias`, `bias_se` and `median_bar` "
                               "beside it: the correction removes the bias from the coverage, so the bias "
                               "must be tested on its own")
            else:
                try:
                    if abs(float(bb)) > float(mb):
                        reasons.append(f"the bias {float(bb):+.4g} exceeds the median bar {float(mb):.4g}: the "
                                       f"estimator's own uncertainty does not cover its systematic, and a "
                                       f"corrected coverage cannot see that")
                except (TypeError, ValueError):
                    reasons.append(f"bias, bias_se or median_bar is not a number: {bb!r}, {bse!r}, {mb!r}")
        if rung == "archive":
            for k in ("bias_subtracted", "spread_validated"):
                v = _need(detail, k, reasons)
                if v is not None and not bool(v):
                    sc = detail.get("spread_check") if isinstance(detail.get("spread_check"), dict) else None
                    if k == "spread_validated" and sc is not None and int(sc.get("n_compared", 1) or 0) == 0:
                        # ABSENT IS NOT OUTSIDE THE BAND (A286): a spread check that compared nothing has no
                        # reference, and the rung's FAIL says so instead of reading as the twin's spread
                        reasons.append("spread_validated is false because the spread check compared NOTHING: "
                                       f"the repeats' reference is ABSENT ({sc.get('reason', 'no reason recorded')}); "
                                       "this is a missing reference, not a ratio outside the band")
                    else:
                        reasons.append(f"{k} is false: the archive rung needs the twin's bias removed "
                                       "and its spread checked against the repeats")
    return ("PASS" if not reasons else "FAIL"), reasons


def level_ratio(injected_sigma, record_sigma) -> float:
    """The ratio a noisy rung must report: injected sigma over the record's own.

    ASSERTING 1.0 IS NOT MEASURING IT, and A280 is why this exists. Three harnesses
    would have written `injected_over_record=1.0` in perfect good faith while injecting
    twenty-nine times the archive's noise, because the number they scaled was the PEAK
    and not the law. A caller hands in the two sigmas it actually used and this divides
    them, so the field carries a measurement rather than an intention.

    Both arguments may be arrays (per sample or per trace); the ratio is taken on their
    root-mean-square, which is the quantity a chi-squared is built from.
    """
    import numpy as _np
    a = _np.asarray(injected_sigma, dtype=float).ravel()
    b = _np.asarray(record_sigma, dtype=float).ravel()
    if a.size == 0 or b.size == 0:
        raise ValueError("level_ratio needs both sigmas; an empty one cannot be checked")
    ra = float(_np.sqrt(_np.mean(a ** 2)))
    rb = float(_np.sqrt(_np.mean(b ** 2)))
    if not (rb > 0):
        raise ValueError("the record's sigma is zero: there is nothing to compare the rung against")
    return ra / rb


def spectrum_ratio(injected_noise, record_tau: float) -> float:
    """The second ratio a noisy rung must report: the correlation time of the noise it
    actually injected, over the record's own, both as truncated ACF times.

    THE LEVEL CHECK CANNOT SEE THIS AND A280 IS WHY IT IS SEPARATE. That entry put three
    harnesses at twenty-nine times the archive's noise with the noiseless rung unable to
    notice, and the repair was `level_ratio`. This is the same shape one axis over:
    `level_ratio` compares root-mean-square amplitudes, so independent samples and an
    AR(1) at any coefficient whatever both report exactly 1.000. Amplitude is not noise.

    IT READS THE NOISE AND NOT THE TRACE, for two measured reasons.
    `noise.wing_correlation` picks its wing by `lev < QC_STEP_WING_NSIGMA * sigma_w`, so a
    quieter rung selects a tighter, flatter, further-out segment and reads a smaller time:
    the statistic is a function of the rung's own scale, and a rung at 0.3 of the law scores
    0.425 on a trace with nothing wrong with it. And the time it reads is dominated by the
    LINE's wing curvature rather than the noise (2026-09-16: an analytic line over provably
    independent samples reads 2.31 against the archive's 2.57, and a quadratic detrend takes
    the archive to 1.000). A noise array has no wing to select and no line to curve.

    SO WHAT IS `record_tau`? The archive's NOISE correlation, which is 1.000 -- measured,
    not assumed, and it is what `rb5s6s/noise.py`'s own 2026-07-11 V3 verification already
    said in words ("wing noise is essentially WHITE at sample scale"). It is NOT the
    `tau_int` column of `results/noise_model.csv`, which is that column's line curvature
    and is the number a rung would be wrongly tuned to. It is required rather than
    defaulted, because a caller that has not asked which of the two it holds is the
    caller this check exists for.

    Returns the ratio; an empty draw or a non-positive record time is refused rather than
    defaulted, a missing time being the state this check exists to notice.
    """
    import numpy as _np
    try:                                   # `python rb5s6s/ladder_gate.py --self-test` runs this
        from . import config as _C         # file as a script, where a relative import has no
    except ImportError:                    # parent package and the plant cannot run at all
        from rb5s6s import config as _C
    arrs = [_np.asarray(w, dtype=float).ravel() for w in injected_noise]
    arrs = [w for w in arrs if w.size >= 100]
    if not arrs:
        raise ValueError("spectrum_ratio needs the injected noise; no draw was long enough to read")
    rt = float(record_tau)
    if not (rt > 0):
        raise ValueError("the record's noise correlation time is not positive: there is nothing "
                         "to compare the rung's shape against")
    times = []
    for w in arrs:
        w = w - w.mean()
        d = float(_np.dot(w, w))
        if not (d > 0):
            continue
        t = 1.0
        for k in range(1, min(_C.NOISE_MAX_LAG, w.size // 4)):
            c = float(_np.dot(w[:-k], w[k:]) / d)
            if c < _C.NOISE_ACF_TRUNC:
                break
            t += 2.0 * c
        times.append(t)
    if not times:
        raise ValueError("no injected draw had any variance: there is no spectrum to read")
    return float(_np.mean(times)) / rt


def _predecessor(rung: str, analysis_id: str = ""):
    r = rungs_of(analysis_id) if analysis_id else RUNGS
    i = r.index(rung)
    return r[i - 1] if i else None


class LadderRefused(RuntimeError):
    """Raised when real traces are asked for before the synthetic ladder has passed."""


def _cache() -> pathlib.Path:
    """The session's current cache, from the pointer the instruments share."""
    p = ROOT / "private" / "cache" / "CURRENT_CACHE"
    if p.is_file():
        lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
        if lines:
            return (ROOT / lines[0]).resolve()
    return ROOT / "private" / "cache"


def ladder_dir(analysis_id: str, cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    return (cache or _cache()) / ".ladder" / analysis_id


def _private_results_dir() -> Optional[pathlib.Path]:
    """The private results directory a re-run was pointed at, or None for the live tree."""
    import os
    v = os.environ.get("RB5S6S_RESULTS_DIR")
    if not v:
        return None
    try:
        if pathlib.Path(v).resolve() == (ROOT / "results").resolve():
            return None
    except OSError:
        pass
    return pathlib.Path(v)


def record_dir(analysis_id: str, cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    """Where `record` writes. A RE-RUN POINTED AT A PRIVATE RESULTS DIRECTORY WRITES ITS RUNGS THERE TOO
    (F482, 2026-09-24): a re-obtain of `run_window_surface.py` under `RB5S6S_RESULTS_DIR` overwrote the
    LIVE noiseless rung of `window_surface`, the gate's own evidence, with a record of a table the live tree
    did not carry. Reading is unchanged, so a private re-run is still gated by the live ladder; only its
    writes stay beside its tables. An explicit `cache` is the caller's own choice and is honoured."""
    if cache is None:
        priv = _private_results_dir()
        if priv is not None:
            return priv / ".ladder_private" / analysis_id
    return ladder_dir(analysis_id, cache)


def climbable(analysis_id: str, rung: str, cache: Optional[pathlib.Path] = None) -> None:
    """Refuse BEFORE the computation, not only before the artefact (2026-09-16 night).

    `record()` already refused a rung whose predecessor was absent or failing, but a harness
    learned that only after spending the level's whole computation: three refused levels of the
    window surface cost 190 s each and recorded nothing. The owner's rule is that a twin noise
    level is not USED before the lower level is validated, so a harness asks this first, with the
    same rule `record()` applies, and a chain stops at the first refusal.
    """
    if rung not in rungs_of(analysis_id):
        raise ValueError(f"rung must be one of {rungs_of(analysis_id)} for {analysis_id!r} "
                         f"(profile {profile_of(analysis_id)}), got {rung!r}")
    allr = rungs_of(analysis_id); i = allr.index(rung)
    req = REQUIRED[profile_of(analysis_id)]
    d = ladder_dir(analysis_id, cache)
    for r in allr[:i]:
        if r in req:                               # every required rung below must read PASS
            f = d / f"{r}.json"
            if not f.is_file():
                raise LadderRefused(f"cannot record '{rung}' for '{analysis_id}': the required rung "
                                    f"'{r}' below it has no artefact. The ladder is climbed in order.")
            if json.loads(f.read_text()).get("verdict") != "PASS":
                raise LadderRefused(f"cannot record '{rung}' for '{analysis_id}': the required rung "
                                    f"'{r}' below it does not read PASS.")
    below = [r for r in allr[:i] if (d / f"{r}.json").is_file()]
    if below and json.loads((d / f"{below[-1]}.json").read_text()).get("verdict") != "PASS":
        raise LadderRefused(f"cannot record '{rung}' for '{analysis_id}': the nearest recorded rung "
                            f"below it, '{below[-1]}', does not read PASS.")
    if i > 0 and not below:
        raise LadderRefused(f"cannot record '{rung}' for '{analysis_id}': no rung below it has an "
                            f"artefact. The ladder is climbed in order.")


#: THE LADDERS THAT CERTIFY ONE ESTIMATOR AT ONE CANONICAL TRUTH (C5-carry-1, 2026-09-22). F277: on
#: 2026-09-21 a closure run at the retired truths with two realisations wrote the waist ladder's noiseless
#: and low rungs, and `real_traces` would have read them for the 42 um estimator. The closure refused it at
#: its one call site; the refusal now lives where the rung is written, so no caller can bypass it.
CANONICAL_REQUIRED = {"ultra_joint_waist"}


def _canonical_check(analysis_id: str, rung: str, canonical: Optional[Dict[str, Any]],
                     d: pathlib.Path) -> None:
    """Refuse a rung whose canonical key differs from the one the ladder FROZE at its first rung.

    The key is whatever identifies what the ladder certifies (for the waist ladder, the truth in um).
    The first rung written with a key freezes it in `canonical.json`; every later rung must present the
    same key, and an analysis in CANONICAL_REQUIRED must present one at all. A new canonical truth is a
    new ladder: its old directory goes to the history record, never overwritten here.
    """
    if canonical is None:
        if analysis_id in CANONICAL_REQUIRED:
            raise LadderRefused(
                f"{analysis_id} certifies one estimator at one canonical truth, so its rung {rung!r} must "
                f"declare it (record(..., canonical={{...}})); a rung without a key could have been measured "
                f"anywhere (F277)")
        return
    key = json.loads(json.dumps(canonical, sort_keys=True))
    f = d / "canonical.json"
    if f.is_file():
        frozen = json.loads(f.read_text())
        if frozen != key:
            raise LadderRefused(
                f"{analysis_id}: rung {rung!r} declares canonical {key}, but the ladder froze {frozen} at "
                f"its first rung; a different truth is a different ladder (F277)")
    else:
        d.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(key, sort_keys=True, indent=1))


def record(analysis_id: str, rung: str, *, detail: Dict[str, Any],
           cache: Optional[pathlib.Path] = None,
           canonical: Optional[Dict[str, Any]] = None) -> pathlib.Path:
    """Write one rung's artefact, with the verdict COMPUTED from `detail`.

    There is deliberately no `passed` argument: a caller that tries to hand a verdict in gets a
    TypeError.  A rung whose PREDECESSOR is absent or not PASS is refused outright, so the ladder
    cannot be climbed out of order. `canonical` is what the ladder certifies (the waist ladder's
    truth); it is frozen at the first rung and a mismatch is refused (`_canonical_check`).
    """
    climbable(analysis_id, rung, cache=cache)
    verdict, reasons = _judge(rung, detail)
    d = record_dir(analysis_id, cache)
    _canonical_check(analysis_id, rung, canonical, ladder_dir(analysis_id, cache))
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{rung}.json"
    out.write_text(json.dumps({
        "analysis_id": analysis_id, "rung": rung, "noise_scale": NOISE_SCALE[rung],
        "verdict": verdict, "reasons": reasons,
        "when": time.strftime("%Y-%m-%dT%H:%M:%S"), "detail": detail,
    }, indent=1))
    return out


def status(analysis_id: str, harness: Optional[str] = None,
           cache: Optional[pathlib.Path] = None) -> List[str]:
    """Empty when every rung admits; otherwise one line per rung that does not."""
    d = ladder_dir(analysis_id, cache)
    h_mtime = pathlib.Path(harness).resolve().stat().st_mtime if harness else None
    bad = []
    for rung in gating_rungs(analysis_id):
        f = d / f"{rung}.json"
        if not f.is_file():
            bad.append(f"the {rung} rung has no artefact ({f}): run it before the real traces")
            continue
        try:
            row = json.loads(f.read_text())
        except ValueError as e:
            bad.append(f"the {rung} rung's artefact is unreadable: {e}")
            continue
        if row.get("verdict") != "PASS":
            bad.append(f"the {rung} rung reads {row.get('verdict')}: " + json.dumps(row.get("detail", {}))[:200])
            continue
        # AND THE STORED VERDICT IS RE-JUDGED, NEVER TRUSTED. Until 2026-09-16 this read
        # `row["verdict"]` and stopped, so a rung recorded under an older and weaker gate
        # kept its PASS for ever and every strengthening of `_judge` was silently
        # NON-RETROACTIVE. That is the rule file's own named class -- a mechanism renamed
        # rather than rewritten reports compliance while grading a retired rule -- and it
        # was live: `injected_over_record` was added on 2026-09-16 after A280 put three
        # harnesses at twenty-nine times the archive's noise, and every rung recorded
        # before it went on admitting real traces on a field nobody had ever supplied.
        # A ladder whose rungs are graded by whatever rules happened to hold the day they
        # were written is not a ratchet. The stored DETAIL is the evidence; the verdict is
        # a reading of it, and the reading is remade here against the rules in force now.
        again, why = _judge(rung, row.get("detail", {}))
        if again != "PASS":
            bad.append(f"the {rung} rung was recorded PASS under an earlier gate and does not "
                       f"pass the current one: {'; '.join(why)}. Re-run it -- the artefact is "
                       f"evidence and the rules that grade it have moved")
            continue
        if h_mtime is not None and f.stat().st_mtime < h_mtime:
            bad.append(f"the {rung} rung is OLDER than the analysis that would use it: re-run it")
    return bad


def real_traces(analysis_id: str, harness: Optional[str] = None, *,
                rows: Optional[List[Dict[str, str]]] = None,
                cache: Optional[pathlib.Path] = None, with_info: bool = False):
    """The archive's own traces, refused until the ladder passes. Returns (row, freqs, volts) triples."""
    bad = status(analysis_id, harness, cache)
    if bad:
        raise LadderRefused(
            f"real traces refused for '{analysis_id}': " + "; ".join(bad)
            + ". The synthetic ladder comes first: noiseless, then 0.3 of the archive's law, then 1.0.")
    from . import ingest
    # THE SANCTIONED ROUTE IDENTIFIES ITSELF. `check_caller` refuses any caller that is not
    # on the debt list, and this IS the way through, so it says so rather than being special-
    # cased by name -- a name test would admit anything that renamed itself.
    with _clearance():
        manifest = rows if rows is not None else ingest.load_manifest()
        out = []
        for r in manifest:
            loaded = ingest.load_trace(ingest.trace_path(r), with_info=with_info)
            out.append((r, loaded))
    return out



# ------------------------------------------------------------------ THE SIZE LADDER
# Owner, 2026-09-16: "start small, then increase the computation time spent on attempts ... I
# already gave this rule and it has been broken systematically ... implement mechanisms to refute
# your new attempts in case you didn't follow the protocol". So it is a refusal, orthogonal to the
# noise ladder and stored beside it: an MLE attempt declares its SIZE on named axes, a stage is
# admitted only on a recorded PASS at no more than SIZE_GROWTH times smaller on every axis and a
# cost predicted from that rung under the stage's budget, and the artefacts stay so a reader can
# see the ladder was climbed. Stage 0 is the smallest world in which the question can be asked.
SIZE_AXES = ("conditions", "windows", "orders", "free", "realisations", "forms", "truths")
SIZE_GROWTH = 4.0


def busy_workers() -> int:
    """Pool workers running on this machine now, counted from the process table by the spawn entry
    point every `ProcessPoolExecutor` child carries (this record kills a pool by matching
    `spawn_main`, never the script name). Zero when the table cannot be read, because a refusal
    that fires on a missing instrument is worse than no refusal."""
    import subprocess
    try:
        out = subprocess.run(["ps", "-A", "-o", "command="], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return 0
    return sum(1 for line in out.splitlines() if "spawn_main" in line)


def cores() -> int:
    """This machine's physical cores, performance and efficiency together."""
    import subprocess
    try:
        out = subprocess.run(["sysctl", "-n", "hw.physicalcpu"], capture_output=True,
                             text=True, timeout=10).stdout
        return max(int(out.strip()), 1)
    except (OSError, ValueError, subprocess.SubprocessError):
        return 10
SIZE_BUDGET_S = {0: 120.0, 1: 480.0, 2: 1800.0, 3: 3600.0, 4: 8 * 3600.0}
SIZE_STAGE0_CAP = {"conditions": 1, "windows": 3, "orders": 3, "free": 8, "realisations": 1,
                   "forms": 1, "truths": 1}


class SizeRefused(RuntimeError):
    """Raised when an MLE attempt asks for a size no passing smaller rung licenses."""


def size_dir(analysis_id: str, cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    return ladder_dir(analysis_id, cache) / "size"


def _size_cells(size: Dict[str, Any]) -> float:
    out = 1.0
    for ax in SIZE_AXES:
        out *= float(size.get(ax, 1))
    return out


def _size_judge(evidence: Dict[str, Any]) -> tuple:
    """PASS on the same tolerances the noise ladder uses: a noiseless recovery inside
    NOISELESS_TOL, or a coverage inside COVER_TOL of its nominal."""
    why = []
    if "max_abs_rel_error" in evidence:
        if float(evidence["max_abs_rel_error"]) > NOISELESS_TOL:
            why.append(f"recovery off by {float(evidence['max_abs_rel_error']):.3g}, over {NOISELESS_TOL}")
    elif "coverage" in evidence:
        nom = float(evidence.get("nominal", 0.68))
        nr = evidence.get("n_realisations")
        # AN UNRESOLVED COVERAGE IS NOT A FAILED WORLD (F32.3, F35): growing the realisation count is
        # how a coverage gets resolved, so a size rung whose coverage is under the resolving count is
        # judged on its bias against the realised scatter instead, and licenses the next stage on
        # that axis; a resolved coverage is judged on the band as before
        if nr is not None and int(nr) < coverage_resolved_n(nom):
            b, sd = evidence.get("bias_um"), evidence.get("scatter_um")
            if b is None or sd is None:
                why.append(f"coverage unresolved at {int(nr)} realisations and no bias_um/scatter_um to judge instead")
            elif abs(float(b)) > 3.0 * float(sd) / max(int(nr), 1) ** 0.5:
                why.append(f"bias {float(b):.3g} um is over three standard errors of the realised scatter at {int(nr)} realisations")
        elif abs(float(evidence["coverage"]) - nom) > COVER_TOL:
            why.append(f"coverage {float(evidence['coverage']):.2f} outside {nom} +- {COVER_TOL}")
    else:
        why.append("no evidence: a size rung carries max_abs_rel_error or coverage")
    return ("PASS" if not why else "FAIL"), why


def size_rung(analysis_id: str, stage: int, size: Dict[str, Any], cost_s: float,
              evidence: Dict[str, Any], cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    """Record one stage of the size ladder; the verdict is COMPUTED from `evidence`."""
    bad = [ax for ax in size if ax not in SIZE_AXES]
    if bad:
        raise ValueError(f"unknown size axes {bad}; the axes are {SIZE_AXES}")
    verdict, reasons = _size_judge(evidence)
    d = size_dir(analysis_id, cache)
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"S{int(stage)}.json"
    out.write_text(json.dumps({"analysis_id": analysis_id, "stage": int(stage), "size": dict(size),
                               "cells": _size_cells(size), "cost_s": float(cost_s),
                               "verdict": verdict, "reasons": reasons, "evidence": evidence,
                               "when": time.strftime("%Y-%m-%dT%H:%M:%S")}, indent=1))
    return out


def launch(analysis_id: str, stage: int, size: Dict[str, Any], *, pool_speedup: float = 1.0,
           cache: Optional[pathlib.Path] = None, reason: str = "", workers: int = 0) -> Dict[str, Any]:
    """The refusal. Returns the admission with its cost prediction, or raises SizeRefused.

    THE CORES ARE PART OF THE SIZE (0g, F50, 2026-09-17). Pass `workers` and a pool that would
    put more workers on this machine than it has cores, counting what already runs, is refused
    unless `reason` names the trade.

    Stage 0 is admitted only inside SIZE_STAGE0_CAP on every axis. A later stage needs a recorded
    PASS at a lower stage with every axis at least size/SIZE_GROWTH, and the cost predicted from
    that rung (its cost per cell times this stage's cells, over the pool speed-up) under the
    stage's budget. A skipped stage, a failed predecessor or an eightfold jump on one axis is a
    refusal with the reason in words.
    """
    if workers:
        _busy, _cores = busy_workers(), cores()
        if int(workers) + _busy > _cores and not reason:
            raise SizeRefused(
                f"stage {stage} of '{analysis_id}' refused: {int(workers)} workers on top of "
                f"{_busy} already running exceeds this machine's {_cores} cores, so every pool "
                f"runs at part speed and the wall clock is longer than serialising. Wait for the "
                f"cores, ask for fewer, or pass reason= naming the trade.")
    stage = int(stage)
    bad = [ax for ax in size if ax not in SIZE_AXES]
    if bad:
        raise ValueError(f"unknown size axes {bad}; the axes are {SIZE_AXES}")
    if stage == 0:
        over = {ax: (size.get(ax, 1), SIZE_STAGE0_CAP[ax]) for ax in SIZE_AXES
                if float(size.get(ax, 1)) > SIZE_STAGE0_CAP[ax]}
        if over:
            raise SizeRefused(f"stage 0 of '{analysis_id}' is not small: {over} (axis: (asked, cap)). "
                              f"Start in the smallest world the question can be asked in.")
        return dict({"stage": 0, "cells": _size_cells(size), "predicted_s": None, "licensed_by": None}, reason=reason)
    d = size_dir(analysis_id, cache)
    prev = None
    # A SMALLER WORLD AT THE SAME STAGE NUMBER LICENSES TOO (2026-09-17 12:10): four and eight
    # realisations on the L both land on stage 4 by the cells arithmetic, and the search below
    # looked only at lower stages, so the four-realisation PASS licensed nothing and the eight
    # were refused as an eightfold jump over one realisation. The same-stage record counts when
    # it is smaller on some axis and larger on none; the growth rule is then read against it.
    # A PASSED SUPERSET LICENSES ITS SUBSETS OUTRIGHT (F37, 2026-09-17): a two-world diagnostic at
    # 32 conditions was refused as an eightfold jump over the four-condition record while a PASS at
    # 32 conditions and six worlds stood at a higher stage. A recorded PASS that is larger or equal
    # on EVERY axis has already run the asked world inside it, so the size question is answered.
    for f in sorted(d.glob("S*.json")):
        row = json.loads(f.read_text())
        psize = row.get("size", {})
        if row.get("verdict") == "PASS" and all(float(psize.get(ax, 1)) >= float(size.get(ax, 1)) for ax in SIZE_AXES):
            return dict({"stage": stage, "cells": _size_cells(size), "predicted_s": None,
                         "licensed_by": row.get("stage"), "per_cell_s": None, "superset": True}, reason=reason)
    for st in range(stage, -1, -1):
        f = d / f"S{st}.json"
        if f.is_file():
            row = json.loads(f.read_text())
            if st == stage:
                psize = row.get("size", {})
                smaller = any(float(psize.get(ax, 1)) < float(size.get(ax, 1)) for ax in SIZE_AXES)
                larger = any(float(psize.get(ax, 1)) > float(size.get(ax, 1)) for ax in SIZE_AXES)
                if not smaller or larger or row.get("verdict") != "PASS":
                    continue
            if row.get("verdict") == "PASS":
                prev = row
                break
            raise SizeRefused(f"stage {stage} of '{analysis_id}' refused: stage {st} reads "
                              f"{row.get('verdict')} ({'; '.join(row.get('reasons', []))}). "
                              f"A failed smaller world licenses nothing larger.")
    if prev is None:
        raise SizeRefused(f"stage {stage} of '{analysis_id}' refused: no smaller stage has been "
                          f"recorded PASS. Start small: record stage 0 first.")
    jumps = {ax: (float(size.get(ax, 1)), float(prev["size"].get(ax, 1))) for ax in SIZE_AXES
             if float(size.get(ax, 1)) > SIZE_GROWTH * float(prev["size"].get(ax, 1))}
    if jumps:
        raise SizeRefused(f"stage {stage} of '{analysis_id}' refused: it grows more than "
                          f"{SIZE_GROWTH:g}x on {jumps} (axis: (asked, licensed)) over stage "
                          f"{prev['stage']}. Grow one axis at a time.")
    per_cell = float(prev["cost_s"]) / max(float(prev["cells"]), 1.0)
    predicted = per_cell * _size_cells(size) / max(float(pool_speedup), 1.0)
    budget = SIZE_BUDGET_S.get(stage, SIZE_BUDGET_S[max(SIZE_BUDGET_S)])
    if predicted > budget:
        raise SizeRefused(f"stage {stage} of '{analysis_id}' refused: predicted {predicted:.0f} s "
                          f"from stage {prev['stage']}'s {per_cell:.2f} s per cell, over the "
                          f"{budget:.0f} s ceiling of this stage. A smaller stage comes first.")
    return {"stage": stage, "cells": _size_cells(size), "predicted_s": predicted,
            "licensed_by": prev["stage"], "per_cell_s": per_cell}


def _self_test() -> List[str]:
    """GUARD noise-ladder, planted BOTH ways on every refusal it owns.

    The 2026-09-15 repair is what most of this plants: before it, `record` took the verdict from
    the caller, so the gate could refuse a MISSING rung and never a FALSE one.  Each case below
    names the defect it would catch.
    """
    import tempfile
    OK_N = {"max_abs_rel_error": 1e-6, "n_truths": 8}
    # `injected_over_record` joined the noisy rungs' required detail on 2026-09-16
    # (A280). This self-test was written before it and stopped passing the moment the
    # field existed -- caught within the hour by `instrument_msa`, which runs every
    # plant, which is the whole reason that harness exists. A guard gaining a
    # requirement must carry its own plant forward in the same edit.
    OK_C = {"coverage": 0.68, "chi2_red": 1.02, "odd_sign_agreement": True, "n_realisations": 100,
            "injected_over_record": 1.0, "injected_tau_over_record": 1.0,
            "blame": "twin reproduces mu2 and k4; mu3 open"}
    OK_A = dict(OK_C, bias_subtracted=True, spread_validated=True)
    bad = []
    # A SUFFIXED ID CLIMBS ITS BASE'S RUNGS (C6b, 2026-09-22): a twin world or a session is the same
    # analysis on another world, so it takes the base's profile, and an unknown base is still refused
    # to the default's three rungs rather than inheriting from a name it merely contains
    if profile_of("moment_window_bias@volume") != "moment_window_bias" or profile_of("ultra_joint_waist@E") != "waist":
        bad.append("suffix: a suffixed id fell to the default profile instead of its base's")
    if profile_of("no_such_analysis@volume") != "default":
        bad.append("suffix: an unknown base was given a profile it does not have")
    # THE RESOLUTION COUNT (F32.3): eight realisations inside the band are UNRESOLVED, a hundred PASS
    _v8, _why8 = _judge("low", dict(OK_C, n_realisations=8))
    if _v8 == "PASS" or not any("UNRESOLVED" in w for w in _why8):
        bad.append("resolution: a coverage on eight realisations was admitted as a statement")
    if _judge("low", dict(OK_C, n_realisations=coverage_resolved_n()))[0] != "PASS":
        bad.append("resolution: a coverage at the resolving count was refused")
    if coverage_resolved_n(0.68, 0.10, 2.0) != 88 or coverage_resolved_n(0.95, 0.10, 2.0) != 19:
        bad.append("resolution: the resolving count is not the binomial arithmetic (88 at 0.68, 19 at 0.95)")
    # THE REALISATION FLOOR: a coverage read on six is refused whatever it reads
    _v6, _why6 = _judge("low", dict(OK_C, n_realisations=6))
    if _v6 == "PASS" or not any("floor" in w for w in _why6):
        bad.append("floor: a coverage on six realisations was admitted")
    with tempfile.TemporaryDirectory() as td:
        cache = pathlib.Path(td)
        harness = cache / "h.py"
        harness.write_text("# plant\n")

        # 0. THE CANONICAL KEY (C5-carry-1), both ways: frozen at the first rung, a mismatch refused,
        #    a required ladder refused without one, and the same key admitted at the next rung
        try:
            record("ultra_joint_waist", "noiseless", detail=OK_N, cache=cache)
            bad.append("canonical: a required ladder recorded a rung without a canonical key")
        except LadderRefused:
            pass
        record("ultra_joint_waist", "noiseless", detail=OK_N, cache=cache, canonical={"truth_um": 42.0})
        try:
            record("ultra_joint_waist", "low", detail=OK_C, cache=cache, canonical={"truth_um": 52.0})
            bad.append("canonical: a rung at a different truth than the frozen one was recorded (F277)")
        except LadderRefused:
            pass
        try:
            record("ultra_joint_waist", "low", detail=OK_C, cache=cache, canonical={"truth_um": 42.0})
        except LadderRefused as exc:
            bad.append(f"canonical: the frozen truth itself was refused at the next rung: {exc}")
        record("plant_free", "noiseless", detail=OK_N, cache=cache)      # an unlisted ladder needs no key

        # 1. nothing recorded at all -> refused, and real_traces raises
        if not status("plant", str(harness), cache):
            bad.append("noise-ladder: an analysis with no rungs was admitted")
        try:
            real_traces("plant", str(harness), cache=cache)
            bad.append("noise-ladder: real_traces returned without any ladder")
        except LadderRefused:
            pass

        # 2. THE REPAIR: a verdict cannot be handed in any more
        try:
            record("plant", "noiseless", passed=True, detail={}, cache=cache)  # type: ignore[call-arg]
            bad.append("noise-ladder: `passed=` was accepted -- the rubber stamp is back")
        except TypeError:
            pass

        # 3. THE REPAIR: an EMPTY detail is judged FAIL, not PASS
        r = json.loads(record("plant", "noiseless", detail={}, cache=cache).read_text())
        if r["verdict"] != "FAIL" or not r["reasons"]:
            bad.append("noise-ladder: an empty detail was not judged FAIL with reasons")

        # 4. the ladder cannot be climbed out of order
        try:
            record("plant", "archive", detail=OK_A, cache=cache)
            bad.append("noise-ladder: 'archive' was recorded while 'noiseless' reads FAIL")
        except LadderRefused:
            pass

        # 5. good evidence passes, rung by rung
        for rung, det in (("noiseless", OK_N), ("low", OK_C), ("archive", OK_A)):
            r = json.loads(record("plant", rung, detail=det, cache=cache).read_text())
            if r["verdict"] != "PASS":
                bad.append(f"noise-ladder: sound evidence for {rung} was refused: {r['reasons']}")
        if status("plant", str(harness), cache):
            bad.append("noise-ladder: three passing rungs were still refused")

        # 5d. THE CORES ARE PART OF THE SIZE (0g, F50): a pool over-subscribing the machine is
        # refused, and a reason naming the trade admits it; the counters read the live table, so
        # the plant asks for a pool larger than any machine
        try:
            launch("plant_cores", 0, {"conditions": 1, "forms": 1}, cache=cache, workers=10_000)
            bad.append("cores: a pool of ten thousand workers was admitted")
        except SizeRefused as _e:
            if "cores" not in str(_e):
                bad.append(f"cores: the refusal did not name the cores: {_e}")
        try:
            launch("plant_cores", 0, {"conditions": 1, "forms": 1}, cache=cache, workers=10_000,
                   reason="the trade is named: this pool runs alone overnight")
        except SizeRefused:
            bad.append("cores: a reason naming the trade did not admit the pool")
        if busy_workers() < 0 or cores() < 1:
            bad.append("cores: the counters returned a value no machine can have")
        # 5c. A PASSED SUPERSET LICENSES A SUBSET, and a world larger on any axis is still refused
        sup_id = "plant_superset"
        size_rung(sup_id, 4, {"conditions": 32, "forms": 6}, 100.0, {"max_abs_rel_error": 0.0}, cache=cache)
        try:
            adm_sub = launch(sup_id, 3, {"conditions": 32, "forms": 2}, cache=cache)
            if not adm_sub.get("superset"):
                bad.append("size-ladder: a subset of a passed world was admitted without the superset licence")
        except SizeRefused:
            bad.append("size-ladder: a subset of a passed larger world was refused")
        try:
            launch(sup_id, 4, {"conditions": 32, "forms": 40}, cache=cache)   # 40/6 is over the 4x growth, and no superset holds it
            bad.append("size-ladder: a world growing past the rule on one axis with no superset was admitted")
        except SizeRefused:
            pass
        # 6. TWO-SIDED coverage: probe just outside the catch region in EACH direction
        for cov, side in ((0.55, "under"), (0.81, "over")):
            r = json.loads(record("plant", "low", detail=dict(OK_C, coverage=cov),
                                  cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: {side}-coverage {cov} was admitted; "
                           "over-coverage is an inflated bar and must fail as hard as under")
        # and just INSIDE, both directions, so the band is not simply always-refusing
        for cov in (0.59, 0.77):
            r = json.loads(record("plant", "low", detail=dict(OK_C, coverage=cov),
                                  cache=cache).read_text())
            if r["verdict"] != "PASS":
                bad.append(f"noise-ladder: in-band coverage {cov} was refused")

        # 7. each remaining judged field, planted once
        for det, what in ((dict(OK_C, chi2_red=4.0), "chi2 4.0"),
                          (dict(OK_C, odd_sign_agreement=False), "odd-sign disagreement"),
                          (dict(OK_C, blame="  "), "an empty blame verdict")):
            r = json.loads(record("plant", "low", detail=det, cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: {what} was admitted")

        # 7b. THE SPECTRUM, probed just outside the band in EACH direction and just inside,
        #     because a one-sided tolerance admits half of what it exists to refuse. Too LOW
        #     is a rung whose noise is more independent than the record's; too HIGH is one
        #     driven through a correlation the record does not carry, which is the arm that
        #     would have been added in good faith on the strength of `tau_int` alone.
        for sp, side in ((1.0 / SPECTRUM_TOL * 0.95, "under"), (SPECTRUM_TOL * 1.05, "over")):
            r = json.loads(record("plant", "low", detail=dict(OK_C, injected_tau_over_record=sp),
                                  cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: a rung {side} the spectrum band at {sp:.3g} was admitted")
        for sp in (1.0 / SPECTRUM_TOL * 1.05, SPECTRUM_TOL * 0.95):
            r = json.loads(record("plant", "low", detail=dict(OK_C, injected_tau_over_record=sp),
                                  cache=cache).read_text())
            if r["verdict"] != "PASS":
                bad.append(f"noise-ladder: an in-band spectrum ratio {sp:.3g} was refused")
        d = dict(OK_C)
        d.pop("injected_tau_over_record")
        r = json.loads(record("plant", "low", detail=d, cache=cache).read_text())
        if r["verdict"] != "FAIL":
            bad.append("noise-ladder: a noisy rung with no spectrum field was admitted")

        # 7c. THE INSTRUMENT, on the discriminating case. `level_ratio` reports 1.000 for
        #     both of these -- they differ only in their spectrum -- and `spectrum_ratio`
        #     must not, or the field is decoration.
        import numpy as _np
        _r = _np.random.default_rng(7)
        _n = 4000
        _white = [_r.standard_normal(_n) for _ in range(4)]
        _a = 0.6                                    # AR(1): tau_int = (1+a)/(1-a) = 4 exactly
        _corr = []
        for _ in range(4):
            w = _r.standard_normal(_n)
            x = _np.empty(_n)
            x[0] = w[0]
            for i in range(1, _n):
                x[i] = _a * x[i - 1] + _np.sqrt(1 - _a * _a) * w[i]
            _corr.append(x)
        if abs(level_ratio(_np.concatenate(_corr), _np.concatenate(_white)) - 1.0) > 0.05:
            bad.append("noise-ladder: the plant's correlated and white arms differ in LEVEL, so "
                       "they do not isolate the spectrum and prove nothing about it")
        sw, sc = spectrum_ratio(_white, 1.0), spectrum_ratio(_corr, 1.0)
        if not (1.0 / SPECTRUM_TOL <= sw <= SPECTRUM_TOL):
            bad.append(f"noise-ladder: spectrum_ratio reads {sw:.3g} on independent samples against "
                       "a record time of 1, so a CORRECT rung would be refused")
        if sc <= SPECTRUM_TOL:
            bad.append(f"noise-ladder: spectrum_ratio reads only {sc:.3g} on AR(1) noise at 0.6, "
                       "whose time is 4 by construction: the check cannot see a spectrum")
        for arg, why in ((([], 1.0), "no draw"), ((_white, 0.0), "a zero record time"),
                         (([_np.zeros(_n)], 1.0), "a draw with no variance")):
            try:
                spectrum_ratio(*arg)
                bad.append(f"noise-ladder: spectrum_ratio accepted {why} instead of refusing")
            except ValueError:
                pass
        record("plant", "low", detail=OK_C, cache=cache)
        for det, what in ((dict(OK_A, bias_subtracted=False), "an unsubtracted twin bias"),
                          (dict(OK_A, spread_validated=False), "an unvalidated spread"),
                          (dict(OK_A, spread_validated=False, spread_check={"n_compared": 0, "reason": "no rows"}),
                           "a spread check that compared nothing")):
            r = json.loads(record("plant", "archive", detail=det, cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: {what} was admitted at the archive rung")
        record("plant", "archive", detail=OK_A, cache=cache)

        # 7d. A RUNG RECORDED UNDER A WEAKER GATE DOES NOT KEEP ITS PASS. The three rungs
        #     read PASS right now; strip a judged field out of a stored artefact, leaving
        #     its stored verdict saying PASS, and the ladder must refuse it -- which is what
        #     a gate strengthened after the fact has to do to be a ratchet at all. Planted
        #     on the exact field whose absence this session added, and restored after.
        art = ladder_dir("plant", cache) / "low.json"
        keep = art.read_text()
        row = json.loads(keep)
        assert row["verdict"] == "PASS", "the plant needs a stored PASS to weaken"
        row["detail"].pop("injected_tau_over_record", None)
        art.write_text(json.dumps(row))
        if not status("plant", None, cache):
            bad.append("noise-ladder: a rung whose stored verdict says PASS but whose detail no "
                       "longer passes the current gate was admitted -- strengthening the gate is "
                       "not retroactive and the ladder is not a ratchet")
        art.write_text(keep)
        if status("plant", None, cache):
            bad.append(f"noise-ladder: restoring the plant's artefact left the ladder refusing: "
                       f"{status('plant', None, cache)}")

        # 8b. A CORRECTED COVERAGE CANNOT SEE A BIAS, so the bias is tested beside it (finding of 2026-09-19)
        okc = dict(OK_C, coverage_raw=0.2, bias=0.05, bias_se=0.01, median_bar=0.3)
        if _judge("low", okc)[0] != "PASS":
            bad.append("noise-ladder: a corrected rung with a bias inside its bar was refused: " + str(_judge("low", okc)[1]))
        badb = dict(okc, bias=0.5)
        if _judge("low", badb)[0] == "PASS":
            bad.append("noise-ladder: a corrected rung whose bias exceeds its bar passed")
        nob = dict(OK_C, coverage_raw=0.2)
        if _judge("low", nob)[0] == "PASS":
            bad.append("noise-ladder: a corrected rung with no bias recorded passed")
        # 8. a harness edited after its ladder no longer has it
        time.sleep(0.01)
        harness.write_text("# plant, edited after the ladder\n")
        if not status("plant", str(harness), cache):
            bad.append("noise-ladder: a harness edited after its ladder kept it")
    # ---- the size ladder, planted both ways (2026-09-16)
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _c = pathlib.Path(_td)
        _ok = lambda fn, *a, **k: (fn(*a, **k) or True) and True
        def _refused(fn, *a, **k):
            try:
                fn(*a, **k)
            except SizeRefused:
                return True
            return False
        if not _refused(launch, "sz", 1, {"conditions": 32}, cache=_c):
            bad.append("size-ladder: a stage with no smaller PASS was admitted")
        if not _refused(launch, "sz", 0, {"conditions": 32}, cache=_c):
            bad.append("size-ladder: a large stage 0 was admitted")
        launch("sz", 0, {"conditions": 1, "windows": 3, "orders": 3}, cache=_c)
        size_rung("sz", 0, {"conditions": 1, "windows": 3, "orders": 3}, 30.0,
                  {"max_abs_rel_error": 5e-2}, cache=_c)
        if not _refused(launch, "sz", 1, {"conditions": 1, "windows": 6, "orders": 6}, cache=_c):
            bad.append("size-ladder: a stage over a FAILED smaller rung was admitted")
        size_rung("sz", 0, {"conditions": 1, "windows": 3, "orders": 3}, 30.0,
                  {"max_abs_rel_error": 1e-6}, cache=_c)
        adm = launch("sz", 1, {"conditions": 1, "windows": 6, "orders": 6}, cache=_c)
        if adm.get("licensed_by") != 0 or not (adm["predicted_s"] > 0):
            bad.append("size-ladder: a licensed stage was not admitted with its prediction")
        if not _refused(launch, "sz", 1, {"conditions": 32, "windows": 6, "orders": 6}, cache=_c):
            bad.append("size-ladder: a 32x jump on one axis was admitted")
        size_rung("sz", 1, {"conditions": 1, "windows": 6, "orders": 6}, 240.0,
                  {"max_abs_rel_error": 1e-6}, cache=_c)
        if not _refused(launch, "sz", 2, {"conditions": 4, "windows": 6, "orders": 6,
                                          "realisations": 4, "forms": 3}, cache=_c):
            bad.append("size-ladder: a stage predicted over its budget was admitted")
        if (size_dir("sz", _c) / "S1.json").is_file() is False:
            bad.append("size-ladder: the rung artefact was not written")

        # a smaller world at the SAME stage number licenses a larger one (reals 4 -> 8 on the L)
        size_rung("plant_size", 4, {"conditions": 32, "realisations": 4}, 400.0, {"max_abs_rel_error": 1e-5}, cache=_c)
        try:
            adm8 = launch("plant_size", 4, {"conditions": 32, "realisations": 8}, cache=_c)
            if adm8.get("licensed_by") != 4:
                bad.append("size-ladder: eight realisations at stage 4 were not licensed by the four at stage 4")
        except SizeRefused as exc:
            bad.append(f"size-ladder: a same-stage smaller PASS licensed nothing: {exc}")
    # ---- the profiles: the moments climb seven levels in order (2026-09-16)
    with _tf.TemporaryDirectory() as _td:
        _c = pathlib.Path(_td)
        OKN = {"max_abs_rel_error": 1e-6, "n_truths": 8}
        record("plant_moments", "noiseless", detail=OKN, cache=_c)
        record("plant_moments", "n03", detail=OK_C, cache=_c)     # a REFINEMENT, admitted on the noiseless alone
        try:
            record("plant_moments", "archive", detail=OK_C, cache=_c)
            bad.append("profiles: the archive rung was recorded before the required n10 on a moments analysis")
        except LadderRefused:
            pass
        try:
            record("plant_moments", "low", detail=OK_C, cache=_c)
            bad.append("profiles: the default three-rung climb was accepted on a moments analysis")
        except LadderRefused:
            pass
        for r in ("n01", "n03", "n10"):
            record("plant_moments", r, detail=OK_C, cache=_c)
        if status("plant_moments", cache=_c) == []:
            bad.append("profiles: a moments analysis short of the archive rung was admitted")
        record("plant_moments", "low", detail=OK_C, cache=_c)
        record("plant_moments", "archive", detail=OK_A, cache=_c)
        if status("plant_moments", cache=_c):
            bad.append("profiles: a moments analysis with its chain through the archive was refused: "
                       + "; ".join(status("plant_moments", cache=_c))[:200])
        if rungs_of("no_such_analysis") != RUNGS:
            bad.append("profiles: an unregistered analysis did not get the default rungs")

        # O34'S BIAS SURFACE, PLANTED BOTH WAYS (T0c). RT18's defect is the one that matters here and
        # it is silent: an id nobody registers falls through to `default`, so the climber records three
        # rungs, the gate admits, and a surface the owner asked for over EIGHT levels is certified on
        # a chain that never saw 0.001 -- a wall that reads exactly like a gate holding the line.
        want = ("noiseless", "n001", "n003", "n01", "n03", "n10", "low", "archive")
        if rungs_of("moment_window_bias") != want:
            bad.append(f"window-bias: the profile is {rungs_of('moment_window_bias')}, not the owner's grid")
        if "n300" in rungs_of("moment_window_bias"):
            bad.append("window-bias: a 3.0 rung entered a surface that is a bias table and not a death curve")
        for r, v in (("n001", 0.001), ("n003", 0.003)):
            if NOISE_SCALE.get(r) != v:
                bad.append(f"window-bias: rung {r} scales {NOISE_SCALE.get(r)}, not {v}")
        record("plant_window_bias", "noiseless", detail=OKN, cache=_c)
        # the REQUIRED chain is 0 -> 0.01 -> 0.1 -> 1.0, so 0.1 may not be recorded before 0.01.
        # `_refused` above catches SizeRefused and this refusal is a LadderRefused, so it is asked
        # for by name: a helper reused for the wrong exception would let the raise escape and the
        # plant would read as an error rather than as the refusal it is testing for.
        try:
            record("plant_window_bias", "n10", detail=OK_C, cache=_c)
            bad.append("window-bias: 0.1 was recorded with 0.01 absent, so the required chain is not read")
        except LadderRefused:
            pass
        record("plant_window_bias", "n01", detail=OK_C, cache=_c)
        record("plant_window_bias", "n10", detail=OK_C, cache=_c)
        if status("plant_window_bias", cache=_c) == []:
            bad.append("window-bias: a surface short of the archive rung was admitted")
        record("plant_window_bias", "archive", detail=OK_A, cache=_c)
        if status("plant_window_bias", cache=_c):
            bad.append("window-bias: the full required chain was refused: "
                       + "; ".join(status("plant_window_bias", cache=_c))[:200])
    return bad


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        b = _self_test()
        for x in b:
            print(x)
        print(f"ladder_gate: self-test {'OK' if not b else 'FAILED'}")
        sys.exit(1 if b else 0)
    print(__doc__)


# ---------------------------------------------------------------------------
# THE RUNTIME REFUSAL, AT THE CHOKEPOINT
# ---------------------------------------------------------------------------
#: True while `real_traces` is handing traces over, so the loader lets its own route through.
_IN_REAL_TRACES = False


@contextlib.contextmanager
def _clearance():
    global _IN_REAL_TRACES
    was, _IN_REAL_TRACES = _IN_REAL_TRACES, True
    try:
        yield
    finally:
        _IN_REAL_TRACES = was


def check_caller(loader: str) -> None:
    """Refuse a caller that reaches the archive without climbing the ladder.

    WHY THIS EXISTS WHEN A SCANNER ALREADY DID. The scanner is a TEXT scan, and on
    2026-09-16 it reported zero direct routes while forty-one producers read the archive,
    because its pattern wanted `from ingest import` and this repository writes
    `from rb5s6s.ingest import`. A regex can always be out-spelled; the LOADER cannot be
    gone around, because every route to a trace ends here. So the scanner keeps its job of
    naming the debt and this keeps the rule.

    WHO IS LET THROUGH, and each is a decision rather than a convenience: anything inside a
    `real_traces` call, which is the sanctioned route; anything under `tests/`, because a
    test is not an analysis and the suite must be able to read a fixture; the package's own
    modules; the files on `PREDATES_THE_GATE`, which is the debt list and may only
    shrink; and, decided in the loader itself rather than here, the one example trace that
    travels inside the wheel (`ingest._is_packaged_example`), a tutorial fixture admitted by
    where it lives. Everything else raises.

    FALSE-PASS DIRECTION: a file that renames itself onto the list is admitted, so this
    refuses the accident and not the determined. It is the accident that has happened.
    """
    import sys
    if _IN_REAL_TRACES:
        return
    f = sys._getframe(1)
    while f is not None:
        name = f.f_code.co_filename
        if "/rb5s6s/" in name:
            f = f.f_back
            continue
        base = pathlib.Path(name).name
        parts = pathlib.Path(name).parts
        if "tests" in parts or base.startswith("test_") or base == "conftest.py":
            return
        if base in PREDATES_THE_GATE:
            return
        raise LadderRefused(
            f"{base} called {loader} without climbing the ladder. Call "
            f"rb5s6s.ladder_gate.real_traces(<analysis id>, __file__) instead: it refuses "
            f"until the noiseless, low and archive rungs are recorded and read PASS. A new "
            f"harness cannot be born with a direct route to the archive, and PREDATES_THE_GATE "
            f"carries the ones that came before the gate and may only shrink.")
    return
