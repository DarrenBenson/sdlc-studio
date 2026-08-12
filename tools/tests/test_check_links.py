"""Unit tests for tools/check_links.py (skill-dev link checker).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import shutil
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

class NestedFenceTests(unittest.TestCase):
    """BG0349: the checker tracks fences by the ONE shared CommonMark rule, never a three-character
    toggle. A toggle released a four-backtick block on its inner three-backtick fence, so the
    documented example beneath it was reported as a live broken reference - the guard crying wolf
    on exactly the artefact that DOCUMENTS a broken link."""

    TICK = "`"

    def _repo(self, root: Path) -> None:
        _write(root, ".claude/skills/sdlc-studio/SKILL.md", "# Skill\n")

    def test_a_link_inside_a_nested_fence_is_still_an_example(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repo(root)
            _write(root, "sdlc-studio/bugs/BG9997-probe.md",
                   "# BG9997\n\n"
                   + self.TICK * 4 + "markdown\n"
                   + self.TICK * 3 + "\n"
                   "[x](gone-nested.md)\n"
                   + self.TICK * 3 + "\n"
                   + self.TICK * 4 + "\n")
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            self.assertEqual(broken, [])

    def test_a_fence_carrying_an_info_string_never_closes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repo(root)
            _write(root, "sdlc-studio/bugs/BG9996-probe.md",
                   "# BG9996\n\n"
                   + self.TICK * 3 + "markdown\n"
                   + self.TICK * 3 + "text\n"
                   "[x](gone-info.md)\n"
                   + self.TICK * 3 + "\n")
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            self.assertEqual(broken, [])

    def test_a_live_link_after_the_matching_closer_is_still_reported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repo(root)
            _write(root, "sdlc-studio/bugs/BG9995-probe.md",
                   "# BG9995\n\n"
                   + self.TICK * 4 + "markdown\n"
                   + self.TICK * 3 + "\n"
                   "[x](gone-nested.md)\n"
                   + self.TICK * 3 + "\n"
                   + self.TICK * 4 + "\n\n"
                   "Live: [x](gone-live.md)\n")
            broken = check_links.check_body_links(root / "sdlc-studio", set())
            joined = " ".join(broken)
            self.assertIn("gone-live.md", joined)
            self.assertNotIn("gone-nested.md", joined)

    def test_rename_never_rewrites_a_link_inside_a_nested_fence(self):
        text = (self.TICK * 4 + "markdown\n"
                + self.TICK * 3 + "\n"
                "[x](old.md)\n"
                + self.TICK * 3 + "\n"
                + self.TICK * 4 + "\n")
        new_text, changed = check_links.rewrite_inbound_links(text, "old.md", "new.md")
        self.assertEqual(changed, 0)
        self.assertEqual(new_text, text)


SKILL = Path(__file__).resolve().parents[2] / ".claude" / "skills" / "sdlc-studio"


def _guide_fixture(rows: list[str]) -> Path:
    """A skill root whose SKILL.md holds only a Progressive Loading Guide."""
    d = Path(tempfile.mkdtemp(prefix="guide_"))
    body = ("# Skill\n\n## Progressive Loading Guide\n\n"
            "| Task Type | Primary Load |\n| --- | --- |\n" + "\n".join(rows) + "\n\n## Next\n")
    (d / "SKILL.md").write_text(body, encoding="utf-8")
    return d


class LoadingGuideTests(unittest.TestCase):
    """US0486: every guide cell that PRESENTS a path resolves.

    The existing link passes match `[text](file.md#anchor)`, so they were blind to a bare cell and
    to any non-`.md` path. Five cells shipped naming `modules/trd/c4-diagrams.md` while the tree
    holds `templates/modules/trd/c4-diagrams.md` - a remembered prefix the tree does not use.
    """

    def test_a_cell_naming_a_missing_path_is_reported(self) -> None:
        """AC1. And the message names the PATH, not just the cell, because the fix is the prefix."""
        d = _guide_fixture(["| Doing a thing | does/not/exist.md |"])
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        errors = check_links.check_loading_guide(d)
        self.assertEqual(1, len(errors), f"expected one finding: {errors}")
        self.assertIn("does/not/exist.md", errors[0])
        self.assertIn("not on disk", errors[0])

    def test_a_cell_naming_a_present_path_passes(self) -> None:
        """The positive control: a check that reported every cell would pass the test above."""
        d = _guide_fixture(["| Doing a thing | there.md |"])
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "there.md").write_text("# there\n", encoding="utf-8")
        self.assertEqual([], check_links.check_loading_guide(d))

    def test_anchored_cells_remain_fully_checked(self) -> None:
        """AC2: only templated forms and script invocations are classified out, so the guide's
        strongest existing coverage is not exempted away.

        MUTANT: classify an anchored cell as `prose`, or fold `anchored` into the exempt kinds.
        The live count is asserted, so a reclassification that quietly drops coverage reddens here.
        """
        cells = check_links.loading_guide_cells(SKILL)
        kinds = {}
        for c in cells:
            kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
        self.assertEqual(29, kinds.get("anchored"),
                         f"the anchored-cell count changed: {kinds}. The story's AC said 30; the "
                         f"measured figure is 29, and this pins the measurement rather than the "
                         f"claim")
        for c in cells:
            if c["kind"] == "anchored":
                self.assertTrue(c["path"], "an anchored cell yielded no path to check")
                self.assertTrue(c["anchor"], "an anchored cell lost its anchor")

    def test_bare_and_non_markdown_cells_are_covered(self) -> None:
        """AC3: the bare unanchored cells and the non-markdown ones naming scripts and config.

        The existing patterns match only `.md` links, so every one of these was invisible.
        """
        cells = check_links.loading_guide_cells(SKILL)
        bare = [c for c in cells if c["kind"] == "bare"]
        self.assertGreater(len(bare), 50, "the bare-cell sweep has stopped sweeping")
        exts = {Path(c["path"]).suffix for c in cells if c["path"]}
        self.assertIn(".md", exts)
        self.assertTrue(exts - {".md"},
                        "no non-markdown path is checked, so the scripts and config cells are "
                        "still invisible")

    def test_the_guard_reddens_on_a_mutated_cell(self) -> None:
        """AC4: the guard can GO RED against the live guide, not merely be true when written.

        A cell carrying the LIVE guide's content is repointed at a path that does not exist, and
        the guard must report it. Without this, every other assertion here could hold because the
        tree happens to be clean rather than because the check works - and this is the story whose
        whole subject is a check that was blind to five broken cells.

        THE MUTATION LANDS ON A COPY, NEVER ON THE LIVE FILE. This test used to write the real
        `SKILL.md` and restore it byte-for-byte in a `finally`, which reads as safe and is not:
        `tools/repo_writes.py` reports a restored path precisely BECAUSE a run that edits a tracked
        file and puts it back has raced every concurrent reader of it, and silence about that is
        what made three of four earlier incidents invisible. It also left the skill's own entry
        point one interrupted run away from being the thing a fixture destroyed. The guard caught
        it at a release boundary, which is the whole reason that lane exists.

        The skill tree is 22M, so it is not copied: every child is symlinked and only `SKILL.md` is
        a real file. Path resolution behaves exactly as it does live, and the guide being checked
        holds the live bytes.
        """
        original = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        live = [c for c in check_links.loading_guide_cells(SKILL) if c["path"]]
        self.assertTrue(live, "no path-bearing cell in the live guide to mutate")
        # A path whose string occurs EXACTLY ONCE in the file. Taking `live[0]` blindly mutated the
        # first occurrence anywhere in SKILL.md - often an unrelated mention outside the guide - so
        # the cell was left untouched and the test failed while the guard was working.
        target = next((c["path"] for c in live if original.count(c["path"]) == 1), None)
        self.assertIsNotNone(target, "no guide path appears exactly once, so none can be mutated "
                                     "without also changing an unrelated mention")

        with tempfile.TemporaryDirectory() as d:
            fake = Path(d) / "sdlc-studio"
            fake.mkdir()
            for child in SKILL.iterdir():
                if child.name == "SKILL.md":
                    continue
                (fake / child.name).symlink_to(child)

            (fake / "SKILL.md").write_text(original.replace(target, f"no-such-dir/{target}", 1),
                                           encoding="utf-8")
            errors = check_links.check_loading_guide(fake)
            self.assertTrue(errors, "a cell repointed at a missing path was not reported - the "
                                    "guard cannot go red, so it proves nothing when it is green")
            self.assertTrue(any("no-such-dir" in e for e in errors),
                            f"reported something else instead: {errors[:2]}")

            # The positive control, on the same symlinked root: the UNmutated guide resolves. Without
            # it, the assertion above would also pass for a root where every path is unresolvable.
            (fake / "SKILL.md").write_text(original, encoding="utf-8")
            self.assertEqual([], check_links.check_loading_guide(fake),
                             "the live guide does not resolve through the symlinked root, so the "
                             "red above proves nothing about the mutation")

        self.assertEqual(original, (SKILL / "SKILL.md").read_text(encoding="utf-8"),
                         "the live SKILL.md was written by a test that must never touch it")

    def test_templated_and_invocation_cells_are_classified_OUT_explicitly(self) -> None:
        """An exemption is a decision on the page, not a pattern that quietly matched nothing."""
        d = _guide_fixture(["| A | help/{type}.md |",
                            "| B | `python3 scripts/x.py build` |",
                            "| C | some prose about loading |"])
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        kinds = {c["kind"] for c in check_links.loading_guide_cells(d)}
        self.assertEqual({"templated", "invocation", "prose"}, kinds)
        self.assertEqual([], check_links.check_loading_guide(d),
                         "a templated or invocation cell was treated as a path")

    def test_a_renamed_section_FAILS_LOUD_rather_than_reporting_clean(self) -> None:
        """MUTANT: match the bare phrase instead of the HEADING.

        This is not hypothetical: the first cut used `text.find("Progressive Loading Guide")`, which
        matched a sentence in the intro, so the block ended at the next heading and the sweep read
        ZERO cells while reporting clean - the very failure this story is about, inside its checker.
        """
        d = Path(tempfile.mkdtemp(prefix="guide_none_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "SKILL.md").write_text("# Skill\n\nThe Progressive Loading Guide is below.\n\n"
                                    "## Something Else\n", encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            check_links.loading_guide_cells(d)
        self.assertIn("HEADING", str(ctx.exception))

    def test_the_live_guide_has_a_heading_so_the_checker_is_not_a_no_op_here(self) -> None:
        """The seam's other half. `check_loading_guide` is a no-op for a root with no guide, because
        a consuming project need not have one - so THIS repository having the section is what makes
        the check live, and a rename here must redden rather than quietly become not-applicable.
        """
        import re as _re
        self.assertTrue(_re.search(r"^#{2,3} .*Progressive Loading Guide.*$",
                                   (SKILL / "SKILL.md").read_text(encoding="utf-8"), _re.M),
                        "SKILL.md has no Progressive Loading Guide heading, so the guide check is "
                        "silently not-applicable on the repository that owns it")
        self.assertTrue(check_links.loading_guide_cells(SKILL),
                        "the live guide parses to zero cells")

    def test_a_root_with_no_guide_is_not_applicable_rather_than_an_error(self) -> None:
        """The pre-existing fixtures in this very file are roots with no guide, and the first cut
        made `main()` RAISE on every one of them."""
        d = Path(tempfile.mkdtemp(prefix="noguide_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        self.assertEqual([], check_links.check_loading_guide(d), "an absent SKILL.md errored")
        (d / "SKILL.md").write_text("# Skill\n\n## Something Else\n", encoding="utf-8")
        self.assertEqual([], check_links.check_loading_guide(d), "a guideless SKILL.md errored")

    def test_an_EMPTY_guide_section_refuses_rather_than_reporting_clean(self) -> None:
        """MUTANT: drop the empty-block refusal.

        A heading whose table has been emptied is the same hazard as a renamed one - the sweep reads
        zero cells and reports clean - but it is a DIFFERENT state, so it needs its own fixture: with
        the heading match correct the block is never empty in the live tree, and nothing else here
        reaches the branch.
        """
        d = Path(tempfile.mkdtemp(prefix="guide_empty_"))
        self.addCleanup(shutil.rmtree, d, ignore_errors=True)
        (d / "SKILL.md").write_text("# Skill\n\n## Progressive Loading Guide\n\n## Next\n",
                                    encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            check_links.loading_guide_cells(d)
        self.assertIn("empty", str(ctx.exception))

    def test_the_live_guide_resolves(self) -> None:
        """Against the shipped SKILL.md, because a fixture cannot see a cell that ships broken."""
        self.assertEqual([], check_links.check_loading_guide(SKILL))

    def test_the_check_is_wired_into_the_command(self) -> None:
        """A helper `main` never calls is not a lane."""
        src = TOOLS.read_text(encoding="utf-8")
        self.assertIn("check_loading_guide(root)", src,
                      "the guide check is not called from main(), so the binary the gate runs "
                      "does not perform it")


class LoadingGuideColumnTests(unittest.TestCase):
    """Which column holds a label is decided by the table's own header, not assumed.

    The sweep skipped column 0 unconditionally - true of the guide's first table, false of its
    second, which is headed `| Path | Purpose |`. Its path cells sat in column 0 and were never
    examined, by a check whose entire purpose is to examine them.
    """

    def _cells(self, skill_md: str):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "check_links", Path(__file__).resolve().parents[2] / "tools" / "check_links.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules["check_links"] = mod
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory() as d:
            skill = Path(d)
            (skill / "SKILL.md").write_text(skill_md, encoding="utf-8")
            return mod.loading_guide_cells(skill)

    def test_a_path_column_zero_is_examined(self) -> None:
        """MUTANT: restore the unconditional `cells[1:]`.

        The table is headed `| Path | Purpose |`, so the thing being checked IS column 0.
        """
        cells = self._cells(
            "## Progressive Loading Guide\n\n"
            "| Path | Purpose |\n| --- | --- |\n"
            "| `reference-doctrine.md` | the doctrine |\n")
        paths = [c["path"] for c in cells if c["kind"] in ("anchored", "bare")]
        self.assertIn("reference-doctrine.md", paths,
                      "a path in column 0 of a Path-headed table was never examined")

    def test_a_label_column_zero_is_still_skipped(self) -> None:
        """The control. MUTANT: examine every column unconditionally.

        A task label is not a path, and reading it as one would report a broken link for every
        row of the guide's first table.
        """
        cells = self._cells(
            "## Progressive Loading Guide\n\n"
            "| Task | Read |\n| --- | --- |\n"
            "| Write a PRD | `reference-prd.md` |\n")
        paths = [c["path"] for c in cells if c["kind"] in ("anchored", "bare")]
        self.assertIn("reference-prd.md", paths, "the real path column was not read")
        self.assertNotIn("Write a PRD", [c["cell"] for c in cells],
                         "a task label was read as a path cell")


class RootDocCodeSpanTests(unittest.TestCase):
    """A link inside backticks is an example in a root doc too.

    `check_root_docs` read raw lines while `check_body_links` blanked code spans and fences,
    so the identical text was a reference in one directory and an example in another - and a
    CHANGELOG entry could not quote the link form it was describing. The mutant these hold:
    revert the loop to `path.read_text().splitlines()`.
    """

    def _root(self, body: str) -> Path:
        d = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, d, True)
        (d / "README.md").write_text(body, encoding="utf-8")
        return d

    def test_a_link_inside_a_code_span_is_an_example_not_a_reference(self) -> None:
        root = self._root("The passes match `[text](file.md#anchor)`, so a bare cell was missed.\n")
        self.assertEqual([], check_links.check_root_docs(root),
                         "an example inside backticks was reported as a broken link")

    def test_a_link_inside_a_fence_is_an_example_too(self) -> None:
        root = self._root("Example:\n\n```markdown\n[Epic](../epics/EP0001-x.md)\n```\n")
        self.assertEqual([], check_links.check_root_docs(root),
                         "an example inside a fenced block was reported as a broken link")

    def test_a_live_broken_link_is_still_reported(self) -> None:
        """The control. Blanking code spans must not blank the links the pass exists to find."""
        root = self._root("See [the guide](docs/missing-guide.md) for more.\n")
        broken = check_links.check_root_docs(root)
        self.assertEqual(1, len(broken), f"the live broken link was lost: {broken}")
        self.assertIn("docs/missing-guide.md", broken[0])

    def test_the_reported_line_number_still_points_at_the_line(self) -> None:
        """`_without_code` preserves line COUNT; a pass that collapsed them would misreport."""
        root = self._root("one\ntwo `[x](a.md)`\nthree\n[real](b.md)\n")
        broken = check_links.check_root_docs(root)
        self.assertEqual(["README.md:4 -> b.md [file missing]"], broken)


if __name__ == "__main__":
    unittest.main()
