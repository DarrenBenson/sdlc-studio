"""US1172 (EP0314): the PRD, TRD and TSD describe what 6.4 ships.

The records 6.4 commits are read from the code that writes them: the persona memory path from
`persona_memory`, the verdict file a brief issues from `critic`, and the evidence pack's path from
`evidence_pack`. Git tracks no persona memory or evidence pack here yet, so each row is proved
against a path the code itself produces. Each writer a row names is held to the parser verb that
writes or binds the record, followed through the script's own functions. The flag defaults are
read from `reference-config.md`, the sweep marker is given to `gate.select_tests` in a fixture, and
the push gate's noise wrapper is read from the pre-push hook. Typed here are the features'
locations, each checked to exist, the phrases each row must say, and the unit ids, since no code
enumerates which units built a feature.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_specs_v64.py
"""
# test-census-subject: sdlc-studio/prd.md
from __future__ import annotations

import argparse
import ast
import fnmatch
import functools
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
SPECS = {name: REPO / "sdlc-studio" / f"{name}.md" for name in ("prd", "trd", "tsd")}
STORIES = REPO / "sdlc-studio" / "stories"
CONFIG_REF = SKILL / "reference-config.md"
ANNEX = SKILL / "reference-evidence-schema.md"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import critic  # noqa: E402
import evidence_pack  # noqa: E402
import gate  # noqa: E402
import gitutil  # noqa: E402 - git with the confined environment
import persona_memory  # noqa: E402
import sprint  # noqa: E402
import sprint_report  # noqa: E402
import test_evidence_annex_fingerprint as fingerprint  # noqa: E402 - the annex's committed pages
import test_lean_trd_refresh as trd_refresh  # noqa: E402 - the committed-records scanner
from lib import run_state  # noqa: E402
from test_lean_prd_refresh import location_problems, unknown_commands  # noqa: E402

#: Each 6.4 feature: what its inventory row must name (a location the skill or repo holds, a
#: command or phrase) and the units that built it.
FEATURES = {
    "evidence annex and committed run record": (
        ("reference-evidence-schema.md", "scripts/sprint_report.py", run_state.EVIDENCE_SCHEMA,
         run_state.PLAN_DIGEST),
        ("US0992", "US0993", "US0994", "US0995", "US0996", "US0997", "US0998", "US1001")),
    "release evidence pack and evidence page": (
        ("scripts/evidence_pack.py", "docs/evidence.md", "release_cut.py evidence-pack",
         "sprint_report.py evidence"), ("US1155", "US1156", "US1160", "US1161")),
    "escaped-defect tracing": (
        ("scripts/escape.py", "escape.py trace", "escape.py to-class", "--escaped"),
        ("US1157", "US1158", "US1159")),
    "each seat's record": (("scripts/retro.py", "retro.py seats", "--author"),
                           ("US1061", "US1062", "US1064")),
    "persona learnings": (
        ("reference-persona-learning.md", "scripts/persona_memory.py", persona_memory.MEMORY_REL),
        ("US1058", "US1059", "US1065", "US1066", "US1067", "US1068")),
    "risk class and second seat": (("reference-config.md#risk-map", "risk.components",
                                    "Risk-class", "second"), ("US1152", "US1153", "US1154")),
    "cost forecast and dispatch effort": (
        ("reference-config.md#routing", "routing.effort", "Dollar cost", "effort_builder"),
        ("US1150", "US1151", "US1165", "US1166")),
    "resume brief and handoff": (
        ("scripts/lib/resume_brief.py", "reference-sprint.md#wave-boundary", "sprint.py handoff",
         sprint.RESUME_BRIEF_REL.name), ("US1140", "US1141", "US1142")),
}
#: A Location mark: a path the skill or the repository root holds, with an optional anchor.
_LOCATION = re.compile(r"^(?:scripts/|templates/|reference-|help/|docs/)")
#: The flags whose defaults the PRD must state, beside every `routing.effort` and
#: `personas.memory` key `reference-config.md` documents.
FLAGS = ("risk.components", "pricing.copilot_billing")
FLAG_FAMILIES = ("routing.effort.", "personas.memory.")
#: A default stated in prose: `` `key` (default `value`) ``.
_PROSE_DEFAULT = re.compile(r"`([\w.]+)` \(default `([^`]*)`\)")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def _body(text: str) -> str:
    """A spec without its Revision History, whose rows record what earlier versions said."""
    return text.split("\n## Revision History", 1)[0]


