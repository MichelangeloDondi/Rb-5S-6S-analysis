#!/usr/bin/env python3
"""The two-atom two-photon channel: what it opens, where it sits, how big.

WHY. Every selection-rule argument this record carries for the 5S-6S line is
a SINGLE-ATOM argument, and one leg of it is that a J=1/2 state has two
magnetic sublevels, so a rank-2 operator has no reduced matrix element
between two of them and the sigma+sigma+ content of the drive is refused.
That leg does not survive being asked about two atoms: a PAIR has four
sublevel products and can take two units of angular momentum by taking one
unit each. This producer computes what the pair opens, and how large.

WHAT IT WRITES. Three blocks in one CSV, distinguished by the `block`
column.

  pair_state  every two-atom configuration the committed level table can
              build, ranked by defect from the two-photon energy. The first
              row is the resonance and every other row is the argument: the
              runner-up is 23 THz away, so no pair channel competes for the
              resonance and a cooperative process cannot make a new LINE.

  satellite   where the pair's sublevel channels sit, for both topologies.
              ALIGNED takes one unit in the same sense on each atom, which
              is the sigma+sigma+ content a single atom must refuse, and the
              two Zeeman shifts ADD to 2 g_F mu_B B, the Delta m_F = +-2
              position. EXCHANGE takes opposite units and the shifts cancel
              for a matched pair. Their zeros are complementary, so no field
              arrangement closes both.

  size        the rate as a fraction of the single-atom rate, at the
              Weisskopf radius of the same van der Waals difference M18
              computes for beta_self. Inside that radius the collision is
              strong and fully dephasing, which is broadening this record has
              already MEASURED rather than a new coherent channel, so the
              cutoff avoids counting the same physics twice.

WHAT TO READ OFF IT. The size column is the point. At 130 C it is 1.3e-9,
about eight times the single-atom hyperfine-mixing route, so the pair route
DOMINATES the forbidden-channel budget rather than sitting far below it. It
is also the only route with any amplitude at the Delta m_F = +-2 position at
all. Both sit six orders below the tightest bound this record carries on an
out-of-window feature, which is 0.0018 of peak in wing_check.csv.

VALIDITY. Angular factors of order unity are not carried, which is stated in
the module and is why this is a ceiling rather than a prediction. The size
integral is dominated by its cutoff, so the cutoff is a column, never
implied.

    python scripts/run_cooperative_channel.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from rb5s6s import cooperative as co                          # noqa: E402
from rb5s6s.polarisation import zeeman_satellite_mhz          # noqa: E402

OUT = REPO / "results" / "cooperative_channel.csv"
B_FIELD_UT = 50.0
TEMPS_C = (70.0, 100.0, 130.0)
PAIRS = ((("87Rb", 2), ("87Rb", 2)), (("87Rb", 2), ("87Rb", 1)),
         (("85Rb", 3), ("85Rb", 3)), (("85Rb", 3), ("85Rb", 2)),
         (("87Rb", 2), ("85Rb", 3)))


def main() -> None:
    rows = []

    for label, total_cm, defect_cm, defect_thz in co.pair_final_states():
        rows.append({"block": "pair_state", "label": label,
                     "value": f"{defect_cm:.3f}", "unit": "cm^-1",
                     "aux": f"{defect_thz:.3f}", "aux_unit": "THz",
                     "note": f"total {total_cm:.3f} cm^-1"})

    for topology in ("aligned", "exchange"):
        for a, b in PAIRS:
            mhz = co.satellite_mhz(B_FIELD_UT, a, b, topology)
            rows.append({
                "block": "satellite",
                "label": f"{topology} {a[0]} F={a[1]} + {b[0]} F={b[1]}",
                "value": f"{mhz:.4f}", "unit": "MHz",
                "aux": f"{B_FIELD_UT:.1f}", "aux_unit": "uT",
                "note": "zero by cancellation" if mhz == 0.0 else
                        f"{mhz / zeeman_satellite_mhz(a[0], B_FIELD_UT):.3f}"
                        " times the single-atom position"})

    floor = co.perturbative_floor_nm()
    rows.append({"block": "size", "label": "perturbative floor",
                 "value": f"{floor:.4f}", "unit": "nm", "aux": "0.1",
                 "aux_unit": "V_dd/Delta",
                 "note": "below this the third-order expression is an "
                         "extrapolation, and rate_ratio refuses it"})
    rows.append({"block": "size", "label": "suppression volume K",
                 "value": f"{co.suppression_volume_m3():.6e}", "unit": "m^3",
                 "aux": f"{co.TRANSFER_DEFECT_CM:.1f}", "aux_unit": "cm^-1",
                 "note": "V_dd/Delta = K/R^3, aux is the |5P,5P> defect"})

    for T in TEMPS_C:
        r_w = co.weisskopf_radius_nm(T)
        rows.append({"block": "size", "label": f"rate ratio at {T:.0f} C",
                     "value": f"{co.rate_ratio(T):.6e}", "unit": "fraction",
                     "aux": f"{r_w:.4f}", "aux_unit": "nm cutoff",
                     "note": "cutoff is the Weisskopf radius, inside which "
                             "the collision is already counted in beta_self"})

    # THE THREE KNOBS. Reported as the channel's response to what an
    # experiment can actually turn, which is not the same as its response to
    # the quantities the theory is written in.
    rows.append({"block": "knob", "label": "power, two-photon pair channel",
                 "value": f"{co.POWER_EXPONENT_TWO_PHOTON:.1f}",
                 "unit": "exponent of the RATIO against intensity",
                 "aux": "2", "aux_unit": "exponent of the rate itself",
                 "note": "the pair channel absorbs the same two photons the "
                         "line does, so both go as intensity squared and the "
                         "ratio is FLAT. Power cannot switch this channel on"})
    rows.append({"block": "knob", "label": "power, four-photon pair channel",
                 "value": f"{co.POWER_EXPONENT_FOUR_PHOTON:.1f}",
                 "unit": "exponent of the RATIO against intensity",
                 "aux": "4", "aux_unit": "exponent of the rate itself",
                 "note": "the only power-tunable member of the family. "
                         "Doubling the power quadruples its ratio to the line"})

    for T in TEMPS_C:
        k = co.knob_table(T, B_FIELD_UT)
        rows.append({"block": "knob", "label": f"temperature {T:.0f} C",
                     "value": f"{k['rate_ratio']:.6e}", "unit": "fraction",
                     "aux": f"{k['density_cm3']:.4e}", "aux_unit": "cm^-3",
                     "note": "temperature is the ONLY lever on the rate, "
                             "through density, and the ratio is linear in it"})

    rows.append({"block": "knob", "label": "field, satellite position",
                 "value": f"{co.knob_table()['satellite_mhz_per_ut']:.6f}",
                 "unit": "MHz per microtesla, aligned matched 87Rb pair",
                 "aux": "0", "aux_unit": "exponent of the RATE against field",
                 "note": "the field is a POSITION lever and not an amplitude "
                         "one. It moves the satellite and leaves the rate "
                         "alone, which is what makes it a discriminant"})
    for B in (5.0, 50.0, 200.0, 500.0):
        rows.append({"block": "knob", "label": f"field {B:.0f} uT",
                     "value": f"{co.satellite_width_contribution_mhz(B):.4e}",
                     "unit": "MHz added to the measured width",
                     "aux": f"{co.satellite_mhz(B, ('87Rb', 2), ('87Rb', 2)):.4f}",
                     "aux_unit": "MHz satellite offset",
                     "note": "below the resolving field the satellite is a "
                             "second-moment contribution, growing as B squared "
                             "while the channel itself does not change"})
    rows.append({"block": "knob", "label": "resolving field",
                 "value": f"{co.resolving_field_ut():.1f}", "unit": "uT",
                 "aux": "5.37", "aux_unit": "MHz line width",
                 "note": "above this the satellite offset exceeds the line "
                         "width, so a search for it becomes a search for a "
                         "RESOLVED feature at a known position"})

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["block", "label", "value", "unit",
                                           "aux", "aux_unit", "note"])
        w.writeheader()
        w.writerows(rows)

    print(f"wrote {OUT.relative_to(REPO)}  ({len(rows)} rows)")
    print(f"  pair resonance is unique, runner-up "
          f"{co.pair_final_states()[1][3]:+.1f} THz away")
    print(f"  aligned satellite, matched 87Rb pair: "
          f"{co.satellite_mhz(B_FIELD_UT, ('87Rb', 2), ('87Rb', 2)):.4f} MHz")
    for T in TEMPS_C:
        print(f"  rate ratio at {T:5.1f} C: {co.rate_ratio(T):.3e}")


if __name__ == "__main__":
    main()
