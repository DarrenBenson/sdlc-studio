"""BG0967: a shell command in a finding's Steps to Reproduce is filed byte-identical inside a
fenced block, so the repro a reviewer copies still runs, while the prose around it is still
markdown-safed.

Each finding is filed through a shipped CLI (`file_finding.py file`, `artifact.py new`) into a
throwaway fixture root, with the steps supplied in a `--fields-file` document so no value crosses
a shell on the way in.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding_steps_commands.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
import file_finding  # noqa: E402
import gitutil  # noqa: E402 - confined git, so an inherited GIT_DIR cannot steer the lookup

FILER = SCRIPTS / "file_finding.py"
CREATOR = SCRIPTS / "artifact.py"

#: The bug's own repro: identifiers the old safing back-ticked inside the double quotes, where a
#: backtick is command substitution.
CMD = 'python3 -c "import sys; from lib import sdlc_md; print(sdlc_md.__name__)"'


#: Prose, a prompted command, a numbered command, an author's fence and an unclosed one: every
#: shape the steps safing writes, filed together so markdownlint judges them side by side.
MIXED = (f"From the scripts folder:\n$ {CMD}\nThe import_error names it.\n\n"
         "1. python3 -m pytest -q x_test.py  \n2. Read the my_output line\n\n"
         "```sh\nexport A_B=1; my_tool --x_y\n```\nthen check _a and _b.\n```\npython3 y_z.py")


def _markdownlint() -> str | None:
    """The markdownlint the repo's lane runs: on PATH, in this checkout, or in the main checkout
    this worktree hangs off (a worktree carries no `node_modules` of its own)."""
    found = shutil.which("markdownlint")
    if found:
        return found
    roots = [SCRIPTS.parents[3]]
    common = gitutil.git(["rev-parse", "--path-format=absolute", "--git-common-dir"], SCRIPTS,
                         check=False, text=True)
    if common.returncode == 0 and common.stdout.strip():
        roots.append(Path(common.stdout.strip()).parent)
    for root in roots:
        cand = root / "node_modules" / ".bin" / "markdownlint"
        if cand.exists():
            return str(cand)
    return None


def _section(body: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n\n(.*?)\n\n## ", body, re.S | re.M)
    if not m:
        raise AssertionError(f"no '## {heading}' section in:\n{body}")
    return m.group(1)


class _Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "thing.py").write_text("", encoding="utf-8")

    def tearDown(self) -> None:
        self._td.cleanup()

    def _doc(self, **fields) -> str:
        p = self.root / "finding.json"
        p.write_text(json.dumps(fields), encoding="utf-8")
        return str(p)

    def file(self, steps: str, type_: str = "bug") -> str:
        """File one finding through `file_finding.py file`; return the written body."""
        extra = (["--severity", "low", "--points", "1", "--ac", "the repro runs",
                  "--verify", "pytest tests/test_x.py"] if type_ == "bug"
                 else ["--priority", "low", "--ac", "the repro runs"])
        r = subprocess.run(
            [sys.executable, str(FILER), "file", "--root", str(self.root), "--type", type_,
             "--title", "a repro command", *extra, "--affects", "src/thing.py",
             "--fields-file", self._doc(summary="s", steps=steps, fix="f")],
            capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, f"the filer refused the fixture:\n{r.stdout}{r.stderr}")
        folder = "bugs" if type_ == "bug" else "change-requests"
        return next(p for p in (self.root / "sdlc-studio" / folder).glob("*.md")
                    if p.name != "_index.md").read_text(encoding="utf-8")

    def create(self, steps: str, *template: str) -> str:
        """Create one bug through `artifact.py new`; return the written body."""
        r = subprocess.run(
            [sys.executable, str(CREATOR), "new", "--type", "bug", "--title", "a repro command",
             "--root", str(self.root), *template, "--fields-file",
             self._doc(severity="Low", points=1, affects="src/thing.py", summary="s",
                       steps=steps, fix="f")],
            capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, f"artifact new refused the fixture:\n{r.stdout}{r.stderr}")
        return next(p for p in (self.root / "sdlc-studio" / "bugs").glob("*.md")
                    if p.name != "_index.md").read_text(encoding="utf-8")

    def batch(self, steps: str) -> str:
        """Create one bug through `artifact.py batch`; return the written body."""
        spec = self.root / "batch.json"
        spec.write_text(json.dumps([{"title": "a repro command", "severity": "Low", "points": 1,
                                     "affects": "src/thing.py", "summary": "s", "steps": steps,
                                     "fix": "f"}]), encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CREATOR), "batch", "--type", "bug", "--spec", str(spec),
             "--root", str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, f"artifact batch refused the fixture:\n{r.stdout}{r.stderr}")
        return next(p for p in (self.root / "sdlc-studio" / "bugs").glob("*.md")
                    if p.name != "_index.md").read_text(encoding="utf-8")


class CommandSurvivesFilingTests(_Fixture):
    """AC1: through every path that writes a Steps to Reproduce section."""

    #: The creators label the bare fence the safing writes when they write the file (MD040).
    FENCED = f"```text\n{CMD}\n```"

    def test_command_survives_filing_byte_identical_in_a_fence(self) -> None:
        self.assertEqual(_section(self.file(CMD), "Steps to Reproduce"), self.FENCED)

    def test_command_survives_filing_and_still_runs_when_copied(self) -> None:
        """Copy the fenced block out of the filed bug and run it where the repro says."""
        steps = _section(self.file(CMD), "Steps to Reproduce")
        m = re.fullmatch(r"```text\n(.*)\n```", steps, re.S)
        self.assertIsNotNone(m, steps)
        r = subprocess.run(["bash", "-c", m.group(1)], cwd=SCRIPTS, capture_output=True,
                           text=True, check=False)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "lib.sdlc_md"), r.stderr)

    def test_command_survives_filing_through_artifact_new(self) -> None:
        self.assertEqual(_section(self.create(CMD), "Steps to Reproduce"), self.FENCED)

    def test_command_survives_filing_through_artifact_new_full_template(self) -> None:
        body = self.create(CMD, "--template", "full")
        self.assertIn(f"## Steps to Reproduce\n\n{self.FENCED}\n", body)

    def test_command_survives_filing_through_artifact_batch(self) -> None:
        self.assertEqual(_section(self.batch(CMD), "Steps to Reproduce"), self.FENCED)

    def test_command_survives_filing_on_a_cr_whose_steps_are_landed(self) -> None:
        """A CR has no Steps section of its own: the lander appends one, safed the same way."""
        self.assertEqual(_section(self.file(CMD, "cr"), "Steps to Reproduce"), self.FENCED)

    def test_command_survives_filing_beside_prose_and_the_file_passes_markdownlint(self) -> None:
        """Every shape at once, through the filer (whose drop guard reads the author's letters
        and numbers in order) and through markdownlint under the skill's own config."""
        body = self.file(MIXED)
        self.assertIn(f"From the scripts folder:\n\n```text\n{CMD}\n```\n\nThe `import_error`",
                      body)
        lint = _markdownlint()
        if lint is None:
            self.skipTest("markdownlint is not installed (npm install) - the lint lane enforces this")
        path = next((self.root / "sdlc-studio" / "bugs").glob("BG*.md"))
        r = subprocess.run([lint, "-c", str(SCRIPTS.parent / ".markdownlint.json"), str(path)],
                           capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


class StepsShapesTests(unittest.TestCase):
    """The steps safing over each shape a repro takes, at the function the creators share."""

    @staticmethod
    def safe(text: str) -> str:
        return file_finding._steps_safe(text)

    def test_prose_around_a_command_is_still_safed_and_the_fence_stands_apart(self) -> None:
        steps = f"From the scripts folder:\n{CMD}\nThe import_error names it."
        self.assertEqual(self.safe(steps),
                         f"From the scripts folder:\n\n```\n{CMD}\n```\n\n"
                         "The `import_error` names it.")

    def test_a_prompt_is_dropped_so_the_fence_runs_as_pasted(self) -> None:
        """MD014 refuses a block whose every command shows a `$`, and a pasted `$` does not run;
        the indentation before the prompt is kept."""
        self.assertEqual(self.safe(f"$ {CMD}\n  $  git status"),
                         f"```\n{CMD}\n  git status\n```")

    def test_a_blank_line_already_beside_a_command_is_not_doubled(self) -> None:
        steps = f"Run:\n\n{CMD}\n\nThen read it."
        self.assertEqual(self.safe(steps), f"Run:\n\n```\n{CMD}\n```\n\nThen read it.")

    def test_two_commands_apart_keep_one_blank_line_between_their_fences(self) -> None:
        self.assertEqual(self.safe(f"{CMD}\n\ngit status"),
                         f"```\n{CMD}\n```\n\n```\ngit status\n```")

    def test_consecutive_command_lines_share_one_fence(self) -> None:
        steps = f"git status\n{CMD}"
        self.assertEqual(self.safe(steps), f"```\ngit status\n{CMD}\n```")

    def test_a_fence_beside_an_authors_fence_stands_apart(self) -> None:
        block = "```sh\nexport A_B=1\n```"
        self.assertEqual(self.safe(f"{block}\n{CMD}"), f"{block}\n\n```\n{CMD}\n```")

    def test_an_authors_fenced_block_is_left_verbatim(self) -> None:
        block = f"```sh\n{CMD}\nexport A_B=1\n```"
        self.assertEqual(self.safe(f"Repro:\n\n{block}\nthen read_me now"),
                         f"Repro:\n\n{block}\n\nthen `read_me` now")

    def test_a_tilde_fence_closes_only_on_its_own_marker(self) -> None:
        block = f"~~~~\n```\n{CMD}\n~~~\n~~~~"
        self.assertEqual(self.safe(block), block)

    def test_a_fence_line_carrying_an_info_string_does_not_close_the_block(self) -> None:
        """Read by the shared fence reader: a closer may carry nothing after its run."""
        block = f"```\n{CMD}\n```sh\nexport A_B=1\n```"
        self.assertEqual(self.safe(f"{block}\nthen read_me now"), f"{block}\n\nthen `read_me` now")

    def test_inline_code_in_triple_backticks_is_prose_not_a_fence(self) -> None:
        """CommonMark: a backtick run with another backtick after it on the line opens no fence,
        so it is neither kept verbatim nor closed at the end."""
        self.assertEqual(self.safe("```x_y``` then a_b"), "```x_y``` then `a_b`")

    def test_an_unclosed_fence_is_closed_so_it_cannot_swallow_the_next_section(self) -> None:
        self.assertEqual(self.safe(f"```\n{CMD}"), f"```\n{CMD}\n```")
        self.assertEqual(self.safe(f"````text\n{CMD}"), f"````text\n{CMD}\n````")

    def test_a_fence_outlasts_a_backtick_run_inside_the_command(self) -> None:
        cmd = "python3 -c \"print('```')\""
        self.assertEqual(self.safe(cmd), f"````\n{cmd}\n````")

    def test_a_command_that_is_a_list_items_body_is_code_spanned_in_place(self) -> None:
        steps = f"1. {CMD}\n2. Read the my_output line"
        self.assertEqual(self.safe(steps), f"1. `{CMD}`\n2. Read the `my_output` line")

    def test_consecutive_command_items_each_keep_their_marker(self) -> None:
        self.assertEqual(self.safe("1. git status\n  * $ python3 a_b.py  "),
                         "1. `git status`\n  * `python3 a_b.py`")

    def test_a_list_items_command_holding_a_backtick_is_left_to_the_prose_pass(self) -> None:
        """A single-backtick span cannot hold a backtick, so that body is safed as prose."""
        self.assertEqual(self.safe("- grep -n `x` my_file"), "- grep -n `x` `my_file`")

    def test_a_list_item_is_never_fenced_even_with_a_shell_operator(self) -> None:
        self.assertEqual(self.safe("- run a_b && c"), "- `run a_b && c`")

    def test_a_line_that_only_quotes_a_command_in_a_code_span_is_prose(self) -> None:
        steps = "See `git log && true` in snake_case output"
        self.assertEqual(self.safe(steps), "See `git log && true` in `snake_case` output")

    def test_a_prose_only_value_is_safed_exactly_as_before(self) -> None:
        steps = "1. Open `a\nb` then read x_y\n> **Waived:** yes"
        self.assertEqual(self.safe(steps), file_finding._prose_safe(steps))

    def test_only_the_steps_field_takes_the_command_rule(self) -> None:
        self.assertEqual(file_finding._field_safe("steps", CMD), f"```\n{CMD}\n```")
        self.assertEqual(file_finding._field_safe("summary", CMD), file_finding._prose_safe(CMD))


if __name__ == "__main__":
    unittest.main()
