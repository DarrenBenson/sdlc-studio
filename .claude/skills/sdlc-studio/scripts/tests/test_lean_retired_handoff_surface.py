"""BG0929: migrate names the retired handoff surface in a project's own docs.

6.1 retired the handoff writers (`handoff.py generate`, `artifact.py new --type handoff`) and
`gate.py --require-handoff`, but none of them sat where migrate's retired-surface scan reads
retirements, so a 6.0 runbook still running them was never named. The verb is registered in
`handoff.py`'s `RETIRED_VERBS` and the two flags in a `#### Retired flags` table, and each
named line carries what replaced the surface. Driven through the shipped `migrate.py` against a
throwaway project.

The table rides in the fix's changelog fragment, so the release cut must fold it without breaking
the CHANGELOG: `CutKeepsTheTableOutOfTheListTests` cuts a fixture holding a fragment of that
shape among others and lints the result.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/lib/retired_surface.py
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
sys.path.insert(0, str(SCRIPTS))
from lib import retired_surface  # noqa: E402

_README = ("# Runbook\n"
           "\n"
           "We read the last handoff before planning, and the handoff writers wrote it.\n"
           "\n"
           "At the close run `handoff.py generate --title \"Sprint 3\"`.\n"
           "\n"
           "```bash\n"
           "python3 scripts/artifact.py new --type handoff --title \"Sprint 3\"\n"
           "python3 scripts/gate.py --release --require-handoff HO0003\n"
           "```\n")

#: README line -> (the surface it must be named for, a phrase of what replaced it).
_EXPECTED = {
    5: ("handoff.py generate", "sprint.py plan --worklist RPTxxxx"),
    8: ("artifact.py new --type handoff", "sprint.py plan --worklist RPTxxxx"),
    9: ("gate.py --require-handoff", "sprint.py sign"),
}


def _py(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", *argv], capture_output=True, text=True,
                          check=False, timeout=300)


class RetiredHandoffSurfaceTests(unittest.TestCase):
    """AC1."""

    def test_the_retired_handoff_surface_is_named(self) -> None:
        """AC1. MUTANT: HEAD's scan, which names none of lines 5, 8 and 9 (no `RETIRED_VERBS`
        entry in handoff.py, no retired-flag row for either flag). MUTANT: a named line with no
        replacement (the detail as it read before, `names the retired X - edit it`). The
        control: line 3 names handoffs in prose and is not reported."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "p"
            root.mkdir()
            proc = _py(str(SCRIPTS / "init.py"), "run", "--root", str(root))
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            (root / "README.md").write_text(_README, encoding="utf-8")
            proc = _py(str(SCRIPTS / "migrate.py"), "--root", str(root))
            out = proc.stdout + proc.stderr
            self.assertEqual(0, proc.returncode, out)
            named = {int(ln.split("README.md:", 1)[1].split()[0]): ln
                     for ln in out.splitlines() if "README.md:" in ln}
            self.assertEqual(sorted(_EXPECTED), sorted(named), out)
            for line, (surface, replacement) in _EXPECTED.items():
                with self.subTest(line=line):
                    self.assertIn(f"`{surface}`", named[line])
                    self.assertIn(replacement, named[line].split(f"`{surface}`", 1)[1])


_CHANGELOG = ("# Changelog\n"
              "\n"
              "## [Unreleased]\n"
              "\n"
              "## [6.0.0] - 2026-09-29\n"
              "\n"
              "### Fixed\n"
              "\n"
              "- An old fix (BG0001).\n")

#: The shape of changelog.d/BG0929.md: a wrapped bullet, then a `#### Retired flags` table.
_TABLE_FRAGMENT = (
    "<!-- section: Fixed -->\n"
    "\n"
    "- `migrate` names the retired handoff commands where a project's own markdown docs still\n"
    "  run them in code (BG0929).\n"
    "\n"
    "#### Retired flags\n"
    "\n"
    "| Before (v6.0) | After (v6.1) | Migration |\n"
    "| --- | --- | --- |\n"
    "| `artifact.py new --type handoff` | Removed (argparse error) | "
    "`sprint.py plan --worklist RPTxxxx` |\n"
    "| `gate.py --require-handoff` | Removed (argparse error) | the signed sprint report |\n")

#: Fragment file -> (its section, its text). Two Fixed fragments sort either side of the table's.
_OTHERS = {
    "BG0002.md": ("Fixed", "<!-- section: Fixed -->\n\n- An early fix (BG0002).\n"),
    "BG0999.md": ("Fixed", "<!-- section: Fixed -->\n\n- A late fix (BG0999).\n"),
    "US0001.md": ("Added", "<!-- section: Added -->\n\n- A new thing (US0001).\n"),
}

