"""Unit tests for verify_ac.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import signal
import stat
import sys
import subprocess
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
import workspace  # noqa: E402 - the shared "am I in the dev repo?" check

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "verify_ac.py"
_spec = importlib.util.spec_from_file_location("verify_ac", SCRIPT_PATH)
assert _spec and _spec.loader
verify_ac = importlib.util.module_from_spec(_spec)
sys.modules["verify_ac"] = verify_ac
_spec.loader.exec_module(verify_ac)
sdlc_md = verify_ac.sdlc_md  # shared parsing helpers, via the loaded module
from lib import run_state  # noqa: E402 - reachable once verify_ac has put scripts/ on the path


def _load_mutation():
    """The sibling `mutation` module - the WRITER of the ledger these tests read back.

    Loaded rather than faked: a ledger hand-built as JSON would pin this suite to a shape
    nothing emits, which is the dead-reader defect the testing guidance names by name.
    """
    import mutation  # noqa: PLC0415 - scripts/ is on the path once verify_ac has loaded
    return mutation


def _quiet_main(*args, **kwargs):
    """Run verify_ac.main with its `[APL]`/`[DRY]`/`wrote ...` progress lines suppressed, so the
    verify tests do not leak them into the suite output."""
    with contextlib.redirect_stdout(io.StringIO()):
        return verify_ac.main(*args, **kwargs)


def _quiet_cmd_run(args):
    with contextlib.redirect_stdout(io.StringIO()):
        return verify_ac.cmd_run(args)


PASSING_STORY = """\
# US0001: Login flow

## Acceptance Criteria

### AC1: Happy path email login
- **Given** a valid account
- **When** the user submits the form
- **Then** they see the dashboard
- **Verify:** file scripts/repo_map.py

### AC2: Uses current password hashing
- **Given** a stored user
- **When** the user logs in
- **Then** the hash matches
- **Verify:** shell echo ok
- **Verified:** yes (2026-01-01)

### AC3: Manual check only
- **Given** regulatory requirement
- **When** audited
- **Then** records exist
"""

BULLET_STORY = """\
# US0003: Bullet-style AC

## Acceptance Criteria

- **AC1:** Search returns ranked results
  - **Given** an index
  - **When** I search
  - **Verify:** file scripts/repo_map.py
- **AC2:** Handles empty query
  - **Given** no query
  - **Then** a 422
  - **Verify:** shell echo ok
  - **Verified:** yes (2026-01-01)
"""

FAILING_STORY = """\
# US0002: Broken path

## Acceptance Criteria

### AC1: Missing file
- **Given** x
- **When** y
- **Then** z
- **Verify:** file does-not-exist.txt
- **Verified:** yes (2026-01-01)
"""


class FixtureRoot:
    def __init__(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="verify_ac_test_"))
        (self.tmp / "scripts").mkdir()
        (self.tmp / "scripts" / "repo_map.py").write_text("# marker\n")
        stories = self.tmp / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        (stories / "US0001-login.md").write_text(PASSING_STORY)
        (stories / "US0002-broken.md").write_text(FAILING_STORY)

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class ParseTests(unittest.TestCase):
    def test_parse_extracts_three_acs(self) -> None:
        blocks = verify_ac.parse_story(PASSING_STORY)
        self.assertEqual(len(blocks), 3)
        ids = [b.ac_id for b in blocks]
        self.assertEqual(ids, ["AC1", "AC2", "AC3"])

    def test_parse_extracts_bullet_style_acs(self) -> None:
        # BG0003: bullet-style AC (- **AC1:**) must be parsed, not ignored.
        blocks = verify_ac.parse_story(BULLET_STORY)
        ids = [b.ac_id for b in blocks]
        self.assertEqual(ids, ["AC1", "AC2"])
        self.assertEqual(blocks[0].verifier, "file scripts/repo_map.py")
        self.assertEqual(blocks[1].verified_state, "yes")

    def test_verifier_captured_on_ac1(self) -> None:
        blocks = verify_ac.parse_story(PASSING_STORY)
        self.assertEqual(blocks[0].verifier, "file scripts/repo_map.py")
        self.assertIsNone(blocks[0].verified_state)

    def test_verified_yes_captured_on_ac2(self) -> None:
        blocks = verify_ac.parse_story(PASSING_STORY)
        self.assertEqual(blocks[1].verifier, "shell echo ok")
        self.assertEqual(blocks[1].verified_state, "yes")

    def test_manual_ac_has_no_verifier(self) -> None:
        blocks = verify_ac.parse_story(PASSING_STORY)
        self.assertIsNone(blocks[2].verifier)

    def test_insert_after_prefers_verify_line_over_later_bullets(self) -> None:
        story = (
            "### AC1: x\n"
            "- **Given** x\n"
            "- **Verify:** file README.md\n"
            "- **Note:** extra context\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertEqual(blocks[0].insert_after, 2)
        updated = verify_ac.update_verified(story.splitlines(), blocks[0], "yes")
        # Canonical order is Given / When / Then / Verify / Verified, so the
        # new line goes directly after Verify, not after trailing bullets
        self.assertIn("**Verified:** yes", updated[3])
        self.assertIn("**Note:**", updated[4])

    def test_insert_after_tracks_last_bullet_without_verify_line(self) -> None:
        story = (
            "### AC1: x\n"
            "- **Given** x\n"
            "- **When** y\n"
            "- **Then** z\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertEqual(blocks[0].insert_after, 3)


class DSLTests(unittest.TestCase):
    def test_build_command_pytest(self) -> None:
        kind, cmd = verify_ac._build_command("pytest tests/test_x.py::test_y")
        self.assertEqual(kind, "pytest")
        self.assertIn("pytest", cmd)
        self.assertIn("tests/test_x.py::test_y", cmd)

    def test_build_command_pytest_with_k_flag_splits_into_separate_args(self) -> None:
        # BG: `pytest <path> -k <marker>` was passed as one glued argv element, so
        # pytest saw a single nonexistent "file" (path + " -k " + marker) instead of
        # a path arg and a -k arg - every such Verify line false-failed.
        kind, cmd = verify_ac._build_command(
            "pytest .claude/skills/sdlc-studio/scripts/tests/test_config.py -k override_warn")
        self.assertEqual(kind, "pytest")
        self.assertEqual(cmd, ["pytest", "-q",
                                ".claude/skills/sdlc-studio/scripts/tests/test_config.py",
                                "-k", "override_warn"])

    def test_build_command_file(self) -> None:
        kind, cmd = verify_ac._build_command("file src/auth/email.ts")
        self.assertEqual(kind, "file")
        self.assertEqual(cmd, ["test", "-e", "src/auth/email.ts"])

    def test_build_command_http(self) -> None:
        kind, cmd = verify_ac._build_command(
            'http GET http://localhost/health -- .status == "ok"'
        )
        self.assertEqual(kind, "http")
        self.assertIn("curl", cmd)
        self.assertIn("jq", cmd)

    def test_build_command_unknown_head_raises(self) -> None:
        # BG0057: an unrecognised head is an invalid verifier, not a silent shell run.
        with self.assertRaises(ValueError):
            verify_ac._build_command("ls -la nonexistent")

    def test_build_command_shell_fallback_opt_in(self) -> None:
        # The legacy whole-expression-as-shell stays available behind the explicit opt-in.
        kind, cmd = verify_ac._build_command("ls -la nonexistent", allow_fallback=True)
        self.assertEqual(kind, "shell")
        self.assertEqual(cmd, "ls -la nonexistent")

    def test_build_command_shell_prefix(self) -> None:
        kind, cmd = verify_ac._build_command("shell test -f README.md")
        self.assertEqual(kind, "shell")
        self.assertEqual(cmd, "test -f README.md")


class RunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = FixtureRoot()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_dry_run_passes_valid_file(self) -> None:
        rc = _quiet_main(
            [
                "run",
                "--story",
                str(self.fixture.tmp / "sdlc-studio/stories/US0001-login.md"),
                "--dry-run",
                "--repo-root",
                str(self.fixture.tmp),
                "--report",
                str(self.fixture.tmp / ".local/verify-report.json"),
            ]
        )
        self.assertEqual(rc, 0, "expected all ACs to pass in dry run")

    def test_dry_run_flags_missing_file(self) -> None:
        rc = _quiet_main(
            [
                "run",
                "--story",
                str(self.fixture.tmp / "sdlc-studio/stories/US0002-broken.md"),
                "--dry-run",
                "--repo-root",
                str(self.fixture.tmp),
                "--report",
                str(self.fixture.tmp / ".local/verify-report.json"),
            ]
        )
        self.assertEqual(rc, 1, "expected failure exit code for broken story")

    def test_apply_mode_updates_verified_state(self) -> None:
        story = self.fixture.tmp / "sdlc-studio/stories/US0001-login.md"
        rc = _quiet_main(
            [
                "run",
                "--story",
                str(story),
                "--repo-root",
                str(self.fixture.tmp),
                "--report",
                str(self.fixture.tmp / ".local/verify-report.json"),
            ]
        )
        self.assertEqual(rc, 0)
        # AC1 initially had no Verified line; apply mode should add one
        updated = story.read_text()
        self.assertIn("**Verified:** yes", updated)
        # Report should be written
        report_path = self.fixture.tmp / ".local/verify-report.json"
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text())
        self.assertIn("US0001-login", report["stories"])

    def test_apply_mode_downgrades_stale_yes_on_failure(self) -> None:
        story = self.fixture.tmp / "sdlc-studio/stories/US0002-broken.md"
        rc = _quiet_main(
            [
                "run",
                "--story",
                str(story),
                "--repo-root",
                str(self.fixture.tmp),
                "--report",
                str(self.fixture.tmp / ".local/verify-report.json"),
            ]
        )
        self.assertEqual(rc, 1)
        updated = story.read_text()
        # AC1 was Verified: yes in fixture, verifier fails, should become no
        self.assertIn("**Verified:** no", updated)
        self.assertNotIn("yes (2026-01-01)", updated)
        # The downgrade must be counted as stale in the report
        report = json.loads(
            (self.fixture.tmp / ".local/verify-report.json").read_text()
        )
        self.assertEqual(report["stories"]["US0002-broken"]["stale"], 1)

    def test_passing_story_reports_zero_stale(self) -> None:
        rc = _quiet_main(
            [
                "run",
                "--story",
                str(self.fixture.tmp / "sdlc-studio/stories/US0001-login.md"),
                "--repo-root",
                str(self.fixture.tmp),
                "--report",
                str(self.fixture.tmp / ".local/verify-report.json"),
            ]
        )
        self.assertEqual(rc, 0)
        report = json.loads(
            (self.fixture.tmp / ".local/verify-report.json").read_text()
        )
        self.assertEqual(report["stories"]["US0001-login"]["stale"], 0)

    def test_dry_run_counts_stale_downgrade_without_writing(self) -> None:
        story = self.fixture.tmp / "sdlc-studio/stories/US0002-broken.md"
        before = story.read_text()
        report = verify_ac.verify_story(
            story, dry_run=True, timeout=10, repo_root=self.fixture.tmp
        )
        self.assertEqual(report.stale, 1)
        self.assertEqual(story.read_text(), before)


class UpdateTests(unittest.TestCase):
    def test_update_verified_replaces_existing_state(self) -> None:
        story = "### AC1: x\n- **Given** x\n- **Verify:** file README.md\n- **Verified:** no (2026-01-01)\n"
        lines = story.splitlines()
        blocks = verify_ac.parse_story(story)
        updated = verify_ac.update_verified(lines, blocks[0], "yes")
        joined = "\n".join(updated)
        self.assertIn("**Verified:** yes", joined)
        self.assertNotIn("**Verified:** no", joined)

    def test_update_verified_inserts_new_line_when_absent(self) -> None:
        story = "### AC1: x\n- **Given** x\n- **Verify:** file README.md\n"
        lines = story.splitlines()
        blocks = verify_ac.parse_story(story)
        updated = verify_ac.update_verified(lines, blocks[0], "yes")
        joined = "\n".join(updated)
        self.assertIn("**Verified:** yes", joined)


class HardeningTests(unittest.TestCase):
    def test_update_verified_clamps_out_of_bounds_insert(self) -> None:
        lines = ["### AC1: x", "- **Verify:** file README.md"]
        block = verify_ac.ACBlock(
            heading_line=0,
            ac_id="AC1",
            title="x",
            verifier="file README.md",
            insert_after=99,  # past EOF
        )
        updated = verify_ac.update_verified(lines, block, "yes")
        self.assertIn("**Verified:** yes", "\n".join(updated))

    def test_update_verified_handles_empty_lines(self) -> None:
        block = verify_ac.ACBlock(
            heading_line=0, ac_id="AC1", title="x", insert_after=5
        )
        self.assertEqual(verify_ac.update_verified([], block, "yes"), [])

    def test_run_verifier_shell_pass_and_fail(self) -> None:
        ok = verify_ac.run_verifier("shell echo ok", timeout=10, cwd=Path("."))
        self.assertTrue(ok.ok)
        self.assertEqual(ok.kind, "shell")
        bad = verify_ac.run_verifier("shell false", timeout=10, cwd=Path("."))
        self.assertFalse(bad.ok)

    def test_verify_story_preserves_non_ascii(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_unicode_"))
        try:
            (tmp / "scripts").mkdir()
            (tmp / "scripts" / "repo_map.py").write_text("# marker\n", encoding="utf-8")
            story = tmp / "story.md"
            story.write_text(
                "# US0009: Café checkout – naïve flow\n\n"
                "## Acceptance Criteria\n\n"
                "### AC1: Existing file\n"
                "- **Verify:** file scripts/repo_map.py\n",
                encoding="utf-8",
            )
            report = verify_ac.verify_story(
                story, dry_run=False, timeout=10, repo_root=tmp
            )
            self.assertEqual(report.verified, 1)
            text = story.read_text(encoding="utf-8")
            self.assertIn("Café checkout", text)
            self.assertIn("naïve", text)
            self.assertIn("**Verified:** yes", text)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class ReportHistoryTests(unittest.TestCase):
    """CR0005: dry-run report enumerates pending flips; runs append to history."""

    def test_dry_run_records_flips_without_modifying_file(self) -> None:
        fr = FixtureRoot()
        try:
            p = fr.tmp / "sdlc-studio" / "stories" / "US0001-login.md"
            before = p.read_text()
            report = verify_ac.verify_story(p, dry_run=True, timeout=10, repo_root=fr.tmp)
            flips = {f["ac"]: (f["old_state"], f["new_state"]) for f in report.flips}
            self.assertEqual(flips.get("AC1"), ("none", "yes"))  # AC1 would flip to yes
            self.assertEqual(p.read_text(), before)              # dry-run touches nothing
        finally:
            fr.cleanup()

    def test_write_report_has_flips_and_dry_run_flag(self) -> None:
        fr = FixtureRoot()
        try:
            p = fr.tmp / "sdlc-studio" / "stories" / "US0001-login.md"
            rep = verify_ac.verify_story(p, dry_run=True, timeout=10, repo_root=fr.tmp)
            out = fr.tmp / "r.json"
            verify_ac.write_report(out, [rep], dry_run=True)
            data = json.loads(out.read_text())
            self.assertTrue(data["dry_run"])
            self.assertTrue(data["stories"]["US0001-login"]["flips"])
        finally:
            fr.cleanup()

    def test_history_is_append_only(self) -> None:
        fr = FixtureRoot()
        try:
            p = fr.tmp / "sdlc-studio" / "stories" / "US0001-login.md"
            rep = verify_ac.verify_story(p, dry_run=True, timeout=10, repo_root=fr.tmp)
            hist = fr.tmp / "sdlc-studio" / ".local" / "verify-history.jsonl"
            verify_ac.append_history(hist, [rep], True)
            verify_ac.append_history(hist, [rep], True)
            lines = hist.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2)
            rec = json.loads(lines[0])
            self.assertEqual(rec["story"], "US0001-login")
            self.assertIn("verified", rec)
        finally:
            fr.cleanup()


class EvalVerbTests(unittest.TestCase):
    """CR0006: graded `eval <cmd> --threshold X` verifier (pluggable, stubbed)."""

    def _eval(self, expr):
        return verify_ac.run_verifier(expr, timeout=10, cwd=Path("."))

    def test_passes_at_or_above_threshold(self) -> None:
        r = self._eval("eval echo '{\"score\": 0.9}' --threshold 0.8")
        self.assertTrue(r.ok)
        self.assertEqual(r.score, 0.9)
        self.assertEqual(r.kind, "eval")

    def test_fails_below_threshold(self) -> None:
        r = self._eval("eval echo '{\"score\": 0.5}' --threshold 0.8")
        self.assertFalse(r.ok)
        self.assertEqual(r.score, 0.5)

    def test_missing_threshold_errors(self) -> None:
        r = self._eval("eval echo '{\"score\": 0.9}'")
        self.assertFalse(r.ok)
        self.assertEqual(r.kind, "eval")

    def test_non_numeric_score_fails(self) -> None:
        r = self._eval("eval echo 'not json' --threshold 0.5")
        self.assertFalse(r.ok)
        self.assertIsNone(r.score)

    def test_exact_threshold_passes(self) -> None:
        # score == threshold must pass (>=, not >).
        r = self._eval("eval echo '{\"score\": 0.8}' --threshold 0.8")
        self.assertTrue(r.ok)

    def test_non_numeric_threshold_fails_cleanly(self) -> None:
        # A malformed threshold must fail as kind eval, not crash.
        r = self._eval("eval echo '{\"score\": 0.9}' --threshold 1.2.3")
        self.assertFalse(r.ok)
        self.assertEqual(r.kind, "eval")

    def test_manual_verify_line_counted_not_shelled(self) -> None:
        # BG0028: `Verify: manual ...` is counted manual, never executed (shelling timed out -> failed)
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_manual_"))
        try:
            story = tmp / "US0001-x.md"
            story.write_text(
                "# US0001: x\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: human check\n- **Given** a thing\n- **Verify:** manual confirm the dashboard loads\n\n"
                "### AC2: mixed\n- **Given** y\n- **Verify:** manual + `pnpm test`\n", encoding="utf-8")
            rep = verify_ac.verify_story(story, dry_run=True, timeout=5, repo_root=tmp)
            self.assertEqual(rep.manual, 2)
            self.assertEqual(rep.failed, 0)   # not shelled, not failed
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_real_command_not_treated_as_manual(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_cmd_"))
        try:
            story = tmp / "US0002-y.md"
            story.write_text(
                "# US0002: y\n\n> **Status:** Done\n\n## Acceptance Criteria\n\n"
                "### AC1: runs\n- **Given** y\n- **Verify:** shell echo ok\n", encoding="utf-8")
            rep = verify_ac.verify_story(story, dry_run=True, timeout=5, repo_root=tmp)
            self.assertEqual(rep.manual, 0)   # a real command is not manual
            self.assertEqual(rep.verified, 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class CanonicalPlacementTests(unittest.TestCase):
    """BG0051: multiple insertions in one run must not shift later blocks - every
    new Verified line lands directly after its own AC's Verify line."""

    STORY = (
        "# US0009: multi\n\n## Acceptance Criteria\n\n"
        "### AC1: a\n- **Given** g\n- **When** w\n- **Then** t\n"
        "- **Verify:** shell true\n\n"
        "### AC2: b\n- **Given** g\n- **When** w\n- **Then** t\n"
        "- **Verify:** shell true\n\n"
        "### AC3: c\n- **Given** g\n- **When** w\n- **Then** t\n"
        "- **Verify:** shell true\n"
    )

    def test_all_inserted_verified_lines_follow_their_verify_lines(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            story = sd / "US0009-multi.md"
            story.write_text(self.STORY, encoding="utf-8")
            rc = _quiet_main(["run", "--story", str(story), "--repo-root", str(root),
                                 "--report", str(root / ".local" / "r.json")])
            self.assertEqual(rc, 0)
            lines = story.read_text(encoding="utf-8").splitlines()
            verified_idx = [i for i, l in enumerate(lines) if "**Verified:**" in l]
            self.assertEqual(len(verified_idx), 3)
            for i in verified_idx:
                self.assertIn("**Verify:**", lines[i - 1],
                              f"Verified at line {i} does not follow its Verify:\n" +
                              "\n".join(lines))


class RunnerAvailabilityTests(unittest.TestCase):
    """CR0145: a Verify runner absent from THIS machine's PATH draws an advisory
    note that owns the author-vs-CI ambiguity - never a block."""

    def test_missing_runner_flagged_with_path_ambiguity_wording(self) -> None:
        msg = verify_ac.lint_runner_available("pytest tests/test_x.py::T::t",
                                              _which=lambda tok: None)
        self.assertIsNotNone(msg)
        self.assertIn("this machine's PATH", msg)
        self.assertIn("runs elsewhere", msg)

    def test_present_runner_not_flagged(self) -> None:
        self.assertIsNone(verify_ac.lint_runner_available(
            "pytest tests/test_x.py", _which=lambda tok: "/usr/bin/pytest"))

    def test_manual_and_shell_exempt(self) -> None:
        self.assertIsNone(verify_ac.lint_runner_available("manual check the dashboard",
                                                          _which=lambda tok: None))
        self.assertIsNone(verify_ac.lint_runner_available("shell echo ok",
                                                          _which=lambda tok: None))

    def test_http_checks_curl_and_jq(self) -> None:
        msg = verify_ac.lint_runner_available("http GET /health -- .ok",
                                              _which=lambda tok: None if tok == "jq" else "/bin/x")
        self.assertIsNotNone(msg)
        self.assertIn("jq", msg)


class LintVerifierTests(unittest.TestCase):
    """CR0085: flag Verify lines that fall through to shell as mis-written runner calls."""

    def test_dsl_verbs_pass(self) -> None:
        for ok in ('jest "login happy path"', "pytest tests/test_x.py::test_y",
                   'http GET /health -- .status == "ok"', "manual check the dashboard",
                   "shell test -f dist/bundle.js"):
            self.assertIsNone(verify_ac.lint_verifier(ok), ok)

    def test_miswritten_forms_flagged(self) -> None:
        self.assertIsNotNone(verify_ac.lint_verifier('npm test -- api/test/x.test.ts -t "json"'))
        self.assertIsNotNone(verify_ac.lint_verifier("curl http://localhost:3000/health returns 200"))
        self.assertIsNotNone(verify_ac.lint_verifier("psql -c 'select 1'"))


class LintCliTests(unittest.TestCase):
    """The lint CLI over a stories DIRECTORY must work - the no-story path crashed
    with a NameError (repo_root undefined) until a benchmark delivery agent hit it."""

    def test_lint_over_a_directory_does_not_crash(self) -> None:
        import contextlib, io, tempfile
        with tempfile.TemporaryDirectory() as d:
            sdir = Path(d) / "sdlc-studio" / "stories"
            sdir.mkdir(parents=True)
            (sdir / "US0001-x.md").write_text(
                "# US0001: x\n\n- **AC1:** works\n  - Verify: `pytest tests/test_x.py`\n",
                encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = verify_ac.main(["lint", "--root", d])
            self.assertEqual(rc, 0)

    def test_lint_single_story_still_works(self) -> None:
        import contextlib, io, tempfile
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "US0001-x.md"
            p.write_text("# US0001: x\n\n- **AC1:** works\n  - Verify: `pytest tests/t.py`\n",
                         encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                rc = verify_ac.main(["lint", "--story", str(p)])
            self.assertEqual(rc, 0)


class TsCheckTests(unittest.TestCase):
    """CR0085: the AC Coverage Matrix must not be decorative."""

    def _spec(self, root: Path, body: str) -> Path:
        p = root / "ts.md"
        p.write_text("# TS0001\n\n### AC Coverage Matrix\n\n"
                     "| Story | AC | Description | Test Cases | Status |\n"
                     "| --- | --- | --- | --- | --- |\n" + body, encoding="utf-8")
        return p

    def test_complete_matrix_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._spec(Path(d), '| US0001 | AC1 | login | jest "login" | pass |\n')
            self.assertEqual(verify_ac.ts_check(p), [])

    def test_unmapped_and_unpassing_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._spec(Path(d),
                           "| US0001 | AC1 | login | -- | pass |\n"
                           '| US0001 | AC2 | logout | jest "logout" | TODO |\n')
            issues = {i["ac"]: i["issue"] for i in verify_ac.ts_check(p)}
            self.assertIn("AC1", issues)   # no test case mapped
            self.assertIn("AC2", issues)   # status not passing

    def test_placeholder_row_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = self._spec(Path(d), "| {{story}} | {{ac}} | {{desc}} | {{tc}} | {{status}} |\n")
            self.assertTrue(verify_ac.ts_check(p))

    def test_later_tables_do_not_bleed_into_the_matrix(self) -> None:
        # BG0049: the canonical spec shape puts References + Revision History AFTER
        # the matrix; their rows are not AC rows.
        with tempfile.TemporaryDirectory() as d:
            p = self._spec(Path(d),
                           '| US0001 | AC1 | login | jest "login" | pass |\n\n'
                           "## References\n\n"
                           "| Doc | Link |\n| --- | --- |\n| TSD | [tsd](../tsd.md) |\n\n"
                           "## Revision History\n\n"
                           "| Date | Author | Change |\n| --- | --- | --- |\n"
                           "| 2026-07-04 | Sam | Initial spec |\n")
            self.assertEqual(verify_ac.ts_check(p), [])

    def test_unmapped_ac_after_later_tables_still_true_positive(self) -> None:
        # The boundary must not weaken the check: a second matrix section with a
        # genuinely unmapped AC row still fails.
        with tempfile.TemporaryDirectory() as d:
            p = self._spec(Path(d),
                           "| US0001 | AC1 | login | -- | pass |\n\n"
                           "## Revision History\n\n"
                           "| Date | Author | Change |\n| --- | --- | --- |\n"
                           "| 2026-07-04 | Sam | Initial spec |\n")
            issues = {i["ac"]: i["issue"] for i in verify_ac.ts_check(p)}
            self.assertEqual(list(issues), ["AC1"])   # only the real AC row flags


class TsCheckCrossReportTests(unittest.TestCase):
    """BG0055: the verify-report cross-check must be story-qualified, not bare-AC."""

    def _spec(self, root: Path, body: str) -> Path:
        p = root / "ts.md"
        p.write_text("# TS0001\n\n### AC Coverage Matrix\n\n"
                     "| Story | AC | Description | Test Cases | Status |\n"
                     "| --- | --- | --- | --- | --- |\n" + body, encoding="utf-8")
        return p

    def _report(self, root: Path) -> Path:
        import json
        # A MERGED report: story A's AC1 failed; story B's AC1 passed (no failure entry).
        rep = {"stories": {
            "US0001-a": {"failed": 1, "failures": [{"ac": "AC1"}]},
            "US0002-b": {"failed": 0, "failures": []},
        }}
        p = root / "verify-report.json"
        p.write_text(json.dumps(rep), encoding="utf-8")
        return p

    def test_unrelated_story_same_ac_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # B.AC1 passes in the report; the matrix marks it pass. It must NOT be flagged
            # just because a *different* story's AC1 failed.
            spec = self._spec(root, '| US0002 | AC1 | logout | jest "logout" | pass |\n')
            issues = verify_ac.ts_check(spec, self._report(root))
            self.assertEqual(issues, [])

    def test_own_story_failing_ac_still_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            spec = self._spec(root, '| US0001 | AC1 | login | jest "login" | pass |\n')
            issues = verify_ac.ts_check(spec, self._report(root))
            self.assertEqual([i["ac"] for i in issues], ["AC1"])  # A.AC1 genuinely red


class TsCheckAbsentSpecTests(unittest.TestCase):
    """BG0229: a spec that could not be read is a REFUSAL, never a clean matrix.

    `ts_check` read a missing file as empty text, found no matrix rows, and reported
    'every AC is mapped to a passing test case' with exit 0 - so a moved, renamed or
    typo'd `--spec` passed a gate that had read nothing at all. Every assertion below
    therefore pins a NON-zero exit or a raised error; an rc-0 assertion here would be
    satisfied by the defect itself.
    """

    NOT_UTF8 = b"\xff\xfe\x00\x00# TS0001\n"

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def test_a_missing_spec_exits_2_and_names_the_path_tried(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            missing = Path(d) / "TS-DOES-NOT-EXIST.md"
            rc, out, err = self._run(["ts-check", "--spec", str(missing)])
            self.assertEqual(rc, 2, f"a missing spec passed as green: {out!r}")
            self.assertIn(str(missing), err, "the refusal did not name the path it tried")
            self.assertNotIn("ts-check:", out, "a summary line was printed over a spec "
                                               "that was never read")

    def test_the_refusal_names_the_resolved_path_not_the_bare_argument(self) -> None:
        """A relative --spec is anchored on the root, so the refusal must print where it
        actually looked - the whole point is telling the caller which path was wrong."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            rc, _out, err = self._run(["--root", str(root), "ts-check",
                                       "--spec", "test-specs/nope.md"])
            self.assertEqual(rc, 2)
            self.assertIn(str(root / "test-specs" / "nope.md"), err)

    def test_json_format_refuses_rather_than_printing_an_empty_finding_list(self) -> None:
        """`--format json` is what a gate parses. An empty array plus exit 0 reads as
        'no findings'; the file was never opened."""
        with tempfile.TemporaryDirectory() as d:
            missing = Path(d) / "nope.md"
            rc, out, _err = self._run(["ts-check", "--spec", str(missing), "--format", "json"])
            self.assertEqual(rc, 2)
            self.assertNotEqual(out.strip(), "[]", "a gate would read this as a clean matrix")

    def test_a_directory_given_as_spec_is_refused(self) -> None:
        """A directory reads back as empty text exactly as a missing file does."""
        with tempfile.TemporaryDirectory() as d:
            rc, _out, err = self._run(["ts-check", "--spec", d])
            self.assertEqual(rc, 2)
            self.assertIn(d, err)

    def test_ts_check_itself_raises_on_an_absent_spec(self) -> None:
        """The refusal lives in the library, so no caller can obtain [] from a spec that
        is not there - the CLI is not the only entry point."""
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                verify_ac.ts_check(Path(d) / "nope.md")

    def test_an_unreadable_spec_is_flagged_and_exits_non_zero(self) -> None:
        """Present but not valid UTF-8: the bytes exist, so a scanner walking a tree must
        survive it (it stays a returned finding, not an exception), but it must never be
        counted as a matrix with nothing wrong in it."""
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "ts.md"
            spec.write_bytes(self.NOT_UTF8)
            # Captured, not silenced: the warning naming the file is the wanted behaviour and
            # is asserted, but a green suite must say nothing or a real error hides in it.
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                issues = verify_ac.ts_check(spec)
            self.assertIn("ts.md", buf.getvalue(),
                          "the unreadable spec was not named in the warning")
            self.assertTrue(issues, "an unreadable spec reported a clean matrix")
            self.assertIn("unreadable", issues[0]["issue"])
            rc, _out, _err = self._run(["ts-check", "--spec", str(spec)])
            self.assertNotEqual(rc, 0)

    def test_a_present_empty_spec_does_not_share_the_absent_exit_code(self) -> None:
        """'Absent' and 'present but empty' are different facts. The zero-byte file is
        readable, so it is not the refusal path - only that distinction is pinned here,
        not any claim that an empty spec is a good one."""
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "ts.md"
            spec.write_text("", encoding="utf-8")
            rc, _out, _err = self._run(["ts-check", "--spec", str(spec)])
            self.assertNotEqual(rc, 2)


class TsCheckAbsentMatrixTests(unittest.TestCase):
    """A spec with NO AC Coverage Matrix asserts no coverage, and must not read as complete.

    One step further in than the absent-FILE refusal: the file is present, readable and valid
    UTF-8, but it holds no matrix. That produced zero rows, zero findings and exit 0 - the same
    output a fully mapped matrix produces, so the two states were indistinguishable from the
    command. Silence is not an assertion of coverage. Every test below therefore pins a
    NON-zero exit or a non-empty finding list where the defect produced 0 and [].

    Absence is read as NOT YET WRITTEN, never as a deliberate exemption: an exemption is a
    decision somebody made, and nothing distinguishes a decision from an omission by looking
    at what is not there.
    """

    HEADER = ("| Story | AC | Description | Test Cases | Status |\n"
              "| --- | --- | --- | --- | --- |\n")

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def _spec(self, d: str, body: str) -> Path:
        p = Path(d) / "TS0001-x.md"
        p.write_text(body, encoding="utf-8")
        return p

    def test_a_spec_with_no_matrix_section_reports_a_finding(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\n## Scope\n\nProse, and no matrix.\n")
            issues = verify_ac.ts_check(spec)
            self.assertTrue(issues, "a spec with no matrix reported a clean matrix")
            self.assertEqual(len(issues), 1, "one absent matrix reported as two findings")

    def test_a_spec_with_no_matrix_section_exits_non_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\n## Scope\n\nProse, and no matrix.\n")
            rc, out, _err = self._run(["ts-check", "--spec", str(spec)])
            self.assertEqual(rc, 1, f"a matrix-less spec passed as green: {out!r}")

    def test_the_missing_section_does_not_borrow_the_broken_invocation_exit(self) -> None:
        """Exit 2 means "the path was wrong". This spec was found and read; its CONTENT is
        the finding, so it must sit with the other content findings on exit 1."""
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\nno matrix\n")
            self.assertNotEqual(self._run(["ts-check", "--spec", str(spec)])[0], 2)

    def test_its_output_differs_from_a_complete_matrix(self) -> None:
        """The whole complaint: the two states printed the same line. Compare the real
        outputs rather than asserting a wording nobody re-runs."""
        with tempfile.TemporaryDirectory() as d:
            bare = self._spec(d, "# TS0001: x\n\nno matrix\n")
            full = Path(d) / "TS0002-x.md"
            full.write_text("# TS0002: x\n\n### AC Coverage Matrix\n\n" + self.HEADER
                            + "| US0001 | AC1 | x | jest \"x\" | pass |\n", encoding="utf-8")
            _rc_a, out_a, _ = self._run(["ts-check", "--spec", str(bare)])
            rc_b, out_b, _ = self._run(["ts-check", "--spec", str(full)])
            self.assertEqual(rc_b, 0, "a complete matrix must stay green")
            self.assertNotEqual(out_a.replace(bare.name, ""), out_b.replace(full.name, ""),
                                "the two states are still indistinguishable from the output")

    def test_a_complete_matrix_is_not_flagged(self) -> None:
        """The guard must not fire on the case it exists to tell apart."""
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\n### AC Coverage Matrix\n\n" + self.HEADER
                              + "| US0001 | AC1 | x | jest \"x\" | pass |\n")
            self.assertEqual(verify_ac.ts_check(spec), [])

    def test_a_heading_with_no_table_under_it_is_named_as_malformed(self) -> None:
        """Three readings of "no matrix" want three repairs. A heading with nothing
        parseable under it is a BROKEN section, not an unwritten one, and saying which
        is the difference between "write the matrix" and "fix the columns"."""
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\n### AC Coverage Matrix\n\nTBD.\n")
            issues = verify_ac.ts_check(spec)
            self.assertTrue(issues)
            bare = Path(d) / "TS0002-x.md"
            bare.write_text("# TS0002: x\n\nno heading at all\n", encoding="utf-8")
            self.assertNotEqual(issues[0]["issue"], verify_ac.ts_check(bare)[0]["issue"],
                                "a malformed section and an unwritten one report identically")

    def test_prose_naming_the_section_is_not_a_heading(self) -> None:
        """The heading test must stay a HEADING test. A spec that merely mentions the
        matrix in a sentence has not got one, and telling its author to fix the columns
        of a table that does not exist sends them looking for nothing."""
        with tempfile.TemporaryDirectory() as d:
            mentions = self._spec(d, "# TS0001: x\n\nAn AC Coverage Matrix will follow.\n")
            issue = verify_ac.ts_check(mentions)[0]["issue"]
            bare = Path(d) / "TS0002-x.md"
            bare.write_text("# TS0002: x\n\nnothing at all\n", encoding="utf-8")
            self.assertEqual(issue, verify_ac.ts_check(bare)[0]["issue"],
                             "a prose mention was read as a malformed section")

    def test_a_matrix_with_a_header_and_no_rows_is_a_finding(self) -> None:
        """The escape hatch the fix must close: if an empty header table were clean, an
        author could silence the new finding by pasting two lines that assert nothing."""
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\n### AC Coverage Matrix\n\n" + self.HEADER)
            self.assertTrue(verify_ac.ts_check(spec),
                            "an AC-less matrix table reported a clean matrix")

    def test_a_non_matrix_table_does_not_count_as_a_matrix(self) -> None:
        """Kills a counter that credits any table. A Revision History is not coverage.

        The CLASSIFICATION is what is pinned, not merely that something was reported: a
        counter crediting any table still produces a finding, just the wrong one ("the
        matrix has no rows" over a table that is not the matrix), and that sends the
        author to fix the columns of a Revision History. Asserting only that the list is
        non-empty leaves that mutant alive - it did, first time round.
        """
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(d, "# TS0001: x\n\n## Revision History\n\n"
                                 "| Date | Author | Change |\n| --- | --- | --- |\n"
                                 "| 2026-07-21 | a | Filed |\n")
            issues = verify_ac.ts_check(spec)
            self.assertTrue(issues,
                            "a Revision History table was counted as an AC Coverage Matrix")
            bare = Path(d) / "TS0002-x.md"
            bare.write_text("# TS0002: x\n\nno tables at all\n", encoding="utf-8")
            self.assertEqual(issues[0]["issue"], verify_ac.ts_check(bare)[0]["issue"],
                             "a Revision History table was counted as an AC Coverage Matrix")

    def test_an_absent_spec_still_refuses_with_exit_2(self) -> None:
        """The new finding must not swallow the older refusal: a path that is not there is
        still a broken invocation, not a spec whose matrix is missing."""
        with tempfile.TemporaryDirectory() as d:
            rc, _out, err = self._run(["ts-check", "--spec", str(Path(d) / "nope.md")])
            self.assertEqual(rc, 2)
            self.assertIn("nope.md", err)

    def test_epic_ts_fails_when_the_epic_s_only_spec_has_no_matrix(self) -> None:
        """The semantics change this bug is really about: an epic whose test-spec asserts
        no coverage no longer passes the epic-scope requirement."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "test-specs"
            sd.mkdir(parents=True)
            (sd / "TS0001-x.md").write_text(
                "# TS0001: x\n\n> **Epic:** [EP0001](EP0001-x.md)\n\n## Scope\n\nNo matrix.\n",
                encoding="utf-8")
            r = verify_ac.epic_test_spec_check(root, "EP0001")
            self.assertFalse(r["ok"], "an epic passed on a spec with no coverage matrix")
            self.assertEqual(r["specs"], ["TS0001-x.md"])

    def test_a_present_but_unreadable_spec_keeps_its_own_finding(self) -> None:
        """A non-UTF-8 spec must report as unreadable, not as one with no matrix - the
        repair for each is different and the wrong one wastes the reader's time."""
        with tempfile.TemporaryDirectory() as d:
            spec = Path(d) / "TS0001-x.md"
            spec.write_bytes(b"\xff\xfe\x00\x00# TS0001\n")
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                issues = verify_ac.ts_check(spec)
            self.assertEqual(len(issues), 1)
            self.assertIn("unreadable", issues[0]["issue"])


class ShellExecutionPolicyTests(unittest.TestCase):
    """BG0056/BG0057: shell execution is gated by provenance / --no-shell, and an
    unrecognised verifier does not silently fall through to shell."""

    def test_unknown_head_is_invalid_not_shell(self) -> None:
        # BG0057: a line whose head is not a DSL verb must be an invalid verifier
        # (exit 2), not executed as a shell command.
        res = verify_ac.run_verifier("frobnicate the widget", timeout=5, cwd=Path("."))
        self.assertEqual(res.kind, "invalid")
        self.assertEqual(res.exit_code, 2)

    def test_explicit_shell_fallback_opt_in_still_runs(self) -> None:
        # Back-compat: the old behaviour is available behind an explicit opt-in.
        res = verify_ac.run_verifier("true", timeout=5, cwd=Path("."), allow_fallback=True)
        self.assertEqual(res.kind, "shell")
        self.assertTrue(res.ok)

    def test_no_shell_blocks_shell_verb(self) -> None:
        # BG0056: with shell disabled, an explicit shell verb is blocked, not run.
        res = verify_ac.run_verifier("shell true", timeout=5, cwd=Path("."), allow_shell=False)
        self.assertEqual(res.kind, "blocked")
        self.assertFalse(res.ok)

    def test_no_shell_still_allows_structured_verbs(self) -> None:
        # A structured DSL verb (argv, no shell) still runs under --no-shell.
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "f.txt").write_text("x", encoding="utf-8")
            res = verify_ac.run_verifier("file f.txt", timeout=5, cwd=Path(d), allow_shell=False)
            self.assertEqual(res.kind, "file")
            self.assertTrue(res.ok)

    def test_external_provenance_story_blocks_shell(self) -> None:
        # BG0056: a story stamped `Provenance: external` must not have its shell verbs run.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = root / "US0001-ext.md"
            story.write_text(
                "# US0001: ext\n\n> **Provenance:** external\n\n## Acceptance Criteria\n\n"
                "### AC1: x\n\n- **Then** done\n- **Verify:** shell touch /tmp/pwn_bg0056\n",
                encoding="utf-8")
            rep = verify_ac.verify_story(story, dry_run=True, timeout=5, repo_root=root)
            self.assertEqual(rep.failed, 1)
            self.assertEqual(rep.failures[0]["kind"], "blocked")


class EpicTestSpecTests(unittest.TestCase):
    """CR0096: an epic must have a test-spec whose AC Coverage Matrix passes ts-check."""

    def _ts(self, root: Path, epic: str, matrix_row: str) -> None:
        d = root / "sdlc-studio" / "test-specs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "TS0001-x.md").write_text(
            f"# TS0001: x\n\n> **Epic:** [{epic}]({epic}-x.md)\n\n### AC Coverage Matrix\n\n"
            "| Story | AC | Description | Test Cases | Status |\n| --- | --- | --- | --- | --- |\n"
            + matrix_row, encoding="utf-8")

    def test_missing_test_spec_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            r = verify_ac.epic_test_spec_check(Path(d), "EP0001")
            self.assertFalse(r["ok"])

    def test_passing_matrix_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._ts(root, "EP0001", '| US0001 | AC1 | x | jest "x" | pass |\n')
            self.assertTrue(verify_ac.epic_test_spec_check(root, "EP0001")["ok"])

    def test_failing_matrix_not_ok(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._ts(root, "EP0001", "| US0001 | AC1 | x | -- | pass |\n")  # no test case mapped
            self.assertFalse(verify_ac.epic_test_spec_check(root, "EP0001")["ok"])


class EpicTestSpecOptOutTests(unittest.TestCase):
    """BG0250: `quality.epic_requires_test_spec` is documented in four places as the
    caller's opt-out from the epic-scope test-spec requirement, and was read by no code.
    These pin the read, so the documentation cannot silently become false again."""

    def _project(self, d: str, matrix_row: str, config: str | None = None) -> Path:
        root = Path(d)
        sd = root / "sdlc-studio"
        (sd / "test-specs").mkdir(parents=True, exist_ok=True)
        (sd / "test-specs" / "TS0001-x.md").write_text(
            "# TS0001: x\n\n> **Epic:** [EP0001](EP0001-x.md)\n\n### AC Coverage Matrix\n\n"
            "| Story | AC | Description | Test Cases | Status |\n| --- | --- | --- | --- | --- |\n"
            + matrix_row, encoding="utf-8")
        if config is not None:
            (sd / ".config.yaml").write_text(config, encoding="utf-8")
        return root

    def _epic_ts(self, root: Path) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(["epic-ts", "--epic", "EP0001", "--root", str(root)])
        return rc, out.getvalue(), err.getvalue()

    FAILING = "| US0001 | AC1 | x | -- | pass |\n"          # no test case mapped
    PASSING = '| US0001 | AC1 | x | jest "x" | pass |\n'

    def test_the_key_set_false_downgrades_the_failure_to_advisory(self) -> None:
        """The documented opt-out must actually change the outcome: a failing epic exits 0
        instead of 1. Red before the config read existed - the run exited 1 regardless."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING,
                                 "quality:\n  epic_requires_test_spec: false\n")
            self.assertFalse(verify_ac.epic_test_spec_check(root, "EP0001")["enforced"],
                             "epic_requires_test_spec: false was not read")
            rc, out, _err = self._epic_ts(root)
            self.assertEqual(rc, 0, f"the documented opt-out did not lift the gate: {out!r}")

    def test_the_opt_out_still_reports_the_findings_it_stops_enforcing(self) -> None:
        """An opt-out that hides the findings is a different, worse feature: the project
        staging a migration must still see which specs it owes."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING,
                                 "quality:\n  epic_requires_test_spec: false\n")
            r = verify_ac.epic_test_spec_check(root, "EP0001")
            self.assertFalse(r["ok"], "the opt-out silenced the check's own verdict")
            self.assertTrue(r["issues"], "the opt-out discarded the findings")
            _rc, out, _err = self._epic_ts(root)
            self.assertIn("no test case mapped", out, "the findings were not printed")
            self.assertIn("epic_requires_test_spec", out,
                          "the run did not say why a FAIL exited 0")

    def test_the_default_with_no_config_at_all_still_enforces(self) -> None:
        """The default is unchanged for a project that sets nothing: still exit 1."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING)
            self.assertTrue(verify_ac.epic_test_spec_check(root, "EP0001")["enforced"])
            rc, out, _err = self._epic_ts(root)
            self.assertEqual(rc, 1, f"the default stopped enforcing: {out!r}")

    def test_the_key_set_true_enforces(self) -> None:
        """Kills a read that treats the key's mere PRESENCE as the opt-out."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING,
                                 "quality:\n  epic_requires_test_spec: true\n")
            self.assertTrue(verify_ac.epic_test_spec_check(root, "EP0001")["enforced"])
            self.assertEqual(self._epic_ts(root)[0], 1)

    def test_an_unrelated_quality_key_does_not_lift_the_gate(self) -> None:
        """Kills a read of the wrong key: another `quality.*` setting must not disable
        this one."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING,
                                 "quality:\n  done_requires_verified: false\n")
            self.assertTrue(verify_ac.epic_test_spec_check(root, "EP0001")["enforced"])
            self.assertEqual(self._epic_ts(root)[0], 1)

    def test_a_passing_epic_exits_0_whichever_way_the_key_is_set(self) -> None:
        """The opt-out governs the FAILURE only; it must not turn a green run amber."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.PASSING,
                                 "quality:\n  epic_requires_test_spec: false\n")
            rc, out, _err = self._epic_ts(root)
            self.assertEqual(rc, 0)
            self.assertIn("OK", out)
            self.assertNotIn("advisory", out, "a passing run was reported as advisory")

    def test_a_non_boolean_value_warns_and_keeps_enforcing(self) -> None:
        """A value the reader cannot honour is the same defect this bug is: a setting
        acted on in good faith with no effect and no warning. It must say so, and it must
        fail safe (still enforce) rather than guess the project meant off."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING,
                                 "quality:\n  epic_requires_test_spec: maybe\n")
            rc, _out, err = self._epic_ts(root)
            self.assertEqual(rc, 1, "a value that is not a boolean silently lifted the gate")
            self.assertIn("epic_requires_test_spec", err, "the unhonoured value was silent")
            self.assertIn("maybe", err, "the warning did not name the value it could not honour")

    def test_json_output_carries_the_enforcement_state(self) -> None:
        """A programmatic caller must be able to tell "the check failed" from "the check
        failed and the project gates on it" without re-reading the config itself."""
        with tempfile.TemporaryDirectory() as d:
            root = self._project(d, self.FAILING,
                                 "quality:\n  epic_requires_test_spec: false\n")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                verify_ac.main(["epic-ts", "--epic", "EP0001", "--root", str(root),
                                "--format", "json"])
            payload = json.loads(out.getvalue())
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["enforced"])


