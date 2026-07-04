"""Unit tests for transition.py - status transition + index/epic cascade (CR0042).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

DIR = Path(__file__).resolve().parent.parent


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, DIR / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tr = _load("transition", "transition.py")
rc = _load("reconcile", "reconcile.py")


def _repo(root: Path) -> Path:
    sd = root / "sdlc-studio" / "stories"
    sd.mkdir(parents=True)
    (sd / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
        "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n", encoding="utf-8")
    (sd / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Ready | 1 |\n| In Progress | 0 |\n| Done | 0 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
    ed = root / "sdlc-studio" / "epics"
    ed.mkdir(parents=True)
    (ed / "EP0001-e.md").write_text(
        "# EP0001: e\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
        "- [ ] [US0001: s](../stories/US0001-x.md)\n", encoding="utf-8")
    return root


def _read(root, *parts):
    return (root.joinpath("sdlc-studio", *parts)).read_text(encoding="utf-8")


class TransitionTests(unittest.TestCase):
    def test_sets_status_syncs_index_and_ticks_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            res = tr.transition(root, "US0001", "Done", force=True)  # gate bypassed: cascade test
            self.assertEqual((res["from"], res["to"]), ("Ready", "Done"))
            self.assertIn("> **Status:** Done", _read(root, "stories", "US0001-x.md"))
            idx = _read(root, "stories", "_index.md")
            self.assertIn("| [US0001](US0001-x.md) | s | Done |", idx)   # row synced
            self.assertIn("| Done | 1 |", idx)                          # counts recomputed
            self.assertIn("| Ready | 0 |", idx)
            self.assertIn("- [x] [US0001: s]", _read(root, "epics", "EP0001-e.md"))  # epic ticked
            self.assertEqual(res["epic"], "EP0001")
            self.assertEqual(rc.detect_type("story", root)["drift"], [])  # 0 drift after

    def test_reopen_unticks_epic(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            tr.transition(root, "US0001", "Done", force=True)  # gate bypassed: cascade test
            tr.transition(root, "US0001", "In Progress")
            self.assertIn("- [ ] [US0001: s]", _read(root, "epics", "EP0001-e.md"))
            self.assertIn("> **Status:** In Progress", _read(root, "stories", "US0001-x.md"))
            self.assertEqual(rc.detect_type("story", root)["drift"], [])

    def test_invalid_status_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Frozen")

    def test_unknown_id_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US9099", "Done")

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            before_story = _read(root, "stories", "US0001-x.md")
            before_idx = _read(root, "stories", "_index.md")
            before_epic = _read(root, "epics", "EP0001-e.md")
            res = tr.transition(root, "US0001", "Done", dry_run=True)
            self.assertEqual(res["to"], "Done")
            self.assertEqual(_read(root, "stories", "US0001-x.md"), before_story)
            self.assertEqual(_read(root, "stories", "_index.md"), before_idx)
            self.assertEqual(_read(root, "epics", "EP0001-e.md"), before_epic)

    def test_inline_status_field_preserved(self) -> None:
        # House inline `· **Status:** X · **Epic:** Y` form: only the Status value changes.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text("# US0001: s\n\n> **Status:** Ready · **Epic:** EP0001 · **Points:** 3\n\n"
                          "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n",
                          encoding="utf-8")
            tr.transition(root, "US0001", "Done", force=True)  # gate bypassed: cascade test
            line = next(ln for ln in sp.read_text(encoding="utf-8").splitlines() if "Status" in ln)
            self.assertIn("**Status:** Done", line)
            self.assertIn("**Epic:** EP0001", line)   # neighbours intact
            self.assertIn("**Points:** 3", line)


class DoneGateTests(unittest.TestCase):
    """CR0084: a story may not reach Done with red / never-run executable ACs."""

    def _story(self, root: Path, body: str) -> None:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "US0001-x.md").write_text(body, encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")

    def _report(self, root: Path, payload: dict) -> None:
        rp = root / "sdlc-studio" / ".local" / "verify-report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(payload), encoding="utf-8")

    def test_blocks_when_executable_ac_never_verified(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")        # no report -> blocked

    def test_blocks_when_report_red(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            self._report(root, {"stories": {"US0001-x": {"failed": 1, "stale": 0,
                                                          "failures": [{"ac": "AC1"}]}}})
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_passes_when_report_green(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            self._report(root, {"stories": {"US0001-x": {"failed": 0, "stale": 0, "failures": []}}})
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_manual_only_story_not_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** manual eyeball it\n")
            res = tr.transition(root, "US0001", "Done")     # only manual ACs -> nothing to gate
            self.assertEqual(res["to"], "Done")

    def test_force_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            res = tr.transition(root, "US0001", "Done", force=True)
            self.assertEqual(res["to"], "Done")

    def test_config_toggle_downgrades_to_advisory(self) -> None:  # CR0095
        import config
        orig = config.get
        config.get = lambda root, dotted, default=None: (
            False if dotted == "quality.done_requires_verified" else orig(root, dotted, default))
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
                self._report(root, {"stories": {"US0001-x": {"failed": 1, "stale": 0,
                                                             "failures": [{"ac": "AC1"}]}}})
                res = tr.transition(root, "US0001", "Done")   # toggle off -> warns, does not raise
                self.assertEqual(res["to"], "Done")
                self.assertIn("advisory", (res["warning"] or "").lower())
        finally:
            config.get = orig


def _bug_repo(root: Path, depth: str | None, prod: bool = False) -> Path:
    bd = root / "sdlc-studio" / "bugs"
    bd.mkdir(parents=True)
    header = "# BG0001: b\n\n> **Status:** In Progress\n> **Severity:** medium\n"
    if prod:
        header += "> **Production-affecting:** yes\n"
    if depth is not None:
        header += f"> **Verification depth:** {depth}\n"
    (bd / "BG0001-x.md").write_text(
        header + "\n## Summary\n\nx\n\n## Steps to Reproduce\n\n1. x\n\n## Proposed Fix\n\ny\n",
        encoding="utf-8")
    (bd / "_index.md").write_text(
        "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| In Progress | 1 |\n| Fixed | 0 |\n| Closed | 0 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [BG0001](BG0001-x.md) | b | In Progress |\n", encoding="utf-8")
    return root


class DepthTierGateTests(unittest.TestCase):
    """Verification-depth tiers are enforced on bug transitions, not decorative."""

    def test_smoke_to_fixed_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "smoke")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Fixed")
            self.assertIn("smoke", str(cm.exception))
            self.assertIn("functional", str(cm.exception))  # names required tier

    def test_functional_to_fixed_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional (unit + regression)")
            res = tr.transition(root, "BG0001", "Fixed")
            self.assertEqual(res["to"], "Fixed")

    def test_missing_depth_refused_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Fixed")
            self.assertIn("Verification depth", str(cm.exception))

    def test_prod_bug_smoke_to_closed_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional", prod=True)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Closed")
            self.assertIn("soak", str(cm.exception))

    def test_prod_bug_soak_to_closed_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "soak (7 days)", prod=True)
            res = tr.transition(root, "BG0001", "Closed")
            self.assertEqual(res["to"], "Closed")

    def test_non_prod_close_path_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)  # no depth, not production-affecting
            res = tr.transition(root, "BG0001", "Closed")
            self.assertEqual(res["to"], "Closed")

    def test_decorated_prod_flag_still_gates(self) -> None:
        # 'yes (checkout path)' must not silently switch the soak gate OFF.
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional")
            p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "> **Severity:** medium\n",
                "> **Severity:** medium\n> **Production-affecting:** yes (checkout path)\n"),
                encoding="utf-8")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Closed")
            self.assertIn("soak", str(cm.exception))

    def test_force_overrides_depth_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "smoke")
            res = tr.transition(root, "BG0001", "Fixed", force=True)
            self.assertEqual(res["to"], "Fixed")


class StoryTargetParityTests(unittest.TestCase):
    """Story Done should not out-run a declared AC Verification target - advisory
    by default, gateable via quality.depth_parity_gate."""

    def _story_with_target(self, root: Path, target: str) -> Path:
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True)
        (sd / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            f"### AC1\n- **Verify:** manual check\n- **Verification target:** {target}\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return root

    def test_target_above_functional_warns_but_allows(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._story_with_target(Path(d), "soak")
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")
            self.assertIn("soak", res["warning"] or "")

    def test_functional_target_no_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._story_with_target(Path(d), "functional")
            res = tr.transition(root, "US0001", "Done")
            self.assertIsNone(res["warning"])


class BatchIdsTests(unittest.TestCase):
    """CR0143: --ids batches same-target transitions; each id individually gated,
    one refusal never aborts the rest."""

    def _two_bugs(self, root: Path):
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n"
            "> **Verification depth:** functional\n", encoding="utf-8")
        (bd / "BG0002-y.md").write_text(
            "# BG0002: b\n\n> **Status:** In Progress\n"
            "> **Verification depth:** smoke\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n"
            "| [BG0002](BG0002-y.md) | b | In Progress |\n", encoding="utf-8")
        return root

    def test_ids_batch_gates_each_and_continues(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = tr.main(["set", "--ids", "BG0001,BG0002", "--status", "Fixed",
                              "--root", str(root)])
            out = buf.getvalue()
            self.assertNotEqual(rc, 0)                       # one refusal -> non-zero
            self.assertIn("BG0001", out)                     # the pass reported
            self.assertIn("blocked", out.lower())            # the refusal reported
            text1 = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            text2 = (root / "sdlc-studio" / "bugs" / "BG0002-y.md").read_text(encoding="utf-8")
            self.assertIn("**Status:** Fixed", text1)        # gated pass applied
            self.assertIn("**Status:** In Progress", text2)  # gated refusal untouched

    def test_id_and_ids_mutually_exclusive(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--ids", "BG0001,BG0002",
                          "--status", "Fixed", "--root", str(root)])
            self.assertEqual(rc, 2)

    def test_meta_type_refused_with_reason(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio" / "retros").mkdir(parents=True)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RETRO0001", "Done")
            self.assertIn("meta", str(cm.exception).lower())


class BatchJsonCleanTests(unittest.TestCase):
    def test_batch_json_stdout_is_parseable(self) -> None:
        # critic finding: the human batch summary must not pollute json stdout
        import io, json as _json
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"; bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text(
                "# BG0001: a\n\n> **Status:** Open\n", encoding="utf-8")
            (bd / "_index.md").write_text(
                "# B\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [BG0001](BG0001-x.md) | a | Open |\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                tr.main(["set", "--ids", "BG0001,BG9999", "--status", "In Progress",
                         "--root", str(root), "--format", "json"])
            _json.loads(buf.getvalue())   # must be pure JSON


class TelemetryOnCloseTests(unittest.TestCase):
    """BG0052: a terminal transition records the telemetry event - the loop's
    real close path must not bypass the calibration data (never a second call)."""

    def _bug(self, root: Path, status="In Progress"):
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True, exist_ok=True)
        (bd / "BG0001-x.md").write_text(
            f"# BG0001: a\n\n> **Status:** {status}\n"
            "> **Verification depth:** functional\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# B\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [BG0001](BG0001-x.md) | a | {status} |\n", encoding="utf-8")
        return root

    def _records(self, root: Path):
        p = root / "sdlc-studio" / ".local" / "telemetry.jsonl"
        if not p.exists():
            return []
        return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_terminal_transition_records_exactly_one_event(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Closed")
            recs = self._records(root)
            self.assertEqual(len(recs), 1, recs)
            self.assertEqual(recs[0]["id"], "BG0001")
            self.assertEqual(recs[0]["type"], "bug")

    def test_non_terminal_transition_records_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d), status="Open")
            tr.transition(root, "BG0001", "In Progress")
            self.assertEqual(self._records(root), [])

    def test_dry_run_records_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Closed", dry_run=True)
            self.assertEqual(self._records(root), [])

    def test_lifecycle_records_exactly_one_event(self) -> None:
        # Fixed -> Verified -> Closed is ONE unit closing once: one event, not three;
        # an idempotent re-close records nothing.
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Fixed")
            tr.transition(root, "BG0001", "Verified")
            tr.transition(root, "BG0001", "Closed")
            tr.transition(root, "BG0001", "Closed")
            self.assertEqual(len(self._records(root)), 1)

    def test_reopen_and_reclose_records_a_second_event(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.transition(root, "BG0001", "Closed")
            tr.transition(root, "BG0001", "In Progress")   # reopened
            tr.transition(root, "BG0001", "Closed")
            recs = self._records(root)
            self.assertEqual(len(recs), 2)

    def test_fractional_wall_time_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            tr.main(["set", "--id", "BG0001", "--status", "Closed",
                     "--root", str(root), "--wall-time-s", "12.5"])
            self.assertEqual(self._records(root)[0]["wall_time_s"], 12.5)

    def test_cli_metrics_pass_through(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc_ = tr.main(["set", "--id", "BG0001", "--status", "Closed",
                           "--root", str(root), "--iterations", "2",
                           "--verdict", "approve"])
            self.assertEqual(rc_, 0)
            recs = self._records(root)
            self.assertEqual(recs[0]["iterations"], 2)
            self.assertEqual(recs[0]["critic_verdict"], "approve")


class HonestSyncTests(unittest.TestCase):
    """index_synced reflects the real post-transition state (critic CR0042)."""

    def test_archived_row_reports_not_synced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text(
                "# US0001: s\n\n> **Status:** Ready\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
                "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n",
                encoding="utf-8")  # empty active table - the row lives in archive
            ad = sd / "archive" / "r1"
            ad.mkdir(parents=True)
            (ad / "story.md").write_text(
                "# story archive - r1\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](../../US0001-x.md) | s | Ready |\n", encoding="utf-8")
            res = tr.transition(root, "US0001", "Done")
            self.assertFalse(res["index_synced"])      # archive row not synced - honest
            self.assertIsNotNone(res["warning"])

    def test_status_without_summary_row_reports_not_synced(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: s\n\n> **Status:** Ready\n", encoding="utf-8")
            (sd / "_index.md").write_text(
                "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n\n"
                "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")  # no Done summary row
            res = tr.transition(root, "US0001", "Done")
            self.assertFalse(res["index_synced"])

    def test_no_status_field_raises(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            sd = root / "sdlc-studio" / "stories"
            sd.mkdir(parents=True)
            (sd / "US0001-x.md").write_text("# US0001: s\n\n> **Epic:** EP0001\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_non_story_type_no_epic_cascade(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cd = root / "sdlc-studio" / "change-requests"
            cd.mkdir(parents=True)
            (cd / "CR0001-x.md").write_text("# CR-0001: c\n\n> **Status:** Proposed\n", encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 1 |\n"
                "| Complete | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0001](CR0001-x.md) | c | Proposed |\n", encoding="utf-8")
            res = tr.transition(root, "CR0001", "Complete")
            self.assertTrue(res["index_synced"])
            self.assertIsNone(res["epic"])
            self.assertEqual(rc.detect_type("cr", root)["drift"], [])

    def test_epic_absent_skips_gracefully(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            # point the story at a non-existent epic
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "[EP0001: e](../epics/EP0001-e.md)", "[EP0099: gone](../epics/EP0099-gone.md)"),
                encoding="utf-8")
            res = tr.transition(root, "US0001", "Done", force=True)  # must not crash (cascade test)
            self.assertIsNone(res["epic"])
            self.assertTrue(res["index_synced"])


if __name__ == "__main__":
    unittest.main()
