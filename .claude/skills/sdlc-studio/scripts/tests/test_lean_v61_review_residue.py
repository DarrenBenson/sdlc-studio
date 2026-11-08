"""BG0936: the v6.1 review residue (D0326, D0333).

Four low findings the v6.1 reviews raised that no unit carried:

- `goal-review record`'s two "no seat" refusals were pinned only on a shared word, so either
  could print the other's text; and a fields-file `seats` entry that is not an object was
  dropped, so `["qa|yes|x|yes"]` was refused as a list that "holds none" (BG0933).
- nothing pinned that the newest transcript is chosen by time rather than by listing order
  (BG0932).
- the goal-note ratio parser backtracked quadratically on a long punctuation run straight
  after a measure name, about 2.5 s on 8,000 characters (BG0922).
- the TRD's `.local` table named writers no reader could find: `project orchestration` and
  `review workflow`, for files the agent writes while running a shipped workflow (US0984).

Each is driven through what the user meets: `sprint.py goal-review record`, the token meter
`run_state.session_tokens`, the real close, and the TRD as committed.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import ast
import fnmatch
import functools
import json
import os
import re
import sys
import tempfile
import time
import unittest
import unittest.mock
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - the close fixture, shared
import test_lean_goal_note_ratio_numeric as numeric  # noqa: E402 - by module, not re-collected
from test_lean_goal_review_fields_keys import _sprint  # noqa: E402

SKILL = Path(__file__).resolve().parents[2]
REPO = Path(__file__).resolve().parents[5]
TRD = REPO / "sdlc-studio" / "trd.md"
SEAT = {"seat": "qa", "achievable": "yes", "done_means": "the page is signed",
        "one_increment": "yes"}


def _local_rows(text: str) -> list[tuple[str, str]]:
    """(file, writer cell) for every row of each table under a heading naming `.local`."""
    parts = re.split(r"(?m)^(#+ .*)$", text)
    rows = []
    for i in range(1, len(parts), 2):
        if ".local" not in parts[i]:
            continue
        for row in parts[i + 1].splitlines():
            cells = row.split("|")
            first = _BARE_CELL_RE.fullmatch(cells[1]) if len(cells) > 3 else None
            if first:
                rows.append((first.group(1), cells[2]))
    return rows


#: A `.local` row's first cell naming one bare file, which `_local_rows` reads.
_BARE_CELL_RE = re.compile(r"\s*`([\w.-]+\.\w+)`\s*")
#: US1138: a backticked path in a row's first cell, `lane/` or `briefs/<unit>-qa.txt`.
_PATH_SPAN_RE = re.compile(r"`([^`\s]*/[^`\s]*)`")
#: A table's separator line.
_SEPARATOR_RE = re.compile(r"\|(?:\s*:?-+:?\s*\|)+\s*")


def _local_cells(text: str) -> list[list[str]]:
    """The cells of each body row of each table under a heading naming `.local`: every table line
    but a header, the line above a separator, and the separator."""
    parts = re.split(r"(?m)^(#+ .*)$", text)
    out = []
    for i in range(1, len(parts), 2):
        if ".local" not in parts[i]:
            continue
        lines = parts[i + 1].splitlines()
        for j, line in enumerate(lines):
            if (line.startswith("|") and not _SEPARATOR_RE.fullmatch(line)
                    and not (j + 1 < len(lines) and _SEPARATOR_RE.fullmatch(lines[j + 1]))
                    and len(cells := line.split("|")) > 3):
                out.append(cells)
    return out


def _local_path_rows(text: str) -> list[tuple[str, str]]:
    """US1138: (path, writer cell) for each backticked path in the first cell of a `.local` row
    `_local_rows` does not read: `lane/`, `briefs/<unit>-qa.txt`."""
    return [(span, cells[2]) for cells in _local_cells(text)
            if not _BARE_CELL_RE.fullmatch(cells[1]) for span in _PATH_SPAN_RE.findall(cells[1])]


def _unread_rows(text: str) -> list[str]:
    """The first cell of each `.local` row that neither `_local_rows` nor `_local_path_rows`
    reads, so a row the pins skip fails rather than passing unread."""
    return [cells[1].strip() for cells in _local_cells(text)
            if not _BARE_CELL_RE.fullmatch(cells[1]) and not _PATH_SPAN_RE.search(cells[1])]


# US1100: the pin reads whether a writer WRITES the file, not whether its source spells the name.
# A script writes it when one of its calls `_is_write` passes a path expression for the file
# (`_Writes._path`), or calls a function that does, in its own module or, as `module.func` or an
# imported name, in a module it imports that also spells the file. A path expression starts from
# a seed: a string constant whose last `/` segment is the file name, and, when the pin names a
# directory, whose own text or `/` join puts that directory directly above it (BG1163). A page
# writes it when one of its lines names the file beside a word `_PAGE_WRITE_RE` matches, in a
# clause `_PAGE_NEGATION_RE` does not negate. The pin counts a script's write only where it runs
# (`_Writes.live_calls`): at module level, or in a def shipped code refers to.
#: Path methods that write the path they are called on.
_PATH_WRITE_METHODS = ("write_text", "write_bytes")
#: `src.replace(dst)` and `src.rename(dst)` write their one argument; `os.replace(src, dst)` and
#: these `shutil` calls write their second.
_MOVE_METHODS = ("replace", "rename")
_MOVE_CALLS = {"os": ("replace", "rename"), "shutil": ("move", "copy", "copy2", "copyfile")}
#: An `open` mode that writes.
_WRITE_MODE_RE = re.compile(r"[wax+]")
#: US1138: an `os.open` flag that writes, as `cursor_usage_hook.py` appends its ledger.
_OS_WRITE_FLAGS = frozenset({"O_WRONLY", "O_RDWR", "O_APPEND", "O_CREAT", "O_TRUNC"})
#: A helper whose name joins one of these to another word (`atomic_write`, `append_history`,
#: `write_report`) writes each path it is passed; a bare `append` or `write` is a list or a handle.
_WRITE_WORDS = frozenset({"write", "append", "save"})
#: Calls whose result is still read as the path they are given, the sibling `with_name` or
#: `with_suffix` returns included.
_PATH_CALLS = frozenset({"Path", "PurePath", "PurePosixPath", "str", "fspath", "under_root",
                         "with_name", "with_suffix", "resolve", "absolute", "expanduser"})
#: A word that, on a page line naming the file, tells the agent to write it.
_PAGE_WRITE_RE = re.compile(r"\b(?:writes?|written|updates?|saves?|appends?|records?)\b", re.I)
#: BG1163: a word that, in the clause holding the write word, says the page does NOT write it
#: ('does not write', 'never records', "doesn't save", 'no longer updates', 'writes nothing').
_PAGE_NEGATION_RE = re.compile(r"\b(?:not|never|no|nor|cannot|nothing)\b|n't\b", re.I)
#: Where a page line's clauses part: a semicolon, a sentence stop, a colon or a spaced hyphen.
_PAGE_CLAUSE_RE = re.compile(r";|[.!?:](?=\s)|\s-\s")
#: BG1163: the directory the `.local` table documents. A row's file is matched by its path, so a
#: file moved out of `.local/` is not read as the row's file.
LOCAL_DIR = ".local"


def _imports(nodes: list[ast.AST]) -> tuple[dict[str, str], dict[str, tuple[str, str]]]:
    """({alias: module file}, {imported name: (module file, name)}) from a module's import nodes,
    deferred ones included; `from lib import run_state as rs` maps `rs` to `run_state.py`."""
    mods, names = {}, {}
    for n in nodes:
        if isinstance(n, ast.Import):
            for a in n.names:
                mods[a.asname or a.name.split(".")[0]] = a.name.rsplit(".", 1)[-1] + ".py"
        elif n.module:
            for a in n.names:
                if n.module.split(".")[-1] == "lib":
                    mods[a.asname or a.name] = a.name + ".py"
                else:
                    names[a.asname or a.name] = (n.module.rsplit(".", 1)[-1] + ".py", a.name)
    return mods, names


#: The nodes `_Writes._pass` reads; every other node is only walked through.
_READ = (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr, ast.Return, ast.Call)
_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)
#: The callees `_Writes._is_write` or the `add_argument` read can match on their name alone.
_CALLEES = frozenset({"open", "add_argument", *_PATH_WRITE_METHODS, *_MOVE_METHODS,
                      *(c for calls in _MOVE_CALLS.values() for c in calls)})


@functools.lru_cache(maxsize=None)
def _compound_write(callee: str) -> bool:
    """Whether `callee` joins a `_WRITE_WORDS` word to another (`atomic_write`, not `write`)."""
    words = callee.strip("_").split("_")
    return len(words) > 1 and bool(_WRITE_WORDS.intersection(words))


@functools.lru_cache(maxsize=None)
def _index(source: str) -> tuple:
    """(scopes, imports, joins) for a module's source, read in one walk. A scope, the
    module first and then each def, is [node, its `_READ` nodes, the names and attributes it
    uses, its string constants]; a def's body is its own scope, and the nodes a lambda or a class
    holds outside a def belong to none. `joins` is every `/` join whose right side is a string."""
    tree = ast.parse(source)
    scopes, imports, joins = {id(tree): [tree, [], set(), []]}, [], []
    stack = [(tree, scopes[id(tree)])]
    while stack:
        node, scope = stack.pop()
        for child in ast.iter_child_nodes(node):
            if scope is not None:
                if isinstance(child, _READ):
                    scope[1].append(child)
                if isinstance(child, ast.Name):
                    scope[2].add(child.id)
                elif isinstance(child, ast.Attribute):
                    scope[2].add(child.attr)
                elif isinstance(child, ast.Constant) and isinstance(child.value, str):
                    scope[3].append(child)
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                imports.append(child)
            elif (isinstance(child, ast.BinOp) and isinstance(child.op, ast.Div)
                  and isinstance(child.right, ast.Constant) and isinstance(child.right.value, str)):
                joins.append(child)
            if isinstance(child, _DEFS):
                inner = scopes[id(child)] = [child, [], set(), []]
            elif isinstance(child, (ast.Lambda, ast.ClassDef)):
                inner = None
            else:
                inner = scope
            stack.append((child, inner))
    return list(scopes.values()), _imports(imports), joins


class _Writes:
    """Which of `sources` ({file name: text}) write the file `name`; see the comment above. A scope
    using none of the names the analysis has bound, and holding no seed, is skipped: nothing in it
    can be a path expression or a call to a writer."""

    def __init__(self, sources: dict[str, str], name: str, under: str | None = None) -> None:
        self.sources, self.name, self.under = sources, name, under
        self.mods: dict[str, dict] = {}

    def _modules(self, start: str) -> list[str]:
        """`start` and, transitively, each module it imports that `sources` holds and that spells
        the file name."""
        out, todo = [], [start]
        while todo:
            m = todo.pop()
            if m in out or m not in self.sources:
                continue
            out.append(m)
            mods, names = _index(self.sources[m])[1]
            todo += [f for f in [*mods.values(), *(f for f, _ in names.values())]
                     if self.name in self.sources.get(f, "")]
        return out

    def _setup(self, m: str) -> None:
        scopes, imports, _joins = _index(self.sources[m])
        seeds = _seeds(self.sources[m], self.name, self.under)
        self.mods[m] = {
            "seeds": seeds, "imports": imports, "glob": set(),
            "dests": set(), "paths": set(), "writers": set(), "calls": [], "scope_of": {},
            "scopes": [(s, read, used, set(), any(id(n) in seeds for n in strings))
                       for s, read, used, strings in scopes]}

    def _bound(self, m: str) -> set[str]:
        """The names whose use can make a scope of `m` hold a path expression or a write."""
        st = self.mods[m]
        mods, imported = st["imports"]
        out = st["glob"] | st["dests"] | st["paths"] | st["writers"]
        for f in set(mods.values()):
            out |= self._of(f, "paths") | self._of(f, "writers")
        return out | {a for a, (f, n) in imported.items()
                      if n in self._of(f, "paths") | self._of(f, "writers")}

    def _of(self, alias_file: str | None, key: str) -> set[str]:
        """`key` of an imported module, read only when it spells the file name, as `_modules`
        reaches; a cited writer analysed earlier must not answer for one that does not."""
        if alias_file in self.mods and self.name in self.sources[alias_file]:
            return self.mods[alias_file][key]
        return set()

    def _path(self, m: str, e: ast.AST, names: set[str]) -> bool:
        """Whether `e` is a path expression for the file in module `m`, with `names` bound to one:
        a seed string; a name an assignment in the same function, or at module level, binds to
        one; `x.<dest>` of an `add_argument` whose default is one; a call to a function returning
        one; or a `/` join, an attribute or a `_PATH_CALLS` call taken on one."""
        st = self.mods[m]
        mods, imported = st["imports"]
        if isinstance(e, ast.Constant):
            return id(e) in st["seeds"]
        if isinstance(e, ast.Name):
            return e.id in names or e.id in st["glob"]
        if isinstance(e, ast.Attribute):
            return ((e.attr in st["dests"] and isinstance(e.value, ast.Name))
                    or self._path(m, e.value, names))
        if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Div):
            return self._path(m, e.left, names) or self._path(m, e.right, names)
        if isinstance(e, ast.IfExp):
            # US1138: `run_state._memo_path` returns the memo's path or None.
            return self._path(m, e.body, names) or self._path(m, e.orelse, names)
        if not isinstance(e, ast.Call):
            return False
        f = e.func
        if isinstance(f, ast.Name):
            f_file, f_name = imported.get(f.id, (None, None))
            if f.id in st["paths"] or f_name in self._of(f_file, "paths"):
                return True
            callee = f.id
        elif isinstance(f, ast.Attribute):
            if isinstance(f.value, ast.Name) and f.attr in self._of(mods.get(f.value.id), "paths"):
                return True
            if f.attr in _PATH_CALLS and self._path(m, f.value, names):
                return True
            callee = f.attr
        else:
            return False
        return callee in _PATH_CALLS and any(self._path(m, a, names) for a in e.args)

    def _is_write(self, m: str, c: ast.Call, names: set[str]) -> bool:
        """Whether call `c` writes the file: `_PATH_WRITE_METHODS` or a writing `open` on a path
        expression, a move or copy onto one, a `_WRITE_WORDS` helper passed one, or a call to a
        function that writes it."""
        st = self.mods[m]
        mods, imported = st["imports"]
        f = c.func

        def path(e: ast.AST) -> bool:
            return self._path(m, e, names)

        def writes_mode(i: int) -> bool:
            mode = next((k.value for k in c.keywords if k.arg == "mode"),
                        c.args[i] if len(c.args) > i else None)
            return (isinstance(mode, ast.Constant) and isinstance(mode.value, str)
                    and bool(_WRITE_MODE_RE.search(mode.value)))

        if isinstance(f, ast.Name):
            if f.id == "open":
                return bool(c.args) and path(c.args[0]) and writes_mode(1)
            f_file, f_name = imported.get(f.id, (None, None))
            if f.id in st["writers"] or f_name in self._of(f_file, "writers"):
                return True
            callee = f.id
        elif isinstance(f, ast.Attribute):
            if f.attr in _PATH_WRITE_METHODS:
                return path(f.value)
            if f.attr == "open" and path(f.value):
                return writes_mode(0)
            if f.attr == "open" and isinstance(f.value, ast.Name) and f.value.id == "os":
                return (len(c.args) > 1 and path(c.args[0]) and any(
                    (n.attr if isinstance(n, ast.Attribute) else getattr(n, "id", None))
                    in _OS_WRITE_FLAGS for n in ast.walk(c.args[1])))
            if isinstance(f.value, ast.Name) and f.attr in _MOVE_CALLS.get(f.value.id, ()):
                return len(c.args) == 2 and path(c.args[1])
            if f.attr in _MOVE_METHODS:
                return len(c.args) == 1 and not c.keywords and path(c.args[0])
            if isinstance(f.value, ast.Name) and f.attr in self._of(mods.get(f.value.id), "writers"):
                return True
            callee = f.attr
        else:
            return False
        return _compound_write(callee) and any(path(a) for a in [*c.args,
                                                                  *(k.value for k in c.keywords)])

    def _pass(self, m: str) -> bool:
        """One pass over module `m`; whether it bound anything new."""
        st = self.mods[m]

        def size() -> tuple:
            return (len(st["glob"]), len(st["dests"]), len(st["paths"]), len(st["writers"]),
                    sum(len(s[3]) for s in st["scopes"]))

        before, bound, calls = size(), self._bound(m), []
        for scope, nodes, used, local, seeded in st["scopes"]:
            names = st["glob"] if isinstance(scope, ast.Module) else local
            if not (seeded or names or used & bound):
                continue
            for n in nodes:
                if isinstance(n, ast.Call):
                    f = n.func
                    callee = (f.id if isinstance(f, ast.Name)
                              else f.attr if isinstance(f, ast.Attribute) else "")
                    if not (callee in _CALLEES or callee in bound or _compound_write(callee)):
                        continue
                    if (callee == "add_argument"
                            and any(k.arg == "default" and self._path(m, k.value, names)
                                    for k in n.keywords)):
                        dest = next((k.value.value for k in n.keywords if k.arg == "dest"), None)
                        flag = next((a.value for a in n.args if isinstance(a, ast.Constant)
                                     and str(a.value).startswith("--")), "")
                        st["dests"].add(dest or flag.lstrip("-").replace("-", "_"))
                    if self._is_write(m, n, names):
                        calls.append(n)
                        st["scope_of"][id(n)] = scope
                        if not isinstance(scope, ast.Module):
                            st["writers"].add(scope.name)
                    continue
                value, targets = getattr(n, "value", None), []
                if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                    targets = n.targets if isinstance(n, ast.Assign) else [n.target]
                if value is not None and targets and self._path(m, value, names):
                    names.update(t.id for tgt in targets for t in ast.walk(tgt)
                                 if isinstance(t, ast.Name))
                if (isinstance(n, ast.Return) and n.value is not None
                        and not isinstance(scope, ast.Module) and self._path(m, n.value, names)):
                    st["paths"].add(scope.name)
        st["calls"] = calls
        return before != size()

    def write_calls(self, module: str) -> list[ast.Call]:
        """The calls in `module` that write the file, once every module it reaches has settled."""
        mods = self._modules(module)
        for m in mods:
            if m not in self.mods:
                self._setup(m)
        while any([self._pass(m) for m in mods]):
            pass
        return self.mods[module]["calls"] if module in self.mods else []

    def live_calls(self, module: str) -> list[ast.Call]:
        """BG1163: the `write_calls` of `module` that run - at module level, or in a def that some
        `.py` source refers to outside the def's own body: a call, a `func=` a parser dispatches
        to, a table entry. In `module` itself a bare name or an attribute (`self.save`) refers
        to it; elsewhere `alias.name` of an import of `module`, or a name imported from it."""
        calls = self.write_calls(module)
        scope_of = self.mods[module]["scope_of"] if module in self.mods else {}
        live = {id(s): isinstance(s, ast.Module) or self._referred_to(module, s)
                for s in {id(s): s for s in scope_of.values()}.values()}
        return [c for c in calls if live[id(scope_of[id(c)])]]

    def _referred_to(self, module: str, fn: ast.AST) -> bool:
        inside = range(fn.lineno, fn.end_lineno + 1)
        for n in _refs(self.sources[module]).get(fn.name, ()):
            if n.lineno not in inside:
                return True
        for other, text in self.sources.items():
            if other == module or not other.endswith(".py") or fn.name not in text:
                continue
            mods, names = _index(text)[1]
            aliases = {a for a, f in mods.items() if f == module}
            imported = {a for a, (f, n) in names.items() if f == module and n == fn.name}
            for n in _refs(text).get(fn.name, ()):
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                        and n.value.id in aliases:
                    return True
            if any(_refs(text).get(a) for a in imported):
                return True
        return False


@functools.lru_cache(maxsize=None)
def _seeds(source: str, name: str, under: str | None) -> frozenset[int]:
    """The ids, in `_index`'s tree of `source`, of the string constants that spell the file: its
    name as the last `/` segment, and, under a directory, that directory as the segment above it
    in the constant's own text (`'sdlc-studio/.local/x.json'`) or as the last segment of the `/`
    join's left side (`root / '.local' / 'x.json'`, `Path('.local') / 'x.json'`)."""
    if name not in source:
        return frozenset()
    scopes, _imports, joins = _index(source)
    out = {id(n) for _s, _r, _u, strings in scopes for n in strings
           if (segments := n.value.split("/"))[-1] == name
           and (under is None or segments[-2:-1] == [under])}
    if under is not None:
        out |= {id(j.right) for j in joins
                if j.right.value == name and _last_segment(j.left) == under}
    return frozenset(out)


