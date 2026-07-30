"""`readiness.py detector-owed` (US0463): a lens paid for twice wants a script, not a re-run.

The rule is SURVIVAL ACROSS RUNS, never volume within one. A run finding a class five times is
the lens working; the same class surviving into a second run is a judgement the model has now
been billed for twice, and that is what a deterministic detector should take over.

Three verdicts, and the third is the one that matters most. `cannot-judge` is separate from
`clean` and DOMINATES `owed`, because a workspace whose findings carry no attribution has nothing
to say about recurrence - and reporting that as "nothing owed" is the read-a-green-off-something-
that-never-ran class this project keeps filing bugs about.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

audit = loader.load_script("readiness")
cost = loader.load_script("audit_cost")

#: A lens whose shipped signature declares NO mechanical detector, so recurrence means owed.
MANUAL_LENS = "correctness"
#: A lens whose shipped signature IS mechanical, so recurrence means the script already exists.
MECHANICAL_LENS = "determinism"


def _workspace() -> Path:
    d = Path(tempfile.mkdtemp(prefix="owed_"))
    (d / "sdlc-studio" / "bugs").mkdir(parents=True)
    (d / "sdlc-studio" / "change-requests").mkdir(parents=True)
    return d


def _register(root: Path, *run_ids: str, provenance: str | None = None) -> None:
    for rid in run_ids:
        cost.record(root, {"run_id": rid, "lenses": 3, "rounds": 3, "votes": 3,
                           "provenance": provenance,
                           "estimated_agents": 30, "estimated_tokens": 900_000,
                           "actual_agents": 33, "actual_tokens": 1_000_000})


def _finding(root: Path, rec: str, *, lens: str | None = None, run: str | None = None) -> None:
    """A bug or CR on disk, with or without an audit attribution."""
    rel = "bugs" if rec.startswith("BG") else "change-requests"
    lines = [f"# {rec}: a finding", "", "> **Status:** Open", "> **Severity:** Medium"]
    if lens:
        lines.append(f"> **Audit-lens:** {lens}")
    if run:
        lines.append(f"> **Audit-run:** {run}")
    (root / "sdlc-studio" / rel / f"{rec}-a-finding.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")


class DetectorOwedTests(unittest.TestCase):

    def setUp(self) -> None:
        self.root = _workspace()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def _cli(self, fmt: str = "text") -> tuple[int, str]:
        args = type("A", (), {"root": str(self.root), "format": fmt})()
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = audit.cmd_detector_owed(args)
        return code, buf.getvalue()

    def test_a_lens_filed_in_two_runs_is_owed_and_the_exit_code_and_json_agree(self) -> None:
        """AC1.

        MUTANTS. (1) `len(entry["runs"]) < 2` -> `len(entry["findings"]) < 2`, which AC2 kills.
        (2) `< 2` -> `< 1`, which the clean workspace below kills. (3) the JSON and the text mode
        disagreeing, which is why BOTH are asserted from the same fixture.
        """
        _register(self.root, "RUN-A", "RUN-B")
        _finding(self.root, "BG0001", lens=MANUAL_LENS, run="RUN-A")
        _finding(self.root, "BG0002", lens=MANUAL_LENS, run="RUN-B")

        res = audit.detector_owed(self.root)
        self.assertEqual(1, len(res["owed"]), f"the recurring lens was not owed: {res}")
        row = res["owed"][0]
        self.assertEqual(MANUAL_LENS, row["lens"])
        self.assertEqual(["RUN-A", "RUN-B"], row["runs"], "both runs must be named")
        self.assertEqual(["BG0001", "BG0002"], row["findings"])
        self.assertTrue(row["rationale"], "the pack's own reason for having no detector is unnamed")
        self.assertEqual(audit.OWED_FOUND, audit.owed_exit_code(res))

        code, out = self._cli()
        self.assertEqual(audit.OWED_FOUND, code)
        self.assertIn(MANUAL_LENS, out)
        self.assertIn("RUN-A", out)

        jcode, jout = self._cli("json")
        payload = json.loads(jout)
        self.assertEqual(jcode, payload["exit_code"], "the JSON disagrees with the exit code")
        self.assertEqual([MANUAL_LENS], [r["lens"] for r in payload["owed"]])

    def test_a_clean_workspace_exits_zero(self) -> None:
        """The positive control for AC1: a checker that reported everything owed would pass the
        test above while being useless. Also kills the `>= 1` mutant."""
        _register(self.root, "RUN-A")
        _finding(self.root, "BG0001", lens=MANUAL_LENS, run="RUN-A")
        res = audit.detector_owed(self.root)
        self.assertEqual([], res["owed"])
        self.assertFalse(res["cannot_judge"], "a fully attributed workspace read as unjudgeable")
        self.assertEqual(audit.OWED_CLEAN, audit.owed_exit_code(res))

    def test_repeats_inside_one_run_are_not_owed(self) -> None:
        """AC2. Five findings, ONE run: the rule is survival across runs, not volume within one.

        MUTANT: count findings instead of distinct runs. This is the only test that separates
        those two, so without it the implementation is free to count the wrong thing.
        """
        _register(self.root, "RUN-A")
        for i in range(1, 6):
            _finding(self.root, f"BG000{i}", lens=MANUAL_LENS, run="RUN-A")
        res = audit.detector_owed(self.root)
        self.assertEqual([], res["owed"],
                         "five hits in ONE run were treated as recurrence - that is the lens "
                         "working, not a detector owed")
        self.assertEqual(audit.OWED_CLEAN, audit.owed_exit_code(res))

    def test_a_mechanical_signature_reports_detector_exists(self) -> None:
        """AC3: a recurring lens whose detector already ships must never be re-commissioned.

        MUTANTS. (1) invert the mechanical test. (2) report it as detector-exists AND ALSO list it
        as owed - so the owed list is asserted EMPTY and the exit code asserted clean, not merely
        that `exists` is populated.
        """
        _register(self.root, "RUN-A", "RUN-B")
        _finding(self.root, "BG0001", lens=MECHANICAL_LENS, run="RUN-A")
        _finding(self.root, "BG0002", lens=MECHANICAL_LENS, run="RUN-B")
        res = audit.detector_owed(self.root)
        self.assertEqual([MECHANICAL_LENS], [r["lens"] for r in res["exists"]])
        self.assertEqual([], res["owed"], "an existing detector was re-commissioned as owed")
        self.assertEqual(audit.OWED_CLEAN, audit.owed_exit_code(res))
        self.assertTrue(res["exists"][0]["signature"],
                        "detector-exists must name the command a finder should run and skip on")

    def test_unattributed_findings_are_named_not_counted_as_clean(self) -> None:
        """AC4: a workspace it could not read is never reported as having nothing owed."""
        _register(self.root, "RUN-A")
        _finding(self.root, "BG0001", lens=MANUAL_LENS, run="RUN-A")
        _finding(self.root, "BG0002")            # no attribution at all
        _finding(self.root, "CR0001")            # nor this one, and CRs are scanned too
        res = audit.detector_owed(self.root)
        self.assertEqual(["BG0002", "CR0001"], res["unattributed"],
                         "an unattributed finding was not named - or CRs are not scanned")
        self.assertTrue(res["cannot_judge"])
        code, out = self._cli()
        self.assertEqual(audit.OWED_CANNOT_JUDGE, code)
        self.assertIn("CANNOT JUDGE", out)
        self.assertIn("NOT 'nothing owed'", out,
                      "the report does not say that cannot-judge is not a clean verdict")

    def test_the_cannot_judge_exit_code_is_3_and_not_2(self) -> None:
        """MUTANT: return 2 for cannot-judge. `cmd_profile` already returns 2 for an unknown
        profile and argparse uses 2 for a usage error, so a caller could not tell "I could not
        judge this workspace" from "you typed the flag wrong". The exact integer is asserted,
        never `!= 0`.
        """
        _finding(self.root, "BG0002")
        res = audit.detector_owed(self.root)
        self.assertEqual(3, audit.owed_exit_code(res))
        self.assertNotEqual(2, audit.OWED_CANNOT_JUDGE)

    def test_cannot_judge_DOMINATES_owed(self) -> None:
        """MUTANT: `if result["cannot_judge"]` -> `if result["cannot_judge"] and not result["owed"]`.

        Dies ONLY to a fixture holding BOTH an owed lens and unattributable findings. Without
        precedence the unreadable findings vanish behind a verdict that looks like an answer.
        """
        _register(self.root, "RUN-A", "RUN-B")
        _finding(self.root, "BG0001", lens=MANUAL_LENS, run="RUN-A")
        _finding(self.root, "BG0002", lens=MANUAL_LENS, run="RUN-B")
        _finding(self.root, "BG0003")            # and something it cannot read
        res = audit.detector_owed(self.root)
        self.assertTrue(res["owed"], "precondition: the fixture must ALSO have an owed lens")
        self.assertTrue(res["unattributed"], "precondition: and something unattributable")
        self.assertEqual(audit.OWED_CANNOT_JUDGE, audit.owed_exit_code(res),
                         "owed won over cannot-judge, so the unreadable findings are hidden "
                         "behind a verdict that reads like an answer")

    def test_an_UNREGISTERED_run_is_not_counted_as_a_second_run(self) -> None:
        """The register's whole purpose, and the mutant the design review said would otherwise
        go unpinned: count distinct run ids WITHOUT checking them against the register.

        Fixture: one registered run and one id the register does not hold. Counting both would
        make this lens owed on the strength of a string nobody recorded - which is the
        typo-manufactured second run the filing-time validation exists to prevent, arriving by
        the back door instead.
        """
        _register(self.root, "RUN-A")
        _finding(self.root, "BG0001", lens=MANUAL_LENS, run="RUN-A")
        _finding(self.root, "BG0002", lens=MANUAL_LENS, run="RUN-TYPO")
        res = audit.detector_owed(self.root)
        self.assertEqual([], res["owed"],
                         "an unregistered run id was counted as a second distinct run")
        self.assertEqual(["BG0002"], [r["id"] for r in res["unregistered"]])
        self.assertEqual(audit.OWED_CANNOT_JUDGE, audit.owed_exit_code(res),
                         "an unregistered citation must be reported, not silently dropped")

    def test_a_backfilled_run_is_reported_as_such(self) -> None:
        """A verdict resting on ids asserted from prose is weaker than one resting on measured
        runs, so the provenance travels with the row rather than being flattened away."""
        _register(self.root, "RUN-A")
        _register(self.root, "wf_old", provenance=cost.PROVENANCE_BACKFILLED)
        _finding(self.root, "BG0001", lens=MANUAL_LENS, run="RUN-A")
        _finding(self.root, "BG0002", lens=MANUAL_LENS, run="wf_old")
        res = audit.detector_owed(self.root)
        self.assertEqual(1, len(res["owed"]))
        self.assertEqual([cost.PROVENANCE_BACKFILLED, cost.PROVENANCE_RECORDED],
                         res["owed"][0]["provenance"],
                         "the row does not distinguish a measured run from an asserted one")

    def test_a_lens_no_pack_declares_is_owed_rather_than_silently_dropped(self) -> None:
        """A lens name that resolves to nothing has no signature to judge, so it cannot be
        detector-exists. It must not therefore disappear: it recurs, and something is owed."""
        _register(self.root, "RUN-A", "RUN-B")
        _finding(self.root, "BG0001", lens="a-lens-no-pack-declares", run="RUN-A")
        _finding(self.root, "BG0002", lens="a-lens-no-pack-declares", run="RUN-B")
        res = audit.detector_owed(self.root)
        self.assertEqual(["a-lens-no-pack-declares"], [r["lens"] for r in res["owed"]])
        self.assertIsNone(res["owed"][0]["profile"])


class DetectorOwedCliTests(unittest.TestCase):

    def test_the_verb_is_reachable_from_the_parser(self) -> None:
        """A verb only its own tests call is not a command. Driven through `build_parser`, since
        `main` would run over this repository."""
        args = audit.build_parser().parse_args(["detector-owed", "--format", "json"])
        self.assertIs(audit.cmd_detector_owed, args.func)
        self.assertEqual("json", args.format)


if __name__ == "__main__":
    unittest.main()
