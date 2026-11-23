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

#: The reviewer's commands that run over more than one line, each run from the scripts folder:
#: a quoted program, a here-document and a backslash continuation.
MULTI = {"quoted": 'python3 -c "\nfrom lib import sdlc_md\nprint(sdlc_md.__name__)\n"',
         "heredoc": "python3 - <<'EOF'\nfrom lib import sdlc_md\nprint(sdlc_md.__name__)\nEOF",
         "backslash": 'python3 -c \\\n  "from lib import sdlc_md; print(sdlc_md.__name__)"'}

#: The reviewer's backslash-continued pytest, which has no test file here to run.
PYTEST = "python3 -m pytest -q \\\n  tests/test_x.py::test_my_case"


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

    def _clear(self) -> None:
        for p in (self.root / "sdlc-studio" / "bugs").glob("*.md"):
            p.unlink()

    def _lint(self, body: str) -> None:
        """markdownlint over the filed bug under the skill's config and the repository's own,
        the one this repository's markdown lane runs over a filed bug."""
        lint = _markdownlint()
        if lint is None:
            self.skipTest("markdownlint is not installed (npm install) - the lint lane enforces this")
        path = next((self.root / "sdlc-studio" / "bugs").glob("BG*.md"))
        self.assertEqual(path.read_text(encoding="utf-8"), body)
        repo = SCRIPTS.parents[3] / ".markdownlint.json"  # absent from an installed copy
        for config in (SCRIPTS.parent / ".markdownlint.json", *[repo][:repo.exists()]):
            r = subprocess.run([lint, "-c", str(config), str(path)], capture_output=True,
                               text=True, check=False)
            self.assertEqual(r.returncode, 0, f"{config}:\n{r.stdout}{r.stderr}")

    def _doc(self, **fields) -> str:
        p = self.root / "finding.json"
        p.write_text(json.dumps(fields), encoding="utf-8")
        return str(p)

    def file(self, steps: str, type_: str = "bug", fix: str = "f") -> str:
        """File one finding through `file_finding.py file`; return the written body."""
        extra = (["--severity", "low", "--points", "1", "--ac", "the repro runs",
                  "--verify", "pytest tests/test_x.py"] if type_ == "bug"
                 else ["--priority", "low", "--ac", "the repro runs"])
        r = subprocess.run(
            [sys.executable, str(FILER), "file", "--root", str(self.root), "--type", type_,
             "--title", "a repro command", *extra, "--affects", "src/thing.py",
             "--fields-file", self._doc(summary="s", steps=steps, fix=fix)],
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
                         f"From the scripts folder:\n\n```text\n{CMD}\n```\n\n"
                         "The `import_error` names it.")

    def test_a_prompt_is_dropped_so_the_fence_runs_as_pasted(self) -> None:
        """MD014 refuses a block whose every command shows a `$`, and a pasted `$` does not run;
        the indentation before the prompt is kept."""
        self.assertEqual(self.safe(f"$ {CMD}\n  $  git status"),
                         f"```text\n{CMD}\n  git status\n```")

    def test_a_blank_line_already_beside_a_command_is_not_doubled(self) -> None:
        steps = f"Run:\n\n{CMD}\n\nThen read it."
        self.assertEqual(self.safe(steps), f"Run:\n\n```text\n{CMD}\n```\n\nThen read it.")

    def test_two_commands_apart_keep_one_blank_line_between_their_fences(self) -> None:
        self.assertEqual(self.safe(f"{CMD}\n\ngit status"),
                         f"```text\n{CMD}\n```\n\n```text\ngit status\n```")

    def test_consecutive_command_lines_share_one_fence(self) -> None:
        steps = f"git status\n{CMD}"
        self.assertEqual(self.safe(steps), f"```text\ngit status\n{CMD}\n```")

    def test_a_fence_beside_an_authors_fence_stands_apart(self) -> None:
        block = "```sh\nexport A_B=1\n```"
        self.assertEqual(self.safe(f"{block}\n{CMD}"), f"{block}\n\n```text\n{CMD}\n```")

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

    def test_an_unclosed_tilde_fence_is_closed_on_its_own_marker(self) -> None:
        self.assertEqual(self.safe(f"~~~\n{CMD}\n\n## Next"), f"~~~\n{CMD}\n\n## Next\n~~~")

    def test_a_fence_outlasts_a_backtick_run_inside_the_command(self) -> None:
        cmd = "python3 -c \"print('```')\""
        self.assertEqual(self.safe(cmd), f"````text\n{cmd}\n````")

    def test_a_line_that_only_quotes_a_command_in_a_code_span_is_prose(self) -> None:
        steps = "See `git log && true` in snake_case output"
        self.assertEqual(self.safe(steps), "See `git log && true` in `snake_case` output")

    def test_a_prose_only_value_is_safed_exactly_as_before(self) -> None:
        steps = "1. Open `a\nb` then read x_y\n> **Waived:** yes"
        self.assertEqual(self.safe(steps), file_finding._prose_safe(steps))

    def test_only_the_steps_field_takes_the_command_rule(self) -> None:
        self.assertEqual(file_finding._field_safe("steps", CMD), f"```text\n{CMD}\n```")
        self.assertEqual(file_finding._field_safe("summary", CMD), file_finding._prose_safe(CMD))


