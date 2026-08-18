*Chapter 2 of 11 of [the plan](../PLAN.md)*

## 3. Priorities if the budget shrinks

The session's job is bounds to measurements. Rank the work by which bound becomes
a measurement and how absolute. If a day is lost, cut from the bottom, never
the top. This section ranks observables and points each item at the block that
runs it. §10 costs the sampling currencies against the measured 2025 failure
modes.

[`BIG_PICTURE.md`](../BIG_PICTURE.md) §5 also ranks new vapour-cell measurements,
by leverage on the physics rather than by what a shrinking budget cuts, and its
order is beam waist, the pull, same-session high temperature, tighter focus.
The two orders differ because the criteria differ, and the items are the same
items. The ramp-monitor export and the retro ratio are absent from that list
because they are instrument repairs rather than new physics, which is exactly
why they sit at the top of this one.

**stage 0, the systematic floor. Protect first. None of these is a
more-data knob.**

**The fixed lock, the epoch condition, which the cut rule cannot reach.** Every
item ranked below assumes a laser held to an absolute reference for the length
of a block, so the lock is the premise of the session rather than a line in it,
and cutting from the bottom can never reach it: cutting removes days, while
removing this removes the epoch and with it every item above. `APPARATUS.md`
§1.1 is the record of what was engaged in 2025. Three dated photographs of the
SolsTiS control page show the etalon and reference-cavity locks holding the
laser short-term and the ECD row reading Not Locked in all three, and that
section's 2026-07-25 correction identifies ECD as the external cavity doubler
rather than a frequency reference. So the deficiency those photographs
establish, and the one this session exists to fix, is the missing outer loop:
no lock against an absolute reference was ever closed, and the cavity set point
was moved by hand whenever drift walked the line out of the window, which is
why the dataset's centres carry no metrological meaning. The instrument for closing
that loop on this system is the wavemeter link. The cavity lock itself was
repaired on 2026-08-16 and its state reconfirmed on 2026-08-18, so this stage
now tests an existing lock rather than waits on a repair, and the go/no-go
below is the stability measurement that licenses spending science shots on it.
**Needs.** The etalon and reference-cavity locks engaged and past the thermal
transient of §7h, the wavemeter link engaged, and a spare channel carrying the
lock state. No new hardware (`APPARATUS.md` §1.1). **Shots.** No science shots.
One continuous wavemeter record at a fixed set point before the first science
block, and another after any pause long enough to reopen the transient.
**Go/no-go.** Engage the lock chain and hold it thirty minutes. It passes if
the held drift magnitude over that half hour stays below 0.025 MHz per minute,
the upper edge of the dataset's own held-lock band. The fig15 record puts that
band at 0.016 MHz per minute in magnitude, 0.007 to 0.025, fitted across the
campaign's five-hour power session with the sign undetermined, so the criterion
asks the new epoch to be no worse than the old one at its worst. On fail the
session falls back to the drifting-lock protocol and every block keeps its
per-block ruler calibration, which is the record's own licensed mode, so the
day is degraded and not lost. **Empty.** No empty case. The half-hour record
either meets the criterion or it does not, and either way it selects which of
the two protocols the day runs under. **Record.** The half-hour wavemeter
record with its fitted drift magnitude and sign, the lock states engaged, and
the protocol selected. Runs first in §9 D1, ahead of the export below.

0. **Export the ramp monitor.** The triangle drive was on scope CH1 in 2025 and
   only CH2 was saved. Without it the exported time axis is referenced to the
   scope's horizontal setting, which is how a reconstructed "laser history"
   turned out to be the knob and why the centre channel is dead. The size of
   that loss is recorded rather than estimated: fitting a shared pull against
   three drift forms leaves the light shift bounded only at 9.49, 14.57 and
   17.65 MHz, and its sign flips between the first two, which is
   unidentifiability and not imprecision ([`RESULTS.md`](../RESULTS.md) C3e). One
   extra column fixes the time origin independently of both knob and laser.
   Rahaman & Dutta (2022)
   co-record exactly this on the sister Cs line. Two design rules travel with
   it, both learned on the 2025 dataset. Cycle or randomise the power ordering so
   that drift is orthogonal to the pull, which in particular rules out putting
   the lowest power last in a descending ladder, where it is the most drifted,
   lowest-SNR rung and the only one whose sweep retrace re-crosses the line. And
   leave the horizontal position alone, or log it, because every move severs the
   centre record.
   **Needs.** One spare scope channel, and the ramp monitor already available on
   the bench. `APPARATUS.md` §4.2 records that channel as present and costs it
   low, calling it the first thing to drop if channels are contended, and this
   plan disagrees with that priority rather than with the hardware fact. The
   verdict there was written before the window-reference retraction and weighs
   the ramp against the EOM comb, which is the wrong comparison: the comb fixes
   the scale and the ramp export fixes the origin, and the origin is what the
   centre channel lost. That is what lifts it to stage 0 here. **Shots.** The
   triangle drive co-recorded on
   every science trace, not sampled. **Go/no-go.** Confirm on the first exported
   file that the ramp column is present and that its apex times reconstruct the
   sweep direction. If it is absent, the session still runs and the centre
   channel stays dead, which is the 2025 outcome. **Empty.** No empty case, the
   column is either saved or it is not. **Record.** The ramp column in every
   export, and the horizontal-position log. Producers:
   `scripts/run_laser_history.py` and `scripts/run_stark_centres.py` are the two
   modules whose 2025 failures this repairs.
