# Adapting this pipeline

The fastest way in: [examples/your_line.ipynb](../examples/your_line.ipynb)
takes a dictionary of your transition's numbers and shows your composite
line, the light-shift distribution your light geometry implies (focused
beam, nanofibre evanescent field, hollow-core mode, or your own sampled
profile), and the observable line with the shift folded in. GitHub renders
it with the plots embedded.

The analysis is a library (`rb5s6s/`, installable with `pip install -e .`)
driven by thin scripts (`scripts/run_*.py`). It was built for one campaign
on one transition, but its parts separate along clean seams, and this page
names them for anyone pointing the machinery at a different line, a
different species, or a different light geometry. The test battery
(`pytest --runslow`, see CI) pins the behaviour of every part named below,
so an adaptation that breaks an assumption fails loudly rather than
silently.

## The seams

| you want to change | you touch | what lives there |
|---|---|---|
| the transition or species | `rb5s6s/constants.py` | line frequencies, hyperfine constants, natural width from the upper-state lifetime, polarizability inputs. Every value carries a provenance tag and a source. |
| the vapour and its density | `rb5s6s/density.py` | the vapour-pressure chain N(T) and its stated systematics. A molecular beam or a buffer-gas cell replaces this file, nothing else reads the vapour law directly. |
| the apparatus | `rb5s6s/config.py` | waists, powers, temperatures, file layouts, directory roots. No physics. |
| the light geometry | `rb5s6s/lineshape.py` | the composite line model and the intensity-distribution machinery. See below, this is the deep seam. |
| the detection noise | `rb5s6s/noise.py` | the measured noise law fitted from repeats, used as fit weights everywhere. Refit it for a new detector, do not guess it. |
| the frequency axis | `rb5s6s/ruler.py` and M2 | the sideband-ruler calibration. Any calibrated axis can replace it as long as each block carries a rate and an error. |

## The deep seam: the intensity distribution

The pipeline's central object is the map from an intensity distribution to
a lineshape. A focused Gaussian beam gives the closed-form geometric
P(I) used here (a triangular light-shift distribution for a two-photon
line, `lineshape.stark_ramp`). Other environments give other P(I):

- a nanofibre evanescent field (radial exponential falloff),
- a hollow-core fibre mode (Bessel-like core profile),
- a lattice or dipole-trap site (harmonic near the centre).

`stark_ramp` and the moment machinery (`ramp_moment_contributions`) accept
the general construction: replace the weight `f(s) ∝ |s|^(n-1)` and its
support with the one your P(I) implies, and the cumulant chain, the joint
fits, and the identifiability tools run unchanged. The n-photon weight
means a one-photon line uses n=1, and molecules with a different
power-scaling of the detected signal change only that exponent.

## What the fit layer assumes

`linefit.fit_condition` fits repeats of one condition jointly: shared
physical widths, per-trace centre, amplitude, and linear background. It
assumes nothing about which atom produced the line. It does assume the
symmetric kernels (Lorentzian, Gaussian, two-sided-exponential transit)
convolved with one asymmetric mechanism. If your system has a second
asymmetric mechanism, add it in `lineshape.py` and extend the model-form
study (M8) so the data get to vote on it.

## The parts that transfer with no edits at all

The statistical machinery is physics-blind: the noise-law fitting (M1),
the identifiability and coverage studies (M12, M13), the BIC model ladder
(M11), the profile-likelihood bound constructions, and the repository
guards (the canonical-value test, the figure fingerprint, the results
status tags). They are the parts most worth stealing, and
`docs/methods/06_the_statistics.md` derives each one.

## A worked example of the whole loop

M23 (`run_stark_joint.py`) is the template for a multi-session joint fit:
sessions with different instruments and different frequency axes, tied by
shared physics, with every nuisance either fitted or bounded and every
robustness check written into the results CSV. Reading it top to bottom is
the fastest way to see how the parts compose.
