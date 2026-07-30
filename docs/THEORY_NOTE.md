# Theory note — the AC-Stark "ramp" lineshape of a focused two-photon transition

*A short, self-contained note for a theoretical check and contribution. The
backing pipeline and data live in this repository; nothing here depends on
reading the code. Notation follows the README; every frequency is on the
two-photon **transition axis** (twice the laser frequency) unless stated.*

## 1. What this note asks

We drive the Doppler-free $5S_{1/2}\to 6S_{1/2}$ two-photon transition in a Rb
vapour cell with a **focused, retro-reflected** 993 nm beam. Because the
excitation rate goes as the square of a spatially inhomogeneous intensity, the
distribution of AC-Stark shifts across the illuminated atoms is not a single
number but a **skewed distribution with a closed form**. This note derives that
form, its moments, the drift-immune way we extract it from a lock too unstable
to hold a line centre, and the field-intensity convention that fixes its
coefficient. It closes with **one genuinely open theoretical question** — the
survival of the closed form under the real collection geometry — which is the
natural place for a contribution.

## 2. The ramp law

Let the two-photon excitation rate be $\propto I^{n}$ with $n=2$ (one power of
$I$ per photon), and the light shift of the transition be $s = -\kappa I$ with
$\kappa>0$ (red shift; sign discussed in §5). In a Gaussian beam
$I(r)=I_0 e^{-2r^2/w_0^2}$, put $u \equiv I/I_0 \in (0,1]$. The signal from the
annulus $[r,r+dr]$ is

$$dS \propto I^{n}(2\pi r\ dr) \propto u^{n} r\ dr$$

Changing variable with $du/u = -(4r/w_0^2)\ dr$ gives $dS \propto u^{n-1} du$,
and with $s=-S_0 u$ (where $S_0=\kappa I_0$ is the on-axis maximum shift) the
**signal-weighted shift distribution** is

$$\boxed{\ f(s) \propto |s|^{n-1}\quad\text{on}\quad s\in[-S_0,0]\ }$$

For $n=2$ this is the **triangular ramp** $f(s)=2|s|/S_0^2$. The same $dS\propto dI/I \cdot I^{n}$ argument holds for any monotonic $I$ profile that is flat in
one coordinate — including the exponential evanescent field of a nanofibre —
which is the bridge to the fibre geometry (Paper 2). Normalising, the moments
follow by direct integration:

$$\langle s\rangle = -\tfrac{2}{3}S_0,\qquad
\mathrm{Var}(s) = \tfrac{1}{18}S_0^2,\qquad
\kappa_3 = +\tfrac{1}{135}S_0^3$$

so the ramp's **intrinsic standardised skewness** is the pure number

$$g_1 = \frac{\kappa_3}{\mathrm{Var}^{3/2}} = \frac{18^{3/2}}{135} \approx +0.566$$

independent of $S_0$ — a property of the **ramp component's shape**, a
diagnostic, not a standardised skewness of the observed line (which is
ill-defined; see §3). The one-photon case $n=1$ (e.g. a Stark-induced forbidden
line) gives the **uniform** distribution, $\langle s\rangle=-S_0/2$ and
$\kappa_3=0$ — **exactly zero skew**. The skewness observable therefore exists
*only because the two-photon rate goes as $I^2$*; that is the sharpest statement
of what is specific here.

### 2.1 Does the atoms' motion wash the ramp out? (M19)

The derivation above is **quasi-static**: each atom sits at one intensity and
carries one shift. Real atoms cross the beam, sweeping their own shift from
zero to the on-axis maximum and back within a transit time (~0.2 µs at
$w_0\approx 50$ µm) that is only a few times the
natural response $1/\Gamma\approx 45$ ns. Camparo and Lambropoulos (JOSA B **9**, 2163 (1992)) show for
a two-photon transition in a fluctuating field that this ratio decides the
answer: slowly-varying intensity gives an asymmetric line, rapidly-varying
intensity averages to a symmetric one at the mean shift. So the composite model
convolving a static ramp with a transit lineshape needs a justification, not an
assumption — the two factors describe the same atom crossing the same beam.

**It survives, and the reason is a change of variables.** An atom's impact
parameter $b$ and its displacement $vt$ along the flight direction *are* the
transverse plane, and $\mathrm{d}b\mathrm{d}(vt)$ *is* the area element; a
uniform-density ensemble weighted by crossing flux therefore samples exactly
the spatial measure the static derivation integrates over. Motion re-labels
which atom carries which shift without changing the distribution over shifts.

