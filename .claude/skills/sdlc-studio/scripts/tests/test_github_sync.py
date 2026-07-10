"""Unit tests for github_sync.py.

These tests exercise the pure functions (parsing, hashing, label
construction, state management, local file mutation). The gh-wrapper
path is exercised via a monkey-patched gh() stub so the tests do not
touch the network.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
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


# -----------------------------------------------------------------------------
# gh wrapper-layer tests (gh() itself stubbed, never reaching subprocess)
# -----------------------------------------------------------------------------


class GhIssueListTests(unittest.TestCase):
    """gh_issue_list parses JSON and degrades on error/garbage."""

    def test_parses_issue_array(self) -> None:
        payload = '[{"number": 7, "title": "x", "labels": []}]'
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, payload, "")
        ):
            issues = github_sync.gh_issue_list("sdlc:cr")
        self.assertEqual(issues, [{"number": 7, "title": "x", "labels": []}])

    def test_raises_on_nonzero_returncode(self) -> None:
        # BG0064: a gh failure must be distinguishable from an empty result, not
        # silently flattened to [] (which then reads as "nothing to do").
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(1, "", "boom")
        ):
            with self.assertRaises(github_sync.GhError):
                github_sync.gh_issue_list("sdlc:cr")

    def test_returns_empty_on_malformed_json(self) -> None:
        # Non-zero would mask the parse path, so use a success exit with garbage.
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, "not json{", "")
        ):
            self.assertEqual(github_sync.gh_issue_list("sdlc:cr"), [])

    def test_returns_empty_on_blank_stdout(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, "   ", "")
        ):
            self.assertEqual(github_sync.gh_issue_list("sdlc:cr"), [])

    def test_passes_state_all_and_label_filter(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, "[]", "")
        ) as gh_mock:
            github_sync.gh_issue_list("sdlc:epic")
        called_args = gh_mock.call_args.args
        self.assertIn("--label", called_args)
        self.assertIn("sdlc:epic", called_args)
        self.assertIn("all", called_args)


class GhIssueCreateTests(unittest.TestCase):
    """gh_issue_create extracts the issue number from the returned URL."""

    def test_extracts_number_from_url(self) -> None:
        with mock.patch.object(
            github_sync,
            "gh",
            return_value=subprocess_result(
                0, "https://github.com/o/r/issues/123\n", ""
            ),
        ):
            number = github_sync.gh_issue_create("t", "b", ["sdlc:cr"])
        self.assertEqual(number, 123)

    def test_returns_none_when_url_has_no_number(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, "no url here", "")
        ):
            self.assertIsNone(github_sync.gh_issue_create("t", "b", []))

    def test_returns_none_on_failure(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(1, "", "denied")
        ):
            self.assertIsNone(github_sync.gh_issue_create("t", "b", ["sdlc:cr"]))

    def test_each_label_passed_as_separate_flag(self) -> None:
        with mock.patch.object(
            github_sync,
            "gh",
            return_value=subprocess_result(0, "/issues/1", ""),
        ) as gh_mock:
            github_sync.gh_issue_create("Title", "Body", ["sdlc:cr", "sdlc:status:proposed"])
        args = list(gh_mock.call_args.args)
        # Two labels -> two --label occurrences.
        self.assertEqual(args.count("--label"), 2)
        self.assertIn("sdlc:status:proposed", args)


class GhIssueEditTests(unittest.TestCase):
    """gh_issue_edit short-circuits and builds add/remove flags."""

    def test_no_labels_is_noop_success_without_calling_gh(self) -> None:
        with mock.patch.object(github_sync, "gh") as gh_mock:
            self.assertTrue(github_sync.gh_issue_edit(5, [], []))
            gh_mock.assert_not_called()

    def test_builds_add_and_remove_flags(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, "", "")
        ) as gh_mock:
            ok = github_sync.gh_issue_edit(9, ["sdlc:status:done"], ["sdlc:status:ready"])
        self.assertTrue(ok)
        args = list(gh_mock.call_args.args)
        self.assertEqual(args[:3], ["issue", "edit", "9"])
        self.assertIn("--add-label", args)
        self.assertIn("sdlc:status:done", args)
        self.assertIn("--remove-label", args)
        self.assertIn("sdlc:status:ready", args)

    def test_returns_false_on_failure(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(1, "", "nope")
        ):
            self.assertFalse(github_sync.gh_issue_edit(9, ["sdlc:cr"], []))


class GhPrListMergedTests(unittest.TestCase):
    """gh_pr_list_merged filters by since_ref and degrades on error."""

    PRS = json.dumps(
        [
            {"number": 1, "body": "", "mergedAt": "2026-01-01T00:00:00Z"},
            {"number": 2, "body": "", "mergedAt": "2026-03-01T00:00:00Z"},
            {"number": 3, "body": "", "mergedAt": "2026-05-01T00:00:00Z"},
        ]
    )

    def test_no_since_returns_all(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, self.PRS, "")
        ):
            prs = github_sync.gh_pr_list_merged(None)
        self.assertEqual([p["number"] for p in prs], [1, 2, 3])

    def test_since_excludes_older_and_equal(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, self.PRS, "")
        ):
            prs = github_sync.gh_pr_list_merged("2026-03-01T00:00:00Z")
        # Strictly-greater comparison: only the May PR survives.
        self.assertEqual([p["number"] for p in prs], [3])

    def test_returns_empty_on_error(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(2, "", "fail")
        ):
            self.assertEqual(github_sync.gh_pr_list_merged(None), [])

    def test_pr_missing_mergedat_is_filtered_out_when_since_set(self) -> None:
        payload = json.dumps([{"number": 8, "body": ""}])
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, payload, "")
        ):
            prs = github_sync.gh_pr_list_merged("2020-01-01T00:00:00Z")
        self.assertEqual(prs, [])


# -----------------------------------------------------------------------------
# Hashing and field-extraction edge cases
# -----------------------------------------------------------------------------


class HashAndExtractTests(unittest.TestCase):
    def test_hash_is_stable_and_content_sensitive(self) -> None:
        h1 = github_sync._hash_body("alpha")
        self.assertEqual(h1, github_sync._hash_body("alpha"))
        self.assertNotEqual(h1, github_sync._hash_body("beta"))
        self.assertTrue(h1.startswith("sha256:"))

    def test_extract_github_issue_none_when_absent(self) -> None:
        self.assertIsNone(github_sync._extract_github_issue("# Title\n\nNo metadata."))

    def test_extract_github_issue_parses_hashed_number(self) -> None:
        text = "> **GitHub Issue:** #314\n"
        self.assertEqual(github_sync._extract_github_issue(text), 314)


# -----------------------------------------------------------------------------
# _resolve_types
# -----------------------------------------------------------------------------


class ResolveTypesTests(unittest.TestCase):
    def test_all_expands_to_three_types(self) -> None:
        self.assertEqual(github_sync._resolve_types("all"), ["cr", "story", "epic"])

    def test_single_type_passes_through(self) -> None:
        self.assertEqual(github_sync._resolve_types("story"), ["story"])

    def test_unknown_type_raises_systemexit(self) -> None:
        with self.assertRaises(SystemExit):
            github_sync._resolve_types("widget")


# -----------------------------------------------------------------------------
# set_github_issue_field idempotency and placement
# -----------------------------------------------------------------------------


class SetGithubIssueFieldTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="ghsf_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_noop_when_already_correct(self) -> None:
        p = self.tmp / "cr.md"
        p.write_text(SAMPLE_CR_WITH_ISSUE)
        before = p.read_text()
        github_sync.set_github_issue_field(p, 42)  # already #42
        self.assertEqual(p.read_text(), before)

    def test_inserts_after_status_line(self) -> None:
        p = self.tmp / "cr.md"
        p.write_text(SAMPLE_CR)  # has a Status line, no GitHub Issue
        github_sync.set_github_issue_field(p, 77)
        lines = p.read_text().splitlines()
        status_idx = next(i for i, l in enumerate(lines) if "**Status:**" in l)
        self.assertIn("**GitHub Issue:** #77", lines[status_idx + 1])

    def test_appends_when_no_status_line(self) -> None:
        p = self.tmp / "bare.md"
        p.write_text("# CR-0099: Bare record\n\nNo metadata block.\n")
        github_sync.set_github_issue_field(p, 12)
        self.assertIn("**GitHub Issue:** #12", p.read_text())


# -----------------------------------------------------------------------------
# Push: label diff/sync, idempotency, state persistence
# -----------------------------------------------------------------------------


class PushLabelSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def _state_path(self) -> Path:
        return self.fixture.tmp / github_sync.STATE_PATH

    def test_mapped_cr_with_stale_labels_gets_diffed(self) -> None:
        """CR-0002 (#42) carries P1/in-progress locally; issue has wrong labels.

        The push must add the desired sdlc labels and remove the stale ones,
        touching only `sdlc:` labels (a foreign label must be left alone).
        """
        captured: dict[str, list[str]] = {}

        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "create"):
                return subprocess_result(0, "/issues/99", "")  # unmapped records create cleanly
            if args[:2] == ("issue", "list"):
                issue = {
                    "number": 42,
                    "labels": [
                        {"name": "sdlc:cr"},
                        {"name": "sdlc:status:proposed"},  # stale -> remove
                        {"name": "sdlc:priority:P3"},      # stale -> remove
                        {"name": "needs-triage"},          # foreign -> keep
                    ],
                }
                return subprocess_result(0, json.dumps([issue]), "")
            if args[:2] == ("issue", "edit"):
                arglist = list(args)
                captured["add"] = [
                    arglist[i + 1]
                    for i, a in enumerate(arglist)
                    if a == "--add-label"
                ]
                captured["remove"] = [
                    arglist[i + 1]
                    for i, a in enumerate(arglist)
                    if a == "--remove-label"
                ]
                return subprocess_result(0, "", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 0)
        # Desired labels for CR-0002: in-progress, P1, production-feedback.
        self.assertIn("sdlc:status:in-progress", captured["add"])
        self.assertIn("sdlc:priority:P1", captured["add"])
        self.assertIn("sdlc:type:production-feedback", captured["add"])
        # Stale sdlc labels removed; foreign label untouched.
        self.assertIn("sdlc:status:proposed", captured["remove"])
        self.assertIn("sdlc:priority:P3", captured["remove"])
        self.assertNotIn("needs-triage", captured["remove"])

    def test_idempotent_when_hash_matches_state(self) -> None:
        """If the mapping hash equals the current body hash, skip the issue entirely."""
        rec = next(
            r for r in github_sync.walk_local("cr") if r.rec_id == "CR-0002"
        )
        state = github_sync._empty_state()
        state["mappings"]["CR-0002"] = {
            "type": "cr",
            "issue": 42,
            "hash": rec.content_hash,
            "updated_at": "2026-01-01T00:00:00Z",
        }
        github_sync.save_state(state, self._state_path())

        edited = {"issues": []}

        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "list"):
                # CR0206: an unmapped record (CR-0001) now lists once for the adopt check;
                # return no adoptable issue so CR-0001 falls through to create.
                return subprocess_result(0, "[]", "")
            if args[:2] == ("issue", "create"):
                return subprocess_result(0, "/issues/60", "")
            if args[:2] == ("issue", "edit"):
                edited["issues"].append(args[2])
                return subprocess_result(0, "", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 0)
        # The real invariant: the mapped, hash-matched CR-0002 (#42) is skipped entirely -
        # its labels are never edited.
        self.assertNotIn("42", edited["issues"])

    def test_missing_remote_issue_is_skipped_not_fatal(self) -> None:
        """A local CR points at #42 but gh returns no such issue -> skip, rc 0."""
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "list"):
                return subprocess_result(0, "[]", "")  # #42 absent
            if args[:2] == ("issue", "create"):
                return subprocess_result(0, "/issues/61", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 0)
        # CR-0002 mapping must not be written, since the edit never happened.
        state = github_sync.load_state(self._state_path())
        self.assertNotIn("CR-0002", state.get("mappings", {}))

    def test_create_failure_does_not_write_mapping(self) -> None:
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "create"):
                return subprocess_result(1, "", "create failed")
            if args[:2] == ("issue", "list"):
                return subprocess_result(0, "[]", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
        # BG0092: a gh failure must be signalled (non-zero) and must NOT stamp last_push -
        # the BG0064 pull fix, now on the push side.
        self.assertNotEqual(rc, 0)
        state = github_sync.load_state(self._state_path())
        self.assertIsNone(state.get("last_push"))
        self.assertNotIn("CR-0001", state.get("mappings", {}))
        # And the file must not have gained a bogus issue number.
        path = self.fixture.tmp / "sdlc-studio/change-requests/CR-0001-rate-limit.md"
        self.assertNotIn("**GitHub Issue:**", path.read_text())

    def test_apply_push_persists_state_and_mapping(self) -> None:
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "create"):
                return subprocess_result(0, "/issues/70", "")
            if args[:2] == ("issue", "list"):
                return subprocess_result(0, "[]", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            github_sync.main(["push", "--type", "cr"])
        state = github_sync.load_state(self._state_path())
        self.assertIsNotNone(state["last_push"])
        self.assertEqual(state["mappings"]["CR-0001"]["issue"], 70)
        # The persisted hash matches the file as written (post issue-field edit).
        rec = next(
            r for r in github_sync.walk_local("cr") if r.rec_id == "CR-0001"
        )
        self.assertEqual(state["mappings"]["CR-0001"]["hash"], rec.content_hash)

    def test_dry_run_does_not_persist_state(self) -> None:
        with mock.patch.object(github_sync, "gh") as gh_mock:
            github_sync.main(["push", "--type", "cr", "--dry-run"])
            gh_mock.assert_not_called()
        # No state file written on a dry run.
        self.assertFalse(self._state_path().exists())


# -----------------------------------------------------------------------------
# Pull command
# -----------------------------------------------------------------------------


class PullTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def _state_path(self) -> Path:
        return self.fixture.tmp / github_sync.STATE_PATH

    def test_pull_skips_already_linked_issue(self) -> None:
        """Issue #42 is already linked to CR-0002 locally, so no ingest needed."""
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "list"):
                issue = {"number": 42, "title": "Linked", "body": "x", "labels": []}
                return subprocess_result(0, json.dumps([issue]), "")
            return subprocess_result(0, "", "")

        out = io.StringIO()
        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            with contextlib.redirect_stdout(out):
                rc = github_sync.main(["pull", "--type", "cr"])
        self.assertEqual(rc, 0)
        self.assertIn("issues_needing_ingest=0", out.getvalue())

    def test_pull_flags_unlinked_issue_for_ingest(self) -> None:
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "list"):
                issue = {"number": 500, "title": "New CR", "body": "x", "labels": []}
                return subprocess_result(0, json.dumps([issue]), "")
            return subprocess_result(0, "", "")

        out = io.StringIO()
        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            with contextlib.redirect_stdout(out):
                rc = github_sync.main(["pull", "--type", "cr"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("issues_needing_ingest=1", text)
        self.assertIn("--from-issue 500", text)

    def test_pull_dry_run_does_not_write_state(self) -> None:
        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "list"):
                issue = {"number": 500, "title": "New CR", "body": "x", "labels": []}
                return subprocess_result(0, json.dumps([issue]), "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            with contextlib.redirect_stdout(io.StringIO()):
                github_sync.main(["pull", "--type", "cr", "--dry-run"])
        self.assertFalse(self._state_path().exists())

    def test_pull_apply_stamps_last_pull(self) -> None:
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(0, "[]", "")
        ):
            with contextlib.redirect_stdout(io.StringIO()):
                github_sync.main(["pull", "--type", "cr"])
        state = github_sync.load_state(self._state_path())
        self.assertIsNotNone(state["last_pull"])

    def test_pull_does_not_stamp_or_succeed_on_gh_failure(self) -> None:
        # BG0064: a transient gh failure must NOT advance last_pull or exit 0 - the state
        # would then assert a pull happened at time T that never did.
        with mock.patch.object(
            github_sync, "gh", return_value=subprocess_result(1, "", "auth required")
        ):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                rc = github_sync.main(["pull", "--type", "cr"])
        self.assertNotEqual(rc, 0)
        self.assertFalse(self._state_path().exists())  # no state written on failure

    def test_gh_timeout_surfaces_as_failure(self) -> None:
        # BG0063: a hung gh call must time out and surface a failure, never block forever.
        import subprocess
        def _boom(*a, **k):
            raise subprocess.TimeoutExpired(cmd="gh", timeout=1)
        with mock.patch("subprocess.run", side_effect=_boom), \
             mock.patch("shutil.which", return_value="/usr/bin/gh"):
            res = github_sync.gh("issue", "list")
        self.assertNotEqual(res.returncode, 0)


# -----------------------------------------------------------------------------
# Cascade command
# -----------------------------------------------------------------------------


class CascadeCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        # Add a story dir with a story linked to issue #42.
        stories = self.fixture.tmp / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        (stories / "US0023-login.md").write_text(
            "# US0023: Login story\n\n"
            "> **Status:** In Progress\n"
            "> **GitHub Issue:** #42\n\n"
            "## Summary\n\nStory body.\n"
        )
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def _state_path(self) -> Path:
        return self.fixture.tmp / github_sync.STATE_PATH

    def test_no_prs_returns_early(self) -> None:
        out = io.StringIO()
        with mock.patch.object(github_sync, "gh_pr_list_merged", return_value=[]):
            with contextlib.redirect_stdout(out):
                rc = github_sync.main(["cascade"])
        self.assertEqual(rc, 0)
        self.assertIn("no merged PRs", out.getvalue())

    def test_prs_without_sdlc_refs_report_none(self) -> None:
        prs = [{"number": 1, "body": "just a normal merge", "mergedAt": "2026-05-01T00:00:00Z"}]
        out = io.StringIO()
        with mock.patch.object(github_sync, "gh_pr_list_merged", return_value=prs):
            with contextlib.redirect_stdout(out):
                rc = github_sync.main(["cascade"])
        self.assertEqual(rc, 0)
        self.assertIn("no sdlc references", out.getvalue())

    def test_closes_ref_maps_issue_number_to_local_story(self) -> None:
        prs = [
            {
                "number": 11,
                "body": "Closes #42",
                "mergedAt": "2026-05-02T00:00:00Z",
            }
        ]
        out = io.StringIO()
        with mock.patch.object(github_sync, "gh_pr_list_merged", return_value=prs):
            with contextlib.redirect_stdout(out):
                rc = github_sync.main(["cascade"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        # Issue #42 maps to local US0023 via its GitHub Issue field.
        self.assertIn("US0023", text)

    def test_explicit_sdlc_refs_are_reported(self) -> None:
        prs = [
            {
                "number": 12,
                "body": "sdlc:story US0099 and sdlc:cr CR-0007",
                "mergedAt": "2026-05-03T00:00:00Z",
            }
        ]
        out = io.StringIO()
        with mock.patch.object(github_sync, "gh_pr_list_merged", return_value=prs):
            with contextlib.redirect_stdout(out):
                rc = github_sync.main(["cascade"])
        self.assertEqual(rc, 0)
        text = out.getvalue()
        self.assertIn("US0099", text)
        self.assertIn("CR-0007", text)

    def test_apply_records_last_cascade_ref(self) -> None:
        prs = [
            {"number": 13, "body": "Closes #42", "mergedAt": "2026-05-09T12:00:00Z"},
        ]
        with mock.patch.object(github_sync, "gh_pr_list_merged", return_value=prs):
            with contextlib.redirect_stdout(io.StringIO()):
                github_sync.main(["cascade"])
        state = github_sync.load_state(self._state_path())
        self.assertEqual(state["last_cascade_ref"], "2026-05-09T12:00:00Z")

    def test_dry_run_does_not_record_cascade_ref(self) -> None:
        prs = [
            {"number": 14, "body": "Closes #42", "mergedAt": "2026-05-10T00:00:00Z"},
        ]
        with mock.patch.object(github_sync, "gh_pr_list_merged", return_value=prs):
            with contextlib.redirect_stdout(io.StringIO()):
                github_sync.main(["cascade", "--dry-run"])
        self.assertFalse(self._state_path().exists())

    def test_since_arg_is_passed_to_pr_lister(self) -> None:
        with mock.patch.object(
            github_sync, "gh_pr_list_merged", return_value=[]
        ) as lister:
            with contextlib.redirect_stdout(io.StringIO()):
                github_sync.main(["cascade", "--since", "2026-01-01T00:00:00Z"])
        lister.assert_called_once_with("2026-01-01T00:00:00Z")

    def test_state_last_cascade_ref_used_when_since_absent(self) -> None:
        state = github_sync._empty_state()
        state["last_cascade_ref"] = "2026-02-02T00:00:00Z"
        github_sync.save_state(state, self._state_path())
        with mock.patch.object(
            github_sync, "gh_pr_list_merged", return_value=[]
        ) as lister:
            with contextlib.redirect_stdout(io.StringIO()):
                github_sync.main(["cascade"])
        lister.assert_called_once_with("2026-02-02T00:00:00Z")


# -----------------------------------------------------------------------------
# state subcommand
# -----------------------------------------------------------------------------


class StateCommandTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def test_state_prints_valid_json_empty_when_unsynced(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = github_sync.main(["state"])
        self.assertEqual(rc, 0)
        parsed = json.loads(out.getvalue())
        self.assertEqual(parsed["version"], 1)
        self.assertEqual(parsed["mappings"], {})


class FriendlyAliasTests(unittest.TestCase):
    """US0057/RFC0024: a synced artefact's GitHub issue number is a resolvable friendly
    alias; the id (ULID) stays canonical; offline is a no-op."""

    def _bug(self, root: Path, name: str, issue: int | None) -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        gh = f"> **GitHub Issue:** #{issue}\n" if issue else ""
        p = d / f"{name}.md"
        p.write_text(f"# {name}: x\n\n> **Status:** Open\n> **Severity:** Low\n{gh}\n", encoding="utf-8")
        return p

    def test_friendly_number_resolves_to_canonical(self) -> None:
        from lib import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, "BG-01JQK3F8-fix", issue=42)
            amap = sdlc_md.alias_map(root)
            self.assertEqual(amap.get(sdlc_md.norm_id("GH42")), "BG-01JQK3F8")

    def test_no_issue_no_friendly_alias(self) -> None:
        from lib import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, "BG-01JQK3F8-fix", issue=None)  # never synced (offline)
            self.assertEqual(sdlc_md.alias_map(root), {})

    def test_set_issue_field_keeps_id_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root, "BG-01JQK3F8-fix", issue=None)
            github_sync.set_github_issue_field(p, 42)
            self.assertTrue(p.exists())  # filename (canonical id) unchanged
            self.assertIn("#42", p.read_text(encoding="utf-8"))


class LowercaseDiscoveryTests(unittest.TestCase):
    """US0077/CR0181: walk_local finds lowercase-named artefacts (was a case-sensitive glob)."""

    def test_lowercase_cr_is_found(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"; cd.mkdir(parents=True)
            (cd / "cr0001-lower.md").write_text(
                "# CR-0001: lower\n\n> **Status:** Proposed\n> **Priority:** Low\n> **Type:** X\n",
                encoding="utf-8")
            recs = list(github_sync.walk_local("cr", repo_root=root))
            self.assertEqual(len(recs), 1)  # found despite the lowercase filename
            from lib import sdlc_md
            self.assertEqual(sdlc_md.norm_id(recs[0].rec_id), "CR0001")


class SharedDiscoveryTests(unittest.TestCase):
    """US0097/CR0181: discovery flows through the shared layer (lowercase-safe), no dup table."""

    def test_lowercase_named_cr_is_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            crd = Path(d) / "sdlc-studio" / "change-requests"
            crd.mkdir(parents=True)
            (crd / "cr-0009-lower.md").write_text(SAMPLE_CR, encoding="utf-8")  # lowercase name
            self.assertEqual(len(list(github_sync.walk_local("cr", Path(d)))), 1)

    def test_no_private_type_dirs_duplicate(self) -> None:
        self.assertFalse(hasattr(github_sync, "TYPE_DIRS"))          # no local dup of the type map
        self.assertEqual(github_sync._MIRRORED, ("cr", "story", "epic"))


class RootFlagTests(unittest.TestCase):
    """US0097/CR0181: --root works from outside the repo; STATE_PATH resolves against it."""

    def test_walk_local_honours_root_without_chdir(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            crd = Path(d) / "sdlc-studio" / "change-requests"
            crd.mkdir(parents=True)
            (crd / "CR-0001-x.md").write_text(SAMPLE_CR, encoding="utf-8")
            self.assertEqual(len(list(github_sync.walk_local("cr", Path(d)))), 1)  # cwd elsewhere

    def test_state_path_resolves_against_root(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sp = github_sync._state_path(root)
            self.assertEqual(sp, root / "sdlc-studio" / ".local" / "github-sync-state.json")
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            github_sync.save_state(github_sync._empty_state(), sp)
            self.assertTrue(sp.exists())
            self.assertEqual(github_sync.load_state(sp)["version"], 1)


# Obviously-fake, pattern-shaped sentinels (never real secrets).
_FAKE_AWS = "AKIA" + "IOSFODNN7EXAMPLE"                       # AKIA + 16
_FAKE_GH = "ghp_" + "0123456789abcdefghijklmnopqrstuvwxyz01"  # ghp_ + 38

CR_WITH_SECRET = f"""\
# CR-0003: leaks a token

> **Status:** Proposed
> **Priority:** P2
> **Type:** feature-request
> **Date:** 2026-07-09

## Summary

Debug note: aws key {_FAKE_AWS} and token {_FAKE_GH} left in the body.
"""


class SecretScanTests(unittest.TestCase):
    def test_detects_each_token_class(self) -> None:
        f = github_sync.scan_secrets(f"x {_FAKE_AWS} y {_FAKE_GH} z")
        kinds = {d["kind"] for d in f}
        self.assertIn("aws-access-key", kinds)
        self.assertIn("github-token", kinds)

    def test_clean_text_is_empty(self) -> None:
        self.assertEqual(github_sync.scan_secrets("just prose about rate limiting /login"), [])

    def test_findings_are_redacted_never_raw(self) -> None:
        f = github_sync.scan_secrets(_FAKE_AWS)
        self.assertTrue(f)
        for d in f:
            self.assertNotIn(_FAKE_AWS, d["redacted"])   # never the raw token
            self.assertIn("***", d["redacted"])
            self.assertIn("len=", d["redacted"])

    def test_repo_is_public_maps_visibility(self) -> None:
        with mock.patch.object(github_sync, "gh",
                               return_value=subprocess_result(0, "PUBLIC\n", "")):
            self.assertTrue(github_sync.repo_is_public())
        with mock.patch.object(github_sync, "gh",
                               return_value=subprocess_result(0, "PRIVATE\n", "")):
            self.assertFalse(github_sync.repo_is_public())
        with mock.patch.object(github_sync, "gh",
                               return_value=subprocess_result(1, "", "boom")):
            self.assertIsNone(github_sync.repo_is_public())   # unknown on error


class SecretPushTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        (self.fixture.tmp / "sdlc-studio/change-requests/CR-0003-leak.md").write_text(
            CR_WITH_SECRET)
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def _gh(self, visibility: str):
        created = []
        def fake_gh(*args, capture=True):
            if args[:2] == ("repo", "view"):
                return subprocess_result(0, f"{visibility}\n", "")
            if args[:2] == ("issue", "create"):
                created.append(args)
                return subprocess_result(0, "https://github.com/x/y/issues/77\n", "")
            if args[:2] == ("issue", "list"):
                return subprocess_result(0, "[]", "")
            return subprocess_result(0, "", "")
        return fake_gh, created

    def test_public_target_refuses_secret_record(self) -> None:
        fake_gh, created = self._gh("PUBLIC")
        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 1)                                   # non-zero: something blocked
        self.assertIn("REFUSED CR-0003", buf.getvalue())
        self.assertNotIn(_FAKE_AWS, buf.getvalue())               # redacted in the message
        # no issue was created for the leaking CR
        self.assertFalse(any(("issue", "create") == a[:2] for a in created if "CR-0003" in str(a))
                         or any("CR-0003" in str(a) for a in created))

    def test_unknown_visibility_also_refuses(self) -> None:
        fake_gh, _ = self._gh("")                                 # gh returns blank -> None
        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            buf = io.StringIO()
            with contextlib.redirect_stderr(buf):
                rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 1)
        self.assertIn("unknown-visibility", buf.getvalue())

    def test_private_target_allows_secret_record(self) -> None:
        fake_gh, created = self._gh("PRIVATE")
        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 0)                                   # private is safe
        self.assertTrue(any(a[:2] == ("issue", "create") for a in created))

    def test_allow_secrets_override_skips_scan(self) -> None:
        all_calls = []

        def fake_gh(*args, capture=True):
            all_calls.append(args)
            if args[:2] == ("issue", "create"):
                return subprocess_result(0, "https://github.com/x/y/issues/77\n", "")
            if args[:2] == ("issue", "list"):
                return subprocess_result(0, "[]", "")
            return subprocess_result(0, "PUBLIC\n", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr", "--allow-secrets"])
        self.assertEqual(rc, 0)
        # --allow-secrets skips the scan, so visibility is never consulted
        self.assertFalse(any(a[:2] == ("repo", "view") for a in all_calls))
        self.assertTrue(any(a[:2] == ("issue", "create") for a in all_calls))

class AdoptExistingIssueTests(unittest.TestCase):
    """CR0206: push must adopt an existing [rec_id]-titled issue instead of creating a
    duplicate - the crash/timeout-after-create dedupe."""

    def setUp(self) -> None:
        self.fixture = FixtureRepo()
        self._cwd = Path.cwd()
        import os
        os.chdir(self.fixture.tmp)

    def tearDown(self) -> None:
        import os
        os.chdir(self._cwd)
        self.fixture.cleanup()

    def test_push_adopts_titled_issue_and_does_not_create(self) -> None:
        created_calls = []

        def fake_gh(*args, capture=True):
            if args[:2] == ("issue", "list"):
                # a previous run already created the issue for CR-0001
                return subprocess_result(0, json.dumps([
                    {"number": 77, "title": "[CR-0001] Rate-limit the login endpoint",
                     "state": "OPEN", "labels": [], "body": "", "url": "",
                     "updatedAt": "", "createdAt": ""}]), "")
            if args[:2] == ("issue", "create"):
                created_calls.append(args)
                return subprocess_result(0, "/issues/999", "")
            return subprocess_result(0, "", "")

        with mock.patch.object(github_sync, "gh", side_effect=fake_gh):
            rc = github_sync.main(["push", "--type", "cr"])
        self.assertEqual(rc, 0)
        self.assertEqual(created_calls, [], "push created a duplicate instead of adopting")
        # CR-0001 now points at the adopted #77, not a new issue
        path = self.fixture.tmp / "sdlc-studio/change-requests/CR-0001-rate-limit.md"
        self.assertIn("**GitHub Issue:** #77", path.read_text())


if __name__ == "__main__":
    unittest.main()
