*Chapter 12 of 12 of [the plan](../PLAN.md)*

## 13. The open apparatus items, and how the forecast handles each

Every cell-side number in this plan that nobody has measured is listed here,
with what it would change and how the forecast proceeds without it. The
guided-platform unknowns live in the fibre thread, per the skip promise
[the big picture](../BIG_PICTURE.md) declares. **An open item is
spanned, never assumed**, and the span lives in a committed producer so a
reader can see how far the answer moves across it.

**This chapter exists because the alternative failed.** On 2026-08-28 a
forecast of the next campaign used the 2025 archive's lock drift rate as
though it described the repaired lock. The apparatus had changed, this plan
already said so in two chapters, and the forecast contradicted the plan
instead of reading it. A list of what is genuinely unknown is what stops the
next session inventing a value, or asking for one nobody has.

| item | status | what it changes | how the forecast proceeds |
|---|---|---|---|
| **repaired lock, residual drift** | not measured. The lock was repaired 2026-08-16 and no longer drifts. Its rate is unknown, and [chapter 9](09_the-fixed-lock.md) section 10c.2 already calls for measuring it | every centre-channel measurement on either platform. Absolute line centres become available with a stable lock, which is what the 2025 campaign could not do | spanned from 0 to 40 kHz per minute, with the recovered precision reported at each point, in `results/projections.csv` and its guided-platform counterpart |
| **repaired lock, per-sweep excursion** | not measured. The same characterisation run [chapter 9](09_the-fixed-lock.md) calls for reads it beside the drift | every centre measurement on either platform rides it, as the drift row above | spanned in the fibre thread ([the campaign chapter](../big_picture/09_the-campaign-cases.md)): its paired-acquisition forecast covers the comb best-fit class to the wavemeter ceiling and the acquisition-geometry verdict there turns on exactly this item. No cell-side forecast reads it yet |
| **beam waist in the interaction volume** | not measured in this cell. The working 64 um is a same-conditions measurement from an earlier thesis on this apparatus lineage | the largest open systematic in the record. Every intensity-denominated number rides it | spanned across the band the data allow in `results/transit_mc.csv`, and [chapter 5](05_width-collision-amplitude.md) specifies the profile measurement that closes it |
| **cell temperature against the cold spot** | instrumented but the gradient is not resolved | the density lever, and through it the collisional coefficient | carried as a stated systematic in `results/beta_self_probe.csv` |
| **retro-reflection intensity ratio** | not measured. The working value is a stated prior, carried with its spread in `results/delta_alpha_posterior.csv`'s notes, and [chapter 7](07_acquisition-settings.md) records one in-record reading that contradicts it outright | the effective intensity, and through it every light-shift prediction. [Chapter 6](06_sizing-and-spending-rules.md) already schedules turning the assumption into a measurement | carried as the prior in `results/delta_alpha_posterior.csv`, whose limit row states how far the priors move it, and inside the predicted envelope of `results/stark_joint.csv` |

**The fit-window systematic on the collisional width**, not an apparatus
number but an analysis unknown the same rules govern: the window scan
(`results/fit_window_scan.csv`) shows a coherent drift of the fitted width
with the fit window that no committed error bar carries
(`docs/UNCERTAINTY.md` §3a). What closes it: the committed shared-slope
$\beta$ construction re-run per window. Until then the headline bound's own
line in [RESULTS.md](../RESULTS.md) points at that section, and the
forecast proceeds unchanged because every per-window indicative slope is
consistent with zero.

### The 225 mW point's power calibration

The predicted light shift and its coefficient scale as the power at the atoms,
and the record carries the 225 mW operating point without a calibration
uncertainty: the sweep's envelope (`rb5s6s/stark.py`) propagates the waist band
and the retro-ratio error and nothing for the power. Nobody holds the figure,
so it is a measurement here and not a question. It needs the meter's calibration
certificate, the loss budget between meter and cell, and the window
transmission at 993 nm. Until it exists the prediction band spans it at 5 per
cent, which moves $\kappa_\mathrm{pred}$ by the same 5 per cent, and
`results/prediction_band.csv` carries that span in its worst-case edges.

What it would change: whether the prediction band reaches the bound, and the
guided arm's per-run power ruler, since a calibrated power at the fibre is the
same measurement.

### The collection lens and its image distance

The fluorescence collection optics set the axial window of the interaction
volume, which is the `z_ratio` of `stark_ramp_axial`. That function has carried
the closed form since July with its window flagged open, and
`constants.collection_z_ratio()` now closes it from the focal length, the
image distance and the cathode's 12 mm dimension along the beam. Two of the
three are stated to a tolerance and not yet measured: $f = 18 \pm 1$ mm and an
image distance of $50 \pm 10$ mm.

They close with a ruler and no atoms. What they change: the window is
[0.26](../../results/prediction_band.csv "ref:prediction_band:collection_window:z_ratio")
Rayleigh ranges, where the ramp is exact over most of the shift range and the
recovered shift is biased low by
[-1.97](../../results/prediction_band.csv "ref:prediction_band:collection_window:shift_bias_width_pct")
per cent. That correction stays conservative only while the window is below
[1.691](../../results/prediction_band.csv "ref:prediction_band:collection_window:width_bias_sign_flip_z_ratio"),
and the third cumulant's own null sits at
[1.117](../../results/prediction_band.csv "ref:prediction_band:collection_window:skew_null_z_ratio").
**The largest of the three uncertainties is how the 50 mm is read**: as the
image distance it gives the window above, and as the object distance it would
give one about three times wider, a twelvefold larger bias with the null within
reach. `constants.COLLECTION_IMAGE_DIST_M` names the reading it takes.

### What each item costs to close

**The lock residual is the cheapest and the highest leverage.** It needs no
atoms: step the lock, record the recovery, and read an Allan deviation of line
centres across a session. [Chapter 9](09_the-fixed-lock.md) already specifies
it. Until it exists, every centre-channel forecast in this repository is
reported across a span instead of at a value.

**The waist closes in an afternoon with no atoms at all**, and it is the one
measurement that sharpens every existing bound at once.

**The collection distances close in a minute with a ruler**, and they are the
only items on this page already carried into a committed result instead of
being spanned around it.

### The guided-platform items

The nanofibre arm has open items of its own, and they are listed in the fibre
thread rather than here so that a reader with no fibre keeps the skip promise
of [BIG_PICTURE](../BIG_PICTURE.md):
[chapter 6](../big_picture/06_next-nanofibre.md).

---

*[Beyond 993 nm](11_beyond-993.md) - [The plan](../PLAN.md)*
