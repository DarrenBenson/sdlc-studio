"""US1119: `sprint lane accept` records a reviewer's verdict and, on APPROVE, finishes the unit.

Every case drives `sprint.py lane accept` through `sprint.main` against a throwaway repository
holding a story whose criterion passes (`shell true`), one whose criterion fails (`shell false`)
and a bug, each with the QA brief `lane land` saves and the note `critic.py brief` makes of it.
The note carries the `full` tier, which the fixture's risk band would never derive, and a later
decoy note for the same unit carries another fingerprint and tier, so a verdict recorded at
`full` was matched by the brief's own fingerprint. `critic.py record`, `verify_ac.py run`,
`transition.py set` and `sprint.py lane return` run for real through their entry points; a spy
on `lanes._script` names the calls made. One case stubs the record, for a REJECT at the review
cap: carrying a unit needs an open run whose batch holds it.

BG1290's cases land rounds of the green story for real, through `sprint.py lane land` from a
`lane-us0101` worktree checked out afresh for each round, so the brief `lane accept` reads is
the one a landing wrote, or none. BG1339's cases brief the seat again with `critic.py brief
--rejoinder` and accept the file that brief issued, after the repair landed or before it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/lanes.py
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
from lib import lanes, run_state  # noqa: E402

critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

GREEN, RED, BUG = "US0101", "US0102", "BG0001"
AUTHOR = "builder-agent"
APPROVE = "VERDICT: APPROVE\nISSUES: none\nBLOCKING: none\n"
REJECT = ("VERDICT: REJECT\n"
          "ISSUES: [new] the gate lets a red unit through; [new] a docstring overstates the "
          "refusal; [pre-existing] BG0900 the lane is slow\n"
          "BLOCKING: [new] the gate lets a red unit through\n")
CLAIMS = [{"surface": "commit message", "claim": "a", "ruling": "TRUE"},
          {"surface": f"changelog.d/{GREEN}.md", "claim": "a", "ruling": "TRUE"}]
MUTANTS = [{"mutant": "a stays one", "test": "tests/test_a.py::test_a", "result": "killed"}]
#: the worktree every round of the green story lands from, as `sprint lane run` names it
LANE_WT = f"lane-{GREEN.lower()}"
HAND_IN = "sdlc-studio/.local/lane"


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _unit(root: Path, uid: str, verify: str) -> None:
    kind, status = ("bugs", "In Progress") if uid.startswith("BG") else ("stories", "Review")
    _write(root, f"sdlc-studio/{kind}/{uid}-lane.md",
           f"# {uid}: lane\n\n> **Status:** {status}\n> **Points:** 2\n> **Epic:** EP0001\n"
           f"> **Severity:** Medium\n> **Affects:** src/a.py, tests/test_a.py, "
           f"changelog.d/{uid}.md\n\n## Acceptance Criteria\n\n### AC1: works\n"
           f"- **Verify:** shell {verify}\n")


def _status(root: Path, uid: str) -> str:
    path = next((root / "sdlc-studio").glob(f"*/{uid}-lane.md"))
    line = next(ln for ln in path.read_text(encoding="utf-8").splitlines() if "Status:" in ln)
    return line.split("**Status:**", 1)[1].strip()


class LaneAcceptTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = root = Path(self._tmp.name).resolve()
        _write(root, ".gitignore", "sdlc-studio/.local/\n")
        _write(root, "src/a.py", "A = 1\n")
        _write(root, "tests/test_a.py", "def test_a():\n    assert True\n")
        _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam\n\ncharter\n\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
        _unit(root, GREEN, "true")
        _unit(root, RED, "false")
        _unit(root, BUG, "true")
        gitutil.git(["init", "-q", "-b", "main"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "chore: the fixture"], root)
        self.fp = {}
        notes = []
        for uid in (GREEN, RED, BUG):
            text = f"QA brief for {uid}\nreview the diff of {uid}\n"
            _write(root, f"sdlc-studio/.local/briefs/{uid}-qa.txt", text)
            self.fp[uid] = critic.brief_fingerprint(text)
            notes.append({"fp": self.fp[uid], "unit": uid, "seat": "qa", "tier": "full"})
            notes.append({"fp": "0123456789ab", "unit": uid, "seat": "qa", "tier": "light"})
        _write(root, "sdlc-studio/.local/briefs.jsonl", "".join(json.dumps(n) + "\n"
                                                              for n in notes))
        files = [_write(root, f"sc/{n}.json", json.dumps(v))
                 for n, v in (("claims", CLAIMS), ("mutants", MUTANTS))]
        done = subprocess.run(
            [sys.executable, str(SCRIPTS / "critic.py"), "self-check", "record", "--unit", GREEN,
             "--claims", str(files[0]), "--mutants", str(files[1]), "--author", AUTHOR,
             "--root", str(root)], capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _accept(self, uid: str, verdict: str, *extra: str, stub=None,
                at: Path | None = None, reviewer: str = "qa-seat") -> tuple[int, str, str]:
        path = _write(self.root, str(at or f"verdicts/{uid}.txt"), verdict)
        real = lanes._script

        def spy(root, script, *args, **kw):
            self.calls.append((script, args))
            return (stub or real)(root, script, *args, **kw)

        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.object(lanes, "_script", spy), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "accept", "--unit", uid, "--verdict", str(path),
                              "--reviewer", reviewer, *extra, "--root", str(self.root)])
        return rc, out.getvalue(), err.getvalue()

    def _rows(self, uid: str) -> list[list[str]]:
        text = critic.verdicts_path(self.root).read_text(encoding="utf-8")
        return [[c.strip() for c in ln.strip().strip("|").split("|")]
                for ln in text.splitlines() if ln.startswith(f"| {uid} |")]

    def _scripts(self) -> list[str]:
        return [f"{script} {args[0]}" for script, args in self.calls]

    def test_an_approve_records_verifies_transitions_and_returns(self) -> None:
        rc, out, err = self._accept(GREEN, APPROVE, "--agent", "agent-x",
                                    "--proof", "unit=pinned")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self._scripts(), ["critic.py record", "verify_ac.py run",
                                           "transition.py set", "sprint.py lane"])
        row = self._rows(GREEN)[-1]
        # verdict, reviewer, author (the self-check's), date, brief fingerprint, tier
        # BG1520: the free-text `qa-seat` is kept and given the briefed seat's role group
        self.assertEqual([row[1], row[2], row[3], row[5], row[6]],
                         ["APPROVE", "qa-seat (qa)", AUTHOR, self.fp[GREEN], "full"])
        self.assertEqual(_status(self.root, GREEN), "Done")
        back = self.calls[-1][1]
        self.assertEqual(back[:3], ("lane", "return", "--units"))
        self.assertIn(("--agent", "agent-x"), list(zip(back, back[1:])))
        self.assertIn(("--proof", "unit=pinned"), list(zip(back, back[1:])))
        self.assertNotIn("--model", back)
        self.assertIn("AC1: passed", out)
        # a bug moves to Fixed, not Done; its author is named when no self-check names one
        self.calls.clear()
        rc, out, err = self._accept(BUG, APPROVE, "--author", "bug-builder", "--tokens", "1200",
                                    "--minutes", "3", "--gap", "unit=none owed",
                                    "--model", "claude-sonnet-4-6")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(_status(self.root, BUG), "Fixed")
        self.assertEqual(self._rows(BUG)[-1][3], "bug-builder")
        back = self.calls[-1][1]
        for pair in (("--tokens", "1200"), ("--minutes", "3.0"), ("--gap", "unit=none owed"),
                     ("--model", "claude-sonnet-4-6")):
            self.assertIn(pair, list(zip(back, back[1:])))
        self.assertNotIn("--agent", back)

    def test_an_approve_passes_on_every_warning_the_record_printed(self) -> None:
        """MUTANT: lane accept drops record's output once it has found the recorded row, so a
        verdict recorded with a caveat (taken against an earlier scope) moves the unit with no
        word of it."""
        real = lanes._script
        caveat = "WARNING the verdict was taken against an earlier Affects scope"

        def warned(root, script, *args, **kw):
            if script != "critic.py":
                return real(root, script, *args, **kw)
            said = f"recorded {GREEN} APPROVE [delivery] round 1 -> verdicts.md\n"
            return subprocess.CompletedProcess([script, *args], 0, said, caveat + "\n")

        rc, out, err = self._accept(GREEN, APPROVE, stub=warned)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(caveat, err)
        self.assertEqual(_status(self.root, GREEN), "Done")

    def test_a_reject_records_and_prints_only_the_blocking_findings(self) -> None:
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._scripts(), ["critic.py record"])
        self.assertEqual(self._rows(GREEN)[-1][1], "REJECT")
        self.assertEqual(_status(self.root, GREEN), "Review")
        self.assertIn("round 1", out)
        self.assertIn("BLOCKING: [new] the gate lets a red unit through", out)
        for unblocking in ("docstring overstates", "BG0900", "lane is slow"):
            self.assertNotIn(unblocking, out + err)
        # at the review cap the record carries the unit as a bug, and its id is printed
        self.calls.clear()

        def capped(root, script, *args, **kw):
            said = (f"recorded {GREEN} REJECT [delivery] round 2 -> verdicts.md\n"
                    f"{critic.carried_notice(GREEN, 'BG0042')}\n")
            return subprocess.CompletedProcess([script, *args], 0, said, "")

        rc, out, err = self._accept(GREEN, REJECT, stub=capped)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._scripts(), ["critic.py record"])
        self.assertIn("round 2", out)
        self.assertIn(f"{critic.CARRIED_REASON}: BG0042", out)
        self.assertEqual(_status(self.root, GREEN), "Review")

    def test_a_red_criterion_stops_the_transition(self) -> None:
        rc, out, err = self._accept(RED, APPROVE, "--author", "red-builder",
                                    "--agent", "agent-x")
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._scripts(), ["critic.py record", "verify_ac.py run"])
        self.assertEqual(_status(self.root, RED), "Review")
        self.assertIn("FAIL AC1: shell false", err)
        self.assertIn("NOT moved to Done", err)

    def test_a_refusal_records_nothing(self) -> None:
        cases = {"no brief": (RED, ("--author", "x"), "no QA brief"),
                 "no author": (RED, (), "name --author"),
                 "no unit": ("US0999", ("--author", "x"), "no artefact with id US0999"),
                 "no noted tier": (RED, ("--author", "x"), "records the review tier")}
        (self.root / "sdlc-studio/.local/briefs" / f"{RED}-qa.txt").unlink()
        for name, (uid, extra, said) in cases.items():
            with self.subTest(name):
                if name == "no author":
                    _write(self.root, f"sdlc-studio/.local/briefs/{RED}-qa.txt",
                           f"QA brief for {RED}\nreview the diff of {RED}\n")
                if name == "no noted tier":
                    (self.root / "sdlc-studio/.local/briefs.jsonl").unlink()
                rc, out, err = self._accept(uid, APPROVE, *extra)
                self.assertEqual(rc, 2, out + err)
                self.assertIn(said, err)
        self.assertEqual(self.calls, [])
        self.assertFalse(critic.verdicts_path(self.root).exists())

    # -- BG1520: the Reviewer cell names the briefed seat ---------------------------------

    def test_the_recorded_reviewer_cell_names_the_briefed_seat(self) -> None:
        """BG1520 AC1. MUTANTS: the value recorded as given, so `recorded_seat` reads nothing;
        the role group left off; the value replaced by the seat's bare holder, which drops the
        reviewer's instance; the role read only through a declared card, so a project with no
        qa card records nothing attributable."""
        rc, out, err = self._accept(GREEN, APPROVE, reviewer=f"qa-seat-{GREEN}-r1")
        self.assertEqual(rc, 0, out + err)
        cell = self._rows(GREEN)[-1][2]
        self.assertEqual(f"qa-seat-{GREEN}-r1 (qa)", cell,
                         "the cell is not the reviewer's own value in the holder and role form")
        self.assertEqual("qa", critic.recorded_seat(cell))
        # a project declaring no qa card: the shipped seat's role is still read from the value
        (self.root / "sdlc-studio/personas/seats/qa.md").unlink()
        rc, out, err = self._accept(BUG, APPROVE, "--author", "bug-builder",
                                    reviewer=f"qa-seat-{BUG}-r1")
        self.assertEqual(rc, 0, out + err)
        self.assertEqual("qa", critic.recorded_seat(self._rows(BUG)[-1][2]))

    def test_a_reviewer_naming_no_known_seat_is_refused(self) -> None:
        """BG1520 AC2. MUTANTS: the refusal dropped, so the value is recorded unattributed; the
        known seats left out of the refusal; the refusal written after the record; a value in the
        holder and role form, or naming the holder alone, refused; a value whose `(<role>)`
        group names an unbriefed seat accepted on a word, recorded under the group's seat."""
        for value in ("reviewer-r1", "engineering-seat-r1", "qa-seat-r1 (engineering)"):
            with self.subTest(refused=value):
                rc, out, err = self._accept(GREEN, APPROVE, reviewer=value)
                self.assertEqual(rc, 2, out + err)
                self.assertIn("known seats: engineering, product, qa", err)
                self.assertIn("the brief named qa", err)
                self.assertEqual(self.calls, [], "lane accept ran a script on the refused value")
                self.assertFalse(critic.verdicts_path(self.root).exists(), "a row was written")
        for value, uid in (("Sam (qa)", GREEN), ("Sam", BUG)):
            with self.subTest(recorded=value):
                named = ("--author", "bug-builder") if uid == BUG else ()
                rc, out, err = self._accept(uid, APPROVE, *named, reviewer=value)
                self.assertEqual(rc, 0, out + err)
                self.assertEqual("Sam (qa)", self._rows(uid)[-1][2])

    def test_a_build_seat_review_stays_independent_of_its_build_seat_author(self) -> None:
        """BG1520, the round-one regression. A second review by the build seat, accepted
        against the build seat's own `<holder> (<role>)` author, is recorded independent, as the
        base recorded it, and lane accept's claim agrees with the ledger; a reviewer that reads
        as the author is refused before anything is recorded. MUTANTS: the cell rewritten to
        the seat's bare signature (reviewer == author, a self-review the lane reports as
        independent); the self-review check dropped; the author the check reads not the one
        recorded; every unit's brief notes read, so a seat briefed for another unit passes."""
        _write(self.root, "sdlc-studio/personas/seats/engineering.md",
               "<!-- role: engineering -->\n# Dani\n\ncharter\n\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
        notes = self.root / "sdlc-studio/.local/briefs.jsonl"
        notes.write_text(notes.read_text(encoding="utf-8") + json.dumps(
            {"fp": "fedcba987654", "unit": BUG, "seat": "engineering", "tier": "full"}) + "\n",
            encoding="utf-8")
        builder = critic.seat_signature(self.root, "engineering")
        self.assertEqual("Dani (engineering)", builder)
        for value in ("Dani", builder):
            with self.subTest(refused=value):
                rc, out, err = self._accept(BUG, APPROVE, "--author", builder, reviewer=value)
                self.assertEqual(rc, 2, out + err)
                self.assertIn("would be recorded as a self-review", err)
                self.assertEqual(self.calls, [], "lane accept ran a script on a self-review")
                self.assertFalse(critic.verdicts_path(self.root).exists(), "a row was written")
                self.assertEqual("In Progress", _status(self.root, BUG))
        with self.subTest("a seat briefed only for another unit"):
            rc, out, err = self._accept(GREEN, APPROVE, reviewer=f"engineering-seat-{GREEN}-r1")
            self.assertEqual(rc, 2, out + err)
            self.assertIn("the brief named qa,", err)
        with self.subTest("the build seat's own review instance"):
            value = f"engineering-seat-{BUG}-r1"
            rc, out, err = self._accept(BUG, APPROVE, "--author", builder, reviewer=value)
            self.assertEqual(rc, 0, out + err)
            row = self._rows(BUG)[-1]
            self.assertEqual([f"{value} (engineering)", builder], [row[2], row[3]])
            self.assertEqual("engineering", critic.recorded_seat(row[2]))
            self.assertEqual((True, ""), critic.independence(row[2], row[3]))
            self.assertNotIn("self-review", out + err)
            self.assertEqual("Fixed", _status(self.root, BUG))
            claimed = self.calls[-1][1]
            self.assertIn("Fixed on an independent APPROVE (round 1)", claimed)

    def test_the_runbook_row_documents_the_seat_form(self) -> None:
        """BG1520 AC4. MUTANTS: the lane accept row back to a bare `--reviewer <name>`; the
        record row's form changed so the two differ."""
        runbook = (SCRIPTS.parent / "reference-sprint-toolchain.md").read_text(encoding="utf-8")
        rows = {verb: next(ln for ln in runbook.splitlines()
                           if ln.startswith("|") and f"`{verb} " in ln)
                for verb in ("sprint.py lane accept", "critic.py record")}
        form = '--reviewer "<holder> (<role>)"'
        for verb, row in rows.items():
            with self.subTest(verb):
                self.assertIn(form, row, f"the {verb} row does not document the seat form")
        self.assertNotIn("--reviewer <name>", rows["sprint.py lane accept"])

    # -- BG1290: the brief a landing leaves -----------------------------------------------

    def _land_round(self, body: str, message: str, *, claims: list | None = None,
                    self_check: bool = True, main_moves: bool = False,
                    units: str = GREEN) -> subprocess.CompletedProcess:
        """Land one round of the green story from a fresh `lane-us0101` worktree: `src/a.py`
        set to `body` and staged, handed in with `message` and, when `self_check`, a self-check
        whose claims are `claims` if given. `main_moves` commits to main's `src/a.py` after the
        worktree branched, so the landing stops at its rebase."""
        if not hasattr(self, "lanes"):
            tmp = tempfile.TemporaryDirectory()
            self.addCleanup(tmp.cleanup)
            self.lanes = Path(tmp.name).resolve()
        wt = self.lanes / LANE_WT
        gitutil.git(["worktree", "add", "-q", "-b", LANE_WT, str(wt), "main"], self.root)
        if main_moves:
            _write(self.root, "src/a.py", "A = 'main'\n")
            gitutil.git(["commit", "-q", "-m", "chore: main moves src/a.py", "--", "src/a.py"],
                        self.root)
        _write(wt, "src/a.py", body)
        gitutil.git(["add", "--", "src/a.py"], wt)
        _write(wt, f"{HAND_IN}/commit-msg.txt", message + "\n")
        if self_check:
            _write(wt, f"{HAND_IN}/{GREEN}-claims.json", json.dumps(claims or CLAIMS))
            _write(wt, f"{HAND_IN}/{GREEN}-mutants.json", json.dumps(MUTANTS))
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "sprint.py"), "lane", "land", "--worktree",
             str(wt), "--units", units, "--root", str(self.root)], capture_output=True,
            text=True, timeout=600, cwd=str(self.root), env=gitutil.git_env(), check=False)

    def _brief(self, uid: str = GREEN) -> Path:
        return self.root / f"sdlc-studio/.local/briefs/{uid}-qa.txt"

    def _landed_fp(self, landed: subprocess.CompletedProcess) -> str:
        """The fingerprint the landing printed for the brief it wrote; asserted to be the
        fingerprint of the brief now on disk."""
        printed = re.search(rf"^{GREEN}: self-check recorded; QA brief .* fingerprint: (\S+)$",
                            landed.stdout, re.M)
        self.assertIsNotNone(printed, landed.stdout + landed.stderr)
        fp = lanes.saved_brief_fingerprint(self._brief().read_text(encoding="utf-8"))
        self.assertEqual(printed.group(1), fp, "the brief on disk is not the one it wrote")
        return fp

    def test_accept_refuses_when_the_latest_landing_wrote_no_brief(self) -> None:
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        first = self._landed_fp(landed)
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        rows = self._rows(GREEN)
        self.assertEqual([rows[-1][1], rows[-1][5]], ["REJECT", first])
        # a self-check the critic refuses is refused before the commit, so lands nothing and
        # writes no brief (test_self_check_before_commit); one not handed in still lands
        repairs = {"not recorded": ({"self_check": False}, "self-check NOT RECORDED")}
        for n, (name, (how, why)) in enumerate(repairs.items(), start=3):
            with self.subTest(name):
                landed = self._land_round(f"A = {n}\n", f"fix({GREEN}): a is {n}", **how)
                self.assertEqual(landed.returncode, 1, landed.stdout + landed.stderr)
                self.assertIn(f"{GREEN}: {why} and no brief written", landed.stderr)
                self.calls.clear()
                rc, out, err = self._accept(GREEN, APPROVE)
                self.assertEqual(rc, 2, out + err)
                self.assertNotIn("APPROVE recorded", out)
                self.assertEqual(self.calls, [], "lane accept ran a script against no brief")
                self.assertEqual(self._rows(GREEN), rows, "a verdict was recorded")
                self.assertEqual(_status(self.root, GREEN), "Review")
                # the refusal names the landing that wrote no brief, and why it wrote none
                self.assertIn(f"no QA brief at sdlc-studio/.local/briefs/{GREEN}-qa.txt", err)
                self.assertIn(f"the landing of {LANE_WT} ", err)
                self.assertIn(f"wrote no brief: {GREEN}: {why}", err)

    def test_accept_reads_the_brief_by_the_normalised_unit_id(self) -> None:
        """BG1296: a repair landed under `--units us0101` with no self-check leaves no brief for
        `US0101`, so an APPROVE naming the unit in either spelling is refused for want of one and
        records nothing, rather than landing on the earlier round's brief."""
        _write(self.root, "sdlc-studio/.config.yaml", "review:\n  author_self_check: report\n")
        landed = self._land_round("A = 2\n", f"fix({GREEN}): a is two", self_check=False,
                                  units=GREEN.lower())
        self.assertEqual(landed.returncode, 1, landed.stdout + landed.stderr)
        self.assertFalse(self._brief().exists(), "the earlier round's brief was left")
        ledger = critic.verdicts_path(self.root)
        for spelling in (GREEN, GREEN.lower()):
            with self.subTest(spelling):
                self.calls.clear()
                rc, out, err = self._accept(spelling, APPROVE)
                self.assertEqual(rc, 2, out + err)
                self.assertIn(f"no QA brief at sdlc-studio/.local/briefs/{GREEN}-qa.txt", err)
                self.assertEqual(self.calls, [], "lane accept ran a script against no brief")
                self.assertFalse(ledger.exists(), "a verdict was recorded")
                self.assertEqual(_status(self.root, GREEN), "Review")

    def test_a_refused_transition_names_the_lane_return_that_finishes_the_unit(self) -> None:
        """BG1649: the verdict is recorded and the criteria are green, so the refusal of the
        move names `transition.py set` and then `sprint.py lane return`. Control: the same
        APPROVE with the move allowed prints no such advice."""
        real = lanes._script

        def refusing(root, script, *args, **kw):
            if (script, args[0]) == ("transition.py", "set"):
                return subprocess.CompletedProcess([script, *args], 1, "", "refused: stubbed\n")
            return real(root, script, *args, **kw)

        rc, out, err = self._accept(GREEN, APPROVE, stub=refusing)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(_status(self.root, GREEN), "Review")
        self.assertIn("refused: stubbed", err)
        self.assertIn(f"`transition.py set --id {GREEN} --status Done`, then "
                      f"`sprint.py lane return --units {GREEN}`", err)
        self.assertNotIn("sprint.py lane", self._scripts()[-1])
        rc, out, err = self._accept(BUG, APPROVE, "--author", "bug-builder")
        self.assertEqual(rc, 0, out + err)
        self.assertNotIn("then `sprint.py lane return --units", err)

    def test_lane_return_after_a_hand_transition_clears_the_lane(self) -> None:
        """BG1649: a unit moved by hand after that refusal is still in flight with its span
        open; the named `lane return` clears the one and closes the other."""
        run_state.open_run(self.root, batch=[GREEN])
        run_state.record_lane_start(self.root, GREEN)
        run_state.record_unit_actual(self.root, GREEN, run_state.UNIT_START_STATUS, False)
        path = next((self.root / "sdlc-studio").glob(f"*/{GREEN}-lane.md"))
        path.write_text(path.read_text(encoding="utf-8").replace(
            "> **Status:** Review", "> **Status:** Done"), encoding="utf-8")
        self.assertEqual([GREEN], [r["unit"] for r in run_state.lanes_in_flight(self.root)])
        span = lambda: (run_state.read(self.root).get(run_state.UNIT_ACTUALS) or {})[GREEN]
        self.assertTrue(span()["open"], "premise: the span is open")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main(["lane", "return", "--units", GREEN, "--root", str(self.root)])
        self.assertEqual(rc, 0, out.getvalue() + err.getvalue())
        self.assertEqual([], run_state.lanes_in_flight(self.root))
        self.assertFalse(span()["open"], "the span was left open")

    def test_a_landing_leaves_only_its_own_brief(self) -> None:
        earlier = self._brief().read_text(encoding="utf-8")
        # a landing that briefs the unit leaves its own brief, not the earlier round's
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        self.assertNotEqual(self._landed_fp(landed), self.fp[GREEN])
        none = self.root / f"sdlc-studio/.local/briefs/{GREEN}-qa.none"
        self.assertFalse(none.exists(), "a landing that wrote the brief left a no-brief note")
        landings = {"no self-check handed in": {"self_check": False},
                    # stopped part way, at the rebase: the worktree is left, so this goes last
                    "stopped at the rebase": {"main_moves": True}}
        for n, (name, how) in enumerate(landings.items(), start=3):
            with self.subTest(name):
                _write(self.root, f"sdlc-studio/.local/briefs/{GREEN}-qa.txt", earlier)
                landed = self._land_round(f"A = {n}\n", f"fix({GREEN}): a is {n}", **how)
                self.assertEqual(landed.returncode, 1, landed.stdout + landed.stderr)
                self.assertFalse(self._brief().exists(),
                                 f"a landing that wrote no brief left one ({name})")
                self.assertIn(f"the landing of {LANE_WT} ", none.read_text(encoding="utf-8"))
                # the other units' briefs are not this landing's to clear
                self.assertTrue(self._brief(RED).is_file())
        self.assertIn("rebasing", landed.stderr)

    def test_a_repair_with_its_own_brief_is_accepted(self) -> None:
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        self._landed_fp(landed)
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        # the brief text repeats from round to round, so round one's file is marked: the
        # fingerprint on disk matches the one the repair printed only if the repair rewrote it
        stale = self._brief().read_text(encoding="utf-8") + "round one's brief\n"
        _write(self.root, f"sdlc-studio/.local/briefs/{GREEN}-qa.txt", stale)
        landed = self._land_round("A = 3\n", f"fix({GREEN}): a is three")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        fresh = self._landed_fp(landed)
        self.assertNotEqual(fresh, critic.brief_fingerprint(stale))
        self.calls.clear()
        rc, out, err = self._accept(GREEN, APPROVE)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"{GREEN}: APPROVE recorded, round 2, against brief {fresh}", out)
        row = self._rows(GREEN)[-1]
        self.assertEqual([row[1], row[5]], ["APPROVE", fresh])
        self.assertEqual(_status(self.root, GREEN), "Done")

    # -- BG1339: a round-2 verdict answers a rejoinder brief ---------------------------------

    def _rejoinder(self, prior: Path, *tier: str) -> tuple[Path, str, str]:
        """Brief the QA seat with `critic.py brief --rejoinder <prior>` through its entry point;
        the verdict file it issued, and the fingerprint and tier its footer printed."""
        done = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "critic.py"), "brief", "--unit", GREEN,
             "--seat", "qa", "--rejoinder", str(prior), *tier, "--root", str(self.root)],
            capture_output=True, text=True, timeout=300, cwd=str(self.root),
            env=gitutil.git_env(), check=False)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("--- RE-REVIEW (rejoinder) ---", done.stdout)
        path = Path(re.search(r"^(/\S+\.txt)\nUNIT: ", done.stdout, re.M).group(1))
        fp = re.search(r"^brief fingerprint: (\S+)$", done.stderr, re.M).group(1)
        tier = re.search(r"^review tier: (\S+)", done.stderr, re.M).group(1)
        return path, fp, tier

    def _round_one_rejected(self) -> tuple[str, Path]:
        """Land round one and record its REJECT: the brief it was recorded against, and the
        verdict file the rejoinder quotes."""
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        first = self._landed_fp(landed)
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["REJECT", first])
        return first, self.root / f"verdicts/{GREEN}.txt"

    def test_a_round_two_verdict_records_against_its_rejoinder_brief(self) -> None:
        first, prior = self._round_one_rejected()
        landed = self._land_round("A = 3\n", f"fix({GREEN}): a is three")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        # at a tier the saved brief's note does not carry, so the tier is the rejoinder's own
        path, fp, tier = self._rejoinder(prior, "--tier", "full")
        self.assertEqual(tier, "full")
        self.assertNotIn(fp, (first, saved), "the rejoinder brief shares a fingerprint")
        self.calls.clear()
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"{GREEN}: APPROVE recorded, round 2, against brief {fp} at the {tier} "
                      f"tier", out)
        row = self._rows(GREEN)[-1]
        self.assertEqual([row[1], row[5], row[6]], ["APPROVE", fp, tier])
        # bound to the file the rejoinder brief issued, not transcribed
        self.assertEqual(row[7].split()[1:2], [path.name], row)
        self.assertTrue(row[7].startswith("sha256:"), row)
        self.assertEqual(self._scripts(), ["critic.py record", "verify_ac.py run",
                                           "transition.py set", "sprint.py lane"])
        self.assertEqual(_status(self.root, GREEN), "Done")

    def test_a_headerless_verdict_at_a_rejoinder_s_issued_path_records_against_it(self) -> None:
        """MUTANT: the headerless path match dropped, so a verdict a rejoinder brief issued that
        opens with no BRIEF line is recorded against the saved brief at its tier."""
        first, prior = self._round_one_rejected()
        landed = self._land_round("A = 3\n", f"fix({GREEN}): a is three")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        path, fp, tier = self._rejoinder(prior, "--tier", "full")
        self.assertNotIn(fp, (first, saved), "the rejoinder brief shares a fingerprint")
        rc, out, err = self._accept(GREEN, APPROVE, at=path)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"{GREEN}: APPROVE recorded, round 2, against brief {fp} at the {tier} "
                      f"tier", out)
        row = self._rows(GREEN)[-1]
        self.assertEqual([row[1], row[5], row[6]], ["APPROVE", fp, tier])

    def test_a_rejoinder_briefed_before_the_latest_landing_is_refused(self) -> None:
        _, prior = self._round_one_rejected()
        # briefed before the repair landed, so its reviewer read the round the REJECT judged
        path, _, _ = self._rejoinder(prior)
        landed = self._land_round("A = 3\n", f"fix({GREEN}): a is three")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        saved = self._landed_fp(landed)
        rows = self._rows(GREEN)
        self.calls.clear()
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path)
        self.assertEqual(rc, 2, out + err)
        self.assertEqual(self.calls, [], "lane accept ran a script on a stale rejoinder")
        self.assertEqual(self._rows(GREEN), rows, "a verdict was recorded")
        self.assertEqual(_status(self.root, GREEN), "Review")
        self.assertIn(f"{path} was issued by a rejoinder brief written before the landing that "
                      f"saved sdlc-studio/.local/briefs/{GREEN}-qa.txt (fingerprint {saved})",
                      err)
        self.assertIn(f"brief the seat again with `critic.py brief --unit {GREEN} --seat qa "
                      f"--rejoinder`", err)
        # positive control: the seat briefed again after that landing is recorded
        path, fp, _ = self._rejoinder(prior)
        rc, out, err = self._accept(GREEN, f"UNIT: {GREEN}\nBRIEF: {path.stem}\n{APPROVE}",
                                    at=path)
        self.assertEqual(rc, 0, out + err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["APPROVE", fp])

    def test_accept_refuses_when_the_affects_changed_since_the_self_check(self) -> None:
        """BG1290's round-1 review, P1 and P1b: a commit reaches main with no `lane land` of the
        unit, so its Affects change after the self-check the brief was written against, and the
        brief's text, which repeats from round to round, cannot show it. Under `block` accept
        refuses as `critic.py brief` would; under `report` it records with the same finding."""
        config = _write(self.root, "sdlc-studio/.config.yaml",
                        "review:\n  author_self_check: block\n")
        gitutil.git(["add", "--", str(config)], self.root)
        gitutil.git(["commit", "-q", "-m", "chore: the self-check gate blocks"], self.root)
        landed = self._land_round("A = 2\n", f"feat({GREEN}): a is two")
        self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
        first = self._landed_fp(landed)
        # positive control: the landing's own self-check is current, so the verdict is recorded
        rc, out, err = self._accept(GREEN, REJECT)
        self.assertEqual(rc, 1, out + err)
        self.assertEqual(self._rows(GREEN)[-1][1:6:4], ["REJECT", first])
        out_of_band = {"P1: a repair committed on main after the REJECT": False,
                       "P1b: a follow-up after a self-checked repair landing": True}
        for n, (name, relanded) in enumerate(out_of_band.items(), start=3):
            with self.subTest(name):
                if relanded:
                    landed = self._land_round(f"A = {n}\n", f"fix({GREEN}): a is {n}")
                    self.assertEqual(landed.returncode, 0, landed.stdout + landed.stderr)
                    self._landed_fp(landed)
                _write(self.root, "src/a.py", f"A = {n}0\n")
                gitutil.git(["commit", "-q", "-m", f"fix({GREEN}): a is {n}0", "--", "src/a.py"],
                            self.root)
                rows, stale = self._rows(GREEN), critic.read_self_checks(self.root)[-1]
                self.calls.clear()
                rc, out, err = self._accept(GREEN, APPROVE)
                self.assertEqual(rc, 2, out + err)
                self.assertNotIn("APPROVE recorded", out)
                self.assertEqual(self.calls, [], "lane accept ran a script on a stale self-check")
                self.assertEqual(self._rows(GREEN), rows, "a verdict was recorded")
                self.assertEqual(_status(self.root, GREEN), "Review")
                # the refusal names the self-check that no longer matches the unit's Affects
                self.assertIn(f"the self-check recorded for {GREEN} on {stale['date']} is "
                              f"stale: its digest {stale['digest']} is of an earlier diff", err)
                self.assertIn("review.author_self_check: block", err)
        # under `report` the same unit is recorded and moved, the stale self-check named
        _write(self.root, "sdlc-studio/.config.yaml", "review:\n  author_self_check: report\n")
        rc, out, err = self._accept(GREEN, APPROVE)
        self.assertEqual(rc, 0, out + err)
        self.assertIn(f"WARNING {GREEN}: the self-check recorded for {GREEN} on "
                      f"{stale['date']} is stale", err)
        self.assertEqual(self._rows(GREEN)[-1][1], "APPROVE")
        self.assertEqual(_status(self.root, GREEN), "Done")

    # -- BG1491: an APPROVE on a criterion with no Verify line moves nothing ----------------

    def _two_criteria(self, second_verify: str) -> None:
        """BUG with a second criterion, carrying `second_verify` as its Verify line or none."""
        line = f"- **Verify:** {second_verify}\n" if second_verify else ""
        _write(self.root, f"sdlc-studio/bugs/{BUG}-lane.md",
               f"# {BUG}: lane\n\n> **Status:** In Progress\n> **Points:** 2\n"
               f"> **Epic:** EP0001\n> **Severity:** Medium\n> **Affects:** src/a.py, "
               f"tests/test_a.py, changelog.d/{BUG}.md\n\n## Acceptance Criteria\n\n"
               f"### AC1: works\n- **Verify:** shell true\n\n### AC3: says so\n"
               f"- **Then** it says so\n{line}")

    def _briefed(self) -> None:
        """An open run holding BUG, whose lane was briefed and has not returned."""
        from lib import run_state  # noqa: PLC0415 - the fixture's own run record
        with unittest.mock.patch.dict(os.environ, {
                run_state.TRANSCRIPTS_ENV: str(self.root / "no-transcripts")}):
            run_state.open_run(self.root, batch=[BUG], goal="g")
        run_state.record_lane_start(self.root, BUG, "engineering")
        self.assertEqual([BUG], self._in_flight())

    def _in_flight(self) -> list:
        from lib import run_state  # noqa: PLC0415 - the fixture's own run record
        return [row["unit"] for row in run_state.lanes_in_flight(self.root)]

    def test_an_approve_on_a_criterion_with_no_verify_line_moves_nothing(self) -> None:
        """BG1491 AC1. MUTANT: no check before the record, so the APPROVE is recorded, BUG is
        moved to Fixed and its return then reports the lane blocked on AC3."""
        self._two_criteria("")
        self._briefed()
        rc, out, err = self._accept(BUG, APPROVE, "--author", "bug-builder")
        self.assertEqual(2, rc, out + err)
        self.assertIn("AC3 (says so)", err)
        self.assertIn("no Verify line", err)
        self.assertEqual([], self.calls, "a script ran before the refusal")
        self.assertFalse(critic.verdicts_path(self.root).exists(), "a verdict was recorded")
        self.assertEqual("In Progress", _status(self.root, BUG))
        self.assertEqual([BUG], self._in_flight(), "the lane record moved")
        # a REJECT moves nothing, so it is recorded as before
        rc, out, err = self._accept(BUG, REJECT, "--author", "bug-builder")
        self.assertEqual(1, rc, out + err)
        self.assertEqual("REJECT", self._rows(BUG)[-1][1])

    def test_an_approve_with_every_criterion_specified_transitions_and_returns(self) -> None:
        """BG1491 AC2. MUTANT: the check refuses whenever a unit has more than one criterion,
        or counts a criterion's `Then` line as missing its Verify."""
        self._two_criteria("shell true")
        self._briefed()
        rc, out, err = self._accept(BUG, APPROVE, "--author", "bug-builder")
        self.assertEqual(0, rc, out + err)
        self.assertEqual(["critic.py record", "verify_ac.py run", "transition.py set",
                          "sprint.py lane"], self._scripts())
        self.assertEqual("Fixed", _status(self.root, BUG))
        self.assertEqual([], self._in_flight(), "the lane was not returned")
        self.assertIn("AC3: passed", out)


if __name__ == "__main__":
    unittest.main()
