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
pdf: null
held: false
status: REPORTED
routing:
  - CITE
verify_flags:
  - 'REPORTED. The bibliographic record is from Crossref, authoritative for the
    DOI, and confirms the author list, title, volume, page and the 17 January
    2013 date exactly as supplied; the abstract was supplied verbatim by the
    experimenter the same day. The paper itself has not been read and APS
    returns 403 without a subscription.'
  - 'The abstract says absorption was maintained over detunings up to 9 GHz
    "from an intermediate state". A DEGENERATE 778 nm two-photon excitation sits
    of order 1 THz from 5P_3/2, so a 9 GHz detuning scale implies a TWO-COLOUR
    scheme (near 780 + 776 nm) rather than the degenerate one -- but the
    abstract does not say, and this note must not assume it. Settle it from the
    full text before citing the geometry.'
  - 'The hollow-core fibre type and core diameter are not in the abstract. The
    transit arithmetic in the body is therefore an inference about their
    linewidth, not a reading of their paper.'
summary: >
  Two-photon spectroscopy of THERMAL Rb vapour confined in the hollow core of a
  photonic-crystal fibre (Adelaide/Luiten with Benabid): linewidths as narrow as
  10 MHz on 5S1/2 -> 5D5/2, resolving the excited-state hyperfine structure,
  with very strong nonlinear absorption (>90%) observed and "substantial"
  absorption maintained out to 9 GHz of intermediate-state detuning -- two
  separate statements in the abstract, the weaker quantifier attached to the
  detuning range. The high-resolution counterpart to saha2010 in the same
  geometry, and the closest published indication of what confinement COSTS in
  linewidth: 10 MHz is the right order for a transit-limited FEW-MICRON guided
  mode by this repository's own transit formula. The published hollow cores in
  this lineage are TIGHTER still -- Saha's own is a 6 um Crystal Fiber AIR-6-800
  (~28 MHz) and Slepkov's stated 1e-7 cm^2 area is ~1.8 um (~33 MHz) -- so
  Perrella's 10 MHz is if anything better than those geometries predict, and the
  realistic penalty against free space is 15-30x for THOSE fibres. The 18 um
  mode field this note previously credited to saha2010 appears in NO held paper:
  it is the experimenter's own CRYST3 apparatus at Bologna, gives ~3.3 MHz, and
  is an UNSOURCED apparatus fact needing confirmation (radius or diameter?).
loci:
  - M9
  - P2
section: oist-lineage
---

# perrella2013

**REPORTED, 2026-07-30.** Record from Crossref (authoritative for the DOI, and
it confirms every field the experimenter supplied); abstract supplied verbatim by
the experimenter from the publisher listing. Not held, not read — APS returns 403
without a subscription.

**Abstract, verbatim.** "We present two-photon spectroscopy of a thermal rubidium
vapor confined to the hollow core of a photonic-crystal fiber. Linewidths as
narrow as 10 MHz were observed on the 5S₁∕₂→5D₅∕₂ transition enabling the
hyperfine splitting of the excited state to be resolved. Very strong nonlinear
absorption (>90%) was observed, with substantial absorption maintained over large
detunings (9 GHz) from an intermediate state. These attributes make this system
ideal for many frequency metrology and quantum optics applications."

## Where it sits

[saha2010](saha2010.md) is the existence proof — Doppler-free two-photon Rb at
778 nm inside a hollow core, 1% absorption at 1 mW. This is the same geometry
pushed to **high resolution and near-complete absorption**: >90% nonlinear
absorption, and a line narrow enough to resolve 5D₅∕₂ hyperfine structure. Where
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

Their "as narrow as 10 MHz" lands at $w_0 \approx 5$–6 µm, entirely plausible for
a hollow core at 780 nm — so the reported linewidth is *consistent with* being
transit-limited by the guided mode, against this campaign's **1.19 MHz** at the
free-space $w_0 = 50$ µm prior.

**The penalty depends entirely on which fibre, and this note has now been wrong
about it in both directions.** The scaling is $1/w_0$. A first version called it a
flat "factor of ten"; a correction then put the repository's own candidate at
3.3 MHz — a factor of 2.8 — on the strength of an **18 µm mode field** attributed
to [saha2010](saha2010.md) and [slepkov2010](slepkov2010.md). **Both attributions
were wrong** (checked 2026-07-30): neither paper contains an 18 µm figure, and
that number is an apparatus value for a *prospective* collaboration supplied by
the experimenter, not a literature quantity.

The hollow cores actually in this literature are much tighter, and the penalty is
correspondingly much worse (CALCULATED at 100 °C with the repo's own function):

| fibre, as published | mode radius | transit FWHM |
|---|---|---|
| Saha's Crystal Fiber AIR-6-800, **6 µm core** | ~2.1 µm | **28 MHz** |
| Slepkov's stated area $10^{-7}$ cm² | ~1.8 µm | **33 MHz** |
| a 10 µm core (Slepkov's acetylene citation) | ~3.5 µm | **17 MHz** |
| free-space campaign prior | 50 µm | 1.2 MHz |
| *prospective* 18 µm mode field (experimenter, not literature) | 18 µm | *3.3 MHz* |

So Perrella's 10 MHz is, if anything, **better than the published hollow-core
geometries would predict** — it implies a looser mode than Saha's or Slepkov's,
and the penalty across *that literature* is roughly **15–30×**, not 3× and not
10×.

**But the relevant fibre is not one of theirs.** The experimenter's own CRYST³
hollow core (EU H2020 GA 964531, the Bologna apparatus behind their doctoral
work) is quoted at an 18 µm mode field, which gives **3.3 MHz** — a factor of
2.8. So there are two different statements and they must not be run together:
*published* hollow cores in the Rb two-photon literature are tight and cost
15–30×; *this programme's* fibre is much larger and costs about 3×. Perrella
sits between them. **The 18 µm itself is an apparatus fact with no source in
this repository** and needs confirming by the experimenter, including whether it
is a radius or a diameter — as a radius it gives 3.3 MHz, as a diameter
6.6 MHz.

*And the whole comparison is an inference.* The core diameter is not in the
abstract, the vapour temperature in the fibre is not either, and 10 MHz may
include laser width, power broadening or collisional contributions that would
push the implied $w_0$ larger — which would shrink the penalty further. The claim
defended here is only that 10 MHz is the right order for a transit-limited
few-micron mode, not that their line *is* transit-limited.

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

## What to check in the full text

Whether the excitation is degenerate 778 nm or two-colour (see the verify flag —
the 9 GHz detuning scale suggests two-colour, and it changes what transfers);
what the core diameter and mode field radius actually are, which converts the
table above from an inference into a comparison; and how they decompose the
10 MHz, since a published transit/power/collisional budget in a guided geometry
is directly reusable and is exactly what M9 does in free space.
