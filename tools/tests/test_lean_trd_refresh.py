"""CR0645 (EP0293): the TRD describes what 6.2 builds. The type sets this module checks are read
from the code that decides them (LL0043), never typed here, and each is checked to hold a member
known to be in it before it is compared, so an empty read cannot pass as agreement.

US1099: which types execute their `- **Verify:**` lines is `sdlc_md.EXECUTES_VERIFIERS`. The TRD
names that set as the authority, and its table gives each type in it as executed and each type
the creators refuse a command-shaped `Verify:` on as refused; both sets are compared here with the
code. The two code comments that said only a story executes its verifier, and the refusal the
filer prints, name the set instead.

US1101: the TRD's type tables are `sdlc_md`'s maps, its network table is what a scan of the
shipped scripts finds calling `gh`, opening a connection or fetching from origin, and ADR-003,
ADR-004, ADR-009, ADR-012 and the coverage line are held to the code and tree they describe.

Run from the repo root:
    python3 -m pytest tools/tests/test_lean_trd_refresh.py
"""
# test-census-subject: sdlc-studio/trd.md
from __future__ import annotations

import argparse
import ast
import contextlib
import fnmatch
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"
FILE_FINDING = SCRIPTS / "file_finding.py"
ARTIFACT = SCRIPTS / "artifact.py"

sys.path.insert(0, str(SCRIPTS))
import critic  # noqa: E402
import doc_freshness  # noqa: E402
import file_finding  # noqa: E402
import lessons  # noqa: E402
import persona_gen  # noqa: E402
import reconcile  # noqa: E402
import sprint  # noqa: E402
import sprint_report  # noqa: E402
import telemetry  # noqa: E402
from lib import run_state, sdlc_md  # noqa: E402

#: The authority's name. Each test first checks `sdlc_md` defines it, so a rename fails here
#: rather than leaving the documents naming a set that no longer exists.
AUTHORITY = "EXECUTES_VERIFIERS"
#: A criterion the shared refusal reads as a command, and one it reads as an outcome.
COMMAND_SHAPED = "Verify: rg -q needle src/app.py"
OUTCOME_SHAPED = "Verify: the operator sees a red banner naming the file"
#: The two verdicts the TRD's table may give a type, as its second column spells them.
EXECUTED, REFUSED = "executed", "refused when command-shaped"
#: A sentence or clause speaks of executing a `Verify:` line when it holds one of these words and
#: the stem `verif` ("Verify", "verifier", `verify_ac`), both in any case.
_EXECUTING_RE = re.compile(r"\b(?:execut\w*|run|runs|ran|running)\b", re.I)
_VERIF_RE = re.compile(r"verif", re.I)
#: Where a sentence is cut into clauses, outside a code span: a `;`, a spaced hyphen, a parenthesis.
_CLAUSE_CUT_RE = re.compile(r";|\s-\s|[()]")
#: "the authority", or "the one", "the single" or "the sole authority", in any case.
_THE_AUTHORITY = r"(?i:\bthe\s+(?:(?:one|single|sole)\s+)?authority\b)"
#: The text allowed between the set's name and that phrase: no backtick (so no other code span),
#: `;`, `:` or `.`, and no `not`, `no` or `never` as a word or `n't`, in any case.
_GAP = r"(?:(?!(?i:\b(?:not|no|never)\b|n't))[^`;:.])*?"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _trd_body() -> str:
    """The TRD without its Revision History, whose rows record what earlier versions said."""
    return _read(TRD).split("\n## Revision History", 1)[0]


