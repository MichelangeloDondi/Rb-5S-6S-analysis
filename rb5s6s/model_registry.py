"""The model-terms REGISTRY: one source naming which physical terms of the forward model each
computation path carries, so the thesis, the Monte Carlo, the twin and the wiki cannot silently
diverge again (owner order, 2026-09-25).

THE THREE PATHS, read from their own code before this module was written:

  fitter  rb5s6s/fullmodel.py (`full_profile`, and the `Cell` class of `scripts/run_ultra_joint.py`
          that wraps it for the committed ultra-joint fits) and `rb5s6s/lineshape.py` as they call
          it; `rb5s6s/beta.py` (`fit_beta_self`) and `rb5s6s/linefit.py` (`fit_condition`) are
          fitters too. Each term carries ONE fitter status, written by hand as the weakest of the
          three; `check_census_agreement` grades it against the `full_profile` path alone, through
          `results/twin_term_census.csv`, so no instrument reads `fit_beta_self` or `fit_condition`
          for a disagreement yet (owed: a per-consumer check, the audit of 2026-09-25).
  twin    the JOINT twin of record: `rb5s6s/volume_line.py` (`joint_spectrum`, `sample_atoms`,
          `JointTable`) through `rb5s6s/twin_volume.py` (`synthetic_traces`). The LAYERED
          generators `rb5s6s/forecast.py` `synthetic_traces` and `build_world_trace` are a
          registered APPROXIMATION of it and are named in `impl_twin` where they carry a term the
          twin of record does not, never given their own row or column.
  mc      `scripts/run_kernel_mc.py` (`run_node`), the atom-sampled Monte Carlo behind every
          validated kernel-gate node.

SEMANTICS (agreed with the thesis session that seeded this registry; see
`private/model_registry_seed_2026-09-25.tsv` in the PhD-Thesis repository, not carried into this
tree). A status records what the COMMITTED results of record were computed with, never what a
switch merely allows: a term implemented but run off is `owed`. Two regimes: `2025` (the archive's
own conditions, up to 270 mW, 70-130 C) and `campaign` (the proposed campaign, up to 500 mW,
150-170 C). Kinds, written `kind[:detail]`:

  carried    the committed path's own construction applies the term.
  owed       implemented somewhere reachable from the path, or entirely absent, but not applied to
             the path's own committed results; the debt is real and the mechanism, where one
             exists, is still named in the `impl_*` column. Every `owed` status carries a
             kebab-case TAG as its detail, `owed:<tag>`, naming the \\OWED marker of the PhD thesis
             chapter 7 this row's debt corresponds to (the PhD-Thesis session's own convention,
             2026-09-25); a bare `owed` with no tag is refused below.
  neglected  deliberately left out on a stated, evidenced size: `neglected:<size>`, whose evidence
             is a tracked path, an `## F<n> ` finding heading, or a probe id, read from the row's
             `evidence` column.
  absorbed   not modelled as its own term, but a free parameter the path already carries spans its
             effect without a separate mechanism (a free centre spanning a constant shift; a free
             Lorentzian width spanning a degenerate constant broadening).
  n/a        outside the computational method's own declared scope (a rate-based, incoherent Monte
             Carlo has no chirp to carry or neglect; an atom-sampling kernel has no line centre to
             shift).

Every `carried` status names the code site that applies it in its own `impl_*` column; where none
could be found the status is `owed`, never asserted from a docstring alone.

A CROSS-CHECK AGAINST `results/twin_term_census.csv` (the code-inspected census this registry
overrides for the fitter column) is `check_census_agreement()`, below: it refuses a contradiction
between what the census's own `fitter` column says and what this registry's `status_fitter_2025`
says, for every term the seed's own `census_row` column names. A term the seed maps to `NONE` (no
census row exists) is outside the census's reach and is not checked.

THE PREFLIGHT (owner order O58, 2026-09-25: "make sure ... that the twin and montecarlo are always wired to the same
full model, and that the computations can't start without this match"). `preflight(consumer, regime, executes)` is
called BEFORE a run's first atom, with the registry ids the configured run will execute, and raises `ModelReduced`
unless (a) a run standing behind a result executes exactly its consumer's carried set, and a declared study names
every term it drops or adds with a reason; (b) every term the twin and the Monte Carlo do not both carry is a
declared debt on the other side (`owed` or `n/a`); and (c) the two RATCHETS hold: the set of terms carried by one
path and not the other, and the set of terms both carry through DIFFERENT code, are each no larger than
`PAIRING_BASELINE` and `IMPL_BASELINE`, frozen at the registry of 2026-09-25, so the twin and the Monte Carlo can
only come together. The single full model (plan V6.1) is what empties both, and then any divergence refuses every
computation at its start. `mc_contract.guard` calls it for every guarded harness.

THE EXECUTED-TERM LEDGER (implemented and planted here; NOT YET WIRED into `fullmodel.py`,
`volume_line.py` or `scripts/run_kernel_mc.py` themselves -- that wiring is a later, separate wave,
named so a reader does not mistake this module's own self-consistency for the model modules'
compliance). `run(consumer, regime)` opens a context; `executed(term_id, strength)` records a term
actually applied by THIS run, refusing an unknown id and ignoring a zero or falsy strength;
`require()` compares what was executed against what the registry says this consumer/regime
combination carries, and raises `ModelReduced` naming every carried term silently dropped;
`ablation(reason, drop)` is the licensed way to drop some on purpose, with a reason of real length.
"""
from __future__ import annotations

import contextlib
import contextvars
import csv
import hashlib
import re
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Iterable, Optional, Sequence

__all__ = [
    "ModelTerm", "REGISTRY", "TERM_IDS", "VALID_KINDS", "REGIMES", "CONSUMERS",
    "kind_of", "status_fields", "carried_term_ids", "executed_digest", "registry_digest", "registry_content_digest",
    "consumer_digest", "ModelReduced", "run", "executed", "current", "require", "ablation",
    "manifest", "CENSUS_ROW_FOR", "census_says_fitter_carries", "check_census_agreement",
    "CensusDisagreement", "to_csv_rows", "CSV_COLUMNS",
    "preflight", "pairing_gaps", "impl_gaps", "PAIRING_BASELINE", "IMPL_BASELINE",
]

# ---------------------------------------------------------------------------
# The vocabulary
# ---------------------------------------------------------------------------

VALID_KINDS: tuple[str, ...] = ("carried", "owed", "neglected", "absorbed", "n/a")
REGIMES: tuple[str, ...] = ("2025", "campaign")
CONSUMERS: tuple[str, ...] = ("fitter", "twin", "mc")

#: an evidence citation for a `neglected:<size>` row must look like one of these three kinds of
#: pointer, so a size cannot be asserted from prose alone (the rule file's own evidence discipline)
_EVIDENCE_PATH_PREFIXES: tuple[str, ...] = (
    "results/", "rb5s6s/", "scripts/", "docs/", "tests/", "examples/", "private/",
)

#: an `owed` tag is kebab-case: lowercase letters and digits, hyphen-joined, no underscore and no
#: leading/trailing/doubled hyphen (the PhD-Thesis session's own convention, 2026-09-25), so a tag
#: this registry writes can stand as an \OWED marker in the thesis without reformatting.
_KEBAB_TAG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def kind_of(status: str) -> str:
    """The kind half of a `kind[:detail]` status string, validated against `VALID_KINDS`."""
    kind = status.split(":", 1)[0]
    if kind not in VALID_KINDS:
        raise ValueError(
            f"unknown status kind {kind!r} in {status!r}; valid kinds are {VALID_KINDS}")
    return kind


def _detail_of(status: str) -> str:
    parts = status.split(":", 1)
    return parts[1] if len(parts) == 2 else ""


def _looks_like_evidence(evidence: str) -> bool:
    if not evidence:
        return False
    if evidence.startswith("## F") or evidence.startswith("probe:"):
        return True
    return evidence.startswith(_EVIDENCE_PATH_PREFIXES)


#: the six status columns, in the order the CSV and the docs page carry them
STATUS_FIELDS: tuple[str, ...] = tuple(
    f"status_{consumer}_{regime}" for consumer in CONSUMERS for regime in REGIMES
)


def status_fields() -> tuple[str, ...]:
    return STATUS_FIELDS


