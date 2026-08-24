# The van der Waals anchor: which C₆ enters, and one open inelastic channel

Status: adjudicated 2026-08-05. Both items were parked in
[the pooling pre-registration](beta_self_pooling_prereg.md) under "Adjacent
findings recorded for separate adjudication, not acted on here". This note
closes the first and opens the second properly.

`provenance: rb5s6s/vanderwaals.py::beta_self_anchored` - **this page was declared NO_PRODUCER and that was wrong.** Its load-bearing numbers are reproduced right now by that committed pure function, which takes no CSV and no raw trace: calling it returns `c6_ratio = 0.34733905` and `dc6_ratio = 0.31282691`, the table's 0.3473 and 0.3128 exactly. **The declaration was false because the guard's vocabulary had no kind for a committed function**, so the only available option was the merely pessimistic one. That error overstates the gap, which is why it would have survived: a number making the record look worse than it is attracts no scrutiny. Recorded in `docs/HISTORY.md`.


## 1. The question

A referee argued on 2026-08-04 that the anchor ratio in `rb5s6s/vanderwaals.py`
should use the difference of van der Waals coefficients,

    DC6(5S+nS) = C6(5S+nS) - C6(5S+5S)

rather than the pair coefficient C₆(5S+nS) alone, on the ground that the impact
phase is set by the difference between the upper- and lower-state interactions
with a ground-state perturber. Their numbers: the scale factor moves from 0.6551
to 0.6282 and the 6S anchor from 3.53 to 3.38 kHz per 10¹² cm⁻³, a 4.1 per cent
shift and inside the quoted ±0.30.

## 2. The referee is right

The module's own primary source settles it. Lewis, *Phys. Rep.* **58**, 1 (1980)
([note](../lit/lewis1980.md), held and read in full) says the same thing three
times, at three levels of the derivation.

**Eq. (2.39), the impact width and shift.** Lewis writes the complex damping
parameter as a product over the upper and lower state S-matrices,

    w + i*d = < 1 - S_ii * S_ff* >

averaged over impact parameters, velocities and orientations. For a central
potential each S-matrix is a pure phase, so the product is
exp{-(i/ħ) ∫ [V_i(R(t)) - V_f(R(t))] dt}. The lower level is in the expression
from the start. Only the difference of the two interactions survives.

**Eq. (4.13), the phase-shift cross-section this module specializes.** The real
and imaginary cross-sections are integrals of [1 - cos(Φ_i - Φ_f)] and
sin(Φ_i - Φ_f) over impact parameter. Not of a single-level phase.

**Section 4.2, in words.** Discussing the shift cross-section under the Anderson
cut-off, Lewis states that its sign depends on the overall sign of the potential
difference, which he names verbatim as "the difference in the interactions for
the two levels involved". Eq. (4.15) then defines the phase from a power-law
interaction V = C_n/R^n, and by the two lines above that V is the difference
potential and C_n the difference constant.

So the C₆ that belongs in eq. (4.17), and therefore in `beta_self_vdw`, is
ΔC₆. Passing the upper pair's coefficient alone is the correct limit only when
the lower state is a spectator. That is the usual excited-to-ground case in the
broadening literature, where the ground-state term is small enough to ignore,
and it is why the shorthand is common. It is not this case: the radiator's lower
level is a ground-state Rb atom facing a ground-state Rb perturber, and
C₆(5S+5S) = 4180 a.u. is 14 per cent of C₆(5S+6S) and 5 per cent of C₆(5S+7S).

**And it does not cancel in the ratio.** The anchoring construction exists
because the Lindholm-Foley prefactor, the mean-speed step and the dropped core
and tail are common to the 6S and 7S rungs and divide out. The ground-pair term
is not that kind of error. It is the same number subtracted from a smaller
numerator and a larger denominator, so it moves the ratio by construction. That
is the whole content of the correction.

## 3. What changed

All values from `rb5s6s.vanderwaals`, at 403.15 K and 10¹² cm⁻³.

| quantity | before | after |
|---|---|---|
| coefficient ratio, 6S over 7S | 0.3473 (pair) | 0.3128 (difference) |
| scale factor, ratio to the power 2/5 | 0.6551 | 0.6282 |
| β_self(6S) anchored on Zameroski | 3.53 ± 0.30 kHz | 3.38 ± 0.29 kHz |
| β_self(7S) predicted absolutely | 4.50 kHz | 4.40 kHz |
| that prediction against the measured 5.39 | 17 per cent low | 18 per cent low |

Inputs: C₆(5S+5S) = 4180, C₆(5S+6S) = 28908, C₆(5S+7S) = 83228 a.u., so
ΔC₆(6S) = 24728 and ΔC₆(7S) = 79048 a.u.

Two consequences worth stating rather than leaving to be rediscovered.

The absolute closure gets marginally worse, not better. The 7S prediction was
17 per cent below Zameroski's measured rate and is now 18 per cent below,
because subtracting the ground pair lowers the predicted width at fixed
prefactor. The correction was not accepted because it improved agreement. It is
accepted because it is the formula the source derives.

The ground-pair term is taken from this module's own Casimir-Polder integral,
4180 a.u., and not from the 4691 a.u. literature Rb₂ value, so that both rungs
are built from the same truncated sum and the valence-only truncation partly
cancels. Substituting 4691 gives 3.36 instead of 3.38, half a per cent, far
inside the envelope. The choice does not matter at this precision and is
recorded so that it is not re-litigated.

