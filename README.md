# Rb 5S→6S two-photon lineshape analysis

[![tests](https://github.com/MichelangeloDondi/Rb-5S-6S-analysis/actions/workflows/tests.yml/badge.svg)](https://github.com/MichelangeloDondi/Rb-5S-6S-analysis/actions/workflows/tests.yml)
[![release](https://img.shields.io/github/v/release/MichelangeloDondi/Rb-5S-6S-analysis)](https://github.com/MichelangeloDondi/Rb-5S-6S-analysis/releases)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **New here? [START_HERE.md](START_HERE.md)** is the short front door: a
> working setup in five minutes, then a reading order that depends on why you
> came. This page is the full account. If the vocabulary is unfamiliar,
> [docs/GLOSSARY.md](docs/GLOSSARY.md) explains the measurement in six
> sentences and then defines every term and symbol used anywhere here.

A physics-based forward-model analysis of the rubidium **5S₁/₂ → 6S₁/₂**
two-photon transition at **993 nm**, from Doppler-free spectroscopy in a hot
vapour cell. The data were taken at OIST in 2025.

The physics is the one that limits cold atoms in structured light. When a
field varies across the atoms that sample it, every atom shifts by a
different amount and the line carries that whole distribution rather than one
number. The same object sets what can be cooled inside a hollow-core fibre,
and for how long it stays coherent, which is the apparatus work this analysis
sits beside (see [About](#about)). A fixed-lock follow-up
session is proposed and specified in [`docs/PLAN.md`](docs/PLAN.md), and the
machinery is written to be pointed at other transitions
([`docs/ADAPTING.md`](docs/ADAPTING.md) names the seams).

> **In one sentence:** when the lock drifts, the position of a line is lost but
> its shape is not, so collisional broadening, laser width and the
> power-dependent light shift are read out of the *shape* as **bounds**, and
> the fixed-lock measurements that would turn each bound into a number are
> specified here.

The scope and the headline numbers, up front. Four hyperfine components, 159 line traces and 105 ruler traces across 70–130 °C and 25–225 mW, three bounds at 95%:
collisional self-broadening β_self below 0.03 to 0.05 MHz per 10¹² cm⁻³ across
the four peaks (holding across the waist band the data allow), the 2025 laser width below 1.2 MHz per photon
at the 64 µm measured waist, and the AC-Stark coefficient
S₀(225 mW) below 0.26 MHz against 0.35 predicted at the measured waist (the
prediction rides the measured waist directly, the bound only weakly, through
its transit kernel).
The full claim ledger, including what is deliberately not claimed, is
[`docs/CLAIMS.md`](docs/CLAIMS.md).

<p align="center">
  <img src="figures/fig0_spectrum.png" width="560" alt="A representative fitted line">
</p>

*One ⁸⁵Rb 5S₁/₂ F=3 → 6S₁/₂ F′=3 line at 130 °C and 225 mW, with the
composite fit and its residuals: total FWHM 5.37 ± 0.03 MHz, reduced χ² 1.09.
This is the raw material everything below is built from. Every width in the
panel is a full width at half maximum, and the fitted ones carry the one-sigma
error of this condition's fit. The two marked fixed are inputs: the natural
width from the measured 6S lifetime, and the transit width computed from the
beam waist, 64 µm, measured on this apparatus lineage in Rajasree's 2020 OIST thesis (128 µm
1/e² diameter on a profiler, same lens, temperature, geometry and laser model,
and a knife-edge scan on this bench would confirm it here). In the lower strip,
σ is each point's own error from the fit's signal-dependent noise model, which
is why the ±1 band is flat here while the raw noise grows with signal.*

**Why this line is worth measuring.** The environmental coefficients of the
993 nm 5S→6S line have only ever been bounded, and coarsely. Those
coefficients set how tightly an environment must be controlled to reach any
given stability, so they are worth knowing for a line nobody has measured them
on. This is not a claim that 993 nm beats the 778 nm 5S→5D reference the
compact-clock community already uses. On natural linewidth it starts behind
it, by about an order of magnitude, and nothing here suggests otherwise
([`docs/BIG_PICTURE.md`](docs/BIG_PICTURE.md) §1).

**What each piece would buy.** A beam-profile measurement of the waist would sharpen
every archival bound with no new physics run. A fixed-lock cell session
would turn the light-shift and collisional bounds into measurements. A
nanofibre session would test the same light-shift law in an evanescent field,
against the cell as its reference. The dependency map is the first thing in
[`docs/BIG_PICTURE.md`](docs/BIG_PICTURE.md).

<p align="center">
  <img src="docs/apparatus/apparatus_schematic.svg" width="700" alt="Bench schematic. The laser output passes through the optical isolator, then a half-wave plate and polarizing beam splitter working in reflection for power control, then the fold mirror onto the cell axis: polarizing filter, half-wave plate, 12.5 MHz EOM and f = 150 mm lens into the tilted Rb cell oven, a second f = 150 mm lens, a flip-in power meter and the flat retro mirror. An f = 18 mm lens and 795 nm filter in a tube on the PMT holder re-image the cascade fluorescence onto the side-on PMT, then a preamplifier and the scope. A fibre runs from the laser head to the wavemeter">
</p>

*The bench, components numbered 1–13 as in the annotated photograph. Every
element is established in [`docs/APPARATUS.md`](docs/APPARATUS.md), which
also carries the dated photographs behind each box.*

**Where to go next:** the big picture (goals, prior art, what each future
measurement adds) → [`docs/BIG_PICTURE.md`](docs/BIG_PICTURE.md) ·
full derivations and statistics → [`docs/methods.md`](docs/methods.md) ·
results table (auto-generated) → [`docs/RESULTS.md`](docs/RESULTS.md) ·
measurement plan → [`docs/PLAN.md`](docs/PLAN.md) ·
prior work → [`docs/LITERATURE.md`](docs/LITERATURE.md) ·
adapting it to your line → [`docs/ADAPTING.md`](docs/ADAPTING.md).

---

## How the measurement works

A 993 nm beam is retro-reflected through a hot Rb cell, and an atom absorbs
one photon from each direction, cancelling the first-order Doppler shift for
every atom at once: the half-GHz thermal smear collapses to a line a few MHz
wide. The surviving second-order term, of order 0.4 kHz here, sits four
orders below the linewidth.

<p align="center">
  <img src="figures/fig13_level_scheme.png" width="760" alt="Left, the 5S to 6S term diagram with the virtual level below 5P. Right, the photographed cavity scan with the four hyperfine components labelled on the up-sweep">
</p>

*Left: two 993 nm photons, one from each direction, drive 5S₁/₂ → 6S₁/₂
through a virtual level that lies below the real 5P₁/₂. The atom returns by
the 6S → 5P → 5S cascade and the bench detects the 795 nm arm. The 780 nm
channel of the same cascade is suppressed by about 50 dB, and the 5P
fine-structure splitting is enlarged in the drawing rather than drawn to scale.
Right: the cavity scan's up-sweep carries the laser across all four hyperfine
components, two per isotope, all F → F, and the down-sweep repeats the same
four mirrored about the ramp apex. Their spike integrals track the
ground-state populations, abundance × (2F+1)/G_iso. Within ⁸⁵Rb that predicts
F = 3 at 7/5 = 1.40 times F = 2, and the digitised record integrates to 1.42
on the up-sweep, 1.34 to 1.42 across integration rules. Between isotopes the
(2F+1) factors sum away and the prediction is the bare abundance ratio, 2.59,
against 2.45 measured. The display compresses the tallest spikes and the whole
down-sweep, so peak heights are not read for ratios. The integration rules and
their caveats are [APPARATUS §6](docs/APPARATUS.md).*

The 6S₁/₂ population is read out through the 795 nm fluorescence of the
6S₁/₂ → 5P₁/₂ → 5S₁/₂ cascade. Four hyperfine components are recorded across
a temperature sweep (70–130 °C at 225 mW, spanning N = 0.56–29 × 10¹² cm⁻³)
and a power sweep (25–225 mW at 130 °C). There are 297 traces in all:
159 composite-line traces and 105 frequency-ruler calibration traces enter
the fits, and the remaining 33 files from the same nights are excluded before
any fit. Those 33 are an aborted first attempt at one power sweep, its
calibration brackets, and four individually excluded shots (one with a
measured defect, one a duplicate save, two held out by pre-registration),
each exclusion with its stated reason in [`docs/DATA.md`](docs/DATA.md).

## Shapes without centres

The 2025 data were taken with a drifting, hand-re-centred lock, with MHz-scale
re-centrings between blocks (a block is one set of back-to-back repeats at a
fixed condition; [APPARATUS §6](docs/APPARATUS.md)). The consequence:

- absolute line **centres are lost** (drift moves them scan to scan), but
- line **shapes are preserved**.

<p align="center">
  <img src="figures/fig15_drift_story.png" width="760" alt="The drift problem photographed, the campaign reconstructed from its own traces, and what each drift regime licenses">
</p>

*The whole constraint. Top: the problem as photographed on a preliminary
session, a wavemeter record of cavity re-locks and relaxations. No frequency log
survives from the campaign itself, which is why the middle panel has to be
reconstructed. Middle: the campaign reconstructed from its own traces. Each
vertical stroke is one trace's own frequency sweep drawn to scale, which is a
sweep extent and not an uncertainty. The oscilloscope window was moved 58 times
and each move re-zeroes the offset axis, so every segment floats and offsets are
comparable only between traces taken at the same scope setting. Only the widths
and shapes of the individual traces carry information. The inset is drawn for
scale rather than as a measurement: the held lock's drift is bounded at order
0.02 MHz/min over three hours and the sign is not established, so both
directions are drawn. Shapes survive, centres do not. Bottom: what each drift
regime licenses, from the 2025 bounds to the fixed-lock session that would
convert them.*

The numbers behind the figure were recovered, not recorded: the exports carry
no acquisition time, and a backup that did was audited under a
pre-registration written before it was opened. The held-lock drift is bounded
at order 0.02 MHz/min on the laser axis (per-photon frequency, half the
transition axis every linewidth here is quoted on), with the sign
undetermined once the scope offsets are accounted for. The megahertz motion
was the hand re-centring after lock dropouts, not the drift. The full trail,
including the retraction of a headline that turned out to be the knob, is in
[`docs/PREREGISTRATION_RESULTS.md`](docs/PREREGISTRATION_RESULTS.md).

What the *shape* of a line carries (widths, power-law scalings, asymmetry) is
therefore reported as bounds, nulls and consistency checks, while
the absolute shifts wait for a stable lock. Each bound sets the sensitivity
target a follow-up session would need to beat. The width-only AC-Stark bound
brackets its prediction rather than resolving it (the predicted effect is
about one block's width scatter, so the bound rests on averaging), while the
joint three-session fit lands below the predicted band, the tension the
results table quotes. The 95% constructions are checked by
injection-recovery ([methods §4.11](docs/methods/06_the_statistics.md)).

The chain from raw trace to quoted bound, each stage a runnable script, each
output a committed CSV:

```mermaid
flowchart LR
    T["297 raw traces"] --> N["measured noise law"]
    T --> K["frequency ruler"]
    N --> F["hierarchical<br/>lineshape fits"]
    K --> F
    F --> W["widths and shapes<br/>vs T, P"]
    W --> D["density lever<br/>β_self bound"]
    W --> P["power lever<br/>S₀ bound"]
    W --> S["ramp asymmetry<br/>upper bound"]
    W --> A["amplitude laws<br/>P² and density<br/>checks"]
    G["guards<br/>model ladder<br/>identifiability<br/>coverage"] -.-> D
    G -.-> P
```

A lever is the spread of conditions a fit uses to pin down a slope: the wider
the temperature or power range, the tighter the bound. The fits are
hierarchical in the plain sense that some parameters are shared across a
peak's traces while others stay free per trace. The dashed **guards** are the
three validation analyses that gate the headline bounds
([methods §4](docs/methods/06_the_statistics.md)):

- **Model ladder.** Every lineshape component must earn its place against
  nested alternatives (ΔBIC), so nothing is over- or under-fitted.
- **Identifiability.** Profile likelihoods establish which parameters the
  data can actually separate. Where transit and laser width are degenerate,
  the bound carries that degeneracy as an explicit band.
- **Coverage.** The quoted 95% intervals are re-run on campaign-like
  synthetic data with known truth, and must cover that truth at the stated
  rate.

The **amplitude checks** are the two-photon rate laws: peak amplitude must
scale as P² at fixed density and linearly with N at fixed power. Both hold
(log-log slopes 1.83–2.12 and 0.85–1.02).

Every scan carries its own frequency ruler: the 12.5 MHz EOM's sideband pairs
excite copies of the line every 12.5 MHz on the transition axis, 6.25 MHz
apart in laser tuning, up to seven per scan. The frequency axis is therefore
self-calibrated per block even as the lock drifts, and the ruler *rate* is a
differential across identical lines, immune to the light shift and to the
lineshape asymmetry ([methods §3](docs/methods/05_the_frequency_ruler.md)):

<p align="center">
  <img src="figures/fig8_ruler.png" width="720" alt="A ruler trace with its seven-tooth comb fit, and the sweep-linearity check, flat to within 0.3 percent in the well-sampled windows">
</p>

*Left: one ruler trace with its seven-tooth comb fit, six teeth standing above
the trace's own fit residual. Why the seventh is below it: at this modulation
depth the third-order pair carries about 2% of the first-order power, and the
scan end clips the outermost window, as on every recorded ruler. This trace is
the one drawn because it meets conditions fixed before the analysis, the
selection rule of
[the ruler specification](docs/notes/ruler_validity_and_trim_prereg.md) §7 and
amendment 4: the two first-order teeth are among the three tallest without
relabelling, six of the seven teeth stand above the scatter of the fit residual
with the weakest at 0.63 of it, and the reduced χ² is 1.01 against a ceiling of
2.0. Seven of the 104 recorded rulers clear every clause. Right: the
sweep-linearity check, local rate against block rate. Sweep non-linearity and
any tooth-dependent pull together stay within 0.3%, and that bound is set by
the well-sampled windows. The open markers at the scan edges carry an
uncertainty larger than the bound itself, so they do not constrain it.*

## Results at a glance

The model these numbers rest on, shown against one representative trace per
line: the global archive fit at its best-fit parameters, residuals below each
panel. The sub-unity reduced χ² reflect the conservative per-block noise
inflation (1.2–2.2×), not an over-fit. The antisymmetric near-centre residual
structure is shot noise (it falls as amplitude^-0.5 on both the power and
temperature axes). One feature remains unattributed: a symmetric centre
excess reaching 1.4% of peak on the brightest line, 3.7σ against the
uninflated errors and absorbed by the inflation. It changes none of the
reported values.

<p align="center">
  <img src="figures/fig16_fit_gallery.png" width="760" alt="Fit-quality gallery: the global archive model over one trace per peak, with residual panels">
</p>

*One panel per component, each the highest-signal repeat of the 225 mW, 130 °C
power sweep. The collisional width, the laser linewidth, the Stark coefficient
and the transit width are common to every campaign trace and held fixed here,
and the fitted Stark coefficient sits at zero, so no Stark broadening is drawn.
Only each trace's own amplitude, centre and background are refit. Each residual
strip divides by that point's own uncertainty. Where a reduced χ² falls below
one, the per-point noise assumed in the fit is conservative and the
uncertainties read off it are upper bounds. The four traces' own fitted widths,
reduced χ² and detector-saturation bounds are printed on the full-page versions,
`figures/fig18_single_*.png`.*

The dominant shared systematic for every absolute number is the beam waist
**w₀** (density scale, model form and block scatter contribute at a lower
level, see RESULTS), so each is reported as a bound together with the
measurement that would lift it.

| Quantity | 2025 result | Type | Lifted by |
|---|---|---|---|
| Collisional self-broadening **β_self** | ≲ 0.03-0.05 MHz per 10¹² cm⁻³ (95% per peak, four-point 70/90/110/130 °C density lever) | bound | partly delivered already by folding the archival 130 °C point into the density lever (2026-08-02). Same-session 150–170 °C points and a lower between-block scatter are still needed for a measurement |
| 2025 laser linewidth **σ_laser** | 1.75–2.15 MHz across the four temperature blocks (transition axis, so 0.88–1.08 MHz per photon). 95% bound 1.2 MHz per photon at the measured waist, rising with w₀ | bound | beam-profile w₀ |
| AC-Stark coefficient **S₀(225 mW)** | < 0.26 MHz (95%, joint three-session profile likelihood at the unscaled 2.706 threshold. Below the 0.35 predicted at the measured waist, see [RESULTS](docs/RESULTS.md)) | bound | fixed lock + tighter focus |
| Power scaling | width: no power trend (3–8% block scatter); amplitude consistent with P² | null + consistency check | — |
| Beam waist **w₀** | 64 µm, measured. Rajasree's 2020 OIST thesis recorded a 128 µm 1/e² diameter on a profiler, through the same 150 mm lens, at 130 °C, in the same retro geometry, on the same laser model. Nieddu 2019 quotes the identical 128 µm on the previous laser | measured (lineage) | a knife-edge scan on this bench would confirm it here |

**The fitted collisional width behaves like a floor, not a measurement.** It
barely grows with density (below), while a real binary-collision width must
grow *linearly*, so β_self is quoted as a bound. A density-independent floor
is also what an unresolved instrumental component would produce, or a fixed
foreign-gas broadening from an undocumented cell fill
([APPARATUS §5](docs/APPARATUS.md) records that the cell's fill history is
not on record).

<p align="center">
  <img src="figures/fig6_gamma_floor.png" width="560" alt="The lever test: the collisional width is a floor">
</p>

*The four components faint, their mean in black. The mean of the four fitted
collisional widths is nearly constant: it rises by a factor 1.47 while the Rb
density rises by a factor 52.5. A binary-collision width would be proportional
to density, so these data bound the coefficient rather than measure it, and the
bound depends on which density range is used. The two straight lines are that
comparison drawn: each is what the width would do if the coefficient took the
value fitted over the range named beside it, not a fit to the points. The
dashed one reaches 1.9 MHz at the highest density shown, where the mean of the
four peaks is 0.59 MHz. The density axis is logarithmic and carries a
20 per cent scale systematic from the vapour-pressure model, common to every
point, so it slides the whole abscissa rather than scattering it.*

**The power sweep bears out the ramp's power-law predictions.** At fixed
temperature only the AC-Stark shift varies with power, and both predictions
hold: the linewidth stays flat (the shift broadens the line only as S₀²,
negligible here) and the amplitude follows the two-photon rate law, ∝ P².
These are *consistent with* the light-shift model, not proof of it. A flat
width is equally what zero shift would give, and the ramp's *distinctive*
signature, the skew ∝ S₀³, is below detection in the archive (a bound). The
coefficient itself waits for a fixed-lock session. The S₀ bound and its
prediction are independent by construction: the bound uses only the
width-vs-power data (no w₀ enters), while the predicted 0.35 MHz is the
computed polarizability at the measured w₀, with the retro
ratio ρ=0.94±0.04 (its in-situ measurement is a fixed-lock-session task),
fixed before the fit and never an input to it.

<p align="center">
  <img src="figures/fig2_power_sweep.png" width="720" alt="Power sweep: width flat, amplitude proportional to P squared">
</p>

*(a) the width shows no trend with power. The point-to-point scatter is 3 to
8 per cent, above the 2 per cent or less a light-shift gradient alone would
predict, and the rest of it is scatter between measurement blocks. (b) the
amplitude, with the square-of-power rate law drawn as a reference of fixed
slope: each dashed line has only its offset fitted to its own component, so it
is a reference and not a fit to the points. Widths here are measured directly
off each trace, which runs below the fitted total width of the joint
per-condition fit in fig10, and the two are not read against each other.*

## The lineshape, mechanism by mechanism

The measured line is a convolution (⊗) of independent broadening mechanisms:

$$I(\nu) = A\left[ L_{\Gamma_\mathrm{nat}+\gamma_\mathrm{coll}} \otimes G_{\sigma_\mathrm{laser}} \otimes K_\mathrm{transit} \otimes R_{S_0} \right] + \text{background}$$

| Mechanism | Physical origin | FWHM (transition axis) | Shape |
|---|---|---|---|
| Natural width **Γ_nat** | finite 6S lifetime | 3.49 MHz (fixed, known) | Lorentzian |
| Collisional **γ_coll** | Rb–Rb collisions | 0.19–0.93 MHz across the 32 fitted conditions | Lorentzian (adds to natural) |
| Laser **σ_laser** | laser frequency jitter | 1.75–2.15 MHz across temperature blocks | Gaussian |
| Transit | finite time an atom spends in the beam | ~0.93 MHz at w₀ ≈ 64 µm | cusp kernel (Biraben–Cagnac / Lehmann) |
| AC-Stark **R(S₀)** | intensity-dependent light shift across the focus | ~0.35 MHz at 225 mW | triangular "ramp" |

Every width in the table is a FWHM. σ_laser names the Gaussian laser kernel's
FWHM, already doubled for the two photons. The background is flat over the
scan window: the same-beam absorption pedestal is about a GHz wide, so it
enters as a constant.

The AC-Stark **ramp** is what the rest of the analysis is built on: because
the beam is focused, the light shift runs from zero at the dim edge to a
maximum S₀ on the bright axis, and for a two-photon (intensity-squared)
signal that distribution is a closed-form triangle. Its skew is a
light-shift readout that survives a drifting lock. The derivation is in
[`docs/methods/03_the_ac_stark_ramp.md`](docs/methods/03_the_ac_stark_ramp.md)
and [`docs/THEORY_NOTE.md`](docs/THEORY_NOTE.md).

## The dominant systematic: the beam waist w₀

The transit width and the laser width both depend on the beam waist, and the
archive cannot separate them: a tighter waist means more transit broadening
and less room for laser width, and vice versa. The observed ≈ 5.3 MHz line is
reproduced anywhere from w₀ ≈ 38 µm (the hard floor, where the laser width
goes to zero) upward, and the data alone set no ceiling. The 64 µm working
value comes from two direct profile measurements on the same-lineage
beamline (Nieddu 2019, and Rajasree's 2020 OIST thesis), not from a fit. Only a direct
beam-profile measurement (a knife-edge scan, a camera profiler, or both)
collapses the degeneracy. Every absolute number above is w₀-conditional, and
the beam profile is the first thing a proposed fixed-lock session would fix.
What each assumption moves, quantity by quantity, is tabulated live from the
result CSVs in [`docs/RESULTS.md`](docs/RESULTS.md) ("Sensitivity at a
glance").

<p align="center">
  <img src="figures/fig3_transit_mc.png" width="560" alt="Line width versus beam waist: the transit/laser degeneracy">
</p>

*Transit-time broadening grows as the beam narrows, because a faster crossing
gives a larger frequency spread. The shaded region is excluded: waists below
about 40 µm would already put the transit and natural widths together above the
observed total. The laser and collisional contributions are not in the curve, so
the true waist is higher still. The waist itself has not been measured. The
knife-edge scan is pending, and until it runs this axis is a hypothesis being
scanned rather than a measured quantity. The excluded region is drawn at the
interpolated crossing, and 40 µm is that crossing rounded to the spacing of the
two sampled waists that bracket it.*

## What a follow-up session would add

- **A proposed fixed-lock session.** A stable lock would return the absolute
  centres, and a direct beam-profile measurement would pin w₀, turning the
  bounds above into the first measured 5S–6S AC-Stark and collisional self-shift
  coefficients. With power capped at 225 mW, the intensity axis would come
  from the waist instead: a telescope gives two working waists spanning a
  ×16 intensity range. Points at 150–170 °C in the same session would give
  β_self a density lever without borrowing a temperature point from another
  epoch. The archive's own 130 °C point already stretches the lever to
  ×52.5, but reach alone is not enough while the between-block scatter is
  co-limiting. Full specification: [`docs/PLAN.md`](docs/PLAN.md) §8.
- **Optical nanofibre.** The same ramp law tested in the evanescent field at
  a fibre surface, where an atom–surface potential and the "pushing dip"
  (Gokhroo et al., 2022) ride on the lineshape.

## Calculated quantities

Three numbers in this archive are computed, not measured, and they sit
here rather than in the results table so the table stays a record of
what the data itself established.

| quantity | value and status | provenance | what would settle it |
|---|---|---|---|
| Differential polarizability **Δα(993 nm)** | recomputed −1145 a.u.; \|Δα\| within ~5% of Orson 2021's 1093 but opposite sign. Orson's side is verified from the typeset PDF (convention stated in words, value repeated in SI, his own worked −0.66 MHz reproduced here at −0.653), so the disagreement is real rather than a units artifact ([THEORY_NOTE §5](docs/THEORY_NOTE.md)); this work's sign is anchored to the measured static α and tune-out | calculated | external sign adjudication |
| First **5S–6S magic wavelengths** (scalar) | ≈ 1203.9 / 1287.9 / 1339.6 nm, a trap there would hold both states without pulling the 993 nm line. The 1204 nm crossing sits on the smooth part of the curve and is the practical one, and the other two lie hard against 6S→nP resonances, where trap-photon scattering is high. No published values found to the depth searched (2026-07-17) | calculated (envelope) | a trapped-atom experiment (the corrections a design needs are the row below) |
| **Trap-design corrections** at the crossings | at 1203.9 nm the fourth-order differential shift is +0.87 Hz per megahertz squared of trap depth, the vector shift on a stretched state is 280 kHz per megahertz of depth per unit circularity of the trap light, and those two terms together with trap-photon scattering disqualify every other crossing ([rb5s6s/hyperpolarizability.py](rb5s6s/hyperpolarizability.py)) | calculated, to within a factor of two | a trapped-atom measurement of shift against depth and polarization |

The second row, drawn. The lower panel shows why the crossings exist
where they do: the flat 5S polarizability threads the 6S curve's
nearby resonances.

<p align="center">
  <img src="figures/fig17_magic_wavelengths.png" width="760" alt="Magic wavelengths: the differential scalar polarizability crossing zero at 1204, 1288 and 1340 nm">
</p>

*A magic wavelength is where the differential light shift between two states
vanishes, so a trap held there shifts both equally and does not move the
transition. Here that is Rb 5S₁/₂–6S₁/₂, the 993 nm line. Scalar only, which is
exact for J = 1/2 under linear polarization. The bracket printed under each
crossing is the range over which that crossing moves when the contributing
matrix elements are varied over their quoted uncertainties: ±0.84 nm at the
widest and ±0.065 nm at the tightest, so the three are not one uncertainty and
no single status word covers them. What is unpublished, to the depth searched,
is the calculation behind them, and that is a different thing from what the
brackets measure. In the lower panel the 5S polarizability varies slowly here
because the D lines are far away, while the 6S polarizability diverges at each
nearby 6S→nP resonance, and that contrast is why the crossings fall where they
do. Both panels are truncated at ±2500 a.u. The grey dotted line marks a
further crossing, at 1297.53 nm, which is not one of the three reported values:
the search that produced those stepped over a guard strip on each side of every
resonance, and this crossing falls inside such a strip. A crossing is a sign
change of the difference, and no rule puts one in every gap between resonances,
because the 6S→5P transitions run downward and their resonances carry the
opposite sign. Of the five gaps drawn here, two change sign end to end, and four
crossings fall in the window. A crossing this close to a resonance is unusable
as a trap and is exactly what a null measurement of the matrix element wants,
which the planning documents take up.*

## Reproduce

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q                 # fast test suite (~2 min)
pytest -q --runslow       # full suite incl. high-statistics closure tests (what CI runs)
```

The dataset's manifest is committed
([`data_raw/MANIFEST.csv`](data_raw/MANIFEST.csv)). The 297 raw traces are
held privately, and **On the raw traces**, below, says exactly what that
leaves runnable from a clone (the certification suite and the
clock-dependent results, which is the bulk of the battery). With the traces
in place, each stage reads the previous stages' output in `results/`:

```bash
bash scripts/run_all.sh   # every stage in dependency order, then the figures,
                          # docs/RESULTS.md, and the CSV status column
```

Re-running any stage reproduces its committed CSV in `results/` within the
tolerance `scripts/verify_results_fresh.py` states, and to the printed digit
in the environment [`results/ENVIRONMENT_OF_RECORD.md`](results/ENVIRONMENT_OF_RECORD.md)
records. One committed number sits outside `run_all.sh`, the joint
three-session AC-Stark bound, which needs the raw rehearsal and pilot trees.
The lock-drift measurement and its audit trail go the other way and reproduce
from a clone with no raw traces at all, off the committed acquisition clock.
[`docs/REPRODUCING.md`](docs/REPRODUCING.md) says which script writes what,
and how each quoted number is held to the file that produces it.

## Repository map

```
rb5s6s/     the library: ingest, quality control, noise model, frequency ruler,
            lineshape + fitting, density, collisional/global/AC-Stark fits,
            transit Monte-Carlo, amplitude analyses, shared utilities
scripts/    one runnable per analysis stage, plus make_figures / make_results_ledger
examples/   your_line.ipynb, the pipeline pointed at a different line by
            editing one dictionary
data_raw/   MANIFEST.csv, the frozen 2025 dataset's index (the 297 traces
            themselves are held privately, see On the raw traces)
data_recovered/  the backup-recovered layer: the acquisition clock
            (CLOCK.csv), backup-only discards, degradation lineage
results/    the committed output CSVs (the documented run)
figures/    publication figures produced by make_figures.py
tests/      full test battery, run by CI on the minimum and latest numpy
docs/       the documentation tree, indexed by its own README. Read first:
            CLAIMS.md (the claim ledger) · BIG_PICTURE.md (goals, prior art,
            what each future measurement would add) · methods/ (8 ordered
            chapters, the full derivations)
private/    local working folder, excluded by .gitignore and enforced by
            tests/test_repo_hygiene.py
```

## Conventions

- **Transition-frequency axis everywhere** — the two-photon sum frequency, i.e.
  twice the laser frequency. Per-photon quantities carry a `_LASER` suffix in code.
- **Every number carries a provenance tag** (measured here / calculated /
  established / open); the same tags drive the machine-readable `status`
  column on every results CSV.
- **Physics constants and analysis choices are separated** (`constants.py` vs
  `config.py`); repeat counts are read from `MANIFEST.csv` rather than
  inferred from filenames, and data-quality cuts are fixed before fitting
  rather than chosen afterward.

## About

I am Michelangelo Dondi, a PhD candidate in experimental cold-atom physics at
the University of Bologna, on the EU project CRYST³. My work there is the
transport and cooling of cold ⁸⁷Rb atoms inside hollow-core photonic-crystal
fibres, where the light shifts of the guided mode vary across the atoms and
set what can be cooled and how long it stays coherent. This repository looks
at the same physics through a different observable: the shape a two-photon
line takes when a focused standing wave shifts each atom differently.

The dataset is from a six-month research visit to OIST in 2025, an
independent project alongside my work there on atom-nanofibre interfaces.
The analysis was written after the campaign.

Contact: michelangelo.dondi@unibo.it ·
[ORCID 0009-0006-9050-2881](https://orcid.org/0009-0006-9050-2881) ·
citation metadata in [`CITATION.cff`](CITATION.cff) · MIT license.

**On the raw traces.** This repository ships the analysis, the committed
results, the figures, and the dataset's manifest
([`data_raw/MANIFEST.csv`](data_raw/MANIFEST.csv) — every trace's filename,
condition, role and MD5), but **not the 297 raw traces themselves**. They were
taken at OIST and are held privately; they are available on request
(michelangelo.dondi@unibo.it). What that means concretely:

- **Everything that certifies the analysis runs here.** The injection-recovery
  closures, the coverage study and minimum-detectable-effect, the transit-kernel
  asymptotics, the identifiability and model-comparison machinery — all of it is
  synthetic and needs no archive. That is the bulk of the suite.
- **The clock-dependent results also reproduce from a clone**, because the
  acquisition clock is committed as
  [`data_recovered/CLOCK.csv`](data_recovered/CLOCK.csv) (hashes → timestamps,
  not measurement data).
- **What cannot run here** is the raw→results pipeline itself, and the four
  tests that re-hash the traces against the manifest; those skip with a stated
  reason rather than failing. With the traces in place they all run, and each
  stage reproduces its committed CSV within the stated tolerance (the
  `run_all.sh` command under **Reproduce**).

**Adapting it to your own line.** The analysis is a library with its
physics, apparatus, and statistics kept behind separate seams.
[docs/ADAPTING.md](docs/ADAPTING.md) names them for anyone pointing the
machinery at a different transition, species, or light geometry, and
[examples/your_line.ipynb](examples/your_line.ipynb) lets you try it on
your own line by editing one dictionary. Neither needs the raw traces.
