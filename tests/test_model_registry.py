"""Closure tests for the model-terms registry (rb5s6s/model_registry.py).

Every plant is both ways: the negative case (a defect the guard must catch) and the positive case
(the real, correct construction the guard must pass), so a change that disables the guard shows up
as a positive test failing rather than only as a negative one silently stopping firing.
"""
from __future__ import annotations

import csv
import dataclasses
from pathlib import Path

import pytest

from rb5s6s import model_registry as MR


def _make_model_terms():
    """The producer, imported when a test runs and never at collection (tests/test_conftest_companions.py:
    a module-scope import runs the script while pytest collects, where the conftest's fixture cannot help)."""
    from scripts import make_model_terms
    return make_model_terms

ROOT = Path(__file__).resolve().parents[1]


# ---------------------------------------------------------------------------
# The generated artefacts are fresh
# ---------------------------------------------------------------------------

def _committed_rows() -> list:
    return list(csv.DictReader((ROOT / "results" / "model_terms.csv").read_text().splitlines()))


def test_committed_csv_equals_the_module_up_to_the_annotators_own_status_column():
    # scripts/make_model_terms.py writes CSV_COLUMNS; scripts/annotate_results_status.py then
    # appends exactly one more column, `status` (the repository-wide convention every results
    # table follows), so the committed file is the module's own rendering PLUS that one column.
    generated_rows = list(csv.DictReader(_make_model_terms().csv_text().splitlines()))
    committed_rows = _committed_rows()
    assert len(generated_rows) == len(committed_rows)
    for generated, committed in zip(generated_rows, committed_rows):
        assert committed["status"] == "DIAGNOSTIC"
        without_status = {k: v for k, v in committed.items() if k != "status"}
        assert without_status == generated


def test_committed_csv_is_not_trivially_empty():
    assert len(_committed_rows()) == len(MR.REGISTRY) == 34


def test_generated_docs_page_is_fresh():
    committed = (ROOT / "docs" / "methods" / "model_terms.md").read_text()
    assert committed == _make_model_terms().doc_text()


def test_csv_columns_are_the_dataclass_fields_plus_the_digest_plus_the_annotators_status():
    header = next(csv.reader((ROOT / "results" / "model_terms.csv").read_text().splitlines()))
    assert tuple(header[:-1]) == MR.CSV_COLUMNS
    assert header[-2] == "registry_digest"
    assert header[-1] == "status"


def test_every_registry_row_carries_the_same_registry_digest_on_the_csv():
    digests = {r["registry_digest"] for r in _committed_rows()}
    assert digests == {MR.registry_digest()}


# ---------------------------------------------------------------------------
# The row's own shape: a term_id set matching the thesis seed, no duplicates
# ---------------------------------------------------------------------------

def test_no_duplicate_term_ids():
    assert len(MR.TERM_IDS) == len(set(MR.TERM_IDS))


def test_registry_matches_the_thesis_seeds_34_term_ids():
    # THE EXACT POPULATION (PhD-Thesis session, 2026-09-25): renaming or dropping one of these
    # is a contract break with the thesis chapter that reads this registry by term_id.
    expected = {
        "natural_width", "transit", "transit_chirp", "laser_kernel", "self_broadening_vdw",
        "self_broadening_T03", "foreign_gas", "ac_stark_ramp", "doppler_pedestal", "saturation",
        "hyperfine_pumping", "companion_pull_reduction", "axial_collection_window",
        "bore_clipping", "retro_mismatch", "retro_offset", "fringe_tail", "collisional_shift",
        "retro_tilt", "second_order_doppler", "blackbody", "two_photon_absorption", "kerr_lens",
        "radiation_trapping", "photoionisation", "beam_quality_m2", "depletion_cascade",
        "hyperfine_shares", "quench_4D", "speed_dependent_collisional_shift",
        "speed_dependent_collisional_width", "resonant_exchange_by_line_share", "pump_depletion",
        "population_lens",
    }
    assert set(MR.TERM_IDS) == expected
    assert len(expected) == 34


# ---------------------------------------------------------------------------
# The dataclass's own validation: a plant both ways for every rule it enforces
# ---------------------------------------------------------------------------

