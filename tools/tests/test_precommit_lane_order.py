"""The pre-commit gate's lane ORDER and its short-circuit (US0268).

Two separate properties, and the second is the one that actually saves the time.

ORDER. The cheap guards must be invoked before the expensive unit suites. Measured
before the change: the suites ran at hook lines 117-136 and the markdown lanes at
142-164, so a one-line markdown error was reported only after ~132 seconds of tests.

SHORT-CIRCUIT. Ordering alone changes nothing, because `run()` records a failure and
returns 0 - the hook runs every lane and checks `fail` at the very end. Without a guard
on the expensive block, moving markdown earlier just reports it earlier and still pays
for the suites. The suites must therefore be skipped when a cheaper lane has already
failed, and that skip must be NAMED: this hook's standing rule is that a guard which
quietly does not run is indistinguishable from one that ran and passed.

MESSAGE FIRST (US0372). The expensive lanes since moved OUT of `pre-commit` altogether,
behind the commit-message check in `commit-msg`: git runs `pre-commit` before the message
exists, so no ordering inside one hook could ever put the message rules first. The order
is therefore pinned across the PAIR, and `MessageCheckOrderTests` holds it.

These tests read the shipped hooks, so a change to either has to come here first. What
they cannot show is that a lane ran at all - `tools/tests/test_message_first_gate.py`
executes the pair over a real `git commit` for that.
"""
# test-census-subject: .githooks/pre-commit
from __future__ import annotations

import re
import unittest
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GITHOOKS = REPO / ".githooks"
HOOK = GITHOOKS / "pre-commit"
MSG_HOOK = GITHOOKS / "commit-msg"


def _text(hook: Path = HOOK) -> str:
    return hook.read_text(encoding="utf-8")


def _line_matching(pattern: str, hook: Path) -> int:
    """1-indexed line of the first line matching `pattern` in `hook`."""
    for i, line in enumerate(_text(hook).splitlines(), 1):
        if re.search(pattern, line):
            return i
    raise AssertionError(f"no line matching {pattern!r} in {hook.name}")


def _lane_line(key: str, hook: Path = HOOK) -> int:
    """1-indexed line of the `run "<key>"` invocation."""
    return _line_matching(rf'^\s*run\s+"{re.escape(key)}"', hook)


def _lane_keys(hook: Path = HOOK) -> list[str]:
    return re.findall(r'^\s*run\s+"([^"]+)"', _text(hook), re.M)


#: Every lane each hook is expected to declare. This is the anti-loss guard: a reorder
#: that drops a lane would otherwise pass every ordering assertion below while silently
#: reducing coverage.
#: `gate` is a `run` lane since US0901, so `--list` names it like every other.
#: US0901 kept this list: it is the one hand record that fails when a lane is DROPPED, which
#: `--list` (derived from the hook) cannot, since it agrees with any hook. US0905's lane cap is
#: the candidate to replace it; until then adding a lane means a line here.
#:
#: HAND-MAINTAINED ON PURPOSE - do not "fix" this by deriving it from the hook. This list IS
#: the assertion: derived from the thing it checks, it would agree with any hook including one
#: that lost a lane, which is the exact failure it exists to catch. Every OTHER mirror of a
#: production list in this suite should be derived (see `hookutil.py`); this one is the
#: deliberate exception, and the guard below refuses a new hand-copied list so the distinction
#: stays a decision rather than a habit.
EXPECTED_LANES = {
    "style", "links", "skill-spec", "versions",
    "stamps-staged",
    # US0879 deleted runbook, lens-signatures, spec-claims and practice-rules: four lanes that
    # checked documents against documents and caught nothing.
    # BG0662: nothing opened a changelog fragment until the release cut, where compose refused
    # the whole fold; 59 of 119 had drifted past a green gate.
    "changelog-shape",
    # US0902 deleted script-tests: it held the TSD's prose map to the scripts tree.
    # US0896 deleted warning-ratchet: every entry it refused was a file deleted by design.
    # US0897 deleted verify-ratchet: it refused a bug sharing its fixing story's selector.
    "budgets",
    "neutrality",
    "action-pins", "dead-flags", "floor-pending", "gate", "markdown", "markdown-payload",
    # US0901: the handover refusal became a `run` lane so `--list` names it.
    "suite-handover",
}

