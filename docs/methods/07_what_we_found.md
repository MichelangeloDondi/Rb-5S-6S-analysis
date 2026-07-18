*Chapter 7 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

## 5. What we found (2025 archival data)

**Headline: the T-sweep *bounds* $\beta_\text{self}$ and shows why it cannot
measure it.** The raw, model-independent widths are **non-monotonic in
density** for three of four peaks (e.g. 993.4207 nm: 5.11 → 4.92 → 5.35 MHz for
70 → 90 → 110 °C — *narrower* at higher density, which no collision can
produce). Within-block repeat scatter is $\sim0.05$ MHz, but between-block
scatter is $\sim0.06$–$0.16$ MHz: the 2025 laser width drifted between cooling
steps by about as much as the entire collisional trend. Applying [§4.5 — The statistics](06_the_statistics.md), the model-independent 95% per-peak bound is

$$\boxed{ \beta_\text{self}\lesssim 0.2\text{ to }0.4\ \text{MHz per }10^{12}\ \text{cm}^{-3}. }$$

Two coverage corrections define this bound (both 2026-07-16). First, the
between-block scatter that dominates the slope error is estimated on only
**one residual degree of freedom** (3 density points, 2 fit parameters), so a
one-sided 95% limit needs the Student-t quantile $t(0.95, 1)=6.31$, not the
Gaussian-asymptotic 2 an earlier revision used — that earlier
"$\approx2\sigma$" quote (0.07–0.15) under-covered, which is exactly why it
was flagged with a factor-2 own-uncertainty; the t-quantile formalizes that
flag into the number. Second, $\beta\propto 1/N$, so the $\sim$20% spread
between published vapor-pressure correlations is a density-scale systematic
that moves every $\beta$ by the same fraction; the cold-spot direction makes
the fitted $\beta$ an underestimate, so the bound is inflated on the + side
($\times1.2$; see `density.py`). (The scatter estimate divides by the DOF,
not by $n$; using $n$ would tighten the bound $\sim$40% — a directional bug
fixed 2026-07-12.) A naive global Voigt fit instead reports a
4–10$\sigma$ "detection" — the [§4.5 — The statistics](06_the_statistics.md) cautionary tale made flesh. This bound is
the archival data *proving the two-epoch design was necessary*, and is itself a
Paper-1 result.

**A hierarchical cross-check ($\beta$ per isotope).** The full fit ([§4.2 — The statistics](06_the_statistics.md),
`fit_global`) — which properly lets $\sigma_\text{laser}$ drift per temperature
and weights each block by its own correlation time — returns
$\beta_{85}=\beta_{87}=0.036(4)$ MHz per $10^{12}$ cm$^{-3}$: **no isotope
dependence** ($\beta_{85}-\beta_{87}=0.000\pm0.006$, $0.0\sigma$), robust to
leaving any block out. It is a *model-based* value: it sits above the per-peak model fits
($0.027$–$0.047$) but comfortably **below all four** model-independent per-peak
bounds ($0.22$–$0.44$ with the corrected t-quantile and density-scale
coverage) — so it is consistent with the bound, not in
tension with it, though it still inherits the same $w_0$ and model-form limits.
Those limits are **not** hand-waved: this $0.036$ carries **four separate error
bars**, and the systematics dominate the statistical one — statistical
$\pm0.004$ (joint-fit covariance); **transit model-form $\pm0.033$** (the
$|\text{Voigt}-\text{Lehmann}|$ shift, [§4.7 — The statistics](06_the_statistics.md), `run_global_fit`: the Gaussian-transit
Voigt gives the *higher* $\beta\approx0.068$ because a narrower transit core forces
more width onto collisions); **density scale $\pm0.007$** ($\beta\propto1/N$, the
$\sim$20% spread between published vapor-pressure correlations, `density.py`);
and — **largest of the four** — the $w_0$-band
$[0.025,0.065]$ (a factor ${\sim}2.5$, since every absolute $\beta$ rides on the
OPEN beam waist). The paper must quote all four, not the optimistic $\pm0.004$ alone.
So the conservative model-independent bound, not this value, stays the headline.
Its real value is the isotope test, and the validation (M4c, §sharing test) that
the four peaks at each temperature agree on a single $\sigma_\text{laser}$
(χ²/dof < 1) — so the per-temperature sharing is licensed. The fit's
$\sigma_\text{laser}(T)\approx2.1/2.2/1.6$ MHz is **not** a clean drift curve,
though: the free per-condition fit gives a *flat* $\sim$1.7 MHz, so that trend
is the $\beta \leftrightarrow \sigma_\text{laser}$ degeneracy under the density
tie, not a physical laser drift — the 110 °C dip is a model artifact, not a
stale block (and it does not corrupt $\beta$, which the density lever still
pins).

