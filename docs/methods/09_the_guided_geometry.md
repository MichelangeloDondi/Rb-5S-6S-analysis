*Chapter 9 of the [methods](../methods.md)*

## 9. The guided geometry: the same model in an evanescent field

**The question.** What does each term of the cell's lineshape become for an
atom in the evanescent field of an optical nanofibre, and which of them changes
form and not merely size?
**Takes.** The lineshape and AC-Stark chapters, whose four terms it carries
across, and a solved HE11 mode from `rb5s6s.fibre`.
**Gives.** The guided transit kernel and its second-order entry into the width,
the light shift referred to the field an atom actually sees, and the
atom-surface term the cell has no analogue for.
**Skip if.** You have no interest in guided geometries. Nothing in the
vapour-cell result depends on this chapter, and the fibre thread is declared in
[BIG_PICTURE](../BIG_PICTURE.md) so it can be skipped whole.

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> explains the measurement in six sentences, then defines every term
> and symbol used anywhere in this repository.

Chapters 2 to 4 derive the lineshape for atoms crossing a focused Gaussian
beam in a vapour cell. This chapter derives the same four terms for atoms in
the evanescent field of an optical nanofibre, states which of them change
functional form and not only magnitude, and gives the numbers for the fibre
diameters this programme would use.

Everything is on the transition axis, the two-photon sum frequency, which is
twice the laser axis.

### 9.1 The guided mode

A silica nanofibre of radius $a$ in vacuum guides the fundamental $\mathrm{HE}_{11}$
mode. Writing $k_0 = 2\pi/\lambda$, $\beta = n_{\mathrm{eff}}k_0$ for the
propagation constant, and

$$U = a\sqrt{n_1^2k_0^2-\beta^2}, \qquad W = a\sqrt{\beta^2-n_2^2k_0^2}, \qquad V^2 = U^2+W^2$$

with $n_1$ the silica index and $n_2 = 1$, the effective index solves

$$\left[\frac{J_1'(U)}{UJ_1(U)}+\frac{K_1'(W)}{WK_1(W)}\right]\left[n_1^2\frac{J_1'(U)}{UJ_1(U)}+n_2^2\frac{K_1'(W)}{WK_1(W)}\right] = n_{\mathrm{eff}}^2\left(\frac{1}{U^2}+\frac{1}{W^2}\right)^2$$

The mode is single if $V\lt2.405$. Outside the glass the field falls as
$K_1(qr)$ with

$$q = \sqrt{\beta^2-k_0^2} = k_0\sqrt{n_{\mathrm{eff}}^2-1}$$

**Two decay lengths follow and they differ by a factor of two.** The field
amplitude falls with $1/q$ and the intensity, which goes as the square, falls
with $\Lambda = 1/(2q)$. Conflating them is a factor of two in every
intensity, shift and rate below.

Solved at the probe wavelength 993.4181 nm (`rb5s6s.fibre.solve_he11`,
validated against two effective-index values standard for this geometry, which no note in this record cites to a paper, and against an independently written solver):

| $2a$ | $V$ | $n_{\mathrm{eff}}$ | $1/q$ | $\Lambda$ | $qa$ |
|---|---|---|---|---|---|
| 350 nm | 1.163 | 1.01283 | 984 nm | 492 nm | 0.178 |
| 370 nm | 1.229 | 1.01927 | 802 nm | 401 nm | 0.231 |
| 400 nm | 1.329 | 1.03164 | 624 nm | 312 nm | 0.321 |

**The exponential approximation is not available here.** $K_1(x)$ reduces to
$\sqrt{\pi/2x}e^{-x}$ only for $x\gg1$, and $qa$ is 0.18 to 0.32, so the
asymptotic form is unavailable anywhere the atoms sit.

