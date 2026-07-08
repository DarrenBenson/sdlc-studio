"""Unit tests for verify_ac.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "verify_ac.py"
_spec = importlib.util.spec_from_file_location("verify_ac", SCRIPT_PATH)
assert _spec and _spec.loader
verify_ac = importlib.util.module_from_spec(_spec)
sys.modules["verify_ac"] = verify_ac
_spec.loader.exec_module(verify_ac)
sdlc_md = verify_ac.sdlc_md  # shared parsing helpers, via the loaded module


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
        rc = verify_ac.main(
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
        rc = verify_ac.main(
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
        rc = verify_ac.main(
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
        rc = verify_ac.main(
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
        rc = verify_ac.main(
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
            rc = verify_ac.main(["run", "--story", str(story), "--repo-root", str(root),
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


if __name__ == "__main__":
    unittest.main()
