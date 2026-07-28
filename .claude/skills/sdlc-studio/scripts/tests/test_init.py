"""Unit tests for init.py - the deterministic greenfield initialiser (CR0079)."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402
import artifact  # noqa: E402
import file_finding  # noqa: E402


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


class PlaceholderFillTests(unittest.TestCase):
    """BG0255: the filler matched `{{project_name}}` case-SENSITIVELY while the shipped
    agent-instructions template heads with `{{PROJECT_NAME}}`, so every seeded AGENTS.md
    shipped a literal unfilled placeholder and nothing noticed. The fix is in the FILLER,
    and the postcondition is the guard: a placeholder the filler claims to know may never
    survive a seed."""

    TEMPLATE = init.SKILL / "templates" / "agent-instructions.md"

    def test_shipped_template_gets_its_project_name_filled(self) -> None:
        text = self.TEMPLATE.read_text(encoding="utf-8")
        out = init._fill_known(text, {"project_name": "ACME", "date": "2026-01-01",
                                      "last_updated": "2026-01-01"})
        self.assertIn("ACME", out, "the project name never reached the template")
        self.assertNotRegex(out, r"(?i)\{\{\s*project_name\s*\}\}")

    def test_seeded_agent_files_carry_no_known_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            for dst in ("AGENTS.md", "CLAUDE.md"):
                text = (repo / dst).read_text(encoding="utf-8")
                self.assertEqual(
                    init.unfilled_known(text, {"project_name": repo.resolve().name}), [],
                    f"{dst} kept a placeholder the filler claims to know")
            self.assertIn(repo.resolve().name, (repo / "AGENTS.md").read_text(encoding="utf-8"))

    def test_unfilled_known_reports_only_the_survivors_it_claims(self) -> None:
        fields = {"project_name": "ACME", "date": "2026-01-01"}
        self.assertEqual(init.unfilled_known("# {{PROJECT_NAME}}\n", fields), ["project_name"])
        self.assertEqual(init.unfilled_known("# ACME on 2026-01-01\n", fields), [])
        # a key the caller never supplied is not the filler's claim, so it is not a survivor
        self.assertEqual(init.unfilled_known("{{language}}\n", fields), [])

    def test_fill_known_refuses_to_return_a_surviving_known_placeholder(self) -> None:
        # The postcondition, exercised: a value that re-introduces the placeholder must
        # raise rather than be written out. This is the class the bug was - a substitution
        # doing nothing, silently.
        with self.assertRaises(RuntimeError) as ctx:
            init._fill_known("# {{PROJECT_NAME}}\n", {"project_name": "{{project_name}}"})
        self.assertIn("project_name", str(ctx.exception))


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


class GuidedInitTests(unittest.TestCase):
    """RFC0055 / US0437: the guided-onboarding orchestrator skeleton - resumable state,
    greenfield/brownfield classification, and the confirm/skip/reset stage runner. The stage
    ACTIONS are later stories; this pins the machinery they plug into."""

    def test_onboarding_state_resumes_from_first_incomplete_stage(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            state = init.start_onboarding(root)
            self.assertEqual(init.first_incomplete(state), init.ONBOARDING_STAGES[0])
            # complete the first, skip the second -> resume points at the third (first pending)
            init.set_stage(root, init.ONBOARDING_STAGES[0], "done")
            init.set_stage(root, init.ONBOARDING_STAGES[1], "skipped")
            resumed = init.read_onboarding(root)
            self.assertEqual(init.first_incomplete(resumed), init.ONBOARDING_STAGES[2])
            # persisted to the runtime-state dir, never restarting from the top
            self.assertTrue((root / "sdlc-studio" / ".local" / "onboarding.json").is_file())
            self.assertEqual(init.start_onboarding(root)["stages"][0]["status"], "done")

    def test_classifies_greenfield_and_brownfield(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(init.classify_path(Path(d)), "greenfield")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
            self.assertEqual(init.classify_path(root), "brownfield")
        # BG0312: US0437 AC2's Given is a repo that already CONTAINS SOURCE. This verifier
        # exercised a manifest only, so it could not fail on the AC's own Given - the case that
        # was broken. Source with no manifest belongs in the criterion's own verifier, not only
        # in the sibling test below.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "app.rb").write_text("class App; end\n", encoding="utf-8")
            self.assertIsNone(init.detect_stack(root))
            self.assertEqual(init.classify_path(root), "brownfield")

    def test_source_without_a_recognised_manifest_classifies_brownfield(self) -> None:
        """BG0312: US0437 AC2 promises brownfield for a repo 'that already contains source', but
        the classifier keyed entirely off six manifest markers plus *.csproj - so a C/C++, Ruby or
        PHP tree, or a Python project with only a setup.py, read as an empty repo and US0439's PRD
        stage sent it down the greenfield INTERVIEW. That is the exact wrong fork the guided flow
        exists to avoid. The AC's own Given is source on disk, not a manifest this skill happens
        to recognise, so the classifier must census the source too."""
        cases = {
            "c": [("src/main.c", "int main(void) { return 0; }\n"),
                  ("src/util.h", "#pragma once\n")],
            "ruby": [("app/models/user.rb", "class User; end\n")],
            "php": [("public/index.php", "<?php echo 'hi';\n")],
            "setup-py-only-python": [("setup.py", "from setuptools import setup\nsetup()\n"),
                                     ("pkg/core.py", "def go():\n    return 1\n")],
        }
        for name, files in cases.items():
            with self.subTest(stack=name), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                for rel, body in files:
                    p = root / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_text(body, encoding="utf-8")
                self.assertIsNone(init.detect_stack(root))      # no manifest marker: the premise
                self.assertEqual(init.classify_path(root), "brownfield")

    def test_a_manifest_less_source_repo_is_sent_down_the_brownfield_prd_fork(self) -> None:
        # The consequence the bug is about: the classification is only useful if the PRD stage
        # forks on it. A C repo must be told to GENERATE its PRD from the code, never interviewed.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "src").mkdir()
            (root / "src" / "main.c").write_text("int main(void) { return 0; }\n",
                                                 encoding="utf-8")
            self.assertEqual(init.start_onboarding(root)["path"], "brownfield")
            r = init.stage_prd(root)
            self.assertEqual(r["path"], "brownfield")
            self.assertIn("prd generate", r["directive"])
            self.assertNotIn("prd create", r["directive"])

    def test_docs_and_derived_directories_do_not_make_a_repo_brownfield(self) -> None:
        """The census must not fire on non-source, or every greenfield project reads brownfield
        the moment `init` writes its own markdown. Vendored/derived trees are pruned for the same
        reason: a checked-in dependency is not this project's source."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "README.md").write_text("# hi\n", encoding="utf-8")
            (root / "sdlc-studio" / "stories").mkdir(parents=True)
            (root / "sdlc-studio" / "stories" / "_index.md").write_text("# Stories\n",
                                                                        encoding="utf-8")
            (root / "notes.txt").write_text("thoughts\n", encoding="utf-8")
            self.assertEqual(init.classify_path(root), "greenfield")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for pruned in ("node_modules/left-pad", ".git/hooks", ".venv/lib", "dist/bundle"):
                p = root / pruned
                p.mkdir(parents=True)
                (p / "index.js").write_text("module.exports = 1;\n", encoding="utf-8")
            self.assertEqual(init.classify_path(root), "greenfield")

    def test_stage_runner_confirm_skip_and_reset(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root)
            init.set_stage(root, init.ONBOARDING_STAGES[0], "done")   # confirm advances
            self.assertEqual(init.stage_status(init.read_onboarding(root),
                                                init.ONBOARDING_STAGES[0]), "done")
            init.set_stage(root, init.ONBOARDING_STAGES[1], "skipped")  # skip recorded, not dropped
            self.assertEqual(init.stage_status(init.read_onboarding(root),
                                                init.ONBOARDING_STAGES[1]), "skipped")
            init.reset_onboarding(root)                               # reset -> all pending
            self.assertTrue(all(s["status"] == "pending"
                                for s in init.read_onboarding(root)["stages"]))

    def test_agents_stage_drafts_the_instructions(self) -> None:
        # US0438 AC1 promises `AGENTS.md` AND the `CLAUDE.md` import. BG0334: this verifier
        # asserted only AGENTS.md, so deleting the CLAUDE.md starter from AGENT_FILES - or
        # shipping an installed copy without that template - kept it green while Claude Code,
        # which reads CLAUDE.md and not AGENTS.md, inherited nothing.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            r = init.stage_agents(root)
            self.assertIn("AGENTS.md", r["created"])
            self.assertIn("CLAUDE.md", r["created"])
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertTrue((root / "CLAUDE.md").is_file())
            # the CLAUDE.md file is the IMPORT the AC names, not merely a file of that name
            claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            # the guidance comment is stripped and the import is the first thing Claude Code reads
            self.assertTrue(claude.lstrip().startswith("@AGENTS.md"), claude[:120])
            # idempotent: a second run leaves the (possibly edited) files untouched
            r2 = init.stage_agents(root)
            self.assertIn("AGENTS.md", r2["skipped"])
            self.assertIn("CLAUDE.md", r2["skipped"])
            self.assertEqual(r2["created"], [])

    def test_a_missing_starter_template_is_refused_not_skipped_in_silence(self) -> None:
        """BG0334: `stage_agents` skipped a missing template with a bare `continue`, reporting it
        in neither `created` nor `skipped`. The first stage of onboarding then produced nothing,
        said nothing, and the operator confirmed it - the silent-success class. A starter missing
        from the installed skill is a broken install, so the stage refuses rather than drafting
        half of what its AC promises."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as fake:
            root, skill = Path(d), Path(fake)
            (skill / "templates").mkdir()
            # only the AGENTS.md starter is present; the CLAUDE.md import starter is gone
            (skill / "templates" / "agent-instructions.md").write_text(
                (init.SKILL / "templates" / "agent-instructions.md").read_text(encoding="utf-8"),
                encoding="utf-8")
            real = init.SKILL
            init.SKILL = skill
            try:
                with self.assertRaises(RuntimeError) as ctx:
                    init.stage_agents(root)
                self.assertIn("agent-instructions.CLAUDE.md", str(ctx.exception))
                # nothing partial is written: no half-drafted stage to confirm
                self.assertFalse((root / "AGENTS.md").exists())
                # and the runner does not swallow it - the stage stays pending, not advanced
                init.start_onboarding(root)
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(RuntimeError):
                    init.main(["guided", "--root", str(root)])
                self.assertEqual(init.first_incomplete(init.read_onboarding(root)), "agents")
            finally:
                init.SKILL = real

    def test_guided_confirm_and_skip_advance_the_runner(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root)
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--confirm", "--root", str(root)])
            self.assertEqual(init.stage_status(init.read_onboarding(root),
                                                init.ONBOARDING_STAGES[0]), "done")
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--skip", "--root", str(root)])
            self.assertEqual(init.stage_status(init.read_onboarding(root),
                                                init.ONBOARDING_STAGES[1]), "skipped")

    def test_prd_stage_forks_greenfield_and_brownfield(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="greenfield")
            r = init.stage_prd(root)
            self.assertEqual(r["path"], "greenfield")
            self.assertIn("prd create", r["directive"])
            self.assertIn("sdlc-studio/prd.md", r["created"])
            self.assertTrue((root / "sdlc-studio" / "prd.md").is_file())
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="brownfield")
            r = init.stage_prd(root)
            self.assertEqual(r["path"], "brownfield")
            self.assertIn("prd generate", r["directive"])

    def test_prd_stage_is_reached_and_advances(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="greenfield")
            init.set_stage(root, "agents", "done")
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--root", str(root)])
            self.assertEqual(init.first_incomplete(init.read_onboarding(root)), "prd")
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--confirm", "--root", str(root)])
            self.assertEqual(init.first_incomplete(init.read_onboarding(root)), "trd")

    def test_trd_and_tsd_stages_seed_and_direct(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="brownfield")
            rt = init.stage_trd(root)
            self.assertIn("sdlc-studio/trd.md", rt["created"])
            self.assertIn("PRD", rt["directive"])
            self.assertTrue((root / "sdlc-studio" / "trd.md").is_file())
            rs = init.stage_tsd(root)
            self.assertIn("sdlc-studio/tsd.md", rs["created"])
            self.assertIn("stack", rs["directive"])   # brownfield names the stack

    def test_tsd_directive_omits_stack_on_greenfield(self) -> None:
        # US0440 AC1 scopes the "detected stack" clause to brownfield: a greenfield project has no
        # stack to detect, so its directive must not claim one.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="greenfield")
            self.assertNotIn("stack", init.stage_tsd(root)["directive"])

    def test_corrupt_or_shape_invalid_state_reads_as_absent(self) -> None:
        # A hand-mangled `.local` checkpoint must never crash the read-only orientation path; it is
        # treated as absent, so `cmd_guided` self-heals and `status`/`hint` fall through.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = init.onboarding_path(root)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("{not valid json", encoding="utf-8")
            self.assertIsNone(init.read_onboarding(root))
            p.write_text('{"path": "greenfield"}', encoding="utf-8")  # no "stages" key
            self.assertIsNone(init.read_onboarding(root))
            # cmd_guided self-heals a corrupt file into a fresh, valid checkpoint.
            p.write_text("{broken", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--root", str(root)])
            self.assertEqual(init.first_incomplete(init.read_onboarding(root)), "agents")

    def test_trd_tsd_advance_to_personas(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="greenfield")
            init.set_stage(root, "agents", "done")
            init.set_stage(root, "prd", "done")
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--confirm", "--root", str(root)])   # trd done
                init.main(["guided", "--confirm", "--root", str(root)])   # tsd done
            self.assertEqual(init.first_incomplete(init.read_onboarding(root)), "personas")

    def test_personas_stage_seeds_and_directs(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root)
            r = init.stage_personas(root)
            self.assertIn("sdlc-studio/personas.md", r["created"])
            self.assertIn("persona generate --team", r["directive"])
            self.assertTrue((root / "sdlc-studio" / "personas.md").is_file())

    def test_personas_stage_advances_to_decompose(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="greenfield")
            for st in ("agents", "prd", "trd", "tsd"):
                init.set_stage(root, st, "done")
            with contextlib.redirect_stdout(io.StringIO()):
                init.main(["guided", "--confirm", "--root", str(root)])   # personas done
            self.assertEqual(init.first_incomplete(init.read_onboarding(root)), "decompose")

    def test_decompose_and_plan_stages_direct(self) -> None:
        # US0442 AC1 names three commands. BG0334: this verifier asserted the bare substrings
        # 'epic' and 'sprint plan' and never mentioned the story command at all - and 'epic' is
        # satisfied by the word 'epics' in the surrounding prose, so stripping BOTH backticked
        # commands out of the directive left it green. Assert the commands as the directive
        # marks them up, so prose alone can never satisfy the AC.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root)
            decompose = init.stage_decompose(root)["directive"]
            self.assertIn("`epic`", decompose)
            self.assertIn("`story`", decompose)
            self.assertIn("`sprint plan`", init.stage_plan(root)["directive"])

    def test_confirming_all_stages_completes_onboarding(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root, path="greenfield")
            for _ in init.ONBOARDING_STAGES:
                with contextlib.redirect_stdout(io.StringIO()):
                    init.main(["guided", "--confirm", "--root", str(root)])
            self.assertIsNone(init.first_incomplete(init.read_onboarding(root)))
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                init.main(["guided", "--root", str(root)])
            self.assertIn("complete", buf.getvalue())

    def test_an_unknown_stage_or_status_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            init.start_onboarding(root)
            with self.assertRaises(ValueError):
                init.set_stage(root, "not-a-stage", "done")
            with self.assertRaises(ValueError):
                init.set_stage(root, init.ONBOARDING_STAGES[0], "finished")


class InstalledSkillIsNotSourceTests(unittest.TestCase):
    """`install.sh --local` writes the skill into .claude/, .agents/ and .github/. A repo carrying
    that payload and nothing else is GREENFIELD - classifying it brownfield sends guided onboarding
    to reverse-engineer a PRD from the skill's own scripts, which is the wrong-fork harm the census
    exists to prevent, inverted."""

    def _tree(self, root, extra=None):
        (root / "README.md").write_text("x", encoding="utf-8")
        (root / "sdlc-studio").mkdir(exist_ok=True)
        (root / "sdlc-studio" / "prd.md").write_text("x", encoding="utf-8")
        for rel in (extra or []):
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("x = 1\n", encoding="utf-8")

    def test_an_installed_skill_payload_does_not_make_a_repo_brownfield(self):
        for skill_dir in (".claude/skills/s/scripts/a.py", ".agents/skills/s/scripts/a.py",
                          ".github/skills/s/scripts/a.py", ".gemini/skills/s/a.py"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                self._tree(root, [skill_dir])
                self.assertEqual(init.classify_path(root), "greenfield",
                                 f"{skill_dir} is installed payload, not this project's source")

    def test_real_source_beside_an_installed_skill_is_still_brownfield(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self._tree(root, [".claude/skills/s/scripts/a.py", "app.py"])
            self.assertEqual(init.classify_path(root), "brownfield",
                             "pruning the payload must not blind the census to real source")


class IssueTypeTests(unittest.TestCase):
    """US0529/US0530: the tree init creates is DERIVED from the shipped type table.

    A new project had no `issues/` directory and no issues index, so the issue type - a shipped
    artefact type with its own status vocabulary, index template and creator branch - could not be
    used until somebody made the directory by hand. The cause was a hand-written list of
    directories that silently exempted the type nobody remembered to add to it."""

    def test_init_creates_a_usable_issues_directory(self) -> None:
        """US0529 AC1: the issues directory and index exist, and an issue files straight in."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            issues = repo / sdlc_md.ARTIFACT_TYPES["issue"][0]
            self.assertTrue(issues.is_dir(), "init created no issues directory")
            idx = issues / "_index.md"
            self.assertTrue(idx.exists(), "init created no issues index")
            self.assertNotIn("{{", idx.read_text(encoding="utf-8"))
            # Usable immediately: file an issue with NO directory made by hand.
            r = artifact.new(repo, "issue", "Login times out on a slow link",
                             {"summary": "reported by a user", "size": "S"})
            self.assertTrue(Path(r["path"]).exists(), "the filed issue was not written")
            self.assertEqual(Path(r["path"]).parent, issues,
                             "the issue did not land in the directory init created")
            self.assertTrue(r["indexed"], "the filed issue was not indexed")
            self.assertIn(r["id"], idx.read_text(encoding="utf-8"))

    def test_every_shipped_type_gets_a_directory(self) -> None:
        """US0530 AC1: measured against the shipped table, not against init's own list."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            missing = []
            for t, (rel, _prefix) in sdlc_md.ARTIFACT_TYPES.items():
                if not (repo / rel).is_dir():
                    missing.append(f"{t}: no {rel}/")
                elif not (repo / rel / "_index.md").exists():
                    missing.append(f"{t}: no {rel}/_index.md")
            self.assertEqual(missing, [], "shipped types with no home on a new project")
            # ... and the list init exposes is the table's, not a subset that drifted from it.
            self.assertEqual(set(init.index_types()), set(sdlc_md.ARTIFACT_TYPES))

    def test_a_new_type_is_covered_without_editing_init(self) -> None:
        """US0530 AC2: append a type to the shipped table; init covers it with no edit to init.

        The per-type index template is a separate shipped asset, so its lookup is stubbed here -
        what is under test is whether init DERIVES its tree from the table or restates it."""
        real_template = file_finding.index_template_path

        def _stub(type_: str) -> Path:
            return real_template("bug" if type_ == "widget" else type_)

        with tempfile.TemporaryDirectory() as d, \
                mock.patch.dict(sdlc_md.ARTIFACT_TYPES,
                                {"widget": ("sdlc-studio/widgets", "WG")}), \
                mock.patch.object(file_finding, "index_template_path", _stub):
            repo = Path(d)
            init.init(repo)
            self.assertTrue((repo / "sdlc-studio" / "widgets").is_dir(),
                            "a type added to the shipped table got no directory")
            self.assertTrue((repo / "sdlc-studio" / "widgets" / "_index.md").exists(),
                            "a type added to the shipped table got no index")

    def test_the_workspaces_are_still_created(self) -> None:
        """Deriving the artefact dirs must not drop the cross-cutting workspaces beside them."""
        with tempfile.TemporaryDirectory() as d:
            repo = Path(d)
            init.init(repo)
            for w in ("retros", "handoffs", "decisions", "reviews", ".local"):
                self.assertTrue((repo / "sdlc-studio" / w).is_dir(), w)


if __name__ == "__main__":
    unittest.main()
