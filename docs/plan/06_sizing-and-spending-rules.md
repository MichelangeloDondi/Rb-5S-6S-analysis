*Chapter 6 of 11 of [the plan](../PLAN.md)*

**The question.** How large must a session be, and what does the 2025 post-mortem forbid?
**Takes.** The blocks of chapters 4 and 5.
**Gives.** The block register, the sizing arithmetic, and the spending rules.
**Skip if.** You want the physics rather than the budget.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

> **Question.** How large must a session be, and what does the 2025 post-mortem forbid?
> **Design.** Block sizes set by the precision each block must reach, not by the time available.
> **Ambiguity removed.** The block-to-block drift that swamped the 2025 trends.
> **Success.** Each block reaches its stated go criterion inside its stated duration.
> **Residual uncertainty.** Anything the register marks as needing hardware the bench does not have.

## The block register

Every block this document costs, with its address, what it converts, its cost,
its empty case, and whether its output is community-facing. Durations are this
document's own where a block is costed and are marked otherwise. Sections 5 to
8 and 12 hold the blocks. Section 3 ranks them for a shrinking budget, and each
of its items points at the block that executes it.

| block | address | what it converts | bench cost | could come back empty | output |
|---|---|---|---|---|---|
| the fixed lock | §3 stage 0 lead, run first in §9 D1 | a shape-only epoch into one whose centres carry metrological meaning | half an hour before the first science block, no new hardware | no empty case, the held-drift record selects which protocol the day runs under | internal |
| ramp-monitor export | §3 item 0, run in §9 D1 | the dead centre channel into a time axis independent of the scope knob | one spare channel, no bench time of its own | nothing, the column is either saved or it is not | internal |
| beam profile w₀ | §3 item 1, §4.2, run in §9 D1 and D4 | every w₀-conditional absolute number into a measured one | an afternoon per configuration, no atoms | the number may describe the present bench rather than the 2025 one | community |
| retro ratio ρ in situ | §3 item 2, §4.2, run in §9 D1 and D4 | an assumed ρ into a measured one, per configuration and per temperature | inside the metrology afternoon | a pick-off that does not separate outgoing from returning light | internal |
| transit-difference anchor and model-form closure | §5, run in §9 D6 | a knife-edge-conditional intensity axis into one anchored on thermal physics, and an assumed transit kernel into a tested one | one cold, low-power day at S and L | the cusp may sit under the detection bandwidth, leaving the model comparison without a preference | community |
| wide-scan Doppler pedestal | §5 | an adopted gas temperature and retro ratio into in-situ measurements | a wider scan setting on dwells already costed, no new hardware and no lock quality | the pedestal may not separate from scattered light, and the area ratio is flat in ρ near one | community |
| mean pull against P | §6 item 1 | the AC-Stark bound into the first measured light shift on this line | one morning of randomized power cycling | the lock may not hold minutes-scale stability | community |
| excess variance against P² | §6 item 2 | a second, independent functional of the same S₀ | rides the same blocks as item 1 | the second moment may stay under its own floor | community |
| skew hunt at S | §6 item 3 | a bound on the third cumulant into a detection, or a meaningful bound | the deep-integration day, §9 D5 | not a promised result, sized for the pessimistic end | community |
| geometry sign flip | §6 item 4 | a parameter-free prediction into a test, through the axial window Z_c | the slit scan inside §9 D5 | the flip is secured by the landscape cathode, so the exposure is magnitude and not sign | community |
| collection rebuild | §6, the two-lens relay | field of view decoupled from collection, and Z_c set as hardware | inside §9 D1 | the slit image plane may not be reachable with the available focal lengths | internal |
| opposite-order T grid | §7a | a drift-confounded density slope into a measured residual | two days, §9 D2 and D3 | the residual may exceed the physics, which would be the result rather than a failure | community |
| five T blocks per peak | §7b | one residual degree of freedom into three | inside D2 and D3 | nothing, the blocks either run or they do not | internal |
| same-session 150–170 °C | §7c | reach, not combinability, on the density lever | inside D2 and D3 if the oven allows | the oven may not reach or hold the top of the range | community |
| matched-PM ruler | §7d | a monitor that was uncorrelated with the science light into a drift compensator | interleaved with science blocks, unpriced separately | the tank may not reach the modulation index the null needs, which is an open item | community |
| returned-to block | §7e | an assumption that block scatter averages down into a test of it | one short block per day | one block settles the direction, not the magnitude | internal |
| interleaved peaks and timestamps | §7f, §7g | cross-peak systematics of 30–50% into 2–4%, and block order into a clock | inside every dwell | the scope may not export per-trace times, in which case the external log carries it | internal |
| etalon thermal discipline | §7h | dropouts inside the thermal transient into a bounded held-lock drift | two hours before first data, and again after any long pause | the transient may be longer on the day than the dataset measured | internal |
| σ_laser at L | §7i | a drifting-lock bound into a fixed-lock measurement, with the collision prior stated | falls out of the T grid | it stays a bound if the collision prior cannot be tightened | community |
| width-to-shift ratio | §7j | a van der Waals anchor into an independent test | needs the centre channel, so it rides the fixed lock | the pressure shift may stay under the block scatter | community |
| degeneracy-law test | §8 item 1 | area ratios into a parameter-free check at the interleaved floor | inside every interleaved block | PMT nonlinearity may swamp the 1–3% floor | community |
| four-line common-slope Δα | §8 item 2 | four line-specific pulls into one over-determined coefficient | rides the §6 item 1 blocks | admissible at L only, since S is saturated | community |
| absorption channel for N(T) | §8 item 3 | an adopted vapour density into a measured one, with the cold-spot lag | a weak D-line probe and a photodiode, new hardware | the cold spot may not flatten enough at the high end to be read | community |
| fluorescence over absorption | §8 item 4 | a trapping confound into a measured collection efficiency | rides the same blocks as item 3 | needs item 3 to run at all | community |
| 1.3 µm cascade channel | §8 item 5 | the degeneracy law measured without the trapping confound | an InGaAs detector, new hardware | the cascade photon rate may sit under the detector's own floor | community |
| O-band null rider | §12 | a computed polarizability zero into a 6S to 7P matrix element | one telecom-band diode and its wavemeter, riding any cell session | the delivered perturber intensity at the cell could undershoot | community |

