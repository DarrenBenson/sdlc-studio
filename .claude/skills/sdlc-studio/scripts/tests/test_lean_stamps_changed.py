"""US0945: a staged change to a stamped test lists the criteria that stamp it.

`stamps --staged` refused a staged rename or deletion that orphaned a stamped selector, but an
edit that kept the node and changed what it asserts passed in silence, so a `Verified: yes`
criterion could keep claiming what its test no longer checked. The lane now lists each such
criterion's id and words under a `re-read` heading. It is advisory: an edit never changes the
exit code, and a deletion still refuses exactly as before.

Each test drives the shipped CLI against a throwaway git repository whose index holds the edit.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "verify_ac.py"
TEST = "tests/test_probe.py"

PROBE = (
    "class TestT:\n"
    "    def test_x(self):\n"
    "        value = 1 + 1\n"
    "        assert value == 2\n"
    "\n"
    "    def test_y(self):\n"
    "        assert 'a' in 'abc'\n"
)

OTHER = "tests/test_other.py"

WORDS = "Given the probe, when it runs, then one plus one is still two."
HEADING_THEN = "the heading criterion's words are listed"
CHECKBOX_WORDS = "the checkbox criterion's words are listed."
SECOND_WORDS = "Given a second Verify line, then it is read too."


def _story(root: Path) -> None:
    """US0001 AC1 stamps `test_x`; AC2 names `test_x` too but is not verified, so it is never
    listed; nothing stamps `test_y`."""
    path = root / "sdlc-studio" / "stories" / "US0001-probe.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# US0001: a stamped probe\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
        f"- **AC1:** {WORDS}\n"
        f"  - **Verify:** pytest {TEST}::TestT::test_x\n"
        "  - **Verified:** yes (2026-09-25)\n"
        "- **AC2:** Given an unverified claim, then it is never listed.\n"
        f"  - **Verify:** pytest {TEST}::TestT::test_x\n"
        "  - **Verified:** no\n", encoding="utf-8")
    # The two shapes whose parsed title is empty, so the words come from elsewhere: a `### ACn`
    # heading over Given/When/Then bullets, and a checkbox whose words sit inside the bold.
    (path.parent / "US0002-heading.md").write_text(
        "# US0002: heading shape\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n### AC1\n\n"
        "- **Given** the heading shape\n- **When** its test changes\n"
        f"- **Then** {HEADING_THEN}\n\n"
        f"- **Verify:** pytest {TEST}::TestT::test_x\n- **Verified:** yes (2026-09-25)\n",
        encoding="utf-8")
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True, exist_ok=True)
    (bugs / "BG0003-checkbox.md").write_text(
        "# BG0003: checkbox shape\n\n> **Status:** Fixed\n\n## Acceptance Criteria\n\n"
        f"- [x] **AC1: {CHECKBOX_WORDS}**\n"
        f"  - **Verify:** pytest {TEST}::TestT::test_x\n  - **Verified:** yes (2026-09-25)\n",
        encoding="utf-8")
    # Its FIRST Verify line names another file; only its second names `test_x`.
    (path.parent / "US0004-second-line.md").write_text(
        "# US0004: second line\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
        f"- **AC1:** {SECOND_WORDS}\n"
        f"  - **Verify:** pytest {OTHER}::test_o\n"
        f"  - **Verify:** pytest {TEST}::TestT::test_x\n"
        "  - **Verified:** yes (2026-09-25)\n", encoding="utf-8")


class StampsChangedTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "repo"
        (self.root / "tests").mkdir(parents=True)
        (self.root / TEST).write_text(PROBE, encoding="utf-8")
        (self.root / OTHER).write_text("def test_o():\n    assert True\n", encoding="utf-8")
        _story(self.root)
        gitutil.git(["init", "-q"], self.root)
        gitutil.git(["add", "-A"], self.root)
        gitutil.git(["commit", "-q", "--no-verify", "-m", "fixture"], self.root)

    def _stage(self, body: str) -> None:
        self.assertNotEqual(body, PROBE, "the fixture edit did not apply")
        (self.root / TEST).write_text(body, encoding="utf-8")
        gitutil.git(["add", TEST], self.root)

    def _stamps(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "stamps", "--staged", "--root", str(self.root)],
            capture_output=True, text=True, timeout=120, cwd=str(self.root), env=gitutil.git_env())

    def test_an_edited_stamped_test_lists_its_criterion(self) -> None:
        """AC1. MUTANTS: HEAD, which reads only whether `test_x` still exists - exit 0 and no
        `re-read` heading; printing the parsed title alone, which is empty for the heading and
        checkbox shapes; reading only a criterion's first Verify line, which misses US0004.
        The unverified AC2 names the same node and must stay unlisted."""
        self._stage(PROBE.replace("value = 1 + 1", "value = 2"))
        proc = self._stamps()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        lines = proc.stdout.splitlines()
        heading = [i for i, ln in enumerate(lines) if "re-read" in ln]
        self.assertTrue(heading, "no `re-read` heading:\n" + proc.stdout)
        listed = "\n".join(lines[heading[0] + 1:])
        self.assertIn(f"US0001 AC1: {WORDS}", listed, proc.stdout)
        self.assertIn("US0002 AC1: Given the heading shape When its test changes Then "
                      f"{HEADING_THEN}", listed, proc.stdout)
        self.assertIn(f"BG0003 AC1: {CHECKBOX_WORDS}", listed, proc.stdout)
        self.assertIn(f"US0004 AC1: {SECOND_WORDS}", listed,
                      "a criterion whose second Verify line names the edited test was not listed")
        self.assertNotIn("AC2", proc.stdout, "an unverified criterion was listed")

    def test_a_deleted_stamped_test_still_refuses(self) -> None:
        """AC2. MUTANT: folding a deleted node into the advisory list - exit 0, or the
        criterion listed to re-read instead of refused as orphaned."""
        head, _sep, _tail = PROBE.partition("    def test_x(self):\n")
        body = head + PROBE.split("\n\n", 1)[1]
        self.assertNotIn("test_x", body)
        self._stage(body)
        proc = self._stamps()
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("US0001 AC1: stamped verified, but its verifier selects nothing",
                      proc.stdout)
        self.assertIn("orphaned by this commit", proc.stderr)
        self.assertNotIn("re-read", proc.stdout + proc.stderr,
                         "a deletion was folded into the advisory list")

    def test_an_unstamped_edit_lists_nothing(self) -> None:
        """AC3. MUTANT: listing every stamped criterion in a changed test file - `test_y`,
        which nothing stamps, shares the file with the stamped `test_x`."""
        self._stage(PROBE.replace("'a' in 'abc'", "'b' in 'abc'"))
        proc = self._stamps()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("re-read", proc.stdout + proc.stderr, proc.stdout)
        self.assertNotIn("US0001", proc.stdout + proc.stderr, proc.stdout)

    def test_a_cosmetic_edit_lists_nothing(self) -> None:
        """AC4. MUTANT: comparing raw text rather than each node's parsed body. The edit
        moves `test_x` down two lines, respaces an expression and adds comments."""
        cosmetic = PROBE.replace(
            "class TestT:\n",
            "# a comment above the class\n\n\nclass TestT:\n").replace(
            "        value = 1 + 1\n",
            "        # a comment in the body\n\n        value = 1+1   # trailing\n")
        self._stage(cosmetic)
        proc = self._stamps()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("re-read", proc.stdout + proc.stderr, proc.stdout)


if __name__ == "__main__":
    unittest.main()
