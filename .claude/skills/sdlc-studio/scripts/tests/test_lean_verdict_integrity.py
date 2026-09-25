"""US0873: a verdict is written by one set of rules, and parallel writers never lose a row.

The vocabulary tests drive `transition.py set` through `transition.main`, the surface an agent
invokes. The concurrency tests run eight writers on threads with a delay injected inside the
critical section, so a writer that does not hold the lock loses rows every time rather than
only when the scheduler happens to interleave them. Every workspace is a temporary directory.
"""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import artifact  # noqa: E402
import critic  # noqa: E402
import transition  # noqa: E402
import verify_ac  # noqa: E402
from lib import sdlc_md  # noqa: E402

WRITERS = 8


def _bug(root: Path, refused: bool = False) -> Path:
    """A bug that reaches Fixed; with `refused`, its one criterion is unticked and carries no
    `Verify:`, so nothing speaks for the fix and the gated transition refuses it."""
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    path = bugs / "BG0001-x.md"
    box = " " if refused else "x"
    path.write_text("# BG0001: a\n\n> **Status:** In Progress\n\n\n## Acceptance Criteria\n\n"
                    f"- [{box}] the unit behaves\n", encoding="utf-8")
    (bugs / "_index.md").write_text("# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                                    "| [BG0001](BG0001-x.md) | a | In Progress |\n",
                                    encoding="utf-8")
    return path


def _set(root: Path, *argv: str) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = transition.main(["set", "--id", "BG0001", *argv, "--root", str(root)])
    return rc, buf.getvalue()


