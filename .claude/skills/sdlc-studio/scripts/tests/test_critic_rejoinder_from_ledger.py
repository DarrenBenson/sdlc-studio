"""US1016: `critic.py brief --rejoinder` with no file quotes the seat's standing REJECT from the
verdict ledger.

The REJECT is the briefed seat's unanswered one in the unit's current delivery. A row bound to
the file its brief issued is quoted from that file's bytes, found through the row's `Source`
cell; a transcribed row is rebuilt from its cells and labelled as a rebuild. No such REJECT is
a refusal naming the unit and the seat, before anything reaches stdout.

Every case drives `critic.py` through its entry point in a throwaway project, from a working
directory that is not the project root.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")

UNIT = "US0001"
REBUILT_LABEL = "rebuilt from the ledger's fields"
FINGERPRINT = re.compile(r"^brief fingerprint: (\S+)$", re.M)


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, engineering: bool = False) -> None:
    """One story with a QA seat card (and an engineering one), in a throwaway project."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    if engineering:
        _write(root, "sdlc-studio/personas/seats/engineering.md",
               "<!-- role: engineering -->\n# Priya - Engineering amigo\n\ncharter\n")
    _write(root, f"sdlc-studio/stories/{UNIT}-widget.md",
           f"# {UNIT}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
           "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
           "- **Verify:** shell true\n")


def _critic(cwd: Path, root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args, "--root", str(root)],
                          cwd=cwd, capture_output=True, text=True, timeout=300,
                          env=gitutil.git_env(), check=False)


def _brief(cwd: Path, root: Path, *extra: str, seat: str = "qa") -> subprocess.CompletedProcess:
    return _critic(cwd, root, "brief", "--unit", UNIT, "--seat", seat, *extra)


def _issued(r: subprocess.CompletedProcess) -> tuple[Path, list[str]]:
    """The verdict file a brief issued and its footer's record command as argv."""
    assert r.returncode == 0, r.stderr
    tail = r.stdout[r.stdout.rindex(critic._RETURN_CONTRACT):]
    path = next(Path(ln.strip()) for ln in tail.splitlines() if ln.strip().endswith(".txt"))
    m = re.search(r"record the verdict with:\s+critic\.py (record .*)$", r.stderr, re.M)
    assert m, r.stderr
    return path, [a for a in shlex.split(m.group(1)) if a != "..."]


def _record(cwd: Path, root: Path, *argv: str, reviewer: str = "qa-seat") -> None:
    r = _critic(cwd, root, *argv, "--reviewer", reviewer, "--author", "builder")
    assert r.returncode == 0, r.stderr


def _transcribe(cwd: Path, root: Path, verdict: str, issues: str, reviewer: str) -> None:
    _record(cwd, root, "record", "--unit", UNIT, "--verdict", verdict, "--issues", issues,
            reviewer=reviewer)


def _quote(stdout: str) -> tuple[str, str]:
    """(the line introducing the prior verdict, the quoted block) beneath the RE-REVIEW mark."""
    after = stdout.split(critic._REJOINDER_MARK, 1)[1]
    intro, rest = after.split("Your prior verdict", 1)[1].split("\n", 1)
    return intro, rest.split("The author's repairs summary", 1)[0].strip()


