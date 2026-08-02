#!/usr/bin/env python3
"""Audit the skill command surface against the process spine.

The surface has grown organically; this tool ENUMERATES every command and route
deterministically, maps each to the process spine, and assigns a keep / fold / retire
disposition - the map a cleanup acts on, kept re-runnable so the surface cannot silently
drift again. It does NOT itself retire anything (that is a reviewed, editorial step); it
produces the evidence.

The process spine (CR reference): raise a bug/CR/RFC/Issue -> break it down into the delivery
backlog -> run sprints with independent reviews. The top-level human levers are the documents
(PRD, TRD, TSD, Personas); reconcile / review / audit are support. A command that does not serve
that spine is a candidate to fold or retire.

Three signals feed the disposition, all structural (facts, not taste):
  - SPINE      : the curated category a command serves (or `unmapped` - a review candidate)
  - DRIFT      : a command in the help catalogue but not the SKILL Type Reference, or vice versa
  - TOOLING    : (with --check-tools) does the backing script's `--help` run? a dead route is a
                 help entry whose tool is broken or missing

Skill-development tool: it inspects the SKILL itself, so for a CONSUMING project (no SKILL.md
under the root) it is a no-op. Pure stdlib.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doc_coverage  # noqa: E402  (reuse the enumerators the gate already trusts)
from lib import sdlc_md  # noqa: E402

# The process-spine category each command serves. Curated - the one editorial input - so the
# disposition is reproducible and reviewable in one place. A command in the surface but absent
# here is reported `unmapped`, a fold/retire candidate for the human to rule on. Keep in sync as
# commands are added: a NEW command lands `unmapped` until it is placed, which is the nudge to ask
# "does this serve the spine?".
SPINE: dict[str, str] = {
    # RAISE - intake into the Discovery backlog
    "bug": "raise", "cr": "raise", "rfc": "raise", "issue": "raise",
    # BREAK DOWN - Discovery -> Delivery
    "refine": "break-down", "triage": "break-down", "epic": "break-down", "story": "break-down",
    # SPRINT + REVIEW - the delivery loop
    "sprint": "sprint+review", "handoff": "sprint+review", "review": "sprint+review",
    # LEVERS - the top-level human direction documents
    "prd": "lever", "trd": "lever", "tsd": "lever", "persona": "lever", "pvd": "lever",
    "consult": "lever", "chat": "lever",
    # SUPPORT - keep the backlog honest and visible
    "reconcile": "support", "status": "support", "hint": "support", "gate": "support",
    "decisions": "support", "lessons": "support", "audit": "support",
    # UTILITY / lifecycle - legitimate, off the delivery spine
    "init": "utility", "help": "utility", "skill-update": "utility", "upgrade": "utility",
    "migrate": "utility", "project": "utility", "repo": "utility", "plan": "utility",
    "code": "utility", "test-spec": "utility", "test-automation": "utility", "test-env": "utility",
    "deploy": "utility", "mutation": "utility", "retro": "utility",
}

# The spine categories, in the order the audit report groups them.
SPINE_ORDER = ("raise", "break-down", "sprint+review", "lever", "support", "utility", "unmapped")


# A folded command's signpost: it is NOT a catalogue entry. Folding takes a command out of the
# surface while keeping the route alive - an operator following an old habit lands on the command
# that replaced it instead of a dead end. Counting the signpost as a catalogue entry would make a
# fold indistinguishable from leaving the command in place, so these lines are stripped before the
# catalogue is enumerated, and parsed separately as redirects.
_REDIRECT_RE = re.compile(
    r"^- Folded: `/sdlc-studio ([a-z][a-z-]*)` -> `/sdlc-studio ([a-z][a-z-]*)`")


def _redirects(skill_dir: Path) -> dict[str, str]:
    """Folded command -> the command that replaced it, read from the help catalogue's redirect
    lines. One entry per folded command."""
    text = (skill_dir / "help" / "help.md").read_text(encoding="utf-8")
    return {m.group(1): m.group(2)
            for ln in text.splitlines() if (m := _REDIRECT_RE.match(ln))}


def _help_commands(skill_dir: Path) -> list[str]:
    """Distinct `/sdlc-studio <cmd>` tokens in the help catalogue - the commands an operator is
    actually told they can run. The complement of the Type Reference: a command in one but not the
    other is drift. Redirect lines are excluded: a signpost to a folded command's replacement is
    not an offer to run it."""
    text = (skill_dir / "help" / "help.md").read_text(encoding="utf-8")
    text = "\n".join(ln for ln in text.splitlines() if not _REDIRECT_RE.match(ln))
    # rstrip a trailing hyphen so `/sdlc-studio foo-` (a wrapped/placeholder token) does not mint a
    # phantom `foo-` command; empty captures are dropped.
    return sorted({t for m in re.finditer(r"/sdlc-studio ([a-z][a-z-]*)", text)
                   if (t := m.group(1).rstrip("-"))})


def _tool_alive(skill_dir: Path, name: str, timeout: float = 10.0) -> bool:
    """True when `scripts/<name>.py --help` exits 0 - the backing tool is present and parses. A
    command with no same-named script is not a dead route (many commands are natural-language
    routes, not a 1:1 script), so a missing script is reported UNKNOWN, never dead; only a script
    that exists and fails `--help` is a broken tool."""
    p = skill_dir / "scripts" / f"{name}.py"
    if not p.is_file():
        return None
    try:
        r = subprocess.run([sys.executable, str(p), "--help"],
                           capture_output=True, timeout=timeout)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def audit(repo_root: Path | str = ".", *, check_tools: bool = False) -> dict:
    """Enumerate the command surface and disposition each command. Returns
    `{applicable, commands: [{command, spine, in_type_ref, in_help, drift, tool, disposition}],
      scripts: {...}, summary: {...}}`. `check_tools` additionally runs each backing script's
    `--help` (slower; a subprocess per script)."""
    skill_dir = doc_coverage._skill_dir(Path(repo_root))
    if skill_dir is None:
        return {"applicable": False, "commands": [], "scripts": {}, "redirects": {}, "summary": {}}
    type_ref = set(doc_coverage._type_ref_commands(skill_dir))
    help_cmds = set(_help_commands(skill_dir))
    redirects = _redirects(skill_dir)
    scripts = set(doc_coverage._scripts(skill_dir))
    documented_scripts = _documented_scripts(skill_dir)

    rows: list[dict] = []
    for cmd in sorted(type_ref | help_cmds):
        spine = SPINE.get(cmd, "unmapped")
        in_tr, in_help = cmd in type_ref, cmd in help_cmds
        drift = None
        if in_tr and not in_help:
            drift = "in-type-ref-not-in-help"
        elif in_help and not in_tr:
            drift = "in-help-not-in-type-ref"
        tool = _tool_alive(skill_dir, cmd) if check_tools else None
        # Disposition: keep a spine-mapped command with no drift and no broken tool; everything
        # else is a REVIEW candidate (the human rules fold vs retire vs promote). `tool is False`
        # is a genuine broken route - the strongest review signal.
        if tool is False or spine == "unmapped" or drift:
            disposition = "review"
        else:
            disposition = "keep"
        rows.append({"command": cmd, "spine": spine, "in_type_ref": in_tr, "in_help": in_help,
                     "drift": drift, "tool": tool, "disposition": disposition})

    # Scripts are the tooling BEHIND the commands. An undocumented script (no reference entry) is a
    # fold/document candidate; a script whose --help fails is a broken tool.
    script_rows = []
    for s in sorted(scripts):
        alive = _tool_alive(skill_dir, s) if check_tools else None
        script_rows.append({"script": s, "documented": s in documented_scripts, "alive": alive})

    summary = {
        "commands": len(rows),
        "keep": sum(1 for r in rows if r["disposition"] == "keep"),
        "review": sum(1 for r in rows if r["disposition"] == "review"),
        "unmapped": sum(1 for r in rows if r["spine"] == "unmapped"),
        "drift": sum(1 for r in rows if r["drift"]),
        "broken_tools": sum(1 for r in rows if r["tool"] is False)
                        + sum(1 for r in script_rows if r["alive"] is False),
        "scripts": len(script_rows),
        "undocumented_scripts": sum(1 for r in script_rows if not r["documented"]),
        "redirects": len(redirects),
    }
    return {"applicable": True, "checked": check_tools, "commands": rows, "scripts": script_rows,
            "redirects": redirects, "summary": summary}


def _documented_scripts(skill_dir: Path) -> set[str]:
    """Scripts that carry a `### \\`name.py\\`` entry in any reference-scripts*.md page - the
    same authority `doc_coverage` uses, so 'documented' means one thing across both tools."""
    refscripts = "\n".join(
        p.read_text(encoding="utf-8") for p in sorted(skill_dir.glob("reference-scripts*.md")))
    return {s for s in doc_coverage._scripts(skill_dir) if f"### `{s}.py`" in refscripts}


# --- Dead flags -----------------------------------------------------------------------------
# A flag whose argparse destination nothing ever ACTS ON. The distinction that matters, and the
# reason an earlier specification for this was cut: counting the sites that mention a destination
# cannot find the defect. A `verify_batch` flag was mentioned three times in gate.py - defined, read
# through a defaulted lookup, and forwarded as a keyword argument into `run_gate` - and no line of
# `run_gate` read the parameter it arrived in. Every mention-counting rule, and every rule that
# treats `getattr(args, name, default)` as a read, calls that flag live. So the analysis FOLLOWS
# the value: a read is a consumption only when the value is acted on where it lands, or where it
# is forwarded to.
#
# Bounds, stated rather than hidden. A value assigned to a local name that nothing then reads is
# counted as consumed (the follow stops at the call boundary, not the assignment). Positionals are
# not judged: a flag is what this is about, and argparse enforces a positional's presence whether
# or not the value is read. And three shapes make a module's unread destinations CANNOT-JUDGE
# rather than dead, because in each of them the value may be read somewhere this analysis cannot
# see: a namespace handed to a callee that will not resolve, a `getattr` whose attribute name is
# computed, and a module that declares flags on a parser it never parses. A fabricated verdict is
# worse than an absent one.

#: `argparse` actions that never bind a destination, so they are not flags to judge.
_DESTLESS_ACTIONS = ("help", "version")

#: Directories an escaping namespace's callee is resolved against, relative to the analysed file.
_SIBLING_DIRS = (".", "lib")


def _parents(tree: ast.AST) -> dict:
    """child node -> parent node, so a read can be judged by where it sits."""
    return {child: parent
            for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}


def _functions(tree: ast.AST) -> dict[str, ast.FunctionDef]:
    """Every function this module defines, by bare name.

    Keyed by BARE NAME over the whole module, so a name defined twice keeps only the last
    definition the walk reaches. That is why `collided_names` exists beside this: two ordinary
    verb handlers each with a local helper of the same name is enough to resolve a forwarded
    value into the WRONG body, and a class method colliding with a module-level function
    misjudges too, because `self` absorbs argument index 0. Resolving properly needs a scope
    key; refusing to judge a collided name is the honest interim, and it is the module's own
    three-state design - dead, live, or not judged with the reason.
    """
    return {n.name: n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def collided_names(tree: ast.AST) -> set[str]:
    """Function names this module defines MORE THAN ONCE.

    A call to one of these cannot be resolved to a body by name alone, so anything it forwards
    into is unjudgeable rather than dead. Reporting it dead is the failure this guards: the
    reviewer's fixture reported `0 dead flag(s), 0 not judged` for a genuinely dead flag -
    silently clean, which is worse than either honest answer - and, with the helper bodies
    swapped, reported a LIVE flag as dead.
    """
    seen, twice = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            (twice if n.name in seen else seen).add(n.name)
    return twice


def _str_arg(node: ast.AST) -> str | None:
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def _dotted(node: ast.AST) -> str | None:
    """`a.b.c` as written, or None for anything that is not a plain dotted name."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    parts.append(node.id)
    return ".".join(reversed(parts))


