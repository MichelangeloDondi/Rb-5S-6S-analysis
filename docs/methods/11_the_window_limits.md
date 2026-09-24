# 11. The window limits

> [GLOSSARY.md](../GLOSSARY.md) states the measurement in six sentences and
> defines every term and symbol used anywhere in this repository.

This page stands on the physics rung, then the mathematical one. The forms below are derived before they are fitted, and the
fit that reads them (`private/cache/plan_2026-09-16/p18_window_limits.py` on the 42 µm surface,
`scripts/run_window_limits.py` once that surface is a tracked result) keeps the exponents the
derivation fixes and frees only the coefficients. A windowed statistic is compared against its own
forward prediction and is never an estimate of the untruncated cumulant (chapter 06). The limits
are where that rule is made quantitative, because a limit is a quantity of the line and a window is
not. The numbers this page's measurements returned are held with their artefacts in the private
finding F148 until the surface and its limits are tracked results, so this page states what they
showed and not their decimals.

## 11.1 The object

The record's windowed cumulant $\kappa_n(W)$ is the $n$-th cumulant of the de-baselined line
restricted to $[\nu_c - W, \nu_c + W]$ and renormalised there, with $\nu_c$ the window's own centroid
iterated to convergence (`rb5s6s.cumulants.windowed_moments`, whose second and third orders equal the
cumulants exactly). Self-centring is what makes the
odd orders a statement about the line's asymmetry and not about where the window was put.

The record's "higher moments" channel is computed as cumulants, and the two differ in a way that
decides signs. An even central moment of a non-negative line,
$\mu_n(W) = \int (\nu - \nu_c)^n f / \int f$ over the window, is positive at every window, always, and
there is nothing to discuss about its sign. A cumulant is a polynomial in the moments,

$$\kappa_2 = \mu_2, \qquad \kappa_3 = \mu_3, \qquad \kappa_4 = \mu_4 - 3\mu_2^2, \qquad \kappa_6 = \mu_6 - 15\mu_4\mu_2 - 10\mu_3^2 + 30\mu_2^3,$$

so from the fourth order up an even cumulant is a difference of positive quantities and carries no sign
constraint of its own. $\kappa_4$ is the excess-kurtosis combination: negative when the truncated line is
flat-topped (platykurtic), zero when its fourth cumulant matches a Gaussian's, positive when heavy wings
dominate (leptokurtic). The rect window's own limit of 11.2, $\kappa_4 \to -2W^4/15$, is the platykurtic
end of exactly that statement.

Measured on three analytic densities at this surface's own windows, every $\mu_2$, $\mu_4$ and $\mu_6$ is
positive at every window while $\kappa_4$ changes sign: for a Lorentzian of half-width 1.75 MHz it is
negative out to 5 MHz and positive from 8 MHz. For a Gaussian it approaches zero from underneath and never
becomes positive. **So the crossing is the object's own algebra, and where it falls moves with the line's
parameters**, which is what makes a window at a crossing a poor place to quote a statistic, and what the
statement that $\kappa_4$ dies near 8 MHz means for this line and this line only.

The record uses central moments from fourth order up, not cumulants (owner order O33, section 11.7
gives the reason). What that costs is the cancellation of section 11.6, and the conditioning number
reported there is how the cost is read.

## 11.2 $W \to 0$: the geometry

For a window narrow against every width in the line, the density inside it is its Taylor expansion
about $\nu_c$, $f(\nu) = f_0 [1 + a_1 u + a_2 u^2 + \dots]$ with $u = \nu - \nu_c$ and
$a_k = f^{(k)}(\nu_c) / (k! f_0)$. Self-centring sets the first windowed moment to zero, which fixes
$\nu_c$ at the stationary point of the local density to order $W^2$, so $a_1 = O(W^2)$ and the
leading term is the rect window's own distribution. The cumulants of a uniform density on $[-W, W]$
are the Bernoulli numbers' series,

$$\kappa_2 = \frac{W^2}{3}, \qquad \kappa_4 = -\frac{2 W^4}{15}, \qquad \kappa_6 = \frac{16 W^6}{63}, \qquad \kappa_8 = -\frac{16 W^8}{15},$$

and every odd cumulant vanishes. The line enters at the next order: the curvature $a_2$ multiplies
each even order by $1 + c_n a_2 W^2 + O(W^4)$ with $c_2 = 2/5$, and the local skew $a_3$ gives
the odd orders $\kappa_3 = \tfrac{8}{175} a_3 W^5 (1 + O(W^2))$ with each higher odd order two
powers of $W$ further down. So the zero-window limit is the geometry of the window, every even order
tending to a known multiple of $W^n$ and every odd order to zero as $W^{n+2}$, and the first
correction is a derivative of the line at its centre.

<!-- C6b: re-measured as a moment (A149) -->
The limit is a self-check of the window
machinery against the model's own derivatives, and it is met: on the noiseless 42 µm surface at the
smallest window, one seventh of the line's width, every one of the 32 conditions reads the rect
window's own cumulant at orders 2, 4 and 6 within a few per cent, the shortfall being the curvature
term, and the odd orders sit at the numerical floor (F148).

## 11.3 $W \to \infty$: the term classes

