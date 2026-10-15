"""US1004: CI and the prerequisite checker read one list of the suite's Python packages.

`tools/gate_prereqs.py` checks a clone against `requirements-dev.txt`; CI's suite step installed
its own inline list, so the two could drift and a clone could pass the checker yet miss what CI
runs with. The ci job now installs from the file. The scheduled corpus-verify job keeps its own
list on purpose (moving it would add pytest-xdist to a lane compared against a recorded
baseline), so it is held to a declared subset instead.

What the reader reads (BG1053), each spelling listed in `test_the_readers_and_rules_refuse_what_
they_must`: pip run as `pip`, `pip3`, `pip3.12`, a path to one, `python -m pip` or `uv pip`, with
pip's general options before `install`; `-r` and `-c` given separately, attached (`-rFILE`),
clustered (`-qrFILE`, `-qr FILE`) or long with `=`; and a requirements file's own `-r` lines. A
`PIP_REQUIREMENT` or `PIP_CONSTRAINT` variable, and a ci install run from another directory, are
refused outright. Anything else (a pip config file, a wrapper script) is not read.

MUTANTS: the inline package list left in the ci job's suite step (AC1); a second requirements
file on the suite step, a ci step installing anything but the file and a named non-suite tool,
an install the reader does not see (options before `install`, a clustered `-qr`), or a
requirements source the line does not show (AC1); requirements-dev.txt including another file
the checker does not follow (AC1); the corpus-verify job installing a package, or a looser
floor, that requirements-dev.txt does not declare (AC2); any rule or reader branch dropped (the
self-test).
"""
# test-census-subject: .github/workflows/lint.yml
from __future__ import annotations

import re
import shlex
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
SUITE_FILE = "requirements-dev.txt"
#: Tools a ci step may install by hand: none is a suite package, and none may be declared in
#: requirements-dev.txt (a declared one comes from the file).
NON_SUITE_TOOLS = {"bandit"}
#: Environment variables pip reads as extra requirements or constraints files.
PIP_FILE_VARIABLES = {"PIP_REQUIREMENT", "PIP_CONSTRAINT"}
_LONG_FILE = {"--requirement": "requirements", "--constraint": "constraints"}
_SHORT_FILE = {"r": "requirements", "c": "constraints"}
#: `pip install` short options that take a value (the rest of the word, or the next word).
_SHORT_VALUED = {"r", "c", "e", "i", "f", "t"}
#: `pip install` long options that take a value as the next word.
_LONG_VALUED = {"--index-url", "--extra-index-url", "--find-links", "--target", "--prefix",
                "--root", "--src", "--upgrade-strategy", "--progress-bar", "--python-version",
                "--platform", "--implementation", "--abi", "--editable", "--report"}
#: pip's general options (before the subcommand) that take a value as the next word.
_GENERAL_VALUED = {"--log", "--log-file", "--proxy", "--retries", "--timeout",
                   "--exists-action", "--trusted-host", "--cert", "--client-cert", "--cache-dir",
                   "--python", "--use-feature", "--use-deprecated", "--keyring-provider",
                   "--resume-retries"}
_PIP_EXE = re.compile(r"^(?:.*/)?pip(?:\d+(?:\.\d+)*)?$")
_SEPARATOR = re.compile(r"^[;&|]+$")


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _floor(spec: str) -> tuple[int, ...] | None:
    """The lowest version a spec admits (its `>=`, `==` or `~=` version), padded to three parts
    so `7.10` and `7.10.0` compare equal."""
    m = re.search(r"(?:>=|==|~=)\s*([0-9][0-9.]*)", spec)
    if not m:
        return None
    parts = tuple(int(p) for p in m.group(1).rstrip(".").split("."))
    return parts + (0,) * max(0, 3 - len(parts))


def _name(spec: str) -> str:
    return _norm(re.split(r"[<>=!~;\[ ]", spec, maxsplit=1)[0])


