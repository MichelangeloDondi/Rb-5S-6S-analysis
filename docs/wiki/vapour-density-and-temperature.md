# Vapour density and temperature

*[wiki index](README.md) · concept*

**The question.** How a cell temperature becomes a number density, why a set
point is not a temperature, and what an unmeasured temperature costs every
density-linked quantity.
**Takes.** A vapour-pressure curve and a cell.
**Gives.** The conversion, its steepness, and the in-situ measurement that
replaces an adopted number with a measured one.
**Skip if.** The question is what density does to a lineshape once you have
it, which is [self-broadening](self-broadening.md).

> **Unfamiliar with the vocabulary?** [GLOSSARY.md](../GLOSSARY.md)
> defines every term and symbol used anywhere in this repository.

## What it is

A vapour cell holds a reservoir of liquid or solid metal in equilibrium with
its vapour. The vapour pressure follows an Antoine-type law,

$$\log_{10} p = A - \frac{B}{T},$$

so the number density $n = p / k_B T$ rises very steeply with temperature. For
rubidium near 400 K a ten kelvin change moves the density by roughly thirty
per cent. **Density is the lever every collisional measurement runs on**, and
it is also the quantity most easily got wrong, because the thing that is easy
to read off the apparatus is not the thing the formula wants.

## A set point is not a temperature

This distinction has already cost this record twice, and it is worth stating
in its own section.

A variac setting, a controller dial and a heater current are all SET POINTS.
They determine the temperature only through the oven's own transfer function,
which depends on ambient conditions, on the cell's thermal contact, and on how
long the system has been running. Two labels in this archive that read like
temperatures, `91c` and `(90C-0.65A)`, are variac set points, and the internal
temperature they produced is a different number.

The consequence is not cosmetic. The 2025-07-17 pilot's internal temperature
is carried as a RANGE, 110 to 130 C, because that is what the record supports.
Through the vapour-pressure curve that range is **a factor of 3.2 in number
density**, and every quantity that divides by density inherits it.

Three failure modes follow, and they are distinct:

**The reading is a set point.** The number is not a temperature at all.

**The reading is a real temperature somewhere else.** A thermocouple on the
oven body, on the cold finger, or on the cell wall each measure a different
thing, and the vapour density is set by the COLDEST POINT in the cell, since
that is where the reservoir equilibrates.

**The cell has a gradient.** One number then describes a distribution, and the
density along the beam is not the density at the sensor.

## The in-situ measurement that removes the problem

The Doppler pedestal of the two-photon line carries the temperature directly.
Atoms moving along the beam see the two counter-propagating photons shifted in
opposite directions, so the Doppler-free peak sits on a pedestal whose width
is the one-photon Doppler width,

$$\Delta\nu_D = \frac{\nu_0}{c}\sqrt{\frac{8 k_B T \ln 2}{m}},$$

which depends on temperature and on nothing else that is unknown.

The arithmetic of using it as a thermometer is modest. Because the width goes
as $\sqrt{T}$, a fractional width error is HALF the fractional temperature
error, so

$$\frac{\delta T}{T} = 2 \frac{\delta(\Delta\nu_D)}{\Delta\nu_D}.$$

Resolving 20 K near 400 K, a five per cent temperature determination, asks for
a width fit good to 2.5 per cent. That is undemanding for a fit, and it costs
one wide slow scan per temperature block.

Two things can defeat it, both worth stating rather than discovering: the
pedestal may not separate cleanly from scattered light, and the pedestal area
ratio is flat in the retro-reflection ratio near one, so an area-based
estimator loses sensitivity exactly where the geometry is best.

## What can go wrong

**Quoting a set point as a temperature.** Covered above, and it is the
commonest.

**Using the mean of a gradient.** The vapour equilibrates at the coldest
point, not the average one, so a gradient biases the density downward
relative to a mean-temperature estimate.

**Forgetting that the exponential amplifies everything.** A five per cent
temperature error is not a five per cent density error. Through the
vapour-pressure law near 400 K it is closer to fifteen.

**Treating the density uncertainty as independent between conditions.** A
systematic error in the temperature scale moves every condition the same way,
so it does not average down across a temperature sweep, and a fit that treats
it as random will report an interval that is too small.

## Where this is used

The density conversion enters the self-broadening channel and the trapping
channels. The pedestal thermometer is set out as a campaign lever in
[the acquisition settings chapter](../plan/07_acquisition-settings.md), and
its cost and failure conditions are carried in
[the sizing chapter](../plan/06_sizing-and-spending-rules.md).

---

[← Collisional self-broadening](self-broadening.md) · *Experimental spectroscopy, 9 of 9* · [wiki index →](README.md)
