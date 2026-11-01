"""US1102: the TSD states coverage by the CI step, describes per-unit line coverage, names both
test-module conventions, maps every PRD NFR to a row and carries a 6.2 header.

Each fact is read from where it is decided: the coverage floor, step name and command from
`.github/workflows/lint.yml`; this repository's `review.line_coverage` through
`transition.line_coverage_mode`, which reads `sdlc-studio/.config.yaml`, and the modes from
`transition.LINE_COVERAGE_MODES`; the shared helpers from the two test trees and the repository
root, the markers from `pytest.ini` and the hooks from `.githooks/`; the NFRs from the PRD's
section 5, split into clauses; the release baseline through `doc_freshness`'s census. Pinned by
hand, as the criteria name them: the two module conventions and the `6.2` on main.
"""
# test-census-subject: sdlc-studio/tsd.md
import configparser
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
TSD = REPO / "sdlc-studio" / "tsd.md"
PRD = REPO / "sdlc-studio" / "prd.md"
WORKFLOW = REPO / ".github" / "workflows" / "lint.yml"
TEST_TREES = (SCRIPTS / "tests", REPO / "tools" / "tests")
sys.path.insert(0, str(SCRIPTS))

import doc_freshness  # noqa: E402 - the census that reads a document's release baseline
import transition  # noqa: E402 - the reader of `review.line_coverage` and its modes
from lib import sdlc_md  # noqa: E402 - the raw `.config.yaml` reader, with no defaults merged

#: The two module conventions (US1102 AC2), as the criterion names them, with the file pattern
#: each is written as.
CONVENTIONS = {"per-script": "test_<script>.py", "per-unit lean": "test_lean_<topic>.py"}
#: The work on `main` beside the released baseline (US1102 AC4), as the criterion names it.
ON_MAIN = "6.2"
NFR_HEADING = "## Quality Gates (PRD section 5 NFR mapping)"
_SENTENCE_RE = re.compile(r"(?<=[.;])\s+")
_PERCENT_RE = re.compile(r"(\d+(?:\.\d+)?)\s?%")
_TICKED_RE = re.compile(r"`([^`\n]+)`")
_STEP_RE = re.compile(r"^[ \t]*- name: (?P<name>[^\n]+?)[ \t]*\n(?:[ \t]*#[^\n]*\n)*"
                      r"[ \t]*run: (?P<run>coverage report\b[^\n]*?)[ \t]*$", re.M)
#: A component count: a number, in digits or as a word from two to twelve ("one test" is a
#: sentence, not an inventory), before `module`, `file`, `test` or `script`, up to two words on.
_COUNT_RE = re.compile(r"\b(?:\d[\d,]*\+?|two|three|four|five|six|seven|eight|nine|ten|eleven|"
                       r"twelve)\s+(?:[\w-]+\s+){0,2}(?:modules?|files?|tests?|scripts?)\b", re.I)
_QUOTE_RE = re.compile(r'"([^"]+)"')
_ROW_HEADING_RE = re.compile(r"^\*\*(?P<h>[^*]+)\*\*")
_TEST_REF_RE = re.compile(r"`(?:[\w./-]*/)?(test_\w+\.py)(?:::(\w+))?(?:::(\w+))?`")
_STATUS_RE = re.compile(r"^>\s*\*\*Status:\*\*\s*(?P<v>.+?)\s*$", re.M)
_VALUES_RE = re.compile(r"\*\*Status Values:\*\*\s*(?P<v>.+?)\s*$", re.M)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flat(text: str) -> str:
    return " ".join(text.split())


