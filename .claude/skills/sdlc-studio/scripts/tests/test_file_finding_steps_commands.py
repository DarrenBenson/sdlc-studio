"""BG0967: a finding's Steps to Reproduce is written as its author gave it, so a repro command
copied out of the filed bug still runs. The filer adds no backtick, fence, marker or indentation
there, and tells no command from prose. Two changes remain: the metadata-line guard escapes a field
declaration's bold markers, and a fence the author left open is closed after the value. Every
other prose field keeps `_prose_safe`.

Each finding is filed through a shipped CLI (`file_finding.py file`, `artifact.py new` and
`batch`) into a throwaway fixture root, with the steps supplied in a `--fields-file` or spec
document so no value crosses a shell on the way in.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding_steps_commands.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import file_finding  # noqa: E402
from lib import sdlc_md  # noqa: E402

FILER = SCRIPTS / "file_finding.py"
CREATOR = SCRIPTS / "artifact.py"
VERIFIER = SCRIPTS / "verify_ac.py"
STEPS = "Steps to Reproduce"

#: The bug's own repro: identifiers the old safing back-ticked inside the double quotes, where a
#: backtick is command substitution.
CMD = 'python3 -c "import sys; from lib import sdlc_md; print(sdlc_md.__name__)"'

#: The same program over more than one line, each run from the scripts folder: inside double
#: quotes, as a here-document and after a backslash continuation.
MULTI = {"quoted": 'python3 -c "\nfrom lib import sdlc_md\nprint(sdlc_md.__name__)\n"',
         "heredoc": "python3 - <<'EOF'\nfrom lib import sdlc_md\nprint(sdlc_md.__name__)\nEOF",
         "backslash": 'python3 -c \\\n  "from lib import sdlc_md; print(sdlc_md.__name__)"'}

#: Commands whose first word no command list held, each naming an underscored identifier.
EXPORT = "export A_B=1\necho my_var"

#: A heredoc as a numbered item's body, its lines after the first unindented.
ITEM_HEREDOC = "1. python3 - <<'EOF'\nfrom lib import sdlc_md\nprint(sdlc_md.__name__)\nEOF"

#: Prose holding a shell operator, a plural possessive and an apostrophe, then underscored names.
PROSE = "Run git status && check the users' list\nThen read Bob's note on my_x\nand the my_y value"

#: Every unfenced shape the filer must write byte for byte.
UNFENCED = {"one-line": CMD, **MULTI, "export": EXPORT, "item heredoc": ITEM_HEREDOC,
            "prose": PROSE}

#: The `python3` commands that must still print the module's name when copied and run.
RUNNABLE = {"one-line": CMD, **MULTI}


def _section(body: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\n\n(.*?)\n\n## ", body, re.S | re.M)
    if not m:
        raise AssertionError(f"no '## {heading}' section in:\n{body}")
    return m.group(1)


def _escaped(text: str, *names: str) -> str:
    """`text` with each named declaration's bold markers escaped, as the guard writes them."""
    for name in names:
        text = text.replace(f"**{name}:**", rf"\*\*{name}:\*\*")
    return text


class _Fixture(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "thing.py").write_text("", encoding="utf-8")

    def tearDown(self) -> None:
        self._td.cleanup()

    def _clear(self) -> None:
        for folder in ("bugs", "change-requests"):
            for p in (self.root / "sdlc-studio" / folder).glob("*.md"):
                p.unlink()

    def _doc(self, **fields) -> str:
        p = self.root / "finding.json"
        p.write_text(json.dumps(fields), encoding="utf-8")
        return str(p)

    def _written(self, folder: str) -> str:
        return next(p for p in (self.root / "sdlc-studio" / folder).glob("*.md")
                    if p.name != "_index.md").read_text(encoding="utf-8")

    def file(self, steps: str, type_: str = "bug", summary: str = "s", fix: str = "f") -> str:
        """File one finding through `file_finding.py file`; return the written body."""
        self._clear()  # one finding on disc at a time, whatever an earlier subtest left
        extra = (["--severity", "low", "--points", "1", "--ac", "the repro runs",
                  "--verify", "pytest tests/test_x.py"] if type_ == "bug"
                 else ["--priority", "low", "--ac", "the repro runs"])
        r = subprocess.run(
            [sys.executable, str(FILER), "file", "--root", str(self.root), "--type", type_,
             "--title", "a repro command", *extra, "--affects", "src/thing.py",
             "--fields-file", self._doc(summary=summary, steps=steps, fix=fix)],
            capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, f"the filer refused the fixture:\n{r.stdout}{r.stderr}")
        return self._written("bugs" if type_ == "bug" else "change-requests")

    def create(self, steps: str, *template: str, summary: str = "s") -> str:
        """Create one bug through `artifact.py new`; return the written body."""
        self._clear()  # one finding on disc at a time, whatever an earlier subtest left
        r = subprocess.run(
            [sys.executable, str(CREATOR), "new", "--type", "bug", "--title", "a repro command",
             "--root", str(self.root), *template, "--fields-file",
             self._doc(severity="Low", points=1, affects="src/thing.py", summary=summary,
                       steps=steps, fix="f")],
            capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, f"artifact new refused the fixture:\n{r.stdout}{r.stderr}")
        return self._written("bugs")

    def batch(self, steps: str, summary: str = "s") -> str:
        """Create one bug through `artifact.py batch`; return the written body."""
        self._clear()  # one finding on disc at a time, whatever an earlier subtest left
        spec = self.root / "batch.json"
        spec.write_text(json.dumps([{"title": "a repro command", "severity": "Low", "points": 1,
                                     "affects": "src/thing.py", "summary": summary, "steps": steps,
                                     "fix": "f"}]), encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(CREATOR), "batch", "--type", "bug", "--spec", str(spec),
             "--root", str(self.root)], capture_output=True, text=True, check=False)
        self.assertEqual(r.returncode, 0, f"artifact batch refused the fixture:\n{r.stdout}{r.stderr}")
        return self._written("bugs")


