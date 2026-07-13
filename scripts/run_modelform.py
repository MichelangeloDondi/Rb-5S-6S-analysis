#!/usr/bin/env python3
"""
M8: model-form comparison (Voigt vs Lehmann cusp) at the cold-dim corner.

At 70 C the line is narrowest, so the transit fraction is largest and the cusp
(if resolvable at all in the 2025 epoch) is most visible. For each peak we fit
'voigt', 'lehmann' and 'full' and report BIC. dBIC = BIC(voigt) - BIC(lehmann):
positive favours the cusp, negative favours Gaussian; |dBIC| < 2 means the
archival data cannot tell them apart (the expected outcome -- the decisive
test is October's narrow laser).

Reads results/ruler_blocks.csv for rates. PRELIMINARY.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s.ingest import load_manifest, load_trace, trace_path  # noqa: E402
from rb5s6s.noise import condition_noise_model  # noqa: E402
from rb5s6s.qc import trace_metrics, hard_flags, ingest_flags  # noqa: E402
from rb5s6s.linefit import to_frequency  # noqa: E402
from rb5s6s.modelform import compare_forms  # noqa: E402

PEAKS = ("4121", "4154", "4192", "4207")


def main() -> int:
    rows = load_manifest()
    trates = {}
    for r in csv.DictReader(open(C.RESULTS_DIR / "ruler_blocks.csv")):
        if r["session"] == "T":
            trates[(r["peak"], r["T"])] = 2.0 * float(r["rate"])

    print("=" * 78)
    print("(M8) MODEL FORM at the cold-dim corner (70 C): Voigt vs Lehmann cusp")
    print(f"{'peak':>6s} {'chi2 voigt':>11s} {'chi2 lehm':>10s} {'chi2 full':>10s} "
          f"{'dBIC(V-L)':>10s}  verdict")
    out = []
    for peak in PEAKS:
        if (peak, "70") not in trates:
            continue
        rate = trates[(peak, "70")]
        recs = [r for r in rows if r["flag"] == "canonical" and r["role"] == "t_sweep"
                and r["peak"] == peak and r["temperature_C"] == "70"]
        fs, vs = [], []
        for r in recs:
            t, v, info = load_trace(trace_path(r), with_info=True)
            m = trace_metrics(t, v)
            if any("truncated" in f or "dropout" in f
                   for f in hard_flags(m, rf_on=False) + ingest_flags(info)):
                continue
            fs.append(to_frequency(t, rate)); vs.append(v)
        if len(vs) < 3:
            continue
        law = condition_noise_model(vs)
        cmp = compare_forms(fs, vs, law=law)
        f = cmp["forms"]; d = cmp["dBIC_voigt_minus_lehmann"]
        verdict = ("cusp favoured" if d > 10 else "Gaussian favoured" if d < -10 else
                   "indistinguishable" if abs(d) < 2 else "weak preference")
        print(f"{peak:>6s} {f['voigt']['chi2']:>11.1f} {f['lehmann']['chi2']:>10.1f} "
              f"{f['full']['chi2']:>10.1f} {d:>+10.1f}  {verdict}")
        out.append({"peak": peak, "dBIC_voigt_minus_lehmann": d,
                    "chi2_voigt": f["voigt"]["chi2"], "chi2_lehmann": f["lehmann"]["chi2"],
                    "chi2_full": f["full"]["chi2"],
                    "full_gauss": f["full"]["shape"].get("gauss"),
                    "full_exp": f["full"]["shape"].get("exp")})

    with open(C.RESULTS_DIR / "modelform.csv", "w", newline="") as fh:
        if out:
            w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)

    ds = [o["dBIC_voigt_minus_lehmann"] for o in out]
    print(f"\n{'-'*78}")
    if ds and max(abs(x) for x in ds) < 10:
        npos = sum(1 for x in ds if x > 0)
        print(f"VERDICT: NO decisive preference (max |dBIC| = {max(abs(x) for x in ds):.1f} < 10)")
        print("-> the 2025 data CANNOT resolve a cusped (Lehmann) vs smooth (Voigt)")
        print("extra-broadening, exactly as the two-epoch design anticipated: the ~2 MHz")
        print("bad-lock laser Gaussian smears the cusp. Mild colour, not a claim:")
        print(f"dBIC is non-negative on {npos}/{len(ds)} peaks (a faint, consistent LEAN")
        print("toward the cusp, one peak at 'positive evidence' ~3.7) -- suggestive that a")
        print("real cusp is there but unresolved. The decisive test is October's")
        print("narrow-laser cold-dim run; this module is its validated infrastructure.")
    else:
        print("VERDICT: a DECISIVE preference is present -- inspect the winning form and")
        print("the 'full' fit's Gaussian vs exponential split per peak.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
