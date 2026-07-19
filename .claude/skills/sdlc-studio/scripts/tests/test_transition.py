"""Unit tests for transition.py - status transition + index/epic cascade (CR0042).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import json
import sys
import contextlib
import re
import io
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


class VerdictErrorNamesAnnotateTests(unittest.TestCase):
    """`set --author X` without the verdict pair is an identity-only stamp gone to the
    wrong verb. The all-or-none refusal must name `transition annotate` - the verb
    that exists for exactly that - so the actor is not left to re-derive it."""

    def test_author_without_verdict_pair_names_annotate(self) -> None:
        import io
        from contextlib import redirect_stderr
        args = tr.build_parser().parse_args(
            ["set", "--id", "US0001", "--status", "Fixed", "--author", "dani"])
        buf = io.StringIO()
        with redirect_stderr(buf):
            rc_val = tr.cmd_set(args)
        self.assertEqual(rc_val, 2)
        self.assertIn("annotate", buf.getvalue())


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
        # `In Progress`, not `Done`. This story declares an executable AC that has never been
        # verified, so a Done dry-run now correctly REFUSES (BG0213) - it used to pass, which
        # is precisely the dishonesty that bug was about. The write-nothing property being
        # asserted here needs a transition that is actually allowed; the refused case is
        # covered by DryRunHonestyTests.
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            before_story = _read(root, "stories", "US0001-x.md")
            before_idx = _read(root, "stories", "_index.md")
            before_epic = _read(root, "epics", "EP0001-e.md")
            res = tr.transition(root, "US0001", "In Progress", dry_run=True)
            self.assertEqual(res["to"], "In Progress")
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
                _quiet(tr.transition, root, "BG0001", "Fixed")
            self.assertIn("smoke", str(cm.exception))
            self.assertIn("functional", str(cm.exception))  # names required tier

    def test_functional_to_fixed_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), "functional (unit + regression)")
            res = _quiet(tr.transition, root, "BG0001", "Fixed")
            self.assertEqual(res["to"], "Fixed")

    def test_missing_depth_refused_not_passed(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _bug_repo(Path(d), None)
            with self.assertRaises(ValueError) as cm:
                _quiet(tr.transition, root, "BG0001", "Fixed")
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
        # Through the public read, not a hard-coded path: where the evidence lives is
        # telemetry's business, and a test that pinned the path would have to be edited every
        # time it moved rather than checking the behaviour it cares about.
        import telemetry as tel
        return tel.read_all(root)

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
            _quiet(tr.transition, root, "BG0001", "Fixed")
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

    def test_close_threads_attempts_to_telemetry(self) -> None:
        # BG0152: a close that escalated must record every attempt through the SAME close
        # path, so unit_cost sums the true cost. Before the fix the metrics dict dropped
        # attempts/tokens/model entirely and every escalation landed as a flat record.
        import telemetry as tel
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc_ = tr.main(["set", "--id", "BG0001", "--status", "Closed",
                           "--root", str(root),
                           "--attempt", "haiku:1000", "--attempt", "opus:5000"])
            self.assertEqual(rc_, 0)
            rec = self._records(root)[0]
            self.assertEqual(rec["attempts"],
                             [{"model": "haiku", "tokens": 1000},
                              {"model": "opus", "tokens": 5000}])
            self.assertEqual(tel.unit_cost(root, rec)["tokens"], 6000)  # summed, not last-line

    def test_malformed_attempt_fails_fast_and_writes_nothing(self) -> None:
        # A bad --attempt is a usage error (rc 2), refused before any id is touched -
        # never caught and re-reported once per id, never a partial write.
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            rc_ = tr.main(["set", "--id", "BG0001", "--status", "Closed",
                           "--root", str(root), "--attempt", "no-tokens-here"])
            self.assertEqual(rc_, 2)
            self.assertEqual(self._records(root), [])


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
            (cd / "CR0001-x.md").write_text(
                "# CR-0001: c\n\n> **Status:** Proposed\n> **Decomposed-into:** EP0001\n",
                encoding="utf-8")
            (cd / "_index.md").write_text(
                "# CRs\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Proposed | 1 |\n"
                "| Complete | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [CR-0001](CR0001-x.md) | c | Proposed |\n", encoding="utf-8")
            # G2 (US0122): a CR reaches Complete only when its children are resolved. Give it a
            # Done child epic so the completion is legitimate - this test is about the non-story
            # cascade/sync, not the derived-status gate.
            ed = root / "sdlc-studio" / "epics"
            ed.mkdir(parents=True)
            (ed / "EP0001-c.md").write_text(
                "# EP0001: c\n\n> **Status:** Done\n> **Parent:** CR0001\n", encoding="utf-8")
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
                _quiet(tr.transition, root, "BG0001", "Fixed")
            msg = str(ctx.exception)
            self.assertIn("Verification depth", msg)
            self.assertIn("triage", msg.lower())




def _quiet(fn, *args, **kwargs):
    """Run `fn` with its diagnostics captured. A green suite must print nothing, or a real
    error hides in the noise - the repo's test-noise gate enforces that as a line budget."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*args, **kwargs)


