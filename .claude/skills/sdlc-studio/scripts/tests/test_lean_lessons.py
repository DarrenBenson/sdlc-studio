"""US0887: a lesson is a failure class that counts its repeats and reaches the work.

The store is one committed file, `sdlc-studio/lessons.jsonl`, one row per failure class. A retro
Try item names its class - `[LC-003]` for a class already recorded, `[new: <class name>]` for a
new one - and the close counts a repeat as a hit on the class instead of writing the lesson again.
The plan output, a build brief and a review brief each carry the active lessons injected at that
phase, as rule plus behaviour, at most five, and no other lessons.

US0888: the close measures and acts on the store. A REJECT whose findings cite a class code
(`[LC-003]`) is a hit for the run; a class repeated twice after it was recorded files one CR
proposing a check and reads `graduating`; a class quiet for its last five runs retires; and the
report appendix lists each live class's hits this run and in total.

Driven through `retro.main`, `sprint.main`, `lessons.main`, `critic.brief`, the close's own step
and `sprint_report`, the shipped entry points, in throwaway trees.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

lessons = loader.load_script("lessons")
retro = loader.load_script("retro")
sprint = loader.load_script("sprint")
critic = loader.load_script("critic")


class _AtTestTime:
    """`sprint_report`, loaded when a test first uses it rather than at discovery. A later module
    replaces `sys.modules["retro"]` while the suite is discovered, so loading it here would bind
    it to a `retro` those modules no longer see, and their patches of `retro` would miss it."""

    def __getattr__(self, name):
        return getattr(loader.load_script("sprint_report"), name)


sprint_report = _AtTestTime()

STORE = Path("sdlc-studio") / "lessons.jsonl"
FIELDS = {"id", "class", "rule", "behaviour", "inject", "hits", "state"}
NEW_TRY = ("[new: mutant never applied] Assert a mutation applied before trusting its verdict. "
           "Count the replaced text first and refuse the run when it is not exactly one.")
RUN = "RUN-LEAN0001"


def _live(name: str):
    """The module the close resolves at call time (see test_lean_close): whatever
    `sys.modules` holds now, so a patch lands on the instance the close reads."""
    return sys.modules.get(name) or importlib.import_module(name)


def _retro(root: Path, *tries: str, rid: str = "RETRO0001") -> None:
    d = root / "sdlc-studio" / "retros"
    d.mkdir(parents=True, exist_ok=True)
    for old in d.glob(f"{rid}-*.md"):
        old.unlink()
    n = int(rid[5:])
    body = [f"# RETRO-{n:04d}: a sprint", "", "> **Date:** 2026-09-24", "> **Batch:** US0101", "",
            "## Keep", "", "- small units", "", "## Stop", "", "- plan review", "",
            "## Try", ""] + [f"- {t}" for t in tries] + [""]
    (d / f"{rid}-a-sprint.md").write_text("\n".join(body), encoding="utf-8")


def _cli(main, argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = main(argv)
    return rc, out.getvalue()


def _extract(root: Path, run: str | None, rid: str = "RETRO0001") -> tuple[int, str]:
    argv = ["--root", str(root), "extract", "--id", rid]
    return _cli(retro.main, argv + (["--run", run] if run else []))


def _rows(root: Path) -> list[dict]:
    path = root / STORE
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _row(n: int, inject, *, hits: int = 0, state: str = "active") -> dict:
    return {"id": f"LC-{n:03d}", "class": f"class {n}", "rule": f"Rule {n} holds.",
            "behaviour": f"Behaviour {n} follows.", "inject": list(inject),
            "hits": [{"run": f"RUN-{i}", "unit": "", "source": f"retro:RETRO{i:04d}"}
                     for i in range(hits)],
            "state": state, "recorded_run": "RUN-0"}


def _store(root: Path, *rows: dict) -> Path:
    path = root / STORE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def _open_run(root: Path, run: str = RUN) -> None:
    """An open run's state, in the shape `sprint plan --write` leaves it."""
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({
        "schema": 1, "run_id": run, "started_at": "2026-09-24T00:00:00Z", "ended_at": None,
        "outcome": "running", "goal": "done", "batch": ["US0101"], "handoff": None,
        "appetite": {"minutes": 240.0, "units": 8}, "sprint_goal": "the close finishes",
        "sprint_goal_verdict": {"verdict": "achieved", "note": "it did"}}), encoding="utf-8")


class LessonStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        _store(self.root)  # a project store with no classes yet, so the seed is not read

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
        self.assertEqual("retro:RETRO0001", row["recorded_source"])
        # A narrowed injection and a malformed one.
        _retro(self.root, "[new: scope drift | build, review] Review only the unit's diff. "
                          "Run git log -S before calling a finding a regression.", rid="RETRO0002")
        self.assertEqual(0, _extract(self.root, "RUN-B", "RETRO0002")[0])
        self.assertEqual(["build", "review"], _rows(self.root)[1]["inject"])
        _retro(self.root, "[new: bad phase | deploy] A rule. A behaviour.", rid="RETRO0003")
        rc, out = _extract(self.root, "RUN-C", "RETRO0003")
        self.assertNotEqual(0, rc)
        self.assertIn("deploy", out)
        # A new class with no behaviour sentence is incomplete, and refused by the validator.
        _retro(self.root, "[new: rule only] A rule with nothing to do differently.",
               rid="RETRO0003")
        res = retro.validate(self.root, "RETRO0003")
        self.assertFalse(res["ok"])
        self.assertTrue(any("behaviour" in e for e in res["errors"]), res["errors"])

    def test_a_repeat_is_a_hit_not_a_new_lesson(self) -> None:
        """AC2. MUTANT: mint a row for every Try item, as the prose log did - a class that
        recurs is then written again as a new lesson and its repeats are never counted."""
        _retro(self.root, NEW_TRY)
        self.assertEqual(0, _extract(self.root, "RUN-A")[0])
        code = _rows(self.root)[0]["id"]
        prose = lessons.default_project_file(self.root)

        _retro(self.root, f"[{code}] It happened again on US0005; the mutant never landed.",
               rid="RETRO0002")
        rc, out = _extract(self.root, "RUN-B", "RETRO0002")
        self.assertEqual(0, rc, out)
        rows = _rows(self.root)
        self.assertEqual(1, len(rows), "a repeat was written as a new lesson")
        self.assertEqual([{"run": "RUN-B", "unit": "US0005", "source": "retro:RETRO0002"}],
                         rows[0]["hits"])
        self.assertFalse(prose.is_file(), "a classed Try item also went to the prose log")
        # A re-run close counts the same repeat once.
        self.assertEqual(0, _extract(self.root, "RUN-B", "RETRO0002")[0])
        self.assertEqual(1, len(_rows(self.root)[0]["hits"]))

        # Naming the class again as `new` in a later retro is a repeat too, not a second row.
        _retro(self.root, NEW_TRY.replace("mutant never applied", "Mutant  Never Applied"),
               rid="RETRO0003")
        self.assertEqual(0, _extract(self.root, "RUN-C", "RETRO0003")[0])
        rows = _rows(self.root)
        self.assertEqual(1, len(rows))
        self.assertEqual(["RUN-B", "RUN-C"], [h["run"] for h in rows[0]["hits"]])

        # A new class writes a new row.
        _retro(self.root, "[new: review scope drift] Review only the unit's diff. Run git "
                          "log -S before calling a finding a regression.", rid="RETRO0004")
        self.assertEqual(0, _extract(self.root, "RUN-D", "RETRO0004")[0])
        rows = _rows(self.root)
        self.assertEqual([code, "LC-002"], [r["id"] for r in rows])
        self.assertEqual([], rows[1]["hits"])

        # An unknown code is refused and the store is left as it was.
        before = (self.root / STORE).read_text(encoding="utf-8")
        _retro(self.root, "[LC-099] no such class.", rid="RETRO0005")
        rc, out = _extract(self.root, "RUN-E", "RETRO0005")
        self.assertNotEqual(0, rc)
        self.assertIn("LC-099", out)
        self.assertEqual(before, (self.root / STORE).read_text(encoding="utf-8"))

    def test_lessons_reach_the_phase_they_inject(self) -> None:
        """AC3. MUTANT: keep briefing the frozen LESSONS-TOP titles, the prose digest or the
        cross-project titles, or render every active lesson whatever its phase - the rule then
        never reaches the work, or every brief carries every lesson and none is read."""
        _store(self.root, *[_row(n, ("build",), hits=n) for n in range(1, 7)],  # six build
               _row(7, ("plan",)), _row(8, ("review",)),
               _row(9, ("plan", "build", "review"), hits=9, state="retired"))
        # The old carried set and the prose log, which must no longer reach any brief.
        top = self.root / "sdlc-studio" / "retros" / "LESSONS-TOP.md"
        top.parent.mkdir(parents=True, exist_ok=True)
        top.write_text("# Carried\n\n## 1. A frozen carried title\n\nbody\n", encoding="utf-8")
        prose = self.root / "sdlc-studio" / ".local" / "lessons.md"
        prose.parent.mkdir(parents=True, exist_ok=True)
        prose.write_text("# Project Lessons\n\n## L-0001: A prose digest title\n\n"
                         "- **Rule:** read the log\n", encoding="utf-8")
        bug = self.root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        bug.parent.mkdir(parents=True, exist_ok=True)
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("", encoding="utf-8")
        bug.write_text("# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
                       "> **Affects:** src/a.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
                       "### AC1: it holds\n\n- **Verify:** shell true\n", encoding="utf-8")
        seats = self.root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "qa.md").write_text("# QA seat\n", encoding="utf-8")
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
            # the review brief the runbook names, in both of its phases
            "critic": critic.brief(self.root, "BG0001", "qa"),
            "critic-plan": critic.brief(self.root, "BG0001", "qa", phase="plan-review"),
        }
        expect = {"plan": ["LC-007"], "review": ["LC-008"], "critic": ["LC-008"],
                  "critic-plan": ["LC-008"],
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
                self.assertNotIn("Rule 9 holds.", text, "a retired lesson was injected")
                # only the class store's lessons: no curated titles, no prose digest, no
                # cross-project registry
                self.assertNotIn("A frozen carried title", text)
                self.assertNotIn("A prose digest title", text)
                self.assertNotRegex(text, r"\bLL\d{4}\b")
        self.assertIn("+1 more", rendered["build"], "the cap dropped a lesson silently")
        for phase in ("critic", "critic-plan"):
            self.assertIn("cites its class code", rendered[phase])


class OneRepeatCountsOnceTests(unittest.TestCase):
    """Review round 1: a manual `retro.py extract` (the runbook's close step) followed by the
    close's own counted one repeat twice, because the manual call defaulted its run to the retro
    id and a hit was keyed on the run."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        _store(self.root)  # a project store with no classes yet, so the seed is not read

    def _close(self) -> tuple[int, str]:
        """`sprint close` with every chain step stubbed green except the extract."""
        mod = _live("sprint")
        out = io.StringIO()
        with contextlib.ExitStack() as stack:
            stack.enter_context(unittest.mock.patch.object(mod, "_report_holds",
                                                           lambda *a, **k: []))
            for name in mod._CLOSE_CHAIN:
                if name != "retro-extract":
                    stack.enter_context(unittest.mock.patch.object(
                        mod, "_close_" + name.replace("-", "_"),
                        lambda *a, _n=name, **k: (True, f"{_n} ok", "")))
            stack.enter_context(contextlib.redirect_stdout(out))
            stack.enter_context(contextlib.redirect_stderr(out))
            rc = mod.main(["close", "--retro", "RETRO0001", "--root", str(self.root)])
        return rc, out.getvalue()

    def test_a_manual_extract_then_the_close_counts_one_repeat(self) -> None:
        """MUTANT: default a manual extract's run to the retro id, or key a hit on its run -
        the runbook's step 5 then records the repeat under RETRO0001 and the close records it
        again under the run."""
        _store(self.root, _row(1, ("build",)))
        _open_run(self.root)
        (self.root / "src").mkdir()
        (self.root / "src" / "widget.py").write_text("x = 1\n", encoding="utf-8")
        story = self.root / "sdlc-studio" / "stories" / "US0101-widget.md"
        story.parent.mkdir(parents=True)
        story.write_text("# US0101: widget\n\n> **Status:** Review\n> **Points:** 3\n"
                         "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n"
                         "### AC1: works\n- **Verify:** shell true\n", encoding="utf-8")
        _retro(self.root, "[LC-001] The mutant never landed again on US0101.")

        rc, out = _extract(self.root, None)                  # the runbook's manual step
        self.assertEqual(0, rc, out)
        self.assertEqual([{"run": RUN, "unit": "US0101", "source": "retro:RETRO0001"}],
                         _rows(self.root)[0]["hits"], "a manual extract named the wrong run")
        rc, out = self._close()
        self.assertEqual(0, rc, out)
        self.assertIn("retro-extract", out)
        self.assertEqual(1, len(_rows(self.root)[0]["hits"]), "the close counted it again")

    def test_the_same_retro_item_counts_once_whatever_the_run(self) -> None:
        """MUTANT: key a hit on (run, unit, source) - one retro item read under two spellings of
        the run then counts twice."""
        _store(self.root, _row(1, ("build",)))
        _retro(self.root, "[LC-001] again on US0101.")
        for run in (None, "RUN-X", "run-x ", "RUN-Y"):
            self.assertEqual(0, _extract(self.root, run)[0])
        self.assertEqual(1, len(_rows(self.root)[0]["hits"]))
        # A second retro naming the same repeat is a second item, and counts.
        _retro(self.root, "[LC-001] again on US0101.", rid="RETRO0002")
        self.assertEqual(0, _extract(self.root, "RUN-Y", "RETRO0002")[0])
        self.assertEqual(["retro:RETRO0001", "retro:RETRO0002"],
                         [h["source"] for h in _rows(self.root)[0]["hits"]])

    def test_a_new_item_extracted_twice_never_hits_its_own_class(self) -> None:
        """MUTANT: let a `new` item that matches a row always count, or tell the record from a
        repeat by its run - re-reading the recording retro under another run then counts the
        class's own record as its first repeat."""
        _retro(self.root, NEW_TRY)
        for run in (None, "RUN-A", None, "RUN-B"):
            rc, out = _extract(self.root, run)
            self.assertEqual(0, rc, out)
        rows = _rows(self.root)
        self.assertEqual(1, len(rows))
        self.assertEqual([], rows[0]["hits"], "the recording item counted as a repeat")
        self.assertEqual("RETRO0001", rows[0]["recorded_run"], "no run open: the retro id")


class MalformedTagTests(unittest.TestCase):
    """Review round 1: a tag that did not parse went silently to the prose log, so the repeat
    its author meant to count was lost."""

    BAD = ("[LC-01] again", "[LC 001] again", "(LC-001) again", "LC-001: again",
           "**[LC-001]** again", "[new scope drift] Review the diff. Run git log -S.",
           "[new scope drift | build] Review the diff. Run git log -S.")
    GOOD = ("[LC-001 ] again", "[ LC-001] again", "[lc-001] again", "[LC-001]again")
    # Ordinary prose a Try item may lead with: a link, a checkbox, a passing mention of a code,
    # or a sentence that opens on the word "new". None is a tag, and none may be refused as one.
    PROSE = ("[US0887](../stories/x.md) showed the plan printed no lessons. Seed them.",
             "[x] done: the digest is gone. Keep it gone.",
             "Make LC-001 a pre-commit check. Stop relying on the rule being read.",
             "New units open when lanes start. Measure the work.")

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.store = _store(self.root, _row(1, ("build",)))

    def test_a_tag_that_does_not_parse_is_refused(self) -> None:
        """MUTANT: drop the tag-like check, or the `\\s*` before `]` - a malformed tag goes to
        the prose log, or a spaced one is refused."""
        prose = lessons.default_project_file(self.root)
        before = self.store.read_text(encoding="utf-8")
        for item in self.BAD:
            with self.subTest(item=item):
                _retro(self.root, item)
                res = retro.validate(self.root, "RETRO0001")
                self.assertFalse(res["ok"])
                self.assertTrue(any("reads as a class tag" in e for e in res["errors"]),
                                res["errors"])
                rc, out = _extract(self.root, "RUN-A")
                self.assertNotEqual(0, rc, out)
                self.assertIn("lessons.py classes", out)
                self.assertFalse(prose.is_file(), "a malformed tag went to the prose log")
                self.assertEqual(before, self.store.read_text(encoding="utf-8"))
        # positive controls: every spelling that does parse counts, and prose still goes to
        # the prose log
        for n, item in enumerate(self.GOOD, 1):
            with self.subTest(item=item):
                _retro(self.root, item, rid=f"RETRO{n + 1:04d}")
                self.assertTrue(retro.validate(self.root, f"RETRO{n + 1:04d}")["ok"])
                self.assertEqual(0, _extract(self.root, "RUN-A", f"RETRO{n + 1:04d}")[0])
        self.assertEqual(len(self.GOOD), len(_rows(self.root)[0]["hits"]))
        _retro(self.root, "Open units when lanes start. Measure the work.", rid="RETRO0009")
        self.assertEqual(0, _extract(self.root, "RUN-A", "RETRO0009")[0])
        self.assertTrue(prose.is_file())

    def test_prose_that_is_not_a_tag_passes(self) -> None:
        """MUTANT: read any leading `[` or any `LC-<digit>` anywhere as a tag (the round 2 check)
        - a Try item opening on a markdown link or a checkbox, or naming a code in passing, is
        then refused, and the retro cannot close."""
        before = self.store.read_text(encoding="utf-8")
        for n, item in enumerate(self.PROSE, 10):
            with self.subTest(item=item):
                self.assertIsNone(retro.try_class(item))
                _retro(self.root, item, rid=f"RETRO{n:04d}")
                res = retro.validate(self.root, f"RETRO{n:04d}")
                self.assertFalse(any("reads as a class tag" in e for e in res["errors"]),
                                 res["errors"])
                rc, out = _extract(self.root, "RUN-A", f"RETRO{n:04d}")
                self.assertEqual(0, rc, out)
        self.assertEqual(before, self.store.read_text(encoding="utf-8"),
                         "prose was counted on the class store")

    def test_a_corrupt_store_is_a_named_refusal(self) -> None:
        """MUTANT: load the store only for a hit tag, or let its ValueError escape - a `new`
        tag over a corrupt store is then a traceback, and `validate` passes a store every
        brief reports as unreadable."""
        self.store.write_text("not json\n", encoding="utf-8")
        for item in (NEW_TRY, "[LC-001] again", "Open units when lanes start. Measure."):
            with self.subTest(item=item):
                _retro(self.root, item)
                res = retro.validate(self.root, "RETRO0001")
                self.assertFalse(res["ok"])
                self.assertTrue(any("lessons.jsonl line 1" in e for e in res["errors"]),
                                res["errors"])
                rc, out = _extract(self.root, "RUN-A")
                self.assertEqual(1, rc)
                self.assertIn("lessons.jsonl line 1", out)
                self.assertNotIn("Traceback", out)
        self.assertEqual("not json\n", self.store.read_text(encoding="utf-8"))

    def test_an_unreadable_run_state_is_a_named_refusal(self) -> None:
        state = self.root / "sdlc-studio" / ".local" / "run-state.json"
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text("{", encoding="utf-8")
        _retro(self.root, "[LC-001] again")
        rc, out = _extract(self.root, None)
        self.assertEqual(1, rc)
        self.assertIn("cannot tell which run", out)
        self.assertEqual([], _rows(self.root)[0]["hits"])


class ClassesListingTests(unittest.TestCase):
    def test_classes_lists_every_code_name_state_and_hits(self) -> None:
        """MUTANT: list only the active classes, or drop the hit count - the author cannot find
        a graduated code to cite, or which classes keep recurring."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _store(root)  # an empty project store: no seed, and no classes yet
            rc, out = _cli(lessons.main, ["classes", "--root", str(root)])
            self.assertEqual(0, rc)
            self.assertIn("no classes", out)
            _store(root, _row(1, ("build",), hits=2), _row(2, ("review",), state="retired"))
            rc, out = _cli(lessons.main, ["classes", "--root", str(root)])
            self.assertEqual(0, rc, out)
            self.assertRegex(out, r"LC-001\s+active\s+2 hit\(s\)\s+class 1")
            self.assertRegex(out, r"LC-002\s+retired\s+0 hit\(s\)\s+class 2")
            rc, out = _cli(lessons.main, ["classes", "--root", str(root), "--format", "json"])
            self.assertEqual([("LC-001", 2), ("LC-002", 0)],
                             [(r["id"], r["hits"]) for r in json.loads(out)])
            (root / STORE).write_text("not json\n", encoding="utf-8")
            rc, out = _cli(lessons.main, ["classes", "--root", str(root)])
            self.assertEqual(1, rc)
            self.assertIn("classes refused", out)


class SeedFallbackTests(unittest.TestCase):
    """D0261: a project with no store of its own reads the six generic classes bundled with the
    skill, so a greenfield plan and review carry lessons rather than none. Its first write
    creates its own store from that seed, and the seed itself is never written."""

    PLAN = ["LC-004", "LC-003", "LC-002"]    # the seed's plan classes, newest first on no hits
    REVIEW = ["LC-006", "LC-004", "LC-003", "LC-002", "LC-001"]

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.seed = lessons.SEED_FILE.read_bytes()

    def _greenfield_unit(self) -> Path:
        (self.root / "src").mkdir()
        (self.root / "src" / "a.py").write_text("", encoding="utf-8")
        bug = self.root / "sdlc-studio" / "bugs" / "BG0001-x.md"
        bug.parent.mkdir(parents=True)
        bug.write_text("# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n"
                       "> **Affects:** src/a.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
                       "### AC1: it holds\n\n- **Verify:** shell true\n", encoding="utf-8")
        seats = self.root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "qa.md").write_text("# QA seat\n", encoding="utf-8")
        worklist = self.root / "wl.txt"
        worklist.write_text("BG0001\n", encoding="utf-8")
        return worklist

    def test_the_seed_is_six_generic_classes_with_no_hits(self) -> None:
        rows = lessons.load_store(self.root)
        self.assertEqual([f"LC-{n:03d}" for n in range(1, 7)], [r["id"] for r in rows])
        for r in rows:
            self.assertLessEqual(FIELDS, set(r))
            self.assertEqual(([], "active"), (r["hits"], r["state"]), r["id"])

    def test_a_greenfield_plan_and_review_carry_the_seed(self) -> None:
        """MUTANT: no fallback - read only the project's store, as round 2 did. The greenfield
        plan then prints "none active" and the critic brief carries no lesson at all."""
        worklist = self._greenfield_unit()
        self.assertFalse((self.root / STORE).exists())
        rc, plan = _cli(sprint.main, ["plan", "--worklist", str(worklist), "--no-fetch",
                                      "--root", str(self.root)])
        self.assertEqual(0, rc, plan)
        review = critic.brief(self.root, "BG0001", "qa")
        seed = {r["id"]: r for r in lessons.load_store(self.root)}
        for name, text, want in (("plan", plan, self.PLAN), ("critic", review, self.REVIEW)):
            with self.subTest(output=name):
                self.assertNotIn("none active", text)
                self.assertEqual(want, re.findall(r"\bLC-\d{3}\b", text), text)
                for code in want:
                    self.assertIn(seed[code]["rule"], text)
                    self.assertIn(seed[code]["behaviour"], text)
                self.assertIn("bundled seed", text)
        self.assertFalse((self.root / STORE).exists(), "reading the seed wrote a store")
        # A project's own store, once it exists, replaces the seed: an empty one injects none.
        _store(self.root)
        rc, plan = _cli(sprint.main, ["plan", "--worklist", str(worklist), "--no-fetch",
                                      "--root", str(self.root)])
        self.assertIn("Lessons for plan: none active", plan)

    def test_a_write_creates_the_project_store_from_the_seed(self) -> None:
        """MUTANT: write the hit into the bundled seed, or save only the rows the write touched
        - the seed then carries one project's repeats into every other, or the new store drops
        the seed classes and the next code minted collides with a seed code."""
        _retro(self.root, "[LC-003] the lane brief reached no caller on US0007.",
               "[new: fixture unreachable] A fixture must reach the branch. Run the Given.")
        rc, out = _extract(self.root, "RUN-A")
        self.assertEqual(0, rc, out)
        rows = {r["id"]: r for r in _rows(self.root)}
        self.assertEqual([f"LC-{n:03d}" for n in range(1, 8)], sorted(rows))
        self.assertEqual([{"run": "RUN-A", "unit": "US0007", "source": "retro:RETRO0001"}],
                         rows["LC-003"]["hits"])
        self.assertEqual("fixture unreachable", rows["LC-007"]["class"])
        self.assertEqual(self.seed, lessons.SEED_FILE.read_bytes(), "the seed was written")
        rc, out = _cli(lessons.main, ["classes", "--root", str(self.root)])
        self.assertNotIn("bundled seed", out)

    def test_classes_lists_the_seed_on_a_greenfield_project(self) -> None:
        rc, out = _cli(lessons.main, ["classes", "--root", str(self.root)])
        self.assertEqual(0, rc, out)
        self.assertRegex(out, r"LC-001\s+active\s+0 hit\(s\)\s+mutant never applied")
        self.assertIn("bundled seed", out)


LEDGER_HEAD = ("# Critic Verdicts\n\n| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | "
               "Issues |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n")


def _hit(run: str, unit: str = "", source: str = "") -> dict:
    """A hit as the store holds it; a REJECT's hit by default, whose source names its run."""
    return {"run": run, "unit": unit, "source": source or f"critic:{run}"}


class GraduationTests(unittest.TestCase):
    """The close counts cited REJECTs, graduates a recurring class and retires a quiet one."""

    def setUp(self) -> None:
        self.root = self._workspace()

    def _workspace(self) -> Path:
        """A workspace a CR can be filed into, and a retro the close's extract step reads."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        d = root / "sdlc-studio" / "change-requests"
        d.mkdir(parents=True, exist_ok=True)
        (d / "_index.md").write_text(
            "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 0 |\n"
            "| **Total** | **0** |\n\n## All\n\n"
            "| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n", encoding="utf-8")
        _retro(root, "[new: retro class] A rule from the retro. What to do instead.")
        return root

    def _store(self, *rows: dict) -> None:
        path = self.root / STORE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    def _row(self, code: str, recorded: str, *hits: dict, state: str = "active") -> dict:
        return {"id": code, "class": f"class {code}", "rule": f"Rule of {code} holds.",
                "behaviour": f"Do {code} differently.", "inject": ["build"],
                "hits": list(hits), "state": state, "recorded_run": recorded}

    def _ledger(self, *rows: tuple[str, str, str]) -> None:
        path = self.root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(LEDGER_HEAD + "".join(
            f"| {u} | {v} | a seat | author | 2026-09-24 | - | full | {i} |\n"
            for u, v, i in rows), encoding="utf-8")

    def _state(self, run: str, batch=(), base=None) -> dict:
        state = {"schema": 1, "run_id": run, "outcome": "running",
                 "started_at": "2026-09-24T08:00:00Z", "batch": list(batch),
                 "review_base": dict(base or {}), "sprint_goal": "Lessons act on themselves."}
        path = self.root / "sdlc-studio" / ".local" / "run-state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state), encoding="utf-8")
        return state

    def _archive(self, *runs: str) -> None:
        d = self.root / "sdlc-studio" / ".local" / "run-archive"
        d.mkdir(parents=True, exist_ok=True)
        for n, run in enumerate(runs, 1):
            (d / f"{run}.json").write_text(json.dumps(
                {"run_id": run, "started_at": f"2026-09-{n:02d}T08:00:00Z",
                 "outcome": "goal-reached"}), encoding="utf-8")

    def _close(self, state: dict) -> str:
        """The close's retro-extract step, as `sprint close` runs it."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            ok, detail, remedy = sprint._close_retro_extract(self.root, "RETRO0001", state)
        self.assertTrue(ok, f"{detail}\n{remedy}\n{out.getvalue()}")
        return detail

    def _by_id(self) -> dict:
        return {r["id"]: r for r in _rows(self.root)}

    def _crs(self) -> list[Path]:
        return sorted((self.root / "sdlc-studio" / "change-requests").glob("CR*.md"))

    def test_a_citing_reject_counts_a_hit(self) -> None:
        """AC1. MUTANT: count every row that cites a code, or every row of the unit in the
        ledger - an APPROVE, or a REJECT an earlier run recorded, then counts as this run's
        repeat. MUTANT: drop the (source, unit) key - a re-run close counts it twice.
        MUTANT: read a batch unit the run fixed no review base for - US0003's REJECT, which
        this run never reviewed, then counts. MUTANT: drop the finding - the hit loses the
        evidence the graduation CR carries."""
        self._store(self._row("LC-001", "RUN-0"), self._row("LC-002", "RUN-0"))
        self._ledger(
            ("US0002", "REJECT", "[regression] an earlier run's repeat [LC-002]"),
            ("US0001", "REJECT", "[new] the mutant never landed [LC-001]; [new] also [LC-099]"),
            ("US0002", "APPROVE", "[pre-existing] mentions [LC-002] in passing"),
            ("US0003", "REJECT", "[new] not reviewed by this run [LC-002]"),
            ("US0001", "APPROVE", "-"))
        state = self._state("RUN-A", ("US0001", "US0002", "US0003"),
                            {"US0001": 0, "US0002": 1})
        detail = self._close(state)
        self.assertIn("1 hit(s) from cited REJECTs", detail)
        rows = self._by_id()
        cited = {**_hit("RUN-A", "US0001"), "finding": "the mutant never landed [LC-001]"}
        self.assertEqual([cited], rows["LC-001"]["hits"])
        self.assertEqual([], rows["LC-002"]["hits"], "an APPROVE, an earlier run's REJECT or "
                                                     "an unreviewed unit was counted as this "
                                                     "run's repeat")
        self.assertNotIn("LC-099", rows, "an unknown code minted a class")
        # A re-run close counts the same REJECT once, and a record no longer `running` still
        # reads only the units the run reviewed.
        state["outcome"] = "goal-reached"
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps(state), encoding="utf-8")
        self._close(state)
        self.assertEqual([cited], self._by_id()["LC-001"]["hits"])
        self.assertEqual([], self._by_id()["LC-002"]["hits"])
        # The review brief tells the reviewer how a finding cites a class.
        brief = "\n".join(lessons.render_phase(
            {"phase": "review", "lessons": [rows["LC-001"]], "active": 1}))
        self.assertIn("`[new] ... [LC-NNN]`", brief)

    def test_two_hits_propose_a_check(self) -> None:
        """AC2. MUTANT: count the hit taken in the run that recorded the class, or count two
        sources of one repeat twice - LC-002 or LC-003 then graduates on a single recurrence.
        MUTANT: leave the row `active` after filing - the next close files a second CR.
        MUTANT: count a unitless hit apart from the unit hit it shares a run with - LC-004, a
        retro Try item and a REJECT naming one repeat in RUN-1, then graduates.
        MUTANT: drop the finding text from the CR's hits, or stamp it as raised outside any
        batch - the groomer loses the evidence, and the report the run that raised it."""
        self._store(
            self._row("LC-001", "RUN-0", _hit("RUN-0", "US0009", "retro:RETRO0001"),
                      _hit("RUN-1", "US0003")),
            self._row("LC-002", "RUN-0", _hit("RUN-0", "US0009"), _hit("RUN-A", "US0004")),
            self._row("LC-003", "RUN-0", _hit("RUN-1", "US0005", "retro:RETRO0001"),
                      _hit("RUN-1", "US0005")),
            self._row("LC-004", "RUN-0", _hit("RUN-1", "", "retro:RETRO0001"),
                      _hit("RUN-1", "US0001")))
        self._ledger(("US0001", "REJECT", "[new] the class again [LC-001]"))
        state = self._state("RUN-A", ("US0001",), {"US0001": 0})
        detail = self._close(state)
        crs = self._crs()
        self.assertEqual(1, len(crs), [p.name for p in crs])
        cr_id = crs[0].name.split("-", 1)[0]
        rows = self._by_id()
        self.assertEqual("graduating", rows["LC-001"]["state"])
        self.assertEqual(cr_id, rows["LC-001"]["cr"])
        self.assertIn(cr_id, detail)
        body = crs[0].read_text(encoding="utf-8")
        for text in ("LC-001", "class LC-001", "Rule of LC-001 holds.", "RUN-1", "RUN-A",
                     "US0003", "US0001"):
            self.assertIn(text, body)
        self.assertIn("- RUN-A on US0001 (critic:RUN-A): the class again [LC-001]", body)
        self.assertIn("Which check to build, and where it lands, is named at grooming", body)
        self.assertRegex(body, r"> \*\*Raised-in-batch:\*\* RUN-A close, \d{4}-\d\d-\d\dT")
        self.assertIn("> **Status:** Proposed", body)
        self.assertEqual({"LC-002": "active", "LC-003": "active", "LC-004": "active"},
                         {k: rows[k]["state"] for k in ("LC-002", "LC-003", "LC-004")})
        # A later close, with the class hit again, files nothing more.
        self._ledger(("US0007", "REJECT", "[new] and again [LC-001]"))
        self._close(self._state("RUN-B", ("US0007",), {"US0007": 0}))
        self.assertEqual(crs, self._crs(), "a graduating class filed a second CR")
        self.assertEqual("graduating", self._by_id()["LC-001"]["state"])

    def test_two_units_rejected_in_one_run_are_two_repeats(self) -> None:
        """AC2. MUTANT: count one repeat per run however many units it names - LC-005, hit on
        US0001 and US0002 in RUN-1, then never graduates."""
        self._store(self._row("LC-005", "RUN-0", _hit("RUN-1", "US0001"),
                              _hit("RUN-1", "US0002")))
        self._close(self._state("RUN-A", ("US0001",), {"US0001": 0}))
        self.assertEqual("graduating", self._by_id()["LC-005"]["state"])
        self.assertEqual(1, len(self._crs()))

    def test_a_later_runs_cite_on_the_same_unit_counts(self) -> None:
        """A hit is one per (source, unit), so the REJECT's source names its run. MUTANT: record
        every REJECT's hit under the bare source `critic` - a later run citing the class on a
        unit an earlier run already cited it on is dropped as a duplicate, and LC-001, repeated
        in RUN-A and again in RUN-B, never graduates. A retro Try item and a REJECT naming the
        class on one unit in one run stay one repeat, and a re-run close adds nothing."""
        self._store(self._row("LC-001", "RUN-0"))
        _retro(self.root, "[LC-001] it came back on US0001")
        self._ledger(("US0001", "REJECT", "[new] the class again [LC-001]"))
        state = self._state("RUN-A", ("US0001",), {"US0001": 0})
        self._close(state)
        self._close(state)
        row = self._by_id()["LC-001"]
        self.assertEqual({("RUN-A", "retro:RETRO0001"), ("RUN-A", "critic:RUN-A")},
                         {(h["run"], h["source"]) for h in row["hits"]})
        self.assertEqual(2, len(row["hits"]), "a re-run close counted a hit twice")
        self.assertEqual(1, lessons.repeats_after_recording(row))
        self.assertEqual(("active", []), (row["state"], self._crs()))
        # RUN-B's review rejects the same unit again, citing the same class.
        self._ledger(("US0001", "REJECT", "[new] the class again [LC-001]"),
                     ("US0001", "REJECT", "[new] and again next run [LC-001]"))
        self._close(self._state("RUN-B", ("US0001",), {"US0001": 1}))
        row = self._by_id()["LC-001"]
        self.assertIn(("RUN-B", "US0001", "critic:RUN-B"),
                      [(h["run"], h["unit"], h["source"]) for h in row["hits"]],
                      "a later run's cite on the same unit was dropped")
        self.assertEqual(2, lessons.repeats_after_recording(row))
        self.assertEqual("graduating", row["state"])
        self.assertEqual(1, len(self._crs()))

    def test_a_quiet_lesson_retires(self) -> None:
        """AC3. MUTANT: judge quiet on the hits alone - LC-003, recorded two runs ago, retires
        before it has had five runs to recur. MUTANT: count the window from the oldest run, or
        make it four runs - LC-002, hit in RUN-3, the oldest of the last five, then retires
        too. MUTANT: make it six runs - LC-001, hit in RUN-2, then stays."""
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4", "RUN-5", "RUN-6")
        self._store(
            self._row("LC-001", "RUN-1", _hit("RUN-2", "US0001")),
            self._row("LC-002", "RUN-1", _hit("RUN-3", "US0002")),
            self._row("LC-003", "RUN-5"),
            self._row("LC-004", "RUN-1", state="graduating"))
        state = self._state("RUN-7")       # the last five runs are RUN-3 .. RUN-7
        detail = self._close(state)
        rows = self._by_id()
        self.assertEqual({"LC-001": "retired", "LC-002": "active", "LC-003": "active",
                          "LC-004": "graduating"},
                         {k: rows[k]["state"] for k in ("LC-001", "LC-002", "LC-003", "LC-004")})
        self.assertIn("retired LC-001", detail)
        self.assertNotIn("Rule of LC-001", "\n".join(
            lessons.render_phase(lessons.phase_digest(self.root, "build"))),
            "a retired class is still injected")
        # Five runs on record retire nothing: no run is older than the window yet.
        self._store(self._row("LC-001", "RUN-1"))
        for p in (self.root / "sdlc-studio" / ".local" / "run-archive").glob("*.json"):
            p.unlink()
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4")
        self._close(state)
        self.assertEqual("active", self._by_id()["LC-001"]["state"])

    def test_a_run_another_clone_holds_keeps_a_class_active(self) -> None:
        """The store is committed and the run archive is per clone. MUTANT: judge the window
        by membership of the last five runs - LC-007, recorded in a run only clone B holds,
        and LC-008, hit in clone B's latest run, retire on clone A at once, and retirement is
        not undone by anything but a new repeat."""
        store = [self._row("LC-007", "RUN-B1"),
                 self._row("LC-008", "RUN-1", _hit("RUN-B6", "US0001")),
                 self._row("LC-009", "RUN-1", _hit("RUN-2", "US0002"))]
        self._store(*store)
        self._archive("RUN-1", "RUN-2", "RUN-3", "RUN-4", "RUN-5", "RUN-6")
        detail = self._close(self._state("RUN-7"))
        self.assertEqual({"LC-007": "active", "LC-008": "active", "LC-009": "retired"},
                         {k: r["state"] for k, r in self._by_id().items() if k in
                          ("LC-007", "LC-008", "LC-009")}, detail)
        # Clone B knows RUN-B1 and judges LC-007 there; it has never seen RUN-1, so LC-008 and
        # LC-009 stay as the store it was given has them.
        self.root = self._workspace()
        self._store(*store)
        self._archive("RUN-B1", "RUN-B2", "RUN-B3", "RUN-B4", "RUN-B5", "RUN-B6")
        self._close(self._state("RUN-B7"))
        self.assertEqual({"LC-007": "retired", "LC-008": "active", "LC-009": "active"},
                         {k: r["state"] for k, r in self._by_id().items() if k in
                          ("LC-007", "LC-008", "LC-009")})

    def test_a_repeat_puts_a_retired_class_back(self) -> None:
        """A class retires because it stopped recurring; a repeat after that is evidence it has
        not. MUTANT: leave a hit on a retired class as a hit only - the class stays retired and
        its rule never reaches the work again, through a cited REJECT or a retro Try item."""
        # Clone A retired all three in its own run and committed the store; clone B's run
        # repeats them.
        self._store(*[{**self._row(code, "RUN-1"), "state": "retired", "retired_run": "RUN-7"}
                      for code in ("LC-001", "LC-002", "LC-003")])
        self._archive("RUN-B1", "RUN-B2")
        _retro(self.root, "[LC-002] it came back on US0009", "[new: class LC-003] Rule. Do.")
        self._ledger(("US0001", "REJECT", "[new] the retired class again [LC-001]"))
        detail = self._close(self._state("RUN-B3", ("US0001",), {"US0001": 0}))
        rows = self._by_id()
        self.assertEqual({"LC-001": "active", "LC-002": "active", "LC-003": "active"},
                         {k: rows[k]["state"] for k in ("LC-001", "LC-002", "LC-003")}, detail)
        self.assertNotIn("retired_run", rows["LC-001"])
        self.assertIn("back in force: LC-001", detail)
        self.assertIn("Rule of LC-002", "\n".join(
            lessons.render_phase(lessons.phase_digest(self.root, "build"))))

    def test_the_report_shows_recurrence(self) -> None:
        """AC4. MUTANT: count every hit as this run's, or list the retired class - the appendix
        then reports a repeat that did not happen here, or a class no longer in force."""
        self._store(
            self._row("LC-001", "RUN-0", _hit("RUN-0", "US0001"), _hit("RUN-A", "US0002"),
                      _hit("RUN-A", "US0003", "retro:RETRO0001")),
            self._row("LC-002", "RUN-0"),
            self._row("LC-003", "RUN-0", _hit("RUN-A", "US0004"), state="retired"),
            {**self._row("LC-004", "RUN-0", _hit("RUN-A", "US0005"), _hit("RUN-1", "US0006"),
                         state="graduating"), "cr": "CR0042"})
        # Ended, so the window the fingerprint covers does not end at the clock: an open run's
        # ends at `now`, and two builds either side of a second boundary sign different pages.
        state = self._state("RUN-A")
        (self.root / "sdlc-studio" / ".local" / "run-state.json").write_text(
            json.dumps({**state, "ended_at": "2026-09-24T09:00:00Z"}), encoding="utf-8")
        rep = sprint_report.build_report(self.root, "RETRO0001")
        md = sprint_report.render_markdown(rep)
        front, appendix = md.split("\n## Appendix\n", 1)
        self.assertNotIn("LC-00", front, "the lessons reached the front page")
        section = appendix.split("\n### Lessons\n", 1)[1]
        self.assertRegex(section, r"\| LC-001 \| class LC-001 \| active \| 2 \| 3 \|")
        self.assertRegex(section, r"\| LC-002 \| class LC-002 \| active \| 0 \| 0 \|")
        self.assertRegex(section,
                         r"\| LC-004 \| class LC-004 \| graduating \(CR0042\) \| 1 \| 2 \|")
        self.assertNotIn("LC-003", section, "a retired class is listed")
        html = sprint_report.render_html(rep)
        self.assertIn("<h3>Lessons</h3>", html)
        self.assertRegex(html, r"LC-001</th><td>class LC-001</td><td>active</td>"
                               r"<td class=\"num\">2</td><td class=\"num\">3</td>")
        # The store moves on after the page is signed; the signed figures must not.
        signed = rep["fingerprint"]
        self._store(self._row("LC-001", "RUN-0", *[_hit(f"RUN-{n}") for n in range(9)]))
        self.assertEqual(signed,
                         sprint_report.build_report(self.root, "RETRO0001")["fingerprint"])
        # A page filed before the section existed renders exactly as it did: the templates with
        # the lessons block cut out render it byte for byte the same.
        old = {**rep, "sections": [s for s in rep["sections"] if s["key"] != "lessons"]}
        tpl = sprint_report.template_path("core/sprint-report.md").read_text(encoding="utf-8")
        cut = re.sub(r"\n<!-- when: lessons_present -->.*\Z", "", tpl, flags=re.S)
        self.assertNotEqual(tpl, cut)
        self.assertEqual(sprint_report.render_markdown(old, cut),
                         sprint_report.render_markdown(old))
        tpl = sprint_report.template_path("reports/sprint-report.html").read_text(
            encoding="utf-8")
        cut = re.sub(r"<!-- when: lessons_present -->\n.*?<!-- end -->\n(?=</section>)", "",
                     tpl, flags=re.S)
        self.assertNotEqual(tpl, cut)
        self.assertEqual(sprint_report.render_html(old, cut), sprint_report.render_html(old))


if __name__ == "__main__":
    unittest.main()
