# Theory note: the AC-Stark ramp lineshape of a focused two-photon transition

*A short self-contained note for a theoretical check and a contribution. The
backing pipeline and data live in this repository. Nothing here depends on
reading the code. Notation follows the README, and every frequency is on the
two-photon **transition axis** (twice the laser frequency) unless stated.*

**The question.** What does a focused beam do to the shape of a two-photon
line, and how much of that is new?
**Takes.** Nothing. The note is self-contained and does not require the code.
**Gives.** The ramp law and its cumulants, the diverging-beam form and its sign
flip, the two width companions, the open sign disagreement on the
polarizability, and an explicit position against the nearest prior art.
**Skip if.** You want the recorded result. This is the theory behind it, and
its central quantity is below the 2025 noise floor.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

## 1. What this note asks

We drive the Doppler-free $5S_{1/2}\to 6S_{1/2}$ two-photon transition in a Rb
vapour cell with a **focused, retro-reflected** 993 nm beam. Because the
excitation rate goes as the square of a spatially inhomogeneous intensity, the
distribution of AC-Stark shifts across the illuminated atoms is not a single
number but a **skewed distribution with a closed form**. That relation is a
1980 result, Eq. (5.3) of the multifrequency-field review of Delone,
Kovarskii, Masalov and Perel'man, and §2 shows the
reduction. What this note does is evaluate it for the case where the
distribution is set by beam geometry rather than by laser statistics, which is
where their integral closes and ours does not stay formal. It gives that
evaluation, its moments, the drift-immune way we extract it from a lock too
unstable to hold a line centre, and the field-intensity convention that fixes
its coefficient. It closes with **one genuinely open theoretical question**, the
survival of the closed form under the real collection geometry, which is the
natural place for a contribution.


| you want | go to |
|---|---|
| the derivation and its moments | §2 |
| whether atomic motion destroys it | §2.1 |
| why a light shift is measurable from a drifted dataset | §3 |
| what the 2025 data actually returned | §4 |
| the intensity convention, and the $\Delta\alpha$ sign dispute | §5 |
| what is new here and what is not | §6 |
| the open question | §7 |
[methods chapter 3](methods/03_the_ac_stark_ramp.md). This note states the

## 2. The ramp law

Let the two-photon excitation rate be $\propto I^{n}$ with $n=2$ (one power of
$I$ per photon), and the light shift of the transition be $s = -\kappa I$ with
positive $\kappa$ (red shift, sign discussed in §5). In a Gaussian beam
$I(r)=I_0 e^{-2r^2/w_0^2}$, put $u \equiv I/I_0 \in (0,1]$. The signal from the
annulus $[r,r+dr]$ is

$$dS \propto I^{n}(2\pi r\ dr) \propto u^{n} r\ dr$$

Changing variable with $du/u = -(4r/w_0^2)\ dr$ gives $dS \propto u^{n-1} du$,
and with $s=-S_0 u$ (where $S_0=\kappa I_0$ is the on-axis maximum shift) the
signal-weighted shift distribution is

$$\boxed{\ f(s) \propto |s|^{n-1}\quad\text{on}\quad s\in[-S_0,0]\ }$$

For $n=2$ this is the triangular **ramp** $f(s)=2|s|/S_0^2$.

**This relation is not new, and the note should not be read as claiming it.**
It reduces exactly to Eq. (5.3) of the 1980 review of Delone, Kovarskii,
Masalov and Perel'man ([delone1980](lit/delone1980.md)) once the geometric
intensity distribution of a Gaussian beam, $P(I) \propto 1/I$, is substituted
into their general result. The reduction was checked against the shipped
`stark_ramp` implementation and agrees to $7\times10^{-12}$. Their review also
already contains the lineshape as a map of the shift distribution, the $F^k$
intensity weighting for $k$-photon excitation, and the asymmetric
shift-dominated limit. The full delineation is `docs/LITERATURE.md` §5.2a.

What is claimable is the evaluation rather than the relation. Delone's $P$ is
the statistics of a fluctuating field, unknown a priori, so their integral
stays formal. In a focused beam the distribution is fixed by **geometry**, the
integral closes, and the moments follow by direct integration:

$$\langle s\rangle = -\tfrac{2}{3}S_0,\qquad
\mathrm{Var}(s) = \tfrac{1}{18}S_0^2,\qquad
\kappa_3 = +\tfrac{1}{135}S_0^3$$

so the ramp's intrinsic standardised skewness is the pure number

$$g_1 = \frac{\kappa_3}{\mathrm{Var}^{3/2}} = \frac{18^{3/2}}{135} \approx +0.566$$

independent of $S_0$. It is a property of the ramp component's shape and a
diagnostic, not a standardised skewness of the observed line, which is
ill-defined (see §3).

**The law is general in $n$, and the next rung up is worth naming** (added
2026-08-09 when a one-colour three-photon target entered the future programme,
`FUTURE_TRANSITIONS_titsapph.md` §3.5). Direct integration of
$f(s)\propto|s|^{n-1}$ gives

$$\langle s\rangle=-\frac{n}{n+1}S_0,\qquad
\mathrm{Var}(s)=\frac{n}{(n+1)^2(n+2)}S_0^2,\qquad
g_1=+\frac{2(n-1)}{n+3}\sqrt{\frac{n+2}{n}}$$

The sign is positive because the substitution $u=-s/S_0$ maps the density onto
a Beta distribution with parameters $(n,1)$ on the unit interval, whose own skew
is negative, and the reflection
$s=-S_0u$ flips it. The magnitude rises with $n$: zero at $n=1$, 0.566 at $n=2$, and 0.861 at
$n=3$, where the distribution is the parabola $f(s)=3s^2/S_0^3$ with
$\langle s\rangle=-\tfrac34 S_0$ and $\mathrm{Var}=\tfrac{3}{80}S_0^2$. So a
three-photon rung would carry a shape asymmetry 1.52 times this one's on a
relatively tighter distribution, which is the reason to want it. The moment
machinery already accepts the photon order, and
`tests/test_lineshape.py` pins $n=1$, 2 and 3. The one-photon case $n=1$, a Stark-induced forbidden line
for instance, gives the uniform distribution, $\langle s\rangle=-S_0/2$ and
$\kappa_3=0$, exactly zero skew. The skewness observable therefore exists *only
because the two-photon rate goes as $I^2$*, which is the sharpest statement of
what is specific here.

**The three-photon case costs more than that paragraph makes it sound**
(added 2026-08-10). A three-photon Rabi frequency goes as $I^{3/2}$ while a
light shift goes as $I$, so the ratio of rate to shift is fixed by the atom and
not by a knob, and the near resonance that makes such a rate viable at all is
the same small denominator that makes the shift large. Computed from published
elements, the target's own shift reaches its natural width at a fifth of the
intensity this experiment already runs. So the parabola is real but it does not
arrive as a delicate asymmetry on a natural-width line: it arrives in the
cliff regime, where the shift greatly exceeds the linewidth. That is a
legitimate measurement of a shift and a poor one of anything needing a narrow
line. `FUTURE_TRANSITIONS_titsapph.md` section 3.5 carries the numbers.

### 2.0a The exponent is a weak-field statement, and the dataset is near its edge

![the weak-field limit and what leaving it costs the predicted skewness](../figures/fig24_weak_field_limit.png)

*The whole section in one picture. On the left, the weight the atom actually
carries against the square law that replaces it, with the dataset and the
proposed tight focus marked. The two markers are a fourfold change in waist,
which is a 256-fold change in the saturation parameter against a 16-fold change
in the shift, because one goes as the fourth power of the inverse waist and the
other only as the second. On the right, what that does to the observable the
tight focus is wanted for. The flip in the sign of $g_1$ there is not a
saturation effect at all: it is the axial average over the collection window
crossing $Z_c/z_R\approx1.12$, which the right panel already carries, and the
saturated weight moves how much of the beam contributes rather than where the
crossing sits. So the sign survives and the magnitude does not.*

Everything above takes the signal weight to be exactly $I^{n}$. That is the
first Born-order rate, and it holds while the drive is weak. Once the
saturation parameter $s=2\Omega^2/\Gamma^2$ is not negligible the per-atom
weight is the steady-state excited fraction $(s/2)/(1+s)$, whose logarithmic
slope in intensity falls below $n$, and **the whole family above moves with it**:
$g_1$ shrinks toward its $n=1$ value of zero.

This matters because $s$ scales as the fourth power of the inverse waist. At
the dataset's measured 64 µm and 225 mW it is 0.033, so the weak-field law is
good to a per cent and nothing here is affected. At the 16 µm the fixed-lock
session proposes it is 8.5, and integrating the moments with the saturated
weight instead moves the predicted axial skew from $-0.36$ to $-1.07$. So the
committed axial machinery, which takes an integer photon order, is being asked
a question outside its range at exactly the configuration that was chosen to
make the skew large.

The recorded results are unaffected and the design conclusion is not.
[notes/running_wave_and_waist_design.md](notes/running_wave_and_waist_design.md)
carries the table and what the machinery needs before that waist is chosen
deliberately.

