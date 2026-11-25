"""US1329 (EP0379): the PRD, TRD and TSD describe what 6.5 ships.

Each fact a row states is read from the code that makes it true wherever the code holds it: the
verbs and options from each script's `build_parser()`, the flag defaults from
`reference-config.md`, the persona review ledger from `persona_review.LEDGER_REL`, the drive log
and the land record from the paths `lib/drive.py` and `lib/lanes.py` write in a fixture, the edit
runner's verdicts from `mutation.EDIT_RESULTS`, and the red-run answers from `gate.red_run` run
on a fixture project. Whether `ci.wait_timeout_minutes` has a reader is judged by the status
BG1613's own file records, so a later fix does not turn this test red. Typed here are the units,
since no code enumerates which units built a feature, and the phrases each row must say.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_specs_v65.py
"""
# test-census-subject: sdlc-studio/prd.md
from __future__ import annotations

import argparse
import fnmatch
import inspect
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import critic  # noqa: E402
import file_finding  # noqa: E402
import gate  # noqa: E402
import gitutil  # noqa: E402 - git with the confined environment
import mutation  # noqa: E402
import persona_review  # noqa: E402
import reconcile  # noqa: E402

import test_lean_trd_refresh as trd_refresh  # noqa: E402 - the committed-records scanner
import test_lean_v61_review_residue as residue  # noqa: E402 - the `.local` writer pin
from lib import drive, lanes, sdlc_md  # noqa: E402
from test_lean_prd_refresh import location_problems, unknown_commands  # noqa: E402
from test_lean_specs_v64 import (  # noqa: E402 - the 6.4 test's readers of the same pages
    CONFIG_REF, SPECS, STORIES, _body, _flat, _read, _rows, _section, _spans, _unquote,
    config_defaults, handler, reaches, verbs, writer_problems)

#: Each 6.5 feature: the marks its inventory row must name (a location the skill or repo holds,
#: a command or a phrase) and the units that built it.
FEATURES = {
    "persona standard and persona review": (
        ("scripts/persona_review.py", "best-practices/persona.md", "persona_review.py check",
         "persona_review.py brief", "persona_review.py record", "persona_review.py owed",
         persona_review.LEDGER_REL.as_posix(), "personas.standard"),
        ("US1052", "US1053", "US1054", "US1055", "US1056", "US1057", "US1322")),
    "testable persona goals and per-seat goal review": (
        ("scripts/validate.py", "sprint.py goal-review brief --seat", "validate.py personas",
         "validate.py seats", "Applies-to:"), ("US1036", "US1039", "US1040", "US1046")),
    "sprint drive and multi-worktree landing": (
        ("scripts/lib/drive.py", "sprint.py drive", "sprint.py lane land", "--resume",
         "sprint.py lane brief --repair", "decision record"),
        ("US1192", "US1193", "US1195", "US1196", "US1197", "US1198")),
    "author's mutation runner and its replay": (
        ("scripts/mutation.py", "mutation.py run --edits <list.json> --scope <id>",
         "critic.py self-check record --mutants-from", "critic.py brief", "labelled the author's"),
        ("US1200", "US1201", "US1202")),
    "red CI run policy": (
        ("scripts/gate.py", "reference-test-validation.md#red-ci-run", "gate.py --red-run",
         "ci.rerun_limit", "`file_finding`"), ("US1236", "US1237", "US1238")),
    "delegated and waiting signatures": (
        ("scripts/status.py", "sprint.py plan --write", "sprint.py sign --delegated --decision",
         "awaits its signature", "ADR-013"), ("US1290", "US1291", "US1292", "US1293")),
    "duplicate refusal and the plan's test advisories": (
        ("scripts/file_finding.py", "file_finding.py file", "--distinct-from", "Distinct-from",
         "advisory"), ("US1324", "US1326")),
    "harness and enterprise pages": (
        ("docs/harnesses.md", "docs/enterprise.md", "harness-agnostic"),
        ("US1315", "US1316", "US1317", "US1318", "US1319", "US1320", "US1321")),
}
#: A Location mark: a path the skill or the repository root holds, with an optional anchor.
_LOCATION = re.compile(r"^(?:scripts/|templates/|reference-|help/|docs/|best-practices/)")
#: The options each feature's command takes, read from its parser: (script, verb, options).
OPTIONS = (("mutation", "run", ("--edits", "--scope", "--report")),
           ("gate", None, ("--red-run", "--failed", "--token")),
           ("file_finding", "file", ("--distinct-from",)),
           ("sprint", "sign", ("--delegated", "--decision")),
           ("sprint", "lane", ("--resume", "--repair")),
           ("sprint", "goal-review", ("--seat",)),
           ("sprint", "drive", ("--after",)))
