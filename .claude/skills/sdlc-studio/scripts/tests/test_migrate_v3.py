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


if __name__ == "__main__":
    unittest.main()
