"""The deep configuration of the moment-power map, as its own producer so the
freshness check can name it: the archive's noise level, the deepest scope,
the shift resolved, a ladder that starts at the archive's rung, forty
thousand traces a rung. It sets the environment the map reads and hands over.

    RB5S6S_WORKERS=6 python scripts/run_moment_power_map_deep.py
"""
import os
import runpy
import sys
from pathlib import Path



def main() -> None:
    # SET, never setdefault: an inherited RB5S6S_MPM_TRACES would silently make
    # a different file, and the freshness check runs this with whatever the
    # parent environment carries. The plant and the timing forms take the
    # main producer directly.
    os.environ["RB5S6S_MPM_DEEP"] = "1"
    os.environ["RB5S6S_MPM_TRACES"] = "40000"
    sys.argv = [str(Path(__file__).resolve().parent / "run_moment_power_map.py")] + sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")


if __name__ == "__main__":
    # guarded, so an import (a checker, a subagent, a read-only pass) does not
    # launch a ninety-minute grid into results/
    main()