def argparse_dests(tree: ast.AST) -> dict[str, dict]:
    """Every destination an OPTIONAL `add_argument` binds: `{dest: {line, flag}}`.

    `dest=` wins; otherwise the first long option names it (`--dry-run` binds `dry_run`), as
    argparse itself derives it. The flag is carried as written, so the report names the switch
    an operator types rather than reconstructing a spelling from the destination.

    Positionals are skipped. They are not flags, and argparse makes the caller supply one whether
    or not any line reads the value, so "never consumed" is not a defect there.
    """
    out: dict[str, dict] = {}
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        kw = {k.arg: k.value for k in node.keywords if k.arg}
        if _str_arg(kw.get("action")) in _DESTLESS_ACTIONS:
            continue
        names = [s for a in node.args if (s := _str_arg(a))]
        options = [s for s in names if s.startswith("-")]
        if not options:
            continue
        longs = [s for s in options if s.startswith("--")]
        flag = longs[0] if longs else options[0]
        dest = _str_arg(kw.get("dest")) or flag.lstrip("-").replace("-", "_")
        if dest:
            out.setdefault(dest, {"line": node.lineno, "flag": flag})
    return out


def _initialisers(tree: ast.AST) -> dict:
    """class name -> its `__init__`, so a namespace handed to a constructor can be followed."""
    out = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            init = next((n for n in node.body
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and n.name == "__init__"), None)
            if init is not None:
                out[node.name] = init
    return out


