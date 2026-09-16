"""GUARD noise-ladder: the real traces are reachable only after the synthetic ladder has passed.

Owner, 2026-09-15: "Make sure to make a mechanism for which every analysis is at first performed
in synthetic traces without noise, then with ones with low noise level, then in ones with archive
noise level, and only as last step in the real traces after all this validation."

A rule saying that is a rule that gets skipped the first time a real trace is one line away, so it
is a refusal instead. An analysis declares an id; its three rungs write artefacts; `real_traces`
raises until all three exist, are newer than the analysis's own file, and read PASS.

    from rb5s6s import ladder_gate
    ladder_gate.record("moment_mle", "noiseless", passed=True, detail={...})   # rung by rung
    rows = ladder_gate.real_traces("moment_mle", __file__)                     # raises unless 3/3

The rungs, and what each has to show before it writes PASS:

  noiseless  the estimator recovers the injected truth with no noise at all. A failure here is
             an arithmetic or a convention error and nothing further is worth running.
  low        at 0.3 times the archive's own noise law, the truth is recovered with coverage
             inside [nominal - 0.10, nominal + 0.10] in BOTH directions; over-coverage is an
             inflated bar and is as much a failure as under-coverage.
  archive    the same at 1.0 times the law, per condition, with the twin's bias subtracted and
             its spread validated against the five repeats.

`analysis_id` is a name, not a path, so two harnesses sharing an estimator share one ladder.
"""
from __future__ import annotations

import json
import pathlib
import time
from typing import Any, Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
RUNGS = ("noiseless", "low", "archive")
NOISE_SCALE = {"noiseless": 0.0, "low": 0.3, "archive": 1.0}


# ---------------------------------------------------------------------------------------------
# The verdict is COMPUTED from the evidence and is NEVER passed in.  Until 2026-09-15 `record`
# took `passed: bool` from the caller, so this gate refused a MISSING rung and could not refuse a
# FALSE one: any harness could write PASS with an empty detail.  The repair removes the parameter
# outright, so a caller that still tries to hand a verdict in fails with a TypeError rather than
# being quietly believed.  `_judge` below is the only thing that can write PASS.
# ---------------------------------------------------------------------------------------------

NOISELESS_TOL = 1e-3          # a noiseless recovery is arithmetic: it closes or it does not
COVER_TOL = 0.10              # two-sided: over-coverage is an inflated bar, as bad as under
CHI2_BAND = (0.8, 1.3)        # the gage's own band


def _need(detail, key, reasons):
    if key not in detail:
        reasons.append(f"the detail carries no {key!r}, which this rung is judged on")
        return None
    return detail[key]


def _judge(rung: str, detail: Dict[str, Any]) -> tuple:
    """(verdict, reasons).  PASS only when the evidence for THIS rung is present and inside band."""
    reasons: List[str] = []
    if rung == "noiseless":
        e = _need(detail, "max_abs_rel_error", reasons)
        if e is not None and float(e) > NOISELESS_TOL:
            reasons.append(f"noiseless recovery is off by {float(e):.3g}, over {NOISELESS_TOL:g}: "
                           "a noiseless failure is an arithmetic or convention error")
        n = _need(detail, "n_truths", reasons)
        if n is not None and int(n) < 1:
            reasons.append("no injected truth was tested")
    else:
        nominal = float(detail.get("nominal", 0.68))
        c = _need(detail, "coverage", reasons)
        if c is not None and not (nominal - COVER_TOL <= float(c) <= nominal + COVER_TOL):
            reasons.append(
                f"coverage {float(c):.3f} is outside [{nominal - COVER_TOL:.2f}, {nominal + COVER_TOL:.2f}] "
                "(TWO-SIDED: over-coverage is an inflated bar and fails as hard as under-coverage)")
        x = _need(detail, "chi2_red", reasons)
        if x is not None and not (CHI2_BAND[0] <= float(x) <= CHI2_BAND[1]):
            reasons.append(f"chi2_red {float(x):.3f} is outside {CHI2_BAND}")
        o = _need(detail, "odd_sign_agreement", reasons)
        if o is not None and not bool(o):
            reasons.append("the odd orders disagree in sign with the twin's prediction")
        b = _need(detail, "blame", reasons)
        if b is not None and not str(b).strip():
            reasons.append("the blame verdict is empty: say what the twin reproduces and what it does not")
        if rung == "archive":
            for k in ("bias_subtracted", "spread_validated"):
                v = _need(detail, k, reasons)
                if v is not None and not bool(v):
                    reasons.append(f"{k} is false: the archive rung needs the twin's bias removed "
                                   "and its spread checked against the repeats")
    return ("PASS" if not reasons else "FAIL"), reasons


