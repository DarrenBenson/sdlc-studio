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


class TailorTests(unittest.TestCase):
    """CR0326 / RFC0043 slice 3: init writes the default DoR/DoD documents and OFFERS a
    stack-derived tailoring pass - proposed criteria the operator accepts or edits;
    nothing is applied without acceptance (the persona team-gen pattern)."""

    def test_init_writes_the_default_documents(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            for name in ("definition-of-ready.md", "definition-of-done.md"):
                p = repo / "sdlc-studio" / name
                self.assertTrue(p.is_file(), f"{name} not written")
                text = p.read_text(encoding="utf-8")
                self.assertIn("## Story", text)
                self.assertEqual(sdlc_md.unknown_check_ids(text), [])

    def test_tailoring_offer_is_printed_never_auto_applied(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            r = init.init(repo, detect=True)
            self.assertTrue(r["tailoring"]["suggestions"])       # stack-derived offers
            self.assertFalse(r["tailoring"]["applied"])          # nothing applied
            done = (repo / "sdlc-studio" / "definition-of-done.md").read_text(encoding="utf-8")
            for s in r["tailoring"]["suggestions"]:
                self.assertNotIn(s["criterion"], done)           # offer, not an edit

    def test_offer_text_names_the_acceptance_path(self) -> None:
        import contextlib
        import io
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            mod = _load()
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = mod.main(["run", "--root", d, "--detect"])
            self.assertEqual(rc, 0)
            self.assertIn("tailoring offer", out.getvalue().lower())
            self.assertIn("--accept-tailoring", out.getvalue())
            self.assertIn("nothing is applied without acceptance", out.getvalue().lower())

    def test_accept_tailoring_appends_under_the_right_level(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            r = init.init(repo, detect=True, accept_tailoring=True)
            self.assertTrue(r["tailoring"]["applied"])
            done = (repo / "sdlc-studio" / "definition-of-done.md").read_text(encoding="utf-8")
            suggestion = next(s for s in r["tailoring"]["suggestions"] if s["kind"] == "done")
            self.assertIn(suggestion["criterion"], done)
            # appended INSIDE its level section, not at EOF after another level
            level_pos = done.index(f"## {suggestion['level']}")
            next_level = done.find("\n## ", level_pos + 1)
            criterion_pos = done.index(suggestion["criterion"])
            self.assertGreater(criterion_pos, level_pos)
            if next_level != -1:
                self.assertLess(criterion_pos, next_level)

    def test_repeat_accept_does_not_duplicate(self) -> None:
        # The offer text itself says "re-run with --accept-tailoring", so a second
        # accept is a natural flow: it must be idempotent, never duplicating criteria.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            init.init(repo, detect=True, accept_tailoring=True)
            r2 = init.init(repo, detect=True, accept_tailoring=True)
            done = (repo / "sdlc-studio" / "definition-of-done.md").read_text(encoding="utf-8")
            crit = next(s for s in r2["tailoring"]["suggestions"]
                        if s["kind"] == "done")["criterion"]
            self.assertEqual(done.count(crit), 1)          # appended once, ever
            self.assertFalse(r2["tailoring"]["applied"])   # nothing new = not "applied"

    def test_accept_into_document_missing_the_level_appends_a_section(self) -> None:
        # A user-edited document without the level must still receive the accepted
        # criterion (a new section) - an accepted edit is never silently dropped.
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "Dockerfile").write_text("FROM python:3\n", encoding="utf-8")
            init.init(repo)   # write defaults first
            doc = repo / "sdlc-studio" / "definition-of-done.md"
            doc.write_text("# Definition of Done\n\n## Story\n\n- [ ] human judged\n",
                           encoding="utf-8")   # user edit: Release level deleted
            r = init.init(repo, detect=True, accept_tailoring=True)
            text = doc.read_text(encoding="utf-8")
            crit = next(s for s in r["tailoring"]["suggestions"]
                        if s["level"] == "Release")["criterion"]
            self.assertIn("## Release", text)
            self.assertIn(crit, text)

    def test_no_stack_no_offer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            r = init.init(repo, detect=True)   # nothing to detect
            self.assertEqual(r["tailoring"]["suggestions"], [])


class TailorRegistryTests(unittest.TestCase):
    """CR0326 AC2: the tailored result passes slice 1's registry validation."""

    def test_tailored_documents_pass_registry_validation(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            (repo / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            (repo / "Dockerfile").write_text("FROM python:3\n", encoding="utf-8")
            init.init(repo, detect=True, accept_tailoring=True)
            for name in ("definition-of-ready.md", "definition-of-done.md"):
                text = (repo / "sdlc-studio" / name).read_text(encoding="utf-8")
                self.assertEqual(sdlc_md.unknown_check_ids(text), [], f"{name} fails registry")

    def test_every_suggestion_in_the_table_is_registry_clean(self) -> None:
        for suggestions in init.TAILOR_SUGGESTIONS.values():
            for s in suggestions:
                self.assertEqual(sdlc_md.unknown_check_ids(s["criterion"]), [])
                self.assertIn(s["kind"], ("ready", "done"))
                self.assertIn(s["level"], ("Story", "Sprint", "Release"))


if __name__ == "__main__":
    unittest.main()
