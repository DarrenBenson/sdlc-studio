"""Unit tests for status.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "status.py"
_spec = importlib.util.spec_from_file_location("status", SCRIPT_PATH)
assert _spec and _spec.loader
status = importlib.util.module_from_spec(_spec)
sys.modules["status"] = status
_spec.loader.exec_module(status)


def _story(root: Path, num: int, st: str) -> None:
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / f"US{num:04d}-x.md").write_text(f"# S{num}\n\n> **Status:** {st}\n", encoding="utf-8")


class CensusTests(unittest.TestCase):
    def test_count_by_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            _story(root, 2, "Done")
            _story(root, 3, "In Progress")
            census = status.count_by_status("story", root)
            self.assertEqual(census["total"], 3)
            self.assertEqual(census["by_status"]["Done"], 2)

    def test_decorated_status_collapses_to_canonical(self) -> None:
        # `Done (v2.66.0) · **CR:** CR-0088` must tally under `Done`, not as a
        # distinct bucket, so done-percentages stay correct.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done (v2.66.0) · **CR:** CR-0088")
            _story(root, 2, "Done")
            census = status.count_by_status("story", root)
            self.assertEqual(census["total"], 2)
            self.assertEqual(census["by_status"], {"Done": 2})

    def test_pct_done(self) -> None:
        census = {"total": 4, "by_status": {"Done": 1, "Draft": 3}}
        self.assertEqual(status._pct_done(census, ("Done",)), 25)
        self.assertEqual(status._pct_done({"total": 0, "by_status": {}}, ("Done",)), 0)


class GatherTests(unittest.TestCase):
    def test_gather_reports_artifacts_and_docs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            (root / "sdlc-studio" / "prd.md").write_text("# PRD\n", encoding="utf-8")
            data = status.gather(root)
            self.assertTrue(data["requirements"]["prd"])
            self.assertFalse(data["code"]["trd"])
            self.assertEqual(data["requirements"]["stories"]["total"], 1)
            self.assertEqual(data["requirements"]["stories_done_pct"], 100)

    def test_gather_counts_bugs_and_workflows(self) -> None:
        # BG0002: bug and workflow types must appear in the census.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bdir = root / "sdlc-studio" / "bugs"
            bdir.mkdir(parents=True, exist_ok=True)
            (bdir / "BG0001-x.md").write_text("# B1\n\n> **Status:** Open\n", encoding="utf-8")
            (bdir / "BG0002-x.md").write_text("# B2\n\n> **Status:** Fixed\n", encoding="utf-8")
            data = status.gather(root)
            self.assertEqual(data["bugs"]["total"], 2)
            self.assertEqual(data["bugs"]["by_status"].get("Open"), 1)
            self.assertEqual(data["workflows"]["total"], 0)


class HintTests(unittest.TestCase):
    def test_hint_no_prd_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            data = status.gather(Path(d))
            hint = status.compute_hint(data, Path(d))
            self.assertIn("prd", hint["next_command"])

    def test_hint_seeded_pipeline(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            base = root / "sdlc-studio"
            base.mkdir(parents=True)
            for name in ("prd.md", "trd.md", "tsd.md", "personas.md"):
                (base / name).write_text("# x\n", encoding="utf-8")
            (base / "epics").mkdir()
            (base / "epics" / "EP0001-x.md").write_text("# E\n\n> **Status:** Done\n", encoding="utf-8")
            _story(root, 1, "Done")
            hint = status.compute_hint(status.gather(root), root)
            self.assertIn("story", hint["next_command"])


class VerifyLaneTests(unittest.TestCase):
    """CR0095: status surfaces the AC-verification lane from verify-report.json."""

    def test_lane_counts_unverified_and_manual(self) -> None:
        import json
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rp = root / "sdlc-studio" / ".local" / "verify-report.json"
            rp.parent.mkdir(parents=True)
            rp.write_text(json.dumps({"stories": {
                "US0001-x": {"failed": 1, "stale": 0, "manual": 0, "failures": [{"ac": "AC1"}]},
                "US0002-x": {"failed": 0, "stale": 0, "manual": 2, "failures": []},
            }}), encoding="utf-8")
            lane = status._verify_lane(root)
            self.assertTrue(lane["has_report"])
            self.assertEqual(lane["stories_with_unverified_acs"], 1)
            self.assertEqual(lane["manual_acs"], 2)

    def test_lane_empty_without_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            lane = status._verify_lane(Path(d))
            self.assertFalse(lane["has_report"])


class WorkspaceAdvisoryTests(unittest.TestCase):
    """CR0150: status/hint surface uncommitted workspace artifact changes as a
    one-line advisory naming ids - informational, never blocking, no authorship
    guesses, silent without git."""

    def _repo(self, d: Path) -> Path:
        import subprocess
        root = Path(d)
        cd = root / "sdlc-studio" / "change-requests"
        cd.mkdir(parents=True)
        (cd / "CR0001-a.md").write_text("# CR-0001: a\n\n> **Status:** Proposed\n",
                                        encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                        "commit", "-qm", "base"], cwd=root, check=True)
        return root

    def test_uncommitted_artifact_changes_are_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            cd = root / "sdlc-studio" / "change-requests"
            (cd / "CR0001-a.md").write_text("# CR-0001: a\n\n> **Status:** Approved\n",
                                            encoding="utf-8")          # modified
            (cd / "CR0002-b.md").write_text("# CR-0002: b\n\n> **Status:** Proposed\n",
                                            encoding="utf-8")          # untracked
            adv = status.workspace_advisory(root)
            self.assertIsNotNone(adv)
            self.assertIn("CR0001", adv)
            self.assertIn("CR0002", adv)
            self.assertIn("another session", adv)   # awareness wording, no authorship claim

    def test_clean_workspace_no_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            self.assertIsNone(status.workspace_advisory(root))

    def test_no_git_degrades_silently(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            self.assertIsNone(status.workspace_advisory(root))

    def test_changes_outside_workspace_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            (root / "README.md").write_text("x\n", encoding="utf-8")   # outside sdlc-studio/
            self.assertIsNone(status.workspace_advisory(root))


if __name__ == "__main__":
    unittest.main()
