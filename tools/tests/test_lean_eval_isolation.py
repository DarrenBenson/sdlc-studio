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
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("eval_run_bg0839", REPO / "tools" / "eval_run.py")
eval_run = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(eval_run)

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


if __name__ == "__main__":
    unittest.main()