def _last_segment(e: ast.AST) -> str | None:
    """The last path segment a `/` join's left side ends in, when its text says: a string, the
    right side of a join, or the last argument of a `Path` call; None for anything else."""
    if isinstance(e, ast.Constant) and isinstance(e.value, str):
        return e.value.rstrip("/").rsplit("/", 1)[-1]
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Div):
        return _last_segment(e.right)
    if (isinstance(e, ast.Call) and isinstance(e.func, ast.Name)
            and e.func.id in ("Path", "PurePath", "PurePosixPath") and e.args):
        return _last_segment(e.args[-1])
    return None


@functools.lru_cache(maxsize=None)
def _refs(source: str) -> dict[str, list[ast.AST]]:
    """{name: the nodes that load it}: each `Name` read and each attribute taken, by its name."""
    out: dict[str, list[ast.AST]] = {}
    for n in ast.walk(ast.parse(source)):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            out.setdefault(n.id, []).append(n)
        elif isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Load):
            out.setdefault(n.attr, []).append(n)
    return out


def _page_writes(text: str, name: str) -> bool:
    """Whether a line of the page names `name` and has a clause holding a word `_PAGE_WRITE_RE`
    matches and none `_PAGE_NEGATION_RE` matches: 'does not write `x`' is no write (BG1163)."""
    return any(name in line and any(_PAGE_WRITE_RE.search(c) and not _PAGE_NEGATION_RE.search(c)
                                    for c in _PAGE_CLAUSE_RE.split(line))
               for line in text.splitlines())


