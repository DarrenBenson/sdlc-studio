"""US1004: CI and the prerequisite checker read one list of the suite's Python packages.

`tools/gate_prereqs.py` checks a clone against `requirements-dev.txt`; CI's suite step installed
its own inline list, so the two could drift and a clone could pass the checker yet miss what CI
runs with. The ci job now installs from the file. The scheduled corpus-verify job keeps its own
list on purpose (moving it would add pytest-xdist to a lane compared against a recorded
baseline), so it is held to a declared subset instead.

A closed world, not a parser (BG1056). Reading every spelling pip accepts failed four review
rounds running, each finding one more, so the two jobs are held to exact forms instead:

- every command that names pip is `python -m pip install`, `python3 -m pip install`,
  `pip install` or `pip3 install`, followed only by the flags in `ALLOWED_FLAGS` and, in the ci
  job, either `-r requirements-dev.txt` alone or the names in `NON_SUITE_TOOLS`; in
  corpus-verify, plain requirement specs;
- any other command that names pip (`pip -q install`, `uv pip`, `ensurepip`, `pipx`), another
  installer (`uv`, `poetry`, `pdm`, `conda`, `mamba`), a `PIP_` setting anywhere in a run block
  or an `env:`, and a change of directory in a step that installs (`cd`, `pushd`,
  `working-directory`, a default one) is refused.

A wrapper script that installs packages is not read: it names no pip on the job's own lines.

MUTANTS: the inline package list left in the ci job's suite step (AC1); anything on a pip line
beyond the exact forms, a pip command in another form, another installer, a `PIP_` setting or a
directory change (AC1); requirements-dev.txt including another file the checker does not follow
(AC1); the corpus-verify job installing a package, or a looser floor, that requirements-dev.txt
does not declare (AC2); any rule dropped (the self-test).
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
SUITE_FILE = "requirements-dev.txt"
#: Tools a ci step may install by hand: none is a suite package, and none may be declared in
#: requirements-dev.txt (a declared one comes from the file).
NON_SUITE_TOOLS = {"bandit"}
#: The only ways a job may run pip install.
PIP_FORMS = (("python", "-m", "pip", "install"), ("python3", "-m", "pip", "install"),
             ("pip", "install"), ("pip3", "install"))
#: The only options a pip install line may carry beside what it installs. None takes a value.
ALLOWED_FLAGS = {"--quiet", "-q", "--upgrade", "-U", "--disable-pip-version-check",
                 "--no-cache-dir"}
#: Installers other than pip: none may run in either job.
OTHER_INSTALLERS = {"uv", "uvx", "poetry", "pdm", "conda", "mamba", "micromamba", "pipx",
                    "easy_install", "pipenv", "hatch", "rye"}
_SEPARATOR = re.compile(r"^[;&|]+$")
#: A command naming pip in any case. A `PIP_` setting on a line names it too, so that line is
#: refused as a pip command outside the exact forms.
_NAMES_PIP = re.compile(r"pip", re.I)
_SPEC = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*(\[[A-Za-z0-9,._-]+\])?\s*([<>=!~]=?[^\s;]+"
                   r"(\s*,\s*[<>=!~]=?[^\s,;]+)*)?$")


def _norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _name(spec: str) -> str:
    return _norm(re.split(r"[<>=!~;\[ ]", spec, maxsplit=1)[0])


def _floor(spec: str) -> tuple[int, ...] | None:
    """The lowest version a spec admits (its `>=`, `==` or `~=` version), padded to three parts
    so `7.10` and `7.10.0` compare equal."""
    m = re.search(r"(?:>=|==|~=)\s*([0-9][0-9.]*)", spec)
    if not m:
        return None
    parts = tuple(int(p) for p in m.group(1).rstrip(".").split("."))
    return parts + (0,) * max(0, 3 - len(parts))


def _commands(text: str) -> list[list[str]]:
    """A run block's commands, split on newlines, `;`, `&&`, `||` and `|`, comments cut."""
    out: list[list[str]] = []
    for line in text.splitlines():
        lexer = shlex.shlex(line, posix=True, punctuation_chars=";&|")
        lexer.whitespace_split = True
        lexer.commenters = "#"
        current: list[str] = []
        for token in lexer:
            if _SEPARATOR.match(token):
                out.append(current)
                current = []
            else:
                current.append(token)
        out.append(current)
    return [c for c in out if c]