Write the line as a Gaussian-cored part of unit weight less $f_L$, plus a Lorentzian-winged part of
weight $f_L$ and half-width $\gamma$ (the composite of chapter 04 has this structure: the transit
and the ramp are compact, the collisional and natural widths are Lorentzian).

* **A compact term converges exponentially.** Its truncated moments differ from the full ones by
  $\exp(-W^2 / 2\sigma^2)$ factors, so past three widths every cumulant of the compact part is its
  own untruncated cumulant to any precision the surface carries. For the ramp alone this would be
  the value the record derives, $\mu_3 \to -S_0^3/135$ at weak drive (chapter 03). The third
  bullet says why the whole line does not reach it.
<!-- C6b: re-measured as a moment (A149) -->
* **A Lorentzian wing makes the even orders diverge as powers.** The truncated central moment of a
  Cauchy wing of weight $f_L$ is $m_{2k}(W) = \tfrac{2 f_L \gamma}{\pi} \tfrac{W^{2k-1}}{2k-1} [1 + O(\gamma^2 / W^2)]$
  for $W \gg \gamma$, so $\kappa_2 \sim \tfrac{2 f_L \gamma}{\pi} W$, and
  $\kappa_4 = m_4 - 3 m_2^2 \sim \tfrac{2 f_L \gamma}{3\pi} W^3 - 3 (\tfrac{2 f_L \gamma}{\pi})^2 W^2$, the
  two terms of opposite sign. In general $\kappa_{2k}(W)$ is a polynomial of degree $2k - 1$ in $W$
  whose leading coefficient is $\tfrac{2 f_L \gamma}{\pi (2k-1)}$, so the leading divergence
  coefficient of every even order is **one number**, the Lorentzian weight times its half-width. That is a
  testable invariant, not a channel, and on this record's own surface it does not hold: recovered from
  $d\kappa_2/dW$, from $(d\kappa_4/dW)/W^2$ and from $(d\kappa_6/dW)/W^4$ at the same window it gives
  three numbers a factor of ten apart and of opposite sign, so no even order here is in its asymptotic
  regime and none of them measures $\gamma$. Section 11.5 and the private finding F159 carry the
  measurement. The invariant is kept in the derivation because failing it is how the asymptote was
  refuted.
* **The odd orders of an offset wing do not cancel, and they grow.** A Cauchy wing is even about
  its own centre, but the window is centred on the whole line's centroid, which the ramp displaces
  from the wing's centre by $\delta$ of the order of the shift. The wing's truncated odd moments
  are then $O(f_L \gamma \delta W^{2k-2})$, growing with the window instead of converging, and the
  centroid itself moves with $W$ as more of the asymmetric wing is admitted. So for a line that
  carries both a compact asymmetric part and a Lorentzian wing, the odd orders have no finite
  infinite-window limit reachable through a window, and a form that assumes one reads the
  truncation. The first draft of this page claimed the opposite, and the surface refuted it within
  the hour (11.5).

<!-- C6b: re-measured as a moment (A149) -->
The sign changes the noiseless surface shows are these two limits meeting, read through 11.1's algebra:
at small $W$ the truncated line is flat-topped and $\kappa_4 = \mu_4 - 3\mu_2^2$ is negative, tending to
the rect window's own $-2W^4/15$. At large $W$ the Lorentzian wing makes the line leptokurtic and
$\kappa_4$ is positive, growing as $W^3$. Where it crosses is not one number. Over the 32 conditions of the
noiseless surface, 22 cross between 5 and 8 MHz and 10 between 8 and 13, and the ten are exactly the two
highest drive powers of the power arm: **the crossing walks outward with drive power**, which is the
AC-Stark ramp widening the line and moving the window at which its wings take over. That is the same
statement as the paragraph below, measured and not asserted, and it is why no single interval is quoted
here.

What does hold uniformly across the surface is the conditioning of section 11.6: every one of the 32 conditions
has its worst-conditioned $\kappa_4$ row at 8 MHz, which is why that half-width left the quoted set on the
measured signal-to-noise (the C2 wave, 2026-09-19) and is computed as a diagnostic instead. A statistic at
its own zero has a small value and an undiminished noise, so its signal-to-noise collapses there while the
channel is perfectly healthy a window away.

$\kappa_6$ crosses twice, between 5 and 8 and again between 13 and 21 MHz. **The crossing is not a
property of the window set but of the line**, so it moves with the fitted parameters, and the crossing
itself carries information about the wing weight.

## 11.4 The fit forms, with the exponents fixed

For each statistic the extrapolation model is the sum of the two limits with the exponents the term
class fixes and only the coefficients free:

| order | form fitted to $\kappa_n(W)$ over the surface's windows | what the coefficients are |
|---|---|---|
| even, $n = 2k$ | $\sum_{j=0}^{2k-1} a_j W^j$ | $a_{2k-1} = 2 f_L \gamma / (\pi (2k-1))$ the wing, $a_0$ the compact part's own cumulant |
| odd, $n = 2k+1$ | $c_n W^{p_n}$ over every window, $p_n$ read against the geometry's $n + 2$ | $c_n$ the line's local skew ($\tfrac{8}{175} a_3$ for $\kappa_3$ at small $W$), and a $p_n$ below $n+2$ is the offset wing taking over |

