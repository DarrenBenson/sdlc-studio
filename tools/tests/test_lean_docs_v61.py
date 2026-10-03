"""US0984: the upgrade page, the README, the specifications and the help describe the 6.1 code.

Each test reads what the code does rather than a hand list: the config keys a 6.0 project loses
come from a real `migrate.py` run on a 6.0-shaped fixture, the gate lanes from `gate.py`'s own
registry (the `valid:` list an unknown `--only` prints), the retired surface from the repo's
`retired_surface` helper, and each 6.1 command is run, or its parser asked, as the help names it.
"""
# test-census-subject: docs/existing-users.md
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
PAGE = REPO / "docs" / "existing-users.md"
README = REPO / "README.md"
SPECS = {name: REPO / "sdlc-studio" / f"{name}.md" for name in ("prd", "trd", "tsd")}

sys.path.insert(0, str(SCRIPTS / "tests"))
import retired_surface  # noqa: E402

#: The 6.1 retirements the specs are held to beside the helper's list, label -> pattern.
RETIRED_61 = {
    "handoff.py generate": r"\bhandoff(?:\.py)?\s+generate\b",
    "--type handoff": r"--type[ =]handoff\b",
    "--require-handoff": r"(?<![\w-])--require-handoff\b",
    "carry_forward": r"\bcarry_forward\b",
    "run_state.batches": r"\brun_state\.batches\b",
}
#: The three retired handoff names, as the repo helper labels them.
HANDOFF_LABELS = ("handoff.py generate", "artifact.py new --type handoff", "gate.py --require-handoff")
#: A runbook running the three retired handoff commands, in prose code spans and in a fence.
_HANDOFF_RUNBOOK = ("# Ops\n"
                    "\n"
                    "At the close run `handoff.py generate --title \"S3\"`.\n"
                    "\n"
                    "```bash\n"
                    "python3 scripts/artifact.py new --type handoff --title S3\n"
                    "python3 scripts/gate.py --release --require-handoff HO0003\n"
                    "```\n")
#: A history section: what the specs record of the past is not a description of the code.
_HISTORY = re.compile(r"(?m)^## (?:Revision History|Changelog)\b")


def _env() -> dict:
    """The caller's environment minus every git locating variable, so a hook's GIT_DIR cannot
    steer a fixture at the outer repository."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _py(script: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                          capture_output=True, text=True, check=False, timeout=600, env=_env())


def _sections(text: str, level: str = "##") -> list[tuple[str, str]]:
    """(heading, body) for each heading of exactly `level`, in order."""
    parts = re.split(rf"(?m)^({level} (?!#).*)$", text)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]


def _anchor(heading: str) -> str:
    """GitHub's anchor for a markdown heading."""
    text = re.sub(r"^#+\s*", "", heading).strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def _blocks(text: str) -> list[str]:
    """Each paragraph, list item and table row of `text`, as one string apiece."""
    out: list[str] = []
    for para in re.split(r"\n\s*\n", text):
        lines = para.splitlines()
        if lines and all(ln.startswith("|") for ln in lines):
            out += lines
        else:
            out += re.split(r"\n(?=\s*(?:\d+\.|[-*])\s)", para)
    return out


def _current(path: Path) -> str:
    """A spec read outside its history section."""
    text = path.read_text(encoding="utf-8")
    cut = _HISTORY.search(text)
    return text[:cut.start()] if cut else text


def _init(base: Path) -> Path:
    root = base / "p"
    root.mkdir()
    proc = _py("init.py", "run", "--root", str(root))
    if proc.returncode != 0:
        raise AssertionError(proc.stdout + proc.stderr)
    return root


def _registered_lanes(root: Path) -> set[str]:
    """Every lane `gate.py` registers at the release boundary with the close lanes bound: the
    `valid:` list its own refusal of an unknown `--only` prints."""
    proc = _py("gate.py", "--root", str(root), "--release", "--boundary", "release",
               "--require-retro", "RETRO0001", "--require-review", "--only", "no-such-lane",
               "--format", "json")
    detail = json.loads(proc.stdout)["checks"][0]["detail"]
    return {name.strip() for name in detail.split("valid:", 1)[1].split(",")}


