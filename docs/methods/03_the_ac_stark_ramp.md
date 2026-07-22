*Chapter 3 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

### 2.6 AC-Stark shift — derivation of the triangular "ramp law"

Intense light shifts atomic levels (the AC-Stark or light shift) by an amount
proportional to the local intensity $I$. This chapter takes the shift toward the
**red** (lower frequency), following [Orson *et al.*](../lit/orson2021.md) 2021's
published $\Delta\alpha$ for this line; note that an independent recompute here
returns the same magnitude but the *opposite* sign, an open question flagged for
adjudication in [`THEORY_NOTE.md`](../THEORY_NOTE.md) §5. Nothing in the archival
results depends on the choice — the shape below and every bound drawn from it are
sign-immune ("The coefficient", below). Different atoms sit at different radii in the beam and so
feel different shifts — what does the *line* show? Two facts set it up:

- **Two-photon excitation rate** $\propto I^2$ (each photon contributes one
  power of $I$).
- **Shift** $s = -\kappa I$ for some constant $\kappa>0$ (red $\Rightarrow$
  minus, per the convention fixed above).

Take a Gaussian beam, $I(r)=I_0e^{-2r^2/w_0^2}$, and let $u\equiv I/I_0\in(0,1]$.
The signal contributed by the annulus between $r$ and $r+dr$ is

$$dS  \propto  I^2(2\pi rdr) \propto  u^2rdr$$

Change variables from $r$ to $u$. From $u=e^{-2r^2/w_0^2}$,

$$\frac{du}{u}=-\frac{4r}{w_0^2}dr  \Longrightarrow   rdr=-\frac{w_0^2}{4}\frac{du}{u}$$

so

$$dS \propto  u^2\cdot\frac{du}{u} = udu$$

The shift at intensity $u$ is $s=-\kappa I_0u \equiv -S_0u$, where
$S_0=\kappa I_0>0$ is the on-axis (maximum) shift magnitude. Substituting
$u=-s/S_0$, the **signal-weighted distribution of shifts** is

$$\boxed{f(s) \propto |s|\quad\text{on}\quad s\in[-S_0,0]}$$

— a triangular **ramp**. (Remarkably, the identical law holds for a nanofibre's
evanescent field, because the intensity is exponential in the flat coordinate
there too — that shared law is the physics bridge to Paper 2.) Normalizing,
$f(s)=2|s|/S_0^2$, we get the moments by direct integration:

$$\langle s\rangle=\int_{-S_0}^{0}  sf(s)ds=-\tfrac{2}{3}S_0,
\qquad
\mathrm{Var}(s)=\tfrac{1}{18}S_0^2,
\qquad
\kappa_3=\langle(s-\langle s\rangle)^3\rangle=+\tfrac{1}{135}S_0^3$$

So the **mean red pull is $\tfrac23 S_0$**, and the distribution is
positively skewed (peak pulled red, thin tail toward the blue). Here
$\kappa_2\equiv\mathrm{Var}$ and $\kappa_3$ are the second and third
*cumulants*; the ramp's own **standardized** skewness — the scale-free shape
number — is $\kappa_3/\kappa_2^{3/2}=18^{3/2}/135\approx0.566$, independent
of $S_0$ (a property of the triangle, not of the power). That fixed number is
the target of the form test (below); what varies with power is the
*observed line's* asymmetry, which we get by folding the ramp into the rest
of the line.

**Cumulants add under convolution** (the cumulant of a sum of independent
variables is the sum of the cumulants), and the symmetric kernels contribute
nothing asymmetric: the Lorentzian, Gaussian and transit kernels all have
$\kappa_1=\kappa_3=0$. So the ramp's odd cumulants pass through the
convolution untouched — the *whole line's* first-moment pull is
$-\tfrac23 S_0$ and its third cumulant is $\kappa_3^{\text{tot}}=S_0^3/135$,
**exactly**, independent of the (unknown) laser/transit widths. These two
odd cumulants are the clean, apparatus-independent handles, and the mean
pull is the primary fixed-lock-session observable ([§7 — Assumptions, and where this can go](08_assumptions_and_outlook.md)).

A literal *standardized* skewness of the full profile is more delicate,
because the homogeneous Lorentzian has divergent second and higher even
moments — $\kappa_2^{\text{tot}}$ is not finite, so one must work at fixed
fit window rather than with whole-line moments. Over the fit window the
symmetric part contributes an effective width $\sigma_\text{eff}$ (a standard
deviation, $\sim 2$MHz, set mostly by the $\sim 5$ MHz total FWHM and
nearly power-independent), against which the asymmetry reads as

