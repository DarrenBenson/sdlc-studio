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
import functools
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts"
TRD = REPO / "sdlc-studio" / "trd.md"
FILE_FINDING = SCRIPTS / "file_finding.py"
ARTIFACT = SCRIPTS / "artifact.py"

sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import critic  # noqa: E402
import decisions  # noqa: E402
import doc_freshness  # noqa: E402
import evidence_pack  # noqa: E402
import file_finding  # noqa: E402
import gate  # noqa: E402
import gitutil  # noqa: E402 - confined git for the scratch and fixture repositories
import ledger  # noqa: E402
import lessons  # noqa: E402
import persona_gen  # noqa: E402
import persona_memory  # noqa: E402
from test_lean_prd_refresh import release_baseline  # noqa: E402 - the release the specs name
import reconcile  # noqa: E402
import sprint  # noqa: E402
import sprint_report  # noqa: E402
import verify_ac  # noqa: E402
import telemetry  # noqa: E402
from lib import lanes, run_state, sdlc_md  # noqa: E402

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

    #: A passage that widens the allow-list past the `http` verb, naming every or all of the
    #: Verify-line tools or saying the list bounds every, all or any of them, or that says it
    #: bounds only until a project sets it.
    WIDENED = re.compile(r"\b(?:every|all)\b(?:\s+other)?\s+Verify-line tools?\b|"
                         r"\bbounds?\s+(?:every|all|any)\b|\bbounds?\s+only\s+until\b", re.I)

    def test_the_http_allow_list_is_described_as_unset_and_http_only(self) -> None:
        """Mutants: the Network paths prose or the exfiltration row saying a project's
        Verify-line tools are bounded to the hosts the variable names; either dropping `unset by
        default`, the `http` verb or `bounds nothing until`; either widening the list past the
        `http` verb (to every other Verify-line tool, or bounding every one once set); `bounds
        nothing until` turned into `bounds only until`; the code reading a default list."""
        var = "SDLC_VERIFY_HTTP_HOSTS"
        with mock.patch.dict("os.environ", clear=False) as env:
            env.pop(var, None)
            self.assertEqual((), verify_ac._restricted_http_hosts())
            verify_ac._check_http_target("http://example.test/")
            env[var] = "only.test"
            with self.assertRaises(ValueError):
                verify_ac._check_http_target("http://example.test/")
        body = _trd_body()
        prose = next(p for p in _section(body, "Network paths").split("\n\n") if var in p)
        row = next(r for r in _threat_rows() if r[0] == "Network exfiltration")
        for name, text in (("Network paths", prose), ("Network exfiltration", row[3])):
            flat = " ".join(text.split())
            with self.subTest(passage=name):
                self.assertIn(var, flat)
                self.assertIn("unset by default", flat)
                self.assertIn("applies to the `http` verb only", flat)
                self.assertIn("bounds nothing until a project sets it", flat)
                self.assertNotRegex(flat, r"bounded to the hosts|host-bounded by")
                self.assertNotRegex(flat, self.WIDENED)

    def test_the_threat_model_has_a_verify_line_execution_row(self) -> None:
        """Mutants: the row removed; the stamp, `--no-shell` or `--allow-external` left out of
        its control; the limit (self-declared stamp, an absent stamp permits shell) left out; the
        code no longer permitting shell for an absent stamp."""
        text = "# US0001: s\n\n> **Status:** Ready\n"
        self.assertTrue(verify_ac.shell_allowed_for(text), "an absent stamp permits shell")
        external = text + "> **Provenance:** external\n"
        self.assertFalse(verify_ac.shell_allowed_for(external))
        self.assertTrue(verify_ac.shell_allowed_for(external, allow_external=True))
        self.assertFalse(verify_ac.shell_allowed_for(text, allow_shell=False))
        rows = [r for r in _threat_rows() if "Verif" in r[0] and "shell" in r[0]]
        self.assertEqual(1, len(rows), "no Threat Model row for the verifier's shell")
        control = " ".join(rows[0][3].split())
        for named in ("`Provenance: external`", "`--no-shell`", "`--allow-external`"):
            self.assertIn(named, control)
        self.assertIn("self-declared", control)
        self.assertIn("an absent stamp permits shell", control)


def _git(*argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *argv], capture_output=True, text=True)


def _tracked(*pathspec: str) -> list[str]:
    """The files git tracks under `pathspec`, repo-relative."""
    out = _git("ls-files", "-z", "--", *pathspec)
    if out.returncode:
        raise AssertionError(f"git ls-files failed: {out.stderr}")
    return [f for f in out.stdout.split("\0") if f]


def _ignore_files(root: Path) -> list[str]:
    """The `.gitignore` files git tracks in `root`, root-relative."""
    out = gitutil.git(["ls-files", "-z", "--", ":(glob)**/.gitignore"], root, text=True)
    return [f for f in out.stdout.split("\0") if f]


def _ignored(path: str, root: Path = REPO) -> bool:
    """Whether the `.gitignore` files `root` tracks ignore `path`, read from those rules alone.

    Asked in `root` itself, git refuses a path beyond a symbolic link with rc 128, which read as
    "not ignored"; the gate host makes `sdlc-studio/.local` one (`tools/remote-gate.sh`, BG1166).
    So the question goes to a scratch repository holding only those files, copied from `root`'s
    working tree, with no `info/exclude` and no excludes file, so nothing at `path` and no host
    rule has a say."""
    with tempfile.TemporaryDirectory() as d:
        scratch = Path(d)
        gitutil.git(["init", "-q", "--template="], scratch)
        for rel in _ignore_files(root):
            (scratch / rel).parent.mkdir(parents=True, exist_ok=True)
            (scratch / rel).write_bytes((root / rel).read_bytes())
        return gitutil.git(["-c", "core.excludesFile=/dev/null", "check-ignore", "-q",
                            "--no-index", "--", path], scratch, check=False).returncode == 0


def _one_table(section: str, first: str) -> list[list[str]]:
    """The one table in `section` whose header's first cell is `first`."""
    tables = [t for t in _tables(section) if t[0][0] == first]
    if len(tables) != 1:
        raise AssertionError(f"{len(tables)} tables headed {first!r}, expected one")
    return tables[0]


def _spans(cell: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", cell))


def _glob(path: str) -> str:
    """A listed path as a glob: each `<placeholder>` in it stands for any name."""
    return re.sub(r"<[^<>]+>", "*", path)


def decision_stores() -> list[str]:
    """The decision log `decisions.py` appends to and the directory of per-tranche ledgers
    `ledger.py` writes, each read from its writer's code."""
    return [decisions.LOG_REL, ledger.ledger_path("", "x").parent.as_posix()]


def committed_trees() -> list[str]:
    """The directories whose every tracked file a committed record's row must match, each read
    from its writer's code: the evidence shards, the reports, the verdict files a brief issues,
    the persona memory files and the per-tranche decision ledgers."""
    return [telemetry.EVIDENCE.as_posix(), sprint_report.report_dir("").as_posix(),
            critic.VERDICTS_DIR_REL.as_posix(), persona_memory.MEMORY_REL,
            ledger.ledger_path("", "x").parent.as_posix()]


def committed_files() -> list[str]:
    """The single committed files a row must list beside those directories, each read from its
    writer's code: the decision log."""
    return [decisions.LOG_REL]


#: The committed file `critic.py self-check record --mutants-from` keeps a unit's mutants in.
AUTHOR_MUTANTS = (Path("sdlc-studio") / "reviews" / critic.AUTHOR_MUTANTS_DIR
                  / "<id>.json").as_posix()


def unlisted(files: list[str], listed: set[str]) -> list[str]:
    """Each of `files`, other than an `_index.md`, that no listed path matches as a glob."""
    return [f for f in files if Path(f).name != "_index.md"
            and not any(fnmatch.fnmatchcase(f, _glob(p)) for p in listed)]


def _sprint_verbs() -> dict[str, argparse.ArgumentParser]:
    parser = sprint.build_parser()
    return next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction)).choices


@functools.lru_cache(maxsize=None)
def _sprint_funcs() -> dict[str, ast.FunctionDef]:
    tree = ast.parse(_read(SCRIPTS / "sprint.py"))
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def _reaches(nodes, target: str, seen: set[str]) -> bool:
    """Whether a call among `nodes`, or in what they hold, is `run_state.<target>` or a call by
    name to a `sprint.py` function that, by the same rule, reaches it."""
    funcs = _sprint_funcs()
    for node in nodes:
        for c in ast.walk(node):
            f = getattr(c, "func", None)
            if (isinstance(f, ast.Attribute) and f.attr == target
                    and isinstance(f.value, ast.Name) and f.value.id == "run_state"):
                return True
            if isinstance(f, ast.Name) and f.id in funcs and f.id not in seen:
                seen.add(f.id)
                if _reaches([funcs[f.id]], target, seen):
                    return True
    return False


def _flag_read(test: ast.expr) -> str | None:
    """The dest an `if` test reads off `args` and nothing else: `args.x` or `getattr(args, "x"...)`."""
    if isinstance(test, ast.Attribute) and isinstance(test.value, ast.Name) \
            and test.value.id == "args":
        return test.attr
    if (isinstance(test, ast.Call) and isinstance(test.func, ast.Name)
            and test.func.id == "getattr" and len(test.args) >= 2
            and isinstance(test.args[0], ast.Name) and test.args[0].id == "args"
            and isinstance(test.args[1], ast.Constant)):
        return test.args[1].value
    return None


@functools.lru_cache(maxsize=None)
def _routes() -> dict[tuple[str, str | None], tuple[ast.AST, ...]]:
    """BG1163: each route through a `sprint.py` verb, to the statements it runs. A verb's handler
    has a route per `if args.<flag>:` branch that ends in a `return`, keyed `(verb, '--flag')`,
    and its plain route `(verb, None)`: the calls it makes outside those branches."""
    funcs, out = _sprint_funcs(), {}
    for verb, parser in _sprint_verbs().items():
        fn = parser.get_default("func")
        if fn is None or fn.__name__ not in funcs:
            continue
        handler = funcs[fn.__name__]
        options = {a.dest: max(a.option_strings, key=len)
                   for a in parser._actions if a.option_strings}
        branched: set[int] = set()
        for node in ast.walk(handler):
            if (isinstance(node, ast.If) and (dest := _flag_read(node.test)) in options
                    and isinstance(node.body[-1], ast.Return)):
                out[(verb, options[dest])] = tuple(node.body)
                branched |= {id(n) for b in node.body for n in ast.walk(b)}
        out[(verb, None)] = tuple(n for n in ast.walk(handler)
                                  if isinstance(n, ast.Call) and id(n) not in branched)
    return out


def _routes_reaching(target: str) -> set[tuple[str, str | None]]:
    """The routes `_routes` reads whose statements reach `run_state.<target>` (`_reaches`)."""
    return {route for route, nodes in _routes().items() if _reaches(nodes, target, set())}


#: A backticked `sprint.py` command, its verb and the words after it.
_SPRINT_COMMAND_RE = re.compile(r"`sprint\.py ([\w-]+)([^`]*)`")


def _named_routes(text: str) -> set[tuple[str, str | None]]:
    """The routes `text` names: a backticked `sprint.py <verb>` names `(verb, '--flag')` for each
    route flag it carries, and the plain `(verb, None)` when it carries none."""
    out = set()
    for verb, rest in _SPRINT_COMMAND_RE.findall(text):
        flags = {f for f in rest.split() if (verb, f) in _routes()}
        out |= {(verb, f) for f in flags} or {(verb, None)}
    return out