def _parse(words: list[str]) -> dict[str, list[str]]:
    """Package specs, requirements files and constraints files named by `pip install` arguments."""
    out: dict[str, list[str]] = {"specs": [], "requirements": [], "constraints": []}
    i = 0
    while i < len(words):
        word = words[i]
        flag, eq, value = word.partition("=")
        if word.startswith("--"):
            if flag in _LONG_FILE:
                if not eq and i + 1 < len(words):
                    i, value = i + 1, words[i + 1]
                out[_LONG_FILE[flag]].append(value)
            elif word in _LONG_VALUED:
                i += 1
        elif word.startswith("-") and len(word) > 1:
            # A cluster of short options (`-q`, `-qr FILE`, `-qrFILE`), read as pip reads it: each
            # letter in turn, and the first that takes a value takes the rest of the word or, when
            # nothing is left, the next word.
            for k, letter in enumerate(word[1:], 1):
                if letter in _SHORT_VALUED:
                    value = word[k + 1:]
                    if not value and i + 1 < len(words):
                        i, value = i + 1, words[i + 1]
                    if letter in _SHORT_FILE:
                        out[_SHORT_FILE[letter]].append(value)
                    elif letter == "e":
                        out["specs"].append(value)
                    break
        else:
            out["specs"].append(word)
        i += 1
    return out


def _commands(line: str) -> list[list[str]]:
    """One shell line's commands, split on `;`, `&&`, `||` and `|`, comments cut."""
    lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    lexer.commenters = "#"
    out: list[list[str]] = [[]]
    for token in lexer:
        if _SEPARATOR.match(token):
            out.append([])
        else:
            out[-1].append(token)
    return [c for c in out if c]


def _install_args(argv: list[str]) -> list[str] | None:
    """The arguments after `install` when `argv` runs pip install, else None. pip's general
    options may stand between pip and `install`."""
    for i, word in enumerate(argv):
        if not _PIP_EXE.match(word):
            continue
        j = i + 1
        while j < len(argv) and argv[j].startswith("-"):
            j += 2 if argv[j] in _GENERAL_VALUED else 1
        if j < len(argv) and argv[j] == "install":
            return argv[j + 1:]
    return None


def _invocations(step: dict) -> list[dict]:
    """Each pip install in one step's `run`: its parsed arguments, and whether a `cd` ran before
    it on its line (so it installs from another directory)."""
    out = []
    for line in str(step.get("run") or "").splitlines():
        moved = False
        for argv in _commands(line):
            if argv and argv[0] in ("cd", "pushd"):
                moved = True
            args = _install_args(argv)
            if args is not None:
                out.append({"line": line.strip(), "cd": moved, **_parse(args)})
    return out


def _file_specs(rel: str, root: Path = REPO, seen: frozenset = frozenset()) -> list[str]:
    """The package specs a requirements file declares, its own `-r` lines followed."""
    if rel in seen:
        return []
    specs: list[str] = []
    for line in (root / rel).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        parsed = _parse(shlex.split(line))
        specs += parsed["specs"]
        for nested in parsed["requirements"]:
            specs += _file_specs(nested, root, seen | {rel})
    return specs


def _option_lines(text: str) -> list[str]:
    """The lines of a requirements file that are pip options rather than requirements."""
    return [line for line in (raw.split("#", 1)[0].strip() for raw in text.splitlines())
            if line.startswith("-")]


def _declared(root: Path = REPO) -> dict[str, tuple[int, ...] | None]:
    return {_name(spec): _floor(spec) for spec in _file_specs(SUITE_FILE, root)}


