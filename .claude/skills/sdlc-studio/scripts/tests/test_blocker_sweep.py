"""Unit tests for blocker_sweep.py (US0049 / CR0130).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "lib"))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


blocker_sweep = _load("blocker_sweep")


def _story(d: Path, sid: str, status: str, depends: str | None = None,
           blocked_by: str | None = None) -> None:
    d.mkdir(parents=True, exist_ok=True)
    lines = [f"# {sid}: t", "", f"> **Status:** {status}"]
    if depends:
        lines.append(f"> **Depends on:** {depends}")
    if blocked_by:
        lines.append(f"> **Blocked By:** {blocked_by}")
    lines.append("")
    (d / f"{sid}-x.md").write_text("\n".join(lines), encoding="utf-8")


def _epic(d: Path, eid: str, status: str) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{eid}-x.md").write_text(f"# {eid}: t\n\n> **Status:** {status}\n", encoding="utf-8")


class BlockerSweepTests(unittest.TestCase):
    def _repo(self, t: str) -> Path:
        root = Path(t)
        s = root / "sdlc-studio" / "stories"
        # US0011 Done -> clears US0010 (Blocked, depends US0011)
        _story(s, "US0010", "Blocked", depends="US0011")
        _story(s, "US0011", "Done")
        # US0012 Blocked, depends US0013 (In Progress) -> still blocked
        _story(s, "US0012", "Blocked", depends="US0013")
        _story(s, "US0013", "In Progress")
        # US0014 Draft with a Depends on -> dependent signal, not a candidate
        _story(s, "US0014", "Draft", depends="US0011")
        return root

    def test_blocker_sweep_collects_signals(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            rep = blocker_sweep.sweep(root)
            ids = {u["id"]: u for u in rep["units"]}
            # every signal-bearing unit is collected, each with referent statuses
            self.assertIn("US0010", ids)
            self.assertIn("US0014", ids)  # depends-on-only is still collected
            self.assertEqual(ids["US0014"]["state"], "dependent")  # but not a candidate
            self.assertEqual(ids["US0010"]["referents"][0]["id"], "US0011")
            self.assertEqual(ids["US0010"]["referents"][0]["status"], "Done")

    def test_blocker_sweep_in_repo_unblock(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._repo(t)
            rep = blocker_sweep.sweep(root)
            self.assertIn("US0010", rep["now_unblocked"])   # referent Done
            self.assertIn("US0012", rep["still_blocked"])   # referent In Progress
            self.assertNotIn("US0012", rep["now_unblocked"])

    def test_blocker_sweep_cross_repo_unblock(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            # blocked unit in repo A depends on an epic delivered in sibling repo B
            _story(root / "sdlc-studio" / "stories", "US0020", "Blocked", depends="EP0099")
            sibling = root / "sibling"
            _epic(sibling / "sdlc-studio" / "epics", "EP0099", "Done")
            (root / "product-manifest.yaml").write_text(
                "master_pvd: x\nrepos:\n  - id: sib\n    path: ./sibling\n", encoding="utf-8")
            rep = blocker_sweep.sweep(root)
            self.assertIn("US0020", rep["now_unblocked"])
            u = next(x for x in rep["units"] if x["id"] == "US0020")
            self.assertEqual(u["referents"][0]["repo"], "sib")

    def test_blocker_sweep_failloud(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            # referent missing everywhere -> still blocked, error recorded, never cleared
            _story(root / "sdlc-studio" / "stories", "US0030", "Blocked", depends="US9999")
            rep = blocker_sweep.sweep(root)
            self.assertNotIn("US0030", rep["now_unblocked"])
            self.assertIn("US0030", rep["still_blocked"])
            self.assertTrue(any("US9999" in e and "missing" in e for e in rep["errors"]))


class WiringTests(unittest.TestCase):
    """US0050 / CR0130: the sweep runs before plan and as an advisory reconcile lane, and only
    ever proposes - the Blocked -> Ready transition stays the gated actor."""

    def _blocked_cleared(self, t: str) -> Path:
        root = Path(t)
        s = root / "sdlc-studio" / "stories"
        _story(s, "US0040", "Blocked", depends="US0041")
        _story(s, "US0041", "Done")
        return root

    def test_blocker_sweep_runs_before_plan(self) -> None:
        sprint = _load("sprint")
        with tempfile.TemporaryDirectory() as t:
            root = self._blocked_cleared(t)
            rep = sprint.pre_plan_blocker_sweep(root)
            self.assertIn("US0040", rep["now_unblocked"])

    def test_blocker_sweep_reconcile_lane(self) -> None:
        import contextlib
        import io
        import json
        reconcile = _load("reconcile")
        with tempfile.TemporaryDirectory() as t:
            root = self._blocked_cleared(t)
            # same fixture, with and without the lane: the lane must not change drift or exit
            base_out = io.StringIO()
            with contextlib.redirect_stdout(base_out):
                rc_base = reconcile.main(["detect", "--root", str(root), "--format", "json"])
            lane_out = io.StringIO()
            with contextlib.redirect_stdout(lane_out):
                rc_lane = reconcile.main(["detect", "--root", str(root),
                                          "--blocker-sweep", "--format", "json"])
            base = json.loads(base_out.getvalue())
            lane = json.loads(lane_out.getvalue())
            self.assertEqual(rc_base, rc_lane)  # advisory: never changes the result
            self.assertEqual(base["summary"]["drift_items"], lane["summary"]["drift_items"])
            self.assertNotIn("blocker_sweep", base)
            self.assertIn("blocker_sweep", lane)  # advisory output present
            self.assertIn("US0040", lane["blocker_sweep"]["now_unblocked"])

    def test_blocker_sweep_no_auto_transition(self) -> None:
        with tempfile.TemporaryDirectory() as t:
            root = self._blocked_cleared(t)
            f = root / "sdlc-studio" / "stories" / "US0040-x.md"
            before = f.read_text(encoding="utf-8")
            rep = blocker_sweep.sweep(root)
            self.assertIn("US0040", rep["now_unblocked"])  # proposed
            self.assertEqual(f.read_text(encoding="utf-8"), before)  # but never applied
            self.assertIn("**Status:** Blocked", f.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