**The profile below is the axial Poynting flux of the solved vector field**,
not a single Bessel term. The distinction is worth stating because
$[K_1(qr)/K_1(qa)]^2$ describes $E_z$ alone, about a tenth of the field: on the
370 nm fibre it gives 0.058 at 400 nm from the surface where the full flux
gives [0.156](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_400nm:flux_fraction"), a factor of 2.7. **The two fibres in this chapter carry
different numbers and they must not be mixed**: on the 400 nm fibre the same
quantity is [0.119](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_400nm_at_400nm:flux_fraction").
Both fibres are tabulated in that one file so no surface has to choose. The fields are validated by $E_z$ and $H_\phi$ continuity at the
boundary before any of these numbers is read off them.

| distance from surface | $I/I_{\mathrm{surf}}$, 370 nm fibre | the exponential, for comparison |
|---|---|---|
| 100 nm | [0.580](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_100nm:flux_fraction") | [0.779](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_100nm:flux_fraction_exponential") |
| 200 nm | [0.360](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_200nm:flux_fraction") | [0.607](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_200nm:flux_fraction_exponential") |
| 400 nm | [0.156](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_400nm:flux_fraction") | [0.369](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_400nm:flux_fraction_exponential") |
| 600 nm | [0.074](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_600nm:flux_fraction") | [0.224](../../results/guided_mode_tables.csv "ref:guided_mode_tables:evanescent_profile_370nm_at_600nm:flux_fraction_exponential") |

So the exponential overstates the delivered intensity by about **2.4** at a
400 nm trap distance, and by a factor that grows with distance. Reproduce the
column with `HE11Field(370.0, 993.4181).intensity_at(d)`.

### 9.2 Transit broadening changes functional form, not just magnitude

In the cell an atom crosses a Gaussian beam and the two-photon transit
profile is a two-sided exponential **in frequency**, $\exp(-|\nu|/b)$, whose
central cusp is its signature (Biraben, Bassini and Cagnac 1979). It is
distinguishable by shape from every Lorentzian in the budget.

In the evanescent field the exponential sits in the conjugate variable. An
atom moving radially at speed $v$ sees an intensity envelope

$$I(t) = I_0\exp(-v|t|/\Lambda)$$

and for a two-photon transition the coupling is proportional to $I$, so the
interaction amplitude is that same two-sided exponential in **time**, with
$\tau = \Lambda/v$.

**This exponential is a stated envelope choice, and the section above is why
it has to be stated.** The solved field's decay is not exponential at these radii,
and its local decay length where the atoms sit runs well below the nominal
$\Lambda$ this section carries, so every added width below understates by
roughly the square of that ratio, about a factor two on the second-moment
matched length. The direction is conservative for the temperature-ladder
lever, the size is in [the campaign chapter's open item](../big_picture/06_next-nanofibre.md),
and carrying the solved profile through this kernel is the named open
derivation.

**The lineshape is the squared magnitude of its transform, not the transform.**
Chapter 2 states that rule. The transform is

$$\mathcal{F}\left[e^{-|t|/\tau}\right] = \frac{2\tau}{1+(2\pi\nu\tau)^2}$$

and the profile is its square, a **squared Lorentzian**. Setting
$(1+x^2)^2 = 2$ gives $x = \sqrt{\sqrt2-1} = 0.6436$, so the squared form is
narrower than the Lorentzian built from it by exactly that factor.

**That 0.6436 is the two-sidedness of the envelope and not the squaring, and
saying otherwise would hide a trajectory assumption.** For a **one-sided**
coupling $\Omega(t) = I_0e^{-vt/\Lambda}\theta(t)$ the transform is
$\tau/(1+2\pi i\nu\tau)$, so $|\mathcal{F}|^2 = \tau^2/(1+(2\pi\nu\tau)^2)$
is a **true Lorentzian of FWHM exactly $\bar v/(\pi\Lambda)$** with the
squaring rule fully applied.

**So the factor is a statement about the trajectory, and the trajectory is a
free atom's.** A two-sided envelope is what an atom sees if it approaches and
recedes: a free atom on a single passage past the fibre, or one reflected by
the repulsive component of a two-colour potential. **An atom that arrives and
stops, adsorbed at the glass, or that starts there and leaves, sees a one-sided
envelope**, and read like for like against the same velocity average that gives
each factor below, sidedness is worth 1.554 at a single velocity and about 1.57
across the ensembles. The weighting choice is worth 1.811. Both are comparable
levers and both are inputs, not results.

**A trapped atom is not this calculation at all**, and saying it was would
double-count one motion into two budget terms. An atom held in the two-colour
potential never has its coupling extinguished: it stays in the field for the
trap lifetime, milliseconds and longer, so its transit contribution is
sub-kilohertz. Its radial motion modulates the intensity it sees instead of
switching it off, which is a modulation and a light-shift spread, and section
9.3 already carries that as the trap's own radial term.

**A third input sits upstream of both.** Writing the envelope as
$e^{-v|t|/\Lambda}$ assumes $d(t) = d_0 + v|t|$, which is a strictly radial
approach. A pass at impact parameter $b$ gives
$d(t) = \sqrt{b^2 + (vt)^2} - a$, exponential in $|t|$ only asymptotically.

**The ensemble average narrows it again, and how much depends on the weight.**
The speed-weighted ensemble narrows by more than the squaring did, $\times0.38$
against $\times0.64$. The flux-weighted default narrows by less, $\times0.68$.
Slow atoms interact longer and their $|a|^2$ carries $\tau^2$, which pulls the
average toward the narrowest contributions, and a flux weight partly cancels
that by favouring fast atoms. At 150 microkelvin in a 401 nm mode:

| treatment | FWHM | against the retired form |
|---|---|---|
| $\bar v/(\pi\Lambda)$, the retired form | [151.8](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_amplitude_lorentzian:fwhm") kHz | [1.0](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_amplitude_lorentzian:factor") |
| squared Lorentzian at $\bar v$ | [97.7](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_single_velocity:fwhm") kHz | [0.6436](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_single_velocity:factor") |
| Maxwell ensemble, flux weighted | [66.6](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_ensemble_flux:fwhm") kHz | [0.4387](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_ensemble_flux:factor") |
| Maxwell ensemble, speed weighted | [36.8](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_ensemble_speed:fwhm") kHz | [0.2422](../../results/guided_mode_tables.csv "ref:guided_mode_tables:transit_kernel_ensemble_speed:factor") |

**The weighting is a model choice and this record does not settle it**, because
which weight applies depends on how atoms arrive at the surface, which is a
property of the trap and not of the line. It is therefore **spanned**:
`TRANSIT_KERNEL_FACTOR` names all four, `transit_fwhm` takes the branch as an
argument, and every branch is exercised by a test. The default is the
flux-weighted ensemble and it is not 1.

So the guided transit width is

$$\Gamma_{\mathrm{transit}} = f\frac{\bar v}{\pi\Lambda}, \qquad
\bar v = \sqrt{\frac{8k_BT}{\pi m}}, \qquad f = 0.24\ \text{to}\ 0.44$$

**This is the central structural difference between the two platforms, and it
is not the one an earlier version of this chapter stated.** The guided kernel
does **not** add linearly to the Lorentzian terms. Its time-domain function is
the autocorrelation
$(1+|t|/\tau)e^{-|t|/\tau} = 1 - t^2/2\tau^2 + |t|^3/3\tau^3 - \dots$,
and **the linear term cancels**. Being linear at the
origin is exactly the property that makes Lorentzian widths add, so this kernel
enters at *second* order instead, the way a Gaussian does.

The size of that is worth stating, because it is not a refinement. Convolved
with the natural width alone, a kernel of nominal FWHM $\Gamma_\mathrm{transit}$
adds only

$$0.083 \text{ to } 0.171 \text{ of } \Gamma_\mathrm{transit}$$

across the three kernel branches at 170 µK in a 401 nm mode, **each branch
against its own kernel width**, against 1.0 for a term that added exactly. The
kHz band quoted later in this chapter divides by a single 71 kHz kernel
instead, so the two do not divide into each other and neither is wrong. **The band is the `added_fraction_170uK_band` row of
`results/transit_additivity.csv` and it is quoted with the core it was
computed against**, a 3.8905 MHz Lorentzian FWHM and a Gaussian of 0.30 MHz
standard deviation, which is 0.7064 MHz FWHM. **The two widths are of
different kinds and the sentence has to say which is which**: reading the
Gaussian as an FWHM reproduces the band about six per cent wide, and the
committed table is reproduced only by the standard-deviation reading. That
pairing is not decoration: the fraction is a property of the kernel together
with the line it is added to, and a band stated without its core is uninterpretable.
Its correction history is in
[the guided-geometry record](../history/09_the-guided-geometry.md).
**The fraction is not a constant**: being second
order it is set by the ratio of the two widths, so it grows with
$\Gamma_\mathrm{transit}$ and falls against a broader Lorentzian core.

**The consequence for a temperature ladder is the sharper statement.** Since
$\Gamma_\mathrm{transit}\propto\sqrt T$ and the contribution is second order,
the width a ladder actually sees goes as $T^{p}$ with $p$ in
[0.973 to 0.980](../../results/transit_additivity.csv "ref:transit_additivity:spanned:temperature_exponent_band")
over 10 to 170 µK, not as $\sqrt T$. **The committed row is a band across the
three velocity weightings and this sentence quoted a single 0.98**, which is
prose narrowing a band to a point, the reverse of the usual defect and the
same class. A design that fits a $\sqrt T$ column is fitting the wrong basis
function, and the amplitude it recovers is not the transit width. **So the guided transit term is far smaller in the
line than its own width suggests**, and any lever that reads it through the
total width is correspondingly weaker. The $\nu^{-4}$ wing against a
Lorentzian's $\nu^{-2}$ is a real shape difference, but it is not what governs
the addition and this record does not claim it is measurable at the achieved
signal-to-noise.

Evaluated at $\Lambda = 401$ nm, the 370 nm fibre:

| $T$ | $\bar v$ | $\Gamma_{\mathrm{transit}}$ |
|---|---|---|
| 170 µK | 0.204 m/s | 71 kHz |
| 50 µK | 0.110 m/s | 38 kHz |
| 20 µK | 0.070 m/s | 24 kHz |
| 10 µK | 0.049 m/s | 17 kHz |

Since $\Gamma_{\mathrm{transit}}\propto\sqrt{T}$ and nothing else in the
budget depends on temperature at fixed atom number, a molasses temperature
ladder is the only lever that acts on it. **How well it acts is a separate
question and the answer is badly**: what the ladder reads is not
$\Gamma_{\mathrm{transit}}$ but the second-order contribution below,
[6.70 to 9.94](../../results/transit_additivity.csv "ref:transit_additivity:spanned:added_width_170uK_band")
kHz at 170 µK against a 71 kHz kernel, and
[5.0452](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:temperature_ladder:sigma_transit_frac")
fractional precision at the 2025 lock, read from a design whose added width
comes from `results/transit_additivity.csv` and not from a coefficient
fitted here. Being the only lever and being a good one are different claims.

**This table stood at $f=1$ for as long as the derivation above it said
$f=0.24$ to $0.44$**, so it read 163 kHz at 170 µK where the committed kernel
gives 72. It is now computed through `transit_fwhm` at the flux-weighted
ensemble default rather than typed from the retired form.

### 9.3 The light shift

The ladder is unchanged in form. With $\Delta\alpha = \alpha(6S)-\alpha(5S)$,

$$S(d) = \frac{\Delta\alpha}{2\varepsilon_0 c h}\frac{P}{A_{\mathrm{Stark}}}g(d),
\qquad g(d) = \frac{\langle|E(a+d)|^2\rangle_\phi}{\langle|E(a)|^2\rangle_\phi}$$

with $A_{\mathrm{Stark}}$ the area a light shift divides power by, which is
**not** the mode area a power budget uses. The two differ by about a quarter on
these fibres, because $E_z$ carries no axial flux, and dividing by
$A_{\mathrm{eff}}$ instead lands a reader a quarter low.

**The profile $g$ is $|E|^2$ from the solved fields**, not
$[K_1(q(a+d))/K_1(qa)]^2$, for two reasons: $K_1$ alone describes $E_z$, about
a tenth of the field, and a light shift scales with $|E|^2$ rather than with
the axial flux, which for a guided mode is a further 18 per cent at the trap
distance. Earlier forms are in [HISTORY](../HISTORY.md).

What changes is that $w_0$, an assumed quantity in the cell and the record's
largest open systematic, is replaced by $a$, which is measurable, and by a
mode that the eigenvalue equation of 9.1 computes from it. **The geometry
stops being a fitted or assumed parameter and becomes an instrument
specification.**

For free atoms crossing the field the shift distribution is the evanescent
analogue of the ramp of chapter 3, taken over the $K_1^2$ profile and not over
a Gaussian. For atoms held in a two-colour trap at $d_0$ the distribution
collapses toward a single shift, and the residual width is set by the trap's
own radial spread.

### 9.4 The atom-surface potential, which has no cell analogue

Within a few hundred nanometres of the glass each level is shifted by a
Casimir-Polder interaction, in the near-field van der Waals limit

$$U_i(d) = -\frac{C_3^{(i)}}{d^3}$$

so the transition shifts by the **differential** coefficient

$$\frac{\Delta U(d)}{h} = -\frac{C_3^{(6S)}-C_3^{(5S)}}{h d^3}$$

With the committed $C_3^{(5S)} = 845$ Hz µm³ and the ratio
$C_3^{(6S)}/C_3^{(5S)}$ committed as 3 to 6:

| $d$ | $\Delta U/h$, ratio 3 | ratio 6 |
|---|---|---|
| 100 nm | $-1.69$ MHz | $-4.23$ MHz |
| 200 nm | $-0.21$ MHz | $-0.53$ MHz |
| 400 nm | $-0.026$ MHz | $-0.066$ MHz |

**The sign is carried, not dropped.** With $C_3^{(6S)} \gt C_3^{(5S)}$ the
equation above makes $\Delta U/h$ negative, so the surface pulls the line
**red**. This record has twice printed a magnitude where a direction was
meant, and both times an `abs()` hid it.

Against a natural width of 3.4925 MHz this is a leading term within 100 nm and
a small correction beyond 400 nm. **The factor of two spanned by the $C_3$
ratio does not shrink with integration time**, which is what makes it a
measurement target and not a systematic to average down.

### 9.5 The three separations, and what each one costs

The four terms above share one observable, so the design question is which
knobs move them differently. Three do.

| knob | $\Gamma_{\mathrm{transit}}$ | $S_0$ | $\Delta U$ | $\gamma_{\mathrm{coll}}$ |
|---|---|---|---|---|
| molasses temperature | $\propto\sqrt{T}$ | — | — | — |
| probe power | — | $\propto P$ | — | — |
| trap-colour ratio, moving $d_0$ | weak | $\propto I(d_0)$ | $\propto d_0^{-3}$ | — |

**Power separates the light shift from the surface term by exponent alone**,
with no model of the surface required, because $S_0\propto P$ and $\Delta U$
is power-independent. **Temperature separates transit from everything else.**
**The distance scan measures the decay length, and through it the fibre
diameter.** Its sensitivity must be weighted by the intensity present at each
rung, the fitted observable must be a frequency rather than a bare ratio, and
the drive's own surface shift must be marginalised because the scan cannot know
it a priori. With all three, the mode length comes out at
[0.2895](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:distance_scan:sigma_lambda_frac")
and the diameter at
[30.7](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:distance_scan:sigma_diameter_nm") nm
at the 2025 drifting lock, falling to
[0.67](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.0:sigma_diameter_nm") nm
at the photon floor.

**The surface coefficient is the weaker parameter of the same scan**, at
[1.851](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:distance_scan:sigma_C3_frac"),
because the light-shift column is large and the $d^{-3}$ column is not.

*This paragraph said the opposite on every count for part of 2026-08-28: that
the scan reached $C_3$ at 16 per cent, that the mode length came out at 48, and
that the route to the diameter was closed. `docs/big_picture/06` narrates that
history.*

### 9.6 What the twin says this buys, and what it costs

Monte Carlo through simulate, fit and read the covariance
(`results/campaign_twin_forecast.csv`):

| | vapour cell | nanofibre |
|---|---|---|
| collisional width | 0.19 to 0.93 MHz | 178 Hz at MOT density |
| $\mathrm{corr}(\gamma_{\mathrm{coll}},\sigma_G)$ | $-0.941$ at 5 traces, $-0.913$ at 80 | $-0.941$ |
| error on the Lorentzian excess at 0.004 of peak | 0.0035 MHz, 80 traces | 0.0090 MHz, 5 traces |
| time per trace at 0.004 of peak | seconds | **69 +- 16 minutes** |

**Three quantitative conclusions.**

1. **The fibre does not break the Voigt degeneracy.** The
   Lorentzian-against-Gaussian correlation is $-0.94$ on both platforms, and
   sixteen times more cell data moves it by 0.03. It is a property of fitting
   a Voigt, not of the apparatus.
2. **What the fibre changes is the composition of the Lorentzian.** Collisions
   fall by about 3300, so the excess has one temperature-dependent origin
   instead of two, and the ladder of 9.2 becomes attributive and not
   merely constraining. **Attributive is not the same as precise**: the
   ladder's own fractional precision is
   [5.0452](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:temperature_ladder:sigma_transit_frac")
   at the 2025 lock, so what it
   buys is which mechanism the width belongs to, not how big it is.
3. **The cost is photons.** At the demonstrated 25 to 40 counts per ms,
   matching the cell's per-trace precision takes about an hour per trace, and
   surface adsorption scales with exposure time and not with power.

**The limitation this does not remove.** `results/fibre_twin.csv` identifies
the common Lorentzian component at
[0.9640](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_312nm:coverage_gamma_l") and
[0.9580](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_492nm:coverage_gamma_l") coverage across
the decay band, and **fails on the Gaussian**, at
[0.4040](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_312nm:coverage_sigma_g") and
[0.3760](../../results/fibre_twin.csv "ref:fibre_twin:O2A_lambda_492nm:coverage_sigma_g"). The ladder returns the
Lorentzian total, not the full Lorentzian-Gaussian split, and no design in
this chapter changes that.

---

*[Assumptions and outlook](08_assumptions_and_outlook.md) · [The nanofibre campaign case](../big_picture/06_next-nanofibre.md)*
