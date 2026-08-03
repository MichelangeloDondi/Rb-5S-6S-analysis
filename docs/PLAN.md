# A fixed-lock session for Rb 5S₁/₂→6S₁/₂: proposal and measurement protocol

*A specification, not a schedule. Nothing here has been agreed with any group,
no date is assumed, and no operator is named. It is written to be refereed as
a proposal and executed as a protocol: each item names the archival bound it
would convert into a measurement, so a partial session has predictable value.
The archival analysis this builds on is complete and under continuous test.
Its pipeline ingests session data unchanged, so the session carries shots, not
analysis risk. The executed archival analysis plan is summarised in Appendix A
and documented in [`methods.md`](methods.md).*

## 1. Aim

The 2025 archive delivers a method and bounds: the drift-immune lineshape
framework, the self-calibrating EOM ruler, the identifiability and coverage
analyses, and the computed 5S–6S dynamic polarizabilities and magic
wavelengths ([`THEORY_NOTE.md`](THEORY_NOTE.md) §5). That result stands on its
own and depends on no further data. A session is an upgrade, not a rescue. It
would convert three named bounds into measured coefficients:

1. **The AC-Stark coefficient Δα.** The strongest observable: under a fixed
   lock the pull (∝ S₀) comes alive, and a small waist raises S₀ several-fold.
   This is where the intensity effort points.
2. **β_self and the collisional self-shift.** Intrinsically ~kHz per
   10¹² cm⁻³, so the deliverable is a modest first measurement or a much
   tighter bound, completing the 5D/7S self-broadening series
   ([BIG_PICTURE §1](BIG_PICTURE.md)). Do not over-invest expecting headline
   precision.
3. **σ_laser of the new epoch**, with the transit term removed by geometry
   instead of assumed.

The smallest tranche that converts even one bound is the config-L width
program: a geometry-setup block plus the two opposite-order T-grid days
(§9, D1–D3). That alone yields β_self, or a much tighter bound, plus the
fixed-lock σ_laser. A single same-direction day does not: the
bound-to-measurement guarantee needs the opposite-order pair (§7). Value is
monotone in shots. A session truncated at any point still leaves the
higher-priority conversions done (§3), and if no session is ever run the
archival result stands unchanged.

## 2. Risks a referee would raise

*Each answer concedes what is true first. The campaign is not worth running if
these do not survive.*