class JestBatchTests(unittest.TestCase):
    """CR0111: resolve jest verifiers from one cached --json run."""

    SAMPLE = json.dumps({"testResults": [{"assertionResults": [
        {"fullName": "US0011: adds a valid item", "title": "adds a valid item", "status": "passed"},
        {"fullName": "US0016: equal positions resolve deterministically", "status": "failed"},
    ]}]})

    def test_parse_flattens_assertions(self):
        asserts = verify_ac._parse_jest_json("noise\n" + self.SAMPLE)
        self.assertEqual(len(asserts), 2)
        self.assertTrue(asserts[0]["ok"])
        self.assertFalse(asserts[1]["ok"])

    def test_parse_bad_json_is_empty(self):
        self.assertEqual(verify_ac._parse_jest_json("not json"), [])

    def test_resolve_pass(self):
        asserts = verify_ac._parse_jest_json(self.SAMPLE)
        r = verify_ac.resolve_jest_from_cache('jest "US0011: adds a valid item"', asserts)
        self.assertIsNotNone(r)
        self.assertTrue(r.ok)

    def test_resolve_fail(self):
        asserts = verify_ac._parse_jest_json(self.SAMPLE)
        r = verify_ac.resolve_jest_from_cache('jest "equal positions resolve deterministically"', asserts)
        self.assertFalse(r.ok)

    def test_resolve_no_match_falls_through(self):
        asserts = verify_ac._parse_jest_json(self.SAMPLE)
        self.assertIsNone(verify_ac.resolve_jest_from_cache('jest "nonexistent title"', asserts))

    def test_resolve_non_jest_verb_is_none(self):
        self.assertIsNone(verify_ac.resolve_jest_from_cache("pytest tests/x.py", [{"name": "x", "ok": True}]))

    # --- BG0337: the cache must select the SAME tests jest -t would -------------------
    def test_a_pattern_is_a_regex_not_a_literal_substring(self):
        """`jest -t` is a testNamePattern regex. Selecting by substring computes the verdict
        over a different test set, and under --release the cache stands in for the
        authoritative run in a blocking lane."""
        asserts = [
            {"name": "renders the total", "ok": False},
            {"name": "renders the totals", "ok": True},
        ]
        # `renders the total$` anchors: jest selects only the FAILING one.
        r = verify_ac.resolve_jest_from_cache('jest "renders the total$"', asserts)
        self.assertIsNotNone(r, "the pattern matches an assertion, so the cache can answer")
        self.assertFalse(r.ok, "jest -t would select the red test; the cache said green")

    def test_a_metacharacter_pattern_matching_nothing_falls_through(self):
        # Literal containment finds `a.b` inside `a.b passes`; as a regex the `.` still
        # matches, so use a pattern where the two disagree the other way.
        asserts = [{"name": "adds a valid item", "ok": True}]
        self.assertIsNone(
            verify_ac.resolve_jest_from_cache('jest "^valid item"', asserts),
            "jest -t '^valid item' selects nothing here - the cache must not claim a pass")

    def test_an_invalid_regex_falls_back_to_the_authoritative_run(self):
        asserts = [{"name": "counts (1 items", "ok": True}]
        self.assertIsNone(
            verify_ac.resolve_jest_from_cache('jest "counts (1 items"', asserts),
            "an unparseable pattern is not a verdict - the subprocess must own it")

    def test_a_plain_pattern_still_resolves(self):
        asserts = verify_ac._parse_jest_json(self.SAMPLE)
        r = verify_ac.resolve_jest_from_cache('jest "adds a valid item"', asserts)
        self.assertTrue(r.ok)


class WriteReportMergeTests(unittest.TestCase):
    """BG0037: per-story runs merge into the report instead of clobbering it."""

    def _keys(self, p):
        return set(json.loads(p.read_text(encoding="utf-8"))["stories"].keys())

    def test_sequential_runs_accumulate(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "verify-report.json"
            verify_ac.write_report(p, [verify_ac.StoryReport(path="US0011-x.md", ac_count=1, verified=1)])
            verify_ac.write_report(p, [verify_ac.StoryReport(path="US0012-x.md", ac_count=1, verified=1)])
            self.assertEqual(self._keys(p), {"US0011-x", "US0012-x"})  # both present, not clobbered

    def test_rerun_updates_in_place(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "verify-report.json"
            verify_ac.write_report(p, [verify_ac.StoryReport(path="US0011-x.md", ac_count=1, failed=1)])
            verify_ac.write_report(p, [verify_ac.StoryReport(path="US0011-x.md", ac_count=1, verified=1)])
            stories = json.loads(p.read_text(encoding="utf-8"))["stories"]
            self.assertEqual(stories["US0011-x"]["verified"], 1)  # latest result wins
            self.assertEqual(stories["US0011-x"]["failed"], 0)

    def test_fresh_rebuilds(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "verify-report.json"
            verify_ac.write_report(p, [verify_ac.StoryReport(path="US0011-x.md", ac_count=1, verified=1)])
            verify_ac.write_report(p, [verify_ac.StoryReport(path="US0012-x.md", ac_count=1, verified=1)], merge=False)
            self.assertEqual(self._keys(p), {"US0012-x"})  # --fresh path drops the prior entry


REPORT_REL = Path("sdlc-studio") / ".local" / "verify-report.json"
HISTORY_REL = Path("sdlc-studio") / ".local" / "verify-history.jsonl"


def _run_quiet(argv: list[str]) -> tuple[int, str, str]:
    """(exit, stdout, stderr) with BOTH streams captured, so a scoping run's progress and
    diagnostic lines are asserted on rather than leaked into the suite output."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = verify_ac.main(argv)
    return rc, out.getvalue(), err.getvalue()


def _scope_workspace(root: Path) -> Path:
    """Four stories - three passing, one failing - so a scope can be shown to exclude both a
    passing story and the failing one that decides the exit code."""
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "repo_map.py").write_text("# marker\n", encoding="utf-8")
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    (d / "US0001-login.md").write_text(PASSING_STORY, encoding="utf-8")
    (d / "US0002-broken.md").write_text(FAILING_STORY, encoding="utf-8")
    (d / "US0003-search.md").write_text(BULLET_STORY, encoding="utf-8")
    (d / "US0004-extra.md").write_text(
        PASSING_STORY.replace("US0001", "US0004"), encoding="utf-8")
    return root


class _ScopeCase(unittest.TestCase):
    """Shared fixture: one workspace of four stories per test, plus report accessors."""

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory(prefix="verify_ac_scope_")
        self.root = _scope_workspace(Path(self._td.name) / "proj")
        self.report = self.root / REPORT_REL

    def tearDown(self) -> None:
        self._td.cleanup()

    def _stories(self, report: Path | None = None) -> dict:
        p = report or self.report
        return json.loads(p.read_text(encoding="utf-8"))["stories"]

    def _keys(self, report: Path | None = None) -> set:
        return set(self._stories(report))


class IdListScopeTests(_ScopeCase):
    """US0394 AC1: `--ids` scopes the run to exactly the stories named."""

    def test_only_the_named_ids_run_and_an_unresolvable_id_exits_2(self) -> None:
        # comma-separated and case-insensitive: two of four stories judged and written,
        # and the failing story left out of scope does not decide the exit code
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--ids", "us0001,US0003"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self._keys(), {"US0001-login", "US0003-search"})

        # the repeated form names the same scope
        self.report.unlink()
        rc, _, err = _run_quiet(["run", "--root", str(self.root),
                                 "--ids", "US0001", "--ids", "US0003"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self._keys(), {"US0001-login", "US0003-search"})

        # a scope that DOES hold the failing story fails - so the exit above is a verdict
        # over the scope, not a constant
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--ids", "US0002"])
        self.assertEqual(rc, 1, err)

        # an id resolving to no story file is an ERROR naming it, before anything is written
        before = self.report.read_bytes()
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--ids", "US0001,US9999"])
        self.assertEqual(rc, 2)
        self.assertIn("US9999", err)
        self.assertEqual(self.report.read_bytes(), before,
                         "a refused scope still rewrote the report")


class WorklistScopeTests(_ScopeCase):
    """US0394 AC2: a tranche file is a batch source, on the planner's own tolerances."""

    def test_bullets_comments_and_duplicates_resolve_to_the_named_stories(self) -> None:
        wl = self.root / "tranche.md"
        wl.write_text(
            "# tranche 1 - the approved batch\n"
            "- US0001\n"
            "* US0003\n"
            "US0001\n"
            "  # US0002 was cut from this tranche\n"
            "- US0003\n", encoding="utf-8")
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--worklist", str(wl)])
        self.assertEqual(rc, 0, err)
        # the commented id is not read as a member, and the bullet forms are
        self.assertEqual(self._keys(), {"US0001-login", "US0003-search"})
        # de-duplicated: each story was verified ONCE, not once per mention
        lines = [json.loads(ln) for ln
                 in (self.root / HISTORY_REL).read_text(encoding="utf-8").splitlines() if ln]
        self.assertEqual([ln["story"] for ln in lines], ["US0001-login", "US0003-search"])


class RunStateScopeTests(_ScopeCase):
    """US0394 AC3: the open run's approved batch is the scope, and no run is a refusal."""

    def _bug(self, ident: str = "BG0007") -> None:
        """A real bug file for the batch to resolve. BG0360: a bug is a DELIVERY unit and its
        criteria are executed, so an id in the batch names a file that must exist - it is no
        longer quietly skipped as "not a story"."""
        bugs = self.root / "sdlc-studio" / "bugs"
        bugs.mkdir(parents=True, exist_ok=True)
        (bugs / f"{ident}-scoped.md").write_text(
            f"# {ident}: a scoped bug\n\n> **Status:** Open\n> **Severity:** Low\n"
            "> **Points:** 1\n\n## Acceptance Criteria\n\n"
            "### AC1: it is verifiable\n\n- **Verify:** manual verified at delivery\n",
            encoding="utf-8")

    def test_batch_units_run_including_bugs(self) -> None:
        self._bug()
        run_state.open_run(self.root, batch=["US0001", "BG0007", "US0003"], goal="scope test")
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--from-run"])
        self.assertEqual(rc, 0, err)
        # BG0360: the bug is verified alongside the stories rather than skipped. A lane's
        # return rule - verify your unit before returning - was unrunnable for every bug in a
        # batch while this walked stories alone.
        self.assertEqual(self._keys(),
                         {"US0001-login", "US0003-search", "BG0007-scoped"})

    def test_a_batch_id_with_no_unit_file_refuses(self) -> None:
        """The carve-out must not become a silent skip: an id resolving to nothing is read by
        the completion gate as "that unit had nothing to fail"."""
        run_state.open_run(self.root, batch=["US0001", "BG0007"], goal="dangling")
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--from-run"])
        self.assertEqual(rc, 2)
        self.assertIn("BG0007", err)

    def test_batch_stories_run_and_no_open_run_exits_2(self) -> None:
        run_state.open_run(self.root, batch=["US0001", "US0003"], goal="scope test")
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--from-run"])
        self.assertEqual(rc, 0, err)
        self.assertEqual(self._keys(), {"US0001-login", "US0003-search"})

        before = self.report.read_bytes()

        # an OPEN run whose batch resolves to nothing at all - the fallback is the same nine
        # minutes whichever way the scope comes out empty
        run_state.path(self.root).unlink()
        run_state.open_run(self.root, batch=["CR0007"], goal="requests only")
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--from-run"])
        self.assertEqual(rc, 2, err)
        self.assertEqual(self.report.read_bytes(), before,
                         "an empty batch fell back to a whole-workspace run")

        # with no run open there is no batch, and a whole-workspace fallback is exactly the
        # cost the flag exists to avoid - so it refuses instead
        run_state.path(self.root).unlink()
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--from-run"])
        self.assertEqual(rc, 2)
        self.assertIn("no run", err.lower())
        self.assertEqual(self.report.read_bytes(), before,
                         "a refused --from-run fell back to a whole-workspace run")


class ScopedReportMergeTests(_ScopeCase):
    """US0395 AC1: a scoped run leaves every out-of-scope entry exactly as it found it."""

    def test_out_of_scope_entries_including_verified_at_are_untouched(self) -> None:
        rc, _, err = _run_quiet(["run", "--root", str(self.root)])
        self.assertEqual(rc, 1, err)  # the whole workspace, including the failing story

        # Stamp every entry with its OWN distinguishable freshness fields. Re-running inside
        # the same second would otherwise produce an identical `verified_at`, and a run that
        # re-stamped the whole merged report would pass unnoticed.
        data = json.loads(self.report.read_text(encoding="utf-8"))
        for key, entry in data["stories"].items():
            entry["verified_at"] = "2020-01-01T00:00:00Z"
            entry["ac_fingerprint"] = f"sentinel-{key}"
        self.report.write_text(json.dumps(data, indent=2), encoding="utf-8")
        before = json.loads(self.report.read_text(encoding="utf-8"))["stories"]

        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--ids", "US0001,US0003"])
        self.assertEqual(rc, 0, err)
        after = self._stories()

        self.assertEqual(set(after), set(before), "a scoped run dropped an entry")
        for key in ("US0002-broken", "US0004-extra"):
            self.assertEqual(after[key], before[key],
                             f"the out-of-scope entry {key} was rewritten")
            self.assertEqual(after[key]["verified_at"], "2020-01-01T00:00:00Z",
                             f"{key} was re-stamped fresh without being verified")
            self.assertEqual(after[key]["ac_fingerprint"], f"sentinel-{key}")
        # and the in-scope entries DID move on, so the assertions above are not vacuous
        for key in ("US0001-login", "US0003-search"):
            self.assertNotEqual(after[key]["verified_at"], "2020-01-01T00:00:00Z",
                                f"{key} was in scope but kept the stale stamp")
            self.assertNotEqual(after[key]["ac_fingerprint"], f"sentinel-{key}")


class ScopedUnscopedEquivalenceTests(unittest.TestCase):
    """US0395 AC2: the scope decides WHICH stories are judged, never HOW one is judged."""

    @staticmethod
    def _timeless(entry: dict) -> dict:
        """The entry with its two WALL-CLOCK fields dropped and everything else kept.

        `verified_at` is when the run happened and `duration_ms` is how long a verifier
        took; neither is part of the verdict, and both differ between two runs of identical
        work. Every judgement field - the counts, the passed list, the failure records with
        their exit codes and stderr, the flips, the fingerprint - is compared.
        """
        out = {k: v for k, v in entry.items() if k != "verified_at"}
        out["failures"] = [{k: v for k, v in f.items() if k != "duration_ms"}
                           for f in out.get("failures", [])]
        return out

    def test_shared_story_entries_and_exit_are_identical_under_both_scopes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="verify_ac_equiv_") as d:
            # three identical copies - each run must start from the same story state, since
            # an apply run rewrites the Verified: lines it flips
            wide = _scope_workspace(Path(d) / "wide")
            narrow = _scope_workspace(Path(d) / "narrow")
            passing = _scope_workspace(Path(d) / "passing")

            rc_wide, _, err = _run_quiet(["run", "--root", str(wide)])
            self.assertEqual(rc_wide, 1, err)
            rc_narrow, _, err = _run_quiet(["run", "--root", str(narrow),
                                            "--ids", "US0001,US0002"])
            w = json.loads((wide / REPORT_REL).read_text(encoding="utf-8"))["stories"]
            n = json.loads((narrow / REPORT_REL).read_text(encoding="utf-8"))["stories"]

            self.assertEqual(set(n), {"US0001-login", "US0002-broken"})
            for key in n:
                self.assertEqual(self._timeless(n[key]), self._timeless(w[key]),
                                 f"the scope changed how {key} was judged")

            # the exit is the verdict over the stories in scope - derived from the values the
            # wide run recorded for them, not from a status string
            expected = 1 if any(w[k]["failed"] for k in n) else 0
            self.assertEqual(rc_narrow, expected)

            # a scope holding no failing story exits 0 while the wide run over the same
            # workspace exits 1, so the equality above cannot be met by a constant
            rc_pass, _, err = _run_quiet(["run", "--root", str(passing),
                                          "--ids", "US0001,US0003"])
            p = json.loads((passing / REPORT_REL).read_text(encoding="utf-8"))["stories"]
            self.assertEqual(rc_pass, 0 if not any(w[k]["failed"] for k in p) else 1, err)
            self.assertEqual(rc_pass, 0)
            for key in p:
                self.assertEqual(self._timeless(p[key]), self._timeless(w[key]),
                                 f"the scope changed how {key} was judged")


class ScopedFreshRefusalTests(_ScopeCase):
    """US0395 AC3: a rebuild combined with a scope would blank every out-of-scope verdict."""

    def test_fresh_with_a_scope_exits_2_and_writes_nothing(self) -> None:
        rc, _, err = _run_quiet(["run", "--root", str(self.root)])
        self.assertEqual(rc, 1, err)
        # an entry only a rebuild can remove, so "the report is unchanged" has teeth and the
        # unscoped --fresh below is proved still to rebuild
        data = json.loads(self.report.read_text(encoding="utf-8"))
        data["stories"]["US9999-retired"] = {"ac_count": 1, "verified": 1, "failed": 0,
                                             "verified_at": "2020-01-01T00:00:00Z",
                                             "ac_fingerprint": "sentinel-retired"}
        self.report.write_text(json.dumps(data, indent=2), encoding="utf-8")
        before = self.report.read_bytes()

        wl = self.root / "tranche.md"
        wl.write_text("- US0001\n", encoding="utf-8")
        run_state.open_run(self.root, batch=["US0001"], goal="scope test")

        for scope in (["--ids", "US0001"], ["--worklist", str(wl)], ["--from-run"]):
            rc, out, err = _run_quiet(["run", "--root", str(self.root), "--fresh", *scope])
            self.assertEqual(rc, 2, f"{scope} + --fresh was not refused")
            self.assertIn("--fresh", err)
            self.assertIn(scope[0], err, "the refusal did not name the scope flag passed")
            # both ways forward, named
            self.assertIn("drop the scope", err.lower())
            self.assertIn("drop --fresh", err.lower())
            self.assertEqual(self.report.read_bytes(), before,
                             f"{scope} + --fresh wrote the report anyway")

        # the guard is scoped, not a blanket ban: an UNSCOPED --fresh still rebuilds
        rc, _, err = _run_quiet(["run", "--root", str(self.root), "--fresh"])
        self.assertEqual(rc, 1, err)
        self.assertNotIn("US9999-retired", self._keys())


class ScaffoldMatrixTests(unittest.TestCase):
    """CR0115: scaffold the AC Coverage Matrix from an epic's stories' ACs at design time."""

    def _story(self, root: Path, story_id: str, epic: str, acs: list[tuple[str, str]]) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        body = [f"# {story_id}: x", "", f"> **Epic:** [{epic}]({epic}-x.md)", "",
                "## Acceptance Criteria", ""]
        for ac_id, title in acs:
            body += [f"### {ac_id}: {title}", "- **Given** x", "- **Then** y", ""]
        (d / f"{story_id}-x.md").write_text("\n".join(body), encoding="utf-8")

    def test_one_row_per_ac_across_n_stories(self) -> None:
        # 3 stories totalling 6 ACs -> a matrix with exactly 6 data rows.
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._story(root, "US0001", "EP0001", [("AC1", "login"), ("AC2", "logout")])
            self._story(root, "US0002", "EP0001", [("AC1", "search"), ("AC2", "page"), ("AC3", "empty")])
            self._story(root, "US0003", "EP0001", [("AC1", "rate limit")])
            matrix = verify_ac.scaffold_ac_matrix(root, "EP0001")
            data_rows = [c for ln in matrix.splitlines()
                         if (c := sdlc_md.table_cells(ln)) and c[0] != "Story"]
            self.assertEqual(len(data_rows), 6)
            pairs = {(r[0], r[1]) for r in data_rows}
            self.assertEqual(pairs, {
                ("US0001", "AC1"), ("US0001", "AC2"),
                ("US0002", "AC1"), ("US0002", "AC2"), ("US0002", "AC3"),
                ("US0003", "AC1"),
            })

    def test_every_ac_appears_exactly_once(self) -> None:
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._story(root, "US0001", "EP0001", [("AC1", "a"), ("AC2", "b"), ("AC3", "c")])
            matrix = verify_ac.scaffold_ac_matrix(root, "EP0001")
            keys = [(c[0], c[1]) for ln in matrix.splitlines()
                    if (c := sdlc_md.table_cells(ln)) and c[0] != "Story"]
            self.assertEqual(len(keys), len(set(keys)))  # no AC duplicated, none dropped
            self.assertEqual(set(keys), {("US0001", "AC1"), ("US0001", "AC2"), ("US0001", "AC3")})

    def test_description_carries_the_ac_title(self) -> None:
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._story(root, "US0001", "EP0001", [("AC1", "valid email login")])
            row = next(c for ln in verify_ac.scaffold_ac_matrix(root, "EP0001").splitlines()
                       if (c := sdlc_md.table_cells(ln)) and c[0] == "US0001")
            self.assertEqual(row[2], "valid email login")  # Description column

    def test_test_cases_and_status_left_blank_so_ts_check_flags_them(self) -> None:
        # The two judgement columns must ship blank - proven by ts-check rejecting the
        # un-filled scaffold (a no-test-case finding per AC). If the scaffold pre-filled
        # them, ts-check would pass and the coverage guard would be defeated.
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._story(root, "US0001", "EP0001", [("AC1", "a"), ("AC2", "b")])
            spec = root / "ts.md"
            spec.write_text("# TS0001\n\n" + verify_ac.scaffold_ac_matrix(root, "EP0001"),
                            encoding="utf-8")
            issues = {i["ac"]: i["issue"] for i in verify_ac.ts_check(spec)}
            self.assertEqual(set(issues), {"AC1", "AC2"})
            self.assertTrue(all("no test case mapped" in v for v in issues.values()))

    def test_other_epics_stories_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._story(root, "US0001", "EP0001", [("AC1", "in scope")])
            self._story(root, "US0002", "EP0002", [("AC1", "other epic")])
            keys = {(c[0], c[1]) for ln in verify_ac.scaffold_ac_matrix(root, "EP0001").splitlines()
                    if (c := sdlc_md.table_cells(ln)) and c[0] != "Story"}
            self.assertEqual(keys, {("US0001", "AC1")})

    def test_bullet_form_acs_are_not_silently_dropped(self) -> None:
        # The compact bullet AC (`- **AC1:** ...`) is a real story shape `parse_story`
        # handles explicitly; without that branch bullet-AC stories parse to zero ACs.
        # The scaffold must surface them too, else a whole story's ACs vanish from the
        # matrix - the exact silent coverage gap this CR exists to close. Boundary case
        # for the parse-form the other tests (heading ACs) never exercise.
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            d = root / "sdlc-studio" / "stories"
            d.mkdir(parents=True, exist_ok=True)
            (d / "US0001-x.md").write_text(
                "# US0001: x\n\n> **Epic:** [EP0001](EP0001-x.md)\n\n"
                "## Acceptance Criteria\n\n"
                "- **AC1:** first criterion\n- **AC2:** second criterion\n",
                encoding="utf-8")
            keys = [(c[0], c[1]) for ln in verify_ac.scaffold_ac_matrix(root, "EP0001").splitlines()
                    if (c := sdlc_md.table_cells(ln)) and c[0] != "Story"]
            self.assertEqual(keys, [("US0001", "AC1"), ("US0001", "AC2")])

    def test_epic_with_no_stories_yields_header_only(self) -> None:
        # Boundary: an epic with no member stories must not crash and must emit a
        # well-formed header-only matrix (zero data rows), not a placeholder row.
        with tempfile.TemporaryDirectory() as dd:
            root = Path(dd)
            self._story(root, "US0001", "EP0002", [("AC1", "elsewhere")])
            matrix = verify_ac.scaffold_ac_matrix(root, "EP0001")
            data_rows = [c for ln in matrix.splitlines()
                         if (c := sdlc_md.table_cells(ln)) and c[0] != "Story"]
            self.assertEqual(data_rows, [])
            self.assertIn("| Story | AC | Description | Test Cases | Status |", matrix)

class SharedDiscoveryTests(unittest.TestCase):
    """US0097/CR0181: verify_ac discovers lowercase-named stories too (case-insensitive)."""

    def _story(self, sd, name):
        (sd).mkdir(parents=True, exist_ok=True)
        (sd / name).write_text(
            "# US0099: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            "### AC1: a\n- **Then** x\n- **Verify:** manual check\n", encoding="utf-8")

    def test_walk_stories_finds_lowercase(self):
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / "sdlc-studio" / "stories"
            self._story(sd, "us0099-lower.md")                     # lowercase filename
            found = list(verify_ac.walk_stories(sd))
            self.assertEqual([p.name for p in found], ["us0099-lower.md"])

    def test_run_by_id_resolves_lowercase(self):
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / "sdlc-studio" / "stories"
            self._story(sd, "us0099-lower.md")
            args = verify_ac.build_parser().parse_args(
                ["run", "--dir", str(sd), "--id", "US0099", "--dry-run", "--root", d])
            self.assertEqual(_quiet_cmd_run(args), 0)           # found, not "no story file"

    def test_root_and_repo_root_bind_the_standard_dest(self):
        # flag grammar parity: `--root` is the family-standard spelling and `--repo-root`
        # is a legacy alias; BOTH bind the standard `root` dest, so a global --root before
        # the verb and the flag after it resolve to one root (never diverge to `repo_root`).
        args = verify_ac.build_parser().parse_args(["run", "--root", "/x"])
        self.assertEqual(args.root, "/x")
        args2 = verify_ac.build_parser().parse_args(["run", "--repo-root", "/y"])
        self.assertEqual(args2.root, "/y")
        before = verify_ac.build_parser().parse_args(["--root", "/z", "run"])
        self.assertEqual(before.root, "/z")


class RestrictedHttpTests(unittest.TestCase):
    """US0101/CR0186: the http verb has a scheme floor in every mode and a host allow-list
    (restricted mode via SDLC_VERIFY_HTTP_HOSTS)."""

    def setUp(self):
        import os
        self._prev = os.environ.get("SDLC_VERIFY_HTTP_HOSTS")

    def tearDown(self):
        import os
        if self._prev is None:
            os.environ.pop("SDLC_VERIFY_HTTP_HOSTS", None)
        else:
            os.environ["SDLC_VERIFY_HTTP_HOSTS"] = self._prev

    def _set(self, val):
        import os
        if val is None:
            os.environ.pop("SDLC_VERIFY_HTTP_HOSTS", None)
        else:
            os.environ["SDLC_VERIFY_HTTP_HOSTS"] = val

    def test_scheme_floor_blocks_ssrf_scheme_even_unrestricted(self):
        self._set(None)  # unrestricted
        for bad in ("file:///etc/passwd", "gopher://x/1", "ftp://h/f"):
            with self.assertRaises(ValueError):
                verify_ac._build_http(f'GET {bad} -- .x == 1')

    def test_unrestricted_allows_any_host(self):
        self._set(None)
        cmd = verify_ac._build_http('GET https://anything.example/health -- .ok == true')
        self.assertIn("anything.example", cmd)

    def test_restricted_refuses_offlist_host(self):
        self._set("localhost,127.0.0.1")
        with self.assertRaises(ValueError):
            verify_ac._build_http('GET https://evil.example/x -- .x == 1')

    def test_restricted_allows_onlist_host(self):
        self._set("localhost,127.0.0.1")
        cmd = verify_ac._build_http('GET http://localhost:8080/health -- .ok == true')
        self.assertIn("localhost", cmd)

    def test_restricted_refuses_relative_url(self):
        self._set("localhost")
        with self.assertRaises(ValueError):
            verify_ac._build_http('GET /health -- .ok == true')

    def test_run_verifier_reports_invalid_on_refused_target(self):
        self._set("localhost")
        r = verify_ac.run_verifier('http GET https://evil.example/x -- .x == 1',
                                   timeout=5, cwd=Path("."))
        self.assertFalse(r.ok)
        self.assertEqual(r.kind, "invalid")


class DebugTraceTests(unittest.TestCase):
    """CR0187 items 5/7: SDLC_DEBUG=1 emits one stderr line from a swallowed-advisory site;
    the append-only history log is bounded (rolls)."""

    def setUp(self):
        import os
        self._prev = os.environ.get("SDLC_DEBUG")

    def tearDown(self):
        import os
        if self._prev is None:
            os.environ.pop("SDLC_DEBUG", None)
        else:
            os.environ["SDLC_DEBUG"] = self._prev

    def _set(self, v):
        import os
        if v is None:
            os.environ.pop("SDLC_DEBUG", None)
        else:
            os.environ["SDLC_DEBUG"] = v

    def test_debug_silent_by_default(self):
        self._set(None)
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            sdlc_md.debug("somewhere", "detail")
        self.assertEqual(buf.getvalue(), "")

    def test_debug_emits_one_line_when_enabled(self):
        self._set("1")
        buf = io.StringIO()
        with contextlib.redirect_stderr(buf):
            sdlc_md.debug("somewhere", "boom")
        out = buf.getvalue()
        self.assertEqual(out.count("\n"), 1)             # exactly one line
        self.assertIn("somewhere", out)
        self.assertIn("boom", out)

    def test_swallowed_site_traces_under_debug(self):
        # jest_batch_cache swallows a subprocess failure; under SDLC_DEBUG it must leave a trace.
        import subprocess
        from unittest import mock
        self._set("1")
        buf = io.StringIO()
        with mock.patch.object(verify_ac.subprocess, "run",
                               side_effect=FileNotFoundError("no npx")):
            with contextlib.redirect_stderr(buf):
                res = verify_ac.jest_batch_cache(Path("."), timeout=1)
        self.assertEqual(res, [])                         # still degrades to []
        self.assertIn("jest_batch_cache", buf.getvalue())  # but traced

    def test_swallowed_site_silent_without_debug(self):
        import subprocess
        from unittest import mock
        self._set(None)
        buf = io.StringIO()
        with mock.patch.object(verify_ac.subprocess, "run",
                               side_effect=FileNotFoundError("no npx")):
            with contextlib.redirect_stderr(buf):
                verify_ac.jest_batch_cache(Path("."), timeout=1)
        self.assertEqual(buf.getvalue(), "")

    def test_history_log_rolls_when_over_cap(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "hist.jsonl"
            p.write_text("\n".join(f'{{"n": {i}}}' for i in range(10)) + "\n", encoding="utf-8")
            rolled = sdlc_md.roll_jsonl(p, max_lines=4)
            self.assertTrue(rolled)
            lines = p.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 4)
            self.assertEqual(lines[-1], '{"n": 9}')       # keeps the most recent
            # within-cap is a no-op
            self.assertFalse(sdlc_md.roll_jsonl(p, max_lines=4))


class MissingStoryExitCodeTests(unittest.TestCase):
    """BG0084: an explicitly-named --story that does not exist must exit 2, not 0 - a typo'd
    path was silently read as 'all ACs green'."""

    def test_missing_story_path_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            rc = verify_ac.main(["run", "--story", str(Path(d) / "sdlc-studio" / "US9999-x.md"),
                                 "--root", d])
            self.assertEqual(rc, 2)


class CompanionExclusionTests(unittest.TestCase):
    """BG0083: walk_stories must exclude companion docs - a consultations note under a
    story's id must not be verified (its quoted example Verify lines run arbitrary shell)."""

    def test_companion_and_non_us_files_excluded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d)
            (sd / "US0001-login.md").write_text("# US0001: x\n", encoding="utf-8")
            (sd / "US0001-login-consultations.md").write_text("# note\n", encoding="utf-8")
            (sd / "_index.md").write_text("# idx\n", encoding="utf-8")
            (sd / "usage-guide.md").write_text("# not a story\n", encoding="utf-8")
            found = [p.name for p in verify_ac.walk_stories(sd)]
            self.assertEqual(found, ["US0001-login.md"])




class RootRelativePathsTests(unittest.TestCase):
    """BG0089: run from any cwd with --root, discovery and report resolve against the repo
    root - not the cwd - so the Done gate reads the report the run actually wrote."""

    def test_dir_and_report_resolve_against_root_not_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: x\n\n## Acceptance Criteria\n\n### AC1: a\n"
                "- **Given** a\n- **When** b\n- **Then** c\n- **Verify:** file "
                + str((root / "marker.txt")) + "\n", encoding="utf-8")
            (root / "marker.txt").write_text("x\n", encoding="utf-8")
            other = Path(d) / "elsewhere"
            other.mkdir()
            import os
            cwd = os.getcwd()
            os.chdir(other)  # run from a DIFFERENT cwd
            try:
                rc = _quiet_main(["run", "--root", str(root)])
            finally:
                os.chdir(cwd)
            # the run found the story under root (not "no stories found" from cwd) and wrote
            # the report where the Done gate reads it: root/sdlc-studio/.local/
            self.assertEqual(rc, 0)
            self.assertTrue((root / "sdlc-studio" / ".local" / "verify-report.json").exists())

    def test_root_BEFORE_verb_is_honoured_not_silently_dropped(self) -> None:
        # A --root given BEFORE the verb must run verifiers against THAT tree. The global
        # --root and the --repo-root alias must resolve to one root, never diverge - a
        # dropped root would compute the pass/fail verdict against the cwd, silently wrong.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: x\n\n## Acceptance Criteria\n\n### AC1: a\n"
                "- **Given** a\n- **When** b\n- **Then** c\n- **Verify:** file "
                + str((root / "marker.txt")) + "\n", encoding="utf-8")
            (root / "marker.txt").write_text("x\n", encoding="utf-8")
            other = Path(d) / "elsewhere"
            other.mkdir()
            import os
            cwd = os.getcwd()
            os.chdir(other)  # a cwd with NO stories: a dropped root finds nothing here
            try:
                rc = _quiet_main(["--root", str(root), "run"])   # root BEFORE the verb
            finally:
                os.chdir(cwd)
            self.assertEqual(rc, 0)
            self.assertTrue((root / "sdlc-studio" / ".local" / "verify-report.json").exists())