class ListItemCommandTests(unittest.TestCase):
    """A command written as a list item, or on an item's continuation line, is fenced inside the
    item, so the list keeps its numbering."""

    @staticmethod
    def safe(text: str) -> str:
        return file_finding._steps_safe(text)

    def test_a_command_that_is_a_list_items_body_is_fenced_under_its_marker(self) -> None:
        steps = f"1. {CMD}\n2. Read the my_output line"
        self.assertEqual(self.safe(steps), f"1. <!-- -->\n\n   ```text\n   {CMD}\n   ```\n\n"
                                           "2. Read the `my_output` line")

    def test_consecutive_command_items_each_keep_their_marker_and_fence(self) -> None:
        self.assertEqual(self.safe("1. git status\n  * $ python3 a_b.py  "),
                         "1. <!-- -->\n\n   ```text\n   git status\n   ```\n\n"
                         "  * <!-- -->\n\n    ```text\n    python3 a_b.py\n    ```")

    def test_a_list_items_command_holding_a_backtick_is_fenced_not_safed(self) -> None:
        self.assertEqual(self.safe("- grep -n `x` my_file"),
                         "- <!-- -->\n\n  ```text\n  grep -n `x` my_file\n  ```")

    def test_every_list_marker_shape_is_read_as_an_item(self) -> None:
        for marker in ("-", "*", "+", "1.", "1)", "10.", "123456789."):
            pad = " " * (len(marker) + 1)
            with self.subTest(marker=marker):
                self.assertEqual(self.safe(f"{marker} rg -q x"),
                                 f"{marker} <!-- -->\n\n{pad}```text\n{pad}rg -q x\n{pad}```")

    def test_a_ten_digit_number_is_not_a_list_marker(self) -> None:
        self.assertEqual(self.safe("1234567890. rg -q x"), "1234567890. rg -q x")

    def test_a_command_on_an_items_continuation_line_is_fenced_inside_the_item(self) -> None:
        """The reviewer's input: a column-0 fence here ended the list, and the next step was
        refused by MD029."""
        steps = ('1. From the scripts folder run:\n   python3 -c "import sys\\; from lib import '
                 'sdlc_md"\n2. Read the my_output line')
        self.assertEqual(self.safe(steps),
                         '1. From the scripts folder run:\n\n   ```text\n   python3 -c "import '
                         'sys\\; from lib import sdlc_md"\n   ```\n\n2. Read the `my_output` line')

    def test_a_continuation_command_takes_the_items_own_content_column(self) -> None:
        """Two spaces after the marker put the item's text, and so its fence, in column four."""
        self.assertEqual(self.safe("1.  From here run:\n    python3 a_b.py"),
                         "1.  From here run:\n\n    ```text\n    python3 a_b.py\n    ```")

    def test_a_lazy_command_and_the_prose_after_it_are_indented_into_the_item(self) -> None:
        """Unindented lines straight after an item continue it (CommonMark's lazy line); once a
        fence stands between, they are indented to stay in it."""
        steps = "1. Run:\npython3 a_b.py\nthen read c_d\n2. Next"
        self.assertEqual(self.safe(steps), "1. Run:\n\n   ```text\n   python3 a_b.py\n   ```\n\n"
                                           "   then read `c_d`\n2. Next")

    def test_a_lazy_line_after_an_authors_fence_is_left_where_it_was(self) -> None:
        steps = "1. Run:\n\n   ```sh\n   export A=1\n   ```\nthen read c_d"
        self.assertEqual(self.safe(steps), "1. Run:\n\n   ```sh\n   export A=1\n   ```\n\n"
                                           "then read `c_d`")

    def test_a_command_after_a_blank_line_left_of_the_item_is_not_in_it(self) -> None:
        self.assertEqual(self.safe("1. Run it\n\npython3 a_b.py"),
                         "1. Run it\n\n```text\npython3 a_b.py\n```")

    def test_an_authors_fence_left_of_the_item_ends_it_at_once(self) -> None:
        steps = "1. Run it\n```sh\nexport A=1\n```\npython3 a_b.py"
        self.assertEqual(self.safe(steps),
                         "1. Run it\n\n```sh\nexport A=1\n```\n\n```text\npython3 a_b.py\n```")

    def test_a_nested_items_continuation_command_takes_the_nested_column(self) -> None:
        steps = "1. Step\n   - sub step:\n     python3 a_b.py\n\n   python3 c_d.py\n2. Next"
        self.assertEqual(self.safe(steps),
                         "1. Step\n   - sub step:\n\n     ```text\n     python3 a_b.py\n     ```\n\n"
                         "   ```text\n   python3 c_d.py\n   ```\n\n2. Next")

    def test_two_blank_lines_do_not_end_the_item(self) -> None:
        self.assertEqual(self.safe("1. Run it\n\n\n   python3 a_b.py"),
                         "1. Run it\n\n\n   ```text\n   python3 a_b.py\n   ```")

    def test_a_command_outside_a_list_keeps_its_own_indentation(self) -> None:
        self.assertEqual(self.safe("  rg -q x"), "```text\n  rg -q x\n```")

    def test_a_lazy_line_after_a_command_item_is_indented_and_a_blank_line_is_not(self) -> None:
        self.assertEqual(self.safe("1. python3 a_b.py\nthen read c_d\n2. Next"),
                         "1. <!-- -->\n\n   ```text\n   python3 a_b.py\n   ```\n\n   then read `c_d`\n2. Next")
        self.assertEqual(self.safe("1. python3 a_b.py\n\n   then read c_d"),
                         "1. <!-- -->\n\n   ```text\n   python3 a_b.py\n   ```\n\n   then read `c_d`")

    def test_a_deeper_indented_command_is_rebased_on_the_item_column(self) -> None:
        steps = "1. Run:\n      python3 a_b.py\n        | rg x"
        self.assertEqual(self.safe(steps), "1. Run:\n\n   ```text\n   python3 a_b.py\n"
                                           "     | rg x\n   ```")


