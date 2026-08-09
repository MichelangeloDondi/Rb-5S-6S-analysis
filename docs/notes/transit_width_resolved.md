# Transit-width tension: RESOLVED — one flux bug, w₀ re-centred 32 → 50 → 64 µm

**Status: RESOLVED 2026-07-13. The beam-measured waist in force is the adopted
64 µm**, taken at v3.0.0 (2026-08-01) from the lineage measurement in the
v3.0.0 block below, which replaces the 50 µm conclusion this note originally
reached. How it got there: the M9 transit MC (`rb5s6s/transit_mc.py`) had
**one** real bug, a missing crossing-flux factor, now fixed. The corrected
transit re-centred the beam-measured waist from 32 µm to **~50 µm** and was
propagated through every fit, and the lineage measurement then moved it again
to 64 µm. An earlier draft of this note claimed the MC had **two** bugs and
inferred **w₀ ≈ 90 µm**, which was wrong by a factor of 2 (see "What the
earlier note got wrong" below) and is retracted.

## The one real bug (flux), and the fix

The signal is a steady-state excitation **rate** = (atom crossing **flux**) ×
(excitation probability per crossing). Lehmann 2021 eq. 6 carries the flux factor
`v` explicitly. The MC sampled transverse speeds from the 2-D Maxwell–Boltzmann
speed density (Rayleigh, ∝ v) and weighted the per-atom amplitude by
`|c_e|² ∝ 1/v²`, but **omitted the flux `v`** — net weight ∝ 1/v, a spurious
log-divergent, n_atoms-dependent cusp that ran the transit **~2× too narrow**.
Adding the one factor of `v` (`transit_mc.py`, `amp *= v_perp`) makes the net
v-power 0 — a **finite** two-sided-exponential peak (the Biraben–Cagnac cusp).

**Validation.** The closed form is `constants.transit_fwhm_from_w0` =
`ln2·v_th/(π w0)`, `v_th=√(2k_BT/m)`. For Lehmann's NNO worked example (m = 44 u,
w₀ = 0.90 mm, 300 K) it returns HWHM 41.3 kHz vs his **41.2 kHz** (0.2%). The
flux-fixed MC reproduces it (40 kHz) and the analytic Rb value (1.87 MHz at 32 µm,
110 °C, transition axis) to <1%. `tests/test_transit_mc.py` locks both anchors.

## Consequence: w₀ ≈ 50 µm, not 90 µm (32 µm disfavoured)

The corrected **bare** transit at the old 32 µm nominal is **1.87 MHz** (110 °C,
transition axis). Convolved with the 3.49 MHz natural Lorentzian this already
gives **5.64 MHz > the observed ~5.25 MHz** line — *before* any laser or
collisional width — so **w₀ = 32 µm is excluded in the thin single-waist
limit**. Over a realistic multi-mm collection column the beam defocuses and the
added transit drops to ~1.6 MHz, which the line alone no longer decisively
excludes (`results/README.md`, `transit_mc.csv`); the ~50 µm prior therefore
rests on the direct waist measurement as much as on the line. Matching the observed width
(with a plausible laser) puts

    w₀ ≈ 45–70 µm  (central ~50 µm, hard floor ~38 µm),

i.e. **~1.5× the old nominal, not ~3×**. `W0_MEASURED_M` is re-centred to 50 µm and
`TRANSIT_FWHM_PLACEHOLDER_MHZ` is now DERIVED from it (≈1.20 MHz at 110 °C).

**Independent corroboration — a direct beam measurement (2026-07-13).** The group's
own 993 nm lineage measured the focused cell beam directly: **Nieddu 2019** (his
Opt. Express paper *and* OIST thesis, "measured to be 128 µm") and the
**Rajasree-KP 2020** OIST thesis both quote a **1/e² beam diameter of 128 µm →
w₀ = 64 µm**, with the same f = 150 mm lens. That measured value lands at the top
of the transit-inferred 45–70 µm band and **independently excludes 32 µm** — the
naive Gaussian estimate assumed a 3 mm input beam diameter clipped by "the EOM
aperture". That attribution is now sourced rather than inferred (2026-08-01,
APPARATUS.md §1.2/§2): no lens or telescope sits between the SolsTiS and the
EOM, the isolator ahead of it (ISOWAVE I-98T-5L, 5 mm clear aperture) is wide
enough not to clip, and the EOM-02-12.5-V's own clear aperture **is** 3 mm per
the manufacturer's specification table, with the experimenter separately
recalling an IR-card observation of clipping there. A recollected clipping
event does not fix how much of the beam was clipped, so the estimate stays a
Gaussian-optics calculation, not a measurement. It is, though, no longer a free
parameter chosen to fit. Two independent routes (the corrected transit physics
and a direct beam-profile
measurement, both below) now converge on **w₀ ≈ 50–64 µm**, above the naive
32 µm estimate.