$$g_1^{\text{obs}} \sim \frac{\kappa_3^{\text{tot}}}{\sigma_\text{eff}^3}
=\frac{S_0^3/135}{\sigma_\text{eff}^3} \propto S_0^3 \propto P^3$$

since $S_0\propto$ power $P$. (No contradiction with the fixed $0.566$: that
is the standardized skew of the ramp *alone*; here the same $\kappa_3$ is
divided by a much larger, nearly fixed symmetric width.) **Two consequences
for the archival data:** (i) the FWHM moves $\lesssim2$% across our power
sweep, so the old "power null" is a *prediction confirmed*, not a null
result; (ii) the observed asymmetry $\propto P^3$ is $\sim10^{-4}$ against a
$\sim10^{-3}$ noise floor — unmeasurable — so all AC-Stark *coefficients*
move to a fixed-lock session (where the shift itself, $\propto P$, is measured directly
against a stable lock). *Code:* `stark_ramp()` — built from exact per-cell
integrals so the area is exactly 1 and the mean exactly $-\tfrac23 S_0$ even
for shifts far below the grid step.

#### The general law: the signal exponent sets the ramp shape

Nothing in the change of variables above used $n=2$ except the weight
$u^n$. For a signal $\propto I^n$ the same steps give

$$dS  \propto  u^n\frac{du}{u}  =  u^{n-1}du
\qquad\Longrightarrow\qquad
f(s) \propto |s|^{n-1}\ \ \text{on}\ [-S_0,0]$$

For a **one-photon** transition ($n=1$ — e.g. the Stark-induced forbidden
lines of the parity-violation literature) the distribution is **uniform**:
mean $-S_0/2$ and, being symmetric about its mean, $\kappa_3=0$ — **zero
skew**. The skewness observable exists at all *only because the two-photon
signal goes as $I^2$*. This one line is the delineation from the nearest
prior art ([Stalnaker *et al.*](../lit/stalnaker2006.md), PRA **73**, 043416 (2006), who extracted an
AC-Stark parameter from asymmetric standing-wave lineshapes numerically, in
the $n=1$, fringe-resolved regime — full delineation in
`docs/LITERATURE.md`).

#### The parameter-free moment hierarchy (the form test)

Dividing out $S_0$, the ramp component predicts *pure numbers*:

$$\frac{\mathrm{Var}(s)}{\langle s\rangle^2}=\frac{1/18}{4/9}=\frac18,
\qquad
g_1\equiv\frac{\kappa_3}{\mathrm{Var}(s)^{3/2}}
=\frac{1/135}{(1/18)^{3/2}}=\frac{18^{3/2}}{135}\approx+0.566$$

A fixed-lock session tests them in order of statistical cost: (1) **mean pull vs
$P$** — the first cumulant, exact and apparatus-independent (§above), first
order in $S_0$, and the fixed lock makes centers usable; (2) **excess
variance vs $P^2$** — the symmetric second-moment growth
$\mathrm{Var}\propto S_0^2$ (exactly what the Cs 6S–8S literature reported as
a growing Gaussian width); (3) **skewness** — smallest signal, the only
moment that is
*zero unless* $n=2$. The pure numbers above are the ramp *alone*; in the
measured line each is diluted by the symmetric kernels (and read at fixed fit
window, per the divergence caveat above), so the hierarchy is fitted jointly,
not read off one trace.

#### Diverging-beam collection: the closed form and the sign flip

The triangle assumed a beam of constant waist across the detection region.
Really the fluorescence lens collects from an axial window $|z|\le Z_c$
around the focus while the beam diverges, $w^2(z)=w_0^2(1+\zeta^2)$ with
$\zeta=z/z_R$, $z_R=\pi w_0^2/\lambda$. At each $\zeta$ the transverse law
holds with a *local* maximum shift $S(\zeta)=S_0/(1+\zeta^2)$, and the per-slice
signal weight is $\propto w^2 I_0^{n}\propto(1+\zeta^2)^{1-n}$ — which
exactly cancels the local normalization $S(\zeta)^{-n}$ up to one factor
$(1+\zeta^2)$. The $z$-integral then closes for any $n$:

$$f(s) \propto |s|^{n-1}\left[\zeta_m+\frac{\zeta_m^3}{3}\right],
\qquad
\zeta_m(s)=\min \left(\frac{Z_c}{z_R},\ \sqrt{\frac{S_0}{|s|}-1}\right)$$