class StepsAsWrittenTests(_Fixture):
    """AC1: an unfenced Steps value is filed byte for byte, whatever its lines hold."""

    def test_command_survives_filing_byte_for_byte_in_every_shape(self) -> None:
        for shape, steps in UNFENCED.items():
            with self.subTest(shape=shape):
                self.assertEqual(_section(self.file(steps), STEPS), steps)

    def test_command_survives_filing_and_still_runs_when_copied(self) -> None:
        """Copy the section out of the filed bug and run it where the repro says."""
        for shape, steps in RUNNABLE.items():
            with self.subTest(shape=shape):
                section = _section(self.file(steps), STEPS)
                r = subprocess.run(["bash", "-c", section], cwd=SCRIPTS, capture_output=True,
                                   text=True, check=False)
                self.assertEqual((r.returncode, r.stdout.strip()), (0, "lib.sdlc_md"), r.stderr)


class StepsAsWrittenEveryCreatorTests(_Fixture):
    """AC2: every other path that writes a Steps to Reproduce section writes it as given."""

    SHAPES = {"one-line": CMD, "heredoc": MULTI["heredoc"], "export": EXPORT}

    #: A safed Summary beside the Steps, so each creator's drop guard must read the author's
    #: letters and digits across the backticks the safing adds there.
    SUMMARY = "read my_var"

    def _each(self, make) -> None:
        for shape, steps in self.SHAPES.items():
            with self.subTest(shape=shape):
                body = make(steps)
                self.assertEqual(_section(body, STEPS), steps)
                self.assertEqual(_section(body, "Summary"), "read `my_var`")

    def test_command_survives_filing_through_artifact_new(self) -> None:
        self._each(lambda steps: self.create(steps, summary=self.SUMMARY))

    def test_command_survives_filing_through_artifact_new_full_template(self) -> None:
        self._each(lambda steps: self.create(steps, "--template", "full", summary=self.SUMMARY))

    def test_command_survives_filing_through_artifact_batch(self) -> None:
        self._each(lambda steps: self.batch(steps, summary=self.SUMMARY))

    def test_command_survives_filing_on_a_cr_whose_steps_are_landed(self) -> None:
        """A CR has no Steps section of its own: the lander appends one, written the same way."""
        self._each(lambda steps: self.file(steps, "cr", summary=self.SUMMARY))


