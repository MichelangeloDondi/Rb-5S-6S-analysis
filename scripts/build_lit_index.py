#!/usr/bin/env python3
"""
Single source of truth for the literature: docs/lit/<citekey>.md.

Each paper is one Markdown file with a YAML-ish frontmatter block (the structured
fields this script consumes) followed by a free Markdown body (the rich relevance
notes -- human-only). From those files this script regenerates two committed,
byte-reproducible views:

  docs/references.bib     BibTeX (for eventual LaTeX use; nothing consumes it yet)
  PDF_papers/README.md    the holdings index (one table, one column schema)

Usage:
  build_lit_index.py                 regenerate the two views in place
  build_lit_index.py --check         regenerate in memory, diff vs committed, exit 1 if stale
  build_lit_index.py --bootstrap     ONE-TIME: parse the existing references.bib into docs/lit/*.md
                                     (writes only files that do not already exist)

No third-party deps (no pyyaml): the frontmatter subset here is flat scalars +
short lists + one block scalar, handled by _parse_frontmatter below.
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIT_DIR = ROOT / "docs" / "lit"
BIB = ROOT / "docs" / "references.bib"
PDF_README = ROOT / "PDF_papers" / "README.md"   # LOCAL index (untracked)
PUBLIC_INDEX = ROOT / "docs" / "LITERATURE_INDEX.md"  # PUBLIC index (tracked)

# Fields emitted to BibTeX, in this fixed order (missing ones skipped).
BIB_FIELD_ORDER = ["author", "title", "journal", "booktitle", "howpublished",
                   "volume", "number", "pages", "year", "doi", "eprint",
                   "archivePrefix", "note"]

# Thematic sections mirroring docs/LITERATURE.md, in fixed emit order. The `section`
# frontmatter field selects one of these slugs; both generated views group by it.
# "unsorted" is the fallback bucket and always sorts last.
SECTION_ORDER = [
    ("prior-art",        "Nearest prior art (delineate from)"),
    ("collision-series", "Collision-rate / self-broadening series"),
    ("transit-time",     "Transit-time lineshape pedigree"),
    ("oist-lineage",     "This line (5S-6S, 993 nm): OIST apparatus lineage"),
    ("usafa-lineage",    "This line (5S-6S, 993 nm): USAFA (Knize/Lindsay) lineage"),
    ("method-anchors",   "Method anchors and reference standards"),
    ("landscape-24-26",  "The 2024-2026 landscape and future transitions"),
    ("deep-search",      "ONF community map and near-surface physics (Paper 2)"),
    ("unsorted",         "Unsorted"),
]
SECTION_TITLES = dict(SECTION_ORDER)
SECTION_SLUGS = [s for s, _ in SECTION_ORDER]


def _by_section(entries: list[dict]) -> dict:
    """Group entries by their `section` slug; unknown/missing -> 'unsorted'."""
    groups: dict = {}
    for e in entries:
        slug = e.get("section")
        if slug not in SECTION_TITLES:
            slug = "unsorted"
        groups.setdefault(slug, []).append(e)
    return groups

# ---------------------------------------------------------------------------
# tiny YAML-subset frontmatter (flat scalars, "- " lists, ">" block scalar)
# ---------------------------------------------------------------------------

def _scalar(v: str):
    v = v.strip()
    if v in ("null", "~", ""):
        return None
    if v == "true":
        return True
    if v == "false":
        return False
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        return inner.replace("''", "'") if v[0] == "'" else inner
    return v


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    end = text.index("\n---", 3)
    lines = text[3:end].splitlines()
    out: dict = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, rest = m.group(1), m.group(2)
        if rest.strip() in (">", "|", ">-", "|-"):  # block scalar
            buf = []
            i += 1
            while i < len(lines) and (lines[i].startswith("  ") or not lines[i].strip()):
                buf.append(lines[i].strip())
                i += 1
            out[key] = " ".join(b for b in buf if b)
            continue
        if rest.strip() == "[]":  # empty inline list
            out[key] = []
            i += 1
            continue
        if rest.strip() == "":  # maybe a block list
            items = []
            i += 1
            while i < len(lines) and lines[i].lstrip().startswith("- "):
                items.append(_scalar(lines[i].lstrip()[2:]))
                i += 1
            out[key] = items
            continue
        out[key] = _scalar(rest)
        i += 1
    return out


def _dump_frontmatter(d: dict) -> str:
    """Deterministic frontmatter for a lit file (bootstrap output)."""
    order = ["citekey", "type", "authors", "title", "journal", "volume",
             "number", "pages", "year", "doi", "arxiv", "pdf", "held",
             "status", "routing", "verify_flags", "verified_date", "summary",
             "loci", "section"]
    out = ["---"]
    for k in order:
        if k not in d:
            continue
        v = d[k]
        if isinstance(v, list):
            out.append(f"{k}:")
            for item in v:
                out.append(f"  - {_yaml_scalar(item)}")
            if not v:
                out[-1] = f"{k}: []"
        elif isinstance(v, bool):
            out.append(f"{k}: {'true' if v else 'false'}")
        elif v is None:
            out.append(f"{k}: null")
        elif k == "summary":
            out.append(f"{k}: >")
            for chunk in _wrap(str(v), 74, indent="  "):
                out.append(chunk)
        else:
            out.append(f"{k}: {_yaml_scalar(v)}")
    out.append("---")
    return "\n".join(out)


def _yaml_scalar(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if v is None:
        return "null"
    s = str(v)
    if s == "" or re.search(r"[:#\[\]{}'\"]|^\s|\s$|^[-?&*!|>%@`]", s):
        return "'" + s.replace("'", "''") + "'"
    return s


def _wrap(s: str, width: int, indent: str = "") -> list[str]:
    words = s.split()
    lines, cur = [], indent
    for w in words:
        if cur.strip() and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = indent + w
        else:
            cur = (cur + " " + w) if cur.strip() else (indent + w)
    if cur.strip():
        lines.append(cur)
    return lines or [indent.rstrip()]


# ---------------------------------------------------------------------------
# BibTeX parsing (bootstrap: existing references.bib -> structured entries)
# ---------------------------------------------------------------------------

def parse_bib(text: str) -> list[dict]:
    entries = []
    i, n = 0, len(text)
    while True:
        at = text.find("@", i)
        if at < 0:
            break
        brace = text.find("{", at)
        etype = text[at + 1:brace].strip().lower()
        comma = text.find(",", brace)
        key = text[brace + 1:comma].strip()
        j = comma + 1
        fields = {}
        while j < n:
            while j < n and text[j] in " \n\t\r,":
                j += 1
            if j < n and text[j] == "}":
                j += 1
                break
            eq = text.find("=", j)
            fname = text[j:eq].strip().lower()
            k = eq + 1
            while k < n and text[k] in " \n\t\r":
                k += 1
            if text[k] == "{":
                d, k2 = 1, k + 1
                while k2 < n and d > 0:
                    if text[k2] == "{":
                        d += 1
                    elif text[k2] == "}":
                        d -= 1
                    k2 += 1
                val = text[k + 1:k2 - 1]
                j = k2
            else:  # bare token to next comma/close
                k2 = k
                while k2 < n and text[k2] not in ",}":
                    k2 += 1
                val = text[k:k2].strip()
                j = k2
            fields[fname] = re.sub(r"\s+", " ", val).strip()
        entries.append({"type": etype, "key": key, "fields": fields})
        i = j
    return entries


_PDF_RE = re.compile(r"PDF\\?_papers/[^\s;)]+?\.pdf")
_HELD_NEG = re.compile(r"no pdf held|not (?:yet )?held|paywalled|grab from|"
                       r"pull if needed|pull the", re.I)
# Bookkeeping leads to skip when picking the one-line relevance summary.
_PROV_RE = re.compile(r"^\(?(held\b|published\b|doi\b|page \d|verified\b|"
                      r"read off\b|copy held\b|grabbed\b|downloaded\b|"
                      r"preprint\b|arxiv\b|bibliographic\b)", re.I)


def _note_to_fields(note: str) -> dict:
    """Split a bib note into pdf/held/status/routing/summary/body drafts."""
    pdf = None
    m = _PDF_RE.search(note)
    if m:
        pdf = m.group(0).replace("\\_", "_")
    routing = []
    if re.search(r"\[CITE", note):
        routing.append("CITE")
    if re.search(r"\[FEED", note):
        routing.append("FEED")
    held = bool(pdf) and not _HELD_NEG.search(note)
    if not pdf and not _HELD_NEG.search(note):
        held = False
    status = "VERIFIED" if (held or re.search(r"verified|read in full", note, re.I)) else "REPORTED"
    verify = []
    for vm in re.finditer(r"([A-Za-z/ ]+?)\s*VERIFY(?:\s+at (?:cite|submission))?", note):
        verify.append(vm.group(1).strip().rstrip(".") + " VERIFY at submission")
    # summary = first sentence of the note after removing the pdf token + tags
    body = note
    if m:
        body = (note[:m.start()] + note[m.end():]).strip().lstrip(".; ").strip()
    body = re.sub(r"\[(CITE|FEED)[^\]]*\]\s*", "", body).lstrip(",;: ").strip()
    # first substantial sentence (skip short ID / parenthetical / VERIFY leads)
    first = ""
    for s in re.split(r"(?<=[.;])\s+", body):
        s = s.strip().lstrip("(,;:. ").strip()
        if (len(s.split()) >= 4 and "VERIFY" not in s
                and not _PROV_RE.match(s) and not _HELD_NEG.search(s)):
            first = s.rstrip(";") + ("." if not s.endswith((".", ")")) else "")
            break
    if not first and body:
        first = body.split(".")[0].strip() + "."
    return {"pdf": pdf, "held": held, "status": status,
            "routing": routing, "verify_flags": verify,
            "summary": first, "body": body}


def bootstrap(overwrite=False) -> int:
    LIT_DIR.mkdir(parents=True, exist_ok=True)
    entries = parse_bib(BIB.read_text())
    written = 0
    for e in entries:
        key = e["key"]
        path = LIT_DIR / f"{key}.md"
        if path.exists() and not overwrite:
            continue
        f = e["fields"]
        nf = _note_to_fields(f.get("note", ""))
        authors = [a.strip() for a in re.split(r"\s+and\s+", f.get("author", "")) if a.strip()]
        d = {
            "citekey": key,
            "type": e["type"],
            "authors": authors,
            "title": f.get("title", "").strip(),
            "journal": f.get("journal") or f.get("booktitle") or f.get("howpublished"),
            "volume": f.get("volume"),
            "number": f.get("number"),
            "pages": f.get("pages"),
            "year": f.get("year"),
            "doi": f.get("doi"),
            "arxiv": f.get("eprint"),
            "pdf": nf["pdf"],
            "held": nf["held"],
            "status": nf["status"],
            "routing": nf["routing"],
            "verify_flags": nf["verify_flags"],
            "verified_date": None,
            "summary": nf["summary"] or "TODO one-line relevance",
            "loci": [],
            "section": "unsorted",
        }
        d = {k: v for k, v in d.items() if v is not None or k in
             ("arxiv", "doi", "pdf", "verified_date")}
        body = nf["body"]
        text = _dump_frontmatter(d) + "\n\n# " + key + "\n\n" + body + "\n"
        path.write_text(text)
        written += 1
    return written


# ---------------------------------------------------------------------------
# emit BibTeX + README from the lit files (the ongoing generator direction)
# ---------------------------------------------------------------------------

def load_lit() -> list[dict]:
    out = []
    for p in sorted(LIT_DIR.glob("*.md")):
        fm = _parse_frontmatter(p.read_text())
        out.append(fm)
    return out


def _esc(s: str) -> str:
    return s.replace("_", "\\_")


def _emit_bib_entry(e: dict, lines: list[str]) -> None:
    note_bits = []
    if e.get("pdf"):
        note_bits.append(_esc(e["pdf"]) + ".")
    rt = e.get("routing") or []
    tag = "".join(f"[{r}] " for r in rt)
    note_bits.append(tag + (e.get("summary") or "").strip())
    for vf in (e.get("verify_flags") or []):
        note_bits.append(vf + ".")
    note = " ".join(b for b in note_bits if b).strip()
    f = {
        "author": " and ".join(e.get("authors") or []),
        "title": e.get("title"),
        e_journal_key(e): e.get("journal"),
        "volume": e.get("volume"), "number": e.get("number"),
        "pages": e.get("pages"), "year": e.get("year"),
        "doi": e.get("doi"),
        "eprint": e.get("arxiv"),
        "archivePrefix": "arXiv" if e.get("arxiv") else None,
        "note": note,
    }
    lines.append(f"@{e.get('type','article')}{{{e['citekey']},")
    emitted = []
    for k in BIB_FIELD_ORDER:
        v = f.get(k)
        if v in (None, "", []):
            continue
        emitted.append((k, v))
    for idx, (k, v) in enumerate(emitted):
        comma = "," if idx < len(emitted) - 1 else ""
        wrapped = _wrap(str(v), 74, indent="             ")
        wrapped[0] = f"  {k:<7}= {{{wrapped[0].strip()}"
        wrapped[-1] = wrapped[-1] + "}" + comma
        lines.extend(wrapped)
    lines.append("}")
    lines.append("")


def emit_bib(entries: list[dict]) -> str:
    lines = [
        f"% {len(entries)} entries -- GENERATED by scripts/build_lit_index.py from",
        "% docs/lit/*.md; DO NOT EDIT BY HAND. Prose ledger: docs/LITERATURE.md.",
        "% Grouped by thematic section (mirrors docs/LITERATURE.md).",
        "",
    ]
    groups = _by_section(entries)
    for slug in SECTION_SLUGS:
        grp = groups.get(slug)
        if not grp:
            continue
        lines.append(f"% ===== {SECTION_TITLES[slug]} =====")
        lines.append("")
        for e in sorted(grp, key=lambda x: x["citekey"]):
            _emit_bib_entry(e, lines)
    return "\n".join(lines).rstrip() + "\n"


def e_journal_key(e: dict) -> str:
    return {"inproceedings": "booktitle", "misc": "howpublished"}.get(
        e.get("type", "article"), "journal")


def emit_readme(entries: list[dict]) -> str:
    preamble = (PDF_README.read_text().split("<!-- GENERATED", 1)[0].rstrip()
                if PDF_README.exists() and "<!-- GENERATED" in PDF_README.read_text()
                else "# PDF_papers -- literature holdings index\n\n"
                     "Everything except this README is gitignored (source PDFs are "
                     "possibly copyrighted). This table is GENERATED by "
                     "`scripts/build_lit_index.py` from `docs/lit/*.md` -- do not edit by hand.")
    def _row(e):
        pdf = e.get("pdf") or ""
        fname = Path(pdf).name if pdf else "*(not held)*"
        held = "yes" if e.get("held") else "no"
        rt = ", ".join(e.get("routing") or []) or "—"
        loci = ", ".join(e.get("loci") or []) or "—"
        summ = (e.get("summary") or "").replace("|", "\\|")
        return (f"| `{fname}` | `{e['citekey']}` | {held} | "
                f"{e.get('status','')} | {rt} | {loci} | {summ} |")

    rows = ["<!-- GENERATED by scripts/build_lit_index.py -- do not edit below -->", ""]
    groups = _by_section(entries)
    for slug in SECTION_SLUGS:
        grp = groups.get(slug)
        if not grp:
            continue
        rows += [f"### {SECTION_TITLES[slug]}", "",
                 "| file | citekey | held | status | routing | loci | why it matters |",
                 "|---|---|---|---|---|---|---|"]
        rows += [_row(e) for e in sorted(grp, key=lambda x: x["citekey"])]
        rows.append("")
    return preamble + "\n\n" + "\n".join(rows).rstrip() + "\n"


def emit_public_index(entries: list[dict]) -> str:
    """The tracked literature index: citekey/status/routing/loci/summary only.

    Deliberately NO filename and NO held column: the public page indexes the
    *notes* (docs/lit/), not a shelf of source PDFs. The full holdings table
    (with local filenames) is written to PDF_papers/README.md, which is
    untracked -- publishing a list of held publisher PDFs invites the wrong
    reading of a folder named PDF_papers, even though no PDF is distributed.
    """
    preamble = (
        "# Literature index\n\n"
        "GENERATED by `scripts/build_lit_index.py` from the per-paper notes in "
        "`docs/lit/*.md` -- do not edit by hand. Each citekey links to the "
        "note, which carries the full bibliographic record (also exported to "
        "`docs/references.bib`). Source PDFs are not distributed.")
    def _row(e):
        rt = ", ".join(e.get("routing") or []) or "—"
        loci = ", ".join(e.get("loci") or []) or "—"
        summ = (e.get("summary") or "").replace("|", "\\|")
        return (f"| [`{e['citekey']}`](lit/{e['citekey']}.md) | "
                f"{e.get('status','')} | {rt} | {loci} | {summ} |")
    rows = ["<!-- GENERATED by scripts/build_lit_index.py -- do not edit below -->", ""]
    groups = _by_section(entries)
    for slug in SECTION_SLUGS:
        grp = groups.get(slug)
        if not grp:
            continue
        rows += [f"### {SECTION_TITLES[slug]}", "",
                 "| citekey | status | routing | loci | why it matters |",
                 "|---|---|---|---|---|"]
        rows += [_row(e) for e in sorted(grp, key=lambda x: x["citekey"])]
        rows.append("")
    return preamble + "\n\n" + "\n".join(rows).rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--bootstrap", action="store_true")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    if args.bootstrap:
        n = bootstrap(overwrite=args.overwrite)
        print(f"bootstrap: wrote {n} lit files to {LIT_DIR}")
        return 0

    entries = load_lit()
    bib, readme = emit_bib(entries), emit_readme(entries)
    public = emit_public_index(entries)
    if args.check:
        bad = False
        # gate the TRACKED artifacts; PDF_README is a local convenience
        for path, new in ((BIB, bib), (PUBLIC_INDEX, public)):
            old = path.read_text() if path.exists() else ""
            if old != new:
                bad = True
                print(f"STALE: {path.relative_to(ROOT)} -- re-run scripts/build_lit_index.py")
                sys.stdout.writelines(difflib.unified_diff(
                    old.splitlines(True), new.splitlines(True),
                    str(path), "generated", n=1))
        return 1 if bad else 0

    BIB.write_text(bib)
    PUBLIC_INDEX.write_text(public)
    PDF_README.write_text(readme)  # local holdings table, untracked
    print(f"wrote {BIB.relative_to(ROOT)}, {PUBLIC_INDEX.relative_to(ROOT)} "
          f"and {PDF_README.relative_to(ROOT)} (local) from {len(entries)} lit files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
