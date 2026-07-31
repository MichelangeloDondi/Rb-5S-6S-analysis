---
citekey: boustimi2017
type: inproceedings
authors:
  - Boustimi, M.
  - Loulou, M.
  - Natto, S.
  - Belafhal, A.
  - Baudon, J.
title: 'Van der Waals dispersion energy between atoms and nanoparticles'
journal: 'J. Phys.: Conf. Ser.'
volume: 869
pages: 012057
year: 2017
doi: 10.1088/1742-6596/869/1/012057
arxiv: null
pdf: PDF_papers/Boustimi_2017_J._Phys.__Conf._Ser._869_012057.pdf
held: true
status: VERIFIED
routing:
  - FEED
verify_flags:
  - 'Author list COMPLETED 2026-07-31 from the paper''s own title block: M
    Boustimi, M Loulou, S Natto (Umm Al-Qura, Makkah), A Belafhal (Chouaib
    Doukkali, El Jadida) and J Baudon (LPL, Paris 13). Two earlier versions of
    this field were wrong and are recorded so the pattern is visible: the first
    GUESSED "Baudon, J.; Robert, J." from the author''s other work; the second
    took "M Boustimi, M Loulou, S Natto et al." from schmidt2011''s IOP citation
    list and truncated at "et al.". Baudon happens to be real -- which is
    exactly why the guess was not acceptable evidence.'
  - 'Its equations do not survive PDF text extraction (the reflection-coefficient
    and energy expressions come out as mojibake). Everything quoted below is
    from prose; the formulae themselves have NOT been read and must be taken
    from the rendered pages before use.'
verified_date: 2026-07-31
summary: >
  OPEN-ACCESS conference paper by the same author as the paywalled boustimi2002,
  presenting the same susceptibility-tensor framework for van der Waals
  dispersion energy and covering "sphere, cylinder and plane" geometries -- its
  section 2.2 treats an atom near a nanowire explicitly. Held 2026-07-31 as a
  possible free substitute for the METHOD that sague2007 used to compute its own
  van der Waals shift. Carries the same limitation as the 2002 paper: the
  worked nanowire case is METALLIC, with the dispersion coefficients written to
  "carry the nonlocal behavior of the metal". So it supplies the framework, not
  a dielectric result. SUPERSEDED FOR THE REFIT later the same day: frawley2012
  was found to be held, and is cylindrical, dielectric-capable and in a directly
  usable factorised form. Keep this only as an independent cross-check of the
  framework.
loci:
  - P2
section: method-anchors
---

# boustimi2017

**Held and skimmed 2026-07-31**, supplied by the experimenter while chasing the
paywalled [boustimi2002] — which it does not replace, but may make unnecessary.

## Why it matters: what Sagué actually needed from Boustimi

The refit blocked on `boustimi2002` (PRB 65, 155402) on the assumption that a
*number* was needed from it. Re-reading [sague2007](sague2007.md) settles that it
is not. Their words: "**We calculated** the vdW shift, $\delta_{\rm vdW}(r)$, for
the D2 line of Cs near a 500 nm diameter **dielectric cylinder** [15]." Sagué did
the calculation themselves and cite Boustimi for the **method**. The often-noted
objection — that Boustimi's worked case is an argon atom near an *aluminium*
wire, while Sagué's fibre is silica — therefore does not land: nobody imported a
metallic number into a dielectric problem.

## What this paper provides

The same framework, stated for highly symmetric geometries — "sphere, cylinder
and plane" — built on "the susceptibility tensors of the two partners in
interaction" to give a general expression for the dispersive energy. Its §2.2,
"Atom near a metallic nanowire", writes the atom–wire dispersive interaction
(their Eq. 11) as an integral over the wire's reflection coefficient, with
$k_\parallel$ the wave-vector component along the wire axis.

**The limitation is the same as the 2002 paper's, and is explicit**: the
dispersion coefficients "carry the nonlocal behavior of the **metal**". So the
worked expressions are metallic. Whether the reflection coefficient can simply
be evaluated for a dielectric $\varepsilon$ — which is what Sagué must have done
— is **not established here**, and is the thing to check on the rendered pages
before treating this as a drop-in.

## Status for the refit: superseded, later the same day

**This paper is no longer needed, and neither is `boustimi2002`.**
[frawley2012](frawley2012.md) was supplied by the experimenter the same night:
same electrostatic approximation, the right **cylindrical** geometry, and
explicitly **metal *and* dielectric** rather than metal only. It also gives the
answer in the directly usable form $U = -(C_3/x_0^3)\mu$, a flat-surface result
times one position-dependent scalar. That is strictly better than anything this
proceeding offers for the refit.

What this paper is still good for is corroboration — an independent statement of
the same susceptibility-tensor framework across sphere, cylinder and plane, by a
different group, open access. Keep it as a method cross-check, not as an input.

The vdW shift was in any case the *second* input to the Patterson refit. The
first, [klimovducloy2004](klimovducloy2004.md)'s decay rate, turns out to be the
harder one: its closed form is quasistatic and **not valid at either fibre of
interest**.