**"Orson (2021) already published nulls on this line. Your bounds say 'we also
saw nothing', slower."** True as pure numbers: the archival bounds are
confirmatory of Orson's nulls, same direction, tighter. The increment is by
channel. The method (a closed-form two-photon ramp lineshape law plus a
reference-free moment readout) is not pursued elsewhere. The S₀ bound
(< 0.27 MHz, ~22× below Orson's ~6 MHz null) was extracted from shape alone
under a drifting lock. And a fixed-lock session would give the first measured
light shift on this line, plus the collisional self-shift: positive
observables, not sharper nulls.

**"The lock drifted MHz-scale all night in 2025. What stops a repeat?"** The
root cause is now diagnosed, not just remembered: cavity-lock dropouts during
the ~2 h etalon thermal transient, with held-lock drift only ~0.02 MHz/min
([`APPARATUS.md`](APPARATUS.md) §6). The etalon discipline in §10 is the
procedural fix. What remains asserted is only that it will be followed. The
session also degrades gracefully. The pull is a differential measurement
needing minutes of stability. The pre-registered bracket veto (§7) cuts
drift-jump blocks instead of averaging them. The sentinel condition (§10.6)
monitors residual drift directly. Ayachitula (2024) held a lock on this same
transition to < 0.5 kHz over 50 min, so a stable lock is demonstrated, not
hoped for. Worst case, the D1 beam-profile and ρ measurements retroactively
sharpen the 2025 archive and stand alone.

![the drift problem, what was extracted, and what a fixed lock buys](../figures/fig15_drift_story.png)

*The whole argument in one figure. Top: the drift problem as photographed on
a preliminary session, a wavemeter record of cavity re-locks and relaxations
(no such log survives from the campaign itself). Middle: the campaign,
reconstructed from its own traces. Line offsets are meaningful only within
one scope-knob epoch, the spikes are re-lock events, and the measured
held-lock drift barely moves in three hours, which is why shapes survive and
centres do not. Bottom: what each drift regime licenses. The 2025 lock
supported the shape-only bounds this archive reports. A fixed lock of the
class already demonstrated on this transition would make the centre channel
usable, converting the bounds into the measured pull, the collisional
self-shift, and a 3–12σ β_self.*

**"Drift does not stay out of the shape. It skews the line within a scan, and
skew is your observable."** Right in principle, answered by timescale. A scan
is ~1 s, and even the drift envelope is ~0.017 MHz/s, so within-scan drift is
~0.01 MHz against a 5.25 MHz line, and each block carries its own EOM ruler.
Drift acts between blocks, which is exactly why β_self is a bound today. The
closure test (inject a within-scan ramp, confirm unbiased moments) is
committed: `tests/test_intrascan_drift.py`.

**"A Δα bracket that wide discriminates nothing."** Partly answered by the
joint three-session bound: S₀(225 mW) < 0.27 MHz sits 1.3× below the
0.35 MHz prediction at the adopted geometry, so the archive constrains the
(Δα, intensity) pair. What it cannot do is split the pair: either the
intensity or |Δα| sits modestly below the adopted values, and the most
conservative data subset reaches the prediction itself and needs no
headroom at all. A beam-profile measurement decides which. The measured
coefficient needs the session.

**"Your own recompute flips the sign of Δα against the published computation.
Bug?"** Not a bug. The M16 recompute is validated on anchors it does not fit
(the measured 5S tune-out to ~2 pm, the static polarizabilities) and agrees
with Orson's magnitude within 5%. The sign disagreement has an identified
mechanism, every archival result is sign-immune (bounds and the asymmetry
null use |Δα|), and the item is flagged for external theory adjudication
([`THEORY_NOTE.md`](THEORY_NOTE.md) §5). It blocks nothing.

**"Put a student on this and it strands them with un-analysed shots."** The
handover is a project commitment and belongs in a direct conversation, not in
this document. What the document can put against the risk: the pipeline is
built to a bus-test standard with a documented ingest path, it ingests session
data unchanged, and the smallest tranche has a defined standalone deliverable,
so a truncated session yields a finished result rather than orphaned data.
An adaptation guide ([`ADAPTING.md`](ADAPTING.md)) names the seams for other
lines and species.

**"The numbers keep moving. How do I know they are frozen?"** Every headline
is generated from the committed CSVs, a registry test forces every quoted copy
to match its source, and releases are tagged. The audit report logs every
revision with its cause ([`PREREGISTRATION_RESULTS.md`](PREREGISTRATION_RESULTS.md)):
most moved toward more conservative error treatment, and the remainder were
identified biases, fixed and documented rather than absorbed.

## 3. Priorities if the budget shrinks

The session's job is bounds to measurements. Rank effort by which bound
becomes a measurement and how absolute. If a day is lost, cut from the bottom,
never the top. (This section ranks observables. §10 prices the sampling
currencies against the measured 2025 failure modes.)

**Tier 0, the systematic floor. Protect first. None of these is a
more-data knob.**

0. **Export the ramp monitor.** The triangle drive was on scope CH1 in 2025
   and only CH2 was saved. Without it the exported time axis is referenced to
   the scope's horizontal setting, which is how a 65 MHz "laser history"
   turned out to be the knob and why the centre channel is dead
   (`run_laser_history.py`, `run_stark_centres.py`). One extra column fixes
   the time origin independently of both knob and laser. Rahaman & Dutta
   (2022) co-record exactly this on the sister Cs line. Two free riders: do
   not move the horizontal position mid-session (or log it), and do not put
   the lowest power last in a descending ladder, where it is the most
   drifted, lowest-SNR rung and the only one whose sweep retrace re-crosses
   the line.
1. **Beam-profile w₀ per config, knife-edge plus camera (§4.2).** S₀ ∝ 1/w₀²
   and transit rides on w₀, so w₀ sets the systematic on every absolute
   number (a 10% w₀ error is 20% on Δα) and collapses the transit↔σ_laser
   degeneracy. This is the difference between a w₀-conditional bracket and an
   absolute measurement.
2. **Retro ratio ρ in situ, per config, and it drifts with temperature.**
   S₀ ∝ (1+ρ). The retro leg is exit-window → lens → mirror → lens →
   exit-window, so ρ = T_win² T_lens² R_mirror, and the exit window films
   with Rb as the cell cools. A film taking per-pass transmission from 0.99
   to 0.90 takes ρ from ~0.90 to ~0.75 across 130→70 °C: an ~8% drift in S₀
   from optics alone, which uncorrected reads as a temperature-dependent
   light shift. Measure the stable part (lens²·mirror, once, before the
   campaign) and the drifting part (window transmission before AND after the
   cell, at every condition). A pick-off reading both the outgoing and
   returning beam gives ρ directly with no symmetry assumption.

**Tier 1, enablers. The measurement does not exist without them.**

3. **150–170 °C, same session, interleaved T order.** 70–130 °C gives
   Δγ ≈ 20 kHz (invisible), while 150–170 °C gives 0.07–0.25 MHz. In 2025
   temperature ran monotonically down with elapsed time, so T and drift were
   confounded, and that is what turned β into a bound. The hot points alone are
   not sufficient (M17): at the archival block-noise floor they reach only
   ~1–3σ per block, and cutting that floor 4× (interleaving plus per-trace
   power logging) takes the same signal to ~3–12σ. Both halves are
   load-bearing.
4. **The fixed lock itself.** The epoch premise, and what resurrects the pull.

**Tier 2, handle strength (S₀ ∝ (1+ρ)P/w₀²), served by two waists.**

5. **Small waist (16 µm), the Stark/skew/form config**: ~14× more S₀ than
   60 µm, so the skew (∝ S₀³) becomes measurable, and at the cliff
   (S₀ ≫ linewidth) the triangular ramp is directly visible. The skew's
   sign-flip test rides on the collection geometry: the flip happens where
   the axial window Z_c crosses 1.12 z_R, which the small waist puts within
   reach (§6). **60 µm is the clean-κ width workhorse.**
6. **Power.** The 2025 ceiling of 225 mW is almost certainly an assumption,
   not physics. Photoionization is excluded (993 nm, 1.25 eV, is below the
   6S threshold at 1.68 eV). Two-photon saturation at 50–60 µm leaves 1–2 W
   of headroom (S₀(225 mW) ≈ 0.4 MHz ≪ Γ = 3.49 MHz, and the archival
   amplitude ∝ P² to 225 mW confirms it), while 16 µm is already saturated
   at 225 mW, so power is not the knob there. The one in-beam part with a
   plausible sub-watt limit is the EOM: check its damage rating before
   lifting the ceiling, and watch the P² bend at 60 µm rather than assuming
   1 W is clean.

**Tier 3, sampling and precision. Refines, does not enable.**

7. More power points: a 6–8 point log grid into the cliff plus a linearity
   check beats crowded points.
8. More T points: reaching 150–170 °C matters far more than point count. The
   real limit is knowing N (the cold spot, §8). Spend on the density axis.
9. More days: the value is earning the day-to-day systematic error bar, plus
   the archival-waist epoch bridge. Budget 1–2 days. Never trade the high-T
   lever or the beam profile for averaging days.

## 4. Configurations and optics protocol

### 4.1 The three configurations

Two working waists plus one continuity check (a third full waist is dropped
by design):

- **L (w₀ ≈ 60 µm, z_R ≈ 11 mm).** The width workhorse. Transit ~1.0 MHz,
  collection inside z_R, clean geometry. Runs the full two-day T grid.
- **S (w₀ ≈ 15–16 µm, z_R ≈ 0.8 mm).** The Stark/skew/cusp config. One model
  caveat is specific to it: the composite lineshape convolves transit with
  the natural Lorentzian, which is rigorous when the crossing time is long
  against the 6S lifetime (45 ns). At the archival waist the ratio is ~4. At
  16 µm it is ~1.3, so this is where a referee should ask for the
  convolution's validity range and where a Bloch-equation cross-check earns
  its time. A caveat to state and test, not a reason to retreat.
- **M (w₀ = 64 µm, the archival geometry).** Half-day spot check: knife-edge,
  camera, P grid, one 130 °C point, for direct 2025-epoch continuity.

![the bench of record](apparatus/apparatus_schematic.svg)

*The 2025 bench the session modifies, at its three touch points: a telescope
before the EOM sets the config waist, the retro leg (lens, mirror, exit
window) is where ρ is measured, and the collection arm is rebuilt as the
relay plus slit of §6.*

Size the telescope so the beam enters the EOM at ≤ 1 mm waist (the 3 mm
aperture then clips nothing). Per config, before science: knife-edge w(z) at
five or more z positions in two orientations, camera z-scan through the same
focus (§4.2), lens separations calipered at setup and teardown (§4.3), ρ in
situ (both directions), collection geometry measured (u, v, and the detector
aperture. The PMT of record is the side-on R636-10 with a 3 × 12 mm cathode,
mounted landscape), and polarization defined at the cell with a polarizer,
not merely logged (§4.4).

### 4.2 Why w₀ gets two instruments

w₀ is the dominant systematic of the whole analysis, and the one thing you do
not do to a dominant systematic is measure it once with an instrument that
has a single failure mode. The knife-edge gives absolute size in true power
units, down to the smallest waist, but integrates away the 2D shape: a
clipped or structured profile fits an error function acceptably and returns
the wrong waist. The camera gives shape (ellipticity, astigmatism, M², the
forward/retro overlap that backs ρ), but under-samples a 16 µm spot and its
saturation corrupts exactly the wings a power measurement needs. Each is
strongest where the other is blind. Run the camera first to find the focus
and validate the Gaussian the analysis integrates over, then size it with the
knife-edge. The camera pixel scale is also a third independent length ruler
beside the knife stage and z_R = πw₀²/λ, so a scale error must fool three
unrelated instruments to pass.

### 4.3 Lens separations as a creep detector

Caliper the two lens separations bracketing the cell at every setup and
teardown. Absolute accuracy (~1–2 mm) does not pin w₀, but it catches gross
mispositioning where it bites hardest: at config S a 1 mm placement error
costs over 2× in on-axis intensity (z_R ≈ 0.8 mm), directly an S₀ error.
Repeatability on fiducial marks is < 0.1 mm, so a setup-versus-teardown
change flags mechanical drift of the focus or the retro overlap during the
run. A config whose lenses moved is a config whose w₀ and ρ are suspect.

### 4.4 Polarization

For S→S lines the strong ΔF = 0 components are driven by the scalar part of
the two-photon operator, with amplitude ∝ ε_f·ε_b. Rajasree (2020) measured
on this line that the rate scales as the squared degree of linear
polarization and vanishes for circular. The configuration table (Nieddu 2019,
verified from the paper): parallel linear (π–π) gives the Doppler-free peak
on a Doppler pedestal and is the archival default. Crossed linear kills the
peak, same-handed circular is forbidden, and opposite-circular (σ–σ′, quarter
waveplates before both the cell and the mirror) gives a background-free peak
at half height.

Prescriptions:

- **Default π–π, polarization defined by a polarizer at the cell**, with a
  per-config extinction null: the forbidden settings must read zero, and any
  residual calibrates the impurity.
- **Characterize the retro-path retardance** by Stokes tomography of the
  returning beam. Double-passed birefringence in window, lens and mirror
  pulls ε_f·ε_b below 1 and lets it drift as optics warm: a concrete
  candidate for the archival 30–50% amplitude wander.
- **Fit removable QWP slots before the lens and before the mirror**, so σ–σ′
  is available on demand. It is valuable as a diagnostic, never as the
  default: it removes the Doppler pedestal (a pedestal-subtraction
  cross-check) and it switches off the intensity standing wave, so comparing
  π–π with σ–σ′ at matched power measures the fringe contribution the
  analysis otherwise only models. It stays off the precision path because it
  halves the signal, runs on the vector channel (a computable coupling
  change), and is B-sensitive.
- **One deliberate B block, a bound not a scan.** The line itself is
  m_F-blind (pure scalar operator, J = ½ has zero tensor polarizability) and
  nearly B-blind (Δg_J only, sub-kHz per Gauss). What can bite is the heater:
  its stray field tracks T, and with any circular impurity it opens vector
  satellites that mimic a T-dependent shift. Kill it with bifilar winding or
  bound it with a magnetometer, and measure dν/dB at one condition with a
  known applied field.

## 5. The intensity axis

The shift-versus-(P/w₀²) collapse across configs catches only relative waist
errors. A common scale error passes silently. The orthogonal absolute anchor
is the differential transit width: width(S) − width(L) in the same session is
~2.7 MHz of pure transit (σ_laser, collisions and natural width cancel in the
difference), and transit ∝ v̄/w₀ is thermal physics with no knife-edge
involved. Measured to ±5–7% it anchors the intensity axis to ~15%,
independent of the stage. Knife-edge, w(z) self-consistency, calipered
geometry and the transit difference must agree before any Stark coefficient
is quoted in physical units. The ramp-law form tests never need the absolute
axis. Only Δα does.

![transit width vs waist and collection geometry](../figures/fig3_transit_mc.png)

*The physics behind the anchor: the Monte-Carlo transit width against waist
and collection geometry. The S−L width difference reads ~2.7 MHz off the
steep part of this curve, which is what makes it an intensity calibration
independent of the knife-edge stage.*

## 6. The light-shift program

The triangular ramp predicts a parameter-free moment hierarchy: mean pull
−(2/3)S₀, variance/mean² = 1/8, standardized skew ≈ 0.566. The one-photon
case predicts zero skew, so the skew exists at all only because the signal
goes as I².

![the ramp construction](../figures/fig12_ramp_construction.png)

*The object under test: the intensity distribution of a focused Gaussian
beam, weighted by the I² two-photon rate, maps to the triangular shift
distribution f(s) ∝ |s| whose moments the session measures. Every item below
is a functional of this one construction.*

Test in order of statistical cost:

1. **Mean pull versus P** (config M/L). First order in S₀, the workhorse form
   test, alive only under the fixed lock.
2. **Excess variance versus P²** (config L/M).
3. **Skew hunt at S.** Not a promised result: sized for the pessimistic end
   (≥ 15× the 2025-equivalent trace count at one condition), which turns
   even the worst-case per-block significance into ≥ 3σ, detection or
   meaningful bound either way. The fringe-resolved tail suppresses the
   small-waist skew by ~26–28% (THEORY_NOTE §5), and the field-amplitude
   convention is pinned in `constants.py`.
4. **The geometry sign flip, the cleanest test in the program.** The
   z-average over the collection window has the closed form
   f(s) ∝ |s|^(n−1)·[ζₘ + ζₘ³/3] with ζₘ = min(Z_c/z_R, √(S₀/|s|−1))
   (`lineshape.stark_ramp_axial`). At config L the ramp stays clean
   (g₁ ≈ +0.56), and the archival M geometry carries only a few-percent
   correction (g1 +0.558). At config S the skew flips sign, with the
   crossover at Z_c/z_R ≈ 1.12. The flip condition is
   Z_c > 1.12 z_R ≈ 0.9 mm at S, while at L it would need Z_c > 12.7 mm,
   beyond any achievable field of view. With the cathode landscape
   (L∥ = 12 mm, the 2025 orientation) Z_c = 6/M mm, and the flip holds for
   every M < 6.6: secured by hardware, not tuning. Numbers from
   `run_ramp_geometry.py`:

   | orientation | M | Z_c | g₁ @ L (60 µm) | g₁ @ S (16 µm) | flip |
   |---|---|---|---|---|---|
   | landscape (12 mm) | 1.9 | 3.16 mm | +0.555 | **−0.421** | yes |
   | landscape (12 mm) | 2.8 | 2.14 mm | +0.563 | **−0.367** | yes |
   | portrait (3 mm) | 1.9 | 0.79 mm | +0.566 | +0.103 | no |
   | portrait (3 mm) | 2.8 | 0.54 mm | +0.566 | +0.367 | no |

   Portrait removes the test at every plausible M. Keep landscape.

**Collection rebuild: a two-lens relay.** Keep the f = 18 mm as L1 (it sets
the collection NA), add L2 (f₂ ≈ 35–50 mm, 2 inch) focusing onto the PMT,
the 795 nm bandpass in the collimated segment, and an adjustable slit at the
image plane. Then M = f₂/f₁ decouples field of view from collection, the
slit sets Z_c as hardware, and scanning the slit measures the collection
profile, an input the imaging formula cannot supply. The slit scan doubles
as a skew observable: at S alone, g₁ walks from +0.40 through zero
(Z_c ≈ 0.90 mm) to −0.42 on the slit, with atoms, power, lock and waist all
fixed. No instrumental asymmetry, blind to z_R, can mimic either flip.

   | slit → Z_c | g₁ @ L | g₁ @ S | signal @ S |
   |---|---|---|---|
   | 0.5 mm | +0.566 | **+0.402** | 35% |
   | 1.0 mm | +0.566 | −0.071 | 57% |
   | 2.0 mm | +0.564 | −0.354 | 76% |
   | 3.0 mm | +0.557 | −0.416 | 83% |

**One fit, pre-registered.** The four items are one fit, not four: per
condition, fit a single ramp amplitude S₀ and compare the pull, excess
variance and third cumulant as three analytic functionals of it
(`lineshape.ramp_moment_contributions`), with a χ² for their mutual
consistency. Pre-register which moment is primary at each (P, w₀): the
lowest-order moment above its own floor. Report the primary as the
measurement and the others as consistency checks. Choosing post hoc which
moment "worked" is rejected, as is hybridizing extraction methods for one
moment: one estimator per observable, the hierarchy across moments only.
One more rule, learned on the archive the hard way: any bounded amplitude
that can trade against the core is fitted from a spread of starting values,
and convergence is checked before an outlier is interpreted. A single zero
start once parked a wing amplitude at twenty times the true optimum's χ² and
read as physics for two days ([audit addendum 20](PREREGISTRATION_RESULTS.md)).
At S the sign is the robust observable (saturation bends the n = 2
magnitudes). The magnitudes belong to L/M.

## 7. The width and collision program

- **T grid at L only, twice, on different days, in opposite directions.**
  Cancels every drift component monotonic in time in the mean, and the
  difference measures the residual. Brackets (RF-off before/after plus an
  EOM ruler per block) catch jumps, with a pre-registered veto: a bracket
  tooth moving > 0.2 MHz within a block excludes the block. Jump-like drift
  does not average out. It gets cut.
  ![the archival width-vs-density floor](../figures/fig6_gamma_floor.png)

  *The archival floor this program upgrades: the fitted collisional width
  rises only ×1.47 while the density rises ×52.5, so the 2025 slope is a
  bound. The session's levers are the two the figure lacks: densities at
  150–170 °C, and block noise cut 4× by interleaving.*

- **At least five T blocks per peak.** The archival headline now runs on
  four points and two residual degrees of freedom, so its error
  multiplier is t(0.95,2) = 2.92 (the three-point construction it
  replaced paid ×6.31 on one). Five blocks give t(0.95,3) = 2.35, a
  further tightening before any drift compensation, and the cheapest
  statistical buy on the page.
- **150–170 °C in the same locked session, interleaved.** Still wanted, for a
  narrower reason than the 2025 post-mortem gave it. The archival lever test
  shows the joint β collapses 0.036 → 0.014 when the ×53 anchor (the 130 °C
  block) is folded in; earlier drafts of this plan read that collapse as
  "cross-session anchors cannot be combined." `rb5s6s/lever_crosscheck.py`'s
  own docstring already disagreed with that reading, and a 2026-08-02
  decision (Michelangelo, firsthand: the 130 °C power-sweep session ran in
  the SAME optical/cell configuration as the T-sweep, differing only by
  epoch and per-session calibration, which `load_t_rates` already handles)
  promoted the four-point fold-in to the archival headline
  (`scripts/run_beta_self.py`). The collapse is not a session artifact: it
  is the correct least-squares response to a line that barely moves across
  a 52.5× density span (gamma_coll rises only ×1.47–1.9), which is exactly
  what makes "residual floor, not resolved collisions" a demonstrated
  conclusion rather than an assumption. What a same-session 150–170 °C
  extension still buys, on top of the archival fold-in: it removes the
  cross-epoch calibration step entirely rather than relying on it being
  handled correctly after the fact (a within-session lever is cleaner than
  a cross-session one on general grounds, independent of this particular
  case), and it is the only route to densities where a genuine ~kHz
  collisional effect could clear the block-noise floor -- the archive's
  four-point bound (≲0.03–0.05 MHz per 10¹² cm⁻³) is still roughly an order
  of magnitude above the ~3.5 kHz expectation (§1, `docs/BIG_PICTURE.md`
  §1), so the case for the session is now about REACH, not about combining
  points at all.
  ![the EOM comb and its nonlinearity map](../figures/fig8_ruler.png)

  *The ruler as it worked in 2025: seven line replicas 6.25 MHz apart on the
  laser axis, and the empirical sweep-linearity map they stitch. The session
  keeps the comb and fixes its one hardware mismatch, below.*

- **The matched-PM ruler.** In 2025 the ruler light differed from the
  science light (the half-wave-plate carrier-suppression trick), so tooth
  widths could not serve as a drift compensator. The fix: drive the EOM at
  modulation index β ≈ 1.202, where the two-photon comb's central tooth
  nulls by pair interference (A_k ∝ J_k(2β)²) and the ruler runs at science
  polarization and power. Interleave rulers with science blocks rather than
  only bracketing: the sweep rate genuinely drifts within a session (the
  archive's before/after brackets disagree by up to ~1%, and a time-resolved
  rate model is now standard in the pipeline, `rate_model.py`). Monitor
  modulation purity live via the A₊ₖ = A₋ₖ symmetry, fit the comb to ±3
  orders (truncating at five biased the archival rate by 0.1%,
  [audit addendum 19](PREREGISTRATION_RESULTS.md)), calibrate any
  control-variate coefficient on dedicated dither data, and freeze all
  decision rules before first data. A correction may widen a bound. It may
  never, by itself, flip a bound into a measurement.
- **A returned-to block.** Re-measure one earlier condition later in the
  session. Every bound that averages block scatter assumes the scatter
  averages down. A systematic common to all peaks at a setting does not, and
  the 2025 design cannot tell the two apart (permutation p = 0.11). One
  block settles it. This is load-bearing for S₀, whose predicted effect is
  1.0 block scatters.
- **Four peaks interleaved within every block**, minutes apart, per-trace
  power logging. Cross-peak systematics drop from 30–50% to 2–4% and the
  amplitude discriminators (§8) become possible. Amplitude-ratio blocks get
  12–16 repeats (gain-limited), width blocks 8, P order randomized.
- **Per-scan timestamps in hardware metadata, not just the notebook.** The
  2025 exports carried no acquisition time, which is the single reason the
  σ_laser-sharing behind the hierarchical β is untestable (the recovered
  clock later showed the four peaks of a dwell sat 54–76 min apart). A
  wall-clock on every scan makes the sharing a tested fact, reconstructs the
  drift diary, and time-orders the interleaved blocks. On the Agilent of
  record, save the native `.h5` (its metadata carries the time) or take
  repeats as segmented acquisitions with per-segment trigger times. Set the
  scope clock at session start and note block starts independently. The
  LeCroy's per-trace TRIGGER_TIME is demonstrated on the 2025 rehearsal
  files, but its ~250× file weight buys nothing for a 60 ms feature: choose
  it only if the external time log fails in practice.
- **Etalon-lock thermal discipline.** The 2025 disturbance was not drift but
  dropouts inside the ~2 h etalon transient (re-kick amplitude 4.4 MHz,
  recapture τ = 97 [87, 118] min, validated out of sample). Engage the
  etalon lock ≥ 2 h before first data, budget the transient again after any
  ≥ 3 h pause, and once past it keep hands off the reference (at the held-lock rate
  a 43 MHz window lasts ~40 h). Log the lock state on a spare channel, and
  take one long off-resonance capture for the noise spectrum: the 2025
  chain carried a 61 Hz line at 0.2% of peak, harmless on a 60 ms line and
  not harmless on the narrower lines this session is for.
- **σ_laser at L**: transit removed by geometry, collisions bounded
  externally at tens of kHz by the literature scale. Quote it with that
  prior stated, or as a bound. Never as an assumption-free measurement.
- **The width/shift ratio, a fixed-lock-only check.** A drifting lock cannot
  measure a pressure *shift*: only widths survive the 2025 archive, so the
  session's centre channel is what would let this run. Lewis (1980, Table
  4.1) predicts $2\gamma/\beta = 2.75$ for a pure $n=6$ van der Waals
  potential, a second, independent test of the vdW anchor (M18) beyond the
  $T^{0.3}$ width-scaling check (§4.2 of the statistics chapter), and one the
  archive has no route to at all.

