"""US0977: a lesson class finishes its lifecycle without a hand edit to `lessons.jsonl`.

Two ends the close never reached. A `graduating` class whose CR reached a terminal status stayed
`graduating` (the 2026-10-01 sweep edited four rows to `graduated` by hand), and an `active`
class whose recording and hit runs this clone's archive has never seen stayed active for ever,
because quiet was judged only on runs the archive knows to be old.

Each test writes a throwaway workspace, runs `lessons.close_pass` with the run state the close
passes it, and reads the result back through the shipped `lessons.py classes`.

BG1139, the project log's end of the same lifecycle: `revalidate --extend` dropped its reason, so a
judged extension read exactly like an unjudged one. `RevalidationRecordTests` drives
`lessons.main` with the date pinned, and runs the script itself where the exit code is the claim.
"""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

lessons = loader.load_script("lessons")
critic = loader.load_script("critic")
sprint = loader.load_script("sprint")
SCRIPTS = Path(__file__).resolve().parent.parent

_CR = ("# {cid}: a graduation request\n\n> **Status:** {status}\n> **Priority:** Medium\n"
       "> **Type:** Enhancement\n\n## Summary\n\nFix the path.\n")


class LessonLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / "sdlc-studio" / "change-requests").mkdir(parents=True)

    def _row(self, code: str, recorded: str, *hit_runs: str, state: str = "active",
             cr: str | None = None) -> dict:
        row = {"id": code, "class": f"class {code}", "rule": f"Rule of {code} holds.",
               "behaviour": f"Do {code} differently.", "inject": ["build"],
               "hits": [{"run": r, "unit": "US0001", "source": f"critic:{r}"} for r in hit_runs],
               "state": state, "recorded_run": recorded}
        if cr:
            row["cr"] = cr
        return row

    def _store(self, *rows: dict) -> None:
        (self.root / lessons.STORE_FILE).write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def _cr(self, cid: str, status: str) -> None:
        (self.root / "sdlc-studio" / "change-requests" / f"{cid}-a-graduation-request.md"
         ).write_text(_CR.format(cid=cid, status=status), encoding="utf-8")

    def _archive(self, *runs: str) -> None:
        d = self.root / "sdlc-studio" / ".local" / "run-archive"
        d.mkdir(parents=True, exist_ok=True)
        for n, run in enumerate(runs, 1):
            (d / f"{run}.json").write_text(json.dumps(
                {"run_id": run, "started_at": f"2026-09-{n:02d}T08:00:00Z",
                 "outcome": "goal-reached"}), encoding="utf-8")

    def _close(self, run: str) -> dict:
        return lessons.close_pass(self.root, run, {"run_id": run, "batch": []})

    def _classes(self) -> dict[str, str]:
        """{code: state} as `lessons.py classes` prints it."""
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "lessons.py"), "--root", str(self.root),
             "classes"], capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        out = {}
        for ln in proc.stdout.splitlines():
            parts = ln.split()
            if len(parts) >= 2 and lessons.CLASS_CODE_RE.match(parts[0]):
                out[parts[0]] = parts[1]
        return out

    def test_a_class_graduates_when_its_cr_closes(self) -> None:
        """AC1. A shipped CR (Complete, Superseded) graduates its class; a Rejected one fixed
        nothing, so the class retires, revivable by its next repeat; an open one leaves it.
        MUTANT: HEAD, which leaves all four `graduating`. MUTANT: graduate on any CR that exists,
        whatever its status - LC-002, still Proposed, graduates too. MUTANT: graduate on any
        terminal status - LC-004, Rejected, graduates for good. MUTANT: graduate only on
        Complete - LC-003, Superseded, stays `graduating`."""
        self._cr("CR0001", "Complete")
        self._cr("CR0002", "Proposed")
        self._cr("CR0003", "Superseded")
        self._cr("CR0004", "Rejected")
        self._store(*[self._row(f"LC-00{n}", "RUN-1", state="graduating", cr=f"CR000{n}")
                      for n in (1, 2, 3, 4)])
        res = self._close("RUN-2")
        self.assertEqual({"LC-001": "graduated", "LC-002": "graduating", "LC-003": "graduated",
                          "LC-004": "retired"}, self._classes())
        self.assertEqual(["LC-001", "LC-003"], res.get("graduated"))
        line = lessons.close_pass_line(res)
        self.assertIn("LC-001 graduated (CR0001 Complete)", line)
        self.assertIn("LC-004 retired (CR0004 Rejected, nothing fixed)", line)
        self.assertNotIn("quiet for", line, "a Rejected CR's retirement read as a quiet one")
        rows = {r["id"]: r for r in lessons.load_store(self.root)}
        self.assertEqual("RUN-2", rows["LC-004"].get("retired_run"))
        # A re-run close finds nothing more to move.
        again = self._close("RUN-2")
        self.assertEqual(([], []), (again.get("graduated"), again.get("retired")))

    def test_a_graduation_alone_is_saved(self) -> None:
        """The store is written when the only move is a graduation. MUTANT: leave `graduated`
        out of the save condition - the close reports LC-001 graduated and the file still reads
        `graduating`."""
        self._cr("CR0001", "Complete")
        self._store(self._row("LC-001", "RUN-1", state="graduating", cr="CR0001"))
        res = self._close("RUN-2")
        self.assertEqual(["LC-001"], res["graduated"])
        self.assertEqual({"LC-001": "graduated"}, self._classes())

    def _retro(self, *tries: str) -> None:
        d = self.root / "sdlc-studio" / "retros"
        d.mkdir(parents=True, exist_ok=True)
        body = ["# RETRO-0001: a sprint", "", "> **Date:** 2026-10-01", "> **Batch:** US0001",
                "", "## Keep", "", "- small units", "", "## Stop", "", "- nothing", "",
                "## Try", ""] + [f"- {t}" for t in tries] + [""]
        (d / "RETRO0001-a-sprint.md").write_text("\n".join(body), encoding="utf-8")

    def _sprint_close(self, run: str) -> str:
        """The close's extract-then-close_pass step, as `sprint close` runs it."""
        state = {"run_id": run, "batch": [], "outcome": "running"}
        ok, detail, remedy = sprint._close_retro_extract(self.root, "RETRO0001", state)
        self.assertTrue(ok, f"{detail}\n{remedy}")
        return detail

    def test_a_try_item_hit_lifted_by_the_close_keeps_it_graduating(self) -> None:
        """A retro Try item naming the class is a repeat recorded in this run, by the close's own
        extract before the pass. MUTANT: count only the REJECTs the pass itself cites - LC-001
        then graduates on the very close that recorded it recurring."""
        self._cr("CR0001", "Complete")
        self._store(self._row("LC-001", "RUN-1", state="graduating", cr="CR0001"))
        self._retro("[LC-001] it came back on US0001")
        self._sprint_close("RUN-A")
        rows = {r["id"]: r for r in lessons.load_store(self.root)}
        self.assertIn("RUN-A", [h["run"] for h in rows["LC-001"]["hits"]],
                      "the extract did not record the Try item as a hit, so this proves nothing")
        self.assertEqual({"LC-001": "graduating"}, self._classes())

    def test_a_rerun_close_keeps_a_class_it_kept_graduating(self) -> None:
        """Idempotence. MUTANT: judge only hits this pass ADDED - the re-run adds none, so the
        second pass of the same close graduates the class the first pass kept."""
        self._cr("CR0001", "Complete")
        self._store(self._row("LC-001", "RUN-1", state="graduating", cr="CR0001"))
        cite = [("LC-001", "US0009", "[new] again [LC-001]")]
        state = {"run_id": "RUN-2", "batch": []}
        with mock.patch("critic.cited_lessons", return_value=cite):
            first = lessons.close_pass(self.root, "RUN-2", state)
            second = lessons.close_pass(self.root, "RUN-2", state)
        self.assertEqual((1, 0), (first["hits"], second["hits"]))
        self.assertEqual({"LC-001": "graduating"}, self._classes())

    def test_a_class_hit_in_the_closing_run_stays_graduating(self) -> None:
        """A repeat in the very close that would graduate the class is evidence the fix has not
        held. MUTANT: graduate whatever this close recorded - LC-001 graduates with a fresh hit."""
        self._cr("CR0001", "Complete")
        self._store(self._row("LC-001", "RUN-1", state="graduating", cr="CR0001"))
        # Patch by name: close_pass does `import critic` at call time, which resolves
        # sys.modules["critic"]; other modules in one discovery run replace that entry, so a
        # patch on this module's own loaded object can miss the one close_pass reads.
        with mock.patch("critic.cited_lessons",
                        return_value=[("LC-001", "US0009", "[new] again [LC-001]")]):
            res = lessons.close_pass(self.root, "RUN-2", {"run_id": "RUN-2", "batch": []})
        self.assertEqual(1, res["hits"])
        self.assertEqual({"LC-001": "graduating"}, self._classes())

    def test_a_class_recorded_in_another_clone_retires_when_quiet(self) -> None:
        """AC2. MUTANT: HEAD, which keeps LC-001 active because RUN-B1 is in no window this
        clone knows. MUTANT: retire on unknown runs alone, ignoring the window - LC-002, hit in
        RUN-6, which this clone knows and is one of its last five, retires too. MUTANT: judge
        before this clone has seen a full window - with five runs on record LC-001 retires."""
        self._store(self._row("LC-001", "RUN-B1", "RUN-B4"),
                    self._row("LC-002", "RUN-B1", "RUN-6"))
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4")
        self._close("RUN-5")
        self.assertEqual({"LC-001": "active", "LC-002": "active"}, self._classes(),
                         "five runs on record are one window, with no run yet older than it")
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4", "RUN-5", "RUN-6")
        res = self._close("RUN-7")
        self.assertEqual({"LC-001": "retired", "LC-002": "active"}, self._classes())
        self.assertEqual(["LC-001"], res["retired"])


