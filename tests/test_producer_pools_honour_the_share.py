"""A producer's internal pool honours RB5S6S_WORKERS, the share agreed with the thesis session (2026-09-26).

The share's own sentence reads that a producer run inside a sweep or a verifier caps its internal pool with
RB5S6S_WORKERS, because a pool fixed inside a command honours neither half. It was a sentence, and on the morning it
was agreed `scripts/run_kernel_worlds.py` ran eight processes under a job declared as one, beside the other session's
five, because its pool was `ProcessPoolExecutor(max_workers=8)`.

AN ALLOW-LIST, NOT A DENY-LIST (V7.2's board, the rules seat). The first version refused only literal-like sizes, so a
size read from another environment variable, a random draw, or a helper returning eight -- F563's own shape one call
away from the literal -- all passed. A pool's size is admitted only when it READS THE SHARE: `RB5S6S_WORKERS`,
`workers.n_workers`, or a command-line attribute the launcher's `{pool}` template sets (`a.workers`, `a.pool`),
directly or through one module-level name; or when it is a plain expression of the function's own local names (a
parameter, a variable it set, arithmetic and `min`/`max`/`int`/`len` of them) in a file that has a share path (it
reads the variable or `n_workers`, or defines a `--workers`, `--pool` or `--jobs` argument), since that is how a caller
hands the share down. Everything else is refused.
"""
import ast
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOLS = {"ProcessPoolExecutor", "ThreadPoolExecutor", "Pool"}
#: a pool whose size is what the file tests, with its reason
EXEMPT = {"scripts/_m25_parallel_smoke.py": "a two-worker determinism smoke: the pool's size is what it tests"}
#: the command-line attributes the launcher's {pool} template sets
SHARE_ATTRS = {"workers", "pool", "n_workers", "jobs"}
#: the calls a plain local-name expression may use
PLAIN_CALLS = {"min", "max", "int", "len"}
_SHARE_PATH = re.compile(r"RB5S6S_WORKERS|\bn_workers\b|add_argument\(\s*['\"]--(?:workers|pool|jobs)\b")


def _reads_share(expr, names) -> bool:
    """The size reads the share, directly or through one module-level name."""
    exprs = [expr] + [names[n.id] for n in ast.walk(expr) if isinstance(n, ast.Name) and n.id in names]
    for e in exprs:
        for n in ast.walk(e):
            if isinstance(n, ast.Constant) and n.value == "RB5S6S_WORKERS":
                return True
            if isinstance(n, ast.Attribute) and n.attr in SHARE_ATTRS:
                return True
            if isinstance(n, ast.Name) and n.id == "n_workers":
                return True
    return False


def _plain_local(expr, names) -> bool:
    """Built only from the function's own local names, literals, arithmetic and min/max/int/len, with at least one
    local name: a size a caller can have handed down. A module-level name or any other call is not plain."""
    local = False
    for n in ast.walk(expr):
        if isinstance(n, ast.Call):
            f = n.func
            if not (isinstance(f, ast.Name) and f.id in PLAIN_CALLS):
                return False
        elif isinstance(n, ast.Name):
            if n.id in names:
                return False
            if n.id not in PLAIN_CALLS:
                local = True
        elif isinstance(n, ast.Attribute):
            return False
    return local


def _literal_only(expr) -> bool:
    """Built only from literals and os.cpu_count(): a size that no caller and no variable can move."""
    for n in ast.walk(expr):
        if isinstance(n, ast.Name) and n.id not in PLAIN_CALLS and n.id != "os":
            return False
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name not in PLAIN_CALLS and name != "cpu_count":
                return False
    return True


def _fixed_in_scope(size, func) -> bool:
    """A local name the enclosing function itself assigns from literals alone (V7.2's board, the twin seat: a
    `workers = 8` one line above the pool passed as a name handed down)."""
    if func is None:
        return False
    locals_ = {n.id for n in ast.walk(size) if isinstance(n, ast.Name) and n.id not in PLAIN_CALLS}
    for n in ast.walk(func):
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in locals_ for t in n.targets):
            if _literal_only(n.value) and not _reads_share(n.value, {}):
                return True
    return False


