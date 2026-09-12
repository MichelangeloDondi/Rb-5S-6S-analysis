#!/usr/bin/env python3
"""Recover the drive power of the RF-on traces, which the manifest leaves blank.

`import_data.py` reads the power from the filename, and the modulator traces do
not carry one: they are named `<peak>nm_eom_before<N>`, `_after<N>` or
`_<TTT>c<N>`. So `power_mW` is empty on all 115 of them and the record has
treated them as powerless, which is why they were used only as a frequency
ruler and never as a physics lever.

**THE POWER IS RECOVERABLE AND THE CLOCK RECOVERS IT.** Two separate routes,
and each is written into its own basis string rather than merged:

* the temperature rulers name their temperature (`_070c`, `_090c`, `_110c`) and
  belong to the temperature arm, which runs at the pinned operating power;
* the `before` power rulers sit immediately ahead of the power sweep, and the
  sweep DESCENDS from its maximum, so the laser was at that maximum when they
  were taken. Checked on all four lines from `data_recovered/CLOCK.csv`: the
  next acquisition after the last before-ruler is the 225 mW block, 2.7, 4.1,
  4.6 and 5.3 minutes later, with nothing in between.

**THE `after` RULERS ARE NOT INFERRED**, and saying so is the point of keeping
the two apart. They follow the 25 mW block by about ten minutes and no
acquisition between them shows the power being returned, so the clock does not
support a value and this script does not invent one.

**AND THE INFERENCE NEVER TOUCHES `power_mW`.** It lands in its own columns, so
a reader can always tell a logged setting from a reconstructed one. Putting a
reconstruction in the column that holds measurements is the failure this
separation exists to prevent.

    ./.venv/bin/python scripts/annotate_manifest_power.py [--check]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from rb5s6s.config import MANIFEST_CSV  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CLOCK = ROOT / "data_recovered" / "CLOCK.csv"
#: The operating power both arms run at. The temperature arm is pinned there
#: (owner, 2026-09-11) and the power sweep descends from it.
OPERATING_MW = "225"
NEW = ("power_mW_inferred", "power_inference_basis")


def _clock() -> dict:
    if not CLOCK.is_file():
        return {}
    return {r["manifest_file"]: int(r["mtime_epoch"])
            for r in csv.DictReader(CLOCK.open()) if r["manifest_file"]}


def _basis(row: dict, clock: dict) -> tuple[str, str]:
    """(inferred power, why) for one row, or ("", why not)."""
    if row["power_mW"]:
        return "", "logged: power_mW carries it"
    if row["role"] == "t_sweep":
        return OPERATING_MW, ("temperature arm, pinned at the operating power "
                              "(owner-stated); the filename carries the "
                              "temperature and not the power")
    if row["rf_on"] != "True":
        return "", "not a modulator trace and no logged power"
    if row["role"] == "ruler_t":
        return OPERATING_MW, ("temperature arm, pinned at the operating power; "
                              "the filename carries the temperature")
    if row["role"] == "ruler_p" and row["bracket"] == "before":
        if row["file"] not in clock:
            return "", "before-ruler with no recovered timestamp"
        return OPERATING_MW, ("clock adjacency: the power sweep descends from "
                              "the operating power and this precedes its first "
                              "block with no acquisition in between")
    if row["role"] == "ruler_p" and row["bracket"] == "after":
        # THE AMPLITUDE EXCLUDES 25 mW. IT DOES NOT MEASURE THE POWER.
        # A two-photon signal goes as the square of the power, and the law is
        # validated on the logged rows: the 25 mW blocks sit at 0.0131 of the
        # 225 mW ones against 0.0123. The after-rulers sit at 0.646 of the
        # before-rulers, fifty times above where 25 mW would put them, so that
        # setting is excluded with margin.
        #
        # BUT 0.646 IS NOT A POWER RATIO. For 5S to 6S only rank 0 survives
        # (rank 1 absent by the exchange symmetry, rank 2 zero for J = 1/2),
        # and rank 0 goes as e1.e2, so the Doppler-free rate carries cos^2 of
        # the angle between the forward and retro polarisations -- and the
        # owner states that axis was always different. A 0.646 amplitude is
        # cos^2 at about 37 degrees, so reading it as drift, alignment or a
        # power deficit is reading a waveplate. The inference here is the
        # EXCLUSION of the low setting and nothing finer.
        # THE VALUE IS LEFT BLANK, which is what the module docstring and
        # scripts/README.md both promise and what this branch did NOT do until
        # 2026-09-12: it returned the operating power while its own basis string
        # said the amplitude "does not measure the power". A reader of the
        # committed MANIFEST found 225 in twenty-one rows the record calls
        # the record calls uninferred. The exclusion is real
        # and is kept as the basis; the number it cannot support is not.
        return "", ("amplitude EXCLUDES 25 mW with a factor of fifty of margin "
                    "(0.646 of the before-rulers against 0.012) but does NOT "
                    "measure the power: the rank-0 rate carries cos^2 of the "
                    "forward-retro polarisation angle and that axis varied, so "
                    "no value is inferred here")
    return "", "no route: neither a logged power nor a clock adjacency"


def main() -> int:
    check = "--check" in sys.argv
    rows = list(csv.DictReader(open(MANIFEST_CSV)))
    clock = _clock()
    if not clock:
        print("no recovered clock: the before-rulers cannot be inferred")
    fields = [f for f in rows[0] if f not in NEW] + list(NEW)
    changed = 0
    for r in rows:
        val, why = _basis(r, clock)
        if r.get("power_mW_inferred") != val or r.get("power_inference_basis") != why:
            changed += 1
        r["power_mW_inferred"], r["power_inference_basis"] = val, why
    n_inf = sum(1 for r in rows if r["power_mW_inferred"])
    if check:
        print(f"{changed} row(s) would change; {n_inf} carry an inferred power")
        return 1 if changed else 0
    with open(MANIFEST_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {MANIFEST_CSV.name}: {n_inf} inferred power(s), "
          f"{sum(1 for r in rows if r['power_mW'])} logged, "
          f"{sum(1 for r in rows if not r['power_mW'] and not r['power_mW_inferred'])} "
          f"left blank with a stated reason")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
