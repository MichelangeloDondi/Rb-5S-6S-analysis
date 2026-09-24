"""GUARD kernel-mc: a node of the full model is used only after its Monte Carlo agrees with it.

Owner, 2026-09-16: "make sure (with proper mechanisms, as always, to refuse to proceed in case
it's not correct what would be done!) that for each w_0 and M^2 (and in case also rho and other
parameters) you run the proper Monte Carlo simulation before using it in the full model."

A NODE is the geometry and the conditions `fullmodel.full_profile` is evaluated on: the waist,
the beam quality, the retro ratio, the temperature, the power. For each node an ARTEFACT under
`<current cache>/.kernel_mc/<key>.json` holds the Monte Carlo's readings against the closed forms
the model uses, each with its tolerance, and a verdict COMPUTED from them (`record_node` takes no
verdict). `require_node` raises `KernelUnvalidated` on a node with no artefact, a FAIL, or an
artefact whose recorded digest of the model's own file differs from the file's, which is how a
model edit re-opens every node (a digest and not a modification time, so the artefacts can be
tracked fixtures on a hosted runner, where every checkout time is "now").

FALSE-PASS DIRECTION: green means the Monte Carlo and the closed form agree on the READINGS the
artefact carries, not that both are the atom; a term absent from both stays invisible here, which
is why the readings include the depletion-widened kernel and the four lines' shares and not only
the transit's width.

    python rb5s6s/kernel_gate.py --self-test
    python rb5s6s/kernel_gate.py --status <analysis-cache>
"""
from __future__ import annotations
import json
import os
import pathlib
import sys
import time
from typing import Any, Dict, Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
MODEL_FILE = ROOT / "rb5s6s" / "fullmodel.py"
#: The Monte Carlo producer, whose own package imports are part of what a node's readings computed.
MC_PRODUCER = ROOT / "scripts" / "run_kernel_mc.py"
#: The judge is not the model: an edit to the gate re-judges every artefact at `status_node` time and
#: must not re-open the Monte Carlo besides.
_NOT_THE_MODEL = frozenset({"kernel_gate"})


_POPULATION_CACHE: dict = {}
_DIGEST_CACHE: dict = {}


def _stamp(files) -> tuple:
    """(path, mtime_ns, size) per file: the key under which a parse is reused."""
    out = []
    for f in files:
        try:
            st = f.stat()
            out.append((str(f), st.st_mtime_ns, st.st_size))
        except OSError:
            out.append((str(f), None, None))
    return tuple(out)


def model_population() -> tuple:
    """Every package module whose CODE a node's readings depend on, DERIVED from the imports.

    THE DEFECT THIS REPAIRS (F95, 2026-09-17). The digest read `fullmodel.py` alone, while the ramp,
    the kernels, the amplitude shares and the cascade that a node's readings compare live in
    `lineshape`, `amplitudes`, `cascade` and `platforms`. Owner order O27 named the widening as its
    deliverable; it did not land, so when `lineshape.stark_ramp` changed sides the gate could not see
    it and a node validated against the red ramp read as valid against the blue one. The population
    is the transitive closure of package imports from `fullmodel.py` and the Monte Carlo producer,
    never a typed list, so a module either starts importing joins the digest without an edit here.
    """
    import ast
    pkg = ROOT / "rb5s6s"

    def imports_of(path: pathlib.Path) -> set:
        out: set = set()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            return out
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom):
                if n.level == 1:
                    out |= {n.module.split(".")[0]} if n.module else {a.name for a in n.names}
                elif n.module and n.module.split(".")[0] == "rb5s6s":
                    parts = n.module.split(".")
                    out |= {parts[1]} if len(parts) > 1 else {a.name for a in n.names}
            elif isinstance(n, ast.Import):
                out |= {a.name.split(".")[1] for a in n.names if a.name.startswith("rb5s6s.")}
        return {m for m in out if (pkg / f"{m}.py").is_file()}

    # THE CLOSURE IS CACHED ON THE PACKAGE'S OWN STAMPS (F97, 2026-09-17): recomputed on every
    # `status_node`, it parsed nineteen modules per node and a 744-node status sweep ran past two
    # minutes; the closure calls the gate thousands of times per cell. A file whose stamp moved
    # re-derives it, so an edit is still seen.
    key = _stamp(sorted(pkg.glob("*.py")) + [MC_PRODUCER])
    if key in _POPULATION_CACHE:
        return _POPULATION_CACHE[key]
    seen: set = set()
    todo = ["fullmodel"] + sorted(imports_of(MC_PRODUCER))
    while todo:
        m = todo.pop()
        if m in seen or m in _NOT_THE_MODEL:
            continue
        seen.add(m)
        todo += sorted(imports_of(pkg / f"{m}.py") - seen)
    out = tuple(pkg / f"{m}.py" for m in sorted(seen))
    _POPULATION_CACHE.clear(); _POPULATION_CACHE[key] = out
    return out

