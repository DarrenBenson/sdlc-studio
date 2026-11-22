"""BG1628: `critic.py record` escapes a bare asterisk outside code spans, as it does an underscore.

`_escape_outside_spans` escaped bare underscores and a linking bracket, never an asterisk, so a
finding naming globs outside a code span (`no author_mutants_* or mutation_edits_* folder`) was
written as `author\\_mutants\\_* or mutation\\_edits\\_*`, which markdownlint reads as emphasis
with spaces inside (MD037), refusing the next commit touching the ledger. The ledger disabled
MD037 meanwhile. A bare asterisk is now escaped there and unescaped by the readers, so the row
reads back as written, and the ledger lints with MD037 on.
"""
# test-census-subject: sdlc-studio/reviews/critic-verdicts.md
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

critic = loader.load_script("critic")
SKILL = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
LEDGER = REPO / "sdlc-studio" / "reviews" / "critic-verdicts.md"
CONFIG = REPO / ".markdownlint.json"
#: The run-eighteen finding that first tripped MD037, and others asterisks reach.
FINDINGS = ("no author_mutants_* or mutation_edits_* folder was left",
            "a_* or b_* outside backticks",
            "the glob `test_lean_*` in a span and test_x_* outside it",
            "**bold** and *em* and 2 * 3")


def _markdownlint() -> str | None:
    """The markdownlint the repo's lane runs: on PATH, in this checkout, or in the main checkout
    this worktree hangs off (a worktree carries no `node_modules` of its own)."""
    found = shutil.which("markdownlint")
    if found:
        return found
    roots = [REPO]
    common = gitutil.git(["rev-parse", "--path-format=absolute", "--git-common-dir"], SKILL,
                         check=False, text=True)
    if common.returncode == 0 and common.stdout.strip():
        roots.append(Path(common.stdout.strip()).parent)
    for root in roots:
        cand = root / "node_modules" / ".bin" / "markdownlint"
        if cand.exists():
            return str(cand)
    return None


def _lint(case: unittest.TestCase, path: Path) -> list[dict]:
    """markdownlint's findings on `path` under the repo's config, as JSON."""
    mdl = _markdownlint()
    if mdl is None:
        case.skipTest("markdownlint is not installed (run `npm install`)")
    r = subprocess.run([mdl, "--config", str(CONFIG), "--json", str(path)],
                       capture_output=True, text=True, check=False, timeout=300)
    out = (r.stderr or r.stdout).strip()
    return json.loads(out) if out else []


def _record(root: Path, issues: str) -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return critic.main(["record", "--unit", "US0001", "--verdict", "reject", "--reviewer",
                            "qa-seat", "--author", "eng-seat", "--issues", issues,
                            "--root", str(root)])


def _project(root: Path) -> None:
    story = root / "sdlc-studio" / "stories" / "US0001-the-widget.md"
    story.parent.mkdir(parents=True)
    story.write_text("# US0001: the widget\n\n> **Status:** Review\n> **Points:** 1\n",
                     encoding="utf-8")


class CriticRecordAsteriskEscapeTests(unittest.TestCase):

    def test_a_glob_finding_lints_and_reads_back_as_written(self) -> None:
        """AC1. Mutants: the asterisk left bare (the row trips MD037); the asterisk escaped and
        not unescaped by the readers (the finding reads back with backslashes); the escape
        applied inside a code span (the span reads back with a backslash in it)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root)
            issues = "; ".join(f"[new] {f}" for f in FINDINGS)
            self.assertEqual(0, _record(root, issues))
            path = critic.verdicts_path(root)
            row = path.read_text(encoding="utf-8").splitlines()[-1]
            self.assertIn("author\\_mutants\\_\\* or mutation\\_edits\\_\\*", row)
            self.assertIn("`test_lean_*`", row, "the code span was escaped")
            found = [f for f in _lint(self, path) if f.get("ruleNames", [""])[0] == "MD037"]
            self.assertEqual([], found, "the row reads as emphasis")
            got = [f["text"] for f in critic.parse_findings(critic.read_verdicts(root)[-1]
                                                            ["issues"])]
            self.assertEqual(list(FINDINGS), got)
            block = critic.rebuild_verdict_block(critic.read_verdicts(root)[-1])
            for finding in FINDINGS[:3]:
                self.assertIn(finding, block)

    def test_the_escape_round_trips_and_is_idempotent(self) -> None:
        """The escape and its inverse over every shape here: an asterisk outside a span is
        escaped once, however often the value is cleaned again, and reads back as written."""
        for text in (*FINDINGS, "`a_`*`_b`", "``x*y`` and x*y", "plain"):
            with self.subTest(text=text):
                once = critic._escape_outside_spans(text)
                self.assertEqual(once, critic._escape_outside_spans(once), "not idempotent")
                self.assertEqual(text, critic._unescape_outside_spans(once))
                outside = []
                critic._outside_spans(once, lambda t: outside.append(t) or t)
                self.assertNotRegex("".join(outside), r"(?<!\\)\*",
                                    "a bare asterisk outside a span was written")
        self.assertEqual("a\\*b", critic._escape_outside_spans("a\\*b"),
                         "an asterisk already escaped was escaped again")
        self.assertEqual("a*b", critic._unescape("a\\*b"))
        self.assertEqual("`x*y` a*b", critic._unescape_outside_spans("`x*y` a\\*b"))

    def test_an_identity_cell_with_an_asterisk_reads_back(self) -> None:
        """The identity readers (`_id`, `recorded_seat`) undo the escape too, so a reviewer
        named with an asterisk is the same identity once written."""
        self.assertTrue(critic.same_identity(critic._clean("qa*seat"), "qa*seat"))


class CriticLedgerMd037Tests(unittest.TestCase):

    def test_the_ledger_lints_with_md037_on(self) -> None:
        """AC2. Mutant: MD037 left in the ledger's disable line. The ledger as committed passes
        markdownlint under the repo's config with the rule on."""
        text = LEDGER.read_text(encoding="utf-8")
        disables = re.findall(r"markdownlint-disable([^>]*)-->", text)
        self.assertTrue(disables, "premise: the ledger keeps its bare-URL disable")
        self.assertEqual([], [d for d in disables if "MD037" in d], "MD037 is still disabled")
        self.assertEqual([], [f for f in _lint(self, LEDGER)
                              if f.get("ruleNames", [""])[0] == "MD037"])

    def test_the_run_eighteen_row_reads_back_as_written(self) -> None:
        """The one row MD037 caught, its asterisks now escaped in the ledger, reads back with
        them as the reviewer wrote them."""
        rows = [r for r in critic.read_verdicts(REPO) if "mutation\\_edits\\_" in
                r.get("issues", "")]
        self.assertTrue(rows, "the row naming author_mutants_* reads back without it")
        self.assertIn("no author_mutants_* or mutation_edits_* folder was left",
                      critic._unescape_outside_spans(rows[0]["issues"]))


if __name__ == "__main__":
    unittest.main()
