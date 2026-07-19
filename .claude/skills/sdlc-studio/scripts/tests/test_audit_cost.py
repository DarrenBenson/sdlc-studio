"""Tests for the audit cost estimator (audit_cost.py) - CR0276 / US0159.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
_spec = importlib.util.spec_from_file_location("audit_cost", _SCRIPTS / "audit_cost.py")
audit_cost = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit_cost)


class EstimateTests(unittest.TestCase):
    def test_reference_run_is_in_the_right_ballpark(self) -> None:
        # measured reference: 7 lenses -> 192 agents, ~6.9M tokens, ~29 min. The estimate is
        # order-of-magnitude; assert it lands within a sane band, not on the nose.
        est = audit_cost.estimate(7)
        self.assertTrue(150 <= est["agents"] <= 230)
        self.assertTrue(5_000_000 <= est["tokens"] <= 9_000_000)
        self.assertTrue(20 <= est["wall_minutes"] <= 50)
        self.assertTrue(est["large"])

    def test_small_scoped_audit_is_not_large(self) -> None:
        est = audit_cost.estimate(2, rounds=1, candidates_per_lens=3)
        self.assertFalse(est["large"])
        self.assertLess(est["agents"], audit_cost.LARGE_AGENTS)

    def test_single_lens_at_defaults_is_not_large(self) -> None:
        # the "no ceremony" path the docs promise: one lens at the default knobs must be small
        est = audit_cost.estimate(1)
        self.assertFalse(est["large"])

    def test_breakdown_adds_up(self) -> None:
        est = audit_cost.estimate(5, rounds=2, votes=3, candidates_per_lens=4)
        b = est["breakdown"]
        self.assertEqual(b["finders"], 5 * 2)
        self.assertEqual(b["candidates_est"], 5 * 4)
        self.assertEqual(b["refuters"], 5 * 4 * 3)
        self.assertEqual(est["agents"], b["finders"] + b["refuters"] + b["merge"])
        self.assertEqual(est["tokens"], est["agents"] * audit_cost.TOKENS_PER_AGENT)

    def test_zero_lenses_is_zero(self) -> None:
        est = audit_cost.estimate(0)
        self.assertEqual(est["agents"], 0)
        self.assertFalse(est["large"])

    def test_large_threshold_on_tokens_alone(self) -> None:
        # even a modest agent count crosses "large" if the token budget does
        est = audit_cost.estimate(3, candidates_per_lens=10, tokens_per_agent=60_000)
        self.assertTrue(est["tokens"] >= audit_cost.LARGE_TOKENS)
        self.assertTrue(est["large"])

    def test_cli_json(self) -> None:
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = audit_cost.main(["--lenses", "7", "--format", "json"])
        import json
        self.assertEqual(rc, 0)
        self.assertIn("agents", json.loads(buf.getvalue()))


def _run(argv: list[str]) -> tuple[int, str]:
    """Drive the CLI, returning (exit code, stdout)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = audit_cost.main(argv)
    return rc, buf.getvalue()


#: One fully-populated run row, as `record` takes it on the command line.
_ROW = ("--lenses", "7", "--rounds", "3", "--votes", "3",
        "--est-agents", "217", "--est-tokens", "7800000",
        "--actual-agents", "265", "--actual-tokens", "12400000",
        "--actual-minutes", "95")


