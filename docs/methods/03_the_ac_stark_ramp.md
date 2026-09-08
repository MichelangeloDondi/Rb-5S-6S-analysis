*Chapter 3 of 8 · [methods index](../methods.md)*

**The question.** What does a focused beam do to the light shift, once you
notice that the atoms it shifts sit at every intensity in the beam rather than
at one?
**Takes.** The lineshape chapter, for the symmetric kernels the ramp is
convolved with, and the measurement chapter for the retro geometry.
**Gives.** The triangular ramp law and its cumulants, the diverging-beam closed
form and its sign flip, which the collection geometry sets (the axial window
crossing 1.12 of the Rayleigh range), and the pinned intensity convention
behind $S_0$.
**Skip if.** You want the record's result rather than the physics. The ramp is
not resolved in the 2025 data and its bound is in the results chapter.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

### 2.6 AC-Stark shift: derivation of the triangular "ramp law"

Intense light shifts atomic levels (the AC-Stark or light shift) by an amount
proportional to the local intensity $I$. This chapter takes the shift toward the
**red** (lower frequency), following [Orson *et al.*](../lit/orson2021.md) 2021's
published $\Delta\alpha$ for this line. An independent recompute here
returns the same magnitude but the *opposite* sign, an open question flagged for
adjudication in [`THEORY_NOTE.md`](../THEORY_NOTE.md) §5. Nothing in the record's
results depends on the choice, because the shape below and every bound drawn
from it are sign-immune ("The coefficient", below). Different atoms sit at
different radii in the beam and so feel different shifts. What does the *line*
show? Two facts set it up:

- **Two-photon excitation rate** $\propto I^2$ (each photon contributes one
  power of $I$).
- **Shift** $s = -\kappa I$ for some positive constant $\kappa$ (red $\Rightarrow$
  minus, per the convention fixed above).

Take a Gaussian beam, $I(r)=I_0e^{-2r^2/w_0^2}$, and let $u\equiv I/I_0\in(0,1]$.
The signal contributed by the annulus between $r$ and $r+dr$ is

$$dS  \propto  I^2(2\pi rdr) \propto  u^2rdr$$

Change variables from $r$ to $u$. From $u=e^{-2r^2/w_0^2}$,

$$\frac{du}{u}=-\frac{4r}{w_0^2}dr  \Longrightarrow   rdr=-\frac{w_0^2}{4}\frac{du}{u}$$

so

$$dS \propto  u^2\cdot\frac{du}{u} = udu$$

The shift at intensity $u$ is $s=-\kappa I_0u \equiv -S_0u$, where
the positive quantity $S_0=\kappa I_0$ is the on-axis (maximum) shift magnitude. Substituting
$u=-s/S_0$, the **signal-weighted distribution of shifts** is

$$\boxed{f(s) \propto |s|\quad\text{on}\quad s\in[-S_0,0]}$$

which is a triangular **ramp**. (The same law holds for a nanofibre's
evanescent field, because the intensity is exponential in the flat coordinate
there too, and that shared law is the physics bridge to the nanofibre extension.) Normalizing,
$f(s)=2|s|/S_0^2$, we get the moments by direct integration:

$$\langle s\rangle=\int_{-S_0}^{0}  sf(s)ds=-\tfrac{2}{3}S_0,
\qquad
\mathrm{Var}(s)=\tfrac{1}{18}S_0^2,
\qquad
\kappa_3=\langle(s-\langle s\rangle)^3\rangle=+\tfrac{1}{135}S_0^3$$

