"""US0877: the retro is three lines, and a re-run close keeps one report per run.

A new retro asks three things - what to keep, what to stop, what to try - and the close lifts
each Try item into the lessons store once, however many times it runs. Re-filing a run's report
rewrites that run's RPT in place rather than minting another id.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import artifact  # noqa: E402
import lessons  # noqa: E402
import retro  # noqa: E402
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run

#: `sprint_report`, imported at test time for the reason `test_lean_report` gives.
sr = lean.sr

#: A Try item whose first sentence runs past the headline limit, so its lesson title is elided
#: with `...` - the shape whose duplicates fill this repository's own lessons store.
LONG_TRY = ("**A test moved to accommodate a defect is worse than the defect.** It converts a "
            "caught error into a permanent blind spot, and only an independent reader of the "
            "diff will ever notice it.")


def _retro(root: Path, *, keep=("the one-page report",), stop=("plan review",),
           tries=("cap review at two rounds",), extra: str = "") -> Path:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    body = ["# RETRO-0001: a sprint", "", "> **Date:** 2026-09-23", "> **Batch:** US0001", ""]
    for heading, items in (("Keep", keep), ("Stop", stop), ("Try", tries)):
        body += [f"## {heading}", ""] + [f"- {item}" for item in items] + [""]
    p = d / "RETRO0001-a-sprint.md"
    p.write_text("\n".join(body) + extra, encoding="utf-8")
    return p


def _extract(root: Path) -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return retro.main(["--root", str(root), "extract", "--id", "RETRO0001"])


def _titles(root: Path) -> list[str]:
    log = lessons.default_project_file(root)
    return [e["title"] for e in lessons.parse_project_lessons(log.read_text(encoding="utf-8"))]


class ThreeLineRetroTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_the_retro_scaffold_is_keep_stop_try(self) -> None:
        """AC1. MUTANT: leave any of the old sections (Delivered, Lessons, Actions raised) in
        the template - the scaffold then asks for more than three lines again."""
        res = artifact.meta_new(self.root, "retro", "a sprint", {"date": "2026-09-23"})
        path = Path(res["path"])
        text = path.read_text(encoding="utf-8")
        self.assertEqual(["Keep", "Stop", "Try"], list(retro.sections(text)))
        # Filling the three - and the batch the scaffold asks for - is all it takes.
        filled = (text.replace("{{batch}}", "US0001").replace("{{keep}}", "small units")
                  .replace("{{stop}}", "plan review").replace("{{try}}", "a round cap"))
        path.write_text(filled, encoding="utf-8")
        res = retro.validate(self.root, res["file_id"])
        self.assertTrue(res["ok"], res["errors"])

    def test_validate_accepts_three_lines_and_rejects_placeholders_and_long_try(self) -> None:
        """AC2. MUTANT: drop the Try limit or the placeholder check - a retro of seven tries,
        or one nobody filled in, passes the close."""
        _retro(self.root)
        ok = retro.validate(self.root, "RETRO0001")
        self.assertTrue(ok["ok"], ok["errors"])
        self.assertEqual(["cap review at two rounds"], ok["lessons"])

        _retro(self.root, tries=("one", "two", "three", "four"))
        long = retro.validate(self.root, "RETRO0001")
        self.assertFalse(long["ok"])
        self.assertTrue(any("4" in e and "3" in e and "Try" in e for e in long["errors"]),
                        f"the refusal does not name the limit: {long['errors']}")

        _retro(self.root, stop=("{{stop}}",))
        placeholder = retro.validate(self.root, "RETRO0001")
        self.assertFalse(placeholder["ok"])
        self.assertTrue(any("{{stop}}" in e for e in placeholder["errors"]),
                        placeholder["errors"])

        _retro(self.root, extra="\n> **Goal:** {{goal}}\n")
        stray = retro.validate(self.root, "RETRO0001")
        self.assertFalse(stray["ok"], "a placeholder outside the three sections passed")

        _retro(self.root, keep=())
        empty = retro.validate(self.root, "RETRO0001")
        self.assertFalse(empty["ok"], "an empty Keep passed")

    def test_try_items_become_lessons_exactly_once(self) -> None:
        """AC3. MUTANT: dedupe on the elided title, as the close did - a lesson whose stored
        headline has lost its `...` is recorded again on every close attempt, which is how one
        retro's four lessons came to be stored three times each."""
        _retro(self.root, tries=(LONG_TRY, "cap review at two rounds"))
        self.assertEqual(0, _extract(self.root))
        first = _titles(self.root)
        self.assertEqual(2, len(first), first)
        self.assertEqual(0, _extract(self.root))
        self.assertEqual(first, _titles(self.root), "a second extraction recorded again")
        # The store's own shape on this repository: the elided headline without its `...`.
        log = lessons.default_project_file(self.root)
        text = log.read_text(encoding="utf-8")
        elided = retro.lesson_title(LONG_TRY)
        self.assertTrue(elided.endswith("..."))
        log.write_text(text.replace(elided, elided[:-3]), encoding="utf-8")
        self.assertEqual(0, _extract(self.root))
        self.assertEqual(2, len(_titles(self.root)),
                         "a lesson whose headline lost its ellipsis was recorded twice")
        # ...and the control: a new Try item is still recorded.
        _retro(self.root, tries=(LONG_TRY, "cap review at two rounds", "a third try"))
        self.assertEqual(0, _extract(self.root))
        self.assertEqual(3, len(_titles(self.root)))

    def test_two_try_items_sharing_a_headline_are_two_lessons(self) -> None:
        """AC3. MUTANT: judge "already recorded" by the headline - two different Try items that
        open on the same sentence share a title, and the second is dropped as a duplicate of
        the first, in the same run and in a later one."""
        same = ("Cap review. Two rounds for delivery review, then escalate.",
                "Cap review. Plan review gets one round, not four.")
        _retro(self.root, tries=same)
        self.assertEqual(0, _extract(self.root))
        self.assertEqual(2, len(_titles(self.root)), "one run merged two lessons")
        with tempfile.TemporaryDirectory() as other:
            later = Path(other)
            _retro(later, tries=same[:1])
            self.assertEqual(0, _extract(later))
            _retro(later, tries=same)
            self.assertEqual(0, _extract(later))
            self.assertEqual(2, len(_titles(later)), "a later run merged two lessons")

    def test_a_try_item_repeated_in_one_retro_is_one_lesson(self) -> None:
        """AC3. MUTANT: stop counting the lessons added in this run - the same Try item written
        twice in one retro is recorded twice, whether it is one sentence or several."""
        _retro(self.root, tries=("cap review at two rounds", "cap review at two rounds",
                                 LONG_TRY, LONG_TRY))
        self.assertEqual(0, _extract(self.root))
        self.assertEqual(2, len(_titles(self.root)), _titles(self.root))


class OneReportPerRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _file(self) -> str:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "build", "--format", "json", "--write"])
        self.assertEqual(0, rc, err.getvalue())
        return json.loads(out.getvalue())["report_id"]

    def test_refiling_a_runs_report_reuses_its_id(self) -> None:
        """AC4. MUTANT: allocate a fresh id on every filing - a close run twice leaves two
        reports for one run, which is how RPT0004 and RPT0005 came to exist."""
        lean.lean_run(self.root)
        reports = self.root / "sdlc-studio" / "reports"
        first = self._file()
        # A late fix between the two filings, so the rewrite is visible in the page.
        unit = self.root / "sdlc-studio" / "stories" / "US0002-a-unit.md"
        unit.write_text(unit.read_text(encoding="utf-8").replace("Points:** 5", "Points:** 8"),
                        encoding="utf-8")
        again = self._file()
        self.assertEqual(first, again, "re-filing the same run allocated a new id")
        self.assertEqual([f"{first}.json"], sorted(p.name for p in reports.glob("RPT*.json")))
        self.assertEqual(1, len(list(reports.glob(f"{first}-*.md"))))
        self.assertEqual(19, sr.read_report(self.root, first)["sections"][2]["figures"]
                         ["points_delivered"]["value"], "the report was not rewritten in place")
        index = (reports / "_index.md").read_text(encoding="utf-8")
        self.assertEqual(1, index.count(f"[{first}]"))
        # A different run gets a new id.
        state_path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["run_id"] = "RUN-01LEANTWO"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        other = self._file()
        self.assertNotEqual(first, other)
        self.assertEqual(2, len(list(reports.glob("RPT*.json"))))

    def test_a_signed_report_is_never_overwritten_on_refiling(self) -> None:
        """AC4. MUTANT: reuse the run's report whether or not it is signed - re-filing a signed
        run's report writes over the page the reviewer of record put a name to."""
        import sprint  # noqa: PLC0415 - the seal's own signature writer, not a hand-made one
        lean.lean_run(self.root)
        first = self._file()
        with contextlib.redirect_stdout(io.StringIO()):
            signature = sprint._write_the_signature(self.root, first, "the operator")
        signed = sr.read_report(self.root, first)
        again = self._file()
        self.assertNotEqual(first, again, "a signed report was rewritten under its own id")
        self.assertEqual(signed, sr.read_report(self.root, first), "the signed page moved")
        self.assertEqual("the operator", signed["signature"]["principal"])
        self.assertEqual(signature["fingerprint"], signed["fingerprint"])
        self.assertFalse(sr.read_report(self.root, again).get("signature"))

class RetroTailTests(unittest.TestCase):
    """MUTANT: write the retro with the section helper's tail untouched - a Handoff section at
    the foot of the retro leaves a trailing blank line, and markdownlint refuses the commit."""

    def test_linking_the_handoff_leaves_exactly_one_newline(self) -> None:
        import handoff  # noqa: PLC0415 - the writer under test
        with tempfile.TemporaryDirectory() as tmp:
            retro = Path(tmp) / "RETRO0001-x.md"
            retro.write_text("# RETRO-0001: x\n\n## Keep\n\n- a\n\n## Handoff\n\n- old\n",
                             encoding="utf-8")
            report = {"summary": {"remaining": 0, handoff.COPILOT_TAIL: 0, handoff.JUDGEMENT: 0},
                      "worklist": "w.txt"}
            for _ in range(2):   # a re-run close links again
                handoff._link_from_retro(retro, "HO-0001", "HO0001-x.md", report)
                text = retro.read_text(encoding="utf-8")
                self.assertTrue(text.endswith("\n") and not text.endswith("\n\n"),
                                repr(text[-40:]))


if __name__ == "__main__":
    unittest.main()
