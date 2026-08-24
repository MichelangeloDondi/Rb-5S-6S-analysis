# Bench photographs and schematics

These are the dated setup photographs, the beam-path schematic and one
digitised scope record that establish what the 2025 measurement was made
with. [../APPARATUS.md](../APPARATUS.md) is the document that reads them:
each asset is embedded there inside the passage that uses it, under a caption
saying what the frame shows, and every technical fact drawn from an asset
carries a provenance tag on that page. What is published here is a curated,
metadata-stripped subset of the photograph set, with frames carrying
equipment serials or a name held back. Every asset here is referenced from a
documentation page, all but the last from `../APPARATUS.md`.

| file | what it shows | date | section that uses it |
|---|---|---|---|
| `2025-06-10_agilent_ramp_and_hyperfine_peaks.jpg` | The Agilent dso-x 3054a of record, channel 1 carrying the cavity triangle and channel 2 the fluorescence, with four hyperfine peaks on Doppler pedestals and their mirror images folding at the ramp apex. | 2025-06-10 | §4.2 The ramp-monitor channel |
| `2025-06-11_solstis_lock_page.jpg` | The SolsTiS control page at 23:33, reading etalon Locked, ref cav Locked, ECD Not Locked, and scan "Cavity triangular". | 2025-06-11 | §1.1 Lock configuration |
| `2025-06-11_wavemeter_drift_23min.jpg` | A 23 minute wavemeter LongTerm record photographed at 22:52, the first of the pair whose envelope drift reads 0.19 MHz/min. | 2025-06-11 | §6 Laser drift |
| `2025-06-11_wavemeter_drift_53min.jpg` | The 53 minute two-regime LongTerm record photographed at 23:22, the second of that pair. | 2025-06-11 | §6 Laser drift |
| `2025-06-12_cavity_scan_IMG_2508_digitised.csv` | Two digitised scope channels from the cavity-scan photograph. Channel 1 is the 5.00 s triangular cavity ramp with its apex at t = 2.62 s. Channel 2 reads as the four 5S to 6S hyperfine components crossed once per sweep direction. | 2025-06-12 | §6 Laser drift |
| `2025-07-01_cell_thermocouples.jpg` | The cell unwrapped in its copper block, Kapton-taped thermocouple positions 3 and 4 annotated on the frame itself, and Rb condensation visible on the window. | 2025-07-01 | §5 Cell and thermal environment |
| `2025-07-15_eom_comb_five_teeth.jpg` | The two-photon EOM comb on the scope at 200 ms per division, with carrier, first sidebands and two faint outer teeth. | 2025-07-15 | §4.2 The ramp-monitor channel |
| `2025-07-18_detection_region_overview.jpg` | The detection region as it ran, with the foil-wrapped cell, the Thorlabs PXT1/M module housing the r636-10 below it, the lens tube pointing toward the cell, and the mtcd dual-channel temperature controller. | 2025-07-18 | §3 Detection |
| `2025-07-18_wavemeter_relock_settling.jpg` | The later of the two in-campaign wavemeter records, taskbar clock reading 17:03, showing the re-lock transient after the daytime break with the instrument's own statistics panel in shot. | 2025-07-18 | §6 Laser drift |
| `2025-07-29_lecroy_ws3104z.jpg` | The Teledyne LeCroy WaveSurfer 3104z, the scope of the 2025-07-04 dress rehearsal and not of the archive. | 2025-07-29 | §4.2 The ramp-monitor channel |
| `2025-07-29_source_chain_overhead.jpg` | The source chain from above, the Verdi v-18 pump feeding the M Squared SolsTiS modules. | 2025-07-29 | §1 Source chain |
| `2025-07-29_verdi_v18_panel.jpg` | The Verdi front panel at its campaign set point, 18.50 W and 50.37 A. | 2025-07-29 | §1 Source chain |
| `apparatus_schematic.svg` | The bench in one drawing, the beam path from pump to detection with components numbered 1 to 13 following the annotated bench photograph that also fixes the drawing's handedness. | none in the filename | The page header, above the provenance tags |
| `program_timeline.png` | Not referenced from `../APPARATUS.md`. It is embedded in the campaign chronology of [../DATA.md](../DATA.md), and it is drawn by [`scripts/make_timeline_figure.py`](../../scripts/make_timeline_figure.py), which writes its output into this directory. | none in the filename | none on the apparatus page |

The photographs are the only record of several bench facts, because the
wavemeter logs and the sweep-ramp channel were never saved to disk. Where a
number here was extracted rather than read off a panel, the extraction is a
script and the apparatus page names it.

[← APPARATUS.md](../APPARATUS.md) · [docs index](../README.md)
