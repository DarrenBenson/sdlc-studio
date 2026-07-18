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


import re  # noqa: E402


class CurrentSchemaCoherenceTests(unittest.TestCase):
    """BG0189: the skill must give ONE answer for 'current schema version'. `init` seeds a new
    project from templates/config.yaml, so that file's schema_version is the current version; an
    upgrade computed against a stale `CURRENT_SCHEMA` would move a project to the wrong version.
    config-defaults.yaml stays the explicitly-named FALLBACK for un-stamped legacy workspaces."""

    def _template_schema(self, name: str) -> int:
        text = (SCR.parent / "templates" / name).read_text(encoding="utf-8")
        m = re.search(r"^schema_version:\s*(\d+)", text, re.M)
        self.assertIsNotNone(m, f"{name} has no schema_version")
        return int(m.group(1))

    def test_current_schema_equals_the_init_seed_template(self) -> None:
        """CURRENT_SCHEMA (the upgrade target) == templates/config.yaml (what init copies in)."""
        self.assertEqual(pu.CURRENT_SCHEMA, self._template_schema("config.yaml"))

    def test_current_schema_is_derived_not_the_fallback(self) -> None:
        """The seed (config.yaml) leads current; config-defaults.yaml is only the legacy fallback,
        and the two intentionally differ - so CURRENT_SCHEMA must not be the fallback's value."""
        self.assertGreater(pu.CURRENT_SCHEMA, self._template_schema("config-defaults.yaml"))

    def test_sdlc_md_current_schema_helper_matches_the_template(self) -> None:
        from lib import sdlc_md  # noqa: PLC0415
        self.assertEqual(sdlc_md.current_schema(), self._template_schema("config.yaml"))


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


