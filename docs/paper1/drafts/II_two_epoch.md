# Paper 1 — §II draft prose: the two-epoch design (methodological spine)

**FIRST-PASS DRAFT** — to be revised with the co-authors. Fills the §II stub of
`PAPER1_SKELETON.md`. This is the paper's conceptual spine; it is framing as much
as fact, so expect it to change most in your revision. Provenance/framing notes
in **[brackets]**, LaTeX inline.

---

## II. The two-epoch design

The problem this paper confronts is absolute-frequency metrology in a system
whose reference drifts. Our 2025 laser lock wandered at of order a megahertz per
minute — slow on the timescale of a single frequency sweep, but large compared
with the sub-megahertz shifts and widths we wish to measure. A naive reading
would discard such data as uncalibrated. The observation behind this
paper is that a slow drift destroys *absolute line centres* but leaves *line
shapes* and *relative* structure intact: within one fast sweep the drift is a
nearly constant offset, so it displaces a trace bodily without distorting it.
What a drifted-lock archive can therefore deliver is everything that
does not require an absolute centre — widths, their scaling with density and
power, amplitude ratios, and the *shape* of the AC-Stark ramp — while everything
that does require a centre, the absolute shifts, is out of reach until the lock
is fixed.

We turn this into an analysis principle by putting each trace's centre in a
free per-scan nuisance parameter (§V.C): the drift is absorbed exactly where it
lives, and the physics is carried by the parameters shared across traces — the
collisional, laser, transit, and ramp widths. This is what makes a
shape-only archive usable rather than merely suggestive, and it is why the
naive alternative of pooling drifted scans onto a common absolute axis
manufactures false detections (§VI.A). [This paragraph is the load-bearing idea
of the paper — worth stating crisply and once, then referring back.]

The archive (**Epoch 1**) accordingly yields the results of §VI as *bounds and
confirmed scalings*: the collisional self-broadening and laser-width bounds, the
power-law confirmations of the ramp model, and the upper bound on the AC-Stark
coefficient. The complementary **Epoch 2** — a fixed-lock campaign (§VII) — is
what converts them into measurements: with the centres alive, the first-order
AC-Stark and collisional self-*shifts* become observable, and a direct beam-profile
measurement of the beam waist sets the absolute scale that every width inherits.

The beam waist is the single systematic that runs through the entire paper. The two-photon beam is focused and retro-reflected
through an electro-optic modulator whose 3 mm aperture clips it, leaving the
waist $w_0$ at the interaction region uncertain at the tens-of-percent level
[OPEN]. Because the transit width scales as $1/w_0$ and the AC-Stark depth as
$1/w_0^2$, every *absolute* width and shift we quote from the archive is
conditional on $w_0$; this is the reason those quantities appear throughout as
bounds rather than values, and why the beam-profile measurement would be the campaign's first
task. The two-epoch design is thus not a workaround for a spoiled dataset but a
deliberate division of labour — the drifted archive establishes the method, the
systematics, and the bounds; the fixed-lock session supplies the absolute
measurements. [Framing: you may want to end §II by
positioning this as a transferable template for metrology in any slowly-drifting
system, or save that for §VIII — your call.]

---

### Facts anchored here (see later sections for the numbers)
- drift $\sim$ MHz/min; sweep fast compared with it → per-scan offset, not distortion
- centres → free per-trace nuisance (§V.C); shared widths carry the physics
- Epoch 1 = bounds + scalings (§VI); Epoch 2 = shifts + absolute scale (§VII)
- $w_0$ OPEN (EOM 3 mm clip, tens-of-%); transit $\propto1/w_0$, Stark $\propto1/w_0^2$ → every absolute is $w_0$-conditional

### Open framing choices for you
- This section can be a short "Principle" subsection of §I rather than a standalone §II — depends how much you want to foreground it.
- The "transferable template" claim (drifted-lock metrology as a general method) is a strong positioning line; decide whether it belongs in the abstract/intro or the conclusion.
- Tone on the drift: "spoiled data rescued" vs "deliberate two-epoch design". The repo's framing is the latter (the archive was always intended to be topped up); state whichever is true to the history.
