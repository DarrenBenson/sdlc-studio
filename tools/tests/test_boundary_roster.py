"""BG0641 AC6 and AC7: every boundary AGENTS.md names has a hook invocation behind it.

Run from the repo root:
    python3 -m unittest discover -s tools/tests
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS_MD = REPO / "AGENTS.md"          # bound to a name so the gate's static relevance scan sees it
HOOKS_DIR = REPO / ".githooks"
SCRIPT = REPO / "tools" / "boundary_roster.py"


def _load():
    spec = importlib.util.spec_from_file_location("boundary_roster", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["boundary_roster"] = mod
    spec.loader.exec_module(mod)
    return mod


br = _load()

ROSTER = ("# Fixture\n\nOne lane binds at the **push and release boundaries only** "
          "(`gate.py --boundary push|release`).\n")


class BoundaryRosterTests(unittest.TestCase):

    def test_every_boundary_agents_md_names_has_a_gate_invocation_behind_it(self) -> None:
        """AC6, over THIS tree. MUTANTS: (1) remove `--boundary` from both gate invocations in
        `.githooks/pre-push`; (2) parse only `--boundary (\\w+)` so the `release` half of
        `push|release` is never read - the checker still exits 0 with one boundary, so BOTH are
        asserted as read; (3) recognise only the `--boundary` spelling, so the env-spelled
        fixture hook (below) binds nothing; (4) drop the `gate.py` anchor from the flag pattern, so
        any line carrying `--boundary` binds."""
        read, bound, missing = br.check(AGENTS_MD, HOOKS_DIR)
        self.assertEqual({"push", "release"}, read, f"the roster read {read}")
        self.assertEqual([], missing, missing)
        self.assertTrue({"push", "release"} <= bound, bound)
        import subprocess  # noqa: PLC0415
        r = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=REPO)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("read push, release", r.stdout)
        # the env spelling the gate accepts binds too
        with tempfile.TemporaryDirectory() as d:
            hooks = Path(d) / "hooks"; hooks.mkdir()
            (hooks / "pre-push").write_text("#!/usr/bin/env bash\nSDLC_GATE_BOUNDARY=release python3 x/gate.py\n"
                                            "python3 x/gate.py --boundary push\n"
                                            "echo --boundary deploy\n")      # no gate.py on the line: binds nothing
            self.assertEqual({"push", "release"}, br.bound_boundaries(hooks))

    def test_a_boundary_with_nothing_behind_it_is_refused(self) -> None:
        """AC7. MUTANTS: (1) return an empty list of missing boundaries unconditionally;
        (2) hard-code the boundary list `(push, release)` instead of reading the roster, so
        `deploy` is never demanded; (3) read comment lines as invocations; (4) treat a roster
        that parsed to nothing as satisfied."""
        import subprocess  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            agents = root / "AGENTS.md"
            agents.write_text(ROSTER.replace("push|release", "push|release|deploy"))
            hooks = root / "hooks"; hooks.mkdir()
            (hooks / "pre-push").write_text("#!/usr/bin/env bash\npython3 x/gate.py --boundary push\n"
                                            "python3 x/gate.py --boundary release\n")
            r = subprocess.run([sys.executable, str(SCRIPT), "--agents", str(agents), "--hooks", str(hooks)],
                               capture_output=True, text=True)
            self.assertEqual(1, r.returncode, r.stdout + r.stderr)
            self.assertIn("`deploy`", r.stderr)
            # a comment-only mention is NOT an invocation
            (hooks / "pre-push").write_text("#!/usr/bin/env bash\n# python3 x/gate.py --boundary deploy\n"
                                            "python3 x/gate.py --boundary push\npython3 x/gate.py --boundary release\n")
            r = subprocess.run([sys.executable, str(SCRIPT), "--agents", str(agents), "--hooks", str(hooks)],
                               capture_output=True, text=True)
            self.assertEqual(1, r.returncode, "a boundary named only in a comment satisfied the roster")
            self.assertIn("`deploy`", r.stderr)
            # a roster that parses to nothing is refused as unreadable, never passed as empty
            agents.write_text("# Fixture\n\nNo boundaries here.\n")
            r = subprocess.run([sys.executable, str(SCRIPT), "--agents", str(agents), "--hooks", str(hooks)],
                               capture_output=True, text=True)
            self.assertEqual(1, r.returncode, "an empty roster passed")
            self.assertIn("names no boundary", r.stderr)


if __name__ == "__main__":
    unittest.main()
