"""Model comparison as an EVIDENCE VECTOR, never as a verdict.

STATUS: UNCALIBRATED. The parametric-bootstrap branch has not yet had its
coverage measured on this experiment's noise structure, so `bootstrap_p` is
reported and must not be read as a calibrated p-value until a coverage run
promotes this label. Every function here says so in its output.

WHY THIS EXISTS. This repository has repeatedly found that different selection
criteria are MEASUREMENTS OF DIFFERENT ASSUMPTIONS rather than votes, and that
an algorithmic threshold quietly becomes a scientific verdict if you let one
function return "preferred". So computation and interpretation are separated
here by construction:

    compare(...)                  -> the evidence, several statistics
    interpret_model_comparison(...) -> robust / convention-dependent /
                                       assumption-dependent / unresolved

THE CLASSICAL F TEST IS A LABELLED CONVENTION, NOT A REPAIRED VERDICT. Its
reference distribution needs independent, homoscedastic, Gaussian residuals
from linear models. This experiment has correlated samples, a fitted noise
law, nonlinear models and nuisance parameters. Substituting an effective
sample size for N does NOT restore the reference distribution: under
correlation the numerator and denominator sums of squares stop being
independent scaled chi-squares, and no substitution for N recovers that. The
F statistic is therefore computed, reported, and flagged with the conditions
it violates, so a downstream reader cannot mistake a p-value for authority.

N_eff. Where an effective sample size is supplied, the information criteria
are reported BOTH ways. The pair is the point: where they disagree, the
disagreement is the result.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

__all__ = [
    "ModelFit",
    "ComparisonEvidence",
    "compare",
    "interpret_model_comparison",
    "UNCALIBRATED",
]

UNCALIBRATED = True
_UNCALIBRATED_NOTE = (
    "UNCALIBRATED: bootstrap_p has no measured coverage on this noise "
    "structure yet; treat it as an ordering statistic, not a probability"
)


@dataclass(frozen=True)
class ModelFit:
    """One fitted model, reduced to what a comparison needs.

    ``n_eff`` is optional and, where given, must be the number of INDEPENDENT
    points rather than the number of samples.
    """

    name: str
    chi2: float
    k: int
    n: int
    n_eff: float | None = None
    chi2_eff: float | None = None

    def __post_init__(self) -> None:
        if self.chi2 < 0:
            raise ValueError(f"{self.name}: chi2 must not be negative")
        if self.k < 0 or self.n <= 0:
            raise ValueError(f"{self.name}: bad parameter or point count")
        if self.n_eff is not None and not (0 < self.n_eff <= self.n):
            raise ValueError(f"{self.name}: n_eff must lie in (0, n]")
        if self.chi2_eff is not None and self.n_eff is None:
            raise ValueError(f"{self.name}: chi2_eff without n_eff is a "
                             "half-treatment and is refused")

    def bic(self, effective: bool = False) -> float:
        """BIC, raw or effective.

        THE EFFECTIVE FORM CHANGES BOTH TERMS, and refuses to run on half of
        them. `rb5s6s.sharing_bic` records why: with a raw chi2 against an
        effective penalty, a correlated fit's chi2 gain is inflated by roughly
        tau_int while its parameter cost falls, and the verdict flips for a
        reason that is purely bookkeeping. The whitened chi2 must travel with
        the effective count, so `chi2_eff` is required rather than assumed
        equal to `chi2`.

        This is the repository-defined sensitivity criterion, not a
        theoretically established one for this likelihood.
        """
        if not effective:
            return self.chi2 + self.k * math.log(self.n)
        if self.n_eff is None or self.chi2_eff is None:
            raise ValueError(
                f"{self.name}: the effective BIC needs BOTH chi2_eff and "
                "n_eff; supplying only the effective count would inflate the "
                "chi2 gain against a reduced penalty")
        return self.chi2_eff + self.k * math.log(self.n_eff)

    def aic(self) -> float:
        return self.chi2 + 2 * self.k

    def aicc(self, effective: bool = False) -> float:
        if effective and (self.n_eff is None or self.chi2_eff is None):
            raise ValueError(f"{self.name}: the effective AICc needs both "
                             "chi2_eff and n_eff")
        n = self.n_eff if effective else self.n
        base = (self.chi2_eff if effective else self.chi2) + 2 * self.k
        denom = n - self.k - 1
        if denom <= 0:
            return math.inf
        return base + 2 * self.k * (self.k + 1) / denom


@dataclass(frozen=True)
class ComparisonEvidence:
    """Several statistics about one pair of models. Deliberately not a verdict.

    Every field is a MEASUREMENT under a stated assumption. Nothing here says
    which model to use; `interpret_model_comparison` does that, separately, and
    can be disagreed with without touching the arithmetic.
    """

    simpler: str
    richer: str
    delta_chi2: float
    delta_k: int
    likelihood_ratio_valid: bool
    f_statistic: float | None
    f_validity: str
    f_reason: str
    delta_bic: float
    delta_bic_eff: float | None
    delta_aic: float
    delta_aicc: float
    delta_aicc_eff: float | None
    bootstrap_p: float | None = None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def favours_richer(self) -> dict[str, bool | None]:
        """Which way EACH criterion points. A dict, never a single answer."""
        return {
            "delta_bic": self.delta_bic > 0,
            "delta_bic_eff": None if self.delta_bic_eff is None else self.delta_bic_eff > 0,
            "delta_aic": self.delta_aic > 0,
            "delta_aicc": self.delta_aicc > 0,
            "delta_aicc_eff": None if self.delta_aicc_eff is None else self.delta_aicc_eff > 0,
        }


def compare(simpler: ModelFit, richer: ModelFit, *,
            nested: bool = True, bootstrap_p: float | None = None) -> ComparisonEvidence:
    """Compute the evidence vector for one nested pair. Returns no verdict."""
    if richer.k <= simpler.k:
        raise ValueError("the richer model must carry more parameters")
    if richer.n != simpler.n:
        raise ValueError("the two fits must be over the same points")

    dk = richer.k - simpler.k
    dchi2 = simpler.chi2 - richer.chi2

    dof = richer.n - richer.k
    if not nested:
        f_stat, validity = None, "not applicable"
        reason = "the models are not nested, so an F ratio has no meaning here"
    elif dof <= 0:
        f_stat, validity = None, "undefined"
        reason = "no residual degrees of freedom"
    else:
        f_stat = (dchi2 / dk) / (richer.chi2 / dof)
        validity = "conditional"
        reason = ("correlated samples and a fitted noise law: the reference "
                  "distribution is not F even after an n_eff substitution")
        if simpler.n_eff is not None and simpler.n_eff < simpler.n:
            reason += (f"; measured independence is {simpler.n_eff:.0f} of "
                       f"{simpler.n} points")

    notes = [_UNCALIBRATED_NOTE] if bootstrap_p is not None else []
    if simpler.chi2_eff is None or richer.chi2_eff is None:
        notes.append("no whitened chi2 supplied: the effective criteria are "
                     "absent, not equal to their raw counterparts")

    return ComparisonEvidence(
        simpler=simpler.name, richer=richer.name,
        delta_chi2=dchi2, delta_k=dk,
        likelihood_ratio_valid=bool(nested and dof > 0),
        f_statistic=f_stat, f_validity=validity, f_reason=reason,
        delta_bic=simpler.bic() - richer.bic(),
        delta_bic_eff=(simpler.bic(True) - richer.bic(True))
        if (simpler.chi2_eff is not None and richer.chi2_eff is not None) else None,
        delta_aic=simpler.aic() - richer.aic(),
        delta_aicc=simpler.aicc() - richer.aicc(),
        delta_aicc_eff=(simpler.aicc(True) - richer.aicc(True))
        if (simpler.chi2_eff is not None and richer.chi2_eff is not None) else None,
        bootstrap_p=bootstrap_p,
        notes=tuple(notes),
    )


def interpret_model_comparison(ev: ComparisonEvidence,
                               decisive_bic: float = 6.0) -> dict[str, object]:
    """Classify the evidence. THE ONLY PLACE A JUDGEMENT IS MADE.

    Four outcomes, and none of them is "model preferred" on its own:

      robust                 every available criterion agrees, and decisively
      convention-dependent   criteria disagree, so the answer is a choice of
                             convention rather than a fact about the data
      assumption-dependent   the raw and effective forms disagree, so the
                             answer depends on the correlation treatment
      unresolved             the evidence is too weak to separate the models
    """
    directions = {k: v for k, v in ev.favours_richer().items() if v is not None}
    magnitudes = [abs(x) for x in (ev.delta_bic, ev.delta_bic_eff,
                                   ev.delta_aic, ev.delta_aicc,
                                   ev.delta_aicc_eff) if x is not None]

    raw = {k: v for k, v in directions.items() if not k.endswith("_eff")}
    eff = {k: v for k, v in directions.items() if k.endswith("_eff")}

    if max(magnitudes) < decisive_bic:
        verdict = "unresolved"
        why = (f"the largest criterion separation is {max(magnitudes):.2f}, "
               f"below the {decisive_bic} treated as decisive")
    elif eff and set(raw.values()) != set(eff.values()):
        verdict = "assumption-dependent"
        why = ("the raw and effective-sample-size forms point opposite ways, "
               "so the answer depends on the correlation treatment rather "
               "than on the models")
    elif len(set(directions.values())) > 1:
        verdict = "convention-dependent"
        why = ("the criteria disagree among themselves, so which model is "
               "preferred is a choice of convention")
    else:
        verdict = "robust"
        why = ("every available criterion agrees in direction and at least "
               "one separates decisively")

    return {
        "verdict": verdict,
        "reason": why,
        "favours_richer": (None if verdict in ("unresolved", "convention-dependent",
                                               "assumption-dependent")
                           else next(iter(directions.values()))),
        "directions": directions,
        "uncalibrated": UNCALIBRATED,
        "f_validity": ev.f_validity,
    }
