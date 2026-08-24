*Chapter 5 of 8 · [methods index](../methods.md)*

**The question.** How does a record of volts against time become a frequency
axis, and how well is that axis known?
**Takes.** The measurement chapter, for the sweep and the apparatus. It needs
none of the lineshape chapters, which is why it can be read early.
**Gives.** The tooth spacing and the sweep rate that turn every millisecond in
the dataset into megahertz. Every width quoted anywhere in this set is
denominated in this axis.
**Skip if.** You are reading for the physics of the line rather than for the
calibration. Nothing later re-derives the axis, it only spends it.

## 3. From volts-versus-time to a frequency axis (the EOM ruler)

An EOM phase-modulates the light, its sidebands pair up in the two-photon
absorption, and the result is a comb of line copies spaced by half the
modulation frequency. [EOM sidebands](../wiki/eom-sidebands.md) carries that
derivation. Here $\Omega = 12.5$ MHz gives

$$\boxed{ \Delta\nu_\text{tooth}=\frac{\Omega}{2}=6.25\ \text{MHz (laser axis)} }$$

with the same factor-2 as [§0](../methods.md). Fitting the tooth spacing (in ms) per block gives
the sweep rate. We measure $0.042524(51)$ MHz/ms on the laser axis, and the
sweep is linear across the window to better than 0.3%.

This spacing's exactness, assumed above to calibrate the sweep rate, is now
a derived property rather than a design assumption: a velocity-symmetry
argument shows every tooth centroid is exactly symmetric in atomic velocity,
because the retro beam carries the same sideband spectrum as the forward
beam by construction. The worst-case differential pull from sideband
interference is 1 to 6 parts in $10^6$ of the 6.25 MHz spacing, with the
full derivation in the audit trail
([PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md), addendum 22).

A half-wave-plate trick mixes in
amplitude modulation on the ruler traces to suppress the carrier so the
sidebands stand tall. The tooth *spacing* is exact and is read from the tooth
positions alone. The tooth *heights* are read for two other things, which
tooth is which and how deep the drive is, and never for the spacing. Because
the amplitude admixture is real, the pure-phase-modulation height law below
is an approximation rather than a law here: the second-to-first height ratio
still gives the modulation depth to a few per cent, while the carrier height
carries the admixture and settles nothing
([pre-registration](../notes/ruler_validity_and_trim_prereg.md), section A2
and amendment 6). *Code:* `ruler.py` (M2), with
$\Omega/2$ locked by a permanent test in `test_constants.py`.

**How many teeth the fit must include, and what it cost to get wrong
(2026-08-01).** The comb runs to $\pm3$ orders. Until this date the fit
modelled only $\pm2$, and truncation is not a harmless economy here: the
unmodelled sixth and seventh teeth sit just outside the fitted set, their
tails leak into the window, and the only way a five-tooth model can absorb
them is to push its outermost teeth outward. That makes $\Delta$ too small
and the rate too high. Refitting the same 24 ruler traces both ways gives
$\Delta=146.804$ ms at five teeth against $146.970$ ms at seven, and the
five-tooth value reproduces the previously committed rate exactly, which is
what identifies the truncation as the cause. The corrected campaign rate is
therefore **0.4% of a linewidth lower**, $0.0425706 \to 0.0425243$ MHz/ms,
a $-0.109$% shift carried by every frequency this analysis quotes. The size
is about one standard error of the rate itself and is small beside the beam
waist, but it is a one-directional bias rather than scatter, so it is
corrected rather than absorbed into an error bar. The same truncation was
railing the collisional width at zero in the M25 comb fits, which is how it
surfaced.

### Why the ruler is a clean number: the common-mode rejections

The rate is a *differential* measurement across five copies of the **same
physical line**, and everything that afflicts the line afflicts every copy
equally:

- **The AC-Stark shift.** The atom sees the *total* field, carrier plus all
  sidebands and both beams, at every instant, regardless of which tooth is
  resonant, so the light shift translates the whole comb **rigidly** and the
  spacing is untouched. The residual is second-order: a power drift *within*
  one trace shifts teeth differentially by $S_0\times$(fractional drift per
  spacing), which is $\lesssim10^{-4}$ at the 2025 $S_0\lesssim0.6$ MHz and
  below the quoted precision.
- **The line asymmetry** (the ramp skew of [§2.6](03_the_ac_stark_ramp.md),
  or any other shape distortion). Same line, same intensity, same shape on
  every tooth ⇒ the same centre pull on every tooth ⇒ absorbed into the comb
  phase $t_0$, never into the spacing. The genuine second-order effect is that
  **edge teeth have only one neighbour**, so overlapping *asymmetric* wings
  pull the comb ends differently, and that is why the fit is a *constrained
  simultaneous* comb (one shared tooth shape and free heights, where at about
  147 ms spacing and about 60 ms width a strong tooth's wing under a weak
  neighbour is about 20% of the weak peak, and single-tooth fits pull centres by
  O(ms)), and why the free-centres nonlinearity map exists: it bounds *any*
  tooth-dependent pull, scan nonlinearity and differential shape effects
  together, **empirically at $\lesssim0.3$% per position**
  (`results/ruler_nlmap.csv`), already inside the quoted error through the
  PDG block-scatter inflation.
- **Sideband amplitude imbalance** (residual am from the carrier-suppression
  trick): absorbed by the free per-tooth heights, so amplitude never enters the
  spacing.