class FencedVerifyTests(unittest.TestCase):
    """A `- **Verify:**` line shown as an example inside a ``` fence must NOT be picked up as
    the AC's real verifier - otherwise a documentation example reaches shell execution."""

    def test_fenced_verify_line_is_ignored(self) -> None:
        story = (
            "### AC1: real\n\n"
            "- **Verify:** shell true\n\n"
            "Example of a dangerous verifier:\n\n"
            "```\n- **Verify:** shell rm -rf /\n```\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0].verifier, "shell true")

    def test_real_verify_after_a_fence_still_parses(self) -> None:
        story = (
            "### AC1: real\n\n"
            "```\n- **Verify:** shell echo example\n```\n\n"
            "- **Verify:** shell true\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertEqual(blocks[0].verifier, "shell true")

    def test_inner_fence_inside_a_longer_fence_does_not_release_the_block(self) -> None:
        # BG0305: a naive toggle closed on any leading ```, so the inner ```text opener of a
        # ````markdown block ended the fence and the illustration below it became a LIVE
        # shell verifier. CommonMark closes only on the same character at the opening length
        # or longer.
        story = (
            "### AC1: real\n\n"
            "````markdown\n"
            "```text\n"
            "- **Verify:** shell echo INJECTED; exit 1\n"
            "```\n"
            "````\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertEqual(len(blocks), 1)
        self.assertIsNone(blocks[0].verifier)
        self.assertEqual(blocks[0].extra_verifiers, [])

    def test_a_tilde_fence_is_not_closed_by_a_backtick_run(self) -> None:
        story = (
            "### AC1: real\n\n"
            "~~~markdown\n"
            "```\n"
            "- **Verify:** shell echo INJECTED; exit 1\n"
            "```\n"
            "~~~\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertIsNone(blocks[0].verifier)

    def test_a_real_verify_after_the_long_fence_closes_still_parses(self) -> None:
        story = (
            "### AC1: real\n\n"
            "````markdown\n"
            "```text\n"
            "- **Verify:** shell echo example\n"
            "```\n"
            "````\n\n"
            "- **Verify:** shell true\n"
        )
        blocks = verify_ac.parse_story(story)
        self.assertEqual(blocks[0].verifier, "shell true")


class GrepVerbTests(unittest.TestCase):
    """The grep verb had zero coverage, which is why BG0125/BG0128 survived. These fail against
    the pre-fix builder (which passed a glob to rg/grep literally)."""

    def test_documented_glob_matches_present_code(self) -> None:
        """BG0125: `grep <re> src/**/*.ts` false-RED'd on present code. It must now PASS."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src" / "auth").mkdir(parents=True)
            (root / "src" / "auth" / "client.ts").write_text("export class AuthClient {}\n")
            res = verify_ac.run_verifier('grep "export class AuthClient" src/**/*.ts',
                                         timeout=30, cwd=root, allow_shell=False)
            self.assertTrue(res.ok, f"{res.kind} exit={res.exit_code} {res.stderr}")

    def test_glob_matching_nothing_fails_honestly(self) -> None:
        """An unmatched glob must FAIL (not vacuously pass) - it is a real missing target."""
        with tempfile.TemporaryDirectory() as d:
            res = verify_ac.run_verifier('grep "x" src/**/*.ts',
                                         timeout=30, cwd=Path(d), allow_shell=False)
            self.assertFalse(res.ok)

    def test_expand_globs_passes_plain_paths_through(self) -> None:
        self.assertEqual(verify_ac._expand_globs(["src/a.ts"], None), ["src/a.ts"])

    def test_expand_globs_unmatched_glob_is_literal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(verify_ac._expand_globs(["nope/**/*.zz"], Path(d)), ["nope/**/*.zz"])


class RunFileAliasTests(unittest.TestCase):
    """CR0251: --file is the flag an agent reaches for; it aliases --story."""

    def test_run_accepts_file_as_alias_for_story(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            story = Path(d) / "US0001-x.md"
            # AC checks an absolute path so it passes regardless of the verifier's cwd - the
            # test isolates the flag alias (rc 0 = parsed + ran), not path resolution.
            story.write_text(f"# US0001: x\n\n### AC1: t\n\n- **Verify:** file {story}\n")
            # --root pins the run to the tempdir: without it the report and history landed
            # in whatever project sat above the cwd, so the suite appended to the live
            # workspace's verify-history.jsonl every time it ran.
            rc = _quiet_main(["run", "--file", str(story), "--dry-run", "--root", d])
            self.assertEqual(rc, 0)


class StoryIdTests(unittest.TestCase):
    """US0192: `run --story` accepts a story ID where a story is meant - the natural
    first invocation must work, and a value that is neither fails naming both."""

    def setUp(self) -> None:
        self.fixture = FixtureRoot()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def _run(self, story_value: str) -> tuple[int, str]:
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = _quiet_main(["run", "--story", story_value, "--dry-run",
                              "--repo-root", str(self.fixture.tmp),
                              "--dir", str(self.fixture.tmp / "sdlc-studio/stories"),
                              "--report",
                              str(self.fixture.tmp / ".local/verify-report.json")])
        return rc, err.getvalue()

    def test_story_id_resolves_when_no_such_path_exists(self) -> None:
        rc, err = self._run("US0001")
        self.assertEqual(rc, 0, err)

    def test_existing_path_behaviour_unchanged(self) -> None:
        rc, _ = self._run(str(self.fixture.tmp / "sdlc-studio/stories/US0001-login.md"))
        self.assertEqual(rc, 0)

    def test_story_id_neither_path_nor_id_fails_naming_both(self) -> None:
        rc, err = self._run("US9999")
        self.assertEqual(rc, 2)
        self.assertIn("no story file at", err)   # the path lookup failed
        self.assertIn("US9999", err)
        self.assertIn("id", err.lower())         # ...and the id resolution failed

    def test_non_id_missing_path_still_plain_error(self) -> None:
        rc, err = self._run("does/not/exist.md")
        self.assertEqual(rc, 2)
        self.assertIn("no story file at", err)


class VacuousVerifierTests(unittest.TestCase):
    """A runner that exits 0 having run nothing must not count as proof (BG0193)."""

    def _run(self, script: str, kind_expr: str | None = None):
        """Execute a shell verifier that emits `script` on stdout and exits 0."""
        expr = kind_expr or f"shell printf '%s\\n' {shlex_quote(script)}"
        return verify_ac.run_verifier(expr, 30, Path.cwd())

    def test_unittest_ran_zero_tests_is_not_a_pass(self):
        r = self._run("Ran 0 tests in 0.000s")
        self.assertFalse(r.ok)
        self.assertTrue(r.vacuous)
        self.assertEqual(r.exit_code, 0)

    def test_unittest_no_tests_ran_banner_is_not_a_pass(self):
        self.assertTrue(self._run("NO TESTS RAN").vacuous)

    def test_pytest_no_tests_ran_is_not_a_pass(self):
        self.assertTrue(self._run("no tests ran in 0.01s").vacuous)

    def test_pytest_no_tests_collected_is_not_a_pass(self):
        self.assertTrue(self._run("no tests collected (93 deselected) in 0.08s").vacuous)

    def test_go_no_tests_to_run_is_not_a_pass(self):
        self.assertTrue(self._run("testing: warning: no tests to run").vacuous)
        self.assertTrue(self._run("ok  \texample.com/pkg\t0.002s [no tests to run]").vacuous)

    def test_jest_and_vitest_no_tests_found_are_not_a_pass(self):
        self.assertTrue(self._run("No tests found, exiting with code 0").vacuous)
        self.assertTrue(self._run("No test files found, exiting with code 0").vacuous)

    def test_the_failure_names_the_remedy(self):
        r = self._run("Ran 0 tests in 0.000s")
        self.assertIn("ran NO tests", r.stderr)
        self.assertIn("Re-point the Verify line", r.stderr)

    def test_a_real_passing_run_is_untouched(self):
        r = self._run("Ran 9 tests in 0.001s\n\nOK")
        self.assertTrue(r.ok)
        self.assertFalse(r.vacuous)

    def test_a_nonzero_exit_is_still_a_plain_failure_not_vacuous(self):
        r = verify_ac.run_verifier("shell printf 'Ran 0 tests in 0.000s\\n'; exit 5",
                                   30, Path.cwd())
        self.assertFalse(r.ok)
        self.assertFalse(r.vacuous)  # a shell verb owns its exit; nothing to attribute


    def test_only_test_running_verbs_are_judged_for_vacuity(self):
        # The kind guard's own contract. No verb currently SHIPPING emits a runner summary
        # through a non-test kind (`grep`/`file` run quiet), so this is defence-in-depth
        # against a future verb, and is asserted directly rather than through a verifier
        # that cannot reach the branch.
        signature = "Ran 0 tests in 0.000s"
        for kind in ("shell", "pytest", "go", "jest", "vitest", "fallback"):
            with self.subTest(kind=kind):
                self.assertTrue(verify_ac._ran_no_tests(kind, signature, ""))
        for kind in ("grep", "file", "http", "eval", "invalid", "blocked"):
            with self.subTest(kind=kind):
                self.assertFalse(verify_ac._ran_no_tests(kind, signature, ""))

    def test_unrelated_tool_output_cannot_disarm_the_check(self):
        # A blob-wide "did anything pass?" veto was tried and removed. A `shell` Verify line
        # is routinely `make test` / `npm run check`, and a co-running linter or coverage tool
        # printing "N passed" then silenced the gate entirely - a false NEGATIVE, which is a
        # worse failure than the false positive the veto was added to fix.
        for noise in ("Coverage: 12 passed", "lint: 0 failed, 1 passed", "eslint 4 passed",
                      "PASS", "ok  \tex/other\t0.010s"):
            with self.subTest(noise=noise):
                self.assertTrue(
                    verify_ac._ran_no_tests("shell", f"Ran 0 tests in 0.000s\n{noise}\n", ""),
                    "unrelated output must not speak for the runner under test")
                self.assertTrue(
                    verify_ac._ran_no_tests("shell", f"no tests ran in 0.01s\n{noise}\n", ""))

    def test_a_go_filter_matching_nothing_is_vacuous_even_beside_the_binarys_pass_line(self):
        # `testing: warning: no tests to run` is printed by the test binary, which prints PASS
        # on the same stream - so a PASS-based veto made this signature dead in every real run.
        out = ("testing: warning: no tests to run\nPASS\n"
               "ok  \tex/foo\t0.002s [no tests to run]\n")
        self.assertTrue(verify_ac._ran_no_tests("go", out, ""))

    def test_a_bare_go_warning_with_no_package_summary_is_still_vacuous(self):
        self.assertTrue(verify_ac._ran_no_tests("go", "testing: warning: no tests to run\n", ""))

    def test_a_multi_package_go_run_with_real_results_is_not_vacuous(self):
        # `go test ./...` prints `[no test files]` per package WITHOUT tests while others
        # pass. Failing that green suite would tell the author to re-point a Verify line at
        # tests that demonstrably ran.
        green = ("ok  \tex/foo\t0.012s\n"
                 "?   \tex/internal/util\t[no test files]\n"
                 "ok  \tex/bar\t0.004s\n")
        self.assertFalse(verify_ac._ran_no_tests("go", green, ""))
        self.assertFalse(verify_ac._ran_no_tests("shell", green, ""))

    def test_a_go_run_where_no_package_ran_anything_is_vacuous(self):
        none = "?   \tex/a\t[no test files]\n?   \tex/b\t[no test files]\n"
        self.assertTrue(verify_ac._ran_no_tests("go", none, ""))

    def test_a_go_run_filter_matching_nothing_is_still_vacuous(self):
        # The package line carries a bracket suffix, so it is not evidence anything ran.
        out = "testing: warning: no tests to run\nok  \tex/foo\t0.002s [no tests to run]\n"
        self.assertTrue(verify_ac._ran_no_tests("go", out, ""))

    def test_a_jest_workspace_with_one_project_empty_is_not_vacuous(self):
        mixed = "PASS src/a.test.js\nNo tests found, exiting with code 0\n"
        self.assertFalse(verify_ac._ran_no_tests("jest", mixed, ""))
        self.assertTrue(verify_ac._ran_no_tests("jest", "No tests found, exiting with code 0\n", ""))

    def test_a_partly_deselected_pytest_run_is_not_vacuous(self):
        self.assertFalse(verify_ac._ran_no_tests("shell", "3 passed, 90 deselected in 0.08s\n", ""))
        self.assertTrue(verify_ac._ran_no_tests("shell", "no tests ran in 0.01s\n", ""))

    def test_the_signature_is_read_from_stderr_too(self):
        # unittest writes its summary to stderr, pytest to stdout.
        self.assertTrue(verify_ac._ran_no_tests("shell", "", "Ran 0 tests in 0.000s"))

    def test_a_non_test_verb_is_never_judged_vacuous(self):
        # `grep` has no test count, and could match a signature inside the file it searches.
        with tempfile.TemporaryDirectory() as td:
            f = Path(td) / "notes.md"
            f.write_text("Ran 0 tests in 0.000s\n", encoding="utf-8")
            r = verify_ac.run_verifier("grep 'Ran 0 tests' notes.md", 30, Path(td))
            self.assertTrue(r.ok)
            self.assertFalse(r.vacuous)

    def test_prose_mentioning_a_count_mid_line_does_not_false_positive(self):
        # Anchored patterns: an honest test that PRINTS about test counts still passes.
        r = self._run("checked that we never claim Ran 0 tests in a report")
        self.assertTrue(r.ok)
        self.assertFalse(r.vacuous)

    def test_report_counts_and_flags_the_vacuous_ac(self):
        story = (
            "# US9001: demo\n\n## Acceptance Criteria\n\n"
            "### AC1: a filter that matches nothing\n\n"
            "- **Verify:** shell printf 'Ran 0 tests in 0.000s\\n'\n"
            "- **Verified:** yes (2026-01-01)\n"
        )
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            sp = root / "story.md"
            sp.write_text(story, encoding="utf-8")
            rep = verify_ac.verify_story(sp, True, 30, root)
            self.assertEqual(rep.failed, 1)
            self.assertEqual(rep.verified, 0)
            self.assertEqual(rep.vacuous, 1)
            self.assertTrue(rep.failures[0]["vacuous"])


class UnresolvedPytestVerifierTests(unittest.TestCase):
    """BG0231 - a pytest verifier whose named test no longer exists must be attributed as an
    unresolved verifier, not read as a code failure. A deleted node exits 4 and a stale -k
    pattern exits 5; both mean the runner ran nothing, so the green they replace proves
    nothing, and the remedy (re-point the Verify line) is different from fixing code."""

    def _pytest_project(self, d):
        (Path(d) / "test_present.py").write_text(
            "def test_here():\n    assert True\n\ndef test_fails():\n    assert False\n",
            encoding="utf-8")

    def test_a_deleted_node_is_vacuous_not_a_plain_failure(self):
        with tempfile.TemporaryDirectory() as d:
            self._pytest_project(d)
            r = verify_ac.run_verifier("pytest test_present.py::test_GONE", 60, Path(d))
            self.assertFalse(r.ok)
            self.assertTrue(r.vacuous, "a deleted node ran nothing - it proves nothing")
            self.assertIn(r.exit_code, (4, 5))

    def test_a_stale_k_pattern_is_vacuous(self):
        with tempfile.TemporaryDirectory() as d:
            self._pytest_project(d)
            r = verify_ac.run_verifier("pytest test_present.py -k test_GONE", 60, Path(d))
            self.assertFalse(r.ok)
            self.assertTrue(r.vacuous, "a -k pattern matching nothing ran nothing")

    def test_the_vacuous_pytest_result_names_the_remedy(self):
        with tempfile.TemporaryDirectory() as d:
            self._pytest_project(d)
            r = verify_ac.run_verifier("pytest test_present.py::test_GONE", 60, Path(d))
            self.assertIn("Re-point the Verify line", r.stderr)

    def test_a_real_failure_is_a_plain_failure_not_vacuous(self):
        with tempfile.TemporaryDirectory() as d:
            self._pytest_project(d)
            r = verify_ac.run_verifier("pytest test_present.py::test_fails", 60, Path(d))
            self.assertFalse(r.ok)
            self.assertFalse(r.vacuous, "the test ran and failed - that is a code failure")
            self.assertEqual(r.exit_code, 1)

    def test_a_real_pass_is_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            self._pytest_project(d)
            r = verify_ac.run_verifier("pytest test_present.py::test_here", 60, Path(d))
            self.assertTrue(r.ok)
            self.assertFalse(r.vacuous)


class SkippedPytestVerifierTests(unittest.TestCase):
    """BG0317 - a pytest run whose selected tests were ALL skipped exits 0 and prints
    "1 skipped", which the no-tests-ran regex does not match. The default per-AC path stamped
    such an AC green while the batch path, reading the SAME run out of JUnit XML, refused the
    skip as not-a-pass. Identical inputs, opposite verdicts; the green one is the dangerous
    one, because a skipped test proves exactly as much as a test that never ran."""

    def _run(self, script: str):
        return verify_ac.run_verifier(f"shell printf '%s\\n' {shlex_quote(script)}",
                                      30, Path.cwd())

    def test_an_all_skipped_run_is_not_a_pass(self):
        r = self._run("1 skipped in 0.01s")
        self.assertFalse(r.ok)
        self.assertTrue(r.vacuous)
        self.assertEqual(r.exit_code, 0)

    def test_the_banner_summary_form_is_judged_too(self):
        self.assertTrue(self._run("===== 1 skipped in 0.01s =====").vacuous)

    def test_skips_beside_deselections_and_warnings_are_still_vacuous(self):
        self.assertTrue(self._run("2 skipped, 91 deselected, 1 warning in 0.08s").vacuous)

    def test_a_skip_beside_a_real_pass_is_still_a_pass(self):
        r = self._run("3 passed, 1 skipped in 0.04s")
        self.assertTrue(r.ok, "one test did run and pass - that is not vacuous")
        self.assertFalse(r.vacuous)

    def test_a_real_skipped_node_matches_the_batch_path_verdict(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_skipped.py").write_text(
                "import pytest\n\n\n"
                "@pytest.mark.skip(reason='not today')\n"
                "def test_a():\n    assert True\n",
                encoding="utf-8")
            r = verify_ac.run_verifier("pytest test_skipped.py::test_a", 60, Path(d))
        self.assertFalse(r.ok, "the JUnit batch path calls this not-a-pass; so must this one")
        self.assertTrue(r.vacuous)
        # The same run through the batch path, for the parity this bug was about.
        xml = ('<testsuites><testsuite>'
               '<testcase classname="test_skipped" name="test_a"><skipped /></testcase>'
               '</testsuite></testsuites>')
        nodes = verify_ac._parse_junit_xml(xml, ["test_skipped.py"])
        self.assertFalse(nodes["test_skipped.py::test_a"])

    def test_the_cached_verdict_does_not_call_a_skip_a_failure(self):
        # The cache records pass/not-pass, so it cannot tell a skip from a red test. Saying
        # "cached pytest failure" for a skipped node sends the reader to debug code that
        # never ran.
        r = verify_ac.resolve_pytest_from_cache("pytest tests/test_x.py::test_a",
                                                {"tests/test_x.py::test_a": False})
        self.assertFalse(r.ok)
        self.assertIn("skipped", r.stderr)
        self.assertNotRegex(r.stderr, r"cached pytest failure")


class AllSkippedNonPytestRunnerTests(unittest.TestCase):
    """BG0348 - the all-skipped hole was closed for pytest only. Every other runner family
    exits 0 on a run where nothing executed and prints a summary the zero-count signatures do
    not match, so the AC was stamped green by tests that never ran. `unittest` matters most:
    it is this repository's own default runner."""

    def _run(self, script: str):
        return verify_ac.run_verifier(f"shell printf '%s\\n' {shlex_quote(script)}",
                                      30, Path.cwd())

    # --- unittest -------------------------------------------------------------------
    def test_a_real_all_skipped_unittest_run_is_not_a_pass(self):
        """The exact bytes a real `python3 -m unittest` all-skipped run prints."""
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "test_allskip.py").write_text(
                "import unittest\n\n\n"
                "class T(unittest.TestCase):\n"
                "    @unittest.skip('not today')\n"
                "    def test_a(self):\n        self.assertTrue(False)\n",
                encoding="utf-8")
            r = verify_ac.run_verifier("shell python3 -m unittest test_allskip", 60, Path(d))
        self.assertEqual(r.exit_code, 0, "unittest exits 0 on an all-skipped run")
        self.assertFalse(r.ok, "nothing ran, so nothing was proved")
        self.assertTrue(r.vacuous)
        self.assertIn("SKIPPED", r.stderr)

    def test_a_mixed_unittest_run_with_one_skip_is_still_a_pass(self):
        """`Ran 4 tests` beside `skipped=1` means three tests really ran - not vacuous."""
        r = self._run("Ran 4 tests in 0.001s\n\nOK (skipped=1)")
        self.assertTrue(r.ok, "three tests ran and passed")
        self.assertFalse(r.vacuous)

    def test_unittest_skips_beside_expected_failures_are_not_all_skipped(self):
        r = self._run("Ran 2 tests in 0.001s\n\nOK (skipped=1, expected failures=1)")
        self.assertFalse(r.vacuous, "an expected failure is a test that ran")

    def test_two_unittest_runs_one_all_skipped_one_green_is_not_vacuous(self):
        # A `shell` Verify line routinely runs both suites. One empty run beside a real one
        # must not fail the gate.
        r = self._run("Ran 1 test in 0.000s\n\nOK (skipped=1)\n"
                      "Ran 9 tests in 0.100s\n\nOK")
        self.assertFalse(r.vacuous)

    def test_two_unittest_runs_both_all_skipped_is_vacuous(self):
        r = self._run("Ran 1 test in 0.000s\n\nOK (skipped=1)\n"
                      "Ran 3 tests in 0.100s\n\nOK (skipped=3)")
        self.assertTrue(r.vacuous)

    # --- jest -----------------------------------------------------------------------
    def test_an_all_skipped_jest_run_is_not_a_pass(self):
        r = self._run("Test Suites: 1 skipped, 1 total\n"
                      "Tests:       3 skipped, 3 total\n"
                      "Snapshots:   0 total")
        self.assertFalse(r.ok)
        self.assertTrue(r.vacuous)
        self.assertIn("SKIPPED", r.stderr)

    def test_a_mixed_jest_run_is_still_a_pass(self):
        r = self._run("Tests:       1 skipped, 2 passed, 3 total")
        self.assertTrue(r.ok)
        self.assertFalse(r.vacuous)

    def test_a_jest_run_of_only_todos_ran_nothing_either(self):
        self.assertTrue(self._run("Tests:       2 todo, 2 total").vacuous)
        self.assertTrue(self._run("Tests:       1 skipped, 1 todo, 2 total").vacuous)

    # --- vitest ---------------------------------------------------------------------
    def test_an_all_skipped_vitest_run_is_not_a_pass(self):
        r = self._run(" Test Files  1 skipped (1)\n      Tests  3 skipped (3)")
        self.assertFalse(r.ok)
        self.assertTrue(r.vacuous)
        self.assertIn("SKIPPED", r.stderr)

    def test_a_mixed_vitest_run_is_still_a_pass(self):
        r = self._run(" Test Files  1 passed (1)\n      Tests  2 passed | 1 skipped (3)")
        self.assertTrue(r.ok)
        self.assertFalse(r.vacuous)

    # --- go -------------------------------------------------------------------------
    def test_a_go_run_whose_every_test_skipped_is_not_a_pass(self):
        r = self._run("=== RUN   TestA\n    a_test.go:6: not today\n--- SKIP: TestA (0.00s)\n"
                      "PASS\nok  \tex/foo\t0.002s")
        self.assertFalse(r.ok)
        self.assertTrue(r.vacuous)
        self.assertIn("SKIPPED", r.stderr)

    def test_a_go_run_with_one_real_pass_beside_a_skip_is_still_a_pass(self):
        r = self._run("--- SKIP: TestA (0.00s)\n--- PASS: TestB (0.00s)\n"
                      "PASS\nok  \tex/foo\t0.002s")
        self.assertTrue(r.ok)
        self.assertFalse(r.vacuous)

    # --- the remedy the reader is given --------------------------------------------
    def test_the_all_skipped_remedy_is_not_the_re_point_one(self):
        # Re-pointing a Verify line at a different test is the wrong advice here: the
        # selector is fine, the test is switched off.
        r = self._run("Ran 1 test in 0.000s\n\nOK (skipped=1)")
        self.assertIn("SKIPPED", r.stderr)
        self.assertNotIn("Re-point the Verify line at a test that exists", r.stderr)

    def test_a_green_run_of_every_family_is_untouched(self):
        for green in ("Ran 9 tests in 0.001s\n\nOK",
                      "Tests:       3 passed, 3 total",
                      " Test Files  1 passed (1)\n      Tests  3 passed (3)",
                      "--- PASS: TestA (0.00s)\nPASS\nok  \tex/foo\t0.002s",
                      "3 passed in 0.04s"):
            with self.subTest(green=green.splitlines()[0]):
                r = self._run(green)
                self.assertTrue(r.ok)
                self.assertFalse(r.vacuous)


def shlex_quote(s: str) -> str:
    import shlex as _s
    return _s.quote(s)


class GrepDashPatternTests(unittest.TestCase):
    """A dash-leading grep pattern must not be read as the tool's own flags (US0228)."""

    def _build(self, expr: str, with_rg: bool):
        orig = verify_ac.shutil.which
        self.addCleanup(setattr, verify_ac.shutil, "which", orig)
        verify_ac.shutil.which = lambda name: "/usr/bin/rg" if (with_rg and name == "rg") else None
        return verify_ac._build_command(expr, cwd=Path.cwd())

    def test_dash_leading_pattern_is_passed_behind_dash_e(self):
        for with_rg in (True, False):
            with self.subTest(rg=with_rg):
                _, cmd = self._build("grep -Ran notes.md", with_rg)
                self.assertIn("-e", cmd)
                self.assertEqual(cmd[cmd.index("-e") + 1], "-Ran")
                # and never as a bare positional ahead of -e
                self.assertLess(cmd.index("-e"), cmd.index("-Ran"))

    def test_paths_sit_behind_a_double_dash_terminator(self):
        for with_rg in (True, False):
            with self.subTest(rg=with_rg):
                _, cmd = self._build("grep pattern notes.md", with_rg)
                self.assertIn("--", cmd)
                self.assertTrue(all(cmd.index("--") < cmd.index(p)
                                    for p in cmd if p.endswith("notes.md")))

    def test_both_backends_are_hardened(self):
        _, with_rg = self._build("grep -x notes.md", True)
        _, without = self._build("grep -x notes.md", False)
        self.assertEqual(with_rg[:4], ["rg", "-q", "-e", "-x"])
        self.assertEqual(without[:4], ["grep", "-rqE", "-e", "-x"])
        for cmd in (with_rg, without):
            self.assertIn("--", cmd)

    def test_ordinary_patterns_are_unaffected(self):
        # The search still finds what it found before - semantics unchanged, only quoting.
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "notes.md").write_text("hello world\n", encoding="utf-8")
            self.assertTrue(verify_ac.run_verifier("grep 'hello' notes.md", 30, Path(td)).ok)
            self.assertFalse(verify_ac.run_verifier("grep 'absent' notes.md", 30, Path(td)).ok)

    def test_a_dash_leading_pattern_actually_matches_end_to_end(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "notes.md").write_text("-Ran the thing\n", encoding="utf-8")
            r = verify_ac.run_verifier("grep '\\-Ran' notes.md", 30, Path(td))
            self.assertTrue(r.ok, f"exit={r.exit_code} stderr={r.stderr}")


class US0166Ac3Tests(unittest.TestCase):
    """US0166 AC3's own verifier must check its claim, not misparse into a green (US0226).

    Reads the dogfooded workspace by path, so it is dev-repo-only: from an installed copy
    the story is not there and these would raise FileNotFoundError, which says nothing
    about the consuming project's own install (BG0209).
    """

    STORY = (Path(__file__).resolve().parents[5]
             / "sdlc-studio/stories/US0166-ship-a-stop-hook-installer-and-redefine-sprint.md")

    def setUp(self):
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)

    def _ac3(self):
        blocks = verify_ac.parse_story(self.STORY.read_text(encoding="utf-8"))
        ac3 = next((b for b in blocks if b.ac_id == "AC3"), None)
        self.assertIsNotNone(ac3, "US0166 AC3 not found")
        return ac3

    def test_ac3_uses_the_shell_verb(self):
        # A compound, multi-file check is not the single-pattern `grep` verb.
        self.assertTrue(self._ac3().verifier.startswith("shell "))

    def test_ac3_no_longer_carries_a_bare_grep_verb_with_a_flag(self):
        # `grep -q ...` as a DSL verb parses the flag as the PATTERN - the original defect.
        v = self._ac3().verifier
        self.assertFalse(v.startswith("grep -"))

    def test_ac3_names_both_files_it_claims(self):
        v = self._ac3().verifier
        self.assertIn("help/gate.md", v)
        self.assertIn("reference-retro.md", v)

    def test_ac3_checks_both_halves_of_its_claim(self):
        v = self._ac3().verifier
        self.assertIn("never at .deployed", v)
        self.assertIn("require-close", v)

    def test_ac3_actually_passes_against_the_live_tree(self):
        repo_root = self.STORY.resolve().parents[2]
        r = verify_ac.run_verifier(self._ac3().verifier, 60, repo_root)
        self.assertTrue(r.ok, f"exit={r.exit_code} stderr={r.stderr[:300]}")
        self.assertFalse(r.vacuous)


class DuplicateVerifierTests(unittest.TestCase):
    """US0227: two ACs sharing a selector cannot both discriminate.

    The two workspace-reading tests below are dev-repo-only and skip from an installed
    copy (BG0209); `test_duplicates_are_reported_with_every_claiming_ac` builds its own
    fixture in a temporary directory and runs everywhere, which is what keeps the
    detector itself covered off the dev repo.
    """

    STORIES = Path(__file__).resolve().parents[5] / "sdlc-studio" / "stories"

    def _verifiers(self, prefix: str) -> list[str]:
        if not workspace.in_dev_repo():
            self.skipTest(workspace.SKIP_REASON)
        path = next(p for p in self.STORIES.glob(f"{prefix}-*.md"))
        return [" ".join(b.verifier.split())
                for b in verify_ac.parse_story(path.read_text(encoding="utf-8"))
                if b.verifier]

    def test_the_named_stories_no_longer_share_a_selector(self):
        a, b = self._verifiers("US0172"), self._verifiers("US0173")
        self.assertTrue(a and b)
        self.assertFalse(set(a) & set(b), "US0172 and US0173 still share a Verify command")
        # and neither leans on the broad class-wide filter that hid the overlap
        for v in a + b:
            self.assertNotIn("-k AttemptsAndCost", v)

    def test_us0163_acs_select_different_suites(self):
        vs = self._verifiers("US0163")
        self.assertGreaterEqual(len(vs), 2)
        self.assertEqual(len(set(vs)), len(vs), "US0163's ACs still share a Verify command")

    def test_duplicates_are_reported_with_every_claiming_ac(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "US0001-a.md").write_text(
                "# US0001: a\n\n## Acceptance Criteria\n\n"
                "### AC1: one\n- **Verify:** shell run-the-suite\n\n"
                "### AC2: two\n- **Verify:** shell run-the-suite\n", encoding="utf-8")
            (root / "US0002-b.md").write_text(
                "# US0002: b\n\n## Acceptance Criteria\n\n"
                "### AC1: one\n- **Verify:** shell something-else\n", encoding="utf-8")
            dupes = verify_ac.duplicate_verifiers(sorted(root.glob("*.md")))
            self.assertEqual(len(dupes), 1)
            self.assertEqual(dupes[0]["verifier"], "shell run-the-suite")
            self.assertEqual(dupes[0]["acs"], ["US0001 AC1", "US0001 AC2"])

    def test_duplicates_are_found_across_different_stories(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for n in ("0001", "0002"):
                (root / f"US{n}-x.md").write_text(
                    f"# US{n}: x\n\n## Acceptance Criteria\n\n"
                    "### AC1: one\n- **Verify:** shell shared-run\n", encoding="utf-8")
            dupes = verify_ac.duplicate_verifiers(sorted(root.glob("*.md")))
            self.assertEqual([d["acs"] for d in dupes], [["US0001 AC1", "US0002 AC1"]])

    def test_whitespace_normalised_and_manual_exempt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "US0001-a.md").write_text(
                "# US0001: a\n\n## Acceptance Criteria\n\n"
                "### AC1: one\n- **Verify:** shell run   the-suite\n\n"
                "### AC2: two\n- **Verify:** shell run the-suite\n\n"
                "### AC3: three\n- **Verify:** manual an operator reads it\n\n"
                "### AC4: four\n- **Verify:** manual an operator reads it\n", encoding="utf-8")
            dupes = verify_ac.duplicate_verifiers(sorted(root.glob("*.md")))
            self.assertEqual(len(dupes), 1, "spacing-only difference is the same run")
            self.assertEqual(dupes[0]["acs"], ["US0001 AC1", "US0001 AC2"])
            self.assertNotIn("manual", dupes[0]["verifier"])

    def test_a_story_with_no_duplicates_reports_none(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "US0001-a.md").write_text(
                "# US0001: a\n\n## Acceptance Criteria\n\n"
                "### AC1: one\n- **Verify:** shell run-a\n\n"
                "### AC2: two\n- **Verify:** shell run-b\n", encoding="utf-8")
            self.assertEqual(verify_ac.duplicate_verifiers(sorted(root.glob("*.md"))), [])


class RootRelativeWriteTests(unittest.TestCase):
    """BG0220: every path verify_ac reads or writes anchors on the PROJECT ROOT, never on
    the current directory. Each test runs from a cwd that is not the root - a test that
    chdir'd to the root would pass on a script that ignores `--root` entirely and prove
    nothing. Same class as BG0219 (lessons.py wrote its digest beside the cwd)."""

    def setUp(self) -> None:
        self._prev_cwd = Path.cwd()
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name) / "proj"
        (self.root / "sdlc-studio" / "stories").mkdir(parents=True)
        (self.root / "sdlc-studio" / "epics").mkdir(parents=True)
        self.story = self.root / "sdlc-studio" / "stories" / "US0001-login.md"
        self.story.write_text(
            "# US0001: Login\n\n## Acceptance Criteria\n\n"
            "### AC1: it runs\n- **Verify:** shell true\n", encoding="utf-8")
        (self.root / "sdlc-studio" / "epics" / "EP0001-x.md").write_text(
            "# EP0001: x\n\n## Stories\n\n| ID | Title |\n| --- | --- |\n| US0001 | Login |\n",
            encoding="utf-8")
        # a nested working directory inside the project, standing in for `scripts/`
        self.inner = self.root / "scripts"
        self.inner.mkdir()

    def tearDown(self) -> None:
        import os
        os.chdir(self._prev_cwd)
        self._td.cleanup()

    def _chdir(self, d: Path) -> None:
        import os
        os.chdir(d)

    def _strays(self, d: Path) -> list[str]:
        """Anything verify_ac left beside `d` that was not there before."""
        return sorted(p.name for p in d.iterdir())

    def test_run_without_root_writes_under_the_discovered_root_not_the_cwd(self) -> None:
        """The reported symptom: `run` from a subdirectory grew a stray sdlc-studio/.local
        tree beside the cwd, because --root defaulted to the cwd rather than the project."""
        self._chdir(self.inner)
        rc = _quiet_main(["run", "--file", str(self.story), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertEqual(self._strays(self.inner), [],
                         "verify_ac wrote beside the cwd instead of under the project root")
        self.assertTrue(
            (self.root / "sdlc-studio" / ".local" / "verify-report.dry-run.json").is_file(),
            "the dry-run report did not land under the project root")

    def test_run_without_root_writes_history_under_the_discovered_root(self) -> None:
        self._chdir(self.inner)
        rc = _quiet_main(["run", "--file", str(self.story)])
        self.assertEqual(rc, 0)
        self.assertEqual(self._strays(self.inner), [])
        self.assertTrue(
            (self.root / "sdlc-studio" / ".local" / "verify-history.jsonl").is_file(),
            "the history log did not land under the project root")

    def test_report_reads_the_report_run_wrote_under_the_same_root(self) -> None:
        """`run --root X` then `--root X report` must agree on where the report is. They
        did not: run anchored on the root and report resolved against the cwd, so the
        gate that reads the report saw 'no report' from anywhere but the root."""
        self._chdir(self.inner)
        self.assertEqual(_quiet_main(["run", "--root", str(self.root)]), 0)
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = verify_ac.main(["--root", str(self.root), "report"])
        self.assertEqual(rc, 0, err.getvalue())
        self.assertNotIn("no report", err.getvalue())

    def test_scaffold_matrix_out_is_written_under_the_root(self) -> None:
        """`--out` is a write, and it resolved against the cwd."""
        self._chdir(self.inner)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = verify_ac.main(["--root", str(self.root), "scaffold-matrix",
                                 "--epic", "EP0001", "--out", "matrix.md"])
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / "matrix.md").is_file(),
                        "the matrix was written beside the cwd, not under the root")
        self.assertEqual(self._strays(self.inner), [])

    def test_ts_check_spec_is_resolved_under_the_root(self) -> None:
        """The spec carries a KNOWN-BAD row, so only a run that actually read the file can
        report the issue. Asserting rc 0 here would be vacuous: `ts_check` reads a missing
        spec as empty text and reports a clean matrix, so the cwd-relative miss passed."""
        spec = self.root / "ts.md"
        spec.write_text(
            "## AC Coverage Matrix\n\n"
            "| Story | AC | Test Case | Status |\n"
            "| --- | --- | --- | --- |\n"
            "| US0001 | AC1 | {{test}} | pass |\n", encoding="utf-8")
        self._chdir(self.inner)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = verify_ac.main(["--root", str(self.root), "ts-check", "--spec", "ts.md"])
        self.assertEqual(rc, 1, "a root-relative --spec was not read from a foreign cwd")
        self.assertIn("placeholder", out.getvalue())

    def test_an_absolute_path_is_still_honoured_verbatim(self) -> None:
        """Anchoring must not capture an absolute path the caller chose deliberately."""
        self._chdir(self.inner)
        out = Path(self._td.name) / "outside-the-root.json"
        rc = _quiet_main(["run", "--root", str(self.root), "--report", str(out)])
        self.assertEqual(rc, 0)
        self.assertTrue(out.is_file(), "an absolute --report was re-anchored under the root")

    def test_a_named_root_is_honoured_verbatim_not_re_pointed_by_discovery(self) -> None:
        """Discovery widens the default `.` only. A root the caller NAMED is where the run
        writes, even when a bigger project sits above it - silently retargeting a named
        root would be the same class of lie in the other direction."""
        named = self.inner            # inside self.root, but not itself a project root
        rc = _quiet_main(["run", "--root", str(named),
                          "--dir", str(self.root / "sdlc-studio" / "stories")])
        self.assertEqual(rc, 0)
        self.assertTrue((named / "sdlc-studio" / ".local" / "verify-report.json").is_file(),
                        "the named root was ignored")
        self.assertFalse((self.root / "sdlc-studio" / ".local").exists(),
                         "discovery overrode a root the caller named")

    def test_discovery_does_not_escape_a_cwd_with_no_project_above_it(self) -> None:
        """With no project root anywhere above, the cwd is the honest answer - discovery
        must not silently walk to `/` and write somewhere unrelated."""
        with tempfile.TemporaryDirectory() as bare:
            self.assertEqual(verify_ac.discover_root(Path(bare)), Path(bare).resolve())


