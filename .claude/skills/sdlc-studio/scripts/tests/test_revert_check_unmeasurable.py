"""`verify_ac.py revert-check` judges only what it measured.

Two ways it judged what it never measured. A verifier that timed out was counted red, the proof
that the unit's tests reach its change, so a unit whose criteria never touch its change passed.
A revert that changed no byte (the base is the tree as it stands) left every criterion green,
and the unit was refused for a change that was never removed. Every case drives the shipped
entry point in a real git repository, and each refusal sits beside a judged control.
"""
from __future__ import annotations

import contextlib
import io
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(SCRIPTS))
import gitutil  # noqa: E402 - confined, hermetic git for the fixture repositories
import verify_ac  # noqa: E402

HELP = SCRIPTS.parent / "help" / "verify.md"
BASE = "BASE_ONLY = 1\n"
SHIPPED = 'BASE_ONLY = 1\nSHIPPED_MARKER = "SHIPPED_MARKER"\n'
REACHES = "grep SHIPPED_MARKER scripts/prod.py"  # red once the change is reverted
MISSES = "grep BASE_ONLY scripts/prod.py"         # green with or without the change
SLOW = "shell sleep 30"                           # outlives a one-second timeout


class UnmeasurableRevertTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="revert_unmeasured_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        (self.root / "scripts").mkdir()
        prod = self.root / "scripts" / "prod.py"
        prod.write_text(BASE, encoding="utf-8")
        (self.root / "scripts" / "other.py").write_text(BASE, encoding="utf-8")  # never changes
        for args in (["init", "-q"], ["config", "user.email", "t@example.com"],
                     ["config", "user.name", "t"], ["add", "-A"], ["commit", "-qm", "base"]):
            gitutil.git(args, self.root)
        prod.write_text(SHIPPED, encoding="utf-8")
        gitutil.git(["commit", "-qam", "ship"], self.root)
        self.stories = self.root / "sdlc-studio" / "stories"
        self.stories.mkdir(parents=True)

    def _unit(self, uid: str, affects: str, *verifiers: str) -> None:
        acs = "".join(f"- [ ] **AC{n}** the change is reached\n  - **Verify:** {v}\n"
                      for n, v in enumerate(verifiers, 1))
        (self.stories / f"{uid}-fixture.md").write_text(
            f"# {uid}: fixture\n\n> **Status:** Draft\n> **Affects:** {affects}\n\n"
            f"## Acceptance Criteria\n\n{acs}", encoding="utf-8")

    def _check(self, *args: str) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = verify_ac.main(["revert-check", *args, "--root", str(self.root)])
        return code, buf.getvalue()

    def test_a_timed_out_verifier_is_not_red(self):
        self._unit("US0001", "scripts/prod.py", SLOW)
        self._unit("US0002", "scripts/prod.py", SLOW, MISSES)
        code, out = self._check("--unit", "US0001", "--base", "HEAD~1", "--timeout", "1")
        self.assertRegex(out, r"AC1\s+unmeasured", out)
        self.assertNotIn("PASSES", out)
        self.assertEqual(code, 3, out)
        # Beside a criterion that stays green, the timeout is no proof of reach: refused.
        code, out = self._check("--unit", "US0002", "--base", "HEAD~1", "--timeout", "1")
        self.assertRegex(out, r"AC1\s+unmeasured", out)
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)

    def test_an_empty_revert_is_not_judged(self):
        self._unit("US0001", "scripts/prod.py", MISSES)
        before = (self.root / "scripts" / "prod.py").read_bytes()
        code, out = self._check("--unit", "US0001", "--base", "HEAD")
        self.assertEqual(code, 3, out)
        self.assertIn("not judged", out)
        self.assertIn("changes no byte", out)
        self.assertNotIn("stayed GREEN", out)
        self.assertEqual(before, (self.root / "scripts" / "prod.py").read_bytes())

    def test_a_differing_base_is_still_judged(self):
        # One file the revert leaves as it is does not make the whole revert empty.
        self._unit("US0001", "scripts/prod.py, scripts/other.py", MISSES)
        self._unit("US0002", "scripts/prod.py, scripts/other.py", REACHES)
        code, out = self._check("--unit", "US0001", "--base", "HEAD~1")
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)
        code, out = self._check("--unit", "US0002", "--base", "HEAD~1")
        self.assertEqual(code, 0, out)
        self.assertIn("PASSES", out)

    def test_only_a_run_that_reached_a_failing_verdict_is_red(self):
        def state(kind: str, code: int, *, ok: bool = False, vacuous: bool = False) -> str:
            return verify_ac._revert_state(
                verify_ac.VerifierResult(ok, kind, code, "", "", 0, vacuous=vacuous))
        self.assertEqual("green", state("pytest", 0, ok=True))
        self.assertEqual("red", state("pytest", 1))
        # A collection error after the revert (the test imports what was removed) is reach.
        self.assertEqual("red", state("pytest", 2))
        self.assertEqual("red", state("shell", 3))
        # A clean exit that is no pass: pytest skipped part of what it selected.
        self.assertEqual("unmeasured", state("pytest", 0))
        for code in (124, 126, 127):
            self.assertEqual("unmeasured", state("shell", code), code)
        self.assertEqual("unmeasured", state("pytest", 5, vacuous=True))
        self.assertEqual("unmeasured", state("invalid", 2))
        self.assertEqual("unmeasured", state("blocked", 2))

    def test_the_help_verdicts_match_the_exit_codes(self):
        text = HELP.read_text(encoding="utf-8")
        section = text.split("### revert-check", 1)[1].split("\n### ", 1)[0]
        table = dict(re.findall(r"^\| (pass|refused|not judged|error) \| (\d) \|", section, re.M))
        self.assertEqual({"pass": "0", "refused": "1", "not judged": "3", "error": "1"}, table)
        not_judged = next(ln for ln in section.splitlines() if ln.startswith("| not judged |"))
        self.assertIn("directory", not_judged, "the directory case is stated")
        self._unit("US0001", "scripts/prod.py", REACHES)
        self._unit("US0002", "scripts/prod.py", MISSES)
        self._unit("US0003", "scripts", REACHES)
        examples = re.findall(r"^verify_ac\.py (revert-check .+?)\s+# exit (\d)\b", section, re.M)
        self.assertEqual({"0", "1", "3"}, {want for _, want in examples}, examples)
        # US0001 reaches its change, US0002 misses it, US0003 names a directory in `Affects`.
        self.assertIn(("revert-check --unit US0003 --base HEAD~1", "3"), examples)
        for args, want in examples:
            code, out = self._check(*shlex.split(args)[1:])
            self.assertEqual(int(want), code, f"`{args}` returned {code}, the help says {want}\n{out}")


if __name__ == "__main__":
    unittest.main()