## 8. The amplitude program

Amplitudes were useless in 2025 for one measured reason: within-block
statistics of 1–3% under a between-block gain, power and polarization wander
of 30–50%. Every exploit below is a ratio, a within-block slope, or a
monitored quantity, so the wander cancels identically.

1. **The degeneracy-law test.** The S→S operator is pure scalar, so line
   areas are pure initial population: within one isotope the area ratios are
   parameter-free, 5/3 for ⁸⁷Rb and 7/5 for ⁸⁵Rb, and on interleaved lines
   the test runs at the 1–3% floor. The cross-isotope total-area ratio is
   the flat abundance ratio 2.59, constant in T, whose curvature onset flags
   PMT nonlinearity.
2. **The four-line common-slope Δα fit.** Δα is electronic and scalar, so
   all four lines share one Stark slope: a 4×-over-determined Δα with
   line-specific pulls isolated as residuals. Since area ∝ I², √area is a
   per-trace intensity proxy that soaks up alignment wander (valid at
   config L only: S is saturated, a pre-registered admissibility gate).
3. **An absorption channel for N(T).** A weak D-line probe plus photodiode:
   transmission is immune to PMT gain, and its log-slope versus 1/T returns
   the vapour-pressure curve. A cold spot flattens the high-T end, so the
   offset measures the cold-spot lag directly. The archive already prefers
   ΔT_cs ≈ 20 K at face value (0–30 K unexcluded), and at ×1.4–×7 leverage
   on the C1 bound the cold spot is plausibly a larger systematic than w₀.
   This is the single highest-value hardware addition of the session.
