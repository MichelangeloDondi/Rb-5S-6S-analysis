# The beam and the apparatus

*[History](../HISTORY.md) · the waist, the geometry and what the instrument was doing*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

## The 60 µm working waist, retired 2026-08-15

| quantity | was | now | live value in |
|---|---|---|---|
| working waist, configuration L | 60 µm | 64 µm | [Rajasree 2020](../lit/rajasree2020thesis.md), [Nieddu 2019](../lit/nieddu2019.md) |
| two-waist intensity ratio | ×14 | ×16 | recomputed at 64 µm |
| g₁ sign-flip table, L column, Rayleigh range | z_R = 11 mm | z_R = 13 mm | recomputed at 64 µm |

The 60 µm figure was a stand-in written before the waist was measured, with no telescope ever specified to produce it. The ratio and the sign-flip table are recomputed at the measured 64 µm beam.

## The 2026-08-15 band and design corrections

Nine numbers drafted in the private record on 2026-08-15 were corrected the same day, before any reached a committed result.

| quantity | was | now | cause |
|---|---|---|---|
| band-holdout replication | 7 of 7 conditions low, p = 0.0078 | 11 of 14 fresh conditions, p = 0.029 | two of the seven were pilot traces regrouped by peak, and no soundness threshold was in the frozen script |
| infinite-window collisional width, γ(∞) | 0.246 MHz | retracted, no replacement value | the frozen spec required a form spread. 1/w² gives 0.446 MHz against an exponential 0.504 MHz on peak 4154 |
| wide-scan span | 800 MHz, ±400 | 2400 MHz, ±1200 (at 3σ reach) | the free per-trace background degeneracy leaves 0.140 retained SNR at 1σ reach, not the assumed 0.7 |
| wide-scan record length | 3000 points | 10000 points | followed the span change |
| pedestal detectability | ~29σ per trace | ~31σ per trace, 13σ at worst τ | the degeneracy factor is 0.645 at the new reach, and the τ_int median is 3.81 |
| residual-Doppler retro tilt | 1.6 mrad | 3.2 to 3.5 mrad | the pedestal already carries k_eff = 2k. The correct coefficient is 471 MHz/rad, not 942 |
| in-campaign wavemeter records | one | two (and the section count by ten) | a second record, 2025-07-18 02:37, was already in the register |
| wide-scan shape requirement | 20 points across the line FWHM | 90 points (the 40000-point record in PLAN section 10a) | the B5/B6 runs measured width recovery at the committed noise law. About 22 points fails the frozen criterion |
| pedestal detectability, 10000-point record | ~31σ per trace | ~61σ per trace, 27σ at worst τ | the record length rose with the shape requirement above |

Protocol §6 now requires a refutation tally to record its direction alongside its count.

## The cascade line table, 2026-08-19

`rb5s6s/cascade.py`'s `DRIVEN_F` table assigned 993.4154 nm and 993.4207 nm to the wrong isotope and 993.4192 nm to the wrong hyperfine level. The branching fractions are keyed by wavelength from the committed manifold output and never moved. `DRIVEN_F` now matches `constants.PEAKS`, the repository's independent line table. The module's own test had asserted the table back at itself. It now asserts against `constants.PEAKS`. Nothing was pushed while the wrong table stood.

## The modulation depth menu, 2026-08-19

Plan chapter 7's modulation menu claimed teeth are never free statistics, from comparing an RF-on sweep against an RF-off sweep for the same slot. The budget's real alternative is different. Ruler brackets are mandatory calibration that the M25 joint fit already ingests, with a no-rulers arm as its robustness check, and against that alternative tooth width information is free and additive, a factor 1.26 to 1.33 per block at 2025-like proportions, propagating linearly to the collisional coefficient. Plan chapter 7 now splits the depth by the trace's job, deep brackets since ruler information climbs with depth, shallow interleaves since width information falls with it. The wrong frame lived in one local commit for under an hour.

## The comb tooth-weight model, 2026-08-19

Every tooth weight in this record was $J_s(2\beta)^2$, the zero-delay limit of the interference between sideband pairs that reach the same offset through the retro mirror's round trip. The general form is $2\beta\cos(\pi f\tau)$, cell-averaged. At the 2025 campaign's 12.5 MHz drive the delay phase is 0.05 rad and usable teeth correct by at most 0.2 per cent, so no committed ruler number moves. Two plan design figures computed under the old limit did change:

| Design figure | Old value | New value |
|---|---|---|
| Sub-GHz coincidence tooth weight | 0.16 | 0.003 (50x lower) |
| Cascade main-line survival at 579.6 MHz | 0.076 | 0.62 |

