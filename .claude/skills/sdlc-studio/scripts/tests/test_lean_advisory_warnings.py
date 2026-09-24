"""US0896: footprint warnings advise, and a finished artefact is never re-judged.

The pre-commit `warning-ratchet` lane refused any Affects/Verify warning its baseline did not
record. Every entry added to that baseline in its last month was a file deleted by design, or a
superseded artefact naming the file it was about, so the lane refused commits on paperwork and
never on a code defect. The lane, the `validate.py warning-ratchet` verb, its npm script and the
baseline are deleted. The warnings stay, as advice on open work: a terminal artefact is a
finished record, and a file it named that was later deleted says nothing about it.

AC1 DRIVES THE REAL HOOKS in the hermetic fixture `tools/tests/test_precommit_window_guard.py`
builds, and reads this repository's package.json and tree, because its criterion is about this
repository. AC2 runs the shipped `validate.py check` in a throwaway workspace. AC3 reads the
live artefacts.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/validate.py
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
import workspace  # noqa: E402

REPO = workspace.REPO
VALIDATE = SCRIPTS / "validate.py"
SKILL = ".claude/skills/sdlc-studio/scripts"
BASELINE = "sdlc-studio/.validate-warning-baseline.json"
TRIPWIRE_LOG = "sdlc-studio/.local/warning-ratchet-tripwire.log"
ARTEFACT_DIRS = ("stories", "bugs", "change-requests")


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _code(hook: str) -> str:
    """The hook's executable lines: a comment may say what a lane USED to do."""
    text = (REPO / ".githooks" / hook).read_text(encoding="utf-8")
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _npm_lint_commands() -> list[str]:
    """Every command `npm run lint` reaches, following its `npm run <name>` chain."""
    scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
    seen: list[str] = []
    todo = ["lint"]
    while todo:
        body = scripts[todo.pop()]
        seen.append(body)
        todo.extend(n for n in re.findall(r"npm run ([\w:-]+)", body) if n in scripts)
    return seen


def _story(sid: str, status: str, affects: str, verify: str) -> str:
    return (f"# {sid}: a unit\n\n> **Status:** {status}\n> **Affects:** {affects}\n"
            f"> **Points:** 2\n\n## Acceptance Criteria\n\n- **AC1:** Given x, then y\n"
            f"  - **Verify:** {verify}\n")


def _check(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VALIDATE), "check", "--root", str(root)],
                          capture_output=True, text=True, timeout=300, check=False)


