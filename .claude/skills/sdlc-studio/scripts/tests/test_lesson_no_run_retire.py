"""A lesson class recorded with no run open gets its full quiet window, and class-add refuses
every blank field.

`lessons.py class-add` stamps an empty `recorded_run` when no run is open, and a manual
`retro.py extract` stamps the retro id. The close retires a class none of whose runs is in its
last QUIET_RUNS, so once this clone had archived more runs than that, a class recorded between
runs retired at the very next close unless that run happened to hit it (LC-001 did, in a probe).
A class recorded with no run now takes the next run to close as the start of its quiet window.

The same review found class-add's blank-field refusal tested for `--rule` alone and its
unreadable-run-state refusal not at all. Each case runs the shipped entry point over a
throwaway project.
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lessons  # noqa: E402
import retro  # noqa: E402
from lib import run_state  # noqa: E402

RID = "RETRO9999"


class _Project(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="no_run_retire_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        self._archive(*(f"RUN-{n}" for n in range(1, 7)))

    def _archive(self, *runs: str) -> None:
        for run in runs:
            n = int(run.split("-")[1]) if run.split("-")[1].isdigit() else 0
            run_state.archive(self.root, {"run_id": run, "outcome": "goal-reached",
                                          "started_at": f"2026-09-{n + 1:02d}T08:00:00Z"})

    def _store(self, *rows: dict) -> None:
        (self.root / lessons.STORE_FILE).write_text(
            "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def _class_add(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = lessons.main(["class-add", *argv, "--root", str(self.root)])
            except SystemExit as exc:      # argparse refuses a value outside the choices
                rc = int(exc.code or 0)
        return rc, out.getvalue(), err.getvalue()

    def _close(self, run: str) -> dict:
        return lessons.close_pass(self.root, run, {"run_id": run, "batch": []})

    def _row(self, code: str) -> dict:
        return next(r for r in lessons.load_store(self.root) if r["id"] == code)


QUIET = ("--class", "a quiet trap", "--rule", "A rule that holds.", "--behaviour",
         "Do it differently.", "--phase", "review", "--source", "a mid-run finding")


class NoRunRetireTests(_Project):

    def test_a_class_added_with_no_run_open_survives_the_next_close(self) -> None:
        """AC1, by class-add. MUTANT: HEAD - LC-002 retires at RUN-7's close. The window then
        runs its full QUIET_RUNS: active through RUN-11, retired at RUN-12. MUTANT: restamp the
        window's start at every close - it never retires. LC-001, recorded in a run this clone
        never saw, still retires at RUN-7 as it always has. MUTANT: give every unknown run a
        window - LC-001 stays."""
        self._store({"id": "LC-001", "class": "another clone's trap", "rule": "r.",
                     "behaviour": "b.", "inject": ["review"], "hits": [], "state": "active",
                     "recorded_run": "RUN-B1", "recorded_source": "retro:RETRO0001"})
        rc, out, err = self._class_add(*QUIET)
        self.assertEqual(0, rc, out + err)
        self.assertEqual("", self._row("LC-002")["recorded_run"], "no run was open")
        res = self._close("RUN-7")
        self.assertEqual("active", self._row("LC-002")["state"])
        self.assertEqual("RUN-7", self._row("LC-002")["quiet_from"])
        self.assertEqual(["LC-001"], res["retired"])
        self.assertEqual(["LC-002"], res["quiet_from"])
        self.assertIn("recorded with no run, quiet window from this run: LC-002",
                      lessons.close_pass_line(res))
        again = self._close("RUN-7")
        self.assertEqual([], again["quiet_from"], "a re-run close stamps nothing")
        self.assertNotIn("recorded with no run", lessons.close_pass_line(again))
        for n in range(8, 12):
            self._archive(f"RUN-{n - 1}")
            self._close(f"RUN-{n}")
            self.assertEqual("active", self._row("LC-002")["state"], f"RUN-{n}")
        self._archive("RUN-11")
        self.assertEqual(["LC-002"], self._close("RUN-12")["retired"])
        self.assertEqual("RUN-7", self._row("LC-002")["quiet_from"])

    def test_a_class_extracted_with_no_run_open_survives_the_next_close(self) -> None:
        """AC1, by a manual `retro.py extract`, which names the retro as the class's run.
        MUTANT: HEAD - it retires at RUN-7's close. MUTANT: save the store only when a hit, a
        retirement or a graduation moved it - the stamp is lost when nothing else changed."""
        (self.root / "sdlc-studio" / "retros" / f"{RID}-a-run.md").write_text(
            "# RETRO-9999: a run\n\n> **Date:** 2026-11-22\n> **Run:** -\n> **Batch:** US0001\n\n"
            "## Keep\n\n- the gate\n\n## Stop\n\n- the wait\n\n## Try\n\n"
            "- [new: a quiet trap | review] A rule that holds. Do it differently.\n",
            encoding="utf-8")
        self._store()
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = retro.main(["--root", str(self.root), "extract", "--id", RID])
        self.assertEqual(0, rc, out.getvalue() + err.getvalue())
        self.assertEqual(RID, self._row("LC-001")["recorded_run"])
        self._close("RUN-7")
        self.assertEqual("active", self._row("LC-001")["state"])
        self.assertEqual("RUN-7", self._row("LC-001").get("quiet_from"),
                         "the stamp is saved when it is the only change")

    def test_a_class_with_no_run_that_is_not_active_is_left_alone(self) -> None:
        """Only an active class is given a window: a graduating or retired one recorded with no
        run is not stamped, so the store is not rewritten for it."""
        self._store(*({"id": f"LC-00{n}", "class": f"c{n}", "rule": "r.", "behaviour": "b.",
                       "inject": ["review"], "hits": [], "state": state, "recorded_run": ""}
                      for n, state in ((1, "graduating"), (2, "retired"))))
        before = (self.root / lessons.STORE_FILE).read_bytes()
        res = self._close("RUN-7")
        self.assertEqual([], res["quiet_from"])
        self.assertEqual(before, (self.root / lessons.STORE_FILE).read_bytes())


class ClassAddRefusalTests(_Project):

    def setUp(self) -> None:
        super().setUp()
        self._store({"id": "LC-001", "class": "a held trap", "rule": "r.", "behaviour": "b.",
                     "inject": ["build"], "hits": [], "state": "active", "recorded_run": "RUN-1"})
        self.before = (self.root / lessons.STORE_FILE).read_bytes()

    def _untouched(self) -> None:
        self.assertEqual(self.before, (self.root / lessons.STORE_FILE).read_bytes())

    def test_each_blank_required_field_is_refused_and_the_store_is_untouched(self) -> None:
        """AC2. MUTANT: check only `--rule` - a blank class, behaviour or source is written."""
        for flag in ("--class", "--rule", "--behaviour", "--source"):
            with self.subTest(flag=flag):
                argv = list(QUIET)
                argv[argv.index(flag) + 1] = "   "
                rc, out, err = self._class_add(*argv)
                self.assertEqual(1, rc, out + err)
                self.assertIn(f"{flag} must not be blank", err)
                self._untouched()

    def test_a_blank_phase_is_refused_and_the_store_is_untouched(self) -> None:
        """AC2, the fifth required field: a blank `--phase` is no phase, refused by the parser."""
        argv = list(QUIET)
        argv[argv.index("--phase") + 1] = ""
        rc, _out, err = self._class_add(*argv)
        self.assertEqual(2, rc)
        self.assertIn("--phase", err)
        self._untouched()

    def test_an_unreadable_run_state_is_refused_and_the_store_is_untouched(self) -> None:
        """AC2. A class stamped with no run while one is open is a repeat the close cannot count,
        so an unreadable run state refuses rather than reading as no run."""
        run_state.path(self.root).write_text("{not json", encoding="utf-8")
        rc, out, err = self._class_add(*QUIET)
        self.assertEqual(1, rc, out + err)
        self.assertIn("class-add refused", err)
        self.assertIn("not valid JSON", err)
        self._untouched()

    def test_every_field_given_records_the_class(self) -> None:
        """The positive control: the same command with every field filled appends LC-002."""
        rc, out, err = self._class_add(*QUIET)
        self.assertEqual(0, rc, out + err)
        self.assertEqual(["LC-001", "LC-002"], [r["id"] for r in lessons.load_store(self.root)])


if __name__ == "__main__":
    unittest.main()
