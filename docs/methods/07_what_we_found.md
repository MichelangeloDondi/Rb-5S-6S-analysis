*Chapter 7 of 8 · [methods index](../methods.md)*

This chapter sets out what the 2025 dataset delivered, and why every headline is a bound or a null. This chapter builds on the lineshape through statistics chapters, chapters 2 to 6 and sets out the results the paper reports and the reason each one is conditional, which the assumptions chapter then turns into what to challenge. Not covered here: you have read [`docs/RESULTS.md`](../RESULTS.md), the generated ledger of the same numbers with its full audit trail.

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

## 5. Findings from the 2025 data
### 5.1 $\beta_\text{self}$: the T-sweep bounds it

Headline: the T-sweep *bounds* $\beta_\text{self}$ and shows why it cannot
measure it. The raw, model-independent widths are **non-monotonic in
density** for two of the four peaks (993.4154 and 993.4207 nm): somewhere along
the sweep the line gets *narrower* at higher density, which no collision can
produce. The scatter left over about the fitted width-versus-density line is
0.14 to 0.25 MHz across the four peaks, and it is between-block scatter, the
2025 laser width wandering between cooling steps by about as much as the entire
collisional trend. No peak resolves a slope: the four signal-to-noise ratios are
1.1, 0.7, 0.8 and 1.9. Applying [§4.5](06_the_statistics.md), the model-independent 95% per-peak bound is

$$\boxed{ \beta_\text{self}\lesssim 0.03\text{ to }0.05\ \text{MHz per }10^{12}\ \text{cm}^{-3}. }$$

The four density points are 70, 90, 110 and 130 °C, a $\times48.1$ lever. The
130 °C point is the 225 mW power session, taken in the same optical and cell
configuration and inside the same continuous campaign, with each session's axis
calibrated from its own rate source before the two are put on one density axis
(`docs/RESEARCH_DECISIONS.md` §9). Folding it in stretches the lever from
$\times16.2$, and no three-point construction is kept alongside it.

Two coverage corrections define this bound (both 2026-07-16). First, the
between-block scatter that dominates the slope error is estimated on only
**two residual degrees of freedom** (4 density points, 2 fit parameters), so a
one-sided 95% limit needs the Student-t quantile $t(0.95, 2)=2.92$, not the
Gaussian-asymptotic 2 an earlier revision used.

Second, $\beta\propto 1/N$, so
the spread between published vapor-pressure correlations, now derived from
the model-form arms (24.3 per cent, worst at 70 °C, `density.py`'s
`N_SCALE_FRAC_SYST`), enters this bound as a conservative envelope on
$\beta$, not a measured response: a refit of $\beta$ itself at the
alternate law would move by less, lever-weighted toward the fit's hottest
point, and that refit is not yet a committed cell. The cold-spot direction
makes the fitted $\beta$ an
underestimate, so the bound is inflated on the + side ($\times1.2$, see
`density.py`). (The scatter estimate
divides by the degrees of freedom, not by $n$. Using $n$ would tighten the
bound, a directional bug fixed 2026-07-12.) The spread across the boxed range
is systematics rather than physics, because the four bounds track each peak's
residual scatter and not a physical rate, so the number to quote is the loosest
of the four.

A naive global Voigt fit instead reports a
4–10 sigma "detection", the [§4.5](06_the_statistics.md) cautionary tale in practice. This bound is
the 2025 data *showing the two-epoch design was necessary*, and is reported as a
vapour-cell result.

### 5.2 A hierarchical cross-check ($\beta$ per isotope)

The full fit ([§4.2](06_the_statistics.md),
`fit_global`), which lets $\sigma_\text{laser}$ drift per temperature
and weights each block by its own correlation time, returns
$\beta_{85}=$ [0.0086](../../results/global_fit.csv "ref:global_fit:beta_self:85Rb") $\pm$ [0.0026](../../results/global_fit.csv "ref:global_fit:beta_self:85Rb:err") and $\beta_{87}=$ [0.0093](../../results/global_fit.csv "ref:global_fit:beta_self:87Rb") $\pm$ [0.0030](../../results/global_fit.csv "ref:global_fit:beta_self:87Rb:err") MHz per $10^{12}$ cm⁻³:
**no isotope dependence**, the two differing by $0.0007$, well inside either
error bar, and dropping any one peak moves the value by at most $0.0072$. It is
a *model-based* value, and it sits **above** the per-peak model fits
(0.0043–0.0069) and **below** all four model-independent per-peak bounds
(0.025–0.042), the opposite ordering from the earlier joint fit this chapter
carried. The three estimators of the same quantity therefore span about
a factor of ten, and that spread across $\sigma_\text{laser}$ treatments is
the uncertainty on this deliverable, larger than any single fit's error
bar.