# ---------------------------------------------------------------------------
# The row
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ModelTerm:
    """One physical term of the forward model, and what each path does with it.

    `impl_fitter`, `impl_twin`, `impl_mc` are each `"module:function"` or `"-"`: ONE implementation
    per term per path. A `carried` status in that path's regimes MUST name a site here (checked
    below); an `owed`, `neglected`, `absorbed` or `n/a` status MAY still name one, when a
    reachable-but-unapplied mechanism exists (a parameter a caller never sets; the registered
    approximation `rb5s6s.forecast` carries where the twin of record does not) -- naming it is what
    turns a debt into something a reader can act on rather than merely a claim.
    """

    term_id: str
    status_fitter_2025: str
    status_twin_2025: str
    status_mc_2025: str
    status_fitter_campaign: str
    status_twin_campaign: str
    status_mc_campaign: str
    physics: str
    impl_fitter: str
    impl_twin: str
    impl_mc: str
    param_keys: str
    thesis_anchor: str
    wiki_page: str
    methods_page: str
    evidence: str

    def __post_init__(self) -> None:
        if not self.term_id:
            raise ValueError("a term_id is required")
        _impl_of = {"fitter": self.impl_fitter, "twin": self.impl_twin, "mc": self.impl_mc}
        for consumer in CONSUMERS:
            impl = _impl_of[consumer]
            if impl != "-" and ":" not in impl:
                raise ValueError(
                    f"{self.term_id}: impl_{consumer}={impl!r} is neither '-' nor 'module:function'")
            for regime in REGIMES:
                status = getattr(self, f"status_{consumer}_{regime}")
                kind = kind_of(status)  # raises on an unknown kind
                if kind == "carried" and impl == "-":
                    raise ValueError(
                        f"{self.term_id}: status_{consumer}_{regime}={status!r} is carried but "
                        f"impl_{consumer} names no code site")
                if kind == "neglected":
                    size = _detail_of(status)
                    if not size:
                        raise ValueError(
                            f"{self.term_id}: status_{consumer}_{regime}={status!r} is neglected "
                            "without a stated size (write 'neglected:<size>')")
                    if not _looks_like_evidence(self.evidence):
                        raise ValueError(
                            f"{self.term_id}: status_{consumer}_{regime}={status!r} is neglected "
                            f"but evidence={self.evidence!r} is not a tracked path, an '## F<n> ' "
                            "finding heading, or a probe id")
                if kind == "owed":
                    tag = _detail_of(status)
                    if not tag:
                        raise ValueError(
                            f"{self.term_id}: status_{consumer}_{regime}={status!r} is owed with "
                            "no tag (write 'owed:<tag>', the tag a kebab-case \\OWED marker of "
                            "PhD thesis chapter 7)")
                    if not _KEBAB_TAG_RE.match(tag):
                        raise ValueError(
                            f"{self.term_id}: status_{consumer}_{regime}={status!r}'s tag "
                            f"{tag!r} is not kebab-case (lowercase, digits, single hyphens)")


# ---------------------------------------------------------------------------
# The registry: one row per term_id of the thesis session's 34-term seed, and the four terms the
# two sessions agreed on 2026-09-25 after each side had read the forward model against its code
# (retro_focus_offset, sweep_axis_curvature, amplitude_slope, quadratic_zeeman), each owed under
# the chapter-7 marker the thesis already carries. A further term is added the same way: agreed
# with the thesis session, with its marker, never by one side alone.
# ---------------------------------------------------------------------------