def _shipped_sources() -> dict[str, str]:
    """{file name: text} for each shipped script (tests excluded) and reference or help page."""
    files = [p for p in (SKILL / "scripts").rglob("*.py") if "tests" not in p.parts]
    files += list(SKILL.glob("reference-*.md")) + list((SKILL / "help").glob("*.md"))
    return {p.name: p.read_text(encoding="utf-8") for p in files}


def _cited(writer: str) -> list[str]:
    """The script and page file names a writer cell backticks."""
    return [Path(c).name for c in re.findall(r"`([\w/.-]+\.(?:py|md))`", writer)]


def _pin_failures(rows: list[tuple[str, str]], sources: dict[str, str]) -> list[str]:
    """One line per `.local` row whose writer cell names no shipped script or page, names one
    `sources` lacks, or names one that does not write the row's file. Every cited writer must
    write it, so a row naming a caller beside the library holds the caller too. The file is the
    one under `LOCAL_DIR`, and a script's write counts only where it runs (BG1163)."""
    out = []
    for name, writer in rows:
        cited, writes = _cited(writer), _Writes(sources, name, LOCAL_DIR)
        if not cited:
            out.append(f"{name}: the writer cell {writer.strip()!r} names no script or page")
        for c in cited:
            if c not in sources:
                out.append(f"{name}: `{c}` is no shipped script or workflow page")
            elif c.endswith(".md") and not _page_writes(sources[c], name):
                out.append(f"{name}: `{c}` has no line telling the agent to write it")
            elif c.endswith(".py") and not writes.write_calls(c):
                out.append(f"{name}: `{c}` does not write it")
            elif c.endswith(".py") and not writes.live_calls(c):
                defs = sorted({s.name for s in map(writes.mods[c]["scope_of"].get,
                                                   map(id, writes.write_calls(c)))})
                out.append(f"{name}: `{c}` writes it only in {', '.join(defs)}, which nothing "
                           f"calls")
    return out