So the **mean red pull is $\tfrac23 S_0$**, and the distribution is
positively skewed (peak pulled red, thin tail toward the blue). Here
$\kappa_2\equiv\mathrm{Var}$ and $\kappa_3$ are the second and third
*cumulants*. The ramp's own **standardized** skewness, the scale-free shape
number, is $\kappa_3/\kappa_2^{3/2}=18^{3/2}/135\approx0.566$, independent
of $S_0$ (a property of the triangle, not of the power). That fixed number is
the target of the form test below. The ramp's cumulants continue
$\kappa_4 = -S_0^4/540$ and $\kappa_5 = -S_0^5/567$, with the seventh
positive again (`rb5s6s.cumulants.cumulants_from_central_moments` on the
density's moments, and `tests/test_cumulants.py` pins the third), so the odd
orders alternate in sign, and a statistic built on the sign of a windowed
cumulant is read against each order's own sign and never against zero. The
signs are the coded red side's, and on the blue side every odd one flips. What varies with power is the
*observed line's* asymmetry, which we get by folding the ramp into the rest
of the line.

**[Cumulants add under convolution](../wiki/third-cumulant.md)** (the cumulant of a sum of independent
variables is the sum of the cumulants), and the Gaussian and transit kernels
have $\kappa_1=\kappa_3=0$ exactly. **The Lorentzian is the qualified case.** Its even cumulants diverge, so
whole-line $\kappa_2$ and any standardised skew exist only at a fixed
window, and the caveat below stands. The whole line's pre-window third
cumulant is still $\kappa_3^{\text{tot}} = S_0^3/135$, since the odd
moments of every kernel cancel. What a windowed, self-centred readout keeps
of it is the truncation-limited fraction the `survival` rows of
[`results/cumulant_window_check.csv`](../../results/cumulant_window_check.csv)
measure, while mis-centring by $\delta$ leaks first cumulant at
$\sim(2/\pi)\gamma\delta W$ ($\gamma$ the half-width). Drift immunity
therefore belongs to self-centred readouts, the fit's free per-scan centre
first among them. Derivation and numbers are on
[the concept page](../wiki/third-cumulant.md), the dated account in
the history. The mean
pull is the primary fixed-lock-session observable
([where this can go](08_assumptions_and_outlook.md)).
(The dataset's centre channel supplies no bound of its own. A peak position is
a frequency only within a run of traces taken at one scope horizontal setting,
so each run carries a free offset, and the pull comes out unidentifiable rather
than merely imprecise. The width-and-shape channel is the dataset's only
light-shift channel: see [the results chapter](07_what_we_found.md) and
[`THEORY_NOTE.md`](../THEORY_NOTE.md) §3.)

A literal *standardized* skewness of the full profile is more delicate,
because the homogeneous Lorentzian has divergent second and higher even
moments. $\kappa_2^{\text{tot}}$ is not finite, so one must work at fixed
fit window rather than with whole-line moments. Over the fit window the
symmetric part contributes an effective width $\sigma_\text{eff}$ (a standard
deviation, $\sim 2$ MHz, set mostly by the $\sim 5$ MHz total FWHM and
nearly power-independent), against which the asymmetry reads as

$$g_1^{\text{obs}} \sim \frac{\kappa_3^{\text{tot}}}{\sigma_\text{eff}^3}
=\frac{S_0^3/135}{\sigma_\text{eff}^3} \propto S_0^3 \propto P^3$$

since $S_0\propto$ power $P$. This is a self-centred construction, the
window riding the fitted centre, which is what licenses using
$\kappa_3^{\text{tot}} = S_0^3/135$ here at all (remark above). (No contradiction with the fixed $0.566$: that
is the standardized skew of the ramp *alone*, where here the same $\kappa_3$ is
divided by a much larger and nearly fixed symmetric width.)

**Two consequences for the 2025 data.** First, the ramp predicts the FWHM
should move $\lesssim2$% across our power sweep, and the dataset shows no
significant power trend. The observed 3 to 8% spread is non-monotonic block
scatter, an order above the predicted ramp contribution, so the dataset cannot
resolve the ramp term. The old "power null" is therefore a null the ramp law is
*consistent with*, not a confirmation of it. Second, the observed asymmetry
$\propto P^3$ is $\sim10^{-4}$ against a $\sim10^{-3}$ noise floor, which is
unmeasurable, so all AC-Stark *coefficients* move to a fixed-lock session, where
the shift itself ($\propto P$) is measured directly against a stable lock.

*Code:* `stark_ramp()`, built from exact per-cell integrals so the area is
exactly 1 and the mean exactly $-\tfrac23 S_0$ even for shifts far below the
grid step.

#### The general law: the signal exponent sets the ramp shape

*General framing: [the AC-Stark shift](../wiki/ac-stark-shift.md). The
derivation below stays here.*

Nothing in the change of variables above used $n=2$ except the weight
$u^n$. For a signal $\propto I^n$ the same steps give

$$dS  \propto  u^n\frac{du}{u}  =  u^{n-1}du
\qquad\Longrightarrow\qquad
f(s) \propto |s|^{n-1}\ \ \text{on}\ [-S_0,0]$$

For a **one-photon** transition ($n=1$, for instance the Stark-induced
forbidden lines of the parity-violation literature) the distribution is
**uniform**: mean $-S_0/2$ and, being symmetric about its mean, $\kappa_3=0$,
which is **zero skew**. The skewness observable exists at all *only because the two-photon
signal goes as $I^2$*. This one line is the delineation from the nearest
prior art ([Stalnaker *et al.*](../lit/stalnaker2006.md), PRA **73**, 043416 (2006), who extracted an
AC-Stark parameter from asymmetric standing-wave lineshapes numerically, in
the $n=1$, fringe-resolved regime, with the full delineation in
`docs/LITERATURE.md`).

#### $n=2$ is a weak-field statement, and the dataset sits near its edge

![the weak-field limit and what leaving it costs the predicted skewness](../../figures/fig24_weak_field_limit.png)

*Left, the weight the atom carries against the square law that stands in for
it, with this dataset and the proposed tight focus marked. Right, the
consequence for the observable the tight focus is wanted for. The dataset's own
configuration sits where the two agree to a couple of per cent.*

The $I^2$ weight is the leading term of the excited fraction, not the fraction
itself. What the atom actually contributes goes as $(s/2)/(1+s)$ with
$s=2\Omega^2/\Gamma^2$, which reduces to $I^2$ only while $s\ll1$, since
$\Omega$ itself is two-photon and quadratic in the field. That matters here
because $s$ scales as the *fourth* power of the inverse waist while $S_0$
scales only as the second, so the two do not move together. At the dataset's
measured 64 µm and 225 mW, $s=0.033$ and the weak-field law is safe to well
under a percent. At the 16 µm the small-waist session proposes, $s=8.5$, the
weight is nearly flat in intensity, and re-integrating the moments with the
saturated weight moves the predicted axial skew from $-0.36$ to $-1.07$. The
sign flip survives, the magnitude does not, so the tight-focus prediction is a
factor-of-three statement and the reason is a modelling assumption rather than
an unmeasured input. Computed by `scripts/run_geometry_design.py`, written up
in [`docs/notes/running_wave_and_waist_design.md`](../notes/running_wave_and_waist_design.md).

#### The parameter-free moment hierarchy (the form test)

Dividing out $S_0$, the ramp component predicts *pure numbers*:

$$\frac{\mathrm{Var}(s)}{\langle s\rangle^2}=\frac{1/18}{4/9}=\frac18,
\qquad
g_1\equiv\frac{\kappa_3}{\mathrm{Var}(s)^{3/2}}
=\frac{1/135}{(1/18)^{3/2}}=\frac{18^{3/2}}{135}\approx+0.566$$

A fixed-lock session would test them in order of statistical cost.

1. **Mean pull against $P$.** The first cumulant, exact,
   apparatus-independent and first order in $S_0$. At the producer's 3 MHz
   reference shift, window and collisional width (named in the file's notes) it
   carries a windowed excess of [0.051](../../results/cumulant_window_check.csv "ref:cumulant_window_check:kappa1_window_excess_pct:gc0.55") per cent (`kappa1_window_excess_pct` row and its construction note), measured at that
   shift alone. A fixed lock is what makes centres usable at all.
2. **Excess variance against $P^2$.** The symmetric second-moment growth
   $\mathrm{Var}\propto S_0^2$, which is exactly what the Cs 6S to 8S
   literature reported as a growing Gaussian width.
3. **Skewness.** The smallest signal, and the only moment that is *zero unless*
   $n=2$.

The pure numbers above are the ramp *alone*. In the measured line each is
diluted by the symmetric kernels, and read at a fixed fit window per the
divergence caveat above, so the hierarchy is fitted jointly rather than read off
one trace.

#### Diverging-beam collection: the closed form and the sign flip

The triangle assumed a beam of constant waist across the detection region.
Really the fluorescence lens collects from an axial window $|z|\le Z_c$
around the focus while the beam diverges, $w^2(z)=w_0^2(1+\zeta^2)$ with
$\zeta=z/z_R$, $z_R=\pi w_0^2/\lambda$. At each $\zeta$ the transverse law
holds with a *local* maximum shift $S(\zeta)=S_0/(1+\zeta^2)$, and the per-slice
signal weight is $\propto w^2 I_0^{n}\propto(1+\zeta^2)^{1-n}$, which
exactly cancels the local normalization $S(\zeta)^{-n}$ up to one factor
$(1+\zeta^2)$. The $z$-integral then closes for any $n$:

$$f(s) \propto |s|^{n-1}\left[\zeta_m+\frac{\zeta_m^3}{3}\right],
\qquad
\zeta_m(s)=\min \left(\frac{Z_c}{z_R},\ \sqrt{\frac{S_0}{|s|}-1}\right)$$

$Z_c/z_R\to0$ recovers the triangle, and the hard edge at $-S_0$ softens to
zero because only the focal plane reaches the full shift. Numerically, on a
uniform window at $Z_c=2$ mm, which was a placeholder when this table was first
computed and is now supported by the magnification estimate below at 2.0 to
2.4 mm, and which stays OPEN until the fixed-lock session's collection-profile
measurement:

| config | $Z_c/z_R$ | $\text{mean}/S_0$ | $\text{Var}/\text{mean}^2$ | $g_1$ |
|---|---|---|---|---|
| pure triangle | 0 | $-0.667$ | 0.125 | $+0.566$ |
| 60 µm (proposed config L) | 0.18 | $-0.660$ | 0.125 | $+0.564$ |
| 64 µm (2025 dataset) | 0.15 | $-0.661$ | 0.125 | $+0.565$ |
| 16 µm (proposed config S) | 2.47 | $-0.431$ | 0.333 | $-0.354$ * |

\* At 225 mW config S is already saturated (PLAN §3), so the effective
signal exponent $n$ there is below 2: that *strengthens* the negative skew but the
$n=2$ magnitudes in this row are no longer parameter-free. At config S the
sign is the robust observable, and the magnitudes belong to L and M.

An independent derivation reached the same numbers (a reader outside the project,
2026-07-26, held privately): working the $z$-integration by hand gives the
long-cell weight in closed form, $w(u)\propto\sqrt{(1-u)/u}(1+2u)$ with
mean $S_0/3$, variance $11S_0^2/144$ and $|g_1| = 0.5482$, and its quadrature
matches this module's numerics to every printed digit at every geometry
tested, with the crossover at $Z_c/z_R = 1.1172$. The closed forms are held as
tests (`test_axial_ramp_matches_the_independent_closed_form`).

**The skewness flips sign** (crossover at $Z_c/z_R = 1.1172$): a long
window piles signal into weak out-of-focus shifts, leaving a tail toward
$-S_0$. Whether config S lands past the crossover is a question about the
collection optics, and $Z_c$ is not a free parameter: for the side-viewing
$f=18$ mm lens imaging the beam onto the PMT it is the axial field of view in
object space, $Z_c=L_\parallel/2M$ with magnification $M=v/u$ ($u$ = lens–beam
and $v$ = lens–PMT distances, $1/u+1/v=1/f$), where $L_\parallel$ is the
photocathode's active extent *along the beam image*. The R636-10 cathode, the
tube housed in the Thorlabs PXT1/M module seen in the in-campaign photograph,
is a 3 × 12 mm rectangle, so which of its axes lies along the beam is a ×4
lever on $Z_c$.

It is the 12 mm axis. The cathode was mounted with its 12 mm axis along the beam through the 2025
campaign (confirmed from recollection 2026-07-23, [APPARATUS](../APPARATUS.md)) and is not
re-oriented between configurations, so $Z_c = 6/M$ mm is a single fixed number
and $Z_c/z_R$ moves between the two configurations only through $w_0$.
The along-beam mounting is the larger of the two cases, so it pushes $Z_c$ *towards* the
crossover rather than away from it, and the two-waist flip survives it across
the whole plausible range of magnification:

| $M$ | $Z_c$ (mm) | $g_1$ at 64 µm | $g_1$ at 16 µm | flips |
|---|---|---|---|---|
| 0.5 | 12.0 | $+0.142$ | $-0.510$ | yes |
| 1.0 | 6.0 | $+0.498$ | $-0.476$ | yes |
| 2.0 | 3.0 | $+0.560$ | $-0.416$ | yes |
| 4.0 | 1.5 | $+0.565$ | $-0.277$ | yes |
| 6.0 | 1.0 | $+0.566$ | $-0.071$ | yes |

So the sign-flip test does not require $M$ to be known: it holds for every $M$
from 0.5 to 6, and a magnification near forty, which the plan hub now offers
as one route at the tight waist, removes it with the window that makes it. Portrait would have forfeited it, because $Z_c = 1.5/M$ mm sits
below the 0.90 mm flip threshold for any $M$ above 1.7 (PLAN §6 #4).

**The magnification is roughly known too.** The collection lens was the
$f=18$ mm one and nothing else, with $M$ estimated at 2.5–3 (recollection,
2026-07-29, an estimate and not a measurement, with $u$ and $v$ still wanting
a ruler).
That gives $Z_c = 6/M = 2.0$ to $2.4$ mm, and it hangs together: $1/u+1/v=1/f$ with
$M=2.5$–3 puts the lens 24–25 mm from the beam and the photocathode 63–72 mm
behind it, an ordinary side-viewing layout.

**A second recollection, 2026-09-04, states the distances with tolerances**:
$f = 18 \pm 1$ mm and the photocathode in focus at $v = 50 \pm 10$ mm with no
second element, so $M = (v-f)/f = 1.8$, the lens 28 mm from the beam and
$Z_c = 3.4$ mm. The two recollections overlap at one sigma, the July one
sitting at the upper edge of the September tolerance. Propagating $f$, $v$
and the waist band together, since $z_R$ carries the waist squared, the
window is $Z_c/z_R =$
[0.26](../../results/prediction_band.csv "ref:prediction_band:collection_window:z_ratio")
$\pm\ 0.14$, the uncertainty spanning the stated errors, and that is the
value `constants.collection_z_ratio()` now carries into
`results/prediction_band.csv`. Below $u_c = 1/(1+(Z_c/z_R)^2) = 0.94$ the
window binds and the density is exactly the triangle, so the departure lives
in the top 6 per cent of the shift range. Three consequences:

1. **The $Z_c = 2$ mm placeholder this chapter has been carrying sits at the
   lower edge of the September tolerance.** The table rows at $\zeta = 0.15$
   to $0.19$ stand as that edge, and the producer's central value is 0.26.
2. **The dataset's configuration sits at $\zeta = 0.26 \pm 0.14$**, inside
   the transverse-only regime, where the departure from the triangle is a
   signed correction and not a model error: $\kappa_2$ is
   [0.9610](../../results/prediction_band.csv "ref:prediction_band:collection_window:kappa2_ratio")
   of the triangle's and $\kappa_3$ is
   [0.9279](../../results/prediction_band.csv "ref:prediction_band:collection_window:kappa3_ratio"),
   so a fit that assumes the triangle recovers $S_0$ low by
   [-1.97](../../results/prediction_band.csv "ref:prediction_band:collection_window:shift_bias_width_pct")
   per cent through the width channel, which is the channel the 2025 bound
   came through, and by
   [-2.46](../../results/prediction_band.csv "ref:prediction_band:collection_window:shift_bias_k3_pct")
   per cent through the third cumulant. Correcting for the window raises the
   bound. **That sign is conditional and the condition is emitted beside it**:
   $\kappa_3$ falls monotonically through zero at
   [1.117](../../results/prediction_band.csv "ref:prediction_band:collection_window:skew_null_z_ratio"),
   but $\kappa_2$ reaches a minimum near 0.79 and returns to the triangle's
   value at
   [1.691](../../results/prediction_band.csv "ref:prediction_band:collection_window:width_bias_sign_flip_z_ratio"),
   above which the width-channel correction reverses. The 2025 geometry sits
   inside both by factors of four and six. The transit kernel, which varies as
   the inverse local beam radius, has a signal-weighted rms spread of
   [0.97](../../results/prediction_band.csv "ref:prediction_band:collection_window:transit_kernel_rms_spread_pct")
   per cent over the same window, which is the size of the non-convolution
   the composite of [chapter 4](04_the_composite_model.md) neglects.
3. **The proposed flip is near the best the geometry allows**: $+0.56$ at 64 µm
   against $-0.35$ to $-0.39$ at 16 µm, a swing of $\approx0.92$ to $0.95$ in a
   quantity whose full range is $\pm0.57$.

The remaining measurement is $u$ and $v$ (PLAN §4, §6 #4). The solid-angle
weighting varies by under 2% across any such window, so the top-hat form is
fair and the *width* is the only unknown. Geometry permitting, a proposed
session's skew program is then a **sign-flip test between beam
configurations**, $g_1$ positive at the large waist and negative at the small
one, a signature no instrumental asymmetry can mimic because the instrument
depends on $z_R$. At the measured 64 µm 2025 waist the coefficients above
carry only a few-% geometry caveat: its longer $z_R$ makes the ramp nearly the
pure-triangle $Z_c\to0$ limit at $g_1\approx+0.56$, where it was 10 to 40% at
the old 32 µm nominal, and the wider waist only strengthens the
approximation). *Code:*
`stark_ramp_axial()`, table from `scripts/run_ramp_geometry.py`.

#### The axial mixture: one form carries the window and the fringes together

The closed form above is one member of a family. Write the local shift density
on the dimensionless shift $x = s/S(\zeta)$ as $g(x)$, area one on $[-1, 0]$,
equal to $n|x|^{n-1}$ for the transverse law. The window's mixture over the
axial coordinate, with the same signal weight and the same local edge, is

$$f(s) = \frac{1}{S_0}\int_0^{Z_c/z_R} (1+\zeta^2)^{2-n}  g\left(\frac{s (1+\zeta^2)}{S_0}\right) d\zeta ,$$

normalised over $s$. With $g$ the transverse law the integrand is
$n|s|^{n-1}(1+\zeta^2)/S_0^{n}$ below the local edge and zero above it, and the
integral over $\zeta$ is $\zeta_m + \zeta_m^3/3$: the closed form is this
integral done by hand. With $g$ the fringe-resolved density of the next
subsection, the signal-weighted histogram of the standing wave's effective
shift, which reaches $x = -2$ at a perfect retro because a slow atom at an
antinode sees twice the fringe-averaged intensity, the same integral carries
both terms at once, and $Z_c \to 0$ leaves the fringe density alone.
*Code:* `lineshape.ramp_mixture` (the integral, cell-integrated, converging as
one over the number of axial samples at the local edge),
`fringe_tail.fringe_shift_density` (the density, one Monte Carlo per waist,
retro ratio and temperature, independent of $S_0$, with the path factor
divided out so its no-contrast limit is the transverse law), and
`forecast.build_world_trace(z_ratio=..., fringe_density=...)`, off by default
so every committed trace is unchanged. `tests/test_ramp_threading.py` holds
the mixture against `stark_ramp_axial` at the four bench windows and the
density against the pooled moments of the same draws.

#### Standing-wave fringes: why the shift follows the envelope

![the standing wave, its mean and its fringe amplitude, and the gap between them](../../figures/fig25_retro_combination.png)

*The question this subsection answers, and the one it does not. The shift takes
the fringe mean, $1+\rho$, which is what the paragraphs below establish. The
Doppler-free two-photon coupling takes a different combination of the same two
arms, the fringe amplitude $2\sqrt{\rho}$, because only the term whose
wavevectors cancel is Doppler-free. Their ratio is the fringe contrast, which
at this bench's $\rho$ is a correction in the fourth digit and at a poorer
retro is not.*

The retro-reflected beam makes $\lambda/2$ intensity fringes. Does an atom
feel the fringe *peak* intensity (a coherent $\times2$) or the average? The
frequency-modulation criterion ([Stalnaker *et al.*](../lit/stalnaker2006.md), Sec. IV): as an atom
crosses fringes its AC-Stark shift is modulated with peak deviation
$\xi=S_0\lesssim1$ MHz at modulation frequency
$f_\text{mod}=2v/\lambda\approx0.56$ GHz (axial thermal speed $\sim280$ m/s,
fringe spacing $\lambda/2$). The FM modulation index is
$\xi/f_\text{mod}\sim2\times10^{-3}$:
deep in the narrow-band regime, so the shift response is a pure carrier and
the sidebands are negligible and the atom responds to the **time-averaged**
intensity. The shift is thus $\propto(1+\rho)I_{\text{fwd}}$ with $\rho$ the
retro power ratio, with **no coherent fringe enhancement**. (Atoms with axial
speed $\lesssim5$ m/s, 1 to 2% of the signal, are fringe-resolved, which is a
percent-level correction.) The remaining OPEN quantity in $S_0$ is the
measured $\rho$ per beam configuration (in situ at the cell, in a fixed-lock session).

**Why $\rho$ sits close to 1 by design, and what the assumption rests on.** The 2025 retro is a
self-imaging (lens-based) one: the beam is focused into the cell by L1
($f=150$ mm), and a second lens L2 ($f=150$ mm) after the cell maps the cell
waist onto an intermediate waist behind it, since by the Gaussian f–f property a
waist at a lens's front focal plane becomes a waist at its back focal plane,
here $w_0'=\lambda f/(\pi w_0)\approx0.74$ mm for $w_0=64$ µm. A **flat**
mirror placed at that flat wavefront *time-reverses* the beam, so it retraces
back through L2 and re-forms the original 64 µm cell waist. The forward and
return modes therefore match **by construction**, and $\rho$ falls below 1
through losses (two further L2 passes, two further window passes, mirror
reflectivity) and through whatever superposition imperfection the alignment
leaves. Since v3.0.0 the code assumes $\rho=0.94\pm0.04$ rather than the
design value 1, because the design argument covers mode matching and not
loss. The arrangement is also forgiving:
that intermediate beam has $z_R'\approx2.8$ m, so the "mirror at the waist"
condition holds to within tens of centimetres, and residual sensitivity is
dominated by mirror *tilt*, not longitudinal placement. (The 2019 reference
measurement on this line achieves the same self-imaging with a concave mirror
at $2f$ instead of a lens plus flat mirror, which is a different implementation
of the identical idea, `LITERATURE.md` §6a.) Note the design must be *re-established
per waist* in a fixed-lock session: L2 has to sit a focal length from the new waist, and the
intermediate beam grows to $\approx3$ mm at $w_0=16$ µm, so return-path
clipping is the thing to watch (PLAN §4).

How much would a departure from the assumed $\rho$ actually cost? Less than
one might fear, and the dataset's own signal quality provides indirect
evidence. Since $S_0\propto(1+\rho)$, *any*
$\rho\in[0,1]$ moves the prediction only between 0.18 and 0.36 MHz, a factor
of two end-to-end, and the recorded bound ($S_0(225\ \text{mW})$ below 0.26 MHz,
[what we found](07_what_we_found.md))
brackets the whole range, so no conclusion in the record turns on it. Better, the
Doppler-free *rate* scales as $\rho$ itself (it needs one photon from each
direction, so the signal $\propto I_\text{fwd}I_\text{bwd}$), not as $1+\rho$:
a badly mismatched retro would have destroyed the signal long before it
appreciably moved the shift, so the dataset's strong, clean lines are
evidence that $\rho$ is not small. The asymmetry is worth
remembering: the retro threatens the *signal* far more than the *coefficient*.
It matters for a fixed-lock session precisely because the coefficient is then the point:
$\rho$ is measured in situ, per configuration (return-path clipping differs
with waist), before any $\Delta\alpha$ in physical units is quoted.

#### The coefficient (field-intensity convention, pinned)

The ramp *shape* and its centred moments are convention-free, but the
*magnitude* of $S_0$, which converts a measured centroid pull into the
differential polarizability $\Delta\alpha=\alpha_{6S}-\alpha_{5S}$, needs the
$\langle E^2\rangle$ convention fixed. We adopt the standard AMO one ([Grimm
*et al.*](../lit/grimm2000.md) 2000, [Steck](../lit/steck_rb.md)): for $E(t)=E_0\cos\omega t$, $\langle E^2\rangle=E_0^2/2$,
so $\Delta E_i=-\tfrac14\alpha_i E_0^2=-\alpha_i I/(2\varepsilon_0 c)$ and

$$S_0=\frac{\Delta\alpha\ I_\text{eff}}{2\varepsilon_0 c h},\qquad
I_\text{eff}=(1+\rho)\frac{2P}{\pi w_0^2}$$

With $\Delta\alpha=1093$ a.u. ([Orson *et al.*](../lit/orson2021.md) 2021) this is $S_0=0.35$ MHz (transition) at 225 mW,
$w_0=64$ µm (the accepted prior, where it read 0.59 at the replaced 50 µm and
1.43 at the 32 µm nominal before that) and
$\rho=0.94$, growing to 5.6 MHz at $w_0=16$ µm. The on-axis $\propto S_0^3$
scaling above is the *pure transverse triangle*. At a small waist the axial
average over the collection window changes the third cumulant's magnitude and,
past $Z_c/z_R\approx1.12$, its sign, so the small-waist gain is not the naive
$\times 64$ (see the geometry discussion below and PLAN §6 #4). The **sign** is
convention-independent, set by $\text{sign}(\Delta\alpha)$, red for Orson's
published positive $\Delta\alpha$. That sign is itself under adjudication: an
independent sum-over-states recompute here agrees on magnitude to within 5% but
returns a negative $\Delta\alpha$, which is a **blue** shift
([`THEORY_NOTE.md`](../THEORY_NOTE.md) §5). Every recorded result quoted in this
repository is unaffected, because the asymmetry null is symmetric and both the
$S_0$ bound and its prediction band use $|\Delta\alpha|$. *Code:* `lineshape.stark_shift_S0_mhz()`. The full
theorist-facing derivation, novelty position, and the open diverging-beam
question are in [`docs/THEORY_NOTE.md`](../THEORY_NOTE.md).

#### One dressing, many teeth: what the modulation depth can and cannot move

The ramp above is set by the intensity, and an electro-optic phase modulator
changes the spectrum of the light without changing its intensity. That is one
sentence of physics with a campaign design inside it, so the derivation
follows.

**The dressing is common to every tooth and independent of the depth.** Write
the modulated field as $E(t)=E_0e^{i(\omega t+\beta\sin\Omega t)}$. Its modulus
is $E_0$ at every instant, so the intensity is constant in time and constant in
$\beta$, and a shift proportional to intensity cannot move when only $\beta$
moves. In the frequency picture the same fact is a sum rule. The sidebands
carry fractions $J_k(\beta)^2$ of the intensity, these sum to one, and the
level shift is the sum over components

$$\Delta = -\tfrac{1}{4}\sum_k \alpha(\omega+k\Omega)|E_k|^2 = -\tfrac{1}{4}|E_0|^2\left[\alpha(\omega)+\tfrac{1}{4}\alpha''(\omega)\beta^2\Omega^2\right],$$

because $\sum_k J_k(\beta)^2 k = 0$ kills the first-order term and
$\sum_k J_k(\beta)^2 k^2 = \beta^2/2$ sets the second. The correction is
relative $(\beta\Omega/\Delta_{\rm res})^2/2$ with $\Delta_{\rm res}$ the
detuning from the nearest resonance, which for this line and drive is of order
$10^{-14}$: the depth-independence of the light shift is exact for any purpose
this record has.

**What the depth does move is the excitation rate, tooth by tooth.** The
two-photon amplitude into the tooth at sum order $k$ is the coherent sum over
sideband pairs, $\sum_n J_n(\beta)J_{k-n}(\beta) = J_k(2\beta)$ by the addition
theorem, so the rate follows $J_k(2\beta)^2$
([the ruler](05_the_frequency_ruler.md), and
[EOM sidebands](../wiki/eom-sidebands.md) for the theorem). Those weights sum
to one as well, which gives the second sum rule: **in the linear regime the
summed signal over all teeth is the same at every depth**, and the distribution
over teeth is what the depth chooses.

**So the depth axis splits the model into families with three different
scalings, and that is more than it first appears.** The light shift and its
ramp shape are set by the whole spectrum, so they do not move with depth at
all. The tooth amplitude, the cascade depletion of
[the cascade](../wiki/the-cascade-and-f-depletion.md) and radiation trapping
follow the tooth's excitation rate, so they move as $J_k(2\beta)^2$. **Power
broadening sits between them**: the resonant two-photon Rabi frequency of the
tooth at order $k$ is $J_k(2\beta)$ of the line's, being an amplitude and not a
rate, so the companion width the saturation adds moves as the square root of
the rate share. The transit, laser and collisional widths follow none of the
three. **On a ladder in power the shift and the power broadening move together and
not apart**: a
two-photon Rabi frequency goes as the intensity, the same power of $P$ as the
shift, so the power broadening is proportional to the shift along the whole
ladder and no exponent separates them. The rate is the only one with a
different power, $P^2$. **A ladder in depth at fixed power gives each of the
three a different and known dependence on one knob, $1$, $J_k(2\beta)$ and
$J_k(2\beta)^2$, with the shift exactly fixed.** That is the degeneracy the
lever breaks, and it is a different degeneracy from the three-width one, which
no rate-driven knob can touch because none of those widths is rate-driven.

Three tests follow, and each of them is a null.

1. **The fitted centre against depth, at fixed power, is flat.** A slope is not
   a light shift, since the light shift cannot depend on depth. It is residual
   amplitude modulation or a rate-dependent pull, and it is reported as a bound
   on that channel.
2. **The summed tooth areas are the same at every depth.** A deficit is
   depletion and trapping, measured with the dressing held fixed, which no
   power ladder can arrange.
3. **The carrier null.** Where $2\beta$ reaches the first zero of $J_0$ the
   carrier's rate vanishes while the intensity is untouched. Signal left at the
   carrier position is residual amplitude modulation or the retro-delay
   smearing of the weights, both of which
   [the two-photon comb](../wiki/the-two-photon-comb.md) already quantifies.

**The blind regions, named.** Residual amplitude modulation breaks the premise
outright, because an amplitude-modulated field does not have constant
intensity, which is why test 1 returns a measurement of that admixture and
never an assumption about it. The depth is read from the tooth heights on the same
trace, so the abscissa is self-calibrating under pure phase modulation and
wrong by the same admixture when it is not. And with the modulator in the
common path the weights follow an effective depth $2\beta\cos(\pi f\tau)$ over
the cell's spread of retro delays $\tau$, so the depth a comb reports is a cell
average whose spread grows as $(\pi f\tau)^2$ with the drive frequency.

This section is physics and mathematics, the first two rungs. What each test
buys in coefficient units is a twin question, and the campaign case takes it
there.

#### The waist as the second axis, and what a known magnification buys

The depth moves the spectrum of the light. The other knob moves its geometry,
and the two are complementary because they separate different terms.

**The problem it attacks is the one this record calls its largest.** Every
absolute quantity here is conditional on $w_0$, which was never measured on
this bench, and a scan across configurations catches only relative waist
errors while a common scale error passes silently
([the plan's light-shift chapter](../plan/04_intensity-and-light-shift.md)
section 5 states it in those words).

**The knob.** An adjustable beam expander ahead of the cell scales the waist by
its magnification $M$ at fixed power and fixed retro ratio, so
$w_0(M) = Mw_0^{\rm ref}$. **The abscissa is then known even though its scale is
not**, because a telescope's magnification is a ratio of focal lengths and can
be checked by imaging, while the absolute waist needs a knife edge and carries
its own systematics.

**Every term of the model scales with a different power of that knob.** With
the temperature and the power held, and $v_{\rm th}$ fixed by the first:

| term | law | power of $w_0$ |
|---|---|---|
| collisional and laser widths | independent of the beam | $0$ |
| transit FWHM | $\ln 2 v_{\rm th}/\pi w_0$ | $-1$ |
| the peak light shift $S_0$ | $\propto I \propto P/w_0^2$ | $-2$ |
| the two-photon Rabi frequency, and the power broadening that follows it | $\propto I$ | $-2$ |
| the axial collection ratio $L/z_R$, since $z_R=\pi w_0^2/\lambda$ | $\propto 1/w_0^2$ | $-2$ |
| excitation cycles in one crossing | rate $\times$ crossing time $\propto I^2w_0$ | $-3$ |
| the two-photon rate per atom | $\propto I^2$ | $-4$ |

Five distinct exponents. A ladder in power has only two, since every term there
is $P$ or $P^2$, so the geometry axis is strictly the richer one, and each row
above is a check of the code that carries it
(`constants.transit_fwhm_from_w0`, `stark.stark_shift_S0_mhz`,
`hyperpolarizability.two_photon_rabi_hz`, `constants.collection_z_ratio`).

**What the known magnification buys, precisely.** Each term becomes a known
function of one unknown, $w_0^{\rm ref}$, so a joint fit across settings
measures it, and measures it twice: the transit width scales as $1/M$ and the
light shift as $1/M^2$, and the two must agree. Their agreement is a test of
the transit law where the record's present anchor, a differential transit width
at one setting, has to assume it.

**And the collected signal does not scale the way the naive count says.** The
two-photon signal collected through an axial half-window $L$ is

$$S \propto \int_{-L}^{L} \int I^2 dA dz = \frac{2P^2}{\lambda}\arctan\left(\frac{L}{z_R}\right),$$

because $\int I^2 dA = P^2/\pi w(z)^2$ and $z_R=\pi w_0^2/\lambda$. The window
is fixed by the detector and the Rayleigh range shrinks as $M^2$, so tightening
the beam gains far less than $M^{-2}$: over the record's own span of waists a
fourfold tightening multiplies the integrated signal by about five, and it
saturates from there, since a window that already swallows the beam cannot
swallow more of it.

**The peak height is the interesting one, and it turns over.** The line does not
broaden with the transit alone, and at these conditions the transit is about a
fifth of the composite width, so quadrupling it widens the line by well under a
factor of two and the peak height rises, by about three over the same span.
What turns it over is the ramp itself: the light shift grows as $M^{-2}$, so
below a waist near a third of the record's it broadens the line faster than the
collection gains photons, and the peak height falls again. The maximum sits
inside the range the campaign proposes while the integrated signal is still
climbing, so **a tight waist is a shift lever and a signal lever both**, and the
two do not want quite the same waist. Computed through the record's own
composite profile at its measured collisional and laser widths, which is the
correction a first draft of this section needed: it divided the collected
signal by the transit width instead of the line's, and concluded that the peak
height fell.

**What it does not do.** It does not separate the light shift from the power
broadening: both follow the intensity, so both scale as $M^{-2}$ and their
ratio is fixed along the whole ladder, exactly as it is along a power ladder.
The depth ladder above is the knob for that pair. And it does not touch the
collisional-against-laser split, which no beam geometry moves.

**The blind regions, named.**

1. **The retro ratio.** The shift takes $(1+\rho)$ and the two-photon coupling
   $2\sqrt{\rho}$, so an unmodelled $\rho(M)$ moves them differently and would
   be read as a waist error. Expanding the beam changes the returning mode's
   overlap unless the retro is re-matched, so $\rho$ is measured at each
   setting or the setting is not usable.
2. **The collection window moves with the knob.** $L/z_R$ scales as $M^{-2}$,
   so the ramp's own shape changes along the ladder, and this chapter's axial
   analysis has the third cumulant reversing sign above a ratio near one. A
   fourfold tightening from the 2025 bench crosses that boundary. For a joint
   fit that is a second computable function of the same knob. For the skew
   channel alone it is a trap.
3. **The expander itself.** Its magnification accuracy, its thermal behaviour
   under the beam and whether it preserves the mode quality are apparatus
   facts, and [the open items](../plan/12_open-apparatus-items.md) carries
   them.
4. **The rate-driven terms are largest where the shift is largest**, since
   depletion grows as $M^{-3}$ against the shift's $M^{-2}$. The depth ladder
   at the tightest setting is what separates those two.

This section is the first two rungs as well. The twin's amplitudes are
caller-owned and carry no waist dependence of their own, so the signal law
above is analytic here and is owed to a producer before any forecast quotes it.

---

**Where the numbers live.** Modules M16, M19 · producers
`scripts/run_ramp_geometry.py`, `scripts/run_polarizability.py`,
`scripts/run_cumulant_window_check.py`, and `scripts/run_waist_ladder.py`
for the waist axis of the subsection above · results
`results/waist_ladder.csv` ·
`results/polarizability.csv` · figures: `fig24_weak_field_limit.png` for the
regime this law holds in and `fig25_retro_combination.png` for the intensity
convention behind $S_0$. Library code:
`rb5s6s/lineshape.py`, for `stark_ramp()`, `stark_ramp_axial()` and
`stark_shift_S0_mhz()`, with the independent closed forms held as tests.

**What would falsify this.** A measured skewness of the same sign at both beam
configurations. The sign flip is set by $Z_c/z_R$ and by nothing an
experimentalist can tune independently, so a sign-preserving pair would refute the
diverging-beam form, and a skew magnitude away from the tabulated one at a
measured $Z_c$ would refute the $n=2$ weighting the whole law rests on.

[← The lineshape, kernel by kernel](02_the_lineshape.md) · [The composite model →](04_the_composite_model.md)
