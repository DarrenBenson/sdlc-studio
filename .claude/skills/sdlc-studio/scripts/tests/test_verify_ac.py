"""Unit tests for verify_ac.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the sibling helper
import workspace  # noqa: E402 - the shared "am I in the dev repo?" check

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "verify_ac.py"
_spec = importlib.util.spec_from_file_location("verify_ac", SCRIPT_PATH)
assert _spec and _spec.loader
verify_ac = importlib.util.module_from_spec(_spec)
sys.modules["verify_ac"] = verify_ac
_spec.loader.exec_module(verify_ac)
sdlc_md = verify_ac.sdlc_md  # shared parsing helpers, via the loaded module


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


if __name__ == "__main__":
    unittest.main()
