"""BG0817: the bug fix and close steps hand the reviewer the brief whole, as a file.

The guidance said only "briefed with `critic.py brief`", and a worker relayed its own summary of
the brief instead: the standing practices and lessons were dropped, and one launch carried a shell
placeholder and no brief at all. `critic.py brief ... > brief.txt` already writes the whole brief
to the file and the fingerprint footer to stderr, so the fix is the guidance, and the second test
pins the redirect the guidance now teaches.

BG1344: a unit that declares `> **Isolation:** home` is briefed for the main checkout, since a
worktree lane's command check refuses the temporary HOME its tests set.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
critic = loader.load_script("critic")

_BUG = ("# BG0001: a bug\n\n> **Status:** In Progress\n> **Severity:** Low\n> **Affects:** a.py\n\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c. Fails on: x\n"
        "  - **Verify:** shell true\n")
#: the worktree lane's landing, which a HOME-isolated unit's brief must not name
_LANDS = "`sprint lane land` commits"
_MAIN = "Lane: the main checkout, not a worktree"


class BriefHandoverTests(unittest.TestCase):
    def test_the_close_steps_say_pass_the_brief_whole(self) -> None:
        """AC1. MUTANT: HEAD, where each step says only 'briefed with `critic.py brief`'.
        MUTANT: fix one step and leave the other - every line naming the brief is read, and
        reference-bug.md must carry it in both its fix and its close step."""
        for rel, steps in (("help/bug.md", 1), ("reference-bug.md", 2)):
            text = (SKILL / rel).read_text(encoding="utf-8")
            lines = [ln for ln in text.splitlines() if "critic.py brief --unit BG" in ln]
            with self.subTest(file=rel):
                self.assertEqual(steps, len(lines), f"{rel}: the steps naming the brief moved")
                for ln in lines:
                    self.assertIn("> brief.txt", ln, f"{rel}: no file hand-over in: {ln}")
                    self.assertRegex(ln, r"\bwhole\b", f"{rel}: not told to pass it whole: {ln}")

    def test_a_redirected_brief_is_the_fingerprinted_text(self) -> None:
        """AC2. MUTANT: a brief that prints its fingerprint footer to stdout - the redirect then
        writes the footer into the file the reviewer reads."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.py").write_text("", encoding="utf-8")
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            (bugs / "BG0001-a-bug.md").write_text(_BUG, encoding="utf-8")
            out = root / "brief.txt"
            with out.open("w", encoding="utf-8") as fh:
                proc = subprocess.run(
                    [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit",
                     "BG0001", "--seat", "qa", "--root", str(root)],
                    stdout=fh, stderr=subprocess.PIPE, text=True, check=False, timeout=120)
            self.assertEqual(0, proc.returncode, proc.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("BG0001", text)
            self.assertIn("AC1", text)
            self.assertNotIn("brief fingerprint:", text)
            m = re.search(r"brief fingerprint: ([0-9a-f]{12})", proc.stderr)
            self.assertIsNotNone(m, proc.stderr)
            self.assertEqual(critic.brief_fingerprint(text), m.group(1))

    def test_a_home_isolated_unit_is_briefed_for_the_main_checkout(self) -> None:
        """BG1344 AC1. MUTANT: the declaration is not read, so the HOME-isolated unit is briefed
        for the worktree lane `sprint lane land` lands. MUTANT: any `Isolation` value counts. An
        undeclared unit and one declaring another isolation are the positive controls."""
        units = {"BG0001": "", "BG0002": "> **Isolation:** home\n",
                 "BG0003": "> **Isolation:** none\n"}
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.py").write_text("", encoding="utf-8")
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            for uid, field in units.items():
                text = _BUG.replace("BG0001", uid).replace("> **Affects:** a.py\n",
                                                           f"> **Affects:** a.py\n{field}")
                (bugs / f"{uid}-a-bug.md").write_text(text, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", str(SCRIPTS / "sprint.py"), "lane", "brief", "--units",
                 *units, "--root", str(root)], capture_output=True, text=True, check=False,
                timeout=120, cwd=str(root), env=gitutil.git_env())
        self.assertEqual(0, proc.returncode, proc.stderr)
        briefs = dict(re.findall(r"^Unit: (BG\d+) (.*?)(?=^Unit: |\Z)", proc.stdout, re.M | re.S))
        self.assertEqual(sorted(briefs), sorted(units))
        home = briefs["BG0002"]
        self.assertIn(f"{_MAIN} - BG0002 declares `Isolation: home`", home)
        for said in ("run it as the wave's last lane", "every other lane's commit held",
                     "git add -- a.py"):
            self.assertIn(said, " ".join(home.split()))
        self.assertNotIn(_LANDS, home)
        for uid in ("BG0001", "BG0003"):
            with self.subTest(uid):
                self.assertIn(_LANDS, briefs[uid])
                self.assertNotIn(_MAIN, briefs[uid])


if __name__ == "__main__":
    unittest.main()
