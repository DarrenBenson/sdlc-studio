"""US0975: migrate reports where a project's own docs name retired v5 surface.

`migrate` reported retired keys and verbs only in AGENTS.md, CLAUDE.md and the DoR/DoD, and the
scanner this repository's doc tests use lived under `scripts/tests/` reading this repository's
CHANGELOG, so it could not ship. The scanner now ships as `scripts/lib/retired_surface.py`, and
migrate lists each line of the project's own markdown naming a retired surface as `file:line`
for a human, never rewriting it.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repo

SCRIPTS = Path(__file__).resolve().parent.parent

_README = ("# My project\n\n"
           "After review run `mutation.py register` then `sprint.py close --apply-signoff`.\n"
           "The `mutation.py register` verb was retired in v6.\n")


def _py(*argv: str, scripts: Path = SCRIPTS, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", *argv], capture_output=True, text=True,
                          check=False, timeout=300, cwd=str(cwd) if cwd else None)


class MigrateRetiredDocsTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)

    def test_migrate_names_each_retired_line_and_rewrites_nothing(self) -> None:
        """AC1. MUTANT: HEAD, whose migrate names no README line. MUTANT: rewrite the line - the
        README must stay byte-identical. MUTANT: report a line that says the surface is retired
        (line 4) - only line 3 teaches the retired names."""
        root = self.base / "p"
        root.mkdir()
        proc = _py(str(SCRIPTS / "init.py"), "run", "--root", str(root))
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        readme = root / "README.md"
        readme.write_text(_README, encoding="utf-8")
        before = readme.read_bytes()
        for apply in ((), ("--apply",)):
            with self.subTest(apply=bool(apply)):
                proc = _py(str(SCRIPTS / "migrate.py"), "--root", str(root), *apply)
                out = proc.stdout + proc.stderr
                self.assertEqual(0, proc.returncode, out)
                human = out.split("## Needs a human", 1)[-1] if "## Needs a human" in out else ""
                line3 = [ln for ln in human.splitlines() if "README.md:3" in ln]
                self.assertEqual(1, len(line3), out)
                self.assertIn("mutation.py register", line3[0])
                self.assertIn("sprint.py close --apply-signoff", line3[0])
                self.assertNotIn("README.md:4", human, "a line saying it is retired was reported")
                self.assertEqual(before, readme.read_bytes(), "migrate rewrote the README")

    def test_a_git_project_is_scanned_by_what_it_tracks(self) -> None:
        """In a git work tree the scan reads the TRACKED markdown, and never the skill copy, the
        CHANGELOG or `sdlc-studio/`. MUTANTS: walk the tree regardless (the untracked scratch note
        is reported); read the CHANGELOG (history names retired surface on purpose)."""
        root = self.base / "g"
        root.mkdir()
        self.assertEqual(0, _py(str(SCRIPTS / "init.py"), "run", "--root", str(root)).returncode)
        line = "Run `mutation.py register` first.\n"
        (root / "docs").mkdir()
        (root / "docs" / "guide.md").write_text(line, encoding="utf-8")
        (root / "CHANGELOG.md").write_text(line, encoding="utf-8")
        skill = root / ".claude" / "skills" / "sdlc-studio"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(line, encoding="utf-8")
        gitutil.git(["init", "-q"], root)
        gitutil.git(["add", "-A"], root)
        (root / "scratch.md").write_text(line, encoding="utf-8")       # untracked
        proc = _py(str(SCRIPTS / "migrate.py"), "--root", str(root))
        out = proc.stdout + proc.stderr
        self.assertEqual(0, proc.returncode, out)
        self.assertIn("docs/guide.md:1", out)
        for skipped in ("scratch.md:1", "CHANGELOG.md:1", "SKILL.md:1"):
            self.assertNotIn(skipped, out)

    def test_the_scanner_ships_and_needs_no_changelog(self) -> None:
        """AC2. A copy of the shipped scripts with no CHANGELOG beside the skill: the scanner
        imports and finds a retired verb and a retired config key. MUTANT: HEAD, whose only
        scanner is the test helper reading this repository's CHANGELOG. MUTANT: keep a second
        list in the test helper."""
        skill = self.base / "sdlc-studio"
        shutil.copytree(SCRIPTS, skill / "scripts",
                        ignore=shutil.ignore_patterns("tests", "__pycache__"))
        self.assertFalse((skill / "CHANGELOG.md").exists())
        probe = ("import sys; sys.path.insert(0, sys.argv[1]);"
                 "from lib import retired_surface as r, sdlc_md;"
                 "key = sorted(sdlc_md.RETIRED_CONFIG_KEYS)[0];"
                 "verb = sorted(r.retired_verbs())[0];"
                 "hits = r.live_mentions(f'Run {verb} and set {key}.\\n');"
                 "print(sorted({h[1] for h in hits} & {key, verb}) == sorted({key, verb}))")
        proc = _py("-c", probe, str(skill / "scripts"), cwd=self.base)
        self.assertEqual("True", proc.stdout.strip(), proc.stdout + proc.stderr)
        helper = (SCRIPTS / "tests" / "retired_surface.py").read_text(encoding="utf-8")
        sys.path.insert(0, str(SCRIPTS))
        try:
            from lib import retired_surface as shipped  # noqa: PLC0415
        finally:
            sys.path.remove(str(SCRIPTS))
        for label, pattern in {**shipped.DELETED_VERBS, **shipped.PHRASES}.items():
            self.assertNotIn(pattern, helper, f"the test helper keeps its own copy of {label!r}")
        self.assertNotIn("RETIRED_VERBS = {", helper)


if __name__ == "__main__":
    unittest.main()