def _section(text: str, heading: str) -> str:
    """The body under the one heading whose title is `heading`, up to the next heading of the
    same or a higher level."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines)
              if re.fullmatch(rf"#+\s+{re.escape(heading)}\s*", line)]
    if len(starts) != 1:
        raise AssertionError(f"{len(starts)} headings titled {heading!r}, expected one")
    level = len(lines[starts[0]].split()[0])
    out = []
    for nxt in lines[starts[0] + 1:]:
        m = re.match(r"^(#+)\s", nxt)
        if m and len(m.group(1)) <= level:
            break
        out.append(nxt)
    return "\n".join(out)


def _units(text: str) -> list[str]:
    """The sentences of `text`'s lines that are not table rows, cut after a `.`, `!` or `?` that
    whitespace follows, then each cell of the rows (lines opening `|`), so that a table is not
    read as one sentence."""
    prose, cells = [], []
    for line in text.splitlines():
        if line.lstrip().startswith("|"):
            cells.extend(c.strip() for c in line.strip().strip("|").split("|"))
        else:
            prose.append(line)
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(" ".join(prose).split()))
    return [u for u in sentences + cells if u]


def _clauses(unit: str) -> list[str]:
    """`unit` cut at each `_CLAUSE_CUT_RE` match that falls outside a code span."""
    out = [""]
    for i, part in enumerate(re.split(r"(`[^`]*`)", unit)):
        pieces = [part] if i % 2 else _CLAUSE_CUT_RE.split(part)
        out[-1] += pieces[0]
        out.extend(pieces[1:])
    return [c.strip() for c in out if c.strip()]


def _names(text: str, type_: str) -> bool:
    """Whether `text` holds `type_` as a word, or its plural (a final `y` as `ies`, otherwise an
    added `s`), in any case."""
    stem = (re.escape(type_[:-1]) + "(?:y|ies)" if type_.endswith("y")
            else re.escape(type_) + "s?")
    return re.search(rf"\b{stem}\b", text, re.I) is not None


def _narrower_than(text: str, types: set[str]) -> list[str]:
    """Each sentence or table cell of `text` (`_units`), and each clause of one (`_clauses`),
    that speaks of executing a `Verify:` line (`_EXECUTING_RE` and `_VERIF_RE`) and names some of
    `types` but not all of them (`_names`). It reads which types are named, not what is said of
    each: a clause that names every type passes whatever it says of them, and a sentence that
    names none passes too."""
    out = []
    for unit in _units(text):
        for piece in dict.fromkeys([unit, *_clauses(unit)]):
            named = {t for t in types if _names(piece, t)}
            if (named and named != types and _EXECUTING_RE.search(piece)
                    and _VERIF_RE.search(piece)):
                out.append(piece)
    return out


def _calls_it_the_authority(sentence: str, name: str) -> bool:
    """Whether `sentence` runs from `name` to `_THE_AUTHORITY`, or from that phrase to `name`,
    through text `_GAP` allows."""
    n = re.escape(name)
    return re.search(rf"{n}{_GAP}{_THE_AUTHORITY}|{_THE_AUTHORITY}{_GAP}{n}", sentence) is not None


def _tables(text: str) -> list[list[list[str]]]:
    """Each markdown table in `text`, as rows of stripped cells: header first, rule dropped."""
    tables, rows = [], []
    for line in text.splitlines() + [""]:
        if line.lstrip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif rows:
            tables.append(rows)
            rows = []
    return tables


def _comment_above(path: Path, anchor: str) -> str:
    """The run of `#` comment lines directly above the one line of `path` opening `anchor`."""
    lines = _read(path).splitlines()
    at = [i for i, line in enumerate(lines) if line.strip().startswith(anchor)]
    if len(at) != 1:
        raise AssertionError(f"{len(at)} lines of {path.name} open {anchor!r}, expected one")
    out = []
    for line in reversed(lines[:at[0]]):
        if not line.strip().startswith("#"):
            break
        out.append(line.strip().lstrip("#").strip())
    if not out:
        raise AssertionError(f"no comment above {anchor!r} in {path.name}")
    return "\n".join(reversed(out))


def _refusing_types() -> set[str]:
    """The types in `sdlc_md.ARTIFACT_TYPES` whose creation refuses a command-shaped `Verify:`,
    read from the refusal `file_finding.py` and `artifact.py` both call."""
    refused = set()
    for type_ in sdlc_md.ARTIFACT_TYPES:
        try:
            file_finding.check_prose_acs(type_, {"acs": [COMMAND_SHAPED]})
        except ValueError:
            refused.add(type_)
    return refused


class TrdVerifierAuthorityTests(unittest.TestCase):
    """US1099: the TRD and the code comments name `sdlc_md.EXECUTES_VERIFIERS`."""

    def setUp(self) -> None:
        self.assertTrue(hasattr(sdlc_md, AUTHORITY), f"sdlc_md defines no {AUTHORITY}")
        self.executes = set(getattr(sdlc_md, AUTHORITY))
        self.assertIn("story", self.executes)

    def test_the_refusal_is_read_by_command_shape(self) -> None:
        """Mutant: the derived refusing set taken from a check that refuses every criterion, or
        none. The outcome-shaped control is refused for no type; the command-shaped one for cr."""
        for type_ in sdlc_md.ARTIFACT_TYPES:
            with self.subTest(type_=type_):
                file_finding.check_prose_acs(type_, {"acs": [OUTCOME_SHAPED]})
        refused = _refusing_types()
        self.assertIn("cr", refused)
        self.assertEqual(set(), refused & self.executes)

    def test_the_trd_names_the_executing_types(self) -> None:
        """Mutants: no sentence or table cell of the section naming `sdlc_md.EXECUTES_VERIFIERS`
        and calling it the authority, as `_calls_it_the_authority` reads one; a type added to
        `EXECUTES_VERIFIERS` that the TRD's table does not give as executed; a type the creators
        refuse that the table does not give as refused; a table row with any other verdict; a
        sentence, cell or clause of the TRD outside its Revision History that `_narrower_than`
        finds naming some of the executing types and not all."""
        section, name = _section(_trd_body(), "Acceptance criteria"), f"`sdlc_md.{AUTHORITY}`"
        self.assertTrue(any(_calls_it_the_authority(s, name) for s in _units(section)),
                        f"no sentence or cell of the section names {name} and calls it the authority")
        tables = [t for t in _tables(section) if t[0][0] == "Type"]
        self.assertEqual(1, len(tables), "expected one table headed Type in the section")
        verdicts = {row[0].strip("`"): row[1] for row in tables[0][1:]}
        refused = _refusing_types()
        self.assertIn("cr", refused)
        self.assertEqual(self.executes, {t for t, v in verdicts.items() if v == EXECUTED})
        self.assertEqual(refused, {t for t, v in verdicts.items() if v == REFUSED})
        self.assertEqual(self.executes | refused, set(verdicts))
        self.assertEqual([], _narrower_than(_trd_body(), self.executes))

    def test_the_code_comments_name_the_set(self) -> None:
        """Mutant: either comment reverted to the story-only wording, or no longer naming the
        set: the pseudo-Verify comment above `_VERIFY_LEAD_RE` in `file_finding.py`, and the one
        above `artifact.py`'s create-path call to the shared refusal."""
        for path, anchor in ((FILE_FINDING, "_VERIFY_LEAD_RE = "),
                             (ARTIFACT, "file_finding.check_prose_acs(type_, f)")):
            comment = _comment_above(path, anchor)
            with self.subTest(path=path.name):
                self.assertIn(f"`sdlc_md.{AUTHORITY}`", comment)
                self.assertEqual([], _narrower_than(comment, self.executes))

    def test_the_filer_s_refusal_names_the_executing_types(self) -> None:
        """Mutant: the refusal `file_finding.py file` prints reverted to saying verify_ac runs
        only a story's line, or no longer naming the set or one of its types."""
        for type_ in sorted(_refusing_types()):
            err = io.StringIO()
            with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(err), \
                    contextlib.redirect_stdout(io.StringIO()):
                (Path(d) / "sdlc-studio").mkdir()
                rc = file_finding.main(["--root", d, "file", "--type", type_, "--title", "A thing",
                                        "--summary", "s", "--priority", "High", "--option", "a",
                                        "--ac", COMMAND_SHAPED])
            with self.subTest(type_=type_):
                self.assertNotEqual(0, rc)
                why = next(line for line in err.getvalue().splitlines() if "Why:" in line)
                self.assertIn(f"`sdlc_md.{AUTHORITY}`", why)
                for member in self.executes:
                    self.assertRegex(why, rf"\b{re.escape(member)}\b")
                self.assertEqual([], _narrower_than(why, self.executes))


