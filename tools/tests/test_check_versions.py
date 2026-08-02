"""Unit tests for tools/check_versions.py (version-consistency checker).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import subprocess
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

    def test_a_blockquoted_status_does_not_drop_a_live_home(self) -> None:
        """The first version read the first `**Status:**` within 4000 chars INCLUDING the
        blockquoted form, so a spec quoting an artefact header - which tsd.md already does -
        could silently drop itself as a version home and take its drift with it. Only the
        document's own top-level status speaks for it. Found by an independent reviewer."""
        root = self._repo({"sdlc-studio/spec.md":
                           "# spec\n\n**Version:** 4.1.0\n\n"
                           "Example of an artefact header:\n\n"
                           "> **Status:** Archived\n"})
        self.assertIn("sdlc-studio/spec.md", check_versions.discover_spec_homes(root),
                      "a live document was dropped as a home by a QUOTED status line")
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            rc = check_versions.main(["--root", str(root)])
        self.assertNotEqual(rc, 0, "its 4.1.0 drift was silenced with it")

    def test_the_real_discovery_failure_path_raises(self) -> None:
        """The REAL raise site, not an injected exception. The sibling test monkeypatches
        `tracked_markdown` to raise, so deleting the only genuine `raise DiscoveryFailed`
        changed nothing - it survived as a mutant. Exercised here through an unreadable tree."""
        import os
        import stat
        root = self._repo()
        walled = root / "sdlc-studio" / "walled"
        walled.mkdir(parents=True, exist_ok=True)
        self.assertTrue(hasattr(check_versions, "DiscoveryFailed"),
                        "the guard has no failure type at all")
        # The raise must be reachable from the module, not only from a patched double.
        import inspect
        src = inspect.getsource(check_versions.tracked_markdown)
        self.assertIn("raise DiscoveryFailed", src,
                      "tracked_markdown cannot report a failed discovery, so a tree it could "
                      "not read would degrade to a clean scan over nothing")
        try:
            os.chmod(root, 0o000)
            if os.access(root, os.R_OK):
                self.skipTest("running as a user chmod cannot restrict")
            with self.assertRaises((check_versions.DiscoveryFailed, OSError)):
                check_versions.tracked_markdown(root / "nope" / "deeper")
        finally:
            os.chmod(root, stat.S_IRWXU)

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

    def test_a_fenced_status_example_does_not_drop_a_home_and_hide_its_drift(self) -> None:
        """BG0446, the one REGRESSION this batch introduced.

        Before `_is_superseded` existed, every spec was checked unconditionally, so no
        documentation example could cost a version home. The skip closed the blockquoted case
        and left the fenced one, and a spec DOCUMENTING an artefact header - ordinary technical
        writing, which these specs already do - was then read as declaring ITSELF superseded:
        dropped as a home, taking its real drift with it, exit 0.

        Asserted as a CONTROL PAIR. The drift is identical in both halves; only the presence of
        the example differs. Without the control half, a guard that had stopped checking
        anything at all would also pass.
        """
        drifted = "# TSD\n\n> **Version:** 1.2.3\n\ntext\n"
        example = ("# TSD\n\n```markdown\n**Status:** Superseded\n```\n\n"
                   "> **Version:** 1.2.3\n\ntext\n")
        for label, body in (("control, no example", drifted), ("with the example", example)):
            with self.subTest(case=label):
                root = self._repo({"sdlc-studio/tsd.md": body})
                self.assertIn("sdlc-studio/tsd.md", check_versions.discover_spec_homes(root),
                              "the spec was dropped as a version home")
                with contextlib.redirect_stderr(io.StringIO()), \
                        contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(1, check_versions.main(["--root", str(root)]),
                                     "real version drift was not reported")

    def test_a_fenced_version_example_is_not_read_as_the_documents_version(self) -> None:
        """The mirror image, closed in the same place. Milder - it reports a WRONG version
        rather than silently dropping a home - but it is the same defect, and leaving it would
        hand the next reviewer the other half of a fix that was already being made."""
        root = self._repo({"sdlc-studio/tsd.md":
                           "# TSD\n\n```markdown\n**Version:** 9.9.9\n```\n\n"
                           "> **Version:** 5.0.0\n"})
        self.assertEqual("5.0.0", check_versions.from_spec(root, "sdlc-studio/tsd.md"),
                         "a documented example was read as the document's own version")


class DiscoveryIsNotEnumerationTests(unittest.TestCase):
    """The version guard reaches homes it DISCOVERS, not just the ones it enumerates.

    The original verifier asserted that `trd.md` and `tsd.md` appear in `discover_spec_homes()`
    - and both are members of `SPEC_FILES`, which the function unions in unconditionally. So it
    passed identically with discovery deleted, which is a verifier that cannot fail on its
    subject. Measured on this repo, all three discovered homes are in `SPEC_FILES`, so the
    discriminating case has to be built.
    """

    def _repo(self, d):
        root = Path(d)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
        return root

    def test_a_home_outside_the_enumeration_is_discovered(self) -> None:
        """MUTANT: return `sorted(SPEC_FILES)` and delete the scan.

        The file is version-declaring markdown that is NOT in `SPEC_FILES`, so the assertion
        can only be satisfied by discovery actually running.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_versions", Path(__file__).resolve().parents[1] / "check_versions.py")
        cv = importlib.util.module_from_spec(spec)
        sys.modules["check_versions"] = cv
        spec.loader.exec_module(cv)
        with tempfile.TemporaryDirectory() as d:
            root = self._repo(d)
            (root / "docs").mkdir()
            home = root / "docs" / "handbook.md"
            home.write_text("# Handbook\n\n> **Version:** 1.2.3\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-qm", "add"], cwd=root, check=True)
            homes = cv.discover_spec_homes(root)
        self.assertIn("docs/handbook.md", homes,
                      "a version-declaring file outside SPEC_FILES was not discovered - the "
                      "coverage is enumerated, not discovered")
        self.assertNotIn("docs/handbook.md", cv.SPEC_FILES,
                         "the fixture path is in SPEC_FILES, so this assertion proves nothing")


if __name__ == "__main__":
    unittest.main()
