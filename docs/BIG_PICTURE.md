# The big picture

*The map of this project. It opens with what each piece buys, then why the
993 nm line is worth characterising at all, what we are trying to do, what
already exists, what the 2025 dataset delivered, and what new measurements
would each add, in the vapour cell or at an optical nanofibre. Everything
quantitative below appears in [`RESULTS.md`](RESULTS.md) with its
provenance.*

## What each piece buys

```
  2025 archive (done)        model + bounds + method, w0-conditional
        │
        ├── beam-profile w0 ───────► every archive bound sharpens (no new physics run)
        │
        ├── fixed-lock cell session ► Δα and β would be measured (if run)
        │         │
        │         └── small waist ──► shape-based readout demonstrated vs the pull
        │
        └── nanofibre session ──────► pushing-dip model + surface shift,
                                      read against the cell reference
```

Each arrow is independently valuable; nothing below the archive is required
for the archive's own results to stand.

---

## 1. Why the line is worth characterising at all

Stated at the size the evidence supports: two of the three items below are
still calculations rather than results. Sections 5 and 6 say what the next
measurements would add.

**An uncharacterised line in a well-motivated class — but not a better clock
line.** The 778 nm 5S→5D two-photon transition is an established optical
frequency reference, and the reason is structural: two-photon Doppler-free
excitation kills the first-order Doppler width without a beam-geometry trick,
so the apparatus is a cell, a laser and a detector. That compactness is the
documented draw of the whole class ([Martin 2018](lit/martin2018.md);
[Newman 2021](lit/newman2021.md)).

993 nm 5S→6S shares that structure. It does **not** share the linewidth
advantage: the 6S₁/₂ upper state lives 45.57 ns
([Gomez 2005](lit/gomez2005.md)), giving the 3.49 MHz natural width every fit
here carries, whereas 5D₅/₂ is far longer-lived: [Bandi 2025](lit/bandi2025.md)
quotes the 5S→5D two-photon working linewidth as **≈330 kHz**, about an order of
magnitude narrower. On natural quality factor alone, 993 nm starts *behind* the
line the compact-clock community already uses — and that
community is at 6×10⁻¹⁴/√τ ([Ahern 2025](lit/ahern2025.md)). Nothing in this
archive suggests 993 nm would overtake it, and this page should not be read as
claiming so.

