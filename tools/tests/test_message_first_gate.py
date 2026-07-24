"""The commit-message rules are checked before the expensive test lanes (US0372).

The measured problem: the gate costs ~205s when scripts are staged, and a one-line
commit-message defect was refused only AFTER all of it had run - then paid for again on
the retry. Two full suite runs for a fault knowable in milliseconds, which is what teaches
an agent to reach for `--no-verify`.

Why the fix is a RESTRUCTURE and not a reorder. Git runs `pre-commit` BEFORE the commit
message exists: at that moment `$GIT_DIR/COMMIT_EDITMSG` is absent (first commit) or still
holds the PREVIOUS commit's message. Verified directly, and `test_precommit_floor_pending`
records the same fact for the engagement floor. So there is no order of lanes inside
`pre-commit` that can check the message. The expensive lanes therefore move OUT of
`pre-commit` and sit behind the message check in `commit-msg`, with the timing, scope and
budget recording moving with them. `pre-commit` still decides whether they are selected,
and hands that decision over in a one-shot record inside the git directory.

These tests RUN THE REAL HOOK PAIR over `git commit` in a throwaway repo. They assert what
EXECUTED - a lane log the stubs append to, and the verdict lines the hooks print - never
what the scripts say about themselves. A test that read the hook source could be satisfied
by a hook that never runs.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PRE_COMMIT = REPO / ".githooks" / "pre-commit"
COMMIT_MSG = REPO / ".githooks" / "commit-msg"
SKILL_SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

#: See tools/tests/test_skill_tests_env.py - every fixture module that shells out to git
#: carries this list, and that module holds them all to one definition.
_GIT_ENV_VARS = (
    "GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_INDEX_VERSION",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES", "GIT_DISCOVERY_ACROSS_FILESYSTEM", "GIT_PREFIX",
)

#: Every lane the hook PAIR is expected to execute for a code commit, each exactly once.
#: This is the anti-loss and anti-duplication guard of AC2: the move must neither drop a
#: check nor run one twice. `gate` is an inline if/else block rather than a `run "..."`
#: lane, and it prints the same verdict line, so it counts here too.
EXPECTED_LANES = (
    "style", "links", "skill-spec", "versions", "budgets", "neutrality", "action-pins",
    "floor-pending", "gate", "markdown", "markdown-payload", "skill-tests", "tool-tests",
)

#: The hooks' verdict lines: `  ok   <key>` / `  FAIL <key>` (no colour when captured).
_VERDICT = re.compile(r"^ {2}(ok|FAIL)\s+(\S+)", re.M)

PASS_PY = "import sys\nsys.exit(0)\n"

#: The skill scripts each fixture needs, prepared ONCE for the module and symlinked in
#: rather than copied per test. This lane is itself paid for on every commit - a fixture
#: that copied ~50 files fifteen times added measurable seconds to the gate this story
#: exists to make cheaper.
_SCRIPTS_TEMPLATE: Path | None = None


def _scripts_template() -> Path:
    """The real skill scripts, minus their own test tree, with `gate.py` stubbed.

    `engagement_floor.py` must be the shipped one - it decides the message verdict, so a
    stub would make every refusal test vacuous. Only `gate.py` is replaced: this fixture is
    not a whole project, and a gate lane failing on a missing index would refuse every
    commit here for a reason nothing under test caused.
    """
    global _SCRIPTS_TEMPLATE
    if _SCRIPTS_TEMPLATE is None:
        holder = tempfile.mkdtemp(prefix="us0372-scripts-")
        dest = Path(holder) / "scripts"
        shutil.copytree(SKILL_SCRIPTS, dest,
                        ignore=shutil.ignore_patterns("tests", "__pycache__"))
        (dest / "gate.py").write_text(PASS_PY, encoding="utf-8")
        _SCRIPTS_TEMPLATE = dest
    return _SCRIPTS_TEMPLATE


def tearDownModule() -> None:
    if _SCRIPTS_TEMPLATE is not None:
        shutil.rmtree(_SCRIPTS_TEMPLATE.parent, ignore_errors=True)


def _clean_env() -> dict:
    env = dict(os.environ)
    for var in _GIT_ENV_VARS:
        env.pop(var, None)
    return env


def _git(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cwd), *args],
                          capture_output=True, text=True, env=_clean_env())


def _lanes(out: str) -> list[str]:
    """The lane keys that actually reported a verdict, in the order they reported it."""
    return [m.group(2) for m in _VERDICT.finditer(out)]


def _failed_lanes(out: str) -> list[str]:
    return [m.group(2) for m in _VERDICT.finditer(out) if m.group(1) == "FAIL"]


class _GateFixture(unittest.TestCase):
    """A throwaway repo carrying BOTH real hooks and the real message checker.

    Every cheap guard is stubbed to pass so the hook reaches `fail=0` and the branch under
    test is the one that runs. The two expensive lanes are stubbed too, but each APPENDS
    ITS NAME to a lane log, which is how these tests observe execution rather than infer
    it. `engagement_floor.py` is the real script - it is what refuses the message, so
    stubbing it would make every refusal test vacuous.
    """

    #: Wall-clock the suite stub deliberately burns, so a run that paid for it is
    #: distinguishable from one that did not. Zero by default: this lane is itself part of
    #: the gate, and only the tests that MEASURE the saving need to pay for it.
    SUITE_COST_SECONDS = 0

    #: Wall-clock deliberately spent in the FIRST hook. Zero unless a test needs the two
    #: halves of the gate to be told apart by duration - see BudgetAcrossThePairTests.
    CHEAP_COST_SECONDS = 0

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._build(Path(self._tmp.name))
        self.lane_log = self.root / "lane-log"

    def _build(self, tmp: Path) -> Path:
        root = tmp / "r"
        for rel in ("tools/tests", ".githooks", "node_modules/.bin",
                    "sdlc-studio/.local", "sdlc-studio/bugs", "sdlc-studio/stories"):
            (root / rel).mkdir(parents=True, exist_ok=True)
        lane_log = root / "lane-log"

        for name in ("pre-commit", "commit-msg"):
            dest = root / ".githooks" / name
            dest.write_text((REPO / ".githooks" / name).read_text(encoding="utf-8"),
                            encoding="utf-8")
            dest.chmod(0o755)

        pass_sh = "#!/usr/bin/env bash\nexit 0\n"
        for name in ("lint-style.sh", "check_action_pins.sh"):
            p = root / "tools" / name
            p.write_text(pass_sh, encoding="utf-8")
            p.chmod(0o755)
        if self.CHEAP_COST_SECONDS:
            style = root / "tools" / "lint-style.sh"
            style.write_text(f"#!/usr/bin/env bash\nsleep {self.CHEAP_COST_SECONDS}\nexit 0\n",
                             encoding="utf-8")
            style.chmod(0o755)
        for name in ("check_links.py", "validate_skill.py", "check_versions.py",
                     "check_budgets.py", "check_neutrality.py"):
            (root / "tools" / name).write_text(PASS_PY, encoding="utf-8")

        # The skill-tests lane: costly, and it says it ran. `Ran N tests` is the line the
        # hook parses for the scope check, so the stub has to speak the real dialect.
        skill_tests = root / "tools" / "skill-tests.sh"
        skill_tests.write_text(
            "#!/usr/bin/env bash\n"
            f"echo skill-tests >> {lane_log}\n"
            + (f"sleep {self.SUITE_COST_SECONDS}\n" if self.SUITE_COST_SECONDS else "")
            + "echo 'Ran 12 tests in 1.000s'\necho OK\nexit 0\n", encoding="utf-8")
        skill_tests.chmod(0o755)

        (root / "tools" / "gate_timing.py").write_text(
            (REPO / "tools" / "gate_timing.py").read_text(encoding="utf-8"), encoding="utf-8")

        # The tool-tests lane: a real `unittest discover` over one stub module that records
        # its own execution at import time.
        (root / "tools" / "tests" / "__init__.py").write_text("", encoding="utf-8")
        (root / "tools" / "tests" / "test_stub.py").write_text(
            "import unittest\n"
            f"open({str(lane_log)!r}, 'a').write('tool-tests\\n')\n\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n        self.assertTrue(True)\n", encoding="utf-8")

        md = root / "node_modules" / ".bin" / "markdownlint"
        md.write_text(pass_sh, encoding="utf-8")
        md.chmod(0o755)

        dest = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(_scripts_template(), target_is_directory=True)

        (root / "sdlc-studio" / ".config.yaml").write_text(
            "gate_budget:\n  seconds: 120\n  baseline_seconds: 99\n"
            "  baseline_date: 2026-07-21\n", encoding="utf-8")

        _git(root, "init", "-q")
        _git(root, "config", "user.email", "t@t")
        _git(root, "config", "user.name", "t")
        # The scaffolding lands in a first commit that bypasses the hooks, so a later
        # `git add -A` stages only what the test itself wrote.
        _git(root, "add", "-A")
        _git(root, "commit", "-q", "--no-verify", "-m", "fixture")
        _git(root, "config", "core.hooksPath", ".githooks")
        return root

    def _stage_code(self, name: str = "thing.py", body: str = "x = 1\n") -> None:
        """Stage a test-relevant change - the case that selects the expensive lanes."""
        (self.root / "tools" / name).write_text(body, encoding="utf-8")
        _git(self.root, "add", "-A")

    def _commit(self, message: str) -> tuple[int, str, float]:
        t0 = time.monotonic()
        out = subprocess.run(["git", "-C", str(self.root), "commit", "-m", message],
                             capture_output=True, text=True, env=_clean_env())
        return out.returncode, out.stdout + out.stderr, time.monotonic() - t0

    def _subjects(self) -> list[str]:
        return _git(self.root, "log", "--format=%s").stdout.split()

    def _ran(self) -> list[str]:
        if not self.lane_log.exists():
            return []
        return self.lane_log.read_text(encoding="utf-8").split()


class MessageBeforeSuitesTests(_GateFixture):

    #: The saving is a wall-clock claim, so the suites have to cost wall-clock here.
    SUITE_COST_SECONDS = 1

    def test_a_refused_message_never_reaches_the_unit_suites(self) -> None:
        """AC1. A subject naming two ids with no `Refs:` trailer, over a staged change that
        DOES select the suites: refused, with the same message and paste-ready trailers as
        before, and neither expensive lane executed.

        The second half is the control that stops this passing vacuously: the identical
        staged change with the trailers added runs both lanes and commits. Without it, a
        hook that had simply lost the suites would satisfy the first half.
        """
        self._stage_code()

        rc, refused_out, refused_secs = self._commit("feat(CR0257, CR0258): batch fix")

        self.assertNotEqual(rc, 0, f"the message defect did not refuse the commit:\n{refused_out}")
        self.assertEqual(self._subjects(), ["fixture"], "the refused commit LANDED")
        # The refusal is unchanged: same reason, same paste-ready trailers, same one escape.
        self.assertIn("Refs: CR0257", refused_out)
        self.assertIn("Refs: CR0258", refused_out)
        self.assertIn("--no-verify", refused_out)
        # ...and it cost neither expensive lane. Observed from what the lanes RECORDED, and
        # cross-checked against the verdict lines the hooks printed.
        self.assertEqual(self._ran(), [],
                         "an expensive lane executed for a message that was going to be refused")
        for lane in ("skill-tests", "tool-tests"):
            self.assertNotIn(lane, _lanes(refused_out))

        # The control: same staged change, a message the rules accept.
        rc, ok_out, ok_secs = self._commit(
            "feat(CR0257, CR0258): batch fix\n\nRefs: CR0257\nRefs: CR0258\n")
        self.assertEqual(rc, 0, ok_out)
        self.assertEqual(sorted(self._ran()), ["skill-tests", "tool-tests"],
                         f"the accepted commit did not run the suites:\n{ok_out}")
        # The saving, measured rather than asserted from the source: the refusal is cheaper
        # than the accepted run by at least the cost of the suites it did not pay for.
        self.assertLess(refused_secs, ok_secs - self.SUITE_COST_SECONDS / 2,
                        f"the refusal cost {refused_secs:.2f}s against {ok_secs:.2f}s for the "
                        "full run - it did not skip the expensive lanes")

    def test_a_docs_only_commit_still_skips_the_suites_and_says_so(self) -> None:
        """The selection rule survives the move: a commit touching no scripts/, templates/
        or tools/ file pays for no suite, and the skip is NAMED rather than silent."""
        (self.root / "README.md").write_text("x\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        rc, out, _ = self._commit("docs: tidy the README")
        self.assertEqual(rc, 0, out)
        self.assertIn("no test-relevant file staged", out)
        self.assertEqual(self._ran(), [], "a docs-only commit paid for the unit suites")

    def test_a_cheap_lane_failure_still_skips_the_suites_and_says_so(self) -> None:
        """The other short-circuit survives the move: a cheaper lane already blocked the
        commit, so the expensive lanes are not paid for at all."""
        style = self.root / "tools" / "lint-style.sh"
        style.write_text("#!/usr/bin/env bash\necho 'stub failure'\nexit 1\n", encoding="utf-8")
        style.chmod(0o755)
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertNotEqual(rc, 0, out)
        self.assertIn("a cheaper lane already failed", out)
        self.assertEqual(self._ran(), [])


class LaneInventoryTests(_GateFixture):

    def test_every_lane_runs_exactly_once_across_the_hook_pair(self) -> None:
        """AC2. The move adds no refusal and removes no check: for a green code commit,
        every lane that ran before it reports a verdict, each exactly once, across the two
        hooks together. Counted from what was printed, so a lane that were declared but
        never invoked - or invoked twice, once in each hook - fails here."""
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertEqual(rc, 0, f"a clean commit was refused:\n{out}")
        self.assertEqual(Counter(_lanes(out)), Counter(EXPECTED_LANES),
                         f"the lane inventory changed:\n{out}")
        self.assertEqual(_failed_lanes(out), [])
        self.assertEqual(sorted(self._ran()), ["skill-tests", "tool-tests"])

    def test_a_failing_expensive_lane_still_blocks_the_commit(self) -> None:
        """The move must not turn a blocking lane into an advisory one. A red suite in its
        new home refuses the commit exactly as it did in its old one."""
        red = self.root / "tools" / "tests" / "test_red.py"
        red.write_text("import unittest\n\n\nclass T(unittest.TestCase):\n"
                       "    def test_red(self):\n        self.fail('deliberate')\n",
                       encoding="utf-8")
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertNotEqual(rc, 0, f"a red suite did not block the commit:\n{out}")
        self.assertIn("tool-tests", _failed_lanes(out))
        self.assertEqual(self._subjects(), ["fixture"], "the commit landed with a red suite")

    def test_the_expensive_lanes_are_paid_for_once_not_once_per_hook(self) -> None:
        """The duplication half of AC2, from the lane log rather than the printed verdicts:
        a lane left behind in `pre-commit` as well as added to `commit-msg` would print two
        verdicts AND execute twice. Both are checked, because a lane could be invoked twice
        under one printed key."""
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertEqual(rc, 0, out)
        self.assertEqual(Counter(self._ran()),
                         Counter({"skill-tests": 1, "tool-tests": 1}),
                         "an expensive lane executed more than once")

    def test_the_declared_lanes_and_the_executed_lanes_agree(self) -> None:
        """Closes the loop between the static inventory AC3 pins and the executed one above:
        without this, both could drift together to a smaller set and stay green."""
        declared = set()
        for hook in (PRE_COMMIT, COMMIT_MSG):
            declared |= set(re.findall(r'^\s*run\s+"([^"]+)"', hook.read_text(encoding="utf-8"),
                                       re.M))
        declared.add("gate")      # an inline if/else block, not a `run "..."` lane
        self.assertEqual(declared, set(EXPECTED_LANES))


class HandoffTests(_GateFixture):
    """The record `pre-commit` leaves for `commit-msg`.

    It lives in the git directory (never the working tree, and never shared between
    worktrees), and it is ONE-SHOT: read and removed before the suites run. A record that
    outlived its commit would make the next `git merge` - which runs `commit-msg` but not
    `pre-commit` - pay for a suite run nobody asked for.
    """

    def _handoff(self) -> Path:
        return self.root / ".git" / "sdlc-gate-suites"

    def test_the_record_does_not_survive_the_commit_it_was_written_for(self) -> None:
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertEqual(rc, 0, out)
        self.assertFalse(self._handoff().exists(),
                         "the suite handoff outlived its commit; the next commit-msg-only "
                         "operation would run the suites unasked")

    def test_a_stale_record_does_not_make_a_docs_only_commit_pay(self) -> None:
        """The failure the one-shot rule exists to prevent, forced directly: a record left
        on disk by an abandoned commit must not select the suites for the next one. The
        docs-only commit below re-writes the decision, so the stale record cannot win."""
        self._handoff().write_text("precommit_seconds=5\n", encoding="utf-8")
        (self.root / "README.md").write_text("x\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        rc, out, _ = self._commit("docs: tidy the README")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self._ran(), [], "a stale handoff made a docs-only commit pay")
        self.assertFalse(self._handoff().exists())

    def test_a_commit_nested_inside_a_running_gate_still_runs_its_own_suites(self) -> None:
        """Found by running the restructured pair end to end, not by reading it.

        The first version of the handover carried an exported re-entry latch as well as the
        record. The tool-tests lane runs this repo's own hook fixtures, each of which makes
        a real commit in its own throwaway repo - and every one of them inherited the latch
        from the gate run that had invoked them, so each fixture commit silently ran only
        its cheap half and the tests that assert on the finished gate went red.

        Selection belongs to the repository being committed to, never to the process tree.
        Anything in the environment is inherited; the record is not.
        """
        self._stage_code()
        env = _clean_env()
        for latch in ("SDLC_GATE_SUITES_RUNNING", "SDLC_GATE_SUITES", "SDLC_GATE_RUNNING"):
            env[latch] = "1"
        out = subprocess.run(["git", "-C", str(self.root), "commit", "-m", "chore: touch a tool"],
                             capture_output=True, text=True, env=env)
        combined = out.stdout + out.stderr
        self.assertEqual(out.returncode, 0, combined)
        self.assertEqual(sorted(self._ran()), ["skill-tests", "tool-tests"],
                         f"an inherited environment variable suppressed the suites:\n{combined}")

    def test_a_handover_that_cannot_be_written_refuses_rather_than_passing_quietly(self) -> None:
        """The expensive lanes are now reachable only through the record, so a record that
        cannot be written means they do not run at all. That must be a refusal, not a warm
        green: an unrunnable guard inside an otherwise passing gate is indistinguishable
        from one that ran and passed, which is the state every named skip in this hook
        exists to prevent.

        Forced by putting a DIRECTORY where the record goes, so the redirect fails for a
        reason the hook cannot talk itself out of.
        """
        self._handoff().mkdir(parents=True, exist_ok=True)
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertNotEqual(rc, 0, f"an unwritable handover passed the gate:\n{out}")
        self.assertIn("suite-handover", out)
        self.assertEqual(self._ran(), [])
        self.assertEqual(self._subjects(), ["fixture"], "the commit landed with no suites run")

    def test_the_record_stays_out_of_the_working_tree(self) -> None:
        """It must never show up as an untracked file: a gate that dirties the tree it is
        gating trains people to `git add -A` past it."""
        self._stage_code()
        self._commit("chore: touch a tool")
        untracked = _git(self.root, "status", "--porcelain").stdout
        self.assertNotIn("sdlc-gate-suites", untracked, untracked)


class BudgetAcrossThePairTests(_GateFixture):
    """The timing and budget recording moved WITH the suites, and still measures the whole
    gate rather than only the half that now runs last."""

    def _totals(self) -> list[float]:
        import json
        p = self.root / "sdlc-studio" / ".local" / "gate-timings.json"
        return json.loads(p.read_text(encoding="utf-8")).get("total", []) if p.exists() else []

    def test_a_commit_that_ran_the_suites_is_recorded_against_the_budget(self) -> None:
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertEqual(rc, 0, out)
        self.assertEqual(len(self._totals()), 1, f"the full-lane commit was not recorded:\n{out}")
        self.assertIn("gate-budget:", out)
        self.assertIn("baseline 99s", out)

    def test_a_docs_only_commit_still_enters_no_series(self) -> None:
        (self.root / "README.md").write_text("x\n", encoding="utf-8")
        _git(self.root, "add", "-A")
        rc, out, _ = self._commit("docs: tidy the README")
        self.assertEqual(rc, 0, out)
        self.assertEqual(self._totals(), [], "a docs-only commit was recorded as a gate cost")
        self.assertNotIn("gate-budget:", out)


class TotalSpansBothHooksTests(BudgetAcrossThePairTests):
    """The one property that needs the two halves of the gate to be told apart by duration.

    It sits in its own class because the wall-clock below is paid on every commit through
    this gate, and only this test needs it.
    """

    #: Spent in `pre-commit`, so a total that covered only `commit-msg` is arithmetically
    #: distinguishable from one that covered both. Without it, dropping the first hook's
    #: share from the sum would change the recorded number and no assertion would notice.
    CHEAP_COST_SECONDS = 3

    def test_a_commit_that_ran_the_suites_is_recorded_against_the_budget(self) -> None:
        self.skipTest("covered by BudgetAcrossThePairTests without the wall-clock cost")

    def test_a_docs_only_commit_still_enters_no_series(self) -> None:
        self.skipTest("covered by BudgetAcrossThePairTests without the wall-clock cost")

    def test_the_recorded_total_covers_both_hooks_not_just_the_second(self) -> None:
        """`$SECONDS` used to span the whole gate in one process. It now spans two, so the
        recorded total has to be the SUM - otherwise the budget silently starts measuring
        only the suites, and the ratchet it exists to expose goes invisible."""
        self._stage_code()
        rc, out, _ = self._commit("chore: touch a tool")
        self.assertEqual(rc, 0, out)
        total = self._totals()[-1]
        # The pre-commit half of this fixture costs CHEAP_COST_SECONDS that the commit-msg
        # half never sees. A total recorded from the second hook's clock alone could not
        # reach this number.
        self.assertGreaterEqual(
            total, self.CHEAP_COST_SECONDS - 1,
            f"the recorded total ({total}s) is too small to include pre-commit's share - "
            "the budget series has silently started measuring only the second hook")


if __name__ == "__main__":
    unittest.main()
