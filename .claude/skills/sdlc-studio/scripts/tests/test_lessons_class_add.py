"""`lessons.py class-add` records one failure class in the project's store outside a retro.

A retro records a class from a `[new: <class name>]` Try item when `retro.py extract` runs at the
close. A class found mid-run needs the same row without a retro: `class-add` appends one validated
active row to `sdlc-studio/lessons.jsonl` through the store's own functions, with the next `LC-`
code, the open run's id and the source, so `lessons classes` lists it and the lane brief's build
digest carries it. A duplicate class or a phase the digest does not know is refused and leaves the
store byte-identical.

Driven through `lessons.main`, the shipped entry point, in throwaway project roots.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lessons.py
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

SKILL = Path(__file__).resolve().parents[2]
STORE = Path("sdlc-studio") / "lessons.jsonl"
RUN = "RUN-CLASSADD01"
KNOWN = {"id": "LC-001", "class": "mutant never applied",
         "rule": "Assert a mutation applied before trusting its verdict.",
         "behaviour": "Count the replaced text first.", "inject": ["build"], "hits": [],
         "state": "active", "recorded_run": "RUN-OLD", "recorded_source": "retro:RETRO0001"}


def _cli(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        try:
            rc = lessons.main(argv)
        except SystemExit as exc:  # argparse refuses a flag value by exiting
            rc = exc.code
    return rc, out.getvalue()


def _store(root: Path, *rows: dict) -> Path:
    path = root / STORE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    return path


def _open_run(root: Path, run: str = RUN) -> None:
    p = root / "sdlc-studio" / ".local" / "run-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"schema": 1, "run_id": run, "started_at": "2026-11-15T00:00:00Z",
                             "ended_at": None, "outcome": "running", "batch": ["BG0001"]}),
                 encoding="utf-8")


def _add(root: Path, name: str, *phases: str, source: str = "finding:critic",
         extra: tuple[str, ...] = ()) -> tuple[int, str]:
    argv = ["class-add", "--root", str(root), "--lessons-dir", str(root / "registry"),
            "--class", name, "--rule", "A lane reads its brief once.",
            "--behaviour", "Read the brief, then the notes, each once.", "--source", source]
    for p in phases:
        argv += ["--phase", p]
    return _cli(argv + list(extra))


class ClassAddTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.path = _store(self.root, KNOWN)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _rows(self) -> list[dict]:
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()
                if line.strip()]

    def test_a_class_row_reaches_the_store_and_the_digest(self) -> None:
        """MUTANT: write to the `lessons/` registry, drop the code, the run or the source, or
        write a row `load_store` refuses - the digest then skips the class."""
        _open_run(self.root)
        rc, out = _add(self.root, "brief read twice", "build", "review",
                       source="finding:BG0001")
        self.assertEqual(rc, 0, out)
        rows = self._rows()
        self.assertEqual([r["id"] for r in rows], ["LC-001", "LC-002"])
        self.assertEqual(rows[0], KNOWN, "the existing row was rewritten")
        row = rows[1]
        self.assertEqual(row["class"], "brief read twice")
        self.assertEqual(row["state"], "active")
        self.assertEqual(row["inject"], ["build", "review"])
        self.assertEqual(row["hits"], [])
        self.assertEqual(row["recorded_run"], RUN)
        self.assertEqual(row["recorded_source"], "finding:BG0001")
        self.assertEqual(row["rule"], "A lane reads its brief once.")
        self.assertIn("LC-002", out)
        self.assertFalse((self.root / "registry").exists(), "a row reached the lessons/ registry")
        self.assertFalse((self.root / "sdlc-studio" / "retros").exists(),
                         "a row reached the project lessons log")
        # The store still loads as a store, the listing names the code, and the build digest
        # the lane brief renders carries the class.
        self.assertEqual([r["id"] for r in lessons.load_store(self.root)], ["LC-001", "LC-002"])
        rc, listing = _cli(["classes", "--root", str(self.root)])
        self.assertEqual(rc, 0, listing)
        self.assertRegex(listing, r"LC-002\s+active\s+0 hit\(s\)\s+brief read twice")
        digest = lessons.phase_digest(self.root, "build")
        self.assertEqual(digest["error"], "")
        self.assertIn("LC-002", [r["id"] for r in digest["lessons"]])
        self.assertIn("LC-002 brief read twice", "\n".join(lessons.render_phase(digest)))
        self.assertNotIn("LC-002", [r["id"] for r in lessons.phase_digest(self.root, "plan")
                                    ["lessons"]])

    def test_no_open_run_records_no_run(self) -> None:
        """MUTANT: stamp a run that is not open - the close then reads a repeat against it."""
        _open_run(self.root, "RUN-CLOSED")
        state = self.root / "sdlc-studio" / ".local" / "run-state.json"
        closed = json.loads(state.read_text(encoding="utf-8"))
        state.write_text(json.dumps({**closed, "outcome": "partial"}), encoding="utf-8")
        rc, out = _add(self.root, "brief read twice", "build", extra=("--format", "json"))
        self.assertEqual(rc, 0, out)
        self.assertEqual(json.loads(out)["id"], "LC-002")
        self.assertEqual(self._rows()[1]["recorded_run"], "")

    def test_a_duplicate_class_or_unknown_phase_is_refused(self) -> None:
        """MUTANT: append the duplicate, store the unknown phase, or write before refusing."""
        before = self.path.read_bytes()
        refusals = {
            "duplicate name": (["Mutant-Never  Applied", "build"], "LC-001"),
            "a class code as a name": (["lc-099", "build"], "class code"),
            "unknown phase": (["brief read twice", "build", "deploy"], "deploy"),
            "blank rule": (None, "rule"),
        }
        for case, (args, reason) in refusals.items():
            with self.subTest(case):
                if args is None:
                    rc, out = _cli(["class-add", "--root", str(self.root), "--class", "fresh",
                                    "--rule", "  ", "--behaviour", "b", "--phase", "build",
                                    "--source", "s"])
                else:
                    rc, out = _add(self.root, *args)
                self.assertNotEqual(rc, 0, out)
                self.assertIn(reason, out)
                self.assertEqual(self.path.read_bytes(), before, "the store changed on a refusal")
        # The positive control: a new class at a known phase is recorded.
        rc, out = _add(self.root, "brief read twice", "plan")
        self.assertEqual(rc, 0, out)
        self.assertEqual([r["id"] for r in self._rows()], ["LC-001", "LC-002"])


class ClassAddDocsTests(unittest.TestCase):
    PAGES = ("help/lessons.md", "reference-scripts.md")

    def _text(self, page: str) -> str:
        return " ".join((SKILL / page).read_text(encoding="utf-8").split())

    def test_both_pages_name_class_add_beside_retro_extract_and_the_store(self) -> None:
        for page in self.PAGES:
            with self.subTest(page):
                text = self._text(page)
                self.assertIn("class-add", text)
                self.assertIn("retro.py extract", text)
                self.assertIn("[new: <class name>]", text)
                self.assertIn("sdlc-studio/lessons.jsonl", text)
                self.assertRegex(text, r"lane brief reads the store, not the `lessons/` registry")

    def test_documented_flags_are_flags_the_parser_takes(self) -> None:
        parser = lessons.build_parser()
        sub = next(a for a in parser._actions if a.dest == "cmd").choices["class-add"]
        taken = set(sub._option_string_actions)
        for page in self.PAGES:
            with self.subTest(page):
                spans = re.findall(r"`[^`]*class-add[^`]*`", self._text(page))
                self.assertTrue(spans, f"{page} gives no class-add invocation")
                flags = {f for s in spans for f in re.findall(r"--[a-z][a-z-]*", s)}
                self.assertTrue({"--class", "--rule", "--behaviour", "--phase",
                                 "--source"} <= flags, f"{page} omits a required flag")
                self.assertEqual(flags - taken, set(), f"{page} documents flags class-add "
                                                       f"does not take")


if __name__ == "__main__":
    unittest.main()
