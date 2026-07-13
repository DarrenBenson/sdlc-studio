"""Every report/check verb that gained `--format json` must emit valid, parseable JSON.

Guards CR0208 AC8: a machine caller can read these verbs the same way. Each verb is run
against a throwaway root with stdout captured; the captured text must `json.loads` and the
exit code must be an int (the verb's own semantics, not asserted here).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# (module, module file, argv template - {root} filled per test)
VERBS = [
    ("spec_guard", "spec_guard.py", ["check", "--changed", "x.py", "--format", "json"]),
    ("plan_review", "plan_review.py", ["check", "--id", "US9999", "--format", "json"]),
    ("ledger", "ledger.py", ["show", "--unit", "CR9999", "--format", "json"]),
    ("critic", "critic.py", ["show", "--format", "json"]),
    ("doc_freshness", "doc_freshness.py", ["--format", "json"]),
    ("persona_resolve", "persona_resolve.py", ["resolve", "--seat", "product", "--format", "json"]),
    ("loop_guard", "loop_guard.py",
     ["record", "--unit", "US1", "--signature", "t::x", "--format", "json"]),
    ("handoff", "handoff.py", ["show", "--ids", "US9999", "--format", "json"]),
]


class JsonReportParity(unittest.TestCase):
    def test_each_verb_emits_valid_json(self) -> None:
        for name, rel, argv in VERBS:
            with self.subTest(verb=name):
                mod = _load(name, rel)
                with tempfile.TemporaryDirectory() as d:
                    buf = io.StringIO()
                    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                        rc = mod.main(argv + ["--root", d])
                    self.assertIsInstance(rc, int, name)
                    payload = buf.getvalue().strip()
                    self.assertTrue(payload, f"{name} printed nothing on --format json")
                    json.loads(payload)  # raises -> test fails with the offending verb named


if __name__ == "__main__":
    unittest.main()