The cascade correction inverts its operating mode, from calibration sweeps only to safe for science sweeps. `rb5s6s.forecast.comb_tooth_weights` now computes all three cases.

## Sub-GHz EOM drive justification, 2026-08-19

Plan chapter 8 justified a sub-GHz EOM drive by a tooth-to-pair coincidence that removes a 185-tooth-spacing extrapolation between an isotope pair's two lines. That extrapolation belongs to the retired narrow-span geometry. The wide-span design proposed in the same section had already removed it without added hardware. The section went through two more versions the same day:

| Version | Basis | Problem |
|---|---|---|
| First replacement | about 192 tooth positions span the pair gap | counts positions, not teeth that carry a resonance |
| Second replacement (current) | usable comb is four clusters of about five teeth, gaps to 1155 MHz uncovered | none |

The section's current justification no longer depends on the coincidence-vs-extrapolation argument. Reading the doublet at its measured per-crossing precision reaches 0.3 kHz in about 100 crossings against constants known to 2 kHz, folded with the drive recommendation into one hardware conclusion since one modulator serves both.

## The pair-route magnetic-channel rate, 2026-08-20

The wiki closed the magnetic channel with a single-atom rule ($J=1/2$, no reduced matrix element between two sublevels of a rank-two operator), without saying it applies to one atom only. A pair of ground-state atoms has four sublevel products, so the closure lifts, and a nonzero rate remains, set by the pair's dipole-dipole transfer amplitude. That replacement first summed only the $5P_{1/2}$ intermediate leg. Adding the E1-allowed $5P_{3/2}$ leg, which carries the larger reduced elements, multiplies the amplitude by 2.82 and the rate by 7.97, moving the published rate from $1.5\times10^{-10}$ to $1.3\times10^{-9}$, about eight times the single-atom hyperfine route.

## The two-atom channel's headroom margin, 2026-08-20

The two-atom module quoted the channel's margin below the record's resolving power as "ten orders" in one paragraph and "nine orders" in another. Neither figure had a producer, and no constant in the tree defined what the record can resolve. Measured against the tightest bound the record carries on an out-of-window feature, `f_wing_red_mean` at 0.0009 of peak in `wing_check.csv`, the margin is six orders.

## The 1.9 ms autocorrelation's mechanism, 2026-08-23

`APPARATUS.md` attributed the committed 1.9 ms autocorrelation to the oscilloscope's High Resolution mode, described as averaging and correlating adjacent samples. That explanation is withdrawn. On the InfiniiVision, High Resolution boxcar-averages samples inside each stored point's own disjoint interval and does not correlate one stored point to the next. The LeCroy's ERes, a digital filter spanning several output points, is the mechanism that does. The committed data span 11.86 bits, 0.14 under a documented twelve-bit ceiling, consistent with the disjoint boxcar. The 1.9 ms correlation is now unexplained in `APPARATUS.md`. The leading candidate is the decimation stage between acquisition memory and the 2000 stored points.

## The acquisition-mode ceiling, 2026-08-24

The prior entry inferred a twelve-bit ceiling on the InfiniiVision's High Resolution mode from arithmetic. Both instrument manuals confirm it directly.

| sweep speed | bits (InfiniiVision manual) |
|---|---|
| ≤ 1 microsecond/division | 8 |
| ≥ 20 microseconds/division | 12 (ceiling) |

The campaign ran at 100 ms per division, so the mode delivered exactly twelve bits, matching the measured 11.86. The manual states the mechanism as averaging samples within one acquisition into one stored point, a boxcar over disjoint blocks. A second manual states the same taxonomy. High Resolution and Peak Detect are decimation methods, Average and Envelope are arithmetic methods built from several acquisitions. The 1.9 ms correlation remains unexplained. The leading candidate is unchanged, the decimation stage between acquisition memory and the 2000 stored points.

## The bit-depth argument, withdrawn 2026-08-24

The data-collection chapter claimed every open noise question lives under
the oscilloscope's quantisation step, the stated justification for
two-window acquisition. Measured across all 35 quality-passed conditions
(`results/quantisation.csv`): the analogue baseline noise is 5.2 to 246
times the quantisation step, median 37, so the quantiser contributes at
most 0.155 per cent of the noise, and even an eight-bit hypothetical gives
1.3 steps of dither. The claim is withdrawn, and two-window acquisition now
survives only as clipping headroom or a second simultaneous chain. What
binds instead, light-linked background and cathode shot noise, is
diagnosed on the noise-law wiki page, with the pooling and
acquisition-design pages carrying what follows from it.