REGISTRY: tuple[ModelTerm, ...] = (

    ModelTerm(
        term_id="natural_width",
        status_fitter_2025="carried", status_twin_2025="carried", status_mc_2025="carried",
        status_fitter_campaign="carried", status_twin_campaign="carried", status_mc_campaign="carried",
        physics="The 5S-6S transition's own radiative decay rate Gamma_nat, a fixed Lorentzian "
                "component every construction of the line adds before any broadening.",
        impl_fitter="rb5s6s.lineshape:model_profile",
        impl_twin="rb5s6s.volume_line:joint_spectrum",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="gamma_nat_mhz, gamma_hom_mhz",
        thesis_anchor="tab:tps_magnitudes. Sec:rb5s6s section 7.2.6",
        wiki_page="voigt-profile.md", methods_page="docs/methods/02_the_lineshape.md",
        evidence="rb5s6s/constants.py",
    ),

    ModelTerm(
        term_id="transit",
        status_fitter_2025="carried", status_twin_2025="carried", status_mc_2025="carried",
        status_fitter_campaign="carried", status_twin_campaign="carried", status_mc_campaign="carried",
        physics="Finite crossing time through the focused beam: a two-sided-exponential (cusp) "
                "kernel in the fitter, and the atom's own w(z)/v transit time in the twin and MC.",
        impl_fitter="rb5s6s.lineshape:model_profile",
        impl_twin="rb5s6s.volume_line:sample_atoms",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="transit_fwhm, transit_ref_mhz, w0_m",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.5",
        wiki_page="transit-time-broadening.md", methods_page="docs/methods/02_the_lineshape.md",
        evidence="results/kernel_mc.csv",
    ),

    ModelTerm(
        term_id="transit_chirp",
        status_fitter_2025="owed:odd-channel-chirp", status_twin_2025="carried",
        status_mc_2025="owed:odd-channel-chirp",
        status_fitter_campaign="owed:odd-channel-chirp", status_twin_campaign="carried",
        status_mc_campaign="owed:odd-channel-chirp",
        physics="The AC-Stark phase and the transit width are correlated within one crossing (the "
                "same beam sets both), so the coherent line is not exactly a product of independent "
                "ramp and transit factors. The joint twin carries the correlation directly through "
                "the per-atom phase phi(t), the fitter's convolution factorisation does not.",
        impl_fitter="rb5s6s.fullmodel:full_profile",
        impl_twin="rb5s6s.volume_line:joint_spectrum",
        impl_mc="-",
        param_keys="phi(t), sign, S0_mhz",
        thesis_anchor="tab:tps_magnitudes. Eq:tps_chirp. Section 7.2.5",
        wiki_page="third-cumulant.md", methods_page="docs/methods/10_the_odd_moments.md",
        evidence="rb5s6s/ramp_transit.py",
    ),

    ModelTerm(
        term_id="laser_kernel",
        status_fitter_2025="carried", status_twin_2025="carried", status_mc_2025="n/a",
        status_fitter_campaign="carried", status_twin_campaign="carried", status_mc_campaign="n/a",
        physics="The laser's own frequency noise, a Gaussian and/or Lorentzian kernel convolved "
                "onto the transit-and-collision core (doubled for the two photons).",
        impl_fitter="rb5s6s.lineshape:model_profile",
        impl_twin="rb5s6s.volume_line:joint_spectrum",
        impl_mc="-",
        param_keys="sigma_laser_fwhm, gamma_l, laser_kind, sigma_laser_mhz",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.8",
        wiki_page="laser-frequency-noise-and-the-linewidth.md",
        methods_page="docs/methods/02_the_lineshape.md",
        evidence="the atom-sampling Monte Carlo has no laser-noise source at all (scripts/run_kernel_mc.py)",
    ),

    ModelTerm(
        term_id="self_broadening_vdw",
        status_fitter_2025="carried", status_twin_2025="carried", status_mc_2025="n/a",
        status_fitter_campaign="carried", status_twin_campaign="carried", status_mc_campaign="n/a",
        physics="Rb-Rb collisional (van der Waals) broadening, gamma_coll = beta_self * N(T): a "
                "Lorentzian whose width tracks the vapour density.",
        impl_fitter="rb5s6s.beta:fit_beta_self",
        impl_twin="rb5s6s.volume_line:joint_spectrum",
        impl_mc="-",
        param_keys="gamma_coll, beta_self, beta_rel, gamma_hom_mhz",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.7. Appendix C",
        wiki_page="self-broadening.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="the kernel Monte Carlo validates transit/ramp/saturation/depletion, never the "
                 "empirically-fitted collisional width (scripts/run_kernel_mc.py)",
    ),

    ModelTerm(
        term_id="self_broadening_T03",
        status_fitter_2025="owed:beta-self-temperature-law",
        status_twin_2025="owed:beta-self-temperature-law", status_mc_2025="n/a",
        status_fitter_campaign="owed:beta-self-temperature-law",
        status_twin_campaign="owed:beta-self-temperature-law", status_mc_campaign="n/a",
        physics="A kinetic-theory T^0.3 correction to the collisional cross-section itself, on top "
                "of the density's own N(T): every committed fit holds beta_self as ONE constant "
                "coefficient across the temperature ladder, with no separate power-law term.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="beta_self",
        thesis_anchor="section 7.2.7. F.8",
        wiki_page="self-broadening.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="rb5s6s/beta.py:fit_beta_self (gamma_coll(T) = beta_self * N(T), no T-power term)",
    ),

    ModelTerm(
        term_id="foreign_gas",
        status_fitter_2025="absorbed:gamma_l", status_twin_2025="absorbed:gamma_hom_mhz",
        status_mc_2025="n/a",
        status_fitter_campaign="absorbed:gamma_l", status_twin_campaign="absorbed:gamma_hom_mhz",
        status_mc_campaign="n/a",
        physics="Permeated atmospheric gas (helium, then neon) is a constant Lorentzian, exactly "
                "the same shape as gamma_l/gamma_hom_mhz, so its value is a PRIOR on that shared "
                "width rather than a second term. No coefficient for 5S-6S is held (F136-F138).",
        impl_fitter="rb5s6s.lineshape:permeated_gas_width_mhz",
        impl_twin="-",
        impl_mc="-",
        param_keys="gamma_l, fit_gamma_l, gamma_hom_mhz",
        thesis_anchor="tab:tps_magnitudes. Appendix C.5",
        wiki_page="self-broadening.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="rb5s6s/lineshape.py:permeated_gas_width_mhz's own docstring ('THIS IS A PRIOR ON "
                 "gamma_l, NOT A SECOND TERM')",
    ),

    ModelTerm(
        term_id="ac_stark_ramp",
        status_fitter_2025="carried", status_twin_2025="carried", status_mc_2025="carried",
        status_fitter_campaign="carried", status_twin_campaign="carried", status_mc_campaign="carried",
        physics="The AC-Stark shift distribution a focused, I^2-weighted beam imprints: a "
                "triangular ramp (or its saturated/axially-mixed generalisation) on [0, S0].",
        impl_fitter="rb5s6s.fullmodel:full_profile",
        impl_twin="rb5s6s.volume_line:joint_spectrum",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="s0, S0_mhz, stark_shift_S0_mhz",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.10",
        wiki_page="ac-stark-shift.md", methods_page="docs/methods/03_the_ac_stark_ramp.md",
        evidence="results/kernel_mc.csv (ramp_k2_rel, ramp_k3_rel)",
    ),

    ModelTerm(
        term_id="doppler_pedestal",
        status_fitter_2025="absorbed:baseline", status_twin_2025="owed:doppler-pedestal-in-twin",
        status_mc_2025="n/a",
        status_fitter_campaign="absorbed:baseline",
        status_twin_campaign="owed:doppler-pedestal-in-twin",
        status_mc_campaign="n/a",
        physics="The co-propagating two-photon absorption's own Doppler-broadened (~931 MHz at "
                "130 C) pedestal under the narrow Doppler-free line, at about three parts in a "
                "thousand of its height.",
        impl_fitter="rb5s6s.fullmodel:doppler_pedestal_fwhm_mhz",
        impl_twin="rb5s6s.forecast:build_world_trace",
        impl_mc="-",
        param_keys="pedestal_height_frac",
        thesis_anchor="tab:tps_magnitudes. Table 7.5",
        wiki_page="doppler-free-two-photon.md", methods_page="docs/methods/02_the_lineshape.md",
        evidence="over the archive's sub-100 MHz span the pedestal is a near-constant offset, "
                 "degenerate with the free per-trace baseline every committed fit already carries "
                 "(results/twin_term_census.csv: doppler_pedestal)",
    ),

    ModelTerm(
        term_id="saturation",
        status_fitter_2025="carried", status_twin_2025="owed:saturated-arm", status_mc_2025="carried",
        status_fitter_campaign="carried", status_twin_campaign="owed:saturated-arm",
        status_mc_campaign="carried",
        physics="Homogeneous broadening and ramp reshaping from a non-perturbative two-photon "
                "drive: the companion width goes as Gamma*(sqrt(1+2(Omega/Gamma)^2)-1) and the "
                "ramp's own local density saturates from x to G(Px)/x.",
        impl_fitter="rb5s6s.fullmodel:saturation_companion_mhz",
        impl_twin="-",
        impl_mc="rb5s6s.platforms:excitation_rate_per_atom",
        param_keys="omega_mhz, saturated_ramp_density, excitation_rate_per_atom",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.12. Table 7.5",
        wiki_page="saturation.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="rb5s6s/volume_line.py's own module docstring ('WEAK FIELD ONLY... DEFERS the "
                 "saturated arm')",
    ),

    ModelTerm(
        term_id="hyperfine_pumping",
        status_fitter_2025="carried", status_twin_2025="owed:saturated-arm", status_mc_2025="carried",
        status_fitter_campaign="carried", status_twin_campaign="owed:saturated-arm",
        status_mc_campaign="carried",
        physics="Optical pumping into the other F state mid-crossing, F-dependent through the "
                "cascade's branching fraction (0.223 to 0.372 across the four lines).",
        impl_fitter="rb5s6s.fullmodel:saturation_companion_mhz",
        impl_twin="-",
        impl_mc="rb5s6s.cascade:BRANCHING_F",
        param_keys="pump_scale, peak, F_PER_LINE, BRANCHING_F",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.3. Table 7.5",
        wiki_page="the-cascade-and-f-depletion.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="joint_spectrum has no peak/F argument at all (rb5s6s/volume_line.py)",
    ),

    ModelTerm(
        term_id="companion_pull_reduction",
        status_fitter_2025="owed:companion-pull-reduction",
        status_twin_2025="owed:companion-pull-reduction", status_mc_2025="carried",
        status_fitter_campaign="owed:companion-pull-reduction",
        status_twin_campaign="owed:companion-pull-reduction", status_mc_campaign="carried",
        physics="Saturation and pumping reduce the ramp's mean pull by about two per cent, because "
                "the saturating rate under-weights the brightest (most-shifted) part of the beam.",
        impl_fitter="-", impl_twin="-",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="ramp_mean, m_s, m_w",
        thesis_anchor="tab:tps_magnitudes. Table 7.5 caption",
        wiki_page="ac-stark-shift.md", methods_page="docs/methods/03_the_ac_stark_ramp.md",
        evidence="scripts/run_kernel_mc.py's run_node reports both the saturated and weak-field "
                 "ramp means (detail['ramp_mean']) but no fitter or twin construction reads the "
                 "reduction back into the fitted pull",
    ),

    ModelTerm(
        term_id="axial_collection_window",
        status_fitter_2025="owed:collection-window-in-fitter", status_twin_2025="carried",
        status_mc_2025="carried",
        status_fitter_campaign="owed:collection-window-in-fitter", status_twin_campaign="carried",
        status_mc_campaign="carried",
        physics="Beam divergence over the collected column: the local ramp edge falls as "
                "S(zeta)/(1+zeta^2) and the per-z weight as (1+zeta^2)^(1-n), mixing the "
                "transverse law axially at z_ratio = Z/z_R.",
        impl_fitter="scripts.run_ultra_joint:window_profile",
        impl_twin="rb5s6s.volume_line:sample_atoms",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="z_ratio, half_window_m, collection_z_ratio_m2",
        thesis_anchor="tab:tps_magnitudes. Appendix A.9",
        wiki_page="the-beam-waist.md", methods_page="docs/methods/03_the_ac_stark_ramp.md",
        evidence="the window enters the Cell only as z_ratio derived from the Cell's own fixed "
                 "(w0, M2) configuration, never as an independently fitted quantity "
                 "(scripts/run_ultra_joint.py:Cell.__init__)",
    ),

    ModelTerm(
        term_id="bore_clipping",
        status_fitter_2025="owed:bore-limited-recompute", status_twin_2025="carried",
        status_mc_2025="carried",
        status_fitter_campaign="owed:bore-limited-recompute",
        status_twin_campaign="carried",
        status_mc_campaign="carried",
        physics="The EOM's 3 mm bore clips the focused Gaussian: the on-axis focal intensity per "
                "recorded watt is reduced and the profile (side lobes, effective M2, the transit "
                "kernel, the ramp's own f(s)) is reshaped by diffraction at the aperture.",
        impl_fitter="rb5s6s.lineshape:aperture_onaxis_factor_actual",
        impl_twin="rb5s6s.beam_field:ClippedBeam",
        impl_mc="rb5s6s.beam_field:ClippedBeam",
        param_keys="aperture_onaxis, w_act_m, EOM_APERTURE_RADIUS_M",
        thesis_anchor="tab:tps_magnitudes. Section 7.1.5. Section 7.2.9",
        wiki_page="beam-delivery-and-the-waist-ratio.md", methods_page="docs/methods/03_the_ac_stark_ramp.md",
        evidence="the Cell applies only the ON-AXIS reading correction to S0. The profile's side "
                 "lobes and kernel reshaping (aperture_spread_factor) never reach a committed fit "
                 "(scripts/run_ultra_joint.py:Cell._per_trace). F538: read along each chord the "
                 "clipped focus carries 0.7713 +- 0.0029, 0.6910 +- 0.0039 and 0.5870 +- 0.0063 of the "
                 "alpha signal on windowed mu3 of a Gaussian at the same focus, at W = 5, 6 and 8 MHz "
                 "(against the Gaussian of equal width the ratios and the width channel move, the thesis "
                 "side's reading of 2026-09-25, not yet re-obtained here), so a Gaussian reading "
                 "of the bench's line puts alpha through mu3 low by about 1.3x to 1.7x "
                 "(private/cache/plan_2026-09-25/v65_borecheck/borecheck.tsv)",
    ),

    ModelTerm(
        term_id="retro_mismatch",
        status_fitter_2025="owed:retro-waist", status_twin_2025="owed:retro-waist",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:retro-waist",
        status_twin_campaign="owed:retro-waist", status_mc_campaign="n/a",
        physics="The returning (retro) beam wider than the forward one at the atoms, about 1.2 "
                "times, reducing the standing-wave fringe contrast and the Doppler-free rate's "
                "uniformity. It is the scalar limit of retro_focus_offset: a returning focus displaced "
                "by Delta is, at the forward focus, wider by sqrt(1 + (Delta/z_R)^2), which is 1.2 at "
                "Delta = 0.66 z_R, while the full term also moves where along z the two arms peak.",
        impl_fitter="rb5s6s.fullmodel:fringe_survival_mc",
        impl_twin="-", impl_mc="-",
        param_keys="rho, e1_dot_e2",
        thesis_anchor="tab:tps_magnitudes. Appendix A",
        wiki_page="standing-waves.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="rb5s6s/fullmodel.py:fringe_survival_mc is never called from full_profile or the "
                 "Cell's own model()",
    ),

    ModelTerm(
        term_id="retro_offset",
        status_fitter_2025="owed:retro-waist", status_twin_2025="owed:retro-waist",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:retro-waist",
        status_twin_campaign="owed:retro-waist", status_mc_campaign="n/a",
        physics="A returning beam displaced by about 0.2 w0 makes the local fringe contrast a "
                "function of transverse position rather than a single number.",
        impl_fitter="rb5s6s.fullmodel:fringe_survival_mc",
        impl_twin="-", impl_mc="-",
        param_keys="offset_m",
        thesis_anchor="tab:tps_magnitudes",
        wiki_page="standing-waves.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="rb5s6s/fullmodel.py:fringe_survival_mc takes offset_m but no committed fit calls it",
    ),

    ModelTerm(
        term_id="fringe_tail",
        status_fitter_2025="owed:fringe-resolved-skew", status_twin_2025="owed:fringe-resolved-skew",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:fringe-resolved-skew",
        status_twin_campaign="owed:fringe-resolved-skew", status_mc_campaign="n/a",
        physics="Atoms that resolve the standing wave's lambda/2 fringes (rather than averaging "
                "over many of them) sample a suppressed third-cumulant skew, about 7 per cent at "
                "the archive's waist.",
        impl_fitter="rb5s6s.fullmodel:fringe_survival_mc",
        impl_twin="-",
        impl_mc="-",
        param_keys="coherence_s, fringe_variance_weight",
        thesis_anchor="tab:tps_magnitudes. Table 7.3",
        wiki_page="standing-waves.md", methods_page="docs/methods/11_the_window_limits.md",
        evidence="results/twin_term_census.csv: standing_wave_fringe_tail is off by default in "
                 "the forecast approximation and absent from the twin of record and the MC alike",
    ),

    ModelTerm(
        term_id="retro_tilt",
        status_fitter_2025="absorbed:sigma_laser_fwhm", status_twin_2025="owed:retro-tilt-in-twin",
        status_mc_2025="n/a",
        status_fitter_campaign="absorbed:sigma_laser_fwhm",
        status_twin_campaign="owed:retro-tilt-in-twin",
        status_mc_campaign="n/a",
        physics="A residual tilt between the forward and retro beams leaves an un-cancelled "
                "two-photon wave-vector 2k sin(theta/2), broadening without shifting: 0.47 MHz "
                "per mrad at 110 C.",
        impl_fitter="rb5s6s.fullmodel:residual_doppler_fwhm_mhz",
        impl_twin="-", impl_mc="-",
        param_keys="retro_tilt_rad",
        thesis_anchor="tab:tps_magnitudes. Table 7.5",
        wiki_page="standing-waves.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="a Gaussian width at fixed intensity: 'the fitter puts it in sigma_laser and the "
                 "waist does not move' (results/twin_term_census.csv: retro_tilt_residual_doppler)",
    ),

    ModelTerm(
        term_id="beam_quality_m2",
        status_fitter_2025="owed:collection-window-in-fitter", status_twin_2025="carried",
        status_mc_2025="carried",
        status_fitter_campaign="owed:collection-window-in-fitter", status_twin_campaign="carried",
        status_mc_campaign="carried",
        physics="M^2 enters exactly once, the Rayleigh range z_R = pi w0^2/(M^2 lambda), hence "
                "every axial-collection and beam-divergence quantity built from z_R.",
        impl_fitter="scripts.run_ultra_joint:window_profile",
        impl_twin="rb5s6s.volume_line:GaussianBeam",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="m2, M2, collection_z_ratio_m2",
        thesis_anchor="Table 7.5",
        wiki_page="the-beam-waist.md", methods_page="docs/methods/03_the_ac_stark_ramp.md",
        evidence="M^2 enters the Cell only as a FIXED per-Cell configuration axis (spec['m2']), "
                 "never as a parameter the fit itself identifies, matching the degeneracy with the "
                 "waist the census records (results/twin_term_census.csv: beam_quality_m2)",
    ),

    ModelTerm(
        term_id="collisional_shift",
        status_fitter_2025="absorbed:centre_mhz", status_twin_2025="absorbed:centre_mhz",
        status_mc_2025="n/a",
        status_fitter_campaign="absorbed:centre_mhz", status_twin_campaign="absorbed:centre_mhz",
        status_mc_campaign="n/a",
        physics="Collisions shift the line as well as broadening it. No construction here carries "
                "a collisional SHIFT term, so it rides in the free per-trace centre.",
        impl_fitter="rb5s6s.linefit:fit_condition",
        impl_twin="rb5s6s.twin_volume:synthetic_traces",
        impl_mc="-",
        param_keys="centre_mhz, center_i",
        thesis_anchor="tab:tps_magnitudes. Section 7.2.7",
        wiki_page="self-broadening.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="results/collisional_shift_bound.csv",
    ),

    ModelTerm(
        term_id="second_order_doppler",
        status_fitter_2025="neglected:4e-4-MHz", status_twin_2025="owed:second-order-doppler",
        status_mc_2025="n/a",
        status_fitter_campaign="neglected:4e-4-MHz",
        status_twin_campaign="owed:second-order-doppler", status_mc_campaign="n/a",
        physics="The relativistic (v/c)^2 time-dilation correction to the two-photon resonance "
                "condition.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="tab:tps_magnitudes",
        wiki_page="doppler-free-two-photon.md", methods_page="docs/methods/02_the_lineshape.md",
        evidence="private/THE_ESTIMATOR_AND_THE_ALPHA_GAP.md section 3c: the second-order Doppler is 4e-4 MHz, under a tenth of the per-trace centre error, and a centre shift the free centre absorbs. The thesis quotes 0.39 kHz at 130 C, 7e-5 of the observed width",
    ),

    ModelTerm(
        term_id="blackbody",
        status_fitter_2025="absorbed:centre_mhz", status_twin_2025="owed:blackbody-in-twin",
        status_mc_2025="n/a",
        status_fitter_campaign="absorbed:centre_mhz", status_twin_campaign="owed:blackbody-in-twin",
        status_mc_campaign="n/a",
        physics="Thermal (blackbody) radiation from the cell walls Stark-shifts the atom. A "
                "centre shift of order -0.16 kHz at 130 C, negligible against the MHz-scale width.",
        impl_fitter="rb5s6s.fullmodel:full_profile",
        impl_twin="rb5s6s.forecast:build_world_trace",
        impl_mc="-",
        param_keys="t_bbr_k, shift_hz",
        thesis_anchor="tab:tps_magnitudes",
        wiki_page="blackbody-radiation.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="'a centre shift, absorbed exactly by the free per-trace centre' "
                 "(rb5s6s/fullmodel.py UNFITTABLE['t_bbr_k'])",
    ),

    ModelTerm(
        term_id="two_photon_absorption",
        status_fitter_2025="owed:drive-depletion",
        status_twin_2025="owed:drive-depletion", status_mc_2025="n/a",
        status_fitter_campaign="owed:drive-depletion",
        status_twin_campaign="owed:drive-depletion", status_mc_campaign="n/a",
        physics="The two-photon transition itself depletes the driving beam's power as it "
                "propagates, at about one part in a thousand per pass, affecting the forward/retro "
                "power ratio rho.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="rho",
        thesis_anchor="tab:tps_magnitudes",
        wiki_page="multiphoton-transitions.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="no forward-model term feeds an absorbed-power correction back into rho anywhere "
                 "in this package",
    ),

    ModelTerm(
        term_id="kerr_lens",
        status_fitter_2025="owed:kerr-lens-moments", status_twin_2025="owed:kerr-lens-moments",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:kerr-lens-moments",
        status_twin_campaign="owed:kerr-lens-moments", status_mc_campaign="n/a",
        physics="The vapour's own intensity-dependent refractive index self-(de)focuses the drive "
                "beam, of order 1e-4 to 1e-3 rad on the axis.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="tab:tps_magnitudes. Chapter 8 Table 8.6 paragraph",
        wiki_page="the-beam-waist.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="the thesis's own chapter 8 names it 'owed in the forward model'. No module here "
                 "computes a Kerr-lens term",
    ),

    ModelTerm(
        term_id="radiation_trapping",
        status_fitter_2025="owed:trapping-window",
        status_twin_2025="owed:trapping-window", status_mc_2025="n/a",
        status_fitter_campaign="owed:trapping-window",
        status_twin_campaign="owed:trapping-window", status_mc_campaign="n/a",
        physics="Trapped D-line cascade photons are re-emitted from a volume larger than the one the "
                "993 nm drive excites, so the photons the detector collects come from a window whose "
                "effective extent grows with the density: re-emission blurs the collected window with "
                "temperature. The detected frequency does not depend on the 993 nm detuning, so it "
                "cannot reshape the line directly, and the per-trace free amplitude absorbs its "
                "constant part. What no free amplitude absorbs is the window it moves, which the "
                "moments read through the ramp's distribution of shifts along z (re-read 2026-09-25 "
                "with the thesis session, from absorbed:amplitude). It also matters where an amplitude "
                "is read as a density, which scripts/run_amplitude_trapping.py measures."
,
        impl_fitter="-",
        impl_twin="rb5s6s.forecast:build_world_trace",
        impl_mc="-",
        param_keys="halo_fraction",
        thesis_anchor="Table 7.5",
        wiki_page="the-cascade-and-f-depletion.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="results/twin_term_census.csv: radiation_trapping ('the fitter parks it in "
                 "beta_self and the collisional coefficient reads high')",
    ),

    ModelTerm(
        term_id="photoionisation",
        status_fitter_2025="owed:photoionisation-channel",
        status_twin_2025="owed:photoionisation-channel", status_mc_2025="n/a",
        status_fitter_campaign="owed:photoionisation-channel",
        status_twin_campaign="owed:photoionisation-channel", status_mc_campaign="n/a",
        physics="A one-photon ionisation channel from an excited intermediate state. The thesis's "
                "own argument is that no such channel is resonant here.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="tab:tps_magnitudes",
        wiki_page="multiphoton-transitions.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="no module in this repository computes or bounds it",
    ),

    ModelTerm(
        term_id="depletion_cascade",
        status_fitter_2025="owed:saturated-arm", status_twin_2025="owed:saturated-arm",
        status_mc_2025="carried",
        status_fitter_campaign="owed:saturated-arm",
        status_twin_campaign="owed:saturated-arm", status_mc_campaign="owed:kernel-gate-node-coverage",
        physics="The 5P cascade's F-changing relaxation depletes the driven ground-state "
                "population as an atom crosses the beam, non-uniformly across transverse speed, "
                "widening the surviving transit kernel (about 12 per cent at three mean cycles).",
        impl_fitter="rb5s6s.kernel_gate:depletion_factor",
        impl_twin="-",
        impl_mc="scripts.run_kernel_mc:run_node",
        param_keys="q, BRANCHING_F, depletion_factor, cycles",
        thesis_anchor="section 7.1.6",
        wiki_page="the-cascade-and-f-depletion.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="the Cell multiplies its transit width by a kernel-gate-validated factor rather "
                 "than modelling depletion itself, and no validated node exists past the archive's "
                 "own (w0, M2, rho, T, P) grid (scripts/run_ultra_joint.py:Cell._per_trace. "
                 "scripts/run_kernel_mc.py:GRID_CONDITIONS)",
    ),

    ModelTerm(
        term_id="hyperfine_shares",
        status_fitter_2025="owed:hyperfine-shares-untied",
        status_twin_2025="owed:hyperfine-shares-untied", status_mc_2025="carried",
        status_fitter_campaign="owed:hyperfine-shares-untied",
        status_twin_campaign="owed:hyperfine-shares-untied", status_mc_campaign="carried",
        physics="The four hyperfine lines' relative amplitudes: abundance times (2F+1)/G_iso, "
                "reweighted by each line's own cascade depletion.",
        impl_fitter="-",
        impl_twin="rb5s6s.forecast:build_world_trace",
        impl_mc="rb5s6s.amplitudes:predicted_shares",
        param_keys="predicted_shares, shares_abs, shares_shift_abs",
        thesis_anchor="section 7.2.3",
        wiki_page="hyperfine-populations-and-branching.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="every committed fit floats each trace's own amplitude freely. No fitter or twin "
                 "construction ties amplitudes across peaks by predicted_shares",
    ),

    ModelTerm(
        term_id="quench_4D",
        status_fitter_2025="owed:beta-envelope", status_twin_2025="owed:beta-envelope",
        status_mc_2025="owed:beta-envelope",
        status_fitter_campaign="owed:beta-envelope", status_twin_campaign="owed:beta-envelope",
        status_mc_campaign="owed:beta-envelope",
        physics="The inelastic exit channel 6S+5S -> 4D+5S (777 cm^-1 released), a collisional "
                "loss channel folded, unresolved, into the empirically fitted beta_self.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="appendix C.4",
        wiki_page="self-broadening.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="rb5s6s/vanderwaals.py's own text: 'the 6S+5S -> 4D+5S channel ... still unsized'",
    ),

    ModelTerm(
        term_id="speed_dependent_collisional_shift",
        status_fitter_2025="owed:speed-dependent-collisions",
        status_twin_2025="owed:speed-dependent-collisions",
        status_mc_2025="owed:speed-dependent-collisions",
        status_fitter_campaign="owed:speed-dependent-collisions",
        status_twin_campaign="owed:speed-dependent-collisions",
        status_mc_campaign="owed:speed-dependent-collisions",
        physics="A collisional shift that depends on the colliding atom's own speed, rather than "
                "the single Voigt every atom shares today (the speed-dependent shift check of 2026-09-25).",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="Table 7.1, as a third-central-moment term (coordinator, 2026-09-25). "
                      "chapter 7 section 7.2.1 still gives every atom the same Voigt",
        wiki_page="self-broadening.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="named the same day this registry was built (2026-09-25). No code exists yet",
    ),

    ModelTerm(
        term_id="speed_dependent_collisional_width",
        status_fitter_2025="owed:speed-dependent-collisions",
        status_twin_2025="owed:speed-dependent-collisions",
        status_mc_2025="owed:speed-dependent-collisions",
        status_fitter_campaign="owed:speed-dependent-collisions",
        status_twin_campaign="owed:speed-dependent-collisions",
        status_mc_campaign="owed:speed-dependent-collisions",
        physics="A collisional width that depends on the colliding atom's own speed, entangled "
                "with speed-selection by optical pumping (owner, 2026-09-25: the beta_self "
                "exponent).",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="none",
        wiki_page="self-broadening.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="named the same day this registry was built (2026-09-25). No code exists yet",
    ),

    ModelTerm(
        term_id="resonant_exchange_by_line_share",
        status_fitter_2025="owed:resonant-exchange-by-line",
        status_twin_2025="owed:resonant-exchange-by-line",
        status_mc_2025="owed:resonant-exchange-by-line",
        status_fitter_campaign="owed:resonant-exchange-by-line",
        status_twin_campaign="owed:resonant-exchange-by-line",
        status_mc_campaign="owed:resonant-exchange-by-line",
        physics="The resonant-exchange contribution to self-broadening varies by which hyperfine "
                "line is driven (the thesis session's M1). Appendix C uses one branch-averaged coefficient "
                "(0.985) for all four.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="appendix C uses the branch average 0.985",
        wiki_page="hyperfine-populations-and-branching.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="named the same day this registry was built (2026-09-25). Appendix C's own "
                 "branch-average is the only treatment on record",
    ),

    ModelTerm(
        term_id="pump_depletion",
        status_fitter_2025="owed:pump-depletion-lineshape",
        status_twin_2025="owed:pump-depletion-lineshape",
        status_mc_2025="owed:pump-depletion-lineshape",
        status_fitter_campaign="owed:pump-depletion-lineshape",
        status_twin_campaign="owed:pump-depletion-lineshape",
        status_mc_campaign="owed:pump-depletion-lineshape",
        physics="Optical pumping's effect on the fitted LINE CENTRE specifically (F514, the thesis session's "
                "M2), distinct from the width-widening cascade_depletion already carries in the MC.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="outline Table 7.1 'two photon absorption 1e-3' is the absorbed fraction only",
        wiki_page="the-cascade-and-f-depletion.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="F514 names the effect. No producer applies a centre-specific pump-depletion "
                 "correction anywhere in this repository",
    ),

    ModelTerm(
        term_id="retro_focus_offset",
        status_fitter_2025="owed:retro-waist", status_twin_2025="owed:retro-waist",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:retro-waist",
        status_twin_campaign="owed:retro-waist", status_mc_campaign="n/a",
        physics="The returning lens (lens 8, f = 150 mm) and its mirror, a distance d behind it, image "
                "the forward focus back onto itself only for a lens one focal length from the atoms and a "
                "mirror at its focal plane. For a lens displaced by delta the round trip is, to first "
                "order, minus a free propagation of 2 delta and a weak lens that vanishes only for d = f, "
                "so the returning focus sits Delta = 2 delta + 2 z_R^2 (f - d)/f^2 away, positive toward "
                "the lens. The owner gives d as 25 to 35 mm (2026-09-25): at d = 30 mm the fixed part is "
                "0.344 mm (0.061 z_R), the power overlap of the two modes 0.99908, and a lens 1 mm out "
                "puts the returning focus 2.34 mm (0.41 z_R) away (probe:1ec2face). At d = f it is 2 delta "
                "alone. The two "
                "arms' shifts and the Rabi frequency sqrt(I_fwd I_ret) then peak at different z, which "
                "reshapes the ramp's distribution and so the odd moments that read alpha. "
                "retro_mismatch is this term's scalar limit.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="retro_focus_offset_m, lens8_displacement_m, mirror_behind_lens8_m",
        thesis_anchor="Section 7.4.2",
        wiki_page="standing-waves.md", methods_page="docs/methods/04_the_composite_model.md",
        evidence="docs/plan/12_open-apparatus-items.md (the returning lens's focus along the beam), "
                 "owed to the campaign's micrometric stage and infrared-viewer check "
                 "(docs/plan/03_optics-protocol.md, section 4.2b2)",
    ),

    ModelTerm(
        term_id="sweep_axis_curvature",
        status_fitter_2025="owed:axis-curvature", status_twin_2025="owed:axis-curvature",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:axis-curvature",
        status_twin_campaign="owed:axis-curvature", status_mc_campaign="n/a",
        physics="The frequency axis the traces are read on is not exactly linear: the ruler's "
                "non-linearity map reads a curvature in its interior bins, and a quadratic term in the "
                "axis turns an even moment of the line into a spurious odd one, degenerate at first "
                "order with the ramp's own asymmetry. The prior is the ruler's two bins that bracket "
                "the lines' own times in the sweep, not a fit across the interior, whose leverage "
                "reaches far past them (the thesis side's reading of 2026-09-25, not yet re-obtained "
                "here). The ripple below the 12.5 MHz teeth is what the marker still owes.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="axis_curvature_per_mhz",
        thesis_anchor="Section 7.3.3",
        wiki_page="the-wavemeter-and-the-frequency-axis.md",
        methods_page="docs/methods/05_the_frequency_ruler.md",
        evidence="results/ruler_nlmap.csv: the two bins that bracket the lines' own sweep times, the "
                 "prior this term would carry. No committed fit carries a curvature term "
                 "(scripts/run_ultra_joint.py:Cell)",
    ),

    ModelTerm(
        term_id="amplitude_slope",
        status_fitter_2025="owed:axis-curvature", status_twin_2025="owed:axis-curvature",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:axis-curvature",
        status_twin_campaign="owed:axis-curvature", status_mc_campaign="n/a",
        physics="A gain or drive power drifting linearly across the sweep multiplies the line by "
                "(1 + a delta), which moves the centroid by a mu2 and the third central moment by "
                "a (mu4 - 3 mu2^2), the line's fourth cumulant, at first order: an odd moment made from "
                "the even ones, degenerate with the ramp's asymmetry exactly where alpha is read.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="amplitude_slope_per_mhz",
        thesis_anchor="Section 7.3.3",
        wiki_page="the-wavemeter-and-the-frequency-axis.md",
        methods_page="docs/methods/05_the_frequency_ruler.md",
        evidence="the same ruler and detection chain as sweep_axis_curvature. No committed fit "
                 "carries a slope term (scripts/run_ultra_joint.py:Cell)",
    ),

    ModelTerm(
        term_id="quadratic_zeeman",
        status_fitter_2025="owed:quadratic-zeeman", status_twin_2025="owed:quadratic-zeeman",
        status_mc_2025="n/a",
        status_fitter_campaign="owed:quadratic-zeeman",
        status_twin_campaign="owed:quadratic-zeeman", status_mc_campaign="n/a",
        physics="In a field B the m_F = 0 components shift by +-(g_J mu_B B)^2 (1/dE_6S - 1/dE_5S)/4, "
                "positive on the F = I + 1/2 line and negative on the F = I - 1/2 line: 0.929 kHz for "
                "87Rb and 2.091 kHz for 85Rb at 1 G, so each isotope's pair separates by 1.857 and "
                "4.182 kHz per G^2 (probe:672aba88). It moves each line's centre, which the free centre "
                "absorbs, and the spread of the m_F components is a width far below the collisional one "
                "at a few gauss. A resistive heater's field squared scales with its power, roughly T - "
                "T_amb, about twofold from 70 to 130 C while the density grows about fiftyfold, so it "
                "cannot mimic beta_self. The field at the cell was not recorded.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="B_gauss",
        thesis_anchor="Appendix A.12",
        wiki_page="magnetic-sublevels.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="probe:672aba88",
    ),

    ModelTerm(
        term_id="population_lens",
        status_fitter_2025="owed:population-lens", status_twin_2025="owed:population-lens",
        status_mc_2025="owed:population-lens",
        status_fitter_campaign="owed:population-lens", status_twin_campaign="owed:population-lens",
        status_mc_campaign="owed:population-lens",
        physics="A dispersive, population-grating lensing effect from the driven population's own "
                "spatial structure (the thesis session's M2), about half the size of the dispersive Kerr peak "
                "at the archive's own power and waist.",
        impl_fitter="-", impl_twin="-", impl_mc="-",
        param_keys="-",
        thesis_anchor="none",
        wiki_page="the-beam-waist.md", methods_page="docs/methods/08_assumptions_and_outlook.md",
        evidence="named the same day this registry was built (2026-09-25). No code exists yet",
    ),

)

TERM_IDS: tuple[str, ...] = tuple(row.term_id for row in REGISTRY)

if len(TERM_IDS) != len(set(TERM_IDS)):
    dupes = sorted({t for t in TERM_IDS if TERM_IDS.count(t) > 1})
    raise ValueError(f"REGISTRY has duplicate term_id(s): {dupes}")

_BY_ID: dict = {row.term_id: row for row in REGISTRY}


# ---------------------------------------------------------------------------
# Digests
# ---------------------------------------------------------------------------

def executed_digest(term_ids: Iterable[str]) -> str:
    """The first 16 hex of sha256 over the sorted ids, joined by newlines.

    Deterministic in the ids' CONTENT and never in the caller's own iteration order, so two
    equal sets always agree and a set differing by one member never does (asserted in
    `tests/test_model_registry.py`)."""
    joined = "\n".join(sorted(set(term_ids)))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


def carried_term_ids(consumer: str, regime: str) -> tuple[str, ...]:
    """Every term_id whose `status_<consumer>_<regime>` kind is `carried`."""
    if consumer not in CONSUMERS:
        raise ValueError(f"unknown consumer {consumer!r}; expected one of {CONSUMERS}")
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r}; expected one of {REGIMES}")
    attr = f"status_{consumer}_{regime}"
    return tuple(sorted(
        row.term_id for row in REGISTRY if kind_of(getattr(row, attr)) == "carried"))