#: The lanes that cost real wall-clock, and that therefore may not run until every cheap
#: refusal - including the commit-message rules - has had its chance.
#: `unit-tests` runs a selection in parallel; `skill-tests` and `tool-tests` are the unittest
#: path, taken with no selection or no pytest (US0880).
EXPENSIVE_LANES = {"unit-tests", "skill-tests", "tool-tests"}

#: Every lane `commit-msg` declares, on the same hand-maintained terms as EXPECTED_LANES above.
#: `repo-writes` is cheap and still lives here rather than in `pre-commit`, because what it
#: checks is what the SUITES did: it compares the tree against the snapshot `pre-commit` took
#: when it selected them, so it cannot run until they have.
MSG_HOOK_LANES = EXPENSIVE_LANES | {"repo-writes",
                                     # US0901: the message rule and the collapse check (BG0413)
                                     # became `run` lanes so `--list` names them.
                                     "message-refs", "suite-collapse"}


class LaneOrderTests(unittest.TestCase):
    def test_markdown_lanes_run_before_the_unit_suites(self) -> None:
        # Across the pair: the cheap lanes live in `pre-commit`, which git runs first in
        # its entirety, so every one of them precedes the suites in `commit-msg`.
        for cheap in ("markdown", "markdown-payload"):
            self.assertIn(cheap, _lane_keys(HOOK),
                          f'the "{cheap}" lane must stay in pre-commit, ahead of the suites - a '
                          "markdown error must not cost a full unit-suite run first")
        for suite in EXPENSIVE_LANES:
            self.assertIn(suite, _lane_keys(MSG_HOOK))

    def test_the_cheap_static_guards_all_precede_the_suites(self) -> None:
        for cheap in ("style", "links", "budgets", "neutrality", "versions", "floor-pending"):
            self.assertIn(cheap, _lane_keys(HOOK))
        self.assertEqual(EXPENSIVE_LANES & set(_lane_keys(HOOK)), set(),
                         "an expensive lane is back in pre-commit, which runs before the "
                         "commit message exists")

    def test_no_lane_is_lost_in_the_reorder(self) -> None:
        # A dropped lane is a silent coverage cut.
        self.assertEqual(set(_lane_keys(HOOK)), EXPECTED_LANES)
        self.assertEqual(set(_lane_keys(MSG_HOOK)), MSG_HOOK_LANES)

    def test_the_repo_writes_lane_runs_after_the_suites_it_judges(self) -> None:
        """It compares the tree against a snapshot taken before the suites ran, so a lane
        placed above them would report on a run that had not happened yet."""
        for suite in EXPENSIVE_LANES:
            self.assertLess(_lane_line(suite, MSG_HOOK), _lane_line("repo-writes", MSG_HOOK),
                            f"repo-writes runs before the {suite} lane it is meant to judge")

    def test_every_lane_key_is_unique(self) -> None:
        keys = _lane_keys(HOOK) + _lane_keys(MSG_HOOK)
        self.assertEqual(len(keys), len(set(keys)), f"a lane is invoked twice: {keys}")