def _git(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *argv], capture_output=True, text=True)


def _tracked(*pathspec: str) -> list[str]:
    """The files git tracks under `pathspec`, repo-relative."""
    out = _git("ls-files", "-z", "--", *pathspec)
    if out.returncode:
        raise AssertionError(f"git ls-files failed: {out.stderr}")
    return [f for f in out.stdout.split("\0") if f]


def _ignored(path: str) -> bool:
    """Whether git ignores `path`, read from the ignore rules alone."""
    return _git("check-ignore", "-q", "--no-index", path).returncode == 0


def _one_table(section: str, first: str) -> list[list[str]]:
    """The one table in `section` whose header's first cell is `first`."""
    tables = [t for t in _tables(section) if t[0][0] == first]
    if len(tables) != 1:
        raise AssertionError(f"{len(tables)} tables headed {first!r}, expected one")
    return tables[0]


def _spans(cell: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", cell))


def _sprint_verbs_reaching(target: str) -> set[str]:
    """The `sprint.py` verbs whose handler calls `run_state.<target>`, in its own body or in a
    function of `sprint.py` that it, or one such function, calls by name."""
    tree = ast.parse(_read(SCRIPTS / "sprint.py"))
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}

    def reaches(name: str, seen: set[str]) -> bool:
        if name in seen or name not in funcs:
            return False
        seen.add(name)
        for c in ast.walk(funcs[name]):
            f = getattr(c, "func", None)
            if (isinstance(f, ast.Attribute) and f.attr == target
                    and isinstance(f.value, ast.Name) and f.value.id == "run_state"):
                return True
            if isinstance(f, ast.Name) and reaches(f.id, seen):
                return True
        return False

    return {verb for verb, p in _sprint_verbs().items()
            if (fn := p.get_default("func")) is not None and reaches(fn.__name__, set())}


