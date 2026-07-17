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

For $n=2$ this is the **triangular ramp** $f(s)=2|s|/S_0^2$. The same $dS\propto
dI/I \cdot I^{n}$ argument holds for any monotonic $I$ profile that is flat in
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

## 3. The drift-immune method

The 2025 archival lock drifted at $\sim$MHz/min, so absolute line **centres**
are dead — and a fit must give each scan its own free centre to absorb that
drift. This has a sharp consequence for the ramp. Its **first-order effect is a
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
signature) — but note the pull is available only once a stable lock (a fixed-lock session)
un-absorbs it.

Two caveats. *Between*-scan drift is absorbed exactly by the free centres.
*Within*-scan drift is not a pure translation — it smears the line
asymmetrically in a scan-direction-dependent way that couples the fitted centre
to the fitted asymmetry; at the established $\lesssim0.1$ MHz within-scan drift
this is small, but because the asymmetry is itself small it must be *estimated*,
not assumed zero.

**Status.** In the 2025 sweep the fitted asymmetry coefficient is **consistent
with zero**: at $\le225$ mW its significance (the skew grows only as $S_0^3$)
sits below the SNR $\approx130$ floor, so the estimator — correct as it is —
returns an **upper bound, not a detection**. A fit always returns *some* value
with an error bar; the discipline is to report a bound unless it clears that
bar, which at archival intensity it does not. A fixed-lock session changes this two ways:
the fixed lock **recovers the first-order pull** ($-\tfrac23 S_0 \propto P$, a
$\sim$MHz shift against a stable reference — the primary $S_0$ measurement, no
longer absorbed by a free centre); and the small waist, where $S_0$ is $4\times$
larger and its skew signature up to $64\times$ larger, lifts the shape asymmetry
into a **detection**. Both are *conditional on the small-waist skew corrections
— the beam-divergence collection average of §7 (the larger, sign-flipping one)
and the standing-wave fringe-resolved tail of §5, same-sign and fit jointly* —
which move the ramp form — and the pull coefficient off $-\tfrac23$ — at small
waist, and must be applied before $S_0$, hence $\Delta\alpha$, is read.

**The hybrid, made principled.** The three cumulants are not three rival
measurements to be combined or cherry-picked — they are three analytic
functionals of the *one* parameter $S_0(P)$ (`lineshape.ramp_moment_contributions`):
pull $\propto S_0$, excess variance $\propto S_0^2$, third cumulant $\propto
S_0^3$. the fixed-lock fit uses a single $S_0$ per condition and checks that the pull,
excess-variance and third-cumulant *measured from the data* are mutually
consistent with it — a $\chi^2$ across the moment hierarchy. The primary
observable at each intensity is pre-registered as the lowest-order moment above
its own noise floor (pull where $S_0$ is small, the skew only where $P^3$ has
climbed clear of noise); the others are consistency checks with their own error
bars. This is what makes the fragile small-waist skew defensible: a spurious
asymmetry from a fit artifact or the diverging-beam geometry will not *also*
reproduce the correct, more-robust lower-order pull and variance for the same
$S_0$, so the claim is never "we measured the skew" but "pull, variance and
skew are jointly consistent with one triangular ramp of amplitude $S_0(P)$."
(The extraction stays single: one fitted profile per condition, three
functionals of it — never several estimators of one moment.)

## 4. Prediction confirmed in the archive

At fixed density the archive already confirms the *convention-free* content:
across a $9\times$ power sweep the linewidth is flat to $\lesssim2$% (the ramp
adds variance $\propto S_0^2$, negligible against the $\sim$5 MHz budget), and
the amplitude scales as $P^{2}$ (log-log slopes 1.83–2.12). The asymmetry is
predicted below the archival noise and is not detected — as designed.