class RejoinderFromLedgerTests(unittest.TestCase):

    def test_the_ledger_rejoinder_quotes_the_issued_file_verbatim(self) -> None:
        """AC1. Mutants: quoting the row's issues cell instead of the stored file; the newest file
        in the unit's folder in place of the one `Source` names; fingerprinting the quoted prior
        verdict as well as the base brief; `ledger` read as a file name."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            path, argv = _issued(_brief(cwd, root))
            written = (f"UNIT: {UNIT}\nBRIEF: {path.stem}\n"
                       "I ran the Verify line and read src/widget.py; only the file holds this.\n\n"
                       "VERDICT: REJECT\n"
                       "ISSUES: [new] the widget returns 1 (src/widget.py:2);\n"
                       "        [pre-existing] BG0001 the gate is slow\n"
                       "BLOCKING: [new] the widget returns 1\n")
            path.write_text(written, encoding="utf-8")
            _record(cwd, root, *argv)
            self.assertTrue(critic.read_verdicts(root)[-1]["source"].endswith(path.name))
            # A later brief's file, written and never recorded: the folder's newest, never quoted.
            plain = _brief(cwd, root)
            decoy, _ = _issued(plain)
            self.assertRegex(plain.stderr, r"--rejoinder\b", "a plain brief names the rejoinder")
            decoy.write_text(f"UNIT: {UNIT}\nBRIEF: {decoy.stem}\nVERDICT: REJECT\n"
                             "ISSUES: [new] a decoy finding (src/widget.py:1)\n"
                             "BLOCKING: [new] a decoy finding\n", encoding="utf-8")
            outs = {}
            for spelling in ((), ("ledger",), (str(path),)):
                r = _brief(cwd, root, "--rejoinder", *spelling)
                self.assertEqual(0, r.returncode, f"--rejoinder {spelling}: {r.stderr}")
                fp = FINGERPRINT.search(r.stderr)
                self.assertIsNotNone(fp, r.stderr)
                outs[spelling] = (critic.strip_verdict_file(r.stdout), fp.group(1))
            text, fp = outs[()]
            intro, quoted = _quote(text)
            want = critic._VERDICT_HEADER_RE.sub("", written, count=1).strip()
            self.assertEqual(want, quoted, "the issued file's bytes, verbatim")
            self.assertIn("verbatim", intro)
            self.assertNotIn(REBUILT_LABEL, text)
            self.assertNotIn("decoy", text)
            self.assertEqual(outs[(str(path),)], outs[()],
                             "the brief and fingerprint `--rejoinder <that file>` prints")
            self.assertEqual(outs[("ledger",)], outs[()], "`ledger` is the bare flag's spelling")
            self.assertEqual(critic.rejoinder_fingerprint(text), fp)
            # A file edited since it was recorded no longer holds what the row was read from: the
            # quote is rebuilt from the row, labelled so, and the notice says why.
            path.write_text(written.replace("only the file holds this", "edited"), encoding="utf-8")
            r = _brief(cwd, root, "--rejoinder")
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertIn(REBUILT_LABEL, _quote(r.stdout)[0])
            self.assertNotIn("edited", r.stdout)
            self.assertIn("changed since it was recorded", r.stderr)

    def test_a_transcribed_reject_is_rebuilt_from_its_cells_and_labelled(self) -> None:
        """AC2. Mutants: dropping the BLOCKING findings the issues cell carries (or all but the
        first); a RULINGS item quoted as a finding; the rebuild introduced as verbatim."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            issues = ("BLOCKING: [new] first defect in `w()\\; again`\\; see src/widget.py:2; "
                      "[pre-existing] BG0001 the gate is slow; "
                      "BLOCKING: [regression] second defect (src/widget.py:1); "
                      "RULINGS: the earlier note CLOSED")
            _transcribe(cwd, root, "REJECT", issues, "qa-seat")
            row = critic.read_verdicts(root)[-1]
            self.assertEqual("-", row["source"])
            r = _brief(cwd, root, "--rejoinder")
            self.assertEqual(0, r.returncode, r.stderr)
            intro, quoted = _quote(r.stdout)
            self.assertIn(REBUILT_LABEL, intro)
            self.assertNotIn("verbatim", intro, "a rebuild is not the reviewer's own words")
            self.assertRegex(quoted, r"(?m)^VERDICT: REJECT$")
            blocking = critic._block_field(quoted, "BLOCKING")
            self.assertIn("[new] first defect", blocking)
            self.assertIn("[regression] second defect", blocking)
            self.assertNotIn("BG0001", blocking)
            self.assertEqual("the earlier note CLOSED", critic._block_field(quoted, "RULINGS"))
            self.assertEqual(1, quoted.count("RULINGS:"), "a RULINGS item is no finding")
            # The rebuild reads back as the row it came from: every finding, its tag and its
            # blocking mark, in order, and the rulings kept as rulings.
            verdict, parsed = critic.parse_verdict_block(quoted)
            self.assertEqual("REJECT", verdict)

            def items(cell: str) -> list[str]:
                return critic.split_items(critic._unescape_outside_spans(cell))
            self.assertEqual(items(row["issues"]), items(parsed))

    def test_no_unanswered_reject_for_the_seat_is_refused(self) -> None:
        """AC3. Mutants: choosing with `standing_rejects` (the latest REJECT although answered);
        falling back to another seat's REJECT; reading rows from an earlier delivery; printing
        the brief before refusing."""
        def refused(cwd: Path, root: Path, why: str) -> None:
            r = _brief(cwd, root, "--rejoinder")
            self.assertEqual(2, r.returncode, f"{why}: {r.stdout[-300:]}")
            self.assertEqual("", r.stdout, why)
            self.assertIn(UNIT, r.stderr, why)
            self.assertRegex(r.stderr, r"\bqa\b", why)

        def quoted(cwd: Path, root: Path, why: str, seat: str = "qa") -> None:
            r = _brief(cwd, root, "--rejoinder", seat=seat)
            self.assertEqual(0, r.returncode, f"{why}: {r.stderr}")
            self.assertIn("VERDICT: REJECT", _quote(r.stdout)[1], why)

        reject = "BLOCKING: [new] the widget returns 1 (src/widget.py:2)"
        with tempfile.TemporaryDirectory() as elsewhere:
            cwd = Path(elsewhere)
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root)
                refused(cwd, root, "nothing recorded")
                _transcribe(cwd, root, "REJECT", reject, "qa-seat")
                quoted(cwd, root, "control: the seat's REJECT stands")
                _transcribe(cwd, root, "APPROVE", "none", "qa-seat")
                refused(cwd, root, "the seat's REJECT answered by its APPROVE")
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, engineering=True)
                _transcribe(cwd, root, "APPROVE", "none", "qa-seat")
                _transcribe(cwd, root, "REJECT", reject, "engineering-seat")
                refused(cwd, root, "only another seat's REJECT stands")
                quoted(cwd, root, "control: that seat's own rejoinder", seat="engineering")
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _project(root, engineering=True)
                row = "| {u} | {v} | {who} | builder | 2026-11-0{n} | - | full | - | {i} |\n"
                rows = [row.format(u=UNIT, v="REJECT", who="qa-seat", n=1, i=reject),
                        row.format(u=UNIT, v="APPROVE", who="engineering-seat", n=2, i="none")]
                ledger = critic.verdicts_path(root)
                _write(root, str(ledger.relative_to(root)), critic._TABLE + "".join(rows))
                quoted(cwd, root, "control: the REJECT is in the current delivery")
                _write(root, str(ledger.relative_to(root)), critic._TABLE + "".join(rows) +
                       row.format(u=UNIT, v="APPROVE", who="engineering-seat", n=3, i="none"))
                refused(cwd, root, "the seat's REJECT is from an earlier delivery")

    def test_a_carried_units_earlier_reject_is_quoted(self) -> None:
        """A unit carried at the review cap is briefed again in a later run, whose delivery holds
        no row of it yet: the rejoinder quotes the seat's unanswered REJECT from the run that
        carried it, the one `standing_rejects` (what `sprint plan` reports) names. Mutants:
        reading the current delivery alone (the refusal this pins); reading every delivery for
        a unit nobody carried; the latest REJECT although its seat answered it; another seat's
        REJECT quoted for this one."""
        def brief(cwd: Path, root: Path, seat: str = "qa") -> subprocess.CompletedProcess:
            return _brief(cwd, root, "--rejoinder", seat=seat)

        first = "BLOCKING: [new] the widget returns 1 (src/widget.py:2)"
        second = "BLOCKING: [new] the widget still returns 1 (src/widget.py:2)"
        row = "| {u} | {v} | {who} | builder | 2026-11-0{n} | - | full | - | {i} |\n"
        rows = [row.format(u=UNIT, v="REJECT", who="qa-seat", n=1, i=first),
                row.format(u=UNIT, v="REJECT", who="qa-seat", n=2, i=second)]
        rs = critic.run_state
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root, engineering=True)
            _write(root, "sdlc-studio/bugs/BG0001-carried-findings.md",
                   "# BG0001: carried findings\n\n> **Status:** Open\n")
            ledger = critic.verdicts_path(root)
            _write(root, str(ledger.relative_to(root)), critic._TABLE + "".join(rows))

            def carried_from(reason: str) -> None:
                rs.archive(root, {"run_id": "RUN-0000EARL", "outcome": "goal-reached",
                                  "batch": [], "batch_changes": [
                                      {"action": "drop", "id": UNIT, "reason": reason}]})

            carried_from(f"{critic.CARRIED_REASON}: BG0001")
            rs.open_run(root, batch=[UNIT], goal="deliver the carried unit")
            rs.mark_review_base(root, UNIT, len(rows))
            self.assertEqual([], critic.delivery_rounds(root, UNIT),
                             "premise: the later run's delivery holds no row of the unit")
            self.assertEqual("BG0001", critic.carried_by(root, UNIT), "premise: carried")
            standing = {r["reviewer"] for r in critic.standing_rejects(root, UNIT)}
            self.assertEqual({"qa-seat"}, standing,
                             "premise: the close-requirement reader names the REJECT")
            r = brief(cwd, root)
            self.assertEqual(0, r.returncode, r.stderr)
            intro, quoted = _quote(r.stdout)
            self.assertIn(REBUILT_LABEL, intro)
            self.assertRegex(quoted, r"(?m)^VERDICT: REJECT$")
            self.assertIn("still returns 1", critic._block_field(quoted, "BLOCKING"),
                          "the seat's latest unanswered REJECT")
            # Another seat holds no REJECT, carried or not: refused, naming the unit.
            other = brief(cwd, root, seat="engineering")
            self.assertEqual(2, other.returncode, other.stdout[-300:])
            self.assertEqual("", other.stdout)
            self.assertIn(UNIT, other.stderr)
            # A drop that is no carry leaves the earlier delivery closed to the rejoinder.
            carried_from("dropped by hand")
            self.assertIsNone(critic.carried_by(root, UNIT), "premise: no longer carried")
            plain = brief(cwd, root)
            self.assertEqual(2, plain.returncode, plain.stdout[-300:])
            self.assertEqual("", plain.stdout)
            # The seat's APPROVE discharges the carry: nothing stands to quote.
            carried_from(f"{critic.CARRIED_REASON}: BG0001")
            _write(root, str(ledger.relative_to(root)), critic._TABLE + "".join(rows) +
                   row.format(u=UNIT, v="APPROVE", who="qa-seat", n=3, i="none"))
            answered = brief(cwd, root)
            self.assertEqual(2, answered.returncode, answered.stdout[-300:])
            self.assertEqual("", answered.stdout)
            self.assertRegex(answered.stderr, r"\bqa\b")


if __name__ == "__main__":
    unittest.main()
