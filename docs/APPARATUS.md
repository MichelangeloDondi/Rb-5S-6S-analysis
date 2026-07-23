# Apparatus — hardware of record and its provenance

*What the 2025 measurement was actually made with, and how each item is known.
Compiled 2026-07-23 from dated setup photographs (2025-06-07 → 2025-07-29). The
photographs themselves are not published — they carry equipment serials and a
purchaser's name — so this page records the technical facts and their dates.*

Provenance tags: **PHOTO** (read off a dated setup photograph), **DATA**
(established from the archive files), **ASSUMED** (inherited from a citation,
not verified for this bench), **EXPERIMENTER** (recollection).

---

## 1. Source chain

| item | value | provenance |
|---|---|---|
| Pump | Coherent Verdi V-18, 18.50 W set, 50.37 A | PHOTO 2025-07-29 |
| Ti:Sapph | M-Squared SolsTiS (unit 196010) | PHOTO 2025-06-10 |
| Pump chiller | 18.02 °C (set 18.0), stable to ~0.03 °C | PHOTO 2025-07-29 |
| Ti:Sapph chiller | 20.00 °C (set 20.0), stable to ~0.01 °C | PHOTO 2025-07-29 |
| SolsTiS internal temperature | 40.000 °C | PHOTO 2025-06-10/11 |
| Scan mode | **"Cavity triangular"**, continuous | PHOTO 2025-06-10/11, 07-29 |

The scan-mode reading matters: `DATA.md` §5 *infers* a triangular sweep with a
fold from the traces themselves. The SolsTiS control page states it directly.

### 1.1 Lock configuration — the concrete candidate for "misconfigured"

`DATA.md` §1 says only that "the 2025 lock was misconfigured". Three dated
photographs of the SolsTiS control page show which locks were engaged:

| date | etalon lock | ref-cav lock | ECD lock |
|---|---|---|---|
| 2025-06-10 | Locked | **Not Locked** | **Not Locked** |
| 2025-06-11 | Locked | Locked | **Not Locked** |
| 2025-07-29 (teardown) | Not Locked | Not Locked | Not Locked |

**The ECD lock is disengaged in every photograph.** For the campaign itself
the experimenter confirms (2026-07-23) that the **reference cavity was
locked**, with its **set point moved from time to time to follow the drift** —
which is what `DATA.md` §2 records as "cavity-reference recenters".

That completes the account of "misconfigured". Etalon + reference cavity hold
the laser *short-term*, which is why shapes survive and intra-block positions
are stable. What is missing is the ECD lock, i.e. any **absolute** reference —
and because the cavity set point was re-defined by hand whenever drift pushed
the line out of the window, the zero of the frequency axis is re-chosen
arbitrarily between blocks. Hence: centres carry no metrological meaning,
shapes do. The two halves of the archive's central limitation fall out of the
lock configuration exactly.

**The ECD lock was never engaged during the campaign**
(experimenter-confirmed, 2026-07-23: "I never touched it"), consistent with
every photograph. Why is a separate question — the experimenter's guess is
that it was not working, which is untested. For a future session that
distinction matters: if the ECD lock is functional, engaging it converts the
archive's whole shape-only limitation into an absolute-frequency capability
at zero hardware cost; if it is broken, that is the first repair to price.
**Checking whether the ECD lock works is therefore the cheapest
highest-leverage test a future session could open with.**

---

## 2. Frequency ruler — the EOM chain

The comb ruler underwrites the whole frequency axis, and assumption 1 of
[methods §6](methods/08_assumptions_and_outlook.md) records that everything
scales ×2 if the tooth spacing is Ω rather than Ω/2. Both halves are now
documented in hardware:

| item | value | provenance |
|---|---|---|
| RF source | Tektronix **AFG31021**, 25 MHz / 250 MS/s | PHOTO 2025-07-29 |
| RF setting | **12.500 000 000 0 MHz**, sine, continuous, **10.00 Vpp**, 0 offset | PHOTO 2025-07-29 |
| EOM | Photonics Technologies **EOM-02-12.5-V**, ×2 units | PHOTO (certificates) |
| EOM resonance | **12.5 MHz** (both units) | PHOTO |
| EOM 3 dB bandwidth | 550 kHz / 546 kHz | PHOTO |
| EOM AR coating | **650–1000 nm** — covers 993.4 nm | PHOTO |
| EOM impedance / SWR | 52 Ω, 1.29:1 / 50 Ω, 1.09:1 | PHOTO |
| Drive for 100% modulation | 15.4 V / 16.0 V pk-pk | PHOTO |