The same $dS\propto dI/I \cdot I^{n}$ argument holds for any monotonic $I$
profile that is flat in one coordinate, including the exponential evanescent
field of a nanofibre. That is the bridge to the fibre geometry of the proposed
extension.

### 2.1 Does the atoms' motion wash the ramp out? (M19)

The derivation above is quasi-static. Each atom sits at one intensity and
carries one shift. Real atoms cross the beam, sweeping their own shift from
zero to the on-axis maximum and back within a transit time (about 0.2 µs at
$w_0\approx 64$ µm) that is only a few times the natural response
$1/\Gamma\approx 45$ ns. [Camparo and Lambropoulos](lit/camparo1992.md) (*JOSA
B* **9**, 2163 (1992)) show for a two-photon transition in a fluctuating field
that this ratio decides the answer. Slowly-varying intensity gives an
asymmetric line, rapidly-varying intensity averages to a symmetric one at the
mean shift. So a composite model convolving a static ramp with a transit
lineshape needs a justification rather than an assumption, because the two
factors describe the same atom crossing the same beam.

**It survives, and the reason is a change of variables.** An atom's impact
parameter $b$ and its displacement $vt$ along the flight direction *are* the
transverse plane, and $\mathrm{d}b\mathrm{d}(vt)$ *is* the area element. A
uniform-density ensemble weighted by crossing flux therefore samples exactly
the spatial measure the static derivation integrates over. Motion re-labels
which atom carries which shift without changing the distribution over shifts.

That argument still assumes the atom's spectrum reflects the shifts it samples,
which is the very quasi-static step at issue. **M19** (`rb5s6s/ramp_transit.py`)
checks it without that assumption, propagating the weak-excitation amplitude
with the phase integrated along each trajectory. The static triangle's first
two moments are recovered to $\sim0.1$% across $S_0/\mathrm{transit\ FWHM}$
from $0.09$ to $7.6$, from far inside the non-adiabatic regime to far inside
the adiabatic one. The first-moment invariance is in fact exact for any
modulation, since the mean of a power spectrum is the coupling-weighted mean
instantaneous frequency. The second moment is the substantive check, and it is
what licenses the convolution.

The real geometry adds two more complications, and the pull survives both. The
beam is retro-reflected, so it is a standing wave whose $\lambda/2$ fringes
modulate the shift, and the atoms carry a thermal spread of speeds rather than
one speed.

- *Standing wave.* The fringe modulates the **shift**, which follows the total
  $|E_+ + E_-|^2$ over the full fringe period, but not the **coupling**. The
  Doppler-free rate takes one photon from each counter-propagating beam, so it
  goes as $I_+I_-$ and is $z$-uniform. M19 recovers the triangle in both
  limits, fringes swept fast by an axial atom (about 113 per transit, the
  experiment's 0.56 GHz against a 5 MHz transit rate) and the frozen fringe of
  a near-transverse atom sampled over the node-to-antinode arcsine. That
  independently confirms the fringe-immunity of the **mean** asserted in
  `constants`. The fringe's suppression of the **skew** is a different and
  non-null question, quantified separately in M15.
- *Maxwell-Boltzmann.* Only the ratio $S_0/(v/w)$ enters, so the sweep above is
  itself a sweep over transverse speed spanning about 80 times, bracketing the
  thermal distribution. Every speed class shares one mean and one ramp
  variance and differs only in transit width, so any mixture inherits both.
  Checked directly against a flux-weighted Maxwell-Boltzmann sample.

The third cumulant, the one the asymmetry claim rests on, is **not** resolved
by that simulation, because the FFT noise floor weighted by $\nu^3$ swamps it.
For $\kappa_3$ the change-of-variables argument stands alone, and it carries
the quasi-static assumption. The fringe's effect on $\kappa_3$ is M15's result,
not this one's.

![the ramp construction](../figures/fig12_ramp_construction.png)

*From a Gaussian beam to a triangular shift distribution. A focused beam does not
apply one light shift, it applies a distribution of them. (a) the intensity
profile sets each atom's shift, from zero at the dim edge to $-S_0$ on axis, with
radius in units of the beam radius $w$ at which the intensity has fallen to
$1/e^2$ of its on-axis value. (b) the two weights that compete, many atoms sit at
low intensity but each contributes only $I^2$ of signal, and the product is
linear in $u$. (c) hence $f(s)\propto|s|$, a triangle with mean
$-\tfrac{2}{3}S_0$ and intrinsic skew $+0.566$, which exists at all only because
the rate goes as $I^2$, drawn as a density normalised to unit area. (d) the line
it produces, drawn at $S_0=3$ MHz so the asymmetry is visible.*

## 3. The drift-immune method

The 2025 recorded line walked at the MHz scale between scans, with hand
re-centrings riding a held-lock drift bounded at order 0.02 MHz/min on the
laser axis, sign undetermined (`APPARATUS.md` §6). Absolute line **centres**
are therefore dead, and a fit must give each scan its own free centre to absorb
that motion.

That has a sharp consequence for the ramp. Its first-order effect is a shift of
the line, the centroid pull $-\tfrac23 S_0$, and a shift is exactly what a
per-scan free centre absorbs. In the drifted dataset the pull is degenerate
with the drift and is not a usable handle on $S_0$. What survives is the ramp's
**shape asymmetry**, which no free centre can absorb because it is not a
translation. That is the drift-immune observable and the methodologically
specific point (§6). The light shift is read from a drift-invariant *shape*,
not from a line position the drift has destroyed.

The extraction is a **model fit, not a moment computation**. The full lineshape
(ramp $\otimes$ symmetric core) is fit with a per-trace free centre and a
shared **asymmetry coefficient**, the amplitude of the ramp skew, equivalently
$S_0$. Computed from the fitted function rather than the raw trace it stays
finite and window-independent, and the Lorentzian wings that make a raw-data
skewness divergent never enter. The residual systematic is then
core-model-dependence. The fitted asymmetry depends on the assumed core, and a
wrong core (Voigt where the truth is Voigt $\otimes$ transit-cusp) exchanges
against it. Unlike raw-moment window-dependence, that is *checkable*, by BIC
and the M8 cusp fit.

**Why the asymmetry is identified while the width is not.** The drift argument
above is about *translations*, and a per-scan free centre absorbs a shift but
cannot absorb a shape change. A second and independent argument is about *the
other broadeners*, and it is what makes the fit identifiable at all. The model
core is a convolution of components that are symmetric by construction, the
natural and collisional Lorentzian, the laser kernel and the transit kernel
(two-sided exponential or Gaussian, `lineshape.composite_profile`). A symmetric
component cannot produce asymmetry at any width. The ramp is the *only*
asymmetric factor in the model, so the fitted asymmetry coefficient does not
exchange against $\Gamma_{\rm nat}$, $\gamma_{\rm coll}$, $\sigma_{\rm laser}$ or
the transit width, which is the four-way degeneracy that dominates the width
channel and that M9 and M4c work on. (Stated as symmetry rather
than as $\kappa_3 = 0$. Cumulants are additive under convolution and vanish for
symmetric factors, but a Lorentzian has no finite third moment, so symmetry is
the property the fit actually uses. This is the same reason the extraction is a
model fit rather than a raw-moment computation.)

The exposure that remains is therefore narrow and named. It is an asymmetric
error in the assumed core, not a mis-estimated symmetric width. That is the
core-model dependence above, and it is checkable by BIC and the M8 cusp fit,
which is why those exist.

**And the width channel is not merely worse, it is blind.** At the campaign's
maximum 225 mW with the measured $w_0 = 64$ µm prior, `stark_shift_S0_mhz` gives
$S_0 = 0.348$ MHz, so the ramp kernel is 0.20 MHz FWHM. Added in quadrature to
the observed 5.2 MHz line that is **0.004 MHz** of extra width, a part in 1400,
far below the width budget's own systematics. No width measurement of any
precision reaches this signal. The asymmetry channel is not a refinement of the
width channel but the only channel there is. Calculated 2026-07-30, requoted
2026-08-02 at the measured waist.

The reference moments the fit encodes,

$$\text{centroid pull} = -\tfrac{2}{3}S_0,\qquad
\kappa_3^{\text{ramp}} = +\tfrac{1}{135}S_0^3$$

order the signal by statistical cost: pull $\propto P$, excess variance
$\propto P^2$, skew $\propto P^3$, the last vanishing unless $n=2$, the $I^2$
signature. The pull as a *measurement* becomes available only once a stable
lock un-absorbs it.

**Two caveats on the drift.** *Between*-scan drift is absorbed exactly by the
free centres. *Within*-scan drift is not a pure translation. It smears the line
asymmetrically in a scan-direction-dependent way that couples the fitted centre
to the fitted asymmetry. At the established $\lesssim0.1$ MHz within-scan drift
this is small, but because the asymmetry is itself small it must be
*estimated*, not assumed zero. A synthetic closure test now bounds it rather
than the timescale argument alone (`tests/test_intrascan_drift.py`). The drift
is injected into a synthetic scan and the asymmetry recovered through the same
free-centre fit, so the linear sweep warp lands in the fitted width and only
the residual curvature can skew. At the dataset's within-scan drift the fitted
ramp coefficient shifts by well under a fifth of its SNR-limited statistical
error, a few $\times 10^{-3}$ on $S_0$ for the dominant linear part, and
reaches order $S_0$ only at tens of times the dataset's rate. The within-scan
skew is therefore bounded and small, not unmodelled.

**Status.** In the 2025 sweep the fitted asymmetry coefficient is consistent
with zero. At $\le225$ mW its significance (the skew grows only as $S_0^3$)
sits below the SNR $\approx130$ floor, so the estimator, correct as it is,
returns an **upper bound, not a detection**. A fit always returns *some* value
with an error bar, and the discipline is to report a bound unless it clears
that bar, which at the dataset's intensity it does not.

A fixed-lock session would change this two ways. The fixed lock would recover
the first-order pull ($-\tfrac23 S_0 \propto P$, a shift of order MHz against a
stable reference, and the primary $S_0$ measurement once it is no longer
absorbed by a free centre). The small waist, where $S_0$ would be about
16 times larger, would lift the shape asymmetry into a detection, though not by
the naive $S_0^3$ cube of that gain, because the axial average changes the
third cumulant's magnitude and, for a long enough collection window, its sign
(§7). Both are conditional on the small-waist skew corrections, the
beam-divergence collection average of §7 (the larger, sign-flipping one) and
the standing-wave fringe-resolved tail of §5 (same-sign, and fit jointly with
it). Those move the ramp form, and the pull coefficient off $-\tfrac23$, at
small waist, and must be applied before $S_0$, hence $\Delta\alpha$, is read.

**The hybrid, made principled.** The three cumulants are not three rival
measurements to be combined or cherry-picked. They are three analytic
functionals of the *one* parameter $S_0(P)$
(`lineshape.ramp_moment_contributions`): pull $\propto S_0$, excess variance
$\propto S_0^2$, third cumulant $\propto S_0^3$. A fixed-lock fit would use a
single $S_0$ per condition and check that the pull, excess-variance and
third-cumulant *measured from the data* are mutually consistent with it, a
$\chi^2$ across the moment hierarchy. The primary observable at each intensity
is pre-registered as the lowest-order moment above its own noise floor (the
pull where $S_0$ is small, the skew only where $P^3$ has climbed clear of
noise), and the others are consistency checks with their own error bars. A
spurious asymmetry from a fit artifact or from the diverging-beam geometry will
not *also* reproduce the correct, more-robust lower-order pull and variance for
the same $S_0$. So the claim is never "we measured the skew" but "pull,
variance and skew are jointly consistent with one triangular ramp of amplitude
$S_0(P)$". The extraction stays single: one fitted profile per condition and
three functionals of it, never several estimators of one moment.

## 4. What the dataset returns

At fixed density the dataset tests the *convention-free* content, and is
consistent with it. Across a $9\times$ power sweep the linewidth is flat to
$\lesssim2$% (the ramp adds variance $\propto S_0^2$, negligible against the
5 MHz budget), and the amplitude scales approximately but **not exactly** as $P^{2}$
(log-log slopes 1.83 to 2.12, of which three of four exclude 2 under a
block bootstrap. The departure replicates in an independent session, is
invariant under ladder direction, and is ordered by line brightness rather
than by any atomic quantity, so it belongs to the detection rather than to
the transition). The asymmetry is predicted below the dataset's noise and is not detected,
as designed.

That flatness is not merely a null. Fitting one shared $S_0=\kappa P$ to the
four peaks' width-against-power (`stark.fit_stark_sweep`, M4e) turns it into a
quantitative upper bound of $0.64$ MHz on $S_0$ at 225 mW (95%, profile
likelihood). The fitted value is consistent with zero, so the dataset
*brackets* the predicted $0.35$ MHz (§5) without resolving it. It is a bound
for the same two-epoch reason as everything else here. The drifted lock
destroys the centres, the pull $\propto S_0$ is absorbed by each trace's free
centre, and only the ramp's $\propto S_0^2$ width broadening survives (a
$0.6$ MHz $S_0$ inflates a $5$ MHz line by less than $0.1$ MHz).

