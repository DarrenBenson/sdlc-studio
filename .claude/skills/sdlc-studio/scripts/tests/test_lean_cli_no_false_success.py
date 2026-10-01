"""US0969: a CLI never reports a success it did not have.

`validate.py check` on a directory with no workspace printed `checked=0 errors=0` and exited 0;
`sprint_report.fetch_ci_runs` read a forge error object as a window with no runs; and
`artifact.py batch` named the `--template` flag's value while a project-declared template
rendered the stories. Each runs the shipped entry point in a temporary tree.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/validate.py
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402


def _cli(root: Path, script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(_SCRIPTS / script), *argv, "--root", str(root)],
                          cwd=root, env=gitutil.git_env(), capture_output=True, text=True,
                          timeout=300)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class CliNoFalseSuccessTests(unittest.TestCase):

    def test_an_absent_config_key_is_named_not_printed_as_null(self) -> None:
        """AC1. MUTANTS: (1) HEAD - `null` at exit 0; (2) every key refused, so the declared
        `review.blocking_priority` no longer prints (the positive control); (3) a key the
        project sets to null read as absent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], env=gitutil.git_env(), check=True)
            self.assertEqual(0, _cli(root, "init.py", "run").returncode)
            r = _cli(root, "config.py", "show", "--key", "nonexistent.key")
            self.assertEqual(1, r.returncode, r.stdout + r.stderr)
            self.assertIn("nonexistent.key", r.stderr)
            self.assertNotIn("null", r.stdout)
            r = _cli(root, "config.py", "show", "--key", "review.blocking_priority")
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual('"high"', r.stdout.strip())
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.write_text(cfg.read_text(encoding="utf-8") + "\nprobe:\n  unset: null\n",
                           encoding="utf-8")
            r = _cli(root, "config.py", "show", "--key", "probe.unset")
            self.assertEqual(0, r.returncode, r.stderr)
            self.assertEqual("null", r.stdout.strip())

    def test_validate_on_a_directory_with_no_workspace_says_so(self) -> None:
        """AC2. MUTANTS: (1) HEAD - `checked=0 errors=0 warnings=0` at exit 0; (2) the check
        refusing a real workspace too (the positive control: a fresh project exits 0)."""
        with tempfile.TemporaryDirectory() as d:
            r = _cli(Path(d), "validate.py", "check")
            self.assertEqual(1, r.returncode, r.stdout + r.stderr)
            self.assertIn("no sdlc-studio/ workspace", r.stdout + r.stderr)
            self.assertNotIn("checked=0", r.stdout)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], env=gitutil.git_env(), check=True)
            self.assertEqual(0, _cli(root, "init.py", "run").returncode)
            r = _cli(root, "validate.py", "check")
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_a_non_list_gh_answer_reads_unreadable_not_empty(self) -> None:
        """AC3. MUTANTS: (1) HEAD - `([], 'gh run list')`, the shape of an empty window;
        (2) a list answer read as unreadable too (the positive control)."""
        sprint_report = _load("sprint_report")
        for answer, expect_rows, unreadable in (('{"message": "HTTP 403"}', 0, True),
                                                ('[{"databaseId": 1}]', 1, False)):
            with self.subTest(answer), tempfile.TemporaryDirectory() as d:
                bindir = Path(d) / "bin"
                bindir.mkdir()
                gh = bindir / "gh"
                gh.write_text(f"#!/bin/sh\necho '{answer}'\n", encoding="utf-8")
                gh.chmod(0o755)
                with mock.patch.dict(os.environ,
                                     {"PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}"}):
                    rows, source = sprint_report.fetch_ci_runs(Path(d))
                self.assertEqual(expect_rows, len(rows))
                if unreadable:
                    self.assertTrue(source.startswith("gh run list - "), source)
                    self.assertIn("not a list", source)
                else:
                    self.assertEqual("gh run list", source)

    def test_batch_names_the_template_it_rendered(self) -> None:
        """AC4. MUTANT: HEAD - the summary names `template=minimal`, the flag's default, while
        the project's template rendered the stories."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", str(root)], env=gitutil.git_env(), check=True)
            self.assertEqual(0, _cli(root, "init.py", "run").returncode)
            tpl = root / "sdlc-studio" / "templates" / "story.md"
            tpl.parent.mkdir(parents=True)
            tpl.write_text("<!-- house story -->\n\n# {{id}}: {{title}}\n\n## House notes\n\n"
                           "{{notes}}\n\n## Acceptance Criteria\n\n{{acs}}\n",
                           encoding="utf-8")
            cfg = root / "sdlc-studio" / ".config.yaml"
            cfg.write_text(cfg.read_text(encoding="utf-8") + "\nconventions:\n  templates:\n"
                           "    story: sdlc-studio/templates/story.md\n", encoding="utf-8")
            r = _cli(root, "artifact.py", "new", "--type", "epic", "--title", "E",
                     "--format", "json")
            epic = json.loads(r.stdout)["id"]
            spec = root / "spec.json"
            spec.write_text(json.dumps([{"title": "one", "epic": epic},
                                        {"title": "two", "epic": epic}]), encoding="utf-8")
            r = _cli(root, "artifact.py", "batch", "--type", "story", "--spec", str(spec))
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            made = sorted((root / "sdlc-studio" / "stories").glob("US*.md"))
            self.assertEqual(2, len(made))
            self.assertIn("## House notes", made[0].read_text(encoding="utf-8"))
        line = next(ln for ln in r.stdout.splitlines() if ln.startswith("batch:"))
        self.assertIn("sdlc-studio/templates/story.md", line)
        self.assertNotIn("template=minimal", line)


if __name__ == "__main__":
    unittest.main()
