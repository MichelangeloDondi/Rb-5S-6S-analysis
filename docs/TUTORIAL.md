# Tutorial: build a digital twin of your experiment

*[START_HERE](../START_HERE.md) · guide*

**The question.** Can you find out what your experiment will measure before
you build it, and can you trust the answer?
**Takes.** A transition you care about and a rough idea of your apparatus.
**Gives.** A digital twin: software that generates the data your instrument
would record, fits it the way your analysis would, tells you which parameters
are degenerate, and forecasts the precision you can reach.
**Skip if.** You want the rubidium result rather than the method, which is
[RESULTS.md](RESULTS.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](GLOSSARY.md) defines
> every term and symbol used anywhere in this repository.

## What a digital twin is, and why it is the point

The same forward model that FITS data can GENERATE it. That single fact turns
an analysis package into a design instrument: an experiment that does not
exist yet can be run in software, its data collected, its analysis rehearsed,
and its achievable precision read off, before a single optic is mounted.

The loop this tutorial teaches is the whole method:

    choose the experiment -> simulate -> fit -> find what is degenerate
        -> change the measurement -> forecast again

Every chapter below is one step of it. The code blocks are all in
`examples/tutorial_forecast.py`, which runs from a bare clone with no data.

## 1. Install, and the five-minute check

```
pip install -e ".[dev]"
pytest -q
python examples/synthetic_recovery.py
```

The third command is the package proving itself: it builds a line whose
answer it already knows, fits it, and reports whether every parameter came
back within its own uncertainty. **Run it before you trust anything else
here.** A package that cannot recover a known truth has no business
forecasting an unknown one.

## 2. Describe your line

One dictionary holds everything the model needs. `examples/your_line.ipynb`
carries the same one with plots attached, and is worth opening beside this.

```python
YOUR_LINE = {
    "name":           "my transition",
    "gamma_coll":     0.5,   # MHz FWHM, collisional at your density
    "sigma_laser":    1.5,   # MHz FWHM, laser width (x2 if two photons, one beam)
    "transit_fwhm":   1.8,   # MHz FWHM, from your beam waist and temperature
}
```

Where these come from in a real laboratory: the collisional width from your
vapour density and a literature coefficient, the laser width from your lock,
the transit width from your waist through
`rb5s6s.transit_fwhm_from_w0`. None has to be right yet. The point of a twin
is to ask what happens if they are.

## 3. Generate the data your instrument would record

```python
from rb5s6s.forecast import synthetic_traces

freqs, volts = synthetic_traces(
    YOUR_LINE["gamma_coll"], YOUR_LINE["sigma_laser"], YOUR_LINE["transit_fwhm"],
    span_mhz=60.0, n_points=2000, n_traces=5, noise=0.004)
```

`noise=0.004` is the simple mode: Gaussian, a fraction of the peak. Real
detectors are not like that, and when you have measured your own noise you
pass the law itself:

```python
from rb5s6s.noise import condition_noise_model
law = condition_noise_model(your_real_traces)      # variance against signal
freqs, volts = synthetic_traces(..., noise=law)     # simulate under YOUR detector
```

That is the difference between a toy and a twin. The twin simulates under the
noise you actually have.

The generator also takes the LASER KERNEL, which matters if the quantity you
are after is the kernel itself rather than a width measured through it:

```python
freqs, volts = synthetic_traces(
    gamma_coll, sigma_laser, transit_fwhm,
    laser_kind="gaussian",   # the Gaussian component, slow frequency noise
    gamma_l=0.0,             # a LORENTZIAN laser component, fast noise
    noise=0.004)
```

`gamma_l` defaults to zero and that default is bit-identical to the generator
without it. Setting it emits a line whose laser kernel is Gaussian and
Lorentzian at once, which is what lets a twin ask whether YOUR analysis can
recover a Lorentzian laser component from YOUR design. One warning the twin
will hand you if you try it at a single condition: it cannot. A Lorentzian
laser width and the collisional width add exactly, so only their sum is
identifiable there. The lever is a DENSITY LADDER, and
`fit_beta_self(..., fit_gamma_l=True)` across temperatures is where the
separation actually happens.

## 4. Fit it back, and check the recovery

```python
from rb5s6s.linefit import fit_condition
res = fit_condition(freqs, volts, T_C=130.0, transit_fwhm=YOUR_LINE["transit_fwhm"])
pull = abs(res["gamma_coll"] - YOUR_LINE["gamma_coll"]) / res["gamma_coll_err"]
```