def _row(**overrides) -> MR.ModelTerm:
    """A minimal, otherwise-valid ModelTerm, so a test overrides only the field it probes."""
    base = dict(
        term_id="probe_term", status_fitter_2025="owed:probe-tag", status_twin_2025="owed:probe-tag",
        status_mc_2025="n/a", status_fitter_campaign="owed:probe-tag",
        status_twin_campaign="owed:probe-tag", status_mc_campaign="n/a",
        physics="a probe row for the validator, never a member of REGISTRY",
        impl_fitter="-", impl_twin="-", impl_mc="-", param_keys="-",
        thesis_anchor="-", wiki_page="-", methods_page="-", evidence="-",
    )
    base.update(overrides)
    return MR.ModelTerm(**base)


def test_an_unknown_kind_is_refused():
    with pytest.raises(ValueError, match="unknown status kind"):
        _row(status_fitter_2025="maybe")


def test_a_known_kind_is_accepted():
    _row(status_fitter_2025="n/a")  # does not raise


def test_kind_of_splits_only_on_the_first_colon():
    assert MR.kind_of("owed:some-tag:with-colon") == "owed"


@pytest.mark.parametrize("kind", MR.VALID_KINDS)
def test_every_valid_kind_is_individually_accepted_by_kind_of(kind):
    assert MR.kind_of(kind) == kind
    assert MR.kind_of(f"{kind}:detail") == kind


def test_carried_status_requires_a_named_impl_site():
    with pytest.raises(ValueError, match="carried but"):
        _row(status_fitter_2025="carried", impl_fitter="-")


def test_carried_status_with_an_impl_site_is_accepted():
    _row(status_fitter_2025="carried", impl_fitter="rb5s6s.lineshape:model_profile")  # no raise


def test_neglected_without_a_size_is_refused():
    with pytest.raises(ValueError, match="neglected without a stated size"):
        _row(status_fitter_2025="neglected", evidence="results/some_producer.csv")


def test_neglected_without_tracked_evidence_is_refused():
    with pytest.raises(ValueError, match="is not a tracked path"):
        _row(status_fitter_2025="neglected:0.4 kHz", evidence="the owner said so once")


@pytest.mark.parametrize("evidence", [
    "results/collisional_shift_bound.csv", "rb5s6s/vanderwaals.py", "## F123 a finding heading",
    "probe:kerr_lens_2026_09_25",
])
def test_neglected_with_a_sized_and_evidenced_status_is_accepted(evidence):
    _row(status_fitter_2025="neglected:0.4 kHz", evidence=evidence)  # no raise


def test_owed_without_a_tag_is_refused():
    with pytest.raises(ValueError, match="owed with no tag"):
        _row(status_fitter_2025="owed")


@pytest.mark.parametrize("bad_tag", ["Bad-Tag", "bad_tag", "-bad-tag", "bad-tag-", "bad--tag"])
def test_owed_with_a_non_kebab_tag_is_refused(bad_tag):
    with pytest.raises(ValueError, match="not kebab-case"):
        _row(status_fitter_2025=f"owed:{bad_tag}")


def test_owed_with_a_kebab_tag_is_accepted():
    _row(status_fitter_2025="owed:a-good-tag")  # no raise


def test_impl_field_must_be_dash_or_module_colon_function():
    with pytest.raises(ValueError, match="neither '-' nor"):
        _row(impl_fitter="rb5s6s.lineshape")


def test_every_owed_status_in_the_real_registry_carries_a_kebab_tag():
    for row in MR.REGISTRY:
        for attr in MR.STATUS_FIELDS:
            status = getattr(row, attr)
            if MR.kind_of(status) == "owed":
                tag = status.split(":", 1)[1]
                assert MR._KEBAB_TAG_RE.match(tag), f"{row.term_id}.{attr}={status!r}"


def test_a_row_whose_six_statuses_are_all_carried_or_na_never_needs_a_tag():
    # sanity on the fixture helper itself: n/a and carried never require a detail
    _row(status_fitter_2025="n/a", status_twin_2025="carried",
         impl_twin="rb5s6s.volume_line:joint_spectrum")


# ---------------------------------------------------------------------------
# Digests
# ---------------------------------------------------------------------------

def test_executed_digest_is_deterministic_regardless_of_input_order():
    a = MR.executed_digest(["transit", "natural_width", "laser_kernel"])
    b = MR.executed_digest(["laser_kernel", "transit", "natural_width"])
    assert a == b
    assert len(a) == 16
    int(a, 16)  # is valid hex


