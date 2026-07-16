*Chapter 8 of 8 · [methods index](../methods.md) · assumes only the chapters before it.*

## 6. Load-bearing assumptions (the ones to challenge)

1. Comb teeth spaced $\Omega/2$, not $\Omega$ (everything scales $\times2$ if
   wrong; locked by tests + the 5-tooth amplitude pattern + a hyperfine
   label-spacing check).
2. Scope triggered on the sweep sync so file-time $=$ ramp-phase (evidence
   strong; experimenter confirmation pending — `A1` in PLAN).
3. Kernel *shapes*: laser Gaussian, transit two-sided exponential (the Voigt
   split depends on them). The model-form study ([§4.7 — The statistics](06_the_statistics.md), M8) confirms the 2025
   data cannot distinguish these forms — so the *shape* assumption is untested
   by the archival data and is a genuine attack surface until a fixed-lock session.
4. Transit width rides on the OPEN $w_0$ prior until the knife-edge measurement.
5. The retro ratio $\rho=1$ behind the quoted $S_0$ prediction ([§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md)) is a
   *geometric design property, not a measured number*. The 2025 retro is
   self-imaging: L2 ($f=150$ mm) maps the cell waist to a $\sim$1 mm
   intermediate waist and a flat mirror at that flat wavefront time-reverses
   the beam, re-forming the original waist ([§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md)) — so the forward/return
   *mode match* is by construction, and $\rho$ departs from 1 only through
   *losses* (two extra L2 passes, two extra window passes, mirror
   reflectivity), never characterized for the archive. The exposure is bounded
   anyway: $S_0\propto(1+\rho)$ confines the prediction to 0.29–0.59 MHz for
   any $\rho$, and the Doppler-free rate's own $\propto\rho$ scaling means the
   archive's strong lines already argue $\rho$ is not small. What no static
   bound covers is a *drifting* overlap within a scan (mirror tilt is the
   sensitive axis; the longitudinal placement is forgiving to tens of cm),
   which is skew-like. A fixed-lock session measures $\rho$ in situ per configuration
   (PLAN §8.1).
6. The non-monotonicity is laser drift, not a temperature-correlated *rate*
   artifact (block rates scatter only $0.6$% ($\approx0.03$ MHz) on a 5 MHz line).
7. $N(T)$ correlation + a possible cell cold spot affect only *absolute*
   scales, not the *shape* of $N(T)$.
8. Discards and quarantine are curation-time (pre-analysis) decisions, audited
   symmetrically, so they cannot bias the fits.

---

## 7. Where this can go next

*Archival: done conditional on $w_0$.* Every archival module (M0–M8) is built,
tested, and reported in [§5 — What we found (2025 archive)](07_what_we_found.md) — collisional bound + isotope test, laser-epoch
bound, power/ramp-law predictions, trapping, and the cusp model-form study.
What is left is not more archival analysis but the measurements the 2025 data
physically cannot yield — first among them the $w_0$ knife-edge on which every
absolute scale above rests.

*A fixed-lock session — the measurements that lift the bounds* (full
time-budgeted design: **PLAN §8**). Power is capped at
225 mW, so the intensity axis comes from the **beam waist instead**
($I\propto P/w_0^2$; a telescope unclips the EOM aperture and two working
waists, 60 µm and 16 µm, span a $\times16$ intensity range at fixed power).
Headline shots: the AC-Stark shift coefficient with the intensity axis
anchored by the *differential transit width* (knife-edge-independent); the
ramp-law **moment hierarchy** ([§2.6 — The AC-Stark ramp](03_the_ac_stark_ramp.md)) including the predicted **skewness sign
flip** between the two waists; $\beta_\text{self}$ measured — not bounded —
which the collision-rate literature says requires the **150–170 °C**
extension (expected $\beta\sim1$ kHz per $10^{12}$cm$^{-3}$, see
`docs/LITERATURE.md`); the Lehmann cusp in the cold-dim small-waist corner;
the knife-edge $w_0$ itself. Wavemeter calibration is folded in as a
byproduct (PLAN §7): the atoms ($\sim$ kHz) calibrate the wavemeter
($\sim$ 10 MHz), not the reverse.

*Paper 2 (nanofibre / ONF):* the same ramp law tested at the fibre; a
trajectory Monte-Carlo of the published pushing dip; the pulse-duration kill
test.

---

---

[← What we found (2025 archive)](07_what_we_found.md) · [methods index →](../methods.md)
