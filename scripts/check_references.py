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

The lit values table is a `## Values` section on docs/lit/<citekey>.md:
    | field | value | where in the paper |
and this checker compares against its `value` column, so a transcription
drift between the paper, the lit page and the prose has two named edges
instead of zero.

WHAT THIS DOES NOT SEE, recorded at birth rather than discovered: a
paraphrased number ("about three times" for 3.24), a unit-converted
restatement, and any quote with no reference at all. The first two stay
human; the third is the coverage ratchet's job, not this resolver's.

TWO FURTHER MODES, the design's phase 4:
  --fix    rewrite the PURE-VALUE link texts to the current source value
           at the precision the page printed, and only those: a value
           inside a sentence can falsify the prose around it, and no
           fixer may rewrite an argument. Flagged sites stay failures.
  --graph  emit docs/reference_graph.json, the derived dependents map:
           claim key to source, producer and quoting sites. Generated,
           never hand-edited, and not itself a quoting surface.
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
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
            parts = key.split(":")
            line = text[: m.start()].count("\n") + 1
            if parts[0] == "lit" and len(parts) == 3:
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
    out = ROOT / "docs" / "reference_graph.json"
    out.write_text(json.dumps(graph, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    return out


_PURE = re.compile(r"^[<>~\s]*-?[\d.,()]+$")


def _fix() -> int:
    """Rewrite pure-value link texts to the source, report the rest."""
    rewritten = flagged = 0
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
            stripped = r["written"].strip().lstrip("<>~ ")
            places = (len(stripped.split(".")[1]) if "." in stripped else 0)
            try:
                newtext = f"{float(r['source']):.{places}f}"
            except ValueError:
                newtext = r["source"]
            prefix = r["written"][: len(r["written"]) - len(r["written"].lstrip("<>~ "))]
            a, b = r["span"]
            old_link = text[a:b]
            new_link = old_link.replace(f"[{r['written']}]",
                                        f"[{prefix}{newtext}]", 1)
            text = text[:a] + new_link + text[b:]
            rewritten += 1
            print(f"  rewrote {rel}:{r['line']}: {r['written']!r} -> "
                  f"{prefix}{newtext!r}")
        path.write_text(text, encoding="utf-8")
    print(f"fix: {rewritten} rewritten, {flagged} flagged for a human")
    return 0 if flagged == 0 else 1


def main() -> int:
    if "--graph" in sys.argv:
        out = _emit_graph()
        print(f"check_references: graph written to {out.relative_to(ROOT)}")
        return 0
    if "--fix" in sys.argv:
        return _fix()
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
            parts = key.split(":")
            line = text[: m.start()].count("\n") + 1
            where = f"{rel}:{line}"
            if parts[0] == "lit":
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
