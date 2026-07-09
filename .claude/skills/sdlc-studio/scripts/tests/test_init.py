"""Unit tests for init.py - the deterministic greenfield initialiser (CR0079)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("init", SCR / "init.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["init"] = mod
    spec.loader.exec_module(mod)
    return mod


init = _load()


class InitTests(unittest.TestCase):
    def test_creates_tree_indexes_config_agentfiles(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = init.init(repo)
            # full directory tree
            for sub in init.DIRS:
                self.assertTrue((repo / "sdlc-studio" / sub).is_dir(), sub)
            # an index per numbered type, free of template placeholders
            for t in init.INDEX_TYPES:
                idx = repo / sdlc_md.ARTIFACT_TYPES[t][0] / "_index.md"
                self.assertTrue(idx.exists(), t)
                self.assertNotIn("{{", idx.read_text(encoding="utf-8"))
            # config + agent-instructions
            self.assertTrue((repo / "sdlc-studio" / ".config.yaml").exists())
            self.assertTrue((repo / "AGENTS.md").exists())
            self.assertTrue((repo / "CLAUDE.md").exists())
            # BG0036: a .gitignore so the runtime-state dir is never committed
            gi = repo / "sdlc-studio" / ".gitignore"
            self.assertTrue(gi.exists())
            self.assertIn(".local/", gi.read_text(encoding="utf-8"))
            self.assertFalse(r["dry_run"])

    def test_idempotent_second_run_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            again = init.init(repo)
            self.assertEqual(again["created"], [], "nothing new on a second run")
            self.assertTrue(again["skipped"])

    def test_scaffold_seeds_singletons_optionally(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo, scaffold=False)
            self.assertFalse((repo / "sdlc-studio" / "prd.md").exists())
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo, scaffold=True)
            for name in init.SINGLETONS:
                self.assertTrue((repo / "sdlc-studio" / f"{name}.md").exists(), name)

    def test_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = init.init(repo, scaffold=True, dry_run=True)
            self.assertTrue(r["created"])              # reports what it would do
            self.assertFalse((repo / "sdlc-studio").exists())  # but writes nothing

    def test_detect_stack(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "go.mod").write_text("module x\n", encoding="utf-8")
            self.assertEqual(init.detect_stack(repo), "go")
            r = init.init(repo, detect=True)
            self.assertEqual(r["language"], "go")
            self.assertIn("go", (repo / "sdlc-studio" / ".config.yaml").read_text())


class SchemaDefaultTests(unittest.TestCase):
    """US0105/CR0198: init scaffolds a NEW project at schema_version 3."""

    def test_init_writes_schema_version_3(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            cfg = (repo / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8")
            self.assertRegex(cfg, r"(?m)^\s*schema_version:\s*3\b")
            self.assertEqual(sdlc_md.schema_version(repo), 3)
            self.assertTrue(sdlc_md.is_schema_v3(repo))


class CodeDefaultUnchangedTests(unittest.TestCase):
    """US0105: the code default stays 2 - an unpinned/existing project is never auto-flipped."""

    def test_no_config_reads_as_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)  # no sdlc-studio/.config.yaml at all
            self.assertEqual(sdlc_md.schema_version(repo), 2)
            self.assertFalse(sdlc_md.is_schema_v3(repo))

    def test_config_without_schema_key_reads_as_v2(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            cfgdir = repo / "sdlc-studio"; cfgdir.mkdir(parents=True)
            (cfgdir / ".config.yaml").write_text("profile: full\n", encoding="utf-8")
            self.assertEqual(sdlc_md.schema_version(repo), 2)
            self.assertFalse(sdlc_md.is_schema_v3(repo))


class EraGateRegressionTests(unittest.TestCase):
    """US0105: a v2 project's v3-gated paths stay dormant after the init-default flip."""

    def test_v2_project_v3_paths_dormant(self) -> None:
        import spec_guard
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            cfgdir = repo / "sdlc-studio"; cfgdir.mkdir(parents=True)
            (cfgdir / ".config.yaml").write_text("schema_version: 2\n", encoding="utf-8")
            self.assertFalse(sdlc_md.is_schema_v3(repo))
            # spec_guard.spec_edits is a v3-only path: it must be a no-op on v2
            self.assertEqual(spec_guard.spec_edits(repo, ["prd.md"]), [])


if __name__ == "__main__":
    unittest.main()