class AuditApplyConsistencyTests(unittest.TestCase):
    """BG0189 regression guard: audit()'s auto-fix list must match what apply() actually does.
    A stamped v2 project on the current skill declines v3 legitimately - its `.version` is NOT
    stale, apply() is a no-op on it, and audit must not advertise a stale-version stamp bump apply
    will never perform (else the finding is permanent and uncorrectable)."""

    def test_v2_project_on_current_skill_has_no_uncorrectable_stale_version(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(2, INSTALLED))     # v2, current skill, no .config.yaml (schema 2)
            kinds = [f["kind"] for f in pu.audit(d)["auto"]]
            self.assertNotIn("stale-version", kinds)
            ver = Path(d) / "sdlc-studio" / ".version"
            before = ver.read_text(encoding="utf-8")
            pu.apply(Path(d))                       # apply must be a no-op on .version
            self.assertEqual(ver.read_text(encoding="utf-8"), before)
            # dry-run matches apply, permanently: re-auditing after apply is still clean
            self.assertNotIn("stale-version", [f["kind"] for f in pu.audit(d)["auto"]])

    def test_a_genuinely_stale_skill_still_flags_and_apply_clears_it(self) -> None:
        # The clause must still fire for what apply DOES fix - a lagging skill version.
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(2, "1.0.0"))       # skill behind the installed one
            self.assertIn("stale-version", [f["kind"] for f in pu.audit(d)["auto"]])
            pu.apply(Path(d))
            self.assertNotIn("stale-version", [f["kind"] for f in pu.audit(d)["auto"]])


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
            second = pu.apply(d)
            # the standing team-offer advisory may repeat while roles stay uncovered, but a
            # second run performs NO write actions
            writes = [a for a in second
                      if any(v in a for v in ("created", "installed", "updated", "migrated",
                                              "repaired", "reconciled"))]
            self.assertEqual(writes, [])

    def test_apply_updates_stale_version(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(pu.CURRENT_SCHEMA, "1.0.0"))
            actions = pu.apply(d)
            self.assertIn(f'skill_version: "{INSTALLED}"', (Path(d) / "sdlc-studio" / ".version").read_text())
            self.assertTrue(any("updated" in a and ".version" in a for a in actions))

    def test_unresolvable_skill_version_warns_and_does_not_stamp_unknown(self):
        # BG0150: when the installed SKILL.md carries no parseable version, apply must NOT write a
        # bogus skill_version: "unknown" (which reads as "the version is missing" and corrupts the
        # metadata skill-update/migrate compare against) - it warns and skips the stamp.
        # patch the version_check object `pu` actually holds (via `import version_check`), not a
        # separately-imported one - under the full suite another test's importlib load can make
        # them different module instances.
        vc = pu.version_check
        orig = vc.installed_version
        vc.installed_version = lambda *a, **k: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _project(d)   # no .version yet
                actions = pu.apply(d)
                ver = Path(d) / "sdlc-studio" / ".version"
                self.assertFalse(ver.exists())                         # nothing bogus written
                self.assertTrue(any("NOT stamped" in a for a in actions))
                self.assertFalse(any("unknown" in a for a in actions))
        finally:
            vc.installed_version = orig

    def test_unresolvable_version_with_existing_dotversion_leaves_it_and_warns(self):
        # BG0150, the bump/repair branch: an existing .version + a newly-unreadable install must be
        # LEFT as-is (not rewritten to "unknown"), with a warning.
        vc = pu.version_check
        orig = vc.installed_version
        vc.installed_version = lambda *a, **k: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _project(d, version=(pu.CURRENT_SCHEMA, "1.0.0"))
                before = (Path(d) / "sdlc-studio" / ".version").read_text()
                actions = pu.apply(d)
                after = (Path(d) / "sdlc-studio" / ".version").read_text()
                self.assertEqual(before, after)                    # untouched, not "unknown"
                self.assertTrue(any("NOT stamped" in a for a in actions))
        finally:
            vc.installed_version = orig

    def test_audit_reports_unreadable_version_as_manual_not_auto(self):
        # BG0150: the dry-run preview must not PROMISE a version stamp apply will skip.
        vc = pu.version_check
        orig = vc.installed_version
        vc.installed_version = lambda *a, **k: None
        try:
            with tempfile.TemporaryDirectory() as d:
                _project(d)   # no .version
                a = pu.audit(d)
                self.assertNotIn("missing-version", {x["kind"] for x in a["auto"]})
                self.assertIn("version-unresolvable", {x["kind"] for x in a["manual"]})
        finally:
            vc.installed_version = orig

    def test_real_version_still_stamps_after_the_guard(self):
        # the guard must not regress the normal path
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            pu.apply(d)
            text = (Path(d) / "sdlc-studio" / ".version").read_text()
            self.assertIn(f'skill_version: "{INSTALLED}"', text)
            self.assertNotIn("unknown", text)

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

    def test_apply_does_not_auto_install_defaults(self):
        # RFC0028: the offer precedes the defaults - a plain --apply reports the uncovered
        # roles and points at `persona generate --team`; it installs NOTHING unrequested.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            actions = pu.apply(d)
            self.assertFalse((sd / "personas" / "amigos").exists())
            self.assertFalse(any((sd / "personas" / "seats").glob("*.md"))
                             if (sd / "personas" / "seats").is_dir() else False)
            self.assertTrue(any("persona generate --team" in a for a in actions))

    def test_apply_with_default_amigos_installs_into_seats(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            actions = pu.apply(d, with_default_amigos=True)
            sdir = sd / "personas" / "seats"
            for name in self.AMIGOS:
                self.assertTrue((sdir / name).exists(), f"{name} not installed to seats/")
            src = pu._amigos_source()
            self.assertEqual((sdir / "engineering.md").read_text(encoding="utf-8"),
                             (src / "engineering.md").read_text(encoding="utf-8"))
            self.assertTrue(any("seats/" in a for a in actions))
            self.assertFalse((sd / "personas" / "amigos").exists())  # retired home untouched

    def test_apply_migrates_legacy_amigos_to_seats(self):
        # The converged home: existing personas/amigos/ cards move to seats/ mechanically,
        # gaining a role comment from the filename when absent; amigos/ is removed when empty.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            adir = sd / "personas" / "amigos"
            adir.mkdir(parents=True, exist_ok=True)
            custom = "# Our own engineer\n\nproject-specific amigo\n"  # no role comment
            (adir / "engineering.md").write_text(custom, encoding="utf-8")
            pu.apply(d)
            moved = sd / "personas" / "seats" / "engineering.md"
            self.assertTrue(moved.exists())
            text = moved.read_text(encoding="utf-8")
            self.assertIn("<!-- role: engineering -->", text)   # role ensured
            self.assertIn("project-specific amigo", text)       # content preserved
            self.assertFalse(adir.exists())                     # retired home removed

    def test_migration_never_overwrites_an_existing_seat_filename(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            adir = sd / "personas" / "amigos"; adir.mkdir(parents=True, exist_ok=True)
            sdir = sd / "personas" / "seats"; sdir.mkdir(parents=True, exist_ok=True)
            (adir / "qa.md").write_text("# legacy qa\n", encoding="utf-8")
            authored = "<!-- role: qa -->\n# Priya\n"
            (sdir / "qa.md").write_text(authored, encoding="utf-8")
            actions = pu.apply(d)
            self.assertEqual((sdir / "qa.md").read_text(encoding="utf-8"), authored)  # untouched
            self.assertTrue((adir / "qa.md").exists())          # legacy left for hand-merge
            self.assertTrue(any("SKIPPED" in a for a in actions))

    def test_migration_never_creates_a_role_collision(self):
        # Sam's CR0218 defect: a legacy card whose declared role is already claimed by
        # a DIFFERENTLY-NAMED seats/ card must be skipped, not migrated into a
        # duplicate-role collision that can flip resolution away from the authored seat.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            adir = sd / "personas" / "amigos"; adir.mkdir(parents=True, exist_ok=True)
            sdir = sd / "personas" / "seats"; sdir.mkdir(parents=True, exist_ok=True)
            (adir / "qa.md").write_text("<!-- role: qa -->\n# Legacy QA amigo\n",
                                        encoding="utf-8")
            authored = "<!-- role: qa -->\n# Sara - authored QA seat\n"
            (sdir / "sara.md").write_text(authored, encoding="utf-8")
            actions = pu.apply(d)
            self.assertFalse((sdir / "qa.md").exists())          # never migrated into collision
            self.assertTrue((adir / "qa.md").exists())           # left for the operator
            self.assertTrue(any("role" in a and ("SKIPPED" in a or "retire" in a.lower())
                                for a in actions), actions)
            # resolution still returns the authored seat
            import importlib.util, sys as _sys
            spec = importlib.util.spec_from_file_location(
                "persona_resolve", SCR / "persona_resolve.py")
            pr = importlib.util.module_from_spec(spec); _sys.modules["persona_resolve"] = pr
            spec.loader.exec_module(pr)
            card = pr.resolve_card(Path(d), "qa")
            self.assertIn("Sara", Path(card).read_text(encoding="utf-8"))

    def test_with_default_amigos_installs_even_when_nothing_else_to_apply(self):
        # Sam's CR0218 defect 2: the documented decline command must not be a no-op on a
        # current project. The defect lives in the CLI apply gate, so drive main():
        # after a first --apply the project is current, and the exact command the
        # report recommends must still install the uncovered defaults.
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            with contextlib.redirect_stdout(io.StringIO()):
                pu.main(["--root", d, "--apply"])                  # project now current
            with contextlib.redirect_stdout(io.StringIO()):
                pu.main(["--root", d, "--apply", "--with-default-amigos"])
            self.assertTrue(any((sd / "personas" / "seats").glob("*.md")),
                            "the documented decline command installed nothing")

    def test_apply_idempotent_for_amigos(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            pu.apply(d, with_default_amigos=True)
            second = pu.apply(d, with_default_amigos=True)
            self.assertFalse(any("installed" in a for a in second))  # nothing re-installed

    def test_audit_offers_the_team_for_uncovered_roles(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            report = pu.audit(d)
            kinds = [f["kind"] for f in report["manual"]]
            self.assertIn("team-offer", kinds)
            offer = next(f for f in report["manual"] if f["kind"] == "team-offer")
            self.assertIn("persona generate --team", offer["detail"])

    def test_audit_no_flag_when_all_amigos_present(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d, version=(pu.CURRENT_SCHEMA, INSTALLED))
            adir = sd / "personas" / "amigos"
            adir.mkdir(parents=True, exist_ok=True)
            for name in self.AMIGOS:
                (adir / name).write_text("# x\n", encoding="utf-8")
            kinds = [f["kind"] for f in pu.audit(d)["auto"]]
            self.assertNotIn("missing-amigos", kinds)


class BG0041HintTests(unittest.TestCase):
    """The old-persona-model finding names the actual structural signal that fired, not a
    generic 'rewrite content' hint that does not clear the detector."""

    def _personas_finding(self, d):
        return next((f for f in pu.audit(d)["manual"] if f["kind"] == "personas"), None)

    def test_nested_dirs_hint_names_the_dirs(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, personas=[("team/sarah.md", "# Sarah\n\nx\n")])
            f = self._personas_finding(d)
            self.assertIsNotNone(f)
            self.assertIn("team", f["detail"])  # names the real trigger (the nested dir)
            self.assertNotIn("rewrite to the Cooper model", f["detail"])  # not the misdirecting hint

    def test_amigo_in_index_hint_names_index(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, personas=[("index.md", "# Personas\n\nthe amigo set\n")])
            f = self._personas_finding(d)
            self.assertIsNotNone(f)
            self.assertIn("amigo", f["detail"])
            self.assertIn("index.md", f["detail"])

    def test_old_heading_hint_names_the_file(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d, personas=[("emma.md", "# Emma\n\n## Backstory\n\nx\n")])
            f = self._personas_finding(d)
            self.assertIsNotNone(f)
            self.assertIn("emma.md", f["detail"])  # names the offending file


class CR0120SeatAwareTests(unittest.TestCase):
    """CR0120 AC1-4 + RFC0021 D2/D4: upgrade is seat-aware; no parallel install when seats cover
    the role; overlap heads-up even in --dry-run."""

    AMIGOS = ("engineering.md", "qa.md", "product.md")

    def _seat(self, sd, filename, role):
        d = sd / "personas" / "seats"
        d.mkdir(parents=True, exist_ok=True)
        (d / filename).write_text(
            f"<!-- role: {role} -->\n# Person - {role} seat\n\n"
            "## Lens\n\nx\n## Pushes Back When\n\nx\n## Shadow\n\nx\n", encoding="utf-8")

    def test_seat_covered_role_not_reported_missing(self):
        # AC1: a role covered by a seat (by declared role, not filename) is NOT a missing amigo.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            self._seat(sd, "sarah.md", "engineering")
            self.assertNotIn("engineering.md", pu._missing_amigos(Path(d)))
            # the uncovered roles are still missing
            self.assertIn("qa.md", pu._missing_amigos(Path(d)))

    def test_all_roles_seat_covered_installs_no_parallel_set(self):
        # AC2/AC3: when seats cover every role, --apply installs no parallel amigos/ set.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            self._seat(sd, "sarah.md", "engineering")
            self._seat(sd, "marcus.md", "qa")
            self._seat(sd, "priya.md", "product")
            pu.apply(d)
            self.assertFalse((sd / "personas" / "amigos").exists())  # no parallel set manufactured

    def test_greenfield_generic_install_is_opt_in_and_lands_in_seats(self):
        # RFC0028 supersedes CR0120 AC3: generic cards are OPT-IN (--with-default-amigos,
        # after the team-generation offer) and install into the converged seats/ home.
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            pu.apply(d)  # plain apply: offer only
            self.assertFalse((sd / "personas" / "amigos").exists())
            pu.apply(d, with_default_amigos=True)
            for name in self.AMIGOS:
                self.assertTrue((sd / "personas" / "seats" / name).exists())

    def test_overlap_headsup_in_dry_run(self):
        # AC4: when amigos and seats coexist (overlap), the heads-up fires even in --dry-run.
        import io
        from contextlib import redirect_stdout
        with tempfile.TemporaryDirectory() as d:
            sd = _project(d)
            self._seat(sd, "sarah.md", "engineering")
            adir = sd / "personas" / "amigos"; adir.mkdir(parents=True, exist_ok=True)
            (adir / "engineering.md").write_text("<!-- role: engineering -->\n# Dani\n", encoding="utf-8")
            buf = io.StringIO()
            with redirect_stdout(buf):
                pu.main(["--root", d])  # dry-run, no --apply
            out = buf.getvalue().lower()
            self.assertIn("overlap", out)
            self.assertIn("engineering", out)

    def test_no_overlap_headsup_when_no_seats(self):
        with tempfile.TemporaryDirectory() as d:
            _project(d)
            self.assertEqual(pu._seat_amigo_overlap(Path(d)), [])


class UpgradeWalkTests(unittest.TestCase):
    """US0106/CR0198: a v2 project's upgrade is presented as a directed v2->v3 sequence."""

    def test_v2_project_gets_ordered_walk(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(2, "3.6.0"))
            walk = pu.migration_walk(Path(d))
            steps = [s["step"] for s in walk]
            # ordered: operator decision -> migrate_v3 dry-run -> migrate_v3 apply -> re-baseline
            self.assertEqual(len(walk), 4)
            joined = " | ".join(steps).lower()
            self.assertLess(joined.index("operator decision"), joined.index("migrate_v3"))
            self.assertLess(joined.rindex("migrate_v3"), joined.index("re-baseline"))
            self.assertTrue(any("dry-run" in s["detail"].lower() for s in walk))

    def test_walk_frames_numbering_switch_as_operator_question(self) -> None:
        # CR0216: the id renumbering is an explicit operator decision, never a default.
        # The walk must state the choice, the multi-user rationale, that declining is
        # fully supported, and that apply requires --confirm.
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(2, "3.6.0"))
            walk = pu.migration_walk(Path(d))
            decision = walk[0]
            self.assertIn("operator decision", decision["step"].lower())
            detail = decision["detail"].lower()
            # the three explicit answers: full migration, forward-only, stay on v2
            for needle in ("collision-free", "forward-only", "stay on v2", "asked explicitly"):
                self.assertIn(needle, detail)
            self.assertTrue(any("--confirm" in s["detail"] for s in walk))
            self.assertTrue(any("adopt --confirm" in s["detail"] for s in walk))

    def test_v3_project_has_no_walk(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(3, "4.0.0-rc.1"))
            self.assertEqual(pu.migration_walk(Path(d)), [])

    def test_fresh_init_v3_project_has_no_walk(self) -> None:
        # A fresh v4 project: init writes .config.yaml (schema_version: 3) but NO .version.
        # migration_walk must read the authoritative config, not just .version, and show no walk.
        import importlib.util as _u
        spec = _u.spec_from_file_location("init", SCR / "init.py")
        init = _u.module_from_spec(spec); spec.loader.exec_module(init)
        with tempfile.TemporaryDirectory() as d:
            init.init(Path(d))
            self.assertEqual(pu.migration_walk(Path(d)), [])          # already v3 -> no walk
            self.assertEqual(pu.detect(Path(d))["project_schema"], 3)  # effective schema from config


FIXTURE_CHANGELOG = """# Changelog

## [3.4.0] - 2026-07-04

### Added

- Mutation-check gate over the changed surface
- Batch transitions with per-id gating

### Changed

- Telemetry records terminal closes

## [3.0.0] - 2026-06-20

### Added

- Constitution check

## [2.5.0] - 2026-06-01

### Added

- Old capability the project already has
"""


class ChangelogDigestTests(unittest.TestCase):
    """The upgrade must say what the skill can now DO, not only which files it
    corrected - the capability delta between recorded and installed versions."""

    def _changelog(self, d, text=FIXTURE_CHANGELOG):
        p = Path(d) / "CHANGELOG.md"
        p.write_text(text, encoding="utf-8")
        return p

    def test_range_excludes_recorded_includes_installed(self):
        with tempfile.TemporaryDirectory() as d:
            dig = pu.changelog_digest("2.5.0", "3.4.0", self._changelog(d))
            self.assertTrue(dig["available"], dig)
            self.assertEqual(dig["versions"], ["3.4.0", "3.0.0"])
            added = "\n".join(dig["groups"]["Added"])
            self.assertIn("Mutation-check gate", added)
            self.assertIn("Constitution check", added)
            self.assertNotIn("Old capability", added)   # recorded version excluded
            self.assertIn("Telemetry records", "\n".join(dig["groups"]["Changed"]))

    def test_missing_changelog_degrades_honestly(self):
        dig = pu.changelog_digest("2.5.0", "3.4.0", Path("/nonexistent/CHANGELOG.md"))
        self.assertFalse(dig["available"])
        self.assertIn("CHANGELOG", dig["reason"])

    def test_empty_range_degrades(self):
        with tempfile.TemporaryDirectory() as d:
            dig = pu.changelog_digest("3.4.0", "3.4.0", self._changelog(d))
            self.assertFalse(dig["available"])
            self.assertIn("between", dig["reason"])

    def test_unparseable_changelog_degrades_never_crashes(self):
        with tempfile.TemporaryDirectory() as d:
            dig = pu.changelog_digest("2.5.0", "3.4.0",
                                      self._changelog(d, "just prose, no versions\n"))
            self.assertFalse(dig["available"])

    def test_unknown_recorded_version_degrades(self):
        with tempfile.TemporaryDirectory() as d:
            dig = pu.changelog_digest(None, "3.4.0", self._changelog(d))
            self.assertFalse(dig["available"])


class AdvisoryLaneTests(unittest.TestCase):
    """A gate lane that reads not-run when absent must be NAMED at upgrade time
    when it arrived in the version gap - a new integrity check must not land
    silently as a benign-looking warn."""

    def test_mutation_lane_named_in_gap(self):
        lanes = pu.new_advisory_lanes("2.5.0", "3.4.0")
        names = [x["lane"] for x in lanes]
        self.assertIn("mutation", names)
        mut = next(x for x in lanes if x["lane"] == "mutation")
        self.assertIn("mutation.py", mut["baseline"])   # the directed next step

    def test_lane_outside_gap_not_named(self):
        self.assertEqual([x["lane"] for x in pu.new_advisory_lanes("3.4.0", "3.5.0")
                          if x["lane"] == "mutation"], [])


class DigestKindHandlingTests(unittest.TestCase):
    """Non-standard change kinds must be printed, and a qualified kind heading
    (### Added (project upgrade)) resets the kind rather than leaking bullets
    into the previous group."""

    CL = """# Changelog

## [3.5.0] - 2026-07-10

### Added

- Standard added item

### Added (project upgrade)

- Qualified-heading item

### Proposed

- Project-specific kind item
"""

    def test_qualified_heading_resets_kind_and_custom_kind_prints(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "CHANGELOG.md"
            p.write_text(self.CL, encoding="utf-8")
            dig = pu.changelog_digest("3.4.0", "3.5.0", p)
            self.assertTrue(dig["available"], dig)
            self.assertIn("Qualified-heading item", dig["groups"]["Added"])
            self.assertIn("Project-specific kind item", dig["groups"]["Proposed"])
            rendered = "\n".join(pu._render_digest(dig))
            self.assertIn("Proposed:", rendered)          # custom kind printed
            self.assertIn("Project-specific kind item", rendered)


def _v3_story(sd, sid, status="Ready", difficulty=True, affects="a.py",
              ac_verify=True, override=False):
    """A schema-v3 story with controllable baseline attributes (US0094 census fixture)."""
    lines = [f"# US{sid:04d}: s", "", f"> **Status:** {status}", "> **Epic:** EP0001"]
    if affects:
        lines.append(f"> **Affects:** {affects}")
    if difficulty:
        lines.append("> **Difficulty:** medium")
    if override:
        lines.append("> **Plan-Review-Override:** ops")
    lines += ["", "## Acceptance Criteria", "", "### AC1: a", "- **Given** x",
              "- **When** y", "- **Then** z"]
    if ac_verify:
        lines.append("- **Verify:** pytest tests/test_x.py::t")
    d = sd / "stories"; d.mkdir(exist_ok=True)
    (d / f"US{sid:04d}-s.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _v3_project(d, v3=True):
    sd = Path(d) / "sdlc-studio"
    (sd / "stories").mkdir(parents=True, exist_ok=True)
    (sd / "reviews").mkdir(parents=True, exist_ok=True)
    if v3:
        (sd / ".config.yaml").write_text(
            "schema_version: 3\nplan_review:\n  affects_files_threshold: 99\n"
            "  min_difficulty: extreme\n", encoding="utf-8")
    return sd


class RebaselineCensusTests(unittest.TestCase):
    """US0094 AC1: per-artifact gaps bucketed backfill / re-review / residual (schema v3)."""

    def _ids(self, bucket):
        return sorted(e["id"] for e in bucket)

    def test_buckets_isolate_each_capability(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 1, status="Done")                                # terminal -> absent
            _v3_story(sd, 2)                                               # fully baselined -> absent
            _v3_story(sd, 3, difficulty=False)                            # -> backfill (no Difficulty)
            _v3_story(sd, 4, affects="docs/prd.md")                       # spec-cite -> re-review
            _v3_story(sd, 5, ac_verify=False)                            # AC missing Verify -> residual
            r = pu.rebaseline(d)
            self.assertNotIn("US0001", self._ids(r["backfill"] + r["re-review"] + r["residual"]))
            self.assertNotIn("US0002", self._ids(r["backfill"] + r["re-review"] + r["residual"]))
            self.assertIn("US0003", self._ids(r["backfill"]))
            self.assertIn("US0004", self._ids(r["re-review"]))
            self.assertIn("US0005", self._ids(r["residual"]))

    def test_spec_story_with_override_is_not_re_review(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 4, affects="docs/prd.md", override=True)        # override satisfies it
            self.assertNotIn("US0004", [e["id"] for e in pu.rebaseline(d)["re-review"]])

    def test_terminal_story_with_every_gap_is_in_no_bucket(self):
        # locks terminal-skip for ALL buckets: a Done story with a missing Difficulty, a spec
        # citation, and an AC missing Verify must still appear nowhere.
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 1, status="Done", difficulty=False,
                      affects="docs/prd.md", ac_verify=False)
            r = pu.rebaseline(d)
            self.assertEqual([], r["backfill"] + r["re-review"] + r["residual"])

    def test_stray_verify_outside_ac_section_does_not_mask_a_gap(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            (sd / "stories").mkdir(exist_ok=True)
            (sd / "stories" / "US0007-s.md").write_text(
                "# US0007: s\n\n> **Status:** Ready\n> **Difficulty:** low\n> **Affects:** a.py\n\n"
                "## Acceptance Criteria\n\n### AC1: a\n- **Then** x\n- **Verify:** pytest t\n"
                "### AC2: b\n- **Then** y\n\n## Notes\n\n- **Verify:** an example only\n",
                encoding="utf-8")
            self.assertIn("US0007", [e["id"] for e in pu.rebaseline(d)["residual"]])

    def test_re_review_respects_independence(self):
        import critic
        for reviewer, cleared in (("qa", True), ("dev", False)):     # dev==author => self-review
            with tempfile.TemporaryDirectory() as d:
                sd = _v3_project(d)
                _v3_story(sd, 4, affects="docs/prd.md")
                critic.record_verdict(d, "US0004", "APPROVE", reviewer=reviewer,
                                      author="dev", phase="plan-review")
                flagged = "US0004" in [e["id"] for e in pu.rebaseline(d)["re-review"]]
                self.assertEqual(flagged, not cleared)
        with tempfile.TemporaryDirectory() as d:                     # independent REJECT: not cleared
            sd = _v3_project(d)
            _v3_story(sd, 4, affects="docs/prd.md")
            critic.record_verdict(d, "US0004", "REJECT", reviewer="qa", author="dev",
                                  phase="plan-review")
            self.assertIn("US0004", [e["id"] for e in pu.rebaseline(d)["re-review"]])


class RebaselineEraBoundaryTests(unittest.TestCase):
    """US0094 AC3: Done untouched, Ready flagged; unadopted (v2) -> no gaps."""

    def test_done_untouched_ready_flagged(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 1, status="Done", difficulty=False)            # terminal, ignored
            _v3_story(sd, 2, status="Ready", difficulty=False)          # flagged
            r = pu.rebaseline(d)
            ids = [e["id"] for e in r["backfill"]]
            self.assertIn("US0002", ids)
            self.assertNotIn("US0001", ids)

    def test_dormant_under_v2(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d, v3=False)
            _v3_story(sd, 2, difficulty=False, affects="docs/prd.md", ac_verify=False)
            r = pu.rebaseline(d)
            self.assertEqual(r, {"backfill": [], "re-review": [], "residual": []})


class RebaselineReportTests(unittest.TestCase):
    """US0094 AC2: the report lists artifacts per bucket; empty buckets are explicit."""

    def test_report_names_buckets_and_empty_is_explicit(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 3, difficulty=False)                           # backfill only
            lines = pu.rebaseline_report(d)
            text = "\n".join(lines)
            self.assertIn("US0003", text)
            self.assertIn("backfill", text.lower())
            self.assertIn("re-review", text.lower())
            self.assertIn("none", text.lower())                          # empty buckets explicit


class RebaselineDeterminismTests(unittest.TestCase):
    """US0094 AC4: identical result across runs (no model judgement)."""

    def test_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 3, difficulty=False)
            _v3_story(sd, 4, affects="docs/prd.md")
            self.assertEqual(pu.rebaseline(d), pu.rebaseline(d))


class BackfillApplyTests(unittest.TestCase):
    """US0095/CR0197: --apply performs ONLY the backfill bucket, deterministically."""

    def test_apply_stamps_difficulty_on_a_unit_lacking_it(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 3, difficulty=False)                       # backfill candidate
            actions = pu.rebaseline_apply(d)
            self.assertTrue(any("US0003" in a for a in actions))
            text = (sd / "stories" / "US0003-s.md").read_text(encoding="utf-8")
            self.assertRegex(text, r"> \*\*Difficulty:\*\* \w+")   # stamped

    def test_apply_does_not_action_re_review_or_residual(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 4, affects="docs/prd.md")                  # re-review (has Difficulty)
            _v3_story(sd, 5, ac_verify=False)                        # residual (has Difficulty)
            before4 = (sd / "stories" / "US0004-s.md").read_text(encoding="utf-8")
            before5 = (sd / "stories" / "US0005-s.md").read_text(encoding="utf-8")
            pu.rebaseline_apply(d)
            self.assertEqual(before4, (sd / "stories" / "US0004-s.md").read_text(encoding="utf-8"))
            self.assertEqual(before5, (sd / "stories" / "US0005-s.md").read_text(encoding="utf-8"))

    def test_dormant_under_v2(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d, v3=False)
            _v3_story(sd, 3, difficulty=False)
            self.assertEqual(pu.rebaseline_apply(d), [])


class BackfillIdempotencyTests(unittest.TestCase):
    def test_second_apply_is_a_noop(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 3, difficulty=False)
            self.assertTrue(pu.rebaseline_apply(d))                  # first run stamps
            self.assertEqual(pu.rebaseline_apply(d), [])            # second run: nothing to do


class BackfillLineEndingTests(unittest.TestCase):
    def test_apply_preserves_crlf(self):
        # --apply adds exactly one line; a CRLF file must not be normalised to LF wholesale.
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            p = sd / "stories"; p.mkdir(exist_ok=True)
            body = ("# US0013: s\n> **Status:** Ready\n> **Affects:** a.py\n\n"
                    "## Acceptance Criteria\n### AC1: a\n- **Verify:** m\n").replace("\n", "\r\n")
            (p / "US0013-s.md").write_text(body, encoding="utf-8", newline="")
            before = (p / "US0013-s.md").read_bytes().count(b"\r\n")
            pu.rebaseline_apply(d)
            after = (p / "US0013-s.md").read_bytes().count(b"\r\n")
            self.assertEqual(after, before + 1)          # one line added, CRLF preserved


class NoFabricatedHistoryTests(unittest.TestCase):
    def test_apply_invents_no_telemetry_rows(self):
        with tempfile.TemporaryDirectory() as d:
            sd = _v3_project(d)
            _v3_story(sd, 3, difficulty=False)
            pu.rebaseline_apply(d)
            self.assertFalse((sd / ".local" / "telemetry.jsonl").exists())  # no back-dated rows

class SchemaStampTests(unittest.TestCase):
    """BG0102: an upgrade may only ever RAISE the .version schema stamp - a skill-version
    bump on a migrated v3 project must not rewrite its stamp back to 2."""

    def test_apply_never_downgrades_a_v3_stamp(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(3, "3.9.0"))  # migrated project, older skill stamp
            (Path(d) / "sdlc-studio" / ".config.yaml").write_text(
                "schema_version: 3\n", encoding="utf-8")
            pu.apply(Path(d))
            text = (Path(d) / "sdlc-studio" / ".version").read_text(encoding="utf-8")
            self.assertIn("schema_version: 3", text)
            self.assertNotIn("schema_version: 2", text)

    def test_declining_the_switch_leaves_v2_fully_upgraded(self) -> None:
        # CR0216 AC2: an operator who declines the renumbering still gets the whole
        # upgrade - and the project stays functional on v2 numbering.
        with tempfile.TemporaryDirectory() as d:
            _project(d, version=(2, "3.9.0"), story_id=1)
            pu.apply(Path(d))  # the "rest of the upgrade", no migrate_v3 run
            text = (Path(d) / "sdlc-studio" / ".version").read_text(encoding="utf-8")
            self.assertIn("schema_version: 2", text)  # not silently flipped to 3
            story = next((Path(d) / "sdlc-studio" / "stories").glob("US0001-*.md"))
            self.assertTrue(story.exists())  # ids untouched - still sequential


if __name__ == "__main__":
    unittest.main()