# US1138: a `.local` row whose first cell is a path, `lane-runs/<unit>/<session>.json`,
# `lane/landed/<worktree>/`, rather than one bare file name. The span is read segment by segment
# under `LOCAL_DIR`, a `<placeholder>` standing for any text, and a span ending in `/` as a
# directory written inside. A cited script writes the path when one of its writing calls
# (`_written`) is given an expression whose segments (`_segments`) match the span and no deeper
# span of the table (`_claims`), at module level or in a def shipped code refers to; it is read
# in its own code, a caller beside it not followed. A cell saying the script `directs` the agent
# that writes the path holds the script to a string it builds that tells the reader to.
#: A writer cell saying the script it cites only directs the agent that writes the path.
_DIRECTS_RE = re.compile(r"\bdirects?\b")
#: A path segment the code does not spell.
_WILD = "*"
_PATH_CTORS = ("Path", "PurePath", "PurePosixPath")


def _segments(e: ast.AST, env: dict[str, list[str]]) -> list[str] | None:
    """The path segments `e` spells, each a glob: a literal as itself, `*` for each value an
    f-string or a `.format` call fills in, `*` for a name `env` does not bind and for an attribute
    (`wt.name`); None for an expression that is no string or path."""
    if isinstance(e, ast.Constant):
        return [s for s in e.value.split("/") if s] if isinstance(e.value, str) else None
    if isinstance(e, ast.JoinedStr):
        return [s for s in _rendered(e, env).split("/") if s]
    if isinstance(e, ast.Name):
        return env.get(e.id, [_WILD])
    if isinstance(e, ast.Attribute):
        return [_WILD]
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Div):
        left, right = _segments(e.left, env), _segments(e.right, env)
        return None if left is None or right is None else left + right
    if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id in _PATH_CTORS:
        args = [_segments(a, env) for a in e.args]
        return None if any(a is None for a in args) else [s for a in args for s in a]
    if isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute) and e.func.attr == "format":
        base = _segments(e.func.value, env)
        return None if base is None else [re.sub(r"\{[^{}]*\}", _WILD, s) for s in base]
    return None


def _rendered(e: ast.JoinedStr, env: dict[str, list[str]]) -> str:
    """An f-string's text, each value it formats filled in as the literal path `env` binds it to,
    or `*`."""
    out = []
    for v in e.values:
        if isinstance(v, ast.Constant):
            out.append(v.value)
            continue
        segs = _segments(v.value, env)
        out.append("/".join(segs) if segs and _WILD not in "".join(segs) else _WILD)
    return "".join(out)


def _env(nodes: list[ast.AST], env: dict[str, list[str]],
         before: tuple[int, int] | None = None) -> dict[str, list[str]]:
    """`env` with each name an assignment among `nodes` ending before `before` binds, in source
    order: to the segments its value spells, or unbound when it spells none."""
    env = dict(env)
    for n in sorted((n for n in nodes if isinstance(n, (ast.Assign, ast.AnnAssign))
                     and n.value is not None), key=lambda n: (n.end_lineno, n.end_col_offset)):
        if before is not None and (n.end_lineno, n.end_col_offset) > before:
            break
        pairs = [(t, n.value) for t in (n.targets if isinstance(n, ast.Assign) else [n.target])]
        pairs += [p for t, v in pairs if isinstance(t, ast.Tuple) and isinstance(v, ast.Tuple)
                  and len(t.elts) == len(v.elts) for p in zip(t.elts, v.elts)]
        for t, v in pairs:
            if isinstance(t, ast.Name):
                segs = _segments(v, env)
                if segs is None:
                    env.pop(t.id, None)
                else:
                    env[t.id] = segs
    return env


def _opens_to_write(c: ast.Call, i: int) -> bool:
    """Whether an `open` call's mode, its `mode=` or its argument `i`, writes."""
    mode = next((k.value for k in c.keywords if k.arg == "mode"),
                c.args[i] if len(c.args) > i else None)
    return (isinstance(mode, ast.Constant) and isinstance(mode.value, str)
            and bool(_WRITE_MODE_RE.search(mode.value)))


def _written(c: ast.Call) -> list[ast.AST]:
    """The expressions call `c` writes, the shapes `_Writes._is_write` reads: the receiver of a
    `_PATH_WRITE_METHODS` call, a writing `open`'s file, a move or copy's target, or each argument
    of a `_WRITE_WORDS` helper."""
    f = c.func
    if isinstance(f, ast.Name):
        if f.id == "open":
            return c.args[:1] if _opens_to_write(c, 1) else []
        callee = f.id
    elif isinstance(f, ast.Attribute):
        os_call = isinstance(f.value, ast.Name) and f.value.id == "os"
        if f.attr in _PATH_WRITE_METHODS or (f.attr == "open" and not os_call):
            return [f.value] if f.attr != "open" or _opens_to_write(c, 0) else []
        if f.attr == "open":
            return c.args[:1] if len(c.args) > 1 and any(
                (n.attr if isinstance(n, ast.Attribute) else getattr(n, "id", None))
                in _OS_WRITE_FLAGS for n in ast.walk(c.args[1])) else []
        if isinstance(f.value, ast.Name) and f.attr in _MOVE_CALLS.get(f.value.id, ()):
            return c.args[1:2] if len(c.args) == 2 else []
        if f.attr in _MOVE_METHODS:
            return c.args[:1] if len(c.args) == 1 and not c.keywords else []
        callee = f.attr
    else:
        return []
    return [*c.args, *(k.value for k in c.keywords)] if _compound_write(callee) else []


def _matches(span: str, segs: list[str]) -> bool:
    """Whether `segs` hold `LOCAL_DIR` and then the span's segments: a literal the same, a lone
    `<placeholder>` any segment, a mixed one (`<unit>-qa.txt`) the same glob or a literal it
    fits; one more segment or deeper for a span ending in `/`, none for any other."""
    want = [re.sub(r"<[^<>]*>", _WILD, s) for s in span.split("/") if s]
    for i in (i for i, s in enumerate(segs) if s == LOCAL_DIR):
        rest = segs[i + 1:]
        if ((len(rest) > len(want)) if span.endswith("/") else (len(rest) == len(want))) and all(
                w in (_WILD, r) or (_WILD not in r and fnmatch.fnmatchcase(r, w))
                for w, r in zip(want, rest)):
            return True
    return False


