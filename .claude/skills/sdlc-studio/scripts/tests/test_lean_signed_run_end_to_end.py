"""BG0862: the operator's whole path, unstubbed - close, commit, sign, commit, check.

Every other close and sign test stubs the chain (`test_lean_close._green_steps`) or the seal
(`test_lean_sign._seal_stubbed`), so none proves the run end the operator actually runs. This one
runs it once, on a schema 3 (ULID) project, through the shipped command lines and nothing else:
each step is a subprocess of a script beside this test, with the real close chain and the real
seal. The run holds every thing the signed page must disclose:

- an approved story at Review and an approved bug at In Progress, each with an In Progress span
  opened inside the run on a token meter that keeps growing (BG0848, BG0859);
- a bug carried at the review cap by its reviewer's round-2 REJECT, then discharged by that
  reviewer's APPROVE and moved to Fixed through its own gate, no `--force` (BG0850, BG0829);
- a `sprint decision resolve` (BG0851);
- a story dropped from the batch and then moved with `transition.py set --force` (BG0851);
- a lesson class repeated twice since it was recorded, which the close graduates into a CR that
  the retro rules by its class code (BG0849);
- and the page names each known issue's ruling, the close's own CR included (BG0865).

A bare `sprint.py close` scaffolds the retro with the run id and the carried table (BG0826); the
test fills the table and the Keep/Stop/Try lines, then `close --retro`, commit, `sign`, commit,
`check`. No batch unit is moved to a terminal status by the test. The run is built once for the
class; each criterion reads it.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
sys.path.insert(0, str(HERE))
import gitutil  # noqa: E402

#: The batch as planned: the two units the sign seals, the bug carried at the cap and the story
#: the operator drops and forces.
STORY, BUG, CARRIED, DROPPED = "US0101", "BG0101", "BG0102", "US0102"
CLASS = "LC-900"
AUTHOR, REVIEWER = "Builder; agent; v1", "Reviewer; agent; v1"
TERMINAL = {"stories": "Done", "bugs": "Fixed"}


class _Run:
    """The throwaway project and every command the test runs against it, in order."""

    def __init__(self, d: str) -> None:
        self.root = Path(d) / "repo"
        self.transcripts = Path(d) / "transcripts"
        self.transcripts.mkdir()
        self.root.mkdir()
        self.env = {**gitutil.git_env(), "SDLC_STUDIO_TRANSCRIPTS": str(self.transcripts),
                    "PYTHONDONTWRITEBYTECODE": "1"}
        self.log: list[tuple[list[str], int, str]] = []
        #: Every `transition.py set` the test ran: (unit, status, forced).
        self.moves: list[tuple[str, str, bool]] = []

    # --- primitives --------------------------------------------------------------------------

    def spend(self, tokens: int) -> None:
        """One usage record on the session transcript: the meter grows by `tokens`."""
        with (self.transcripts / "session.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"message": {"model": "m", "usage": {
                "input_tokens": tokens, "output_tokens": 0}}}) + "\n")

    def cli(self, script: str, *argv: str, ok: bool = True, root_flag: bool = True) -> tuple:
        """`python3 <script>.py <argv> --root <root>` beside this test: (rc, stdout+stderr)."""
        cmd = [sys.executable, str(SCRIPTS / f"{script}.py"), *argv]
        if root_flag:
            cmd += ["--root", str(self.root)]
        res = subprocess.run(cmd, cwd=self.root, env=self.env, capture_output=True, text=True,
                             timeout=300)
        out = res.stdout + res.stderr
        self.log.append((cmd[1:], res.returncode, out))
        if ok and res.returncode != 0:
            raise AssertionError(f"{script} {' '.join(argv)} exited {res.returncode}:\n{out}")
        return res.returncode, out

    def git(self, *argv: str) -> str:
        res = subprocess.run(["git", "-C", str(self.root), *argv], env=self.env,
                             capture_output=True, text=True, check=True)
        return res.stdout

    def commit(self, message: str) -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "--allow-empty", "-m", message)

    def move(self, uid: str, status: str, *, force: bool = False) -> tuple:
        self.moves.append((uid, status, force))
        return self.cli("transition", "set", "--id", uid, "--status", status,
                        *(["--force"] if force else []), ok=False)

    def state(self) -> dict:
        return json.loads((self.root / "sdlc-studio" / ".local" / "run-state.json")
                          .read_text(encoding="utf-8"))

    def path(self, uid: str) -> Path:
        hits = [p for d in ("stories", "bugs", "change-requests")
                for p in (self.root / "sdlc-studio" / d).glob(f"{uid}-*.md")]
        assert len(hits) == 1, f"{uid}: {hits}"
        return hits[0]

    def field(self, uid: str, name: str) -> str:
        m = re.search(rf"^> \*\*{re.escape(name)}:\*\* (.*)$",
                      self.path(uid).read_text(encoding="utf-8"), re.M)
        return m.group(1).strip() if m else ""

    def reports(self) -> list[str]:
        return sorted(p.name for p in (self.root / "sdlc-studio" / "reports").glob("RPT*.json"))

    # --- the run -----------------------------------------------------------------------------

    def _unit(self, uid: str, status: str) -> None:
        folder = "bugs" if uid.startswith("BG") else "stories"
        d = self.root / "sdlc-studio" / folder
        d.mkdir(parents=True, exist_ok=True)
        head = "> **Severity:** Medium\n" if folder == "bugs" else "> **Epic:** EP0001\n"
        (d / f"{uid}-x.md").write_text(
            f"# {uid}: {uid.lower()} works\n\n> **Status:** {status}\n{head}> **Points:** 2\n"
            f"> **Affects:** src/{uid.lower()}.py\n\n## Acceptance Criteria\n\n"
            f"- [ ] **AC1** {uid} works\n  - **Verify:** shell true\n", encoding="utf-8")
        (self.root / "src").mkdir(exist_ok=True)
        (self.root / "src" / f"{uid.lower()}.py").write_text("x = 1\n", encoding="utf-8")

    def build(self) -> None:
        root = self.root
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "schema_version: 3\nreview:\n  require_brief_provenance: false\n", encoding="utf-8")
        (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
        for uid, status in ((STORY, "Ready"), (BUG, "Open"), (CARRIED, "Open"),
                            (DROPPED, "Ready")):
            self._unit(uid, status)
        (root / "sdlc-studio" / "lessons.jsonl").write_text(json.dumps({
            "id": CLASS, "class": "class 900", "rule": "Rule 900 holds.",
            "behaviour": "Behaviour 900 follows.", "inject": ["build"], "state": "active",
            "recorded_run": "RUN-0",
            "hits": [{"run": "RUN-1", "unit": "US0001", "source": "critic:RUN-1"},
                     {"run": "RUN-2", "unit": "US0002", "source": "critic:RUN-2"}]}) + "\n",
            encoding="utf-8")
        self.git("init", "-q")
        self.commit("base")
        self.spend(1000)
        # The run, opened as `sprint plan --write` leaves one: a baseline stamp and a base ref.
        subprocess.run([sys.executable, "-c", (
            "import sys; sys.path.insert(0, sys.argv[1]); from lib import run_state; "
            "run_state.open_run(sys.argv[2], batch=sys.argv[3].split(','), goal='done'); "
            "run_state.update(sys.argv[2], sprint_goal='Maya signs a page that checks VALID')"),
            str(SCRIPTS), str(root), ",".join((STORY, BUG, CARRIED, DROPPED))],
            env=self.env, check=True, capture_output=True, text=True)
        # The work: spans opened inside the run, each unit's own commit naming it.
        for uid in (STORY, BUG, CARRIED, DROPPED):
            self.move(uid, "In Progress")
        self.move(STORY, "Review")
        self.spend(5000)
        for uid in (STORY, BUG, CARRIED):
            (root / "src" / f"{uid.lower()}.py").write_text("x = 2\n", encoding="utf-8")
            self.cli("verify_ac", "run", "--id", uid)
            self.commit(f"fix({uid}): {uid.lower()} works")
        for uid in (STORY, BUG):
            self.cli("critic", "record", "--unit", uid, "--verdict", "approve",
                     "--reviewer", REVIEWER, "--author", AUTHOR)
        # The carry: rev-a rejects twice, the second at the cap carries the unit into a bug.
        for issues in ("[new] the widget drops a row", "[new] the widget still drops it"):
            self.cli("critic", "record", "--unit", CARRIED, "--verdict", "reject",
                     "--reviewer", "rev-a", "--author", AUTHOR, "--issues", issues)
        # The operator's interventions: a deferred decision resolved, a story dropped and forced.
        self.cli("sprint", "decision", "defer", "--unit", STORY, "--question",
                 "Ship US0101 this run?", "--option", "ship|it ships with the run",
                 "--option", "hold|it waits a run")
        self.cli("sprint", "decision", "resolve", "--index", "1", "--choice", "ship",
                 "--note", "the operator ships it")
        self.cli("sprint", "batch", "drop", DROPPED, "--reason", "the operator descoped it")
        self.forced = self.move(DROPPED, "Done", force=True)
        # The carry's own exit: its rejecting reviewer approves, and its gate moves it.
        self.discharge = self.cli("critic", "record", "--unit", CARRIED, "--verdict", "approve",
                                  "--reviewer", "rev-a", "--author", AUTHOR, ok=False)
        self.fixed = self.move(CARRIED, "Fixed")
        self.statuses_before_close = {u: self.field(u, "Status") for u in (STORY, BUG)}
        self.commit("the run's work and paperwork")
        # The close the operator runs bare: it scaffolds the retro and stops.
        self.bare_close = self.cli("sprint", "close", ok=False)
        self.reports_after_bare_close = self.reports()
        self.retro_id = sdlc_md_id(self.state().get("scaffolded_retro") or "")
        self.carry_bug = carried_bug(self.state(), CARRIED)
        retro = next((root / "sdlc-studio" / "retros").glob("RETRO*.md"))
        text = retro.read_text(encoding="utf-8")
        self.scaffold = text
        for slot, words in (("{{keep}}", "small units"), ("{{stop}}", "hand-filed tables"),
                            ("{{try}}", "name the mutant first")):
            text = text.replace(slot, words)
        retro.write_text(text.rstrip("\n") + "\n"
                         f"| {self.carry_bug} | not-stop-ship | Maya | 2026-10-01 |\n"
                         f"| {CLASS} | not-stop-ship | Maya | 2026-10-01 |\n", encoding="utf-8")
        self.commit("the retro")
        time.sleep(1)
        self.close = self.cli("sprint", "close", "--retro", self.retro_id, "--goal-verdict",
                              "achieved", "--note", "every unit landed", ok=False)
        self.report_id = self.state().get("report") or ""
        self.commit("close paperwork")
        self.spend(3000)
        self.sign = self.cli("sprint", "sign", "--report", self.report_id,
                             "--principal", "Maya", ok=False)
        self.commit("signed")
        self.check = self._check()

    def _check(self) -> tuple:
        """`sprint_report.py --root <root> check`: its `--root` precedes the verb."""
        cmd = [sys.executable, str(SCRIPTS / "sprint_report.py"), "--root", str(self.root),
               "check", "--report", self.report_id]
        res = subprocess.run(cmd, cwd=self.root, env=self.env, capture_output=True, text=True,
                             timeout=300)
        self.log.append((cmd[1:], res.returncode, res.stdout + res.stderr))
        return res.returncode, res.stdout + res.stderr

    def page(self) -> str:
        """The signed page's Markdown twin, as the signing commit holds it."""
        md = next((self.root / "sdlc-studio" / "reports").glob(f"{self.report_id}-*.md"))
        return md.read_text(encoding="utf-8")


