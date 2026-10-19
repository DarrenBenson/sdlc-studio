"""US1085: the TRD's stack and the TSD's framework rows name what the clone installs, and the
TSD names each CI job with the trigger it runs on.

Every fact is read from the file it describes (LL0043), never typed here: the packages from
requirements-dev.txt and package.json, the lint chain from package.json's `lint` script, the jobs
and their triggers from .github/workflows/*.yml, and the Python floor from the versions the `ci`
job installs. Each derived set first asserts a member known to be in it. Versions are read as
the workflow's text, never through YAML, which reads an unquoted 3.10 as the number 3.1.
"""
# test-census-subject: sdlc-studio/tsd.md
from __future__ import annotations

import ast
import json
import re
import sys
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
TRD = REPO / "sdlc-studio" / "trd.md"
TSD = REPO / "sdlc-studio" / "tsd.md"
WORKFLOWS = REPO / ".github" / "workflows"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """The body under the first heading whose title starts with `heading`, up to the next heading
    of the same or a higher level."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s+(.*)$", line)
        if m and m.group(2).startswith(heading):
            level, out = len(m.group(1)), []
            for nxt in lines[i + 1:]:
                n = re.match(r"^(#+)\s", nxt)
                if n and len(n.group(1)) <= level:
                    break
                out.append(nxt)
            return "\n".join(out)
    raise AssertionError(f"no section headed {heading!r}")


def _blocks(text: str) -> list[str]:
    """Paragraphs, list items and table rows, each a block of its own."""
    blocks, cur = [], []
    for line in text.splitlines():
        starts = bool(re.match(r"^\s*(\d+\.|[-*]|\|)\s", line))
        if not line.strip() or (starts and cur):
            if cur:
                blocks.append(" ".join(cur))
            cur = [line.strip()] if line.strip() else []
        else:
            cur.append(line.strip())
    if cur:
        blocks.append(" ".join(cur))
    return blocks


def _named(name: str, text: str) -> bool:
    """`name` appears as a word of its own, not inside a longer name (`pytest` in `pytest-xdist`)."""
    return re.search(rf"(?<![\w.-]){re.escape(name)}(?![\w-])", text) is not None


def _current(path: Path) -> str:
    """The document as a claim about now: its revision history records what was true when each
    row was written, so it is left out."""
    return _read(path).split("\n## Revision History", 1)[0]


def _soft_dependencies() -> set[str]:
    """Third-party modules the shipped scripts import inside a `try` that catches the import's
    failure: what a feature degrades without, read from the code rather than listed here."""
    scripts = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
    files = sorted([*scripts.glob("*.py"), *(scripts / "lib").glob("*.py")])
    local = {f.stem for f in files} | {"lib"}
    found = set()
    for f in files:
        for node in ast.walk(ast.parse(_read(f))):
            if not isinstance(node, ast.Try):
                continue
            caught = {getattr(e, "id", "") for h in node.handlers if h.type is not None
                      for e in (h.type.elts if isinstance(h.type, ast.Tuple) else [h.type])}
            if not caught & {"ImportError", "ModuleNotFoundError"}:
                continue
            for n in (x for stmt in node.body for x in ast.walk(stmt)):
                mods = ([a.name for a in n.names] if isinstance(n, ast.Import)
                        else [n.module] if isinstance(n, ast.ImportFrom) and n.level == 0 and n.module
                        else [])
                found |= {m.split(".")[0] for m in mods} - set(sys.stdlib_module_names) - local
    return found


#: The distribution a soft dependency's import name installs from, where the two differ.
DISTRIBUTION = {"yaml": "PyYAML"}


def _requirements() -> list[str]:
    names = []
    for line in _read(REPO / "requirements-dev.txt").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.append(re.match(r"[A-Za-z0-9][A-Za-z0-9._-]*", line).group(0))
    return names


#: How each GitHub event reads in the documents.
EVENT_WORD = {"push": "push", "pull_request": "pull request", "schedule": "schedule",
              "workflow_dispatch": "dispatch"}


def _jobs() -> dict[str, set[str]]:
    """Each job, with the triggers it runs on: the workflow's events, narrowed by the job's own
    `if` where it names `github.event_name`, and a push filtered to tags read as `tag`."""
    out: dict[str, set[str]] = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        doc = yaml.safe_load(_read(wf))
        on = doc.get(True, doc.get("on")) or {}
        events = on if isinstance(on, dict) else {e: None for e in ([on] if isinstance(on, str) else on)}
        for name, job in doc["jobs"].items():
            cond = str(job.get("if") or "")
            named = set(re.findall(r"github\.event_name\s*==\s*'(\w+)'", cond))
            words = set()
            for event, spec in events.items():
                if named and event not in named:
                    continue
                if event == "push" and isinstance(spec, dict) and "tags" in spec:
                    words.add("tag")
                else:
                    words.add(EVENT_WORD.get(event, event))
            out[name] = words
    return out


class GateToolchainDocsTests(unittest.TestCase):

    def test_every_declared_dependency_is_named(self) -> None:
        """AC1. Mutants: a package dropped from the TRD's stack or the TSD's framework rows; the TRD
        no longer naming requirements-dev.txt as the one Python list."""
        python = _requirements()
        node = list(json.loads(_read(REPO / "package.json")).get("devDependencies", {}))
        self.assertIn("pytest-xdist", python, "requirements-dev.txt was not read")
        self.assertIn("markdownlint-cli", node, "package.json was not read")
        stack = _section(_read(TRD), "4. Technology Stack")
        framework = _section(_read(TSD), "Automation Framework Stack")
        for name in python + node:
            with self.subTest(package=name):
                self.assertTrue(_named(name, stack), f"the TRD's technology stack does not name {name}")
                self.assertTrue(_named(name, framework), f"the TSD's framework rows do not name {name}")
        self.assertTrue(any(re.search(r"(?i)`requirements-dev\.txt` is the (?:one|only|single) Python "
                                      r"dependency list", b) for b in _blocks(stack)),
                        "the TRD does not name requirements-dev.txt as the one Python dependency list")

    def test_the_shipped_scripts_soft_dependencies_are_named(self) -> None:
        """The TRD's statement of the shipped scripts' soft dependencies names each one the code
        guards an import of. Mutant: one dropped, or the sentence back to naming PyYAML alone."""
        soft = _soft_dependencies()
        self.assertIn("yaml", soft, "the shipped scripts' guarded imports were not read")
        stack = _section(_read(TRD), "4. Technology Stack")
        rows = [r for r in stack.splitlines() if r.startswith("|") and "soft dependenc" in r]
        self.assertTrue(rows, "the TRD's stack does not state the shipped scripts' soft dependencies")
        for module in sorted(soft):
            name = DISTRIBUTION.get(module, module)
            with self.subTest(dependency=name):
                self.assertTrue(any(_named(name, r) for r in rows), f"the TRD does not name the soft dependency {name}")

    def test_every_ci_job_is_named_with_its_trigger(self) -> None:
        """AC2. Mutants: a job dropped, or named without a trigger it runs on; the baseline file
        unnamed, or named without what it compares."""
        jobs = _jobs()
        self.assertIn("corpus-verify", jobs, "the workflows were not read")
        self.assertIn("tag", jobs.get("publish", set()), "a tag-filtered push was not read as a tag")
        tsd = _read(TSD)
        table = [r for r in _section(tsd, "CI jobs").splitlines() if r.startswith("| `")]
        for job, triggers in sorted(jobs.items()):
            with self.subTest(job=job):
                rows = [r for r in table if r.split("|")[1].strip() == f"`{job}`"]
                self.assertEqual(len(rows), 1, f"the TSD's CI jobs table has no row of its own for {job}")
                cell = rows[0].split("|")[3]
                tag = bool(re.search(r"(?i)\btag push\b", cell))
                rest = re.sub(r"(?i)\btag push\b", "", cell)
                stated = {w for w, pat in (("push", r"\bpush\b"), ("pull request", r"\bpull request\b"),
                                           ("schedule", r"\bschedule\b"), ("dispatch", r"\bdispatch\b"))
                          if re.search(rf"(?i){pat}", rest)} | ({"tag"} if tag else set())
                self.assertEqual(stated, triggers, f"the TSD gives {job} the wrong triggers")
        baseline = [b for b in _blocks(tsd) if "tools/verify-corpus-baseline.txt" in b]
        self.assertTrue(baseline, "the TSD does not name the corpus baseline")
        self.assertTrue(any(re.search(r"(?i)select", b) and re.search(r"(?i)fail", b) for b in baseline),
                        "the TSD names the baseline without what it compares")

    def test_every_lint_check_is_named_uncounted(self) -> None:
        """AC3. Mutants: a check of the chain left unnamed; a count of the checks stated."""
        scripts = json.loads(_read(REPO / "package.json"))["scripts"]
        chain = re.findall(r"npm run (lint:[\w-]+)", scripts["lint"])
        self.assertIn("lint:md", chain, "the lint chain was not read")
        tsd = _read(TSD)
        for check in chain:
            with self.subTest(check=check):
                self.assertIn(f"`{check}`", tsd, f"the TSD does not name {check}")
        number = r"(?:\d+|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
        counted = re.compile(rf"(?i)\b{number}(?:\s+[\w-]+)?\s+(?:sub-?)?(?:checks?|checkers?|lints|linters|guards|"
                             rf"steps|scripts|tools)\b|\b{number}\s+of\s+the\s+{number}\b")
        for doc in (TRD, TSD):
            # The revision history records what was true when each row was written, so a count
            # there is history, not a claim about the chain as it stands.
            for b in _blocks(_current(doc)):
                if "lint" in b.lower():
                    self.assertIsNone(counted.search(b), f"{doc.name} counts the lint checks: {b[:160]}")

    def test_the_python_floor_matches_ci(self) -> None:
        """AC4. Mutant: the TRD stating a floor other than the oldest version the ci job installs."""
        text = _read(WORKFLOWS / "lint.yml")
        ci = re.search(r"^  ci:\n(.*?)(?=^  \S)", text, re.M | re.S).group(1)
        versions = re.findall(r"python-version:\s*['\"]?(\d+\.\d+)", ci)
        self.assertIn("3.12", versions, "the ci job's Python versions were not read")
        floor = min(versions, key=lambda v: tuple(int(x) for x in v.split(".")))
        rows = [r for r in _section(_read(TRD), "4. Technology Stack").splitlines()
                if r.startswith("|") and re.search(r"\bPython\b", r)]
        self.assertTrue(rows, "the TRD's stack has no Python row")
        stated = {v for b in _blocks(_current(TRD)) if re.search(r"\bPython\b", b)
                  for v in re.findall(r"(?<![\d.])3\.\d+\+", b)}
        self.assertEqual(stated, {f"{floor}+"}, f"the TRD states a Python floor other than {floor}, the oldest ci installs")


if __name__ == "__main__":
    unittest.main()