The **lever cross-check** (M4d, `run_lever_crosscheck`) packages exactly this — the
cooling-sweep $\beta$ with its stacked error bars and a leave-one-peak /
leave-one-temperature scan — and adds the honest lever test: folding in the
130 °C anchor ([§4.2 — The statistics](06_the_statistics.md)) pulls $\beta$ well below $0.036$, because $\gamma_\text{coll}$
rises only ${\sim}1.5\times$ across a ${\times}52$ density span — a residual floor,
not resolved collisions — so $\beta$ is a lever-dependent bound. The full audited
budget is in the results ledger (`docs/RESULTS.md`).

**The 2025 laser width (deliverable C2) — an upper bound.**
$\sigma_\text{laser}(2025)\lesssim2.0$ MHz (transition axis; $\lesssim1.0$ MHz
laser axis; it is $\sim0.84$ MHz laser-axis at the $w_0=50\ \mu$m prior) —
a bound, not a measurement, because that non-Lorentzian Gaussian
is degenerate with the transit width, and the transit Monte-Carlo ([§2.5 — The lineshape, kernel by kernel](02_the_lineshape.md), M9)
now makes the degeneracy quantitative: the corrected transit adds $\sim2.1$ MHz
at $w_0=32\ \mu$m (which OVERSHOOTS the observed line, excluding 32 µm) but only
$\sim1.2$ MHz at the $50\ \mu$m prior, so below $w_0\approx38\ \mu$m transit
alone fills the observed 5.25 MHz and **the laser is narrow**, while at the
50 µm prior the laser carries $\sim0.8$ MHz laser-axis. The
archival data cannot locate that crossover; only the knife-edge measurement $w_0$
can. (Slow drift is *not* the culprit — only $\sim0.01$ MHz within a scan.) The
knife-edge $w_0$ (fixing transit) turns this bound into a measurement; meanwhile it is the
ONF starting linewidth for Paper 2.

**The power sweep, recast as confirmed predictions (deliverable C3).** At fixed
130 °C only the AC-Stark $S_0$ varies, so the ramp law ([§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md)) predicts, and the
data confirm: (C3a) the linewidth is **flat** — no monotonic power broadening,
with 3–8% block scatter that is the same between-block wander seen elsewhere;
(C3b) the amplitude is **consistent with $P^2$** (log-log slopes 1.83–2.12,
clustered on the two-photon rate law; 993.4121 nm sits below at 1.83). We say
*consistent with*, not *confirms*: at the thick-cell end ($\tau/$cm up to 160)
a slope below 2 could be genuine saturation OR a weak power-dependence of the
trapping collection efficiency through the saturating emitter profile, and the
single-temperature archival sweep cannot separate the two — the 4121 low slope
is the visible symptom of that degeneracy, resolvable only by the fixed-lock session's
multi-$T$ sweeps;
(C3c) the **ramp** skew (growing as $P^3$) is below detection, a bound — but the
committed residual skew is emphatically *not* zero: it is large and positive at
low power (up to $\sim$10$\sigma$ at 25 mW, e.g. 993.4154 nm $0.345\pm0.036$)
and *falls* with amplitude as $\sim$amp$^{-0.5}$. That is the Poisson
**shot-noise skewness** (the noise is right-skewed $\propto1/\sqrt{\text{counts}}$,
vanishing as the line brightens) — a statistical artifact with the *opposite*
sign and power dependence to the ramp, not a physical asymmetry. So the ramp is
the genuine null; the significant low-power skew is identified, not unexplained.
The old "power null" is thus a suite of confirmed predictions — with the
residual skew correctly attributed to shot noise, not laundered into "zero."

