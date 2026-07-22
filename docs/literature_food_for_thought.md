# Food for thought — what the pulled papers change

Deep read of `PDF_papers/` (2026-07-12), mined for what actually revises the
analysis, not just what to cite. One headline finding (a confirmed bug + a
revised w₀), plus three smaller refinements. Numbers reproducible from the
papers + the snippets in each section.

---

## 1. The transit MC was wrong; w₀ re-centres from 32 to ~50 µm

**Confirmed by cross-checking against Lehmann's worked example.** Lehmann 2021 works a numerical example (NNO, m=44 u,
w₀=0.90 mm, T=300 K → transit HWHM **41.2 kHz**, vrms 335 m/s). My analytic
transit formula
$$\text{HWHM}_\text{laser}=\frac{v_\text{th}\ln 2}{2\pi w_0},\quad v_\text{th}=\sqrt{2k_BT/m}$$
gives **41.3 kHz** and vrms 337 m/s — a match to 0.2%. So the analytic form is
right, and two independent things follow:

- **Our M9 Monte Carlo (`transit_mc.py`) had one real bug — a missing flux
  factor — now FIXED (2026-07-13).** Lehmann page 6 states the lineshape has a
  *finite cusp* because the crossing flux `v` cancels the `1/v²` of the
  excitation amplitude. The MC sampled `v~Rayleigh` and weighted by `1/v²` but
  omitted the leading flux `v` (Lehmann eq. 6), producing a v-power-−1
  near-log-divergence (bare FWHM ~0.11 MHz) instead of the v-power-0 finite cusp.
  Adding the flux (`amp *= v_perp`) reproduces Lehmann's NNO worked example
  (41.2 kHz) and the analytic `ln2·v_th/(π w0)` to <1%.

- **The correct transit at the nominal w₀ = 32 µm is 1.87 MHz** (bare, transition
  axis, 110 °C) — *half* what an earlier draft of this note claimed (3.85). That
  draft also alleged a second, laser-vs-transition "factor of 2" bug; it was
  **spurious** (the MC's `2π·ν_T` transition-axis convention is correct) and was
  the source of the doubled transit. There is only **one** bug (flux).

- **w₀ is re-centred 32 → 50 µm, not 90.** natural(3.49) ⊛ transit(32 µm, 1.87)
  = 5.64 MHz already EXCEEDS the observed ~5.25 line, so 32 µm is EXCLUDED; the
  width is consistent with **w₀ ≈ 45–70 µm (central 50, floor 38)**. The earlier
  "w₀ ≈ 90 µm" needed the doubled transit and an implausible ~2.3 MHz laser.

**Why this matters (the cascade, corrected):**
- The dominant systematic's central value moves from ~32 µm to **~50 µm** (~1.5×).
- $S_0\propto 1/w_0^2$, so the predicted AC-Stark shift drops by
  $(32/50)^2\approx2.4\times$: $S_0(225\text{ mW})\approx1.43\to0.59$ MHz (not ÷8).
  The archival bound (re-run: 95% $<\sim$0.63 MHz, profile likelihood) still brackets it, now narrowly.
- `TRANSIT_FWHM_PLACEHOLDER_MHZ` is now DERIVED from w₀ via
  `constants.transit_fwhm_from_w0` (≈1.20 MHz at 50 µm); every fit was re-run.

**This propagation is DONE** (`docs/notes/transit_width_resolved.md`): the flux fix +
Lehmann test, the w₀ re-pin, and the C1/C2/C3d re-runs all landed 2026-07-13. The
headline archival results are unchanged in *kind* (model-independent bounds and
nulls, gated on a direct beam-profile measurement); only the w₀-conditional central values
moved (β central ~0.056 → 0.036, σ_laser bound 1.1 → 1.0 laser axis, S₀ pred
1.43 → 0.59).

## 2. Zameroski — the β_self expectation, sharpened (use broadening, not shift)

Zameroski 2014 measures the **7S self-broadening rate = 129 kHz/mTorr** (p.11).
Converting: at 393 K, 1 mTorr ↔ 24.5×10¹² cm⁻³, so
$$\beta_\text{self}(7S)\approx 129/24.5 \approx 5\ \text{kHz per }10^{12}\ \text{cm}^{-3}.$$
Our archival β_self **bound** is 0.2–0.4 MHz = 200–440 kHz per 10¹² cm⁻³ (95%,
t-corrected for the 1-DOF scatter + the 20% density-scale systematic), so it
sits ~40–90× above the 7S self-broadening scale (6S should be similar or a bit
smaller). Refinement for the paper: quote the **self-broadening** coefficient
(what β_self is), not the self-*shift* (−17.8 kHz/mTorr) the memory had used — the
right comparison is broadening-to-broadening. Conclusion unchanged (consistent,
not constraining; the 70–130 °C lever can't reach it → the fixed-lock session's 150–170 °C).

## 3. Grimm & Stalnaker — the ⟨E²⟩ convention and the novelty bound (both hold)

- **Grimm 2000** confirms our S₀ convention verbatim: $\Delta E=-\tfrac14\alpha E_0^2=-\alpha I/(2\varepsilon_0 c)$
  (their oscillator model, §II). No change; it is the right citation for
  `stark_shift_S0_mhz`.
- **Stalnaker 2006** is genuinely the nearest prior art: a spatially-varying
  AC-Stark shift producing an asymmetric lineshape from which α was extracted.
  This *bounds our novelty* (we do not claim the asymmetry's existence) but also
  *supports our method* — it is a precedent for using the shift's spatial
  structure as a measurement channel, in the fringe-averaged FM regime we invoke.

## 4. Lehmann §II — a ready-made tool for the fixed-lock session's saturated Stark regime

Lehmann's saturated-field treatment (his §II) gives the two-photon lineshape
*with* an AC-Stark shift in dimensionless reduced units (reduced Rabi
$\Omega'=\sqrt{\pi/2}\cdot w\Omega_{2p}/v$, reduced shift $\beta=\Delta\omega_{fg}/\Omega_{2p}$).
the small-waist runs are exactly this regime (high intensity, non-negligible
S₀). His reduced-unit lineshape + the numerical integration of
$d\vec r/dt=-\vec\Omega\times\vec r$ is a validated forward model to fit the fixed-lock session's
Stark data against — worth adopting rather than re-deriving. (Also: his 2nd-order
Doppler shift $-\omega v^2/2c^2$ is ~tens of Hz, negligible for us — one less
systematic to worry about.)

---

### Bottom line
The papers did what the archive's own numbers couldn't: they **caught a real bug
in the transit MC** (a missing crossing-flux factor) **and re-centred the dominant
systematic** (w₀ ~50 µm, not the 32 µm nominal — which the corrected transit
excludes), with a clean downstream consequence (the predicted AC-Stark shift is
~2.4× smaller, 1.43 → 0.59 MHz). Everything is confirmed against Lehmann's own
worked example (41.2 kHz, 0.2%). The propagation is DONE (2026-07-13): the fix,
the w₀ re-pin, and every w₀-conditional fit have been re-run.