def registry_digest() -> str:
    """`executed_digest` of the twin's 2025 carried set: the model of record."""
    return executed_digest(carried_term_ids("twin", "2025"))


def registry_content_digest() -> str:
    """The digest of the registry's whole STATEMENT: every term id and every one of its six statuses, in row order.

    `registry_digest` stamps what a computation CARRIED (the twin's 2025 carried set), so a term added as owed or a
    status moved between absorbed and owed leaves it unchanged, correctly: no table computed with the carried set
    changed its model. What did change is what the registry SAYS about the model, and a reader keyed on that (the thesis
    side's model_sync, 2026-09-26) needs a digest that moves with every status. This is that digest; the two are stated
    side by side, and neither stands in for the other."""
    rows = [[row.term_id] + [str(getattr(row, f)) for f in STATUS_FIELDS] for row in REGISTRY]
    return hashlib.sha256("\n".join("\t".join(r) for r in rows).encode("utf-8")).hexdigest()[:16]


def consumer_digest(consumer: str, regime: str) -> str:
    """`executed_digest` of one path's carried set at one regime."""
    return executed_digest(carried_term_ids(consumer, regime))


# ---------------------------------------------------------------------------
# The executed-term ledger (planted, not yet wired into the model modules)
# ---------------------------------------------------------------------------