class MidSentenceTests(unittest.TestCase):
    """What `_command_line` reads as a command: a line opening with one, or carrying a shell
    operator outside its code spans wherever the operator sits (the reviewer's three inputs)."""

    @staticmethod
    def safe(text: str) -> str:
        return file_finding._steps_safe(text)

    def test_a_sentence_carrying_a_shell_operator_is_fenced_whole(self) -> None:
        for line in ("Then run git status && read the my_output line",
                     "The value $(date) is printed in my_log"):
            with self.subTest(line=line):
                self.assertEqual(self.safe(line), f"```text\n{line}\n```")
        item = "1. Run the build && check that my_output is empty"
        self.assertEqual(self.safe(item), "1. <!-- -->\n\n   ```text\n   Run the build && check that my_output "
                                          "is empty\n   ```")

    def test_a_sentence_naming_a_command_with_no_operator_is_prose(self) -> None:
        self.assertEqual(self.safe("Then run git status and read the my_output line"),
                         "Then run git status and read the `my_output` line")


class MetadataGuardTests(unittest.TestCase):
    """A line kept verbatim in a fence still has a metadata declaration's bold markers escaped,
    since `extract_field` reads one inside a fence as readily as outside."""

    @staticmethod
    def safe(text: str) -> str:
        return file_finding._steps_safe(text)

    def test_a_command_line_declaring_a_field_is_escaped_in_its_fence(self) -> None:
        self.assertEqual(self.safe("> **Waived:** yes && true"),
                         "```text\n> \\*\\*Waived:\\*\\* yes && true\n```")

    def test_a_command_item_declaring_an_inline_field_is_escaped_in_its_fence(self) -> None:
        self.assertEqual(self.safe("- printf '· **Verified:** yes'"),
                         "- <!-- -->\n\n  ```text\n  printf '· \\*\\*Verified:\\*\\* yes'\n  ```")

    def test_an_authors_fence_declaring_a_field_is_escaped(self) -> None:
        self.assertEqual(self.safe("```\n> **Waived:** yes\n```"),
                         "```\n> \\*\\*Waived:\\*\\* yes\n```")