#: The control cut, as it read before the table fragment existed: bullets only, newest first.
_CONTROL = ("# Changelog\n"
            "\n"
            "## [Unreleased]\n"
            "\n"
            "## [6.1.0] - DATE\n"
            "\n"
            "### Added\n"
            "\n"
            "- A new thing (US0001).\n"
            "\n"
            "### Fixed\n"
            "\n"
            "- A late fix (BG0999).\n"
            "- An early fix (BG0002).\n"
            "\n"
            "## [6.0.0] - 2026-09-29\n"
            "\n"
            "### Fixed\n"
            "\n"
            "- An old fix (BG0001).\n")


def _markdownlint() -> str:
    """The markdownlint the repository's markdown lane runs, or a skip naming what is missing."""
    local = REPO / "node_modules" / ".bin" / "markdownlint"
    if local.is_file() and os.access(local, os.X_OK):
        return str(local)
    found = shutil.which("markdownlint")
    if found and (REPO / ".markdownlint.json").is_file():
        return found
    raise unittest.SkipTest("markdownlint or the repository's .markdownlint.json is absent")


def _cut(test: unittest.TestCase, fragments: dict[str, str]) -> tuple[Path, str]:
    """Cut 6.1.0 through the shipped `release_cut.py` in a throwaway project; (CHANGELOG path,
    its text with the cut's date replaced by DATE)."""
    root = Path(tempfile.mkdtemp())
    test.addCleanup(shutil.rmtree, root, True)
    (root / "changelog.d").mkdir()
    (root / "CHANGELOG.md").write_text(_CHANGELOG, encoding="utf-8")
    for name, text in fragments.items():
        (root / "changelog.d" / name).write_text(text, encoding="utf-8")
    proc = _py(str(SCRIPTS / "release_cut.py"), "--root", str(root), "changelog-cut",
               "--version", "6.1.0")
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    clog = root / "CHANGELOG.md"
    text = re.sub(r"(?m)^(## \[6\.1\.0\] - )\S+$", r"\1DATE", clog.read_text(encoding="utf-8"))
    return clog, text


class CutKeepsTheTableOutOfTheListTests(unittest.TestCase):
    """The repair of BG0929's review: its fragment is the first to carry a `####` table, and the
    cut folded it mid-list, so the cut CHANGELOG failed the markdown lane (MD058, MD032) and the
    later Fixed entries sat under `#### Retired flags`."""

    def test_the_cut_places_the_table_after_its_sections_bullets(self) -> None:
        """MUTANT: HEAD's compose, which inserts the whole fragment at the top of `### Fixed`, so
        the table runs straight into the next bullet: markdownlint reports MD058 and MD032, and
        BG0002's bullet sits under `#### Retired flags`. MUTANT: the table dropped from the cut
        entry, so the scan reads no row once the fragment is consumed."""
        lint = _markdownlint()
        frags = {name: text for name, (_s, text) in _OTHERS.items()}
        frags["BG0929.md"] = _TABLE_FRAGMENT
        clog, text = _cut(self, frags)
        self.assertFalse(list((clog.parent / "changelog.d").glob("*.md")), "fragments consumed")
        proc = subprocess.run([lint, "--config", str(REPO / ".markdownlint.json"), str(clog)],
                              capture_output=True, text=True, check=False, timeout=120)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr + text)
        heading, found = None, {}
        for line in text.split("## [6.0.0]", 1)[0].splitlines():
            if line.startswith("#"):
                heading = line
            unit = re.search(r"\(((?:BG|US)\d{4})\)\.$", line)
            if unit:
                found[unit.group(1)] = heading
        sections = {"BG0929": "Fixed", **{n[:-3]: s for n, (s, _t) in _OTHERS.items()}}
        self.assertEqual({u: f"### {s}" for u, s in sections.items()}, found, text)
        self.assertEqual(["artifact.py new --type handoff", "gate.py --require-handoff"],
                         retired_surface.changelog_flags(clog))

    def test_a_cut_with_no_table_is_unchanged(self) -> None:
        """The control: a cut of bullet-only fragments reads exactly as it did before."""
        _clog, text = _cut(self, {name: text for name, (_s, text) in _OTHERS.items()})
        self.assertEqual(_CONTROL, text)


if __name__ == "__main__":
    unittest.main()
