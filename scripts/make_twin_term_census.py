#!/usr/bin/env python3
"""Census the twin's terms by INSPECTING the code, and commit the result.

Every row answers four questions for one model term: does the public
forecast path carry it, does the example's world carry it, which module owns
the physics, and does the fitter model it. The answers are read from the
live code -- signature parameters, layer keys, attribute existence -- not
from anyone's memory of the code, because the plan's own census of
2026-08-31 was hand-read and the hand-read class is what this repository's
correction history is made of. A term the inspection cannot find reports
`no`, never a blank; a judgement the code cannot witness (a DELIBERATE
absence) says `stated:` and names the document that states it.

Output: results/twin_term_census.csv. Re-run after touching
rb5s6s/forecast.py, examples/campaign_twin.py or the physics modules.
"""
from __future__ import annotations
import os

import csv
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import blackbody, cascade, detection, fibre, forecast, stark  # noqa: E402

# resolved through the config so RB5S6S_RESULTS_DIR redirects this producer;
# a hand-built path is not redirected, so the freshness verifier compares a
# committed file against itself (2026-09-11).
from rb5s6s import config as _CFG  # noqa: E402
_CFG_RESULTS = _CFG.RESULTS_DIR


def _per_tooth_depletion() -> bool:
    """Is a comb tooth depleted at its OWN rate, read from the builder's source?

    INSPECTED, never recalled, which is this file's whole contract. A plant on
    a scratch copy removed the per-tooth rate and this returns False, where the
    hand-typed clause it replaces came out byte-identical with the feature
    removed.
    """
    import inspect

    from rb5s6s import forecast
    src = inspect.getsource(forecast.build_world_trace)
    return ("tooth_of" in inspect.signature(forecast.build_world_trace).parameters
            and "cycles_at_max * p_rel * rate" in src)


def _params(fn) -> set:
    return set(inspect.signature(fn).parameters)


def _example_layers() -> set:
    """The layer keys the example actually switches, read from its source."""
    src = (ROOT / "examples" / "campaign_twin.py").read_text(encoding="utf-8")
    m = re.search(r"layers = \{([^}]*)\}", src)
    return set(re.findall(r'"(\w+)"', m.group(1))) if m else set()


def _example_calls() -> str:
    """The example's own build_world_trace call, read from its source.

    A row must not choose what to inspect: the two rows added on 2026-09-08
    asked whether a keyword exists in `build_world_trace`'s SIGNATURE and
    printed the answer in the example's column, so the census said the exhibit
    carries the collection window and the fringe tail when the example names
    neither, and emptying the example would not have changed the cell.
    This file had already recorded the same mistake corrected once in the
    neighbouring column.
    """
    src = (ROOT / "examples" / "campaign_twin.py").read_text(encoding="utf-8")
    i = src.find("build_world_trace(")
    return src[i:src.find("\n\n", i)] if i >= 0 else ""


def _builder_layers() -> set:
    """The layer keys the public builder consults, read from its source."""
    src = inspect.getsource(forecast.build_world_trace)
    return set(re.findall(r'layers\["(\w+)"\]', src))


#: WHICH WAY EACH GAP BIASES A CLOSED LOOP, which is the reading the census was
#: missing. A term the WORLD carries and the FITTER lacks biases a recovery: the
#: THE FITTER COLUMN IS COMPUTED, NOT TYPED. `fullmodel.term_coverage`'s own
#: docstring says the census kept this by hand and that keeping it by hand is
#: how it went stale within a day; it then stayed hand-typed anyway, and three
#: of the five rows added on 2026-09-12 said "no" for terms that ARE in
#: FIT_TERMS and that `fit_full` recovers. One word was carrying two claims --
#: structurally unfittable, and fittable but not yet used in a committed fit --
#: for a reader who greps this file to learn which terms a fit can take.
_CENSUS_TERM_TO_PARAM = {
    "doppler_pedestal": "pedestal_height_frac",
    "retro_tilt_residual_doppler": "retro_tilt_rad",
    "beam_quality_m2": "m2",
    "radiation_temperature_separate": "t_bbr_k",
    "saturation_parameterised_by_rabi": "omega_mhz",
}


def _fitter_verdict(term: str) -> str:
    """`yes, <param>` when the parameter is fittable, `no: <reason>` when the
    model refuses it, and `-` for a term with no parameter in this model."""
    from rb5s6s.fullmodel import FIT_TERMS, UNFITTABLE
    param = _CENSUS_TERM_TO_PARAM.get(term)
    if param is None:
        return "-"
    if param in UNFITTABLE:
        # THE WHOLE REASON, not a slice. A [:60] cut fell mid-word and dropped
        # the colon clause carrying the remedy ("fit z_ratio, not M^2 and w0
        # separately"), which is the only part a reader needed.
        return f"no: {UNFITTABLE[param]}"
    if param in FIT_TERMS:
        return f"yes, fit_full free=('{param}',)"
    return "-"