## 9. Session sizing

Sized to about eight days at the cell. An ordering, not a booking: run in
this order and a truncation at any point leaves the higher-priority
conversions done.

| day | content | deliverable |
|---|---|---|
| D1 | Setup and metrology at configuration L, in the order given below the table, because the first item selects which protocol the rest of the session runs under. | the held-drift record and the protocol it selects, a time axis independent of the scope knob, the outer-loop characterisation, the measured w₀ and ρ at L, and a frozen bracket cadence |
| D2 | Temperature grid day A at L, ascending, four peaks interleaved plus a mini-P excursion per dwell, sentinel three times, 150/170 °C if the oven allows. | the ascending grid |
| D3 | Temperature grid day B at L, descending, sentinel three times. | with D2: β_self or a tighter bound, the fixed-lock σ_laser, and the measured drift residual |
| D4 | Power grid at L, randomized, about 8 powers, morning. Reconfigure to S, an afternoon: knife-edge, camera, ρ. | the mean pull and the excess variance, the four-line common slope, and the measured w₀ and ρ at S |
| D5 | Skew deep-integration at S. The slit scan g₁(Z_c) at four or five settings, the sign walk of §6 item 4. Power grid at S. Overnight, cool for the cusp. | S₀ at the small waist, the third cumulant or its bound, and the geometry sign flip |
| D6 | The cold, low-power blocks at S and L specified in §5: the transit kernel of Lehmann 2021 against a Voigt, on the same data that anchor the differential-transit intensity calibration. | the model-form closure and the absolute intensity axis, hence Δα in physical units |
| D7 | Configuration M spot check, half a day: knife-edge, camera, power grid, one 130 °C point. Wavemeter GHz-linearity shots (§11). | the 2025-epoch bridge, and the wavemeter's own frequency scale |
| D8 | Contingency: re-run whatever the bracket veto excluded. | the recovered blocks, or unused |

