"""Guards on images embedded in the documentation.

Every image a doc references must exist in the repo (a broken figure on the
GitHub page is worse than none), every published apparatus photo must be
referenced somewhere (no orphan uploads), and none may carry EXIF metadata
(the sources are phone photographs; publication copies are stripped).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IMG_MD = re.compile(r"!\[[^\]]*\]\(([^)#\s]+)\)")
IMG_HTML = re.compile(r"<img[^>]+src=\"([^\"]+)\"")


def _tracked_docs():
    import subprocess
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return [ROOT / f for f in out]


def _referenced_images():
    refs = {}
    for doc in _tracked_docs():
        text = doc.read_text(encoding="utf-8", errors="replace")
        for m in list(IMG_MD.finditer(text)) + list(IMG_HTML.finditer(text)):
            src = m.group(1)
            if src.startswith("http"):
                continue
            refs.setdefault((doc.parent / src).resolve(), []).append(
                str(doc.relative_to(ROOT)))
    return refs


def test_every_embedded_image_exists():
    missing = [f"{p} (from {', '.join(docs)})"
               for p, docs in _referenced_images().items() if not p.is_file()]
    assert not missing, "docs reference images that do not exist:\n  " + \
        "\n  ".join(missing)


def test_every_apparatus_photo_is_referenced():
    refs = {p for p in _referenced_images()}
    orphans = [p.name for p in (ROOT / "docs" / "apparatus").glob("*.jpg")
               if p.resolve() not in refs]
    assert not orphans, f"published but unreferenced apparatus photos: {orphans}"


def test_apparatus_photos_carry_no_exif():
    from PIL import Image
    dirty = []
    for p in (ROOT / "docs" / "apparatus").glob("*.jpg"):
        exif = Image.open(p).getexif()
        if len(exif) > 0:
            dirty.append(p.name)
    assert not dirty, f"apparatus photos with EXIF metadata: {dirty}"
