"""US1329 and US1343 (EP0379): the PRD, TRD and TSD describe what 6.5 ships.

Each fact a row states is read from the code that makes it true wherever the code holds it: the
verbs and options from each script's `build_parser()`, the flag defaults from
`reference-config.md`, the persona review ledger from `persona_review.LEDGER_REL`, the drive log
and the land record from the paths `lib/drive.py` and `lib/lanes.py` write in a fixture, the edit
runner's verdicts from `mutation.EDIT_RESULTS`, and the red-run answers from `gate.red_run` run
on a fixture project. Whether `ci.wait_timeout_minutes` has a reader is judged by the status
BG1613's own file records, so a later fix does not turn this test red. Typed here are the units,
since no code enumerates which units built a feature, and the phrases each row must say.
The widened release's facts (US1343) are read the same way: the spend appetite's exit code,
warnings and options from `loop_guard` and `sprint`, the cache measures from `retro`,
`cost_anatomy` and `sprint_report`, the release record from a fixture cut, the rate's window
and settling period from `escape`, and the solution review ledger from `critic`.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_specs_v65.py
"""
# test-census-subject: sdlc-studio/prd.md
from __future__ import annotations

import argparse
import ast
import fnmatch
import importlib.util
import inspect
import io
import json
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
import deploy  # noqa: E402
import escape  # noqa: E402
import file_finding  # noqa: E402
import gate  # noqa: E402
import gitutil  # noqa: E402 - git with the confined environment
import loop_guard  # noqa: E402
import mutation  # noqa: E402
import persona_review  # noqa: E402
import reconcile  # noqa: E402
import release_cut  # noqa: E402
import retro  # noqa: E402
import sprint  # noqa: E402
import sprint_report  # noqa: E402

import test_lean_trd_refresh as trd_refresh  # noqa: E402 - the committed-records scanner
import test_lean_v61_review_residue as residue  # noqa: E402 - the `.local` writer pin
from lib import cost_anatomy, drive, lanes, run_state, sdlc_md  # noqa: E402
from test_lean_delegated_reports_disclosed import DISCLOSED  # noqa: E402 - the six disclosed
from test_lean_prd_refresh import location_problems, unknown_commands  # noqa: E402
from test_lean_specs_v64 import (  # noqa: E402 - the 6.4 test's readers of the same pages
    CONFIG_REF, SPECS, STORIES, _body, _flat, _read, _rows, _section, _spans, _tables,
    _unquote,
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
    "solution review": (
        ("scripts/critic.py", "reference-scripts-review.md", "critic.py approach brief",
         "critic.py approach record", f"sdlc-studio/reviews/{critic.SOLUTION_REVIEW_FILE}",
         "review.solution_review.min_points", "review.solution_review.risk_classes",
         "critic.py approach panel", "critic.py approach spend", "review.solution_review.panel",
         "sprint.py lane brief", "first-round approval and rounds per unit"),
        tuple(f"US{n}" for n in range(1344, 1354))),
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
         "review.rendered_paths", "review.solution_review.min_points",
         "review.solution_review.risk_classes",
         "review.solution_review.panel")
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


def _red_run_exit(root: str, run: str, failed: list[str], token: str) -> int:
    """`gate.py --red-run`'s exit status, through the command's own handler."""
    args = argparse.Namespace(root=root, red_run=run, failed=failed, token=token, format="json")
    with mock.patch("sys.stdout"), mock.patch("sys.stderr"):
        return gate.cmd_red_run(args)


def _page(name: str) -> Path:
    """A page the harness row names: under the repository root, or the skill's `SKILL.md`."""
    return next(p for p in (REPO / name, SKILL / name) if p.is_file())


def harness_claim_problems(cell: str) -> list[str]:
    """Why the harness row says of a page what the page does not: each page it lists as calling
    SDLC Studio a harness-agnostic Agent Skill must hold both phrases, and each phrase it quotes
    from `SKILL.md` must stand in that file's front matter."""
    flat = _flat(cell)
    # The clause's own sentence: a full stop ends it only where a space follows, not in a name.
    m = re.search(r"((?:[^.]|\.(?=\S))*) call SDLC Studio a harness-agnostic Agent Skill", flat)
    if not m:
        return ["the row says no page calls SDLC Studio a harness-agnostic Agent Skill"]
    out = []
    pages = re.findall(r"`([\w.-]+\.(?:md|txt|json))`", m.group(1))
    if not pages:
        out.append("the harness-agnostic clause names no page")
    for name in pages:
        text = _read(_page(name))
        if not (re.search(r"(?i)harness-agnostic", text) and "Agent Skill" in text):
            out.append(f"{name} does not call SDLC Studio a harness-agnostic Agent Skill")
    front = _read(SKILL / "SKILL.md").split("\n---", 1)[0]
    quoted = re.findall(r'`SKILL\.md`[^"]*"([^"]+)"', flat)
    if not quoted:
        out.append("the row quotes nothing SKILL.md says")
    out += [f"SKILL.md's front matter does not say {q!r}" for q in quoted if q not in front]
    return out


