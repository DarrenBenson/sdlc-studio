"""CR0645 (EP0293): the TRD describes what 6.2 builds. The type sets this module checks are read
from the code that decides them (LL0043), never typed here, and each is checked to hold a member
known to be in it before it is compared, so an empty read cannot pass as agreement.

US1099: which types execute their `- **Verify:**` lines is `sdlc_md.EXECUTES_VERIFIERS`. The TRD
names that set as the authority, and its table gives each type in it as executed and each type
the creators refuse a command-shaped `Verify:` on as refused; both sets are compared here with the
code. The two code comments that said only a story executes its verifier, and the refusal the
filer prints, name the set instead.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_trd_refresh.py
"""
# test-census-subject: sdlc-studio/trd.md
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"
FILE_FINDING = SCRIPTS / "file_finding.py"
ARTIFACT = SCRIPTS / "artifact.py"

sys.path.insert(0, str(SCRIPTS))
import file_finding  # noqa: E402
from lib import sdlc_md  # noqa: E402

#: The authority's name. Each test first checks `sdlc_md` defines it, so a rename fails here
#: rather than leaving the documents naming a set that no longer exists.
AUTHORITY = "EXECUTES_VERIFIERS"
#: A criterion the shared refusal reads as a command, and one it reads as an outcome.
COMMAND_SHAPED = "Verify: rg -q needle src/app.py"
OUTCOME_SHAPED = "Verify: the operator sees a red banner naming the file"
#: The two verdicts the TRD's table may give a type, as its second column spells them.
EXECUTED, REFUSED = "executed", "refused when command-shaped"
#: "only a story", "only the story", "only stories", "story-only" or "stories only", in any case:
#: the wording CR0645 retires.
_STORY_ONLY_RE = re.compile(
    r"\bonly\s+(?:an?\s+|the\s+)?stor(?:y|ies)\b|\bstor(?:y|ies)[- ]only\b", re.I)
_EXECUTION_RE = re.compile(r"verif|execut", re.I)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _trd_body() -> str:
    """The TRD without its Revision History, whose rows record what earlier versions said."""
    return _read(TRD).split("\n## Revision History", 1)[0]


