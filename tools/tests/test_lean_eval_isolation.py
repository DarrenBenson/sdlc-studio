"""BG0839: `eval_run.py setup` isolates the candidate skill from the operator's personal copy.

Under `claude -p` a personal `~/.claude/skills/sdlc-studio` is not outranked by a project copy of
the same name, so an eval worker loaded the personal skill and the run was mixed. `setup` now
builds `<dir>.claude-config/skills/sdlc-studio` from this working tree's skill - a sibling of the
fixture, so the worker's transcripts never dirty the fixture's `git status` - and prints the
worker command with `CLAUDE_CONFIG_DIR` set to it. It never copies a credential.
"""
from __future__ import annotations

# test-census-subject: tools/eval_run.py
import contextlib
import importlib.util
import io
import json
import os
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("eval_run_bg0839", REPO / "tools" / "eval_run.py")
eval_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eval_run)
sys.path.insert(0, str(REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"))
from lib import run_state  # noqa: E402

_SCENARIO = {"id": "99-isolation", "setup": "prose", "prompt": "Run the thing; say 'done'.",
             "fixture": {"files": {"README.md": "# fixture\n", "sdlc-studio/.config.yaml": "a: 1\n"}},
             "expected_behaviours": [{"id": "EB1", "severity": "blocking", "description": "d"}],
             "forbidden_behaviours": []}


class EvalIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        scenarios = self.root / "scenarios"
        scenarios.mkdir()
        (scenarios / "99-isolation.json").write_text(json.dumps(_SCENARIO), encoding="utf-8")
        old = eval_run.SCENARIOS
        eval_run.SCENARIOS = scenarios
        self.addCleanup(setattr, eval_run, "SCENARIOS", old)

    def _setup(self, dest: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = eval_run.main(["setup", "--scenario", "99-isolation", "--dir", dest])
        return rc, out.getvalue(), err.getvalue()

    def _fake_skill(self) -> Path:
        """A small candidate skill holding the runtime folders the copy must leave behind."""
        src = self.root / "candidate" / "sdlc-studio"
        for sub in (".local", "__pycache__", "scripts"):
            (src / sub).mkdir(parents=True)
        (src / "SKILL.md").write_text("---\nname: sdlc-studio\n---\n", encoding="utf-8")
        (src / ".local" / "state.json").write_text("{}", encoding="utf-8")
        (src / "__pycache__" / "x.pyc").write_bytes(b"\0")
        (src / "scripts" / "tool.py").write_text("", encoding="utf-8")
        patch = mock.patch.object(eval_run, "SKILL_SRC", src)
        patch.start()
        self.addCleanup(patch.stop)
        return src

    def _fixture_files(self, scratch: Path) -> list[str]:
        return sorted(p.relative_to(scratch).as_posix() for p in scratch.rglob("*")
                      if p.is_file())

    def test_setup_isolates_the_candidate_skill(self) -> None:
        """AC1. MUTANT: HEAD, which builds no config directory and prints no command. MUTANT:
        build the config inside the fixture - its files then show in the fixture's git status.
        MUTANT: copy the operator's credentials in - setup must never write one."""
        scratch = self.root / "fx"
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            rc = eval_run.main(["setup", "--scenario", "99-isolation", "--dir", str(scratch)])
        self.assertEqual(0, rc)
        config = Path(f"{scratch}.claude-config")
        self.assertTrue((config / "skills" / "sdlc-studio" / "SKILL.md").is_file())
        written = sorted(p.relative_to(scratch).as_posix() for p in scratch.rglob("*")
                         if p.is_file())
        self.assertEqual(sorted(_SCENARIO["fixture"]["files"]), written)
        creds = [p for p in config.rglob("*") if "credential" in p.name.lower()]
        self.assertEqual([], creds, "setup wrote a credential file")
        lines = out.getvalue().splitlines()
        self.assertTrue(any(ln.startswith(f"CLAUDE_CONFIG_DIR={config} ") for ln in lines),
                        out.getvalue())

    def test_the_meter_is_pointed_at_the_worker_transcripts(self) -> None:
        """Round-2 repro. The worker writes `<config>/projects/<slug>/*.jsonl`, the slug being
        the fixture's path with every character outside [A-Za-z0-9] turned into `-` (spelled out
        here, not read from the code under test). MUTANT: print `<config>/projects` - the meter
        globs `*.jsonl` directly in it and finds nothing."""
        self._fake_skill()
        scratch = self.root / "fx_1.v2"
        rc, out, err = self._setup(str(scratch))
        self.assertEqual(0, rc, err)
        command = next(ln for ln in out.splitlines() if ln.startswith("CLAUDE_CONFIG_DIR="))
        env = dict(tok.split("=", 1) for tok in shlex.split(command) if "=" in tok
                   and tok.split("=", 1)[0].isupper())
        slug = str(scratch.resolve())
        for ch in "/._":
            slug = slug.replace(ch, "-")
        worker = Path(f"{scratch.resolve()}.claude-config") / "projects" / slug
        worker.mkdir(parents=True)
        (worker / "s.jsonl").write_text(
            json.dumps({"message": {"usage": {"input_tokens": 9}}}) + "\n", encoding="utf-8")
        with mock.patch.dict(os.environ,
                             {"SDLC_STUDIO_TRANSCRIPTS": env["SDLC_STUDIO_TRANSCRIPTS"]}):
            got = run_state.session_tokens(scratch)
        self.assertEqual(9, got.get("tokens"), got)

    def test_a_dir_whose_parent_is_not_made_yet_is_built(self) -> None:
        """Round-2 repro: scenario 09's `--dir /tmp/evals-v6/09-lean-sprint` on a host with no
        `/tmp/evals-v6`. MUTANT: check the config's own parent for write access - a path that
        does not exist is not writable, so the documented command is refused."""
        self._fake_skill()
        scratch = self.root / "not-yet" / "09-lean-sprint"
        rc, out, err = self._setup(str(scratch))
        self.assertEqual(0, rc, out + err)
        self.assertTrue((self.root / "not-yet" / "09-lean-sprint.claude-config" / "skills" /
                         "sdlc-studio" / "SKILL.md").is_file())
        self.assertEqual(sorted(_SCENARIO["fixture"]["files"]), self._fixture_files(scratch))

    def test_a_relative_dot_dir_puts_the_config_beside_the_fixture(self) -> None:
        """Round-1 repro. MUTANT: build the config from the unresolved `--dir` - `.` names
        `..claude-config`, INSIDE the fixture, which a scenario's `git add -A` stages."""
        self._fake_skill()
        scratch = self.root / "fx"
        scratch.mkdir()
        cwd = os.getcwd()
        os.chdir(scratch)
        self.addCleanup(os.chdir, cwd)
        rc, out, err = self._setup(".")
        self.assertEqual(0, rc, err)
        self.assertTrue((self.root / "fx.claude-config" / "skills" / "sdlc-studio" /
                         "SKILL.md").is_file(), out)
        self.assertEqual(sorted(_SCENARIO["fixture"]["files"]), self._fixture_files(scratch))
        self.assertEqual([], [p.name for p in scratch.iterdir() if "claude-config" in p.name])

    def test_an_unwritable_parent_is_refused_before_the_fixture(self) -> None:
        """A top-level `--dir /tmp/` names `/tmp.claude-config`, under an unwritable `/`.
        MUTANT: check nothing first - the fixture is written, then a PermissionError traceback."""
        if os.geteuid() == 0:                       # pragma: no cover - root writes anywhere
            self.skipTest("root can write any directory")
        self._fake_skill()
        locked = self.root / "locked"
        locked.mkdir()
        locked.chmod(0o555)
        self.addCleanup(locked.chmod, 0o755)
        rc, out, err = self._setup(str(locked / "fx"))
        self.assertEqual(2, rc, out + err)
        self.assertEqual(1, len(err.strip().splitlines()), err)
        self.assertIn(str(locked / "fx.claude-config"), err)
        self.assertFalse((locked / "fx").exists(), "the fixture was written before the refusal")

    def test_a_symlinked_skill_folder_is_never_rebuilt_through(self) -> None:
        """MUTANT: rmtree the existing skill folder whatever it is - a link to a skill the
        operator keeps is deleted through."""
        self._fake_skill()
        kept = self.root / "home" / ".claude" / "skills" / "sdlc-studio"
        kept.mkdir(parents=True)
        (kept / "SKILL.md").write_text("mine\n", encoding="utf-8")
        skills = self.root / "fx.claude-config" / "skills"
        skills.mkdir(parents=True)
        (skills / "sdlc-studio").symlink_to(kept, target_is_directory=True)
        rc, out, err = self._setup(str(self.root / "fx"))
        self.assertEqual(2, rc, out + err)
        self.assertIn("symlink", err)
        self.assertEqual("mine\n", (kept / "SKILL.md").read_text(encoding="utf-8"))
        self.assertFalse((self.root / "fx").exists())

    def test_a_symlinked_skills_folder_is_never_rebuilt_through(self) -> None:
        """The refusal covers every level, not only the leaf. MUTANT: check the skill folder
        alone - a link at `skills/` passes and the rebuild deletes the kept copy through it."""
        self._fake_skill()
        kept = self.root / "home" / ".claude" / "skills"
        (kept / "sdlc-studio").mkdir(parents=True)
        (kept / "sdlc-studio" / "SKILL.md").write_text("mine\n", encoding="utf-8")
        config = self.root / "fx.claude-config"
        config.mkdir()
        (config / "skills").symlink_to(kept, target_is_directory=True)
        rc, out, err = self._setup(str(self.root / "fx"))
        self.assertEqual(2, rc, out + err)
        self.assertIn(f"{config / 'skills'} is a symlink", err)
        self.assertEqual("mine\n", (kept / "sdlc-studio" / "SKILL.md").read_text(encoding="utf-8"))

    def test_the_rebuild_is_fresh_filtered_and_credential_free(self) -> None:
        """MUTANTS: copy over the old folder (a stale file survives); drop the ignore list
        (`.local` and `__pycache__` are copied); copy a credential from HOME into the config."""
        self._fake_skill()
        home = self.root / "home"
        (home / ".claude").mkdir(parents=True)
        (home / ".claude" / ".credentials.json").write_text('{"token": "x"}', encoding="utf-8")
        scratch = str(self.root / "fx")
        skill = self.root / "fx.claude-config" / "skills" / "sdlc-studio"
        with mock.patch.dict(os.environ, {"HOME": str(home)}):
            self.assertEqual(0, self._setup(scratch)[0])
            (skill / "stale.md").write_text("old\n", encoding="utf-8")
            self.assertEqual(0, self._setup(scratch)[0])
        self.assertFalse((skill / "stale.md").exists(), "the rebuild kept a stale file")
        self.assertTrue((skill / "scripts" / "tool.py").is_file())
        self.assertFalse((skill / ".local").exists())
        self.assertFalse((skill / "__pycache__").exists())
        config = self.root / "fx.claude-config"
        self.assertEqual([], [p for p in config.rglob("*") if "credential" in p.name.lower()])


if __name__ == "__main__":
    unittest.main()