class AcFingerprintTests(unittest.TestCase):
    """BG0232 - the freshness spine pinned by its own test, from both sides.

    A fingerprint that never changes is as useless as one that always does; only the pair -
    differs on a material change, stable across an immaterial one - distinguishes a real hash
    from a constant or a passthrough. Every mutation here purges bytecode implicitly (the
    functions are pure), so a same-length edit cannot hide behind a cached .pyc.
    """

    STORY = (
        "# US0001: x\n\n> **Status:** Ready\n\n"
        "### AC1: the thing works\n"
        "- **Given** a\n- **When** b\n- **Then** c\n"
        "- **Verify:** pytest tests/test_x.py -k test_a\n"
        "- **Verified:** yes (2026-01-01)\n"
    )

    def test_fingerprint_is_stable_across_a_status_change(self) -> None:
        before = verify_ac.ac_fingerprint(self.STORY)
        after = verify_ac.ac_fingerprint(self.STORY.replace("Status:** Ready", "Status:** Done"))
        self.assertEqual(before, after, "a Status edit changed nothing the verifier runs")

    def test_fingerprint_is_stable_across_a_revision_history_row(self) -> None:
        before = verify_ac.ac_fingerprint(self.STORY)
        after = verify_ac.ac_fingerprint(
            self.STORY + "\n## Revision History\n\n| Date | Author | Change |\n"
            "| --- | --- | --- |\n| 2026-01-02 | x | groomed |\n")
        self.assertEqual(before, after, "a Revision History row is not an AC change")

    def test_fingerprint_is_stable_across_the_verified_stamp(self) -> None:
        before = verify_ac.ac_fingerprint(self.STORY)
        after = verify_ac.ac_fingerprint(
            self.STORY.replace("Verified:** yes (2026-01-01)", "Verified:** no (2026-05-05)"))
        self.assertEqual(before, after, "the machine-maintained stamp must not feed back in")

    def test_fingerprint_changes_when_a_verify_command_changes(self) -> None:
        before = verify_ac.ac_fingerprint(self.STORY)
        after = verify_ac.ac_fingerprint(
            self.STORY.replace("test_x.py -k test_a", "test_x.py -k test_b"))
        self.assertNotEqual(before, after, "a re-pointed verifier must go stale")

    def test_fingerprint_changes_when_an_ac_title_changes(self) -> None:
        before = verify_ac.ac_fingerprint(self.STORY)
        after = verify_ac.ac_fingerprint(
            self.STORY.replace("AC1: the thing works", "AC1: the thing works differently"))
        self.assertNotEqual(before, after, "a retitled AC is a different claim")

    def test_fingerprint_changes_when_an_ac_is_added(self) -> None:
        before = verify_ac.ac_fingerprint(self.STORY)
        after = verify_ac.ac_fingerprint(
            self.STORY + "\n### AC2: another\n- **Verify:** file README.md\n")
        self.assertNotEqual(before, after, "an added AC changes what must pass")

    def test_fingerprint_changes_when_an_ac_is_removed(self) -> None:
        two = self.STORY + "\n### AC2: another\n- **Verify:** file README.md\n"
        self.assertNotEqual(verify_ac.ac_fingerprint(two),
                            verify_ac.ac_fingerprint(self.STORY),
                            "removing an AC changes the coverage the entry claims")

    def test_fingerprint_is_not_a_constant(self) -> None:
        # guards the crudest break - a hash function replaced by a literal passes every
        # stability test above and fails only this
        a = verify_ac.ac_fingerprint(self.STORY)
        b = verify_ac.ac_fingerprint("### ACZ: unrelated\n- **Verify:** file X.md\n")
        self.assertNotEqual(a, b)


#: The four verifiers US0310 ACTUALLY SHIPPED in commit e1bc477, recovered from git rather
#: than invented for this test. All four passed. None of them touched the guard they claimed
#: to verify, and the sprint published a verified count four higher than its evidence
#: supported. They are the fixture because a guard is validated with the bug it defends
#: against (LL0010), and a hand-written approximation would be a guess about the shape.
US0310_SHIPPED_VERIFIERS = [
    'grep "review is a concurrent-writer window" .claude/skills/sdlc-studio/reference-sprint.md',
    'grep "symlink" .claude/skills/sdlc-studio/reference-review.md',
    'grep "green" .claude/skills/sdlc-studio/reference-review.md',
    'grep "window" .claude/skills/sdlc-studio/reference-sprint.md',
]


