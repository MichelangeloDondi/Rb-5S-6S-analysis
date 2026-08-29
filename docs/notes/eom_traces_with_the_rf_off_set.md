# What the EOM traces add when fitted with the RF-off set

Status: OPEN, scoped 2026-08-10. Nothing here is a result. It records what the
RF-on traces are, what combining them with the RF-off set can and cannot buy, and
one test that tonight's saturation work makes newly decisive. The joint fit itself
is not built.

`provenance: DESIGN` - Its own status line is OPEN and scoped, and says plainly that nothing here is a result and the joint fit is not built. The page quotes the record rather than producing numbers. An untagged number here is a claim to check, not a checked one.


## The census, which corrects a docstring

| role | n | temperature | power | comb |
|---|---|---|---|---|
| p_sweep | 101 | 130 C | 25 to 225 mW, recorded | RF off |
| t_sweep | 62 | 70 / 90 / 110 C | 225 mW, recorded | RF off |
| ruler_t | 61 | 70 / 90 / 110 C | **not recorded** | RF on |
| ruler_p | 44 | 130 C | **not recorded** | RF on |

`run_global_dataset_fit.py` says "ruler_p stays out: its power setting was never
recorded", which is true, but ruler_t's is not recorded either. ruler_t is usable
because the temperature ladder ran at one fixed power, so its power is fixed by
the ladder rather than by its own row. ruler_p sits at 130 C, which is exactly
where the power lever lives, and that is why its missing power matters.

## The brackets were taken at one power, not at the ladder's ends

ruler_p is 23 traces marked `before` and 21 marked `after`, at block sequence 0
and 6, so they bracket the whole ladder for each peak rather than any individual
rung. That leaves their power to be inferred. The total comb area, integrated
above baseline over the whole record, settles it:

| peak | before | after | ratio | implied power ratio |
|---|---|---|---|---|
| 4121 | 27.0 +/- 4.6 | 28.2 +/- 2.5 | 0.96 | 0.98 |
| 4154 | 75 +/- 12 | 70 +/- 14 | 1.06 | 1.03 |
| 4192 | 85 +/- 19 | 136 +/- 36 | 0.62 | 0.79 |
| 4207 | 44.3 +/- 7.2 | 36.6 +/- 5.3 | 1.21 | 1.10 |

Three of four agree inside one standard error and the fourth at about 1.3, so
**the rulers were recorded at the same power before and after the ladder**, not at
its first and last rung. The consequence is negative for the obvious hope: the 44
traces do not span a power range and cannot supply a power lever by themselves.
What they can supply is one additional rung, if that common power is calibrated,
and 44 traces of core-width statistics at the temperature where the power lever
needs the core pinned.

## The test tonight's work makes decisive

The record already reports an unexplained disagreement: the RF-on blocks prefer a
collisional width of 0.4 to 0.7 MHz at 110 C where the RF-off campaign implies
about 0.17 MHz at the fitted coefficient, a factor of three, carried as a stated
systematic with the cause listed as EOM phase noise, a different saturation
regime, or velocity-class selection.

**Saturation is now excluded, and by its sign.** The EOM splits the drive among
seven teeth with the carrier deliberately suppressed, so each tooth drives with a
small fraction of the total power. The saturation parameter goes as the square of
the intensity, so a tooth carrying a seventh of the power saturates roughly fifty
times less than the unmodulated beam at the same total power. Saturation
broadening therefore predicts the RF-on cores to be narrower than the RF-off
cores. They are three times wider. A candidate that predicts the opposite sign of
the observed effect is not the explanation, which leaves EOM phase noise and
velocity-class selection, and those two are distinguishable: phase noise adds
laser width and should scale with the RF drive amplitude, while velocity-class
selection depends on the tooth spacing against the Doppler width.

That is the first thing the combined fit should be asked, because it decides
whether the ruler traces' cores may be pooled with the campaign's at all.

## What a combined fit would have to do, in order

1. Calibrate the ruler power from the comb area against the RF-off amplitude law
   at 130 C, whose log-log slopes are 1.83 to 2.12 rather than exactly 2, so the
   calibration carries that spread as a systematic rather than assuming a square.
2. Settle the RF-on core question above. If the cores do not agree after phase
   noise is given its own width parameter, the ruler traces contribute frequency
   calibration and lineshape shape but must not contribute the collisional width.
3. Only then pool. What that buys is not a new lever but a better-pinned core at 130 C,
   which is the nuisance the width-channel Stark bound is limited by, and 44
   traces at seven teeth each is a large amount of shape information at exactly
   the condition that matters.

## What this does not do

It does not revive the centre channel.
[centre_channel_cannot_be_revived.md](centre_channel_cannot_be_revived.md) shows
every session lacks a knob-independent frequency origin, and the comb does not
supply one: its teeth locate the line relative to itself, since all seven replicas
are the same transition and shift together under a light shift. The comb fixes the
scale of a trace's frequency axis, which it already does, and not its origin.