def _sprint_verbs() -> dict[str, argparse.ArgumentParser]:
    parser = sprint.build_parser()
    return next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction)).choices


class TrdStorageTests(unittest.TestCase):
    """US1100: the storage sections list the committed records and the run's state and lifecycle,
    each read from the code that writes it."""

    def test_every_committed_record_is_listed(self) -> None:
        """Mutants: a record the code writes and git tracks dropped from the table, or listed at
        another path; a tracked file under the evidence or report directories that no listed path
        matches; a listed path that tracks no file. The set is read from the writers' code: the
        actuals and forecast shards, the lessons store, the verdict log of each `critic.PHASES`
        phase, the self-check log, the reports and the run records."""
        section = _section(_trd_body(), "Committed evidence and records")
        table = _one_table(section, "Record")
        col = table[0].index("Path")
        listed = set().union(*(_spans(row[col]) for row in table[1:]))
        report_dir = sprint_report.report_dir("")
        expected = {p.as_posix() for p in (
            telemetry.actuals_path("", "*"), telemetry.forecasts_path("", "*"),
            lessons.store_path(""), critic.self_checks_path(""),
            *(critic.verdicts_path("", phase) for phase in critic.PHASES),
            report_dir / f"{sdlc_md.META_TYPES['report'][1]}*.json",
            run_state.tracked_path("", "*"))}
        self.assertIn("sdlc-studio/lessons.jsonl", expected)
        self.assertEqual(sdlc_md.META_TYPES["report"][0], report_dir.as_posix())
        tracked = _tracked("sdlc-studio")
        for pattern in sorted(expected):
            with self.subTest(record=pattern):
                self.assertTrue(fnmatch.filter(tracked, pattern), f"git tracks no {pattern}")
                self.assertIn(pattern, listed)
        # The reports directory's `_index.md` is an index registry, which the Storage Strategy
        # table gives its own row.
        self.assertIn("`_index.md`", _section(_trd_body(), "Storage Strategy"))
        swept = [f for f in _tracked(telemetry.EVIDENCE.as_posix(), report_dir.as_posix())
                 if Path(f).name != "_index.md"]
        self.assertTrue(fnmatch.filter(swept, telemetry.actuals_path("", "*").as_posix()))
        for f in swept:
            with self.subTest(tracked=f):
                self.assertTrue(any(fnmatch.fnmatchcase(f, p) for p in listed),
                                f"{f} is committed and no listed path matches it")
        for p in sorted(listed):
            with self.subTest(listed=p):
                self.assertTrue(fnmatch.filter(tracked, p), f"the TRD lists {p}, which tracks nothing")

    def test_the_run_lifecycle_reaches_sign(self) -> None:
        """Mutants: the run state shown as `.local` only (the tracked record dropped, or kept in
        `.local`); a path the TRD gives that `run_state` does not keep; the sign step left out or
        not last, or close not before it; a step naming the tracked record whose `sprint.py` verb
        does not file it, or a verb that files it on a step that does not say so. The paths are
        `run_state`'s, the tiers are git's, and which verbs open the run or file the tracked
        record is read from `sprint.py`'s handlers."""
        body, live = _trd_body(), run_state.REL.as_posix()
        tracked_record = run_state.tracked_path("", "*").as_posix()
        self.assertIn(".local", run_state.REL.parts)
        self.assertNotIn(".local", run_state.TRACKED_REL.parts)
        state = _one_table(_section(body, "Run state"), "Run state")
        path, kept = state[0].index("Path"), state[0].index("Kept in")
        rows = {next(iter(_spans(r[path]))): r[kept] for r in state[1:]}
        self.assertEqual({live, run_state.archive_path("", "*").as_posix(), tracked_record},
                         set(rows))
        for p, where in rows.items():
            with self.subTest(path=p):
                self.assertEqual(where.startswith("`.local`"), _ignored(p), where)
                if not _ignored(p):
                    self.assertEqual("tracked", where)
                    self.assertTrue(_tracked(p), f"git tracks no {p}")

        life = _one_table(_section(body, "The run lifecycle"), "Step")
        cmd, says = life[0].index("Command"), life[0].index("Run state")
        steps = [r[0] for r in life[1:]]
        self.assertEqual(("plan", "sign"), (steps[0], steps[-1]))
        self.assertLess(steps.index("close"), steps.index("sign"))
        verbs = [set(re.findall(r"`sprint\.py ([\w-]+)", r[cmd])) for r in life[1:]]
        openers, filers = _sprint_verbs_reaching("open_run"), _sprint_verbs_reaching("file_tracked")
        self.assertIn("plan", openers)
        self.assertIn("sign", filers)
        for row, named in zip(life[1:], verbs):
            with self.subTest(step=row[0]):
                self.assertLessEqual(named, set(_sprint_verbs()))
                self.assertEqual(bool(named & filers), tracked_record in row[says], row)
        self.assertLessEqual(filers, set().union(*verbs))
        self.assertTrue(verbs[0] & openers and live in life[1][says], life[1])
        self.assertTrue(verbs[-1] & filers, life[-1])


