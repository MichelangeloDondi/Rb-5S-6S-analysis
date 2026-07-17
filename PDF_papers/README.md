# PDF_papers — literature holdings index

Everything in this folder except this README is **gitignored** (copyright: papers,
theses and internal documents are user-provided; only this index is tracked).
Naming convention: `Author_year_what-it-says.pdf`. Claims in intake digests are
**UNVERIFIED input** until a digestion pass checks them against the actual PDF
(house rule: verify the reviewer too).

**Digestion status**: `queued` items are scheduled as repo tasks (one careful
pass per turn); `DONE` items have been folded into `docs/LITERATURE.md` /
`docs/references.bib` / code provenance.

## Core spine (the arguments Paper 1 directly rests on)

| file | citekey | why it matters | digested? |
|---|---|---|---|
| `Biraben_1979_finite-transit-time-two-photon-lineshape.pdf` | biraben1979 | the original Lorentzian ⊗ double-exponential transit line | DONE (transit kernel) |
| `Borde_1976_general-two-photon-Doppler-free-transit-lineshape.pdf` | borde1976 | general treatment; the *C. R. Acad. Sci. B* **282**, 341 two-photon note (scan — we DO hold a copy, contra the intake digest's "not digitized") | DONE (App. B lineage) |
| `Lehmann_2021_transit-time-limited-two-photon-lineshape.pdf` | lehmann2021 | closed-form transit limit; its 41.2 kHz NNO example VALIDATED the 2026-07-13 flux-bug fix (`docs/notes/transit_width_resolved.md`) | DONE |
| `Stalnaker_2006_dynamic-Stark-forbidden-transition-asymmetric-lineshapes.pdf` | stalnaker2006 | AC-Stark lineshape asymmetry prior art; FM/fringe-averaging regime | DONE |
| `Grimm_2000_optical-dipole-traps-AC-Stark-shift-convention.pdf` | grimm2000 | the pinned ⟨E²⟩/light-shift convention | DONE |
| `Zameroski_2014_Rb-5S-5D-7S-pressure-broadening-and-shift.pdf` | zameroski2014 | 7S self-broadening 129 kHz/mTorr ≈ 5 kHz per 10¹² cm⁻³ — the β_self scale anchor | DONE |
| `Gomez_2005_Rb-6S-lifetime-tau-45ns.pdf` | gomez2005 | τ(6S) = 45.57(17) ns — the source of `GAMMA_NAT` (constants.py) | queued (verify digits) |
| `Nieddu_2019_993nm-5S-6S-two-photon-frequency-reference.pdf` | nieddu2019 | the group's 993 nm frequency reference — same channel, 2019 baseline | **DONE (turn A; published OE copy swapped in 2026-07-14, page 6528/DOI now read off the publisher PDF)**: measured beam **1/e² diam 128 µm ⇒ w₀=64 µm** (f=150 mm) — corroborates the w₀ re-pin; 4 peaks FWHM 2.43–2.60 MHz laser-axis ≈5 MHz transition (corroborates our width); laser MBR-110 @ ~100 kHz. **New apparatus facts (2026-07-14 read) — same idea as ours, different implementation:** Nieddu's retro = **concave mirror f=75 mm at 2f from the focus** (self-imaging → ρ≈1 by design); ours = the **lens-based equivalent** (L2 f=150 + flat mirror at the ~1 mm intermediate waist ⇒ time-reversal ⇒ same waist re-formed; MD 2026-07-14). So mode match is by construction in both; ρ<1 only via losses. Detection = **780 + 795 nm together** through an 800 nm short-pass (R636-10) — unlike our 795-only archival stack, so cross-paper amplitude comparisons must not assume the same collection channel; QWP slots before L1 and CM. |
| `Orson_2021_Rb-5S-6S-absolute-hyperfine-isotope-shift.pdf` | orson2021 | **prior art on OUR transition** (USAFA, Knize/Lindsay), J. Phys. B **54** 175001 | **DONE (turn B)**: prior NULLS — "no AC-Stark or light shift at 6 MHz resolution" (power-varied) + "no density shift" over N≥3×10¹¹; isotope shift (87−85) +94(12) MHz. Our bounds refine below their floor. |
| `Ayachitula_2024_Rb-6S-hyperfine-constants-isotope-shift-kHz.pdf` | ayachitula2024 | PRA **110**, 022803 — the kHz A(6S) remeasurement | **DONE (turn B)**: A(6S)=807.355(2)/239.065(2) MHz **swapped into constants.py** (superseded Perez-Galván); iso-shift (85−87) −99.189(3); lock drift <0.5 kHz/50 min (a benchmark for the fixed-lock session) |
| `Rajasree_2020_cold-Rydberg-atoms-near-nanofiber.pdf` | rajasree2020 | group lineage (cold Rydberg @ ONF) | queued (skim) |
| `Rajasree_2020_spin-selection-two-photon-ONF-cold-atoms.pdf` | rajasree2020spin | PRR **2**, 033341 — spin selection in single-frequency two-photon excitation; warm-vapor paraxial AND cold-atom ONF configs on OUR line | **DONE (2026-07-14)**: paraxial rate ∝ **D²** (squared degree of linear polarization; **zero for circular**) — a drift channel candidate for the M10 amplitude wander AND a free a fixed-lock session extinction null-test; ONF config (400 nm waist, SM800-5.6-125, ~30% transmission @993) demonstrates **cold-atom 5S–6S excitation via the evanescent field** at 25–40 counts/ms (Paper-2 route-(b) feasibility evidence); nonparaxial minimum ~13% theory / 25% practice (not extinguishable); Le Kien K=0,1,2 operator decomposition = published in-lineage backing for the M10 scalar-only degeneracy law. |
| `Gokhroo_2022_ONF-two-photon-pushing-density-dip_Paper2-target.pdf` | gokhroo2022 | the Paper-2 target (pushing-dip + ONF lineshapes) | queued |
| `Steck_Rb85_D-line-data.pdf`, `Steck_Rb87_D-line-data.pdf` | steck_rb85 / steck_rb87 | vapor-pressure curve → N(T) (stated ±5% over 298–550 K = the density-axis floor); current revisions (a stale Rb87 rev 1.6 (2003) copy was removed as superseded) | **DONE (turn A)**: `density.py` = Steck/Nesmeyanov liquid-Rb + ideal gas, confirmed vs both theses (Rajasree cites Steck) — no change |

## Expansion set (fetched 2026-07-13 via `literature_intake/download_papers.sh`)

**Cluster A — 778 nm 5S–5D two-photon clock (the sibling; AC-Stark is THEIR dominant systematic too):**

| file | citekey | role |
|---|---|---|
| `Martin_2019_Rb-778nm-two-photon-Stark-shifts-differential-polarizability.pdf` | martin2019 | **KEY** — the direct methodological analog: computes+measures the differential polarizability of a Rb two-photon line; our Δα(993 nm) is the same construction |
| `Gerginov_2018_778nm-active-AC-Stark-cancellation.pdf` | gerginov2018 | prior art for *suppressing* the shift (we *use* it — the Intro contrast) |
| `Newman_2021_compact-778nm-optical-standard.pdf` | newman2021 | state-of-the-art compact standard (application framing) |
| `Martin_2018_compact-778nm-two-photon-clock.pdf` | martin2018 | compact-clock motivation |
| `Callejo_2025_778nm-microcell-clock-stability.pdf` | callejo2025 | recent microcell landscape |
| `Poulin_2002_1556nm-telecom-Rb-778nm-two-photon-frequency-standard.pdf` | poulin2002 | user-added: telecom-band (192.6 THz) standard referenced to the Rb two-photon line |

**Cluster B — 5S–7S sibling:** `Morzynski_2013_Rb-5S-7S-two-photon-absolute-frequency.pdf` (morzynski2013) — kHz 5S–7S; pressure + AC-Stark systematics analysed; digital-lock parallel to our drift problem.

**Cluster E — differential polarizability (sets Δα and the red sign):**

| file | citekey | role |
|---|---|---|
| `Safronova_2006_alkali-frequency-dependent-polarizabilities.pdf` | safronova2006 | dynamic α(ω) for alkalis (matrix elements + Table III α(λ)). **Turn C outcome:** Δα(993 nm) did NOT need a from-scratch recompute — **it was already Orson 2021's published −1093 a.u.** (see below). Safronova remains the *independent-recompute fallback* if a referee pushes. **DONE (turn C).** |
| `Hamilton_2023_Rb-5D-dynamic-polarizability-E1-elements.pdf` | hamilton2023 | measured+calculated Rb two-photon polarizabilities; the rigor template (+ magic-λ idea for §VII). **DONE (turn C, context)** |
| `Martin_2019_...` (see Cluster A) | martin2019 | the METHOD Orson used to compute Δα ("in a manner similar to Martin"). **DONE (turn C)** |

**Group lineage:** `Roy_2017_1033nm-Yb-fiber-laser-frequency-reference.pdf` (roy2017), `Ray_2020_516nm-electric-quadrupole-nanofiber.pdf` (ray2020).

## Second intake (user, 2026-07-13) — broadening / FM / trapping / review

Digested in turn D (folded into `docs/LITERATURE.md` §2 + new §7). A duplicate
Ayachitula copy (`PRA.pdf`) was md5-checked and removed.

| file | citekey | role | digested? |
|---|---|---|---|
| `Sautenkov_2026_self-broadened-lineshapes-optically-saturated-high-density-Rb.pdf` | sautenkov2026 | arXiv:2607.07303 — Rb D2 (5S–5P) **resonance** self-broadening decomposed into static + collision width at N~10¹⁷; the resonance-vs-vdW contrast for why our S→S self term is small | **DONE (D)** [FEED], LITERATURE §2 |
| `Bala_2026_isotopic-effect-collisional-widths-shifts-Hg-clock-by-Rb.pdf` | bala2026 | arXiv:2605.01908 (Toruń/Julienne) — theory of isotope-dependence of collisional widths/shifts (reduced mass + C₆ + scattering length); frames why β₈₅=β₈₇ is EXPECTED | **DONE (D)** [FEED], LITERATURE §2 |
| `Spiegelman-Allard-Kielkopf_2022_collision-satellite-Balmer-beta-wing.pdf` | spiegelman2022 | arXiv:2201.03294 — the Allard–Kielkopf broadening lineage (non-Lorentzian satellites, quasistatic regime) | **DONE (D)** [FEED], LITERATURE §2 |
| `Snadden_1996_FM-two-photon-spectroscopy-mode-locked-laser-cold-Rb.pdf` | snadden1996 | IQEC 1996 — FM two-photon spectroscopy in laser-cooled Rb; a direct EOM-ruler ancestry precedent (§V) | **DONE (D)** [CITE], LITERATURE §7 |
| `Fioretti_1998_radiation-trapping-dense-Cs-MOT.pdf` | fioretti1998 | Opt. Commun. 149, 415 — radiation trapping in a dense Cs MOT; the alkali-cloud trapping anchor for M7/§VI.D (was Tier-2 paywalled, now in hand) | **DONE (D)** [CITE], LITERATURE §7 |
| `Biraben_2019_first-decades-Doppler-free-two-photon-review.pdf` | biraben2019 | C. R. Physique 20, 671 — the pioneer's own retrospective review of Doppler-free two-photon spectroscopy; Intro anchor | **DONE (D)** [CITE], LITERATURE §7 |
| `Amy_2017_two-photon-5S-5D-Rb-in-porous-glass.pdf` | amy2017 | arXiv:1706.04868 — two-photon 5S→5D Rb under confinement (porous glass); landscape | **DONE (D)** [FEED], LITERATURE §7 |

## Latest intake (2026-07-17)

| file | key | why held |
|---|---|---|
| `Pennetta_2026_hybrid-nanofiber-trap-surface-forces-blue-detuned.pdf` | pennetta2026 | *Nature Photonics* DOI 10.1038/s41566-026-01961-9 (arXiv:2509.17767; published PDF held). Rauschenbeutel **hybrid ONF trap** — Casimir–Polder + surface-charge attraction vs blue-detuned repulsion; Cs on a 450 nm fibre; storage 140(9) ms, Ramsey T₂\*=17.8(7) ms. **[FEED]** — nearest-platform for Paper 2: the quantified atom–surface forces `gokhroo2022` lacks, and a real-world demonstration that differential-light-shift dephasing is the guided-atom coherence limiter. `docs/LITERATURE.md` §8. |
| `Pache_2026_gray-molasses-EIT-cooling-nanophotonic-traps.pdf` | pache2026 | arXiv:2605.13387 (same Rauschenbeutel group, 450 nm fibre). **Λ-gray-molasses loading** (6× gain) + **EIT cooling** of Cs in a nanophotonic trap; ~4000 atoms in a 24 µK trap, storage 400(9) ms (5×), a few hundred pW. **[FEED]** — guided-atom source optimisation (the EIT-cooling / Lan-pitch match) and Paper 2's loading/cooling toolkit; again flags the trapping-field differential light shift. `docs/LITERATURE.md` §8. |
| `Beard_2024_two-photon-Rb-clock-776nm-cascade-fluorescence.pdf` | beard2024 | Opt. Express **32**, 7417 (DOI 10.1364/OE.513974; arXiv:2510.09560). First 5S–5D₅/₂ two-photon Rb clock read out on the **776 nm (5D→6P) cascade**. **[CITE]** — cascade-detection precedent for the 1.3 µm trapping-free channel (PLAN §8.4a). `docs/LITERATURE.md` §9. |
| *(not held — cite by DOI)* | hassanin2023 | Hassanin et al., Phys. Rev. A **107**, 043104 (2023). Rb **5S–5D** two-photon via the **5D→5P IR cascade**, "does not suffer from reabsorption" at high density. **[CITE]** — the direct precedent for the 1.3 µm (6S→5P) trapping-free amplitude channel. PDF paywalled (APS), pull if needed. `docs/LITERATURE.md` §9. |
| `Dutta_2025_selective-reflection-CP-thermal-velocity-lineshape.pdf` | dutta2025 | PRA (accepted), arXiv:2507.05925. CP selective-reflection lineshape **with the thermal velocity distribution folded in**. **[CITE]** — the direct template for Paper 2 §IV (surface shift as a thermal-averaged distribution). `docs/LITERATURE.md` §9. |
| `Sargsyan_2025_Cs-6S-7P-nanocell-selective-reflection-surface-shift.pdf` | sargsyan2025 | arXiv:2501.11548. Cs 6S–7P surface shift (C₃) read from a **nanocell** selective-reflection lineshape. **[CITE]** — the experimental analogue for Paper 2 §IV. `docs/LITERATURE.md` §9. |
| `Piotrowski_2026_limits-near-field-probing-nanophotonic-traps.pdf` | piotrowski2026 | arXiv:2605.07798 (Rauschenbeutel group). Probe scattering heats trapped atoms → **near-field probing is transient**. **[CITE]** — a Paper-2 feasibility bound (probe window/power). `docs/LITERATURE.md` §9. |
| `Dutta_2024_higher-order-Casimir-Polder-Rydberg-spectroscopy.pdf` | dutta2024 | PRR, arXiv:2404.13354. Higher-order (quadrupole/octupole) CP corrections for atoms close to a surface. **[FEED]** — close-range background for Paper 2. `docs/LITERATURE.md` §9. |
| `Wang_2025_Rb-5S-7S-multi-channel-cascade-fluorescence.pdf` | wang2025 | Spectrochim. Acta B (Shanxi Univ.). Rb **5S–7S** multi-channel cascade fluorescence (780/741/795/728/420 nm) vs power/pol/T. **[CITE]** — directly on our 7S ladder (741/728 nm = the 7S→5P near-poles) + multi-channel-detection precedent. `docs/LITERATURE.md` §9. |

## Theses & internal materials

| file | what it is | digestion target |
|---|---|---|
| `theses/Nieddu_2019_PhD-thesis_nanofibers-multiphoton-Rb_OIST.pdf` | Thomas Nieddu PhD (OIST 2019, 185 pp) | **DONE (turn A)** for beam geometry: confirms 128 µm 1/e² diam (w₀=64 µm), f=150 mm. Oven/amplitude-baseline chapters still worth a deeper pass if §V/§VI need it |
| `theses/Rajasree-KP_2020_PhD-thesis_Rydberg-multiphoton-cold-Rb-nanofibre_OIST.pdf` | Krishnapriya S. Rajasree PhD (OIST 2020, 149 pp) | **DONE (turn A)**: confirms the 128 µm beam + the Steck N(T) chain |
| `internal/Lab-plan_2025-06-18_two-photon-campaign-one-month.pdf` | the June-2025 campaign design doc (2 pp) | **DONE (turn A)**: a project-management timeline (planned 40–80 °C; campaign actually ran to 130 °C); does NOT specify beam waist/telescope/powers — so it does NOT pin w₀ (the prior rests on Gaussian optics + Nieddu's measurement) |
| `internal/Dondi_2025_research-intern-report.docx` | Michelangelo's intern report | cross-check campaign narrative (skim if a detail is disputed) |
| `internal/NOTE_nieddu-2.5MHz-interpretation_QA_UNVERIFIED.pdf` | a saved Q&A note arguing Nieddu's "2.5 MHz" is reference-stability, not a physical linewidth | **DEBUNKED (turn A)** — the paper fits real two-photon FWHM 2.43–2.60 MHz (laser axis) = ~5 MHz transition, consistent with our data; the note wrongly used the 795 nm D1 detection-photon width as a floor on the resonance width (category error). See DATA.md 2026-07-13. |

## Intake tooling

`literature_intake/` — the 2026-07 literature-expansion bundle:
`LITERATURE_expansion_paper1.md` (the cluster-by-cluster digest with
[CITE]/[FEED] tags and the manuscript-locus map), `MANIFEST.md` (download table +
paywalled-DOI tiers + the Bordé disambiguation), `download_papers.sh` (re-runnable
fetcher; its Biraben URL now returns HTML — harmless, we hold the good HAL copy).
Treat digest claims as input, not fact, until digested. Note: it references a
`Paper1_working_draft.tex` that does NOT exist in this repo (external context).

## Still-missing (paywalled — cite DOI-only, or chase via institutional access)

*(Acquired in the 2026-07-13 second intake, no longer missing: `fioretti1998`,
`biraben2019` review, `snadden1996` FM — and `grynbergcagnac1977` is now well
covered by the Biraben 2019 retrospective.)*

Tier 1: `lewis1980` (Phys. Rep. 58, 1 — collisional-broadening review),
`bjorklund1980` (Opt. Lett. 5, 15 — FM spectroscopy origin), `zapka1983`
(Opt. Lett. 8, 27 — CW Doppler-free two-photon FM in Rb; the Snadden 1996 IQEC
precedent is now in hand as a companion), `holstein1947` (Phys. Rev. 72, 1212 —
radiation trapping; Fioretti 1998 alkali demonstration now in hand).
Tier 2: `allardkielkopf1982`, `bjorkholmliao1976` (clean-intermediate-state
argument), `bjorklund1983`, `edwards2005`, `alcock1984`,
`molischoehry1998` (book). Tier 3 (landscape): perrella2019, douli2024, nez1993,
touahri1997, maurice2020, chui2005, cagnac1985, biraben-cagnac-grynberg1974,
levenson-bloembergen1974.

**Landscape addendum (2026-07-13):** `literature_intake/landscape_2026_drift-immune-Rb-5S6S-and-778nm-frontier.md` — a sibling-chat sweep of the 2024–2026 field (the 993 nm line is un-scooped; the 778 nm 5S–5D clock is the active-AC-Stark frontier). Digested into `docs/LITERATURE.md` §8 and the Ti:Sapph strategy `docs/FUTURE_TRANSITIONS_titsapph.md`.

## Recent-lit intake (2026-07-13, second literature bundle — 6 held + digested)

We re-verified 7 new arXiv IDs and caught two errors (Li dual-interrogation ID,
Drago2026 — quarantined, not fetched). Six fetched + renamed (Bandi2025 is MDPI-OA,
403 on curl — grab from the page). All folded into `LITERATURE.md` §8 + `references.bib`.

| file | citekey | role |
|---|---|---|
| `Andeweg_2026_778nm-active-AC-Stark-power-modulation-NIST.pdf` | andeweg2026 | newest competitor: active ×1000 ac-Stark suppression (778 nm) — the passive-vs-active contrast |
| `Ahern_2025_778nm-5S5D-two-color-clock-stability.pdf` | ahern2025 | two-color 5S–5D, best short-term stability, light-shift-limited |
| `Antypas_2018_lineshape-asymmetry-elimination-Yb.pdf` | antypas2018 | **the asymmetry-ELIMINATION precedent our method inverts** (Budker group) |
| `Safronova_2004_Rb-matrix-elements-lifetimes-polarizabilities.pdf` | safronova2004 | benchmark Rb ns matrix elements + **6S dynamic polarizability** (stronger Δα anchor for 6S) |
| `Chevrollier_2012_radiation-trapping-Levy-flights-review.pdf` | chevrollier2012 | the dedicated radiation-trapping / Lévy-flight review (M7/§VI.D) |
| `Araujo_2021_Levy-flights-photons-He-broadened-hot-Rb.pdf` | araujo2021 | Lévy flights in He-broadened hot Rb — closest to a heated cell |

Bundle updated in `literature_intake/` (download_papers.sh now 27 fetches;
`RECENT_LITERATURE_2023-2026.md` added). Quarantined IDs (do NOT cite): Li
dual-interrogation arXiv (real compensation preprint = 2405.14281); drago2026
(2602.07161, malformed).
