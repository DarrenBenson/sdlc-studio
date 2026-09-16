"""US0815 AC7: the CI workflow installs `coverage` BEFORE the suite that needs it, and the
repository's own docs name the dependency. The order is the assertion - the module was already
installed after the suite, for the coverage gate, and a test for presence alone would have
passed while the suite step ran without it."""
from __future__ import annotations

import ast
import re
import tempfile
import shlex
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
GATE = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "gate.py"
BASELINE = REPO / "tools" / "verify-corpus-baseline.txt"
BUGS = REPO / "sdlc-studio" / "bugs"
CORPUS_JOB = "corpus-verify"
LANE = "tools/verify-corpus.sh"
#: The slowest criterion the corpus lane executes, measured on a developer machine:
#: GateRealWrapperTests, about 136 s, against gate.py's 120 s default ceiling.
SLOWEST_CRITERION_S = 136
#: The red-criteria row's identities at 3f73ab64, the commit the re-measure is judged from. A
#: literal, so an id the re-measure ADDS is judged against a fixed prior set rather than against
#: whatever the file says today.
PRIOR_RED = frozenset(
    "US0021::AC1 US0040::AC3 US0042::AC2 US0047::AC1 US0052::AC4 US0063::AC1 US0063::AC2 "
    "US0070::AC1 US0070::AC2 US0080::AC2 US0165::AC2 US0202::AC3 US0207::AC3 US0268::AC1 "
    "US0284::AC4 US0289::AC2 US0347::AC1 US0512::AC4 US0666::AC1 US0666::AC2".split())
_RUN_LINE = re.compile(r"^# re-measured from CI run (\d+)\s*$", re.M)
_ID = re.compile(r"^[A-Z]{2}\d{4}::AC\d+$")
_JUSTIFIED = re.compile(r"^#\s+(?P<id>[A-Z]{2}\d{4}::AC\d+)\s+(?P<rest>.*)$")
_SEPARATORS = {"&&", "||", ";", "|"}


def _job(name: str) -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"][name]


def _commands(job: dict) -> list[list[str]]:
    """Every live shell command in one job's `run:` steps, as argv. A line YAML keeps inside a
    block but the shell reads as a comment carries nothing, and a trailing comment is cut."""
    out: list[list[str]] = []
    for step in job.get("steps", []):
        for line in str(step.get("run", "")).replace("\\\n", " ").splitlines():
            argv: list[str] = []
            for tok in shlex.split(line, comments=True):
                if tok in _SEPARATORS:
                    out.append(argv)
                    argv = []
                else:
                    argv.append(tok)
            out.append(argv)
    return [a for a in out if a]


def _coverage_requirements(job: dict) -> list[str]:
    """The `coverage` requirement tokens every `pip install` in the job names."""
    found = []
    for argv in _commands(job):
        names = [Path(t).name for t in argv]
        pips = [i for i, t in enumerate(names) if t in ("pip", "pip3")]
        if not pips or "install" not in argv[pips[0] + 1:]:
            continue
        found += [t for t in argv[argv.index("install", pips[0]) + 1:]
                  if re.match(r"^coverage(\[[^\]]*\])?(?![\w.-])", t)]
    return found


def _override_name() -> str:
    """The variable gate.py's verify lane reads, taken from the read itself in its source."""
    tree = ast.parse(GATE.read_text(encoding="utf-8"))
    consts = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign)
              and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)
              for t in n.targets if isinstance(t, ast.Name)}
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "_verify_timeout")
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "environ" and node.args):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                return arg.value
            if isinstance(arg, ast.Name) and arg.id in consts:
                return consts[arg.id]
    raise AssertionError("gate.py's `_verify_timeout` reads no environment variable")


