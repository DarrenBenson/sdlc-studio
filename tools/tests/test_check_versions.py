"""Unit tests for tools/check_versions.py (version-consistency checker).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

# tools/ lives at the repo root, six parents up from this test file.
TOOLS = Path(__file__).resolve().parents[1] / "check_versions.py"
_spec = importlib.util.spec_from_file_location("check_versions", TOOLS)
assert _spec and _spec.loader
check_versions = importlib.util.module_from_spec(_spec)
sys.modules["check_versions"] = check_versions
_spec.loader.exec_module(check_versions)


def _fixture(root: Path, pkg="2.0.0", yaml="2.0.0", skill="2.0.0",
             readme="2.0.0", changelog="2.0.0") -> None:
    (root / "package.json").write_text('{"version": "%s"}' % pkg)
    sd = root / ".claude/skills/sdlc-studio"
    (sd / "templates").mkdir(parents=True)
    (sd / "templates" / "version.yaml").write_text(
        'schema_version: 2\nskill_version: "%s"  # comment\n' % yaml)
    (sd / "SKILL.md").write_text(
        '---\nname: sdlc-studio\ndescription: "x"\nmetadata:\n  version: "%s"\n---\n# T\n'
        % skill)
    (root / "README.md").write_text("# SDLC Studio\n\n**Version:** v%s\n" % readme)
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n- x\n\n## [%s] - 2026-06-12\n" % changelog)


class VersionTests(unittest.TestCase):
    def test_consistent_versions_pass(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d))
            self.assertEqual(check_versions.main(["--root", d]), 0)

    def test_strict_passes_when_changelog_matches(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d))
            self.assertEqual(check_versions.main(["--root", d, "--strict"]), 0)

    def test_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d), pkg="2.0.1")
            self.assertEqual(check_versions.main(["--root", d]), 1)

    def test_changelog_lag_is_advisory_without_strict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d), changelog="1.9.1")
            self.assertEqual(check_versions.main(["--root", d]), 0)

    def test_changelog_lag_fails_strict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d), changelog="1.9.1")
            self.assertEqual(check_versions.main(["--root", d, "--strict"]), 1)

    def test_unreleased_heading_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d))
            self.assertEqual(check_versions.from_changelog(Path(d)), "2.0.0")

    def test_prose_mentions_are_ignored(self) -> None:
        # A different version string in skill prose must not trip the check.
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d))
            ref = Path(d) / ".claude/skills/sdlc-studio" / "reference-x.md"
            ref.write_text("Example output mentions v9.9.9 here.\n")
            self.assertEqual(check_versions.main(["--root", d]), 0)

    def test_missing_location_fails(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d))
            (Path(d) / "package.json").unlink()
            self.assertEqual(check_versions.main(["--root", d]), 1)

    def test_real_repo_passes(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        self.assertEqual(check_versions.main(["--root", str(repo)]), 0)


if __name__ == "__main__":
    unittest.main()
