"""US0910: `Verification depth` is no longer derived, and the gate runs no depth lane.

`verify_ac.py depth` and `depth-check` are retired, refused by name, and the standard gate's
`derived-depth` lane is gone. AC1 to AC3 drive the shipped entry points (`verify_ac.py`,
`gate.py`, `docgen.py`) as subprocesses; AC2's fixture is a throwaway workspace. AC3 and AC4 read
this repository, because their criteria name its surface table and its stamped criteria.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import workspace  # noqa: E402
import gate  # noqa: E402
import verify_ac  # noqa: E402

REPO = workspace.REPO

#: A story whose derived half carries a seal its contents do not match: the hand-edit the
#: retired lane refused.
_STORY = """# US0001: fixture

> **Status:** Draft
> **Epic:** [EP0001: fixture](../epics/EP0001-fixture.md)
> **Verification depth:** functional [[derived: criteria 1; killed 9 | fp 0123456789ab ]] (judgement)

## Acceptance Criteria

### AC1: works

- **Verify:** shell true
"""

#: The criteria whose stamped selectors named the deleted DerivedDepthTests and
#: DerivedDepthLaneTests nodes.
_RETIRED = {"US0675": ("AC1", "AC2", "AC3", "AC4", "AC5"),
            "US0676": ("AC1", "AC2", "AC3", "AC4", "AC5", "AC6", "AC7", "AC8", "AC9")}

#: The test modules this story edits. Every stamped selector naming one must still select a node.
_EDITED = (".claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py",
           ".claude/skills/sdlc-studio/scripts/tests/test_gate.py",
           ".claude/skills/sdlc-studio/scripts/tests/test_transition.py")


def _run(script: str, *argv: str, root: Path, cwd: Path | None = None):
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, timeout=300, cwd=cwd)


class DepthGoneTests(unittest.TestCase):

    def test_the_depth_verbs_are_retired(self) -> None:
        """AC1. MUTANT: delete the two parsers outright - argparse then exits 2 with a bare
        `invalid choice` usage error that says nothing about retirement or the evidence."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for argv in (("depth", "--unit", "US0001", "--write"), ("depth-check",)):
                with self.subTest(verb=argv[0]):
                    r = _run("verify_ac.py", *argv, root=root)
                    self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                    self.assertIn(f"verify_ac.py {argv[0]}` is retired", r.stderr)
                    self.assertIn("Verify selectors are its evidence", r.stderr)
                    self.assertNotIn("invalid choice", r.stderr)
            self.assertEqual([], list(root.iterdir()), "a retired verb wrote something")
        helptext = subprocess.run([sys.executable, "-B", str(SCRIPTS / "verify_ac.py"), "--help"],
                                  capture_output=True, text=True, check=True, timeout=60).stdout
        self.assertIn("revert-check", helptext, "the help did not list the live verbs")
        self.assertNotIn("depth", helptext)

    def test_the_gate_runs_no_derived_depth_lane(self) -> None:
        """AC2. MUTANT: keep `derived-depth` in `BLOCKING_ON_ERROR` after dropping it from
        `DEFAULT_CHECKS`; and HEAD, where the lane refuses the hand-edited span."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            ws = root / "sdlc-studio"
            (ws / "stories").mkdir(parents=True)
            (ws / "epics").mkdir()
            (ws / "stories" / "US0001-fixture.md").write_text(_STORY, encoding="utf-8")
            (ws / "epics" / "EP0001-fixture.md").write_text(
                "# EP0001: fixture\n\n> **Status:** Draft\n", encoding="utf-8")
            applied = _run("reconcile.py", "apply", root=root)
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            r = _run("gate.py", root=root)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)
            self.assertIn("gate: PASS", out)
            self.assertNotIn("derived-depth", out)
            self.assertIn("[[derived: criteria 1; killed 9",
                          (ws / "stories" / "US0001-fixture.md").read_text(encoding="utf-8"))
        self.assertNotIn("derived-depth", gate.DEFAULT_CHECKS)
        self.assertNotIn("derived-depth", gate.BLOCKING_ON_ERROR)

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_the_surface_names_no_retired_verb(self) -> None:
        """AC3. MUTANT: retire the verbs without rerunning `docgen.py surface`, so the table
        still lists them and `--check` reports drift."""
        text = (SKILL / "reference-scripts-surface.md").read_text(encoding="utf-8")
        self.assertIn("`verify_ac.py revert-check`", text)
        for verb in ("depth", "depth-check"):
            self.assertFalse(f"`verify_ac.py {verb}`" in text, f"the surface lists {verb}")
        r = _run("docgen.py", "surface", "--check", root=REPO)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("docgen surface: 0 drift item(s)", r.stdout)

    @unittest.skipUnless(workspace.in_dev_repo(), workspace.SKIP_REASON)
    def test_no_stamp_names_a_deleted_test(self) -> None:
        """AC4. MUTANTS: leave any one US0675/US0676 criterion stamped on its deleted node;
        delete `CriteriaSectionTests` rather than edit it."""
        nodes = {rel: verify_ac._ast_nodes((REPO / rel).read_text(encoding="utf-8"))
                 for rel in _EDITED}
        for gone in ("DerivedDepthTests", "DerivedDepthLaneTests"):
            self.assertFalse(any(gone in names for names in nodes.values()), gone)
        self.assertIn("CriteriaSectionTests::test_verify_ac_and_the_brief_count_the_same_criteria",
                      nodes[_EDITED[0]])

        ws = REPO / "sdlc-studio"
        paths = [p for sub in ("stories", "bugs", "change-requests")
                 for p in sorted((ws / sub).glob("*.md")) if not p.name.startswith("_")]
        dead, checked = [], 0
        for path in paths:
            for block in verify_ac.criteria_blocks(path.read_text(encoding="utf-8")):
                if (block.verified_state or "").strip().lower() != "yes" or not block.verifier:
                    continue
                test_file, node, kpat = verify_ac._selector_parts(block.verifier, REPO)
                if test_file not in nodes:
                    continue
                checked += 1
                if not verify_ac._selector_live(test_file, node, kpat, nodes[test_file]):
                    dead.append(f"{path.name} {block.ac_id}: {block.verifier}")
        self.assertGreater(checked, 0, "no stamped selector names an edited module")
        self.assertEqual([], dead)

        for unit, acs in _RETIRED.items():
            path = next((ws / "stories").glob(f"{unit}-*.md"))
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            blocks = {b.ac_id: b for b in verify_ac.criteria_blocks(text)}
            for ac in acs:
                with self.subTest(unit=unit, ac=ac):
                    block = blocks[ac]
                    self.assertRegex(block.verifier or "", r"^manual - retired by US0910: \S")
                    self.assertIsNotNone(block.verified_line, "no Verified line")
                    self.assertRegex(lines[block.verified_line],
                                     r"\*\*Verified:\*\* manual \(\d{4}-\d{2}-\d{2}\) - retired, "
                                     r"superseded by US0910$")


if __name__ == "__main__":
    unittest.main()