def _enclosing(node: ast.AST, parents: dict):
    """The function `node` sits in, or the Module."""
    cur = parents.get(node)
    while cur is not None and not isinstance(
            cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
        cur = parents.get(cur)
    return cur


def _function_values(scope: ast.AST, functions: dict, parents: dict) -> set[str]:
    """Module functions this scope names as a VALUE rather than calling - a handler table."""
    return {n.id for n in ast.walk(scope)
            if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in functions
            and not (isinstance(p := parents.get(n), ast.Call) and p.func is n)}


def _dispatch_targets(tree: ast.AST, functions: dict) -> set[str]:
    """The verb handlers `args.func(args)` reaches, from `set_defaults(func=...)`.

    Without these the whole family's dispatch is an unresolvable callee, every destination is
    cannot-judge, and the detector is inert on the corpus it exists for.

    Reading the argument is not always enough: `retro.py` registers its seven verbs from a table
    (`for name, fn, helptext in (...): p.set_defaults(func=fn)`), so the argument is a loop
    variable and all thirteen of that module's flags went unjudged. When the argument does not
    name a function, the handlers are taken to be the functions that scope names as values.

    Kept to the registered handlers rather than to every function named as a value anywhere:
    a wider set puts a namespace into parameters that never receive one (gate.py's
    `_conformance(root, ...)`), and a string read as a namespace escapes on its first use -
    which cost that module's verdict on the one flag that was actually dead.
    """
    parents = _parents(tree)
    out: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "set_defaults"):
            continue
        for kw in node.keywords:
            if kw.arg != "func" or not isinstance(kw.value, ast.Name):
                continue
            if kw.value.id in functions:
                out.add(kw.value.id)
            else:
                out |= _function_values(_enclosing(node, parents), functions, parents)
    return out


