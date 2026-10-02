"""US0982: the lane brief tells a repair to carry only its blocking fix and the pins that kill it.

A repair answering a REJECT kept breaking what the first build got right (LC-005), because
nothing the builder reads said a repair is bounded. The ruling was already made; the brief now
states it in one line among the lane's obligations, and adds no flag, refusal or gate.

Driven through `sprint.py lane brief`, the shipped entry point, in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))


def _live(name: str):
    """The module the command resolves at call time (see `test_lean_close._live`)."""
    return sys.modules.get(name) or importlib.import_module(name)


def _obligations(text: str) -> list[str]:
    """The lines of the brief's "Obligations on this lane" list."""
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines) if ln.startswith("Obligations on this lane"))
    rows = []
    for ln in lines[start + 1:]:
        if not ln.startswith("  - "):
            break
        rows.append(ln[4:])
    return rows


class LaneBriefRepairScopeTests(unittest.TestCase):
    def test_the_brief_names_the_repair_scope(self) -> None:
        """AC1. MUTANT: HEAD, whose obligations name no repair scope; or a line that bounds the
        repair but drops the filing of the non-blocking findings. The control: the existing
        obligations stay, and the brief still exits 0 with no new flag."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            stories = root / "sdlc-studio" / "stories"
            stories.mkdir(parents=True)
            (stories / "US0101-x.md").write_text(
                "# US0101: x\n\n> **Status:** Ready\n> **Points:** 1\n> **Affects:** src/a.py\n\n"
                "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/a.py\n",
                encoding="utf-8")
            _live("lib.run_state").open_run(root, batch=["US0101"], goal="g")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                rc = _live("sprint").main(["lane", "brief", "--units", "US0101",
                                           "--root", str(root)])
            self.assertEqual(0, rc, out.getvalue())
            rows = _obligations(out.getvalue())
            scope = [r for r in rows if "repair answering a REJECT" in r]
            self.assertEqual(1, len(scope), rows)
            self.assertIn("only the blocking findings", scope[0])
            self.assertIn("pins that kill them", scope[0])
            self.assertIn("files the rest", scope[0])
            self.assertTrue(any(r.startswith("Refuse a unit that carries no authored") for r in rows),
                            rows)
            self.assertEqual(4, len(rows), rows)


if __name__ == "__main__":
    unittest.main()
