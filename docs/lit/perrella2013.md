---
citekey: perrella2013
type: article
authors:
  - Perrella, C.
  - Light, P. S.
  - Anstie, J. D.
  - Stace, T. M.
  - Benabid, F.
  - Luiten, A. N.
title: 'High-resolution two-photon spectroscopy of rubidium within a confined geometry'
journal: Phys. Rev. A
volume: 87
pages: 013818
year: 2013
doi: 10.1103/PhysRevA.87.013818
arxiv: null
pdf: PDF_papers/theses/Perrella_2013_PhD-thesis_nonlinear-spectroscopy-Rb-hollow-core-fibres.pdf
held: true
status: VERIFIED
routing:
  - CITE
verify_flags:
  - 'HELD VIA THE THESIS, NOT THE ARTICLE. The APS paper is paywalled and has no
    arXiv preprint (checked 2026-07-30). What is held is the first author''s
    open-access UWA PhD thesis, "Non-Linear Spectroscopy of Rubidium in
    Hollow-Core Fibres" (Feb 2013, 235 pp, supervisors Luiten and Light), which
    REPRINTS this paper in full including its abstract, setup and figures.
    Quotations below are from that reprint. Page and figure numbers are the
    article''s own.'
  - 'The two questions this note previously carried as OPEN are now SETTLED from
    that reprint, and both had been guessed correctly in one case and wrongly in
    the other -- see the body. Excitation: TWO-COLOUR, 780 + 776 nm. Fibre:
    kagome HC-PCF, 45 um CORE DIAMETER, 40 cm, at 90 C.'
verified_date: 2026-07-31
summary: >
  Two-photon spectroscopy of THERMAL Rb vapour in a hollow-core fibre
  (Adelaide/Luiten with Benabid), 5S1/2 -> 5D5/2, linewidths as narrow as
  10 MHz, >90% nonlinear absorption, absorption sustained to 9 GHz of
  intermediate-state detuning. Held from 2026-07-31 via the first author's
  open-access PhD thesis, which reprints the paper. TWO CORRECTIONS TO THIS
  NOTE followed: the excitation is TWO-COLOUR (780 + 776 nm, an ECDL and a
  Ti:sapphire), as the 9 GHz detuning scale had suggested; and the fibre is a
  kagome HC-PCF of 45 um CORE DIAMETER at 90 C, so the mode radius is ~15 um
  and transit accounts for only 3-4 MHz of the 10 MHz -- NOT the few-micron,
  transit-limited mode this note previously inferred by reading the geometry
  backwards out of the linewidth. The thesis points at coupling to higher-order
  transverse modes, caused by the curved large-core fibre, for the remainder.
loci:
  - M9
  - P2
section: oist-lineage
---

# perrella2013

**VERIFIED 2026-07-31, via the thesis.** The APS article is paywalled and has no
arXiv preprint, but the first author's open-access UWA PhD thesis — *Non-Linear
Spectroscopy of Rubidium in Hollow-Core Fibres*, 235 pp — reprints it in full,
and is what is held. The record itself came from Crossref (authoritative for the
DOI, confirming every field the experimenter supplied) and the abstract was
supplied verbatim by the experimenter from the publisher listing.

**Abstract, verbatim.** "We present two-photon spectroscopy of a thermal rubidium
vapor confined to the hollow core of a photonic-crystal fiber. Linewidths as
narrow as 10 MHz were observed on the 5S₁∕₂→5D₅∕₂ transition enabling the
hyperfine splitting of the excited state to be resolved. Very strong nonlinear
absorption (>90%) was observed, with substantial absorption maintained over large
detunings (9 GHz) from an intermediate state. These attributes make this system
ideal for many frequency metrology and quantum optics applications."

## Where it sits

[saha2010](saha2010.md) is the existence proof — *degenerate* Doppler-free
two-photon Rb at 778 nm inside a **6 µm-core** photonic band-gap fibre, 1%
absorption at 1 mW. This is the same **platform** pushed to **high resolution
and near-complete absorption**: >90% nonlinear absorption, and a line narrow
enough to resolve 5D₅∕₂ hyperfine structure. It is **not the same experiment**,
and the note used to call it "the same geometry", which it is not: the core here
is a 45 µm kagomé, seven times wider, and the excitation is **two-colour
780 + 776 nm** rather than degenerate 778 nm. Both differences change what
transfers. Where
[slepkov2010](slepkov2010.md) models the AC-Stark shift through a Gaussian-core
guided mode, this measures what the resulting line actually looks like. It
belongs in the guided-mode paragraph of `LITERATURE.md` §5 alongside those two.