The small window end enters as a constraint, not a fit: the form must reproduce the uniform
cumulant at the smallest window to the curvature correction's size, and a form that does not is
refused before its coefficients are read. Bars come from the surface's replica spread at each window
through weighted least squares (a jackknife over the replica set once the surface carries replicas
rather than their mean and spread), and a free-exponent power law fitted beside the derived form says
whether the derived exponents are what the surface actually shows.

## 11.5 The yield of the limits

<!-- C6b: re-measured as a moment (A149) -->
Measured on the 42 µm surface on 2026-09-19 (F148).

* **The geometry holds everywhere.** On the noiseless surface all 32 conditions meet the rect
  window's own cumulant at the smallest window within ten per cent at every order 2 to 7, the even
  orders a few per cent under it (the curvature term) and the odd orders at the numerical floor.
* **The wing is not read from $\kappa_2$ on this window set, and the claim that it was is withdrawn.**
  A first version of this page reported that the $W \to \infty$ form returned the Lorentzian weight times
  half-width within three per cent of $\Gamma/2$ and called it a channel on $\gamma_l$. The derivative
  refutes it: a Lorentzian wing gives a constant $d\kappa_2/dW$, and the surface's adjacent secants fall
  across the widest three intervals while the local exponent $d\ln\kappa_2 / d\ln W$ falls monotonically
  from the geometry's 2 towards and then below 1. $\kappa_2$ is not asymptotic anywhere on this window set, so a
  leading coefficient fitted across a range that is mostly geometry measures nothing, and the agreement was
  a coincidence of that fit. Two mechanisms do it, both measured on a Voigt line on the archive's own axis:
  the wing baseline this estimator subtracts removes part of the Lorentzian pedestal the limit is meant to
  measure, costing about a seventh of $\kappa_2$ at the widest window. And the trace's finite span
  truncates the tail beyond it. **The standing rule is the one that was broken**. a summary statistic is
  compared against its own forward prediction and does not have to converge to anything. so the channel on
  $\gamma_l$ is the twin's prediction of $\kappa_2(W)$ with the baseline and the grid in it, against the
  archive's $\kappa_2(W)$, which is what the joint fit already does. The account is the private finding
  F151.
* **The zero crossings are derived from 11.1's algebra**, not from an asymptotic story: $\kappa_4$ crosses
  between 5 and 8 MHz and $\kappa_6$ twice, and those are where the surface changes sign.
* **The odd orders have no limit here, and they say so.** Over the whole range from half a
  megahertz to 21 MHz the odd orders grow as powers of $W$ between the small window geometry's
  $n + 2$ and one power below it, for $\kappa_3$, $\kappa_5$ and $\kappa_7$ alike, and the
  $\kappa_n^\infty + b_1 / W + b_2 / W^2$ form fitted past 3 MHz returns numbers two orders of
  magnitude above the ramp's $-S_0^3/135$ with bars of half their size, which is the form reading
  the truncation. **No infinite-window odd cumulant is quoted from this record.** What the odd
  channel measures at any window is the line's local skew scaled by the window, compared, as the
  standing rule says, against its own forward prediction.

## 11.4b The universal ratio at real order

Section 11.2 states three limits as separate constants. They are one curve.

The moment of real order $x \gt 0$ is the absolute moment $\mu_x=\mathrm{E}|\nu|^x$, which is defined
for every real $x$ below the tail index and, inside a finite window, for every $x$. At $W\to0$ any
smooth line is locally flat, so the limit is the rect window's own uniform law, and

$$\frac{\mu_x}{\mu_2^{x/2}} \longrightarrow \frac{3^{x/2}}{x+1}.$$

At $x=4,6,8$ this is $9/5$, $27/7$ and $81/9$, the three constants section 11.2 carries. Checked by
quadrature at nine orders including $3.5$, $4.5$ and $6.5$, it reproduces the closed form to one
part in $10^{10}$. **The acceptance test is therefore a curve and not three points**, and a
harness can be graded anywhere on it.

**Two families, not one.** $\mathrm{E}|\nu|^x$ interpolates the even orders, discarding the sign.
$\mathrm{E}[\mathrm{sign}(\nu)|\nu|^x]$ interpolates the odd ones. The integer sequence is two
interleaved continuous curves. As a function of complex order, $\mu_x$ is the Mellin transform of
the distribution. So the continuous family is the object the integer moments sample.

**What the continuous order buys, and it is not interpolation.** A moment at $4.5$ placed beside
$\mu_4$ and $\mu_5$ adds almost nothing and worsens the conditioning, because consecutive moments
are nearly collinear: that is section 11.7's rule, not an exception to it. What a continuous order
buys is optimisation. $\mu_x$ weights the wings as $|\nu|^x$, so $x$ is a soft control on how much
wing enters where $W$ is a hard one. Each can be loosened to tighten the other. A soft weight carries no
truncation discontinuity, so its bias need not behave like the window's.

**Status: derived and not yet reachable here.** `cumulants.windowed_moments` coerces its orders to
integers, so a fractional order asked of this repository today returns a different moment. The
refusal and the machinery are owed together.