def _strict_stop_follows_the_close(source: str) -> bool:
    """BG1163 r2: whether `cmd_boundary` in `source` reads its `--strict` branch only below every
    `run_state.close_run` it makes, so a drift stop meets a record the cycle's close has closed
    and `_boundary_stop`, which closes only a record still running, leaves its outcome."""
    fn = next(n for n in ast.parse(source).body
              if isinstance(n, ast.FunctionDef) and n.name == "cmd_boundary")
    closes = [c.lineno for c in ast.walk(fn) if isinstance(c, ast.Call)
              and isinstance(c.func, ast.Attribute) and c.func.attr == "close_run"]
    strict = [n.lineno for n in ast.walk(fn)
              if isinstance(n, ast.If) and _flag_read(n.test) == "strict"]
    return bool(closes and strict) and max(closes) < min(strict)


def _unnamed_close_routes(body: str) -> set[tuple[str, str | None]]:
    """The routes reaching `run_state.close_run` that the TRD's run lifecycle does not name."""
    return _routes_reaching("close_run") - _named_routes(_section(body, "The run lifecycle"))


#: BG1163: each Run state row by its label, to the `run_state` path it must give.
_RUN_STATE_LABELS = {"Live record": run_state.REL.as_posix(),
                     "Archive": run_state.archive_path("", "*").as_posix(),
                     "Tracked record": run_state.tracked_path("", "*").as_posix()}


def _run_state_failures(body: str) -> list[str]:
    """One line per Run state row that is missing, gives another path than `run_state` keeps for
    its label, or a tier git's ignore rules contradict; the tracked one must track a file."""
    state = _one_table(_section(body, "Run state"), "Run state")
    path, kept = state[0].index("Path"), state[0].index("Kept in")
    rows = {r[0]: (sorted(_spans(r[path])), r[kept]) for r in state[1:]}
    out = [f"the table has a row {label!r}, which `run_state` keeps no path for"
           for label in sorted(set(rows) - set(_RUN_STATE_LABELS))]
    for label, p in _RUN_STATE_LABELS.items():
        spans, where = rows.get(label, ([], ""))
        if spans != [p]:
            out.append(f"{label}: the TRD gives {spans or 'no row'}, `run_state` keeps {p}")
        elif where.startswith("`.local`") != _ignored(p):
            out.append(f"{label}: kept in {where!r}, which git's ignore rules contradict")
        elif not _ignored(p) and (where != "tracked" or not _tracked(p)):
            out.append(f"{label}: kept in {where!r} and git tracks {len(_tracked(p))} file(s)")
    return out


