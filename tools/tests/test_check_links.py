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

    def test_archive_subindex_row_resolves_relative_to_the_subindex(self) -> None:
        # archive.py moves ROWS to `<type>/archive/<release>/`, leaving the FILES in the
        # type dir, so an archived row must link two levels up to the artefact.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/archive/v1.0.0/bug.md",
                   "| ID | Status |\n| --- | --- |\n| [BG0001](../../BG0001-x.md) | Fixed |\n")
            _write(root, "sdlc-studio/bugs/BG0001-x.md", "# BG0001\n")
            self.assertEqual(check_links.check_index_links(root / "sdlc-studio"), [])

    def test_archive_subindex_row_at_the_wrong_depth_is_broken(self) -> None:
        # BG0137: a bare filename does NOT resolve from `<type>/archive/<release>/` - it
        # 404s on GitHub. The guard used to read it against the type dir and pass it.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/archive/v1.0.0/bug.md",
                   "| ID | Status |\n| --- | --- |\n| [BG0001](BG0001-x.md) | Fixed |\n")
            _write(root, "sdlc-studio/bugs/BG0001-x.md", "# BG0001\n")
            broken = check_links.check_index_links(root / "sdlc-studio")
            self.assertEqual(len(broken), 1)
            self.assertIn("BG0001-x.md", broken[0])

    def test_main_exits_non_zero_on_a_wrong_depth_archive_link(self) -> None:
        # the public path: a wrong-depth archived row must FAIL the gate
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")
            _write(root, "sdlc-studio/bugs/archive/v1.0.0/bug.md",
                   "| ID | Status |\n| --- | --- |\n| [BG0001](BG0001-x.md) | Fixed |\n")
            _write(root, "sdlc-studio/bugs/BG0001-x.md", "# BG0001\n")
            rc = check_links.main(["--root", str(root / ".claude/skills/sdlc-studio"),
                                   "--repo-root", str(root)])
            self.assertEqual(rc, 1)

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


