"""US0913: a repair closes without a reviewed repair plan.

The repair-plan gate (`repair_plan.py`, `review.repair_plan_gate`) is deleted with its config
keys, its critic kind and its tests. A REJECT now costs one fix and one re-review.

AC1 drives `critic.py record` and `transition.py set` through their shipped entry points over a
throwaway workspace. AC2 and AC3 read the shipped scripts tree. AC4 and AC5 read this
repository's generated surface and its stamped criteria, because their criteria are about them.
"""
from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
import workspace  # noqa: E402
import test_lean_no_two_role as stamps  # noqa: E402 - `shipped_source`, the shared reader scan

REPO = workspace.REPO

#: The bug under repair: one manual criterion stamped green, so the AC-verify gate passes and,
#: with no cutoff set, nothing but a repair-plan gate could hold it at Fixed.
BUG = ("# BG0001: the parser drops a field\n\n> **Status:** In Progress\n> **Severity:** Medium\n"
       "> **Verification depth:** functional\n\n## Summary\n\nx\n\n## Steps to Reproduce\n\n"
       "1. x\n\n## Proposed Fix\n\ny\n\n## Acceptance Criteria\n\n"
       "### AC1: the field survives\n- **Verify:** manual a human re-ran the parse\n"
       "- **Verified:** yes (2026-09-25)\n")

#: The retired config keys, as dotted names and as the leaf a YAML block carries.
RETIRED_KEYS = ("review.repair_plan_gate", "review.repair_design_threshold")

#: The CLI verbs the deleted module offered.
RETIRED_VERBS = ("brief", "record", "review", "gate")

#: The test nodes this story deletes, by the selector text a `Verify:` line names them with.
DELETED_NODES = ("tests/test_repair_plan.py::", "tests/test_critic.py::RepairProvenanceTests::")

#: The criteria that named a deleted node, by artefact, and how many each carried.
RETIRED = {"BG0267": 2, "BG0673": 7, "BG0678": 6, "US0311": 3, "US0312": 4, "US0313": 3,
           "US0314": 2, "US0315": 3, "US0343": 4, "US0344": 2}

#: The D0259 pattern, naming this story as the retirer.
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0913: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0913\b")


def _run(root: Path, script: str, *argv: str) -> tuple[int, str]:
    p = subprocess.run([sys.executable, str(SCRIPTS / script), *argv, "--root", str(root)],
                       capture_output=True, text=True, timeout=300)
    return p.returncode, p.stdout + p.stderr


def _shipped_scripts() -> list[Path]:
    """Every Python file the skill ships, tests excluded: a test names a key to assert its
    absence, which is not a read."""
    return sorted(p for p in SCRIPTS.rglob("*.py")
                  if "tests" not in p.relative_to(SCRIPTS).parts
                  and "__pycache__" not in p.parts)