<!-- term-of-art: option pricing and strike price are the finance literature's own names for their subject, not this record's process vocabulary -->
## 11.5b Option pricing over a finite range

Finance meets the same integral over a finite truncation range and treats its error in two named
halves. [Jiang and Tian 2005](../lit/jiang2005.md) separate a **truncation error**, from the range
being finite, from a **discretisation error**, from the grid inside it being finite, and bound each
on its own. Their Proposition 2 makes the first depend on the local variation in the tails, and they
are explicit that the tight form of the bound "are not model free", with a looser model-free bound
derived separately.

**Their two thresholds do not transfer here, and the reason is this page's own subject.** Both are
counted in standard deviations of the distribution being integrated: truncation negligible beyond
about two, the grid fine enough below about a third of one. Section 11.3 shows that a Lorentzian
wing leaves the untruncated even moments divergent, so the line studied here has no standard
deviation to count. A criterion in those units is therefore unavailable, and its unavailability is
the same fact that makes $W$ a designed axis and not an implementation detail.

What does transfer is the model-free bound, and this record does not have one. Every bias
quoted here is the twin's, which is model-based by construction: the twin knows the truth because
the twin generated it. A model-free upper bound on a windowed central moment's truncation error
would be a check on the twin and not an output of it.

And one lever is unexplored. Their asymmetric result -- "With a fatter left tail, a larger range
<!-- term-of-art: option pricing and strike price are the finance literature's own names for their subject, not this record's process vocabulary -->
of strike prices is needed on the left of Fo if we wish to have identical truncation errors from
both sides" -- applies directly: the window here is a symmetric rect while the line is skewed by the
AC-Stark ramp, so the two sides do not carry equal truncation error. An asymmetric window matched to
the line's own skew has never been tried.

## 11.5c Two-window cancellation of the divergence

[Zhang, Mykland and Ait-Sahalia 2005](../lit/zhang2005.md) remove a sampling-induced bias by
evaluating one estimator at two scales and subtracting, "by combining estimators obtained over the
two time scales". Section 11.4 fixes the exponent that makes the same device available here: with
$\lambda = (W_1/W_2)^{n-1}$, the combination $[\mu_n(W_1) - \lambda \mu_n(W_2)]/(1 - \lambda)$
cancels the leading divergence and returns the converged moment, with no twin in the loop.

The normalisation is load-bearing: without the $1/(1-\lambda)$ the combination returns the
converged moment times $(1-\lambda)$. **Status: derived, not measured.** It is algebra on the
asymptotic form of section 11.4 and it assumes that form holds at the two windows chosen, which is
exactly what the twin has to be asked before any number from it is quoted.

## 11.6 The cancellation conditioning

<!-- C6b: re-measured as a moment (A149) -->
From 11.1, $\kappa_4 = \mu_4 - 3\mu_2^2$ is a difference of positive numbers, so near its zero it is a
small difference of large ones. the rule this record already carries for the third moment, applied to
the even orders. The residue that survives the cancellation,

$$\mathrm{cond}_n(W) = \frac{\lvert \kappa_n(W) \rvert}{\lvert \mu_n(W) \rvert},$$

is the statistic's conditioning number at that window: at $\mathrm{cond} = 0.01$ a one per cent error in
$\mu_n$ is a hundred per cent error in the cumulant. The absolute value on the denominator is not
decoration: $\mu_3$ is negative on almost every row of this surface, and a conditioning allowed to go
negative would mark the whole odd channel unquotable.
 
And $\mu_n$ is only one of the inputs, so the number
is a floor on the amplification and not the whole of it: $\kappa_4 = \mu_4 - 3\mu_2^2$ amplifies an
error in $\mu_2$ by about twice as much again, and the higher orders by more. It is computed per (case, order, window) beside every
row, never tabulated once, because it moves with the line's parameters.

On the noiseless surface
$\kappa_2$ and $\kappa_3$ read 1 by construction, being moments. $\kappa_4$'s worst window is 8 MHz, where
its conditioning falls to a few parts in ten thousand across every condition, and $\kappa_6$'s is the
widest window. **That is the whole of the statement that $\kappa_4$ dies at 8 MHz**: not a dead channel but a window at which
the statistic is almost entirely cancellation, so any error in the fourth moment is amplified into it. The
measured signal-to-noise that moved 8 MHz out of the quoted set is this algebra seen through the noise.

What the limits yield, then, is the zero-window geometry as a check on the machinery, the conditioning
number as a reading on where a statistic may be quoted, a reading, not yet a rule, because no producer in this repository admits or refuses on it and the quoted set of `rb5s6s.windows` was chosen on measured signal-to-noise rather than on this. Wiring it is named in the queue, and one refutation: the truncation bias of chapter
06 is not a bias to subtract but the whole of what a windowed odd order is. The route is
`p18_window_limits.py` and `p18_window_derivatives.py` with their artefacts under
`private/cache/plan_2026-09-18/`, whose decimals enter this page when they enter `results/`.

## 11.7 Moments, not cumulants

