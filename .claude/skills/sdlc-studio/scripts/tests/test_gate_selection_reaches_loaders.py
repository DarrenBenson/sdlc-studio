"""BG1000: the commit's test selection reaches every module that drives a changed file.

A module that loads its script through `loader.load_script("x")`, one whose `test-census-subject`
header names the changed file, and one that imports a fixture test module reaching the change are
each selected. Every case drives `gate.py --suite-decision --changed` through its entry point:
the fixture cases over a tree laid out as this repository's two suites are, and AC3 over this
repository, for the reproduction the bug was filed on.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
GATE = SCRIPTS / "gate.py"
SKILL = ".claude/skills/sdlc-studio/scripts"
SKILL_TESTS = f"{SKILL}/tests"
TOOLS_TESTS = "tools/tests"


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _selected(root: Path, *changed: str) -> set[str]:
    """The `suite-selector:` lines `gate.py --suite-decision --changed` prints for `changed`."""
    r = subprocess.run([sys.executable, str(GATE), "--root", str(root), "--suite-decision",
                        "--changed", *changed], cwd=root, env=_env(), capture_output=True,
                       text=True, timeout=300)
    assert r.returncode in (0, 1), r.stdout + r.stderr
    return {line.split(": ", 1)[1] for line in r.stdout.splitlines()
            if line.startswith("suite-selector: ")}


def _tree(root: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


class SelectionReachesLoadersTests(unittest.TestCase):

    def test_load_script_is_a_load(self) -> None:
        """AC1. Mutant: `_LOADER_NAME` without its `load_script` alternative, so a module that
        loads `widget` only through the shared loader is not selected for a change to it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, {
                f"{SKILL}/widget.py": "X = 1\n",
                f"{SKILL}/gadget.py": "Y = 1\n",
                f"{SKILL_TESTS}/test_drives_it.py":
                    "import loader\nwidget = loader.load_script(\"widget\")\n",
                f"{SKILL_TESTS}/test_bare_call.py":
                    "from loader import load_script\nW = load_script( 'widget' )\n",
                f"{SKILL_TESTS}/test_elsewhere.py":
                    "import loader\ngadget = loader.load_script(\"gadget\")\n",
            })
            self.assertEqual({f"{SKILL_TESTS}/test_drives_it.py", f"{SKILL_TESTS}/test_bare_call.py"},
                             _selected(root, f"{SKILL}/widget.py"),
                             "a change to widget must select exactly the modules that load it")

    def test_census_subject_and_fixture_imports_reach(self) -> None:
        """AC2. Mutants: the `test-census-subject` header ignored, so a doc's own test is not
        selected for a change to the doc; the header read only for a changed file that is not
        code (M7), so a module whose census subject is a script, and which neither imports nor
        loads it, is not selected for a change to that script; a fixture test module's reach
        not inherited by the module importing it; a reach inherited from a test module the
        importer never names; inheritance followed past one level, which the changelog says it
        is not."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, {
                "docs/guide.md": "# Guide\n",
                "docs/other.md": "# Other\n",
                f"{SKILL}/widget.py": "X = 1\n",
                f"{SKILL}/gadget.py": "Y = 1\n",
                f"{SKILL}/gizmo.py": "Z = 1\n",
                f"{TOOLS_TESTS}/test_gizmo_contract.py":
                    f"# test-census-subject: {SKILL}/gizmo.py\nNAME = 'gizmo'\n",
                f"{TOOLS_TESTS}/test_guide_claims.py":
                    "# test-census-subject: docs/guide.md\nGUIDE = 'docs/guide.md'\n",
                f"{TOOLS_TESTS}/test_other_claims.py":
                    "# test-census-subject: docs/other.md\nOTHER = 'docs/other.md'\n",
                f"{SKILL_TESTS}/test_close_fixture.py":
                    "import loader\nwidget = loader.load_script(\"widget\")\nclass Base: pass\n",
                f"{SKILL_TESTS}/test_close_page.py":
                    "from test_close_fixture import Base\n",
                f"{SKILL_TESTS}/test_close_page_twice_removed.py":
                    "import test_close_page\n",
                f"{SKILL_TESTS}/test_gadget_fixture.py":
                    "import loader\ngadget = loader.load_script(\"gadget\")\n",
                f"{SKILL_TESTS}/test_gadget_page.py":
                    "import test_gadget_fixture\n",
            })
            doc = _selected(root, "docs/guide.md")
            self.assertEqual({f"{TOOLS_TESTS}/test_guide_claims.py"}, doc,
                             "a doc's change must select exactly the module naming it as subject")
            self.assertEqual({f"{TOOLS_TESTS}/test_gizmo_contract.py"},
                             _selected(root, f"{SKILL}/gizmo.py"),
                             "a script's change must select the module naming it as census "
                             "subject, though that module neither imports nor loads it")
            self.assertEqual({f"{SKILL_TESTS}/test_close_fixture.py", f"{SKILL_TESTS}/test_close_page.py"},
                             _selected(root, f"{SKILL}/widget.py"),
                             "a change to widget must select its fixture module and the module "
                             "importing it, and no module that imports neither")

    def test_the_reproduction_selects_the_close_modules(self) -> None:
        """AC3. Mutant: any of the three close modules the bug names missing from the selection
        for a change to sprint.py."""
        got = _selected(REPO, f"{SKILL}/sprint.py")
        # HAND-MAINTAINED ON PURPOSE: these are the three modules BG1000's reproduction names,
        # so the list is the assertion itself, not a copy of a set the tree owns.
        for module in ("test_lean_close.py", "test_lean_close_shows_the_page.py",
                       "test_lean_sign.py"):
            with self.subTest(module=module):
                self.assertIn(f"{SKILL_TESTS}/{module}", got)


if __name__ == "__main__":
    unittest.main()
