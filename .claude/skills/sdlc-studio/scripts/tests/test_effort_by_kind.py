"""US1336: `routing.effort` takes an effort per kind of unit (docs, bug and code), and the plan
and the lane brief carry each unit's resolved effort.

A unit's kind is route's classification (`route.work_kind`): a bug by its id, else code when an
Affects path ends in one of `route.CODE_EXTS`, else docs. A role a kind's entry leaves out takes
the role default, and the kind entries ship empty, so a project that sets none plans as before.
Driven through the shipped `sprint.py plan` and `sprint.py lane brief` entry points, in-process,
against a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

sprint = loader.load_script("sprint")
route = loader.load_script("route")
from lib import run_state  # noqa: E402

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:  # pragma: no cover - config is read through PyYAML
    HAVE_YAML = False

DOCS, CODE, BUG = "US0001", "US0002", "BG0001"
EFFORTS = ("inherit", "low", "medium", "high", "xhigh", "max")
#: AC1's configuration: role defaults, a docs entry and a bug entry, no code entry.
AC1 = ("routing:\n  effort:\n    builder: medium\n    reviewer: high\n"
       "    docs: {builder: low}\n    bug: {builder: high}\n")
ROLES_ONLY = "routing:\n  effort:\n    builder: medium\n    reviewer: high\n"
#: Every key `routing.effort` takes, which a refusal of any other key names.
KEYS = ("builder", "reviewer", "reviewer_below_builder", "docs", "bug", "code")


def _live(name: str):
    """The module the command resolves at call time; another test module may re-register it."""
    return sys.modules.get(name) or importlib.import_module(name)


def _unit(path: Path, uid: str, status: str, affects: str, extra: str = "") -> None:
    path.write_text(
        f"# {uid}: x\n\n> **Status:** {status}\n{extra}> **Affects:** {affects}\n"
        "> **Points:** 2\n\n## Acceptance Criteria\n\n### AC1: it holds\n\n"
        "- **Verify:** shell true\n",
        encoding="utf-8")


def _project(d: str, config: str = "") -> Path:
    """A Ready story naming only a `.md` file, a Ready story naming a `.py` file and an Open bug
    naming a `.py` file, with the project config given."""
    root = Path(d) / "repo"
    stories, bugs = root / "sdlc-studio" / "stories", root / "sdlc-studio" / "bugs"
    for p in (stories, bugs, root / "src", root / "docs"):
        p.mkdir(parents=True)
    (root / "src" / "app.py").write_text("", encoding="utf-8")
    (root / "docs" / "guide.md").write_text("# g\n", encoding="utf-8")
    _unit(stories / f"{DOCS}-docs.md", DOCS, "Ready", "docs/guide.md")
    _unit(stories / f"{CODE}-code.md", CODE, "Ready", "docs/guide.md, src/app.py")
    _unit(bugs / f"{BUG}-bug.md", BUG, "Open", "src/app.py", "> **Severity:** Medium\n")
    _config(root, config)
    return root


def _config(root: Path, config: str) -> None:
    (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")


def _decision(root: Path, did: str) -> None:
    (root / "sdlc-studio" / "decisions.md").write_text(
        f"# Decisions\n\n| ID | Decision |\n| --- | --- |\n| {did} | The reviewer may reason "
        "below its builder on docs. |\n", encoding="utf-8")


def _plan(root: Path, *extra: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(["plan", "--root", str(root), "--stories", "Ready",
                                   "--skip-personas", "--no-fetch", "--format", "json", *extra])
    return rc, out.getvalue(), err.getvalue()


def _efforts(stdout: str) -> dict:
    return {row["id"]: row.get("effort") for row in json.loads(stdout)["batch"]}


def _brief_line(root: Path, uid: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _live("sprint").main(["lane", "brief", "--units", uid, "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"lane brief refused ({rc}): {err.getvalue()}")
    lines = [line for line in out.getvalue().splitlines() if line.startswith("Effort:")]
    if len(lines) != 1:
        raise AssertionError(f"expected one effort line, got {lines}")
    return lines[0]


@unittest.skipUnless(HAVE_YAML, "the project config is read through PyYAML")
class EffortByKindTests(unittest.TestCase):

    def test_each_unit_is_stamped_with_its_kinds_effort(self) -> None:
        """AC1. MUTANTS: the kind entry not read; the kind not stamped; a bug classed by its
        Affects; a story naming one code file among docs classed docs; the role default not
        taken for a role the entry leaves out; the kind stamped when no entry is set."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, AC1)
            rc, out, err = _plan(root, "--bugs", "Open")
            self.assertEqual(rc, 0, err)
            self.assertEqual(_efforts(out), {
                DOCS: {"builder": "low", "reviewer": "high", "kind": "docs"},
                CODE: {"builder": "medium", "reviewer": "high", "kind": "code"},
                BUG: {"builder": "high", "reviewer": "high", "kind": "bug"}})

            # The kind entries removed, or present and empty as they ship: every unit takes the
            # role defaults and the row reads as it did before kinds existed.
            for config in (ROLES_ONLY, ROLES_ONLY + "    docs: {}\n    bug: {}\n    code: {}\n",
                           ROLES_ONLY + "    docs:\n    bug: {}\n"):
                with self.subTest(config=config):
                    _config(root, config)
                    rc, out, err = _plan(root, "--bugs", "Open")
                    self.assertEqual(rc, 0, err)
                    want = {"builder": "medium", "reviewer": "high"}
                    self.assertEqual(_efforts(out), {DOCS: want, CODE: want, BUG: want})

    def test_a_kind_value_is_read_as_a_role_value_is(self) -> None:
        """A kind's value is trimmed and lower-cased as a role default's is, and a code entry
        reaches the code story alone. MUTANTS: the kind value compared raw; the code entry
        applied to every kind."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, ROLES_ONLY + "    code: {reviewer: ' XHigh '}\n")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            self.assertEqual(_efforts(out), {
                DOCS: {"builder": "medium", "reviewer": "high", "kind": "docs"},
                CODE: {"builder": "medium", "reviewer": "xhigh", "kind": "code"}})

    def test_work_kind_composes_routes_classification(self) -> None:
        """`route.work_kind`: a bug by its id whatever it names, code by an Affects path in
        `CODE_EXTS`, else docs; the file is read when no text is given."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d)
            stories = root / "sdlc-studio" / "stories"
            bug = root / "sdlc-studio" / "bugs" / f"{BUG}-bug.md"
            _unit(bug, BUG, "Open", "docs/guide.md")
            self.assertEqual("bug", route.work_kind(root, bug))
            self.assertEqual("code", route.work_kind(root, stories / f"{CODE}-code.md"))
            self.assertEqual("docs", route.work_kind(root, stories / f"{DOCS}-docs.md"))
            self.assertEqual("code", route.work_kind(
                root, stories / f"{DOCS}-docs.md", "> **Affects:** tools/x.sh\n"))

    def test_an_unknown_kind_role_or_value_is_refused_by_name(self) -> None:
        """AC2. Any key `routing.effort` does not take is refused, a misspelt role default as
        well as a near-miss kind, scalar or mapping. MUTANTS: an unknown kind ignored; an
        unknown key refused only when its value is a mapping; an unknown role ignored; an
        unknown value passed through; a kind entry that is not a mapping accepted; each refusal
        silent on the key or on what it takes; a refused plan writing its plan file."""
        cases = (
            ("doc: {builder: low}", r"routing\.effort\.doc\b", ("docs", "bug", "code")),
            ("builder: medium\n    reviwer: high", r"routing\.effort\.reviwer\b", KEYS),
            ("tests: {builder: low}", r"routing\.effort\.tests\b", KEYS),
            ("docs: {author: low}", r"routing\.effort\.docs\.author\b", ("builder", "reviewer")),
            ("docs: {builder: fast}", r"routing\.effort\.docs\.builder\b", EFFORTS),
            ("docs: low", r"routing\.effort\.docs\b(?!\.)", ("builder", "reviewer")),
        )
        for entry, key, takes in cases:
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as d:
                root = _project(d, f"routing:\n  effort:\n    {entry}\n")
                rc, out, err = _plan(root, "--write")
                self.assertEqual(rc, 2, f"{entry} planned:\n{out}{err}")
                self.assertRegex(err, key)
                for word in takes:
                    self.assertRegex(err, rf"\b{word}\b")
                self.assertEqual(out.strip(), "", "a refused plan printed a batch")
                self.assertFalse((root / sprint.PLAN_REL).exists(),
                                 "a refused plan wrote its plan file")
        # The positive controls: a known kind plans, and so do the keys 6.4 documented.
        for config in ("docs: {builder: low}",
                       "builder: medium\n    reviewer: high\n    reviewer_below_builder: ''"):
            with self.subTest(config=config), tempfile.TemporaryDirectory() as d:
                root = _project(d, f"routing:\n  effort:\n    {config}\n")
                rc, out, err = _plan(root, "--write")
                self.assertEqual(rc, 0, err)
                self.assertTrue((root / sprint.PLAN_REL).exists(), "premise: the plan file moved")

    def test_a_reviewer_below_its_builder_within_a_kind_needs_a_decision(self) -> None:
        """AC3. MUTANTS: a kind's pair never ranked; the refusal silent on the kind or on an
        effort; a decision the ledger does not hold accepted; the accepted id not printed or
        stamped on a unit whose own pair is not below."""
        with tempfile.TemporaryDirectory() as d:
            config = "routing:\n  effort:\n    docs: {builder: high, reviewer: low}\n"
            root = _project(d, config)
            rc, out, err = _plan(root)
            self.assertEqual(rc, 2, f"a docs reviewer below its builder planned:\n{out}{err}")
            self.assertIn("routing.effort.docs: the reviewer's effort (low) is below its "
                          "builder's (high)", err)
            self.assertIn("Raise routing.effort.docs.reviewer", err)
            self.assertIn("routing.effort.reviewer_below_builder", err)
            self.assertEqual(out.strip(), "", "a refused plan printed a batch")

            _config(root, config + "    reviewer_below_builder: D0001\n")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 2, "a decision decisions.md does not record was accepted")
            self.assertIn("names D0001, which", err)
            self.assertIn("in routing.effort.docs is refused", err)

            _decision(root, "D0001")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            self.assertRegex(err, r"reviewer's low is below its builder's high for the docs "
                                  r"kind, accepted under D0001")
            self.assertEqual(_efforts(out), {
                DOCS: {"builder": "high", "reviewer": "low", "kind": "docs",
                       "reviewer_below_builder": "D0001"},
                CODE: {"builder": "inherit", "reviewer": "inherit", "kind": "code"}})

    def test_the_role_defaults_are_ranked_beside_the_kinds(self) -> None:
        """The role defaults' pair is ranked as before, and an empty kind entry adds no pair of
        its own. MUTANTS: the defaults' pair never ranked; their refusal named as a kind's; an
        empty entry ranked as its kind; the decision stamped on a row whose pair is not below."""
        with tempfile.TemporaryDirectory() as d:
            config = ("routing:\n  effort:\n    builder: high\n    reviewer: low\n"
                      "    docs: {}\n    bug: {}\n")
            root = _project(d, config)
            rc, out, err = _plan(root)
            self.assertEqual(rc, 2, f"the defaults' reviewer below its builder planned:\n{err}")
            self.assertIn("routing.effort: the reviewer's effort (low) is below its builder's "
                          "(high)", err)

            _decision(root, "D0001")
            _config(root, config + "    reviewer_below_builder: D0001\n")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            accepted = [line for line in err.splitlines() if "accepted under" in line]
            self.assertEqual(["effort: the reviewer's low is below its builder's high, accepted "
                              "under D0001"], accepted)
            below = {"builder": "high", "reviewer": "low", "reviewer_below_builder": "D0001"}
            self.assertEqual(_efforts(out), {DOCS: below, CODE: below})

            _config(root, f"{config}    reviewer_below_builder: D0001\n"
                          "    code: {reviewer: high}\n")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 0, err)
            self.assertEqual(_efforts(out), {
                DOCS: {**below, "kind": "docs"},
                CODE: {"builder": "high", "reviewer": "high", "kind": "code"}})

            # Both the defaults and a kind below, and no decision: the defaults are named first.
            _config(root, "routing:\n  effort:\n    builder: high\n    reviewer: low\n"
                          "    code: {builder: max, reviewer: high}\n")
            rc, out, err = _plan(root)
            self.assertEqual(rc, 2, err)
            self.assertIn("routing.effort: the reviewer's effort (low)", err)

    def test_a_kind_at_or_above_its_builder_needs_no_decision(self) -> None:
        """AC3's boundary: an equal reviewer, or one the role default fills with inherit, is
        never below. MUTANT: `<` turned `<=`; the role default not filled before ranking."""
        for entry in ("{builder: high, reviewer: high}", "{builder: high}"):
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as d:
                root = _project(d, f"routing:\n  effort:\n    docs: {entry}\n")
                rc, out, err = _plan(root)
                self.assertEqual(rc, 0, err)
                self.assertNotIn("accepted under", err)
                setting = _live("sprint").effort_setting(root)
                self.assertEqual((None, []), (setting["reviewer_below_builder"], setting["below"]))

    def test_the_lane_brief_names_the_units_own_effort(self) -> None:
        """AC4. MUTANTS: the brief reading the role defaults for every unit; the kind left out
        of the line; a kind's both-inherit pair read as `routing.effort is not set`."""
        with tempfile.TemporaryDirectory() as d:
            root = _project(d, AC1)
            run_state.open_run(root, batch=[DOCS, CODE], goal="g")
            line = _brief_line(root, DOCS)
            self.assertRegex(line, r"builder at low effort\b.*reviewer at high effort\b")
            self.assertIn("the docs kind", line)
            line = _brief_line(root, CODE)
            self.assertRegex(line, r"builder at medium effort\b.*reviewer at high effort\b")
            self.assertIn("the code kind", line)
            self.assertNotIn("not set", line)

            _config(root, "routing:\n  effort:\n    code: {builder: high}\n")
            line = _brief_line(root, DOCS)
            self.assertIn("at the session's own effort", line)
            self.assertIn("the docs kind", line)
            self.assertNotIn("not set", line)

            # The entries as they ship, empty: the line a project that sets nothing has always read.
            _config(root, "routing:\n  effort:\n    docs: {}\n    bug: {}\n    code: {}\n")
            self.assertEqual("Effort: dispatch the builder and its reviewer at the session's own "
                             "effort (routing.effort is not set).", _brief_line(root, DOCS))

            # A kind's value `sprint plan` refuses is never passed on to the spawn.
            _config(root, "routing:\n  effort:\n    docs: {builder: nope}\n")
            line = _brief_line(root, DOCS)
            self.assertIn("routing.effort is not valid", line)
            self.assertNotIn("nope", line)


if __name__ == "__main__":
    unittest.main()
