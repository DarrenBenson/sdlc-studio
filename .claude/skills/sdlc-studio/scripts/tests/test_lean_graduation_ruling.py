"""BG0849: a retro rules a lesson's graduation CR by its class code.

On a schema 3 project the graduation CR gets a fresh ULID each time it is filed, and a close dry
run files into a scratch copy, so every dry run and the close name a different id. A retro could
not rule an id nobody can predict, so the CR was always handed over UNRULED. The class code
(LC-nnn) is the one stable name, and the lesson store already links the graduating class to the
CR the close filed (`cr` on the class's row), so a `## Known issues carried` row ruling the code
rules that CR.

Driven through `sprint.py close` (and `--dry-run`) with the chain stubbed green except the two
steps under test, `retro-extract` (which graduates the class) and `checklist` (which joins the
rulings), in a throwaway schema 3 tree.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared

CLASS = "LC-900"
REAL = ("retro-extract", "checklist")
UNRULED = re.compile(r"UNRULED CR")


def _class_row() -> dict:
    """LC-900, active, repeated in two runs after the run that recorded it: the close
    graduates it and files its CR."""
    return {"id": CLASS, "class": "class 900", "rule": "Rule 900 holds.",
            "behaviour": "Behaviour 900 follows.", "inject": ["build"], "state": "active",
            "recorded_run": "RUN-0",
            "hits": [{"run": "RUN-1", "unit": "US0001", "source": "critic:RUN-1"},
                     {"run": "RUN-2", "unit": "US0002", "source": "critic:RUN-2"}]}


class GraduationRulingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        env = unittest.mock.patch.dict(os.environ, {
            lean._live("sprint").run_state.TRANSCRIPTS_ENV: "/nonexistent-transcripts"})
        env.start()
        self.addCleanup(env.stop)

    def _run(self, rows: str = "") -> None:
        """The lean close fixture on schema 3, its batch unit approved, the retro carrying its
        run and the carried table with `rows`, and LC-900 due to graduate."""
        root = self.root
        lean._fixture(root)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                          encoding="utf-8")
        lean._live("critic").record_verdict(root, "US0101", "APPROVE", reviewer="qa-seat",
                                            author="builder", issues="none blocking")
        retro = lean._live("retro")
        (root / "sdlc-studio" / "retros" / "RETRO0001-lean.md").write_text(
            "# RETRO-0001: lean\n\n> **Date:** 2026-09-23\n> **Run:** RUN-LEAN0001\n"
            "> **Batch:** US0101\n\n## Keep\n\n- small units\n\n## Stop\n\n- hand tables\n\n"
            "## Try\n\n- name the mutant first\n\n## Known issues carried\n\n"
            f"{retro.known_issues_table()}\n{rows}", encoding="utf-8")
        (root / "sdlc-studio" / "lessons.jsonl").write_text(json.dumps(_class_row()) + "\n",
                                                            encoding="utf-8")

    def _store_cr(self) -> str:
        rows = [json.loads(ln) for ln in (self.root / "sdlc-studio" / "lessons.jsonl")
                .read_text(encoding="utf-8").splitlines() if ln.strip()]
        return next(r for r in rows if r["id"] == CLASS).get("cr") or ""

    def _known_issues_row(self) -> dict:
        report = lean._live("sprint_report")
        rows = report.checklist(self.root, "RETRO0001")["items"]
        return next(r for r in rows if r["id"] == "known-issues")

    def test_a_retro_rules_the_graduation_cr_by_its_class(self) -> None:
        """AC1. MUTANTS: HEAD, whose `LC-900` row names no artefact, so the CR is UNRULED; ids
        kept stable within one process, which the dry run's scratch copy never shares; a join
        on the CR's title, which the retitle below defeats."""
        self._run(f"| {CLASS} | not-stop-ship | operator | 2026-09-30 |\n")
        for _ in range(2):
            _rc, out, err = lean._close(self.root, "--dry-run", real=REAL)
            self.assertNotRegex(out + err, UNRULED, "the dry run handed the CR over unruled")
            self.assertIn(f"{CLASS} graduating -> CR", out + err, "premise: no graduation")
        rc, out, err = lean._close(self.root, real=REAL)
        self.assertEqual(0, rc, err)
        self.assertNotRegex(out + err, UNRULED, "the close handed the CR over unruled")
        cr = self._store_cr()
        self.assertTrue(cr.startswith("CR") and len(cr) > 6, f"premise: no ULID CR: {cr!r}")
        filed = list((self.root / "sdlc-studio" / "change-requests").glob("CR*.md"))
        self.assertEqual(1, len(filed), "the dry runs filed into the real tree")
        known = [k["detail"] for k in lean._read(self.root)["close_known_issues"]
                 if k["detail"].startswith("known-issues")]
        self.assertEqual([], known, "the close recorded the carried table as a known issue")
        # Retitled in grooming: the class is joined through the store's link, not the title.
        text = filed[0].read_text(encoding="utf-8")
        filed[0].write_text(re.sub(r"^# (\S+): .*$", r"# \1: retitled by grooming", text,
                                   count=1, flags=re.M), encoding="utf-8")
        row = self._known_issues_row()
        self.assertEqual("answered", row["state"], row)
        self.assertIn("1 ruled", row["value"])
        self.assertIn(cr, row["detail"], "the ruled row does not name the CR it ruled")

    def test_an_unruled_graduation_cr_names_its_class(self) -> None:
        """AC2. MUTANTS: dropping graduation CRs from the known issues, which hides a CR nobody
        ruled; HEAD's row, which names the id alone."""
        self._run()
        rc, out, err = lean._close(self.root, real=REAL)
        self.assertEqual(0, rc, err)
        cr = self._store_cr()
        row = self._known_issues_row()
        self.assertEqual("unanswered", row["state"], row)
        unruled = [b for b in row["detail"].split("; ") if b.startswith(f"UNRULED {cr}")]
        self.assertEqual(1, len(unruled), row["detail"])
        self.assertIn(CLASS, unruled[0], "the unruled row does not name the class to rule")


if __name__ == "__main__":
    unittest.main()
