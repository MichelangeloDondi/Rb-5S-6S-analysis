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

**The ECD lock is disengaged in every photograph**, including both operating
days. Running on etalon (± reference-cavity) lock alone leaves no absolute
frequency reference, which is exactly the failure the archive shows: line
centres drift between scans and carry no metrological meaning, while shapes
survive. This is *consistent with* the recorded symptom and is the most
specific account available — but **no photograph covers the 17–18 July
campaign itself**, so it remains a strong candidate, not a confirmed fact.

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
| Cell fluorescence detector | **Thorlabs PXT1/M** (heat-sinked module) | PHOTO 2025-07-18 (in campaign) |
| Cathode geometry | 3 × 12 mm rectangle | **ASSUMED** — see below |
| Filter stack | ~50 dB of 795 nm passband (not a short-pass) | DATA / EXPERIMENTER |
| IR receiver on the bench | **New Focus 2153 IR femtowatt photoreceiver**, gain to 2×10¹¹ V/A, DC–750 Hz | PHOTO 2025-07-29 |

> **Unresolved, and it matters.** `config.py` attributes the detector to a
> side-on Hamamatsu R636-10, citing **Nieddu 2019 — the nanofibre experiment,
> not this bench**. The only in-campaign photograph of the detector shows a
> Thorlabs PXT1/M. Whether that module houses an R636-10 or is a different
> detector is open. The 3 × 12 mm cathode, the ×4 rotation lever, and the
> landscape-vs-portrait install decision in `PLAN.md` §8.3 #4 all follow from
> the assumed cathode and must be re-derived if it is wrong. The ×14 flip
> window does **not** depend on it.

The IR receiver is the instrument [BIG_PICTURE](BIG_PICTURE.md) refers to as
"an IR receiver already on the bench" for the trapping-free 6S→5P 1.3 µm
cascade option ([FUTURE_TRANSITIONS](FUTURE_TRANSITIONS_titsapph.md)). Its
DC–750 Hz bandwidth is comfortable against a 1 s scan.

---

## 4. Acquisition

| item | value | provenance |
|---|---|---|
| Scope of record | Teledyne LeCroy **WaveSurfer 3104z**, 1 GHz, 4 GS/s | PHOTO 2025-07-29 |
| Also on the bench | LeCroy **WaveSurfer 10** (1 GHz, 10 GS/s); Agilent **DSO-X 3054A** (500 MHz) | PHOTO 2025-07-29, 06-10 |
| Trace format | 2000 points, 0.5 ms step, 1.000 s window | DATA |
| Wavemeter | HighFinesse **Ångstrom WS-8** (WS/8L, unit 4039) | PHOTO |
| Wavemeter autocal | every 8 minutes | PHOTO 2025-06-08 |
| Wavemeter short-term StdDev | 100 kHz (floating, 10 measurements) | PHOTO 2025-07-18 |

### 4.1 A ramp-monitor channel existed

A 2025-06-10 photograph of the Agilent scope shows **two channels**: a clean
triangular **sweep-ramp monitor** on Ch1 and the fluorescence on Ch2, with the
fluorescence peaks mirrored about the ramp apex — the fold, directly visible.

That bears on assumption **A1** (scope triggered on the sweep sync, so file
time = ramp phase), which `PLAN.md` still lists as needing one word of
confirmation. A ramp monitor was available; a 2025-07-15 photograph of the
LeCroy shows the five-tooth comb with the scope reading "Trig'd". **If the ramp
channel was saved alongside the fluorescence for any archival trace, A1 becomes
directly testable rather than assumed** — the archive as curated holds
single-channel traces, so this is a question for the experimenter.

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

**The question this leaves.** Campaign drift depends on which lock was engaged
on 17–18 July, and no photograph covers those days. If the campaign ran
etalon-only — which the "misconfigured lock" description and §1.1's
never-engaged ECD both suggest — the settled expectation is ~1 MHz/min. With
the reference cavity it would be ~0.2. The Ti:Sapph ran continuously through
the 24 h ([DATA.md](DATA.md) §2), so most acquisition sat in the settled
regime; re-centring events that involved retuning would restart a transient,
and how often that happened is not established.

---

*Nothing on this page changes an archival result. It records what the
measurement was made with, which of those facts are verified, and which are
inherited assumptions still to be checked.*

[← DATA.md](DATA.md) · [PLAN.md](PLAN.md) · [methods index](methods.md)