class FiledShapesTests(_Fixture):
    """The shapes above through the shipped creators: read back, linted and run."""

    #: The reviewer's three injections, filed through `file_finding.py file`.
    INJECTED = {"Waived": "> **Waived:** yes && true",
                "Verified": "- printf '· **Verified:** yes'",
                "Depends on": ("printf '> **Status:** Ready · **Depends on:** US0001\\n' > s.md "
                               "&& python3 sprint.py plan")}

    def test_a_filed_command_declares_no_field_its_head_did_not(self) -> None:
        sdlc_md = file_finding.sdlc_md
        base = self.file("plain steps")
        for name, steps in self.INJECTED.items():
            self._clear()
            with self.subTest(field=name):
                body = self.file(steps)
                self.assertEqual(sdlc_md.extract_field(body, name),
                                 sdlc_md.extract_field(base, name), body)

    def test_command_survives_filing_as_a_list_item_in_a_fence(self) -> None:
        body = self.file(f"1. {CMD}\n2. Read the my_output line")
        steps = _section(body, "Steps to Reproduce")
        self.assertEqual(steps, f"1. <!-- -->\n\n   ```text\n   {CMD}\n   ```\n\n2. Read the `my_output` line")
        m = re.search(r"```text\n   (.*)\n   ```", steps)
        r = subprocess.run(["bash", "-c", m.group(1)], cwd=SCRIPTS, capture_output=True,
                           text=True, check=False)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "lib.sdlc_md"), r.stderr)
        self._lint(body)

    def test_an_item_command_leaves_the_criteria_and_a_later_fence_readable(self) -> None:
        """The item's fence opens on a line of its own, so the fence readers that strip a line
        pair it: the criteria parser still finds the criteria, and the labeller labels the fix's
        bare fence rather than the item's closer."""
        body = self.file("1. rg -q x", fix="Patch it:\n\n```\nexport A=1\n```")
        self.assertIn("1. <!-- -->\n\n   ```text\n   rg -q x\n   ```\n", body)
        self.assertIn("Patch it:\n\n```text\nexport A=1\n```", body)
        r = subprocess.run([sys.executable, str(SCRIPTS / "verify_ac.py"), "run", "--id",
                            "BG0001", "--dry-run", "--root", str(self.root)],
                           capture_output=True, text=True, check=False)
        self.assertIn("ac=1 ", r.stdout + r.stderr)  # parsed; the Verify itself has no file to run
        self._lint(body)

    def test_a_continuation_command_files_lint_clean(self) -> None:
        """The reviewer's MD029 input, filed and linted."""
        self._lint(self.file('1. From the scripts folder run:\n   python3 -c "import sys\\; from '
                             'lib import sdlc_md"\n2. Read the my_output line'))

    def test_lazy_nested_and_wide_numbered_commands_file_lint_clean(self) -> None:
        self._lint(self.file("1. Run:\npython3 a_b.py\nthen read c_d\n2. Step\n   - sub step:\n"
                             "     python3 e_f.py\n3. Next\n4. a\n5. b\n6. c\n7. d\n8. e\n9. f\n"
                             "10. From here:\n    python3 g_h.py\n11. rg -q x"))

    def test_command_survives_filing_with_a_text_label_through_both_creators(self) -> None:
        """The drop guards read past a fence's `text` label on both sides: the steps safing's
        own, here mid-value, and an author's."""
        steps = f"From the scripts folder:\n{CMD}\n```text\nexport A_B=1\n```"
        want = f"From the scripts folder:\n\n```text\n{CMD}\n```\n\n```text\nexport A_B=1\n```"
        self.assertEqual(_section(self.file(steps), "Steps to Reproduce"), want)
        self._clear()
        self.assertEqual(_section(self.create(steps), "Steps to Reproduce"), want)
        self._clear()
        self.assertEqual(_section(self.create("```text\nexport A_B=1\n```"), "Steps to Reproduce"),
                         "```text\nexport A_B=1\n```")