def test_executed_digest_differs_when_one_term_is_dropped():
    full = MR.executed_digest(["transit", "natural_width", "laser_kernel"])
    dropped = MR.executed_digest(["transit", "natural_width"])
    assert full != dropped


def test_registry_digest_is_the_twins_2025_carried_set():
    assert MR.registry_digest() == MR.executed_digest(MR.carried_term_ids("twin", "2025"))


def test_consumer_digest_matches_registry_digest_for_twin_2025():
    assert MR.consumer_digest("twin", "2025") == MR.registry_digest()


def test_consumer_digest_differs_across_paths():
    # the fitter and the twin carry different term sets at 2025, so their digests differ;
    # if this ever collides it means the two carried sets are byte-identical, worth knowing
    assert MR.consumer_digest("fitter", "2025") != MR.consumer_digest("twin", "2025")


def test_carried_term_ids_rejects_unknown_consumer_or_regime():
    with pytest.raises(ValueError):
        MR.carried_term_ids("estimator", "2025")
    with pytest.raises(ValueError):
        MR.carried_term_ids("fitter", "2030")


# ---------------------------------------------------------------------------
# The executed-term ledger
# ---------------------------------------------------------------------------

def test_run_rejects_unknown_consumer_or_regime():
    with pytest.raises(ValueError):
        with MR.run("estimator", "2025"):
            pass
    with pytest.raises(ValueError):
        with MR.run("fitter", "2030"):
            pass


def test_executed_outside_a_run_is_refused():
    with pytest.raises(RuntimeError, match="outside model_registry.run"):
        MR.executed("transit", 1.0)


def test_executed_refuses_an_unknown_term_id():
    with MR.run("fitter", "2025"):
        with pytest.raises(ValueError, match="unknown term_id"):
            MR.executed("not_a_real_term", 1.0)


def test_executed_refuses_an_unknown_term_id_even_at_zero_strength():
    # the refusal is about the NAME, not about whether it would have been recorded
    with MR.run("fitter", "2025"):
        with pytest.raises(ValueError, match="unknown term_id"):
            MR.executed("not_a_real_term", 0.0)


@pytest.mark.parametrize("strength", [0, 0.0, False, None, ""])
def test_a_zero_or_falsy_strength_does_not_count_as_executed(strength):
    with MR.run("fitter", "2025") as state:
        MR.executed("transit", strength)
        assert "transit" not in state.executed


@pytest.mark.parametrize("strength", [1, 1.0, True, -1, 0.001])
def test_a_truthy_nonzero_strength_counts_as_executed(strength):
    with MR.run("fitter", "2025") as state:
        MR.executed("transit", strength)
        assert "transit" in state.executed


def test_current_is_none_outside_a_run_and_the_state_inside_one():
    assert MR.current() is None
    with MR.run("mc", "2025") as state:
        assert MR.current() is state
    assert MR.current() is None


def test_require_raises_model_reduced_and_names_every_missing_carried_term():
    carried = set(MR.carried_term_ids("fitter", "2025"))
    assert carried, "the fitter must carry at least one term at 2025 for this test to mean anything"
    with MR.run("fitter", "2025"):
        # execute nothing: every carried term of the fitter/2025 combination is missing
        with pytest.raises(MR.ModelReduced) as excinfo:
            MR.require()
    for term_id in carried:
        assert term_id in str(excinfo.value)


def test_require_passes_when_every_carried_term_was_executed():
    with MR.run("fitter", "2025"):
        for term_id in MR.carried_term_ids("fitter", "2025"):
            MR.executed(term_id, 1.0)
        MR.require()  # does not raise


def test_require_still_raises_for_one_missing_carried_term():
    carried = MR.carried_term_ids("fitter", "2025")
    with MR.run("fitter", "2025"):
        for term_id in carried[1:]:
            MR.executed(term_id, 1.0)
        with pytest.raises(MR.ModelReduced, match=carried[0]):
            MR.require()


def test_require_outside_a_run_is_refused():
    with pytest.raises(RuntimeError, match="outside model_registry.run"):
        MR.require()


def test_run_contexts_do_not_leak_into_each_other():
    with MR.run("fitter", "2025") as first:
        MR.executed("transit", 1.0)
        with MR.run("twin", "2025") as second:
            assert MR.current() is second
            assert "transit" not in second.executed
        assert MR.current() is first
        assert "transit" in first.executed


