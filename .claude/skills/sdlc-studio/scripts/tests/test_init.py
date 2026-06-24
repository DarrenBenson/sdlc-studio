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


if __name__ == "__main__":
    unittest.main()