class MultiLineCommandTests(_Fixture):
    """AC1 for a command that runs over more than one line: kept whole in one fence, through the
    shipped creators, run and linted."""

    def _run(self, fenced: str) -> None:
        """Run a fence's content, dedented to its fence's column, from the scripts folder."""
        lines = fenced.split("\n")
        pad = len(lines[0]) - len(lines[0].lstrip())
        r = subprocess.run(["bash", "-c", "\n".join(ln[pad:] for ln in lines[1:-1])],
                           cwd=SCRIPTS, capture_output=True, text=True, check=False)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "lib.sdlc_md"), r.stderr)

    def test_command_survives_filing_whole_when_it_spans_lines(self) -> None:
        for name, cmd in {**MULTI, "pytest": PYTEST}.items():
            self._clear()
            with self.subTest(command=name):
                self.assertEqual(_section(self.file(cmd), "Steps to Reproduce"),
                                 f"```text\n{cmd}\n```")

    def test_command_survives_filing_over_lines_and_still_runs_when_copied(self) -> None:
        for name, cmd in MULTI.items():
            self._clear()
            with self.subTest(command=name):
                self._run(_section(self.file(cmd), "Steps to Reproduce"))

    def test_command_survives_filing_over_lines_through_both_creators(self) -> None:
        self.assertEqual(_section(self.create(MULTI["heredoc"]), "Steps to Reproduce"),
                         f"```text\n{MULTI['heredoc']}\n```")
        self._clear()
        self.assertEqual(_section(self.batch(MULTI["quoted"]), "Steps to Reproduce"),
                         f"```text\n{MULTI['quoted']}\n```")

    def test_command_survives_filing_over_lines_as_a_list_item(self) -> None:
        heredoc = MULTI["heredoc"].replace("\n", "\n   ")
        body = self.file(f"1. {heredoc}\n2. Read the my_output line")
        steps = _section(body, "Steps to Reproduce")
        self.assertEqual(steps, f"1. <!-- -->\n\n   ```text\n   {heredoc}\n   ```\n\n"
                                "2. Read the `my_output` line")
        self._run(re.search(r"   ```text\n.*?\n   ```", steps, re.S).group(0))
        self._lint(body)

    def test_command_survives_filing_over_lines_beside_prose_lint_clean(self) -> None:
        steps = "\n".join(f"Then the {name} one:\n{cmd}" for name, cmd in MULTI.items())
        body = self.file(steps + "\nand the my_output line")
        for cmd in MULTI.values():
            self.assertIn(f"\n\n```text\n{cmd}\n```\n\n", body)
        self.assertIn("```\n\nand the `my_output` line", body)
        self._lint(body)


