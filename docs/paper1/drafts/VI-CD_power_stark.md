# Paper 1 — §VI.C/D draft prose: power sweep + the AC-Stark bound

**FIRST-PASS DRAFT, for MD/Síle to revise into your voice.** Fills the
§VI.C and §VI.D stubs of `PAPER1_SKELETON.md`. Not final text; every number is
from the committed ledger (`docs/RESULTS.md`), provenance/framing notes in
**[brackets]**, figures are committed `figures/` files, LaTeX inline.

---

## VI.C Power dependence: the ramp-law predictions confirmed

At a fixed 130 °C the density, transit width, and (within one power session) the
laser width are all constant, so the only quantity that varies across the
25–225 mW sweep is the AC-Stark shift $S_0\propto P$. The intensity-averaged
"ramp" model of §III then makes three predictions that need no absolute-frequency
information — they survive the drifted lock — and the archive confirms all three
(Fig. 2).

**Linewidth is flat (C3a).** The triangular ramp of on-axis depth $S_0$ adds an
excess variance $\propto S_0^2$, which for the archival $S_0\lesssim1.4$ MHz
inflates the $\sim5$ MHz composite FWHM by under 2%. No power broadening is
observed: the measured widths are flat to within their scatter (3–8% peak-to-
peak, set by the low-SNR 25 mW points) with no monotonic trend. [This is the
sense in which the classic "power null" is not a null result but a confirmed
prediction — worth saying explicitly.] **Amplitude scales as $P^2$ (C3b).** The
two-photon rate goes as $I_\text{fwd}I_\text{ret}\propto P^2$; the measured
log–log slopes are $1.83$–$2.12$ [MEASURED-HERE] across the four components,
consistent with $P^2$. The one low value (993.4121 nm, slope $\approx1.85$) is
driven by its 25 mW point, where saturation and radiation-trapping corrections
are degenerate in a single-temperature sweep; we therefore say "consistent with
$P^2$", not "confirms $P^2$", and defer the trapping discriminator to the
interleaved fixed-lock-session data (§VII).

