"""US1004: CI and the prerequisite checker read one list of the suite's Python packages.

`tools/gate_prereqs.py` checks a clone against `requirements-dev.txt`; CI's suite step installed
its own inline list, so the two could drift and a clone could pass the checker yet miss what CI
runs with. The ci job now installs from the file. The scheduled corpus-verify job keeps its own
list on purpose (moving it would add pytest-xdist to a lane compared against a recorded
baseline), so it is held to a declared subset instead.

Every `pip install` line is read the way pip reads it (BG1053): a requirements or constraints
file in every spelling pip accepts (`-r F`, `-rF`, `--requirement F`, `--requirement=F`, and the
same for `-c`), by any pip (`pip`, `pip3`, `pip3.12`), with a file's own `-r` lines followed.

MUTANTS: the inline package list left in the ci job's suite step (AC1); a second requirements
file on the suite step, in any spelling, or a ci step installing anything but the file and a
named non-suite tool (AC1); requirements-dev.txt including another file the checker does not
follow (AC1); the corpus-verify job installing a package, or a looser floor, that
requirements-dev.txt does not declare, by any spelling or nesting (AC2); the reader dropping a
spelling (the reader self-test).
"""
# test-census-subject: .github/workflows/lint.yml
from __future__ import annotations

import re
import shlex
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
#: Tools a ci step may install by hand: none is a suite package, and none may be declared in
#: requirements-dev.txt (a declared one comes from the file).
NON_SUITE_TOOLS = {"bandit"}
_FILE_FLAGS = {"-r": "requirements", "--requirement": "requirements",
               "-c": "constraints", "--constraint": "constraints"}
#: pip install options that take a value as the next word, which is therefore not a package.
_VALUED = {"-i", "--index-url", "--extra-index-url", "-f", "--find-links", "-t", "--target",
           "--prefix", "--root", "--src", "--upgrade-strategy", "--progress-bar", "--log",
           "--cache-dir", "--python-version", "--platform", "--implementation", "--abi"}
_PIP = re.compile(r"\bpip(?:\d+(?:\.\d+)*)?\s+install\b")


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _floor(spec: str) -> tuple[int, ...] | None:
    """The lowest version a spec admits: its `>=`, `==` or `~=` version."""
    m = re.search(r"(?:>=|==|~=)\s*([0-9][0-9.]*)", spec)
    return tuple(int(p) for p in m.group(1).rstrip(".").split(".")) if m else None


def _name(spec: str) -> str:
    return _norm(re.split(r"[<>=!~;\[ ]", spec, maxsplit=1)[0])


def _parse(words: list[str]) -> dict[str, list[str]]:
    """Package specs, requirements files and constraints files named by pip arguments."""
    out: dict[str, list[str]] = {"specs": [], "requirements": [], "constraints": []}
    i = 0
    while i < len(words):
        word = words[i]
        if word in _FILE_FLAGS:
            if i + 1 < len(words):
                out[_FILE_FLAGS[word]].append(words[i + 1])
            i += 2
            continue
        flag, eq, value = word.partition("=")
        if eq and flag in _FILE_FLAGS:
            out[_FILE_FLAGS[flag]].append(value)
        elif word[:2] in ("-r", "-c") and len(word) > 2 and not word.startswith("--"):
            out[_FILE_FLAGS[word[:2]]].append(word[2:])
        elif word in _VALUED:
            i += 1
        elif not word.startswith("-"):
            out["specs"].append(word)
        i += 1
    return out


def _install(command: str) -> dict[str, list[str]]:
    """What one `pip install` command line names (`_parse`), flags read the way pip reads them."""
    words = shlex.split(command)
    return _parse(words[words.index("install") + 1:])


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


def _pip_installs(step: dict) -> list[str]:
    """Each `pip install` command line in one step, by any pip, comments cut."""
    return [line.split("#", 1)[0].strip()
            for line in str(step.get("run") or "").splitlines()
            if _PIP.search(line.split("#", 1)[0])]


def _declared() -> dict[str, tuple[int, ...] | None]:
    return {_name(spec): _floor(spec) for spec in _file_specs("requirements-dev.txt")}


class OneListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]

    def test_the_ci_suite_step_installs_from_requirements_dev(self) -> None:
        commands = [c for s in self.jobs["ci"]["steps"] for c in _pip_installs(s)]
        suite = [c for c in commands if "requirements-dev.txt" in _install(c)["requirements"]]
        self.assertTrue(suite, "no ci step installs from requirements-dev.txt")
        for command in suite:
            parsed = _install(command)
            with self.subTest(command=command):
                self.assertEqual(["requirements-dev.txt"], parsed["requirements"],
                                 "the suite step reads a second requirements file")
                self.assertEqual([], parsed["specs"],
                                 "the suite step still carries a package list of its own")
                self.assertEqual([], parsed["constraints"])
        declared = _declared()
        for command in commands:
            parsed = _install(command)
            with self.subTest(command=command):
                self.assertTrue(set(parsed["requirements"]) <= {"requirements-dev.txt"},
                                f"a ci step installs from another file: {parsed['requirements']}")
                for spec in parsed["specs"]:
                    self.assertIn(_name(spec), NON_SUITE_TOOLS,
                                  f"a ci step installs {spec} by hand, outside the one list")
                    self.assertNotIn(_name(spec), declared,
                                     f"{spec} is declared in requirements-dev.txt but installed "
                                     f"by hand")
        # pip follows a `-r` inside the file and tools/gate_prereqs.py does not, so the one list
        # stays one file.
        for line in (REPO / "requirements-dev.txt").read_text(encoding="utf-8").splitlines():
            line = line.split("#", 1)[0].strip()
            with self.subTest(line=line):
                self.assertFalse(line.startswith("-"), f"requirements-dev.txt carries {line!r}, "
                                 f"which the checker does not read")

    def test_the_corpus_verify_job_installs_a_declared_subset(self) -> None:
        declared = _declared()
        specs = []
        for step in self.jobs["corpus-verify"]["steps"]:
            for command in _pip_installs(step):
                parsed = _install(command)
                specs += parsed["specs"]
                for rel in parsed["requirements"]:
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

    def test_the_reader_reads_every_spelling(self) -> None:
        """The readers the two tests lean on, over synthetic lines. MUTANT: a spelling pip
        accepts (`-rF`, `--requirement=F`, `-c`, `pip3.12`, a nested `-r`) read as a flag."""
        for command, field, value in (
                ("python -m pip install -r a.txt", "requirements", ["a.txt"]),
                ("pip install --requirement a.txt", "requirements", ["a.txt"]),
                ("pip install --requirement=a.txt", "requirements", ["a.txt"]),
                ("pip install -ra.txt", "requirements", ["a.txt"]),
                ("pip install -r requirements-dev.txt -r b.txt", "requirements",
                 ["requirements-dev.txt", "b.txt"]),
                ("pip install -c a.txt x", "constraints", ["a.txt"]),
                ("pip install --constraint=a.txt x", "constraints", ["a.txt"]),
                ("pip install -i https://example.test/simple pytest 'coverage>=7.10'", "specs",
                 ["pytest", "coverage>=7.10"]),
                ("pip install --quiet --upgrade bandit", "specs", ["bandit"])):
            with self.subTest(command=command):
                self.assertEqual(value, _install(command)[field])
        for line in ("pip install x", "pip3 install x", "pip3.12 install x",
                     "uv pip install x", "python3 -m pip install x"):
            with self.subTest(line=line):
                self.assertEqual([line], _pip_installs({"run": f"echo hi\n{line}"}))
        self.assertEqual([], _pip_installs({"run": "# pip install x\npipx run thing"}))
        import tempfile  # noqa: PLC0415 - only the nested-file case needs one
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "a.txt").write_text("pytest\n-r b.txt\n# x\n", encoding="utf-8")
            (root / "b.txt").write_text("--requirement=c.txt\ncoverage>=7.10,<8\n",
                                        encoding="utf-8")
            (root / "c.txt").write_text("pytest-timeout\n-r a.txt\n", encoding="utf-8")
            self.assertEqual(["pytest", "pytest-timeout", "coverage>=7.10,<8"],
                             _file_specs("a.txt", root))
        self.assertEqual((7, 10), _floor("coverage==7.10"))
        self.assertEqual((7, 10), _floor("coverage>=7.10,<8"))
        self.assertIsNone(_floor("coverage<8"))


if __name__ == "__main__":
    unittest.main()
