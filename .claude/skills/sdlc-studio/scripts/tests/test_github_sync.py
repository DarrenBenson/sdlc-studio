"""Unit tests for github_sync.py.

These tests exercise the pure functions (parsing, hashing, label
construction, state management, local file mutation). The gh-wrapper
path is exercised via a monkey-patched gh() stub so the tests do not
touch the network.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "github_sync.py"
_spec = importlib.util.spec_from_file_location("github_sync", SCRIPT_PATH)
assert _spec and _spec.loader
github_sync = importlib.util.module_from_spec(_spec)
sys.modules["github_sync"] = github_sync
_spec.loader.exec_module(github_sync)


SAMPLE_CR = """\
# CR-0001: Rate-limit the login endpoint

> **Status:** Proposed
> **Priority:** P2
> **Type:** feature-request
> **Requester:** Darren
> **Date:** 2026-04-14
> **Affects:** auth
> **Depends on:** --

## Summary

We need per-IP rate limiting on /login.
"""

SAMPLE_CR_WITH_ISSUE = """\
# CR-0002: Already linked

> **Status:** In Progress
> **Priority:** P1
> **Type:** production-feedback
> **GitHub Issue:** #42
> **Date:** 2026-04-10

## Summary

Already has an issue number.
"""


class FixtureRepo:
    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="github_sync_test_"))
        (self.tmp / "sdlc-studio" / "change-requests").mkdir(parents=True)
        (self.tmp / "sdlc-studio" / ".local").mkdir(parents=True)
        (self.tmp / "sdlc-studio" / "change-requests" / "CR-0001-rate-limit.md").write_text(
            SAMPLE_CR
        )
        (self.tmp / "sdlc-studio" / "change-requests" / "CR-0002-linked.md").write_text(
            SAMPLE_CR_WITH_ISSUE
        )

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class ParseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def test_walk_local_finds_both_crs(self) -> None:
        records = list(github_sync.walk_local("cr"))
        self.assertEqual(len(records), 2)
        ids = sorted(r.rec_id for r in records)
        self.assertEqual(ids, ["CR-0001", "CR-0002"])

    def test_parse_captures_status_priority_type(self) -> None:
        records = list(github_sync.walk_local("cr"))
        r1 = next(r for r in records if r.rec_id == "CR-0001")
        self.assertEqual(r1.status, "Proposed")
        self.assertEqual(r1.priority, "P2")
        self.assertEqual(r1.rec_type, "feature-request")
        self.assertIsNone(r1.github_issue)

    def test_parse_captures_existing_github_issue(self) -> None:
        records = list(github_sync.walk_local("cr"))
        r2 = next(r for r in records if r.rec_id == "CR-0002")
        self.assertEqual(r2.github_issue, 42)

    def test_labels_include_all_expected_prefixes(self) -> None:
        records = list(github_sync.walk_local("cr"))
        r1 = next(r for r in records if r.rec_id == "CR-0001")
        labels = r1.labels()
        self.assertIn("sdlc:cr", labels)
        self.assertIn("sdlc:status:proposed", labels)
        self.assertIn("sdlc:priority:P2", labels)
        self.assertIn("sdlc:type:feature-request", labels)

    def test_set_github_issue_field_inserts_when_missing(self) -> None:
        records = list(github_sync.walk_local("cr"))
        r1 = next(r for r in records if r.rec_id == "CR-0001")
        github_sync.set_github_issue_field(r1.path, 101)
        text = r1.path.read_text()
        self.assertIn("**GitHub Issue:** #101", text)
        # Re-parse and confirm github_issue is 101
        reparsed = github_sync.parse_local_file(r1.path, "cr")
        self.assertEqual(reparsed.github_issue, 101)

    def test_set_github_issue_field_replaces_when_present(self) -> None:
        records = list(github_sync.walk_local("cr"))
        r2 = next(r for r in records if r.rec_id == "CR-0002")
        github_sync.set_github_issue_field(r2.path, 999)
        text = r2.path.read_text()
        self.assertIn("**GitHub Issue:** #999", text)
        self.assertNotIn("#42", text)


class StateTests(unittest.TestCase):
    def test_load_state_returns_empty_when_missing(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            state = github_sync.load_state(tmp / "state.json")
            self.assertEqual(state["version"], 1)
            self.assertIsNone(state["last_pull"])
            self.assertEqual(state["mappings"], {})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_save_and_reload_state_round_trip(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            path = tmp / "state.json"
            state = github_sync.load_state(path)
            state["last_pull"] = "2026-04-15T00:00:00Z"
            state["mappings"]["CR-0001"] = {"issue": 1, "hash": "sha256:x"}
            github_sync.save_state(state, path)
            reloaded = github_sync.load_state(path)
            self.assertEqual(reloaded["last_pull"], "2026-04-15T00:00:00Z")
            self.assertEqual(reloaded["mappings"]["CR-0001"]["issue"], 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class PushTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def test_dry_run_push_reports_without_calling_gh(self) -> None:
        with mock.patch.object(github_sync, "gh") as gh_mock:
            rc = github_sync.main(["push", "--type", "cr", "--dry-run"])
            self.assertEqual(rc, 0)
            # Dry run should not call gh
            gh_mock.assert_not_called()

    def test_push_creates_issue_for_unmapped_cr(self) -> None:
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "create"):
                return subprocess_result(0, "https://github.com/x/y/issues/55\n", "")
            if args[:2] == ("issue", "list"):
                return subprocess_result(0, "[]", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
            self.assertEqual(rc, 0)
        # CR-0001 should now have a GitHub Issue field pointing at #55
        path = self.fixture.tmp / "sdlc-studio/change-requests/CR-0001-rate-limit.md"
        self.assertIn("**GitHub Issue:** #55", path.read_text())


class CascadeTests(unittest.TestCase):
    def test_extract_closes_and_sdlc_refs(self) -> None:
        body = (
            "Closes #42.\n"
            "Also fixes #99 and resolves #101.\n"
            "sdlc:story US0023 and sdlc:cr CR-0007 referenced too."
        )
        closes = github_sync._CLOSES_RE.findall(body)
        self.assertEqual(sorted(int(n) for n in closes), [42, 99, 101])
        stories = github_sync._STORY_REF_RE.findall(body)
        self.assertEqual(stories, ["US0023"])
        crs = github_sync._CR_REF_RE.findall(body)
        self.assertEqual(crs, ["CR-0007"])


class HardeningTests(unittest.TestCase):
    def test_loads_returns_default_on_malformed(self) -> None:
        self.assertEqual(github_sync._loads("not json", []), [])
        self.assertEqual(github_sync._loads("", []), [])
        self.assertEqual(github_sync._loads("   ", []), [])
        self.assertEqual(github_sync._loads('[{"number": 1}]', []), [{"number": 1}])

    def test_load_state_recovers_from_corrupt_file(self) -> None:
        tmp = Path(tempfile.mkdtemp())
        try:
            path = tmp / "state.json"
            path.write_text("{ not valid json", encoding="utf-8")
            state = github_sync.load_state(path)
            self.assertEqual(state["version"], 1)
            self.assertEqual(state["mappings"], {})
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_gh_raises_runtimeerror_when_cli_missing(self) -> None:
        with mock.patch.object(github_sync.shutil, "which", return_value=None):
            with self.assertRaises(RuntimeError):
                github_sync.gh("issue", "list")

    def test_main_returns_127_when_gh_missing(self) -> None:
        fixture = FixtureRepo()
        import os
        cwd = Path.cwd()
        os.chdir(fixture.tmp)
        try:
            with mock.patch.object(github_sync.shutil, "which", return_value=None):
                rc = github_sync.main(["push", "--type", "cr"])
            self.assertEqual(rc, 127)
        finally:
            os.chdir(cwd)
            fixture.cleanup()


def subprocess_result(returncode: int, stdout: str, stderr: str):
    import subprocess
    return subprocess.CompletedProcess(
        args=["gh"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


if __name__ == "__main__":
    unittest.main()