$Z_c/z_R\to0$ recovers the triangle; the hard edge at $-S_0$ softens to zero
(only the focal plane reaches the full shift). Numerically (uniform window,
$Z_c=2$ mm placeholder — OPEN until the fixed-lock session collection-profile
measurement):

| config | $Z_c/z_R$ | mean$/S_0$ | Var/mean$^2$ | $g_1$ |
|---|---|---|---|---|
| pure triangle | 0 | $-0.667$ | 0.125 | $+0.566$ |
| 60 µm (proposed config L) | 0.18 | $-0.660$ | 0.125 | $+0.564$ |
| 50 µm (2025 archival) | 0.25 | $-0.653$ | 0.125 | $+0.558$ |
| 16 µm (proposed config S) | 2.47 | $-0.431$ | 0.333 | $-0.354$ |

**The skewness flips sign** (crossover at $Z_c/z_R\approx1.12$): a long
window piles signal into weak out-of-focus shifts, leaving a tail toward
$-S_0$. **The flip at config S is conditional on the collection geometry,
which is unmeasured.** $Z_c$ is not a free parameter: for the side-viewing
$f=18$ mm lens imaging the beam onto the PMT it is the axial field of view
in object space, $Z_c=r_\text{PMT}/M$ with magnification $M=v/u$
($u$ = lens–beam and $v$ = lens–PMT distances, $1/u+1/v=1/f$), so the flip
condition at 16 µm reads $r_\text{PMT}/M > 1.12 z_R \approx 0.9$ mm — and
plausible bench layouts land on *both* sides (a short-conjugate,
high-magnification layout gives $g_1\approx+0.5$, no flip; a 1:1 relay or a
large photocathode gives $g_1\approx-0.3$ to $-0.5$). Three ruler-and-datasheet
numbers ($u$, $v$, the PMT active diameter) settle it, which is why they are
part of the proposed session's setup metrology (PLAN §8.1, §8.3 #4); the
solid-angle weighting varies by <2% across any such window, so the top-hat
form is fair and the *width* is the only unknown. Geometry permitting, a
proposed session's skew program is then a **sign-flip test between beam
configurations** — $g_1>0$ at the large waist, $g_1<0$ at the small one —
a signature no instrumental asymmetry can mimic, because the instrument
knows nothing about $z_R$. At the re-centred 50 µm archival waist the
coefficients above carry only a few-% geometry caveat (its longer $z_R$ makes
the ramp nearly the pure-triangle $Z_c\to0$ limit, $g_1\approx+0.56$; it was
10–40% at the old 32 µm nominal). *Code:*
`stark_ramp_axial()`, table from `scripts/run_ramp_geometry.py`.

#### Standing-wave fringes: why the shift follows the envelope

The retro-reflected beam makes $\lambda/2$ intensity fringes — does an atom
feel the fringe *peak* intensity (a coherent $\times2$) or the average? The
frequency-modulation criterion ([Stalnaker *et al.*](../lit/stalnaker2006.md), Sec. IV): as an atom
crosses fringes its AC-Stark shift is modulated with peak deviation
$\xi=S_0\lesssim1$ MHz at modulation frequency
$f_\text{mod}=2v/\lambda\approx0.56$ GHz (axial thermal speed $\sim280$ m/s,
fringe spacing $\lambda/2$). The FM modulation index is
$\xi/f_\text{mod}\sim2\times10^{-3}$:
deep in the narrow-band regime, so the shift response is a pure carrier and
the sidebands are negligible — the atom responds to the **time-averaged**
intensity. The shift is thus $\propto(1+\rho)I_{\text{fwd}}$ with $\rho$ the
retro power ratio, with **no coherent fringe enhancement**. (Atoms with axial
speed $\lesssim5$ m/s — 1–2% of the signal — are fringe-resolved; a
percent-level correction.) The remaining OPEN quantity in $S_0$ is the
measured $\rho$ per beam configuration (in situ at the cell, in a fixed-lock session).

