#!/usr/bin/env python3
"""The expert modules, end to end, from a bare clone and no repository data.

The five-minute path a stranger meets first is `synthetic_recovery.py`: define
a line, simulate it, add noise, fit it, read the uncertainty. THIS script is
the second thing they meet, and it exercises the modules that make the model
complete rather than merely working.

    python examples/full_model_tour.py

Nothing here reads results/ or data_raw/, so it runs anywhere the package
installs.
"""
from __future__ import annotations

from rb5s6s import blackbody as bbr
from rb5s6s import cascade
from rb5s6s.model_compare import ModelFit, compare, interpret_model_comparison


def cascade_tour() -> None:
    print("1. CASCADE AND F-DEPLETION")
    print("   An observed amplitude is not a transition strength: the cascade")
    print("   returns atoms to the other ground level, where they are off")
    print("   resonance and stop contributing.\n")
    print(f"   {'line':10s} {'branching f':>12s} {'after 3 cycles':>15s} {'amplitude factor':>18s}")
    for peak in sorted(cascade.BRANCHING_F):
        f = cascade.BRANCHING_F[peak]
        survive = cascade.surviving_fraction(f, cycles=3.0)
        amp = cascade.amplitude_factor(peak, cycles=3.0)
        print(f"   {peak:10s} {f:12.4f} {survive:15.4f} {amp:18.4f}")
    p = cascade.CascadePopulations("4121", cycles=3.0)
    print(f"\n   populations always sum to one: {p.total():.12f}")
    print("   and with repumping the level relaxes to r/(f+r) instead of to zero:")
    late = cascade.surviving_fraction(cascade.BRANCHING_F["4121"], 1e4, repump_rate=0.1)
    print(f"     r = 0.10 gives {late:.4f}\n")


def blackbody_tour() -> None:
    print("2. BLACKBODY AS A CAMPAIGN BOUNDARY")
    print("   The deliverable is a family, not a ceiling: pass a target")
    print("   precision and receive the temperature above which thermal")
    print("   radiation enters the budget.\n")
    print(f"   cell range 70 to 130 C: shift {bbr.shift_hz(343.15):.1f} to "
          f"{bbr.shift_hz(403.15):.1f} Hz")
    print(f"   {'target':>12s} {'uncorrected':>14s} {'corrected':>14s}")
    for target in (100.0, 1e3, 1e4):
        u, c = bbr.t_max(target) - 273.15, bbr.t_max(target, corrected=True) - 273.15
        print(f"   {target:9.0f} Hz {u:11.0f} C {c:11.0f} C")
    print("\n   so blackbody is not what limits the temperature lever here\n")


def model_comparison_tour() -> None:
    print("3. MODEL COMPARISON AS AN EVIDENCE VECTOR")
    print("   The computation returns several statistics under several")
    print("   assumptions. A separate layer judges, and three of its four")
    print("   answers are refusals to choose.\n")
    cases = {
        "decisive, all criteria agree":
            (ModelFit("simple", 1000.0, 3, 500), ModelFit("rich", 900.0, 4, 500)),
        "too weak to separate":
            (ModelFit("simple", 1000.0, 3, 500), ModelFit("rich", 999.0, 4, 500)),
        "correlation decides it":
            (ModelFit("simple", 1000.0, 2, 5000, 40.0, 8.0),
             ModelFit("rich", 985.0, 6, 5000, 40.0, 7.88)),
    }
    for label, (a, b) in cases.items():
        out = interpret_model_comparison(compare(a, b))
        print(f"   {label:30s} -> {out['verdict']}")
    ev = compare(*cases["decisive, all criteria agree"])
    print(f"\n   the F statistic always carries its validity: {ev.f_validity}")
    print(f"   reason: {ev.f_reason[:64]}...")


def main() -> int:
    print(__doc__.splitlines()[0], "\n")
    cascade_tour()
    blackbody_tour()
    model_comparison_tour()
    print("Every number above came from the installed package alone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