def fixed_pools(sources: dict) -> list:
    """Every pool construction in `sources` ({path: text}) whose size does not read the share."""
    bad = []
    for rel, text in sorted(sources.items()):
        if rel in EXEMPT:
            continue
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        names = {t.id: n.value for n in tree.body if isinstance(n, ast.Assign)
                 for t in n.targets if isinstance(t, ast.Name)}
        path = bool(_SHARE_PATH.search(text))
        owner = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for c in ast.walk(fn):
                    owner.setdefault(id(c), fn) if c is not fn else None
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name not in POOLS:
                continue
            size = next((k.value for k in n.keywords if k.arg in ("max_workers", "processes")),
                        n.args[0] if n.args else None)
            ok = size is not None and (_reads_share(size, names) or (
                path and _plain_local(size, names) and not _fixed_in_scope(size, owner.get(id(n)))))
            if not ok:
                bad.append(f"{rel}:{n.lineno} {name}({ast.unparse(size) if size is not None else ''})")
    return bad


def test_the_scan_is_planted_both_ways():
    fixed = {
        "scripts/a.py": "from concurrent.futures import ProcessPoolExecutor\nProcessPoolExecutor(max_workers=8)\n",
        "scripts/b.py": "import os\nWORKERS = min(8, os.cpu_count() or 1)\nProcessPoolExecutor(WORKERS)\n",
        "scripts/c.py": "import multiprocessing as mp\nmp.get_context('spawn').Pool()\n",
        # the rules seat's three: another variable, a random draw, and F563's literal one call away
        "scripts/d.py": "import os\nProcessPoolExecutor(int(os.environ.get('TOTALLY_UNRELATED_VAR', '8')))\n",
        "scripts/e.py": "import random\nProcessPoolExecutor(random.randint(1, 8))\n",
        "scripts/f.py": "def guess():\n    return 8\nProcessPoolExecutor(guess())\n",
        # a local name in a file with no share path is not handed down from anywhere
        "scripts/g.py": "def run(workers):\n    ProcessPoolExecutor(workers)\n",
        # the twin seat's: a literal one line above the pool, in a file that reads the share elsewhere
        "scripts/m.py": "import os\nW = os.environ.get('RB5S6S_WORKERS')\ndef f():\n    workers = 8\n"
                         "    ProcessPoolExecutor(max_workers=workers)\n",
    }
    honoured = {
        "scripts/h.py": "import os\nProcessPoolExecutor(max(1, min(8, int(os.environ.get('RB5S6S_WORKERS', '8')))))\n",
        "scripts/i.py": "from rb5s6s.workers import n_workers\nnw = n_workers()\nPool(min(nw, 4))\n",
        "scripts/j.py": "def main(a):\n    ProcessPoolExecutor(a.workers)\n",
        "scripts/k.py": "import os\nW = int(os.environ.get('RB5S6S_WORKERS', '5'))\ndef f(t):\n    ProcessPoolExecutor(min(W, len(t)))\n",
        "scripts/l.py": "ap.add_argument('--workers', type=int)\ndef run(jobs, workers):\n    ProcessPoolExecutor(workers)\n",
        "scripts/_m25_parallel_smoke.py": "Pool(2)\n",
    }
    got = fixed_pools({**fixed, **honoured})
    assert [g.split(":")[0] for g in got] == sorted(fixed), got


def test_no_producer_fixes_its_pool_inside_itself():
    files = subprocess.run(["git", "ls-files", "scripts/*.py", "examples/*.py", "rb5s6s/*.py"], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split()
    sources = {rel: (ROOT / rel).read_text(encoding="utf-8", errors="ignore") for rel in files
               if (ROOT / rel).exists()}
    assert len(sources) > 50, len(sources)
    bad = fixed_pools(sources)
    assert not bad, ("a producer's pool size does not read the share with the thesis session; read RB5S6S_WORKERS "
                     "(or take the size from the command line):\n  " + "\n  ".join(bad))
