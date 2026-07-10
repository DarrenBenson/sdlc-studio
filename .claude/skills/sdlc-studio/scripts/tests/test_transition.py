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

    def test_pyyaml_absent_still_blocks_not_crashes(self) -> None:  # BG0062
        # On a machine without PyYAML the Done gate must still emit its block (ValueError),
        # not surface a config-loading RuntimeError. The gate reads policy via the
        # gracefully-degrading project_override, never config.get's hard PyYAML path.
        import config
        orig = config._yaml
        def _boom():
            raise RuntimeError("config loading needs PyYAML")
        config._yaml = _boom
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
                self._report(root, {"stories": {"US0001-x": {"failed": 1, "stale": 0,
                                                             "failures": [{"ac": "AC1"}]}}})
                with self.assertRaises(ValueError):
                    tr.transition(root, "US0001", "Done")
        finally:
            config._yaml = orig

    def test_blocks_when_story_edited_after_verify(self) -> None:  # BG0065
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            # a green entry, but stamped in the past - the story file is newer (edited since).
            self._report(root, {"stories": {"US0001-x": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2020-01-01T00:00:00Z"}}})
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_blocks_when_ac_added_after_verify(self) -> None:  # BG0065
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n"
                              "### AC1\n- **Verify:** shell true\n\n### AC2\n- **Verify:** shell true\n")
            # green + fresh stamp (mtime check passes), but the report only accounted for 1 AC.
            self._report(root, {"stories": {"US0001-x": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2099-01-01T00:00:00Z"}}})
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "Done")

    def test_passes_when_fresh_and_ac_count_matches(self) -> None:  # BG0065 no false positive
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._story(root, "# US0001: s\n\n> **Status:** Ready\n\n### AC1\n- **Verify:** shell true\n")
            self._report(root, {"stories": {"US0001-x": {
                "failed": 0, "stale": 0, "failures": [], "ac_count": 1,
                "verified_at": "2099-01-01T00:00:00Z"}}})
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_config_toggle_downgrades_to_advisory(self) -> None:  # CR0095
        from lib import sdlc_md
        orig = sdlc_md.project_override
        sdlc_md.project_override = lambda root, dotted, default=None: (
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
            sdlc_md.project_override = orig


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

    def test_functional_to_verified_refused(self) -> None:
        # Verified claims the higher-tier proof landed; functional alone is
        # exactly the false assurance the status exists to prevent
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional (unit + component)")
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Verified")
            self.assertIn("functional", str(cm.exception))

    def test_soak_to_verified_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "soak (24h in staging)")
            res = tr.transition(root, "BG0001", "Verified")
            self.assertEqual(res["to"], "Verified")

    def test_missing_depth_to_verified_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Verified")
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

    def test_id_and_ids_merge_deduped(self) -> None:
        # CR0210 grammar: --id (repeatable) and --ids (comma list) are combinable and merged,
        # de-duplicated in first-seen order - not mutually exclusive. Here BG0001 appears in
        # both, so exactly BG0001 and BG0002 are attempted (each individually gated).
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                tr.main(["set", "--id", "BG0001", "--ids", "BG0001,BG0002",
                         "--status", "Fixed", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("BG0001", out)
            self.assertIn("BG0002", out)

    def test_repeatable_id_batches(self) -> None:
        # CR0210: repeat --id instead of the comma spelling
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            buf = io.StringIO()
            with redirect_stdout(buf):
                tr.main(["set", "--id", "BG0001", "--id", "BG0002",
                         "--status", "Fixed", "--root", str(root)])
            out = buf.getvalue()
            self.assertIn("BG0001", out)
            self.assertIn("BG0002", out)

    def test_no_ids_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._two_bugs(Path(d))
            rc = tr.main(["set", "--status", "Fixed", "--root", str(root)])
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
            "> **Verification depth:** soak\n", encoding="utf-8")
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

    def test_status_without_summary_row_now_syncs_by_insertion(self) -> None:
        # Formerly pinned index_synced=False: the writer could not ADD a
        # missing summary row, so the honest report was not-synced. The
        # summary-row insertion removed the limitation - the row is inserted
        # into the managed block and the sync report is truthfully True.
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
            self.assertTrue(res["index_synced"])
            text = (sd / "_index.md").read_text(encoding="utf-8")
            self.assertIn("| Done | 1 |", text)
            self.assertIn("| Ready | 0 |", text)

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


def _v3_bug_repo(root: Path, status: str = "inbox",
                 raised_by: str = "Scout; agent; 1") -> Path:
    """A schema-v3 repo with one bug in `status` carrying a structured Raised-by (US0065)."""
    sd = root / "sdlc-studio"
    sd.mkdir(parents=True)
    (sd / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    bd = sd / "bugs"
    bd.mkdir(parents=True)
    (bd / "BG0001-x.md").write_text(
        f"# BG0001: b\n\n> **Status:** {status}\n> **Severity:** high\n"
        f"> **Raised-by:** {raised_by}\n\n## Summary\n\nx\n", encoding="utf-8")
    (bd / "_index.md").write_text(
        "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| inbox | 1 |\n| Open | 0 |\n\n## All\n\n| ID | Title | Status |\n"
        "| --- | --- | --- |\n| [BG0001](BG0001-x.md) | b | inbox |\n", encoding="utf-8")
    return root


class TriageGateTests(unittest.TestCase):
    """US0065: the v3 gated inbox->triaged transition recording triaged_by (AC1/AC2)."""

    def test_triage_gate_requires_triaged_by(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "BG0001", "Open")  # no triaged_by -> fail loud
            self.assertIn("triaging seat must be recorded", str(ctx.exception).lower())

    def test_triage_gate_enforces_separation_of_duties(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "BG0001", "Open", triaged_by="Scout; agent; 1")
            self.assertIn("separation of duties", str(ctx.exception).lower())

    def test_triage_gate_records_triaged_by_on_success(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            res = tr.transition(root, "BG0001", "Open", triaged_by="Knox; agent; 1")
            self.assertEqual(res["to"], "Open")
            text = _read(root, "bugs", "BG0001-x.md")
            self.assertIn("> **Status:** Open", text)
            self.assertIn("> **Triaged-by:** Knox; agent; 1", text)
            self.assertTrue(res["index_synced"])

    def test_triage_gate_dormant_under_v2(self) -> None:
        # No schema_version:3 -> the triage gate never fires; a normal bug transition
        # needs no triaged_by (era-gating keeps v2 projects untouched).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text(
                "# BG0001: b\n\n> **Status:** Open\n> **Severity:** high\n\n## Summary\n\nx\n",
                encoding="utf-8")
            (bd / "_index.md").write_text(
                "# Bugs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 1 |\n"
                "| In Progress | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [BG0001](BG0001-x.md) | b | Open |\n", encoding="utf-8")
            res = tr.transition(root, "BG0001", "In Progress")  # no triaged_by required
            self.assertEqual(res["to"], "In Progress")

    def test_triage_gate_allows_solo_human_self_triage_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Darren; human; 1")
            res = tr.transition(root, "BG0001", "Open", triaged_by="Darren; human; 1")
            self.assertEqual(res["to"], "Open")               # not deadlocked
            self.assertIn("solo-human self-triage", res["warning"])

    def test_triage_gate_covers_all_exits_from_inbox(self) -> None:
        # Leaving inbox by any exit is the triage act - not only the canonical accept
        # target - so an agent cannot sidestep triage by jumping to another state.
        for target in ("In Progress", "Superseded"):
            with tempfile.TemporaryDirectory() as d:
                root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
                with self.assertRaises(ValueError) as ctx:
                    tr.transition(root, "BG0001", target)  # no triaged_by
                self.assertIn("triaging seat must be recorded", str(ctx.exception).lower())

    def test_triage_gate_records_on_non_canonical_exit(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            res = tr.transition(root, "BG0001", "In Progress", triaged_by="Knox; agent; 1")
            self.assertEqual(res["to"], "In Progress")
            self.assertIn("> **Triaged-by:** Knox; agent; 1",
                          _read(root, "bugs", "BG0001-x.md"))

    def test_triage_gate_dry_run_is_honest(self) -> None:
        # A dry-run preflight of a triage that would block must not report a false green.
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")
            with self.assertRaises(ValueError):
                tr.transition(root, "BG0001", "Open", dry_run=True)  # no triaged_by

    def test_triage_severity_recorded_alongside_raiser(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d), raised_by="Scout; agent; 1")  # raiser Severity: high
            tr.transition(root, "BG0001", "Open",
                          triaged_by="Knox; agent; 1", triage_severity="low")
            text = _read(root, "bugs", "BG0001-x.md")
            self.assertIn("> **Severity:** high", text)         # raiser's retained
            self.assertIn("> **Triage-severity:** low", text)   # triager's recorded


def _v3_story_repo(root: Path, affects: str = "docs/prd.md",
                   cfg_extra: str = "plan_review:\n  affects_files_threshold: 99\n"
                                    "  min_difficulty: extreme\n") -> Path:
    """A schema-v3 repo with one Ready story (spec-citing by default) + its index."""
    sd = root / "sdlc-studio"
    (sd / "stories").mkdir(parents=True)
    (sd / "reviews").mkdir(parents=True)
    (sd / ".config.yaml").write_text("schema_version: 3\n" + cfg_extra, encoding="utf-8")
    (sd / "stories" / "US0001-x.md").write_text(
        "# US0001: s\n\n> **Status:** Ready\n> **Epic:** EP0001\n"
        f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n"
        "### AC1: a\n- **Given** x\n- **When** y\n- **Then** z\n", encoding="utf-8")
    (sd / "stories" / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
        "| In Progress | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
    return root


class PlanReviewGateTests(unittest.TestCase):
    """US0090: a spec-derived story is blocked from entering In Progress until reviewed."""

    def test_triggered_story_blocked_entering_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))          # cites docs/prd.md -> trigger fires
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "US0001", "In Progress")
            self.assertIn("plan-review", str(ctx.exception).lower())

    def test_independent_plan_approve_unblocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            cr = _load("critic", "critic.py")
            cr.record_verdict(root, "US0001", "APPROVE", reviewer="qa", author="dev",
                              phase="plan-review")
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")

    def test_override_field_unblocks(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "> **Affects:** docs/prd.md",
                "> **Affects:** docs/prd.md\n> **Plan-Review-Override:** ops: hotfix"),
                encoding="utf-8")
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")

    def test_force_does_not_bypass(self) -> None:
        # The only sanctioned skip is the recorded override, never --force (AC3).
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "In Progress", force=True)

    def test_dry_run_is_honest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "US0001", "In Progress", dry_run=True)

    def test_untriggered_story_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d), affects="a.py")   # no spec, low volume
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")

    def test_direct_ready_to_done_is_blocked(self) -> None:
        # The gate's PURPOSE is defeated if a spec-derived story can be closed straight to
        # Done unreviewed - guard every entry to an implementation state, not just In Progress.
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "US0001", "Done")
            self.assertIn("plan-review", str(ctx.exception).lower())

    def test_forward_walk_after_review_reaches_done(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            cr = _load("critic", "critic.py")
            cr.record_verdict(root, "US0001", "APPROVE", reviewer="qa", author="dev",
                              phase="plan-review")
            self.assertEqual(tr.transition(root, "US0001", "In Progress")["to"], "In Progress")
            # In Progress -> Done is not re-gated (already past the pre-impl states)
            self.assertEqual(tr.transition(root, "US0001", "Done", force=True)["to"], "Done")

    def test_dormant_under_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_story_repo(Path(d))
            sd = root / "sdlc-studio"
            (sd / ".config.yaml").write_text("schema_version: 2\n", encoding="utf-8")
            res = tr.transition(root, "US0001", "In Progress")
            self.assertEqual(res["to"], "In Progress")       # gate no-op on v2




class AnnotateVerbTests(unittest.TestCase):
    """CR0209/US0116 AC1: a deterministic metadata-stamp verb."""

    def _bug(self, root: Path) -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True, exist_ok=True)
        p = d / "BG0001-x.md"
        p.write_text("# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n"
                     "> **Created-by:** sdlc-studio new\n\n## Summary\n\ns\n", encoding="utf-8")
        return p

    def test_annotate_inserts_a_new_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            rc = tr.main(["annotate", "--id", "BG0001",
                                  "--field", "Verification depth",
                                  "--value", "functional (tests red-first)", "--root", str(root)])
            self.assertEqual(rc, 0)
            body = p.read_text(encoding="utf-8")
            self.assertIn("> **Verification depth:** functional (tests red-first)", body)
            self.assertEqual(tr.sdlc_md.extract_field(body, "Verification depth"),
                             "functional (tests red-first)")

    def test_annotate_updates_in_place_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            for value in ("smoke", "functional (upgraded)"):
                rc = tr.main(["annotate", "--id", "BG0001",
                                      "--field", "Verification depth",
                                      "--value", value, "--root", str(root)])
                self.assertEqual(rc, 0)
            body = p.read_text(encoding="utf-8")
            self.assertEqual(body.count("**Verification depth:**"), 1)
            self.assertIn("functional (upgraded)", body)

    def test_annotate_unknown_id_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "sdlc-studio").mkdir()
            rc = tr.main(["annotate", "--id", "BG9999", "--field", "F",
                                  "--value", "v", "--root", d])
            self.assertNotEqual(rc, 0)


