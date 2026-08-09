*Chapter 5 of 8 · [methods index](../methods.md)*

**The question.** How does a record of volts against time become a frequency
axis, and how well is that axis known?
**Takes.** The measurement chapter, for the sweep and the apparatus. It needs
none of the lineshape chapters, which is why it can be read early.
**Gives.** The tooth spacing and the sweep rate that turn every millisecond in
the archive into megahertz. Every width quoted anywhere in this set is
denominated in this axis.
**Skip if.** You are reading for the physics of the line rather than for the
calibration. Nothing later re-derives the axis, it only spends it.

## 3. From volts-versus-time to a frequency axis (the EOM ruler)

The scope records fluorescence versus *time* while the laser sweeps; we need
$\nu$ versus time. The sweep is nonlinear and its rate unknown, so a ruler was
built into the scan: an EOM phase-modulates the light at exactly
$\Omega=12.5$ MHz, adding sidebands at $\nu_c\pm n\Omega$ around the carrier
$\nu_c$. Two-photon absorption picks any *pair* of sidebands whose frequencies
sum to the transition $\nu_0$:

$$(\nu_c+m\Omega)+(\nu_c+m'\Omega)=\nu_0
  \Longrightarrow
2\nu_c+(m+m')\Omega=\nu_0$$

Writing $k=m+m'$, resonances occur at carrier frequencies
$\nu_c=(\nu_0-k\Omega)/2$, i.e. a comb of line-copies spaced by

$$\boxed{ \Delta\nu_\text{tooth}=\frac{\Omega}{2}=6.25\ \text{MHz (laser axis)} }$$

— the same factor-2 as [§0](../methods.md). Fitting the tooth spacing (in ms) per block gives
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
and amendment 6). *Code:* `ruler.py` (M2);
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

### Why the ruler is a clean number — the common-mode rejections

The rate is a *differential* measurement across five copies of the **same
physical line**, and everything that afflicts the line afflicts every copy
equally:

- **The AC-Stark shift.** The atom sees the *total* field — carrier plus all
  sidebands, both beams — at every instant, regardless of which tooth is
  resonant, so the light shift translates the whole comb **rigidly**: the
  spacing is untouched. The residual is second-order — a power drift *within*
  one trace shifts teeth differentially by $S_0\times$(fractional drift per
  spacing) $\lesssim10^{-4}$ at the archival $S_0\lesssim0.6$ MHz — below the
  quoted precision.
- **The line asymmetry** (the ramp skew of [§2.6](03_the_ac_stark_ramp.md),
  or any other shape distortion). Same line, same intensity, same shape on
  every tooth ⇒ the same centre pull on every tooth ⇒ absorbed into the comb
  phase $t_0$, never into the spacing. The genuine second-order effect —
  **edge teeth have only one neighbour**, so overlapping *asymmetric* wings
  pull the comb ends differently — is why the fit is a *constrained
  simultaneous* comb (one shared tooth shape, free heights; at about 147 ms
  spacing and about 60 ms width a strong tooth's wing under a weak neighbour
  is about 20% of the weak peak, and single-tooth fits pull centres by O(ms)),
  and why the free-centres nonlinearity map exists: it bounds *any*
  tooth-dependent pull — scan nonlinearity and differential shape effects
  together — **empirically at $\lesssim0.3$% per position**
  (`results/ruler_nlmap.csv`), already inside the quoted error through the
  PDG block-scatter inflation.
- **Sideband amplitude imbalance** (residual AM from the carrier-suppression
  trick): absorbed by the free per-tooth heights — amplitude never enters the
  spacing.
- **Laser drift during a trace** is not a bias but part of the *measured*
  effective rate, and the line fits use their own block's rate — the drift is
  self-consistently calibrated out by a per-block
  ruler under a drifting lock.

![a ruler trace and the sweep-linearity map](../../figures/fig8_ruler.png)

*A representative ruler trace with its seven-tooth comb fit over its
standardized residual strip (left) and the pooled sweep-linearity map
(right): the local rate never departs from the block rate by more than 0.3%
in any well-sampled window. Six of the seven teeth stand above this trace's
fit residual, and the panel states why the seventh does not: the third-order
pair carries about 2% of the first-order power at this modulation depth, and
the scan end clips the outermost window, as on every recorded ruler
(pre-registration
[amendment 4](../notes/ruler_validity_and_trim_prereg.md)). The residual strip
carries the standardized units of the statistics chapter's §4.1, and the climb
at the scan end is the clipped window showing itself in the evidence.*

### The comb amplitudes — and the pure-phase-modulation null

For *pure* phase modulation at index $\beta$ on both counter-propagating
beams, the two-photon tooth amplitudes obey an exact closed law: the tooth at
$k$ sums every sideband pair $m+m'=k$, and by Neumann's addition theorem

$$A_k \propto \Big|\sum_m J_m(\beta) J_{k-m}(\beta)\Big|^2 = J_k(2\beta)^2 .$$

This explains the 2025 design compromise and prescribes its fix:

- **At small $\beta$ the sidebands are buried**: $J_k(2\beta)^2$ gives
  $1 : 0.10 : 0.002$ at $\beta=0.3$ — the outer teeth drown in the central
  tooth's tails. The 2025 workaround rotated a half-wave plate to admix
  amplitude modulation and suppress the optical carrier — which worked, but
  put the ruler light at a **different polarization and power than the science
  light** (the reason the ruler traces cannot serve as a hardware-matched
  width monitor for the archive; PLAN §7).
- **The fix needs no polarizer**: drive the EOM at
  $\beta \approx 1.202$ (where $J_0(2\beta)=0$) and the central tooth **nulls
  by coherent pair interference** — the two-photon analogue of carrier
  suppression — leaving a comb $0 : 1.00 : 0.69 : 0.15$ ($k=0,\pm1,\pm2,\pm3$)
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