What is true is narrower and worth stating on its own: the environmental
coefficients of 993 nm have only ever been bounded, and coarsely
([Orson 2021](lit/orson2021.md)'s nulls at ~6 MHz). Those coefficients decide
how well an environment must be controlled for any target stability, so they
are worth knowing for a line nobody has measured them on — and they are the
entry the 5D/7S self-broadening series is missing. That is the case: an
uncharacterised line in a practically-motivated class, not a challenger.

The rungs either side of it are now measured, by one group and one method,
which makes the gap concrete rather than rhetorical. Both drive a
Doppler-free two-photon line in a pure Rb cell and read the cascade
fluorescence, and both infer density from cell temperature rather than
measuring it:

| line | self-broadening | in MHz per 10¹² cm⁻³ | convention |
|---|---|---|---|
| 5S→5D₃/₂ ([Cao 2025](lit/cao2025.md)) | 40 ± 0.54 kHz/mTorr | ≈ 0.0018 | FWHM, stated |
| 5S→7S ([Wang 2025](lit/wang2025.md)) | 0.32 ± 0.01 MHz/mTorr | ≈ 0.014 | not stated |
| **5S→6S, this work** | — | **bound 0.03–0.05** | FWHM |

Converted at 423 K, the temperature both papers use. The 7S paper never says
whether its linewidth is a half width or a full width, so the factor of eight
between the two rungs carries a factor-of-two caveat until someone settles it.

Two things follow. This archive's bound sits 15 to 31 times above the 7S
entry, which is the headroom a bound should have and is not in tension with
anything. And the per-peak *fitted* values here, 0.026 to 0.045, land above
the 7S rung even though 6S is the more compact state. That is independent
support, from outside this archive, for the reading its own lever test already
forces: those fitted widths are a floor, not resolved collisions. Inside the
archive the evidence is that the width rises only ×1.47 across a ×52.5 density
span. The neighbouring rung says the same thing from the other direction.

Worth noting who else is in this space: [Wang 2025](lit/wang2025.md) closes by
proposing 5S→7S as the basis for an optical frequency standard. The 5S→6S line
is not being characterised in an empty field.

**Magic wavelengths would let it be done on trapped atoms.** The awkwardness of
a cell reference is that the atoms are hot, colliding and moving through the
beam — the transit and collisional terms this archive spends its effort
bounding. Trapping fixes that, but a trap normally shifts the very line you
are measuring. A *magic* wavelength does not: both states shift equally, and
the transition frequency is untouched. That is the trick behind lattice
clocks (Sr at 813 nm). M16 computes the **first 5S–6S magic wavelengths** —
≈ 1204 / 1288 / 1340 nm, all trapping (α > 0 for both states) — so the
trapped-atom version of this measurement has candidate wavelengths where
before it had none. The state pair has to be said out loud: Zang *et al.* 2012
report six magic wavelengths between 1200 and 1600 nm for the **6s–5p₁/₂,₃/₂**
pairs of a four-level active clock, two of which (1336 and 1342 nm) bracket the
1339.6 here. They are a different state pair and a different magic condition,
and the crowding is expected: every 6S-involving root in the infrared is
confined between the 5p₁/₂–6s₁/₂ and 5p₃/₂–6s₁/₂ resonances at 1323.88 and
1366.87 nm, a 43 nm window. **ENVELOPE, and scalar only** — which for these states is less of a caveat
than it sounds: the tensor polarizability vanishes identically for $J=1/2$
(triangle rule), so with linear polarization the scalar term is exact, not an
approximation. The residual is the vector term
near the 6S–5P lines need their own treatment before anyone designs a trap,
and none of the three has been measured.

![the polarizability ladder and the magic crossings](../figures/fig9_polarizability_ladder.png)

*Where the magic wavelengths come from: the 5S and 6S dynamic polarizabilities
cross three times between 1200 and 1340 nm, and each crossing is a wavelength
where a trap would hold both states without pulling the 993 nm line.*

Worth one line on where they landed, since it was not designed for: **two of the
three sit inside the telecom O-band** (1260–1360 nm, ITU) — 1287.9 and
1339.6 nm — so a trap at either could in principle be built from datacom-grade
diodes, which are cheap, fibre-coupled by default and available space-qualified.
The caveat is real though: the O-band has no erbium amplifier, so reaching trap
power there is harder than in the C-band. Recorded as an observation about the
numbers, not a design: they remain unvalidated, scalar-only envelopes, and the
band edges are an external convention rather than anything this repo computes.

**The method outlives the line, and the gap it fills is a real one.** In any
structured field the light shift is not one number but a distribution over
where the atoms sit — and because a two-photon signal goes as intensity
*squared*, that distribution has a closed form with a calculable asymmetry
that survives in the line *shape* even when the absolute frequency is
unusable.

What makes this worth saying is how the neighbouring field handles the same
problem. On the 778 nm 5S→5D line the AC-Stark shift is *the* limiting
systematic — [Ahern 2025](lit/ahern2025.md) is explicitly light-shift-limited
at 6×10⁻¹⁴/√τ, and [Bandi 2025](lit/bandi2025.md)'s review states that light-shift
variations "and vapor-cell temperature variations predominantly limit
performance for medium- to long-term averaging", against a field target of
better than 10⁻¹⁵ at a day. Note *both* halves of that pair: the light shift is
what the shape method reads, and the cell-temperature term is the
density-coefficient territory this archive bounds. The effort goes into suppressing it: shift cancellation
([Gerginov 2018](lit/gerginov2018.md)), active power modulation at ×1000
(Yudin 2020; [Andeweg 2026](lit/andeweg2026.md)), magic
wavelengths ([Hamilton 2023](lit/hamilton2023.md)). Every one of those
suppresses the **mean** shift.

![what each observable can and cannot see](../figures/fig10_degeneracy_vs_observable.png)

*The method in one picture: which physical parameters each lineshape
observable responds to. The mean shift, the width and the asymmetry read
different projections of the same shift distribution, which is why nulling
the mean leaves the spread untouched.*

But the mean is not the distribution. [Hamilton 2023](lit/hamilton2023.md)
builds the very same focus-average integral this analysis does and then
collapses it to a single spatially-averaged number — the distribution is set
up and discarded. Nulling a mean leaves the *spread*, and a spread over atoms
does not average away: it dephases them. Whenever atoms are held long enough
for that to matter — an evanescent field around a nanofibre (§5), an optical
lattice, a hollow-core fibre mode — what limits coherence is the width of the
shift distribution, not its centre. This method reads that width from
lineshape, without needing the absolute frequency a drifting or structured
environment takes away.

**The narrower claim, after an adversarial literature audit (2026-07-26).**
An earlier version of this paragraph said the width "is what nobody is
measuring". That is too strong and has been withdrawn: the audit surfaced two
prior treatments that keep the distribution and read an asymmetric line from
it, both pre-2015. [Slepkov 2010](lit/slepkov2010.md) is now read here and
says it plainly: simulating a Lorentzian saturated-absorption peak through a
Gaussian-core guided mode, "the nonuniformity of the core mode is also seen to
broaden and to steepen the line toward higher frequencies", and the measured
shifts are "well fit by the simulated shift of a nonuniform Gaussian-guided
mode" in preference to a flat-top model. And
[Wall 2014](lit/wall2014.md), now read, goes further than the audit reported:
exciting helium Rydberg states in a converging beam, atoms far from the focus
"experience a smaller range of ac Stark shifts, causing the overall signal from
these atoms to 'bunch up' close to the unperturbed transition frequency", while
those near the focus spread out — giving "a spectral line with a maximum close
to the unperturbed transition frequency, and a long tail towards higher
frequencies". That is the density-of-states argument behind a ramp-shaped
weight, and it is **single-colour two-photon**, so even the I² intensity
weighting is not new.

Keeping the distribution rather than its mean is therefore **not** new, and
neither is the I² weighting on its own.

What neither precedent contains — checked in both PDFs rather than inferred —
is a **closed form**. Both reproduce their lineshape by numerical ensemble
averaging over the beam, describe the asymmetry qualitatively, and keep the
frequency axis intact; neither writes an analytic weight with a calculable
asymmetry coefficient, and neither inverts the lineshape to recover the shift.
So what this analysis adds is the conjunction: the **triangular law in closed
form**, its asymmetry calculable rather than simulated, used to recover the
coefficient **when the frequency reference is unusable**. That
is the sentence the paper should claim, and the precedents should be cited up
front rather than discovered by a referee.

The cell is simply where that is cheap to validate, which is why it was built
here first. **What is demonstrated so far is a bound, on one line, in one
geometry** — the claim is that the observable exists and is drift-immune, not
that it has yet beaten anything.

**And one small completion.** Self-broadening coefficients are published for
the 5D and 7S states; 6S is the missing entry. A measured β_self(6S) closes
that series.

**The expected size is now computed rather than borrowed** (M18,
`rb5s6s/vanderwaals.py`). Both 5S and 6S are S states, so there is no resonant
dipole-dipole term and the leading interaction is van der Waals — which means
the coefficient follows from the same matrix elements that produced Δα(993),
continued to imaginary frequency: C₆ = (3/π)∫α_5S(iω)α_6S(iω)dω. That gives
**C₆(5S+6S) ≈ 2.9×10⁴ a.u.**

That absolute value should not be used on its own, and the reason is worth
stating. Run on 7S — the one nS state in Rb with a *measured* self-broadening
rate (Zameroski 2014, 129 ± 11 kHz/mTorr) — the same code returns 4.5 kHz per
10¹² cm⁻³ against a measured 5.4, 17% low. That is close to (a bit past) the
±10–15% the valence-only truncation and the mean-speed approximation explain.
(An earlier version of the code double-applied the HWHM→FWHM conversion,
a double-count in the code that had been reported as "high by 1.7×,"
traced and fixed 2026-08-03, see `docs/PREREGISTRATION_RESULTS.md`
Addendum 23.) The
(C₆/ħ)^0.4 v^0.6 scaling itself is [Lewis 1980](lit/lewis1980.md)'s
(*Phys. Rep.* **58**, 1 (1980)) primary phase-shift derivation for an n=6
potential, specialised from his eq. (4.15)–(4.18). His own quoted ~4%
Lindholm-Foley error bound is for a different comparison (a J=1 excited-state
angular average our S–S pair does not have) and is far too small to be the
17% seen here, so it rules that approximation out as the cause of the
residual gap.

The prefactor is common to 6S and 7S, so it cancels in a ratio regardless of
its absolute accuracy. Using the computed C₆(6S)/C₆(7S) = 0.347 to scale the
*measured* 7S rate gives

**β_self(6S) = 3.5 ± 0.3 kHz per 10¹² cm⁻³**,

an expectation anchored on a measurement of the same observable on the
neighbouring state. The archival bound (0.03–0.05 MHz, the four-point
70/90/110/130 °C construction, 2026-08-02) sits **8–14× above it** -- tighter
than the earlier three-point bound (was 0.2–0.4 MHz, 57–113× above), because
folding the 130 °C point into the headline extends the density lever from
×16.2 to ×52.5 (`scripts/run_beta_self.py`).

The validation matters more than the number: the identical machinery gives
C₆(5S+5S) = 4180 a.u. against the literature Rb₂ value of ~4691 — 11% low, in
the direction and roughly the size the deliberately-dropped core predicts. Read
everything here as ENVELOPE at the 10–15% level. The impact
prefactor is quoted from the pressure-broadening literature rather than derived.

That expectation also has an upper anchor from measurement. [Weller 2011](lit/weller2011.md) measures the Rb **D1**
self-broadening coefficient at β/2π = (0.69 ± 0.04)×10⁻⁷ Hz cm³ — **69 kHz per
10¹² cm⁻³**. D1 is the *resonant* dipole-dipole case, the largest such
mechanism, because its two states are dipole-coupled to each other. 5S–6S
cannot work that way: both states are S, so there is no resonant dipole
coupling and the interaction is van der Waals, which should sit well below
that figure. So 69 kHz is a ceiling the 6S coefficient should fall far
under — consistent with the ~kHz expectation, and it makes the archival bound
(0.03–0.05 MHz, four-point, 2026-08-02) loose by a factor one can now name
rather than guess, tighter by an order of magnitude than the earlier
three-point reading (was 0.2–0.4 MHz). The archive already has the design for
this one; it needs only the higher-density points of §4.

*Status, plainly: 993 nm is not put forward as a better clock line — on
natural linewidth it is worse than the 778 nm standard; the
magic wavelengths are calculated and unvalidated; the method is demonstrated
on this dataset as a bound. What has actually been delivered is in §3.*

## 2. What we would like to do

The rubidium 5S₁/₂ → 6S₁/₂ two-photon transition at 993 nm is a narrow,
Doppler-free line that has been remarkably little studied — the field's
two-photon effort sits almost entirely on the neighbouring 778 nm 5S → 5D
clock line. The long-term goal is to turn 993 nm into a properly
characterised metrological line by measuring the coefficients that couple its
shape and position to the environment:

- the **AC-Stark (light-shift) coefficient** Δα — how the line moves and
  distorts with laser intensity;
- the **collisional self-broadening and self-shift** β — how it responds to
  Rb density, completing the published 5D/7S series with the missing 6S
  entry;
- the **lineshape itself** — natural, transit, laser and light-shift
  contributions, each pinned by an independent handle.

Alongside the coefficients there is a methodological goal that grew out of
this dataset's main defect. In a focused beam the light shift is not one
number but a distribution — zero at the dim edge of the beam, maximal on
axis — and because a two-photon signal scales as intensity *squared*, that
distribution has a closed form (a triangle) with a fixed, calculable
asymmetry. The line's *shape* therefore carries light-shift information that
survives even when the laser's absolute frequency is unusable — a
shape-based, reference-free light-shift readout, insensitive to the lock
drift that prevents centre-based measurements.

## 3. What others have already done

**On this line.** Precision work on 5S–6S is essentially one group: the USAF
Academy measured the absolute frequencies and hyperfine constants ([Orson
2021](lit/orson2021.md), to MHz; [Ayachitula 2024](lit/ayachitula2024.md), to kHz, with a lock stable to <0.5 kHz over
50 minutes). [Orson 2021](lit/orson2021.md) also reports two null results at ~6 MHz resolution —
no observable light shift and no density shift — and computes the
differential polarizability Δα = 1093 a.u. An independent in-repo recompute
(module M16) reproduces that magnitude to ~5% at −1145 a.u. but finds the
opposite sign. Both sides are now verified from the typeset PDFs: Orson states
the convention in words, repeats the value in SI, and works a −0.66 MHz red
shift that this repo's unit chain returns as −0.653 — so the disagreement is
real, not a convention or units artifact — while this work's sign is anchored
to two measurements it does not fit, the static α and the tune-out. And the disagreement is **not symmetric**: reaching Orson's sign would need
the 6S–5P dipole elements ×2.15, which drives the 6S lifetime from 45.4 ns to
9.9 ns against the measured 45.57(17) ns (Gomez 2005) — roughly 210σ. The upward
6S–6P group cannot supply it instead, because at 993 nm the drive sits above
that resonance and those terms are negative by construction. So one side is
anchored to a measured lifetime and the other is not
([THEORY_NOTE §5](THEORY_NOTE.md), which also records a candidate mechanism as
a hypothesis); every archival result here uses |Δα| and is sign-immune. So on this line the *constants* are measured, but
the *environmental coefficients* are only bounded, coarsely.

**In the group.** OIST has its own 993 nm lineage: [Nieddu 2019](lit/nieddu2019.md) demonstrated
the cell line as a frequency reference; [Rajasree 2020](lit/rajasree2020spin.md) excited 5S–6S in cold
atoms through an optical nanofibre's evanescent field (tens of counts per
millisecond — the feasibility number for everything in §5); [Gokhroo 2022](lit/gokhroo2022.md)
drove the same transition on cold atoms around a nanofibre and observed a
two-peak profile — a dip where resonance-scattering pushes atoms out of the
evanescent field — explained at the level of a stated hypothesis, with no
fitted model. A citation audit (2026-07, in `LITERATURE.md`) confirms nobody
has modelled that dip since.