class MessageCheckOrderTests(unittest.TestCase):
    """AC3: the order is pinned so it cannot silently revert.

    The saving is real only if the message verdict is reached before the first expensive
    lane AND the refusal leaves before them. Both are read from the shipped hooks here;
    `test_message_first_gate.py` proves the same two properties by execution.
    """

    def test_the_message_check_precedes_the_expensive_lanes(self) -> None:
        check = _line_matching(r"python3 .*check-commit-msg", MSG_HOOK)
        for lane in sorted(EXPENSIVE_LANES):
            self.assertLess(check, _lane_line(lane, MSG_HOOK),
                            f'the commit-message check must be invoked before "{lane}"')
        # The refusal has to LEAVE before them; reaching the verdict and then running the
        # suites anyway would report the defect early and still charge for it.
        refusal_exit = _line_matching(r"^\s*exit 1\b", MSG_HOOK)
        self.assertLess(check, refusal_exit)
        for lane in sorted(EXPENSIVE_LANES):
            self.assertLess(refusal_exit, _lane_line(lane, MSG_HOOK))
        # ...and they are gone from the hook git runs before the message exists.
        self.assertEqual(EXPENSIVE_LANES & set(_lane_keys(HOOK)), set())

    def test_the_timing_and_budget_recording_moved_with_the_suites(self) -> None:
        """The measurement has to wrap the lanes wherever they now run: a per-suite record, the
        scope judgement and the per-commit total after. US0880 removed the up-front estimate and
        the budget ratchet; the one budget report is pinned by test_lean_test_selection.py."""
        msg = _text(MSG_HOOK)
        for fragment in ("record --suite skill-tests", "record --suite tool-tests",
                         "gate_timing.py scope"):
            self.assertIn(fragment, msg, f"{fragment!r} did not move with the suites")
        # The per-commit TOTAL, asserted on the behaviour rather than one spelling. The suite
        # name is now a variable, because a selected run records into `total.selected` so its
        # partial count cannot erode the full-run peak the scope floor is judged against. A
        # literal `record --suite total` would have to be re-typed here every time that
        # decision moves, which turns this guard into a spelling test.
        self.assertRegex(msg, r'record --suite (total\b|"\$total_suite")',
                         "the per-commit total is no longer recorded after the suites")
        self.assertIn("total.selected", msg,
                      "a selected run has no separate series, so its partial count will drag "
                      "the peak down until the scope floor protects nothing")

    def test_the_message_hook_never_blocks_a_commit_on_its_own_timing(self) -> None:
        # Same rule the pre-commit lanes are held to: an advisory measurement that can fail
        # a commit is worse than no measurement.
        for line in _text(MSG_HOOK).splitlines():
            if "gate_timing.py" in line:
                self.assertIn("2>/dev/null", line, f"unguarded timing call: {line.strip()}")

    def test_pre_commit_hands_the_selection_over_rather_than_deciding_twice(self) -> None:
        """The selection rule stays in ONE place. `pre-commit` sees the staged index and
        decides; `commit-msg` obeys the record. A second copy of the grep in the message
        hook would be a rule that could drift against the one the skip message describes."""
        self.assertIn("test_relevant=", _text(HOOK))
        self.assertNotIn("test_relevant=", _text(MSG_HOOK))


class ShortCircuitTests(unittest.TestCase):
    """Ordering without a short-circuit saves nothing - `run` never exits."""

    def test_run_does_not_exit_so_a_guard_is_required(self) -> None:
        # Pins the premise. If `run` were ever changed to exit on failure, the guard
        # below would be redundant and this test says so rather than letting the two
        # mechanisms drift into contradicting each other.
        body = re.search(r"^run\(\)\s*\{(.*?)^\}", _text(), re.M | re.S)
        self.assertIsNotNone(body, "the hook must define run()")
        self.assertNotRegex(body.group(1), r"\bexit\b",
                            "run() does not exit; the expensive block needs its own guard")

    def test_the_unit_suites_are_guarded_by_the_accumulated_failure(self) -> None:
        # The suites must not run once a cheaper lane has already failed. Anchored on
        # `--name-` rather than on one spelling of the flag: this test is about the GUARD,
        # and pinning the flag made it fail when the staged list moved to --name-status for
        # a reason that has nothing to do with lane order.
        text = _text()
        guard = re.search(r'if \[ "\$fail" -eq 0 \].*?--suite-decision --staged', text, re.S)
        self.assertIsNotNone(
            guard,
            'the unit-suite block must be guarded by `[ "$fail" -eq 0 ]`, or a failing cheap '
            "lane still pays for the full suite - `run` records the failure and returns 0")

    def test_the_staged_list_carries_the_change_kind(self) -> None:
        # US0880: the selection reads the staged paths itself (`--suite-decision --staged`),
        # both sides of a rename, and the change kind no longer matters - the listing-only
        # narrowing that needed it is deleted.
        self.assertIn("--suite-decision --staged", _text(),
                      "the commit's selection is not taken from the staged paths")

    def test_the_short_circuit_skip_is_named(self) -> None:
        # A silent skip is indistinguishable from a lane that ran and passed.
        self.assertRegex(
            _text(), r"SKIP.*unit suites.*cheaper lane",
            "the short-circuit skip must SAY it skipped and why, like the docs-only skip does")