That flatness is not merely a null. Fitting one shared $S_0=\kappa P$ to the
four peaks' width-vs-power (`stark.fit_stark_sweep`, M4e) turns it into a
quantitative **upper bound $S_0$(225 mW) $<0.63$ MHz (95%, profile
likelihood)**; the fitted value is consistent with zero, so the archive *brackets* the predicted
$0.59$ MHz (§5) without resolving it. It is a bound, not a measurement, for the
same two-epoch reason as everything else here: the 2025 drifted lock kills the
line centres, so the pull $\propto S_0$ — the sensitive handle — is absorbed by
each trace's free centre, leaving only the ramp's $\propto S_0^2$ width
broadening (a $0.6$ MHz $S_0$ inflates a $5$ MHz line by $<0.1$ MHz). Through the
§5 convention, at the nominal $w_0=50\ \mu$m this brackets $\Delta\alpha$ below
$\sim1.1\times$ the computed value ($<\sim1200$ a.u., 95%, profile likelihood;
the earlier $\sim5800$ came from a Wald interval evaluated at the $\kappa=0$
rail, where it has no valid coverage) — consistent with
$1093$, with the mapping inheriting the open $w_0$. So the archive **does not
contradict** the computed $\Delta\alpha$; the fixed lock measures the pull
$\propto S_0$ directly (small waist $\Rightarrow S_0$ $\sim4\times$ larger),
turning this bracket into the coefficient.

## 5. The coefficient (the field-intensity convention, pinned)

The shape and centred moments above are convention-free. The **magnitude** of
$S_0$ — needed to turn a measured pull into a differential polarizability
$\Delta\alpha = \alpha_{6S}-\alpha_{5S}$, or to predict $S_0$ from a computed
$\Delta\alpha$ — requires fixing the $\langle E^2\rangle$ convention. We adopt
the standard AMO one (Grimm, Weidemüller & Ovchinnikov, *Adv. At. Mol. Opt.
Phys.* **42**, 95 (2000); Steck): for a real field $E(t)=E_0\cos(\omega t)$ the
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
$\sim2\times10^{-3}$ — in Stalnaker's FM framework (*Phys. Rev. A* **73**,
043416 (2006), Sec. IV), the small-modulation-index limit puts the carrier at
the fringe-*mean* intensity, so $I_{\text{eff}}$ **is** that standing-wave mean
and the pull is exactly fringe-immune. But the line is Doppler-free over **all** $v_z$, so
near-transverse atoms sit at a frozen fringe and sample the node-antinode
arcsine: a fringe-*resolved* tail (weight $f_\text{res}$) that keeps the mean
but, because the fringe *multiplies* the shift $s\to s(1+x)$ with $x$ arcsine,
**suppresses** the ramp skew — $\kappa_3\to S_0^3(1/135-f_\text{res}/10)$ at
$\rho=1$ (a $-13.5 f_\text{res}$ fractional leverage $\propto$ contrast$^2$; only
$P=f_\text{res}\sigma_x^2$ is observable). Negligible at $w_0=50\ \mu$m
($\sim$5–8% of an already-below-noise skew), $\sim$25% at $16\ \mu$m, and
**same-sign-additive** to the larger §7 divergence correction — the two must be
fit jointly at small waist (quantified, coherence-window-bracketed, in
`fringe_tail`). With $\Delta\alpha = 1093$ a.u.
(Orson *et al.* 2021, sourced below) this gives $S_0 = 0.59$ MHz (transition) at $P=225$ mW, $w_0=50\ \mu$m,
$\rho=1$; it grows to $5.7$ MHz at $w_0=16\ \mu$m, which is why the fixed-lock session's small
waist makes the $\propto S_0^3$ skew measurable. Code: `lineshape.stark_shift_S0_mhz`.

**Sign, and provenance.** The $\langle E^2\rangle$ convention is magnitude-only;
the *direction* of the pull is set by $\mathrm{sign}(\Delta\alpha)$. **$\Delta\alpha$
is Orson *et al.* 2021's published value** (*J. Phys. B* **54**, 175001 — prior art
on this exact 5S–6S line): they compute $\alpha_{56}=\alpha_{5S}-\alpha_{6S}=-1093$
a.u. "in a manner similar to Martin 2019," so our $\Delta\alpha=\alpha_{6S}-\alpha_{5S}
=+1093>0$ (6S pulled down more than 5S $\Rightarrow$ red shift $\Rightarrow$ $S_0>0$).
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
check is one line for a theorist: the sign of $\alpha_{6S}$ at 993 nm) — and
since Orson's own AC-Stark measurement was a *null* at 6 MHz resolution, the sign
was never set by experiment, so this is a theory-vs-theory question that a
fixed-lock *pull* measurement (the sign of the shift-vs-power slope) would settle
outright. The narrative above keeps the established convention until it is resolved.