The cooling-sweep value's error budget is carried in
[`results/lever_crosscheck.csv`](../../results/lever_crosscheck.csv) rather
than composed here, and it is organised differently from an earlier telling
of this paragraph, which named a kernel axis, a transit axis, a density-scale
axis and a $w_0$-band sized against the retired $0.0433$ headline: a
statistical error of [0.0026](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_crosscheck:85Rb:err")/[0.0030](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_crosscheck:87Rb:err")
(85Rb/87Rb), a transit model-form axis of
[0.0462](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_modelform:85Rb")/[0.0454](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_modelform:87Rb")
(the $|\text{Voigt}-\text{Lehmann}|$ shift, [§4.7](06_the_statistics.md),
`run_global_fit`), now the largest of the group, an extra-homogeneous-kernel
axis of [0.0067](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_kernel:85Rb")
carried separately because it is not inside the model-form spread, a
sigma-sharing axis of
[0.0040](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_sharing:85Rb")/[0.0060](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_err_sharing:87Rb"),
and a $w_0$-band of
[0.0028](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_w0_band:85Rb") to
[0.0181](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_w0_band:85Rb:err") <!-- other-quantity: this file's own w0-band error at 85Rb, not the retired beta_lever_probe_130 cell -->
(85Rb), over transit reference widths 1.33 to 1.49 MHz, $w_0$ 45 to 40 µm,
the open waist band `constants.W0_BAND_M`. So the conservative
model-independent bound, not this value, stays the headline.

Its real value is the isotope test, and the in-sample consistency check
(`run_sigma_laser_sharing`) that the four peaks at each temperature agree on a
single $\sigma_\text{laser}$. That check is *passive*: χ²/dof = 0.28/0.59/0.32,
all well below 1, so the peak-blocks are closer to the shared model than their
own error bars, and the test cannot discriminate. It does not license the
sharing, it merely fails to contradict it (RESULTS §σ_laser sharing). It also
covers only 70, 90 and 110 °C, so it says nothing about sharing at the 130 °C
point that now carries most of the lever.

At the retired waist convention, until 2026-09-22, the fit's
$\sigma_\text{laser}(T)\approx2.0/2.2/1.5$ MHz was **not** a clean drift curve:
the free per-condition fit gave a *flat* 1.5–1.75 MHz, so that trend was the
$\beta \leftrightarrow \sigma_\text{laser}$ degeneracy under the density tie, not a
physical laser drift. At the ruled 42.38 µm the tied values are 0.64/0.98/0.69 MHz
(`results/global_fit.csv`) and the free per-condition inverse-variance means
0.33/0.84/0.71 MHz (`results/linefit_conditions.csv`, the temperature arm): neither is
flat, the laser width is small beside the 1.45 MHz transit, and at two conditions
the fit rails it at zero, so what the trend says about the laser is not read until
the fitter carries the full transit. It does not corrupt $\beta$, which the density
lever still pins.

The **lever cross-check** (`run_lever_crosscheck`) packages exactly this, the
cooling-sweep $\beta$ with its stacked error bars and a leave-one-peak and
leave-one-temperature scan, and adds the lever test: folding in the
130 °C anchor ([§4.2](06_the_statistics.md)) pulls $\beta$ down
to [0.0058](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_lever_probe_130:85Rb") (85Rb) and
[0.0076](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_lever_probe_130:87Rb") (87Rb), shifts of
[-0.0028](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_lever_probe_130:85Rb:err") and
[-0.0016](../../results/lever_crosscheck.csv "ref:lever_crosscheck:beta_lever_probe_130:87Rb:err")
against the cooling-sweep value, because $\gamma_\text{coll}$
rises only about [2.99](../../results/lever_crosscheck.csv "ref:lever_crosscheck:gamma_rise_factor:70to130")-fold across a ${\times}48.1$ density span. That is a
residual floor rather than resolved collisions, so $\beta$ is a lever-dependent
bound. The full audited
budget is in the results ledger (`docs/RESULTS.md`).

### 5.3 The 2025 laser width

$\sigma_\text{laser}(2025)\lesssim1.4$ MHz on the transition axis, which is
below [0.7](../../results/laser_epoch.csv "ref:laser_epoch:sigma_laser_bound:over_w0_band") MHz on the laser axis over the 40 to 45 µm band, and
$\sim0.54$ MHz laser-axis at the calculated 42 µm waist.
It is a bound and not a measurement, because that non-Lorentzian Gaussian
is degenerate with the transit width, and the transit Monte-Carlo ([§2.5](02_the_lineshape.md), M9)
now makes the degeneracy quantitative: the corrected transit adds $\sim2.1$ MHz
at $w_0=32$ µm (which overshoots the observed line, excluding 32 µm) and
$\sim1.41$ MHz at the calculated waist, so below $w_0\approx38$ µm transit
alone fills the observed 5.25 MHz and **the laser is narrow**, while at the
calculated waist the laser carries $\sim0.54$ MHz laser-axis, under the
bound: widening the waist hands width from transit to laser.

The
dataset cannot locate that crossover, and only a direct beam-profile $w_0$
can. (Slow drift is *not* the cause, at only $\sim0.01$ MHz within a scan.)
A measured $w_0$, by fixing transit, would turn this bound into a measurement.
Until then it is the ONF starting linewidth for the nanofibre extension.

### 5.4 The power sweep against the ramp law

At fixed
130 °C only the AC-Stark $S_0$ varies, so the ramp law ([§2.6](03_the_ac_stark_ramp.md)) predicts, and the
data confirm.

(C3a) The linewidth is **flat**, with no monotonic power broadening, and its
3 to 8% block scatter is the same between-block wander seen elsewhere.

A separate question about any width-versus-power reading is whether its
power axis is physical at all, since every campaign ladder ran monotone
in time. The 2025-07-04 rehearsal permits a one-metric test, the only such comparison the record holds today: its
trigger stamps show two peaks' ladders ascending and one descending, and
on a deliberately biased model-independent width a pooled comparison
with per-peak intercepts prefers power over clock time at
ΔAIC $= -12.4$, with the per-peak slopes carrying one sign in both
directions (ascending 993.4121 nm at $+3.00 \pm 0.78$ MHz/W and
993.4207 nm at $+0.86 \pm 0.66$, descending 993.4192 nm at
$+0.70 \pm 0.93$) but the descending one unresolved on its own, so the
pooled row, not any single ladder, carries the discrimination
([`power_time_sign_test.csv`](../../results/power_time_sign_test.csv),
every row DIAGNOSTIC).

Three limits are part of the statement. The
campaign-morning pilot, the least collinear arm in the file, gives a weak opposite-sign slope
($-2.7 \pm 1.7$ MHz/W) that resolves nothing either way and is that
file's recorded caveat. The fitted width on the same rehearsal behaves
differently: [the results ledger](../RESULTS.md) reports its trend on
the descending ladder while both ascending ladders show none, the
order-dependence that keeps the concavity provisional, and the
model-free and fitted metrics have not been reconciled row to row,
which is an open analysis item. And the campaign's own axis remains
unseparated: this paragraph is about the rehearsal, under one metric.
It neither measures the campaign's width law nor disturbs C3a's
flatness, and the withdrawn concavity of
[the composite-model chapter](04_the_composite_model.md) stays
withdrawn.

(C3b) The amplitude is **near $P^2$, and three of the four slopes are not
consistent with it** (log-log slopes 1.83 to 2.12). **Corrected**:
this paragraph previously read the four slopes as a band clustered on the rate
law, flagging only 993.4121 nm as low. Tested against 2 rather than described,
under a block bootstrap over the power cells that respects this sweep's
power-time collinearity, 993.4121 nm at 1.831 excludes 2 from below, 993.4154
nm at 2.121 and 993.4192 nm at 2.116 exclude it from above, <!-- other-quantity: amplitude-departure log-log slope exponents, not an identifiability-profile cell -->
and 993.4207 nm at
2.100 becomes consistent with 2 once the block treatment replaces the
within-cell error. The departure replicates in the 2025-07-04 rehearsal, whose
alternating ladder directions show it to be invariant under acquisition order,
and its ordering across lines follows their brightness rather than their
hyperfine branching, so it is a signature of the detection rather than of the
transition.

No inventoried mechanism predicts that combination, and
[the amplitude departure note](../notes/amplitude_departure_from_p2.md)
carries the construction. The interpretive discussion below is retained
because it remains the best account of the low slope specifically, and it does
not address the two high ones. The word is *near*, not *confirms*: at the thick-cell end ($\tau/\text{cm}$ up to 160)
a slope below 2 could be genuine saturation or a weak power-dependence of the
trapping collection efficiency through the saturating emitter profile, and the
single-temperature 2025 sweep cannot separate the two. The 4121 low slope
is the visible symptom of that degeneracy, resolvable only by the fixed-lock
session's multi-temperature sweeps.

(C3c) The **ramp** skew, growing as $P^3$, is below detection and is therefore a
bound. The committed residual skew is *not* zero: it is large and positive at
low power (up to about 10 sigma at 25 mW, e.g. 993.4154 nm $0.346\pm0.035$)
and *falls* with amplitude as $\sim\text{amp}^{-0.5}$. That is the Poisson
**shot-noise skewness** (the noise is right-skewed $\propto1/\sqrt{\text{counts}}$,
vanishing as the line brightens), a statistical artifact with the *opposite*
sign and power dependence to the ramp rather than a physical asymmetry. So the
ramp is the genuine null, and the significant low-power skew is identified
rather than unexplained. The old "power null" resolves into a typed suite, a
null (width) and a consistency check ($P^2$) and a bound (skew), with the
residual skew attributed to shot noise rather than reported as zero.

(C3d) the same width-vs-power data **bound the AC-Stark coefficient itself**
(module M4e, `run_stark_sweep`): one shared $\kappa$ ($S_0=\kappa P$) fit to the
four peaks' FWHM-vs-power, each floating its power-independent core. In the
drifted dataset the *shift* (the pull $\propto S_0$) is dead, so $\kappa$ is
constrained only through the ramp's $\propto S_0^2$ width broadening, a weak
and one-sided handle, so the best fit **rails at $\kappa=0$**. That boundary is why
the bound needs care: at $\kappa=0$ the width handle has *zero gradient*, so a
linearized (Wald) $\kappa+1.645\sigma$ interval is evaluated where the Jacobian
column vanishes and its "sigma" is a finite-difference artifact with no 95%
coverage (that route reads 1.0 MHz un-inflated and 2.4 MHz inflated, both kept
in the CSV as replaced diagnostics).

The quoted limit is therefore a
**profile likelihood**: scan $\kappa$ upward, re-minimizing the per-peak cores,
to the one-sided crossing $\Delta\chi^2=2.706\times\chi^2_\text{red}$ (the
threshold scaled by the block-to-block over-dispersion $\chi^2_\text{red}=3.7$,
the same conservative rescale the $\sqrt{\chi^2_\text{red}}$ inflation applies
elsewhere). It gives a 95% profile-likelihood bound of 0.63 MHz from the
widths alone.

The joint three-session full-profile fit
(`run_stark_joint`, RESULTS C3f), over 100 traces from the campaign, 46 from
the 4 July evening session and 26 from the campaign-morning session,
sharpens the same channel to $S_0(225\ \text{mW})$ below [0.18](../../results/stark_joint.csv "ref:stark_joint:S0_225mW_ub95:primary") MHz
with the ramp on either side of the line (mirrored, the limit moves by under one per
cent, a check of 2026-09-24), under the [0.729](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred:shared") MHz predicted at the waist convention, so the $\Delta\alpha$
bracket sits under both values on the table (Orson's published 1093 and this
work's recomputed [-1131.8](../../results/polarizability_deep.csv "ref:polarizability_deep:delta_alpha:at_drive"),
[§2.6](03_the_ac_stark_ramp.md)). The constraint
therefore lands on the (Δα, intensity) pair rather than adjudicating the
theory, and since the waist convention is a lineage profile taken on another source, the
comparison is a direct test of it. The comparison is on magnitude and is
therefore untouched by the sign disagreement between them
([THEORY_NOTE §5](../THEORY_NOTE.md)).

The reading is a conservative bound, not a sensitivity claim: the width
channel is over-dispersed ($\chi^2_\text{red}=3.7$, block-to-block drift),
so it does not cleanly resolve or exclude $\kappa$. The [0.796](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_ub95_profile:shared") MHz limit uses the
inflated threshold and brackets the predicted [0.729](../../results/stark_sweep.csv "ref:stark_sweep:S0_225mW_pred:shared") MHz without measuring it.

It bounds the drift, not the
coefficient's scale. It is also loose by a measured factor, because the model
behind it carries no saturation and no hyperfine pumping and both broaden with
the ramp's own $P^2$ signature
([§2.8](04_the_composite_model.md)): injecting the saturation term and
re-profiling gives $0.23$ MHz here and $0.117$ MHz on the joint fit, factors of
$2.8$ and $2.21$. Neither committed bound moves, because the injected law is
the two-level homogeneous form used with a two-photon Rabi frequency, so the
looseness is stated with its size rather than taken. There is no second channel
behind it.

The centre channel
was worked and yields nothing: the fitted pull reverses sign between drift
models, and the limit loosens as the drift model gains freedom,
$|S_0(225\ \text{mW})|$ below $9.49$, $14.57$ and $17.65$ MHz for linear,
one-exponential and two-exponential drift, so the pull is unidentifiable in
this dataset rather than merely imprecise. The tighter centre bounds earlier
releases carried are withdrawn, because they differenced centres across changes
of the scope horizontal position ([`THEORY_NOTE.md`](../THEORY_NOTE.md) §3).
A second attempt worked the channel the other way round, fitting inside each
maximal run of unchanged scope window (module M27, `run_centre_stark`), where
the lock is untouched and a constant offset cannot bias a slope.

It returns a
bound of $8.65$ MHz/W, about $7.8$ times weaker than the width channel's [0.810](../../results/stark_joint.csv "ref:stark_joint:kappa_ub95:primary")
and $12.21$ (about $11.0$ times weaker) once its drift prior is corrected to the sign-undetermined form
the 2026-07-30 window-reference correction leaves licensed (addendum 29),
and it measures its own false-positive floor by injecting a power step into
epochs where the true power difference is zero: those controls return spurious
pulls of several MHz/W, comparable to the signal.

Extending it to the other two
sessions was then tested and closed, and the closure is arithmetic rather than
a preference. The campaign itself ran its powers in monotonic order, so any
drift the epoch model does not capture is confounded with power by
construction. The separate session of that morning, which has three and a half
times the lever and would otherwise be the best of the three, moves its own
recorded frame with power at $9.25$ MHz/W, eleven times the statistical error
the extra lever would buy. The 4 July evening session has no bracketing pair
to calibrate a frame against. What would reopen it is not a
better estimator but an export of the ramp monitor, which would supply a
frequency reference independent of the scope window
([`docs/notes/centre_channel_cannot_be_revived.md`](../notes/centre_channel_cannot_be_revived.md)).

Width and shape are the dataset's only light-shift channel, and the two
constructions above are two readings of that one channel, not two channels. A
fixed-lock session's stable lock would resurrect the pull
$\propto S_0$ (a far stronger handle), and the small waist makes $S_0$
several-fold larger, which would turn this bracket into a measured coefficient.

### 5.5 Radiation trapping

Thick cell, near-linear signal, drift-dominated ratios. Peak amplitude scales roughly *linearly* with density: log-log
slopes $0.94(13)$, $0.91(5)$, $0.85(15)$, $1.02(8)$ across $\times52$ in $N$, <!-- other-quantity: amplitude slopes -->
all consistent with slope 1 within about 1 to 2 sigma, so any
trapping/993-absorption rollover is weak and not resolved, consistent with
M1's temperature-flat shot-noise coefficient. This is at first sight *surprising*: the
D1 optical depth ([§2.7](04_the_composite_model.md)) is $\tau/\text{cm}\approx1$ to $60$ (⁸⁷Rb) and
$3$ to $160$ (⁸⁵Rb) across the sweep, so over the few-cm path the cell is
optically **thick** and naive trapping should bite hard. The resolution is a
real physical statement about the geometry: a thick cell without quenching
still emits nearly one collected 795 nm photon per excitation. Trapping
*redistributes* the photons in a random walk to the walls rather than destroying
them, and the wide $f18$ mm collection captures the diffuse re-emission, so the
collected signal stays $\propto N$. The near-linearity thus **bounds
non-radiative quenching to be weak** over the trapping random-walk.

Trapping's degeneracy-breaking (peak-differential) effect ([§2.7](04_the_composite_model.md)) is then sought
three ways, all model-independent. (i) The isotope-averaged slope difference is
the cleanest fingerprint: ⁸⁷Rb $\langle s\rangle=1.00(7)$ vs ⁸⁵Rb
$\langle s\rangle=0.91(5)$, so ⁸⁵Rb is $0.09(8)$ *more* sublinear, which is the
sign trapping predicts (⁸⁵Rb has $2.6\times$ the absorbers) but only at
$\sim1\sigma$, a hint rather than a detection. (ii) The peak-*height* ratios are
**non-monotonic** in density (e.g. 993.4207/993.4121 nm runs
$1.09\to1.01\to2.48\to1.94$ <!-- other-quantity: a sequence of ratios -->), whereas trapping would bend them *monotonically*,
so the 30 to 50% degeneracy-law disagreement (module M10, on the *areas*) is
between-block **drift**, not trapping. (iii) A one-parameter trapping model does not improve
the fit over pure $\propto N$ (both $\chi^2_\text{red}\gg1$, dominated by the
drift scatter).

*Conclusion:* trapping is physically present and expected-large by
$\tau$, but its net effect on the collected amplitude is modest and its
degeneracy-breaking effect is $\lesssim10$%, buried under drift. Separating it
needs a fixed-lock interleaved-peak run with a controlled collection
geometry. A clean separation of the trapping/993-absorption losses and an
absolute trapping fraction additionally want [Nieddu's 2019](../lit/nieddu2019.md) same-channel
baseline (not loaded here).

### 5.6 The Lehmann cusp, not resolvable in 2025 as designed

At the
cold-dim 70 °C cell of the grid the BIC comparison ([§4.7](06_the_statistics.md)) gives
$\Delta\text{BIC}(\text{Voigt}-\text{Lehmann})=+0.4/+0.9/+3.7/-0.1$ across
peaks, a **statistical null**: three of four have $|\Delta\text{BIC}|$ below 2
(the "not worth a mention" band) and the fourth is 3.6 (weak, and it is the
same peak, 993.4192 nm, whose fits are noisiest elsewhere), against a claim gate of
$\Delta\text{BIC}\gtrsim10$. The statement is that **the 2025 data
cannot distinguish a cusped (Lehmann) from a smooth (Voigt) extra-broadening**,
exactly as the two-epoch design anticipated, since the $\sim2$ MHz bad-lock
laser Gaussian smears the cusp and the transit/laser split is itself
unresolved ([§2.5](02_the_lineshape.md)). No lean is claimed. The decisive cusp test is the fixed-lock session's
narrow-laser data, for which this module (closure-tested to prefer the right
form when a cusp *is* present) is validated infrastructure.

### 5.7 Area ratios against the degeneracy law

A parameter-free prediction the dataset cannot yet test. For two *identical* photons the
$S\to S$ two-photon operator is purely **scalar** (rank 2 cannot connect
$J=\tfrac12\to\tfrac12$), so every $F,m_F$ has the same per-atom rate and the
line *areas* (not heights, which confound with width) must be pure initial
population: $S\propto\text{abundance}\times(2F{+}1)$, i.e. within-isotope
ratios of exactly $5/3$ (⁸⁷Rb) and $7/5$ (⁸⁵Rb). Measured: the
within-block repeatability is 1–3%, but the area ratios swing
30–50% *between* temperatures, non-monotonically (the 993.4207/993.4121 nm
*area* ratio runs $1.10\to0.98\to2.53\to1.97$ against a constant $5/3$, and the
slightly different height ratios in the trapping paragraph above tell the
same drift story). That is between-block power and alignment drift rather than
physics, because real differential trapping would be smooth in density.
Two consequences: cross-peak amplitude comparisons in this dataset carry
roughly 30–50% systematics (per-peak, within-block analyses like M7 are
unaffected), and the clean degeneracy-law test is a task for a fixed-lock
session: measure the four peaks **interleaved**, with power logging.

`figures/fig4_amplitude_ratios.png` draws the two measured area ratios against
those two predictions, each on its own dashed line, over cell temperature. Its
bars combine the scatter over repeats with the drift between measurement blocks,
and that combination is far larger than the difference the prediction would
show, which is the sense in which this dataset cannot test the law.

### 5.8 Foundational results underpinning the above

The sweep rate is
$0.042524(51)$ MHz/ms (laser axis), $\times11$ slower than the pre-analysis
seed, confirmed by three independent methods, sweep linear to better than 0.3% within a
block. The 20 blocks over-disperse ($\chi^2_\text{red}=8.1$), block-level
ruler scatter (bracket-to-bracket drift, and the calibrated spacing rule removes
three temperature-session combs while missing
`rulers_p/4207nm_T130C_P225mWi_RFon_before_r5.csv`, which the top-three amplitude test does
flag, so the two instruments disagree about that one trace, see
[`DATA.md`](../DATA.md) §5 and
[the ruler specification](../notes/ruler_validity_and_trim_prereg.md)
amendment 3 C6),
**not** a peak-ordered trend (bracket-resolved rates are non-monotonic), and
the quoted error is already $\sqrt{\chi^2_\text{red}}$-inflated (≈2.8×)
to absorb it, so it is a symmetric common-axis uncertainty rather than a
cross-peak bias, and the fits use each condition's own block rate. Total
line widths are 4.8 to 5.7 MHz, sitting on the
[lineshape chapter](02_the_lineshape.md) budget. The dataset
is decoded and frozen: 722 files became **297 unique traces**, and every anomaly
(double-saves, renames, discards, off-center-sweep mirrors) is explained and
either excluded or handled.

---

**Where the numbers live.** Modules M2, M4, M4b, M4d, M4e, M5, M6, M7, M8, M10,
M23 · producers `scripts/run_beta_self.py`, `scripts/run_global_fit.py`,
`scripts/run_lever_crosscheck.py`, `scripts/run_laser_epoch.py`,
`scripts/run_power_sweep.py`, `scripts/run_stark_sweep.py`,
`scripts/run_stark_joint.py`, `scripts/run_amplitude_trapping.py`,
`scripts/run_modelform.py`, `scripts/run_amplitude_ratios.py`,
`scripts/run_ruler.py` · results `results/beta_self.csv`,
`results/global_fit.csv`, `results/lever_crosscheck.csv`,
`results/laser_epoch.csv`, `results/power_sweep.csv`,
`results/stark_sweep.csv`, `results/stark_joint.csv`,
`results/amplitude_trapping.csv`, `results/modelform.csv`,
`results/amplitude_ratios.csv`, `results/ruler_campaign.csv` · figures
`figures/fig1_width_vs_density.png`, `figures/fig2_power_sweep.png`,
`figures/fig4_amplitude_ratios.png`, `figures/fig8_ruler.png`. The deliverable
codes C1, C2 and C3a to C3g index the same results in
[`docs/RESULTS.md`](../RESULTS.md), which is generated from these CSVs.

**What would falsify this.** A width that grew monotonically with density on
all four peaks. Every bound in this chapter is a bound because the dataset's
raw widths are non-monotonic, so a clean monotonic set at the same conditions
would turn the collisional headline from a bound into a measurement and would
say the non-monotonicity was an artifact of this analysis rather than of the
2025 lock.

[← The statistics](06_the_statistics.md) · [Assumptions, and where this can go →](08_assumptions_and_outlook.md)