class ModelReduced(Exception):
    """A run claimed a consumer/regime but silently dropped one of its carried terms."""


@dataclass
class _RunState:
    consumer: str
    regime: str
    scope: str = "result"
    executed: set = field(default_factory=set)
    reason: Optional[str] = None
    dropped: tuple = ()


_CURRENT: "contextvars.ContextVar[Optional[_RunState]]" = contextvars.ContextVar(
    "rb5s6s_model_registry_current", default=None)


def _require_state(caller: str) -> _RunState:
    state = _CURRENT.get()
    if state is None:
        raise RuntimeError(f"{caller}() was called outside model_registry.run(...)")
    return state


@contextlib.contextmanager
def run(consumer: str, regime: str, scope: str = "result"):
    """Open the executed-term ledger for one run of one consumer at one regime.

    `scope` is `"result"` by default (a run standing behind a committed number) or `"ablation"`
    (a deliberate partial run; `ablation()` below is the sanctioned way to reach that scope, since
    it also demands a reason)."""
    if consumer not in CONSUMERS:
        raise ValueError(f"unknown consumer {consumer!r}; expected one of {CONSUMERS}")
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r}; expected one of {REGIMES}")
    state = _RunState(consumer=consumer, regime=regime, scope=scope)
    token = _CURRENT.set(state)
    try:
        yield state
    finally:
        _CURRENT.reset(token)


