"""Unit tests for tools/check_versions.py (version-consistency checker).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
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


class StrictBumpTests(unittest.TestCase):
    """US0347 / EP0117: a version bump is refused while ANY authoritative file disagrees, and the
    disagreeing file is NAMED so the fix is one edit, not a hunt."""

    def test_a_single_stale_file_is_named(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            # every home at 5.0.0 except package.json, left stale at 4.1.0
            _fixture(Path(d), pkg="4.1.0", yaml="5.0.0", skill="5.0.0",
                     readme="5.0.0", changelog="5.0.0")
            err = io.StringIO()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
                rc = check_versions.main(["--root", d, "--strict"])
            self.assertNotEqual(rc, 0)                        # refused
            msg = err.getvalue()
            self.assertIn("package.json", msg)                # the disagreeing file, by name
            self.assertIn("4.1.0", msg)                       # ...and its stale value
            self.assertIn("5.0.0", msg)                       # against the version the rest carry

    def test_all_at_5_0_0_passes_strict(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d), pkg="5.0.0", yaml="5.0.0", skill="5.0.0",
                     readme="5.0.0", changelog="5.0.0")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(check_versions.main(["--root", d, "--strict"]), 0)


class VersionTests(unittest.TestCase):
    def setUp(self) -> None:
        # the checker prints its report to stdout and findings to stderr; tests assert on
        # the exit code, so capture both to keep the unittest summary clean
        self._silence = contextlib.ExitStack()
        self._silence.enter_context(contextlib.redirect_stdout(io.StringIO()))
        self._silence.enter_context(contextlib.redirect_stderr(io.StringIO()))

    def tearDown(self) -> None:
        self._silence.close()

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

    def test_prerelease_package_json_normalises_to_core(self) -> None:
        # A pre-release (`4.0.0-rc.1`) in package.json must compare equal to the SEMVER-core
        # `4.0.0` the other homes yield, so an rc release passes the consistency check.
        with tempfile.TemporaryDirectory() as d:
            _fixture(Path(d), pkg="4.0.0-rc.1", yaml="4.0.0", skill="4.0.0",
                     readme="4.0.0", changelog="4.0.0")
            self.assertEqual(check_versions.from_package_json(Path(d)), "4.0.0")
            self.assertEqual(check_versions.main(["--root", d]), 0)

    def test_real_repo_passes(self) -> None:
        repo = Path(__file__).resolve().parents[2]
        self.assertEqual(check_versions.main(["--root", str(repo)]), 0)


class DiscoveredHomesTests(unittest.TestCase):
    """US0452. The guard held a hand-maintained list of spec files, and the list had not been
    extended in two files' worth of drift: `sdlc-studio/trd.md` and `sdlc-studio/tsd.md` were
    never reached. Coverage now follows the REPO, so a home is covered on the day it declares a
    version rather than on the day someone remembers this list exists."""

    def _repo(self, extra: dict | None = None) -> Path:
        import subprocess
        d = Path(tempfile.mkdtemp(prefix="versions_"))
        self.addCleanup(__import__("shutil").rmtree, d, ignore_errors=True)
        (d / "package.json").write_text('{"version": "5.0.0"}', encoding="utf-8")
        (d / "README.md").write_text("# r\n\n**Version:** 5.0.0\n", encoding="utf-8")
        # The two fixed homes main also demands: without them every assertion about the
        # DISCOVERED set would be made against a run that failed for an unrelated reason.
        skill = d / check_versions.SKILL_DIR
        (skill / "templates").mkdir(parents=True)
        (skill / "templates" / "version.yaml").write_text(
            "skill_version: 5.0.0\n", encoding="utf-8")
        (skill / "SKILL.md").write_text(
            "---\nname: sdlc-studio\nmetadata:\n  version: 5.0.0\n---\n# s\n",
            encoding="utf-8")
        ws = d / "sdlc-studio"
        ws.mkdir()
        for name in ("prd.md", "trd.md", "tsd.md"):
            (ws / name).write_text(f"# {name}\n\n**Version:** 5.0.0\n", encoding="utf-8")
        for rel, body in (extra or {}).items():
            (d / rel).parent.mkdir(parents=True, exist_ok=True)
            (d / rel).write_text(body, encoding="utf-8")
        subprocess.run(["git", "-C", str(d), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
        return d

    def test_every_declared_version_home_is_checked(self) -> None:
        """trd.md and tsd.md - the two the four-entry list never reached."""
        root = self._repo()
        homes = check_versions.discover_spec_homes(root)
        self.assertIn("sdlc-studio/trd.md", homes)
        self.assertIn("sdlc-studio/tsd.md", homes)

    def test_a_new_version_home_is_covered_without_editing_the_guard(self) -> None:
        """The whole point: a NEW file declaring a disagreeing version fails the guard with no
        change made to the guard itself."""
        root = self._repo({"sdlc-studio/architecture.md": "# a\n\n**Version:** 4.1.0\n"})
        self.assertIn("sdlc-studio/architecture.md",
                      check_versions.discover_spec_homes(root))
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = check_versions.main(["--root", str(root)])
        self.assertNotEqual(rc, 0, "a new home declaring 4.1.0 did not fail the guard")
        self.assertIn("architecture.md", err.getvalue(), "the drifting file was not named")

    def test_failed_discovery_refuses_to_report_clean(self) -> None:
        """A scan that could not list its own scope has checked nothing, and reporting success
        is the loudest possible lie - it passes trivially exactly when the checkout is wrong."""
        root = self._repo()
        real = check_versions.tracked_markdown

        def boom(_root):
            raise check_versions.DiscoveryFailed("git could not enumerate the tree")

        check_versions.tracked_markdown = boom
        try:
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = check_versions.main(["--root", str(root)])
        finally:
            check_versions.tracked_markdown = real
        self.assertEqual(rc, 1, "a failed discovery reported a clean scan over nothing")
        self.assertIn("nothing was scanned", err.getvalue())

    def test_a_superseded_document_is_not_a_home(self) -> None:
        """A superseded appendix declaring an old version is HISTORY, not drift. Holding it to
        the current version would force a maintainer to falsify the record to go green, which
        is the one thing a truth guard must never demand."""
        root = self._repo({"sdlc-studio/personas.md":
                           "# p\n\n**Version:** 2.0.0\n**Status:** Superseded (historical)\n"})
        self.assertNotIn("sdlc-studio/personas.md",
                         check_versions.discover_spec_homes(root))
        with contextlib.redirect_stderr(io.StringIO()), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, check_versions.main(["--root", str(root)]))

    def test_an_artefact_quoting_a_version_is_not_a_home(self) -> None:
        """A bug REPORTING a version mismatch quotes a version. Holding it to the current one
        would make filing that bug impossible."""
        root = self._repo({"sdlc-studio/bugs/BG0001-x.md":
                           "# BG0001\n\n**Version:** 1.2.3\n"})
        self.assertNotIn("sdlc-studio/bugs/BG0001-x.md",
                         check_versions.discover_spec_homes(root))


if __name__ == "__main__":
    unittest.main()