class _Module:
    """One module's flag analysis. Built once; every question below reads it."""

    def __init__(self, tree: ast.AST, path: Path | None = None) -> None:
        self.tree = tree
        self.path = path
        self.parents = _parents(tree)
        self.functions = _functions(tree)
        self.initialisers = _initialisers(tree)
        self._bound_methods = frozenset(self.initialisers.values())
        self.dispatch = _dispatch_targets(tree, self.functions)
        self._read_index: dict[str, list] | None = None
        self._binds_cache: dict[tuple, bool] = {}
        self.namespaces: dict[int, set[str]] = {}
        self._track_namespaces()

    # -- namespace tracking ------------------------------------------------------------------
    def _track_namespaces(self) -> None:
        """Which name holds a parsed namespace, PER SCOPE, followed to a fixed point.

        Per scope rather than per module, because a same-named local is not the namespace. Two
        real ones cost the analysis its verdict when the names were pooled: `args = shlex.split(
        tail)` in a verifier helper, and a nested `def _git(*args)` inside gate.py - the second
        made every flag in that module cannot-judge, the dead one included.

        Seeded from `parse_args()` and from the first parameter of each dispatch target, then
        widened through in-module calls that pass the namespace on.
        """
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                    and isinstance(node.value.func, ast.Attribute) \
                    and node.value.func.attr == "parse_args":
                scope = self._enclosing_function(node)
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        # A name the enclosing function declares `global` binds at MODULE scope,
                        # so it must be registered there. Registered against the function, a read
                        # from a sibling walked the chain out to Module, found nothing, and the
                        # destination fell straight through to `dead` - a FALSE POSITIVE on a
                        # blocking lane, with no warning attached, over a mainstream Python
                        # idiom the detector's own docstring did not list among its bounds.
                        # BOTH scopes for a `global`, not the module alone. `_is_namespace`
                        # stops the chain at the first scope that BINDS the name, and the
                        # declaring function does bind it - so registering only on the module
                        # would fix the sibling reads and break the declaring function's own.
                        self.namespaces.setdefault(id(scope), set()).add(t.id)
                        if self._declared_global(scope, t.id):
                            self.namespaces.setdefault(id(self.tree), set()).add(t.id)
        calls = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call)]
        widened = True
        while widened:
            widened = False
            for call in calls:
                for fn in self._callees(call) or ():
                    for param, value in self._bindings(call, fn):
                        if isinstance(value, ast.Name) and self._is_namespace(value) \
                                and param not in self.namespaces.get(id(fn), ()):
                            self.namespaces.setdefault(id(fn), set()).add(param)
                            widened = True

    def _declared_global(self, scope, name: str) -> bool:
        """Does `scope` declare `name` with a `global` statement? False at module scope, where
        the question does not arise. Walks the scope's own body only - a `global` inside a
        NESTED function binds for that function, not for this one."""
        if scope is None or isinstance(scope, ast.Module):
            return False
        for node in ast.walk(scope):
            if isinstance(node, ast.Global) and name in node.names \
                    and _enclosing(node, self.parents) is scope:
                return True
        return False

    def _binds(self, fn: ast.FunctionDef, name: str) -> bool:
        """Does this function bind `name` itself - as any kind of parameter, or by assignment?

        `*args` counts. A varargs tuple named `args` is not a namespace, and treating it as one
        read `["git", *args]` as the namespace leaving the module.
        """
        key = (id(fn), name)
        if key not in self._binds_cache:
            a = fn.args
            bound = {x.arg for x in a.posonlyargs + a.args + a.kwonlyargs}
            bound |= {x.arg for x in (a.vararg, a.kwarg) if x is not None}
            self._binds_cache[key] = name in bound or any(
                isinstance(n, (ast.Assign, ast.AugAssign, ast.AnnAssign, ast.NamedExpr))
                and any(isinstance(t, ast.Name) and t.id == name
                        for t in (n.targets if isinstance(n, ast.Assign) else [n.target]))
                for n in ast.walk(fn))
        return self._binds_cache[key]

    def _callees(self, call: ast.Call) -> list | None:
        """The in-module functions a call can reach, or None when it leaves this module.

        A class counts: `github_sync` hands the whole namespace to `_PushState(args)`, whose
        `__init__` is where the flags are read.
        """
        func = call.func
        if isinstance(func, ast.Name):
            if func.id in self.initialisers:
                return [self.initialisers[func.id]]
            fn = self.functions.get(func.id)
            return [fn] if fn is not None else None
        if isinstance(func, ast.Attribute) and func.attr == "func" \
                and isinstance(func.value, ast.Name) and self._is_namespace(func.value):
            return [self.functions[d] for d in sorted(self.dispatch) if d in self.functions]
        return None

    def _bindings(self, call: ast.Call, fn: ast.FunctionDef):
        """(parameter name, argument node) for each argument this call binds by name or index."""
        params = [a.arg for a in fn.args.posonlyargs] + [a.arg for a in fn.args.args]
        if fn in self._bound_methods:
            params = params[1:]        # `self` is supplied by the call, not by the caller
        for i, value in enumerate(call.args):
            if isinstance(value, ast.Starred):
                break
            if i < len(params):
                yield params[i], value
        keywords = params + [a.arg for a in fn.args.kwonlyargs]
        for kw in call.keywords:
            if kw.arg in keywords:
                yield kw.arg, kw.value

    # -- consumption -------------------------------------------------------------------------
    def _forwarded_to(self, node: ast.AST) -> list[tuple]:
        """(function, parameter) pairs this value is handed straight on to.

        Empty means the value is not a bare forward into a function this module defines, which
        is read as a consumption: it is being acted on here, or it has left where we can see.
        """
        parent = self.parents.get(node)
        if isinstance(parent, ast.keyword):
            call, keyword = self.parents.get(parent), parent.arg
        elif isinstance(parent, ast.Call) and any(a is node for a in parent.args):
            call, keyword = parent, None
        else:
            return []
        if not isinstance(call, ast.Call):
            return []
        out = []
        for fn in self._callees(call) or ():
            for param, value in self._bindings(call, fn):
                if value is node and (keyword is None or param == keyword):
                    out.append((fn, param))
        return out

    def _param_consumed(self, fn: ast.FunctionDef, param: str, seen: frozenset) -> bool:
        """Does anything act on `param` inside `fn`, or inside what `fn` forwards it to?"""
        key = (fn.name, param)
        if key in seen:
            return False        # a forward-only cycle acts on nothing
        seen = seen | {key}
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Name) and node.id == param
                    and isinstance(node.ctx, ast.Load)):
                continue
            forwards = self._forwarded_to(node)
            if not forwards:
                return True
            if any(self._param_consumed(f, p, seen) for f, p in forwards):
                return True
        return False

    def _enclosing_function(self, node: ast.AST):
        return _enclosing(node, self.parents)

    def _is_namespace(self, node: ast.AST) -> bool:
        """A named namespace in scope here, or an unnamed one read straight off `parse_args()`.

        Resolved outwards through the scope chain, stopping at the first function that binds the
        name itself - which is what Python does, and what keeps a same-named local out.
        """
        if isinstance(node, ast.Name):
            scope = self._enclosing_function(node)
            while scope is not None:
                if node.id in self.namespaces.get(id(scope), ()):
                    return True
                if isinstance(scope, ast.Module) or self._binds(scope, node.id):
                    return False
                scope = self._enclosing_function(scope)
            return False
        return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
            and node.func.attr == "parse_args"

    def _reads(self, dest: str) -> list:
        """Every site that takes `dest` off a namespace, plain or through a defaulted lookup.

        Indexed on first use: a module declaring thirty flags would otherwise walk its whole tree
        thirty times, and this runs on every commit.
        """
        if self._read_index is None:
            index: dict[str, list] = {}
            for node in ast.walk(self.tree):
                name = None
                if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load) \
                        and self._is_namespace(node.value):
                    name = node.attr
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                        and node.func.id == "getattr" and len(node.args) >= 2 \
                        and self._is_namespace(node.args[0]):
                    name = _str_arg(node.args[1])
                if name:
                    index.setdefault(name, []).append(node)
            self._read_index = index
        return self._read_index.get(dest, [])

    def parses(self) -> bool:
        """Does this module parse a namespace at all?

        A module that only DECLARES arguments - the shared `add_*_arg` helpers, which take the
        caller's parser as a parameter - binds destinations that are read in the module that
        parses them. Judging them here would report every shared declarator as dead.
        """
        return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                   and n.func.attr == "parse_args" for n in ast.walk(self.tree))

    def dynamic_reads(self) -> list[dict]:
        """`getattr(args, <computed>, ...)` sites - a read of a destination we cannot name.

        The shared prose-fields loader is built this way (`{k: getattr(args, k, None) for k in
        keys}`), so treating these as no read at all reported live flags as dead.
        """
        out = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id == "getattr" and len(node.args) >= 2 \
                    and self._is_namespace(node.args[0]) and _str_arg(node.args[1]) is None:
                out.append({"line": node.lineno})
        return out

    def consumed(self, dest: str) -> bool:
        """True when at least one read of `dest` reaches a line that acts on the value."""
        return any(not (f := self._forwarded_to(node))
                   or any(self._param_consumed(fn, p, frozenset()) for fn, p in f)
                   for node in self._reads(dest))

    # -- namespace escapes -------------------------------------------------------------------
    def escapes(self) -> list[dict]:
        """Sites where the whole namespace leaves the functions this module defines."""
        out = []
        for node in ast.walk(self.tree):
            if not (isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                    and self._is_namespace(node)):
                continue
            parent = self.parents.get(node)
            if isinstance(parent, ast.Attribute):
                continue                                    # `args.x` - a destination read
            # A test of the namespace's EXISTENCE reads no destination off it. `resolve_boundary`
            # guards with `args is not None`, and reading that as an escape made every flag in
            # gate.py cannot-judge - including the dead one this detector exists to catch.
            if isinstance(parent, (ast.Compare, ast.UnaryOp, ast.BoolOp)):
                continue
            if isinstance(parent, (ast.If, ast.IfExp, ast.While, ast.Assert)) \
                    and parent.test is node:
                continue
            call = self.parents.get(parent) if isinstance(parent, ast.keyword) else parent
            if not (isinstance(call, ast.Call) and call.func is not node):
                out.append({"line": node.lineno, "callee": None, "param": None})
                continue
            if isinstance(call.func, ast.Name) and call.func.id == "getattr":
                continue                                    # a defaulted destination read
            if self._callees(call) is not None:
                continue                                    # in-module; already analysed
            index = next((i for i, a in enumerate(call.args) if a is node), None)
            keyword = parent.arg if isinstance(parent, ast.keyword) else None
            out.append({"line": node.lineno, "callee": _dotted(call.func),
                        "param": keyword, "index": index})
        return out

    def escaped_reads(self) -> tuple[set[str], list[dict]]:
        """(destinations an escape's callee reads, escapes that could not be resolved).

        The universal escape in this family is `sdlc_md.resolve_root(args)`, which reads exactly
        one destination. Resolving it is what keeps every other destination judgeable.
        """
        reads: set[str] = set()
        unresolved = []
        for esc in self.escapes():
            found = self._resolve_escape(esc)
            if found is None:
                unresolved.append(esc)
            else:
                reads |= found
        return reads, unresolved

    def _resolve_escape(self, esc: dict) -> set[str] | None:
        """What the escape's callee reads off the namespace, or None if that is unknowable."""
        callee, path = esc.get("callee"), self.path
        if not callee or path is None:
            return None
        if "." not in callee:
            # A bare name this module does not define is a re-export it imported under that name
            # (`from lib.sdlc_md import resolve_root`, or a module-level alias).
            alias = _reexport(self.tree, callee)
            if not alias or esc.get("hops", 0) >= 1:
                return None
            return self._resolve_escape({**esc, "callee": alias, "hops": 1})
        alias, _, name = callee.rpartition(".")
        if "." in alias:
            return None
        target = next((c for d in _SIBLING_DIRS
                       if (c := path.parent / d / f"{alias}.py").is_file()), None)
        if target is None:
            return None
        try:
            tree = ast.parse(target.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            return None
        fn = _functions(tree).get(name)
        if fn is None:
            # One hop through a re-export (`resolve_root = sdlc_md.resolve_root`). Without it the
            # family's most common flag is unjudgeable in every module that reaches the shared
            # root resolver through a sibling rather than directly.
            alias = _reexport(tree, name)
            if not alias or esc.get("hops", 0) >= 1:
                return None
            return self._resolve_escape({**esc, "callee": alias, "hops": 1})
        params = [a.arg for a in fn.args.posonlyargs] + [a.arg for a in fn.args.args]
        param = esc.get("param")
        if param is None:
            index = esc.get("index")
            if index is None or index >= len(params):
                return None
            param = params[index]
        elif param not in params:
            return None
        return _reads_off_param(tree, fn, param)


def _reexport(tree: ast.AST, name: str) -> str | None:
    """`name = other.thing` at module level - the dotted target, so an escape can follow it."""
    for node in tree.body if isinstance(tree, ast.Module) else ():
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name
                                                for t in node.targets):
            return _dotted(node.value)
    return None