def executed(term_id: str, strength) -> None:
    """Record `term_id` as executed by the current run, iff `strength` is truthy and non-zero.

    Refuses an unknown term_id regardless of `strength`, so a typo cannot be silently ignored by
    passing a falsy strength alongside it."""
    if term_id not in _BY_ID:
        raise ValueError(f"executed(): unknown term_id {term_id!r}; not in the registry")
    state = _require_state("executed")
    if strength:
        state.executed.add(term_id)


def current() -> Optional[_RunState]:
    """The open run's state, or None outside `run(...)`."""
    return _CURRENT.get()


def require() -> None:
    """Raise `ModelReduced` naming every carried term of the run's own consumer and regime that
    was not executed; a term named in an `ablation()` drop is exempted, since that is what
    licenses the deviation."""
    state = _require_state("require")
    carried = set(carried_term_ids(state.consumer, state.regime))
    missing = sorted((carried - state.executed) - set(state.dropped))
    if missing:
        raise ModelReduced(
            f"{state.consumer}/{state.regime}: carried term(s) not executed this run: "
            f"{', '.join(missing)}")


def ablation(reason: str, drop: Sequence[str]) -> None:
    """Stamp the current run `scope='ablation'`, licensing `require()` to exempt `drop`.

    `reason` must carry at least six words, matching the mc_contract convention this repository
    already uses for a declared deviation."""
    state = _require_state("ablation")
    if len(reason.split()) < 6:
        raise ValueError(
            f"ablation() needs a reason of at least six words, got {reason.split()!r}")
    unknown = [d for d in drop if d not in _BY_ID]
    if unknown:
        raise ValueError(f"ablation(): unknown term_id(s) in drop: {unknown}")
    state.scope = "ablation"
    state.reason = reason
    state.dropped = tuple(drop)


