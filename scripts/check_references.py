#!/usr/bin/env python
"""Resolve every inline data reference against its source, or fail naming it.

THE SYSTEM THIS IMPLEMENTS (private/REFERENCE_SYSTEM_DESIGN_2026-08-24.md).
A quoted number carries its reference inline, as a standard markdown link
whose target is the source file and whose title is a machine-readable key:

    [0.030](../results/beta_pooling.csv "ref:beta_pooling:pooled:bound_95")

The reader gets one click to the source (GitHub renders the CSV as a
table). This checker gets the machine channel: it scans tracked markdown
for `ref:` titles, resolves each key, and compares the LINK TEXT, the
number the reader actually reads, against the source value at the
precision the page prints. A regenerated CSV therefore fails every stale
quoting site BY NAME, which is the anti-staleness half: the failure list
is the notification, and staleness cannot be committed.

Key forms:
    ref:<csv-stem>:<scope>:<quantity>   a results/ CSV cell (value column)
    ref:lit:<citekey>:<field>           a row of the lit page's values table
    ref:constant:<NAME>[:<unit>]        a constant of rb5s6s/constants.py, the SSOT of a
                                        physical constant (a results row echoing one is a
                                        copy); <unit> scales it: Hz, kHz, MHz, GHz, or a
                                        number such as 1e-6
    ref:expr:<expression over {key}s>   a number DERIVED from other references, so a
                                        computed fact never gets a second cell of its own
                                        (owner order O40). Each {key} inside the curly
                                        braces is one of the three forms above, and the
                                        expression around them is + - * / ** parentheses
                                        and numeric literals, read by a small ast walker
                                        with no eval() and no name lookup:
                                            [8](../results/x.csv "ref:expr:{x:speed:a} + 5")
                                        if x:speed:a holds 3, the page above is stale at 8
                                        and --fix rewrites it to 6.

The lit values table is a `## Values` section on docs/lit/<citekey>.md:
    | field | value | where in the paper |
and this checker compares against its `value` column, so a transcription
drift between the paper, the lit page and the prose has two named edges
instead of zero.

WHAT THIS DOES NOT SEE, recorded at birth rather than discovered: a
paraphrased number ("about three times" for 3.24), a unit-converted
restatement, and any quote with no reference at all. The first two stay
human; the third is the coverage ratchet's job, not this resolver's.

FOUR FURTHER MODES, the design's phase 4 and O40's propagation step:
  --fix    rewrite the PURE-VALUE link texts to the current source value
           at the precision the page printed, and only those: a value
           inside a sentence can falsify the prose around it, and no
           fixer may rewrite an argument. Flagged sites stay failures.
           A ref:expr: site is a pure value like any other and is
           rewritten by the same rule, at the same precision.
  --graph  emit docs/reference_graph.json, the derived dependents map:
           claim key to source, producer and quoting sites. Generated,
           never hand-edited, and not itself a quoting surface. A
           ref:expr: site is also recorded as a DEPENDENT of every
           reference its expression reads.
  --thesis-outbox PATH
           read one PhD-Thesis chapter file, READ-ONLY, find its own
           ref: tags, and append a row to
           private/cache/plan_2026-09-16/THESIS_OUTBOX.md for every tag
           whose cell has moved since the chapter's number was written.
           Never opens the chapter for writing: the chapter's own
           repository applies the row, this one only names it.
"""
from __future__ import annotations

import ast
import csv
import json
import operator
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AMBIGUOUS = "\0ambiguous"   # a coordinate matching more than one row
RESULTS = ROOT / "results"
LIT = ROOT / "docs" / "lit"

# A markdown inline link with a title: [text](target "title")
LINK = re.compile(
    r"\[(?P<text>[^\]]+)\]\(\s*(?P<target>[^)\s]+)\s+\"(?P<title>ref:[^\"]+)\"\s*\)")