def _log(*ids: int) -> str:
    """A committed project log holding open lessons with these numbers, newest first."""
    head = "# Project Lessons\n\n**Last Updated:** 2026-01-01\n"
    return head + "".join(
        f"\n## L-{n:04d}: Lesson {n}\n\n- **Added:** 2026-01-01\n- **Review-by:** 2026-04-01\n\n"
        f"Body of lesson {n}.\n" for n in sorted(ids, reverse=True))


class RevalidationRecordTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.log = self.root / lessons.DEFAULT_PROJECT_FILE
        self.log.parent.mkdir(parents=True)
        self.log.write_text(_log(1, 2, 3, 4, 5, 6, 7), encoding="utf-8")

    def _main(self, today: str, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(lessons.sdlc_md, "now_date", return_value=today), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = lessons.main(["revalidate", "--root", str(self.root), *argv])
        return rc, out.getvalue(), err.getvalue()

    def _script(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "lessons.py"), "revalidate", "--root",
             str(self.root), *argv], capture_output=True, text=True, check=False, timeout=120)

    def _entry(self, lid: str) -> dict:
        return {e["id"]: e for e in
                lessons.parse_project_lessons(self.log.read_text(encoding="utf-8"))}[lid]

    def _open_rows(self) -> dict:
        rc, out, err = self._main("2026-06-02", "--format", "json")
        self.assertEqual(0, rc, err)
        return {r["id"]: r for r in json.loads(out)["open"]}

    def test_an_extension_records_its_date_and_reason(self) -> None:
        """AC1. MUTANT: HEAD, which moves Review-by and drops the reason - no Revalidated line.
        MUTANT: append the bullet rather than replace it - the second extension leaves two.
        MUTANT: stop moving Review-by - the horizon stays 2026-04-01. MUTANT: stamp every open
        lesson - L-0001, never extended, gains a record. MUTANT: leave the record out of the
        `--format json` rows - the read-back misses it."""
        rc, _, err = self._main("2026-06-01", "--extend", "L-0002", "L-0003", "--reason",
                                "still true: the hook refuses it")
        self.assertEqual(0, rc, err)
        self.assertIn("- **Revalidated:** 2026-06-01 - still true: the hook refuses it",
                      self._entry("L-0002")["body"])
        self.assertEqual("2026-08-30", self._entry("L-0002")["fields"]["review-by"])  # +90 days
        rc, _, err = self._main("2026-07-01", "--extend", "L-0002", "--reason", "rechecked")
        self.assertEqual(0, rc, err)
        body = self._entry("L-0002")["body"]
        self.assertEqual(1, body.count("**Revalidated:**"), body)
        self.assertIn("- **Revalidated:** 2026-07-01 - rechecked", body)
        self.assertEqual("2026-09-29", self._entry("L-0002")["fields"]["review-by"])
        self.assertNotIn("Revalidated", self._entry("L-0001")["body"])
        rows = self._open_rows()
        self.assertEqual(("2026-07-01", "rechecked"),
                         (rows["L-0002"]["revalidated"], rows["L-0002"]["revalidated_reason"]))
        self.assertEqual(("2026-06-01", "still true: the hook refuses it"),
                         (rows["L-0003"]["revalidated"], rows["L-0003"]["revalidated_reason"]))
        self.assertEqual((None, None),
                         (rows["L-0001"]["revalidated"], rows["L-0001"]["revalidated_reason"]))

    def test_a_multi_line_reason_is_recorded_on_one_line(self) -> None:
        """A --fields-file reason may carry newlines; a bullet cut by one parses back as its first
        line. MUTANT: write the reason verbatim - the read-back reason loses its second line."""
        doc = self.root / "fields.json"
        doc.write_text(json.dumps({"reason": "checked `gate.py`\nand the hook"}),
                       encoding="utf-8")
        rc, _, err = self._main("2026-06-01", "--extend", "L-0004", "--fields-file", str(doc))
        self.assertEqual(0, rc, err)
        self.assertEqual("checked `gate.py` and the hook",
                         self._open_rows()["L-0004"]["revalidated_reason"])

    def test_an_extension_with_no_reason_is_refused_by_name(self) -> None:
        """AC2. MUTANT: HEAD, which exits 0 and moves Review-by with no reason. MUTANT: refuse
        only a missing flag - `--reason "   "` passes and writes a blank record. Positive
        control: the same call with a reason writes."""
        before = self.log.read_bytes()
        for extra in ([], ["--reason", "   "]):
            rc, _, err = self._main("2026-06-01", "--extend", "L-0002", *extra)
            self.assertEqual(2, rc, f"{extra}: {err}")
            self.assertIn("--reason", err)
            self.assertEqual(before, self.log.read_bytes(), f"{extra} wrote the log")
        rc, _, err = self._main("2026-06-01", "--extend", "L-0002", "--reason", "holds")
        self.assertEqual(0, rc, err)
        self.assertNotEqual(before, self.log.read_bytes())

    def test_unjudged_since_lists_each_unjudged_open_lesson_in_the_range(self) -> None:
        """AC3, through the script. In L-0002:L-0006, L-0002 and L-0006 are the bounds and never
        judged, L-0003 is closed, L-0004 was extended on the date and L-0005 the day before.
        MUTANT: `>` for `>=` - L-0004 is listed. MUTANT: ignore the close - L-0003 is listed.
        MUTANT: ignore the range - L-0001 and L-0007 are listed. MUTANT: an exclusive bound -
        L-0002 or L-0006 is missed. MUTANT: exit 0 with rows listed. Positive control: once
        the three are extended on the date, it exits 0."""
        self._main("2026-06-01", "--close", "L-0003", "--reason", "fixed in the tool")
        self._main("2026-07-01", "--extend", "L-0004", "--reason", "rechecked")
        self._main("2026-06-30", "--extend", "L-0005", "--reason", "an earlier pass")
        proc = self._script("--unjudged-since", "2026-07-01", "--range", "L-0002:L-0006")
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)
        listed = [ln.split()[0] for ln in proc.stdout.splitlines() if ln.startswith("L-")]
        self.assertEqual(["L-0006", "L-0005", "L-0002"], listed)
        self.assertIn("L-0005  Lesson 5  [last revalidated 2026-06-30]", proc.stdout)
        self.assertIn("L-0002  Lesson 2  [never revalidated]", proc.stdout)
        self.assertIn("3 of 4 open lesson(s) in L-0002:L-0006 unjudged since 2026-07-01",
                      proc.stdout)
        proc = self._script("--unjudged-since", "2026-07-01", "--range", "L-0002:L-0006",
                            "--format", "json")
        self.assertEqual(1, proc.returncode, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertEqual((["L-0006", "L-0005", "L-0002"], 3, 4),
                         ([r["id"] for r in data["unjudged"]], data["count"], data["open"]))
        self.assertEqual("an earlier pass", data["unjudged"][1]["revalidated_reason"])
        self._main("2026-07-01", "--extend", "L-0002", "L-0005", "L-0006", "--reason", "holds")
        proc = self._script("--unjudged-since", "2026-07-01", "--range", "L-0002:L-0006")
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("0 of 4 open lesson(s) in L-0002:L-0006 unjudged since 2026-07-01",
                      proc.stdout)

    def test_a_check_that_could_pass_vacuously_is_refused(self) -> None:
        """A malformed date or range, a range naming no lesson, or --range on its own would
        otherwise judge nothing and could exit 0. MUTANT: drop the empty-scope refusal -
        L-0100:L-0200 exits 0. MUTANT: drop the date check - `2026-7-1` is compared as text and
        answers 1 rather than refusing. Positive control: the well-formed call exits 1."""
        for argv, needle in ((["--unjudged-since", "2026-7-1"], "YYYY-MM-DD"),
                             (["--unjudged-since", "2026-13-01"], "YYYY-MM-DD"),
                             (["--unjudged-since", "2026-07-01", "--range", "L-1:L-9"],
                              "L-NNNN:L-NNNN"),
                             (["--unjudged-since", "2026-07-01", "--range", "L-0006:L-0002"],
                              "backwards"),
                             (["--unjudged-since", "2026-07-01", "--range", "L-0100:L-0200"],
                              "no lesson in L-0100:L-0200"),
                             (["--range", "L-0001:L-0002"], "--unjudged-since")):
            proc = self._script(*argv)
            self.assertEqual(2, proc.returncode, f"{argv}: {proc.stdout}{proc.stderr}")
            self.assertIn(needle, proc.stderr, argv)
        proc = self._script("--unjudged-since", "2026-07-01", "--range", "L-0001:L-0002")
        self.assertEqual(1, proc.returncode, proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