class MarkdownEvidenceLintTests(unittest.TestCase):
    """BG0264: a verifier that only reads prose proves a sentence was written.

    Five versions of this guard were defeated in four review rounds, every one by trying to
    ENUMERATE what the runner reads. The current design inverts the burden: a prose verb is
    refused unless a non-markdown file it reads can be pointed at, so every uncertainty
    refuses. These tests pin the escapes that were actually found, not invented ones.
    """

    #: The four verifiers US0310 SHIPPED in e1bc477, recovered from git. All four passed,
    #: none touched the guard they claimed to verify, and the sprint published a verified
    #: count four higher than its evidence supported.
    US0310_SHIPPED_VERIFIERS = [
        'grep "review is a concurrent-writer window" .claude/skills/sdlc-studio/reference-sprint.md',
        'grep "symlink" .claude/skills/sdlc-studio/reference-review.md',
        'grep "green" .claude/skills/sdlc-studio/reference-review.md',
        'grep "window" .claude/skills/sdlc-studio/reference-sprint.md',
    ]

    #: Every form found by review, quoted as the reviewer wrote it. Round 1: the tokens as
    #: written. Round 2: a directory glob, a flag read as the pattern, a bare directory.
    #: Round 3: hidden and symlinked files rg will not read. Round 4: rg --files listing a
    #: file rg cannot open, and rg --files exiting 2 on one unreadable subdirectory.
    ESCAPES_FOUND_BY_REVIEW = [
        'grep "anything" sdlc-studio/reviews/*',
        'grep -c "window" .claude/skills/sdlc-studio/reference-sprint.md',
        'grep -r "x" .claude/skills/sdlc-studio/best-practices/',
        'grep "anything" sdlc-studio/reviews/',
        'grep -m 1 "x" .claude/skills/sdlc-studio/reference-cr.md',
        'grep --include x "y" .claude/skills/sdlc-studio/reference-rfc.md',
        'grep -R "x" .claude/skills/sdlc-studio/help/',
    ]

    @staticmethod
    def _root() -> Path:
        return Path(__file__).resolve().parents[5]

    def test_every_verifier_us0310_shipped_is_refused(self) -> None:
        for expr in self.US0310_SHIPPED_VERIFIERS:
            with self.subTest(expr=expr):
                self.assertIsNotNone(verify_ac.lint_markdown_evidence(expr, self._root()))

    def test_every_escape_found_by_review_is_refused(self) -> None:
        for expr in self.ESCAPES_FOUND_BY_REVIEW:
            with self.subTest(expr=expr):
                self.assertIsNotNone(verify_ac.lint_markdown_evidence(expr, self._root()))

    def test_a_behavioural_verifier_is_untouched(self) -> None:
        root = self._root()
        for expr in ("pytest scripts/tests/test_x.py::C::t",
                     "shell scripts/gate.py --check",
                     "manual the operator confirms the banner renders",
                     'grep "x" .claude/skills/sdlc-studio/scripts/verify_ac.py',
                     'grep "x" .claude/skills/sdlc-studio/scripts/'):
            with self.subTest(expr=expr):
                self.assertIsNone(verify_ac.lint_markdown_evidence(expr, root))

    def test_the_file_verb_is_refused_over_markdown_and_over_a_prose_directory(self) -> None:
        # BG0266: `file <dir>` runs `test -e`, which passes forever. The inverted burden
        # closes it without a separate rule - a prose directory demonstrates nothing.
        root = self._root()
        self.assertIsNotNone(verify_ac.lint_markdown_evidence(
            "file .claude/skills/sdlc-studio/reference-cr.md", root))
        self.assertIsNotNone(verify_ac.lint_markdown_evidence(
            "file .claude/skills/sdlc-studio/help/", root))

    # BOTH tests below assert the rg-PRESENT behaviour and only that. `_runner_candidates`
    # has two paths: with `rg` the candidate set is `rg --files`, which SKIPS hidden and
    # ignored files; without it the runner is `grep -rqE`, which genuinely DOES read them, so
    # a hidden `.py` licenses the directory and it is right to. Neither test said so, so both
    # failed on a runner with no ripgrep - green here, red in CI, for two releases.
    #
    # Skipped rather than rewritten to pass either way: "a hidden decoy does not license" is
    # not a claim about `grep`, and making it pass under grep would mean asserting something
    # weaker than the criterion. CI installs ripgrep so the skip does not silently take the
    # coverage away - a skip nobody notices is the same hole with a friendlier colour.
    @unittest.skipUnless(shutil.which("rg"),
                         "this claim is about the rg candidate set; without rg the runner is "
                         "`grep -rqE`, which reads hidden files, so the decoy licenses correctly")
    def test_a_hidden_symlinked_or_unreadable_decoy_does_not_license_a_prose_directory(self) -> None:
        # Round 3 and round 4's escapes together. rg skips hidden files, follows no symlink
        # found in a walk, and cannot open a file it lacks permission for - so none of these
        # is evidence that the runner reads anything but prose.
        outer = Path(tempfile.mkdtemp(prefix="verify_ac_decoys_"))
        try:
            (outer / "real.py").write_text("code\n")
            docs = outer / "docs"
            docs.mkdir()
            (docs / "note.md").write_text("the guard refuses\n")
            (docs / ".hidden.py").write_text("code\n")
            locked = docs / "locked.py"
            locked.write_text("code\n")
            try:
                (docs / "link.py").symlink_to(outer / "real.py")
                locked.chmod(0o000)
            except OSError:
                pass
            try:
                self.assertIsNotNone(
                    verify_ac.lint_markdown_evidence('grep "refuses" docs', outer))
            finally:
                try:
                    locked.chmod(0o644)
                except OSError:
                    pass
        finally:
            shutil.rmtree(outer, ignore_errors=True)

    @unittest.skipUnless(shutil.which("rg"),
                         "this claim is about the rg candidate set; without rg the runner is "
                         "`grep -rqE`, which reads hidden files, so the decoy licenses correctly")
    def test_an_unreadable_subdirectory_refuses_rather_than_falling_back_to_a_plain_walk(self) -> None:
        # Round 4 MAJOR-1. `rg --files` exits 2 when any part of the tree errors. Falling
        # back to rglob then re-listed the hidden files rg refuses to read, reinstating the
        # escape. No candidates must mean no demonstration, which refuses.
        outer = Path(tempfile.mkdtemp(prefix="verify_ac_rgerr_"))
        try:
            docs = outer / "docs"
            docs.mkdir()
            (docs / "note.md").write_text("x\n")
            (docs / ".hidden.py").write_text("code\n")
            vault = docs / "vault"
            vault.mkdir()
            (vault / "a.md").write_text("x\n")
            try:
                vault.chmod(0o000)
            except OSError:
                self.skipTest("cannot make a directory unreadable here")
            try:
                self.assertIsNotNone(verify_ac.lint_markdown_evidence('grep "x" docs', outer))
            finally:
                vault.chmod(0o755)
        finally:
            shutil.rmtree(outer, ignore_errors=True)

    def test_a_real_code_file_in_a_directory_licenses_it(self) -> None:
        # The guard must not refuse everything. A readable, non-markdown, non-symlink file
        # is the demonstration the design asks for.
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_mixed_"))
        try:
            (tmp / "note.md").write_text("x\n")
            (tmp / "impl.py").write_text("code\n")
            self.assertIsNone(verify_ac.lint_markdown_evidence(f'grep "x" {tmp}', tmp))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_one_predicate_decides_what_markdown_means(self) -> None:
        # The case rule lived in two places and they disagreed, so a mutant dropping one
        # `.lower()` flipped a verdict while every test stayed green. One predicate now.
        for name in ("a.md", "A.MD", "x/y/Z.Md"):
            with self.subTest(name=name):
                self.assertTrue(verify_ac._is_markdown(name))
        for name in ("a.py", "a.markdown", "README"):
            with self.subTest(name=name):
                self.assertFalse(verify_ac._is_markdown(name))

    def test_an_uppercase_extension_directory_is_refused(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_case_"))
        try:
            (tmp / "NOTE.MD").write_text("x\n")
            (tmp / "b.MD").write_text("x\n")
            self.assertIsNotNone(verify_ac.lint_markdown_evidence(f'grep "x" {tmp}', tmp))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_nested_all_markdown_directory_is_refused(self) -> None:
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_nested_"))
        try:
            (tmp / "a.md").write_text("x\n")
            deep = tmp / "sub" / "deeper"
            deep.mkdir(parents=True)
            (deep / "b.md").write_text("x\n")
            self.assertIsNotNone(verify_ac.lint_markdown_evidence(f'grep "x" {tmp}', tmp))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_missing_operand_proves_nothing(self) -> None:
        # MEASURED: `rg -q -e -r -- x help/` exits 0, warning about the missing path while
        # matching inside the directory. A flag form is a working silent verifier, not a
        # loudly broken one, so an unread operand must not license it.
        root = self._root()
        self.assertIsNotNone(verify_ac.lint_markdown_evidence(
            'grep -r "x" .claude/skills/sdlc-studio/help/', root))

    def test_the_written_split_matches_the_dsl_not_an_invented_one(self) -> None:
        self.assertEqual(verify_ac._verifier_targets('grep -c "x" a.md'), ["x", "a.md"])
        _, argv = verify_ac._build_command('grep -c "x" a.md', cwd=".")
        self.assertEqual(argv[argv.index("--") + 1:], ["x", "a.md"])

    def test_without_rg_a_symlinked_code_file_still_licenses_nothing(self) -> None:
        # `rg --files` already omits symlinks, so the symlink rule only bites on the
        # `grep -rqE` fallback - and no test covered that branch, so deleting the rule
        # survived mutation. `grep -r` follows only paths named on the command line.
        outer = Path(tempfile.mkdtemp(prefix="verify_ac_norg_link_"))
        try:
            (outer / "real.py").write_text("code\n")
            docs = outer / "docs"
            docs.mkdir()
            (docs / "note.md").write_text("the guard refuses\n")
            try:
                (docs / "link.py").symlink_to(outer / "real.py")
            except OSError:
                self.skipTest("cannot create a symlink here")
            real_which = verify_ac.shutil.which
            verify_ac.shutil.which = lambda n: None if n == "rg" else real_which(n)
            try:
                self.assertIsNotNone(
                    verify_ac.lint_markdown_evidence('grep "refuses" docs', outer))
            finally:
                verify_ac.shutil.which = real_which
        finally:
            shutil.rmtree(outer, ignore_errors=True)

    def test_without_rg_a_hidden_code_file_DOES_license_it(self) -> None:
        # The counter-test, so the rule above cannot be satisfied by refusing everything:
        # `grep -rqE` really does read hidden files, so one is a genuine demonstration.
        outer = Path(tempfile.mkdtemp(prefix="verify_ac_norg_hidden_"))
        try:
            docs = outer / "docs"
            docs.mkdir()
            (docs / "note.md").write_text("x\n")
            (docs / ".hidden.py").write_text("code\n")
            real_which = verify_ac.shutil.which
            verify_ac.shutil.which = lambda n: None if n == "rg" else real_which(n)
            try:
                self.assertIsNone(verify_ac.lint_markdown_evidence('grep "x" docs', outer))
            finally:
                verify_ac.shutil.which = real_which
        finally:
            shutil.rmtree(outer, ignore_errors=True)

    def test_lint_exits_non_zero_on_a_draft_story_and_zero_once_done(self) -> None:
        root = FixtureRoot()
        try:
            story = root.tmp / "sdlc-studio" / "stories" / "US0003-prose.md"
            (root.tmp / "notes.md").write_text("the guard refuses\n")
            body = (
                "# US0003: a criterion about a guard\n\n"
                "> **Status:** {status}\n\n"
                "## Acceptance Criteria\n\n"
                "### AC1: the guard refuses\n\n"
                "- **Verify:** grep \"the guard refuses\" notes.md\n"
            )
            args = argparse.Namespace(root=str(root.tmp), dir="sdlc-studio/stories",
                                      story=str(story), repo_root=None)
            story.write_text(body.format(status="Draft"))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                draft_rc = verify_ac.cmd_lint(args)
            story.write_text(body.format(status="Done"))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                done_rc = verify_ac.cmd_lint(args)
            self.assertEqual((draft_rc, done_rc), (1, 0))
        finally:
            root.cleanup()


class StackedVerifierTests(unittest.TestCase):
    """BG0265: only the FIRST Verify line in an AC block is executed."""

    def test_a_second_verify_line_in_one_block_is_refused(self) -> None:
        root = FixtureRoot()
        try:
            story = root.tmp / "sdlc-studio" / "stories" / "US0004-stacked.md"
            body = (
                "# US0004: a criterion with two checks\n\n"
                "> **Status:** {status}\n\n"
                "## Acceptance Criteria\n\n"
                "### AC1: it does two things\n\n"
                "- **Verify:** pytest a/b.py::C::t_one\n"
                "- **Verify:** pytest a/b.py::C::t_two\n"
            )
            args = argparse.Namespace(root=str(root.tmp), dir="sdlc-studio/stories",
                                      story=str(story), repo_root=None)
            story.write_text(body.format(status="Draft"))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                rc = verify_ac.cmd_lint(args)
            self.assertEqual(rc, 1)
            # The refusal must NAME the dropped verifier, not merely count it - an author
            # who cannot see which check was discarded cannot act on the message.
            self.assertIn("t_two", buf.getvalue())
            # Past authoring it has shipped; refusing retrospectively blocks a lint over
            # history without helping anyone, exactly as the markdown-evidence guard does.
            story.write_text(body.format(status="Done"))
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(verify_ac.cmd_lint(args), 0)
        finally:
            root.cleanup()

    def test_the_parser_records_the_dropped_verifiers_rather_than_discarding_them(self) -> None:
        blocks = verify_ac.parse_story(
            "### AC1: x\n\n- **Verify:** pytest a::t1\n- **Verify:** pytest a::t2\n"
            "- **Verify:** pytest a::t3\n")
        self.assertEqual(blocks[0].verifier, "pytest a::t1")
        self.assertEqual(blocks[0].extra_verifiers, ["pytest a::t2", "pytest a::t3"])

    def test_no_ac_block_in_the_workspace_stacks_verifiers(self) -> None:
        """The census, over the live tree. Seven verifiers sat here unexecuted - four on
        stories at Done, two of them counted inside a published claim of 84 criteria
        verified. This goes red again the moment another one is added."""
        if not workspace.in_dev_repo():
            self.skipTest("census applies to the dev repo's own workspace")
        root = Path(__file__).resolve().parents[5]
        offenders = []
        for sub in ("stories", "bugs"):
            d = root / "sdlc-studio" / sub
            if not d.is_dir():
                continue
            for f in sorted(d.glob("*.md")):
                for b in verify_ac.parse_story(sdlc_md.read_text_safe(f)):
                    if b.extra_verifiers:
                        offenders.append(f"{f.name} {b.ac_id} (+{len(b.extra_verifiers)})")
        self.assertEqual(offenders, [], "AC blocks stacking verifiers that will never run")


class StampResolutionTests(unittest.TestCase):
    """BG0256: a stamp is evidence only while the thing it points at still exists."""

    TESTFILE = ".claude/skills/sdlc-studio/scripts/tests/test_critic.py"
    SELF_FILE = ".claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py"
    LIVE = "test_neutral_text_reports_no_violations"

    def _story(self, tmp: Path, verifier: str, stamped: str = "yes") -> Path:
        d = tmp / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "US9001-dead.md"
        f.write_text(
            "# US9001: a stamped criterion\n\n> **Status:** Done\n\n"
            "## Acceptance Criteria\n\n### AC1: it holds\n\n"
            f"- **Verify:** {verifier}\n- **Verified:** {stamped} (2026-07-20)\n")
        return f

    def test_a_recorded_green_whose_selector_selects_nothing_is_reported_stale(self) -> None:
        """Both shapes, in one test so neither can carry the other: a `-k` pattern matching
        nothing while its file still collects - the shape that produced this bug, and the one
        a file-exists check passes - and a node address whose class is gone."""
        root = Path(__file__).resolve().parents[5]
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_stamp_"))
        try:
            for verifier in (f"pytest {self.TESTFILE} -k test_no_such_name_anywhere",
                             f"pytest {self.TESTFILE}::NoSuchClass::test_gone"):
                with self.subTest(verifier=verifier):
                    f = self._story(tmp, verifier)
                    rows = verify_ac.unresolvable_stamps(f, root)
                    self.assertEqual([r["ac"] for r in rows], ["AC1"])
                    # The reader must be told WHICH pointer died, not that the story changed.
                    self.assertIn(verifier.split()[-1], rows[0]["verifier"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_a_resolving_selector_stays_green_and_no_test_body_is_executed(self) -> None:
        """The negative control. Without it the fix is indistinguishable from marking every
        stamp stale, which is the same defect with the sign flipped. Resolution is decided by
        COLLECTION: the check must answer without running the test it names."""
        root = Path(__file__).resolve().parents[5]
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_live_"))
        try:
            f = self._story(tmp, f"pytest {self.TESTFILE} -k {self.LIVE}")
            self.assertEqual(verify_ac.unresolvable_stamps(f, root), [])
            # No test BODY runs: every subprocess this check spawns is a --collect-only
            # call. Clear the file cache first so a call is actually made to observe.
            verify_ac._COLLECT_CACHE.clear()
            calls = []
            real = verify_ac.subprocess.run

            def spy(cmd, *a, **kw):
                calls.append(cmd)
                return real(cmd, *a, **kw)

            verify_ac.subprocess.run = spy
            try:
                self.assertIs(verify_ac.selector_resolves(
                    f"pytest {self.TESTFILE} -k {self.LIVE}", root), True)
            finally:
                verify_ac.subprocess.run = real
            self.assertTrue(calls, "no collection was performed")
            for cmd in calls:
                self.assertIn("--collect-only", cmd)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_an_unanswerable_verifier_is_not_reported_as_dead_and_costs_no_subprocess(self) -> None:
        """None, not False: a `manual`/`grep`/`shell` selector cannot be collected, and
        calling it unresolvable would mark every non-pytest stamp stale.

        The subprocess assertion is the load-bearing half. Deleting the verb guard still
        returned None for all three - but only by luck downstream (`which("manual")` misses,
        `rg` chokes on `--collect-only`), which meant the guard could be removed with every
        test green while the check started shelling out for verifiers it cannot answer."""
        verify_ac._COLLECT_CACHE.clear()
        real = verify_ac.subprocess.run
        calls = []
        verify_ac.subprocess.run = lambda cmd, *a, **kw: calls.append(cmd)
        try:
            for expr in ("manual the operator confirms it",
                         'grep "x" .claude/skills/sdlc-studio/scripts/verify_ac.py',
                         "shell scripts/gate.py --check"):
                with self.subTest(expr=expr):
                    self.assertIsNone(verify_ac.selector_resolves(expr, "."))
        finally:
            verify_ac.subprocess.run = real
        self.assertEqual(calls, [], "an unanswerable verifier shelled out anyway")

    def test_an_unstamped_ac_with_a_dead_selector_is_not_reported(self) -> None:
        # An unstamped AC claims nothing, so a dead selector there is the author's business
        # at the next run - not a false green on disk, which is what this bug is about.
        root = Path(__file__).resolve().parents[5]
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_unstamped_"))
        try:
            f = self._story(tmp, f"pytest {self.TESTFILE} -k test_no_such_name", stamped="no")
            self.assertEqual(verify_ac.unresolvable_stamps(f, root), [])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


    def test_resolution_is_answered_in_process_against_a_cached_file_collection(self) -> None:
        """The regression fix: one collection per FILE, not per AC. A node address, a class
        prefix, and a -k boolean are all resolved against the same cached node list, so a
        second selector into the same file spawns no further subprocess."""
        root = Path(__file__).resolve().parents[5]
        verify_ac._COLLECT_CACHE.clear()
        tf = self.TESTFILE
        # An exact node address that exists in this very file resolves True; its class prefix
        # also resolves True; a bogus method under a real class resolves False.
        me = "%s::StampResolutionTests::test_a_k_boolean_expression_resolves_without_pytests_engine" % self.SELF_FILE
        self.assertIs(verify_ac.selector_resolves(f"pytest {me}", root), True)
        self.assertIs(verify_ac.selector_resolves(
            f"pytest {self.SELF_FILE}::StampResolutionTests", root), True)
        self.assertIs(verify_ac.selector_resolves(
            f"pytest {self.SELF_FILE}::StampResolutionTests::test_gone_forever", root), False)
        calls = []
        real = verify_ac.subprocess.run
        verify_ac.subprocess.run = lambda *a, **k: (calls.append(a), real(*a, **k))[1]
        try:
            live = verify_ac.selector_resolves(f"pytest {tf} -k {self.LIVE}", root)
            # second selector, same file - must hit the cache, no new subprocess
            before = len(calls)
            other = verify_ac.selector_resolves(f"pytest {tf} -k no_such_test_name_at_all", root)
        finally:
            verify_ac.subprocess.run = real
        self.assertIs(live, True)
        self.assertIs(other, False)
        self.assertEqual(len(calls), before, "a repeated file target re-collected instead of using the cache")

    def test_a_k_boolean_expression_resolves_without_pytests_engine(self) -> None:
        nodes = ["t.py::test_alpha_one", "t.py::test_beta_two"]
        self.assertTrue(verify_ac._k_selects("alpha", nodes))
        self.assertTrue(verify_ac._k_selects("alpha or gamma", nodes))
        self.assertFalse(verify_ac._k_selects("alpha and gamma", nodes))
        self.assertTrue(verify_ac._k_selects("not gamma", nodes))
        self.assertFalse(verify_ac._k_selects("gamma", nodes))

    def test_the_command_exits_non_zero_on_a_story_whose_stamped_verifier_cannot_resolve(self) -> None:
        root = Path(__file__).resolve().parents[5]
        tmp = Path(tempfile.mkdtemp(prefix="verify_ac_cmd_"))
        try:
            dead = self._story(tmp, f"pytest {self.TESTFILE} -k test_no_such_name_anywhere")
            args = argparse.Namespace(root=str(root), dir="sdlc-studio/stories",
                                      story=str(dead), bugs=False, repo_root=None)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                rc = verify_ac.cmd_stamps(args)
            self.assertEqual(rc, 1)
            out = buf.getvalue()
            self.assertIn("US9001", out)
            self.assertIn("AC1", out)
            self.assertIn("test_no_such_name_anywhere", out)

            live = self._story(tmp, f"pytest {self.TESTFILE} -k {self.LIVE}")
            args.story = str(live)
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(verify_ac.cmd_stamps(args), 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)




class FenceInfoStringTests(unittest.TestCase):
    """A closing fence may be followed only by spaces (CommonMark 4.5). Treating an info-string
    line as a closer released the block early and turned the illustration beneath it into a LIVE
    shell verifier - the same harm the four-backtick case had, by a different route."""

    def _first_verifier(self, body):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "US9999-x.md"
            p.write_text("# US9999: x\n\n## Acceptance Criteria\n\n### AC1: a\n\n" + body,
                         encoding="utf-8")
            blocks = verify_ac.parse_story(p.read_text(encoding="utf-8"))
            return blocks[0].verifier if blocks else None

    def test_an_info_string_line_does_not_close_a_fence(self):
        v = self._first_verifier(
            "```\nA story looks like this:\n```markdown\n"
            "- **Verify:** shell echo INJECTED\n```\n")
        self.assertIsNone(v, "an illustration inside a fenced block must never become a verifier")

    def test_a_tilde_info_string_line_does_not_close_a_fence(self):
        v = self._first_verifier(
            "~~~\nexample:\n~~~text\n- **Verify:** shell echo INJECTED\n~~~\n")
        self.assertIsNone(v)

    def test_a_bare_closer_still_closes_so_a_real_verify_after_it_parses(self):
        v = self._first_verifier(
            "```\nillustration\n```\n- **Verify:** shell true\n")
        self.assertEqual(v, "shell true",
                         "the fix must not swallow a genuine Verify line after a real closer")

    def test_a_closer_with_trailing_spaces_still_closes(self):
        v = self._first_verifier("```\nx\n```   \n- **Verify:** shell true\n")
        self.assertEqual(v, "shell true")


def _ratchet_repo(root, dupes=1, bug_dupe=False, baseline=None, story_status="Ready"):
    """A workspace with `dupes` stories sharing one selector, optionally a BUG sharing another."""
    import json as _json
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True, exist_ok=True)
    shared = "pytest tests/test_x.py::T::t_shared"
    for i in range(1, dupes + 2):
        (sd / f"US000{i}-x.md").write_text(
            f"# US000{i}: x\n\n> **Status:** {story_status}\n\n"
            f"## Acceptance Criteria\n\n### AC1\n- **Verify:** {shared}\n", encoding="utf-8")
    if bug_dupe:
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True, exist_ok=True)
        parked = "pytest tests/test_y.py::T::t_parked"
        for i in (1, 2):
            (bd / f"BG000{i}-b.md").write_text(
                f"# BG000{i}: b\n\n> **Status:** Open\n> **Severity:** Medium\n\n"
                f"## Acceptance Criteria\n\n### AC1\n- **Verify:** {parked}\n",
                encoding="utf-8")
    if baseline is not None:
        p = root / verify_ac.DUP_BASELINE_REL
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(_json.dumps(baseline), encoding="utf-8")
    return root


class RatchetTests(unittest.TestCase):
    """US0461. `duplicate_verifiers` reported and never refused, so the shared-selector class
    could grow indefinitely. The ratchet compares the SET of groups, never the count."""

    def _paths(self, root, bugs=False):
        paths = list(verify_ac.walk_stories(root / "sdlc-studio" / "stories"))
        if bugs:
            # `prefixes=("BG",)`: walk_stories defaults to stories alone, so passing the bugs
            # directory without it yields NOTHING and the test would prove the opposite of
            # what it claims.
            paths += list(verify_ac.walk_stories(root / "sdlc-studio" / "bugs",
                                                 prefixes=("BG",)))
        return paths

    def test_an_unbaselined_duplicate_refuses_across_stories_and_bugs(self) -> None:
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name), bug_dupe=True, baseline={"groups": {}})
        # Stories only: the story group is refused, the parked bug group is INVISIBLE.
        story_only = verify_ac.dup_ratchet(root, self._paths(root))
        self.assertFalse(story_only["ok"])
        self.assertTrue(any("test_x" in g for g in story_only["new"]))
        self.assertFalse(any("test_y" in g for g in story_only["new"]),
                         "the bug group was seen without --bugs, so this proves nothing")
        # With bugs: BOTH are refused - a shared selector cannot be parked where nothing looks.
        both = verify_ac.dup_ratchet(root, self._paths(root, bugs=True))
        self.assertTrue(any("test_y" in g for g in both["new"]),
                        "a shared selector parked in a bug escaped the ratchet")

    def test_the_COMMAND_scans_bugs_when_asked(self) -> None:
        """Through `cmd_lint`, not by assembling paths here. The sibling test builds its own
        path list, so dropping the `prefixes=("BG",)` from the command survived - and without
        that prefix `walk_stories` on the bugs directory yields NOTHING, which is the
        exemption-by-omission the flag exists to close. Caught by mutation."""
        import argparse
        import contextlib
        import io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name), bug_dupe=True, baseline={"groups": {}})
        err = io.StringIO()
        args = argparse.Namespace(root=str(root), dir="sdlc-studio/stories", story=None,
                                  bugs=True, ratchet=True, stamp=False)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = verify_ac.cmd_lint(args)
        self.assertEqual(1, rc)
        self.assertIn("test_y", err.getvalue(),
                      "the command did not reach the bug group - `--bugs` scanned nothing, "
                      "which reads exactly like a clean tree")

    def test_a_recorded_group_passes_silently(self) -> None:
        """The positive control: a ratchet that refuses everything is unusable."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        found = verify_ac.duplicate_verifiers(self._paths(root))
        # MUTANT: `duplicate_verifiers` stubbed to `return []`. Without this assertion the whole
        # test passes over an EMPTY baseline against an EMPTY scan - a control that is green when
        # the detector finds nothing is not a control.
        self.assertTrue(found, "the fixture produced no duplicate group, so this control would "
                               "pass with the detector returning nothing")
        groups = {g["verifier"]: {"acs": g["acs"], "reason": "one indivisible behaviour"}
                  for g in found}
        (root / verify_ac.DUP_BASELINE_REL).write_text(
            json.dumps({"groups": groups}), encoding="utf-8")
        verdict = verify_ac.dup_ratchet(root, self._paths(root))
        self.assertTrue(verdict["ok"], f"a recorded group was refused: {verdict}")

    def test_a_swap_that_keeps_the_count_flat_is_still_refused(self) -> None:
        """The comparison is over the SET. A change that splits one baselined group and adds a
        new one leaves the count unchanged - and a count-based guard passes it, which is the
        guard a rising total would already have caught."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        live = verify_ac.duplicate_verifiers(self._paths(root))
        self.assertEqual(1, len(live), "fixture did not produce exactly one live group")
        # Baseline records a DIFFERENT single group: same count, different identity.
        (root / verify_ac.DUP_BASELINE_REL).write_text(json.dumps({"groups": {
            "pytest tests/test_gone.py::T::t_fixed": {"acs": ["US0001 AC1", "US0002 AC1"],
                                                      "reason": "historical"}}}),
            encoding="utf-8")
        verdict = verify_ac.dup_ratchet(root, self._paths(root))
        self.assertFalse(verdict["ok"], "a flat-count swap passed the ratchet")
        self.assertTrue(verdict["new"], "the new group was not named")
        self.assertTrue(verdict["stale"], "the fixed group was not named as stale")

    def test_no_untrustworthy_baseline_reports_clean(self) -> None:
        """Three DISTINCT states, because the remedy differs and none may read as clean."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        base = Path(td.name)
        absent = _ratchet_repo(base / "absent")
        self.assertEqual("not-baselined", verify_ac.dup_ratchet(absent, self._paths(absent))["state"])
        corrupt = _ratchet_repo(base / "corrupt", baseline=None)
        p = corrupt / verify_ac.DUP_BASELINE_REL
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("{ not json", encoding="utf-8")
        self.assertEqual("corrupt", verify_ac.dup_ratchet(corrupt, self._paths(corrupt))["state"])
        stale = _ratchet_repo(base / "stale", dupes=0, baseline={"groups": {
            "pytest tests/test_gone.py::T::t": {"acs": ["US0001 AC1"], "reason": "why"}}})
        v = verify_ac.dup_ratchet(stale, self._paths(stale))
        self.assertFalse(v["ok"], "a stale entry reported clean")
        self.assertTrue(v["stale"])


#: The records whose intra-record groups this pair split. Named, so the resolvability sweep
#: answers for the selectors that were WRITTEN rather than auditing the whole corpus.
SPLIT_STORIES = ("US0025", "US0111", "US0113", "US0114", "US0123", "US0124", "US0166",
                 "US0167", "US0170", "US0247", "US0266", "US0268", "US0392")
SPLIT_BUGS = ("BG0239", "BG0240", "BG0241", "BG0242", "BG0245", "BG0251")


#: The twenty intra-record baseline entries US0635 and US0636 removed. A literal, so the
#: direction is proven against something committed rather than against a run-local file.
BURNED_DOWN_KEYS = (
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ProseWriterSweepTests::test_the_four_cr0392_writers_are_now_safe",
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::AdoptCutoffTests::test_pre_cutoff_story_is_exempt",
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k HookEnabled",
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py -k guard",
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_briefing_is_generated_from_definitions",
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::TwoBacklogStatusTests",
    "pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::UndecomposedDriftTests",
    "pytest tools/tests/test_lint_style.py::ProvenanceGuardTests",
    "pytest tools/tests/test_precommit_lane_order.py",
    "shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_conformance.SprintReviewCritiquedTests",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_backlog_triage.py -k Duplicate",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_close_guard.py",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_engagement_floor.py",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_loop_guard.py",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_mutation.py",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint.py -k TriageInPlan",
    "shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_verify_ac.py",
    "shell python3 -m unittest discover -s tools/tests -p test_precommit_budget_recording.py",
    "shell python3 -m unittest discover -s tools/tests -p test_skill_tests_env.py",
    "shell python3 -m unittest tools.tests.test_precommit_floor_pending",
)


class DuplicateBurndownTests(unittest.TestCase):
    """US0635/US0636. Two ACs sharing a selector cannot both discriminate: a regression in
    either fails both, and neither says which.

    The assertions are over the RESOLVER's intra-record subset, never over `lint --ratchet`'s
    exit code - that verdict answers for the whole corpus including cross-record debt this pair
    does not touch, so a test pinned to it is green or red for reasons outside these units.

    Every emptiness assertion is preceded by a liveness one. `walk_stories` yields nothing when
    it is pointed at the wrong prefix, and `selector_resolves` answers None when the runner is
    absent from PATH - either way "no group remains" goes green over a scan that saw nothing,
    which is the failure this whole file exists to refuse.
    """

    #: The repo root. Five levels up from `.../.claude/skills/sdlc-studio/scripts/tests/`, and
    #: asserted rather than counted: an off-by-one here would point the whole class at a
    #: directory holding no workspace, and every emptiness assertion would pass over nothing.
    ROOT = Path(__file__).resolve().parents[5]

    @classmethod
    def setUpClass(cls) -> None:
        if not (cls.ROOT / "sdlc-studio" / "stories").is_dir():
            raise unittest.SkipTest(
                f"no workspace under {cls.ROOT} - this class reads the LIVE corpus and would "
                f"otherwise report a burn-down complete over a directory that is not there")

    def _groups(self, kind: str):
        paths = sorted((self.ROOT / "sdlc-studio" / kind).glob("*.md"))
        self.assertGreater(len(paths), 100, f"the {kind} scan collected almost nothing")
        groups = verify_ac.duplicate_verifiers(paths)
        intra = [g for g in groups if len({a.split()[0] for a in g["acs"]}) == 1]
        return groups, intra

    def _selectors(self, kind: str, ids: tuple) -> list[str]:
        """The Verify lines of the records this burn-down SPLIT, not of the whole corpus.

        Scoped deliberately. The criterion is that the selectors written here resolve; sweeping
        every record in the tree measures 1,400 lines this pair never touched and turns a
        specific claim into an unrelated corpus audit.
        """
        out = []
        for uid in ids:
            for p in (self.ROOT / "sdlc-studio" / kind).glob(f"{uid}-*.md"):
                for line in verify_ac.sdlc_md.criteria_section(
                        p.read_text(encoding="utf-8")).splitlines():
                    m = re.search(r"\*\*Verify:\*\*\s*(.+?)\s*$", line)
                    if m:
                        out.append(m.group(1))
        return out

    def test_no_intra_record_group_remains_in_stories(self) -> None:
        """Mutant: point one split criterion at a node id that collects nothing.

        Uniqueness alone is met by appending junk - the groups empty, the baseline entries go
        stale and get removed, and nothing was split. So every story-side selector must RESOLVE.
        """
        groups, intra = self._groups("stories")
        self.assertTrue(groups, "the resolver found no groups at all - the scan is not live")
        self.assertEqual([], [g["acs"] for g in intra])
        unresolvable = [s for s in self._selectors("stories", SPLIT_STORIES)
                        if s.startswith("pytest ")
                        and verify_ac.selector_resolves(s, cwd=str(self.ROOT)) is False]
        self.assertEqual([], unresolvable,
                         f"story selectors that resolve to nothing: {unresolvable[:5]}")

    def test_the_story_side_baseline_entries_are_gone_and_none_were_added(self) -> None:
        """Mutant: return a story-side entry to the baseline, so the set grew rather than shrank.

        Pinned to COMMITTED state, not to `run_state.base_ref` - that reads an untracked
        run-local file and answers empty once the run closes, so a permanent suite test would
        lose its oracle.
        """
        cur = json.loads((self.ROOT / "sdlc-studio" / ".verify-lint-baseline.json")
                         .read_text(encoding="utf-8"))["groups"]
        self.assertTrue(cur, "the baseline parsed empty - the comparison would be vacuous")
        intra = [k for k, v in cur.items() if len({a.split()[0] for a in v["acs"]}) == 1]
        self.assertEqual([], intra, f"intra-record entries still baselined: {intra[:5]}")
        # The twenty keys this burn-down removed, as LITERALS. Pinned to committed state rather
        # than to `run_state.base_ref`, which reads an untracked run-local file and answers
        # empty the moment the run closes - a permanent suite test cannot keep that oracle.
        back = sorted(set(BURNED_DOWN_KEYS) & set(cur))
        self.assertEqual([], back, f"a burned-down entry returned to the baseline: {back[:3]}")
        self.assertEqual(20, len(BURNED_DOWN_KEYS),
                         "the pinned burn-down set changed size; it is a record of what landed")

    def test_a_fresh_duplicate_in_a_story_is_still_refused(self) -> None:
        """Mutant: widen the shipped baseline with the fixture's selector.

        Run over the LIVE story paths plus one planted record, so the SHIPPED baseline is the
        surface. Every sibling ratchet test builds its own tmp baseline, against which editing
        the shipped file changes nothing at all.
        """
        shared = "pytest tests/test_planted.py::PlantedTests::test_planted_and_shared"
        with tempfile.TemporaryDirectory() as d:
            plant = Path(d) / "US9999-planted.md"
            plant.write_text(
                "# US9999: planted\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                f"### AC1: a\n\n- **Verify:** {shared}\n\n### AC2: b\n\n"
                f"- **Verify:** {shared}\n", encoding="utf-8")
            live = sorted((self.ROOT / "sdlc-studio" / "stories").glob("*.md"))
            verdict = verify_ac.dup_ratchet(self.ROOT, live + [plant])
            control = verify_ac.dup_ratchet(self.ROOT, live)
        # `dup_ratchet` answers not-ok for at least five reasons, and a non-ok BASELINE returns
        # every live group as `new` - so a bare assertFalse(ok) passes for the wrong one.
        self.assertEqual("ok", control.get("state"),
                         f"the control run is already not-ok: {control.get('state')}")
        self.assertEqual("ok", verdict.get("state"))
        self.assertFalse(verdict["ok"], "the planted duplicate was not refused")
        # The ratchet keys on the RESOLVED command (BG0486), so the planted selector
        # is named in the form it runs as - `-q` supplied by the runner.
        self.assertIn(verify_ac.dup_group_key(shared), verdict["new"],
                      "the refusal did not name the planted selector")

    def test_no_intra_record_group_remains_in_bugs(self) -> None:
        """Mutant: point one split criterion under sdlc-studio/bugs at a node id collecting
        nothing. All seven bug-side groups were `shell ... discover`, which `selector_resolves`
        answers None for - so a cosmetic split leaves them unanswerable and invisible."""
        groups, intra = self._groups("bugs")
        self.assertTrue(groups, "the bug scan found no groups at all - it is not live")
        self.assertTrue(any(len({a.split()[0] for a in g["acs"]}) > 1 for g in groups),
                        "no cross-record group was seen, so the scan is not reaching the corpus")
        self.assertEqual([], [g["acs"] for g in intra])
        unresolvable = [s for s in self._selectors("bugs", SPLIT_BUGS)
                        if s.startswith("pytest ")
                        and verify_ac.selector_resolves(s, cwd=str(self.ROOT)) is False]
        self.assertEqual([], unresolvable,
                         f"bug selectors that resolve to nothing: {unresolvable[:5]}")

    def test_a_fresh_duplicate_in_a_bug_is_still_refused(self) -> None:
        """The bug-side half, on the same terms - live paths, shipped baseline, state asserted
        alongside the named selector, and a control run without the plant."""
        shared = "pytest tests/test_planted.py::PlantedTests::test_planted_bug_side"
        with tempfile.TemporaryDirectory() as d:
            plant = Path(d) / "BG9999-planted.md"
            plant.write_text(
                "# BG9999: planted\n\n> **Status:** Open\n\n## Acceptance Criteria\n\n"
                f"- [ ] **AC1** a\n  **Verify:** {shared}\n"
                f"- [ ] **AC2** b\n  **Verify:** {shared}\n", encoding="utf-8")
            live = sorted((self.ROOT / "sdlc-studio" / "bugs").glob("*.md"))
            verdict = verify_ac.dup_ratchet(self.ROOT, live + [plant])
            control = verify_ac.dup_ratchet(self.ROOT, live)
        self.assertEqual("ok", control.get("state"))
        self.assertEqual("ok", verdict.get("state"))
        self.assertFalse(verdict["ok"], "the planted bug-side duplicate was not refused")
        self.assertIn(verify_ac.dup_group_key(shared), verdict["new"])

    def test_the_baseline_holds_no_intra_record_group_in_either_directory(self) -> None:
        """Mutant: return one intra-record entry to the baseline after both halves have landed.

        The closing claim: what remains is cross-record ONLY. Asserted with the surviving
        cross-record entries required present, so it cannot pass over a baseline never read.
        """
        cur = json.loads((self.ROOT / "sdlc-studio" / ".verify-lint-baseline.json")
                         .read_text(encoding="utf-8"))["groups"]
        self.assertTrue(cur, "the baseline parsed empty, so this assertion would be vacuous")
        by_kind = {"intra": [], "cross": []}
        for k, v in cur.items():
            by_kind["intra" if len({a.split()[0] for a in v["acs"]}) == 1 else "cross"].append(k)
        self.assertEqual([], by_kind["intra"],
                         f"intra-record debt still baselined: {by_kind['intra'][:5]}")
        self.assertTrue(by_kind["cross"],
                        "no cross-record entry survives, so the baseline was emptied rather "
                        "than burned down - the guard would have nothing left to enforce from")


class BaselineSchemaTests(unittest.TestCase):
    """US0461 AC4. An exemption is MACHINERY, not an assumption a later story makes."""

    def _root(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            "# US0001: x\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            "### AC1\n- **Verify:** shell true\n", encoding="utf-8")
        return root

    def test_a_reasonless_unresolvable_or_oversized_entry_is_refused(self) -> None:
        root = self._root()
        reasonless = verify_ac.dup_entry_errors(root, "cmd", {"acs": ["US0001 AC1"], "reason": ""})
        self.assertTrue(any("substance" in e for e in reasonless),
                        f"an empty reason was not refused: {reasonless}")
        dangling = verify_ac.dup_entry_errors(
            root, "cmd", {"acs": ["US9999 AC1"], "reason": "why"})
        self.assertTrue(any("resolves to no artefact" in e for e in dangling))
        oversized = verify_ac.dup_entry_errors(
            root, "cmd", {"acs": [f"US0001 AC{i}" for i in range(10)],
                          "reason": "a stated reason with real substance in it"})
        self.assertTrue(any("over the cap" in e for e in oversized))
        # MUTANT: `DUP_ENTRY_AC_CAP = 8` -> `1000`. The fixture used to be built from the
        # production constant (`range(DUP_ENTRY_AC_CAP + 2)`), so the cap could be set to any
        # value and this test stayed green - it asserted only "over whatever the cap says".
        # The count above is a LITERAL 10, and the cap's value is pinned here.
        self.assertEqual(8, verify_ac.DUP_ENTRY_AC_CAP,
                         "the cap's value changed; a group this wide is not the one baselined")
        # The positive control: a well-formed entry is accepted, or every entry is refused.
        self.assertEqual([], verify_ac.dup_entry_errors(
            root, "cmd", {"acs": ["US0001 AC1"], "reason": "one indivisible behaviour"}))

    def _paths(self, root, bugs=False):
        """Same walk as the sibling class. `prefixes=("BG",)` is REQUIRED for bugs: the default
        walks stories alone, so passing the bugs dir without it yields nothing."""
        paths = list(verify_ac.walk_stories(root / "sdlc-studio" / "stories"))
        if bugs:
            paths += list(verify_ac.walk_stories(root / "sdlc-studio" / "bugs",
                                                prefixes=("BG",)))
        return paths

    def test_a_bad_entry_refuses_through_the_RATCHET_not_only_the_helper(self) -> None:
        """MUTANTS this must die to, all of which left 263 tests green:
        (1) `dup_ratchet`'s verdict changed to `not (new or stale)`, ignoring `errors` entirely;
        (2) the `dup_entry_errors` loop inside `dup_ratchet` replaced with `pass`.

        The sibling tests call `dup_entry_errors` DIRECTLY, so the whole wiring from entry
        validation to refusal carried no test at all - AC4's promise is that the refusal happens
        in `verify_ac.py` itself. This is the author's recurring defect: the helper is asserted
        and the caller that must consult it is not.
        """
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        found = verify_ac.duplicate_verifiers(self._paths(root))
        self.assertTrue(found, "no duplicate group in the fixture")
        # Every field correct EXCEPT the reason, so `new`/`stale` are both empty and the verdict
        # can only be driven by the entry errors.
        groups = {g["verifier"]: {"acs": g["acs"], "reason": "-"} for g in found}
        (root / verify_ac.DUP_BASELINE_REL).write_text(
            json.dumps({"groups": groups}), encoding="utf-8")
        verdict = verify_ac.dup_ratchet(root, self._paths(root))
        self.assertEqual([], verdict["new"], "precondition: the group IS recorded")
        self.assertEqual([], verdict["stale"], "precondition: nothing is stale")
        self.assertFalse(verdict["ok"],
                         "a reasonless entry was tolerated by the ratchet even though the helper "
                         "reports it - the verdict does not consult the entry errors")
        self.assertTrue(any("substance" in e for e in verdict["errors"]))

    def test_a_bad_entry_refuses_through_the_COMMAND_an_operator_types(self) -> None:
        """MUTANT: `cmd_lint`'s `--stamp`/ratchet wiring disabled. The command is the surface a
        gate lane invokes, and a guard reachable only from a helper is not a lane."""
        import contextlib
        import io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        found = verify_ac.duplicate_verifiers(self._paths(root))
        groups = {g["verifier"]: {"acs": g["acs"], "reason": "-"} for g in found}
        (root / verify_ac.DUP_BASELINE_REL).write_text(
            json.dumps({"groups": groups}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            rc = verify_ac.main(["lint", "--ratchet", "--root", str(root)])
        self.assertEqual(1, rc, "the command exited 0 over a baseline entry it must refuse")
        self.assertIn("substance", err.getvalue())

    def test_a_baselined_group_that_has_SPREAD_since_is_refused(self) -> None:
        """The fail-open a reviewer demonstrated against the live 43-entry baseline: the AC cap was
        applied only to the entry's RECORDED list, and the recorded list was never compared to the
        live one. A group baselined at 2 ACs was accepted spread across 30.

        MUTANT: drop the `live_acs` comparison from `dup_entry_errors`, or stop passing
        `live_acs` from `dup_ratchet`.
        """
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name), dupes=4)
        found = verify_ac.duplicate_verifiers(self._paths(root))
        self.assertGreater(len(found[0]["acs"]), 2, "the fixture must have a group wider than 2")
        # Record only TWO of the ACs that share the selector; the rest have spread since.
        groups = {found[0]["verifier"]: {"acs": found[0]["acs"][:2],
                                        "reason": "recorded when only two ACs shared this"}}
        (root / verify_ac.DUP_BASELINE_REL).write_text(
            json.dumps({"groups": groups}), encoding="utf-8")
        verdict = verify_ac.dup_ratchet(root, self._paths(root))
        self.assertFalse(verdict["ok"],
                         "a selector that spread beyond its baselined AC set was tolerated")
        self.assertTrue(any("has spread since it was baselined" in e for e in verdict["errors"]),
                        f"refused, but not for the spread: {verdict['errors']}")

    def test_an_epic_or_cr_id_cannot_stand_in_for_the_group_s_acs(self) -> None:
        """A reviewer silenced a real group with `{"acs": ["EP0169 AC1"], "reason": "-"}`: the id
        resolved to SOME artefact, and nothing checked it was a unit that carries ACs.

        MUTANT: drop the `DUP_AC_UNIT_PREFIXES` check.
        """
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        ed = root / "sdlc-studio" / "epics"
        ed.mkdir(parents=True, exist_ok=True)
        (ed / "EP0001-e.md").write_text("# EP0001: e\n\n> **Status:** Active\n", encoding="utf-8")
        errors = verify_ac.dup_entry_errors(
            root, "cmd", {"acs": ["EP0001 AC1"],
                          "reason": "an epic id that happens to resolve on disk"})
        self.assertTrue(any("not a story or a bug" in e for e in errors),
                        f"an epic id was accepted as one of a duplicate group's ACs: {errors}")

    def test_a_case_only_twin_of_a_selector_is_one_group_not_two_of_one(self) -> None:
        """MUTANT: `dup_group_key` stops lowercasing the verb.

        The DSL lowercases the verb before dispatch, so `PyTest x` and `pytest x` run the
        IDENTICAL command. Grouped case-sensitively they were a group of ONE under each spelling,
        so `len(acs) > 1` never fired and the pair was reported as no duplicate at all - a way
        past the ratchet that needed only a shift key.
        """
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        for i, verb in ((1, "pytest"), (2, "PyTest")):
            (sd / f"US000{i}-x.md").write_text(
                f"# US000{i}: x\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
                f"### AC1\n- **Verify:** {verb} tests/test_x.py::T::t\n", encoding="utf-8")
        found = verify_ac.duplicate_verifiers(self._paths(root))
        self.assertEqual(1, len(found),
                         f"a case-only twin was not grouped with the selector it duplicates: "
                         f"{found}")
        self.assertEqual(2, len(found[0]["acs"]))

    def test_a_baseline_key_a_human_hand_edited_is_normalised_on_the_way_in(self) -> None:
        """MUTANT: stop normalising baseline keys on read.

        Normalisation used to be applied ONLY to the live side, which `duplicate_verifiers`
        already normalises - so it was applied to the one side that did not need it. The baseline
        is the side a human hand-edits, and a key with a double space was reported as BOTH new and
        stale: two refusals describing one entry, neither naming the cause.
        """
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        found = verify_ac.duplicate_verifiers(self._paths(root))
        self.assertTrue(found)
        sloppy = found[0]["verifier"].replace(" ", "  ", 1)   # as a hand edit leaves it
        self.assertNotEqual(sloppy, found[0]["verifier"], "the fixture did not introduce drift")
        (root / verify_ac.DUP_BASELINE_REL).write_text(
            json.dumps({"groups": {sloppy: {"acs": found[0]["acs"],
                                            "reason": "recorded with an untidy key by hand"}}}),
            encoding="utf-8")
        verdict = verify_ac.dup_ratchet(root, self._paths(root))
        self.assertEqual([], verdict["new"],
                         "a hand-spaced key read as an unrecorded group")
        self.assertEqual([], verdict["stale"],
                         "the same entry was ALSO reported stale, which is the double refusal")
        self.assertTrue(verdict["ok"], f"refused: {verdict['errors']}")

    def test_two_baseline_keys_that_collide_once_normalised_are_corrupt(self) -> None:
        """Normalising on read can silently drop an entry when two keys fold together, so that
        case is refused as corrupt rather than resolved by whichever happened to be last."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        (root / verify_ac.DUP_BASELINE_REL).write_text(
            json.dumps({"groups": {"pytest a::b": {"acs": ["US0001 AC1"], "reason": "x" * 25},
                                   "pytest  a::b": {"acs": ["US0002 AC1"], "reason": "y" * 25}}}),
            encoding="utf-8")
        base = verify_ac.read_dup_baseline(root)
        self.assertEqual("corrupt", base["state"],
                         "one of two colliding entries was silently discarded")
        self.assertIn("collide", base["detail"])

    def test_stamp_will_not_mint_an_entry_with_a_reason(self) -> None:
        """`--stamp` mints an EMPTY reason and returns non-zero, so a stamp cannot be used to
        manufacture an exemption nobody decided on."""
        import contextlib
        import io
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = _ratchet_repo(Path(td.name))
        paths = list(verify_ac.walk_stories(root / "sdlc-studio" / "stories"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = verify_ac._stamp_dup_baseline(root, paths)
        self.assertEqual(1, rc, "a stamp that mints exemptions exited 0")
        written = json.loads((root / verify_ac.DUP_BASELINE_REL).read_text(encoding="utf-8"))
        self.assertTrue(written["groups"], "nothing was recorded")
        for entry in written["groups"].values():
            self.assertEqual("", entry["reason"],
                             "the stamp invented a reason no human wrote")


class EmptyParseIsRefusedTests(unittest.TestCase):
    """BG0530: `verify_ac run` reported a clean pass over criteria it never read.

    311 of 534 bug files printed `ac=0 pass=0 fail=0`, exit 0 - a line byte-comparable to a
    clean pass - and 74% of everything filed since BG0500. Nothing detected the drift between
    the writer and the parser because the failure mode WAS exit 0.
    """

    def _unit(self, root: Path, body: str, name: str = "BG9001-x.md") -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        f = d / name
        f.write_text(body, encoding="utf-8")
        return f

    HEAD = "# BG9001: a bug\n\n> **Status:** Open\n> **Severity:** Medium\n\n"

    def _run(self, root: Path, unit: str = "BG9001"):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = verify_ac.main(["run", "--id", unit, "--root", str(root), "--dry-run"])
        return rc, out.getvalue() + err.getvalue()

    def test_a_section_that_parses_to_nothing_is_refused_through_the_cli(self) -> None:
        """Driven as a COMMAND, not a library call - the exit code is the whole finding.

        Mutant: delete the non-zero exit on a zero criterion count, which is the state 75 bug
        files are in today and which printed a line indistinguishable from a pass.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n"
                             "- [ ] it behaves, written in a shape this parser cannot read\n")
            rc, text = self._run(root)
            self.assertNotEqual(rc, 0, "an unreadable criteria section reported a clean pass")
            self.assertIn("REFUSED", text)
            self.assertIn("executed nothing", text)

    def test_absent_and_unparseable_are_different_events(self) -> None:
        """They have different fixes, so one message for both sends the reader to the wrong one.
        232 filed findings never claimed a verifier and nothing else in the tree refuses them.

        Mutant: return one identical message for both - this reddens on the distinction.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, self.HEAD + "## Summary\n\nno criteria section at all\n")
            rc_absent, absent = self._run(root)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n- [ ] unreadable shape\n")
            rc_unread, unread = self._run(root)
        self.assertNotEqual(rc_unread, 0, "an unreadable section was not refused")
        self.assertEqual(rc_absent, 0,
                         "a unit that never claimed a verifier was refused - 232 filed findings "
                         "would start failing and the refusal becomes noise")
        self.assertIn("REFUSED", unread)
        self.assertNotIn("REFUSED", absent)

    def test_criteria_with_no_verifiers_are_not_a_pass(self) -> None:
        """THE CASE THAT WOULD SURVIVE THIS FIX, named by a seat at plan review. 36 bug files
        parse to criteria carrying no `Verify:` line at all - `ac=N pass=0 unspecified=N`, exit
        0 - and widening the parser MOVES the unreadable ones into that same bucket, converting
        a would-be refusal into a silent pass while the headline count improves.

        Mutant: return 0 when every parsed criterion is unspecified - the fix reproduces the
        defect it repairs, in a different costume.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n"
                             "### AC1: it behaves\n\n- **Then** it behaves\n")
            rc, text = self._run(root)
            self.assertNotEqual(rc, 0, "criteria carrying no verifier reported a pass")
            self.assertIn("NONE carries", text)

    def test_a_well_formed_unit_still_passes(self) -> None:
        """THE POSITIVE CONTROL. `verify_ac` sits in the per-commit lane, so a refusal wired
        unconditionally satisfies every criterion above and stops every commit in every
        consuming project.

        Mutant: return the refusal for every unit regardless of what parsed - this reddens alone.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n"
                             "### AC1: it behaves\n\n- **Then** it behaves\n"
                             "- **Verify:** shell true\n")
            rc, text = self._run(root)
            self.assertEqual(rc, 0, f"a well-formed unit was refused: {text}")
            self.assertNotIn("REFUSED", text)

    def test_the_corpus_scan_reports_three_distinct_states(self) -> None:
        """The counting routine SHIPS, so the before and after figures of any fix come from the
        same code rather than a script somebody wrote once and threw away.

        Mutant: collapse the three counts into one total - the three states become
        indistinguishable and the vacuous one hides inside an improving number.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, self.HEAD + "## Summary\n\nnothing\n", "BG9001-a.md")
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n- [ ] unreadable\n",
                       "BG9002-b.md")
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n### AC1: x\n\n"
                             "- **Then** x\n", "BG9003-c.md")
            self._unit(root, self.HEAD + "## Acceptance Criteria\n\n### AC1: x\n\n"
                             "- **Then** x\n- **Verify:** shell true\n", "BG9004-d.md")
            res = verify_ac.corpus_scan(root, "bugs")
            self.assertEqual(
                (res["no_section"], res["unreadable"], res["no_verifier"], res["ok"]),
                (1, 1, 1, 1),
                f"the three blind states are not counted apart: {res}")


class TestPlanDeriveTests(unittest.TestCase):
    """US0629: the test plan is DERIVED from the unit's criteria, never assembled by hand.

    The plan for this unit was itself authored by hand and reviewed by an independent seat before
    any code existed - the unit that automates the mechanism cannot yet derive its own plan. Every
    fixture below is one the seat measured against the real parsers rather than hypothesised.
    """

    THEN = ("it emits exactly N rows keyed by criterion id, and refuses to write a plan whose "
            "row count differs from the criteria it read, because a plan assembled by hand is "
            "exactly where a criterion goes missing")

    def _unit(self, root: Path, body: str, affects="scripts/verify_ac.py") -> Path:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "US0001-x.md"
        f.write_text(f"# US0001: a unit\n\n> **Status:** Ready\n> **Points:** 3\n"
                     f"> **Affects:** {affects}\n\n{body}\n\n## Revision History\n",
                     encoding="utf-8")
        return f

    def _derive(self, root: Path, **kw):
        return verify_ac.testplan_derive(root, "US0001", **kw)

    # --- AC1 -------------------------------------------------------------------------------

    def test_every_criterion_gets_exactly_one_row(self) -> None:
        """The count is ENFORCED, and by two independent readers - `parse_story` reads the whole
        file for `### ACn`, `sdlc_md.count_acs` reads only the AC section and also counts bare
        `- [ ]` items. Counting criteria from the row list would make the equality tautological
        and the mutant that deletes it would survive every fixture, which is why the design
        constraint sits on the criterion rather than in the implementation.

        Mutants: (a) delete the equality; (b) count criteria from the rows themselves; (c) key
        rows into a dict by ac_id, collapsing a duplicate id to one row.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "## Acceptance Criteria\n\n"
                             "### AC1: one\n\n- **Then** a\n\n### AC2: two\n\n- **Then** b\n")
            res = self._derive(root)
            self.assertTrue(res["ok"], res)
            self.assertEqual((res["rows"], res["criteria"]), (2, 2))

        # BOTH directions - "differs" is symmetric, and each fixture is one the two readers
        # genuinely disagree about.
        cases = {
            "a bare checkbox beside two headings": (
                "## Acceptance Criteria\n\n### AC1: one\n\n- **Then** a\n\n"
                "### AC2: two\n\n- **Then** b\n\n- [ ] a third, unnumbered\n"),
            # The counts AGREE here (2 blocks, 2 counted), so the row-count equality cannot
            # refuse it: only the duplicate-id check can. Without that, keying rows into a dict
            # by ac_id collapses two criteria into one row and the plan governs the survivor
            # alone - a mutant this unit's own plan predicted.
            "a duplicate heading id, with the counts agreeing": (
                "## Acceptance Criteria\n\n### AC1: one\n\n- **Then** a\n\n"
                "### AC1: also one\n\n- **Then** b\n"),
            "a criterion outside the AC section": (
                "## Acceptance Criteria\n\n### AC1: one\n\n- **Then** a\n\n"
                "## Notes\n\n### AC7: stray\n\n- **Then** c\n"),
        }
        for why, body in cases.items():
            with self.subTest(why=why), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                f = self._unit(root, body)
                before = f.read_bytes()
                res = self._derive(root)
                self.assertFalse(res["ok"], f"{why}: a mismatched plan was written")
                joined = " ".join(res["errors"])
                self.assertIn("AC1", joined, "the refusal does not name what it covered")
                self.assertEqual(f.read_bytes(), before,
                                 "a refused derive wrote to the unit anyway")

    # --- AC2 -------------------------------------------------------------------------------

    def test_the_last_criterion_does_not_read_the_plan_that_follows_it(self) -> None:
        """BG0545. The last criterion's `Then` range ran to the END OF THE FILE, so it swallowed
        everything after the criteria section - including the `## Test Plan` table, which holds
        every mutant's own text. The final row's mutant was then measured for overlap against a
        passage CONTAINING that mutant, scored 100%, and was refused as a restatement of itself.

        Deterministic, and invisible to every fixture here: it struck only the LAST row, and only
        once a plan already existed, so the first derive of a unit passed and every re-derive of
        it failed. No fixture in this class had a plan when it derived. Measured on four real
        units - BG0553 AC7, BG0556 AC3, BG0576 AC5, BG0555 AC3 - all at exactly 100%.

        MUTANT: bound the last criterion at `len(lines)` again.
        """
        body = ("## Acceptance Criteria\n\n"
                "- [x] **AC1** Given a plan exists, when it is re-derived, then the row is kept.\n"
                "  - **Verify:** manual a human checks it\n\n"
                "## Test Plan\n\n"
                "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                "| AC1 | in verify_ac.py, delete the len(rows) == len(criteria) equality |  |\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, body)
            res = self._derive(root, write=False)
            self.assertTrue(
                res["ok"],
                f"re-deriving a unit that already has a plan was refused: {res.get('errors')}")
            self.assertFalse([e for e in res.get("errors") or [] if "restates" in e],
                             "the last row was measured against the plan table containing it")

    def test_a_mutant_with_no_substance_is_not_called_a_restatement(self) -> None:
        """BG0545, second half. `_overlap_ratio` returned 1.0 over an EMPTY set, so a mutant made
        only of path tokens was refused for `restating its own criterion` against a `Then` clause
        it shares not one word with. The refusal was right and its reason was false - which is
        worse than a wrong verdict, because an author fixing the named restatement is fixing
        something that is not there. The true fault has its own limb and must be the one reported.

        MUTANT: return 1.0 for the empty set again.
        """
        affects = ["scripts/verify_ac.py"]
        faults = verify_ac.testplan_row_faults("verify_ac.py", self.THEN, affects)
        self.assertTrue(faults, "a mutant naming only a path was accepted")
        self.assertFalse([f for f in faults if "restates" in f],
                         f"refused as a restatement of a clause it shares nothing with: {faults}")
        self.assertTrue(any("edit verb" in f for f in faults),
                        f"the true fault was not the one reported: {faults}")
        self.assertEqual(0.0, verify_ac._overlap_ratio("verify_ac.py", self.THEN, affects))
        # ...and a real restatement is still caught, so this did not buy headroom.
        restatement = ("in verify_ac.py, make it so the plan does not have exactly one row "
                       "per criterion")
        self.assertTrue(
            [f for f in verify_ac.testplan_row_faults(restatement, self.THEN, affects)
             if "restates" in f], "the restatement limb stopped firing")

    def test_a_restated_criterion_is_not_a_mutant(self) -> None:
        """THE DISCRIMINATING PAIR, taken from the criterion rather than invented here. Both name
        `verify_ac.py` and both carry an edit verb, so they differ in ONE property and the
        THRESHOLD is what is under test rather than the examples.

        The near-miss ACCEPT is required, not optional: without it a threshold tuned to refuse
        everything passes every refusal row for exactly the wrong reason.

        Mutants: (a) accept a blank field; (b) accept the 67% restatement; (c) drop the `Affects`
        constraint so any path-shaped token passes - the defeating mutant named a REAL file, so a
        rule checking path SHAPE rather than membership still accepts it.
        """
        affects = ["scripts/verify_ac.py"]
        refuse = "in verify_ac.py, make it so the plan does not have exactly one row per criterion"
        accept = "in verify_ac.py, delete the len(rows) == len(criteria) equality"

        faults = verify_ac.testplan_row_faults(refuse, self.THEN, affects)
        self.assertTrue(faults, "a verbatim restatement was accepted as a mutant")
        self.assertTrue(any("restates" in f for f in faults),
                        f"refused for the wrong reason: {faults}")
        self.assertEqual(verify_ac.testplan_row_faults(accept, self.THEN, affects), [],
                         "a legitimate mutant sharing its criterion's vocabulary was refused")

        # Each limb refuses for ITS OWN reason - a guard that refuses for the wrong one passes a
        # bare-refusal assertion.
        for field, marker in (("", "blank"),
                              ("delete the equality check", "Affects"),
                              # PATH-SHAPED but not a member: the defeating mutant named a REAL
                              # file, so a rule checking shape rather than membership accepts it.
                              ("in other_module.py, delete the equality", "Affects"),
                              ("in scripts/elsewhere.py, delete the equality", "Affects"),
                              ("verify_ac.py is broken somehow", "edit verb")):
            with self.subTest(field=field or "<blank>"):
                got = verify_ac.testplan_row_faults(field, self.THEN, affects)
                self.assertTrue(got, f"{field!r} was accepted")
                self.assertTrue(any(marker in f for f in got), f"{field!r} -> {got}")

        # The path is EXCLUDED from the overlap: naming a file is separately required, so
        # counting it as novel substance lets a restatement buy headroom with obliged words.
        self.assertGreater(verify_ac._overlap_ratio(refuse, self.THEN, affects),
                           verify_ac._overlap_ratio(refuse, self.THEN, []),
                           "the path is not being excluded, so a restatement is diluted by it")

    def test_an_unparseable_plan_is_never_overwritten(self) -> None:
        """A seat ran the shipped verb against US0629's OWN artefact and watched 178 lines
        become 79: a prose plan yields no table rows, so `existing` is empty and the section is
        replaced with placeholders at exit 0. An independently-reviewed artefact destroyed by the
        command that exists to protect it.

        Mutant: replace a section that parsed to no rows - this reddens, and the file it would
        have destroyed is asserted byte-identical.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            f = self._unit(root, "## Acceptance Criteria\n\n### AC1: one\n\n- **Then** a\n\n"
                                 "## Test Plan\n\n> Authored by hand before any code.\n\n"
                                 "AC1 is falsified by deleting the guard in verify_ac.py, and "
                                 "the assertion that catches it is the count equality.\n")
            before = f.read_bytes()
            res = self._derive(root)
            self.assertFalse(res["ok"], "an unreadable plan was overwritten")
            self.assertIn("cannot read", " ".join(res["errors"]))
            self.assertEqual(f.read_bytes(), before, "the authored plan was destroyed")

    def test_the_ceiling_is_the_first_refused_value(self) -> None:
        """A mutant sitting EXACTLY on the ceiling is a restatement. `>` accepted it, and a seat
        showed 0.60 is reachable - an off-by-one on the one criterion whose whole point is that
        the threshold is the thing under test.

        Mutant: `>=` back to `>` - the exact-ceiling case flips to accepted and this reddens.
        """
        then = "alpha bravo charlie"
        mutant = "in verify_ac.py, delete alpha bravo charlie delta"
        affects = ["scripts/verify_ac.py"]
        self.assertAlmostEqual(
            verify_ac._overlap_ratio(mutant, then, affects), 0.60, places=2,
            msg="the fixture no longer sits on the ceiling, so it pins nothing")
        self.assertTrue(verify_ac.testplan_row_faults(mutant, then, affects),
                        "a mutant exactly on the ceiling was accepted")

    def test_a_criterion_with_no_then_bullet_still_measures_its_overlap(self) -> None:
        """The fallback branch, which nothing covered. Reachable on every unit authored to the
        house bug template - which is most bugs, per BG0530 - and the test-plan gate applies to
        every type.

        Mutant: return "" from the fallback - overlap measures 0% for those units and the
        restatement limb accepts everything they write.
        """
        body = "- it refuses the row and names the criterion"
        lines = ["### AC1: it refuses", "", body]
        self.assertIn("refuses", verify_ac._then_clause(lines, 0, len(lines)),
                      "a criterion with no **Then** bullet contributes no text at all")
        faults = verify_ac.testplan_row_faults(
            "in verify_ac.py, make it so it refuses the row and names the criterion",
            verify_ac._then_clause(lines, 0, len(lines)), ["scripts/verify_ac.py"])
        self.assertTrue(any("restates" in f for f in faults),
                        "a restatement of a Then-less criterion was accepted")

    def test_a_refused_row_names_its_criterion_through_the_shipped_verb(self) -> None:
        """The LANE half: the refusal must reach an operator through `verify_ac.py testplan
        derive`, not only through the predicate. Mutant: return the faults and exit 0."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._unit(root, "## Acceptance Criteria\n\n### AC1: one\n\n"
                             f"- **Then** {self.THEN}\n\n"
                             "## Test Plan\n\n| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                             "| AC1 | in verify_ac.py, make it so the plan does not have exactly "
                             "one row per criterion | one |\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = verify_ac.main(["testplan", "derive", "--unit", "US0001", "--root", str(root)])
            self.assertEqual(rc, 2, "the shipped verb accepted a restatement")
            self.assertIn("AC1", err.getvalue())
            self.assertIn("restates", err.getvalue())

    # --- AC3 -------------------------------------------------------------------------------

    def test_derive_is_idempotent_and_preserves_authored_mutants(self) -> None:
        """Three overwrite mutants all preserve a distinctive string, so "the authored text
        survives" is necessary and NOT sufficient: regenerate-and-append leaves the old section
        in place while the generated one governs; reassign attaches it to another criterion's
        row; append-within-the-cell makes it `<authored>; regenerated: <derived>`.

        So: exactly ONE `## Test Plan`, the assertion is KEYED to the criterion, and it is cell
        EQUALITY rather than containment. Idempotency carries a negative control - run 1 must NOT
        report a no-op, run 2 must, and run 2's bytes must equal run 1's.
        """
        authored = "in verify_ac.py, delete the len(rows) == len(criteria) equality"
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            f = self._unit(root, "## Acceptance Criteria\n\n### AC1: one\n\n"
                                 f"- **Then** {self.THEN}\n\n### AC2: two\n\n- **Then** b\n")
            first = self._derive(root)
            self.assertTrue(first["ok"], first)
            self.assertFalse(first["unchanged"], "run 1 reported a no-op before writing anything")

            # Author a mutant into AC2's row, as a human would.
            text = f.read_text(encoding="utf-8")
            f.write_text(text.replace(
                f"| AC2 | {verify_ac._TESTPLAN_PLACEHOLDER} |", f"| AC2 | {authored} |"),
                encoding="utf-8")
            authored_bytes = f.read_bytes()

            second = self._derive(root)
            self.assertTrue(second["ok"], second)
            self.assertTrue(second["unchanged"], "a re-derive rewrote a plan that already matched")
            self.assertEqual(f.read_bytes(), authored_bytes,
                             "the re-derive changed the file it called unchanged")

            body = f.read_text(encoding="utf-8")
            self.assertEqual(body.count(verify_ac._TESTPLAN_HEADING), 1,
                             "a second Test Plan section was appended beside the first")
            # `_testplan_rows` returns one entry PER ROW now, so a criterion's mutants are a
            # list. Asserted through the grouped accessor rather than by index, and as the whole
            # list rather than its first element - a criterion that gained a spurious second row
            # would otherwise still read as preserved.
            rows = verify_ac.testplan_rows_by_criterion(body)
            self.assertEqual(rows["AC2"], [authored],
                             "the authored mutant was reassigned, appended to, or regenerated")
            self.assertEqual(rows["AC1"], [verify_ac._TESTPLAN_PLACEHOLDER])

    def test_a_derived_plan_does_not_stale_a_green_verify_entry(self) -> None:
        """`ac_fingerprint` covers ac_id, title and verifier. Writing a Test Plan section must not
        move it, or every unit's verified stamp goes stale the moment it gains a plan.

        Mutant: fold the plan's rows into the fingerprint - this reddens.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            f = self._unit(root, "## Acceptance Criteria\n\n### AC1: one\n\n"
                                 "- **Then** a\n- **Verify:** pytest x\n")
            before = verify_ac.ac_fingerprint(f.read_text(encoding="utf-8"))
            self.assertTrue(self._derive(root)["ok"])
            after = verify_ac.ac_fingerprint(f.read_text(encoding="utf-8"))
            self.assertEqual(before, after,
                             "writing a test plan staled the unit's verification fingerprint")


class LaneCheckTests(unittest.TestCase):
    """A criterion verified only through the library is not evidence the feature ships.

    US0577 shipped `brief_fingerprint` with a passing acceptance test and a feature that did
    not work: the test computed it in-process while the CLI never called it. The wiring is
    exactly what a library test does not exercise, and it is where this defect class lives.
    """

    def _fixture(self, d, verifier_body: str, verify_line: str):
        root = Path(d)
        (root / "scripts").mkdir(parents=True, exist_ok=True)
        (root / "tests").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / "stories").mkdir(parents=True, exist_ok=True)
        # A CLI-BEARING script: both markers, so a library with a convenience runner and a
        # parser with no entry point are both excluded.
        (root / "scripts" / "thing.py").write_text(
            "import argparse\n\ndef fingerprint(x):\n    return x\n\n"
            "def main(argv=None):\n    argparse.ArgumentParser().parse_args(argv)\n    return 0\n",
            encoding="utf-8")
        (root / "tests" / "test_thing.py").write_text(verifier_body, encoding="utf-8")
        story = root / "sdlc-studio" / "stories" / "US0001-x.md"
        story.write_text(
            "# US0001: a unit\n\n> **Status:** Review\n> **Points:** 3\n"
            "> **Affects:** scripts/thing.py, tests/test_thing.py\n\n"
            "## Acceptance Criteria\n\n### AC1: it behaves\n\n"
            "- **Then** it behaves\n"
            f"- **Verify:** {verify_line}\n", encoding="utf-8")
        return root, story

    def test_a_library_only_verifier_is_reported(self) -> None:
        """MUTANT: return [] from lane_check, or drop the `_enters_the_lane` test."""
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\ndef test_it():\n    assert thing.fingerprint('a') == 'a'\n",
                "pytest tests/test_thing.py")
            found = mod.lane_check(root, [story])
        self.assertEqual(1, len(found), f"the library-only verifier was not reported: {found}")
        self.assertIn("scripts/thing.py", found[0]["cli"])

    def test_a_cli_verifier_is_clean(self) -> None:
        """The control. MUTANT: report every criterion.

        A check that flags everything discriminates no better than one that flags nothing, and
        would be switched off on a gate already over its ceiling.
        """
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\ndef test_it():\n    assert thing.main([]) == 0\n",
                "pytest tests/test_thing.py")
            found = mod.lane_check(root, [story])
        self.assertEqual([], found, f"a verifier that enters the entry point was reported: {found}")

    def test_detection_is_by_execution_not_by_name(self) -> None:
        """MUTANT: decide from the test's NAME rather than its source.

        A naming convention is satisfied by a rename. This test's name says `cli` while its
        body never enters the lane, so a name-based detector reports it clean and this fails.
        """
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\ndef test_the_cli_entry_point_works():\n"
                "    assert thing.fingerprint('a') == 'a'\n",
                "pytest tests/test_thing.py")
            found = mod.lane_check(root, [story])
        self.assertEqual(1, len(found),
                         "a test named for the CLI but never entering it was reported clean")

    def test_a_unit_touching_no_cli_is_not_reported(self) -> None:
        """MUTANT: report every unit regardless of what it touches.

        A pure-library or docs unit has no entry point to enter, so the question does not
        arise - flagging it would be noise on units that cannot act on it.
        """
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\ndef test_it():\n    assert thing.fingerprint('a') == 'a'\n",
                "pytest tests/test_thing.py")
            (root / "scripts" / "thing.py").write_text(
                "def fingerprint(x):\n    return x\n", encoding="utf-8")  # no CLI now
            found = mod.lane_check(root, [story])
        self.assertEqual([], found, "a unit touching no CLI-bearing script was reported")


    def test_entry_made_through_a_shared_test_helper_is_credited(self) -> None:
        """BG0487. MUTANT: judge the scoped node's own source only.

        A class that shells the CLI once in a `_run` helper and calls `self._run(...)` from
        every method is a correct and common shape - it is the shape used by this repo's own
        `SwapTests` and `AddEpicTests`. Scoping to the node alone reports it as never entering
        the lane, which is a detector telling tested work it is untested. It fired on three
        units the sprint that shipped it had delivered.
        """
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\n\nclass T:\n"
                "    def _run(self, *a):\n        return thing.main(list(a))\n\n"
                "    def test_it(self):\n        assert self._run() == 0\n",
                "pytest tests/test_thing.py::T::test_it")
            found = mod.lane_check(root, [story])
        self.assertEqual([], found,
                         f"entry made through a shared helper was reported as no entry: {found}")

    def test_helper_resolution_is_one_level_and_does_not_credit_the_whole_file(self) -> None:
        """MUTANT: fall back to whole-file matching when the node shows no entry.

        This is the failure the scoping fixed in the first place - whole-file matching reported
        0 findings over 615 units, because one `main([...])` anywhere in a thousand-line module
        marked every criterion in it clean. The helper the node calls must enter the lane; a
        DIFFERENT helper elsewhere in the file entering it must not count.
        """
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\n\nclass T:\n"
                "    def _unrelated(self, *a):\n        return thing.main(list(a))\n\n"
                "    def _lib(self, x):\n        return thing.fingerprint(x)\n\n"
                "    def test_it(self):\n        assert self._lib('a') == 'a'\n",
                "pytest tests/test_thing.py::T::test_it")
            found = mod.lane_check(root, [story])
        self.assertEqual(1, len(found),
                         "an unrelated helper elsewhere in the file credited a library-only "
                         "verifier - the fix restored whole-file permissiveness")

    def test_a_library_only_method_beside_lane_entering_ones_is_still_reported(self) -> None:
        """The shape the BG0487 repair could plausibly have hidden. MUTANT: credit the class.

        Distinct from the plain library-only case: here the class DOES enter the lane, from a
        sibling test method, and only the criterion's own node does not. A repair that widened
        from the node to the class would report this clean, and that is the original US0577
        defect walking back in through the fix for its detector.
        """
        mod = verify_ac
        with tempfile.TemporaryDirectory() as d:
            root, story = self._fixture(
                d,
                "import thing\n\n\nclass T:\n"
                "    def test_other(self):\n        assert thing.main([]) == 0\n\n"
                "    def test_it(self):\n        assert thing.fingerprint('a') == 'a'\n",
                "pytest tests/test_thing.py::T::test_it")
            found = mod.lane_check(root, [story])
        self.assertEqual(1, len(found),
                         "a library-only criterion was cleared by a SIBLING method entering the "
                         "lane - the original defect shape is no longer reported")


class UnanswerableGroupTests(unittest.TestCase):
    """US0637: the duplicate groups no collection can answer are named one by one.

    A group whose selector `selector_resolves` answers None for - `manual`, `grep`, `shell`, an
    absent runner - cannot be split into discriminating halves, because nothing can say what
    either half selects. Those groups are genuinely exempt from the burn-down, and the reader
    needs to see WHICH: a count cannot be taken apart, so an exemption that quietly stopped
    being true is indistinguishable from one that still holds.
    """

    def _lint(self, root) -> str:
        mod = verify_ac
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            mod.main(["lint", "--root", str(root)])
        return out.getvalue() + err.getvalue()

    def _story(self, root, sid, verifier, acs=2):
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        body = "".join(
            f"\n### AC{i}: it behaves {i}\n\n- **Given** a thing\n- **When** it runs\n"
            f"- **Then** it works\n- **Verify:** {verifier}\n" for i in range(1, acs + 1))
        (d / f"{sid}-x.md").write_text(
            f"# {sid}: a story\n\n> **Status:** Ready\n> **Epic:** EP0100\n> **Points:** 2\n"
            f"\n## Acceptance Criteria\n{body}", encoding="utf-8")

    def test_the_set_is_derived_from_the_resolver_at_lint_time(self) -> None:
        """MUTANT: read the exempt set from a hard-coded list instead of calling the resolver.

        Two groups, identical in shape, differing ONLY in whether their selector is resolvable.
        A hard-coded list cannot tell them apart; the resolver can. That is the whole claim.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            self._story(root, "US0001", "shell npm run lint:links")
            # THE DISCRIMINATING CASE, and it took two attempts to find. A missing pytest FILE
            # is not unanswerable - the resolver answers False for it, which is `stale`, a
            # different fact. What it answers None for is an ABSENT RUNNER: `jest` is not
            # installed here, so the resolver cannot decide what the selector selects even
            # though the verb reads as perfectly resolvable. Without a case like this the test
            # passes against an implementation that just groups by verb, and the claim - that
            # the set is DERIVED from the resolver - is unheld. A hard-coding mutant survived
            # the first version for exactly that reason.
            self._story(root, "US0005", "jest some/spec.test.js -t a thing")
            # THE CASE A VERB HEURISTIC CANNOT REACH. `jest` above is outside `_COLLECTABLE`, so
            # `head not in _COLLECTABLE` short-circuits before the absent-runner branch ever runs
            # and "the resolver answered None" is operationally the same sentence as "the verb is
            # not pytest" - which is why swapping the resolver for a verb comparison survived
            # (BG0523). This selector's verb IS pytest, and the resolver still answers None: it
            # names no file target, so no collection can decide what it selects.
            self._story(root, "US0006", "pytest -k a_thing")
            text = self._lint(root)
        self.assertIn("unanswerable", text, "no unanswerable section was produced")
        exempt = text.split("unanswerable", 1)[1]
        self.assertIn("US0001", exempt,
                      "the manual group was not derived as unanswerable")
        self.assertIn("US0005", exempt,
                      "a selector whose RUNNER is absent was not reported exempt - the set is "
                      "being guessed from the verb rather than derived from the resolver")
        self.assertIn("US0006", exempt,
                      "a COLLECTABLE-verb selector the resolver cannot answer was not reported "
                      "exempt - the set is a verb comparison wearing the resolver's name")

    def test_each_member_is_named_with_its_verb_and_claimants(self) -> None:
        """MUTANT: print a count of exempt groups instead of a line each.

        Asserts the verb AND every claiming AC appear, because a reader who cannot see which
        ACs claim a group cannot judge whether the exemption is still honest.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            self._story(root, "US0003", "shell npm run lint:links", acs=3)
            text = self._lint(root)
        exempt = text.split("unanswerable", 1)[1]
        self.assertIn("[shell]", exempt, "the verb making it unanswerable is not named")
        for ac in ("US0003 AC1", "US0003 AC2", "US0003 AC3"):
            with self.subTest(ac=ac):
                self.assertIn(ac, exempt, f"{ac} claims the group but is not named")

    def test_the_resolver_and_a_verb_heuristic_disagree_and_the_report_follows_the_resolver(self):
        """MUTANT: replace the `selector_resolves(...) is None` call in the lint with
        `verb != "pytest"`.

        The disagreement is asserted FIRST, as the premise: `pytest` is inside `_COLLECTABLE`,
        so a verb heuristic calls this selector answerable, while the resolver answers None
        because the selector names no file any collection could be run over. Every fixture the
        set was previously derived over used a verb outside `_COLLECTABLE`, where the two
        agree by construction - so the derivation claim was unpinned however the report read.
        """
        self.assertIn("pytest", verify_ac._COLLECTABLE,
                      "the premise is gone: `pytest` is no longer a collectable verb, so this "
                      "selector no longer separates the resolver from a verb comparison")
        self.assertIsNone(verify_ac.selector_resolves("pytest -k a_thing"),
                          "the resolver now answers a selector naming no file target, so this "
                          "case no longer discriminates - find another and say why")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            self._story(root, "US0007", "pytest -k a_thing")
            text = self._lint(root)
        self.assertIn("unanswerable", text, "no unanswerable section was produced")
        splittable, exempt = text.split("unanswerable", 1)
        self.assertIn("US0007", exempt,
                      "a group the resolver cannot answer was not reported exempt")
        self.assertNotIn("US0007", splittable,
                         "the same group was also told to split into discriminating halves, so "
                         "the report is following the verb rather than the resolver")

    def test_an_unanswerable_group_is_not_also_reported_as_splittable(self) -> None:
        """MUTANT: report every group in both places.

        Telling an author to split a group that cannot be split is advice they cannot take, and
        it is how a report stops being read.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            self._story(root, "US0004", "shell npm run lint:links")
            text = self._lint(root)
        splittable = text.split("unanswerable", 1)[0]
        self.assertNotIn("US0004", splittable,
                         "an unanswerable group was also told to split into discriminating halves")