(C3d) the same width-vs-power data **bound the AC-Stark coefficient itself**
(module M4e, `run_stark_sweep`): one shared $\kappa$ ($S_0=\kappa P$) fit to the
four peaks' FWHM-vs-power, each floating its power-independent core. In the
drifted archive the *shift* (the pull $\propto S_0$) is dead, so $\kappa$ is
constrained only through the ramp's $\propto S_0^2$ width broadening — a weak,
one-sided handle, so the best fit **rails at $\kappa=0$**. That boundary is why
the bound needs care: at $\kappa=0$ the width handle has *zero gradient*, so a
linearized (Wald) $\kappa+1.645\sigma$ interval is evaluated where the Jacobian
column vanishes and its "$\sigma$" is a finite-difference artifact with no 95%
coverage (it read a spurious 3.1 MHz). The quoted limit is therefore a
**profile likelihood** — scan $\kappa$ upward, re-minimizing the per-peak cores,
to the one-sided crossing $\Delta\chi^2=2.706\times\chi^2_\text{red}$ (the
threshold scaled by the block-to-block over-dispersion $\chi^2_\text{red}\approx4$,
the same conservative rescale the $\sqrt{\chi^2_\text{red}}$ inflation applies
elsewhere). It gives the 95% profile-likelihood bound
$$S_0(225\ \text{mW}) < 0.63\ \text{MHz},$$
sitting just above the predicted 0.59 MHz — i.e. $\Delta\alpha\lesssim1200$ a.u.
against the computed 1093 ([§3 — The AC-Stark ramp](03_the_ac_stark_ramp.md)).
The honest reading is a conservative bound, not a sensitivity claim: the width
channel is over-dispersed ($\chi^2_\text{red}\approx4.3$, block-to-block drift),
so it does not cleanly resolve or exclude $\kappa$ — the $0.63$ MHz limit uses the
inflated threshold and brackets the predicted $0.59$ without measuring it (an
unscaled threshold would fall below the prediction). It bounds the drift, not the
coefficient's scale. The fixed-lock session's stable lock resurrects the pull
$\propto S_0$ (a far stronger handle), and the small waist makes $S_0$
several-fold larger, turning this bracket into the measured coefficient.

**Radiation trapping — thick cell, near-linear signal, drift-dominated ratios
(module M7).** Peak amplitude scales roughly *linearly* with density: log-log
slopes $0.94(13)$, $0.91(5)$, $0.85(15)$, $1.02(8)$ across $\times52$ in $N$ —
all consistent with slope 1 within $\sim1$–$2\sigma$, so any
trapping/993-absorption rollover is weak and not resolved, consistent with
M1's flat-$T$ shot-noise coefficient. This is at first sight *surprising*: the
D1 optical depth ([§2.7 — The composite model (and what does not enter it)](04_the_composite_model.md)) is $\tau/\text{cm}\approx1$–$60$ ($^{87}$Rb) and
$3$–$160$ ($^{85}$Rb) across the sweep, so over the few-cm path the cell is
optically **thick** and naive trapping should bite hard. The resolution is a
real physical statement about the geometry: a thick cell without quenching
still emits nearly one collected 795 nm photon per excitation — trapping
*redistributes* the photons (a random walk to the walls) rather than destroying
them, and the wide $f18$ mm collection captures the diffuse re-emission — so the
collected signal stays $\propto N$. The near-linearity thus **bounds
non-radiative quenching to be weak** over the trapping random-walk.

