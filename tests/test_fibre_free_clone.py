"""The published analysis must import and run with the fibre layer deleted.

WHY THIS IS A DIFFERENT TEST FROM THE IMPORT-BOUNDARY GUARD.
tests/test_module_boundaries.py reads the source and asserts that no core
module NAMES the prospective layer. That is a static check and it can be
satisfied while a runtime path still reaches the layer -- a deferred import
inside a function, an entry in a registry, a getattr by string. This test
answers the question the static one cannot: delete the file and see whether
the archive still stands up.

WHY IT MATTERS FOR A RELEASE. The fibre layer models an apparatus that does
not exist. If the published analysis silently depended on it, a reader
reproducing the archive would be reproducing a dependency on unbuilt hardware,
and the failure would surface only for them.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LEAF_FILES = ("fibre.py",)


@pytest.mark.slow
def test_the_record_imports_without_the_fibre_layer():
    present = [f for f in LEAF_FILES if (ROOT / "rb5s6s" / f).exists()]
    if not present:
        pytest.skip("no fibre layer present; nothing to delete")

    with tempfile.TemporaryDirectory() as td:
        clone = Path(td) / "clone"
        shutil.copytree(ROOT / "rb5s6s", clone / "rb5s6s")
        for f in present:
            (clone / "rb5s6s" / f).unlink()

        # Import the package and exercise the core lineshape path, which is
        # what every committed result is built on.
        # THE EDITABLE INSTALL MASKS THE DELETION, AND THAT IS THE WHOLE
        # REASON THIS TEST NEEDED DEBUGGING. This checkout is installed with a
        # setuptools editable finder (__editable___rb5s6s_*_finder), which
        # registers a MetaPathFinder. sys.meta_path is consulted BEFORE
        # sys.path, so `import rb5s6s.fibre` resolved to the real repository
        # even with the clone first on the path and the file deleted from it.
        # A reader reproducing from a fresh clone has no such finder, so
        # removing it is what makes the subprocess resemble their machine
        # rather than this one.
        code = (
            "import sys\n"
            # The finder is registered as a CLASS, not an instance, so its
            # defining module is on f.__module__ while type(f).__module__ is
            # just 'builtins'. Checking the wrong one silently matches nothing
            # and the guard passes for the wrong reason.
            "sys.meta_path = [f for f in sys.meta_path\n"
            "                 if '__editable__' not in (\n"
            "                     getattr(f, '__module__', '') or '')\n"
            "                 and '__editable__' not in (\n"
            "                     getattr(type(f), '__module__', '') or '')]\n"
            # Drop only path entries that would supply a DIFFERENT rb5s6s.
            # Filtering on the repository name instead removes the virtualenv's
            # site-packages too, because .venv lives inside the checkout, and
            # the subprocess then fails on numpy rather than on the thing under
            # test.
            "import os\n"
            "sys.path = [p for p in sys.path\n"
            "            if not os.path.isdir(os.path.join(p, 'rb5s6s'))]\n"
            "sys.path.insert(0, %r)\n"
            "import rb5s6s\n"
            "assert %r in rb5s6s.__file__, rb5s6s.__file__\n"
            "from rb5s6s.lineshape import composite_profile\n"
            "import numpy as np\n"
            "g, p = composite_profile(0.02, 0.30, 0.45)\n"
            "assert np.isfinite(p).all() and p.max() > 0\n"
            "import importlib\n"
            "try:\n"
            "    importlib.import_module('rb5s6s.fibre')\n"
            "except ModuleNotFoundError:\n"
            "    pass\n"
            "else:\n"
            "    raise SystemExit('the fibre layer was still importable')\n"
            "print('ok')\n" % (str(clone), str(clone))
        )
        r = subprocess.run([sys.executable, "-c", code],
                           capture_output=True, text=True)
        assert r.returncode == 0, (
            "the archive does not stand up without the fibre layer:\n"
            f"stdout: {r.stdout}\nstderr: {r.stderr}")
        assert "ok" in r.stdout