def _run_together(n: int, fn) -> None:
    """Start `n` calls of `fn(i)` at one barrier and wait for all of them."""
    barrier = threading.Barrier(n)
    errors: list[BaseException] = []

    def one(i: int) -> None:
        barrier.wait()
        try:
            fn(i)
        except BaseException as exc:  # noqa: BLE001 - surfaced below
            errors.append(exc)

    threads = [threading.Thread(target=one, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    if errors:
        raise errors[0]


def _slow(real):
    """`real`, entered only after a pause: widens the read-to-write window a lock must cover."""
    def slow(*args, **kwargs):
        time.sleep(0.05)
        return real(*args, **kwargs)
    return slow


class VerdictVocabularyTests(unittest.TestCase):
    def test_an_unknown_verdict_word_is_refused(self) -> None:
        """AC1. MUTANT: drop the vocabulary check in `transition.cmd_set`, so `lgtm` is written
        to the ledger and the bug moves to Fixed. The control: APPROVE through the same call
        is accepted."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _bug(root)
            for argv in (("--reviewer", "rev", "--author", "dev"), ()):
                with self.subTest(argv=argv):
                    rc, out = _set(root, "--status", "Fixed", "--verdict", "lgtm", *argv)
                    self.assertEqual(rc, 2, out)
                    self.assertIn("APPROVE", out)
                    self.assertIn("REJECT", out)
                    self.assertFalse(critic.verdicts_path(root).exists(), "a row was written")
                    self.assertIn("> **Status:** In Progress", path.read_text(encoding="utf-8"))
            rc, out = _set(root, "--status", "Fixed", "--verdict", "approve",
                           "--reviewer", "rev", "--author", "dev")
            self.assertEqual(rc, 0, out)
            self.assertEqual([r["verdict"] for r in critic.read_verdicts(root)], ["APPROVE"])

    def test_a_refused_transition_leaves_no_verdict(self) -> None:
        """AC2. MUTANT: drop the withdrawal in `critic.provisional_verdict`, so the APPROVE
        written before the gated transition outlives its refusal. Both shapes: a ledger the
        verdict created is removed, and a ledger that held other rows is left byte-identical."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _bug(root, refused=True)
            # nothing speaks for the fix, so the criteria floor refuses Fixed
            rc, out = _set(root, "--status", "Fixed", "--verdict", "APPROVE",
                           "--reviewer", "rev", "--author", "dev")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("> **Status:** In Progress", path.read_text(encoding="utf-8"))
            self.assertFalse(critic.verdicts_path(root).exists(), "the refused close left a row")

            critic.record_verdict(root, "US0009", "APPROVE", "rev", "dev")
            before = critic.verdicts_path(root).read_bytes()
            rc, out = _set(root, "--status", "Fixed", "--verdict", "APPROVE",
                           "--reviewer", "rev", "--author", "dev")
            self.assertNotEqual(rc, 0, out)
            self.assertEqual(critic.verdicts_path(root).read_bytes(), before)

    def test_a_withdrawal_keeps_another_writers_rows(self) -> None:
        """AC2 with a second writer. MUTANT: withdraw by truncating the ledger back to the
        bytes it held before the verdict was written, so a row another writer appended while
        the close ran, and a supersession section written below the table, are lost with it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _bug(root, refused=True)
            real = transition.transition

            def interleaved(*args, **kwargs):
                critic.record_verdict(root, "US0042", "REJECT", "other", "dev2", issues="#1 x")
                ledger = critic.verdicts_path(root)
                ledger.write_text(ledger.read_text(encoding="utf-8") + "\n"
                                  + critic.SUPERSEDE_HEADING + "\n\nnone yet\n",
                                  encoding="utf-8")
                return real(*args, **kwargs)

            with mock.patch.object(transition, "transition", side_effect=interleaved):
                rc, out = _set(root, "--status", "Fixed", "--verdict", "APPROVE",
                               "--reviewer", "rev", "--author", "dev")
            self.assertNotEqual(rc, 0, out)
            self.assertIn("> **Status:** In Progress", path.read_text(encoding="utf-8"))
            rows = [(r["unit"], r["verdict"]) for r in critic.read_verdicts(root)]
            self.assertEqual(rows, [("US0042", "REJECT")])
            self.assertIn(critic.SUPERSEDE_HEADING,
                          critic.verdicts_path(root).read_text(encoding="utf-8"))

    def test_a_raise_after_the_status_write_keeps_the_verdict(self) -> None:
        """AC2's limit: a verdict is withdrawn only while the transition has not landed.
        MUTANT: withdraw on any raise, so a close whose status write landed and whose index
        sync (or an interrupt) then raised leaves a Fixed bug with no verdict row."""
        for raised in (ValueError("the index sync failed"), KeyboardInterrupt()):
            with self.subTest(raised=type(raised).__name__), \
                    tempfile.TemporaryDirectory() as d:
                root = Path(d)
                path = _bug(root)
                with mock.patch.object(transition.reconcile, "apply_type",
                                       side_effect=raised):
                    try:
                        rc, out = _set(root, "--status", "Fixed", "--verdict", "APPROVE",
                                       "--reviewer", "rev", "--author", "dev")
                        self.assertNotEqual(rc, 0, out)
                    except KeyboardInterrupt:
                        self.assertIsInstance(raised, KeyboardInterrupt)
                self.assertIn("> **Status:** Fixed", path.read_text(encoding="utf-8"),
                              "premise: the status write landed")
                self.assertEqual([(r["unit"], r["verdict"]) for r in critic.read_verdicts(root)],
                                 [("BG0001", "APPROVE")])

    def test_the_artifact_close_refuses_an_unknown_verdict_word(self) -> None:
        """Every writer holds the vocabulary. MUTANT: drop the check in
        `critic._write_verdict`, so `artifact.py close --verdict lgtm` writes a row no gate
        matches. Nothing is written: no ledger, no status change. The control:
        APPROVE through the same close is recorded."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = _bug(root)
            before = path.read_bytes()

            def close(word: str) -> tuple[int, str]:
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    rc = artifact.main(["close", "--id", "BG0001",
                                        "--verdict", word, "--reviewer", "rev",
                                        "--author", "dev", "--root", str(root)])
                return rc, buf.getvalue()

            rc, out = close("lgtm")
            self.assertEqual(rc, 2, out)
            self.assertIn("APPROVE", out)
            self.assertFalse(critic.verdicts_path(root).exists(), "a row was written")
            self.assertEqual(path.read_bytes(), before, "the artefact was written")
            rc, out = close("APPROVE")
            self.assertEqual(rc, 0, out)
            self.assertEqual([r["verdict"] for r in critic.read_verdicts(root)], ["APPROVE"])


class LedgerConcurrencyTests(unittest.TestCase):
    def test_concurrent_verdicts_are_all_kept(self) -> None:
        """AC3. MUTANT: take no lock round the ledger write. With the pause inside the
        critical section, an unlocked writer loses rows: every creator writes the header over
        the others' rows, and every inserting writer writes back a ledger read before the others
        appended. (The atomic rewrite guards a crash mid-write, which this test does not stage.)"""
        for seeded in (False, True):
            with self.subTest(seeded=seeded), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                stories = root / "sdlc-studio" / "stories"
                stories.mkdir(parents=True)
                for i in range(WRITERS):
                    (stories / f"US010{i}-u.md").write_text(
                        f"# US010{i}: u\n\n> **Status:** Review\n", encoding="utf-8")
                (root / "sdlc-studio" / ".config.yaml").write_text(
                    "review:\n  require_brief_provenance: false\n", encoding="utf-8")
                if seeded:
                    # a supersession section below the table: rows are then inserted by a
                    # read-modify-write rather than appended
                    critic.record_verdict(root, "US0999", "APPROVE", "rev", "dev")
                    ledger = critic.verdicts_path(root)
                    ledger.write_text(ledger.read_text(encoding="utf-8") + "\n"
                                      + critic.SUPERSEDE_HEADING + "\n\nnone yet\n",
                                      encoding="utf-8")

                def record(i: int) -> None:
                    rc = critic.main(["record", "--unit", f"US010{i}", "--verdict", "APPROVE",
                                      "--reviewer", "rev", "--author", "dev",
                                      "--root", str(root)])
                    assert rc == 0, rc

                with contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()) as err, \
                        mock.patch.object(critic, "_header", _slow(critic._header)), \
                        mock.patch.object(sdlc_md, "atomic_write", _slow(sdlc_md.atomic_write)):
                    _run_together(WRITERS, record)
                    rows = critic.read_verdicts(root)
                self.assertNotIn("malformed", err.getvalue())
                units = sorted(sdlc_md.norm_id(r["unit"]) for r in rows)
                self.assertEqual(units, sorted([f"US010{i}" for i in range(WRITERS)]
                                               + (["US0999"] if seeded else [])))
                text = critic.verdicts_path(root).read_text(encoding="utf-8")
                self.assertEqual(text.count("| Unit | Verdict |"), 1, text)

    def test_concurrent_verify_reports_are_all_kept(self) -> None:
        """AC4. MUTANT: take no lock round the report's read-merge-write. Every unlocked
        writer merges into a report read before the others wrote, so the last one to write
        keeps only its own entry. (The atomic write guards a crash mid-write, not staged here.)"""
        with tempfile.TemporaryDirectory() as d:
            report = Path(d) / "sdlc-studio" / ".local" / "verify-report.json"

            def write(i: int) -> None:
                verify_ac.write_report(report, [verify_ac.StoryReport(
                    path=f"sdlc-studio/stories/US020{i}-u.md", ac_count=1, verified=1)])

            with mock.patch.object(sdlc_md, "atomic_write", _slow(sdlc_md.atomic_write)):
                _run_together(WRITERS, write)
            stories = json.loads(report.read_text(encoding="utf-8"))["stories"]
            self.assertEqual(sorted(stories), [f"US020{i}-u" for i in range(WRITERS)])


if __name__ == "__main__":
    unittest.main()