class DryRunHonestyTests(unittest.TestCase):
    """BG0213: a dry-run must give the same answer as the real run, and write nothing.

    A dry-run exists so an agent learns a transition's requirements BEFORE doing the work.
    One that reports success where the real run blocks is worse than none: the requirement
    is still met as a refusal afterwards, and the agent has been told the opposite in the
    meantime. The tier gate already fires on dry-run for exactly this reason, in a comment
    stating that an honest preflight surfaces the refusal a real run would hit; the bug-depth,
    depth-parity and AC-verify gates simply did not follow it.
    """

    def _bug_without_depth(self, root: Path) -> None:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        (d / "BG0001-x.md").write_text(
            "# BG0001: x\n\n> **Status:** Open\n> **Severity:** Low\n> **Points:** 2\n\n"
            "## Summary\n\ns\n", encoding="utf-8")
        (d / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | x | Open |\n", encoding="utf-8")

    def test_a_dry_run_reports_the_refusal_the_real_run_gives(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            self.assertIn("Verification depth", str(ctx.exception))

    def test_the_dry_run_and_the_real_run_agree(self) -> None:
        # The two paths must differ only in whether the write happens.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            dry = real = None
            try:
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            except ValueError as exc:
                dry = str(exc)
            try:
                _quiet(tr.transition, root, "BG0001", "Fixed")
            except ValueError as exc:
                real = str(exc)
            self.assertEqual(dry, real, "dry-run and real run disagree about the same transition")
            self.assertIsNotNone(dry, "both must refuse; a passing pair proves nothing here")

    def test_a_refused_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            before = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            with self.assertRaises(ValueError):
                _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            after = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)

    def test_a_satisfiable_transition_still_dry_runs_clean(self) -> None:
        # The negative branch: making the gates fire on dry-run must not make every dry-run
        # refuse, or the honesty fix would just be a different lie.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            p = root / "sdlc-studio" / "bugs" / "BG0001-x.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "> **Severity:** Low",
                "> **Verification depth:** functional (reproduced)\n> **Severity:** Low"),
                encoding="utf-8")
            res = _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True)
            self.assertEqual(res["to"], "Fixed")
            self.assertIn("> **Status:** Open", p.read_text(encoding="utf-8"))

    def test_a_story_done_dry_run_reports_the_ac_verify_refusal(self) -> None:
        """The STORY half of the same fix, which the bug cases cannot reach.

        Restoring `not dry_run` on the AC-verify gate alone left the whole suite green -
        every other test here exercises a BUG, so the story branch was unpinned while the
        commit claimed the fix applied to all of them.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))       # US0001 declares an executable AC, never verified
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "US0001", "Done", dry_run=True)
            self.assertIn("never verified", str(ctx.exception))
            self.assertIn("> **Status:** Ready", _read(root, "stories", "US0001-x.md"))

    def test_a_story_dry_run_reports_the_depth_parity_refusal(self) -> None:
        """The THIRD gate the BG0213 fix changed, which had no test at all.

        Restoring `not dry_run` on this branch left the entire suite green, while the commit
        claimed the fix covered all three gates it touched. It is advisory by default, so the
        project must opt in via `quality.depth_parity_gate` for it to refuse - which is why
        the other story tests never reach it.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _repo(Path(d))
            (root / "sdlc-studio" / ".config.yaml").write_text(
                "quality:\n  depth_parity_gate: true\n  done_requires_verified: false\n",
                encoding="utf-8")
            sp = root / "sdlc-studio" / "stories" / "US0001-x.md"
            sp.write_text(sp.read_text(encoding="utf-8").replace(
                "- **Verify:** shell echo ok",
                "- **Verification target:** soak\n- **Verify:** shell echo ok"),
                encoding="utf-8")
            with self.assertRaises(ValueError) as ctx:
                _quiet(tr.transition, root, "US0001", "Done", dry_run=True)
            self.assertIn("Verification target", str(ctx.exception))
            self.assertIn("> **Status:** Ready", sp.read_text(encoding="utf-8"))

    def test_force_still_waives_the_gate_on_a_dry_run(self) -> None:
        # `--force` is a legitimate override, so a forced dry-run must report what a forced
        # real run would do - not refuse. Dropping `not dry_run` without keeping `not force`
        # would break this.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug_without_depth(root)
            res = _quiet(tr.transition, root, "BG0001", "Fixed", dry_run=True, force=True)
            self.assertEqual(res["to"], "Fixed")