#: The SAME tag in a python docstring, where a markdown link cannot go:
#: `2.85 [ref:moment_admission:effective_rank_admitted:]`. The number is the
#: token immediately before the bracket, which is what the link text is in the
#: markdown form.
PYLINK = re.compile(
    r"(?P<text>[-+]?\d[\d.eE+-]*)\s*\[(?P<title>ref:[^\]]+)\]")


def _tracked_markdown() -> list[str]:
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"],
                         capture_output=True, text=True)
    return out.stdout.split()


def _tracked_python() -> list[str]:
    """THE POPULATION WAS MARKDOWN ONLY, AND THAT IS WHERE FOUR NUMBERS HID.

    On 2026-09-12 an SNR range quoted in two `fullmodel.py` docstrings and a
    licence boundary in a third turned out to match no cell of the CSV they
    described, while this checker printed 458 references resolved and zero
    findings. It was not wrong: those numbers were outside its population.
    An exported docstring ports to the public mirror and is read as the
    module's own statement about a committed cell, so it belongs in the same
    population as the prose. This is the record's own rule about repairing the
    POPULATION rather than the name last found missing.
    """
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.py"],
                         capture_output=True, text=True)
    # THIS FILE IS THE ONE EXEMPTION AND IT IS STRUCTURAL, not a convenience:
    # the checker's own source must contain the marker it searches for, in its
    # regex and in its examples, so including it reports the instrument as a
    # defect in every run. Nothing else is exempt, and a second entry here
    # would need its own reason on this line.
    return [r for r in out.stdout.split()
            if r != "scripts/check_references.py"]


#: The raw-mark counts are regexes and not substrings: in python the marker is
#: also a string literal this file carries, and counting the bare text made the
#: checker report itself. A tag immediately preceded by a quote is code.
_MD_MARK = re.compile(r'"ref:')
_PY_MARK = re.compile(r'(?<!["\'])\[ref:')


def _reference_population() -> list[tuple[str, "re.Pattern", "re.Pattern"]]:
    """Every surface a reference may live on, with its link form and its mark.

    ONE BUILDER, because the checker and the graph emitter each had their own
    loop and the graph's was left on markdown when the checker's population
    grew. The comment at that site already said "THE SAME BLINDNESS AS
    main()'s, and it was left here when that one was fixed" -- about a previous
    divergence of exactly these two loops. This makes the divergence
    impossible rather than noting it a third time.
    """
    return ([(r, LINK, _MD_MARK) for r in _tracked_markdown()]
            + [(r, PYLINK, _PY_MARK) for r in _tracked_python()])


def _csv_cell(stem: str, a: str, b: str, col: str | None = None) -> str | None:
    """The first two columns are the row coordinates, whatever their names.

    The results tree carries three live schemas, (scope, quantity, value),
    (quantity, key, value) and wide per-peak tables, and unifying on
    position rather than on names means a reference key works against all
    of them: `ref:<stem>:<a>:<b>` matches the first two columns to (a, b)
    and reads `value`; the four-part form appends an explicit column name
    for the wide tables, `ref:beta_self_probe:pooled_slope::bound95_nscale`
    style with the second coordinate allowed empty.
    """
    path = RESULTS / f"{stem}.csv"
    if not path.exists():
        return None
    with path.open() as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        if not header or len(header) < 2:
            return None
        want = col if col else "value"
        if want not in header:
            return None
        vi = header.index(want)
        hits = [row[vi] for row in reader
                if len(row) > vi and row[0] == a and (b == "" or row[1] == b)]
    # AN AMBIGUOUS COORDINATE IS REFUSED, NOT RESOLVED TO THE FIRST HIT.
    # Until 2026-08-29 this returned on the first match, so a coordinate
    # naming several rows silently validated against whichever came first.
    # Measured then: 92 distinct coordinates in tracked markdown, 2 of them
    # ambiguous, both in the one results CSV whose first two columns were not
    # a key. No published number was wrong, because in both cases the first
    # row happened to be the one quoted -- which is exactly the shape of a
    # false pass, and why the resolver may not choose.
    #
    # THE FALSE-PASS DIRECTION: this cannot see a coordinate that is unique
    # today and becomes ambiguous when a producer adds a row, until the next
    # run. That is why the refusal lives here rather than in a one-off audit.
    if len(hits) > 1:
        return AMBIGUOUS
    return hits[0] if hits else None


