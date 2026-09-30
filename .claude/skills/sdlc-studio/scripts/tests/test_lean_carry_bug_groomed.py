"""BG0829: a unit carried at the review cap is filed as a bug `sprint plan` can take, and the
carry's escalation claims no notification that nothing sends.

`critic.carry_at_cap` filed the carried bug with two tool-derived criteria restating its summary
and no `Verify:` line, so `sprint.py breakdown` reported it ungroomed (derived-only) and the next
plan refused it until it was groomed by hand. The escalation printed on every carry said "The
operator is NOTIFIED", and nothing notifies anyone.

Driven through `critic.py record` and `sprint.py breakdown`, the shipped entry points, in a
throwaway workspace. Nothing reads this repository's own config, ledgers or `.local` state.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import sprint  # noqa: E402
import verify_ac  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

UNIT = "US0001"
#: The unit's two criteria and their verifiers: the redelivery must still pass them.
CRITERIA = (("the parser keeps every row", "pytest tests/test_unit.py::UnitTests::test_rows_kept"),
            ("the last row survives a trailing newline",
             "pytest tests/test_unit.py::UnitTests::test_last_row"))
#: The round-2 REJECT's two findings, origin tags kept.
FINDINGS = ("[new] the parser still drops the last row",
            "[new] AC2 test passes with the fix removed")


def _workspace(d: str) -> Path:
    root = Path(d)
    stories = root / "sdlc-studio" / "stories"
    stories.mkdir(parents=True)
    acs = "".join(f"- [ ] **AC{n}** {text}\n  - **Verify:** {sel}\n"
                  for n, (text, sel) in enumerate(CRITERIA, 1))
    (stories / f"{UNIT}-a-unit.md").write_text(
        f"# {UNIT}: a unit\n\n> **Status:** Review\n> **Epic:** EP0001\n> **Points:** 3\n"
        f"> **Affects:** src/unit.py\n\n## Acceptance Criteria\n\n{acs}", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src" / "unit.py").write_text("x = 1\n", encoding="utf-8")
    (root / "sdlc-studio" / ".config.yaml").write_text(
        "review:\n  require_brief_provenance: false\n", encoding="utf-8")
    return root


def _run(module, argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = module.main(argv)
    return rc, buf.getvalue()


def _reject(root: Path, issues: str) -> tuple[int, str]:
    return _run(critic, ["record", "--unit", UNIT, "--verdict", "REJECT", "--reviewer", "rev-a",
                         "--author", "builder", "--issues", issues, "--root", str(root)])


class CarryBugGroomedTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env

    def _carry(self, root: Path) -> tuple[str, str]:
        """Carry the unit at the cap in an open run: the bug's id and the round-2 output."""
        run_state.open_run(root, batch=[UNIT, "US0002"], goal="g")
        self.assertEqual(0, _reject(root, "[new] the parser drops a row")[0])
        rc, out = _reject(root, "; ".join(FINDINGS))
        self.assertEqual(0, rc, out)
        bugs = list((root / "sdlc-studio" / "bugs").glob("BG*.md"))
        self.assertEqual(1, len(bugs), f"premise: the carry filed no bug:\n{out}")
        return sdlc_md.extract_record_id(bugs[0].stem), out

    def test_the_carried_bug_is_filed_groomed(self) -> None:
        """AC1. MUTANTS: HEAD's tool-derived criteria (breakdown: derived-only); the findings
        alone, with no `Verify:` line (breakdown: no-verifier); the unit's criteria alone (the
        findings are lost); the unit's criteria without their verifiers; all the findings as one
        criterion; the unit's Points or Affects dropped."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            bug, _out = self._carry(root)
            text = sdlc_md.read_text_safe(sdlc_md.find_by_id(root, bug)[0])
            blocks = verify_ac.criteria_blocks(text)
            for finding in FINDINGS:
                naming = [b for b in blocks if finding in b.title]
                self.assertEqual(1, len(naming), f"no criterion of its own names {finding!r}:"
                                                 f"\n{text}")
            for criterion, selector in CRITERIA:
                owned = [b for b in blocks if criterion in b.title]
                self.assertEqual(1, len(owned), f"the unit's {criterion!r} is not carried:\n{text}")
                self.assertEqual(selector, owned[0].verifier,
                                 f"{criterion!r} lost its Verify line:\n{text}")
            self.assertEqual(len(FINDINGS) + len(CRITERIA), len(blocks), text)
            self.assertEqual("3", sdlc_md.extract_field(text, "Points"))
            self.assertEqual("src/unit.py", sdlc_md.extract_field(text, "Affects"))
            # The reader `sprint plan` refuses on, through its own command.
            rc, out = _run(sprint, ["breakdown", "--bugs", "Open", "--root", str(root)])
            self.assertRegex(out, r"breakdown: 1 unit\(s\), 0 ungroomed", out)
            self.assertNotIn(f"{bug}   lacks", out)
            self.assertEqual(0, rc, out)

    def test_no_notification_is_claimed(self) -> None:
        """AC2. MUTANTS: HEAD's "The operator is NOTIFIED"; a line that drops the claim but
        names nowhere the operator reads the escalation."""
        with tempfile.TemporaryDirectory() as d:
            root = _workspace(d)
            bug, out = self._carry(root)
            lines = [ln for ln in out.splitlines() if "ESCALATED" in ln]
            self.assertEqual(1, len(lines), f"premise: the carry printed no escalation:\n{out}")
            self.assertNotIn("notified", out.lower(), "a notification is claimed that nothing sends")
            self.assertIn("sprint report", lines[0], f"no place the operator reads it: {lines[0]}")
            self.assertIn(bug, lines[0], f"the bug holding the findings is not named: {lines[0]}")


if __name__ == "__main__":
    unittest.main()