class TrdStorageTests(unittest.TestCase):
    """US1100: the storage sections list the committed records and the run's state and lifecycle,
    each read from the code that writes it."""

    def test_every_committed_record_is_listed(self) -> None:
        """Mutants: a record the code writes and git tracks dropped from the table, or listed at
        another path; a tracked file under the evidence, report, verdict-file or persona memory
        directories that no listed path matches; a listed path that tracks no file, other than a
        record the code writes and this repository holds none of yet. The set is read from the
        writers' code: the actuals and forecast shards, the lessons store, the verdict log of each
        `critic.PHASES` phase, the verdict files a brief issues, the self-check log, the reports,
        the run records, and the persona memory files and a release's evidence pack. A listed
        path's `<placeholder>` matches any name."""
        section = _section(_trd_body(), "Committed evidence and records")
        table = _one_table(section, "Record")
        col = table[0].index("Path")
        listed = set().union(*(_spans(row[col]) for row in table[1:]))
        report_dir = sprint_report.report_dir("")
        expected = {p.as_posix() for p in (
            telemetry.actuals_path("", "*"), telemetry.forecasts_path("", "*"),
            lessons.store_path(""), critic.self_checks_path(""),
            *(critic.verdicts_path("", phase) for phase in critic.PHASES),
            critic.VERDICTS_DIR_REL / "<unit>" / "<fp>-<token>.txt",
            report_dir / f"{sdlc_md.META_TYPES['report'][1]}*.json",
            run_state.tracked_path("", "*"))}
        # Records the code writes that need not be tracked yet: no learning has been recorded and
        # no release's pack written here, so each is held to its row and not to a tracked file.
        pending = {persona_memory.memory_path("", "<persona>").as_posix(),
                   evidence_pack.pack_rel("<version>"), AUTHOR_MUTANTS}
        self.assertIn("sdlc-studio/lessons.jsonl", expected)
        self.assertEqual(sdlc_md.META_TYPES["report"][0], report_dir.as_posix())
        tracked = _tracked("sdlc-studio")
        for pattern in sorted(expected):
            with self.subTest(record=pattern):
                self.assertTrue(fnmatch.filter(tracked, _glob(pattern)), f"git tracks no {pattern}")
                self.assertIn(pattern, listed)
        for pattern in sorted(pending):
            with self.subTest(record=pattern):
                self.assertIn(pattern, listed)
        # The reports directory's `_index.md` is an index registry, which the Storage Strategy
        # table gives its own row.
        self.assertIn("`_index.md`", _section(_trd_body(), "Storage Strategy"))
        swept = _tracked(*committed_trees(), *committed_files())
        self.assertTrue(fnmatch.filter(swept, telemetry.actuals_path("", "*").as_posix()))
        self.assertTrue(fnmatch.filter(swept, f"{critic.VERDICTS_DIR_REL.as_posix()}/*"))
        for f in unlisted(swept, listed):
            with self.subTest(tracked=f):
                self.fail(f"{f} is committed and no listed path matches it")
        for p in sorted(listed - pending):
            with self.subTest(listed=p):
                self.assertTrue(fnmatch.filter(tracked, _glob(p)),
                                f"the TRD lists {p}, which tracks nothing")

    def _records(self) -> tuple[list[str], list[list[str]]]:
        table = _one_table(_section(_trd_body(), "Committed evidence and records"), "Record")
        return table[0], table[1:]

    def _row(self, path: str) -> dict[str, str]:
        """The one row of the committed records table listing `path`, by column name."""
        header, rows = self._records()
        found = [r for r in rows if path in _spans(r[header.index("Path")])]
        self.assertEqual(1, len(found), f"{len(found)} rows list {path}")
        return dict(zip(header, found[0]))

    def test_both_decision_stores_are_listed_with_their_writers(self) -> None:
        """BG1556 AC1. Mutants: either store's row dropped; the log credited to `ledger.py` or
        the per-tranche ledger to `decisions.py`; a row with no purpose."""
        log = self._row(decisions.LOG_REL)
        tranche = self._row(ledger.ledger_path("", "<tranche>").as_posix())
        self.assertEqual({"decisions.py"}, {s for s in _spans(log["Writer"]) if s.endswith(".py")})
        self.assertEqual({"ledger.py"}, {s for s in _spans(tranche["Writer"])
                                         if s.endswith(".py")})
        for row in (log, tranche):
            with self.subTest(record=row["Record"]):
                self.assertGreater(len(row["Purpose"].split()), 8, row["Purpose"])

    def test_every_tracked_decision_file_matches_a_listed_path(self) -> None:
        """BG1556 AC2. Mutants: the decision stores left out of the swept paths (exempt by
        enumeration); a tracked decision file no listed path matches."""
        stores = decision_stores()
        self.assertLessEqual(set(stores), set(committed_trees()) | set(committed_files()))
        tracked = _tracked(*stores)
        self.assertIn(decisions.LOG_REL, tracked, "premise: git tracks the decision log")
        self.assertTrue([f for f in tracked if f.startswith(stores[1] + "/")],
                        "premise: git tracks a per-tranche ledger")
        header, rows = self._records()
        listed = set().union(*(_spans(r[header.index("Path")]) for r in rows))
        self.assertEqual([], unlisted(tracked, listed))
        self.assertEqual(["sdlc-studio/decisions.json"],
                         unlisted(["sdlc-studio/decisions.json", "sdlc-studio/decisions/T1.md"],
                                  listed), "premise: a file beside the stores is not listed")

    def test_rule_five_names_each_script_with_its_own_store(self) -> None:
        """BG1556 AC3. Mutants: `decisions.py` credited with the per-tranche ledger, or
        `ledger.py` with the log; `ledger.py` dropped from the write surface."""
        contract = " ".join(_section(_trd_body(), "Script CLI contract").split())
        rule5 = contract.split(" 5. ", 1)[1].split(" 6. ", 1)[0]
        clauses = re.split(r";\s*", rule5)
        log = [c for c in clauses if "`decisions.py`" in c]
        tranche = [c for c in clauses if "`ledger.py" in c]
        self.assertEqual(1, len(log), "rule 5 names `decisions.py` in one clause")
        self.assertEqual(1, len(tranche), "rule 5 names `ledger.py` in one clause")
        self.assertIn(f"`{decisions.LOG_REL}`", log[0])
        self.assertNotIn("`sdlc-studio/decisions/", log[0])
        self.assertIn(f"`{ledger.ledger_path('', '<tranche>').as_posix()}`", tranche[0])
        self.assertNotIn(f"`{decisions.LOG_REL}`", tranche[0])

    def test_the_committed_records_table_lists_the_author_mutant_lists(self) -> None:
        """BG1621 AC1. Mutants: the row dropped, or at another path than the code keeps the list
        at; its writer not naming `--mutants-from`; its purpose not naming the QA brief's replay."""
        self.assertEqual(Path(AUTHOR_MUTANTS).parent,
                         critic.author_mutants_path("", "US0001").parent)
        self.assertEqual(".json", critic.author_mutants_path("", "US0001").suffix)
        row = self._row(AUTHOR_MUTANTS)
        self.assertIn("`critic.py self-check record --mutants-from`", row["Writer"])
        purpose = " ".join(row["Purpose"].split())
        self.assertRegex(purpose, r"QA brief")
        self.assertRegex(purpose, r"replays? the author's mutants")

    def test_a_shared_file_is_defined_and_every_exception_is_listed(self) -> None:
        """Mutants: the definition of a shared file dropped from rule 5 or from the scripts row
        of the component table; the ledgers called the one exception again; a script the
        shared-file sweep lets rewrite a tracked file whole (`SHARED_WRITE_ALLOWLIST`, kind
        outside, or `NOT_YET_MOVED`) left off rule 5's list of exceptions, a listed script that
        is no such writer, or an exception listed with no reason; the not-yet-moved bullet
        naming a script or function `NOT_YET_MOVED` does not, or leaving one out; the sweep's
        sentence naming fewer call forms than it sees."""
        from test_confinement import (  # noqa: PLC0415
            NOT_YET_MOVED, OUTSIDE, SHARED_WRITE_ALLOWLIST)
        body = _trd_body()
        rule5 = _section(body, "Script CLI contract").split("\n5. ", 1)[1].split("\n6. ", 1)[0]
        flat = " ".join(rule5.split())
        self.assertRegex(flat, r"A shared file is any tracked workspace file a script rewrites "
                               r"whole\.")
        self.assertNotRegex(flat, r"(?i)\bone (?:deliberate )?exception\b")
        row = " ".join(next(line for line in body.splitlines()
                            if line.startswith("| `scripts/`")).split())
        self.assertRegex(row, r"shared files \(any tracked workspace file a script rewrites "
                              r"whole; §5 rule 5 lists the writers left outside\)")
        bullets = [" ".join(b.split())
                   for b in re.findall(r"^ {3}- (.*(?:\n {5}\S.*)*)", rule5, re.M)]
        self.assertTrue([b for b in bullets if "`O_APPEND`" in b],
                        "the append-only ledgers are listed among the exceptions")
        listed: dict[str, str] = {}
        for bullet in bullets:
            head, sep, reason = bullet.partition(": ")
            for script in re.findall(r"`([a-z0-9_]+\.py)\b", head):
                listed[script] = reason if sep else ""
        outside = {site.split("::", 1)[0] for site, (kind, _why) in SHARED_WRITE_ALLOWLIST.items()
                   if kind == OUTSIDE}
        moving = {site.split("::", 1)[0] for site in NOT_YET_MOVED}
        self.assertGreater(len(outside), 3, "premise: the sweep names writers left outside")
        self.assertEqual(sorted(listed), sorted(outside | moving))
        pending = [b for b in bullets if "not yet moved" in b.partition(": ")[2]]
        self.assertEqual(len(pending), 1, "one bullet lists the writers not yet moved")
        head = pending[0].partition(": ")[0]
        self.assertEqual(sorted(set(re.findall(r"`([a-z0-9_]+\.py)\b", head))), sorted(moving))
        for site in NOT_YET_MOVED:
            with self.subTest(not_yet_moved=site):
                self.assertIn(f"`{site.split('::')[1]}`", head)
        self.assertRegex(flat, r"names every `write_text` and `write_bytes` call, and every "
                               r"`open` given a literal mode holding `w`")
        for script, reason in sorted(listed.items()):
            with self.subTest(script=script):
                self.assertGreaterEqual(len(reason.split()), 5, f"{script} carries no reason")

    def test_the_run_lifecycle_reaches_sign(self) -> None:
        """Mutants: the run state shown as `.local` only (the tracked record dropped, or kept in
        `.local`); a path the TRD gives that `run_state` does not keep; the sign step left out or
        not last, or close not before it; a step naming the tracked record whose `sprint.py`
        route does not file it, or a route that files it on a step that does not say so. The
        paths are `run_state`'s, the tiers are git's, and which routes open the run or file the
        tracked record is read from `sprint.py`'s handlers. BG1163 reads the routes a flag branch
        takes (`close --file-and-close` files none), and the Run state rows by label."""
        body, live = _trd_body(), run_state.REL.as_posix()
        tracked_record = run_state.tracked_path("", "*").as_posix()
        self.assertIn(".local", run_state.REL.parts)
        self.assertNotIn(".local", run_state.TRACKED_REL.parts)
        self.assertEqual([], _run_state_failures(body))

        life = _one_table(_section(body, "The run lifecycle"), "Step")
        cmd, says = life[0].index("Command"), life[0].index("Run state")
        steps = [r[0] for r in life[1:]]
        self.assertEqual(("plan", "sign"), (steps[0], steps[-1]))
        self.assertLess(steps.index("close"), steps.index("sign"))
        routes = [_named_routes(r[cmd]) for r in life[1:]]
        openers, filers = _routes_reaching("open_run"), _routes_reaching("file_tracked")
        self.assertIn(("plan", None), openers)
        self.assertIn(("sign", None), filers)
        self.assertNotIn(("close", "--file-and-close"), filers)
        for row, named in zip(life[1:], routes):
            with self.subTest(step=row[0]):
                self.assertLessEqual({verb for verb, _ in named}, set(_sprint_verbs()))
                self.assertEqual(bool(named & filers), tracked_record in row[says], row)
        self.assertLessEqual(filers, set().union(*routes))
        self.assertTrue(routes[0] & openers and live in life[1][says], life[1])
        self.assertTrue(routes[-1] & filers, life[-1])

    def test_every_close_route_reaching_close_run_is_named_in_the_lifecycle(self) -> None:
        """BG1163 AC1. The lifecycle showed only the route that ends in a signature, and its close
        row said the close files the tracked record, which `close --file-and-close` returns
        before doing; `stop` and `boundary` close the run too. MUTANTS: drop the stop row, or
        `--file-and-close` from its row, or the boundary note; read the routes by verb alone, so
        `sprint.py close` names the file-and-close exit. The control is the TRD as committed; then
        each route's naming spans are taken out, alone, and the check names that route."""
        routes = _routes_reaching("close_run")
        self.assertLessEqual({("stop", None), ("close", "--file-and-close"), ("close", None),
                              ("sign", None), ("boundary", None)}, routes,
                             "premise: the close routes moved in sprint.py")
        body = _trd_body()
        self.assertEqual(set(), _unnamed_close_routes(body))
        for verb, flag in sorted(routes, key=str):
            with self.subTest(route=(verb, flag)):
                pruned = _SPRINT_COMMAND_RE.sub(
                    lambda m: "" if _named_routes(m.group(0)) == {(verb, flag)} else m.group(0),
                    body)
                self.assertNotEqual(body, pruned)
                self.assertEqual({(verb, flag)}, _unnamed_close_routes(pruned))
        # What each files: a lifecycle row naming a close route that files no tracked record
        # says so, beside the route-level tracked-path check above.
        life = _one_table(_section(body, "The run lifecycle"), "Step")
        cmd, says = life[0].index("Command"), life[0].index("Run state")
        quiet = routes - _routes_reaching("file_tracked")
        rows = [r for r in life[1:] if _named_routes(r[cmd]) & quiet]
        self.assertEqual({"stop", "file and close"}, {r[0] for r in rows})
        for row in rows:
            with self.subTest(step=row[0]):
                self.assertIn("creates no tracked record", row[says])

    def test_swapped_live_and_tracked_labels_fail(self) -> None:
        """BG1163 AC3. The Run state rows were keyed by path and their label never read, so the
        Live and Tracked labels could swap with every test green. MUTANT: `_run_state_failures`
        keying the rows by path alone. The control is the TRD as committed."""
        body = _trd_body()
        self.assertEqual([], _run_state_failures(body))
        swapped = (body.replace("| Live record |", "| @@swap@@ |")
                   .replace("| Tracked record |", "| Live record |")
                   .replace("| @@swap@@ |", "| Tracked record |"))
        self.assertIn(f"| Tracked record | `{run_state.REL.as_posix()}` |", swapped,
                      "premise: the swap missed the Live record row")
        failures = _run_state_failures(swapped)
        for label in ("Live record", "Tracked record"):
            with self.subTest(label=label):
                self.assertTrue(any(f.startswith(f"{label}: ") for f in failures), failures)

    def test_a_strict_drift_stop_keeps_the_cycle_close_outcome(self) -> None:
        """BG1163 r2. The fragment said origin drift under `--strict` ends the run `blocked`;
        the drift check runs after the cycle's close has closed the record, so the run keeps
        that close's outcome, and the TRD says a stop closes `blocked` only a record still
        running. MUTANT: the `--strict` branch read above the cycle's `close_run`. The control
        is `sprint.py`; the near miss a handler checking drift first."""
        self.assertTrue(_strict_stop_follows_the_close(_read(SCRIPTS / "sprint.py")))
        first = ("def cmd_boundary(args):\n"
                 "    if getattr(args, 'strict', False):\n"
                 "        return _boundary_stop(root, 'origin-drift', '', '')\n"
                 "    run_state.close_run(root, run_state.STOPPED)\n")
        self.assertFalse(_strict_stop_follows_the_close(first))
        self.assertIn("closing a record still running `blocked`",
                      " ".join(_section(_trd_body(), "The run lifecycle").split()))

    def test_the_tier_does_not_depend_on_what_local_is(self) -> None:
        """BG1166. Each Run state path gets the same tier from `_ignored` whether `.local` is a
        symlink, as the gate host makes it, a directory or absent: ignored inside `.local`, not
        ignored outside it. Mutants: `_ignored` asks git in the checkout, where the symlink draws
        rc 128 and its two `.local` paths read as not ignored; or it lets the host's excludes
        file speak, which here ignores every `.json`. Each fixture tracks this repository's
        `.gitignore` files, and its symlink is shown to draw that refusal, so the case is the
        gate host's."""
        paths = (run_state.REL.as_posix(), run_state.archive_path("", "*").as_posix(),
                 run_state.tracked_path("", "*").as_posix())
        with tempfile.TemporaryDirectory() as host, \
                mock.patch.dict("os.environ", {"XDG_CONFIG_HOME": host}):
            (Path(host) / "git").mkdir()
            (Path(host) / "git" / "ignore").write_text("*.json\n", encoding="utf-8")
            for shape in ("symlink", "directory", "absent"):
                with tempfile.TemporaryDirectory() as d:
                    root = self._checkout(Path(d), shape)
                    for p in paths:
                        with self.subTest(local=shape, path=p):
                            self.assertEqual(".local" in Path(p).parts, _ignored(p, root))

    def _checkout(self, d: Path, shape: str) -> Path:
        """A repository under `d` tracking this one's `.gitignore` files, its `.local` given
        `shape` and, unless absent, holding a run state file."""
        root, state, local = d / "clone", d / "state", run_state.REL.parent
        rules = _ignore_files(REPO)
        self.assertIn(f"{local.parent.as_posix()}/.gitignore", rules)
        gitutil.git(["init", "-q", str(root)], d)
        for rel in rules:
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_bytes((REPO / rel).read_bytes())
        gitutil.git(["add", "--", *rules], root)
        if shape == "symlink":
            state.mkdir()
            (root / local).symlink_to(state, target_is_directory=True)
            refused = gitutil.git(["check-ignore", "-q", "--no-index", "--",
                                   run_state.REL.as_posix()], root, check=False, text=True)
            self.assertEqual(128, refused.returncode)
            self.assertIn("beyond a symbolic link", refused.stderr)
        elif shape == "directory":
            (root / local).mkdir()
        if shape != "absent":
            (root / run_state.REL).write_text("{}\n", encoding="utf-8")
        return root


#: The release the TRD's coverage line names and the work on `main` beside it (US1101 AC3), read
#: from package.json as `test_lean_prd_refresh` reads the PRD's (US1111): a cut that moves the
#: version moves these with it.
BASELINE, ON_MAIN = release_baseline()
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

    tree = ast.parse(source)
    if hit is _connects:
        hit = functools.partial(_connects, openers=_openers(tree))
    visit(tree, "<module>")
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


def _callee(node: ast.AST) -> str | None:
    """The name a call calls, as an attribute (`urllib.request.urlopen`) or bare."""
    f = node.func if isinstance(node, ast.Call) else None
    return f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)


def _openers(tree: ast.AST) -> frozenset[str]:
    """US1138: each name an assignment binds to a `build_opener(...)` call, the opener
    `lib/meter_cursor.py` refuses redirects through."""
    return frozenset(t.id for n in ast.walk(tree) if isinstance(n, (ast.Assign, ast.AnnAssign))
                     and _callee(n.value) == "build_opener"
                     for t in (n.targets if isinstance(n, ast.Assign) else [n.target])
                     if isinstance(t, ast.Name))


def _connects(node: ast.AST, openers: frozenset[str] = frozenset()) -> bool:
    """A call of a `_CONNECTS` name, as an attribute (`urllib.request.urlopen`) or bare, or an
    opener's `.open(...)`: on a name in `openers`, or on a `build_opener(...)` call itself."""
    if not isinstance(node, ast.Call):
        return False
    if _callee(node) in _CONNECTS:
        return True
    f = node.func
    return (isinstance(f, ast.Attribute) and f.attr == "open"
            and (isinstance(f.value, ast.Name) and f.value.id in openers
                 or _callee(f.value) == "build_opener"))


