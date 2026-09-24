"""US0902: adding a script no longer needs a matching TSD sentence to commit.

The script-tests lane held the TSD's Unit coverage map, a fenced list of prose, to the scripts
tree. A script that arrived without a test AND without a line in that list refused the commit,
so the lane caught a missing document entry, never a code defect. The lane, its checker and the
checker's own tests are deleted, and the TSD no longer claims a checker holds the map.

AC1 DRIVES THE REAL HOOKS in the hermetic fixture `test_precommit_window_guard.py` builds, so
what it pins is what a commit runs, not what the hook text happens to say.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

# Imported as a MODULE so unittest does not collect and re-run its cases here.
import test_precommit_window_guard as _wg

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / ".githooks"
CHECKER = "check_script_tests.py"
DELETED = ("tools/check_script_tests.py", "tools/tests/test_check_script_tests.py")
TRIPWIRE_LOG = "sdlc-studio/.local/script-tests-tripwire.log"
ARTEFACT_DIRS = ("stories", "bugs", "change-requests")

#: The criteria that named a deleted node, by artefact, and how many each carried. The count is
#: the assertion: a retired line dropped or added is a changed record, not a rewording.
RETIRED = {"US0456": 5, "BG0727": 1}

#: The D0259 pattern, naming this story as the retirer.
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0902: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0902\b")


def _code(hook: str) -> str:
    """The hook's executable lines: a comment may say what a lane USED to do."""
    text = (HOOKS / hook).read_text(encoding="utf-8")
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _npm_lint_commands() -> list[str]:
    """Every command `npm run lint` reaches, following its `npm run <name>` chain."""
    scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
    seen: list[str] = []
    todo = ["lint"]
    while todo:
        name = todo.pop()
        body = scripts[name]
        seen.append(body)
        todo.extend(n for n in re.findall(r"npm run ([\w:-]+)", body) if n in scripts)
    return seen


def _artefacts() -> list[Path]:
    root = REPO / "sdlc-studio"
    return [p for d in ARTEFACT_DIRS for p in sorted((root / d).glob("*.md"))]


class ScriptTestsLaneTests(unittest.TestCase):

    def test_an_unmapped_script_refuses_no_commit(self) -> None:
        """AC1. MUTANTS: put the `script-tests` lane back into the pre-commit hook (its stand-in
        here refuses an unmapped script, as the real checker did); put `lint:script-tests` back
        into the npm lint chain; restore the checker or its tests; restore the TSD sentence."""
        # 1. By EXECUTION: a new skill script with no test and no coverage-map entry, over a
        # stand-in for the deleted checker that logs its run and refuses.
        with tempfile.TemporaryDirectory() as d:
            root = _wg.WindowGuardTests("run")._repo(Path(d))
            _write(root, f"tools/{CHECKER}",
                   "import sys\n"
                   f"open({TRIPWIRE_LOG!r}, 'a', encoding='utf-8').write('ran\\n')\n"
                   "print('untested module with no coverage-map entry: brand_new', "
                   "file=sys.stderr)\n"
                   "sys.exit(1)\n")
            _wg._git(root, "add", "-A")
            _wg._git(root, "commit", "-q", "--no-verify", "-m", "tripwire")
            _write(root, ".claude/skills/sdlc-studio/scripts/brand_new.py", "VALUE = 1\n")
            _wg._git(root, "add", "-A")
            done = subprocess.run(["git", "-C", str(root), "commit", "-m", "feat: a new script"],
                                  capture_output=True, text=True, env=_wg._clean_env())
            out = done.stdout + done.stderr
            log = root / TRIPWIRE_LOG
            self.assertFalse(log.exists(), f"the deleted checker ran:\n{out}")
            self.assertEqual(0, done.returncode, f"the commit was refused:\n{out}")
            self.assertNotRegex(out, r"\b(ok|FAIL)\b\s+script-tests\b")
            # The positive control: the fixture reached the kept lanes and the end of the gate.
            self.assertRegex(out, r"\bok\b\s+budgets\b")
            self.assertIn("gate green.", out)
        # 2. No hook invokes the checker under any key.
        for hook in ("pre-commit", "commit-msg"):
            with self.subTest(hook=hook):
                self.assertNotIn(CHECKER, _code(hook))
                self.assertNotIn('run "script-tests"', _code(hook))
        # 3. `npm run lint` reaches no command that runs it.
        for command in _npm_lint_commands():
            self.assertNotIn(CHECKER, command)
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertNotIn("lint:script-tests", scripts)
        # 4. The checker and its test module are gone.
        for rel in DELETED:
            with self.subTest(deleted=rel):
                self.assertFalse((REPO / rel).exists(), f"{rel} still exists")
        # 5. The TSD no longer says a checker holds its map to the tree.
        tsd = (REPO / "sdlc-studio" / "tsd.md").read_text(encoding="utf-8")
        self.assertNotIn(CHECKER, tsd)
        self.assertNotRegex(tsd, r"holds (the|its|this) (list|map)[^.]*to the tree")

    def test_the_script_tests_criteria_are_retired(self) -> None:
        """AC2. MUTANTS: leave any criterion's `Verify:` naming a deleted node; retire one
        without its `Verified:` stamp; name another story as the retirer."""
        live, retired = [], {}
        for path in _artefacts():
            lines = path.read_text(encoding="utf-8").splitlines()
            unit = path.name.split("-")[0]
            for i, line in enumerate(lines):
                if re.search(r"\*\*Verify:\*\*\s*pytest\s+\S*test_check_script_tests", line):
                    live.append(f"{path.name}:{i + 1}")
                if RETIRED_VERIFY.search(line):
                    stamp = next((ln for ln in lines[i + 1:i + 3] if "Verified:" in ln), "")
                    self.assertRegex(stamp, RETIRED_STAMP,
                                     f"{path.name}:{i + 1} is retired without its stamp")
                    retired[unit] = retired.get(unit, 0) + 1
        self.assertEqual([], live, "a criterion still names a deleted test node")
        self.assertEqual(RETIRED, retired)


if __name__ == "__main__":
    unittest.main()
