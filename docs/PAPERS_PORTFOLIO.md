# Paper portfolio — what we can write under each scenario

**Status: planning / decision aid (2026-07-13).** Refines `PAPER1_SKELETON.md` §0.
Beyond the archive, the publishable output depends on two *independent* future
measurement sessions — **neither scheduled, agreed, nor assigned to anyone**. This
doc maps papers → scenarios so the writing plan degrades gracefully if either or
both never happen (which is the branch to plan against, not the exception). Honest
throughout: the archive delivers **bounds + a validated method**, not coefficients
(see `PAPER1_SKELETON.md` §I) — the measurements need a session.

## The three inputs

1. **The 2025 archive** — in hand, fully analysed. Delivers the drift-immune *method*
   + *bounds* (β_self, σ_laser, S₀ AC-Stark) + the systematics catalogue + the
   transit/w₀ physics. This is the fixed asset; everything else is contingent.
2. **A fixed-lock cell session** (specified in `PLAN.md` §8) — knife-edge w₀, a
   *stable* lock (line centres come back), same-session high-T (150–170 °C) and
   power up to ~1 W. Turns the archival **brackets into measurements**. *May* extend to
   the Ti:Sapph 5D/7S lines (`FUTURE_TRANSITIONS_titsapph.md`) if the optics set +
   420 nm detection allow. **Neither scheduled nor tied to one operator:** §8 is
   written as a specification, so whoever has the cell and the beam time can run it,
   in whole or in part, whenever suits.
3. **ONF measurements** (the Gokhroo/Le Kien/Nic Chormaic pushing-dip + ONF
   lineshapes — `gokhroo2022`). A separate session feeding Paper 2.

**What is contingent, and on whom.** The archive is the only asset in hand. Both
sessions above are *proposals*: nothing here has been agreed with the group, and
neither the timing nor the operator is assumed — either could be run by whoever is
at the apparatus, sooner or later or not at all. The **thesis rides on the archive
alone** (P1-min content, with the sessions as future work); the further **papers**
are what a session would unlock, whoever runs it.

## The paper inventory (honest status)

| # | paper | needs | claim | status/risk |
|---|---|---|---|---|
| **P1-min** | *Drift-immune metrology of Rb 5S–6S: method + archival bounds* | archive only | the two-epoch method + closed-form two-photon ramp + **bounds** (β_self, σ_laser, S₀) + systematics | **ready now**; modest but solid + un-scooped; = the thesis core |
| **P1-full** | same, + the fixed-lock coefficients | archive + **a fixed-lock session** | as P1-min, plus **measured** AC-Stark coeff (pull resurrected), β_self (high-T lever + knife-edge w₀), σ_laser | flagship; medium risk (a fixed-lock session must deliver) |
| **P2** | *ONF pushing-dip / near-surface two-photon lineshapes* | **ONF** (+ cell as reference) | quantitative completion of Gokhroo 2022; surface/pushing effects vs the clean cell line | needs an ONF collaboration (not approached); impact set by the ONF result |
| **PA** | *Reference-free light shift / magic-λ on 778 nm 5S–5D via lineshape asymmetry* | new **5D-capable** session (optics set + 420 nm det.) | reference-free, orthogonal-systematics magic-λ cross-check | topical, **methodological not precision-competitive** (see §Paper A caveat there); needs PC |
| **PB** | *β_self and Δα across the Rb 5S→nS/nD ladder (6S, 7S, 5D)* | multi-transition session | the n-scaling series; completes Zameroski/Weber-Niemax | **unscoopable, safer, lower ceiling** — a strong thesis/second-paper bet |
| **PC** | *Near-resonant intermediate state and the two-photon transit/ramp lineshape* | 5D + 7S data | clean(6S)→resonant(5D) lineshape ladder; Bjorkholm–Liao test | methods engine that de-risks PA |

## The 2×2 (fixed-lock session × ONF), Ti:Sapph 5D/7S as a conditional add-on

| | **no ONF** | **with ONF** |
|---|---|---|
| **no a fixed-lock session** | **P1-min** only (1 paper: method + bounds). The safe floor. | **P1-min + P2** (2 papers; P2 uses the *archival* cell as reference — weaker but workable). |
| **with a fixed-lock session** | **P1-full** (the flagship). **+ PA/PB/PC** iff the session tunes to 5D/7S (→ up to 4 papers). | **P1-full + P2** (P2 now uses the *fixed-lock-refined* cell reference — the strongest Paper 2). **+ PA/PB/PC** if extended (→ up to 5). |

## Decision guidance

- **P1 is the anchor and it is not really optional** — the only choice is *when/what
  form*:
  - **(a) Hold for P1-full** (one combined paper, a fixed-lock session fills §VII). Higher impact;
    defensible because the 5S–6S light shift / β_self is **un-scooped** and the field
    is not racing on this line (it is all on 778 nm — `LITERATURE.md` §8), so priority
    pressure is low. **Recommended default.**
  - **(b) Publish P1-min now**, follow with a measurement paper after a fixed-lock session. De-risks
    priority, gives an earlier output and a clean thesis chapter, at some cost of a
    thinner first paper. Choose this if a publication is needed on a fixed timescale —
    which, since no session is scheduled or agreed, is the realistic default rather
    than a fallback.
- **P2 needs an ONF collaboration** that has not been approached; it is gated on the
  fibre work, not on us, and is *better with* a fixed-lock session (a refined cell
  reference). If ONF data appear first, P2 can still proceed on the archival reference.
- **PA/PB/PC are the Ti:Sapph upside**, gated on a session that reaches 5D/7S. If the
  installed SolsTiS optics set is **700–1000 nm**, 5D/7S ride the *same optics* as the
  6S work (only the 420 nm detection swap) — then **PB** (the safe, unscoopable ladder)
  is the natural low-risk add, and **PA+PC** the higher-reward option. If the set is
  950–1050, 5D/7S need an optics swap first — treat PA/PB/PC as a later program.

## Recommended writing plan (concrete)

1. **Now → thesis:** write the thesis on the archive = **P1-min content** + the
   fixed-lock/ONF/Ti:Sapph plans as future work. (The analysis is done; this is a
   writing task, not a measurement one.)
2. **Default first paper = P1-full**, submitted after a successful a fixed-lock session cell
   session. Keep P1-min as the fallback if a fixed-lock session slips past a needed deadline.
3. **Second paper, whichever campaign lands first:** P2 (if ONF) or PB (if a 5D/7S
   Ti:Sapph session). Both reuse the validated pipeline/method.
4. **Opportunistic third:** PA+PC (the 5D magic-λ story) if a 5D session with adequate
   S₀ (small waist) happens — framed as method + cross-check, not a precision claim.

*Cross-refs: `PAPER1_SKELETON.md` (P1 structure), `PLAN.md` §8–9 (the fixed-lock session + Ti:Sapph
shot lists), `FUTURE_TRANSITIONS_titsapph.md` (PA/PB/PC physics + optics), `LITERATURE.md`
§8 (competitive landscape + positioning).*
