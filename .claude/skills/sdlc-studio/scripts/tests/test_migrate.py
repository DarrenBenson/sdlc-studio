"""Tests for the migrate orchestrator (migrate.py) - RFC0041, US0154-US0156.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
migrate = _load("migrate")


def _w(root: Path, rel: str, text: str) -> None:
    p = root / "sdlc-studio" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _mixed(root: Path) -> None:
    """A project with one of each: a legacy-Effort container (deterministic Size), an accepted
    childless request (needs refine), a childless Triaging Issue (needs triage), a legacy-Effort
    delivery unit (needs resize)."""
    _w(root, "change-requests/CR0001-x.md", "# CR-0001: legacy\n\n> **Status:** Approved\n> **Effort:** M\n")
    _w(root, "change-requests/CR0002-y.md", "# CR-0002: accepted\n\n> **Status:** Approved\n> **Size:** M\n")
    _w(root, "issues/IS0001-z.md", "# IS0001: untriaged\n\n> **Status:** Triaging\n> **Severity:** High\n> **Size:** M\n")
    _w(root, "bugs/BG0001-b.md", "# BG0001: bug\n\n> **Status:** Open\n> **Effort:** S\n> **Severity:** Low\n")


class MigrateTests(unittest.TestCase):
    def test_non_skill_repo_is_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            res = migrate.migrate(Path(d))
            self.assertFalse(res["applicable"])

    def test_dry_run_aggregates_deterministic_and_needs_human_and_writes_nothing(self) -> None:
        from lib import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root)   # dry-run
            self.assertTrue(res["applicable"])
            self.assertFalse(res["applied"])
            # deterministic includes the container's sizing conversion + the conventions gaps
            det = {x.get("id") or x.get("kind") for x in res["deterministic"]}
            self.assertIn("CR0001", det)
            # nothing written
            self.assertFalse((root / "sdlc-studio" / ".version").exists())
            self.assertIsNone(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text()))

    def test_the_artefact_sweep_names_each_ceremony_with_a_command(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root)
            kinds = {h["kind"]: h for h in res["needs_human"] if h.get("id")}
            self.assertIn("needs-refine", kinds)          # CR0002 (and CR0001) accepted, childless
            self.assertIn("needs-triage", kinds)          # IS0001
            self.assertIn("needs-resize", kinds)          # BG0001 legacy Effort
            # each carries the exact command to resolve it
            refine = next(h for h in res["needs_human"] if h["kind"] == "needs-refine")
            self.assertIn("refine apply --request", refine["command"])
            triage = next(h for h in res["needs_human"] if h["kind"] == "needs-triage")
            self.assertIn("triage apply --issue IS0001", triage["command"])

    def test_apply_writes_only_the_deterministic_set(self) -> None:
        from lib import sdlc_md
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root, apply=True)
            self.assertTrue(res["applied"])
            # deterministic set written: a real version (BG0150 - never "unknown"), config, Size
            ver = (root / "sdlc-studio" / ".version").read_text()
            self.assertIn("skill_version:", ver)
            self.assertNotIn("unknown", ver)
            self.assertEqual(sdlc_md.read_size(
                (root / "sdlc-studio" / "change-requests" / "CR0001-x.md").read_text()), "M")
            # the needs-human items are NEVER auto-applied, checked at the FILE level:
            # the accepted CR is still childless, the Issue still untriaged, the bug still no Points
            self.assertEqual(sdlc_md.decomposed_ids(
                (root / "sdlc-studio" / "change-requests" / "CR0002-y.md").read_text()), [])
            issue = (root / "sdlc-studio" / "issues" / "IS0001-z.md").read_text()
            self.assertEqual(sdlc_md.decomposed_ids(issue), [])
            self.assertEqual(sdlc_md.extract_field(issue, "Status"), "Triaging")   # not triaged
            self.assertIsNone(sdlc_md.read_points(
                (root / "sdlc-studio" / "bugs" / "BG0001-b.md").read_text()))

    def test_apply_deterministic_list_has_no_advisories_or_warnings(self) -> None:
        # the honest split: an advisory (team-offer) or a warning (BG0150 not-stamped) must NEVER be
        # reported as an applied deterministic upgrade - only real changes are.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            res = migrate.migrate(root, apply=True)
            for det in res["deterministic"]:
                self.assertNotIn("WARNING", det["detail"])
                self.assertNotIn("run persona", det["detail"])
                self.assertNotIn("uncovered", det["detail"])
                self.assertNotIn("SKIPPED", det["detail"])

    def test_dry_run_and_apply_agree_on_the_deterministic_count(self) -> None:
        # dry-run is a faithful preview: applying the same tree reports the same deterministic set,
        # classified from the same source (audit), not from apply's free-text actions.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            preview = migrate.migrate(root)["summary"]["deterministic"]
            applied = migrate.migrate(root, apply=True)["summary"]["deterministic"]
            self.assertEqual(preview, applied)

    def test_unreadable_install_version_is_needs_human_not_deterministic(self) -> None:
        # BG0150 through the orchestrator: when the install version cannot be read, the version is a
        # needs-human blocker in the report - never a promised/applied deterministic upgrade.
        vc = migrate.project_upgrade.version_check
        orig = vc.installed_version
        vc.installed_version = lambda *a, **k: None
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _mixed(root)
                res = migrate.migrate(root)   # dry-run
                det_kinds = {x.get("kind") for x in res["deterministic"]}
                self.assertNotIn("missing-version", det_kinds)   # not promised
                hk = {h["kind"] for h in res["needs_human"]}
                self.assertIn("version-unresolvable", hk)        # reported as a blocker
        finally:
            vc.installed_version = orig

    def test_render_has_both_sections(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _mixed(root)
            text = migrate.render(migrate.migrate(root))
            self.assertIn("Deterministic", text)
            self.assertIn("Needs a human", text)
            self.assertIn("refine apply --request", text)


if __name__ == "__main__":
    unittest.main()
