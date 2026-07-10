"""US0056/RFC0024: the v2 -> v3 migration - order-preserving, alias-retaining, link-rewriting,
idempotent, and reconcile-clean afterwards.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


migrate_v3 = _load("migrate_v3")
reconcile = _load("reconcile")


def _fixture(root: Path) -> None:
    """A small v2 workspace: an epic, two stories that link it, and their index."""
    ep = root / "sdlc-studio" / "epics"
    st = root / "sdlc-studio" / "stories"
    ep.mkdir(parents=True)
    st.mkdir(parents=True)
    (ep / "EP0001-auth.md").write_text(
        "# EP0001: Auth\n\n> **Status:** Draft\n> **Created-by:** sdlc-studio new\n\n"
        "## Story Breakdown\n\n- [ ] [US0001](../stories/US0001-login.md)\n"
        "- [ ] [US0002](../stories/US0002-logout.md)\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n", encoding="utf-8")
    (ep / "_index.md").write_text(
        "# Epics\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Draft | 1 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [EP0001](EP0001-auth.md) | Auth | Draft |\n", encoding="utf-8")
    for num, name in [(1, "login"), (2, "logout")]:
        (st / f"US{num:04d}-{name}.md").write_text(
            f"# US{num:04d}: {name}\n\n> **Status:** Draft\n> **Created-by:** sdlc-studio new\n"
            f"> **Epic:** [EP0001](../epics/EP0001-auth.md)\n\n## User Story\n\nx\n\n"
            "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n", encoding="utf-8")
    (st / "_index.md").write_text(
        "# Stories\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Draft | 2 |\n\n"
        "## All\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        "| [US0001](US0001-login.md) | login | Draft |\n"
        "| [US0002](US0002-logout.md) | logout | Draft |\n", encoding="utf-8")


class GitBatchScaleTests(unittest.TestCase):
    """BG0070: build_id_map must batch the creation-date lookup into ONE git pass, not a
    git-log-per-artefact (which does not scale to a large project)."""

    def test_build_id_map_makes_at_most_one_git_call(self) -> None:
        from unittest import mock
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)  # 3 v2 artefacts (1 epic + 2 stories)
            calls = []
            real_run = migrate_v3.subprocess.run

            def spy(cmd, *a, **k):
                if cmd and cmd[0] == "git":
                    calls.append(cmd)
                return real_run(cmd, *a, **k)

            with mock.patch.object(migrate_v3.subprocess, "run", side_effect=spy):
                id_map = migrate_v3.build_id_map(root)
            self.assertEqual(len(id_map), 3)                 # still maps every artefact
            self.assertLessEqual(len(calls), 1,
                                 f"expected <=1 git call, got {len(calls)} (per-file git = BG0070)")


class MigrationTests(unittest.TestCase):
    def test_migration_preserves_order_aliases_and_links(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            res = migrate_v3.migrate(root, dry_run=False)
            self.assertEqual(res["migrated"], 3)  # EP0001, US0001, US0002

            st = root / "sdlc-studio" / "stories"
            files = sorted(p.name for p in st.glob("US-*.md"))
            self.assertEqual(len(files), 2)
            # order preserved: the earlier-created story sorts first by its new id
            ids = [sdlc_md.extract_record_id(Path(f).stem) for f in files]
            self.assertEqual(ids, sorted(ids))

            # old id retained as an alias, resolvable
            amap = sdlc_md.alias_map(root)
            self.assertIn("US0001", {k.upper(): v for k, v in amap.items()} or amap)
            self.assertIn(sdlc_md.norm_id("US0001"), amap)

            # links rewritten: no dangling old id remains in the epic's breakdown
            epic = next((root / "sdlc-studio" / "epics").glob("EP-*.md")).read_text(encoding="utf-8")
            self.assertNotIn("US0001", epic)
            self.assertNotIn("](../stories/US0001", epic)

            # reconcile is clean after migration
            self.assertEqual(reconcile.detect_type("story", root)["drift"], [])
            self.assertEqual(reconcile.detect_type("epic", root)["drift"], [])

    def test_migration_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            migrate_v3.migrate(root, dry_run=False)
            second = migrate_v3.migrate(root, dry_run=False)
            self.assertEqual(second["migrated"], 0)  # nothing left to migrate

    def test_plan_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            res = migrate_v3.migrate(root, dry_run=True)
            self.assertEqual(res["migrated"], 3)
            self.assertTrue((root / "sdlc-studio" / "stories" / "US0001-login.md").exists())  # untouched


class SchemaStampTests(unittest.TestCase):
    """A completed apply must flip the project to v3 itself - leaving the stamp manual means
    the next filing mints a numeric id that collides with a live `Aliases:` line."""

    def test_apply_stamps_schema_version_3(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            migrate_v3.migrate(root, dry_run=False)
            cfg = root / "sdlc-studio" / ".config.yaml"
            self.assertTrue(cfg.exists())
            self.assertRegex(cfg.read_text(encoding="utf-8"), r"(?m)^schema_version: 3$")

    def test_apply_updates_an_existing_config_preserving_other_keys(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.write_text("profile: full\nschema_version: 2\n", encoding="utf-8")
            migrate_v3.migrate(root, dry_run=False)
            text = cfg.read_text(encoding="utf-8")
            self.assertIn("profile: full", text)
            self.assertRegex(text, r"(?m)^schema_version: 3$")
            self.assertNotIn("schema_version: 2", text)

    def test_plan_never_stamps(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            migrate_v3.migrate(root, dry_run=True)
            self.assertFalse((root / "sdlc-studio" / ".config.yaml").exists())


class JournalResumeTests(unittest.TestCase):
    """An interrupted apply must resume from its persisted id map - re-planning from
    now-changed mtimes/order silently cross-wires identities."""

    def test_apply_persists_then_clears_the_journal(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            migrate_v3.migrate(root, dry_run=False)
            self.assertFalse(migrate_v3._journal_path(root).exists())

    def test_journal_survives_a_crash_and_resume_completes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            real = migrate_v3.reconcile.apply_type
            migrate_v3.reconcile.apply_type = lambda *a, **k: (_ for _ in ()).throw(OSError("boom"))
            try:
                with self.assertRaises(OSError):
                    migrate_v3.migrate(root, dry_run=False)  # dies at phase 3
            finally:
                migrate_v3.reconcile.apply_type = real
            jp = migrate_v3._journal_path(root)
            self.assertTrue(jp.exists(), "journal must survive the crash")
            res = migrate_v3.migrate(root, dry_run=False)  # resume
            self.assertTrue(res.get("resume"))
            self.assertFalse(jp.exists())
            cfg = (root / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8")
            self.assertIn("schema_version: 3", cfg)

    def test_resume_uses_the_saved_map_not_a_fresh_plan(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            id_map = migrate_v3.build_id_map(root)
            # handcraft DIFFERENT ids into the journal - if resume re-planned, these would lose
            forced = {old: dict(e, new_id=f"{e['new_id'][:3]}TEST{i:04d}",
                                new_path=e["old_path"].parent / f"{e['new_id'][:3]}TEST{i:04d}-x.md")
                      for i, (old, e) in enumerate(sorted(id_map.items()))}
            migrate_v3._save_journal(root, forced)
            migrate_v3.migrate(root, dry_run=False)
            stems = {q.stem for t_ in ("story", "epic")
                     for q in (root / "sdlc-studio" / ("stories" if t_ == "story" else "epics")).glob("*.md")
                     if q.name != "_index.md"}
            for e in forced.values():
                self.assertIn(e["new_path"].stem, stems)

    def test_corrupt_journal_fails_loud(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            jp = migrate_v3._journal_path(root)
            jp.parent.mkdir(parents=True, exist_ok=True)
            jp.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                migrate_v3.migrate(root, dry_run=False)

    def test_plan_reports_a_pending_resume(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            migrate_v3._save_journal(root, migrate_v3.build_id_map(root))
            res = migrate_v3.migrate(root, dry_run=True)
            self.assertTrue(res.get("resume"))


class AliasSurvivesResumeTests(unittest.TestCase):
    def test_resume_never_rewrites_alias_lines(self) -> None:
        # Critic finding on the journal fix: phase 1 re-ran over renamed files on resume and
        # rewrote the OLD id inside "> **Aliases:**" lines, making every alias self-referential
        # and destroying the v2 identity the alias exists to preserve.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            real = migrate_v3.reconcile.apply_type
            migrate_v3.reconcile.apply_type = lambda *a, **k: (_ for _ in ()).throw(OSError("boom"))
            try:
                with self.assertRaises(OSError):
                    migrate_v3.migrate(root, dry_run=False)  # crash AFTER aliases were written
            finally:
                migrate_v3.reconcile.apply_type = real
            migrate_v3.migrate(root, dry_run=False)  # resume
            for rel, old in (("stories", "US0001"), ("stories", "US0002"), ("epics", "EP0001")):
                blobs = [q.read_text(encoding="utf-8")
                         for q in (root / "sdlc-studio" / rel).glob("*.md")]
                self.assertTrue(any(f"> **Aliases:** {old}" in b for b in blobs),
                                f"{old}: original v2 alias must survive the resume")




class GitAddEpochParseTests(unittest.TestCase):
    def test_add_epochs_parse_real_git_log(self) -> None:
        # Kills the surviving invert-guard mutant on the '@'-line parser: a broken parse
        # silently degrades every file to the mtime fallback.
        import subprocess
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "a.md").write_text("x\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t",
                            "-c", "user.name=t", "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(root), "-c", "user.email=t@t",
                            "-c", "user.name=t", "commit", "-qm", "add"], check=True)
            epochs = migrate_v3._git_add_epochs(root)
            self.assertIn("a.md", epochs)
            self.assertGreater(epochs["a.md"], 1_000_000_000_000)  # a real ms epoch


if __name__ == "__main__":
    unittest.main()