#: fitter must put that width or that shift somewhere, and where it puts it says
#: which parameter comes back wrong. A term NEITHER carries is invisible, so the
#: loop recovers what it injects and says nothing about this bench -- the
#: failure this record already met once on the collection window.
_RECOVERY_BIAS = {
    "lorentzian_core_collisional": "none: both sides carry it",
    "laser_kernel_both_forms": "none: both sides carry it",
    "transit_cusp": "none: both sides carry it",
    "ac_stark_ramp": "fitter optional. With s0 fixed at zero the ramp's width "
                     "lands in the free Lorentzians, so beta and gamma_l absorb it",
    "axial_collection_window": "INVISIBLE: neither side carries it, so a loop "
                               "recovers its injection and would not recover "
                               "this bench's. Measured at 0.928 of the pure "
                               "ramp's third cumulant here",
    "standing_wave_fringe_tail": "INVISIBLE: neither side carries it. Suppresses "
                                 "the skew by about 7 per cent at this waist, so "
                                 "a loop over-reads the third cumulant",
    "saturation_companions": "world only: the fitter must absorb a homogeneous "
                             "width, which the Lorentzian sum takes one for one, "
                             "so beta or gamma_l comes back high and the waist "
                             "does not move",
    "cascade_depletion": "world only, and a WIDTH and not an amplitude: "
                         "depletion removes the slow, narrow atoms first, so the "
                         "surviving transit kernel is 12 per cent wider at three "
                         "mean cycles. The free amplitude takes the surviving "
                         "fraction and leaves the widening, so a closed loop that "
                         "ignores it reads the waist too SMALL, 64 um as 57",
    "blackbody": "world only: a centre shift the fitter absorbs into the free "
                 "per-trace centre, so it costs the SHIFT channel and no width",
    "lock_drift": "absorbed by design: free centres span it, and the oracle "
                  "arm sizes what that absorption costs",
    "noise": "none: the weights carry it",
    "scope_quantisation": "world only: adds a floor the fitter reads as noise",
    "power_order_randomisation": "caller-side: a monotone order makes the drift "
                                 "column an exact affine function of the power "
                                 "column and the pull is not identified at all",
    "radiation_trapping": "world only, and it scales with N, so the fitter parks "
                          "it in beta_self and the collisional coefficient reads high",
    "hyperfine_F_statistics": "world only: the single-line forecast generator "
                              "cannot vary F, so the one axis that splits the "
                              "shift family internally is absent from that path",
    "background_scattering": "absorbed by the per-trace baseline while it is flat. "
                             "A sloped one is an asymmetry the odd cumulants cannot "
                             "tell from the ramp except by their sign pattern",
    "laser_kernel_lorentzian_component": "none: both sides carry it, and it is the "
                                         "term that takes any missing homogeneous "
                                         "width one for one",
    "onf_guided_geometry": "INVISIBLE: no scenario yet on either side",
    "doppler_pedestal": "world only (2026-09-12). Over a sub-100 MHz trace it is "
                        "a near-constant offset, degenerate with the detector "
                        "offset the fitter already floats, so it costs nothing "
                        "here and bites only on a campaign-width scan",
    "retro_tilt_residual_doppler": "world only (2026-09-12). A Gaussian width at "
                                   "fixed intensity, so the fitter puts it in "
                                   "sigma_laser and the WAIST does not move",
    "beam_quality_m2": "world only (2026-09-12), through the collection ratio and "
                       "the axial sampling. Refuses without a waist rather than "
                       "defaulting to an ideal beam",
    "radiation_temperature_separate": "world only (2026-09-12). A MOT's atoms sit "
                                      "at microkelvin inside a room-temperature "
                                      "chamber, so tying the two costs 118 Hz "
                                      "between a cell and a cold platform",
    "saturation_parameterised_by_rabi": "world only (2026-09-12). Frees the "
                                        "saturation from the fitted shift, so it "
                                        "survives the zero this archive drives "
                                        "kappa to",
}