**Method precedents.** The transit lineshape theory is textbook
([Biraben–Cagnac](lit/biraben1979.md); [Lehmann 2021](lit/lehmann2021.md)). Extracting a polarizability from an
asymmetric line has one clear precedent ([Stalnaker 2006](lit/stalnaker2006.md): one-photon,
standing wave, stable reference, numerical model) — so the *idea* of reading
physics from asymmetry is not new; what is open is the two-photon,
closed-form, reference-free version, used *because* no reference is
available. The 778 nm clock community suppresses the light shift actively
and does not use shape information at all — with a good reference the centre
is strictly better, which is precisely why the shape route matters only in
the reference-free regime.

## 4. What the 2025 dataset delivered

The 2025 campaign (297 traces: four hyperfine peaks, 70–130 °C, 25–225 mW)
was taken with a drifting, hand-re-centred lock (MHz-scale line motion
between blocks; the held-lock rate itself is bounded at order 0.02 MHz/min,
`APPARATUS.md` §6). That one fact organises
everything: **absolute centres are lost, line shapes survive**. The analysis
therefore extracts what shapes alone can support, and states everything else
as a bound. Concretely:

- **A validated lineshape model.** Natural (3.49 MHz) ⊗ transit ⊗ laser ⊗
  light-shift ramp reproduces every line at reduced χ² ≈ 1.1. The beam waist
  is **adopted, not measured here**: 64 µm (prior), the value
  [Rajasree 2020](lit/rajasree2020thesis.md) measured on the same laser model,
  the same f = 150 mm lens and the same retro geometry. The 32 µm figure this
  work started from was a Gaussian-optics estimate that cannot account for how
  much of the beam the 3 mm EOM aperture removed, and transit physics excludes
  it. Residual clipping and imperfect retro overlap both push the *effective*
  waist above 64 µm, so the working band is 60–70 µm and ρ = 0.94 ± 0.04.