Because that argument still assumes the atom's spectrum reflects the shifts it
samples — the very quasi-static step at issue — **M19**
(`rb5s6s/ramp_transit.py`) checks it without that assumption, propagating the
weak-excitation amplitude with the phase integrated along each trajectory. The
static triangle's first two moments are recovered to $\sim0.1$% across
$S_0/\mathrm{transit\ FWHM}$ from $0.09$ to $7.6$ — from far inside the
non-adiabatic regime to far inside the adiabatic one. The first-moment
invariance is in fact exact for any modulation, since the mean of a power
spectrum is the coupling-weighted mean instantaneous frequency; the second
moment is the substantive check, and it is what licenses the convolution.

**The real geometry adds two more complications, and the pull survives both.**
The beam is retro-reflected, so it is a standing wave whose $\lambda/2$ fringes
modulate the shift; and the atoms carry a thermal spread of speeds, not one
speed.

- *Standing wave.* The fringe modulates the **shift**, which follows the total
  $|E_+ + E_-|^2$ over the full fringe period, but not the **coupling**: the
  Doppler-free rate takes one photon from each counter-propagating beam, so it
  goes as $I_+I_-$ and is $z$-uniform. M19 recovers the triangle in both
  limits — fringes swept fast by an axial atom (~113 per transit, the
  experiment's ~0.56 GHz against a ~5 MHz transit rate) and the frozen fringe
  of a near-transverse atom sampled over the node–antinode arcsine. That
  independently confirms the fringe-immunity of the **mean** asserted in
  `constants`; the fringe's suppression of the **skew** is a different and
  non-null question, quantified separately in M15.
- *Maxwell–Boltzmann.* Only the ratio $S_0/(v/w)$ enters, so the sweep above is
  itself a sweep over transverse speed spanning ~80×, bracketing the thermal
  distribution. Every speed class shares one mean and one ramp variance and
  differs only in transit width, so any mixture inherits both — checked
  directly against a flux-weighted Maxwell–Boltzmann sample.

The third cumulant — the one the asymmetry claim rests on — is **not** resolved
by that simulation: the FFT noise floor weighted by $\nu^3$ swamps it. For
$\kappa_3$ the change-of-variables argument stands alone, and it carries the
quasi-static assumption. The fringe's effect on $\kappa_3$ is M15's result, not
this one's.


![the ramp construction](../figures/fig12_ramp_construction.png)

*From a Gaussian beam to a triangular shift distribution. (a) the intensity
profile sets each atom's shift, from zero at the dim edge to $-S_0$ on axis;
(b) the two weights that compete — many atoms sit at low intensity, but each
contributes only $I^2$ of signal, and the product is linear in $u$; (c) hence
$f(s)\propto|s|$, a triangle with mean $-\tfrac{2}{3}S_0$ and intrinsic skew
$+0.566$, which exists at all only because the rate goes as $I^2$; (d) the line
it produces, with $S_0$ exaggerated so the asymmetry is visible.*

## 3. The drift-immune method

The 2025 archival line walked at the MHz scale between scans — hand
re-centrings riding a measured constant $\sim$0.02 MHz/min drift
(`APPARATUS.md` §6) — so absolute line **centres** are dead, and a fit must
give each scan its own free centre to absorb that motion. This has a sharp consequence for the ramp. Its **first-order effect is a
shift** of the line (the centroid pull $-\tfrac23 S_0$), and a shift is exactly
what a per-scan free centre absorbs — so in the drifted archive the pull is
**degenerate with the drift and not a usable handle** on $S_0$. What survives is
the ramp's **shape asymmetry** (its skew), which no free centre can absorb
because it is not a translation. That is the drift-immune observable, and it is
the methodologically specific point (§6): the light shift is read from a
drift-invariant *shape*, not from a line position the drift has destroyed.

The extraction is a **model fit, not a moment computation**: the full lineshape
(ramp $\otimes$ symmetric core) is fit with a per-trace free centre and a
shared **asymmetry coefficient** — the amplitude of the ramp skew, equivalently
$S_0$. Computed from the fitted function rather than the raw trace it stays
finite and window-independent — the Lorentzian wings that make a raw-data
skewness divergent never enter. The residual systematic is then
**core-model-dependence**: the fitted asymmetry depends on the assumed core, and
a wrong core (Voigt where the truth is Voigt$\otimes$transit-cusp) trades
against it — but unlike raw-moment window-dependence, that is *checkable*, by
BIC and the M8 cusp fit. The reference moments the fit encodes,

$$\text{centroid pull} = -\tfrac{2}{3}S_0,\qquad
\kappa_3^{\text{ramp}} = +\tfrac{1}{135}S_0^3$$

order the signal by statistical cost — pull $\propto P$, excess variance
$\propto P^2$, skew $\propto P^3$ (the last vanishing unless $n=2$, the $I^2$
signature) — but note the pull as a *measurement* is available only once a
stable lock (a fixed-lock session) un-absorbs it. **The centre channel gives no
bound either** (M21, `scripts/run_stark_centres.py`, 2026-07-30). A peak position
is a frequency only within a *display epoch* — a run of unchanged scope
horizontal position, see `run_laser_history.py`'s retraction — so each epoch
carries a free offset, and of the 26 epochs covering the power sweep only three
contrast two powers, none spanning two lines. The pull is then unidentifiable
rather than imprecise: its sign REVERSES between drift models
($+3.45$ vs $-3.26$ MHz/W) and the limit degrades as the drift model gains
freedom, $|S_0(225$ mW$)| < 9.50$, $14.59$, $17.67$ MHz for linear,
one-exponential and two-exponential drift. Tagged NULL. Earlier
state-space versions of this bound — $3.5$ MHz in addendum 6, $5.5$ MHz under
addendum 7's mixture, and a $7.3$ MHz variant in M20 — were *tighter* only
because they differenced centres across horizontal-position moves, and are
withdrawn. The width channel's $S_0(225$ mW$) < 0.63$ MHz is the archive's only
light-shift channel; there is no second channel to corroborate it.

Two caveats. *Between*-scan drift is absorbed exactly by the free centres.
*Within*-scan drift is not a pure translation — it smears the line
asymmetrically in a scan-direction-dependent way that couples the fitted centre
to the fitted asymmetry; at the established $\lesssim0.1$ MHz within-scan drift
this is small, but because the asymmetry is itself small it must be *estimated*,
not assumed zero. A synthetic closure test now bounds it rather than the
timescale argument alone (`tests/test_intrascan_drift.py`): the drift is injected
into a synthetic scan and the asymmetry recovered through the same free-centre
fit, so the linear sweep warp lands in the fitted width and only the residual
curvature can skew. At the archival within-scan drift the fitted ramp
coefficient shifts by **well under a fifth of its SNR-limited statistical
error** — a few $\times 10^{-3}$ on $S_0$ for the dominant linear part — and
reaches order-$S_0$ only at tens of times the archival rate. The within-scan
skew is therefore bounded and small, not unmodelled.

**Status.** In the 2025 sweep the fitted asymmetry coefficient is **consistent
with zero**: at $\le225$ mW its significance (the skew grows only as $S_0^3$)
sits below the SNR $\approx130$ floor, so the estimator — correct as it is —
returns an **upper bound, not a detection**. A fit always returns *some* value
with an error bar; the discipline is to report a bound unless it clears that
bar, which at archival intensity it does not. A fixed-lock session changes this two ways:
the fixed lock **recovers the first-order pull** ($-\tfrac23 S_0 \propto P$, a
$\sim$MHz shift against a stable reference — the primary $S_0$ measurement, no
longer absorbed by a free centre); and the small waist, where $S_0$ is $\approx10\times$
larger, lifts the shape asymmetry into a **detection** — though not by the naive
$S_0^3$ factor of 64: the axial average changes the third cumulant's magnitude
and, for a long enough collection window, its sign (§7). Both are *conditional on the small-waist skew corrections
— the beam-divergence collection average of §7 (the larger, sign-flipping one)
and the standing-wave fringe-resolved tail of §5, same-sign and fit jointly* —
which move the ramp form — and the pull coefficient off $-\tfrac23$ — at small
waist, and must be applied before $S_0$, hence $\Delta\alpha$, is read.

**The hybrid, made principled.** The three cumulants are not three rival
measurements to be combined or cherry-picked — they are three analytic
functionals of the *one* parameter $S_0(P)$ (`lineshape.ramp_moment_contributions`):
pull $\propto S_0$, excess variance $\propto S_0^2$, third cumulant $\propto S_0^3$. The fixed-lock fit uses a single $S_0$ per condition and checks that the pull,
excess-variance and third-cumulant *measured from the data* are mutually
consistent with it — a $\chi^2$ across the moment hierarchy. The primary
observable at each intensity is pre-registered as the lowest-order moment above
its own noise floor (pull where $S_0$ is small, the skew only where $P^3$ has
climbed clear of noise); the others are consistency checks with their own error
bars. A spurious
asymmetry from a fit artifact or the diverging-beam geometry will not *also*
reproduce the correct, more-robust lower-order pull and variance for the same
$S_0$, so the claim is never "we measured the skew" but "pull, variance and
skew are jointly consistent with one triangular ramp of amplitude $S_0(P)$."
(The extraction stays single: one fitted profile per condition, three
functionals of it — never several estimators of one moment.)

## 4. The prediction tested against the archive

At fixed density the archive tests the *convention-free* content, and is consistent with it:
across a $9\times$ power sweep the linewidth is flat to $\lesssim2$% (the ramp
adds variance $\propto S_0^2$, negligible against the $\sim$5 MHz budget), and
the amplitude scales as $P^{2}$ (log-log slopes 1.83–2.12). The asymmetry is
predicted below the archival noise and is not detected — as designed.

That flatness is not merely a null. Fitting one shared $S_0=\kappa P$ to the
four peaks' width-vs-power (`stark.fit_stark_sweep`, M4e) turns it into a
quantitative **upper bound $S_0$(225 mW) $<0.63$ MHz (95%, profile
likelihood)**; the fitted value is consistent with zero, so the archive *brackets* the predicted
$0.59$ MHz (§5) without resolving it. It is a bound, not a measurement, for the
same two-epoch reason as everything else here: the 2025 drifted lock destroys the
line centres, so the pull $\propto S_0$ — the sensitive handle — is absorbed by
each trace's free centre, leaving only the ramp's $\propto S_0^2$ width
broadening (a $0.6$ MHz $S_0$ inflates a $5$ MHz line by $<0.1$ MHz). Through the
§5 convention, at the nominal $w_0=50\ \mu$m this brackets $\Delta\alpha$ below
$\sim1.1\times$ the computed value ($<\sim1200$ a.u., 95%, profile likelihood;
the earlier $\sim5800$ came from a Wald interval evaluated at the $\kappa=0$
rail, where it has no valid coverage) — consistent with
$1093$, with the mapping inheriting the open $w_0$. So the archive **does not
contradict** the computed $\Delta\alpha$; a fixed lock would measure the pull
$\propto S_0$ directly (small waist $\Rightarrow S_0$ $\approx10\times$ larger),
turning this bracket into the coefficient.

## 5. The coefficient (the field-intensity convention, pinned)

The shape and centred moments above are convention-free. The **magnitude** of
$S_0$ — needed to turn a measured pull into a differential polarizability
$\Delta\alpha = \alpha_{6S}-\alpha_{5S}$, or to predict $S_0$ from a computed
$\Delta\alpha$ — requires fixing the $\langle E^2\rangle$ convention. We adopt
the standard AMO one ([Grimm, Weidemüller & Ovchinnikov](lit/grimm2000.md), *Adv. At. Mol. Opt.
Phys.* **42**, 95 (2000); [Steck](lit/steck_rb.md)): for a real field $E(t)=E_0\cos(\omega t)$ the
time average is $\langle E^2\rangle = E_0^2/2$, and

$$\Delta E_i = -\tfrac{1}{2}\alpha_i\langle E^2\rangle
= -\tfrac{1}{4}\alpha_i E_0^2
= -\frac{\alpha_i I}{2\varepsilon_0 c}$$

$$\boxed{\ S_0 = \frac{\Delta\alpha\ I_{\text{eff}}}{2\varepsilon_0 c h},\qquad
I_{\text{eff}} = (1+\rho)\frac{2P}{\pi w_0^2}\ }$$

Here $I_{\text{eff}}$ is the **time-averaged** on-axis intensity of the forward
plus retro beams, $\rho$ the retro power ratio. There is **no coherent
$\times2$ standing-wave enhancement**: a *fast-axial* atom crosses the
$\lambda/2$ fringes at $2v_z/\lambda\sim0.56$ GHz (mean axial speed) while the
shift depth is $\lesssim1$ MHz, so its frequency-modulation index is
$\sim2\times10^{-3}$ — in [Stalnaker](lit/stalnaker2006.md)'s FM framework (*Phys. Rev. A* **73**,
043416 (2006), Sec. IV), the small-modulation-index limit puts the carrier at
the fringe-*mean* intensity, so $I_{\text{eff}}$ **is** that standing-wave mean
and the pull is exactly fringe-immune. But the line is Doppler-free over **all** $v_z$, so
near-transverse atoms sit at a frozen fringe and sample the node-antinode
arcsine: a fringe-*resolved* tail (weight $f_\text{res}$) that keeps the mean
but, because the fringe *multiplies* the shift $s\to s(1+x)$ with $x$ arcsine,
**suppresses** the ramp skew — $\kappa_3\to S_0^3(1/135-f_\text{res}/10)$ at
$\rho=1$ (a $-13.5 f_\text{res}$ fractional leverage $\propto$ contrast$^2$; only
$P=f_\text{res}\sigma_x^2$ is observable). Negligible at $w_0=50\ \mu$m
($\sim$9–14% of an already-below-noise skew, `results/fringe_tail.csv`),
$\sim$26–28% at $16\ \mu$m, and
**same-sign-additive** to the larger §7 divergence correction — the two must be
fit jointly at small waist (quantified, coherence-window-bracketed, in
`fringe_tail`). With $\Delta\alpha = 1093$ a.u.
([Orson *et al.*](lit/orson2021.md) 2021, sourced below) this gives $S_0 = 0.59$ MHz (transition) at $P=225$ mW, $w_0=50\ \mu$m,
$\rho=1$; it grows to $5.7$ MHz at $w_0=16\ \mu$m, which is why a small waist
lifts the ramp asymmetry to a detection — but *not* by the on-axis $S_0^3$
factor of 64, since the axial average over the collection window changes the
third cumulant's magnitude and, past $Z_c/z_R\approx1.12$, its sign (§7). Code: `lineshape.stark_shift_S0_mhz`.