def _lit_value(citekey: str, field: str) -> str | None:
    path = LIT / f"{citekey}.md"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^## Values\s*$(.*?)(?:^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and cells[0] == field:
            return cells[1]
    return None


_UNIT_SCALE = {"Hz": 1.0, "kHz": 1e-3, "MHz": 1e-6, "GHz": 1e-9, "": 1.0}


def _constant_value(name: str, unit: str = "") -> str | None:
    """A constant of the package at the unit the page prints, as the source string `_matches`
    compares against. The natural width on two platform-neutral pages was bound to a fibre-only
    file's echo of GAMMA_NAT_HZ on 2026-09-17, and the platform lane refused the citation: the
    constant's own module is its SSOT and this scheme binds to it directly."""
    try:
        from rb5s6s import constants as _K
        value = float(getattr(_K, name))
    except (ImportError, AttributeError, TypeError, ValueError):
        return None
    if unit in _UNIT_SCALE:
        scale = _UNIT_SCALE[unit]
    else:
        try:
            scale = float(unit)
        except ValueError:
            return None
    return f"{value * scale:.12g}"


def _matches(written: str, source: str) -> bool:
    """Compare at the precision the page prints, the prototype's rule."""
    w = written.strip().replace("−", "-")
    s = source.strip()
    if w == s:
        return True
    try:
        sval = float(s)
    except ValueError:
        return w == s
    stripped = w.lstrip("<>~ ").replace(",", "")
    try:
        float(stripped)
    except ValueError:
        return False
    places = len(stripped.split(".")[1]) if "." in stripped else 0
    return stripped == f"{sval:.{places}f}"


def _producers() -> dict[str, str]:
    """CSV stem to producer script, parsed from results/README.md's table.

    The table is the committed producer map (63 rows at writing); parsing
    it rather than duplicating it keeps one authority. A stem with no row
    maps to None and the graph says so rather than guessing.
    """
    out: dict[str, str] = {}
    readme = RESULTS / "README.md"
    if not readme.exists():
        return out
    # one index row may cover several files: "| `a.csv`, `b.csv` | `run.py`"
    row = re.compile(r"^\|([^|]+)\|\s*`([\w./]+\.py)`")
    for line in readme.read_text(encoding="utf-8").splitlines():
        m = row.match(line)
        if m:
            for stem in re.findall(r"`([\w.]+)\.csv`", m.group(1)):
                out[stem] = m.group(2)
    return out


# THE DERIVED FORM (owner order O40, private/OWNER_ORDERS.tsv). A number computed from other
# references never gets a cell of its own: giving it one would be a SECOND source of truth for
# the same fact. ref:expr:<expression> reads other ref: keys, each written {key} inside curly
# braces, combines them with + - * / ** parentheses and numeric literals, and is evaluated by
# the small ast walker below. No eval(), no name lookup, no call: an expression written in a
# document is data, and the whitelist is the whole language it gets.

_EXPR_TOKEN = re.compile(r"\{([^{}]+)\}")

_EXPR_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
             ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
             ast.UAdd: operator.pos}


class ExprError(Exception):
    """A ref:expr: this checker refuses instead of guessing: a {key} it cannot resolve, or
    syntax outside the arithmetic whitelist. Always raised, never swallowed into a pass."""


