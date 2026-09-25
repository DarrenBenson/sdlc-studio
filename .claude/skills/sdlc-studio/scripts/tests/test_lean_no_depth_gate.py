"""US0934: a bug reaches Fixed on its green Verify selectors, with no depth tier to stamp.

Every test drives the shipped entry points (`transition.py`, `artifact.py`, `verify_ac.py`) as
subprocesses against a throwaway workspace. Nothing reads this repository's own config, ledgers
or `.local` state, except the one scan AC3 names over the shipped scripts.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402

_BUG = ("# {id}: a bug\n\n> **Status:** {status}\n> **Severity:** medium\n{extra}\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c\n"
        "  - **Verify:** shell {verdict}\n")
_STORY = ("# {id}: a story\n\n> **Status:** In Progress\n\n## Acceptance Criteria\n\n"
          "### AC1: it works\n\n- **Verify:** shell true\n{target}")


def _run(script: str, *argv: str, root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv, "--root", str(root)],
                          capture_output=True, text=True, check=False, timeout=300)


def _workspace(d: str, config: str = "") -> Path:
    root = Path(d)
    for sub in ("bugs", "stories"):
        (root / "sdlc-studio" / sub).mkdir(parents=True)
    (root / "sdlc-studio" / ".config.yaml").write_text(f"schema_version: 3\n{config}",
                                                       encoding="utf-8")
    return root


def _bug(root: Path, uid: str, verdict: str = "true", status: str = "In Progress",
         extra: str = "") -> Path:
    path = root / "sdlc-studio" / "bugs" / f"{uid}-a-bug.md"
    path.write_text(_BUG.format(id=uid, status=status, extra=extra, verdict=verdict),
                    encoding="utf-8")
    return path


def _story(root: Path, uid: str, target: str = "") -> Path:
    path = root / "sdlc-studio" / "stories" / f"{uid}-a-story.md"
    line = f"- **Verification target:** {target}\n" if target else ""
    path.write_text(_STORY.format(id=uid, target=line), encoding="utf-8")
    return path


def _reviewed_and_verified(test: unittest.TestCase, root: Path, uid: str) -> None:
    """An independent delivery APPROVE on record, and the unit's selectors run once."""
    critic.record_verdict(root, uid, "APPROVE", "rev", "dev")
    _run("verify_ac.py", "run", "--id", uid, root=root)


def _status(path: Path) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("> **Status:**"):
            return line.split(":**", 1)[1].strip()
    return ""


class DepthGateGoneTests(unittest.TestCase):
    def test_a_bug_without_a_depth_reaches_fixed(self) -> None:
        """AC1. MUTANTS: HEAD's `_bug_depth_gate`, which refuses the missing field; and a
        deletion that takes the Verify gate with it, so the red bug reaches Fixed too."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            green = _bug(root, "BG0001", "true")
            red = _bug(root, "BG0002", "false")
            for uid in ("BG0001", "BG0002"):
                _reviewed_and_verified(self, root, uid)
            self.assertNotIn("Verification depth", green.read_text(encoding="utf-8"))

            r = _run("transition.py", "set", "BG0001", "Fixed", root=root)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(_status(green), "Fixed")

            r = _run("transition.py", "set", "BG0002", "Fixed", root=root)
            out = r.stdout + r.stderr
            self.assertNotEqual(r.returncode, 0, out)
            self.assertIn("red (AC1)", out)
            self.assertNotIn("Verification depth", out)
            self.assertEqual(_status(red), "In Progress")

    def test_both_depth_flags_are_retired_and_close_still_works(self) -> None:
        """AC2. MUTANT: remove only `artifact.py close --depth`, leaving `transition.py set
        --depth` accepted - the second call then exits 0 and stamps the field."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            bug = _bug(root, "BG0001", "true")
            _reviewed_and_verified(self, root, "BG0001")
            before = bug.read_bytes()
            for script, argv in (("artifact.py", ("close", "--id", "BG0001")),
                                 ("transition.py", ("set", "BG0001", "Fixed"))):
                with self.subTest(script=script):
                    r = _run(script, *argv, "--depth", "functional", root=root)
                    self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                    self.assertIn("--depth", r.stderr)
                    self.assertIn("retired", r.stderr)
                    self.assertEqual(bug.read_bytes(), before, "a retired flag wrote something")

            story = _story(root, "US0001")
            _reviewed_and_verified(self, root, "US0001")
            r = _run("artifact.py", "close", "--id", "US0001", root=root)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(_status(story), "Done")

    def test_no_parity_refusal_or_reopen_retraction(self) -> None:
        """AC3. MUTANTS: keep the parity check under `quality.depth_parity_gate`; keep the reopen
        retraction; keep `critic.py`'s `depth_retracted` read."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d, "quality:\n  depth_parity_gate: block\n")
            story = _story(root, "US0001", target="soak")
            _reviewed_and_verified(self, root, "US0001")
            r = _run("transition.py", "set", "US0001", "Done", root=root)
            out = r.stdout + r.stderr
            self.assertEqual(r.returncode, 0, out)
            self.assertEqual(_status(story), "Done")
            self.assertNotIn("parity", out)

            depth = "> **Verification depth:** functional (unit)\n"
            bug = _bug(root, "BG0001", "true", status="Fixed", extra=depth)
            r = _run("transition.py", "set", "BG0001", "In Progress", root=root)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            text = bug.read_text(encoding="utf-8")
            self.assertEqual(_status(bug), "In Progress")
            self.assertIn(depth, text)
            self.assertNotIn("RETRACTED", text)

        callers = [p.relative_to(SCRIPTS).as_posix() for p in sorted(SCRIPTS.rglob("*.py"))
                   if "tests" not in p.relative_to(SCRIPTS).parts
                   and "depth_retracted" in p.read_text(encoding="utf-8")]
        self.assertEqual(callers, [])

    def test_a_new_bug_carries_no_depth_field(self) -> None:
        """AC4. MUTANT: drop the field from the template while the created bug still carries it
        (or the reverse); both halves are read."""
        template = (SKILL / "templates" / "core" / "bug.md").read_text(encoding="utf-8")
        self.assertNotIn("Verification depth", template)
        self.assertNotIn("verification_depth", template)
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            for tier in ("minimal", "planning", "full"):
                with self.subTest(template=tier):
                    r = _run("artifact.py", "new", "--type", "bug", "--title", f"a {tier} bug",
                             "--template", tier, "--affects", "src/x.py", "--points", "2",
                             root=root)
                    self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            made = sorted((root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self.assertEqual(len(made), 3)
            for path in made:
                self.assertNotIn("Verification depth", path.read_text(encoding="utf-8"), path.name)


if __name__ == "__main__":
    unittest.main()