1. **Beam-profile w₀ per configuration, knife-edge plus camera (§4.2).**
   S₀ ∝ 1/w₀² and transit rides on w₀, so w₀ sets the systematic on every
   absolute number (a 10% w₀ error is 20% on Δα) and collapses the
   transit-against-σ_laser degeneracy. This is the difference between a
   w₀-conditional bracket and an absolute measurement. Run as the metrology
   block of §4.2, an afternoon per configuration, which is the allocation the
   decision-maker table carries.
2. **Retro ratio ρ in situ, per configuration, and it drifts with
   temperature.** S₀ ∝ (1+ρ). The retro leg is exit-window → lens → mirror →
   lens → exit-window, so ρ = T_win² T_lens² R_mirror, and the exit window films
   with Rb as the cell cools. A film taking per-pass transmission from 0.99 to
   0.90 takes ρ from ~0.90 to ~0.75 across 130→70 °C: an ~8% drift in S₀ from
   optics alone, which uncorrected reads as a temperature-dependent light shift.
   Measure the stable part (lens²·mirror, once, before the campaign) and the
   drifting part (window transmission before AND after the cell, at every
   condition). A pick-off reading both the outgoing and returning beam gives ρ
   directly with no symmetry assumption. The wide-scan pedestal of §5 would give
   a second, in-situ ρ on the same traces, by a route that shares no optic with
   the pick-off.
   **Added 2026-08-09.** A third route exists and it measures a better quantity.
   Offsetting the retro arm in frequency makes the two arms beat, and the beat
   amplitude reads the MODE-OVERLAP-WEIGHTED ρ, which is what enters S₀, where a
   pick-off reads power. It also makes the fringe mean exact for every velocity
   class instead of the fast ones, which is the fringe-resolved tail's only
   remedy. It is not cheap: the offset has to outrun the axial thermal spread
   rather than the linewidth, so it is 800 MHz and above, and the present
   self-imaging retro would have to be rebuilt double-pass.
   [notes/running_wave_and_waist_design.md](../notes/running_wave_and_waist_design.md)
   has the criterion, the numbers and the costs.

**stage 1, enablers. The measurement does not exist without them.**

3. **150–170 °C, same session, interleaved T order.** 70–130 °C gives
   Δγ ≈ 20 kHz (invisible), while 150–170 °C gives 0.07–0.25 MHz. In 2025
   temperature ran monotonically down with elapsed time, so T and drift were
   confounded, and that is what turned β into a bound. The hot points alone are
   not sufficient: at the dataset's block-noise floor they reach only ~1–3σ per
   block, and cutting that floor 4× (interleaving plus per-trace power logging)
   takes the same signal to ~3–12σ (`results/resolving_power.csv`). Both halves
   are load-bearing. Runs as §7c.

   **What the hot end costs, added 2026-08-10 and not previously carried.** The
   infrared halo of [methods 4](../methods/04_the_composite_model.md) re-excites
   5P to 6S at 1.1 per cent of the primary rate at 130 °C, **8.9 at 150 and
   30.6 at 170** (`scripts/run_campaign_conditions.py`, and it is ENVELOPE with
   a standoff band of 21 to 34 per cent at the top). **β_self is read from
   widths and none of this reaches it.** What it reaches is every amplitude
   comparison taken in the same session, which is where M7 and M10 live, and at
   a third of the primary rate the argument that the halo merely rescales the
   amplitude is being asked to hold well past where it was derived. Two
   consequences for the session plan, neither of which costs drive time: take
   the **amplitude** work at the cold end and the **width** work at the hot end,
   and **vary the standoff deliberately at one hot condition**, since that is
   the measurement that turns this envelope into a number and it costs one
   translation stage. Blackbody over the same extension stays negligible: the
   6S to 6P transfer runs 2.0 to 6.5 parts per million and the thermal shift
   161 to 245 Hz, neither of which a width measurement can see.
