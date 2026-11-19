"""`sprint drive` walks one unit's lane from build to paperwork and stops with a decision record.

Every case drives `sprint.py drive` through `sprint.main` against a throwaway repository with an
open run, a stub pre-commit hook and a stub `claude` CLI on PATH. As a builder the stub stages the
unit's files and its hand-in in the lane's worktree; as a reviewer, given a brief naming a verdict
file, it writes the verdict its spec names there (an APPROVE unless told otherwise). Both print the
captured Claude Code usage (`fixtures/harness_usage/claude.json`), so every lane is metered, and
both log each session. `lane run`, `lane land`, `critic.py`, `lane accept`, `verify_ac.py`,
`transition.py` and the paperwork commit all run for real. HOME, XDG_DATA_HOME and
CLAUDE_CONFIG_DIR point into the fixture, never at the operator's harness store.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil
import loader

SCRIPTS = Path(__file__).resolve().parent.parent
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from lib import drive, run_state  # noqa: E402

critic = loader.load_script("critic")
sprint = loader.load_script("sprint")

A, B, C = "US0101", "US0102", "US0103"
USAGE = Path(__file__).resolve().parent / "fixtures" / "harness_usage" / "claude.json"
HOOK = """#!/bin/sh
git rev-parse --show-toplevel >> "{log}"
if [ -f "{refuse}" ]; then
  i=1
  while [ $i -le 60 ]; do echo "stub hook line $i" >&2; i=$((i+1)); done
  exit 1
fi
{sleep}
exit 0
"""
STUB = """#!{python}
import json, os, re, subprocess, sys, time
from pathlib import Path
argv = sys.argv[1:]
prompt = argv[argv.index("-p") + 1]
spec = json.loads(Path(os.environ["DRIVE_STUB_SPEC"]).read_text())
log = Path(os.environ["DRIVE_STUB_LOG"])
usage = Path(os.environ["DRIVE_STUB_USAGE"]).read_text()

def note(**event):
    event["at"] = time.time()
    with log.open("a") as fh:
        fh.write(json.dumps(event) + "\\n")

found = re.findall(r"^(/.*/sdlc-studio/reviews/verdicts/.+\\.txt)\\nUNIT: (\\S+)\\nBRIEF: (\\S+)\\s*$",
                   prompt, re.M)
if found:
    path, unit, stem = found[-1]
    verdict = spec.get(unit, {{}}).get("verdict") or "VERDICT: APPROVE\\nISSUES: none\\nBLOCKING: none\\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(f"UNIT: {{unit}}\\nBRIEF: {{stem}}\\n{{verdict}}")
    note(role="review", unit=unit)
    print(usage)
    sys.exit(0)
unit = re.search(r"^Unit: (\\S+)", prompt, re.M).group(1)
mine = spec[unit]
probe = Path(mine["probe"]).read_text() if mine.get("probe") else None
note(role="build", unit=unit, event="start", probe=probe)
time.sleep(mine.get("sleep", 0))
for rel, body in mine["files"].items():
    Path(rel).parent.mkdir(parents=True, exist_ok=True)
    Path(rel).write_text(body)
    subprocess.run(["git", "add", "--", rel], check=True)
lane = Path("sdlc-studio/.local/lane")
lane.mkdir(parents=True, exist_ok=True)
(lane / "commit-msg.txt").write_text(f"feat({{unit}}): {{unit}} lands\\n")
claims = [{{"surface": "commit message", "claim": "it lands", "ruling": "TRUE"}},
          {{"surface": f"changelog.d/{{unit}}.md", "claim": "it lands", "ruling": "TRUE"}}]