def _baseline_problems(text: str, bugs: Path) -> list[str]:
    """Why a re-measured red-criteria baseline cannot be trusted, or [] when it can."""
    problems = []
    if not _RUN_LINE.search(text):
        problems.append("no `# re-measured from CI run <databaseId>` line")
    row = next((ln for ln in text.splitlines() if ln.startswith("red-criteria|")), None)
    if row is None:
        return problems + ["no red-criteria row"]
    fields = row.split("|", 3)
    if len(fields) != 4 or not fields[1].isdigit():
        return problems + [f"the red-criteria row is not `metric|count|prose|ids`: {row}"]
    ids = fields[3].split()
    stray = [t for t in ids if not _ID.match(t)]
    if stray:
        problems.append(f"field 4 carries non-id token(s), which the lane reads as ids: {stray}")
    if int(fields[1]) != len(ids):
        problems.append(f"the row counts {fields[1]} and names {len(ids)} id(s)")
    reasons: dict[str, list[str]] = {}
    for ln in text.splitlines():
        m = _JUSTIFIED.match(ln)
        if m:
            reasons.setdefault(m["id"], []).append(m["rest"])

    def justified(rest: str) -> bool:
        return bool(re.search(r"\bcause:\s*\S", rest)) or any(
            any(bugs.glob(f"{bg}-*.md")) for bg in re.findall(r"\bBG\d{4}\b", rest))

    for ident in (i for i in ids if i not in PRIOR_RED):
        if not any(justified(r) for r in reasons.get(ident, [])):
            problems.append(f"{ident} was added with no comment line of its own naming an "
                            f"existing bug or a `cause:`")
    return problems


class CoverageBeforeSuiteTests(unittest.TestCase):
    def test_coverage_is_installed_before_the_suite_runs_and_named_as_a_dependency(self) -> None:
        """MUTANTS: move the coverage install step below the suite step in lint.yml; delete
        `coverage` from AGENTS.md's soft-dependency table; drop the `>=7.10` floor from the
        install line."""
        text = (REPO / ".github" / "workflows" / "lint.yml").read_text(encoding="utf-8")
        install = re.search(r"pip install[^\n]*'coverage>=7\.10'", text)
        self.assertIsNotNone(install, "lint.yml must install coverage>=7.10 explicitly")
        suite = text.index("bash tools/skill-tests.sh")
        self.assertLess(install.start(), suite, "the coverage install must sit BEFORE the suite step, by position")
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        start = agents.index("## Soft dependencies")
        self.assertIn("`coverage` 7.10 or later", agents[start:start + 2000], "AGENTS.md's soft-dependency table must name coverage")
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("**coverage** 7.10 or later, needed only by `verify_ac run --coverage`", readme, "README's dependency sentence must name coverage and what needs it")
        self.assertNotIn("PyYAML** is the one optional dependency", readme)