def section(text: str, heading: str) -> str:
    """The body under `heading` (a whole heading line), up to the next heading of its level or
    above; empty when the heading is absent."""
    level = len(heading) - len(heading.lstrip("#"))
    m = re.search(rf"^{re.escape(heading)}\s*$(.*?)(?=^#{{1,{level}}}\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def body(tsd: str) -> str:
    """The TSD above its revision history, which narrates what the document used to say."""
    return re.split(r"^## Revision History\s*$", tsd, maxsplit=1, flags=re.M)[0]


def mutate(text: str, old: str, new: str) -> str:
    """`text` with its one `old` replaced, so a mutant cannot silently miss its target."""
    assert text.count(old) == 1, f"{old!r} occurs {text.count(old)} times, not once"
    return text.replace(old, new)


# AC1: coverage points at the CI step, and per-unit line coverage carries this repo's setting.

def coverage_step(workflow: str) -> dict | None:
    """The workflow step that runs `coverage report`: its name, command and `--fail-under`."""
    m = _STEP_RE.search(workflow)
    if not m:
        return None
    floor = re.search(r"--fail-under=(\d+)", m.group("run"))
    return {"name": m.group("name"), "run": m.group("run"),
            "floor": floor.group(1) if floor else None}


def stated_modes(sentence: str, modes: tuple[str, ...]) -> set[str]:
    """The `review.line_coverage` modes a sentence names in code spans, bare or as `key: mode`."""
    named = set()
    for token in _TICKED_RE.findall(sentence):
        keyed = re.fullmatch(r"review\.line_coverage:\s*(\S+)", token)
        if token in modes:
            named.add(token)
        elif keyed:
            named.add(keyed.group(1))
    return named


def coverage_problems(tsd: str, step: dict, mode: str, unset: bool) -> list[str]:
    """Why the TSD pins a coverage percentage other than the CI step's floor, why its Coverage
    Measurement section does not point at that step, or why it misstates per-unit line coverage
    or this repository's `mode`; empty when it states coverage as the CI step holds it."""
    modes = transition.LINE_COVERAGE_MODES
    problems = [f"the TSD pins {p}%, which is not the CI step's {step['floor']}% floor"
                for p in sorted(set(_PERCENT_RE.findall(body(tsd))) - {step["floor"]})]
    measurement = flat(section(tsd, "## Coverage Measurement"))
    for what in (step["name"], step["run"], WORKFLOW.relative_to(REPO).as_posix(),
                 "verify_ac.py run --coverage"):
        if what not in measurement:
            problems.append(f"Coverage Measurement does not name {what!r}")
    problems += [f"Coverage Measurement does not describe `{m}`" for m in modes
                 if f"`{m}`" not in measurement]
    stated = [s for s in _SENTENCE_RE.split(measurement)
              if "review.line_coverage" in s and re.search(r"\bthis repository\b", s, re.I)]
    if not stated:
        problems.append("Coverage Measurement does not state this repository's "
                        "review.line_coverage")
    for s in stated:
        named = stated_modes(s, modes)
        if named != {mode}:
            problems.append(f"this repository's review.line_coverage is stated as "
                            f"{sorted(named)}; the config reads {mode}: {s!r}")
        if "shipped default" in s and mode != transition.LINE_COVERAGE_DEFAULT:
            problems.append(f"{mode} is called the shipped default: {s!r}")
        if re.search(r"\bunset\b", s) and not unset:
            problems.append(f"the config is said to leave review.line_coverage unset: {s!r}")
    return problems


# AC2: the test tree names both conventions, the shared helpers, the markers and the hooks.

def shared_helpers() -> list[str]:
    """Each non-test module and directory in the two test trees, and the root conftest, by
    name, one entry per file, so a name two trees share is required twice."""
    names = []
    for tree in TEST_TREES:
        for path in sorted(tree.iterdir()):
            if path.name.startswith(("_", ".")) or path.name.startswith("test_"):
                continue
            if path.is_dir():
                names.append(path.name + "/")
            elif path.suffix == ".py":
                names.append(path.name)
    if (REPO / "conftest.py").exists():
        names.append("conftest.py")
    return names


def pytest_markers() -> list[str]:
    parser = configparser.ConfigParser()
    parser.read(REPO / "pytest.ini", encoding="utf-8")
    return [line.split(":", 1)[0].strip()
            for line in parser.get("pytest", "markers", fallback="").splitlines() if line.strip()]


def hooks() -> list[str]:
    return sorted(p.name for p in (REPO / ".githooks").iterdir() if p.is_file())


def organisation_problems(tsd: str, helpers: list[str], markers: list[str],
                          hook_names: list[str]) -> list[str]:
    """Why the Test Organisation section misses a module convention, a shared helper, a marker
    or a hook, or states a component count; empty when it names them all, uncounted."""
    org = section(tsd, "## Test Organisation")
    problems = [f"Test Organisation does not name the {name} convention ({pattern})"
                for name, pattern in CONVENTIONS.items()
                if name not in org or pattern not in org]
    for name in sorted(set(helpers)):
        if org.count(name) < helpers.count(name):
            problems.append(f"Test Organisation names {name} {org.count(name)} times; "
                            f"the tree has {helpers.count(name)}")
    problems += [f"Test Organisation does not name the {m} marker" for m in markers if m not in org]
    problems += [f"Test Organisation does not name the {h} hook" for h in hook_names
                 if f"{h}" not in org]
    problems += [f"Test Organisation states a count: {m.group(0)!r}"
                 for m in _COUNT_RE.finditer(org)]
    return problems


# AC3: every clause of the PRD's section 5 maps to a TSD row that quotes it.

def blocks(text: str) -> list[tuple[str, bool]]:
    """Each paragraph of `text`, with each list item a block of its own, and whether it is one."""
    out: list[tuple[str, bool]] = []
    current: list[str] = []
    item = False
    for line in text.splitlines():
        s = line.strip()
        if not s or s == "---" or s.startswith("- "):
            if current:
                out.append((" ".join(current), item))
            current, item = ([s[2:]], True) if s.startswith("- ") else ([], False)
            continue
        current.append(s)
    if current:
        out.append((" ".join(current), item))
    return out


def clauses(block: str) -> list[str]:
    """`block` cut after each `.` or `;` that a space or the end follows, outside a code span or
    a parenthesis, so a list item's own `;` inside brackets keeps the item whole."""
    text, out, start, depth, code = flat(block), [], 0, 0, False
    for i, ch in enumerate(text):
        if ch == "`":
            code = not code
        elif code:
            continue
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch in ".;" and depth == 0 and (i + 1 == len(text) or text[i + 1] == " "):
            out.append(text[start:i + 1].strip())
            start = i + 1
    if text[start:].strip():
        out.append(text[start:].strip())
    return [c for c in out if c]


def prd_nfrs(prd: str) -> list[tuple[str, str, bool]]:
    """(heading, clause, is a list item) for each clause under each `###` of the PRD's section 5."""
    nfr = section(prd, "## 5. Non-Functional Requirements")
    out = []
    for m in re.finditer(r"^### (?P<h>[^\n]+?)\s*\n(?P<b>.*?)(?=^### |\Z)", nfr, re.M | re.S):
        for block, item in blocks(m.group("b")):
            out += [(m.group("h"), c, item) for c in clauses(block)]
    return out


def nfr_rows(tsd: str) -> list[dict]:
    """The rows of the first table under the NFR mapping heading: each row's heading, the
    clauses it quotes, its gate cell and the line itself."""
    lines = section(tsd, NFR_HEADING).splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("| NFR")), None)
    if start is None:
        return []
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        heading = _ROW_HEADING_RE.match(cells[0])
        rows.append({"heading": heading.group("h") if heading else None,
                     "quotes": [flat(q) for q in _QUOTE_RE.findall(cells[0])],
                     "gate": cells[1] if len(cells) > 1 else "", "line": line})
    return rows


