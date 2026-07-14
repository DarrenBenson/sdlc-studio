"""Unit tests for tools/check_links.py (skill-dev link checker).

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
TOOLS = Path(__file__).resolve().parents[1] / "check_links.py"
_spec = importlib.util.spec_from_file_location("check_links", TOOLS)
assert _spec and _spec.loader
check_links = importlib.util.module_from_spec(_spec)
sys.modules["check_links"] = check_links
_spec.loader.exec_module(check_links)


def _write(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


class SlugTests(unittest.TestCase):
    def test_slug_and_explicit_id_stripped(self) -> None:
        self.assertEqual(check_links.slug("Test Organisation (X)"), "test-organisation-x")
        self.assertEqual(check_links.slug("Foo {#bar}"), "foo")


class CheckTests(unittest.TestCase):
    def test_resolves_valid_and_flags_broken(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.md", "## Foo {#foo}\n\n## Plain Heading\n")
            _write(root, "b.md",
                   "see `a.md#foo` and `a.md#plain-heading` and `a.md#missing` and `c.md#x`\n")
            _write(root, "sub/e.md", "rel link `../a.md#foo`\n")  # file-relative, valid
            broken = check_links.check(root, set())
            joined = "\n".join(broken)
            self.assertIn("a.md#missing [anchor missing]", joined)
            self.assertIn("c.md#x [file missing]", joined)
            # Valid references must not be reported.
            self.assertNotIn("a.md#foo", joined)
            self.assertNotIn("a.md#plain-heading", joined)
            self.assertNotIn("../a.md#foo", joined)

    def test_allowlist_suppresses(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "g.md", "example `doc.md#section-name`\n")
            self.assertEqual(check_links.check(root, {"doc.md#section-name"}), [])

    def test_explicit_anchor_on_non_heading_line(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "a.md", "- e. Post-Wave Merge Protocol {#merge}\n")
            _write(root, "b.md", "ref `a.md#merge`\n")
            self.assertEqual(check_links.check(root, set()), [])


class RootDocsTests(unittest.TestCase):
    """The root docs (README, AGENTS, ...) sit outside the skill tree; check_root_docs must
    verify their `.md` links exist, catching a broken link the skill scan never saw."""

    def test_broken_root_doc_link_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("See [contributing](CONTRIBUTING.md).\n", encoding="utf-8")
            broken = check_links.check_root_docs(root)
            self.assertEqual(len(broken), 1)
            self.assertIn("CONTRIBUTING.md", broken[0])

    def test_resolving_root_doc_link_passes(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "CONTRIBUTING.md").write_text("# contributing\n", encoding="utf-8")
            (root / "README.md").write_text("See [contributing](CONTRIBUTING.md).\n", encoding="utf-8")
            self.assertEqual(check_links.check_root_docs(root), [])

    def test_anchored_root_doc_link_checks_the_file(self) -> None:
        # an anchor-carrying root-doc link is still file-checked (anchor ignored)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("[x](docs/missing.md#section)\n", encoding="utf-8")
            broken = check_links.check_root_docs(root)
            self.assertEqual(len(broken), 1)
            self.assertIn("docs/missing.md", broken[0])


class IndexLinkTests(unittest.TestCase):
    """BG0135: an `_index.md` row linking an artefact file that does not exist was
    invisible here - the checker validated ANCHORS, and never scanned the workspace at
    all. A markdown link to a non-existent file must fail the guard, so a phantom row
    cannot survive the gate.
    """

    def _index(self, root: Path, rel: str, rows: str) -> None:
        _write(root, rel, "# Index\n\n| ID | Title | Status |\n| --- | --- | --- |\n" + rows)

    def test_row_linking_a_missing_file_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._index(root, "sdlc-studio/change-requests/_index.md",
                        "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            broken = check_links.check_index_links(root / "sdlc-studio")
            self.assertEqual(len(broken), 1)
            self.assertIn("CR0261-probe.md", broken[0])

    def test_row_linking_a_real_file_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._index(root, "sdlc-studio/change-requests/_index.md",
                        "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            _write(root, "sdlc-studio/change-requests/CR0261-probe.md", "# CR\n")
            self.assertEqual(check_links.check_index_links(root / "sdlc-studio"), [])

    def test_archive_subindex_row_resolves_against_the_type_dir(self) -> None:
        # archive.py moves ROWS to `<type>/archive/<release>/`, leaving the FILES in the
        # type dir, so a sub-index row's bare filename is read from the type dir too.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/archive/v1.0.0/bug.md",
                   "| ID | Status |\n| --- | --- |\n| [BG0001](BG0001-x.md) | Fixed |\n")
            _write(root, "sdlc-studio/bugs/BG0001-x.md", "# BG0001\n")
            self.assertEqual(check_links.check_index_links(root / "sdlc-studio"), [])

    def test_archive_subindex_row_with_no_file_anywhere_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/archive/v1.0.0/bug.md",
                   "| ID | Status |\n| --- | --- |\n| [BG0002](BG0002-gone.md) | Fixed |\n")
            broken = check_links.check_index_links(root / "sdlc-studio")
            self.assertEqual(len(broken), 1)
            self.assertIn("BG0002-gone.md", broken[0])

    def test_main_exits_non_zero_on_a_dead_index_link(self) -> None:
        # the public path: the guard must FAIL the gate, not just print a note
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")
            self._index(root, "sdlc-studio/change-requests/_index.md",
                        "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            rc = check_links.main(["--root", str(root / ".claude/skills/sdlc-studio"),
                                   "--repo-root", str(root)])
            self.assertEqual(rc, 1)

    def test_main_passes_when_every_index_link_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")
            self._index(root, "sdlc-studio/change-requests/_index.md",
                        "| [CR-0261](CR0261-probe.md) | Probe | Proposed |\n")
            _write(root, "sdlc-studio/change-requests/CR0261-probe.md", "# CR\n")
            rc = check_links.main(["--root", str(root / ".claude/skills/sdlc-studio"),
                                   "--repo-root", str(root)])
            self.assertEqual(rc, 0)

    def test_missing_workspace_is_not_a_failure(self) -> None:
        # a consuming repo without a dogfooded workspace must not be failed for it
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(check_links.check_index_links(Path(d) / "sdlc-studio"), [])


if __name__ == "__main__":
    unittest.main()