class LaneCheckScopeTests(unittest.TestCase):
    """BG0491: the corpus sweep judged stories and silently omitted bugs."""

    def test_the_lane_check_sweep_covers_bugs_not_only_stories(self) -> None:
        """MUTANT: drop the `bugs/BG*.md` glob from `cmd_lane_check`, leaving stories only.

        `--ids BG0487` then prints `0 unit(s)`, which is indistinguishable from a clean result
        for a unit nothing looked at - and 487 bugs sit outside a figure CR0539 proposes making
        blocking. Asserted on the SOURCE of the sweep rather than on a corpus count, because a
        count moves with the corpus and would make this test a monitor rather than a check.
        """
        import inspect
        src = inspect.getsource(verify_ac.cmd_lane_check)
        self.assertIn('"bugs"', src,
                      "the lane-check sweep must glob the bugs directory, not stories alone")
        self.assertIn('BG*.md', src, "bugs are selected by their own id prefix")
        # The control: stories are still swept. A fix that swapped one for the other would
        # satisfy the assertions above while losing the half that already worked.
        self.assertIn('US*.md', src, "stories must remain in scope")


class EditVerbVocabularyTests(unittest.TestCase):
    """BG0563/BG0534: the vocabulary enumerated only subtractive edits."""

    def test_an_additive_or_positional_edit_verb_is_accepted(self) -> None:
        """MUTANT: remove the additive and positional groups from `_EDIT_VERBS`.

        A mutant that ADDS or MOVES something could not be stated at all, so `testplan derive`
        refused legitimate rows and trained authors to reword for the checker rather than for
        the reader.
        """
        for phrase in ("add a second call to the writer",
                       "insert a guard before the loop",
                       "move the affects check below the batch write",
                       "print the bare message"):
            with self.subTest(phrase=phrase):
                self.assertTrue(any(v in phrase for v in verify_ac._EDIT_VERBS),
                                f"{phrase!r} names a real production edit and must be accepted")

    def test_an_outcome_phrased_mutant_is_still_refused(self) -> None:
        """The control. Widening the vocabulary must not widen it to nothing - a mutant stating
        what STOPS WORKING rather than what is CHANGED still names no edit."""
        for phrase in ("the suite goes red", "it fails", "the guard no longer holds"):
            with self.subTest(phrase=phrase):
                self.assertFalse(any(v in phrase for v in verify_ac._EDIT_VERBS),
                                 f"{phrase!r} is an outcome, not an edit")

