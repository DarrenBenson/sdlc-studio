"""The size vocabulary: modified Fibonacci story points, and nothing else (RFC0038 / CR0265).

A blind re-estimation of 21 delivered units - recovered as filed, `Effort` stripped, sized by
three independent estimators with no access to outcomes - scored r = +0.68 pooled and +0.78 on
units of 8 or below, where every computed metric failed (`max_cognitive` scored +0.03) and the
declared `Effort` S/M/L managed only +0.35. Points became the ONE size vocabulary; `Effort` was
retired.

The tests here are the CONTRACT of that vocabulary, driven through the public creation paths
(the finding filer's CLI and `artifact new` / `artifact batch`) and read back with the parser
the planner uses. Nothing here greps a source file for a string.

The load-bearing pair:

- A value OFF the scale is REFUSED, with a message that names the scale. A 7 is exactly the
  false precision the widening Fibonacci gaps exist to prevent: it is much harder to argue a
  unit is a 7 rather than an 8 than to choose between a 5 and an 8. The scale IS the estimate,
  so 7 is never silently rounded - it is refused, and the author makes the call.
- A value ON the scale is accepted, lands on disk, reads back through the parser, and satisfies
  the planner's own grooming gate. A size the creator writes that the planner cannot read is
  the two-ends-of-one-pipeline bug (LL0016) in a new place.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ff = _load("file_finding")
artifact = _load("artifact")
sprint = _load("sprint")
sdlc_md = ff.sdlc_md

# Off the scale, each for its own reason: a 7 and a 4 and a 6 are the false precision the
# widening gaps exist to prevent; a 0 is not a size; a 21 is the true Fibonacci number the
# MODIFIED scale replaces with 20; a decimal is precision nobody has; and the retired S/M/L
# vocabulary must not be quietly re-admitted through the new flag.
OFF_SCALE = ("7", "4", "6", "0", "9", "21", "100", "5.5", "-5", "S", "M", "L", "unknown", "")


def _seed_index(root: Path, type_: str) -> Path:
    """A minimal valid index for a type (summary + empty data table)."""
    dirs = {"bug": ("bugs", "| ID | Title | Status | Severity | Created | Updated |",
                    "| Open | 0 |\n| Fixed | 0 |"),
            "cr": ("change-requests",
                   "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
                   "| Proposed | 0 |\n| Complete | 0 |")}
    rel, header, summary = dirs[type_]
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    sep = "|" + " --- |" * (header.count("|") - 1)
    (d / "_index.md").write_text(
        f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{summary}\n"
        f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    return d / "_index.md"


def _artifacts(root: Path, type_: str) -> list[Path]:
    rel = {"bug": "bugs", "cr": "change-requests"}[type_]
    return [p for p in (root / "sdlc-studio" / rel).glob("*.md") if p.name != "_index.md"]


def _run(main, argv: list[str]) -> tuple[int, str]:
    """Drive a creator's CLI as the operator does. Returns (exit code, message) - a refusal
    raises ValueError out of `main`, exactly as it does under the shell wrapper (exit 1)."""
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = main(argv)
    except ValueError as exc:
        return 1, str(exc)
    return rc, err.getvalue()


def _file_bug(root: Path, *extra: str) -> tuple[int, str]:
    return _run(ff.main, ["file", "--type", "bug", "--title", "the parser drops a dash",
                          "--severity", "High", "--summary", "s", "--steps", "x", "--fix", "y",
                          "--affects", "src/thing.py", "--root", str(root), *extra])


def _file_cr(root: Path, *extra: str) -> tuple[int, str]:
    return _run(ff.main, ["file", "--type", "cr", "--title", "size the unit honestly",
                          "--priority", "High", "--ctype", "Improvement", "--summary", "s",
                          "--impact", "i", "--ac", "a criterion",
                          "--affects", "src/thing.py", "--root", str(root), *extra])


def _new(root: Path, type_: str, *extra: str) -> tuple[int, str]:
    argv = ["new", "--type", type_, "--title", "a unit of work", "--summary", "s",
            "--affects", "src/thing.py", "--root", str(root), *extra]
    if type_ == "bug":
        argv += ["--steps", "x", "--fix", "y", "--severity", "High"]
    else:
        argv += ["--impact", "i", "--ac", "a criterion"]
    return _run(artifact.main, argv)


class TheScaleIsTheEstimate(unittest.TestCase):
    """A value off the modified Fibonacci scale is REFUSED - never rounded, never coerced."""

    def test_an_off_scale_value_is_refused_and_nothing_is_written(self) -> None:
        for bad in OFF_SCALE:
            with self.subTest(points=bad), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                idx = _seed_index(root, "bug")
                before = idx.read_text(encoding="utf-8")
                rc, msg = _file_bug(root, "--points", bad)
                self.assertEqual(rc, 1, f"{bad!r} was accepted")
                self.assertEqual(_artifacts(root, "bug"), [])          # no artefact minted
                self.assertEqual(idx.read_text(encoding="utf-8"), before)  # no row, no id burnt

    def test_the_refusal_names_the_scale_and_the_offending_value(self) -> None:
        # A cryptic refusal teaches nothing: the author must be told what the scale IS and why
        # the value they chose is not on it, or they will simply try 6 next.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            _, msg = _file_bug(root, "--points", "7")
            self.assertIn("7", msg)
            for term in ("1, 2, 3, 5, 8, 13, 20", "Fibonacci"):
                self.assertIn(term, msg)

    def test_every_value_on_the_scale_is_accepted(self) -> None:
        for good in sdlc_md.POINTS_SCALE:
            with self.subTest(points=good), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _seed_index(root, "bug")
                rc, _ = _file_bug(root, "--points", str(good))
                self.assertEqual(rc, 0)
                body = _artifacts(root, "bug")[0].read_text(encoding="utf-8")
                self.assertEqual(sdlc_md.read_points(body), good)

    def test_the_scale_is_the_modified_fibonacci_and_nothing_else(self) -> None:
        self.assertEqual(sdlc_md.POINTS_SCALE, (1, 2, 3, 5, 8, 13, 20))


class PointsAreDemanded(unittest.TestCase):
    """An unsized unit is refused at BOTH creation paths - `sprint plan` refuses to plan one."""

    def test_a_bug_filed_with_no_points_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, msg = _file_bug(root)
            self.assertEqual(rc, 1)
            self.assertEqual(_artifacts(root, "bug"), [])
            self.assertIn("--points", msg)          # the refusal names the flag that supplies it

    def test_a_cr_filed_with_no_points_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            rc, _ = _file_cr(root)
            self.assertEqual(rc, 1)
            self.assertEqual(_artifacts(root, "cr"), [])

    def test_artifact_new_demands_points_too(self) -> None:
        # The two creation paths answer to ONE definition of a sized artefact - otherwise the
        # second is simply the way round the first.
        for type_ in ("bug", "cr"):
            with self.subTest(type=type_), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _seed_index(root, type_)
                rc, _ = _new(root, type_)
                self.assertEqual(rc, 1)
                self.assertEqual(_artifacts(root, type_), [])
                rc, _ = _new(root, type_, "--points", "7")   # ... and to ONE scale
                self.assertEqual(rc, 1)
                self.assertEqual(_artifacts(root, type_), [])
                rc, _ = _new(root, type_, "--points", "5")
                self.assertEqual(rc, 0)
                body = _artifacts(root, type_)[0].read_text(encoding="utf-8")
                self.assertEqual(sdlc_md.read_points(body), 5)

    def test_a_batch_carrying_one_off_scale_item_writes_nothing(self) -> None:
        # All-or-nothing: item 2's bad size must abort before item 1 is on disk.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            spec = root / "batch.json"
            spec.write_text(json.dumps([
                {"title": "first", "severity": "High", "summary": "s", "steps": "x", "fix": "y",
                 "affects": "src/a.py", "points": 3},
                {"title": "second", "severity": "High", "summary": "s", "steps": "x", "fix": "y",
                 "affects": "src/b.py", "points": 7},
            ]), encoding="utf-8")
            rc, msg = _run(artifact.main, ["batch", "--type", "bug", "--spec", str(spec),
                                           "--root", str(root)])
            self.assertEqual(rc, 1)
            self.assertEqual(_artifacts(root, "bug"), [])
            self.assertIn("7", msg)


class TheRoundTripFiledThenPlannable(unittest.TestCase):
    """A size the creator writes must be a size the PLANNER reads. One field, one parser."""

    def test_points_land_on_disk_and_read_back_through_the_planner(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, _ = _file_bug(root, "--points", "5")
            self.assertEqual(rc, 0)
            filed = _artifacts(root, "bug")[0]
            text = filed.read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.extract_field(text, "Points"), "5")
            bd = sprint.breakdown(root, [{"id": filed.stem.split("-")[0], "type": "bug",
                                          "path": str(filed)}], skip_personas=True)
            self.assertEqual(bd["ungroomed"], [],
                             "the planner refused an artefact the filer sized")
            self.assertTrue(bd["ok"])

    def test_a_cr_carries_its_tshirt_size_where_the_parser_finds_it(self) -> None:
        # A CR is a REQUEST, sized by a T-shirt Size (not story points), and that Size must be a
        # Size the PLANNER reads back as groomed - the two-ends-of-one-pipeline contract, in the
        # container vocabulary this time.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            rc, _ = _file_cr(root, "--size", "M")
            self.assertEqual(rc, 0)
            filed = _artifacts(root, "cr")[0]
            text = filed.read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.read_size(text), "M")
            self.assertIsNone(sdlc_md.read_points(text),
                              "a CR is a container - it carries a T-shirt Size, never points")
            bd = sprint.breakdown(root, [{"id": filed.stem.split("-")[0], "type": "cr",
                                          "path": str(filed)}], skip_personas=True)
            self.assertEqual(bd["ungroomed"], [])
            self.assertTrue(bd["ok"])


class EffortIsRetired(unittest.TestCase):
    """One size vocabulary. `Effort` S/M/L scored 0.35 against measured cost and is gone: a
    second vocabulary is a second answer to the same question, and the two drift."""

    def test_a_filed_artefact_carries_no_effort_field(self) -> None:
        # Sized by what it IS: a bug is a delivery unit (points), a CR is a request (T-shirt Size).
        for type_, filer, size_arg in (("bug", _file_bug, ("--points", "3")),
                                       ("cr", _file_cr, ("--size", "M"))):
            with self.subTest(type=type_), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _seed_index(root, type_)
                rc, _ = filer(root, *size_arg)
                self.assertEqual(rc, 0)
                text = _artifacts(root, type_)[0].read_text(encoding="utf-8")
                self.assertIsNone(sdlc_md.extract_field(text, "Effort"),
                                  "a retired vocabulary is still being written")

    def test_the_effort_flag_is_gone_from_both_creators(self) -> None:
        # Not a source grep: argparse REFUSES an unknown flag with exit 2, which is the
        # behaviour an operator (or an agent) reaching for the old flag actually meets.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            for main, argv in ((ff.main, ["file", "--type", "bug", "--title", "t",
                                          "--severity", "High", "--summary", "s", "--steps", "x",
                                          "--fix", "y", "--effort", "S", "--root", str(root)]),
                               (artifact.main, ["new", "--type", "bug", "--title", "t",
                                                "--effort", "S", "--root", str(root)])):
                with self.subTest(argv=argv[0]), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as cm:
                        main(argv)
                    self.assertEqual(cm.exception.code, 2)
            self.assertEqual(_artifacts(root, "bug"), [])


class AboveEightMustBeSplit(unittest.TestCase):
    """The scale works where the literature says it works and breaks where it says it breaks:
    the 13s in the blind re-estimation were systematically over-estimated, and all three
    estimators returned them with low confidence and the words 'should be split'. A 13 or a 20
    is a legal estimate - and a WARNING, because it is a triage failure, not a sizing one."""

    def test_a_unit_above_eight_is_accepted_with_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, err = _file_bug(root, "--points", "13")
            self.assertEqual(rc, 0)
            self.assertEqual(sdlc_md.read_points(
                _artifacts(root, "bug")[0].read_text(encoding="utf-8")), 13)
            self.assertIn("split", err.lower())

    def test_eight_and_under_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            _, err = _file_bug(root, "--points", "8")
            self.assertNotIn("split", err.lower())


if __name__ == "__main__":
    unittest.main()