def subverbs(script: str, verb: str) -> dict[str, argparse.ArgumentParser]:
    """The sub-verbs `script`'s `verb` subparser takes, by name, read from its parser."""
    parser = verbs(script)[verb]
    return next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction)).choices


def inventory(prd: str, table: str = "3. Feature Inventory") -> list[list[str]]:
    """The Feature Inventory's rows, or those of one of its tables by heading."""
    return _rows(_section(prd, table), "Feature")


def flag_rows(prd: str) -> dict[str, tuple[str, str]]:
    """Each key the PRD's Feature Flags table lists: (its default, its Effect, flattened)."""
    return {key: (_unquote(row[1]), _flat(row[2]))
            for row in _rows(_section(prd, "Feature Flags"), "Key") for key in _spans(row[0])}


def row_problems(rows: list[list[str]], marks: tuple[str, ...], units: tuple[str, ...]) -> list[str]:
    """Why no one inventory row names every mark, is Complete, names a Location that resolves
    and no `<script>.py <verb>` its script lacks, and names each unit as a whole word."""
    hits = [r for r in rows if all(m in " | ".join(r) for m in marks)]
    if len(hits) != 1:
        return [f"{len(hits)} rows name {marks}"]
    row = hits[0]
    return ([] if row[2] == "Complete" else [f"{row[0]} is {row[2]}, not Complete"]) \
        + location_problems(row[4]) + unknown_commands(row[1]) \
        + [f"{row[0]} does not name {u}" for u in units if not re.search(rf"\b{u}\b", row[5])]


def one_row(rows: list[list[str]], marks: tuple[str, ...]) -> list[str]:
    """The one inventory row naming every mark."""
    return next(r for r in rows if all(m in " | ".join(r) for m in marks))


def disclosed_range() -> str:
    """The reports `sprint_report.py disclose` gave a disclosure line, as `RPTa to RPTb`, each
    checked to carry a delegated signature in its own JSON."""
    ids = sorted(DISCLOSED)
    for rid in ids:
        sig = sprint_report.read_report(REPO, rid).get("signature") or {}
        if not sig.get("delegated"):
            raise AssertionError(f"premise: {rid}'s signature records no delegation")
    return f"{ids[0]} to {ids[-1]}"


def cut_fixture(root: Path) -> dict:
    """The record `release_cut.py changelog-cut`'s cut writes in a fixture project at `root`,
    read back from the path it wrote, which must be `release_cut.RELEASES_REL`."""
    (root / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n\n### Added\n\n- probe\n",
                                       encoding="utf-8")
    release_cut.cut_changelog(root, "9.9.9")
    written = [p.relative_to(root).as_posix() for p in root.rglob("*.jsonl")]
    if written != [release_cut.RELEASES_REL]:
        raise AssertionError(f"premise: the cut wrote {written}")
    lines = (root / release_cut.RELEASES_REL).read_text(encoding="utf-8").splitlines()
    return json.loads(lines[0]) if len(lines) == 1 else {"lines": lines}


def pending_when_tracked(path: str) -> set[str]:
    """`pending_records()` with git tracking a file at `path` alone."""
    with mock.patch.object(trd_refresh, "_tracked",
                           side_effect=lambda *spec: [path] if spec == (path,) else []):
        return trd_refresh.pending_records()


#: The tests that hold the spend axis, each named on the TSD's Scalability row.
SPEND_TESTS = ("test_spend_at_the_appetite_stops_the_run_and_marks_nothing",
               "test_spend_warns_at_75_and_95_per_cent",
               "test_an_unreadable_meter_is_named_and_minutes_still_stop_the_run",
               "test_a_meter_with_no_usage_yet_is_unread_with_its_own_reason",
               "test_the_spend_appetite_resolves_flag_then_run_then_config_and_ships_unbounded")