def _claims(span: str, segs: list[str], spans: list[str]) -> bool:
    """Whether `segs` is `span`'s: it matches, and no span of `spans` with more segments does,
    so a write into `lane/landed/<worktree>/` is not read as one into `lane/`."""
    depth = len([s for s in span.split("/") if s])
    return _matches(span, segs) and not any(
        len([s for s in t.split("/") if s]) > depth and _matches(t, segs) for t in spans)


def _path_writes(sources: dict[str, str], module: str, span: str,
                 spans: list[str]) -> list[ast.Call]:
    """The calls in `module` that write a path `_claims` gives `span`, each read with the names
    assigned before it, at module level or in a def shipped code refers to."""
    if span.split("/", 1)[0].split("<", 1)[0] not in sources[module]:
        return []
    scopes = _index(sources[module])[0]
    menv, refs, out = _env(scopes[0][1], {}), _Writes(sources, span), []
    for node, nodes, _used, _strings in scopes:
        base = {} if isinstance(node, ast.Module) else menv
        calls = [c for c in nodes if isinstance(c, ast.Call) and any(
            (segs := _segments(p, _env(nodes, base, (c.lineno, c.col_offset)))) is not None
            and _claims(span, segs, spans) for p in _written(c))]
        if calls and (isinstance(node, ast.Module) or refs._referred_to(module, node)):
            out += calls
    return out


def _printed_writes(source: str, prefix: str) -> bool:
    """Whether a string the script builds, its f-string values filled in from the module's
    names, is a line `_page_writes` reads as telling the reader to write `prefix`."""
    scopes = _index(source)[0]
    env = _env(scopes[0][1], {})
    return any(_page_writes(_rendered(n, env) if isinstance(n, ast.JoinedStr) else n.value, prefix)
               for n in ast.walk(scopes[0][0]) if isinstance(n, ast.JoinedStr)
               or (isinstance(n, ast.Constant) and isinstance(n.value, str)))


def _path_pin_failures(rows: list[tuple[str, str]], sources: dict[str, str]) -> list[str]:
    """One line per path row whose writer cell names no shipped script or page, names one
    `sources` lacks, or names one that does not write the path: a page with no line telling the
    agent to write under it, a script the cell says `directs` the agent with no string telling
    the reader to, any other script with no `_path_writes` call."""
    spans, out = [s for s, _ in rows], []
    for span, writer in rows:
        cited, prefix = _cited(writer), f"{LOCAL_DIR}/{span.split('<', 1)[0]}"
        if not cited:
            out.append(f"{span}: the writer cell {writer.strip()!r} names no script or page")
        for c in cited:
            if c not in sources:
                out.append(f"{span}: `{c}` is no shipped script or workflow page")
            elif c.endswith(".md") and not _page_writes(sources[c], prefix):
                out.append(f"{span}: `{c}` has no line telling the agent to write it")
            elif c.endswith(".py") and _DIRECTS_RE.search(writer):
                if not _printed_writes(sources[c], prefix):
                    out.append(f"{span}: `{c}` prints nothing telling the agent to write it")
            elif c.endswith(".py") and not _path_writes(sources, c, span, spans):
                out.append(f"{span}: `{c}` does not write it where it runs")
    return out


def _blank(text: str, calls: list[ast.Call]) -> str:
    """`text` with the source of each outermost of `calls` replaced by `None`."""
    starts = [0]
    for line in text.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def at(line: int, col: int) -> int:
        """A character offset, from the 1-based line and the UTF-8 byte column `ast` gives."""
        return starts[line - 1] + len(text[starts[line - 1]:starts[line]].encode()[:col].decode())

    spans = sorted({(at(c.lineno, c.col_offset), at(c.end_lineno, c.end_col_offset))
                    for c in calls})
    outer = [s for i, s in enumerate(spans) if not any(o[0] <= s[0] and s[1] <= o[1]
                                                       for o in spans[:i])]
    for start, end in reversed(outer):
        text = text[:start] + "None" + text[end:]
    return text


def _stopped(writes: _Writes, writer: str) -> str:
    """`writer`'s text edited so it no longer writes the file `writes` reads: the source of each
    outermost call `writes` reads as writing it replaced by `None`, or, for a page, each line
    `_page_writes` reads dropped."""
    text, name = writes.sources[writer], writes.name
    if writer.endswith(".md"):
        return "\n".join(line for line in text.splitlines() if not _page_writes(line, name))
    return _blank(text, writes.write_calls(writer))