**Sign, and provenance.** The $\langle E^2\rangle$ convention is magnitude-only;
the *direction* of the pull is set by $\mathrm{sign}(\Delta\alpha)$. **$\Delta\alpha$
is [Orson *et al.*](lit/orson2021.md) 2021's published value** (*J. Phys. B* **54**, 175001 — prior art
on this exact 5S–6S line): they compute $\alpha_{56}=\alpha_{5S}-\alpha_{6S}=-1093$
a.u. "in a manner similar to [Martin 2019](lit/martin2019.md)," so our $\Delta\alpha=\alpha_{6S}-\alpha_{5S} =+1093>0$ (6S pulled down more than 5S $\Rightarrow$ red shift $\Rightarrow$ $S_0>0$).
This was formerly flagged as the number most wanting a theorist's check; it is now
(a) a **cited** value on our exact transition and (b) **cross-checked** — our
`stark_shift_S0_mhz` reproduces Orson's own $-0.66$ MHz shift prediction (0.8 W,
63 µm) to the digit (`test_stark_S0_reproduces_orson2021`).

**The independent recompute now exists in-repo** (`rb5s6s/polarizability.py`,
M16): a sum-over-states model from Safronova-lineage matrix elements, validated
on anchors it does not use — it reproduces the *measured* 5S scalar tune-out
790.03235 nm to $\approx2$ pm, the measured static $\alpha_{5S}=318.79(1.42)$,
and the Safronova-group static $\alpha_{6S}=5167(22)$. It **confirms the
magnitude**, $|\Delta\alpha(993)| = 1145$ a.u., within 5% of Orson's 1093 —
**but finds the opposite sign**: $\alpha_{6S}(993)\approx-330$ a.u. (the
dominant 6S couplings, 6S–6P at 2.73/2.79 µm, are driven far blue-detuned at
993 nm, pushing 6S *up*, while 5S is pushed *down*), so
$\Delta\alpha=\alpha_{6S}-\alpha_{5S}<0$ and the light shift of the transition
is **blue**, not red. Every archival result is sign-immune (C3c is a symmetric
null; C3d and the prediction band use $|\Delta\alpha|$), but the fixed-lock
*pull direction* and the ramp's stated side depend on it. The discrepancy with
Orson's printed $\alpha_{56}=-1093$ is flagged for adjudication (the decisive
check is one line for a theorist: the sign of $\alpha_{6S}$ at 993 nm)

