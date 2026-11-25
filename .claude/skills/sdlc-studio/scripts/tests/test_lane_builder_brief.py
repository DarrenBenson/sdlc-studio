"""US1093: `sprint.py lane brief` hands a fresh builder agent everything it needs for one unit.

The brief carries the unit's Affects, one path per line, and a commit step that stages exactly
those paths; the author self-check `critic.author_self_check` prints, verbatim but for its record
line, which names the hand-in files instead (US1120); the hand-in files and the command that runs
the unit's criteria; and the engineering seat card's
work render to adopt. The toolchain runbook's delivery table builds each unit that way: a fresh
agent per unit (a fresh session where the harness has no subagents), waited on by its completion
notification and accepted back through `sprint.py lane return`.

The brief tests drive `sprint.py lane brief` in-process against a throwaway project with an
open run; the runbook test reads THIS repository's shipped runbook, as the criterion names it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import re
import shlex
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

critic = loader.load_script("critic")
persona_resolve = loader.load_script("persona_resolve")
sprint = loader.load_script("sprint")
from lib import run_state, sdlc_md  # noqa: E402

# parents: [0] tests [1] scripts [2] the shipped skill.
SKILL = Path(__file__).resolve().parents[2]
BATCH = ("US0101", "US0102")
# A parenthetical note and a test file and a fragment among the paths: the note is stripped only
# by `affects_files`, and the test file and fragment give the self-check something to name.
AFFECTS = {"US0101": "src/other.py, tests/test_other.py",
           "US0102": "src/app.py (new), tests/test_app.py, changelog.d/US0102.md"}
#: A project engineering seat with its work render and the review render's three sections, the
#: floor the persona standard holds a seat card to before it frames any brief.
PROJECT_SEAT = ("<!-- role: engineering -->\n# Ola - the project's engineer\n\n"
                "## How They Work *(work render)*\n\nSmall diffs, test first.\n"
                "\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")


def _live(name: str):
    """The module the command resolves at call time. Another test module may re-register a
    sibling in `sys.modules`, so a patch on the object loaded here would miss the command."""
    return sys.modules.get(name) or importlib.import_module(name)


def _story(root: Path, uid: str, affects: str | None) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    field = f"> **Affects:** {affects}\n" if affects is not None else ""
    (d / f"{uid}-x.md").write_text(
        f"# {uid}: x\n\n> **Status:** Ready\n{field}> **Points:** 2\n\n"
        "## Acceptance Criteria\n\n### AC1: it holds\n\n- **Verify:** file src/app.py\n",
        encoding="utf-8")


def _project(d: str, affects: dict[str, str | None] | None = None) -> Path:
    """Two groomed Ready stories and an open run whose batch holds both."""
    root = Path(d) / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
    for uid in BATCH:
        _story(root, uid, (affects or AFFECTS).get(uid))
    run_state.open_run(root, batch=list(BATCH), goal="g")
    return root


def _brief(root: Path, uid: str) -> str:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = sprint.main(["lane", "brief", "--units", uid, "--root", str(root)])
    if rc != 0:
        raise AssertionError(f"lane brief refused ({rc}): {err.getvalue()}")
    return out.getvalue()


def _unit_text(root: Path, uid: str) -> str:
    return (root / "sdlc-studio" / "stories" / f"{uid}-x.md").read_text(encoding="utf-8")


def _listed_affects(out: str) -> list[str]:
    """The paths under the brief's one Affects heading, one per indented line."""
    lines = out.splitlines()
    heads = [i for i, ln in enumerate(lines) if ln.startswith("Affects (")]
    if len(heads) != 1:
        raise AssertionError(f"expected one Affects heading, found {len(heads)}:\n{out}")
    listed = []
    for ln in lines[heads[0] + 1:]:
        if not ln.startswith("  "):
            break
        listed.append(ln.strip())
    return listed


