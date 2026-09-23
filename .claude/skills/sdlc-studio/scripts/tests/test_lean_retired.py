"""US0886: the criteria Sprint 1 superseded (D0259) are retired, and their stub tests deleted.

Both tests read THIS repository, as the criteria name it: the artefacts D0259 lists and the test
modules their selectors used to point at. The first drives `verify_ac.py run --dry-run`, the
shipped entry point, over those units.
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

verify_ac = loader.load_script("verify_ac")

# parents: [0] tests [1] scripts [2] sdlc-studio [3] skills [4] .claude [5] repo root.
_REPO = Path(__file__).resolve().parents[5]
_TESTS = Path(__file__).resolve().parent

#: D0259, criterion by criterion: unit -> {criterion: what superseded it}.
_RETIRED = {
    "US0351": {"AC2": "US0876"},
    "US0435": {"AC1": "US0876", "AC2": "US0876", "AC3": "US0876"},
    "US0600": {f"AC{n}": "US0876" for n in range(1, 6)},
    "BG0517": {"AC1": "US0876", "AC2": "US0876", "AC3": "US0876"},
    "BG0635": {"AC3": "US0876"},
    "US0834": {"AC1": "US0876", "AC2": "US0876", "AC3": "US0876"},
    "US0282": {"AC1": "US0876"},
    "US0283": {"AC1": "US0876"},
    "US0592": {"AC1": "US0868", "AC2": "US0868"},
    "US0297": {"AC3": "US0868"},
    "BG0262": {"AC1": "US0868"},
    "US0336": {"AC1": "D0258", "AC2": "D0258", "AC3": "D0258"},
    "US0338": {"AC1": "D0258", "AC2": "D0258", "AC3": "D0258"},
}

#: The skipped stubs those criteria's selectors named, by module.
_STUBS = {
    "test_sprint.py": {
        "test_a_growing_deferrable_set_offers_the_bounded_exit",
        "test_a_growing_hard_set_is_told_to_clear_the_lanes_not_sent_to_a_dead_end",
        "test_a_converging_or_first_attempt_makes_no_offer",
        "test_a_plan_with_no_sprint_goal_is_refused",
        "test_the_escape_is_recorded_at_plan_time",
        "test_plan_refuses_a_sprint_goal_no_seat_has_reviewed",
        "test_blocked_close_offers_file_and_close",
        "test_reclose_reports_outstanding_set_trend",
        "test_the_total_is_a_fixed_term_plus_points_times_the_marginal_rate",
        "test_the_rendered_forecast_shows_both_terms_and_not_one_product",
        "test_a_half_size_batch_costs_more_than_half_and_more_per_point",
        "test_a_two_sprint_fit_is_reported_and_kept_out_of_the_total",
        "test_every_quoted_fixed_term_states_the_sprint_count_behind_it",
        "test_a_fit_at_the_minimum_is_applied_and_names_its_sprint_count",
        "test_the_round_cap_ends_the_loop",
        "test_a_growing_set_stops_the_loop",
        "test_a_shrinking_set_runs_on",
        "test_one_growth_alone_does_not_stop_the_loop",
        "test_the_rule_is_wired_into_the_close_not_only_the_library",
        "test_a_series_ending_in_zero_outstanding_never_terminates",
        "test_the_cap_still_stops_a_loop_that_is_not_converging",
        "test_divergence_still_terminates",
        "test_the_cap_fires_through_the_shipped_close_only_on_a_blocked_run",
        "test_a_non_terminal_batch_unit_refuses_the_report",
        "test_an_unanswered_review_refuses_the_report",
        "test_index_drift_refuses_the_report_and_a_clean_run_produces_one",
    },
    "test_autosprint.py": {"test_a_failing_unit_stops_the_loop_and_is_named"},
}


def _unit_file(unit: str) -> Path:
    folder = "bugs" if unit.startswith("BG") else "stories"
    found = sorted((_REPO / "sdlc-studio" / folder).glob(f"{unit}-*.md"))
    if len(found) != 1:
        raise AssertionError(f"{unit}: expected one artefact, found {found}")
    return found[0]


def _mirror(root: Path) -> None:
    """Symlink this repository into `root`, all but `sdlc-studio/.local/`.

    `verify_ac run` appends to `<root>/sdlc-studio/.local/verify-history.jsonl` even under
    `--dry-run`, and a suite that writes there is refused at commit. The mirror gives the run
    the real artefacts and test modules to execute against while its history lands in `root`.
    """
    for entry in _REPO.iterdir():
        if entry.name not in {".git", ".pytest_cache", "sdlc-studio"}:
            (root / entry.name).symlink_to(entry)
    (root / "sdlc-studio").mkdir()
    for entry in (_REPO / "sdlc-studio").iterdir():
        if entry.name != ".local":
            (root / "sdlc-studio" / entry.name).symlink_to(entry)


def _skip_reason(node) -> str | None:
    """The reason of a `@unittest.skip(...)` decorator on `node`, or None."""
    for dec in node.decorator_list:
        if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "skip":
            return ast.unparse(dec.args[0]) if dec.args else ""
    return None


class RetiredCriteriaTests(unittest.TestCase):

    def test_no_d0259_criterion_reads_red(self) -> None:
        """AC1. MUTANT: leave any one retired Verify line naming its skipped stub - the run reads
        it FAIL (every selected test SKIPPED), which is BG0749."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "repo"
            root.mkdir()
            _mirror(root)
            report = Path(d) / "report.json"
            proc = subprocess.run(
                [sys.executable, str(root / ".claude/skills/sdlc-studio/scripts/verify_ac.py"),
                 "run", "--dry-run", "--root", str(root),
                 "--dir", str(root / "sdlc-studio" / "stories"),
                 "--ids", ",".join(_RETIRED), "--report", str(report)],
                cwd=root, capture_output=True, text=True, timeout=600)
            written = sorted(Path(d).glob("report*.json"))
            self.assertTrue(written, f"no report was written:\n{proc.stdout}{proc.stderr}")
            stories = json.loads(written[0].read_text(encoding="utf-8"))["stories"]
            self.assertTrue((root / "sdlc-studio" / ".local" / "verify-history.jsonl").is_file(),
                            "the run's history did not land in the mirror")
        by_unit = {verify_ac.sdlc_md.extract_record_id(stem): row
                   for stem, row in stories.items()}
        self.assertEqual(set(_RETIRED), set(by_unit), "the run did not cover every D0259 unit")
        # The positive control: a live criterion in the same run passes, so the mirror executes
        # selectors and a retired line reading neither pass nor fail is not a run that ran nothing.
        self.assertIn("AC0", by_unit["US0834"]["passed"], f"the control did not pass:\n{proc.stdout}")
        for unit, retired in _RETIRED.items():
            row = by_unit[unit]
            for failure in row["failures"]:
                self.assertNotIn(failure["ac"], retired,
                                 f"{unit} {failure['ac']} reads FAIL: {failure['stderr']}")
                self.assertNotIn("SKIPPED", failure["stderr"],
                                 f"{unit} {failure['ac']} is red on an all-skipped selection")
            self.assertFalse(set(row["passed"]) & set(retired),
                             f"{unit}: a retired criterion reads green {row['passed']}")
            self.assertGreaterEqual(row["manual"], len(retired),
                                    f"{unit}: its retired criteria are not counted manual")
            blocks = {b.ac_id: b for b in
                      verify_ac.criteria_blocks(_unit_file(unit).read_text(encoding="utf-8"))}
            for ac, superseder in retired.items():
                block = blocks[ac]
                where = f"{unit} {ac}"
                self.assertTrue(verify_ac._is_manual(block.verifier or ""),
                                f"{where}: Verify is not retired: {block.verifier}")
                self.assertIn("retired", block.verifier, where)
                self.assertIn(superseder, block.verifier, f"{where}: the superseder is unnamed")
                self.assertIn("D0259", block.verifier, f"{where}: the ruling is unnamed")
                self.assertEqual("manual", (block.verified_state or "").lower(),
                                 f"{where}: the Verified line still reads "
                                 f"{block.verified_state!r}")
                self.assertIn(superseder, block.verified_reason,
                              f"{where}: the Verified line does not name the superseder")

    def test_the_stub_tests_are_gone(self) -> None:
        """AC2. MUTANT: keep any one stub - its name is still defined in its module."""
        for module, names in _STUBS.items():
            tree = ast.parse((_TESTS / module).read_text(encoding="utf-8"))
            defined = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            self.assertFalse(defined & names, f"{module} still defines {sorted(defined & names)}")
            superseded = sorted(n.name for n in ast.walk(tree)
                                if isinstance(n, ast.FunctionDef)
                                and "supersede" in (_skip_reason(n) or ""))
            self.assertEqual([], superseded, f"{module} keeps superseded skipped stubs")


if __name__ == "__main__":
    unittest.main()
