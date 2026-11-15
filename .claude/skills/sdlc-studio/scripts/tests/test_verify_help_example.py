"""help/verify.md's example `run` and `report` output carries every field the tool prints.

The examples are compared with what `verify_ac.py run` and `verify_ac.py report` print for a
fixture project: each example story line must carry the same `name=` fields, in the same order,
as the tool's story line, and each example must close with a `total:` line carrying the tool's
total fields and summing its own story lines. A planted example missing a field fails beside
the live page.
"""
from __future__ import annotations

# test-census-subject: .claude/skills/sdlc-studio/help/verify.md

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import verify_ac  # noqa: E402

HELP = HERE.parent.parent / "help" / "verify.md"
HEAD = "# {uid}: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n\n## Acceptance Criteria\n\n"
_FIELD = re.compile(r"\b(\w+)=")
#: A `run` story line, and a `report` story line.
_RUN_STORY = re.compile(r"^\[(?:APL|DRY)\] \S+: (ac=.*)$", re.M)
_REPORT_STORY = re.compile(r"^\S+: (ac=.*)$", re.M)
_TOTAL = re.compile(r"^total: (.*)$", re.M)


def fields(line: str) -> list[str]:
    """The `name=` field names of one output line, in order."""
    return _FIELD.findall(line)


def example(text: str, heading: str) -> str:
    """The first `text` fence after `**Output example:**` in the `### heading` section."""
    section = re.search(rf"^### {re.escape(heading)}\s*$(.*?)(?=^### |^## |\Z)", text, re.M | re.S)
    if not section:
        return ""
    block = re.search(r"\*\*Output example:\*\*\s*```text\n(.*?)```", section.group(1), re.S)
    return block.group(1) if block else ""


def example_problems(block: str, story: re.Pattern, want_story: list[str],
                     want_total: list[str]) -> list[str]:
    """Each way an example block disagrees with the fields the tool prints."""
    problems = []
    stories = story.findall(block)
    if not stories:
        problems.append("the example has no story line")
    for line in stories:
        if fields(line) != want_story:
            problems.append(f"story line fields {fields(line)} != the tool's {want_story}")
    totals = _TOTAL.findall(block)
    if len(totals) != 1:
        return problems + [f"the example has {len(totals)} total: lines, want 1"]
    if fields(totals[0]) != want_total:
        problems.append(f"total: fields {fields(totals[0])} != the tool's {want_total}")
    values = dict(re.findall(r"\b(\w+)=(\d+)", totals[0]))
    for name, value in values.items():
        summed = sum(int(v) for line in stories for k, v in re.findall(r"\b(\w+)=(\d+)", line)
                     if k == name)
        if summed != int(value):
            problems.append(f"total: {name}={value} but the story lines sum to {summed}")
    return problems


class VerifyHelpExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "present.txt").write_text("here\n", encoding="utf-8")
            bugs = root / "sdlc-studio" / "bugs"
            bugs.mkdir(parents=True)
            for uid, verify in (("BG9201", "file present.txt"), ("BG9202", "file missing.txt")):
                (bugs / f"{uid}-x.md").write_text(
                    HEAD.format(uid=uid) + f"- [ ] **AC1** it holds\n  - **Verify:** {verify}\n",
                    encoding="utf-8")
            cls.run_out = cls._main(["run", "--root", str(root), "--ids", "BG9201,BG9202"])
            cls.report_out = cls._main(
                ["report", "--report", str(root / "sdlc-studio" / ".local" / "verify-report.json")])
        cls.text = HELP.read_text(encoding="utf-8")

    @staticmethod
    def _main(argv: list[str]) -> str:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            verify_ac.main(argv)
        return out.getvalue()

    def _tool(self, out: str, story: re.Pattern) -> tuple[list[str], list[str]]:
        stories, totals = story.findall(out), _TOTAL.findall(out)
        self.assertTrue(stories, out)
        self.assertEqual(len(totals), 1, out)
        return fields(stories[0]), fields(totals[0])

    def test_the_tool_prints_the_fields_the_criterion_names(self) -> None:
        for out, story in ((self.run_out, _RUN_STORY), (self.report_out, _REPORT_STORY)):
            want_story, want_total = self._tool(out, story)
            for name in ("unspecified", "partly_skipped"):
                self.assertIn(name, want_story)
                self.assertIn(name, want_total)

    def test_the_run_example_matches_what_run_prints(self) -> None:
        want_story, want_total = self._tool(self.run_out, _RUN_STORY)
        block = example(self.text, "run")
        self.assertTrue(block, "help/verify.md has no run output example")
        self.assertEqual(example_problems(block, _RUN_STORY, want_story, want_total), [])

    def test_the_report_example_matches_what_report_prints(self) -> None:
        want_story, want_total = self._tool(self.report_out, _REPORT_STORY)
        block = example(self.text, "report")
        self.assertTrue(block, "help/verify.md has no report output example")
        self.assertEqual(example_problems(block, _REPORT_STORY, want_story, want_total), [])

    def test_a_planted_stale_example_is_refused(self) -> None:
        want_story, want_total = self._tool(self.run_out, _RUN_STORY)
        good = ("[APL] US0001-a.md: ac=2 pass=1 fail=1 partly_skipped=0 manual=0 unspecified=0 "
                "changes=1\ntotal: pass=1 fail=1 partly_skipped=0 manual=0 unspecified=0\n")
        self.assertEqual(example_problems(good, _RUN_STORY, want_story, want_total), [])
        stale = good.replace(" partly_skipped=0 manual=0 unspecified=0 changes", " manual=0 changes")
        self.assertEqual(len(example_problems(stale, _RUN_STORY, want_story, want_total)), 1)
        no_total = good.split("total:")[0]
        self.assertIn("the example has 0 total: lines, want 1",
                      example_problems(no_total, _RUN_STORY, want_story, want_total))
        wrong_sum = good.replace("total: pass=1", "total: pass=7")
        self.assertIn("total: pass=7 but the story lines sum to 1",
                      example_problems(wrong_sum, _RUN_STORY, want_story, want_total))
        self.assertEqual(example("## Other\n\n### run\n\nNo example.\n", "run"), "")


if __name__ == "__main__":
    unittest.main()