#: A source text no `hit` can match in, read before parsing it: each hit's strings and names
#: stand in the text as written, quoted for a string. A string spelt with escapes is not read.
_PREFILTER = {_runs_gh: re.compile(r"[\"']gh[\s\"']"),
              _runs_git_fetch: re.compile(r"[\"']fetch[\"']"),
              _connects: re.compile(r"\b(?:" + "|".join(sorted(_CONNECTS | {"build_opener"}))
                                    + r")\b")}


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


#: The `Under ADR-004` cell of the row for a process the skill spawns, not a call it makes.
SPAWNED = "spawned process"


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
        row naming a function its script does not define; a connection not to `api.github.com`
        given as the exception. The scanners are checked first on a sample: an argv display, a
        `shell=True` string, an opener's `.open`, and the near misses they must pass."""
        sample = ("import shutil, subprocess\n"
                  "def a(): subprocess.run(['gh', 'run', 'list'])\n"
                  "def b(): cmd = ('gh',)\n"
                  "def c(): subprocess.run('gh api x', shell=True)\n"
                  "def d(): shutil.which('gh')\n"
                  "def e(): subprocess.run('gh api x')\n"
                  "def f():\n    def g(): subprocess.run(['git', 'fetch'])\n"
                  "def h(): run(root, 'fetch', 'origin')\n"
                  "def i(): steps = ('close-down', 'fetch')\n"
                  "def j(): urllib.request.urlopen(r)\n"
                  "O = urllib.request.build_opener(h)\n"
                  "def k(): O.open(r)\n"
                  "def m(): path.open('w')\n"
                  "def n(): open(r)\n"
                  "def o(): urllib.request.build_opener(h).open(r)\n")
        self.assertEqual({"a", "b", "c"}, _owners(sample, _runs_gh))
        self.assertEqual({"g", "h"}, _owners(sample, _runs_git_fetch))
        self.assertEqual({"j", "k", "o"}, _owners(sample, _connects))
        gh, fetch, get = _scan(_runs_gh), _scan(_runs_git_fetch), _scan(_connects)
        self.assertIn(("github_sync.py", "gh"), gh)
        self.assertIn(("sprint.py", "origin_drift"), fetch)
        self.assertIn(("version_check.py", "latest_release"), get)
        self.assertIn(("lib/meter_cursor.py", "call"), get)

        table = _one_table(_section(_trd_body(), "Network paths"), "Path")
        script, fn, cmd, adr = (table[0].index(c) for c in
                                ("Script", "Function", "Command or endpoint", "Under ADR-004"))
        every = {(r[script].strip("`"), r[fn].strip("`")): r for r in table[1:]}
        self.assertEqual(len(table) - 1, len(every), "a script and function listed twice")
        # BG1516: the lane runner's agent CLI is a process the skill spawns, whose own network use
        # no scan of the shipped scripts can see; it is listed as `spawned process`, and the
        # function it names must be the one that starts a process.
        spawned = {k for k, r in every.items() if r[adr] == SPAWNED}
        self.assertEqual({("lib/lanes.py", "_run_in_group")}, spawned)
        self.assertIn("subprocess.Popen", ast.unparse(next(
            n for n in ast.walk(ast.parse(_read(SCRIPTS / "lib" / "lanes.py")))
            if isinstance(n, ast.FunctionDef) and n.name == "_run_in_group")))
        rows = {k: r for k, r in every.items() if k not in spawned}
        # US1138: a connection is the ADR-004 exception when its script reaches `api.github.com`,
        # and not GitHub otherwise, as the Cursor usage GET is.
        github = {k for k in get if "api.github.com" in _read(SCRIPTS / k[0])}
        self.assertIn(("version_check.py", "latest_release"), github)
        for verdict, found in ((VIA_GH, gh), (EXCEPTION, github),
                               (NOT_GITHUB, fetch | (get - github))):
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
        self.assertLessEqual({p for p, _ in github}, _spans(exception[1].split("\n\n", 1)[0]))

    def test_the_adrs_and_header_match_6_2(self) -> None:
        """AC3. Mutants: ADR-012 with no Revision History row dated on or after its acceptance;
        a coverage line naming an older baseline, no `ON_MAIN` work on main, or a second
        baseline; a header or coverage line naming another release; ADR-012 naming a path that
        does not exist outside its Not yet built paragraph, or listing one there that now exists;
        ADR-003 not naming `reconcile.py settle`, or the hook not running it; ADR-009 not
        naming a `persona_gen.py` verb or a shipped default seat; a `persona_gen.py` verb
        creating a card that was not there."""
        text, body = _read(TRD), _trd_body()
        self.assertIn(f"## [{BASELINE}]", _read(REPO / "CHANGELOG.md"))
        claims = list(doc_freshness._BASELINE_CLAIM.finditer(body))
        self.assertEqual([BASELINE], [m.group("version") for m in claims])
        coverage = next((u for u in _units(_section(body, "Scope"))
                         if u.startswith("Coverage:")), None)
        self.assertIsNotNone(coverage, "the Scope states no Coverage line")
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


# --- US1293: the deferred signature ruling (D0503, RFC0065) -----------------------------------

RFC0060 = REPO / "sdlc-studio" / "rfcs" / "RFC0060-the-dark-factory-a-sprint-that-decides-for.md"
SPRINT_PAGES = (SCRIPTS.parent / "reference-sprint.md", SCRIPTS.parent / "help" / "sprint.md")
#: The ruling, the RFC it answers and the ADR that records it: ADR-012 was the last before it.
RULING, RULED_RFC, RULING_ADR = "D0503", "RFC0065", "013"

#: A sentence or cell saying a run awaiting its signature, or still running, holds the next one
#: back: something refusing while one awaits, or one that blocks or holds the slot with no
#: `not`, `never` or `longer` directly before the verb.
_WAITING = r"(?:awaits?|awaiting|still running|unsigned)"
_WAITING_BLOCKS_RE = re.compile(
    rf"\brefus\w*\b[^.;|]*?\b(?:while|when|until)\b[^.;|]*?\b{_WAITING}\b"
    rf"|\b{_WAITING}\b[^.;|]*?(?<!not )(?<!never )(?<!longer )"
    rf"\b(?:blocks?|holds the (?:run )?slot)\b", re.I)
#: A backticked `sprint.py sign ...` command, or one on a fenced line, up to a comment.
_SIGN_RE = re.compile(r"sprint\.py (sign\b[^`#\n]*)")


def _waiting_blocks(text: str) -> list[str]:
    """Each sentence or table cell of `text` that says a waiting run holds the next one back."""
    return [u for u in _units(text) if _WAITING_BLOCKS_RE.search(u)]


def _sign_options() -> set[str]:
    """Every option string the shipped `sprint.py sign` parser defines."""
    return {o for a in _sprint_verbs()["sign"]._actions for o in a.option_strings}


def _parsed_signs(text: str) -> list[tuple[str, argparse.Namespace]]:
    """`(invocation, namespace)` for each `sprint.py sign` command `text` gives, parsed by the
    shipped parser, so an option it does not define fails the parse (SystemExit). Each option is
    first held to the parser's own spelling, since argparse would take `--delegate` for
    `--delegated`."""
    import shlex
    out, options = [], _sign_options()
    for words in _SIGN_RE.findall(text):
        argv = shlex.split(words.strip())
        unknown = [w for w in argv if w.startswith("--") and w not in options]
        if unknown:
            raise AssertionError(f"sprint.py {words.strip()!r} names {unknown}, which the "
                                 f"sign parser does not define")
        with contextlib.redirect_stderr(io.StringIO()) as err:
            try:
                out.append((words, sprint.build_parser().parse_args(argv)))
            except SystemExit:
                raise AssertionError(f"sprint.py {words.strip()!r} does not parse: "
                                     f"{err.getvalue().strip()}") from None
    return out


def _accepted(did: str) -> bool:
    """Whether `sdlc-studio/decisions.md` holds `did` as accepted."""
    import decisions  # noqa: PLC0415 - the log's own reader
    return any(r["id"] == did and r["status"].lower() == "accepted"
               for r in decisions.list_decisions(REPO))


