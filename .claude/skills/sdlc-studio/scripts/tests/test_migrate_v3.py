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
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tests/ dir, for the shared gitutil helper
from lib import sdlc_md  # noqa: E402
import gitutil  # noqa: E402


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
            gitutil.git(["init", "-q"], root)
            (root / "a.md").write_text("x\n", encoding="utf-8")
            gitutil.git(["add", "-A"], root)
            gitutil.git(["commit", "-qm", "add"], root)
            epochs = migrate_v3._git_add_epochs(root)
            self.assertIn("a.md", epochs)
            self.assertGreater(epochs["a.md"], 1_000_000_000_000)  # a real ms epoch


class CounterWrapAndSlugTests(unittest.TestCase):
    """BG0087: the per-file counter must not wrap (silent rename overwrite = data loss) and
    the migrated slug must not embed the stale v2 number."""

    def test_minted_ids_are_unique(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _fixture(root)
            id_map = migrate_v3.build_id_map(root)
            new_ids = [e["new_id"] for e in id_map.values()]
            self.assertEqual(len(new_ids), len(set(new_ids)))

    def test_counter_width_covers_the_entry_count(self) -> None:
        # a 2-char base32 counter wraps at 1024; width must scale so >1024 entries stay unique.
        self.assertGreaterEqual(migrate_v3._counter_width(1025), 3)
        self.assertGreaterEqual(migrate_v3._counter_width(2000), 3)
        self.assertEqual(migrate_v3._counter_width(10), 2)  # small batch keeps the compact form

    def test_slug_drops_the_v2_number(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            crd = root / "sdlc-studio" / "change-requests"
            crd.mkdir(parents=True)
            (crd / "CR-0001-add-auth.md").write_text(
                "# CR-0001: add auth\n\n> **Status:** Complete\n> **Priority:** Medium\n"
                "> **Type:** Feature\n> **Created-by:** sdlc-studio new\n", encoding="utf-8")
            (crd / "_index.md").write_text(
                "# CRs\n\n## All\n\n| ID | Title | Status | Priority | Type | Date | Linked Epics |\n"
                "| --- | --- | --- | --- | --- | --- | --- |\n"
                "| [CR-0001](CR-0001-add-auth.md) | add auth | Complete | Medium | Feature | 2026-01-01 | - |\n",
                encoding="utf-8")
            id_map = migrate_v3.build_id_map(root)
            new_path = id_map["CR-0001"]["new_path"]
            self.assertNotIn("0001", new_path.stem)
            self.assertTrue(new_path.stem.endswith("add-auth"))


class ConfirmGateTests(unittest.TestCase):
    """CR0216: apply renumbers every id - an operator decision, never headless. Without
    --confirm it must refuse with guidance and write NOTHING; plan stays unrestricted."""

    def _v2(self, root: Path) -> Path:
        d = root / "sdlc-studio" / "bugs"
        d.mkdir(parents=True)
        (d / "BG0001-x.md").write_text("# BG0001: x\n\n> **Status:** Open\n", encoding="utf-8")
        return root

    def test_apply_without_confirm_refuses_and_writes_nothing(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = self._v2(Path(d))
            before = sorted(p.name for p in (root / "sdlc-studio" / "bugs").iterdir())
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = migrate_v3.main(["apply", "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("operator", err.getvalue().lower())
            self.assertIn("--confirm", err.getvalue())
            after = sorted(p.name for p in (root / "sdlc-studio" / "bugs").iterdir())
            self.assertEqual(before, after)  # nothing renamed

    def test_apply_with_confirm_proceeds(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = self._v2(Path(d))
            with contextlib.redirect_stdout(io.StringIO()):
                rc = migrate_v3.main(["apply", "--confirm", "--root", str(root)])
            self.assertEqual(rc, 0)
            names = [p.name for p in (root / "sdlc-studio" / "bugs").iterdir()]
            self.assertTrue(any(n.startswith("BG-") for n in names))  # ULID form minted

    def test_plan_needs_no_confirm(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = self._v2(Path(d))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(migrate_v3.main(["plan", "--root", str(root)]), 0)


class AdoptForwardOnlyTests(unittest.TestCase):
    """Operator option (b): forward-only era switch - existing sequential ids stay (valid
    wherever referenced out-of-system), only NEW artefacts mint ULIDs. adopt stamps the
    schema and touches nothing else; like apply it refuses without --confirm."""

    def test_adopt_without_confirm_refuses(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _fixture(root)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                rc = migrate_v3.main(["adopt", "--root", str(root)])
            self.assertEqual(rc, 2)
            self.assertIn("forward-only", err.getvalue().lower())
            self.assertFalse((root / "sdlc-studio" / ".config.yaml").exists())  # no stamp

    def test_adopt_stamps_schema_and_renames_nothing(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _fixture(root)
            before = sorted(p.name for p in (root / "sdlc-studio" / "stories").iterdir())
            with contextlib.redirect_stdout(io.StringIO()):
                rc = migrate_v3.main(["adopt", "--confirm", "--root", str(root)])
            self.assertEqual(rc, 0)
            cfg = (root / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8")
            self.assertRegex(cfg, r"(?m)^schema_version: 3$")
            after = sorted(p.name for p in (root / "sdlc-studio" / "stories").iterdir())
            self.assertEqual(before, after)  # ids untouched - forward-only

    def test_new_filing_after_adopt_mints_ulid_and_reconcile_stays_clean(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _fixture(root)
            with contextlib.redirect_stdout(io.StringIO()):
                migrate_v3.main(["adopt", "--confirm", "--root", str(root)])
            artifact = _load("artifact")
            res = artifact.new(root, "bug", "a fresh v3 bug",
                               {"severity": "Medium", "priority": "Medium"})
            self.assertRegex(res["id"], r"^BG-[0-9A-Z]{8,}")   # new era id
            drift = (reconcile.detect_type("story", root)["drift"]
                     + reconcile.detect_type("epic", root)["drift"])
            self.assertEqual(drift, [])                        # mixed eras reconcile clean


class AdoptResidualTests(unittest.TestCase):
    """Critic residuals: adopt raises an existing .version stamp (else the era decision is
    re-presented forever), and apply/adopt refuse a directory with no workspace."""

    def test_adopt_raises_a_stale_version_stamp(self) -> None:
        import contextlib, io
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _fixture(root)
            (root / "sdlc-studio" / ".version").write_text(
                'schema_version: 2\nskill_version: "3.6.0"\n', encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                migrate_v3.main(["adopt", "--confirm", "--root", str(root)])
            vt = (root / "sdlc-studio" / ".version").read_text(encoding="utf-8")
            self.assertIn("schema_version: 3", vt)
            self.assertIn('skill_version: "3.6.0"', vt)  # other lines preserved

    def test_apply_and_adopt_refuse_a_non_workspace_dir(self) -> None:
        import contextlib, io
        for cmd in ("apply", "adopt"):
            with tempfile.TemporaryDirectory() as d:
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    rc = migrate_v3.main([cmd, "--confirm", "--root", d])
                self.assertEqual(rc, 2, cmd)
                self.assertIn("no sdlc-studio/ workspace", err.getvalue())
                self.assertFalse((Path(d) / "sdlc-studio").exists())  # nothing created


if __name__ == "__main__":
    unittest.main()