**D1 in order.** The sequence matters, so it is a list rather than a cell:

1. The fixed lock of §3 stage 0, engaged and held thirty minutes against its
   go/no-go, before anything else. It selects which protocol the rest of the
   session runs under, so nothing else can start until it has passed or failed.
2. The ramp-monitor export of §3 item 0, configured before any data is taken.
3. Wavemeter-link characterisation: how tightly the laser holds a set point,
   and its calibration drift. This is the system's only outer loop, it needs no
   new hardware, and it decides whether shifts are measurable at all.
4. Telescope install.
5. Collection rebuild, the relay and slit of §6, landscape.
6. Configuration L metrology, an afternoon: knife-edge, camera, calipers, ρ,
   and polarization with tomography and the extinction null.
7. While the oven settles, the drift-characterization block that freezes the RF
   cadence (§10.5).

The interleaved blocks of §7f run inside D2 to D5 and carry the degeneracy-law
and trapping tests of §8. The wide-scan pedestal of §5 rides whichever of these
days runs.

## 10. Spending rules from the 2025 post-mortem

### 10.1 The 2025 failure modes

Seven of the ten sizes below are measured on the dataset. The three that are
not say so in the cell, with the assumption they rest on, because a reader who
takes row 8 for a measurement of these cell windows would be reading a worked
example as a bench fact.

| # | what bit | size, measured unless the cell says otherwise | consequence | cure |
|---|---|---|---|---|
| 1 | between-block width scatter (drifting lock) | σ_B ≈ 0.12 MHz vs within-block SEM ≈ 0.05 | widths drift-limited, σ_laser a bound | fixed lock, brackets and veto (§7a) |
| 2 | only 3 densities, 1 residual DOF | t(0.95,1) = 6.31 | β_self a bound | folding in the 130 °C point gives dof=2, t=2.92 (the 2026-08-02 headline), and five or more T blocks tighten further (§7b) |
| 3 | T monotonic in time | density slope collinear with drift | a guard had to carry the claim | opposite-order days (§7a) |
| 4 | 2025 lever short at ×16.2 (three T points) | joint β collapses 0.036 → 0.014 once the ×52.5 (130 °C) anchor is folded in | the fitted floor responding correctly to a near-flat gamma_coll(T), folded into the headline 2026-08-02 | same-session 150–170 °C (§7c), to reach densities where a ~kHz effect could clear the block-noise floor |
| 5 | no acquisition clock in the analysed exports | block order was the only time coordinate, and not even the acquisition order | σ_laser-sharing untestable, and the recovered clock later dated the peaks 54–76 min apart | interleave the peaks in minutes plus hardware timestamps (§7f, §7g) |
| 6 | ruler light differed from science light (HWP trick) | monitor reliability ≈ 0 | no drift compensator | matched-PM ruler (§7d) |
| 7 | w₀ never measured | *not measured*, a tens-of-% prior, from the 64 µm beamline-lineage value | every absolute number conditional | beam profile first (§3 item 1) |
| 8 | ρ(T) never measured | *not measured*, ~8% S₀ drift, computed in §3 item 2 for an assumed film taking per-pass transmission 0.99 to 0.90, not observed on these windows | optics drift reads as physics | T_win before and after, per condition (§3 item 2), with the pedestal cross-check of §5 |
| 9 | P sweep at a single T | *not measured*, the trapping immunity is untested across density, so this row is a gap rather than a size | discriminators data-starved | mini-P excursion per dwell (§10.4) |
| 10 | between-block amplitude wander | 30–50% | amplitude observables dead | polarization defined plus tomography (§4.4), 12–16 repeats (§7f) |

Items 1 to 3 share one root cause: 2025 spent statistics against a
systematics-limited experiment. Within-block noise was already 2.4× below the
block scatter, and the campaign kept buying the cheap term.