#: the readings every artefact carries, and the tolerance each is judged on (relative unless
#: the name says absolute). A reading absent from an artefact is a refusal, never a pass.
READINGS = {
    "transit_fwhm_rel": 0.01,          # the Monte Carlo kernel's FWHM against transit_fwhm_from_w0
    "transit_shape_rel": 0.02,         # the kernel's cusp shape: the ratio of its 10 and 50 per cent widths
    "ramp_k2_rel": 0.02,               # the light-shift distribution's second cumulant against the ramp's
    "ramp_k3_rel": 0.05,               # its third, the grid movement stated (a small difference of large numbers)
    "amplitude_power_law_abs": 0.02,   # the departure of the amplitude from P^2 at the node, absolute in the exponent
    "shares_abs": 0.01,                # the four lines' shares, absolute per line
    "depleted_line_abs": 2e-3,       # the composed depleted line against the fit's form, peak-normalised        # the surviving kernel's width with the F depletion along the chord
}


def node_key(w0_um: float, m2: float = 1.0, rho: float = 0.94, T_C: float = 130.0,
             P_mW: float = 225.0) -> str:
    """The node's name: the geometry and conditions rounded to what the model resolves."""
    return f"w{w0_um:.1f}_m{m2:.2f}_r{rho:.3f}_T{T_C:.0f}_P{P_mW:.0f}"


def _cache() -> pathlib.Path:
    p = ROOT / "private" / "cache" / "CURRENT_CACHE"
    if p.is_file():
        lines = [l.strip() for l in p.read_text().splitlines() if l.strip()]
        if lines:
            return (ROOT / lines[0]).resolve()
    return ROOT / "private" / "cache"


def _ast_without_docstrings(src: str) -> str:
    """The model's syntax tree as text, with every docstring removed (2026-09-17).

    WHY THE DIGEST IS NOT THE FILE'S BYTES. A node's validation is a statement about the code that
    computed it. Hashing the bytes made a corrected sentence in a docstring invalidate 736 validated
    nodes, so a prose repair waited on hours of Monte Carlo and the record carried the stale
    sentence meanwhile. Stripping the docstrings and hashing `ast.dump` keeps every behavioural
    change inside the digest (a changed constant, a reordered expression, a new argument, even a
    renamed local) and leaves prose outside it. A comment is already outside, since it never reaches
    the tree, and that asymmetry is the defect this removes.
    """
    import ast
    tree = ast.parse(src)

    def prose(stmt) -> bool:
        return isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) \
            and isinstance(stmt.value.value, str)

    # EVERY bare string statement, not only a body's first (F96, 2026-09-17): an attribute docstring
    # after an assignment in `constants.py` is prose with no runtime effect, and a corrected sentence
    # in one moved the digest and reopened every node. A string that is an argument, a default or an
    # assigned value is not a statement and stays inside the digest.
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list) and stmts and any(prose(s) for s in stmts):
                kept = [s for s in stmts if not prose(s)]
                setattr(node, field, kept or ([ast.Pass()] if field == "body" else []))
    return ast.dump(ast.fix_missing_locations(tree), annotate_fields=True, include_attributes=False)


