*Chapter 8 of 8 · [methods index](../methods.md)*

**The question.** What is everything above resting on, and what would a second
epoch of data lift?
**Takes.** All seven chapters before it, since each assumption belongs to one
of them.
**Gives.** The list a referee should attack first, and the measurements that
would turn the archive's bounds into values.
**Skip if.** Nothing. This is the shortest chapter in the set and it is the one
that says what the other seven are conditional on.

## 6. Load-bearing assumptions (the ones to challenge)

1. Comb teeth spaced $\Omega/2$, not $\Omega$ (everything scales $\times2$ if
   wrong, and it is locked by tests, by the 5-tooth amplitude pattern and by a
   hyperfine label-spacing check).
2. Scope triggered on the sweep sync so file-time $=$ ramp-phase (evidence
   strong, experimenter confirmation pending, and the ramp-monitor export of
   PLAN §3 item 0 would settle it).
3. Kernel *shapes*: laser Gaussian, transit two-sided exponential (the Voigt
   split depends on them). The model-form study ([§4.7](06_the_statistics.md)) confirms the 2025
   data cannot distinguish these forms, so the *shape* assumption is untested
   by the archival data and is among the assumptions most exposed to being wrong until a fixed-lock session is run.
4. The beam waist $w_0=64$ µm is **adopted from the lineage measurement,
   not measured on this bench**. Rajasree 2020 recorded a 128 µm $1/e^2$
   diameter with a beam profiler on the same laser model, the same $f=150$ mm
   lens, the same 130 °C cell and the same $2f$ retro geometry, and Nieddu
   2019 quotes the same number on the older laser. Transferring it assumes the
   2025 alignment matched. Two documented effects push the *effective* waist
   ABOVE 64 µm and neither is fitted: residual clipping at the 3 mm EOM
   aperture, and imperfect superposition of the retro beam. A direct
   beam-profile measurement in a fixed-lock session settles it for this bench,
   and until then every absolute number carries the $w_0$ band.
5. The retro ratio $\rho=0.94\pm0.04$ behind the quoted $S_0$ prediction
   ([§2.6](03_the_ac_stark_ramp.md)) is an **assumption**.
   Until v3.0.0 the code asserted $\rho=1$ on a geometric design argument: the
   2025 retro is self-imaging, L2 ($f=150$ mm) maps the cell waist to a
   about 0.7 mm intermediate waist and a flat mirror at that flat wavefront
   time-reverses the beam, re-forming the original waist, so the
   forward/return *mode match* is by construction. That argument covers mode
   matching and not *loss* (two extra L2 passes, two extra window passes,
   mirror reflectivity), and it does not cover alignment-imperfect
   superposition either. Neither was characterized for the archive, so a
   modest departure is now assumed instead of a perfect retro. The exposure is
   bounded either way: $S_0\propto(1+\rho)$ confines the prediction to
   0.18–0.36 MHz for any $\rho$, and the Doppler-free rate's own
   $\propto\rho$ scaling means the archive's strong lines already argue
   $\rho$ is not small. What no static bound covers is a *drifting* overlap
   within a scan (mirror tilt is the sensitive axis, and the longitudinal
   placement is forgiving to tens of cm), which is skew-like. A fixed-lock
   session would measure $\rho$ in situ per configuration (PLAN §4).
6. The non-monotonicity is laser drift, not a temperature-correlated *rate*
   artifact (block rates scatter only $0.6$% ($\approx0.03$ MHz) on a 5 MHz line).
7. $N(T)$ correlation + a possible cell cold spot affect only *absolute*
   scales, not the *shape* of $N(T)$.
8. Discards and excluded are curation-time (pre-analysis) decisions, audited
   symmetrically, so they cannot bias the fits. **No longer only an argument
   from timing:** all twenty discarded acquisitions now recoverable were tested
   against the kept repeats at their own conditions, and are indistinguishable
   in the *fitted* quantity, the linewidth, even where they are measurably dimmer
   ([PREREGISTRATION_RESULTS.md](../PREREGISTRATION_RESULTS.md) addendum 3).

---

## 7. Where this can go next

*Archival: done conditional on $w_0$.* Every archival module (M0–M30) is built,
tested, and reported in [what we found](07_what_we_found.md): the collisional
bound and isotope test, the laser-epoch bound, the power and ramp-law
predictions, trapping, and the cusp model-form study.
What is left is not more archival analysis but the measurements the 2025 data
physically cannot yield, first among them the beam-profile $w_0$ on which every
absolute scale above rests.

*A proposed fixed-lock session, the measurements that would lift the bounds*
(not yet scheduled or agreed, with the full time-budgeted design at
**PLAN §9**). Power
would be capped at
225 mW, so the intensity axis comes from the **beam waist instead**
($I\propto P/w_0^2$, since a telescope unclips the EOM aperture and two working
waists, 60 µm and 16 µm, span a $\times14$ intensity range at fixed power).
The headline shots would be these.

* The AC-Stark shift coefficient, with the intensity axis anchored by the
  *differential transit width* and therefore independent of any beam-profile
  measurement.
* The ramp-law **moment hierarchy** ([§2.6](03_the_ac_stark_ramp.md)) including
  the predicted **skewness sign flip** between the two waists, conditional on
  the collection geometry, which is unmeasured (PLAN §6 #4).
* $\beta_\text{self}$ measured rather than bounded, which the collision-rate
  literature says would require the **150 to 170 °C** extension. The expected
  value is $\beta_\text{self}(6S) = 3.4 \pm 0.3$ kHz per
  10¹² cm⁻³, the anchor `docs/LITERATURE.md` scales from Zameroski's
  measured 7S rate through the computed C₆ difference ratio, and it is what
  `rb5s6s.vanderwaals.beta_self_anchored` returns.
* The Lehmann cusp in the cold-dim small-waist corner.
* The beam-profile $w_0$ itself. Wavemeter calibration is folded in as a
byproduct (PLAN §11): the atoms ($\sim$ kHz) calibrate the wavemeter
($\sim$ 10 MHz), not the reverse.

*The nanofibre extension, proposed:* the same ramp law tested at the fibre. A
trajectory Monte-Carlo of the published pushing dip, and the pulse-duration
kill test.

---

**Where the numbers live.** Modules M0–M30, the whole archival pipeline ·
producers every `scripts/run_*.py` that writes a committed CSV · results the
full `results/` set, indexed in [`docs/RESULTS.md`](../RESULTS.md) · figures:
none of its own. Each assumption is sourced from the chapter that makes it,
and the forward programme it points at is costed in [`PLAN.md`](../PLAN.md).

**What would falsify this.** A beam-profile measurement returning a waist
outside the 62 to 68 µm band. Assumption 4 is the one every absolute number in
this repository leans on, and a waist measured away from the lineage value
would move the transit subtraction and the Stark prediction together, in the
same direction, without any fit noticing.

[← What we found](07_what_we_found.md) · [methods index →](../methods.md)