- **The light-shift bound sits just below its own prediction.** S₀(225 mW)
  < 0.27 MHz (95%, M23: a joint full-profile fit of three sessions, every
  trace with a free centre so the drifting laser costs nothing. The
  earlier 0.15 MHz was basin-inflated and is retracted, preregistration
  addendum 24). The predicted 0.35 MHz at the adopted geometry puts the
  bound **1.3× below it**, equivalently Δα ≲ 842 a.u. against the
  computed ~1100 a.u. The tension is modest, and the most conservative
  data subset (dropping the peak that carries the pilot session) reaches
  the prediction itself. Either the intensity sits slightly lower than
  the adopted geometry implies, or |Δα| is slightly smaller than
  computed. A beam-profile measurement decides which. Twenty-two times
  below Orson's ~6 MHz null, from shape alone.
- **β_self is bounded, and the bound's necessity is demonstrated.** The
  fitted collisional width rises ×1.9 while the density rises ×53 — a
  residual floor, not resolved collisions — so a naive fit's "4–10σ
  detection" would be an artifact. Since 2026-08-02 the headline construction
  folds that same ×52.5-lever 130 °C point into the density-slope fit
  itself (`scripts/run_beta_self.py`; earlier drafts kept it out on a
  "different configuration" reading of the 130 °C power-sweep session that
  did not survive firsthand confirmation the apparatus was unchanged). The
  per-peak bound is
  ≲ 0.03–0.05 MHz per 10¹² cm⁻³ (95%, four-point, dof=2, with the
  low-degrees-of-freedom scatter and the vapour-pressure density scale both
  propagated) -- an order of magnitude tighter than the earlier three-point
  reading (was ≲0.2–0.4 MHz, dof=1). Showing that the two-epoch design was
  *required* is reported as a vapour-cell result.