class RequirementsPreflightTests(unittest.TestCase):
    """US0267: ask what a transition needs BEFORE doing the work."""

    def _bug(self, root: Path, depth: str = "") -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        line = f"> **Verification depth:** {depth}\n" if depth else ""
        p = d / "BG0001-x.md"
        p.write_text(f"# BG0001: x\n\n> **Status:** Open\n{line}"
                     "> **Severity:** Low\n> **Points:** 2\n\n## Summary\n\ns\n",
                     encoding="utf-8")
        (d / "_index.md").write_text(
            "# Bugs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [BG0001](BG0001-x.md) | x | Open |\n", encoding="utf-8")
        return p

    def test_requirements_listed_before_work(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root)
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertEqual(len(unmet), 1)
            self.assertIn("Verification depth", unmet[0])

    def test_a_satisfied_transition_reports_nothing_unmet(self) -> None:
        # The negative branch: a command that always found a requirement would be useless
        # and would still pass the assertion above.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._bug(root, depth="functional (reproduced)")
            self.assertEqual(_quiet(tr.requirements, root, "BG0001", "Fixed"), [])

    def test_asking_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = self._bug(root)
            before = p.read_text(encoding="utf-8")
            _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertEqual(p.read_text(encoding="utf-8"), before)

    def test_requirements_are_not_duplicated(self) -> None:
        """AC3: the text comes from the gate, so it cannot drift from the gate.

        Proven by changing the GATE's wording and watching the reported requirement change
        with it. A hand-maintained copy in the reporter would keep the old words and pass
        every other test in this class.
        """
        sentinel = "SENTINEL-GATE-WORDING"
        original = tr._bug_depth_gate
        try:
            tr._bug_depth_gate = lambda text, target: sentinel
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._bug(root)
                unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertTrue(any(sentinel in u for u in unmet),
                            "the reporter restates requirements instead of deriving them")
        finally:
            tr._bug_depth_gate = original

    def test_an_unknown_id_raises_rather_than_reporting_a_bogus_requirement(self) -> None:
        """A lookup failure must never masquerade as a requirement.

        The first version parsed ANY ValueError into the unmet list, so asking about a
        nonexistent id answered "you must satisfy: <not-found message>" - a confidently wrong
        answer, which is the class of defect this command exists to end. Caught by the
        briefing's own unresolvable-unit test rather than by reading.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir(parents=True)
            with self.assertRaises((ValueError, FileNotFoundError)):
                _quiet(tr.requirements, root, "BG9999", "Fixed")

    def _two_suffix_free_gates(self, root: Path) -> None:
        """A story that trips the TIER gate and the PLAN-REVIEW gate.

        Both state their reason WITHOUT the `". Override with --force"` suffix, which is the
        case the old prose-splitting collapsed into one item. Every earlier attempt at this
        test used a fixture where one of the two blocks carried the suffix, so the wrong
        delimiter still yielded two and the test passed on the defect.
        """
        (root / "sdlc-studio").mkdir(parents=True)
        (root / "sdlc-studio" / ".config.yaml").write_text("schema_version: 3\n",
                                                           encoding="utf-8")
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir()
        # `Template: full` with none of the sections the full tier promises -> tier gate.
        # Ready -> In Progress on a schema-v3 story -> plan-review gate.
        (sd / "US0001-x.md").write_text(
            "# US0001: s\n\n> **Status:** Ready\n> **Template:** full\n"
            "> **Epic:** [EP0001: e](../epics/EP0001-e.md)\n\n"
            "## Acceptance Criteria\n\n### AC1\n- **Verify:** shell echo ok\n",
            encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        ed = root / "sdlc-studio" / "epics"
        ed.mkdir()
        (ed / "EP0001-e.md").write_text(
            "# EP0001: e\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n"
            "- [ ] [US0001: s](../stories/US0001-x.md)\n", encoding="utf-8")

    def test_two_suffix_free_gates_are_two_requirements_not_one(self) -> None:
        """THE case the re-parsing collapsed - driven through the real ladder.

        The previous version of this test constructed a `GateRefusal` by hand and asserted
        `__init__` stored its argument. No gate ran, `requirements()` was never called, and
        the defective code it claimed to catch was never executed - so re-introducing the
        merge left the whole suite green. A test that names a defect it cannot reach is worse
        than no test: it reads as coverage.
        """
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._two_suffix_free_gates(root)
            unmet = _quiet(tr.requirements, root, "US0001", "In Progress")
        self.assertEqual(len(unmet), 2, f"two gates collapsed into {len(unmet)}: {unmet}")
        joined = " ".join(unmet)
        self.assertIn("full", joined)          # the tier gate's reason
        self.assertIn("plan-review", joined)   # the plan-review gate's reason
        for item in unmet:
            self.assertNotIn("; AND ", item)

    def test_the_refusal_carries_its_blocks_as_data(self) -> None:
        # The mechanism, exercised through the real ladder rather than a hand-built object:
        # `blocks` must match what the message claims, so the two can never disagree.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._two_suffix_free_gates(root)
            try:
                _quiet(tr.transition, root, "US0001", "In Progress", dry_run=True)
                self.fail("expected the ladder to refuse")
            except tr.GateRefusal as exc:
                self.assertEqual(len(exc.blocks), 2)
                self.assertIsInstance(exc, ValueError)   # every existing caller still catches
                stated = int(re.search(r"blocked \((\d+) requirement", str(exc)).group(1))
                self.assertEqual(stated, len(exc.blocks))

    def test_no_requirement_carries_the_ladders_join_token(self) -> None:
        # The observable symptom of re-parsing: a leaked `; AND ` inside an item.
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
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
        self.assertGreaterEqual(len(unmet), 2)
        for item in unmet:
            self.assertNotIn("; AND ", item, f"the join token leaked into an item: {item!r}")

    def test_the_reported_count_matches_the_gates_own_count(self) -> None:
        # The two numbers came from different places and could disagree; now they cannot.
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
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            try:
                _quiet(tr.transition, root, "BG0001", "Fixed")
                self.fail("expected the gate to refuse")
            except ValueError as exc:
                stated = int(re.search(r"blocked \((\d+) requirement", str(exc)).group(1))
        self.assertEqual(len(unmet), stated)

    def test_every_unmet_gate_is_listed_not_just_the_first(self) -> None:
        # The ladder collects all refusals into one message; the reporter must split them
        # back out rather than returning the joined blob as a single item.
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
            unmet = _quiet(tr.requirements, root, "BG0001", "Fixed")
            self.assertGreaterEqual(len(unmet), 2, f"expected several requirements, got {unmet}")
            joined = " ".join(unmet)
            self.assertIn("Verification depth", joined)
            self.assertIn("triage", joined.lower())


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

    def test_statically_undershooting_depth_refuses_before_any_write(self) -> None:
        # Critic repro: --depth smoke --status Verified is a pure function of the flags -
        # it must refuse with NO stamp and NO verdict row, not stamp-then-block.
        with tempfile.TemporaryDirectory() as d:
            root = self._bug(Path(d))
            before = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            rc = tr.main(["set", "--id", "BG0001", "--status", "Verified",
                          "--depth", "smoke", "--verdict", "approve",
                          "--reviewer", "r1", "--author", "a1", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            after = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)  # byte-identical: no stamp landed
            self.assertFalse((root / "sdlc-studio" / "reviews" / "critic-verdicts.md").exists())

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


class MetadataLineInjectionTests(unittest.TestCase):
    """Every writer of a metadata line inherits ONE refusal (`sdlc_md.require_single_line` in
    `_upsert_field`), rather than each caller remembering to escape. `annotate` guarded its own
    value; the triage stamps went straight to the writer and did not, so a triage record could
    write arbitrary metadata lines into the artefact it was closing."""

    BREAK = "\n> **Evil:** injected"

    def test_triaged_by_cannot_inject_a_metadata_line(self) -> None:
        # the fixture reproduction: --triaged-by $'Dani Okafor; human; v1\n> **Evil:** injected'
        # stamped a `> **Evil:**` line that `extract_field` read back
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "BG0001", "Open",
                              triaged_by="Dani Okafor; human; v1" + self.BREAK)
            self.assertIn("single line", str(cm.exception))
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIsNone(tr.sdlc_md.extract_field(text, "Evil"))
            self.assertNotIn("Evil", text)

    def test_triage_severity_cannot_inject_a_metadata_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.transition(root, "BG0001", "Open", triaged_by="Knox; agent; 1",
                              triage_severity="low" + self.BREAK)
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertNotIn("Evil", text)

    def test_the_whole_line_breaking_class_is_refused_at_the_writer(self) -> None:
        for ch in ("\n", "\r", "\v", "\f", "\x1c", "\x1d", "\x1e", "\x85",
                   "\u2028", "\u2029", "\x00"):
            with self.subTest(ch=repr(ch)):
                with self.assertRaises(ValueError):
                    tr._upsert_field("# x\n\n> **Status:** Open\n", "Triaged-by",
                                     f"Knox{ch}> **Evil:** injected")
                with self.assertRaises(ValueError):
                    tr._upsert_field("# x\n\n> **Status:** Open\n", f"Bad{ch}Field", "v")

    def test_annotate_still_refuses_and_a_clean_stamp_still_lands(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _v3_bug_repo(Path(d))
            with self.assertRaises(ValueError):
                tr.annotate(root, "BG0001", "Verification depth", "functional" + self.BREAK)
            res = tr.transition(root, "BG0001", "Open", triaged_by="Knox; agent; 1",
                                triage_severity="low")
            self.assertEqual(res["to"], "Open")
            text = (root / "sdlc-studio" / "bugs" / "BG0001-x.md").read_text(encoding="utf-8")
            self.assertIn("> **Triaged-by:** Knox; agent; 1", text)
            self.assertIn("> **Triage-severity:** low", text)


class AcFingerprintFreshnessTests(unittest.TestCase):
    """US0213: freshness must be judged on what the verifier ran against, not on mtime.

    A Status transition, a Revision History row, and verify_ac's own `**Verified:**` stamps
    all bump mtime while leaving every AC and verifier untouched - under the mtime rule a
    correct green was rejected as "edited after it was last verified", forcing a re-run that
    could only ever produce the same result."""

    STORY = ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
             "### AC1: it works\n- **Verify:** shell true\n")

    def _root(self, d, body=None):
        root = Path(d)
        sd = root / "sdlc-studio" / "stories"
        sd.mkdir(parents=True, exist_ok=True)
        (sd / "US0001-x.md").write_text(body or self.STORY, encoding="utf-8")
        (sd / "_index.md").write_text(
            "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Ready | 1 |\n"
            "| Done | 0 |\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [US0001](US0001-x.md) | s | Ready |\n", encoding="utf-8")
        return root

    def _report(self, root, entry):
        rp = root / "sdlc-studio" / ".local" / "verify-report.json"
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps({"stories": {"US0001-x": entry}}), encoding="utf-8")

    def _fp(self, text):
        import verify_ac
        return verify_ac.ac_fingerprint(text)

    def _green(self, text, **over):
        return {"failed": 0, "stale": 0, "failures": [],
                "verified_at": "2000-01-01T00:00:00Z",      # long in the past: mtime WILL be newer
                "ac_fingerprint": self._fp(text), **over}

    def test_metadata_edit_stays_fresh(self) -> None:
        """AC1: an edit outside the AC section must not invalidate the green."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            self._report(root, self._green(self.STORY))
            # touch metadata only - a Revision History row, exactly what closing paperwork adds
            p = root / "sdlc-studio" / "stories" / "US0001-x.md"
            p.write_text(self.STORY + "\n## Revision History\n\n| 2026-07-18 | me | edited |\n",
                         encoding="utf-8")
            res = tr.transition(root, "US0001", "Done")
            self.assertEqual(res["to"], "Done")

    def test_ac_edits_invalidate(self) -> None:
        """AC2: retitling an AC, re-pointing a verifier, or adding an AC each block."""
        mutations = {
            "retitled": "### AC1: it works differently\n- **Verify:** shell true\n",
            "re-pointed": "### AC1: it works\n- **Verify:** shell false\n",
            "added": "### AC1: it works\n- **Verify:** shell true\n\n"
                     "### AC2: more\n- **Verify:** shell true\n",
        }
        for label, acs in mutations.items():
            with self.subTest(label), tempfile.TemporaryDirectory() as d:
                root = self._root(d)
                self._report(root, self._green(self.STORY))
                edited = ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n" + acs)
                (root / "sdlc-studio" / "stories" / "US0001-x.md").write_text(edited, encoding="utf-8")
                with self.assertRaises(ValueError):
                    tr.transition(root, "US0001", "Done")

    def test_legacy_report_falls_back_to_mtime(self) -> None:
        """AC3: a pre-fingerprint report must not silently pass - mtime still governs."""
        with tempfile.TemporaryDirectory() as d:
            root = self._root(d)
            entry = self._green(self.STORY)
            entry.pop("ac_fingerprint")          # written before the field existed
            self._report(root, entry)
            with self.assertRaises(ValueError):  # story mtime is newer than verified_at
                tr.transition(root, "US0001", "Done")


