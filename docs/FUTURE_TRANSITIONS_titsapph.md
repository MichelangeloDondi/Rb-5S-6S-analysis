# Exploiting the tunable Ti:Sapph — future transitions and the papers they enable

**Status: strategy / food-for-thought (2026-07-13).** Not a plan of record. The
premise (recorded 2026-07-13): the drive laser is a **tunable Ti:Sapphire**, so a new
measurement session is not locked to 993 nm — it can reach *other* Rb two-photon
transitions, "as long as we can reach the frequency and the optics is fine at the
next frequency." This note maps what that buys us, grounded in the 2024–2026
landscape (`PDF_papers/literature_intake/landscape_2026_...md`).

## 1. The one-sentence strategic picture

Our current line (5S→6S, 993 nm) is **little studied and not currently pursued elsewhere** — the only
active group (USAFA/Knize: Ayachitula 2024, and the earlier McLaughlin 5S–6S work)
reports *null* AC-Stark and density shifts at ~6 MHz resolution — so it is the
clean **demonstrator** of the drift-immune method. The **far more actively worked line is one
transition over**, at 778 nm 5S→5D, where 2024–2026 clock work (NIST/Andeweg,
Adelaide/Ahern, Feng, FEMTO-ST/Callejo, Gerginov, Li–Dou) suppresses the AC-Stark
shift **entirely with *active* schemes** (power modulation, dual interrogation,
two-color, magic-wavelength locking). **Nobody uses a passive lineshape-asymmetry
observable there.** A tunable Ti:Sapph lets us carry our reference-free method onto
that hot transition — so wavelength scans across the magic point become the measurement.

## 2. The transition menu the Ti:Sapph opens (verified)

Two-photon from 5S₁/₂; wavelength = 2×10⁷ / E_upper[cm⁻¹]. "Intermediate detuning"
= how far the virtual one-photon level sits from the nearest real 5P (the physics
that sets how much a near-resonant intermediate distorts the two-photon lineshape,
Bjorkholm–Liao 1976). **Reachability is set by the installed SolsTiS optics set, not
a single continuous range** — see the laser-specific §below; the M-Squared datasheet
lists discrete sets 670–710 / 725–875 / 725–975 / 700–1000 / 950–1050 nm (custom
<700 or >1000 on enquiry), each ≤300 nm wide.

| upper | 2-photon λ | intermediate Δ | character | detection | SolsTiS optics set | competition |
|---|---|---|---|---|---|---|
| **5D₅/₂** | **778 nm** | **1.1 THz** | **near-resonant** (5P₃/₂) | 420 nm (6P→5S) | 725–875 / 725–975 / **700–1000** | **hot** (clock frontier) |
| **7S₁/₂** | **760 nm** | 10 THz | intermediate | 420 nm (6P→5S) | 725–875 / 725–975 / **700–1000** | light (Morzyński, Chui) |
| 8S₁/₂ | 697 nm | 46 THz | ~clean | 420 nm (6P→5S) | **670–710 only** (blue set) | none |
| 9S₁/₂ | 660 nm | 70 THz | clean | 420 nm (6P→5S) | custom <700 nm | none |
| **6S₁/₂** | **993 nm** | 75 THz | **clean** | 795 nm (5P₁/₂→5S) | **700–1000** (edge) or 950–1050 ← *current* | none (us + USAFA) |
| 4D_J | 1033 nm | 87 THz | clean | (5D→…) | 950–1050 / custom >1000 | 4D_J clock (2024) |

The blunt consequence: **no single set covers everything.** The pivotal question is
which set is in *your* SolsTiS. If it is **700–1000 nm**, then 6S (993, near the red
edge), 5D (778) and 7S (760) are all reachable with **the same optics** — the whole
near-IR program needs no laser-optics swap, only the 420 nm detection change. If it
is **950–1050 nm**, 993 and 4D (1033) are easy but 5D/7S require an optics-set swap.
8S needs the dedicated 670–710 blue set; 9S (660) and any >1000 work are custom.

### Your laser (M-Squared SolsTiS + Coherent Verdi V18 @ 18.5 A)

- **Pump is not the limiter — the optics set is.** The Verdi V18 delivers up to
  **18 W at 532 nm** (datasheet-confirmed). Whether 18.5 A is your full-power point
  or a set-point, that is a *generous* pump for a SolsTiS (which needs far less), so
  tuning range is fixed by the installed BRF/mirror set, not by pump. Ample pump is
  exactly what buys usable power at a set's *edges* — which is how you reach 993 nm
  at the top of a 700–1000 set, and what the large-S₀ regime Paper A needs.