Trapping's degeneracy-breaking (peak-differential) effect ([§2.7 — The composite model (and what does not enter it)](04_the_composite_model.md)) is then sought
three ways, all model-independent. (i) The isotope-averaged slope difference is
the cleanest fingerprint: $^{87}$Rb $\langle s\rangle=1.00(7)$ vs $^{85}$Rb
$\langle s\rangle=0.91(5)$, i.e. $^{85}$Rb is $0.09(8)$ *more* sublinear — the
sign trapping predicts ($^{85}$Rb has $2.6\times$ the absorbers), but only
$\sim1\sigma$: a hint, not a detection. (ii) The peak-*height* ratios are
**non-monotonic** in density (e.g. 993.4207/993.4121 nm runs
$1.09\to1.01\to2.48\to1.94$), whereas trapping would bend them *monotonically* —
so the 30–50% degeneracy-law disagreement (module M10, on the *areas*) is
between-block **drift**, not trapping. (iii) A one-parameter trapping model does not improve
the fit over pure $\propto N$ (both $\chi^2_\text{red}\gg1$, dominated by the
drift scatter). *Verdict:* trapping is physically present and expected-large by
$\tau$, but its net effect on the collected amplitude is modest and its
degeneracy-breaking effect is $\lesssim10$%, buried under drift; separating it
needs the fixed-lock session's fixed-lock interleaved-peak run with a controlled collection
geometry. A clean separation of the trapping/993-absorption losses and an
absolute trapping fraction additionally want [Nieddu's 2019](../lit/nieddu2019.md) same-channel
baseline (not loaded here).

**The Lehmann cusp — not resolvable in 2025, as designed (module M8).** At the
cold-dim 70 °C corner the BIC comparison ([§4.7 — The statistics](06_the_statistics.md)) gives
$\Delta\text{BIC}(\text{Voigt}-\text{Lehmann})=+0.4/+0.9/+3.6/-0.1$ across
peaks — a **statistical null**: three of four are $|\Delta\text{BIC}|<2$
(the "not worth a mention" band) and the fourth is 3.6 (weak, and it is the
same peak, 993.4192 nm, whose fits are noisiest elsewhere), against a claim gate of
$\Delta\text{BIC}\gtrsim10$. The honest statement is that **the archival data
cannot distinguish a cusped (Lehmann) from a smooth (Voigt) extra-broadening**
— exactly as the two-epoch design anticipated, since the $\sim2$ MHz bad-lock
laser Gaussian smears the cusp and the transit/laser split is itself
unresolved ([§2.5 — The lineshape, kernel by kernel](02_the_lineshape.md)). No lean is claimed. The decisive cusp test is the fixed-lock session's
narrow-laser data, for which this module (closure-tested to prefer the right
form when a cusp *is* present) is validated infrastructure.

**Area ratios vs the degeneracy law (module M10) — a parameter-free
prediction the archive cannot yet test.** For two *identical* photons the
$S\to S$ two-photon operator is purely **scalar** (rank 2 cannot connect
$J=\tfrac12\to\tfrac12$), so every $F,m_F$ has the same per-atom rate and the
line *areas* (not heights — heights confound with width) must be pure initial
population: $S\propto\text{abundance}\times(2F{+}1)$, i.e. within-isotope
ratios of exactly $5/3$ ($^{87}$Rb) and $7/5$ ($^{85}$Rb). Measured: the
within-block statistics are superb ($1$–$3$%), but the area ratios swing
30–50% *between* temperatures, non-monotonically (the 993.4207/993.4121 nm
*area* ratio runs $1.10\to0.98\to2.53\to1.97$ against a constant $5/3$; the
slightly different height ratios in the trapping paragraph above tell the
same drift story) — that is between-block power/alignment drift, not physics
(real differential trapping would be smooth in density).
Two consequences: cross-peak amplitude comparisons in this archive carry
$\sim$30–50% systematics (per-peak, within-block analyses like M7 are
unaffected), and the clean degeneracy-law test is an task for the fixed-lock session — measure
the four peaks **interleaved**, with power logging.

**Foundational results underpinning all of the above.** The sweep rate is
$0.04257(5)$ MHz/ms (laser axis) — $\times11$ slower than the pre-analysis
seed, confirmed by three independent methods, sweep linear to $<0.4$% within a
block. The 20 blocks over-disperse ($\chi^2_\text{red}=6.8$) — block-level
ruler scatter (bracket-to-bracket drift, a likely 993.4207-nm-*after* outlier),
**not** a peak-ordered trend (bracket-resolved rates are non-monotonic) — and
the quoted error is already $\sqrt{\chi^2_\text{red}}$-inflated ($\approx$2.6×)
to absorb it, so it is a symmetric common-axis uncertainty, not a cross-peak
bias; the fits use each condition's own block rate. Total
line widths are 4.8–5.5 MHz, sitting exactly on the [§2 — The lineshape, kernel by kernel](02_the_lineshape.md) budget; and the dataset
is decoded and frozen (722 files → **297 unique traces**, every anomaly —
double-saves, renames, discards, off-center-sweep mirrors — explained and
either quarantined or handled).

---

---

[← The statistics](06_the_statistics.md) · [Assumptions, and where this can go →](08_assumptions_and_outlook.md)
