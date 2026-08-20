*Chapter 1 of 11 of [the plan](../PLAN.md)*

## 1. Aim

The 2025 record delivers a method and bounds: the drift-immune lineshape
framework, the self-calibrating EOM ruler, the identifiability and coverage
analyses, and the computed 5S–6S dynamic polarizabilities and magic
wavelengths ([`THEORY_NOTE.md`](../THEORY_NOTE.md) §5). That result stands on its
own and depends on no further data. A session is an upgrade, not a rescue. It
would convert three named bounds into measured coefficients:

1. **The AC-Stark coefficient Δα.** The strongest observable: under a fixed
   lock the pull (∝ S₀) comes alive, and a small waist raises S₀ several-fold.
   This is where raising the intensity pays off most.
2. **β_self and the collisional self-shift.** Intrinsically ~kHz per
   10¹² cm⁻³, so the deliverable is a modest first measurement or a much
   tighter bound, completing the 5D/7S self-broadening series
   ([BIG_PICTURE §1](../BIG_PICTURE.md)). Do not over-invest expecting headline
   precision.
3. **σ_laser of the new epoch**, with the transit term removed by geometry
   instead of assumed.

The smallest tranche that converts even one bound is the configuration-L width
program: the setup and metrology day plus the two opposite-order temperature
grid days (§9, D1–D3). D1 is that setup day in full, and it holds the fixed-lock
go/no-go, the ramp-monitor export, the wavemeter-link characterisation, the telescope and
collection rebuild, the configuration-L metrology afternoon, and the block that
freezes the RF cadence. D1 to D3 alone yields β_self, or a much tighter bound,
plus the fixed-lock σ_laser. A single same-direction day does not: the
bound-to-measurement guarantee needs the opposite-order pair (§7a). Value is
monotone in shots. A session truncated at any point still leaves the
higher-priority conversions done (§3), and if no session is ever run the
record stands unchanged.

## 2. The objections a referee would raise

