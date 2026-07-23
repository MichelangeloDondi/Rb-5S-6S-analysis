#!/usr/bin/env python3
"""
Is the intra-block position scatter DRIFT or JITTER?  (PLAN §8.4, limitation 5)

The experimenter confirmed (2026-07-22) that the scope horizontal knob and the
cavity reference were USUALLY not touched within a single 5-repeat block --
a tendency, not a protocol -- though they were moved many times between
blocks. The exceptions are visible in the data and are separated below: a
block whose positions STEP rather than scatter is one where something moved,
so excluding those is principled rather than convenient.

Within a block that did not move, `peak_pos_ms` is comparable across its
repeats -- and since `repeat_idx` is the time order (DATA.md §2), the block's
five positions carry their own arrow of time.

So the question can be settled from the archive alone, with no timestamps and
no wavemeter log:

  * accumulated DRIFT  -> position trends monotonically with repeat_idx,
                          R^2 of a linear fit -> 1
  * short-term JITTER  -> the order is random, E[R^2] = 1/(n-1) = 0.25 at n=5

This matters because docs/PREREGISTRATION_timestamps.md derived a predicted
block DURATION (D4) by dividing the 0.08 MHz intra-block scatter by a drift
rate -- which is only valid if that scatter is drift in the first place.

Scope: RF-off science blocks only. The RF-on ruler blocks are excluded because
`peak_pos_ms` there locks onto different comb teeth between traces, giving a
~120 ms scatter that is an artifact of tooth identification, not of the laser.
Pooling them in was an error that inflated the apparent scatter ~7x.

Outputs: stdout only (a diagnostic of archival data, not a new result).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MS_PER_MHZ = 1.8 / 0.08          # DATA.md §2 calibration: 1.8 ms = 0.08 MHz
JUMP_MS = 10.0                   # a block with std above this has a step, not scatter


def blocks() -> pd.DataFrame:
    d = pd.read_csv(ROOT / "results" / "qc_metrics.csv")
    d = d[(d.flag == "canonical") & (~d.rf_on)
          & (d.role.isin(["p_sweep", "t_sweep"]))].copy()
    rows = []
    for key, g in d.groupby(["role", "peak", "temperature_C", "power_mW"],
                            dropna=False):
        g = g.sort_values("repeat_idx")
        if len(g) < 4:
            continue
        x = g.repeat_idx.to_numpy(float)
        y = g.peak_pos_ms.to_numpy(float)
        if y.std() == 0:
            continue
        r = np.corrcoef(x, y)[0, 1]
        rows.append(dict(key=key, n=len(g), std=y.std(ddof=1), r2=r * r,
                         slope=np.polyfit(x, y, 1)[0], positions=y))
    return pd.DataFrame(rows)


def main() -> int:
    R = blocks()
    clean = R[R["std"] < JUMP_MS]
    print("=" * 74)
    print("INTRA-BLOCK POSITION TREND  (drift or jitter?)")
    print(f"RF-off science blocks with >=4 canonical repeats : {len(R)}")
    print(f"  of which scatter-like (std < {JUMP_MS:g} ms)         : {len(clean)}")
    print(f"  of which step-like                             : {len(R) - len(clean)}")
    print(f"\nmedian within-block std : {clean['std'].median():.2f} ms "
          f"= {clean['std'].median() / MS_PER_MHZ:.3f} MHz   "
          f"(DATA.md quotes 1.8 ms = 0.08 MHz)")
    null = 1.0 / (clean.n - 1)
    t, p = stats.ttest_1samp(clean.r2 - null, 0.0)
    print(f"\nlinear trend vs repeat index:")
    print(f"  mean R^2 observed      : {clean.r2.mean():.3f}")
    print(f"  expected if order random: {null.mean():.3f}")
    print(f"  paired t-test          : t = {t:+.2f}, p = {p:.3f}")
    print(f"  slope signs            : {(clean.slope > 0).sum()} up, "
          f"{(clean.slope < 0).sum()} down")
    verdict = "JITTER (no accumulation)" if p > 0.05 else "TREND PRESENT"
    print(f"\n  => {verdict}")
    print("\nConsequences:")
    print("  * The 0.08 MHz intra-block scatter does NOT accumulate with repeat")
    print("    order, so it cannot be divided by a drift rate to get a block")
    print("    duration -- PREREGISTRATION D4's premise fails.")
    print("  * It matches the wavemeter's own short-term StdDev (100 kHz,")
    print("    IMG_2896), which is what jitter should look like.")
    print("  * Within-block variation therefore measures laser JITTER; between-")
    print("    block variation is destroyed by re-centring. The archive ALONE has")
    print("    no lever on the lock DRIFT RATE -- the recovered clock restored")
    print("    one (scripts/run_drift_settling.py).")
    if len(R) > len(clean):
        print(f"\nStep-like blocks ({len(R) - len(clean)}) -- position jumps mid-block,")
        print("i.e. blocks where the reference DID move mid-acquisition:")
        for _, row in R[R["std"] >= JUMP_MS].iterrows():
            print(f"  {str(row.key):38s} std={row['std']:7.1f} ms  "
                  f"{np.round(row.positions, 1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
