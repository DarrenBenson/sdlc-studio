"""Unit tests for tools/test_noise.py - the green-run noise detector (RED first).

The class these lock: a PASSING suite must say nothing. A diagnostic that escapes an
expected-failure fixture trains everyone to skim past `error`, which is the reflex that
lets a real one through. The shipped detector matched exactly one shape - `ERROR` or
`WARN` followed by an absolute path - and caught almost none of the 233 lines this repo's own suite
was leaking, because the real leaks are lowercase `error:`, `warning:`, `usage:` and
tool-prefixed messages.
"""
from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "test_noise.py"


def _load():
    spec = importlib.util.spec_from_file_location("test_noise", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["test_noise"] = mod
    spec.loader.exec_module(mod)
    return mod


tn = _load()

# Real lines this repo's suite printed during a fully green run.
OBSERVED_LEAKS = [
    "error: reviewer == author - independence is the floor; a self-review never clears",
    "command_audit: 1 broken tool(s) (--strict)",
    "warning: could not load .config.yaml (config loading needs PyYAML); using defaults",
    "sprint-review refused: reviewer 'bob' == author - a sprint-level self-review",
    "usage: python3 -m unittest record [-h] --unit UNIT",
    "issue #42 not found via gh for CR-0002; skipping",
    "gh issue create failed: denied",
    "failed to create issue for CR-0001",
    "ERROR   /tmp/x/sdlc-studio/bugs/BG0001-x.md: [evidence-present] bug has no evidence",
    "WARN    /tmp/x/sdlc-studio/bugs/BG0002-y.md: [pseudo-verify] line 36",
]

# Lines a unittest run legitimately prints. Flagging any of these would make the gate
# fire on every green run, which is how a guard gets switched off.
RUNNER_OUTPUT = [
    "....................",
    "..s..x..",
    "----------------------------------------------------------------------",
    "======================================================================",
    "Ran 3048 tests in 116.245s",
    "OK",
    "OK (skipped=1)",
    "FAILED (failures=2)",
    "",
    "FAIL: test_thing (tests.test_x.ThingTests.test_thing)",
    "ERROR: test_other (tests.test_x.OtherTests.test_other)",
    "Traceback (most recent call last):",
    '  File "/x/tests/test_x.py", line 12, in test_thing',
    "    self.assertEqual(1, 2)",
    "AssertionError: 1 != 2",
    "During handling of the above exception, another exception occurred:",
]


class NoiseShapeDetectorTests(unittest.TestCase):
    """AC2: the detector catches the leak shapes this suite actually produces."""

    def test_every_observed_leak_is_detected(self) -> None:
        missed = [l for l in OBSERVED_LEAKS if not tn.leaked_lines(l)]
        self.assertEqual(missed, [], f"{len(missed)} real leak shape(s) undetected")

    def test_no_runner_output_is_flagged(self) -> None:
        false = [l for l in RUNNER_OUTPUT if tn.leaked_lines(l)]
        self.assertEqual(false, [], f"{len(false)} legitimate runner line(s) flagged")

    def test_the_original_single_shape_still_matches(self) -> None:
        """The shape the shipped guard caught must not be lost while broadening."""
        self.assertTrue(tn.leaked_lines("ERROR   /tmp/x/a.md: [rule] message"))
        self.assertTrue(tn.leaked_lines("WARN    /tmp/x/a.md: [rule] message"))

    def test_a_multiline_block_returns_each_leak_once(self) -> None:
        text = "\n".join(["....", "error: boom", "OK", "warning: hmm", "Ran 3 tests in 0.1s"])
        self.assertEqual(tn.leaked_lines(text), ["error: boom", "warning: hmm"])

    def test_a_clean_run_returns_nothing(self) -> None:
        self.assertEqual(tn.leaked_lines("\n".join(RUNNER_OUTPUT)), [])

    def test_an_assertion_message_mentioning_error_is_not_a_leak(self) -> None:
        """A failure's own text is the runner reporting, not a tool leaking."""
        self.assertEqual(tn.leaked_lines("AssertionError: error: expected this"), [])

    def test_detection_is_anchored_not_substring(self) -> None:
        """A sentence merely containing the word must not fire, or the gate cries wolf."""
        self.assertEqual(tn.leaked_lines("the parser reports an error: this is prose"), [])


class RunnerExclusionCannotSwallowLeaksTests(unittest.TestCase):
    """The exclusion list is the dangerous half: anything it swallows is invisible for ever.

    The first version excluded `\\s.*` (ANY indented line) and `\\w*(?:Error|...)` where the
    `\\w*` matches empty. So indenting a leak, or capitalising it, disarmed the gate - the
    same shape as a vacuity gate any tool printing "N passed" could switch off. Two real
    leaks in this repo's own suite were invisible purely because they were indented.
    """

    DISARMED = [
        "  error: leaked at /tmp/x",                       # indented
        "\terror: leaked at /tmp/x",                       # tab-indented
        "Error: leaked at /tmp/x",                         # capitalised
        "ERROR: gh issue create failed",                   # upper-case
        "  warning: /tmp/x/LESSONS-SUMMARY.md does not exist",
        "capacity: this batch does not fit. Cut it, or raise the appetite deliberately",
    ]

    def test_indenting_or_capitalising_a_leak_does_not_hide_it(self) -> None:
        missed = [l for l in self.DISARMED if not tn.leaked_lines(l)]
        self.assertEqual(missed, [], f"{len(missed)} leak(s) disarmed by the exclusion list")

    def test_the_runner_s_own_failure_header_is_still_excluded(self) -> None:
        """`ERROR: test_x (a.b.C.test_x)` is unittest naming a test, not a tool leaking.
        Distinguished by SHAPE - name then a dotted path in brackets - not by the word."""
        self.assertEqual(tn.leaked_lines("ERROR: test_thing (tests.test_x.T.test_thing)"), [])
        self.assertEqual(tn.leaked_lines("FAIL: test_thing (tests.test_x.T.test_thing)"), [])

    def test_an_exception_repr_is_excluded_but_a_bare_Error_is_not(self) -> None:
        """`AssertionError:` is a Python repr. A bare `Error:` is nobody's exception."""
        self.assertEqual(tn.leaked_lines("AssertionError: 1 != 2"), [])
        self.assertEqual(tn.leaked_lines("ValueError: bad input"), [])
        self.assertTrue(tn.leaked_lines("Error: something a tool printed"))


class NoiseBaselineTests(unittest.TestCase):
    """The ratchet. This repo leaks 233 lines today; requiring zero before the gate can
    run at all would mean the gate never runs, which is the state it is in now. The
    baseline grandfathers the current count and fails on an INCREASE, so the debt is
    visible and cannot grow."""

    def test_a_count_at_the_baseline_passes(self) -> None:
        self.assertTrue(tn.within_baseline(233, 233))

    def test_a_count_below_the_baseline_passes(self) -> None:
        self.assertTrue(tn.within_baseline(200, 233))

    def test_a_count_above_the_baseline_fails(self) -> None:
        self.assertFalse(tn.within_baseline(284, 233))

    def test_no_baseline_means_zero_tolerated(self) -> None:
        """A project adopting the gate clean must not inherit a silent allowance."""
        self.assertFalse(tn.within_baseline(1, None))
        self.assertTrue(tn.within_baseline(0, None))

# ---- BG0644: the ratchet holds a selection to the SUM of its modules' budgets ----------------

REPO = Path(__file__).resolve().parents[2]
SKILL_TESTS = REPO / "tools" / "skill-tests.sh"


def _leaky_module(n_leaks: int) -> str:
    """A passing test module whose tests print `n_leaks` warning-shaped lines to stderr."""
    body = ["import sys, unittest", "", "", "class Leaky(unittest.TestCase):"]
    for i in range(max(n_leaks, 1)):
        body += [f"    def test_{i}(self):",
                 f"        {'sys.stderr.write(\"warning: fixture leak\\n\")' if i < n_leaks else 'pass'}",
                 ""]
    return "\n".join(body) + "\n"


def _git(cwd: Path, *args: str) -> None:
    import subprocess
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True,
                   env={**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null",
                        "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                        "GIT_COMMITTER_EMAIL": "t@t"})


class _BudgetFixture:
    """A throwaway skill tree with leaky test modules and a COMMITTED budget file in its own repo."""

    def __init__(self, leaks: dict[str, int], budget: dict[str, int]) -> None:
        import json, tempfile
        self.tmp = Path(tempfile.mkdtemp(prefix="noise_budget_"))
        self.skill = self.tmp / "skill"
        (self.skill / "tests").mkdir(parents=True)
        for mod, n in leaks.items():
            (self.skill / "tests" / f"{mod}.py").write_text(_leaky_module(n), encoding="utf-8")
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        _git(self.repo, "init", "-q", "-b", "main")
        self.budget = self.repo / "test-noise-baseline.json"
        self.budget.write_text(json.dumps(budget), encoding="utf-8")
        _git(self.repo, "add", "-A"); _git(self.repo, "commit", "-q", "-m", "budget")

    def run_script(self, *mods: str, budget_path=None):
        import subprocess
        env = {**os.environ, "TEST_NOISE_BUDGET_FILE": str(budget_path or self.budget)}
        return subprocess.run(["bash", str(SKILL_TESTS), str(self.skill), *mods],
                              capture_output=True, text=True, env=env, cwd=str(REPO), timeout=600)

    def cleanup(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)


class SelectionBudgetTests(unittest.TestCase):
    """BG0644 AC1-AC3, through `tools/skill-tests.sh` over a fixture suite."""

    def test_a_selection_over_its_summed_budget_refuses_through_the_script(self) -> None:
        """AC1. MUTANTS: (1) hold the selection to `_total` - today's absolute check in the new
        file's clothing (8 leaks under a total of 20 passes); (2) hold the selection to the
        LARGEST selected entry (the printed figure names 3, not 6); (3) print the count and
        budget without the leaked lines."""
        fx = _BudgetFixture({"test_a": 4, "test_b": 4}, {"_total": 20, "test_a": 3, "test_b": 3})
        try:
            r = fx.run_script("test_a.py", "test_b.py")
            out = r.stdout + r.stderr
            self.assertNotEqual(0, r.returncode, out)
            self.assertIn("summed budget of 6", out, out)
            self.assertIn("test_a=3", out); self.assertIn("test_b=3", out)
            self.assertIn("printed 8 diagnostic line(s)", out, out)
            # The script echoes the suite's own output BEFORE the noise report, so the leaked
            # line is asserted inside the report, not anywhere in the combined output.
            report = out.split("test-noise: a PASSING run printed", 1)[1]
            self.assertIn("warning: fixture leak", report, "the leaked lines were not listed in the report:\n" + out)
            self.assertIn("recorded in", report, "the refusal does not name the budget file:\n" + out)
        finally:
            fx.cleanup()

    def test_a_full_run_over_the_total_still_refuses(self) -> None:
        """AC2. MUTANT: apply no ceiling when no selection is given."""
        fx = _BudgetFixture({"test_a": 4, "test_b": 4}, {"_total": 5, "test_a": 9, "test_b": 9})
        try:
            r = fx.run_script()
            out = r.stdout + r.stderr
            self.assertNotEqual(0, r.returncode, out)
            self.assertIn("full-run total of 5", out, out)
        finally:
            fx.cleanup()

    def test_a_run_within_budget_passes_and_an_unrecorded_module_contributes_zero(self) -> None:
        """AC3. MUTANTS: (1) refuse whenever the count is above zero (the within-budget run dies);
        (2) default an unrecorded module's budget to the largest recorded entry (test_c, with 2
        leaks against a largest entry of 3, would pass). The within-budget count (4) sits strictly
        between the largest selected entry (3) and the sum (6), so AC1's largest-entry mutant also
        dies here on a VERDICT."""
        fx = _BudgetFixture({"test_a": 2, "test_b": 2, "test_c": 2},
                            {"_total": 20, "test_a": 3, "test_b": 3})
        try:
            ok = fx.run_script("test_a.py", "test_b.py")
            self.assertEqual(0, ok.returncode, ok.stdout + ok.stderr)
            self.assertIn("declared debt, not a new leak", ok.stdout + ok.stderr)
            alone = fx.run_script("test_c.py")
            out = alone.stdout + alone.stderr
            self.assertNotEqual(0, alone.returncode, out)
            self.assertIn("no entry, contributing zero: test_c", out, out)
        finally:
            fx.cleanup()


class BudgetShrinksOnlyTests(unittest.TestCase):
    """BG0644 AC4-AC5: `budget-check` against the committed file, and its callers."""

    def _check(self, path) -> tuple[int, str]:
        import subprocess
        r = subprocess.run([sys.executable, str(SCRIPT), "--budget-check", str(path)],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr

    def test_a_raised_or_new_module_budget_is_refused_and_a_shrink_is_accepted(self) -> None:
        """AC4. MUTANTS: (1) compare the committed and working sets of entry NAMES only (a raised
        count passes); (2) refuse every difference from the committed file (a lowered entry is
        refused too)."""
        import json
        fx = _BudgetFixture({"test_a": 1}, {"_total": 10, "test_a": 3, "test_b": 2})
        try:
            def write(d):
                fx.budget.write_text(json.dumps(d), encoding="utf-8")
            write({"_total": 10, "test_a": 4, "test_b": 2})
            rc, out = self._check(fx.budget); self.assertEqual(1, rc, out); self.assertIn("test_a raised 3 -> 4", out)
            write({"_total": 11, "test_a": 3, "test_b": 2})
            rc, out = self._check(fx.budget); self.assertEqual(1, rc, out); self.assertIn("_total raised 10 -> 11", out)
            write({"_total": 10, "test_a": 3, "test_b": 2, "test_c": 3})
            rc, out = self._check(fx.budget); self.assertEqual(1, rc, out); self.assertIn("new entry test_c=3", out)
            for accepted in ({"_total": 9, "test_a": 2, "test_b": 2},      # lowered
                             {"_total": 10, "test_a": 3},                   # vanished
                             {"_total": 10, "test_a": 3, "test_b": 2, "test_c": 0}):  # new at zero
                write(accepted)
                rc, out = self._check(fx.budget); self.assertEqual(0, rc, out)
            fresh = fx.tmp / "fresh"; fresh.mkdir(); _git(fresh, "init", "-q", "-b", "main")
            (fresh / "b.json").write_text(json.dumps({"_total": 1, "x": 1}), encoding="utf-8")
            rc, out = self._check(fresh / "b.json"); self.assertEqual(0, rc, "an introduced file was refused:\n" + out)
            bare = fx.tmp / "bare"; bare.mkdir()
            (bare / "b.json").write_text(json.dumps({"_total": 1}), encoding="utf-8")
            rc, out = self._check(bare / "b.json"); self.assertEqual(1, rc, out); self.assertIn("not inside a git work tree", out)
            # a committed version that is not a budget is refused by name, never read as absent
            corrupt = fx.tmp / "corrupt"; corrupt.mkdir(); _git(corrupt, "init", "-q", "-b", "main")
            (corrupt / "b.json").write_text("[1, 2]", encoding="utf-8")
            _git(corrupt, "add", "-A"); _git(corrupt, "commit", "-q", "-m", "bad")
            (corrupt / "b.json").write_text(json.dumps({"_total": 1}), encoding="utf-8")
            rc, out = self._check(corrupt / "b.json"); self.assertEqual(1, rc, out); self.assertIn("not a budget", out)
            (corrupt / "b.json").write_text("{not json", encoding="utf-8"); _git(corrupt, "add", "-A"); _git(corrupt, "commit", "-q", "-m", "worse")
            (corrupt / "b.json").write_text(json.dumps({"_total": 1}), encoding="utf-8")
            rc, out = self._check(corrupt / "b.json"); self.assertEqual(1, rc, out); self.assertIn("is not JSON", out)
            # a note key is allowed and ignored by the arithmetic
            write({"_note": "why", "_total": 10, "test_a": 3, "test_b": 2})
            rc, out = self._check(fx.budget); self.assertEqual(0, rc, out)
        finally:
            fx.cleanup()

    def test_the_script_and_this_tree_both_run_budget_check(self) -> None:
        """AC5. MUTANTS: (1) remove the `budget-check` invocation from the script; (2) move it after
        the suite (a `Ran N tests` line precedes the refusal); (3) fall back to the scalar when the
        budget file is unreadable (an absent path runs the suite instead of refusing)."""
        import json
        fx = _BudgetFixture({"test_a": 1}, {"_total": 10, "test_a": 3})
        try:
            fx.budget.write_text(json.dumps({"_total": 10, "test_a": 4}), encoding="utf-8")
            r = fx.run_script("test_a.py")
            out = r.stdout + r.stderr
            self.assertNotEqual(0, r.returncode, out)
            self.assertIn("test_a raised 3 -> 4", out, out)
            self.assertNotIn("Ran ", out, "the suite ran before the budget was checked:\n" + out)
            absent = fx.run_script("test_a.py", budget_path=fx.tmp / "no-such-budget.json")
            out = absent.stdout + absent.stderr
            self.assertNotEqual(0, absent.returncode, out)
            self.assertIn("cannot be read", out, out)
            rc, out = self._check(fx.tmp / "no-such-budget.json")
            self.assertEqual(2, rc, "an unreadable budget file must exit 2 by the tool's own contract:\n" + out)
            self.assertNotIn("Ran ", out, "an unreadable budget fell back to running the suite:\n" + out)
        finally:
            fx.cleanup()
        rc, out = self._check(REPO / "tools" / "test-noise-baseline.json")
        self.assertEqual(0, rc, "this tree's budget file has grown against HEAD:\n" + out)


if __name__ == "__main__":
    unittest.main()
