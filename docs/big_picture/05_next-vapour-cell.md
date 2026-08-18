*Chapter 5 of 8 of [the big picture](../BIG_PICTURE.md)*

## 5. What new vapour-cell measurements would add

A cell session with a stable lock (the cavity lock was repaired on
2026-08-16, with minutes-scale stability still to be measured at the bench)
would convert the bounds into the first measured environmental
coefficients for this line. None of it is scheduled or agreed. Every item
below opens with the same four things, so that the quantifying lives in one place:
what it would convert, what it would cost, how it could come back empty, and
which block of [`PLAN.md`](../PLAN.md) runs it. In order of leverage on the
physics:

1. **A direct beam-waist measurement**, knife-edge and camera profiler.
   Converts every waist-conditional absolute number in the record into a
   measured one, for an afternoon per configuration and no atoms. It could
   come back describing the present bench rather than the 2025 one. Runs as
   the beam-profile block, [`PLAN.md`](../PLAN.md) §4.2.

   No physics run at all, but w₀ is the dominant shared systematic under every
   number denominated in intensity. The light shift goes as 1/w₀², and the
   transit and laser widths are degenerate through it, so measuring it
   retroactively sharpens all of them at once. It is not the systematic under
   the collisional number, which rides on the density scale instead.
2. **Line centre vs power (the "pull").**
   Converts the AC-Stark bound into the first measured light shift on this
   line, for one morning of randomized power cycling. It could come back empty
   if the repaired lock does not hold minutes-scale stability, which the plan's stage-0 go/no-go measures before science shots are spent. Runs as
   [`PLAN.md`](../PLAN.md) §6 item 1.

   With centres alive, the first-order light shift (−⅔S₀, the strong handle)
   becomes measurable as a *differential* quantity, centre against power within
   a scan series, needing only minutes-scale lock stability. That would be the
   first measured AC-Stark coefficient of the line, and it would validate the
   shape-based method against the same data.
3. **Same-session high-density points (150–170 °C).**
   Converts reach on the density lever, rather than combinability, which the
   record has already settled. It rides the temperature-grid days if the oven
   allows, and could come back empty if the oven will not reach or hold the
   top of the range. Runs as [`PLAN.md`](../PLAN.md) §7c.

   Folding the dataset's own 130 °C point into the headline already stretched
   the 2025 lever from ×16.2 to ×52.5 and tightened the bound an order of
   magnitude (was 0.2–0.4, now 0.03–0.05 MHz per 10¹² cm⁻³). Even at ×52.5 the
   bound sits only 8–15× above the ~3.5 kHz expectation of §1.4, on the
   contested anchor §1.4 records, closer than
   before, but a same-session 150–170 °C extension is still the cleaner route.
   It removes the cross-epoch calibration step that folding the 130 °C point in
   relies on, and the higher temperatures make the collisional width move by
   0.07–0.25 MHz, against a ~20 kHz signal in 2025. **The hot points are
   necessary and not sufficient**: measured against the block-to-block width
   reproducibility that actually limits the comparison, they reach only
   0.9–3.0σ per block (`results/resolving_power.csv`). Interleaving the peaks
   and logging the power per trace would cut that floor, and would take the
   same signal to 3.4–12.2σ. The two halves are co-limiting, not a headline and
   a refinement. Interleaving also fixes a second problem: in 2025 temperature
   ran monotonically down with elapsed time, so slow drift and density trends
   are confounded.
4. **A tighter focus (~16 µm).**
   Converts the bound on the third cumulant into a detection, or into a
   meaningful bound, on the deep-integration day. It is sized for the
   pessimistic end and is not a promised result. Runs as
   [`PLAN.md`](../PLAN.md) §6 items 3 and 4.

   S₀ grows ~16× over the 2025 dataset's 64 µm waist (×14 against the planned
   64 µm configuration), and the third cumulant grows
   faster still, though not by the naive $S_0^3$ cube of that gain, a reading
   that [THEORY_NOTE.md](../THEORY_NOTE.md) §3 and [RESULTS.md](../RESULTS.md) C3c
   both record as replaced. The axial average over the
   collection window changes both its size and, if the window is long enough,
   its sign ([`PLAN.md`](../PLAN.md) §6 item 4: the sign flip is secured by the
   landscape cathode for any plausible magnification, while its size still
   rides on the unmeasured lens conjugates). The intrinsic asymmetry would
   become detectable, turning the drift-immune shape readout from a bound into
   a demonstration, cross-checked against the simultaneously measured pull.

Three acquisition changes would make those four *trustworthy*, not merely
*possible*. Each closes a gap the 2025 dataset could only bound around, and
each is stated on the same four points as the items above.

**Interleaving the four peaks within minutes, with a logged per-scan
timestamp**, which the analysed exports do not carry. It converts cross-peak
systematics from something assumed into something checked, rides inside every
dwell at no cost of its own, and fails only if the scope will not export
per-trace times, in which case an external log carries it
([`PLAN.md`](../PLAN.md) §7f and §7g). A recovered backup supplied file timestamps
after the fact, and that dating exposed the gap: the four peaks at one
temperature were acquired **54–76 minutes apart**, so the sharing assumption
behind the tighter β was never close-in-time to begin with
([PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md),
[RESULTS.md](../RESULTS.md)). A logged timestamp would turn that assumption from
untested into a checked fact. The HighFinesse wavemeter's own long-term log,
running alongside, is an independent drift diary for free.

**An absorption channel for the rubidium density N(T).** It converts an
adopted vapour density into a measured one, needs a weak D-line probe and a
photodiode of its own, neither of which the apparatus record lists, and could
come back empty if the cold spot will not flatten enough at the high end to be
read ([`PLAN.md`](../PLAN.md) §8 item 3). The infrared receiver named below is on
the bench and is not that detector. The collisional bound is denominated in a
density the record takes from a vapour-pressure
curve rather than measures, and the cold-spot audit puts that scale at ×1.4 to
×7 leverage on the headline collisional number, which is plausibly a larger
systematic than the beam waist. It also gates item 3 above, because the
high-temperature grid cannot be read until the cold-spot lag is characterised.

**Reading the 6S→5P ~1.3 µm cascade** instead of the reabsorbed 795 nm
fluorescence. It converts the degeneracy law into something measured without
the trapping confound, and could come back empty if the cascade photon rate
sits under the detector's own floor ([`PLAN.md`](../PLAN.md) §8 item 5). That is
trapping-free detection, established on the sibling 5S–5D line
([Hassanin 2023](../lit/hassanin2023.md),
[Beard 2024](../lit/beard2024.md)) and plausibly feasible with the IR receiver
already on the bench, a New Focus 2153 femtowatt photoreceiver with gain to
2×10¹¹ V/A over DC–750 Hz ([APPARATUS.md](../APPARATUS.md) §3). It would support
the density and amplitude work at the higher temperatures item 3 needs.

None of the three is new physics, and each removes a systematic the 2025
dataset had to live with. None of it is scheduled or assigned. The specification
([`PLAN.md`](../PLAN.md)) is written so that any prefix of it can be run, whenever
that becomes possible.
[`FUTURE_TRANSITIONS_titsapph.md`](../FUTURE_TRANSITIONS_titsapph.md) §4 ranks the
papers these items would produce against the other candidate lines, by
risk-adjusted distinctiveness per unit bench cost rather than by leverage, and
puts the O-band null of §1.2 first of the four.

---

*[What the 2025 dataset delivered](04_what-2025-delivered.md) · [The next nanofibre session](06_next-nanofibre.md)*