class RecordSubcommandTests(unittest.TestCase):
    """`record` appends a run's scope, estimate and actuals to the committed ledger."""

    def test_record_writes_the_scope_estimate_and_actuals(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out = _run(["record", "--root", d, *_ROW, "--notes", "an outage forced rework"])
            self.assertEqual(rc, 0)
            rows = audit_cost.read_ledger(d)
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row["lenses"], 7)
            self.assertEqual(row["rounds"], 3)
            self.assertEqual(row["votes"], 3)
            self.assertEqual(row["estimated_agents"], 217)
            self.assertEqual(row["estimated_tokens"], 7_800_000)
            self.assertEqual(row["actual_agents"], 265)
            self.assertEqual(row["actual_tokens"], 12_400_000)
            self.assertEqual(row["actual_minutes"], 95)
            self.assertEqual(row["notes"], "an outage forced rework")
            self.assertTrue(row["date"], "the row must carry the date it was recorded")
            self.assertIn(audit_cost.ledger_path(d).name, out)

    def test_the_ledger_is_committed_evidence_not_local_state(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = audit_cost.ledger_path(d)
            self.assertNotIn(".local", path.parts,
                             "the ledger is project evidence, so it cannot live in .local/")
            self.assertEqual(path.parent, Path(d) / "sdlc-studio" / "retros" / "evidence")

    def test_a_second_record_leaves_the_first_intact(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _run(["record", "--root", d, *_ROW, "--notes", "first"])
            _run(["record", "--root", d, "--lenses", "3", "--rounds", "2", "--votes", "3",
                  "--est-agents", "80", "--est-tokens", "2900000",
                  "--actual-agents", "91", "--actual-tokens", "3600000", "--notes", "second"])
            rows = audit_cost.read_ledger(d)
            self.assertEqual([r["notes"] for r in rows], ["first", "second"])
            self.assertEqual(rows[0]["actual_agents"], 265)

    def test_optional_fields_are_omitted_rather_than_invented(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _run(["record", "--root", d, "--lenses", "2", "--rounds", "1", "--votes", "3",
                  "--est-agents", "26", "--est-tokens", "940000",
                  "--actual-agents", "30", "--actual-tokens", "1100000"])
            row = audit_cost.read_ledger(d)[0]
            self.assertIsNone(row.get("actual_minutes"))
            self.assertIsNone(row.get("notes"))

    def test_record_reports_json_when_asked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            rc, out = _run(["record", "--root", d, *_ROW, "--format", "json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out)["actual_agents"], 265)

    def test_the_flat_estimate_invocation_still_works(self) -> None:
        # The docs and profiles call `audit_cost.py --lenses 7` with no subcommand;
        # restructuring into subparsers must not break them.
        rc, out = _run(["--lenses", "7"])
        self.assertEqual(rc, 0)
        self.assertIn("audit cost estimate", out)

    def test_root_is_accepted_before_the_verb(self) -> None:
        # --root is a global in this script family, so it must parse on either side of the
        # verb - and the inferred verb must not be planted in front of it.
        with tempfile.TemporaryDirectory() as d:
            rc, _ = _run(["--root", d, "record", *_ROW])
            self.assertEqual(rc, 0)
            self.assertEqual(len(audit_cost.read_ledger(d)), 1)
            args = audit_cost.build_parser().parse_args(["--root", d, "run", "--lenses", "2"])
            self.assertEqual(args.root, d)

    def test_run_is_reachable_by_name(self) -> None:
        rc, out = _run(["run", "--lenses", "7"])
        self.assertEqual(rc, 0)
        self.assertIn("audit cost estimate", out)


class LedgerBasisTests(unittest.TestCase):
    """The estimate is derived from the recorded medians, and names the basis it used."""

    @staticmethod
    def _seed(root: str, rows: list[tuple[int, int, int, int, int]]) -> None:
        for lenses, rounds, votes, agents, tokens in rows:
            _run(["record", "--root", root,
                  "--lenses", str(lenses), "--rounds", str(rounds), "--votes", str(votes),
                  "--est-agents", "1", "--est-tokens", "1",
                  "--actual-agents", str(agents), "--actual-tokens", str(tokens)])

    def test_empty_ledger_falls_back_to_the_shipped_constants(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            basis = audit_cost.measured_basis(d)
            self.assertEqual(basis["source"], "constants")
            self.assertEqual(basis["runs"], 0)
            self.assertEqual(basis["candidates_per_lens"], audit_cost.CANDIDATES_PER_LENS)
            self.assertEqual(basis["tokens_per_agent"], audit_cost.TOKENS_PER_AGENT)

    def test_medians_come_from_the_recorded_runs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # agents = lenses*rounds + candidates*votes + 1, inverted per row:
            #   (61 - 2 - 1) / 3 = 19.33 candidates over 2 lenses -> 9.67/lens
            #   (91 - 6 - 1) / 3 = 28 candidates over 3 lenses    -> 9.33/lens
            #   (46 - 1 - 1) / 3 = 14.67 candidates over 1 lens   -> 14.67/lens
            # median of {9.67, 9.33, 14.67} -> 9.67 -> 10 rounded
            # tokens/agent: 61->40000, 91->20000, 46->60000 ; median 40000
            self._seed(d, [(2, 1, 3, 61, 2_440_000),
                           (3, 2, 3, 91, 1_820_000),
                           (1, 1, 3, 46, 2_760_000)])
            basis = audit_cost.measured_basis(d)
            self.assertEqual(basis["source"], "ledger")
            self.assertEqual(basis["runs"], 3)
            self.assertEqual(basis["candidates_per_lens"], 10)
            self.assertEqual(basis["tokens_per_agent"], 40_000)

    def test_a_single_run_is_enough_to_shift_the_basis(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(d, [(1, 1, 3, 46, 2_760_000)])
            basis = audit_cost.measured_basis(d)
            self.assertEqual(basis["source"], "ledger")
            self.assertEqual(basis["runs"], 1)
            self.assertEqual(basis["candidates_per_lens"], 15)
            self.assertEqual(basis["tokens_per_agent"], 60_000)

    def test_an_unreadable_ledger_falls_back_without_raising(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            path = audit_cost.ledger_path(d)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("not json at all\n{\n", encoding="utf-8")
            basis = audit_cost.measured_basis(d)
            self.assertEqual(basis["source"], "constants")
            self.assertEqual(basis["tokens_per_agent"], audit_cost.TOKENS_PER_AGENT)

    def test_rows_that_cannot_yield_a_measurement_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # zero lenses, and an agent count below the finder floor: neither inverts
            # into a candidate count, so neither may contribute a median.
            self._seed(d, [(0, 1, 3, 10, 360_000), (4, 3, 3, 5, 180_000)])
            basis = audit_cost.measured_basis(d)
            self.assertEqual(basis["candidates_per_lens"], audit_cost.CANDIDATES_PER_LENS,
                             "an uninvertible row must not reach the candidate median")
            self.assertEqual(basis["runs"], 0)

    def test_the_estimate_uses_the_basis_it_is_given(self) -> None:
        basis = {"source": "ledger", "runs": 2,
                 "candidates_per_lens": 16, "tokens_per_agent": 72_000}
        est = audit_cost.estimate(7, basis=basis)
        self.assertEqual(est["assumptions"]["candidates_per_lens"], 16)
        self.assertEqual(est["assumptions"]["tokens_per_agent"], 72_000)
        self.assertEqual(est["basis"], {"source": "ledger", "runs": 2})
        self.assertGreater(est["agents"], audit_cost.estimate(7)["agents"])

    def test_an_explicit_flag_overrides_the_measured_basis(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(d, [(1, 1, 3, 46, 2_760_000)])
            rc, out = _run(["run", "--root", d, "--lenses", "2",
                            "--candidates-per-lens", "4", "--format", "json"])
            self.assertEqual(rc, 0)
            est = json.loads(out)
            self.assertEqual(est["assumptions"]["candidates_per_lens"], 4)
            self.assertEqual(est["assumptions"]["tokens_per_agent"], 60_000)

    def test_the_output_names_which_basis_it_used(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _, out = _run(["run", "--root", d, "--lenses", "3"])
            self.assertIn("shipped constants", out)
            self.assertNotIn("recorded run", out)

            self._seed(d, [(1, 1, 3, 46, 2_760_000)])
            _, out = _run(["run", "--root", d, "--lenses", "3"])
            self.assertIn("1 recorded run", out)
            self.assertNotIn("shipped constants", out)

    def test_json_output_carries_the_basis(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self._seed(d, [(1, 1, 3, 46, 2_760_000)])
            _, out = _run(["run", "--root", d, "--lenses", "3", "--format", "json"])
            self.assertEqual(json.loads(out)["basis"], {"source": "ledger", "runs": 1})

    def test_the_default_estimate_is_still_the_shipped_constants(self) -> None:
        # No basis passed means no cwd dependence: a library caller gets the seeds.
        est = audit_cost.estimate(7)
        self.assertEqual(est["basis"]["source"], "constants")
        self.assertEqual(est["assumptions"]["tokens_per_agent"], audit_cost.TOKENS_PER_AGENT)


if __name__ == "__main__":
    unittest.main()