## The number that matters here, and it is a cost not a benefit

The programme's guided-mode extension is usually argued on absorption: a hollow
core holds the intensity over centimetres instead of a Rayleigh range. This paper
supplies the other half of the ledger. Feeding a guided-mode radius through this
repository's **own** `transit_fwhm_from_w0` at 100 °C (CALCULATED here, not read
from the paper):

| mode radius $w_0$ | transit FWHM |
|---|---|
| 2 µm | 29.5 MHz |
| 3 µm | 19.7 MHz |
| 5 µm | 11.8 MHz |
| 8 µm | 7.4 MHz |
| 12 µm | 4.9 MHz |
| 20 µm | 2.9 MHz |

**That inference was wrong, and the paper's own thesis says so
(2026-07-31).** It read the geometry backwards out of the linewidth: "as narrow
as 10 MHz" was taken to imply $w_0 \approx 5$–6 µm. The fibre is nothing like
that. Perrella's PhD thesis (`theses/`, 235 pp, open access from UWA, which
reprints this paper in full) states the setup outright: a **kagomé HC-PCF of
45 µm core diameter**, 40 cm long, at **90 °C**, with a mode radius therefore
around 15 µm. Recomputed at that geometry:

| $w_0$ | transit FWHM at 90 °C |
|---|---|
| 14.6 µm ($0.65a$) | **3.98 MHz** |
| 15.8 µm ($0.70a$) | **3.69 MHz** |
| 22.5 µm (= core radius, upper bound) | 2.58 MHz |

So **transit accounts for only 3–4 MHz of their 10 MHz**, not the whole of it,
and this paper is *not* an example of a transit-limited hollow-core line. The
thesis names a likely source of the remainder: the fibre "was curved between the
vacuum chambers, which, combined with its large core diameter, resulted in
**coupling to higher-order transverse optical modes**" — several modes with
different intensity profiles, which broadens a two-photon line without any of it
being transit. Pressure broadening they put at ≈12 kHz, negligible.

**The penalty depends entirely on which fibre, and this note has now been wrong
about it in both directions.** The scaling is $1/w_0$. A first version called it a
flat "factor of ten"; a correction then put the repository's own candidate at
3.3 MHz — a factor of 2.8 — on the strength of an **18 µm mode field** attributed
to [saha2010](saha2010.md) and [slepkov2010](slepkov2010.md). **Both attributions
were wrong** (checked 2026-07-30): neither paper contains an 18 µm figure. The
description that replaced them — "an apparatus value for a *prospective*
collaboration" — was **also wrong**, and was retracted in
[saha2010](saha2010.md): the CRYST³ fibre is the experimenter's **own operating
apparatus** at Bologna, not a prospect. It is now sourced to
[nasoni2026](nasoni2026.md).