So Ω = 12.5 MHz is set to 0.1 Hz resolution on the generator *and* is the
EOM's designed resonance, independently. The 6.25 MHz laser-axis tooth spacing
follows as Ω/2 by the two-photon selection rules (`PLAN.md` §2), and the
certificates' own 100%-modulation traces show the same five-tooth pattern the
archive rulers show.

**Modulation headroom.** The campaign ran at 10.00 Vpp, which the certificates
place at **≈54–60% of full modulation**; full scale is ≈1.6× higher in drive
voltage. `PLAN.md` §8.9 asks whether the 12.5 MHz tank can reach β ≈ 1.2 — that
headroom is the first quantitative input to the question. Note the certificates
were taken at 780 nm, and phase-modulation index scales as 1/λ, so the index at
993 nm is ≈0.79× the 780 nm figure at equal drive.

**A constraint on the upgrade path.** The AFG31021 tops out at **25 MHz**, so
the "higher-frequency EOM" fallback in `PLAN.md` §8.9 needs a different
generator as well as a different tank.

---

## 3. Detection

| item | value | provenance |
|---|---|---|
| Cell fluorescence detector | Hamamatsu **R636-10** side-on PMT, housed in a **Thorlabs PXT1/M** module | PHOTO 2025-07-18 (in campaign) + EXPERIMENTER |
| Cathode geometry | 3 × 12 mm rectangle | datasheet TPMS1016E |
| Cathode orientation (2025) | **landscape** — 12 mm axis along the beam | EXPERIMENTER |
| Filter stack | ~50 dB of 795 nm passband (not a short-pass) | DATA / EXPERIMENTER |
| IR receiver on the bench | **New Focus 2153 IR femtowatt photoreceiver**, gain to 2×10¹¹ V/A, DC–750 Hz | PHOTO 2025-07-29 |

> **Resolved 2026-07-23.** `config.py` attributed the detector to an R636-10
> citing *Nieddu 2019 — the nanofibre experiment, not this bench* — and the only
> in-campaign photograph shows a Thorlabs PXT1/M module, which looked like a
> contradiction. The experimenter confirms the PXT1/M **houses** the R636-10, so
> the attribution was right by luck rather than by sourcing. The 3 × 12 mm
> cathode and the landscape-vs-portrait install decision in `PLAN.md` §8.3 #4
> therefore stand. One practical rider: the tube sits in a commercial housing,
> so orientation is set by rotating the *module* — worth checking its mounting
> before assuming both orientations are equally easy to realise.

The IR receiver is the instrument [BIG_PICTURE](BIG_PICTURE.md) refers to as
"an IR receiver already on the bench" for the trapping-free 6S→5P 1.3 µm
cascade option ([FUTURE_TRANSITIONS](FUTURE_TRANSITIONS_titsapph.md)). Its
DC–750 Hz bandwidth is comfortable against a 1 s scan.

---

## 4. Acquisition

| item | value | provenance |
|---|---|---|
| **Scope of record** | Agilent/Keysight **InfiniiVision DSO-X 3054A**, 500 MHz, 4 GSa/s | PHOTO 2025-06-10 + **DATA** (CSV signature) + EXPERIMENTER |
| Also on the bench (not used for the archive) | LeCroy **WaveSurfer 3104z** (1 GHz, 4 GS/s); LeCroy **WaveSurfer 10** (1 GHz, 10 GS/s) | PHOTO 2025-07-29 |
| Trace format | 2000 points, 0.5 ms step, 1.000 s window | DATA |
| Wavemeter | HighFinesse **Ångstrom WS-8** (WS/8L, unit 4039) | PHOTO |
| Wavemeter autocal | every 8 minutes | PHOTO 2025-06-08 |
| Wavemeter short-term StdDev | 100 kHz (floating, 10 measurements) | PHOTO 2025-07-18 |

### 4.1 Why the Agilent, and how we know