class CorpusJobEnvironmentTests(unittest.TestCase):
    """The scheduled corpus-verify job read 20 criteria red that pass on any developer machine:
    it lacked `coverage`, gave verifiers the 120 s default, and cloned one commit deep. Each is
    pinned against that job's own block, never the whole file, because the ci job already
    carries the same install and a whole-file search finds it there."""

    def test_the_corpus_job_installs_coverage(self) -> None:
        """MUTANTS: drop `'coverage>=7.10'` from the corpus-verify install while the ci job's
        keeps it; install plain `coverage`, unversioned; leave the install at `pyyaml pytest`
        and add `# pip install 'coverage>=7.10'` under the job as a comment."""
        job = _job(CORPUS_JOB)
        reqs = _coverage_requirements(job)
        self.assertTrue(reqs, f"no live `pip install` in the {CORPUS_JOB} job names coverage: "
                              f"{_commands(job)}")
        for req in reqs:
            self.assertRegex(req, r"^coverage(\[[^\]]*\])?>=7\.10(?!\d)",
                             f"the {CORPUS_JOB} job installs coverage without the >=7.10 floor")
        # The reader is scoped, not lucky: the same reader over the ci job finds that job's own
        # floored install, and a commented-out install reads as nothing.
        self.assertIn("coverage>=7.10", _coverage_requirements(_job("ci")))
        self.assertEqual(_coverage_requirements(
            {"steps": [{"run": "# pip install 'coverage>=7.10'\npip install pyyaml pytest"}]}), [])

    def test_the_corpus_job_gives_verifiers_time(self) -> None:
        """MUTANTS: set the override to 130 s, above the 120 s default yet short of the 136 s
        the slowest criterion needs; set it on the ci job's suite step instead; rename it in the
        corpus job to `SDLC_VERIFY_TIMEOUT_S`, which gate.py never reads.

        Only the job's own env or its verification step's env counts: a value on another step
        of the job never reaches the lane."""
        name = _override_name()
        self.assertEqual(name, "SDLC_VERIFY_TIMEOUT", "the name AC2's lane reads has moved")
        job = _job(CORPUS_JOB)
        lanes = [s for s in job.get("steps", []) if LANE in str(s.get("run", ""))]
        self.assertEqual(len(lanes), 1, f"exactly one {CORPUS_JOB} step runs {LANE}")
        step_env = lanes[0].get("env") or {}
        value = step_env[name] if name in step_env else (job.get("env") or {}).get(name)
        self.assertIsNotNone(value, f"the {CORPUS_JOB} job sets no {name} on itself or on the "
                                    f"step that runs {LANE}")
        self.assertNotIsInstance(value, bool)
        self.assertRegex(str(value), r"^\d+$", f"{name} must be whole seconds, got {value!r}")
        self.assertGreater(int(value), SLOWEST_CRITERION_S,
                           f"{name}={value} does not clear the slowest criterion's "
                           f"{SLOWEST_CRITERION_S} s")

    def test_the_baseline_names_its_ci_run(self) -> None:
        """MUTANTS: append US0031::AC3 to field 4 and bump the count with no new comment line,
        so only the header prose mentions it; write no CI run line; justify an added id with
        BG9999, which no file carries; justify one with a bare `cause:`.

        The controls first, so a checker that refuses every id, or none, fails here rather
        than passing a real baseline that happens to add nothing."""
        bug = "BG0001"
        self.assertFalse(any(BUGS.glob("BG9999-*.md")), "the negative control's id exists")
        prior = " ".join(sorted(PRIOR_RED))

        def page(*comments: str, extra: str = "", run: bool = True) -> str:
            ids = f"{prior} {extra}".strip()
            head = ["# re-measured from CI run 1234567890"] if run else ["# local 3f73ab64"]
            return "\n".join(head + list(comments) + [
                f"red-criteria|{len(ids.split())}|what it counts|{ids}", ""])

        with tempfile.TemporaryDirectory() as d:
            fake_bugs = Path(d)
            (fake_bugs / f"{bug}-x.md").write_text("x", encoding="utf-8")
            good = page("# US9998::AC1 cause: coverage, absent on the runner",
                        f"# US9999::AC2 - {bug}", extra="US9998::AC1 US9999::AC2")
            self.assertEqual(_baseline_problems(good, fake_bugs), [],
                             "a baseline whose added ids each carry a cause or a real bug is "
                             "refused, so the checker refuses everything")
            for why, bad in {
                "prose mention only": page("# Its extra row was US9998::AC1, which timed out",
                                           extra="US9998::AC1"),
                "no run line": page("# US9998::AC1 cause: coverage", extra="US9998::AC1",
                                    run=False),
                "a bug no file carries": page("# US9998::AC1 - BG9999", extra="US9998::AC1"),
                "a bare cause": page("# US9998::AC1 cause:", extra="US9998::AC1"),
                "a count its list does not support":
                    page().replace("red-criteria|20|", "red-criteria|21|"),
                "a cause written into field 4": page(extra="US9998::AC1 cause: coverage"),
            }.items():
                self.assertNotEqual(_baseline_problems(bad, fake_bugs), [], why)

        problems = _baseline_problems(BASELINE.read_text(encoding="utf-8"), BUGS)
        self.assertEqual(problems, [], f"{BASELINE.name} cannot be trusted as a re-measure: "
                                       f"{problems}")


if __name__ == "__main__":
    unittest.main()