def manifest() -> dict:
    """The current run's manifest: consumer, regime, scope, what was executed, and both digests."""
    state = _require_state("manifest")
    return {
        "consumer": state.consumer,
        "regime": state.regime,
        "scope": state.scope,
        "executed": sorted(state.executed),
        "model_digest": executed_digest(state.executed),
        "registry_digest": registry_digest(),
    }


# ---------------------------------------------------------------------------
# The preflight (O58): a twin or Monte Carlo run refuses at its start unless it is the registry's
# ---------------------------------------------------------------------------

#: THE TWIN AND THE MONTE CARLO MAY ONLY COME TOGETHER. The terms one of the two carries and the
#: other does not, frozen at the registry of 2026-09-25: a registry edit that adds a divergence is
#: refused at the start of every twin and Monte Carlo computation, and a paydown shrinks this set in
#: the same commit. Plan V6.1's single full model is what empties it. Raising it is a raising
#: reseed and needs the owner's word (the rule file's reseed door).
PAIRING_BASELINE: dict = {
    "2025": frozenset({
        "companion_pull_reduction", "depletion_cascade", "hyperfine_pumping",
        "hyperfine_shares", "laser_kernel", "saturation", "self_broadening_vdw", "transit_chirp"}),
    "campaign": frozenset({
        "companion_pull_reduction", "hyperfine_pumping", "hyperfine_shares",
        "laser_kernel", "saturation", "self_broadening_vdw", "transit_chirp"}),
}

#: THE SAME TERM THROUGH DIFFERENT CODE IS NOT THE SAME MODEL. The terms both paths carry whose
#: `impl_twin` and `impl_mc` name different code sites, frozen the same day and under the same
#: rule: every shared term runs through `volume_line` on the twin and `run_kernel_mc` on the Monte
#: Carlo today, and the single full model makes both name one site. So a PAYDOWN moves a term onto ONE
#: code site: carrying it on the twin through a second implementation of what the Monte Carlo already
#: does trades a pairing debt for a code debt, and the second ratchet refuses it.
IMPL_BASELINE: dict = {
    "2025": frozenset({"ac_stark_ramp", "axial_collection_window", "beam_quality_m2", "natural_width",
                       "transit"}),
    "campaign": frozenset({"ac_stark_ramp", "axial_collection_window", "beam_quality_m2",
                           "natural_width", "transit"}),
}

#: the kinds a declared study may ADD to a path: everything the registry names as outside the
#: path's committed results except `n/a`, which is outside the method's own scope
_ADDABLE_KINDS = ("owed", "neglected", "absorbed")


def pairing_gaps(regime: str) -> dict:
    """{term_id: (status_twin, status_mc)} for every term exactly one of the twin and the Monte
    Carlo carries at `regime`."""
    tw = set(carried_term_ids("twin", regime))
    mc = set(carried_term_ids("mc", regime))
    return {t: (getattr(_BY_ID[t], f"status_twin_{regime}"), getattr(_BY_ID[t], f"status_mc_{regime}"))
            for t in sorted(tw ^ mc)}


def impl_gaps(regime: str) -> dict:
    """{term_id: (impl_twin, impl_mc)} for every term BOTH paths carry at `regime` through
    different code sites."""
    both = set(carried_term_ids("twin", regime)) & set(carried_term_ids("mc", regime))
    return {t: (_BY_ID[t].impl_twin, _BY_ID[t].impl_mc) for t in sorted(both)
            if _BY_ID[t].impl_twin != _BY_ID[t].impl_mc}


def _pairing_refusals(regime: str) -> list:
    bad = []
    gaps = pairing_gaps(regime)
    for t, (st_tw, st_mc) in gaps.items():
        other, st = ("mc", st_mc) if kind_of(st_tw) == "carried" else ("twin", st_tw)
        if kind_of(st) not in ("owed", "n/a"):
            bad.append(f"pairing: {t} is carried by one path and {st!r} on the {other}, "
                       "neither owed nor n/a")
    grown = sorted(set(gaps) - PAIRING_BASELINE[regime])
    if grown:
        bad.append(f"pairing ratchet: {', '.join(grown)} now divide(s) the twin from the Monte Carlo "
                   f"at {regime}, beyond the frozen baseline; the two paths may only come together")
    split = sorted(set(impl_gaps(regime)) - IMPL_BASELINE[regime])
    if split:
        bad.append(f"code ratchet: {', '.join(split)} now run(s) through different code on the twin "
                   f"and the Monte Carlo at {regime}, beyond the frozen baseline")
    return bad