#: An ASSIGNMENT to `fail`, in every form the shell writes one IN PLACE. Anchored on the name
#: and the operator rather than on one literal: the check greped for `fail=1`, so
#: `fail=$(( fail + 1 ))` appended below the verdict write survived - door four left open by the
#: very test that pins the property (BG0523). The second branch is the arithmetic context, where
#: the name carries no `=` of its own: `(( fail++ ))` and `: $(( fail += 1 ))` both write `fail`
#: and both walked past the first branch.
#:
#: NOT every conceivable write. A shell can also set the variable through a command that names
#: it - `read fail`, `declare fail=`, `printf -v fail` - and those are out of scope here rather
#: than covered: the hook uses none of them, and a detector claiming a completeness it does not
#: have is the shape this repair is about. Extend both this pattern and the executed spellings
#: below together, or the new case turns the suite red on itself.
#:
#: The lookbehind keeps `skill_fail=` and `window_fail=` out; `$fail` has no `=` after the name
#: and so is never a match.
_FAIL_ASSIGNMENT = re.compile(r"(?<![\w])fail\+?=|\(\(\s*fail\s*(?:\+\+|--|[-+*/%]?=)")


def _fail_assignments_below_verdict(text: str) -> list[str]:
    """Every line below the suite-verdict write that can still set `fail`, comments excluded."""
    after = text[text.index("--record-suite-verdict"):]
    return [ln.strip() for ln in after.splitlines()
            if _FAIL_ASSIGNMENT.search(ln) and not ln.strip().startswith("#")]