def _code_payload(mf: pathlib.Path) -> bytes:
    try:
        return _ast_without_docstrings(mf.read_text(encoding="utf-8")).encode("utf-8")
    except (SyntaxError, UnicodeDecodeError):
        return mf.read_bytes()               # an unparsable module is hashed as bytes, never skipped


def model_digest(model_file: Optional[pathlib.Path] = None, files: Optional[tuple] = None) -> Optional[str]:
    """The first sixteen hex digits of the sha256 of the model's CODE: each module's syntax tree with
    the docstrings stripped (`_ast_without_docstrings`), not the files' bytes. With no argument the
    model is `model_population()`, every module the readings compute with; `model_file` hashes one
    file and `files` a given tuple, which is how the plants reach it. None when the root is absent."""
    import hashlib
    if model_file is not None:
        return hashlib.sha256(_code_payload(model_file)).hexdigest()[:16] if model_file.is_file() else None
    population = files if files is not None else model_population()
    if not population or not all(f.is_file() for f in population):
        return None
    key = _stamp(population)
    if key in _DIGEST_CACHE:
        return _DIGEST_CACHE[key]
    h = hashlib.sha256()
    for f in population:
        h.update(f.name.encode("utf-8") + b"\n" + _code_payload(f) + b"\n")
    out = h.hexdigest()[:16]
    if len(_DIGEST_CACHE) > 64:
        _DIGEST_CACHE.clear()
    _DIGEST_CACHE[key] = out
    return out


