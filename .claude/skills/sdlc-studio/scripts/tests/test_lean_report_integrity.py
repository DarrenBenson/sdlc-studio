"""US0883: a filed report's own figures are checked, not only the tree it re-derives from.

`check` used to compare a re-derivation of the tree with the fingerprint the page records, and
never looked at the page: a hand-edited JSON figure, or a hand-edited Markdown twin, read VALID
for as long as the tree still re-derived the original (BG0745). Each test files a report from the
one-page report's fixture run, edits the page the way a person would, and reads the verdict
through the shipped `sprint_report.py check` entry point.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import test_lean_report as lean  # noqa: E402 - the one-page report's fixture run
import gitutil  # noqa: E402 - confined, hermetic git for fixtures

#: `sprint_report`, imported at test time for the reason `test_lean_report` gives.
sr = lean.sr

GOAL = "A sprint runs start to finish on its own and hands you one page."


class PageIntegrityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        lean.lean_run(self.root)
        self.rid = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO))
        reports = self.root / "sdlc-studio" / "reports"
        self.json = reports / f"{self.rid}.json"
        self.md = next(reports.glob(f"{self.rid}-*.md"))

    def _check(self) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sr.main(["--root", str(self.root), "check", "--report", self.rid])
        return rc, out.getvalue() + err.getvalue()

    def _edit_json_figure(self, section: str, key: str, value) -> dict:
        report = json.loads(self.json.read_text(encoding="utf-8"))
        sec = next(s for s in report["sections"] if s["key"] == section)
        self.assertNotEqual(value, sec["figures"][key]["value"], "the edit changes nothing")
        sec["figures"][key]["value"] = value
        self.json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
        return report

    def _edit_md(self, old: str, new: str) -> None:
        text = self.md.read_text(encoding="utf-8")
        self.assertEqual(1, text.count(old), f"the edit anchor {old!r} is not unique")
        self.md.write_text(text.replace(old, new), encoding="utf-8")

    def test_an_edited_json_figure_is_invalid(self) -> None:
        """AC1. MUTANT: judge the page only by re-deriving the tree against the fingerprint it
        RECORDS - the tree still re-derives the original, so the edited figure reads VALID. The
        second case re-renders the twin from the edited JSON, as a careful editor would, so only
        a digest over the filed figures can see it."""
        rc, out = self._check()
        self.assertEqual(0, rc, out)                      # the positive control
        self.assertIn("VALID", out)
        signed = sr.read_report(self.root, self.rid)["fingerprint"]
        for twin in ("left as filed", "re-rendered from the edited JSON"):
            with self.subTest(twin=twin):
                edited = self._edit_json_figure("delivered", "points_delivered", 99)
                if twin != "left as filed":
                    self.md.write_text(sr.render_markdown(edited), encoding="utf-8")
                rc, out = self._check()
                self.assertEqual(1, rc, out)
                self.assertIn("INVALID", out)
                self.assertIn("points_delivered", out)
                self.assertIn("99", out)
                # The tree was never touched: it still re-derives the page as filed.
                self.assertEqual(signed, sr.build_report(
                    self.root, lean.RETRO,
                    as_of=edited["generated_at"], window_end=edited["window_end"])["fingerprint"])
                self._edit_json_figure("delivered", "points_delivered", 16)
                self.md.write_text(sr.render_markdown(sr.read_report(self.root, self.rid)),
                                   encoding="utf-8")
                self.assertEqual(0, self._check()[0], "restoring the figure restores VALID")

    def test_an_edited_markdown_figure_is_invalid(self) -> None:
        """AC2. MUTANT: check the JSON and never the twin committed beside it - the page a
        reader reads says what nobody derived, and check says VALID."""
        self._edit_md(GOAL, "A sprint that ran itself and needed nobody.")
        rc, out = self._check()
        self.assertEqual(1, rc, out)
        self.assertIn("INVALID", out)
        self.assertIn("sprint_goal", out)
        self.assertEqual(sr.fingerprint(sr.read_report(self.root, self.rid)),
                         sr.read_report(self.root, self.rid)["fingerprint"],
                         "the JSON is untouched, so only the twin can have been judged")
        self._edit_md("| Dropped | 1 | 2 |", "| Dropped | 0 | 2 |")
        self._edit_md("A sprint that ran itself and needed nobody.", GOAL)
        rc, out = self._check()
        self.assertEqual(1, rc, out)
        self.assertIn("dropped_units", out)
        # The row carries a second figure the edit left alone: it is not named.
        self.assertNotIn("dropped_points", out, "a figure the edit left alone is named")
        self.assertNotIn("sprint_goal", out, "a restored figure is no longer named")
        # Two figures that read the same on one row: the edited cell names its own figure only.
        self._edit_md("| Dropped | 0 | 2 |", "| Dropped | 1 | 2 |")
        self._edit_md("| US0005 | 3 | 3 | carried", "| US0005 | 3 | 5 | carried")
        rc, out = self._check()
        self.assertEqual(1, rc, out)
        self.assertEqual(["delivered.unit_points[3]"],
                         [e["figure"] for e in sr.revalidate(self.root, self.rid)["edited"]])
        self.assertIn("unit_points[3]", out)

    def test_trailing_blank_lines_are_not_an_edit(self) -> None:
        """MUTANT: compare the twin line for line including its tail - an editor that saves
        with an extra newline turns an untouched page INVALID, naming nothing."""
        self.md.write_text(self.md.read_text(encoding="utf-8") + "\n\n", encoding="utf-8")
        rc, out = self._check()
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {self.rid}", out)
        self.assertNotIn("not comparable", out, "the twin was not matched outright")

    def test_the_signature_does_not_invalidate(self) -> None:
        """AC3. MUTANT: compare the twin against a render of the report WITHOUT its signature,
        or digest the whole JSON file - signing then invalidates the page it has just signed."""
        import sprint  # noqa: PLC0415 - the seal's own signature writer, not a hand-made one
        with contextlib.redirect_stdout(io.StringIO()):
            signature = sprint._write_the_signature(self.root, self.rid, "the operator")
        self.assertIn("the operator", self.md.read_text(encoding="utf-8"),
                      "sign wrote no signature row onto the twin")
        self.assertEqual("the operator",
                         sr.read_report(self.root, self.rid)["signature"]["principal"])
        rc, out = self._check()
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {self.rid}", out)
        self.assertIn(signature["fingerprint"], out)
        # Matched outright: a signature row read as template wording would pass only as a note.
        self.assertNotIn("not comparable", out, "the signed twin was not matched outright")
        # A signed page is still checked: an edit after the signature is caught.
        self._edit_md(GOAL, "A sprint that ran itself and needed nobody.")
        rc, out = self._check()
        self.assertEqual(1, rc, out)
        self.assertIn("INVALID", out)
        self.assertIn("sprint_goal", out)


class LifecycleFigureTests(unittest.TestCase):
    """`goal.ended_at` and `goal.duration_hours` sit outside the digest, because the seal moves
    the run's end after the page is written. They are still the page's figures, so each is
    checked against what the run record says it was when the page was generated."""

    def _file(self, root: Path, *, open_run: bool) -> tuple[str, Path]:
        lean.lean_run(root)
        live = root / "sdlc-studio" / ".local" / "run-state.json"
        if open_run:
            state = json.loads(live.read_text(encoding="utf-8"))
            state.pop("ended_at")
            live.write_text(json.dumps(state), encoding="utf-8")
        rid = sr.file_report(root, sr.build_report(root, lean.RETRO))
        return rid, root / "sdlc-studio" / "reports" / f"{rid}.json"

    @staticmethod
    def _edit(root: Path, path: Path, key: str, value: str) -> None:
        """Edit one goal figure and re-render the twin from it, as a careful editor would."""
        report = json.loads(path.read_text(encoding="utf-8"))
        goal = next(s for s in report["sections"] if s["key"] == "goal")
        assert goal["figures"][key]["value"] != value, "the edit changes nothing"
        goal["figures"][key]["value"] = value
        sr.write_report(root, report)

    def test_an_edited_end_or_duration_is_invalid(self) -> None:
        """MUTANT: leave the two figures outside the digest unchecked - editing the run's end or
        its duration, with the twin re-rendered to match, reads VALID."""
        # `open` is an edit too: this run had ended before its page was generated.
        for key, value in (("ended_at", "2099-01-01T00:00:00Z"), ("ended_at", "open"),
                           ("duration_hours", "99.0h")):
            with self.subTest(key=key, value=value), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                rid, path = self._file(root, open_run=False)
                self.assertTrue(sr.revalidate(root, rid)["valid"])     # the positive control
                self._edit(root, path, key, value)
                check = sr.revalidate(root, rid)
                self.assertFalse(check["valid"])
                self.assertEqual([f"goal.{key}"], [e["figure"] for e in check["edited"]])
                self.assertIn(value, check["edited"][0]["detail"])

    def test_a_run_sealed_after_its_page_still_reads_valid(self) -> None:
        """MUTANT: require the filed end to equal the run record's end - a page filed while the
        run was open reads `open`, the seal then writes the end, and every signed page reads
        INVALID from its seal on."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rid, path = self._file(root, open_run=True)
            report = json.loads(path.read_text(encoding="utf-8"))
            goal = next(s for s in report["sections"] if s["key"] == "goal")
            self.assertEqual("open", goal["figures"]["ended_at"]["value"])
            live = root / "sdlc-studio" / ".local" / "run-state.json"
            state = json.loads(live.read_text(encoding="utf-8"))
            sealed = datetime.strptime(report["generated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc) + timedelta(hours=1)
            state["ended_at"] = sealed.strftime("%Y-%m-%dT%H:%M:%SZ")
            live.write_text(json.dumps(state), encoding="utf-8")
            sr.run_state.archive(root)
            check = sr.revalidate(root, rid)
            self.assertTrue(check["valid"], check["edited"])
            # An end the run record never held is still an edit on a sealed run's page.
            self._edit(root, path, "ended_at", (sealed + timedelta(days=1)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"))
            self.assertEqual(["goal.ended_at"],
                             [e["figure"] for e in sr.revalidate(root, rid)["edited"]])


def _git(root: Path, *args: str) -> None:
    """Git confined to the fixture, with the host's config and identity neutralised."""
    gitutil.git(list(args), root)


def _sprint_report():
    """The real `sprint_report` module, which `mock.patch.object` needs rather than the proxy."""
    import sprint_report  # noqa: PLC0415
    return sprint_report


class TemplateChangeTests(unittest.TestCase):
    """The twin is compared with a rendering of its JSON, and the template renders it. A page
    filed under one template and read under a later one differs in lines no figure fills, and
    that is not an edit. The template the twin was rendered with is read from the commit that
    last wrote the twin; without that history, template-only differences are named as not
    comparable, and a differing figure is still an edit."""

    TEMPLATE = "core/sprint-report.md"

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # The template lives in the same repository as the reports, as it does here.
        self.templates = self.root / ".claude" / "skills" / "sdlc-studio" / "templates"
        (self.templates / "core").mkdir(parents=True)
        shutil.copy(sr.template_path(self.TEMPLATE), self.templates / self.TEMPLATE)
        patcher = mock.patch.object(_sprint_report(), "template_path",
                                    lambda name: self.templates / name)
        patcher.start()
        self.addCleanup(patcher.stop)
        lean.lean_run(self.root)
        self.rid = sr.file_report(self.root, sr.build_report(self.root, lean.RETRO))
        import sprint  # noqa: PLC0415 - the seal's own signature writer
        with contextlib.redirect_stdout(io.StringIO()):
            sprint._write_the_signature(self.root, self.rid, "the operator")
        self.md = next((self.root / "sdlc-studio" / "reports").glob(f"{self.rid}-*.md"))

    def _check(self) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            rc = sr.main(["--root", str(self.root), "check", "--report", self.rid])
        return rc, out.getvalue()

    def _change_template(self) -> None:
        """A later template: a reworded heading and a new line of prose, no figure touched."""
        path = self.templates / self.TEMPLATE
        text = path.read_text(encoding="utf-8")
        self.assertEqual(1, text.count("## Goal\n"))
        path.write_text(text.replace("## Goal\n", "## The goal\n\nWhat the run set out to do.\n"),
                        encoding="utf-8")

    def _edit_twin_figure(self) -> None:
        text = self.md.read_text(encoding="utf-8")
        self.assertEqual(1, text.count(GOAL))
        self.md.write_text(text.replace(GOAL, "A sprint that ran itself."), encoding="utf-8")

    def test_a_template_change_leaves_a_signed_committed_page_valid(self) -> None:
        """MUTANT: compare the twin only with the CURRENT template's rendering - every filed
        page reads edited the moment the template changes, and status advises restoring a
        file that already matches version control."""
        _git(self.root, "init", "-q")
        _git(self.root, "add", "-A")
        _git(self.root, "commit", "-q", "-m", "file and sign the report")
        self.assertEqual(0, self._check()[0])                  # the positive control
        self._change_template()
        _git(self.root, "commit", "-q", "-am", "a later template")
        self.assertNotEqual(self.md.read_text(encoding="utf-8"),
                            sr.render_markdown(sr.read_report(self.root, self.rid)),
                            "the template change does not reach the rendering")
        rc, out = self._check()
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {self.rid}", out)
        self.assertNotIn("not comparable", out)
        # A committed hand edit to the twin is still an edit, and only the figure is named.
        self._edit_twin_figure()
        _git(self.root, "commit", "-q", "-am", "a hand edit")
        rc, out = self._check()
        self.assertEqual(1, rc, out)
        self.assertIn("INVALID", out)
        self.assertIn("goal.sprint_goal", out)
        self.assertNotIn("wording no figure fills", out)

    def test_without_history_a_template_change_is_not_comparable(self) -> None:
        """MUTANT: read every difference as an edit when no history holds the filing template,
        or none - a template-only change reads INVALID, or a figure edit hides behind it."""
        self._change_template()
        rc, out = self._check()
        self.assertEqual(0, rc, out)
        self.assertIn(f"VALID: {self.rid}", out)
        self.assertIn("not comparable", out)
        self._edit_twin_figure()
        rc, out = self._check()
        self.assertEqual(1, rc, out)
        self.assertIn("goal.sprint_goal", out)


class OwnRunTests(unittest.TestCase):
    def test_a_report_re_derives_its_own_run_after_the_next_one_opens(self) -> None:
        """MUTANT: re-derive whichever run is live - once the next run opens, every earlier
        report reads INVALIDATED against a run it never described."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            lean.lean_run(root)
            rid = sr.file_report(root, sr.build_report(root, lean.RETRO))
            sr.run_state.archive(root)
            live = root / "sdlc-studio" / ".local" / "run-state.json"
            state = json.loads(live.read_text(encoding="utf-8"))
            live.write_text(json.dumps({**state, "run_id": "RUN-01LEANNEXT",
                                        "sprint_goal": "the next run"}), encoding="utf-8")
            check = sr.revalidate(root, rid)
        self.assertTrue(check["valid"], check["changes"])


if __name__ == "__main__":
    unittest.main()