def _reads_off_param(tree: ast.AST, fn: ast.FunctionDef, param: str) -> set[str] | None:
    """The attribute names read off `param` inside `fn`, or None if `param` goes on elsewhere.

    A namespace the callee passes further on could be read anywhere, so the honest answer there
    is "unknown" rather than the short list this function can see.
    """
    parents = _parents(fn)
    found = set()
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Name) and node.id == param
                and isinstance(node.ctx, ast.Load)):
            continue
        parent = parents.get(node)
        if isinstance(parent, ast.Attribute):
            found.add(parent.attr)
            continue
        if isinstance(parent, ast.Call) and isinstance(parent.func, ast.Name) \
                and parent.func.id == "getattr" and len(parent.args) >= 2 \
                and parent.args[0] is node and (s := _str_arg(parent.args[1])):
            found.add(s)
            continue
        return None
    return found


def dead_flags(source: str, path: Path | None = None) -> dict:
    """Judge one module's flags. `{dests, dead, unjudged}`, each destination in exactly one.

    A destination is dead when no read of it reaches a line that acts on the value AND nothing
    this analysis cannot see could be reading it.
    """
    tree = ast.parse(source)
    mod = _Module(tree, path)
    dests = argparse_dests(tree)
    external, unresolved = mod.escaped_reads()
    dynamic = mod.dynamic_reads()
    declare_only = bool(dests) and not mod.parses()
    collided = collided_names(tree)
    dead, unjudged = [], []
    for dest, where in sorted(dests.items()):
        line = where["line"]
        if mod.consumed(dest) or dest in external:
            continue
        if declare_only:
            reason = "this module declares flags on a parser it never parses, so the value is " \
                     "read by whichever module parses it"
        elif dynamic:
            reason = (f"a getattr with a computed attribute name at line {dynamic[0]['line']} "
                      f"may read any destination")
        elif collided:
            # Ordered AFTER the dynamic/declare-only reasons and BEFORE `dead`: a module whose
            # names collide cannot be judged by this resolver at all, and a flag reported dead
            # on a mis-resolved body is a documented switch deleted for the wrong reason.
            reason = (f"{len(collided)} function name(s) are defined more than once in this "
                      f"module ({', '.join(sorted(collided)[:4])}), so a forwarded value "
                      f"cannot be resolved to a body by name alone")
        elif unresolved:
            esc = unresolved[0]
            reason = (f"the namespace escapes to "
                      f"{esc['callee'] or 'a value this module cannot follow'} at line "
                      f"{esc['line']}, which may read it")
        else:
            dead.append({"dest": dest, "line": line, "flag": where["flag"]})
            continue
        unjudged.append({"dest": dest, "line": line, "flag": where["flag"], "reason": reason})
    return {"dests": dests, "dead": dead, "unjudged": unjudged}