class TrdSignatureRulingTests(unittest.TestCase):
    """US1293 (CR0729): D0503 recorded as an ADR, the sprint pages naming the delegation option
    `sign` accepts, and RFC0060's D6 closed. Each name is held to the parser or log it names."""

    def test_the_trd_records_the_deferred_signature_ruling_as_an_adr(self) -> None:
        """AC1. Mutants: no ADR citing D0503, or two; one numbered other than next after
        ADR-012; Status not Accepted; RFC0065 not cited; either half of the ruling left out,
        or one of the three places the delegation is disclosed; an option the `sign` parser
        does not define; the lifecycle's plan row still refusing while a record awaits."""
        self.assertTrue(_accepted(RULING), f"premise: {RULING} is accepted in the log")
        self.assertTrue(list((REPO / "sdlc-studio" / "rfcs").glob(f"{RULED_RFC}-*.md")))
        body = _trd_body()
        numbers = re.findall(r"^###\s+ADR-(\d+):", body, re.M)
        self.assertEqual(list(range(1, len(numbers) + 1)), [int(n) for n in numbers])
        citing = [n for n in numbers if re.search(rf"\b{RULING}\b", _adr(body, n))]
        self.assertEqual([RULING_ADR], citing, f"one ADR cites {RULING}, ADR-{RULING_ADR}")
        adr = _adr(body, RULING_ADR)
        self.assertRegex(adr, r"(?m)^\*\*Status:\*\*\s*Accepted\b")
        self.assertRegex(adr, rf"\b{RULED_RFC}\b")
        units = _units(adr)
        waits = [u for u in units if re.search(r"\b(?:await\w*|waits?)\b", u)
                 and re.search(r"\bsignature\b", u) and re.search(r"\bnext run\b", u)
                 and re.search(r"\bopens?\b", u)]
        self.assertTrue(waits, "no sentence says a closed run waits and the next run opens")
        disclosed = [u for u in units if re.search(r"\bdelegat\w*\b", u)
                     and re.search(r"\bdecision\b", u)
                     and all(re.search(rf"\b{p}\b", u)
                             for p in ("signature block", "report", "evidence pack"))]
        self.assertTrue(disclosed, "no sentence discloses a delegated signature in the "
                                   "signature block, the report and the evidence pack")
        self.assertLessEqual({"--delegated", "--decision"}, _sign_options())
        signs = _parsed_signs(adr)
        self.assertTrue([w for w, ns in signs if ns.delegated and ns.decision], signs)
        self.assertEqual([], _waiting_blocks(body))

    def test_the_sprint_pages_name_the_delegation_option_sign_accepts(self) -> None:
        """AC2. Mutants: a page with no delegated `sign` invocation, or one naming an option
        the parser does not define (`--delegate`, `--decision-id`); a page with no sentence
        saying a waiting run does not block the next; a page still saying `plan` refuses while a
        record awaits or is still running."""
        options = _sign_options()
        self.assertLessEqual({"--delegated", "--decision"}, options, "premise: US1291's options")
        for page in SPRINT_PAGES:
            text = _read(page)
            with self.subTest(page=page.name):
                signs = _parsed_signs(text)
                self.assertTrue(signs, "premise: the page gives a sign command")
                self.assertTrue([w for w, ns in signs if ns.delegated and ns.decision],
                                "no runnable sign command uses --delegated with --decision")
                frees = [u for u in _units(text) if re.search(r"\bawait\w*\b", u)
                         and re.search(r"\b(?:not|no longer|never)\b[^.;]*?\b(?:block|hold)", u)
                         and re.search(r"\bnext\b", u)]
                self.assertTrue(frees, "no sentence says a waiting run does not block the next")
                self.assertEqual([], _waiting_blocks(text))

    def test_rfc0060_d6_is_closed_with_a_pointer_to_rfc0065(self) -> None:
        """AC3. Mutants: the D6 ruling still Open; RFC0065 not named; the Recorded cell
        empty or naming another decision; the note still saying D6 remains open."""
        self.assertTrue(_accepted(RULING), f"premise: {RULING} is accepted in the log")
        section = _section(_read(RFC0060), "Open Decisions")
        table = _one_table(section, "#")
        ruling, recorded = table[0].index("Ruling"), table[0].index("Recorded")
        d6 = next(r for r in table[1:] if r[0] == "D6")
        self.assertNotRegex(d6[ruling], r"\bOpen\b")
        self.assertRegex(d6[ruling], rf"\b{RULED_RFC}\b")
        self.assertRegex(d6[recorded], rf"\b{RULING}\b")
        note = "\n".join(line for line in section.splitlines() if line.startswith(">"))
        self.assertTrue(note, "premise: the note above the table")
        self.assertNotRegex(note, r"\bD6\b[^.]*\b(?:remains|is|left|stays)\s+open\b")

    def test_signing_beside_a_later_run_states_the_committed_close_rule(self) -> None:
        """The QA REJECT of US1293's first build: ADR-013 and help/sprint.md say `sign` seals a
        waiting run while a later run is open, which holds only as D0524 rules it. Each also
        says that once HEAD has moved past the commit that filed the run's record, or while a
        later run is open, the run is judged against that commit, and that a close not yet
        committed beside a later run is refused in the words `sprint.py` prints. Mutants: either
        rule left out of either page; the refusal quoted in words the script does not print."""
        refusal = "commit the close first"
        # The f-strings the script prints, not its docstrings, which quote the refusal too.
        printed = ["".join(v.value for v in n.values if isinstance(v, ast.Constant))
                   for n in ast.walk(ast.parse(_read(SCRIPTS / "sprint.py")))
                   if isinstance(n, ast.JoinedStr)]
        self.assertTrue([s for s in printed if refusal in s], "premise: the shipped refusal")
        for name, text in (("ADR-013", _adr(_trd_body(), RULING_ADR)),
                           ("help/sprint.md", _read(SPRINT_PAGES[1]))):
            units = _units(text)
            with self.subTest(page=name):
                self.assertTrue([u for u in units if re.search(r"\blater run\b", u)
                                 and re.search(r"\b(?:set|setting)\b[^.]*\baside\b", u)],
                                "premise: the page seals a waiting run beside a later run")
                self.assertTrue([u for u in units if re.search(r"\bD0524\b", u)
                                 and re.search(r"\bHEAD\b[^.]*\bmoved past the commit that "
                                               r"filed\b", u)
                                 and re.search(r"\bjudge[sd]?\b[^.]*?\bagainst that commit\b",
                                               u)],
                                "no sentence says the run is judged against its committed close")
                self.assertTrue([u for u in units if re.search(r"\bnot yet committed\b", u)
                                 and re.search(r"\blater run\b", u) and refusal in u],
                                "no sentence says an uncommitted close beside a later run is "
                                "refused, in the refusal's own words")


# --- BG1516, BG1529, BG1530, BG1531, BG1533: the TRD held to the code and tree it describes ---


def _threat_rows() -> list[list[str]]:
    return _one_table(_section(_trd_body(), "Threat Model"), "Threat")[1:]


def _network_rows() -> list[list[str]]:
    return _one_table(_section(_trd_body(), "Network paths"), "Path")[1:]