class AllGatesInOneRefusalTests(unittest.TestCase):
    """CR0209/US0116 AC2: a blocked transition names EVERY unmet gate."""

    def test_v3_finding_refusal_names_depth_and_triage_together(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                               encoding="utf-8")
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir()
            (bd / "BG0001-x.md").write_text(
                "# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n## Summary\n\ns\n",
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                tr.transition(root, "BG0001", "Fixed")
            msg = str(ctx.exception)
            self.assertIn("Verification depth", msg)
            self.assertIn("triage", msg.lower())




class AnnotateCannotBypassGatesTests(unittest.TestCase):
    """Critic F1/F2/F5: annotate must never touch gated/index-backed fields, must fail loud
    without a Status anchor, and must reject metadata-injection values."""

    def _v3_inbox_bug(self, root: Path) -> Path:
        (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(exist_ok=True)
        p = d / "BG0001-x.md"
        p.write_text("# BG0001: x\n\n> **Status:** inbox\n> **Severity:** Low\n\n"
                     "## Summary\n\ns\n", encoding="utf-8")
        return p

    def test_annotate_refuses_the_status_field(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            before = p.read_text(encoding="utf-8")
            for spelling in ("Status", "status", "STATUS"):
                rc = tr.main(["annotate", "--id", "BG0001", "--field", spelling,
                              "--value", "Fixed", "--root", str(root)])
                self.assertNotEqual(rc, 0, spelling)
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_annotate_refuses_the_provenance_security_stamp(self) -> None:
        # Closing-critic F1: Provenance is a verify_ac shell-gate control - annotate clearing
        # it exit-0 re-enabled shell on untrusted content. It must be denylisted like Status.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            p.write_text(p.read_text(encoding="utf-8").replace(
                "> **Severity:** Low\n", "> **Severity:** Low\n> **Provenance:** external\n"),
                encoding="utf-8")
            before = p.read_text(encoding="utf-8")
            for spelling in ("Provenance", "provenance", " Provenance "):
                rc = tr.main(["annotate", "--id", "BG0001", "--field", spelling,
                              "--value", "internal", "--root", str(root)])
                self.assertNotEqual(rc, 0, spelling)
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_annotate_refuses_triage_fields(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            before = p.read_text(encoding="utf-8")
            rc = tr.main(["annotate", "--id", "BG0001", "--field", "Triaged-by",
                          "--value", "Me; human; 1", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_annotate_fails_loud_without_a_status_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            bd = root / "sdlc-studio" / "bugs"
            bd.mkdir(parents=True)
            (bd / "BG0001-x.md").write_text("# BG0001: x\n\nno metadata block\n",
                                            encoding="utf-8")
            rc = tr.main(["annotate", "--id", "BG0001", "--field", "Verification depth",
                          "--value", "functional", "--root", str(root)])
            self.assertNotEqual(rc, 0)

    def test_annotate_rejects_newlines_in_field_and_value(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._v3_inbox_bug(root)
            before = p.read_text(encoding="utf-8")
            for sep in ("\n", "\r", "\u2028"):
                rc = tr.main(["annotate", "--id", "BG0001", "--field", "Verification depth",
                              "--value", f"functional{sep}> **Status:** Fixed",
                              "--root", str(root)])
                self.assertNotEqual(rc, 0, repr(sep))
            self.assertEqual(p.read_text(encoding="utf-8"), before)


class OneCallCloseTests(unittest.TestCase):
    """CR0213: the three-verb bug close (annotate depth, record verdict, gated set) collapses
    to one call - and every predictable refusal happens BEFORE any write."""

    def _bug(self, root: Path) -> Path:
        bd = root / "sdlc-studio" / "bugs"
        bd.mkdir(parents=True)
        (bd / "BG0001-x.md").write_text(
            "# BG0001: a\n\n> **Status:** In Progress\n", encoding="utf-8")
        (bd / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | a | In Progress |\n", encoding="utf-8")
        return root

    def test_one_call_stamps_records_and_transitions(self) -> None:
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            with redirect_stdout(io.StringIO()):
                rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                              "--depth", "functional (one-call test)",
                              "--verdict", "approve", "--reviewer", "Blake", "--author", "Alex",
                              "--root", str(root)])
            self.assertEqual(rc, 0)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** Fixed", text)
            self.assertIn("Verification depth:** functional (one-call test)", text)
            log = (root / "sdlc-studio" / "reviews" / "critic-verdicts.md").read_text(encoding="utf-8")
            self.assertIn("BG0001", log)
            self.assertIn("Blake", log)

    def test_self_review_refused_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                          "--depth", "functional", "--verdict", "approve",
                          "--reviewer", "Alex", "--author", "Alex", "--root", str(root)])
            self.assertEqual(rc, 2)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** In Progress", text)           # no transition
            self.assertNotIn("Verification depth", text)               # no depth stamp either
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

    def test_reviewer_without_author_is_a_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                          "--verdict", "approve", "--reviewer", "Blake", "--root", str(root)])
            self.assertEqual(rc, 2)

    def test_depth_alone_still_gates_normally(self) -> None:
        # --depth without reviewer/author: stamp + gated transition, no verdict recording
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            with redirect_stdout(io.StringIO()):
                rc = tr.main(["set", "--id", "BG0001", "--status", "Fixed",
                              "--depth", "functional (stamp only)", "--root", str(root)])
            self.assertEqual(rc, 0)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Status:** Fixed", text)


if __name__ == "__main__":
    unittest.main()
