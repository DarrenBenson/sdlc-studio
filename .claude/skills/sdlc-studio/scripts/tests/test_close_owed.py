"""The close-owed detector: is a sprint close owed right now?

The load-bearing cases are not "no retros at all" - they are the partial ones a real project
hits: a terminal unit some retro DID account for (covered, not owed), the historical tail a
baseline forgives (grandfathered, not owed), and the one that matters - a unit closed AFTER
adoption that no retro names (owed, and must be caught). A detector that only fired on an empty
project would never fire in practice, because the failure mode is shipping Done work and skipping
the retro, not omitting the work.
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import close_owed  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _story(root: Path, sid: str, status: str) -> None:
    _write(root / "sdlc-studio" / "stories" / f"{sid}-s.md",
           f"# {sid}: A story\n\n> **Status:** {status}\n> **Epic:** EP0100\n> **Points:** 2\n")


def _bug(root: Path, bid: str, status: str) -> None:
    _write(root / "sdlc-studio" / "bugs" / f"{bid}-b.md",
           f"# {bid}: A bug\n\n> **Status:** {status}\n> **Points:** 2\n")


def _retro(root: Path, rid: str, batch: str) -> None:
    _write(root / "sdlc-studio" / "retros" / f"{rid}-r.md",
           f"# RETRO-{rid[5:]}: a sprint\n\n> **Batch:** {batch}\n\n## Delivered\n- shipped\n")


class CloseOwedBase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sdlc-studio" / "retros").mkdir(parents=True)
        self.addCleanup(self.tmp.cleanup)


class UnbaselinedTests(CloseOwedBase):
    def test_unbaselined_reports_every_uncovered_terminal_unit(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        report = close_owed.owed(self.root)
        self.assertFalse(report["baselined"])
        ids = {cid for cid, _ in report["owed"]}
        self.assertEqual(ids, {"US0001", "BG0001"})

    def test_non_terminal_units_are_never_owed(self) -> None:
        _story(self.root, "US0001", "In Progress")
        _story(self.root, "US0002", "Draft")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_detect_exit_zero_when_unbaselined_even_with_uncovered(self) -> None:
        _story(self.root, "US0001", "Done")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = close_owed.main(["--root", str(self.root), "detect", "--format", "json"])
        self.assertEqual(rc, 0)  # unbaselined is a soft state, not a gate failure


class CoverageTests(CloseOwedBase):
    def test_a_retro_that_names_the_unit_makes_it_covered(self) -> None:
        _story(self.root, "US0001", "Done")
        _retro(self.root, "RETRO0001", "US0001")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])
        self.assertEqual(close_owed.owed(self.root)["covered"], 1)


class BaselineTests(CloseOwedBase):
    def test_baseline_grandfathers_the_existing_tail(self) -> None:
        _story(self.root, "US0001", "Done")
        _bug(self.root, "BG0001", "Fixed")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        report = close_owed.owed(self.root)
        self.assertTrue(report["baselined"])
        self.assertEqual(report["owed"], [])
        self.assertEqual(report["grandfathered"], 2)

    def test_a_higher_id_closed_after_the_baseline_is_owed(self) -> None:
        _story(self.root, "US0001", "Done")  # pre-adoption tail
        close_owed.stamp_baseline(self.root, date="2026-01-01")  # cutoff US=1
        _story(self.root, "US0005", "Done")  # later work, no retro
        report = close_owed.owed(self.root)
        self.assertEqual({cid for cid, _ in report["owed"]}, {"US0005"})
        self.assertEqual(report["grandfathered"], 1)

    def test_later_work_covered_by_a_retro_is_not_owed(self) -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _story(self.root, "US0005", "Done")
        _retro(self.root, "RETRO0002", "US0005")
        self.assertEqual(close_owed.owed(self.root)["owed"], [])

    def test_detect_exits_nonzero_when_a_close_is_owed(self) -> None:
        _story(self.root, "US0001", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        _story(self.root, "US0005", "Done")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = close_owed.main(["--root", str(self.root), "detect", "--format", "json"])
        self.assertEqual(rc, 1)

    def test_lower_id_in_flight_at_baseline_owes_when_it_later_closes(self) -> None:
        # The BLOCKER the set model fixes: a unit NON-terminal at baseline (a lower id) that closes
        # later must be owed, never silently forgiven. A highest-id cutoff would grandfather it.
        _story(self.root, "US0100", "Done")   # high id, terminal at baseline
        _story(self.root, "US0050", "Draft")  # in flight, lower id, NOT terminal at baseline
        close_owed.stamp_baseline(self.root, date="2026-01-01")  # forgives only {US0100}
        _story(self.root, "US0050", "Done")   # closes later, no retro -> must be owed
        report = close_owed.owed(self.root)
        self.assertEqual({cid for cid, _ in report["owed"]}, {"US0050"})

    def test_ulid_ids_are_grandfathered_by_set_membership(self) -> None:
        # Schema-v3 ULID ids have no numeric value; a highest-id cutoff broke entirely on them
        # (baseline empty -> everything owed forever). Set membership forgives them correctly.
        _story(self.root, "US-01JQK3F8AAZ8QK", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01")
        report = close_owed.owed(self.root)
        self.assertEqual(report["owed"], [])
        self.assertEqual(report["grandfathered"], 1)

    def test_exclude_holds_named_ids_to_a_close_at_stamp_time(self) -> None:
        _story(self.root, "US0001", "Done")
        _story(self.root, "US0002", "Done")
        close_owed.stamp_baseline(self.root, date="2026-01-01", exclude={"US0002"})
        report = close_owed.owed(self.root)
        self.assertEqual({cid for cid, _ in report["owed"]}, {"US0002"})


if __name__ == "__main__":
    unittest.main()
