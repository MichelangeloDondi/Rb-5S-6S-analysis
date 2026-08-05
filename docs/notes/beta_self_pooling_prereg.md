# Pooling the self-broadening slope: specification before code

Status: pre-registered 2026-08-04, before any pooled number was computed.
Owner's question of record: "are you sure that we should have 4 different
fits? I would do only one joint fit, or at most one for each isotope."
The construction below was fixed after a three-referee verification
(collision physics, estimator statistics, dependency plumbing) and before
`scripts/run_beta_self.py` was touched. The pooled code runs only after this
note is committed.

## 1. The physics that licenses one shared slope

The four 993 nm lines are hyperfine components of one dipole-forbidden
transition, and the broadening they see from ground-state Rb is R^-6
physics. Three statements carry the licence, each checked adversarially:

1. There is no first-order resonant exchange term of the D-line type. The
   5S-6S transition dipole is zero by parity, the electronic quadrupole
   vanishes between two J = 1/2 states (rank 2 exceeds 2J), and the magnetic
   channel sits thirteen orders below the van der Waals term.
2. The R^-6 exchange contribution is large (the referee estimates about 0.7
   of the direct term through the dominant intermediate channel) but
   isotope-blind: the collision is sudden with respect to the 99.2 MHz
   5S-6S isotope shift by a factor of order 300, so the exchange operates on
   effectively degenerate pair states for both isotope pairings.
3. What survives is kinematics. With natural abundance the reduced-mass
   velocity factor puts the 87 radiator 0.35 per cent below the 85 radiator,
   and hyperfine structure enters below 0.2 per cent. Both sit three orders
   of magnitude under the present slope sensitivity.

So the model ladder is decided by physics, not by fit statistics: one shared
slope for all four lines, per-line floors. The per-isotope split is demoted
from a fit structure to a consistency check with an expected null. The
sharing-comparison numbers (the BIC idiom of the archive) are reported as a
check on the data, never as the licence.

## 2. The estimator, fixed in advance

The design is balanced, four lines by four conditions, so the pooled
generalized-least-squares slope collapses exactly to a floor plus slope fit
of the four condition-mean widths. The referee verified the identity
numerically on the committed tables. The pooled variance is

    V = s_c^2 + s_ind^2 / 4

where s_c is the condition-common component of the between-block scatter and
s_ind the per-line component, separated by restricted maximum likelihood on
the sixteen points, with the effective degrees of freedom of V by
Satterthwaite and the one-sided bound quoted at t(0.95, dof_eff). Both
variance components and the common-mode fraction f = s_c^2 / (s_c^2 +
s_ind^2) are reported beside the bound.

What this buys, stated before running: the gain over the worst per-line
bound is 2 / sqrt(1 + 3 f) from pooling plus the t relief from the larger
effective dof. On the committed tables the referee brackets the net gain at
1.1 to 1.8, centre near 1.5. The naive sqrt(4) times t-relief figure of
about 3 is wrong, because the between-block scatter that dominates the error
is strongly shared across the four lines (residual correlations of +0.98 and
above among three of them). Four conditions cannot pin f, so the quoted
bound uses the REML point value and the profile range of f is printed
beside it.

## 3. The verdict is frozen at bound

The measurement-versus-bound rule asks whether the drift probes bound the
drift contribution to at most one third of the observed trend. Temperature
is monotone in time across the campaign and the four lines of one condition
sit within about an hour of each other, so a slow drift enters all four with
the same sign and nearly the same size. Pooling divides that term by exactly
one. A pooled signal-to-noise may therefore cross thresholds that the
confound analysis has not moved at all, and any verdict flip produced that
way would be noise dressed as physics. The pooled result is quoted as a
BOUND for this release regardless of its signal-to-noise, by this amendment.
The known weak-trace narrowing of the 70 C points steepens the pooled slope
in the conservative direction and its share of the pooled slope is computed
and printed by the implementation, not typed here.

## 4. Scope, and the pole dependency that sets it

Two products exist and only one changes.

* `results/beta_self_probe.csv`, the model-independent width-slope bound
  that fig19 panel 1 draws and the documents quote: THIS pools.
* `results/beta_self.csv`, the per-line model fit whose values the M23 and
  M28 joint fits consume as a fixed prior at fit time: UNTOUCHED this
  release. Changing it after the poles finish would silently stale both
  (the plumbing referee confirmed neither pole reads the probe file, and
  M25 frees the coefficient itself and depends on neither). Sharing the
  slope inside the model fit is legitimate future work priced at a full
  pole re-run, and it is recorded here as not done.

## 5. Predictions

1. The pooled 95 per cent bound lands below the worst per-line bound and
   above one quarter of it.
2. The four per-line slopes are consistent with the shared slope within
   their own errors, and the per-isotope split is consistent with zero.
3. The pooled bound's fractional gain over the worst per-line bound falls
   inside the pre-stated 1.1 to 1.8 bracket.

If prediction 1 or 3 fails, stop and escalate to the owner before anything
is written. If prediction 2 fails, that is a finding about a per-line
systematic (the cross-line consistency probe exists for exactly this) and
it goes to the owner with the pooling left unadopted.

## 6. Sequencing

The recompute of 2026-08-04 runs to completion on the four-fit construction
first, and its pre-registered predictions are checked on that construction,
so the pooling never contaminates the six-tooth correction's own audit
trail. This note is committed with that recompute. The pooled construction
is implemented and run only after both, in its own commit, and fig19's first
panel then draws one shared line per the owner's decision with the per-line
floors it already shows.

## Adjacent findings recorded for separate adjudication, not acted on here

* The van der Waals anchor bookkeeping: the referee argues the impact phase
  is set by the difference of upper- and lower-state coefficients, so the
  anchor ratio should use Delta C6 = C6(5S+nS) - C6(5S+5S), moving the 6S
  anchor from 3.53 to 3.38 kHz per 10^12 cm^-3, inside its quoted error.
  To be adjudicated against `rb5s6s/vanderwaals.py` on its own evidence.
* The 6S to 4D interval is 777 inverse centimetres, under three thermal
  quanta at 400 K, so collisional transfer is an open inelastic channel and
  a candidate for any measured slope above the elastic anchor. It is
  isotope-blind and cannot break the sharing. A literature and modelling
  note, not a pipeline change.
