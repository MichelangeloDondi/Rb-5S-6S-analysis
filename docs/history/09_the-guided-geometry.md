# The guided geometry

*[History](../HISTORY.md) · the nanofibre mode, its kernels, and what an assumed geometry had been carrying*

> Entries are dated records, newest last. The live value of anything named here is in the file the entry names, never in this page.

**This is a fibre-thread page.** A reader with no interest in guided geometries
skips it and loses nothing: no vapour-cell result depends on anything below.
The thread is declared in [BIG_PICTURE](../BIG_PICTURE.md).

**Why this chapter exists.** The nanofibre arm rested for its whole life on an
*assumed* effective index band. Solving the mode moved twenty committed rows at
once, and every entry below is downstream of that single change. It is the
largest correction cluster in the record since the light-shift restatement, and
it belongs in one place, not scattered across the chapters whose
quantities it touched.

## The mode was assumed and is now solved, 2026-08-27/28

| quantity | was | now | file | cause |
|---|---|---|---|---|
| effective index band | 1.08 to 1.25, tagged `assumed_parameter` | solved per diameter, 1.01283 / 1.01927 / 1.03164 at 350 / 370 / 400 nm | `results/guided_mode_tables.csv` | the assumed band describes a 485 to 796 nm fibre. **The fibres in question are 350 to 400 nm, so the band did not contain the apparatus** |
| effective mode area, 400 nm | 0.50 µm², assumed | 0.615 µm² azimuthal-mean, 0.489 µm² peak | `results/guided_mode_tables.csv` | a solve of the vector fields, under a convention that must now be stated with the number |
| evanescent profile | one Bessel term, $[K_1(qr)/K_1(qa)]^2$ | the axial flux of the full vector field | `rb5s6s/fibre.py` | that term describes $E_z$ alone, about a tenth of the field, and is low by 2.7 |
| guided light shift at 1 mW | 10.7 MHz, one number at the glass under the assumed geometry | two rows on the solved one: 11.5 MHz at the glass (`S0_onf_1mW`) and 1.12 MHz at the 400 nm trap distance (`S0_onf_1mW_at_400nm`), same fibre | `results/onf_candidate.csv` | **evaluated at the glass surface, where no atom is**, and scaled by axial flux where a shift scales with the field squared |

**The two areas are two quantities, and the dispute was not arithmetic.** Four
computations spanning a factor of six turned out to be measuring different
things: power over the axial flux is a *power budget*, power over the mean
squared field is what a *light shift* divides by. Both are now emitted under
stated conventions, because for a guided mode they are not proportional, a
large part of the near-surface energy sits in $E_z$, which carries no axial
flux at all.

**What made the fields checkable, not asserted.** $E_z$ and $H_\phi$ must
be continuous at the glass. The first field build failed that by 53 per cent,
and because the ratio was exactly $n_1^2$ it located a missing region-dependent
factor in the H fields in one line. That validator is why the settled numbers
can be trusted without re-deriving them.

## The transit kernel, and every claim about it retired in one day, 2026-08-28

The claim was retired, replaced, and the replacement retired again, in one day.

| the claim | why it died |
|---|---|
| the guided transit kernel is a Lorentzian of FWHM $\bar v/(\pi\Lambda)$ | a lineshape is the **squared magnitude** of the coupling's transform, which gives a squared Lorentzian, and the Maxwell average narrows it again |
| it adds **exactly** to the other homogeneous widths | false, and the reason is structural, not numerical |
| it adds **almost** exactly | also false, and wrong in the same direction as the claim it replaced |

**What survived.** The kernel's time function $(1+|t|/\tau)e^{-|t|/\tau}$ has
**no linear term**, the property that makes Lorentzian widths add, so it enters
the width at *second* order and a temperature ladder grows as $T$ rather than
as $\sqrt T$.

| quantity | was | now | file |
|---|---|---|---|
| guided transit band, cold | 98 to 181 kHz | 73 to 98 kHz | `results/onf_candidate.csv` |
| kernel factor $f$ | 1 | 0.24 to 0.44, spanned across the velocity weighting | `rb5s6s/fibre.py` |
| what the kernel adds to the line | its whole width | a band per temperature, `results/transit_additivity.csv` | `scripts/run_transit_additivity.py` |
| temperature-ladder precision | 0.875 | 5.0452 | `results/onf_lever_ranking.csv` |

**The second correction was a mechanism rather than a third number.** The
coefficient had been fitted by convolving a *single* squared Lorentzian at the
*ensemble's* FWHM. The ensemble is a **mixture**, and a mixture differs from
one component of equal width in exactly the curvature the added width depends
on. That cost a factor of two, and survived because the quantity was a
hand-fitted literal with no producer.
`scripts/run_transit_additivity.py` replaced it,
`tests/test_transit_additivity.py` pinned its properties, and
`run_onf_lever_ranking.py` was rewired to read the committed row.

## What a lever is worth, and it moved against the campaign

