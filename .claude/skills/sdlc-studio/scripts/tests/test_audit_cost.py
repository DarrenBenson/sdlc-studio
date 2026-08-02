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


class AuditRunRegisterTests(unittest.TestCase):
    """The ledger doubles as the AUDIT-RUN REGISTER (US0462).

    This class exists because the register shipped with all of its coverage in another module's
    test file: two new public functions and a changed `LEDGER_FIELDS` had no test here at all, and
    `cmd_record` could stop passing `run_id` with the whole 5,364-test suite green.
    """

    def test_the_CLI_writes_the_register_entry_not_only_the_library(self) -> None:
        """MUTANT: delete `"run_id": getattr(args, "run_id", None)` from `cmd_record`.

        The CLI then writes no register entry at all, and every later `--audit-run` is refused -
        with the whole suite green, because the sibling tests called `record()` directly. This is
        the same defect as testing `file_finding()` instead of the command, one file over.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = _run(["record", "--root", str(root), "--run-id", "RUN-CLI-01", *_ROW])
            self.assertEqual(0, rc)
            self.assertEqual({"RUN-CLI-01": audit_cost.PROVENANCE_RECORDED},
                             audit_cost.registered_run_ids(root),
                             "the CLI recorded a run that is not a register entry")
            self.assertIsNotNone(audit_cost.run_row(root, "RUN-CLI-01"))

    def test_the_CLI_can_write_a_BACKFILLED_row(self) -> None:
        """MUTANT: no `--provenance` flag at all. Half the provenance vocabulary was reachable
        only by importing the module, which makes `backfilled` a value with no operator-facing
        writer - the same reader-with-nothing-behind-it shape one level down.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rc, _ = _run(["record", "--root", str(root), "--run-id", "wf_asserted",
                          "--provenance", "backfilled", *_ROW])
            self.assertEqual(0, rc)
            self.assertEqual({"wf_asserted": audit_cost.PROVENANCE_BACKFILLED},
                             audit_cost.registered_run_ids(root))

    def test_run_id_is_a_declared_ledger_field(self) -> None:
        """MUTANT: drop `run_id` from `LEDGER_FIELDS`. `record` builds its row from that tuple, so
        the value is accepted and silently dropped."""
        self.assertIn("run_id", audit_cost.LEDGER_FIELDS)
        self.assertIn("provenance", audit_cost.LEDGER_FIELDS)

    def test_a_row_recorded_with_no_run_id_is_not_a_register_entry(self) -> None:
        """The positive control's partner: the two rows already committed to this repository carry
        no run id, and they must not become citable by accident."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _run(["record", "--root", str(root), *_ROW])
            self.assertEqual({}, audit_cost.registered_run_ids(root))
            self.assertEqual("empty", audit_cost.register(root)["state"])

    def test_an_empty_run_id_never_matches_a_row(self) -> None:
        """MUTANT: drop `run_row`'s empty-id guard. `""` would then match the first row whose
        `run_id` is absent, making every unrecorded run look registered."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _run(["record", "--root", str(root), *_ROW])          # a row with NO run id
            for empty in ("", "   ", None):
                with self.subTest(empty=empty):
                    self.assertIsNone(audit_cost.run_row(root, empty))

    def test_a_LEGACY_row_with_no_provenance_key_reads_as_recorded(self) -> None:
        """MUTANT: drop the `or PROVENANCE_RECORDED` fallback in the register read.

        Dead-looking, because `record()` now always writes the key - so every row IT writes has
        one. The fallback is load-bearing for rows written BEFORE this field existed: the two rows
        already committed to this repository have no `provenance` key, and without the default they
        would read as provenance `""`, which is neither of the two documented values.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            shard = audit_cost.ledger_path(root)
            shard.parent.mkdir(parents=True, exist_ok=True)
            shard.write_text(json.dumps({"date": "2026-07-27", "run_id": "RUN-LEGACY",
                                         "lenses": 7}) + "\n", encoding="utf-8")
            self.assertEqual({"RUN-LEGACY": audit_cost.PROVENANCE_RECORDED},
                             audit_cost.registered_run_ids(root),
                             "a row predating the provenance field read as neither documented "
                             "value")
            self.assertIn(audit_cost.registered_run_ids(root)["RUN-LEGACY"],
                          audit_cost.PROVENANCES)

    def test_the_register_distinguishes_ok_empty_and_CORRUPT(self) -> None:
        """The fail-open a reviewer demonstrated: `read_ledger` skips a malformed line, which is
        right for the estimator (a median degrades gracefully) and wrong for a register, where
        absence is a refusal. A truncated shard made every recorded run invisible - identical to
        never-recorded - and the refusal then told the operator to record it again, appending a
        duplicate to an already-broken file.

        MUTANT: route `register` through `read_ledger`, so `corrupt` collapses into `ok`/`empty`.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertEqual("empty", audit_cost.register(root)["state"])
            _run(["record", "--root", str(root), "--run-id", "RUN-OK-01", *_ROW])
            self.assertEqual("ok", audit_cost.register(root)["state"])

            shard = audit_cost.ledger_path(root)
            with open(shard, "a", encoding="utf-8") as fh:
                fh.write("{ this line was never finished\n")
            state = audit_cost.register(root)
            self.assertEqual("corrupt", state["state"],
                             "a truncated shard read as a healthy register")
            self.assertIn("unreadable", state["detail"])
            # The rows it COULD read stay usable - corruption is not an excuse to lose evidence.
            self.assertIn("RUN-OK-01", state["runs"])

    def test_the_estimator_still_tolerates_a_bad_line(self) -> None:
        """The counterpart, so the strict register read does not leak into the estimator: one
        corrupt line must not cost the whole evidence base for a median."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _run(["record", "--root", str(root), "--run-id", "RUN-OK-02", *_ROW])
            with open(audit_cost.ledger_path(root), "a", encoding="utf-8") as fh:
                fh.write("not json at all\n")
            self.assertEqual(1, len(audit_cost.read_ledger(root)),
                             "the estimator's lenient read was made strict")

    def test_the_register_is_written_where_git_TRACKS_it(self) -> None:
        """MUTANT: move the ledger under `.local/`.

        A previous version asserted only `assertNotIn(".local", parts)`, which passes for a move
        to any OTHER gitignored directory. The invariant being protected is that the register is
        TRACKED, so the path is pinned against the committed evidence directory instead of against
        one spelling of one wrong answer.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _run(["record", "--root", str(root), "--run-id", "RUN-OK-03", *_ROW])
            written = audit_cost.ledger_path(root)
            self.assertEqual(("sdlc-studio", "retros", "evidence"),
                             written.relative_to(root).parts[:3],
                             "the register left the committed evidence directory")
            self.assertNotIn(".local", written.parts)


