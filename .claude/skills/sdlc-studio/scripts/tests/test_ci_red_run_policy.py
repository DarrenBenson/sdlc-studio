"""A red CI run on main is put through `gate.py --red-run`, which gives one of three answers.

Every failure named by an open bug filed as flaky: the run is recorded on that bug, and the
answer is to rerun the failed jobs once, while the run's reds, counted across every open bug's
record, are fewer than `ci.rerun_limit`; past the limit, or with a token that cannot rerun, it is
to stop and ask the operator. Any failure no filed flake names, a module that fails whole among
them, makes the run a regression: a bug is filed through the shipped filer and nothing is pushed
until main is green. No answer skips or deselects a test.

Driven through `gate.main` in throwaway projects.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/gate.py
# test-census-subject: .claude/skills/sdlc-studio/help/gate.md
# test-census-subject: .claude/skills/sdlc-studio/reference-test-validation.md
from __future__ import annotations

import contextlib
import importlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))

FLAKE = "tests/test_temp.py::TempTests::test_cleanup"
OTHER = "tests/test_core.py::CoreTests::test_sum"
#: A second filed flake, so one run's reds can land on two flaky bugs. It is named as unittest
#: names a test, with no `::` and no file behind it, so it is a test and not a whole module.
SECOND = "tests.test_io.IoTests.test_read"
#: A test whose path holds the word "flaky", so the regression filed for it does too.
IN_FLAKY_DIR = "tests/flaky/test_net.py::NetTests::test_get"
FLAKY_BUG = """# BG0001: Flaky test: test_cleanup fails when the temp folder is shared

> **Status:** Open
> **Severity:** Medium
> **Affects:** tests/test_temp.py
> **Points:** 1

## Summary

`{test}` fails on CI about one run in ten.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | t | Filed |
"""
#: Words an answer must never carry: the policy reruns a flake, it never hides one.
HIDING = re.compile(r"\bskip|deselect|xfail|--lf\b|-k\s", re.I)


def _live(name: str):
    return sys.modules.get(name) or importlib.import_module(name)


def _project(d: str, config: str | None = None, closed_flake: str | None = None,
             open_flake: str | None = None) -> Path:
    root = Path(d)
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    (bugs / "BG0001-flaky-test-cleanup.md").write_text(FLAKY_BUG.format(test=FLAKE),
                                                       encoding="utf-8")
    if closed_flake:
        (bugs / "BG0002-flaky-test-sum.md").write_text(
            FLAKY_BUG.format(test=closed_flake).replace("BG0001", "BG0002")
            .replace("**Status:** Open", "**Status:** Fixed"), encoding="utf-8")
    if open_flake:
        (bugs / "BG0003-flaky-test-read.md").write_text(
            FLAKY_BUG.format(test=open_flake).replace("BG0001", "BG0003")
            .replace("tests/test_temp.py", "tests/test_io.py"), encoding="utf-8")
    (root / "tests").mkdir()
    (root / "tests" / "flaky").mkdir()
    for name in ("test_temp.py", "test_core.py", "flaky/test_net.py"):
        (root / "tests" / name).write_text("def test_x():\n    pass\n", encoding="utf-8")
    if config is not None:
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")
    return root


def _red(root: Path, run: str, *failed: str, token: str = "can-rerun") -> tuple[int, dict]:
    out, err = io.StringIO(), io.StringIO()
    argv = ["--red-run", run, "--failed", *failed, "--token", token, "--root", str(root),
            "--format", "json"]
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("gate").main(argv)
    try:
        return rc, json.loads(out.getvalue())
    except ValueError:
        raise AssertionError(out.getvalue() + err.getvalue()) from None


def _records(root: Path, bug: str, run: str) -> list[str]:
    """The lines of `bug`'s CI red-run record that name `run`."""
    path = next((root / "sdlc-studio" / "bugs").glob(f"{bug}-*.md"))
    text = path.read_text(encoding="utf-8")
    if "## CI Red Runs" not in text:
        return []
    section = text.split("## CI Red Runs", 1)[1].split("\n## ", 1)[0]
    return [ln for ln in section.splitlines() if re.search(rf"\brun {run}\b", ln)]