class _Isolated(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        transcripts = Path(self._tmp.name) / "transcripts"
        transcripts.mkdir()
        env = unittest.mock.patch.dict(os.environ,
                                       {run_state.TRANSCRIPTS_ENV: str(transcripts)})
        env.start()
        self.addCleanup(env.stop)


class BuilderBriefTests(_Isolated):

    def test_the_brief_names_the_affects_and_stages_only_them(self) -> None:
        """AC1. MUTANTS: the Affects popped from the brief before rendering, as `lane_dispatch`
        did, so no Affects list is printed; the raw field split on commas, which keeps the
        `(new)` note on a path; `git add -A` or `git commit -a` in the commit step, which sweeps
        a concurrent lane's files into this unit's commit; the batch's first unit named for the
        commit subject rather than the one briefed."""
        root = _project(self._tmp.name)
        out = _brief(root, "US0102")
        declared = sdlc_md.affects_files(_unit_text(root, "US0102"))
        self.assertEqual(["src/app.py", "tests/test_app.py", "changelog.d/US0102.md"],
                         declared, "premise: the note is stripped by the shared parser")
        self.assertEqual(declared, _listed_affects(out))
        lines = out.splitlines()
        adds = [i for i, ln in enumerate(lines) if ln.strip().startswith("git add")]
        self.assertEqual(1, len(adds), f"expected one staging command:\n{out}")
        self.assertEqual(["git", "add", "--", *declared], shlex.split(lines[adds[0]]))
        self.assertIn("US0102", lines[adds[0] - 1], "the commit step names the unit")
        self.assertIn("commit subject", lines[adds[0] - 1])
        self.assertNotIn("US0101", lines[adds[0] - 1])
        for sweep in ("git add -A", "git add .", "git commit -a", "git add --all"):
            self.assertNotIn(sweep, out)

    def test_a_unit_with_no_affects_is_told_so_and_stages_nothing(self) -> None:
        """MUTANT: an empty Affects rendered as an empty list and a bare `git add --`, which
        stages nothing and reads as a step done."""
        root = _project(self._tmp.name, {"US0101": "src/other.py", "US0102": None})
        out = _brief(root, "US0102")
        self.assertEqual([], sdlc_md.affects_files(_unit_text(root, "US0102")), "premise")
        self.assertIn("Affects: NONE DECLARED", out)
        self.assertNotIn("git add", out)
        self.assertIn("declares no Affects, so there is no path to stage", out)

    def test_the_brief_carries_the_self_check_and_the_commands_for_this_unit(self) -> None:
        """AC2. MUTANTS: the self-check steps retyped in sprint.py, so the brief keeps them when
        `author_self_check` changes; the self-check left out; either command carrying another
        unit's id (the batch's first, US0101); a command printed before the self-check."""
        root = _project(self._tmp.name)
        real = critic.author_self_check(root, "US0102")
        out = _brief(root, "US0102")
        # Verbatim but for the hand-in rewrite: US1120 hands the record to `sprint lane land`.
        after = 0
        for ln in (ln for ln in sprint._hand_in_self_check(real, "US0102").splitlines()
                   if "do not record them yourself" not in ln):
            after = out.index(ln, after) + len(ln)
        self.assertNotIn("self-check record", out)
        record = "sdlc-studio/.local/lane/US0102-claims.json"
        verify = "verify_ac.py run --id US0102"
        self.assertGreater(out.find(record, after), -1, "the record command after the self-check")
        self.assertGreater(out.find(verify, after), -1, "the verify command after the self-check")
        named = [ln for ln in out[after:].splitlines()
                 if "-claims.json" in ln or "verify_ac.py" in ln]
        self.assertTrue(named and all("US0101" not in ln for ln in named), named)

        stub = "STUB SELF-CHECK for {unit}\nsecond line of the stub"
        with unittest.mock.patch.object(
                _live("critic"), "author_self_check", lambda _root, unit: stub.format(unit=unit)):
            changed = _brief(root, "US0102")
        self.assertIn(stub.format(unit="US0102"), changed, "the brief follows the replacement")
        self.assertNotIn(real, changed)
        after = changed.index("second line of the stub")
        self.assertGreater(changed.find(record, after), -1)
        self.assertGreater(changed.find(verify, after), -1)

    def test_the_brief_names_the_engineering_seats_work_render(self) -> None:
        """AC3. MUTANTS: the shipped default's path hard-coded, which shadows the project's own
        seat; the review render named."""
        root = _project(self._tmp.name)
        shipped = persona_resolve.resolve_card(root, "engineering", render="build")
        self.assertEqual(SKILL / "templates" / "personas" / "amigos" / "engineering.md",
                         shipped, "premise: with no project card the shipped default resolves")
        self.assertEqual([str(shipped)], self._seat_paths(_brief(root, "US0101")))

        seats = root / "sdlc-studio" / "personas" / "seats"
        seats.mkdir(parents=True)
        (seats / "ola.md").write_text(PROJECT_SEAT, encoding="utf-8")
        own = persona_resolve.resolve_card(root, "engineering", render="build")
        self.assertEqual(seats / "ola.md", own, "premise: the project card resolves")
        out = _brief(root, "US0101")
        self.assertEqual([str(own)], self._seat_paths(out))
        self.assertNotIn(str(shipped), out)

    def test_a_project_with_no_engineering_card_is_told_so(self) -> None:
        """MUTANT: no seat line when nothing resolves, which reads the same as a brief that
        never looked."""
        root = _project(self._tmp.name)
        with unittest.mock.patch.object(_live("persona_resolve"), "resolve_card",
                                        lambda *a, **k: None):
            out = _brief(root, "US0101")
        self.assertIn("Seat: no engineering seat card resolves", out)

    def test_a_one_unit_schema3_batch_briefed_by_its_hyphenated_id_has_no_seam(self) -> None:
        """BG1302's recorded steps: a schema-3 run opened by `sprint plan --worklist --write`
        holds the id without its hyphen, and the brief asked for by the id as written paired
        the unit with itself."""
        uid = "US-01M6XQJF"
        root = Path(self._tmp.name) / "repo"
        (root / "src").mkdir(parents=True)
        (root / "src" / "app.py").write_text("x = 1\n", encoding="utf-8")
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")
        _story(root, uid, "src/app.py")
        (root / "w.txt").write_text(uid + "\n", encoding="utf-8")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            planned = sprint.main(["plan", "--worklist", str(root / "w.txt"), "--write",
                                   "--no-fetch", "--root", str(root)])
            self.assertEqual(0, planned, err.getvalue())
            self.assertEqual(["US01M6XQJF"], run_state.read(root)["batch"])
            out.truncate(0)
            out.seek(0)
            rc = sprint.main(["lane", "brief", "--units", uid, "--format", "json",
                              "--root", str(root)])
        self.assertEqual(0, rc, err.getvalue())
        printed = json.loads(out.getvalue())
        self.assertEqual([], printed["seams"])
        self.assertEqual([[]], [b["seams"] for b in printed["briefs"]])
        self.assertNotIn("Seam with", _brief(root, uid))

    def test_the_brief_lists_the_surfaces_rulings_and_results_the_record_accepts(self) -> None:
        """BG1512 AC2. MUTANTS: the list left out, or a surface, ruling or result named only in
        passing; the values retyped in sprint.py, so the list keeps a value the record stops
        accepting (the patched constants below); a page or a code file of the Affects listed
        when the record would refuse it, or a page it would accept left off."""
        affects = "src/app.py, tests/test_app.py, docs/guide.md, changelog.d/US0102.md"
        root = _project(self._tmp.name, {"US0101": "src/other.py", "US0102": affects})

        def listed(out: str) -> str:
            lines = [ln for ln in out.splitlines() if "The values the record accepts" in ln]
            self.assertEqual(1, len(lines), out)
            return lines[0]

        line = listed(_brief(root, "US0102"))
        live = _live("critic")
        required, optional = live.claim_surfaces(sdlc_md.affects_files(_unit_text(root, "US0102")))
        self.assertEqual(["commit message", "changelog.d/US0102.md"], required, "premise")
        self.assertEqual([*live.CLAIM_SURFACES, "docs/guide.md"], optional, "premise")
        self.assertIn("surface: " + "; ".join([*required, *optional]) + ";", line)
        self.assertIn("ruling: TRUE, FALSE, UNVERIFIABLE,", line)
        self.assertIn("result: killed, survived", line)
        self.assertNotIn("src/app.py", line)
        # a test file is no claim surface; it is named only as where a mutant's test lives
        self.assertNotIn("tests/test_app.py", line.split("; ruling:")[0])
        with unittest.mock.patch.object(live, "MUTANT_RESULTS", ("killed", "survived", "x")), \
                unittest.mock.patch.object(live, "CLAIM_RULINGS", ("TRUE", "MAYBE")):
            drifted = listed(_brief(root, "US0102"))
        self.assertIn("result: killed, survived, x", drifted)
        self.assertIn("ruling: TRUE, MAYBE,", drifted)

    def test_the_hand_in_line_names_the_accepted_rulings_and_test_files(self) -> None:
        """The hand-in line says a ruling is one of the accepted values, written bare, and that
        each mutant's test is a `path::name` in one of the unit's Affects test files, named."""
        affects = "src/app.py, tests/test_app.py, tests/test_more.py, changelog.d/US0102.md"
        root = _project(self._tmp.name, {"US0101": "src/other.py", "US0102": affects})

        def hand_in(out: str) -> str:
            lines = [ln for ln in out.splitlines() if "The values the record accepts" in ln]
            self.assertEqual(1, len(lines), out)
            return lines[0]

        line = hand_in(_brief(root, "US0102"))
        self.assertIn("ruling: TRUE, FALSE, UNVERIFIABLE, bare, the evidence in the claim", line)
        self.assertIn("each mutant's test: a `path::name` in one of the unit's Affects test "
                      "files, tests/test_app.py, tests/test_more.py", line)
        self.assertNotIn("src/app.py", line)
        # a unit whose Affects declares no test file is given no test-file rule
        line = hand_in(_brief(root, "US0101"))
        self.assertNotIn("path::name", line)
        self.assertIn("ruling: TRUE, FALSE, UNVERIFIABLE, bare", line)

    def _repo_and_worktree(self) -> tuple[Path, Path]:
        """The project committed on `main`, and a linked worktree on its own branch at main."""
        root = _project(self._tmp.name)
        gitutil.git(["init", "-q", "-b", "main"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "base"], root)
        wt = Path(self._tmp.name) / "wt"
        gitutil.git(["worktree", "add", "-q", "-b", "lane", str(wt), "main"], root)
        return root, wt

    def _brief_in(self, where: Path, uid: str = "US0102") -> tuple[str, list[str]]:
        """`lane brief` run in `where` with git confined to the fixture: (stdout, stderr lines)."""
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, gitutil.git_env(), clear=True), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "brief", "--units", uid, "--root", str(where)])
        self.assertEqual(0, rc, err.getvalue())
        return out.getvalue(), err.getvalue().splitlines()

    @staticmethod
    def _short(where: Path, ref: str) -> str:
        return gitutil.git(["rev-parse", "--short", ref], where, text=True).stdout.strip()

    def test_a_worktree_behind_the_roots_branch_is_warned_with_the_fast_forward(self) -> None:
        root, wt = self._repo_and_worktree()
        story = root / "sdlc-studio" / "stories" / "US0102-x.md"
        story.write_text(story.read_text(encoding="utf-8")
                         + "\n### AC2: it holds again\n\n- **Verify:** file src/app.py\n",
                         encoding="utf-8")
        gitutil.git(["commit", "-q", "-am", "groom US0102"], root)
        out, err = self._brief_in(wt)
        self.assertNotIn("AC2", out)                     # the stale copy is what was briefed
        warned = [ln for ln in err if ln.startswith("WARNING") and "--ff-only" in ln]
        self.assertEqual(1, len(warned), err)
        self.assertIn(f"this worktree's HEAD {self._short(wt, 'HEAD')} is not a descendant of "
                      f"main at {self._short(root, 'main')}", warned[0])
        self.assertIn("`git merge --ff-only main`", warned[0])
        self.assertNotEqual(self._short(wt, "HEAD"), self._short(root, "main"), "premise")
        # the fast-forward it names brings the unit up to date, and the warning goes
        gitutil.git(["merge", "--ff-only", "-q", "main"], wt)
        out, err = self._brief_in(wt)
        self.assertIn("AC2", out)
        self.assertFalse([ln for ln in err if "--ff-only" in ln], err)

    def test_an_up_to_date_worktree_and_the_root_are_not_warned(self) -> None:
        root, wt = self._repo_and_worktree()
        at_tip, err = self._brief_in(wt)
        self.assertFalse([ln for ln in err if "--ff-only" in ln], err)
        here, err = self._brief_in(root)
        self.assertFalse([ln for ln in err if "--ff-only" in ln], err)
        self.assertEqual(here.replace(str(root), "<top>"), at_tip.replace(str(wt), "<top>"))
        # ahead of the tip is not behind it
        (wt / "src" / "app.py").write_text("x = 2\n", encoding="utf-8")
        gitutil.git(["commit", "-q", "-am", "the lane's own work"], wt)
        _out, err = self._brief_in(wt)
        self.assertFalse([ln for ln in err if "--ff-only" in ln], err)
        # the root itself, behind nothing, even with its branch moved past the worktree
        (root / "src" / "app.py").write_text("x = 3\n", encoding="utf-8")
        gitutil.git(["commit", "-q", "-am", "main moves"], root)
        _out, err = self._brief_in(root)
        self.assertFalse([ln for ln in err if "--ff-only" in ln], err)
        # a main worktree on no branch names no branch to fast-forward to
        gitutil.git(["checkout", "-q", "--detach"], root)
        _out, err = self._brief_in(wt)
        self.assertFalse([ln for ln in err if "--ff-only" in ln], err)

    @staticmethod
    def _obligation_rows(out: str) -> list[str]:
        lines = out.splitlines()
        rows = []
        for ln in lines[lines.index("Obligations on this lane:") + 1:]:
            if not ln.startswith("  - "):
                break
            rows.append(ln[4:])
        return rows

    def _committed(self, branch: str) -> Path:
        """The project committed on `branch`, a trunk that need not be called main."""
        root = _project(self._tmp.name)
        gitutil.git(["init", "-q", "-b", branch], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "base"], root)
        return root

    def test_the_landing_obligation_names_lane_land_and_no_branch(self) -> None:
        root = self._committed("trunk")
        out, _err = self._brief_in(root)
        rows = self._obligation_rows(out)
        landing = [r for r in rows if "sprint lane land" in r]
        self.assertEqual(1, len(landing), rows)
        self.assertIn("The lane is landed by `sprint lane land` onto the root's branch: open no "
                      "PR and push no branch", landing[0])
        for row in rows:                       # no obligation names a trunk or a fast-forward
            self.assertNotRegex(row, r"\bmain\b")
            self.assertNotIn("fast-forward", row.lower())
        # beside the brief's own instruction to leave the commit to the landing
        self.assertIn("Do not commit and do not record the self-check", out)

    def test_a_main_checkout_lane_is_told_the_orchestrator_commits_it(self) -> None:
        """A unit declaring `Isolation: home` is built in the main checkout, which `lane land`
        refuses, so its landing obligation agrees with its stage line: the orchestrator commits
        it onto the root's branch, with no PR, no pushed branch and the pr-required exception."""
        root = _project(self._tmp.name)
        story = root / "sdlc-studio" / "stories" / "US0102-x.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            "> **Points:** 2\n", "> **Points:** 2\n> **Isolation:** home\n"), encoding="utf-8")
        out = _brief(root, "US0102")
        rows = self._obligation_rows(out)
        landing = [r for r in rows if "onto the root's branch" in r]
        self.assertEqual([sprint.LANE_HOME_LANDING], landing, rows)
        self.assertIn("the orchestrator commits it onto the root's branch", landing[0])
        self.assertTrue(landing[0].endswith(
            "open no PR and push no branch, unless `release_strategy` is `pr-required`."))
        self.assertNotIn("The lane is landed by `sprint lane land`", out)
        self.assertIn("`sprint lane land` lands only a worktree, so the orchestrator commits", out)
        for row in rows:
            self.assertNotRegex(row, r"\bmain\b")
            self.assertNotIn("fast-forward", row.lower())
        # the control: the same project's worktree lane keeps the landing through `lane land`
        self.assertIn(sprint.LANE_LANDING, self._obligation_rows(_brief(root, "US0101")))

    def test_the_landing_obligation_keeps_the_pr_required_exception(self) -> None:
        out = _brief(_project(self._tmp.name), "US0102")
        landing = [r for r in self._obligation_rows(out) if "sprint lane land" in r]
        self.assertEqual(1, len(landing), out)
        self.assertTrue(landing[0].endswith(
            "open no PR and push no branch, unless `release_strategy` is `pr-required`."),
            landing[0])

    def test_the_brief_names_the_fast_forward_step_and_the_base_to_build_on(self) -> None:
        root = self._committed("trunk")
        harness = Path(self._tmp.name) / "harness"      # cut from origin's older commit
        gitutil.git(["worktree", "add", "-q", "--detach", str(harness), "trunk"], root)
        story = root / "sdlc-studio" / "stories" / "US0102-x.md"
        story.write_text(story.read_text(encoding="utf-8") + "\n<!-- groomed -->\n",
                         encoding="utf-8")
        gitutil.git(["commit", "-q", "-am", "groom US0102"], root)
        tip = self._short(root, "trunk")
        step = "`git merge --ff-only trunk`"
        for where in (root, harness):                   # printed by the orchestrator or here
            out, _err = self._brief_in(where)
            base = [ln for ln in out.splitlines() if ln.startswith("Base: ")]
            self.assertEqual(1, len(base), out)
            self.assertIn(f"build on trunk at {tip}", base[0])
            self.assertIn(step, base[0])
            self.assertLess(out.index("Base: "), out.index("Obligations on this lane:"))
        # the step it names puts the harness worktree on the base
        self.assertNotEqual(tip, self._short(harness, "HEAD"), "premise: the worktree is behind")
        gitutil.git(["merge", "--ff-only", "-q", "trunk"], harness)
        self.assertEqual(tip, self._short(harness, "HEAD"))
        # a root on no branch names its commit as the base and the step to it
        gitutil.git(["checkout", "-q", "--detach"], root)
        out, _err = self._brief_in(root)
        self.assertIn(f"Base: build on commit {tip}", out)
        self.assertIn(f"`git merge --ff-only {tip}`", out)

    def test_a_brief_outside_git_names_no_base(self) -> None:
        out = _brief(_project(self._tmp.name), "US0102")
        self.assertNotIn("Base: ", out)

    def _seat_paths(self, out: str) -> list[str]:
        """The card each Seat line names as the work render to adopt."""
        seat = [ln for ln in out.splitlines() if ln.startswith("Seat: ")]
        self.assertEqual(1, len(seat), out)
        self.assertNotIn("review render", seat[0])
        m = re.fullmatch(r"Seat: adopt the work render of the engineering seat card (\S+) - .+",
                         seat[0])
        self.assertIsNotNone(m, seat[0])
        return [m.group(1)]


    def test_the_brief_says_where_a_hand_run_mutant_runs(self) -> None:
        """The lane brief's hand-in instruction for the unit's MUTANTS.json carries critic's
        where-to-run sentence, so a builder runs a mutant the runner cannot run in a worktree,
        never in a copy of the tests alone. Mutant: the sentence put on a line naming
        `self-check record`, which `_hand_in_self_check` replaces, so the brief drops it."""
        root = _project(self._tmp.name)
        out = _brief(root, "US0102")
        mutants = "US0102-mutants.json"
        lines = [ln for ln in out.splitlines()
                 if f"goes in {mutants} as {{mutant, test, result, answer}}" in ln]
        self.assertEqual(1, len(lines), out)
        for want in ("run such a mutant by hand in the lane's own worktree or a detached "
                     "worktree of the repository (`git worktree add --detach`), never in a copy "
                     "of the tests alone",):
            self.assertIn(want, lines[0])
        real = critic.author_self_check(root, "US0102")
        place = real[real.index("run such a mutant by hand"):].split("\n", 1)[0]
        self.assertIn(place, lines[0], "the brief's sentence is not critic's own")
        self.assertNotIn("self-check record", out)

