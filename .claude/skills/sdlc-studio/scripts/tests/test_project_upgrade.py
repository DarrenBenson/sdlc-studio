"""Unit tests for project_upgrade.py - migrate a consuming project to current conventions (CR0062)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load():
    spec = importlib.util.spec_from_file_location("project_upgrade", SCR / "project_upgrade.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["project_upgrade"] = mod
    spec.loader.exec_module(mod)
    return mod


pu = _load()
import version_check  # noqa: E402
INSTALLED = version_check.installed_version(version_check.skill_root()) or "2.3.0"


def _project(d, *, version=None, personas=None, story_id=None):
    """Minimal consuming project under tmp dir `d`. version=(schema, skill) writes .version."""
    sd = Path(d) / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    if version is not None:
        schema, skill = version
        (sd / ".version").write_text(
            f"schema_version: {schema}\nskill_version: \"{skill}\"\n", encoding="utf-8")
    if story_id is not None:
        sdir = sd / "stories"; sdir.mkdir(exist_ok=True)
        (sdir / f"US{story_id:04d}-x.md").write_text(
            f"# US{story_id:04d}: x\n\n> **Status:** Done\n", encoding="utf-8")
    if personas:  # personas = list of (relpath, body)
        for rel, body in personas:
            f = sd / "personas" / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(body, encoding="utf-8")
    return sd


class DetectTests(unittest.TestCase):
    def test_no_version_is_behind(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            self.assertTrue(pu.detect(d)["behind"])

    def test_current_not_behind(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))
            self.assertFalse(pu.detect(d)["behind"])

    def test_old_schema_is_behind(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(1, INSTALLED))
            self.assertTrue(pu.detect(d)["behind"])


class AuditTests(unittest.TestCase):
    def test_flags_missing_config_and_version(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            kinds = [f["kind"] for f in pu.audit(d)["auto"]]
            self.assertIn("missing-config", kinds)
            self.assertIn("missing-version", kinds)

    def test_old_nested_personas_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, personas=[("team/product/sarah.md", "# Sarah\n\n## Psychology\n\nx\n")])
            self.assertTrue(any(f["kind"] == "personas" for f in pu.audit(d)["manual"]))

    def test_old_persona_headings_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, personas=[("emma.md", "# Emma\n\n## Backstory\n\nx\n")])
            self.assertTrue(pu._old_persona_model(Path(d) / "sdlc-studio"))

    def test_cooper_persona_not_flagged_as_old(self):
        with tempfile.TemporaryDirectory() as d:
            body = ("# Maya\n\n## Quick Reference\n\n| **Cast role** | Primary |\n\n"
                    "## Who They Are\n\nx\n## End Goals\n\nx\n## Experience Goals\n\nx\n"
                    "## Behaviours & Context\n\nx\n## Frustrations\n\nx\n## Scenario\n\nx\n")
            _project(d, personas=[("maya.md", body)])
            self.assertFalse(pu._old_persona_model(Path(d) / "sdlc-studio"))


class ApplyTests(unittest.TestCase):
    def test_apply_creates_config_with_cutoff_and_version(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, story_id=5)  # max id -> cutoff 5
            actions = pu.apply(d)
            sd = Path(d) / "sdlc-studio"
            self.assertTrue((sd / ".config.yaml").exists())
            self.assertIn("adopt_after: 5", (sd / ".config.yaml").read_text())
            self.assertTrue((sd / ".version").exists())
            self.assertIn(f'skill_version: "{INSTALLED}"', (sd / ".version").read_text())
            self.assertTrue(any("config.yaml" in a for a in actions))

    def test_apply_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))
            pu.apply(d)
            self.assertEqual(pu.apply(d), [])  # second run is a no-op

    def test_apply_updates_stale_version(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(pu.CURRENT_SCHEMA, "1.0.0"))
            actions = pu.apply(d)
            self.assertIn(f'skill_version: "{INSTALLED}"', (Path(d) / "sdlc-studio" / ".version").read_text())
            self.assertTrue(any("updated" in a and ".version" in a for a in actions))

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            import hashlib
            def snap():
                return {str(f): hashlib.sha256(f.read_bytes()).hexdigest()
                        for f in Path(d).rglob("*") if f.is_file()}
            before = snap()
            pu.detect(d); pu.audit(d)            # read-only paths
            pu.main(["--root", d, "--format", "json"])  # dry-run (no --apply)
            pu.main(["--root", d])
            self.assertEqual(before, snap())     # byte-identical: dry-run writes nothing


class SafetyAndReconcileTests(unittest.TestCase):
    def test_apply_refuses_non_project(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                pu.apply(d)                       # no sdlc-studio/ dir
            self.assertEqual(pu.main(["--root", d, "--apply"]), 1)  # CLI exits 1, no scaffold
            self.assertFalse((Path(d) / "sdlc-studio").exists())

    def test_apply_preserves_existing_config(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))
            (sd / ".config.yaml").write_text("# custom\nprovenance:\n  enforce: true\n", encoding="utf-8")
            pu.apply(d)
            self.assertEqual((sd / ".config.yaml").read_text(), "# custom\nprovenance:\n  enforce: true\n")

    def test_apply_does_not_bundle_reconcile_by_default(self):
        # BG0029: an upgrade must not rewrite indexes - reconcile is off unless explicitly requested.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED), story_id=1)  # file Status: Done
            idx = sd / "stories" / "_index.md"
            idx.write_text(
                "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | x | In Progress |\n", encoding="utf-8")  # row drifts from file
            actions = pu.apply(d)  # default: no reconcile
            self.assertFalse(any("reconcil" in a for a in actions))
            self.assertIn("In Progress", idx.read_text())  # index left untouched

    def test_apply_with_reconcile_opt_in_runs_it(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED), story_id=1)
            idx = sd / "stories" / "_index.md"
            idx.write_text(
                "# Index\n\n## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
                "| [US0001](US0001-x.md) | x | In Progress |\n", encoding="utf-8")
            actions = pu.apply(d, with_reconcile=True)
            self.assertTrue(any("reconcil" in a for a in actions))
            self.assertIn("Done", idx.read_text())

    def test_current_version_missing_config_still_applies(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))  # current, but no .config.yaml
            self.assertEqual(pu.main(["--root", d, "--apply"]), 0)
            self.assertTrue((sd / ".config.yaml").exists())          # not stranded by the "behind" gate

    def test_stale_version_reported_as_auto(self):
        # BG0025: a present-but-stale .version is auto-correctable (apply bumps it), so the dry-run
        # must report it - not silently omit it.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, "1.6.0"))
            (sd / ".config.yaml").write_text("provenance:\n  adopt_after: 0\n", encoding="utf-8")
            self.assertIn("stale-version", [f["kind"] for f in pu.audit(d)["auto"]])

    def test_current_version_no_stale_finding(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))
            (sd / ".config.yaml").write_text("provenance:\n  adopt_after: 0\n", encoding="utf-8")
            kinds = [f["kind"] for f in pu.audit(d)["auto"]]
            self.assertNotIn("stale-version", kinds)
            self.assertNotIn("missing-version", kinds)

    def test_seats_charters_and_guide_not_flagged_old(self):
        # BG0027: review-seat charters (seats/) + a consult-guide are not "old design personas"
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED), personas=[
                ("seats/sarah.md", "# Sarah\n\n## Role & Mandate\n\nx\n## Lens\n\nx\n## Shadow\n\nx\n"),
                ("consult-guide.md", "# Consult guide\n\nrun consult team for a review\n"),
                ("maya.md", "# Maya\n\n## Quick Reference\n\n| **Cast role** | Primary |\n\n## End Goals\n\nx\n")])
            self.assertFalse(pu._old_persona_model(Path(d) / "sdlc-studio"))

    def test_old_top_level_persona_still_detected(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, personas=[("sarah.md", "# Sarah\n\n## Psychology\n\nx\n")])  # old heading
            self.assertTrue(pu._old_persona_model(Path(d) / "sdlc-studio"))

    def test_version_bump_preserves_created_at(self):
        # BG0030: bumping an existing .version keeps author fields (e.g. created_at) the template drops
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, "1.4.0"))  # stale skill -> bump
            (sd / ".version").write_text(
                'schema_version: 2\ncreated_at: 2025-01-01\nskill_version: "1.4.0"\n', encoding="utf-8")
            pu.apply(d)
            txt = (sd / ".version").read_text()
            self.assertIn("created_at: 2025-01-01", txt)            # preserved
            self.assertIn(f'skill_version: "{INSTALLED}"', txt)     # bumped
            self.assertIn("upgraded_from: 1.4.0", txt)

    def test_apply_date_is_injectable_on_bump(self):
        # CR0071: deterministic date for tests - bump path
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, "1.4.0"))
            pu.apply(d, today="2025-09-09")
            self.assertIn("upgraded_at: 2025-09-09", (sd / ".version").read_text())

    def test_apply_date_is_injectable_on_create(self):
        # CR0071: deterministic date for tests - new-file path
        with tempfile.TemporaryDirectory() as d:
            _project(d)  # no .version -> created
            pu.apply(d, today="2025-09-09")
            self.assertIn("2025-09-09", (Path(d) / "sdlc-studio" / ".version").read_text())


class AmigoDefaultsTests(unittest.TestCase):
    # CR0119: project upgrade installs the v3.1 default amigo cards when absent, idempotently.
    AMIGOS = ("engineering.md", "qa.md", "product.md")

    def test_apply_installs_amigos_when_absent(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            actions = pu.apply(d)
            adir = sd / "personas" / "amigos"
            for name in self.AMIGOS:
                self.assertTrue((adir / name).exists(), f"{name} not installed")
            # the cards match the skill's shipped source byte-for-byte
            src = pu._amigos_source()
            self.assertEqual((adir / "engineering.md").read_text(encoding="utf-8"),
                             (src / "engineering.md").read_text(encoding="utf-8"))
            self.assertTrue(any("amigo" in a.lower() for a in actions))

    def test_apply_skips_customised_amigo(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            adir = sd / "personas" / "amigos"
            adir.mkdir(parents=True, exist_ok=True)
            custom = "# Our own engineer\n\nproject-specific amigo\n"
            (adir / "engineering.md").write_text(custom, encoding="utf-8")
            pu.apply(d)
            # customised card untouched
            self.assertEqual((adir / "engineering.md").read_text(encoding="utf-8"), custom)
            # the missing ones still get installed
            self.assertTrue((adir / "qa.md").exists())
            self.assertTrue((adir / "product.md").exists())

    def test_apply_idempotent_for_amigos(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            pu.apply(d)
            self.assertEqual(pu.apply(d), [])  # second run installs nothing new

    def test_audit_flags_missing_amigos(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            kinds = [f["kind"] for f in pu.audit(d)["auto"]]
            self.assertIn("missing-amigos", kinds)

    def test_audit_no_flag_when_all_amigos_present(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))
            adir = sd / "personas" / "amigos"
            adir.mkdir(parents=True, exist_ok=True)
            for name in self.AMIGOS:
                (adir / name).write_text("# x\n", encoding="utf-8")
            kinds = [f["kind"] for f in pu.audit(d)["auto"]]
            self.assertNotIn("missing-amigos", kinds)


if __name__ == "__main__":
    unittest.main()