def _code_strings(path: Path) -> set[str]:
    """The string constants a Python file's code holds, docstrings excluded."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    docs = {id(node.body[0].value) for node in ast.walk(tree)
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Constant)}
    return {node.value for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
            and id(node) not in docs}


def _local_readers() -> str:
    """What the shipped scripts and the tools/ scripts hold as code: every non-docstring string
    constant of each `.py` (tests excluded) and every non-comment line of each tools/ shell."""
    out: list[str] = []
    for py in [*SCRIPTS.glob("*.py"), *(SCRIPTS / "lib").glob("*.py"), *(REPO / "tools").glob("*.py")]:
        out += _code_strings(py)
    for sh in (REPO / "tools").glob("*.sh"):
        out += [ln for ln in sh.read_text(encoding="utf-8").splitlines()
                if not ln.lstrip().startswith("#")]
    return "\n".join(out)


def _local_table_files(text: str) -> set[str]:
    """The bare file names a `.local` state table lists (a section whose heading names `.local`)
    on each row whose writer cell names a script: the TRD's table lists `run-state.json`, not
    `.local/run-state.json`. A row whose writer is an agent workflow claims no script writes it."""
    parts = re.split(r"(?m)^(#+ .*)$", text)
    out: set[str] = set()
    for i in range(1, len(parts), 2):
        if ".local" not in parts[i]:
            continue
        for row in parts[i + 1].splitlines():
            cells = row.split("|")
            first = re.fullmatch(r"\s*`([\w.-]+\.\w+)`\s*", cells[1]) if len(cells) > 3 else None
            if first and re.search(r"`[\w/]+\.(?:py|sh)`", cells[2]):
                out.add(first.group(1))
    return out


def _item_labels(item: dict) -> list[str]:
    """The surface labels one migrate report item names, as a list."""
    surface = item.get("surface")
    return list(surface) if isinstance(surface, list) else [surface]


class Docs61Tests(unittest.TestCase):

    def test_the_upgrade_page_takes_a_60_project_to_61(self) -> None:
        """AC1. MUTANTS: HEAD's page, which addresses only a v5 or older project (no 6.0-to-6.1
        subsection); a subsection naming the handoff retirements with no replacement; one that
        never names a key `migrate` removes from a 6.0 project; one with `migrate --apply`
        before `migrate`; a README whose upgrade answer does not point a 6.0 user at it."""
        sections = _sections(PAGE.read_text(encoding="utf-8"))
        heading, body = sections[0]
        self.assertRegex(heading, r"^## Upgrading to v6\b")
        subs = [(h, b) for h, b in _sections(body, "###")
                if re.search(r"\b6\.0\b", h) and re.search(r"\b6\.1\b", h)]
        self.assertEqual(1, len(subs), "no one subsection of 'Upgrading to v6' takes 6.0 to 6.1")
        sub_heading, sub = subs[0]

        self.assertRegex(sub, r"(?i)\breinstall", "the subsection never says to reinstall")
        dry, apply = sub.find("`migrate`"), sub.find("`migrate --apply`")
        self.assertGreaterEqual(dry, 0, "no `migrate` dry run in the subsection")
        self.assertGreater(apply, dry, "`migrate --apply` is not given after `migrate`")

        with tempfile.TemporaryDirectory() as d:
            root = _init(Path(d))
            config = root / "sdlc-studio" / ".config.yaml"
            config.write_text(config.read_text(encoding="utf-8")
                              + "\nreview:\n  policy: carry-forward\n", encoding="utf-8")
            (root / "docs").mkdir()
            for doc in ("AGENTS.md", "CLAUDE.md", "docs/ops.md"):
                (root / doc).write_text(_HANDOFF_RUNBOOK, encoding="utf-8")
            proc = _py("migrate.py", "--root", str(root), "--format", "json")
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        report = json.loads(proc.stdout)
        keys = sorted({item["key"] for item in report["deterministic"]
                       if item.get("kind") == "retired-config-key"})
        self.assertIn("review.policy", keys, "the 6.0 fixture's key was not reported removed")
        for key in keys:
            self.assertIn(f"`{key}`", sub, f"`migrate` removes {key} and the subsection never names it")

        blocks = _blocks(sub)
        for name in HANDOFF_LABELS:
            with self.subTest(retired=name):
                beside = [b for b in blocks if f"`{name}`" in b
                          or name == "handoff.py generate" and "`handoff.py generate`" in b]
                self.assertTrue(beside, f"the subsection never names `{name}`")
                self.assertTrue(any("signed" in b and ("`sprint.py plan --worklist RPTxxxx`" in b
                                                       or "`sprint.py sign`" in b) for b in beside),
                                f"`{name}` is named with no replacement beside it")
        # What the runs name, by file, against what the page says they name: every handoff
        # command in the project's other markdown, and in the root instruction files only the
        # retired verbs (`handoff.py generate`), never the flags.
        named_in: dict[str, set[str]] = {}
        for item in report["needs_human"]:
            if item.get("kind") == "retired-surface":
                named_in.setdefault(item["file"], set()).update(_item_labels(item))
        self.assertEqual(set(HANDOFF_LABELS), named_in.get("docs/ops.md", set()),
                         "migrate does not name every handoff command in docs/ops.md")
        roots = [named_in.get(f, set()) & set(HANDOFF_LABELS) for f in ("AGENTS.md", "CLAUDE.md")]
        self.assertEqual(roots[0], roots[1], "migrate reads AGENTS.md and CLAUDE.md differently")
        said = re.search(r"[^.]*`AGENTS\.md`(?:[^.]|\.(?=[\w`]))*", " ".join(sub.split()))
        self.assertTrue(said, "the subsection never says what migrate reads in AGENTS.md")
        yes, _, no = said.group(0).partition(" but not ")
        self.assertEqual(roots[0], {n for n in HANDOFF_LABELS if f"`{n}`" in yes},
                         "the page says the root files name a command migrate does not name there")
        self.assertEqual(set(HANDOFF_LABELS) - roots[0],
                         {n for n in HANDOFF_LABELS if f"`{n}`" in no},
                         "the page does not say which commands the root files are not read for")

        self.assertRegex(sub, r"(?is)\bHO\b[^.]*\bstay readable\b",
                         "the subsection never says the HO files already written stay readable")

        readme = README.read_text(encoding="utf-8")
        answer = re.search(r"(?s)<summary>How do I upgrade\?</summary>(.*?)</details>", readme)
        self.assertTrue(answer, "README has no upgrade answer")
        self.assertIn(f"docs/existing-users.md#{_anchor(sub_heading)}", answer.group(1),
                      "README's upgrade answer does not point a 6.0 user at the 6.1 subsection")

    def test_the_specs_describe_the_shipped_code(self) -> None:
        """AC2. MUTANTS: the TSD left at its 2026-07-17 revision (the mutation gate and its
        ledger `.local/mutation-runs.json`, which nothing writes; a `mutation` lane `gate.py`
        does not register; the verification-depth gate and `carry_forward` in its coverage map);
        the PRD's summary still listing 'the two-role review' and 'mutation evidence'."""
        pats = {**retired_surface.surfaces(),
                **{label: re.compile(rx) for label, rx in RETIRED_61.items()}}
        for name, path in SPECS.items():
            with self.subTest(spec=name):
                self.assertEqual([], retired_surface.live_mentions(_current(path), pats),
                                 f"{name}.md names a retired surface as current")

        tsd = _current(SPECS["tsd"])
        gate_sec = re.search(r"(?ms)^### The artefact gate\b.*?\n(\|.*?)\n\n", tsd)
        self.assertTrue(gate_sec, "the TSD has no artefact-gate lane table")
        named = set()
        for row in gate_sec.group(1).splitlines()[2:]:
            named |= set(re.findall(r"`([\w-]+)`", row.split("|")[1]))
        self.assertTrue(named, "the TSD's lane table names no lane")
        with tempfile.TemporaryDirectory() as d:
            lanes = _registered_lanes(_init(Path(d)))
        self.assertIn("conformance", lanes, "the gate's registry could not be read")
        self.assertEqual([], sorted(named - lanes),
                         "the TSD's lane table names a lane gate.py does not register")

        cov = re.search(r"(?ms)^#### Unit coverage map\b(.*?)^### ", tsd)
        self.assertTrue(cov, "the TSD has no unit coverage map")
        listed = re.search(r"```text\n(.*?)```", cov.group(1), re.S)
        modules = [m.strip() for m in (listed.group(1).splitlines() if listed else []) if m.strip()]
        for row in cov.group(1).splitlines():
            cells = row.split("|")
            if row.startswith("| ") and len(cells) > 3 and not cells[1].strip().startswith(("Tier", "Repo CI")):
                modules += [m[:-3] for m in re.findall(r"`([\w/]+\.py)`", cells[2])]
        self.assertTrue(modules, "the coverage map names no module")
        for module in modules:
            with self.subTest(module=module):
                self.assertTrue((SCRIPTS / f"{module}.py").is_file(),
                                f"the coverage map names {module}, which is not under scripts/")

        code = _local_readers()
        for name, path in SPECS.items():
            for local in sorted(set(re.findall(r"\.local/([\w.-]+\w)", _current(path)))
                                | _local_table_files(_current(path))):
                with self.subTest(spec=name, local=local):
                    self.assertTrue(local in code, f"{name}.md names .local/{local}, which no "
                                                   f"shipped or tools/ script reads or writes")

    def test_each_61_command_change_is_in_its_help(self) -> None:
        """AC3. MUTANTS: HEAD's help, where `verify_ac.py run --unit` is described by its
        changelog fragment alone; a help page restored to teaching `handoff.py generate` as
        the run's last step."""
        pages = sorted((SKILL / "help").glob("*.md")) + sorted(SKILL.glob("reference-*.md"))
        docs = "\n".join(p.read_text(encoding="utf-8") for p in pages)
        blocks = _blocks(docs)
        named = {
            "verify_ac.py run --unit": r"\bverify_ac(?:\.py)? run\b[^\n`]*--unit\b",
            "config.py show --sources": r"\bconfig(?:\.py)? show\b[^\n`]*--sources\b",
            "sprint.py lane return --tokens": r"\blane return\b[^\n`]*--tokens\b",
            "sprint.py lane return --minutes": r"\blane return\b[^\n`]*--minutes\b",
            "refine.py add --into": r"\brefine(?:\.py)? add\b[^\n`]*--into\b",
            "sprint.py plan --worklist RPTxxxx": r"\bplan\b[^\n`]*--worklist RPT",
        }
        for label, rx in named.items():
            with self.subTest(command=label):
                self.assertTrue(re.search(rx, docs), f"no help or reference page names `{label}`")
        self.assertTrue(any(re.search(r"\bhandoff(?:\.py)? show\b", b)
                            and re.search(r"(?i)read-only|without writing|nothing (?:is )?written", b)
                            for b in blocks), "no page names `handoff.py show` as read-only")
        self.assertTrue(any(re.search(r"\bmigrate\b", b) and re.search(r"(?i)\bretired command", b)
                            and re.search(r"(?i)project's own (?:docs|markdown)", b)
                            for b in blocks),
                        "no page says `migrate` reports retired commands in a project's own docs")

        # Each named form runs as written: the flag is on that verb's parser, and the two
        # read-only commands run in a fixture and exit 0.
        for script, verb, flag in (("verify_ac.py", ["run"], "--unit"),
                                   ("config.py", ["show"], "--sources"),
                                   ("sprint.py", ["lane", "return"], "--tokens"),
                                   ("sprint.py", ["lane", "return"], "--minutes"),
                                   ("refine.py", ["add"], "--into"),
                                   ("sprint.py", ["plan"], "--worklist")):
            with self.subTest(parses=f"{script} {' '.join(verb)} {flag}"):
                proc = _py(script, *verb, "--help")
                self.assertEqual(0, proc.returncode, proc.stderr)
                self.assertIn(flag, proc.stdout)
        with tempfile.TemporaryDirectory() as d:
            root = _init(Path(d))
            before = sorted(p.relative_to(root).as_posix() for p in root.rglob("*"))
            for argv in (("config.py", "show", "--sources"),
                         ("handoff.py", "show", "--ids", "US0001")):
                with self.subTest(runs=" ".join(argv)):
                    proc = _py(*argv, "--root", str(root))
                    self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
            self.assertEqual(before, sorted(p.relative_to(root).as_posix() for p in root.rglob("*")),
                             "a read-only command wrote to the project")
            proc = _py("sprint.py", "plan", "--root", str(root), "--worklist", "RPT0001")
            self.assertIn("RPT0001", proc.stdout + proc.stderr)
            self.assertIn("signed report", proc.stdout + proc.stderr,
                          "`plan --worklist RPTxxxx` does not read a report id")

        pats = {label: rx for label, rx in retired_surface.surfaces().items()
                if label in HANDOFF_LABELS}
        self.assertEqual(sorted(HANDOFF_LABELS), sorted(pats), "the helper lacks a handoff label")
        front = [REPO / "README.md", REPO / "docs" / "INSTALL.md", SKILL / "SKILL.md", *pages]
        for path in front:
            with self.subTest(page=path.relative_to(REPO).as_posix()):
                self.assertEqual([], retired_surface.live_mentions(
                    path.read_text(encoding="utf-8"), pats),
                    "a page teaches a retired handoff command outside a retired clause")


if __name__ == "__main__":
    unittest.main()