#: The release the TRD's coverage line names and the work on `main` beside it (US1101 AC3),
#: pinned as the criterion names them, as `test_lean_prd_refresh` pins the PRD's: a TRD that
#: moves its baseline moves these with it.
BASELINE, ON_MAIN = "6.1.0", "6.2"
_VERSION_RE = re.compile(r"(?<![\d.])\d+\.\d+\.\d+(?!\.?\d)")
#: The three verdicts the network table's `Under ADR-004` column may give a path.
VIA_GH, EXCEPTION, NOT_GITHUB = "via `gh`", "exception", "not GitHub"
#: The calls a scan reads as opening a connection: by attribute or by bare name.
_CONNECTS = {"urlopen", "HTTPConnection", "HTTPSConnection", "create_connection"}


def _registry(heading: str) -> dict[str, tuple[str, str]]:
    """The one table headed `Type` under `heading`, as {type: (directory, ID prefix)}."""
    table = _one_table(_section(_trd_body(), heading), "Type")
    return {r[0]: (r[1].strip("`"), r[2].strip("`")) for r in table[1:]}


def _adr(text: str, number: str) -> str:
    """The body of the one ADR whose heading opens `ADR-<number>:`."""
    titles = re.findall(rf"^###\s+(ADR-{number}:.*?)\s*$", text, re.M)
    if len(titles) != 1:
        raise AssertionError(f"{len(titles)} ADR-{number} headings, expected one")
    return _section(text, titles[0])