class AdvisoryWarningTests(unittest.TestCase):

    def test_no_commit_or_lint_run_is_refused_on_a_footprint_warning(self) -> None:
        """AC1. MUTANTS: put the `warning-ratchet` lane back into the pre-commit hook (the
        stand-in below refuses as the real lane did on an unrecorded instance); put
        `lint:warning-ratchet` back into the npm lint chain; restore the verb or the baseline."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        sys.path.insert(0, str(REPO / "tools" / "tests"))
        import test_precommit_window_guard as wg  # noqa: PLC0415 - repo-only fixture module
        # 1. By EXECUTION: a staged story whose Affects names a missing file, committed through
        # the real hooks over a stand-in validate.py that logs any call and refuses the verb.
        with tempfile.TemporaryDirectory() as d:
            root = wg.WindowGuardTests("run")._repo(Path(d))
            _write(root, f"{SKILL}/validate.py",
                   "import sys\n"
                   f"open({TRIPWIRE_LOG!r}, 'a', encoding='utf-8').write(' '.join(sys.argv))\n"
                   "if 'warning-ratchet' in sys.argv:\n"
                   "    print('warning-ratchet: 1 instance(s) the baseline does not record:\\n'\n"
                   "          '    US0900 affects-unresolvable src/gone.py')\n"
                   "    sys.exit(1)\n")
            wg._git(root, "add", "-A")
            wg._git(root, "commit", "-q", "--no-verify", "-m", "tripwire")
            _write(root, "sdlc-studio/stories/US0900-x.md",
                   _story("US0900", "Draft", "src/gone.py", "pytest tests/test_gone.py::T::t"))
            wg._git(root, "add", "-A")
            done = subprocess.run(["git", "-C", str(root), "commit", "-m", "docs: a story"],
                                  capture_output=True, text=True, env=wg._clean_env(),
                                  timeout=600)
            out = done.stdout + done.stderr
            log = root / TRIPWIRE_LOG
            self.assertFalse(log.exists(), f"a hook ran validate.py:\n{out}")
            self.assertEqual(0, done.returncode, f"the commit was refused:\n{out}")
            self.assertNotRegex(out, r"\b(ok|FAIL)\b\s+warning-ratchet\b")
            # The positive control: the fixture reached the kept lanes and the end of the gate.
            self.assertRegex(out, r"\bok\b\s+budgets\b")
            self.assertIn("gate green.", out)
        # 2. No hook runs the verb under any lane key.
        for hook in ("pre-commit", "commit-msg"):
            with self.subTest(hook=hook):
                self.assertNotIn("warning-ratchet", _code(hook))
        # 3. `npm run lint` reaches no command that runs it, and the script is gone.
        for command in _npm_lint_commands():
            self.assertNotIn("warning-ratchet", command)
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertNotIn("lint:warning-ratchet", scripts)
        # 4. The verb is gone from the shipped CLI: argparse refuses it as an unknown choice.
        r = subprocess.run([sys.executable, str(VALIDATE), "warning-ratchet"],
                           capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(2, r.returncode, r.stdout + r.stderr)
        self.assertIn("invalid choice", r.stderr)
        # 5. The baseline is gone.
        self.assertFalse((REPO / BASELINE).exists(), f"{BASELINE} still exists")

    def test_warnings_advise_on_open_work_and_skip_terminal_artefacts(self) -> None:
        """AC2, read narrowly. The open story's warning is for its UNRUNNABLE Verify: a `Verify:`
        target that is neither on disk nor declared (`affects-undeclared`). A file the open story
        declares and has not written yet prints nothing - that is the file it will create
        (US0528 AC1) - and the assertion below pins that silence rather than leaving the story's
        "naming a missing file" to be read as more than the fixture shows.

        MUTANTS: drop the terminal guard on the footprint warnings (the Done, Fixed and
        Superseded units are reported again); widen it to every status (the Draft story's
        warning is lost); make a warning count towards the exit code."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "src/kept.py", "VALUE = 1\n")
            # Open work: Affects declares a file not written yet (not warned), and the Verify
            # names a test file that is neither on disk nor declared, so it cannot run (warned).
            _write(root, "sdlc-studio/stories/US0001-draft.md",
                   _story("US0001", "Draft", "src/not_yet.py",
                          "pytest tests/test_not_yet.py::T::test_it"))
            # Finished records whose Affects names a file deleted since, and whose Verify names
            # a test file gone with it.
            gone = "pytest tests/test_gone.py::T::test_it"
            _write(root, "sdlc-studio/stories/US0002-done.md",
                   _story("US0002", "Done", "src/kept.py, src/deleted.py", gone))
            _write(root, "sdlc-studio/bugs/BG0003-fixed.md",
                   _story("BG0003", "Fixed", "src/kept.py, src/deleted.py", gone))
            _write(root, "sdlc-studio/stories/US0004-superseded.md",
                   _story("US0004", "Superseded", "src/deleted.py", gone))
            # A superseded request carrying a command-shaped Verify nothing executes.
            _write(root, "sdlc-studio/change-requests/CR0005-superseded.md",
                   _story("CR0005", "Superseded", "src/deleted.py", gone))
            r = _check(root)
        out = r.stdout + r.stderr
        self.assertEqual(0, r.returncode, out)
        draft = [ln for ln in out.splitlines() if "US0001-draft.md" in ln]
        self.assertTrue(draft, f"the open story's warning is gone:\n{out}")
        self.assertTrue(all(ln.startswith("WARNING") for ln in draft), out)
        self.assertIn("tests/test_not_yet.py", "\n".join(draft))
        self.assertNotIn("src/not_yet.py", "\n".join(draft),
                         "a declared file the open story will create was warned")
        for name in ("US0002-done.md", "BG0003-fixed.md", "US0004-superseded.md",
                     "CR0005-superseded.md"):
            with self.subTest(unit=name):
                self.assertNotIn(name, out, "a terminal artefact was re-judged")
        # All five were read: the silence on four is a verdict, not a skipped file.
        self.assertRegex(out, r"checked=5 errors=0 warnings=[1-9]")


#: The test nodes this story deletes, by the selector text a `Verify:` line names them with.
#: `test_a_terminal_unit_with_a_missing_path_is_still_warned` pinned the warning AC2 removes.
DELETED_NODES = (
    "WarningRatchetTests", "RatchetStatesTests", "WarningRatchetExitCodeTests",
    "WarningRatchetLaneTests", "a_stale_ratchet_baseline_says_it_is_not_refusing",
    "every_refusing_ratchet_state_exits_non_zero", "a_clean_ratchet_baseline_exits_zero",
    "test_a_terminal_unit_with_a_missing_path_is_still_warned",
)

#: The criteria that named a deleted node, by artefact, and how many each carried. The count is
#: the assertion: a retired line dropped or added is a changed record, not a rewording.
RETIRED = {"US0480": 5, "BG0523": 2, "BG0524": 3, "BG0543": 3, "US0528": 1}

#: The D0259 pattern, naming this story as the retirer.
RETIRED_VERIFY = re.compile(r"\*\*Verify:\*\*\s*manual - retired by US0896: \S")
RETIRED_STAMP = re.compile(
    r"\*\*Verified:\*\*\s*manual \(\d{4}-\d{2}-\d{2}\) - retired, superseded by US0896\b")


class RetiredCriteriaTests(unittest.TestCase):

    def test_the_warning_ratchet_criteria_are_retired(self) -> None:
        """AC3. MUTANTS: leave any criterion's `Verify:` naming a deleted node; retire one
        without its `Verified:` stamp; name another story as the retirer."""
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        live, retired = [], {}
        for path in [p for d in ARTEFACT_DIRS
                     for p in sorted((REPO / "sdlc-studio" / d).glob("*.md"))]:
            lines = path.read_text(encoding="utf-8").splitlines()
            unit = path.name.split("-")[0]
            for i, line in enumerate(lines):
                if "**Verify:**" in line and any(n in line for n in DELETED_NODES):
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