#: The rows the deliver table must hold, as (Do, Command, Instead of) cells.
DELIVER_ROWS = (
    ("Build a unit",
     "`sprint.py lane brief --units <id>`, handed to a fresh agent; a harness without "
     "subagents starts a fresh session per unit from the same brief",
     "building it in the orchestrating context"),
    ("Wait for the builder", "its completion notification", "polling its output or sleeping"),
    ("Accept its return", "`sprint.py lane return --units <id>`",
     "reading the builder's diff or transcript into the orchestrating context"),
)


class BuilderRunbookTests(unittest.TestCase):

    def test_the_deliver_table_builds_each_unit_in_a_fresh_agent(self) -> None:
        """AC4. MUTANTS: a row missing; a Command cell naming another command; the rule stated as
        prose under the table, which is no row; the build row with no fallback for a harness
        without subagents."""
        text = (SKILL / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        m = re.search(r"(?ms)^## 3\. Deliver a unit\n(.*?)(?=^## |\Z)", text)
        self.assertIsNotNone(m, "the runbook has no `## 3. Deliver a unit` section")
        tables = list(sdlc_md.iter_tables(m.group(1)))
        self.assertEqual(1, len(tables))
        self.assertEqual(["Do", "Command", "Instead of"], tables[0]["header"])
        rows = [tuple(cells) for _n, cells in tables[0]["rows"]]
        for row in DELIVER_ROWS:
            self.assertIn(row, rows)


if __name__ == "__main__":
    unittest.main()
