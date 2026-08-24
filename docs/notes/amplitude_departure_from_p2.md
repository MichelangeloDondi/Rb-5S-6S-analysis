# The amplitude departs from the square-of-power law, and the departure is a detection signature

Status: MEASURED and replicated across two independent sessions, mechanism
unattributed, 2026-08-18. Nothing in `results/` moves. The campaign slopes
quoted here are the record's own committed values, tested against 2 rather
than described as a band. The rehearsal and pilot are outside the frozen
archive, and each use below says so.

`provenance: results/stark_joint.csv` - The page's own status line says nothing in `results/` moves and that the campaign slopes quoted here are the record's own committed values, tested against an exponent of 2 rather than derived afresh. It cites `stark_joint.csv` and 17 of its 25 three-significant-figure values appear in committed CSVs. **8 numeric claims on this page remain unaccounted for.** Declared after checking every three-significant-figure value on the page against `results/`, not by labelling.


## What was claimed, and what testing it showed

The record states that the two-photon amplitude scales as the square of the
power, supported by log-log slopes of 1.83 to 2.12 across the four hyperfine
lines, with only the low line flagged. Those slopes carry errors and were
never compared with 2.

The comparison has to respect one feature of the campaign that the record
documents elsewhere: **the power descends with time**, so power and
acquisition order are collinear, and section C3e records that this same design
once produced an apparently significant AC-Stark pull on a sibling channel
which a block bootstrap collapsed to consistency with zero.

| line | slope | block bootstrap, 95 per cent |
|---|---|---|
| 993.4121 nm | 1.831 | 1.750 to 1.897, excludes 2 |
| 993.4154 nm | 2.121 | 2.104 to 2.142, excludes 2 |
| 993.4192 nm | 2.116 | 2.073 to 2.204, excludes 2 |
| 993.4207 nm | 2.100 | 1.986 to 2.269, includes 2 |

Three of four exclude 2. The fourth loses its within-cell significance of 10.6
once the between-block term enters, which is the design effect C3e documents,
and the test removing one line from the claim is the test working.

## The archive contains its own control, and the departure survives it

Two further power ladders exist outside the frozen archive, both already read
by the joint light-shift fit: the 2025-07-04 rehearsal at 90, 180 and 270 mW,
and the 2025-07-17 pilot at 210, 35, 70 and 105 mW. They are excluded from the
frozen record for epoch and instrument reasons rather than for any data
defect, and that standing is stated here because a claim rests on them.

**The rehearsal ran its ladders in alternating directions**, 4192 descending
while 4207 and 4121 ascended, inside one session on one scope at one gain with
one alignment. That varies the acquisition ordering while holding everything
else fixed, which no other comparison in this archive can do.

| peak | direction | exponent | between-block |
|---|---|---|---|
| 4192 | descending | 2.244 | 5.2 |
| 4207 | ascending | 2.228 | 3.2 |
| 4121 | ascending | 2.070 | 1.8 |

All three exceed 2, and the descending peak sits inside the range spanned by
the two ascending ones. **The departure is therefore invariant under
acquisition order**, which excludes the whole class of order-dependent causes,
drift and hysteresis and detector settling and baseline memory alike. The
conclusion does not rest on the session's one damaged cell: the two ascending
peaks carry five usable traces at every power and show the departure alone.

## The structure: a reproducible pattern plus a session offset

Across the two sessions that share three peaks the ordering is identical, a
rank correlation of 1.00, and the gap between the top two peaks is 0.016 in
both. The whole set shifts by 0.165 between sessions.

    exponent = a reproducible peak pattern + a session offset

## What the pattern follows, and it is not an atomic quantity

    by hyperfine branching, high to low : 4121, 4154, 4192, 4207
    by brightness,          dim to bright: 4121, 4207, 4154, 4192
    by exponent,            low to high  : 4121, 4207, 4192, 4154

**The exponent follows the brightness order, not the branching order**, at a
rank correlation of 0.80 on the campaign's four lines and 1.00 on the
rehearsal's three. Brightness is a property of how much signal a line delivers
into the detection chain, and branching is a property of which line it is, so
the departure is a signature of the detection of the line rather than of the
transition.

## What is not explained

A single additive baseline error does not account for it, since that produces
a deviation of fixed sign shrinking with brightness, and the observed
deviation grows with brightness and changes sign between sessions. The
session offset has no candidate at all. The committed per-chain detector
saturations differ by one per cent, far too little to carry a shift of 0.165,
and the gain is recorded exactly once in the entire programme, in the
rehearsal's filenames, so a gain explanation is not determinable from the
record.

## What would settle it

A measured detector response curve, an afternoon with a calibrated source,
which converts the leading candidate from an argument into a measurement.
Alongside it, a power ladder acquired in interleaved or randomised order
rather than monotonically, which the repaired cavity lock and the four-peak
LeCroy acquisition now make straightforward, and which would remove the
power-time collinearity from the next campaign at the source rather than
correcting for it afterwards.