The hollow cores actually in this literature are much tighter, and the penalty is
correspondingly much worse (CALCULATED at 100 °C with the repo's own function):

| fibre, as published | mode radius | transit FWHM |
|---|---|---|
| Saha's Crystal Fiber AIR-6-800, **6 µm core** | ~2.1 µm | **28 MHz** |
| Slepkov's stated area $10^{-7}$ cm² | ~1.8 µm | **33 MHz** |
| a 10 µm core (Slepkov's acetylene citation) | ~3.5 µm | **17 MHz** |
| free-space campaign prior | 50 µm | 1.2 MHz |
| CRYST³ 1064 nm ODT injection waist, a RADIUS ([nasoni2026](nasoni2026.md)) | 18 µm target; 17.1×19.3 µm measured | *3.1–3.4 MHz* |

So Perrella's 10 MHz is narrower than transit alone would give in any of the
*published* hollow cores — but **that follows from their fibre, which is now
known, not from their line**. The thesis states a 45 µm kagomé core, putting the
mode radius near 15 µm by the $0.65a$–$0.70a$ convention, seven to eight times
looser than Saha's or Slepkov's. *An earlier version of this sentence said the
10 MHz "implies a looser mode than Saha's or Slepkov's" — that is the
reading-the-geometry-backwards-out-of-the-linewidth move this note already
retracted once, and it is withdrawn here too.* The penalty across *that
literature* is roughly **15–30×**.

**But the relevant fibre is not one of theirs.** The experimenter's own CRYST³
hollow core (EU H2020 GA 964531, the Bologna apparatus behind their doctoral
work) runs an ~18 µm injection waist, giving **3.1–3.4 MHz**. So there are two
different statements and they must not be run together: *published* hollow cores
in the Rb two-photon literature are tight and cost 15–30×; *this programme's*
fibre is much larger and costs about 3×.

**The 18 µm was an apparatus fact with no source in this repository, and was
sourced 2026-07-31** — a held master's thesis on that apparatus
([nasoni2026](nasoni2026.md), co-supervised by the experimenter). It is an **injection beam waist**, hence a **RADIUS**, so
the 3.3 MHz reading was the right one and the 6.6 MHz alternative is dead. It is
also *measured*: 17.1 ± 0.7 µm by 19.3 ± 0.4 µm, slightly elliptical, against an
18 µm design target and a 13.6 ± 0.1 µm ideal thin-lens value. **The live caveat
is now a different one:** that is the **1064 nm optical-dipole-trap** beam, not
a two-photon probe, and a hollow-core mode depends on wavelength — so carrying
it over to a 778 nm line is an assumption, and it rests on an unpublished
thesis.

**And with the geometry known, Perrella lands next to this programme's fibre
rather than between the two groups.** A ~15 µm mode radius against a *measured*
17.1–19.3 µm injection waist is the same regime. That makes this the **most
relevant published point in the table** — and its lesson is not the transit
number, which is a comfortable 3–4 MHz, but that the *measured* line was
10 MHz. In a real large-core fibre,
transit was less than half the width. Whatever a guided-mode extension of this
campaign budgets for transit, it should budget separately for mode structure.

*The residual inference.* The vapour temperature quoted here is the thesis's
90 °C, but the mode radius is not measured in the reprint as read — the 14.6 and
15.8 µm entries are the conventional $0.65a$–$0.70a$ fractions of the stated
45 µm core, not a published mode field. And the 10 MHz may still include laser
width and power broadening, which would leave even less of it for anything
positional.

## The compensation, which needs stating carefully

Every absolute result in this repository is `BOUND` on an unmeasured beam waist:
$w_0$ is the knife-edge measurement that has not been made, and it is the single
largest open systematic. A guided geometry is attractive partly because the mode
is fixed by the fibre and constant along the interaction length, with no
Rayleigh-range variation to average over — so $w_0$ becomes a property of a
manufactured component rather than of a daily alignment.

**That is an argument, not a result, and nothing in Perrella's abstract supports
it** — the abstract says only that the vapour is confined to a hollow core. It
also should not be overstated into "$w_0$ no longer needs measuring": a mode
field diameter still has to be characterised, and
[slepkov2010](slepkov2010.md) is a standing reminder that guided modes have
their own intensity structure to model. The defensible version is that the
measurement moves from a knife-edge on a free-space focus to a mode
characterisation on a fibre, which is a different and more stable problem.

## What the full text settled, and what it did not

Two of the three questions this section used to pose are **answered** from the
thesis reprint (2026-07-31).

**Excitation is two-colour**, as the 9 GHz detuning scale had suggested —
verbatim: "Two lasers, of wavelengths 780 and 776 nm, drove the
5S₁∕₂ → 5D₅∕₂ two-photon transition", an ECDL and a Ti:sapphire. That matters
for what transfers: a two-colour ladder has a residual first-order Doppler term
and an intermediate-state detuning knob that a degenerate 778 nm scheme does
not, so their 9 GHz result is **not** a statement about the degenerate geometry
this campaign runs.

**The geometry is a 45 µm-core kagomé HC-PCF**, 40 cm, at 90 °C — settled, and
it overturned this note's earlier inference (see above).

**The decomposition of the 10 MHz is still not fully in hand.** Transit gives
3–4 MHz and pressure ≈12 kHz; the thesis attributes the remainder to
higher-order transverse mode coupling but, as read so far, does not turn that
into a line in a budget. A published transit/power/collisional budget in a
guided geometry is directly reusable and is exactly what M9 does in free space,
so **extracting it from the thesis is worth a dedicated pass** — the reprint is
held, so this is reading, not fetching. **[OPEN]**
