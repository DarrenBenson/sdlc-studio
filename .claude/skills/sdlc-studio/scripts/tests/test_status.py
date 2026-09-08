"""Unit tests for status.py.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import contextlib
import io
import shutil
import json
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
import gitutil  # noqa: E402

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "status.py"
_spec = importlib.util.spec_from_file_location("status", SCRIPT_PATH)
assert _spec and _spec.loader
status = importlib.util.module_from_spec(_spec)
sys.modules["status"] = status
_spec.loader.exec_module(status)

_INIT_PATH = Path(__file__).resolve().parent.parent / "init.py"
_ispec = importlib.util.spec_from_file_location("init", _INIT_PATH)
assert _ispec and _ispec.loader
init = importlib.util.module_from_spec(_ispec)
sys.modules["init"] = init
_ispec.loader.exec_module(init)


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


class OnboardingHintTests(unittest.TestCase):
    """US0443: while guided onboarding is in progress, the hint resumes it and names the next
    stage, taking precedence over the ordinary pipeline ladder - so the operator is walked to a
    first plan. A complete or absent onboarding falls through to the normal hint."""

    def test_hint_resumes_guided_onboarding_while_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root)  # every stage pending; first is `agents`
            hint = status.compute_hint(status.gather(root), root)
            self.assertEqual(hint["next_command"], "init guided")
            self.assertIn("agents", hint["reason"])

    def test_completed_or_absent_onboarding_falls_through(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # Absent: no onboarding state at all -> ordinary "no PRD" hint.
            self.assertIn("prd", status.compute_hint(status.gather(root), root)["next_command"])
            # Complete: every stage done/skipped -> the onboarding branch yields nothing.
            init.start_onboarding(root)
            for name in init.ONBOARDING_STAGES:
                init.set_stage(root, name, "done")
            self.assertIn("prd", status.compute_hint(status.gather(root), root)["next_command"])


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


class TeamOfferAdvisoryTests(unittest.TestCase):
    """The meet-your-team offer: PRD present + no seat cards -> one advisory line;
    an offer on status/hint, never a hint-ladder rung."""

    def test_offer_when_prd_and_no_seats(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            (root / "sdlc-studio" / "prd.md").write_text("# PRD\n", encoding="utf-8")
            self.assertIn("persona generate --team", status.team_offer_advisory(root))

    def test_silent_without_prd(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertIsNone(status.team_offer_advisory(Path(d)))

    def test_silent_once_a_seat_exists(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (root / "sdlc-studio" / "prd.md").write_text("# PRD\n", encoding="utf-8")
            (seats / "priya.md").write_text("<!-- role: qa -->\n# P\n", encoding="utf-8")
            self.assertIsNone(status.team_offer_advisory(root))


class WorkspaceAdvisoryTests(unittest.TestCase):
    """CR0150: status/hint surface uncommitted workspace artifact changes as a
    one-line advisory naming ids - informational, never blocking, no authorship
    guesses, silent without git."""

    def _repo(self, d: Path) -> Path:
        root = Path(d)
        cd = root / "sdlc-studio" / "change-requests"
        cd.mkdir(parents=True)
        (cd / "CR0001-a.md").write_text("# CR-0001: a\n\n> **Status:** Proposed\n",
                                        encoding="utf-8")
        gitutil.git(["init", "-q"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-qm", "base"], root)
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
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(Path(d))
            cd = root / "sdlc-studio" / "change-requests"
            gitutil.git(["mv", "sdlc-studio/change-requests/CR0001-a.md",
                         "sdlc-studio/change-requests/CR0002-b.md"], root)
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

def _artifact(root: Path, type_: str, prefix: str, num: int, st: str) -> None:
    import lib.sdlc_md as _m
    rel = _m.ARTIFACT_TYPES[type_][0]
    d = root / rel; d.mkdir(parents=True, exist_ok=True)
    (d / f"{prefix}{num:04d}-x.md").write_text(
        f"# {prefix}{num:04d}: x\n\n> **Status:** {st}\n", encoding="utf-8")


class BacklogTests(unittest.TestCase):
    def test_lists_only_non_terminal_grouped_by_type_and_status(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")            # terminal -> excluded
            _story(root, 2, "In Progress")     # non-terminal
            _story(root, 3, "Ready")           # non-terminal
            _artifact(root, "bug", "BG", 1, "Closed")   # terminal -> excluded
            _artifact(root, "bug", "BG", 2, "Open")     # non-terminal
            _artifact(root, "cr", "CR", 1, "Complete")  # terminal -> excluded
            _artifact(root, "cr", "CR", 2, "Proposed")  # non-terminal
            bl = status.backlog(root)
            self.assertEqual(bl["story"]["count"], 2)
            self.assertEqual(set(bl["story"]["by_status"]), {"In Progress", "Ready"})
            self.assertEqual(bl["bug"]["count"], 1)
            self.assertIn("Open", bl["bug"]["by_status"])
            self.assertEqual(bl["cr"]["count"], 1)
            self.assertIn("Proposed", bl["cr"]["by_status"])


class BacklogVocabTests(unittest.TestCase):
    def test_terminal_detection_is_vocab_driven_not_hardcoded(self) -> None:
        import lib.sdlc_md as _m
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # a LESS-common terminal status must still be excluded (proves the shared vocab
            # terminal set is used, not a hardcoded {Done, Closed} subset)
            _artifact(root, "cr", "CR", 1, "Superseded")     # terminal (vocab) -> excluded
            _artifact(root, "story", "US", 1, "Won't Implement")  # terminal (vocab) -> excluded
            _artifact(root, "story", "US", 2, "Blocked")     # non-terminal -> included
            self.assertTrue(_m.is_terminal_status("cr", "Superseded"))
            bl = status.backlog(root)
            self.assertEqual(bl["cr"]["count"], 0)
            self.assertEqual(bl["story"]["count"], 1)
            self.assertIn("Blocked", bl["story"]["by_status"])


class BacklogFormatTests(unittest.TestCase):
    def test_json_format_stable_and_type_filter(self) -> None:
        import io, json, contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "In Progress")
            _artifact(root, "cr", "CR", 1, "Proposed")
            import contextlib as _c, io as _io
            buf = _io.StringIO()
            with _c.redirect_stdout(buf):
                status.main(["backlog", "--root", str(root), "--format", "json", "--type", "cr"])
            j = json.loads(buf.getvalue())
            self.assertIn("cr", j)
            self.assertNotIn("story", j)          # --type cr restricts the output
            self.assertEqual(j["cr"]["count"], 1)

    def test_empty_backlog_prints_explicitly(self) -> None:
        import io, contextlib
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")               # only terminal artefacts
            import contextlib as _c, io as _io
            buf = _io.StringIO()
            with _c.redirect_stdout(buf):
                status.main(["backlog", "--root", str(root)])
            out = buf.getvalue().lower()
            self.assertIn("empty", out)           # explicit, not blank output


class HookWarningTests(unittest.TestCase):
    def setUp(self):
        import os
        self._env = {k: os.environ.get(k) for k in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM")}
        os.environ["GIT_CONFIG_GLOBAL"] = "/dev/null"
        os.environ["GIT_CONFIG_SYSTEM"] = "/dev/null"

    def tearDown(self):
        import os
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def test_pillars_surfaces_a_disabled_hook(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / ".githooks").mkdir()
            (root / ".githooks" / "pre-commit").write_text("#!/bin/sh\n", encoding="utf-8")
            gitutil.git(["init", "-q", str(root)], cwd=root)
            (root / "sdlc-studio").mkdir()
            buf = io.StringIO()
            with redirect_stdout(buf):
                status.main(["pillars", "--root", str(root)])
            self.assertIn("enable-hooks.sh", buf.getvalue())


class CloseOwedAdvisoryTests(unittest.TestCase):
    """The status/hint nudge (US0164): silent until a close is genuinely owed."""

    def _story(self, root: Path, sid: str, st: str) -> None:
        d = root / "sdlc-studio" / "stories"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{sid}-x.md").write_text(f"# {sid}\n\n> **Status:** {st}\n> **Points:** 2\n",
                                       encoding="utf-8")

    def test_nudges_to_baseline_when_unbaselined_with_terminal_units(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            self._story(root, "US0001", "Done")
            adv = status.close_owed_advisory(root)  # the prerequisite must not be invisible
            self.assertIsNotNone(adv)
            self.assertIn("baseline", adv)

    def test_silent_when_unbaselined_and_nothing_closed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            self._story(root, "US0001", "In Progress")  # nothing terminal to baseline yet
            self.assertIsNone(status.close_owed_advisory(root))

    def test_fires_when_a_close_is_owed(self) -> None:
        import close_owed
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            self._story(root, "US0001", "Done")
            close_owed.stamp_baseline(root, date="2026-01-01")
            self._story(root, "US0005", "Done")
            adv = status.close_owed_advisory(root)
            self.assertIsNotNone(adv)
            self.assertIn("US0005", adv)
            self.assertIn("close is owed", adv)

    def test_silent_when_all_owed_work_is_grandfathered(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            self._story(root, "US0001", "Done")
            import close_owed
            close_owed.stamp_baseline(root, date="2026-01-01")
            self.assertIsNone(status.close_owed_advisory(root))

    def test_surfaces_a_corrupt_baseline_and_directs_repair(self) -> None:
        # BG0155: a corrupt baseline must be surfaced loudly, never re-stamped away.
        import close_owed
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            self._story(root, "US0005", "Done")
            (root / close_owed.BASELINE_FILE).write_text('["US0005"]', encoding="utf-8")
            adv = status.close_owed_advisory(root)
            self.assertIsNotNone(adv)
            self.assertIn("CORRUPT", adv)
            self.assertIn("do", adv.lower())  # directs repair, not a re-stamp




class BacklogTriageAdvisoryTests(unittest.TestCase):
    """US0171: status surfaces a backlog-triage summary; silent on a coherent backlog."""

    def _bug(self, root: Path, num: int, title: str, summary: str, affects: str) -> None:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"BG{num:04d}-x.md").write_text(
            f"# BG{num:04d}: {title}\n\n> **Status:** Open\n> **Affects:** {affects}\n"
            f"> **Points:** 3\n> **Date:** 2026-07-16\n\n## Summary\n\n{summary}\n",
            encoding="utf-8")

    def test_fires_on_a_duplicate_pair(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, 1, "check_links misses an anchor link defect",
                      "check_links does not catch a broken anchor link defect", "tools/x.py")
            self._bug(root, 2, "anchor link defect not caught by check_links",
                      "a broken anchor link defect is not caught by check_links", "tools/x.py")
            adv = status.backlog_triage_advisory(root)
            self.assertIsNotNone(adv)
            self.assertIn("duplicate", adv)

    def test_silent_on_a_coherent_backlog(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, 1, "colour the output", "render green", "tools/a.py")
            self._bug(root, 2, "fix a crash", "divide by zero", "tools/b.py")
            self.assertIsNone(status.backlog_triage_advisory(root))


REPO = Path(__file__).resolve().parents[5]
_FORWARD_PORT = REPO / "tools" / "forward-port.sh"


def _dev_repo_with_check(root: Path) -> Path:
    """A tree carrying the repository's own drift check and a skill source of two files, so
    the advisory is measured against the REAL check rather than a stub that agrees with the
    parser by construction."""
    (root / "tools").mkdir(parents=True)
    import shutil
    shutil.copy(_FORWARD_PORT, root / "tools" / "forward-port.sh")
    skill = root / ".claude" / "skills" / "sdlc-studio"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    (skill / "scripts" / "a.py").write_text("x = 1\n", encoding="utf-8")
    return root


def _installed_copy(home: Path) -> Path:
    p = home / ".claude" / "skills" / "sdlc-studio"
    (p / "scripts").mkdir(parents=True)
    return p


class InstalledCopyDriftAdvisoryTests(unittest.TestCase):
    """The installed copy is what every other project on this machine loads, so a stale
    mirror is a fix believed shipped that is in force nowhere. The drift check reports it;
    this surfaces the report where an agent already looks."""

    def setUp(self) -> None:
        import shutil
        if shutil.which("rsync") is None:            # the check's comparison engine
            self.skipTest("rsync not on PATH")
        if not _FORWARD_PORT.is_file():
            self.skipTest("tools/forward-port.sh not present (consuming project)")

    def _drift(self, root: Path, home: str, **kw):
        """The verdict with HOME pointed at the fixture's installed copy - unpatched, the
        check would compare against the real one on this machine and the count would be
        whatever that happens to be."""
        import os
        with unittest.mock.patch.dict(os.environ, {"HOME": home}):
            return status.installed_copy_drift(root, **kw)

    def _run(self, cmd: str, root: Path, home: str) -> tuple[int, str, str]:
        import io
        import os
        from contextlib import redirect_stderr, redirect_stdout
        out, err = io.StringIO(), io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"HOME": home}):
            with redirect_stdout(out), redirect_stderr(err):
                rc = status.main([cmd, "--root", str(root)])
        return rc, out.getvalue(), err.getvalue()

    def _hint(self, root: Path, home: str) -> tuple[int, str, str]:
        return self._run("hint", root, home)

    def test_the_hint_names_the_differing_file_count(self) -> None:
        """AC1: the number of differing files, alongside the other advisories."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as h:
            root = _dev_repo_with_check(Path(d))
            target = _installed_copy(Path(h))
            # THREE files differ and no more: one changed, two extra at the target. The
            # matching `scripts/a.py` and the excluded caches are not drift.
            target.joinpath("SKILL.md").write_text("# stale skill\n", encoding="utf-8")
            target.joinpath("scripts", "a.py").write_text("x = 1\n", encoding="utf-8")
            target.joinpath("stale-one.md").write_text("old\n", encoding="utf-8")
            target.joinpath("stale-two.md").write_text("old\n", encoding="utf-8")

            drift = self._drift(root, h)
            self.assertEqual(drift["count"], 3, drift)

            for cmd, beside in (("hint", "/sdlc-studio "), ("pillars", "Requirements:")):
                rc, out, _err = self._run(cmd, root, h)
                self.assertEqual(rc, 0)
                advisory = [ln for ln in out.splitlines() if "installed copy" in ln]
                self.assertEqual(len(advisory), 1, out)
                self.assertIn("3 file(s)", advisory[0])
                self.assertIn("forward-port.sh --yes", advisory[0])  # the command that mirrors
                self.assertIn(beside, out)   # alongside the rest, never in place of it

    def test_a_project_without_the_check_is_silent_and_never_raises(self) -> None:
        """AC2: no check, no installed copy, a pinned copy, an erroring or slow check."""
        with tempfile.TemporaryDirectory() as h:
            with tempfile.TemporaryDirectory() as d:      # a consuming project: no check
                self.assertIsNone(self._drift(Path(d), h))
                # and nothing is EXECUTED on its behalf: the check's presence is what arms
                # this surface, so a project without one costs a stat and no process.
                import subprocess

                def never(*a, **kw):
                    raise AssertionError(f"a project with no drift check ran {a!r}")

                with unittest.mock.patch.object(subprocess, "run", never):
                    self.assertIsNone(self._drift(Path(d), h))
            with tempfile.TemporaryDirectory() as d:      # check present, nothing installed
                root = _dev_repo_with_check(Path(d))
                self.assertIsNone(self._drift(root, h))
                rc, out, _err = self._hint(root, h)       # HOME here holds no copy either
                self.assertEqual(rc, 0)
                self.assertNotIn("installed copy", out)
            with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as ph:
                root = _dev_repo_with_check(Path(d))      # a deliberately pinned copy
                target = _installed_copy(Path(ph))
                target.joinpath("SKILL.md").write_text("# stale skill\n", encoding="utf-8")
                (target / ".local").mkdir()
                (target / ".local" / "forward-port.pin").write_text("held\n", encoding="utf-8")
                self.assertIsNone(self._drift(root, ph))
            with tempfile.TemporaryDirectory() as d:      # a check that fails to answer
                root = Path(d)
                (root / "tools").mkdir()
                (root / "tools" / "forward-port.sh").write_text(
                    "#!/usr/bin/env bash\necho 'boom' >&2\nexit 2\n", encoding="utf-8")
                self.assertIsNone(self._drift(root, h))
                rc, out, _err = self._hint(root, h)
                self.assertEqual(rc, 0)
                self.assertNotIn("installed copy", out)
            with tempfile.TemporaryDirectory() as d:      # a check that never returns
                root = Path(d)
                (root / "tools").mkdir()
                (root / "tools" / "forward-port.sh").write_text(
                    "#!/usr/bin/env bash\nsleep 30\n", encoding="utf-8")
                self.assertIsNone(self._drift(root, h, timeout=0.5))


