"""
Runs the test_* functions of tests/test_project.py without needing pytest installed.
It executes the same test functions pytest would collect, with the same pass/fail semantics.
If pytest is installed, simply run `pytest tests/` instead.
"""
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tests"))

import test_project as tp

results = []
test_fns = [(name, fn) for name, fn in vars(tp).items() if name.startswith("test_") and callable(fn)]

for name, fn in test_fns:
    try:
        fn()
        results.append((name, "PASS", None))
    except AssertionError as e:
        results.append((name, "FAIL", str(e)))
    except Exception as e:
        results.append((name, "ERROR", f"{type(e).__name__}: {e}\n{traceback.format_exc(limit=2)}"))

n_pass = sum(1 for _, s, _ in results if s == "PASS")
n_fail = sum(1 for _, s, _ in results if s == "FAIL")
n_err = sum(1 for _, s, _ in results if s == "ERROR")

print(f"{'='*60}\nCollected {len(results)} tests\n{'='*60}")
for name, status, msg in results:
    mark = {"PASS": "PASSED", "FAIL": "FAILED", "ERROR": "ERROR "}[status]
    print(f"{mark}  {name}")
    if status != "PASS":
        print(f"        {msg}")
print(f"{'='*60}\n{n_pass} passed, {n_fail} failed, {n_err} errors out of {len(results)}\n{'='*60}")

sys.exit(0 if (n_fail == 0 and n_err == 0) else 1)