#: The 6.5 keys the flags table must list at the defaults `reference-config.md` states.
FLAGS = ("personas.standard", "ci.wait_timeout_minutes", "ci.rerun_limit",
         "review.rendered_paths")
#: The bug that records `ci.wait_timeout_minutes` has no reader.
NO_READER_BUG = "BG1613"


def options(script: str, verb: str | None) -> set[str]:
    """The option strings `script`'s parser, or its `verb` subparser, accepts."""
    parser = verbs(script)[verb] if verb else __import__(script).build_parser()
    return set(parser._option_string_actions)


def bug_open(bug_id: str) -> bool:
    """Whether the bug's own file records a status that is not terminal."""
    path = next((REPO / "sdlc-studio" / "bugs").glob(f"{bug_id}-*.md"))
    status = (sdlc_md.extract_field(_read(path), "Status") or "").strip()
    return not sdlc_md.is_terminal_status("bug", status)


def _flake_project(root: Path) -> str:
    """A fixture project holding one open bug filed as flaky, naming one test; that test's id."""
    test = "tests/test_probe.py::ProbeTests::test_flaky"
    (root / "tests").mkdir()
    (root / "tests" / "test_probe.py").write_text("import unittest\n", encoding="utf-8")
    (root / "tests" / "test_other.py").write_text("import unittest\n", encoding="utf-8")
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    (bugs / "BG0001-probe-is-flaky.md").write_text(
        f"# BG0001: test_flaky is flaky\n\n> **Status:** Open\n\n## Summary\n\n`{test}` fails "
        f"one run in ten.\n", encoding="utf-8")
    return test


