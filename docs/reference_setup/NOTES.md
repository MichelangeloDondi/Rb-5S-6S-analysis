# Reference setup — photo catalog + food for thought (2026-07-18)

*Transcribed from a set of lab photos of the 993 nm reference setup and the
HighFinesse wavemeter drift traces. UNCOMMITTED, exploratory. The JPEGs live in
`./photos/` (gitignored — they carry serials + a purchaser name). Numbers below
are read off phone photos of instrument screens — treat as approximate /
qualitative until confirmed against each instrument's own log files.*

## 1. Equipment inventory (apparatus provenance for the methods/apparatus section)

| Role | Model | Read off the photo |
|---|---|---|
| Pump laser | Coherent **Verdi V-18** (532 nm) | set 18.50 W, 50.37 A |
| Ti:Sapph | **M Squared SolsTiS** | labelled M-SQUARED (matches DATA.md) |
| Wavemeter | **HighFinesse WS-8** (Ångstrom WS 8), unit **WSU-4039** | reading 993.4 nm / 301.78 THz; long-term logging to ~kHz divisions |
| Scope (archival) | Teledyne LeCroy **WaveSurfer 3104z**, 1 GHz, 4 GS/s | asset tag **SiP FY24-06** — this is the 2025 archival exporter (`constants.TRACE_N_POINTS/DT`) |
| Scope (other) | Teledyne LeCroy **WaveSurfer 10**, 1 GHz, 10 GS/s | second scope on the bench |
| EOM (ruler) | Photonics Technologies **EOM-02-12.5-V**, SN 0240 | resonant **12.5 MHz**, 3 dB BW 546 kHz, SWR 1.09, AR 650-1000 nm; OIST group order, 2018 |
| IR detector | New Focus **2153 IR Femtowatt Photoreceiver**, SN 13266-WX | InGaAs; DC-750 Hz; transimpedance gain up to 2e11 V/A |
| Chiller (Ti:Sapph) | ThermoTek | 20.00 C |
| Chiller (pump) | Coherent | 18.02 C |
| Cell temperature | MTCD dual-channel controller | cell wrapped in foil, thermocouple |
| Room | — | ~26-31 C (hot lab; Okinawa summer) |

## 2. The wavemeter drift traces (WLM LongTerm, unit WSU-4039)

All traces are the **laser-axis** frequency near 301.78 THz (993.4 nm fundamental);
double for the two-photon **transition axis**. Dates on the captures are
**June-July 2025** — around and just before the Aug/Oct 2025 archival campaign.
The different absolute wavelengths (993.415-993.421 nm) are the laser parked on
different hyperfine/isotope peaks of the 5S-6S manifold (they span ~GHz).

| Capture | Window | What it shows | Read-off |
|---|---|---|---|
| settling | ~8 min (7/18 17:03, 26.2 C) | smooth exponential settle after a step | ~40 MHz transient, then **StdDev ~100 kHz** in the settled region |
| long run | ~3.5 h | slow downward drift + large fast excursions | slow drift **~0.3 MHz/min laser (~0.6 MHz/min transition)**, fast excursions filling ~70 MHz |
| sawtooth | ~4 min (6/19 14:36) | very regular sawtooth | **StdDev 25.3 MHz**, ~+/-35 MHz p-p, ~10 s period |
| two-regime | ~16 min | slow ~10 MHz wander (~11 min) then abrupt onset of a large fast oscillation | regime change mid-record |
| 31 C days | 9-27 min | fast oscillation of tens of MHz throughout | |