`T_C` is the cell temperature in degrees Celsius. The fit needs it because
the transit width depends on how fast the atoms cross the beam, which depends
on their thermal speed. Pass the temperature your own cell actually sits at,
and pass `transit_fwhm` explicitly as above if you would rather hold the
transit width fixed than let the temperature set it.

**The discipline that matters: judge the fit by its PULL, not by its residual
plot.** A pull under about three says the fit recovered the truth within the
uncertainty it claims. A small residual with a pull of ten means the fit is
confidently wrong, which looks better on a plot and is worse.

## 5. Find what is degenerate, by breaking it on purpose

Run chapter 4 and look at `res["corr_laser_coll"]`. It will be around
**-0.9**. That number is the tutorial's real lesson: the laser width and the
collisional width are strongly anticorrelated, so the data constrain their
SUM far better than either alone, and a fit can trade one against the other
almost freely.

Now break the package deliberately. Each of these teaches what honest failure
looks like:

| what you change | what should happen |
|---|---|
| `n_points=50` | errors grow, the fit still recovers, the pull stays sane |
| noise x10 | errors grow proportionally, and the pull does not |
| `sigma_laser` and `gamma_coll` both near 1.0 | the correlation approaches -1 and the individual errors blow up |
| a wrong `transit_fwhm` | the other widths absorb it and the pull on them goes bad |

**A package that fails honestly reports larger errors and a warning
correlation. A package that fails dishonestly reports the same small error
and a wrong number.** Check which one you have before you believe a forecast.

## 6. Change the measurement, and learn what does not work first

This is where a twin stops being a demonstration and starts being a design
tool, and the first thing it will tell you is unwelcome.

Run the same fit with a five times wider span, then with ten times the
traces. **The correlation barely moves.** Widening the span from 60 to 300
MHz takes it from -0.9177 to -0.9166, which is nothing at all, and ten times
the traces reaches only -0.881, while both uncertainties shrink throughout. That is the twin telling you something the residual
plots never would: **the degeneracy is a property of the lineshape, not of how
much data you collect.** A Lorentzian core convolved with a Gaussian looks
almost the same when you trade a little of one width for a little of the
other, and no amount of the same measurement distinguishes them.

You break it by measuring one side somewhere else. For a pair with
correlation $\rho$, learning one parameter exactly reduces the other's
variance to $(1-\rho^2)$ of its joint value, so the uncertainty falls by

$$\sqrt{1-\rho^2}.$$

```python
from rb5s6s.forecast import external_constraint_gain
external_constraint_gain(-0.918)     # -> 0.397
```

At this correlation an independent laser-width measurement is worth a factor
of **2.5** on the collisional width, and the twin has just shown that
scanning wider and longer is not. That is the whole argument for putting an
independent linewidth measurement near the top of a campaign plan, and it is
an argument you can now make with a number instead of an intuition.

## 7. Forecast your own experiment

```python
from rb5s6s.forecast import forecast_precision

out = forecast_precision(
    truth={"gamma_coll": 0.5, "sigma_laser": 1.5, "transit_fwhm": 1.8},
    design={"n_points": 2000, "n_traces": 5, "noise": 0.004, "T_C": 130.0},
    n_trials=8)
```

You get the median uncertainty the real analysis would report, the
correlation, and a table of measured SCALINGS: what doubling the power, the
repeats or the points actually buys. The scalings are measured by re-running
the study, not asserted from an exponent, because an asserted exponent is a
claim about a regime you may not be in.

Read `out["assumptions"]` before quoting `out` to anyone. A forecast without
its assumptions is a number, not a forecast.

## 8. The worked example: this project's own next campaign

```
python examples/campaign_twin.py
```

That file is this method applied to a real planned experiment: four hyperfine
peaks on one vertical range, a randomised power ladder with session drift,
cascade depletion, saturation companions, an AC-Stark ramp, blackbody
radiation, shot-like noise and twelve-bit quantisation. It does not
illustrate the campaign, it CROSS-EXAMINES it: each layer prints whether the
record's claim about that layer survives its own simulation.

When it was first
written, its author claimed the campaign's centre channel would detect the
predicted light shift. **The twin refused, at minus zero point eight sigma
with drift present, and the repository's own module M21 turned out to have
said the same thing first: the centre channel cannot measure the pull.** The
twin contradicted its author and sided with the record. That is what a twin is
for, and it is why the loop ends by pointing back at the experiment rather
than at the software.

## Where to go next

[ADAPTING.md](ADAPTING.md) for the seams to change for another species or
geometry. `examples/full_model_tour.py` for the expert modules, cascade
populations, the blackbody boundary and model comparison as an evidence
vector. [The wiki](wiki/README.md) for the physics behind any term here.