4. **Fluorescence over absorption.** Absorption sees true N, fluorescence
   the trapping-distorted emission. Their within-block ratio cancels N and
   isolates the trapping-modified collection efficiency, sharpest at
   150–170 °C. Real trapping is smooth in density. Drift is not.
5. **The 1.3 µm cascade channel.** The 6S decays via 5P (1324/1367 nm)
   before the detected D-line photons, and the 1.3 µm photon is resonant
   with nothing populated, so it escapes trapping-free. Detecting it (an
   InGaAs detector, broadband 1.32–1.37 µm) measures the degeneracy law
   without the trapping confound, and running 795 nm and 1.3 µm at the same
   condition turns any off-ratio into a verdict. The technique is proven on
   the sibling 5D lines (Hassanin 2023, Beard 2024). Only its use on this
   test is new.

Defensive set, all cheap: the forbidden-polarization extinction null (§4.4),
a pre-registered radiation-trapping sentinel fencing the high-T points, area
rather than peak height as the drift-robust observable, and a PMT-linearity
certificate spanning the full fluorescence range with a pre-registered
ceiling.

## 9. Session sizing

Sized to about eight days at the cell. An ordering, not a booking: run in
this order and a truncation at any point leaves the higher-priority
conversions done.

| day | content |
|---|---|
| D1 | First: characterise the wavemeter link (how tightly the laser holds a set point, and its calibration drift). It is this system's only outer loop, it needs no new hardware, and it decides whether shifts are measurable at all. Then telescope install; collection rebuild (relay + slit, landscape, §6); config L metrology (knife-edge, camera, calipers, ρ, polarization + tomography + extinction null). While the oven settles: the drift-characterization block that freezes the RF cadence (§10.5). |
| D2 | T grid day A at L, ascending, 4 peaks interleaved + mini-P excursion per dwell, sentinel ×3, 150/170 °C if the oven allows. |
| D3 | T grid day B at L, descending; sentinel ×3. |
| D4 | P grid at L (randomized, ~8 powers), morning. Reconfigure to S: knife-edge, camera, ρ, afternoon. |
| D5 | Skew deep-integration at S; the slit scan g₁(Z_c) at 4–5 settings (the sign-walk of §6); P grid at S. Overnight: cool for the cusp. |
| D6 | Cold-dim cusp session at S (Lehmann versus Voigt); the same data anchor the differential-transit intensity calibration (§5). |
| D7 | Config M spot check (knife-edge, camera, P grid, one 130 °C point); wavemeter GHz-linearity shots (§11). |
| D8 | Contingency: re-run whatever the bracket veto excluded. |