class StepsGuardTests(_Fixture):
    """AC3: the two changes the filer still makes, neither reading what a line means."""

    def test_an_authors_fence_is_kept_but_for_each_declarations_bold_markers(self) -> None:
        steps = "```markdown\n> **Status:** Done\n> **Depends on:** US0002\nplain my_line\n```"
        body = self.file(steps)
        self.assertEqual(_section(body, STEPS), _escaped(steps, "Status", "Depends on"))
        self.assertEqual(sdlc_md.extract_field(body, "Status"), "Open")
        self.assertIsNone(sdlc_md.extract_field(body, "Depends on"))

    def test_a_blockquoted_declaration_before_a_command_is_escaped(self) -> None:
        steps = "> **Waived:** yes\nyes && true"
        body = self.file(steps)
        self.assertEqual(_section(body, STEPS), _escaped(steps, "Waived"))
        self.assertIsNone(sdlc_md.extract_field(body, "Waived"))

    def test_a_declaration_after_a_middle_dot_in_an_items_command_is_escaped(self) -> None:
        steps = "1. printf '%s\\n' 'run · **Verified:** yes'"
        body = self.file(steps)
        self.assertEqual(_section(body, STEPS), _escaped(steps, "Verified"))
        self.assertIsNone(sdlc_md.extract_field(body, "Verified"))

    def test_an_open_fence_is_closed_on_its_own_marker_so_the_criterion_still_parses(self) -> None:
        for opener, closer in (("```sh", "```"), ("~~~sh", "~~~")):
            with self.subTest(opener=opener):
                steps = f"{opener}\n{EXPORT}"
                body = self.file(steps)
                self.assertEqual(_section(body, STEPS), f"{steps}\n{closer}")
                bug = re.match(r"# (BG\d+)", body)[1]
                r = subprocess.run(
                    [sys.executable, str(VERIFIER), "run", "--id", bug, "--dry-run",
                     "--root", str(self.root), "--dir", str(self.root / "sdlc-studio" / "bugs")],
                    capture_output=True, text=True, check=False)
                self.assertIn("pytest tests/test_x.py", r.stdout + r.stderr,
                              f"the criterion did not parse:\n{r.stdout}{r.stderr}")

    def test_a_fence_is_closed_at_its_own_run_length(self) -> None:
        self.assertEqual(file_finding._steps_safe(f"````text\n{CMD}"), f"````text\n{CMD}\n````")

    def test_a_tilde_fence_closes_only_on_its_own_marker(self) -> None:
        block = f"~~~~\n```\n{CMD}\n~~~\n~~~~"
        self.assertEqual(file_finding._steps_safe(block), block)
        self.assertEqual(file_finding._steps_safe(f"~~~\n```\n{CMD}"), f"~~~\n```\n{CMD}\n~~~")

    def test_an_indented_open_fence_in_a_list_item_is_closed(self) -> None:
        steps = "1. Run:\n\n   ```sh\n   export A_B=1"
        self.assertEqual(file_finding._steps_safe(steps), f"{steps}\n```")

    def test_a_tilde_fence_whose_info_string_holds_a_backtick_is_closed(self) -> None:
        """CommonMark lets a tilde fence's info string hold a backtick, so it still opens."""
        self.assertEqual(file_finding._steps_safe("~~~ `sh`\necho my_var"),
                         "~~~ `sh`\necho my_var\n~~~")

    def test_a_fence_line_carrying_an_info_string_does_not_close_the_block(self) -> None:
        """Read by the shared fence reader: a closer may carry nothing after its run."""
        steps = f"```\n{CMD}\n```sh\nexport A_B=1"
        self.assertEqual(file_finding._steps_safe(steps), f"{steps}\n```")

    def test_inline_code_in_triple_backticks_opens_no_fence(self) -> None:
        """CommonMark: a backtick run with another backtick after it on the line opens no fence,
        so nothing is closed after it."""
        self.assertEqual(file_finding._steps_safe("```x_y``` then a_b"), "```x_y``` then a_b")

    def test_a_closed_fence_is_left_as_written(self) -> None:
        block = f"Repro:\n\n```sh\n{CMD}\nexport A_B=1\n```"
        self.assertEqual(file_finding._steps_safe(block), block)
        self.assertEqual(file_finding._steps_safe(f"{block}\nthen read_me now"),
                         f"{block}\nthen read_me now")


class StepsProseTests(_Fixture):
    """AC4: the filer adds no backtick to the Steps, while every other prose field is safed."""

    PROSE = "Read the __init__ module, my_file.md and https://example.com/a_b"

    def test_the_steps_take_no_backtick_while_the_summary_is_safed(self) -> None:
        # a Proposed Fix of its own words, so the drop guard must find them across the safing
        # rather than in the Steps, which hold the Summary's words as written
        body = self.file(self.PROSE, summary=self.PROSE, fix="Keep the __init__ and my_fix names")
        self.assertEqual(_section(body, STEPS), self.PROSE)
        summary = _section(body, "Summary")
        for span in ("`__init__`", "`my_file.md`", "`https://example.com/a_b`"):
            with self.subTest(span=span):
                self.assertIn(span, summary)
        self.assertEqual(_section(body, "Proposed Fix"), "Keep the `__init__` and `my_fix` names")

    def test_only_the_steps_field_is_written_as_given(self) -> None:
        self.assertEqual(file_finding._field_safe("steps", self.PROSE), self.PROSE)
        for key in ("summary", "fix", "impact", "recommendation"):
            with self.subTest(key=key):
                self.assertEqual(file_finding._field_safe(key, self.PROSE),
                                 file_finding._prose_safe(self.PROSE))
                self.assertNotEqual(file_finding._field_safe(key, self.PROSE), self.PROSE)

    def test_the_steps_help_of_both_commands_says_the_value_is_written_as_given(self) -> None:
        for argv in ([str(FILER), "file", "--help"], [str(CREATOR), "new", "--help"]):
            with self.subTest(argv=argv[1]):
                r = subprocess.run([sys.executable, *argv], capture_output=True, text=True,
                                   check=False)
                self.assertIn("written as given: fence a command so markdown renders it as code",
                              " ".join(r.stdout.split()))


if __name__ == "__main__":
    unittest.main()
