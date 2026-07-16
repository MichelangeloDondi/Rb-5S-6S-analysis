# Paper 1 — §VI.A draft prose: collisional self-broadening (the β bound)

**FIRST-PASS DRAFT, for MD/Síle to revise into your voice.** This fills
the §VI.A stub of `PAPER1_SKELETON.md` with real prose so the writing has a seed;
it is not final text. Every number is from the committed ledger (`docs/RESULTS.md`);
provenance tags and framing notes are in **[brackets]** for you to resolve or
delete. Figures referenced are the committed `figures/` files. LaTeX is inline
(port to the journal template later).

---

## VI.A Collisional self-broadening: an upper bound

At fixed laser and beam geometry the only temperature-dependent contribution to
the homogeneous linewidth is the collisional self-broadening
$\gamma_\text{coll}(T)=\beta_\text{self}N(T)$, linear in the Rb number density
$N(T)$ for binary collisions. We vary $N$ over a factor of 52 across the
70–130 °C sweep and ask what the archive constrains about $\beta_\text{self}$.
The answer is an **upper bound**, not a value — and the reason it is only a
bound is itself the central result of this section.

**The model-independent bound.** Because the collisional width adds in
quadrature-free fashion to the much larger transit and laser widths (total FWHM
$\approx5$ MHz against a natural width $\Gamma_\text{nat}=3.4926$ MHz [ESTABLISHED]),
$\beta_\text{self}$ is most robustly bounded by the *slope* of the measured width
with density, with no lineshape decomposition. That slope is not resolved: the
raw half-maximum widths are **non-monotonic** in $N$ for three of the four
hyperfine components (Fig. 1), which is impossible for a genuine collisional
term, which can only broaden. The non-monotonicity is set by the between-block
drift of the laser width ($\sim0.06$–$0.16$ MHz across the cooling session),
which is comparable to the entire collisional trend it would have to sit on top
of. Bounding the width-vs-density slope by this scatter gives
$$\beta_\text{self}\lesssim 0.2\text{–}0.4\ \text{MHz per }10^{12}\ \text{cm}^{-3}\quad(95\%,\ \text{per component})$$
[MEASURED-HERE, per-peak]. Each bound rests on only 1–2 residual degrees of
freedom (three-to-four density points minus the fit parameters), so it carries a
$\sim$factor-2 own-uncertainty and the $\approx2\sigma$ coverage is approximate;
we therefore quote it to two figures. [Framing: this is the headline archival β
number — say so explicitly. `beta_self_probe.csv:bound95`.]

**Why it is a bound and not a value: the lever test.** A hierarchical fit that
shares one laser width per temperature across the four components and ties
$\gamma_\text{coll}=\beta N$ does return a nominal $\beta_\text{self}=0.036(4)$
(statistical) on the internally-consistent 70/90/110 °C cooling sweep. That
number must not be read as a measurement. Its own diagnostics show why. The
fitted collisional width rises only by a factor $\sim1.5$ (from
$\approx0.41$ to $\approx0.61$ MHz, four-component mean) while the density rises
by a factor 52 (Fig. 6) — far short of the linear scaling a real binary-collision
width requires, so the fitted $\gamma_\text{coll}$ is a near-constant residual
*floor* (unmodelled transit/laser width plus block scatter), not a resolved
collision rate. Consistently, the inferred $\beta$ is **lever-dependent**: adding
the higher-density 130 °C block (extending the density lever from $\times16$ to
$\times52$) pulls the joint value down to $0.014$, and per-condition fits give
$\sim0.01$ [MEASURED-HERE, `beta_lever_probe_130`, `gamma_rise_factor`]. A slope
that moves by $\sim8$ times its own statistical error when a legitimate density
point is added is, by definition, unresolved. The $0.036$ is the short-lever end
of a lever-dependent range that is bounded above by the model-independent number
quoted first; the two are consistent, and the bound is the honest headline.
[Framing note: the 130 °C block is a different acquisition session; we treat it
as a lever probe, not a headline point — see §IV, App. C. The point survives
either way, because the 130 °C widths sit *on* the flat trend rather than off it.]

**Isotope test and error budget (the hierarchical cross-check).** Although
lever-limited, the joint fit is a useful cross-check because it tests the two
isotopes against each other under a common laser model. It finds
$\beta_{85}=\beta_{87}$ to within
$\beta_{85}-\beta_{87}=0.000\pm0.006$ ($0.0\sigma$) — no isotope dependence, as
expected if the collisional physics is common. The nominal $0.036$ carries three
separately-sourced systematics on the cooling-sweep estimator: a statistical
$\pm0.004$; a transit model-form $\pm0.033$ [the shift between the established
Biraben–Cagnac cusp transit and a cusp-free Gaussian null — App. B]; and a
$w_0$-band $[0.004,0.055]$, the largest, reflecting the open beam waist on which
every absolute width depends. It is robust to removing any single component
(dropping the 993.4207 nm line, the one with anomalous per-peak diagnostics,
moves $\beta_{87}$ by $-0.004$, below its statistical error, and leaves the
laser-width pattern intact). [These bars are the *estimator's* precision and
systematics; they do not span the lever range above, which is why the bound, not
this budget, is quoted as the result — keep that distinction explicit.]

**Physical context.** Scaling the measured 7S self-shift of Zameroski *et al.*
[ESTABLISHED; *J. Phys. B* **47**, 225205] to the 6S state gives an expected
$\beta_\text{self}(6S)\sim1$ kHz per $10^{12}$ cm⁻³ — 40 to 100 times below our
archival bound. The archive is therefore consistent with, but does not
constrain, the expected collisional physics, and it cannot: over 70–130 °C the
predicted broadening is $\lesssim20$ kHz, far under the $\sim$MHz systematics.
Resolving $\beta_\text{self}(6S)$ needs the density pushed to where the effect
clears the floor — 150–170 °C, taken in a *single* fixed-lock session so the
lever is not broken by the between-session drift the archive exhibits (§VII). The
archive's role is thus to establish the bound, the systematics, and the method,
and to demonstrate — through the non-monotonic widths and the lever test — that a
drifted-lock dataset cannot do more, which is exactly what motivates the
fixed-lock campaign.

---

### Numbers used (all from `docs/RESULTS.md`, keep synced)

- bound $0.2$–$0.4$ MHz per $10^{12}$ cm⁻³ (95%/peak: $t(1)=6.31$ on the 1-DOF scatter, ×1.2 density-scale; loosest peak = the floor)
- hierarchical $0.036(4)$ stat; lever $\to 0.014$ (+130), per-condition $\sim0.01$
- $\gamma_\text{coll}$ mean $0.41\to0.61$ MHz over $N\times52$ (rise $\times1.5$)
- isotope $\beta_{85}-\beta_{87}=0.000\pm0.006$; bars stat $\pm0.004$ / transit $\pm0.033$ / $w_0$ $[0.004,0.055]$
- drop-4207 $\Delta\beta_{87}=-0.004$; $\Gamma_\text{nat}=3.4926$ MHz; Zameroski expectation $\sim1$ kHz per $10^{12}$ cm⁻³

### Figures: 1 (`fig1_width_vs_density`), 5 (`fig5_pooled_width`), 6 (`fig6_gamma_floor`)

### Open framing choices for you
- Whether to lead the section with the bound (recommended) or the hierarchical number.
- How hard to lean on the "the archive proves the two-epoch design was necessary" line — it is defensible and strong, but it is a rhetorical choice.
- Whether the isotope test deserves its own short subsection given it is the one genuinely *measurement-like* output (a null, but a clean one).