The record's vector is central moments at fourth order and above (owner order O33, 2026-09-20).
This section argued the other way until that ruling, and the argument is kept below and not
deleted. It is correct about the algebra. It is wrong only about which property this bench collects.

Why the reversal. A cumulant is bought for one thing, additivity under convolution, and this
record collects it nowhere: a truncated window is a multiplication and not a convolution, and the
kernel is inhomogeneous across the illuminated volume at the waist the campaign is aimed at. What is
paid for it is cancellation. $\kappa_4 = \mu_4 - 3\mu_2^2$ is a difference of large numbers, and on a
Lorentzian at a 5 MHz half-window $\mu_4 = 46.75$ against $3\mu_2^2 = 48.66$, so the cumulant is a
four per cent residue of the terms that build it and pays roughly that factor in relative precision
once noise enters. A ratio of two cumulants pays it twice.

The even orders also lose a pole. An even central moment of a non-negative line is strictly
positive, so it has no zero to sit near. A $\kappa_4$ carries no sign constraint and crosses zero.
Measured on this record's own composite at the archive's parameters, $\mu_4/\sigma^4$ runs 2.12, 2.54,
2.77, 3.26, 4.32 across half-windows 3, 5, 6, 8 and 12 MHz and never approaches zero, while
$\kappa_4/\sigma^4$ runs $-0.88$, $-0.46$, $-0.23$, $+0.26$, $+1.32$ and **changes sign between 6 and
8 MHz**. A ratio whose denominator crosses zero inside the quoted window set has a pole there, and
moving to moments removes it instead of guarding it.

Nothing below fourth order moves, since $\kappa_2 = \mu_2$ and $\kappa_3 = \mu_3$ identically, so
the third-order skew channel and everything argued from it stands unchanged. A cumulant is an exact
function of the moments, so it is still computed, and it rides as a DIAGNOSTIC with its cancellation
conditioning $|\kappa_n|/\mu_n$ beside it -- which is the number that explains why a cumulant died at
a window. It gates no cell.

### The argument as it stood

The two objects carry the same information and behave oppositely under the two operations this bench
performs, which is the whole of the matter.

Under Convolution, cumulants add and moments do not. If $S = g * h$ then
$\kappa_n(S) = \kappa_n(g) + \kappa_n(h)$ at every order, while $\mu_n(S)$ is a binomial sum over every
pairing of the two factors' moments. The observed line is a convolution of independent broadening
mechanisms, so in cumulants the forward model is a sum over terms and its Jacobian is readable term by
term. That is why this record fits cumulants.

Under mixture, moments are linear and cumulants are not. If the collected signal is an average of
kernels over a latent variable $\lambda$, written $S(\nu) = \mathbb{E}_\lambda[K(\nu, \lambda)]$, then
$\mu_n(S) = \mathbb{E}_\lambda[\mu_n(K|\lambda)]$ exactly, and no such statement holds for $\kappa_n$.

This bench does Both at once, and that is the source of every difficulty on this page. The line is a
convolution of terms, and one of those terms is a mixture over the collected volume.

### The estimator side

A sample cumulant is a polynomial in the sample moments, so its variance grows faster than any single
moment's. For a near-Gaussian line the variance of the $n\text{th}$ k-statistic carries a leading
$n! \kappa_2^n/N$, so the signal-to-noise of an order falls roughly factorially while the information it
adds falls only polynomially. Section 11.6's conditioning number is the systematic half of the same story
and the per-trace signal-to-noise table is the statistical half. Neither alone decides which orders are
quotable.

The variance above is not the only estimator property at stake. The natural estimator of a cumulant from
finite data carries a bias as well, and above second order the moment-based and the cumulant-based routes
stop agreeing on it, so a moment-based fourth-order estimate can show structure that is not in the signal
at all ([the statistics chapter](06_the_statistics.md) section 5, [sifft2026](../lit/sifft2026.md)). The
same source states that a windowed estimate needs normalisation by the window length, the number of points
and the window coefficients before it is comparable across different window configurations, which is
exactly the comparison the geometry, term-class and yield sections above make at every window and every
noise level.

## 11.8 A truncated window is not a further convolution

The question is worth stating precisely because the wrong answer is the intuitive one.

Truncating at $\pm W$ multiplies the density by a rect, $f_W(\nu) = f(\nu) \Pi_W(\nu) / m(W)$ with
$m(W) = \int_{-W}^{W} f$. Multiplication in frequency is convolution in the Conjugate domain, so the
truncated line's characteristic function is $\phi$ convolved with the rect's transform, a sinc of width
$1/W$. That is the sense, and the only sense, in which a window is a convolution: it convolves the
characteristic function, not the lineshape.

**Three consequences follow, and the first is the one that bites.**

1. **Cumulants do not add under truncation.** $\kappa_n(W)$ of a convolution of terms is not the sum of
   the terms' own $\kappa_n(W)$, because the window is a multiplication in the domain where the terms
   combine additively. The window Mixes the terms. So a windowed cumulant is a statistic of the whole
   line and is never an estimate of any one term's cumulant.
2. **The renormalisation is itself window-dependent.** Dividing by $m(W)$ is nonlinear, so every
   $\kappa_n(W)$ depends on the window through the retained mass as well as through the retained shape.