class AcFingerprintTests(unittest.TestCase):
    """US0213 AC4: the fingerprint covers ACs and verifiers, and nothing else."""

    BASE = ("# US0001: s\n\n> **Status:** Ready\n\n## Acceptance Criteria\n\n"
            "### AC1: it works\n- **Verify:** shell true\n")

    def _fp(self, text):
        import verify_ac
        return verify_ac.ac_fingerprint(text)

    def test_metadata_does_not_change_the_fingerprint(self) -> None:
        noise = self.BASE.replace("**Status:** Ready", "**Status:** Done") + \
            "\n## Revision History\n\n| d | a | c |\n"
        self.assertEqual(self._fp(self.BASE), self._fp(noise))

    def test_verified_stamp_does_not_change_the_fingerprint(self) -> None:
        stamped = self.BASE + "- **Verified:** yes (2026-07-18)\n"
        self.assertEqual(self._fp(self.BASE), self._fp(stamped))

    def test_verifier_change_changes_the_fingerprint(self) -> None:
        self.assertNotEqual(self._fp(self.BASE),
                            self._fp(self.BASE.replace("shell true", "shell false")))

    def test_ac_count_change_changes_the_fingerprint(self) -> None:
        self.assertNotEqual(
            self._fp(self.BASE),
            self._fp(self.BASE + "\n### AC2: more\n- **Verify:** shell true\n"))