def _predecessor(rung: str):
    i = RUNGS.index(rung)
    return RUNGS[i - 1] if i else None


class LadderRefused(RuntimeError):
    """Raised when real traces are asked for before the synthetic ladder has passed."""


def _cache() -> pathlib.Path:
    """The session's current cache, from the pointer the instruments share."""
    p = ROOT / "private" / "cache" / "CURRENT_CACHE"
    if p.is_file():
        lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
        if lines:
            return (ROOT / lines[0]).resolve()
    return ROOT / "private" / "cache"


def ladder_dir(analysis_id: str, cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    return (cache or _cache()) / ".ladder" / analysis_id


def record(analysis_id: str, rung: str, *, detail: Dict[str, Any],
           cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    """Write one rung's artefact, with the verdict COMPUTED from `detail`.

    There is deliberately no `passed` argument: a caller that tries to hand a verdict in gets a
    TypeError.  A rung whose PREDECESSOR is absent or not PASS is refused outright, so the ladder
    cannot be climbed out of order.
    """
    if rung not in RUNGS:
        raise ValueError(f"rung must be one of {RUNGS}, got {rung!r}")
    prev = _predecessor(rung)
    if prev is not None:
        f = ladder_dir(analysis_id, cache) / f"{prev}.json"
        if not f.is_file():
            raise LadderRefused(f"cannot record '{rung}' for '{analysis_id}': its predecessor "
                                f"'{prev}' has no artefact. The ladder is climbed in order.")
        if json.loads(f.read_text()).get("verdict") != "PASS":
            raise LadderRefused(f"cannot record '{rung}' for '{analysis_id}': its predecessor "
                                f"'{prev}' does not read PASS.")
    verdict, reasons = _judge(rung, detail)
    d = ladder_dir(analysis_id, cache)
    d.mkdir(parents=True, exist_ok=True)
    out = d / f"{rung}.json"
    out.write_text(json.dumps({
        "analysis_id": analysis_id, "rung": rung, "noise_scale": NOISE_SCALE[rung],
        "verdict": verdict, "reasons": reasons,
        "when": time.strftime("%Y-%m-%dT%H:%M:%S"), "detail": detail,
    }, indent=1))
    return out


def status(analysis_id: str, harness: Optional[str] = None,
           cache: Optional[pathlib.Path] = None) -> List[str]:
    """Empty when every rung admits; otherwise one line per rung that does not."""
    d = ladder_dir(analysis_id, cache)
    h_mtime = pathlib.Path(harness).resolve().stat().st_mtime if harness else None
    bad = []
    for rung in RUNGS:
        f = d / f"{rung}.json"
        if not f.is_file():
            bad.append(f"the {rung} rung has no artefact ({f}): run it before the real traces")
            continue
        try:
            row = json.loads(f.read_text())
        except ValueError as e:
            bad.append(f"the {rung} rung's artefact is unreadable: {e}")
            continue
        if row.get("verdict") != "PASS":
            bad.append(f"the {rung} rung reads {row.get('verdict')}: " + json.dumps(row.get("detail", {}))[:200])
        elif h_mtime is not None and f.stat().st_mtime < h_mtime:
            bad.append(f"the {rung} rung is OLDER than the analysis that would use it: re-run it")
    return bad


def real_traces(analysis_id: str, harness: Optional[str] = None, *,
                rows: Optional[List[Dict[str, str]]] = None,
                cache: Optional[pathlib.Path] = None, with_info: bool = False):
    """The archive's own traces, refused until the ladder passes. Returns (row, freqs, volts) triples."""
    bad = status(analysis_id, harness, cache)
    if bad:
        raise LadderRefused(
            f"real traces refused for '{analysis_id}': " + "; ".join(bad)
            + ". The synthetic ladder comes first: noiseless, then 0.3 of the archive's law, then 1.0.")
    from . import ingest
    manifest = rows if rows is not None else ingest.load_manifest()
    out = []
    for r in manifest:
        loaded = ingest.load_trace(ingest.trace_path(r), with_info=with_info)
        out.append((r, loaded))
    return out


def _self_test() -> List[str]:
    """GUARD noise-ladder, planted BOTH ways on every refusal it owns.

    The 2026-09-15 repair is what most of this plants: before it, `record` took the verdict from
    the caller, so the gate could refuse a MISSING rung and never a FALSE one.  Each case below
    names the defect it would catch.
    """
    import tempfile
    OK_N = {"max_abs_rel_error": 1e-6, "n_truths": 8}
    OK_C = {"coverage": 0.68, "chi2_red": 1.02, "odd_sign_agreement": True,
            "blame": "twin reproduces k2 and k4; k3 open"}
    OK_A = dict(OK_C, bias_subtracted=True, spread_validated=True)
    bad = []
    with tempfile.TemporaryDirectory() as td:
        cache = pathlib.Path(td)
        harness = cache / "h.py"
        harness.write_text("# plant\n")

        # 1. nothing recorded at all -> refused, and real_traces raises
        if not status("plant", str(harness), cache):
            bad.append("noise-ladder: an analysis with no rungs was admitted")
        try:
            real_traces("plant", str(harness), cache=cache)
            bad.append("noise-ladder: real_traces returned without any ladder")
        except LadderRefused:
            pass

        # 2. THE REPAIR: a verdict cannot be handed in any more
        try:
            record("plant", "noiseless", passed=True, detail={}, cache=cache)  # type: ignore[call-arg]
            bad.append("noise-ladder: `passed=` was accepted -- the rubber stamp is back")
        except TypeError:
            pass

        # 3. THE REPAIR: an EMPTY detail is judged FAIL, not PASS
        r = json.loads(record("plant", "noiseless", detail={}, cache=cache).read_text())
        if r["verdict"] != "FAIL" or not r["reasons"]:
            bad.append("noise-ladder: an empty detail was not judged FAIL with reasons")

        # 4. the ladder cannot be climbed out of order
        try:
            record("plant", "archive", detail=OK_A, cache=cache)
            bad.append("noise-ladder: 'archive' was recorded while 'noiseless' reads FAIL")
        except LadderRefused:
            pass

        # 5. good evidence passes, rung by rung
        for rung, det in (("noiseless", OK_N), ("low", OK_C), ("archive", OK_A)):
            r = json.loads(record("plant", rung, detail=det, cache=cache).read_text())
            if r["verdict"] != "PASS":
                bad.append(f"noise-ladder: sound evidence for {rung} was refused: {r['reasons']}")
        if status("plant", str(harness), cache):
            bad.append("noise-ladder: three passing rungs were still refused")

        # 6. TWO-SIDED coverage: probe just outside the catch region in EACH direction
        for cov, side in ((0.55, "under"), (0.81, "over")):
            r = json.loads(record("plant", "low", detail=dict(OK_C, coverage=cov),
                                  cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: {side}-coverage {cov} was admitted; "
                           "over-coverage is an inflated bar and must fail as hard as under")
        # and just INSIDE, both directions, so the band is not simply always-refusing
        for cov in (0.59, 0.77):
            r = json.loads(record("plant", "low", detail=dict(OK_C, coverage=cov),
                                  cache=cache).read_text())
            if r["verdict"] != "PASS":
                bad.append(f"noise-ladder: in-band coverage {cov} was refused")

        # 7. each remaining judged field, planted once
        for det, what in ((dict(OK_C, chi2_red=4.0), "chi2 4.0"),
                          (dict(OK_C, odd_sign_agreement=False), "odd-sign disagreement"),
                          (dict(OK_C, blame="  "), "an empty blame verdict")):
            r = json.loads(record("plant", "low", detail=det, cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: {what} was admitted")
        record("plant", "low", detail=OK_C, cache=cache)
        for det, what in ((dict(OK_A, bias_subtracted=False), "an unsubtracted twin bias"),
                          (dict(OK_A, spread_validated=False), "an unvalidated spread")):
            r = json.loads(record("plant", "archive", detail=det, cache=cache).read_text())
            if r["verdict"] != "FAIL":
                bad.append(f"noise-ladder: {what} was admitted at the archive rung")
        record("plant", "archive", detail=OK_A, cache=cache)

        # 8. a harness edited after its ladder no longer has it
        time.sleep(0.01)
        harness.write_text("# plant, edited after the ladder\n")
        if not status("plant", str(harness), cache):
            bad.append("noise-ladder: a harness edited after its ladder kept it")
    return bad


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        b = _self_test()
        for x in b:
            print(x)
        print(f"ladder_gate: self-test {'OK' if not b else 'FAILED'}")
        sys.exit(1 if b else 0)
    print(__doc__)
