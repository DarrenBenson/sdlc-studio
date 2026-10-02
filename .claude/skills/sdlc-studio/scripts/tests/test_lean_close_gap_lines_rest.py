"""BG0915: retro-validate and the gate's unattributed path hand over only their failures.

`close_known_issues_from` turns every detail line of a failed close step into a known issue.
BG0894 and BG0908 narrowed retro-extract and review-coverage to their failures; two steps were
left: retro-validate carried the validator's `retro RETRO0001: FAIL` header beside the real
failure, and a gate failure no lane could be attributed to carried the gate's whole output and
the close's prose. Each now prints the header, output and prose for the operator and hands over
only the failure. Retro-extract's extract-failed branch (the CLI exits non-zero) is pinned too.

Each test runs the real `sprint.py close` with the step under test real and every other step
stubbed green (`test_lean_close._close`), and reads the known issues off the filed page.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

#: A gate verdict whose one failing lane the close's parser cannot place (no `name: why`).
UNPARSED = "  [FAIL] a lane whose format moved"


class CloseGapLinesRestTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        lean._fixture(self.root)
        self.retro = self.root / "sdlc-studio" / "retros" / "RETRO0001-lean.md"

    def _gaps(self, step: str, *real: str) -> tuple[list[str], str]:
        """The `step` rows on the filed page, and what the close printed."""
        rc, out, err = lean._close(self.root, real=real or (step,))
        self.assertEqual(0, rc, out + err)
        rows = lean._known_issue_rows(self.root, lean._read(self.root)["report"])
        return [r["issue_detail"] for r in rows if r["issue_id"] == step], out + err

    def test_retro_validate_hands_over_only_its_failure(self) -> None:
        """AC1. MUTANT: HEAD, whose failed step hands over the validator's whole output, so the
        page lists `retro RETRO0001: FAIL` as a close gap beside the missing section. The
        control: the failure itself is still handed over, and the header is still printed."""
        self.retro.write_text(self.retro.read_text(encoding="utf-8") + (
            "\n## What went well\n\n- it closed\n\n## What was hard / what stalled\n\n"
            "- nothing\n"), encoding="utf-8")       # only `## Actions raised` is missing
        gaps, printed = self._gaps("retro-validate")
        self.assertEqual(1, len(gaps), gaps)
        self.assertIn("missing section '## Actions raised'", gaps[0])
        self.assertFalse(any("RETRO0001: FAIL" in g for g in gaps), gaps)
        self.assertIn("retro RETRO0001: FAIL", printed)

    def test_unattributed_gate_hands_over_only_its_failure(self) -> None:
        """AC2. MUTANT: HEAD, whose unattributed path hands over the gate's every output line
        and the close's own prose, so one unparsed lane reads as several close gaps. The
        control: the lane's failure line is still handed over, and the output and the prose are
        still printed."""
        def red_gate(argv):
            print("gate: conformance ok\n" + UNPARSED + "\ngate: FAIL")
            return 1

        with unittest.mock.patch.object(lean._live("gate"), "main", red_gate):
            gaps, printed = self._gaps("gate")
        self.assertEqual([UNPARSED.strip()], gaps)
        self.assertIn("gate: conformance ok", printed)
        self.assertIn("could not be attributed", printed)

    def test_extract_failed_is_one_known_issue(self) -> None:
        """AC3. MUTANT: drop the `rc != 0` check in `_close_retro_extract`, so an extract that
        failed passes the step and the page carries no known issue for it. The control is the
        count: one row, naming the failure, not one per line the step printed."""
        self.retro.write_text(self.retro.read_text(encoding="utf-8").replace(
            "- learned a thing", "- [LC-999] a class the store does not hold"),
            encoding="utf-8")
        gaps, _printed = self._gaps("retro-extract")
        self.assertEqual(1, len(gaps), gaps)
        self.assertIn("LC-999 is not a class", gaps[0])


if __name__ == "__main__":
    unittest.main()
