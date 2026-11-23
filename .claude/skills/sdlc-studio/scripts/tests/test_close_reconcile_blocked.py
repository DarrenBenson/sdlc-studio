"""BG1551: a sprint close does not refuse over a drift item that awaits someone's decision.

`reconcile.epic_terminal_undelivered_drift` reports a Done epic none of whose stories was
delivered, carrying `blocked_by` because its owner decides whether it moves or stays; the commit
gate's tally reports such an item without counting it. The close exempted only gate-blocked
request-derivable items, so it refused over the epic in its reconcile step and again in its
final check, naming `reconcile.py apply`, which never rewrites a terminal epic, and one
undecided epic held every later close. Each test drives `sprint._close_reconcile` or the close
tail `sprint._apply_signoff_tail` over the reviewer's fixture: a Done epic over one Superseded
and one Won't Implement story.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import loader  # noqa: E402 - the canonical way to import a script under test

sprint = loader.load_script("sprint")
reconcile = sprint.reconcile


def _quiet(fn, *args, **kwargs):
    """`fn(*args, **kwargs)` with its printing captured: (result, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        result = fn(*args, **kwargs)
    return result, out.getvalue(), err.getvalue()


class CloseReconcileBlockedTests(unittest.TestCase):

    def setUp(self) -> None:
        # The close tail imports reconcile locally, so it reads `sys.modules["reconcile"]`, which
        # another test module may replace with its own copy when it is collected after this one.
        # Hold the entry to the module sprint bound, so a patch here is the one the tail sees.
        held = unittest.mock.patch.dict(sys.modules, {"reconcile": reconcile})
        held.start()
        self.addCleanup(held.stop)
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.root = Path(d.name)
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        for sid, status in (("US0001", "Superseded"), ("US0002", "Won't Implement")):
            (stories / f"{sid}-s.md").write_text(f"# {sid}: s\n\n> **Status:** {status}\n",
                                                 encoding="utf-8")
        epics = self.root / "sdlc-studio" / "epics"
        epics.mkdir()
        (epics / "EP0001-e.md").write_text(
            "# EP0001: e\n\n> **Status:** Done\n\n## Story Breakdown\n\n"
            "- [x] [US0001](../stories/US0001-s.md)\n- [x] [US0002](../stories/US0002-s.md)\n",
            encoding="utf-8")
        # The indexes, written by the product, so the epic's item is the tree's only drift.
        _quiet(reconcile.main, ["apply", "--root", str(self.root)])
        self.assertEqual([("epic-status-stale", "EP0001")], self._drift())
        self.assertTrue(reconcile.detect_all(self.root)[1][0]["blocked_by"])

    # -- helpers -------------------------------------------------------------------------------

    def _drift(self) -> list[tuple[str, str]]:
        return [(d["kind"], d["id"]) for d in reconcile.detect_all(self.root)[1]]

    def _unowned(self):
        """The same epic item with its `blocked_by` removed, as an ordinary drift item."""
        real = reconcile.epic_terminal_undelivered_drift

        def stripped(root):
            return [{k: v for k, v in d.items() if k != "blocked_by"} for d in real(root)]
        return unittest.mock.patch.object(reconcile, "epic_terminal_undelivered_drift", stripped)

    def _mechanical(self) -> None:
        """A story with no index row: mechanical drift beside the epic's item."""
        (self.root / "sdlc-studio" / "stories" / "US0003-s.md").write_text(
            "# US0003: s\n\n> **Status:** Draft\n", encoding="utf-8")

    def _tail(self) -> tuple[int, str, str]:
        """The close tail over the fixture, with its two record writers after the final check
        stood down: they write the run's outcome and tree, which this fixture has neither of."""
        with unittest.mock.patch.object(sprint, "_finalise_outcome", lambda *_a: None), \
                unittest.mock.patch.object(sprint, "record_close_tree", lambda *_a: None):
            return _quiet(sprint._apply_signoff_tail, self.root, {}, units=[], retro_arg=None)

    # -- the reconcile step ----------------------------------------------------------------------

    def test_the_reconcile_step_passes_over_an_item_awaiting_a_decision(self) -> None:
        (ok, detail, remedy), _out, _err = _quiet(sprint._close_reconcile, self.root, None, {})
        self.assertTrue(ok, detail)
        self.assertEqual("no mechanical drift; 1 item(s) awaiting a decision (EP0001) - "
                         "reported, not clearable by apply", detail)
        self.assertEqual("", remedy)
        self.assertEqual([("epic-status-stale", "EP0001")], self._drift())   # still reported

    def test_the_reconcile_step_refuses_the_same_item_without_blocked_by(self) -> None:
        with self._unowned():
            (ok, detail, remedy), _out, _err = _quiet(sprint._close_reconcile, self.root, None,
                                                      {})
        self.assertFalse(ok)
        self.assertTrue(detail.startswith("epic-status-stale EP0001: "), detail)
        self.assertIn("`reconcile.py apply` clears mechanical drift", remedy)

    def test_the_reconcile_step_refuses_a_blocked_item_beside_mechanical_drift(self) -> None:
        self._mechanical()
        (ok, detail, _remedy), _out, _err = _quiet(sprint._close_reconcile, self.root, None, {})
        self.assertFalse(ok)
        self.assertIn("epic-status-stale EP0001: ", detail)
        self.assertIn("US0003", detail)

    # -- the final check -------------------------------------------------------------------------

    def test_the_final_check_passes_over_an_item_awaiting_a_decision(self) -> None:
        rc, out, err = self._tail()
        self.assertEqual(0, rc, err)
        self.assertNotIn("final reconcile reports drift", err)
        self.assertIn("close: 1 item(s) awaiting a decision (EP0001) - reported, not clearable "
                      "by apply", out)

    def test_the_final_check_refuses_the_same_item_without_blocked_by(self) -> None:
        with self._unowned():
            rc, _out, err = self._tail()
        self.assertEqual(1, rc)
        self.assertIn("close: final reconcile reports drift - run `reconcile.py apply`", err)

    def test_the_final_check_refuses_a_blocked_item_beside_mechanical_drift(self) -> None:
        self._mechanical()
        rc, _out, err = self._tail()
        self.assertEqual(1, rc)
        self.assertIn("final reconcile reports drift", err)

    def test_the_final_check_refuses_a_failed_detect_with_nothing_to_exempt(self) -> None:
        # detect exiting non-zero over a tree with no drift item is not an exemption.
        real = sprint._run_cli

        def failing_detect(fn, argv, *a, **k):
            return (2, "") if fn is reconcile.main else real(fn, argv, *a, **k)
        epic = self.root / "sdlc-studio" / "epics" / "EP0001-e.md"
        epic.write_text(epic.read_text(encoding="utf-8").replace(
            "> **Status:** Done", "> **Status:** Superseded"), encoding="utf-8")
        _quiet(reconcile.main, ["apply", "--root", str(self.root)])
        self.assertEqual([], self._drift())
        with unittest.mock.patch.object(sprint, "_run_cli", failing_detect):
            rc, _out, err = self._tail()
        self.assertEqual(1, rc)
        self.assertIn("final reconcile reports drift", err)


if __name__ == "__main__":
    unittest.main()
