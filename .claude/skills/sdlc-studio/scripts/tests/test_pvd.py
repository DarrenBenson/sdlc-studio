"""Unit tests for pvd.py - PVD projection + drift (CR0048)."""
from __future__ import annotations

import importlib.util
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "pvd.py"


def _load():
    spec = importlib.util.spec_from_file_location("pvd", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pvd"] = mod
    spec.loader.exec_module(mod)
    return mod


pvd = _load()
MASTER = "> **Version:** 1.0.0\n\n# Product Vision\n\nbody\n"


def _master(d: Path, text: str = MASTER) -> Path:
    m = d / "master.md"
    m.write_text(text, encoding="utf-8")
    return m


class SyncTests(unittest.TestCase):
    def test_sync_copy_is_readonly_and_matches(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            r = pvd.sync(m, d / "repo")
            dest = Path(r["target"])
            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_text(encoding="utf-8"), MASTER)
            self.assertFalse(os.access(dest, os.W_OK))  # read-only projection

    def test_sync_is_idempotent_over_readonly(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            pvd.sync(m, d / "repo")
            r2 = pvd.sync(m, d / "repo")  # must replace the read-only copy, not crash
            self.assertEqual(Path(r2["target"]).read_text(encoding="utf-8"), MASTER)


class DriftTests(unittest.TestCase):
    def test_in_sync(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            dest = Path(pvd.sync(m, d / "repo")["target"])
            self.assertEqual(pvd.drift(m, dest)["status"], "in-sync")

    def test_stale_same_version_diff_content(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            dest = Path(pvd.sync(m, d / "repo")["target"])
            dest.chmod(stat.S_IWUSR | stat.S_IRUSR)
            dest.write_text(MASTER + "locally edited\n", encoding="utf-8")  # same version
            self.assertEqual(pvd.drift(m, dest)["status"], "stale")

    def test_behind_when_master_version_advances(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            dest = Path(pvd.sync(m, d / "repo")["target"])
            m.write_text("> **Version:** 2.0.0\n\n# Product Vision\n\nnew\n", encoding="utf-8")
            self.assertEqual(pvd.drift(m, dest)["status"], "behind")

    def test_missing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            self.assertEqual(pvd.drift(m, d / "nope.md")["status"], "missing")

    def test_unreadable_master_is_not_vacuous_insync(self) -> None:
        # HIGH regression: a missing/unreadable master must NOT report in-sync.
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            dest = d / "copy.md"
            dest.write_text(MASTER, encoding="utf-8")
            r = pvd.drift(d / "no-master.md", dest)
            self.assertNotEqual(r["status"], "in-sync")
            self.assertEqual(r["status"], "error")


class SymlinkModeTests(unittest.TestCase):
    def test_symlink_mode_links_and_resyncs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            dest = Path(pvd.sync(m, d / "repo", mode="symlink")["target"])
            self.assertTrue(dest.is_symlink())
            self.assertEqual(dest.read_text(encoding="utf-8"), MASTER)
            self.assertEqual(pvd.drift(m, dest)["status"], "in-sync")
            # switch back to copy over the existing symlink (idempotent replace)
            dest2 = Path(pvd.sync(m, d / "repo", mode="copy")["target"])
            self.assertFalse(dest2.is_symlink())


class MissingMasterSyncTests(unittest.TestCase):
    """BG0322: sync must never report a projection it did not make. symlink_to succeeds
    against any path, so a mistyped --master used to leave a dangling link behind an
    {'action': 'synced'} + exit 0."""

    def test_symlink_mode_refuses_a_missing_master(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            r = pvd.sync(d / "NO_SUCH_FILE.md", d / "repo", mode="symlink")
            self.assertEqual(r["action"], "error")
            dest = d / "repo" / pvd.PROJECTED
            self.assertFalse(dest.is_symlink())   # no dangling link left behind
            self.assertFalse(dest.exists())

    def test_copy_mode_refuses_a_missing_master(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            r = pvd.sync(d / "NO_SUCH_FILE.md", d / "repo", mode="copy")
            self.assertEqual(r["action"], "error")

    def test_unreadable_master_refused_like_drift_refuses_it(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            m.chmod(0)
            try:
                r = pvd.sync(m, d / "repo", mode="symlink")
            finally:
                m.chmod(stat.S_IRUSR | stat.S_IWUSR)
            self.assertEqual(r["action"], "error")

    def test_dry_run_does_not_promise_a_sync_it_cannot_make(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            r = pvd.sync(d / "NO_SUCH_FILE.md", d / "repo", mode="symlink", dry_run=True)
            self.assertEqual(r["action"], "error")

    def test_cli_sync_exits_nonzero_on_a_missing_master(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            rc = pvd.main(["sync", "--master", str(d / "NO_SUCH_FILE.md"),
                           "--target", str(d / "repo"), "--mode", "symlink"])
            self.assertEqual(rc, 1)

    def test_existing_projection_survives_a_refused_sync(self) -> None:
        # A good copy must not be unlinked to make way for a sync that then refuses.
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            m = _master(d)
            dest = Path(pvd.sync(m, d / "repo")["target"])
            pvd.sync(d / "NO_SUCH_FILE.md", d / "repo", mode="symlink")
            self.assertTrue(dest.exists())
            self.assertEqual(dest.read_text(encoding="utf-8"), MASTER)


class ManifestCommentTests(unittest.TestCase):
    def test_inline_comments_stripped_from_values(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "manifest.yaml"
            p.write_text(
                "master_pvd: a/b.md\nrepos:\n"
                "  - id: repo-a    # short id\n    path: ../repo-a   # sibling path\n",
                encoding="utf-8")
            m = pvd.read_manifest(p)
            self.assertEqual(m["repos"][0]["id"], "repo-a")
            self.assertEqual(m["repos"][0]["path"], "../repo-a")  # no '# ...' cruft


class ManifestTests(unittest.TestCase):
    def test_read_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "manifest.yaml"
            p.write_text(
                "product: Demo\nmaster_pvd: sdlc-studio/product/pvd.md\nrepos:\n"
                "  - id: repo-a\n    path: ../repo-a\n    url: https://x/repo-a\n"
                "  - id: repo-b\n    path: ../repo-b\n    url: https://x/repo-b\n",
                encoding="utf-8")
            m = pvd.read_manifest(p)
            self.assertEqual(m["master_pvd"], "sdlc-studio/product/pvd.md")
            self.assertEqual([r["id"] for r in m["repos"]], ["repo-a", "repo-b"])
            self.assertEqual(m["repos"][0]["path"], "../repo-a")


if __name__ == "__main__":
    unittest.main()
