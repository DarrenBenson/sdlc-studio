"""BG1606: the close's caller check (`critic.py caller-check`) read every declared file that is
not `.md` as a mechanism that needs a named caller, so a unit changing only an `.mdx` page, or a
static site's pages, components and data that its build renders, was reported `[caller-unnamed]`.
An `.mdx` page is now a page as an `.md` one is, and a project names the files its build consumes
in `review.rendered_paths` (globs, empty by default), so they are no mechanism either. Code
outside those globs is still asked for its caller.

Each case drives `critic.py caller-check` through its entry point in a throwaway project.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
CRITIC = SCRIPTS / "critic.py"
UNNAMED = "[caller-unnamed]"
RENDERED = ("review:\n  rendered_paths:\n    - \"src/pages/*\"\n    - \"src/components/*\"\n"
            "    - \"src/data/*\"\n")


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _unit(root: Path, unit: str, *paths: str) -> None:
    """A unit changing `paths` and its fragment, whose criterion names no caller."""
    for rel in paths:
        _write(root, rel, "x\n")
    affects = ", ".join([*paths, f"changelog.d/{unit}.md"])
    _write(root, f"sdlc-studio/stories/{unit}-page.md",
           f"# {unit}: page\n\n> **Status:** Review\n> **Points:** 1\n> **Epic:** EP0001\n"
           f"> **Affects:** {affects}\n\n## Acceptance Criteria\n\n### AC1: the page reads well\n"
           "- **Verify:** shell true\n")


def _check(root: Path, *units: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), "caller-check", "--unit", *units,
                           "--root", str(root)],
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


class CallerCheckRenderedPathsTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _clean(self, r: subprocess.CompletedProcess, n: int) -> None:
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertNotIn("caller-", r.stdout.split("caller-check:")[0], r.stdout)
        self.assertIn(f"caller-check: 0 finding(s) over {n} unit(s)", r.stdout)

    def test_an_mdx_page_is_not_a_mechanism(self) -> None:
        """AC1. Mutants: only `.md` read as a page; the declared-code list beside an empty
        mechanism still counting the `.mdx` page, so the unit is reported indeterminate."""
        _unit(self.root, "US0101", "src/content/blog/post.mdx")
        self._clean(_check(self.root, "US0101"), 1)

    def test_a_declared_rendered_path_is_consumed_by_the_build(self) -> None:
        """AC2. Mutants: `review.rendered_paths` not read; one glob of several honoured."""
        _write(self.root, "sdlc-studio/.config.yaml", RENDERED)
        _unit(self.root, "US0102", "src/pages/index.astro")
        _unit(self.root, "US0103", "src/components/Card.astro")
        _unit(self.root, "US0104", "src/data/nav.json")
        self._clean(_check(self.root, "US0102", "US0103", "US0104"), 3)

    def test_code_outside_the_rendered_paths_is_still_asked_for_a_caller(self) -> None:
        """AC3, the guards. Mutants: every unit exempted; a path exempted by its suffix or by
        sharing a directory prefix with a glob rather than matching one."""
        _write(self.root, "sdlc-studio/.config.yaml", RENDERED)
        _unit(self.root, "US0105", "src/lib/util.ts")
        r = _check(self.root, "US0105")
        self.assertEqual(1, r.returncode, r.stdout)
        self.assertIn(f"US0105 {UNNAMED}", r.stdout)
        self.assertIn("src/lib/util.ts", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            bare = Path(d)
            _unit(bare, "US0102", "src/pages/index.astro")
            r = _check(bare, "US0102")
            self.assertEqual(1, r.returncode, r.stdout)
            self.assertIn(f"US0102 {UNNAMED}", r.stdout)

    def test_a_malformed_rendered_paths_is_refused_by_name(self) -> None:
        """A value that is not a list of globs is refused naming the key, never read as none.
        Mutants: a bare string, or a list holding a number, read as globs or as nothing."""
        _unit(self.root, "US0102", "src/pages/index.astro")
        for value in ("src/pages/*", "[1]", "{a: b}"):
            with self.subTest(value=value):
                _write(self.root, "sdlc-studio/.config.yaml",
                       f"review:\n  rendered_paths: {value}\n")
                r = _check(self.root, "US0102")
                self.assertEqual(2, r.returncode, r.stdout + r.stderr)
                self.assertIn("review.rendered_paths", r.stderr)
        _write(self.root, "sdlc-studio/.config.yaml", "review:\n  rendered_paths:\n")
        r = _check(self.root, "US0102")
        self.assertEqual(1, r.returncode, "an empty value is no glob: the unit is still asked")
        self.assertIn(f"US0102 {UNNAMED}", r.stdout)

    def test_the_key_is_documented_with_an_empty_default(self) -> None:
        """AC4: the shipped default is an empty list, and the configuration reference names the
        key with that default."""
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertEqual([], defaults["review"]["rendered_paths"])
        page = (SKILL / "reference-config.md").read_text(encoding="utf-8")
        row = re.search(r"^\| `review\.rendered_paths` \| `\[\]` \| (.+) \|$", page, re.M)
        self.assertIsNotNone(row, "reference-config.md has no row for the key with its default")
        self.assertIn("caller-check", row.group(1))


if __name__ == "__main__":
    unittest.main()
