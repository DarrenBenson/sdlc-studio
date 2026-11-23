# test-census-subject: tools/forward-port.sh
"""tools/forward-port.sh and the installer's CHANGELOG.md.

`install.sh` ships the repository's CHANGELOG.md into the installed skill so `project upgrade`
can digest it offline, but the skill source has none, so a plain `rsync --delete` mirror removed
it on every port. These tests run the script against throwaway copies only, never the real
installed skill.
"""
from __future__ import annotations

import pathlib
import subprocess
import tempfile
import unittest

from test_forward_port import _check_count, _fake_dev_repo, _mirror_target, _run

CURRENT = "# Changelog\n\n## Unreleased\n\n- the repository's current notes\n"


def _repo_with_changelog(d: str) -> pathlib.Path:
    root = _fake_dev_repo(pathlib.Path(d))
    (root / "CHANGELOG.md").write_text(CURRENT, encoding="utf-8")
    return root


class ChangelogSweepTests(unittest.TestCase):
    def test_changelog_survives_the_sweep(self) -> None:
        """AC1. MUTANT: the sweep deleting a target CHANGELOG.md the source tree lacks. A stale
        copy is replaced with the repository's current one, never removed."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _repo_with_changelog(d)
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)
            (target / "CHANGELOG.md").write_text("# stale\n", encoding="utf-8")

            r = _run(root, "--yes", "--target", str(target))

            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual(CURRENT, (target / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_changelog_survives_when_the_repository_holds_none(self) -> None:
        """A repository with no CHANGELOG.md has nothing to ship; the target's copy is left
        exactly as it is rather than deleted."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)
            (target / "CHANGELOG.md").write_text("# installer's\n", encoding="utf-8")

            r = _run(root, "--yes", "--target", str(target))

            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertEqual("# installer's\n",
                             (target / "CHANGELOG.md").read_text(encoding="utf-8"))

    def test_a_dry_run_writes_no_changelog(self) -> None:
        """MUTANT: the copy running outside the --yes branch."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _repo_with_changelog(d)
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)

            r = _run(root, "--target", str(target))

            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((target / "CHANGELOG.md").exists())

    def test_other_strays_are_still_swept(self) -> None:
        """AC2. MUTANT: an exclude that matches more than the one root file - a nested
        CHANGELOG.md and any other stray must still go, so the mirror stays exact."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _repo_with_changelog(d)
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)
            (target / "stray.txt").write_text("x", encoding="utf-8")
            (target / "scripts" / "CHANGELOG.md").write_text("nested", encoding="utf-8")
            (target / "scripts" / "old.py").write_text("y", encoding="utf-8")

            r = _run(root, "--yes", "--target", str(target))

            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse((target / "stray.txt").exists())
            self.assertFalse((target / "scripts" / "CHANGELOG.md").exists())
            self.assertFalse((target / "scripts" / "old.py").exists())
            self.assertTrue((target / "CHANGELOG.md").is_file())


class ChangelogDriftTests(unittest.TestCase):
    def test_check_does_not_count_the_changelog_as_drift(self) -> None:
        """AC3. MUTANT: the check itemising CHANGELOG.md as an extra file to delete."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _repo_with_changelog(d)
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)
            (target / "CHANGELOG.md").write_text(CURRENT, encoding="utf-8")

            r = _run(root, "--check", "--target", str(target))

            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("in sync", r.stdout)
            self.assertNotIn("CHANGELOG", r.stdout)

    def test_check_counts_a_stale_changelog_and_a_missing_one_once_each(self) -> None:
        """The positive control: the exclusion hides only the delete, not a real difference.
        A stale copy and an absent copy are one differing file each, and --yes clears both."""
        for label, seed in (("stale", "# stale\n"), ("missing", None)):
            with self.subTest(label), tempfile.TemporaryDirectory() as d, \
                    tempfile.TemporaryDirectory() as t:
                root = _repo_with_changelog(d)
                target = pathlib.Path(t) / "installed"
                _mirror_target(root, target)
                if seed is not None:
                    (target / "CHANGELOG.md").write_text(seed, encoding="utf-8")

                r = _run(root, "--check", "--target", str(target))

                self.assertEqual(1, r.returncode, r.stdout + r.stderr)
                self.assertEqual(1, _check_count(r.stdout))
                self.assertIn("CHANGELOG.md", r.stdout)
                applied = _run(root, "--yes", "--target", str(target))
                self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
                again = _run(root, "--check", "--target", str(target))
                self.assertEqual(0, again.returncode, again.stdout + again.stderr)

    def test_a_repository_without_a_changelog_does_not_make_the_copy_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as t:
            root = _fake_dev_repo(pathlib.Path(d))
            target = pathlib.Path(t) / "installed"
            _mirror_target(root, target)

            r = _run(root, "--check", "--target", str(target))

            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            self.assertIn("in sync", r.stdout)


if __name__ == "__main__":
    unittest.main()