class V61ReviewResidueTests(unittest.TestCase):
    setUp = numeric.GoalNoteRatioNumericTests.setUp
    _close = numeric.GoalNoteRatioNumericTests._close
    named = staticmethod(numeric.GoalNoteRatioNumericTests.named)

    def _record(self, root: Path, fields: dict | None, *argv: str) -> tuple[int, str]:
        args = ["goal-review", "record", *argv, "--root", str(root)]
        if fields is not None:
            doc = root / "fields.json"
            doc.write_text(json.dumps(fields), encoding="utf-8")
            args += ["--fields-file", str(doc)]
        return _sprint(*args)

    def test_goal_review_refusals_are_distinct_and_name_a_bad_seat(self) -> None:
        """AC1. MUTANTS: either refusal printing the other's text (BG0933's test, which reads
        only the word 'seats' and the flag, passes both); the filter that drops an entry that
        is not an object, so `["qa|yes|x|yes"]` is refused as holding none and a list of one
        good seat and one string records the good one silently. The control: one good seat
        object still records."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sdlc-studio" / ".local").mkdir(parents=True)
            rc, no_file = self._record(root, None, "--goal", "one page is signed")
            self.assertEqual(2, rc, no_file)
            rc, no_seats = self._record(root, {"goal": "one page is signed", "seats": []})
            self.assertEqual(2, rc, no_seats)
            self.assertIn("pass --seat or a --fields-file 'seats' list", no_file)
            self.assertNotIn("holds none", no_file)
            self.assertIn("the --fields-file 'seats' list holds none and no --seat was given",
                          no_seats)
            self.assertNotIn("pass --seat or", no_seats)

            for seats in (["qa|yes|x|yes"], [SEAT, "qa|yes|x|yes"], [SEAT, 7]):
                with self.subTest(seats=seats):
                    rc, said = self._record(root, {"goal": "one page is signed", "seats": seats})
                    self.assertEqual(2, rc, said)
                    self.assertNotIn("holds none", said)
                    self.assertIn("refused", said)
                    self.assertIn(repr(seats[-1]), said, "the bad entry is not named")
                    self.assertIn("is not an object", said)
            self.assertFalse((root / "sdlc-studio" / ".local" / "goal-review.json").exists(),
                             "a seats list holding a bad entry recorded a round")

            rc, said = self._record(root, {"goal": "one page is signed", "seats": [SEAT]})
            self.assertEqual(0, rc, said)

    def test_the_newest_transcript_is_chosen_by_time(self) -> None:
        """AC2. MUTANTS: the last (or the first) entry in listing order, unsorted; the
        greatest name. The folder lists the newest in the middle and its name sorts first, so
        each of those reads a different file, and each file's total names which one was read."""
        run_state = lean._live("lib.run_state")
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            spec = (("b-old", 10, 1_000), ("a-new", 3_000, 3_000), ("c-mid", 200, 2_000))
            files = []
            for name, tokens, mtime in spec:
                f = folder / f"{name}.jsonl"
                f.write_text(json.dumps({"message": {"usage": {"input_tokens": tokens}}}) + "\n",
                             encoding="utf-8")
                os.utime(f, (mtime, mtime))
                files.append(f)
            listing = unittest.mock.patch.object(
                type(folder), "glob",
                lambda self, pattern: iter(files) if self == folder else iter(()))
            with listing:
                got = run_state.session_tokens(tmp, transcripts_dir=folder)
            self.assertEqual(3_000, got.get("tokens"), got)

    # A wall-clock bound measures the load beside other work, so a commit's pytest run leaves it
    # out and the push runs it, serially (BG0963); the hook's unittest fallback runs it (BG1144).
    @pytest.mark.serial_only
    @pytest.mark.boundary_only
    def test_the_note_parser_is_linear(self) -> None:
        """AC3. MUTANT: HEAD's pattern, whose lazy run after the name and the punctuation lead
        before the number both claim the same characters, so 8,000 of them straight after
        `tokens` with no ratio after them cost about 2.5 s. Timed around the close's own check,
        in the real close. The control: a wrong ratio earlier in the note is still named, so a
        check that reads nothing also fails."""
        mod = lean._live("sprint")
        real = mod.goal_note_contradiction
        spent: list[float] = []

        def timed(*a, **k):
            t = time.perf_counter()
            try:
                return real(*a, **k)
            finally:
                spent.append(time.perf_counter() - t)

        for i, run in enumerate(("(" * 8_000, "-" * 8_000, ":~" * 4_000)):
            with self.subTest(run=run[:2]), \
                    unittest.mock.patch.object(mod, "goal_note_contradiction", timed):
                spent.clear()
                rc, lines, ratio = self._close(f"long{i}", f"Tokens 1.4x over plan; tokens{run}")
                self.assertEqual("1.7x", ratio, "premise: the filed page derives 1.7x")
                self.assertEqual(0, rc, "\n".join(lines))
                self.assertEqual(1, len(spent), "the close did not check the note")
                self.assertLess(spent[0], 0.25, f"the note check took {spent[0]:.2f}s")
                named = self.named(lines)
                self.assertEqual(1, len(named), lines)
                self.assertIn("1.4x", named[0])

    def test_every_local_row_has_a_writer(self) -> None:
        """AC4. MUTANTS: HEAD's rows for project-state.json and review-queue.json, whose writer
        cells (`project orchestration`, `review workflow`) name nothing that writes them; a
        writer cell naming a script or workflow page that does not write the file. US1100 made
        the check `_pin_failures`: each backticked writer must write the file, not merely name it."""
        text = TRD.read_text(encoding="utf-8")
        rows = _local_rows(text)
        self.assertGreaterEqual(len(rows), 10, "premise: the TRD's .local table moved")
        self.assertEqual([], _pin_failures(rows, _shipped_sources()))
        # US1138: a row whose first cell is a path is read by `_path_pin_failures`, and no row
        # is read by neither
        self.assertGreaterEqual(len(_local_path_rows(text)), 4, "premise: the path rows moved")
        self.assertEqual([], _path_pin_failures(_local_path_rows(text), _shipped_sources()))
        self.assertEqual([], _unread_rows(text))


#: The file the fixtures below write, read or only mention.
PROBE = "probe-state.json"
#: (case, {file name: source}, the writer read, whether it writes `PROBE`). Each near miss names
#: the file in code or prose and does not write it; each control writes it one way a shipped
#: writer does.
_PROBES = (
    ("docstring", {"w.py": f'"""Writes {PROBE}."""\ndef f(root):\n    """Writes .local/{PROBE}."""\n'},
     "w.py", False),
    ("comment", {"w.py": f"# writes .local/{PROBE}\nx = 1\n"}, "w.py", False),
    ("read", {"w.py": f"def f(root):\n    p = root / '.local' / '{PROBE}'\n"
                      f"    return json.loads(p.read_text())\n"}, "w.py", False),
    ("open to read", {"w.py": f"def f(root):\n    with open(root / '{PROBE}', 'r') as fh:\n"
                              f"        return fh.read()\n"}, "w.py", False),
    ("legacy moved away", {"w.py": f"LEGACY = Path('.local') / '{PROBE}'\n"
                                   f"def migrate(root, dst):\n    src = root / LEGACY\n"
                                   f"    src.replace(dst)\n"}, "w.py", False),
    ("str.replace", {"w.py": f"def f(text):\n    return text.replace('{PROBE}', 'x.json')\n"},
     "w.py", False),
    ("a list append", {"w.py": f"def f(root):\n    rows = []\n    rows.append(root / '{PROBE}')\n"
                               f"    return rows\n"}, "w.py", False),
    ("another file written", {"w.py": f"def f(root):\n    p = root / '{PROBE}'\n"
                                      f"    q = root / 'other.json'\n"
                                      f"    q.write_text(p.read_text())\n"}, "w.py", False),
    ("path in a message", {"w.py": f"def f(root, out):\n"
                                   f"    out.write_text(f'see {{root}}/{PROBE}')\n"}, "w.py", False),
    ("write_text", {"w.py": f"def f(root):\n    (root / '.local' / '{PROBE}').write_text('x')\n"},
     "w.py", True),
    ("open to append", {"w.py": f"def f(root):\n    with open(root / '{PROBE}', 'a') as fh:\n"
                                f"        fh.write('x')\n"}, "w.py", True),
    ("os.replace onto it", {"w.py": f"def f(root, tmp):\n    os.replace(tmp, root / '{PROBE}')\n"},
     "w.py", True),
    ("os.open to append", {"w.py": f"def f(root):\n    fd = os.open(root / '{PROBE}', "
                                   f"os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)\n"}, "w.py", True),
    ("os.open to read", {"w.py": f"def f(root):\n    fd = os.open(root / '{PROBE}', os.O_RDONLY)\n"},
     "w.py", False),
    ("a conditional path saved", {"w.py": f"REL = Path('{PROBE}')\n"
                                          f"def path(root, on):\n    return root / REL if on else None\n"
                                          f"def go(root, s):\n    _save_memo(path(root, True), s)\n"},
     "w.py", True),
    ("a conditional of another file", {"w.py": f"# {PROBE}\ndef f(root, on):\n"
                                               f"    p = root / 'other.json' if on else None\n"
                                               f"    p.write_text('x')\n"}, "w.py", False),
    ("an argparse default", {"w.py": f"def main(argv):\n    ap = argparse.ArgumentParser()\n"
                                     f"    ap.add_argument('--out', default='.local/{PROBE}')\n"
                                     f"    args = ap.parse_args(argv)\n"
                                     f"    Path(args.out).write_text('x')\n"}, "w.py", True),
    ("a returned path, atomically", {"lib_w.py": f"REL = Path('.local') / '{PROBE}'\n"
                                                 f"def path(root):\n    return root / REL\n"
                                                 f"def save(root, s):\n    p = path(root)\n"
                                                 f"    sdlc_md.atomic_write(p, s)\n"},
     "lib_w.py", True),
)
#: Callers of `lib_w.py` above: one writes the file only by calling its `save`, one only reads.
_CALLERS = (("calls save", "import lib_w\ndef go(root):\n    lib_w.save(root, 'x')\n", True),
            ("reads the path", "import lib_w\ndef go(root):\n    return lib_w.path(root).read_text()\n",
             False))