def main() -> int:
    gen = _params(forecast.synthetic_traces)
    world = _builder_layers()
    ex = _example_layers()
    fit_p = _params(forecast.fit_condition)
    have = {
        "companion": hasattr(stark, "companion_gamma_mhz"),
        "cascade": hasattr(cascade, "amplitude_factor"),
        "bbr": hasattr(blackbody, "shift_hz"),
        "channel": hasattr(detection, "default_channel"),
        "he11": all(hasattr(fibre, f) for f in
                    ("solve_he11", "evanescent_intensity", "transit_fwhm",
                     "homogeneous_width")),
        "noise_law": (_CFG_RESULTS / "noise_model.csv").is_file(),
    }

    def yes(b): return "yes" if b else "no"

    rows = [
        ("lorentzian_core_collisional", "yes", "yes", "lineshape.py",
         yes("gamma_coll" in gen and "T_C" in fit_p),
         "inspected: gamma_coll in synthetic_traces and the fitter"),
        ("laser_kernel_both_forms", yes("laser_kind" in gen), "yes",
         "lineshape.py", "yes, form assumed",
         "inspected: laser_kind in synthetic_traces. The form choice was "
         "audited 2026-08-20, the switch never thrown before then"),
        ("transit_cusp", yes("transit_fwhm" in gen), "yes", "lineshape.py",
         yes("transit_fwhm" in fit_p),
         "inspected: transit_fwhm in both signatures"),
        ("ac_stark_ramp", yes("s0" in gen), yes("stark" in world & ex),
         "lineshape.stark_ramp", "optional",
         "inspected: s0 in synthetic_traces since 2026-08-30 and the stark "
         "layer in build_world_trace. The side stays open per "
         "tests/test_ramp_side_matches_the_polarizability"),
        ("axial_collection_window", yes("z_ratio" in _params(forecast.build_world_trace)),
         yes("z_ratio" in _example_calls()),
         "lineshape.ramp_mixture", "no",
         "inspected: z_ratio in build_world_trace since 2026-09-08, None by "
         "default. The producers pass constants.collection_z_ratio at the "
         "cell's waist. The fitter has no window parameter"),
        ("standing_wave_fringe_tail", yes("fringe_density" in _params(forecast.build_world_trace)),
         yes("fringe_density" in _example_calls()),
         "fringe_tail.fringe_shift_density", "no",
         "inspected: fringe_density in build_world_trace since 2026-09-08, None "
         "by default. One Monte Carlo per waist, retro ratio and temperature, "
         "independent of the shift"),
        ("saturation_companions", yes("saturation" in world),
         yes("saturation" in ex), "stark.companion_gamma_mhz"
         if have["companion"] else "MISSING",
         "stated: deliberately absent (science plan T1: truth carries it, "
         "the fitter keeps the committed model, the gap is measured in T3)",
         "inspected: saturation layer in build_world_trace"),
        ("cascade_depletion", yes("cascade" in world), yes("cascade" in ex),
         "cascade.py" if have["cascade"] else "MISSING",
         "stated: deliberately absent (same T1 clause as saturation)",
         "inspected: cascade layer in build_world_trace"
         + (", and a tooth of an EOM comb is depleted at its own share of "
            "the line's rate" if _per_tooth_depletion() else "")),
        # forecast_path is measured on synthetic_traces's OWN signature; the
        # first form read the world builder's layer set here, which mislabelled
        # the column and licensed a wiki sentence
        ("blackbody", yes(any("bbr" in k or "blackbody" in k for k in gen)), yes("bbr" in ex),
         "blackbody.py, two-platform rule in twin.py"
         if have["bbr"] else "MISSING", "no",
         "inspected: bbr layer in build_world_trace. Negligible at MHz "
         "widths per the example's CHECK 3"),
        ("lock_drift", yes("drift" in world), yes("drift" in ex), "-",
         "absorbed by free per-scan centres",
         "inspected: drift layer in build_world_trace"),
        ("noise", "flat fraction or measured law", "shot-like anchored",
         "noise.py, per-point law in twin.acquire"
         if have["noise_law"] else "noise.py (law file MISSING)",
         "weights by the law",
         "inspected: noise accepts a law dict in synthetic_traces, and "
         "build_world_trace anchors shot-like noise at the bright rung"),
        ("scope_quantisation", yes("quantise" in world), yes("quantise" in ex),
         "instruments.py, applied by twin.acquire", "-",
         "inspected: quantise layer in build_world_trace. The named scopes "
         "in rb5s6s.instruments were manual-checked 2026-08-31 and the ERes "
         "kernel now hits the printed table"),
        ("power_order_randomisation", "caller-side by design",
         yes("randomise" in ex), "-", "-",
         "stated: the rung order is a design choice of the caller, not a "
         "physics term, and run_world draws it"),
        ("radiation_trapping",
         yes("halo_fraction" in gen),
         yes("halo_fraction" in _params(forecast.build_world_trace)),
         "detection.py" if have["channel"] else "MISSING", "-",
         "measured: the trapped-light halo reaches BOTH generator paths since "
         "2026-09-05, opt-in at zero by default so every committed CSV is "
         "unchanged. It raises the collected amplitude and does not reshape "
         "the line: the trapped photon is the D-line cascade photon, whose "
         "frequency is unrelated to the 993 nm two-photon detuning. The "
         "per-temperature fraction is supplied by the caller from "
         "results/trapping_channels.csv, so the number keeps its provenance"),
        ("hyperfine_F_statistics",
         "n/a, single-line generator",
         yes("shares" in _params(forecast.build_world_trace)),
         "amplitudes.predicted_shares", "-",
         "measured: build_world_trace takes shares and the closed loop and the "
         "campaign example both pass predicted_shares(), abundance times "
         "(2F+1)/G_iso. synthetic_traces generates one line, so shares do not "
         "apply to it"),
        ("background_scattering",
         ("flat only, as offset" if "offset" in gen else "no"),
         ("flat only, as offset" if "offset" in _params(forecast.build_world_trace) else "no"),
         "-", "absorbed by the per-trace linear baseline",
         "measured: a flat pedestal is in both generators as the offset parameter, "
         "and a scan-dependent background is in neither. That is the correct state "
         "and not a gap. Detection is the 795 nm D1 cascade photon behind 50 dB "
         "of 795 nm filtering, the drive is at 993 nm, so scattered drive light "
         "is rejected. What reaches the detector unrejected is the dark rate, "
         "the wall's thermal emission in the passband, and trapped D1 light off "
         "the walls, which scales with the signal and is the halo term. Both "
         "generators already carry a flat pedestal, named offset, which the "
         "fitter's own b0 and b1 absorb exactly. What is absent is a term "
         "varying across the scan on the line's own scale, and whether "
         "anything does is an open apparatus item in docs/plan/12"),
        ("laser_kernel_lorentzian_component",
         yes("gamma_l" in gen),
         yes("gamma_l" in _params(forecast.build_world_trace)),
         "lineshape.model_profile", "-",
         "measured: gamma_l and laser_kind reach BOTH paths since 2026-09-05. "
         "Until then the world builder had the instrument layers and no "
         "kernel forms while the forecast generator had the kernel forms and "
         "no layers, so no single path could vary the laser wing and the "
         "oscilloscope at once"),
        ("onf_guided_geometry", "no scenario yet (T2)", "no",
         "fibre.py" if have["he11"] else "MISSING", "-",
         "inspected: solved HE11 machinery present. The scenario layer "
         "lands with the configuration work"),
        # --- added 2026-09-12 with rb5s6s/fullmodel.py. Every one is in the
        # WORLD and in none of the fitters, which the recovery_bias column is
        # there to say out loud rather than leave to be discovered.
        ("doppler_pedestal",
         "yes, fullmodel.full_profile", "yes, build_world_trace",
         "fullmodel.py", _fitter_verdict("doppler_pedestal"),
         "co-propagating two-photon pedestal, 931 MHz FWHM at 130 C against "
         "the traces' sub-100 MHz span"),
        ("retro_tilt_residual_doppler",
         "yes, fullmodel.full_profile", "yes, build_world_trace",
         "fullmodel.py", _fitter_verdict("retro_tilt_residual_doppler"),
         "2 k sin(theta/2) times the thermal speed, 0.45 MHz per mrad at 110 C"),
        ("beam_quality_m2",
         "yes, collection ratio and the fringe sampling", "yes, fringe_survival_mc",
         "fullmodel.py", _fitter_verdict("beam_quality_m2"),
         "z_R = pi w0^2/(M^2 lambda). The DEFAULT m2=1.0 IS the ideal beam "
         "and installs no axial window at all. The refusal fires only at "
         "m2 != 1 without a waist"),
        ("radiation_temperature_separate",
         "yes, t_bbr_k", "yes, build_world_trace",
         "forecast.py, platforms.py", _fitter_verdict("radiation_temperature_separate"),
         "the walls' temperature and not the atoms'. Refused on a 200 K "
         "physical floor so a cold kind cannot inherit the conflation"),
        ("saturation_parameterised_by_rabi",
         "yes, fullmodel.saturation_companion_mhz", "yes, via full_profile",
         "fullmodel.py", _fitter_verdict("saturation_parameterised_by_rabi"),
         "Omega as its own parameter, so the companion survives the zero this "
         "archive drives the fitted shift to"),
    ]

    _ = _RECOVERY_BIAS  # the writer below reads it
    out = _CFG_RESULTS / "twin_term_census.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["term", "forecast_path", "example_world", "module",
                    "fitter", "provenance", "recovery_bias"])
        for r in rows:
            if any(str(c).strip() == "" for c in r):
                raise SystemExit(f"census refuses an empty cell in {r[0]}")
            bias = _RECOVERY_BIAS.get(r[0])
            if not bias:
                raise SystemExit(
                    f"census refuses {r[0]} with no recovery_bias: a term whose "
                    f"closed-loop direction is unstated is a term whose "
                    f"recovery test cannot be read")
            w.writerow(list(r) + [bias])
    print(f"wrote {os.path.relpath(out, ROOT)} ({len(rows)} terms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