class BodyLinkTests(unittest.TestCase):
    """BG0138: the index-row pass reads index ROWS only, so a cross-reference inside an
    artefact BODY (a test spec's Stories Covered table, a Traceability row) could name a
    file that is not there and nothing noticed. TS0001 carried 13 such links for weeks.

    The pass is scoped to the workspace on purpose: the skill tree ships placeholder links
    that are MEANT not to resolve here, and a guard that flags payload is a guard people
    learn to ignore.
    """

    def _repo(self, root: Path) -> None:
        """Minimal repo shape: a skill root (so main() runs) and nothing else."""
        _write(root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")

    def test_body_link_to_a_missing_file_is_broken(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/test-specs/TS0001-x.md",
                   "| [US0040](../../stories/US0040-a.md) | thing |\n")
            _write(root, "sdlc-studio/stories/US0040-a.md", "# US0040\n")
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            self.assertEqual(len(broken), 1)
            self.assertIn("../../stories/US0040-a.md", broken[0])

    def test_body_link_resolving_relative_to_its_own_file_passes(self) -> None:
        # `../stories/...` from `test-specs/` is what a reader's click follows
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/test-specs/TS0001-x.md",
                   "| [US0040](../stories/US0040-a.md) | thing |\n"
                   "| PRD | [prd](../prd.md) |\n")
            _write(root, "sdlc-studio/stories/US0040-a.md", "# US0040\n")
            _write(root, "sdlc-studio/prd.md", "# PRD\n")
            self.assertEqual(check_links.check_body_links(root / "sdlc-studio", set()), [])

    def test_anchored_body_link_is_still_file_checked(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/BG0001-x.md", "see [epic](../epics/EP0001-gone.md#scope)\n")
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            self.assertEqual(len(broken), 1)
            self.assertIn("EP0001-gone.md", broken[0])

    def test_indexes_and_archives_are_left_to_the_index_row_pass(self) -> None:
        # no double-reporting: check_index_links already owns these files
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/_index.md",
                   "| [BG0001](BG0001-gone.md) | Open |\n")
            _write(root, "sdlc-studio/bugs/archive/v1.0.0/_index.md",
                   "| [BG0002](BG0002-gone.md) | Fixed |\n")
            self.assertEqual(check_links.check_body_links(root / "sdlc-studio", set()), [])

    def test_body_allowlist_suppresses_a_named_source_target_pair(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "sdlc-studio/bugs/BG0001-x.md", "quoting the defect: [BG](BG9999-gone.md)\n")
            ws = root / "sdlc-studio"
            self.assertEqual(len(check_links.check_body_links(ws, set())), 1)
            allow = {"bugs/BG0001-x.md -> BG9999-gone.md"}
            self.assertEqual(check_links.check_body_links(ws, allow), [])

    def test_main_exits_non_zero_on_a_dead_body_link(self) -> None:
        # THE BUG (BG0138): the gate must FAIL, not merely mention it. A guard that prints a
        # failure and exits 0 is a fail-open - that shipped here as BG0134.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            _write(root, "sdlc-studio/test-specs/TS0001-x.md",
                   "| [US0040](../../stories/US0040-a.md) | thing |\n")
            _write(root, "sdlc-studio/stories/US0040-a.md", "# US0040\n")
            rc = check_links.main(["--root", str(root / ".claude/skills/sdlc-studio"),
                                   "--repo-root", str(root)])
            self.assertEqual(rc, 1)

    def test_main_passes_when_every_body_link_resolves(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._repo(root)
            _write(root, "sdlc-studio/test-specs/TS0001-x.md",
                   "| [US0040](../stories/US0040-a.md) | thing |\n")
            _write(root, "sdlc-studio/stories/US0040-a.md", "# US0040\n")
            rc = check_links.main(["--root", str(root / ".claude/skills/sdlc-studio"),
                                   "--repo-root", str(root)])
            self.assertEqual(rc, 0)

    def test_skill_payload_placeholders_are_not_flagged(self) -> None:
        """The guard must not cry wolf on the skill tree. Templates and best-practice docs
        ship links that resolve in a CONSUMING project, not in this repo: a template's
        `../epics/EP{{epic_id}}-...md`, a style guide's `path/to/guide.md`, a reference's
        `../prd.md`. Those are payload. The body pass never looks at them, so main() stays
        green with all of them present."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            skill = ".claude/skills/sdlc-studio"
            _write(root, f"{skill}/SKILL.md", "# Skill\n")
            _write(root, f"{skill}/templates/core/bug.md",
                   "**Epic:** [EP{{epic_id}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)\n"
                   "**Depends on:** [CR](CR{{dep_id}}-{{dep_slug}}.md)\n")
            _write(root, f"{skill}/best-practices/documentation.md",
                   "See [the guide](path/to/guide.md) and [ref](path/to/ref.md).\n")
            _write(root, f"{skill}/reference-cr.md",
                   "The PRD lives at [prd](../prd.md); epics at "
                   "[EP0001](../epics/EP0001-authentication.md).\n")
            # a real workspace alongside it, entirely clean
            _write(root, "sdlc-studio/test-specs/TS0001-x.md",
                   "| [US0040](../stories/US0040-a.md) |\n")
            _write(root, "sdlc-studio/stories/US0040-a.md", "# US0040\n")
            rc = check_links.main(["--root", str(root / skill), "--repo-root", str(root)])
            self.assertEqual(rc, 0)


class BodyLinkCodeSpanTests(unittest.TestCase):
    """BG0143: a link inside backticks or a fence is an EXAMPLE, not a reference.

    Without this, an artefact cannot DOCUMENT a broken link - and a bug report ABOUT broken
    links must quote the broken link it reports. BG0137 does exactly that, and the body pass
    failed the whole repo on its own bug report.
    """

    def _repo(self, root: Path) -> None:
        _write(root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")

    def test_only_the_live_link_is_reported_not_the_documented_examples(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repo(root)
            _write(root, "sdlc-studio/bugs/BG9999-probe.md",
                   "# BG9999\n\n"
                   "Live: [x](gone-live.md)\n\n"
                   "Span: `[x](gone-span.md)`\n\n"
                   "Fence:\n\n"
                   "```markdown\n"
                   "[x](gone-fence.md)\n"
                   "```\n")
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            joined = " ".join(broken)
            self.assertIn("gone-live.md", joined)       # a real dead reference
            self.assertNotIn("gone-span.md", joined)    # an example, in a code span
            self.assertNotIn("gone-fence.md", joined)   # an example, in a fence
            self.assertEqual(len(broken), 1, broken)

    def test_the_reported_line_number_survives_the_stripping(self):
        """Blanking a fence must not COLLAPSE lines, or every number after it shifts."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repo(root)
            _write(root, "sdlc-studio/bugs/BG9998-probe.md",
                   "# BG9998\n"          # 1
                   "\n"                   # 2
                   "```text\n"            # 3
                   "noise\n"              # 4
                   "```\n"                # 5
                   "\n"                   # 6
                   "Live: [x](gone.md)\n")  # 7
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            self.assertEqual(len(broken), 1, broken)
            self.assertIn(":7 ->", broken[0])

if __name__ == "__main__":
    unittest.main()
