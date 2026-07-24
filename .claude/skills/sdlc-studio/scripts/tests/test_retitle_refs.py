"""Unit tests for the retitle's inbound-reference handling and its record (US0399).

A rename must not leave a dangling link: every inbound reference is rewritten to the new
slug, or the retitle refuses and NAMES the references it cannot rewrite; and the retitle is
recorded on the artefact with the previous title so the change is legible."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
import unittest.mock
from datetime import date
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load_from(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load(name: str):
    return _load_from(name, SCR / f"{name}.py")


file_finding = _load("file_finding")
artifact = _load("artifact")

# check_links is a repo CI tool (tools/), not shipped runtime - the retitle locates it, and the
# tests check its inbound scan directly, so resolve it the same way the module does.
_CL_PATH = SCR.resolve().parents[3] / "tools" / "check_links.py"
check_links = _load_from("check_links", _CL_PATH) if _CL_PATH.exists() else None


def _cr(crd: Path, title: str, disp: str = "CR-0001", fid: str = "CR0001") -> Path:
    crd.mkdir(parents=True, exist_ok=True)
    slug = file_finding._slug(title)
    path = crd / f"{fid}-{slug}.md"
    path.write_text(
        f"# {disp}: {title}\n\n> **Status:** Proposed\n\n## Summary\n\nx\n\n"
        f"## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n"
        f"| 2026-07-23 | sdlc | Raised |\n", encoding="utf-8")
    return path


def _cr_index(crd: Path, title: str, disp: str = "CR-0001", fid: str = "CR0001") -> Path:
    slug = file_finding._slug(title)
    idx = crd / "_index.md"
    idx.write_text(
        "# CR Index\n\n## All Changes\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
        f"| [{disp}]({fid}-{slug}.md) | {title} | Proposed |\n", encoding="utf-8")
    return idx


class InboundRefTests(unittest.TestCase):
    @unittest.skipIf(check_links is None, "tools/check_links.py not present")
    def test_inbound_links_are_rewritten_to_the_new_slug(self):
        """AC1: every inbound link the check_links scan finds is repointed to the new slug,
        so link resolution reports no new break."""
        root = Path(tempfile.mkdtemp())
        crd = root / "sdlc-studio" / "change-requests"
        old = "the mistaken title needing correction now"
        old_slug = file_finding._slug(old)
        target = _cr(crd, old)
        _cr_index(crd, old)
        # an inbound reference from another artefact's body, by the old slug
        epd = root / "sdlc-studio" / "epics"
        epd.mkdir(parents=True)
        epic = epd / "EP0001-container.md"
        epic.write_text(
            "# EP0001: container\n\n> **Status:** Draft\n\n## Summary\n\n"
            f"Delivered by [CR-0001](../change-requests/CR0001-{old_slug}.md).\n\n"
            "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n",
            encoding="utf-8")
        # the check_links scan finds it before the rename
        found = check_links.inbound_references(root, target.name)
        self.assertIn(epic.relative_to(root).as_posix(), [f["rel"] for f in found])

        new = "the corrected title"
        r = artifact.retitle(root, "CR-0001", new)
        new_slug = file_finding._slug(new)

        text = epic.read_text(encoding="utf-8")
        self.assertIn(f"CR0001-{new_slug}.md", text)          # rewritten to the new slug
        self.assertNotIn(f"CR0001-{old_slug}.md", text)       # no dangling old link
        self.assertIn(epic.relative_to(root).as_posix(), r["references"])
        # and link resolution finds no break against the renamed file
        broken = check_links.check_body_links(root / "sdlc-studio", set())
        self.assertEqual([b for b in broken if "CR0001" in b], [])

    @unittest.skipIf(check_links is None, "tools/check_links.py not present")
    def test_an_unrewritable_reference_blocks_the_rename_and_is_named(self):
        """AC2: an inbound reference the retitle cannot safely rewrite (a row in immutable
        archived history) blocks the rename and is named - never renamed-and-left-dangling."""
        root = Path(tempfile.mkdtemp())
        crd = root / "sdlc-studio" / "change-requests"
        old = "a well cited title in the archive"
        target = _cr(crd, old)
        _cr_index(crd, old)
        arch = crd / "archive" / "v1"
        arch.mkdir(parents=True)
        arch_idx = arch / "_index.md"
        arch_idx.write_text(
            "# Archived\n\n## Rows\n\n| ID | Title | Status |\n| --- | --- | --- |\n"
            f"| [CR-0001](../../{target.name}) | {old} | Complete |\n", encoding="utf-8")
        target_before, arch_before = target.read_text(), arch_idx.read_text()

        with self.assertRaises(artifact.RetitleBlocked) as ctx:
            artifact.retitle(root, "CR-0001", "a rewritten title attempt")
        self.assertEqual(ctx.exception.surface, "references")
        self.assertIn(arch_idx.relative_to(root).as_posix(), str(ctx.exception))
        # no rename occurred and both surfaces are untouched
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(), target_before)
        self.assertEqual(arch_idx.read_text(), arch_before)


class RetitleRecordTests(unittest.TestCase):
    @unittest.skipIf(check_links is None, "tools/check_links.py not present")
    def test_a_revision_row_records_the_old_title(self):
        """AC3: a successful retitle writes a dated Revision History row naming the retitle
        and the previous title, via the shared revision machinery."""
        root = Path(tempfile.mkdtemp())
        crd = root / "sdlc-studio" / "change-requests"
        old = "the previous title before the fix here"
        _cr(crd, old)
        _cr_index(crd, old)

        artifact.retitle(root, "CR-0001", "the fixed title")
        new_body = next(p for p in crd.glob("CR0001-*.md")).read_text(encoding="utf-8")
        rev = new_body.split("## Revision History", 1)[1]
        # the old title is legible in a new revision row that names the retitle
        added = [ln for ln in rev.splitlines() if ln.startswith("|") and old in ln]
        self.assertEqual(len(added), 1)
        self.assertRegex(added[0].lower(), r"retitl")
        self.assertIn(date.today().isoformat(), added[0])


class RetitleRollbackTests(unittest.TestCase):
    """The write phase is atomic-or-rolled-back (BG0274).

    `retitle` is documented as all-validate-then-write, but that guarantee held only on the
    refusal path: past validation the writes were an unjournalled sequence, so a fault in the
    inbound-rewrite loop left the file renamed, the index updated and the references half
    rewritten - the exact split-surface state validate-first exists to prevent.
    """

    def _fixture(self, root: Path):
        """A CR with an index row and TWO inbound references, so a fault on the second has a
        first one to leave behind."""
        crd = root / "sdlc-studio" / "change-requests"
        old = "the title that must survive a failed rewrite"
        old_slug = file_finding._slug(old)
        target = _cr(crd, old)
        idx = _cr_index(crd, old)
        epd = root / "sdlc-studio" / "epics"
        epd.mkdir(parents=True)
        refs = []
        for n, name in ((1, "first"), (2, "second")):
            p = epd / f"EP000{n}-{name}.md"
            p.write_text(
                f"# EP000{n}: {name}\n\n> **Status:** Draft\n\n## Summary\n\n"
                f"Delivered by [CR-0001](../change-requests/CR0001-{old_slug}.md).\n\n"
                "## Revision History\n\n| Date | Author | Change |\n| --- | --- | --- |\n",
                encoding="utf-8")
            refs.append(p)
        return target, idx, refs, old

    def _failing_write(self, doomed: Path, also_fail_restore: Path | None = None):
        """Stand in for a write that faults partway through the loop. `also_fail_restore` makes
        the ROLLBACK of that path fail too, which is the only way to test the honest report of
        a partial rollback."""
        real_atomic = artifact.sdlc_md.atomic_write
        real_bytes = Path.write_bytes

        def atomic(p, text, *a, **kw):
            if Path(p) == doomed:
                raise OSError(f"simulated fault writing {p}")
            return real_atomic(p, text, *a, **kw)

        def write_bytes(self, data):  # noqa: ANN001 - patched onto Path
            if also_fail_restore is not None and Path(self) == also_fail_restore:
                raise OSError(f"simulated fault restoring {self}")
            return real_bytes(self, data)

        return atomic, write_bytes

    @unittest.skipIf(check_links is None, "tools/check_links.py not present")
    def test_a_fault_mid_write_leaves_every_surface_byte_identical(self):
        """AC1: the file, its name, the index row and the already-rewritten reference all
        go back exactly as they were."""
        root = Path(tempfile.mkdtemp())
        target, idx, refs, old = self._fixture(root)
        before = {p: p.read_bytes() for p in (target, idx, *refs)}
        new = "a corrected title that never lands"
        dest = target.with_name(f"CR0001-{file_finding._slug(new)}.md")

        atomic, _ = self._failing_write(refs[1])
        with unittest.mock.patch.object(artifact.sdlc_md, "atomic_write", atomic):
            with self.assertRaises(artifact.RetitleBlocked):
                artifact.retitle(root, "CR-0001", new)

        self.assertFalse(dest.exists(), "the destination file was left behind")
        for p, b in before.items():
            self.assertTrue(p.exists(), f"{p.name} was not restored")
            self.assertEqual(p.read_bytes(), b, f"{p.name} differs from before the retitle")
        # named explicitly: the rename, the index row and the FIRST reference are the three
        # surfaces the unjournalled version left changed
        self.assertIn(old, target.read_text(encoding="utf-8"))
        self.assertIn(f"CR0001-{file_finding._slug(old)}.md", idx.read_text(encoding="utf-8"))
        self.assertIn(f"CR0001-{file_finding._slug(old)}.md",
                      refs[0].read_text(encoding="utf-8"))

    @unittest.skipIf(check_links is None, "tools/check_links.py not present")
    def test_the_fault_is_reported_and_the_cli_exits_non_zero(self):
        """AC2: the caller is told which write failed and that the tree was put back."""
        root = Path(tempfile.mkdtemp())
        _target, _idx, refs, _old = self._fixture(root)
        atomic, _ = self._failing_write(refs[1])
        with unittest.mock.patch.object(artifact.sdlc_md, "atomic_write", atomic):
            with self.assertRaises(artifact.RetitleBlocked) as ctx:
                artifact.retitle(root, "CR-0001", "another title that never lands")
            self.assertEqual(ctx.exception.surface, "write")
            self.assertIn(str(refs[1]), str(ctx.exception))
            self.assertIn("rolled back", str(ctx.exception).lower())
            self.assertIsInstance(ctx.exception.__cause__, OSError)  # never swallowed
            err = io.StringIO()
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                rc = artifact.main(["retitle", "--id", "CR-0001", "--title",
                                    "a third title that never lands", "--root", str(root)])
            self.assertNotEqual(rc, 0)
            self.assertIn("rolled back", err.getvalue().lower())

    @unittest.skipIf(check_links is None, "tools/check_links.py not present")
    def test_a_failed_rollback_names_what_it_could_not_restore(self):
        """AC3: a partial rollback reported as a clean one is worse than the fault itself."""
        root = Path(tempfile.mkdtemp())
        target, _idx, refs, _old = self._fixture(root)
        atomic, write_bytes = self._failing_write(refs[1], also_fail_restore=refs[0])
        with unittest.mock.patch.object(artifact.sdlc_md, "atomic_write", atomic), \
                unittest.mock.patch.object(Path, "write_bytes", write_bytes):
            with self.assertRaises(artifact.RetitleBlocked) as ctx:
                artifact.retitle(root, "CR-0001", "a title whose rollback also fails")
        msg = str(ctx.exception)
        self.assertIn(str(refs[0]), msg)                 # names the surface left unrestored
        self.assertIn("could not", msg.lower())
        self.assertNotIn("nothing was written", msg.lower())
        self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