def missing_tests(cell: str) -> list[str]:
    """Each `test_<x>.py[::Class[::method]]` a gate cell names in a code span, with or without a
    directory before it, that the test trees lack."""
    out = []
    for m in _TEST_REF_RE.finditer(cell):
        name, cls, meth = m.groups()
        found = [tree / name for tree in TEST_TREES if (tree / name).exists()]
        if not found:
            out.append(f"{name} is no test module")
            continue
        src = "".join(_read(p) for p in found)
        if cls and not re.search(rf"^class {cls}\b", src, re.M):
            out.append(f"{name} has no class {cls}")
        if meth and not re.search(rf"^\s+def {meth}\b", src, re.M):
            out.append(f"{name} has no test {meth}")
    return out


def nfr_problems(prd: str, tsd: str) -> list[str]:
    """Why a PRD section 5 clause has no TSD row quoting it, why a row maps a heading or quotes
    words the PRD does not state, or why a row's gate names a test that does not exist; empty
    when the table and the section map one to the other."""
    stated = prd_nfrs(prd)
    rows = nfr_rows(tsd)
    problems = [] if stated else ["the PRD's section 5 yielded no clause"]
    problems += [] if rows else ["the TSD's NFR mapping table has no row"]
    headings = {h for h, _, _ in stated}
    for row in rows:
        if row["heading"] not in headings:
            problems.append(f"a TSD row maps {row['heading']!r}, no PRD section 5 heading: "
                            f"{row['line'][:80]}")
        if not row["quotes"]:
            problems.append(f"a TSD row quotes no PRD clause: {row['line'][:80]}")
        for q in row["quotes"]:
            if not any(h == row["heading"] and q in c for h, c, _ in stated):
                problems.append(f"a TSD {row['heading']} row quotes {q!r}, which no PRD "
                                f"{row['heading']} clause states")
        problems += [f"a TSD {row['heading']} row names {m}" for m in missing_tests(row["gate"])]
    for h, c, _ in stated:
        if not any(r["heading"] == h and any(q in c for q in r["quotes"]) for r in rows):
            problems.append(f"PRD {h}: no TSD row maps {c!r}")
    return problems