class LocalWriterPinTests(unittest.TestCase):
    """US1100: the `.local` pin fails when a documented writer stops writing its file."""

    def test_a_writer_that_stops_writing_fails_the_pin(self) -> None:
        """AC3. MUTANTS: the pin reverted to BG0936's, which passes a writer whose source only
        names the file (the legacy `telemetry.jsonl` beside `telemetry.py`); `_Writes` reading a
        path in a docstring, a read, a rename away, a list append or a message as a write, or
        missing a shape a shipped writer uses. The control: every row of the TRD passes. Then each writer of each
        row is edited by `_stopped` so it no longer writes the file, alone, and the pin, read
        over a row naming that writer, names it."""
        sources = _shipped_sources()
        rows = _local_rows(TRD.read_text(encoding="utf-8"))
        self.assertIn("run-state.json", dict(rows), "premise: the TRD documents the run state")
        self.assertEqual([], _pin_failures(rows, sources))
        self.assertTrue(_pin_failures([("telemetry.jsonl", "`telemetry.py`")], sources),
                        "the pin passes the legacy name, which telemetry.py only reads")
        for name, writer in rows:
            writes = _Writes(sources, name, LOCAL_DIR)
            for cited in dict.fromkeys(_cited(writer)):
                with self.subTest(file=name, writer=cited):
                    stopped = {**sources, cited: _stopped(writes, cited)}
                    self.assertNotEqual(sources[cited], stopped[cited])
                    failures = _pin_failures([(name, f"`{cited}`")], stopped)
                    self.assertTrue(any(f"`{cited}`" in f for f in failures), failures)
        lib = dict(_PROBES[-1][1])
        for case, files, module, expected in (
                *_PROBES, *((c, {**lib, "c.py": src}, "c.py", w) for c, src, w in _CALLERS)):
            with self.subTest(case=case):
                self.assertEqual(expected, bool(_Writes(files, PROBE).write_calls(module)))
        # `x.py` writes only through `y.py`, which does not spell the file, so it is not read as a
        # writer; the verdict on it must not change when `y.py` is read before it.
        chain = {**lib, "y.py": "import lib_w\ndef go(root):\n    lib_w.save(root, 'x')\n",
                 "x.py": "import y\ndef run(root):\n    y.go(root)\n"}
        self.assertEqual([f"{PROBE}: `x.py` does not write it"],
                         _pin_failures([(PROBE, "`y.py`, `x.py`")], chain))
        self.assertEqual(_pin_failures([(PROBE, "`x.py`")], chain),
                         _pin_failures([(PROBE, "`y.py`, `x.py`")], chain))
        for line, expected in ((f"Read `{PROBE}` to resume.", False),
                               (f"Update `{PROBE}` with the step.", True)):
            with self.subTest(page=line):
                self.assertEqual(expected, _page_writes(line, PROBE))

    def test_an_uncalled_writer_or_a_moved_file_fails_the_pin(self) -> None:
        """BG1163 AC2. qa-seat-US1100-r1 removed both `note_brief(...)` calls from critic.py, and
        moved sprint.py's `GOAL_REVIEW_REL` out of `.local`: the pin stayed green, because it
        counted a def that writes the file whether or not anything calls it, and matched the
        file by its last path segment. MUTANTS: `_pin_failures` reading `write_calls` where it
        reads `live_calls`; `_Writes` built with no directory; `_seeds` taking the last segment
        alone; `_referred_to` counting a def's own recursive call. Each edit below is checked
        against its unedited control."""
        sources = _shipped_sources()
        for row, writer, edit in (
                ("briefs.jsonl", "critic.py", lambda t: _blank(t, [
                    c for c in ast.walk(ast.parse(t)) if isinstance(c, ast.Call)
                    and isinstance(c.func, ast.Name) and c.func.id == "note_brief"])),
                ("goal-review.json", "sprint.py", lambda t: t.replace(
                    'GOAL_REVIEW_REL = Path("sdlc-studio") / ".local" / "goal-review.json"',
                    'GOAL_REVIEW_REL = Path("sdlc-studio") / "goal-review.json"'))):
            with self.subTest(row=row, writer=writer):
                pin = [(row, f"`{writer}`")]
                self.assertEqual([], _pin_failures(pin, sources))
                edited = {**sources, writer: edit(sources[writer])}
                self.assertNotEqual(sources[writer], edited[writer], "premise: the edit missed")
                failures = _pin_failures(pin, edited)
                self.assertTrue(any(f"`{writer}`" in f for f in failures), failures)
        self.assertIn("which nothing calls", "\n".join(_pin_failures(
            [("briefs.jsonl", "`critic.py`")],
            {**sources, "critic.py": _blank(sources["critic.py"], [
                c for c in ast.walk(ast.parse(sources["critic.py"])) if isinstance(c, ast.Call)
                and isinstance(c.func, ast.Name) and c.func.id == "note_brief"])})))
        writer = (f"def save(root):\n    (root / '{LOCAL_DIR}' / '{PROBE}').write_text('x')\n")
        for case, files, writes in (
                ("an uncalled def", {"w.py": writer}, False),
                ("a def calling only itself", {"w.py": writer + "    save(root)\n"}, False),
                ("called at module level", {"w.py": writer + "save(None)\n"}, True),
                ("a parser dispatches to it", {"w.py": writer + "def main(ap):\n"
                                               "    ap.set_defaults(func=save)\n"
                                               "main(None)\n"}, True),
                ("called from another module", {"w.py": writer, "c.py": "import w\n"
                                                "w.save(None)\n"}, True),
                ("a written module-level path", {"w.py": f"from pathlib import Path\n"
                                                 f"Path('{LOCAL_DIR}/{PROBE}').write_text('x')\n"},
                 True),
                ("outside the directory", {"w.py": f"from pathlib import Path\n"
                                           f"(Path('sdlc-studio') / '{PROBE}').write_text('x')\n"},
                 False),
                ("a directory below it", {"w.py": f"from pathlib import Path\n"
                                          f"Path('{LOCAL_DIR}/sub/{PROBE}').write_text('x')\n"},
                 False),
                ("under a directory named like it", {"w.py": f"from pathlib import Path\n"
                                                     f"Path('x{LOCAL_DIR}/{PROBE}')"
                                                     f".write_text('x')\n"}, False)):
            with self.subTest(case=case):
                self.assertEqual(writes, not _pin_failures([(PROBE, "`w.py`")], files),
                                 _pin_failures([(PROBE, "`w.py`")], files))

    def test_a_negated_write_line_is_not_a_writer(self) -> None:
        """BG1163 AC4. A page line naming the file beside a write word read as an instruction to
        write it, 'does not write' and 'never records' included. MUTANT: `_page_writes` without
        the `_PAGE_NEGATION_RE` test. The control: a write word in a clause of its own still
        counts, beside a negated one."""
        for line, writes in ((f"This page does not write `{PROBE}`.", False),
                             (f"It never records `{PROBE}`.", False),
                             (f"The agent doesn't save `{PROBE}` here.", False),
                             (f"`{PROBE}` is no longer updated by hand.", False),
                             (f"It writes nothing to `{PROBE}`.", False),
                             (f"Update `{PROBE}` with the step.", True),
                             (f"Never edit it by hand; record the step in `{PROBE}`.", True),
                             (f"`{PROBE}` is not read here - the agent writes it.", True)):
            with self.subTest(line=line):
                self.assertEqual(writes, _page_writes(line, PROBE))
        page = {"reference-probe.md": f"# Probe\n\nThis workflow does not write `{PROBE}`.\n"
                                      f"It never records `{PROBE}` either.\n"}
        self.assertEqual([f"{PROBE}: `reference-probe.md` has no line telling the agent to "
                          f"write it"], _pin_failures([(PROBE, "`reference-probe.md`")], page))