## 6. Honest novelty position

Asymmetric two-photon-like lineshapes from *spatially distributed* AC-Stark
shifts are **not new**: the cesium parity-violation lineage
(Wieman *et al.*, *Phys. Rev. Lett.* **58**, 1738 (1987); Stalnaker *et al.*
2006) modelled them numerically in a standing wave and even extracted an
AC-Stark parameter from the asymmetry; and the nearest *construction* is
Hamilton *et al.* (*Phys. Rev. Applied* **19**, 054059 (2023)), a
retro-reflected Rb vapour two-photon line whose focus-averaged shift integral is
identical to ours — but collapsed to a single mean shift, never the distribution
(LITERATURE.md §1). We do **not** claim the existence of the asymmetry. What we believe is specific and defensible:

1. the **closed-form** law $f(s)\propto|s|^{n-1}$ for the focused,
   retro-reflected, fringe-*averaged* **standing-wave** geometry — the triangle
   for $n=2$ — versus their fringe-*resolved* numerical Bloch treatment for
   $n=1$. The honest delineation is fringe-*averaged* vs fringe-*resolved*, **not**
   travelling vs standing (both are standing waves): their slow atomic beam
   resolves the $\lambda/2$ fringes, our fast thermal atoms average them (leaving
   only the small resolved tail of §5 / `fringe_tail`);
2. the **drift-immune moment method** (§3) — using a light shift as a
   reference-free measurement channel, which the precision community's
   suppress-the-shift approach never needed;
3. the **geometry-independence to the evanescent case**, the bridge to a
   nanofibre lineshape.

(The transit kernel itself, natural Lorentzian $\otimes$ two-sided exponential,
is the established Biraben–Bassini–Cagnac result, *J. Phys. (Paris)* **40**, 445
(1979); we do not reinvent it. Full ledger: `docs/LITERATURE.md`.)

## 7. The open question (where a contribution fits)

The triangle assumed a beam of constant waist across the detection region. The
fluorescence lens actually collects from an axial window $|z|\le Z_c$ while the
beam diverges, $w^2(z)=w_0^2(1+\zeta^2)$, $\zeta=z/z_R$. Averaging the
transverse law over $z$ (the per-slice weight $\propto(1+\zeta^2)^{1-n}$ cancels
the local ramp normalisation up to one factor $1+\zeta^2$) gives the closed form

$$f(s) \propto |s|^{n-1}\left[\zeta_m + \frac{\zeta_m^3}{3}\right],\qquad
\zeta_m(s) = \min \left(\frac{Z_c}{z_R},\ \sqrt{\frac{S_0}{|s|}-1}\right)$$

which we evaluate numerically (`lineshape.stark_ramp_axial`). It has a striking
consequence: the standardised skewness **changes sign** with the collection
window — $g_1 \approx +0.57$ at $w_0=60\ \mu$m ($z_R \gg Z_c$) but $\approx
-0.35$ at $w_0=16\ \mu$m ($z_R \ll Z_c$), crossing zero near $Z_c/z_R\approx1.2$
— because a long window piles weight at weak out-of-focus shifts. So the pure
triangle holds only at large waist, and the small-waist configuration that
maximises $S_0$ is exactly where the clean triangular law is least valid.

**The questions.** (i) Is the axial-averaged form above correct and complete, or
does a proper treatment of the position- *and* velocity-dependent shift (the
thermal transit through a diverging Gaussian) modify it beyond this
quasi-static $z$-average? (ii) What is the right observable to quote when the
triangle fails — the sign-flip of $g_1$ between two waists is one candidate that
is immune to instrumental asymmetry (the instrument knows nothing about $z_R$);
is there a cleaner invariant? (iii) Does the evanescent-geometry claim in §6
survive the same scrutiny? These are well-posed, they need no new data, and
they sit exactly at the focused-two-photon / inhomogeneous-field boundary.

*Backing material in the repo: README §2.6 (derivations), `docs/LITERATURE.md`
(prior-art ledger), `docs/PLAN.md` §8 (the fixed-lock session that measures $S_0$
and tests the sign-flip). Absolute numbers are PRELIMINARY pending the fixed-lock session
beam-waist measurement, on which every magnitude rides.*