| lever | was | now | file |
|---|---|---|---|
| distance scan → fibre diameter | "about 5 per cent" | ±[30.7](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:distance_scan:sigma_diameter_nm") nm at a 2025-grade lock, ±[0.67](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:lock_span_0.0:sigma_diameter_nm") nm at the photon floor | `results/onf_lever_ranking.csv` |
| distance scan → $C_3$ | 11 per cent | [1.851](../../results/onf_lever_ranking.csv "ref:onf_lever_ranking:distance_scan:sigma_C3_frac") as a fraction, the weakest lever, not the third of three | `results/onf_lever_ranking.csv` |
| power sweep → $\kappa$ | 5.2 per cent | 11.3 per cent, and it is the leading lever | `results/onf_lever_ranking.csv` |

**Every one of these moved against the fibre case.** They are recorded
together for that reason. The diameter lever in
particular is now *worse* than the ±10 nm an earlier chapter claimed, and beats
it only once residual lock drift is at or below about 10 kHz per minute.

## The class this chapter is an instance of

**A repair applied to one site of a class and not to its siblings.** It
recurred at least eight times in one night, and every instance was found by a
checking pass, not while the change was made. Three stand for the rest. The
retracted "adds exactly" survived at nine reader-facing sites after the code
was fixed. A transit band solved on the 400 nm fibre was read into a forecast
written for the 370 nm one. And a guided quantity evaluated at the glass was
carried into every downstream row.

`tests/test_fibre_diameter_provenance.py` answers it, failing any producer that
names a guided quantity solved at a different fibre diameter. The general
lesson is in [producers and provenance](05_producers-and-provenance.md).

## The ruler-resolvability table, and the rows behind it, 2026-08-28

| quantity | was | now | file |
|---|---|---|---|
| cold-fibre transit width | 0.141 MHz | 73 to 98 kHz | `results/onf_candidate.csv` |
| teeth per transit width, cold fibre | 88.5 | 127.18 to 171.45 | same |
| hot-vapour transit width, 130 C | 232 MHz | 98 MHz | same |
| drive needed to restore the teeth | about 695 MHz | 294.8 MHz | same |

**Cause: the prose was corrected on 2026-08-21 and the table under it was not.**
Two committed rows were also still built on the transit value the producer
itself marks as no longer used, ninety lines below the marking, so the budget
and the teeth ratio carried it forward. The table cells are citations now
rather than typed numbers.

## The hot transit width was still the retired route, 2026-08-29

| quantity | was | now | file |
|---|---|---|---|
| hot-vapour transit width, 130 C | 98 MHz | 140.3 MHz | `results/onf_candidate.csv` |
| teeth per transit width, hot fibre | 0.13 | 0.09 | same |
| drive needed to restore the teeth | 294.8 MHz | 421.0 MHz | same |

**Cause: the cold rows were rebuilt on the direct form on 2026-08-21 and the
hot row was not.** It kept the cell's Gaussian-beam coefficient on an
exponential envelope and used the amplitude decay length where the cold rows
use the intensity one. Those ran opposite ways and partly cancelled, which is
why the value looked reasonable, and the direction flattered the ruler's
reach. Both rows come from one route now.

## A repair's own account of itself was wrong, 2026-08-28

| the claim | why it died |
|---|---|
| the analytic route is a lower bound on the added width | it is an upper one. The two routes agree at leading order by construction, and the gap is the first-order term, which is negative |
| the gap orders with the spread of the transit time | that ordering was the ordering of a wrong velocity weight |
| a value read only through `abs()` hid the sign on all three branches | it hid one. The other two were genuinely positive, made so by the weight |

**The last row is the one worth keeping.** Two independent errors held the
retired claim up, each concealing the other's signature, so a repair filed
under "expose the sign" would not have found it: exposing the sign alone would
have failed on one branch and passed on the two carrying the weight bug. The
first account of the repair chose the tidier single-cause story, which is the
flattering direction. The live rows are in `results/transit_additivity.csv`,
signed.

## The silica index at the working wavelength, 2026-08-28

| the claim | where | was | is |
|---|---|---|---|
| the fused-silica index at the record's own wavelength, attributed to Malitson | `rb5s6s/fibre.py` | `1.4525`, the 852 nm entry duplicated | `1.45050`, and the module now computes every index from the Sellmeier form itself, so no copy can drift |

**Cause: a hand-typed table, plus a second bare literal in the field builder
that agreed with it only while both were wrong.** Found by re-solving the
characteristic equation with both indices when a release note's diameter band
would not reconcile with the committed rows. Every guided decay length and
mode area moved by about one per cent or less, and the rows in
`results/guided_mode_tables.csv` and its consumers carry the corrected
values.

## The hot fibre's siblings, and the line budget's missing term, 2026-08-29

| quantity | was | now | file |
|---|---|---|---|
| teeth per transit width, hot fibre | 0.09 | 0.08 to 0.10 | `results/onf_candidate.csv` |
| drive needed to restore the teeth | 421.0 MHz | 358.6 to 483.4 MHz | same |
| the cold-fibre line budget | natural + laser + transit | the same plus the atom-surface term | same |

**Cause of the first two: a band was computed and the two rows consuming it
were not changed to take it.** The hot branch of the derived-row loop received
the central value where the identical cold branch received a pair.

**Cause of the third: the budget omitted a term its own file points at.** The
`cp_shift_*` rows say in their notes that they are read against the budget,
and the budget listed natural width, laser and transit only. What the term
does to the laser-width claim is stated on the row itself.

---

*[History](../HISTORY.md) · [methods chapter 9](../methods/09_the_guided_geometry.md) has the derivations*