The archive was taken on the Agilent, not either LeCroy: the LeCroy would not
trigger reliably (experimenter, 2026-07-23). That is independently confirmed by
the files — every archival CSV opens `x-axis,N` / `second,Volt`, the Keysight
InfiniiVision export signature (398 of 400 sampled; the other two carry a
corrupted first line already tracked as `header_variant`). LeCroy writes a
different header block entirely, so the format alone settles it.

This matters beyond attribution: `PLAN.md` §8.4's advice for recovering
per-scan timestamps was written for LeCroy `.trc`/WAVEDESC files, which this
scope does not produce. Rewritten for InfiniiVision `.h5`, and integrity gate
T6 of the [timestamp pre-registration](PREREGISTRATION_timestamps.md) corrected
the same way — before the backup was opened.

### 4.2 The ramp-monitor channel — available, not saved, and not worth much

A 2025-06-10 photograph of the Agilent shows **two channels**: a clean
triangular sweep-ramp monitor on Ch1 and the fluorescence on Ch2, with the
fluorescence peaks mirrored about the ramp apex — the fold, directly visible.
It was **not saved** with the archival traces (experimenter, 2026-07-23).

**Verdict for a future session: low priority.** The EOM comb already carries
the frequency axis per trace, RF-exact, which a ramp voltage cannot improve on
— so the ramp channel buys nothing for calibration. Its one real use is that
`DATA.md` §5 has to *infer* where each window sits on the triangle, and records
that "window ≈ one up-ramp" holds **for most blocks, not all**, with fits
masking the retrace region. A recorded ramp would make the apex position a
measured per-trace quantity instead of an inference, and would retire
assumption A1 outright rather than leaving it as a stated assumption.

That is worth one spare channel and nothing more. If channels are contended,
this is the first thing to drop.

A 2025-07-15 photograph shows the five-tooth comb on the **LeCroy** reading
"Trig'd", three days before the campaign — consistent with the LeCroy being
tried and then abandoned for the Agilent. It says nothing about A1, since it
is not the scope the archive came from; an earlier version of this page cited
it as weak A1 evidence, which was wrong.

---

## 5. Cell and thermal environment

| item | value | provenance |
|---|---|---|
| Cell | glass vapour cell in a copper block, Kapton-taped, foil-wrapped in operation | PHOTO 2025-07-01, 07-18 |
| Temperature controller | 2-channel | PHOTO |
| Thermocouple/heater positions | **four**, marked 1, 2 (one end) and 3, 4 (the other) | PHOTO 2025-07-01 |
| Rb condensation | visible on the cell windows when unwrapped | PHOTO 2025-07-01 |

Assumption 7 of [methods §6](methods/08_assumptions_and_outlook.md) allows for
"a possible cell cold spot". Four monitored positions along the cell is the
instrumentation you would add to characterise exactly that gradient, and the
visible window condensation shows where Rb collects. Whether the four channels
were logged during the campaign is not established here.

---

## 6. Laser drift — six wavemeter records, and what the cavity lock buys

None of the long-term wavemeter logs were saved to disk, so these are read off
dated screen photographs (±20%, and the band centre of a swept trace is an
eyeball estimate). Only one falls inside the 17–18 July campaign.

Lock state is known for two of the sessions, which turns the table from a list
into a comparison:

| date | span | lock state | reading |
|---|---|---|---|
| 2025-06-16 | 1 h 50 min | — | **~85 GHz of settling** after a tuning change; asymptotes to StdDev 400 kHz |
| 2025-06-11 | 53 min | etalon **+ reference cavity** | **±0.19 MHz/min** |
| 2025-06-19 | 11 min, unswept | **etalon only** (cavity lock off) | **+1.0 MHz/min** |
| 2025-06-19 | 27 min | etalon only | ~0.4 MHz/min |
| 2025-06-19 | 6 min | etalon only | +0.5 MHz/min |
| **2025-07-18** | **8.5 min** | — | **~4.35 MHz/min avg** — **in campaign**, a settling tail (local slope 9.0 → 2.4 MHz/min) |
| 2025-07-23 | 3 h 30 min | — | −0.17 MHz/min |

