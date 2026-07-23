"""Unit tests for `artifact.py retitle` - the deterministic three-surface retitle (US0398).

A title lives in the H1, the filename slug and the index row link/title cell at once, and
until now no command reconciled them. These tests pin the all-validate-then-write contract:
the three surfaces change together in one call, and a retitle blocked on any surface leaves
all three byte-identical (never a half-applied rename)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


file_finding = _load("file_finding")
artifact = _load("artifact")


def _cr_file(crd: Path, title: str, disp: str = "CR-0001", fid: str = "CR0001") -> Path:
    """A minimal, valid CR artefact on disk (H1 + status + a Revision History table)."""
    crd.mkdir(parents=True, exist_ok=True)
    slug = file_finding._slug(title)
    path = crd / f"{fid}-{slug}.md"
    path.write_text(
        f"# {disp}: {title}\n\n> **Status:** Proposed\n> **Priority:** Medium\n"
        f"> **Type:** Improvement\n\n## Summary\n\nx\n\n"
        f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        f"| 2026-07-23 | sdlc | Raised |\n", encoding="utf-8")
    return path


def _cr_index(crd: Path, title: str, disp: str = "CR-0001", fid: str = "CR0001",
              slug: str | None = None) -> Path:
    """A CR index whose single data row links and titles the artefact."""
    crd.mkdir(parents=True, exist_ok=True)
    slug = slug if slug is not None else file_finding._slug(title)
    idx = crd / "_index.md"
    idx.write_text(
        "# Change Request Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n"
        "| Proposed | 1 |\n| **Total** | **1** |\n\n## All Changes\n\n"
        "| ID | Title | Status | Priority | Type | Date |\n"
        "| --- | --- | --- | --- | --- | --- |\n"
        f"| [{disp}]({fid}-{slug}.md) | {title} | Proposed | Medium | Improvement | 2026-07-23 |\n",
        encoding="utf-8")
    return idx


class AtomicRetitleTests(unittest.TestCase):
    def test_h1_filename_and_index_row_all_change_in_one_call(self):
        """AC1: one `retitle` call rewrites the H1, renames the file to the new slug and
        updates the index row's link + title cell, altering no other field."""
        root = Path(tempfile.mkdtemp())
        crd = root / "sdlc-studio" / "change-requests"
        old = "the old title that is quite long indeed yes"
        old_slug = file_finding._slug(old)
        _cr_file(crd, old)
        _cr_index(crd, old)

        new = "the corrected accurate title"
        r = artifact.retitle(root, "CR-0001", new)

        new_slug = file_finding._slug(new)
        # filename slug: the file is renamed, the old one gone
        self.assertTrue((crd / f"CR0001-{new_slug}.md").exists())
        self.assertFalse((crd / f"CR0001-{old_slug}.md").exists())
        # H1: the heading tail reads the new title, the id prefix is kept verbatim
        body = (crd / f"CR0001-{new_slug}.md").read_text(encoding="utf-8")
        self.assertIn(f"# CR-0001: {new}", body)
        self.assertNotIn(old, body.splitlines()[0])
        # index row: the link target is the new slug AND the Title cell reads the new title,
        # with the untouched fields (Status/Priority/Type/Date) preserved exactly
        idx = (crd / "_index.md").read_text(encoding="utf-8")
        row = next(ln for ln in idx.splitlines() if ln.startswith("| [CR-0001]"))
        self.assertIn(f"](CR0001-{new_slug}.md)", row)
        self.assertIn(f"| {new} |", row)
        self.assertNotIn(old, idx)
        self.assertIn("| Proposed | Medium | Improvement | 2026-07-23 |", row)
        self.assertEqual(r["old_title"], old)
        self.assertEqual(r["new_title"], new)

    def test_a_blocked_target_leaves_all_three_untouched(self):
        """AC2 (literal): a retitle blocked because a surface cannot be updated writes
        nothing - the filename, the H1 and the index row are byte-identical, no rename."""
        # (a) destination slug already exists -> the filename surface is blocked
        root = Path(tempfile.mkdtemp())
        crd = root / "sdlc-studio" / "change-requests"
        old = "alpha beta gamma delta epsilon zeta"
        path = _cr_file(crd, old)
        idx = _cr_index(crd, old)
        decoy = crd / "CR0001-taken-slug-value-here.md"  # collides with the new title's slug
        decoy.write_text("decoy", encoding="utf-8")
        file_before, idx_before, decoy_before = (path.read_text(), idx.read_text(),
                                                 decoy.read_text())
        with self.assertRaises(artifact.RetitleBlocked):
            artifact.retitle(root, "CR-0001", "taken slug value here")
        self.assertTrue(path.exists())                       # no rename
        self.assertEqual(path.read_text(), file_before)      # H1 byte-identical
        self.assertEqual(idx.read_text(), idx_before)        # index row byte-identical
        self.assertEqual(decoy.read_text(), decoy_before)    # collision target untouched

        # (b) the index row is missing -> the index surface is blocked, likewise untouched
        root2 = Path(tempfile.mkdtemp())
        crd2 = root2 / "sdlc-studio" / "change-requests"
        path2 = _cr_file(crd2, old)
        idx2 = crd2 / "_index.md"
        idx2.write_text(
            "# I\n\n## All Changes\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [CR-0099](CR0099-other.md) | other | Proposed |\n", encoding="utf-8")
        f2_before, i2_before = path2.read_text(), idx2.read_text()
        with self.assertRaises(artifact.RetitleBlocked):
            artifact.retitle(root2, "CR-0001", "a brand new title string")
        self.assertTrue(path2.exists())
        self.assertEqual(path2.read_text(), f2_before)
        self.assertEqual(idx2.read_text(), i2_before)

    def test_refusal_names_the_blocked_surface_and_the_fix(self):
        """AC3: the refusal states which surface could not be updated and what to do, not a
        bare non-zero exit."""
        # missing index row: the message names the index surface and the corrective command
        root = Path(tempfile.mkdtemp())
        crd = root / "sdlc-studio" / "change-requests"
        _cr_file(crd, "some words for the title here")
        (crd / "_index.md").write_text(
            "# I\n\n## All Changes\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            "| [CR-0099](CR0099-x.md) | x | Proposed |\n", encoding="utf-8")
        with self.assertRaises(artifact.RetitleBlocked) as ctx:
            artifact.retitle(root, "CR-0001", "a replacement title")
        self.assertEqual(ctx.exception.surface, "index")
        msg = str(ctx.exception)
        self.assertIn("index", msg.lower())
        self.assertIn("reconcile", msg)          # names the fix
        self.assertIn("Nothing was written", msg)

        # missing H1 anchor: the message names the H1 surface and how to add it
        root2 = Path(tempfile.mkdtemp())
        crd2 = root2 / "sdlc-studio" / "change-requests"
        bad = crd2 / "CR0001-no-heading.md"
        crd2.mkdir(parents=True)
        bad.write_text("no heading here\n\n> **Status:** Proposed\n", encoding="utf-8")
        with self.assertRaises(artifact.RetitleBlocked) as ctx2:
            artifact.retitle(root2, "CR-0001", "whatever new title")
        self.assertEqual(ctx2.exception.surface, "h1")
        self.assertIn("H1", str(ctx2.exception))


if __name__ == "__main__":
    unittest.main()