_WORDS = {5: "five", 10: "ten"}



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
                if feature == "harness and enterprise pages":
                    self.assertEqual([], harness_claim_problems(row[1]))
                self.assertEqual([], unknown_commands(row[1]))
                self.assertEqual([], [u for u in units if not re.search(rf"\b{u}\b", row[5])])
        # Controls: a page holding only one of the two phrases, a quote SKILL.md lacks, and a row
        # quoting nothing from SKILL.md are each refused.
        claim = ('The first screen of `P.md` call SDLC Studio a harness-agnostic Agent Skill. The '
                 '`SKILL.md` compatibility line says it "Needs no particular harness"')
        for held in ("a harness-agnostic skill", "an Agent Skill"):
            with tempfile.TemporaryDirectory() as d, self.subTest(page=held):
                (Path(d) / "P.md").write_text(held, encoding="utf-8")
                with mock.patch(f"{__name__}._page", return_value=Path(d) / "P.md"):
                    self.assertEqual(["P.md does not call SDLC Studio a harness-agnostic Agent "
                                      "Skill"], harness_claim_problems(claim))
        self.assertEqual(["SKILL.md's front matter does not say 'Needs no harness at all 0f3c'"],
                         harness_claim_problems(claim.replace("particular harness",
                                                              "harness at all 0f3c")
                                                .replace("`P.md`", "`README.md`")))
        self.assertEqual(["the row quotes nothing SKILL.md says"], harness_claim_problems(
            claim.split(". The")[0].replace("`P.md`", "`README.md`")))
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
        with tempfile.TemporaryDirectory() as d:
            test = _flake_project(Path(d))
            self.assertEqual(1, gate._rerun_limit(d), "premise: the default limit moved")  # noqa: SLF001
            first = gate.red_run(d, "5", [test], can_rerun=True)
            self.assertEqual("rerun", first["answer"])
            self.assertEqual("stop", gate.red_run(d, "5", [test], can_rerun=True)["answer"],
                             "the second red of a run past a limit of one")
            self.assertEqual("stop", gate.red_run(d, "6", [test], can_rerun=False)["answer"])
            self.assertEqual(0, _red_run_exit(d, "7", [test], "can-rerun"))
            self.assertNotEqual(0, _red_run_exit(d, "7", [test], "can-rerun"))
            self.assertNotEqual(0, _red_run_exit(d, "8", [test], "cannot-rerun"))
            self._regression_files_through_the_patch(d, test)
        self.assertIn("a regression none of whose failing tests names a file in the tree is "
                      "refused, with the instruction to file it by hand", policy)
        # The edit runner copies the tree once for the whole list, never once per edit.
        self.assertIn("the tree is copied once into a scratch directory", runner)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "stories" / "US0001-probe.md").write_text(
                "# US0001: probe\n\n> **Status:** Ready\n> **Affects:** a.py\n", encoding="utf-8")
            (root / "a.py").write_text("x = 1\ny = 2\n", encoding="utf-8")
            edits = root / "edits.json"
            edits.write_text(json.dumps([
                {"file": "a.py", "old": "x = 1", "new": "x = 0", "test": "t.py::T::a"},
                {"file": "a.py", "old": "y = 2", "new": "y = 0", "test": "t.py::T::b"}]),
                encoding="utf-8")
            args = mutation.build_parser().parse_args(
                ["--root", d, "run", "--edits", str(edits), "--scope", "US0001", "--report",
                 str(root / "report.json")])
            with mock.patch.object(mutation, "_copy_work_tree") as copied, \
                    mock.patch("sys.stdout"), mock.patch("sys.stderr"):
                args.func(args)
            self.assertEqual(1, copied.call_count, "the tree is copied once for two edits")
            report = json.loads((root / "report.json").read_text(encoding="utf-8"))
            self.assertEqual(2, len(report["mutants"]), "premise: both edits were read")

    def _regression_files_through_the_patch(self, d: str, test: str) -> None:
        """`gate.py --red-run`'s regression path on the fixture at `d`, whose open flaky bug names
        `test`: a red on `test` and on a test no bug names files one bug through `file_finding`,
        a later run's red files a second, and a red naming no file in the tree is refused with
        nothing filed. `gate` imports `file_finding` from `sys.modules` when it files, so each
        patch is set by name on the copy `sys.modules` holds, never on the copy this file
        imported at load."""
        other = "tests/test_other.py::OtherTests::test_broken"
        with mock.patch("file_finding.file_finding",
                        return_value={"id": "BG0002"}) as filed:
            regressed = gate.red_run(d, "9", [test, other], can_rerun=True)
            self.assertNotEqual(0, _red_run_exit(d, "10", [other], "can-rerun"))
        self.assertEqual("regression", regressed["answer"])
        self.assertEqual("BG0002", regressed["bug"])
        self.assertEqual([test, other], regressed["failed"], "no failing test is dropped")
        self.assertEqual(2, filed.call_count)
        self.assertIn("CI run 10 is red on", filed.call_args.args[2],
                      "each red files a bug under its own run")
        # A regression whose failing tests name no file in the tree is refused, not filed.
        with mock.patch("file_finding.file_finding") as unfiled, \
                mock.patch("sys.stdout"), mock.patch("sys.stderr", new=io.StringIO()) as err:
            self.assertIs(unfiled, sys.modules["file_finding"].file_finding,
                          "premise: the patch is on the filer gate imports")
            code = gate.cmd_red_run(argparse.Namespace(
                root=d, red_run="44", failed=["nofile.py::X::t"], token="can-rerun",
                format="text"))
        self.assertEqual(2, code)
        self.assertFalse(unfiled.called)
        self.assertIn("red-run refused - regression: run 44", err.getvalue())
        self.assertIn("file it with file_finding.py", err.getvalue())

    def test_the_red_run_policy_holds_when_file_finding_was_reimported(self) -> None:
        """Mutant: the red-run test as it stood, patching `file_finding` on the module object
        this file imported at load. An earlier test in the same worker can put a fresh copy of
        `file_finding` in `sys.modules`; gate then files through that copy, unpatched, and the
        patched filer is called 0 times, not 2. Here a fresh copy stands in `sys.modules` while
        the red-run regression path runs, and the copy that was there is put back after."""
        before = sys.modules["file_finding"]
        spec = importlib.util.spec_from_file_location("file_finding", SCRIPTS / "file_finding.py")
        fresh = importlib.util.module_from_spec(spec)
        sys.modules["file_finding"] = fresh
        try:
            spec.loader.exec_module(fresh)
            self.assertIsNot(file_finding, sys.modules["file_finding"],
                             "premise: gate's import is not the copy this file imported")
            with tempfile.TemporaryDirectory() as d:
                self._regression_files_through_the_patch(d, _flake_project(Path(d)))
        finally:
            sys.modules["file_finding"] = before
        self.assertIs(before, sys.modules["file_finding"], "the fresh copy is taken out again")


    def test_the_prd_names_the_widened_cost_controls(self) -> None:
        """US1343 AC1. Mutants: the PRD at its base, where no row names `--appetite-spend`,
        `capacity.spend`, `cache_read_trend`, `cost_cache_writes` or a `docs` effort entry; any
        mark below dropped from its row, or a unit, or the row not Complete; "Over-budget WARNS,
        never gates" or "The plan stamps both on every unit" put back; the annex row at a
        version other than `sprint_report.EVIDENCE_SCHEMA_VERSION`."""
        prd = _body(_read(SPECS["prd"]))
        rows = inventory(prd)
        self.assertIn("--appetite-spend", options("sprint", "plan"))
        self.assertIn("--appetite-spend", options("loop_guard", "budget"))
        self.assertIn("resize", next(a.choices for a in verbs("sprint")["appetite"]._actions
                                     if a.dest == "action"))
        self.assertLessEqual({"--spend", "--decision"}, options("sprint", "appetite"))
        self.assertIn("validate", verbs("retro"))
        self.assertIn("--anatomy", options("sprint", "cost"))
        source = _read(SCRIPTS / "sprint_report.py")
        for key in ("cache_read_trend", "cost_cache_writes"):
            self.assertIn(f'_section("{key}"', source, f"premise: no {key} section")
        warn = sorted(loop_guard.SPEND_WARNINGS)
        lives = sorted(life for life, _key in cost_anatomy.CACHE_LIFETIMES.values())
        self.assertEqual([300, 3600], lives, "premise: the cache lifetimes moved")
        kinds = sprint.EFFORT_KINDS
        rows_wanted = {
            "sprint capacity": (("Sprint capacity", "`capacity.spend`",
                                 "counted in priced input-equivalent tokens",
                                 "feed the breaker that stops the run"), ("US1332", "US1333")),
            "run appetite": (("Run appetite / breaker", "`--appetite-spend`",
                              f"at a unit boundary with exit {loop_guard.BUDGET_EXIT}",
                              "counted in priced input-equivalent tokens",
                              f"warns at {warn[0]} and {warn[1]} per cent",
                              "A meter that cannot read leaves it unjudged at that boundary while "
                              "minutes and units still stop the run",
                              "`sprint.py appetite resize --spend` raises it only with "
                              "`--decision`"), ("US1332", "US1333")),
            "dispatch effort": (("Cost forecast and dispatch effort",
                                 f"`{kinds[0]}`, `{kinds[1]}` and `{kinds[2]}` entries set it for "
                                 "each kind of unit",
                                 "the plan stamps each unit's resolved effort, and its kind"),
                                ("US1336",)),
            "cost anatomy": (("Cost anatomy", "split into growth and re-writes after the "
                              f"{lives[0] // 60}-minute and {lives[1] // 3600}-hour cache "
                              "lifetimes expire", "a reviewer recorded with its seat is counted"),
                             ("US1337", "BG1764")),
            "cache measures": (("`cache_read_trend`", "`cost_cache_writes`",
                                f"over the last {_WORDS[sprint_report.CACHE_TREND_RUNS]} signed "
                                "runs", f"a `{retro.CACHE_READ_ISSUE}` known issue",
                                f"more than {_WORDS[retro.CACHE_READ_FALL_POINTS]} points",
                                "`retro.py validate` demands a bullet of the retro's "
                                f"`## {retro.COST_SECTION}` section naming that role"),
                               ("US1334", "US1335", "US1338")),
            "evidence annex": (("Evidence annex and committed run record",
                                f"at annex version {sprint_report.EVIDENCE_SCHEMA_VERSION}"),
                               ("US0992",)),
        }
        for name, (marks, units) in rows_wanted.items():
            with self.subTest(row=name):
                self.assertEqual([], row_problems(rows, marks, units))
        self.assertNotRegex(" | ".join(one_row(rows, ("Sprint capacity",))), r"(?i)never gates")
        self.assertNotIn("stamps on every unit", " | ".join(one_row(rows, ("dispatch effort",))))
        self.assertNotIn("The plan stamps both on every unit", prd)
        self.assertEqual({sprint_report.EVIDENCE_SCHEMA_VERSION},
                         set(re.findall(r"annex version (\d+\.\d+)", " ".join(map(str, rows)))))
        # Controls: a unit missing, a mark missing and a row not Complete are each refused.
        row = one_row(rows, ("Run appetite / breaker",))
        marks, units = rows_wanted["run appetite"]
        self.assertEqual(["Run appetite / breaker does not name US1333"], row_problems(
            [[*row[:5], row[5].replace("US1333", "US9999")]], marks, units))
        self.assertEqual([f"0 rows name {marks}"], row_problems(
            [[row[0], row[1].replace("exit 4", "exit 3"), *row[2:]]], marks, units))
        self.assertEqual(["Run appetite / breaker is Partial, not Complete"], row_problems(
            [[*row[:2], "Partial", *row[3:]]], marks, units))

    def test_the_prd_names_the_release_record_disclosure_and_ownership(self) -> None:
        """US1343 AC2. Mutants: the PRD at its base, with no "release record", "change failure",
        "person owns", "authority the person" or "settling"; a mark below dropped, a unit, or a
        Location given an anchor the page lacks; the release row naming `deploy.py metrics`'s
        ledger figure for the report's CI-run rate; the disclosed range not the reports'."""
        prd = _body(_read(SPECS["prd"]))
        rows = inventory(prd)
        self.assertIn("changelog-cut", verbs("release_cut"))
        self.assertIn("failure-rate", verbs("escape"))
        self.assertLessEqual({"disclose", "check"}, set(verbs("sprint_report")))
        self.assertIn("seats", verbs("retro"))
        self.assertTrue(reaches("retro", handler("retro", "seats"), "release_rate"))
        self.assertLessEqual({"dora", "release_cfr"}, set(sprint_report.APPENDIX))
        self.assertIn("PUSH-TRIGGERED runs alone", inspect.getdoc(sprint_report._dora_rows))  # noqa: SLF001
        with tempfile.TemporaryDirectory() as d:
            record = cut_fixture(Path(d))
            pending = escape.failure_rate(d)
            (Path(d) / release_cut.RELEASES_REL).unlink()
            empty = escape.failure_rate(d)
        self.assertEqual({"version", "date", "previous", "reports"}, set(record))
        self.assertEqual((["9.9.9"], None), (pending["pending"], pending["rate_percent"]))
        self.assertIsNone(empty["rate_percent"])
        self.assertTrue(empty["not_measured"])
        disclosed = disclosed_range()
        self.assertEqual("RPT0028 to RPT0034", disclosed, "premise: the disclosed reports moved")
        section = _flat(_section(_read(SKILL / "reference-workflow-personas.md"),
                                 "Seats for the requirements documents"))
        for phrase in ("The person owns every document the skill keeps",
                       "with authority the person delegates", "signs that document's review leg",
                       "proposes as a change request", "the person decides it", "asks the person"):
            self.assertIn(phrase, section, "premise: the seats section moved")
        rows_wanted = {
            "release record": (("Release record and change failure rate",
                                "`release_cut.py changelog-cut` writes one record per version to "
                                f"`{release_cut.RELEASES_REL}`, naming its date and the reports "
                                "signed since the previous release",
                                "`escape.py failure-rate` counts the releases with a linked "
                                "incident over the releases counted",
                                f"in a {escape.WINDOW_DAYS}-day window",
                                f"names a release inside the {escape.SETTLE_DAYS}-day settling "
                                "period as pending", "reads not measured, never 0%, with no "
                                "release or incident record", "in its `release_cfr` section",
                                "beside the change failure rate its `dora` section counts from "
                                "push-triggered CI runs", "`retro.py seats` shows it"),
                               ("US1233", "US1234", "US1235")),
            "disclosure": (("Delegated and waiting signatures", "`sprint_report.py disclose` puts "
                            "that disclosure line on a report already signed",
                            "which `sprint_report.py check` still reads VALID",
                            f"gave {disclosed} theirs"), ("US1294", "US1295")),
            "ownership": (("Document ownership", "The person owns the PRD and the PVD and every "
                           "other document the skill keeps", "The Product Owner or Product Manager "
                           "seat checks the work against its document under authority the person "
                           "delegates and signs its review leg", "it corrects a fact itself",
                           "proposes any change to a requirement, a priority or the scope as a "
                           "change request the person decides", "asks when unsure",
                           "as the personas reference's Seats for the requirements documents "
                           "section says", "| reference-workflow-personas.md |"),
                          ("US1339", "US1340")),
        }
        for name, (marks, units) in rows_wanted.items():
            with self.subTest(row=name):
                self.assertEqual([], row_problems(rows, marks, units))
        release = " | ".join(one_row(rows, ("Release record and change failure rate",)))
        self.assertNotIn("deploy.py metrics", release, "the report's CI-run rate is not the ledger's")
        # Control: the ownership row's Location given an anchor the page lacks is refused.
        owner = one_row(rows, ("Document ownership",))
        self.assertEqual("reference-workflow-personas.md", owner[4])
        moved = [[*owner[:4], owner[4] + "#seats-for-no-requirements-documents", owner[5]]]
        self.assertNotEqual([], row_problems(moved, *rows_wanted["ownership"][:1],
                                             rows_wanted["ownership"][1]))
        self.assertNotEqual([], location_problems(
            "reference-workflow-personas.md#seats-for-no-requirements-documents"))

    def test_the_prd_flags_list_the_widened_keys(self) -> None:
        """US1343 AC3. Mutants: the flags table at its base, listing none of the five keys; a key
        dropped or given another default than `reference-config.md` states; the spend Effect not
        saying a set value stops the run at a unit boundary, the unit or that 0 sets no ceiling;
        the kind Effect not saying it maps a role to an effort for that kind and ships empty; the
        capacity row saying tokens warn only with no word of spend stopping a run."""
        prd = _body(_read(SPECS["prd"]))
        flags = flag_rows(prd)
        stated = config_defaults(_read(CONFIG_REF))
        for key in ("capacity.spend", "appetite.spend"):
            with self.subTest(flag=key):
                self.assertEqual(stated[key], flags[key][0])
                for phrase in ("counted in priced input-equivalent tokens",
                               "a set value stops the run at a unit boundary",
                               "`capacity.spend` 0 sets no ceiling"):
                    self.assertIn(phrase, flags[key][1])
        reference = [r for t in _tables(_read(CONFIG_REF)) if "Default" in t[0] for r in t[1:]]
        for kind in sprint.EFFORT_KINDS:
            key = f"routing.effort.{kind}"
            with self.subTest(flag=key):
                cells = [r for r in reference if {"routing.effort", kind} <= set(_spans(r[0]))]
                self.assertEqual(1, len(cells), f"premise: the reference states {key} once")
                self.assertEqual(_unquote(cells[0][-1]), flags[key][0])
                for phrase in ("Each maps a role", "to an effort for units of that kind",
                               "Each ships empty"):
                    self.assertIn(phrase, flags[key][1])
        capacity = flags["capacity.tokens"][1]
        self.assertNotIn("minutes and units feed the run breaker", capacity)
        self.assertIn("`capacity.spend` feed the run breaker, so spend can stop a run", capacity)

    def test_the_trd_records_the_spend_breaker_and_the_release_record(self) -> None:
        """US1343 AC4. Mutants: the TRD at its base, with "A token budget that gates." in Won't
        Have, "tokens warn while minutes and units stop a run" in section 10, no ADR-015 and no
        release record row; ADR-015 numbered out of turn, citing D0503 or not D0637, or dropping
        an alternative, the unit, the late-never-early sentence, the unjudged meter sentence,
        the 0 default or the decision; the release row at another path than the fixture cut
        writes, naming another writer, or held pending while git tracks the file; the
        `run-state.json` row not naming a spend key `run_state.appetite_record` writes;
        ADR-013's closing bullet not naming `sprint_report.py disclose` or the range."""
        body = _body(_read(SPECS["trd"]))
        self.assertNotIn("A token budget that gates", _section(body, "Won't Have (This Version)"))
        self.assertNotIn("tokens warn while minutes and units stop a run",
                         _flat(_section(body, "10. Performance Requirements")))
        numbers = re.findall(r"^###\s+ADR-(\d+):", body, re.M)
        self.assertEqual(list(range(1, len(numbers) + 1)), [int(n) for n in numbers])
        self.assertEqual("015", numbers[-1])
        adr = _flat(trd_refresh._adr(body, "015"))  # noqa: SLF001
        self.assertRegex(adr, r"\*\*Status:\*\* Accepted \(D0637\b")
        self.assertTrue(trd_refresh._accepted("D0637"))  # noqa: SLF001
        self.assertEqual(["013"], [n for n in numbers if re.search(
            r"\bD0503\b", trd_refresh._adr(body, n))])  # noqa: SLF001
        stated = config_defaults(_read(CONFIG_REF))
        self.assertEqual(("0", "0"), (stated["capacity.spend"], stated["appetite.spend"]))
        unread = loop_guard.budget_verdict(5, 0, 10.0, 0, appetite_spend=100, spend=None,
                                           spend_unread="no meter")
        self.assertEqual((True, "minutes", "no meter"),
                         (unread["exhausted"], unread["reason"], unread["spend_unread"]))
        self.assertFalse(loop_guard.budget_verdict(0, 0, 10.0, 0, appetite_spend=100, spend=None,
                                                   spend_unread="no meter")["exhausted"])
        for phrase in ("*A ceiling in dollars.*", "*Failing closed:*",
                       "*Reusing `capacity.tokens`* as the ceiling",
                       "counted in priced input-equivalent tokens, not dollars",
                       "The reading is a lower bound, so the breaker can fire late but never early.",
                       "A meter that cannot read leaves spend unjudged at that boundary and says "
                       "why, while minutes and units still judge.", "Both keys ship at 0",
                       "a raise mid-run (`sprint.py appetite resize --spend`) needs a recorded "
                       "decision", f"stops the run with exit {loop_guard.BUDGET_EXIT}"):
            with self.subTest(adr=phrase):
                self.assertIn(phrase, adr)
        table = _rows(_section(body, "Committed evidence and records"), "Record")
        with tempfile.TemporaryDirectory() as d:
            self.assertIn("reports", cut_fixture(Path(d)))
        found = [r for r in table if release_cut.RELEASES_REL in _spans(r[1])]
        self.assertEqual(1, len(found), f"{len(found)} rows list {release_cut.RELEASES_REL}")
        self.assertEqual([], writer_problems(found[0][2], (("release_cut", "changelog-cut"),)))
        self.assertIn(sprint_report.report_dir("").as_posix(), trd_refresh.committed_trees(),
                      "premise: the release records sit in a swept tree")
        ledger = trd_refresh.until_tracked_records()[1]
        for tracked, pending in ((release_cut.RELEASES_REL, ledger), (ledger, release_cut.RELEASES_REL)):
            with self.subTest(tracked=tracked):
                held = pending_when_tracked(tracked)
                self.assertNotIn(tracked, held)
                self.assertIn(pending, held)
        state = _rows(_section(body, "JSON state files (under `.local/`)"), "File")
        row = _flat(next(r for r in state if "run-state.json" in _spans(r[0]))[2])
        kw = {"accepted_units": 1, "accepted_minutes": 1, "standing_units": 1,
              "standing_minutes": 1}
        spend = set(run_state.appetite_record(**kw, accepted_spend=2, standing_spend=1)) \
            - set(run_state.appetite_record(**kw))
        self.assertEqual({"spend", "standing_spend", "over_spend"}, spend)
        for key in sorted(spend):
            self.assertIn(f"`{key}`", row)
        self.assertIn('entry["decision"] = decision', _read(SCRIPTS / "lib" / "run_state.py"))
        self.assertIn("a resize records the decision behind each spend raise", row)
        closing = _flat(trd_refresh._adr(body, "013").rstrip().rsplit("\n- ", 1)[1])  # noqa: SLF001
        self.assertIn(f"{disclosed_range()}, and `sprint_report.py disclose` gave each a line", closing)
        self.assertIn("each report still reading VALID", closing)

    def test_the_tsd_names_the_spend_breaker_and_change_failure_rate(self) -> None:
        """US1343 AC5. Mutants: the TSD at its base, with no "spend", "change failure" or
        "settling", and its Scalability row tripping the breaker only "when the appetite's
        minutes or units are spent"; a named spend test renamed or dropped; the passage not
        naming `escape.py failure-rate`, the ratio, the window, the settling period, the not
        measured reading, or the ledger figure `deploy.py metrics` counts."""
        tsd = _body(_read(SPECS["tsd"]))
        row = _flat(next(line for line in tsd.splitlines()
                         if "the appetite breaker bounds an unattended run" in line))
        self.assertNotIn("minutes or units are spent", row)
        module = SCRIPTS / "tests" / "test_loop_guard_spend.py"
        tree = ast.parse(_read(module))
        held = {c.name: {f.name for f in c.body if isinstance(f, ast.FunctionDef)}
                for c in tree.body if isinstance(c, ast.ClassDef)}
        self.assertIn("`test_loop_guard_spend.py::LoopGuardSpendTests` holds the spend axis", row)
        named = re.findall(r"`(test_\w+)`", row)
        self.assertEqual(list(SPEND_TESTS), [n for n in named if n in SPEND_TESTS])
        for name in SPEND_TESTS:
            self.assertIn(name, held["LoopGuardSpendTests"], f"{name} is not in {module.name}")
        for phrase in ("stops the run at the appetite", "warns at each share `loop_guard.SPEND_WARNINGS` names",
                       "leave an unread meter unjudged", "holds the resolution order"):
            self.assertIn(phrase, row)
        self.assertEqual((95, 75), loop_guard.SPEND_WARNINGS)
        self.assertIn("metrics", verbs("deploy"))
        self.assertIn("change failures = `failed` + `rolled-back` rows over ALL rows",
                      _flat(inspect.getdoc(deploy.metrics)))
        passage = _flat(_section(_section(tsd, "Defect Management"), "Change failure rate"))
        for phrase in ("`escape.py failure-rate` derives change failure rate from the release "
                       "records `release_cut.py changelog-cut` writes",
                       "the releases with a linked incident over the releases counted",
                       f"in a {escape.WINDOW_DAYS}-day window",
                       f"A release inside the {escape.SETTLE_DAYS}-day settling period is named "
                       "as pending", "the rate reads not measured, never zero",
                       "the change failure figure `deploy.py metrics` counts from the deploy "
                       "ledger, its failed and rolled-back rows over all its rows",
                       "the sprint report's DORA row, which counts push-triggered CI runs"):
            with self.subTest(passage=phrase):
                self.assertIn(phrase, passage)

    def test_the_prd_and_the_trd_name_the_solution_review(self) -> None:
        """US1343 AC6, the part on `main`: the solution review row and keys for US1344 to US1346
        and US1348, and the ledger's TRD row. Mutants: the PRD and the TRD at its base, naming
        no solution review and no `solution-reviews.md`; the row out of the v5 and v6 table, or
        naming an `approach` sub-verb critic lacks; a key's default not `reference-config.md`'s;
        the ledger row at another path or writer, or pending while git tracks the ledger."""
        self.assertIn("solution review", FEATURES)
        self.assertLessEqual({"review.solution_review.min_points",
                              "review.solution_review.risk_classes",
                              "review.solution_review.panel"}, set(FLAGS))
        prd = _body(_read(SPECS["prd"]))
        marks, units = FEATURES["solution review"]
        self.assertEqual([], row_problems(inventory(prd, "v5 and v6 capabilities"), marks, units))
        row = " | ".join(one_row(inventory(prd), marks))
        subs = re.findall(r"`critic\.py approach ([a-z-]+)`", row)
        self.assertLessEqual({"record", "brief", "panel", "spend"}, set(subs))
        self.assertLessEqual(set(subs), set(subverbs("critic", "approach")))
        stated, flags = config_defaults(_read(CONFIG_REF)), flag_rows(prd)
        for key in ("review.solution_review.min_points", "review.solution_review.risk_classes",
                    "review.solution_review.panel"):
            self.assertEqual(stated[key], flags[key][0])
        self.assertIn("`[qa, product, persona]`", flags["review.solution_review.panel"][1])
        self.assertRegex(_read(REPO / "sdlc-studio" / ".config.yaml"),
                         r"(?m)^  solution_review:\n(?:.*\n)*?    panel: \[qa, product, persona\]$")
        ledger = critic.solution_reviews_path("").as_posix()
        self.assertEqual(f"sdlc-studio/reviews/{critic.SOLUTION_REVIEW_FILE}", ledger)
        self.assertEqual(ledger, trd_refresh.until_tracked_records()[1])
        table = _rows(_section(_body(_read(SPECS["trd"])), "Committed evidence and records"),
                      "Record")
        found = [r for r in table if ledger in _spans(r[1])]
        self.assertEqual(1, len(found), f"{len(found)} rows list {ledger}")
        self.assertIn("`critic.py approach record`", found[0][2])
        self.assertIn("record", subverbs("critic", "approach"))
        with mock.patch.object(trd_refresh, "_tracked", return_value=[]):
            self.assertLessEqual({ledger, release_cut.RELEASES_REL}, trd_refresh.pending_records())
        self.assertNotIn(ledger, pending_when_tracked(ledger))


if __name__ == "__main__":
    unittest.main()