**The reference-cavity lock is worth roughly a factor 2–5.** With it engaged the
laser holds ±0.19 MHz/min; on etalon lock alone it drifts 0.4–1.0 MHz/min. The
06-11 attribution rests on timing rather than a caption: the two drift records
were photographed at 22:52 and 23:22 and the control page showing *etalon
Locked, reference cavity Locked, ECD Not Locked* at 23:33 — eleven minutes
after the second. Circumstantial, but tight. The 06-19 state
(etalon on, cavity off, thermally settled) is experimenter-confirmed and
matches the configuration photographed on 06-10.

**A within-record control.** The 06-19 record runs unswept for its first
~11 minutes and then with the scan active, under one unchanged lock state —
which is exactly the comparison needed to separate genuine laser drift from any
apparent drift introduced by scanning. Reading it off a photograph is not
precise enough to settle the question, but the measurement exists and the
design is right; a repeat with the log saved would answer it outright.

**Synthesis.** After a tuning change the laser settles through tens of GHz over
roughly 1.5 h (the 06-16 curve); thermally settled, it drifts at ~1 MHz/min on
etalon lock alone and ~0.2 MHz/min with the reference cavity added, with a sign
that varies between sessions. The single in-campaign record is a settling tail,
not a steady rate. `constants.DRIFT_RATE_LASER_HZ_PER_MIN = 4 MHz/min`
therefore stands as a genuine **envelope** — it bounds every record here —
while the settled rate is several times smaller.

**The archive's own numbers, recovered 2026-07-23.** Differencing block
positions against the recovered clock (estimator: experimenter;
`scripts/run_drift_settling.py`; results report addendum 4) gives the
campaign's in-situ figures: the lock drift is **one constant
+0.032 [+0.023, +0.040] MHz/min (laser axis) across the whole session** —
~39 MHz over its 20.5 hours, which is why the reference needed moving all
night — well inside the first-hour within-block bound (≲0.17 MHz/min,
itself matching the photographed cavity-locked ±0.19 MHz/min independently).
A drift-settling term adds nothing (ΔAIC +4); **what settles is the
operator** — per-gap re-centring RMS ~1–4 MHz laser in hour 1 decaying with
τ ≈ 1–2.5 h to ≲0.2 MHz, plus two ~25–50 MHz scan-window repositionings.
That operator settling is what matches the post-retune photographs' scale,
as it should: re-lock transients are when the re-centring works hardest. The clock also
explains the one in-campaign wavemeter record: IMG_2896 (17:03) was shot
eighteen minutes before the 90 °C dwell resumed (17:21), i.e. during the
re-lock after the daytime break — its ~4.35 MHz/min is the re-tune transient
the envelope exists to bound, not the acquisition-time drift, which the
archive puts two orders below.

**What this implies for the campaign.** The campaign ran with the reference
cavity locked (experimenter, 2026-07-23), i.e. the 06-11 regime, so the settled
expectation is **≈0.2 MHz/min** — not the ~1 MHz/min of etalon-only operation.
The Ti:Sapph ran continuously through the 24 h ([DATA.md](DATA.md) §2), so most
acquisition sat in the settled regime; each manual set-point move re-zeroed the
accumulated offset rather than restarting a thermal transient, since the laser
was neither retuned nor restarted.

**A bound this yields, for free.** The intra-block positions show *no* trend
with repeat index (§[PREREGISTRATION](PREREGISTRATION_timestamps.md) §8.4,
p = 0.33). At ≈0.2 MHz/min, drift would reach the observed 0.08 MHz scatter
only after ~70 s, so its absence bounds the block:

> **The MEDIAN 5-repeat block spans less than ~70 s** (under ~14 s per saved
> trace). **Scored 2026-07-23: PASS** — median 34 s, range 20–148 s
> ([PREREGISTRATION_RESULTS.md](PREREGISTRATION_RESULTS.md)).

That replaces the voided D4 and inverts its logic: D4 divided the scatter *by*
a drift rate, assuming the scatter *was* drift; this uses the **absence** of
drift, together with a drift rate now known from the lock state, as an upper
bound. It was a genuine pre-data prediction about the recovered timestamps, and it held.

---

*Nothing on this page changes an archival result. It records what the
measurement was made with, which of those facts are verified, and which are
inherited assumptions still to be checked.*

[← DATA.md](DATA.md) · [PLAN.md](PLAN.md) · [methods index](methods.md)
