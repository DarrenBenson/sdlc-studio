"""`backfill_audit_runs.py` (US0568): move a run id out of prose, invent nothing.

The whole value of this pass is that it relocates a datum somebody already wrote. So the tests
are mostly about what it REFUSES to do: it does not derive a lens, it does not pick between two
run ids unless the prose says which, and it does not stamp a seeded run as measured.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

bf = loader.load_script("backfill_audit_runs")
cost = loader.load_script("audit_cost")
audit = loader.load_script("readiness")

# parents: [0] tests [1] scripts [2] sdlc-studio [3] skills [4] .claude [5] repo root.
# `parents[4]` was `.claude`, so both live-corpus tests scanned an empty tree and passed
# vacuously - a fixture-shaped mistake in the one class that exists to read the real corpus.
REPO = Path(__file__).resolve().parents[5]

#: The five ids the live corpus attributes findings to, and how many findings each filed.
#: Pinned so a sixth id appearing later REDDENS this rather than being silently skipped - the
#: original AC named three, and the two it missed were exactly the ones with the fewest findings.
LIVE_RUNS = {"wf_804ef18d": 42, "wf_9903a6e6-53a": 50, "wf_d141ccb5": 12,
             "wf_b62b2ed2": 3, "wf_95377bad": 1}


def _finding(root: Path, rec: str, raised_by: str, *, run_field: str | None = None) -> Path:
    rel = {"BG": "bugs", "CR": "change-requests", "RF": "rfcs"}[rec[:2]]
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# {rec}: a finding", "", "> **Status:** Open",
             f"> **Raised-by:** {raised_by}"]
    if run_field:
        lines.append(f"> **Audit-run:** {run_field}")
    p = d / f"{rec}-a-finding.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


class FilingRunIsReadNotGuessedTests(unittest.TestCase):

    def test_a_single_id_is_the_filing_run(self) -> None:
        self.assertEqual("wf_abc123", bf.filing_run("Claude (adversarial audit wf_abc123); agent"))

    def test_no_id_yields_None_rather_than_a_default(self) -> None:
        self.assertIsNone(bf.filing_run("sdlc-studio; agent; v1"))
        self.assertIsNone(bf.filing_run(""))

    def test_the_carry_over_shape_is_resolved_by_the_PROSE_not_by_order(self) -> None:
        """The twelve dual-id findings. `run <B>` filed it; `<A> carry-over` is where it came from.

        MUTANT: return `ids[0]`, i.e. the first id in the line. That is `wf_804ef18d` here, the
        CARRY-OVER run - so the mutant attributes twelve findings to the wrong run, and both
        would then look like separate runs to a recurrence count. Asserted on the value, and the
        fixture deliberately puts the carry-over id FIRST so order and meaning disagree.
        """
        line = ("Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); "
                "agent; skill v5.0.0")
        self.assertEqual("wf_d141ccb5", bf.filing_run(line))

    def test_two_ids_the_prose_does_NOT_disambiguate_are_refused(self) -> None:
        """A coin toss between two ids would be a fabricated provenance, so it raises."""
        with self.assertRaises(bf.Ambiguous) as ctx:
            bf.filing_run("Claude (audit wf_aaa111 and wf_bbb222); agent")
        self.assertIn("refusing to pick one", str(ctx.exception))


class ApplyStampsAndSeedsTests(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="bf_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_the_run_and_an_explicitly_unknown_lens_are_stamped(self) -> None:
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent")
        res = bf.apply(self.root)
        self.assertEqual(["BG0001"], res["stamped"])
        body = (self.root / "sdlc-studio" / "bugs" / "BG0001-a-finding.md").read_text("utf-8")
        self.assertEqual("wf_aaa111", audit.sdlc_md.extract_field(body, "Audit-run"))
        self.assertEqual(bf.LENS_UNKNOWN, audit.sdlc_md.extract_field(body, "Audit-lens"),
                         "the lens must be recorded as explicitly unknown, never guessed")

    def test_a_seeded_run_is_BACKFILLED_never_recorded(self) -> None:
        """MUTANT: seed with the default provenance. These ids were minted by nothing this project
        runs, so recording them as measured would let a verdict rest on prose strings."""
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent")
        bf.apply(self.root)
        self.assertEqual({"wf_aaa111": cost.PROVENANCE_BACKFILLED},
                         cost.registered_run_ids(self.root))

    def test_applying_TWICE_changes_nothing(self) -> None:
        """MUTANT: drop the `stamped == run` short-circuit, so a second pass appends the fields
        again and the artefact grows a duplicate block every time it runs."""
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent")
        bf.apply(self.root)
        path = self.root / "sdlc-studio" / "bugs" / "BG0001-a-finding.md"
        first = path.read_text(encoding="utf-8")
        second = bf.apply(self.root)
        self.assertEqual(["BG0001"], second["already"])
        self.assertEqual([], second["stamped"])
        self.assertEqual(first, path.read_text(encoding="utf-8"),
                         "a second pass rewrote the artefact")
        self.assertEqual(1, first.count("**Audit-run:**"))

    def test_dry_run_writes_nothing_at_all(self) -> None:
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent")
        res = bf.apply(self.root, dry_run=True)
        self.assertEqual(["BG0001"], res["stamped"])
        body = (self.root / "sdlc-studio" / "bugs" / "BG0001-a-finding.md").read_text("utf-8")
        self.assertNotIn("Audit-run", body)
        self.assertEqual({}, cost.registered_run_ids(self.root))

    def test_a_finding_naming_no_run_is_left_alone(self) -> None:
        """The control: a pass that stamped every artefact would satisfy the tests above."""
        _finding(self.root, "BG0002", "sdlc-studio; agent; v1")
        res = bf.apply(self.root)
        self.assertEqual([], res["stamped"])
        body = (self.root / "sdlc-studio" / "bugs" / "BG0002-a-finding.md").read_text("utf-8")
        self.assertNotIn("Audit-run", body)

    def test_CRs_and_RFCs_are_scanned_too(self) -> None:
        """MUTANT: scan bugs only. An RFC renders the same fields, and a CR is what `refine`
        produces from an audit."""
        _finding(self.root, "CR0001", "Claude (adversarial audit wf_ccc333); agent")
        _finding(self.root, "RFC0001", "Claude (adversarial audit wf_ddd444); agent")
        res = bf.apply(self.root)
        self.assertEqual(["CR0001", "RFC0001"], sorted(res["stamped"]))


class CheckIsTheStandingSweepTests(unittest.TestCase):

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="bfchk_"))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_a_run_in_prose_missing_from_the_field_is_reported(self) -> None:
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent")
        errors = bf.check(self.root)
        self.assertTrue(errors)
        self.assertIn("BG0001", errors[0])
        bf.apply(self.root)
        self.assertEqual([], bf.check(self.root), "the sweep still complains after a clean apply")

    def test_a_field_holding_the_WRONG_run_is_reported(self) -> None:
        """MUTANT: compare only presence, not equality. A field carrying a different id than the
        prose is worse than an absent one - it reads as attributed and points at the wrong run."""
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent",
                 run_field="wf_bbb222")
        errors = bf.check(self.root)
        self.assertTrue(errors, "a field disagreeing with the prose was accepted")
        self.assertIn("wf_aaa111", errors[0])

    def test_the_cli_exits_non_zero_on_a_disagreement_and_zero_when_clean(self) -> None:
        _finding(self.root, "BG0001", "Claude (adversarial audit wf_aaa111); agent")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(1, bf.main(["check", "--root", str(self.root)]))
            self.assertEqual(0, bf.main(["apply", "--root", str(self.root)]))
            self.assertEqual(0, bf.main(["check", "--root", str(self.root)]))


class TheLiveCorpusAgreesTests(unittest.TestCase):
    """Against this repository, because a fixture cannot see a finding that ships unstamped."""

    def test_the_live_sweep_is_clean(self) -> None:
        self.assertEqual([], bf.check(REPO),
                         "a shipped finding names a run in prose that its field does not carry")

    def test_all_FIVE_run_ids_are_seeded_with_the_counts_pinned(self) -> None:
        """The original AC named THREE ids. Two more exist, and they are the two with the fewest
        findings - so a spot check would have missed them exactly as the AC did. Pinned by count,
        so a sixth id reddens this rather than being skipped."""
        found = bf.scan(REPO)
        counts: dict = {}
        for row in found["rows"]:
            counts[row["run"]] = counts.get(row["run"], 0) + 1
        self.assertEqual(LIVE_RUNS, counts,
                         "the corpus's run attribution changed - update LIVE_RUNS deliberately")
        self.assertEqual(108, sum(counts.values()), "the attributed-finding count changed")
        registered = cost.registered_run_ids(REPO)
        for run in LIVE_RUNS:
            self.assertEqual(cost.PROVENANCE_BACKFILLED, registered.get(run),
                             f"{run} is not seeded as a backfilled register entry")

    def test_no_live_finding_is_ambiguous(self) -> None:
        self.assertEqual([], bf.scan(REPO)["ambiguous"])

    def test_the_backfilled_corpus_does_NOT_read_as_detector_owed(self) -> None:
        """The trap this pass was one edit from setting.

        108 findings share one placeholder lens across five runs. Treated as a lens NAME, that is
        a class recurring under five distinct registered runs - so `detector-owed` would report a
        detector owed on a placeholder, which is a verdict manufactured out of nothing. The
        sentinel counts as unattributable instead.

        MUTANT: drop the `lens.lower() != LENS_UNKNOWN` test in `_finding_attributions`.
        """
        res = audit.detector_owed(REPO)
        self.assertEqual([], res["owed"],
                         f"a placeholder lens was counted as a real one: {res['owed']}")
        self.assertTrue(res["cannot_judge"],
                        "a corpus with no real lens attribution must report cannot-judge")

    def test_the_sentinel_has_ONE_definition(self) -> None:
        """MUTANT: re-type the sentinel in either module. The writer stamps it and the reader
        decides attribution by it, so a second copy is how 108 findings quietly change state."""
        from lib import sdlc_md
        self.assertEqual(sdlc_md.LENS_UNKNOWN, bf.LENS_UNKNOWN)
        self.assertEqual(sdlc_md.LENS_UNKNOWN, audit.LENS_UNKNOWN)


class FilingRunDisambiguationTests(unittest.TestCase):
    """Two filing runs on one line are REFUSED, never resolved by document order.

    `filing_run` returned on the FIRST `run <id>` match, so the Ambiguous refusal was reachable
    only when no `run <id>` appeared at all - and a line naming two filing runs was settled by
    which came first in the sentence. That is exactly the guess the refusal exists to prevent,
    and a fabricated provenance is worse than an absent one.
    """

    def test_two_filing_runs_are_refused(self) -> None:
        """MUTANT: restore `if filed: return filed.group(1)`."""
        mod = bf
        with self.assertRaises(mod.Ambiguous) as caught:
            mod.filing_run("run wf_aaa1 and run wf_bbb2 both filed it")
        msg = str(caught.exception)
        self.assertIn("wf_aaa1", msg, "the refusal does not name the candidates")
        self.assertIn("wf_bbb2", msg, "the refusal does not name the candidates")

    def test_a_carry_over_disambiguates_in_both_word_orders(self) -> None:
        """MUTANT: match only `<id> carry-over`.

        Half this corpus writes `carry-over from <id>`, and a pattern that silently matches
        nothing is how the disambiguation quietly stopped happening.
        """
        mod = bf
        self.assertEqual("wf_new1", mod.filing_run("run wf_new1 (wf_old2 carry-over)"))
        self.assertEqual("wf_new1", mod.filing_run("run wf_new1 (carry-over from wf_old2)"))

    def test_a_single_id_is_still_the_answer(self) -> None:
        """The control. MUTANT: refuse whenever more than zero ids appear."""
        mod = bf
        self.assertEqual("wf_abc123", mod.filing_run("filed in run wf_abc123"))
        self.assertIsNone(mod.filing_run("no run named here"))


if __name__ == "__main__":
    unittest.main()