def _install_args(argv: list[str]) -> list[str] | None:
    """What an allowed pip form installs (its arguments, flags removed), or None when `argv` is
    not exactly an allowed form: a pip command in any other shape, or one carrying an option
    outside ALLOWED_FLAGS."""
    for form in PIP_FORMS:
        if tuple(argv[:len(form)]) != form:
            continue
        rest, args, i = argv[len(form):], [], 0
        while i < len(rest):
            word = rest[i]
            if word == "-r" and i + 1 < len(rest) and not rest[i + 1].startswith("-"):
                args += [word, rest[i + 1]]     # the one value-taking option: judged by `allow`
                i += 2
                continue
            if word.startswith("-") and word not in ALLOWED_FLAGS:
                return None
            if word not in ALLOWED_FLAGS:
                args.append(word)
            i += 1
        return args
    return None


def _job_violations(workflow: dict, job_name: str, allow) -> list[str]:
    """Every way `job_name` runs pip outside the exact forms, or sets pip up outside its lines.
    `allow(args)` returns why an allowed form's arguments are not acceptable, or None."""
    job = workflow["jobs"][job_name]
    steps = job.get("steps") or []
    out = []
    for where, env in [("the workflow", workflow.get("env")), (f"the {job_name} job",
                                                               job.get("env"))] + [
            (f"{job_name} step {n}", s.get("env")) for n, s in enumerate(steps)]:
        for key in env or {}:
            if str(key).upper().startswith("PIP_"):
                out.append(f"{where} sets {key}")
    defaults = [((scope or {}).get("defaults") or {}).get("run", {}).get("working-directory")
                for scope in (workflow, job)]
    installs = 0
    for n, step in enumerate(steps):
        commands = _commands(str(step.get("run") or ""))
        names_pip = any(_NAMES_PIP.search(w) for c in commands for w in c)
        where = f"{job_name} step {n}"
        if names_pip and (step.get("working-directory") or any(defaults)
                          or any(c[0] in ("cd", "pushd", "popd") for c in commands)):
            out.append(f"{where} installs after changing directory")
        for argv in commands:
            line = " ".join(argv)
            if argv[0] in OTHER_INSTALLERS:
                out.append(f"{where} runs another installer: {line}")
            if not any(_NAMES_PIP.search(w) for w in argv):
                continue
            args = _install_args(argv)
            if args is None:
                out.append(f"{where} runs pip outside the exact forms: {line}")
                continue
            installs += 1
            if (why := allow(args)):
                out.append(f"{where}: {why}: {line}")
    if not installs:
        out.append(f"the {job_name} job runs no pip install in an exact form")
    return out


def _ci_allow(declared: dict):
    def allow(args: list[str]) -> str | None:
        if args == ["-r", SUITE_FILE]:
            return None
        if not args or any(not _SPEC.match(a) or _name(a) not in NON_SUITE_TOOLS for a in args):
            return f"installs neither `-r {SUITE_FILE}` alone nor named non-suite tools"
        hand = [a for a in args if _name(a) in declared]
        return f"installs {hand} by hand though the file declares them" if hand else None
    return allow


def _corpus_allow(declared: dict):
    def allow(args: list[str]) -> str | None:
        if not args:
            return "installs nothing"
        for spec in args:
            if not _SPEC.match(spec):
                return f"{spec!r} is not a plain requirement"
            name = _name(spec)
            if name not in declared:
                return f"{name} is installed but not declared"
            if declared[name] and (_floor(spec) is None or _floor(spec) < declared[name]):
                return f"{name}'s floor is dropped or looser than declared"
        return None
    return allow


