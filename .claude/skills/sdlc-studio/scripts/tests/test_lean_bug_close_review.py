"""BG0812: the bug-close path names the independent reviewing context it needs.

An agent followed the shipped one-call close, `set --status Fixed --verdict approve --reviewer R
--author A`, named itself reviewer and closed its own fix: nothing in the guidance or the tool
mentioned a separate context or `critic.py brief`. The guidance now says the reviewer is a
separate context briefed with `critic.py brief` and shows the close carrying that brief's
fingerprint; `transition.py set --verdict` without `--brief` still transitions and says, once on
stderr, which step it skipped. Reported, never refused. The doc test reads THIS repository's
shipped skill, as AC1 names it; the CLI tests drive `transition.main` in a temporary workspace.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/transition.py
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import transition  # noqa: E402

DOCS = ("reference-bug.md", "help/bug.md", "reference-scripts.md")
#: a command in the docs that closes a bug to Fixed with a verdict, in either flag order and in
#: the positional form `set <ID> Fixed`; `[^`\n]` keeps a match inside one command
_FIXED = r"(?:--status\s+Fixed|\bset\s+\S+\s+Fixed)\b"
FIXED_WITH_VERDICT = re.compile(rf"{_FIXED}[^`\n]*--verdict|--verdict[^`\n]*{_FIXED}",
                                re.IGNORECASE)
FP = "a1b2c3d4e5f6"


LIST_ITEM = re.compile(r"\s*([-*]|\d+\.)\s")


def _passages(text: str) -> list[str]:
    """Each paragraph or list item of `text`, with a fenced block read as one passage with the
    paragraph or item that introduces it, so a command in a fence is read with its words. A list
    item is its own passage: a catalogue bullet cannot borrow its neighbour's words.
    """
    blocks, current, fenced = [], [], False
    for line in text.splitlines():
        opens = line.lstrip().startswith("```")
        if not fenced and (not line.strip() or LIST_ITEM.match(line)):
            if current:
                blocks.append("\n".join(current))
                current = []
            if not line.strip():
                continue
        if opens:
            fenced = not fenced
        current.append(line)
    if current:
        blocks.append("\n".join(current))
    joined = []
    for block in blocks:
        if block.lstrip().startswith("```") and joined:
            joined[-1] += "\n" + block
        else:
            joined.append(block)
    return joined


def _command(passage: str, match: re.Match) -> str:
    """The whole command `match` sits in: its code span, or its line when it is not in one."""
    start = passage.rfind("\n", 0, match.start()) + 1
    end = passage.find("\n", match.end())
    line = passage[start:end if end >= 0 else None]
    at, offset = match.start() - start, 0
    for n, part in enumerate(line.split("`")):
        if offset <= at < offset + len(part) + 1:
            return part if n % 2 else line
        offset += len(part) + 1
    return line


def _bugs(root: Path, *ids: str) -> None:
    """Bugs In Progress whose one criterion is ticked, so the gated transition to Fixed lands."""
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    rows = []
    for uid in ids:
        (bugs / f"{uid}-x.md").write_text(
            f"# {uid}: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n"
            "- [x] the unit behaves\n", encoding="utf-8")
        rows.append(f"| [{uid}]({uid}-x.md) | a | In Progress |\n")
    (bugs / "_index.md").write_text("# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                                    + "".join(rows), encoding="utf-8")


def _set(root: Path, ids: str, *argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = transition.main(["set", "--ids", ids, "--status", "Fixed", *argv,
                              "--root", str(root)])
    return rc, out.getvalue(), err.getvalue()


def _status(root: Path, uid: str) -> str:
    text = (root / "sdlc-studio" / "bugs" / f"{uid}-x.md").read_text(encoding="utf-8")
    return re.search(r"> \*\*Status:\*\* (.+)", text).group(1)


def _warnings(err: str) -> list[str]:
    return [line for line in err.splitlines() if "critic.py brief" in line]


class BugCloseReviewTests(unittest.TestCase):

    def test_the_close_guidance_names_the_brief(self) -> None:
        """AC1. MUTANTS: the rc.1 wording of reference-scripts.md (a reviewer and an author and
        nothing else); a close with `--brief` but no word of a separate context; either doc
        with no Fixed-with-verdict close at all, which is what rc.1 shipped in both."""
        for rel in DOCS:
            text = (SKILL / rel).read_text(encoding="utf-8")
            shown = [p for p in _passages(text) if FIXED_WITH_VERDICT.search(p)]
            with self.subTest(doc=rel):
                self.assertTrue(shown, f"{rel} shows no Fixed transition with a verdict")
                for passage in shown:
                    for cmd in FIXED_WITH_VERDICT.finditer(passage):
                        self.assertIn("--brief <fingerprint>", _command(passage, cmd), passage)
                    self.assertRegex(passage, r"critic\.py brief --unit \S+ --seat qa", passage)
                    self.assertIn("separate context", passage, passage)

    def test_a_verdict_without_a_brief_is_warned(self) -> None:
        """AC2. MUTANTS: drop the warning (the rc.1 silent close); refuse the close instead of
        warning; warn once per id rather than once per call; accept `--brief` and drop it, so
        the row's Brief cell stays `-`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bugs(root, "BG0001", "BG0002")
            rc, out, err = _set(root, "BG0001,BG0002", "--verdict", "approve",
                                "--reviewer", "rev", "--author", "dev")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual([_status(root, u) for u in ("BG0001", "BG0002")], ["Fixed"] * 2)
            self.assertEqual(len(_warnings(err)), 1, err)
            self.assertIn("--brief", _warnings(err)[0])
            self.assertEqual({r["brief"] for r in critic.read_verdicts(root)}, {"-"})
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bugs(root, "BG0001")
            rc, out, err = _set(root, "BG0001", "--verdict", "approve", "--reviewer", "rev",
                                "--author", "dev", "--brief", FP)
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(_status(root, "BG0001"), "Fixed")
            self.assertEqual(_warnings(err), [], err)
            self.assertEqual([r["brief"] for r in critic.read_verdicts(root)], [FP])

    def test_the_warning_names_a_brief_this_clone_printed(self) -> None:
        """A brief `critic.py brief` noted for the unit is named, so the closer can pass it.
        MUTANT: read the notes for any unit, so another unit's fingerprint is offered."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bugs(root, "BG0001")
            notes = root / critic.BRIEF_NOTES_REL
            notes.parent.mkdir(parents=True)
            notes.write_text(json.dumps({"fp": "0ther0ther000", "unit": "BG0009"}) + "\n"
                             + json.dumps({"fp": FP, "unit": "BG0001"}) + "\n"
                             + json.dumps({"fp": "0ther0ther111", "unit": "BG0009"}) + "\n",
                             encoding="utf-8")
            rc, out, err = _set(root, "BG0001", "--verdict", "approve", "--reviewer", "rev",
                                "--author", "dev")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(len(_warnings(err)), 1, err)
            self.assertIn(FP, err)
            self.assertNotIn("0ther", err)

    def test_a_telemetry_only_verdict_is_not_warned(self) -> None:
        """`--verdict` with no reviewer records no verdict row, and `--brief` there is a usage
        error, so advising `--brief` would send the closer into a refusal. MUTANT: warn on any
        `--verdict`, as round 1 did."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bugs(root, "BG0001")
            rc, out, err = _set(root, "BG0001", "--verdict", "approve")
            self.assertEqual(rc, 0, out + err)
            self.assertEqual(_warnings(err), [], err)

    def test_a_brief_without_the_verdict_names_is_a_usage_error(self) -> None:
        """`--brief` is stored on the verdict row, so without `--reviewer` and `--author` there is
        no row to carry it; it is a usage error rather than a flag silently dropped."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _bugs(root, "BG0001")
            rc, out, err = _set(root, "BG0001", "--verdict", "approve", "--brief", FP)
            self.assertEqual(rc, 2, out + err)
            self.assertEqual(_status(root, "BG0001"), "In Progress")


if __name__ == "__main__":
    unittest.main()