3. **Therefore the only sound use is forward.** A windowed statistic is compared against the model's own
   windowed prediction, computed by putting the model through the same window. This is the standing rule
   of chapter 06 and section 11.1, and sections 11.2 to 11.5 are what makes it computable: the limits and
   the term-class laws are how a windowed number is read back toward a quantity of the line.

## 11.9 The convolution approximation and its first-order correction

`S = f * L` holds only where the homogeneous kernel is the same at every collected volume element. On this
bench it is not, because both the AC-Stark shift and the transit width are set by the local intensity, and
the intensity varies across the collected volume. The cost is not uniform across orders: the centroid is
immune and the third moment is wrong by about a factor of two at every waist, which
`scripts/run_kernel_inhomogeneity.py` measures.

The exact statement is the law of total cumulance. Write the inhomogeneous part as a mixture over the
collected volume element $\lambda$, with the kernel at that element having mean $m(\lambda)$, variance
$v(\lambda)$ and third cumulant $c(\lambda)$. Then

$$\kappa_2(S) = \mathbb{E}[v] + \mathrm{Var}(m)$$
$$\kappa_3(S) = \mathbb{E}[c] + 3 \mathrm{Cov}(v, m) + \kappa_3(m)$$

and the pattern continues, each order gaining the cross-cumulants of the kernel's own parameters across
the mixture.

The convolution approximation keeps the first and last terms of each line and Drops the covariance.
Writing the line as $f * L$ at one fixed $\bar\Gamma$ asserts that the kernel is one fixed object, which is the
statement $\mathrm{Cov}(v, m) = 0$: that the shift an atom sees and the width it is broadened by are
independent across the collected volume. On this bench they are not independent, they are both monotone
functions of the same local intensity, so the dropped term is not a small residue and its sign is set by
the sign of that monotonicity.

### The first-order procedure

1. **Split the terms by whether their kernel varies.** The natural width, the collisional width at fixed
   temperature and the laser width are the same at every volume element, so they genuinely convolve and
   stay in the cumulant sum. Only the intensity-dependent terms leave it.
2. **Carry the intensity-dependent terms as a mixture and take their moments**, where the mixture is
   linear, then convert to cumulants once at the end. This is where the duality of section 11.7 is used
   deliberately: moments for the mixture, cumulants for the convolution, and the conversion at the seam.
3. **Add the covariance term explicitly.** At third order that is the single number
   $3 \mathrm{Cov}(v, m)$, computed over the same weighted volume the model already integrates for the
   shift distribution. It needs no new parameter and no new measurement: the joint distribution of shift
   and width across the collected volume is already what the forward model constructs.

### The non-cylindrical beam enters as the mixture's own weight

The beam is clipped by the modulator's 3 mm bore and carries $M^2 \gt 1$, so it is not the Gaussian the
convolution form assumes. At first order this does not add a term: it Changes the distribution
$p(\lambda)$ that the mixture above averages over, because what the atoms sample is the intensity
distribution over the collected volume and nothing else. So the first-order correction for a
non-cylindrical beam is to build $p(\text{intensity})$ from the clipped, $M^2$-widened profile the bench
actually has and to re-take the mixture moments of step 2 with that weight, leaving every other step
unchanged.

Two things follow that are worth stating before any number is quoted. The correction is a change of
weight and not of form, so it moves the covariance term of step 3 and the shift distribution's own
cumulants and leaves the genuinely convolving terms untouched. And its size is measured and not assumed:
the bore's departure from a Gaussian is absorbed almost entirely by the fitted waist, which is why a
clipped world fitted with the Gaussian model at a pinned waist leaves a large residual while freeing the
waist takes it back down. The waist is the first-order correction's own sink, and that is the reason this
record treats the waist as the dominant systematic and not as a measurement.

## 11.10 The coordinate catalogue

`rb5s6s/moment_coords.py` extends the windowed moments above into a catalogue of coordinates: the central moments of orders one to twelve at every window, the four owner-named ratios and their independent-replica-pair twins, one window derivative of each parity per window, and a family of tent-window integrals. It is designed and tested on its own, against closed forms and synthetic lines (`tests/test_moment_coords.py`), and nothing here is yet read by a fit. What follows checks the module's own numbers against the literature its selection rule and its coordinate budget rest on, ahead of the wiring that is C6c's own work.

### The admitted set's own conditioning

Rule W1 admits a coordinate at one window by its twin-measured bias against its own replica spread. Read coordinate by coordinate that clause is close to uninformative, because the raw windowed moments are badly conditioned as a group before any bias enters. A real, positive-definite Hankel matrix, exactly what a raw-moment covariance is under a noise variance constant across the window (`Cov(M_i, M_j)` proportional to the integral of `t^(i+j)` over the window), cannot be conditioned below a rate that approaches a factor of about 3.21 per additional order however the underlying measure is chosen, and even the best-conditioned matrix of that class already sits at 147 by order seven and above 1.0e5 by order thirteen ([varah2003](../lit/varah2003.md), its Theorem 2.1-2.4 and Table 1).