> **Convention table — read this before comparing any α with the literature.**
> An external audit (2026-07-26) proposed that the whole Orson disagreement was
> a convention artifact. It is not — but a careful reader did reach that
> conclusion from the published material, so every definition is stated
> explicitly here:
>
> | symbol | definition here | value at 993 nm |
> |---|---|---|
> | $\alpha_{5S}$, $\alpha_{6S}$ | scalar polarizability of each level | $+832$, $-312$ a.u. |
> | $\Delta\alpha$ | $\alpha_{6S}-\alpha_{5S}$ (**excited minus ground**) | $-1145$ a.u. |
> | $\alpha_{56}$ (Orson's) | $\alpha_{5S}-\alpha_{6S}$ (**ground minus excited**) | $=-\Delta\alpha$ |
> | level shift | $\delta E = -\tfrac{1}{2}\alpha E^2$ | — |
> | transition shift | $-\tfrac{1}{2}\Delta\alpha E^2 \equiv +\tfrac{1}{2}\alpha_{56}E^2$ | — |
>
> The last row is the point: **both conventions give the same formula**, so the
> algebra is not in dispute. Orson prints $\alpha_{56}=-1093$, hence a *red*
> transition shift; this work computes $\Delta\alpha=-1145$, i.e.
> $\alpha_{56}=+1145$, hence a *blue* one. Same equation, opposite input, and
> **Both sides verified from the typeset PDFs, 2026-07-29** — this no longer
> rests on text extraction or an aggregator. Orson states the convention in
> words ("the AC Stark differential polarizabilty of the 5S state minus 6S
> state $\alpha_5-\alpha_6=\alpha_{56}$"), prints $\alpha_{56}=-1093$ a.u.,
> gives it again in SI as $-1.80\times10^{-38}$ J m² V⁻² (also negative), and
> draws a consequence: at his $w_0=63$ µm and $P=0.8$ W, $E^2=4.8\times10^{10}$
> V² m⁻² and $\Delta f=-0.66$ MHz — a **red** shift. Feeding his own numbers
> through this repo's unit chain returns $-0.653$ MHz, so the disagreement is
> not a units or convention artifact: the same arithmetic on his input
> reproduces his output.
>
> **Where this work's sign comes from, and why it is not a convention choice.**
> $\alpha_{5S}$ here is anchored to two measurements the model does not fit:
> the static value, $+318.28$ against the measured $318.79(1.42)$, and the
> tune-out at $790.0339$ nm against the measured $790.03235(3)$. A positive
> ground-state polarizability far below resonance is required physically, and
> the model reproduces it. Orson reports only the difference, which cannot be
> checked that way.
>
> **The disagreement is not symmetric, and a measured lifetime breaks it.**
> This is the answer to the fair question *how do you know the sign error is
> not yours*. $\alpha_{6S}(993)$ is a cancellation with only one side free.
> The upward 6S–6P group contributes $-949$ a.u. and **its sign is structural**:
> at 993 nm the drive sits above the 2732 nm resonance, so $\omega>\omega_0$
> makes every one of those denominators negative. Orson's $\alpha_{56}=-1093$
> requires $\alpha_{6S}=+1925$, so the downward 6S–5P cascade would have to
> supply $+2874$ instead of $+624$ — a factor $4.6$ in $\alpha$, hence
> $\times2.15$ in the dipole elements.
>
> Those same elements set the 6S lifetime. Unscaled they give **45.42 ns**
> against the **measured 45.57(17) ns** ([Gomez 2005](lit/gomez2005.md), itself
> 45.64(22) in a vapour cell and 45.48(25) in a MOT, averaged) — 0.3%, i.e.
> 0.9σ. ([Arora & Sahoo 2012](lit/arora2012.md)'s 45.44(8) is *calculated* from
> matrix elements 4.144/6.048, essentially the ones used here, so it checks the
> arithmetic rather than supplying a second measurement.) Scaled to reach
> Orson's sign they give **9.9 ns**, about **210σ** from the measurement. Held as a test
> (`test_orsons_sign_would_require_an_excluded_6S_lifetime`).
>
> **A candidate mechanism, offered as a hypothesis and not as a finding.**
> Orson writes that he calculated "in a manner similar to that of Martin *et
> al*". Martin's Eqs. (2) and (21) as printed carry a **leading minus**,
> $\alpha(\omega,J)=-\frac{2}{3(2J+1)}\sum\ldots$, which would make a ground
> state below resonance negatively polarizable. If that minus propagated, the
> published $-1093$ would be the negative of what the method gives, i.e.
> $+1093$ — agreeing with this work in sign and to 4.7% in magnitude. This is
> *not verified*: it would need Martin's tabulated $\alpha$ values checked
> against their own printed equation, and Orson's intermediate numbers, neither
> of which is available here. Recorded because it is testable, not because it
> is established. (Martin is independently inconsistent on sign: $+2.30(4)$ in
> the abstract and Table II against $-2.5(2)$ in Fig. 5's caption for the same
> coefficient.)
>
> the two differ by ~5% in magnitude with opposite sign. That pattern is
> itself diagnostic: a genuine matrix-element disagreement would have to move
> $\alpha_{6S}$ by $\sim$2200 a.u. and then land within 5% of the original
> magnitude by coincidence, whereas a global sign error — in either work —
> produces exactly magnitude agreement with sign opposition. (The same
> literature demonstrably carries printed-sign faults: Martin et al. 2019
> quote $+2.30$ in the abstract and $-2.5$ in Fig. 5 for the same
> coefficient; verified from the held PDF.)
>
> Every archival result uses $|\Delta\alpha|$ and is unaffected either way.
>
> **Where the sign actually comes from — and how much margin it has.** The two
> states are not alike here, and only one of them is robust.
>
> $\alpha_{5S}(993)=+834$ a.u. is **unanimous**: 993 nm is red of every strong
> 5S line, so every term is positive (D2 $+533$, D1 $+290$, rest $<+2$). No
> matrix-element revision can make it negative.
>
> $\alpha_{6S}(993)=-312$ a.u. is a **partial cancellation** — the weak point:
>
> | 6S transition | λ | direction | contribution (a.u.) |
> |---|---|---|---|
> | 6S–6P | 2732 nm | upward | **−566** |
> | 6S–5P | 1367 nm | downward | **+409** |
> | 6S–6P | 2791 nm | upward | **−280** |
> | 6S–5P | 1324 nm | downward | **+214** |
> | | | **net** | **−312** |
>
> Summed over *all* terms, not just the four largest: the upward group totals
> $-947$ and the downward 5P cascade $+623$, so the lines give $-324$ and the
> tail and core carry it to $-312$. The negative total survives by about 34% of
> the larger group. So the
> sign *is* sensitive to the relative strengths of those two groups: raising the
> 6S–5P (1367 nm) strength by **33%**, or lowering the 6S–6P (2732 nm) strength
> by 95%, drives $\alpha_{6S}$ through zero.
>
> That makes the disagreement with Orson a **specific, answerable question**
> rather than a bare contradiction: it lives in the balance between the
> 6S–6P (2.7 µm) and 6S–5P (1.3 µm) reduced matrix elements, not in the overall
> method. Both are stored (`alpha_5s_993`, `alpha_6s_993` in
> `results/polarizability.csv`) and the margins are regression-guarded
> (`test_the_993_sign_and_its_margin`). — and
since Orson's own AC-Stark measurement was a *null* at 6 MHz resolution, the sign
was never set by experiment, so this is a theory-vs-theory question that a
fixed-lock *pull* measurement (the sign of the shift-vs-power slope) would settle
outright. The narrative above keeps the established convention until it is resolved.

### 5.1 Electric quadrupole and magnetic dipole: why neither appears

A fair question about any polarizability calculation, and it splits in two.

**The driven transition is purely E1·E1, by parity.** $5S_{1/2}$ and $6S_{1/2}$
are both even, so a two-photon amplitude connecting them must be even overall.
E1·E1 is odd × odd = even and is the allowed channel. E1·M1 and E1·E2 are both
odd × even = odd, and so vanish identically for $S\to S$. There is no multipole
admixture to the transition amplitude to include or to bound — the selection
rule is exact, not an approximation.

**The polarizability does admit E2 and M1 terms, and they are far below
everything else here.** Their nominal scales relative to $\alpha_{E1}$ are

$$\frac{\alpha_{E2}}{\alpha_{E1}}\sim(ka_0)^2 = 1.1\times10^{-7},\qquad
\frac{\alpha_{M1}}{\alpha_{E1}}\sim\alpha_{\text{fs}}^2 = 5.3\times10^{-5}$$

at $k=2\pi/993.4$ nm. Against $\alpha_{6S}(993)=-312$ a.u. that is
$3.5\times10^{-5}$ and $1.7\times10^{-2}$ a.u. The comparison that matters is
with the questions actually open on this line: the sign dispute is a factor
$4.6$ in a group of terms, the magnitude spread between this work and Orson is
4.7%, and the $w_0$ prior is $\pm20$% and gates every absolute result.
Multipole corrections enter at $10^{-5}$% and $10^{-3}$%.

**Nor is any multipole channel resonantly enhanced out of that suppression.**
The nearest $S$–$D$ (E2) and $S$–$S$ (M1) channels from either state sit
thousands of cm⁻¹ from the 10066 cm⁻¹ drive: $5S$–$4D$ at 516.7 nm (detuned
9289 cm⁻¹), $5S$–$6S$ M1 at 496.7 nm (10066), $6S$–$5D$ at 1796 nm (4497),
$6S$–$4D$ at 12.9 µm (9289). A near-degeneracy could in principle lift a
suppressed channel into relevance; none is available.

## 6. Novelty position relative to prior art

Asymmetric lineshapes from *distributed* AC-Stark shifts are **not new**, and
five separate lines of prior art reach parts of what is done here. Naming them
first is cheaper than having a referee do it.

| prior work | what it already has | what it does not do |
|---|---|---|
| Wieman 1987; [Stalnaker 2006](lit/stalnaker2006.md) | a spatially varying shift producing an asymmetric line, with α extracted *from* the asymmetry | numerical Bloch treatment, fringe-*resolved*, one-photon (n=1), so no I² weighting |
| [Slepkov 2010](lit/slepkov2010.md) | the shift distribution of a guided mode kept and fitted, not averaged | saturated absorption in a hollow core, not two-photon; no closed form |
| [Wall 2014](lit/wall2014.md) | single-colour two-photon, so the I² weighting *is* present, over a measured 3D intensity map | purely numerical; inference runs the other way (α in, lineshape out); longitudinal not transverse; shift ≫ linewidth; a working frequency reference throughout |
| [Camparo 1992](lit/camparo1992.md) | a two-photon shift *distribution* giving an asymmetric line, with the first moment separated from the peak | the distribution is over a stochastic field in **time**, by Monte Carlo, and needs the strong-field adiabatic regime |
| [Fendel 2007](lit/fendel2007.md) | the peak-vs-average question tested and settled in a hot-alkali single-colour two-photon cell: −0.21 Hz/(mW/cm²) against *average* intensity | a deliberately **unfocused** 0.72 mm waist, chosen to make the distribution narrow enough that the average suffices |

[Hamilton 2023](lit/hamilton2023.md) builds the identical focus-averaged shift
integral on a retro-reflected Rb vapour line, then collapses it to a single mean.

Read together these bound the claim tightly: **the existence of the asymmetry is
not claimed here, nor is the I² weighting, nor keeping the distribution.** Fendel
in particular is the paper a referee is most likely to cite back, and it reads
*for* this work rather than against it — a first-rate group, facing a focused-beam
light-shift distribution, engineered it away rather than modelling it. What is
specific here:

1. the **closed-form** law $f(s)\propto|s|^{n-1}$ for the focused,
   retro-reflected, fringe-*averaged* **standing-wave** geometry — the triangle
   for $n=2$ — versus their fringe-*resolved* numerical Bloch treatment for
   $n=1$. The delineation is fringe-*averaged* vs fringe-*resolved*, **not**
   travelling vs standing (both are standing waves): their slow atomic beam
   resolves the $\lambda/2$ fringes, our fast thermal atoms average them (leaving
   only the small resolved tail of §5 / `fringe_tail`);
2. the **drift-immune moment method** (§3) — using a light shift as a
   reference-free measurement channel, which the precision community's
   suppress-the-shift approach never needed;
3. the **geometry-independence to the evanescent case**, the bridge to a
   nanofibre lineshape.

(The transit kernel itself, natural Lorentzian $\otimes$ two-sided exponential,
is the established [Biraben–Bassini–Cagnac](lit/biraben1979.md) result, *J. Phys. (Paris)* **40**, 445
(1979); we do not reinvent it. Full ledger: `docs/LITERATURE.md`.)

## 7. The open question (where a contribution fits)

The triangle assumed a beam of constant waist across the detection region. The
fluorescence lens actually collects from an axial window $|z|\le Z_c$ while the
beam diverges, $w^2(z)=w_0^2(1+\zeta^2)$, $\zeta=z/z_R$. Averaging the
transverse law over $z$ (the per-slice weight $\propto(1+\zeta^2)^{1-n}$ cancels
the local ramp normalisation up to one factor $1+\zeta^2$) gives the closed form

$$f(s) \propto |s|^{n-1}\left[\zeta_m + \frac{\zeta_m^3}{3}\right],\qquad
\zeta_m(s) = \min \left(\frac{Z_c}{z_R},\ \sqrt{\frac{S_0}{|s|}-1}\right)$$

which we evaluate numerically (`lineshape.stark_ramp_axial`). The standardised skewness **changes sign** with the collection
window — $g_1 \approx +0.56$ at $w_0=60\ \mu$m ($Z_c/z_R=0.18$) but $\approx -0.35$ at $w_0=16\ \mu$m ($Z_c/z_R=2.5$), crossing zero at $Z_c/z_R\approx1.12$
— because a long window piles weight at weak out-of-focus shifts. Where the
crossover falls is set by the collection geometry: $Z_c$ is the imaging field of
view $L_\parallel/2M$ of the side-viewing $f=18$ mm lens, with $L_\parallel$ the
cathode's active extent along the beam image. That extent is 12 mm — the R636-10
(housed in the Thorlabs PXT1/M module seen in the in-campaign photo) has a
3 × 12 mm cathode, whose rotation is a ×4 lever on $Z_c$, and it was mounted
landscape (experimenter-confirmed 2026-07-23). So $Z_c = 6/M$ mm, and the
two-waist flip holds for every $M$ from 0.5 to 6 rather than depending on which
layout the bench happens to realise; $u$ and $v$ remain unmeasured, so the
magnitude still carries an envelope (PLAN §8.3 #4). The pure triangle holds only at large waist, and the
small-waist configuration that maximises $S_0$ is exactly where the clean
triangular law is least valid.

**The questions.** (i) Is the axial-averaged form above correct and complete, or
does a proper treatment of the position- *and* velocity-dependent shift (the
thermal transit through a diverging Gaussian) modify it beyond this
quasi-static $z$-average? (ii) What is the right observable to quote when the
triangle fails — the sign-flip of $g_1$ between two waists is one candidate that
is immune to instrumental asymmetry (no instrumental asymmetry depends on $z_R$);
is there a cleaner invariant? (iii) Does the evanescent-geometry claim in §6
survive the same scrutiny? These are well-posed, they need no new data, and
they sit exactly at the focused-two-photon / inhomogeneous-field boundary.

*Backing material in the repo: README §2.6 (derivations), `docs/LITERATURE.md`
(prior-art ledger), `docs/PLAN.md` §8 (the proposed fixed-lock session, which would measure
$S_0$ and test the sign-flip). Absolute numbers are PRELIMINARY pending the fixed-lock session
beam-waist measurement, on which every magnitude rides.*