def mc_dir(cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    """The artefact directory: the cache given, else `RB5S6S_KERNEL_MC_DIR` (a directory of artefacts
    a test builds for itself, or one a hosted runner is handed), else `.kernel_mc/` under the
    session's current cache. No fixture set is tracked; the tests plant their own."""
    if cache is not None:
        return pathlib.Path(cache) / ".kernel_mc"
    env = os.environ.get("RB5S6S_KERNEL_MC_DIR")
    if env:
        return pathlib.Path(env)
    return _cache() / ".kernel_mc"


REQUIRED_DETAIL = ("node", "depletion_widening_rel", "depletion_fwhm_rel", "depletion_note")


class KernelUnvalidated(RuntimeError):
    """Raised when the full model is asked for a node no Monte Carlo has validated."""


#: THE WAIST ANALYSES' READING SET (D1 of PLAN v2, 2026-09-18). The closure and the joint MLE fit ONE
#: FREE AMPLITUDE PER TRACE (`Cell.linear`: amplitude, offset and slope by weighted least squares), so
#: they never consume the amplitude's local power law; requiring `amplitude_power_law_abs` of them
#: blocked the whole 40 to 46 um band on a reading no waist fit reads (F134: 21 of 39 band nodes pass
#: it after the saturated-cycles repair, the worst at 0.0502 against 0.02). Any analysis that TIES
#: amplitudes across powers (the amplitude channel, the shares against the density law) keeps the
#: default, which is every reading. A caller names the set; nothing here loosens a tolerance.
WAIST_READINGS = tuple(n for n in READINGS if n != "amplitude_power_law_abs")


def _names(readings_wanted) -> tuple:
    """The reading names a caller asks for: None is every reading; a subset must be known names."""
    if readings_wanted is None:
        return tuple(READINGS)
    names = tuple(readings_wanted)
    unknown = [n for n in names if n not in READINGS]
    if unknown:
        raise ValueError(f"unknown kernel-gate readings {unknown}; the readings are {list(READINGS)}")
    if not names:
        raise ValueError("an empty reading set gates nothing; name the readings or pass None for all")
    return names


def judge(readings: Dict[str, Any], names=None) -> tuple:
    """(verdict, reasons): every reading present and inside its tolerance, or FAIL naming each.

    `names` restricts the judgement to a subset of `READINGS` (D1: `WAIST_READINGS` for the waist
    analyses); the artefact's RECORDED verdict is always over every reading."""
    why = []
    for name, tol in READINGS.items():
        if name not in _names(names):
            continue
        if name not in readings:
            why.append(f"{name} absent"); continue
        r = readings[name]
        try:
            dev = abs(float(r["mc"] - r["model"])) / (abs(float(r["model"])) if name.endswith("_rel") else 1.0)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            why.append(f"{name} malformed"); continue
        if dev > tol:
            why.append(f"{name} off by {dev:.3g} against {tol}")
        if name == "ramp_k3_rel":
            gm = r.get("grid_movement")
            if gm is None:
                why.append("ramp_k3_rel carries no grid movement")
            elif not (float(gm) <= K3_GRID_TOL):
                why.append(f"ramp_k3_rel grid movement {float(gm):.3g} over {K3_GRID_TOL}")
    return ("PASS" if not why else "FAIL"), why


#: THE DIGEST PIN OF A POOLED RUN (2026-09-18, PLAN v2 C1). A pooled re-run of 976 nodes took 17 minutes,
#: and two package edits made under it moved the digest twice, so the artefacts came out in THREE
#: populations, the deepest nodes stale, and `--collect` refused the table. Nothing said so until the
#: end. A launcher that sets `RB5S6S_MODEL_DIGEST_PIN` to the digest at its start makes every later
#: `record_node` REFUSE when the model has moved, so an edit under a running pool fails the node it is
#: about to write instead of poisoning the population; the run's log names the moved digest and the
#: edit is the thing to undo or to wait out. Unset, nothing changes.
DIGEST_PIN_ENV = "RB5S6S_MODEL_DIGEST_PIN"


class ModelMovedUnderRun(RuntimeError):
    """The model's digest moved while a pinned pooled run was writing artefacts."""


def record_node(key: str, readings: Dict[str, Any], *, detail: Optional[Dict[str, Any]] = None,
                cache: Optional[pathlib.Path] = None) -> pathlib.Path:
    pin = os.environ.get(DIGEST_PIN_ENV)
    if pin:
        now = model_digest()
        if now != pin:
            raise ModelMovedUnderRun(
                f"node {key} not written: the model's digest is {now} and this run was pinned at {pin}; "
                f"a package edit landed under the running pool. Undo it or wait it out, then re-run the "
                f"nodes written since the edit.")
    verdict, why = judge(readings)
    d = mc_dir(cache); d.mkdir(parents=True, exist_ok=True)
    out = d / f"{key}.json"
    out.write_text(json.dumps({"key": key, "verdict": verdict, "reasons": why, "readings": readings,
                               "detail": detail or {}, "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
                               "model_sha": model_digest()},
                              indent=1))
    return out


def status_node(key: str, cache: Optional[pathlib.Path] = None,
                model_file: Optional[pathlib.Path] = None, readings=None) -> list:
    """Empty when the node is admitted; otherwise the reasons. `readings` names the subset of
    `READINGS` the caller consumes (None: all of them; `WAIST_READINGS` for a free-amplitude fit)."""
    f = mc_dir(cache) / f"{key}.json"
    if not f.is_file():
        return [f"no Monte Carlo artefact for node {key}: run scripts/run_kernel_mc.py for it first"]
    row = json.loads(f.read_text())
    # THE SCHEMA THE GATE READS (the physics chair, 2026-09-17): an artefact from a producer version
    # outside the tree can carry a number under a name the fit reads with another meaning; every key
    # the gate reads must be present, or the node is re-run.
    missing = [k for k in REQUIRED_DETAIL if k not in row.get("detail", {})]
    if missing:
        return [f"node {key}'s artefact lacks {missing}: written by another producer version, re-run its Monte Carlo"]
    again, why = judge(row.get("readings", {}), readings)   # re-judged against the rules in force now, on the caller's set
    if again != "PASS":
        return [f"node {key} does not pass the current gate: " + "; ".join(why)]
    if row.get("model_sha") != model_digest(model_file):
        what = model_file.name if model_file is not None else f"{len(model_population())} modules from fullmodel.py"
        return [f"node {key}'s artefact was written against another version of the model ({what}): re-run its Monte Carlo"]
    return []


def require_node(key: str, cache: Optional[pathlib.Path] = None, readings=None) -> None:
    bad = status_node(key, cache, readings=readings)
    if bad:
        raise KernelUnvalidated("; ".join(bad))


def reading(key: str, cache: Optional[pathlib.Path] = None, readings=None) -> Dict[str, Any]:
    """The node's artefact, refused unless it reads PASS on the caller's reading set and was written
    against the model file's own digest."""
    require_node(key, cache, readings)
    return json.loads((mc_dir(cache) / f"{key}.json").read_text())


GRID_STEP_UM = 2.0        # the finest node spacing the producer writes
MAX_SPAN_UM = 8.0         # the widest gap the interpolation may bridge (coarse first, owner 2026-09-17 02:40)
CURVATURE_TOL = 2e-3      # the second difference across three neighbouring nodes, a bound on the linear error


def _validated_waists(m2: float, rho: float, T_C: float, P_mW: float, cache: Optional[pathlib.Path] = None,
                      readings=None) -> list:
    """The waists with a PASSING, fresh artefact at these conditions (on the caller's reading set), sorted."""
    d = mc_dir(cache)
    if not d.is_dir():
        return []
    suffix = node_key(0.0, m2, rho, T_C, P_mW).split("_", 1)[1]
    out = []
    for f in d.glob(f"w*_{suffix}.json"):
        try:
            w = float(f.name[1:].split("_", 1)[0])
        except ValueError:
            continue
        if not status_node(f.stem, cache, readings=readings):
            out.append(w)
    return sorted(out)


def depletion_factor(w0_um: float, line: str, m2: float = 1.0, rho: float = 0.94, T_C: float = 130.0,
                     P_mW: float = 225.0, cache: Optional[pathlib.Path] = None, readings=None) -> float:
    """The surviving transit kernel's width over the bare collected kernel at this node, for
    the fit: `transit_fwhm x depletion_factor`. Read from the node's artefact when the waist
    sits on a validated node; between two validated nodes it is interpolated linearly, whatever
    their spacing up to `MAX_SPAN_UM`, because the factor moves by a part in a thousand per micron
    (5.2 to 2.25 per cent from the retired convention's waist to 90 um at 225 mW, 2026-09-16) and a coarse node grid is the
    order's own preference. The error of the straight line is bounded by the second difference
    across the three nearest nodes where a third exists (`CURVATURE_TOL`), and a waist outside the
    validated span, a gap wider than the bound, or a curvature over the tolerance is refused."""
    w = float(w0_um)
    ws = _validated_waists(m2, rho, T_C, P_mW, cache, readings)
    if not ws:
        raise KernelUnvalidated(f"no validated node at m2 {m2}, rho {rho}, T {T_C}, P {P_mW}: run scripts/run_kernel_mc.py first")
    def _f(x):
        return 1.0 + float(reading(node_key(x, m2, rho, T_C, P_mW), cache, readings)["detail"]["depletion_widening_rel"][line])
    for x in ws:
        if abs(w - x) < 1e-9:
            return _f(x)
    lo = [x for x in ws if x < w]; hi = [x for x in ws if x > w]
    if not lo or not hi:
        raise KernelUnvalidated(f"waist {w} um is outside the validated span {ws[0]}-{ws[-1]} um at these conditions")
    a, b = lo[-1], hi[0]
    if b - a > MAX_SPAN_UM + 1e-9:
        raise KernelUnvalidated(f"the validated nodes about {w} um are {a} and {b}, a gap over {MAX_SPAN_UM} um: validate a node between them")
    fa, fb = _f(a), _f(b)
    third = (lo[-2] if len(lo) > 1 else (hi[1] if len(hi) > 1 else None))
    if third is not None:
        xs = sorted([a, b, third]); ys = [_f(x) for x in xs]
        h1, h2 = xs[1] - xs[0], xs[2] - xs[1]
        curv = abs((ys[2] - ys[1]) / h2 - (ys[1] - ys[0]) / h1) * (b - a) / 2.0     # the linear error's bound over the gap
        if curv > CURVATURE_TOL:
            raise KernelUnvalidated(f"the depletion factor bends by {curv:.2g} across {xs} um, over {CURVATURE_TOL}: validate a node between {a} and {b}")
    return fa + (w - a) / (b - a) * (fb - fa)


def preflight(conditions, w0_lo: float, w0_hi: float, *, line: str = "4121",
              cache: Optional[pathlib.Path] = None, readings=None) -> list:
    """Every refusal a long run over this waist span would meet, found in seconds.

    THE DEFECT THIS EXISTS FOR (F91, 2026-09-17): the closure ran for eight hours and died on
    `KernelUnvalidated` at a waist the node grid did not reach, and eight of the L's conditions
    then still carried a 10 um gap between 80 and 90 against the 8 um interpolation bound -- so
    the SAME run would have died again, later, at a different waist. Nothing asked the question
    before the run, and the question costs a second: the gate already knows every node it holds.

    Returns one string per refusal, empty when the span is clear. It PROBES `depletion_factor`
    itself at each end of the span and at the midpoint of every gap inside it, rather than
    re-deriving the three refusal rules here, because a preflight that reimplements the gate
    drifts from the gate and then certifies a span the gate will refuse.
    """
    out = []
    lo, hi = float(w0_lo), float(w0_hi)
    for cond in conditions:
        m2, rho, T_C, P_mW = cond
        ws = _validated_waists(m2, rho, T_C, P_mW, cache, readings)
        probes = [lo, hi] + [0.5 * (a + b) for a, b in zip(ws, ws[1:]) if b > lo and a < hi]
        for w in sorted(set(round(x, 6) for x in probes)):
            if not (lo - 1e-9 <= w <= hi + 1e-9):
                continue
            try:
                depletion_factor(w, line, m2, rho, T_C, P_mW, cache, readings)
            except KernelUnvalidated as e:
                out.append(f"m2 {m2} rho {rho} T {T_C} P {P_mW} at {w:g} um: {e}")
                break
    return out


def require_span(conditions, w0_lo: float, w0_hi: float, *, line: str = "4121",
                 cache: Optional[pathlib.Path] = None, readings=None) -> None:
    """`preflight` as a refusal, for a producer to call BEFORE its first expensive cell. `readings`
    names the subset of `READINGS` the producer consumes (`WAIST_READINGS` for a free-amplitude fit)."""
    bad = preflight(conditions, w0_lo, w0_hi, line=line, cache=cache, readings=readings)
    if bad:
        raise KernelUnvalidated(
            f"{len(bad)} condition(s) cannot serve waists {w0_lo:g}-{w0_hi:g} um; "
            f"validate the nodes first (scripts/run_kernel_mc.py --w0 <um> --T <C> --P <mW>):\n  "
            + "\n  ".join(bad[:8]))


K3_GRID_TOL = 0.01
"""How far the third cumulant may move when the chord grid is halved, as a fraction of the
reference k3. The rule file asks for both halves -- "Compute it on a halved grid too and refuse
the row when the two disagree" -- and until 2026-09-18 this file did only the first: `judge`
tested that `grid_movement` was PRESENT and never what it said. So a diagnostic pinned at ~1.9 by
a sign defect in the producer's halved-grid path rode through 744 validated nodes without comment,
and the third cumulant -- the odd channel this whole record turns on -- had never actually had its
convergence read. A number a mechanism computes and no mechanism grades is a comment.

0.01 is set from the MEASUREMENT and not from taste: with the sign repaired, 25 nodes spanning
40 to 90 um and every one of the L's conditions read 1.3e-4 to 1.6e-3, median 7e-4, so this sits
about six times above the worst observed and two orders below the defect it would have caught.
Widen it only against a re-measured distribution, never to admit one node."""


_DETAIL_OK = {"node": {}, "depletion_widening_rel": {"4121": 0.005}, "depletion_fwhm_rel": {"4121": 0.05}, "depletion_note": "plant"}


def _self_test() -> list:
    import tempfile
    bad = []
    ok = {n: {"mc": 1.0, "model": 1.0} for n in READINGS}
    ok["ramp_k3_rel"]["grid_movement"] = 1e-4
    with tempfile.TemporaryDirectory() as td:
        c = pathlib.Path(td); key = node_key(64.0)
        try:
            require_node(key, c); bad.append("kernel-mc: a node with no artefact was admitted")
        except KernelUnvalidated:
            pass
        off = json.loads(json.dumps(ok)); off["transit_fwhm_rel"] = {"mc": 1.05, "model": 1.0}
        record_node(key, off, cache=c)
        try:
            require_node(key, c); bad.append("kernel-mc: a FAIL artefact was admitted")
        except KernelUnvalidated:
            pass
        absent = json.loads(json.dumps(ok)); del absent["shares_abs"]
        record_node(key, absent, cache=c)
        try:
            require_node(key, c); bad.append("kernel-mc: an artefact missing a reading was admitted")
        except KernelUnvalidated:
            pass
        nogm = json.loads(json.dumps(ok)); nogm["ramp_k3_rel"] = {"mc": 1.0, "model": 1.0}
        record_node(key, nogm, cache=c)
        try:
            require_node(key, c); bad.append("kernel-mc: a third cumulant with no grid movement was admitted")
        except KernelUnvalidated:
            pass
        record_node(key, ok, detail=_DETAIL_OK, cache=c)
        try:
            require_node(key, c)
        except KernelUnvalidated as exc:
            bad.append(f"kernel-mc: a PASS artefact was refused: {exc}")
        # D1 (2026-09-18): a node failing ONLY the amplitude's power law is refused by default and
        # admitted on the waist set; a node failing a waist reading is refused on both; an unknown
        # or empty reading set is a ValueError, never a silent admission.
        amp = json.loads(json.dumps(ok)); amp["amplitude_power_law_abs"] = {"mc": 1.05, "model": 1.0}
        record_node(key, amp, detail=_DETAIL_OK, cache=c)
        try:
            require_node(key, c); bad.append("kernel-mc: a node failing the amplitude law was admitted on the default set")
        except KernelUnvalidated:
            pass
        try:
            require_node(key, c, readings=WAIST_READINGS)
        except KernelUnvalidated as exc:
            bad.append(f"kernel-mc: a node failing only the amplitude law was refused on the waist set: {exc}")
        k3off = json.loads(json.dumps(ok)); k3off["ramp_k3_rel"] = {"mc": 1.2, "model": 1.0, "grid_movement": 1e-4}
        record_node(key, k3off, detail=_DETAIL_OK, cache=c)
        try:
            require_node(key, c, readings=WAIST_READINGS); bad.append("kernel-mc: a node failing k3 was admitted on the waist set")
        except KernelUnvalidated:
            pass
        for wrong in (("no_such_reading",), ()):
            try:
                require_node(key, c, readings=wrong); bad.append(f"kernel-mc: the reading set {wrong} was accepted")
            except ValueError:
                pass
            except KernelUnvalidated:
                bad.append(f"kernel-mc: the reading set {wrong} refused as a gate verdict instead of a ValueError")
        # THE DIGEST PIN (2026-09-18): a pinned run whose model moved refuses to write; the same pin
        # at the current digest writes; no pin writes.
        _saved = os.environ.get(DIGEST_PIN_ENV)
        try:
            os.environ[DIGEST_PIN_ENV] = "0000000000000000"
            try:
                record_node(key, ok, detail=_DETAIL_OK, cache=c); bad.append("kernel-mc: a node was written under a pin the model has moved from")
            except ModelMovedUnderRun:
                pass
            os.environ[DIGEST_PIN_ENV] = model_digest()
            try:
                record_node(key, ok, detail=_DETAIL_OK, cache=c)
            except ModelMovedUnderRun:
                bad.append("kernel-mc: a node was refused under a pin equal to the current digest")
        finally:
            if _saved is None:
                os.environ.pop(DIGEST_PIN_ENV, None)
            else:
                os.environ[DIGEST_PIN_ENV] = _saved
        record_node(key, ok, detail=_DETAIL_OK, cache=c)
        newer = c / "model.py"; time.sleep(0.02); newer.write_text("# a newer model\n")
        if not status_node(key, c, model_file=newer):
            bad.append("kernel-mc: an artefact written against another model was admitted")
        # F95's plants: the population carries the kernel's own module and not the judge, and a code
        # change in ANY member moves the digest while a docstring change in it does not
        names = {f.stem for f in model_population()}
        for need in ("fullmodel", "lineshape", "stark", "cascade", "amplitudes"):
            if need not in names:
                bad.append(f"kernel-mc: the model population lacks {need}")
        if "kernel_gate" in names:
            bad.append("kernel-mc: the judge is inside the model population")
        a, b = c / "a.py", c / "b.py"
        a.write_text("X = 1\n"); b.write_text('def f():\n    \"\"\"doc\"\"\"\n    return 2\n')
        d0 = model_digest(files=(a, b))
        b.write_text('def f():\n    \"\"\"a corrected sentence\"\"\"\n    return 2\n')
        if model_digest(files=(a, b)) != d0:
            bad.append("kernel-mc: a docstring edit in the second module moved the digest")
        b.write_text('def f():\n    \"\"\"a corrected sentence\"\"\"\n    return -2\n')
        if model_digest(files=(a, b)) == d0:
            bad.append("kernel-mc: a code edit in the second module did not move the digest")
        # F96: an attribute docstring (a bare string after an assignment) is prose too, while a
        # string that is an assigned VALUE is code
        a.write_text("X = 1\n'the unit of X'\nLABEL = 'red'\n")
        d1 = model_digest(files=(a, b))
        a.write_text("X = 1\n'the unit of X, corrected'\nLABEL = 'red'\n")
        if model_digest(files=(a, b)) != d1:
            bad.append("kernel-mc: an attribute docstring edit moved the digest")
        a.write_text("X = 1\n'the unit of X, corrected'\nLABEL = 'blue'\n")
        if model_digest(files=(a, b)) == d1:
            bad.append("kernel-mc: a changed string VALUE did not move the digest")
        # F97: the cache is keyed on the stamps, so a code edit is still seen after a cached read
        a.write_text("X = 1\n'the unit of X, corrected'\nLABEL = 'blue'\n")
        d2 = model_digest(files=(a, b)); d2_again = model_digest(files=(a, b))
        time.sleep(0.01); a.write_text("X = 2\n'the unit of X, corrected'\nLABEL = 'blue'\n")
        if d2 != d2_again or model_digest(files=(a, b)) == d2:
            bad.append("kernel-mc: the digest cache hid a code edit or returned a different value twice")
    return bad


def main(argv) -> int:
    if "--self-test" in argv:
        bad = _self_test()
        print("kernel-mc self-test: " + ("PASS" if not bad else "FAIL\n  " + "\n  ".join(bad)))
        return 1 if bad else 0
    if "--status" in argv:
        d = mc_dir()
        rows = sorted(d.glob("*.json")) if d.is_dir() else []
        print(f"kernel-mc: {len(rows)} node artefact(s) under {d}")
        for f in rows:
            print(f"  {f.stem}: {json.loads(f.read_text()).get('verdict')}")
        return 0
    print(__doc__); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