The audit trail behind rows 2 and 4, including the reading each replaced, is in
[`PREREGISTRATION_RESULTS.md`](../PREREGISTRATION_RESULTS.md). This table carries
the design consequence only.

### 10.2 The variance budget, and a stopping rule

Var(mean) = σ_w²/n + σ_B², and repetition divides only the first term. At the
2025 numbers, doubling the repeats buys 4% for 100% more time. The same
hour on one more T block divides σ_B by √N and buys a residual degree of
freedom, and the t ladder is where the record bled: 6.31, 2.92, 2.35, 2.13,
2.02 for one to five DOF. Freeze the stopping rule in the run notebook:
repeat a condition until σ_w/√n < σ_B/2, then stop, since past that point
infinite repeats recover at most 12%. With 2025-like noise that is n ≈ 4–5.
Repetition is the right currency only where the observable is genuinely
photon- or gain-limited: the skew integration, the amplitude ratios, the
ruler-width monitor.

### 10.3 What ordering buys and repetition cannot

Within one sweep direction, drift monotonic in time is exactly collinear with
physics monotonic in T. That is a rank problem, and no number of repetitions
touches it. One ascending day plus one descending day cancels every
time-linear drift component in the mean and measures the residual in the
difference: a systematic error bar earned, not assumed. Full T randomization
would pay marginally more but costs thermal settling at every reversal. The
single reversal buys most of the protection free. Randomize the free knobs
instead, the power order and the peak order.

### 10.4 Loop structure

T is the only slow knob, so it is the outer loop, and each dwell extracts
everything cheap while the cell sits there: four peaks interleaved, a
randomized 2–3 point mini-P excursion (~10 min, which turns the single-T
power sweep of 2025 into width-against-P at every temperature), matched-PM
ruler interleaves, and the window-transmission reading. Never the converse:
re-thermalizing per power point multiplies dead time for nothing.

### 10.5 The RF cadence, measured on the day

Strict on-off alternation halves science time for monitor information that
saturates within a few brackets. With the matched-PM ruler an RF-on trace is
no longer dead time, but tooth overlap still contaminates the moment
observables, so skew and centered moments come from RF-off traces only.
Spend the first ~30–45 min of D1, while the oven settles, alternating on and
off at one fixed condition. Compute the Allan deviation of tooth width and
sweep rate against lag, set the bracket cadence where drift crosses the
few-trace SEM, and freeze it before the first science block.

### 10.6 The sentinel condition

Pick one condition (say 90 °C, 125 mW, peak 4192, configuration L) and
re-measure it at the start, middle and end of every day, identically. Three
short blocks a day buy a within-day drift series at fixed physics, the
day-to-day reproducibility number that §3 stage 3 demands before days are
averaged, and the common level that ties the two opposite-order grids together.
Every 2025 drift statement is an inference through the lineshape model because
no condition was ever revisited. The sentinel makes drift a direct observable.

### 10.7 The currency table

| currency | attacks | marginal value at 2025 numbers | verdict |
|---|---|---|---|
| beam profile, ρ, same-session high T | the systematic floor | converts bounds to absolute measurements | never cut |
| second day, opposite T order | time-monotone bias | removes what no averaging can, and measures the residual | mandatory |
| more T blocks (to ~6) | DOF and σ_B averaging | ~2.7× from the t quantile alone | best statistical buy |
| interleaves (peaks, mini-P, rulers) | cross-condition systematics | 30–50% → 2–4% at near-zero cost | always on |
| more repeats, same condition | photon noise only | 4% for 2× time | only for skew, amplitudes, ruler monitor |
| strict RF alternation | monitor variance | saturates, and halves science time | no, use the measured cadence (§10.5) |

Spend structure before statistics: orders before days, blocks before repeats,
interleaves before points, and one measured cadence instead of a guessed
alternation.

---

*[Width, collisions and amplitude](05_width-collision-amplitude.md) · [Acquisition settings](07_acquisition-settings.md)*
