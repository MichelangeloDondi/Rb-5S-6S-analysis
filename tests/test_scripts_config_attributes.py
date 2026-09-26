"""Every attribute a script reads off `rb5s6s.config` exists there.

`scripts/run_campaign_conditions.py` read `config.LAMBDA_LASER_M` after 1d0e2617 moved the wavelength to
`rb5s6s.constants`, and failed at runtime for two days: it writes no table, so neither the freshness check nor the code
ledger ever ran it (V7.3's chain found it, F573). A constant that moves homes is not a value that moves, so no SSOT
guard sees it either. This reads every script and example that imports the config module as `C` and asserts each
`C.<NAME>` it names is still an attribute there, which is the whole class and costs a second.
"""
import ast
import re
from pathlib import Path

from rb5s6s import config

ROOT = Path(__file__).resolve().parents[1]
_ALIAS = re.compile(r"^\s*from rb5s6s import config as (\w+)\b|^\s*import rb5s6s\.config as (\w+)\b", re.M)


def missing_config_reads(files):
    """(file, name) for every `<alias>.<NAME>` a file reads off the config module that the module does not define."""
    out = []
    for f in files:
        src = f.read_text(encoding="utf-8")
        aliases = {a or b for a, b in _ALIAS.findall(src)}
        if not aliases:
            continue
        for node in ast.walk(ast.parse(src)):
            if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id in aliases
                    and not hasattr(config, node.attr)):
                out.append((f.name, node.attr))
    return sorted(set(out))


def test_every_config_attribute_a_script_reads_exists():
    files = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "examples").glob("*.py"))
    assert missing_config_reads(files) == []


def test_the_moved_wavelength_is_caught(tmp_path):
    """The instance: a script reading the wavelength off config, where 1d0e2617 no longer defines it."""
    f = tmp_path / "run_x.py"
    f.write_text("from rb5s6s import config as C\nz = C.W0_CENTRAL_M / C.LAMBDA_LASER_M\n", encoding="utf-8")
    assert missing_config_reads([f]) == [("run_x.py", "LAMBDA_LASER_M")]
    f.write_text("from rb5s6s import config as C\nz = C.W0_CENTRAL_M\n", encoding="utf-8")
    assert missing_config_reads([f]) == []
