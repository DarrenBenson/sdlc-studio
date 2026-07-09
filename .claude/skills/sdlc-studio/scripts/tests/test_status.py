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

    def test_rename_names_both_ids(self) -> None:
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            cd = root / "sdlc-studio" / "change-requests"
            subprocess.run(["git", "mv", "sdlc-studio/change-requests/CR0001-a.md",
                            "sdlc-studio/change-requests/CR0002-b.md"],
                           cwd=root, check=True, capture_output=True)
            adv = status.workspace_advisory(root)
            self.assertIn("CR0001", adv)
            self.assertIn("CR0002", adv)
            # the NORMALISED id, not the filename: another session greps for
            # the bare id, and the filename fallback is for non-artifact paths
            self.assertNotIn("CR0001-a.md", adv)
            self.assertNotIn("CR0002-b.md", adv)

    def test_pillars_and_hint_commands_run_in_text_mode(self) -> None:
        # the critic's high finding: the COMMANDS must run, not just the helper
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            for cmd in ("pillars", "hint"):
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = status.main([cmd, "--root", str(root)])
                self.assertEqual(rc, 0, f"{cmd} crashed:\n{buf.getvalue()}")
                self.assertTrue(buf.getvalue().strip(), f"{cmd} printed nothing")

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


class UpdateNoticeTests(unittest.TestCase):
    """Pins _print_update_notice's one behaviour: when the version check yields a
    notice line, it prints; when not, it stays silent. Added because the mutation
    gate SURVIVED both a body short-circuit and a guard inversion here - the
    function was entirely unpinned."""

    def _with_stub(self, notice_value):
        import io, types
        from contextlib import redirect_stdout
        stub = types.ModuleType("version_check")
        stub.DEFAULT_TTL_HOURS = 24
        stub.check = lambda **kw: {"stub": True}
        stub.notice = lambda _res: notice_value
        old = sys.modules.get("version_check")
        sys.modules["version_check"] = stub
        try:
            buf = io.StringIO()
            with redirect_stdout(buf):
                status._print_update_notice(".")
            return buf.getvalue()
        finally:
            if old is not None:
                sys.modules["version_check"] = old
            else:
                sys.modules.pop("version_check", None)

    def test_notice_prints_when_present(self) -> None:
        out = self._with_stub("update available: v9.9.9")
        self.assertIn("update available", out)

    def test_silent_when_no_notice(self) -> None:
        self.assertEqual(self._with_stub(None), "")


class TrancheQueryTests(unittest.TestCase):
    """US0068 AC2: list every artefact carrying a given tranche reference, from the records."""

    def _artefact(self, root: Path, rel: str, body: str) -> None:
        p = root / "sdlc-studio" / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")

    def test_tranche_query_lists_only_matching_members(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._artefact(root, "bugs/BG0001-a.md",
                           "# BG0001: a\n\n> **Status:** Open\n> **Tranche:** sprint-12\n")
            self._artefact(root, "change-requests/CR0001-b.md",
                           "# CR-0001: b\n\n> **Status:** Proposed\n> **Tranche:** sprint-12\n")
            self._artefact(root, "bugs/BG0002-c.md",
                           "# BG0002: c\n\n> **Status:** Open\n> **Tranche:** sprint-13\n")
            self._artefact(root, "bugs/BG0003-d.md",
                           "# BG0003: d\n\n> **Status:** Open\n")  # no tranche
            members = status.tranche_members(root, "sprint-12")
            self.assertEqual([m["id"] for m in members], ["BG0001", "CR0001"])
            self.assertEqual({m["type"] for m in members}, {"bug", "cr"})

    def test_tranche_query_empty_when_no_members(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._artefact(root, "bugs/BG0001-a.md", "# BG0001: a\n\n> **Status:** Open\n")
            self.assertEqual(status.tranche_members(root, "sprint-99"), [])

    def test_tranche_query_empty_field_is_not_a_phantom_member(self) -> None:
        # An empty `> **Tranche:**` line followed by more content must NOT over-capture the next
        # line as a value (the general extract_field bug): it belongs to no tranche.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._artefact(root, "bugs/BG0001-a.md",
                           "# BG0001: a\n\n> **Status:** Open\n> **Tranche:**\n## Summary\n\nbody\n")
            self.assertEqual(status.tranche_members(root, "## Summary"), [])
            self.assertEqual(status.tranche_members(root, ""), [])


if __name__ == "__main__":
    unittest.main()


class IndexBloatHintTests(unittest.TestCase):
    """The archive recommendation surfaces at the HINT (L-0004: the command,
    not only the reconcile helper) and stays silent on a bounded workspace."""

    def _bloated(self, d, n=35):
        root = Path(d)
        dd = root / "sdlc-studio" / "change-requests"
        dd.mkdir(parents=True)
        rows = []
        for i in range(1, n + 1):
            (dd / f"CR{i:04d}-x.md").write_text(
                f"# CR-{i:04d}: x\n\n> **Status:** Complete\n", encoding="utf-8")
            rows.append(f"| CR-{i:04d} | x | Complete |")
        (dd / "_index.md").write_text(
            "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            + "\n".join(rows) + "\n", encoding="utf-8")
        return root

    def test_hint_command_prints_archive_advisory(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bloated(d)
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = status.main(["hint", "--root", str(root)])
            self.assertEqual(rc, 0)
            self.assertIn("archive.py archive --type cr", buf.getvalue())

    def test_hint_silent_when_bounded(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bloated(d, n=5)
            buf = io.StringIO()
            with redirect_stdout(buf):
                status.main(["hint", "--root", str(root)])
            self.assertNotIn("archive.py", buf.getvalue())