Deliverables: L T-grid → β_self and fixed-lock σ_laser. S skew session → S₀
and the skew attempt. L/M pull and variance → the ramp-law form test.
S−L width difference → the absolute intensity axis → Δα in physical units.
Interleaved blocks → the degeneracy-law and trapping tests. M spot → the
epoch bridge. Cusp session → the model-form closure.

## 10. Spending rules from the 2025 post-mortem

### 10.1 What actually bit (measured, not remembered)

| # | what bit | measured size | consequence | cure |
|---|---|---|---|---|
| 1 | between-block width scatter (drifting lock) | σ_B ≈ 0.12 MHz vs within-block SEM ≈ 0.05 | widths drift-limited; σ_laser a bound | fixed lock; brackets + veto (§7) |
| 2 | only 3 densities, 1 residual DOF | t(0.95,1) = 6.31 | β_self a bound | folding in the 130 °C point gives dof=2, t=2.92 (2026-08-02, headline); ≥5 T blocks tightens further (§7) |
| 3 | T monotonic in time | density slope collinear with drift | a guard had to carry the claim | opposite-order days (§7) |
| 4 | archival lever short at ×16.2 (three T points) | joint β collapses 0.036 → 0.014 once the ×52.5 (130 °C) anchor is folded in | was read as "high-T lever unusable"; now read as the fitted floor responding correctly to a near-flat gamma_coll(T) (`lever_crosscheck.py`) -- folded into the headline 2026-08-02 | same-session 150–170 °C (§7) still wanted, to reach densities where a ~kHz effect could clear the block-noise floor |
| 5 | no acquisition clock in the analysed exports | block order was the only time coordinate, and not even the acquisition order | σ_laser-sharing untestable; the recovered clock later dated the peaks 54–76 min apart | interleave the peaks in minutes + hardware timestamps (§7) |
| 6 | ruler light ≠ science light (HWP trick) | monitor reliability ≈ 0 | no drift compensator | matched-PM ruler at β ≈ 1.202 (§7) |
| 7 | w₀ never measured | tens-of-% prior | every absolute number conditional | beam profile first (§3, item 1) |
| 8 | ρ(T) never measured | ~8% S₀ drift from window filming | optics drift reads as physics | T_win before and after, per condition (§3, item 2) |
| 9 | P sweep at a single T | trapping immunity untested across density | discriminators data-starved | mini-P excursion per dwell (§10.4) |
| 10 | between-block amplitude wander | 30–50% | amplitude observables dead | polarization defined + tomography (§4.4); 12–16 reps (§7) |

