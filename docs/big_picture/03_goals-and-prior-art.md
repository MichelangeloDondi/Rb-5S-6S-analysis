*Chapter 3 of 9 of [the big picture](../BIG_PICTURE.md)*

## 2. What we would like to do

The rubidium 5S₁/₂ → 6S₁/₂ two-photon transition at 993 nm is a narrow,
Doppler-free line that has been remarkably little studied. The field's
two-photon work sits almost entirely on the neighbouring 778 nm 5S → 5D
clock line. The long-term goal is to turn 993 nm into a properly
characterised metrological line by measuring the coefficients that couple its
shape and position to the environment:

- the **AC-Stark (light-shift) coefficient** Δα, how the line moves and
  distorts with laser intensity
- the **collisional self-broadening and self-shift** β, how it responds to
  Rb density, completing the published 5D/7S series with the missing 6S
  entry
- the **lineshape itself**, natural, transit, laser and light-shift
  contributions, each pinned by an independent handle.

Alongside the coefficients there is a methodological goal that grew out of
this dataset's main defect: a shape-based, reference-free light-shift readout,
insensitive to the lock drift that prevents centre-based measurements. §1.3
gives the method and §4 states what of it is new.

## 3. What others have already done

**On this line.** Precision work on 5S–6S is essentially one group: the usaf
Academy measured the absolute frequencies and hyperfine constants ([Orson
2021](../lit/orson2021.md) to MHz, [Ayachitula 2024](../lit/ayachitula2024.md) to kHz, with a lock stable to <0.5 kHz over
50 minutes). [Orson 2021](../lit/orson2021.md) also reports two null results at ~6 MHz resolution,
no observable light shift and no density shift, and computes the
differential polarizability Δα = 1093 a.u. An independent in-repo recompute
(`rb5s6s/polarizability.py`) reproduces that magnitude to ~5% at −1145 a.u. but finds the
opposite sign. Both sides are now verified from the typeset PDFs: Orson states
the convention in words, repeats the value in SI, and works a −0.66 MHz red
shift that this repo's unit chain returns as −0.653, so the disagreement is
real rather than a convention or units artifact, while this work's sign is anchored
to two measurements it does not fit, the static α and the tune-out. And the disagreement is **not symmetric**: reaching Orson's sign would need
the 6S–5P dipole elements ×2.15, which drives the 6S lifetime from 45.4 ns to
9.9 ns against the measured 45.57(17) ns (Gomez 2005), roughly 210σ. The upward
6S–6P group cannot supply it instead, because at 993 nm the drive sits above
that resonance and those terms are negative by construction. So one side is
anchored to a measured lifetime and the other is not
([THEORY_NOTE §5](../THEORY_NOTE.md), which also records a candidate mechanism as
a hypothesis). Every result reported here uses |Δα| and is sign-immune. So on
this line the *constants* are measured, but
the *environmental coefficients* are only bounded, coarsely.

**In the group.** OIST has its own 993 nm lineage. [Nieddu 2019](../lit/nieddu2019.md) demonstrated
the cell line as a frequency reference. [Rajasree 2020](../lit/rajasree2020spin.md) excited 5S–6S in cold
atoms through an optical nanofibre's evanescent field (tens of counts per
millisecond, the feasibility number for everything in §6). [Gokhroo 2022](../lit/gokhroo2022.md)
drove the same transition on cold atoms around a nanofibre and observed a
two-peak profile, a dip where resonance-scattering pushes atoms out of the
evanescent field, explained at the level of a stated hypothesis, with no
fitted model. A citation audit (2026-07, in `LITERATURE.md`) confirms nobody
has modelled that dip since.

**Method precedents.** The transit lineshape theory is textbook
([Biraben–Cagnac](../lit/biraben1979.md), [Lehmann 2021](../lit/lehmann2021.md)). Extracting a polarizability from an
asymmetric line has one clear precedent ([Stalnaker 2006](../lit/stalnaker2006.md): one-photon,
standing wave, stable reference, numerical model). So the *idea* of reading
physics from asymmetry is not new, and neither is the two-photon case of it.
[Wall 2014](../lit/wall2014.md) is single-colour two-photon, so the I² weighting
is present there too. [Lee 2010](../lit/lee2010.md) is not an adjacent geometry
but the same experiment in Cs, a two-photon nS→n'S alkali line in a hot vapour
cell, Doppler-free with a retro-reflected beam and cascade-fluorescence
detection, with the intensity-dependent broadening already attributed to the
transverse profile. That phenomenon is theirs, sixteen years ago, and no
wording here should imply otherwise. The closed form is not new either, being
Delone's Eq. (5.3) evaluated for the intensity distribution of a focused
Gaussian beam ([delone1980](../lit/delone1980.md)). What is open is what §4
states and no more: the evaluation for the geometry that actually occurs, its
cumulants in closed form, and the third cumulant used as a measurement channel
*because* no reference is available. The 778 nm clock community suppresses the light shift actively
and does not use shape information at all. With a good reference the centre
is strictly better, which is precisely why the shape route matters only in
the reference-free regime.

---

*[The method and its limits](02_the-method-and-its-limits.md) · [What the 2025 dataset delivered](04_what-2025-delivered.md)*