#: US1138: a path row's fixture writer, `w.py`, as `lib/lanes.py` writes its records.
_RUNS = ("from pathlib import Path\nRUNS = Path('sdlc-studio') / '.local' / 'probe-runs'\n"
         "NOTE = '{unit}-qa.none'\n")


class LocalPathRowPinTests(unittest.TestCase):
    """US1138: a `.local` row naming a path, not one bare file, is held to its writer too."""

    def test_each_path_row_is_held_to_the_code_that_writes_it(self) -> None:
        """qa-seat-US1138-r1: `_local_rows` read a row only when its first cell was one bare file
        name, so the four path rows US1138 added were never read, and their writer cells set to
        `critic.py` stayed green. MUTANTS: `_unread_rows` reading nothing; `_path_pin_failures`
        not run; `_matches` taking a `<placeholder>` for a literal, a literal for a placeholder,
        or ignoring a span's suffix or trailing `/`; `_claims` not deferring to a deeper row;
        `_path_writes` counting an uncalled def; `_DIRECTS_RE` dropped. The control: every path
        row of the TRD passes. Then each is set to `critic.py`, and each code writer has the
        writes the pin found blanked, alone, and the pin names it."""
        text, sources = TRD.read_text(encoding="utf-8"), _shipped_sources()
        rows = _local_path_rows(text)
        spans = dict(rows)
        for span in ("lane-runs/<unit>/<session>.json", "lane/", "lane/landed/<worktree>/",
                     "briefs/<unit>-qa.txt", "briefs/<unit>-qa.none"):
            self.assertIn(span, spans, "premise: the TRD documents the lane state")
        self.assertEqual([], _path_pin_failures(rows, sources))
        self.assertTrue(_unread_rows("## `.local` files\n\n| File | Writer | Purpose |\n"
                                     "| --- | --- | --- |\n| lane runs | `lanes.py` | x |\n"),
                        "a row naming no file in backticks is read by neither reader")
        for span, writer in rows:
            mutant = writer.replace("`sprint.py`", "`critic.py`").replace("`lib/lanes.py`",
                                                                          "`critic.py`")
            with self.subTest(span=span, writer="critic.py"):
                self.assertNotEqual(writer, mutant, "premise: the row cites another script")
                failures = _path_pin_failures([(span, mutant)], sources)
                self.assertTrue(any("`critic.py`" in f for f in failures), failures)
            if _DIRECTS_RE.search(writer):
                continue
            for cited in dict.fromkeys(_cited(writer)):
                with self.subTest(span=span, stopped=cited):
                    calls = _path_writes(sources, cited, span, list(spans))
                    stopped = {**sources, cited: _blank(sources[cited], calls)}
                    self.assertNotEqual(sources[cited], stopped[cited])
                    failures = _path_pin_failures([(span, f"`{cited}`")], stopped)
                    self.assertTrue(any(f"`{cited}`" in f for f in failures), failures)
        # the hand-in the builder writes is not written by `sprint.py`'s code: a cell that does
        # not say the script directs the agent holds it to a write
        self.assertTrue(_path_pin_failures([("lane/", "`sprint.py`")], sources))

    def test_a_path_matches_only_what_its_span_names(self) -> None:
        """The fixture writer `w.py` writes, or does not write, under `.local/probe-runs/`; each
        near miss names the directory and writes elsewhere, or writes there and does not run."""
        live = "w.save(None, 'u', 's')\n"
        for case, body, span, writes in (
                ("the record", "def save(root, unit, s):\n"
                 "    (root / RUNS / unit / f'{s}.json').write_text('x')\n",
                 "probe-runs/<unit>/<session>.json", True),
                ("another suffix", "def save(root, unit, s):\n"
                 "    (root / RUNS / unit / f'{s}.out').write_text('x')\n",
                 "probe-runs/<unit>/<session>.json", False),
                ("one level short", "def save(root, unit, s):\n"
                 "    (root / RUNS / f'{s}.json').write_text('x')\n",
                 "probe-runs/<unit>/<session>.json", False),
                ("an unknown where a literal stands", "def save(root, d, s):\n"
                 "    (root / '.local' / d / f'{s}.json').write_text('x')\n",
                 "probe-runs/<session>.json", False),
                ("a literal fitting a placeholder", "def save(root, unit, s):\n"
                 "    (root / RUNS / 'a-qa.txt').write_text('x')\n",
                 "probe-runs/<unit>-qa.txt", True),
                ("a format template", "def save(root, unit, s):\n"
                 "    p = root / RUNS / NOTE.format(unit=unit)\n    sdlc_md.atomic_write(p, s)\n",
                 "probe-runs/<unit>-qa.none", True),
                ("a copy into the directory", "def save(root, unit, s):\n"
                 "    keep = root / RUNS / s\n    shutil.copy2(unit, keep / 'x.json')\n",
                 "probe-runs/", True),
                ("the directory alone", "def save(root, unit, s):\n"
                 "    (root / RUNS).mkdir(parents=True)\n", "probe-runs/", False),
                ("a read", "def save(root, unit, s):\n"
                 "    return (root / RUNS / unit / f'{s}.json').read_text()\n",
                 "probe-runs/<unit>/<session>.json", False),
                ("a name bound after the write", "def save(root, unit, s):\n"
                 "    p = root / 'x.json'\n    p.write_text('x')\n    p = root / RUNS / 'a.json'\n",
                 "probe-runs/<session>.json", False),
                ("outside .local", "def save(root, unit, s):\n"
                 "    (root / 'probe-runs' / f'{s}.json').write_text('x')\n",
                 "probe-runs/<session>.json", False)):
            for called in (True, False):
                files = {"w.py": _RUNS + body, "c.py": "import w\n" + live * called}
                with self.subTest(case=case, called=called):
                    self.assertEqual(writes and called,
                                     not _path_pin_failures([(span, "`w.py`")], files),
                                     _path_pin_failures([(span, "`w.py`")], files))
        # a write into a deeper row's directory is that row's, not its parent's
        deeper = {"w.py": _RUNS + "def save(root, unit, s):\n"
                              "    (root / RUNS / 'landed' / s / 'x.json').write_text('x')\n"
                              "save(None, 'u', 's')\n"}
        both = [("probe-runs/", "`w.py`"), ("probe-runs/landed/<worktree>/", "`w.py`")]
        self.assertEqual(["probe-runs/: `w.py` does not write it where it runs"],
                         _path_pin_failures(both, deeper))
        self.assertEqual([], _path_pin_failures(both[1:], deeper))

    def test_a_directing_script_is_held_to_its_printed_text(self) -> None:
        """A cell saying the script `directs` the agent holds it to a string, its module-level
        names filled in, that tells the reader to write under the path; a negated one does not."""
        cell = "the builder, as the brief `w.py` prints directs"
        for case, line, writes in (
                ("an instruction", "f'stop: write {HAND}/{NOTE} with what is done'", True),
                ("a negated one", "f'do not write {HAND}/{NOTE}'", False),
                ("the path alone", "f'see {HAND}/{NOTE}'", False),
                ("an unfilled name", "f'write {other}/{NOTE}'", False)):
            src = (f"HAND = 'sdlc-studio/.local/probe'\nNOTE = 'HANDOFF.md'\n"
                   f"def brief(other):\n    return {line}\n")
            with self.subTest(case=case):
                failures = _path_pin_failures([("probe/", cell)], {"w.py": src})
                self.assertEqual(writes, not failures, failures)


if __name__ == "__main__":
    unittest.main()