- **Tuning mechanism** (why "within a set it's continuous"): motorized
  birefringent filter (coarse, spans the whole set) + a 320 GHz-FSR etalon +
  cavity PZT (fine) — continuous within the set, no realignment.
- **Two things to check on the actual unit** (they decide the whole plan):
  1. **Which optics set is installed** — read the config label / M-Squared sheet,
     or just tune to the bluest and reddest points it will lase. If the blue end
     reaches ≲780 nm, 5D/7S are same-set (only a detection swap); if it starts at
     ~950 nm, 5D/7S need an optics-set change (M-Squared swap, non-trivial).
  2. **Output power at 760–778 nm vs at 993 nm.** A 700–1000 set gives *more* power
     mid-band (760–778) than at the 993 edge — good news: the 5D/7S work would run
     with *more* S₀ headroom than the current 6S work, which is what the asymmetry
     signal (∝S₀³) needs.
- You already reach **993 nm** with this pump, so your set reaches at least to 993
  (consistent with 700–1000 or 950–1050); running the V18 near max at 18.5 A is
  consistent with holding that red edge.

Three things fall out. (i) **5D and 7S sit in the Ti:Sapph sweet spot** (more power,
easier lock than the 993 nm red edge). (ii) **The whole upper ladder shares ONE
detection channel** — 420 nm (6P→5S blue fluorescence) serves 5D, 7S, 8S *and* 9S,
because they all cascade through 6P; only 6S is the near-IR (795 nm) outlier. So
the detection swap noted above (the 795 nm filters → a 420 nm bandpass + a
blue-sensitive PMT) is a **prerequisite for every upper-ladder transition**, and one
swap serves all four (see §Detection below). (iii) The intermediate
detuning now spans **~68×** across a five-rung ladder 5D→7S→8S→9S→6S (1 → 75 THz) —
a controlled sweep of intermediate-state admixture in one apparatus (§Paper C).

### Detection — how much does changing the 795 nm filters help?

A lot, but as an **enabler rather than an optimisation**. The 6S work detects the
6S→5P→5S cascade at **795/780 nm** (near-IR). Every *upper* transition (5D, 7S, 8S,
9S) instead cascades **through 6P**, emitting **420 nm** (6P→5S, blue) — a channel
the current near-IR path does not pass. So:

- To see *any* of the upper-ladder transitions at all, the detection filters must
  change to a **420 nm bandpass** (plus a PMT/APD with useful blue quantum
  efficiency — many near-IR-optimised detectors are poor at 420 nm). This is a
  hard requirement; it cannot be trimmed or optimised around.
- The payoff is broad: **one 420 nm path serves 5D, 7S, 8S and 9S together** (all
  via 6P→5S), so a single detection upgrade unlocks the whole upper program.
- Caveat on signal: the 420 nm branching ratio is favourable for 5D and 7S but
  **dilutes for 8S/9S** (more open decay channels), compounding their blue-edge
  Ti:Sapph disadvantage — so 5D/7S are the high-yield targets, 8S/9S the reach.
- Practical check first: confirm whether the present 795 nm optics are a *bandpass
  that passes the signal* or a *notch that rejects the 993 nm pump* — the former is
  swapped for a 420 nm bandpass; the latter (pump rejection) still needs a new
  pump-blocking edge at 760–778 nm. Both are routine, but they are different parts.

- **A note for the 6S line itself: a trapping-free 1.3 µm option.** The 6S cascade's
  *first* step, 6S→5P, emits at **1.32/1.37 µm** — and unlike the 780/795 nm D-line
  photons (ground-resonant, hence radiation-trapped in the dense cell), the 1.3 µm
  photon is resonant with nothing populated and escapes freely. Detecting it (an
  **InGaAs** detector — single-photon sensitivity below a Si PMT, plus hot-cell
  IR-background filtering) is a **trapping-free** amplitude channel, and the
  **795-vs-1.3 µm ratio discriminates a real degeneracy-law/amplitude deviation from
  a radiation-trapping artifact** (`PLAN.md` §8.4a). The IR-cascade-to-beat-trapping
  trick is established on the sibling line — Hassanin et al. 2023 (5D→5P) and Beard
  et al. 2024 (5D→6P, 776 nm) — so it is proven, not speculative. Orthogonal to the
  420 nm upper-ladder swap — this is a 6S-detection refinement, not an enabler.

Net: the filter swap is required once to reach the upper ladder, and it is a
*cheap, one-time* price (one blue detection path) for a *large* payoff (four new
transitions, including the hot 5D clock line).

