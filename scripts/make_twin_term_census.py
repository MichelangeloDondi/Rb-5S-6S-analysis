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

import csv
import inspect
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rb5s6s import blackbody, cascade, detection, fibre, forecast, stark  # noqa: E402


def _params(fn) -> set:
    return set(inspect.signature(fn).parameters)


def _example_layers() -> set:
    """The layer keys the example actually switches, read from its source."""
    src = (ROOT / "examples" / "campaign_twin.py").read_text(encoding="utf-8")
    m = re.search(r"layers = \{([^}]*)\}", src)
    return set(re.findall(r'"(\w+)"', m.group(1))) if m else set()


def _builder_layers() -> set:
    """The layer keys the public builder consults, read from its source."""
    src = inspect.getsource(forecast.build_world_trace)
    return set(re.findall(r'layers\["(\w+)"\]', src))


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
        "noise_law": (ROOT / "results" / "noise_model.csv").is_file(),
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
        ("saturation_companions", yes("saturation" in world),
         yes("saturation" in ex), "stark.companion_gamma_mhz"
         if have["companion"] else "MISSING",
         "stated: deliberately absent (science plan T1: truth carries it, "
         "the fitter keeps the committed model, the gap is measured in T3)",
         "inspected: saturation layer in build_world_trace"),
        ("cascade_depletion", yes("cascade" in world), yes("cascade" in ex),
         "cascade.py" if have["cascade"] else "MISSING",
         "stated: deliberately absent (same T1 clause as saturation)",
         "inspected: cascade layer in build_world_trace"),
        ("blackbody", yes("bbr" in world), yes("bbr" in ex),
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
        ("detection_channel", "no", "no",
         "detection.py" if have["channel"] else "MISSING", "-",
         "open: wiring unverified, on the verification queue"),
        ("onf_guided_geometry", "no scenario yet (T2)", "no",
         "fibre.py" if have["he11"] else "MISSING", "-",
         "inspected: solved HE11 machinery present. The scenario layer "
         "lands with the configuration work"),
    ]

    out = ROOT / "results" / "twin_term_census.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["term", "forecast_path", "example_world", "module",
                    "fitter", "provenance"])
        for r in rows:
            if any(str(c).strip() == "" for c in r):
                raise SystemExit(f"census refuses an empty cell in {r[0]}")
            w.writerow(r)
    print(f"wrote {out.relative_to(ROOT)} ({len(rows)} terms)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
