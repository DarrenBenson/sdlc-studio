"""BG0790: a pre-release such as 6.0.0-rc.1 orders below its final 6.0.0 wherever versions meet.

The suffix used to be dropped at every read, so an rc install read as its final: it was never
offered the release, the rc-to-final digest was empty, and migrate stamped a project with the
core. Each criterion goes through the path a user reaches: `version_check.check`, the upgrade
digest, and `migrate --apply` through `migrate.main`. Every fixture is a temporary directory.
"""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

migrate = loader.load_script("migrate")
pu = migrate.project_upgrade
# The instance project_upgrade holds, so a patch reaches the code under test (L-0057).
vc = pu.version_check


def _skill(root: Path, version: str) -> Path:
    """An installed skill whose SKILL.md frontmatter declares `version`."""
    sd = root / "skill"
    sd.mkdir(parents=True)
    (sd / "SKILL.md").write_text(
        f'---\nname: sdlc-studio\nmetadata:\n  version: "{version}"\n---\n# S\n', encoding="utf-8")
    return sd


def _project(root: Path, stamped: str) -> Path:
    """A schema-3 project whose `.version` records `stamped` as its skill version."""
    proj = root / "proj"
    sd = proj / "sdlc-studio"
    sd.mkdir(parents=True)
    (sd / ".config.yaml").write_text("schema_version: 3\nprovenance:\n  adopt_after: 0\n",
                                     encoding="utf-8")
    (sd / ".version").write_text(
        f"schema_version: 3\nupgraded_from: null\nupgraded_at: 2026-01-01\n"
        f'skill_version: "{stamped}"\n', encoding="utf-8")
    return proj


class PreReleaseVersionTests(unittest.TestCase):
    def test_a_pre_release_orders_below_its_final(self) -> None:
        gt = vc._gt
        self.assertTrue(gt("6.0.0", "6.0.0-rc.1"))
        self.assertTrue(gt("6.0.0-rc.1", "5.1.0"))
        self.assertTrue(gt("6.0.0-rc.10", "6.0.0-rc.2"))       # numerically, not as strings
        self.assertFalse(gt("6.0.0-rc.1", "6.0.0-rc.1"))       # not newer than itself
        # the controls: each ordering is strict, so the reverse reads not-newer
        self.assertFalse(gt("6.0.0-rc.1", "6.0.0"))
        self.assertFalse(gt("5.1.0", "6.0.0-rc.1"))
        self.assertFalse(gt("6.0.0-rc.2", "6.0.0-rc.10"))

    def test_an_rc_install_is_offered_its_final(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), "6.0.0-rc.1")
            res = vc.check(sd, _fetch=lambda: "6.0.0", now=1000.0)
            self.assertEqual(res["installed"], "6.0.0-rc.1")
            self.assertEqual(res["status"], "update-available")
            # the control: the final installed is not offered itself
            done = _skill(Path(d) / "final", "6.0.0")
            self.assertEqual(vc.check(done, _fetch=lambda: "6.0.0", now=1000.0)["status"],
                             "up-to-date")

    def test_the_rc_to_final_digest_holds_only_the_final(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "CHANGELOG.md"
            log.write_text("# Changelog\n\n## [Unreleased]\n\n"
                           "## [6.0.0] - 2026-10-01\n\n### Fixed\n\n- final fix\n\n"
                           "## [6.0.0-rc.1] - 2026-09-26\n\n### Added\n\n- rc feature\n\n"
                           "## [5.1.0] - 2026-09-10\n\n### Added\n\n- old feature\n",
                           encoding="utf-8")
            dig = pu.changelog_digest("6.0.0-rc.1", "6.0.0", log)
            self.assertTrue(dig["available"], dig)
            self.assertEqual(dig["versions"], ["6.0.0"])
            self.assertEqual(dig["groups"], {"Fixed": ["final fix"]})
            wide = pu.changelog_digest("5.1.0", "6.0.0", log)
            self.assertEqual(wide["versions"], ["6.0.0", "6.0.0-rc.1"])
            self.assertEqual(wide["groups"], {"Fixed": ["final fix"], "Added": ["rc feature"]})

    def _migrate(self, root: Path, installed: str, stamped: str) -> str:
        proj = _project(root, stamped)
        sd = _skill(root, installed)
        with mock.patch.object(vc, "skill_root", lambda: sd), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(migrate.main(["--root", str(proj), "--apply"]), 0)
        return (proj / "sdlc-studio" / ".version").read_text(encoding="utf-8")

    def test_migrate_stamps_the_exact_version(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            text = self._migrate(Path(d), installed="6.0.0", stamped="6.0.0-rc.1")
            self.assertIn('skill_version: "6.0.0"\n', text)
            self.assertIn("upgraded_from: 6.0.0-rc.1\n", text)
        with tempfile.TemporaryDirectory() as d:
            text = self._migrate(Path(d), installed="6.0.0-rc.1", stamped="5.1.0")
            self.assertIn('skill_version: "6.0.0-rc.1"\n', text)
            self.assertIn("upgraded_from: 5.1.0\n", text)


if __name__ == "__main__":
    unittest.main()
