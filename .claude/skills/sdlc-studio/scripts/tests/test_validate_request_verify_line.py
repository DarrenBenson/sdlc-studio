"""BG1017: `validate.py check` warned pseudo-verify on the `- **Verify:**` line the finding filer
writes beneath a request's criterion, because `file_finding.scan_prose_acs` judged every line of
the criteria section. Only a criterion's prose is judged now, as the filer's own refusal judges
it: the line beneath a criterion is its check and draws no warning, and a command written into
the criterion's own prose still does, advising that line.

Each case files or writes a request in a throwaway root and runs the shipped CLI
(`validate.py check --file`) over it.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate_request_verify_line.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/validate.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
FILER = SCRIPTS / "file_finding.py"
VALIDATOR = SCRIPTS / "validate.py"

COMMAND = "rg -qi effort sprint.py"


def _file_cr(root: Path, *extra: str) -> Path:
    """One CR filed through the CLI with a criterion and its `verify` entry."""
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "thing.py").write_text("", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(FILER), "file", "--type", "cr", "--root", str(root), "--title",
         "a request", "--summary", "s", "--priority", "Low", "--size", "S", "--affects",
         "src/thing.py", "--author", "Tess Tester", *extra],
        capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise AssertionError(f"the filer refused the fixture request:\n{r.stdout}{r.stderr}")
    return next((root / "sdlc-studio" / "change-requests").glob("CR*.md"))


def _write_cr(root: Path, criteria: str) -> Path:
    path = root / "sdlc-studio" / "change-requests" / "CR0001-x.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# CR-0001: x\n\n> **Status:** Proposed\n> **Priority:** P3\n\n## Summary\n\ns\n\n"
        f"## Acceptance Criteria\n\n{criteria}\n\n## Revision History\n\n"
        "| Date | Author | Change |\n| --- | --- | --- |\n| 2026-07-14 | a | Raised |\n",
        encoding="utf-8")
    return path


def _pseudo(root: Path, path: Path) -> list[dict]:
    """The pseudo-verify violations `validate.py check --file` reports for `path`."""
    r = subprocess.run([sys.executable, str(VALIDATOR), "check", "--file", str(path), "--root",
                        str(root), "--format", "json"], capture_output=True, text=True,
                       check=False)
    return [v for v in json.loads(r.stdout)["violations"] if v["rule"] == "pseudo-verify"]


class RequestVerifyLineTests(unittest.TestCase):

    def setUp(self) -> None:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.root = Path(td.name)

    def test_only_a_command_in_criterion_prose_is_warned(self) -> None:
        """AC1. Mutants: `scan_prose_acs` judging every line of the section (the filer's own
        line warned); an exemption keyed on the word Verify, so the prose command goes quiet
        too."""
        filed = _file_cr(self.root, "--ac", "it holds", "--verify",
                         "pytest tests/test_x.py::T::test_y")
        self.assertIn("  - **Verify:** pytest tests/test_x.py::T::test_y", filed.read_text())
        self.assertEqual([], _pseudo(self.root, filed))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            prose = _write_cr(root, f"- [ ] sprint.py reads the Effort field. Verify: {COMMAND}")
            (hit,) = _pseudo(root, prose)
            self.assertEqual("warning", hit["severity"])
            self.assertIn(COMMAND, hit["message"])
            self.assertIn("`- **Verify:**` line beneath", hit["message"])

    def test_a_verify_line_not_beneath_a_criterion_is_still_judged(self) -> None:
        """The near misses of the exemption. Mutants: any `Verify` bullet exempt; an item
        flush with the margin taken as a child; the criterion's own line exempt because a child
        Verify follows it; a paragraph between the criterion and the line leaving it a child; a child item that is not
        the bold `Verify:` item exempt."""
        with tempfile.TemporaryDirectory() as d:
            for name, body in (
                    ("flush", f"- [ ] it works\n- **Verify:** {COMMAND}"),
                    ("own line", f"- [ ] it works. Verify: {COMMAND}\n"
                                 "  - **Verify:** pytest tests/test_x.py::T::test_y"),
                    ("after a paragraph", f"- [ ] it works\n\nplain words\n\n"
                                          f"  - **Verify:** {COMMAND}"),
                    ("no criterion yet", f"  - **Verify:** {COMMAND}"),
                    ("child without the bold marker", f"- [ ] it works\n  - Verify: {COMMAND}")):
                with self.subTest(name):
                    root = Path(d) / name.replace(" ", "-")
                    self.assertEqual(1, len(_pseudo(root, _write_cr(root, body))), body)

    def test_a_verify_line_beneath_a_criterion_is_not_judged_whatever_it_holds(self) -> None:
        """The exempt shape, in the forms a request carries: a labelled criterion, a ticked
        one, a numbered one, and a second child line; and no `Verify:` word in any prose."""
        with tempfile.TemporaryDirectory() as d:
            for name, body in (
                    ("labelled", f"- [ ] **AC1** it works\n  - **Verify:** {COMMAND}"),
                    ("ticked", f"- [x] it works\n  - **Verify:** {COMMAND}"),
                    ("numbered", f"1. it works\n   - **Verify:** {COMMAND}"),
                    ("second child", f"- [ ] it works\n  - **Verify:** pytest a.py::B::c\n"
                                     f"  - **Verify:** {COMMAND}")):
                with self.subTest(name):
                    root = Path(d) / name.replace(" ", "-")
                    self.assertEqual([], _pseudo(root, _write_cr(root, body)), body)

    def test_a_missing_empty_or_binary_file_is_not_a_crash(self) -> None:
        """The reader's malformed inputs reach the same lane: an empty criteria section, an
        empty file and a file that is not UTF-8 each end in a verdict, never a traceback."""
        empty_section = _write_cr(self.root, "")
        self.assertEqual([], _pseudo(self.root, empty_section))
        for name, data in (("empty.md", b""), ("binary.md", b"\xff\xfe## Acceptance Criteria\n")):
            path = self.root / "sdlc-studio" / "change-requests" / name
            path.write_bytes(data)
            r = subprocess.run([sys.executable, str(VALIDATOR), "check", "--file", str(path),
                                "--root", str(self.root), "--format", "json"],
                               capture_output=True, text=True, check=False)
            self.assertNotIn("Traceback", r.stderr, name)


if __name__ == "__main__":
    unittest.main()