**Why $\rho\approx1$ is a design property here.** The 2025 retro is a
self-imaging (lens-based) one: the beam is focused into the cell by L1
($f=150$ mm), and a second lens L2 ($f=150$ mm) after the cell maps the cell
waist onto an intermediate waist behind it — by the Gaussian $f$–$f$ property a
waist at a lens's front focal plane becomes a waist at its back focal plane,
here $w_0'=\lambda f/(\pi w_0)\approx0.95$ mm for $w_0=50\ \mu$m. A **flat**
mirror placed at that flat wavefront *time-reverses* the beam, so it retraces
back through L2 and re-forms the original 50 µm cell waist. The forward and
return modes therefore match **by construction**, and $\rho$ falls below 1 only
through losses (two further L2 passes, two further window passes, mirror
reflectivity), not through mode mismatch. The arrangement is also forgiving:
that intermediate beam has $z_R'\approx2.8$ m, so the "mirror at the waist"
condition holds to within tens of centimetres, and residual sensitivity is
dominated by mirror *tilt*, not longitudinal placement. (The 2019 reference
measurement on this line achieves the same self-imaging with a concave mirror
at $2f$ instead of a lens plus flat mirror — a different implementation of the
identical idea; `LITERATURE.md` [§6 — Assumptions, and where this can go](08_assumptions_and_outlook.md)a.) Note the design must be *re-established
per waist* in a fixed-lock session: L2 has to sit a focal length from the new waist, and the
intermediate beam grows to $\approx3$ mm at $w_0=16\ \mu$m, so return-path
clipping is the thing to watch (PLAN §8.1).

How much would a departure from $\rho=1$ actually cost? Less than one might
fear, and the archive's own signal quality provides indirect evidence. Since $S_0\propto(1+\rho)$, *any*
$\rho\in[0,1]$ moves the prediction only between 0.29 and 0.59 MHz — a factor
of two end-to-end, and the archival bound ($S_0(225\ \text{mW})<0.63$ MHz, [§5 — What we found (2025 archive)](07_what_we_found.md))
brackets the whole range, so no archival conclusion turns on it. Better, the
Doppler-free *rate* scales as $\rho$ itself (it needs one photon from each
direction, so the signal $\propto I_\text{fwd}I_\text{bwd}$), not as $1+\rho$:
a badly mismatched retro would have destroyed the signal long before it
appreciably moved the shift, so the archive's strong, clean lines are
evidence that $\rho$ is not small. The asymmetry is worth
remembering — the retro is a *signal* risk far more than a *coefficient* risk.
It matters for a fixed-lock session precisely because the coefficient is then the point:
$\rho$ is measured in situ, per configuration (return-path clipping differs
with waist), before any $\Delta\alpha$ in physical units is quoted.

#### The coefficient (field-intensity convention, pinned)

The ramp *shape* and its centred moments are convention-free, but the
*magnitude* of $S_0$ — which converts a measured centroid pull into the
differential polarizability $\Delta\alpha=\alpha_{6S}-\alpha_{5S}$ — needs the
$\langle E^2\rangle$ convention fixed. We adopt the standard AMO one ([Grimm
*et al.*](../lit/grimm2000.md) 2000; [Steck](../lit/steck_rb.md)): for $E(t)=E_0\cos\omega t$, $\langle E^2\rangle=E_0^2/2$,
so $\Delta E_i=-\tfrac14\alpha_i E_0^2=-\alpha_i I/(2\varepsilon_0 c)$ and

$$S_0=\frac{\Delta\alpha\ I_\text{eff}}{2\varepsilon_0 c h},\qquad
I_\text{eff}=(1+\rho)\frac{2P}{\pi w_0^2}$$

With $\Delta\alpha=1093$ a.u. ([Orson *et al.*](../lit/orson2021.md) 2021) this is $S_0=0.59$ MHz (transition) at 225 mW,
$w_0=50\ \mu$m (the archival prior; it was 1.43 at the old 32 µm nominal),
$\rho=1$, growing to 5.7 MHz at $w_0=16\ \mu$m (why the fixed-lock session's
small waist makes the $\propto S_0^3$ skew measurable). The **sign** is
convention-independent — set by $\text{sign}(\Delta\alpha)$, red for Orson's
published $\Delta\alpha>0$. That sign is itself under adjudication: an
independent sum-over-states recompute here agrees on magnitude (within 5%) but
returns $\Delta\alpha<0$, i.e. a **blue** shift ([`THEORY_NOTE.md`](../THEORY_NOTE.md)
§5). Every archival result quoted in this repository is unaffected — the
asymmetry null is symmetric, and the $S_0$ bound and its prediction band use
$|\Delta\alpha|$. *Code:* `lineshape.stark_shift_S0_mhz()`. The full
theorist-facing derivation, novelty position, and the open diverging-beam
question are in [`docs/THEORY_NOTE.md`](../THEORY_NOTE.md).

---

[← The lineshape, kernel by kernel](02_the_lineshape.md) · [The composite model (and what does not enter it) →](04_the_composite_model.md)