def _section(text: str, heading: str) -> str:
    """The body under the one heading whose title is `heading`, up to the next heading of the
    same or a higher level."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines)
              if re.fullmatch(rf"#+\s+{re.escape(heading)}\s*", line)]
    if len(starts) != 1:
        raise AssertionError(f"{len(starts)} headings titled {heading!r}, expected one")
    level = len(lines[starts[0]].split()[0])
    out = []
    for nxt in lines[starts[0] + 1:]:
        m = re.match(r"^(#+)\s", nxt)
        if m and len(m.group(1)) <= level:
            break
        out.append(nxt)
    return "\n".join(out)


def _blocks(text: str) -> list[str]:
    """The blank-line-separated blocks of `text`, each joined onto one line."""
    return [" ".join(b.split()) for b in re.split(r"\n\s*\n", text) if b.strip()]


def _tables(text: str) -> list[list[list[str]]]:
    """Each markdown table in `text`, as rows of stripped cells: header first, rule dropped."""
    tables, rows = [], []
    for line in text.splitlines() + [""]:
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif rows:
            tables.append(rows)
            rows = []
    return tables


def _story_only(text: str) -> list[str]:
    """The sentences of `text` that `_STORY_ONLY_RE` matches and that name verifying or
    executing."""
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    return [s for s in sentences if _STORY_ONLY_RE.search(s) and _EXECUTION_RE.search(s)]


def _comment_above(path: Path, anchor: str) -> str:
    """The run of `#` comment lines directly above the one line of `path` opening `anchor`."""
    lines = _read(path).splitlines()
    at = [i for i, line in enumerate(lines) if line.strip().startswith(anchor)]
    if len(at) != 1:
        raise AssertionError(f"{len(at)} lines of {path.name} open {anchor!r}, expected one")
    out = []
    for line in reversed(lines[:at[0]]):
        if not line.strip().startswith("#"):
            break
        out.append(line.strip().lstrip("#").strip())
    if not out:
        raise AssertionError(f"no comment above {anchor!r} in {path.name}")
    return "\n".join(reversed(out))


def _refusing_types() -> set[str]:
    """The types in `sdlc_md.ARTIFACT_TYPES` whose creation refuses a command-shaped `Verify:`,
    read from the refusal `file_finding.py` and `artifact.py` both call."""
    refused = set()
    for type_ in sdlc_md.ARTIFACT_TYPES:
        try:
            file_finding.check_prose_acs(type_, {"acs": [COMMAND_SHAPED]})
        except ValueError:
            refused.add(type_)
    return refused


class TrdVerifierAuthorityTests(unittest.TestCase):
    """US1099: the TRD and the code comments name `sdlc_md.EXECUTES_VERIFIERS`."""

    def setUp(self) -> None:
        self.assertTrue(hasattr(sdlc_md, AUTHORITY), f"sdlc_md defines no {AUTHORITY}")
        self.executes = set(getattr(sdlc_md, AUTHORITY))
        self.assertIn("story", self.executes)

    def test_the_refusal_is_read_by_command_shape(self) -> None:
        """Mutant: the derived refusing set taken from a check that refuses every criterion, or
        none. The outcome-shaped control is refused for no type; the command-shaped one for cr."""
        for type_ in sdlc_md.ARTIFACT_TYPES:
            with self.subTest(type_=type_):
                file_finding.check_prose_acs(type_, {"acs": [OUTCOME_SHAPED]})
        refused = _refusing_types()
        self.assertIn("cr", refused)
        self.assertEqual(set(), refused & self.executes)

    def test_the_trd_names_the_executing_types(self) -> None:
        """Mutants: a type added to `EXECUTES_VERIFIERS` that the TRD's table does not give as
        executed; a type the creators refuse that the table does not give as refused; a table row
        with any other verdict; the TRD saying again that only a story executes; the section no
        longer naming `sdlc_md.EXECUTES_VERIFIERS` as the authority."""
        section = _section(_trd_body(), "Acceptance criteria")
        self.assertTrue(
            any(f"`sdlc_md.{AUTHORITY}`" in b and "authority" in b for b in _blocks(section)),
            f"no paragraph of the section names `sdlc_md.{AUTHORITY}` as the authority")
        tables = [t for t in _tables(section) if t[0][0] == "Type"]
        self.assertEqual(1, len(tables), "expected one table headed Type in the section")
        verdicts = {row[0].strip("`"): row[1] for row in tables[0][1:]}
        refused = _refusing_types()
        self.assertIn("cr", refused)
        self.assertEqual(self.executes, {t for t, v in verdicts.items() if v == EXECUTED})
        self.assertEqual(refused, {t for t, v in verdicts.items() if v == REFUSED})
        self.assertEqual(self.executes | refused, set(verdicts))
        self.assertEqual([], _story_only(_trd_body()))

    def test_the_code_comments_name_the_set(self) -> None:
        """Mutant: either comment reverted to the story-only wording, or no longer naming the
        set: the pseudo-Verify comment above `_VERIFY_LEAD_RE` in `file_finding.py`, and the one
        above `artifact.py`'s create-path call to the shared refusal."""
        for path, anchor in ((FILE_FINDING, "_VERIFY_LEAD_RE = "),
                             (ARTIFACT, "file_finding.check_prose_acs(type_, f)")):
            comment = _comment_above(path, anchor)
            with self.subTest(path=path.name):
                self.assertIn(f"`sdlc_md.{AUTHORITY}`", comment)
                self.assertEqual([], _story_only(comment))

    def test_the_filer_s_refusal_names_the_executing_types(self) -> None:
        """Mutant: the refusal `file_finding.py file` prints reverted to saying verify_ac runs
        only a story's line, or no longer naming the set or one of its types."""
        for type_ in sorted(_refusing_types()):
            err = io.StringIO()
            with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(err), \
                    contextlib.redirect_stdout(io.StringIO()):
                (Path(d) / "sdlc-studio").mkdir()
                rc = file_finding.main(["--root", d, "file", "--type", type_, "--title", "A thing",
                                        "--summary", "s", "--priority", "High", "--option", "a",
                                        "--ac", COMMAND_SHAPED])
            with self.subTest(type_=type_):
                self.assertNotEqual(0, rc)
                why = next(line for line in err.getvalue().splitlines() if "Why:" in line)
                self.assertIn(f"`sdlc_md.{AUTHORITY}`", why)
                for member in self.executes:
                    self.assertRegex(why, rf"\b{re.escape(member)}\b")
                self.assertEqual([], _story_only(why))


if __name__ == "__main__":
    unittest.main()
