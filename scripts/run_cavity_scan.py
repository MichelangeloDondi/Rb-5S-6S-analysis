#!/usr/bin/env python3
"""
Integrate the 2025-06-12 cavity-scan digitisation (IMG_2508)
============================================================

Writes `results/cavity_scan_integrals.csv`: the eight spike integrals of the
digitised scope record, their mirror-pair midpoints, the flank-fit ramp apex,
and the two up-sweep ratios APPARATUS.md section 6 quotes against the M10
population law. All the physics lives in `rb5s6s/cavity_scan.py`; this script
only commits its rows. Held out of run_all.sh like the other
digitised-photograph producer (run_wavemeter_reconstruction.py);
tests/test_cavity_scan.py diffs the committed CSV against the current code.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s import config as C  # noqa: E402
from rb5s6s import cavity_scan  # noqa: E402


def main():
    out = C.RESULTS_DIR / "cavity_scan_integrals.csv"
    out.write_text(cavity_scan.render_results_csv())
    print(f"wrote {out}")
    cavity_scan.main()


if __name__ == "__main__":
    main()
