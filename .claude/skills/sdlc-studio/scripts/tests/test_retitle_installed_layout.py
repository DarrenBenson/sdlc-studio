"""Retitle from an installed skill in a consuming project.

An installed skill is the skill directory alone (`~/.claude/skills/sdlc-studio/`): no
repository around it, so no `tools/` directory, and a consuming project has none of its own.
The retitle must still find and rewrite every inbound reference there, which means the scan
it runs is shipped payload and not a repository tool loaded by path.

The test copies the shipped `scripts/` tree into an installed-layout home directory, builds a
consuming project with no `tools/`, and runs the copy's `artifact.py retitle` as a subprocess,
so nothing from this repository's checkout can be reached by the code under test.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/artifact.py
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent

OLD = "the mistaken title needing correction now"
OLD_SLUG = "the-mistaken-title-needing-correction-now"
NEW = "the corrected title"
NEW_SLUG = "the-corrected-title"


def _install(base: Path) -> Path:
    """The shipped scripts copied to `<base>/home/.claude/skills/sdlc-studio/scripts`,
    tests and caches left out, as an install lays them down. Returns the scripts directory."""
    dest = base / "home" / ".claude" / "skills" / "sdlc-studio" / "scripts"
    shutil.copytree(SCRIPTS, dest, ignore=shutil.ignore_patterns("tests", "__pycache__"))
    return dest


def _project(base: Path) -> tuple[Path, Path, Path]:
    """A consuming project holding one CR, its index row, an epic that links to the CR and also
    quotes the link in a code span (so the rewriter reads the example), and an epic that only
    quotes it (so the finder must skip it). Returns (root, linking epic, quoting epic)."""
    root = base / "project"
    crd = root / "sdlc-studio" / "change-requests"
    crd.mkdir(parents=True)
    (crd / f"CR0001-{OLD_SLUG}.md").write_text(
        f"# CR-0001: {OLD}\n\n> **Status:** Proposed\n\n## Summary\n\nx\n\n"
        "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        "| 2026-07-23 | sdlc | Raised |\n", encoding="utf-8")
    (crd / "_index.md").write_text(
        "# CR Index\n\n## All Changes\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [CR-0001](CR0001-{OLD_SLUG}.md) | {OLD} | Proposed |\n", encoding="utf-8")
    epd = root / "sdlc-studio" / "epics"
    epd.mkdir(parents=True)
    linking = epd / "EP0001-container.md"
    linking.write_text(
        "# EP0001: container\n\n> **Status:** Draft\n\n## Summary\n\n"
        f"Delivered by [CR-0001](../change-requests/CR0001-{OLD_SLUG}.md#summary).\n\n"
        f"Quoted as `[x](../change-requests/CR0001-{OLD_SLUG}.md)` in the guide.\n",
        encoding="utf-8")
    quoting = epd / "EP0002-example.md"
    quoting.write_text(
        "# EP0002: example\n\n> **Status:** Draft\n\n## Summary\n\n"
        f"An example: `[x](../change-requests/CR0001-{OLD_SLUG}.md)`.\n", encoding="utf-8")
    return root, linking, quoting


class RetitleInstalledLayoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = Path(tempfile.mkdtemp(prefix="retitle_installed_"))
        self.addCleanup(shutil.rmtree, self.base, True)
        self.scripts = _install(self.base)
        self.root, self.linking, self.quoting = _project(self.base)
        home = self.base / "home"
        self.env = {**os.environ, "HOME": str(home), "XDG_DATA_HOME": str(home / ".local"),
                    "CLAUDE_CONFIG_DIR": str(home / ".claude")}

    def _retitle(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.scripts / "artifact.py"), "retitle", "--root",
             str(self.root), "--id", "CR-0001", "--title", NEW, *extra],
            cwd=self.root, env=self.env, capture_output=True, text=True, timeout=300,
            check=False)

    def test_the_fixture_has_no_check_links_anywhere_the_retitle_could_reach(self) -> None:
        """The guard on the fixture: neither the project nor the installed skill's parents
        hold a `tools/check_links.py`, so a pass below cannot come from loading one."""
        self.assertFalse((self.root / "tools").exists())
        for parent in self.scripts.parents:
            self.assertFalse((parent / "tools" / "check_links.py").exists(), parent)

    def test_retitle_rewrites_inbound_links_without_tools_check_links(self) -> None:
        r = self._retitle()
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
        crd = self.root / "sdlc-studio" / "change-requests"
        self.assertTrue((crd / f"CR0001-{NEW_SLUG}.md").exists())
        self.assertFalse((crd / f"CR0001-{OLD_SLUG}.md").exists())
        text = self.linking.read_text(encoding="utf-8")
        # the link is repointed, keeping its directory prefix and its anchor
        self.assertIn(f"Delivered by [CR-0001](../change-requests/CR0001-{NEW_SLUG}.md#summary).",
                      text)
        # an example in a code span is not a reference, so the rename leaves it alone, both
        # beside a real link in a file the rewriter reads and in a file the finder skips
        example = f"`[x](../change-requests/CR0001-{OLD_SLUG}.md)`"
        self.assertEqual(text.count(OLD_SLUG), 1, text)
        self.assertIn(f"Quoted as {example} in the guide.", text)
        self.assertIn(example, self.quoting.read_text(encoding="utf-8"))
        self.assertIn(f"CR0001-{NEW_SLUG}.md", (crd / "_index.md").read_text(encoding="utf-8"))

    def test_the_dry_run_names_the_reference_and_writes_nothing(self) -> None:
        before = self.linking.read_bytes()
        r = self._retitle("--dry-run", "--format", "json")
        self.assertEqual(r.returncode, 0, f"stdout={r.stdout}\nstderr={r.stderr}")
        self.assertEqual(json.loads(r.stdout)["references"],
                         ["sdlc-studio/epics/EP0001-container.md"])
        self.assertEqual(self.linking.read_bytes(), before)
        self.assertTrue((self.root / "sdlc-studio" / "change-requests"
                         / f"CR0001-{OLD_SLUG}.md").exists())


if __name__ == "__main__":
    unittest.main()