Items 1–3 share one root cause: 2025 spent statistics against a
systematics-limited experiment. Within-block noise was already 2.4× below the
block scatter, and the campaign kept buying the cheap term.

### 10.2 The variance budget, and a stopping rule

Var(mean) = σ_w²/n + σ_B², and repetition divides only the first term. At the
archive numbers, doubling the repeats buys 4% for 100% more time. The same
hour on one more T block divides σ_B by √N and buys a residual degree of
freedom, and the t ladder is where the archive bled: 6.31, 2.92, 2.35, 2.13,
2.02 for one to five DOF. Freeze the stopping rule in the run notebook:
repeat a condition until σ_w/√n < σ_B/2, then stop (past that point infinite
repeats recover at most 12%). With 2025-like noise that is n ≈ 4–5.
Repetition is the right currency only where the observable is genuinely
photon- or gain-limited: the skew integration, the amplitude ratios, the
ruler-width monitor.

### 10.3 What ordering buys that repetition cannot

Within one sweep direction, drift monotonic in time is exactly collinear with
physics monotonic in T. That is a rank problem, and no number of repetitions
touches it. One ascending day plus one descending day cancels every
time-linear drift component in the mean and measures the residual in the
difference: a systematic error bar earned, not assumed. Full T randomization
would pay marginally more but costs thermal settling at every reversal. The
single reversal buys most of the protection free. Randomize the free knobs
instead (P order, peak order).