@functools.lru_cache(maxsize=None)
def _lane_runs() -> dict[str, dict]:
    """What `lanes.run` does with a stub `claude` on PATH, in a scratch repository and worktree:
    `hang` runs past a 1 s timeout, `commit` commits in its worktree and exits 0. Each gives
    the run's exit status, the lane records it left and the worktree's last commit subject."""
    out: dict[str, dict] = {}
    with tempfile.TemporaryDirectory() as d:
        base = Path(d)
        root, wt, bin_ = base / "repo", base / "wt", base / "bin"
        root.mkdir()
        bin_.mkdir()
        (root / "a.txt").write_text("a\n", encoding="utf-8")
        gitutil.git(["init", "-q", "-b", "main", "--template="], root)
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "init"], root)
        gitutil.git(["worktree", "add", "-q", "-b", "lane", str(wt)], root)
        stub = bin_ / "claude"
        stub.write_text('#!/bin/sh\nif [ "$STUB" = hang ]; then exec sleep 30; fi\n'
                        'exec git -c user.name=t -c user.email=t@t -c commit.gpgsign=false '
                        'commit -q --allow-empty -m "builder commit"\n', encoding="utf-8")
        stub.chmod(0o755)
        for mode in ("hang", "commit"):
            unit = f"US000{len(out) + 1}"
            env = {"STUB": mode, "PATH": os.pathsep.join((str(bin_), "/usr/bin", "/bin")),
                   "HOME": str(base / "home"), "XDG_DATA_HOME": str(base / "xdg"),
                   "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
            with mock.patch.dict(os.environ, env), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = lanes.run(root, unit, "claude", "BRIEF", worktree=wt, timeout=1)
            records = sorted((root / lanes.RUN_RECORDS / unit).glob("*.json"))
            subject = gitutil.git(["log", "-1", "--format=%s"], wt, text=True).stdout.strip()
            out[mode] = {"rc": rc, "subject": subject,
                         "records": [json.loads(r.read_text(encoding="utf-8")) for r in records]}
    return out


class TrdLaneRunnerTests(unittest.TestCase):
    """BG1516: the TRD names the headless lane runner, the five CLIs it drives and the flags it
    gives them, and no longer calls the Agent-tool fan-out the one harness-specific part."""

    #: What `headless_command` adds that is not a permission: the prompt, the output format.
    NOT_PERMISSIONS = {"-p", "--output-format", "--format", "--json", "-s", "--skip-git-repo-check",
                       "--model", "-m"}

    #: A sentence saying the runner, or what it starts, never commits or pushes.
    NO_COMMIT = re.compile(r"nothing the runner starts commits|never commits or pushes|"
                           r"commits or pushes nothing", re.I)

    def _permissions(self, cmd: list[str], brief: str) -> list[tuple[str, str | None]]:
        """Each permission flag in `cmd`, with the argument after it as its value where that is
        neither another flag nor the brief, else None."""
        args = cmd[1:]
        out = []
        for i, arg in enumerate(args):
            if not arg.startswith("-") or arg in self.NOT_PERMISSIONS:
                continue
            nxt = args[i + 1] if i + 1 < len(args) else None
            out.append((arg, nxt if nxt and not nxt.startswith("-") and nxt != brief else None))
        return out

    def test_every_headless_harness_is_named_with_its_flags(self) -> None:
        """Mutants: no lane runner subsection; a harness `BINARIES` lists left out of its table;
        a flag `headless_command` gives a harness left out of its row, or given another value
        than its row names (Codex's `--sandbox` widened to `danger-full-access`); `none` for a
        harness the code gives flags; the subsection not saying where the runner runs; the
        subsection saying nothing the runner starts commits or pushes, where a lane's CLI
        commits in its worktree and the run exits 0."""
        section = _section(_trd_body(), "Headless lane runner")
        self.assertIn("`sprint.py lane run`", section)
        self.assertIn("worktree", section)
        flat = " ".join(section.split())
        self.assertEqual((0, "builder commit"),
                         (_lane_runs()["commit"]["rc"], _lane_runs()["commit"]["subject"]),
                         "premise: the runner lets a lane's CLI commit")
        self.assertNotRegex(flat, self.NO_COMMIT)
        self.assertRegex(flat, r"does not stop the CLI committing, pushing or writing outside "
                               r"(?:its|the) worktree")
        rows = _one_table(section, "Harness")[1:]
        self.assertGreaterEqual(len(lanes.BINARIES), 5)
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        # A real repository, so Codex's `--add-dir` (the git directory) is part of its command.
        gitutil.git(["init", "-q", "--template="], Path(scratch.name))
        git_dir = (Path(scratch.name) / ".git").resolve()
        for harness, binary in sorted(lanes.BINARIES.items()):
            cmd = lanes.headless_command(harness, "BRIEF", None, Path(scratch.name))
            self.assertEqual(binary, cmd[0])
            named = [r for r in rows if binary in _spans(r[1])]
            with self.subTest(harness=harness):
                self.assertEqual(1, len(named), f"{binary} is named by {len(named)} rows")
                flags = self._permissions(cmd, "BRIEF")
                cell = named[0][2]
                for flag, value in flags:
                    self.assertIn(flag, cell)
                    if value is None:
                        continue
                    if Path(value).is_absolute() and Path(value).resolve() == git_dir:
                        self.assertIn("git directory", cell)
                    elif "," in value:
                        for part in value.split(","):
                            self.assertRegex(cell, rf"\b{re.escape(part)}\b")
                    else:
                        self.assertIn(f"`{flag} {value}`", cell)
                if not flags:
                    self.assertRegex(cell, r"^none\b")
        with self.assertRaises(ValueError):
            lanes.headless_command("nonesuch", "BRIEF", None, Path(scratch.name))

    def test_agentic_waves_are_not_called_the_only_harness_specific_part(self) -> None:
        """Mutants: either passage restored to calling the wave fan-out the one or only
        harness-specific part, with or without words between (`the only harness-specific
        part`, `the one part`); question 3 left open with no word of the lane runner; the
        Agentic passage saying the `compatibility` frontmatter flags the fan-out Claude-Code-only,
        or not saying what that frontmatter says; the passage saying nothing else is tied to one
        harness, or leaving out `plan.py` and the plan-mode folder it manages."""
        body = _trd_body()
        agentic = _section(body, "Agentic execution")
        bullets = re.split(r"\n(?=- \[)", _section(body, "12. Open Technical Questions"))
        q3 = next(b for b in bullets if "agentic wave" in b)
        only = re.compile(r"\b(?:one|only|sole|single)\b(?!\s+of\b)(?:\s+[\w-]+){0,3}?\s+"
                          r"(?:part|feature|non-neutral)s?\b|"
                          r"\bthe\s+rest\s+is\s+harness-neutral\b", re.I)
        for name, text in (("Agentic execution", agentic), ("question 3", q3)):
            with self.subTest(passage=name):
                self.assertIsNone(only.search(" ".join(text.split())), text)
        flat_agentic = " ".join(agentic.split())
        self.assertIn("headless lane runner", flat_agentic)
        compat = re.search(r'^compatibility:\s*"(.*)"\s*$',
                           (SCRIPTS.parent / "SKILL.md").read_text(encoding="utf-8"), re.M)
        said = "Needs no particular harness: "
        self.assertIn(said, compat.group(1), "premise: the frontmatter's harness clause")
        self.assertNotRegex(flat_agentic, r"(?i)claude[- ]code[- ]only",
                            "the passage says the frontmatter flags the fan-out Claude-Code-only")
        self.assertIn(said.lower().rstrip(": "), flat_agentic.lower())
        self.assertIn(compat.group(1).split(said, 1)[1].rstrip("."),
                      flat_agentic.replace("`", ""),
                      "the passage does not say what the compatibility frontmatter says")
        self.assertNotRegex(flat_agentic, r"(?i)\bnothing else\b|\bno other part\b",
                            "the passage closes the list of harness-specific parts")
        plans = re.search(r'^DEFAULT_PLANS_DIR = "([^"]+)"',
                          (SCRIPTS / "plan.py").read_text(encoding="utf-8"), re.M).group(1)
        for named in ("`plan.py`", f"`{plans}`"):
            self.assertIn(named, flat_agentic, "plan.py's plan-mode files are not named")
        flat = " ".join(q3.split())
        self.assertTrue(q3.startswith("- [x]") or all(b in flat for b in lanes.BINARIES.values()),
                        "question 3 is open and does not name the harnesses the runner drives")

    def test_the_spawned_agent_has_a_network_row_and_a_threat_row(self) -> None:
        """Mutants: either row removed; the network row's last cell or the threat row's
        mitigation emptied; the threat row dropping the limit it states; the network row saying
        a timed-out lane is not recorded, where `lanes.run` records it unmetered; the threat row
        counting a bar on commits or pushes, or a landing that stages the Affects, among its
        controls, or its limit leaving out that a lane can commit, push and write outside its
        worktree, or that Claude Code's tools include Bash."""
        runs = _lane_runs()
        hang = runs["hang"]
        self.assertEqual((1, [lanes.TIMED_OUT]),
                         (hang["rc"], [r["unmetered"] for r in hang["records"]]),
                         "premise: a timed-out lane is recorded unmetered")
        self.assertEqual((0, "builder commit"), (runs["commit"]["rc"], runs["commit"]["subject"]),
                         "premise: the runner lets a lane's CLI commit")
        self.assertIn("Bash", lanes.CLAUDE_LANE_TOOLS)
        net = [r for r in _network_rows() if "lib/lanes.py" in r[1]]
        self.assertEqual(1, len(net), "the Network paths table has no row for the lane runner")
        self.assertTrue(net[0][-1].strip(), "the network row names no bound")
        cell = " ".join(net[0][-1].split())
        self.assertIn("bounded", cell)
        self.assertNotRegex(cell, r"no lane (?:is )?recorded")
        self.assertIn(f"recorded unmetered (`{lanes.TIMED_OUT}`)", cell)
        threat = [r for r in _threat_rows() if "agent CLI" in r[0]]
        self.assertEqual(1, len(threat), "the Threat Model has no row for the spawned agent CLI")
        control = " ".join(threat[0][3].split())
        for word in ("worktree", "timeout", "sandbox", "reviewer", "limit"):
            self.assertIn(word, control)
        self.assertNotRegex(control, self.NO_COMMIT)
        self.assertNotRegex(control, r"land\S*`? stages")
        limit = control.split("The limit:", 1)[1]
        for named in ("committing", "pushing", "outside its worktree", "Bash"):
            self.assertIn(named, limit)


class TrdPerformanceClaimTests(unittest.TestCase):
    """BG1529: sections 8 and 10 state no sub-second target for the census, and the cost-model
    paragraph reads as complete sentences."""

    SUB_SECOND = re.compile(r"sub-second|under a second|within a second", re.I)

    def _sections(self) -> dict[str, str]:
        body = _trd_body()
        return {"8": _section(body, "8. Infrastructure"),
                "10": _section(body, "10. Performance Requirements")}

    def test_no_unmeasured_sub_second_target_for_reconcile_or_status(self) -> None:
        """Mutants: a sub-second claim restored for reconcile or status in either section; the
        measured figures, their date, the live command or the `settle` cost dropped."""
        for name, text in self._sections().items():
            for unit in _units(text):
                if re.search(r"\b(?:reconcile|status)\b", unit, re.I):
                    with self.subTest(section=name, unit=unit[:60]):
                        self.assertIsNone(self.SUB_SECOND.search(unit), unit)
        row = next(r for r in _one_table(self._sections()["10"], "Metric")[1:]
                   if r[0].startswith("Reconcile"))
        cell = " ".join(row[1:])
        self.assertIn("scales with artefact count", cell)
        self.assertRegex(cell, r"\d{4}-\d{2}-\d{2}")
        self.assertRegex(cell, r"`reconcile\.py detect` \d+ s")
        self.assertRegex(cell, r"`status\.py` [\d.]+ s")
        self.assertRegex(cell, r"settle` [\d.]+ s")
        self.assertIn("`time python3 <skill>/scripts/reconcile.py detect`", cell)
        scaling = " ".join(self._sections()["8"].split())
        self.assertIn("grows with the artefact count", scaling)
        self.assertIn("`reconcile.py settle`", scaling)
        self.assertRegex(_read(REPO / ".githooks" / "pre-commit"),
                         re.compile(r'^(?![ \t]*#).*reconcile\.py"? settle\b', re.M))

    def test_the_spliced_cost_model_sentence_is_repaired(self) -> None:
        """Mutants: the sentence ending 'is never a gate: a script' run into 'the meter reads
        the store' again; either sentence left without its stop or its capital."""
        text = self._sections()["10"]
        para = next(p for p in text.split("\n\n") if p.startswith("**The cost model"))
        self.assertNotRegex(para, r"a script\s+the meter reads")
        units = _units(para)
        at = next(i for i, u in enumerate(units) if "**never** a gate:" in u)
        self.assertRegex(units[at], r"a gate: a script \w+ .*[.]$")
        self.assertNotIn("the meter reads", units[at])
        self.assertTrue(units[at + 1].startswith("The meter reads the store of the harness"),
                        units[at + 1][:60])
        self.assertTrue(units[at + 1].endswith("is in it."), units[at + 1][-40:])


#: The sentences of `text` naming a story as open, as the stories' ids they name.
_OPEN_CLAIM = re.compile(r"\bopen\b", re.I)
_STORY_ID = re.compile(r"\bUS\d{4}\b")


def _story_status(story: str, stories: Path) -> str | None:
    """The Status line of `story`'s file under `stories`, or None when there is no such file."""
    for path in sorted(stories.glob(f"{story}-*.md")):
        m = re.search(r"^> \*\*Status:\*\*\s*(.+?)\s*$", _read(path), re.M)
        if m:
            return m.group(1)
    return None


def _done_stories_called_open(adr: str, stories: Path) -> list[str]:
    """The stories `adr` names in a sentence that says `open`, whose Status line says Done."""
    named = {s for unit in _units(adr) if _OPEN_CLAIM.search(unit)
             for s in _STORY_ID.findall(unit)}
    return sorted(s for s in named if _story_status(s, stories) == "Done")


class TrdAdr012Tests(unittest.TestCase):
    """BG1530: ADR-012 names the built learning stories as built, and its check reads the
    stories' own Status lines."""

    STORIES = REPO / "sdlc-studio" / "stories"
    BUILT = ("US1066", "US1067", "US1068")

    def test_adr_012_names_the_built_learning_stories_as_built(self) -> None:
        """Mutants: Status ending not yet built; the sentence saying no learning is live yet
        restored; a story left out of Built so far, or listed as not built; no Revision History
        row naming the change."""
        text, adr = _read(TRD), _adr(_trd_body(), "012")
        status = re.search(r"^\*\*Status:\*\*.*$", adr, re.M).group(0)
        self.assertNotRegex(status, r"not yet built\s*$")
        flat = " ".join(adr.split())
        self.assertNotIn("no learning is live yet", flat)
        built, not_built = flat.split("**Built so far:**", 1)[1].split("**Not yet built:**", 1)
        for story in self.BUILT:
            with self.subTest(story=story):
                self.assertEqual("Done", _story_status(story, self.STORIES))
                self.assertIn(story, built)
                self.assertNotIn(story, not_built.split("**Consequences:**")[0])
        history = _one_table(_section(text, "Revision History"), "Date")
        self.assertTrue([r for r in history[1:] if "ADR-012" in r[2]
                         and all(s in r[2] for s in self.BUILT)],
                        "no Revision History row names ADR-012 with US1066, US1067 and US1068")

    def test_a_done_story_called_open_fails_the_check(self) -> None:
        """Mutants: the check reading no Status line (a Done story passes); reading every story
        as Done (an open one fails); ADR-012 calling a Done story open."""
        with tempfile.TemporaryDirectory() as d:
            stories = Path(d)
            (stories / "US9001-done.md").write_text("# US9001: a\n\n> **Status:** Done\n",
                                                    encoding="utf-8")
            (stories / "US9002-open.md").write_text("# US9002: b\n\n> **Status:** Draft\n",
                                                    encoding="utf-8")
            self.assertEqual(["US9001"], _done_stories_called_open("US9001 is still open.",
                                                                   stories))
            self.assertEqual([], _done_stories_called_open("US9002 is still open.", stories))
            self.assertEqual([], _done_stories_called_open("US9001 is built.", stories))
            self.assertEqual([], _done_stories_called_open("US9003 is still open.", stories))
        self.assertEqual(["US1066"], _done_stories_called_open("US1066 is an open story.",
                                                               self.STORIES))
        self.assertEqual([], _done_stories_called_open(_adr(_trd_body(), "012"), self.STORIES))


class TrdReadOnlyHelperTests(unittest.TestCase):
    """BG1531: `critic brief`, `gate` and `review_prep` write state, so no read-only list holds
    them, and every helper a list does hold has a confinement assertion."""

    CONFINEMENT = SCRIPTS / "tests" / "test_confinement.py"
    LIST = re.compile(r"read-only\s+helpers\s*\(([^)]*)\)", re.I)
    WRITERS = ("critic brief", "gate", "review_prep")

    def _lists(self) -> list[set[str]]:
        found = [_spans(m.group(1)) for m in self.LIST.finditer(_trd_body())]
        return [f for f in found if f]

    def test_the_writing_helpers_are_not_listed_as_read_only(self) -> None:
        """Mutants: any of the three put back in a read-only list; section 2 calling the script
        layer read-only; the files and their tracking left out of section 5; `review_prep.py
        close` named without the meta indexes `reconcile.apply_meta` backfills, or without one
        of the `sdlc_md.META_TYPES` folders it reaches; the section 9 mitigation not citing the
        lists."""
        body = _trd_body()
        lists = self._lists()
        self.assertGreaterEqual(len(lists), 2, "premise: the split rule and rule 5 list helpers")
        for held in lists:
            for writer in self.WRITERS:
                with self.subTest(writer=writer, held=sorted(held)):
                    self.assertFalse([h for h in held if h.split("/")[0].startswith(writer)],
                                     held)
        self.assertNotRegex(_section(body, "2. Project Classification"), r"read-only Python")
        contract = " ".join(_section(body, "Script CLI contract").split())
        for named in ("`critic.py brief`", "`sdlc-studio/reviews/verdicts/<UNIT>/`",
                      "`sdlc-studio/.local/briefs.jsonl` (untracked)", "`gate.py`",
                      "`review_prep.py close`", "`sdlc-studio/.local/review-state.json` (untracked)",
                      "`reviews/LATEST.md`", "(all tracked)"):
            self.assertIn(named, contract)
        close = contract.split("`review_prep.py close`", 1)[1].split("`review_prep.py prep`")[0]
        self.assertIn("`reconcile.apply_meta`", close)
        self.assertIn("`_index.md`", close)
        self.assertGreaterEqual(len(sdlc_md.META_TYPES), 4, "premise: the meta folders were read")
        for rel, _prefix in sorted(sdlc_md.META_TYPES.values()):
            with self.subTest(meta=rel):
                self.assertIn(f"`{rel.removeprefix('sdlc-studio/')}/`", close)
        self.assertIn("gate-cost.json", _section(body, "The gate tier"))
        row = next(r for r in _threat_rows() if r[0].startswith("Script mutating"))
        self.assertIn("§5 rule 5", row[3])
        self.assertRegex(row[3], r"`critic brief`, `gate` and `review_prep close`")

    def test_every_helper_called_read_only_has_a_confinement_assertion(self) -> None:
        """Mutants: a helper added to a read-only list with no `_assert_read_only` call for it;
        a call renamed so no list entry matches it."""
        calls = []
        for node in ast.walk(ast.parse(_read(self.CONFINEMENT))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "_assert_read_only" and node.args
                    and isinstance(node.args[0], ast.List)):
                calls.append([e.value for e in node.args[0].elts if isinstance(e, ast.Constant)])
        self.assertTrue(calls, "premise: test_confinement.py asserts some helper read-only")
        lists = self._lists()
        self.assertTrue(lists, "premise: the TRD lists read-only helpers")
        for held in lists:
            for helper in sorted(held):
                tokens = helper.split()
                want = [tokens[0] + ".py", *tokens[1:]]
                with self.subTest(helper=helper):
                    self.assertTrue([c for c in calls if c[:len(want)] == want],
                                    f"no read-only assertion in test_confinement.py runs {helper}")


class TrdInstructionsCheckTests(unittest.TestCase):
    """BG1533: the ADRs call `validate.py instructions` what it is, an advisory report, and this
    repository's `AGENTS.md` passes it within the cap the page states for itself."""

    def test_the_adrs_do_not_call_the_advisory_check_enforcement(self) -> None:
        """Mutants: ADR-005 saying `enforces`, or not saying warnings, init, upgrade and not a
        gate; ADR-001 saying the check keeps the loading guide and type tables in sync; the
        check made a gate (a warning exiting non-zero)."""
        body = _trd_body()
        adr5 = " ".join(_adr(body, "005").split())
        unit = next(u for u in _units(adr5) if "`validate.py instructions`" in u)
        self.assertNotRegex(unit, r"\benforc\w*")
        for word in ("warnings", "`init` and `upgrade`", "not a gate"):
            self.assertIn(word, adr5)
        adr1 = " ".join(_adr(body, "001").split())
        self.assertNotRegex(adr1, r"enforced[^.]*`validate\.py instructions`")
        self.assertRegex(adr1, r"no check holds the type tables|names the check")
        # The premise: a warning does not fail the run, so it is advisory.
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text("# Notes\n", encoding="utf-8")
            out = subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), "--root", d,
                                  "instructions"], capture_output=True, text=True)
        self.assertIn("WARNING [no-doctrine-pointer]", out.stdout)
        self.assertEqual(0, out.returncode)

    def test_the_instructions_check_reports_no_warning_here(self) -> None:
        """Mutants: the doctrine pointer or the integration rule removed from `AGENTS.md`
        (each named by its rule); a file with neither as the positive control."""
        def run(root: Path) -> str:
            return subprocess.run([sys.executable, str(SCRIPTS / "validate.py"), "--root",
                                   str(root), "instructions"], capture_output=True,
                                  text=True).stdout
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "AGENTS.md").write_text("# Notes\n", encoding="utf-8")
            bare = run(Path(d))
        self.assertIn("no-doctrine-pointer", bare)
        self.assertIn("no-integration-rule", bare)
        here = run(REPO)
        self.assertNotIn("WARNING", here)
        self.assertIn("warnings=0", here)
        text = _read(REPO / "AGENTS.md")
        self.assertIn("reference-doctrine", text)
        self.assertIn("Integrate continuously", text)

    def test_agents_md_stays_within_its_character_cap(self) -> None:
        """Mutants: the cap read as larger than the page states; `AGENTS.md` past it."""
        text = _read(REPO / "AGENTS.md")
        stated = re.search(r"held to ([\d,]+) chars", text)
        self.assertIsNotNone(stated, "AGENTS.md states no cap for itself")
        cap = int(stated.group(1).replace(",", ""))
        self.assertEqual(7000, cap)
        self.assertLessEqual(len(text), cap)