**Resolved at v3.0.0 (2026-08-01): the prior IS the measurement, 64 µm.**
The note above kept 50 µm because the transit-width match slightly preferred
50–55 and because the 2025 alignment was not guaranteed to match Nieddu's.
Two things settled it. Rajasree's thesis §5.2 turns out to record the same
128 µm diameter on the **same laser model** this campaign used, through the
same f = 150 mm lens, at the same 130 °C, in the same 2f retro geometry, so
the transfer is far better evidenced than a bare citation. And the
three-session Stark bound (M23) lands below the prediction at every data
subset, which is what a lower intensity, meaning a wider waist, produces.
Two documented effects push the *effective* waist above 64 rather than below
it: residual clipping at the sourced 3 mm EOM aperture, and imperfect
superposition of the retro beam. The consequence the old note anticipated
now holds: at 64 µm the observed width **pins σ_laser near 1.1 MHz
laser-axis**, at the edge of the C2 bound, because the transit↔laser
degeneracy collapses once w₀ is fixed. A fixed-lock beam-profile measurement
would measure the 2025 beam directly, and is now confirmatory rather than the
only route to a sane value.

Corroboration also on the *width* itself: Nieddu 2019 fits the same four two-photon
peaks at FWHM 2.43–2.60 MHz on the **laser axis** = ~5 MHz transition axis —
consistent with our archival ~5.25 MHz, and with a locked-laser linewidth of
~100 kHz (vs the drifted 2025 lock).

Cascade on the AC-Stark prediction (S₀ ∝ (1+ρ)/w₀²): the predicted on-axis
shift at 225 mW dropped **1.43 → 0.59 MHz** at the 50 µm re-centring, and
again to **0.35 MHz** at v3.0.0 with w₀ = 64 µm and ρ = 0.94. The M4e width
bound (0.64 MHz, profile likelihood) brackets it; the M23 three-session bound
sits below it, which is the v3.0.0 result.

## What the propagation changed (all re-run 2026-07-13)

The observed total width is data-anchored and unchanged; the correction re-splits
it and re-centres w₀:

| quantity | old (w₀ 32 µm, transit 0.9) | 2026-07-13 (w₀ 50 µm, transit ~1.2) | v3.0.0 (w₀ 64 µm, ρ 0.94) |
|---|---|---|---|
| transit prior (110 °C, bare) | 0.9 MHz | 1.20 MHz | **0.93 MHz** (derived from w₀) |
| σ_laser (linefit, transition, median) | ~2.0 | ~1.3 (0.64 laser axis) | **1.74** (0.87 laser axis) |
| σ_laser(2025) bound (C2, laser axis) | <~1.1 | <~1.0 | **<1.2** (1.09 at the 64 µm point, rising with w₀) |
| β (global fit, central) | ~0.056 | 0.036(4); w₀-band [0.004, 0.055] | **0.0535(43) / 0.0528(47)** (⁸⁵Rb/⁸⁷Rb) |
| β lever probe (+130 °C) | ~0.02 | 0.014; γ_coll rises ×1.85 over ×53 | **0.020/0.022**; γ_coll rises ×1.47 over ×52.5 |
| S₀(225 mW) predicted | 1.43 | 0.59 | **0.35** |
| S₀(225 mW) 95% bound | ~2.0 | 0.63 (M4e profile likelihood) | M23 joint fit, see RESULTS C3f |

The narrower transit hands more of the observed width to σ_laser and, through
the shared density lever, to β: both rows above rose from the 50 µm column
rather than falling, which is the same mechanism methods/07 already documents
for the tied-fit σ_laser(T) values. Neither is a new degeneracy, just this
one moving along the curve the earlier columns already describe.

Every result stays **w₀-conditional and PRELIMINARY**: the transit↔σ_laser
degeneracy means the archival line cannot pin w₀ on its own — the fixed-lock session
a direct beam-profile measurement does. The re-pin corrects the central prior and excludes 32 µm; it is
not a w₀ measurement.

## What the earlier note got wrong (retracted)

The earlier "DIAGNOSED (decisive), w₀ ≈ 90 µm" claim had two errors:
1. It claimed a **second** bug — a laser-vs-transition "factor of 2" in the
   per-atom Gaussian. That was spurious: the MC's `(2π ν_T)²` transition-axis
   convention is correct (δ = 2π ν_T is the transition detuning; the per-atom
   population is `exp(-δ²w²/4v²)`). There is only **one** bug (flux).
2. Consequently it doubled the transit (3.85 instead of 1.87 MHz at 32 µm) and
   inferred w₀ ≈ 90 µm. The note was internally inconsistent by exactly this 2×:
   its own Lehmann-validated HWHM formula `ln2·v_th/(2π w0)` implies FWHM ≈ 1.9,
   not 3.8, at 32 µm. The correct pull is ~1.5× (to ~50 µm), and S₀ ÷2.4 not ÷8.

## Provenance
Numbers: `results/transit_mc.csv` (M9), the re-run fit CSVs, and
`constants.transit_fwhm_from_w0` (Lehmann-validated). Source PDFs are held locally
(untracked). Synthesis in `docs/literature_food_for_thought.md` §1.