def _requirements(text: str) -> tuple[dict[str, tuple[int, ...] | None], list[str]]:
    """A requirements file's declared `{name: floor}` and its option lines (a `-r`, `-c` or
    other pip option the checker does not read)."""
    declared, options = {}, []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if line.startswith("-"):
            options.append(line)
        elif line:
            declared[_name(line)] = _floor(line)
    return declared, options


def _declared() -> dict[str, tuple[int, ...] | None]:
    return _requirements((REPO / SUITE_FILE).read_text(encoding="utf-8"))[0]


class OneListTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    def test_the_ci_suite_step_installs_from_requirements_dev(self) -> None:
        declared, options = _requirements((REPO / SUITE_FILE).read_text(encoding="utf-8"))
        self.assertEqual([], _job_violations(self.workflow, "ci", _ci_allow(declared)))
        suite = [a for s in self.workflow["jobs"]["ci"]["steps"]
                 for c in _commands(str(s.get("run") or "")) if (a := _install_args(c))]
        self.assertIn(["-r", SUITE_FILE], suite, f"no ci step installs from {SUITE_FILE}")
        # pip follows a `-r` inside the file and tools/gate_prereqs.py does not, so the one list
        # stays one file.
        self.assertEqual([], options)

    def test_the_corpus_verify_job_installs_a_declared_subset(self) -> None:
        self.assertEqual([], _job_violations(self.workflow, "corpus-verify",
                                             _corpus_allow(_declared())))

    def test_the_readers_and_rules_refuse_what_they_must(self) -> None:
        """Every rule above, over synthetic workflows. MUTANT: any rule dropped, so a line
        outside the exact forms, or a setting beside them, passes."""
        declared = {"pytest": None, "coverage": (7, 10, 0)}
        suite, tool = "python -m pip install --quiet -r requirements-dev.txt", "pip install bandit"

        def ci(*runs: str, step: dict | None = None, job: dict | None = None, **workflow) -> list:
            steps = [{"run": r} for r in runs]
            for n, keys in (step or {}).items():
                steps[n].update(keys)
            return _job_violations({"jobs": {"ci": {"steps": steps, **(job or {})}}, **workflow},
                                   "ci", _ci_allow(declared))

        self.assertEqual([], ci(suite, tool))
        self.assertEqual([], ci("pip3 install -U -q -r requirements-dev.txt",
                                "python3 -m pip install --quiet bandit"))
        self.assertEqual([], ci("echo start && " + suite + "; echo done", tool),
                         "a chained command was not split from the install")
        for name, violations in (
                ("no install", ci("echo hi")),
                ("a second file", ci(suite + " -r tools/ci-extra.txt")),
                ("an attached file", ci(suite + " -rtools/ci-extra.txt")),
                ("a clustered file", ci(suite + " -qrtools/ci-extra.txt")),
                ("an abbreviated long option", ci(suite + " --requir=tools/ci-extra.txt")),
                ("requirements from a script",
                 ci(suite + " --requirements-from-script=tools/deps.py")),
                ("an editable", ci(suite + " -e tools/extra-pkg")),
                ("an editable, long", ci(suite + " --editable tools/extra-pkg")),
                ("an editable, long with =", ci(suite + " --editable=tools/extra-pkg")),
                ("a list of its own", ci(suite + " pytest-timeout")),
                ("a constraints file", ci(suite + " -c requirements-dev.txt")),
                ("a constraints file only", ci("pip install -c requirements-dev.txt")),
                ("an index", ci(suite + " -i https://example.test/simple")),
                ("another file in another step", ci(suite, "pip install -r tools/ci-extra.txt")),
                ("a package by hand", ci(suite, "pip install hypothesis")),
                ("a declared package by hand", ci(suite, "pip install pytest bandit")),
                ("a tool with a URL", ci(suite, "pip install bandit@https://example.test/b.whl")),
                ("options before install", ci(suite, "pip -q install hypothesis")),
                ("a general option before install",
                 ci(suite, "python -m pip --local-log /tmp/x.log install hypothesis")),
                ("uv pip", ci(suite, "uv pip install hypothesis")),
                ("another installer", ci(suite, "poetry install")),
                ("ensurepip", ci(suite, "python -m ensurepip")),
                ("a pip path", ci(suite, "/usr/bin/pip install hypothesis")),
                ("a variable before the command",
                 ci("PIP_REQUIREMENT=tools/ci-extra.txt " + suite)),
                ("an exported variable on an earlier line",
                 ci("export PIP_REQUIREMENT=tools/ci-extra.txt\n" + suite)),
                ("a step variable", ci(suite, step={0: {"env": {"PIP_INDEX_URL": "x"}}})),
                ("a job variable", ci(suite, job={"env": {"PIP_CONSTRAINT": "x.txt"}})),
                ("a workflow variable", ci(suite, env={"PIP_REQUIREMENT": "x.txt"})),
                ("a cd on the line", ci("cd tools && " + suite)),
                ("a cd on an earlier line", ci("cd tools\n" + suite)),
                ("a step directory", ci(suite, step={0: {"working-directory": "tools"}})),
                ("a job default directory",
                 ci(suite, job={"defaults": {"run": {"working-directory": "tools"}}}))):
            with self.subTest(rule=name):
                self.assertTrue(violations, name)
        # The rule that must say NO for each, not merely some rule: the rules overlap, and a
        # dropped one would otherwise hide behind the next.
        for name, violations, says in (
                ("options before install", ci(suite, "pip -q install hypothesis"),
                 "outside the exact forms"),
                ("a value-taking option", ci(suite + " -i https://example.test/simple"),
                 "outside the exact forms"),
                ("an editable", ci(suite + " --editable tools/extra-pkg"),
                 "outside the exact forms"),
                ("a variable", ci("export PIP_REQUIREMENT=x.txt\n" + suite),
                 "outside the exact forms"),
                ("a second file", ci(suite + " -r tools/ci-extra.txt"), "neither"),
                ("a declared tool by hand",
                 _job_violations({"jobs": {"ci": {"steps": [{"run": suite}, {"run": tool}]}}},
                                 "ci", _ci_allow({**declared, "bandit": None})),
                 "by hand though the file declares")):
            with self.subTest(says=name):
                self.assertTrue(any(says in v for v in violations), violations)

        def corpus(run: str) -> list:
            return _job_violations({"jobs": {"corpus-verify": {"steps": [{"run": run}]}}},
                                   "corpus-verify", _corpus_allow(declared))

        self.assertEqual([], corpus("python -m pip install --quiet pytest 'coverage>=7.10'"))
        self.assertEqual([], corpus("pip install 'coverage==7.10.0' 'coverage>=7.10,<8'"))
        for name, run in (("an undeclared package", "pip install pytest hypothesis"),
                          ("a looser floor", "pip install 'coverage>=7.9'"),
                          ("a dropped floor", "pip install coverage"),
                          ("a requirements file", "pip install pytest -r tools/corpus-reqs.txt"),
                          ("an editable", "pip install pytest --editable=tools/extra-pkg"),
                          ("options before install", "python -m pip --quiet install hypothesis"),
                          ("a URL requirement", "pip install 'pytest @ https://example.test/p.whl'"),
                          ("an empty install", "pip install --quiet")):
            with self.subTest(corpus=name):
                self.assertTrue(corpus(run), name)
        declared_here, options = _requirements(
            "pytest\ncoverage>=7.10,<8  # floor\n-r x.txt\n# -r y.txt\n--constraint=z.txt\n")
        self.assertEqual({"pytest": None, "coverage": (7, 10, 0)}, declared_here)
        self.assertEqual(["-r x.txt", "--constraint=z.txt"], options)
        self.assertEqual(_floor("coverage==7.10.0"), _floor("coverage>=7.10,<8"))
        self.assertEqual((7, 10, 0), _floor("coverage~=7.10"))
        self.assertIsNone(_floor("coverage<8"))


if __name__ == "__main__":
    unittest.main()