class RegisterProvenanceTests(unittest.TestCase):
    """Two readers of one ledger must agree which row wins.

    `register` folded LAST-row-wins (dict assignment) while `run_row` returned the FIRST match,
    so a duplicated run id gave a different provenance depending on which reader you asked -
    and a seeded run could be silently overwritten by a plain `record` appended after it.
    """

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "retros" / "evidence").mkdir(parents=True)
        return root

    def test_both_readers_agree_on_which_row_wins(self) -> None:
        """MUTANT: revert `run_row` to returning the first match.

        Asserted as AGREEMENT between the two, not against a hardcoded expectation: a test
        pinning one reader's answer would pass while the other still disagreed, which is the
        defect itself.
        """
        mod = audit_cost
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            shard = root / "sdlc-studio" / "retros" / "evidence" / "audit-cost-2026-01-01.jsonl"
            shard.write_text(
                '{"run_id": "RUN-A", "provenance": "seeded", "lenses": 1, "rounds": 1, '
                '"votes": 1, "findings": 1, "tokens": 1}\n'
                '{"run_id": "RUN-A", "provenance": "recorded", "lenses": 1, "rounds": 1, '
                '"votes": 1, "findings": 1, "tokens": 1}\n', encoding="utf-8")
            row = mod.run_row(root, "RUN-A")
            registered = mod.registered_run_ids(root)
        self.assertIsNotNone(row, "the ledger row was not found at all")
        self.assertEqual(registered.get("RUN-A"), row.get("provenance"),
                         "run_row and the register disagree about which duplicate row wins")

    def test_a_duplicate_run_id_with_different_provenance_is_refused(self) -> None:
        """MUTANT: append unconditionally, as `record` did.

        Nothing guarded a duplicate id, so a plain `record` after a seeded run silently
        changed what the register said that run's provenance was.
        """
        mod = audit_cost
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            base = {"lenses": 1, "rounds": 1, "votes": 1, "findings": 1, "tokens": 1}
            mod.record(root, {**base, "run_id": "RUN-B", "provenance": "seeded"})
            with self.assertRaises(ValueError) as caught:
                mod.record(root, {**base, "run_id": "RUN-B", "provenance": "recorded"})
        self.assertIn("RUN-B", str(caught.exception),
                      "the refusal does not name the duplicated run")

    def test_a_fresh_run_id_still_records(self) -> None:
        """The control. MUTANT: refuse every second record.

        A guard that refuses any repeat write would stop the ledger being appended to at all.
        """
        mod = audit_cost
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            base = {"lenses": 1, "rounds": 1, "votes": 1, "findings": 1, "tokens": 1}
            mod.record(root, {**base, "run_id": "RUN-C", "provenance": "seeded"})
            mod.record(root, {**base, "run_id": "RUN-D", "provenance": "recorded"})
            registered = mod.registered_run_ids(root)
        self.assertEqual({"RUN-C", "RUN-D"}, set(registered),
                         "a distinct run id was refused or lost")


if __name__ == "__main__":
    unittest.main()