## 4. What is still open, and it is larger than what was just fixed

The pooling pre-registration records a referee estimate that the R⁻⁶ *exchange*
contribution to the 5S+nS interaction is about 0.7 of the direct term through
the dominant intermediate channel. This module computes the direct Casimir-Polder
term only. That is a much larger omission than the 4 per cent just corrected,
and unlike the prefactor it is not obviously common to the 6S and 7S rungs, so
it could move the ratio rather than only the scale. Nothing here should be read
as a claim that the anchor is now good to 4 per cent. The module's own standing
statement holds: every number in it is an envelope at the 10 to 15 per cent
level, and the 18 per cent absolute miss against the one measured nS rate is the
size of what is not modelled.

What would close it is a proper treatment of the exchange term for the S+S
asymptote, or the ratio measurement itself. Measuring β_self on both 6S and 7S
on one bench turns the ratio from an input into an observable, which is the case
[FUTURE_TRANSITIONS](../FUTURE_TRANSITIONS_titsapph.md) §3.2 already makes.

## 5. Sites still carrying the pre-correction anchor

The correction landed in `rb5s6s/vanderwaals.py`, in `tests/test_vanderwaals.py`,
and in the three documents this pass was scoped to touch:
[CLAIMS](../CLAIMS.md), [LITERATURE](../LITERATURE.md) §2 and
[FUTURE_TRANSITIONS](../FUTURE_TRANSITIONS_titsapph.md) §3.2 and §3.3.

Two things are knowingly left behind. `results/projections.csv` is produced by
`scripts/run_projections.py` from `beta_self_anchored`, so it carries 3.52809
and the four detection-significance rows derived from it until the pending
recompute regenerates them, which lowers those by 4 per cent. And the
bound-over-anchor headline was 8.2 to 14.0 times, quoted as 8 to 14, and is now
8.5 to 14.6, which rounds to 8 to 15. Both belong in one sweep rather than file
by file, so that no two documents disagree on a headline number in the interval.

## 6. The 6S to 4D interval is an open inelastic channel

Recorded as a candidate mechanism, not as a claim. Nothing measured here needs
it, and nothing in the pipeline depends on it.

**The interval.** Rb 4D sits 777 cm⁻¹ below 6S (4D at 19355 cm⁻¹ against 6S at
20133 cm⁻¹, with the two fine-structure components separated by less than half
a wavenumber, so they are one channel for this purpose). That is
the 12.9 µm interval [THEORY_NOTE](../THEORY_NOTE.md) §5.1 already names when
it rules out a near-degenerate multipole resonance on the drive.

**Why it is a channel at all.** 6S to 4D is S to D, so it is closed to electric
dipole radiation and does not appear in the 6S radiative lifetime. It is open
to a collision, which carries no such selection rule, and the transfer
6S + 5S → 4D + 5S releases the 777 cm⁻¹ into relative motion rather than
requiring it, so there is no Boltzmann barrier in the direction that would
matter.

**The scale of the defect.** At 400 K, kT is 278 cm⁻¹, so the defect is 2.8 kT.
That is large enough that the collision is not near-resonant and the adiabaticity
argument runs against the channel: at a mean relative speed near 440 m/s and an
interaction range of order a nanometre the Massey parameter is in the hundreds,
which would suppress the transfer heavily if the coupling acted only at long
range. It is not large enough to dismiss the channel outright, because alkali
excitation transfer at comparable defects proceeds through short-range curve
crossings where that estimate does not apply, and the Rb 5P fine-structure
splitting of 238 cm⁻¹ is the familiar case of a defect of the same order that
mixes readily. The interval alone neither opens nor closes the channel.

**What it would look like if it were there.** Three signatures, all of them
already reachable with instruments this programme has or plans.

1. *It adds to the width and not to the shift.* An inelastic channel destroys
   the upper state, so it contributes to the real part of the damping and
   contributes nothing to the shift at leading order. Lewis Table 4.1 gives the
   potential-independent n = 6 elastic prediction 2γ/β = 2.75. A measured pair
   of coefficients lying above that ratio would be the cleanest evidence for an
   inelastic contribution, and the collisional self-shift is already on the
   list of things a fixed-lock campaign would measure from the same centre
   channel.
2. *It is isotope-blind.* The 5S to 6S isotope shift is 99 MHz against a defect
   of 777 cm⁻¹, which is 23 THz, five orders larger. The channel therefore
   cannot distinguish an ⁸⁵Rb
   radiator from an ⁸⁷Rb one. It therefore cannot break the shared-slope
   licence that the pooling pre-registration rests on, and it would not show up
   in the per-isotope consistency check.
3. *It sits above the elastic anchor, never below.* Any inelastic rate adds to
   the elastic van der Waals rate. So if a measured β_self(6S) came in above the
   3.38 kHz per 10¹² cm⁻³ elastic anchor by more than the anchor's own envelope,
   this channel would be the first candidate to examine, and the width-to-shift
   ratio of item 1 would be the way to examine it. A measurement at or below the
   anchor would say nothing about it either way.

**What would settle it.** A literature search for measured Rb 6S quenching or
excitation-transfer cross-sections against ground-state Rb, which this
repository has not yet run, and which the negative-search record in
[LITERATURE](../LITERATURE.md) §5.2 would be the place to record. Failing that,
a coupled-channel estimate of the 6S and 4D molecular curves at the crossing
would say whether the short-range coupling exists. Neither is a pipeline change
and neither is scheduled.