class SpecsV65Tests(unittest.TestCase):
    """US1329: what the three specs say 6.5 ships."""

    def test_the_prd_inventory_and_flags_name_65s_features(self) -> None:
        """AC1. Mutants: the PRD at HEAD, where no row names `persona_review.py`, `sprint.py
        drive`, `gate.py --red-run`, `mutation.py run --edits` or `--distinct-from`; any 6.5
        feature's row dropped, or not naming its location, its command or phrase or one of its
        units, or not Complete, or naming a Location that resolves to no file or anchor, or a
        `<script>.py <verb>` its script lacks; the risk class row not naming `reconcile.py
        detect`'s `risk-class` drift, `reconcile.py apply` or US1314; one of the four keys missing
        from the flags table or given another default than `reference-config.md` states; the
        `ci.wait_timeout_minutes` row saying it bounds the wait, or not saying no script reads
        it, while BG1613 is open."""
        prd = _body(_read(SPECS["prd"]))
        rows = _rows(_section(prd, "3. Feature Inventory"), "Feature")
        self.assertGreaterEqual(len(rows), 48, "premise: the Feature Inventory moved")
        self.assertLessEqual({"check", "brief", "record", "owed"}, set(verbs("persona_review")))
        self.assertLessEqual({"personas", "seats"}, set(verbs("validate")))
        self.assertIn("drive", verbs("sprint"))
        for script, verb, wanted in OPTIONS:
            with self.subTest(command=f"{script}.py {verb or ''}"):
                self.assertLessEqual(set(wanted), options(script, verb))
        for feature, (marks, units) in FEATURES.items():
            with self.subTest(feature=feature):
                for mark in (m for m in marks if _LOCATION.match(m)):
                    self.assertEqual([], location_problems(mark), f"premise: {mark} moved")
                for unit in units:
                    self.assertTrue(list(STORIES.glob(f"{unit}-*.md")), unit)
                hits = [r for r in rows if all(m in " | ".join(r) for m in marks)]
                self.assertEqual(1, len(hits), f"{feature}: {len(hits)} rows name {marks}")
                row = hits[0]
                self.assertEqual("Complete", row[2])
                self.assertEqual([], location_problems(row[4]))
                self.assertEqual([], unknown_commands(row[1]))
                self.assertEqual([], [u for u in units if not re.search(rf"\b{u}\b", row[5])])
        # The risk class row names reconcile's drift, read from the verbs that report and raise it.
        risk = [r for r in rows if r[0] == "Risk class and second seat"]
        self.assertEqual(1, len(risk))
        self.assertTrue(reaches("reconcile", handler("reconcile", "detect"), "risk_class_drift"))
        self.assertTrue(reaches("reconcile", handler("reconcile", "apply"), "apply_risk_class"))
        self.assertIn('"kind": "risk-class"', inspect.getsource(reconcile.risk_class_drift))
        for mark in ("`reconcile.py detect`", "`risk-class` drift", "`reconcile.py apply`"):
            self.assertIn(mark, risk[0][1])
        self.assertRegex(risk[0][5], r"\bUS1314\b")
        stated = config_defaults(_read(CONFIG_REF))
        self.assertEqual({"personas.standard": "block", "ci.rerun_limit": "1"},
                         {k: stated.get(k) for k in ("personas.standard", "ci.rerun_limit")},
                         "premise: the config reader misread a default")
        flags = {}
        for row in _rows(_section(prd, "Feature Flags"), "Key"):
            for key in _spans(row[0]):
                flags[key] = (_unquote(row[1]), _flat(row[2]))
        for key in FLAGS:
            with self.subTest(flag=key):
                self.assertIn(key, flags, f"the PRD's flags table does not list {key}")
                self.assertEqual(stated[key], flags[key][0])
        effect = flags["ci.wait_timeout_minutes"][1]
        if bug_open(NO_READER_BUG):
            readers = [p.name for p in SCRIPTS.rglob("*.py") if "tests" not in p.parts
                       and "wait_timeout_minutes" in _read(p)]
            self.assertEqual([], readers, f"premise: a script reads the key {NO_READER_BUG} "
                                          "says nothing reads")
            self.assertIn("timeout 30m gh run watch", _read(SKILL / "reference-code.md"))
            self.assertRegex(effect, rf"\bNo script reads it while {NO_READER_BUG} is open\b")
            self.assertNotRegex(effect, r"(?i)\bbound|\bgives? up\b")

    def test_the_trd_names_every_record_65_writes(self) -> None:
        """AC2. Mutants: the TRD at HEAD, which names none of `persona-reviews.md`,
        `.local/drive`, `land.json`, `mutation-edits` or `CI Red Runs`; `committed_trees()` at
        HEAD, which omits the author-mutants tree although git tracks files in it; the persona
        review ledger's row dropped, at another path than `persona_review.LEDGER_REL`, credited
        to a writer other than `persona_review.py record`, or held to a tracked file; a state row
        dropped, at another path than its writer's code writes, or naming another writer; the land
        record given a row of its own beside the landed directory's; the
        `## CI Red Runs` sentence dropped or crediting another writer than `gate.py --red-run`."""
        trd = _body(_read(SPECS["trd"]))
        section = _section(trd, "Committed evidence and records")
        table = _rows(section, "Record")
        listed = {p for r in table for p in _spans(r[1])}
        ledger = persona_review.LEDGER_REL.as_posix()
        hits = [r for r in table if ledger in _spans(r[1])]
        self.assertEqual(1, len(hits), f"{len(hits)} rows list {ledger}")
        self.assertEqual([], writer_problems(hits[0][2], (("persona_review", "record"),)))
        self.assertTrue(reaches("persona_review", handler("persona_review", "record"),
                                "LEDGER_REL"))
        self.assertIn(ledger, trd_refresh.pending_records())
        # The author mutant lists are swept, no longer held only as pending.
        mutants = critic.author_mutants_path("", "x").parent.as_posix()
        self.assertIn(mutants, trd_refresh.committed_trees())
        self.assertNotIn(trd_refresh.AUTHOR_MUTANTS, trd_refresh.pending_records())
        self.assertIn(f"`{mutants}/`", _flat(section.split("\n|", 1)[0]))
        tracked = trd_refresh._tracked(mutants)
        self.assertGreater(len(tracked), 0, "premise: git tracks no author mutant list")
        self.assertEqual([], trd_refresh.unlisted(tracked, listed))
        self.assertEqual([f"{mutants}/notes.txt"],
                         trd_refresh.unlisted([*tracked[:1], f"{mutants}/notes.txt"], listed))
        # Each state row's path, read from the code that writes it in a fixture.
        state = _rows(_section(trd, "JSON state files (under `.local/`)"), "File")
        with tempfile.TemporaryDirectory() as d:
            done = subprocess.CompletedProcess(["true"], 0, "", "")
            log = drive.keep(Path(d), "US0001", "build", done)
            self.assertTrue((Path(d) / log).is_file())
            record = lanes._record_file(Path(d), "agent-x").relative_to(d).as_posix()  # noqa: SLF001
        local = "sdlc-studio/.local/"
        rows = {
            "drive log": ("drive/<unit>/<step>.log", log,
                          (("lib/drive", None), ("sprint", "drive")), ()),
            "land record": ("lane/landed/<worktree>.land.json", record, (("lib/lanes", None),),
                            ("sprint.py lane land",)),
            "edits report": ("mutation-edits-<unit>.json",
                             f"{local}mutation-edits-US0001.json",
                             (("mutation", None),),
                             ("mutation.py run --edits",)),
        }
        self.assertIn(f"default {local}mutation-edits-<unit>.json",
                      " ".join(verbs("mutation")["run"]._option_string_actions["--report"]
                               .help.split()), "premise: the report's default moved")
        self.assertIn("land", next(a.choices for a in verbs("sprint")["lane"]._actions
                                   if a.choices and not a.option_strings))
        # The land record shares the row of the directory it is kept beside.
        landed = "/".join(lanes.LANDED.parts[2:])
        self.assertEqual(("sdlc-studio", ".local"), lanes.LANDED.parts[:2])
        self.assertEqual(1, len([r for r in state if any(s.startswith(landed + "/")
                                                         for s in _spans(r[0]))]),
                         f"more than one state row names a path under {landed}/")
        sources = residue._shipped_sources()  # noqa: SLF001
        spans = [s for r in state for s in _spans(r[0])]
        for name, (span, fixture, writers, named) in rows.items():
            with self.subTest(state=name):
                found = [r for r in state if span in _spans(r[0])]
                self.assertEqual(1, len(found), f"{len(found)} state rows name {span}")
                self.assertTrue(fnmatch.fnmatchcase(fixture, local + trd_refresh._glob(span)),
                                fixture)
                self.assertEqual([], writer_problems(found[0][1], writers))
                for cmd in named:
                    self.assertIn(cmd, _spans(found[0][1]))
                self.assertEqual([], residue._path_pin_failures(  # noqa: SLF001
                    [(span, found[0][1])], sources))
                self.assertEqual([span], [s for s in spans if fnmatch.fnmatchcase(
                    fixture, local + trd_refresh._glob(s))])
        # A flaky bug's red-run section, named with the writer that writes it in a fixture.
        data = _flat(_section(trd, "6. Data Architecture"))
        self.assertRegex(data, rf"`{re.escape(gate.RED_RUN_SECTION)}` section is written by "
                               r"`gate\.py --red-run`")
        with tempfile.TemporaryDirectory() as d:
            test = _flake_project(Path(d))
            gate.red_run(d, "77", [test], can_rerun=True)
            bug = _read(Path(d) / "sdlc-studio" / "bugs" / "BG0001-probe-is-flaky.md")
        self.assertIn(f"\n{gate.RED_RUN_SECTION}\n", bug)
        self.assertIn("CI run 77 red #1", bug)

    def test_the_tsd_names_the_authors_mutants_and_the_red_run_policy(self) -> None:
        """AC3. Mutants: the TSD at HEAD, which names neither `--edits` nor `--red-run`; the
        runner's paragraph not naming its command, the scratch copy, every verdict in
        `mutation.EDIT_RESULTS`, the not-applied answer for an edit outside the Affects, or the
        brief's replay labelled the author's; the red-run subsection not naming any of the three
        answers, the flaky title, `ci.rerun_limit`, `file_finding`, that no answer skips or
        deselects a test, or that it exits 0 only on `rerun`; and each of those against the
        code, run on a fixture."""
        tsd = _body(_read(SPECS["tsd"]))
        runner = _flat(_section(tsd, "Mutation Testing (assertion integrity)"))
        self.assertIn("`mutation.py run --edits <list.json> --scope <id>`", runner)
        self.assertIn("in that scratch copy of the tree, never the working tree", runner)
        results = mutation.EDIT_RESULTS
        self.assertEqual(4, len(results), "premise: the runner's verdicts changed")
        self.assertIn(f"one verdict, {', '.join(results[:-1])} or {results[-1]}", runner)
        self.assertRegex(runner, r"An edit outside the unit's Affects[^.]*is reported "
                                 r"not-applied and never counted killed")
        self.assertRegex(runner, r"`critic\.py brief` then replays the recorded list[^.]*"
                                 r"labelled the author's recorded mutants")
        self.assertIn("never counts as the reviewer's own mutation pass", runner)
        # Each against the code: the runner copies the tree, refuses an edit outside the Affects,
        # and the brief's section is the author's.
        self.assertTrue(reaches("mutation", handler("mutation", "run"), "_copy_work_tree"))
        self.assertTrue(reaches("mutation", handler("mutation", "run"), "run_edits"))
        why = mutation._why_not_applied({"file": "b.py", "old": "x", "new": "y"}, "b.py",  # noqa: SLF001
                                        "US0001", ["a.py"], {"b.py": b"x"})
        self.assertEqual("b.py is not in US0001's Affects", why)
        self.assertIsNone(mutation._why_not_applied(  # noqa: SLF001
            {"file": "a.py", "old": "x", "new": "y"}, "a.py", "US0001", ["a.py"], {"a.py": b"x"}))
        self.assertTrue(critic.AUTHOR_MUTANTS_HEADING.startswith("The author's recorded mutants"))
        self.assertIn("not the reviewer's mutation pass", critic.AUTHOR_MUTANTS_HEADING)
        policy = _flat(_section(_section(tsd, "Defect Management"), "A red CI run"))
        for mark in ("`gate.py --red-run <run> --failed <tests> --token",
                     "answers `rerun` only while every failing test is named by an open bug "
                     "whose title says flaky", "are fewer than `ci.rerun_limit`",
                     "It answers `stop` past the limit, or with a token that cannot rerun",
                     "Otherwise it answers `regression` and files a bug through `file_finding`",
                     "No answer skips or deselects a test", "exits 0 only on `rerun`"):
            self.assertIn(mark, policy)
        self.assertEqual(("can-rerun", "cannot-rerun"), gate.RED_RUN_TOKENS)

        def exit_code(root: str, run: str, failed: list[str], token: str) -> int:
            """`gate.py --red-run`'s exit status, through the command's own handler."""
            args = argparse.Namespace(root=root, red_run=run, failed=failed, token=token,
                                      format="json")
            with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                return gate.cmd_red_run(args)

        with tempfile.TemporaryDirectory() as d:
            test = _flake_project(Path(d))
            self.assertEqual(1, gate._rerun_limit(d), "premise: the default limit moved")  # noqa: SLF001
            first = gate.red_run(d, "5", [test], can_rerun=True)
            self.assertEqual("rerun", first["answer"])
            self.assertEqual("stop", gate.red_run(d, "5", [test], can_rerun=True)["answer"],
                             "the second red of a run past a limit of one")
            self.assertEqual("stop", gate.red_run(d, "6", [test], can_rerun=False)["answer"])
            self.assertEqual(0, exit_code(d, "7", [test], "can-rerun"))
            self.assertNotEqual(0, exit_code(d, "7", [test], "can-rerun"))
            self.assertNotEqual(0, exit_code(d, "8", [test], "cannot-rerun"))
            other = "tests/test_other.py::OtherTests::test_broken"
            with mock.patch.object(file_finding, "file_finding",
                                   return_value={"id": "BG0002"}) as filed:
                regressed = gate.red_run(d, "9", [test, other], can_rerun=True)
                self.assertNotEqual(0, exit_code(d, "10", [other], "can-rerun"))
            self.assertEqual("regression", regressed["answer"])
            self.assertEqual("BG0002", regressed["bug"])
            self.assertEqual([test, other], regressed["failed"], "no failing test is dropped")
            self.assertEqual(2, filed.call_count)


if __name__ == "__main__":
    unittest.main()