def preflight(consumer: str, regime: str, executes: Iterable[str], *, scope: str = "result",
              gaps: Optional[dict] = None, extras: Optional[dict] = None) -> dict:
    """Refuse a twin, fitter or Monte Carlo run BEFORE its first atom unless its term set is the
    registry's (O58). Returns the block a manifest carries.

    `executes` is the set of registry term ids the configured run WILL execute, derived by the
    caller from its own knobs before it computes. With `scope="result"` (a run standing behind a
    quoted number) it must equal `carried_term_ids(consumer, regime)` exactly. With
    `scope="study"` (a run that switches terms on purpose, a term budget or an ablation) every
    carried term it drops is named in `gaps` and every term it adds in `extras`, each with a
    reason of six words or more; an added term must be a registry term the path does not carry
    and whose kind is not `n/a`. Whatever the scope, the registry's own pairing must hold: every
    term only one path carries is `owed` or `n/a` on the other, and neither ratchet has grown.
    """
    if consumer not in CONSUMERS:
        raise ValueError(f"unknown consumer {consumer!r}; expected one of {CONSUMERS}")
    if regime not in REGIMES:
        raise ValueError(f"unknown regime {regime!r}; expected one of {REGIMES}")
    if scope not in ("result", "study"):
        raise ValueError(f"unknown scope {scope!r}; expected 'result' or 'study'")
    gaps, extras = dict(gaps or {}), dict(extras or {})
    ex = set(executes)
    carried = set(carried_term_ids(consumer, regime))
    attr = f"status_{consumer}_{regime}"
    bad = []
    unknown = sorted(t for t in ex | set(gaps) | set(extras) if t not in _BY_ID)
    if unknown:
        bad.append(f"unknown term id(s): {', '.join(unknown)}")
    if scope == "result" and (gaps or extras):
        bad.append("a result run declares no gaps and no extras: it is the registry's model or it "
                   "is a study (scope='study')")
    for label, table in (("gap", gaps), ("extra", extras)):
        for t, why in table.items():
            if len(str(why).split()) < 6:
                bad.append(f"{label} {t!r}: its reason is under six words")
    for t in gaps:
        if t in _BY_ID and t not in carried:
            bad.append(f"gap {t!r} is not carried by {consumer}/{regime}, so there is nothing to drop")
    for t in extras:
        if t in _BY_ID:
            k = kind_of(getattr(_BY_ID[t], attr))
            if t in carried:
                bad.append(f"extra {t!r} is already carried by {consumer}/{regime}")
            elif k not in _ADDABLE_KINDS:
                bad.append(f"extra {t!r} is {k!r} for {consumer}/{regime}, outside the path's scope")
    missing = sorted(carried - ex - set(gaps))
    if missing:
        bad.append(f"carried term(s) the run will not execute and does not declare: "
                   f"{', '.join(missing)}")
    beyond = sorted(t for t in ex - carried - set(extras) if t in _BY_ID)
    if beyond:
        bad.append(f"term(s) the run executes that {consumer}/{regime} does not carry and the run "
                   f"does not declare: {', '.join(beyond)} (update the registry, or declare a study)")
    bad += _pairing_refusals(regime)
    if bad:
        raise ModelReduced(f"preflight {consumer}/{regime} ({scope}) REFUSED: " + "; ".join(bad))
    return {"consumer": consumer, "regime": regime, "scope": scope, "executes": sorted(ex),
            "gaps": gaps, "extras": extras, "executed_digest": executed_digest(ex),
            "consumer_digest": consumer_digest(consumer, regime), "registry_digest": registry_digest()}


# ---------------------------------------------------------------------------
# The census cross-check
# ---------------------------------------------------------------------------

#: term_id -> the results/twin_term_census.csv `term` value(s) the thesis seed's own `census_row`
#: column names, or () where the seed states NONE (no census row exists, so the term is outside
#: the census's reach and is not checked). Several rows are joined where the seed names more than
#: one census row for a single thesis term_id.
CENSUS_ROW_FOR: dict = {
    "natural_width": (),
    "transit": ("transit_cusp",),
    "transit_chirp": (),
    "laser_kernel": ("laser_kernel_both_forms", "laser_kernel_lorentzian_component"),
    "self_broadening_vdw": ("lorentzian_core_collisional",),
    "self_broadening_T03": (),
    "foreign_gas": ("foreign_gas_permeated",),
    "ac_stark_ramp": ("ac_stark_ramp",),
    "doppler_pedestal": ("doppler_pedestal",),
    "saturation": ("saturation_companions", "saturation_parameterised_by_rabi"),
    "hyperfine_pumping": (),
    "companion_pull_reduction": (),
    "axial_collection_window": ("axial_collection_window",),
    "bore_clipping": ("eom_aperture_profile",),
    "retro_mismatch": (),
    "retro_offset": (),
    "fringe_tail": ("standing_wave_fringe_tail",),
    "retro_tilt": ("retro_tilt_residual_doppler",),
    "beam_quality_m2": ("beam_quality_m2",),
    "collisional_shift": (),
    "second_order_doppler": (),
    "blackbody": ("blackbody", "radiation_temperature_separate"),
    "two_photon_absorption": (),
    "kerr_lens": (),
    "radiation_trapping": ("radiation_trapping",),
    "photoionisation": (),
    "depletion_cascade": ("cascade_depletion",),
    "hyperfine_shares": ("hyperfine_F_statistics",),
    "quench_4D": (),
    "speed_dependent_collisional_shift": (),
    "speed_dependent_collisional_width": (),
    "resonant_exchange_by_line_share": (),
    "pump_depletion": (),
    "population_lens": (),
    "retro_focus_offset": (),
    "sweep_axis_curvature": (),
    "amplitude_slope": (),
    "quadratic_zeeman": (),
}

if set(CENSUS_ROW_FOR) != set(TERM_IDS):
    raise ValueError("CENSUS_ROW_FOR must name exactly the registry's own term_ids")


def _census_fitter_says_yes(fitter_cell: str) -> bool:
    """The census's own free-text `fitter` column, read as a boolean.

    A cell starting with 'yes' (however qualified: 'yes, form assumed', "yes, fit_full "
    "free=(...)") or exactly 'optional' reads as the census asserting the fitter CAN and, in some
    committed configuration, DOES carry the term. Everything else -- 'no', 'stated: deliberately "
    "absent...', 'n/a, ...', a bare '-', an absorption sentence with no 'yes' -- reads as no."""
    text = fitter_cell.strip()
    low = text.lower()
    return low.startswith("yes") or low == "optional"


def census_says_fitter_carries(term_id: str, census_csv_path: "str | Path") -> Optional[bool]:
    """Whether `results/twin_term_census.csv`'s own `fitter` column says the fitter carries
    `term_id`, ORed across every census row the seed maps it to. Returns None when the seed maps
    the term to no census row at all (CENSUS_ROW_FOR[term_id] == ()), which is outside the
    census's reach and is never checked."""
    if term_id not in CENSUS_ROW_FOR:
        raise ValueError(f"unknown term_id {term_id!r}")
    rows = CENSUS_ROW_FOR[term_id]
    if not rows:
        return None
    by_term: dict = {}
    with open(census_csv_path, newline="", encoding="utf-8") as fh:
        for record in csv.DictReader(fh):
            by_term[record["term"]] = record.get("fitter", "")
    missing = [r for r in rows if r not in by_term]
    if missing:
        raise KeyError(
            f"{term_id}: census row(s) {missing} named by the thesis seed are not in "
            f"{census_csv_path}; the census population moved and the mapping is stale")
    return any(_census_fitter_says_yes(by_term[r]) for r in rows)


class CensusDisagreement(Exception):
    """The registry's status_fitter_2025 contradicts the census's own `fitter` column."""


def check_census_agreement(census_csv_path: "str | Path" = "results/twin_term_census.csv") -> None:
    """Refuse two shapes of contradiction between this registry and the code-inspected census:

    * the census says the fitter carries a term whose `status_fitter_2025` here is `owed` or
      `neglected` (a term the census read as live that this registry calls a debt or a sized
      absence);
    * this registry marks `status_fitter_2025` `carried` for a term the census says the fitter
      does not carry at all.

    `absorbed` and `n/a` disagree with neither direction: a term the census reads as carried and
    this registry reads as absorbed into another free parameter is not a contradiction, it is a
    more precise reading of the same 'yes'."""
    disagreements = []
    for row in REGISTRY:
        census_yes = census_says_fitter_carries(row.term_id, census_csv_path)
        if census_yes is None:
            continue
        kind = kind_of(row.status_fitter_2025)
        if census_yes and kind in ("owed", "neglected"):
            disagreements.append(
                f"{row.term_id}: the census says the fitter carries this term, but "
                f"status_fitter_2025={row.status_fitter_2025!r}")
        if (not census_yes) and kind == "carried":
            disagreements.append(
                f"{row.term_id}: status_fitter_2025='carried', but the census says the fitter "
                "does not carry this term")
    if disagreements:
        raise CensusDisagreement("; ".join(disagreements))


# ---------------------------------------------------------------------------
# CSV / docs rendering (scripts/make_model_terms.py calls these)
# ---------------------------------------------------------------------------

CSV_COLUMNS: tuple[str, ...] = tuple(f.name for f in fields(ModelTerm)) + ("registry_digest",)


def to_csv_rows() -> list:
    """Every registry row as a dict keyed by `CSV_COLUMNS`, the same `registry_digest` value on
    every row (the model of record's own digest, so a reader can tell at a glance whether the
    committed CSV was generated from the module version it claims)."""
    digest = registry_digest()
    rows = []
    for row in REGISTRY:
        record = {f.name: getattr(row, f.name) for f in fields(ModelTerm)}
        record["registry_digest"] = digest
        rows.append(record)
    return rows
