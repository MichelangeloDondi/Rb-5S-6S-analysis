"""The governance instruments' own plants run, here, in the suite.

WHY THIS TEST EXISTS. `private/checks/instrument_msa.py` measures how many
governance instruments carry a re-runnable validation and runs each one it
finds. Nothing ran IT, and a harness nothing runs is exactly the class it was
written to measure: a plant that has stopped discriminating without saying so.
Wiring it here puts every plant in the suite, so a broken refusal fails the
gate rather than waiting for someone to think of checking.

The archive-only skip is deliberate: `private/` is absent from the public
mirror, and its absence there is correct rather than a failure.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MSA = ROOT / "private" / "checks" / "instrument_msa.py"


@pytest.mark.skipif(not MSA.is_file(),
                    reason="private/ is absent, as it is in the mirror")
def test_every_governance_plant_still_discriminates():
    """Run instrument_msa, which runs every plant it can find.

    A non-zero exit means one of the planted refusals no longer fires. That is
    worse than an unplanted instrument, because the coverage number counts it
    as validated while it validates nothing.
    """
    proc = subprocess.run([sys.executable, str(MSA)],
                          capture_output=True, text=True, timeout=600)
    assert proc.returncode == 0, (
        "a governance plant failed, so a refusal it covers has stopped "
        "firing:\n" + proc.stdout[-3000:] + proc.stderr[-2000:])


@pytest.mark.skipif(not MSA.is_file(), reason="private/ is absent")
def test_the_coverage_reading_is_present_and_honest():
    """The harness must report a fraction, not fall silent.

    Its own failure once printed as a value rather than as NOT MEASURED, which
    is the self-report class the whole exercise is about.
    """
    proc = subprocess.run([sys.executable, str(MSA)],
                          capture_output=True, text=True, timeout=600)
    line = next((ln for ln in proc.stdout.splitlines()
                 if "governance instruments carry" in ln), "")
    assert line, "instrument_msa printed no coverage reading at all"
    assert "per cent)" in line, f"the reading lost its fraction: {line!r}"


PARALLEL = ROOT / "private" / "checks" / "parallel_budget.py"


@pytest.mark.skipif(not PARALLEL.is_file(), reason="private/ is absent")
def test_the_parallel_budget_refuses_to_oversubscribe_this_machine():
    """The worker count beside a gate is measured, and its own plant runs here.

    WHY IT EXISTS (owner, 2026-09-11). The rule that a gate and a computation
    belong on opposite halves of this machine was in the rule file and was not
    followed, because the number it turns on, how many workers fit beside
    whatever is running, was left to be recalled. A rule whose quantity is
    recalled is a rule that gets skipped when the recall is inconvenient.

    FAILURE MODE IF THIS TEST IS DELETED: the budget stops subtracting the
    gate's own footprint, a pool is sized as though the machine were idle, and
    this part goes into swap, which is A186: the gate took 0.4 seconds of CPU
    in six minutes and the producer's progress line stood still for 1500
    seconds, and the obvious story was the wrong one.
    """
    proc = subprocess.run([sys.executable, str(PARALLEL), "--self-test"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (
        "the parallel budget's own plant failed:\n" + proc.stdout + proc.stderr)

    sys.path.insert(0, str(PARALLEL.parent))
    try:
        import parallel_budget as pb
    finally:
        sys.path.pop(0)

    # THE ASSERTIONS ARE INVARIANTS, NOT A LIVE COUNT. The first cut of this
    # test asserted the beside-a-gate budget equals the performance core count,
    # and the gate failed it within the hour: that equality holds only while
    # free memory is ample, and this test runs with a gate on the machine by
    # construction. An expectation that depends on the host's live memory is
    # the class E27 names.
    #
    # A pool is never empty and never exceeds the half of the machine it is on.
    assert pb.workers(job_gib=0.001, beside_gate=True) >= 1
    assert pb.workers(job_gib=0.001, beside_gate=True) <= pb.PERF_CORES
    # A gate never increases the budget.
    assert (pb.workers(job_gib=2.0, beside_gate=True)
            <= pb.workers(job_gib=2.0, beside_gate=False))
    # A heavier job never gets more workers, and memory binds for a huge one.
    assert (pb.workers(job_gib=8.0, beside_gate=False)
            <= pb.workers(job_gib=0.001, beside_gate=False))
    assert pb.workers(job_gib=1000.0, beside_gate=False) == 1

# THE TWO 2026-09-13 INSTRUMENTS RUN THEIR OWN PLANTS HERE. Both shipped with a
# self-test and neither was in the suite, which is the "asserted instrument"
# row of the enforcement report: the plant ran only when a human ran it. A242
# and A243 are what they guard, and both of those were found by hand precisely
# because nothing ran the guard.
UNBACKED = ROOT / "private" / "checks" / "check_unbacked.py"
REMOTE_LAG = ROOT / "private" / "checks" / "check_remote_lag.py"


def _lone_stamp_sites(text: str) -> list[int]:
    """Line numbers that DECIDE on .targeted_ok without .prefloor_ok within two
    lines (a marked floor-only site is exempt). One predicate for the guard and
    its plant (the protocols seat, 2026-09-14: the plant had its own copy and
    it had already drifted)."""
    out = []
    ls = text.splitlines()
    for k, line in enumerate(ls):
        if ".targeted_ok" not in line or ".prefloor_ok" in line or "stamp-site: floor-only" in line:
            continue
        if not any(w in line for w in ("grep -q", "grep -c", "[ -f", "test -f", "read_text", "exists(", "open(", "stamp_matches", "_stamp_tree")):
            continue
        if ".prefloor_ok" not in "\n".join(ls[max(0, k - 2):k + 3]):
            out.append(k + 1)
    return out


@pytest.mark.skipif(not UNBACKED.is_file(),
                    reason="private/ is absent, as it is in the mirror")
def test_the_unbacked_sweep_plant_still_discriminates():
    """`check_unbacked.py --self-test`: the classifier and both verified claims.

    It covers every class on a representative path, and the two
    TRACKED_ELSEWHERE claims through all their states, including the one that
    matters: a STALE backup of the rule file must not read as protection. That
    is A242, where the authority file for three repositories sat on one disk
    for four days while every `git status` read clean.

    FAILURE MODE IF THIS TEST IS DELETED: the sweep keeps reporting paths as
    protected on a claim it no longer checks, and the next file to leave a
    tracked path leaves quietly.
    """
    proc = subprocess.run([sys.executable, str(UNBACKED), "--self-test"],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, (
        "the unbacked sweep's own plant failed:\n" + proc.stdout + proc.stderr)


@pytest.mark.skipif(
    not REMOTE_LAG.is_file()
    or not (Path.home() / "Documents/GitHub/Rb-5S-6S-public/.git").exists(),
    reason="private/ or the mirror checkout is absent; the plant reads both remotes")
def test_the_remote_lag_plant_still_discriminates():
    """`check_remote_lag.py --self-test`: four faults and four legal states.

    The subtle case is DIVERGED on CONTENT rather than on names: two published
    trees can carry identical path lists and different bytes, which a name-only
    comparison cannot see, so the plant substitutes blob shas. The tolerances
    matter as much: exactly one commit behind WITH its backup ref is the
    POLICY, and a mirror level with its main is the normal mid-wave state, so
    refusing either would be a mechanism refusing forever on a correct tree.

    FAILURE MODE IF THIS TEST IS DELETED: the lag check stops discriminating
    and the first thing it fails to catch is a remote whose main has reached
    its tip, after which an amend rewrites pushed history.
    """
    proc = subprocess.run([sys.executable, str(REMOTE_LAG), "--self-test"],
                          capture_output=True, text=True, timeout=180)
    assert proc.returncode == 0, (
        "the remote-lag plant failed:\n" + proc.stdout + proc.stderr)

VERIFY_PRUNE = ROOT / "private" / "checks" / "verify_prune.py"


@pytest.mark.skipif(not VERIFY_PRUNE.is_file(),
                    reason="private/ is absent, as it is in the mirror")
def test_the_prune_verifier_plant_still_discriminates():
    """`verify_prune.py --self-test`: five ways a bulk edit drops content.

    The repository's rule file requires a bulk edit to be checked against the
    PRE-EDIT artefact rather than against its own report, and had no instrument
    for it. The rule was earned when a migration moved 45 blocks, reported every
    one landed truthfully, and had still deleted five numbered policy steps: the
    capture ended at a blank line and a numbered list has none between its items.

    The plant covers that case and four others, including the two this file's
    own prune hit -- a debt moved out of the file whose instrument reads it by
    name, and a debt hoisted without the prose that makes it readable.

    FAILURE MODE IF THIS TEST IS DELETED: the next bulk edit is graded by its
    own accounting, which cannot see what it captured too widely.
    """
    proc = subprocess.run([sys.executable, str(VERIFY_PRUNE), "--self-test"],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, (
        "the prune verifier's own plant failed:\n" + proc.stdout + proc.stderr)


def test_every_reader_of_the_floor_stamp_also_reads_the_fast_stamp():
    """One rule, three files, and it was wired into two of them.

    The fast stamp was taught to the landing script and to the ledger and not
    to `ci_gate.sh`, so the gate refused to start beside a reading stage that
    had already opened: the parallel arrangement failed silently because a
    third copy of one rule was missed. That happened three times in one day
    with three different rules, so the class gets a guard rather than a third
    careful edit.

    ANY file that consults `.targeted_ok` must also consult `.prefloor_ok`.
    Both name the index tree they graded and both answer the same question,
    which is whether SOME guard ran on this exact tree.

    FAILURE MODE IF THIS TEST IS DELETED: a fourth reader is added, accepts
    only the slow stamp, and the thing it guards quietly stops happening in
    the arrangement that was supposed to make it cheap.
    """
    # NAMING THE STAMP IS NOT GATING ON IT. These write it, classify it or list
    # it, and a file that does not decide anything from it cannot fail to decide
    # the same from the other. Each entry carries why, so adding one is a
    # deliberate act rather than a way to quiet the guard.
    NOT_GATES = {
        "scripts/targeted.sh": "writes the stamp; it is the producer",
        "private/checks/enforcement_report.py": "names it in an instrument list",
        "private/checks/plant_begin_record.py": "writes a stamp into its own fixture",
        "private/checks/plant_targeted_moved_values.py": "writes and reads its own fixture",
        "tests/test_gate_verdict_sentinel.py": "names it in docstrings describing the gate's own refusals",
    }
    # THE POPULATION INCLUDES THE ONE OPERATIONAL SCRIPT THAT READS STAMPS (the
    # protocols seat, 2026-09-13): landing.sh lives under private/cache and was
    # invisible to a guard scanning three hand-picked directories.
    roots = [ROOT / "scripts", ROOT / "private" / "checks", ROOT / "tests",
             ROOT / "private" / "cache" / "ultra_joint_2026-09-12"]
    offenders = []
    for base in roots:
        if not base.is_dir():
            continue
        for f in sorted(base.rglob("*")):
            if f.suffix not in (".sh", ".py") or not f.is_file():
                continue
            if f.name in ("test_governance_instruments.py",):
                continue
            txt = f.read_text(errors="ignore")
            rel = str(f.relative_to(ROOT))
            if rel in NOT_GATES or ".targeted_ok" not in txt:
                continue
            # PER SITE, NOT PER FILE (2026-09-14): a file that reads both stamps
            # somewhere would pass a new lone reader of the slow stamp added
            # anywhere in it. A line that DECIDES on .targeted_ok (grep -q, test,
            # if, read_text, exists, open) must read .prefloor_ok within two
            # lines of it; a line that merely names the stamp is not a site.
            offenders.extend(f"{rel}:{k}" for k in _lone_stamp_sites(txt))
    assert not offenders, (
        "these read the floor stamp and not the fast stamp, so a tree graded by "
        "scripts/prefloor.sh reads as ungraded to them:\n  " + "\n  ".join(offenders)
        + "\nTeach each one both, or the parallel arrangement fails silently here.")


ORDERS = ROOT / "private" / "checks" / "check_orders.py"
IDLE = ROOT / "private" / "checks" / "idle_audit.py"


@pytest.mark.skipif(not ORDERS.is_file(),
                    reason="private/ is absent, as it is in the mirror")
def test_the_order_ledger_plant_still_discriminates():
    """`check_orders.py --self-test`: a stale open order refuses, a deferred
    one with a reason passes, a landed one passes, a fresh one passes.

    FAILURE MODE IF THIS TEST IS DELETED: an order given in words can
    sit open for any number of commits with nothing reading it, which is how
    the ultra-joint fit of 2026-09-12 went unseen for five.
    """
    r = subprocess.run([sys.executable, str(ORDERS), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.skipif(not IDLE.is_file(),
                    reason="private/ is absent, as it is in the mirror")
def test_the_idle_audit_plant_still_discriminates():
    """`idle_audit.py --self-test`: the gate counter, the stamp reader and the
    under-gate edit detector, each in both directions.

    FAILURE MODE IF THIS TEST IS DELETED: the audit that `landing.sh commit`
    reads could pass on readers that no longer read, and a commit would land
    with a gate count, a stamp or an edit-under-gate it never measured.
    """
    r = subprocess.run([sys.executable, str(IDLE), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr

def test_the_stamp_guard_sees_a_lone_reader_added_to_a_compliant_file(tmp_path):
    """The per-site predicate on a file that already reads both stamps
    elsewhere: a new site gating on the slow stamp alone is flagged; the same
    site reading both is not.

    FAILURE MODE IF THIS TEST IS DELETED: the guard passes any file that
    mentions the fast stamp once, and a lone reader added to landing.sh, the
    exact shape of three regressions in one day, is invisible to it.
    """
    lines = ["x=1", 'grep -q "$TREE" .prefloor_ok || grep -q "$TREE" .targeted_ok', "y=2", "z=3", "w=4"]
    lone = lines + ['if grep -q "$TREE" .targeted_ok; then echo admitted; fi']
    both = lines + ['if grep -q "$TREE" .targeted_ok || grep -q "$TREE" .prefloor_ok; then echo admitted; fi']
    offenders = _lone_stamp_sites
    assert offenders("\n".join(lone)) == [6]
    assert offenders("\n".join(both)) == []