- **Laser drift during a trace** is not a bias but part of the *measured*
  effective rate, and the line fits use their own block's rate, so the drift is
  self-consistently calibrated out by a per-block
  ruler under a drifting lock.

![a ruler trace and the sweep-linearity map](../../figures/fig8_ruler.png)

*A representative ruler trace with its seven-tooth comb fit over its
standardized residual strip (left) and the pooled sweep-linearity map
(right): the local rate never departs from the block rate by more than 0.25%
in any well-sampled window, and that bound is set by the well-sampled windows
alone. The strip beneath the map carries the number of traces each window
draws on, so the split is visible rather than asserted.

**The two leading-edge windows are not merely imprecise, they depart.** At
-537 ms the local rate sits 1.75% below the whole-scan rate with an
uncertainty of 0.40%, and at -412 ms it sits 0.73% above with an uncertainty
of 0.18%, which are 4.4 and 4.0 standard deviations from flat. They are
excluded from the bound on sample count, four and five traces against nineteen
or more elsewhere, and an earlier version of this caption and of the figure
justified that exclusion by saying such windows carry uncertainties larger
than the bound. Of the five excluded windows two do (0.40% and 0.68%) and
three do not (0.18%, 0.18% and 0.29%), so the justification was true of two of
them and the leading edge needs a different statement: **the scan's
first samples are where the ramp is turning, the conversion from scan time to
frequency is not linear there, and the analysis windows do not reach into
it.** The figure marks those two windows in red and names the worst of them on
the canvas. What the right panel bounds is
sweep non-linearity and any tooth-dependent pull together. Six of the seven teeth
stand above this trace's fit residual, and the seventh does not because the
third-order pair carries about 2% of the first-order power at this modulation
depth, and the scan end clips the outermost window, as on every recorded ruler
(pre-registration
[amendment 4](../notes/ruler_validity_and_trim_prereg.md)). This trace is the one
drawn because it meets the conditions fixed before the analysis, §7 of the same
note, every clause required: the two first-order teeth are among the three
tallest without relabelling, six of the seven teeth stand above the scatter of
the fit residual with the weakest at 0.63 of it and none railed on its zero
bound, the ladder took no re-index action, the trace is not excluded, and the
reduced χ² is 1.01 against a ceiling of 2.0. Seven of the 104 recorded rulers
clear all of it. The residual strip carries the standardized units of the
statistics chapter's §4.1, and the climb at the scan end is the clipped window
showing itself in the evidence.*

### The comb amplitudes, and the pure-phase-modulation null

For *pure* phase modulation the two-photon tooth amplitudes follow the exact
closed law $A_k \propto J_k(2\beta)^2$, derived from Neumann's addition
theorem in [EOM sidebands](../wiki/eom-sidebands.md) and resting on the
[Bessel functions](../wiki/bessel-functions.md) that carry it. That law
explains the 2025 design compromise and prescribes its fix:

- **At small $\beta$ the sidebands are buried**: $J_k(2\beta)^2$ gives
  $1 : 0.10 : 0.002$ at $\beta=0.3$, so the outer teeth drown in the central
  tooth's tails. The 2025 workaround rotated a half-wave plate to admix
  amplitude modulation and suppress the optical carrier. It worked, but it
  put the ruler light at a **different polarization and power than the science
  light**, which is the reason the ruler traces cannot serve as a
  hardware-matched width monitor for the dataset (PLAN §7).
- **The fix needs no polarizer**: drive the EOM at
  $\beta \approx 1.202$ (where $J_0(2\beta)=0$) and the central tooth **nulls
  by coherent pair interference**, the two-photon analogue of carrier
  suppression, leaving a comb $0 : 1.00 : 0.69 : 0.15$ ($k=0,\pm1,\pm2,\pm3$)
  with the ruler light *identical* to the science light.
- **The pattern is a built-in modulation diagnostic.** Pure phase modulation
  demands $A_{+k}=A_{-k}$ exactly, and the 2025 traces violate it, for example
  $1.00$ against $0.90$ at $k=\pm1$ on a T-session ruler. The carrier is where
  the admixture concentrates: across the clean combs its height runs from
  $0.360$ to $1.188$ of the first order and on ten of the 41 it stands *taller*
  than the first order, while the second-to-first ratio holds to four per cent.
  That contrast localises the residual amplitude modulation to the carrier and
  is why the carrier height settles nothing about the labelling. A fixed-lock
  session could monitor modulation purity live from the tooth asymmetry alone.

---

**Where the numbers live.** Modules M2 · producers `scripts/run_ruler.py` ·
results `results/ruler_campaign.csv`, `results/ruler_blocks.csv`,
`results/ruler_traces.csv`, `results/ruler_nlmap.csv` · figures
`figures/fig8_ruler.png`. Library code: `rb5s6s/ruler.py`, with $\Omega/2$
locked by a permanent test in `tests/test_constants.py`. The validity and
trimming rules are pre-registered in
[the ruler specification](../notes/ruler_validity_and_trim_prereg.md), and the
provenance of the combs themselves is [`DATA.md`](../DATA.md) §7.

**What would falsify this.** A comb whose teeth were spaced $\Omega$ rather
than $\Omega/2$. Every frequency in this repository would then be a factor of
two out, which is why the factor is held by three independent things: a
permanent test, the five-tooth amplitude pattern, and the spacings between the
four hyperfine labels.

[← The composite model](04_the_composite_model.md) · [The statistics →](06_the_statistics.md)