class MultiLineShapesTests(unittest.TestCase):
    """Where a command that runs over lines ends, read as the shell reads it."""

    @staticmethod
    def safe(text: str) -> str:
        return file_finding._steps_safe(text)

    def test_a_quote_no_later_line_closes_continues_nothing(self) -> None:
        self.assertEqual(self.safe('printf "a_b\nthe my_var line'),
                         '```text\nprintf "a_b\n```\n\nthe `my_var` line')

    def test_a_line_a_backslash_joins_stays_though_its_quote_never_closes(self) -> None:
        self.assertEqual(self.safe("rg a \\\n'b\nc_d"), "```text\nrg a \\\n'b\n```\n\n`c_d`")

    def test_an_apostrophe_between_letters_opens_no_quote(self) -> None:
        self.assertEqual(self.safe("rg x && it doesn't match\nthe my_var line\nit's here"),
                         "```text\nrg x && it doesn't match\n```\n\nthe `my_var` line\nit's here")

    def test_a_quote_opening_a_word_continues_to_the_line_that_closes_it(self) -> None:
        self.assertEqual(self.safe("rg 'my_a\nmy_b' x\nthe my_var line"),
                         "```text\nrg 'my_a\nmy_b' x\n```\n\nthe `my_var` line")

    def test_a_comment_opens_no_quote(self) -> None:
        self.assertEqual(self.safe("rg x  # users' data\nthe my_var line\nend'"),
                         "```text\nrg x  # users' data\n```\n\nthe `my_var` line\nend'")

    def test_a_hash_inside_a_word_is_no_comment(self) -> None:
        self.assertEqual(self.safe("rg a#'my_b\nmy_c'"), "```text\nrg a#'my_b\nmy_c'\n```")

    def test_a_backslash_before_a_blank_line_continues_nothing(self) -> None:
        self.assertEqual(self.safe("rg x \\\n\nthe my_var line"),
                         "```text\nrg x \\\n```\n\nthe `my_var` line")

    def test_an_escaped_quote_opens_no_quote(self) -> None:
        self.assertEqual(self.safe('rg \\" x\nthe my_var" line'),
                         '```text\nrg \\" x\n```\n\nthe `my_var`" line')

    def test_an_escaped_quote_inside_double_quotes_does_not_close_it(self) -> None:
        cmd = 'rg "say \\"hi\nmy_b"'
        self.assertEqual(self.safe(cmd), f"```text\n{cmd}\n```")

    def test_a_single_quote_closes_only_on_a_single_quote(self) -> None:
        cmd = "rg 'a \\ \"\nmy_b'"
        self.assertEqual(self.safe(cmd + "\nthe my_var line"),
                         f"```text\n{cmd}\n```\n\nthe `my_var` line")

    def test_a_heredoc_no_later_line_ends_continues_nothing(self) -> None:
        self.assertEqual(self.safe("bash <<EOF\nmy_var here"),
                         "```text\nbash <<EOF\n```\n\n`my_var` here")

    def test_a_dashed_double_quoted_heredoc_runs_to_its_delimiter(self) -> None:
        cmd = 'python3 - <<-"PY"\nprint(my_a)\n\tPY'
        self.assertEqual(self.safe(cmd + "\nthe my_var line"),
                         f"```text\n{cmd}\n```\n\nthe `my_var` line")

    def test_a_heredoc_opened_on_a_joined_line_runs_to_its_delimiter(self) -> None:
        cmd = "python3 \\\n  - <<EOF\nprint(my_a)\nEOF"
        self.assertEqual(self.safe(cmd), f"```text\n{cmd}\n```")

    def test_a_heredoc_no_line_ends_leaves_the_next_heredoc_unread(self) -> None:
        """The first body never ends, so the shell never reaches the second."""
        self.assertEqual(self.safe("bash <<A <<B\nmy_b\nB"),
                         "```text\nbash <<A <<B\n```\n\n`my_b`\nB")

    def test_two_heredocs_run_to_their_delimiters_in_turn(self) -> None:
        cmd = "bash <<A <<B\nmy_a\nA\nmy_b\nB"
        self.assertEqual(self.safe(cmd + "\nthe my_var line"),
                         f"```text\n{cmd}\n```\n\nthe `my_var` line")

    def test_a_here_string_is_no_heredoc(self) -> None:
        self.assertEqual(self.safe("rg x <<<EOF\nEOF"), "```text\nrg x <<<EOF\n```\n\nEOF")

    def test_a_shift_inside_quotes_is_no_heredoc(self) -> None:
        self.assertEqual(self.safe('python3 -c "print(a<<b)"\nb'),
                         '```text\npython3 -c "print(a<<b)"\n```\n\nb')

    def test_a_quote_after_a_heredoc_opener_is_read_before_its_body(self) -> None:
        cmd = "python3 - <<'EOF' | rg 'my_a\nmy_b'\nmy_c\nEOF"
        self.assertEqual(self.safe(cmd), f"```text\n{cmd}\n```")

    def test_a_heredoc_body_starts_after_its_opener_line_ends(self) -> None:
        """The delimiter as the backslash's next word is an argument, not the body's end."""
        cmd = "bash <<A \\\nA\nmy_b\nA"
        self.assertEqual(self.safe(cmd), f"```text\n{cmd}\n```")

    def test_only_the_first_lines_prompt_drops_and_the_body_is_not_read_as_markdown(self) -> None:
        self.assertEqual(self.safe("$ bash <<EOF\n$ HOME\n1. my_a\n```\nEOF"),
                         "````text\nbash <<EOF\n$ HOME\n1. my_a\n```\nEOF\n````")

    def test_an_items_lines_move_to_its_column_as_a_block(self) -> None:
        """The body keeps its indentation relative to the command; a blank line in it stays
        empty and is not counted as the least indented."""
        self.assertEqual(self.safe("1. bash <<EOF\n  my_a\n\n  EOF"),
                         "1. <!-- -->\n\n   ```text\n    bash <<EOF\n   my_a\n\n   EOF\n   ```")
        self.assertEqual(self.safe("1. bash <<EOF\nmy_a\nEOF"),
                         "1. <!-- -->\n\n   ```text\n      bash <<EOF\n   my_a\n   EOF\n   ```")

    def test_a_continuation_command_over_lines_keeps_the_items_column(self) -> None:
        self.assertEqual(self.safe("1. Run:\n   rg 'my_a\n\n   my_b'\n2. next"),
                         "1. Run:\n\n   ```text\n   rg 'my_a\n\n   my_b'\n   ```\n\n2. next")


if __name__ == "__main__":
    unittest.main()