def _imports_repair_plan(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(a.name == "repair_plan" for a in node.names):
            return True
        if isinstance(node, ast.ImportFrom) and node.module == "repair_plan":
            return True
        # a deferred load by name: importlib.import_module("repair_plan"), load_script(...)
        if isinstance(node, ast.Constant) and node.value in ("repair_plan", "repair_plan.py"):
            return True
    return False


class RepairPlanGoneTests(unittest.TestCase):

    def test_a_repair_without_a_plan_reaches_fixed(self) -> None:
        """AC1. MUTANT: keep transition.py asking a repair-plan gate at Fixed; the bug is then
        refused for want of a plan although its criteria are green and its reviewer approved."""
        root = Path(tempfile.mkdtemp(prefix="us0913_"))
        self.addCleanup(shutil.rmtree, root, True)
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True)
        (root / "sdlc-studio" / ".local").mkdir()
        bug = bugs / "BG0001-the-parser-drops-a-field.md"
        bug.write_text(BUG, encoding="utf-8")
        # a project that turned the old gate on: the key must now be inert
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "review:\n  repair_plan_gate: on\n", encoding="utf-8")
        for verdict, issues in (("REJECT", "[new] the field is still dropped on a blank line"),
                                ("APPROVE", "-")):
            rc, out = _run(root, "critic.py", "record", "--unit", "BG0001",
                           "--verdict", verdict, "--issues", issues,
                           "--reviewer", "qa-seat", "--author", "builder",
                           "--brief", "0123456789ab")
            self.assertEqual(0, rc, out)
        self.assertFalse((root / "sdlc-studio" / ".local" / "repair-plans").exists())
        rc, out = _run(root, "transition.py", "set", "BG0001", "Fixed")
        self.assertEqual(0, rc, "a repair with no plan was refused at Fixed:\n" + out)
        self.assertRegex(bug.read_text(encoding="utf-8"), r"\*\*Status:\*\*\s*Fixed")
        self.assertNotIn("repair_plan", out)

    def test_nothing_imports_repair_plan(self) -> None:
        """AC2. MUTANTS: delete the module but keep a caller importing it; keep
        `critic.REPAIR_PLAN_KIND` or the `repair-plan` kind in the plan-review vocabulary."""
        self.assertFalse((SCRIPTS / "repair_plan.py").exists(), "repair_plan.py still ships")
        importers = [p.relative_to(SCRIPTS).as_posix() for p in _shipped_scripts()
                     if _imports_repair_plan(ast.parse(p.read_text(encoding="utf-8")))]
        self.assertEqual([], importers, "a shipped script still imports repair_plan")
        critic_src = (SCRIPTS / "critic.py").read_text(encoding="utf-8")
        names = {t.id for node in ast.walk(ast.parse(critic_src))
                 if isinstance(node, (ast.Assign, ast.AnnAssign))
                 for t in (node.targets if isinstance(node, ast.Assign) else [node.target])
                 if isinstance(t, ast.Name)}
        self.assertNotIn("REPAIR_PLAN_KIND", names)
        self.assertNotIn("REPAIR_PLAN_KIND", critic_src)
        self.assertNotIn("repair_plan", critic_src, "critic.py still points at repair_plan.py")
        kinds = re.search(r"^PLAN_REVIEW_KINDS\s*=\s*(.+)$", critic_src, re.M)
        if kinds:
            self.assertNotIn("repair", kinds.group(1), "a repair-plan kind is still accepted")

    def test_no_repair_plan_keys_are_read(self) -> None:
        """AC3. MUTANTS: leave either key in config-defaults.yaml; keep a script reading one."""
        defaults = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        for key in RETIRED_KEYS:
            leaf = key.split(".")[-1]
            self.assertIsNone(re.search(rf"^\s*{leaf}\s*:", defaults, re.M),
                              f"config-defaults.yaml still declares {key}")
            readers = [p.relative_to(SCRIPTS).as_posix() for p in _shipped_scripts()
                       if leaf in stamps.shipped_source(p)]
            self.assertEqual([], readers, f"a shipped script still reads {key}")

    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC4. MUTANTS: leave the retired rows in the surface; leave the surface stale."""
        surface = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        named = [v for v in RETIRED_VERBS if f"`repair_plan.py {v}`" in surface]
        self.assertEqual([], named, "the surface still names a retired verb")
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        rc, out = _run(REPO, "docgen.py", "surface", "--check")
        self.assertEqual(0, rc, out)
        self.assertIn("docgen surface: 0 drift item(s)", out)

    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC5. MUTANTS: leave a stamped criterion naming a deleted node; retire one without
        its `Verified:` stamp; name another story as the retirer; keep a deleted node."""
        self.assertFalse((HERE / "test_repair_plan.py").exists(), "test_repair_plan.py remains")
        self.assertNotIn("class RepairProvenanceTests",
                         (HERE / "test_critic.py").read_text(encoding="utf-8"))
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        live, retired = [], {}
        for path in sorted((REPO / "sdlc-studio").rglob("*.md")):
            lines = path.read_text(encoding="utf-8").splitlines()
            unit = path.name.split("-")[0]
            for i, line in enumerate(lines):
                stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                if ("**Verify:**" in line and re.search(r"Verified:\*\*\s*yes", stamp)
                        and any(n in line for n in DELETED_NODES)):
                    live.append(f"{path.relative_to(REPO)}:{i + 1}")
                if RETIRED_VERIFY.search(line):
                    self.assertRegex(stamp, RETIRED_STAMP,
                                     f"{path.name}:{i + 1} is retired without its stamp")
                    retired[unit] = retired.get(unit, 0) + 1
        self.assertEqual([], live, "a stamped criterion still names a deleted test node")
        self.assertEqual(RETIRED, retired)


if __name__ == "__main__":
    unittest.main()