- **The ramp's power laws hold** (width: no power trend, a null under 3–8%
  block scatter; amplitude: consistent with P²), the
  laser width is bounded (≲1 MHz, consistent with the sub-MHz quote for the
  same laser in [Gokhroo 2022](lit/gokhroo2022.md)), and the drift-immune skew observable is
  derived and bounded; detecting it requires a tighter focus. The premise
  the whole method rests on — that the line *shape* outlives the drift — is now
  **supported by a synthetic closure test**, not only by the timescale argument: between-scan drift is absorbed exactly by the
  per-scan free centres, and a synthetic closure test
  (`tests/test_intrascan_drift.py`) bounds the leftover *within*-scan effect at
  well under a fifth of the statistical error on the recovered asymmetry at the
  archival envelope rate (~MHz/min; the in-campaign bound is ~60×
  lower still) — it reaches order-S₀ only at tens of times the envelope.
- **A reproducible pipeline.** Every number regenerates byte-for-byte from
  the frozen raw data; every CSV row carries a status tag (BOUND / NULL /
  MEASURED / …); the documentation is written to be picked up by whoever
  works on this next.

**What of the method is actually new, stated at the size it will survive.** The
relation the analysis rests on, that the signal-weighted shift distribution goes
as $|s|^{n-1}$, is **not new**. It reduces exactly to Eq. (5.3) of the 1980
review of Delone, Kovarskii, Masalov and Perel'man, checked against the
shipped implementation to
$7\times10^{-12}$, and that review already carries the lineshape as a map of the
shift distribution and the $k$-photon intensity weighting
([delone1980](lit/delone1980.md), and §5 of [LITERATURE.md](LITERATURE.md) for
the full concession).

