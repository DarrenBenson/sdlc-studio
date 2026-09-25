"""BG0779: the pre-commit hook shows the stamps-staged lane's re-read list on a passing commit.

`verify_ac.py stamps --staged` lists every `Verified: yes` criterion whose stamped test the commit
changes, under a `re-read` heading, and exits 0: it is advisory. The hook's `verdict()` printed a
lane's output only on FAIL, so on a passing commit the list reached nobody. These tests drive the
REAL tracked hook in a throwaway repository whose other lanes are stubbed to pass, with the REAL
`verify_ac.py` behind the stamps-staged lane, and read what the commit prints.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

# Importable under both runners: pytest does not put this directory on the path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Imported as a MODULE, so unittest does not collect and re-run its TestCase here.
import hookutil  # noqa: E402
import test_precommit_window_guard as _wg  # noqa: E402

_git = _wg._git
SCRIPTS = _wg.REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

#: The stamps-staged lane's stand-in: the real `verify_ac.py`, run from the shipped tree.
VERIFY_AC_SHIM = """\
import sys
sys.path.insert(0, {scripts!r})
import verify_ac
sys.exit(verify_ac.main())
"""

#: A passing lane that DOES print on success, so a hook printing every lane's output on
#: success is seen. Only the `tools/` checkers the pre-commit hook alone invokes, derived from
#: the hooks; the commit-msg hook reads its stubs' output.
CHATTY = 'print("CHATTY-SUCCESS-OUTPUT {name}")\n'
CHATTY_TOOLS = sorted(set(hookutil.hook_tool_scripts("pre-commit"))
                      - set(hookutil.hook_tool_scripts("commit-msg")))

PROBE = "tools/tests/test_probe.py"
PROBE_BODY = (
    "import unittest\n\n\n"
    "class T(unittest.TestCase):\n"
    "    def test_x(self):\n"
    "        value = 1 + 1\n"
    "        self.assertEqual(value, 2)\n\n"
    "    def test_y(self):\n"
    "        self.assertIn('a', 'abc')\n"
)
WORDS = "Given the probe, when it runs, then one plus one is still two."
STORY = (
    "# US0001: a stamped probe\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
    f"- **AC1:** {WORDS}\n"
    f"  - **Verify:** pytest {PROBE}::T::test_x\n"
    "  - **Verified:** yes (2026-09-25)\n"
)

#: The re-read heading `staged_stamps` prints; its presence is what the hook keys on.
REREAD = "verify-stamps: staged: re-read - "


class StampsAdvisoryTests(unittest.TestCase):

    def _repo(self, tmp: Path) -> Path:
        root = _wg.WindowGuardTests("run")._repo(tmp)
        (root / ".claude" / "skills" / "sdlc-studio" / "scripts" / "verify_ac.py").write_text(
            VERIFY_AC_SHIM.format(scripts=str(SCRIPTS)), encoding="utf-8")
        for name in CHATTY_TOOLS:
            (root / "tools" / name).write_text(CHATTY.format(name=name), encoding="utf-8")
        (root / PROBE).write_text(PROBE_BODY, encoding="utf-8")
        story = root / "sdlc-studio" / "stories" / "US0001-probe.md"
        story.parent.mkdir(parents=True, exist_ok=True)
        story.write_text(STORY, encoding="utf-8")
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        return root

    def _commit_probe(self, old: str, new: str) -> tuple[int, str]:
        self.assertEqual(1, PROBE_BODY.count(old), "the fixture edit's anchor is not unique")
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            fixture = _wg.WindowGuardTests("run")
            return fixture._commit(root, PROBE, PROBE_BODY.replace(old, new))

    @staticmethod
    def _lane_block(out: str) -> str:
        """The stamps-staged lane's `ok` line and everything up to the next lane's verdict."""
        m = re.search(r"^  ok   stamps-staged\n(.*?)(?=^  (?:ok|FAIL) )", out, re.M | re.S)
        if not m:
            raise AssertionError(f"no `ok   stamps-staged` line followed by a lane:\n{out}")
        return m.group(1)

    def test_a_passing_commit_shows_the_re_read_list(self) -> None:
        """AC1. MUTANT: `verdict()` printing a lane's output only on FAIL - the lane reads `ok`
        and the list is never shown."""
        rc, out = self._commit_probe("value = 1 + 1", "value = 2")
        self.assertEqual(0, rc, f"an advisory refused the commit:\n{out}")
        block = self._lane_block(out)
        self.assertIn(REREAD, block, f"the re-read list is not beneath the lane:\n{out}")
        self.assertIn(f"US0001 AC1: {WORDS}", block)
        self.assertIn(f"pytest {PROBE}::T::test_x", block)

    def test_a_commit_touching_no_stamped_test_prints_only_ok(self) -> None:
        """AC2. MUTANT: printing every lane's output on success - the lane's own summary line
        and the chatty stubs' output appear. The edit is to `test_y`, which nothing stamps, in
        the file a stamp names, so the lane really judges the staged file."""
        self.assertTrue(CHATTY_TOOLS, "no pre-commit-only lane to stub as chatty")
        rc, out = self._commit_probe("self.assertIn('a', 'abc')", "self.assertIn('b', 'abc')")
        self.assertEqual(0, rc, f"a clean commit was refused:\n{out}")
        self.assertEqual("", self._lane_block(out),
                         f"the stamps-staged lane printed more than `ok`:\n{out}")
        self.assertNotIn(REREAD, out)
        self.assertNotIn("CHATTY-SUCCESS-OUTPUT", out,
                         "another lane's success output is now printed")


if __name__ == "__main__":
    unittest.main()