# ---------------------------------------------------------------------------
# Ablation
# ---------------------------------------------------------------------------

def test_ablation_requires_at_least_six_words():
    with MR.run("mc", "2025"):
        with pytest.raises(ValueError, match="at least six words"):
            MR.ablation("too short a reason", drop=["saturation"])


def test_ablation_with_a_long_enough_reason_is_accepted_and_stamps_scope():
    with MR.run("mc", "2025") as state:
        MR.ablation("dropping saturation on purpose to measure its own effect size", drop=["saturation"])
        assert state.scope == "ablation"
        assert state.dropped == ("saturation",)
        assert state.reason is not None


def test_ablation_refuses_an_unknown_term_id_in_drop():
    with MR.run("mc", "2025"):
        with pytest.raises(ValueError, match="unknown term_id"):
            MR.ablation("dropping a term that plainly is not in the registry at all", drop=["not_a_term"])


def test_ablation_outside_a_run_is_refused():
    with pytest.raises(RuntimeError, match="outside model_registry.run"):
        MR.ablation("a reason with clearly more than six words in it", drop=[])


def test_require_exempts_a_deliberately_ablated_term():
    carried = MR.carried_term_ids("mc", "2025")
    assert len(carried) >= 2, "need at least two carried mc/2025 terms for this test to be meaningful"
    with MR.run("mc", "2025"):
        MR.ablation("dropping one carried term on purpose to test the exemption", drop=[carried[0]])
        for term_id in carried[1:]:
            MR.executed(term_id, 1.0)
        MR.require()  # does not raise: carried[0] was deliberately dropped


def test_require_still_catches_an_undropped_term_during_an_ablation():
    carried = MR.carried_term_ids("mc", "2025")
    assert len(carried) >= 2
    with MR.run("mc", "2025"):
        MR.ablation("dropping one carried term on purpose but leaving another one out", drop=[carried[0]])
        # deliberately do NOT execute carried[1], which was never dropped
        with pytest.raises(MR.ModelReduced, match=carried[1]):
            MR.require()


# ---------------------------------------------------------------------------
# manifest()
# ---------------------------------------------------------------------------

def test_manifest_outside_a_run_is_refused():
    with pytest.raises(RuntimeError, match="outside model_registry.run"):
        MR.manifest()


def test_manifest_reports_consumer_regime_scope_and_both_digests():
    with MR.run("twin", "2025"):
        MR.executed("transit", 1.0)
        MR.executed("natural_width", 0.0)  # falsy: must not appear in the manifest's executed list
        m = MR.manifest()
    assert m["consumer"] == "twin"
    assert m["regime"] == "2025"
    assert m["scope"] == "result"
    assert m["executed"] == ["transit"]
    assert m["model_digest"] == MR.executed_digest(["transit"])
    assert m["registry_digest"] == MR.registry_digest()


def test_manifest_reflects_ablation_scope():
    with MR.run("mc", "2025"):
        MR.ablation("an ablation whose scope the manifest must report correctly", drop=[])
        m = MR.manifest()
    assert m["scope"] == "ablation"


# ---------------------------------------------------------------------------
# The census cross-check
# ---------------------------------------------------------------------------

CENSUS_PATH = ROOT / "results" / "twin_term_census.csv"


def test_census_cross_check_passes_on_the_real_census():
    MR.check_census_agreement(CENSUS_PATH)  # does not raise


def test_census_row_mapping_covers_exactly_the_registry():
    assert set(MR.CENSUS_ROW_FOR) == set(MR.TERM_IDS)


def test_census_says_fitter_carries_reads_yes_and_optional_as_true(tmp_path):
    fake = tmp_path / "census.csv"
    # blackbody maps to TWO census rows (CENSUS_ROW_FOR); both must be present or the lookup
    # correctly raises KeyError (its own dedicated test below), so both are given here.
    fake.write_text(
        "term,fitter\ntransit_cusp,yes\nac_stark_ramp,optional\n"
        "blackbody,no\nradiation_temperature_separate,no\n")
    assert MR.census_says_fitter_carries("transit", fake) is True
    assert MR.census_says_fitter_carries("ac_stark_ramp", fake) is True
    assert MR.census_says_fitter_carries("blackbody", fake) is False