Three things survive it. Their distribution is the statistics of a fluctuating
field, unknown in advance, so their integral stays formal. In a focused beam it
is fixed by **geometry**, so it closes. That closure gives **analytic cumulants**
on bounded support. And the third of them is a **drift-immune channel**, which is
what makes a dataset with no usable line centres say anything at all.

In summary, the archive turned a drifted-lock
dataset into a validated model, one near-prediction bound, one
demonstrated-necessary bound, and a method — but no coefficients.

## 5. What new vapour-cell measurements would add

A cell session with a stable lock (the laser's locking has since been
improved) would convert the bounds into the first measured environmental
coefficients for this line. None of it is scheduled or agreed; in order of
leverage:

1. **A direct beam-waist measurement** (knife-edge and/or camera profiler)**.** No physics run at all — but w₀
   is the dominant shared systematic every absolute number rides on (transit
   and laser width are degenerate through it), so measuring it retroactively sharpens
   every absolute number in the 2025 archive at once.
2. **Line centre vs power (the "pull").** With centres alive, the
   first-order light shift (−⅔S₀, the strong handle) becomes measurable as
   a *differential* quantity — centre against power within a scan series —
   needing only minutes-scale lock stability. That would be the first
   measured AC-Stark coefficient of the line, and it would validate the
   shape-based method against the same data.