# --- BG1557, BG1565, US1299: the summaries, the built state and the PyYAML ruling ---


class TrdSummaryAgreementTests(unittest.TestCase):
    """BG1557: the TRD's summaries agree with its own detail and with the code: System Context
    names every external service, section 2 does not call the script layer read-only, the C4
    note names a path that exists, the install table gives `install.sh`'s local directories and
    the cost model cites the shipped basis."""

    #: The Deployment Topology table's target names, as `install.sh` names each target.
    TARGETS = {"Claude Code": "claude", "Codex": "codex", "Gemini CLI": "gemini",
               "opencode": "opencode", "GitHub Copilot": "copilot", "`agents` (generic)": "agents"}

    def test_the_summary_names_every_external_service_the_detail_lists(self) -> None:
        """AC1. Mutants: System Context saying the only external service is GitHub through
        `gh`; a service the External Services table lists left out of it; section 2 calling
        the script layer read-only."""
        body = _trd_body()
        context = " ".join(_section(body, "System Context").split())
        self.assertNotRegex(context, r"(?i)only external service")
        services = _one_table(_section(body, "External Services"), "Service")[1:]
        self.assertTrue([r for r in services if r[0] == "Cursor usage API"],
                        "premise: the External Services table lists the Cursor usage API")
        for row in services:
            with self.subTest(service=row[0]):
                self.assertIn(row[0], context)
        hosts = {m for r in _network_rows() for m in re.findall(r"`(api\.[\w.]+)`", r[3])}
        self.assertIn("api.github.com", hosts, "premise: the network table names the release GET")
        self.assertIn("`api.github.com`", context)
        self.assertIn("`gh` CLI", context)
        pattern = " ".join(_section(body, "2. Project Classification").split())
        self.assertNotIn("read-only", pattern)
        self.assertIn("§5 rule 5", pattern)

    def test_the_c4_path_exists_and_the_install_table_matches_install_sh(self) -> None:
        """AC2. Mutants: the C4 note naming `modules/trd/c4-diagrams.md`, which does not exist;
        a row giving a home-directory path under the local heading; a row giving another
        target's directory; a target `install.sh` installs left out of the table."""
        body = _trd_body()
        note = next(p for p in _section(body, "Component Overview").split("\n\n")
                    if "C4 Diagrams" in p)
        paths = [s for s in _spans(note) if s.endswith(".md")]
        self.assertEqual(1, len(paths), note)
        self.assertTrue((SCRIPTS.parent / paths[0]).is_file(), f"{paths[0]} does not exist")
        install = _read(REPO / "install.sh")
        local = dict(re.findall(r'^\s*(\w+):local\)\s+echo "([^"]+)"', install, re.M))
        targets = re.search(r'^ALL_TARGETS="([^"]+)"', install, re.M).group(1).split()
        self.assertEqual(set(targets), set(local), "premise: install.sh's local cases were read")
        self.assertEqual(".gemini/skills", local["gemini"])
        table = _one_table(_section(body, "Deployment Topology"), "Target")
        header, rows = table[0], table[1:]
        self.assertEqual(sorted(targets), sorted(self.TARGETS[r[0]] for r in rows))
        for row in rows:
            target = self.TARGETS[row[0]]
            for column, cell in zip(header[1:], row[1:]):
                if re.search(r"(?i)\bglobal\b", column):
                    continue
                with self.subTest(target=target, column=column):
                    self.assertRegex(column, r"(?i)\blocal\b")
                    self.assertNotIn("~", cell)
                    self.assertEqual(f"{local[target]}/sdlc-studio/",
                                     re.findall(r"`([^`]+)`", cell)[0])

    def test_the_cost_model_count_matches_the_shipped_basis(self) -> None:
        """AC3. Mutants: either passage citing 20 units, or not the measured count the basis
        holds; either dropping the build-only condition."""
        basis = sprint.POINTS_RATE_SEED_BASIS
        units = re.search(r"re-estimation of (\d+) delivered units", basis).group(1)
        measured = re.search(r"(\d+) had measured actuals", basis).group(1)
        self.assertIn(sprint.NO_BASE_TERM_CONDITION, basis)
        self.assertRegex(sprint.NO_BASE_TERM_CONDITION,
                         r"holds for the BUILD, not for a whole sprint")
        body = _trd_body()
        cost = next(p for p in _section(body, "10. Performance Requirements").split("\n\n")
                    if p.startswith("**The cost model"))
        q = next(b for b in re.split(r"\n(?=- \[)", _section(body, "12. Open Technical Questions"))
                 if "plan-time predictor" in b)
        for name, text in (("section 10", cost), ("section 12", q)):
            flat = " ".join(text.split())
            with self.subTest(passage=name):
                self.assertIn(f"re-estimation of {units} delivered units", flat)
                self.assertRegex(flat, rf"\b{measured} (?:of them )?with measured actuals")
                self.assertRegex(flat, r"(?i)holds for the build, not for a whole sprint")


#: A sentence calling a story open or unbuilt.
_UNBUILT_CLAIM = re.compile(r"\bopen\b|\bnot yet built\b|\bunbuilt\b", re.I)


def _stories_called_unbuilt(text: str) -> set[str]:
    """The story ids `text` names in a sentence (`_units`) that calls something open or unbuilt."""
    return {s for unit in _units(text) if _UNBUILT_CLAIM.search(unit)
            for s in _STORY_ID.findall(unit)}


def _done_stories_called_unbuilt(text: str, stories: Path) -> list[str]:
    """Those of `_stories_called_unbuilt(text)` whose file under `stories` reads Done."""
    return sorted(s for s in _stories_called_unbuilt(text)
                  if _story_status(s, stories) == "Done")


