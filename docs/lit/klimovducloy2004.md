---
citekey: klimovducloy2004
type: article
authors:
  - Klimov, V. V.
  - Ducloy, M.
title: 'Spontaneous emission rate of an excited atom placed near a nanofiber'
journal: Phys. Rev. A
volume: 69
pages: 013812
year: 2004
doi: 10.1103/PhysRevA.69.013812
arxiv: physics/0206048
pdf: PDF_papers/KlimovDucloy_2004_spontaneous-emission-atom-near-nanofiber.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'IDENTIFIER AMBIGUITY, unresolved. The held file is arXiv physics/0206048v2
    (20 December 2002), whose title matches Phys. Rev. A 69, 013812 (2004)
    exactly -- but the arXiv metadata carries an Optics Communications DOI
    (10.1016/S0030-4018(02)01802-3), not the PRA one. Either the arXiv
    journal-ref is stale/wrong, or the authors published a shorter Optics
    Communications version first and this preprint corresponds to both. The PRA
    reference above is as printed in sague2007 ref [14] and was verified against
    that bibliography; it has NOT been checked against the published PRA
    article. Settle before formal citation.'
  - 'The 31-page preprint is longer than a PRA article, which is consistent with
    it being the full manuscript behind a condensed publication. Section and
    equation numbers in the held file may therefore not match the published
    version -- do not cite an equation number from this file.'
verified_date: 2026-07-30
summary: >
  The theory input for the position-dependent free-space decay rate
  gamma_free(r) that sague2007 uses, and that patterson2018 omits from its
  width. Spontaneous decay rates of an excited atom near a DIELECTRIC CYLINDER,
  with the subwavelength (nanofiber / photonic wire) case treated specially:
  analytical expressions for the transition rates are derived for different
  dipole orientations, the dominant contribution is the QUASISTATIC interaction
  of the atomic dipole with the fibre, and guided-mode contributions are
  exponentially small in that regime. Section III READ: their
  Eq. (29) gives gamma_rad/gamma_0 in closed form for rho-, phi- and
  z-oriented dipoles, depending on position only through a^2/rho'^2, with the
  z rate unmodified and the rho and phi rates moving in OPPOSITE directions.
  THE CONCLUSION, READ THE SAME DAY, RETIRES THE PLAN TO USE THAT CLOSED FORM
  DIRECTLY: the paper proves quasistatic validity only for ka < 1/epsilon, and
  BOTH fibres of interest violate it -- patterson2018 at ka = 0.97 by a factor
  of two, sague2007 at ka = 1.84 by nearly four. Both land instead in the band
  1/eps < ka < 2.4/sqrt(eps-1) where the paper says guided-mode influence is
  SUBSTANTIAL, which is precisely why sague2007 carries a separate gamma_guid
  term. So a refit needs Section IV, not Eq. (29); and the +8.5%-vs-+27%
  discrepancy is more likely a symptom of using the formula out of range than
  the orientation-weighting effect this note first proposed.
loci:
  - P2
  - THEORY
section: method-anchors
---

# klimovducloy2004

**Held, with Section III and the Conclusion read.** Lebedev
Physical Institute (Moscow) and Laboratoire de Physique des Lasers, Université
Paris-Nord. The quasistatic section carrying the closed form is read, as is
Section VII, which is where the regime of validity is stated. The bodies of
Sections IV–VI (the full electrodynamic treatment, the lossless-surface case,
and the graphical discussion) are **not** — and, per the validity bound below,
Section IV is now the part that matters most.

## Why it is here