class SuiteVerdictFailOpenTests(unittest.TestCase):
    """A green verdict must never be recorded beside a failing lane.

    The gate blocked a commit and passed the byte-identical retry, twice in one session. The
    verdict write ran unconditionally after `skill-tests`, so a FAILING lane still wrote
    `status green` - and the next attempt over an unchanged surface trusted it. A gate that
    fails intermittently trains an operator to retry rather than to read, which is what makes
    the third red - the real one - get discounted.
    """

    HOOK = Path(__file__).resolve().parents[2] / ".githooks" / "commit-msg"

    def test_the_green_verdict_is_guarded_by_the_lane_result(self) -> None:
        """MUTANT: remove the `if [ "$fail" -eq 0 ]` guard around the verdict write."""
        text = self.HOOK.read_text(encoding="utf-8")
        idx = text.index("--record-suite-verdict")
        # The guard must be the nearest enclosing condition, not merely present somewhere.
        preceding = text[:idx]
        self.assertIn('if [ "$fail" -eq 0 ]; then', preceding.rsplit("\n\n", 1)[-1],
                      "the green verdict is recorded without checking whether the lane passed")

    def test_the_green_verdict_is_written_below_both_suite_lanes(self) -> None:
        """MUTANT: move the verdict write back between the skill and tool lanes.

        Guarding the write on `$fail` is only half of it - PLACEMENT is the other half. Sitting
        between the lanes, `$fail` carried the skill lane's verdict alone, so a green skill lane
        beside a failing tool lane still wrote `status green`, and the byte-identical retry then
        reused it and ran no tests. That is the same fail-open the guard was added to close,
        reached through the other lane.

        Both existing criteria assert the hook's TEXT and are green on the misplaced version,
        which is why this asserts ORDER instead.
        """
        text = self.HOOK.read_text(encoding="utf-8")
        tool_lane = text.index('run "tool-tests"')
        verdict = text.index("--record-suite-verdict")
        self.assertGreater(
            verdict, tool_lane,
            "the green suite verdict is recorded before the tool-tests lane has run, so a "
            "failing tool lane still writes `status green` and the retry reuses it")

    def test_nothing_that_can_still_set_fail_sits_below_the_verdict_write(self) -> None:
        """MUTANT: append any `fail=1` assignment after the `--record-suite-verdict` block.

        The general rule, rather than the third instance of it. BG0423 wrote the verdict
        unconditionally, BG0489 wrote it between the lanes, BG0507 wrote it above the scope
        check - three findings, one shape: something could still set `fail` after the verdict
        was on disk, so a blocked commit left a reusable green behind.

        The executing tests pin the three doors that were actually found. This pins the
        PROPERTY, so door four fails here when it is written rather than when it is exploited -
        an enumeration of a rule is a lower bound, not a boundary (LL0043).

        The detector is anchored on an ASSIGNMENT to `fail`, not on the literal `fail=1`: one
        spelling is an enumeration of a rule too, and `fail=$(( fail + 1 ))` walked straight
        past it. Arithmetic-context writes - `(( fail++ ))`, `: $(( fail += 1 ))` - are matched
        as well; writes made through a command that NAMES the variable, such as `read fail`, are
        stated as out of scope beside the pattern rather than claimed.
        """
        offenders = _fail_assignments_below_verdict(self.HOOK.read_text(encoding="utf-8"))
        self.assertEqual(
            offenders, [],
            "these lines can still set `fail` AFTER the suite verdict has been written, so a "
            "commit they block leaves a reusable green verdict at that HEAD and the "
            f"byte-identical retry skips the suites: {offenders}. The verdict must be the LAST "
            "thing a passing hook does - move the write below them.")

    def test_the_property_check_catches_a_late_fail_however_it_is_spelled(self) -> None:
        """MUTANT: narrow the detector back to `"fail=1" in ln`.

        The property test greped one literal, so the mutant its own criterion names -
        appending an assignment below the verdict write - survived in every spelling but that
        one. Each spelling here is applied to a COPY of the shipped hook, so this is the
        criterion's mutant executed rather than a shape asserted about; the real hook is
        asserted clean beside them, without which the detector could simply return everything.

        The two arithmetic spellings were added with the pattern that catches them. A spelling
        added to this loop alone would redden the suite on its own new case, and one added to
        the pattern alone would go unexecuted - which is how the literal `fail=1` survived.
        """
        real = self.HOOK.read_text(encoding="utf-8")
        self.assertEqual(_fail_assignments_below_verdict(real), [],
                         "the shipped hook already carries a late assignment - the positive "
                         "control below would then prove nothing")
        for spelling in ('fail=$(( fail + 1 ))', 'fail=2', 'fail+=1',
                         '  [ -n "$x" ] && fail=1', 'export fail=1',
                         '(( fail++ ))', ': $(( fail += 1 ))'):
            with self.subTest(spelling=spelling):
                caught = _fail_assignments_below_verdict(f"{real}\n{spelling}\n")
                self.assertTrue(
                    caught,
                    f"{spelling!r} appended below the suite-verdict write was not reported, so "
                    f"a commit it blocks still leaves a reusable green verdict at that HEAD")
        # And the complement: a MENTION of the name below the write is not an assignment, or
        # the detector would refuse the hook's own `if [ "$fail" -ne 0 ]` exit branch.
        self.assertEqual(_fail_assignments_below_verdict(f'{real}\nprintf "$fail"\n'), [],
                         "reading `$fail` was reported as setting it")

    def test_a_failing_tool_lane_also_leaves_its_output_behind(self) -> None:
        """MUTANT: drop the tool lane's log capture.

        AC2's Given is "a commit blocked on a suite lane", and tool-tests is a suite lane. It
        left no log at all, so a commit blocked there had the same undiagnosable failure the
        criterion exists to prevent - the defect was narrowed to one lane, not fixed.
        """
        text = self.HOOK.read_text(encoding="utf-8")
        tool_lane = text.index('run "tool-tests"')
        after = text[tool_lane:]
        self.assertIn("gate-suite-last.log", after,
                      "a commit blocked on the tool-tests lane leaves no record of what failed")
        # Guarded on the tool lane's own failure, and only when the skill lane passed - its
        # log is already on disk and is the one worth keeping.
        idx = after.index("gate-suite-last.log")
        self.assertIn('if [ "$fail" -ne 0 ] && [ "${skill_fail:-0}" -eq 0 ]',
                      after[:idx].rsplit("\n\n", 1)[-1],
                      "the tool lane's log is written unconditionally, or overwrites the "
                      "skill lane's")

    def test_a_blocked_commit_leaves_its_suite_output_behind(self) -> None:
        """MUTANT: drop the tee.

        Neither of the two false reds was ever diagnosed, because the output lived only in the
        hook's console and the retry erased it. Evidence that does not survive the retry is not
        evidence.
        """
        text = self.HOOK.read_text(encoding="utf-8")
        self.assertIn("gate-suite-last.log", text,
                      "a blocked commit leaves no record of what failed")
        # Bounded to the SKILL lane's own capture. There are two now, one per lane, and a bare
        # `index()` fell through to the tool lane's copy when this one was deleted - whose
        # guard contains this guard as a substring, so the assertion passed while a commit
        # blocked on the skill lane left no log at all. A verifier its own sibling can satisfy
        # is not checking its own subject.
        skill_lane = text[:text.index('run "tool-tests"')]
        self.assertIn("gate-suite-last.log", skill_lane,
                      "a commit blocked on the skill-tests lane leaves no record of what failed")
        idx = skill_lane.index("gate-suite-last.log")
        self.assertIn('if [ "$fail" -ne 0 ]', skill_lane[:idx].rsplit("\n\n", 1)[-1],
                      "the log is written unconditionally rather than on a failure")