def _ci_violations(workflow: dict, declared: dict) -> list[str]:
    """Every way the workflow's ci job installs Python packages outside the one list."""
    job = workflow["jobs"]["ci"]
    steps = job.get("steps") or []
    out = []
    for where, env in [("the workflow", workflow.get("env")), ("the ci job", job.get("env"))] + [
            (f"ci step {n}", s.get("env")) for n, s in enumerate(steps)]:
        for key in env or {}:
            if str(key).upper() in PIP_FILE_VARIABLES:
                out.append(f"{where} sets {key}, a requirements source no install line shows")
    moved_by_default = any(((scope or {}).get("defaults") or {}).get("run", {}).get(
        "working-directory") for scope in (workflow, job))
    suite = 0
    for n, step in enumerate(steps):
        for inv in _invocations(step):
            where = f"ci step {n} ({inv['line']})"
            if moved_by_default or step.get("working-directory") or inv["cd"]:
                out.append(f"{where} installs from another directory")
            if SUITE_FILE in inv["requirements"]:
                suite += 1
                if inv["requirements"] != [SUITE_FILE]:
                    out.append(f"{where} reads a second requirements file")
                if inv["specs"]:
                    out.append(f"{where} carries a package list of its own")
                if inv["constraints"]:
                    out.append(f"{where} reads a constraints file")
                continue
            if inv["requirements"] or inv["constraints"]:
                out.append(f"{where} installs from another file")
            for spec in inv["specs"]:
                if _name(spec) not in NON_SUITE_TOOLS:
                    out.append(f"{where} installs {spec} by hand, outside the one list")
                elif _name(spec) in declared:
                    out.append(f"{where} installs {spec} by hand though the file declares it")
    if not suite:
        out.append(f"no ci step installs from {SUITE_FILE}")
    return out


class OneListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
        self.jobs = self.workflow["jobs"]

    def test_the_ci_suite_step_installs_from_requirements_dev(self) -> None:
        self.assertEqual([], _ci_violations(self.workflow, _declared()))
        # pip follows a `-r` inside the file and tools/gate_prereqs.py does not, so the one list
        # stays one file.
        self.assertEqual([], _option_lines((REPO / SUITE_FILE).read_text(encoding="utf-8")))

    def test_the_corpus_verify_job_installs_a_declared_subset(self) -> None:
        declared = _declared()
        specs = []
        for step in self.jobs["corpus-verify"]["steps"]:
            for inv in _invocations(step):
                specs += inv["specs"]
                for rel in inv["requirements"]:
                    specs += _file_specs(rel)
        self.assertTrue(specs, "corpus-verify installs no package, so this pins nothing")
        for spec in specs:
            name = _name(spec)
            with self.subTest(package=name):
                self.assertIn(name, declared, f"{name} is installed but not declared")
                if declared[name]:
                    self.assertIsNotNone(_floor(spec), f"{name} drops the declared floor")
                    self.assertGreaterEqual(_floor(spec), declared[name],
                                            f"{name}'s floor is looser than declared")

    def test_the_readers_and_rules_refuse_what_they_must(self) -> None:
        """Every reader and rule above, over synthetic lines and workflows. MUTANT: any branch
        dropped, so a spelling pip accepts or a rule the ci job must meet goes unread."""
        for command, field, value in (
                ("python -m pip install -r a.txt", "requirements", ["a.txt"]),
                ("pip install --requirement a.txt", "requirements", ["a.txt"]),
                ("pip install --requirement=a.txt", "requirements", ["a.txt"]),
                ("pip install -ra.txt", "requirements", ["a.txt"]),
                ("pip install -qra.txt", "requirements", ["a.txt"]),
                ("pip install -qr a.txt", "requirements", ["a.txt"]),
                ("pip install -r requirements-dev.txt -r b.txt", "requirements",
                 ["requirements-dev.txt", "b.txt"]),
                ("pip install -c a.txt x", "constraints", ["a.txt"]),
                ("pip install --constraint=a.txt x", "constraints", ["a.txt"]),
                ("pip install -qc a.txt x", "constraints", ["a.txt"]),
                ("pip install -i https://example.test/simple pytest 'coverage>=7.10'", "specs",
                 ["pytest", "coverage>=7.10"]),
                ("pip install --quiet --upgrade bandit", "specs", ["bandit"])):
            with self.subTest(command=command):
                [inv] = _invocations({"run": command})
                self.assertEqual(value, inv[field])
        for line in ("pip install x", "pip3 install x", "pip3.12 install x", "uv pip install x",
                     "/usr/bin/pip install x", "python3 -m pip install x", "pip -q install x",
                     "python -m pip --disable-pip-version-check install x",
                     "python -m pip --log /tmp/pip.log install x", "echo hi && pip install x"):
            with self.subTest(line=line):
                self.assertEqual(1, len(_invocations({"run": line})), line)
        for line in ("# pip install x", "pipx install x", "pip download x", "pip -q show x"):
            with self.subTest(not_an_install=line):
                self.assertEqual([], _invocations({"run": line}), line)

        def ci(*runs: str, **extra) -> dict:
            steps = [{"run": r} for r in runs]
            for n, keys in extra.pop("step", {}).items():
                steps[n].update(keys)
            return {"jobs": {"ci": {"steps": steps, **extra.pop("job", {})}}, **extra}

        suite, tool = "python -m pip install --quiet -r requirements-dev.txt", "pip install bandit"
        declared = {"pytest": None, "coverage": (7, 10, 0)}
        self.assertEqual([], _ci_violations(ci(suite, tool), declared))
        for name, workflow in (
                ("no suite step", ci(tool)),
                ("a second file", ci(suite + " -r tools/ci-extra.txt")),
                ("a second file, attached", ci(suite + " -rtools/ci-extra.txt")),
                ("a second file, long with =", ci(suite + " --requirement=tools/ci-extra.txt")),
                ("a second file, clustered", ci(suite + " -qrtools/ci-extra.txt")),
                ("a list of its own", ci(suite + " pytest-timeout")),
                ("a constraints file", ci(suite + " -c requirements-dev.txt")),
                ("another file in another step", ci(suite, "pip install -r tools/ci-extra.txt")),
                ("a package by hand", ci(suite, "pip install hypothesis")),
                ("options before install", ci(suite, "pip -q install hypothesis")),
                ("general options before install",
                 ci(suite, "python -m pip --disable-pip-version-check install hypothesis")),
                ("a declared package by hand", ci(suite, "pip install pytest")),
                ("a step variable", ci(suite, step={0: {"env": {"PIP_REQUIREMENT": "x.txt"}}})),
                ("a job variable", ci(suite, job={"env": {"PIP_CONSTRAINT": "x.txt"}})),
                ("a workflow variable", ci(suite, env={"PIP_REQUIREMENT": "x.txt"})),
                ("a step directory", ci(suite, step={0: {"working-directory": "tools"}})),
                ("a job default directory",
                 ci(suite, job={"defaults": {"run": {"working-directory": "tools"}}})),
                ("a cd on the line", ci("cd tools && " + suite))):
            with self.subTest(rule=name):
                self.assertTrue(_ci_violations(workflow, declared), name)
        self.assertTrue(_ci_violations(ci(suite, tool), {**declared, "bandit": None}),
                        "a declared tool installed by hand")
        self.assertEqual(["-r x.txt", "--constraint=z.txt"],
                         _option_lines("pytest\n-r x.txt  # nested\n# -r y.txt\n--constraint=z.txt\n"))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.txt").write_text("pytest\n-r b.txt\n# x\n", encoding="utf-8")
            (root / "b.txt").write_text("--requirement=c.txt\ncoverage>=7.10,<8\n",
                                        encoding="utf-8")
            (root / "c.txt").write_text("pytest-timeout\n-r a.txt\n", encoding="utf-8")
            self.assertEqual(["pytest", "pytest-timeout", "coverage>=7.10,<8"],
                             _file_specs("a.txt", root))
        self.assertEqual((7, 10, 0), _floor("coverage==7.10"))
        self.assertEqual(_floor("coverage==7.10.0"), _floor("coverage>=7.10,<8"))
        self.assertEqual((7, 10, 0), _floor("coverage~=7.10"))
        self.assertIsNone(_floor("coverage<8"))


if __name__ == "__main__":
    unittest.main()