class TrdBuiltStateTests(unittest.TestCase):
    """BG1565: ADR-012 states the learning loop 6.4.0 ships, and no story the TRD calls open or
    not yet built reads Done."""

    STORIES = REPO / "sdlc-studio" / "stories"
    LOOP = ("US1058", "US1059", "US1065", "US1066", "US1067", "US1068")

    def test_adr_012_states_the_learning_loop_as_shipped(self) -> None:
        """AC1. Mutants: Built so far saying approval and signing are open stories, or that no
        learning is live; a loop story left out; a step of the loop (propose, approve or
        reject, the close's listing, the signed gate) left out; no Revision History row."""
        flat = " ".join(_adr(_trd_body(), "012").split())
        self.assertNotRegex(flat, r"(?i)open stor(?:y|ies)|no learning is live")
        built = flat.split("**Built so far:**", 1)[1].split("**Not yet built:**", 1)[0]
        for story in self.LOOP:
            with self.subTest(story=story):
                self.assertIn(story, built)
        for step in (r"proposes? (?:a|its) learning", r"approves or rejects",
                     r"lists every learning about to go live",
                     r"reaches a brief only once (?:the run is signed|a signed close)"):
            with self.subTest(step=step):
                self.assertRegex(built, step)
        history = _one_table(_section(_read(TRD), "Revision History"), "Date")
        self.assertTrue([r for r in history[1:] if "BG1565" in r[2] and "ADR-012" in r[2]
                         and "US1065" in r[2]],
                        "no Revision History row names BG1565's change to ADR-012")

    def test_no_story_called_open_reads_done(self) -> None:
        """AC2. Mutants: ADR-012 calling a Done loop story open or not yet built; the brief
        refusal (US1055) left in Not yet built, or out of Built so far, once it is built; the
        check reading no claim (the Not yet built clause is its premise)."""
        body = _trd_body()
        self.assertTrue([u for u in _units(body)
                         if "**Not yet built:**" in u and _UNBUILT_CLAIM.search(u)],
                        "premise: the claims were read")
        self.assertNotIn("US1055", _stories_called_unbuilt(body))
        flat = " ".join(_adr(body, "012").split())
        built = flat.split("**Built so far:**", 1)[1].split("**Not yet built:**", 1)[0]
        self.assertRegex(built, r"frames no brief.*?refuse it.*?\(US1055\)")
        history = _one_table(_section(_read(TRD), "Revision History"), "Date")
        self.assertTrue([r for r in history[1:] if "US1055" in r[2] and "ADR-012" in r[2]],
                        "no Revision History row names US1055's change to ADR-012")
        self.assertEqual([], _done_stories_called_unbuilt(body, self.STORIES))

    def test_a_done_story_called_open_is_reported_and_a_draft_one_passes(self) -> None:
        """AC3. Mutants: the check reporting every story it reads; passing the stale claim;
        reading `not yet built` as no claim."""
        with tempfile.TemporaryDirectory() as d:
            stories = Path(d)
            (stories / "US9001-done.md").write_text("# US9001: a\n\n> **Status:** Done\n",
                                                    encoding="utf-8")
            (stories / "US9002-draft.md").write_text("# US9002: b\n\n> **Status:** Draft\n",
                                                     encoding="utf-8")
            self.assertEqual(["US9001"], _done_stories_called_unbuilt(
                "US9001 and US9002 are open stories.", stories))
            self.assertEqual(["US9001"], _done_stories_called_unbuilt(
                "**Not yet built:** US9001, US9002.", stories))
            self.assertEqual([], _done_stories_called_unbuilt("US9002 is still open.", stories))
            self.assertEqual([], _done_stories_called_unbuilt("US9001 shipped.", stories))


#: The spec pages that must not call the runtime standard library only.
SPEC_PAGES = (REPO / "sdlc-studio" / "prd.md", TRD, REPO / "sdlc-studio" / "tsd.md",
              REPO / "README.md")
#: A claim that the scripts need only the standard library, or that PyYAML is optional.
_STDLIB_ONLY = re.compile(
    r"\bpure[- ]stdlib\b|\bstdlib[- ]only\b|standard[- ]library[- ]only|pure standard library|"
    r"only the standard library|no third-party packages?|free of third-party|"
    r"PyYAML is used (?:for config )?when present|degrades? to (?:the caller's |built-in )?"
    r"defaults? when absent", re.I)
#: Where a sentence is cut into statements: at `;`, and before a `**Label:**` or a heading.
_STATEMENT_CUT = re.compile(r";|(?=\*\*[^*]+:\*\*)|(?=#{1,6}\s)")
#: A negation, then up to three words, at the end of the text before a term: the term is denied.
_NEGATION_TAIL = re.compile(
    r"(?:\b(?:not|never|no|nothing|rather than|instead of)\b|n't\b)(?:\s+\S+){0,3}\s*$", re.I)
#: A term saying PyYAML may be absent: optional, soft, recommended, used where present, or the
#: scripts falling back or degrading to their defaults.
_MAY_BE_ABSENT = re.compile(
    r"\boptional(?:ly)?\b|\bsoft\b|\brecommended\b|\bfall(?:s|ing)?\s+back\b|\bfallback\b|"
    r"\bdegrad\w*|\bdefaults?\b|\b(?:when|if|where)\s+(?:it\s+is\s+|it's\s+)?"
    r"(?:present|available|installed)\b", re.I)
#: A term saying PyYAML must be there; denied ("not required"), it says PyYAML need not be.
_REQUIRED = re.compile(r"\brequire[sd]?\b|\bmandatory\b|\bnecessary\b|\bneeded\b", re.I)
_NEED_NOT = re.compile(r"\bneeds?\s+not\b|\bneedn't\b", re.I)
#: PyYAML's verb in the past tense: the statement tells the history, not today's runtime.
_PYYAML_PAST = re.compile(r"\bPyYAML`?\s+(?:was|were|had\s+been|used\s+to\s+be)\b")


def _pyyaml_statements(units: list[str]) -> list[str]:
    """The statements of `units` that name PyYAML: each unit, a table cell included, cut into
    sentences, and each sentence at `_STATEMENT_CUT` outside a code span, so that a cell or an
    ADR's labelled paragraphs are judged one statement at a time."""
    out = []
    for unit in units:
        for sentence in re.split(r"(?<=[.!?])\s+", unit):
            pieces = [""]
            for i, part in enumerate(re.split(r"(`[^`]*`)", sentence)):
                cut = [part] if i % 2 else _STATEMENT_CUT.split(part)
                pieces[-1] += cut[0]
                pieces.extend(cut[1:])
            out.extend(p.strip() for p in pieces if "PyYAML" in p)
    return out


def _terms(statement: str, pattern: re.Pattern, denied: bool) -> list[str]:
    """The `pattern` terms in `statement`'s words outside code spans, kept where a negation in
    the three words before them denies them (`denied`) or where none does."""
    words = re.sub(r"`[^`]*`", "`code`", statement)
    return [m.group(0) for m in pattern.finditer(words)
            if bool(_NEGATION_TAIL.search(words[:m.start()])) is denied]


def _calls_pyyaml_optional(statement: str) -> bool:
    """Whether a present-tense statement naming PyYAML says it may be absent: a term from
    `_MAY_BE_ABSENT` it does not deny, a `_REQUIRED` term it does, or "need not"."""
    if _PYYAML_PAST.search(statement):
        return False
    return bool(_terms(statement, _MAY_BE_ABSENT, False) or _terms(statement, _REQUIRED, True)
                or _NEED_NOT.search(statement))


def _calls_pyyaml_required(statement: str) -> bool:
    """Whether a present-tense statement naming PyYAML says it is required, undenied."""
    return not _PYYAML_PAST.search(statement) and bool(_terms(statement, _REQUIRED, False))


class TrdRequiredPyYamlTests(unittest.TestCase):
    """US1299: the PRD, TRD and README name PyYAML as required and none calls the runtime
    standard library only; the TRD records the ruling as an ADR and carries the threat row."""

    def test_no_spec_page_claims_a_standard_library_only_runtime(self) -> None:
        """AC1, over the PRD, TRD, TSD and README, each statement naming PyYAML judged by what it
        says. Mutants: the PRD's `stdlib only` tech stack line; the TSD's pure-stdlib
        supply-chain sentence; the TRD's Won't Have bullet ruling out a required third-party
        dependency; a page that names PyYAML nowhere as required; the README calling PyYAML not
        required, or optional with the scripts falling back to their defaults; the PRD calling
        it optional, or listing it among its soft runtime deps."""
        self.assertIsNotNone(_STDLIB_ONLY.search("- **Python 3.10+ (stdlib only)**"))
        for soft in ("The scripts need Python 3.10 or later; PyYAML is not required.",
                     "PyYAML is optional, and without it the scripts fall back to their defaults.",
                     "PyYAML is optional: the scripts fall back to the defaults without it.",
                     "- **Soft runtime deps** – `gh` CLI (sync), PyYAML (config), `git`.",
                     "PyYAML is recommended.", "PyYAML isn't needed.", "PyYAML need not be there.",
                     "Without PyYAML the scripts degrade to their defaults.",
                     "PyYAML is used when present."):
            with self.subTest(soft=soft):
                said = _pyyaml_statements([soft])
                self.assertTrue([s for s in said if _calls_pyyaml_optional(s)])
                self.assertEqual([], [s for s in said if _calls_pyyaml_required(s)])
        for held in ("A missing PyYAML is refused, never read as defaults.",
                     "A command without PyYAML refuses rather than answering from the defaults.",
                     "**Context:** PyYAML was a soft dependency.",
                     "PyYAML is required; `lizard` is soft and degrades to defaults."):
            with self.subTest(held=held):
                said = _pyyaml_statements([held])
                self.assertEqual([], [s for s in said if _calls_pyyaml_optional(s)])
        for page in SPEC_PAGES:
            text = _read(page).split("\n## Revision History", 1)[0]
            units = _units(text)
            said = _pyyaml_statements(units)
            with self.subTest(page=page.name):
                self.assertEqual([], [u for u in units if _STDLIB_ONLY.search(u)])
                self.assertEqual([], [s for s in said if _calls_pyyaml_optional(s)])
                self.assertTrue([s for s in said if _calls_pyyaml_required(s)],
                                f"{page.name} names PyYAML nowhere as required")
        wont = _section(_trd_body(), "Won't Have (This Version)")
        for bullet in re.split(r"\n(?=- )", wont):
            if re.search(r"(?i)required third-party", bullet):
                with self.subTest(bullet=bullet[:60]):
                    self.assertRegex(bullet, r"other than PyYAML")

    def test_the_trd_records_the_pyyaml_ruling_and_its_threat_row(self) -> None:
        """AC2. Mutants: no ADR citing D0505 and RFC0066, or one not Accepted, or not saying
        the installers and the prerequisite check refuse; no threat row for a missing or
        tampered PyYAML, or one with no mitigation; the supply-chain row still reading pure
        stdlib with no package to compromise; a shipped script loading YAML other than through
        `yaml.safe_load`, which the threat row says it never does."""
        with mock.patch.dict(sys.modules, {"yaml": None}):
            self.assertIn("PyYAML is required", gate.pyyaml_refusal() or "")
        body = _trd_body()
        adrs = re.split(r"\n(?=### ADR-\d{3}:)", _section(body, "11. Architecture Decision Records"))
        cited = [a for a in adrs if "D0505" in a and "RFC0066" in a]
        self.assertEqual(1, len(cited), "one ADR cites D0505 and RFC0066")
        status = re.search(r"^\*\*Status:\*\*\s*(.*)$", cited[0], re.M)
        self.assertTrue(status and status.group(1).startswith("Accepted"))
        flat = " ".join(cited[0].split())
        self.assertRegex(flat, r"`install\.sh` and `install\.ps1` refuse")
        self.assertRegex(flat, r"prerequisite check \(`gate\.py`\) refuses")
        rows = [r for r in _threat_rows() if "PyYAML" in r[0]]
        self.assertEqual(1, len(rows), "no Threat Model row for PyYAML")
        self.assertRegex(rows[0][0], r"(?i)missing")
        self.assertRegex(rows[0][0], r"(?i)tampered")
        mitigation = " ".join(rows[0][3].split())
        self.assertIn("`yaml.safe_load`", mitigation)
        self.assertIn("refuse", mitigation)
        supply = next(r for r in _threat_rows() if r[0].startswith("Supply-chain"))
        self.assertNotRegex(supply[3], r"(?i)pure stdlib|no third-party packages? to compromise")
        self.assertIn("PyYAML", supply[3])
        loads = [f"{path.name}:{n}" for path in _shipped_scripts()
                 for n, line in enumerate(_read(path).splitlines(), 1)
                 if re.search(r"\byaml\.(?:load|unsafe_load|full_load|load_all)\(|yaml\.Loader\b",
                              line)]
        self.assertEqual([], loads, "a shipped script loads YAML past `yaml.safe_load`")


if __name__ == "__main__":
    unittest.main()
