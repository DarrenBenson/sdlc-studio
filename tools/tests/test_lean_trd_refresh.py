"""CR0645 (EP0293): the TRD describes what 6.2 builds. The type sets this module checks are read
from the code that decides them (LL0043), never typed here, and each is checked to hold a member
known to be in it before it is compared, so an empty read cannot pass as agreement.

US1099: which types execute their `- **Verify:**` lines is `sdlc_md.EXECUTES_VERIFIERS`. The TRD
names that set as the authority, and its table gives each type in it as executed and each type
the creators refuse a command-shaped `Verify:` on as refused; both sets are compared here with the
code. The two code comments that said only a story executes its verifier, and the refusal the
filer prints, name the set instead.

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
import file_finding  # noqa: E402
import lessons  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