def _section(text: str, heading: str) -> str:
    """The body under the one heading titled `heading`, to the next of the same or a higher level."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if re.fullmatch(rf"#+\s+{re.escape(heading)}\s*", line)]
    if len(starts) != 1:
        raise AssertionError(f"{len(starts)} headings titled {heading!r}, expected one")
    level = len(lines[starts[0]].split()[0])
    out = []
    for line in lines[starts[0] + 1:]:
        m = re.match(r"^(#+)\s", line)
        if m and len(m.group(1)) <= level:
            break
        out.append(line)
    return "\n".join(out)


def _tables(text: str) -> list[list[list[str]]]:
    """Every table in `text`, each as its header row then its body rows."""
    out, cur = [], None
    for line in text.splitlines():
        if not line.startswith("|"):
            cur = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cur is None:
            cur = [cells]
            out.append(cur)
        elif not set("".join(cells)) <= set("-: "):
            cur.append(cells)
    return out


def _rows(text: str, first: str) -> list[list[str]]:
    """The body rows of every table in `text` whose header's first cell is `first`."""
    return [row for t in _tables(text) if t[0][0] == first for row in t[1:]]


def _spans(cell: str) -> list[str]:
    return re.findall(r"`([^`]+)`", cell)


def _unquote(value: str) -> str:
    return value.strip().strip("`").strip()


def config_defaults(text: str) -> dict[str, str]:
    """Each key `reference-config.md` states a default for: a table row whose first cell
    backticks the key, read in the column headed Default, or a prose `(default ...)`."""
    out = {k: v for k, v in _PROSE_DEFAULT.findall(text)}
    for table in _tables(text):
        if "Default" not in table[0]:
            continue
        col = table[0].index("Default")
        for row in table[1:]:
            for key in _spans(row[0]):
                out.setdefault(key, _unquote(row[col]))
    return out