def _rfc_repo(root: Path, status: str = "In Review", rows: str | None = None,
              override: str | None = None) -> Path:
    """An RFC with an Open Decisions table, the shape reference-rfc.md's accept step reads."""
    d = root / "sdlc-studio" / "rfcs"
    d.mkdir(parents=True, exist_ok=True)
    body = f"# RFC0001: r\n\n> **Status:** {status}\n"
    if override:
        body += f"> **Decision-Override:** {override}\n"
    table = rows if rows is not None else "| D1 | Act on this finding or keep status quo | Open |\n"
    body += ("\n## Summary\n\nx\n\n## Open Decisions\n\n"
             "| # | Decision | Status |\n| --- | --- | --- |\n" + table)
    (d / "RFC0001-r.md").write_text(body, encoding="utf-8")
    (d / "_index.md").write_text(
        "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [RFC0001](RFC0001-r.md) | r | {status} |\n", encoding="utf-8")
    return root


class RfcOpenDecisionGateTests(unittest.TestCase):
    """US0244 AC1: an RFC cannot reach Accepted while a decision row is still Open.

    reference-rfc.md's accept step already forbade this in prose, and six RFCs were
    Accepted, decomposed and delivered carrying nothing but the boilerplate Open row.
    A gate that lives only in prose fires when somebody remembers.
    """

    def test_open_decision_refuses_the_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("D1", str(cm.exception))
            self.assertIn("Status:** In Review", _read(root, "rfcs", "RFC0001-r.md"))

    def test_every_open_row_is_named_not_just_the_first(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows=(
                "| D1 | first | Open |\n| D2 | second | Closed |\n| D3 | third | Open |\n"))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            msg = str(cm.exception)
            self.assertIn("D1", msg)
            self.assertIn("D3", msg)
            self.assertNotIn("D2", msg)  # a Closed row is not a blocker

    def test_all_decisions_closed_lets_the_transition_through(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows="| D1 | settled | Closed |\n")
            tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))

    def test_an_annotated_open_cell_still_counts_as_open(self) -> None:
        """A status cell carrying its reasoning is the shape real RFCs use.

        RFC0042 D2 reads `Open - the mechanism detail for the blocking lane`. A reader that
        demands the bare word misses it and reports the file clean - a false negative in the
        gate, which is worse than the prose rule it replaced.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows=(
                "| D1 | Enforcement mechanism | Resolved: option D (soft nudge + blocking lane) |\n"
                "| D2 | How to detect the trigger | Open - the mechanism detail for the lane |\n"))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            msg = str(cm.exception)
            self.assertIn("D2", msg)
            self.assertNotIn("D1", msg)  # 'Resolved: ...' is settled, not open

    def test_the_reader_is_not_locked_to_one_table_shape(self) -> None:
        """Four false negatives found by the closing review, all the same root cause.

        The reader hardcoded three columns, split on every pipe, matched only `## `
        headings, and accepted only the bare leading word `Open`. Each is a way for a real
        Open decision to pass the gate silently - the outcome the docstring calls worse
        than the prose rule it replaced, because it also looks like proof.
        """
        shapes = {
            "four columns": ("| # | Decision | Options | Status |\n| --- | --- | --- | --- |\n"
                             "| D1 | which store | sqlite/postgres | Open |\n"),
            "pipe in a cell": ("| # | Decision | Status |\n| --- | --- | --- |\n"
                               r"| D1 | keep a \| b | Open |" + "\n"),
            "unresolved": ("| # | Decision | Status |\n| --- | --- | --- |\n"
                           "| D1 | which store | Unresolved |\n"),
            "pending": ("| # | Decision | Status |\n| --- | --- | --- |\n"
                        "| D1 | which store | Pending operator |\n"),
        }
        for name, rows in shapes.items():
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as d:
                root = _rfc_repo(Path(d), rows=rows)
                with self.assertRaises(ValueError, msg=f"{name}: Open decision passed"):
                    tr.transition(root, "RFC0001", "Accepted")

    def test_a_comment_in_a_fenced_block_does_not_end_the_section(self) -> None:
        """Widening the heading match to any line starting with `#` created a NEW bypass.

        A shell comment inside a fenced code block begins with `#`, contains no "decision",
        and so switched the section OFF - every Open row after it invisible. The pre-repair
        code was correct here. Only a real ATX heading is a boundary, and nothing inside a
        fence is a heading at all.
        """
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), rows=(
                "```bash\n# regenerate the table\n```\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n| D1 | which store | Open |\n"))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("D1", str(cm.exception))

    def test_fence_handling_cannot_hide_the_decisions_section(self) -> None:
        """Fence tracking must never DISABLE the gate - the round 2 repair did exactly that.

        A naive `in_fence = not in_fence` toggle treats any fence-like line as a delimiter, so
        an unclosed fence, or a nested longer fence containing a shorter one, left the tracker
        inside a fence at EOF and made the whole decisions section invisible. That is a wider
        bypass than the `#`-in-a-fence case it was fixing, and the code it replaced caught all
        of these. Two guards now: proper CommonMark matching (a fence closes only on the same
        character at the same length or longer), and a fail-closed re-scan if the tracker still
        ends inside a fence, because unparseable markdown must not read as no open decisions.
        """
        table = ("\n| # | Decision | Status |\n| --- | --- | --- |\n"
                 "| D1 | which store | Open |\n")
        shapes = {
            "unclosed fence before the section": "```bash\necho hi\n\n## Open Decisions\n" + table,
            "nested four-backtick fence": (
                "````markdown\n```bash\n````\n\n## Open Decisions\n" + table),
            "tilde fence never closed": "~~~\nstuff\n\n## Open Decisions\n" + table,
            "fence opened inside the section": (
                "## Open Decisions\n\n```bash\n# regenerate\n```\n" + table),
            # The fail-closed re-scan dropped the FENCE rule but kept the SECTION rule, so a
            # `#` comment inside the unterminated fence ended the section and hid every row
            # after it. The fallback then returned "no open decisions" for the exact document
            # it exists to catch: the gate advertised fail-closed and failed OPEN. The two
            # structural signals fail together, so the fallback now drops both.
            "unclosed fence whose body holds a # comment": (
                "## Open Decisions\n\n```bash\n# regenerate the table\n" + table),
            "unclosed tilde fence whose body holds a # comment": (
                "## Open Decisions\n\n~~~bash\n# regenerate the table\n" + table),
        }
        for name, body in shapes.items():
            with self.subTest(shape=name), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                rd = root / "sdlc-studio" / "rfcs"
                rd.mkdir(parents=True)
                (rd / "RFC0001-r.md").write_text(
                    "# RFC0001: r\n\n> **Status:** In Review\n\n" + body, encoding="utf-8")
                (rd / "_index.md").write_text(
                    "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                    "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
                with self.assertRaises(ValueError, msg=f"{name}: gate bypassed"):
                    tr.transition(root, "RFC0001", "Accepted")

    def test_a_fence_hiding_only_some_rows_still_names_every_open_decision(self) -> None:
        """The fail-closed re-scan must fire on an unterminated fence, not only on an empty read.

        The guard was `fence is not None and not open_rows`, so the fallback ran only when the
        main scan found NOTHING. With one open row before a broken fence and another after it,
        the first is found, `not open_rows` is False, the re-scan never fires, and the caller
        gets an INCOMPLETE list. Both callers print that list, so the operator is told the RFC
        carries one open decision, D1, when it carries two.

        The gate still blocks and it converges - closing D1 and re-running surfaces D7 - so this
        costs a round trip rather than correctness. It is still a false completeness claim in
        operator-facing output (BG0207).
        """
        body = ("## Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | which store | Open |\n\n"
                "```bash\necho 'never closed'\n\n"
                "| D7 | which format | Open |\n")
        self.assertEqual(tr._rfc_open_decisions(body), ["D1", "D7"])

    def test_commonmark_fence_matching_is_pinned_independently_of_the_fallback(self) -> None:
        """The CommonMark `(char, length)` rule needs a test the FALLBACK cannot satisfy.

        Every other fence test asserts the gate BLOCKS, and the fail-closed re-scan blocks on
        its own - so reverting the matcher to a naive `in_fence = not in_fence` toggle left
        them all green and the headline guard untested. Only a case where the correct answer
        is "no open decisions" separates the two: a well-formed nested fence, closed properly,
        holding an EXAMPLE row.

        Correct CommonMark: ```` opens, the inner ``` is content, the trailing ```` closes.
        The tracker ends outside any fence, the example row was skipped, the gate passes.
        Under the naive toggle the inner ``` counts as a delimiter, the file ends inside a
        fence, the fail-closed re-scan fires and reads the example row as real - so accepting
        this RFC raises. The mutant FAILS this test where it passes all the others.
        """
        body = ("## Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n"
                "| D1 | which store | Accepted |\n\n"
                "````markdown\n```text\n| D9 | an example row, not a decision | Open |\n"
                "```\n````\n")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "rfcs"
            rd.mkdir(parents=True)
            (rd / "RFC0001-r.md").write_text(
                "# RFC0001: r\n\n> **Status:** In Review\n\n" + body, encoding="utf-8")
            (rd / "_index.md").write_text(
                "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
            tr.transition(root, "RFC0001", "Accepted")   # must NOT raise

    def test_a_hash_that_is_not_a_heading_does_not_end_the_section(self) -> None:
        """`#42` and `#!/bin/sh` start with `#` but are not headings."""
        for line in ("#42 is the issue this row came from", "#!/usr/bin/env bash"):
            with self.subTest(line=line), tempfile.TemporaryDirectory() as d:
                root = _rfc_repo(Path(d), rows=(
                    f"{line}\n\n| # | Decision | Status |\n| --- | --- | --- |\n"
                    "| D1 | q | Open |\n"))
                with self.assertRaises(ValueError):
                    tr.transition(root, "RFC0001", "Accepted")

    def test_a_decisions_section_at_any_heading_level_is_read(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rd = root / "sdlc-studio" / "rfcs"
            rd.mkdir(parents=True)
            (rd / "RFC0001-r.md").write_text(
                "# RFC0001: r\n\n> **Status:** In Review\n\n### Open Decisions\n\n"
                "| # | Decision | Status |\n| --- | --- | --- |\n| D1 | q | Open |\n",
                encoding="utf-8")
            (rd / "_index.md").write_text(
                "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                tr.transition(root, "RFC0001", "Accepted")

    def test_a_settled_row_still_passes_in_every_shape(self) -> None:
        """Widening what counts as open must not start blocking settled work."""
        for cell in ("Closed", "Resolved: option D", "Superseded by RFC0050", "Done"):
            with self.subTest(cell=cell), tempfile.TemporaryDirectory() as d:
                root = _rfc_repo(Path(d), rows=f"| D1 | q | {cell} |\n")
                tr.transition(root, "RFC0001", "Accepted")
                self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))

    def test_an_rfc_with_no_decision_table_is_unaffected(self) -> None:
        """The gate must not invent a blocker for an RFC that never had a table."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            dd = root / "sdlc-studio" / "rfcs"
            dd.mkdir(parents=True)
            (dd / "RFC0001-r.md").write_text(
                "# RFC0001: r\n\n> **Status:** In Review\n\n## Summary\n\nx\n", encoding="utf-8")
            (dd / "_index.md").write_text(
                "# RFCs\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [RFC0001](RFC0001-r.md) | r | In Review |\n", encoding="utf-8")
            tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))