class BareInvocationTests(unittest.TestCase):
    """A bare `status.py` mirrors `/sdlc-studio status`, which every reader of this surface
    starts from. It exited 2 with an argparse usage error, costing a retry per session."""

    def _run(self, argv: list[str]) -> tuple[int, str, str]:
        import contextlib
        import io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = status.main(argv)
            except SystemExit as e:                      # argparse's usage exit
                rc = e.code if isinstance(e.code, int) else 1
        return rc, out.getvalue(), err.getvalue()

    def test_no_subcommand_prints_the_pillars_and_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            bare = self._run(["--root", str(root)])
            explicit = self._run(["pillars", "--root", str(root)])
            self.assertEqual(bare[0], 0, f"bare status exited {bare[0]}: {bare[2]}")
            # Byte-identical to the explicit verb: a default that prints something SIMILAR
            # is a second dashboard to keep in step with the first.
            self.assertEqual(bare[1], explicit[1])
            self.assertIn("Requirements:", bare[1])

    def test_the_bare_call_defaults_to_text_without_a_top_level_format_flag(self) -> None:
        """`--format` stays per-subcommand (the family grammar rule), so the default is
        supplied as a namespace default rather than a second top-level flag that the
        subparser's own default would overwrite on `status.py --format json pillars`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            self.assertEqual(status.build_parser().parse_args(["--root", str(root)]).format,
                             "text")
            self.assertNotIn(
                "--format",
                [o for a in status.build_parser()._actions for o in a.option_strings],
                "a top-level --format would be clobbered by the subparser default")

    def test_explicit_subcommands_are_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _story(root, 1, "Done")
            for verb in ("pillars", "hint", "backlog"):
                rc, out, _ = self._run([verb, "--root", str(root)])
                self.assertEqual(rc, 0, verb)
                self.assertTrue(out.strip(), verb)
            # A flag that belongs to one verb still reaches it, and --root after the verb
            # still wins - the two positions the global-root helper exists to keep working.
            rc, out, _ = self._run(["backlog", "--root", str(root), "--type", "story"])
            self.assertEqual(rc, 0)

    def test_an_unknown_verb_is_still_a_usage_error(self) -> None:
        # Defaulting must not swallow a typo: `status.py pillrs` printing the dashboard and
        # exiting 0 would be worse than the error this story removes.
        rc, _out, err = self._run(["pillrs"])
        self.assertNotEqual(rc, 0)
        self.assertIn("invalid choice", err)


class PointsCensusTests(unittest.TestCase):
    """"How many points are left" had no home in the tooling.

    `status` reported counts, `sprint breakdown` reported grooming state with no points at all,
    and only `sprint plan` summed them - a batch planner, not a backlog query. So the question
    got answered by a script written on the spot, and the first hand-written one silently
    counted a `Won't Implement` story.
    """

    def _root(self, d):
        root = Path(d)
        (root / "sdlc-studio" / "stories").mkdir(parents=True)
        (root / "sdlc-studio" / "bugs").mkdir(parents=True)
        (root / "sdlc-studio" / "stories" / "US0001-a.md").write_text(
            "# US0001: a\n\n> **Status:** Ready\n> **Points:** 5\n", encoding="utf-8")
        (root / "sdlc-studio" / "stories" / "US0002-b.md").write_text(
            "# US0002: b\n\n> **Status:** Review\n> **Points:** 3\n", encoding="utf-8")
        (root / "sdlc-studio" / "bugs" / "BG0001-c.md").write_text(
            "# BG0001: c\n\n> **Status:** Open\n> **Points:** 2\n", encoding="utf-8")
        return root

    def test_points_are_reported_by_status_and_type(self) -> None:
        """MUTANT: report counts instead of points, or collapse the buckets into a total.

        The buckets are the answer. A single total cannot say whether 300 points are Ready to
        plan or sitting at Review awaiting a sign-off, which are entirely different situations.
        """
        mod = status
        with tempfile.TemporaryDirectory() as d:
            census = mod.points_census(self._root(d))
        self.assertEqual(10, census["total"], "the total is not the sum of the points")
        self.assertEqual(8, census["by_type"]["story"])
        self.assertEqual(2, census["by_type"]["bug"])
        self.assertEqual(5, census["by_status"]["Ready"])
        self.assertEqual(3, census["by_status"]["Review"])

    def test_a_terminal_unit_is_excluded(self) -> None:
        """MUTANT: count every unit regardless of status.

        The hand-written census this replaces counted a `Won't Implement` story on its first
        pass, which is precisely the error a shared authority prevents.
        """
        mod = status
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            (root / "sdlc-studio" / "stories" / "US0003-d.md").write_text(
                "# US0003: d\n\n> **Status:** Won't Implement\n> **Points:** 8\n",
                encoding="utf-8")
            (root / "sdlc-studio" / "stories" / "US0004-e.md").write_text(
                "# US0004: e\n\n> **Status:** Done\n> **Points:** 13\n", encoding="utf-8")
            census = mod.points_census(root)
        self.assertEqual(10, census["total"],
                         "a terminal unit was counted as outstanding backlog")

    def test_the_census_is_reachable_through_its_command(self) -> None:
        """MUTANT: break the `points` subcommand wiring.

        A census only importable from Python does not answer the question anybody actually
        asks, which is the whole complaint this unit exists to fix.
        """
        mod = status
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            import contextlib as _c, io as _io
            buf = _io.StringIO()
            with _c.redirect_stdout(buf):
                rc = mod.main(["points", "--root", str(root)])
        self.assertEqual(0, rc)
        self.assertIn("10", buf.getvalue(), "the command printed no total")


class OpenRunLineTests(unittest.TestCase):
    """US0467. AGENTS.md makes `/sdlc-studio status` step two of every session including after a
    context reset, and it answered nothing about the run the reader was standing in.

    MUTANTS:
      1. render the rung from `sprint_goal` instead of `goal` -> AC1 reddens.
      2. count remaining locally instead of asking `handoff.build` -> AC2 reddens.
      3. return None for an unreadable run state -> AC4 reddens (it reports "no run open",
         which is a different fact and orphans the run it failed to read).
    """

    def _root(self, d, state=None, *, raw=None):
        root = Path(d)
        (root / "sdlc-studio" / ".local").mkdir(parents=True)
        if raw is not None:
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(raw, encoding="utf-8")
        elif state is not None:
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                json.dumps(state), encoding="utf-8")
        return root

    def test_run_line_names_id_rung_sprint_goal_batch_and_remaining(self) -> None:
        for goal, expect_rung in ((None, "unset"), ("design", "design")):
            with self.subTest(goal=goal), tempfile.TemporaryDirectory() as d:
                root = self._root(d, {"run_id": "RUN-T1", "outcome": "running", "goal": goal,
                                      "sprint_goal": "a full sentence of intent",
                                      "batch": ["BG0001", "BG0002"]})
                run = status.open_run(root)
                self.assertEqual(run["run_id"], "RUN-T1")
                self.assertEqual(run["rung"], expect_rung)
                self.assertEqual(run["sprint_goal"], "a full sentence of intent")
                self.assertEqual(run["batch"], 2)
                line = status.render_run_line(run)
                self.assertIn("RUN-T1", line)
                self.assertIn(f"rung={expect_rung}", line)
                self.assertIn('sprint-goal="a full sentence of intent"', line)
                self.assertNotIn("rung=a full sentence", line)
                self.assertIn("batch=2", line)
                self.assertIn("remaining=", line)

    def test_remaining_matches_handoff_over_done_wont_implement_open_and_batch_dropped(self) -> None:
        import handoff
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / "bugs").mkdir(parents=True)
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Done\n", encoding="utf-8")
            (root / "sdlc-studio" / "bugs" / "BG0001-x.md").write_text(
                "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Low\n", encoding="utf-8")
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                json.dumps({"run_id": "RUN-T2", "outcome": "running", "goal": "done",
                            "sprint_goal": "g", "batch": ["US0001", "BG0001"]}),
                encoding="utf-8")
            run = status.open_run(root)
            self.assertEqual(run["remaining"], handoff.build(root)["summary"]["remaining"])
            self.assertEqual(run["remaining"], 1, "only the Open bug is remaining")

    def test_absence_of_a_run_is_stated_not_silent(self) -> None:
        with tempfile.TemporaryDirectory() as d:      # no run-state.json at all
            root = self._root(d)
            self.assertIsNone(status.open_run(root))
            self.assertIn("no run open", status.render_run_line(None))
            self.assertIn("run", status.gather(root))
            self.assertIsNone(status.gather(root)["run"], "the key must be explicitly null")
        with tempfile.TemporaryDirectory() as d:      # a CLOSED run, batch still populated
            root = self._root(d, {"run_id": "RUN-OLD", "outcome": "goal-reached",
                                  "ended_at": "2026-01-01", "batch": ["BG0001"], "goal": "done"})
            self.assertIsNone(status.open_run(root))
            self.assertNotIn("RUN-OLD", status.render_run_line(status.open_run(root)))

    def test_unreadable_run_state_is_named_not_reported_as_no_run(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, raw="{ this is not json")
            run = status.open_run(root)
            self.assertIsNotNone(run, "an unreadable state is not the same as no run")
            self.assertTrue(run["unreadable"])
            line = status.render_run_line(run)
            self.assertIn("UNREADABLE", line)
            self.assertNotIn("no run open", line)
            self.assertIn("run-state.json", line)


    def test_a_structurally_malformed_run_state_is_named_not_fatal(self) -> None:
        """The blocking finding from the batch review, pinned. `run_state.read` guarantees the
        file parsed and is an object; it guarantees NOTHING about the shape inside. A `batch`
        that is not a list, or an `outcome` that is not a string, raised straight out of
        `open_run` into `gather` and took the whole four-pillar dashboard - and `hint` - down
        with it. That is the command AGENTS.md makes step two of every session, and US0467's
        own reason for existing.

        A fourth state, where the docstring insisted there were three.

        MUTANT: restore any unguarded field read, e.g. `len(raw.get("batch") or [])`. Each of
        these subtests must redden."""
        import contextlib
        import io
        for label, state in (("batch is not sized", {"outcome": "running", "run_id": "R1", "batch": 5}),
                             ("outcome is not a string", {"outcome": 5, "run_id": "R1", "batch": []}),
                             ("sprint_goal is not a string",
                              {"outcome": "running", "run_id": "R1", "batch": [], "sprint_goal": 5})):
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                root = self._root(d, state)
                run = status.open_run(root)                      # must not raise
                status.render_run_line(run)                      # nor must the renderer
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = status.main(["pillars", "--root", str(root)])
                self.assertEqual(rc, 0, f"the dashboard died on a malformed run state: {label}")
                self.assertIn("Requirements:", buf.getvalue(),
                              "the four-pillar census was lost to a malformed run state")

    def test_open_run_uses_the_shared_reader_not_a_second_one(self) -> None:
        """The contributing cause. `open_run` hand-rolled its own path construction and its own
        parse contract, duplicating `run_state.read` - which already implements exactly these
        states with a typed error. A path change in `run_state` would have made the dashboard
        report "no run open" forever, silently. This is the shape BG0501 repaired elsewhere in
        the same batch, so shipping it here would have been the sprint contradicting itself.

        MUTANT: reintroduce a literal `sdlc-studio/.local/run-state.json` path in `open_run`."""
        src = (Path(__file__).resolve().parents[1] / "status.py").read_text(encoding="utf-8")
        body = src.split("def open_run(", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("run_state.read", body,
                      "open_run must read through the shared reader")
        self.assertNotIn('"run-state.json"', body,
                         "open_run hand-rolls the run-state path - that is a second reader")

    def test_the_run_line_reaches_the_SHIPPED_ENTRY_POINT_not_only_the_library(self) -> None:
        """The wiring is the part a library test does not exercise. `open_run` and
        `render_run_line` can both be perfect while `main()` never calls them - four mechanisms
        shipped that way in one sprint here. This drives `status.main` itself, in both formats.

        MUTANT: remove the `render_run_line(data["run"])` call from `cmd_pillars`, or the
        `"run"` key from `gather` - this test must redden while every other test in the class
        still passes."""
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d, {"run_id": "RUN-CLI", "outcome": "running", "goal": "design",
                                  "sprint_goal": "a goal the CLI must print",
                                  "batch": ["BG0001"]})
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = status.main(["pillars", "--root", str(root)])
            out = buf.getvalue()
            self.assertEqual(rc, 0, out)
            self.assertIn("RUN-CLI", out, "the CLI never printed the run line")
            self.assertIn("rung=design", out)
            self.assertIn('sprint-goal="a goal the CLI must print"', out)
            self.assertTrue(out.lstrip().startswith("Run:"),
                            f"the run line must come first, got: {out[:80]!r}")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = status.main(["pillars", "--root", str(root), "--format", "json"])
            self.assertEqual(rc, 0)
            payload = json.loads(buf.getvalue())
            self.assertEqual(payload["run"]["run_id"], "RUN-CLI")
            self.assertEqual(payload["run"]["rung"], "design")


class RunLineDocTests(unittest.TestCase):
    """US0467 AC5. The help page must document exactly the fields the run line emits, both
    ways, so a field added, renamed or dropped in code fails the test rather than the reader."""

    FIELDS = ("run_id", "rung", "sprint-goal", "batch", "remaining")

    def test_help_page_documents_emitted_fields_and_anchors_the_reanchor_instruction(self) -> None:
        page = (Path(__file__).resolve().parents[2] / "help" / "status.md").read_text(
            encoding="utf-8")
        for field in self.FIELDS:
            self.assertIn(field, page, f"help/status.md does not document `{field}`")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            (root / "sdlc-studio" / ".local" / "run-state.json").write_text(
                json.dumps({"run_id": "RUN-T", "outcome": "running", "goal": "done",
                            "sprint_goal": "g", "batch": []}), encoding="utf-8")
            run = status.open_run(root)
            line = status.render_run_line(run)
        # BOTH WAYS, against the JSON field set - the criterion's "carries them as fields, not
        # only a rendered line". Comparing names against the TEXT would pass on `run_id`, which
        # the line emits as a value under no label, so the check would not see a rename.
        emitted = {"sprint-goal" if k == "sprint_goal" else k
                   for k in run if k not in ("unreadable",)}
        self.assertEqual(emitted, set(self.FIELDS),
                         "the page documents a field the run record does not carry, or vice versa")
        for label in ("rung=", "sprint-goal=", "batch=", "remaining="):
            self.assertIn(label, line, f"the rendered line drops the `{label}` label")
        self.assertIn("agent-instructions.md#operating-doctrine", page,
                      "the page must land a reader on the re-anchor instruction")




class OnboardingHintFalsifiabilityTests(unittest.TestCase):
    """BG0615 - a marker that no state of the tree could dislodge.

    `_onboarding_hint` is asked FIRST and its answer returned whenever any stage is pending, and
    `first_incomplete` decided that from the marker's own `status` field alone. So a marker
    written once and abandoned outranked the entire pipeline ladder for ever. Measured in this
    repository: one written 2026-08-14 with all seven stages pending, in a project holding a PRD,
    a TRD, a TSD, personas and 218 epics, made `hint` answer `init guided` for twelve days.
    """

    def _marked(self, root: Path, *pending: str) -> None:
        (root / "sdlc-studio" / ".local").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".local" / "onboarding.json").write_text(json.dumps(
            {"path": "brownfield",
             "stages": [{"name": s, "status": "pending"} for s in pending]}), encoding="utf-8")

    def _output_for(self, root: Path, stage: str) -> None:
        """Create exactly what `init`'s own stage for `stage` produces."""
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        if stage == "agents":
            for name in ("AGENTS.md", "CLAUDE.md"):     # the stage writes BOTH
                (root / name).write_text(f"# {name}\n", encoding="utf-8")
        elif stage in ("prd", "trd", "tsd", "personas"):
            (root / "sdlc-studio" / f"{stage}.md").write_text(f"# {stage}\n", encoding="utf-8")
        elif stage == "decompose":
            for sub, name in (("epics", "EP0001-x.md"), ("stories", "US0001-x.md")):
                d = root / "sdlc-studio" / sub; d.mkdir(parents=True, exist_ok=True)
                (d / name).write_text(f"# {name}\n", encoding="utf-8")

    def test_a_stage_whose_output_exists_does_not_hold_the_hint(self) -> None:
        """MUTANT: in `init.py`, drop the `stage_output_exists` check from `first_incomplete`,
        deciding from the marker's `status` field alone.

        This is the whole defect: no state of the tree could dislodge the marker."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._marked(root, "agents", "prd")
            for s in ("agents", "prd"):
                self._output_for(root, s)
            self.assertIsNone(init.first_incomplete(
                json.loads((root / "sdlc-studio" / ".local" / "onboarding.json").read_text()),
                root), "a stage whose output is on disk is not incomplete")

    def test_a_genuinely_incomplete_stage_still_holds_the_hint(self) -> None:
        """The paired control. Making the marker falsifiable must not disable guided onboarding
        for the projects genuinely mid-way through it - a check that never fires is switched
        off, and this one exists to help a real greenfield project."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._marked(root, "agents", "prd")
            self._output_for(root, "agents")          # prd's output is NOT on disk
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "onboarding.json").read_text())
            self.assertEqual("prd", init.first_incomplete(state, root))

    def test_a_partly_complete_stage_still_holds_the_hint(self) -> None:
        """MUTANT: in `init.py`, test only `AGENTS.md` for the agents stage and only epics for
        decompose, rather than every file each stage writes.

        Making the marker falsifiable opened the opposite failure. `stage_agents` writes AGENTS.md
        AND CLAUDE.md; the ordinary brownfield repo has the first and not the second, so testing
        one declared the stage done and CLAUDE.md was never drafted. Same for `decompose`, which
        directs `epic` THEN `story`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._marked(root, "agents", "decompose")
            (root / "AGENTS.md").write_text("# agents\n", encoding="utf-8")   # no CLAUDE.md
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "onboarding.json").read_text())
            self.assertEqual("agents", init.first_incomplete(state, root),
                             "half of the agents stage's output declared the whole stage done")
            for name in ("AGENTS.md", "CLAUDE.md"):
                (root / name).write_text("# x\n", encoding="utf-8")
            eps = root / "sdlc-studio" / "epics"; eps.mkdir(parents=True, exist_ok=True)
            (eps / "EP0001-x.md").write_text("# EP0001: x\n", encoding="utf-8")  # no stories
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "onboarding.json").read_text())
            self.assertEqual("decompose", init.first_incomplete(state, root),
                             "epics without stories declared decompose done")

    def test_a_fully_superseded_marker_is_named_not_silently_skipped(self) -> None:
        """MUTANT: in `init.py`, return an empty list from `superseded_stages`.

        A stale file that is quietly stepped over is one nobody ever removes. This one sat for
        twelve days across a dozen sprint closes and nothing reported it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            # `plan` is deliberately NOT satisfiable from the tree - `sprint plan` writes the
            # run state and `.local/` is gitignored, so it stays pending until confirmed.
            stages = ("agents", "prd", "trd", "tsd", "personas", "decompose")
            self._marked(root, *stages)
            for s in stages:
                self._output_for(root, s)
            state = json.loads(
                (root / "sdlc-studio" / ".local" / "onboarding.json").read_text())
            self.assertEqual(list(stages), init.superseded_stages(root, state))
            # THROUGH THE SHIPPED CLI. All three criteria were verified in-process on the first
            # cut - the depth field said so, `entry point 0 of 3` - and a `{"next_command": None}`
            # return with no `reason` key then crashed `cmd_hint` with a KeyError on exactly this
            # input. The orientation command went from a wrong answer to a traceback, and only a
            # test that runs the command could see it.
            self.assertIsNone(init.first_incomplete(state, root),
                              "every stage's output exists, so none is incomplete")
            self.assertIsNotNone(status.superseded_marker_advisory(root),
                                 "a stale marker must be REPORTED, not silently skipped")

    def test_the_shipped_hint_command_survives_a_superseded_marker(self) -> None:
        """MUTANT: in `status.py`, return the supersession note from `_onboarding_hint` as a dict
        carrying no `reason` key, instead of leaving the ladder to answer.

        THROUGH THE SHIPPED COMMAND. All three of this unit's first criteria were verified
        in-process - the depth field said `entry point 0 of 3 criteria through the shipped CLI` -
        and a return with no `reason` key then crashed `cmd_hint` with a KeyError on exactly this
        input. The orientation command went from a wrong answer to a traceback, and every
        advisory below the first print went with it. Only a test that runs the command sees it."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            stages = ("agents", "prd", "trd", "tsd", "personas", "decompose")
            self._marked(root, *stages)
            for s in stages:
                self._output_for(root, s)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = status.main(["hint", "--root", str(root)])
            printed = out.getvalue()
            self.assertEqual(0, rc, f"hint exited {rc}: {err.getvalue().strip()[:120]}")
            self.assertNotIn("init guided", printed,
                             "a fully superseded marker must not hold the hint")
            self.assertIn("SUPERSEDED", printed,
                          "the stale marker must be named beside the ladder's answer")
            self.assertIn("onboarding.json", printed,
                          "the advisory must name the file, or nobody can act on it")


def _corpus_shaped_fixture(root: Path, *, epics: int = 190, discovery: int = 45, total: int = 2340,
                           run_units: int = 5) -> None:
    """A corpus in THIS repository's shape (BG0646): `total` artefacts across stories, bugs,
    epics, CRs and reviews, of which `epics` are terminal epics with children and NO retro
    covering them (so the close-owed advisory enters `_breakdown_child_ids` per epic), `discovery`
    open CRs, a run open over `run_units` of the bugs, and a close-owed history."""
    import json as _json  # noqa: PLC0415
    base = root / "sdlc-studio"
    for sub in ("stories", "bugs", "epics", "change-requests", "reviews", "retros", ".local", "retros/evidence"):
        (base / sub).mkdir(parents=True, exist_ok=True)
    (base / ".config.yaml").write_text("schema_version: 2\n", encoding="utf-8")
    n_ep = epics; n_cr = discovery; n_review = 26
    n_story = (total - n_ep - n_cr - n_review) * 2 // 3; n_bug = total - n_ep - n_cr - n_review - n_story
    for i in range(1, n_review + 1):
        (base / "reviews" / f"RV{i:04d}-fixture-review.md").write_text(
            f"# RV{i:04d}: fixture review {i}\n\n> **Status:** Closed\n\n## Summary\n\nfixture\n", encoding="utf-8")
    for i in range(1, n_ep + 1):
        (base / "epics" / f"EP{i:04d}-fixture-epic.md").write_text(
            f"# EP{i:04d}: fixture epic {i}\n\n> **Status:** Done\n> **Priority:** Medium\n\n## Summary\n\nfixture\n\n"
            f"## Story Breakdown\n\n- [x] US{i:04d}: child\n", encoding="utf-8")
    for i in range(1, n_story + 1):
        ep = ((i - 1) % n_ep) + 1
        (base / "stories" / f"US{i:04d}-fixture-story.md").write_text(
            f"# US{i:04d}: fixture story {i}\n\n> **Status:** {'Done' if i % 3 else 'Ready'}\n> **Epic:** EP{ep:04d}\n> **Points:** 1\n\n"
            f"## Acceptance Criteria\n\n- [x] **AC1** Given a, when b, then c\n  - **Verify:** manual - fixture\n", encoding="utf-8")
    for i in range(1, n_bug + 1):
        (base / "bugs" / f"BG{i:04d}-fixture-bug.md").write_text(
            f"# BG{i:04d}: fixture bug {i}\n\n> **Status:** {'Fixed' if i % 4 else 'Open'}\n> **Severity:** Medium\n> **Points:** 1\n> **Affects:** src/x.py\n\n"
            f"## Acceptance Criteria\n\n- [x] **AC1** Given a, when b, then c\n  - **Verify:** manual - fixture\n", encoding="utf-8")
    for i in range(1, n_cr + 1):
        (base / "change-requests" / f"CR{i:04d}-fixture-request.md").write_text(
            f"# CR{i:04d}: fixture request {i}\n\n> **Status:** Proposed\n> **Priority:** Medium\n> **Size:** S\n\n## Summary\n\nfixture\n", encoding="utf-8")
    hist = base / "retros" / "evidence" / "actuals-2026-01-01.jsonl"
    hist.write_text("".join(_json.dumps({"id": f"BG{i:04d}", "type": "bug", "project": "fx"}) + "\n" for i in range(1, 201)), encoding="utf-8")
    (base / "retros" / "VELOCITY.md").write_text("# Velocity\n\n| Sprint | Points | Tokens |\n| --- | --- | --- |\n| RETRO0001 | 10 | 1000 |\n", encoding="utf-8")
    # stamped, so `close_owed.owed` passes its unbaselined early return and READS the history
    (base / ".close-owed-baseline.json").write_text(_json.dumps({"grandfathered": [], "stamped": "2025-12-01"}), encoding="utf-8")
    # The run's batch exercises EVERY branch of handoff's predicate, so the run line's count is
    # a real join and not a number two copies of the rule agree on by luck: BG0001 Fixed with a
    # RED verify report (remaining, unproven), BG0002/BG0003 Fixed and proven (delivered),
    # BG0004 Open (remaining), BG0005 closed without delivery (dropped), BG9999 in the batch
    # with no file (remaining), and BG0008 quarantined by the loop OUTSIDE the batch (remaining).
    # remaining = 4 by hand: BG0001, BG0004, BG9999, BG0008.
    assert run_units == 5, "the branch layout below is written for a five-unit batch"
    (base / "bugs" / "BG0005-fixture-bug.md").write_text(
        "# BG0005: fixture bug 5\n\n> **Status:** Won't Fix\n> **Severity:** Medium\n> **Points:** 1\n> **Affects:** src/x.py\n\n"
        "## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c\n  - **Verify:** manual - fixture\n", encoding="utf-8")
    (base / ".local" / "verify-report.json").write_text(_json.dumps({"stories": {
        "BG0001-fixture-bug": {"passed": 0, "failed": 1, "stale": 0},
        "BG0002-fixture-bug": {"passed": 1, "failed": 0, "stale": 0},
        "BG0003-fixture-bug": {"passed": 1, "failed": 0, "stale": 0}}}), encoding="utf-8")
    (base / ".local" / "loop-state.json").write_text(_json.dumps({"units": {
        "BG0008": {"attempts": 2, "signatures": ["test_a::x", "test_a::x"]}}}), encoding="utf-8")
    (base / ".local" / "run-state.json").write_text(_json.dumps({
        "schema": "1", "run_id": "RUN-FIXTURE", "started_at": "2026-01-01T00:00:00Z", "ended_at": None,
        "outcome": "running", "goal": "done", "batch": [f"BG{i:04d}" for i in range(1, run_units + 1)] + ["BG9999"],
        "sprint_goal": "fixture", "base_ref": "0" * 40}), encoding="utf-8")


class GatherPerformanceTests(unittest.TestCase):
    """BG0646. MUTANTS (AC1): print the `Run:` headline only after the full gather returns; keep
    `children_of` walking the corpus on every call; print the advisories before the headline;
    print the headline without flushing; keep deriving the run line's remaining count through
    `handoff.build`. The bounds are the consumer's: a piped `status` shows its first line inside
    3 s and exits inside 15 s on a corpus this repository's shape."""

    def _fixture(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="status_perf_")); self.addCleanup(shutil.rmtree, d, True)
        _corpus_shaped_fixture(d)
        return d

    def test_the_shipped_command_answers_a_corpus_shaped_fixture_with_the_headline_first(self) -> None:
        import subprocess, time  # noqa: PLC0415
        root = self._fixture()
        t0 = time.monotonic()
        proc = subprocess.Popen([sys.executable, "-B", str(SCRIPT_PATH), "--root", str(root)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        first = proc.stdout.readline()
        t_first = time.monotonic() - t0
        out, err = proc.communicate(timeout=120)
        t_exit = time.monotonic() - t0
        self.assertEqual(0, proc.returncode, err)
        self.assertTrue(first.startswith("Run:"), f"the first line through the pipe is not the run line: {first!r}")
        self.assertIn("RUN-FIXTURE", first); self.assertIn("remaining=4)", first)
        self.assertLess(t_first, 3.0, f"the headline reached the pipe after {t_first:.1f}s")
        self.assertLess(t_exit, 15.0, f"the command took {t_exit:.1f}s over a corpus this repository's shape")
        lines = (first + out).splitlines()
        self.assertTrue(lines[0].startswith("Run:") and lines[1].startswith("Requirements:"), lines[:3])

    def test_the_headline_is_in_the_buffer_and_flushed_before_gather_is_entered(self) -> None:
        # the structural pin: a cached gather finishes inside any clock, so the ORDER is asserted
        # in-process - when `gather` is entered, stdout already holds the flushed `Run:` line
        root = self._fixture()
        mod = status
        seen = {}
        real_gather = mod.gather
        real_flush = sys.stdout.flush

        class _Out(io.StringIO):
            def flush(self_inner):
                seen["flushed_at"] = len(self_inner.getvalue()); super().flush()

        def spy_gather(r, **kw):
            seen["buffer_at_gather"] = out.getvalue(); seen["flushed_before_gather"] = seen.get("flushed_at")
            return real_gather(r, **kw)

        import handoff  # noqa: PLC0415 - the sibling the run line borrows its predicate from
        real_build = handoff.build

        def spy_build(*a, **k):
            seen["build_called"] = True
            return real_build(*a, **k)

        real_open_run = mod.open_run

        def spy_open_run(r):
            seen["open_run_calls"] = seen.get("open_run_calls", 0) + 1
            return real_open_run(r)

        out = _Out()
        with contextlib.redirect_stdout(out), unittest.mock.patch.object(mod, "gather", spy_gather), \
             unittest.mock.patch.object(handoff, "build", spy_build), \
             unittest.mock.patch.object(mod, "open_run", spy_open_run):
            rc = mod.main(["--root", str(root)])
        self.assertEqual(0, rc)
        # the run is read ONCE: the headline's read is handed to gather, never repeated inside it
        self.assertEqual(1, seen.get("open_run_calls"), "open_run ran more than once per invocation")
        # the remaining count comes from handoff's cheap predicate, never from `build` and its
        # conformance pass - 62 s on this repository with a run open, a cost the fixture cannot see
        self.assertNotIn("build_called", seen, "the run line's remaining count went through handoff.build")
        # and it is the SAME count `build` derives, over a batch that exercises every branch of
        # the predicate (delivered, red evidence, open, dropped, missing, quarantined outside the
        # batch - 4 remain by hand). Asserted on the CLOSED token: `remaining=1` is a prefix of
        # `remaining=10)`, and a count that grew a digit passed the first cut of this pin.
        self.assertEqual(4, real_build(root)["summary"]["remaining"], "the fixture's batch layout drifted")
        self.assertIn("remaining=4)", seen["buffer_at_gather"],
                      "the run line's remaining count is not the count handoff.build derives: " + seen["buffer_at_gather"][:120])
        self.assertIn("batch=6,", seen["buffer_at_gather"])
        self.assertTrue(seen.get("buffer_at_gather", "").startswith("Run:"),
                        "the run line was not in the buffer when gather was entered: " + repr(seen.get("buffer_at_gather", ""))[:80])
        self.assertIsNotNone(seen.get("flushed_before_gather"), "stdout was not flushed before gather was entered")
        self.assertGreater(seen["flushed_before_gather"], 0)


class HintPerformanceTests(unittest.TestCase):
    """BG0652. MUTANT (AC1): move `close_owed_advisory` and the other advisories in `cmd_hint`
    back outside the `corpus_cache()` sweep - today's code, measured at 22.9 s over the fixture
    against 0.7 s for the dashboard. The bound is the consumer's: `status hint` exits inside 15 s
    on a corpus this repository's shape; the identity pin is the structural half, so a faster
    machine cannot pass the wrong shape."""

    def _fixture(self) -> Path:
        d = Path(tempfile.mkdtemp(prefix="status_hint_perf_")); self.addCleanup(shutil.rmtree, d, True)
        _corpus_shaped_fixture(d)
        return d

    def test_the_hint_command_answers_the_corpus_shaped_fixture_inside_the_bound(self) -> None:
        import subprocess, time  # noqa: PLC0415
        from lib import sdlc_md  # noqa: PLC0415
        root = self._fixture()
        t0 = time.monotonic()
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT_PATH), "hint", "--root", str(root)],
                              capture_output=True, text=True, timeout=120)
        t_exit = time.monotonic() - t0
        self.assertEqual(0, proc.returncode, proc.stderr)
        self.assertTrue(proc.stdout.startswith("/sdlc-studio "), proc.stdout[:120])
        self.assertLess(t_exit, 15.0, f"`status hint` took {t_exit:.1f}s over a corpus this repository's shape")
        # The structural pin, as the dashboard's (BG0646 AC2): the shipped command hands the
        # close-owed advisory the census the gather took - entered inside the SAME open sweep,
        # never after it closed or in one of its own.
        seen = {}
        real_gather, real_adv = status.gather, status.close_owed_advisory

        def spy_gather(r, **kw):
            seen["gather_sweep"] = id(sdlc_md._CORPUS_CACHE) if sdlc_md.corpus_cache_active() else None
            return real_gather(r, **kw)

        def spy_adv(r):
            seen["advisory_sweep"] = id(sdlc_md._CORPUS_CACHE) if sdlc_md.corpus_cache_active() else None
            return real_adv(r)

        with unittest.mock.patch.object(status, "gather", spy_gather), \
             unittest.mock.patch.object(status, "close_owed_advisory", spy_adv), \
             contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(0, status.main(["hint", "--root", str(root)]))
        self.assertIsNotNone(seen.get("gather_sweep"), "`hint` ran gather outside any sweep")
        self.assertIsNotNone(seen.get("advisory_sweep"), "`hint` ran the close-owed advisory outside any sweep - its own walk")
        self.assertEqual(seen["gather_sweep"], seen["advisory_sweep"], "the advisory ran in a different sweep from the gather - a second census")

if __name__ == "__main__":
    unittest.main()