**The ramp asymmetry is a bound, and the low-power skew is shot noise, not the
ramp (C3c).** These are two distinct quantities and conflating them is the trap.
The *ramp's* skew — the asymmetry coefficient of the fitted ramp$\otimes$core
profile — scales as $S_0^3$ and is predicted below the archival noise floor at
$\le225$ mW; a symmetric-model fit therefore leaves it undetected, an upper bound
consistent with zero (as the corrected physics of §III requires, since the
ramp's first-order shift is absorbed by the free per-scan centre). Separately,
that symmetric fit leaves a residual skewness that is *large and positive at low
power* — up to $9.6\sigma$ (993.4154 nm, $0.35\pm0.04$ at 25 mW) — and *falls*
with power as $\sim\text{amp}^{-1/2}$. That is the Poisson **shot-noise**
skewness (photon-counting noise is right-skewed $\propto1/\sqrt{\text{counts}}$,
vanishing as the line brightens): it has the opposite sign and the opposite power
dependence to the ramp ($\propto P^3$ growth), so it is a statistical artifact of
the noise, positively identified and cleanly separated from the ramp signal. [The
old "unexplained low-power asymmetry" is thus resolved into shot noise; keep the
two-quantities framing.]

## VI.D The AC-Stark coefficient: an upper bound from the power lever

The width-versus-power data also bound the AC-Stark coefficient itself. We fit a
single shared $\kappa$ ($S_0=\kappa P$, common to the four components) to the
four FWHM-versus-power curves, each component floating its own power-independent
core width. This is only an **upper bound**, and for the same two-epoch reason as
everywhere else: the drifted lock kills the line centres, so the AC-Stark
*shift* (the pull $\propto S_0$, the sensitive handle) is absorbed by each scan's
free centre, leaving only the ramp's $\propto S_0^2$ width broadening — a weak
handle, since a 0.6 MHz $S_0$ inflates a 5 MHz line by under 0.1 MHz. The fit
returns $\kappa$ consistent with zero, giving the 95% profile-likelihood bound
$$S_0(225\ \text{mW}) < 0.63\ \text{MHz},$$
sitting just above the value $S_0=0.59$ MHz predicted from the computed
differential polarizability [CALCULATED; §III, App. A]. The archive thus
**brackets** the prediction without resolving it — a bracketing contingent on the
conservative over-dispersion rescale (below), not a resolution of the coefficient
(the width channel is drift-limited, $\chi^2_\text{red}\approx4.3$).

[Reviewer-hardening — keep this transparency, it is load-bearing.] Two
statistical choices define the bound. First, the best fit rails at $\kappa=0$,
where the width handle ($\propto S_0^2$) has zero gradient, so a linearized
(Wald) $\kappa+1.645\sigma$ interval has no valid coverage there — its
$\sigma$ is a finite-difference artifact. The quoted limit is therefore a
**profile-likelihood** bound: $\kappa$ is scanned upward with the per-component
core widths re-minimized at each point, and the limit sits at the one-sided
$\Delta\chi^2 = 2.706$ crossing. Second, the fit is over-dispersed
($\chi^2_\text{red}\approx4.3$, block-to-block width scatter), so the
$\Delta\chi^2$ threshold is scaled by $\chi^2_\text{red}$ — the profile-space
equivalent of the standard $\sqrt{\chi^2_\text{red}}$ error inflation, and the
conservative choice (the unscaled threshold would give a tighter limit). The
superseded Wald numbers stay in the CSV as diagnostics [`stark_sweep.csv`:
`S0_225mW_ub95_profile` is the bound; `_ub95` and `_ub95_raw` are labelled
superseded]. Through the §III convention, at the nominal $w_0=50\ \mu$m this
brackets the differential polarizability at $\Delta\alpha<\sim1200$ a.u.
(95%), consistent with the computed 1093 — the mapping inheriting the open
beam waist. The archive therefore does not contradict the computed
coefficient; a fixed-lock session would measure the pull $\propto S_0$ directly,
and at a smaller waist ($S_0$ several-fold larger), turning this bracket into
the coefficient (§VII).

---

### Numbers used (all from `docs/RESULTS.md` / committed CSVs, keep synced)

- C3a width inflation 3–8% (measurement scatter, no power trend); predicted ramp $<2$%
- C3b amplitude log–log slopes $1.83$–$2.12$; 993.4121 nm low end ($\approx1.85$) = saturation/trapping degeneracy
- C3c ramp skew below floor (a bound); residual skew up to $9.6\sigma$ (993.4154 nm, $0.35\pm0.04$ @25 mW), $\sim\text{amp}^{-1/2}$ = shot noise
- C3d $S_0(225)<0.63$ MHz (95%, profile likelihood, $\Delta\chi^2$ threshold scaled by $\chi^2_\text{red}\approx4.3$); superseded Wald 1.5 raw / 3.1 inflated; predicted 0.59; $\kappa=0.00$ railed; $\Delta\alpha<\sim1200$ a.u.

### Figures: 2 (`fig2_power_sweep`); a κ/S₀-vs-power panel is optional for §VI.D (skeleton note)

### Open framing choices for you
- §VI.C and §VI.D can merge into one "power dependence" section, or §VI.D can fold into §III as the archival test of the ramp coefficient — your structural call.
- How prominently to feature the shot-noise identification: it is a genuinely nice piece of forensic work (a 9σ effect fully explained), but it is also a negative/diagnostic result — decide whether it earns its own paragraph or a footnote.
- Whether to state the $\Delta\alpha<\sim1200$ a.u. bracket in the main text (it inherits $w_0$) or relegate it to the ramp-theory section where the convention lives. Note it now sits only $\sim$10% above the computed 1093, which strengthens the case for the main text.