class RfcDecisionOverrideTests(unittest.TestCase):
    """US0244 AC2: the only escape is a RECORDED override, never a bare --force.

    Mirrors the Plan-Review-Override convention: a skip that leaves a reason in the
    file is auditable, a --force is not.
    """

    def test_recorded_override_permits_the_transition(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), override="D1 settled verbally at the 07-19 review")
            res = tr.transition(root, "RFC0001", "Accepted")
            self.assertIn("Status:** Accepted", _read(root, "rfcs", "RFC0001-r.md"))
            self.assertIn("settled verbally", (res.get("warning") or ""))

    def test_bare_force_does_not_bypass_the_gate(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d))
            with self.assertRaises(ValueError) as cm:
                tr.transition(root, "RFC0001", "Accepted", force=True)
            self.assertIn("Decision-Override", str(cm.exception))
            self.assertIn("Status:** In Review", _read(root, "rfcs", "RFC0001-r.md"))

    def test_an_empty_override_is_not_an_override(self) -> None:
        """A field present but blank records no reason, so it cannot buy a skip."""
        with tempfile.TemporaryDirectory() as d:
            root = _rfc_repo(Path(d), override="   ")
            with self.assertRaises(ValueError):
                tr.transition(root, "RFC0001", "Accepted")


if __name__ == "__main__":
    unittest.main()
