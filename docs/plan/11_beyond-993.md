*Chapter 11 of 12 of [the plan](../PLAN.md)*

## 12. Beyond 993 nm, and the one rider that costs no drive time

The drive laser is a tunable Ti:Sapphire, so future sessions are not locked to
this line. The reachable Rb two-photon lines and the papers they enable are
worked out in
[`FUTURE_TRANSITIONS_titsapph.md`](../FUTURE_TRANSITIONS_titsapph.md), which is
also where the cost, yield and failure-mode comparison across all of them lives. The
most distinctive candidate on the Ti:Sapph itself: the 778 nm clock line is the
most actively worked AC-Stark system, all of it active suppression, and the
passive asymmetry method plus the Ti:Sapph tunability could give a
reference-free magic-wavelength determination, through the asymmetry sign
reversal across Hamilton 2023's 776 nm magic wavelength.

**The nanofiber beside the cells, three instruments in one apparatus.** The
lab's ONF with its two-colour trap, run trap-dark, is sized in
[`onf_candidate.md`](../notes/onf_candidate.md) with every number produced by
`run_onf_candidate.py` and labelled by basis. The cold trap-off mode measures
the laser's width independently, which is the identifying rung of the width
channel's intercept ladder. The atom-surface tail is a C3 measurement for the
6S state against silica, on the path the Rydberg-near-fiber programme already
walks. Hot vapor turns the transit kernel into the measured object, though hot
rubidium degrades fiber transmission, and the Stark geometry seam in
`model_profile` gets its first second geometry for free. None of it replaces
the cell campaign, because nothing at the fiber carries a density ladder.

**The O-band null at 1297.5 nm, an optional rider on any cell session.** The
computed differential polarizability of the 5S and 6S clock states has a steep
zero crossing at 1297.5 nm, useless as a trap and precise as a lever. One
auxiliary telecom-band beam, scanned across the crossing while the light shift
it induces is read out through the lineshape channel this record already
extracts, would locate the crossing and thereby measure the 6S to 7P matrix
element by frequency metrology rather than by intensity calibration. The same
scan drives the induced shift through zero and out the other side, which is a
sign-reversal test of the asymmetry channel with every instrumental confound
held still, and off the crossing it is a calibrated shift injector for
exercising the §6 analysis on data with a known light shift. It needs no
Ti:Sapph time, because it rides whatever the session is already doing on the
993 nm line.
**Needs.** One stabilized O-band diode and a calibrated wavemeter, both
commodity items at this wavelength, plus a way to overlap the auxiliary beam
with the drive at the cell. No change to the 993 nm path. **Shots.** A
wavelength scan of the auxiliary beam across the crossing, with the 993 nm
lineshape read at each point, run alongside the §6 power blocks. **Go/no-go.**
The delivered perturber intensity at the cell must be enough to move the 993 nm
line by more than the achieved shift precision. Measure it before committing
scan time. **Empty.** The delivered intensity could undershoot, which stretches
the localization beyond the useful range and returns a bound on the crossing
position rather than a measurement. **Record.** The induced shift and the
asymmetry against auxiliary wavelength, and the crossing position with its
error. The full specification, the localization it would reach at the campaign's
projected shift precision, about 26 pm and a 6S to 7P residue near 3 per cent,
and the multipole scrutiny behind the predicted position are in
[`FUTURE_TRANSITIONS_titsapph.md`](../FUTURE_TRANSITIONS_titsapph.md) §5.1.

## Appendix A. The analysis plan of record (executed)

The from-scratch analysis plan that produced the current results was versioned
here until 2026-08-02 and lives in git history. Its content is now where a
reader needs it: the module map and derivations in [`methods.md`](../methods.md),
the data census, chronology and exclusion policy in [`DATA.md`](../DATA.md), the
per-trace table in `data_raw/MANIFEST.csv`, the verification battery in
`tests/` (synthetic closure before real data, end-to-end injected-truth
recovery), and the results with provenance tags in [`RESULTS.md`](../RESULTS.md).
Two of its ground rules bind every future session too: the transition (sum)
frequency axis everywhere, and nothing numeric hard-coded outside
`constants.py` and `config.py`.

---

*[The instrument and the session](10_the-fixed-lock-instrument.md) · [The open apparatus items](12_open-apparatus-items.md)*