### 10.4 Loop structure

T is the only slow knob, so it is the outer loop, and each dwell extracts
everything cheap while the cell sits there: four peaks interleaved, a
randomized 2–3 point mini-P excursion (~10 min, which turns the single-T
power sweep of 2025 into width-versus-P at every temperature), matched-PM
ruler interleaves, and the window-transmission reading. Never the converse:
re-thermalizing per power point multiplies dead time for nothing.

### 10.5 RF cadence, measured not guessed

Strict on-off alternation halves science time for monitor information that
saturates within a few brackets. With the matched-PM ruler an RF-on trace is
no longer dead time, but tooth overlap still contaminates the moment
observables, so skew and centered moments come from RF-off traces only.
Spend the first ~30–45 min of D1, while the oven settles, alternating on/off
at one fixed condition. Compute the Allan deviation of tooth width and sweep
rate versus lag, set the bracket cadence where drift crosses the few-trace
SEM, and freeze it before the first science block.

### 10.6 The sentinel condition

Pick one condition (say 90 °C, 125 mW, peak 4192, config L) and re-measure it
at the start, middle and end of every day, identically. Three short blocks a
day buy a within-day drift series at fixed physics, the day-to-day
reproducibility number that §3 Tier 3 demands before days are averaged, and
the common level that ties the two opposite-order grids together. Every 2025
drift statement is an inference through the lineshape model because no
condition was ever revisited. The sentinel makes drift a direct observable.