def _shipped_scripts() -> list[Path]:
    """Every `.py` file under the skill's `scripts/`, outside `tests/` and `__pycache__/`."""
    return sorted(p for p in SCRIPTS.rglob("*.py")
                  if not {"tests", "__pycache__"} & set(p.relative_to(SCRIPTS).parts))


def _owners(source: str, hit) -> set[str]:
    """The innermost function holding each node of `source` that `hit` accepts, or `<module>`
    for one outside every function."""
    out: set[str] = set()

    def visit(node: ast.AST, owner: str) -> None:
        for child in ast.iter_child_nodes(node):
            if hit(child):
                out.add(owner)
            inner = (child.name if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                     else owner)
            visit(child, inner)

    visit(ast.parse(source), "<module>")
    return out


def _str(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _runs_gh(node: ast.AST) -> bool:
    """A list or tuple display whose first element is the string `gh`, wherever it stands, or a
    call given `shell=True` and a positional string opening `gh` and whitespace."""
    if isinstance(node, (ast.List, ast.Tuple)):
        return bool(node.elts) and _str(node.elts[0]) == "gh"
    if isinstance(node, ast.Call) and any(k.arg == "shell" and getattr(k.value, "value", None)
                                          is True for k in node.keywords):
        return any(re.match(r"gh\s", _str(a) or "") for a in node.args)
    return False


def _runs_git_fetch(node: ast.AST) -> bool:
    """A call given the string `fetch` as a positional argument, or a list or tuple display
    whose first two elements are the strings `git` and `fetch`."""
    if isinstance(node, ast.Call):
        return any(_str(a) == "fetch" for a in node.args)
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_str(e) for e in node.elts[:2]] == ["git", "fetch"]
    return False


def _connects(node: ast.AST) -> bool:
    """A call of a `_CONNECTS` name, as an attribute (`urllib.request.urlopen`) or bare."""
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    return (f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)) in _CONNECTS


#: A source text no `hit` can match in, read before parsing it: each hit's strings and names
#: stand in the text as written, quoted for a string. A string spelt with escapes is not read.
_PREFILTER = {_runs_gh: re.compile(r"[\"']gh[\s\"']"),
              _runs_git_fetch: re.compile(r"[\"']fetch[\"']"),
              _connects: re.compile(r"\b(?:" + "|".join(sorted(_CONNECTS)) + r")\b")}


def _scan(hit) -> set[tuple[str, str]]:
    """Each (script relative to `scripts/`, function) that `_owners` finds `hit` in, over the
    shipped scripts whose text `_PREFILTER` passes."""
    return {(p.relative_to(SCRIPTS).as_posix(), fn) for p in _shipped_scripts()
            if _PREFILTER[hit].search(src := _read(p)) for fn in _owners(src, hit)}


def _verbs(parser: argparse.ArgumentParser) -> set[str]:
    return set(next(a for a in parser._actions
                    if isinstance(a, argparse._SubParsersAction)).choices)


def _in_tree(span: str) -> bool:
    """Whether a path the TRD names exists: one opening `sdlc-studio/` from the repo root, up to
    any `<placeholder>`, and any other from the skill's `scripts/`."""
    if span.startswith("sdlc-studio/"):
        return (REPO / span.split("<", 1)[0]).exists()
    return (SCRIPTS / span).exists()