4. **The pull the fixed lock resurrects.** The lock itself is the epoch
   condition above, not a ranked item. What the ranking contains is the
   observable it brings back, the line centre against power, which is the
   first-order light shift, the strongest handle in the programme and the one
   [`BIG_PICTURE.md`](../BIG_PICTURE.md) §5 ranks second overall. It needs
   minutes-scale stability rather than all-night stability, which makes it the
   least exposed of the three conversions. Runs as §6 item 1.
5. **An absorption channel for N(T).** The collisional bound is denominated in
   a density the record adopts rather than measures, and the audit that
   quantified the cold spot puts it at ×1.4 to ×7 leverage on the headline C1
   number, plausibly a larger systematic than the beam waist and cheap to bound
   in the same session, which is why it recommends moving this item near the top
   of this ranking ([`PREREGISTRATION_RESULTS.md`](../PREREGISTRATION_RESULTS.md)
   addendum 15). It sits in stage 1 rather than lower because §7c cannot run the
   high-temperature grid until the lag is characterised, so it enables rather
   than refines. Runs as §8 item 3.

**stage 2, handle strength (S₀ ∝ (1+ρ)P/w₀²), served by two waists.**

6. **Small waist (16 µm), the Stark, skew and lineshape-form configuration**:
   ~16× more S₀ than 64 µm, so the skew (∝ S₀³) becomes measurable, and at the
   cliff (S₀ ≫ linewidth) the triangular ramp is directly visible. The skew's
   sign-flip test rides on the collection geometry: the flip happens where the
   axial window Z_c crosses 1.12 z_R, which the small waist puts within reach
   (§6 item 4). **64 µm is the clean-κ width workhorse.**
   **Added 2026-08-09, and it bears on the number this item quotes.** Item 7
   below already notes that 16 µm is saturated at 225 mW and treats that as a
   statement about power headroom. It is also a statement about the SKEW, which
   this item does not make. The ramp weights each shift by the signal it
   produces, and that weighting is the intensity squared only while the drive is
   weak, so at a saturation parameter of 8.5 the effective exponent falls and the
   predicted skew at 16 µm moves from −0.36 to −1.07, a factor of three, in the
   same direction as the sign flip rather than against it. The committed axial
   machinery cannot see this, since it takes an integer photon exponent. So the
   sign-flip test stands and the magnitude does not, and the middle of the range
   is worth costing: 32 µm keeps the sign positive at a saturation of 0.5 and
   carries a shot-noise figure of merit 24 times the present waist.
   [notes/running_wave_and_waist_design.md](../notes/running_wave_and_waist_design.md)
   has the table, the identity that a smaller waist buys no shift at matched
   intensity, and what the machinery needs before 16 µm is chosen deliberately.
7. **Power.** The 2025 ceiling of 225 mW is almost certainly an assumption, not
   physics. Photoionization is excluded (993 nm, 1.25 eV, is below the 6S
   threshold at 1.68 eV). Two-photon saturation leaves 1–2 W of headroom at
   the measured waist, where the on-axis saturation parameter is 0.033 at
   225 mW and falls as the inverse fourth power of the waist, so a wider
   focus only adds headroom. The predicted on-axis shift at 225 mW is 0.35 MHz at the adopted
   measured waist, with a band of 0.285 to 0.404 MHz across the waist and retro
   priors (`results/stark_sweep.csv`), against Γ = 3.49 MHz, and the 2025
   dataset's amplitude ∝ P² to 225 mW confirms the headroom. At 16 µm the
   line is already saturated at 225 mW, so power is not the knob there. The
   one in-beam part with a plausible sub-watt limit is the EOM: check its
   damage rating before
   lifting the ceiling, and watch the P² bend at 64 µm rather than assuming 1 W
   is clean. There is also a physics ceiling on drive power that is not a damage
   limit, the point at which the light shift itself exceeds a tenth of the line
   width, and the projections table carries it per rung.

**stage 3, sampling and precision. Refines, does not enable.**

8. More power points: a 6–8 point log grid into the cliff plus a linearity
   check beats crowded points.
9. More days: the value is earning the day-to-day systematic error bar, plus
   the epoch bridge to the 2025 dataset's own waist. Budget 1–2 days. Never
   trade the high-T lever or the beam profile for averaging days.

---

*[The aim and the risks](01_aim-and-risks.md) · [Configurations and optics](03_optics-protocol.md)*
