"""BG1135: `critic.py supersede --brief <fingerprint>` retires exactly one of several delivery
rows that share a unit, date, reviewer and verdict.

BG0962 holds two REJECT rows that agree on unit, date, reviewer and verdict and differ in their
brief fingerprints. `supersede` narrowed only by `--reviewer` and `--verdict`, so it refused both as
ambiguous, and a record keyed by those fields would have retired both. The record now carries the
named row's Brief cell (`row-brief=`), and the join that marks rows superseded for every
`read_verdicts` caller (`_annotate_superseded`) honours it; a record without one still retires
every row it names.

Each test seeds a ledger by hand with rows shaped like BG0962's, then drives the shipped CLI.

MUTANTS: the `--brief` narrowing dropped, so the bug's refusal stands; the record written without
`row-brief`, or the join ignoring it, so both rows are retired; the ambiguous refusal naming no
fingerprint; the first of several same-fingerprint rows taken instead of refused; the fingerprint
matched by prefix or containment, or case-sensitively; `-` not reading as an absent brief; a
record with no `row-brief` read as naming an empty one, so it retires nothing; only the first
record under a key kept; `row-brief` written without `--brief`.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

SCRIPT = Path(__file__).resolve().parent.parent / "critic.py"
critic = loader.load_script("critic")

UNIT, DATE, REVIEWER = "BG0962", "2026-10-07", "qa-seat-BG0962-r1"
FIRST, SECOND = "9ef645b3012d", "2fe801ee8a2a"
OPERATOR = "Darren Benson (operator)"


def _row(brief: str, issues: str, unit: str = UNIT, verdict: str = "REJECT") -> str:
    return (f"| {unit} | {verdict} | {REVIEWER} | engineering-seat-triage | {DATE} | {brief} "
            f"| full | {issues} |\n")


def _seed(root: Path, *rows: str) -> Path:
    path = critic.verdicts_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# Critic Verdicts\n\n" + critic._TABLE + "".join(rows), encoding="utf-8")
    return path


def _cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args, "--root", str(root)],
                          capture_output=True, text=True, check=False)


def _supersede(root: Path, *narrowing: str) -> subprocess.CompletedProcess:
    return _cli(root, "supersede", "--unit", UNIT, "--date", DATE,
                "--reason", "the round-one rejection was recorded twice",
                "--authorised-by", OPERATOR, "--boundary", "operator console", *narrowing)


def _retired(root: Path) -> list[tuple[str, str]]:
    """(unit, brief) of every row `critic.py show --format json` reads as superseded."""
    out = _cli(root, "show", "--format", "json")
    return [(r["unit"], r["brief"]) for r in json.loads(out.stdout) if r["superseded"]]


class SupersedeByBriefTests(unittest.TestCase):

    def test_brief_retires_exactly_the_named_row(self) -> None:
        """Fails if `--brief` does not narrow (exit 2), or if the record omits `row-brief` or
        the join ignores it (both rows retired, so the unit has no live verdict)."""
        for retire, keep in ((SECOND, FIRST), (FIRST, SECOND)):
            with self.subTest(retire=retire), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                path = _seed(root, _row(FIRST, "[new] AC3 is false"),
                             _row(SECOND, "[new] AC7 is false"),
                             _row(SECOND, "[new] another unit", unit="BG0963"))
                done = _supersede(root, "--reviewer", REVIEWER, "--verdict", "REJECT",
                                  "--brief", retire)
                self.assertEqual(done.returncode, 0, done.stderr)
                self.assertIn(retire, done.stdout)
                self.assertIn(f"row-brief={retire} ", path.read_text(encoding="utf-8"))
                self.assertEqual(_retired(root), [(UNIT, retire)])
                live = json.loads(_cli(root, "show", "--unit", UNIT, "--format",
                                       "json").stdout)["verdict"]
                self.assertEqual((live["brief"], live["superseded"]), (keep, False))
                self.assertEqual([r["brief"] for r in critic.standing_rejects(root, UNIT)],
                                 [keep])

    def test_each_row_can_be_retired_by_its_own_record(self) -> None:
        """Fails if the join keeps only the first record under a unit, date, verdict and
        reviewer, so the second record, naming the other brief, retires nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root, _row(FIRST, "[new] AC3"), _row(SECOND, "[new] AC7"))
            for brief in (SECOND, FIRST):
                self.assertEqual(_supersede(root, "--brief", brief).returncode, 0)
            self.assertEqual(_retired(root), [(UNIT, FIRST), (UNIT, SECOND)])

    def test_without_brief_the_record_is_written_as_before(self) -> None:
        """Fails if `row-brief` is written when `--brief` is not given."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _seed(root, _row(FIRST, "[new] AC3"))
            self.assertEqual(_supersede(root).returncode, 0)
            text = path.read_text(encoding="utf-8")
            self.assertIn("row-author=engineering-seat-triage authorised-by=", text)
            self.assertNotIn("row-brief=", text)
            self.assertEqual(_retired(root), [(UNIT, FIRST)])

    def test_the_ambiguous_refusal_names_each_fingerprint(self) -> None:
        """The bug's own reproduction. Fails if the refusal names no fingerprint or does not
        offer `--brief`, or if anything is written."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _seed(root, _row(FIRST, "[new] AC3"), _row(SECOND, "[new] AC7"))
            before = path.read_text(encoding="utf-8")
            done = _supersede(root, "--reviewer", REVIEWER, "--verdict", "REJECT")
            self.assertEqual(done.returncode, 2)
            self.assertIn(f"brief fingerprints {FIRST}, {SECOND}", done.stderr)
            self.assertIn("narrow it with --brief", done.stderr)
            self.assertEqual(path.read_text(encoding="utf-8"), before)

    def test_a_brief_that_still_matches_several_rows_is_refused(self) -> None:
        """Fails if the first of two same-fingerprint rows is retired instead of refused."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _seed(root, _row(SECOND, "[new] AC7"), _row(SECOND, "[new] AC7 again"))
            before = path.read_text(encoding="utf-8")
            done = _supersede(root, "--reviewer", REVIEWER, "--verdict", "REJECT",
                              "--brief", SECOND)
            self.assertEqual(done.returncode, 2)
            self.assertIn(f"brief fingerprints {SECOND}, {SECOND}", done.stderr)
            self.assertIn("no record can retire one of them alone", done.stderr)
            self.assertEqual(path.read_text(encoding="utf-8"), before)
            self.assertEqual(_retired(root), [])

    def test_a_near_miss_fingerprint_is_refused_and_case_is_not_a_miss(self) -> None:
        """Fails if the fingerprint is matched by prefix or containment, or case-sensitively."""
        for near in (SECOND[:6], SECOND + "0", "x" + SECOND):
            with self.subTest(brief=near), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                path = _seed(root, _row(FIRST, "[new] AC3"), _row(SECOND, "[new] AC7"))
                before = path.read_text(encoding="utf-8")
                self.assertEqual(_supersede(root, "--brief", near).returncode, 2)
                self.assertEqual(path.read_text(encoding="utf-8"), before)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root, _row(FIRST, "[new] AC3"), _row(SECOND, "[new] AC7"))
            done = _supersede(root, "--brief", SECOND.upper())
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(_retired(root), [(UNIT, SECOND)])

    def test_a_dash_names_the_row_with_no_brief(self) -> None:
        """Fails if `-` does not read as an absent brief, on the writer or the join."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root, _row("-", "[new] hand-written prompt"), _row(SECOND, "[new] AC7"))
            refused = _supersede(root, "--verdict", "REJECT")
            self.assertIn(f"brief fingerprints -, {SECOND}", refused.stderr)
            done = _supersede(root, "--brief", "-")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(_retired(root), [(UNIT, "-")])

    def test_a_dash_names_a_pre_brief_row(self) -> None:
        """A six-column row from before the Brief column parses with an empty brief. Fails if
        `-` is matched against the cell's text alone, so that row cannot be named."""
        pre_brief = (f"| {UNIT} | REJECT | {REVIEWER} | engineering-seat-triage | {DATE} "
                     f"| [new] old |\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed(root, pre_brief, _row(SECOND, "[new] AC7"))
            refused = _supersede(root, "--verdict", "REJECT")
            self.assertIn(f"brief fingerprints -, {SECOND}", refused.stderr)
            done = _supersede(root, "--brief", "-")
            self.assertEqual(done.returncode, 0, done.stderr)
            self.assertEqual(_retired(root), [(UNIT, "")])

    def test_a_record_without_a_brief_still_retires_every_row_it_names(self) -> None:
        """The ledger's records predate `row-brief`. Fails if an absent field is read as naming
        an empty brief, so a recorded supersession silently stops retiring its row."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _seed(root, _row(FIRST, "[new] AC3"), _row(SECOND, "[new] AC7"))
            with path.open("a", encoding="utf-8") as fh:
                fh.write(f"\n{critic.SUPERSEDE_HEADING}\n\nSUPERSEDED unit={UNIT} "
                         f"row-date={DATE} row-verdict=REJECT row-reviewer={REVIEWER} "
                         f"row-author=engineering-seat-triage authorised-by={OPERATOR} "
                         f"boundary=operator console reason=both rows "
                         f"recorded=2026-10-27\n")
            self.assertEqual(_retired(root), [(UNIT, FIRST), (UNIT, SECOND)])
            self.assertEqual(critic.read_supersessions(root)[0]["row_brief"], "")


if __name__ == "__main__":
    unittest.main()