class TrdRegistryNetworkTests(unittest.TestCase):
    """US1101: the type registry, the network paths, ADR-003, ADR-004, ADR-009, ADR-012 and the
    coverage line match what 6.2 builds."""

    def test_the_type_registry_matches_the_code(self) -> None:
        """AC1. Mutants: a type of `sdlc_md.ARTIFACT_TYPES` or `META_TYPES` missing from its
        table, or given another directory or prefix; a status of `STATUS_VOCAB` missing from its
        type's row, or out of order; the `META_TYPES` table, or the `charter` row, dropped."""
        self.assertIn("charter", sdlc_md.ARTIFACT_TYPES)
        self.assertIn("report", sdlc_md.META_TYPES)
        self.assertIn("Superseded", sdlc_md.STATUS_VOCAB["epic"])
        self.assertEqual(dict(sdlc_md.ARTIFACT_TYPES),
                         _registry("Artifact type registry (`ARTIFACT_TYPES` in `lib/sdlc_md.py`)"))
        self.assertEqual(dict(sdlc_md.META_TYPES),
                         _registry("Meta artefacts (`META_TYPES` in `lib/sdlc_md.py`)"))
        vocab = _one_table(_section(_trd_body(), "Status vocabulary (`STATUS_VOCAB`)"), "Type")
        self.assertEqual({t: list(v) for t, v in sdlc_md.STATUS_VOCAB.items()},
                         {r[0]: [s.strip() for s in r[1].split(",")] for r in vocab[1:]})

    def test_every_gh_caller_is_listed(self) -> None:
        """AC2. Mutants: a function of a shipped script that calls `gh`, opens a connection or
        fetches from origin and has no row, or a row for a function that no longer does; a
        `gh` row whose command names something else; the version check's row given as anything
        but the ADR-004 exception, or ADR-004's Exception paragraph not naming its script; a
        row naming a function its script does not define. The scanners are checked first on a
        sample: an argv display, a `shell=True` string, and the near misses they must pass."""
        sample = ("import shutil, subprocess\n"
                  "def a(): subprocess.run(['gh', 'run', 'list'])\n"
                  "def b(): cmd = ('gh',)\n"
                  "def c(): subprocess.run('gh api x', shell=True)\n"
                  "def d(): shutil.which('gh')\n"
                  "def e(): subprocess.run('gh api x')\n"
                  "def f():\n    def g(): subprocess.run(['git', 'fetch'])\n"
                  "def h(): run(root, 'fetch', 'origin')\n"
                  "def i(): steps = ('close-down', 'fetch')\n"
                  "def j(): urllib.request.urlopen(r)\n")
        self.assertEqual({"a", "b", "c"}, _owners(sample, _runs_gh))
        self.assertEqual({"g", "h"}, _owners(sample, _runs_git_fetch))
        self.assertEqual({"j"}, _owners(sample, _connects))
        gh, fetch, get = _scan(_runs_gh), _scan(_runs_git_fetch), _scan(_connects)
        self.assertIn(("github_sync.py", "gh"), gh)
        self.assertIn(("sprint.py", "origin_drift"), fetch)
        self.assertIn(("version_check.py", "latest_release"), get)

        table = _one_table(_section(_trd_body(), "Network paths"), "Path")
        script, fn, cmd, adr = (table[0].index(c) for c in
                                ("Script", "Function", "Command or endpoint", "Under ADR-004"))
        rows = {(r[script].strip("`"), r[fn].strip("`")): r for r in table[1:]}
        self.assertEqual(len(table) - 1, len(rows), "a script and function listed twice")
        for verdict, found in ((VIA_GH, gh), (EXCEPTION, get), (NOT_GITHUB, fetch)):
            with self.subTest(verdict=verdict):
                self.assertEqual(found, {k for k, r in rows.items() if r[adr] == verdict})
        self.assertEqual(set(rows), gh | get | fetch)
        for (path, name), row in rows.items():
            with self.subTest(script=path, function=name):
                defs = {n.name for n in ast.walk(ast.parse(_read(SCRIPTS / path)))
                        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
                self.assertIn(name, defs)
                if row[adr] == VIA_GH:
                    self.assertTrue(_spans(row[cmd]))
                    self.assertTrue(all(s.split()[0] == "gh" for s in _spans(row[cmd])), row)
        exception = _adr(_trd_body(), "004").split("**Exception:**", 1)
        self.assertEqual(2, len(exception), "ADR-004 has no Exception paragraph")
        self.assertLessEqual({p for p, _ in get}, _spans(exception[1].split("\n\n", 1)[0]))

    def test_the_adrs_and_header_match_6_2(self) -> None:
        """AC3. Mutants: ADR-012 with no Revision History row dated on or after its acceptance;
        a coverage line naming an older baseline, no 6.2 work on main, or a second baseline; a
        header or coverage line naming another release; ADR-012 naming a path that does not
        exist outside its Not yet built paragraph, or listing one there that now exists;
        ADR-003 not naming `reconcile.py settle`, or the hook not running it; ADR-009 not
        naming a `persona_gen.py` verb or a shipped default seat; a `persona_gen.py` verb
        creating a card that was not there."""
        text, body = _read(TRD), _trd_body()
        self.assertIn(f"## [{BASELINE}]", _read(REPO / "CHANGELOG.md"))
        claims = list(doc_freshness._BASELINE_CLAIM.finditer(body))
        self.assertEqual([BASELINE], [m.group("version") for m in claims])
        coverage = next(u for u in _units(_section(body, "Scope")) if u.startswith("Coverage:"))
        self.assertRegex(coverage, rf"\bv{re.escape(BASELINE)}\b.*?\bplus\b.*?"
                                   rf"\b{re.escape(ON_MAIN)}\b.*?\bmain\b")
        header = text.split("\n---\n", 1)[0]
        self.assertEqual({BASELINE}, set(_VERSION_RE.findall(header + "\n" + coverage)))

        adr12 = _adr(body, "012")
        status = re.search(r"^\*\*Status:\*\*.*$", adr12, re.M).group(0)
        accepted = re.search(r"\d{4}-\d{2}-\d{2}", status).group(0)
        history = _one_table(_section(text, "Revision History"), "Date")
        self.assertTrue([r for r in history[1:] if "ADR-012" in r[2] and r[0] >= accepted],
                        f"no Revision History row names ADR-012 on or after {accepted}")
        pathlike = {s for s in _spans(adr12) if s.startswith("sdlc-studio/") or s.endswith(".py")}
        self.assertIn("persona_gen.py", pathlike)
        parts = adr12.split("**Not yet built:**", 1)
        self.assertEqual(2, len(parts), "ADR-012 has no Not yet built paragraph")
        not_built = _spans(parts[1].split("\n\n", 1)[0])
        for span in sorted(pathlike | not_built):
            with self.subTest(path=span):
                self.assertNotEqual(_in_tree(span), span in not_built)

        adr3 = _adr(body, "003")
        self.assertIn("settle", _verbs(reconcile.build_parser()))
        self.assertIn("`reconcile.py settle`", adr3)
        # A line of the hook that is not a comment runs it.
        self.assertRegex(_read(REPO / ".githooks" / "pre-commit"),
                         re.compile(r'^(?![ \t]*#).*reconcile\.py"? settle\b', re.M))
        named = re.findall(r"`reconcile\.([A-Z_]+)`", adr3)
        self.assertIn("SETTLED_INDEX_KINDS", named)
        for name in named:
            self.assertTrue(hasattr(reconcile, name), name)

        adr9, verbs = _adr(body, "009"), _verbs(persona_gen.build_parser())
        seats = SCRIPTS.parent / "templates" / "personas" / "amigos"
        shipped = {p.name for p in seats.glob("*.md")}
        self.assertIn("stamp", verbs)
        self.assertIn("qa.md", shipped)
        self.assertLessEqual(verbs | shipped | {"templates/personas/amigos/"}, _spans(adr9))
        with tempfile.TemporaryDirectory() as d:
            card = Path(d) / "new.md"
            for verb in sorted(verbs):
                with self.subTest(verb=verb), contextlib.redirect_stdout(io.StringIO()), \
                        contextlib.redirect_stderr(io.StringIO()):
                    with contextlib.suppress(OSError, SystemExit):
                        persona_gen.main([verb, "--file", str(card)])
                    self.assertFalse(card.exists(), f"persona_gen.py {verb} wrote a card")


if __name__ == "__main__":
    unittest.main()