3. **Same-session high-density points (150–170 °C).** Folding the archive's
   own 130 °C point into the headline (2026-08-02) already stretched the
   2025 lever from ×16.2 to ×52.5 and tightened the bound an order of
   magnitude (was 0.2–0.4, now 0.03–0.05 MHz per 10¹² cm⁻³); the case for
   going further is now about reach, not about whether extreme lever points can be
   combined at all. Even at ×52.5 the bound sits only 8–14× above the
   ~3.5 kHz expectation (§1) -- closer than before, but a same-session
   150–170 °C extension is still the cleaner route: it removes the
   cross-epoch calibration step this fold-in relies on, and the higher
   temperatures make the collisional width move by 0.07–0.25 MHz, against a
   ~20 kHz signal in 2025. **The hot points are necessary and not
   sufficient**: measured against the block-to-block width reproducibility
   that actually limits the comparison, they reach only 0.8–2.9σ per block
   (module M17). Interleaving the peaks and logging the power per trace cut
   that floor, and take the same signal to 3.2–11.6σ — so the two halves are
   co-limiting, not a headline and a refinement. Interleaving also fixes a
   second problem: in 2025 temperature ran monotonically down with elapsed
   time, so slow drift and density trends are confounded.
4. **A tighter focus (~16 µm).** S₀ grows ~16× over the archival 64 µm waist (×14 against the planned 60 µm config-L), and the third cumulant grows
   faster still — but not by the naive ×64: the axial average over the
   collection window changes both its size and, if the window is long enough,
   its sign (PLAN §6 #4 — the sign flip is secured by the landscape cathode
   for any plausible magnification; its size still rides on the unmeasured
   lens conjugates).
   The intrinsic asymmetry becomes detectable — turning the drift-immune
   shape readout from a bound into a demonstration, cross-checked against
   the simultaneously measured pull.

Two acquisition changes make those four *trustworthy*, not merely *possible* —
each closes a gap the 2025 archive could only bound around. **Interleaving the four peaks within minutes, with a logged per-scan
timestamp** (absent from the analysed exports; a recovered backup supplied
file timestamps after the fact — the pre-registered audit voided at content
identity, but its labelled post-hoc pass then dated the campaign, and the
dating is what exposed the gap: the four peaks of a dwell were acquired
**54–76 minutes apart**, so the sharing assumption behind the tighter β was
never close-in-time to begin with —
[PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md), [RESULTS.md](RESULTS.md))
turns that assumption from untested into a checked fact; the
HighFinesse wavemeter's own long-term log, running alongside, is an independent
drift diary for free. **Reading the 6S→5P ~1.3 µm cascade**
instead of the reabsorbed 795 nm fluorescence — trapping-free detection,
established on the sibling 5S–5D line ([Hassanin 2023](lit/hassanin2023.md),
[Beard 2024](lit/beard2024.md)) and plausibly feasible with the IR receiver
already on the bench — a New Focus 2153 femtowatt photoreceiver, gain to
2×10¹¹ V/A over DC–750 Hz ([APPARATUS.md](APPARATUS.md) §3) — supports the density and amplitude work at the higher
temperatures item 3 needs. Neither is new physics; both remove a systematic the
archive had to live with.

None of this is scheduled or assigned; the specification ([`PLAN.md`](PLAN.md)) is
written so that any prefix of it can be run, whenever that becomes possible.

## 6. What new nanofibre measurements would add

The evanescent field of an optical nanofibre is, in one sense, the natural
home of the ramp physics: the intensity gradient is steep and exponential,
so the local light-shift distribution is large and strongly shaped, and the
same |s|^(n−1) machinery applies. The group has already demonstrated the
hard part — 5S–6S excitation through the fibre works, in warm operation and
with cold atoms ([Rajasree 2020](lit/rajasree2020spin.md)'s count rates are the existence proof). What
does not exist, anywhere, is a **quantitative near-surface lineshape
program**:

- a fitted model of [Gokhroo 2022](lit/gokhroo2022.md)'s pushing dip (its position, width and
  power dependence), which needs the force/density dynamics *plus* the
  lineshape pieces this repo provides — the ramp is one ingredient, not the
  whole model;
- the atom–surface (Casimir–Polder) shift and distortion that rides on the
  line for atoms within ~100 nm of the glass;
- optionally, distance-resolved spectroscopy in a two-colour trap, where
  the red/blue power ratio tunes the atom–surface distance — ambitious, and
  the per-distance signal budget is an open question.

The cell line of §3–4 is the in-vacuo reference against which every
near-surface effect would be read. That is the connection between
the two halves of the program: the cell work is what makes the nanofibre
lineshapes *interpretable*.