class PracticeRulesLaneTests(unittest.TestCase):
    """BG0493 wired `best_practice_rules.py` into a lane; US0879 deleted both, and the criteria
    pinning the lane are retired. The `run` helper test is general to every lane and stays."""

    REPO = Path(__file__).resolve().parents[2]
    HOOK = REPO / ".githooks" / "pre-commit"

    def test_the_hooks_run_helper_carries_a_lanes_failure(self) -> None:
        """MUTANT: discard the command's exit inside the hook's `run` helper.

        The other half of the criterion, and the half no assertion about the lane's argv can
        reach: a lane whose command refuses correctly still guards nothing if the helper that
        invokes it drops the exit. The hook's OWN definition is executed - extracted from the
        file, never retyped - against a command that fails and one that does not."""
        text = self.HOOK.read_text(encoding="utf-8")
        start = text.index("run() {")
        helper = text[start:text.index("\n}\n", start) + 3]
        outcomes = {}
        for name, cmd in (("failing", "false"), ("passing", "true")):
            script = f"{helper}\nfail=0\nrun 'x' 'what' 'fix' -- {cmd}\nexit $fail\n"
            outcomes[name] = subprocess.run(["bash", "-c", script], capture_output=True,
                                            text=True, check=False, timeout=60).returncode
        self.assertNotEqual(0, outcomes["failing"],
                            "the hook's run helper does not carry a lane's failure, so every "
                            "lane it invokes guards nothing")
        self.assertEqual(0, outcomes["passing"],
                         "the hook's run helper reports a failure for a command that succeeded")