The record's own raw windowed moments, orders zero to twelve under a symmetric window and white noise, sit far above even that floor: computed here directly (the closed-form covariance on a symmetric window, transformed with `rb5s6s.moment_coords.monomial_to_legendre`), its condition number is 2.96e8 and its correlation matrix's is 7.86e7.

A bias of one tenth of a standard deviation on each of those thirteen coordinates therefore does not read as one tenth of a standard deviation on the set. Whitened by the covariance's own inverse, that same per-coordinate bias reads a chi-squared `b^T Sigma^-1 b` of 0.031 when its signs align with the covariance's own structure and 5.99e5 at the worst sign pattern of the same per-coordinate size, five orders of magnitude apart for the same nominal bias (computed here with `rb5s6s.moment_coords.whitened_set_bias`). A per-coordinate clause cannot see that spread, so rule W1(a) is read on the admitted set's own whitened bias, against a bound stated once for the whole set, together with the set's own expected null value when the bias and the covariance come from the same `R` replicas, `p / R`: thirteen coordinates over five hundred replicas reads an expected 0.026 (`whitened_set_bias(..., n_rep=500)`).

The remedy is the basis the moments are read in, not a smaller catalogue. In the window's own Legendre basis, the integral of the `k`-th Legendre polynomial against the baseline-subtracted trace, the same white-noise covariance is exactly diagonal, proportional to `2 / (2k + 1)` at order `k` (`rb5s6s.moment_coords.legendre_window_moments`, `monomial_to_legendre`, checked here to a few parts in 1e-10 against that closed form). The two bases carry the same information, related by the exact, invertible transform `monomial_to_legendre` returns, so nothing is discarded by reading the set this way. What changes is which errors amplify: a raw-moment covariance inverted at order twelve amplifies an error in the estimated covariance by up to the Hankel matrix's own condition number, and the Legendre basis does not.

### The fixed centre and each coordinate's S0 power

Every coordinate above is read about a centre held fixed (`windowed_moments_fixed_centre`), section 11.1's self-centring made explicit instead of iterated. What that costs when the fixed centre is not exactly the line's own centroid is Bunker's general, non-centroid cumulant-moment recursion: with a first shifted moment `p1` not zero, every cumulant order mixes it in, `C2 = p2 - p1^2`, `C3 = p3 - 3 p2 p1 + 2 p1^3`, and so on through fifth order, collapsing to the familiar centroid-only forms exactly at `p1 = 0` ([bunker1983](../lit/bunker1983.md), its Eq. 14 and the unlabelled lines following it, p. 441, checked in its own note by substituting `p1 = 0` back into the general fourth- and fifth-order forms and recovering the centroid ones exactly).

`s0_w0_power` and `moment_s0_support` read a coordinate's S0 power off this same cumulant expansion instead of off its raw order, because the two agree only when a moment's own S0 support is homogeneous. Computed directly, under the function's own default assumption that every cumulant of the line's non-ramp part vanishes from third order up (a Gaussian rest, or for the odd orders alone any symmetric one): mu2 carries S0^0 and S0^2, since kappa2 is never clean of the natural, collisional, transit and laser widths. mu3 carries S0^3 alone. mu4 carries S0^0, S0^2 and S0^4, because mu4 = kappa4 + 3 kappa2^2 and kappa2^2 inherits kappa2's own unclean floor squared (`rb5s6s.moment_coords.moment_s0_support`).

<!-- exponents: the S0 powers here are the cumulant expansion's own, enumerated by `rb5s6s.moment_coords.moment_s0_support` and read off the joint line per window and not off the raw order (A167, F341) -->
Relaxing the default assumption changes the answer at higher order: with nothing above first order assumed to vanish, mu6 gains an odd S0^3 contribution it does not carry under either the Gaussian or the symmetric default, because a genuinely asymmetric rest lets its own third cumulant leak into an otherwise even order (the same function, its `clean` argument emptied).

The four owner-named ratios keep their S0 power's total-order rule intact under this reading: mu4/mu2^2, mu3^2/mu2^3 and mu1^3/mu3 are S0-free, and mu5/mu3 carries S0^2, matching the ramp's own weak-drive anchors of 12/5, 8/25, -40 and 20/63 (computed here directly, `rb5s6s.moment_coords.s0_w0_power` applied to `NAMED_RATIOS`, against `NAMED_ANCHOR`). The rule holds for a ratio of moments that are each individually homogeneous, because the powers that fail to cancel in mu2 and mu4 alone cancel between numerator and denominator, and it is stated once here instead of assumed silently at every place a ratio's S0 power is used.

### The coordinate budget and the avoided reconstruction

How many such coordinates one trace can support is bounded before any selection runs. Bunker's Introduction gives a Shannon-style count for a filtered spectrum's independent degrees of freedom: Fourier filtering with a k-window and an r-window jointly admits `(2 Delta K Delta R) / pi` independent data points, "the number of K data points times the fraction of the total r space contained in the pass band" ([bunker1983](../lit/bunker1983.md), its Introduction, p. 437). Applied to one frequency window against a Lorentzian core of width Gamma and a signal-to-noise ratio rho, the analogous count is `2 W t_c` independent numbers, with `t_c = ln(rho) / (pi Gamma)` the time at which the line's own Fourier transform falls to `1 / rho` of its peak (`shannon_coordinate_budget`).

