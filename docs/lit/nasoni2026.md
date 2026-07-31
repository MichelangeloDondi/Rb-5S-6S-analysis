---
citekey: nasoni2026
type: misc
authors:
  - Nasoni, Francesco
title: 'Optical Trapping of Cold Atoms with a Hollow-Core Fiber'
journal: "Master's thesis, Universita di Bologna"
volume: null
pages: null
year: 2026
doi: null
arxiv: null
pdf: PDF_papers/theses/TesiLM_Nasoni_2026_Optical Trapping of Cold Atoms with a Hollow-Core Fiber.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'UNPUBLISHED THESIS from the experimenter''s own group -- supervisors
    Minardi and Prevedelli, co-supervisor M. Dondi (the experimenter),
    defended July 2026. It is APPARATUS PROVENANCE, not independent literature.
    Confirm with the experimenter before any published claim rests on it, and
    do not treat it as a citable external source.'
  - 'THE WAIST IT SUPPLIES IS FOR A DIFFERENT BEAM AND A DIFFERENT EXPERIMENT,
    and this must travel with the number. The 17.1 x 19.3 um injection waist is
    the 1064 nm OPTICAL DIPOLE TRAP beam. A hollow-core guided mode depends on
    wavelength, so carrying it to a 778 nm or 993 nm line is an ASSUMPTION.
    Further, per the experimenter (2026-07-31), the apparatus is headed for
    780 nm EIT cooling; two-photon spectroscopy in that fibre is speculative.'
  - 'Read for the injection-waist passage (its section 2.2.2.1) and the
    abstract. The trap-depth model, the loading-efficiency result and the
    fibre-characterisation chapters are NOT read.'
verified_date: 2026-07-31
summary: >
  Bologna master's thesis, 103 pp, on an optical dipole trap for cold 87Rb made
  by coupling 1064 nm into a hollow-core photonic-crystal fibre, with a
  near-field imaging system for alignment; reports a loading efficiency against
  a "non-shallow trap model" and sets up a counter-propagating second beam for
  an optical conveyor belt. Held since 2026-07-18 and given a lit file
  2026-07-31, when it turned out to be the source of a number the repo had
  carried unsourced for weeks: the CRYST3 fibre's "18 um mode field". The
  thesis makes it an INJECTION BEAM WAIST -- a RADIUS, settling a
  radius-vs-diameter question worth a factor of two in every transit estimate
  -- with an 18 um design target, a 13.6 +/- 0.1 um ideal thin-lens value, and
  a MEASURED 17.1 +/- 0.7 um by 19.3 +/- 0.4 um. CONFIRMED BY THE EXPERIMENTER
  2026-07-31: that mode belongs to the 1064 nm TRAPPING laser, the planned next
  step for the apparatus is 780 nm EIT COOLING, and a 778 nm two-photon line in
  the hollow core is a speculative idea for a possible separate paper rather
  than a plan. Transit numbers computed here for a 778 nm probe are answers to
  a hypothetical.
loci:
  - P1
  - P2
section: oist-lineage
---

# nasoni2026

**Held since 2026-07-18; read for the injection-waist passage 2026-07-31.** A
master's thesis from the experimenter's own group at Bologna — supervisors
Francesco Minardi and Marco Prevedelli, co-supervisor Michelangelo Dondi,
defended July 2026. It is filed here as **apparatus provenance**, not as
literature.

## Why it needed a record

The repository carried an "18 µm mode field" for the CRYST³ hollow-core fibre
that entered [saha2010](saha2010.md) in commit 080d2b2 **with no citation**, was
twice mis-attributed to published papers that do not contain it, and left open
whether it was a radius or a diameter — a factor of two in every transit
estimate built on it. This thesis is where it comes from, and it was held all
the while without a note.

## What it actually says

Verbatim, from its injection-setup section:

> "the real waist at the injection is expected to be closer to the target value
> of approximately $\sim$18 µm"

with the ideal thin-lens calculation giving $w_{\rm inj} \simeq 13.6 \pm 0.1$ µm
and an $M^2 = 1.2$ correction giving $\simeq 15.1$ µm. And then it is
**measured**:

> "the beam profile after the injection lens was characterized … yielding
> $w_{\rm inj\text{-}x} = (17.1 \pm 0.7\ \mu m)$, $w_{\rm inj\text{-}y} =
> (19.3 \pm 0.4\ \mu m)$, sufficiently close to the target waist"

slightly elliptical, which the thesis attributes to the AOM compressing the beam
in $y$ and expanding it in $x$.

**So the 18 µm is a RADIUS** — the 3.3 MHz reading was right and the 6.6 MHz
alternative is dead — and it is a target that the measurement bears out.
Through the repo's own `transit_fwhm_from_w0` at 100 °C (CALCULATED):

| $w_0$ | source | transit FWHM |
|---|---|---|
| 13.6 µm | ideal thin-lens | 4.34 MHz |
| 15.1 µm | $M^2 = 1.2$ | 3.90 MHz |
| 17.1 µm | **measured**, $x$ | 3.45 MHz |
| 18.0 µm | design target | 3.28 MHz |
| 19.3 µm | **measured**, $y$ | 3.06 MHz |

## What the fibre is actually for, and it is not this analysis

**Confirmed by the experimenter, 2026-07-31.** The 18 µm is the guided mode of
the **1064 nm trapping laser**. The next step planned for that apparatus is
**780 nm light for EIT cooling**. Running a 778 nm two-photon line in the
hollow core is *an idea for a possible separate paper, and is speculative at
this stage.*

That matters because this repository had drifted into describing the
hollow-core fibre as its own "guided-mode extension", as though a two-photon
spectroscopy campaign there were planned. It is not. The fibre belongs to an
EIT-cooling programme, and the two-photon use of it is one speculative option
among others. Every transit number computed here for a 778 nm probe answers a
hypothetical question, and is labelled as such wherever it appears.

The physical caveat stands on top of that. A hollow-core guided mode is set by
the fibre *at the wavelength in question*, so the 1064 nm trap mode is not the
778 nm or 993 nm probe mode. Even if the speculative experiment happened, 18 µm
would be an assumption about it rather than a measurement of it.

## Other content, not read

The trap-depth ("non-shallow") model, the loading-efficiency result quoted
against an expected $0.41 \pm 0.04$ per cent, the near-field imaging alignment
procedure, and the conveyor-belt plan for a counter-propagating second 1064 nm
beam. If the speculative two-photon use of this fibre is ever pursued, the
loading efficiency and the alignment method are the parts to return to.