**The settled ~100 kHz StdDev is a direct, independent corroboration of the
`constants.DRIFT_RATE`/within-block figure** (`constants.py`: "within a repeat
block the measured scatter is only ~0.08 MHz because repeats were saved
back-to-back"). The 4 MHz/min in `constants.py` is explicitly an *envelope*; these
traces show the *settled* short-time behaviour sitting an order of magnitude
below it, exactly as the drift-immune argument assumes.

## 3. Food for thought

### 3.1 The wavemeter is a timestamped, independent drift log — the timestamp lead, revisited

The single most useful thing here. The **HighFinesse WLM LongTerm graph logs
frequency vs. wall-clock time**, and the captures carry real dates/times
(6/19, 7/18, 7/23 2025). If that logging was running during the **archival**
campaign (Aug 23 / Oct 5 2025), its export is:

1. **a genuine acquisition-time record** — the exact thing the earlier
   timestamp hunt concluded the scope CSVs had lost (the whole reason M4c's
   sigma_laser-sharing is untestable, RESULTS.md / PLAN.md post-mortem #5); and
2. **an independent, absolute drift diary** of the lock — a second monitor
   alongside the scope, at ~kHz precision.

**Action:** check whether HighFinesse `.wlm` / exported CSV logs were saved on the
wavemeter PC (`C:/Program Files (x86)/HighFinesse/...` per the manual screenshot)
spanning the archival dates. Even a coarse, few-second-cadence WLM log over those
sessions could partially resolve the acquisition-timing ambiguity the archive
otherwise can't — worth asking Zohreh before concluding timestamps are
unrecoverable.

> **Draft ask to Zohreh:** Does the HighFinesse WS-8 PC still hold the WLM
> long-term frequency logs from the Aug-Oct 2025 5S-6S sessions? If it was
> logging during acquisition, its timestamps could recover the per-scan timing
> the scope CSVs never saved -- the gap that makes the sigma_laser-sharing (and
> hence the tighter beta) untestable.

For the *new* campaign it is free: run WLM long-term logging
throughout and it becomes the drift diary PLAN 8.4 asks for, complementing the
scope-`.trc` TRIGGER_TIME route.

### 3.2 The EOM certificate confirms the ruler's 12.5 MHz modulation

The ruler's whole absolute calibration rests on the EOM drive frequency:
`ruler.py` and `methods/05` take teeth **6.25 MHz apart on the laser axis =
Omega/2** (the two-photon sum picks sideband *pairs*, so teeth appear every
Omega/2), and calibrate the sweep as `rate = 6.25 MHz / Delta_ms`. The
**Photonics Technologies certificate independently pins Omega = 12.5 MHz**
(resonant 12.5 MHz, 3 dB BW 546 kHz) — a hardware document backing the number the
0.042526 MHz/ms sweep rate (a headline value) depends on. Not a discrepancy; a
corroboration worth citing in the methods apparatus paragraph. (The rate
itself was corrected on 2026-08-01 from 0.04257061 when the comb fit was
extended from five teeth to seven, which is a -0.104% shift; the EOM's
12.5 MHz drive is unaffected and remains the anchor.) (The 546 kHz
bandwidth is comfortably wider than any drift over a scan, so the sidebands stay
on-resonance across the sweep.)

### 3.3 The large periodic excursions — scan ramp, or lock limit-cycle?

Several traces show a large, regular oscillation (the 4-min one is a clean
~+/-35 MHz sawtooth, StdDev 25.3 MHz). Two readings, with very different
consequences, and worth telling apart from the raw WLM log:

- **Intentional scan ramp** — the laser being swept across the line for
  spectroscopy. Then the sawtooth amplitude/period is just the scan, and this is
  normal operation. (A ~10 s WLM-visible period is much slower than a 1 s data
  scan, so this is more likely a *coarse survey* scan than the acquisition scan.)
- **Servo limit-cycle** — the lock oscillating. A periodic +/-tens-of-MHz
  excursion on the timescale of a scan would be a *within-scan* frequency
  modulation far larger than the ~0.13 MHz linear within-scan drift the closure
  test (`tests/test_intrascan_drift.py`) bounds — and, unlike a slow linear
  drift, a periodic modulation is exactly the kind of non-affine axis warp that
  *can* bias the ramp skew. If any of this is a limit-cycle at scan timescales it
  should be added to the intra-scan stress cases and, more importantly, fixed at
  the lock before the fixed-lock campaign.

Distinguishing them needs the WLM log timebase vs. the data-scan duration — cheap
to do, and it either retires a worry or promotes a systematic.

### 3.4 The IR femtowatt receiver may already be the 1.3 um cascade detector

The **New Focus 2153** is an InGaAs femtowatt receiver (roughly 0.9-1.7 um,
DC-750 Hz, up to 2e11 V/A). The trapping-free detection exploit (PLAN 8.4a) reads
the **6S->5P ~1.3 um cascade** to beat radiation trapping (prior art
`hassanin2023`, `beard2024`). 1.3 um sits squarely in this detector's InGaAs band,
and DC-750 Hz is ample for a ~1 s scan. So the hardware for that exploit may
already be on the bench — a concrete feasibility point for 8.4a, and a cheap
add-on measurement to trial in the fixed-lock session.

### 3.5 Thermal environment

Ti:Sapph chiller 20.00 C, pump 18.02 C, but **room ~26-31 C**. The slow
wavemeter wander (3.5 h run) tracks a lab that is far warmer than the chiller
setpoints, so the residual drift is plausibly lab-thermal, not intrinsic. The
fixed-lock campaign's stability target benefits from anything that tightens room
control (or at least logs room T alongside the WLM, so the drift diary can be
regressed against it).

## 4. Open items to close with the actual logs (not from photos)

- Pull the HighFinesse WLM export for the archival dates if it exists (3.1).
- Identify the periodic excursions as scan vs. limit-cycle from the WLM timebase (3.3).
- Confirm the 2153's wiring/role — is it already on the 1.3 um port, or on 993 nm? (3.4).
- Fold the EOM 12.5 MHz certificate into the methods apparatus provenance (3.2).

## 5. The optical isolator, identified (2026-08-01)

**ISOWAVE I-98T-5L** — recalled by the experimenter, not read off a photo.
Confirmed against the manufacturer's 900-1000nm isolator datasheet
(ISOWAVE DS9010-012010): 5 mm clear aperture, centred 980 nm standard
(orderable 900-1000 nm), tunable input polarizer, 35/38 dB isolation
(min/typ), 0.3/0.5 dB insertion loss (typ/max), 34.9 mm housing diameter,
102 mm length. Sits after the SolsTiS and before the L1 focusing lens,
per the Nieddu/Rajasree layout this bench follows.

**Why it matters:** the archival `constants.py` w0 note blamed the naive
32 um waist estimate on "the EOM aperture" clipping a ~3mm input beam --
that 3mm figure looked inferred backward rather than sourced. The isolator
is the one apertured element between the laser and L1 with a manufacturer
spec, and its 5mm aperture is comfortably larger than any plausible SolsTiS
output beam there, so it does NOT clip. That looked like it removed a leg
of the old clipping story.

**CORRECTED same day, from the experimenter:** no lens or telescope sits
between the SolsTiS and the EOM, so the isolator and EOM both see the raw
output beam -- and the experimenter recalls an IR viewer card showing
clipping AT THE EOM specifically (recollection, over a year old). The
EOM's own aperture is now sourced too: `photonicstechnologies.com`'s
"Standard Characteristics" table for the EOM-01/EOM-02 series states
**Aperture Diameter 3mm** (confirmed via curl + grep on the raw page,
not just an LLM summary), applying to both crystal variants including
our EOM-02-12.5-V. So the original clipping story SURVIVES and is now
better sourced: a real 3mm aperture, plus an experimenter's real
(if decades-old-feeling) memory of clipping there. What it still can't
do is fix HOW MUCH of the beam was clipped -- that keeps w0 = 32 um a
Gaussian-optics estimate, not a measurement, and the transit-width match
plus Nieddu/Rajasree's direct 64 um remain the stronger evidence.
Propagated to constants.py, docs/notes/transit_width_resolved.md,
APPARATUS.md sec 1.2 and sec 2, PAPER1_SKELETON.md sec IV.

**Still open:** whether the beam is apertured or expanded anywhere else
before L1, and the actual collimated beam diameter there from any lab
record -- see private/AFTER_THE_EMAIL.md.

## 6. Two cavity-error records digitised (2026-08-01): IMG_2580, IMG_2737

Both show the WLM with the scan STOPPED by a reference-cavity error (the
state in which the scope's spectroscopy signal goes flat -- the user's own
description). Digitised with the M22 colour-extraction approach; the
calibration is SELF-VALIDATING: mapping the two labelled gridlines
(1 MHz apart, laser axis) to pixels reproduces the panel's own displayed
Mean to +2 kHz (2580) and +4 kHz (2737). Dates from EXIF; 2580's EXIF
(2025-06-18 21:13) matches the taskbar clock in shot, validating the EXIF
route for the folder.

| record | EXIF date | span | lambda | RMS (laser) | p-p | drift | autocorr 1/e |
|---|---|---|---|---|---|---|---|
| IMG_2580 | 2025-06-18 21:13 | 2:05 min | 993.4191 nm | 0.052 MHz | 0.33 MHz | -0.049 MHz/min | ~1.9 s |
| IMG_2737 | 2025-07-02 16:39 | 5.5 min | 993.4165 nm | 0.037 MHz | 0.23 MHz | -0.005 MHz/min | ~0.8 s |

Context: 2580 is the evening before the 06-19 sawtooth/etalon-only
records; 2737 is one day before the EOM trials (07-03) and two days
before the LeCroy rehearsal (07-04).

What they are and are not:
- They are the LASER's scan-off frequency record at the wavemeter's
  ~second exposure: slow-component floor ~40-50 kHz RMS, drift between
  -0.005 and -0.05 MHz/min. They corroborate the within-block 0.08 MHz
  laser scatter (as an upper bound) and bracket the held-lock
  ~0.016 MHz/min drift figure.
- They are NOT a sigma_laser measurement (the ms-scale kernel is averaged
  out by the exposure) and NOT usable for the M1 detection-noise model
  (wrong channel entirely -- M1 is PMT trace residuals).
- They refine the section-6 comparison: the no-cavity state is not
  uniformly 0.4-1.0 MHz/min; it also has quiet phases, minutes long,
  at tens of kHz.
- Failure-mode documentation: cavity error -> sweep stops -> flat trace.
  Checked: no archival CANONICAL trace shows this; the rehearsal's 4
  unusable files are 0xff disk corruption, a different failure. The
  campaign/pilot discard sets were not exhaustively re-checked for flat
  traces (parking lot).

Propagated to APPARATUS.md section 6 (table rows + digitisation block).
Scratch digitisation code inline in the session, not yet a module; the
promotion path (an M22-style module + committed CSV) is in
private/AFTER_THE_EMAIL.md.