def _bugs(root: Path) -> list[Path]:
    return sorted((root / "sdlc-studio" / "bugs").glob("BG*.md"))


class CiRedRunPolicyTests(unittest.TestCase):

    def test_a_filed_flake_is_recorded_on_its_bug_and_rerun_once(self) -> None:
        """AC1. MUTANTS: the record skipped (rerun with nothing on the bug); the limit check
        `>=` made `>` (a second rerun); a record count that ignores the run id (another run's
        red spent this run's rerun); an answer that skips or deselects the test; the run's reds
        counted on only the bugs the current red names (a second rerun when the reds land on two
        flakes); the largest record of one bug taken for the run's count (a third rerun when the
        reds alternate under a limit of two); a red recorded on two bugs counted twice (a stop
        one rerun early)."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            rc, first = _red(root, "9001", FLAKE)
            self.assertEqual(0, rc, first)
            self.assertEqual(("rerun", "BG0001", "9001", 1),
                             (first["answer"], first["bug"], first["run"], first["limit"]))
            self.assertIn("gh run rerun 9001 --failed", first["reason"])
            records = _records(root, "BG0001", "9001")
            self.assertEqual(1, len(records), records)
            self.assertIn(FLAKE, records[0])
            rc, second = _red(root, "9001", FLAKE)
            self.assertNotEqual(0, rc)
            self.assertEqual("stop", second["answer"], second)
            self.assertIn("limit", second["reason"])
            self.assertEqual(2, len(_records(root, "BG0001", "9001")))
            rc, other = _red(root, "9002", FLAKE)
            self.assertEqual("rerun", other["answer"], "each run has its own rerun")
            for answer in (first, second, other):
                self.assertIsNone(HIDING.search(json.dumps(answer)), answer)
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, open_flake=SECOND)
            self.assertEqual("rerun", _red(root, "7000", FLAKE)[1]["answer"])
            rc, moved = _red(root, "7000", SECOND)
            self.assertNotEqual(0, rc, "the run's second red, on another flake, is past the limit")
            self.assertEqual(("stop", "BG0003"), (moved["answer"], moved["bug"]), moved)
            self.assertIn("limit", moved["reason"])
            self.assertEqual(1, len(_records(root, "BG0003", "7000")))
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, config="ci:\n  rerun_limit: 2\n", open_flake=SECOND)
            answers = [_red(root, "7001", test)[1]["answer"] for test in (FLAKE, SECOND, FLAKE)]
            self.assertEqual(["rerun", "rerun", "stop"], answers, "the reds alternate flakes")
            answers = [_red(root, "7002", *tests)[1]["answer"]
                       for tests in ((FLAKE, SECOND), (FLAKE,), (SECOND,))]
            self.assertEqual(["rerun", "rerun", "stop"], answers, "a red on two flakes is one red")

    def test_a_token_that_cannot_rerun_stops_and_asks_the_operator(self) -> None:
        """AC2. MUTANTS: the record skipped when the token cannot rerun; the answer `rerun`
        regardless of the token; a stop that names no operator, no run or no bug."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            rc, answer = _red(root, "9001", FLAKE, token="cannot-rerun")
            self.assertNotEqual(0, rc)
            self.assertEqual("stop", answer["answer"], answer)
            self.assertEqual(1, len(_records(root, "BG0001", "9001")))
            for words in ("ask the operator to rerun", "9001", "BG0001"):
                self.assertIn(words, answer["reason"])

    def test_a_red_run_matching_no_filed_flake_is_a_regression(self) -> None:
        """AC3. MUTANTS: one known flake among the failures read as the whole run being a flake
        (`any` for `all`); a closed flaky bug counted as filed; the regression answered with no
        bug filed, or a bug that names neither the run nor the test; a rerun offered; the
        hold on pushes dropped; a second red of the same run filing a duplicate; a regression
        filed for a test under `flaky/` read as a filed flake by the next run; a test id matched
        as the start of a filed flake's longer id; a failing id naming only a module, as pytest
        prints for one that will not collect, read as the flake whose bug's Affects lists it."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, closed_flake=OTHER)
            before = _bugs(root)
            rc, alone = _red(root, "9101", OTHER)
            self.assertNotEqual(0, rc)
            self.assertEqual("regression", alone["answer"], alone)
            filed = [p for p in _bugs(root) if p not in before]
            self.assertEqual(1, len(filed), filed)
            self.assertTrue(filed[0].name.startswith(alone["bug"]), (filed, alone))
            text = filed[0].read_text(encoding="utf-8")
            for words in ("9101", OTHER, "sdlc-studio file"):
                self.assertIn(words, text)
            rc, mixed = _red(root, "9102", FLAKE, OTHER)
            self.assertEqual("regression", mixed["answer"], mixed)
            mixed_bug = next(p for p in _bugs(root) if p.name.startswith(mixed["bug"]))
            self.assertIn("9102", mixed_bug.read_text(encoding="utf-8"))
            self.assertEqual([], _records(root, "BG0001", "9102"), "no flake rerun is spent")
            for answer in (alone, mixed):
                self.assertIn("do not push again until main is green", answer["reason"])
                self.assertNotIn("gh run rerun", answer["reason"])
            _rc, again = _red(root, "9101", OTHER)
            self.assertEqual(alone["bug"], again["bug"], "a second red of the run files nothing")
            self.assertEqual(len(before) + 2, len(_bugs(root)))
            self.assertEqual("regression", _red(root, "9103", IN_FLAKY_DIR)[1]["answer"])
            self.assertEqual("regression", _red(root, "9104", IN_FLAKY_DIR)[1]["answer"])
            prefix = FLAKE[:-2]  # `test_clean`, which the filed flake's `test_cleanup` starts with
            self.assertEqual("regression", _red(root, "9105", prefix)[1]["answer"])
            module = FLAKE.split("::", 1)[0]  # BG0001's Affects, and a module that will not collect
            rc, broken = _red(root, "9106", module)
            self.assertNotEqual(0, rc)
            self.assertEqual("regression", broken["answer"], broken)
            self.assertEqual([], _records(root, "BG0001", "9106"), "no flake rerun is spent")

    def test_the_help_and_the_reference_state_the_red_run_policy(self) -> None:
        """AC4. MUTANTS: the help section or its command line cut; an answer dropped from the
        help; the reference keeping only prevention advice; its rule dropping the record, the
        configured limit or the never-skip clause."""
        help_text = (SKILL / "help" / "gate.md").read_text(encoding="utf-8")
        section = help_text[help_text.index("## `--red-run`"):]
        section = re.sub(r"\s+", " ", section[:section.index("\n## ", 1)])
        self.assertRegex(section, r'gate\.py" --red-run <run> --failed <test>')
        for words in ("`rerun`", "rerun the failed jobs once", "`stop`",
                      "stop and ask the operator", "`regression`"):
            self.assertIn(words, section)
        ref = (SKILL / "reference-test-validation.md").read_text(encoding="utf-8")
        flaky = ref[ref.index("\n## Flakiness Prevention {#flakiness-prevention}"):]
        flaky = re.sub(r"\s+", " ", flaky[:flaky.index("\n## ", 1)])
        for words in ("`gate.py --red-run`", "recorded on its bug", "`ci.rerun_limit`",
                      "never skipped"):
            self.assertIn(words, flaky)

    def test_a_configured_rerun_limit_of_zero_stops_at_the_first_red_run(self) -> None:
        """AC5. MUTANTS: the limit read as the default of one despite the override; a reason
        that names neither the limit's value nor its key."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, config="ci:\n  rerun_limit: 0\n")
            rc, answer = _red(root, "9001", FLAKE)
            self.assertNotEqual(0, rc)
            self.assertEqual(("stop", 0), (answer["answer"], answer["limit"]), answer)
            self.assertIn("`ci.rerun_limit` is 0", answer["reason"])
            self.assertIn("ask the operator", answer["reason"])
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, config="ci:\n  rerun_limit: 2\n")
            self.assertEqual("rerun", _red(root, "9001", FLAKE)[1]["answer"])
            self.assertEqual("rerun", _red(root, "9001", FLAKE)[1]["answer"])
            self.assertEqual("stop", _red(root, "9001", FLAKE)[1]["answer"])


if __name__ == "__main__":
    unittest.main()