def sdlc_md_id(value: str) -> str:
    return value.replace("-", "").upper()


def carried_bug(state: dict, unit: str) -> str:
    """The bug the run's carry of `unit` filed, from the batch drop that names it."""
    for c in state.get("batch_changes") or []:
        if c.get("id") == unit and str(c.get("reason", "")).startswith("carried at the review cap:"):
            return c["reason"].split(":", 1)[1].strip()
    return ""


class SignedRunEndToEndTests(unittest.TestCase):
    flow: _Run

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        cls.started = time.monotonic()
        cls.flow = _Run(cls._tmp.name)
        try:
            cls.flow.build()
        except Exception:
            cls._tmp.cleanup()
            raise
        cls.seconds = time.monotonic() - cls.started

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_close_sign_check_is_valid_first_time(self) -> None:
        """AC1. MUTANTS: BG0848 reverted (check INVALIDATED on the unit and run token rows); a
        flow that files a report at the bare close, or twice; a stubbed chain or seal, which
        this test cannot be, since every step is the shipped command line."""
        run = self.flow
        self.assertEqual([], run.reports_after_bare_close, "the bare close filed a report")
        self.assertIn("scaffolded", run.bare_close[1], run.bare_close[1])
        # The scaffold names the run, so a reader without --retro finds it, and carries the
        # table the rulings are written in (BG0826).
        self.assertIn(f"> **Run:** {run.state()['run_id']}", run.scaffold)
        self.assertRegex(run.scaffold, r"## Known issues carried\n\n\| id \| ruling \|")
        for name, (rc, out) in (("close", run.close), ("sign", run.sign), ("check", run.check)):
            self.assertEqual(0, rc, f"{name} exited {rc}:\n{out}")
        self.assertTrue(run.report_id, "the close recorded no report")
        self.assertRegex(run.check[1], rf"^VALID: {run.report_id} ", run.check[1])
        self.assertEqual([f"{run.report_id}.json"], run.reports(),
                         "not exactly one report, the one the sign sealed and the check read")
        self.assertIn(run.report_id, run.sign[1] + json.dumps(run.state().get("signature")))

    def test_the_carried_unit_ends_through_its_own_gate(self) -> None:
        """AC2. MUTANTS: BG0850 reverted (the discharge APPROVE refused at the cap, Fixed
        refused on the unanswered REJECT); a flow that reaches Fixed with --force; BG0859
        reverted, whose close tells the operator to move an approved bug by hand."""
        run = self.flow
        self.assertTrue(run.carry_bug, "premise: the unit was not carried at the cap")
        self.assertEqual(0, run.discharge[0], f"the discharge was refused:\n{run.discharge[1]}")
        self.assertEqual(0, run.fixed[0], f"Fixed was refused:\n{run.fixed[1]}")
        self.assertEqual("", run.field(CARRIED, "Forced-override"))
        self.assertIn((CARRIED, "Fixed", False), run.moves)
        # No batch unit the sign seals was moved toward its terminal status by the test...
        self.assertEqual({STORY: "Review", BUG: "In Progress"}, run.statuses_before_close)
        self.assertEqual([], [m for m in run.moves if m[0] in (STORY, BUG)
                              and m[1] in TERMINAL.values()])
        # ...nor did the close ask for one to be.
        self.assertNotRegex(run.close[1], r"\[status\] (?:US0101|BG0101)\b", run.close[1])
        # ...and after the sign every unit the batch held is terminal.
        for uid in (STORY, BUG, CARRIED, DROPPED):
            folder = "bugs" if uid.startswith("BG") else "stories"
            self.assertEqual(TERMINAL[folder], run.field(uid, "Status"), uid)

    def test_the_signed_page_names_every_ruling_carry_and_override(self) -> None:
        """AC3. MUTANTS: BG0851 reverted (no operator ruling, 'no gate stood down'); BG0849
        reverted (the graduation CR UNRULED); BG0826 reverted (no run id, no table: the bare
        close scaffolds a retro the rulings cannot be written in); BG0865 reverted (the page's
        Known issues rows carry no ruling, and the close's own CR is not listed)."""
        run = self.flow
        page = run.page()
        cr = json.loads((run.root / "sdlc-studio" / "lessons.jsonl").read_text(
            encoding="utf-8").splitlines()[0]).get("cr") or ""
        self.assertTrue(cr, "premise: the close graduated no lesson")
        self.assertNotIn("unruled", page.lower(), "the page hands over a finding nobody ruled")
        self.assertIn("the operator ruled 1 time(s)", page)
        self.assertNotIn("no gate stood down", page)
        self.assertRegex(page, rf"\*\*{DROPPED}\*\* - Forced-override: --force waived")
        self.assertRegex(page, rf"{CARRIED} .*carried at the review cap: {run.carry_bug}",
                         "the page does not name the carried unit with its bug")
        self.assertIn(cr, page, "the page does not name the graduation CR")
        # The retro's rulings themselves, each on its Known issues row of the page the operator
        # signs (BG0865): the carry's bug, and the graduation CR ruled by its lesson class.
        for finding in (sdlc_md_id(run.carry_bug), sdlc_md_id(cr)):
            self.assertRegex(page, rf"(?m)^\| {finding} \| [^|]+ \| .* - not-stop-ship, ruled by "
                                   rf"Maya \|$", f"{finding}'s ruling is not on the page")


if __name__ == "__main__":
    unittest.main()