At Gamma = 3 MHz and rho = 1000, computed here directly, the budget is 30.8 numbers at a 21 MHz half-window and 19.1 at 13 MHz (`rb5s6s.moment_coords.shannon_coordinate_budget(21.0, 3.0, 1000.0)` and the same call at 13.0), rounding to the 31 and 19 the module's own tests hold it to. Nested windows share this budget instead of adding to it, since a wider window's transform already carries everything a narrower one's does, so the catalogue's own set of windows is not an independent multiplier on the count.

None of this reconstructs the light-shift distribution from its moments, and the reason is numerical before it is a matter of taste. Tagliani's bound on a maximum-entropy reconstruction from the first M assigned moments shows a uniform relative error in every moment changes the reconstruction by that same small amount, but an error in the top moment alone is amplified by at least `2^(2M - 1)` in root-mean-square terms, with the reconstruction's own Hankel matrix conditioned above `2^(4M - 2)` ([tagliani2001](../lit/tagliani2001.md), its Eq. 2.6-2.8 and 6.13-6.14). At the catalogue's own top order, M = 12, that is an amplification of at least 2^23, about 8.4e6. This record's own route never takes that inversion. A windowed statistic is compared against the model's own windowed prediction (11.8), and the catalogue above is read the same way, a vector of predicted coordinates matched against a vector of measured ones under a fitted covariance, never inverted back into a density.

*Code:* `rb5s6s/moment_coords.py`, closure `tests/test_moment_coords.py`. No producer and no results CSV yet, because the catalogue is not wired into a fit (C6c).

## The basis of a windowed-moment result

The applicability test is three conditions, and any problem meeting them is a candidate for this
treatment: a *truncated* observable, *noisy*, with *inhomogeneous broadening whose distribution is
the quantity of interest*. Where any one fails, the canonical reading is the right one, and on a
homogeneous line the distribution has collapsed to the number a width fit already reports, so this
machinery buys nothing there.

### The untruncated object does not exist on this line

The line carries Lorentzian wings, so its central moments diverge with the window instead of
converging: the second moment grows linearly and the fourth as the cube of the half-width. The
truncated statistic is therefore not an approximation to something behind it. **It is the observable,
and the window is one of its coordinates**, which is why every moment quoted in this record names
its window, its weighting and its integration, and why a moment quoted without them is not yet a
quantity.

### The bias is an estimator bias, not an integral

Fields that truncate a *deterministic* integral can correct it in closed form. Here the moment is
taken about a centre estimated from the same noisy trace, over a window, at the measurement's own
signal-to-noise, so the bias is the sampling bias of a nonlinear estimator and has no closed form.
It is forecast by the twin at known truth, per statistic, per window and per noise level, and
subtracted once with its standard error carried in quadrature.

### Scope statements

1. **The term set is part of the result.** A twin smaller than the fitted model produces numbers
   that look right: omitting the saturated, depleting atom leaves every drive-free ratio unchanged
   within its own scatter while moving a drive-bearing one's exponent by a fifth. Every artefact
   therefore states which terms its model carried, and a computation that omits one must argue the
   omission with its measured cost.
2. **The bias surface is expected to be scale-free, and that expectation is untested.** Truncation
   bias should depend on the window relative to the total width and on the wing weight, and noise
   bias on the signal-to-noise and the effective sample size: four dimensionless numbers, not on
   the dozen physical parameters that produced them. **Whether the surface really collapses that way
   has not been measured**, and until it is, each cell's bias is tabulated and interpolated over the
   truths, never scaled.

### Two sensitive terms and their bounds

Both were measured this session and neither is bounded the way a naive sweep would suggest.

The single-photon Doppler pedestal. A two-photon transition read on a counter-propagating pair is
Doppler-free to first order, but the same-beam absorption leaves a background of the one-photon
Doppler width. On this bench that width is about six times the scan's own half-range, so across the
whole measured span the pedestal is flat to better than two per cent, and the per-trace baseline the
pipeline fits removes it. **Its residual effect on the moments is therefore small, and how small
depends on where the baseline strips sit**. Strips placed inside the line's own Lorentzian wing
subtract real line, so a residual quoted from strips chosen for a harness is not the pipeline's
residual. The reference is the pipeline's own strips.

The retro tilt. A tilt of the retro-reflector is not primarily a broadening: it is a loss of
overlap between the forward and backward beams, because the returning beam is deviated by twice the
tilt and walks off over the mirror's lever arm. On this bench that lever arm turns a few milliradians
into hundreds of microns at the atoms, which is many waists, so **any tilt large enough to broaden
the line has already removed the counter-propagating overlap that makes the line Doppler-free.** The
term is bounded by the signal existing and not by a sweep, and inside that bound it contributes
a small fraction of the transit width. What a large tilt actually does is convert the Doppler-free
line into the pedestal above, which is why the two terms are one piece of physics seen twice.

The general rule this illustrates, and it applies to any swept axis on this page: a swept range
needs a physical bound at each end, and the cheapest one is whether the apparatus still produces a
signal there. A sweep that runs past that point reports the properties of a configuration the
experiment cannot be in.