**"Orson (2021) already published nulls on this line. Your bounds say 'we also
saw nothing', slower."** True as pure numbers: this record's bounds are
confirmatory of Orson's nulls, same direction, tighter. The increment is by
channel. The method (a closed-form two-photon ramp lineshape law plus a
reference-free moment readout) is not pursued elsewhere. The S₀ bound
(< 0.26 MHz, ~23× below Orson's ~6 MHz null) was extracted from shape alone
under a drifting lock. And a fixed-lock session would give the first measured
light shift on this line, plus the collisional self-shift: positive
observables, not sharper nulls.

**"The lock drifted MHz-scale all night in 2025. What stops a repeat?"** The
root cause is cavity-lock dropouts during the ~2 h etalon thermal transient,
with held-lock drift only ~0.02 MHz/min ([`APPARATUS.md`](../APPARATUS.md) §6).
The etalon discipline in §7h is the procedural fix, and what remains asserted
is that it would be followed. The session also degrades gracefully. The pull is
a differential measurement needing minutes of stability. The pre-registered
bracket veto (§7a) cuts drift-jump blocks instead of averaging them. The
sentinel condition (§10.6) monitors residual drift directly. Ayachitula (2024)
held a lock on this same transition to < 0.5 kHz over 50 min, an existence
proof from a high-finesse cavity apparatus rather than from this bench, and
the plan's own thresholds rest on the dataset's measured held-lock rate
rather than on that borrowed figure. Worst case, the D1 beam-profile and ρ
measurements retroactively sharpen the 2025 record and stand alone.

The strongest argument against the observable this plan ranks first sits in the
same apparatus record, and belongs here rather than only there. With the
re-lock steps and the per-interval ramps removed, the 2025-06-11 reconstruction
leaves a **settled floor of 0.62 +/- 0.03 MHz** of unmodelled laser motion, the
error a residual bootstrap over 400 replicates
(`results/wavemeter_reconstruction.csv`, [`APPARATUS.md`](../APPARATUS.md) §6).
That floor sits above both of this record's light-shift bounds carried to the
laser axis, 0.13 MHz from the joint fit and 0.32 MHz from the width-only
construction, so a single block's centre cannot beat what the averaged shape
bounds already deliver. Averaging reaches it only in numbers: about 24 blocks
to bring 0.62 MHz below the joint-fit pull and about 4 to bring it below the
width-only one, and only if the residual is independent from block to block.
The floor is what a fixed lock has to beat, and it is the number the go/no-go
of stage 0 should be read against, not the 0.19 MHz/min straight line the same
record was once read as.

![the drift problem, what was extracted, and what a fixed lock buys](../../figures/fig15_drift_story.png)

*The whole argument in one figure. Top: the drift problem as photographed on
a preliminary session, a wavemeter record read as a sawtooth of per-interval
levels and ramps with one shared 2.6 s rise at each re-lock, the laser holding
a reference that is itself still settling (no such log survives from the
campaign itself), with its twelve confirmed re-locks and the three candidates
the finder rejected. Middle: peak-position move against window-setting move
between consecutive power-sweep blocks, which is where the frame problem is
visible: 99.8 per cent of the between-block position variance is the window
setting, so line offsets are meaningful only within one scope-knob epoch. The
held-lock drift is bounded at order 0.02 MHz/min on the laser axis with the
sign undetermined, which is why shapes survive and centres do not. Bottom: the
three lock regimes, three decades apart. At the 2025 held lock the line shapes
stay usable and the coefficients are therefore upper bounds (S₀ < 0.26 MHz, β
between 0.03 and 0.05 MHz per 10¹² cm⁻³). In the cavity-lock class shown on this
transition in the literature, line centres become usable and those same
coefficients would turn into measurements. The oscilloscope window was moved 58 times over the campaign and each move
re-zeroes the offset axis, so only the widths and shapes of the individual traces
carry information. Each vertical stroke is that trace's own scan ramp drawn to
scale, which is a sweep extent and not an uncertainty. The inset is drawn for
scale rather than as a measurement, and because the sign is not established it
draws both directions. Bottom: what each drift regime licenses. The 2025 lock supported the
shape-only bounds reported here. A fixed lock of the class already
demonstrated on this transition would make the centre channel usable,
converting the bounds into the measured pull, the collisional self-shift, and a
3–12σ β_self.*

**"Drift does not stay out of the shape. It skews the line within a scan, and
skew is your observable."** Right in principle, answered by timescale. A scan
is ~1 s, and even the drift envelope is ~0.017 MHz/s, so within-scan drift is
~0.01 MHz against a ~5.25 MHz line (`results/power_sweep.csv`), and each block
carries its own EOM ruler. Drift acts between blocks, which is exactly why
β_self is a bound today. The closure test (inject a within-scan ramp, confirm
unbiased moments) is committed: `tests/test_intrascan_drift.py`.

**"A Δα bracket that wide discriminates nothing."** Partly answered by the
joint three-session bound: S₀(225 mW) < 0.26 MHz sits below the predicted
0.35 MHz at the adopted geometry (`results/stark_joint.csv`,
`results/stark_sweep.csv`), so the record constrains the (Δα, intensity)
pair. What it cannot do is split the pair: either the intensity or |Δα| sits
modestly below the adopted values, and the most conservative data subset
reaches the prediction itself and needs no headroom at all. A beam-profile
measurement decides which. The measured coefficient needs the session.

**"That bound is looser than you think."** Correct, and by a measured factor
rather than by argument. Two effects broaden the line with the ramp's own
square-of-power signature and are absent from the forward model behind both
bounds: atomic saturation, and hyperfine pumping through the real 5P cascade,
whose decay does not preserve F, so an atom that decays in flight can land in
the other ground state and leave the line
([fig23](../../figures/fig23_hyperfine_pumping.png),
[notes/two_photon_saturation_companion.md](../notes/two_photon_saturation_companion.md)).
Injecting the saturation term and re-profiling tightens the width-only bound by
2.8 and the joint one by 2.21, which would widen the tension above rather than
relieve it. Neither number moves in the record, because the injected law is the
two-level homogeneous form used with a two-photon Rabi frequency, which is
standard practice and not a derivation for this level structure. For this plan
the consequence is a session requirement rather than a caveat, and it points at
the same item this plan already ranks first. The three terms are degenerate in
every knob the width channel has: all three grow as the square of the power,
and all three grow as the inverse fourth power of the waist, the ramp because
its increment goes as the square of a shift that goes as the inverse square,
and the companions because the saturation parameter carries the two-photon Rabi
frequency squared. So neither a power sweep nor a change of focus separates
them. Two things do. The centroid pull, on which the companions do not act at
all because they broaden the line without moving it, and that needs the fixed
lock. And the LINE INDEX, found 2026-08-10: the ramp and the saturation are
identical on all four lines while the pumping is not, since its branching runs
0.223 to 0.372 across the four (a two-step cascade product, not a degeneracy
weight, because the scalar two-photon operator leaves 6S in one hyperfine
level). That is a lever of 1.67 on the pumping term, 3.1 kHz of width at the
committed $S_0$ bound and 7.8 kHz at the predicted one, against an
88 kHz single-block scatter, so it is real and this record cannot spend it. A session that controls the block scatter gets a second
separation without needing a lock.
Until then the width channel yields a bound with a known direction of error,
which is what it is quoted as.

**"Your own recompute flips the sign of Δα against the published computation.
Bug?"** Not a bug. The recompute is validated on anchors it does not fit (the
measured 5S tune-out to ~2 pm, the static polarizabilities) and agrees with
Orson's magnitude within 5%. The sign disagreement has an identified mechanism,
every result in this record is sign-immune (bounds and the asymmetry null use |Δα|),
and the item is flagged for external theory adjudication
([`THEORY_NOTE.md`](../THEORY_NOTE.md) §5). It blocks nothing.

**"Put a student on this and it strands them with un-analysed shots."** The
handover is a project commitment and belongs in a direct conversation. What the
document can put against that objection: the pipeline is built to a handover
standard with a documented ingest path, it ingests session data unchanged, and the
smallest tranche has a defined standalone deliverable, so a truncated session
yields a finished result rather than orphaned data. An adaptation guide
([`ADAPTING.md`](../ADAPTING.md)) names the seams for other lines and species.

**"The numbers keep moving. How do I know they are frozen?"** Every headline is
generated from the committed CSVs, a registry test forces every quoted copy to
match its source, and releases are tagged. The audit report logs every revision
with its cause ([`PREREGISTRATION_RESULTS.md`](../PREREGISTRATION_RESULTS.md)).

---

*[the plan](../PLAN.md) · [Priorities if the budget shrinks](02_priorities.md)*