(lane / f"{{unit}}-claims.json").write_text(json.dumps(claims))
(lane / f"{{unit}}-mutants.json").write_text("[]")
note(role="build", unit=unit, event="end")
print(usage)
"""
REJECT = ("VERDICT: REJECT\nISSUES: [new] the gate lets a red unit through\n"
          "BLOCKING: [new] the gate lets a red unit through\n")


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _git(cwd: Path, *args: str) -> str:
    return gitutil.git(list(args), cwd, text=True).stdout.strip()


def stops_named(text: str) -> set[str]:
    """The stops a page lists in its `five points only` sentence, each `a <stop>`."""
    flat = " ".join(text.split())
    found = re.search(r"five points only[^:]*:\s*(.+?)\.(?:\s|$)", flat)
    if not found:
        return set()
    items = re.split(r",\s*|\s+and\s+|\s+or\s+", re.sub(r"\([^)]*\)", "", found.group(1)))
    return {" ".join(item.split()) for item in items if item.strip()}


class _DriveFixture(unittest.TestCase):
    """The repository, its open run, its stub hook and its stub harness."""

    #: unit -> its Affects
    UNITS = {A: ["src/a.py"]}
    WAVES: list | None = None
    STATUS = "Ready"
    HOOK_SLEEP = 0

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = base = Path(self._tmp.name).resolve()
        self.root = root = base / "repo"
        self.log, self.refuse = base / "hook.log", base / "refuse"
        self.spec_path, self.stub_log = base / "spec.json", base / "stub.log"
        _write(root, ".gitignore", "sdlc-studio/.local/\n")
        for rel in ("src/a.py", "src/b.py", "src/c.py", "src/shared.py"):
            _write(root, rel, f"{Path(rel).stem.upper()} = 1\n")
        _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam\n\ncharter\n")
        _write(root, "sdlc-studio/.config.yaml", self.config())
        for unit, affects in self.UNITS.items():
            _write(root, f"sdlc-studio/stories/{unit}-drive.md",
                   f"# {unit}: drive\n\n> **Status:** {self.STATUS}\n> **Points:** 2\n"
                   f"> **Epic:** EP0001\n> **Affects:** {', '.join(affects)}, "
                   f"changelog.d/{unit}.md\n\n## Acceptance Criteria\n\n### AC1: works\n"
                   f"- **Verify:** shell true\n")
        gitutil.git(["init", "-q", "-b", "main"], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "chore: the fixture"], root)
        sleep = f"sleep {self.HOOK_SLEEP}" if self.HOOK_SLEEP else ""
        _write(base, "hooks/pre-commit", HOOK.format(log=self.log, refuse=self.refuse,
                                                     sleep=sleep)).chmod(0o755)
        gitutil.git(["config", "core.hooksPath", str(base / "hooks")], root)
        _write(base, "bin/claude", STUB.format(python=sys.executable)).chmod(0o755)
        self.home = base / "home"
        (base / "no-transcripts").mkdir()
        self.env = gitutil.git_env(
            PATH=f"{base / 'bin'}{os.pathsep}{os.environ.get('PATH', '')}",
            HOME=str(self.home), CLAUDE_CONFIG_DIR=str(self.home / ".claude"),
            XDG_DATA_HOME=str(self.home / ".local" / "share"),
            DRIVE_STUB_SPEC=str(self.spec_path), DRIVE_STUB_LOG=str(self.stub_log),
            DRIVE_STUB_USAGE=str(USAGE), **{run_state.TRANSCRIPTS_ENV: str(base / "no-transcripts")})
        self.spec({u: {"files": {a[0]: f"{u} = 2\n", f"changelog.d/{u}.md": "x\n"}}
                   for u, a in self.UNITS.items()})
        with unittest.mock.patch.dict(os.environ, self.env, clear=True):
            run_state.open_run(root, batch=list(self.UNITS), goal="g")
        if self.WAVES:
            _write(root, "sdlc-studio/.local/sprint-plan.json", json.dumps({"waves": self.WAVES}))

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def config(self) -> str:
        return "review:\n  author_self_check: block\n"

    def spec(self, spec: dict) -> None:
        self.spec_path.write_text(json.dumps(spec), encoding="utf-8")

    def sessions(self) -> list[dict]:
        if not self.stub_log.is_file():
            return []
        return [json.loads(ln) for ln in self.stub_log.read_text(encoding="utf-8").splitlines()]

    def run_sprint(self, *argv: str, wrap=None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        real = drive.run_script
        spy = (lambda root, script, *args, **kw: wrap(real, root, script, *args, **kw)) \
            if wrap else real
        with unittest.mock.patch.dict(os.environ, self.env, clear=True), \
                unittest.mock.patch.object(drive, "run_script", spy), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = sprint.main([*argv, "--root", str(self.root)])
        return rc, out.getvalue(), err.getvalue()

    def drive(self, wrap=None) -> tuple[int, str, str]:
        return self.run_sprint("drive", "--harness", "claude", wrap=wrap)

    def status_at(self, unit: str, ref: str = "HEAD") -> str:
        text = _git(self.root, "show", f"{ref}:sdlc-studio/stories/{unit}-drive.md")
        return re.search(r"\*\*Status:\*\* (.+)", text).group(1).strip()

    def subjects(self) -> list[str]:
        return _git(self.root, "log", "--format=%s").splitlines()

    def dirty(self) -> list[str]:
        return _git(self.root, "status", "--porcelain", "--", "sdlc-studio").splitlines()

    @staticmethod
    def record_of(out: str) -> list[str]:
        lines = out.splitlines()
        start = next(n for n, ln in enumerate(lines) if ln.startswith("DRIVE STOPPED"))
        return lines[start:]


class SprintDriveTests(_DriveFixture):

    def test_a_clean_unit_is_driven_from_build_to_paperwork(self) -> None:
        rc, out, err = self.drive()
        self.assertEqual(0, rc, out + err)
        at = [next((n for n, ln in enumerate(out.splitlines())
                    if ln.startswith(f"{A} {step}: ")), None) for step in drive.STEPS]
        self.assertNotIn(None, at, f"a step printed no line:\n{out}")
        self.assertEqual(sorted(at), at, f"the steps ran out of order:\n{out}")
        self.assertEqual(len(drive.STEPS), len(set(at)), "two steps shared one line")
        # the build ran in the lane's worktree before the review ran in the root
        self.assertEqual(["build", "build", "review"], [s["role"] for s in self.sessions()])
        self.assertEqual("Done", self.status_at(A))
        self.assertEqual([], self.dirty(), "the paperwork was left uncommitted")
        subjects = self.subjects()
        self.assertTrue(subjects[0].startswith(f"docs({A}): record {A}'s review"), subjects)
        self.assertEqual(f"feat({A}): {A} lands", subjects[1])
        verdicts = critic.verdicts_path(self.root).read_text(encoding="utf-8")
        self.assertIn(f"| {A} | APPROVE |", verdicts)
        self.assertIn(f"wave 1 of 1 ended, {drive.WAVE_END}", out)
        self.assertIn(f"  {A}: Done", out)

    def test_a_refused_step_stops_the_walk_with_a_decision_record(self) -> None:
        self.refuse.write_text("on\n", encoding="utf-8")
        rc, out, err = self.drive()
        self.assertNotEqual(0, rc, out + err)
        self.assertIn(f"{A} build: ", out)
        for step in drive.STEPS[1:]:
            self.assertNotIn(f"{A} {step}: ", out, f"{step} ran after the refused landing")
        self.assertEqual(["build"], sorted({s["role"] for s in self.sessions()}),
                         "a reviewer ran after the refused landing")
        record = self.record_of(out)
        self.assertLessEqual(len(record), drive.RECORD_LINES, "\n".join(record))
        text = "\n".join(record)
        self.assertIn(f"DRIVE STOPPED: {A} at land, {drive.REFUSAL}", text)
        self.assertIn("exit status: 1", text)
        self.assertIn("stub hook line 60", text)
        self.assertNotIn("stub hook line 1\n", text + "\n", "the record printed the whole log")
        kept = re.search(r"^  whole output: (\S+)", text, re.M).group(1)
        self.assertIn("stub hook line 60", (self.root / kept).read_text(encoding="utf-8"))
        hook = re.search(r"the commit's whole output: (\S+)", text).group(1)
        self.assertIn("stub hook line 1\n", Path(hook).read_text(encoding="utf-8"))
        self.assertIn("resume: ", text)
        self.assertIn("sprint.py drive --harness claude", text)
        self.assertEqual(self.STATUS, self.status_at(A, "HEAD"))
        self.assertEqual(["chore: the fixture"], self.subjects())
        # the command the record names resumes the walk at the landing, building nothing again
        self.refuse.unlink()
        rc, out, err = self.drive()
        self.assertEqual(0, rc, out + err)
        self.assertIn(f"{A}: resuming at land", out)
        self.assertEqual(1, sum(1 for s in self.sessions() if s.get("event") == "start"))
        self.assertEqual("Done", self.status_at(A))

    def test_a_reject_stops_the_walk_and_names_the_repair_brief(self) -> None:
        self.spec({A: {"files": {"src/a.py": "A = 2\n", f"changelog.d/{A}.md": "x\n"},
                       "verdict": REJECT}})
        rc, out, err = self.drive()
        self.assertNotEqual(0, rc, out + err)
        rows = [ln for ln in critic.verdicts_path(self.root).read_text(encoding="utf-8")
                .splitlines() if ln.startswith(f"| {A} |")]
        self.assertEqual(1, len(rows), rows)
        self.assertIn("| REJECT |", rows[0])
        for step in ("return", "paperwork"):
            self.assertNotIn(f"{A} {step}: ", out)
        self.assertEqual(self.STATUS, self.status_at(A, "HEAD"))
        self.assertEqual(f"feat({A}): {A} lands", self.subjects()[0])
        text = "\n".join(self.record_of(out))
        self.assertIn(f"DRIVE STOPPED: {A} at accept, {drive.REJECTED}", text)
        self.assertIn("BLOCKING: [new] the gate lets a red unit through", text)
        self.assertIn(f"resume: sprint.py lane brief --repair --units {A}", text)
        # drive spawned no repair: one build session, one review session
        self.assertEqual(["build", "build", "review"], [s["role"] for s in self.sessions()])
        self.assertFalse((self.root / drive.PROMPTS).exists())
        # a re-run resumes at the brief, runs no reviewer over the written verdict, and the
        # verdict already recorded is refused, never recorded twice
        rc, out, err = self.drive()
        self.assertNotEqual(0, rc, out + err)
        self.assertIn(f"{A}: resuming at brief", out)
        self.assertIn("is already written; no reviewer is run again", out)
        self.assertEqual(["build", "build", "review"], [s["role"] for s in self.sessions()])
        self.assertEqual(1, len([ln for ln in critic.verdicts_path(self.root).read_text(
            encoding="utf-8").splitlines() if ln.startswith(f"| {A} |")]))
        self.assertEqual(self.STATUS, self.status_at(A, "HEAD"))

    def test_the_help_and_reference_name_each_stop(self) -> None:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit):
            sprint.main(["drive", "--help"])
        help_page = (SKILL / "help" / "sprint.md").read_text(encoding="utf-8")
        section = re.search(r"^## Driving a wave.*?(?=^## |\Z)", help_page, re.M | re.S)
        self.assertIsNotNone(section, "help/sprint.md has no Driving a wave section")
        reference = (SKILL / "reference-sprint.md").read_text(encoding="utf-8")
        boundary = re.search(r"^### The wave boundary.*?(?=^#)", reference, re.M | re.S)
        pages = {"--help": out.getvalue(), "help/sprint.md": section.group(0),
                 "reference-sprint.md": boundary.group(0)}
        parser = sprint.build_parser()
        drive_parser = next(a for a in parser._actions  # noqa: SLF001
                            if isinstance(a, sprint.argparse._SubParsersAction)  # noqa: SLF001
                            ).choices["drive"]
        accepted = {opt for action in drive_parser._actions  # noqa: SLF001
                    for opt in action.option_strings}
        for name, text in pages.items():
            with self.subTest(page=name):
                self.assertIn("drive", text)
                self.assertEqual(set(drive.STOPS), stops_named(text),
                                 f"{name} names other stops than the loop makes")
                flat = " ".join(text.split())
                self.assertIn("non-zero", flat)
                for step in drive.STEPS:
                    self.assertRegex(flat, rf"\b{step}\b")
                spans = re.findall(r"`([^`]*drive[^`]*)`", text)
                spans += [ln for ln in text.splitlines() if "sprint.py drive" in ln]
                flags = {f for span in spans for f in re.findall(r"(?<![\w-])--[a-z][a-z-]*",
                                                                 span)}
                self.assertEqual(set(), flags - accepted,
                                 f"{name} names a drive flag the parser refuses")
        self.assertIn("sprint.py drive --harness", section.group(0))
        self.assertIn("sprint.py drive step --after", section.group(0))


if __name__ == "__main__":
    unittest.main()