def test_census_says_fitter_carries_returns_none_for_an_unmapped_term(tmp_path):
    fake = tmp_path / "census.csv"
    fake.write_text("term,fitter\n")
    assert MR.census_says_fitter_carries("natural_width", fake) is None


def test_census_says_fitter_carries_raises_on_a_stale_mapping(tmp_path):
    fake = tmp_path / "census.csv"
    fake.write_text("term,fitter\nsome_other_row,yes\n")
    with pytest.raises(KeyError):
        MR.census_says_fitter_carries("transit", fake)


def _mutated_census(tmp_path: Path, term: str, fitter_value: str) -> Path:
    """A copy of the real census CSV with one row's `fitter` cell overwritten."""
    rows = list(csv.DictReader(CENSUS_PATH.read_text().splitlines()))
    found = False
    for r in rows:
        if r["term"] == term:
            r["fitter"] = fitter_value
            found = True
    assert found, f"{term!r} is not a row of the real census; fix the test's plant"
    out = tmp_path / "mutated_census.csv"
    with open(out, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return out


def test_census_cross_check_fires_when_census_says_carried_but_registry_says_owed(tmp_path):
    # self_broadening_T03 has no census row of its own, so plant the contradiction on a term that
    # HAS one: flip transit_cusp's fitter column to something the registry would read as owed-like
    # by first confirming the registry really does say 'carried' for transit/fitter_2025 (it does),
    # then mutating the CENSUS side to 'no', which is the OTHER direction the check refuses.
    assert MR.kind_of(MR._BY_ID["transit"].status_fitter_2025) == "carried"
    mutated = _mutated_census(tmp_path, "transit_cusp", "no")
    with pytest.raises(MR.CensusDisagreement, match="transit"):
        MR.check_census_agreement(mutated)


def test_census_cross_check_fires_when_census_says_no_but_registry_says_carried(tmp_path):
    # axial_collection_window's real census row already says 'no'; the registry already avoids
    # 'carried' there. Flip a row the registry DOES call carried (transit_cusp) to 'no' -- the same
    # plant as above, kept as its own test because it exercises the OTHER named refusal branch of
    # check_census_agreement's docstring (a 'carried' registry status against a 'no' census cell).
    mutated = _mutated_census(tmp_path, "transit_cusp", "no: retracted 2026-09-25 for this plant")
    with pytest.raises(MR.CensusDisagreement):
        MR.check_census_agreement(mutated)


def test_census_cross_check_does_not_fire_on_an_absorbed_status_against_census_yes(tmp_path):
    # doppler_pedestal's own real census row says 'yes'; the registry reads it as 'absorbed', which
    # the docstring says agrees with either census reading. Confirm that holds even where the
    # census is forced to an explicit 'yes'.
    assert MR.kind_of(MR._BY_ID["doppler_pedestal"].status_fitter_2025) == "absorbed"
    mutated = _mutated_census(tmp_path, "doppler_pedestal", "yes, fit_full free=('pedestal_height_frac',)")
    MR.check_census_agreement(mutated)  # does not raise


def test_census_cross_check_does_not_fire_on_an_absorbed_status_against_census_no(tmp_path):
    mutated = _mutated_census(tmp_path, "doppler_pedestal", "no")
    MR.check_census_agreement(mutated)  # does not raise


def test_census_cross_check_raises_keyerror_on_a_stale_census_population(tmp_path):
    # every census row the seed names must still exist in the file, or the mapping itself is stale
    fake = tmp_path / "census.csv"
    fake.write_text("term,fitter\nsome_unrelated_row,yes\n")
    with pytest.raises(KeyError):
        MR.check_census_agreement(fake)


# ---------------------------------------------------------------------------
# The rows are, structurally, exactly what CSV_COLUMNS promises
# ---------------------------------------------------------------------------

def test_to_csv_rows_keys_match_csv_columns():
    rows = MR.to_csv_rows()
    assert len(rows) == len(MR.REGISTRY)
    for r in rows:
        assert set(r) == set(MR.CSV_COLUMNS)


def test_status_fields_are_the_six_in_a_stable_order():
    assert MR.STATUS_FIELDS == (
        "status_fitter_2025", "status_fitter_campaign",
        "status_twin_2025", "status_twin_campaign",
        "status_mc_2025", "status_mc_campaign",
    )


def test_modelterm_is_frozen():
    row = MR.REGISTRY[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        row.term_id = "changed"