## 3. The papers this enables (ranked)

### Paper A — *Reference-free light shift & magic wavelength on the 778 nm 5S→5D clock line, via lineshape asymmetry* — **the topical extension (methodological, not a precision competitor)**

> **Caveat up front (2026-07-13).** This is a *reference-free, orthogonal-
> systematics, no-extra-hardware* determination — a complementary cross-check and a
> clean demonstration of the inverted-nuisance idea. It will **not** out-precision the
> active schemes (NIST/Adelaide), and must not claim to. Its value is method + physics,
> not a smaller error bar. The shape handles are weak (width ∝S₀², skew ∝S₀³) and the
> skew is contamination-prone (shot noise, instrument asymmetry), so it needs the
> *large-S₀* small-waist regime to be a measurement at all — see the scope note in
> `PAPER1_SKELETON.md` §I. That inherits a further dependency: at small waist the
> ramp skew is itself conditional on the axial collection geometry, which is
> unmeasured — the axial average can suppress it or reverse its sign
> (PLAN §8.3 #4). So this proposal is gated on the same collection-profile
> measurement, not only on reaching small waist. The reason "nobody does this" is not an oversight: with a
> stable reference the pull (∝S₀) is strictly better, so the passive shape route is
> preferable only where reference-freedom or orthogonal systematics are required.

- **Why now.** 5S→5D at 778 nm is *the* vapor-cell two-photon clock transition, and
  the 2024–2026 leaders (Andeweg 2026 ×1000 power-modulation suppression; Ahern 2025
  two-color 6×10⁻¹⁴/√τ; Feng 2026; Gerginov 2018; Li–Dou 2024) all fight the AC-Stark
  shift with **active** methods. Our drift-immune **ramp/asymmetry** channel is a
  *passive, reference-free, low-complexity* alternative — a real methodological
  differentiator on a maximally topical transition (Bandi 2025 is the review to cite
  for the benchmark landscape).
- **The measurement the tunability enables.** The ramp asymmetry (third-moment/skew observable)
  scales as S₀ ∝ Δα(λ). Hamilton 2023 puts a **magic wavelength at 776.179 nm**, right
  beside the transition. Tune the Ti:Sapph across it and the asymmetry **crosses zero
  and flips sign** as Δα→0 — a **passive determination of the magic wavelength /
  differential-polarizability zero-crossing**, with no reference cavity and no active
  feedback. That would be a reference-free determination of the differential-polarizability zero crossing.
- **Magic wavelengths for our own 5S–6S pair now exist as computed candidates**
  (M16, `results/polarizability.csv`; unpublished elsewhere to the depth searched
  2026-07-17): α₅S = α₆S crossings at **≈1203.9 nm** (the clean one, far from every
  6S resonance; α ≈ +547 a.u., trapping both states; 16–84% band ±0.8 nm),
  ≈1287.9 nm and ≈1339.6 nm (both wedged near the 6S–7P / between the 6S–5P lines,
  where vector shifts need their own treatment). A trap at the 1203.9 nm crossing
  would hold atoms without perturbing the 993 nm line — the state-insensitive-trap
  ingredient for any trapped-atom version of this spectroscopy, and a small
  original result in its own right. Scalar only; a vector/tensor treatment and a
  blue-side crossing search are the follow-up.
- **Novelty (three claims).** (i) The *inversion* of lineshape asymmetry from
  nuisance-to-eliminate (Wieman 1987; Antypas–Budker 2018) into a self-calibrating
  observable, realized on a *focused* two-photon transition; (ii) magic-λ from an
  asymmetry sign-flip; (iii) reference-free complement to the active-suppression
  mainstream. The literature sweep found no passive-asymmetry light-shift measurement on any
  focused two-photon line, and none on 5D.
- **Feasibility flags (to decide at the bench).** 778 nm is easy for the Ti:Sapph. BUT: (a)
  detection moves to 420 nm (filter + blue PMT); (b) the **near-resonant 5P₃/₂
  intermediate (1 THz)** distorts the two-photon lineshape — the transit/ramp model
  needs the Bjorkholm–Liao intermediate-state term (this is exactly Paper C, so it
  reduces the risk on A); (c) verify the EOM/retro/waveplates behave at 778 vs 993 nm.

### Paper C — *The near-resonant intermediate state and the two-photon transit/AC-Stark lineshape: a clean-vs-resonant comparison (6S, 7S, 5D)* — **the engine-room companion to A**

- The intermediate-detuning **ladder** — 6S (75 THz, clean) → 9S (70) → 8S (46) →
  7S (10) → 5D (1 THz, near-resonant) — is a controlled **five-rung, ~68× sweep**
  of intermediate-state admixture **in one apparatus, one method** (8S/9S added
  2026-07-13; they are blue-edge/short-wave-optics reach but fill the gap
  between the clean 6S anchor and the resonant 5D). Walk it with the Ti:Sapph.
- Test Bjorkholm–Liao 1976 + our transit (Lehmann/Biraben) + ramp model: *how* the
  near-resonant intermediate reshapes the line and the intensity-shift ramp, and
  *where* the clean-case approximation (validated at 6S) breaks.
- This is the intermediate-state correction Paper A needs at 5D — so it can be the
  methods §of A, or a short standalone that A leans on. Either way it converts the
  993 nm work from "one transition" into "the clean anchor of a validated model."

### Paper B — *Self-broadening and drift-immune differential polarizability across the Rb 5S→nS/nD ladder (6S, 7S, 5D)* — **series / completeness (a strong thesis capstone)**

- Same rig, Ti:Sapph tuned to 993/760/778 nm: measure β_self, transit(w₀), and the
  drift-immune Δα for each upper state with **one** method.
- **Completes a real series.** Zameroski 2014 measured *foreign-gas* broadening of
  5D & 7S; Weber–Niemax the nS/nD self-broadening series; we add **self** rates +
  the drift-immune AC-Stark Δα(n), tested against the n-scaling (β ∝ C₆^{2/5},
  C₆ ~ n*⁷) and the Safronova matrix elements. We find **no modern 6S dynamic
  polarizability at 993 nm exists** — a gap this fills.
- Feasibility: β_self is ~kHz at 6S (needs the fixed-lock session high-T, same-session shot-list
  upgrade already in PLAN §8.4); 5D/7S sit closer to resonance so *may* broaden more
  and be easier. Lower risk than A, lower ceiling.

## 4. Recommendation & sequencing

*A proposal for discussion, not a decided roadmap: none of the sessions or
papers below is scheduled, agreed, or assigned. The ordering is what the
physics argues for if the programme is pursued at all.*

1. **Finish Paper 1 (993 nm 5S→6S)** as the clean method demonstrator — and reframe
   its Intro: the *passive, reference-free inversion* of Wieman/Antypas,
   explicitly contrasted with the active 778 nm suppression schemes, on a line no other group is currently working
   transition (quote the USAFA nulls). (This is a `PAPER1_SKELETON` Intro edit — cheap,
   do it in the Paper-1 pass; the refs are in `LITERATURE.md` §8.)
2. **Paper A + C together** are the high-impact next step: carry the method to the
   778 nm clock line and turn the Ti:Sapph tunability into a magic-wavelength /
   Δα(λ) measurement, with the intermediate-state lineshape (C) as the validated
   bridge from the clean 6S anchor. This is where the tunable laser pays off most.
3. **Paper B** is the completeness capstone / thesis chapter — attractive because it
   reuses the exact rig and method across the ladder.

**The most distinctive experiment the Ti:Sapph enables** (distinctive, not
necessarily most precise): scanning the 776 nm magic wavelength on 5S→5D and watching
the ramp asymmetry flip sign — a reference-free magic-wavelength determination, on the
most actively worked transition, by a method those groups do not use. Its systematics
are orthogonal and it needs no active hardware, and it needs the large-S₀
small-waist regime to work at all (§Paper A caveat). A safer thesis bet, lower ceiling
but lower risk, is **Paper B** (the β_self / Δα ladder) — it reuses the exact rig and
method, so it is unlikely to be duplicated.

## 5. Open feasibility questions for the experimenter (Michelangelo)
- Ti:Sapph output power and lock quality at 760–778 nm vs the 993 nm red edge?
- Is the 420 nm detection path (filter + blue-sensitive PMT) available, or a build?
- Do the EOM (ruler), retro-mirror coatings, and waveplates cover 778 nm as well as
  993 nm, or need swaps? (The intensity-anchor / retro-ratio ρ must be re-characterised
  per wavelength.)
- Cell/oven: 5D/7S may want *lower* density than 6S (they are stronger / closer to
  resonance) — the fixed-lock session shot-list temperature range would differ per transition.

*References for §3 are collected in `docs/LITERATURE.md` §8 (2024–2026 landscape).
Source landscape doc: `PDF_papers/literature_intake/landscape_2026_drift-immune-Rb-5S6S-and-778nm-frontier.md`.*