def _load_gitutil():
    """The shipped git-fixture helper, which confines every fixture git call to the fixture.
    Loaded rather than re-implemented, so this module carries no second copy of its list."""
    import importlib.util
    import sys
    path = REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py"
    spec = importlib.util.spec_from_file_location("_lane_order_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()

GOOD_FRAGMENT = "<!-- section: Fixed -->\n- **A repair (BG0001).** Mended.\n"
BAD_FRAGMENT = "### Fixed\n- a heading where the marker belongs\n"


class ChangelogShapeLaneTests(unittest.TestCase):
    """Nothing opened a changelog fragment until the release cut, where compose refuses the
    WHOLE fold on the first bad one: 59 of 119 had drifted past a green gate. The lane judges
    each fragment on the commit that writes it.

    DRIVEN, not read: the lane's `run` block and the hook's `run` helper are both taken from
    `.githooks/pre-commit` and executed in throwaway git repositories, so a lane that is
    present, named and inert fails here whatever it is called."""

    KEY = "changelog-shape"
    SKILL = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"

    def _lane_block(self) -> str:
        """The lane's `run` block, from its `run "<key>"` line through its `--` command line."""
        lines = _text().splitlines()
        start = next((i for i, ln in enumerate(lines)
                      if re.match(rf'\s*run\s+"{re.escape(self.KEY)}"', ln)), None)
        self.assertIsNotNone(start, f'the hook has no `run "{self.KEY}"` lane')
        end = next(i for i in range(start, len(lines)) if lines[i].strip().startswith("-- "))
        return "\n".join(lines[start:end + 1])

    def _run_lane(self, repo: Path) -> tuple[int, str]:
        text = _text()
        start = text.index("run() {")
        helper = text[start:text.index("\n}\n", start) + 3]
        script = (f"{helper}\nR= G= Y= B= N=\nskill='{self.SKILL}'\nfail=0\n"
                  f"{self._lane_block()}\nexit $fail\n")
        r = subprocess.run(["bash", "-c", script], cwd=repo, capture_output=True, text=True,
                           check=False, timeout=120,
                           env=gitutil.git_env(PYTHONDONTWRITEBYTECODE="1"))
        return r.returncode, r.stdout + r.stderr

    def _repo(self, committed: dict | None = None) -> Path:
        """A throwaway git repository holding CHANGELOG.md and `committed` fragments."""
        root = Path(tempfile.mkdtemp(prefix="clshape_"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        gitutil.git(["init", "-q", "-b", "main"], cwd=root)
        (root / "changelog.d").mkdir()
        (root / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n\n",
                                           encoding="utf-8")
        for name, body in (committed or {}).items():
            (root / "changelog.d" / name).write_text(body, encoding="utf-8")
        gitutil.git(["add", "-A"], cwd=root)
        gitutil.git(["commit", "-q", "-m", "seed"], cwd=root)
        return root

    def _stage(self, root: Path, name: str, body: str) -> None:
        (root / "changelog.d").mkdir(exist_ok=True)   # `git rm` of every fragment removes it
        (root / "changelog.d" / name).write_text(body, encoding="utf-8")
        gitutil.git(["add", "--", f"changelog.d/{name}"], cwd=root)

    def test_the_lane_refuses_a_staged_malformed_fragment(self) -> None:
        """MUTANTS: an advisory `if` block that prints through `|| true` and never sets `fail`;
        the lane moved inside the suites-selected block; each staged fragment read from disk
        rather than from its index blob; the lane pointed at `changelog.py structure`.

        Two staged fragments are judged: a NEW one, and a TRACKED one committed well formed
        then edited into a bad shape, so a listing of added files alone misses the second."""
        root = self._repo({"BG0010.md": GOOD_FRAGMENT})
        self._stage(root, "BG0011.md", BAD_FRAGMENT)                 # added
        self._stage(root, "BG0010.md", "- a bare bullet, no marker\n")  # modified
        rc, out = self._run_lane(root)
        self.assertNotEqual(0, rc, f"the lane passed a staged malformed fragment:\n{out}")
        for name in ("BG0011.md", "BG0010.md"):
            self.assertIn(name, out, f"the lane did not name {name}:\n{out}")

        # Repaired on disk and NOT re-staged: the commit still records the bad bytes.
        for name in ("BG0011.md", "BG0010.md"):
            (root / "changelog.d" / name).write_text(GOOD_FRAGMENT, encoding="utf-8")
        rc, out = self._run_lane(root)
        self.assertNotEqual(0, rc, "the lane judged the working tree, not the staged blob, so "
                                   f"a bad blob repaired but left unstaged commits:\n{out}")
        for name in ("BG0011.md", "BG0010.md"):
            self.assertIn(name, out)

        # Top-level, and above the suite selection: every commit is judged, not only one that
        # stages a test-relevant file.
        lane = _lane_line(self.KEY)
        run_line = _text().splitlines()[lane - 1]
        self.assertTrue(run_line.startswith("run "),
                        f"the lane is nested inside a block rather than top-level:\n{run_line}")
        self.assertLess(lane, _line_matching(r"^\s*suites_needed=", HOOK),
                        "the lane runs after the suite selection, so a commit staging no "
                        "test-relevant file can skip it")

    def test_the_lane_passes_the_release_cut_a_well_formed_fragment_and_an_untracked_draft(
            self) -> None:
        """MUTANTS: drop `--diff-filter=d` from the staged listing (the release cut's staged
        deletions are then read, and refused); list the working tree's fragments rather than
        the staged names (the untracked draft then refuses the commit). Positive control in
        the SAME repositories: one malformed fragment staged as well fails the lane, naming
        only that fragment."""
        # 1. a well-formed fragment staged
        well = self._repo()
        self._stage(well, "BG0020.md", GOOD_FRAGMENT)
        # 2. the release cut's own commit: ONLY fragment deletions and a CHANGELOG.md edit.
        # One of the deleted fragments is malformed at HEAD, so a lane reading deletions from
        # any ref refuses it.
        cut = self._repo({"BG0030.md": GOOD_FRAGMENT, "BG0031.md": BAD_FRAGMENT})
        gitutil.git(["rm", "-q", "--", "changelog.d/BG0030.md", "changelog.d/BG0031.md"],
                    cwd=cut)
        (cut / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n\n## [9.9.9]\n\n"
                                          "### Fixed\n\n- folded\n", encoding="utf-8")
        gitutil.git(["add", "--", "CHANGELOG.md"], cwd=cut)
        staged = gitutil.git(["diff", "--cached", "--name-status"], cwd=cut,
                             text=True).stdout.split()
        self.assertEqual(staged, ["M", "CHANGELOG.md", "D", "changelog.d/BG0030.md",
                                  "D", "changelog.d/BG0031.md"])
        # 3. a well-formed fragment staged beside an UNTRACKED malformed draft
        draft = self._repo()
        self._stage(draft, "BG0040.md", GOOD_FRAGMENT)
        (draft / "changelog.d" / "BG0041.md").write_text(BAD_FRAGMENT, encoding="utf-8")

        states = {"well-formed": (well, ["BG0020"]),
                  "release cut": (cut, ["BG0030", "BG0031"]),
                  "untracked draft": (draft, ["BG0040", "BG0041"])}
        for state, (root, others) in states.items():
            with self.subTest(state=state):
                rc, out = self._run_lane(root)
                self.assertEqual(0, rc, f"the lane refused the {state} commit:\n{out}")
        for state, (root, others) in states.items():
            with self.subTest(state=state, control="malformed staged as well"):
                self._stage(root, "BG0099.md", BAD_FRAGMENT)
                rc, out = self._run_lane(root)
                self.assertNotEqual(0, rc, f"the lane passed a staged malformed fragment in "
                                           f"the {state} repository, so it is dead:\n{out}")
                self.assertIn("BG0099.md", out)
                for other in others:
                    self.assertNotIn(other, out,
                                     f"the lane named {other}, which this commit does not "
                                     f"record as a fragment:\n{out}")


if __name__ == "__main__":
    unittest.main()
