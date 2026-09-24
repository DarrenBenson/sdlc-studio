"""US0887: a lesson is a failure class that counts its repeats and reaches the work.

The store is one committed file, `sdlc-studio/lessons.jsonl`, one row per failure class. A retro
Try item names its class - `[LC-003]` for a class already recorded, `[new: <class name>]` for a
new one - and the close counts a repeat as a hit on the class instead of writing the lesson again.
The plan output, a build brief and a review brief each carry the active lessons injected at that
phase, as rule plus behaviour, at most five.

Driven through `retro.main` and `sprint.main`, the shipped entry points, in throwaway trees.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

lessons = loader.load_script("lessons")
retro = loader.load_script("retro")
sprint = loader.load_script("sprint")

STORE = Path("sdlc-studio") / "lessons.jsonl"
FIELDS = {"id", "class", "rule", "behaviour", "inject", "hits", "state"}
NEW_TRY = ("[new: mutant never applied] Assert a mutation applied before trusting its verdict. "
           "Count the replaced text first and refuse the run when it is not exactly one.")


def _retro(root: Path, *tries: str) -> None:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    body = ["# RETRO-0001: a sprint", "", "> **Date:** 2026-09-24", "> **Batch:** US0001", "",
            "## Keep", "", "- small units", "", "## Stop", "", "- plan review", "",
            "## Try", ""] + [f"- {t}" for t in tries] + [""]
    (d / "RETRO0001-a-sprint.md").write_text("\n".join(body), encoding="utf-8")


def _extract(root: Path, run: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = retro.main(["--root", str(root), "extract", "--id", "RETRO0001", "--run", run])
    return rc, out.getvalue()


def _rows(root: Path) -> list[dict]:
    path = root / STORE
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _row(n: int, inject, *, hits: int = 0, state: str = "active") -> dict:
    return {"id": f"LC-{n:03d}", "class": f"class {n}", "rule": f"Rule {n} holds.",
            "behaviour": f"Behaviour {n} follows.", "inject": list(inject),
            "hits": [{"run": f"RUN-{i}", "unit": "", "source": "retro:RETRO0001"}
                     for i in range(hits)],
            "state": state, "recorded_run": "RUN-0"}


class LessonStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_a_lesson_row_carries_its_fields(self) -> None:
        """AC1. MUTANT: write the lesson to the gitignored `.local/` prose log, or drop a field
        from the row - the store then holds nothing the next run can count or inject."""
        _retro(self.root, NEW_TRY)
        rc, out = _extract(self.root, "RUN-A")
        self.assertEqual(0, rc, out)
        self.assertEqual(STORE.as_posix(), lessons.STORE_FILE)
        rows = _rows(self.root)
        self.assertEqual(1, len(rows), rows)
        row = rows[0]
        self.assertLessEqual(FIELDS, set(row), f"missing: {FIELDS - set(row)}")
        self.assertRegex(row["id"], r"^LC-\d{3}$")
        self.assertEqual("mutant never applied", row["class"])
        self.assertEqual("Assert a mutation applied before trusting its verdict.", row["rule"])
        self.assertIn("exactly one", row["behaviour"])
        self.assertEqual(["plan", "build", "review"], row["inject"])
        self.assertEqual([], row["hits"], "recording a class is not a repeat of it")
        self.assertEqual("active", row["state"])
        self.assertEqual("RUN-A", row["recorded_run"])
        # A narrowed injection and a malformed one.
        _retro(self.root, "[new: scope drift | build, review] Review only the unit's diff. "
                          "Run git log -S before calling a finding a regression.")
        self.assertEqual(0, _extract(self.root, "RUN-A")[0])
        self.assertEqual(["build", "review"], _rows(self.root)[1]["inject"])
        _retro(self.root, "[new: bad phase | deploy] A rule. A behaviour.")
        rc, out = _extract(self.root, "RUN-A")
        self.assertNotEqual(0, rc)
        self.assertIn("deploy", out)
        # A new class with no behaviour sentence is incomplete, and refused by the validator.
        _retro(self.root, "[new: rule only] A rule with nothing to do differently.")
        res = retro.validate(self.root, "RETRO0001")
        self.assertFalse(res["ok"])
        self.assertTrue(any("behaviour" in e for e in res["errors"]), res["errors"])

    def test_a_repeat_is_a_hit_not_a_new_lesson(self) -> None:
        """AC2. MUTANT: mint a row for every Try item, as the prose log did - a class that
        recurs is then written again as a new lesson and its repeats are never counted."""
        _retro(self.root, NEW_TRY)
        self.assertEqual(0, _extract(self.root, "RUN-A")[0])
        code = _rows(self.root)[0]["id"]
        prose = lessons.default_project_file(self.root)

        _retro(self.root, f"[{code}] It happened again on US0005; the mutant never landed.")
        rc, out = _extract(self.root, "RUN-B")
        self.assertEqual(0, rc, out)
        rows = _rows(self.root)
        self.assertEqual(1, len(rows), "a repeat was written as a new lesson")
        self.assertEqual([{"run": "RUN-B", "unit": "US0005", "source": "retro:RETRO0001"}],
                         rows[0]["hits"])
        self.assertFalse(prose.is_file(), "a classed Try item also went to the prose log")
        # A re-run close counts the same repeat once.
        self.assertEqual(0, _extract(self.root, "RUN-B")[0])
        self.assertEqual(1, len(_rows(self.root)[0]["hits"]))

        # Naming the class again as `new` in a later run is a repeat too, not a second row.
        _retro(self.root, NEW_TRY.replace("mutant never applied", "Mutant  Never Applied"))
        self.assertEqual(0, _extract(self.root, "RUN-C")[0])
        rows = _rows(self.root)
        self.assertEqual(1, len(rows))
        self.assertEqual(["RUN-B", "RUN-C"], [h["run"] for h in rows[0]["hits"]])

        # A new class writes a new row.
        _retro(self.root, "[new: review scope drift] Review only the unit's diff. Run git "
                          "log -S before calling a finding a regression.")
        self.assertEqual(0, _extract(self.root, "RUN-C")[0])
        rows = _rows(self.root)
        self.assertEqual([code, "LC-002"], [r["id"] for r in rows])
        self.assertEqual([], rows[1]["hits"])

        # An unknown code is refused and the store is left as it was.
        before = (self.root / STORE).read_text(encoding="utf-8")
        _retro(self.root, "[LC-099] no such class.")
        rc, out = _extract(self.root, "RUN-D")
        self.assertNotEqual(0, rc)
        self.assertIn("LC-099", out)
        self.assertEqual(before, (self.root / STORE).read_text(encoding="utf-8"))

    def test_lessons_reach_the_phase_they_inject(self) -> None:
        """AC3. MUTANT: keep briefing the frozen LESSONS-TOP titles, or render every active
        lesson whatever its phase - the rule then never reaches the work, or every brief
        carries every lesson and none is read."""
        rows = [_row(n, ("build",), hits=n) for n in range(1, 7)]      # six build lessons
        rows += [_row(7, ("plan",)), _row(8, ("review",)),
                 _row(9, ("plan", "build", "review"), hits=9, state="retired")]
        store = self.root / STORE
        store.parent.mkdir(parents=True, exist_ok=True)
        store.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
        # The old carried set, which must no longer reach any brief.
        top = self.root / "sdlc-studio" / "retros" / "LESSONS-TOP.md"
        top.parent.mkdir(parents=True, exist_ok=True)
        top.write_text("# Carried\n\n## 1. A frozen carried title\n\nbody\n", encoding="utf-8")
        bug = self.root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        bug.parent.mkdir(parents=True, exist_ok=True)
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("", encoding="utf-8")
        bug.write_text("# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
                       "> **Affects:** src/a.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
                       "### AC1: it holds\n\n- **Verify:** shell true\n", encoding="utf-8")
        worklist = self.root / "wl.txt"
        worklist.write_text("BG0001\n", encoding="utf-8")

        def run(*argv: str) -> str:
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                rc = sprint.main([*argv, "--root", str(self.root)])
            self.assertEqual(0, rc, out.getvalue())
            return out.getvalue()

        rendered = {
            "plan": run("plan", "--worklist", str(worklist), "--no-fetch"),
            "build": run("lane", "brief", "--units", "BG0001"),
            "review": run("goal-review", "brief", "--brief-worklist", str(worklist)),
        }
        expect = {"plan": ["LC-007"], "review": ["LC-008"],
                  # the five most-hit build lessons; LC-001 is the sixth, and the cap drops it
                  "build": ["LC-006", "LC-005", "LC-004", "LC-003", "LC-002"]}
        for phase, text in rendered.items():
            with self.subTest(phase=phase):
                shown = re.findall(r"\bLC-\d{3}\b", text)
                self.assertEqual(expect[phase], shown, text)
                for code in expect[phase]:
                    n = int(code[3:])
                    self.assertIn(f"Rule {n} holds.", text)
                    self.assertIn(f"Behaviour {n} follows.", text)
                self.assertNotIn("A frozen carried title", text)
                self.assertNotIn("Rule 9 holds.", text, "a retired lesson was injected")
        self.assertIn("+1 more", rendered["build"], "the cap dropped a lesson silently")


if __name__ == "__main__":
    unittest.main()
