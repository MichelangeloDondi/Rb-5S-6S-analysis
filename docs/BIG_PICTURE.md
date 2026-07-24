# The big picture

*Where this project sits: what we are trying to do, what already exists, what
the 2025 dataset delivered, and what new measurements — in the vapour cell or
at an optical nanofibre — would each add. Everything quantitative below is in
[`RESULTS.md`](RESULTS.md) with its provenance; this page is the map.*

---

## 1. What we would like to do

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
survives even when the laser's absolute frequency is unusable. A shape-based,
reference-free light-shift readout is worth establishing in its own right:
it is insensitive to the lock drift that prevents centre-based
measurements.

## 2. What others have already done

**On this line.** Precision work on 5S–6S is essentially one group: the USAF
Academy measured the absolute frequencies and hyperfine constants ([Orson
2021](lit/orson2021.md), to MHz; [Ayachitula 2024](lit/ayachitula2024.md), to kHz, with a lock stable to <0.5 kHz over
50 minutes). [Orson 2021](lit/orson2021.md) also reports two null results at ~6 MHz resolution —
no observable light shift and no density shift — and computes the
differential polarizability Δα = 1093 a.u. that our own convention
reproduces to the digit. So on this line the *constants* are measured, but
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

## 3. What the 2025 dataset delivered

The 2025 campaign (297 traces: four hyperfine peaks, 70–130 °C, 25–225 mW)
was taken with a drifting, hand-re-centred lock (MHz-scale line motion
between blocks; the held-lock rate itself measures ~0.02 MHz/min,
`APPARATUS.md` §6). That one fact organises
everything: **absolute centres are lost, line shapes survive**. The analysis
therefore extracts what shapes alone can support, and states everything else
as a bound. Concretely:

- **A validated lineshape model.** Natural (3.49 MHz) ⊗ transit ⊗ laser ⊗
  light-shift ramp reproduces every line at reduced χ² ≈ 1.1, with the beam
  waist re-derived (~50 µm; the 32 µm nominal is excluded by transit physics.
  [Nieddu 2019](lit/nieddu2019.md) measured 64 µm directly on the same-lineage
  apparatus — independent support for excluding 32 µm, and the same order as
  our value, though not the same number and not the same beam).
- **The light-shift bound sits at the prediction.** S₀(225 mW) < 0.63 MHz
  (95%), against a predicted 0.59 MHz — equivalently Δα ≲ 1200 a.u. against
  the computed 1093. This is an order of magnitude below Orson's ~6 MHz
  null, from shape alone, with a drifting laser.
- **β_self is bounded, and the bound's necessity is demonstrated.** The
  fitted collisional width rises ×1.9 while the density rises ×53 — a
  residual floor, not resolved collisions — so a naive fit's "4–10σ
  detection" would be an artifact. The per-peak bound is
  ≲ 0.2–0.4 MHz per 10¹² cm⁻³ (95%, with the low-degrees-of-freedom scatter
  and the vapour-pressure density scale both propagated). Showing that the
  two-epoch design was *required* is reported as a Paper-1 result.
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
  archival envelope rate (~MHz/min; the measured in-campaign rate is ~60×
  lower still) — it reaches order-S₀ only at tens of times the envelope.
- **A reproducible pipeline.** Every number regenerates byte-for-byte from
  the frozen raw data; every CSV row carries a status tag (BOUND / NULL /
  MEASURED / …); the documentation is written to be picked up by whoever
  works on this next.

In summary: *the archive turned a drifted-lock
dataset into a validated model, one near-prediction bound, one
demonstrated-necessary bound, and a method — but no coefficients.*

## 4. What new vapour-cell measurements would add

A cell session with a stable lock (the laser's locking has since been
improved) would convert the bounds into the first measured environmental
coefficients for this line. None of it is scheduled or agreed; in order of
leverage:

1. **A direct beam-waist measurement** (knife-edge and/or camera profiler)**.** No physics run at all — but w₀
   is the one systematic every absolute number rides on (transit and laser
   width are degenerate through it). Measuring it retroactively sharpens
   the entire 2025 archive. Worth doing even if nothing else happens.
2. **Line centre vs power (the "pull").** With centres alive, the
   first-order light shift (−⅔S₀, the strong handle) becomes measurable as
   a *differential* quantity — centre against power within a scan series —
   needing only minutes-scale lock stability. That would be the first
   measured AC-Stark coefficient of the line, and it would validate the
   shape-based method against the same data.
3. **Same-session high-density points (150–170 °C).** The 2025 sweep's
   density lever was too short for the expected ~kHz-scale β; the higher
   temperatures make the collisional width move by 0.07–0.25 MHz — enough
   to measure β_self (or bound it near expectation), completing the 5D/7S
   series. Same-session matters: the 2025 data show cross-session drifts
   masquerade as density trends.
4. **A tighter focus (~16 µm).** S₀ grows ~14×, and the third cumulant grows
   faster still — but not by the naive ×64: the axial average over the
   collection window changes both its size and, if the window is long enough,
   its sign (PLAN §8.3 #4, contingent on the unmeasured collection geometry).
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

None of this is scheduled or assigned; the specification (`PLAN.md` §8) is
written so that any prefix of it can be run, whenever that becomes possible.

## 5. What new nanofibre measurements would add

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

## 6. How the pieces depend on each other

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
