"""BG0826: the retro a close scaffolds names its run and carries the Known issues carried table.

The scaffold held Date, Batch and the Keep/Stop/Try placeholders only. A reader of the run's
rulings without `--retro` (`sprint stop`, the pre-flight, the dry run) finds the run's retro by
the run id in its text, which the scaffold never wrote, so it reported the rulings unreadable;
and the one table a stop-ship ruling is recorded in had to be added by hand, its header guessed
from help/sprint.md.

Driven through `sprint.py close` with no `--retro`, the shipped entry point, in a throwaway
workspace. Nothing reads this repository's own config, ledgers or `.local` state.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
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
import retro  # noqa: E402
import sprint  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

#: One ruling, in the row grammar `retro.carried_issues` reads.
RULING = "| BG0001 | not-stop-ship | operator | 2026-10-01 |"


def _run(module, argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = module.main(argv)
    return rc, buf.getvalue()


class RetroScaffoldRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self._env = os.environ.get(run_state.TRANSCRIPTS_ENV)
        os.environ[run_state.TRANSCRIPTS_ENV] = "/nonexistent-transcripts-for-tests"

    def tearDown(self) -> None:
        if self._env is None:
            os.environ.pop(run_state.TRANSCRIPTS_ENV, None)
        else:
            os.environ[run_state.TRANSCRIPTS_ENV] = self._env

    def _scaffold(self, d: str) -> tuple[Path, dict, Path, str]:
        """An open run closed with no `--retro`: the root, the run state, the retro and its id."""
        root = Path(d)
        stories = root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        (stories / "US0001-widget.md").write_text(
            "# US0001: widget\n\n> **Status:** Done\n> **Points:** 2\n> **Epic:** EP0001\n\n"
            "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n",
            encoding="utf-8")
        bugs = root / "sdlc-studio" / "bugs"
        bugs.mkdir()
        (bugs / "BG0001-carried.md").write_text(
            "# BG0001: carried\n\n> **Status:** Open\n> **Severity:** Medium\n\n"
            "## Acceptance Criteria\n\n- [ ] **AC1** fixed\n", encoding="utf-8")
        run_state.open_run(root, batch=["US0001"], goal="done")
        run_state.update(root, sprint_goal="the widget ships")
        _rc, out = _run(sprint, ["close", "--root", str(root)])
        retros = sorted((root / "sdlc-studio" / "retros").glob("RETRO*.md"))
        self.assertEqual(1, len(retros), f"premise: the close scaffolded no retro:\n{out}")
        state = run_state.read(root)
        rid = sdlc_md.norm_id(state.get("scaffolded_retro") or "")
        self.assertTrue(rid, f"premise: the close recorded no scaffolded retro:\n{out}")
        return root, state, retros[0], rid

    def test_the_scaffold_names_the_run_and_the_table(self) -> None:
        """AC1. MUTANTS: HEAD's template (no run, no table); the run line left as its
        `{{run_id}}` placeholder, which the reader cannot find; a section named otherwise; a
        header the reader takes for a ruling row; a header with a different column set."""
        with tempfile.TemporaryDirectory() as d:
            root, state, path, rid = self._scaffold(d)
            text = path.read_text(encoding="utf-8")
            self.assertEqual(state["run_id"], sdlc_md.extract_field(text, "Run"), text)
            self.assertIn(retro.KNOWN_ISSUES_SECTION, retro.sections(text), text)
            body = [ln for ln in retro.sections(text)[retro.KNOWN_ISSUES_SECTION] if ln.strip()]
            self.assertEqual(list(retro.KNOWN_ISSUES_COLUMNS), sdlc_md.table_cells(body[0]),
                             f"the header is not the reader's columns:\n{text}")
            # The reader skips the header: an empty table is no ruling, not a malformed one.
            self.assertEqual([], retro.carried_issues(text, root=root))
            # The run's rulings found WITHOUT --retro, as `stop` and the pre-flight read them.
            found, rows, why = sprint._carried_rulings(root, state, None)
            self.assertEqual((rid, [], ""), (sdlc_md.norm_id(found or ""), rows, why))
            # And one ruling written under the scaffolded header is read back whole.
            path.write_text(text.rstrip("\n") + f"\n{RULING}\n", encoding="utf-8")
            _found, rows, _why = sprint._carried_rulings(root, state, None)
            self.assertEqual([("BG0001", "not-stop-ship", "operator", True)],
                             [(r["id"], r["ruling"], r["by"], r["ok"]) for r in rows or []])

    def test_an_empty_carried_table_validates(self) -> None:
        """AC2. MUTANTS: a placeholder or example row in the shipped table, or a validator that
        reads an empty table as a gap. The run's own Keep, Stop and Try are filled first, so the
        table is the only thing left to refuse."""
        with tempfile.TemporaryDirectory() as d:
            root, _state, path, rid = self._scaffold(d)
            text = path.read_text(encoding="utf-8")
            for slot, words in (("{{keep}}", "the batch shipped"), ("{{stop}}", "hand tables"),
                                ("{{try}}", "name the mutant before the test")):
                self.assertIn(slot, text, "premise: the scaffold changed shape")
                text = text.replace(slot, words)
            path.write_text(text, encoding="utf-8")
            self.assertIn(retro.KNOWN_ISSUES_SECTION, retro.sections(text),
                          "the scaffold carries no carried table to validate")
            self.assertEqual([], retro.carried_issues(text), "premise: the table is not empty")
            rc, out = _run(retro, ["--root", str(root), "validate", "--id", rid])
            self.assertEqual(0, rc, out)
            res = retro.validate(root, rid)
            self.assertEqual([], res["errors"])


if __name__ == "__main__":
    unittest.main()