### 10.7 The currency table

| currency | attacks | marginal value at archive numbers | verdict |
|---|---|---|---|
| beam profile + ρ + same-session high T | the systematic floor | converts bounds to absolute measurements | never cut |
| second day, opposite T order | time-monotone bias | removes what no averaging can; measures the residual | mandatory |
| more T blocks (to ~6) | DOF + σ_B averaging | ~2.7× from the t quantile alone | best statistical buy |
| interleaves (peaks, mini-P, rulers) | cross-condition systematics | 30–50% → 2–4% at near-zero cost | always on |
| more repeats, same condition | photon noise only | 4% for 2× time | only for skew, amplitudes, ruler monitor |
| strict RF alternation | monitor variance | saturates; halves science time | no; use the measured cadence (§10.5) |

Spend structure before statistics: orders before days, blocks before repeats,
interleaves before points, and one measured cadence instead of a guessed
alternation.

## 11. Wavemeter calibration shots

The accuracy hierarchy is atoms (kHz, Ayachitula 2024) ≫ EOM comb (RF-exact
6.25 MHz teeth) ≫ wavemeter (~10 MHz), so the data calibrate the instrument,
never the reverse, and absolute calibration is a free byproduct rather than
the critical path. The session's targets are shifts, which ignore the
absolute offset. Three shots:

1. **Absolute offset**: wavemeter reading against an identified peak, once
   per session (the wavemeter has its own drift, and the atoms are in every
   scan).
2. **GHz-baseline linearity**: readings at all four peaks against the known
   hyperfine intervals.
3. **MHz transfer check during the shift grids**: log the wavemeter
   continuously and compare its reported shifts to the comb, which wins.

The comb calibrates the scan axis, not the wavemeter, so the wavemeter's own
scale must come from shot 2.

## 12. Beyond 993 nm

The drive laser is a tunable Ti:Sapphire, so future sessions are not locked
to this line. The reachable Rb two-photon lines and the papers they enable
are worked out in [`FUTURE_TRANSITIONS_titsapph.md`](FUTURE_TRANSITIONS_titsapph.md).
The most distinctive candidate: the 778 nm clock line is the most actively
worked AC-Stark system, all of it active suppression, and the passive
asymmetry method plus the Ti:Sapph tunability could give a reference-free
magic-wavelength determination (the asymmetry sign-flip across Hamilton
2023's 776 nm magic wavelength).

## Appendix A. The archival analysis plan (executed)

The from-scratch analysis plan that produced the current results was
versioned here until 2026-08-02 and lives in git history. Its content is now
where a reader needs it: the module map and derivations in
[`methods.md`](methods.md), the data census, chronology and quarantine policy
in [`DATA.md`](DATA.md), the per-trace table in `data_raw/MANIFEST.csv`, the
verification battery in `tests/` (synthetic closure before real data,
end-to-end injected-truth recovery), and the results with provenance tags in
[`RESULTS.md`](RESULTS.md). Two of its ground rules bind every future
session too: the transition (sum) frequency axis everywhere, and nothing
numeric hard-coded outside `constants.py`/`config.py`.