[sague2007](sague2007.md) builds its lineshape from a position-dependent decay
rate $\gamma(r) = \gamma_{\rm free}(r) + \gamma_{\rm guid}(r)$ and takes
$\gamma_{\rm free}(r)$ from this paper (their ref [14], verified against
Sagué's own bibliography). [patterson2018](patterson2018.md) uses the same
physical quantity as a detection weight and leaves it out of the width, which is
the candidate explanation for its unexplained 2 MHz. **This is the paper that
decides whether testing that is a day's work or a project.**

## What it provides, from the abstract

Spontaneous decay rates of an excited atom near a **dielectric cylinder**, with
"special attention paid to the case when the cylinder radius is small in
comparison with radiation wavelength (nanofiber or photonic wire)". In that
regime:

- "the **analytical expressions** of the transition rates for different
  orientations of dipole are derived";
- "the main contribution to decay rates is due to **quasistatic interaction** of
  atom dipole momentum with nanofiber and the contributions of guided modes are
  **exponentially small**";
- when the radius is only slightly less than the wavelength, guided modes can be
  substantial instead.

**This note previously concluded from that third bullet that the 240 nm fibre of
`patterson2018`, being "comfortably subwavelength", has a usable closed form
with a negligible guided-mode part — and that this "makes the refit tractable".
That was wrong, and the paper's own Conclusion says so; see the validity bound
below.** Subwavelength is not the criterion. The criterion is
$ka$ below $1/\varepsilon$, and Patterson's fibre misses it by a factor of two.

**One caution the paper states itself:** the decay rate of a *radially* oriented
dipole "tends to infinity when cylinder radius tends to zero" for an ideally
conducting nanowire. Any refit has to handle the orientation average rather than
take a single dipole orientation, and the near-surface limit needs care.
Non-radiative losses inside the body are also discussed and are a separate term.

## The closed form itself, read 2026-07-31

Section III (quasistatic analysis, from p6 of the held preprint) gives the
result this note *expected* the refit to need, and it is elementary once written
down. **The validity bound in the next section rules it out of range for both
fibres of interest, so what follows is recorded, not used.** Their **Eq.
(29)**, radiative decay rate of an atom at radial distance $\rho'$ from the axis
of a dielectric cylinder of radius $a$ and permittivity $\varepsilon$:

$$\left(\frac{\gamma^{\rm rad}}{\gamma_0}\right)_{\rho}
=\left|1+\frac{\varepsilon-1}{\varepsilon+1}\frac{a^2}{\rho'^2}\right|^2,\qquad
\left(\frac{\gamma^{\rm rad}}{\gamma_0}\right)_{\varphi}
=\left|1-\frac{\varepsilon-1}{\varepsilon+1}\frac{a^2}{\rho'^2}\right|^2,\qquad
\left(\frac{\gamma^{\rm rad}}{\gamma_0}\right)_{z}=1$$

and at the surface, $\rho'=a$, their **Eq. (30)** reduces to
$|2\varepsilon/(\varepsilon+1)|^2$, $|2/(\varepsilon+1)|^2$, and $1$.

Three properties matter for using it. The $z$ rate is **unmodified** at any
distance. The $\rho$ and $\varphi$ rates move in **opposite directions**, so an
orientation average is much smaller than the radial component alone. And the
whole thing depends on position only through $a^2/\rho'^2$ — a single scalar,
trivially insertable into a fit.

## The validity bound — which BOTH fibres of interest violate

**Read from the Conclusion, and it overturns the plan above.** The
paper states its own regime of validity explicitly:

> "It is proved that quasistatic approximation works well for a nanofiber with
> $ka$ < $1/\varepsilon$."

> "For large enough nanofiber, $1/\varepsilon$ < $ka$ < $2.4/\sqrt{\varepsilon-1}$,
> the influence of guided modes on the decay rate is **substantial**."

Evaluated for fused silica, $n = 1.4537$, $\varepsilon = 2.1132$, so
$1/\varepsilon = 0.473$ and $2.4/\sqrt{\varepsilon-1} = 2.275$
(CALCULATED 2026-07-31):

| fibre | $a$ | $\lambda$ | $ka$ | quasistatic ($ka$ below 0.473)? | guided modes substantial? |
|---|---|---|---|---|---|
| [patterson2018](patterson2018.md), 240 ± 20 nm **diameter** | 120 nm | 780 nm | **0.967** | **NO — violated by 2×** | **yes** |
| [sague2007](sague2007.md), 500 nm diameter | 250 nm | 852 nm | **1.844** | **NO — violated by 3.9×** | **yes** |

Both are inside the nanofibre regime overall ($ka$ below 2.275), so the paper
applies — but **both are in the band where the closed form is not sufficient on
its own**, and guided modes have to be added. The "comfortably subwavelength,
so there is a closed form" claim made earlier in this note was wrong: it treated
"subwavelength" as the criterion when the paper's criterion is
$ka$ below $1/\varepsilon$, which is roughly twice as strict.

**Consequence for the refit.** Eq. (29) cannot simply be coded and used. Either
the full electrodynamic treatment of Section IV is needed, or Eq. (29) has to be
supplemented with an explicit guided-mode term — which is, note, exactly the
structure [sague2007](sague2007.md) uses:
$\gamma = \gamma_{\rm free} + \gamma_{\rm guid}$ with
$\gamma_{\rm guid} \simeq 0.3\gamma_0$ at the surface. Sagué's decomposition is
not an arbitrary choice; it is what this regime requires.

## A check on Sagué, and an open question it raises

For fused silica at 852 nm ($n = 1.4537$, $\varepsilon = 2.113$), Eq. (30)
gives (CALCULATED 2026-07-31):

| dipole orientation | $\gamma^{\rm rad}/\gamma_0$ at the surface |
|---|---|
| $\rho$ (radial) | 1.843 |
| $\varphi$ | 0.413 |
| $z$ | 1.000 |
| isotropic average | **1.085**, i.e. +8.5% |

[sague2007](sague2007.md) states that their Eq. (2) — this paper's
$\gamma_{\rm free}$ plus their own $\gamma_{\rm guid} \simeq 0.3\gamma_0$ at
the surface — "predicts a 57% increase" there. Backing out,
$\gamma_{\rm free}$ must supply +27%. **An isotropic average of Eq. (30) gives
only +8.5%**, while the pure radial component gives +84%. So Sagué's 27% sits
between the two, which is what a **mode-polarisation weighting** would produce:
the HE₁₁ mode is strongly radially polarised near the surface, so the $\rho$
rate should be over-weighted relative to isotropic.

**That is an inference, not a reading of Sagué** — they do not state their
orientation weighting in the passage quoted here.

**And there is now a competing explanation which is probably the better one
(2026-07-31).** Sagué's fibre has $ka = 1.84$, nearly four times the
quasistatic bound $1/\varepsilon = 0.473$, so Eq. (30) — a quasistatic result —
simply should not reproduce their $\gamma_{\rm free}$ in the first place. The
+8.5% against +27% gap need not be an orientation-weighting effect at all: it is
the size of correction one expects when a quasistatic formula is evaluated well
outside its stated range, where the paper says guided-mode contributions are
substantial. Attributing the whole gap to mode polarisation was reaching for a
physical mechanism before checking whether the formula applied.

**Recorded as OPEN, with the question changed.** It is no longer "what
orientation average does Sagué use"; it is "does the full electrodynamic
$\gamma_{\rm free}$ of Section IV account for the +27% on its own". Both remain
unanswered, and neither Eq. (29) nor Eq. (30) should be coded into a refit of
Patterson's spectra until one of them is.

## What has not been done

The form is extracted and checked against Sagué's 57% (above), and per the
validity bound it **must not be coded as it stands** — Eq. (29) is out of range
at both fibres. An earlier version of this section named "coding the closed form,
then refitting Patterson" as the remaining work; that is withdrawn, because it
contradicts the bound recorded above.

What is actually outstanding is **Section IV**, the full electrodynamic
treatment, which is **held and unread**: 10.6k characters that expand the fields
over cylinder harmonics and solve for the reflected field, stating that it finds
"the exact expressions for decay rates, which include the contributions from
guided modes". That is the term the refit needs, and obtaining it is theory work
rather than a lookup. Only then does the falsification test recorded in
[patterson2018](patterson2018.md) become runnable. **Recorded as OPEN.**

Sections V and VI (the lossless-surface case and the graphical discussion) are
also unread, and Klimov's ref [45] — "Spontaneous emission of single atom placed
near metallic nanowires (to be published)" — is not held, but is *metallic* and
therefore the wrong material for a silica fibre.