# AC4: the header names the 6.2 baseline and a status the document defines; history in order.

def census_of(tsd: str) -> dict:
    """`doc_freshness.census_claims` over `tsd` beside this repository's SKILL.md."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".claude" / "skills" / "sdlc-studio").mkdir(parents=True)
        shutil.copy(SKILL / "SKILL.md", root / ".claude" / "skills" / "sdlc-studio" / "SKILL.md")
        (root / "sdlc-studio").mkdir()
        (root / "sdlc-studio" / "tsd.md").write_text(tsd, encoding="utf-8")
        return doc_freshness.census_claims(root, "sdlc-studio/tsd.md")


def header_problems(tsd: str) -> list[str]:
    """Why the header (above the first `---` rule) names a baseline other than SKILL.md's
    release plus `ON_MAIN` on main, or a status outside the foot's Status Values."""
    header = tsd.split("\n---\n", 1)[0]
    problems = []
    values = _VALUES_RE.search(tsd)
    defined = [v.strip() for v in values.group("v").split("|")] if values else []
    status = _STATUS_RE.search(header)
    if not defined:
        problems.append("the TSD defines no Status Values")
    if not status:
        problems.append("the header states no Status")
    elif status.group("v") not in defined:
        problems.append(f"the header's status {status.group('v')!r} is not one of {defined}")
    baselines = [r for r in census_of(tsd)["checked"] if r["claim"] == "baseline"]
    if not baselines:
        problems.append("the census reads no baseline in the TSD")
    for r in baselines:
        if not r["ok"]:
            problems.append(f"the TSD names v{r['claimed']}; SKILL.md is {r['actual']}")
        elif not re.search(rf"\*\*Coverage:\*\*\s*v{re.escape(r['actual'])}\b.*?\bplus\b.*?"
                           rf"\b{re.escape(ON_MAIN)}\b.*?\bmain\b", header, re.S):
            problems.append(f"the header does not name v{r['actual']} plus {ON_MAIN} on main")
    return problems