#: Destinations this analysis is known not to judge, one `module:dest` per line. A
#: module-scoped escape demotes EVERY unread destination in that module, including ones the
#: escape has nothing to do with - so the hole is recorded precisely rather than left to widen
#: whenever an unrelated escape is added.
UNJUDGED_BASELINE_REL = "sdlc-studio/.unjudged-flags-baseline.txt"


def unjudged_baseline(repo_root: Path | str = ".") -> set[str]:
    """The recorded `module:dest` pairs, or an empty set when none is recorded."""
    path = Path(repo_root) / UNJUDGED_BASELINE_REL
    text = sdlc_md.read_text_safe(path)
    if not text:
        return set()
    return {ln.strip() for ln in text.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")}


def unjudged_drift(repo_root: Path | str = ".", scan: dict | None = None) -> dict:
    """`{new, cleared}` - unjudged destinations that are not in the baseline, and vice versa.

    `new` is the ratchet: a destination this analysis stopped judging without anybody deciding
    it should. Previously nothing counted them at all, so adding one unrelated escape could
    silently un-judge a whole module's flags and the exit code never moved.

    `cleared` is reported too, because a baseline that only ever grows is not a baseline - a
    pair that is now judgeable should be dropped from the file, and saying so is what makes
    that happen.
    """
    scan = scan if scan is not None else scan_dead_flags(repo_root)
    seen = {f"{u.get('module') or u.get('path')}:{u['dest']}"
            for u in (scan.get("unjudged") or [])}
    recorded = unjudged_baseline(repo_root)
    return {"new": sorted(seen - recorded), "cleared": sorted(recorded - seen)}


def scan_dead_flags(repo_root: Path | str = ".") -> dict:
    """Every module under the skill's scripts/ and the repo's tools/, judged.

    `{applicable, modules, dead, unjudged, summary}`. Test modules are excluded: a fixture
    deliberately builds a dead flag, so scanning them would report the fixtures as findings.
    """
    root = Path(repo_root)
    skill_dir = doc_coverage._skill_dir(root)
    if skill_dir is None:
        return {"applicable": False, "modules": 0, "dead": [], "unjudged": [], "summary": {}}
    paths = [p for p in sorted((skill_dir / "scripts").rglob("*.py"))
             if "tests" not in p.parts and "__pycache__" not in p.parts]
    paths += [p for p in sorted((root / "tools").glob("*.py"))]
    dead, unjudged, judged = [], [], 0
    for path in paths:
        try:
            result = dead_flags(path.read_text(encoding="utf-8"), path)
        except (OSError, SyntaxError) as exc:
            unjudged.append({"module": str(path.relative_to(root)), "dest": None,
                             "reason": f"unreadable: {exc}"})
            continue
        judged += 1
        rel = str(path.relative_to(root))
        dead += [{"module": rel, **d} for d in result["dead"]]
        unjudged += [{"module": rel, **u} for u in result["unjudged"]]
    return {"applicable": True, "modules": judged, "dead": dead, "unjudged": unjudged,
            "summary": {"dead": len(dead), "unjudged": len(unjudged), "modules": judged}}


def render_dead_flags(result: dict) -> str:
    """The lane's output: what is dead, then what could not be judged, always both."""
    if not result["applicable"]:
        return "dead-flags: not a skill repo (no SKILL.md) - nothing to scan.\n"
    s = result["summary"]
    out = [f"dead-flags: {s['modules']} module(s) scanned, {s['dead']} dead flag(s), "
           f"{s['unjudged']} destination(s) not judged."]
    for d in result["dead"]:
        out.append(f"  DEAD {d['module']}:{d['line']} {d['flag']} (dest `{d['dest']}`) "
                   f"- no line acts on the parsed value")
    # Named, never silent: a destination nothing could judge is not a destination that passed.
    for u in result["unjudged"]:
        out.append(f"  not judged {u['module']}"
                   + (f":{u['line']}" if u.get("line") else "")
                   + (f" `{u['dest']}`" if u.get("dest") else "")
                   + f" - {u['reason']}")
    return "\n".join(out) + "\n"


def render_markdown(result: dict) -> str:
    """The audit document body: a per-spine command table with dispositions, then the script
    tooling table, then a summary. What a cleanup slice reads to decide what moves."""
    if not result["applicable"]:
        return "# Command-surface audit\n\n_Not a skill repo - nothing to audit._\n"
    s = result["summary"]
    checked = result.get("checked")
    # Only claim tooling health when it was actually verified (--check-tools). Without it, the
    # disposition still stands on spine + drift, but the doc must not certify "0 broken" - that
    # would be an unverified claim persisted to disk.
    tool_note = (f"{s['broken_tools']} broken tool(s)" if checked else "tooling not checked")
    out = ["# Command-surface audit",
           "",
           "_Generated by `scripts/command_audit.py` - re-run to refresh. Dispositions are "
           "structural signals (spine mapping, catalogue drift, tooling health); the keep / fold / "
           "retire DECISION is the reviewer's, recorded here._",
           "",
           f"**{s['commands']} commands** - {s['keep']} keep, {s['review']} to review "
           f"({s['unmapped']} unmapped, {s['drift']} drift, {tool_note}). "
           f"**{s['scripts']} scripts**, {s['undocumented_scripts']} undocumented.",
           ""]
    by_spine: dict[str, list[dict]] = {}
    for r in result["commands"]:
        by_spine.setdefault(r["spine"], []).append(r)
    for spine in SPINE_ORDER:
        rows = by_spine.get(spine)
        if not rows:
            continue
        out += [f"## {spine}", "", "| Command | In Type Ref | In help | Drift | Disposition |",
                "| --- | --- | --- | --- | --- |"]
        for r in rows:
            out.append(f"| `{r['command']}` | {'yes' if r['in_type_ref'] else 'no'} | "
                       f"{'yes' if r['in_help'] else 'no'} | {r['drift'] or '-'} | "
                       f"{r['disposition']} |")
        out.append("")
    # Folded commands - out of the catalogue, still routed. Recorded so a reader can tell a fold
    # (a live route under a new front door) from a deletion (no route at all).
    if result.get("redirects"):
        out += ["## folded", "", "| Command | Redirects to |", "| --- | --- |"]
        out += [f"| `{c}` | `{t}` |" for c, t in sorted(result["redirects"].items())]
        out.append("")
    # Recommended actions - derived from the structural findings, for the cleanup slice to act on.
    help_only = [r["command"] for r in result["commands"]
                 if r["drift"] == "in-help-not-in-type-ref"]
    tr_only = [r["command"] for r in result["commands"]
               if r["drift"] == "in-type-ref-not-in-help"]
    broken = [r["command"] for r in result["commands"] if r["tool"] is False]
    undoc = [r["script"] for r in result["scripts"] if not r["documented"]]
    out += ["## Recommended actions (for the cleanup slice)", ""]
    if help_only:
        out.append(f"- **Promote or retire {len(help_only)} help-only command(s)** "
                   f"(in the help catalogue, not the SKILL Type Reference): "
                   f"{', '.join(f'`{c}`' for c in help_only)}. Promote the ones that serve the "
                   f"spine to the Type Reference; retire the rest.")
    if tr_only:
        out.append(f"- **Document {len(tr_only)} Type-Reference-only command(s)** "
                   f"(no help catalogue entry): {', '.join(f'`{c}`' for c in tr_only)}.")
    if broken:
        out.append(f"- **Fix {len(broken)} broken tool(s)**: {', '.join(f'`{c}`' for c in broken)}.")
    if undoc:
        out.append(f"- **Document {len(undoc)} script(s)** with no reference-scripts entry: "
                   f"{', '.join(f'`{s}`' for s in undoc)}.")
    if not checked:
        out.append("- Re-run with `--check-tools` to verify the tooling behind each command runs "
                   "(this pass did not check).")
    if not (help_only or tr_only or broken or undoc):
        tail = "every tool runs" if checked else "tooling unchecked this pass"
        out.append(f"- No catalogue/spine issues: the surface is spine-mapped and catalogued both "
                   f"ways ({tail}).")
    # exactly one trailing newline - the per-section trailing blanks must not stack into an MD012
    # double-blank at EOF.
    return "\n".join(out).rstrip("\n") + "\n"


def cmd_run(args: argparse.Namespace) -> int:
    if args.dead_flags:
        result = scan_dead_flags(args.root)
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(render_dead_flags(result), end="")
        # This mode gates on its own: a dead flag is a defect of the same kind as a broken tool,
        # and a lane that reports one and exits 0 cannot stop it shipping.
        return 1 if result["applicable"] and result["dead"] else 0
    result = audit(args.root, check_tools=args.check_tools)
    if not result["applicable"]:
        print("command_audit: not a skill repo (no SKILL.md) - nothing to audit.")
        return 0
    if args.write:
        out = Path(args.root) / "sdlc-studio" / "reviews" / "command-audit.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        sdlc_md.atomic_write(out, render_markdown(result))
        print(f"wrote {out}")
    if args.format == "json":
        print(json.dumps(result, indent=2))
        return 0
    if not args.write:
        print(render_markdown(result), end="")
    # exit non-zero under --strict when a broken tool exists (a dead route is a real defect); the
    # unmapped/drift review candidates are advisory - a report, not a gate, unless asked.
    if args.strict and result["summary"]["broken_tools"]:
        print(f"\ncommand_audit: {result['summary']['broken_tools']} broken tool(s) "
              f"(--strict)", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="command_audit", description=__doc__)
    p.add_argument("--root", default=".", help="repo root")
    p.add_argument("--check-tools", action="store_true",
                   help="run each backing script's --help (slower; detects a broken tool)")
    p.add_argument("--write", action="store_true",
                   help="write sdlc-studio/reviews/command-audit.md instead of stdout")
    p.add_argument("--strict", action="store_true",
                   help="exit non-zero when a broken tool is found (with --check-tools)")
    p.add_argument("--dead-flags", action="store_true",
                   help="report a flag whose parsed destination no line acts on, and exit "
                        "non-zero when one is found (skips the command-surface audit)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