class ResolvedDuplicateKeyTests(unittest.TestCase):
    """BG0486. The ratchet grouped on the written string, so two criteria naming the identical
    run in different words formed a group of one under each spelling and were reported as no
    duplicate at all - while two ACs sharing a selector cannot both discriminate, whichever way
    each was typed."""

    def test_dup_group_key_resolves_the_command_rather_than_the_spelling(self) -> None:
        """AC1, the merges. MUTANT: return the written form again."""
        for a, b in [("pytest x.py::T::t", "pytest -q x.py::T::t"),
                     ("pytest -q -x a.py", "pytest -x -q a.py")]:
            with self.subTest(f"{a} == {b}"):
                self.assertEqual(verify_ac.dup_group_key(a), verify_ac.dup_group_key(b),
                                 "one command written two ways did not group")

    def test_two_different_selectors_are_not_merged(self) -> None:
        """AC3, and the reason AC1 is not the whole story: a key that merged EVERYTHING would
        satisfy the merges and destroy the guard. MUTANT: key on the runner alone."""
        for a, b in [("pytest a.py", "pytest b.py"), ("pytest -k one a.py", "pytest -k two a.py")]:
            with self.subTest(f"{a} != {b}"):
                self.assertNotEqual(verify_ac.dup_group_key(a), verify_ac.dup_group_key(b),
                                    "two genuinely different selectors were merged")

    def test_dup_group_reports_the_written_form_not_the_resolved_key(self) -> None:
        """AC2. Quoting a resolved argv back at an author names a line in nobody's file.
        MUTANT: report the group key instead of the spelling."""
        d = Path(tempfile.mkdtemp(prefix="dupwritten_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        f = d / "US9001-x.md"
        f.write_text("# US9001: x\n\n> **Status:** Draft\n\n## Acceptance Criteria\n\n"
                     "### AC1: a\n\n- **Verify:** pytest tests/t.py::T::t\n\n"
                     "### AC2: b\n\n- **Verify:** pytest -q tests/t.py::T::t\n", encoding="utf-8")
        groups = verify_ac.duplicate_verifiers([f])
        self.assertEqual(1, len(groups), f"the two spellings did not group: {groups}")
        # The LOWEST spelling, so the identity is deterministic - and whichever it is, it is a
        # line that appears in the corpus, which the resolved key is not.
        written = {"pytest tests/t.py::T::t", "pytest -q tests/t.py::T::t"}
        self.assertIn(groups[0]["verifier"], written,
                      "the group is reported as an internal key rather than a written line")
        self.assertEqual(sorted(written),
                         sorted([groups[0]["verifier"], *groups[0]["also_written"]]),
                         "the other spelling in the group is not shown beside it")


class MultiRowTestPlanTests(unittest.TestCase):
    """BG0596 / BG0597: a criterion may declare several mutants, and each is its own claim.

    Every assertion here compares against an INDEPENDENT reader of the file - a plain scan for
    `| AC` rows - never against the repaired parser's own idea of what it holds. Two readers of
    one artefact disagreeing is how the row count and the criterion count came apart in the
    first place, so the test must not use the reader under repair as its own witness.
    """

    PLAN = ("## Test Plan\n\n"
            "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
            "| AC1 | in `verify_ac.py`, delete the first branch | first |\n"
            "| AC1 | in `verify_ac.py`, delete the second branch | second |\n"
            "| AC2 | in `verify_ac.py`, delete the single path | only |\n")

    BODY = ("## Acceptance Criteria\n\n"
            "- [ ] **AC1** Given two rows on one criterion, when the join runs, then both survive\n"
            "- [ ] **AC2** Given one row, when the join runs, then the count is unchanged\n\n")

    @staticmethod
    def _scan(path) -> int:
        """The independent reader: count `| ACn |` rows straight out of the file."""
        return sum(1 for ln in path.read_text(encoding="utf-8").splitlines()
                   if re.match(r"^\|\s*AC\d+\s*\|", ln))

    def _fixture(self, root, body, plan):
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        f = d / "BG9001-x.md"
        f.write_text(f"# BG9001: a unit\n\n> **Status:** Open\n> **Severity:** Medium\n"
                     f"> **Points:** 2\n> **Affects:** scripts/verify_ac.py\n"
                     f"> **Created:** 2026-08-19\n\n## Summary\n\nA thing.\n\n"
                     f"{body}{plan}\n## Revision History\n", encoding="utf-8")
        return f

    # --- BG0596 AC1: the read path keeps every row -----------------------------------------
    def test_the_parser_returns_one_entry_per_declared_row(self) -> None:
        """MUTANT: in `verify_ac.py`, revert `_testplan_rows` to a single-assignment dict."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            f = self._fixture(root, self.BODY, self.PLAN)
            rows = verify_ac._testplan_rows(f.read_text(encoding="utf-8"))
            self.assertEqual(self._scan(f), len(rows),
                             "the parser and a plain scan of the same file disagree about how "
                             "many rows it holds")
            self.assertEqual(3, len(rows))
            self.assertEqual([0, 1, 0], [r["row"] for r in rows],
                             "row identity is not 0-based within each criterion, so two mutants "
                             "on one AC cannot be told apart")

    # --- BG0597 AC1: the write path keeps every row ----------------------------------------
    def test_a_re_derive_preserves_every_row_and_exits_zero(self) -> None:
        """MUTANT: in `verify_ac.py`, revert `testplan_derive`'s row loop to emit one row per
        criterion block.

        The exit-0 clause is load-bearing: a fix that simply REFUSED every multi-row plan would
        lose no rows and satisfy a bare 'both rows survive' assertion, while making the format
        unmaintainable through the shipped command.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            f = self._fixture(root, self.BODY, self.PLAN)
            before = self._scan(f)
            res = verify_ac.testplan_derive(root, "BG9001", write=True)
            self.assertTrue(res["ok"], res)
            self.assertEqual(before, self._scan(f),
                             "a re-derive dropped an authored row - the count fell")
            body = f.read_text(encoding="utf-8")
            self.assertLess(body.index("delete the first branch"),
                            body.index("delete the second branch"),
                            "the rows survived but their order did not, so a set comparison "
                            "would pass while the author's first mutant moved")

    def test_the_shipped_command_preserves_rows_through_a_subprocess(self) -> None:
        """BG0597 AC3's route: the SHIPPED entry point, as a subprocess, against a root asserted
        to be under tempfile. A library call cannot see a command's wiring, and this defect was
        found by running the command rather than by reading the function."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.assertTrue(str(root).startswith(tempfile.gettempdir()),
                            "the fixture root is not under tempfile - this test would write "
                            "into a real workspace")
            f = self._fixture(root, self.BODY, self.PLAN)
            before = self._scan(f)
            script = (Path(__file__).resolve().parents[1] / "verify_ac.py")
            r = subprocess.run([sys.executable, "-B", str(script), "testplan", "derive",
                                "--unit", "BG9001", "--root", str(root)],
                               capture_output=True, text=True)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertEqual(before, self._scan(f),
                             f"the shipped command changed the row count: {r.stdout}{r.stderr}")

    # --- BG0597 AC2: an orphan row is refused, not deleted ---------------------------------
    def test_an_orphan_row_is_refused_and_named(self) -> None:
        """MUTANT: in `verify_ac.py`, delete the orphan-row refusal.

        The second silent-loss path, found while BG0597's own criteria were being authored: a
        row whose criterion is no longer declared - what renumbering an AC produces - used to
        vanish at exit 0 with nothing printed.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            orphan = self.PLAN + "| AC7 | in `verify_ac.py`, delete the gone branch | gone |\n"
            f = self._fixture(root, self.BODY, orphan)
            before = self._scan(f)
            res = verify_ac.testplan_derive(root, "BG9001", write=True)
            self.assertFalse(res["ok"], "an orphan row was accepted and would be deleted")
            self.assertTrue(any("AC7" in e for e in res["errors"]),
                            f"the refusal did not name the row it would have dropped: {res}")
            self.assertEqual(before, self._scan(f), "the refusal still wrote the file")

    # --- BG0597 AC4: the single-row case still round-trips ---------------------------------
    def test_a_single_row_plan_round_trips_unchanged(self) -> None:
        """MUTANT: in `verify_ac.py`, make it refuse every re-derive.

        The CONTROL. Without it, a fix that refuses everything satisfies both preservation
        criteria above. The Title column is regenerated from the criterion by design, so only
        the Criterion and Mutant columns are compared.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            single = ("## Test Plan\n\n| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                      "| AC1 | in `verify_ac.py`, delete the first branch | t |\n"
                      "| AC2 | in `verify_ac.py`, delete the single path | t |\n")
            f = self._fixture(root, self.BODY, single)
            res = verify_ac.testplan_derive(root, "BG9001", write=True)
            self.assertTrue(res["ok"], res)
            cols = [tuple(c.strip() for c in ln.strip("|").split("|")[:2])
                    for ln in f.read_text(encoding="utf-8").splitlines()
                    if re.match(r"^\|\s*AC\d+\s*\|", ln)]
            self.assertEqual([("AC1", "in `verify_ac.py`, delete the first branch"),
                              ("AC2", "in `verify_ac.py`, delete the single path")], cols)



# -----------------------------------------------------------------------------
# revert-check (US0671, US0672, US0673) and derived Verification depth (US0675)
# -----------------------------------------------------------------------------

_PROD_BASE = "BASE_ONLY = 1\n"
_PROD_HEAD = 'BASE_ONLY = 1\nSHIPPED_MARKER = "SHIPPED_MARKER"\n'

_REBUILT_TEST = '''\
def _rebuild():
    """A private helper holding its OWN copy of the production constant."""
    return "SHIPPED_MARKER"


def test_marker_is_present():
    assert _rebuild() == "SHIPPED_MARKER"
'''

_REACHING_TEST = '''\
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


def test_marker_reaches_production():
    import prod
    assert prod.SHIPPED_MARKER == "SHIPPED_MARKER"
'''


import gitutil  # noqa: E402 - tests/ is on the path; the CONFINED git runner


def _git(cwd, *args):
    """Every fixture git call goes through the confined runner.

    An inherited repo-locating variable redirects a fixture's git onto the surrounding
    checkout - it emptied this repository's index once - and the pre-commit hook that runs
    this suite exports them.
    """
    gitutil.git(args, cwd)


class _RevertRepo:
    """A REAL git repository holding one unit, its production file and its verifiers.

    Real git and real files rather than an injected reader, because the whole subject is what
    happens to bytes on disk while the check runs. A stubbed `git show` would prove the
    check's arithmetic and nothing about the property every criterion here is about.
    """

    def __init__(self, criteria: str, affects: str, *, test_body: str | None = None,
                 extra_sections: str = "", uid: str = "US9001") -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="revert_check_"))
        (self.tmp / "scripts").mkdir()
        (self.tmp / "tests").mkdir()
        self.prod = self.tmp / "scripts" / "prod.py"
        self.prod.write_text(_PROD_BASE, encoding="utf-8")
        if test_body:
            (self.tmp / "tests" / "test_prod.py").write_text(test_body, encoding="utf-8")
        _git(self.tmp, "init", "-q")
        _git(self.tmp, "config", "user.email", "t@example.com")
        _git(self.tmp, "config", "user.name", "t")
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-qm", "base")
        self.base = gitutil.git(["rev-parse", "HEAD"], self.tmp).stdout.decode().strip()
        self.prod.write_text(_PROD_HEAD, encoding="utf-8")
        _git(self.tmp, "add", "-A")
        _git(self.tmp, "commit", "-qm", "ship")
        stories = self.tmp / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        self.uid = uid
        self.unit = stories / f"{uid}-fixture.md"
        self.unit.write_text(
            f"# {uid}: fixture\n\n"
            f"> **Status:** Draft\n"
            f"> **Affects:** {affects}\n\n"
            f"## Acceptance Criteria\n\n{criteria}\n{extra_sections}",
            encoding="utf-8")

    def hashes(self) -> dict:
        """Content, MODE and link-target for every file outside `.git`.

        Content alone was not enough, and that gap is why two defects shipped: a file recreated
        by `write_bytes` came back at the umask default (a tracked `100755` script reading
        `100644`, `git status` dirty) and a symlink came back as a regular file holding its
        target's bytes. Both leave the content hash identical, so an assertion over content
        was structurally incapable of failing on either. `lstat`, never `stat`, so the symlink
        itself is measured rather than what it points at."""
        import hashlib
        import os as _os
        import stat as _stat
        out = {}
        for p in sorted(self.tmp.rglob("*")):
            rel = str(p.relative_to(self.tmp)).replace("\\", "/")
            if ".git/" in rel or rel.startswith(".git"):
                continue
            try:
                st = p.lstat()
            except OSError:
                continue
            if _stat.S_ISLNK(st.st_mode):
                out[rel] = ("symlink", _os.readlink(p), _stat.S_IMODE(st.st_mode))
            elif _stat.S_ISREG(st.st_mode):
                out[rel] = ("file", hashlib.sha256(p.read_bytes()).hexdigest(),
                            _stat.S_IMODE(st.st_mode))
        return out

    def cleanup(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


def _ac(num: int, verifier: str, text: str = "the change is reached") -> str:
    return f"- [ ] **AC{num}** {text}\n  - **Verify:** {verifier}\n"


class RevertCheckTests(unittest.TestCase):
    """`verify_ac.py revert-check` - CR0547.

    Every case drives `verify_ac.main([...])`, the shipped entry point, rather than
    `revert_check` directly: the wiring between the command and the function is the part a
    library test does not exercise, and this repository has shipped a working function behind
    a command that never called it.
    """

    def setUp(self) -> None:
        self.repos: list = []

    def tearDown(self) -> None:
        for r in self.repos:
            r.cleanup()

    def _repo(self, *args, **kwargs) -> _RevertRepo:
        r = _RevertRepo(*args, **kwargs)
        self.repos.append(r)
        return r

    def _run(self, repo, extra=()) -> tuple:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = verify_ac.main(["revert-check", "--unit", repo.uid, "--root", str(repo.tmp),
                                   "--base", repo.base, *extra])
        return code, buf.getvalue()

    def test_a_wholly_green_unit_is_refused(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, delete the `if counted and not result["red"]`
        branch so a unit whose every measurable criterion stays green returns `pass`.

        Both criteria grep text the BASE revision already carries, so reverting the production
        change moves neither. That is the defect the whole command exists for: a test that
        passes without the change never reached it."""
        repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py")
                          + _ac(2, "grep 'BASE_ONLY = 1' scripts/prod.py"),
                          "scripts/prod.py")
        code, out = self._run(repo)
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)
        self.assertIn("AC1", out)
        self.assertIn("AC2", out)

    def test_a_unit_whose_verifiers_go_red_passes(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, refuse whenever ANY criterion stays green -
        `if counted and result["green"]` in place of `not result["red"]`.

        The paired control. AC1 greps the shipped marker and goes red on the revert; AC2 greps
        base text and stays green. A gate that refused this has measured nothing, because it
        would refuse every unit put in front of it."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py")
                          + _ac(2, "grep BASE_ONLY scripts/prod.py"),
                          "scripts/prod.py")
        code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertIn("PASSES", out)

    def test_declared_exemptions_do_not_trigger_a_refusal(self) -> None:
        """MUTANT: in `verify_ac.revert_exemptions`, return `{}`.

        Three legitimately-green criteria, one of each declared class - a well-formed
        `unnameable` plan row, a reasoned `Revert-check-exempt` field, and a criterion whose
        plan row names only test code - beside one that goes red. RUN-01M0CT8P measured five
        such criteria in a single six-unit batch, so a check without the taxonomy refuses
        correct work on its first outing, and refusing correct work is how a gate gets
        switched off."""
        plan = ("\n## Test Plan\n\n"
                "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                "| AC1 | in `scripts/prod.py`, drop the shipped marker | a |\n"
                "| AC2 | unnameable: the criterion pins an ordering no single edit can "
                "reverse without also deleting the field it orders | b |\n"
                "| AC3 | in `tests/test_prod.py`, rename the private helper | c |\n"
                "| AC4 | in `scripts/prod.py`, restore the base constant | d |\n")
        repo = self._repo(
            _ac(1, "grep SHIPPED_MARKER scripts/prod.py")
            + _ac(2, "grep BASE_ONLY scripts/prod.py")
            + _ac(3, "grep BASE_ONLY scripts/prod.py")
            + _ac(4, "grep BASE_ONLY scripts/prod.py"),
            "scripts/prod.py, tests/test_prod.py",
            test_body=_REBUILT_TEST, extra_sections=plan)
        text = repo.unit.read_text(encoding="utf-8")
        repo.unit.write_text(text.replace(
            "> **Affects:**",
            "> **Revert-check-exempt:** AC4 - the paired control asserts the behaviour that "
            "stood BEFORE the change, so it must stay green when the change is removed\n"
            "> **Affects:**"), encoding="utf-8")
        code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        for ac in ("AC2", "AC3", "AC4"):
            self.assertRegex(out, rf"{ac}\s+exempt", out)

    def test_the_unexercised_change_fixture_is_refused(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, invert the run classification -
        `"red" if res.ok else "green"`.

        BG0593's pre-repair working-tree state, reproduced as a fixture: the production change
        is present, and the test rebuilds the thing under test in a private helper, so the
        change is unexercised. Stated as a fixture and NOT as a commit by necessity - that
        state was never committed, it lived between 788e0c3f and its repair at 20de1d1c, and
        the mutation ledger it would otherwise be read from lives in gitignored
        `sdlc-studio/.local/`. A criterion claiming to pin a commit that does not hold the
        defect is a fabricated regression case, which is the class this check exists to
        refuse."""
        repo = self._repo(_ac(1, "pytest tests/test_prod.py::test_marker_is_present"),
                          "scripts/prod.py, tests/test_prod.py",
                          test_body=_REBUILT_TEST)
        code, out = self._run(repo)
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)
        self.assertIn("AC1", out)

    def test_a_verifier_that_reaches_production_goes_red(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, skip the revert loop and run the verifiers
        against the intact tree.

        The control for the fixture above, and the reason the pair is worth having: the SAME
        pytest runner, the same node shape, one test importing the production module and one
        rebuilding it locally. Without this, `test_the_unexercised_change_fixture_is_refused`
        could be passing because pytest never ran at all."""
        repo = self._repo(_ac(1, "pytest tests/test_prod.py::test_marker_reaches_production"),
                          "scripts/prod.py, tests/test_prod.py",
                          test_body=_REACHING_TEST)
        code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertIn("PASSES", out)

    def test_an_unresolvable_selector_is_unresolved_not_red(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, delete the `selector_resolves(...) is False`
        arm so an unresolvable selector is executed and its non-zero exit counted as red.

        A selector failing because it names nothing is not a test reaching the change. Counted
        as red it would manufacture a false PASS - the unit would look measured while nothing
        had been measured at all."""
        repo = self._repo(_ac(1, "pytest tests/test_absent.py::Missing::test_nope")
                          + _ac(2, "grep BASE_ONLY scripts/prod.py"),
                          "scripts/prod.py")
        code, out = self._run(repo)
        self.assertRegex(out, r"AC1\s+unresolved", out)
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)
        self.assertNotIn("AC1,", out.split("stayed GREEN")[1])

    def test_the_tree_is_byte_identical_after_a_normal_run(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, delete the snapshot-restore loop.

        Compared by per-file hash taken before and after, over every tracked and untracked
        file outside `.git`, rather than by reading `git status`: a restore that rewrote a
        file with different bytes and then staged them would satisfy `git status` and fail
        this."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"), "scripts/prod.py")
        before = repo.hashes()
        code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertEqual(before, repo.hashes())

    def test_the_tree_is_byte_identical_after_an_interrupted_run(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, move the restore out of the `finally` onto the
        success path.

        A check that dies must not be able to leave a unit's production change reverted on
        disk. The interruption is the verifier run raising, which is where a real one happens -
        a timeout, a killed runner, a keyboard interrupt."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"), "scripts/prod.py")
        before = repo.hashes()

        def boom(*_a, **_k):
            raise RuntimeError("interrupted")

        with unittest.mock.patch.object(verify_ac, "run_verifier", boom):
            with self.assertRaises(RuntimeError):
                self._run(repo)
        self.assertEqual(before, repo.hashes())

    def test_a_sigterm_mid_check_still_restores_the_tree(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, drop the `_guard_signals(restore)` call.

        A `finally` covers an exception and nothing else. An independent review measured the
        gap by signalling a live check: SIGINT restored - Python raises `KeyboardInterrupt`, so
        the `finally` ran - while **SIGTERM left the production change reverted on disk**. And
        SIGTERM is what `kill`, a CI job timeout and a harness cancel all send.

        Driven as a real subprocess receiving a real signal, because the defect is precisely
        that the in-process path already worked: `test_..._after_an_interrupted_run` patches
        `run_verifier` to raise and passes with the guard removed."""
        repo = self._repo(_ac(1, "shell sleep 30"), "scripts/prod.py")
        before = repo.hashes()
        script = (
            "import sys, os\n"
            f"sys.path.insert(0, {str(SCRIPT_PATH.parent)!r})\n"
            "import importlib.util\n"
            f"spec = importlib.util.spec_from_file_location('verify_ac', {str(SCRIPT_PATH)!r})\n"
            "m = importlib.util.module_from_spec(spec); sys.modules['verify_ac'] = m\n"
            "spec.loader.exec_module(m)\n"
            "print('go', flush=True)\n"
            f"m.main(['revert-check', '--unit', {repo.uid!r}, '--root', {str(repo.tmp)!r},"
            f" '--base', {repo.base!r}])\n")
        proc = subprocess.Popen([sys.executable, "-c", script],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        try:
            self.assertEqual("go\n", proc.stdout.readline(),
                             "the child never reached the check")
            # The verifier is a 30s sleep, so the revert is live on disk right now.
            deadline = time.time() + 10
            reverted = False
            while time.time() < deadline:
                if b"SHIPPED_MARKER" not in repo.prod.read_bytes():
                    reverted = True
                    break
                time.sleep(0.05)
            self.assertTrue(reverted, "the revert never became visible, so the signal below "
                                      "would prove nothing about restoring it")
            proc.send_signal(signal.SIGTERM)
            proc.wait(timeout=30)
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait(timeout=10)
        self.assertEqual(before, repo.hashes(),
                         "SIGTERM left the unit's production change reverted on disk")

    def test_uncommitted_edits_survive_the_check(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, restore from git - `git checkout HEAD --
        <path>` - instead of from the byte snapshot.

        The first build of this did exactly that and destroyed uncommitted work, including the
        fix it had just been used to validate. The edit here is uncommitted and is NOT at HEAD,
        so a git-sourced restore silently drops it while leaving the tree clean."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"), "scripts/prod.py")
        repo.prod.write_text(_PROD_HEAD + "UNCOMMITTED = 3\n", encoding="utf-8")
        before = repo.prod.read_bytes()
        code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertEqual(repo.prod.read_bytes(), before)
        self.assertIn("UNCOMMITTED", repo.prod.read_text(encoding="utf-8"))

    def test_a_file_absent_at_base_keeps_its_mode_through_the_check(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, drop the `os.chmod(target, mode_)` from the
        restore.

        A file added by the change does not exist at the base ref, so the revert UNLINKS it and
        the restore recreates it with `write_bytes` - at the process umask. An independent
        review measured a tracked `100755` script coming back `100644` after a SUCCESSFUL run,
        content hash identical, `git status` dirty. Every executable file in this repository is
        a script named in some unit's `Affects`, and this repository's own `repo-writes` lane
        refuses a commit whose run modified a tracked file - so the check would have broken the
        commit it was meant to inform."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"),
                          "scripts/prod.py, scripts/new_tool.py")
        added = repo.tmp / "scripts" / "new_tool.py"
        added.write_text("# added by this change\n", encoding="utf-8")
        added.chmod(0o755)
        before = repo.hashes()
        code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertEqual(before, repo.hashes())
        self.assertEqual(0o755, stat.S_IMODE(added.lstat().st_mode),
                         "the file came back at the umask default, not the mode it had")

    def test_a_symlink_in_affects_is_reported_rather_than_reverted(self) -> None:
        """MUTANT: in `verify_ac._revertible`, drop the `path.is_symlink()` arm.

        `is_file()` FOLLOWS a symlink, so the link was classified production, unlinked, and
        recreated as a regular file holding its target's bytes - `git status` reporting a type
        change, at exit 0. Where the link existed at base, `write_bytes` wrote THROUGH it and
        reverted the target instead of the declared path: a wrong measurement, taken in
        silence. Neither is a revert of what the unit declared."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"),
                          "scripts/prod.py, scripts/link.py")
        (repo.tmp / "scripts" / "link.py").symlink_to("prod.py")
        before = repo.hashes()
        code, out = self._run(repo)
        self.assertEqual(code, 3, out)
        self.assertIn("scripts/link.py", out)
        self.assertEqual(before, repo.hashes())
        self.assertTrue((repo.tmp / "scripts" / "link.py").is_symlink(),
                        "the symlink was replaced by a regular file")

    def test_a_path_outside_the_repo_root_is_reported_and_never_touched(self) -> None:
        """MUTANT: in `verify_ac._revertible`, drop the `is_absolute()` / `is_relative_to`
        arm.

        `(root / rel)` resolves `..` segments, and an ABSOLUTE `rel` replaces the root
        outright, so `../victim/secret.py` and `/tmp/…/victim.py` both looked like ordinary
        production files. `git show <ref>:<path>` then failed, the file was read as absent at
        base and DELETED, and it came back at the process umask - a `0o600` private file
        returned group- and world-readable, with the unit reported as PASSING. `revert_targets`
        promised this defence in its own docstring and the code did not have it."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"), "scripts/prod.py")
        victim = repo.tmp.parent / f"victim-{repo.tmp.name}.py"
        victim.write_text("SECRET = 1\n", encoding="utf-8")
        victim.chmod(0o600)
        try:
            text = repo.unit.read_text(encoding="utf-8")
            repo.unit.write_text(
                text.replace("> **Affects:** scripts/prod.py",
                             f"> **Affects:** scripts/prod.py, {victim}"), encoding="utf-8")
            code, out = self._run(repo)
            self.assertEqual(code, 3, out)
            # THE REASON, not just the exit code. Removing this arm alone still reported the
            # unit - `git ls-tree` fails on an absolute path, so the git-failure guard caught
            # it one step later and the mutant SURVIVED a test that only checked exit 3. A
            # repair masking the defect beside it is invisible unless the report is read.
            self.assertIn("not a readable file here", out,
                          "the path was reported as a GIT failure rather than refused as "
                          "outside the repository, so this passes with the guard removed")
            self.assertNotIn("could not read", out)
            self.assertTrue(victim.exists(), "a file OUTSIDE the repository was deleted")
            self.assertEqual("SECRET = 1\n", victim.read_text(encoding="utf-8"))
            self.assertEqual(0o600, stat.S_IMODE(victim.lstat().st_mode),
                             "a private file outside the repository came back world-readable")
        finally:
            victim.unlink(missing_ok=True)

    def test_a_git_failure_is_reported_rather_than_read_as_absent_at_base(self) -> None:
        """MUTANT: in `verify_ac._base_blob`, return None on any non-zero git exit instead of
        asking `ls-tree` whether the path exists at that ref.

        Absent-at-base and could-not-ask are different answers, and reading the second as the
        first DELETES the production file - which manufactures exactly the red this gate looks
        for, then reports the unit as passing. Reached in practice by a workspace nested below
        the repository root, where `git show` exits 128 saying the path exists but not under
        that name, and by a `git show` timeout."""
        repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py"), "scripts/prod.py")
        before = repo.hashes()
        with unittest.mock.patch.object(
                verify_ac, "_base_blob",
                side_effect=verify_ac._BaseUnreadable("fatal: path exists, but not in HEAD")):
            code, out = self._run(repo)
        self.assertEqual(code, 3, out)
        self.assertIn("could not read", out)
        self.assertEqual(before, repo.hashes(),
                         "the production file was disturbed after git could not be asked")

    def test_a_verifier_that_never_ran_is_not_counted_as_evidence(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, classify every non-ok result as `red`.

        `run_verifier` already distinguishes an expression it could not parse (`invalid`), one
        the trust boundary refused to run (`blocked`), and a runner that exited clean having
        run nothing (`vacuous`). None of those is a test noticing the change. Counted red, a
        unit whose `Verify:` line is a typo PASSES the one check that asks whether its tests
        reach anything - the same false pass AC5 states the rule against, one kind over."""
        repo = self._repo(_ac(1, "definitely-not-a-runner tests/x.py")
                          + _ac(2, "grep BASE_ONLY scripts/prod.py"),
                          "scripts/prod.py")
        code, out = self._run(repo)
        self.assertRegex(out, r"AC1\s+unmeasured", out)
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)

    def test_an_unnameable_row_beside_a_nameable_one_does_not_exempt(self) -> None:
        """MUTANT: in `verify_ac.revert_exemptions`, exempt on ANY well-formed `unnameable`
        row rather than requiring every row on that criterion to be one.

        The marker's whole design is that it costs something to enter. A second row on the same
        criterion naming a perfectly ordinary production change cost nothing and covered the
        first, so the criterion went unmeasured while the plan showed a nameable mutant for
        it."""
        plan = ("\n## Test Plan\n\n"
                "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                "| AC1 | unnameable: the criterion pins an ordering no single edit can "
                "reverse without also deleting the field it orders | a |\n"
                "| AC1 | in `scripts/prod.py`, drop the shipped marker | b |\n")
        repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py"), "scripts/prod.py",
                          extra_sections=plan)
        code, out = self._run(repo)
        self.assertNotRegex(out, r"AC1\s+exempt", out)
        self.assertEqual(code, 1, out)
        self.assertIn("stayed GREEN", out)

    def test_a_plan_row_naming_a_bare_production_filename_does_not_exempt(self) -> None:
        """MUTANT: in `verify_ac._MUTANT_PATH_RE`, require a `/` in a path token again.

        272 of the 459 plan rows in this corpus name their file by BARE FILENAME - "in
        `verify_ac.py`, delete the ..." - so a `/`-requiring pattern could not see the
        production file at all. A row naming a production file beside a test path then read as
        test-code-only and silently exempted the criterion, which is the taxonomy's escape
        hatch swallowing the corpus's own house style."""
        plan = ("\n## Test Plan\n\n"
                "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                "| AC1 | in `prod.py`, drop the shipped marker so "
                "`tests/test_prod.py::test_x` fails | a |\n")
        repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py"), "scripts/prod.py",
                          extra_sections=plan)
        code, out = self._run(repo)
        self.assertNotRegex(out, r"AC1\s+exempt", out)
        self.assertEqual(code, 1, out)

    def test_a_plan_row_naming_a_non_source_production_file_does_not_exempt(self) -> None:
        """MUTANT: in `verify_ac._MUTANT_PATH_RE`, drop the `/`-carrying arm and match only the
        bare-filename extension allowlist, so a path whose extension is not a source-code one
        is invisible to the exemption.

        The FIRST repair widened this pattern on the bare-filename axis and left the extension
        allowlist at the source-code families, so a row naming `config/settings.yaml` beside a
        test path still read as test-code-only. `revert_targets` classified the same yaml as
        production and reverted it, so two readers of one artefact disagreed about what
        production is - which `is_test_path`'s own docstring says it was collapsed to fix. Live
        rather than latent: over this corpus the widened pattern changes exactly one verdict,
        BG0560 AC1, whose row names `docs/existing-users.md` beside a test file and which was
        being exempted on that basis.

        An enumerated list silently exempts whatever it forgot (LL0013), so the arm that closes
        this is the one that needs NO list: a token carrying a `/` is a path whatever it ends
        in. The allowlist survives only for bare filenames, where nothing else separates
        `settings.yaml` from prose."""
        ARMS = {
            # BARE filename, allowlisted extension: only the allowlist arm can see this, so
            # narrowing the allowlist back to the source-code families kills the test.
            "the bare-filename allowlist": "in `settings.yaml`, drop the flag so ",
            # A `/`-carrying path whose extension is in NO allowlist: only the path arm can see
            # this, so deleting that arm kills the test. Two separate tests because each arm
            # alone covered a single yaml-with-directory fixture, so neither was pinned and
            # BOTH mutants survived the first cut of this test.
            "the slash-carrying path arm": "in `config/values.jsonnet`, drop the flag so ",
        }
        for arm, cell in ARMS.items():
            with self.subTest(arm=arm):
                plan = ("\n## Test Plan\n\n"
                        "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                        f"| AC1 | {cell}`tests/test_prod.py::test_x` fails | a |\n")
                repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py"), "scripts/prod.py",
                                  extra_sections=plan)
                code, out = self._run(repo)
                self.assertNotRegex(out, r"AC1\s+exempt", f"{arm} did not see the production file: {out}")
                self.assertEqual(code, 1, out)

    def test_a_plan_row_naming_only_test_code_still_exempts(self) -> None:
        """The paired control for the widened pattern. Widening what counts as a path is only
        safe if the exemption still FIRES when every path named really is test code - a
        pattern that saw production everywhere would refuse correct work, and refusing correct
        work is how a gate gets switched off.

        DISCRIMINATION MATTERS HERE. An earlier cut asserted only that AC1 came back exempt,
        and an independent review proved that vacuous: a mutant which exempts EVERY criterion
        keeps AC1 exempt too, so the control passed with the taxonomy destroyed and the ledger
        recorded a kill that had not happened. The fixture now carries a SECOND criterion whose
        row names production, and the assertion is that the two are treated DIFFERENTLY - which
        no blanket-exemption mutant can satisfy."""
        plan = ("\n## Test Plan\n\n"
                "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                "| AC1 | in `tests/test_prod.py`, widen the assertion window in "
                "`tests/helpers/fixtures.py` | a |\n"
                "| AC2 | in `scripts/prod.py`, drop the shipped marker | b |\n")
        repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py")
                          + _ac(2, "grep SHIPPED_MARKER scripts/prod.py"),
                          "scripts/prod.py", extra_sections=plan)
        code, out = self._run(repo)
        self.assertRegex(out, r"AC1.*exempt", out)
        self.assertNotRegex(out, r"AC2\s+exempt",
                            f"a criterion whose row names PRODUCTION was exempted too, so the "
                            f"taxonomy is not discriminating: {out}")
        # AC2 is measurable and goes red, so the UNIT passes. A blanket-exemption mutant leaves
        # nothing measurable at all and the check exits 3 REPORTED, so the exit code moves too.
        self.assertEqual(code, 0, out)

    def test_an_inherited_git_dir_does_not_steer_the_revert(self) -> None:
        """MUTANT: in `verify_ac._base_blob`/`_ref_exists`, drop `env=_git_env()`.

        The registration in `tools/tests/test_skill_tests_env.py` holds the LIST equal to every
        other copy; it says nothing about the list being APPLIED, and an independent review
        removed both `env=` arguments with all 348 tests in scope still green. `git -C` does not
        override an inherited `GIT_DIR`, and git hooks export one - this repository's own hooks
        run this code. Here `GIT_DIR` points at a DIFFERENT repository whose base ref does not
        contain the path at all: unscrubbed, the check answers for that repository instead."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"), "scripts/prod.py")
        # A DECOY WITH DIFFERENT CONTENT. An identical fixture was tried first and could not
        # discriminate: same bytes, same fixed identity, same timestamp second, so both base
        # commits hashed to the same sha and the mis-steered read returned the right answer by
        # coincidence. The decoy's base must be something the real base is not.
        other = Path(tempfile.mkdtemp(prefix="revert_decoy_"))
        self.addCleanup(shutil.rmtree, other, True)
        (other / "scripts").mkdir(parents=True)
        (other / "scripts" / "prod.py").write_text(
            _PROD_HEAD + "DECOY = 1\n", encoding="utf-8")
        _git(other, "init", "-q")
        _git(other, "add", "-A")
        _git(other, "commit", "-qm", "decoy")
        before = repo.hashes()
        env = dict(os.environ)
        env["GIT_DIR"] = str(other / ".git")
        env["GIT_WORK_TREE"] = str(other)
        with unittest.mock.patch.dict(os.environ, env, clear=False):
            code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"AC1\s+red", out)
        self.assertEqual(before, repo.hashes())

    def test_the_revert_purges_cached_bytecode_for_every_file_it_touches(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, make `_purge_pyc` a no-op.

        CPython invalidates a `.pyc` on (source mtime, source size), so a same-length revert
        landing inside one timestamp granule reuses the ORIGINAL bytecode - a subprocess then
        imports the code that is no longer on disk and the criterion reads green over a tree
        that was reverted. This repository has recorded that false verdict twice, and an
        independent review found the purge here pinned by nothing at all.

        Asserted at the SURFACE the hazard lives on: a stale `.pyc` for a reverted module is
        gone by the time any verifier runs, and gone again afterwards."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"), "scripts/prod.py")
        cache = repo.tmp / "scripts" / "__pycache__"
        cache.mkdir()
        stale = cache / "prod.cpython-999.pyc"
        stale.write_bytes(b"stale bytecode for the un-reverted module\n")
        seen = {}

        real = verify_ac.run_verifier

        def spy(expr, timeout, cwd, **kw):
            seen["during"] = stale.exists()
            return real(expr, timeout, cwd, **kw)

        with unittest.mock.patch.object(verify_ac, "run_verifier", spy):
            code, out = self._run(repo)
        self.assertEqual(code, 0, out)
        self.assertFalse(seen.get("during", True),
                         "the stale .pyc was still on disk while the verifiers ran, so a "
                         "subprocess could import the un-reverted module")
        self.assertFalse(stale.exists(), "the stale .pyc survived the restore")

    def test_a_unit_with_no_production_file_is_reported_not_passed(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, drop the empty-`production` branch so the
        check falls through and returns `pass`.

        Nothing to revert is not evidence that the tests reach anything. An absence and a pass
        must not read the same, so this exits on its own code and names the condition."""
        repo = self._repo(_ac(1, "grep _rebuild tests/test_prod.py"),
                          "tests/test_prod.py, docs/notes.md", test_body=_REBUILT_TEST)
        code, out = self._run(repo)
        self.assertEqual(code, 3, out)
        self.assertIn("names no production file", out)

    def test_a_unit_whose_every_selector_is_dead_is_reported_not_passed(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, delete the `not counted and unresolved` branch
        so a unit with nothing measurable returns `pass`.

        Found by running the boundary lane over a real batch: a unit whose tests are not
        written yet came back GREEN from the one check that exists to ask whether its verifiers
        reach anything at all. It is the empty-`Affects` rule one step further in - an absence
        and a pass must not read the same - and it is distinguished from the all-EXEMPT case,
        which legitimately passes."""
        repo = self._repo(_ac(1, "pytest tests/test_absent.py::Missing::test_nope")
                          + _ac(2, "pytest tests/test_absent.py::Missing::test_also_nope"),
                          "scripts/prod.py")
        code, out = self._run(repo)
        self.assertEqual(code, 3, out)
        self.assertIn("2 unresolvable selector(s)", out)
        self.assertIn("REPORTED rather than passed", out)

    def test_a_wholly_exempt_unit_is_reported_and_not_refused(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, return `pass` when `counted` is empty and every
        criterion is exempt.

        This test asserted the MUTANT until an independent review executed the consequence:
        adding one self-authored line, `> **Revert-check-exempt:** AC1 AC2 AC3 AC4 AC5 - one
        reason covering the lot`, turned the gate off for a whole unit and printed PASSES. A
        declared exemption is a reason a criterion cannot be measured, never evidence that it
        was.

        REPORTED (exit 3) and not REFUSED (exit 1), which is the distinction AC3 turns on: its
        law is that a declared exemption must not REFUSE the unit, and saying that nothing
        could be measured is not a refusal."""
        plan = ("\n## Test Plan\n\n"
                "| Criterion | Mutant | Title |\n| --- | --- | --- |\n"
                "| AC1 | unnameable: the criterion pins an ordering no single edit can "
                "reverse without also deleting the field it orders | a |\n")
        repo = self._repo(_ac(1, "grep BASE_ONLY scripts/prod.py"), "scripts/prod.py",
                          extra_sections=plan)
        code, out = self._run(repo)
        self.assertEqual(code, 3, out)
        self.assertIn("nothing measurable", out)
        self.assertIn("1 exempt", out)
        self.assertNotIn("stayed GREEN", out)

    def test_an_unresolvable_affects_path_is_reported(self) -> None:
        """MUTANT: in `verify_ac.revert_check`, drop the `unresolvable` branch and revert the
        subset that does resolve.

        A partial revert tests a change nobody described: the unit is judged against a surface
        smaller than the one it declared, and the verdict reads the same either way."""
        repo = self._repo(_ac(1, "grep SHIPPED_MARKER scripts/prod.py"),
                          "scripts/prod.py, scripts/absent.py")
        code, out = self._run(repo)
        self.assertEqual(code, 3, out)
        self.assertIn("scripts/absent.py", out)
        self.assertIn("not a readable file here", out)


_DEPTH_UNIT = """\
# US9002: fixture

> **Status:** Draft
> **Verification depth:** functional (the author's judgement half, preserved verbatim)
> **Affects:** scripts/prod.py

## Acceptance Criteria

- [ ] **AC1** the first claim
  - **Verify:** pytest tests/test_prod.py::test_marker_is_present
- [ ] **AC2** the second claim
  - **Verify:** pytest tests/test_prod.py::test_marker_reaches_production
- [ ] **AC3** the third claim
  - **Verify:** pytest tests/test_prod.py::test_third

## Test Plan

| Criterion | Mutant | Title |
| --- | --- | --- |
| AC1 | in `scripts/prod.py`, drop the shipped marker | a |
| AC1 | in `scripts/prod.py`, return the base value from the marker | b |
| AC1 | in `scripts/prod.py`, widen the marker guard to always pass | c |
| AC1 | in `scripts/prod.py`, move the marker below its caller | d |
| AC2 | in `scripts/prod.py`, restore the base constant | e |
| AC2 | in `scripts/prod.py`, rename the constant | f |
| AC2 | in `scripts/prod.py`, drop the constant's export | g |
| AC2 | in `scripts/prod.py`, shadow the constant in the caller | h |
| AC3 | in `scripts/prod.py`, delete the third branch | i |
| AC3 | in `scripts/prod.py`, invert the third branch's test | j |
| AC3 | in `scripts/prod.py`, fall through the third branch | k |
| AC3 | in `scripts/prod.py`, swallow the third branch's error | l |
"""


class DerivedDepthTests(unittest.TestCase):
    """`verify_ac.py depth` - CR0548.

    `Verification depth` is the field a reviewer reads first to decide how hard to look, and an
    independent review found it making a false factual claim on five of six units in one batch.
    Every count here is read from the mutation ledger through `mutation.plan_execution`, so a
    figure the ledger does not hold cannot be rendered.
    """

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="derived_depth_"))
        (self.tmp / "scripts").mkdir()
        (self.tmp / "scripts" / "prod.py").write_text(_PROD_HEAD, encoding="utf-8")
        (self.tmp / "tests").mkdir()
        (self.tmp / "tests" / "test_prod.py").write_text(
            _REBUILT_TEST + "\n" + _REACHING_TEST.split("\n\n", 1)[1], encoding="utf-8")
        stories = self.tmp / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        self.unit = stories / "US9002-fixture.md"
        self.unit.write_text(_DEPTH_UNIT, encoding="utf-8")
        self.mutation = _load_mutation()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _register(self, criterion: str, verdict: str = "killed", row: int = 0) -> None:
        self.mutation.register_mutant(
            self.tmp, "scripts/prod.py",
            mutant=f"in `scripts/prod.py`, the change {criterion} row {row} pins",
            test=f"tests/test_prod.py::{criterion}", verdict=verdict,
            unit="US9002", criterion=criterion, row=row, line=2)

    def _depth(self, extra=()) -> tuple:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = verify_ac.main(["depth", "--unit", "US9002", "--root", str(self.tmp),
                                   *extra])
        return code, buf.getvalue()

    def test_every_count_is_read_from_the_ledger(self) -> None:
        """MUTANT: in `verify_ac.depth_facts`, read ANY of `criteria`, `rows`, `killed`,
        `survived` or `executed` from a different quantity than the ledger's own verdicts -
        e.g. `"executed": len(rows)` or `"criteria": len(rows)`.

        EVERY COUNT IS A DIFFERENT NUMBER, and that is the point of the fixture rather than a
        detail of it. This has now been got wrong TWICE. The first cut used 2 criteria, 2 plan
        rows and 2 executions, so all five figures were 2 and four survived being replaced with
        each other. The repair for that moved to 3 criteria, 4 rows and 3 executions - and an
        independent review measured THAT still degenerate: criteria equalled executed, and
        killed, survived, equivalent and not-run were all 1, so three swap mutants survived this
        very selector while the `killed: 99` positive control died on it.

        So the property is asserted here rather than asserted ABOUT: 3 criteria, 12 declared
        rows, 7 executed (1 killed, 2 survived, 4 ruled equivalent), 5 never run. The seven
        figures are 3, 12, 7, 1, 2, 4, 5 - PAIRWISE distinct, so no count can stand in for any
        other, and the test checks that pairwise-distinctness itself rather than trusting the
        author who chose the numbers.

        THE ARITHMETIC ALSO CLOSES: killed + survived + equivalent + not-run must equal the
        declared rows, which is the property a reader uses to audit the line at all."""
        self._register("AC1", "killed")
        for row in (0, 1):
            self._register("AC2", "survived", row=row)
        for criterion, row in (("AC2", 2), ("AC2", 3), ("AC3", 0), ("AC3", 1)):
            self.mutation.register_mutant(
                self.tmp, "scripts/prod.py",
                mutant=f"in `scripts/prod.py`, the equivalent change {criterion} row {row} pins",
                test="", verdict="equivalent",
                reason="the change is observationally equivalent",
                unit="US9002", criterion=criterion, row=row)
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        counts = {"criteria": 3, "plan rows": 12, "executed": 7, "killed": 1, "survived": 2,
                  "ruled equivalent": 4, "NOT RUN": 5}
        for label, value in counts.items():
            self.assertIn(f"{label} {value}", out, f"{label} {value} missing from: {out}")
        self.assertEqual(len(set(counts.values())), len(counts),
                         "the fixture's counts are not pairwise distinct, so one count can be "
                         "sourced from another undetected - the defect this fixture exists to "
                         "make impossible, twice repaired and twice still present")
        self.assertEqual(counts["killed"] + counts["survived"] + counts["ruled equivalent"]
                         + counts["NOT RUN"], counts["plan rows"], "the row arithmetic does not close")
        self.assertEqual(counts["killed"] + counts["survived"] + counts["ruled equivalent"],
                         counts["executed"], "executed is not the sum of the executed verdicts")
        import re as _re  # noqa: PLC0415 - local: only this assertion parses the rendered line
        for label, value in counts.items():
            found = _re.findall(rf"{_re.escape(label)} (\d+)", out)
            self.assertEqual([str(value)], found,
                             f"{label} rendered as {found}, expected exactly [{value!r}] - a "
                             f"count read from a different quantity than the ledger's own "
                             f"verdicts is the mutant this row exists to kill: {out}")

    def test_an_unexecuted_row_is_named_not_omitted(self) -> None:
        """MUTANT: in `verify_ac.render_depth`, drop the `NOT RUN` branch so an unexecuted row
        is silently absent.

        A derived field that can only report success is the defect this replaces. The row is
        named by criterion AND row index, because a criterion carrying two mutants can have one
        executed and one not."""
        self._register("AC1", "killed")
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("NOT RUN 11", out)
        for named in ("AC2 row 0", "AC2 row 1", "AC3 row 0"):
            self.assertIn(named, out, f"{named!r} not named among the unrun rows: {out}")

    def test_the_entry_point_split_is_derived_per_criterion(self) -> None:
        """MUTANT: in `verify_ac._entry_point_split`, return `through_cli = located`.

        CR0548's motivating defect was a PROSE claim of shipped-CLI coverage that did not
        exist, so deriving only the five mutation counts would leave it standing in the half no
        tool touches. AC2's test enters the lane through `subprocess`; AC1's rebuilds the value
        in a private helper and never leaves the process."""
        self._register("AC1")
        self._register("AC2")
        (self.tmp / "tests" / "test_prod.py").write_text(
            _REBUILT_TEST + "\n\nimport subprocess\n\n\n"
            "def test_marker_reaches_production():\n"
            "    subprocess.run(['true'], check=True)\n\n\n"
            "def test_third():\n"
            "    assert _rebuild() == 'SHIPPED_MARKER'\n", encoding="utf-8")
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("entry point 1 of 3 criteria through the shipped CLI, 2 in-process", out)

    def test_a_criterion_whose_node_cannot_be_isolated_is_undetermined(self) -> None:
        """MUTANT: in `verify_ac._entry_point_split`, fall back to `_enters_the_lane`'s
        whole-file read when the named node cannot be isolated.

        `_enters_the_lane` reads the WHOLE FILE when it cannot find the node, which is right
        for `lane_check` - per-unit and report-only - and wrong here, where the answer becomes a
        per-criterion COUNT presented as derived fact. Measured over this corpus, 185 of 311
        through-CLI counts came from that fallback rather than from the criterion's own test.
        CR0548 was raised on a claim of shipped-CLI coverage that did not exist, so deriving the
        same claim from a detector that never read the criterion's node would re-manufacture it
        with the authority of derivation. AC3 names the criterion's OWN node.

        Here AC3's node is absent from the file, and the file DOES contain a `subprocess.run`
        in an unrelated test - the exact shape that made the fallback over-claim."""
        self._register("AC1", "killed")
        (self.tmp / "tests" / "test_prod.py").write_text(
            _REBUILT_TEST + "\n\nimport subprocess\n\n\n"
            "def test_marker_reaches_production():\n"
            "    subprocess.run(['true'], check=True)\n", encoding="utf-8")
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("1 undetermined (the named node could not be isolated)", out)
        self.assertIn("entry point 1 of 3 criteria through the shipped CLI, 1 in-process", out)
        self.assertNotIn("2 of 3", out)

    def test_an_all_in_process_unit_reports_zero_cli_coverage(self) -> None:
        """MUTANT: in `verify_ac.render_depth`, emit the entry-point clause only when
        `through_cli` is non-zero.

        The paired control. A renderer that only ever reports coverage it FOUND cannot
        contradict a false claim of coverage, which is precisely the claim CR0548 was raised
        on. Neither test here leaves the process, and the field must say so."""
        self._register("AC1")
        self._register("AC2")
        (self.tmp / "tests" / "test_prod.py").write_text(
            _REBUILT_TEST + "\n\ndef test_marker_reaches_production():\n"
            "    assert _rebuild() == 'SHIPPED_MARKER'\n\n\n"
            "def test_third():\n"
            "    assert _rebuild() == 'SHIPPED_MARKER'\n", encoding="utf-8")
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("entry point 0 of 3 criteria through the shipped CLI, 3 in-process", out)

    def test_an_absent_ledger_is_reported_not_rendered_as_zero(self) -> None:
        """MUTANT: in `verify_ac.render_depth`, drop the `ledger_absent` branch so an empty
        ledger renders `executed 0; killed 0; survived 0`.

        Nought executed and nothing recorded are different facts, and a reader who cannot tell
        them apart cannot judge the unit - a row of noughts reads as a measurement that found
        nothing rather than as a measurement nobody took."""
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("EVIDENCE ABSENT", out)
        self.assertNotIn("killed 0", out)

    def test_a_tier_less_field_is_refused_rather_than_written(self) -> None:
        """MUTANT: in `verify_ac.write_depth`, delete the empty-value guard so the derived span
        is spliced into a field carrying no tier.

        `transition` reads the field's LEADING TOKEN as the tier. Splicing into an empty value
        leaves `[[derived:` in that position, so a field that named no tier starts parsing as
        one - the unparseable-but-honest state turned into a parseable false one, which is the
        direction this whole command exists to move away from."""
        self._register("AC1")
        text = self.unit.read_text(encoding="utf-8")
        self.unit.write_text(text.replace(
            "> **Verification depth:** functional (the author's judgement half, "
            "preserved verbatim)", "> **Verification depth:**"), encoding="utf-8")
        code, out = self._depth(["--write"])
        self.assertEqual(code, 1, out)
        self.assertIn("carries no tier", out)
        self.assertNotIn("[[derived:", self.unit.read_text(encoding="utf-8"))

    def test_an_unexecuted_plan_still_names_its_rows(self) -> None:
        """MUTANT: in `verify_ac.depth_facts`, set `ledger_absent` to `not executed` again.

        The regression an independent review found. `ledger_absent` meant "nothing executed",
        so a unit whose every declared row was registered-but-unrun rendered EVIDENCE ABSENT
        and NAMED NONE of them - the single configuration where a reviewer most needs those
        names is the one that hid them. A ledger entry exists here; nothing has run."""
        self._register("AC1", "killed")
        self.mutation.retract_mutant(
            self.tmp, "scripts/prod.py", "US9002", "AC1", 2,
            mutant="in `scripts/prod.py`, the change AC1 row 0 pins",
            verdict="killed",
            reason="withdrawn, so the row reads as declared but never executed")
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("NOT RUN 12", out)
        for named in ("AC1 row 0", "AC2 row 0", "AC2 row 1", "AC3 row 0"):
            self.assertIn(named, out, f"{named!r} not named among the unrun rows: {out}")
        # BOTH facts, in one line: the ledger holds nothing live for this unit AND four
        # declared rows were never executed. Naming the rows is what the mutant removes; the
        # absent-ledger clause beside them is correct and stays.
        self.assertIn("EVIDENCE ABSENT", out)
        self.assertIn("retracted 1", out)

    def test_a_ledger_holding_rows_no_plan_claims_is_reported(self) -> None:
        """MUTANT: in `verify_ac.depth_facts`, set `ledger_absent` from the PLAN join again -
        `not executed` - so a unit with no `## Test Plan` reads EVIDENCE ABSENT.

        A claim about the LEDGER derived from the absence of a PLAN. 484 of the 561 units
        carrying a depth field in this corpus have no test plan, so it was the majority case,
        and it hid registered SURVIVORS - the one thing the gate exists to surface."""
        self._register("AC1", "survived")
        text = self.unit.read_text(encoding="utf-8")
        self.unit.write_text(text.split("## Test Plan")[0], encoding="utf-8")
        code, out = self._depth()
        self.assertEqual(code, 0, out)
        self.assertIn("NO TEST PLAN", out)
        self.assertNotIn("EVIDENCE ABSENT", out)
        self.assertIn("1 SURVIVED", out)

    def test_writing_without_a_ledger_refuses_rather_than_erasing_the_counts(self) -> None:
        """MUTANT: in `verify_ac.write_depth`, delete the `ledger_absent and prior` guard.

        The ledger lives in gitignored `sdlc-studio/.local/`, so a fresh clone, a CI runner and
        every review worktree have none. Rewriting a recorded set of counts as EVIDENCE ABSENT
        there - at exit 0, in silence - destroys the evidence rather than reporting its absence.
        This command must never make a unit's record LESS true than it found it."""
        self._register("AC1", "killed")
        self.assertEqual(self._depth(["--write"])[0], 0)
        sealed = self.unit.read_text(encoding="utf-8")
        self.assertIn("killed 1", sealed)
        (self.tmp / "sdlc-studio" / ".local" / "mutation-runs.json").unlink()
        code, out = self._depth(["--write"])
        self.assertEqual(code, 1, out)
        self.assertIn("no mutation ledger", out)
        self.assertEqual(sealed, self.unit.read_text(encoding="utf-8"),
                         "the recorded counts were overwritten in a workspace with no ledger")

    def test_a_field_wrapping_onto_a_second_line_is_refused(self) -> None:
        """MUTANT: in `verify_ac.write_depth`, drop the continuation-line guard.

        `_DEPTH_LINE_RE` is line-anchored, so only the first line is rewritten and the
        continuation's hand-typed counts stand beside a derived span contradicting them. Five
        tracked units already carry a wrapped field, so this is a live shape rather than a
        hypothetical one."""
        self._register("AC1", "killed")
        text = self.unit.read_text(encoding="utf-8")
        self.unit.write_text(text.replace(
            "> **Verification depth:** functional (the author's judgement half, "
            "preserved verbatim)",
            "> **Verification depth:** functional (the judgement half,\n"
            "> continued: all 4 killed and 6 of 6 criteria driven through the shipped CLI)"),
            encoding="utf-8")
        before = self.unit.read_text(encoding="utf-8")
        code, out = self._depth(["--write"])
        self.assertEqual(code, 1, out)
        self.assertIn("WRAPS onto a second line", out)
        self.assertEqual(before, self.unit.read_text(encoding="utf-8"))

    def test_the_judgement_half_survives_regeneration_verbatim(self) -> None:
        """MUTANT: in `verify_ac.depth_field_value`, rebuild the whole value from the derived
        facts instead of splicing only the delimited span.

        The tier and the honest statement of what was deliberately not covered are the part no
        tool can supply. Regenerated TWICE, because a splice that appends rather than replaces
        is byte-stable on its first run and doubles on its second."""
        self._register("AC1")
        self._register("AC2")
        self.assertEqual(self._depth(["--write"])[0], 0)
        once = self.unit.read_text(encoding="utf-8")
        self.assertEqual(self._depth(["--write"])[0], 0)
        twice = self.unit.read_text(encoding="utf-8")
        self.assertEqual(once, twice)
        self.assertIn("(the author's judgement half, preserved verbatim)", twice)
        self.assertIn("**Verification depth:** functional [[derived:", twice)
        self.assertEqual(
            verify_ac.sdlc_md.extract_field(twice, "Verification depth").split()[0],
            "functional")

if __name__ == "__main__":
    unittest.main()
