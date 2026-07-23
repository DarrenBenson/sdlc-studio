"""tools/lint_corpus.py - the whole-markdown-corpus lint lane (US0357).

The premise the change request was raised on turned out to be false: nothing here
lints "only changed markdown". Both `npm run lint:md` and the pre-commit `markdown`
lane already glob the whole tree. The real hole is a CONFIG SPLIT. A `**/*.md` glob
cannot match a path inside a dot-directory, so everything under `.claude/` is only
ever reached by the second lane, which runs under
`.claude/skills/sdlc-studio/.markdownlint.json` - a config that switches MD025,
MD035, MD040, MD051, MD055, MD056 and MD060 off. An unescaped table pipe in
`help/sprint.md` therefore sat green for an unknown number of commits: the strict
lane could not see the file and the lane that could see it had the rule disabled.

So the corpus lane enumerates from the TRACKED FILE LIST rather than from a shell
glob, and runs the strict root rule set over every one of them.
"""
from __future__ import annotations

import contextlib
import glob
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


lint_corpus = _load(REPO / "tools" / "lint_corpus.py", "lint_corpus")
#: The shipped git-fixture helper: it confines every fixture git call to the fixture
#: (see its own docstring). Imported rather than re-implemented so this module carries
#: no second copy of the repo-locating variable list.
gitutil = _load(REPO / ".claude/skills/sdlc-studio/scripts/tests/gitutil.py", "_lc_gitutil")

#: markdownlint-cli is a devDependency, so `npm install` provides it. Resolution walks up
#: from the repo, which is what makes this work from an agent worktree as well as a clone.
LINTER = lint_corpus.find_linter(REPO)

ROOT_CONFIG = (REPO / ".markdownlint.json").read_text(encoding="utf-8")
PAYLOAD_CONFIG = (REPO / ".claude/skills/sdlc-studio/.markdownlint.json").read_text(
    encoding="utf-8")

#: A table row whose cell contains unescaped pipes: markdownlint reads them as extra
#: columns (MD056) and as compact-style violations (MD060). This is the observed defect,
#: transcribed - the payload config switches both rules off.
UNESCAPED_PIPE_TABLE = (
    "# Sprint\n"
    "\n"
    "| Outcome | Meaning |\n"
    "| --- | --- |\n"
    "| achieved|partial|missed | the three sprint verdicts |\n"
)
#: The 1-indexed line the defect sits on above. Asserted as a value, not "somewhere".
DEFECT_LINE = 5


