---
citekey: camparo1992b
type: article
authors:
  - Camparo, J. C.
  - Klimcak, C. M.
title: 'Resonance shift due to correlated amplitude and frequency variations'
journal: Opt. Commun.
volume: 91
pages: 343
year: 1992
doi: 10.1016/0030-4018(92)90357-W
arxiv: null
pdf: PDF_papers/Camparo-Klimcak_1992_resonance-shift-correlated-AM-FM-fluctuations.pdf
held: true
status: VERIFIED
routing: []
verify_flags: []
verified_date: 2026-07-29
summary: >
  Companion to Camparo & Lambropoulos 1992: a resonance SHIFT arising purely
  from CORRELATED amplitude and frequency fluctuations of the driving field.
  Correlated AM/FM noise makes the field's own spectrum asymmetric, and the
  measured line -- the convolution of that spectrum with the atomic response --
  shifts and skews with no atomic physics involved. Independent of the ac Stark
  effect. A laser-noise mechanism that can fake a line asymmetry, distinct from
  the shift-distribution skew of camparo1992.
loci:
  - THEORY
section: prior-art
---

# camparo1992b

**Read from the held PDF.** Opt. Commun.
**91**, 343 (1992), received February 1992, the same year and group as
[Camparo & Lambropoulos](camparo1992.md), and a distinct mechanism.

**The mechanism.** A field with **correlated** amplitude and frequency
fluctuations has an asymmetric spectrum of its own. The measured resonance is
the convolution of that field spectrum with the atomic response, so the line
centre shifts — and the profile skews — with no atomic physics involved at
all. The paper states it plainly: the shift "is independent of any ac Stark
or Bloch–Siegert effect."

**Why this earns an entry rather than a footnote.** The asymmetry programme
here reads atomic physics out of a line's shape. That inference admits two
laser-noise counterfeits, and they are different:

1. *Uncorrelated* intensity noise sampled slowly — the
   [Camparo & Lambropoulos](camparo1992.md) skew, bounded in these data
   through the noise model's multiplicative term (BIC selects it in 1 of 32
   conditions, and there negative, an artifact);
2. **Correlated AM/FM noise** — this paper. A diode laser's amplitude and
   frequency fluctuations are generically correlated (the same injection
   current drives both), so the mechanism is not exotic, and the M1 bound on
   multiplicative *variance* does not address it: the counterfeit lives in
   the field's spectral asymmetry, not in the signal's noise floor.

For the archival results nothing changes — the committed asymmetry channel is
a bound, and the C3c skew is identified as shot noise. But any future claim
of a *detected* ramp asymmetry (the fixed-lock session's purpose) must
exclude this channel explicitly: the natural discriminator is that the ramp
skew scales as P³ through S₀ while a field-spectrum asymmetry does not scale
with optical power at the atoms, and the geometric sign flip
(methods §2.6) is immune to it entirely — a field-spectrum artifact cannot
know the beam waist.
