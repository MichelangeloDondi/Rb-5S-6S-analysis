"""The twin term census reads the exhibit's switched layers from its SOURCE, and the reader fails closed.

V7.2 moved `examples/campaign_twin.py`'s `layers = {...}` from `main` to a module-level `LAYERS = {...}` when its worlds
were pooled; the census's pattern matched nothing and returned an empty set, so every layer the exhibit switches read
`no` in `results/twin_term_census.csv`, and only the freshness check's pooled re-run saw it. Both spellings are read and
a source with neither refuses.
"""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _census(monkeypatch, tmp_path, example_src=None):
    spec = importlib.util.spec_from_file_location("census_reader_plant", ROOT / "scripts" / "make_twin_term_census.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if example_src is not None:
        (tmp_path / "examples").mkdir()
        (tmp_path / "examples" / "campaign_twin.py").write_text(example_src, encoding="utf-8")
        monkeypatch.setattr(mod, "ROOT", tmp_path)
    return mod


def test_the_module_level_spelling_is_read(monkeypatch, tmp_path):
    mod = _census(monkeypatch, tmp_path, 'LAYERS = {"cascade": True, "stark": False}\n')
    assert mod._example_layers() == {"cascade", "stark"}


def test_the_old_spelling_is_still_read(monkeypatch, tmp_path):
    mod = _census(monkeypatch, tmp_path, 'def main():\n    layers = {"bbr": True}\n')
    assert mod._example_layers() == {"bbr"}


def test_a_source_with_neither_refuses_instead_of_reading_empty(monkeypatch, tmp_path):
    mod = _census(monkeypatch, tmp_path, "def main():\n    return None\n")
    with pytest.raises(SystemExit, match="defines no `layers` or `LAYERS`"):
        mod._example_layers()


def test_the_exhibit_itself_switches_the_layers_the_census_reports(monkeypatch, tmp_path):
    mod = _census(monkeypatch, tmp_path)
    assert {"cascade", "saturation", "stark", "bbr"} <= mod._example_layers()