@functools.lru_cache(maxsize=None)
def _functions(script: str) -> dict[str, ast.AST]:
    tree = ast.parse(_read(SCRIPTS / f"{script}.py"))
    return {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def reaches(script: str, start: str, target: str) -> bool:
    """Whether `start`, a function of `script`, names `target` (a function, attribute or name)
    in its own body or in the body of a function of the same script it names, followed through."""
    funcs, seen, todo = _functions(script), set(), [start]
    while todo:
        name = todo.pop()
        if name in seen or name not in funcs:
            continue
        seen.add(name)
        for node in ast.walk(funcs[name]):
            named = (node.id if isinstance(node, ast.Name) else
                     node.attr if isinstance(node, ast.Attribute) else None)
            if named == target:
                return True
            if named in funcs:
                todo.append(named)
    return False


def verbs(script: str) -> dict[str, argparse.ArgumentParser]:
    """The subcommand parsers of `script`'s `build_parser()`."""
    parser = __import__(script).build_parser()
    return next(a for a in parser._actions
                if isinstance(a, argparse._SubParsersAction)).choices


def handler(script: str, verb: str) -> str:
    return verbs(script)[verb].get_default("func").__name__


def writer_problems(cell: str, wanted: tuple[tuple[str, str | None], ...]) -> list[str]:
    """Why a writer cell does not name each `(script, verb)` in `wanted`, or names a script or
    a verb the code does not have."""
    spans = _spans(cell)
    bad = [f"names no `{s}.py{' ' + v if v else ''}`" for s, v in wanted
           if f"{s}.py{' ' + v if v else ''}" not in spans]
    for span in spans:
        m = re.fullmatch(r"([\w/]+)\.py(?: ([a-z][\w-]*))?", span)
        if not m:
            continue
        if not (SCRIPTS / f"{m.group(1)}.py").is_file():
            bad.append(f"`{span}`: no such script")
        elif m.group(2) and m.group(2) not in verbs(m.group(1)):
            bad.append(f"`{span}`: {m.group(1)}.py has no {m.group(2)} verb")
    return bad


def _tracked(pattern: str) -> list[str]:
    out = gitutil.git(["ls-files", "-z", "--", pattern], REPO, text=True)
    return [f for f in out.stdout.split("\0") if f]


def _stage(hook: str) -> str:
    """The TSD pipeline stage, a numbered item, that names `.githooks/<hook>`."""
    items = re.split(r"\n(?=\d+\. )", _section(_read(SPECS["tsd"]), "Pipeline Stages"))
    found = [_flat(i) for i in items if f".githooks/{hook}" in i and re.match(r"\d+\. ", i)]
    if len(found) != 1:
        raise AssertionError(f"{len(found)} TSD pipeline stages name .githooks/{hook}")
    return found[0]


class SpecsV64Tests(unittest.TestCase):
    """US1172: what the three specs say 6.4 ships."""

    def test_the_prd_inventory_and_flags_name_64s_features(self) -> None:
        """AC1. Mutants: any 6.4 feature's row dropped, or not naming its location, its phrase
        or one of its units, or not Complete, or naming a Location that resolves to no file or
        anchor, or a `<script>.py <verb>` its script lacks; a `risk.components`,
        `pricing.copilot_billing`, `routing.effort` or `personas.memory` key missing from the
        flags table, or given a default other than the one `reference-config.md` states."""
        prd = _body(_read(SPECS["prd"]))
        rows = _rows(_section(prd, "3. Feature Inventory"), "Feature")
        self.assertGreaterEqual(len(rows), 40, "premise: the Feature Inventory moved")
        for feature, (marks, units) in FEATURES.items():
            with self.subTest(feature=feature):
                for mark in (m for m in marks if _LOCATION.match(m)):
                    self.assertEqual([], location_problems(mark), f"premise: {mark} moved")
                for unit in units:
                    self.assertTrue(list(STORIES.glob(f"{unit}-*.md")), unit)
                hits = [r for r in rows if all(m in " | ".join(r) for m in marks)]
                self.assertEqual(1, len(hits), f"{feature}: {len(hits)} rows name {marks}")
                row = hits[0]
                self.assertEqual("Complete", row[2])
                self.assertEqual([], location_problems(row[4]))
                self.assertEqual([], unknown_commands(row[1]))
                self.assertEqual([], [u for u in units if not re.search(rf"\b{u}\b", row[5])])
        stated = config_defaults(_read(CONFIG_REF))
        wanted = set(FLAGS) | {k for k in stated if k.startswith(FLAG_FAMILIES)}
        self.assertLessEqual({"routing.effort.builder", "routing.effort.reviewer",
                              "personas.memory.validity_days", "personas.memory.inject_max",
                              *FLAGS}, wanted, "premise: reference-config.md's keys moved")
        self.assertEqual({"risk.components": "{}", "routing.effort.builder": "inherit",
                          "pricing.copilot_billing": "tokens"},
                         {k: stated[k] for k in ("risk.components", "routing.effort.builder",
                                                 "pricing.copilot_billing")},
                         "premise: the config reader misread a default")
        flags = {}
        for row in _rows(_section(prd, "Feature Flags"), "Key"):
            for key in _spans(row[0]):
                flags[key] = _unquote(row[1])
        for key in sorted(wanted):
            with self.subTest(flag=key):
                self.assertIn(key, flags, f"the PRD's flags table does not list {key}")
                self.assertEqual(stated[key], flags[key])

    def test_the_trd_names_every_record_64_commits(self) -> None:
        """AC2. Mutants: a 6.4 record's row dropped, or its path not the one its writer's code
        writes; a writer cell missing `persona_memory.py`, `critic.py brief`, `critic.py record`
        or `release_cut.py evidence-pack`, or naming a script or verb the code lacks; the state
        table without `resume-brief.md` and `sprint.py handoff`; the data architecture not naming
        the annex or naming another version; the scanner not reading the verdict or persona
        memory tree, or passing a file there that no row matches."""
        trd = _body(_read(SPECS["trd"]))
        section = _section(trd, "Committed evidence and records")
        table = _rows(section, "Record")
        listed = [p for r in table for p in _spans(r[1])]
        with tempfile.TemporaryDirectory() as d:
            issued = critic.issue_verdict_file(d, "US0001", "0123abcd").relative_to(d).as_posix()
        records = {
            "persona memory": (persona_memory.memory_path("", "<persona>").as_posix(),
                               persona_memory.memory_path("", "engineering").as_posix(),
                               (("persona_memory", None), ("sprint", "close"), ("sprint", "sign"))),
            "verdict files": ((critic.VERDICTS_DIR_REL / "<unit>" / "<fp>-<token>.txt").as_posix(),
                              issued, (("critic", "brief"), ("critic", "record"))),
            "evidence pack": (evidence_pack.pack_rel("<version>"), evidence_pack.pack_rel("6.4.0"),
                              (("release_cut", "evidence-pack"),)),
        }
        # Each writer named, read from the code: the verb's handler reaches what writes the path.
        for script, verb, target in (("persona_memory", "add", "memory_path"),
                                     ("persona_memory", "propose", "memory_path"),
                                     ("sprint", "close", "_CLOSE_CHAIN"),
                                     ("sprint", "sign", "strike"),
                                     ("critic", "brief", "issue_verdict_file"),
                                     ("critic", "record", "source_cell"),
                                     ("release_cut", "evidence-pack", "write_pack")):
            with self.subTest(writer=f"{script}.py {verb}"):
                self.assertTrue(reaches(script, handler(script, verb), target),
                                f"{script}.py {verb} does not reach {target}")
        # Controls: a verb that writes no pack does not reach its writer, and a cell naming a verb
        # the script lacks, or leaving one out, is refused.
        self.assertFalse(reaches("release_cut", handler("release_cut", "tag-check"), "write_pack"))
        self.assertEqual(["names no `critic.py record`", "`critic.py verdict`: critic.py has no "
                          "verdict verb"], writer_problems("`critic.py verdict`",
                                                           (("critic", "record"),)))
        # The close runs its chain's steps by name, so its step is read from the chain.
        self.assertIn("persona-memory", sprint._CLOSE_CHAIN)
        self.assertTrue(reaches("sprint", "_close_persona_memory", "mark_listed"))
        for name in ("mark_listed", "strike"):
            self.assertTrue(reaches("persona_memory", name, "memory_path"), name)
        self.assertTrue(reaches("evidence_pack", "write_pack", "pack_rel"))
        for record, (path, fixture, writers) in records.items():
            with self.subTest(record=record):
                hits = [r for r in table if path in _spans(r[1])]
                self.assertEqual(1, len(hits), f"{record}: {len(hits)} rows list {path}")
                self.assertTrue(fnmatch.fnmatchcase(fixture, trd_refresh._glob(path)), fixture)
                self.assertEqual([path], [p for p in listed
                                          if fnmatch.fnmatchcase(fixture, trd_refresh._glob(p))])
                self.assertEqual([], writer_problems(hits[0][2], writers))
        trees = trd_refresh.committed_trees()
        self.assertLessEqual({critic.VERDICTS_DIR_REL.as_posix(), persona_memory.MEMORY_REL,
                              sprint_report.report_dir("").as_posix()}, set(trees))
        preamble = _flat(section.split("\n|", 1)[0])
        for tree in trees:
            self.assertIn(f"`{tree}/`", preamble, f"the TRD does not say the scan reads {tree}")
        stray = f"{persona_memory.MEMORY_REL}/notes.txt"
        self.assertEqual([stray], trd_refresh.unlisted([records["persona memory"][1], issued,
                                                        records["evidence pack"][1], stray],
                                                       set(listed)))
        state = _rows(_section(trd, "JSON state files (under `.local/`)"), "File")
        local = sprint.RESUME_BRIEF_REL.parts
        self.assertEqual(("sdlc-studio", ".local"), local[:2], "premise: the brief left .local")
        brief = "/".join(local[2:])
        hits = [r for r in state if brief in _spans(r[0])]
        self.assertEqual(1, len(hits), f"{len(hits)} state rows name {brief}")
        self.assertEqual([], writer_problems(hits[0][1], (("sprint", None), ("sprint", "handoff"))))
        self.assertTrue(reaches("sprint", handler("sprint", "handoff"), "RESUME_BRIEF_REL"))
        data = _flat(_section(trd, "6. Data Architecture"))
        version = sprint_report.EVIDENCE_SCHEMA_VERSION
        self.assertIn(f"**Annex version {version}.**", _read(ANNEX), "premise: the masthead moved")
        self.assertRegex(data, rf"`reference-evidence-schema\.md`[^.]*\bannex version "
                               rf"{re.escape(version)}\b")
        self.assertIn(f"`{run_state.EVIDENCE_SCHEMA}`", data)

    def test_the_tsd_names_the_sweep_marker_and_the_push_noise_gate(self) -> None:
        """AC3. Mutants: the commit stage not naming the sweep marker, or naming one `gate.py`
        does not read, or not saying it joins every commit's selection or the budget it is held
        to; the push stage naming the full suite and not the noise wrapper or the baseline it
        holds the run to; the noise paragraph still saying neither hook holds it; the annex
        tests unnamed, or holding fewer than every committed report."""
        tsd = _body(_read(SPECS["tsd"]))
        commit = _stage("commit-msg")
        markers = [s for s in _spans(commit) if s.startswith("# test-selection:")]
        self.assertEqual(1, len(markers), f"the commit stage names {markers}")
        self.assertRegex(commit, r"joins every commit's selection")
        self.assertIn(f"{gate.SWEEP_BUDGET_SECONDS}-second", commit)
        self.assertIn(f"first {gate._CENSUS_HEAD_LINES} lines", commit)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tests = root / "tools" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_sweep.py").write_text(f"{markers[0]} 1s\nimport unittest\n",
                                                 encoding="utf-8")
            (tests / "test_other.py").write_text("import unittest\n", encoding="utf-8")
            picked = gate.select_tests(str(root), ["docs/guide.md"])
        self.assertEqual(["tools/tests/test_sweep.py"], picked["selectors"],
                         "the marker the TSD names does not join a docs-only selection")
        hook = _read(REPO / ".githooks" / "pre-push")
        wrapper = "tools/run-suite.sh --noise-gate"
        self.assertIn(f"noise=(bash {wrapper})", hook, "premise: the hook's wrapper moved")
        self.assertEqual(2, len(re.findall(r'\$\{noise\[@\]\+"\$\{noise\[@\]\}"\} python3 '
                                           r'"\$skill/gate\.py" --boundary', hook)),
                         "premise: the hook does not run both boundaries inside the wrapper")
        self.assertIn(wrapper, _read(REPO / "tools" / "remote-gate.sh"))
        baseline = "tools/test-noise-baseline.json"
        self.assertIn(f'budget_rel = "{baseline}"', _read(REPO / "tools" / "run-suite.sh"))
        self.assertIn("tools/skill-tests.sh", _read(REPO / ".github" / "workflows" / "lint.yml"))
        self.assertIn("test_noise.py\" --budget-check", _read(REPO / "tools" / "skill-tests.sh"))
        push = _stage("pre-push")
        self.assertIn("full suite", push)
        self.assertIn(f"`{wrapper}`", push, "the push stage says nothing of the noise gate")
        self.assertIn(f"`{baseline}`", push)
        self.assertNotRegex(_flat(tsd), r"(?i)neither hook holds it")
        modules = ("test_evidence_annex_fingerprint.py", "test_evidence_annex_report.py")
        for name in modules:
            self.assertIn(f"`{name}`", tsd)
            head = _read(SCRIPTS / "tests" / name)[:2000]
            self.assertIn(f"# test-census-subject: .claude/skills/sdlc-studio/{ANNEX.name}", head)
        held = {p.name for p in fingerprint.committed_pages()}
        held |= {f"{r}.json" for r in fingerprint.annex.SCHEMA_ONE}
        committed = {Path(f).name for f in _tracked("sdlc-studio/reports/RPT*.json")}
        self.assertGreater(len(committed), 25, "premise: the reports were not read")
        self.assertEqual(committed, held, "a committed report the annex tests do not hold")
        self.assertTrue(all(json.loads((REPO / "sdlc-studio" / "reports" / n).read_text(
            encoding="utf-8")).get("schema") in (1, 2) for n in committed))


if __name__ == "__main__":
    unittest.main()
