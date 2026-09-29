"""BG0808: `init run` records the project's version, so a fresh project's first `migrate` has
nothing to stamp and its first upgrade digest names the range it crossed.

Before the fix `init` wrote no `sdlc-studio/.version`: the project it had just created was
reported by `migrate` as owing one, and `project_upgrade` rendered 'version range unknown'
where the capability digest belonged.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import init  # noqa: E402
import migrate  # noqa: E402
import project_upgrade  # noqa: E402
import version_check  # noqa: E402

_CHANGELOG = """# Changelog

## [6.0.0] - 2026-09-30

### Fixed

- the final release's own entry

## [6.0.0-rc.1] - 2026-09-27

### Added

- the candidate's entry, already installed
"""


def _installed(version: str) -> contextlib.ExitStack:
    """The running skill reports `version`, wherever init, migrate and upgrade ask.

    Each asks `installed_version` (the skill's SKILL.md) on the module object it holds: init
    imports `version_check` as it runs, so reads whatever `sys.modules` holds then, and project
    upgrade (migrate's too) reads the one bound when it was imported. A suite that loads a test
    module installing its own copy in `sys.modules` makes those different objects, so patching
    only this module's binding left init stamping the real SKILL.md's version (BG0846)."""
    readers = (sys.modules["version_check"], project_upgrade.version_check,
               migrate.project_upgrade.version_check)
    stack = contextlib.ExitStack()
    for mod in {id(m): m for m in readers}.values():
        stack.enter_context(unittest.mock.patch.object(mod, "installed_version",
                                                       lambda *_a, **_k: version))
    return stack


def _init(root: Path) -> None:
    gitutil.git(["init", "-q"], cwd=root)
    with contextlib.redirect_stdout(io.StringIO()):
        rc = init.main(["--root", str(root), "run"])
    if rc != 0:
        raise AssertionError(f"init run exited {rc}")


def _skill_version(root: Path) -> str | None:
    m = re.search(r'^skill_version:\s*"?([^"\n]+)"?\s*$',
                  (root / "sdlc-studio" / ".version").read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else None


class InitVersionTests(unittest.TestCase):

    def test_init_stamps_the_skill_version(self) -> None:
        """Mutants: init writes no `.version` (HEAD); init stamps the version with its
        pre-release suffix dropped, which `migrate` then reports as stale; a reader left on the
        real SKILL.md, which only a version no release has carried shows in every layout."""
        real = version_check.installed_version(version_check.skill_root())
        for installed in (real, "6.0.0-rc.1", "9.9.9-rc.1"):
            with self.subTest(installed=installed), tempfile.TemporaryDirectory() as d, \
                    _installed(installed):
                root = Path(d)
                _init(root)
                self.assertEqual(installed, _skill_version(root))
                result = migrate.migrate(root)
                version_items = [i for i in result["deterministic"]
                                 if "version" in str(i.get("kind", "")).lower()
                                 or ".version" in str(i.get("detail", ""))]
                self.assertEqual([], version_items, result["deterministic"])

    def test_a_fresh_project_gets_its_upgrade_digest(self) -> None:
        """Mutant: no recorded version, so the digest reads 'version range unknown'."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with _installed("6.0.0-rc.1"):
                _init(root)
            log = root / "CHANGELOG.md"
            log.write_text(_CHANGELOG, encoding="utf-8")
            out = io.StringIO()
            with _installed("6.0.0"), contextlib.redirect_stdout(out), \
                    unittest.mock.patch.object(project_upgrade, "_changelog_path", lambda: log):
                project_upgrade.main(["--root", str(root)])
            said = out.getvalue()
            self.assertNotIn("version range unknown", said)
            self.assertIn("Changed since 6.0.0-rc.1 (recorded) -> 6.0.0 (installed)", said)
            self.assertIn("the final release's own entry", said)
            self.assertNotIn("the candidate's entry", said)


if __name__ == "__main__":
    unittest.main()