def _resolve_plain_key(key: str) -> str | None:
    """One of the three plain schemes (constant, lit, or a results/ coordinate) resolved to
    its source string, the same dispatch _report() and _scan() use for a top-level ref: tag.

    Never an expr: key: an expression may combine only the leaf schemes below, so nesting one
    derivation inside another is refused at the point it would be read, not chased.
    """
    parts = key.split(":")
    if parts[0] == "constant" and len(parts) in (2, 3):
        return _constant_value(parts[1], parts[2] if len(parts) == 3 else "")
    if parts[0] == "lit" and len(parts) == 3:
        return _lit_value(parts[1], parts[2])
    if parts[0] not in ("lit", "expr") and len(parts) in (3, 4):
        v = _csv_cell(*parts)
        return None if v is AMBIGUOUS else v
    return None


def _eval_expr_node(node: ast.AST) -> float:
    """Evaluate arithmetic only, ast node types spelled out one by one.

    A Name, a Call, an Attribute, a Subscript, a string, or any other Constant that is not a
    plain number: none of these appear in the chain below, so none of them evaluate. Calling
    eval() on text a document carries is how a document becomes a shell, and this walker is
    built so that no path through it can call anything at all.
    """
    if isinstance(node, ast.Expression):
        return _eval_expr_node(node.body)
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return float(node.value)
        raise ExprError(f"{node.value!r} is not a numeric literal")
    if isinstance(node, ast.BinOp) and type(node.op) in _EXPR_OPS:
        return _EXPR_OPS[type(node.op)](_eval_expr_node(node.left), _eval_expr_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _EXPR_OPS:
        return _EXPR_OPS[type(node.op)](_eval_expr_node(node.operand))
    raise ExprError(f"{type(node).__name__} is outside the arithmetic whitelist (only "
                     f"+ - * / ** and parentheses over numeric literals and {{key}} references)")


def _eval_expr(expr: str) -> float:
    """Substitute every {key} with its resolved source value, then evaluate the arithmetic.

    Substitution happens on TEXT, before any parsing, and every substituted value passes
    through repr(float(...)) on its way in, so a resolved value can never itself carry a name
    or a call into the parser: the parser only ever sees numbers and operators.
    """
    missing: list[str] = []

    def sub(m: re.Match) -> str:
        v = _resolve_plain_key(m.group(1))
        if v is None:
            missing.append(m.group(1))
            return "0"
        try:
            return repr(float(v))
        except ValueError:
            missing.append(m.group(1))
            return "0"

    substituted = _EXPR_TOKEN.sub(sub, expr)
    if missing:
        raise ExprError(f"unresolved reference(s): {', '.join(missing)}")
    try:
        tree = ast.parse(substituted, mode="eval")
    except SyntaxError as exc:
        raise ExprError(f"not a valid arithmetic expression: {exc}") from exc
    return _eval_expr_node(tree)


def _eval_expr_or_none(expr: str) -> tuple[str | None, str | None]:
    """(the evaluated value as a string, an error message). Exactly one of the two is None."""
    try:
        return repr(_eval_expr(expr)), None
    except ExprError as exc:
        return None, str(exc)


def _resolve_any_key(key: str) -> str | None:
    """Every scheme this checker resolves, ref:expr: included: the one call a caller that
    wants only the current value, and not the report-mode wording, should make."""
    if key.startswith("expr:"):
        v, _err = _eval_expr_or_none(key[len("expr:"):])
        return v
    return _resolve_plain_key(key)


def _at_precision(source: str, written: str) -> str:
    """Format a resolved value at the decimal places the page's own written number used.

    The one formatting rule _fix() and --thesis-outbox both need, so a page's digits are
    never rewritten to more, or fewer, decimals than it already carried.
    """
    stripped = written.strip().lstrip("<>~ ")
    places = len(stripped.split(".")[1]) if "." in stripped else 0
    try:
        return f"{float(source):.{places}f}"
    except ValueError:
        return source


def _scan() -> list[dict]:
    """Every reference in the corpus, resolved, one record each."""
    records = []
    # THE GRAPH'S POPULATION FOLLOWS THE CHECKER'S. When the checker gained
    # tracked python, a graph still walking markdown alone would have produced
    # a dependents map missing every docstring edge, which the enforcement
    # report then reads as the whole truth.
    for rel, _RE, _MARK in _reference_population():
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not _MARK.search(text):
            continue
        # THE SAME BLINDNESS AS main()'s, and it was left here when that one was
        # fixed. --graph writes a graph missing the tag and --fix reports "0
        # flagged for a human" while leaving the malformed reference in place: a
        # false "nothing needs you" from the tool whose job is saying otherwise.
        _raw, _seen = len(_MARK.findall(text)), len(_RE.findall(text))
        if _raw > _seen:
            raise SystemExit(
                f"check_references: {rel} carries {_raw - _seen} ref: tag(s) "
                "outside a well-formed link. Run without --graph/--fix to see "
                "them; neither mode may write while a tag is unreadable.")
        for m in _RE.finditer(text):
            key = m.group("title")[len("ref:"):]
            line = text[: m.start()].count("\n") + 1
            if key.startswith("expr:"):
                expr_text = key[len("expr:"):]
                source, _err = _eval_expr_or_none(expr_text)
                records.append(dict(
                    key=key, file=rel, line=line, written=m.group("text"),
                    source=source, source_file=None, producer=None,
                    span=m.span(), expr=expr_text,
                    expr_refs=_EXPR_TOKEN.findall(expr_text)))
                continue
            parts = key.split(":")
            if parts[0] == "constant" and len(parts) in (2, 3):
                source = _constant_value(parts[1], parts[2] if len(parts) == 3 else "")
                src_file = "rb5s6s/constants.py"
                producer = None
            elif parts[0] == "lit" and len(parts) == 3:
                source = _lit_value(parts[1], parts[2])
                src_file = f"docs/lit/{parts[1]}.md"
                producer = None
            elif parts[0] != "lit" and len(parts) in (3, 4):
                source = _csv_cell(*parts)
                # The graph records resolved values. An ambiguous coordinate
                # has no resolved value, so it is recorded as unresolved and
                # the checker's own run is what reports it.
                if source is AMBIGUOUS:
                    source = None
                src_file = f"results/{parts[0]}.csv"
                producer = _producers().get(parts[0])
            else:
                source, src_file, producer = None, None, None
            records.append(dict(
                key=key, file=rel, line=line, written=m.group("text"),
                source=source, source_file=src_file, producer=producer,
                span=m.span()))
    return records


def _emit_graph() -> Path:
    graph: dict[str, dict] = {}
    for r in _scan():
        node = graph.setdefault(r["key"], dict(
            source_file=r["source_file"], producer=r["producer"],
            source_value=r["source"], quoting_sites=[]))
        node["quoting_sites"].append(
            dict(file=r["file"], line=r["line"], writes=r["written"]))
        # A ref:expr: SITE IS A DEPENDENT OF EVERY REFERENCE IT READS, not a quoting site of
        # them: the number it prints is a FUNCTION of theirs, not a copy, so it is recorded on
        # each dependency's own node under its own key. A dependency named only inside an
        # expression, never quoted on its own anywhere, still gets a node here.
        for dep_key in r.get("expr_refs") or []:
            dep = graph.setdefault(dep_key, dict(
                source_file=None, producer=None, source_value=None, quoting_sites=[]))
            dep.setdefault("expr_dependents", []).append(
                dict(file=r["file"], line=r["line"], expr=r.get("expr")))
    out = ROOT / "docs" / "reference_graph.json"
    out.write_text(json.dumps(graph, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    return out


_PURE = re.compile(r"^[<>~\s]*-?[\d.,()]+$")


def _fix() -> int:
    """Rewrite pure-value link texts to the source, report the rest."""
    rewritten = flagged = 0
    moved: list = []
    by_file: dict[str, list] = {}
    for r in _scan():
        if r["source"] is None or _matches(r["written"], r["source"]):
            continue
        by_file.setdefault(r["file"], []).append(r)
    for rel, rs in by_file.items():
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")
        for r in sorted(rs, key=lambda x: -x["span"][0]):
            if not _PURE.match(r["written"]):
                print(f"  FLAGGED {rel}:{r['line']}: {r['written']!r} is "
                      f"inside prose, source now {r['source']!r}, a human "
                      f"decides what the sentence still means")
                flagged += 1
                continue
            newtext = _at_precision(r["source"], r["written"])
            prefix = r["written"][: len(r["written"]) - len(r["written"].lstrip("<>~ "))]
            a, b = r["span"]
            old_link = text[a:b]
            if old_link.lstrip().startswith("["):
                new_link = old_link.replace(f"[{r['written']}]",
                                            f"[{prefix}{newtext}]", 1)
            else:
                # THE PYTHON FORM IS NOT A LINK, and assuming it was made this
                # fixer report rewrites it had not made. In a docstring the
                # reference reads `23.23 [ref:...]`, so the value is the token
                # BEFORE the bracket and `[23.23]` appears nowhere: the replace
                # matched nothing, the file was written back unchanged, and the
                # count and the message went up regardless. Two stale SNR
                # figures in `fullmodel.py` survived three --fix passes that
                # way, on the very population `_tracked_python` was built for.
                new_link = re.sub(r"^\s*[-+]?\d[\d.eE+-]*",
                                  f"{prefix}{newtext}", old_link, count=1)
            if new_link == old_link:
                # AND THE CLAIM IS NOW EVIDENCE: a no-op cannot be reported as
                # a rewrite, whatever form a future surface writes its
                # references in.
                print(f"  REFUSED {rel}:{r['line']}: {r['written']!r} -> "
                      f"{newtext!r} changed nothing, the link form is unhandled")
                flagged += 1
                continue
            text = text[:a] + new_link + text[b:]
            rewritten += 1
            print(f"  rewrote {rel}:{r['line']}: {r['written']!r} -> "
                  f"{prefix}{newtext!r}")
            # THE NUMBER IS CURRENT AND THE SENTENCE MAY NOT BE (2026-09-22,
            # and the owner's "the SSOT fixed once for all, also in the prose"). A rewrite keeps the
            # digits true to the cell and says nothing about the claim built around them: an estimator
            # passage read "close to tied" while its own cells had moved apart. So every moved value
            # prints the sentence it sits in, and the landing re-reads that list.
            moved.append((rel, r["line"], r["written"], f"{prefix}{newtext}", _sentence_at(text, a)))
        path.write_text(text, encoding="utf-8")
    if moved:
        print("\nfix: the sentences whose bound value MOVED, to be re-read before the landing "
              "(a current number can still sit in a stale claim):")
        for rel, line, old, new, sent in moved:
            print(f"  {rel}:{line}: {old} -> {new}\n      {sent}")
    print(f"fix: {rewritten} rewritten, {flagged} flagged for a human, {len(moved)} sentence(s) to re-read")
    return 0 if flagged == 0 else 1


#: The propagation surface's own log: private/cache/plan_2026-09-16/THESIS_OUTBOX.md, rows this
#: repository owes the PhD-Thesis chapter. --thesis-outbox appends to it, nothing else in this
#: file opens it, and a plant never points this NAME at the real path, it passes outbox_path
#: instead (a scratch path in every test, per the working rules for this repository).
THESIS_OUTBOX = ROOT / "private" / "cache" / "plan_2026-09-16" / "THESIS_OUTBOX.md"

_HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)


def _sentence_at(text: str, index: int) -> str:
    """The sentence a rewritten value sits in, for the re-read list.

    A markdown table row is one cell and not one sentence, so the cell is the unit there; elsewhere the
    unit is the sentence, bounded by a full stop and a space or by the line. Collapsed to one line
    because the reader reads a list, and capped so one long row cannot bury the rest."""
    start = text.rfind("\n", 0, index) + 1
    end = text.find("\n", index)
    end = len(text) if end < 0 else end
    line = text[start:end]
    at = index - start
    if line.lstrip().startswith("|"):
        cuts = [i for i, ch in enumerate(line) if ch == "|"]
        lo = max([c for c in cuts if c <= at], default=-1) + 1
        hi = min([c for c in cuts if c > at], default=len(line))
        out = line[lo:hi]
    else:
        lo = max(line.rfind(". ", 0, at) + 2, 0)
        hi = line.find(". ", at)
        out = line[lo:(hi + 1 if hi > 0 else len(line))]
    out = " ".join(out.split())
    return out if len(out) <= 300 else out[:297] + "..."


def _section_at(text: str, upto_line: int) -> str:
    """The nearest markdown heading at or before a line, for the outbox row's own section
    column. 'front matter' names anything before the chapter's first heading."""
    best = "front matter"
    for hm in _HEADING.finditer(text):
        hline = text[: hm.start()].count("\n") + 1
        if hline > upto_line:
            break
        best = hm.group(2).strip()
    return best


def _thesis_outbox(chapter_path: str, outbox_path: str | None = None) -> int:
    """Read one PhD-Thesis chapter, find its ref: tags, and append one outbox row per tag
    whose cell has moved since the chapter's own number was written.

    READ-ONLY on the chapter, always: chapter_path is only ever passed to Path.read_text,
    never to a write call, so a stale chapter number becomes a row here for a human to carry
    across, never an edit this repository makes on the other side of the boundary (the
    outbox's own header names why: the two repositories' safety probes cannot see each
    other's open work). A tag this checker cannot resolve is skipped, not guessed: that is a
    citation defect in the chapter's own repository, and this tool's population is this
    repository's tracked files, never the chapter's.
    """
    chapter = Path(chapter_path)
    if not chapter.exists():
        print(f"check_references: --thesis-outbox {chapter_path} does not exist, nothing read")
        return 1
    text = chapter.read_text(encoding="utf-8")
    rows = []
    for m in LINK.finditer(text):
        key = m.group("title")[len("ref:"):]
        line = text[: m.start()].count("\n") + 1
        current = _resolve_any_key(key)
        if current is None:
            continue
        if not _matches(m.group("text"), current):
            rows.append((_section_at(text, line), m.group("text"),
                         _at_precision(current, m.group("text")), key))
    outbox = Path(outbox_path) if outbox_path else THESIS_OUTBOX
    if rows:
        outbox.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with outbox.open("a", encoding="utf-8") as fh:
            fh.write(f"\n## {stamp}, from check_references.py --thesis-outbox "
                      f"{chapter.name}\n\n")
            fh.write("| chapter section | old reading | new reading | the cell |\n")
            fh.write("|---|---|---|---|\n")
            for section, old, new, key in rows:
                fh.write(f"| {section} | {old} | {new} | `ref:{key}` |\n")
    print(f"check_references: --thesis-outbox {chapter.name}: {len(rows)} "
          f"row(s) appended to {outbox}")
    return 0


def main() -> int:
    if "--thesis-outbox" in sys.argv:
        idx = sys.argv.index("--thesis-outbox")
        if idx + 1 >= len(sys.argv):
            print("check_references: --thesis-outbox needs a chapter path")
            return 2
        return _thesis_outbox(sys.argv[idx + 1])
    if "--graph" in sys.argv:
        out = _emit_graph()
        print(f"check_references: graph written to {out.relative_to(ROOT)}")
        return 0
    if "--fix" in sys.argv:
        return _fix()
    return _report()


def _report() -> int:
    """The default mode: every reference resolved and compared, findings printed and counted.

    Factored out of main() so a caller can read the exit code directly, without sys.argv or a
    subprocess: main() is now a thin dispatcher over four modes, matching how --fix, --graph
    and --thesis-outbox were already their own functions.
    """
    bad: list[str] = []
    n_refs = 0
    # THE RAW-MARK COUNT IS A REGEX AND NOT A SUBSTRING, because in python the
    # marker is also a string literal this very file carries: counting the bare
    # text made the checker report itself as holding an unparseable tag. A tag
    # immediately preceded by a quote is code, not prose.
    _pop = _reference_population()
    for rel, _RE, _MARK in _pop:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not _MARK.search(text):
            continue
        # A MALFORMED LINK DOES NOT FAIL THIS CHECKER, IT VANISHES FROM IT.
        # `[0.97(` for `[0.97](` shipped on 2026-09-05: the file's tag count
        # fell from 9 to 8 and the run still printed "0 findings", so a
        # one-character typo silently removed a provenance check from a number
        # and every guard stayed green. Comparing the raw tags
        # against the parsed ones turns that silence into a finding.
        #
        # THE COMPARISON IS OVER THE WHOLE TEXT AND NEVER PER LINE. `\s`
        # matches a newline, so a link may wrap between its target and its
        # title and still resolve; four in the correction record's first
        # chapter do. The line-based
        # draft of this check reported all four as defects, an exemption list
        # four times its findings, which is the failure the quotation guard's
        # first design already taught this record.
        _raw, _seen = len(_MARK.findall(text)), len(_RE.findall(text))
        if _raw > _seen:
            _rest = _RE.sub("", text)
            _at = [str(_i) for _i, _ln in enumerate(text.splitlines(), 1)
                   if _MARK.search(_ln) and _ln.strip() and _ln.strip() in _rest]
            bad.append(
                f"{rel}: UNPARSEABLE, {_raw - _seen} ref: tag(s) not inside a "
                f"well-formed [text](target \"ref:...\") link "
                f"(line(s) {', '.join(_at) or 'not located'}). Such a tag "
                f"resolves nothing and is invisible to this checker, so the "
                f"number it should certify goes unchecked.")
        for m in _RE.finditer(text):
            n_refs += 1
            key = m.group("title")[len("ref:"):]
            line = text[: m.start()].count("\n") + 1
            where = f"{rel}:{line}"
            if key.startswith("expr:"):
                expr_text = key[len("expr:"):]
                value, err = _eval_expr_or_none(expr_text)
                if err is not None:
                    bad.append(f"{where}: EXPRESSION ERROR, ref:expr:{expr_text} - {err}")
                elif not _matches(m.group("text"), value):
                    bad.append(f"{where}: writes {m.group('text')!r}, the expression "
                               f"{expr_text!r} evaluates to {value!r}")
                continue
            parts = key.split(":")
            if parts[0] == "constant":
                if len(parts) not in (2, 3):
                    bad.append(f"{where}: malformed constant key ref:{key}")
                    continue
                source = _constant_value(parts[1], parts[2] if len(parts) == 3 else "")
                kind = f"rb5s6s/constants.py {parts[1]}" + (f" in {parts[2]}" if len(parts) == 3 else "")
            elif parts[0] == "lit":
                if len(parts) != 3:
                    bad.append(f"{where}: malformed lit key ref:{key}")
                    continue
                source = _lit_value(parts[1], parts[2])
                kind = f"docs/lit/{parts[1]}.md values row {parts[2]!r}"
            else:
                if len(parts) not in (3, 4):
                    bad.append(f"{where}: malformed key ref:{key}")
                    continue
                source = _csv_cell(*parts)
                kind = (f"results/{parts[0]}.csv row ({parts[1]}, {parts[2]})"
                        + (f" column {parts[3]}" if len(parts) == 4 else ""))
            if source is AMBIGUOUS:
                bad.append(f"{where}: AMBIGUOUS, {kind} matches more than "
                           f"one row, so the tag cannot say which. Give the "
                           f"rows distinct coordinates in the producer.")
            elif source is None:
                bad.append(f"{where}: DANGLING, {kind} does not exist "
                           f"(renamed row or moved file)")
            elif not _matches(m.group("text"), source):
                bad.append(f"{where}: writes {m.group('text')!r}, {kind} "
                           f"holds {source!r}")
    print(f"check_references: {n_refs} references resolved, "
          f"{len(bad)} findings")
    for b in bad:
        print(f"  {b}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