def history_problems(tsd: str) -> list[str]:
    """Each revision-history row dated before the row above it."""
    dates = re.findall(r"^\|\s*(\d{4}-\d{2}-\d{2})\s*\|", section(tsd, "## Revision History"),
                       re.M)
    problems = [] if len(dates) > 1 else ["the revision history has fewer than two dated rows"]
    problems += [f"{b} follows {a}" for a, b in zip(dates, dates[1:]) if b < a]
    return problems


class TsdRefreshTests(unittest.TestCase):

    def setUp(self):
        self.tsd = _read(TSD)
        self.prd = _read(PRD)

    def test_coverage_points_at_ci_and_names_line_coverage(self):
        """AC1. Mutants: a pinned measured percentage restored; the floor changed in CI and not
        here; the CI step renamed; this repository's mode stated as `block`, bare or as
        `review.line_coverage: block`; the config set to `report`; the key set explicitly where
        the TSD says unset."""
        step = coverage_step(_read(WORKFLOW))
        self.assertIsNotNone(step, "no workflow step runs `coverage report`")
        self.assertIsNotNone(step["floor"], "the coverage step names no --fail-under")
        mode = transition.line_coverage_mode(REPO)
        unset = sdlc_md.project_override(REPO, "review.line_coverage", None) is None
        self.assertEqual([], coverage_problems(self.tsd, step, mode, unset))
        help_text = subprocess.run([sys.executable, str(SCRIPTS / "verify_ac.py"), "run", "--help"],
                                   capture_output=True, text=True, check=False).stdout
        self.assertIn("--coverage", help_text, "verify_ac.py run takes no --coverage")

        pinned = mutate(self.tsd, "## Coverage Measurement\n",
                        "## Coverage Measurement\n\nMeasured coverage sits at roughly 82%.\n")
        self.assertEqual(["the TSD pins 82%, which is not the CI step's "
                          f"{step['floor']}% floor"],
                         coverage_problems(pinned, step, mode, unset))
        self.assertTrue(coverage_problems(self.tsd, {**step, "floor": "85"}, mode, unset))
        self.assertTrue(coverage_problems(self.tsd, {**step, "name": "Coverage (scripts)"},
                                          mode, unset))
        measurement = section(self.tsd, "## Coverage Measurement")
        unnamed = self.tsd.replace(measurement, measurement.replace(
            "`verify_ac.py run --coverage`", "`verify_ac.py run`"))
        self.assertEqual(["Coverage Measurement does not name 'verify_ac.py run --coverage'"],
                         coverage_problems(unnamed, step, mode, unset))
        for m in transition.LINE_COVERAGE_MODES:
            with self.subTest(undescribed=m):
                bare = self.tsd.replace(measurement, measurement.replace(f"`{m}`", m))
                self.assertIn(f"Coverage Measurement does not describe `{m}`",
                              coverage_problems(bare, step, mode, unset))
        stated = next(s for s in _SENTENCE_RE.split(flat(section(self.tsd,
                                                                  "## Coverage Measurement")))
                      if "this repository" in s and "review.line_coverage" in s)
        span = re.search(r"\s+".join(map(re.escape, stated.split())), self.tsd)
        other_mode = next(m for m in transition.LINE_COVERAGE_MODES if m != mode)
        # one mode swapped for another, bare; and a second mode added as `key: mode` beside it
        for wrong in (f"`{other_mode}`", f"`{mode}` (`review.line_coverage: {other_mode}`)"):
            with self.subTest(wrong=wrong):
                restated = span.group(0).replace(f"`{mode}`", wrong, 1)
                self.assertNotEqual(span.group(0), restated)
                mutant = self.tsd[:span.start()] + restated + self.tsd[span.end():]
                found = coverage_problems(mutant, step, mode, unset)
                self.assertEqual(1, len(found), found)
                self.assertIn("is stated as", found[0])
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "sdlc-studio").mkdir()
            (Path(tmp) / "sdlc-studio" / ".config.yaml").write_text(
                "review:\n  line_coverage: report\n", encoding="utf-8")
            other = transition.line_coverage_mode(tmp)
            self.assertEqual("report", other)
            self.assertFalse(sdlc_md.project_override(tmp, "review.line_coverage", None) is None)
        self.assertTrue(coverage_problems(self.tsd, step, other, unset))
        explicit = coverage_problems(self.tsd, step, mode, False)
        self.assertEqual(1, len(explicit), explicit)
        self.assertIn("unset", explicit[0])
        with mock.patch.object(transition, "LINE_COVERAGE_DEFAULT", other_mode):
            moved = coverage_problems(self.tsd, step, mode, unset)
        self.assertEqual(1, len(moved), moved)
        self.assertIn("shipped default", moved[0])

    def test_the_test_tree_names_both_conventions(self):
        """AC2. Mutants: a convention, a helper, the root conftest, a marker or a hook dropped
        from Test Organisation; a helper added to the tree and not named; a module count."""
        for tree in TEST_TREES:
            names = [p.name for p in tree.glob("test_*.py")]
            self.assertTrue(any(n.startswith("test_lean_") for n in names), tree)
            self.assertTrue(any(not n.startswith("test_lean_") for n in names), tree)
        helpers, markers, hook_names = shared_helpers(), pytest_markers(), hooks()
        self.assertTrue(helpers and markers and hook_names, (helpers, markers, hook_names))
        self.assertGreaterEqual(helpers.count("conftest.py"), 2, helpers)
        self.assertEqual([], organisation_problems(self.tsd, helpers, markers, hook_names))

        org = section(self.tsd, "## Test Organisation")

        def problems_with(new_org: str, **kw) -> list[str]:
            args = {"helpers": helpers, "markers": markers, "hook_names": hook_names, **kw}
            return organisation_problems(self.tsd.replace(org, new_org), **args)

        self.assertTrue(problems_with(org.replace("test_lean_<topic>.py", "test_<topic>.py")))
        self.assertTrue(problems_with(org.replace(markers[0], "a_marker")))
        self.assertTrue(problems_with(org.replace(hook_names[0], "a-hook")))
        root_conftest = next(line for line in org.splitlines() if line.startswith("conftest.py"))
        self.assertTrue(problems_with(org.replace(root_conftest + "\n", "")))
        self.assertTrue(problems_with(org, helpers=helpers + ["newhelper.py"]))
        counted = org.replace("```\n", "```\n\n196 of 332 skill modules are lean.\n", 1)
        self.assertEqual(["Test Organisation states a count: '332 skill modules'"],
                         problems_with(counted))
        worded = org.replace("```\n", "```\n\nIt holds three lean modules.\n", 1)
        self.assertEqual(["Test Organisation states a count: 'three lean modules'"],
                         problems_with(worded))

    def test_every_prd_nfr_has_a_tsd_row(self):
        """AC3. Mutants: a clause added to a PRD NFR, a network path added as a list item, a
        new NFR heading; the appetite breaker's row dropped; a quote the PRD does not state; a
        gate naming a test that does not exist."""
        stated = prd_nfrs(self.prd)
        self.assertTrue(any(item for _, _, item in stated), "no PRD NFR list item was read")
        for words in ("appetite breaker", "ULID"):
            self.assertTrue(any(words in c for _, c, _ in stated), f"no PRD NFR names {words}")
        self.assertEqual([], nfr_problems(self.prd, self.tsd))

        added = mutate(self.prd, "bounds an unattended run.",
                       "bounds an unattended run. The run ledger bounds a session.")
        self.assertEqual(["PRD Scalability: no TSD row maps 'The run ledger bounds a session.'"],
                         nfr_problems(added, self.tsd))
        path = mutate(self.prd, "- the tools a project's Verify lines invoke",
                      "- `curl` from `fetch.py`;\n- the tools a project's Verify lines invoke")
        self.assertEqual(["PRD Security: no TSD row maps '`curl` from `fetch.py`;'"],
                         nfr_problems(path, self.tsd))
        heading = mutate(self.prd, "\n### Availability\n",
                         "\n### Maintainability\n\nEvery script has a test.\n\n### Availability\n")
        self.assertEqual(["PRD Maintainability: no TSD row maps 'Every script has a test.'"],
                         nfr_problems(heading, self.tsd))
        appetite = next(r["line"] for r in nfr_rows(self.tsd)
                        if any("appetite breaker" in q for q in r["quotes"]))
        dropped = nfr_problems(self.prd, mutate(self.tsd, appetite + "\n", ""))
        self.assertEqual(1, len(dropped), dropped)
        self.assertIn("appetite breaker", dropped[0])
        quote = '"Agentic waves bound concurrency"'
        moved = nfr_problems(self.prd, mutate(self.tsd, quote, '"Agentic waves cap concurrency"'))
        self.assertEqual(2, len(moved), moved)
        renamed = nfr_problems(self.prd, mutate(self.tsd, f"**Scalability** - {quote}",
                                                f"**Usability** - {quote}"))
        self.assertEqual(3, len(renamed), renamed)
        self.assertIn("a TSD row maps 'Usability', no PRD section 5 heading", renamed[0])
        cited = "`test_loop_guard.py::BudgetCliTests`"
        missing = nfr_problems(self.prd, mutate(self.tsd, cited,
                                                "`test_loop_guard.py::NoSuchTests`"))
        self.assertEqual(["a TSD Scalability row names test_loop_guard.py has no class "
                          "NoSuchTests"], missing)
        # the near misses of a cited test: a path prefix, a missing test, a module in neither tree
        self.assertEqual([], missing_tests("`tools/tests/test_lean_prd_refresh.py::PrdRulesTests`"
                                           " and `test_sprint.py::WaveTests::"
                                           "test_waves_are_dependency_levels`"))
        self.assertEqual(["test_nope.py is no test module",
                          "test_sprint.py has no test test_nope"],
                         missing_tests("`tools/tests/test_nope.py` and "
                                       "`test_sprint.py::WaveTests::test_nope`"))

    def test_the_header_and_history(self):
        """AC4. Mutants: the baseline back at v6.0.0 or the work on main at 6.1; the status
        restored to the generated wording or set to a value the foot does not define; two
        revision-history rows swapped."""
        self.assertEqual([], header_problems(self.tsd))
        self.assertEqual([], history_problems(self.tsd))

        header = self.tsd.split("\n---\n", 1)[0]
        coverage = re.search(r"\*\*Coverage:\*\* v(\S+) as cut, plus the (\S+) work", header)
        self.assertIsNotNone(coverage, "the header states no Coverage baseline")
        old = mutate(self.tsd, f"v{coverage.group(1)} as cut", "v6.0.0 as cut")
        self.assertEqual([f"the TSD names v6.0.0; SKILL.md is {coverage.group(1)}"],
                         header_problems(old))
        self.assertTrue(header_problems(mutate(self.tsd, f"plus the {ON_MAIN} work",
                                               "plus the 6.1 work")))
        status = _STATUS_RE.search(header).group(0)
        for wrong in ("Generated (brownfield - awaiting validation)", "Approved"):
            with self.subTest(status=wrong):
                mutant = mutate(self.tsd, status, f"> **Status:** {wrong}")
                self.assertEqual(1, len(header_problems(mutant)), header_problems(mutant))
        rows = re.findall(r"^\| \d{4}-\d{2}-\d{2} \|.*$", section(self.tsd, "## Revision History"),
                          re.M)
        swapped = mutate(self.tsd, f"{rows[1]}\n{rows[2]}\n", f"{rows[2]}\n{rows[1]}\n")
        self.assertEqual([f"{rows[1][2:12]} follows {rows[2][2:12]}"], history_problems(swapped))


if __name__ == "__main__":
    unittest.main()