def _write(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _init_repo(root: Path) -> None:
    gitutil.git(["init", "-q", "-b", "main"], cwd=root)


def _commit_all(root: Path, message: str) -> str:
    gitutil.git(["add", "-A"], cwd=root)
    gitutil.git(["commit", "-q", "-m", message], cwd=root)
    return gitutil.git(["rev-parse", "HEAD"], cwd=root, text=True).stdout.strip()


class CorpusEnumerationTests(unittest.TestCase):
    def test_tracked_payload_markdown_is_enumerated_despite_the_dot_directory(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init_repo(root)
            _write(root, ".gitignore", "node_modules/\n.claude/worktrees/\n")
            _write(root, "README.md", "# readme\n")
            payload = ".claude/skills/sdlc-studio/help/sprint.md"
            _write(root, payload, "# sprint\n")
            # Ignored trees. Both contain markdown and neither is corpus: node_modules is a
            # third party's, and .claude/worktrees/ holds an agent's in-progress checkout.
            _write(root, "node_modules/pkg/readme.md", "# vendor\n")
            _write(root, ".claude/worktrees/agent-x/scratch.md", "# scratch\n")
            _commit_all(root, "seed")
            # Untracked but not ignored: real on any working tree, still not corpus.
            _write(root, "scratch-untracked.md", "# untracked\n")

            self.assertEqual(lint_corpus.enumerate_corpus(root), [payload, "README.md"])

            # The premise, pinned. A shell glob cannot see into a dot-directory, which is
            # why enumerating from a glob is what let the payload file hide.
            globbed = sorted(glob.glob("**/*.md", root_dir=str(root), recursive=True))
            self.assertIn("README.md", globbed)
            self.assertNotIn(payload, globbed,
                             "if `**/*.md` now matches a dot-directory the config split has "
                             "changed and this lane's premise needs revisiting")


class StrictRuleSetTests(unittest.TestCase):
    def test_a_rule_the_payload_config_relaxes_is_still_reported_by_the_corpus_lane(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init_repo(root)
            _write(root, ".markdownlint.json", ROOT_CONFIG)
            _write(root, ".claude/skills/sdlc-studio/.markdownlint.json", PAYLOAD_CONFIG)
            payload = ".claude/skills/sdlc-studio/help/sprint.md"
            _write(root, payload, UNESCAPED_PIPE_TABLE)
            _commit_all(root, "seed")

            # The hole, measured rather than asserted: under the config the per-commit
            # payload lane uses, this defect is not a finding at all.
            relaxed = lint_corpus.lint_files(
                [payload], cwd=root, linter=LINTER,
                config=root / ".claude/skills/sdlc-studio/.markdownlint.json")
            self.assertEqual([f.rule for f in relaxed if f.rule in ("MD056", "MD060")], [],
                             "the payload config no longer relaxes the observed defect - "
                             "this test's premise has moved")

            findings = lint_corpus.lint_corpus(root, linter=LINTER)

            table = [f for f in findings if f.rule == "MD056"]
            self.assertEqual(len(table), 1, f"expected one MD056 finding, got {findings}")
            self.assertEqual(table[0].path, payload)
            self.assertEqual(table[0].line, DEFECT_LINE)
            self.assertIn("MD060", {f.rule for f in findings},
                          "the strict rule set reports the pipe spacing too")

    def test_a_missing_linter_is_an_error_and_never_a_clean_report(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _init_repo(root)
            _write(root, ".markdownlint.json", ROOT_CONFIG)
            _write(root, "broken.md", UNESCAPED_PIPE_TABLE)
            _commit_all(root, "seed")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                rc = lint_corpus.main(["--root", str(root), "--linter", str(root / "nope")])
            self.assertNotEqual(rc, 0)
            self.assertIn("markdownlint", err.getvalue())
            self.assertNotIn("0 findings", out.getvalue())


class LaneWiringTests(unittest.TestCase):
    def test_the_corpus_lane_is_scheduled_and_absent_from_the_precommit_hook(self) -> None:
        workflow = yaml.safe_load(
            (REPO / ".github/workflows/lint.yml").read_text(encoding="utf-8"))
        # A bare `on:` key parses as the YAML boolean True; accept either spelling.
        triggers = workflow.get("on", workflow.get(True)) or {}
        self.assertIn("schedule", triggers,
                      "the corpus lane must run on a schedule, not only on a push")

        owners = [name for name, job in workflow["jobs"].items()
                  for step in job.get("steps", [])
                  if "lint_corpus.py" in str(step.get("run", ""))
                  or "lint:corpus" in str(step.get("run", ""))]
        self.assertEqual(len(owners), 1, f"exactly one workflow step runs the corpus lane, "
                                         f"found {owners}")
        self.assertNotEqual(owners[0], "ci",
                            "the corpus lane must not sit in the per-push `ci` job")
        self.assertIn("schedule", str(workflow["jobs"][owners[0]].get("if", "")),
                      "the corpus job must be gated on the scheduled/dispatched event, or "
                      "every push pays for a whole-corpus lint")

        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertIn("lint:corpus", scripts)
        self.assertIn("tools/lint_corpus.py", scripts["lint:corpus"])

        hook = (REPO / ".githooks/pre-commit").read_text(encoding="utf-8")
        self.assertNotIn("lint_corpus", hook,
                         "the pre-commit gate already runs ~197s against a 120s budget - the "
                         "corpus lane must add nothing to it")
        self.assertNotIn('run "corpus"', hook)

    def test_the_corpus_lane_is_not_wired_into_the_per_commit_lint_script(self) -> None:
        scripts = json.loads((REPO / "package.json").read_text(encoding="utf-8"))["scripts"]
        self.assertNotIn("lint:corpus", scripts["lint"],
                         "`npm run lint` is the per-commit aggregate; the corpus lane is "
                         "periodic and pre-release")


class CorpusLaneRunsOnThisRepo(unittest.TestCase):
    """The lane against the real corpus. Not a green/red assertion - the repo carries
    hundreds of pre-existing findings - but the enumeration must be real and the run
    must complete, or the lane is wired to nothing."""

    def test_the_real_corpus_is_enumerated_and_linted(self) -> None:
        files = lint_corpus.enumerate_corpus(REPO)
        self.assertGreater(len(files), 100, "the tracked markdown corpus went missing")
        self.assertTrue(any(f.startswith(".claude/skills/sdlc-studio/") for f in files),
                        "the shipped payload is not in the enumeration")
        self.assertTrue(all(f.endswith(".md") for f in files))
        tracked = {p for p in subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, text=True,
            check=True).stdout.split("\0") if p}
        self.assertTrue(set(files) <= tracked, "the lane enumerated an untracked file")


if __name__ == "__main__":
    unittest.main()