M23 (`run_stark_joint`) tightens the same channel to $S_0(225\ \text{mW})$ below 0.26 MHz
by fitting every point of every profile across the sessions instead of 20
summary widths. The 20-summary-width construction is kept as the independent
simpler bracket, so there are two constructions of one physical channel and
still no second channel to corroborate it.

**The centre channel gives no bound either** (M21,
`scripts/run_stark_centres.py`). A peak position is a frequency only within a
*display epoch*, a run of unchanged scope horizontal position, so each epoch
carries a free offset, and of the 26 epochs covering the power sweep only three
contrast two powers, none spanning two lines. The pull is then unidentifiable
rather than imprecise. Its sign reverses between drift models ($+3.44$ against
$-3.25$ MHz/W) and the limit degrades as the drift model gains freedom,
$|S_0(225\ \text{mW})|$ below $9.49$, $14.57$, $17.65$ MHz for linear, one-exponential and
two-exponential drift. Tagged NULL. Earlier versions of this bound ($3.5$ MHz
in addendum 6, $5.4$ MHz under addendum 7's mixture, $7.3$ MHz in M20) were
tighter only because they differenced centres across horizontal-position moves,
and are withdrawn. The width-and-shape channel is the dataset's only
light-shift channel.

That was re-examined in full on 2026-08-10, since the centre carries the pull
linearly and is worth several tries. It cannot be recovered from this dataset,
and each session refuses for its own reason. The campaign's three multi-power
epochs run strictly downward in power with time, so drift and pull share one
regression column. The campaign-morning session's power order *is* scrambled
and would forecast 0.87 MHz/W, but its window setting moves at exactly the
transition carrying the lever, which projects to a frame systematic eleven
times the statistical error. And the 4 July evening session, whose
alternating ladders are the design the campaign lacked, cannot fix its own
frequency origin, because each 5 s record contains one crossing of the line
and not the mirror pair a self-referenced apex would need.
Every obstruction is the same shape, no frequency reference independent of the
knobs, which promotes the unexported ramp-monitor channel from a convenience to
the precondition for this channel existing.
[notes/centre_channel_cannot_be_revived.md](notes/centre_channel_cannot_be_revived.md)
carries the forecasts and the arithmetic.

Through the §5 convention the M23 bound maps to a $\Delta\alpha$ bracket below
the computed $1093$ at the measured $w_0=64$ µm, so the dataset constrains
the $(\Delta\alpha,\ \text{intensity})$ pair rather than either alone. The
prior is now the lineage measurement itself (§5), a direct test rather than an
inference pointing at an external number. Two documented effects push the
*effective* intensity below even that prior: residual clipping at the 3 mm EOM
aperture, and imperfect superposition of the retro beam. The replaced
readings of this bracket (271 a.u. at the old 50 µm prior, about 1200 from the
width-only bound, about 5800 from a Wald interval with no coverage at the rail)
live in the audit record. The dataset does not adjudicate $\Delta\alpha$
itself, since the mapping inherits $w_0$. A fixed lock would measure the pull
$\propto S_0$ directly at a small waist, turning this bracket into the
coefficient.

### 4.1 The width channel has two companions with the same power signature

![the hyperfine branch, how often it fires, and the three terms it competes with](../figures/fig23_hyperfine_pumping.png)

*The second companion is the one that needs a picture. Every real 6S decay
cascades through 5P, and the 5P decay does not preserve $F$, so an atom that
decays mid-crossing can land in the other ground state. It is then off
resonance by the ground hyperfine splitting, which this dataset resolves as two
of its own four lines, so the branch is an exit rather than a detuning. The
middle panel is how often that happens on one crossing. The right panel is the
point of the section: of the three terms that grow as the square of the power,
the one the bound is built on is the smallest.*

Added 2026-08-10, and it bears on how both bounds above should be read. The
ramp broadens the line as $S_0^2\propto P^2$, which is the signature the width
fit attributes to the light shift. **Two other effects carry the identical
$P^2$ signature and were absent from the forward model.**

*Power broadening.* The two-photon Rabi frequency is 450 kHz at the campaign
maximum, which the repository had never computed, giving a saturation parameter
$s=2\Omega^2/\Gamma^2$ of 0.033 on axis. The homogeneous width then goes as
$\Gamma\sqrt{1+s}$. At the predicted $S_0$ the ramp contributes 6.6 kHz where
saturation contributes 24 to 25 kHz, so **the companion is the larger term by
about 3.7**, and $s\propto I^2\propto P^2$ makes the two degenerate at this
order.

*Hyperfine pumping.* The excited state cascades through $5P$, whose decay does
not preserve $F$, so an atom that cycles during its transit can land in the
other ground hyperfine level and leave the resonance 3 GHz behind. Eight to
fifteen per cent of transiting atoms decay at least once, the ends being the
signal-weighted average and the on-axis value, and the smaller 2 to 6 per cent
of them land in the other level and are actually lost. In the weak-drive
limit the added width is **exactly the branching fraction times the saturation
width**, everything else cancelling because $\Gamma_{6S}/2\pi$ *is*
$\Gamma_\text{FWHM}$, which takes the companion-to-ramp ratio to 4.9–6.2. The
two-level saturation law assumes a closed system. This is the correction for
its being open.

**The direction is favourable, which is why no bound moves.** If the observed
$P^2$ broadening is mostly companion rather than ramp, the true limit on the
Stark coefficient is *tighter* than quoted. Adding the saturation term to the
forward model and re-profiling confirms it: the width-only bound moves from
0.6325 to about 0.23 MHz, and the joint bound from 0.258 to 0.117, factors of
2.8 and 2.21. The joint fit moves less, as predicted in advance, because its
collisional-width prior absorbs part of an added Lorentzian width.

Both committed bounds therefore stand as quoted and are now known to be
**conservative by a measured factor rather than by argument**. They do not move
because the injected law is the two-level homogeneous form used with a
two-photon Rabi frequency: standard, and the steady-state condition holds here
since the beam chord is about ten natural lifetimes, but an approximation
rather than a derivation for a two-photon transition.
[notes/two_photon_saturation_companion.md](notes/two_photon_saturation_companion.md)
carries the derivation, the probe and what it does not license.

**And the degeneracy is complete in both of the width channel's continuous
knobs, which is why no sweep can break it.** All three terms grow as $P^2$, and all three
also grow as the inverse fourth power of the waist: the ramp because its width
increment goes as $S_0^2$ and $S_0$ goes as $w_0^{-2}$, the companions because
$s$ carries $\Omega^2$ and $\Omega$ is two-photon. So neither a power sweep
nor a change of focus can separate them, and the dataset's inability to do so
is structural rather than a matter of statistics. What does separate them is a
channel the companions do not feed: they broaden the line without moving it,
while the ramp pulls the centroid by $\tfrac23 S_0$. That channel is the
centroid pull, and reaching it is the fixed lock's job, which is the same
conclusion §3 reaches from the other direction.

**There is a second separator, and it is a discrete one (2026-08-10).** The
ramp and the saturation are identical on all four dataset lines, because the
two-photon Rabi frequency is $F$-independent here and the hyperfine factor is
exactly 1 (`constants.ABUNDANCE_RB85`). The pumping is not. Its branching is
the branching of the cascade into the ground level not being driven. Because
the two-photon operator is scalar, 6S sits in one hyperfine level, so this is a
two-step product rather than a degeneracy weight, and each leg scales that
weight by a clean fraction:

$$f = \frac{2F'+1}{\sum_F (2F+1)}\left(\tfrac89 b_{1/2}+\tfrac49 b_{3/2}\right)
= 0.372,\ 0.348,\ 0.248,\ 0.223
\ \text{ for } 993.4121,\ 4154,\ 4192,\ 4207\ \text{nm}$$

with $b$ the two legs' branching, 0.341 and 0.659, and the bracket evaluating to
0.596 for every line. The $8/9$ and $4/9$ are not an averaging over hyperfine
structure, and the obvious objection is worth answering here rather than leaving
to the reader: every line feeds one $5P_{3/2}$ level that cannot decay to the
undriven ground level at all, since a $J=1$ photon cannot change $F$ by two, and
those levels differ per line ($F=0,1,4,3$ across 4121, 4154, 4192, 4207) and
carry between 0.17 and 0.70 of that leg. They are in the calculation, and they
cancel against the enhanced paths exactly. The reason is that a spontaneous
decay evolves the density matrix as $\rho\to\sum_q D_q\rho D_q^\dagger$, which
is basis-free, and neither dipole operator touches the nucleus, so evaluating it
in $|m_J,m_I\rangle$ makes the nuclear spin a spectator and the leg ratio
reduces to $2(1-p)$ with $p$ the purely electronic non-flip probability, $5/9$
and $7/9$. **A sum of probabilities over an intermediate basis is not itself
basis-free**, so that argument does not on its own license the hyperfine sum.
What does is that the $5P$ hyperfine splitting far exceeds the linewidth, so
those coherences dephase, and that the prepared state is unpolarised, so the
$m$ coherences are absent. Neither has to be taken on trust: check 7 of
`scripts/run_zeeman_depletion.py` runs the full density matrix with every
coherence kept, in exact rationals, and lands on the same $8/9$ and $4/9$ in all
eight cases. Check 6 prints the cascade resolved by intermediate $F$.

![the cascade resolved by intermediate F, and the sum rule](../figures/fig28_cascade_resolved.png)

*The objection and the answer in one figure. On the left, one line's cascade
resolved by intermediate $F$: the level fed with 0.17 of that leg loses none of
it, because it cannot reach the undriven ground level at all. On the right, why
that leaves no per-line correction behind: the individual intermediate
contributions scatter from 0 to 0.67 and their sums land on exactly two values,
for all four lines and both isotopes.*

So the pumping companion carries a per-line signature that
neither of the other two has, a lever of 1.67 between the extreme lines. In this
dataset it is 3.1 kHz of width at the committed $S_0(225)$ bound of 0.217 MHz,
rising to 4.4 kHz at the joint bound and 7.8 kHz at the predicted $S_0$, against
an 88 kHz single-block scatter. It cannot be spent at any of the three. It is stated because it is the only separation found that does not require
a lock, and because it retires the $1/3$ to $2/3$ bracket §4.1 was carrying,
downward: the lower two lines fall below that bracket.

The separation was preregistered and run, and it returns **less than the
scatter argument predicts**. Comparing the lever against 88 kHz treats $S_0$ as
though it sat at one of those three values. It does not. This dataset bounds
$S_0$ from above, zero is inside the bound, and the companion is proportional to
it, so a fit that is free to choose sets $S_0$ to zero and switches the
companion off. The scale it multiplies is then unidentifiable rather than
loosely bounded, and $\chi^2$ is flat along its axis to four decimals. The
factor of thirty is real, and it is not the binding constraint. See the
[postscript to the refit's preregistration](notes/companion_inclusive_refit_prereg.md).

## 5. The coefficient (the field-intensity convention, pinned)

The shape and centred moments above are convention-free. The **magnitude** of
$S_0$, needed to turn a measured pull into a differential polarizability
$\Delta\alpha = \alpha_{6S}-\alpha_{5S}$ or to predict $S_0$ from a computed
$\Delta\alpha$, requires fixing the $\langle E^2\rangle$ convention. We adopt
the standard AMO one ([Grimm, Weidemüller &
Ovchinnikov](lit/grimm2000.md), *Adv. At. Mol. Opt. Phys.* **42**, 95 (2000),
and [Steck](lit/steck_rb.md)): for a real field $E(t)=E_0\cos(\omega t)$ the time
average is $\langle E^2\rangle = E_0^2/2$, and

$$\Delta E_i = -\tfrac{1}{2}\alpha_i\langle E^2\rangle
= -\tfrac{1}{4}\alpha_i E_0^2
= -\frac{\alpha_i I}{2\varepsilon_0 c}$$

$$\boxed{\ S_0 = \frac{\Delta\alpha\ I_{\text{eff}}}{2\varepsilon_0 c h},\qquad
I_{\text{eff}} = (1+\rho)\frac{2P}{\pi w_0^2}\ }$$

Here $I_{\text{eff}}$ is the time-averaged on-axis intensity of the forward
plus retro beams and $\rho$ is the retro power ratio. Code:
`lineshape.stark_shift_S0_mhz`.

**No coherent standing-wave enhancement, and why.** A *fast-axial* atom crosses
the $\lambda/2$ fringes at $2v_z/\lambda\sim0.56$ GHz (mean axial speed) while
the shift depth is $\lesssim1$ MHz, so its frequency-modulation index is about
$2\times10^{-3}$. In [Stalnaker](lit/stalnaker2006.md)'s FM framework (*Phys.
Rev. A* **73**, 043416 (2006), Sec. IV) the small-modulation-index limit puts
the carrier at the fringe-*mean* intensity, so $I_{\text{eff}}$ **is** that
standing-wave mean and the pull is exactly fringe-immune. There is no factor of
two to add.

**The fringe-resolved tail suppresses the skew.** The line is Doppler-free over
**all** $v_z$, so near-transverse atoms sit at a frozen fringe and sample the
node-to-antinode arcsine. That is a fringe-resolved tail (weight
$f_\text{res}$) which keeps the mean but, because the fringe *multiplies* the
shift $s\to s(1+x)$ with $x$ arcsine, suppresses the ramp skew:
$\kappa_3\to S_0^3(1/135-f_\text{res}/10)$ at $\rho=1$, a $-13.5 f_\text{res}$
fractional leverage $\propto$ contrast², of which only
$P=f_\text{res}\sigma_x^2$ is observable. Measured as the change in standardized
skew over the intrinsic +0.566 of the triangle, it is negligible at $w_0=64$ µm
(≈7–14% of an already-below-noise skew, `results/fringe_tail.csv`, whose
7–14% spread is the open coherence-window choice, not Monte-Carlo noise: the
block-to-block error on the underlying standardized skew, `d_skew_mc_err` in
the same file, is 2 to 4% of the value it accompanies) and
≈26–28% at 16 µm, where it is same-sign-additive to the larger §7
divergence correction, so the two must be fit jointly at small waist
(quantified and coherence-window-bracketed in `fringe_tail`).

**The predicted magnitude.** With $\Delta\alpha = 1093$ a.u. ([Orson *et
al.*](lit/orson2021.md) 2021, sourced below) this gives $S_0 = 0.35$ MHz
(transition) at $P=225$ mW, $w_0=64$ µm, $\rho=0.94$. It grows to $5.6$ MHz
at $w_0=16$ µm, which is why a small waist would lift the ramp asymmetry to
a detection, though *not* by the on-axis $S_0^3$ cube of the intensity gain,
since the axial average over the collection window changes the third cumulant's
magnitude and, past $Z_c/z_R\approx1.12$, its sign (§7).

**Sign, and provenance.** The $\langle E^2\rangle$ convention is magnitude-only.
The *direction* of the pull is set by $\mathrm{sign}(\Delta\alpha)$, and
$\Delta\alpha$ is [Orson *et al.*](lit/orson2021.md) 2021's published value
(*J. Phys. B* **54**, 175001, prior art on this exact 5S–6S line). They compute
$\alpha_{56}=\alpha_{5S}-\alpha_{6S}=-1093$ a.u. "in a manner similar to
[Martin 2019](lit/martin2019.md)", so our
$\Delta\alpha=\alpha_{6S}-\alpha_{5S} =+1093$ is positive (6S pulled down more
than 5S, hence red shift, hence positive $S_0$). This was formerly flagged as
the number most wanting a theorist's check. It is now (a) a **cited** value on
our exact
transition and (b) **cross-checked**, in that our `stark_shift_S0_mhz`
reproduces Orson's own $-0.66$ MHz shift prediction (0.8 W, 63 µm) to the digit
(`test_stark_S0_reproduces_orson2021`).

**The independent recompute now exists in-repo** (`rb5s6s/polarizability.py`,
M16), a sum-over-states model from Safronova-lineage matrix elements. Two of
its three anchors are held out and one is not, and the distinction is worth
making rather than blurring. Held out, and therefore evidence: it reproduces
the *measured* 5S scalar tune-out 790.032326(32) nm to $\approx1.6$ pm, and
the measured static $\alpha_{5S}=318.79(1.42)$. Not held out: the model also
returns the Safronova-group static $\alpha_{6S}=5167(22)$, but its 6S tail term
is *fixed by* that value (`TAIL_6S` in `rb5s6s/polarizability.py`, and
`results/polarizability.csv` records the row as tail-calibrated), so the
agreement there is arithmetic rather than a test. It **confirms the
magnitude**,
$|\Delta\alpha(993)| = 1145$ a.u., within 5% of Orson's 1093, **but finds the
opposite sign**: $\alpha_{6S}(993)\approx-312$ a.u., because the dominant 6S
couplings, 6S–6P at 2.73 and 2.79 µm, are driven far blue-detuned at 993 nm and
push 6S *up* while 5S is pushed *down*.

The per-line breakdown is worth printing, because the one-line story above names
only the largest term and the runner-up is not the one a reader would guess.
Computed line by line through `polarizability._alpha` (2026-08-09): the 5P pair
contributes $+214.6$ and $+409.5$ a.u., positive because 6S–5P runs *downward*.
The 6P pair gives $-279.8$ and $-567.0$, the 7P pair $-13.2$ and $-32.4$, and the
8P pair $-15.3$ and $-41.2$, for a line sum of $-324.7$ and $-312.2$ after tail
and core. So the 8P pair, at $-56.5$ a.u., is **18% of $\alpha_{6S}$ and the second
largest upward group**, ahead of 7P. The reason is that 993 nm sits only
345 cm^-1 blue of the *real* 6S–8P3/2 transition at 1028.67 nm, which is the
closest real coupling this field has to 6S, 6.8 times closer than 7P and
18.8 times closer than 6P. Proximity still loses: the 8P matrix elements are
about twenty times smaller than 6P's and enter squared.

That matters for two questions and settles both. It is why the 8P pair cannot
rescue Orson's sign, since a $1\sigma$ move of both 8P elements shifts
$\alpha_{6S}$ by 1.68 a.u. and the predicted coefficient by 0.15%. And it is
why 8P is worth naming at all: it supplies 4.9% of the differential
$\Delta\alpha$ that sets the light shift, so it is a term to keep rather than a
term to neglect. Section 5.2 quantifies the rest of what a third 993 nm photon does.

So $\Delta\alpha=\alpha_{6S}-\alpha_{5S}$
is negative and the light shift of the transition is **blue**, not red. Every
recorded result is sign-immune (C3c is a symmetric null, and C3d and the
prediction band use $|\Delta\alpha|$), but the fixed-lock *pull direction*
and the ramp's stated side depend on it. The discrepancy with Orson's printed
$\alpha_{56}=-1093$ was **settled by the experimenter, who took this
record's value as the package value** and kept the published one named
beside it as `DELTA_ALPHA_AU_ORSON2021`. That is a decision on the theory and
not a measurement: the sign remains unset by experiment, and the decisive
check is still one line for a theorist, the sign of $\alpha_{6S}$ at 993 nm,
with the fixed-lock pull direction as the experiment that would settle it.

### 5.0 The sign dispute, and the adjudication that closed it

An external audit (2026-07-26) proposed that the whole Orson disagreement was
a convention artifact. It is not, but a careful reader did reach that
conclusion from the published material, so every definition is stated
explicitly before anything is compared:

| symbol | definition here | value at 993 nm |
|---|---|---|
| $\alpha_{5S}$, $\alpha_{6S}$ | scalar polarizability of each level | $+834$, $-312$ a.u. |
| $\Delta\alpha$ | $\alpha_{6S}-\alpha_{5S}$ (**excited minus ground**) | $-1145$ a.u. |
| $\alpha_{56}$ (Orson's) | $\alpha_{5S}-\alpha_{6S}$ (**ground minus excited**) | $=-\Delta\alpha$ |
| level shift | $\delta E = -\tfrac{1}{2}\alpha E^2$ | — |
| transition shift | $-\tfrac{1}{2}\Delta\alpha E^2 \equiv +\tfrac{1}{2}\alpha_{56}E^2$ | — |

The last row is the point: both conventions give the same formula, so the
algebra is not in dispute. Orson prints $\alpha_{56}=$ [-1093](lit/orson2021.md "ref:lit:orson2021:alpha_56_au"), hence a red
transition shift. This work computes $\Delta\alpha=-1145$, that is
$\alpha_{56}=+1145$, hence a blue one. Same equation, opposite input. Both
sides are verified from the typeset PDFs. Orson states the convention in
words, prints $\alpha_{56}=-1093$ a.u., repeats it in SI as
$-1.80\times10^{-38}$ J m² V⁻², and draws the consequence $\Delta f=-0.66$
MHz at his own $w_0=63$ µm, $P=0.8$ W. Feeding his numbers through this
repository's unit chain returns $-0.653$ MHz, so the disagreement is not a
units artifact: the same arithmetic on his input reproduces his output.

The magnitude pattern is itself diagnostic. The two computations differ by
~5% in magnitude with opposite sign. A genuine matrix-element disagreement
would have to move $\alpha_{6S}$ by ~2200 a.u. and then land within 5% of
the original magnitude by coincidence, whereas a global sign error, in either
work, produces exactly magnitude agreement with sign opposition. The same
literature demonstrably carries printed-sign faults: [Martin 2019](lit/martin2019.md)
quotes $+2.30$ in its abstract and Table ii against $-2.5$ in its Fig. 5
caption for the same coefficient, verified from the held PDF.

### 5.0.1 Where this work's sign is anchored

$\alpha_{5S}$ here is pinned by two measurements the model does not fit: the
static value ($+318.28$ computed against the measured $318.79(1.42)$) and the
5S tune-out wavelength ($790.0339$ nm computed against the measured
[790.032326(32)](lit/leonard2017.md "ref:lit:leonard2017:tuneout_nm"), [Leonard 2015](lit/leonard2015.md) as corrected by their
[2017 erratum](lit/leonard2017.md), both held). A positive ground-state
polarizability far below resonance is also required physically. Orson reports
only the difference, which cannot be checked this way.

$\alpha_{5S}(993)=+834$ a.u. is unanimous: 993 nm is red of every strong 5S
line, so every term is positive (D2 $+533$, D1 $+290$, the rest below $+2$). No
matrix-element revision can make it negative.

$\alpha_{6S}(993)=-312$ a.u. is a partial cancellation, and that is the
honest weak point:

| 6S transition | λ | direction | contribution (a.u.) |
|---|---|---|---|
| 6S–6P | 2732 nm | upward | **−566** |
| 6S–5P | 1367 nm | downward | **+409** |
| 6S–6P | 2791 nm | upward | **−280** |
| 6S–5P | 1324 nm | downward | **+214** |
| | | **net** | **−312** |

Summed over all terms: the upward group totals $-947$, the downward 5P
cascade $+623$, the lines give $-324$, and the tail and core carry it to
$-312$. The negative total survives by about a third of the larger group, so
the sign is sensitive to the balance: raising the 6S–5P (1367 nm) strength by
33%, or lowering the 6S–6P (2732 nm) strength by 95%, drives $\alpha_{6S}$
through zero. That makes the disagreement a specific, answerable question
about two reduced matrix elements, not a bare contradiction. Both values are
committed (`results/polarizability.csv`) and the margins are
regression-guarded (`test_the_993_sign_and_its_margin`).

### 5.0.2 The lifetime discriminant

This answers the fair question of how we know the sign error is not ours. The
upward 6S–6P group's sign is structural: at 993 nm the drive sits above the
2732 nm resonance, so every one of those denominators is negative. Orson's
$\alpha_{56}=-1093$ therefore requires $\alpha_{6S}=+1925$, which the
downward 6S–5P cascade could only supply by growing from $+624$ to $+2874$: a
factor 4.6 in $\alpha$, hence $\times2.15$ in the dipole elements.

Those same elements set the 6S lifetime. Unscaled they give **45.42 ns**
against the measured **[45.57(17)](lit/gomez2005.md "ref:lit:gomez2005:tau_6s_ns") ns** ([Gomez 2005](lit/gomez2005.md)), a
0.9σ agreement. Scaled to reach Orson's sign they give **9.9 ns**, about
**210σ** from the measurement. Held as a permanent test
(`test_orsons_sign_would_require_an_excluded_6S_lifetime`).

### 5.0.3 A candidate mechanism, offered as hypothesis

Orson writes that he calculated "in a manner similar to that of Martin et
al." Martin's Eqs. (2) and (21) as printed carry a leading minus,
$\alpha(\omega,J)=-\frac{2}{3(2J+1)}\sum\ldots$, which would make a
ground state below resonance negatively polarizable. If that minus
propagated, the published $-1093$ would be the negative of what the method
gives, agreeing with this work in sign and to 4.7% in magnitude. Not
verified: it would need Martin's tabulated values checked against their own
printed equation, and Orson's intermediate numbers, neither available here.
Recorded because it is testable.

### 5.0.4 What resolves it

Every recorded result uses $|\Delta\alpha|$ and is unaffected either way.
Orson's own AC-Stark measurement was a null at 6 MHz resolution, so the sign
has never been set by experiment. A fixed-lock pull measurement (the sign of
the shift-versus-power slope) settles it outright, and it has not been run.

**What changed on 2026-08-24, and what did not.** The experimenter
adjudicated the theoretical evidence and took this record's value as
the package's, so `rb5s6s.DELTA_ALPHA_AU` is now $-1145$ a.u. and Orson's
$+1093$ is kept beside it under its own name for the comparison. That is a
decision about which value the framework hands its reader, taken on the three
anchors and the lifetime discriminant above. **It is not an experimental
resolution**: the sign remains unset by measurement, this section stands
unchanged as the argument, and the fixed-lock pull is still what would
settle it. The decisive theory check is one
line for a specialist: the sign of $\alpha_{6S}$ at 993 nm.

### 5.1 Electric quadrupole and magnetic dipole: why neither appears

A fair question about any polarizability calculation, and it splits in two.

**The driven transition is purely E1·E1, by parity.** $5S_{1/2}$ and $6S_{1/2}$
are both even, so a two-photon amplitude connecting them must be even overall.
E1·E1 is odd × odd = even and is the allowed channel. E1·M1 and E1·E2 are both
odd × even = odd, and so vanish identically for $S\to S$. There is no multipole
admixture to the transition amplitude to include or to bound, because the
selection rule is exact rather than an approximation.

**The polarizability does admit E2 and M1 terms, and they are far below
everything else here.** Their nominal scales relative to $\alpha_{E1}$ are

$$\frac{\alpha_{E2}}{\alpha_{E1}}\sim(ka_0)^2 = 1.1\times10^{-7},\qquad
\frac{\alpha_{M1}}{\alpha_{E1}}\sim\alpha_{\text{fs}}^2 = 5.3\times10^{-5}$$

at $k=2\pi/993.4$ nm. Against $\alpha_{6S}(993)=-312$ a.u. that is
$3.5\times10^{-5}$ and $1.7\times10^{-2}$ a.u. The comparison that matters is
with the questions actually open on this line. The sign dispute is a factor
$4.6$ in a group of terms, the magnitude spread between this work and Orson is
4.7%, and the measured $w_0$ is $\pm20$% and gates every absolute result.
Multipole corrections enter at $10^{-5}$% and $10^{-3}$%.

**Nor is any multipole channel resonantly enhanced out of that suppression.**
The nearest S–D (E2) and S–S (M1) channels from either state sit
thousands of cm⁻¹ from the 10066 cm⁻¹ drive: 5S–4D at 516.7 nm (detuned
9289 cm⁻¹), 5S–6S M1 at 496.7 nm (10066), 6S–5D at 1796 nm (4497),
6S–4D at 12.9 µm (9289). A near-degeneracy could in principle lift a
suppressed channel into relevance. None is available. (That last interval, 6S
to 4D, is closed to dipole radiation and so is invisible in the 6S lifetime,
but it is open to a collision, and it is examined as a candidate inelastic
channel in [the van der Waals difference-potential
note](notes/vdw_difference_potential_and_4d_channel.md) §6.)

The same scrutiny has been run where it bites hardest, on the computed
differential-polarizability zero at 1297.5 nm that a proposed telecom-band
lever would locate. That root sits only 0.745 nm from the 6S to 7P pole, so a
neglected multipole term could in principle move it. It cannot. No
multipole-allowed one-photon resonance of either clock state falls inside the
1292.4 to 1298.3 nm gap the root lives in, the nearest being 6S to 6D at
1169 nm (E2), 6S to 8S at 1122 nm (M1) and 6S to 4F at 1502 nm (E3), so the
neglected terms contribute background and never a local pole. Granting the
radial matrix elements two orders of magnitude of enhancement still leaves that
background below $10^{-5}$ of the dipole background the root balances against,
which moves the root by under a hundredth of a picometre. A ten per cent error
on the dipole inputs themselves moves it by about 75 pm, four orders of
magnitude further. Slope table in
[FUTURE_TRANSITIONS_titsapph.md](FUTURE_TRANSITIONS_titsapph.md) §5.1.

### 5.2 What a third 993 nm photon does, quantified

Asked 2026-08-09 and answered here because the polarizability breakdown above
raises it: the field that drives the two-photon transition is still present once
the atom is in 6S, so what does the next photon do? The short answer is almost
nothing, and the arithmetic is worth keeping because it closes three questions
at once.

**It reaches no resonance.** From 6S a third photon lands at 30198.75 cm^-1.
Selection rules allow only $n\mathrm{P}$ from a real S state, and the nearest odd-parity
level of any kind is 8P3/2 at 29853.79 cm^-1, so the photon arrives
**345 cm^-1 above it**. That is 10.34 THz, about 23000 Doppler widths of the
1028.67 nm transition at 130 C, and roughly $2\times10^{7}$ times the 8P natural
width. The next candidates are farther: 8P1/2 at 364 cm^-1, then 9P and 6F at
several hundred more. A single-colour three-photon resonance to 8P3/2 would need
1004.90 nm, 11.5 nm from where this laser runs.

**It is not a loss channel.** At 225 mW and the measured waist the 8P admixture of
6S is $1.7\times10^{-9}$, and the 6S to 8P scattering rate is $8.5\times10^{-4}$
per second. Every channel together, from `hyperpolarizability.scattering_rates`
rescaled to the campaign field, reaches 0.122 per second and is dominated by the
*downward* 6S to 5P Raman channels rather than by 8P at all. Against the 6S decay
rate $2.194\times10^{7}$ per second that is a branching of $6\times10^{-9}$, and
the width it adds is 0.04 Hz against a 3.4925 MHz natural width. No power law in
the data can see it.

**It cannot ionize, and the fourth photon can.** 6S sits 13558.30 cm^-1 below the
33690.81 cm^-1 limit, and one photon falls 3492.06 cm^-1 short. A fourth clears
threshold by 6574 cm^-1, which `FUTURE_TRANSITIONS_titsapph.md` already records
for this laser. So the open process is 2+1+1 rather than 2+1, at a rate this
experiment cannot reach.

**The one footprint it does leave** is the 8P contribution to the light shift
computed above: 18% of $\alpha_{6S}$ and 4.9% of the differential, which is a
term to keep and the reason 8P appears in the line lists at all.

**The cascade's own photons, asked and quantified (2026-08-09).** Each excitation
ends in a cascade that emits one infrared photon, 1323.9 or 1366.9 nm on
6S to 5P, then one D-line photon, 795.0 or 780.2 nm on 5P to 5S, so the cell
contains four more wavelengths than the drive, and the atom passes through a
real 5P transient of 27.7 ns on every count. From the committed term energies,
none of the re-excitation channels these open comes near a resonance.

From the real 5P transient, one more 993 nm photon lands 2513 to 2750 cm^-1
from the nearest even level, and two more fall 742 to 979 cm^-1 short of the
ionization limit. From a real 6S atom, its own infrared photon reaches
149 cm^-1 short of 7P1/2, and a D-line photon lands 742 to 979 cm^-1 below the
limit, inside the high-nP Rydberg ladder whose spacing there is about
190 cm^-1. The closest coincidence in the whole family is a trapped D2 photon
on a 5P3/2 atom, which lands 67 cm^-1 from 5D because 780 nm sits near the
776 nm second step of the well-known two-step ladder. Every one of these needs
a real excited atom to meet a cascade photon, and the steady-state populations
at the campaign's brightest point are $1.2\times10^{-3}$ for 6S and
$7.4\times10^{-4}$ for 5P of the illuminated atoms, so the rates are doubly
negligible before any detuning suppression is counted.

**Every pairwise two-photon combination of the five wavelengths, from 5S.** The
sums of {993.4, 780.2, 795.0, 1323.9, 1366.9} nm photon pairs land as follows
against the even-parity levels: the drive pair on 6S exactly, which is the
signal. Two mixed pairs, 780.2 with 1366.9 and 795.0 with 1323.9, land on 6S
**exactly**, and must, because each is the cascade's own photon pair and energy
conservation closes the loop. The D2 pair lands 69 cm^-1 from 5D, the familiar
proximity of 780 nm to the 778 nm two-photon line. Everything else is 238 cm^-1
or farther from any even level, and the infrared pairs land thousands of
wavenumbers from anything.

**The exactly resonant pairs are a two-step echo, and its rate is small with a
distinctive scaling.** The first step is D-line reabsorption, which is the
known radiation trapping and makes a real 5P atom. The second is an infrared
cascade photon driving that atom 5P to 6S resonantly. At the campaign maximum,
with the peak-rate envelope below, the second step runs at about
$2.6\times10^{4}$ per second on a 5P atom against its $3.6\times10^{7}$ per
second decay, so the echo re-excites 6S at a fraction of order $10^{-3}$ of the
direct rate, and it scales as the fourth power of the drive power, since both
the photon bath and the 5P population scale as the second. That is invisible
under the measured amplitude slopes of 1.83 to 2.12 and adds nothing a width or
centre channel can see. ENVELOPE grade.

**The light shift from the bath fields, which is the sharper question.** Four
new wavelengths fill the cell, so the levels are shifted by more than the
drive. The infrared bath is ballistic, of order $10^{3}$ photons per cubic
centimetre at the campaign maximum, an equivalent intensity below a microwatt
per square centimetre, and its shift is sub-millihertz. The D-line bath is
trapped and is the one that needs numbers. An a-priori chain, the beam-column
excitation rate at the record's peak-rate figure, one D photon per cascade, and
a Holstein confinement of about 64 natural lifetimes at the record's line-centre
opacity of 160 per centimetre, gives an equivalent bath intensity of order
$10^{2}$ milliwatts per square centimetre. That chain refutes itself at the top:
such a bath would saturate the D lines and put a visible fraction of the cell in
5P, which the data exclude on sight, so at least one link, the
peak-rate-everywhere assumption or the confinement time, overestimates by an
order or more. What bounds the effect is structure and data rather
than the chain. The trapped spectrum is redistributed roughly symmetrically
about the D-line centres, and a symmetric near-resonant spectrum cancels its
dispersive shift at first order. What survives scales as the square of the
drive power, like the excitation rate that sources it, and the width and centre
channels cap any such term empirically: the width shows no power trend under
3 to 8 per cent block scatter (C3a), and the window-referenced centre analysis
bounds power-correlated centre motion at the few-hundred-kilohertz level (C3e).
So for this dataset the bath shift is bounded well below the drive's own
$S_0$, but it is not dismissible a priori at the precision a fixed-lock centre
campaign aims for, and it is common-mode across the four peaks. Recorded OPEN:
a fixed-lock session that reads absolute centres should either estimate the
trapped-light shift properly, Holstein geometry and measured fluorescence in
hand, or take a cell-temperature lever against it, since the trapping factor
rides the ground-state density.

**Addendum, 2026-08-09, from an adversarial pass on the paragraph above.** Three
corrections, and the first reverses the direction the paragraph assumed.

*The confinement factor is too small, not too large, and the cell geometry now
says so.* The paragraph offers two candidates for the link that overestimates,
the peak-rate-everywhere assumption or the confinement time, and the confinement
time is the wrong suspect. Taking the paragraph's own line-centre opacity of 160
per centimetre, which does reproduce `density.d1_optical_depth_per_cm` at 130 C,
the standard Doppler-limited escape factor for a cylinder, and the cell's
dimensions as APPARATUS.md section 5 now records them, about 25 mm across and
100 mm long, the transverse escape path is a 1.25 cm radius and the trapping
factor is **about 500 natural lifetimes at 130 C and 140 at 110 C**, against the
64 quoted. Reproducing 64 would need a 2 mm radius. So that link makes the
estimate eight times worse at the campaign's hottest condition, and by
elimination the overestimate sits in the excitation-rate assumption, which is
where a Gaussian beam column is being treated as a uniform one at peak rate.

*The number has no code behind it, which is unlike the rest of this section.*
Every other figure in section 5.2 names the function that produced it. The
equivalent bath intensity of order 100 milliwatts per square centimetre names
none, and no module, script or test in the repository computes a Holstein factor
or a bath intensity. Its intermediate arithmetic could not be reconstructed on
review. Until it is code, read it as an order-of-magnitude marker rather than a
computed quantity.

*The uncertainty is dominated by the excitation profile, not by the temperature
and no longer by the radius.* The instinct is that a bath estimate is dominated by
the ground-state density, which runs exponentially in temperature. It is not. The
density carries the documented 20 per cent correlation systematic and the
cold-spot offset, a factor of a few at worst. The escape factor was the largest
term while the cell radius was unknown, and with the radius recorded it
contributes only the recollection's ten per cent, amplified logarithmically. What
is left, and what now dominates, is the excitation-profile assumption, plausibly a
factor of ten to a hundred on its own. So the bath term carries one to two orders
of magnitude, and closing it means computing the excitation properly rather than
measuring anything.

*The bench fact this needed is now recorded, and it is approximate.* Nothing in
this repository held the cell's length or diameter until 2026-08-09, because
nothing else needed them. APPARATUS.md section 5 now carries them, about 25 mm
across and 100 mm long, tagged as an experimenter recollection rather than a
datasheet reading. A supplier record or a photograph with a scale would upgrade
them, and neither is on hand: a search of this repository's history, the
excluded trees and the wider filesystem found no primary record, and the one
close-up cell photograph carries no scale.

*Second correction, same day: the correction above is itself conditional on a
centred source, and the source is not centred.* The experimenter then stated that
the 993 nm focus was placed close to the collection lens rather than at the cell's
mid-plane, to raise the collected solid angle (APPARATUS.md section 3). That
changes the escape geometry, because a trapped photon leaves by the shortest
optically thick path and the shortest path is now the standoff to the near window,
not the 12.5 mm radius. At 130 C the factor runs 508 lifetimes for a centred
source, 185 at a 5 mm standoff, 66 at 2 mm and 29 at 1 mm, and at 110 C from 138
down to 7 over the same range. **So the 64 the paragraph quotes is defensible
after all, and corresponds to a standoff of about 2 mm.** The claim that the
confinement link makes the estimate eight times worse holds only for a source at
the cell's mid-plane, which this apparatus does not have. What survives is that
the factor is not 64 by derivation, it is 64 by coincidence with an unrecorded
standoff, and the span over the plausible geometry is thirty to five hundred. The standoff is now the bench fact that matters, not the diameter.

*One channel the section does not consider at all.* The drive inverts a
measurable fraction of the cell on the 6S to 5P transitions, whose photons at
1324 and 1367 nm are not trapped and leave along the beam axis, which is the long
dimension. A gain-length estimate at the excited fractions this section already
quotes lands of order unity, so amplified spontaneous emission on those lines
cannot be dismissed by inspection. It is not quantified here, since the net
inversion needs the 5P population subtracted properly and the geometry above is
missing, and it is recorded as the one candidate that could rival the trapped
D-line bath.

What the cascade photons do measurably in this dataset is the D-line radiation
trapping already carried by the record: the trapping factor is set by the
ground-state density, so it is power-independent at fixed temperature and
rescales the amplitude without bending the power law, which is C3b's stated
immunity argument. The infrared pair is not trapped at all, since its only
absorbers are the 5P transients themselves.

**And the standard treatment is already in the prior art.** Section 6c of
[delone1980](lit/delone1980.md) is the resonance-enhanced $k = k_1 + k_2$
problem, which is exactly this 2+1, and it names the three field-induced
perturbations with their intensity scalings, including an ionization broadening
$\Gamma_i$ from the resonant state to the continuum. The right way to quantify a
third photon here is their $\Gamma_i$, not a fresh derivation, and all three of
their terms sit far below the natural width at this intensity.

**A caution about the fourth-order machinery, recorded where it will be found.**
`hyperpolarizability._rspt4` must not be evaluated at this wavelength. Its
Floquet basis contains the partner S state two photons down, so it carries a pole
wherever $2h\nu$ equals a real S-to-S interval, and for 5S-6S that is here. Fed a
campaign peak label it returns a differential fourth-order shift of order 100 Hz,
of which 99.995% is that single term: it is the two-photon level repulsion,
$|M|^2/D$ with $|M|$ of order $2\times10^{5}$ Hz, not a hyperpolarizability.

The cleanest proof that the number is meaningless is that **it changes sign across
the four measured lines**, swinging from $-27.75$ to $+152.73$ Hz. The reason is
that $D$ is not a physical detuning at all. The peak labels are fitted hyperfine
positions, so the drive sits *on* the component it addresses, while `E_6S_CM` is
the NIST hyperfine **centroid**. $D$ is the residue between them, part genuine
hyperfine offset and part a common-mode calibration offset shared by all four
labels. The genuine non-resonant value is of order $10^{-3}$ Hz, about
$5\times10^{7}$ below the second-order differential shift at the same field and
eight orders below the light-shift bound of record.

No published coefficient is affected, because the nearest crossing the module is
evaluated at sits 354 cm^-1 clear of the pole, and
`tests/test_hyperpolarizability.py` now pins both that clearance and the pole's
structure.


## 6. Novelty position relative to prior art

Asymmetric lineshapes from *distributed* AC-Stark shifts are **not new**, and
seven separate lines of prior art reach parts of what is done here. Naming them
first is cheaper than having a referee do it.

| prior work | what it already has | what it does not do |
|---|---|---|
| [Lee 2010](lit/lee2010.md) | the same experiment in Cs (6S–8S at 822 nm, hot cell, retro-reflected, cascade fluorescence), intensity and density scanned independently, and the intensity-dependent broadening separated from the homogeneous width | fits that component as a symmetric Gaussian, so no third moment, no closed form and no cumulants, and attributes it to intensity inhomogeneity only tentatively, keeping velocity-dependent collisions alive |
| Wieman 1987 and [Stalnaker 2006](lit/stalnaker2006.md) | a spatially varying shift producing an asymmetric line, with α extracted *from* the asymmetry | numerical Bloch treatment, fringe-*resolved*, one-photon (n=1), so no I² weighting |
| [Delone 1980](lit/delone1980.md) | the general result itself: the lineshape as a map of the shift distribution, the $F^k$ multiphoton weight, the asymmetric shift-dominated limit, and the inverse problem stated twice | $P$ is the unknown to be reconstructed, so the integral stays formal and no cumulant can be written down |
| [Slepkov 2010](lit/slepkov2010.md) | the shift distribution of a guided mode kept and fitted, not averaged | saturated absorption in a hollow core, not two-photon, and no closed form |
| [Wall 2014](lit/wall2014.md) | single-colour two-photon, so the I² weighting *is* present, over a measured 3D intensity map | purely numerical. Inference runs the other way (α in, lineshape out), longitudinal not transverse, shift ≫ linewidth, and a working frequency reference throughout |
| [Camparo 1992](lit/camparo1992.md) | a two-photon shift *distribution* giving an asymmetric line, with the first moment separated from the peak | the distribution is over a stochastic field in **time**, by Monte Carlo, and needs the strong-field adiabatic regime |
| [Fendel 2007](lit/fendel2007.md) | the peak-vs-average question tested and settled in a hot-alkali single-colour two-photon cell: −0.21 Hz/(mW/cm²) against *average* intensity | a deliberately **unfocused** 0.72 mm waist, chosen to make the distribution narrow enough that the average suffices |

[Hamilton 2023](lit/hamilton2023.md) builds the identical focus-averaged shift
integral on a retro-reflected Rb vapour line, then collapses it to a single mean.

Read together these bound the claim tightly. **The existence of the asymmetry is
not claimed here, nor the I² weighting, nor keeping the distribution, nor the
closed form, nor the phenomenon that a transverse intensity distribution
broadens a two-photon alkali line.** Lee measured that last one in Cs sixteen
years ago, and any wording implying this programme first noticed it is
indefensible. Fendel in particular is the paper a referee is most likely to cite
back, and it reads *for* this work rather than against it. A first-rate group,
facing a focused-beam light-shift distribution, engineered it away rather than
modelling it. What is specific here:

1. the **evaluation** of Delone's general result for the distribution that
   actually occurs. Their $P$ is a laser's unknown statistics, so their
   integral stays formal. In a focused beam $P$ is fixed by geometry, the
   integral closes, and the result carries **analytic cumulants on bounded
   support**, in particular the intrinsic $g_1=+0.566$ at $n=2$, which is a
   number rather than a fit. The closed form itself is theirs.
2. the **drift-immune moment method** (§3), using a light shift as a
   reference-free measurement channel, which the precision community's
   suppress-the-shift approach never needed. Delone frame the lineshape as a
   read-out of $P$ and say so twice, so the map is theirs too. What is claimed
   is the pair of properties §3 separates, translation immunity and component
   specificity, both answers to an untrustworthy reference that does not arise
   in their setting.
3. the **fringe-averaged** treatment of the retro standing wave, with M19
   showing that the fringes do not move the mean. The delineation against
   Wieman and Stalnaker is fringe-*averaged* against fringe-*resolved*, **not**
   travelling against standing, since both are standing waves. Their slow
   atomic beam resolves the $\lambda/2$ fringes and our fast thermal atoms
   average them, leaving only the small resolved tail of §5.
4. the **geometry-independence to the evanescent case**, the bridge to a
   nanofibre lineshape.

Against Lee specifically, what survives is the shape and its cumulants, never
the phenomenon. A Voigt fit has no third moment to put $g_1$ in.

(The transit kernel itself, natural Lorentzian $\otimes$ two-sided exponential,
is the established [Biraben–Bassini–Cagnac](lit/biraben1979.md) result, *J.
Phys. (Paris)* **40**, 445 (1979), and we do not reinvent it. Full ledger:
`docs/LITERATURE.md`.)

## 7. The open question (where a contribution fits)

The triangle assumed a beam of constant waist across the detection region. The
fluorescence lens actually collects from an axial window $|z|\le Z_c$ while the
beam diverges, $w^2(z)=w_0^2(1+\zeta^2)$, $\zeta=z/z_R$. Averaging the
transverse law over $z$ (the per-slice weight $\propto(1+\zeta^2)^{1-n}$ cancels
the local ramp normalisation up to one factor $1+\zeta^2$) gives the closed form

$$f(s) \propto |s|^{n-1}\left[\zeta_m + \frac{\zeta_m^3}{3}\right],\qquad
\zeta_m(s) = \min \left(\frac{Z_c}{z_R},\ \sqrt{\frac{S_0}{|s|}-1}\right)$$

which we evaluate numerically (`lineshape.stark_ramp_axial`). The standardised
skewness **changes sign** with the collection window, $g_1 \approx +0.56$ at
$w_0=60$ µm ($Z_c/z_R=0.18$) but $\approx -0.35$ at $w_0=16$ µm
($Z_c/z_R=2.5$), crossing zero at $Z_c/z_R\approx1.12$, because a long window
piles weight at weak out-of-focus shifts.

Where the crossover falls is set by the collection geometry. $Z_c$ is the
imaging field of view $L_\parallel/2M$ of the side-viewing $f=18$ mm lens, with
$L_\parallel$ the cathode's active extent along the beam image. That extent is
12 mm: the R636-10 (housed in the Thorlabs PXT1/M module seen in the in-campaign
photo) has a 3 × 12 mm cathode, whose rotation is a ×4 lever on $Z_c$, and it
was mounted with its long axis along the beam (experimenter-confirmed 2026-07-23). So $Z_c = 6/M$ mm,
and the two-waist flip holds for every $M$ from 0.5 to 6 rather than depending
on which layout the bench happens to realise. $u$ and $v$ remain unmeasured, so
the magnitude still carries an envelope (PLAN §6 #4). The pure triangle holds
only at large waist, and the small-waist configuration that maximises $S_0$ is
exactly where the clean triangular law is least valid.

**The questions.** (i) Is the axial-averaged form above correct and complete, or
does a proper treatment of the position- *and* velocity-dependent shift (the
thermal transit through a diverging Gaussian) modify it beyond this
quasi-static $z$-average? (ii) What is the right observable to quote when the
triangle fails? The sign-flip of $g_1$ between two waists is one candidate that
is immune to instrumental asymmetry, since no instrumental asymmetry depends on
$z_R$. Is there a cleaner invariant? (iii) Does the evanescent-geometry claim in
§6 survive the same scrutiny? These are well-posed, they need no new data, and
they sit exactly at the focused-two-photon / inhomogeneous-field boundary.

*Backing material in the repo: README §2.6 (derivations),
[methods chapter 3](methods/03_the_ac_stark_ramp.md) (the long-form
derivation), `docs/LITERATURE.md` (prior-art ledger), `docs/PLAN.md` §6 (the
light-shift program of the proposed fixed-lock session, which would measure
$S_0$ and test the sign-flip). Absolute numbers are preliminary pending the
fixed-lock session beam-waist measurement, on which every magnitude rides.*
